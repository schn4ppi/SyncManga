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
from syncmanga.common import json_aendern  # noqa: E402
from syncmanga.enrich import cache_fuer_werkzeuge, cache_keys_for_h  # noqa: E402
from syncmanga.parse import norm  # noqa: E402

OV = os.path.join(PKG, "data", "series_overrides.json")
BROKEN = os.path.join(PKG, "data", "broken_links.json")
ARCHIVE = os.path.join(PKG, "data", "broken_links.done.json")   # verarbeitete Meldungen (Historie)


def overrides_entfernen(path, reports, cache):
    """Nur gemeldete Serien aus dem aktuell gesperrten Override-Dokument nehmen."""
    keys = set()
    for r in reports or []:
        keys.add(norm((r.get("name") or "").strip()))
        for ck in cache_keys_for_h(cache, r.get("h")):
            keys |= {norm(ck), norm((cache.get(ck) or {}).get("title") or "")}
    removed = 0
    def aenderung(data):
        nonlocal removed
        ov = data.get("overrides") or {}
        for k in keys:
            if k and k in ov:
                del ov[k]
                removed += 1
                print(f"  - kaputten Override entfernt: {k}", flush=True)
        data["overrides"] = ov
    return removed if json_aendern(path, aenderung, standard={"overrides": {}}, streng=True) is not None else None


def meldungen_archivieren(path, reports):
    return json_aendern(path, lambda alt: alt + (reports or []), standard=[], streng=True)


def main():
    try:
        reports = json.load(open(BROKEN, encoding="utf-8"))
    except Exception:
        print("Keine data/broken_links.json (vom ⚠-Export) gefunden - nichts zu tun.", flush=True)
        return 0
    if not reports:
        return 0
    cache = cache_fuer_werkzeuge(PKG, sys.argv[1] if len(sys.argv) > 1 else None)
    removed = overrides_entfernen(OV, reports, cache)
    if removed is None:
        print("fix_broken: series_overrides.json gesperrt; Meldungen bleiben erhalten.")
        return 0
    # Meldungen archivieren + die Eingangsdatei leeren (damit sie nicht erneut verarbeitet wird)
    try:
        if meldungen_archivieren(ARCHIVE, reports) is not None:
            json_aendern(BROKEN, lambda aktuell: [r for r in aktuell if r not in reports], standard=[])
    except Exception:
        pass
    print(f"Fertig: {removed} kaputte Overrides entfernt -> werden neu aufgeloest.", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
