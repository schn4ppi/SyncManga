# Wöchentliche Pflege — was rostet, und wie man es merkt

> Begleitmaterial zu `VISION_SYNCFINDUS.md`.
> **JB-Vorgabe 08.08.2026:** *„Wir müssen ab und an immer wieder prüfen, was es Neues gibt, was
> Altes ersetzt und was gestorben ist. Das gehört zur wöchentlichen Roadmap, egal in welchem
> Chat ich bin."*
>
> **Darum steht es hier und nicht in einem Gespräch.** Ein Chat endet, diese Datei nicht.
> Wer immer als Nächstes an SyncFindus arbeitet — Mensch oder KI — führt diese Liste aus und
> trägt das Ergebnis unten ein.

---

## Warum ausgerechnet das

Alles am Pflichtenheft altert langsam. **Die Außenwelt nicht.** Die Halbwertszeit ist brutal
verschieden:

| Was | Hält | Beleg |
|---|---|---|
| Entscheidungen über das Werk-Modell | Jahre | Open Library modelliert *Work → Edition* seit zwanzig Jahren |
| Gestaltungsregeln | Jahre | WCAG-Zielgrößen ändern sich pro Jahrzehnt |
| **Werkzeuge** | Monate | Readarr wurde Mitte 2025 eingestellt — **an den Metadaten**, nicht am Code |
| **Quellen** | **Wochen** | Sony nahm mit *einer* Meldung über 200 Aniyomi-Erweiterungen offline |

> 🔑 **Ein Fund gehört in eine Datei, nie in einen Chat.** Jede Zeile, die diese Prüfung
> ergibt, wandert in den Änderungsverlauf (§15) oder in den betroffenen Abschnitt des
> Pflichtenhefts. Was nur im Gespräch stand, ist beim nächsten Mal weg.

---

## Der wöchentliche Lauf — neun Prüfungen

Reihenfolge nach Schadenshöhe. Jede Prüfung hat einen **Fund-Auslöser**: nur wenn der eintritt,
gibt es Arbeit.

### 1 · Die vier Protokolle leben *(§7.5)*

| Protokoll | Nachsehen | Fund, wenn |
|---|---|---|
| **Cardigann-YAML** | letzter Commit in `Prowlarr/Indexers` | älter als 14 Tage → die tägliche Abgleich-Aktion hängt |
| **`index.min.json`** | Zeitstempel der Erweiterungsliste | älter als 7 Tage → Betreiber weg oder Repo entführt |
| **yt-dlp** | letzte Veröffentlichung, offene Fehler „extractor broken" | Veröffentlichung > 6 Wochen alt → Projekt in Not |
| **MediathekView-Filmliste** | Zeitstempel + Größe | Größe springt > 20 % → ein Sender ist raus |

⚠️ **Prüfsumme mitprüfen, nicht nur Erreichbarkeit** — eine entführte Liste antwortet
freundlich (E12).

### 2 · Wissensketten *(§7.4, `quellen.html`)*

Für jede der fünf Ketten (Manga · Bewegtbild · Musik · Buch · Spiele): **ist das erste Glied
erreichbar, und antwortet es noch in derselben Form?**

**Fund, wenn:** ein Glied fällt aus · ein Feld verschwindet aus der Antwort · eine
Anmeldepflicht kommt dazu · ein Limit wird enger.
**Reaktion:** Kette umsortieren, nicht flicken. Fällt ein Primär aus, wird der Zweite Primär —
und der Ausfall steht in `srcstatus`.

### 3 · Werkzeuge *(§7.6)*

yt-dlp · streamlink · gallery-dl · Prowlarr · qBittorrent · Bazarr · beets · Picard · spotDL ·
MakeMKV · ffmpeg · Calibre · Kavita/Komga · MediathekView · Nicotine+

**Fund, wenn:** letzte Veröffentlichung > 6 Monate · Archiviert-Hinweis · Betreuer sucht
Nachfolger · Lizenzwechsel · ein Nachfolger hat mehr Sterne als das Original.

### 4 · Der Friedhof

Wer ist **gestorben**? Das ist die Prüfung, die man am liebsten vergisst, weil nichts
kaputtgeht — es fehlt nur etwas.

- **Reader-Ampel** aus SyncManga: welche Hosts liefern seit ≥ 3 Wochen 404 oder Weiterleitung?
- **Verzeichnis-Friedhöfe** (EverythingMoe *Graveyard*, FMHY-Änderungen): was ist neu
  eingetragen?
