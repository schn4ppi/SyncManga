# SyncRegal — Vision & Fundament

> **Arbeitstitel.** Der Nachfolger von SyncManga und SyncYouTube: **ein** Programm für
> Anime, Manga, Novels, Musik, Hörbücher, Filme und Serien — mit eigener Bibliothek,
> eigenem Leser, eigenem Spieler, eigener Veredelung.
>
> **Stand:** 2026-08-06 · **Fassung:** 0.2 · **Pflege:** JB + Claude

---

## 0. Wie dieses Dokument zu benutzen ist

Dies ist **kein Protokoll**, sondern der Bauplan. Es wächst nicht durch Anhängen, sondern
durch **Überarbeiten**. Wer etwas hinzufügt, räumt gleichzeitig auf.

**Pflegeregeln (JB, 06.08.2026):**

1. **Jede Idee wird recherchiert, bevor sie hier steht.** Behauptung ohne Beleg ist eine
   offene Frage, keine Entscheidung.
2. **Jede Entscheidung trägt ihre Begründung.** Ohne Begründung kann man sie später nicht
   guten Gewissens umwerfen — und genau das muss möglich bleiben.
3. **Jede Entscheidung ist korrigierbar.** Wird eine umgeworfen, wandert sie mit Datum und
   Grund in §15, statt spurlos zu verschwinden.
4. **Widersprüche werden aufgelöst, nicht danebengestellt.** Zwei Absätze, die sich
   widersprechen, sind ein Fehler im Dokument.
5. **Ziel ist minimale Frustration beim Bauen.** Was hier ungeklärt bleibt, wird später
   dreimal umgebaut.

**Statuszeichen:**

| | Bedeutung |
|---|---|
| ✅ | entschieden, begründet, recherchiert |
| 🟡 | Richtung klar, Feinheiten offen |
| ❓ | offene Frage — in §13 gelistet |
| ⚠️ | bekanntes Risiko |
| 🔑 | tragende Entscheidung — Umwurf zieht viel nach sich |

---

## 1. Was SyncRegal ist

Ein **lokales, privates Medienregal** für alles, was man liest, sieht und hört.
Es baut seine Bibliothek **aus dem eigenen Verhalten** (Browserverlauf, Erweiterung,
Konten), reichert sie aus offenen Datenbanken an, beschafft Inhalte auf Wunsch,
**veredelt** sie (übersetzen, vertonen, kolorieren) und spielt sie auf PC, Handy und
Fernseher aus — offline-fähig.

Es ersetzt **SyncManga** und **SyncYouTube** und übernimmt deren Bestand.

---

## 2. Warum überhaupt — die Lücke im Markt

Recherchiert am 06.08.2026.

| Vorhandenes | kann | kann nicht |
|---|---|---|
| Suwayomi | Manga-Server, Mihon-Extensions, CBZ, OPDS | keine Novels, kein Anime, keine Erkennung |
| Seanime | Anime **und** Manga, HLS/Transcoding, AniList | keine Novels, braucht lokale Dateien |
| Kavita | Manga **und** Light Novels, echter Textleser | kein Anime, kein Spieler |
| Komga | Comics, top API, OPDS v2, Kobo | keine Novels, kein Anime |
| Mihon / Aniyomi / LNReader | je eine App pro Medium | drei Apps, drei Bibliotheken |
| *arr-Familie | Beschaffung automatisieren | keine Bibliothek, keine Erkennung, **Readarr tot** |

**Drei Alleinstellungsmerkmale:**

1. 🔑 **Die Bibliothek entsteht aus dem eigenen Verhalten.** Alle anderen verlangen
   manuelles Eintragen oder vorhandene Dateien. Das gibt es kein zweites Mal.
2. 🔑 **Alle Medien unter einer Oberfläche, mit eigenem Leser *und* Spieler.**
   Kavita kommt bei Manga+Novel am nächsten, Seanime bei Anime+Manga — die Kombination
   existiert nicht.
3. 🔑 **Übersetzungs- und Verfügbarkeitsstand prominent.** „Wird das noch übersetzt?"
   beantwortet niemand sonst auf einen Blick. Bei Novels ist die Frage sogar dringender.

**Und die offene Flanke:** seit Readarrs Einstellung (Mitte 2025, gescheitert an den
**Metadaten**, nicht an den Downloads) gibt es **kein funktionierendes *arr für Bücher,
Novels oder Manga**. Genau dort ist SyncMangas Stärke.

---

## 3. Entscheidungen

| # | Thema | Entscheidung | St. |
|---|---|---|---|
| E01 | Form | **Ein Programm**, nicht föderierte Module | ✅ |
| E02 | Abschaltbarkeit | Kern + **Fähigkeiten**; abschalten = registriert sich nicht | ✅ |
| E03 | Datenmodell | **Werk / Ausgabe / Beziehung**; Trennregel §4.2 | 🔑✅ |
| E04 | Sortierung | Vierstufige **Leiter** Sammlung→Gruppe→Einheit→Position | 🔑✅ |
| E05 | Rückgrat | **Eine Warteschlange**, viele Auftragsarten | 🔑✅ |
| E06 | Formate | **Standardformate** (CBZ/EPUB/MKV/M4B/FLAC), nie eigene | ✅ |
| E07 | Startseite | **Fortsetzung statt Auswahl**, nach Absicht sortiert | ✅ |
| E08 | Anordnung | **Selbstordnend + festnagelbar**, kein Einrichtungsdialog | ✅ |
| E09 | Farben | Tinte (Nacht) · Papier (Tag) · Spieler **immer** schwarz | ✅ |
| E10 | Anpassung Geräte | **Eine Prioritätsleiter**, keine Geräte-Entwürfe | 🔑✅ |
| E11 | Quellen-Kopplung | **Adapter-Schicht**, kein Fremdmodell im Kern | 🔑✅ |
| E12 | Quellenkatalog | **Laufzeitdatei**, nie im Repo (DMCA) | 🔑✅ |
| E13 | *arr | Integrieren, nicht nachbauen; Bücher selbst besitzen | ✅ |
| E14 | Vertonung | Ein-Sprecher-Modell **zeilenweise**, nicht Mehr-Sprecher-Modell | ✅ |
| E15 | Werk-Wissen | **Ein Artefakt** für Übersetzung + Stimmen + Kolorierung | 🔑✅ |
| E16 | Zugangsdaten | **Niemals speichern.** Nur Browser-Sitzungen mitbenutzen | 🔑✅ |
| E17 | Torrent | **Schnittstellen-Bindung** Pflicht, Abschalten nur ausdrücklich | ✅ |
| E18 | Erneuerung | Dreistufig: *falsch* sofort · *besser* langsam · *anders* nie | ✅ |
| E19 | Empfehlungen | Immer mit Grund; Profil lesbar und **von Hand korrigierbar** | ✅ |
| E20 | Identifikation | **Fingerabdruck vor Dateiname**; Fragen ins Postfach | 🔑✅ |
| E21 | MangaDex | Nur Metadaten, **nie** primäre Lesequelle (§7.1) | ✅ |
| E22 | Oberflächentechnik | Lokaler Server + Web-Oberfläche, **Video extern** (VLC/mpv) | 🟡 |
| E23 | Signatur | OV-Zertifikat + **Zeitstempel**; Reputation hängt am Zertifikat | ✅ |
| E24 | Medien-Umfang | Drei Schichten (§6); Grenze = Einheiten + Identität | ✅ |
| E25 | Spieler-Motor | **libmpv** Standard, **libVLC** zweite Umsetzung hinter derselben Schnittstelle | ✅ |
| E26 | Plattform-Offenheit | **Alle Logik hinter einer HTTP-Schnittstelle** — jede Hülle bleibt möglich | 🔑✅ |
| E27 | Ordnerstruktur | Etablierte Konventionen **übernehmen**, nie erfinden (§4.6) | ✅ |
| E28 | Pfade | **Wurzel-Kennung + relativer Pfad**, nie absolute Pfade als Identität | 🔑✅ |
| E29 | Umbenennen | Nur in eingeladenen Ordnern · immer Probelauf · immer rückgängig | ✅ |
| E30 | Mängel | **Deklarieren, nicht verschweigen und nicht blockieren**; Suche läuft weiter | ✅ |
| E31 | Titel-Zuordnung | Mehrere gewichtete Zeugen; **Popularität nur als Stichentscheid** | 🔑✅ |
| E32 | Export | **Grundrecht**, in Standardformaten; HTML-Datei wird Freigabe-Format | ✅ |
| E33 | Spiele | Playnite-Modell übernehmen, nicht nachbauen; **Spielzeit = Fortschritt** | ✅ |

---

## 4. Das Fundament

### 4.1 Kern und Fähigkeiten

> 🔑 **Der Kern darf niemals wissen, welche Medien es gibt.** Kein `if medium == "anime"`
> außerhalb eines Medien-Bausteins. Diese eine Zeile macht das Programm wieder zu einem
> Modulverbund mit Extraschritten.

