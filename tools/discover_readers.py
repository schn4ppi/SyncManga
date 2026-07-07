#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reader selbst finden + bereinigen -> data/readers_pattern.json (haelt "weiterlesen" aktuell).

Off-peak laufen lassen (HTTP-lastig, NICHT waehrend eines Manga-Laufs): prueft die bekannten
Reader erneut (tote raus = Selbst-Bereinigung) und sucht in everythingmoe nach neuen
verifizierbaren Readern (200 fuer echtes Kapitel, 404 fuer Muell-Slug = Selbst-Erweiterung).
So bleibt die Abdeckung ohne Zutun des Nutzers aktuell — spaeter per Dashboard-Button ausloesbar.

Aufruf:  python -m tools.discover_readers   (oder die Datei direkt)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.normpath(os.path.join(HERE, ".."))      # SyncManga/
if PKG not in sys.path:
    sys.path.insert(0, PKG)

from syncmanga import readers, readerlink              # noqa: E402

SNAP = os.path.join(PKG, "data", "readers_moe.json")
OUT = os.path.join(PKG, "data", "readers_pattern.json")


def refresh(snap_path=SNAP, out_path=OUT, verbose=True):
    """Reader-Liste bereinigen + erweitern und speichern. Gibt (aktiv, entfernt, neu) zurueck."""
    snap = readers.refresh_if_stale(snap_path)
    existing = list(readerlink.load_readers(out_path))
    if verbose:
        print(f"Bestehende Reader: {len(existing)} | everythingmoe-Eintraege: "
              f"{len(snap.get('items') or [])}", flush=True)
    alive = [r for r in existing if readerlink.verify_reader(r)]
    dropped = [r["host"] for r in existing if r not in alive]
    found = readerlink.discover(snap, workers=14)      # parallel + kurzer Timeout = deutlich schneller
    merged = readerlink.merge_readers(alive, found)
    before = {r["host"] for r in existing}
    new = [r["host"] for r in merged if r["host"] not in before]
    readerlink.save_readers(out_path, merged)
    if verbose:
        print(f"aktiv: {len(merged)} Reader | entfernt (tot): {dropped or '-'} | neu: {new or '-'}",
              flush=True)
    return merged, dropped, new


if __name__ == "__main__":
    refresh()
