# SyncFundus — Vision & Fundament

> **Arbeitstitel.** Der Nachfolger von SyncManga und SyncYouTube: **ein** Programm für
> Anime, Manga, Novels, Musik, Hörbücher, Filme und Serien — mit eigener Bibliothek,
> eigenem Leser, eigener Bühne, eigener Veredelung.
>
> **Stand:** 2026-08-07 · **Fassung:** 1.1 · **Pflege:** JB + Claude

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

## 1. Was SyncFundus ist

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
| Kavita | Manga **und** Light Novels, echter Textleser | kein Anime, keine Bühne |
| Komga | Comics, top API, OPDS v2, Kobo | keine Novels, kein Anime |
| Mihon / Aniyomi / LNReader | je eine App pro Medium | drei Apps, drei Bibliotheken |
| *arr-Familie | Beschaffung automatisieren | keine Bibliothek, keine Erkennung, **Readarr tot** |

**Drei Alleinstellungsmerkmale:**

1. 🔑 **Die Bibliothek entsteht aus dem eigenen Verhalten.** Alle anderen verlangen
   manuelles Eintragen oder vorhandene Dateien. Das gibt es kein zweites Mal.
2. 🔑 **Alle Medien unter einer Oberfläche, mit eigenem Leser *und* eigener Bühne.**
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
| E09 | Farben | Tinte (Nacht) · Papier (Tag) · Bühne **immer** schwarz | ✅ |
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
| E25 | Bühnen-Motor | **libmpv** Standard, **libVLC** zweite Umsetzung hinter derselben Schnittstelle | ✅ |
| E26 | Plattform-Offenheit | **Alle Logik hinter einer HTTP-Schnittstelle** — jede Hülle bleibt möglich | 🔑✅ |
| E27 | Ordnerstruktur | Etablierte Konventionen **übernehmen**, nie erfinden (§4.6) | ✅ |
| E28 | Pfade | **Wurzel-Kennung + relativer Pfad**, nie absolute Pfade als Identität | 🔑✅ |
| E29 | Umbenennen | Nur in eingeladenen Ordnern · immer Probelauf · immer rückgängig | ✅ |
| E30 | Mängel | **Deklarieren, nicht verschweigen und nicht blockieren**; Suche läuft weiter | ✅ |
| E31 | Titel-Zuordnung | Mehrere gewichtete Zeugen; **Popularität nur als Stichentscheid** | 🔑✅ |
| E32 | Export | **Grundrecht**, in Standardformaten; HTML-Datei wird Freigabe-Format | ✅ |
| E33 | Spiele | Playnite-Modell übernehmen, nicht nachbauen; **Spielzeit = Fortschritt** | ✅ |
| E34 | Fenster | 🔑 **Es gibt nie zwei Fenster.** Motor zeichnet in unsere Fläche | 🔑✅ |
| E35 | Bedienelemente | **Der Motor liefert Pixel, wir liefern alles andere** | 🔑✅ |
| E36 | Navigation | **Seitenleiste** führt · Kopfzeile global · Reiter nur im Werk · keine Menüzeile | ✅ |
| E37 | Sichtbarkeit | Vier Stufen; Stufe 1 = **max. 1 Haupthandlung** | ✅ |
| E38 | Tiefe | **3 Ebenen** (Regal→Werk→Einheit); alles andere ist eine **Tafel** | 🔑✅ |
| E39 | Ordnertiefe | **Der Container ersetzt den Ordner**; max. Medium/Werk/(Gruppe)/Datei | ✅ |
| E40 | Eigene Dateien | Regal **„Eigenes"** — nie umbenannt, nie verschoben | ✅ |
| E41 | Eingriffe | **Vorschlagen statt verändern** — übergriffig ist das Schweigen, nicht das Wissen | 🔑✅ |
| E42 | Qualitätsnetz | Layout-Wächter · Text-Wächter · Bildvergleich · Affe · Nutzungszähler | ✅ |
| E43 | Titel-Schema | **Rollen statt Zeichenkette**: Urheber · Titel · Kontext · Zeitpunkt | ✅ |
| E44 | Live | Live-TV **ja** (mit EPG), Live-Sport-Streams **nein** — ein Moment ist kein Werk | ✅ |
| E45 | Anforderungen | **Die Suche ist die Anforderung** — kein zweiter Modus | ✅ |
| E46 | Meilensteine | Erscheinen **einmal**, danach nur im Rückblick — nie als Startliste | ✅ |
| E47 | Blu-ray | Externes Werkzeug **einbinden** (`makemkvcon`), nie selbst entschlüsseln | ✅ |
| E48 | Erkennung | 🔑 **Genau ein Ausgang pro Datei** — keine Regelkaskade, kein Wiedereinstieg | 🔑✅ |
| E49 | Fehlerprotokoll | Lokal sammeln · verschlüsselt · **opt-in** hochladen · keine privaten Inhalte | ✅ |
| E50 | GPU-Nutzung | **Nachgebend**: bei Ruhe nehmen, bei Bedarf sofort freigeben | ✅ |
| E51 | Anmeldungen | Erneuern sich still; gefragt wird nur bei **echtem Entzug** | ✅ |
| E52 | Kern | **Deterministisch** — kein `random`, kein `now()` in der Logik | 🔑✅ |
| E53 | Suche | **Ein Feld, zwei Gruppen** (Regal / draußen) — keine Reiter | ✅ |
| E54 | Suche | Dritter Zustand **◐ gekannt, nicht im Regal** — sortiert über ○ | 🔑✅ |
| E55 | Filter | Dreistufig: neutral → **nur das** → **das nicht** | ✅ |
| E56 | Suche | **Ein Werk, eine Zeile** — zusammengeführt, aber nie über Mediengrenzen | ✅ |
| E57 | Zahlen | **Nichts erfinden**: unbekannte Gesamtzahl ist `?`, nie geschätzt | 🔑✅ |
| E58 | Leser | **Leserichtung ist Eigenschaft der Ausgabe** (↤ ↦ ↧), nicht Einstellung | 🔑✅ |
| E59 | Zeichen | **▶** für alles mit Laufzeit, **Lesezeichen-Pfeil** für alles Geblätterte | ✅ |
| E60 | Schrift | Inter · Literata · Atkinson · JetBrains Mono — Oberflächenschrift **nicht wählbar** | ✅ |
| E61 | Fortschritt | Balken nur bei bekanntem Nenner · **keine Restzeit beim Lesen** | ✅ |
| E62 | Farbe | **Zwei Skalen**: Übersetzungs-Lebendigkeit ≠ Serien-Zustand | ✅ |
| E63 | Güte | Wortabzeichen `MTL` `MTL+KI` `Fan` `Offiziell` — nie Emoji, nie Sterne | ✅ |
| E64 | Anzeige | Kapitelzelle `gelesen / übersetzt / gesamt` in festem `ch`-Raster | ✅ |
| E65 | Leser | **Ein Griff, zwei Gedächtnisse** — Zoom und Schriftgröße teilen nicht den Wert | ✅ |
| E66 | Startseite | **Kein Selbstlauf** — Held wechselt auf Zuruf, nicht auf Uhr (außer TV) | ✅ |
| E67 | Erweiterung | Spricht **nur** mit `127.0.0.1` · lädt nichts · max. 3 Eingriffe je Seite | 🔑✅ |
| E68 | Erweiterung | Adapterliste kommt **lokal**, nicht aus dem Store-Paket | ✅ |
| E69 | Archiv | Friedhof **mit Gedächtnis** — still, aber antwortet beim exakten Namen | ✅ |
| E70 | Startseite | **Neu für dich ≠ neu erschienen** — zwei Reihen, nie eine | ✅ |
| E71 | Bauen | **Prüfen vor dem Zeigen** — keine Oberflächendatei ungeprüft ausliefern | ✅ |
| E72 | Sprache | **„Spieler" ist verboten** — die Abspielfläche heißt **Bühne**; Spieler ist ein Mensch | ✅ |
| E73 | Zahlen | Drei Zahlen, alle echt: `gelesen / übersetzt / **erschienen**` — `…` nur bei echtem Nichtwissen | 🔑✅ |
| E74 | Leser | Im geführten Modus regelt der Griff die **Füllung**, nicht die Seitengröße | ✅ |
| E75 | Bühne | Untertitel: `srt`/`vtt` zeichnen **wir**, `ass` zeichnet der Motor | ✅ |
| E76 | Erweiterung | Fortschritt hängt am **Werk**, nicht an der Seite — Quellen sind austauschbar | 🔑✅ |
| E77 | Bühne | Gamepad-Belegung ist **fest** — Muskelgedächtnis schlägt Anpassbarkeit | ✅ |
| E78 | Suche | **Das kluge Regal** — eine gespeicherte Suche wird ein Regal, das sich selbst füllt | ✅ |
| E79 | Suche | Erweiterte Suche **zugeklappt**, aber mit Zähler — nie ein unsichtbarer scharfer Filter | ✅ |
| E80 | Bühne | **10 s tippen, halten spult** (4× → 12× → 30×) — spulen, nie schnell abspielen | ✅ |
| E81 | Bühne | Bedienung liegt **im Bild** und blendet weich weg: raus 420 ms, rein 120 ms | ✅ |
| E82 | Bühne | **Pausenkarte** nach 12 s, am Rand, mit Rollen — **nie** Empfehlungen | ✅ |
| E83 | Sprache | **„Ton & Text"** statt „Spuren" · Einstellen (Zahnrad) ≠ Auswählen | ✅ |
| E84 | Bühne | Folgen wohnen **unter** der Bühne, nicht in einer Tafel | ✅ |
| E85 | Anzeige | Zahlentrio: die Luft gehört dem **Trenner**, ausgerichtet mit Ziffernleerzeichen | ✅ |
| E86 | Titel | **Alle Sprachen gleichrangig** — Englisch ist nicht die Wahrheit, Romanisierung ist ein Titel unter vielen | 🔑✅ |
| E87 | Erkennung | **Nie früh verwerfen** — im Zweifel ins Postfach, nie wegfiltern | 🔑✅ |
| E88 | Regal | Jede Kachel trägt **ihren Namen** — kein reines Bilderraten | ✅ |
| E89 | Werk | Ein **Ausschnitt** ist eine Ausgabe, nie ein neues Werk | ✅ |
| E90 | Veredelung | **Karaoke = Mitlesen** — eine Technik, ein Name, überall dieselbe | ✅ |
| E91 | Bühne | **„Zur Quelle"** — zurück zur Herkunftsseite, an der aktuellen Stelle | ✅ |
| E92 | Bühne | **Mini-Bühne** unten als Leiste, wenn etwas nebenher läuft | ✅ |
| E93 | Suche | **Transkript-Suche** über Untertitel *und* Buchtext — gehört in die Suche | ✅ |
| E94 | Bühne | Folgen: am PC **Raster**, am Fernseher **Reihe** mit sichtbarer Staffelwand | ✅ |
| E95 | Leser | **Ein Ort für den Fortschritt** — dieselbe Leiste in jedem Modus | ✅ |
| E96 | Musik | **Das Lied ist das Werk**, die Aufnahme die Ausgabe, das Album eine Gruppe | 🔑✅ |
| E97 | Rahmen | **Eine Sache hat das Bild, eine den Ton** — und sie dürfen verschieden sein | 🔑✅ |
| E98 | Rahmen | Die **Klangleiste** ist immer die Antwort auf „wo kommt der Ton her" | 🔑✅ |
| E99 | Rahmen | **Genau ein** schwebendes Bildfenster · nie über Leser oder Musikfläche | ✅ |
| E100 | Rahmen | **Genau eine Tafel** gleichzeitig · nichts darunter verrutscht · Esc schließt | ✅ |
| E101 | Rahmen | Fläche, Leser und Bühne belegen **denselben Bereich** — nie ein zweites Fenster | 🔑✅ |
| E102 | Übernahme | Der **Code-Übernahme-Pfad** steht im Dokument: was aus SyncYouTube kommt, kommt dokumentiert | ✅ |
| E103 | Oberfläche | **Nichts springt beim Wechseln** — wechselnde Beschriftungen bekommen feste Breiten | 🔑✅ |
| E104 | Oberfläche | **Einstellen ≠ Wählen** — Aussehen und Auswahl liegen nie im selben Menü | ✅ |
| E105 | Oberfläche | **Klick daneben schließt** jede Tafel, jedes Menü, überall | ✅ |
| E106 | Bühne | Bei **Ton ohne Bild** blendet nichts aus — Ausblenden ist etwas für Bilder | ✅ |
| E107 | Bühne | **Klangzeichen** (Klick) beim Bedienen auf Distanz — leise, kurz, abschaltbar | ✅ |
| E108 | Hörbuch | Hörbücher haben **Kapitel, keine Lieder** — nie im Musikregal | 🔑✅ |
| E109 | Qualität | **Herkunft und Güte sind Information, kein Menü** — wie 1080p neben 4K | ✅ |
| E110 | Empfehlung | Das Programm fragt **nie**, ob du etwas aufgibst — du filterst selbst | 🔑✅ |
| E111 | Profile | Profilwechsel wie bei Netflix: **im Menü, nie beim Start**, nie in der Bibliothek | ✅ |
| E112 | Zeichen | **Farbe ist die Beschriftung** — grau aus, Akzent an; nie Zustand als Text | 🔑✅ |
| E113 | Zeichen | **Eigener Satz** im Gleichdick — Formen frei, Zeichnung unsere, nichts kopiert | ✅ |
| E114 | Farbe | **Der Grund folgt dem Material** — eigene Farbe darauf ⇒ neutral, nur Schrift ⇒ warm | 🔑✅ |
| E115 | Bühne | **Kanonische Weiche** am Folgenende statt blindem Autostart | ✅ |
| E116 | Bühne | **Nur-Ton** für Musikvideos — Bild aus, Ton läuft | ✅ |
| E117 | Hörbuch | **Wo war ich?** — Rücksprung und Zusammenfassung, wenn man eingeschlafen ist | 🔑✅ |

### Die Unverhandelbaren

**Zehn Regeln der Bauart** — wer eine bricht, bricht das Programm:

**E02** Kern kennt keine Medien · **E03** Fortschritt trennt Werke · **E11** kein fremdes
Datenmodell im Kern · **E12** Quellenkatalog nur zur Laufzeit · **E16** niemals Zugangsdaten ·
**E20** Fingerabdruck vor Dateiname · **E26** alles hinter einer HTTP-Schnittstelle ·
**E34** nie zwei Fenster · **E48** genau ein Ausgang pro Datei · **E52** deterministischer Kern

