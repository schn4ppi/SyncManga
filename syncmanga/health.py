# -*- coding: utf-8 -*-
"""
Gesundheit — Reader-Domains pruefen UND Quellen-Status verbuchen.

Teil 1: Automatische Gesundheitspruefung von Reader-Domains.
Teil 2 (Runde 28 aus srcstatus.py hierher gezogen, JB: 'mehr Dateien zusammenfuegen'):
Quellen-Status je externer DB-Quelle (record/is_down/snapshot/load/save).

Erkennt die Fehlerarten, die ein reiner HTTP-Status (link_ok) NICHT sieht und die JB beim
Durchklicken gefunden hat:
  - Startseiten-Redirect: die Kapitel-URL leitet auf die Domain-Wurzel um (Pfad verloren).
  - Cloudflare-Challenge / "Just a moment" / Connection-Timeout (522) -> Nutzer kommt nicht rein.
  - Server-Fehler (5xx) / Verbindungsabbruch.

Geprueft wird pro DOMAIN (nicht pro Serie -> ~Dutzende statt Hunderte) anhand EINER
Beispiel-Kapitel-URL, Ergebnis je Domain gecacht (reader_health.json). So erledigt das
System das Fact-Checking selbst, statt es dem Nutzer aufzubuerden.

Die Klassifikation ist eine reine, testbare Funktion; der Netzzugriff ist injizierbar.
"""
import json
import os
import threading
import time
import urllib.error
import urllib.request
from urllib.parse import urlparse

from .common import Pacer
from .parse import host

HEALTH_PACER = Pacer(0.3)          # hoeflich gegen die Reader-Seiten
RECHECK_DAYS = 14                  # Domain-Gesundheit so lange cachen, bevor neu geprueft wird
# Marker einer Cloudflare-/Bot-Schutz-Zwischenseite (Nutzer sieht keinen Manga).
CF_MARKERS = ("just a moment", "checking your browser", "cf-chl", "attention required",
              "enable javascript and cookies", "ddos-guard")


def classify(sample_url, final_url, status, body, error):
    """Reine Klassifikation -> 'alive' | 'dead' | 'blocked'.

    NUR EIN definitives Signal ergibt 'dead': die Kapitel-URL leitet auf die Domain-Wurzel um
    (Kapitel-Pfad verloren = Kapitel wirklich weg). Alles Transiente/Unsichere -> 'blocked'.

    JB-Regel (05.07.2026, No-Go): einen funktionierenden Link NIE wegen Netz/Bot-Sperre/5xx als
    tot loeschen. Ein Timeout, ein 5xx oder eine Cloudflare-Challenge heisst 'gerade nicht
    pruefbar' (im Browser nutzbar), NICHT 'tot'. Frueher wurde all das als 'dead' gewertet ->
    bei schlechtem Netz loeschte der Audit funktionierende read_urls (JB-Vorfall)."""
    if error:
        return 'blocked'                     # Timeout/Verbindungsfehler -> nicht pruefbar, nie tot
    if status and status >= 500:
        return 'blocked'                     # Server-Hickup (5xx/52x) -> transient, nie tot
    low = (body or '')[:4000].lower()
    if any(m in low for m in CF_MARKERS):
        return 'blocked'                     # Cloudflare/Bot-Challenge -> im Browser nutzbar
    orig_path = (urlparse(sample_url).path or '').rstrip('/')
    final_path = (urlparse(final_url or sample_url).path or '').rstrip('/')
    if orig_path and not final_path:         # hatte Kapitel-Pfad, landet auf "/" -> Kapitel weg
        return 'dead'
    return 'alive'


def _fetch(url, timeout=6):
    """Echter Fetch: Browser-UA, folgt Redirects, liest nur den Anfang. -> (final_url, status, body)."""
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        body = r.read(4000).decode("utf-8", "replace")
        return r.geturl(), getattr(r, "status", 200), body


def check_domain(samples, fetch=None):
    """Eine Domain ueber EINE oder MEHRERE Beispiel-Kapitel-URLs pruefen -> 'dead'/'alive'.

    Lebt, sobald EINE Stichprobe lebt -> eine einzelne tote Stichprobe (geloeschtes Kapitel,
    Redirect zur Startseite) verfaelscht eine grosse Multi-Serien-Domain (z.B. MangaDex) nicht.
    """
    fetch = fetch or _fetch
    urls = [samples] if isinstance(samples, str) else list(samples)
    blocked = False          # transientes/Bot-Signal (4xx, 5xx, CF, Timeout) -> schuetzt vor 'dead'
    definit_dead = False     # nur der Startseiten-Redirect (Kapitel wirklich weg) zaehlt
    for u in urls:
        try:
            v = classify(u, *fetch(u), None)
            if v == 'alive':
                return 'alive'
            if v == 'dead':
                definit_dead = True
            else:
                blocked = True          # 'blocked' (CF/5xx) -> NICHT tot
        except urllib.error.HTTPError:
            blocked = True              # 4xx Bot-Block ODER 5xx -> beides transient, NICHT tot
        except Exception:
            blocked = True              # Timeout/Verbindungsfehler -> NICHT tot (frueher: 'dead')
    # 'dead' NUR bei definitivem Signal UND ohne jedes transiente/Bot-Signal (JB-Regel).
    if blocked:
        return 'alive'
    return 'dead' if definit_dead else 'alive'


