# Übergabe-Prompt für die zweite KI

> Alles ab der gestrichelten Linie ist **zum Kopieren**. Es ist bewusst lang: die zweite KI
> arbeitet **allein und über Nacht**, und jede Frage, die sie nicht stellen kann, muss hier
> beantwortet sein.

---

## Kurzfassung für JB

| | |
|---|---|
| **Was der Prompt tut** | Lässt die zweite KI die drei Vorgänger-Repos auf dem Rechner **suchen**, das Pflichtenheft lesen, und dann **Baustein 1–3 bauen** — Register, Warteschlange, Erkennung |
| **Wie lange** | So lange sie will. Sie stoppt von selbst, wenn ein Baustein grün ist und der nächste eine Entscheidung von dir braucht |
| **Was am Morgen dasteht** | Ein `ARBEITSPROTOKOLL.md` mit allem, was passiert ist, plus eine Liste **„das musst du entscheiden"** |
| **Was sie nie tut** | Auf `main` pushen · etwas löschen · zwangspushen · Zugangsdaten anfassen · irgendwo etwas veröffentlichen |

---

```text
━━━━━━━━━━━━━━━━━━━━━━━━━━ AB HIER KOPIEREN ━━━━━━━━━━━━━━━━━━━━━━━━━━

Du baust SyncFindus. Ich schlafe. Arbeite selbständig durch, bis du an
einen Punkt kommst, an dem nur ich entscheiden kann — dann schreib es
auf und mach woanders weiter.

═══════════════════════════════════════════════════════════════════════
0 · ZUERST: FINDEN
═══════════════════════════════════════════════════════════════════════

Suche auf diesem Rechner nach drei Projekten. Ich weiß nicht, wo genau
sie liegen — such sie.

Suchbegriffe (Ordnernamen):
    SyncManga · SyncYouTube · SyncEngine · SyncDashTray · SyncFindus

Suche in dieser Reihenfolge, hör auf, sobald du fündig wirst:
    1. Der Ordner, in dem du gerade stehst, und seine Geschwister
    2. Benutzerordner: Dokumente, Projekte, Code, Git, Desktop, Downloads
    3. Alle Laufwerke, nach Ordnername (nicht nach Inhalt — das dauert ewig)

Windows:
    Get-ChildItem -Path C:\,D:\,E:\ -Directory -Recurse -Depth 5 `
      -Include Sync* -ErrorAction SilentlyContinue | Select FullName
Linux/macOS:
    find / -maxdepth 6 -type d -name 'Sync*' 2>/dev/null

Wenn du eines nicht findest, hol es von GitHub:
    https://github.com/schn4ppi/SyncManga      (enthält das Pflichtenheft)
    https://github.com/schn4ppi/SyncYouTube

Prüfe jeden Fund, bevor du ihn benutzt: liegt in SyncManga ein Ordner
`Doku/` mit `VISION_SYNCFINDUS.md`? Liegt in SyncYouTube ein Ordner
`System/` mit `youtube_app.py` (~6.200 Zeilen)? Wenn nicht, ist es der
falsche Ordner. Ein Ordner heißt nicht das, was drinsteht.

Schreib mir am Ende in eine Zeile, wo du was gefunden hast.

═══════════════════════════════════════════════════════════════════════
1 · DANN: LESEN — vollständig, vor der ersten Zeile Code
═══════════════════════════════════════════════════════════════════════

