# -*- coding: utf-8 -*-
"""
PyInstaller-Einstieg der eigenständigen App „SyncManga".

Startet das schlanke Tray. Nutzerdaten (config.json, cache/, Manga_Leseliste.html) landen
in einem schreibbaren User-Ordner (%LOCALAPPDATA%\\SyncManga); die mitgelieferten Daten
(overrides.json, sources.json, Templates) kommen aus dem PyInstaller-Bundle.
"""
import os
import sys


def _data_dir():
    if getattr(sys, "frozen", False):                       # als .exe gepackt
        base = os.path.join(os.environ.get("LOCALAPPDATA") or os.path.expanduser("~"), "SyncManga")
    else:                                                    # aus dem Quellbaum
        base = os.getcwd()
    os.makedirs(base, exist_ok=True)
    return base


def main():
    from syncmanga.tray import main as tray_main
    tray_main([_data_dir()])


if __name__ == "__main__":
    main()
