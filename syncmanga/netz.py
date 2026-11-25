# -*- coding: utf-8 -*-
"""Der eine Netz-Ausgang von SyncManga: jeder Abruf nach außen geht durch `oeffnen`.

Vor jedem Versuch gelten dieselben Regeln, egal welches Modul abruft:

1. **Gedächtnis:** Eine Adresse, die eben 403, 404 oder 410 lieferte, wird innerhalb der
   Merkfrist nicht noch einmal gefragt. Der Aufrufer bekommt dieselbe Antwort als
   `NichtGesendet` (ein `HTTPError` mit dem gemerkten Code) und urteilt wie bisher.
2. **Bremse je Host:** Nach 429 (oder 503 mit Retry-After) ruht der Host. Eine genannte
   Retry-After-Frist gilt, sonst eine kurze Stufe, die bei weiteren 429 wächst. Kurze Reste
   (bis `WARTE_HOECHSTENS_S`) wartet der Ausgang ab; längere lehnt er ohne Senden ab
   (`NichtGesendet` mit Code 429 und dem Rest als Retry-After-Kopf).
3. **Tagesbudget:** Je Host und insgesamt eine Obergrenze je Kalendertag. Ist sie erreicht,
   wird bis Mitternacht nichts mehr gesendet (`NichtGesendet`, Code 429).
4. **Takt je Host:** Ein Mindestabstand zwischen zwei Sendungen an denselben Host, auch wenn
   mehrere Module oder Fäden ihn nutzen. Die Werte stammen aus den bisherigen Pacern
   (Diensttabelle `DIENSTE`); die Pacer der Aufrufer bleiben zusätzlich bestehen.

Warum `NichtGesendet` ein `HTTPError` mit Code 429 ist: Alle Aufrufer werten 429 schon als
„gesperrt, nicht tot“ (readerlink `blocked`, health `alive`, linkhealth kein Herabstufen).
Ein nicht gesendeter Abruf darf nie als toter Link gelten — so bleibt das Urteil gleich.
Wiederholschleifen fragen `nicht_gesendet(e)` und hören dann auf, statt blind zu wiederholen.

Budget und Bremse überdauern den Prozess in `%LOCALAPPDATA%\\SyncManga\\netz_zustand.json`
(Tray-Lauf, Werkzeuge und die eigenständige App auf demselben PC teilen sich die Server).
Unter pytest bleibt alles im Speicher, außer ein Test setzt ausdrücklich einen Pfad.

Vorbild: SyncFindus `netz/abruf.py` + `netz/dienste.py` (dort viel breiter); dieses Modul
bleibt bewusst klein und hängt nur an `common.json_aendern` (Paket ohne Familie lauffähig).

WICHTIG für Tests: gesendet wird über `urllib.request.urlopen` (Modul-Attribut) — ein Mock
davon greift weiter. Uhr und Schlaf laufen über `_uhr`/`_schlafen` (in Tests ersetzbar).
"""
import atexit
import email.message
import email.utils
import hashlib
import io
import math
import os
import sys
import threading
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timedelta
from urllib.parse import urlsplit


@dataclass(frozen=True)
class Dienst:
    takt_s: float       # Mindestabstand zwischen zwei Sendungen an diesen Host
    tag: int            # Tagesbudget (Sendungen je Kalendertag)
    herkunft: str       # woher der Takt stammt (bisheriger Pacer)


# Takt-Werte = der jeweils strengste bisherige Pacer für diesen Host. Die Budgets fangen nur
# Ausreißer ab (Schleifen, die einen Host hämmern). Gemessen am echten Tray-Lauf vom 25.11.2026
# (mit der wöchentlichen Empfehlungs-Runde): 17.713 Abrufe an 146 Hosts, Spitze mgeko.cc mit 572.
# Der Tray läuft viermal am Tag, dazu kommen Hand- und Voll-Läufe — darum gesamt 120.000 (knapp
# sieben solche Läufe) und je Reader-Host 5000 (rund achtmal die gemessene Spitze).
DIENSTE = {
    "graphql.anilist.co": Dienst(0.7, 5000, "sources.AL_PACER 0.7 s (anilist.AL_PACER 2.1 s bleibt beim Abgleich)"),
    "api.mangadex.org": Dienst(0.2, 8000, "sources.MD_PACER 0.2 s"),
    "api.mangaupdates.com": Dienst(0.3, 5000, "sources.MU_PACER 0.3 s"),
    "kitsu.io": Dienst(0.3, 3000, "sources.KITSU_PACER 0.3 s"),
    "api.jikan.moe": Dienst(1.1, 3000, "sources.JK_PACER 1.1 s"),
    "api.mangabaka.org": Dienst(0.6, 5000, "catalog.MB_PACER 0.6 s"),
    "mangafire.to": Dienst(1.2, 5000, "readerlink/regen_read_scheme 1.2 s (sources.MF_PACER 1.0 s)"),
    "dynasty-scans.com": Dienst(0.8, 3000, "sources.DY_PACER 0.8 s"),
    "webtoons.com": Dienst(1.0, 3000, "sources.WT_PACER 1.0 s"),
    "api.comick.dev": Dienst(1.0, 3000, "sources.CK_PACER 1.0 s"),
}
STANDARD = Dienst(0.25, 5000, "readerlink.READER_PACER 0.25 s (global) — hier je Host")
TAG_BUDGET_GESAMT = 120000