In dieser Reihenfolge. Überspring nichts, fass nichts zusammen.

  1. SyncManga/Doku/VISION_SYNCFINDUS.md   ← das Pflichtenheft, ~3.900
     Zeilen, 183 nummerierte Entscheidungen (E001–E183). Das ist der
     Bauplan. Alles andere ist Beiwerk.
  2. SyncManga/Doku/NICHT_UEBERNOMMEN.md   ← was aus den Vorgängern
     übernommen wird und was ausdrücklich nicht, mit Begründung
  3. SyncManga/Doku/UEBERNAHME_AUS_SYNCYOUTUBE.md ← welcher Code wörtlich
     portiert wird, mit Datei und Funktionsname
  4. SyncManga/Doku/ENTWUERFE.md           ← Verzeichnis der 22 Entwürfe
  5. SyncManga/Doku/entwuerfe/*.html       ← die Entwürfe selbst. Öffne
     sie im Browser. Sie sind anklickbar und zeigen, wie es aussehen
     soll. Wenn Text und Entwurf sich widersprechen, gilt der TEXT —
     und du schreibst den Widerspruch ins Protokoll.
  6. SyncManga/Doku/PFLEGE.md              ← die wiederkehrende Prüfung
  7. Den Quelltext beider Vorgänger, mindestens die Kopfkommentare
     jeder Datei.

WICHTIG BEIM LESEN DES ALTEN CODES: Wo im Quelltext ein Kommentar mit
"JB" und einem Datum steht, steckt ein echter Fehler aus dem Betrieb
dahinter. Diese Kommentare sind der eigentliche Wert des alten Codes.
Sie werden mit portiert, nicht wegoptimiert.

═══════════════════════════════════════════════════════════════════════
2 · DIE REGELN, DIE NIE GEBROCHEN WERDEN
═══════════════════════════════════════════════════════════════════════

Diese stehen ausführlich im Pflichtenheft. Hier die, an denen der Bau
scheitert, wenn du sie verletzt:

  E151  Das Register (SQLite) ist die Wahrheit. Jede Anzeige ist eine
        SICHT darauf, nie ein Speicher. Kein Zustand in HTML, kein
        localStorage, keine Datei, die ein Mensch exportieren muss.
  E146  Der Schlüssel eines Fortschritts ist die stabile ID — nie der
        Titel, nie ein Titel-Hash. (Der Vorgänger hat das falsch
        gemacht und damit Archiv und Favoriten zerstört.)
  E182  Fortschritt ist eine MENGE, keine Zahl. Je Einheit drei
        Zustände: ungesehen / mittendrin (mit Marke) / gesehen.
  E11   Nie ein fremdes Datenmodell in den Kern lassen. Adapter
        übersetzen nach außen. Der Kern weiß nicht, dass Jellyfin
        existiert.
  E52   Deterministischer Kern: kein random(), kein now() IN DER LOGIK
        — beides wird hineingereicht. Ohne das ist kein Fehler
        reproduzierbar und der Bruchtest wertlos.
  E48   Genau ein Ausgang je Datei: Werk ODER Eigenes ODER Postfach.
        Nie verschwindet eine.
  E168  Löschen geht in den Papierkorb. Nie endgültig. Auch nicht für
        Zwischenspeicher, auch nicht auf ausdrücklichen Wunsch.
  E12   Der Quellenkatalog ist eine Laufzeitdatei, NIE Repo-Inhalt.
        Leg niemals eine Liste von Quellenadressen ins Repo.
  E71   Vor dem Zeigen prüfen. Kein Artefakt geht raus, das nicht
        syntaktisch geprüft ist.

═══════════════════════════════════════════════════════════════════════
3 · WAS DU BAUST — in dieser Reihenfolge, nicht anders
═══════════════════════════════════════════════════════════════════════

Baustein N+1 wird nicht angefangen, solange N nicht GRÜN ist. "Grün"
heißt nicht "läuft", sondern: die Eigenschaften unten sind geprüft.

  BAUSTEIN 1 · Register und Werk-Modell
    Werk · Ausgabe · Gruppe · Beziehung · Position (§4.2, §4.3, §4.4)
    Dazu die vier Orte aus §4.7 als Datenmodell (noch ohne Anbindung).
    GRÜN, wenn diese vier Eigenschaften an erfundenen Daten halten:
      · Jede Datei, die hineingeht, kommt als Werk ODER Eigenes ODER
        ins Postfach — nie verschwindet eine.
      · Die Leiter sortiert bei jeder Eingabe stabil.
      · Fortschritt geht nie rückwärts, außer der Nutzer setzt ihn.
      · Jede Handkorrektur überlebt jede Neuanreicherung.

  BAUSTEIN 2 · Die Warteschlange
    Sieben Auftragsarten (§4.5), drei streng getrennte Fehlerarten,
    das Rennen (E149) und der Wunsch, der nie stirbt (E150).
    GRÜN, wenn: ein Programmfehler NIE wiederholt wird (E45), ein
    vergifteter Auftrag sichtbar ausfliegt, und ein Wunsch nach
    Scheitern aller Kandidaten weiterlauert.

  BAUSTEIN 3 · Erkennung und Identität
    Die Kaskade aus §8.2, das Postfach mit seinen sechs Gründen (§8.6),
    die sechs Zeugen (§8.5).
    GRÜN, wenn das Postfach genau die sechs Gründe kennt und jeder
    einen Standard-Ausgang hat.

  DANACH kommen 4–10 (Regal, Suche, Leser, Bühne, Erweiterung,
  Beschaffung, Veredelung). Fang sie NICHT an, bevor 1–3 grün sind.
  Wenn du bis dahin kommst, hast du eine gute Nacht gehabt.

═══════════════════════════════════════════════════════════════════════
4 · WIE DU ARBEITEST
═══════════════════════════════════════════════════════════════════════

Wenn Superpowers verfügbar ist, benutze es — und zwar in der Reihenfolge,
die es selbst vorgibt: erst durchdenken, dann einen schriftlichen Plan,
dann testgetrieben bauen, dann prüfen, bevor du etwas "fertig" nennst.
Lies zuerst nach, welche Skills du wirklich hast, statt Namen zu raten.

Ohne Superpowers dasselbe von Hand:
  1. Plan schreiben, bevor du Code schreibst. In eine Datei, nicht in
     den Chat.
  2. Test zuerst. Die vier Eigenschaften oben sind keine Testfälle,
     sondern Regeln, die IMMER gelten — schreib sie als
     eigenschaftsbasierte Tests (Hypothesis), nicht als Beispiele.
  3. Kleine Schritte, oft festschreiben (committen). Ein Commit soll
     eine Sache tun und in einem Satz erklärbar sein.
  4. Nach jedem Baustein: die Eigenschaften laufen lassen. Rot heißt,
     du bist nicht fertig.

Sprache: Code und Kommentare auf DEUTSCH, wie in beiden Vorgängern.
Bezeichner dürfen deutsch sein (werk, ausgabe, fortschritt). Halte dich
an den Stil, den du im alten Code vorfindest — nicht an deinen eigenen.

Zweig: Arbeite auf einem eigenen Zweig, benannt nach dem Baustein, z.B.
`bau/1-register`. Niemals auf main.

═══════════════════════════════════════════════════════════════════════
5 · WAS DU NIEMALS TUST, OHNE MICH ZU FRAGEN
═══════════════════════════════════════════════════════════════════════

  · Auf main pushen oder irgendetwas zwangspushen (force)
  · Git-Historie umschreiben
  · Dateien löschen, die du nicht selbst angelegt hast
  · Die vorhandenen SyncManga/SyncYouTube-Installationen anfassen.
    LIES sie, ändere sie nicht. Sie laufen noch.
  · Zugangsdaten, Schlüssel, Tokens anlegen, lesen oder verschicken
  · Etwas veröffentlichen, hochladen oder verschicken
  · Geld ausgeben, Konten anlegen, Dienste abonnieren
  · Eine Liste von Quellenadressen ins Repo legen (E12)

═══════════════════════════════════════════════════════════════════════
6 · WENN DU FESTSTECKST
═══════════════════════════════════════════════════════════════════════

Nicht warten. Nicht raten. In dieser Reihenfolge:

  1. Steht die Antwort im Pflichtenheft? Such nach der E-Nummer.
  2. Hat einer der Vorgänger das Problem schon gelöst? Dann portiere,
     statt neu zu bauen — das ist ausdrücklich erwünscht.
  3. Kannst du eine Annahme treffen, die sich später billig umdrehen
     lässt? Dann triff sie, SCHREIB SIE AUF und mach weiter.
  4. Erst wenn keins davon geht: ins Protokoll unter "DAS MUSST DU
     ENTSCHEIDEN", und am nächsten Punkt weiterarbeiten.

Drei Dinge sind im Pflichtenheft bekannt-unfertig. Wenn du dort
ankommst, arbeite drumherum und schreib es auf:
  · Die WERKSTATT — der Ort für Rücknahmen, Regeln und Handkorrekturen
    (E41, E135, E141, E173) ist neunmal genannt und nie definiert.
  · Die EINSTELLUNGEN haben keinen Entwurf.
  · Leere und kaputte Zustände sind nirgends beschrieben.
Alle drei betreffen die Oberfläche. Baustein 1–3 kommen ohne sie aus.

═══════════════════════════════════════════════════════════════════════
7 · WAS AM MORGEN DASTEHEN SOLL
═══════════════════════════════════════════════════════════════════════

Eine Datei `ARBEITSPROTOKOLL.md` im SyncManga-Repo, mit:

  1. GEFUNDEN — welches Projekt liegt wo auf dem Rechner
  2. GELESEN — was du gelesen hast, und was dir dabei aufgefallen ist
     (besonders: Widersprüche im Pflichtenheft, Dinge die nicht
     zusammenpassen — die sind wertvoller als der Code)
  3. GEBAUT — was steht, was grün ist, was noch rot
  4. ANNAHMEN — jede Entscheidung, die du selbst getroffen hast, mit
     einem Satz warum und wie teuer es wäre, sie umzudrehen
  5. DAS MUSST DU ENTSCHEIDEN — die Liste für mich, sortiert danach,
     was am meisten blockiert
  6. WAS ICH ALS NÄCHSTES TUN WÜRDE — drei Zeilen

Schreib es so, dass ich es beim Kaffee lesen kann. Keine Logdatei,
sondern ein Bericht.

Und wenn du gar nicht weiterkommst: das ist auch ein Ergebnis. Schreib
auf, woran es lag, und hör auf. Ein ehrliches "ich bin hier hängen
geblieben und hier ist warum" ist mehr wert als 2.000 Zeilen Code, die
niemand nachvollziehen kann.

━━━━━━━━━━━━━━━━━━━━━━━━━━ BIS HIER KOPIEREN ━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Warum der Prompt so gebaut ist

| Abschnitt | Grund |
|---|---|
| **Suchen statt Pfad angeben** | Ich kenne JBs Ordnerstruktur nicht. Ein geratener Pfad wäre schlimmer als eine Suchanweisung — und die Prüfung *„liegt da wirklich das drin, was draufsteht"* verhindert den häufigsten Fehler bei automatischer Suche |
| **Lesen vor Code, vollständig** | Das ist der ganze Sinn von drei Tagen Pflichtenheft. Eine KI, die nach dem Überfliegen anfängt, baut das Falsche schnell |
| **Neun Regeln statt 183** | 183 Entscheidungen liest man nicht als Checkliste mit. Die neun hier sind die, bei deren Verletzung man **neu anfangen** muss |
| **Baustein 1–3 als Nachtziel** | Realistisch, und sie brauchen **keine** der drei offenen Oberflächen-Lücken. Die KI kann die ganze Nacht arbeiten, ohne an ein Loch zu stoßen |
| **„Grün" ist definiert** | Sonst nennt jede KI ihren Code fertig, sobald er läuft. Die vier Eigenschaften stehen schon in §12.6 |
| **Feststecken hat ein Verfahren** | Ohne das wartet sie entweder auf eine Antwort, die nachts nicht kommt, oder sie rät. Beides kostet die Nacht |
| **Das Protokoll ist der Deliverable** | Bei einem Nachtlauf ist der Bericht wichtiger als der Code — er entscheidet, ob der Code brauchbar ist |