Eine **Fähigkeit** ist kein Programm im Programm: gleicher Prozess, gleiche Bibliothek,
gleiche Hülle, gleiche Einstellungen. Sie meldet an, was sie kann. Abgeschaltet meldet sie
sich nicht — und **nichts anderes darf das merken**.

Der Installer entfernt **keinen Code**. Häkchen schreiben nur eine Liste in die
Konfiguration; Wiedereinschalten ist kein Nachinstallieren.

Diese Schnitte gab es schon: `youtube_app → geo → vpn` (Einbahn), `filme.py` ruft nie
zurück. Die Grenzen sind gezogen — sie bekommen nur einen billigeren Übergang.

### 4.2 Das Werk

**Die Trennregel:**

> 🔑 **Zählt der Fortschritt getrennt, sind es zwei Werke.
> Zählt er gleich, ist es ein Werk in zwei Ausgaben.**

| Fall | Urteil |
|---|---|
| Buch & Hörbuch | Kapitel 9 = Kapitel 9 → **ein Werk, zwei Ausgaben** |
| Novel DE & EN | gleiche Kapitel → **ein Werk, zwei Ausgaben** |
| Novel & KI-Hörbuch | gleiche Kapitel → **ein Werk, zwei Ausgaben** |
| Manga & Anime | Kap. 141 ≠ Folge 19 → **zwei Werke, verknüpft** |
| Alita & Last Order | eigene Zählung → **zwei Werke, verknüpft** |
| OVA zur Serie | eigene Zählung → **zwei Werke, verknüpft** |

Wer zu viel verschmilzt, macht Fortschritt bedeutungslos. Wer zu wenig verschmilzt, hat
vier Einträge für dasselbe Buch.

**Bestätigung von außen:** Open Library modelliert seit zwanzig Jahren wörtlich
*Work → Edition*. Dieselbe Trennung, unabhängig hergeleitet.

**Beziehungsarten:** Vorlage→Adaption · Fortsetzung/Vorgeschichte · Nebengeschichte ·
Sonderfolge (OVA/ONA/Special/Film) · Alternative Fassung · Sammlung.

> ⚠️ **Den Beziehungsgraphen nicht selbst bauen.** AniList führt ihn typisiert,
> MangaUpdates ebenso, TMDB hat Sammlungen, MusicBrainz hat den reichsten überhaupt.
> Selbst bauen wäre ein Forschungsprojekt statt eines Features.

**Reihenfolge** (OVA-Problem): Erscheinung ≠ Chronologie ≠ empfohlene Reihenfolge.
Graph speichern, Reihenfolge als **Wahl** anbieten, Community-Reihenfolgen importierbar.
Nicht berechnen wollen.

### 4.3 Die Leiter

Immer vier Sprossen, überall gleich geformt, nur anders benannt:

| | Sammlung | Gruppe | **Einheit** | Position |
|---|---|---|---|---|
| Anime | Staffel 2 | — | Folge 19 | Sek. 412 |
| Manga | — | Band 3 | Kap. 141.5 | Seite 14 |
| Novel | Arc 4 | Band 12 | Kap. 1204 | 63 % |
| Musik | — | Album | Titel 7 | Sek. 92 |
| Hörbuch | — | Teil 1 | Kap. 9 | Sek. 1840 |
| Film | Reihe | — | Teil 2 | Sek. 3120 |

Sortiert wird immer derselbe Vierer, gelesen die **Einheit**, gemerkt die **Position**.
Film und Lied sind Werke mit *einer* Einheit — Grenzfall, kein Sonderfall.

⚠️ **Die Einheit ist eine Dezimalzahl**, keine Ganzzahl (Kapitel 141.5).
Speicherform: die Leiter ist die Wahrheit, ein abgeleiteter Dezimalschlüssel
(`002.000.0019.0412`) dient nur der Sortierung und ist jederzeit neu berechenbar.

### 4.4 Das Register

Jede **Tatsache** wird gespeichert als: Wert · **Quelle** · **Datum** · Vertrauen ·
Korrekturmarke.

> 🔑 **Alles wird lokal kopiert.** Stirbt eine Quelle morgen, läuft die Bibliothek weiter.
> Das ist die Readarr-Versicherung, und sie kostet fast nichts.

**Vertrauensrangfolge pro Feld, nicht pro Quelle.** TMDB gewinnt bei Film-Covern,
MusicBrainz bei Titelreihenfolge, AniDB bei Folgennummern, MangaBaka bei Manga-Identität.
Nicht „X ist die beste Quelle", sondern „X ist die beste Quelle *für dieses Feld*".

⚠️ **Handkorrekturen müssen jede Neuanreicherung überleben.** Das ist der Punkt, an dem
die meisten Systeme scheitern: Nutzer korrigiert → nächster Lauf überschreibt → Nutzer
gibt auf. `overrides.json` aus SyncManga ist das bestehende Muster.

**Selbstheilung:** ein Hintergrundauftrag nimmt sich immer die ältesten und unsichersten
Einträge vor.

### 4.5 Die Warteschlange

Vorhanden in SyncYouTube: Auto-Retry mit Backoff, Resume nach Neustart, Persistenz.
Erwachsene Infrastruktur — sie wird verallgemeinert:

```
Auftrag { was · womit · Priorität · Versuche · Zustand · Zeitfenster }
  ├─ identifizieren   Werk erkennen, Kandidaten bewerten
  ├─ anreichern       Metadaten, Cover, Beziehungen
  ├─ beschaffen       Video / Kapitelbilder / Text / Audio
  ├─ umwandeln        → CBZ / EPUB / MKV / M4B, transkodieren
  ├─ prüfen           Linkgesundheit, Datei-Echtheit, Übersetzungsstand
  ├─ veredeln         Glossar · übersetzen · Rollen · vertonen · kolorieren
  ├─ erneuern         veraltete Erzeugnisse neu bauen (§10.4)
  └─ verteilen        auf Gerät spiegeln
```

**Prioritäten:** was gerade benutzt wird → sofort · Vorrat (N Einheiten voraus) → hoch ·
Masse → Nachtfenster · Erneuerung *besser* → niedrigste.

### 4.6 Die Ablage

- **Ort ≠ Werk.** Ein Werk hat *mehrere mögliche* Orte (NAS, lokaler Zwischenspeicher,
  Handy). Steht der Ort im Werk, kann man keine Platte umziehen.
- **Standardformate** (E06). Begründung: die Bibliothek überlebt das Programm. Kavita,
  Komga, Kobo, VLC, Jellyfin lesen sie alle.
- **Metadaten in die Datei**, nicht nur ins Register: ID3/Vorbis/MP4-Atome, MKV-Tags,
  EPUB-OPF, `ComicInfo.xml` im CBZ. Eine herausgelöste Datei muss sich selbst erklären.

**E28 — Pfade:** gespeichert wird **Wurzel-Kennung + relativer Pfad**
(`NAS-Filme` + `Der Wüstenplanet (2021)/…`), nie ein absoluter Pfad. Platte umziehen =
eine Einstellung ändern, alles folgt. Verschwindet eine Datei, wird der Eintrag **nicht
gelöscht**, sondern als *vermisst* markiert — der Fingerabdruck sucht sie woanders.
So überleben Plex und Jellyfin Laufwerkswechsel.

**E27 — Ordnerstruktur: übernehmen, nicht erfinden.** Dann lesen Jellyfin, Plex, Kavita,
Komga und Audiobookshelf die Bibliothek ohne Zutun — die Regel „überlebt das Programm"
in ihrer konkretesten Form. Quelle: TRaSH Guides, Jellyfin-Namenskonvention.

```
Filme/     Der Wüstenplanet (2021)/Der Wüstenplanet (2021).mkv
                                   ├── cover.jpg · poster.jpg
                                   └── Der Wüstenplanet (2021).de.srt
Serien/    Frieren/Season 01/Frieren - S01E14 - Der Zauber….mkv
Anime/     wie Serien, aber absolute Folgennummer mitführen (Fansubs zählen so)
Manga/     Solo Leveling/Solo Leveling Vol.01.cbz   (+ ComicInfo.xml im Archiv)
Musik/     Nujabes/Modal Soul (2005)/01 - Feather.flac  (+ cover.jpg)
Hörbücher/ Frank Herbert/Der Wüstenplanet (2021)/Der Wüstenplanet.m4b
           └── M4B: EINE Datei mit eingebetteten Kapiteln — der Standard
Novels/    Lord of the Mysteries/Band 03/Lord of the Mysteries - Band 03.epub
DJ-Sets/   Künstler @ Event-Ort (2026-07-14)/…            (MixesDB-Konvention)
```

**E29 — Umbenennen und Aufräumen:**