- ***arr*-Familie**: Readarr ist tot (2025). Wer ist dazugekommen, wer wackelt?

**Reaktion:** tote Quelle → abwerten, nicht löschen. Ein toter Reader ist Wissen (E122).

### 5 · Recht und Schlösser

**Fund, wenn:** neues Urteil zu § 95a / Privatkopie · Widevine-Stufen ändern sich · ein Anbieter
gibt DRM auf (kommt vor!) · eine Bibliotheksleihe wird offen.

**Reaktion:** §7.4 und §7.6 anpassen — inklusive der ehrlichen Fußnoten. **Nie beschönigen.**

### 6 · Neue Konkurrenz, neue Vorbilder

Was hat jemand gebaut, das wir **übernehmen** könnten? Suchbegriffe, die sich bewährt haben:
`self-hosted media library`, `manga reader server`, `metadata agent`, `*arr alternative`,
`local-first library`.

**Fund, wenn:** jemand hat ein Problem gelöst, das bei uns noch offen ist. → In §7.6 als
*Vorbild* eintragen, mit einem Satz, **was** genau übernommen wird.

### 7 · Browser *(§8.4, §8.5)*

**Fund, wenn:** Firefox ändert `places.sqlite` · Chrome baut weiter an MV3 ab · eine
Erweiterungsschnittstelle fällt weg · ein Browser sperrt `localhost`-Verbindungen.

Das ist die Prüfung mit der **längsten Vorwarnzeit** und dem **größten Schaden** — Ankündigungen
kommen Monate vorher, und wer sie verpasst, steht plötzlich ohne Zustandsquelle da.

### 8 · Die eigene Baustelle

- **Zertifikat** (§12.1): Bestellstand, Token-Wahl, Ablaufdatum.
- **Offene Fragen** (§13): ist eine durch die Außenwelt beantwortet worden?
- **Lücken** (§13.1): kann eine jetzt geschlossen werden?

### 9 · Die drei Suchen im eigenen Dokument

⚠️ **Am 08.08.2026 hinzugefügt, nachdem sie drei Lücken auf einmal fanden.**
Das **Warum** steht als **L4** in `LEHRBUCH.md`; hier steht nur, **wie** man es ausführt.

| Suche | Was sie findet | Fundbeispiel |
|---|---|---|
| **Oft genannt, nie erklärt** | Zähle die Nennungen jedes Eigennamens im Dokument. Steht einer ≥ 5-mal da, ohne je einen eigenen Abschnitt zu haben, ist er ein **leerer Raum, auf den Entscheidungen zeigen** | **„Werkstatt"** — 9 Nennungen als Zielort für vier tragende Entscheidungen, nie definiert |
| **Kommt gar nicht vor** | Suche nach Wörtern, die in *jedem* Programm vorkommen müssen: *kein Treffer · leer · antwortet nicht · abgebrochen · Zeitüberschreitung* | **Leere und kaputte Zustände** — nahezu null Treffer |
| **Handlung ohne Weg** | Spiele eine gewöhnliche Handlung durch und suche den Entwurf dazu. Findest du keinen, fehlt er | **Werke von Hand teilen** — bei 800 Werken sicher nötig, nirgends beschrieben |

**Auslöser:** monatlich, oder immer wenn zehn neue Entscheidungen dazugekommen sind.

---

## Wie ein Fund eingetragen wird

1. **Betroffenen Abschnitt** im Pflichtenheft ändern — nicht anhängen, **ändern** (§0).
2. **Eine Zeile im Änderungsverlauf** (§15) mit Datum und dem, was sich real geändert hat.
3. Wird daraus eine Regel: **neue E-Nummer**, fortlaufend, ohne Lücke.
4. Ist ein Entwurf betroffen: neu prüfen (`node --check`, E71) und neu veröffentlichen.

⚠️ **Kein Fund ist auch ein Ergebnis.** Eine Woche ohne Änderung wird eingetragen, sonst weiß
niemand, ob geprüft oder vergessen wurde.

---

## Protokoll

| Datum | Wer | Geprüft | Funde |
|---|---|---|---|
| 2026-08-08 | Claude | 1–8, Erstaufnahme | Cardigann 500+ aktiv · yt-dlp ~1.800 Extraktoren · Keiyoushi als Nachfolge-Erweiterungsladen · MediathekView stabil seit 2011 · **Readarr tot (2025)**, Nachfolger jung (Chaptarr, LazyLibrarian, rreading-glasses) · Jahrgang 1930 seit 01.01.2026 gemeinfrei (US) |
