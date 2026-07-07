# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller-Spec fuer die eigenstaendige App "SyncManga" (nur der syncmanga-Kern + Tray).
Erzeugt eine fensterlose .exe. KEIN Mail-/Beleg-Code, KEINE privaten Daten.

Dieses Open-Source-Repo enthaelt BEWUSST keine vorgefertigte Direktlink-Sammlung
(series_overrides.json) und keine Sitemap-Kataloge (*_map.json.gz) -> die Leseliste entsteht
aus dem eigenen Browser-Verlauf des Nutzers. Gebuendelt werden nur die generischen Tool-Daten.

Build (aus dem Repo-Root, oder einfach build\\build.bat doppelklicken):
    pyinstaller --noconfirm --clean --distpath . --workpath %TEMP%\\syncmanga_pyi build\\SyncManga.spec
"""
import os

ROOT = os.path.abspath(os.path.join(SPECPATH, ".."))   # SPECPATH = build/

a = Analysis(
    [os.path.join(SPECPATH, "SyncManga.py")],
    pathex=[ROOT],
    binaries=[],
    datas=[
        (os.path.join(ROOT, "syncmanga", "templates"), "syncmanga/templates"),
        *[(os.path.join(ROOT, "data", f), "data") for f in (
            "overrides.json",          # NAME_FIX (Titel-/Typ-Korrekturen)
            "sources.json",            # Reader-Quellen + Sperrliste (self-updatebar)
            "readers_pattern.json",    # Reader-Muster (readerlink)
        )],
        (os.path.join(ROOT, "README.md"), "."),
    ],
    hiddenimports=["pystray._win32", "PIL._tkinter_finder"],
    hookspath=[],
    runtime_hooks=[],
    excludes=["gmail_sync", "imap_sync", "mailsort", "belege_vorbereiten"],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="SyncManga",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    # UPX bewusst AUS: gepackte PyInstaller-exes triggern Antivirus-Heuristiken oefter.
    upx=False,
    console=False,             # Tray-App, kein Konsolenfenster
    disable_windowed_traceback=False,
    icon=None,
    # Metadaten (Firma/Beschreibung/Version) in den exe-Eigenschaften -> serioeser in SmartScreen.
    version=os.path.join(SPECPATH, "version_info.txt"),
)
