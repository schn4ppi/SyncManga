# -*- coding: utf-8 -*-
"""
Mehrsprachige UI-Strings des Manga-Kerns.

Sprache = OS-Locale (Deutsch -> Deutsch, sonst Englisch), per Settings ueberschreibbar.
Alle nutzersichtbaren Texte (Liste, Fortschritt, Tray-Menue, Hilfe) liegen in EINEM Dict;
eine neue Sprache = ein neuer Block mit denselben Keys (Test erzwingt Key-Vollstaendigkeit).

Verwendung:
    from syncmanga import i18n
    s = i18n.strings(i18n.detect_lang())     # dict key->Text
    s["title"]                               # z.B. "Manga-Leseliste"
"""
import os

DEFAULT = "en"          # Fallback-Sprache, wenn OS-Locale nicht Deutsch ist

STRINGS = {
    "de": {
        # Kopf / Liste
        "title": "Manga-Leseliste",
        "series": "Serien",
        "dead_sources": "tote Quellen",
        "updated": "Stand",
        "unknown": "unbekannt",
        # Spalten
        "col_series": "Serie",
        "col_author": "Autor",
        "col_user": "User",
        "col_user_title": "Dein Lese-Fortschritt, automatisch abgeleitet",
        "st_tip_reading": "🟢 Lese gerade — kürzlich weitergelesen, noch Kapitel offen",
        "st_tip_paused": "🟡 Pausiert — länger nicht weitergelesen (bis ~3 Monate)",
        "st_tip_paused_long": "🟥 Länger als ~3 Monate pausiert — evtl. abgebrochen?",
        "st_tip_caught": "🔵 Aufgeholt — alles Verfügbare gelesen, wartet auf neue Kapitel",
        "st_tip_finished": "🩵 Fertig — abgeschlossene Serie komplett gelesen",
        "st_tip_backlog": "◻ Backlog — gemerkt, aber noch nicht begonnen",
        "col_status": "Status",
        "col_chapters": "Kap. gelesen/neu",
        "col_chapters_title": "neu = höchstes bekanntes Kapitel über alle Quellen; "
                              "wird nie unter deinem gelesenen angezeigt. "
                              "Quellen können hinterherhängen.",
        "col_last": "Zuletzt",
        "col_source": "Quelle",
        "col_rating": "Bewertung",
        "col_chapters_s": "gel./neu", "col_rating_s": "★",   # Mobile-Kurzformen (JB 09.07.2026)
        "pinbox_tip": "Archiv & Favoriten ein-/ausklappen",
        "col_action": "Aktion",
        # User-Fortschritt (Werte zugleich Filter)
        "prog_reading": "Lese gerade",
        "prog_caught": "Aufgeholt",
        "prog_finished": "Abgeschlossen",
        "prog_paused": "Pausiert",
        "prog_backlog": "Backlog",
        # Steuerung / Filter
        "filter_all": "Alle",
        "search_placeholder": "Serie/Autor suchen…",
        "country_all": "Alle Länder",
        "type_all": "Alle Typen",
        "genre_all": "Alle Genres",
        "prog_tips": {"prog_reading": "Du liest gerade — aktuell dran",
                      "prog_caught": "Alle Kapitel gelesen, wartet auf neue",
                      "prog_finished": "Serie fertig (abgeschlossen + durchgelesen)",
                      "prog_paused": "Länger nicht weitergelesen",
                      "prog_backlog": "Gemerkt, aber noch nicht angefangen"},
        "filter_all_tip": "Alle Serien anzeigen",
        "stats_toggle": "Lese-Statistik ein-/ausklappen",
        "recs_toggle": "Externe Empfehlungen (AniList) — basierend auf allen Serien deiner Liste",
        "genre_toggle": "Nach Genre filtern — mehrere gleichzeitig kombinierbar",
        "nsfw_title": "18+-Inhalte ein-/ausblenden", "nsfw_all": "🔞 Alle",
        "nsfw_hide_sexual": "🔞 nur Sexuelles aus", "nsfw_hide_gore": "🩸 nur Gore aus", "nsfw_hide_both": "🔞 NSFW off",
        "recs_title": "Empfehlungen",
        "recs_hint": "Weil deine Liste viel {g} enthält — diese Serien (extern, noch nicht in deiner Liste) könnten dir gefallen:",
        "recs_shuffle": "↻ neue Vorschläge",
        "recs_shuffle_title": "12 andere Vorschläge aus dem aktuellen Empfehlungs-Pool ziehen",
        "archive": "Archivieren",
        "archive_count": "Archiv",
        "help_button": "❓ Hilfe: {n}",
        "new_button": "{n}", "new_button_title": "Nur Serien mit ungelesenen Kapiteln",
        "help_button_title": "Nur Serien, die Hilfe brauchen: kein Treffer/Autor – "
                             "Titel prüfen oder korrigieren",
        "help_badge_title": "Braucht Hilfe: kein Treffer/Autor – Titel prüfen",
        "mismatch_badge_title": "Lesestand über der bekannten Kapitelzahl – wahrscheinlich falscher Match, bitte prüfen",
        "finished_badge_title": "Abgeschlossen – komplett gelesen",
        "report_broken_title": "Link kaputt? Melden — weiterlesen springt auf die Reserve. Nochmal klicken = alles rückgängig",
        "report_export_title": ("🛠 Wartung: gemeldete kaputte Links zur Reparatur übergeben — "
                                "läuft das Tray, direkt per Klick (der nächste Sync prüft die "
                                "Serien komplett neu); sonst als broken_links.json exportieren "
                                "und nach Manga/data legen"),
        "brk_sent": ("🛠 An die Reparatur übergeben — der nächste Sync prüft die gemeldeten "
                     "Serien komplett neu."),
        "dud_arch": "Link kaputt",
        "dud_back": "zurückholen",
        "dud_all": "alle zurückholen",
        "ampel_series": "Serien in deiner Liste",
        "confirm_title": "Match bestätigen: dieser Titel ist korrekt (✔ exportieren → wird fest gepinnt)",
        "confirm_export_title": "Bestätigte Titel exportieren (title_confirms.json) — Datei nach Manga/data legen, der Wochen-Lauf pinnt sie",
        "state_export_title": "Zustand sichern (Favoriten, Archiv, Einstellungen) → list_state.json. Nach Manga/data legen = automatische Wiederherstellung in jedem Browser",
        "welcome_empty": "👋 Willkommen! Noch keine Serien gefunden — lies ein paar Manga-Kapitel im Browser, beim nächsten Lauf füllt sich die Liste von selbst. Kein Grund zur Sorge: alles funktioniert.",
        "export_menu": "Im-/Export",
        "export_menu_title": "Leseliste exportieren (MAL-XML/JSON) oder eine fremde Liste importieren — Anleitung im Menü",
        "export_with_arch": "Archivierte mitnehmen",
        "export_fav_only": "nur Favoriten",
        "export_mal": "MAL-XML",
        "export_mal_title": "Standard-Format: bei MyAnimeList oder AniList importieren → MangaBaka kann deine Bibliothek von dort übernehmen",
        "export_json": "JSON",
        "export_done": "Serien exportiert",
        "export_skipped": "ohne MAL-ID übersprungen (füllt sich nach dem nächsten Voll-Lauf)",
        "import_mal": "⤵ Import",
        "import_mal_title": "MAL-XML einlesen (Export von MyAnimeList/AniList): bekannte Serien heben sofort den Lesestand an, unbekannte landen in einer Datei für den nächsten Lauf",
        "import_done": "Lesestände übernommen",
        "import_new": "unbekannte Serien → imported_series.json heruntergeladen (in Manga/data legen, der nächste Lauf ergänzt sie)",
        "theme_title": "Tag-/Nachtmodus umschalten (merkt sich deine Wahl)",
        "syncbar": "Aktualisiere Serien",
        "sync_paused": "Tray geschlossen — Update pausiert",
        "guide_title": "Anleitung öffnen — alle Funktionen & Einrichtung Schritt für Schritt",
        "tiles_title": "Kachel-Ansicht: Cover-Galerie mit Lesestand (Klick aufs Bild = weiterlesen)",
        "guide_file": "Anleitung.html",
        "xg_title": "❓ Kurzanleitung",
        "xg_up": '⤴ <b>Liste exportieren:</b> „MAL-XML" erzeugen und bei <a href="https://myanimelist.net/import.php" target=_blank rel=noopener>MyAnimeList</a> oder <a href="https://anilist.co/settings/import" target=_blank rel=noopener>AniList</a> hochladen — MangaBaka übernimmt sie von dort.',
        "xg_down": '⤵ <b>Liste importieren:</b> XML beim <a href="https://myanimelist.net/panel.php?go=export" target=_blank rel=noopener>MAL-Export</a> holen → hier „⤵ Import" klicken → Datei wählen. Bekannte Serien sofort übernommen, unbekannte ergänzt der nächste Lauf.',
        "xg_al": '🔄 <b>AniList-Auto-Sync:</b> kostenloses Konto auf <a href="https://anilist.co/signup" target=_blank rel=noopener>anilist.co/signup</a> anlegen (falls noch keins), dann einmalig <code>Core\\anilist_verbinden.bat</code> doppelklicken (Browser öffnet → Approve → Code ins schwarze Fenster) — danach schreibt jeder Lauf deinen Fortschritt von selbst zu AniList.',
        "xg_more": '📖 <b><a href="Anleitung.html" target=_blank>Ausführliche Anleitung öffnen</a></b> — alle Funktionen, Einrichtung Schritt für Schritt (AniList, Gmail, Web.de).',
        "xg_bug": '🐛 <b><a href="mailto:jan.bernd.kalvelage@gmail.com?subject=%5BSyncManga%5D%20Fehlerbericht&body=Was%20ist%20passiert%3F%0A%0AWelche%20Serie%2FSeite%3F%0A%0A(Gern%20die%20broken_links.json%20vom%20%E2%9A%A0-Knopf%20anh%C3%A4ngen.)">Fehler melden</a></b> — kurze Mail genügt; Berichte fließen direkt in die Fehlerbehebung.',
        "dynamic_hint": "Webtoon/dynamische Seite – Fortschritt ggf. ungenau",
        # Aktionen je Zeile
        "open": "▶ öffnen",
        "start_reading": "▶ anfangen",
        "finished_label": "🏁 beendet",
        "continue": "↪ weiterlesen",
        "search": "🔍 suchen",
        "alt_menu": "＋ Alt",
        "alt_search_tip": "Google-Suche über alle gelisteten Lese-Seiten",
        "source_dead": "Quelle tot",
        "source_unsafe": "Quelle unsicher",
        "source_stale_hint": "Link evtl. veraltet – „weiterlesen“ sucht eine aktuelle, lebende Quelle.",
        "source_auto_hint": "automatisch gefundener, geprüfter Reader (nicht deine gespeicherte Seite)",
        "to_top": "Nach oben",
        "chapfix_tip": "Klick: Lesestand manuell setzen (z.B. am Handy gelesen). Leer = zurücksetzen, Abbrechen = nichts ändern",
        "chapfix_prompt": "Gelesen bis Kapitel? (leer = zurücksetzen)",
        "lucky_title": "🎲 Überrasch mich: zufällige ungelesene Serie aus dem Backlog (Bewertung gewichtet)",
        "dense_title": "Kompakt-Modus: schmalere Zeilen für mehr Übersicht",
        "source_alt": "Alternative",
        "source_status_label": "Datenquellen",
        "reader_status_label": "Lese-Seiten",
        "src_open_hint": "im neuen Tab öffnen",
        "stats_title": "Statistik", "stats_chapters": "Kapitel gelesen",
        "legend_ok": "funktioniert", "legend_browser": "nur im Browser", "legend_maint": "in Wartung", "legend_down": "nicht erreichbar",
        "stats_tip_count": "Serien in deiner Liste",
        "stats_tip_status": "Lese gerade · 🏁 Abgeschlossen · ✅ Aufgeholt · ⏸ Pausiert · 📋 Backlog",
        "stats_tip_rating": "Durchschnittliche Bewertung (Median über mehrere Datenbanken)",
        "stats_tip_chapters": "Summe deiner gelesenen Kapitel",
        "stats_tip_country": "Verteilung nach Herkunftsland",
        "stats_tip_type": "Verteilung nach Typ (Manga/Manhwa/Manhua/…)",
        "stats_tip_adult": "Serien mit 18+-Inhalt",
        "stats_tip_top": "Deine höchstbewertete Serie",
        "stats_mono": "ohne Reserve",
        "stats_tip_cover": "Absicherung: Anteil der Serien, die beim Ausfall ihrer Lese-Seite eine Reserve auf einer ANDEREN Seite haben — der Reserve-Auffüller arbeitet die Lücken automatisch ab",
        "read_direct_hint": "Direkter, geprüfter Link zu deinem nächsten Kapitel auf einer freien Leseseite.",
        "rating_tip": "Median {rating} aus {n} Bayes-Quelle(n): {vals}",
        "archive_title": "archivieren",
        "unarchive_title": "wiederherstellen",
        "archview_title": "Archivierte Serien anzeigen und einzeln wiederherstellen",
        "archmode_title": "An: 🗃-Symbol erscheint neben jedem Titel zum Archivieren",
        "cols_menu": "＋ Spalten",
        "cols_menu_title": "Spalten ein-/ausblenden",
        "pause_menu": "⏸ Pausen",
        "pause_menu_title": ("Nicht automatisch prüfbare Lese-Seiten manuell pausieren "
                             "(Wartung/Umbau): die Aktionen zeigen dann Reserve-Links, "
                             "bis du die Pause aufhebst. Es geht nichts verloren."),
        "paused_tip": "⏸ pausiert (Wartung/Umbau) — Aktionen zeigen Reserve-Links",
        "pause_covers": "umfasst: {doms}",
        "new_chaps_tip": "{n} neue Kapitel seit deinem Lesestand",
        "recs_read_tip": "📖 Kapitel 1 direkt auf einem geprüften Reader öffnen",
        "alt_verified_tip": "Geprüfter Direktlink zum Kapitel",
        "alt_verified_en": "✓ EN-Kapitel per API bestätigt — verlässlichster Direktlink",
        "src_confirm": "Als richtige Quelle bestätigen (wird beim nächsten Sync fest übernommen)",
        "src_confirm_own": "✔ eigenen Link bestätigen …",
        "src_confirm_prompt": "Direktlink zum aktuellen Kapitel einfügen (wird als deine Quelle gespeichert):",
        "src_saved_badge": "✔ Quellen speichern",
        "src_saved_ok": "✔ Quelle(n) gemerkt — der nächste Sync übernimmt sie fest als deinen Direktlink.",
        "last_group_tip": "zuletzt von {g}",
        "pause_group": "📚 Einzel-Serien-Seiten ({n})",
        "pause_group_title": ("Seiten, die nur EINE Serie hosten — Haken pausiert alle auf "
                              "einmal, Aufklappen zeigt die Einzel-Schalter."),
        "fav_button": "Favoriten",
        "fav_mode": "Favorit",
        "fav_mode_title": "Favorit-Modus: ⭐ neben jedem Titel erscheint zum Anpinnen (wie Archivieren)",
        "fav_button_title": "Favoriten ein-/ausblenden (stehen oben, sortiert nach ungelesenen Kapiteln, dann Bewertung)",
        "fav_title": "Als Favorit oben anpinnen",
        # Tray-Menue
        "tray_update": "Aktualisieren",
        "tray_force": "Komplett neu laden (alle Titel)",
        "tray_open": "Liste öffnen",
        "tray_language": "Sprache",
        "tray_help": "Hilfe",
        "tray_quit": "Beenden",
        "tray_update_available": "Update verfügbar",
        # Selbst-Update der exe (Task #34)
        "tray_selfupdate": "Nach Update suchen…",
        "tray_autoupdate": "Automatisch aktualisieren",
        "upd_none": "SyncManga ist aktuell (v{v}).",
        "upd_available": "Update auf v{v} verfügbar — installieren: Menü → „Nach Update suchen…“.",
        "upd_installing": "Update auf v{v} wird installiert — SyncManga startet gleich neu.",
        "upd_failed": "Update fehlgeschlagen: {e} — alles bleibt beim Alten.",
        "tray_started": "SyncManga läuft im Tray – Linksklick aufs Symbol öffnet die Liste.",
        "tray_first_sync": "Die Liste wird gerade zum ersten Mal gebaut (ein paar Minuten) – sie öffnet sich danach von selbst.",
        "tray_last": "Zuletzt", "tray_syncing": "Synchronisiert gerade …",
        "tray_never": "Noch nicht synchronisiert",
        # Tooltip fuers Tray-Symbol (Mauszeiger drueber): erklaert die Symbolfarbe.
        "tray_tip_running": "läuft gerade …",
        "tray_tip_ok": "✓ alle Datenquellen ok",
        "tray_tip_dead": "⚠ {n} Datenquelle(n) offline",
        # Datenschutz-Hinweis (erster Start / Hilfe)
        "privacy": "100% lokal – es werden keine Daten hochgeladen.",
    },
    "en": {
        "title": "Manga Reading List",
        "series": "series",
        "dead_sources": "dead sources",
        "updated": "Updated",
        "unknown": "unknown",
        "col_series": "Series",
        "col_author": "Author",
        "col_user": "You",
        "col_user_title": "Your reading progress, derived automatically",
        "st_tip_reading": "🟢 Reading — recently continued, chapters still open",
        "st_tip_paused": "🟡 Paused — not continued for a while (up to ~3 months)",
        "st_tip_paused_long": "🟥 Paused longer than ~3 months — maybe dropped?",
        "st_tip_caught": "🔵 Caught up — read all available, waiting for new chapters",
        "st_tip_finished": "🩵 Finished — completed series fully read",
        "st_tip_backlog": "◻ Backlog — saved but not started yet",
        "col_status": "Status",
        "col_chapters": "Ch. read/new",
        "col_chapters_title": "new = highest chapter known across all sources; "
                              "never shown below the one you've read.",
        "col_last": "Last",
        "col_source": "Source",
        "col_rating": "Rating",
        "col_chapters_s": "rd./new", "col_rating_s": "★",   # mobile short forms
        "pinbox_tip": "expand/collapse archive & favorites",
        "col_action": "Action",
        "prog_reading": "Reading",
        "prog_caught": "Caught up",
        "prog_finished": "Finished",
        "prog_paused": "Paused",
        "prog_backlog": "Backlog",
        "filter_all": "All",
        "search_placeholder": "Search series/author…",
        "country_all": "All countries",
        "type_all": "All types",
        "genre_all": "All genres",
        "prog_tips": {"prog_reading": "Currently reading — actively on it",
                      "prog_caught": "All chapters read, waiting for new ones",
                      "prog_finished": "Series done (completed + fully read)",
                      "prog_paused": "Not continued in a while",
                      "prog_backlog": "Saved but not started yet"},
        "filter_all_tip": "Show all series",
        "stats_toggle": "Toggle reading statistics",
        "recs_toggle": "External recommendations (AniList) — based on all series in your list",
        "genre_toggle": "Filter by genre — combine several at once",
        "nsfw_title": "Show/hide 18+ content", "nsfw_all": "🔞 All",
        "nsfw_hide_sexual": "🔞 hide sexual only", "nsfw_hide_gore": "🩸 hide gore only", "nsfw_hide_both": "🔞 NSFW off",
        "recs_title": "Recommendations",
        "recs_hint": "Because your list is full of {g} — these series (external, not in your list yet) might be for you:",
        "recs_shuffle": "↻ shuffle",
        "recs_shuffle_title": "Draw 12 different suggestions from the current recommendation pool",
        "archive": "Archive",
        "archive_count": "Archived",
        "help_button": "❓ Help: {n}",
        "new_button": "{n}", "new_button_title": "Only series with unread chapters",
        "help_button_title": "Only series that need help: no match/author – "
                             "check or correct the title",
        "help_badge_title": "Needs help: no match/author – check the title",
        "mismatch_badge_title": "Read chapter above known total – likely a wrong match, please check",
        "finished_badge_title": "Finished – fully read",
        "report_broken_title": "Broken link? Report — continue-reading jumps to the reserve. Click again = undo all",
        "report_export_title": ("🛠 Maintenance: hand reported broken links to the repair — "
                                "with the tray running it's one click (next sync fully "
                                "re-resolves those series); otherwise export broken_links.json "
                                "and put it into Manga/data"),
        "brk_sent": ("🛠 Handed to repair — the next sync fully re-resolves the reported "
                     "series."),
        "dud_arch": "Broken link",
        "dud_back": "restore",
        "dud_all": "restore all",
        "ampel_series": "series in your list",
        "confirm_title": "Confirm match: this title is correct (export ✔ → gets pinned)",
        "confirm_export_title": "Export confirmed titles (title_confirms.json) — put the file into Manga/data, the weekly run pins them",
        "state_export_title": "Back up state (favorites, archive, settings) → list_state.json. Put it into Manga/data = automatic restore in any browser",
        "welcome_empty": "👋 Welcome! No series found yet — read a few manga chapters in your browser and the list fills itself on the next run. Nothing is wrong: everything is working.",
        "export_menu": "Import/Export",
        "export_menu_title": "Export your list (MAL XML/JSON) or import another list — guide inside the menu",
        "export_with_arch": "include archived",
        "export_fav_only": "favorites only",
        "export_mal": "MAL XML",
        "export_mal_title": "Standard format: import at MyAnimeList or AniList → MangaBaka can pull your library from there",
        "export_json": "JSON",
        "export_done": "series exported",
        "export_skipped": "skipped without MAL id (fills up after the next full run)",
        "import_mal": "⤵ Import",
        "import_mal_title": "Read a MAL XML (export from MyAnimeList/AniList): known series bump their progress instantly, unknown ones go into a file for the next run",
        "import_done": "progress entries applied",
        "import_new": "unknown series → imported_series.json downloaded (put it in Manga/data, the next run adds them)",
        "theme_title": "Toggle day/night mode (remembers your choice)",
        "syncbar": "Updating series",
        "sync_paused": "Tray closed — update paused",
        "guide_title": "Open the guide — every feature & setup step by step",
        "tiles_title": "Tile view: cover gallery with reading progress (click a cover to read on)",
        "guide_file": "Guide.html",
        "xg_title": "❓ Quick guide",
        "xg_up": '⤴ <b>Export your list:</b> create the "MAL XML" and upload it at <a href="https://myanimelist.net/import.php" target=_blank rel=noopener>MyAnimeList</a> or <a href="https://anilist.co/settings/import" target=_blank rel=noopener>AniList</a> — MangaBaka picks it up from there.',
        "xg_down": '⤵ <b>Import a list:</b> grab the XML from the <a href="https://myanimelist.net/panel.php?go=export" target=_blank rel=noopener>MAL export</a> → click "⤵ Import" here → choose the file. Known series apply instantly, unknown ones are added by the next run.',
        "xg_al": '🔄 <b>AniList auto-sync:</b> create a free account at <a href="https://anilist.co/signup" target=_blank rel=noopener>anilist.co/signup</a> (if you have none), then double-click <code>Core\\anilist_verbinden.bat</code> once (browser opens → Approve → paste the code) — after that every run pushes your progress to AniList automatically.',
        "xg_more": '📖 <b><a href="Guide.html" target=_blank>Open the full guide</a></b> — every feature, step-by-step setup (AniList, Gmail, Web.de).',
        "xg_bug": '🐛 <b><a href="mailto:jan.bernd.kalvelage@gmail.com?subject=%5BSyncManga%5D%20Bug%20report&body=What%20happened%3F%0A%0AWhich%20series%2Fsite%3F%0A%0A(Feel%20free%20to%20attach%20broken_links.json%20from%20the%20%E2%9A%A0%20button.)">Report a bug</a></b> — a short mail is enough; reports feed straight into fixes.',
        "dynamic_hint": "Webtoon/dynamic site – progress may be inaccurate",
        "open": "▶ open",
        "start_reading": "▶ start",
        "finished_label": "🏁 finished",
        "continue": "↪ read on",
        "search": "🔍 search",
        "alt_menu": "＋ Alt",
        "alt_search_tip": "Google search across all listed reader sites",
        "source_dead": "source down",
        "source_unsafe": "source unsafe",
        "source_stale_hint": "Link may be outdated – “read on” searches for a current, live source.",
        "source_auto_hint": "automatically found, verified reader (not your saved site)",
        "to_top": "Back to top",
        "chapfix_tip": "Click: set read progress manually (e.g. read on your phone). Empty = reset, cancel = no change",
        "chapfix_prompt": "Read up to chapter? (empty = reset)",
        "lucky_title": "🎲 Surprise me: random unread series from your backlog (rating-weighted)",
        "dense_title": "Compact mode: slimmer rows for a better overview",
        "source_alt": "Alternative",
        "source_status_label": "Data sources",
        "reader_status_label": "Reader sites",
        "src_open_hint": "open in a new tab",
        "stats_title": "Statistics", "stats_chapters": "chapters read",
        "legend_ok": "working", "legend_browser": "browser only", "legend_maint": "maintenance", "legend_down": "down",
        "stats_tip_count": "Series in your list",
        "stats_tip_status": "Reading · 🏁 Finished · ✅ Caught up · ⏸ Paused · 📋 Backlog",
        "stats_tip_rating": "Average rating (median across several databases)",
        "stats_tip_chapters": "Total chapters you've read",
        "stats_tip_country": "Distribution by country of origin",
        "stats_tip_type": "Distribution by type (manga/manhwa/manhua/…)",
        "stats_tip_adult": "Series with 18+ content",
        "stats_tip_top": "Your highest-rated series",
        "stats_mono": "without backup",
        "stats_tip_cover": "Coverage: share of series with a backup link on a DIFFERENT site if their reader goes down — the reserve filler works through the gaps automatically",
        "read_direct_hint": "Direct, verified link to your next chapter on a free reading site.",
        "rating_tip": "Median {rating} from {n} Bayes source(s): {vals}",
        "archive_title": "archive",
        "unarchive_title": "restore",
        "archview_title": "Show archived series and restore them individually",
        "archmode_title": "On: a 🗃 icon appears next to each title for archiving",
        "cols_menu": "＋ Columns",
        "cols_menu_title": "Show/hide columns",
        "pause_menu": "⏸ Paused",
        "pause_menu_title": ("Manually pause reader sites that can't be checked automatically "
                             "(maintenance/rebuild): actions switch to backup links until "
                             "you unpause. Nothing is lost."),
        "paused_tip": "⏸ paused (maintenance) — actions show backup links",
        "pause_covers": "covers: {doms}",
        "new_chaps_tip": "{n} new chapters since your progress",
        "recs_read_tip": "📖 open chapter 1 on a verified reader",
        "alt_verified_tip": "Verified direct chapter link",
        "alt_verified_en": "✓ EN chapter confirmed via API — most reliable direct link",
        "src_confirm": "Confirm as the correct source (pinned on the next sync)",
        "src_confirm_own": "✔ confirm your own link …",
        "src_confirm_prompt": "Paste the direct link to the current chapter (saved as your source):",
        "src_saved_badge": "✔ Save sources",
        "src_saved_ok": "✔ Source(s) noted — the next sync pins them as your direct link.",
        "last_group_tip": "latest by {g}",
        "pause_group": "📚 Single-series sites ({n})",
        "pause_group_title": ("Sites hosting only ONE series — the checkbox pauses them all "
                              "at once, expand for individual switches."),
        "fav_button": "Favorites",
        "fav_mode": "Favorite",
        "fav_mode_title": "Favorite mode: a ⭐ appears next to each title for pinning (like archiving)",
        "fav_button_title": "Show/hide favorites (pinned on top, sorted by unread chapters, then rating)",
        "fav_title": "Pin as favorite (top)",
        "tray_update": "Update now",
        "tray_force": "Reload everything (all titles)",
        "tray_open": "Open list",
        "tray_language": "Language",
        "tray_help": "Help",
        "tray_quit": "Quit",
        "tray_update_available": "Update available",
        # exe self-update (task #34)
        "tray_selfupdate": "Check for updates…",
        "tray_autoupdate": "Update automatically",
        "upd_none": "SyncManga is up to date (v{v}).",
        "upd_available": "Update v{v} available — install: menu → “Check for updates…”.",
        "upd_installing": "Installing update v{v} — SyncManga will restart in a moment.",
        "upd_failed": "Update failed: {e} — nothing was changed.",
        "tray_started": "SyncManga is running in the tray – left-click the icon to open the list.",
        "tray_first_sync": "Your list is being built for the first time (a few minutes) – it will open by itself when ready.",
        "tray_last": "Last sync", "tray_syncing": "Syncing right now …",
        "tray_never": "Not synced yet",
        # Tooltip for the tray icon (hover): explains the icon colour.
        "tray_tip_running": "syncing …",
        "tray_tip_ok": "✓ all data sources ok",
        "tray_tip_dead": "⚠ {n} data source(s) offline",
        "privacy": "100% local – nothing is uploaded.",
    },
}


