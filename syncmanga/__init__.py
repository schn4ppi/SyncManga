# -*- coding: utf-8 -*-
"""
syncmanga — gemeinsamer Manga-Kern.

Aus diesem Paket entstehen ZWEI Builds (gleicher Code, keine Forks):
  - extern: Standalone-App „SyncManga" (nur Manga, weitergebbar)
  - privat: JBs Vollsuite (Mail + Belege + Manga), die diesen Kern mitnutzt

Der Kern importiert NIEMALS Mail-/Beleg-Code und enthält keine privaten Daten/Secrets.

Phase 2 (Herauslösen aus SyncEngine/manga_update.py) — Stand:
  - parse.py  : reine Parser-/Normalisierungs-Funktionen (extrahiert, verbatim).
  Weitere Module (scan/sources/enrich/render/i18n/tray/update/common) folgen je Phase.
"""

# Quelle der Wahrheit zur LAUFZEIT (auch in der gepackten exe; Basis des Selbst-Updates).
# Ein Test erzwingt Gleichschritt mit Core/VERSION und Manga/build/version_info.txt.
__version__ = "0.4.2"

# stdout/stderr sofort beim Import des Kerns auf UTF-8 stellen. So ist JEDER Einstieg
# geschuetzt (Suite SyncEngine/manga_update.py, Standalone-.exe der Freunde, Tray, Tests),
# ohne dass jede Datei es einzeln tun muss — ein Emoji im print() darf nie den Lauf killen.
from .common import use_utf8_stdio as _use_utf8_stdio  # noqa: E402

_use_utf8_stdio()