| Dateien | Standard |
|---|---|
| **Von uns beschafft** | umbenennen **an** — wir haben sie benannt |
| **Fremde / lokale Dateien** | **nur lesen.** Aufräumen ist eine Einladung **pro Ordner** |

Zwei Regeln machen aus „übergriffig" „hilfreich": **immer erst Probelauf** (vorher/nachher
als Liste, dann bestätigen — danach läuft der Ordner still weiter) und **immer rückgängig**
(Umbenennungs-Tagebuch). Wenn Irrtum nichts kostet, ist Eingriff nicht schlimm.

---

## 5. Die Oberfläche

### 5.1 Startseite

> **Ein Start, der fragt „Was willst du?", kostet eine Entscheidung — jeden Tag.
> Ein Start, der antwortet „Hier, mach weiter", kostet nichts.**

Aufbau: **Held** (die wahrscheinlichste Fortsetzung, ein Knopf) → **Angefangen**
(medienübergreifend) → **Neu für dich** → **Regale nach Medium** (nach Nutzung sortiert)
→ **Entdecken**.

Belege: Auswahl-Überlastung (Schwartz) — zu viele gleichrangige Optionen erzeugen Zögern
und Abbruch; Amazon zeigt bewusst 4–7. Unterbrochenes hat mehr Sog als Neues.

**Sortiert nach Absicht, nicht nach Gattung.** Medium ist ein Filter, kein Reiter.

**Ungenutztes sinkt, statt zu verschwinden** — eine ruhige Zeile ganz unten, aufklappbar.
⚠️ Reihenfolge nur **selten** neu rechnen (wöchentlich) und festnagelbar: Oberflächen, die
täglich umsortieren, sind berüchtigt dafür, gehasst zu werden.

**Anpassen im Moment des Ärgers**, nicht im Einrichtungsdialog: Rechtsklick aufs Regal →
*immer oben* · *nach unten* · *nicht mehr zeigen*. Keine Einstellungsseite für die
Startseite. Gilt **pro Profil × Gerät**.

**Vorschau-Schnipsel:** nur im Helden, nach ~1,5 s Verweilen, stumm, abschaltbar. Nie in
den Regalen — Bewegung ist Erregung, nicht Ruhe. Bei Fortgesetztem an *deiner* Stelle
starten, sonst auf die nächste Kapitelmarke schnappen statt fester Prozentzahl.

**Schrumpft sauber:** wer nur ein Medium nutzt, bekommt ein Ein-Medien-Regal. Dass der
Entwurf beim Schrumpfen nicht kaputtgeht, ist der Beweis für den Schnitt.

### 5.2 Geräte: eine Prioritätsleiter

> 🔑 **Nicht sechs Entwürfe für sechs Geräte — eine Rangfolge.** Jedes Element hat einen
> Rang; beim Schrumpfen fällt von unten weg.

**Drei Arten zu wachsen:**

| Regel | gilt für | Verhalten |
|---|---|---|
| **A · Mehr davon** | Regale, Kacheln, Listen | Kachel behält Größe, es passen mehr rein. 5120 px = 14 Kacheln, **nicht** 6 riesige |
| **B · Nebeneinander** | Detail, Warteschlange | ab ~2200 px neben statt über dem Regal |
| **C · Nie breiter** | alles Gelesene | 65–75 Zeichen, egal wie breit |
| **D · Fingerfreundlich** | alle Ziele | erkannt am **Zeigergerät**, nicht an der Breite |

**Zielgrößen:** WCAG 2.5.8 verlangt 24×24 px (Stufe AA, über den European Accessibility
Act seit Juni 2025 bindend), Apple empfiehlt 44, Material 48.
**Trefferfläche ≠ Symbolgröße** — Symbol 24 px, Innenabstand macht 48 daraus.

**Immer verboten:** waagerechtes Scrollen der Seite · Menüs, die über den Rand aufklappen ·
Fenster, die von Haus aus scrollen müssen · feste Pixelzahlen im Code.

⚠️ **Prüfstein:** jedes Bauteil wird bei **360 / 834 / 1280 / 3440** geprüft, bevor es
fertig ist. Bricht es bei einer Breite, ist es nicht fertig — nicht „später anpassen".

### 5.3 Farben

| Fläche | Nacht | Tag | |
|---|---|---|---|
| Regal | Tinte `#0E1217` | Papier `#F1EAE0` | schaltet |
| Leser | warm-dunkel `#1C1611` | Papier `#F6EFE3` | schaltet |
| Spieler | Bühne `#0A0A0B` | Bühne `#0A0A0B` | **fest** |
| Akzent | `#F0873C` | `#B4551A` | gleicher Ton, andere Helligkeit |

**Begründungen:**
- Der **Spieler** schaltet nie: ein heller Rahmen um einen Film ist auch mittags falsch.
  Spotify begründet seinen Dauer-Dunkelmodus wörtlich mit dem Kinosaal.
- Der **Leser** folgt nachts *nicht* dem Regal: lange Wellenlängen (Bernstein) stören den
  Schlaf am wenigsten. Tinte ist ein guter Rahmen, ein schlechter Lesegrund um Mitternacht.
- **Für ausdauerndes Lesen ist heller Grund im Vorteil** — besonders bei Astigmatismus.
  Deshalb hat der Leser eigene Modi, unabhängig vom Rest.

⚠️ **Kein reines Schwarz mit reinem Weiß, nirgends.** 21:1 lässt Schrift ausfransen
(Halation, betrifft rund die Hälfte der Menschen mit Astigmatismus). Empfohlen `#121212`–`#1E1E1E`.

**Farbregeln:** Orange ist nie Fläche, immer Zeichen · **Farbe kodiert Zustand, Form und
Kürzel kodieren Medium** · Zustandsfarben aus SyncManga bleiben (grün lese · gelb pausiert ·
weiß Backlog · blaugrau aufgeholt · türkis abgeschlossen).

### 5.4 Haltung zum Menschen

> **Die Oberfläche fordert nie, sie bietet an. Nichts auf der Startseite ist eine Aufgabe.**

Eine Oberfläche, **drei Tiefen**:
1. **Fläche** — eine Handlung
2. **Griffbereit** — 3–5 Dinge während des Konsums, bei Ruhe ausgeblendet
3. **Werkstatt** — alles andere (Long Strip, Doppelseite, Sepia, Smooth Scrolling, …)

⚠️ **Die Voreinstellungen müssen so gut sein, dass 90 % die Werkstatt nie öffnen.**
Optionen sind für die 10 %, keine Entschuldigung für schwache Standards.

| Typ | braucht | bekommt |
|---|---|---|
| Fokussiert | rein, ohne Störung | Held + ein Knopf |
| Normal | dass es einfach geht | gute Voreinstellungen |
| Hyperaktiv / ADHS | wenig Reiz, klare Rangfolge | keine Bewegung in Regalen, `prefers-reduced-motion`, Schalter „alles ruhig" |
| Gelangweilt | Überraschung | Joker (§11) und Regal „Vergraben" |
| Perfektionist | Vollständigkeit, Kontrolle | Werkstatt, lesbares Profil, Statistik, „alles zeigen" |

**Belegt falsch, in jeder Gruppe:** einrichten müssen bevor man genießen darf ·
Bewegung, die man nicht bestellt hat · verstecken, was das System über einen denkt.

### 5.5 Flüssigkeit

1. **Vorgerechneter Startseiten-Zustand** — die Startseite fragt nie die Bibliothek
2. **Skelett in Endmaßen** — nichts springt; das Ärgernis ist Springen, nicht Spätsein
3. **Winzige Unschärfe-Vorschau** im Zustand (wenige hundert Byte je Cover)
4. **Nur Sichtbares zeichnen** — 3000 Lieder, 20 Elemente im Dokument
5. **Nie beim Start arbeiten** — Scans und Prüfungen in die Warteschlange
6. 🔑 **Die Oberfläche wartet nie aufs Netz.** Lokal zuerst, das Netz aktualisiert nur den
   lokalen Stand. ⚠️ SyncMangas HTML-Datei fühlt sich instantan an, *weil* sie das tut —
   diese Eigenschaft darf beim Umstieg auf einen Server nicht verlorengehen.

---

## 6. Welche Medien — die Zwiebel

> **Ein Medium gehört rein, wenn es (a) Einheiten hat, an denen Fortschritt messbar ist,
> und (b) eine Quelle, die es identifiziert.**

| Schicht | Medien |
|---|---|
| **1 · Kern** | Anime · Manga · Novel · Film · Serie · Musik · Hörbuch |
| **2 · Naher Ring** | Webtoon/Manhwa/Manhua · Comic · eBook · Podcast · Hörspiel · **Fanfiction** · Doku · YouTube-Kanal als Serie |
| **2 · Naher Ring** *(Nachtrag)* | **DJ-Sets / Mixe / Radioshows** · Vorträge & Konferenztalks |
| **3 · Ferner Ring** | Visual Novel (nur Titel) · Artbook/Doujinshi · Live-TV · Konzertmitschnitt · **Spiele + Emulatoren** · **Sportevents** · Theater-/Opernaufzeichnung · **physische Sammlung** |
| **draußen** | Memes · lose Dateien · Fotos · Software allgemein |