def available():
    """Verfuegbare Sprachcodes."""
    return tuple(STRINGS)


def _os_locale():
    """OS-Locale best-effort, OHNE die in 3.12+ deprecate getdefaultlocale()."""
    try:
        import locale
        loc = locale.getlocale()[0]
        if loc:
            return loc
    except Exception:
        pass
    try:                               # Windows: UI-Sprache ueber LCID -> z.B. "de_DE"
        import ctypes
        import locale as _l
        lcid = ctypes.windll.kernel32.GetUserDefaultUILanguage()
        return _l.windows_locale.get(lcid, "")
    except Exception:
        return ""


def detect_lang(override=None, loc=None):
    """UI-Sprache bestimmen: Override (Settings) > OS-Locale (de* -> Deutsch) > Englisch.

    `loc` erlaubt das Einspeisen eines Locale-Strings (Tests); sonst best-effort aus
    der Umgebung/dem OS. Unbekannte Overrides werden ignoriert (fallen auf die Erkennung)."""
    if override in STRINGS:
        return override
    if loc is None:
        loc = os.environ.get("LC_ALL") or os.environ.get("LANG") or _os_locale()
    return "de" if (loc or "").lower().startswith("de") else DEFAULT


def strings(lang):
    """String-Dict fuer `lang`; fehlende Keys fallen auf die Default-Sprache zurueck."""
    return {**STRINGS.get(DEFAULT, {}), **STRINGS.get(lang, {})}
