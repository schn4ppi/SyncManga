# Übernahme aus SyncYouTube — was wörtlich portiert wird

> **Zweck:** SyncFundus wird von einer zweiten KI gebaut, die Zugriff auf **alle**
> Sync-Programme hat. Dieses Dokument sagt ihr, **was sie nicht neu erfinden darf** —
> mit Datei, Funktion und der Regel dahinter.
>
> **Stand:** 2026-08-07 · **Quelle:** `schn4ppi/SyncYouTube`, `System/oberflaeche.py` (9944 Z.),
> `System/youtube_app.py` (6186 Z.)

## Grundregel

> **Wo SyncYouTube etwas schon gelöst hat, wird der Code portiert — nicht nachgebaut.**
> Nachbauen heißt: dieselben Fehler zweimal machen. Jede der Lösungen unten ist aus einem
> konkreten JB-Einwand entstanden und trägt den im Kommentar.

Beim Portieren gilt: **die Kommentare kommen mit.** Sie erklären, *warum* etwas so ist —
das ist der eigentliche Wert, nicht der Code.

---

## 1 · Das Untertitel-Panel — wörtlich

**Quelle:** `oberflaeche.py`, `subMenu()` (ab Z. 6496), `SUB_STANDARD`, `SUB_SCHRIFTEN`,
`subStilAnwenden()`, `subStilSetzen()`, `subStilReset()`, `subStilVomServer()`.

**Zeilen des Panels, in dieser Reihenfolge:**

| Zeile | Werte |
|---|---|
| **Vorschau** | Live, oben, **feste Höhe** — der Text skaliert darin |
| Modus | `aus` · `Untertitel` · `Karaoke` |
| Sprache | dedupliziert (`xx-orig` verdeckt `xx`), nur wenn > 1 |
| Größe | `0.8` klein · `1` mittel · `1.35` groß · `1.8` riesig (TV) — als gestaffelte **Aa** |
| Schrift | `standard` `serif` `mono` `casual` `kursiv` `breit` — **Aa jeweils in der echten Schrift** |
| Farbe | 8 Punkte: `#ffffff #111111 #3b6df0 #38d1c8 #59c93c #ffe94a #e04343 #c94fc9` |
| Deckkraft | **ein Zyklusknopf** 100 % → 75 % → 50 % · daneben `Schatten` |
| Hintergrund | Punkt schwarz · Punkt weiß · Zyklus 70 % → 100 % → aus → 25 % → 50 % |
| Versatz | `‹` Wert `›` + Schrittweiten-Knopf `0,1 → 0,5 → 1 → 5 s` |
| Zurücksetzen | dezent unten |

**Regeln, die mitkommen müssen:**

| Regel | Herkunft |
|---|---|
| Vorschau hat **feste Höhe** | JB 05.08.: *„das Fenster wird größer und kleiner"* |
| Bei **Karaoke verschwinden** Farbe/Deckkraft/Hintergrund | JB 05.08.: die Farben gehören dem Wischer. Größe/Schrift/Versatz wirken weiter |
| Deckkraft als **ein** Zyklusknopf statt Knopfreihe | JB: *„zu viel Text in der Zeile"* |
| **Pfeiltasten bewegen den Fokus**, Enter wählt, Esc schließt | fernbedienungstauglich |
| **Fokus überlebt das Neu-Malen** (Index merken, nach dem Neuaufbau wiederherstellen) | sonst springt die Fernbedienung |
| Eigene `pointerdown` verlassen das Panel nie (`stopPropagation`) | JB: *„kann eh nichts anklicken"* — fremde Schließer |
| Gemerkt **je Browser** (`localStorage`) **und** server-global | versionsfest |
| **Versatz je Titel** gemerkt | |
| Alte 4 Presets werden beim Laden in Look-Felder übersetzt (`subPresetZuLook`) | Migration |

**Ergänzungen für SyncFundus** (neu, nicht in SyncYouTube): Zeile **Ort** (unten/oben — wenn
unten Schilder im Bild stehen) und **Rand** (harte Kontur für helle Bilder).

---

## 2 · Ausschnitte — Gruppierung und Favorit

**Quelle:** `youtube_app.py`, `_ist_clip()`, `_clip_gruppe()`, `_favorit_je_gruppe()` (Z. 1034),
`_clip_favorit_setzen()`, `_clip_favorit_zuruecksetzen()`, `clip_erstellen()` (Z. 1083),
`_clip_basisname()`.

**Das Modell:** ein Ausschnitt trägt `|clip` im Schlüssel und **teilt die Video-Id mit seinem
Song**. Damit gehört er zur Gruppe, ohne eine eigene Sammlung zu sein.

**Die Favoritenregel** (`_favorit_je_gruppe`), wörtlich zu übernehmen:

1. Gibt es eine **eigene Wahl** (`favorit`-Flag) → die gewinnt (bei mehreren: die neuste).
2. Sonst gewinnt der **Hauptsong** (Nicht-Clip).
3. Gibt es gar keinen Hauptsong (reine Clip-Gruppe) → der **neuste**.
4. Nach einem **neuen** Ausschnitt werden die Wahlen der Gruppe gelöscht, damit der neue Favorit
   wird (`_clip_favorit_zuruecksetzen`).