- **Fanfiction: eigenes Medium**, nicht unter Light Novel. Struktur identisch, aber
  Herkunft, Rechte und Qualitätsverteilung völlig anders. AO3 hat das beste Tag-System im
  Netz. Dazu RoyalRoad, ScribbleHub, Wattpad.
- **Visual Novels bewusst ohne Fortschritt** — der ist dort ein Baum, keine Zahl.
  Als Titel führen, nicht hineinzwingen.
- **Memes: die Grenze.** Keine Einheiten, kein Fortschritt, keine Identität — eine Datei,
  kein Werk.
- **Die Schichtzuordnung ist nutzerabhängig.** Wer 5000 Visual Novels hat, für den rückt
  die Schicht nach oben. Die Ringe ordnen den *Bauaufwand*, nicht die Wichtigkeit.
- **DJ-Sets** passen elegant: der Mix ist die Einheit, die **Tracklist wird zu
  Kapitelmarken** — dann verhält sich ein Set wie ein Hörbuch mit Kapiteln.
  Quellen: **1001Tracklists** (API mit `find_by_media_url`, nimmt eine SoundCloud- oder
  YouTube-Adresse und liefert die Tracklist) und **MixesDB**.
  ⚠️ Automatisches Erkennen von Tracks *in* einem Mix ist ungelöst — AcoustID scheitert an
  Beatmatching und Tonhöhenverschiebung. Marken müssen von Hand setzbar sein.
- **Sportevents** passen wörtlich in die Leiter: Saison 25/26 → Spieltag 14 → Spiel → Minute.
- **Physische Sammlung**: „ich besitze es, habe aber keine Datei" — ein Werk ohne Ausgabe
  ist im Modell erlaubt. Quelle: Discogs, Open Library.
- **Spiele (E33):** **Playnite** ist der Maßstab (MIT, offen) — importiert Steam, Epic, GOG,
  EA, Ubisoft, Battle.net, Xbox, Amazon **und Emulatoren** (RetroArch, Dolphin, PCSX2,
  RPCS3, PPSSPP, MAME). **Nicht nachbauen, anbinden.**
  Aufnahmebedingung erfüllt, weil **Spielzeit der Fortschritt ist** (Steam liefert sie),
  Errungenschaften als zweite Skala. ROM = Werk, Emulator = „Spieler" — dieselbe
  Rollenverteilung wie Datei ↔ mpv.
  Von Steam übernehmen: **Big Picture ist die Vorlage für den Fernsehmodus** (nicht Netflix),
  und „Zuletzt gespielt" oben ist eine unabhängige Bestätigung unserer Startseite.
