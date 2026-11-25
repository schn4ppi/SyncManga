# -*- coding: utf-8 -*-
"""
Gemeinsame HTTP-/Tempo-Helfer des Manga-Kerns — keine quellenspezifische Logik.

Konsolidiert den zuvor in jeder Lookup-Funktion wiederholten urllib-Aufbau
(Request bauen -> urlopen(timeout) -> JSON). Verhalten ist identisch zu vorher:
  - get_json: Standard-Header = UA (wie das alte _get_json); abweichende Header
    (z.B. Kitsu `application/vnd.api+json`) koennen ueberschrieben werden.
  - post_json: setzt UA + Content-Type/Accept = application/json (wie AniList/MangaUpdates).

Gesendet wird ueber den einen Netz-Ausgang `netz.oeffnen` (Budget, Takt je Host, Bremse).
WICHTIG fuer Tests: der Ausgang sendet ueber `urllib.request.urlopen` (Modul-Attribut),
damit ein Mock von `urllib.request.urlopen` greift — keine echten Netzaufrufe in Tests.
"""
import json
import os
import sys
import threading
import time
import urllib.request

from . import netz

try:
    import familie as _fam  # Familienbetrieb: der gemeinsame Kern (CLAUDE.md, „Geteilter Zustand“)
except ImportError:                 # eigenständige App / öffentliches Repo: dort gibt es familie.py nicht
    _fam = None

UA = {"User-Agent": "manga-leseliste/1.0"}


def json_aendern(pfad, aenderung, standard=None, streng=False):
    """Lesen-Ändern-Schreiben einer geteilten JSON-Datei (Register JR68).

    Im Familienbetrieb über `familie.json_aendern` — dieselbe Datei-Sperre wie Tray und
    Werkzeuge; `None` heißt: nichts geschrieben (Sperre nicht bekommen, Schreibfehler oder — mit
    `streng` — Datei vorhanden, aber unlesbar). Das Paket bleibt in sich geschlossen (exe,
    öffentliches Repo, vgl. `fremde_datenbank.py`): ohne `familie.py` derselbe Ablauf atomar,
    aber ohne prozessübergreifende Sperre — dort schreibt nur die eine App."""
    if _fam is not None:
        return _fam.json_aendern(pfad, aenderung, standard=standard, streng=streng)
    try:
        with open(pfad, encoding="utf-8") as f:
            daten = json.load(f)
    except (OSError, ValueError):
        if streng and os.path.exists(pfad):
            return None
        daten = {} if standard is None else standard
    neu = aenderung(daten)
    neu = daten if neu is None else neu
    tmp = f"{pfad}.{os.getpid()}.{threading.get_ident():x}.tmp"
    try:
        os.makedirs(os.path.dirname(os.path.abspath(pfad)), exist_ok=True)
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(neu, f, ensure_ascii=False, indent=1)
        os.replace(tmp, pfad)
    except (OSError, TypeError, ValueError):
        try:
            os.remove(tmp)
        except OSError:
            pass
        return None
    return neu


def _json_delta(aktuell, vorher, nachher):
    """Nur lokal geaenderte Felder uebernehmen; fremde Ergaenzungen bleiben erhalten."""
    if not all(isinstance(d, dict) for d in (aktuell, vorher, nachher)):
        return nachher
    for key in vorher.keys() - nachher.keys():
        if key in aktuell and aktuell[key] == vorher[key]:
            aktuell.pop(key)
    for key, wert in nachher.items():
        if key not in vorher:
            if isinstance(wert, dict) and isinstance(aktuell.get(key), dict):
                aktuell[key] = _json_delta(aktuell[key], {}, wert)
            else:
                aktuell[key] = wert
        elif wert != vorher[key]:
            aktuell[key] = _json_delta(aktuell.get(key), vorher[key], wert)
    return aktuell


def json_delta_speichern(pfad, vorher, nachher):
    """Lange Netzarbeit ausserhalb der Sperre, ihren Feld-Delta unter Dateisperre speichern.

    Immer streng: eine vorhandene, aber unlesbare Datei (z. B. md_cache.json) wird nie durch
    den Delta allein ersetzt — der alte `_save_cache` schrieb den vollen Stand, ein Delta auf
    `{}` hätte Stunden Anreicherung verworfen (Durchsicht JR68). Fehlt die Datei, gilt der volle
    Stand `nachher`."""
    leer = {}

    def aenderung(aktuell):
        return nachher if aktuell is leer else _json_delta(aktuell, vorher, nachher)
    return json_aendern(pfad, aenderung, standard=leer, streng=True)


def use_utf8_stdio():
    """stdout/stderr fuer diesen Prozess auf UTF-8 zwingen (idempotent, fehlertolerant).

    Windows-Konsole/Pipe laeuft sonst mit cp1252 — ein einzelnes Emoji/⚠ im print()
    wirft dann UnicodeEncodeError und bricht den GANZEN Lauf ab (genau so ist am
    2026-07-01 der Manga-Lauf gestorben). errors='replace' ist der letzte Sicherheitsgurt:
    lieber ein Ersatzzeichen als ein Absturz. Nicht-destruktiv, aendert nur die Ausgabe."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass    # stdout kann None sein (windowed .exe) oder ein Test-Capture ohne reconfigure


class Pacer:
    """Globale Tempo-Bremse: mindestens `gap` Sekunden zwischen Aufrufen (threadsicher)."""
    def __init__(self, gap):
        self.gap, self.lock, self.last = gap, threading.Lock(), 0.0

    def wait(self):
        with self.lock:
            w = self.gap - (time.time() - self.last)
            if w > 0:
                time.sleep(w)
            self.last = time.time()


def get_json(url, headers=None, timeout=10):
    """GET -> JSON. Standard-Header = UA; `headers` ueberschreibt komplett (wie bisher)."""
    req = urllib.request.Request(url, headers=headers or UA)
    with netz.oeffnen(req, timeout=timeout) as r:
        return json.load(r)


def post_json(url, payload, headers=None, timeout=10):
    """POST eines JSON-Bodys -> JSON. Header = UA + Content-Type/Accept JSON; `headers` ergaenzt."""
    body = json.dumps(payload).encode("utf-8")
    h = {**UA, "Content-Type": "application/json", "Accept": "application/json"}
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, data=body, headers=h)
    with netz.oeffnen(req, timeout=timeout) as r:
        return json.load(r)