WARTE_HOECHSTENS_S = 5.0          # kürzere Bremsreste wartet der Ausgang ab, längere lehnt er ab
BREMSE_429_S = 5.0                # 429 ohne Retry-After: erste Stufe …
BREMSE_429_MAX_S = 900.0          # … verdoppelt je weiterem 429 bis höchstens hierhin
RETRY_AFTER_MAX_S = 6 * 3600.0    # unplausibel lange Fristen deckeln (Uhrfehler beim Anbieter)
MERKE_S = {403: 600.0, 404: 3600.0, 410: 3600.0}
GEDAECHTNIS_MAX = 4096
SPEICHERN_JE = 50                 # Zähler alle N Sendungen in die Zustandsdatei


class NichtGesendet(urllib.error.HTTPError):
    """Der Ausgang hat nicht gesendet (Bremse, Budget oder gemerkte Antwort)."""

    gesendet = False

    def __init__(self, url, code, grund, rest_s=0.0, koepfe=None):
        hdrs = email.message.Message()
        for k, v in (dict(koepfe.items()) if koepfe is not None and hasattr(koepfe, "items") else {}).items():
            hdrs[k] = v
        if rest_s > 0 and "Retry-After" not in hdrs:
            hdrs["Retry-After"] = str(math.ceil(rest_s))
        super().__init__(url, code, grund, hdrs, io.BytesIO(b""))
        self.grund, self.rest_s = grund, rest_s


def nicht_gesendet(exc):
    """True, wenn die Ausnahme vom Ausgang stammt und nichts gesendet wurde.
    Wiederholschleifen hören dann auf (die Frist steht in `exc.rest_s`)."""
    return getattr(exc, "gesendet", True) is False


# ---------------- Uhr (in Tests ersetzbar) ----------------
def _uhr():
    return time.time()


def _schlafen(sekunden):
    time.sleep(sekunden)


# ---------------- Zustand ----------------
_sperre = threading.RLock()
_naechster = {}          # host -> frühester Sendezeitpunkt (Takt)
_bremse = {}             # host -> bis (Epoche)
_folge_429 = {}          # host -> Zahl aufeinanderfolgender 429
_gedaechtnis = {}        # (methode, url, rumpf-hash) -> (bis, code, grund, koepfe)
_tag = ""
_basis = {}              # host -> Zähler aus der Datei (Stand des letzten Abgleichs)
_neu = {}                # host -> Sendungen seit dem letzten Abgleich
_neu_summe = 0
_geladen = False
_pfad_gesetzt = False
_pfad = None


def _unter_test():
    return "pytest" in sys.modules or bool(os.environ.get("PYTEST_CURRENT_TEST"))


def _standard_pfad():
    roh = os.environ.get("SYNCMANGA_NETZ_ZUSTAND")
    if roh is not None:
        return None if roh.strip().lower() in ("", "aus", "0") else roh
    if _unter_test():
        return None
    basis = os.environ.get("LOCALAPPDATA")
    return os.path.join(basis, "SyncManga", "netz_zustand.json") if basis else None


def zustand_pfad_setzen(pfad):
    """Zustandsdatei festlegen (`None` = nur im Speicher). Für Tests und Sonderläufe."""
    global _pfad, _pfad_gesetzt, _geladen
    with _sperre:
        _speichern()
        _pfad, _pfad_gesetzt, _geladen = pfad, True, False


def _zustandspfad():
    return _pfad if _pfad_gesetzt else _standard_pfad()


def _heute():
    return datetime.fromtimestamp(_uhr()).strftime("%Y-%m-%d")


