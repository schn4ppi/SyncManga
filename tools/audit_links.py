#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Woechentlicher Link-Audit (off-peak, NICHT waehrend eines Manga-Laufs): prueft die gespeicherten
"weiterlesen"-Links ALLER Serien erneut — inkl. Redirect-Ziel- und IDENTITAETS-Check (fuehrt der
Link noch zu DIESER Serie?). Nicht-destruktiv/selbstheilend: nur nachweislich tote Links ("no",
"gone" bei funktionierendem Netz) werden aus dem Cache geleert (read_chap=None -> der naechste
Manga-Lauf baut sie frisch und verifiziert neu); blocked/down gelten als nicht pruefbar, "odd"
(fremde Serie oder Drosselseite) wird nur gezaehlt. Nichts anderes wird angefasst. Report -> data/link_audit.json.

Aufruf:  python -m tools.audit_links [pfad/zu/md_cache.json] [--limit N]
Default-Cache: ../../SyncDashTray/System/md_cache.json (JBs Vollsuite).
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
from syncmanga.common import json_aendern  # noqa: E402

DEFAULT_CACHE = os.path.normpath(os.path.join(PKG, "..", "..", "SyncDashTray", "System", "md_cache.json"))
REPORT = os.path.join(PKG, "data", "link_audit.json")


def audit(cache_path, limit=0):
    cache = json.load(open(cache_path, encoding="utf-8"))
    entries = [(k, v) for k, v in cache.items()
               if isinstance(v, dict) and v.get("read_url") and not v.get("novel")]
    if limit:
        entries = entries[:limit]
    checked, dead, uncheckable, unclear = 0, [], 0, 0
    netz = None   # erst beim ersten 'gone' pruefen, danach je 'gone' neu (Netzabriss im Lauf)
    for k, v in entries:
        titles = [v.get("title"), v.get("title_romaji")] + (v.get("alt_titles") or [])
        checked += 1
        status = readerlink._alive_status(v["read_url"], [t for t in titles if t])
        if status == "odd":
            unclear += 1
            continue
        if status == "gone" and netz is not False:
            netz = readerlink.netz_ok()
        if status in ("blocked", "down") or (status == "gone" and not netz):
            uncheckable += 1
            continue
        if status not in ("no", "gone"):
            continue
        # Nachweislich tot -> Link leeren; read_chap=None erzwingt Neuaufbau beim naechsten Lauf
        dead.append({"key": k, "title": v.get("title"), "url": v.get("read_url")})
        if checked % 50 == 0:
            print(f"  ... {checked}/{len(entries)} geprueft, {len(dead)} tot", flush=True)
    if dead:
        if _tote_links_entfernen(cache_path, dead) is None:
            print("Link-Audit: Cache gesperrt; Links bleiben fuer den naechsten Lauf erhalten.")
            return None
    report = {"ts": time.time(), "checked": checked, "dead": len(dead), "entries": dead[:200],
              "uncheckable": uncheckable, "unclear": unclear}
    json.dump(report, open(REPORT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"Link-Audit: {checked} geprueft, {len(dead)} tote geleert, "
          f"{uncheckable} nicht pruefbar, {unclear} unklar -> {REPORT}")
    return report


def _tote_links_entfernen(cache_path, dead):
    """Nur die tatsaechlich gepruefte URL leeren, neuere Reparaturen behalten."""
    def aenderung(cache):
        for rep in dead:
            v = cache.get(rep["key"])
            if isinstance(v, dict) and v.get("read_url") == rep["url"]:
                v.update(read_url="", read_site="", read_urls=[], read_chap=None)
    return json_aendern(cache_path, aenderung, standard={}, streng=True)


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
