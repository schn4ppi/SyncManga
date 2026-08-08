# SyncFindus — Vision & Fundament

> **Arbeitstitel.** Der Nachfolger von SyncManga und SyncYouTube: **ein** Programm für
> Anime, Manga, Novels, Musik, Hörbücher, Filme und Serien — mit eigener Bibliothek,
> eigenem Leser, eigener Bühne, eigener Veredelung.
>
> **Stand:** 2026-08-08 · **Fassung:** 1.16 · **Pflege:** JB + Claude

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
6. **Die Außenwelt wird wöchentlich nachgeprüft** (JB, 08.08.2026). Quellen haben eine
   Halbwertszeit von Wochen, Werkzeuge von Monaten — dieses Dokument von Jahren. Die
   Prüfliste steht in **`PFLEGE.md`** und wird dort protokolliert, **nicht in einem Chat**.
   *Ein Chat endet, die Datei nicht.*

**Die Begleitdateien:**

| Datei | Wofür |
|---|---|
| `ENTWUERFE.md` | welche Entwürfe es gibt und was noch fehlt |
| `NICHT_UEBERNOMMEN.md` | ⚠️ **was aus SyncManga und SyncYouTube noch fehlt** — wird abgearbeitet, bis sie leer ist |
| `PFLEGE.md` | **die wöchentliche Prüfung** — was neu ist, was ersetzt wurde, was gestorben ist |
| `UEBERNAHME_AUS_SYNCYOUTUBE.md` | welcher Code wörtlich übernommen wird, mit Datei und Funktion |

**Statuszeichen:**

| | Bedeutung |
|---|---|
| ✅ | entschieden, begründet, recherchiert |
| 🟡 | Richtung klar, Feinheiten offen |
| ❓ | offene Frage — in §13 gelistet |
| ⚠️ | bekanntes Risiko |
| 🔑 | tragende Entscheidung — Umwurf zieht viel nach sich |

---

## 1. Was SyncFindus ist

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
| E118 | Bühne | **Ton ohne Bild ⇒ Leiste gehört zum Raum**, Film ⇒ Leiste ist Überzug | 🔑✅ |
| E119 | Bühne | Weiche: **30 s Grundzeit + 10 s je Wahl** — man muss die Fernbedienung erst finden | ✅ |
| E120 | Werk | **Reihen und Universen** — kanonische Ordnung gilt auch für Filme | 🔑✅ |
| E121 | Oberfläche | **Höhen werden gemessen, nie geraten** — keine magische Zahl für eine Leiste | 🔑✅ |
| E122 | Oberfläche | **Gestuftes Aufgeben** — Inhalt fällt in fester Reihenfolge weg, statt überzulaufen | ✅ |
| E123 | Sammlung | **Playlist ist eine Sicht, keine Kopie** — Sammlung wie jede andere, `.m3u` als Export | ✅ |
| E124 | Bühne | **Besetzungskarte** rechts bei Pause — nie ins laufende Bild | ✅ |
| E125 | Oberfläche | **Freie Fläche ist kein Fehler** — sie wird nicht gefüllt, nur geordnet | 🔑✅ |
| E126 | Musik | **Drei Anordnungen** (Bühne · Mitte · Text), je Gerät gemerkt | ✅ |
| E127 | Oberfläche | **Rechtsklick: max. 7 Zeilen, ein Trennstrich**, nie doppelt zum Knopf | ✅ |
| E128 | Empfehlung | **Radio ≠ Zufall** — drei getrennte Begriffe, drei getrennte Knöpfe | ✅ |
| E129 | Quellen | **Kein Streaming-Konto als Quelle** — Spotify/SoundCloud nur als Wissen | 🔑✅ |
| E130 | Oberfläche | **Nichts scrollt, was eine Bühne ist** — es gibt nach, es rollt nicht | 🔑✅ |
| E131 | Oberfläche | **Ein Knopf, eine Bedeutung** — kein Etikettwechsel auf gleicher Handlung | 🔑✅ |
| E132 | Oberfläche | **Angebote schließen sich aus** — nie zwei Aufforderungen im selben Bild | ✅ |
| E133 | Oberfläche | **Nichts steht zweimal im Bild** — trägt der Inhalt den Titel, trägt der Kopf die Herkunft | ✅ |
| E134 | Übersetzung | **Englisch zuerst, Deutsch aus dem Englischen** — der zweite Lauf erbt das Glossar | 🔑✅ |
| E135 | Übersetzung | **Das Glossar schlägt jedes Modell** — Beständigkeit vor Klugheit | 🔑✅ |
| E136 | Übersetzung | **Blasenprüfung**: passt der Satz nicht, ist er falsch — Platz schlägt Schönheit | 🔑✅ |
| E137 | Übersetzung | **Sprichwörter: drei Wege**, die Verortung entscheidet — nie stumm verpflanzen | ✅ |
| E138 | Vertonung | **Stimmen sichtbar** — höchstens drei Marken, dann „+ N weitere" | ✅ |
| E139 | Werk | **Eine Anordnung, ein Band das wechselt** — der Aufmacher bleibt, nur eine Zeile darin ändert sich ⟳ | 🔑✅ |
| E140 | Quellen | **Die Güte wird gemessen, nicht geglaubt** — eine Stufenleiter S–D für alle Medien | 🔑✅ |
| E141 | Erkennung | **Das Postfach wächst nie stumm** — sichtbar, Standardausgang, Regel aus Wiederholung | 🔑✅ |
| E142 | Warteschlange | **Bündeln nach Werk, nicht nach Auftrag** — der Auftrag ist die Einheit des Systems | ✅ |
| E143 | Warteschlange | **Drei Fragen je Zeile** — was tut sie, worauf wartet sie, was bei Fehlschlag | 🔑✅ |
| E144 | Werk | **Beziehungen sind gerichtet und benannt** — ein ungerichtetes „ähnlich" ist wertlos | ✅ |
| E145 | Erkennung | **Der Browser ist ein Zeuge, kein Gedächtnis** — gelöschter Verlauf ändert nichts | 🔑✅ |
| E146 | Zustand | **Der Zustand hängt nie an der Identität** — Schlüssel ist die ID, nie der Titel | 🔑✅ |
| E147 | Qualität | **Der Bruchtest** — bei jedem Beenden still eine Invariante prüfen | ✅ |
| E148 | Empfehlung | **Der Kalender empfiehlt, die Bilanz nicht** — Jahreszeit statt Jahresrückblick | ✅ |
| E149 | Beschaffung | **Ein Rennen, kein Auftrag** — alle Kandidaten treten an, Vorprüfung kostet keine Bytes | 🔑✅ |
| E150 | Beschaffung | **Der Wunsch stirbt nie** — ein Auftrag scheitert, ein Wunsch lauert | 🔑✅ |
| E151 | Zustand | **Das Register ist die Wahrheit, die Anzeige eine Sicht** — nie ein Speicher | 🔑✅ |
| E152 | Oberfläche | **Eine Leiste endet vor dem Streifen** — oben wie unten, nie darüber | ✅ |
| E153 | Oberfläche | **Eine Tafel ist eine Tabelle** — beide Kanten stimmen, gleiche Zellen je Zeile | ✅ |
| E154 | Ton | **Musik-Lücke = Zahl, Hörbuch-Lücke = Defekt** — zwei Regale, nicht eins | 🔑✅ |
| E155 | Auslieferung | **Pflicht wird gezeigt, nicht versteckt** — Haken gesetzt und ausgegraut, mit Grund | 🔑✅ |
| E156 | Netz | **Ohne Netz steht die Uhr** — bei Rückkehr läuft alles seit dem Bruch als Nachtrag | 🔑✅ |
| E157 | Zeit | **Eine Uhr: deine** — alles nach Berliner Zeit, Herkunftszeit nur als Fußnote | ✅ |
| E158 | Profile | **Das Alter entscheidet** — eine Zahl statt einer Häkchenliste | ✅ |
| E159 | Spiele | **Die Einstellung gehört zum Spiel**, nicht zum Emulator — drei Ebenen mit Herkunft | 🔑✅ |
| E160 | Empfehlung | **Die Lücken-Liste ist der Eingang zur Beschaffung**, kein Bericht | 🔑✅ |
| E161 | Profile | **Ein Rechner hat Vorrang** — wer davorsitzt, gewinnt | ✅ |
| E162 | Übernahme | **SyncManga ist Lehrer, nicht Vorgänger** — kein Umzug als Pflicht | 🔑✅ |
| E163 | Quellen | **Der Katalog verlässt das öffentliche Repo** — F05 entschieden | 🔑✅ |
| E164 | Meldung | **Es meldet sich nur, wenn du sonst etwas verlierst** — drei Anlässe, mehr nicht | ✅ |
| E165 | Oberfläche | **Sofort der Rand, nach 400 ms das Band** — Hover hilft, drängt nicht | ✅ |
| E166 | Sicherung | **Zwei Ringe: gegen unsere Fehler, gegen den Verlust des NAS** ⟳ | 🔑✅ |
| E167 | Sprache | **Zwei gepflegte Sprachen, alle anderen sind eine Datei** | ✅ |
| E168 | Ablage | **Löschen geht in den Papierkorb** — nie endgültig, nie ohne Rückweg | 🔑✅ |
| E169 | Fundament | **Ein Werk kann fern liegen** — ein Medienserver ist ein Ort, keine Quelle | 🔑✅ |
| E170 | Fortschritt | **Er fließt in beide Richtungen** — und was nicht ankam, wird nachgereicht | 🔑✅ |
| E171 | Register | **Eine Registerdatei, ein Programm** — Einzelinstanz ist Pflicht, nicht Komfort | 🔑✅ |
| E172 | Auslieferung | **Prüfen vor dem Tausch** — `.bak`, atomar, nie löschen | 🔑✅ |
| E173 | Qualität | **Heilen ist die zweite Hälfte des Bruchtests** — jeder Fund kennt seinen Vorschlag | 🔑✅ |
| E174 | Ablage | **Der Wachordner** — was hineinfällt, wird ein Werk, ohne dass jemand klickt | ✅ |
| E175 | Oberfläche | **Das Programm zeigt sich im Infobereich** — Zustand ohne Öffnen | ✅ |
| E176 | Profile | **Inhaltsfilter für Erwachsene** — nicht dasselbe wie ein Kinderprofil | ✅ |
| E177 | Erkennung | **Was der Mensch bestätigt, wiegt schwerer als was wir messen** | 🔑✅ |
| E178 | Werk | **Sechs Lesezustände** — „lange pausiert" ist die wichtigste Erfindung darunter | ✅ |
| E179 | Fundament | **LANoMAT: fremde Bibliotheken sind Orte, keine Konten** — Fortschritt bleibt daheim | 🔑✅ |
| E180 | Beschaffung | **Eine Anfrage ist ein Wunsch über eine Grenze** — drei Kontexte, ein Mechanismus | 🔑✅ |
| E181 | Fortschritt | **Er gehört einem Profil, nicht einem Ort** — wer sonst streamt, existiert nicht | 🔑✅ |
| E182 | Fortschritt | **Eine Menge, keine Zahl** — je Einheit drei Zustände, also nie ein Konflikt | 🔑✅ |
| E183 | Fortschritt | **Geöffnet ist nicht gesehen** — Schwellen, und „das war ich nicht" | 🔑✅ |

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

### 4.2.1 Die Werk-Seite (E139, E144)

> **Entwurf:** `werkseite.html` — drei Anordnungen zum Anklicken, vier Medien im selben Rahmen.

Die Werk-Seite ist der Knotenpunkt: Startseite → **Werk** → Einheit (E38). Sie ist die
Probe aufs Datenmodell — **ist sie für Film und Manga verschieden, war das Modell falsch.**
Nur die Wörter wechseln, nie die Kästen.

| Block | Manga | Anime/Serie | Film | Album |
|---|---|---|---|---|
| **Identität** | Titel EN + JP, Typ, Jahr, Status | dito + Studio | dito + Regie | Künstler, Label |
| **Fortschritt** | 1141 / 1148 Kapitel | Folge 8 / 28 | 0:47 / 2:46 | zuletzt gehört |
| **Die eine Tat** | Weiterlesen | Weitersehen | Weitersehen | Weiterhören |
| **Gruppen** | Bände / Arcs | Staffeln | *(eine)* | Discs |
| **Einheiten** | Kapitel | Folgen | der Film | Titel |
| **Ausgaben** | Scan-Gruppen, Bände | Fassungen, Sprachen | Kino / Extended | CD · Vinyl · Remaster |
| **Beziehungen** | Vorgänger, Ableger, Anime | Vorlage, OVA, Film | Reihe, Universum | Vorgänger, Live |
| **Herkunft** | *identisch für alle vier* — woher, wann geprüft, was fehlt (E17, E50) |||| 

**Die vierte Sprosse rettet den Film.** Sammlung → Gruppe → Einheit → Position gilt auch da,
wo sie sinnlos wirkt: ein Film ist eine **Gruppe mit genau einer Einheit**. Deshalb braucht die
Werk-Seite keinen Sonderfall — sie blendet die leere Sprosse aus, wie sie beim Manga ohne
Bände die Bandzeile ausblendet. *Sonderfälle im Modell werden zu Sonderfällen in jeder
Ansicht, für immer.*

**E139 — eine Anordnung, ein Band das wechselt** *(überarbeitet 08.08.2026 nach JB-Einwand)*.
Drei Anordnungen wurden gezeichnet. **JB wählte A** und stellte dabei die Frage, die meinen
ersten Entwurf umgeworfen hat: *„Wenn du sagst, wir sollen die gleiche Oberfläche haben, dann
widersprichst du dir doch, oder?"*

| | Was oben steht | Urteil |
|---|---|---|
| **A · Das Bild** | Aufmacher 21:8, Titel im Bild | ✅ **die Anordnung** |
| **B · Die Akte** | Titelbild 104 px, sofort Zahlen | keine eigene Anordnung — **A unter 700 px** (E39) |
| **C · Der Faden** | wo du warst, was seitdem kam | ❌ verworfen; sein guter Gedanke lebt **in A** weiter |

**Der Einwand sitzt, und hier ist der ehrliche Unterschied.** *Dieselben Kästen über alle
Medien* ist eine Aussage über das **Datenmodell** — sie kostet nichts und ist immer richtig.
*Verschiedene Anordnungen je nach Zustand* ist eine Aussage über das **Verhalten** — und die
kostet Lernbarkeit. Ich hatte die zweite mit der Autorität der ersten begründet. Das war
falsch: **eine Seite, die sich umbaut, ist eine Seite, die man nicht lernen kann.**

> 🔑 **Der Aufmacher bleibt immer stehen. Der Fortschritt entscheidet nur, was in einer
> einzigen Zeile darin steht** — Herkunft oder Faden. Gleicher Ort, gleiche Höhe, anderer
> Inhalt. Nichts springt, nichts baut sich um, und die Seite ist nach dem zweiten Besuch
> auswendig gelernt.

| Medium | Zeile ohne Fortschritt | Zeile mit Fortschritt |
|---|---|---|
| Manga | *Manga · JP · 1997 – läuft · Eiichiro Oda* | *Du warst hier · Kapitel 1141 „Der Wille des D." · 7 neu* |
| Anime | *Anime · JP · 2023 · Madhouse* | *Du warst hier · Folge 8 · Folge 9 ist seit 2 Tagen da* |
| **Film** | *Film · US · 2024 · Villeneuve · 166 min* | *Du warst hier · bei 0:47:12 — Die Reiterprüfung · noch 1 h 59* |
| Album | *Album · FR · 2013 · Daft Punk · Columbia* | *Zuletzt gehört · Titel 7 „Touch" · 6 nie gehört* |

Ein Film hat kein „nächstes Kapitel" — also trägt das Band dort die **Zeitmarke**. Dieselbe
Zeile, dieselbe Höhe, eine andere Sorte Auskunft. Das ist der Unterschied zwischen *dieselbe
Seite* und *dasselbe Bild*.

**E144 — Beziehungen sind gerichtet und benannt.** *Vorlage · Adaption · Vorgänger ·
Nachfolger · Ableger · Neuauflage · Reihe · Universum.* Ein ungerichtetes „ähnlich" wäre
wertlos, weil es die eigentliche Frage nicht beantwortet: **was fasse ich als Nächstes an?**
Die Richtung kommt aus AniList/TMDB/MusicBrainz (E120) — gebaut wird sie nicht.

#### E125 — Freie Fläche ist kein Fehler

**JB, 07.08.2026:** *„Versuch nicht Sachen zu verdecken. Es muss doch freie Flächen erkennbar
geben, oder?"* — Ja. Und das ist eine Regel, keine Geschmacksfrage.

> **Leerraum wird nicht gefüllt, sondern geordnet.** Was in eine Ecke wandert, nur weil sie leer
> ist, ist immer das Falsche — es steht dort ohne Grund und wird nie gesucht.

Deshalb gilt in jeder Anordnung dieselbe Rangfolge, und **Rang 4 darf verschwinden** (E122):

| Rang | Was |
|---|---|
| 1 | **Was läuft** — Titel, Cover, Werk |
| 2 | **Wo im Stück** — Leiste, Zeit |
| 3 | **Was kommt** — Warteschlange, nächste Folge |
| 4 | alles andere — Karaoke, Abzeichen, Zusatzknöpfe |

⚠️ Zwei Fehler, die dabei gleich schlimm sind: eine **tote Ecke**, weil ein Bauteil zu früh
aufhört (die Warteschlange endete über der Leiste statt an der Unterkante) — und **etwas
Hineingestopftes**, damit es nicht leer aussieht. Das erste ist Schlamperei, das zweite Absicht.

#### E126 — Drei Anordnungen für Musik

Spotify, Apple Music und YouTube Music haben **alle drei** — sie nennen sie nur nicht so und
verstecken sie hinter verschiedenen Knöpfen. Der Fehler wäre, sich für eine zu entscheiden.

| | Vorbild | Wofür |
|---|---|---|
| **A · Bühne** | Apple Music Vollbild, Tidal | der Alltag: Cover links, Warteschlange rechts — was läuft *und* was kommt, ohne Klick |
| **B · Mitte** | Spotify Vollbild, YouTube Music | wenn das Cover das Erlebnis ist. Ruhiger, Warteschlange aufklappbar. Gut am Fernseher |
| **C · Text** | Apple Music Lyrics | zum Mitsingen: Liedtext füllt die Fläche, bei Japanisch **mit Romaji darunter** — das kann sonst niemand |

**Gemerkt wird je Gerät, nicht je Titel** — die Ansicht hängt an der Situation (Schreibtisch,
Fernseher, Handy), nicht am Lied.

#### E127 — Der Rechtsklick

| Regel | |
|---|---|
| **Höchstens 7 Zeilen** | wird es mehr, fehlt eine Ebene, nicht eine Zeile |
| **Höchstens ein Trennstrich** | braucht es zwei, sind es zwei Menüs |
| **Nie doppelt zum Knopf** | was sichtbar geht, steht nicht im Menü — außer es ist der einzige Weg auf Distanz |
| **Die obersten zwei Zeilen** | sind die 90-Prozent-Fälle; der Rest darf länger dauern |
| **Überall dasselbe Muster** | Haupthandlung · Zustand ändern · ─ · Vertiefen · Weggeben |

Vollständige Menüs: siehe Entwurf `buehne.html`.

#### E128 — Radio ist nicht Zufall

Drei verschiedene Dinge, drei getrennte Knöpfe, nie vermischt:

| | Was es tut | Vorbild |
|---|---|---|
| **Zufall** | mischt **deine** Warteschlange — gestreut, nie zweimal derselbe Urheber hintereinander | Spotifys Shuffle (den sie 2014 bewusst *un*zufälliger gemacht haben, weil echte Zufälligkeit Häufungen erzeugt und sich falsch anfühlt) |
| **Radio** | spielt endlos weiter mit **Ähnlichem aus deiner Bibliothek**, wenn die Warteschlange leer ist | Spotifys *Smart Shuffle* mit dem Stern — nur dass deren Vorschläge aus dem Katalog kommen und unsere aus dem Regal |
| **Entdecken** | sucht **draußen**, filtert alles heraus, was du schon hast | SyncYouTubes ✨ Entdecken |

Der Unterschied, der zählt: **Zufall ordnet um, Radio hängt an, Entdecken holt herein.**

#### E123 — Wo Playlists leben

Eine Playlist ist **kein Sonderfall**, sondern eine **Sammlung** — dieselbe Sprosse der Leiter
(§4.3), auf der auch ein Regal steht. Deshalb braucht sie keine eigene Verwaltung.

| | |
|---|---|
| **Gelistet** | in der Seitenleiste **unter „Musik"**, eingerückt — wie Staffeln unter einer Serie |
| **Gespeichert** | je Profil eine Datei im Profilordner. Nichts in der Cloud, nichts in einer unlesbaren Datenbank |
| **Angelegt** | drei Wege ohne Dialog: Titel in die Warteschlange ziehen · *Als Playlist* · oder eine gespeicherte Suche (**das kluge Regal**, E78) |
| **Exportiert** | `.m3u` — jedes Programm der Welt liest es (E06). Import genauso |
| **Abgeglichen** | auf Wunsch gegen eine echte Playlist beim Anbieter, wie `playlist_sync()` es im Downloader schon tut |
| ⚠️ **Nicht** | kein zweiter Ort für „meine Musik". Eine Playlist ist eine **Sicht** auf die Bibliothek, keine Kopie |

#### E154 — Zwei Regale für Ton

> **Entwurf:** `regale.html`, Reiter *Musik* und *Hörbuch*.

**JB, 08.08.2026:** *„Es sollte zwei Regale geben. Musik ist nicht Hörbuch, auch wenn es Audio
ist. Ein Hörbuch ist nur gesamt zu gebrauchen — ich brauche kein Hörbuch, wo der dritte Track
fehlt. Bei Musik sind Alben nicht vollständig wichtig, das Lied zählt."*

> 🔑 **In der Musik ist eine Lücke eine Zahl. Im Hörbuch ist eine Lücke ein Defekt.**
> Aus diesem einen Satz folgt jede weitere Unterscheidung — es ist keine Geschmacksfrage,
> sondern eine über die **Brauchbarkeit** des Gegenstands.

