#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Eigene Lesedomains der Serien automatisch finden -> data/series_overrides.json (off-peak).

Viele Mangas haben eine eigene Lesedomain (readchainsawman.online, kingdomscans.com, ...).
Dieses Tool raet je Serie typische Domain-Endungen + Pfade und VERIFIZIERT strikt (Kapitel lebt,
Muell-Kapitel -> Startseite/404). Treffer werden als Overrides gespeichert und ab dann guenstig
genutzt (kein Raten mehr im Normallauf). Nur Serien OHNE bestehenden Override werden geprueft;
manuelle Eintraege bleiben unangetastet. HTTP-lastig, aber ueber Tausende Einzeldomains verteilt
(hoeflich) -> off-peak, NICHT waehrend eines Manga-Laufs.

Aufruf:  python -m tools.discover_dedicated
"""
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.normpath(os.path.join(HERE, ".."))          # SyncManga/
if PKG not in sys.path:
    sys.path.insert(0, PKG)

from syncmanga import readerlink                            # noqa: E402
from syncmanga.parse import norm                            # noqa: E402

CACHE = os.path.normpath(os.path.join(PKG, "..", "..", "SyncDashTray", "System", "md_cache.json"))
OV = os.path.join(PKG, "data", "series_overrides.json")
PROBE_CHAPTER = 1                                            # ein existierendes Kapitel zum Pruefen


def _series_titles(cache_path):
    try:
        c = json.load(open(cache_path, encoding="utf-8"))
    except Exception:
        return []
    seen, out = set(), []
    for e in c.values():
        t = e.get("title")
        if t and not e.get("novel") and norm(t) not in seen:
            seen.add(norm(t))
            out.append(t)
    return out


def _probe(title):
    tpl, _ = readerlink.dedicated_link(readerlink.slug_candidates([title]), PROBE_CHAPTER,
                                       require_images=True)   # tote SEO-Domains (ohne Bilder) verwerfen
    return (norm(title), title, tpl) if tpl else None


def main(workers=16):
    titles = _series_titles(CACHE)
    try:
        data = json.load(open(OV, encoding="utf-8"))
    except Exception:
        data = {"overrides": {}}
    ov = data.get("overrides") or {}
    todo = [t for t in titles if norm(t) not in ov]         # manuelle/bekannte ueberspringen
    print(f"{len(titles)} Serien, {len(todo)} ohne Override -> Eigendomain suchen ...", flush=True)
    found = 0
    with ThreadPoolExecutor(max_workers=workers) as ex:
        for r in ex.map(_probe, todo):
            if r:
                k, title, tpl = r
                ov[k] = {"name": title, "chapter": tpl}
                found += 1
                print(f"  + {title} -> {tpl}", flush=True)
    data["overrides"] = ov
    tmp = OV + ".tmp"                              # atomar schreiben (gefahrlos parallel zum Manga-Lauf)
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, OV)
    print(f"Fertig: {found} neue Eigendomains gefunden -> {OV}", flush=True)


if __name__ == "__main__":
    main()
