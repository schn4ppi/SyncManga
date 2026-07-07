#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LIVE-Onlineprüfung der Quellen-Stufen (JB Runde 42: 'prüf online mit').

Die pytest-Suite läuft bewusst OHNE Netz (mockbar, schnell, stabil) — dieses Tool ist das
Gegenstück: es prüft die Kern-Quellen GEGEN DIE ECHTEN SEITEN mit bekannten Serien und
druckt OK/FAIL je Stufe. Bei FAIL hat sich die Seite geändert -> Claude zeigen.

Aufruf:  python -m tools.live_smoke     (~1-2 Minuten, höflich getaktet)
"""
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.normpath(os.path.join(HERE, ".."))
if PKG not in sys.path:
    sys.path.insert(0, PKG)

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from syncmanga import readerlink                              # noqa: E402
from syncmanga.sources import (md_lookup, md_chapter_link,    # noqa: E402
                               wt_chapter_link, ck_chapter_link)

readerlink.load_readers(os.path.join(PKG, "data", "readers_pattern.json"))
fails = 0


def check(name, fn, want=None):
    global fails
    try:
        got = fn()
    except Exception as ex:
        got = f"EXCEPTION {type(ex).__name__}: {ex}"
    ok = bool(got) and (want is None or want in str(got))
    print(("OK   " if ok else "FAIL "), name, "->", str(got)[:90])
    fails += 0 if ok else 1


check("MangaDex-Suche (Titel + all_titles)",
      lambda: md_lookup("The Boxer").get("md_id"))
check("MangaDex EN-Kapitel (chapter_only, Usogui hat EN)",
      lambda: md_chapter_link(md_lookup("Usogui").get("md_id"), 100,
                              chapter_only=True)[0], want="mangadex.org/chapter/")
check("Webtoons-Suche + Episode-Verify",
      lambda: wt_chapter_link(["The Boxer"], 3)[0], want="title_no=")
check("Madara-Such-Ernte (?s=&post_type=wp-manga)",
      lambda: readerlink.search_slug_link(
          ["Martial Peak"], 100, mtype="manhwa")[0], want="chapter")
check("Muster-Reader direkt (mgeko)",
      lambda: readerlink._fast_alive(
          "https://www.mgeko.cc/reader/en/solo-leveling-chapter-100-eng-li/"))
check("Comick-Gruppen-Info (Tracker-Metadaten)",
      lambda: ck_chapter_link("Solo Leveling", 110)[2])
# comix: JS-Suche ohne SSR/Sitemap -> Stufe kann leer sein, kein FAIL (ehrliche Grenze)
try:
    _cx = readerlink.cx_chapter_link(["Solo Leveling"], 100)[0]
    print("INFO ", "comix-Such-Ernte (optional, JS-Suche) ->", _cx or "(leer — erwartbar)")
except Exception as _ex:
    print("INFO ", "comix-Such-Ernte (optional) -> Fehler:", type(_ex).__name__)

print(f"\n{'ALLES OK' if not fails else str(fails) + ' Stufe(n) FAIL — Seite(n) geändert?'}")
sys.exit(1 if fails else 0)
