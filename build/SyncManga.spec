# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller-Spec fuer die eigenstaendige App „SyncManga" (NUR der syncmanga-Kern + Tray,
KEIN Mail-/Beleg-Code, KEINE privaten Daten). Erzeugt eine fenster-lose .exe.

Build (aus dem Repo-Root):
    pyinstaller --noconfirm --clean --distpath dist \
        --workpath %TEMP%\\syncmanga_pyi build\\SyncManga.spec
"""
import os

ROOT = os.path.abspath(os.path.join(SPECPATH, ".."))   # SPECPATH = build/

a = Analysis(
    [os.path.join(SPECPATH, "SyncManga.py")],
    pathex=[ROOT],
    binaries=[],
    datas=[
        (os.path.join(ROOT, "syncmanga", "templates"), "syncmanga/templates"),
        # Laufzeit-Daten buendeln. WICHTIG seit v29: die Sitemap-Maps (*.json.gz, ~1.3 MB) sind
        # die HAUPT-Linkquelle (readerlink._sitemap_lookup, 53k Templates) — ohne sie haette die
        # Standalone nur Muster-Reader + Suche. projects.json bleibt draussen (JB-spezifisch).
        *[(os.path.join(ROOT, "data", f), "data") for f in (
            "series_overrides.json",   # die ~660 verifizierten Direkt-Lese-Links
            "overrides.json",          # NAME_FIX (Titel-/Typ-Korrekturen)
            "sources.json",            # Reader-Quellen + Sperrliste (self-updatebar)
            "readers_pattern.json",    # Reader-Muster (readerlink)
            "readers_moe.json",        # Reader-Verzeichnis (readers.py / +Alt)
            "mangafire_map.json.gz",   # Sitemap-DBs: exakte Serien-Templates inkl. ID-Suffixe
            "weebcentral_map.json.gz",
            "roliascan_map.json.gz",
            "mangaread_map.json.gz",
            "mgread_map.json.gz",
        )],
        (os.path.join(ROOT, "README.md"), "."),
        (os.path.join(ROOT, "Anleitung.html"), "."),   # 📖-Anleitung DE (Liste verlinkt relativ)
        (os.path.join(ROOT, "Guide.html"), "."),       # 📖-Guide EN (Sprache folgt dem OS)
    ],
    hiddenimports=["pystray._win32", "PIL._tkinter_finder"],
    hookspath=[],
    runtime_hooks=[],
    excludes=["SyncEngine", "gmail_sync", "imap_sync", "mailsort", "belege_vorbereiten"],
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
    # UPX bewusst AUS: gepackte PyInstaller-exes triggern Antivirus-Heuristiken deutlich
    # oefter (VirusTotal-Befund v0.3.0: 5/70 generische Treffer). Groessere Datei > Fehlalarm.
    upx=False,
    console=False,             # Tray-App, kein Konsolenfenster
    disable_windowed_traceback=False,
    # Familien-Emblem (S im Gleichdick, gruen) als Datei-Icon — erzeugt via make_icon.py
    icon=os.path.join(SPECPATH, "SyncManga.ico"),
    # Metadaten in den exe-Eigenschaften (Firma/Beschreibung/Version) -> SmartScreen/Explorer
    # zeigen etwas Serioeses statt "Unbekannter Herausgeber ohne Angaben" (JB-Wunsch 2b).
    version=os.path.join(SPECPATH, "version_info.txt"),
)
