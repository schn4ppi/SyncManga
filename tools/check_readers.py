#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI-Wrapper: Status der Haupt-Lese-Seiten pruefen -> data/reader_status.json (Quellen-Ampel).
Die Logik liegt in syncmanga.readers (refresh_status; wird auch vor jedem Render aufgerufen).

Aufruf:  python -m tools.check_readers
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.normpath(os.path.join(HERE, ".."))
if PKG not in sys.path:
    sys.path.insert(0, PKG)
from syncmanga import readers                                  # noqa: E402


def main():
    data = readers.refresh_status()
    for r in data["readers"].values():
        print(f"  {r['status']:10} {r['name']}", flush=True)


if __name__ == "__main__":
    main()