> Der Favorit ist der **Repräsentant**: er wird angezeigt, abgespielt und zählt im Zufall.
> Reine Auslese, kein Seiteneffekt.

**Für SyncFundus (E89):** ein Ausschnitt ist eine **Ausgabe** des Werks, nie ein neues Werk.
Die Gruppe oben entspricht bei uns dem Werk, das `favorit`-Flag der **bevorzugten Ausgabe**.
`clip_erstellen` bleibt **nicht-destruktiv** — das Original wird nie angefasst.

---

## 3 · Weiteres, das portiert wird

| Was | Quelle | Wird bei uns |
|---|---|---|
| **Spulen 2× → 32×** | Spieler-Tasten, `⏪/⏩` | E80: gehalten statt mehrfach gedrückt, Staffelung bleibt |
| **Mini-Player** | `miniToggle()`, `miniLayoutBauen()`, Klasse `body.mini` | E92/E98: die **Klangleiste** — aber viel kleiner, siehe §5.11.2 |
| **Karaoke** | `karWorte()`, `karLauf()`, `_romaji()`, `_lrc_cues()`, `_lrclib_get()` | E90: dieselbe Technik wie *Mitlesen*; **ein** Name, **eine** Umsetzung |
| **Transkript-Suche** | `transkript_suche()`, `_vtt_cues()` | E93: gehört in die **Suche**, erweitert auf Buchtext |
| **Autotag** | `_mb_suche()`, `_itunes_suche()`, `_cover_holen()`, `_cover_in_datei()`, `autotag_lauf()` | §10: MusicBrainz + iTunes, unverändert |
| **Umbenennung mit Probelauf** | Migration mit *„zeigt alt → neu, es wird NICHTS umbenannt"* + Rückgängig | E43: Titel als Rollen; Probelauf und Rücknahme sind **Pflicht**, kein Extra |
| **Fingerabdruck** | `_datei_fp()`, `_fp_von()`, `_id_tag_schreiben/lesen()` | E20: Fingerabdruck vor Dateiname |
| **Geo-Stufen** | `geo.py` (324 Z.) | §9: Header-Trick → eigene Proxys → Gratis-Proxys → VPN, in dieser Reihenfolge |
| **VPN** | `vpn.py` (107 Z.) | §9.5: **Einbahn-Regel** — kein anderes Modul spricht mit dem VPN |
| **Profile & Geräte** | `profil_geraete.py`, `handy.py`, `familie.py` | §12: Pairing, Fernsteuerung |
| **Warteschlange** | `class Warteschlange` (Z. 227) | §4.5 — aber um die drei Fehlerarten erweitert |
| **Link deuten** | `link_deuten()`, `ist_einzelvideo()`, `_ist_mix()` | §8: „erkennt selbst, was der Link ist" |
| **Playlists** | `playlist_aktion()`, `playlist_sync()`, `playlist_m3u()`, `playlist_import_m3u()` | §4.3: Playlist = **Sammlung**, m3u bleibt Export-Format (E06) |
| **SponsorBlock** | `sponsorblock_kategorien()` | §5.12: dieselbe Kategorienlogik für Vorspann-Sprung |

## 4 · Was **nicht** übernommen wird — mit Begründung

| Was | Warum nicht |
|---|---|
| **Ausgabegerät Browser ↔ VLC** (`_vlc_spieler`, `vlc_kommando`) | War eine Notlösung, weil der Browser nicht alles abspielt. Bei uns steckt **libmpv im eigenen Fenster** (E34) — die ganze Zwei-Geräte-Logik entfällt |
| **Layout-Editor mit andockbaren Panels** (`layout_kern.js`, `renderPanels`) | Richtig für einen Downloader (mehrere Listen im Blick), falsch für einen Ort zum Lesen. **E101**: eine Fläche |
| **Playlist als herauslösbares Fenster** (`plqFenster`) | Folgt aus E101 |
| **Browser-Player-Tasten in HTML5** | libmpv liefert die Wiedergabe, wir liefern nur die Bedienung (E35) |

## 5 · Was die zweite KI zuerst lesen soll

1. `Doku/VISION_SYNCFUNDUS.md` — vollständig, vor der ersten Zeile Code.
2. **Dieses Dokument** — damit nichts doppelt gebaut wird.
3. `SyncYouTube/System/_ARCHITEKTUR.md` und `MODULE.md` — die dortige Modulaufteilung.
4. `SyncYouTube/System/oberflaeche.py` — der Kopfkommentar allein erspart einen Tag Fehlersuche.

> **Und die wichtigste Regel beim Portieren:** wo im Quellcode ein Kommentar mit *„JB"* und
> einem Datum steht, steckt dahinter ein echter Fehler aus dem Betrieb. **Diese Kommentare
> werden mitgenommen, nicht wegoptimiert.**