| | Musik | Hörbuch |
|---|---|---|
| **Was zählt** | das **Lied** | das **ganze Werk** |
| **Eine Lücke ist** | eine graue Zahl („9 von 14") | ein **Defekt** — rot, mit eigenem Knopf |
| **Grundform** | quadratische Kacheln, dicht (132 px) | Zeilen mit 2:3-Rücken und Balken |
| **Sortierung** | zuletzt gehört | angefangen zuerst |
| **Reihenfolge** | egal — **Zufall ist ein Feature** | heilig — **es gibt keinen Zufall** |
| **Fortschritt** | gibt es nicht (man hört Alben nicht „zu Ende") | der wichtigste Wert überhaupt (E117) |
| **Gruppe** | Album = Sortierhilfe | Reihe/Band = echte Ordnung |
| **Wer spricht** | Künstler | **Sprecher** — eigene Sortierung wert (E138) |
| **Vorrat holen** | einzelne Lieder | **nie einzelne Kapitel** — immer der ganze Titel |

**Der Vollständigkeitsbalken ist segmentiert, nicht prozentual.** Ein Prozentwert („92 %")
verschweigt, **wo** das Loch sitzt. Ein Loch in Kapitel 3 von 12 ruiniert den Abend nach
vierzig Minuten; ein Loch in Kapitel 47 von 48 ist ärgerlich, aber später. **Segmente zeigen
den Unterschied, Prozente verstecken ihn.**

**Folge für die Beschaffung:** Ein Hörbuch ist **ein** Wunsch (E149) — erfüllt erst, wenn
*alle* Kapitel da sind; fehlt eines, lauert der Wunsch weiter (E150), auch bei 11 von 12. Bei
Musik ist jedes Lied ein eigener Wunsch, und elf erfüllte von vierzehn sind schlicht elf
erfüllte Wünsche.

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

#### E120 — Reihen und Universen

**JB, 07.08.2026:** *„Gilt das auch für Filme? Marvel, Herr der Ringe? Was ist mit
übergreifenden Universen?"* — Ja, und es ist dieselbe Mechanik wie bei OVAs, nur eine Ebene höher.

Wir bauen **keinen** eigenen Beziehungsgraphen (§14, Todesursache 2) — wir nutzen die
vorhandenen und legen **eine** eigene Schicht darüber: die **Ordnung**.

| Ebene | Was | Woher |
|---|---|---|
| **Werk** | *Iron Man*, *Die Gefährten*, *Vinland Saga S2* | vorhanden |
| **Reihe** | *Der Herr der Ringe*, *Vinland Saga* | TMDB `collection`, AniList `PARENT/SEQUEL` |
| **Universum** | MCU, Mittelerde, Star Wars, das Nasuverse | TMDB-Sammlungen + Wikidata; für Anime **AniDB** und die AniList-Beziehungsketten |
| **Ordnung** | *in welcher Folge man das ansieht* | **unsere Schicht** — eine kleine Liste je Universum |

**Drei Ordnungen, umschaltbar** — und das ist der eigentliche Nutzen, weil bei genau diesen
Reihen seit Jahrzehnten gestritten wird:

| Ordnung | Beispiel |
|---|---|
| **Erscheinung** | wie es herauskam. MCU: *Iron Man* zuerst. Star Wars: Episode IV zuerst |
| **Kanonisch/Chronologisch** | wie die Geschichte spielt. MCU: *Captain America* zuerst. Herr der Ringe: *Der Hobbit* zuerst |
| **Empfohlen** | die gepflegte Mischform (bei Star Wars die „Machete-Reihenfolge", bei Anime die Fan-Watch-Order) |

**Regeln:**
1. Die Ordnung ist eine **Eigenschaft des Universums**, nicht des Werks — ein Film kann in
   mehreren Universen stehen (Crossover) und dort verschiedene Plätze haben.
2. Am Ende eines Films greift dieselbe **Weiche** (E115/E119) wie am Folgenende: *„Als Nächstes
   nach kanonischer Ordnung: …"* mit den Alternativen daneben.
3. ⚠️ **Nie automatisch quer durchs Universum starten.** Nach *Iron Man* kommt nicht ungefragt
   *Der unglaubliche Hulk*. Innerhalb einer **Reihe** ja, über die Reihe hinaus nur auf Nachfrage —
   sonst sitzt man um drei Uhr nachts in einem Film, den man nie ausgewählt hat.
4. Die Ordnung ist **von Hand korrigierbar** und die Korrektur überlebt jede Neuanreicherung (E41).

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

#### 4.5.1 Wie sie aussieht (E142, E143)

> **Entwurf:** `werkseite.html`, Reiter *Die Warteschlange* — drei Anordnungen.

Drei wurden gezeichnet: **Die Bahn** (fünf Spuren, ein Auftrag wandert nach rechts) · **Die
Zeilen** (eine Zeile je Auftrag, der Weg als fünf Punkte) · **Nach Werk** (aufklappbare
Bündel).

**JB wählte die Bahn** — und begründete es mit einem Satz, der meine Empfehlung schlägt:
*„Ich glaube, die Warteschlange wird eh etwas überbewertet, es ist halt ein Progress."*

> 🔑 **Das entscheidet die Frage: die Warteschlange ist eine Tafel zum Danebenschauen, keine
> Arbeitsfläche.** Mein Einwand gegen die Bahn war „wo ist One Piece 1142? — fünf Spalten
> absuchen". Der Einwand zählt nur, wenn man sie **durchsucht**. Wenn man sie nur **ansieht**,
> gewinnt die Bahn, weil sie als einzige auf einen Blick zeigt, **wo es klemmt** — vier rote
> Karten in der Spur *Beschaffen* sagen mehr als vierzehn rote Zeilen in einer Liste.

**Farbige Umkreisung statt Rahmenfarbe** (JB): Der Zustand ist ein **Schein um die Karte**,
kein Rahmen — er verschiebt nichts und ist im Augenwinkel sichtbar, was bei einer Tafel zum
Danebenschauen genau der Punkt ist. Laufendes pulst langsam (2,4 s); bei
`prefers-reduced-motion` steht es still.

**Die anderen zwei sind nicht verworfen, sondern verschoben:**

| | wohin |
|---|---|
| **B · Die Zeilen** | wird die Bahn unter 640 px — dort ist kein Platz für fünf Spuren (E122) |
| **C · Nach Werk** | wird das **Aufklappen**: ein Klick auf eine Karte zeigt alles, was zu diesem Werk läuft |

> 🔑 **E142 — bündeln nach Werk, nicht nach Auftrag** — gilt weiter, aber **in der Tiefe**.
> Der Auftrag ist die Einheit des Systems, das **Werk** ist die Einheit des Menschen. Wer
> nachsieht, fragt „was passiert mit meinem Kram" — und bekommt es beim Aufklappen. Alles ohne
> Werkbezug (Titelbilder, Prüfungen, Aufräumen) bleibt in **einer** Sammelkarte.

> 🔑 **E143 — jede Zeile beantwortet drei Fragen, ohne dass man klickt.**
> **Was tut sie gerade** („lädt von Cosmic Scans, 4,1 MB") · **worauf wartet sie**
> („Versuch 2 von 5, nächster in 4 h") · **was passiert, wenn es schiefgeht** („dann bleibt
> Stufe C liegen und du wirst gefragt"). *Ein Fortschrittsbalken ohne diese drei Antworten
> ist Dekoration.*

**Vier Zustände, vier Farben — und einer davon ist nicht rot:**

| Zustand | Farbe | Heißt | Was der Mensch tun kann |
|---|---|---|---|
| **läuft** | Akzent | arbeitet gerade | anhalten, vorziehen |
| **wartet** | grau | Reihenfolge, kein Problem | nichts — **und das ist die Botschaft** |
| **wartet auf dich** | gelb | eine Entscheidung fehlt | hier entscheiden **oder** ins Postfach schieben |
| **hängt** | rot | hat es versucht und aufgegeben | andere Quelle erlauben, Stufe senken, streichen |

⚠️ **Gelb ist kein Fehler.** Wer „wartet auf dich" rot färbt, erzieht dazu, Rot zu
ignorieren — und dann wird auch echtes Rot ignoriert. Rot heißt: das Programm hat sein Bestes
gegeben (E122, gestuftes Aufgeben: 1 · 4 · 24 · 72 Stunden, danach still).

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

**E174 — Der Wachordner.** Ein Ordner, in den man etwas legt, und **es erscheint**. Aus
SyncYouTube übernommen (`ordner_importieren`, `downloads_einsortieren`,
`_auto_import_anstossen`). Das ist die bequemste Art, eine Bibliothek zu füllen, und die
einzige, die ganz ohne Bedienung auskommt — man zieht etwas hinein und geht weg.

> **Er nimmt nur an, er räumt nicht auf.** Was hineinfällt, geht durch dieselbe Erkennung wie
> alles andere (§8.2) und hat dieselben drei Ausgänge: **Werk · Eigenes · Postfach**. Nichts
> wird umbenannt, nichts verschoben, nichts gelöscht — die Datei bleibt liegen, wo sie liegt,
> bis der Nutzer etwas anderes sagt (E29).

**E168 — Löschen geht in den Papierkorb.** Aus SyncYouTube geerbt (`_in_papierkorb`) und bisher
nirgends aufgeschrieben: **das Programm löscht nie endgültig.** Alles Entfernte geht in den
Papierkorb des Betriebssystems — sichtbar, zurückholbar, mit einem Werkzeug, das jeder kennt.
Billiger als jede eigene Rücknahme-Logik. **Auch nicht für Zwischenspeicher, auch nicht beim
Aufräumen, auch nicht auf ausdrücklichen Wunsch.**

### 4.7 Ein Werk kann fern liegen (E169, E170)

> ⚠️ **Der größte Fund der Bestandsaufnahme.** `SyncYouTube/System/filme.py` (878 Zeilen)
> spricht seit Langem als **Klient** mit einem Jellyfin/Emby-Server: Anmeldung, Katalogabzug,
> Folgen, Reihen, Merkliste, Abspieladresse, Fortschritt-Rückmeldung, Jellyseerr-Anfragen.
> Im Pflichtenheft kam Jellyfin bis heute nur als **Ziel** vor („kann unsere Dateien lesen"),
> nie als Gegenüber. Siehe `NICHT_UEBERNOMMEN.md` §1.

> 🔑 **E169 — ein Medienserver ist ein Ort, keine Quelle und kein Motor.**
> §4.6 sagt *„Ort ≠ Werk"* — das galt bisher nur für Platten. Es gilt genauso für Server.

**Vier Sorten Ort, und der Unterschied ist keine Feinheit:**

| Ort | Beispiel | Was wir dürfen |
|---|---|---|
| **Lokal** | NAS, interne Platte | alles — lesen, holen, veredeln, umbenennen |
| **Fern und eigen** | dein Jellyfin/Emby zu Hause | **lesen und abspielen**, Fortschritt in beide Richtungen, Merkliste teilen. Nicht umbenennen, nicht veredeln — es ist nicht unser Ordner |
| **Fern und geliehen** | die Bibliothek von jemandem im selben Netz (**LANoMAT**, E179) | **sehen, anfragen, mit Zustimmung holen.** Nie Fortschritt, nie Veredelung |
| **Fern und fremd** | Netflix, Crunchyroll | **nur Wissen** (E129). Kein Bild, kein Ton, keine Datei |

**Was daraus folgt, konkret:**

1. **Ein Werk kann gleichzeitig an mehreren Orten liegen** — lokal *und* auf dem Server. Das
   ist kein Konflikt, sondern **zwei Ausgaben** desselben Werks (E03), jede mit eigener
   Güteangabe (E140). Beim Abspielen entscheidet das Profil, nicht der Zufall.
2. **Der Serverkatalog ist kein zweites Register.** Er wird über einen **Adapter** in
   Werk-Sprache übersetzt (E11) und mit unserem Register **verschmolzen** — nicht daneben
   gehängt. Die Server-ID ist ein Fremdschlüssel wie AniList-ID oder ISBN, mehr nicht.
3. **Die Merkliste ist eine Sammlung** (§4.3), keine neue Sorte Ding. Sie wird beidseitig
   abgeglichen wie eine Playlist.
4. **Jellyseerr ist ein Kandidat im Rennen** (E149), kein Sonderweg. Ein Wunsch, den der
   Medienserver erfüllen kann, geht dorthin — genau wie er sonst an einen Indexer ginge.
5. **Ein ferner Ort darf ausfallen, ohne dass etwas verlorengeht.** Ist der Server weg, ist das
   Werk immer noch da — mit Fortschritt, Merkliste und allem. Es fehlt nur eine Ausgabe.

#### E170 — Fortschritt fließt in beide Richtungen

Bisher stand im Heft nur die Richtung **hinein**: sechs Zeugen liefern uns, wo der Nutzer
steht (§8.5). Die Gegenrichtung fehlte — obwohl `filme.py` sie längst kann
(`_fortschritt_senden`, `fortschritt_nachreichen`, `_queue_lesen`).

> 🔑 **Was wir wissen, geben wir zurück.** Wer in SyncFindus eine Folge zu Ende sieht, findet
> sie auf dem Jellyfin-Handy als gesehen vor. Alles andere wäre ein Programm, das Daten
> aufsaugt und nichts zurückgibt.

**Was nicht ankommt, wandert in eine Nachreich-Schlange** und wird beim nächsten Mal geschickt —
einzeln und in der richtigen Reihenfolge. Das ist **E156 in klein**, und
`fortschritt_nachreichen` ist der fertige Code dafür.

#### E182 — Fortschritt ist eine Menge, keine Zahl

⚠️ **Korrektur vom 08.08.2026.** Die erste Fassung von E170 enthielt eine „Konfliktregel":
*es gewinnt die weitere Position, nicht der neuere Zeitstempel.* **JB hat sie zerlegt:**

> *„Wenn ich an meinem PC nicht Episode 12 geguckt habe, bin ich bei Folge 3. Ich sehe den
> Konflikt nicht. Kannst du nicht differenzieren zwischen einmal geöffnet und von wem?"*

**Er hat recht, und der Konflikt war ein Fehler in meinem Modell — kein echtes Problem.** Ich
hatte Fortschritt als **eine Zahl** modelliert („du bist bei Folge 8"). Sobald man das tut,
kollidieren zwei Zahlen, und man braucht eine Regel, welche gewinnt. **Modelliert man ihn als
das, was er ist — ein Zustand je Einheit — gibt es nichts zu entscheiden.**

> 🔑 **Je Einheit genau drei Zustände: ungesehen · mittendrin (mit Marke) · gesehen.**
> Jellyfin führt es genauso (`Played` + `PlaybackPositionTicks`), MyAnimeList und AniList
> ebenfalls. Wir hatten es als einziges falsch.

| Regel | Warum |
|---|---|
| **Zwischen Einheiten wird vereinigt, nie verglichen** | „Gesehen" ist je Einheit **einbahnig**. Zwei Geräte können sich hier **gar nicht widersprechen** — sie können nur beide recht haben. Der Fall „hier 12, dort 3" ist also: *Folgen 1–12 gesehen, und in Folge 3 steht zusätzlich eine Marke, weil du sie nochmal ansiehst.* **Beides ist wahr.** |
| **Innerhalb einer Einheit gewinnt die neuere Marke** | Zurückspulen ist normal. Wer in Folge 8 von 12:07 auf 3:00 springt, hat das gemeint. *Genau hier hatte ich es vorher umgekehrt und falsch* |
| **„Weiter" ist eine Frage, keine Zahl** | Es ist die Einheit mit **offener Marke** — und wenn es keine gibt, die **erste ungesehene**. Deshalb bringt eine Folge 12 von irgendwoher niemanden irgendwohin |
| **Nur die Hand nimmt „gesehen" zurück** | Ein ausdrückliches Zurücksetzen ist die **einzige** Handlung, die die Einbahnregel aufhebt. Sie gilt sofort auf beiden Seiten — und sie ist der Grund, warum die Einbahnregel überhaupt sicher ist |

#### E181 — Fortschritt gehört einem Profil, nicht einem Ort

**JB:** *„Wenn jemand von meinem PC streamt, dann hat das nicht mit dem Programm zu tun. Er ist
in seinem Programm und guckt von da."*

> 🔑 Auf dem Server melden wir uns als **ein bestimmter Benutzer** an und lesen und schreiben
> **ausschließlich dessen** Daten. Wer sonst noch von diesem Server streamt, ist ein anderer
> Benutzer — **für uns existiert er nicht.**

⚠️ **Die eine Bedingung dafür: teile den Server, nicht das Konto.** Wer sein Passwort
weitergibt, hat keine zwei Benutzer, sondern **einen mit zwei Menschen** — und dann kann kein
Programm der Welt auseinanderhalten, wer gesehen hat. SyncFindus merkt das immerhin: eine
Sitzung von einem **unbekannten Gerät** wird *gefragt statt geglaubt*.

Dasselbe gilt nach innen: **Fortschritt hängt am Profil** (E161, E158), nicht am Rechner und
nicht am Ort. Zwei Menschen an einem PC sind zwei Profile, nicht ein durcheinandergeratener
Lesestand.

#### E183 — Geöffnet ist nicht gesehen

Kurz reinschauen, jemandem etwas zeigen, versehentlich starten — **das ist kein Fortschritt und
schreibt gar nichts.**

| Schwelle | Was passiert |
|---|---|
| unter **2 %** oder unter **60 Sekunden** | **nichts.** Kein Eintrag, keine Marke, keine Meldung nach außen |
| darüber | eine **Marke** — mittendrin |
| ab **90 %** oder mit dem Abspann | **gesehen** |
| Manga/Buch | eine angetippte Seite ist nichts, die **letzte Seite eines Kapitels** ist alles |

**Und der Notausgang:** jeder Fortschrittseintrag trägt **„das war ich nicht"** — ein Griff, und
er verschwindet, auf beiden Seiten. Weil es immer den Abend gibt, an dem jemand anderes am
Rechner saß.

> ⚠️ **Und weil JB es ausdrücklich angesprochen hat:** *„Wenn jemand Folge 12 anfragt, dann
> bringt mich das nicht auf Folge 12."* — Richtig, und das ist eine eigene Regel wert:
> **eine Anfrage ist eine Absicht, kein Ereignis.** Anfragen (E180), Wünsche (E150),
> Merklisten, Warteschlangen-Einträge — **nichts davon berührt jemals eine Position.**
> Fortschritt entsteht ausschließlich durch **Abspielen**, und zwar durch deins.

**Live-TV** (`live_tv.py`, `m3u_parsen`, `kanaele`, `programm`): **E44** hat es längst
zugelassen — dass der Code dafür schon existiert, stand nirgends. Ein Sender ist ein
**Ort ohne Vorrat**: man kann hinschauen, aber nichts holen und nichts fortsetzen.

#### E179 — LANoMAT: fremde Bibliotheken sind Orte, keine Konten (F09 beantwortet)

**JB fragte am 08.08.2026 nach LANoMAT — und die Antwort fällt jetzt zusammen mit E169**, denn
es ist **dasselbe Problem**: ein Werk liegt irgendwo, das nicht mir gehört. Damit braucht
LANoMAT keine eigene Maschinerie, sondern nur eine vierte Zeile in der Tabelle oben.
`familie.py` (193 Z.: `familie`, `nachbar`, `status_schreiben/lesen`) ist der Ausgangspunkt.

> 🔑 **Kein Konto, kein Server, keine Anmeldung. Wer im selben Netz ist, ist da — und wer geht,
> ist weg.** Erkennung über Zeroconf/mDNS, wie ein Drucker sich meldet. Ein LAN-Abend braucht
> keine Registrierung.

**Warum es das überhaupt wert ist**, und es ist ein einziger Satz: **die Lücken-Liste (E160)
trifft auf sechs andere Bibliotheken.** Deine 163 fehlenden Werke werden gegen alle Anwesenden
gehalten, und was zusammenpasst, steht da: *„Kevin hat 4 davon, Ann hat 11."* Das ist etwas,
das kein Streaming-Dienst und kein Verzeichnis leisten kann — und es ist genau der Moment, in
dem eine LAN-Party besser ist als das Internet.

**Die Rechte sind gestuft, und der Standard ist die unterste Stufe:**

| Stufe | Der andere sieht | Standard |
|---|---|---|
| **Aus** | nichts. Du bist unsichtbar | ✅ **so beginnt jede Sitzung** |
| **Sehen** | *dass* du ein Werk hast — Titel und Güte, sonst nichts | auf Zuruf |
| **Anfragen** | er darf fragen; du bekommst eine Karte mit *„Kevin fragt nach One Piece 1–1140"* und einem Ja/Nein | auf Zuruf |
| **Holen** | er darf ohne Rückfrage ziehen, was du freigegeben hast | nur ausdrücklich, nur für benannte Personen |

⚠️ **Was niemals geteilt wird, auf keiner Stufe:** dein **Fortschritt**. Was du gelesen hast,
wie weit, wann und wie oft — das ist das Persönlichste im ganzen Programm (§8.5) und verlässt
den Rechner nie. Auch nicht als Zahl, auch nicht anonym. *Man teilt seine Bibliothek, nicht
sein Tagebuch.*

**Drei weitere Regeln, ohne die es kippt:**

1. **Nichts wird geschoben, alles wird gezogen.** Niemand kann dir etwas in die Bibliothek
   legen. Was du holst, geht durch dieselbe Erkennung wie jede Datei (§8.2) und landet
   notfalls im Postfach.
2. **Der Ort verschwindet, das Wissen darf bleiben.** Ist die LAN-Party vorbei, ist die
   Bibliothek weg — aber *„Kevin hatte Vinland Saga vollständig"* darf als Notiz stehen
   bleiben, **wenn Kevin das erlaubt hat**. Sonst ist auch das weg.
3. **Es ist eine Sitzung, kein Zustand.** LANoMAT ist beim Start immer aus. Es gibt keinen
   Dauerbetrieb, keine Freundesliste, kein „online seit". Ein Programm, das dauerhaft im Netz
   nach anderen sucht, ist etwas anderes als eines, das man für einen Abend einschaltet.

#### E180 — Eine Anfrage ist ein Wunsch, der über eine Grenze geht

> **Entwurf:** `orte.html`, Reiter *Anfragen*.

**JB, 08.08.2026:** *„Also sind Anfragen nun auch ein Thema durch seerr, oder?"* — **Ja.** Und
das Beste daran: es ist **kein neues System**. Jellyseerr, LANoMAT und der Haushalt sind
dreimal dieselbe Sache.

> 🔑 Ein **Wunsch** (E150) ist an mich selbst gerichtet: *ich will das, und mein Programm
> versucht es.* Eine **Anfrage** ist an jemand anderen gerichtet: *ich will das, und ein Mensch
> muss zustimmen.* **Gleiche Form, andere Grenze** — deshalb hängt der Zustand am Wunsch, der
> Weg ist die Warteschlange, und die Zustimmung ist eine Karte. Nichts davon ist neu gebaut.

| Wohin | Wer sagt Ja | Was danach passiert |
|---|---|---|
| **An den eigenen Server** (Jellyseerr) | meistens **du selbst** — deshalb fühlt es sich wie ein Wunsch an | Der Server ist **ein Kandidat im Rennen** (E149), kein Sonderweg: er tritt gegen Indexer und Direktlinks an und gewinnt, wenn er schneller ist |
| **An eine fremde Bibliothek** (E179) | **ein anderer Mensch**, mit einer Karte und drei Knöpfen | Bei Ja wird **gezogen, nie geschoben**. Die Datei geht durch dieselbe Erkennung wie jede andere (§8.2) |
| **An jemanden im Haushalt** (`familie.py`) | der **Profilinhaber** — z. B. ein Elternteil bei einem Kinderprofil (E158) | Dasselbe. **Ein Kind fragt, statt heimlich zu suchen** — die freundlichere Form von Jugendschutz |

**Drei Antworten, nicht zwei:** *Ja* · *Nein* · **„Nur ansehen"**. Die Zwischenstufe ist das,
was man beim LAN-Abend fast immer meint — *lies es bei mir, nimm es nicht mit* — und sie
existiert in keinem Programm. Sie kostet nichts und löst die meisten Fälle.

**Vier Regeln, damit aus Anfragen keine Bettelei wird:**

1. **Eine Ablehnung ist ein Ergebnis, kein Fehler.** Sie ist nicht rot. Der Wunsch bleibt bei
   dir und **lauert weiter** (E150). ⚠️ **Man fragt denselben Menschen nicht zweimal nach
   derselben Sache** — ein zweiter Versuch braucht deine ausdrückliche Handlung, das Programm
   wiederholt ihn **nie** von selbst. *Das ist der einzige Ort im ganzen Entwurf, an dem E150
   ausdrücklich nicht gilt.*
2. **Der Anfragende sieht nur „gestellt".** Nicht, ob der andere sie gelesen, geöffnet oder
   ignoriert hat. Kein Lesebestätigungs-Elend.
3. **Eine Anfrage trägt nie deinen Fortschritt.** Sie sagt *„ich hätte gern X"* — nicht *„ich
   bin bei Kapitel 63 und mir fehlen die davor"*. Das wäre eine Auskunft über dich, die niemand
   angefordert hat (E179).
4. **Anfragen sind Post, kein Postfach.** Sie kommen **nicht** ins Postfach (E141) — das ist
   für **Unklarheit**, und eine Anfrage ist das Gegenteil: völlig klar, sie braucht nur eine
   Antwort. Sie stehen bei der Warteschlange, weil dort das Ergebnis landet.

⚠️ **Und das Neue daran, das man sich bewusst machen muss:** Mit den Anfragen taucht zum ersten
Mal **ein anderer Mensch auf deinem Bildschirm** auf. Bis hierhin war SyncFindus ein Programm
für genau eine Person. Deshalb die vier Regeln — jede einzelne verhindert eine Sorte
sozialen Druck, die ein Werkzeug nicht erzeugen sollte.

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

### 5.10.3 Die Hover-Karte (E165)

> **Entwurf:** `regale.html`, Reiter *Die Hover-Karte* — vier Möglichkeiten zum Anklicken.

| | Was passiert | Urteil |
|---|---|---|
| **A · Die Kachel wächst** | 1,12× skaliert, Angaben darunter (Netflix' Weg) | vertraut — *schiebt aber die Nachbarn optisch weg und wächst am Regalrand aus dem Bild* |
| **B · Karte daneben** | feste Karte rechts, Regal bleibt ruhig | viel Platz — *der Blick springt weit* |
| **C · Die Reihe klappt auf** | Band **unterhalb** der Reihe | ✅ **nichts wird verdeckt, nichts springt** — und es ist der einzige Weg, der auf dem Handy identisch funktioniert |
| **D · Nur der Rand** | Rahmen + voller Titel, sonst nichts | die ehrlichste Antwort — *sagt aber nichts Neues* |

> 🔑 **C mit D als Sofortantwort.** Rand und voller Titel erscheinen bei **0 ms**, das Band nach
> **400 ms**. Wer über das Regal streift, sieht nie ein Band; wer stehen bleibt, bekommt alles.
> Das ist der ganze Unterschied zwischen *hilfsbereit* und *aufdringlich*.

**Vier Regeln für jede Variante:**
1. **Nichts erscheint unter dem Zeiger** — sonst klickt man versehentlich hinein.
2. **200 ms Nachlauf beim Verlassen** — sonst flackert es beim Durchfahren.
3. **Tastatur zeigt dasselbe wie Maus** (Fokus = Hover) — sonst gibt es zwei Programme.
4. ⚠️ **Auf dem Handy gibt es keinen Zwischenschritt.** Der erste Tipp öffnet das Werk. *Eine
   Hover-Karte, die auf Berührung reagiert, kostet jedem Handynutzer einen zusätzlichen Griff —
   für immer.*

### 5.10.4 Die Kachelgrößen — und warum keine ohne Namen (E88)

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

### 5.11.3 Was fest sein muss und was atmen darf (E103)

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
> (andockbar, herauslösbar, Layout-Editor). Bei SyncFindus ist die Bühne eine **Ebene** — man
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
beobachtet. SyncFindus ist ein Ort zum **Lesen und Sehen**. Wer liest, will eine Fläche, nicht sechs.

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
⚠️ **Sie hängt oben, nicht in der Mitte** (JB-Fund 08.08.2026: *„Die Pausenkarte sollte nicht
über dem Player-Menü sein. Weiter oben links und etwas kleiner, je nachdem wie klein der Player
gezogen ist."*). Bei `top:50 %` ragte sie in die Bedienleiste, sobald die Bühne kurz wurde.
Jetzt hängt sie **unter der Kopfzeile** und ihre Höhe ist auf den freien Raum geklammert —
beide Höhen **gemessen**, nicht geraten (E121). Wird es eng, gibt sie gestuft nach (E122):
erst der Inhaltstext auf zwei Zeilen, dann ganz weg, dann die Nebenangabe — der **Titel bleibt
immer**.
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

**E118 — die Leiste gehört mal zum Raum, mal darüber.** JB-Fund 07.08.2026:
*„Es darf keine unsichtbare Barriere sein, die das Bild plötzlich kleiner werden lässt."*

| | Bühne bei **Film/Anime** | Bühne bei **Musik/Hörbuch** |
|---|---|---|
| Leiste | **Überzug** über dem Bild | **Teil des Raums** — die Fläche endet darüber |
| Blendet aus | ja, nach 2,5 s (E81) | **nie** (E106) |
| Grund | ein Bild darf nicht beschnitten werden, nur verdeckt | es gibt kein Bild zu beschneiden, und Ton braucht dauernd Bedienung |
| Folge | nichts verschiebt sich, wenn sie kommt und geht | nichts rutscht je darunter |

Damit gibt es **keine unsichtbare Grenze**: entweder die Leiste liegt sichtbar oben drauf und
das Darunter ändert seine Größe nie — oder sie ist Möbel und der Raum ist von vornherein kleiner.
Was es nicht gibt: eine Leiste, die mal Platz nimmt und mal nicht.

**E121 — Höhen werden gemessen, nie geraten.** JB-Fund 07.08.2026: *„Wenn ich das Fenster
kleiner ziehe, verschwindet was vom Bild."* Ursache war eine feste Zahl (`bottom: 62px`) für
eine Leiste, die je nach Breite umbricht und dann höher ist.

> **Wo ein Bauteil einem anderen Platz macht, wird die Höhe zur Laufzeit gemessen**
> (`ResizeObserver` → CSS-Variable), nicht im Stylesheet festgeschrieben.
> Magische Zahlen stimmen genau bei der Breite, bei der man sie gemessen hat.

Das gilt überall, wo etwas „darüber" oder „darunter" sitzt: Klangleiste, Bühnenleiste,
Kopfzeilen, das schwebende Bildfenster.

**E130 — nichts scrollt, was eine Bühne ist.** JB-Fund 07.08.2026: *„In Hörbuch kann man nach
oben und unten scrollen, das darf natürlich nie passieren, egal wie klein der Player wird."*

> Eine **Bühne** (Leser, Spieler, Musik, Hörbuch) ist ein **Bild**, kein Dokument.
> Bilder rollen nicht — sie geben nach (E122).

`overflow:auto` an einer Bühnenfläche ist immer ein Fehler; es ist die bequeme Ausrede dafür,
die Prioritätsleiter nicht geschrieben zu haben. **Gerollt wird nur in Listen** (Warteschlange,
Kapitelliste, Regal) — dort ist es der Zweck.
Konsequenz: alle Textzeilen einer Bühne sind **einzeilig mit Auslassung** oder auf eine feste
Zeilenzahl geklammert, nie frei wachsend.

**E133 — nichts steht zweimal im Bild.** JB-Fund 07.08.2026: *„Wieso steht bei Musik der Titel
oben und unter dem Cover nochmal?"* — Weil ich zwei Bauteile unabhängig entworfen hatte.

> **Trägt der Inhalt den Titel, trägt die Kopfzeile die Herkunft.** Und der Pfeil führt genau
> dorthin zurück, was oben steht.

In Anordnung **A** trägt das Cover den Titel ⇒ oben steht *Musik · Playlist „Ushio, alles"*.
In **B** und **C** wird der Titel klein bzw. der Text regiert ⇒ er wandert nach oben, die
Herkunft verschwindet. Dieselbe Regel gilt überall: Werk-Seite, Leser, Bühne.

**E152 — eine Leiste endet vor dem Streifen.** JB-Fund 08.08.2026: *„Kapitel usw. sind verdeckt
von ‚von uns vertont' und ‚Mitlesen an'."* — Die **untere** Leiste hatte bei Musik und Hörbuch
längst gelernt, vor dem Seitenstreifen zu enden (`right: 262px`). Die **obere** nicht: sie lief
über die volle Breite, und ihre rechten Marken landeten genau auf der Kopfzeile des
Kapitelstreifens.

> **Wer eine Regel für die eine Kante schreibt, schreibt sie für beide.** Eine Leiste, die
> einen Streifen hat, endet vor dem Streifen — oben wie unten, links wie rechts. Ich hatte den
> Fehler unten bemerkt, behoben und **nicht nachgesehen, ob er oben genauso steckt**. Das ist
> die häufigste Sorte Fehler überhaupt: ein reparierter Fehler mit einem unreparierten Zwilling.

**E122 gilt auch senkrecht.** JB-Fund 08.08.2026: *„Die Namen der Sprecher sind ausserhalb des
Bildes"* und *„Ich seh weiterlesen statt hören nicht, wenn es zu klein gezogen ist."* — Ursache:
der Textblock war **inhaltshoch** in einem zentrierenden Kasten. Wurde er höher als die Bühne,
wuchs er **nach oben und unten** aus der Mitte heraus: oben fielen die Sprechermarken hinaus,
unten der Knopf. Beides unsichtbar, beides ohne Hinweis.

> **Gestuftes Aufgeben ist keine Breitenregel, sondern eine Regel über knappen Raum.**
> Der Block wird auf die Bühnenhöhe geklammert und lässt in fester Reihenfolge weg:
> Textabsätze 3 → 2 → 1, dann die Stimmenzeile einreihig, dann das Mitlesen ganz.
> **Der Knopf steht nie in der Verzichtsreihe** — er ist das Angebot, nicht die Zier.

**E153 — eine Tafel ist eine Tabelle.** JB-Fund 08.08.2026: *„Untertitel-Einstellungen sehen
gut aus, doch das Fenster sieht irgendwie falsch aus."* — Es gab nichts Kaputtes zu sehen, und
genau das macht diese Sorte Fehler gefährlich. Drei Ursachen, alle drei unterhalb der
Benennbarkeitsschwelle:

| Ursache | Was das Auge merkt |
|---|---|
| **Links bündig, rechts fransig** | Die Beschriftungen standen in fester Spalte, die Knopfgruppen daneben waren jede anders breit → sieben Zeilen, **sieben verschiedene rechte Kanten**. Links liest man eine Tabelle und erwartet rechts auch eine |
| **Gleich aussehende Zeilen, anderer Takt** | „Größe" und „Schrift" sind beide *Aa*-Knöpfe, hatten aber 7 px bzw. 6 px Innenabstand → sie standen **nicht übereinander**, obwohl sie es sollten |
| **Vier Gewichte in einer 32-px-Zeile** | 24-px-Knöpfe neben 15-px-Punkten neben 46-px-Feldern neben 26-px-Pfeilen |
| *(dazu)* **ein Pixel** | Die Tafel hat überall 15 px Rand, die Zeilen hatten 14 px |

> **Die Wertespalte ist fest breit, und jede Gruppe teilt sie in gleiche Zellen.** Damit stimmen
> **beide** Kanten in jeder Zeile, jede Zelle einer Zeile ist gleich groß, und wechselnde
> Beschriftungen („100 %" → „75 %") springen nicht mehr (E103 — die Zelle *ist* die feste
> Breite). Farbpunkte wachsen auf 22 px und wiegen damit so viel wie ein Knopf.

**E131 — ein Knopf, eine Bedeutung.** ⚠️ Ich hatte beim Hörbuch demselben Knopf ein anderes
Etikett gegeben („Einschlafen 30 min") und ihn trotzdem die Ton-&-Text-Tafel öffnen lassen.
Wer das Etikett ändert, **muss** auch die Handlung ändern — sonst lügt der Knopf.
Zulässig ist nur: gleiche Handlung, anderes Wort für dieselbe Sache.

**E132 — Angebote schließen sich aus.** Nie zwei Aufforderungen gleichzeitig im Bild.
Die **Weiche** (E115) verlangt eine Entscheidung, die **Besetzungskarte** (E124) lädt zum
Verweilen ein — beides zusammen ist Lärm. Erscheint die Weiche, verschwindet die Besetzung.
Allgemein: **höchstens eine Karte, die etwas will.**

**E122 — gestuftes Aufgeben.** Wird es eng, fällt der Inhalt in einer **festgelegten
Reihenfolge** weg, statt zu überlaufen oder zu stapeln. Für die Musikbühne:

| Ab | fällt weg |
|---|---|
| 960 px | Romaji-Zeile |
| 860 px | Karaoke ganz |
| 760 px | Wellenform · Cover wird kleiner · Mitlesen |
| 700 px | Warteschlange · dann erst stapelt es sich |

Das ist die Prioritätsleiter (§5.2) am Bauteil statt am Fenster — und sie muss **geschrieben**
sein, sonst entscheidet der Zufall des Umbruchs.

**E119 — die Weiche braucht Zeit.** Autostart nach 9 s ist richtig, wenn es **eine** Fortsetzung
gibt. Bei einer Wahl ist er falsch: *„manchmal muss ich die Fernbedienung finden."*
**30 s Grundzeit + 10 s je zusätzlicher Wahlmöglichkeit** — bei zwei Wegen also 50 s.
Jede Bewegung an Maus, Taste oder Gamepad hält den Zähler **ganz** an, nicht nur kurz.

**E124 — die Besetzungskarte.** Spiegelbild der Pausenkarte: links steht, **was** läuft,
rechts **wer** zu sehen ist. Vorbild ist Amazons X-Ray, aber mit zwei Unterschieden.

| | |
|---|---|
| **Immer möglich** | die volle Besetzung mit Rolle, Name und Gesicht aus TMDB/AniList — haben wir ohnehin |
| **„Gerade im Bild"** | ein **einmaliger Durchlauf beim Einlagern** vergleicht Gesichter mit den Besetzungsfotos und erzeugt eine Zeitliste. Amazon lässt das von Hand annotieren; wir rechnen es nachts auf der Grafikkarte (~2 Min je Film) |
| **Bei Anime** | Figuren statt Schauspieler, Sprecher darunter — und die Erkennung funktioniert bei gezeichneten Figuren **besser** als bei Menschen. Nebenbei füttert sie das Werk-Wissen für die Vertonung (§10.1) |
| ⚠️ **Nie behaupten** | ohne den Durchlauf steht dort *die Besetzung*, nicht *„gerade zu sehen"*. Erkanntes wird markiert, der Rest steht blass darunter (E57) |
| ⚠️ **Nie im laufenden Bild** | X-Ray blendet Namen ins Bild — der schnellste Weg, eine Szene zu zerstören. Bei uns **nur bei Pause**, und es verschwindet mit ihr |

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

#### E159 — Die Einstellung gehört zum Spiel, nicht zum Emulator

> **Entwurf:** `erststart.html`, Reiter *Emulator-Einstellungen*.

**JB, 08.08.2026:** *„Spiele-Regal finde ich gut, mir geht es sehr um die Settings für den
Emulator."* — Das ist die richtige Frage, denn der übliche Weg geht immer schief: Man stellt
RetroArch ein, und alles erbt es. Aber *Chrono Trigger* braucht einen anderen Shader als
*Sonic*, und *Ocarina of Time* eine andere Auflösung als *Pokémon Rot*.

> 🔑 **Drei Ebenen: Grundlage → System → Spiel. Und jede Zeile sagt, woher ihr Wert kommt.**
> Was auf Spielebene gesetzt ist, steht in Akzentfarbe mit dem Wort **eigen**; alles andere ist
> blass und trägt **geerbt · SNES**. So sieht man auf einen Blick, **was man selbst verstellt
> hat** — die Frage, die man sich nach sechs Monaten stellt.

Zwei Knöpfe schließen den Kreis: **„Auf SNES zurücksetzen"** macht ein Spiel wieder
unauffällig, **„Als SNES-Standard übernehmen"** hebt eine gute Einstellung eine Ebene hoch.
*Ohne den zweiten Knopf stellt man dieselbe Sache 41-mal ein.*

| Gehört zum **Werk** | Gehört zum **System** | Gehört nirgends hin |
|---|---|---|
| Shader · Skalierung · Seitenverhältnis · Steuerungsbelegung · Schnellspeicher-Plätze · Regionsfassung (J/U/E) · Patches | Der Kern (welcher Emulator) · BIOS · Bildwiederholrate · Aufnahme | **Der Emulator selbst** — er ist ein Abspielweg wie mpv, austauschbar, ohne dass ein Spielstand verlorengeht |

**ROM = Ausgabe, Spiel = Werk** (E03): die japanische, die amerikanische und die
fan-übersetzte Fassung sind **drei Ausgaben eines Werks** mit **einem** gemeinsamen
Spielstand-Verlauf und **einer** Spielzeit.
**Spielstände liegen beim Werk im Register**, nicht im Emulator-Ordner — Emulator wechseln,
Rechner wechseln, Fassung wechseln: der Stand bleibt.
**Echtheit über Prüfsumme:** No-Intro und Redump führen Prüfsummen sauberer Abzüge — dieselbe
Idee wie die Güteleiter, *gemessen statt geglaubt* (E140).
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

### 7.0.1 E129 — Streaming-Konten sind Wissen, keine Quelle

**JB-Frage 07.08.2026:** *„Können wir Spotify mit einbinden? Oder SoundCloud? Oder alles
irgendwie locked?"*

| Dienst | Was geht | Was nicht |
|---|---|---|
| **Spotify** | Web-API mit OAuth: **Bibliothek, Playlists, Verlauf, Metadaten, Audio-Merkmale**. Wiedergabe **steuern** (Play/Pause/Skip) auf einem Gerät, auf dem Spotify schon läuft — Connect-Prinzip | **Kein Tonstrom.** Der Stream ist Widevine-verschlüsselt und die API gibt ihn nicht heraus. Auch die 30-Sekunden-Hörproben sind seit Ende 2024 für neue Anwendungen gesperrt |
| **SoundCloud** | API mit OAuth: Likes, Playlists, Metadaten. **Freigegebene** Titel haben eine offene Stream-URL — viele Künstler erlauben den Download ausdrücklich | Für alles andere gilt dasselbe: kein Zugriff auf Geschütztes. Neue API-Zugänge werden seit Jahren nur zögerlich vergeben |
| **Last.fm / ListenBrainz** | vollständiger Hörverlauf, offen, ohne Haken | — |
| **Bandcamp** | gekaufte Titel gehören dir, als Datei | — |

**Die Regel, die daraus folgt — und sie ist dieselbe wie bei Crunchyroll und Netflix:**

> **Konten liefern Wissen, nicht Inhalt.** Deine Spotify-Bibliothek wird gelesen und wird zu
> Regal-Einträgen im Zustand **◐ gekannt** (E54). SyncFindus sagt dir dann, was davon du
> **wirklich** besitzt, was als Datei zu bekommen wäre, und wo eine Lücke ist.

Das ist nicht der Trostpreis, sondern genau unser Alleinstellungsmerkmal: **kein anderes
Programm zeigt dir die Lücke zwischen dem, was du hörst, und dem, was dir gehört.**
Und wenn ein Abo endet, bleibt dein Regal — die Liste, was du gehört hast, ist dann mehr wert
als das Abo es war.

⚠️ **Was wir nie tun:** einen geschützten Stream mitschneiden oder entschlüsseln. Nicht aus
Prüderie, sondern weil es (a) rechtlich eine andere Kategorie ist als die Privatkopie,
(b) bei jedem Update kaputtgeht und (c) das ganze Vorhaben in Geiselhaft nimmt.

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

### 7.4 Die Güteleiter (E140)

> **Entwurf:** `quellen.html` — Wissensketten, Inhaltsquellen, Zeugen.

Qualität ist kein Häkchen, sondern eine Leiter. **Eine** Leiter für alle Medien, damit ein
Profil („nie unter B") *eine* Regel ist statt vier.

| Stufe | Bewegtbild | Musik | Buch / Manga | Bedeutung |
|---|---|---|---|---|
| **S** Quelle | Remux, unangetastet | FLAC / Vinyl-Rip 24 bit | Verlags-EPUB, Verlagsscan | es gibt nichts Besseres |
| **A** Sehr gut | BDRip 1080p+ | V0 / 320 kbit aus S | Scan ≥ 1600 px, entrastert | verlustbehaftet, aber nicht wahrnehmbar |
| **B** Gut | WEB-DL | 256 kbit AAC | Reader-Scan ≈ 1200 px | der Alltagsfall — was Streaming liefert |
| **C** Brauchbar | WEBRip / HDTV | 192 kbit | Webscan mit Kompressionsrändern | man sieht es, es stört nicht immer |
| **D** Notnagel | Cam / < 480p | < 128 kbit, Transcode | fotografierte Seiten, OCR ohne Bilder | besser als nichts — **wird markiert** |

> 🔑 **E140 — die Stufe wird gemessen, nicht geglaubt.** Ein Dateiname, der `1080p BluRay`
> sagt, ist eine Behauptung von jemandem, den wir nicht kennen. Die Stufe kommt aus dem
> Messbaren: Auflösung, Bitrate je Minute, Codec, Kanalzahl, Tonspur-Sprachen — beim Scan aus
> Seitenhöhe, Bytes je Seite und Kompressionsartefakten. **Behauptung und Messung stehen
> beide da**; widersprechen sie sich, gewinnt die Messung und der Widerspruch geht ins
> Postfach.

⚠️ **Der Doppel-Transcode ist der schlimmste Fall**, weil er sich wie A anfühlt und wie C
klingt: 320 kbit, erzeugt aus einer 192-kbit-Datei. Am Spektrum erkennbar (harte Abbruchkante
bei 16 kHz statt 20 kHz) — **einmal beim Einlesen prüfen**, nie bei jedem Abspielen.

**Was legal beschaffbar ist, je Medium** (recherchiert 08.2026; die Liste ist Wissen für den
Bau, **nicht** der Quellenkatalog — der bleibt Laufzeitdatei, E12):

| Medium | Stark | Anmerkung |
|---|---|---|
| **Bücher** | Standard Ebooks (S, ~1.000 handgesetzt) · Project Gutenberg (B, ~78.000) · Baen Free Library / Tor (S, DRM-frei geschenkt) · DTA + zeno.org (deutscher Kanon, TEI-XML) | ⚠️ Projekt Gutenberg-DE ist aus Deutschland gesperrt (S.-Fischer-Urteil). Internet Archive nur als **Wissen** — die Leihe hat DRM |
| **Hörbücher** | **ARD Audiothek** (A, Hörspiele in Rundfunkqualität) · Deutschlandfunk-Feeds · LibriVox (C, ~20.000, Qualität je Sprecher) | Audible liefert `.aax` mit DRM → nicht unser Weg |
| **Musik** | **Bandcamp** (S, FLAC 24 bit, DRM-frei) · **Live Music Archive** (S, > 250.000 bandfreigegebene Konzerte als FLAC) · arte Concert (A, ganze Sets) · eigene CDs (S, bitgenau, AccurateRip bestätigt) | Das Live Music Archive ist der DJ-Set-/Konzertfall — und maschinenlesbar |
| **Film / Serie** | **MediathekView** (B, eine Filmliste über 13 öffentlich-rechtliche Sender, MP4 vorgesehen, mit Untertiteln) · arte (A) · Internet Archive (C, gemeinfrei; Jahrgang 1930 seit 01.01.2026 frei) | ⚠️ Eigene Blu-ray: technisch der einzige Weg zu echtem S, rechtlich in DE heikel — § 95a UrhG verbietet das Umgehen wirksamer Maßnahmen **auch für die Privatkopie**, und AACS gilt als solche |
| **Manga / Comics** | MANGA Plus (A, offiziell, am Erscheinungstag) · Webtoon/Tapas (A) · Digital Comic Museum (B, Golden Age als CBZ) · Verlags-Bundles (S, CBZ ohne DRM) | MANGA Plus steht zu Recht in SyncMangas `PAYWALL_SITES`: als **Leseort** legal, als Quelle für eine *ganze* Serie untauglich |

**MediathekView ist der stärkste Einzelfund**: ein Adapter deckt ARD, ZDF, arte, 3sat, KiKA,
ORF, SRF und die Dritten ab — mit maschinenlesbarer Filmliste, ohne Konto, ohne Bot-Schutz,
seit Jahren stabil, samt Untertiteln und teils Audiodeskription.

❌ **Was nicht geht und nie gehen wird:** Widevine (Netflix, Disney+, Crunchyroll), Adobe ACSM
(Bibliotheksleihe), Audible-DRM. Das Konto liefert **Wissen**, nie Inhalt (E129).

### 7.5 Vier Protokolle statt einer Liste

**JB, 08.08.2026:** *„Das sieht mir alles zu legal aus. Ich will alle Anbieter haben. Gibt es
Torrentseiten mit jedem erdenklichen Kram? … Lets look deep, far and wide."*

**Die Antwort ist kein Verzeichnis, sondern eine Bauform** — und sie ist stärker als jedes
Verzeichnis. Eine Liste von 200 Adressen ist in drei Monaten zu einem Drittel tot. Ein Adapter
auf ein gepflegtes Protokoll ist in drei Monaten **mehr** wert, weil in der Zwischenzeit
hunderte Leute nachgezogen haben. SyncFindus spricht deshalb die vier Sprachen, in denen
Quellenlisten überhaupt veröffentlicht werden:

| Protokoll | Wer pflegt | Umfang | Was wir bauen |
|---|---|---|---|
| **Cardigann-YAML** (Prowlarr · Jackett) | Gemeinschaft, **täglich** per GitHub-Action zwischen beiden Projekten abgeglichen | **500+** Indexer | **Ein** Adapter zu deinem Prowlarr. Jeder Indexer, den du dort einträgst, ist bei uns sofort eine Quelle |
| **`index.min.json`** (Mihon · Aniyomi · Keiyoushi) | Gemeinschaft, Abgleich alle paar Stunden | hunderte Lesequellen | Ein **Abonnent** für Erweiterungslisten — genau die Bauform aus E12 |
| **yt-dlp-Extraktoren** | hunderte Mitwirkende, fast wöchentlich | **~1.800 Seiten** | yt-dlp **ist** unser universeller HTTP-Adapter |
| **MediathekView-Filmliste** | Verein, seit 2011 | 13 Sender | eine komprimierte JSON-Datei lesen |
| **BitTorrent / Magnet** | niemand — es ist ein **Protokoll**, kein Anbieter | — | Magnetlink erkennen, an deinen Client übergeben, Fortschritt zurücklesen |

> 🔑 **Der Nutzer bekommt nicht unsere Liste — er bekommt jede Liste, die es gibt, und die von
> morgen dazu.** Und weil nichts davon im Paket steht, gibt es nichts, was man dem Projekt
> wegnehmen könnte (E12).

### 7.6 Das Werkzeugfeld — was schon gelöst ist

Alles hier ist quelloffen, aktiv gepflegt und wird **eingebunden statt nachgebaut** (E11).

| Werkzeug | Rolle | Wofür |
|---|---|---|
| **yt-dlp** | Motor | alles über HTTP; läuft in SyncYouTube bereits |
| **streamlink** | Motor | Live-Ströme, die yt-dlp schlechter kann |
| **gallery-dl** | Motor | Bildstrecken **und Manga-Kapitel** — genau die Lücke, die SyncManga heute hat |
| **Prowlarr** · **Jackett** | Klempnerei | 500+ Indexer hinter einer Suchschnittstelle |
| **qBittorrent** · **Transmission** · libtorrent | Klempnerei | Magnet hinein, Fortschritt heraus. Wir bauen keinen Torrent-Motor |
| **Bazarr** | Klempnerei | Untertitel — bis unsere eigene Übersetzung besser ist (§10.2) |
| **beets** | **Vorbild** | Goldstandard für Musikbibliotheken; sein Autotagger ist §8.2 in Code |
| **MusicBrainz Picard** | Motor | Tonabdruck → Etiketten, von Hand korrigierbar |
| **spotDL** | **Vorbild** | E129 in Code: das Konto liefert die **Liste**, nicht den Ton |
| **MakeMKV** | eigene Scheibe | Blu-ray/DVD → MKV, alle Spuren unangetastet (**Stufe S**) |
| **ffmpeg** / `ffprobe` · HandBrake | Motor | umwandeln — und `ffprobe` ist unser **Messgerät** für E140 |
| **Calibre** | Vorbild | die beste Metadatenkette, die es für Bücher gibt |
| **Kavita** · **Komga** · Kapowarr | Vorbild + Ziel | wir exportieren so, dass sie unsere Bibliothek lesen (E06) |
| **Nicotine+** | Klempnerei | Soulseek — das älteste noch lebende Musiktauschnetz, stark bei Seltenem |

⚠️ **Zur eigenen Blu-ray ohne Abspieler** (JB-Fall): Das Werkzeug ist **MakeMKV**. Und die
ehrliche Fußnote gehört dazu: § 95a UrhG verbietet in Deutschland das Umgehen wirksamer
technischer Maßnahmen, AACS gilt als eine — **ohne Ausnahme für die Privatkopie**. Andere
Länder sehen das anders. Das Werkzeug und die Rechtslage stehen hier; die Entscheidung liegt
beim Nutzer.

⚠️ **Was dieses Dokument nicht enthält und nie enthalten wird:** eine kuratierte Liste von
Piraterieseiten. Nicht aus Zimperlichkeit — sondern weil eine solche Liste **exakt das
Artefakt** ist, wegen dem Tachiyomi eingestellt wurde und 200 Aniyomi-Erweiterungen mit einer
einzigen Meldung verschwanden (E12). Das Programm kann jede Quelle beschreiben, suchen, prüfen
und holen. Welche Quellen es sind, trägt der Nutzer ein.

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

**E177 — was der Mensch bestätigt, wiegt schwerer als was wir messen.** Aus SyncManga
übernommen (`cfm`, `cfmSrc`, `cfmSrcOwn` zum Bestätigen, `rep` zum Meldung eines Defekts →
`data/broken_links.json` → `_consume_broken` in `enrich.py:687`). Ein geschlossener Kreis, der
nirgends im Heft stand:

> **Bestätigt der Nutzer eine Quelle als brauchbar, steigt sie in der Rangliste — dauerhaft und
> über jede automatische Messung hinweg.** Meldet er sie als defekt, fällt sie, auch wenn
> unsere Prüfung sie für erreichbar hält. *Wir messen HTTP-Antworten; ein Mensch sieht, ob
> tatsächlich das Kapitel dasteht, das dastehen soll.*

Das ist die Fortsetzung von E41 („vorschlagen statt verändern") in die andere Richtung: der
Mensch korrigiert nicht nur Titel, sondern auch **unser Urteil über eine Quelle** — und diese
Korrektur überlebt jede Neuanreicherung (E135, Herkunft „Hand").

**E178 — sechs Lesezustände, nicht drei.** SyncMangas `i18n.py` unterscheidet
`st_tip_reading` · `_backlog` · `_caught` · `_finished` · `_paused` · `_paused_long`.
Die wichtigste Erfindung darunter ist **„lange pausiert"**:

| Zustand | Heißt |
|---|---|
| **liest** | in den letzten Wochen weitergekommen |
| **Rückstand** | es gibt mehr, als du gelesen hast |
| **aufgeholt** | du bist am Ende des Erschienenen — es liegt nicht an dir |
| **fertig** | das Werk ist abgeschlossen und du bist durch |
| **pausiert** | eine Weile nichts, aber das kommt vor |
| ⚠️ **lange pausiert** | Monate nichts. **Kein Vorwurf, sondern eine Einladung:** *„Kapitel 63 von 178 — soll ich dich erinnern, wo du warst?"* |

*„Aufgeholt" und „Rückstand" auseinanderzuhalten ist der Unterschied zwischen einem Programm,
das dich hetzt, und einem, das dich informiert.*

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
JSON-Datei, die SyncFindus lokal ausliefert. Zwei Gründe: eine neue Seite ist dann eine Zeile
Text statt zwei Wochen Store-Prüfung — und die Liste steht nirgends öffentlich im Paket
(dieselbe Trennung wie **E12**).

⚠️ **Der ehrliche Haken.** Firefox erlaubt das alles; Chrome baut seit 2024 schrittweise ab,
was wir brauchen, und mag Add-ons nicht, die mit `localhost` reden. Also **Firefox zuerst und
ordentlich**, Chrome als Beipack. Für beide gilt: die Erweiterung ist **Zubehör**. Fällt sie
weg, läuft SyncFindus weiter — dann eben nur mit der `places.sqlite`-Auswertung, die es
ohnehin schon gibt.

### 8.5 Woher der Zustand kommt — sechs Zeugen (E145, E146)

> **Entwurf:** `quellen.html`, Reiter *Zustand · Browser*.

Sechs Datenquellen, nach **Verlässlichkeit** geordnet und **gewichtet** (E31). Jede steht
allein: fällt eine weg, arbeitet das Programm ungenauer weiter — nie gar nicht.

| # | Zeuge | Gewicht | Was er ist |
|---|---|---|---|
| 1 | **Unser eigener Leser / unsere Bühne** | 1,0 | Beweis. Seiten- und sekundengenau, kein Parser |
| 2 | **Die Erweiterung** | 0,9 | Beweis. Meldet Werk + Kapitel an `localhost` (E67) |
| 3 | **Verlauf & Lesezeichen** | 0,6 | Hinweis. `places.sqlite`, Chromium-`History` + `Bookmarks` |
| 4 | **Fremdkonten** | 0,7 | Hinweis. AniList, MAL, Trakt, Spotify — genau, aber alt |
| 5 | **Dateien auf der Platte** | 0,4 | Indiz. Sagt was du *hast*, nicht was du *gelesen* hast |
| 6 | **Dateiname & Adresse** | 0,2 | Verdacht. „Die Adresse ist ein Hinweis, nie ein Beweis" (E76) |

**Ein Lesezeichen wiegt mehr als ein Verlaufseintrag: Absicht schlägt Zufall.**

**Die Sicherheiten** — was schiefgeht und was es abfängt:

| Gefahr | Was wirklich passiert | Sicherung |
|---|---|---|
| **Browser sperrt die DB** | Firefox hält `places.sqlite` mit WAL offen; Lesen liefert Bruchstücke | in den Temp-Ordner **kopieren**, Kopie `immutable` öffnen. **Im Browser wird nie etwas verändert** — harte Regel |
| **Rauschen im Verlauf** | Wayback-Besuche wurden zur Serie *„Wayback Machine"*; ein Newsletter (*„Your Manga Week #16"*) wurde ein Reader; ein Shop wurde eine Serie | Sperrliste **+** Reader-Pfadmuster **+** kuratierte Leseseiten-Liste. Alle drei müssen zusammenpassen |
| **Fehlzuordnung** | zwei ähnliche Titel | **zwei unabhängige Zeugen** (E31); Popularität ist nur Stichentscheid |
| **Falsche Kapitelzahl** | Seite zählt anders, `chapter-953-5` | konstanten Versatz suchen, ab ≥ 80 % speichern **und anzeigen**; sonst Postfach |
| **Rückschritt** | alter Verlaufseintrag setzt 1141 auf 300 | Fortschritt geht nie rückwärts; Sprünge > 20 % ins Postfach |
| **Verlauf gelöscht** | Chrome kürzt nach 90 Tagen; „Browserdaten löschen" wischt alles | **E145** |
| **Privater Modus** | liefert nichts | kein Umweg, keine Trickserei — wer privat liest, will nicht gezählt werden |

> 🔑 **E145 — der Browser ist ein Zeuge, kein Gedächtnis.** Einmal gelesen, gehört der
> Lesestand uns: dauerhaft, mit Datum und Herkunft. Ein geleerter Verlauf ändert **gar
> nichts**. Wer den Browser als Speicher benutzt, verliert alles beim ersten Aufräumen.

> 🔑 **E146 — der Zustand hängt nie an der Identität.** Schlüssel eines Fortschritts ist die
> **stabile ID**, nie der Titel und nie ein Titel-Hash. Belegt am eigenen Schaden: in SyncManga
> war `data-h` einmal `norm(Anzeigetitel)` — **jede Titelkorrektur löschte Archiv, Favoriten
> und Bestätigungen** (JB: *„Mein Archiv hat sich resetted"*). Repariert wurde es mit einer
> Alias-Karte beim Start; richtig gebaut braucht es die nie. Siehe §16.5.

### 8.6 Das Postfach (E141)

> **Entwurf:** `werkseite.html`, Reiter *Das Postfach* — drei Anordnungen.

Der einzige Ausgang für Unsicherheit (E48, E87). Alles Uneindeutige liegt hier, **nichts wird
verworfen**. Die Gefahr ist deshalb nicht Datenverlust, sondern das Gegenteil: ein Postfach,
das auf 3.000 Einträge wächst und nie wieder angefasst wird.

Drei Anordnungen wurden gezeichnet: **Der Stapel** (ein Fall, groß, mit Bildern, per Tastatur)
· **Die Liste** (Häkchen, Massenaktion) · **Der Trichter** (nach Grund gruppiert).

> 🔑 **Der Trichter ist der Rahmen, der Stapel der Arbeitsmodus.** Gleiche Ursache = gleicher
> Griff: „6 × zwei Kandidaten, alle über 90 %" ist **eine** Entscheidung statt sechs. Was
> übrig bleibt, sind die echten Fälle — und die öffnen sich als Stapel.

> 🔑 **E141 — das Postfach wächst nie stumm, und es muss leer werden können.** Drei Pflichten:
> **1. Sichtbar** — eine Zahl in der Seitenleiste, immer. Wird sie zweistellig, ohne dass
> jemand hinsieht, ist eine **Regel** kaputt, nicht der Mensch faul.
> **2. Jeder Fall hat einen Standard-Ausgang** — es gibt keinen Eintrag, für den nur „du musst
> nachdenken" gilt. *Ein Postfach ohne Standardausgänge ist ein Friedhof.*
> **3. Entscheidungen werden zu Regeln** — wer dreimal dasselbe entscheidet, bekommt „daraus
> eine Regel machen" angeboten, mit dem Satz der Regel im Klartext. Die Regel landet in der
> Werkstatt und ist dort **rücknehmbar** (E41).

**Die sechs Gründe — mehr darf es nicht geben.** Ein siebter heißt: die Erkennung hat eine
neue Sorte Unsicherheit erfunden, und die gehört benannt statt versteckt.

| Grund | Was wir zeigen | Standard-Ausgang |
|---|---|---|
| **Zwei Kandidaten** | 3 Vorschläge mit Titelbild, Prozent, Quelle — *wiedererkennen statt erinnern* | bester Treffer, wenn ≥ 90 % **und** Abstand ≥ 5 Punkte |
| **Kein Treffer** | Dateiname zerlegt, was daran gelesen wurde | Suchfeld vorbelegt — **nie** automatisch verwerfen |
| **Kapitelsprung** | deine Zählung vs. die der Seite, gefundener Versatz | Versatz vorschlagen, wenn er für ≥ 80 % passt |
| **Doppelt** | beide Ausgaben mit **gemessener** Stufe nebeneinander (E140) | höhere Stufe behalten, andere ins Archiv |
| **Widerspruch** | was die Messung sagt, was die Behauptung sagt | Messung übernehmen, Behauptung merken |
| **Kein Medium** | als **Bündel**, nicht als 89 Zeilen | als *Eigenes* ablegen — nie löschen (E13) |

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

#### E163 — Der Katalog verlässt das öffentliche Repo (F05 entschieden)

**JB, 08.08.2026:** *„Ich würde sagen, du entscheidest mit den Dateien aus dem Repo. Ich weiß
es nicht. Ich kann nicht einschätzen, wie wichtig das ist."*

> 🔑 **Entscheidung: ja. `data/sources.json` und `data/readers_pattern.json` kommen aus dem
> öffentlichen Repo heraus.**

**Wie wichtig ist es wirklich?** Ehrlich abgewogen, beide Seiten:

| Dafür, sie zu entfernen | Dagegen |
|---|---|
| Es ist **exakt** die Artefaktklasse, die Projekte tötet: Sony nahm 200 Aniyomi-Erweiterungen mit *einer* Meldung offline; FAKKU ging 03/2026 gegen Mihon-Repos vor; Kakao drohte Tachiyomis Entwicklern **persönlich**, bis das Projekt einging | Die Dateien enthalten **Domainnamen**, keine Inhalte — juristisch eine schwächere Angriffsfläche als eine Extension |
| Ein Repo mit einer kuratierten Leseseiten-Liste ist **auffindbar** — genau danach wird gesucht | Bisher ist nichts passiert, und SyncManga nutzen zwei Leute |
| Die Entfernung **kostet nichts**: E12 verlangt ohnehin abonnierbare Laufzeitlisten, und §7.5 hat vier gepflegte Protokolle, die es besser können | Es ist Arbeit, und die Historie behält die Dateien ohnehin |

**Warum ich mich trotzdem klar entscheide:** Das Risiko ist **asymmetrisch**. Bleiben die
Dateien liegen und nichts passiert, gewinnen wir *null*. Bleiben sie liegen und es passiert
etwas, verlieren wir das Repo, den Namen und die Historie — und rückgängig machen lässt sich
das nicht. **Bei so einem Verhältnis entscheidet man nicht nach Wahrscheinlichkeit, sondern
nach Schadenshöhe.**

⚠️ **Und ein Punkt, der oft übersehen wird:** Ein `git rm` reicht nicht — die Dateien bleiben in
der **Historie** abrufbar. Wer sie wirklich entfernen will, muss die Historie umschreiben
(`git filter-repo`) und einmal erzwungen pushen. Das ist ein echter Eingriff und braucht JBs
ausdrückliche Zustimmung, weil es alle vorhandenen Kopien des Repos entwertet.

**Der Weg, in dieser Reihenfolge:**

1. **`readers_pattern.json` und `sources.json` aus dem Paket nehmen** und in eine
   **Laufzeitliste** überführen (E12), die beim ersten Start aus einer abonnierbaren Adresse
   geholt wird — oder eben nicht, wenn niemand eine einträgt.
2. **Die eingebauten Verteidigungslisten bleiben**: `PAYWALL_SITES`, `UNSAFE_SITES`, die
   Rausch-Sperrliste. Das sind **Schutzregeln**, keine Quellenliste — sie sagen, wo man *nicht*
   hinsoll.
3. **Der Rest von SyncManga bleibt öffentlich.** Die Reader-Engine, die Anreicherung, die
   Parser — das ist der Teil, auf den wir stolz sein können, und **er war nie das Ziel von
   Angriffen** (E12).
4. **Historie erst umschreiben, wenn JB zustimmt** — bis dahin sind die Dateien wenigstens
   nicht mehr im aktuellen Stand.

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

### 9.6 Das Rennen (E149, E150)

**JB, 08.08.2026:** *„Was wichtig an der Warteschlange ist, dass nichts aufgehalten wird. Wenn
z. B. YouTube blockiert durch Länderzonen, oder wenn ein Torrent keine Seeder mehr hat, oder
alle Seeder seit Stunden offline sind. Oder ein Direktdownload fehlerhaft ist. Wie garantieren
wir Sicherheit und Erfolg?"*

**Garantieren kann man nichts.** Man kann nur dafür sorgen, dass ein Fehlschlag **nichts kostet
außer Zeit, die ohnehin parallel läuft**. Der ganze Trick steckt darin, den Auftrag anders zu
formulieren:

| | Auftrag ❌ | Wunsch ✅ |
|---|---|---|
| **lautet** | „lade Frieren 09 von dort" | „beschaffe Frieren 09, mind. Stufe B, JP + Sub DE" |
| **Quelle tot** | scheitert | Kandidat 2 von 5 übernimmt — **ohne dass jemand etwas merkt** |
| **Geo-Sperre** | rot | ein **Ablöseschritt**, kein Fehler |
| **alles gescheitert** | stirbt, du erfährst es nie | **lauert** und schlägt zu, wenn eine neue Quelle auftaucht |

> 🔑 **E149 — Beschaffung ist ein Rennen, kein Auftrag.**

| Regel | Warum |
|---|---|
| **Vorprüfung kostet keine Bytes** | Seederzahl aus DHT/Tracker **vor** dem Start. Direktlink per `HEAD`: Größe plausibel? `Accept-Ranges` da? Inhaltstyp richtig? **Ein Kandidat, der sich nicht fortsetzen lässt, ist ein schlechter Kandidat — und das weiß man vorher, nicht nach 4 GB.** |
| **Ablösung statt Abbruch** | Fällt die Rate über 3 Minuten unter ein Viertel des Erwarteten, startet Kandidat 2 **parallel**. Wer zuerst fertig ist, gewinnt; der Langsame wird **überholt**, nicht abgebrochen |
| **Teildaten bleiben** | Bei Torrents zählen sie ohnehin weiter, bei HTTP mit `Range` setzt der nächste Versuch dort an. **Nichts wird zweimal geladen** |
| **Geo ist ein Schritt** | `geo.py` und `vpn.py` aus SyncYouTube **existieren bereits**. „In DE gesperrt" heißt: nächster Ausgang, nicht rot |
| **Spuren sind getrennt** | Ein hängender Torrent belegt **keinen** Platz beim Prüfen, Veredeln oder Anreichern. Deshalb hält nie etwas etwas anderes auf |

> 🔑 **E150 — der Wunsch stirbt nie.** Scheitern alle Kandidaten, bleibt der Wunsch stehen und
> **lauert**: er wird bei jeder neuen Quelle, jedem RSS-Treffer, jeder neu abonnierten Liste
> automatisch neu bewertet. **Ein Auftrag scheitert. Ein Wunsch wartet.** *Berserk 374 gibt es
> heute nicht über Stufe C — in vier Wochen schon, und dann passiert es von selbst.*

**Die drei Sicherheiten, die nichts mit Erfolg zu tun haben, aber alles mit Ruhe:**
1. Was hereinkommt, wird geprüft, **bevor** es die Bibliothek berührt — Dateityp gegen Inhalt
   (nicht gegen Endung), `ffprobe` muss die Datei verstehen, Archive nie entpackt-und-ausgeführt.
2. Alles Netzwerkige schreibt **nur in einen Eingangsordner**, nie in die Bibliothek.
3. **Kein Beschaffungsweg darf je den Leser oder die Bühne blockieren.** Was gerade angesehen
   wird, hat immer Vorrang (§4.5).

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

### 10.2.1 Die Übersetzung im Bild (E134–E137)

> Entwurf: `uebersetzung.html` (07.08.2026)

**E135 — das Glossar schlägt jedes Modell.** Ein gutes Modell übersetzt eine einzelne Zeile heute
schon sehr gut. Was es **nicht** kann, ist sich an Kapitel 41 zu erinnern — es sei denn, jemand
schreibt die Entscheidung auf.

| Woher ein Glossareintrag kommt | Rang |
|---|---|
| **deine Handkorrektur** | 1 — gewinnt immer |
| die **offizielle** Ausgabe, wenn es eine gibt | 2 |
| AniList/MangaUpdates-Namen | 3 |
| die häufigste Fassung in den Fan-Übersetzungen | 4 |
| Vorschlag des Modells | 5 |

⚠️ **Nie stumm überschreiben.** Ändert eine Quelle ihre Meinung, wird daraus ein Eintrag im
**Postfach**, keine automatische Korrektur (E41, E87).

**Rückwirkend besser werden:** eine Glossarzeile ändern ⇒ alle betroffenen Stellen wandern in die
Warteschlange. ⚠️ **Der Lesestand bleibt** — er hängt am Werk, nicht an der Ausgabe (E76).
Kein Zurückspringen, kein Verlust.

**E136 — Blasenprüfung.** Beim Manga ist nicht die Übersetzung das Problem, sondern der **Platz**.
Nach jedem Satz wird gemessen: passt er in die Sprechblase, bei welcher Zeilenzahl, bei welcher
Füllung? Passt er nicht, ist er **falsch** — auch wenn er schöner ist.
Rangfolge: Bild behalten → kürzen → Weg 3 (E137). **Nie über den Rand.**

**E134 — Englisch zuerst.** Zielsprache ist **Englisch**, weil dort die meisten Fan-Fassungen
fehlen und die Vorlagen am besten sind. **Deutsch ist der zweite Lauf — und er läuft aus
unserer englischen Fassung, nicht aus dem Original**, weil das Glossar dann schon steht.
Zwei Sprünge klingen nach Verlust, sind aber besser: der zweite erbt jede Entscheidung des ersten.

#### E137 — Sprichwörter (F03 beantwortet)

Wörtlich übersetzt ergibt es Unsinn; ersetzt man es, klingt ein koreanischer Jäger plötzlich wie
ein englischer Landwirt. **Es gibt keine Lösung, nur drei Wege.**

| Weg | Was | Wann |
|---|---|---|
| **1 · Ersetzen** | echtes Sprichwort der Zielsprache mit gleicher Bedeutung | nur bei Werken **ohne Ortsbezug** (Isekai, reine Fantasy) |
| **2 · Bild behalten, erklären** | wörtlich, mit punktierter Linie beim **ersten** Vorkommen je Kapitel; Erklärung auf Antippen | **Standard** bei allem, was in der Ursprungskultur spielt |
| **3 · Sinn ohne Bild** | reine Bedeutung, kein Sprichwort | Rückfall, wenn Weg 2 nicht in die Blase passt (E136) |

**Entschieden wird in dieser Reihenfolge:** spielt das Werk in der Ursprungskultur? → passt Weg 2
in die Blase? → steht es überhaupt in einer Sprichwortsammlung (sonst normal übersetzen)? → gibt
es eine offizielle Fassung (die gewinnt, auch gegen unseren Geschmack)? → **schon einmal
entschieden? Dann steht es im Glossar und wird nie wieder neu entschieden.**

> ⚠️ **Ehrlich:** Sprichwörter sind die Stelle, an der eine gute Fan-Gruppe uns weiterhin schlägt —
> sie *kennt* die Serie und weiß, ob die Figur gerade ironisch ist. Unser Ausgleich ist nicht
> Klugheit, sondern **Beständigkeit und Umkehrbarkeit**: jede Entscheidung steht im Glossar,
> ist mit einem Klick änderbar, und die Änderung gilt rückwirkend.

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

#### E138 — Mehrere Stimmen sichtbar machen

**JB-Frage 07.08.2026:** *„Was ist, wenn mehrere Stimmen sprechen?"*

| | |
|---|---|
| **Über dem Text** | höchstens **drei** Stimmen als Marken mit Farbpunkt (`Thorfinn` · `Einar` · `Erzähler`), danach *„+ N weitere"*. Mehr als drei liest niemand im Vorbeigehen |
| **Im Mitlesen** | jede Zeile bekommt links den **Punkt ihres Sprechers**. Damit sieht man beim Lesen, wer spricht, ohne dass Namen im Text stehen |
| **Die Farbe** | kommt aus dem **Werk-Wissen** (§10.1) — dieselbe Figur hat im ganzen Werk dieselbe Farbe, auch in der Besetzungskarte (E124) und im Glossar |
| ⚠️ **Nicht** | keine Namen im Fließtext, keine eingefärbten Wörter. Das war schon beim Leser die falsche Idee, und beim Hörbuch wäre es schlimmer |
| **Ein-Stimmen-Fall** | steht nur der Name, ohne Punkt und ohne Marken im Text — die häufigste Form soll die ruhigste sein |

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
> SyncFindus über dich" — sichtbar, editierbar, exportierbar, löschbar. Netflix und Spotify
> verstecken das. Es ist die einzige ehrliche Antwort auf „wie schärfe ich meine Meinung".

#### E160 — Die Lücken-Liste ist der Eingang zur Beschaffung

> **Entwurf:** `regale.html`, Reiter *Die Lücken-Liste*.

**JB, 08.08.2026:** *„Die Lückenliste ist also eine Art Download, oder?"* — **Ja, und genau das
ist der Punkt.** Sie ist kein Bericht, den man liest und wegklickt, sondern der Ort, an dem aus
**◐ gekannt** ein **Wunsch** wird (E150).

Kein anderes Programm kann diese Liste bauen, weil kein anderes weiß, **was du gelesen hast,
ohne es zu besitzen** — dafür gibt es die sechs Zeugen (§8.5).

> 🔑 **Jede Zeile hat genau eine Tat: wünschen.** Der Wunsch geht in die Warteschlange (E149),
> scheitert er, lauert er (E150) — und taucht Wochen später von selbst als fertiges Werk im
> Regal auf. **Der Weg von „das kenne ich" zu „das habe ich" ist ein Klick und danach Geduld.**

Drei Gestaltungsregeln, die den Unterschied machen:

| Regel | Warum |
|---|---|
| **Sie beschämt nicht** | Die Zahl oben heißt *„du kennst 812 Werke"*, nicht *„dir fehlen 381"*. Dieselben Daten, ein anderes Programm |
| **Erreichbarkeit steht dabei** | „Wünschen" ohne Aussicht ist eine Enttäuschung mit Verzögerung. Steht *nur Stufe C* dran, weißt du es **vorher** |
| **Kein Abzeichen in der Seitenleiste** | Die Lücken-Liste ist ein Ort, den man **aufsucht** — kein Zähler, der ruft. *Das ist der Unterschied zum Postfach, das rufen **muss** (E141).* |

**E148 — der Kalender empfiehlt, die Bilanz nicht.** Der Jahresrückblick („Wrapped") wurde
verworfen: er sagt dir, was du schon weißt, einmal im Jahr, und ändert nichts. Der Kalender
dagegen **verändert, was gerade richtig ist** — und zwar ganzjährig:

| Anlass | Was hochkommt | Woher wir es wissen |
|---|---|---|
| **Jahreszeit** | Winterfilme im Dezember, Horror im Oktober, Sommerfilme im Juli | Genre + Stichwörter (TMDB `keywords`: *christmas*, *summer camp*) |
| **Jahrestag** | „vor 10 Jahren erschienen", „vor 5 Jahren gesehen" | Erscheinungsdatum + eigener Verlauf |
| **Saison** | die neue Anime-Saison beginnt — was davon liegt schon im Regal | AniList `season` + `seasonYear` |
| **Wetter** | Regentag → lange Formate, Hitze → kurze | ⚠️ optional, braucht Ortsdaten → standardmäßig **aus** |
| **Uhrzeit** | 23 Uhr: kein 3-Stunden-Film, sondern eine 24-Minuten-Folge | lokale Zeit, keine Datenquelle nötig |

⚠️ **Ein Anlass darf höchstens einen Platz im Regal belegen** — sonst wird im Dezember alles
weihnachtlich, und das Regal hört auf, deine Bibliothek zu sein.

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

#### E155 — Pflicht wird gezeigt, nicht versteckt

> **Entwurf:** `erststart.html`, Reiter *Der Installer*.

**JB, 08.08.2026:** *„Installer und erster Start ist super wichtig. Es gibt bestimmt einiges an
Fremdsoftware — wenn etwas Pflicht ist, dann sollte der Haken auf einem ausgegrauten Feld sein.
Der User muss informiert sein, aber wissen, dass ohne das Programm nicht geht."*

**Das ist genau richtig, und die meisten machen es falsch.** Zwei verbreitete Fehler:
Pflichtbestandteile **gar nicht zeigen** (das Programm installiert heimlich etwas —
Vertrauensbruch beim allerersten Kontakt) oder sie **abwählbar aussehen lassen** und dann
meckern (der Nutzer wurde verarscht). **Gesetzt und ausgegraut** ist die einzige ehrliche Form:
man sieht es, man versteht warum, und man merkt sofort, dass es nicht zur Debatte steht.

> 🔑 **Drei Klassen, drei Sätze. Jeder Bestandteil hat genau einen davon.**

| Klasse | Haken | Der Satz |
|---|---|---|
| **Pflicht** | gesetzt, **ausgegraut** | *„Ohne das gibt es **X** nicht."* |
| **Empfohlen** | gesetzt, änderbar | *„Ohne das verlierst du **Y**."* |
| **Optional** | leer, änderbar | *„Wenn du es einschaltest, bekommst du **Z**."* |

**Pflicht** sind nach heutigem Stand vier: **mpv** (ohne Bild und Ton keine Bühne, E34) ·
**ffmpeg/ffprobe** (ohne Messgerät keine Güteleiter, E140) · **yt-dlp** (ohne HTTP-Adapter
bleibt genau ein Kandidat im Rennen, E149) · **SQLite** (das Register *ist* die Wahrheit, E151).

**Bei jedem Bestandteil steht: Größe, Lizenz, Zweck in einem Satz.** Wer 4,1 GB für ein
Übersetzungsmodell herunterlädt, darf das vorher wissen; wer GPL-3 nicht will, auch.

⚠️ **Was nie passiert:** kein vorausgewähltes Extra, keine Symbolleiste, keine Suchmaschine,
kein „auch installieren". *Der Installer ist der erste Vertrauensbeweis — und der einzige, den
man nur einmal geben kann.*

#### Der erste Start — das leere Programm

Der **einzige Bildschirm, den jeder Nutzer sieht**, und der einzige, auf dem noch nichts da
ist. Vier Kacheln, **jede ein vollständiger Weg, keine Reihenfolge**:

| Weg | Was passiert |
|---|---|
| **Einen Ordner zeigen** | Was da liegt, wird zu Werken. Nichts wird verschoben oder umbenannt |
| **Aus dem Browser lesen** | Verlauf und Lesezeichen einmal durchsehen — read-only (§8.5) |
| **Ein Konto verbinden** | AniList/MAL/Trakt — die Listen kommen, der Inhalt nicht (E129) |
| **Einfach umsehen** | Nichts einlesen. Suchen, stöbern, ein erstes Werk wünschen |

Kein Assistent mit sieben Schritten — der erste Start hat in jedem Programm die höchste
Abbruchrate. Und der wichtigste Satz steht ganz unten: **nichts wird gelöscht, umbenannt oder
verschoben.** Wer 64 TB hat, klickt sonst nirgends drauf, zu Recht.

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

#### E147 — Der Bruchtest

**Was das ist** (JB fragte danach): Ein Test prüft *eine Sache, die du dir ausgedacht hast*.
Ein **Bruchtest** prüft *eine Regel, die immer gelten muss* — an **echten Daten, im laufenden
Betrieb**, ohne dass jemand einen Testfall geschrieben hat. Er sucht nicht nach dem Fehler,
den man erwartet, sondern nach dem **Widerspruch**, den niemand erwartet hat.

**Wie er läuft:** Bei jedem Beenden — der einzige Moment, in dem das Programm garantiert
nichts Wichtiges tut — wird **genau eine** Invariante gezogen und gegen den echten Bestand
geprüft. Eine, nicht alle: das dauert Millisekunden und fällt nie auf. Über hundert Starts
sind hundert Stichproben; über ein Jahr ist jede Invariante hundertfach an echten Daten
geprüft worden. **Ein Widerspruch wird nie repariert, sondern gemeldet** — er landet im
Postfach mit dem Satz der verletzten Regel im Klartext.

| Gezogene Regel | Widerspruch, den sie fände |
|---|---|
| *Jede Ausgabe gehört zu genau einem Werk* | eine Datei hängt nach einer Zusammenführung an zwei Werken |
| *Kein Werk hat zwei Einheiten mit derselben Nummer* | ein Kapitelversatz wurde zweimal angewandt |
| *Jede Datei im Register existiert auf der Platte* | jemand hat einen Ordner verschoben |
| *Jede Datei auf der Platte steht im Register* | ein Download ist an der Warteschlange vorbeigelaufen |
| *Kein Fortschritt liegt über der Gesamtzahl* | Kapitel 1150 von 1148 gelesen — Zählung kaputt |
| *Jede Handkorrektur ist noch da* | eine Neuanreicherung hat sie überschrieben |

⚠️ **Der Bruchtest braucht E52** (deterministischer Kern). Ohne reproduzierbaren Lauf ist ein
gemeldeter Widerspruch nicht nachstellbar und damit wertlos.

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

### 12.7 Sicherung und Wiederherstellung (E166)

> **Entwurf:** `sicherung.html`.
> ⚠️ **Am 08.08.2026 überarbeitet, nachdem JB einen echten Fehler gefunden hat.** Die erste
> Fassung hatte drei Ringe und setzte stillschweigend voraus, dass das Register auf dem PC
> liegt. Es liegt aber auf dem NAS. Siehe „Der Einwand" unten.

64 TB Dateien lassen sich neu holen. **Der Lesestand nicht.** JB, 08.08.2026: *„Mir sind die
Infos, was ich bereits gelesen und gesehen habe, wichtiger als die Daten selbst. Die kann ich
mir immer wieder ansammeln."* — Genau so ist es gebaut:

| Unersetzlich → wird gesichert | Ersetzbar → wird nicht gesichert |
|---|---|
| Register · Fortschritt · **Handkorrekturen** · Glossar · Wünsche (auch lauernde) · Einstellungen bis zum Untertitel-Versatz je Titel · Spielstände | Mediendateien (64 TB) · Titelbilder · angereicherte Metadaten · erzeugte Übersetzungen und Vertonungen · Quellenkatalog · Protokolle |
| **zusammen unter 500 MB bei 800 Werken** | |

#### Der Einwand — und warum er richtig ist

**JB:** *„Erklär mir, was eine Kopie auf dem NAS bringt, wenn die Daten eh auf dem NAS sind.
Ich werde keine Daten auf meinem PC speichern."*

⚠️ **Gar nichts, und das war ein Fehler im ersten Entwurf.** Ich hatte die 3-2-1-Regel
übernommen, ohne sie auf **diese** Anlage anzuwenden. Sie stammt aus Serverräumen: *drei
Kopien, zwei Datenträger, eine außer Haus.* Bei einem Menschen mit **einem** NAS heißt „zwei
Datenträger" nichts, solange beide im selben Gehäuse stecken — eine Kopie von der NAS-Platte
auf die NAS-Platte ist **Theater**.

> 🔑 **E166, überarbeitet: zwei Ringe. Einer gegen unsere Fehler, einer gegen den Verlust des
> NAS. Was dazwischen lag, waren nie zwei Ringe, sondern einer mit zwei Qualitätsstufen.**

| | Wo | Takt | Fängt ab |
|---|---|---|---|
| **1 · Der Schnappschuss** | **auf dem NAS**, neben dem Register | stündlich · beim Beenden · vor jeder Änderung am Aufbau | **Unseren eigenen Fehler.** Eine kaputte Umstellung, ein Import, der überschrieben hat, ein versehentliches „alles als gelesen". Kostet Sekunden (`VACUUM INTO`, sperrt nicht) und ein paar hundert MB |
| **2 · Die Kopie, die nicht das NAS ist** | irgendwo sonst | täglich | **Alles andere.** Controller stirbt, Netzteil stirbt, zwei Platten gleichzeitig, Trojaner, Diebstahl, Feuer, ein falsches `rm` |

**Und hier ist der Punkt, der deinen Einwand auflöst:** Das Register ist **unter 500 MB**.
Das ist kein „Daten auf dem PC speichern" — das ist die Größe von zwei Filmen im Handygepäck.
Es passt auf **alles**:

| Ziel | Taugt gegen | Aufwand |
|---|---|---|
| **USB-Stick in der Schublade** | Ausfall, Trojaner, Diebstahl des NAS | einmal einstecken |
| **Ein Ordner auf dem PC** | dasselbe | 500 MB — das ist keine Datenhaltung, das ist eine Datei |
| **Dein eigener Server** (nicht das NAS) | dasselbe + Feuer, wenn er woanders steht | einmal einrichten |
| **Verschlüsselter Speicherdienst** | alles, auch Wohnungsbrand | einmal einrichten, ⚠️ **versioniert und nur anfügend**, sonst nützt er gegen Trojaner nichts |

**Was RAID nicht ist.** Ein NAS mit Plattenspiegelung überlebt den Ausfall **einer Platte** —
und sonst nichts. Es schützt nicht gegen Löschen, nicht gegen Verschlüsselung, nicht gegen
einen kaputten Schreibvorgang, und schon gar nicht gegen Diebstahl. *RAID ist
Verfügbarkeit, keine Sicherung.* **Deshalb bleibt Ring 2 nötig, so klein er auch ist.**

#### Der Rückspiel-Test — die einzige Zeremonie, die bleibt

Alles oben ist Handwerk. Das hier ist der Teil, den fast niemand macht — und der Grund, warum
Sicherungen im Ernstfall so oft nutzlos sind: nicht weil nicht gesichert wurde, sondern weil
die Sicherung defekt war und **es niemand wusste**.

> **Einmal im Monat, automatisch, ohne Nachfrage:** die **älteste** Kopie aus Ring 2 in einen
> Temp-Ordner zurückspielen, Werke und Fortschrittseinträge zählen, den **Bruchtest (E147)
> gegen die Kopie** laufen lassen. Bei Erfolg still. Bei Misserfolg ist es einer der drei
> Anlässe aus **E164** — *„etwas ist kaputt und du merkst es sonst nicht."*

Die älteste, nicht die neueste: wer die neueste testet, testet den einfachsten Fall.

#### Die Wiederherstellung

| Regel | Warum |
|---|---|
| **Nie überschreiben, immer daneben** | Die laufende Datenbank wird vor jeder Wiederherstellung selbst zum Schnappschuss. Wer sich vergreift, hat sonst zwei Katastrophen |
| **Vorher zeigen, was drin ist** | *„Diese Sicherung ist vom 12.07. mit 812 Werken — deine jetzige hat 819."* **Die Differenz steht da, bevor man klickt** |
| **Teilweise geht auch** | Nur das Glossar. Nur ein Werk. Der häufigste Ernstfall ist nicht „alles weg", sondern **„ich habe eine Sache kaputtgemacht"** |
| **Ohne das Programm lesbar** | Neben der Datenbank liegt der Export aus **E14** — CSV und JSON, derselbe Stand. Falls SyncFindus selbst das Problem ist, oder es in zehn Jahren nicht mehr gibt |

#### Der dritte Ring, den wir nicht bauen müssen

⚠️ **Das Wichtigste liegt ohnehin doppelt** — und zwar ohne dass wir dafür etwas tun:

Sobald **E170** steht (Fortschritt fließt in beide Richtungen), lebt *„was habe ich gesehen"*
in **zwei unabhängigen Systemen**: bei uns im Register und auf dem Jellyfin-Server. Dasselbe
gilt für AniList und MyAnimeList, sobald ein Konto verbunden ist. **Das ist keine Sicherung,
die wir gebaut haben — es ist eine Redundanz, die wir geschenkt bekommen**, weil wir
zurückschreiben statt nur zu lesen.

> **Die Folge, und sie ist beruhigend:** Selbst im vollständigen Katastrophenfall — NAS weg,
> Ring 2 weg — wäre der Lesestand nicht verloren, sondern **rekonstruierbar**: aus Jellyfin,
> aus AniList, aus dem Browserverlauf (§8.5). Es wäre mühsam und lückenhaft, aber es wäre
> nicht null. *Ein System, das seine wichtigsten Daten zurückgibt statt sie zu horten, sichert
> sich nebenbei selbst.*

#### E168 — Löschen geht in den Papierkorb

Aus SyncYouTube geerbt (`_in_papierkorb`, `_datei_loeschen`) und bisher nirgends
aufgeschrieben: **das Programm löscht nie endgültig.** Alles Entfernte geht in den Papierkorb
des Betriebssystems, wo der Nutzer es sieht und zurückholen kann — billiger als jede eigene
Rücknahme-Logik und von jedem Menschen sofort verstanden. **Auch nicht für Zwischenspeicher,
auch nicht beim Aufräumen, auch nicht auf ausdrücklichen Wunsch.**

#### E171 — Eine Registerdatei, ein Programm

Aus SyncManga übernommen (`single_instance`, `_is_own_process`, `_kill_if_ours`) — und **nach
E151 keine Bequemlichkeit mehr, sondern Pflicht.** Solange der Zustand in einer HTML-Datei
wohnte, waren zwei laufende Kopien lästig. Auf **einer** SQLite-Registerdatei sind sie eine
Katastrophe mit Ansage — und **auf einem NAS gilt das doppelt**, weil dort auch zwei
*verschiedene Rechner* zugreifen können.

> **Beim Start wird eine Sperrdatei genommen.** Läuft schon eine Kopie, wird **die vorhandene
> nach vorn geholt** statt einer zweiten gestartet — das ist die Antwort, die der Nutzer
> erwartet, wenn er zweimal aufs Symbol klickt. Eine tote Sperrdatei (Absturz) wird erkannt und
> nur dann geräumt, wenn der eingetragene Prozess **nachweislich unserer war**. Über Netz
> gilt zusätzlich: die Sperre trägt Rechnernamen und Zeitstempel, damit man sieht, **wer**
> gerade dran ist (E161 — wer davorsitzt, gewinnt).

#### E172 — Prüfen vor dem Tausch

Aus SyncMangas `update.py` (419 Z.) — vier Regeln, die alle bezahlt wurden:

> **1.** Nichts löschen, keine System- oder Rechteänderungen. **2.** Vor jedem Tausch ein
> `.bak` des Alten. **3.** Heruntergeladene Daten **vor** dem Tausch prüfen — ungültig heißt:
> die alte Datei bleibt. **4.** Immer atomar schreiben (`tmp` + `os.replace`).

⚠️ **Was ausdrücklich nicht mitkommt: der Selbstneustart bei Codeänderung im Leerlauf**
(`_quell_signatur`, `_code_leerlauf`, `_selbst_neustart`). Das war klug für ein Skript, das man
selbst bearbeitet. Für ein **signiertes Programm** ist ein Prozess, der seinen eigenen
Quelltext beobachtet und sich selbst austauscht, genau das Verhalten, das Virenscanner und
Smart App Control als Schadsoftware werten — und dann ist die Signatur wertlos, für die wir
gerade Wochen aufwenden (§12.1). **Erneuert wird beim Start, nicht im Betrieb.**

#### E173 — Heilen ist die zweite Hälfte des Bruchtests

§12.6 beschreibt bisher nur das **Finden**. SyncYouTube hat längst acht Reparaturen —
`queue_heilen`, `pfade_heilen`, `_abo_heilen`, `dubletten_heilen` mit `_dubletten_score`,
`untertitel_aufraeumen`, `_vtt_verwaist`, `wiedergabe_sub_altlast_raeumen`,
`_fehler_aufraeumen`.

> 🔑 **Jeder Fund kennt seinen Reparaturvorschlag — und führt ihn nie selbst aus.**
> Der Bruchtest schreibt ins Postfach: *„Regel verletzt: jede Datei im Register existiert auf
> der Platte. 14 Einträge betroffen."* Daneben steht der Vorschlag: *„Die 14 als **vermisst**
> markieren (E28)."* **Ein Griff, umkehrbar, mit Namen.**

Das ist derselbe Bau wie E141 im Postfach: **jeder Fall hat einen Standard-Ausgang, aber
niemand nimmt ihn ungefragt.** Einzige Ausnahme bleibt die **Dublettenbewertung** — sie darf
vorschlagen, welche Ausgabe die bessere ist, weil das eine Messung ist (E140) und keine
Meinung.

#### E175 — Das Programm zeigt sich im Infobereich

Aus SyncMangas `tray.py` (619 Z.): Symbol mit **Zustandsemblem** — Farbpunkt nach Zahl toter
Quellen, Betriebsanzeige während eines Laufs, Abzeichen bei verfügbarer Neuerung, Kurzhinweis
mit Namen. **So weiß man, dass das Programm lebt, ohne es zu öffnen.**

> Es gilt dieselbe Sparsamkeit wie bei den Meldungen (E164): **das Symbol informiert, es ruft
> nicht.** Rot heißt „etwas hängt", nicht „komm sofort her". Und ein Klick öffnet das Fenster —
> er startet nie eine Handlung.

### 12.8 Sprache der Oberfläche (E167)

> 🔑 **Zwei Sprachen kommen mit, gepflegt: Deutsch und Englisch. Alle weiteren sind eine
> Datei, die jemand danebenlegt.**

**Warum genau zwei.** Eine dritte Sprache, die niemand korrekturlesen kann, ist **schlechter
als keine**: sie sieht fertig aus, ist es nicht, und der Nutzer merkt es erst an der Stelle,
an der es weh tut. Deutsch, weil JB darin denkt. Englisch, weil ohne Englisch niemand außerhalb
das Programm ausprobiert — und weil die Übersetzung ohnehin nach Englisch zuerst geht (E134).

⚠️ **Die wichtigere Unterscheidung, die bisher fehlte:** Die Sprache der **Oberfläche** und die
Sprache des **Inhalts** sind zwei verschiedene Einstellungen. Wer die Oberfläche auf Englisch
stellt, will nicht automatisch englische Untertitel — und umgekehrt. `i18n.py` regelt das
Erste, §10.2 das Zweite; **sie dürfen sich nie gegenseitig setzen.**

**Weitere Sprachen:** eine JSON-Datei mit denselben Schlüsseln, in einen Ordner gelegt,
erscheint in der Auswahl — mit dem sichtbaren Vermerk **„von der Gemeinschaft, ungeprüft"**
und dem Namen dessen, der sie beigesteuert hat. Der **Text-Wächter** (§12.6) prüft sie beim
Laden: fehlende Schlüssel, Überlängen in fester Breite, CJK-Zeichen in einer lateinischen
Sprache. Fällt sie durch, wird sie **nicht geladen** und der Grund steht dabei.

### 12.9 Datenträger einlesen (E47)

⚠️ **Rechtslage Deutschland:** § 95a UrhG verbietet das Umgehen wirksamer technischer
Schutzmaßnahmen (AACS, BD+, Cinavia). § 53 UrhG erlaubt die Privatkopie, aber nicht das
Brechen des Schutzes dafür. Der Widerspruch ist bekannt und gewollt. **JB hat das zur
Kenntnis genommen und für sein autarkes System entschieden** (06.08.2026).

**Bauform — dieselbe Trennung wie beim Quellenkatalog (E12):**

> **SyncFindus entschlüsselt nichts selbst.** Es ruft ein **externes Werkzeug** auf, das der
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
| ~~F02~~ | ~~Endgültiger Name~~ → **beantwortet 08.08.2026: SyncFindus** (JB: *„Mein Kater heißt so, als Findus."*) | — |
| ~~F03~~ | ~~Sprichwörter~~ → **beantwortet: E137** (drei Wege, die Verortung entscheidet) | — |
| F04 | Wie stark **Namens-Verwestlichung** — Voreinstellung an oder aus? | §10.2 |
| ~~F05~~ | ~~Quellendateien aus dem öffentlichen Repo?~~ → **beantwortet: E163 — ja, sie kommen raus** (JB delegierte die Entscheidung; Begründung in §9.2) | — |
| F06 | **Quellen-Späher**: halbautomatisch mit Vorschlagsliste, oder nur Meldung? | §7.3 |
| F07 | **Text-Korrektur** schlecht lektorierter Verlagstexte — wie weit darf die KI eingreifen? | §10.2 |
| F08 | **Eigene Werk-IDs** zusätzlich zu ASIN/ISBN/AniList — sinnvoll oder Ballast? | §4.4 |
| ~~F09~~ | ~~LANoMAT~~ → **beantwortet: E179** (dieselbe Bauform wie E169 — eine vierte Sorte Ort, kein eigenes System) | — |
| ~~F10~~ | ~~Remixe und Coverversionen~~ → **beantwortet: E96** (JB 07.08.2026 — „Das Lied ist das Werk, dann kommt das Album") | — |
| F11 | **Geräteprofile** für Handhelds (Steam Deck, ROG Ally, …) — selbst pflegen oder von EmuDeck übernehmen? | §6 |
| F12 | **Übergabe an eine zweite KI** — welches Werkzeug für die Abarbeitung (DeepSeek günstig/1M-Kontext, Cursor im Editor, Codex parallel)? Entscheidend ist ohnehin das Pflichtenheft, nicht das Modell | Umsetzung |

---

## 13.1 Wie weit wir sind

**Noch keine Zeile Code — und das ist Absicht.** Was bisher entstand, ist das Pflichtenheft und
16 Entwürfe (siehe `ENTWUERFE.md`). Der Stand nach Bausteinen aus §16.2:

| # | Baustein | Entschieden | Gezeichnet | Gebaut |
|---|---|---|---|---|
| 1 | Register + Werk-Modell | ✅ vollständig (**E151**) | ✅ (Werk-Seite belegt das Modell) | ⬜ |
| 2 | Warteschlange | ✅ vollständig | ✅ | ⬜ |
| 3 | Erkennung + Identität | ✅ vollständig (E48, E76, E87, E141) | ✅ (Erweiterung + Postfach) | ⬜ |
| 4 | Regal + Startseite | ✅ vollständig | ✅ | ⬜ |
| 5 | Suche | ✅ vollständig | ✅ | ⬜ |
| 6 | Leser | ✅ vollständig | ✅ | ⬜ |
| 7 | Bühne | ✅ vollständig | ✅ | ⬜ |
| 8 | Erweiterung | ✅ vollständig | ✅ | ⬜ |
| 9 | Beschaffung | ✅ vollständig (E140, E149, E150, §7.5) | ✅ (das Rennen) | ⬜ |
| 10 | Veredelung | ✅ Grundsätze, offen: **F04, F07** | teilweise (Übersetzung ✅, Vertonung ⬜) | ⬜ |

> **Alle zehn Bausteine sind entschieden, neun von zehn gezeichnet.** Der Unterbau (1–3), der
> beim letzten Stand noch *ein* Bild hatte, ist jetzt vollständig belegt. Damit ist die Phase
> „zeichnen" im Wesentlichen vorbei — was bleibt, sind **Lücken schließen** und **übergeben**.

**In Zahlen:** 183 Entscheidungen · 16 Regeln der Bauart und des Vertrauens · **6 offene
Fragen** · 20 gelernte Fallen · 20 Entwürfe + 1 Beiblatt.

✅ **Die Übernahme-Lücke ist geschlossen.** `NICHT_UEBERNOMMEN.md` listete 18 Funktionen aus
SyncManga und SyncYouTube, die im Pflichtenheft fehlten. Alle 18 sind entschieden: zehn wurden
zu Regeln (E169–E178), zehn zu einem Ja ohne eigene Nummer, **vier zu einem Nein mit
Begründung**, eine vertagt (F09). ✅ **Und der letzte Entwurf steht** (`orte.html`): ein Werk an vier Orten,
Fortschritt in beide Richtungen, Anfragen. **Es ist kein Entwurf mehr offen, der etwas
beweisen müsste.**

### Die Lücken — Stand 08.08.2026, abends

**Die zehn Lücken vom 07.08. sind alle geschlossen.** Am selben Tag sind bei einer
strukturierten Nachsuche **drei neue** aufgetaucht — und sie sind von einer anderen Art als
die alten: es sind keine vergessenen Themen, sondern **Orte, auf die andere Entscheidungen
zeigen und die es nicht gibt**.

| Neue Lücke | Warum sie wehtut | Gefunden durch |
|---|---|---|
| ⚠️ **Die Werkstatt** | Sie wird im Heft **neunmal namentlich genannt** — als der Ort, an dem Regeln landen (E141), Handkorrekturen leben (E135), Heilungsvorschläge angeboten werden (E173) und Vorschläge zurückgenommen werden (E41). **Sie ist nie definiert und nie gezeichnet.** Vier tragende Entscheidungen zeigen auf einen leeren Raum | Suche nach Begriffen, die oft *verwendet*, aber nie *erklärt* werden |
| **Die Einstellungen** | Zwölf verstreute Erwähnungen, kein Ort. Inzwischen gibt es Güteprofil · zwei Sprachachsen · Sicherung · Profile · Inhaltsfilter · Quellenlisten · Geräte · Emulator-Grundlage · Schwellen (E183) · Meldungen (E164) · Wachordner · LANoMAT. **Ohne Entwurf wird das eine Abladefläche** — genau das, wovor E39 warnt | dasselbe |
| **Leere und kaputte Zustände** | Nahezu **null** Treffer. Was steht da, wenn die Suche nichts findet, das Regal nach einem Filter leer ist, eine Quelle nicht antwortet, das NAS weg ist? **Jeder Bildschirm hat diesen Zustand, und keiner ist entworfen.** Er entscheidet, ob sich ein Programm kaputt oder ruhig anfühlt | Suche nach dem, was *nie* vorkommt |
| **Werke von Hand teilen und zusammenführen** | Das Postfach kennt *doppelt* (E141, Grund 4). Aber: *„ich merke nach drei Monaten, dass das zwei Werke sind"* — oder eines — hat **keinen Weg**. Bei 800 Werken passiert das sicher | Durchspielen einer Handlung, die kein Entwurf zeigt |

> **Was diese vier gemeinsam haben und was daraus zu lernen ist:** Keine davon wurde durch
> *Lesen* gefunden. Sie kamen aus drei mechanischen Suchen — nach **oft genannten, nie
> definierten Begriffen**, nach **Wörtern, die gar nicht vorkommen**, und nach **Handlungen,
> die kein Entwurf zeigt**. *Das Wiederlesen eines Dokuments findet die Fehler nicht, die man
> beim Schreiben gemacht hat.* Diese drei Suchen gehören deshalb in `PFLEGE.md`.

#### Die sieben Antworten im Klartext

**E156 — ohne Netz steht die Uhr.** JB: *„Das System merkt sich, wann ich kein Internet mehr
hatte, und was ab dem Zeitpunkt neu rauskommt, wird als Update gefahren. Der Offline-Reader
wird dann spannend."*

> Das ist eine bessere Antwort als „es wartet". Beim Abriss wird ein **Zeitstempel** gesetzt.
> Bei Rückkehr fragt SyncFindus jede Quelle nicht *„was gibt es?"*, sondern **„was gibt es seit
> diesem Zeitpunkt?"** — ein Nachtrag, kein Neuaufbau. Das ist billiger, vollständiger und
> nachvollziehbar (*„14 Kapitel, 3 Folgen und 2 Alben sind erschienen, während du weg warst"*).

Was daraus folgt: **Vorrat ist keine Bequemlichkeit, sondern die Offline-Vorsorge.** Der Leser
muss die nächsten N Einheiten immer schon auf der Platte haben — und die Warteschlange lauert
weiter (E150), sie scheitert nicht. Wer zwei Wochen im Funkloch ist, liest zwei Wochen.

**E157 — eine Uhr: deine.** JB: *„Wenn das Kapitel um 4:00 Uhr morgens in CEST erscheint und in
Japan um 23:00 Uhr, dann sind es unterschiedliche Tage, doch wir gehen nach CEST (Berlin)."*

> Alles Sichtbare rechnet in **deiner** Zeitzone. „Heute neu" heißt: heute, nach der Uhr an
> deiner Wand. Die Herkunftszeit wird **gespeichert** (sonst kann man nicht sortieren) und
> **nur auf Nachfrage** gezeigt: *„erschienen 09.08. 04:12 — in Japan war es der 8. um 23:12."*
> Nie beide Daten gleichzeitig im Regal, das verwirrt mehr, als es klärt.

**E161 — ein Rechner hat Vorrang.** JB: *„Zwei Menschen gleichzeitig ist doch ok. Abwechselnd.
Wenn das nicht geht, ist die Prio bei diesem PC."*

> Kein Warteschlangen-Verwalter, keine Anteilsberechnung, kein Zeitscheibenverfahren. **Wer
> am Hauptrechner sitzt, gewinnt** — bei Grafikkarte, Bandbreite und Rechenzeit. Der zweite
> Zugang läuft weiter, nur langsamer, und **sieht das auch** („Veredelung pausiert, der
> Hauptrechner arbeitet"). Der Lesestand ist ohnehin je Profil getrennt.

**E164 — es meldet sich nur, wenn du sonst etwas verlierst.** JB: *„Versteh das Problem
nicht."* — Fair, das Problem ist unsichtbar, bis es da ist: Ein Programm, das alles Neue
meldet, wird nach zwei Wochen stummgeschaltet. Ein Programm, das nie etwas meldet, verschweigt
dir, dass etwas kaputt ist. **Die Antwort ist keine Einstellung, sondern eine kurze Liste.**

> **Drei Anlässe, mehr gibt es nicht:**
> **1.** Etwas ist **kaputt und du merkst es sonst nicht** — die Bibliotheksplatte antwortet
> nicht, das Zertifikat läuft ab, eine Anmeldung ist abgelaufen.
> **2.** Etwas **läuft weg** — eine Mediathek-Folge verschwindet in 3 Tagen und du hast sie
> nicht geholt.
> **3.** Du hast **ausdrücklich darum gebeten** — „sag mir, wenn Kapitel 1142 da ist".
>
> Alles andere — neue Kapitel, fertige Downloads, abgeschlossene Übersetzungen — steht im
> Regal und **wartet dort**. ⚠️ Nie eine Meldung, die nur „gute Nachrichten" transportiert.

**E176 — Inhaltsfilter für Erwachsene.** Aus SyncManga übernommen (`nsfw_hide_both`,
`_sexual`, `_gore`) und **nicht dasselbe wie E158**. Ein erwachsener Mensch darf
Gewaltdarstellung ausblenden wollen, ohne dafür ein Kinderprofil anzulegen — und die beiden
Achsen sind getrennt: manche wollen Blut nicht sehen, aber Erotik schon, und umgekehrt.

> **Zwei Schalter, nicht einer:** *sexuelle Darstellung* und *Gewaltdarstellung*, je einzeln.
> Grundlage ist `content_rating`, das SyncManga schon führt. Und es gilt dieselbe Regel wie
> überall: **was ausgeblendet ist, ist unsichtbar, nicht durchgestrichen** — ein Regal voller
> grauer Kacheln wäre schlimmer als ein kürzeres Regal.

**E158 — das Alter entscheidet.** JB: *„Wenn Kinderprofil, dann Alter eingeben, das entscheidet
was angezeigt wird."*

> **Eine Zahl statt einer Häkchenliste.** Aus dem Alter folgen FSK/USK/Altersfreigabe aus den
> Metadaten und die Inhaltsmarken (`content_rating`, das SyncManga schon führt). Zwei Regeln
> dazu: **Was nicht bewertet ist, gilt als nicht freigegeben** — im Zweifel unsichtbar, nicht
> im Zweifel sichtbar. Und: **das Kind sieht nicht, dass etwas fehlt** — keine grauen Kacheln,
> keine Schlösser, kein „ab 16". Ein leeres Regal ist besser als ein Regal voller Verbote.

**E162 und E159** stehen in §16.5 bzw. §6.

**Von den drei Ideen ohne E-Nummer:** der **Jahresrückblick** ist verworfen (JB: *„meh"*) und
durch **E148** ersetzt — der Kalender empfiehlt ganzjährig, statt einmal Bilanz zu ziehen. Der
**Bruchtest** ist jetzt **E147** (§12.6). Die **Lücken-Liste** (aus ◐ *gekannt* eine eigene
Ansicht — die Liste, die kein anderes Programm bauen kann) wartet weiter auf einen Entwurf.

**Was als nächstes fehlt, in dieser Reihenfolge** *(Stand 08.08.2026, abends)*:

| | Was | Art | Wer |
|---|---|---|---|
| **1** | **Die Werkstatt** — definieren und zeichnen | ⚠️ **Loch, auf das vier Entscheidungen zeigen** | zeichnen |
| **2** | **Die Einstellungen** — ein Ort statt zwölf Erwähnungen | Entwurf | zeichnen |
| **3** | **Leere und kaputte Zustände** — für jeden Bildschirm einer | Entwurf | zeichnen |
| **4** | **Werke teilen und zusammenführen** | Entscheidung + kleiner Entwurf | entscheiden |
| **5** | **F04 · F07** — Verwestlichung und Text-Korrektur | zwei Voreinstellungen in §10.2 | ⚠️ **JB** |
| **6** | **F06 · F08 · F11** — Quellen-Späher, eigene IDs, Geräteprofile | drei kleine, keine blockiert etwas | entscheiden |
| **7** | **F12** — welches Werkzeug die zweite KI benutzt | ⚠️ **JB**, aber erst kurz vor der Übergabe | ⚠️ **JB** |

**Was ausdrücklich *nicht* mehr auf dieser Liste steht:** der Prüflauf-Bericht (seit E162
optional), die Spiele-Regalansicht (blockiert nichts), das Zertifikat (JB hat Zeit), F02 und
F05 und F09 und F10 (beantwortet).

---

## 14.---

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
| 2026-08-08 | Fassung 1.16 — ⚠️ **Die Konfliktregel aus E170 ist zurückgenommen. JB hat sie zerlegt, und er hatte recht.** Seine Frage: *„Wenn ich an meinem PC nicht Episode 12 geguckt habe, bin ich bei Folge 3. Ich sehe den Konflikt nicht. Wenn jemand von meinem PC streamt, hat das nicht mit dem Programm zu tun — er ist in seinem Programm. Kannst du nicht differenzieren zwischen einmal geöffnet und von wem?"* — **Der Konflikt war ein Fehler in meinem Modell, kein echtes Problem.** Ich hatte Fortschritt als **eine Zahl** modelliert („du bist bei Folge 8"); sobald man das tut, kollidieren zwei Zahlen und man braucht eine Regel, welche gewinnt. Dieselbe Regel hätte JB beim Nochmalsehen von Folge 3 zurück auf Folge 13 gezerrt — **genau das, was er nicht wollte.** **🔑 E182 — Fortschritt ist eine Menge, keine Zahl.** Je Einheit genau drei Zustände: **ungesehen · mittendrin (mit Marke) · gesehen**. Daraus folgt alles: **zwischen Einheiten wird vereinigt, nie verglichen** (»gesehen« ist je Einheit einbahnig, zwei Geräte können sich gar nicht widersprechen, nur beide recht haben); **innerhalb einer Einheit gewinnt die neuere Marke**, weil Zurückspulen normal ist — *genau hier hatte ich es vorher umgekehrt*; **„weiter" ist eine Frage, keine Zahl** (die Einheit mit offener Marke, sonst die erste ungesehene); und **nur die Hand nimmt „gesehen" zurück**. Jellyfin, AniList und MyAnimeList führen es alle so — wir hatten es als einziges falsch. **🔑 E181 — Fortschritt gehört einem Profil, nicht einem Ort.** Auf dem Server melden wir uns als **ein bestimmter Benutzer** an und lesen und schreiben ausschließlich dessen Daten; wer sonst von diesem Server streamt, **existiert für uns nicht**. ⚠️ Mit der einen Bedingung dafür: **teile den Server, nicht das Konto** — wer sein Passwort weitergibt, hat einen Benutzer mit zwei Menschen, und das kann kein Programm auflösen; eine Sitzung von einem unbekannten Gerät wird deshalb *gefragt statt geglaubt*. **🔑 E183 — geöffnet ist nicht gesehen.** Unter 2 % oder 60 Sekunden passiert **gar nichts** — kein Eintrag, keine Marke, keine Meldung nach außen; darüber eine Marke; ab 90 % oder mit dem Abspann gilt es als gesehen. Beim Manga ist eine angetippte Seite nichts und die letzte Seite eines Kapitels alles. Dazu der Notausgang **„das war ich nicht"** an jedem Fortschrittseintrag, weil es immer den Abend gibt, an dem jemand anderes am Rechner saß. Und die Regel, die JB direkt angesprochen hat: **eine Anfrage ist eine Absicht, kein Ereignis** — Anfragen, Wünsche, Merklisten und Warteschlangen-Einträge berühren **nie** eine Position; Fortschritt entsteht ausschließlich durch Abspielen. **Entwurf `orte.html` überarbeitet:** der Reiter *Fortschritt* zeigt jetzt **Felder je Folge statt einer Zahl** — daran sieht man den Unterschied sofort — mit sieben durchspielbaren Fällen, darunter die drei neuen: *von vorn anfangen* (kein Konflikt, beides wahr), *Kevin streamt von deinem Server* (bei dir passiert nichts) und *40 Sekunden reingeschaut* (es wird gar nichts geschrieben). |
| 2026-08-08 | Fassung 1.15 — **E180 Anfragen, und der letzte Entwurf ist gezeichnet.** JB: *„Also sind Anfragen nun auch ein Thema durch seerr, oder?"* — **Ja, und es ist kein neues System.** **🔑 E180 — eine Anfrage ist ein Wunsch, der über eine Grenze geht.** Ein Wunsch (E150) ist an mich selbst gerichtet: ich will das, mein Programm versucht es. Eine Anfrage ist an **jemand anderen** gerichtet: ich will das, ein Mensch muss zustimmen. **Gleiche Form, andere Grenze** — deshalb hängt der Zustand am Wunsch, der Weg ist die Warteschlange, die Zustimmung ist eine Karte; nichts davon wird neu gebaut. Damit sind **Jellyseerr, LANoMAT und der Haushalt dreimal dieselbe Sache**: beim eigenen Server sagt meistens **du selbst** Ja (deshalb fühlt es sich wie ein Wunsch an), im LAN ein anderer Mensch, im Haushalt der Profilinhaber — *ein Kind fragt, statt heimlich zu suchen, und das ist die freundlichere Form von Jugendschutz*. **Drei Antworten, nicht zwei:** Ja · Nein · **„nur ansehen"** — die Zwischenstufe, die man beim LAN-Abend fast immer meint (*lies es bei mir, nimm es nicht mit*) und die in keinem Programm existiert. **Vier Regeln, damit aus Anfragen keine Bettelei wird:** eine Ablehnung ist ein **Ergebnis, kein Fehler** und nicht rot — ⚠️ **man fragt denselben Menschen nicht zweimal nach derselben Sache**, ein zweiter Versuch braucht eine ausdrückliche Handlung, und das ist **der einzige Ort im ganzen Entwurf, an dem E150 nicht gilt** · der Anfragende sieht nur *„gestellt"*, nie ob der andere sie gelesen hat (kein Lesebestätigungs-Elend) · eine Anfrage trägt **nie deinen Fortschritt** (E179) · **Anfragen sind Post, kein Postfach** — das ist für Unklarheit, eine Anfrage ist das Gegenteil davon. Dazu der Punkt, den man sich bewusst machen muss: mit den Anfragen taucht **zum ersten Mal ein anderer Mensch auf dem Bildschirm** auf — bis hierhin war SyncFindus ein Programm für genau eine Person, und jede der vier Regeln verhindert eine Sorte sozialen Druck, die ein Werkzeug nicht erzeugen sollte. **Neu: Entwurf `orte.html` (Nr. 20)** — vier Orte an einem Werk mit vollständiger Rechtematrix, **fünf durchspielbare Abgleichsfälle** (Normalfall · Gegenrichtung · Konflikt · offline · Zurücksetzen von Hand) und die Anfragen in beide Richtungen. Damit ist `NICHT_UEBERNOMMEN.md` **vollständig abgearbeitet** und **kein Entwurf mehr offen, der etwas beweisen müsste**. |
| 2026-08-08 | Fassung 1.14 — **E166 korrigiert (JB-Einwand), E179 LANoMAT, F09 geschlossen.** ⚠️ **Korrektur an E166:** JB fragte *„Erklär mir, was eine Kopie auf dem NAS bringt, wenn die Daten eh auf dem NAS sind. Ich werde keine Daten auf meinem PC speichern."* — **Gar nichts, und das war ein Fehler.** Ich hatte die 3-2-1-Regel übernommen, ohne sie auf **diese** Anlage anzuwenden: sie stammt aus Serverräumen, und bei einem Menschen mit **einem** NAS heißt „zwei Datenträger" nichts, solange beide im selben Gehäuse stecken. **Aus drei Ringen werden zwei** — einer auf dem NAS gegen unsere eigenen Fehler, einer außerhalb gegen alles andere; was dazwischenlag, waren nie zwei Ringe, sondern einer mit zwei Qualitätsstufen. Dazu der Punkt, der den Einwand auflöst: **das Register ist unter 500 MB** — das ist keine Datenhaltung auf dem PC, das ist eine Datei, und sie passt auf einen USB-Stick in der Schublade. Neu benannt: **RAID ist Verfügbarkeit, keine Sicherung** (überlebt eine Platte, sonst nichts — nicht Löschen, nicht Verschlüsselung, nicht Diebstahl). Und **der dritte Ring, den wir nicht bauen müssen**: sobald E170 steht, lebt *„was habe ich gesehen"* in zwei unabhängigen Systemen — bei uns und auf dem Jellyfin-Server, dazu AniList. Das ist keine Sicherung, die wir gebaut haben, sondern eine **Redundanz, die wir geschenkt bekommen, weil wir zurückschreiben statt nur zu lesen**; selbst bei totalem Verlust wäre der Lesestand rekonstruierbar statt null. **🔑 E179 — LANoMAT: fremde Bibliotheken sind Orte, keine Konten** (F09 beantwortet). JB fragte danach, und die Antwort fällt mit **E169** zusammen, weil es dasselbe Problem ist: ein Werk liegt irgendwo, das mir nicht gehört. Also **eine vierte Sorte Ort**, kein eigenes System — `familie.py` ist der Ausgangspunkt. Kein Konto, kein Server, keine Anmeldung: Erkennung über Zeroconf, wer im Netz ist, ist da. Der Grund, warum es das wert ist, ist ein Satz: **die Lücken-Liste (E160) trifft auf sechs andere Bibliotheken** — *„Kevin hat 4 davon, Ann hat 11"*, und das kann kein Streaming-Dienst leisten. Vier Rechtestufen mit **aus als Standard jeder Sitzung**; ⚠️ **der Fortschritt wird auf keiner Stufe geteilt** — auch nicht als Zahl, auch nicht anonym: *man teilt seine Bibliothek, nicht sein Tagebuch*. Dazu: nichts wird geschoben, alles wird gezogen · der Ort verschwindet, das Wissen darf mit Erlaubnis bleiben · es ist eine **Sitzung, kein Zustand** (kein Dauerbetrieb, keine Freundesliste, kein „online seit"). **E171 erweitert:** die Sperrdatei trägt Rechnernamen und Zeitstempel, weil auf einem NAS auch zwei verschiedene Rechner zugreifen können (E161). |
| 2026-08-08 | Fassung 1.13 — **Alle 18 Funde entschieden** (JB: *„ok lass uns entscheiden"*). Zehn wurden zu Regeln, zehn zu einem Ja ohne Nummer, **vier zu einem Nein mit Begründung**, eine vertagt. **🔑 Neu: §4.7 Ein Werk kann fern liegen (E169).** Der größte Fund kommt ins Fundament, nicht in die Beschaffung: ein Medienserver ist ein **Ort**, keine Quelle und kein Motor — §4.6 sagte *„Ort ≠ Werk"* und meinte bisher nur Platten. Drei Sorten Ort mit klaren Rechten (lokal · fern-eigen · fern-fremd = nur Wissen, E129); der Serverkatalog wird über einen Adapter **verschmolzen statt danebengehängt** (E11); die Merkliste ist eine **Sammlung**, keine neue Sorte Ding; Jellyseerr ist ein **Kandidat im Rennen** (E149), kein Sonderweg; und ein ferner Ort darf ausfallen, ohne dass etwas verlorengeht — es fehlt dann nur eine Ausgabe. Dazu **Live-TV als Ort ohne Vorrat** (E44 hatte es zugelassen, `live_tv.py` existiert). **🔑 E170 Fortschritt fließt in beide Richtungen** — bisher stand nur die Richtung hinein im Heft. Was wir wissen, geben wir zurück; alles andere wäre ein Programm, das Daten aufsaugt und nichts zurückgibt. Mit einer Konfliktregel, ~~es gewinnt die weitere Position~~ — **am selben Tag von JB widerlegt und durch E182 ersetzt, siehe Fassung 1.16** — und was nicht ankam, wandert in eine **Nachreich-Schlange**, E156 in klein. Ausdrücklich ausgenommen: ein Zurücksetzen von Hand ist keine Regression, sondern eine Ansage. **E171 eine Registerdatei, ein Programm** — nach E151 Pflicht statt Komfort; zweimal aufs Symbol geklickt holt die vorhandene Kopie nach vorn, und eine tote Sperrdatei wird nur geräumt, wenn der Prozess nachweislich unserer war. **E172 prüfen vor dem Tausch** — vier bezahlte Regeln aus `update.py`: nichts löschen, `.bak` vor jedem Tausch, **Daten vor dem Tausch validieren** (ungültig → alte Datei bleibt), atomar schreiben. **🔑 E173 Heilen ist die zweite Hälfte des Bruchtests** — §12.6 kannte nur das Finden; acht vorhandene Reparaturen werden zu einer Regel: **jeder Fund kennt seinen Vorschlag und führt ihn nie selbst aus**, genau wie im Postfach (E141). Einzige Ausnahme bleibt die Dublettenbewertung, weil sie eine Messung ist (E140) und keine Meinung. **E174 der Wachordner nimmt an, er räumt nicht auf** — dieselben drei Ausgänge wie jede andere Quelle. **E175 das Programm zeigt sich im Infobereich** — Zustandsemblem statt Öffnen, und es informiert, es ruft nicht (E164). **E176 Inhaltsfilter für Erwachsene** — **zwei getrennte Achsen** (sexuelle Darstellung, Gewaltdarstellung), nicht dasselbe wie das Kinderprofil E158; was ausgeblendet ist, ist unsichtbar, nicht durchgestrichen. **🔑 E177 was der Mensch bestätigt, wiegt schwerer als was wir messen** — die Rückmeldeschleife aus SyncManga wird zur Regel: wir messen HTTP-Antworten, ein Mensch sieht, ob tatsächlich das Kapitel dasteht; seine Korrektur überlebt jede Neuanreicherung. **E178 sechs Lesezustände statt drei** — *„aufgeholt"* ≠ *„Rückstand"* ist der Unterschied zwischen einem Programm, das hetzt, und einem, das informiert; *„lange pausiert"* ist eine Einladung, kein Vorwurf. **Neu: §16.6 Die Kleinen** mit zehn Ja und **vier Nein** — Selbstneustart bei Codeänderung (macht die Signatur wertlos, für die wir Wochen aufwenden), **Spaltenwahl** (meist die Ausrede dafür, die Prioritätsleiter nicht geschrieben zu haben — wir haben sie geschrieben), Tonspurwahl beim externen Abspielen (E34), Cloud-Slot (ersetzt durch Gerätekopplung — die **Datensparsamkeit** wird übernommen). *Eine Übernahmeliste, die nur aus Ja besteht, ist keine Liste, sondern ein Umzug.* **`NICHT_UEBERNOMMEN.md` schrumpft** von einer Fundliste zu einem Nachweis; offen bleibt eine Zeile: `filme.py` ist entschieden, aber nicht gezeichnet. |
| 2026-08-08 | Fassung 1.12 — **Die letzten zwei Lücken geschlossen — und eine große neue gefunden.** **🔑 E166 Sicherung: drei Ringe, und nur die Wiederherstellung zählt.** Getrennt wird nach **Katastrophenart**, nicht nach Häufigkeit: Schnappschuss (unser eigener Fehler, stündlich, `VACUUM INTO` im Betrieb) · Kopie (Plattenausfall, täglich, anderer Datenträger, plus Klartext-Ausgabe die SyncFindus überlebt) · Auswärtiges (Feuer/Diebstahl/Trojaner, wöchentlich, verschlüsselt, **versioniert und nur anfügend**). Gesichert wird nur das Unersetzliche — **unter 500 MB bei 800 Werken**, weil eine Sicherung, die 64 TB kopiert, nach drei Wochen abgestellt wird. Kernstück ist der **Rückspiel-Test**: monatlich, automatisch, mit der **ältesten** Sicherung (nicht der neuesten), zurückgespielt in einen Temp-Ordner, gezählt und mit dem **Bruchtest (E147) gegen die Kopie** geprüft. Eine Sicherung, die nie zurückgespielt wurde, ist keine Sicherung, sondern eine Hoffnung. Dazu die Wiederherstellungsregeln: nie überschreiben, vorher die Differenz zeigen, **teilweise wiederherstellen** (der häufigste Ernstfall ist nicht „alles weg", sondern „ich habe eine Sache kaputtgemacht"). **E167 Sprache: zwei gepflegte, alle weiteren eine Datei.** Deutsch und Englisch kommen mit; eine dritte, die niemand korrekturlesen kann, ist schlechter als keine. Gemeinschaftssprachen werden geladen, wenn der Text-Wächter sie durchlässt, und tragen sichtbar „ungeprüft". Dazu die Unterscheidung, die bisher fehlte: **Sprache der Oberfläche und Sprache des Inhalts sind zwei Einstellungen und dürfen sich nie gegenseitig setzen.** **🔑 E168 Löschen geht in den Papierkorb** — aus SyncYouTube geerbt und nie aufgeschrieben: keine endgültige Löschung, auch nicht für Zwischenspeicher, auch nicht auf Wunsch. **Neu: `Doku/NICHT_UEBERNOMMEN.md`.** JB fragte, was aus den verwandten Programmen nicht mitgenommen wurde; beide Repos wurden dafür **gelesen, nicht erinnert** (SyncYouTube frisch geklont, Stand `558d183`, 18.446 Zeilen). Ergebnis: **18 übersehene Funktionen** — und ein Fund von Bausteingröße: **`filme.py` (878 Zeilen)**, eine vollständige Jellyfin/Emby-Anbindung mit Katalogabzug, Merkliste, **Fortschritt-Rückmeldung samt Nachreichen nach Offline** (E156, zwei Jahre früher und schon gebaut) und **Jellyseerr** als fertigem Beschaffungsweg. Im Pflichtenheft kam Jellyfin bis heute nur als *Ziel* vor, nie als *Klient*. Dazu `live_tv.py` (E44 hat Live-TV zugelassen, der Code dafür existiert), die **Heilungsfamilie** (acht Reparaturfunktionen — §12.6 kennt nur das Finden), **Wachordner**, **Selbstneustart bei Codeänderung im Leerlauf**, **Einzelinstanz-Sperre** (nach E151 gefährlicher als vorher), **Selbst-Aktualisierung** mit vier erkauften Regeln, **Tray-Symbol mit Zustandsemblem**, **Statistik-Tafel**, **Inhaltsfilter** (nicht dasselbe wie E158), **Kapitelkorrektur von Hand**, die **Rückmeldeschleife** Quelle-bestätigen/defekt-melden, und sechs statt drei Lesezuständen. Mit der ehrlichen Ursache: ich habe zweimal nach **Architektur** gesucht und nie nach **Funktionen** — und der Alltag eines Programms steht in den kleinen Funktionen. **Neu: Entwurf `sicherung.html`.** |
| 2026-08-08 | Fassung 1.11 — **Der Name steht, die Fessel fällt, neun Lücken schließen sich.** **F02 beantwortet: SyncFindus** (JB: *„Mein Kater heißt so, als Findus."*) — Dokument, Dateiname und alle Entwürfe umbenannt. **F05 beantwortet: E163, ja.** JB delegierte die Entscheidung; §9.2 wägt beide Seiten ab und entscheidet nach **Schadenshöhe statt Wahrscheinlichkeit** — bleiben die Dateien liegen und nichts passiert, gewinnen wir null; passiert etwas, ist das Repo weg. Dazu der ehrliche Hinweis, dass `git rm` nicht reicht (Historie) und ein Umschreiben JBs ausdrückliche Zustimmung braucht. **🔑 E162 — SyncManga ist Lehrer, nicht Vorgänger.** JB: *„Die Library ist egal, die sollten wir uns selber aufbauen … wir sind noch nicht so etabliert, dass wir nichts wagen können."* Damit fällt die größte Fessel des Vorhabens: die erste Fassung heißt nicht mehr *800 Werke drin*, sondern **ein Werk richtig**. Festgehalten bleibt die eine Asymmetrie — Dateien sind ersetzbar, **Lesestand nicht**; deshalb ein winziger Import von drei Feldern (Titel · letztes Kapitel · Datum) durch dieselbe Erkennung wie jede andere Quelle, als **Angebot ohne Zeitdruck**. **🔑 E154 — zwei Regale für Ton:** in der Musik ist eine Lücke eine **Zahl**, im Hörbuch ein **Defekt**. Neun Unterschiede tabellarisch, Vollständigkeitsbalken **segmentiert statt prozentual** (ein Prozentwert verschweigt, *wo* das Loch sitzt), und ein Hörbuch ist **ein** Wunsch, Musik viele. **🔑 E155 — Pflicht wird gezeigt, nicht versteckt:** Haken gesetzt und ausgegraut, drei Klassen mit je einem festen Satz, Größe/Lizenz/Zweck bei jedem Bestandteil, nie ein vorausgewähltes Extra. Dazu **der erste Start** als vier gleichwertige Wege ohne Reihenfolge. **🔑 E159 — die Einstellung gehört zum Spiel, nicht zum Emulator:** drei Ebenen mit sichtbarer Herkunft je Zeile, plus der Knopf *„als Systemstandard übernehmen"*, ohne den man dieselbe Sache 41-mal einstellt. **🔑 E160 — die Lücken-Liste ist der Eingang zur Beschaffung**, kein Bericht: eine Tat je Zeile, sie beschämt nicht, und sie hat bewusst **kein Abzeichen** — anders als das Postfach, das rufen muss. **E165 — sofort der Rand, nach 400 ms das Band** (vier Hover-Varianten verglichen, C gewinnt mit D als Sofortantwort). **Sieben Lücken geschlossen:** **E156** ohne Netz steht die Uhr, bei Rückkehr läuft alles seit dem Bruch als Nachtrag (JBs Antwort war besser als meine Frage) · **E157** eine Uhr, deine — alles nach Berliner Zeit, Herkunftszeit nur auf Nachfrage · **E158** das Alter entscheidet, und was nicht bewertet ist, gilt als nicht freigegeben; das Kind sieht keine Schlösser · **E161** ein Rechner hat Vorrang, wer davorsitzt gewinnt · **E164** es meldet sich nur bei drei Anlässen — kaputt, läuft weg, ausdrücklich gewünscht; nie eine reine Erfolgsmeldung · *Platte voll* („dann erweitere ich" — keine Verdrängungslogik, das ist die richtige Antwort) · *ohne Maus* (keine Funktion, sondern eine **Bauvorgabe**: fehlende Fokussierbarkeit ist eine neue Säule und darf nie entstehen). **Offen bleiben zwei:** Sicherung & Wiederherstellung — nach E151 trägt **eine** Datei alles — und die Sprache der Oberfläche. **Neu: Entwürfe `regale.html` und `erststart.html`.** |
| 2026-08-08 | Fassung 1.10 — **Die wöchentliche Pflege wird dauerhaft.** JB-Vorgabe: *„Wir müssen ab und an immer wieder prüfen, was es Neues gibt, was Altes ersetzt und was gestorben ist — egal in welchem Chat ich bin."* → **Neu: `Doku/PFLEGE.md`** mit acht Prüfungen, jede mit einem **Fund-Auslöser** (nur wenn der eintritt, gibt es Arbeit): die vier Protokolle leben · Wissensketten antworten unverändert · Werkzeuge werden gepflegt · **der Friedhof** — wer ist gestorben, die Prüfung, die man am liebsten vergisst, weil nichts kaputtgeht, sondern nur etwas fehlt · Recht und Schlösser · neue Vorbilder · Browser-Änderungen · die eigene Baustelle. Dazu die **Halbwertszeit-Tabelle**, die begründet, warum ausgerechnet das nachgeprüft werden muss: Werk-Modell hält **Jahre**, Gestaltungsregeln **Jahre**, Werkzeuge **Monate**, Quellen **Wochen**. Neu in §0: **Pflegeregel 6** und die Tabelle der drei Begleitdateien. Ein Fund gehört in eine Datei, nie in ein Gespräch — *ein Chat endet, die Datei nicht*; auch „kein Fund" wird protokolliert, sonst weiß niemand, ob geprüft oder vergessen wurde. **§13.1 auf den echten Stand gebracht:** alle zehn Bausteine entschieden, neun von zehn gezeichnet, **kein fehlender Entwurf blockiert mehr einen Baustein**. Die Lücke *Übernahme aus SyncManga* ist geschlossen (§16.5), neun bleiben — mit dem Hinweis, dass **E151** die Sicherungsfrage und **E150** die Offline-Frage verschärft haben. Die nächsten Schritte sind neu sortiert, obenan die **drei Dinge, die auf JB warten**: **F05** (die zwei Dateien aus dem öffentlichen Repo — die einzige Frage, bei der Zögern selbst das Risiko ist), die **Token-Wahl bei Sectigo** (Vorlauf Wochen, nicht Tage) und **F02 der Name** (blockiert alles Sichtbare, steht auch im Zertifikat). **Entwurf 15 überarbeitet** zu *Was noch offen ist*. |
| 2026-08-08 | Fassung 1.9 — **E149–E153, E139 überarbeitet, der SyncManga-Damm gebrochen.** **JB entschied drei Anordnungen:** Werk-Seite **A**, Postfach **C**, Warteschlange **A** — und überstimmte mich zweimal zu Recht. **E139 überarbeitet:** JBs Einwand *„wenn du sagst, wir sollen die gleiche Oberfläche haben, dann widersprichst du dir doch"* sitzt. *Dieselben Kästen über alle Medien* ist eine Aussage über das **Datenmodell** und kostet nichts; *verschiedene Anordnungen je Zustand* ist eine über das **Verhalten** und kostet Lernbarkeit — ich hatte die zweite mit der Autorität der ersten begründet. Jetzt: **eine Anordnung, ein Band das seinen Inhalt wechselt** — der Aufmacher bleibt immer stehen, nur eine Zeile darin wird vom Herkunftssatz zum Faden; beim Film trägt dieselbe Zeile die Zeitmarke. **§4.5.1 überarbeitet:** die Bahn gewinnt, weil die Warteschlange eine **Tafel zum Danebenschauen** ist und keine Arbeitsfläche (JB: *„es ist halt ein Progress"*) — mit farbiger **Umkreisung** statt Rahmenfarbe; die Zeilen werden ihre Notlage unter 640 px, die Bündelung nach Werk wird das Aufklappen. **Neu: §9.6 Das Rennen** — **E149 Beschaffung ist ein Rennen, kein Auftrag** (Vorprüfung kostet keine Bytes: Seederzahl aus dem DHT, `HEAD` auf `Accept-Ranges`; Ablösung statt Abbruch; Teildaten bleiben liegen; Geo-Sperre ist ein Schritt, kein Fehler) und **E150 der Wunsch stirbt nie** — ein Auftrag scheitert, ein Wunsch lauert und schlägt zu, sobald eine neue Quelle auftaucht. **Neu: §7.5 Vier Protokolle statt einer Liste** (Cardigann-YAML mit 500+ Indexern, `index.min.json` der Erweiterungsläden, ~1.800 yt-dlp-Extraktoren, MediathekView-Filmliste, BitTorrent als Protokoll ohne Anbieter) und **§7.6 Das Werkzeugfeld** — 14 quelloffene Werkzeuge mit ihrer Rolle, eingebunden statt nachgebaut, dazu MakeMKV für die eigene Scheibe mit der ehrlichen § 95a-Fußnote. Ausdrücklich **nicht** enthalten: eine kuratierte Seitenliste — genau das Artefakt, an dem Tachiyomi starb. **E151 Das Register ist die Wahrheit, die Anzeige eine Sicht** — acht konkrete Beschlüsse in §16.5 schließen alle drei ineinandergreifenden SyncManga-Macken auf einmal; `CACHE_VER` entfällt, jedes Feld trägt eigenes Alter und eigene Herkunft. **Behoben (JB-Funde 08.08.):** **E152** die Kopfzeile lief über den Kapitelstreifen — die untere Leiste kannte die Regel längst, die obere nicht (*ein reparierter Fehler mit einem unreparierten Zwilling*); **E122 gilt auch senkrecht** — Sprechermarken und der Weiterlesen-Knopf wuchsen aus der zentrierten Mitte heraus und waren unsichtbar, der Knopf steht jetzt nie in der Verzichtsreihe; **E153 eine Tafel ist eine Tabelle** — die Untertitel-Werkstatt war links bündig und rechts fransig, „Größe" und „Schrift" standen wegen 1 px Innenabstand nicht übereinander, vier Bedienelement-Gewichte in 32-px-Zeilen, dazu ein Pixel Randversatz gegen die eigene Tafel; **E82** die Pausenkarte hing mittig und ragte in die Bedienleiste — jetzt oben angeschlagen, höhenbegrenzt und gestuft nachgebend. |
| 2026-08-07 | Fassung 1.8 — **E139–E148, vier blockierende Entwürfe erledigt.** **Neu: §4.2.1 Die Werk-Seite** mit dem Vier-Medien-Nachweis (dieselben Kästen für Manga, Anime, Film, Album — nur die Wörter wechseln) und **E139: zwei Gesichter, der Fortschritt entscheidet** — kein Fortschritt → Bild-Anordnung, Fortschritt → Faden-Anordnung, unter 700 px → Akte; **keine Einstellung**, eine Folge des Zustands. **E144** Beziehungen sind gerichtet und benannt. **Neu: §4.5.1** die Warteschlange sichtbar — **E142** bündeln nach Werk statt nach Auftrag, **E143** jede Zeile beantwortet drei Fragen (was tut sie, worauf wartet sie, was bei Fehlschlag), vier Zustände und **gelb ist kein Fehler**. **Neu: §8.6 Das Postfach** — der Trichter als Rahmen, der Stapel als Arbeitsmodus, **E141** (sichtbar · Standardausgang · Regel aus Wiederholung) und die **sechs geschlossenen Gründe**. **Neu: §7.4 Die Güteleiter** — **E140**, eine Stufenleiter S–D für alle Medien, **gemessen statt geglaubt**; dazu die recherchierte Liste legal beschaffbarer Quellen je Medium (Standard Ebooks, Baen, DTA, ARD Audiothek, Bandcamp, **Live Music Archive**, **MediathekView** als stärkster Einzelfund, Digital Comic Museum) und die ehrliche Grenze bei Widevine, AACS und § 95a UrhG. **Neu: §8.5 Sechs Zeugen** mit Gewichten und Sicherungen — **E145 der Browser ist ein Zeuge, kein Gedächtnis**, **E146 der Zustand hängt nie an der Identität**. **Neu: §16.5 Übernahme aus SyncManga** — alle 18 Module gelesen, **drei ineinandergreifende Macken** benannt (Zustand im localStorage · Titel als Schlüssel · Cache = Bibliothek) samt der einen Entscheidung, die alle drei auflöst, plus was durch Leser und Herunterladen jetzt möglich wird. **E147 Der Bruchtest** (§12.6) mit sechs Beispielregeln, **E148 der Kalender empfiehlt, die Bilanz nicht** (Jahresrückblick verworfen). **Neu: Entwürfe `werkseite.html` und `quellen.html`.** **Behoben:** fehlendes `</div>` in `.hlinks` (verschluckte die Bedienschicht — der Spieler verschwand bei Hörbüchern); Vorschaubild auf der Tonspur-Zeitleiste, wo es kein Video gibt; vierte Spulstufe 60× ab 3,4 s. |
| 2026-08-07 | Fassung 1.7 — **E138** Stimmen sichtbar machen (höchstens drei Marken, dann „+ N weitere"; Sprecherpunkte im Mitlesen; Farben aus dem Werk-Wissen; nie Namen im Fließtext). **Neu: §13.1 Ungeschriebene Lücken** — zehn Dinge, die im Pflichtenheft fehlen und beim Bauen weh tun, nach Schmerz sortiert; obenan die **Übernahme aus SyncManga** (800 Werke mit Lesestand müssen am ersten Tag drin sein). Dazu drei Ideen ohne E-Nummer: Jahresrückblick, Lücken-Liste, Bruchtest beim Beenden. **Neu: Entwurf `fahrplan.html`** mit dem Status aller zehn Bausteine, den acht fehlenden Entwürfen und vier Phasen. **Behoben:** Hörbuch zeigte Titel, Band und Kapitel doppelt — E133 gilt jetzt auch dort, der Platz gehört dem Mitlesen. |
| 2026-08-07 | Fassung 1.6 — E133–E137, **F03 geschlossen**. **Neu: §10.2.1 Die Übersetzung im Bild.** **E135 das Glossar schlägt jedes Modell** — fünfstufige Herkunftsrangfolge, Handkorrektur gewinnt immer, nie stumm überschreiben; eine Glossarzeile ändern erneuert alle betroffenen Stellen rückwirkend, **der Lesestand bleibt** (E76). **E136 Blasenprüfung:** beim Manga ist nicht die Übersetzung das Problem, sondern der Platz — passt der Satz nicht in die Sprechblase, ist er falsch, auch wenn er schöner ist. **E134 Englisch zuerst**, Deutsch als zweiter Lauf **aus der englischen Fassung**, weil das Glossar dann schon steht. **E137 Sprichwörter (F03):** drei Wege — ersetzen nur ohne Ortsbezug, Bild behalten mit Antipp-Erklärung als Standard, Sinn ohne Bild als Rückfall; entschieden wird einmal und steht dann im Glossar. **E133 nichts steht zweimal im Bild:** trägt der Inhalt den Titel, trägt die Kopfzeile die Herkunft — und der Pfeil führt dorthin zurück. **Behoben:** Ausschnitt lag unter der Leiste (jetzt in der Bedienschicht); Warteschlangenfuß hatte Zufall/Wiederholen/Als Playlist doppelt zu den Leistenknöpfen — jetzt nur noch ein ⋯ mit warteschlangeneigenen Werkzeugen; Karaoke-Mikro mit versetzter Kapsel. |
| 2026-08-07 | Fassung 1.5 — E130–E132, alle drei aus JB-Funden. **E130 nichts scrollt, was eine Bühne ist:** eine Bühne ist ein Bild, kein Dokument — `overflow:auto` dort ist immer die bequeme Ausrede dafür, die Prioritätsleiter nicht geschrieben zu haben. Gerollt wird nur in Listen. Alle Bühnentexte sind einzeilig mit Auslassung oder auf feste Zeilenzahl geklammert. **E131 ein Knopf, eine Bedeutung:** beim Hörbuch trug ein Knopf das Etikett „Einschlafen" und öffnete trotzdem Ton & Text — wer das Etikett ändert, muss die Handlung ändern, sonst lügt der Knopf. **E132 Angebote schließen sich aus:** die Weiche verlangt eine Entscheidung, die Besetzungskarte lädt zum Verweilen — höchstens eine Karte, die etwas will. **Behoben:** A/B/C lag unter der Bedienschicht und war nicht anklickbar (z-index innerhalb eines Stapelkontexts); Musik und Hörbuch scrollten bei kleinem Fenster; Karaoke-Zeichen war ein Standmikro und sah stummgeschaltet aus → **Handmikrofon**; Zufall war bei 17 px ein Kreuz → neu gezeichnet mit gebogenen Wegen. Die sieben Rechtsklick-Menüs sind jetzt im Entwurf **anklickbar** statt nur tabelliert. |
| 2026-08-07 | Fassung 1.4 — E125–E129. **E125 freie Fläche ist kein Fehler:** Leerraum wird nicht gefüllt, sondern geordnet — vierstufige Rangfolge (was läuft · wo im Stück · was kommt · alles andere), und Rang 4 darf verschwinden. Zwei gleich schlimme Fehler: die tote Ecke, weil ein Bauteil zu früh aufhört, und das Hineingestopfte, damit es nicht leer aussieht. **E126 drei Musik-Anordnungen** (Bühne · Mitte · Text) nach den Vorbildern Apple Music, Spotify-Vollbild und Apple-Music-Lyrics — je Gerät gemerkt, weil die Ansicht an der Situation hängt, nicht am Lied. **E127 Rechtsklick:** max. 7 Zeilen, max. ein Trennstrich, nie doppelt zu einem sichtbaren Knopf; vollständige Menüs im Entwurf. **E128 Radio ≠ Zufall ≠ Entdecken** — Zufall ordnet um, Radio hängt an, Entdecken holt herein. **Neu: §7.0.1 (E129) Streaming-Konten sind Wissen, keine Quelle** — Spotify und SoundCloud liefern Bibliothek, Playlists und Verlauf, aber keinen Tonstrom; daraus werden Regal-Einträge im Zustand *gekannt*, und die Lücke zwischen Gehörtem und Besessenem ist unser Alleinstellungsmerkmal. **Behoben:** Fernseh-Pfeile flankieren jetzt die Reihe statt oben zu stehen; die tote Ecke rechts unten in der Musikbühne ist weg (nur der linke Teil macht der Leiste Platz). |
| 2026-08-07 | Fassung 1.3 — E121–E124. **E121 Höhen werden gemessen, nie geraten:** wo ein Bauteil einem anderen Platz macht, wird die Höhe zur Laufzeit gemessen (`ResizeObserver` → CSS-Variable). Die feste `62px` stimmte genau bei der Breite, bei der ich sie gemessen hatte — beim Schrumpfen brach die Leiste um und verdeckte das Bild. **E122 gestuftes Aufgeben:** wird es eng, fällt der Inhalt in einer festgeschriebenen Reihenfolge weg (Romaji → Karaoke → Wellenform → Warteschlange → stapeln), statt dass der Umbruch entscheidet. **E123 Playlists sind Sichten, keine Kopien** — Sammlung wie jede andere, in der Seitenleiste unter „Musik", je Profil als Datei, `.m3u` für Ex- und Import. **E124 Besetzungskarte** als Spiegelbild der Pausenkarte: links was läuft, rechts wer zu sehen ist; volle Besetzung immer, „gerade im Bild" aus einem einmaligen Gesichtsdurchlauf beim Einlagern — und **nie** ins laufende Bild, anders als Amazons X-Ray. |
| 2026-08-07 | Fassung 1.2 — E118–E120. **E118:** bei Ton ohne Bild gehört die Leiste **zum Raum** (die Fläche endet darüber, nichts rutscht darunter, nichts blendet weg), bei Film bleibt sie **Überzug** — damit gibt es keine unsichtbare Barriere, die das Bild kleiner werden lässt. **E119:** die Weiche bekommt **30 s Grundzeit + 10 s je Wahl** statt 9 s Autostart — „manchmal muss ich die Fernbedienung finden"; jede Eingabe hält den Zähler ganz an. **E120 Reihen und Universen:** dieselbe Mechanik wie bei OVAs, eine Ebene höher — Werk → Reihe → Universum aus TMDB-Sammlungen, AniList-Ketten, AniDB und Wikidata; darüber **unsere** Ordnungsschicht mit drei umschaltbaren Reihenfolgen (Erscheinung · kanonisch · empfohlen). Nie automatisch quer durchs Universum starten. **Behoben:** Fernsehreihe verschmilzt jetzt Randverlauf **und** Zählwerk statt drei Varianten; Pausenkarte sitzt am linken Bildrand und ist durchsichtiger; Zusatzpunkt unter Schaltern entfernt (die Farbe reicht); die **1** beim Wiederholen sitzt zwischen den Pfeilen; Lieblingssong ist ein **Plus**, das zum gefüllten Haken wird; Karaoke ist ein **Mikrofon**; Radio ein **Sendemast** statt WLAN-Fächer; „Beschaffen" heißt **Holen** und zeigt Pfeil in Ablage; die 10-Sekunden-Ziffer berührt den Kreis nicht mehr; der Ausschnitt liegt jetzt oben auf statt dahinter. |
| 2026-08-07 | Fassung 1.1 — E112–E117. **Neu: §5.3.1 Der Grund folgt dem Material** (E114): eigene Farbe darauf ⇒ neutral, nur Schrift ⇒ warm. Damit ist der Leser für **Bilder** von `#1C1611` auf `#0F1012` gewechselt — Braun ließ gescannte Graustufen vergilbt aussehen; für **Text** bleibt es warm, dort war es immer richtig. **E112 Farbe ist die Beschriftung** (grau aus, Akzent an; nie Zustand als Text; Grün bleibt für „läuft/aktiv" reserviert; zweiter Kanal für Farbenblinde). **E113 eigener Zeichensatz** — Spotifys Satz ist geschützt und wir wollen ein eigenes Gesicht; frei sind die Formen (IEC 60417), unsere ist die Strichführung: 24er-Raster, Gleichdick 1,5, gefüllt nur wo Distanz es verlangt, Prüfung bei 16 px und in Graustufen. Entwurf `zeichen.html` mit 28 Zeichen. **E115 kanonische Weiche** am Folgenende (OVA/Folge/Regal) statt blindem Autostart, gespeist aus AniList-Beziehungen, AniDB und TMDB-Staffel 0. **E116 Nur-Ton** für Musikvideos. **E117 Hörbuch „Wo war ich?"** — sekundengenauer Stand mit 30 s Rücksprung, Erkennung des Einschlafens und eine **spoilerfreie Zusammenfassung** bis exakt zur gelaufenen Stelle. **Behoben:** Fernsehknöpfe zu wuchtig; Staffelwahl klappt am PC nach unten aus statt als Vollbild; Musikschalter tragen jetzt Zustandsfarbe. |
| 2026-08-07 | **Fassung 1.0** — E103–E111. **Neu: §5.10.2 Was fest sein muss und was atmen darf** (E103): alles, dessen Beschriftung sich beim Bedienen ändert, bekommt eine feste Breite — Faustregel „ändert sich der Text durch **meine** Handlung → fest, durch den **Inhalt** → frei", mit Tabelle für beide Seiten. **E104** Einstellen ≠ Wählen: Sprache und Fassung in „Ton & Text", Aussehen im Zahnrad — nie im selben Menü. **E105** Klick daneben schließt alles. **E106** bei Ton ohne Bild blendet nichts aus. **E107** Klangzeichen auf Distanz (Klick beim Fokuswechsel, Tock beim Bestätigen; am PC aus). **E108** Hörbücher sind keine Musik — eigenes Regal, Kapitel statt Lieder, kein Zufall, Erkennung über ASIN/M4B/Kapitelmarken. **E109** Herkunft und Güte sind Information, kein Menü — damit ist auch die halb gekaufte, halb gescannte Sammlung **ein** Werk. **E110** das Programm fragt nie, ob du etwas aufgibst; stattdessen ein selbstgesetzter Filter „über N Kapitel gelesen". **E111** Profilwechsel im Menü, nie beim Start. **Behoben:** Untertitel-Panel war gequetscht und überladen — Modus und Sprache sind raus (gehören nach nebenan), Farben in einer Reihe mit 15-px-Punkten, alle Zyklusknöpfe auf feste Breite; Klick daneben schließt jetzt; Musikleiste bleibt stehen und trägt die Aktionen als Symbolreihe; Hörbuch hat eine Kapitelliste; Staffelwechsel am Fernseher über eine Liste statt Scrollen; Endlosstreifen hat gar keine Fußleiste mehr. |
| 2026-08-07 | Fassung 0.9 — **E97–E102.** **Neu: §5.11.2 Der Rahmen** — die Antwort auf JBs wichtigste Frage („wo kommt denn der Ton her?"): *eine Sache hat das Bild, eine den Ton, und beide dürfen verschieden sein*. Klangleiste (46 px statt Spotifys 72–90, Fortschritt als 2-px-Faden, weg wenn nichts läuft), genau ein schwebendes Bildfenster (nie über Leser oder Musikfläche), genau eine Tafel, immer derselbe Bereich. Frei verschiebbare Fenster bauen wir bewusst nicht — der Layout-Editor bleibt im Downloader. **Neu: `Doku/UEBERNAHME_AUS_SYNCYOUTUBE.md` (E102)** mit Datei, Funktionsname und Regel für alles, was portiert wird: das Untertitel-Panel zeilengenau, die Ausschnitt-Favoritenregel, Karaoke, Transkript-Suche, Autotag, Umbenennung mit Probelauf, Geo-Stufen, VPN-Einbahnregel — und was ausdrücklich **nicht** übernommen wird. **Behoben:** Untertitel-Panel war „mau" und jetzt zeilengleich mit `subMenu()`; Ton-&-Text-Wahl schlug nicht auf Kopfzeile und Knopf durch; die Bedienung blendete beim Halten des Spulknopfes weg; Fußleiste lag bei Musik über der Warteschlange; Ausschnitt fehlte bei Musik; Endlosstreifen bekommt die Bildlaufschiene zurück, mit Fortschritt **je Kapitel**; drei Fernsehreihen ohne Bildlaufbalken zur Auswahl. |
| 2026-08-07 | Fassung 0.8 — **E89–E96, F10 geschlossen.** **Musik im vorhandenen Modell:** das Lied ist das Werk, die Aufnahme die Ausgabe, das Album eine Gruppe (§4.2) — MusicBrainz' drei Ebenen fallen genau auf unsere vorhandenen, kein neuer Begriff nötig; Coverversion, Remix, Live-Fassung und DJ-Set lösen sich damit von selbst. **Neu: §5.11.1 Bestandsaufnahme SyncYouTube** (JB-Einwand: „du hast nicht genau hingeschaut, was wir bereits erschaffen haben") — Ausschnitt-Werkzeug, Karaoke mit Romaji, „Auf YouTube öffnen", Mini-Player und Transkript-Suche fehlten im Entwurf und sind jetzt E89–E93; das vorhandene Untertitel-Panel wird übernommen statt neu geschrieben; die Kompakt-Ansicht des Downloaders bestätigt E88 aus dem eigenen Bestand. **E94** Folgen am PC als Raster, am Fernseher als Reihe mit Staffelwand. **E95** ein Ort für den Fortschritt — die angedockte Schiene im Endlosstreifen ist gestrichen, sie war doppelt und liess unten eine halbleere Leiste stehen (JB: „der Bildschirm wird nicht magisch größer"). **Behoben:** Spulen sprang beim Loslassen nochmal 10 s, weil `mouseleave` und `mouseup` beide stoppten; Zahnrad sah aus wie eine Sonne; „Warteschlange" öffnete die Ton-Tafel; Pausenkarte gibt es jetzt für alle drei Gestalten. |
| 2026-08-07 | Fassung 0.7 — **E78–E88.** Neu: **§5.8.1 Titel sind vielsprachig** (kein „richtiger" Titel; Englisch ist keine Leitwährung; Romanisierungen normalisiert vergleichen; Titelvorrat wächst nur) und **E87 nie früh verwerfen** — Falsch-Behalten schlägt Richtig-Wegwerfen. **§5.10.1 Kachelgrößen:** die Mini-Kachel ohne Titel ist gestrichen (JB: „dann sehe ich nicht, welchen Manga ich lese") — Titel ist Rang 1 der Prioritätsleiter und fällt nie; stattdessen „Dicht" mit einzeiligem Titel. **Bühne erweitert:** 10 s tippen / halten spult mit 4×–12×–30× (Vergleich Netflix, Plex, Jellyfin, Kodi, Prime, VLC, mpv) · Bedienung liegt im Bild und blendet weich weg (420 ms raus, 120 ms rein) · Pausenkarte nach 12 s mit Rollenzeile, nie Empfehlungen · „Ton & Text" statt „Spuren", Einstellen vom Auswählen getrennt (Zahnrad) · Folgen unter der Bühne. **Suche:** erweiterte Suche zugeklappt mit Zähler, dieselbe Dreistufigkeit, und **das kluge Regal** (gespeicherte Suche wird Regal). **E85 Zahlentypografie:** die Luft gehört dem Trenner, ausgerichtet mit Ziffernleerzeichen, Füllbreite aus der aktuellen Ansicht — damit hören vierstellige Kapitel auf, am Schrägstrich zu kleben. **Neu: §13.1 Wie weit wir sind** und **`Doku/ENTWUERFE.md`** als Index der elf Entwürfe. Drei weitere Fallen in §5.11 (`visibility` reserviert Platz · Maßstab am falschen Element · Zellbreite trägt den Abstand). |
| 2026-08-07 | Fassung 0.6 — **E72–E77.** Neu: **§5.12 Die Bühne** (Video, Musik, Hörbuch auf einer Fläche; die Leiste als Landkarte der Folge; wer welche Untertitel zeichnet; feste Gamepad-Belegung; der Übergang Hören ↔ Lesen). **§8.4 um E76 erweitert:** wie die Erweiterung dasselbe Werk auf verschiedenen Seiten, unter anderen Titeln, von anderen Gruppen und mit anderer Kapitelzählung wiedererkennt — die Adresse ist ein Hinweis, nie ein Beweis. **E58 verschärft:** Leserichtung hat zwei Achsen (Fluss + Achse); Chinesisch ist der Sonderfall, weil Webtoon und gebundener Band verschieden laufen. **JB-Funde:** „Spieler" war zweideutig → **Bühne**, das Wort kommt auf die Verbotsliste des Text-Wächters (Dokument durchgesehen und umgestellt) · „gesamt" hieß fälschlich Endstand → **erschienen**, drei Zahlen, alle echt · `…` statt `?` · Geführt-Modus zoomte nicht, sondern verkleinerte den Text (Einpassen hebt Zoom auf). Drei neue Fallen in §5.11. |
| 2026-08-07 | Fassung 0.5 — **E53–E71.** Neu: **§5.8 Die Suche** (ein Feld, zwei Gruppen, drei Zustände, dreistufige Filter, Zusammenführungsregeln, die sieben Entnerv-Regeln) · **§5.9 Der Leser** (Leserichtung als Eigenschaft der Ausgabe, ein Griff mit zwei Gedächtnissen, keine Restzeit beim Lesen) · **§5.10 Schrift und Zeichen** (Inter/Literata/Atkinson/JetBrains Mono; ▶ vs. Lesezeichen-Pfeil; zwei Farbskalen; Wortabzeichen statt Emoji; die Kapitelzelle) · **§5.11 Gelernte Fallen** (sieben Fehler, die in dieser Sitzung wirklich passiert sind) · **§8.4 Die Browser-Erweiterung** (vier Knopfzustände, drei Eingriffe je Seite, nur `127.0.0.1`, Adapterliste lokal). Die „zehn unverhandelbaren" aufgeteilt in **zehn Regeln der Bauart** und **vier Regeln des Vertrauens** — die alte Zehnerliste bleibt unverändert. Entwürfe: `suche.html`, `erweiterung.html`; `leser.html` und `regal.html` überarbeitet. **JB-Funde:** geteilter Regler zwischen Zoom und Schriftgröße · „Kapitel 88 von 122" war zweideutig · 🖐-Emoji unlesbar · Restdauer beim Lesen setzt unter Druck. |
| 2026-08-07 | Fassung 0.4 — **Name entschieden: SyncFindus** (der Fundus ist im Theater und Film der Bestand, aus dem man schöpft). Datei umbenannt. E46–E52: Meilensteine nur einmal · Blu-ray über externes Werkzeug einbinden statt selbst entschlüsseln · **genau ein Ausgang pro Datei** (JB-Einwand gegen kaskadierende Regeln — berechtigt, Modell vereinfacht) · Fehlerprotokoll lokal/verschlüsselt/opt-in · GPU nachgebend · Anmeldungen erneuern sich still · deterministischer Kern. Warteschlange um die drei Fehlerarten und vergiftete Aufträge erweitert. Qualitätsnetz um die extreme Stufe erweitert (JB: „machen"). **Neu: §16 Übergabe an eine zweite KI** mit verbindlicher Baureihenfolge. **Neu: die zehn unverhandelbaren.** Aufgeräumt: §12.6 war falsch eingerückt, §5.6/5.7 neu geordnet. |
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

### 16.5 Übernahme aus SyncManga — was trägt, was klemmt (Analyse 07.08.2026)

**JB:** *„Die Übernahme aus SyncManga ist ein wichtiger Schritt, wir haben lange daran
gewerkelt, es ist ein fertiges Produkt mit kleinen Baustellen. Was kann man jetzt, wo wir neu
aufsetzen, anpacken? Was für ineinandergreifende Macken hat SyncManga?"*

Gelesen wurden alle 18 Module (≈ 9.150 Zeilen) plus `data/`. Das Urteil vorweg:
**die Logik ist gut und wandert fast vollständig mit; die Architektur hat drei Konstruktionen,
die einander verstärken.** Nicht die einzelnen Macken sind das Problem, sondern wie sie
ineinandergreifen.

#### Was ohne Änderung mitkommt

| Modul | Z. | Warum es trägt |
|---|---|---|
| `parse.py` | 264 | Seiteneffektfrei, vollständig getestet, jede Regex mit Datenbeleg im Kommentar. **Vorbild für alles andere.** |
| `catalog.py` | 514 | Fallback-Kette mit `srcstatus`-Meldung — genau das Muster aus §7 |
| `sources.py` | 1.025 | Fünf Adapter, je eine Tempobremse mit dokumentiertem Limit |
| `readerlink.py` | 1.312 | Kapitel-URL **raten und per HTTP bestätigen** statt MangaDex — die beste Einzelidee im Programm |
| `health.py` / `linkhealth.py` | 557 | Quellen-Ampel, tote Reader, Sperrpausen |
| `anilist.py` | 233 | OAuth + Zwei-Wege-Abgleich, funktioniert |
| `i18n.py` | 518 | Text-Wächter samt CJK-Prüfung |

#### Die drei ineinandergreifenden Macken

**① Der Zustand wohnt im `localStorage` einer erzeugten HTML-Datei.**
Favoriten, Archiv, Kapitelkorrekturen und Bestätigungen liegen im Browser, nicht im Programm.
`render.py` erzeugt `Manga_Leseliste.html`, das JS schreibt in `localStorage`, ein 💾-Knopf
exportiert nach `data/list_state.json`, und der **nächste** Lauf bettet die Datei wieder ein.
Vier Umwege, und **einer davon ist ein Mensch, der auf 💾 drücken muss.**
→ Wer das vergisst und die Website-Daten löscht, verliert Jahre.

**② Der Schlüssel dieses Zustands war der Titel.**
`data-h` war `norm(Anzeigetitel)` — **jede Titelkorrektur invalidierte Archiv, Favoriten und
Bestätigungen** (JB: *„Mein Archiv hat sich resetted"*). Repariert mit einer Alias-Karte
`MIG`, die das JS beim Start einmalig umschreibt. Die Reparatur ist sauber gemacht; die
**Ursache** ist, dass Identität und Zustand denselben Schlüssel teilten → **E146**.

**③ Cache und Bibliothek sind dieselbe Datei.**
`md_cache.json` ist Zwischenspeicher *und* Datenbestand. Deshalb gibt es `CACHE_VER`
(inzwischen **32**): eine neue Zahl erzwingt beim nächsten Lauf eine **vollständige
Neuanreicherung aller ~800 Serien**, nur weil *ein* neues Feld dazugekommen ist. Jede
Erweiterung kostet damit einen Volllauf gegen fünf gedrosselte Fremdquellen.

> 🔑 **Das Ineinandergreifen:** ① macht den Zustand flüchtig, ② macht ihn an der Identität
> zerbrechlich, ③ zwingt regelmäßig zu Läufen, die genau diese Identität neu bestimmen.
> Jede Macke für sich ist verkraftbar. Zusammen ergeben sie: *„mein Archiv hat sich
> resetted."*

**Die Kur** *(JB 08.08.2026: „Schließe die Probleme und brech den Damm.")* — alle drei
verschwinden durch **eine** Entscheidung, und die ist hiermit getroffen:

> 🔑 **E151 — Das Register ist die Wahrheit. Die Anzeige ist eine Sicht darauf, nie ein
> Speicher.**

Was daraus konkret folgt — das ist der Damm, und er ist gebrochen:

| Nr. | Beschluss | Erledigt Macke |
|---|---|---|
| **1** | **SQLite** ist der einzige Ort, an dem Zustand lebt. Kein `localStorage`, keine erzeugte HTML-Datei, **kein 💾-Knopf**, den ein Mensch drücken muss | ① |
| **2** | **Schlüssel ist die stabile Werk-ID**, nie `norm(Titel)` und nie ein Titel-Hash. Titel sind Anzeigedaten und dürfen sich jederzeit ändern | ② (E146) |
| **3** | **Cache ≠ Bibliothek.** Zwei getrennte Ablagen: die Bibliothek ist dauerhaft, der Cache ist wegwerfbar. Ein gelöschter Cache kostet Zeit, nie Daten | ③ |
| **4** | **Kein `CACHE_VER` mehr.** Jedes Feld trägt sein **eigenes Alter** und seine **eigene Herkunft**. Ein neues Feld holt genau dieses Feld nach — für die 800 Serien, nicht *alles* für alle | ③ |
| **5** | **Anreicherung ist ein Auftrag je Feld**, nicht ein Volllauf. Damit gibt es keinen Moment mehr, in dem das Programm alle Identitäten gleichzeitig neu bestimmt | ①②③ |
| **6** | **Pfade kommen von außen herein.** Kein Modul sucht je selbst nach `../../../SyncDashTray/System/` (`readers.py:181`) | Streufund |
| **7** | **Mitgelieferte Regeln und Nutzerdatei vereinen sich, sie ersetzen sich nicht.** Die Sperrliste aus `config.py:159` ist die Blaupause dafür, wie es *nicht* geht | Streufund |
| **8** | **Die HTML-Ausgabe bleibt — als Export** (E14, Grundrecht), nicht als Anwendung. Sie darf gelesen werden, sie speichert nichts | ① |

**Warum das der Damm ist und nicht bloß eine Aufräumaktion:** Solange der Zustand in der
Anzeige wohnt, muss *jede* neue Ansicht ihren eigenen Speicher mitbringen — Leser, Bühne,
Regal, Postfach, Warteschlange, Handy. Sechs Speicher, die sich widersprechen können. Mit
E151 gibt es genau einen, und alle sechs sind **Fenster darauf**. Das ist die Entscheidung,
die den Rest des Programms überhaupt erst baubar macht.

#### Kleinere Baustellen, benannt

| Fund | Ort | Bewertung |
|---|---|---|
| Pfad zu `md_cache.json` sucht `../../../SyncDashTray/System/` | `readers.py:181` | Rest der Suite-Herkunft. **Muss weg** — Pfade kommen von außen herein, nie aus dem Modul |
| Veraltete `sources.json` überschrieb die eingebaute Sperrliste → alle neuen Sperren wirkungslos | `config.py:159` | Repariert, aber ein Muster: **mitgelieferte Regeln und Nutzerdatei müssen sich vereinen, nicht ersetzen** |
| `cp1252`-Konsole unter Windows | `common.py:26` | Verschwindet mit einer echten Oberfläche |
| Ein Modul mit 1.644 Zeilen (`enrich.py`) | — | Erkennung, Anreicherung, Fortschrittsmeldung und Cache-Pflege in einer Datei. In SyncFindus sind das vier Auftragsarten (§4.5) |
| `data/sources.json`, `data/readers_pattern.json` **öffentlich im Repo** | `data/` | ⚠️ Genau die Artefaktklasse aus **E12**. Vor dem Umzug zu klären |
| `overrides.json` hat 647 Zeilen Handkorrekturen | `data/` | **Das wertvollste Datenstück überhaupt** — Jahre an Handarbeit. Wandert 1:1, mit Herkunft „Hand" und höchster Rangstufe (E135) |

#### Was jetzt möglich wird, was vorher nicht ging

Beide neuen Fähigkeiten — **eigener Leser** und **Herunterladen** — verschieben mehrere alte
Kompromisse:

| Alt | Warum es so war | Neu |
|---|---|---|
| Link **raten und bestätigen** (`readerlink.py`) | wir konnten nur *hinschicken* | Wir holen die Kapitelliste selbst → **kein Raten mehr**, der Link ist ein Nebenprodukt |
| Ampel „welche Seite lebt noch" | die Seite *war* das Produkt | Die Seite ist eine **Bezugsquelle** unter mehreren. Stirbt sie, wird woanders geholt — der Lesestand merkt nichts (E76) |
| `PAYWALL_SITES` als Sperrliste | Volume-1-frei-Modelle täuschten die Erkennung | Wird zur **Güteangabe**: MANGA Plus ist ein legaler *Leseort* mit Lücken, kein toter Reader |
| „übersetzt / gesamt" aus MangaUpdates | wir konnten nur zählen, was **andere** übersetzt hatten | Wir übersetzen selbst (§10.2) → die mittlere Zahl wird *„bei dir lesbar"* |
| Bewertung = Median über Datenbanken | keine eigenen Daten | Bleibt — **und bekommt das eigene Lesetempo daneben** (Startseite, E19) |
| Ausgabe = eine HTML-Datei | kein eigenes Fenster | Die HTML-Ausgabe bleibt als **Export** (E14, Grundrecht), ist aber nicht mehr die Anwendung |

#### E162 — SyncManga ist Lehrer, nicht Vorgänger

**JB, 08.08.2026:** *„Ich finde das System hinter SyncManga gut, aber ich finde die Library ist
egal. Die sollten wir uns selber aufbauen. Bisher nutzt nur eine weitere Person SyncManga. Ich
habe viel aus dem Programm gelernt, doch hier sollten wir einen Neuanfang riskieren — wir sind
noch nicht so etabliert, dass wir nichts wagen können. Vielleicht können wir so alte Fehler
besser schließen."*

> 🔑 **Damit fällt die größte Fessel des ganzen Vorhabens.** Bis heute stand über allem: *„800
> Werke müssen am ersten Tag drin sein, sonst wird das Programm nicht benutzt."* Dieser Satz
> hat das Datenmodell mitgeformt — jede Entscheidung musste rückwärtskompatibel zu einer
> Struktur sein, die wir gerade erst als dreifach fehlerhaft beschrieben haben.

**Was das konkret ändert:**

| Vorher | Jetzt |
|---|---|
| Migration ist **Voraussetzung** für die erste Fassung | Migration ist ein **Werkzeug**, das später kommen darf |
| Das neue Modell muss das alte abbilden können | Das neue Modell muss **nur richtig sein** |
| Der Prüflauf-Bericht ist der riskanteste Entwurf | Er ist ein normaler Entwurf ohne Zeitdruck |
| Erste Fassung = „800 Werke drin" | Erste Fassung = **„ein Werk richtig"** |

**Und hier die eine Sache, die ich trotzdem festhalten will** — nicht als Widerspruch, sondern
weil sie sonst später schmerzt:

⚠️ **Dateien sind ersetzbar, Lesestand nicht.** Ein Regal baut man in Wochen neu auf; *„ich war
bei Kapitel 1141"* mal 800 baut niemand neu auf. Das ist der einzige Teil von SyncManga, der
sich nicht wiederbeschaffen lässt — und es sind ein paar hundert Kilobyte.

> **Der Kompromiss, der beides erfüllt:** Wir bauen die Bibliothek **komplett neu**, ohne
> Rücksicht auf die alte Struktur. Aber wir bauen **einen einzigen kleinen Leser** für
> `md_cache.json` + `list_state.json`, der genau **drei Felder** herausholt: *Werk-Titel ·
> zuletzt gelesenes Kapitel · Datum*. Kein Overrides-Umzug, keine Linkgesundheit, keine
> Reservequellen, kein Prüflauf-Zeremoniell. Diese drei Felder gehen durch **dieselbe
> Erkennung wie jede andere Quelle** (§8.2) — was eindeutig ist, wird übernommen, der Rest geht
> ins Postfach.
>
> **Das ist kein Umzug, das ist ein Import wie jeder andere** — und genau deshalb passt er zum
> Neuanfang statt ihn zu behindern. Aufwand: ein Nachmittag. Nutzen, falls du ihn brauchst:
> sieben Jahre.

Ob du ihn ausführst, entscheidest du am Tag der ersten Fassung. **Es blockiert nichts.**

#### Falls doch migriert wird: die Regeln

⚠️ Diese Regeln gelten weiterhin — aber sie beschreiben jetzt ein **Angebot**, keine Pflicht.

1. **Lesen, nicht anfassen.** `md_cache.json` + `list_state.json` + `overrides.json` +
   `series_overrides.json` werden gelesen; SyncManga läuft unverändert weiter, bis JB selbst
   umschaltet. **Kein Migrationsschritt darf die alte Installation verändern.**
2. **Prüflauf zuerst.** Der erste Lauf schreibt nichts, sondern einen Bericht: *so viele
   Werke, so viele eindeutig, so viele ins Postfach, diese Handkorrekturen kollidieren.*
3. **Handkorrekturen gewinnen immer.** Die 647 Zeilen `overrides.json` schlagen jede
   Datenbank (E135). Wo eine Handkorrektur einer Neuanreicherung widerspricht, gewinnt die
   Hand, und der Widerspruch wird **vermerkt**, nicht aufgelöst.
4. **Zurück können.** Die alte Installation bleibt vollständig, bis JB freigibt. Ein
   Rückweg, den man nie braucht, kostet nichts; einer, den man braucht und nicht hat, kostet
   alles.
5. **Der Bruchtest läuft ab Tag eins** (E147) — gerade weil migrierte Daten die Sorte
   Widerspruch tragen, die niemand vorhergesehen hat.

### 16.6 Die Kleinen — mit Ja oder Nein entschieden (08.08.2026)

Aus `NICHT_UEBERNOMMEN.md`. Alles hier braucht **keinen Entwurf**, nur eine Entscheidung —
und die steht jetzt. Vier davon sind ein **Nein**, und das ist der wertvollere Teil der Liste.

| Aus | Urteil | Warum |
|---|---|---|
| **Abos mit Regeln** (8 Funktionen, `_abo_regel_ok`, `_abo_baseline`, `abo_erneuern`, `abo_aufraeumen`) | ✅ **ja** — wird eine **Auftragsart** in §4.5 | Eine Grundlinie („was zählt ab wann als neu") ist genau die Frage, die man beim ersten Abo vergisst und danach nie wieder löst. Der Code hat sie beantwortet |
| **Zugangsprüfung vor dem Holen** (`_zugang_ok`, `geo_test_lauf`, `_geo_download`) | ✅ **ja** — ist **E149** | „Vorprüfung kostet keine Bytes" hat schon eine Umsetzung. Sie wird portiert, nicht nachgebaut |
| **Nachträgliche Anreicherung** (`metadaten_backfill`, `technik_backfill`, `biblio_enrich_alle`) | ✅ **ja** — ist **E151/4** | Feldalter je Feld *braucht* einen Nachziehlauf, sonst holt nichts die alten Einträge ein |
| **Erweiterungs-Nachschub** (`addon_nachschub`, `addon_hab_liste`, `addon_update_info`) | ✅ **ja** — gehört zu §8.4 | §8.4 sagt, was die Erweiterung tut, nicht **wie sie zum Nutzer kommt und sich erneuert** |
| **`huelle.py`** (216 Z.) | ✅ **ja** — Ausgangspunkt für §12.4 | F01 ist beantwortet, der vorhandene Code war nur nie als Startpunkt benannt |
| **Statistik-Tafel** (9 Auswertungen) | ✅ **ja** — als Teil des **lesbaren Profils** (E19) | „Das denkt SyncFindus über dich" ist genau der Ort dafür. Keine eigene Ansicht, kein eigener Menüpunkt |
| **Kapitelkorrektur von Hand** (`chapfix`) | ✅ **ja** — als **Standard-Ausgang** im Postfach | §8 hat den automatischen Versatz ab 80 %. Passt keiner, ist die Handeingabe der Ausgang aus Grund 3 (E141) |
| **MAL-XML hinein und hinaus** | ✅ **ja** | Der De-facto-Austauschstandard. Hinein beim ersten Start (§12.2, Weg 3), hinaus als Grundrecht (E14) |
| **Zufallspick 🎲** (`luckyPick`) | ✅ **ja**, klein | Nicht dasselbe wie der Joker in §11: der Joker empfiehlt **Fremdes**, der Würfel zeigt **Eigenes**. Zwei Bedürfnisse, zwei Knöpfe (E128 gilt sinngemäß) |
| **Familie / Nachbarschaft** (`familie.py`, 193 Z.) | ✅ **ja** — wurde **E179** (LANoMAT) | JB fragte am selben Tag danach. Es ist dasselbe Problem wie E169: ein Werk liegt irgendwo, das mir nicht gehört — also eine vierte Sorte **Ort**, kein eigenes System |
| ❌ **Selbstneustart bei Codeänderung** | **nein** | Siehe E172: ein signiertes Programm, das seinen Quelltext beobachtet und sich selbst austauscht, ist für jeden Virenscanner Schadsoftware |
| ❌ **Spaltenwahl** (`cols_menu`) | **nein** | Eine Spaltenwahl ist meistens die Ausrede dafür, die **Prioritätsleiter** (E39) nicht geschrieben zu haben. Wir haben sie geschrieben. Wer trotzdem etwas vermisst, hat einen Fehler in der Leiter gefunden — und der gehört behoben, nicht umgangen |
| ❌ **Tonspurwahl beim externen Abspielen** (`_ton_spur_waehlen`, `extern_abspielen`) | **nein** | **E34**: nie ein zweites Fenster. Die Tonspurwahl selbst lebt längst in „Ton & Text" (E83). *Öffne das in VLC* bleibt als reiner Systemaufruf möglich — aber ohne dass wir dort etwas steuern |
| ❌ **Cloud-Slot** `manga.j-bk.org` (`cloud.py`, 175 Z.) | **nein** — ersetzt durch Gerätekopplung (§12) | Kein fremder Server für den eigenen Lesestand. ✅ **Aber die Haltung wird übernommen:** kein Konto, keine E-Mail, nur das Nötige — das war vorbildlich und gilt für die Kopplung genauso |

> **Was ein Nein hier wert ist:** Vier Funktionen, die es gibt und die funktionieren, kommen
> trotzdem nicht mit — jede mit einem Grund, der aus einer bestehenden Entscheidung folgt
> (E172, E39, E34, §12). *Eine Übernahmeliste, die nur aus Ja besteht, ist keine Liste, sondern
> ein Umzug.*

### 16.7 Wo die Wahrheit steht

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