**Sechs Regeln des Vertrauens** — wer eine bricht, verliert den Nutzer, nicht den Code:

**E54** der Zustand *gekannt, nicht im Regal* ist unser Alleinstellungsmerkmal — er darf nie
wegoptimiert werden · **E57** nie eine Zahl erfinden; Unbekanntes ist `…` ·
**E58** Leserichtung gehört zur Ausgabe, nicht zur Einstellung ·
**E67** die Erweiterung spricht nur mit dem eigenen Rechner ·
**E73** die drei Zahlen bedeuten drei verschiedene Dinge und werden nie vermischt ·
**E76** Fortschritt hängt am Werk, nie an der Quelle ·
**E86** alle Sprachen eines Titels sind gleichrangig ·
**E87** nie früh verwerfen — im Zweifel ins Postfach

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

#### E108 — Hörbücher sind keine Musik

**JB, 07.08.2026:** *„Will die halt nicht in der Bibliothek der Musik finden, das ist relevant."*

Ein Hörbuch mit 340 Spuren würde jedes Musikregal fluten. Deshalb:

| | Musik | Hörbuch |
|---|---|---|
| Werk | das **Lied** (E96) | das **Buch** |
| Einheit | — | das **Kapitel** (nummeriert, benannt) |
| Sammlung | Album = Gruppe | Reihe/Band |
| Fortschritt | gehört / nicht gehört | **Zeitstand im Kapitel**, wie bei Video |
| Regal | Musik | **Hörbuch** — eigenes Regal, eigene Zwiebelschicht |
| Zufall, Radio, Mixer | ja | **nein** — ein Buch wird nicht gemischt |
| Einschlafzeit | selten | **immer sichtbar** |

Die Trennung passiert bei der Erkennung, nicht beim Anzeigen: eine Datei mit
`ASIN`/`Audible`-Kennung, mit Kapitelmarken über 10 Minuten oder mit einer M4B-Hülle ist ein
Hörbuch — und wandert nie ins Musikregal, auch nicht versehentlich.
Die **Spurnummer bleibt** (Kapitel 7 von 24), weil man sie zum Springen braucht.

#### E117 — Hörbuch: „Wo war ich?"

**JB, 07.08.2026:** *„Merken, wo man war, ist immens wichtig. Eventuell eine Zusammenfassung,
wenn man eingeschlafen ist?"* — Beides, und das zweite ist etwas, das kein Hörbuchprogramm hat.

