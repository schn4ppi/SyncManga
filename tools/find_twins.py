#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Zwillings-Report (JB 07.07.2026, 'unter einen Deckelhut'): findet Serien, die MEHRFACH im Cache
liegen. Reine Anzeige, schreibt NICHTS.

  A) Echte Zwillinge: gleiche MangaBaka-ID (md_id), mehrere gescannte Namen -> werden beim Render
     bereits zusammengefuehrt (read_urls vereint, seit dem Union-Merge). Nur zur Info + Zaehlung.
  B) VERDACHT (die Liste zeigt sie doppelt): (fast) gleicher Titel, ABER verschiedene/fehlende md_id.
     Das sind die, die noch getrennt sind -> Fix: eine mb_id per ✔-Quelle (mangabaka.org-Seite)
     bestaetigen; dann fallen sie unter einen Hut.

Aufruf:  python -m tools.find_twins
"""
import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.normpath(os.path.join(HERE, ".."))
if PKG not in sys.path:
    sys.path.insert(0, PKG)

from syncmanga.parse import norm   # noqa: E402


def load_cache():
    for p in (os.path.join(PKG, "..", "Core", "md_cache.json"),
              os.path.join(os.getcwd(), "cache", "md_cache.json")):
        if os.path.exists(os.path.normpath(p)):
            return json.load(open(os.path.normpath(p), encoding="utf-8"))
    return {}


def report(cache):
    """-> (A_gruppen, B_verdachtsgruppen). Rein/testbar."""
    by_id = collections.defaultdict(list)
    by_title = collections.defaultdict(list)
    for k, e in cache.items():
        if not isinstance(e, dict) or e.get("novel"):
            continue
        if e.get("md_id"):
            by_id[e["md_id"]].append(k)
        t = norm(e.get("title_en") or e.get("title") or "")
        if len(t) >= 6:
            by_title[t].append((k, e.get("md_id")))
    a = {md: ks for md, ks in by_id.items() if len(ks) > 1}
    # B: gleicher Titel, aber >1 verschiedene md_id (bzw. fehlende) -> noch NICHT gemerged
    b = {}
    for t, entries in by_title.items():
        ids = {md for _k, md in entries}
        if len(entries) > 1 and len(ids) > 1:
            b[t] = entries
    return a, b


def main():
    cache = load_cache()
    a, b = report(cache)
    print(f"A) Echte Zwillinge (gleiche md_id, >1 Key) — schon gemerged: {len(a)} Gruppen")
    print(f"B) VERDACHT (gleicher Titel, versch./fehlende md_id) — noch getrennt: {len(b)} Gruppen\n")
    print("Diese hier lohnt sich per ✔-Quelle (mangabaka.org) zu pinnen:")
    for t, entries in sorted(b.items())[:40]:
        title = cache[entries[0][0]].get("title_en") or cache[entries[0][0]].get("title") or t
        ids = ", ".join(str(md) for _k, md in entries)
        print(f"   {str(title)[:44]:44}  ({len(entries)}x)  ids: {ids[:40]}")


if __name__ == "__main__":
    sys.exit(main())
