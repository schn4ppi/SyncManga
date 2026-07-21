#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Woechentlicher Link-Audit (off-peak, NICHT waehrend eines Manga-Laufs): prueft die gespeicherten
"weiterlesen"-Links ALLER Serien erneut — inkl. Redirect-Ziel- und IDENTITAETS-Check (fuehrt der
Link noch zu DIESER Serie?). Nicht-destruktiv/selbstheilend: tote Links werden nur aus dem Cache
geleert (read_chap=None -> der naechste Manga-Lauf baut sie frisch und verifiziert neu); nichts
anderes wird angefasst. Report -> data/link_audit.json.

Aufruf:  python -m tools.audit_links [pfad/zu/md_cache.json] [--limit N]
Default-Cache: ../Core/md_cache.json (JBs Vollsuite).
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.normpath(os.path.join(HERE, ".."))
if PKG not in sys.path:
    sys.path.insert(0, PKG)
from syncmanga import readerlink  # noqa: E402

DEFAULT_CACHE = os.path.normpath(os.path.join(PKG, "..", "..", "SyncDashTray", "System", "md_cache.json"))
REPORT = os.path.join(PKG, "data", "link_audit.json")


def audit(cache_path, limit=0):
    cache = json.load(open(cache_path, encoding="utf-8"))
    entries = [(k, v) for k, v in cache.items()
               if isinstance(v, dict) and v.get("read_url") and not v.get("novel")]
    if limit:
        entries = entries[:limit]
    checked, dead = 0, []
    for k, v in entries:
        titles = [v.get("title"), v.get("title_romaji")] + (v.get("alt_titles") or [])
        checked += 1
        if readerlink._alive(v["read_url"], [t for t in titles if t]):
            continue
        # tot/falsche Serie -> Link leeren; read_chap=None erzwingt Neuaufbau beim naechsten Lauf
        dead.append({"key": k, "title": v.get("title"), "url": v.get("read_url")})
        v["read_url"], v["read_site"], v["read_urls"], v["read_chap"] = "", "", [], None
        if checked % 50 == 0:
            print(f"  ... {checked}/{len(entries)} geprueft, {len(dead)} tot", flush=True)
    if dead:
        json.dump(cache, open(cache_path, "w", encoding="utf-8"), ensure_ascii=False)
    report = {"ts": time.time(), "checked": checked, "dead": len(dead), "entries": dead[:200]}
    json.dump(report, open(REPORT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"Link-Audit: {checked} geprueft, {len(dead)} tote/falsche geleert -> {REPORT}")
    return report


def main():
    args = [a for a in sys.argv[1:]]
    limit = 0
    if "--limit" in args:
        i = args.index("--limit")
        limit = int(args[i + 1]) if i + 1 < len(args) else 0
        del args[i:i + 2]
    cache_path = args[0] if args else DEFAULT_CACHE
    if not os.path.exists(cache_path):
        sys.exit(f"Cache nicht gefunden: {cache_path}")
    audit(cache_path, limit=limit)


if __name__ == "__main__":
    main()
