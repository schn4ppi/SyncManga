#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stichproben-Audit aller Reader-Hosts aus JBs Verlauf (JB-Auftrag Runde 32:
'Nimm viele Manga-Stichproben aller Seiten, vergleich mit unserer Datenbank und
unserem Erkennsystem fuer Kapitel/Seite/Manga').

Je Host werden bis zu 2 echte Kapitel-URLs aus dem Firefox-Verlauf gezogen und geprueft:
  1. TOKEN : erkennt unser URL-Parser die Kapitelzahl (chapter_of / has_chapter_token)?
  2. ERNTE : liefert die Serien-Seite den Kapitel-Link zurueck (harvest_chapter_link)?
  3. MAP   : haben wir eine Sitemap-Map fuer den Host?
  4. MUSTER: gibt es einen Pattern-Reader fuer den Host?
Ergebnis -> Manga/data/host_audit.md (Mensch) — Basis fuer neue Muster/Prioritaeten.
Off-peak laufen lassen (HTTP, gepaced). Aufruf:  python -m tools.audit_hosts
"""
import glob
import gzip
import json
import os
import shutil
import sqlite3
import sys
import tempfile
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.normpath(os.path.join(HERE, ".."))
if PKG not in sys.path:
    sys.path.insert(0, PKG)

from syncmanga import readerlink                                    # noqa: E402
from syncmanga.parse import host, chapter_of, is_dynamic            # noqa: E402
from syncmanga.scan import find_firefox_places, BLACKLIST           # noqa: E402
from syncmanga.config import is_dead_reader                         # noqa: E402

OUT = os.path.join(PKG, "data", "host_audit.md")


def _history_samples(per_host=2):
    """{host: [(kapitel_url, zahl), ...]} aus dem Firefox-Verlauf (nur echte Kapitel-URLs)."""
    src = find_firefox_places()
    tmp = os.path.join(tempfile.gettempdir(), "places_audit.sqlite")
    shutil.copy2(src, tmp)
    con = sqlite3.connect(tmp)
    out = defaultdict(list)
    for u, t in con.execute("select url, title from moz_places where url like 'http%'"):
        h = host(u)
        if not h or BLACKLIST.search(h) or is_dead_reader(h) or is_dynamic(h):
            continue
        n = chapter_of(u, t or "")
        if not n or not readerlink.has_chapter_token(u):
            continue
        if len(out[h]) < per_host and all(u != x[0] for x in out[h]):
            out[h].append((u, n))
    con.close()
    return dict(out)


def _map_hosts():
    hosts = set()
    for p in glob.glob(os.path.join(PKG, "data", "*_map.json.gz")):
        try:
            with gzip.open(p, "rt", encoding="utf-8") as f:
                for tpl in json.load(f).values():
                    hosts.add(host(str(tpl)))
                    break                       # 1 Beispiel je Map reicht (gleicher Host)
        except Exception:
            continue
    return {h for h in hosts if h}


def main():
    samples = _history_samples()
    map_hosts = _map_hosts()
    pattern_hosts = {r.get("host") or host(r.get("chapter") or "") for r in readerlink.PATTERN_READERS}
    zeilen = [f"# Reader-Host-Audit ({len(samples)} Hosts aus dem Verlauf)", "",
              "| Host | Kapitel-URL erkannt | Ernte | Map | Muster | Hinweis |",
              "|------|--------------------|-------|-----|--------|---------|"]
    print(f"{len(samples)} Hosts mit Kapitel-Stichproben", flush=True)
    for h in sorted(samples):
        urls = samples[h]
        token = "ja"
        ernte = "-"
        hinweis = ""
        for u, n in urls:
            page = readerlink.series_page_of(u)
            if not page:
                hinweis = "keine Serien-Seite ableitbar"
                continue
            got = readerlink.harvest_chapter_link(page, n)
            if got:
                ernte = "OK"
                break
            st, _f, body = readerlink.fetch_status(page, timeout=8)
            ernte = ("blockiert" if st in (403, 429, 503) or st == 0
                     else "Kapitel nicht gelistet" if st == 200 else f"HTTP {st}")
        zeilen.append(f"| {h} | {token} | {ernte} | "
                      f"{'ja' if h in map_hosts else '-'} | "
                      f"{'ja' if h in pattern_hosts else '-'} | {hinweis} |")
        print(f"  {h:34} Ernte: {ernte}", flush=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(zeilen) + "\n")
    print(f"-> {OUT}", flush=True)


if __name__ == "__main__":
    main()
