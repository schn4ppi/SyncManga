# -*- coding: utf-8 -*-
"""exe-Datei-Icon aus dem Familien-Emblem erzeugen (JB-Go 22.07.2026, Release v0.4.1).

Rendert das RUHIGE Manga-Emblem (S im Gleichdick, grün — syncmanga.tray.emblem_bild)
als 256er-Master und schreibt `build/SyncManga.ico` mit allen Windows-Größen
(16/24/32/48/64/128/256). Beide Specs + Inno-Setup zeigen auf diese Datei.
Neu erzeugen nur nötig, wenn sich das Emblem ändert:  python build/make_icon.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))                # SyncManga\System\build
SYSTEM = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, SYSTEM)

from syncmanga import tray  # noqa: E402

ZIEL = os.path.join(HERE, "SyncManga.ico")
GROESSEN = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]


def main():
    master = tray.emblem_bild(0, groesse=256)      # ruhiger Zustand, ohne Punkt/Rahmen
    master.save(ZIEL, sizes=GROESSEN)
    print(f"OK: {ZIEL} ({os.path.getsize(ZIEL)} Bytes, {len(GROESSEN)} Größen)")


if __name__ == "__main__":
    main()