- **Kein Medium, aber gebraucht:** Streaming-Abos als **Verfügbarkeitsquelle**
  („wo kann ich das sehen", JustWatch) — gehört zur Verfügbarkeit, nicht zur Zwiebel.

---

## 7. Die Quellen

| Medium | Identität & Metadaten | Verfügbarkeit | Beziehungen |
|---|---|---|---|
| **Anime** | **AniDB** (Referenz für Folgen/OVAs), AniList, MAL, Kitsu | AniList, Simkl | AniList Relations |
| **Manga** | **MangaBaka**, MangaUpdates, AniList | MangaUpdates | AniList |
| **Novel / LN** | **MangaBaka**, NovelUpdates, RanobeDB | NovelUpdates-RSS | AniList |
| **Film** | **TMDB**, OMDb | JustWatch | TMDB Collections |
| **Serie** | TMDB, **TheTVDB** | TMDB, Simkl | TMDB |
| **Musik** | **MusicBrainz**, Discogs | ListenBrainz | **MusicBrainz Relations** |
| **Hörbuch** | **Audnexus** (ASIN), Open Library, LibriVox | — | Open Library |
| **Buch / eBook** | **Open Library** (ISBN), Google Books | — | Open Library Works |
| **Podcast** | **Podcast Index** | RSS *ist* die Wahrheit | — |
| **Comic (West)** | Comic Vine, Metron | — | Comic Vine |
| **Visual Novel** | **VNDB** | — | VNDB |
| **Fanfiction** | AO3 (Tags!), RoyalRoad, ScribbleHub | RSS | AO3 Series |

### 7.1 MangaBaka statt MangaDex — begründet

**MangaBaka** sammelt und *säubert* AniList, Kitsu, MangaDex, MangaUpdates, MyAnimeList,
Anime News Network, Anime-Planet und Shikimori, führt in jedem Eintrag die Verweise auf die
anderen Tracker mit, hat eine API mit Explorer und deckt **Manga *und* Light Novels** ab.
→ **Ein Adapter statt sechs, inklusive Fremd-IDs.**

**MangaDex ist als Lesequelle strukturell unzuverlässig** — und das ist kein Fehler,
sondern Absicht:
- Ein Massen-DMCA entfernte Kapitel für ~7000 Titel.
- Scanlation-Gruppen können Entfernung verlangen; **API-Nutzer sind verpflichtet, das zu
  respektieren**.
- Regionale Sperren kommen dazu.
- Die Option „nicht verfügbare Kapitel zeigen" existiert **nur zum Nachhalten**.

> **Meinung:** MangaDex ist ein rechtetreuer Hoster — deshalb hat sein Katalog Löcher
> **by design**. Als Metadaten- und ID-Quelle gut, als primäre Lesequelle falsch.
> Der Frust mit der Manga-Leseliste war kein Bedienfehler.
>
> **Entscheidung E21:** MangaDex nur für Metadaten. Lesequellen kommen aus dem
> Quellenkatalog (§9.2). MangaBaka wird Erstquelle für Manga und Novel.

### 7.2 Hörbuch-Identität — der unangenehme Fall

- Audible vergibt **ASIN, nicht ISBN** — und ASINs sind **regionsgebunden**
  (Audible.de ≠ Audible.com für dasselbe Buch).
- Audible-Exklusivtitel haben meist **gar keine ISBN**.
- **Audnexus** ist die inoffizielle Audible-API (nutzen auch Audiobookshelf und die
  Plex-Agenten).

**Folge:** das **Buch** trägt die stabile Identität (ISBN / Open-Library-Work), das
**Hörbuch hängt als Ausgabe daran** — mit ASIN, Sprecher, Sprache. Nur so verhalten sich
deutsche und englische Fassung desselben Buchs vernünftig. eBooks sind der einfachere Fall.

**Kein „Übersetzungsstand" beim Hörbuch**, weil es fertig erscheint. Die mittlere Zahl
bedeutet dort **„in deiner Sprache verfügbar"**. Gleicher Platz, andere Bedeutung.

### 7.3 Quellen-Späher

Kuratierte Sammlungen, die beobachtet werden statt einmalig abgeschrieben:
**EverythingMoe** (inkl. „Graveyard" toter Seiten — Gold für die Quellen-Ampel) ·
**FMHY** · **wotaku.wiki** · **thewiki.moe** · awesome-anime-sources.

Ein Auftrag prüft sie regelmäßig auf Neuzugänge und Todesfälle. ❓ Halbautomatisch mit
Vorschlagsliste, nicht blind übernehmen.

---

## 8. Erkennung & Identität

### 8.1 Wie die Bibliothek entsteht

| Weg | sieht | sieht nicht |
|---|---|---|
| **Browserverlauf** | alles Besuchte rückwirkend | keinen Fortschritt *in* der Seite, nichts aus Apps |
| **Browser-Erweiterung** | die lebende Seite: Kapitelnummer im DOM, Scrollstand, **auch hinter Login** | nur was während des Laufens besucht wird |
| **Offene APIs** | vollständige Listen mit Fortschritt | nur was dort gepflegt ist |
| **RSS** | neue Kapitel der eigenen Liste | keinen Fortschritt |

**Komplementär, nicht Ersatz:** Verlauf füllt einmalig auf, Erweiterung hält laufend
präzise nach. **Ein großer Erstlauf, danach nur Neues** — und ein neuer Großlauf, wenn die
Erkennung selbst aktualisiert wurde.

| Plattform | Weg |
|---|---|
| AniList, MyAnimeList | offizielle APIs mit OAuth |
| Kitsu, MangaUpdates | APIs |
| NovelUpdates | keine API — **RSS je Leseliste** reicht |
| Crunchyroll | keine offizielle API; brauchbare Werkzeuge nutzen das **Sitzungs-Cookie aus dem Browser**, ohne Passwort |
| Amazon Prime Video | kein Export — **nur über die Erweiterung** |
| Netflix | Verlaufs-Export (CSV), halbautomatisch |

> 🔑 **E16: Das Programm speichert niemals Zugangsdaten. Es benutzt nur Sitzungen, die der
> Browser ohnehin hat.** Autofill/Passwortspeicher auslesen wäre der Punkt, an dem das
> Programm von „liest meine Spuren" zu „hält meine Schlüssel" kippt. Gewinn gegenüber der
> Erweiterung: fast null. Risiko: riesig. SyncYouTube fährt den Cookie-Weg bereits.

### 8.2 Die Identifikations-Kaskade

Für Dateien, die niemand sauber benannt hat (`"Nujabes" - Aruarian Dance (HQ)_final2.mp3`):

| Stufe | Mittel |
|---|---|
| **0 · Herkunft merken** | Wer selbst lädt, **weiß** was es ist. Identität sofort in Datei *und* Register schreiben. `geladen_log.json` macht das bereits |
| **1 · In die Datei schauen** | ID3, Vorbis, MP4-Atome, MKV-Tags, EPUB-OPF, `ComicInfo.xml` |
| **2 · Fingerabdruck** 🔑 | **AcoustID/Chromaprint** (Musik, erkennt am Klang) · OpenSubtitles-Hash (Video) · ISBN im Text (Buch) |
| **3 · Namen zerlegen** | Erst jetzt. Release-Namen sind **Grammatik**, nicht Chaos: `[Gruppe] Titel - Folge (Auflösung) [CRC]`, `S01E02` |
| **4 · Fragen** | Ins **Postfach** („⚠ Braucht Hilfe"), nie während des Genusses. Immer 3 Kandidaten mit Cover — Wiedererkennen statt Erinnern. Gebündelt |
| **5 · Lernen** | Jede Handkorrektur wird zur Regel (`overrides.json`). „`[Erai-raws]` ist eine Gruppe" gilt danach für alles |

> 🔑 **Der Fingerabdruck schlägt den Namen. Immer.** Der Dateiname ist die *letzte*
> Auskunft, nicht die erste. Die meisten Programme machen es andersherum.

**E31 — Titel-Zuordnung: mehrere Zeugen, gewichtet.** Ähnlichkeit allein reicht belegt
nicht — Levenshtein & Co. erzeugen Falschtreffer, und Manga-Titel sind das schlimmste
denkbare Feld dafür („Ich wurde der X der Y" ist ein ganzes Genre).

| Zeuge | Gewicht | Bemerkung |
|---|---|---|
| **Autor / Zeichner** | ⭐⭐⭐ | stärkster Einzelunterscheider — kaum jemand nutzt ihn |
| **Cover-Wahrnehmungshash** | ⭐⭐⭐ | billig, sehr stark, **in dieser Szene ungenutzt** |
| Titel über **alle** Varianten | ⭐⭐ | Romaji, Englisch, Original, Synonyme — MangaBaka liefert alle |
| Erscheinungsjahr | ⭐⭐ | trennt Remakes und Namensvettern |
| Typ + Ursprungsland | ⭐⭐ | Manga / Manhwa / Manhua |
| Kapitelzahl-Plausibilität | ⭐ | 1100 ≠ 40 Kapitel |
| **Popularität** | ⭐ | **nur Stichentscheid** |

> ⚠️ **Popularität ist ein Stichentscheid, kein Beweis.** Wiegt sie schwerer als Autor oder
> Jahr, werden **systematisch obskure Werke in berühmte einsortiert** — die schlimmste
> Fehlerart, weil sie unsichtbar ist.

**Vor dem Vergleich normalisieren:** Kleinschreibung · Unicode-NFKC · Satzzeichen weg ·
Makron auflösen (ō → ou/o) · Staffel-/Teil-Marker weg · Zusätze wie „(Official)",
„Manhwa", „Novel" weg.

**Gegen Umbenennungen** (Asura Scans benennt Serien regelmäßig um):

> 🔑 **Die Identität eines Werks hängt niemals am Titel einer Seite.**
> Seitentitel sind Eigenschaften, nicht Identität.

Praktisch: **Slug-Geschichte führen** — jede URL und jeder Slug, den wir je gesehen haben,
wird behalten. Benennt eine Seite um, stirbt der alte Link → ⚠-Ablauf → der neue wird
angehängt.

**Drei Ausgänge, nie zwei:** sicher → übernehmen · unsicher → **Postfach mit 3 Kandidaten
+ Cover** · sehr unsicher → gar nichts. Lieber eine Lücke als ein falscher Eintrag.

**Zum Ziel 100 %:** nicht erreichbar — 99 % schon. Das richtige Ziel ist nicht
„100 % automatisch", sondern **100 % geklärt**: die Reste warten höflich in einem Kasten,
den man freiwillig öffnet, statt zu unterbrechen.

### 8.3 Bruchsicherheit

⚠️ Bekannter Schaden aus SyncManga: eine Seite schrieb `ch` statt `chapter`, und es landeten
falsche Einträge in der Liste.

**Gegenmaßnahmen:**
1. **Muster mit Alternativen** statt einem festen Muster:
   `chapter|chap|ch|c|kapitel|episode|ep|folge` — und **Wortgrenzen erzwingen**
   (der v0.4.3-Fix „chapter token no longer matches inside other words" ist genau das).
2. **Zwei Zeugen.** Ein Fund gilt erst, wenn er aus zwei unabhängigen Merkmalen folgt
   (z. B. URL-Muster *und* Seitentitel).
3. **Plausibilität statt Vertrauen.** Kapitel 4711 bei einem Werk mit 120 Kapiteln ist
   verdächtig, nicht wahr. Sprünge > 20 % gehen ins Postfach.
4. **Stichproben-Prüfung.** Ein Auftrag zieht regelmäßig Zufallsstichproben und vergleicht
   Erkanntes mit dem, was die Seite tatsächlich sagt. Weicht es ab, wird das Muster
   markiert — bevor es hundert Einträge verdirbt.
5. **Jede Erkennung merkt sich, welches Muster sie erzeugt hat.** Wird ein Muster als
   kaputt erkannt, lassen sich genau dessen Ergebnisse zurückrollen.

---

## 9. Beschaffung

### 9.1 Anbindung ohne Abhängigkeit

> 🔑 **E11: Nie ein fremdes Datenmodell in den Kern lassen.** Adapter übersetzen
> Fremdsprache in Werk-Sprache. Der Kern weiß nicht, dass Sonarr existiert.
> Dieselbe Einbahnregel wie `youtube_app → geo → vpn`, nur nach außen.

| Ausleihen | Selbst besitzen |
|---|---|
| Indexer-Klempnerei (**Prowlarr**) | Die Bibliothek |
| Download-Clients | Metadaten & Identität |
| Release-Namen zerlegen (Sonarr: Jahre an Sonderfällen) | Fortschritt & Beziehungen |
| Qualitätsprofile | Was der Nutzer sieht |

**Stand *arr 2026:** Sonarr · Radarr · Lidarr · Prowlarr · Bazarr · Tdarr ·
Jellyseerr · Mylar3/Kapowarr · Recyclarr · Huntarr · Unpackerr.
⚠️ **Readarr eingestellt** (Mitte 2025, an den Metadaten). Nachfolger jung: Chaptarr,
LazyLibrarian, rreading-glasses. → Bücher/Novels/Manga besitzen wir von Tag eins.

### 9.2 Der Quellenkatalog

> 🔑 **E12: Der Katalog ist eine Laufzeitdatei, nie Repo-Inhalt.**

Begründung (recherchiert): Sony nahm mit *einer* DMCA-Meldung über 200 Aniyomi-Extensions
offline. FAKKU ging 03/2026 gegen Mihon-Extension-Repos vor. Kakao drohte Tachiyomis
Entwicklern persönlich — das Projekt wurde eingestellt.
**Ziel war nie die Reader-Engine, immer der Quellenkatalog.**

⚠️ `data/sources.json` und `data/readers_pattern.json` liegen heute **öffentlich** im
SyncManga-Repo und sind genau diese Artefaktklasse. Vor dem Umzug zu entscheiden.

**Bauform:** **abonnierbare Quellenlisten.** Adresse einfügen → wird regelmäßig geholt →
Quellen erscheinen; Liste entfernen → weg. Wie uBlock seine Filterlisten und Mihon seine
Extension-Repos seit 2024. Mit Prüfsumme gegen entführte Adressen; **eigene Listen ranken
über geteilten**.

**Gruppen-Vorlieben:** MangaDex führt die Scanlation-Gruppe pro Kapitel, Nyaa/AnimeTosho
die Release-Gruppe. → *„bevorzuge Erai-raws"* / *„diese Gruppe nie"* ist umsetzbar.

### 9.3 Seiten hinter JavaScript

Zweistufig, weil teuer nur wenn nötig (Stand 2026):

1. **TLS-Nachahmung zuerst** — `curl_cffi` / `curl-impersonate` bilden den
   TLS-Fingerabdruck und die HTTP/2-Einstellungen echter Browser nach. Leicht und schnell.
   Reicht, wenn die Erkennung fingerabdruckbasiert ist.
2. **Echter Browser nur bei echten Aufgaben** — **nodriver** (Nachfolger von
   undetected-chromedriver) oder SeleniumBase UC Mode.
3. ⚠️ **FlareSolverr und puppeteer-stealth gelten als veraltet** und werden von aktuellem
   Cloudflare „auf Sicht" erkannt. Nicht darauf bauen.

**Und die ehrliche Regel:** eine Seite, die sich aktiv wehrt, ist eine schlechte Quelle.
Erkennungsaufwand ist ein **Abwertungsgrund** in der Quellen-Rangliste, kein Wettrüsten.

### 9.4 Echtheitsprüfung — gegen Werbung und Fälschungen

Problem: 700 MB „Film", nach 30 Minuten nur noch Werbung. Oder ein Download, der eine
Anzeige statt des Videos ist.

**Prüfkette nach jedem Download, vor dem Einlagern:**

| Prüfung | Mittel |
|---|---|
| Ist es überhaupt das Format? | `ffprobe` — Container, Spuren, Codecs |
| Passt die Länge? | Soll-Laufzeit aus TMDB/AniDB ± 5 % |
| Ist durchgehend Bild da? | Stichproben über die Länge; Schwarzbild-Erkennung (`blackdetect`) |
| Ist durchgehend Ton da? | `silencedetect` — lange Stille am Stück ist verdächtig |
| Passt die Auflösung zur Behauptung? | „1080p" im Namen vs. tatsächlicher Strom |
| Ist es dieselbe Datei wie erwartet? | Größe + Hash gegen die Ankündigung |
| Bei Kapitelbildern | Bildmaße, Dateigröße, Anzahl vs. erwartete Seitenzahl |

⚠️ **Nicht bestandene Prüfung = automatisch zurück in die Warteschlange mit anderer
Quelle**, plus Abwertung dieser Quelle. Der Nutzer erfährt es erst, wenn *alle* Quellen
gescheitert sind.

**E30 — Mängel deklarieren.** Nicht jeder Makel ist ein Ausschlussgrund:

> 🔑 **Kein Mangel wird stillschweigend hingenommen — und keiner blockiert.** Er steht in
> einem Wort auf der Kachel, und die Warteschlange sucht im Hintergrund weiter. Findet sie
> eine bessere Fassung, wird getauscht.

| Mangel | Nachweis (alles ffprobe/ffmpeg, alles billig) |
|---|---|
| **Eingebrannte Untertitel** | keine Untertitelspur + Release-Name („HardSub") + Gruppen-Ruf |
| **Übersteuerter Ton** | EBU-R128: True Peak > 0 dBTP, Lautheit außerhalb der Norm |
| **Falsches FLAC** (aus MP3) | Spektrum: harte Kante bei 16 kHz — die klassische Plage |
| **Falsche Auflösung** | „1080p" im Namen vs. tatsächlicher Strom |
| **Fehlende Tonspur** | Sprachen im Container vs. erwartet |

Ergebnis ist ein **Qualitätsblatt** je Datei, im Regal auf ein Wort verdichtet:
`⚠ eingebrannte Untertitel` · `⚠ Ton übersteuert` · `✓ geprüft`.

### 9.5 Torrent, VPN, Schadsoftware

**Eigener Client:** ja — **libtorrent** treiben (die Bibliothek unter qBittorrent und
Deluge, mit Python-Anbindung). Kein eigenes BitTorrent schreiben.

**Sicherheit — der Mechanismus heißt nicht Killswitch, sondern Bindung:**
den Client an die **Netzwerkschnittstelle** des VPN binden. Fällt der Tunnel, verschwindet
die Schnittstelle und der Verkehr **hört auf**, statt auf die normale Leitung
zurückzufallen. Senkt die Leckwahrscheinlichkeit „auf nahezu null".
*Ein Killswitch schützt das ganze Gerät, eine Bindung genau diese Anwendung.*

> 🔑 **E17: Der Nutzer entscheidet, was er tut. Das Programm entscheidet, dass es nicht aus
> Versehen passiert.** Keine Übertragung über die nackte Leitung, jemals stillschweigend.
> Abschalten geht — einmal, ausdrücklich, mit klarem Satz, nicht vergraben.
> Das ist der Unterschied zwischen einer *Entscheidung* und einem *Versehen*.

**Regel pro Quelle:** LibriVox, Linux-Abbilder, die kodinerds-M3U brauchen keinen Tunnel.
Alles vom Nutzer Hinzugefügte braucht ihn standardmäßig.

**Schadsoftware — ohne PC-Polizei:**
1. **Dateiartenfilter:** Mediensammlungen enthalten `.mkv/.mp4/.cbz/.epub/.flac`.
   `.exe/.scr/.lnk/.bat/.js/.vbs` in einem „Film"-Torrent = **Alarm, kein Import**.
2. **Keine Archive still auspacken.** Passwortgeschützte Archive mit Textdatei daneben sind
   das klassische Muster — nie automatisch öffnen.
3. **Doppelte Endungen und Rechts-nach-links-Tricks** erkennen (`Film.mp4‮exe.`).
4. **Nichts wird ausgeführt, nie.** Das Programm öffnet Medien, keine Programme.
5. **Windows Defender ist da** — die heruntergeladene Datei einmal prüfen lassen (MpCmdRun),
   statt einen eigenen Scanner zu bauen.
6. **Quellen mit Fundmeldung werden abgewertet** — Sicherheit fließt in die Rangliste ein.

---

## 10. Veredelung

### 10.1 Das Werk-Wissen — ein Artefakt, drei Nutzen

| Eintrag | Übersetzung | Vertonung | Kolorierung |
|---|---|---|---|
| Figuren, Namen (Original → Fassung) | Konsistenz | Zuordnung | Wiedererkennung |
| Wer ist wer, Beziehungen | Anreden, Pronomen | Dialogzuordnung | — |
| Charakterzüge, Alter, Ton | Sprachebene | Stimmenwahl | — |
| Begriffe, Sekten, Techniken | Konsistenz | Aussprache | — |
| Aussehen (Haare, Augen, Kleidung) | — | — | Farbtreue |

> 🔑 **E15:** Deshalb ist das Werk-Wissen ein eigenes Ding, kein Nebenprodukt.
> Eine Korrektur darin schickt **alle betroffenen Kapitel** zurück in die Warteschlange —
> Übersetzung *und* Vertonung.

### 10.2 Übersetzung

**Das Glossar ist der Hebel.** Unlesbar macht MTL nicht die Grammatik, sondern dass der
Held in Kapitel 3 „Ye Chen", in Kapitel 40 „Leaf Dust" heißt. Kommerzielle Anbieter
verkaufen genau das als Alleinstellungsmerkmal; im offenen Bereich macht es niemand gut.

**Güteskala** (medienübergreifend):
⛔ nicht übersetzt · 🤖 MTL roh · ✨ MTL + KI-Korrektur · 🖐 von Hand · ⭐ offiziell

⚠️ Ehrlichkeit: eine KI kann eine vorhandene Übersetzung **polieren**, aber nicht
*korrigieren*, wenn sie das Original nicht sieht. Ohne Rohtext ist es Kosmetik.
**Beides ist legitim, muss aber unterschiedlich etikettiert sein.**

**Vorgehen:** Rohtext holen → vorhandene Übersetzung daneben → vergleichen, korrigieren,
zusammenführen. Deutsch als Ziel: direkt aus dem Original, nicht über Englisch
(sonst zweifacher Verlust).

**Sprichwörter** ❓ — chinesische und japanische Redewendungen brauchen eine Haltung:
wörtlich mit Fußnote, sinngemäß europäisch, oder Mischform. Zu besprechen.

**Namens-Verwestlichung** — als Option, ausdrücklich abschaltbar, immer im Glossar mit
Original vermerkt.

**Marktlücke:** NovelUpdates hat **keinen zuverlässigen MTL-Marker** — seit Jahren im Forum
gefordert, nicht sauber umgesetzt. Die Kennzeichnung ist echtes Neuland.

### 10.3 Vertonung

> **E14: Ein Ein-Sprecher-Modell, zeilenweise, mit gewechselter Stimme — dann zusammensetzen.**
> Gibt unbegrenzt viele Stimmen bei ~8 GB VRAM. Mehr-Sprecher-Modelle (Dia2, VibeVoice,
> ~24 GB) kaufen natürliches Sprecherwechseln — was ein Hörbuch gar nicht will.

| Modell | Rolle | Bedarf |
|---|---|---|
| **Chatterbox** (MIT) | Arbeitspferd, Klonen, Spitzenqualität | ~8 GB |
| **Kokoro-82M** | Masse und Notnagel, läuft auf CPU | ~3 GB |
| **XTTS-v2** | Klonen aus ~6 s, 17 Sprachen inkl. Deutsch | mittel |
| **IndexTTS-2** | 8-Emotionen-Vektor, Vorgabe je Figurenzeile, für Hörbuch gebaut | prüfen |
| **Step-Audio-EditX** | Wut/Freude/Trauer/Aufregung/Furcht/Überraschung, nachsteuerbar | prüfen |

**Emotion ist technisch gelöst — das Problem ist zu wissen, welche.** Also ein Durchgang,
drei Ergebnisse: **wer spricht · wie gestimmt · wie schnell.**

**Drei Hebel gegen „künstlich":**
1. Aus der **Szene** ableiten, nicht aus dem Satz
2. **Zurückhaltung** — Überspielen ist das Erkennungsmerkmal Nummer eins
3. **Der Erzähler bleibt ruhig** — nur Dialoge bekommen Emotion (so arbeiten
   professionelle Hörbücher, deshalb ermüden sie nicht)

> **Der Vorteil ist nicht das Modell, sondern der Zusammenhang.** Ein Dienst vertont ein
> Kapitel isoliert. Wir haben Glossar, Figurenblätter, die ganze bisherige Geschichte und
> unbegrenzt Zeit auf eigener Hardware.

**Stimme folgt dem Zustand, nicht dem Alter.** Wichtig für Wuxia/Xianxia: Helden sind
Jahrtausende alt und klingen wie 20; ein Durchbruch kann *verjüngen*; Körpertausch,
Verkleidung und Besessenheit sind Alltag. Daher pro Figur eine **Zustands-Zeitleiste** mit
freien Bezeichnungen — und die Annotation trennt **wer spricht** von **wessen Stimme**.

**Harte Wechsel an Zeitsprüngen**, nicht gleitende Drift: Geschichten altern Figuren an
Zeitsprüngen, dort erwartet der Hörer die Veränderung ohnehin.

**Rechnung auf JBs Homeserver** (256 GB RAM, 32 GB VRAM geteilt, 64 TB SSD + 64 TB HDD):

| | |
|---|---|
| Novel-Kapitel gesprochen | ~20 Min ≈ **10 MB** (64 kbit/s mono) |
| 1000-Kapitel-Novel komplett | ~330 Std ≈ **10 GB** |
| Hundert solche Novels | **~1 TB** von 128 TB |

→ **Rechenzeit ist knapp, Speicher nicht.** Vorab erzeugen ist die offensichtliche Wahl.
**Vorrat** von N Einheiten über dem Lesestand, **Nachtfenster** für Masse,
**Vordrängeln** für Aktuelles.

### 10.4 Erneuerung

Jedes Erzeugnis trägt einen **Stempel**: Modell, Version, Stimmen-IDs, Glossar-Stand,
Parameter.

| Auslöser | heißt | Folge |
|---|---|---|
| Glossar/Name korrigiert | **falsch** | sofort neu, automatisch |
| Neues, besseres Modell | **besser** | langsame Spur: nur Benutztes, nachts, ältestes zuerst |
| Parameter verstellt | **anders** | nichts |

Das Alte bleibt liegen, bis das Neue fertig ist. Dazu ein Knopf „jetzt alles neu".
**Der Nutzer erklärt nichts** — er sieht `🔄 neuere Fassung`, ein Tipp priorisiert.

### 10.5 Kolorierung

Nicht als Massenlauf: ein Kapitel = ~20 Bilder, eine 200-Kapitel-Serie = 4000 Bilder —
das koloriert länger, als man zum Lesen braucht. Und Manga ist *für* Schwarzweiß gezeichnet.

**Auf Zuruf:** Rechtsklick → „koloriert lesen" → Auftrag → morgen fertig. Deutlich
gekennzeichnet, Original immer einen Tipp entfernt. Farbtreue kommt aus dem Werk-Wissen.

---

## 11. Empfehlungen

**Drei Stufen, aufsteigend im Aufwand:**
1. **Adaptions-Graph** — geschenkt und todsicher: Manga gelesen → Anime existiert
2. **Geteilte Merkmale** — AniList-Tags gelten für Anime *und* Manga *und* LN;
   TMDB-Keywords für Film. „Langsam, melancholisch, Fantasy" quer über alle Medien
3. **Kombinierte Ebenen** — ein Profil aus dem *Schnitt* des Abgeschlossenen über alle
   Medien: findet Film, Album und Novel derselben Stimmung

**Regeln:**
- **Nur Abgeschlossenes zählt positiv.**
- ⚠️ **Liegengelassenes zählt gar nichts.** Bei dreißig Jahren Sammlung ist Vergessen der
  Normalfall, nicht Ablehnung. Nur ausdrückliches „weglegen" zählt negativ.
- 🐿️ Daraus wird ein Regal: **„Vergraben"** — vor Jahren angefangen und vergessen.
- **Nur was nicht im Regal steht.**
- **Immer mit Grund** („weil du Vinland Saga abgeschlossen hast") — ohne Grund fühlt es
  sich wie Werbung an, mit Grund wie ein Freund.

**Ablehnen in drei Stufen:** *nicht jetzt* (6 Monate weg, lernt nichts) · *nicht dafür*
(der **Grund** war falsch — schärfste Rückmeldung, nur möglich weil Gründe sichtbar sind) ·
*nie* (gesperrt, Merkmale bekommen Minuspunkte).
**Negative Merkmale als erste Klasse** (ein Schalter für „Isekai nie wieder").

**Bewertungen nur gewichtet:** eine 10,0 aus 3 Stimmen darf keine 8,7 aus 40.000 schlagen —
**bayessche Schrumpfung** zum Gesamtmittel (IMDb-Formel). Quellen **getrennt halten und
gewichtet zusammenführen**, nicht mitteln: MyAnimeList und MangaUpdates haben anderes
Publikum.

**Der Joker heißt Serendipität** und ist belegt *nötig*: wer nur auf Passung optimiert,
erzeugt eine Filterblase, in der nie etwas aus unbekannten Kategorien auftaucht. Maß dafür
ist **bayessche Überraschung** (unerwartet *und* voraussichtlich gut bewertet).
→ **Ein Platz je Regal ist ein Joker**, gekennzeichnet (`🎲 Querschläger`); sein Nein zählt
in einen **eigenen** Topf.

> 🔑 **E19: Das Profil ist lesbar und von Hand korrigierbar.** Eine Seite „Das denkt
> SyncRegal über dich" — sichtbar, editierbar, exportierbar, löschbar. Netflix und Spotify
> verstecken das. Es ist die einzige ehrliche Antwort auf „wie schärfe ich meine Meinung".

---

## 12. Auslieferung

### 12.1 Signatur und Ruf

⚠️ **Smart App Control blockiert unsignierte Dateien**, außer sie haben positive
Cloud-Reputation. **Bei unsignierten Dateien wird der Reputationszähler mit jedem Release
auf null zurückgesetzt** — wer oft veröffentlicht, ist dauerhaft im Nullzustand. Das ist
Systemlogik, kein Zufall.

SyncMangas v0.4.2-Entscheidung (PSF-signiertes Embeddable-Python statt selbstgebauter exe)
war genau richtig. Offen bleibt der Installer.

**Die Zertifikatslage (recherchiert 08/2026):**
- Ab **01.03.2026** sinkt die Höchstlaufzeit von 39 Monaten auf **460 Tage**.
  **Ein „für immer"-Zertifikat gibt es nicht.**
- 🔑 **Aber:** mit **Zeitstempel** signierter Code bleibt **dauerhaft** gültig, auch nachdem
  das Zertifikat abgelaufen ist — der Zeitstempel beweist „signiert, als das Zertifikat
  gültig war".

> **Folge für JBs Wunsch „einmal zahlen, ewig gültig":** erfüllbar **pro Fassung**, nicht
> für künftige. Ein Zertifikat kaufen, alles in seiner Laufzeit signieren und
> **zeitstempeln** — diese Dateien bleiben für immer vertrauenswürdig. Für neue Fassungen
> danach neu entscheiden.
> Reputation hängt am **Zertifikat**, nicht an der Datei — sie überlebt Releases.

**Kostenlos und wirksam daneben:** gleichbleibender Herausgebername · eigene Domain mit
HTTPS · veröffentlichte SHA-256 (vorhanden) · gepflegter Änderungsverlauf · offener
Quellcode · **kein Packer** (UPX ist Auslöser Nummer eins) · nicht in fremde Prozesse
greifen · keine ungefragten Adminrechte.

### 12.2 Installer

Häkchen für Fähigkeiten (schreiben nur Konfiguration, entfernen keinen Code) und getrennt
davon für **Fremdsoftware**: Python (mitgeliefert), VLC/mpv, ffmpeg, Deno.

⚠️ **winget verleiht kein Vertrauen.** Es prüft die SHA-256 gegen das Manifest — du bekommst
*die richtige Datei*, nicht eine *vertrauenswürdige*. Smart App Control prüft danach
trotzdem die Signatur. **Die Signatur ist der einzige Hebel.**
(Korrektur einer früheren Einschätzung, 06.08.2026.)
SyncManga hat den winget-Workflow (`schn4ppi.SyncManga`), **SyncYouTube hat gar keinen** —
daher die Blockade bei Testnutzern.

### 12.3 Neuerungen zeigen

Änderungen, die den Bestand betreffen (neue Stimmen-Modelle, neue Übersetzungsgüte), werden
**im Programm** kurz und knapp gezeigt — nicht nur in den GitHub-Notizen.
Eine Zeile, ein Beispiel zum Anhören, ein Knopf „übernehmen" oder „später".

### 12.4 Hülle und Spieler — F01 beantwortet

**Hülle:** eigenes Fenster (**pywebview**, `huelle.py` existiert bereits) mit der
Web-Oberfläche darin. Fühlt sich an wie ein Programm, ist innen weiter Web — also bleibt
das Entwicklungstempo mit `importlib.reload` + F5 erhalten.

**E25 — Spieler: libmpv als Motor, libVLC als zweite Umsetzung.**

| | libmpv | libVLC |
|---|---|---|
| **ASS/SSA-Untertitel** | **libass = Referenzumsetzung** — Stile, Karaoke, Schilder korrekt | belegte Probleme bei Positionierung/Farben/Effekten, Ruckler beim Untertitelwechsel |
| Bildausgabe | Skalierung, HDR-Tonemapping, Interpolation, eigene Shader (**Anime4K**) | solide, weniger Kontrolle |
| Einbettung | saubere C-API | einfacher zu verpacken |
| Wer baut darauf | IINA, Celluloid, MPC-QT | VLC selbst |
| **Wo VLC gewinnt** | — | DVD/Blu-ray-**Menüs**, DVB/TV-Karten, Streaming-Server, geht mit **kaputten Dateien** gnädiger um |

Für Anime ist es nicht knapp: Fansub-Untertitel sind gestylt und positioniert, VLC macht
sie kaputt. **Beide bleiben verfügbar** — Spieler ist eine Fähigkeit hinter einer
Schnittstelle (E11). ⚠️ **Kein eigenes VLC-Fenster mehr**: der Motor zeichnet ins eigene
Fenster, die Steuerleiste liegt darüber, der Fernsehmodus sieht aus wie ein Streamingdienst.

**E26 — Plattform-Offenheit.** Die Frage ist nicht „welches Framework", sondern:
**gibt es eine saubere Schnittstelle zwischen Logik und Oberfläche?**

> 🔑 **Alle Logik hinter einer HTTP-Schnittstelle.** Dann redet jede Hülle mit demselben
> Server — und jedes Framework bleibt für immer offen. Kostet jetzt nichts, ist später
> unbezahlbar.

| Hülle | Aufwand | Wann |
|---|---|---|
| Browser | 0 | sofort |
| **Eigenes Fenster** (pywebview) | fast 0, vorhanden | **gewählt** |
| PWA am Handy | 0 | sofort — aber iOS räumt Speicher ab, kein Hintergrund-Download |
| Hülle mit nativem Spieler (Tauri/Capacitor) | mittel | wenn Offline + Video am Handy ernst werden |
| Voll nativ (Kotlin Multiplatform, Flutter) | groß | nur bei Bedarf |

Stand 2026: Flutter ~46 % Anteil; **Kotlin Multiplatform wächst am schnellsten** (+120 %/Jahr)
und teilt *Logik*, nicht Oberfläche — passt zu unserem Schnitt; Tauri baut 10–20× kleinere
Binärdateien als Electron.

### 12.5 Export und Freigabe

> **E32: Export ist kein Feature, sondern ein Grundrecht.**

Standardformate, damit es woanders ankommt: Bibliothek als JSON/CSV · **MAL-XML**
(De-facto-Austausch für Anime/Manga-Listen) · OPML für Podcasts · M3U für Wiedergabelisten ·
die Dateien liegen ohnehin in Standardformaten.

**Freigeben:** SyncMangas **einzelne HTML-Datei** wird vom Hauptprodukt zum
**Freigabe-Format** befördert — eine nur lesbare Momentaufnahme, läuft überall, braucht
nichts. Für echten Zugriff: Gerätekopplung mit widerrufbarem Token (vorhanden).

---

## 13. Offene Fragen

| # | Frage | Blockiert |
|---|---|---|
| ~~F01~~ | ~~Oberflächentechnik~~ → **beantwortet, siehe §12.4** | — |
| F02 | Endgültiger **Name** | Alles Sichtbare |
| F03 | Umgang mit **Sprichwörtern** beim Übersetzen | §10.2 |
| F04 | Wie stark **Namens-Verwestlichung** — Voreinstellung an oder aus? | §10.2 |
| F05 | `data/sources.json` + `readers_pattern.json` aus dem öffentlichen Repo nehmen? | §9.2 |
| F06 | **Quellen-Späher**: halbautomatisch mit Vorschlagsliste, oder nur Meldung? | §7.3 |
| F07 | **Text-Korrektur** schlecht lektorierter Verlagstexte — wie weit darf die KI eingreifen? | §10.2 |
| F08 | **Eigene Werk-IDs** zusätzlich zu ASIN/ISBN/AniList — sinnvoll oder Ballast? | §4.4 |
| F09 | **LANoMAT**: Bibliotheken auf LAN-Partys einsehen und tauschen | später |
| F10 | **Remixe und Coverversionen** — eigenes Werk oder Ausgabe? | §4.2 |

---

## 14. Was das Vorhaben töten kann

1. ⚠️ **Zu viel verschmelzen** — Fortschritt wird bedeutungslos. Die Trennregel §4.2
   verhindert es.
2. ⚠️ **Den Beziehungsgraphen selbst bauen** — gibt es geschenkt bei AniList, MangaUpdates,
   TMDB, MusicBrainz.
3. ⚠️ **Perfektion vor Nutzen** — Visual-Novel-Verzweigungen sauber modellieren, bevor man
   ein Kapitel lesen kann.
4. ⚠️ **Metadaten unterschätzen.** Readarr — reifes Projekt, volles Team — ist 2025 genau
   daran gestorben. Nicht Theorie, sondern letztes Jahr.
5. ⚠️ **Die Oberfläche aufs Netz warten lassen.** SyncMangas Datei fühlt sich instantan an,
   weil sie es nicht tut.
6. ⚠️ **Nur auf einen Anwendungsfall bauen.** Ein Bauteil, das nur bei 1920 px funktioniert,
   ist Schuld auf Zins.

---

## 15. Änderungsverlauf

| Datum | Was |
|---|---|
| 2026-08-06 | Fassung 0.2 — E25–E33 ergänzt: Spieler-Motor (libmpv/libVLC), Plattform-Offenheit über HTTP-Schnittstelle, Ordnerkonventionen und Pfadhaltung, Umbenennungsregeln, Mängel-Deklaration, Titel-Zuordnung mit gewichteten Zeugen, Export als Grundrecht, Spiele über Playnite. **F01 beantwortet** (§12.4). Zwiebel um DJ-Sets, Sportevents, Spiele/Emulatoren, physische Sammlung erweitert. **Korrektur:** winget verleiht kein Vertrauen (§12.1). |
| 2026-08-06 | Fassung 0.1 — Startschuss. E01–E24 festgehalten, F01–F10 eröffnet. Grundlage: Brainstorming-Sitzung JB + Claude, mit Recherche zu Marktlage, Farbforschung, WCAG, *arr-Stand, TTS-Stand, Signaturlage, MangaDex-Verfügbarkeit, Cloudflare-Umgehung. |

---

## Anhang · Ein Klick, die ganze Kette

Zur Prüfung, ob das Gerüst trägt — ein einziger Klick bis ins Flugzeug:

| | |
|---|---|
| **Sek. 0** | Erweiterung liest Titel, Kapitelnummer, Scrollstand aus der Seite → meldet an den lokalen Server |
| **Sek. 1** | Register: bekannt? → sonst Auftrag **identifizieren** → MangaBaka/NovelUpdates/RanobeDB → eindeutig: Werk angelegt; uneindeutig: **„⚠ Braucht Hilfe"** |
| **Min. 1** | **anreichern** (Cover, Autor, Stand, Tags) · **Beziehungen** (Manga? Anime? → verknüpft, nicht importiert) · Startseiten-Zustand neu |
| **auf Wunsch** | **beschaffen** (Quellenwahl, Tempobremse) · **prüfen** (§9.4) · **einlagern** (EPUB + Metadaten) |
| **nachts** | **Glossar** · **übersetzen** · **Rollen** · **vertonen** — gestempelt |
| **morgens** | **verteilen** — Handy holt die nächsten 20 Kapitel als Text *und* Audio. Flugmodus. |
| **danach** | RSS meldet Kapitel 413 → **+1** · besseres Modell → nachts erneuert · **Glossar korrigiert → alle betroffenen Kapitel zurück in die Warteschlange** |
