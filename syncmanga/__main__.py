# -*- coding: utf-8 -*-
"""
Standalone-Einstieg der App „SyncManga": scan -> enrich -> render.

Aufruf:
    python -m syncmanga [DATENORDNER] [--lang de|en] [--full]

DATENORDNER (Default: aktuelles Verzeichnis) enthaelt config.json, overrides.json,
cache/ und die Ausgabe Manga_Leseliste.html. Dieser Einstieg ist NUR fuer die
eigenstaendige App; JBs Vollsuite nutzt weiter SyncEngine/manga_update.py.

Sprache: --lang > Settings(config.json:lang) > OS-Locale (de* -> Deutsch) > Englisch.
"""
import os
import sys

from . import config, i18n
from .scan import scan_all
from .enrich import enrich
from .render import render

PKG_DIR = os.path.dirname(os.path.abspath(__file__))
# Mitgelieferte Standard-Overrides (data/overrides.json neben dem Paket), falls der
# Datenordner keine eigene Datei hat.
BUNDLED_OVERRIDES = os.path.normpath(os.path.join(PKG_DIR, "..", "data", "overrides.json"))
BUNDLED_SOURCES = os.path.normpath(os.path.join(PKG_DIR, "..", "data", "sources.json"))
# Die ~660 verifizierten Direkt-Lese-Links (series_overrides.json) sind der Hauptnutzen fuer
# Freunde: ohne sie gaebe es nur Suchlinks. Daher gebuendelt + beim Start geladen.
BUNDLED_SERIES = os.path.normpath(os.path.join(PKG_DIR, "..", "data", "series_overrides.json"))


def resolve_paths(data_dir):
    """Alle Dateipfade der Standalone-App unter einem Datenordner (rein, testbar)."""
    return {
        "settings": os.path.join(data_dir, "config.json"),
        "overrides": os.path.join(data_dir, "overrides.json"),
        "sources": os.path.join(data_dir, "sources.json"),
        "cache": os.path.join(data_dir, "cache", "md_cache.json"),
        "health": data_dir,
        "out_dir": data_dir,
        "out_html": os.path.join(data_dir, "Manga_Leseliste.html"),
    }


def parse_args(argv):
    """argv -> (data_dir, lang, full, force). Reihenfolge der Flags egal (rein, testbar).
    --force = alle Titel komplett neu anreichern (impliziert vollen Lauf)."""
    argv = list(argv)
    force = "--force" in argv
    full = "--full" in argv or force
    argv = [a for a in argv if a not in ("--full", "--force")]
    lang = None
    if "--lang" in argv:
        i = argv.index("--lang")
        if i + 1 < len(argv):
            lang = argv[i + 1]
            del argv[i:i + 2]
        else:
            del argv[i]
    data_dir = argv[0] if argv else os.getcwd()
    return data_dir, lang, full, force


def copy_guides(out_dir):
    """📖-Anleitungen (DE+EN) neben die Liste legen (Links im HTML sind relativ) — best-effort."""
    try:
        import shutil
        for gf in ("Anleitung.html", "Guide.html"):
            src = os.path.normpath(os.path.join(PKG_DIR, "..", gf))
            dst = os.path.join(out_dir, gf)
            if os.path.exists(src) and os.path.abspath(src) != os.path.abspath(dst):
                shutil.copy(src, dst)
    except Exception:
        pass


def choose_lang(cli_lang, settings):
    """Sprachwahl: CLI > Settings-Override > OS-Locale > Englisch (rein, testbar)."""
    return i18n.detect_lang(override=cli_lang or settings.get("lang"))


def run(data_dir, lang=None, full=False, force=False):
    """Voller Standalone-Lauf: scannen, anreichern, rendern. Gibt (anzahl, html_pfad).
    force=True -> alle Titel komplett neu anreichern (kompletter Neuaufbau)."""
    paths = resolve_paths(data_dir)
    settings = config.load_settings(paths["settings"])
    lang = choose_lang(lang, settings)
    ov = paths["overrides"] if os.path.exists(paths["overrides"]) else BUNDLED_OVERRIDES
    name_fix = config.load_overrides(ov)
    src = paths["sources"] if os.path.exists(paths["sources"]) else BUNDLED_SOURCES
    config.apply_sources(config.load_sources(src))   # self-updatebarer Reader-Vorrat
    from . import readerlink                          # die 660 Direkt-Links (Hauptnutzen) laden
    so = os.path.join(data_dir, "series_overrides.json")
    readerlink.load_overrides(so if os.path.exists(so) else BUNDLED_SERIES)
    # Muster-Reader laden (fehlte: ohne diesen Aufruf liefen nur die 3 eingebauten Defaults)
    rp = os.path.join(data_dir, "readers_pattern.json")
    readerlink.load_readers(rp if os.path.exists(rp)
                            else os.path.normpath(os.path.join(PKG_DIR, "..", "data", "readers_pattern.json")))
    os.makedirs(os.path.dirname(paths["cache"]), exist_ok=True)
    copy_guides(paths["out_dir"])
    # Fortschritts-Dateien NEBEN die Liste (data/…) -> der Balken funktioniert relativ, auch file://
    progress_dir = os.path.join(paths["out_dir"], "data")
    os.makedirs(progress_dir, exist_ok=True)
    items = scan_all()
    cap = 10 ** 9 if (full or force) else 80
    rows = enrich(items, paths["cache"], paths["health"], cap, name_fix=name_fix, force=force,
                  progress_dir=progress_dir,
                  checkpoint_render=lambda r: render(r, paths["out_dir"], paths["out_html"], lang=lang))
    try:                                             # Quellen-Ampel frisch halten (best-effort)
        from . import readers as _readers
        _readers.refresh_status()
    except Exception:
        pass
    try:                                             # externe Empfehlungen erneuern (best-effort)
        from .enrich import recs_refresh as _recs_refresh
        _recs_refresh(rows)
    except Exception:
        pass
    n = render(rows, paths["out_dir"], paths["out_html"], lang=lang)
    try:                       # frischer Render-Stempel -> offene (leere/idle) Seiten laden neu
        from .enrich import _progress
        _progress("fertig", 1, 1, progress_dir, rendered=True)
    except Exception:
        pass
    return n, paths["out_html"]


def main(argv=None):
    data_dir, cli_lang, full, force = parse_args(sys.argv[1:] if argv is None else argv)
    n, out = run(data_dir, lang=cli_lang, full=full, force=force)
    print(f"SyncManga: {n} Serien -> {out}")


if __name__ == "__main__":
    main()