def check_domains(samples, cache_path, fetch=None, recheck_days=RECHECK_DAYS, now=None, pacer=HEALTH_PACER):
    """`samples` = {domain: beispiel_kapitel_url}. Prueft je Domain (gecacht) -> set toter Domains.

    Bereits frisch (< recheck_days) gepruefte Domains werden uebersprungen; nur neue/abgelaufene
    werden tatsaechlich abgefragt. Ergebnis pro Domain in cache_path persistiert.
    """
    now = now if now is not None else time.time()
    cache = {}
    if os.path.exists(cache_path):
        try:
            with open(cache_path, encoding="utf-8") as f:
                cache = json.load(f)
        except (OSError, ValueError):
            cache = {}
    for dom, url in samples.items():
        c = cache.get(dom)
        if c and (now - c.get('ts', 0)) < recheck_days * 86400:
            continue
        if pacer:
            pacer.wait()
        cache[dom] = {'status': check_domain(url, fetch), 'ts': now}
    try:
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(cache, f)
    except OSError:
        pass
    return {dom for dom, c in cache.items() if c.get('status') == 'dead'}


def domain_samples(items, per_host=2):
    """Pro Reader-Host bis zu `per_host` Beispiel-Kapitel-URLs (mit Pfad) -> {host: [url, ...]}.

    Mehrere Stichproben, damit eine einzelne tote (geloeschtes Kapitel) eine grosse Domain
    nicht faelschlich als tot stempelt.
    """
    out = {}
    for e in (items.values() if hasattr(items, "values") else items):
        readers = e.get('readers') or ([{'host': host(e.get('url')), 'url': e.get('url')}]
                                       if e.get('url') else [])
        for r in readers:
            u = r.get('url')
            if not u:
                continue
            h = r.get('host') or host(u)
            if not h or not (urlparse(u).path or '').rstrip('/'):
                continue
            lst = out.setdefault(h, [])
            if u not in lst and len(lst) < per_host:
                lst.append(u)
    return out


def merge_auto_dead(items, cache_path, fetch=None, alive_hosts=None):
    """Domains aus items automatisch pruefen und tote in config.DEAD_READERS uebernehmen (Laufzeit).

    Bereits bekannte (manuelle) Tote werden nicht erneut geprueft. `alive_hosts` (z.B. das
    everythingmoe-Live-Verzeichnis) gilt als kuratiert lebend -> wird gar nicht geprueft und nie
    als tot markiert. So erkennt das System tote Quellen SELBST, ohne Last fuer den Nutzer.
    Gibt die neu erkannten toten Domains zurueck.
    """
    from . import config
    alive = {h.lower() for h in (alive_hosts or set())}
    samples = {h: u for h, u in domain_samples(items).items()
               if not config.is_dead_reader(h) and h.lower() not in alive}
    auto = check_domains(samples, cache_path, fetch=fetch)
    if auto:
        config.DEAD_READERS = tuple(config.DEAD_READERS) + tuple(sorted(auto))
    return auto


# ---------------- Quellen-Status (frueher srcstatus.py) ----------------
# Protokolliert pro externer Quelle Erfolg/Fehler/Latenz und speist drei Dinge (JB):
#   1. die Fallback-Kette in `catalog.lookup` (eine "down"-Quelle wird uebersprungen),
#   2. das Dashboard-Fehler-Panel in `render` (welche Quelle klemmt + letzte Meldung),
#   3. die Tray-Ampel.
# NICHT-destruktiv: ausschliesslich Statusdaten. Modul-global, threadsicher, persistierbar.

_LOCK = threading.Lock()
# source -> {ok, last_ok, last_err, error, fails, calls, status, latency}
_STATE = {}

DEGRADED_FAILS = 3      # so viele Fehler in Folge -> "degraded"
DOWN_FAILS = 6          # ... -> "down" (Fallback-Kette ueberspringt die Quelle)


def _blank():
    return {"ok": True, "last_ok": 0.0, "last_err": 0.0, "error": "",
            "fails": 0, "calls": 0, "status": "ok", "latency": None}


def record(source, ok, error="", latency=None):
    """Einen Aufruf einer Quelle verbuchen -> aktueller Status ('ok'/'degraded'/'down')."""
    with _LOCK:
        s = _STATE.setdefault(source, _blank())
        s["calls"] += 1
        now = time.time()
        if ok:
            s.update(ok=True, last_ok=now, fails=0, status="ok", error="")
        else:
            s["ok"] = False
            s["last_err"] = now
            s["fails"] += 1
            s["error"] = str(error)[:200]
            s["status"] = ("down" if s["fails"] >= DOWN_FAILS
                           else "degraded" if s["fails"] >= DEGRADED_FAILS else "ok")
        if latency is not None:
            s["latency"] = round(latency, 3)
        return s["status"]


def is_down(source):
    """True, wenn die Quelle als 'down' gilt (Fallback-Kette soll sie ueberspringen)."""
    with _LOCK:
        s = _STATE.get(source)
        return bool(s and s["status"] == "down")


def snapshot():
    """Kopie des gesamten Status (fuer Render-Panel/Tray)."""
    with _LOCK:
        return {k: dict(v) for k, v in _STATE.items()}


def reset():
    """Status leeren (Tests)."""
    with _LOCK:
        _STATE.clear()


def load(path):
    """Persistierten Quellen-Status laden (best effort; fehlt/kaputt -> leer)."""
    global _STATE
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            with _LOCK:
                _STATE = {k: {**_blank(), **v} for k, v in data.items() if isinstance(v, dict)}
    except (OSError, ValueError):
        pass


def save(path):
    """Quellen-Status persistieren (best effort, nie den Lauf killen)."""
    with _LOCK:
        data = {k: dict(v) for k, v in _STATE.items()}
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
    except OSError:
        pass
