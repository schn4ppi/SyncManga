# -*- coding: utf-8 -*-
"""
Gemeinsame HTTP-/Tempo-Helfer des Manga-Kerns — keine quellenspezifische Logik.

Konsolidiert den zuvor in jeder Lookup-Funktion wiederholten urllib-Aufbau
(Request bauen -> urlopen(timeout) -> JSON). Verhalten ist identisch zu vorher:
  - get_json: Standard-Header = UA (wie das alte _get_json); abweichende Header
    (z.B. Kitsu `application/vnd.api+json`) koennen ueberschrieben werden.
  - post_json: setzt UA + Content-Type/Accept = application/json (wie AniList/MangaUpdates).

WICHTIG fuer Tests: Aufrufe gehen ueber `urllib.request.urlopen` (Modul-Attribut),
damit ein Mock von `urllib.request.urlopen` greift — keine echten Netzaufrufe in Tests.
"""
import json
import sys
import threading
import time
import urllib.request

UA = {"User-Agent": "manga-leseliste/1.0"}


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
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def post_json(url, payload, headers=None, timeout=10):
    """POST eines JSON-Bodys -> JSON. Header = UA + Content-Type/Accept JSON; `headers` ergaenzt."""
    body = json.dumps(payload).encode("utf-8")
    h = {**UA, "Content-Type": "application/json", "Accept": "application/json"}
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, data=body, headers=h)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)