def _mitternacht_rest():
    jetzt = datetime.fromtimestamp(_uhr())
    morgen = (jetzt + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    return max(1.0, (morgen - jetzt).total_seconds())


def _uebernehmen(daten):
    """Dateistand in den Speicher übernehmen (unter `_sperre`)."""
    global _basis
    jetzt = _uhr()
    if isinstance(daten, dict):
        if daten.get("tag") == _tag and isinstance(daten.get("zaehler"), dict):
            _basis = {h: int(n) for h, n in daten["zaehler"].items() if isinstance(n, (int, float))}
        for h, bis in (daten.get("bremse") or {}).items():
            if isinstance(bis, (int, float)) and bis > jetzt and bis > _bremse.get(h, 0):
                _bremse[h] = float(bis)


def _laden():
    global _geladen
    if _geladen:
        return
    _geladen = True
    pfad = _zustandspfad()
    if not pfad:
        return
    import json
    try:
        with open(pfad, encoding="utf-8") as f:
            _uebernehmen(json.load(f))
    except (OSError, ValueError):
        pass


def _speichern(bremse_host=None):
    """Zähler-Delta und Bremsen in die Datei mischen (unter `_sperre`). Fehler sind still:
    der Ausgang zählt im Speicher weiter, ein Schreibfehler verhindert keinen Abruf."""
    global _neu, _neu_summe
    pfad = _zustandspfad()
    if not pfad:
        _neu_summe = 0          # nur im Speicher: die Zähler bleiben in `_neu`
        return
    if not _neu and bremse_host is None:
        return
    delta, tag, jetzt = dict(_neu), _tag, _uhr()
    bremsen = {h: b for h, b in _bremse.items() if b > jetzt}

    def aenderung(daten):
        if not isinstance(daten, dict) or daten.get("tag") != tag:
            daten = {"tag": tag, "zaehler": {}, "bremse": {}}
        z = daten.setdefault("zaehler", {})
        for h, n in delta.items():
            z[h] = int(z.get(h, 0)) + n
        alt = {h: b for h, b in (daten.get("bremse") or {}).items()
               if isinstance(b, (int, float)) and b > jetzt}
        for h, b in bremsen.items():
            alt[h] = max(b, alt.get(h, 0))
        daten["bremse"] = alt
        return daten
    # Spät importiert: common nutzt den Ausgang für get_json/post_json (Kreis vermeiden).
    from .common import json_aendern
    try:
        neu = json_aendern(pfad, aenderung)
    except Exception:
        neu = None
    if neu is not None:
        _neu = {}
        _uebernehmen(neu)
    # Auch nach einem Schreibfehler erst nach weiteren `SPEICHERN_JE` Sendungen neu versuchen —
    # sonst wartete jeder Abruf erneut auf die Dateisperre. Das Delta bleibt dann in `_neu`.
    _neu_summe = 0


def _speichern_sicher():
    try:
        with _sperre:
            _speichern()
    except Exception:
        pass


atexit.register(_speichern_sicher)


def _zuruecksetzen():
    """Speicherstand leeren (Tests). Die Zustandsdatei bleibt unberührt."""
    global _tag, _basis, _neu, _neu_summe, _geladen, _pfad, _pfad_gesetzt
    with _sperre:
        _naechster.clear()
        _bremse.clear()
        _folge_429.clear()
        _gedaechtnis.clear()
        _tag, _basis, _neu, _neu_summe = "", {}, {}, 0
        _geladen, _pfad, _pfad_gesetzt = False, None, False


# ---------------- Regeln ----------------
def host_von(url):
    return (urlsplit(url).hostname or "").lower().removeprefix("www.")


def dienst(host):
    """Tabellenzeile für einen Host (exakter Host ohne `www.`); alle anderen: `STANDARD`."""
    return DIENSTE.get(host, STANDARD)


def _gezaehlt(host):
    return _basis.get(host, 0) + _neu.get(host, 0)


def _gesamt():
    return sum(_basis.values()) + sum(_neu.values())


def _retry_after(koepfe):
    """Retry-After (Sekunden oder HTTP-Datum) -> Sekunden oder None."""
    try:
        roh = koepfe.get("Retry-After") if koepfe is not None else None
    except Exception:
        return None
    if roh is None:
        return None
    roh = str(roh).strip()
    try:
        return max(0.0, min(float(roh), RETRY_AFTER_MAX_S))
    except ValueError:
        pass
    try:
        ziel = email.utils.parsedate_to_datetime(roh).timestamp()
    except (TypeError, ValueError, IndexError, OverflowError):
        return None
    return max(0.0, min(ziel - _uhr(), RETRY_AFTER_MAX_S))


def _schluessel(anfrage):
    rumpf = anfrage.data if isinstance(anfrage.data, (bytes, bytearray)) else b""
    return (anfrage.get_method(), anfrage.full_url, hashlib.sha1(rumpf).hexdigest())


def _vorher(anfrage, host):
    """Gedächtnis, Bremse, Budget und Takt prüfen; zählt die Sendung. Wirft `NichtGesendet`
    oder liefert die Wartezeit, die vor dem Senden noch zu schlafen ist."""
    global _tag, _basis, _neu_summe
    url = anfrage.full_url
    with _sperre:
        jetzt = _uhr()
        heute = _heute()
        if heute != _tag:
            if _tag:
                _speichern()
            _tag, _basis = heute, {}
            _neu.clear()
            _neu_summe = 0
        _laden()
        merk = _gedaechtnis.get(_schluessel(anfrage))
        if merk and merk[0] > jetzt:
            raise NichtGesendet(url, merk[1], f"gemerkt: {merk[2]}", koepfe=merk[3])
        rest = _bremse.get(host, 0) - jetzt
        if rest > WARTE_HOECHSTENS_S:
            raise NichtGesendet(url, 429, f"Bremse: {host} ruht noch {math.ceil(rest)} s", rest)
        d = dienst(host)
        if _gezaehlt(host) >= d.tag:
            raise NichtGesendet(url, 429, f"Tagesbudget {host} ({d.tag}) erschöpft", _mitternacht_rest())
        if _gesamt() >= TAG_BUDGET_GESAMT:
            raise NichtGesendet(url, 429, f"Tagesbudget gesamt ({TAG_BUDGET_GESAMT}) erschöpft",
                                _mitternacht_rest())
        start = max(jetzt, _naechster.get(host, 0.0), _bremse.get(host, 0.0))
        _naechster[host] = start + d.takt_s
        _neu[host] = _neu.get(host, 0) + 1
        _neu_summe += 1
        if _neu_summe >= SPEICHERN_JE:
            _speichern()
        return start - jetzt


def _nachher_fehler(anfrage, host, e):
    code = getattr(e, "code", 0)
    koepfe = getattr(e, "headers", None)
    with _sperre:
        jetzt = _uhr()
        if code in MERKE_S:
            if len(_gedaechtnis) >= GEDAECHTNIS_MAX:
                for k in [k for k, v in _gedaechtnis.items() if v[0] <= jetzt] or list(_gedaechtnis)[:512]:
                    _gedaechtnis.pop(k, None)
            _gedaechtnis[_schluessel(anfrage)] = (jetzt + MERKE_S[code], code, getattr(e, "msg", "") or f"HTTP {code}",
                                                  koepfe)
            return
        frist = _retry_after(koepfe) if code in (429, 503) else None
        if code == 429:
            _folge_429[host] = _folge_429.get(host, 0) + 1
            if frist is None:
                frist = min(BREMSE_429_S * 2 ** (_folge_429[host] - 1), BREMSE_429_MAX_S)
        if frist:
            _bremse[host] = max(_bremse.get(host, 0.0), jetzt + frist)
            _speichern(bremse_host=host)


def oeffnen(anfrage, timeout=30):
    """Ersatz für `urllib.request.urlopen(anfrage, timeout=…)` — gleiche Rückgabe, gleiche
    Ausnahmen; dazu `NichtGesendet`, wenn eine Regel das Senden verbietet."""
    if isinstance(anfrage, str):
        anfrage = urllib.request.Request(anfrage)
    host = host_von(anfrage.full_url)
    warte = _vorher(anfrage, host)
    if warte > 0:
        _schlafen(warte)
    try:
        antwort = urllib.request.urlopen(anfrage, timeout=timeout)
    except urllib.error.HTTPError as e:
        _nachher_fehler(anfrage, host, e)
        raise
    with _sperre:
        _folge_429.pop(host, None)
    return antwort


def stand():
    """Momentaufnahme für Anzeige und Tests: {tag, zaehler, bremse (Restsekunden)}."""
    with _sperre:
        jetzt = _uhr()
        hosts = set(_basis) | set(_neu)
        return {"tag": _tag, "zaehler": {h: _gezaehlt(h) for h in sorted(hosts)},
                "bremse": {h: round(b - jetzt, 1) for h, b in _bremse.items() if b > jetzt}}