| | |
|---|---|
| **Stand merken** | sekundengenau, **je Werk**, und beim Rückkommen automatisch **30 s zurück** — man erinnert sich nie an den letzten Satz, sondern an den davor. Audible macht das, und es ist die beste Kleinigkeit an dieser App |
| **Eingeschlafen erkannt** | Einschlafzeit lief ab **oder** über 20 Minuten kein Eingriff bei laufender Wiedergabe ⇒ die Stelle wird gesondert gemerkt (*„vermutlich eingeschlafen bei 1:12:40"*) |
| **Zusammenfassung** | beim nächsten Start: *„Du warst zuletzt bei Kapitel 7, Minute 12 — seitdem lief es bis 1:12:40 weiter. Kurz, was passiert ist: …"* Drei bis fünf Sätze, erzeugt aus dem **Werk-Wissen** (§10.1), das wir für Übersetzung und Vertonung ohnehin bauen |
| ⚠️ **Spoilerregel** | die Zusammenfassung endet **exakt** an der Stelle, bis zu der es gelaufen ist. Nie einen Satz weiter |
| **Zwei Knöpfe** | *„Da weitermachen"* oder *„Zurück zu Minute 12"*. Nie automatisch entscheiden |

#### E109 — Herkunft und Güte sind Information, kein Menü

**JB, 07.08.2026:** *„Gekauft oder Scan, für mich identisch, nur die Qualität ist relevant.
Nicht als Menü, sondern als Info — wie ein Film, der in 1080p oder 4K verfügbar ist."*

Damit ist auch die halbe Sammlung geklärt: Band 1–8 gekauft, 9–14 als Scan ist **ein Werk**
mit Ausgaben unterschiedlicher Güte. Kein „unvollständig", kein zweiter Eintrag.

| So nicht | So |
|---|---|
| Auswahlmenü „Quelle wählen" bei jedem Öffnen | eine **Zeile Information** am Werk: `Kap. 1–214 · Fan DE · Kap. 1–8 zusätzlich Verlag` |
| „Scan" als Makel | Güte wie eine Auflösung: `Verlag` · `Scan 1200 dpi` · `Fan` · `MTL+KI` |
| stiller Austausch | **Angebot**, wenn etwas Besseres auftaucht: *„Band 9 gibt es jetzt vom Verlag — holen?"* (E41) |
| alte Fassung löschen | bleibt liegen, bis du sie wegwirfst |

#### E96 — Musik im vorhandenen Modell (F10 beantwortet)

**JB, 07.08.2026: „Das Lied ist das Werk, dann kommt das Album."** Damit ist F10 geschlossen —
und das Schöne daran: es braucht **keinen neuen Begriff**. MusicBrainz' drei Ebenen fallen genau
auf unsere vorhandenen:

| MusicBrainz | bei uns | Beispiel |
|---|---|---|
| **Work** (die Komposition) | **Werk** | *Sakura, Sakura* |
| **Recording** (eine Aufnahme davon) | **Ausgabe** | Studiofassung 2016 · Live in Tokio 2019 · Ushio-Remix · Remaster 2023 |
| **Release** (Album/Single) | **Gruppe** (dritte Sprosse der Leiter) | *A Silent Voice OST* |

Damit lösen sich die Fälle, an denen jede Musikbibliothek scheitert, von selbst:

- **Coverversion** — anderes Werk, aber über eine **Beziehung** („Neuaufnahme von") verbunden.
  Der Fortschritt zählt getrennt, also sind es zwei Werke (**E03**).
- **Remix** — dieselbe Aufnahme, andere Fassung ⇒ **Ausgabe** desselben Werks.
- **Live-Fassung** — Ausgabe.
- **Derselbe Song auf drei Alben** — ein Werk, eine Aufnahme, drei Gruppen. Nicht dreimal im Regal.
- **DJ-Set** — ein eigenes Werk mit Laufzeit; die Tracklist ist eine **Beziehungsliste**
  auf die enthaltenen Werke, mit Zeitmarke. Deshalb springen die Kapitelstriche der Bühne
  dort von Titel zu Titel (§5.12).

Und weil das Album eine Gruppe ist, gilt automatisch die Regel aus §4.3: **die Gruppe zählt
keinen eigenen Fortschritt.** „Album zu 60 % gehört" gibt es nicht — gehört werden Lieder.

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

**Drei Fehlerarten, strikt getrennt** — das ist die ganze Kur gegen still verrottende
Warteschlangen:

| Art | Beispiel | Reaktion |
|---|---|---|
| **Vorübergehend** | Netz weg, 503, Zeitüberschreitung | wiederholen mit wachsendem Abstand |
| **Dauerhaft** | 404, Format kaputt, Quelle tot | **nicht** wiederholen — Quelle abwerten, andere nehmen |
| ⚠️ **Unser Fehler** | Ausnahme im eigenen Code | 🔑 **niemals wiederholen** — sofort anhalten, einfrieren, melden |

> ⚠️ **Eine Warteschlange, die einen Programmfehler wiederholt, dreht sich für immer.**
> Deshalb ist die dritte Zeile keine Feinheit, sondern die wichtigste Regel der Warteschlange.

**Vergiftete Aufträge:** nach N Fehlschlägen fliegt ein Auftrag aus der Hauptschlange in eine
**sichtbare** Liste „Steckengeblieben". Nie still, nie ewig.

**Was Selbstheilung kann:** Quelle wechseln · Format wechseln · Auflösung senken · später
erneut · ein als kaputt erkanntes Muster markieren und dessen Ergebnisse zurückrollen.
**Was sie nicht kann:** den eigenen Codefehler beheben. Da hilft nur melden.

**E50 — Zeitfenster und Speicher, nachgebend:** die Warteschlange nimmt sich GPU-Speicher,
wenn das System ruhig ist, und **gibt ihn sofort frei**, wenn ein anderer Dienst ihn braucht.
Ein laufender Auftrag wird dabei sauber angehalten und später fortgesetzt, nicht abgebrochen.
Nachtfenster sind einstellbar, nicht fest verdrahtet.

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
(medienübergreifend) → **Neu erschienen** → **Neu für dich** → **Regale nach Medium**
(nach Nutzung sortiert) → **Entdecken**.

Belege: Auswahl-Überlastung (Schwartz) — zu viele gleichrangige Optionen erzeugen Zögern
und Abbruch; Amazon zeigt bewusst 4–7. Unterbrochenes hat mehr Sog als Neues.

**E110 — das Programm fragt nie, ob du etwas aufgibst.** JB, 07.08.2026: *„nein niemals."*
Eine Serie liegt seit 14 Monaten bei Kapitel 30 — das ist **deine** Sache. Was es stattdessen
gibt, ist ein **Filter, den du selbst setzt**: *zeig mir nur, wo ich über 2 / 5 / 10 Kapitel
gelesen habe*. Damit räumst du deine Startseite auf, ohne dass dich jemand fragt, ob du
aufgibst. Gilt genauso für Serien (*über 2 Folgen gesehen*).

> Der Unterschied ist die Richtung: **du entscheidest, was du sehen willst.**
> Das Programm entscheidet nie, was du fallen lassen sollst.

**E111 — Profilwechsel wie bei Netflix.** Nicht beim Start (niemand will vor dem Lesen erst
ein Konto wählen), nicht in der Bibliothek — sondern **im Menü**, oben rechts, mit den Gesichtern.
Gestartet wird immer im zuletzt benutzten Profil.

**E70 — „Neu für dich" ist nicht „neu erschienen".** Zwei verschiedene Reihen, nie eine:
*neu erschienen* ist ein Nachschub-Regal für Dinge, die du schon verfolgst (Kapitel 413 ist
da); *neu für dich* ist ein Vorschlag für etwas Fremdes. In eine Reihe geworfen wird beides
wertlos — man weiß nicht mehr, ob ein Klick Fortsetzung oder Risiko bedeutet.

**E66 — vier Helden, aber kein Selbstlauf.** Oben kann man zwischen wenigen Titeln wechseln
(Amazon-Prime-Prinzip), **aber nicht auf Uhr.** Automatisch weiterlaufende Karussells sind
seit Jahren als schädlich belegt: die Notre-Dame-Auswertung fand ~1 % Klicks auf das
gesamte Element, davon 84 % auf das erste Bild; NN/g nennt Selbstlauf ausdrücklich als
Ärgernis, weil man das Gelesene verliert, bevor man es zu Ende gelesen hat.
Also: **der Mensch wechselt**, die Auswahl der vier wird **einmal am Tag** neu bestimmt
(deterministisch aus dem Datum — E52). **Ausnahme Fernsehmodus:** dort sitzt man weit weg,
ohne Zeiger, und Bewegung ist der Zweck — dort läuft der Held weiter, mit Stopp beim
ersten Tastendruck.

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
| Bühne | `#0A0A0B` | Bühne `#0A0A0B` | **fest** |
| Akzent | `#F0873C` | `#B4551A` | gleicher Ton, andere Helligkeit |

**Begründungen:**
- Die **Bühne** schaltet nie: ein heller Rahmen um einen Film ist auch mittags falsch.
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

### 5.3.1 Der Grund folgt dem Material (E114)

**JB-Frage 07.08.2026:** *„Warum ist der Hintergrund beim Leser dieses Braun? Passt das zum Rest?"*
— Teilweise. Ich hatte eine **Stimmung** gewählt, wo eine **Regel** hingehört:

> **Liegt eigene Farbe darauf → neutral. Liegt nur Schrift darauf → warm.**

| Fläche | Wert | Temperatur | Weil |
|---|---|---|---|
| Programm | `#0E1217` | kühl | Möbel treten zurück; kühl wirkt neutral neben jedem Cover |
| Bühne | `#0A0A0B` | neutral | jeder Farbstich wäre eine Lüge — Referenzmonitore im Film sind neutral kalibriert |
| **Leser · Bilder** | `#0F1012` ⚠️ **geändert** | neutral | war `#1C1611`. Braun ließ gescannte Graustufen **vergilbt** aussehen, weil das Auge den Rand mitrechnet |
| Leser · Text (Tag) | `#F6EFE3` | **warm** | Papier ist warm, und es gibt keine fremde Farbe zu verfälschen |
| Leser · Text (Nacht) | `#1C1611` | **warm** | bleibt — das ist die Nachtfassung des **Papiers**, nicht die des Programms |
| Musik | aus dem Cover | wechselnd | die einzige Fläche, die sich ändert: zwei Hauptfarben des Covers, stark abgedunkelt |

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

### 5.5 Navigation (E36–E38)

**Seitenleiste führt.** Belegt: unter 5 Punkten gewinnt die Kopfzeile, ab 5–10 die Seitenleiste —
das Auge fixiert im **F-Muster** ohnehin oben und links und erfasst in einem Blick mehr
senkrechte Einträge. Wir haben über zehn Regale. Sie bietet zudem Platz für Hierarchie,
aktive Zustände und Zähler.

**Kopfzeile nur global** (Suche, Einstellungen, Profil) — nie Navigation. Reife Programme
nutzen genau diese Teilung. Die Suche ist zugleich das **Anforderungsfeld** (E45).

⚠️ **Keine Menüzeile** (`Datei · Bearbeiten · Ansicht`) — ein Relikt, das alles hinter zwei
Klicks versteckt. **Reiter nur innerhalb eines Werks** (Übersicht · Einheiten · Beziehungen ·
Dateien · Wissen), weil Reiter „das gehört zusammen" signalisieren.

**E37 — Vier Sichtbarkeits-Stufen:**

| Stufe | Wo | Grenze |
|---|---|---|
| 1 · Fläche | direkt sichtbar | **max. 1 Haupthandlung** + 5 Navigationspunkte |
| 2 · Kontext | bei Auswahl | max. 4 |
| 3 · Auf Zuruf | ⋯ / Rechtsklick | unbegrenzt |
| 4 · Werkstatt | Einstellungen | unbegrenzt |

> **Prüfstein: wenn du erklären musst, was ein Knopf tut, gehört er nicht auf die Fläche.**
> Kein Knopf ohne Wort — Symbol allein ist ein Ratespiel.

**E38 — Tiefenregel: drei Ebenen.** Regal → Werk → Einheit. Alles andere ist eine **Tafel**.

> 🔑 **Der Unterschied zwischen Ebene und Tafel ist der Griff gegen das
> „ich muss einen neuen Tab aufmachen"-Gefühl.** Eine Ebene *ersetzt*, wo du bist.
> Eine Tafel legt sich *darüber* und gibt dich zurück, wo du warst.

Warteschlange, Werkstatt, Postfach und Werk-Wissen sind **immer Tafeln** — man verliert nie
seinen Platz, um etwas nachzusehen.

**Fernseher:** Seitenleiste wird Symbolstreifen, Kopf- und Befehlsleiste verschwinden.
**Handheld:** Vorbild ist **nicht Big Picture** (JB 06.08.: „war immer shit"), sondern die
**Steam-Deck-Oberfläche und EmulationStation** — eine Achse wechselt die Sammlung, eine
blättert, A startet. ⚠️ **Fokus muss immer sichtbar sein** (kräftiger Rahmen, nicht nur
Farbwechsel) — der häufigste Fehler in Fernsehoberflächen.

### 5.6 Nachvollziehbarkeit — nichts entscheidet stumm

Drei Grundsätze gegen verzerrte Prioritäten:

1. **Nichts wird verworfen, nur einsortiert** (E48) — es gibt keinen Mülleimer für Unerkanntes.
2. **Jede Entscheidung hinterlässt eine Spur.** Zu jedem Eintrag gibt es „Warum ist das hier?"
   — welche Quelle, welcher Punktestand, welche Alternativen. Fällt aus dem Register heraus,
   weil dort ohnehin Quelle und Datum gestempelt sind (§4.4).
3. 🔑 **Keine Regel darf stumm greifen.** Jeder Endzustand wird gezählt und angezeigt.
   Ein Zähler „342 Dateien liegen im Postfach, davon 210 wegen Regel R7" ist der Unterschied
   zwischen einem System, dem man traut, und einem, das leise lügt.

**E46 — Meilensteine erscheinen einmal.** Beim Erreichen eine kurze Einblendung, danach nur
noch im **Jahresrückblick**. Nie eine Liste beim Start, nie ein Abzeichen-Regal.
⚠️ Und: **keine Serien/Streaks** — die bestrafen Urlaub.

**Debuggen** folgt daraus: jeder Auftrag schreibt, *was* er entschieden hat und *warum* —
eine Entscheidungsspur pro Werk, kein Protokollmüll. Jeder Auftrag ist **wiederholbar** mit
derselben Eingabe (möglich nur wegen E52). Jede Kette hat einen **Trockenlauf**.

### 5.7 Flüssigkeit

1. **Vorgerechneter Startseiten-Zustand** — die Startseite fragt nie die Bibliothek
2. **Skelett in Endmaßen** — nichts springt; das Ärgernis ist Springen, nicht Spätsein
3. **Winzige Unschärfe-Vorschau** im Zustand (wenige hundert Byte je Cover)
4. **Nur Sichtbares zeichnen** — 3000 Lieder, 20 Elemente im Dokument
5. **Nie beim Start arbeiten** — Scans und Prüfungen in die Warteschlange
6. 🔑 **Die Oberfläche wartet nie aufs Netz.** Lokal zuerst, das Netz aktualisiert nur den
   lokalen Stand. ⚠️ SyncMangas HTML-Datei fühlt sich instantan an, *weil* sie das tut —
   diese Eigenschaft darf beim Umstieg auf einen Server nicht verlorengehen.

### 5.8 Die Suche (E53–E57)

> **Ein Feld. Zwei Gruppen. Drei Zustände.**
> Entwurf: `suche.html` (07.08.2026)

**Warum keine zwei Reiter (E53):** ein Reiter zwingt zur Entscheidung *„Regal oder draußen?"*,
bevor das Ergebnis bekannt ist — genau die Frage, wegen der man sucht. Zwei Gruppen
untereinander beantworten sie, statt sie zu stellen. Die Regalgruppe steht **immer oben**.

| Zeichen | Zustand | Herkunft | Aktion |
|---|---|---|---|
| **●** grün | im Regal | eigene Datenbank | *Weiterlesen* / *Weitersehen* — nie „Öffnen" |
| **◐** gelb | **gekannt, nicht im Regal** | Browserverlauf + Erweiterung, lokal | *Ins Regal & ab Kapitel N holen* |
| **○** grau | neu für dich | MangaBaka, AniList, TMDB, … | *Ins Regal* |

**E54 — der mittlere Zustand ist das Alleinstellungsmerkmal.** Kein Konkurrenzprodukt kennt
ihn: „63 Kapitel auf asuracomic.net gelesen, seit Februar nicht mehr, steht nirgends".
Er lebt in der Gruppe *Draußen gefunden* (die zwei Gruppen bleiben zwei), sortiert aber
**immer über ○** — eine halbe Erinnerung ist mehr wert als ein fremder Titel.

**E55 — Filter dreistufig.** Ein Klick auf ein Medium heißt *nur das*, zwei Klicks heißen
*das nicht*, drei sind wieder neutral. Kein Aufklappmenü, keine Kästchen. Dazu zwei
gestrichelte Schalter: *Auch Archiv*, *Auch 18+*.

**E56 — Zusammenführen.** Drei Kataloge, ein Werk, **eine Zeile**; die Herkunft erscheint nur
als Kürzel, mit einem Aufklapper, der zeigt, was verborgen wurde.

| zusammengeführt wenn | Prüfung |
|---|---|
| gleiche fremde ID | AniList/MAL/TMDB/ISBN/MangaUpdates — sofort sicher |
| Titel + Urheber | normalisierter Titel **und** mindestens ein gleicher Urheber |
| Nebentitel trifft | Synonymliste der Kataloge wird mitdurchsucht (*Only I Level Up* → *Solo Leveling*) |
| Jahr ± 1 | nur als Zusatzbedingung, nie allein |
| ⚠️ **nie über Mediengrenzen** | Manhwa, Anime und Novel sind drei Werke — **E03** gilt auch in der Suche |

**Die Entnerv-Regeln** (sieben, still im Hintergrund):

1. **E57 — nichts erfinden.** Unbekannte Gesamtzahl ist **`?`**, niemals die Nummer des
   letzten bekannten Kapitels. `?` heißt: die Serie läuft, niemand weiß das Ende.
2. Ein Werk, eine Zeile.
3. Was im Regal steht, kommt nicht als Neuvorschlag — nie doppelt.
4. **Archiv bleibt still** (E69) — es antwortet nur beim exakten Namen oder auf Zuruf.
   Ein Friedhof, aber einer mit Gedächtnis.
5. Erwachsenes bleibt aus, bis es einmal eingeschaltet wurde. Danach nie wieder fragen.
6. **Keine leeren Kataloge.** Eine Quelle ohne Treffer wird nicht erwähnt — kein Reiter,
   keine Zeile, keine Fehlermeldung.
7. Tippfehler kosten nichts (Levenshtein ≤ 2 ab vier Zeichen) — aber **nur**, wenn die
   exakte Suche leer bleibt, sonst verwässert es die guten Treffer.

**E79 — die erweiterte Suche.** Die Leiste oben beantwortet die häufige Frage; alles Genauere
liegt eine Etage tiefer und bleibt **zugeklappt**, aber mit einer **Zahl am Knopf**. Der
häufigste Fehler erweiterter Suchen ist der unsichtbare scharfe Filter — man sucht, bekommt
nichts und versteht nicht warum.

| Feld | Bauart |
|---|---|
| Umfang (Kapitel/Folgen), Jahr | **zwei Felder, beide dürfen leer sein.** Kein Aufklappmenü mit „100–200, 200–500, 500+" — das ist immer falsch geschnitten |
| Genre, Herkunft, Serienzustand | dieselbe **Dreistufigkeit** wie oben (E55): einmal *nur das*, zweimal *das nicht*. Eine Geste, überall |
| Der Satz darunter | *„Gesucht wird: Umfang 100–∞ · Korea · nicht Isekai"* — kein Ratespiel, welche Knöpfe gedrückt sind (§5.6) |

**E78 — das kluge Regal.** Eine Suche, die man dreimal tippt, ist ein Regal.
*„Koreanische Manhwa, abgeschlossen, über 100 Kapitel, kein Isekai"* wird per Knopf zu einem
Regal auf der Startseite und füllt sich von selbst — die Bedingung wird gespeichert, nicht die
Trefferliste. Das ist die Brücke zwischen Suche und Startseite und kostet uns keine neue Technik.

### 5.8.1 Titel sind vielsprachig — und das ist keine Kleinigkeit

**E86 — es gibt keinen „richtigen" Titel.** Ein Werk hat einen japanischen, einen
romanisierten, einen englischen, oft einen deutschen und manchmal fünf Fan-Titel. Englisch ist
**kein** Vorzugstitel, sondern einer von vielen — und oft der schlechteste, weil er von einer
Aggregatorseite schlecht übersetzt wurde.

| Art | Beispiel | Rolle |
|---|---|---|
| Original (Landessprache) | 進撃の巨人 · 나 혼자만 레벨업 | **die Wahrheit.** Wird immer gespeichert, auch wenn niemand sie liest |
| Romanisierung | Shingeki no Kyojin · Na Honjaman Level Up | Suchhilfe. Mehrere Systeme (Hepburn, Kunrei, RR, McCune-Reischauer) — **alle** speichern |
| Offiziell fremdsprachig | Attack on Titan · Solo Leveling | meist die Anzeige, aber nur, weil sie geläufig ist |
| Deutsch | Attack on Titan · *(oft gleich)* | Anzeige, wenn vorhanden |
| Fan / Aggregator | *„Advancing Giants"*, *„I Level Up Alone"* | ⚠️ **nur zum Finden, nie zum Anzeigen** |

**Regeln daraus:**
1. Gesucht wird in **allen** Titeln, angezeigt wird der aus deiner Anzeigesprache — mit Rückfall
   auf offiziell fremdsprachig, dann Romanisierung, dann Original.
2. Romanisierungen werden **normalisiert** verglichen: Längungsstriche weg (`Tōkyō` = `Toukyou`
   = `Tokyo`), Bindestriche und Leerzeichen egal.
3. Ein neuer Titel von einer Seite wird **hinzugefügt**, nie ersetzt. Der Titelvorrat wächst nur.
4. ⚠️ **Keine Sprache wird zur Wahrheit erklärt.** Wer Englisch als Leitwährung nimmt, verliert
   jedes Werk, das nie eine englische Lizenz hatte — und das sind gerade die interessanten.

**E87 — nie früh verwerfen.** Die gefährlichste Falle liegt nicht im Nicht-Finden, sondern im
**voreiligen Aussortieren**. Ein Werk mit falsch geschriebenem Titel, mit einer Kapitelzahl, die
nicht passt, mit einem Genre, das die Quelle falsch getaggt hat — all das darf **nie** stumm
herausfallen.

| statt | machen wir |
|---|---|
| unklaren Treffer verwerfen | ins **Postfach** legen, mit dem Grund |
| „passt nicht zum Muster" | Muster merken, Fund **markieren**, weiterlaufen |
| Doppelte automatisch löschen | zusammenführen — und die zweite Fassung behalten, bis jemand widerspricht |
| Alte/ruhende Werke ausblenden | leiser stellen (Archiv, E69), nie entfernen |

> Ein verlorenes Werk merkt niemand. Ein falsch einsortiertes sieht man sofort und kann es
> richten. Deshalb ist **Falsch-Behalten immer besser als Richtig-Wegwerfen.**

### 5.9 Der Leser (E58, E61, E65)

**E58 — die Leserichtung hängt am Werk, nicht am Leser.** Wer eine japanische Seite von links
nach rechts blättert, liest den Dialog rückwärts. Deshalb ist die Richtung eine **Eigenschaft
der Ausgabe**, reist mit ihr mit und steht in jeder Trefferzeile.

Sie hat **zwei Achsen**, nicht eine — das ist der Punkt, an dem die meisten Leser scheitern:

| | **Fluss** — wie geht es weiter? | **Achse** — was steht nebeneinander zuerst? |
|---|---|---|
| | blättern waagerecht · scrollen senkrecht | links→rechts · rechts→links |

| Zeichen | Fluss + Achse | Standard bei |
|---|---|---|
| **↤** | blättern, **rechts → links** | japanische Manga (JP), Lizenzausgaben, die das Original spiegeln |
| **↦** | blättern, **links → rechts** | westliche Comics, OEL-Manga, gespiegelte Altlizenzen, gebundene Manhua-Ausgaben, alle Text-Novels |
| **↧** | scrollen, Achse **links → rechts** | koreanische Manhwa/Webtoons (KR), Kuaikan-Manhua |

**Warum die Achse auch bei ↧ gebraucht wird:** ein Webtoon ist meist eine Spalte, aber nicht
immer — wo zwei Rahmen oder zwei Sprechblasen nebeneinanderstehen, muss die Reihenfolge
feststehen. **Koreanisch und modernes Chinesisch werden waagerecht links→rechts geschrieben**,
also ist ↧ praktisch immer LTR. Der Sonderfall ist **Chinesisch**: dieselbe Serie erscheint
als Webtoon (↧ LTR) *und* als gebundener Band aus Taiwan oder Hongkong, der der
japanischen Konvention folgt (**↤**). Deshalb ist die Richtung eine Eigenschaft der
**Ausgabe**, nicht des Werks und schon gar nicht der Sprache.

**Bestimmt in dieser Reihenfolge:** (1) steht sie in der Datei? `ComicInfo.xml
Manga=YesAndRightToLeft`, EPUB `page-progression-direction` → nehmen. (2) sagt der Katalog ein
Format? AniList `MANHWA` → ↧, `MANGA` + Land JP → ↤ → nehmen. (3) sonst **messen**: Bilder im
Schnitt dreimal höher als breit ⇒ Streifen. (4) Handkorrektur schlägt alles und gilt fürs
**ganze Werk**, nicht fürs Kapitel.
Mit der Richtung drehen sich **Pfeiltasten, Wischgeste, Fortschrittsbalken und
Doppelseiten-Paarung** — nie halb.

**E65 — ein Griff, zwei Gedächtnisse.** Bildzoom und Schriftgröße teilen den Regler, aber
**nicht den Wert**. Wer die Seite auf −40 % stellt, will nicht plötzlich 12-px-Text lesen.
⚠️ JB-Fund 07.08.2026 — war ein echter Fehler im Entwurf.

**E61 — Fortschritt.** Ein Balken braucht einen bekannten Nenner; fehlt er, steht dort eine
Zahl **ohne Balken**. Und: **keine geschätzte Restzeit beim Lesen.** Das setzt künstlich unter
Druck und spoilert die Kapitellänge (JB, 07.08.2026). Bei allem mit Laufzeit — Anime, Film,
Musik, Hörbuch — ist die Restzeit dagegen richtig, weil sie dort tatsächlich feststeht.

### 5.10 Schrift und Zeichen (E59, E60, E62–E64)

**E112 — die Farbe ist die Beschriftung.** Ein Knopf, der seinen Zustand als **Farbe** trägt,
ändert seine Größe nie — und damit springt nichts (E103). Wer den Zustand als Text schreibt
(*„Zufall: an"*), verliert beides. Grau = aus, **Akzent** = an. Bei drei Stufen (Wiederholen)
kommt eine kleine **1** in die Ecke, keine zweite Zeichnung.

⚠️ **Nicht Grün.** Grün ist im ganzen Programm reserviert für *läuft / aktiv / gelesen*
(Zustandsampel, Kapitelstreifen, Tonpuls). Hieße es zusätzlich „Schalter an", hätte es zwei
Bedeutungen. **Orange heißt überall: hier hat jemand etwas eingestellt.**
Für Farbenblinde gibt es immer einen zweiten Kanal: ein Punkt unter dem Zeichen, oder
Umriss ↔ Fläche (Herz, Lesezeichen).

**E113 — eigener Zeichensatz.** *„Können wir die von Spotify übernehmen? Einfach copy."* —
**Nein, und wir wollen es auch nicht.** Spotifys Satz ist Teil ihrer Marke und geschützt; ein
Programm, das aussieht wie ein anderes, hat kein Gesicht. **Frei ist die Form**: Play, Pause,
Zufall, Wiederholen sind seit den Kassettendecks dieselben Zeichen (IEC 60417), die gehören
niemandem. Also dieselben Formen, unsere Strichführung:

| Regel | Wert |
|---|---|
| Raster | 24 × 24 mit 2 px Luft |
| Strich | **1,5 · Gleichdick** — kein Strich dicker als ein anderer, nirgends |
| Enden, Ecken | rund |
| Gefüllt | **nur** Wiedergabe, Pause, vor/zurück, aktives Herz — weil man sie auf drei Metern erkennen muss |
| Prüfung | bei **16 px** noch erkennbar **und** in Graustufen noch unterscheidbar. Sonst neu zeichnen, nicht beschriften |

Entwurf: `zeichen.html` (07.08.2026) — 28 Zeichen.

**E60 — vier Schnitte, alle SIL OFL, zusammen < 900 kB als variable Dateien.**

| Rolle | Schrift | Warum |
|---|---|---|
| Oberfläche | **Inter** | große x-Höhe, echte Tabellenziffern; **nicht wählbar** — ein Knopf sieht überall gleich aus |
| Leser | **Literata** | von Google für Play Books gezeichnet, auf E-Ink und LCD geprüft |
| Barrierefrei | **Atkinson Hyperlegible** | Braille Institute; I/l/1 und O/0 unverwechselbar. Ersetzt das Verdana-Provisorium |
| Zahlen, Zeit, Technik | **JetBrains Mono** | gleiche Breite ⇒ Zahlen springen beim Zählen nicht. Nie für Fließtext |

> Schriftwahl **im Text** ist Komfort, Schriftwahl **in der Oberfläche** ist Chaos.

**E59 — zwei Zeichen, klare Grenze.** **▶** für alles mit Laufzeit (Anime, Film, Serie, Musik,
Hörbuch, DJ-Set), **Lesezeichen mit Pfeil** für alles Geblätterte (Manga, Manhwa, Novel,
Comic) — der Pfeil dreht sich mit der Leserichtung (E58). Ein Symbol **ohne Wort** nur dort,
wo der Titel danebensteht (Kachel, Ecke); in Listen und Knöpfen immer Symbol **und** Wort.

**E62 — zwei Farbskalen, zwei Bedeutungen.** Die Zahl selbst trägt die Farbe, nicht ein
Abzeichen daneben:

| | Skala | Werte |
|---|---|---|
| **übersetzt** | Lebendigkeit der Übersetzung | aktiv · schläft · tot · abgeschlossen |
| **gesamt** | Zustand der Serie | läuft · abgeschlossen · Hiatus · abgebrochen |

**E63 — Übersetzungsgüte als Wortabzeichen:** `MTL` · `MTL+KI` · `Fan` · `Offiziell`.
Nie Emoji, nie Sterne, nie Prozent. ⚠️ Das 🖐-Emoji im ersten Entwurf war unlesbar (JB).

**E64 — die Kapitelzelle.** `gelesen / übersetzt / erschienen` in **einem** Raster mit fester
`ch`-Breite. Die Spaltenköpfe dürfen den Abstand der Zahlen **nie** bestimmen — sonst
zerreißt eine lange Überschrift die Zahlenreihe.
⚠️ Vorher stand dort *„Kapitel 88 von 122 übersetzt"* — JB fragte zu Recht, warum sich
Kapitel 89 dann weiterlesen lässt. Drei Zahlen, drei Bedeutungen, keine Prosa.

**E85 — wo die Luft hingehört.** JB-Fund 07.08.2026: *„nicht alle haben ein Leerzeichen —
liegt es an den 1000er-Kapiteln?"* Ja, genau daran. Bei fester Zellbreite füllt `1140` die Zelle
ganz aus und klebt am Schrägstrich, während `132` schwebt. Der Abstand kam aus dem **Rest** der
Zelle, und der ist von der Stellenzahl abhängig.

| falsch | richtig |
|---|---|
| feste Zellbreite in `ch`, Zahlen rechts/mittig/links darin | Zahlen mit **Ziffernleerzeichen** (`U+2007`, exakt eine Ziffer breit) auf gleiche Länge gebracht |
| Abstand entsteht aus dem Leerraum der Zelle | Abstand gehört dem **Trenner**: `padding:0 .5ch` am `/` — immer gleich, egal wie viele Stellen |
| Breite fest verdrahtet (`4.2ch`) | Füllbreite aus der **breitesten Zahl der aktuellen Ansicht** — ein Regal ohne 1000er hat keine 1000er-Lücken |
| überall gleich | in der **Liste** wird gefüllt (Spalten sollen fluchten), in der **Einzelzeile** nicht (nichts zum Ausrichten) |

Damit steht hinter jedem `/` immer genau ein halbes Zeichen Luft — auch vor dem `…`.

**E73 — die dritte Zahl heißt „erschienen", nicht „gesamt".** JB-Einwand 07.08.2026:
*„Ist gesamt für dich nur verfügbar, wenn der Manga abgeschlossen ist?"* — Nein, und genau
das war der Denkfehler in meiner Beschriftung.

| Zahl | Bedeutung | immer bekannt? |
|---|---|---|
| **gelesen** | wo du stehst | ja |
| **übersetzt** | wie viele Kapitel es **in deiner Sprache** gibt | ja |
| **erschienen** | wie viele Kapitel es **im Original** gibt — jetzt, nicht am Ende | ja, außer keine Quelle zählt mit |
| *(Farbe der dritten Zahl)* | ob die Serie läuft, ruht, abgebrochen oder fertig ist | ja |

„Gesamt" klang nach *Endstand* und war deshalb bei jeder laufenden Serie unbeantwortbar.
„Erschienen" ist eine Momentaufnahme und **immer** eine echte Zahl. Ob die Serie endet, ist
eine **vierte** Information — und die trägt bereits die Farbe (E62), nicht die Ziffer.

⚠️ **`…` statt `?`** (JB, 07.08.2026): ein Fragezeichen liest sich wie *„da stimmt etwas
nicht"* oder wie Hiatus. Drei Punkte lesen sich wie *„geht weiter, wir wissen es nur nicht"*.
Und weil „erschienen" fast immer bekannt ist, tauchen sie ohnehin selten auf.

### 5.10.1 Die Kachelgrößen — und warum keine ohne Namen (E88)

⚠️ **Korrektur 07.08.2026.** Im ersten Entwurf gab es eine *Mini-Kachel*: nur Bild, kein Text,
möglichst viele auf einmal. JB fragte zu Recht: *„Dann sehe ich nicht, welchen Manga ich lese —
ist das cool?"* **Nein.** Die Begründung war „mehr Werke pro Bildschirm", und das ist eine
Zahl, kein Nutzen.

| Größe | Wofür | Text |
|---|---|---|
| **Held** | die eine wahrscheinlichste Fortsetzung | voll: Titel-Logo, Fortschritt, Knopf |
| **Kachel** | die Regale — der Normalfall | Titel + eine Zeile Zustand |
| **Zeile** | lange Listen, Suche, Archiv | Titel, Urheber, Zahlentrio, Aktion |
| ~~Mini~~ → **Dicht** | wenn viele auf den Schirm sollen | **Titel bleibt**, nur einzeilig gekürzt; alles andere fällt weg |

**E88 — jede Kachel trägt ihren Namen.** Cover sind wiedererkennbar, wenn man ein Werk **kennt**.
Genau dann braucht man sie aber nicht. Beim Suchen, beim Stöbern und bei allem Neuen ist das
Cover ein Rätsel — und ein Regal mit 800 Titeln wird zum Memory-Spiel. Die Prioritätsleiter
(§5.2) darf **Zustand, Fortschritt und Quelle** streichen; **der Titel ist Rang 1 und fällt nie.**

Was stattdessen dichter wird: Titel auf **eine** Zeile mit Auslassung, Zustandsfarbe wandert in
einen 3-px-Streifen unter dem Bild, Zahlen verschwinden. Damit passen fast so viele Kacheln auf
den Schirm — und man weiß trotzdem, was man ansieht.

### 5.11 Gelernte Fallen

Fehler, die in dieser Sitzung tatsächlich passiert sind. Für die zweite KI wertvoller als
jede Regel, die nie gebrochen wurde.

| Falle | Symptom | Regel daraus |
|---|---|---|
| **`height:100%` im Flex-Kind** | Bild winzig oder unsichtbar — **dreimal passiert** | Höhe nie in Prozent, wenn der Elternteil sie nicht kennt: `flex:1` + `min-height`, oder in `calc()` rechnen |
| **`::after`-Schleier über dem Text** | Titel im Schatten | jeder Text auf einem Bild bekommt eigenen `z-index` **über** dem Verlauf |
| **Gerades `"` in einer `"`-Zeichenkette** | ganze Datei tot, kein Knopf reagiert | **E71** — jede Oberflächendatei wird syntaktisch geprüft, **bevor** sie jemand sieht |
| **Messen vor jeder Bewegung** | geführte Ansicht „lud neu" statt zu gleiten | Geometrie **einmal** messen, zwischenspeichern, nur bei Modus-/Zoom-/Größenwechsel verwerfen |
| **Zahlen ohne Abstand** | „3 in Arbeit68 %" | zusammengesetzte Angaben immer in eigene Elemente mit `&nbsp;` |
| **Waagerechtes Scrollen im Handheld** | Leiste außerhalb des Bildschirms | `flex-wrap:wrap` statt `overflow-x:auto` — die Prioritätsleiter (§5.2) gilt auch für Leisten |
| **Umbruch bei halber Laptop-Breite** | Regalkopf zweizeilig | Container-Abfragen statt Bildschirm-Abfragen; die Leiter greift am Bauteil, nicht am Fenster |
| **Eigene `display`-Regel schlägt `[hidden]`** | versteckte Bauteile bleiben sichtbar | einmal global `[hidden]{display:none!important}` — sonst ist jedes `hidden` bei Flex-Elementen wirkungslos |
| **Einpassen macht Zoom wirkungslos** | Rahmen bleibt gleich groß, nur der Text schrumpft | wo etwas automatisch eingepasst wird, darf der Regler **nicht** die Quelle vergrößern, sondern muss die **Füllung** steuern (**E74**) |
| **Feste `px` in einer skalierten Fläche** | Sprechblasen schrumpfen, während der Rahmen wächst | ein Maßstab `--sk` an der Fläche; **alles** darin rechnet damit — Schrift, Abstände, Rahmenbreiten |
| **`--sk` am falschen Element** | in einem Geschwisterzweig (Endlosstreifen) ist die Variable undefiniert und die Rechnung ungültig | Maßstäbe gehören an den **gemeinsamen** Vorfahren, nicht an einen Zweig |
| **`visibility:hidden` statt `display:none`** | unten bleibt ein leerer Streifen stehen | `visibility` reserviert den Platz weiter — wer Platz zurückgeben will, braucht `display:none` (JB-Fund: Endlosstreifen) |
| **Zellbreite trägt den Abstand** | vierstellige Zahlen kleben, dreistellige schweben | die Luft gehört dem Trenner, nicht dem Zellrest (**E85**) |

### 5.10.2 Was fest sein muss und was atmen darf (E103)

**JB-Fund 07.08.2026:** *„Wenn ich von 100 % runtergehe, ist der Zeilenumbruch weg.
Diese Sachen sollten fix sein."* — Richtig, und es ist eine allgemeine Regel:

> **Alles, dessen Beschriftung sich beim Bedienen ändert, bekommt eine feste Breite.**
> Sonst springt der Nachbar mit, und man verliert die Stelle, an der man gerade war.

| **Fest** — weil sich der Text ändert, während man klickt | **Frei** — weil der Inhalt die Größe bestimmen darf |
|---|---|
| Zyklusknöpfe (`100 % → 75 % → 50 %`, `70 % → aus`) | Titelzeilen und Beschreibungen — sie kürzen mit `…` |
| Zeit- und Zähleranzeigen (`08:12`, `+0,5 s`, `9 / 24`) | Kacheln im Regal (die Spaltenzahl passt sich der Breite an) |
| Fortschrittsprozente, Kapitelzahlen (mit Ziffernleerzeichen, **E85**) | Tafelhöhe, wenn eine Liste länger wird |
| Die Untertitel-Vorschau (feste Höhe, Text skaliert darin) | Untertitelzeilen im Bild selbst — sie sind der Inhalt |
| Jede Werkzeugleiste, deren Knöpfe ihren Zustand als Text zeigen | Fließtext, Suchergebnisse, alles Gelesene |
| Der Platz für Abzeichen (`MTL`, `Fan`) — auch wenn gerade keins da ist | Die Fläche selbst |

**Die Faustregel:** *Ändert sich der Text durch **meine** Handlung → fest. Ändert er sich, weil
sich der **Inhalt** ändert → frei.* Wer klickt, darf nie bestraft werden, indem sich die
Oberfläche unter dem Zeiger verschiebt.

**E104 — Einstellen ≠ Wählen.** *Welcher* Untertitel (Sprache, Fassung, aus) gehört in
**Ton & Text**. *Wie er aussieht* (Größe, Schrift, Farbe, Kasten, Ort, Versatz) gehört ins
**Zahnrad**. Beides im selben Menü macht es überladen und lässt einen zweimal dieselbe Sache
an zwei Orten suchen.

**E105 — Klick daneben schließt.** Jede Tafel, jedes Menü, jedes Fenster. Ohne Ausnahme,
ohne Nachdenken. Zusätzlich Esc.

**E107 — Klangzeichen auf Distanz.** Am Fernseher und am Handheld gibt es einen **kurzen,
leisen Klick** beim Fokuswechsel und ein tieferes *Tock* beim Bestätigen — genau wie bei
Netflix, Apple TV und der Steam-Deck-Oberfläche. Der Grund ist nicht Zierde: auf drei Metern
sieht man den Fokusrahmen erst nach 100–200 ms, hört den Klick aber sofort. **Am PC ist er
aus** (dort ist der Zeiger die Rückmeldung) und überall abschaltbar.

### 5.11.1 Was SyncYouTube schon kann (Bestandsaufnahme 07.08.2026)

⚠️ **JB-Einwand: „du hast nicht genau hingeschaut, was wir bereits erschaffen haben."**
Berechtigt. Der Downloader hat einen gewachsenen Spieler; einiges davon hätte ich hier neu
erfunden. Die Übernahmeliste:

| Vorhanden in `oberflaeche.py` | Was daraus wird |
|---|---|
| **⏪/⏩ bis 32×** (mehrfach drücken) | **übernommen, verbessert**: gehalten statt mehrfach gedrückt (E80) |
| **Untertitel-Panel** — Größe, Schrift, Farben, Schatten, Hintergrund, Versatz, **Live-Vorschau** | genau die Werkstatt hinter dem Zahnrad. Beim Bau **den vorhandenen Code übernehmen**, nicht neu schreiben |
| **✂ Ausschnitt** wie ein Twitch-Clip: A/B ziehen, Spieler springt mit, als neuer Titel speichern, Original bleibt | **fehlte** → **E89**: der Ausschnitt ist eine **Ausgabe** des Werks, nie ein neues Werk. Favorit je Gruppe wie bisher |
| **Karaoke mit Romaji** (LRCLIB, wortweise) | **fehlte** → **E90**: das ist dieselbe Technik wie *Mitlesen* beim Hörbuch. Ein Name, eine Umsetzung |
| **Auf YouTube öffnen** (springt zur Stelle) · Link kopieren ohne Zeitstempel | **fehlte** → **E91 „Zur Quelle"**, verallgemeinert auf jede Herkunft |
| **Mini-Player** (Cover + Regler, eingebettet) | **E92 Mini-Bühne** — genau das braucht Musik, wenn man nebenher stöbert |
| **Playlist herauslösen / eingliedern** (andockbares Fenster) | bei uns: Warteschlange klebt rechts, klappt weg. Freie Fenster gehören zum Layout-Editor, nicht zur Bühne |
| **Ausgabegerät Browser ↔ VLC** | **erben wir nicht** — libmpv steckt schon im Fenster (E34). Das war eine Notlösung |
| **Transkript-Suche** über alle Untertitel, Funde als Playlist | **E93** — die unterschätzteste Funktion. Gehört in die **Suche**, und dann für Untertitel *und* Buchtext |
| Bild-in-Bild · Sleep-Timer · Crossfade · Tempo · SponsorBlock · ❤ · **eigene Tastenbelegung** | alles richtig, alles eins zu eins übernehmen |
| **Kompakt-Ansicht: „mehr Kacheln, nur Bild + Titel"** | ⚠️ bestätigt **E88** aus dem eigenen Bestand: auch die dichteste Ansicht trug immer den Titel |
| Playlists: Sync, .m3u, Smart-Playlists, Mixer (Radio, Meistgespielt, Zuletzt) · ✨ Entdecken · Abos mit Regeln · Autotag (MusicBrainz + iTunes) · Umbenennung mit **Probelauf und Rückgängig** · Dubletten-/Pfad-Heilung | gehört nicht in die Bühne, aber alles in §9/§10 — nichts davon neu erfinden |

> **Der eine echte Unterschied:** im Downloader ist der Spieler **ein Fenster unter vielen**
> (andockbar, herauslösbar, Layout-Editor). Bei SyncFundus ist die Bühne eine **Ebene** — man
> geht hinein und wieder heraus (E38). Grund: hier wird auch gelesen, und ein Leser in einem
> andockbaren Fensterchen ist kein Leser.

### 5.11.2 Der Rahmen — was gleichzeitig läuft (E97–E101)

> **JB-Frage 07.08.2026: „Wo kommt denn der Ton her? Ich will nicht fünf Tabs wechseln müssen."**
> Entwurf: `rahmen.html`

**E97 — die eine Regel:** *eine Sache hat das Bild, eine Sache hat den Ton, und beide dürfen
verschieden sein.* Alles Weitere folgt daraus.

| Du tust | Fläche | Ton |
|---|---|---|
| Stöbern | Regal | Klangleiste läuft weiter; lief nichts, ist sie **gar nicht da** |
| Lesen | Leser | unverändert — **Musik beim Lesen ist der häufigste Fall überhaupt** |
| Film starten | Bühne | Musik pausiert **sichtbar**: *„von Vinland Saga übernommen"*, ein Klick holt sie zurück |
| Film läuft, du gehst ins Regal | Regal | Bild **schwebt** unten rechts, Ton bleibt beim Film |
| Musik ganz ansehen | Musikfläche mit Warteschlange und Karaoke | gleicher Ton — die Klangleiste **verschwindet dort**, sie wäre doppelt |
| Hörbuch **und** lesen | Leser | geht, aber wir **fragen einmal**. Zwei Sprachströme sind kein Komfort, sondern ein Versehen |

**E98 — die Klangleiste, bewusst unscheinbar.** Spotify ist ein Abspielprogramm, wir sind es
nicht. Deshalb: **46 px** statt 72–90 · Cover **30 px** statt 56–64 · Fortschritt als
**2-px-Faden auf der Oberkante** statt als eigene Leiste (dasselbe Prinzip wie die Ladeanzeige
im Browser) · **3 + 2 Knöpfe** statt neun · **wegklappbar** · und **wenn nichts läuft, ist sie
nicht da** — kein reservierter Platz für Nichts.

**E99 — genau ein schwebendes Bildfenster.** Vier Ecken zum Einrasten, drei Größen, kein freies
Verschieben. **Im Leser und in der vollen Musikfläche wird es ausgeblendet, nicht verschoben** —
wer liest, will nichts Bewegtes im Bild. Der Ton läuft weiter: **Bild zu ≠ Ton aus.**

**E100 — genau eine Tafel.** Eine zweite ersetzt die erste; nie zwei übereinander. Die Fläche
darunter **verrutscht nicht** — keine Spalte, die sich zusammenschiebt. Esc und Klick daneben
schließen. Am Handy fährt sie von unten hoch statt in der Mitte zu schweben.

**E101 — immer derselbe Bereich.** Regal, Leser, Bühne und Werk-Seite belegen **exakt** dieselbe
Fläche; Seitenleiste und Klangleiste bleiben stehen. Nach drei Tagen weiß das Auge, wohin es
schauen muss — das ist mehr wert als jede Animation. Übergang: **180 ms Überblendung**, kein
Vollbildsprung, kein Ladebild.

⚠️ **Was wir nicht bauen:** frei verschiebbare Fenster. SyncYouTube hat einen Layout-Editor mit
andockbaren Panels — für einen **Downloader** richtig, weil man dort mehrere Listen gleichzeitig
beobachtet. SyncFundus ist ein Ort zum **Lesen und Sehen**. Wer liest, will eine Fläche, nicht sechs.

### 5.12 Die Bühne (E72, E75, E77)

> **E72 — das Wort „Spieler" ist verboten.** Im Deutschen ist ein Spieler ein Mensch mit
> Gamepad, und wir haben eine Spiele-Schicht in der Zwiebel. Die Abspielfläche heißt
> **Bühne** — passend für Film, Musik und Hörbuch, und die Farbe hieß ohnehin schon so
> (`#0A0A0B`, die einzige Fläche, die nie zwischen Tag und Nacht wechselt).
> Der **Text-Wächter** (E42) bekommt „Spieler" auf die Verbotsliste.
> Entwurf: `buehne.html` (07.08.2026)

**Drei Gestalten, eine Bühne.** Video (Anime, Film, Serie) · Musik (Lied, Album, DJ-Set) ·
Hörbuch. Verschieden ist nur die Mitte; Leiste, Zeiten, Lautstärke, Tempo, Tafel,
Tastenbelegung und das Zurückschreiben des Fortschritts sind überall dieselben.

**Die Leiste ist der eigentliche Entwurf** — dort wird alles sichtbar, was die Anreicherung
weiß:

| Element | Woher |
|---|---|
| **Vorspann-/Abspannband** (türkis/blau) | Kapitelmarken der Datei; fehlen sie, aus dem **Tonfingerabdruck** — ein Anime-Vorspann ist über eine Staffel akustisch identisch (dieselbe Technik wie Chromaprint, E20) |
| **Kapitelstriche** | Container bei Filmen · Kapiteldateien bei Hörbüchern · **Tracklist** bei DJ-Sets |
| **hellerer Teil** | was auf der Platte liegt — bei lokalen Dateien sofort voll, und **deshalb** aussagekräftig, wenn nicht |
| **Vorschaubild beim Überfahren** | einmal beim Einlagern erzeugt, ein Kachelbild je Folge (~200 kB, ffmpeg, alle 10 s) — kein Netz, kein Warten |

**E81 — die Bedienung liegt IM Bild und blendet weg.** Nie unter dem Bild, nie in einer eigenen
Leiste. Nach **2,5 s** Ruhe blendet sie aus (Netflix, YouTube und Plex nehmen 3 s; kürzer wirkt
hektisch, länger vergisst man sie).

| | Wert | Grund |
|---|---|---|
| Ausblenden | **420 ms** weich | hartes Verschwinden liest sich wie ein Absturz |
| Einblenden | **120 ms** | Ausblenden ist Höflichkeit, Einblenden ist Reaktion — die Zeiten dürfen nicht gleich sein |
| Untertitel | rutschen in derselben Bewegung nach unten | sonst kleben sie mitten im Bild, wo eben Knöpfe waren |
| Mauszeiger | `cursor:none` mit | ein schwebender Pfeil stört mehr als eine Leiste |
| bleibt sichtbar | Zeiger auf der Leiste · Tafel offen · **pausiert** | |

**E80 — zehn Sekunden tippen, halten spult.** Symmetrisch 10/10 in beide Richtungen (nicht
10/30 wie YouTube — das ist Vortrags-Denke, nicht Serien-Denke).

| gehalten seit | Tempo | |
|---|---|---|
| < 0,4 s | — | war ein Tipp: **10 s** |
| ab 0,4 s | **4×** | Spulen beginnt, Kachelbild erscheint |
| ab 1,4 s | **12×** | |
| ab 2,6 s | **30×** | |
| loslassen | — | springt dorthin und läuft weiter |

⚠️ **Das ist Spulen, kein schnelles Abspielen.** Kein Ton, keine verzerrten Stimmen — nur die
Kachelbilder, die beim Einlagern ohnehin entstehen. Deshalb ruckelt es nie, auch bei 30×.
Vorbild ist **Plex/Kodi** (Staffelung), aber als *eine Geste* statt als drei Tastenkombinationen
wie bei VLC (`Shift`/`Alt`/`Strg` + Pfeil).

**E82 — die Pausenkarte.** Nach **12 s** Pause erscheint am **Rand** (nicht in der Mitte, das
Bild bleibt sichtbar) eine Karte: Folgentitel, Jahr, Studio, drei Sätze Inhalt, und eine
**Rollenzeile** — wer gerade zu sehen ist, mit Gesicht. Das beantwortet die einzige Frage, für
die man überhaupt pausiert: *„Moment, wer ist das nochmal?"*
⚠️ **Nie Empfehlungen in der Pause.** Netflix zeigt dort „Ähnliche Titel" — das ist Werbung im
eigenen Wohnzimmer. Die Rollen kommen aus dem Werk-Wissen (§10.1), das für Übersetzung und
Vertonung ohnehin gebaut wird.

**E83 — „Ton & Text", nicht „Spuren".** *Spuren* ist ein Fachwort aus dem Schnitt und wird als
„Untertitel" gelesen, obwohl auch der Ton drin ist. *Sprache* wäre falsch, sobald man 5.1 gegen
Stereo tauscht. *Fassung* ist zu abstrakt. **Ton & Text** benennt beide Hälften.
Und **Einstellen ≠ Auswählen**: die Untertitel-Werkstatt (Größe, Hintergrund, Schrift,
**Versatz ±**, gilt-für-alles/nur-hier) sitzt hinter einem eigenen **Zahnrad** daneben.
Auswählen ist eine Entscheidung pro Folge, Einstellen eine fürs Leben.

**E94 — Folgen: zwei Anordnungen, ein Inhalt.** Am **PC** ein Raster (viele auf einen Blick,
Maus kann zielen). Am **Fernseher** eine **Reihe nach rechts** mit größeren Kacheln und
Einrast-Punkten — dort gibt es nur vier Richtungstasten, und eine Reihe ist die einzige Form,
die sich mit vier Tasten ohne Nachdenken bedienen lässt. **Der Staffelwechsel ist eine Wand**:
ein senkrechter, beschrifteter Balken zwischen den Staffeln, damit niemand unbemerkt in
Staffel 1 rutscht.

**E115 — die kanonische Weiche.** Am Folgenende läuft **nicht** blind die nächste Folge an,
wenn die Reihenfolge etwas anderes vorsieht. Dann erscheint eine Weiche mit zwei bis drei
Wegen — **OVA · nächste Folge · zurück ins Regal** —, und der Zähler läuft nur auf dem
empfohlenen.

| | |
|---|---|
| **Woher die Reihenfolge kommt** | AniList-Beziehungen (`SIDE_STORY`, `SPECIAL`, `PREQUEL`) · AniDB-Episodennummern (OVAs tragen dort eine eigene Reihe) · TMDB-Staffel 0 · und Fan-Pflegelisten wie die bekannten „watch order"-Sammlungen |
| **Wann gefragt wird** | nur, wenn zwischen dieser und der nächsten Folge tatsächlich etwas liegt. Sonst der normale Autostart |
| **Umstellbar** | *kanonisch* ↔ *nach Erscheinungsdatum*. Beides ist bei Anime eine legitime Reihenfolge, und Streit darüber ist älter als das Internet |
| **Filme** | Ein Film, der eine Staffel zusammenfasst (Rekap), wird **markiert, nicht empfohlen** — wer die Folgen gesehen hat, braucht ihn nicht |

**E116 — Nur-Ton.** Musikvideos sind Werke mit Bild, aber oft will man nur den Ton. Ein Schalter
in der Musikleiste: Bild aus, Ton läuft, spart Strom und Aufmerksamkeit. Der Zustand hängt am
**Werk**, nicht an der Sitzung — was einmal Musik war, bleibt Musik.

**E84 — Folgen wohnen unter der Bühne.** Als Kachelreihe mit Bild, Nummer, Dauer,
Fortschrittsstreifen und Staffelwahl — nicht in einer Tafel. Eine Tafel ist für das, was das
*laufende* Bild betrifft; die Nachbarfolgen sind Navigation und gehören in die Fläche darunter.

**E75 — wer die Untertitel zeichnet.** `srt` und `vtt` zeichnen **wir**: dann gelten
Hausschrift, Kontrastsaum und deine Größeneinstellung. `ass`/`ssa` mit Karaoke, Schildern und
Bewegung zeichnet der **Motor**, weil dort die Gestaltung Teil des Werks ist. Der Wechsel ist
unsichtbar, aber die Regel muss stehen — sonst sieht das Programm an zwei Stellen anders aus.

**E77 — die Gamepad-Belegung ist fest:** `A` Pause · `B` zurück · `X` Spuren ·
`Y` Vorspann überspringen · `LB/RB` Kapitel · Stick spulen. Muskelgedächtnis ist wertvoller
als Anpassbarkeit. Auf Distanz wachsen die Ziele auf **48 px**, und die Fokusmarke ist ein
**heller Rahmen**, kein Farbwechsel — auf drei Metern sieht man Rahmen, keine Sättigung.

**Der Übergang Hören ↔ Lesen** ist der Grund, warum das *eine* Bühne sein muss: weil wir die
Stimmen selbst erzeugen, kennen wir zu jedem Satz die Zeitmarke (EPUB-3-Media-Overlays,
geschenkt statt geschätzt). *Weiterlesen ab hier* öffnet den Leser beim **markierten Satz**,
nicht beim Kapitelanfang — und umgekehrt genauso. Bei einem **gekauften** Hörbuch fehlen die
Marken; dort bleibt es beim Kapitel, und das wird auch so gesagt.

**Was die Bühne nie tut:** ein zweites Fenster öffnen (E34) · das Bild dehnen · ohne
Abschaltmöglichkeit automatisch weiterlaufen · die Steuerung ausblenden, während die Maus sich
bewegt · beim Pausieren Empfehlungen über das Bild legen.

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
  Errungenschaften als zweite Skala. ROM = Werk, Emulator = Abspielweg — dieselbe
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

**E51 — Wie oft muss man sich neu anmelden?** Unterschiedlich, und das Programm muss den
Unterschied verstecken:

| Weg | Haltbarkeit | Erneuerung |
|---|---|---|
| **OAuth** (AniList, MAL, Twitch) | Zugriffsmarke kurz (Stunden), **Erneuerungsmarke lang** | **still im Hintergrund** — der Nutzer merkt nichts |
| **Browser-Cookie** (Crunchyroll, Prime) | Wochen bis Monate | läuft irgendwann ab → einmal neu im Browser einloggen |
| **Gerätekopplung** (eigene Geräte) | bis zum Widerruf | nie |

> **Gefragt wird nur bei echtem Entzug.** Eine ablaufende Marke ist kein Ereignis für den
> Nutzer. Dazu eine Seite **„Verbindungen"**, die für jedes Konto zeigt: verbunden seit,
> zuletzt erneuert, was wir davon lesen — und ein Knopf zum Trennen.

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

**E48 — Genau ein Ausgang pro Datei.**

> 🔑 Es gibt **keine** Regel, die aussortiert, und **keine** zweite, die wieder einsortiert.
> Der Weg ist linear: die Kaskade läuft durch und endet in **genau einem** von drei
> Endzuständen.

| Endzustand | wann | Papierkorb? |
|---|---|---|
| **Werk** | identifiziert | nein |
| **Eigenes** | Medium erkannt, aber keine Datenbank kennt es (Familienvideo, eigene Aufnahme) | nein |
| **Postfach** | Medium erkannt, Zuordnung unsicher | nein |

**Alle drei sind gültige Endzustände. Keiner ist ein Papierkorb.** Damit kann keine Regel eine
andere überstimmen, es gibt keine Wiedereintritte und nichts zu verschachteln — die Sorge vor
verzerrten Prioritäten durch kaskadierende Regeln ist konstruktiv ausgeschlossen.

Der Zähler aus §5.7 zählt entsprechend **nicht** „aussortiert", sondern **wie viele Dateien in
welchem Endzustand gelandet sind**. Eine Zahl, die steigt, wo sie nicht steigen soll, ist dann
sofort sichtbar.

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

### 8.4 Die Browser-Erweiterung (E67, E68)

> **Sie markiert. Sie fragt nicht.**
> Entwurf: `erweiterung.html` (07.08.2026)

Sie ist das Auge im Browser — in **beide** Richtungen: sie meldet, was gelesen wird, und malt
umgekehrt den Regalzustand auf die fremde Seite zurück. Das ist der Grund, warum JB überhaupt
online sieht, was er schon liest.

**Was sie tut:**

| | Wie |
|---|---|
| **Lesen erkennen** | Kapitelseite offen **und** (> 60 % gescrollt **oder** > 25 s geblieben). Beides, weil Langstreifen nie scrollen und Doppelseiten nie dauern |
| **Werk zuordnen** | Adapter liest Titel, Nebentitel, Urheber und — wenn vorhanden — die fremde ID aus der Seite; danach dieselbe Zusammenführung wie in der Suche (E56) |
| **Zurückmalen** | grüner Streifen an gelesenen Kapiteln · orange Marke *Hier weiter* am nächsten · Ecken-Zeichen ● ◐ ○ im Raster · **eine** Leiste über der Liste |
| **Übergeben** | ein Klick schickt die Kapitelliste an den lokalen Server; ab dort läuft die Warteschlange |

**E67 — was sie nie tut:**

| | Warum |
|---|---|
| auf allen Seiten laufen | keine `<all_urls>`-Erlaubnis; nur Domains aus der Adapterliste, einzeln freigegeben |
| nach draußen funken | **ein** Ziel: `127.0.0.1` mit einem beim ersten Start erzeugten Token. Keine Telemetrie, kein Konto |
| herunterladen | sie **meldet** nur. Ein Add-on, das Dateien zieht, fliegt aus jedem Store — und wäre das falsche Werkzeug |
| Popups werfen | kein Toast, kein Ton, kein springender Zähler. Wer beim Lesen gestört wird, schaltet sie ab — dann war alles umsonst |

**Der Knopf hat vier Zustände, mehr nicht:** grau (schläft) · orange (neu) · **gelbe Zahl**
(gekannt — wie viele Kapitel hier schon offen waren) · **orange Zahl** (im Regal, Rückstand).
Die Zahl ist immer der **Rückstand**, nie der Fortschritt.

**Im Fenster am Knopf** steht neben Werk und Zustand auch die **Zuordnungssicherheit** und
**der Beweis** („erkannt über Nebentitel 나 혼자 만렙 뉴비 → MangaBaka #34812"). Unter 70 %
wird gefragt statt still das Falsche gezählt — das ist §5.6 (nichts entscheidet stumm),
angewandt auf fremdem Grund. *Falsches Werk?* öffnet die Suche mit dem Seitentitel
vorgetippt; die Korrektur gilt ab sofort für die ganze Domain-Serie.

**E76 — der Fortschritt hängt am Werk, nie an der Seite.** JB-Frage 07.08.2026: *„Wie erkennt
sie den korrekten Ort? Wenn ich denselben Manga woanders lese? Wenn eine andere Scanseite
übersetzt? Wenn der Titel woanders anders ist?"* — Die Seite ist **nie** die Identität. Sie ist
nur ein Weg zum Werk, und Wege sind austauschbar.

```
asuracomic.net/series/solo-max-level-newbie ─┐
mangabuddy.com/manga/solo-max-level-newbie  ─┼─→  Werk #34812  ←── dein Fortschritt
kunmanga.com/nahonja-manleb-nyubi           ─┘        (Kapitel 63)
```

| Fall | Wie er gelöst wird |
|---|---|
| **Dieselbe Serie auf einer anderen Seite** | Der Adapter löst *(Domain, Serienpfad) → Werk-ID* **einmal** auf und merkt sich das Paar. Ab dann kostet jede weitere Seite nichts. Kapitel 64 auf MangaBuddy zählt auf dasselbe Werk wie Kapitel 63 auf Asura. |
| **Anderer Titel dort** | Erkennung läuft über die **Synonymliste** (E56), nicht über den sichtbaren Titel: koreanischer Originaltitel, Romanisierung, englischer Titel, fremde ID im Seitenquelltext. Trifft eines davon, ist es dasselbe Werk. |
| **Andere Übersetzergruppe** | Die Gruppe ist eine Eigenschaft der **Ausgabe**, nicht des Werks — genau wie die Sprache. Zwei Gruppen sind zwei Ausgaben eines Werks, und der Lesefortschritt zählt am Werk. Die Güte (`Fan`, `MTL`, E63) hängt an der Ausgabe. |
| ⚠️ **Andere Kapitelzählung** | Der gefährlichste Fall. Gruppen fassen zusammen, spalten auf, zählen den Prolog mit oder nicht. Wir vergleichen die Kapitelliste der Seite mit unserer **Bezugsliste** (MangaBaka/MangaUpdates) und suchen einen **konstanten Versatz**. Passt einer für ≥ 80 % der Einträge, wird er gespeichert und angezeigt (*„zählt +1 gegen deine Liste"*). Passt keiner, wandert es ins **Postfach** — lieber nachfragen als still danebenzählen. |
| **Dezimalkapitel** (`88.5`, Omake) | Eigene Einheit, zählt aber nicht als Fortschrittssprung. |
| **Zuordnung unter 70 %** | Wird gefragt, nicht geraten (§5.6). Deine Antwort gilt danach für die ganze Domain-Serie. |

> Das ist derselbe Grundsatz wie **E20** (Fingerabdruck vor Dateiname) — nur im Browser:
> **die Adresse ist ein Hinweis, nie ein Beweis.**

**E68 — die Adapterliste wohnt nicht in der Erweiterung**, sondern als kleine signierte
JSON-Datei, die SyncFundus lokal ausliefert. Zwei Gründe: eine neue Seite ist dann eine Zeile
Text statt zwei Wochen Store-Prüfung — und die Liste steht nirgends öffentlich im Paket
(dieselbe Trennung wie **E12**).

⚠️ **Der ehrliche Haken.** Firefox erlaubt das alles; Chrome baut seit 2024 schrittweise ab,
was wir brauchen, und mag Add-ons nicht, die mit `localhost` reden. Also **Firefox zuerst und
ordentlich**, Chrome als Beipack. Für beide gilt: die Erweiterung ist **Zubehör**. Fällt sie
weg, läuft SyncFundus weiter — dann eben nur mit der `places.sqlite`-Auswertung, die es
ohnehin schon gibt.

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
> SyncFundus über dich" — sichtbar, editierbar, exportierbar, löschbar. Netflix und Spotify
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

### 12.4 Hülle und Bühne — F01 beantwortet

**Hülle:** eigenes Fenster (**pywebview**, `huelle.py` existiert bereits) mit der
Web-Oberfläche darin. Fühlt sich an wie ein Programm, ist innen weiter Web — also bleibt
das Entwicklungstempo mit `importlib.reload` + F5 erhalten.

**E25 — Bühne: libmpv als Motor, libVLC als zweite Umsetzung.**

| | libmpv | libVLC |
|---|---|---|
| **ASS/SSA-Untertitel** | **libass = Referenzumsetzung** — Stile, Karaoke, Schilder korrekt | belegte Probleme bei Positionierung/Farben/Effekten, Ruckler beim Untertitelwechsel |
| Bildausgabe | Skalierung, HDR-Tonemapping, Interpolation, eigene Shader (**Anime4K**) | solide, weniger Kontrolle |
| Einbettung | saubere C-API | einfacher zu verpacken |
| Wer baut darauf | IINA, Celluloid, MPC-QT | VLC selbst |
| **Wo VLC gewinnt** | — | DVD/Blu-ray-**Menüs**, DVB/TV-Karten, Streaming-Server, geht mit **kaputten Dateien** gnädiger um |

Für Anime ist es nicht knapp: Fansub-Untertitel sind gestylt und positioniert, VLC macht
sie kaputt. **Beide bleiben verfügbar** — die Bühne ist eine Fähigkeit hinter einer
Schnittstelle (E11). ⚠️ **Kein eigenes VLC-Fenster mehr**: der Motor zeichnet ins eigene
Fenster, die Steuerleiste liegt darüber, der Fernsehmodus sieht aus wie ein Streamingdienst.

**E34/E35 — Es gibt nie zwei Fenster.**

> 🔑 libmpv und libVLC zeichnen in eine **Fläche innerhalb unseres Fensters**. Ein Motor,
> der das nicht kann, ist kein Motor, den wir nehmen.
>
> 🔑 **Der Motor liefert Pixel. Alles andere liefern wir.** Steuerleiste, Spulbalken,
> Untertitelmenü, Tastenkürzel, Fernbedienung — alles unser Code, über die Videofläche
> gezeichnet. mpv und VLC zeichnen **keinen einzigen Knopf**.

Damit ist „beide müssen identisch aussehen" nicht schwer, sondern **konstruktiv unsichtbar**.
So bauen IINA und Celluloid auf libmpv auf. Netflix, Disney+ und Amazon haben das Problem
nie, weil ihre Bühne kein Programm ist, sondern ein Rechteck im selben Dokument.

⚠️ **Folge für F01:** ein Browser kann keine native Videofläche einbetten. Das **eigene
Fenster (pywebview) ist damit technische Voraussetzung**, keine Vorliebe.

**Blu-ray:** ⚠️ **Playlist-Verschleierung** ist eine echte Schutzmaßnahme — Hunderte
Scheintitel mit verwürfelten Segmentkarten. Nicht nachbauen: **MakeMKVs Logik nutzen**
(ab 1.16.4 deutlich besser bei Java-Verschleierung) und quer prüfen mit der
**Laufzeit gegen TMDB** — die Echtheitsprüfung aus §9.4 ist zugleich der Haupttitel-Finder.
Ergebnis: **eine MKV, alle Spuren drin, Menü und Werbung weg.**

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
| Hülle mit nativer Bühne (Tauri/Capacitor) | mittel | wenn Offline + Video am Handy ernst werden |
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

### 12.6 Qualitätsnetz (E42)

Ausgangslage: **ein Tester.** Damit ist Fehlerfreiheit nicht garantierbar — wohl aber, dass
**kein Fehler etwas zerstört** und **kein Fehler still bleibt**.

| Garantie | fängt | Aufwand |
|---|---|---|
| **Verhaltensnetz** (vorhanden: 17 Tests, kein Netz/Platte) | Logikfehler | vorhanden |
| **Layout-Wächter** — behauptet: nichts ragt über den Rand · nichts überlappt ungewollt · kein waagerechtes Scrollen · jedes Ziel ≥ 24 px | überlappende Rahmen, Text außerhalb, zu kleine Symbole | klein, hoher Ertrag |
| **Bildvergleich** je Bauteil bei 360/834/1280/3440 | alles Optische | mittel |
| **Text-Wächter** — alle Zeichenketten aus *einer* Quelle; kein unübersetzter Schlüssel, keine Überlänge in fester Breite, **keine CJK-Zeichen in DE/EN** | „plötzlich japanische Zeichen" | klein |
| **Der Affe** — klickt zufällig, meldet Abstürze | die abstrusen Situationen ohne Testnutzer | klein |
| **Aufnahme & Wiedergabe** einer echten Sitzung | „läuft nur in meinem Ablauf" | mittel |

Dazu: **neue Funktionen kommen dunkel** (Schalter, standardmäßig aus) und **Nutzungszähler,
rein lokal** — ohne Zahlen rätst du, welche Funktion niemand anfasst (Beispiel: der
Equalizer in SyncYouTube). Ungenutzte Funktionen sind Belastung, nicht Vermögen.

**Die extreme Stufe** (JB-Go 06.08.2026 — „machen"):

| | Was | Warum |
|---|---|---|
| **E52 · Deterministischer Kern** | kein `random`, kein `now()` **in der Logik** — beides wird hineingereicht | **jeder** Fehler wird exakt reproduzierbar; ohne das ist alles darunter wertlos |
| **Eigenschaftsbasiertes Prüfen** | nicht Testfälle schreiben, sondern **Regeln, die immer gelten**; das Werkzeug sucht Gegenbeispiele (**Hypothesis**, mit **HypoFuzz** adaptiv) | das ist der „Testnutzer, mit dem du nicht rechnest" |
| **Simulationslauf** | ein Jahr Bibliotheksbetrieb in Sekunden gegen erfundene Quellen | findet Ketten, die erst nach Monaten entstehen |
| **Dauerhafte Invarianten** | auch im **laufenden** Programm prüft ein Hintergrundauftrag ständig die Stimmigkeit | fängt Verfall durch die echte Welt |

Regeln, die immer gelten müssen (die ersten vier Eigenschaften):
- *Jede Datei, die hineingeht, kommt als Werk **oder** Eigenes **oder** ins Postfach — nie verschwindet eine.*
- *Die Leiter sortiert bei jeder Eingabe stabil.*
- *Fortschritt geht nie rückwärts, außer der Nutzer setzt ihn.*
- *Jede Handkorrektur überlebt jede Neuanreicherung.*

**E49 — Fehlerprotokoll.** Alles Auffällige wird **lokal** gesammelt, nicht nur Abstürze:
404er, Weiterleitung auf die Serienseite statt aufs Kapitel, fehlgeschlagene Echtheitsprüfung,
tote Quelle, Muster ohne Treffer. Das ist maschinell erkennbar und der wertvollste Rohstoff
für Verbesserungen.

| | |
|---|---|
| **Wo** | lokale Protokolldatei, rollierend begrenzt |
| **Was drin steht** | Quelle, Fehlerart, Muster-Kennung, Zeitpunkt — **keine Dateipfade, keine Titel, keine Namen** |
| **Hochladen** | opt-in, verschlüsselt, mit **Vorschau vor dem Senden** |
| **Wohin** | **eigener Server** — GlitchTip (Sentry-kompatibel, 4 Container statt 40+, läuft auf 2 GB) |
| **Abstürze** | derselbe Weg, mit Stapelspur |

### 12.7 Datenträger einlesen (E47)

⚠️ **Rechtslage Deutschland:** § 95a UrhG verbietet das Umgehen wirksamer technischer
Schutzmaßnahmen (AACS, BD+, Cinavia). § 53 UrhG erlaubt die Privatkopie, aber nicht das
Brechen des Schutzes dafür. Der Widerspruch ist bekannt und gewollt. **JB hat das zur
Kenntnis genommen und für sein autarkes System entschieden** (06.08.2026).

**Bauform — dieselbe Trennung wie beim Quellenkatalog (E12):**

> **SyncFundus entschlüsselt nichts selbst.** Es ruft ein **externes Werkzeug** auf, das der
> Nutzer separat installiert — genau wie ffmpeg, VLC oder Deno.

| Werkzeug | Rolle | Anmerkung |
|---|---|---|
| **MakeMKV** (`makemkvcon`) | **die Wahl** — vollwertige Befehlszeile, Nachbearbeitungs-Haken (nächster Titel wird gerippt, während der vorige weiterverarbeitet wird), Einstellungen in `settings.conf` | ab 1.16.4 deutlich besser bei Java-Playlist-Verschleierung |
| **libmmbd** aus MakeMKV | kann als `libaacs.dll` / `libbdplus.dll` untergeschoben werden, dann lesen auch HandBrake und VLC direkt | Linux: `libbluray`, `libbdplus0`, `libaacs0` |
| ~~AnyDVD HD~~ | ⚠️ **keine Empfehlung mehr** — RedFox-Seite und Software seit Juni 2024 nicht erreichbar | |
| DVDFab u. a. | kommerziell, kostenpflichtig | nur wenn MakeMKV versagt |

**Unsere Seite der Arbeit** (und die ist der eigentliche Wert):
Haupttitel finden über **Laufzeit gegen TMDB** statt über Rätselraten · Spuren und Sprachen
prüfen (§9.4) · Metadaten setzen · als **eine MKV** einlagern, Menü und Werbung weg ·
in die Warteschlange als regulärer Auftragstyp `einlesen`.

Der Installer bekommt dafür ein eigenes Häkchen unter „Fremdsoftware" (§12.2) — nicht
mitgeliefert, nur erkannt und angebunden.

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
| ~~F10~~ | ~~Remixe und Coverversionen~~ → **beantwortet: E96** (JB 07.08.2026 — „Das Lied ist das Werk, dann kommt das Album") | — |
| F11 | **Geräteprofile** für Handhelds (Steam Deck, ROG Ally, …) — selbst pflegen oder von EmuDeck übernehmen? | §6 |
| F12 | **Übergabe an eine zweite KI** — welches Werkzeug für die Abarbeitung (DeepSeek günstig/1M-Kontext, Cursor im Editor, Codex parallel)? Entscheidend ist ohnehin das Pflichtenheft, nicht das Modell | Umsetzung |

---

## 13.1 Wie weit wir sind

**Noch keine Zeile Code — und das ist Absicht.** Was bisher entstand, ist das Pflichtenheft und
elf Entwürfe (siehe `ENTWUERFE.md`). Der Stand nach Bausteinen aus §16.2:

| # | Baustein | Entschieden | Gezeichnet | Gebaut |
|---|---|---|---|---|
| 1 | Register + Werk-Modell | ✅ vollständig | — | ⬜ |
| 2 | Warteschlange | ✅ vollständig | ⬜ | ⬜ |
| 3 | Erkennung + Identität | ✅ vollständig (E48, E76, E87) | teilweise (Erweiterung) | ⬜ |
| 4 | Regal + Startseite | ✅ vollständig | ✅ | ⬜ |
| 5 | Suche | ✅ vollständig | ✅ | ⬜ |
| 6 | Leser | ✅ vollständig | ✅ | ⬜ |
| 7 | Bühne | ✅ vollständig | ✅ | ⬜ |
| 8 | Erweiterung | ✅ vollständig | ✅ | ⬜ |
| 9 | Beschaffung | ✅ Grundsätze, offen: F05, F06 | ⬜ | ⬜ |
| 10 | Veredelung | ✅ Grundsätze, offen: F03, F04, F07 | ⬜ | ⬜ |

**In Zahlen:** 88 Entscheidungen · 12 Regeln der Bauart und des Vertrauens · 11 offene Fragen ·
10 gelernte Fallen · 11 Entwürfe.

**Was als nächstes fehlt, in dieser Reihenfolge:**
1. **Die Werk-Seite** — ohne sie ist die Kette Startseite → Werk → Einheit (E38) nicht belegt.
2. **F10 entscheiden** (Album oder Lied?) — blockiert die gesamte Musikschicht.
3. **Das Postfach** — der Ausgang aus E48/E87 ist beschrieben, aber nie gezeichnet.
4. **Die Warteschlange sichtbar** — §4.5 ist der Motor des Programms und hat noch kein Gesicht.
5. **Zertifikat abschließen** (§12.1) — läuft, siehe Bestellung; braucht Vorlauf vor der
   ersten ausführbaren Fassung.

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
| 2026-08-07 | Fassung 1.1 — E112–E117. **Neu: §5.3.1 Der Grund folgt dem Material** (E114): eigene Farbe darauf ⇒ neutral, nur Schrift ⇒ warm. Damit ist der Leser für **Bilder** von `#1C1611` auf `#0F1012` gewechselt — Braun ließ gescannte Graustufen vergilbt aussehen; für **Text** bleibt es warm, dort war es immer richtig. **E112 Farbe ist die Beschriftung** (grau aus, Akzent an; nie Zustand als Text; Grün bleibt für „läuft/aktiv" reserviert; zweiter Kanal für Farbenblinde). **E113 eigener Zeichensatz** — Spotifys Satz ist geschützt und wir wollen ein eigenes Gesicht; frei sind die Formen (IEC 60417), unsere ist die Strichführung: 24er-Raster, Gleichdick 1,5, gefüllt nur wo Distanz es verlangt, Prüfung bei 16 px und in Graustufen. Entwurf `zeichen.html` mit 28 Zeichen. **E115 kanonische Weiche** am Folgenende (OVA/Folge/Regal) statt blindem Autostart, gespeist aus AniList-Beziehungen, AniDB und TMDB-Staffel 0. **E116 Nur-Ton** für Musikvideos. **E117 Hörbuch „Wo war ich?"** — sekundengenauer Stand mit 30 s Rücksprung, Erkennung des Einschlafens und eine **spoilerfreie Zusammenfassung** bis exakt zur gelaufenen Stelle. **Behoben:** Fernsehknöpfe zu wuchtig; Staffelwahl klappt am PC nach unten aus statt als Vollbild; Musikschalter tragen jetzt Zustandsfarbe. |
| 2026-08-07 | **Fassung 1.0** — E103–E111. **Neu: §5.10.2 Was fest sein muss und was atmen darf** (E103): alles, dessen Beschriftung sich beim Bedienen ändert, bekommt eine feste Breite — Faustregel „ändert sich der Text durch **meine** Handlung → fest, durch den **Inhalt** → frei", mit Tabelle für beide Seiten. **E104** Einstellen ≠ Wählen: Sprache und Fassung in „Ton & Text", Aussehen im Zahnrad — nie im selben Menü. **E105** Klick daneben schließt alles. **E106** bei Ton ohne Bild blendet nichts aus. **E107** Klangzeichen auf Distanz (Klick beim Fokuswechsel, Tock beim Bestätigen; am PC aus). **E108** Hörbücher sind keine Musik — eigenes Regal, Kapitel statt Lieder, kein Zufall, Erkennung über ASIN/M4B/Kapitelmarken. **E109** Herkunft und Güte sind Information, kein Menü — damit ist auch die halb gekaufte, halb gescannte Sammlung **ein** Werk. **E110** das Programm fragt nie, ob du etwas aufgibst; stattdessen ein selbstgesetzter Filter „über N Kapitel gelesen". **E111** Profilwechsel im Menü, nie beim Start. **Behoben:** Untertitel-Panel war gequetscht und überladen — Modus und Sprache sind raus (gehören nach nebenan), Farben in einer Reihe mit 15-px-Punkten, alle Zyklusknöpfe auf feste Breite; Klick daneben schließt jetzt; Musikleiste bleibt stehen und trägt die Aktionen als Symbolreihe; Hörbuch hat eine Kapitelliste; Staffelwechsel am Fernseher über eine Liste statt Scrollen; Endlosstreifen hat gar keine Fußleiste mehr. |
| 2026-08-07 | Fassung 0.9 — **E97–E102.** **Neu: §5.11.2 Der Rahmen** — die Antwort auf JBs wichtigste Frage („wo kommt denn der Ton her?"): *eine Sache hat das Bild, eine den Ton, und beide dürfen verschieden sein*. Klangleiste (46 px statt Spotifys 72–90, Fortschritt als 2-px-Faden, weg wenn nichts läuft), genau ein schwebendes Bildfenster (nie über Leser oder Musikfläche), genau eine Tafel, immer derselbe Bereich. Frei verschiebbare Fenster bauen wir bewusst nicht — der Layout-Editor bleibt im Downloader. **Neu: `Doku/UEBERNAHME_AUS_SYNCYOUTUBE.md` (E102)** mit Datei, Funktionsname und Regel für alles, was portiert wird: das Untertitel-Panel zeilengenau, die Ausschnitt-Favoritenregel, Karaoke, Transkript-Suche, Autotag, Umbenennung mit Probelauf, Geo-Stufen, VPN-Einbahnregel — und was ausdrücklich **nicht** übernommen wird. **Behoben:** Untertitel-Panel war „mau" und jetzt zeilengleich mit `subMenu()`; Ton-&-Text-Wahl schlug nicht auf Kopfzeile und Knopf durch; die Bedienung blendete beim Halten des Spulknopfes weg; Fußleiste lag bei Musik über der Warteschlange; Ausschnitt fehlte bei Musik; Endlosstreifen bekommt die Bildlaufschiene zurück, mit Fortschritt **je Kapitel**; drei Fernsehreihen ohne Bildlaufbalken zur Auswahl. |
| 2026-08-07 | Fassung 0.8 — **E89–E96, F10 geschlossen.** **Musik im vorhandenen Modell:** das Lied ist das Werk, die Aufnahme die Ausgabe, das Album eine Gruppe (§4.2) — MusicBrainz' drei Ebenen fallen genau auf unsere vorhandenen, kein neuer Begriff nötig; Coverversion, Remix, Live-Fassung und DJ-Set lösen sich damit von selbst. **Neu: §5.11.1 Bestandsaufnahme SyncYouTube** (JB-Einwand: „du hast nicht genau hingeschaut, was wir bereits erschaffen haben") — Ausschnitt-Werkzeug, Karaoke mit Romaji, „Auf YouTube öffnen", Mini-Player und Transkript-Suche fehlten im Entwurf und sind jetzt E89–E93; das vorhandene Untertitel-Panel wird übernommen statt neu geschrieben; die Kompakt-Ansicht des Downloaders bestätigt E88 aus dem eigenen Bestand. **E94** Folgen am PC als Raster, am Fernseher als Reihe mit Staffelwand. **E95** ein Ort für den Fortschritt — die angedockte Schiene im Endlosstreifen ist gestrichen, sie war doppelt und liess unten eine halbleere Leiste stehen (JB: „der Bildschirm wird nicht magisch größer"). **Behoben:** Spulen sprang beim Loslassen nochmal 10 s, weil `mouseleave` und `mouseup` beide stoppten; Zahnrad sah aus wie eine Sonne; „Warteschlange" öffnete die Ton-Tafel; Pausenkarte gibt es jetzt für alle drei Gestalten. |
| 2026-08-07 | Fassung 0.7 — **E78–E88.** Neu: **§5.8.1 Titel sind vielsprachig** (kein „richtiger" Titel; Englisch ist keine Leitwährung; Romanisierungen normalisiert vergleichen; Titelvorrat wächst nur) und **E87 nie früh verwerfen** — Falsch-Behalten schlägt Richtig-Wegwerfen. **§5.10.1 Kachelgrößen:** die Mini-Kachel ohne Titel ist gestrichen (JB: „dann sehe ich nicht, welchen Manga ich lese") — Titel ist Rang 1 der Prioritätsleiter und fällt nie; stattdessen „Dicht" mit einzeiligem Titel. **Bühne erweitert:** 10 s tippen / halten spult mit 4×–12×–30× (Vergleich Netflix, Plex, Jellyfin, Kodi, Prime, VLC, mpv) · Bedienung liegt im Bild und blendet weich weg (420 ms raus, 120 ms rein) · Pausenkarte nach 12 s mit Rollenzeile, nie Empfehlungen · „Ton & Text" statt „Spuren", Einstellen vom Auswählen getrennt (Zahnrad) · Folgen unter der Bühne. **Suche:** erweiterte Suche zugeklappt mit Zähler, dieselbe Dreistufigkeit, und **das kluge Regal** (gespeicherte Suche wird Regal). **E85 Zahlentypografie:** die Luft gehört dem Trenner, ausgerichtet mit Ziffernleerzeichen, Füllbreite aus der aktuellen Ansicht — damit hören vierstellige Kapitel auf, am Schrägstrich zu kleben. **Neu: §13.1 Wie weit wir sind** und **`Doku/ENTWUERFE.md`** als Index der elf Entwürfe. Drei weitere Fallen in §5.11 (`visibility` reserviert Platz · Maßstab am falschen Element · Zellbreite trägt den Abstand). |
| 2026-08-07 | Fassung 0.6 — **E72–E77.** Neu: **§5.12 Die Bühne** (Video, Musik, Hörbuch auf einer Fläche; die Leiste als Landkarte der Folge; wer welche Untertitel zeichnet; feste Gamepad-Belegung; der Übergang Hören ↔ Lesen). **§8.4 um E76 erweitert:** wie die Erweiterung dasselbe Werk auf verschiedenen Seiten, unter anderen Titeln, von anderen Gruppen und mit anderer Kapitelzählung wiedererkennt — die Adresse ist ein Hinweis, nie ein Beweis. **E58 verschärft:** Leserichtung hat zwei Achsen (Fluss + Achse); Chinesisch ist der Sonderfall, weil Webtoon und gebundener Band verschieden laufen. **JB-Funde:** „Spieler" war zweideutig → **Bühne**, das Wort kommt auf die Verbotsliste des Text-Wächters (Dokument durchgesehen und umgestellt) · „gesamt" hieß fälschlich Endstand → **erschienen**, drei Zahlen, alle echt · `…` statt `?` · Geführt-Modus zoomte nicht, sondern verkleinerte den Text (Einpassen hebt Zoom auf). Drei neue Fallen in §5.11. |
| 2026-08-07 | Fassung 0.5 — **E53–E71.** Neu: **§5.8 Die Suche** (ein Feld, zwei Gruppen, drei Zustände, dreistufige Filter, Zusammenführungsregeln, die sieben Entnerv-Regeln) · **§5.9 Der Leser** (Leserichtung als Eigenschaft der Ausgabe, ein Griff mit zwei Gedächtnissen, keine Restzeit beim Lesen) · **§5.10 Schrift und Zeichen** (Inter/Literata/Atkinson/JetBrains Mono; ▶ vs. Lesezeichen-Pfeil; zwei Farbskalen; Wortabzeichen statt Emoji; die Kapitelzelle) · **§5.11 Gelernte Fallen** (sieben Fehler, die in dieser Sitzung wirklich passiert sind) · **§8.4 Die Browser-Erweiterung** (vier Knopfzustände, drei Eingriffe je Seite, nur `127.0.0.1`, Adapterliste lokal). Die „zehn unverhandelbaren" aufgeteilt in **zehn Regeln der Bauart** und **vier Regeln des Vertrauens** — die alte Zehnerliste bleibt unverändert. Entwürfe: `suche.html`, `erweiterung.html`; `leser.html` und `regal.html` überarbeitet. **JB-Funde:** geteilter Regler zwischen Zoom und Schriftgröße · „Kapitel 88 von 122" war zweideutig · 🖐-Emoji unlesbar · Restdauer beim Lesen setzt unter Druck. |
| 2026-08-07 | Fassung 0.4 — **Name entschieden: SyncFundus** (der Fundus ist im Theater und Film der Bestand, aus dem man schöpft). Datei umbenannt. E46–E52: Meilensteine nur einmal · Blu-ray über externes Werkzeug einbinden statt selbst entschlüsseln · **genau ein Ausgang pro Datei** (JB-Einwand gegen kaskadierende Regeln — berechtigt, Modell vereinfacht) · Fehlerprotokoll lokal/verschlüsselt/opt-in · GPU nachgebend · Anmeldungen erneuern sich still · deterministischer Kern. Warteschlange um die drei Fehlerarten und vergiftete Aufträge erweitert. Qualitätsnetz um die extreme Stufe erweitert (JB: „machen"). **Neu: §16 Übergabe an eine zweite KI** mit verbindlicher Baureihenfolge. **Neu: die zehn unverhandelbaren.** Aufgeräumt: §12.6 war falsch eingerückt, §5.6/5.7 neu geordnet. |
| 2026-08-06 | Fassung 0.3 — E34–E45: **kein zweites Fenster** (der Motor liefert Pixel, wir liefern die Bedienung) · Navigation mit Seitenleiste, vier Sichtbarkeits-Stufen, Tiefenregel Ebene-vs-Tafel · Container ersetzt Ordner · Regal „Eigenes" · Vorschlagen statt Verändern · Qualitätsnetz mit Layout- und Text-Wächter · Titel-Schema als Rollen · Live-TV ja / Live-Sport nein · die Suche ist die Anforderung. Blu-ray-Playlist-Verschleierung dokumentiert. F11–F12 eröffnet. **JB-Korrektur:** Big Picture ist *nicht* die Vorlage für den Fernsehmodus — die Steam-Deck-Oberfläche und EmulationStation sind es. |
| 2026-08-06 | Fassung 0.2 — E25–E33 ergänzt: Spieler-Motor (libmpv/libVLC), Plattform-Offenheit über HTTP-Schnittstelle, Ordnerkonventionen und Pfadhaltung, Umbenennungsregeln, Mängel-Deklaration, Titel-Zuordnung mit gewichteten Zeugen, Export als Grundrecht, Spiele über Playnite. **F01 beantwortet** (§12.4). Zwiebel um DJ-Sets, Sportevents, Spiele/Emulatoren, physische Sammlung erweitert. **Korrektur:** winget verleiht kein Vertrauen (§12.1). |
| 2026-08-06 | Fassung 0.1 — Startschuss. E01–E24 festgehalten, F01–F10 eröffnet. Grundlage: Brainstorming-Sitzung JB + Claude, mit Recherche zu Marktlage, Farbforschung, WCAG, *arr-Stand, TTS-Stand, Signaturlage, MangaDex-Verfügbarkeit, Cloudflare-Umgehung. |

---

## 16. Übergabe an eine zweite KI

Dieses Dokument ist das Pflichtenheft. Der Bau soll von einem zweiten Agenten ausgeführt
werden; hier stehen die Bedingungen dafür.

> ⚠️ **Die Übergabequalität hängt am Pflichtenheft, nicht am Modell.** Eine vage Vorlage
> lässt keinen Agenten arbeiten, eine gute lässt jeden fähigen arbeiten.

### 16.1 Voraussetzungen

1. **Dieses Dokument vollständig lesen**, bevor eine Zeile geschrieben wird.
2. **Superpowers-Plugin installieren** (JB-Vorgabe 06.08.2026):
   `/plugin install superpowers@claude-plugins-official` — die Brainstorming-Fertigkeit
   verfeinert Aufgaben durch Rückfragen, bevor gebaut wird.
3. **Code-Signatur-Zertifikat muss vorhanden sein**, bevor die erste ausführbare Fassung
   entsteht (§12.1) — die Reputation baut sich am Zertifikat auf und braucht Vorlauf.

### 16.2 Verbindliche Reihenfolge

| # | Baustein | fertig, wenn |
|---|---|---|
| 1 | **Register + Werk-Modell** (§4.2–4.4) | die vier Eigenschaften aus §12.6 grün sind |
| 2 | **Warteschlange** (§4.5) | die drei Fehlerarten getrennt behandelt werden und „Steckengeblieben" sichtbar ist |
| 3 | **Erkennung + Identität** (§8) | genau ein Ausgang pro Datei (E48), Postfach funktioniert |
| 4 | **Oberfläche: Regal + Startseite** (§5.1, §5.8–5.11) | Layout-Wächter bei 360/834/1280/3440 grün |
| 5 | **Suche** (§5.8) | drei Zustände sichtbar, Zusammenführung greift, Filter dreistufig |
| 6 | **Leser** (§5.9) | Papier/Nacht-Modi · Leserichtung dreht **alles** mit · Fortschritt zweistufig |
| 7 | **Bühne** (§5.12 · libmpv in eigener Fläche, E34/E35) | kein zweites Fenster, Steuerung ist unsere, drei Gestalten laufen |
| 8 | **Erweiterung** (§8.4) | markiert zurück, spricht nur mit `127.0.0.1` |
| 9 | **Beschaffung** (§9) | Echtheitsprüfung läuft vor jedem Einlagern |
| 10 | **Veredelung** (§10) | Werk-Wissen trägt Übersetzung *und* Vertonung |

**Nichts aus Stufe N+1 beginnen, solange N nicht fertig ist.** Der Grund steht in §14.

### 16.3 Arbeitsregeln für den Agenten

- **Die zehn unverhandelbaren** (§3) sind nicht verhandelbar. Wer eine davon brechen will,
  fragt JB — und ändert sie im Dokument, bevor er baut.
- **Kein Baustein gilt als fertig**, bevor er bei 360/834/1280/3440 px geprüft ist (§5.2).
- **Jede Entscheidung, die dieses Dokument nicht abdeckt**, wird als neue E-Nummer mit
  Begründung eingetragen — nicht stillschweigend getroffen.
- **Deterministischer Kern (E52) ab der ersten Zeile.** Nachträglich einzuziehen ist teuer.
- **Standardformate ab der ersten Zeile** (E06) — ein eigenes Format zu ersetzen ist teurer
  als eines zu vermeiden.

### 16.4 Code-Übernahme (E102)

**JB-Vorgabe 07.08.2026:** *„Wenn wir Code übernehmen, muss der Code klar dokumentiert sein.
Ich werde eine andere KI coden lassen, die wird Zugriff auf alle unsere Programme haben."*

Deshalb: **`Doku/UEBERNAHME_AUS_SYNCYOUTUBE.md`** — mit Datei, Funktionsname und der Regel
dahinter. Zwei Grundsätze:

1. **Wo SyncYouTube etwas gelöst hat, wird portiert, nicht nachgebaut.** Nachbauen heißt,
   dieselben Fehler zweimal zu machen.
2. **Die Kommentare kommen mit.** Wo im Quellcode *„JB"* und ein Datum steht, steckt ein echter
   Fehler aus dem Betrieb dahinter. Diese Kommentare werden **nicht wegoptimiert** — sie sind
   der eigentliche Wert.

### 16.5 Wo die Wahrheit steht

| | |
|---|---|
| Bauplan | **dieses Dokument** |
| Was zuletzt beschlossen wurde | §15 Änderungsverlauf |
| Was noch offen ist | §13 |
| Was das Vorhaben tötet | §14 |
| Bestehender Code als Vorlage | `schn4ppi/SyncYouTube` (Server, Warteschlange, Oberfläche, Geräte) und `schn4ppi/SyncManga` (Anreicherung, Overrides, Linkgesundheit) |

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
