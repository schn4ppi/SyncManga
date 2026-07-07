#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Self-Healing: gemeldete kaputte Links verarbeiten -> data/series_overrides.json (off-peak).

Der ⚠-Knopf in der Liste exportiert `broken_links.json` (gemeldete Serien). Lege die Datei nach
SyncManga/data/broken_links.json (oder sie wird dort gesucht). Dieses Tool entfernt fuer jede
gemeldete Serie den (kaputten) Override -> sie wird beim naechsten Discovery-/Manga-Lauf neu
aufgeloest (andere Quelle/Suche). Nicht-destruktiv ausser dem gezielten Override-Entfernen.

In refresh_overrides eingebunden (laeuft VOR der Discovery, damit gleich neu aufgeloest wird).

Aufruf:  python -m tools.fix_broken
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.normpath(os.path.join(HERE, ".."))
if PKG not in sys.path:
    sys.path.insert(0, PKG)
from syncmanga.parse import norm                                # noqa: E402

OV = os.path.join(PKG, "data", "series_overrides.json")
BROKEN = os.path.join(PKG, "data", "broken_links.json")
ARCHIVE = os.path.join(PKG, "data", "broken_links.done.json")   # verarbeitete Meldungen (Historie)


def main():
    try:
        reports = json.load(open(BROKEN, encoding="utf-8"))
    except Exception:
        print("Keine data/broken_links.json (vom ⚠-Export) gefunden - nichts zu tun.", flush=True)
        return 0
    try:
        data = json.load(open(OV, encoding="utf-8"))
    except Exception:
        data = {"overrides": {}}
    ov = data.get("overrides") or {}
    removed = 0
    for r in (reports or []):
        k = norm((r.get("name") or "").strip())
        if k and k in ov:
            del ov[k]
            removed += 1
            print(f"  - kaputten Override entfernt: {r.get('name')}", flush=True)
    data["overrides"] = ov
    tmp = OV + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, OV)
    # Meldungen archivieren + die Eingangsdatei leeren (damit sie nicht erneut verarbeitet wird)
    try:
        old = json.load(open(ARCHIVE, encoding="utf-8")) if os.path.exists(ARCHIVE) else []
        json.dump(old + (reports or []), open(ARCHIVE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        os.remove(BROKEN)
    except Exception:
        pass
    print(f"Fertig: {removed} kaputte Overrides entfernt -> werden neu aufgeloest.", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
