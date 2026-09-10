# Lehrbuch — was beim Bauen gelernt wurde

> Begleitmaterial zu `VISION_SYNCFINDUS.md`, aber **nicht projektgebunden**.
> Hier steht, was auch in einem anderen Projekt und in einem anderen Monat noch stimmt.
> Angelegt 08.08.2026.

**Aufnahmebedingung:** Jede Regel nennt ihren **Vorfall**. Einmal ist ein Vorfall, zweimal
ein Muster — Regeln entstehen erst beim Muster, außer der Vorfall war teuer, dann sofort.
Maßangaben sind **Richtungen**, keine heiligen Zahlen.

**Abgrenzung:** Die projektgebundenen Fassungen dieser Lehren stehen als E-Nummern im
Pflichtenheft. Hier steht die **verallgemeinerte Form** mit Verweis. Nichts wird doppelt
erzählt.

---

## L1 · Ein reparierter Fehler hat oft einen unreparierten Zwilling

**Vorfall.** Die untere Bedienleiste hatte gelernt, vor dem Seitenstreifen zu enden — die
obere nicht. Ich hatte den Fehler unten bemerkt, behoben und **nie nachgesehen, ob er oben
genauso steckt**. Der Nutzer fand ihn. *(→ E152)*

**Zweiter Vorfall, dasselbe Muster.** „Gestuftes Aufgeben" war als Breitenregel geschrieben.
Dass Raum auch senkrecht knapp wird, stand nirgends — bis Text oben und unten aus einem
zentrierten Kasten herauswuchs und unsichtbar wurde. *(→ E122 senkrecht)*

> **Regel.** Wer eine Regel für **eine** Kante, Achse oder Richtung schreibt, sucht **sofort**
> die gespiegelte Stelle. Oben/unten, links/rechts, breit/hoch, hin/zurück, lesen/schreiben.

**Grund.** Ein Fehler entsteht selten allein: er entsteht aus einer Annahme, und die Annahme
gilt meist für mehr als eine Stelle. Die Reparatur behebt das Symptom an der Stelle, an der
es auffiel — und lässt die Annahme stehen.

**Geltung:** immer. **Art:** Leitplanke. Kostet Sekunden, spart eine Fehlermeldung.

---

## L2 · Wenn du eine Konfliktregel brauchst, ist meistens das Modell zu grob

**Vorfall.** Ich hatte Fortschritt als **eine Zahl** modelliert („du bist bei Folge 8"). Zwei
Geräte hatten zwei Zahlen, also brauchte ich eine Regel, welche gewinnt — *„die weitere
Position schlägt den neueren Zeitstempel"*. Klang klug. JB zerlegte sie mit einem Satz:
*„Wenn ich Folge 12 nicht geguckt habe, bin ich bei Folge 3. Ich sehe den Konflikt nicht."*

Er hatte recht: Modelliert man Fortschritt als **Zustand je Einheit** (ungesehen ·
mittendrin · gesehen), **gibt es gar keinen Konflikt** — zwei Mengen vereinigen sich, sie
streiten nicht. Die Regel war nicht die Lösung des Problems, sondern **seine Folge**.
Schlimmer: dieselbe Regel hätte beim Nochmalsehen von Folge 3 zurück auf Folge 13 gezerrt.
*(→ E182)*

> **Regel.** Bevor du eine Vorrang-, Gewinner- oder Stichentscheid-Regel schreibst, prüfe, ob
> das Modell eine Auflösung zu grob ist. **Eine Tie-Break-Regel ist ein Geruch, kein Entwurf.**

**Grund.** Konflikte entstehen an Stellen, an denen zwei Wahrheiten in **einen** Wert
gequetscht werden. Feinere Auflösung macht sie oft nicht lösbar, sondern **unmöglich**.

**Erkennungszeichen:** Du schreibst „es gewinnt…", „im Zweifel…", „der neuere/größere/letzte
…". Halt an und sieh dir die Datenstruktur an.

**Geltung:** immer, besonders bei Abgleich zwischen Geräten, Zusammenführungen und
verteiltem Zustand. **Art:** Leitplanke.

---

## L3 · Bei einer Übernahme zweimal suchen: nach Architektur *und* nach Funktionen

**Vorfall.** Drei Tage lang wurde ein Pflichtenheft für den Nachfolger zweier Programme
geschrieben. Zweimal wurde in den Vorgängern nachgesehen — beide Male **nach Architektur**
(Modulschnitt, Datenmodell, Abhängigkeiten). Erst als JB fragte *„was hast du nicht
übernommen?"*, kam eine Datei mit **878 Zeilen** ans Licht, die eine vollständige
Medienserver-Anbindung enthielt: Katalog, Merkliste, beidseitiger Fortschritt,
Anfragen-System. Dazu **17 weitere übersehene Funktionen**. *(→ `NICHT_UEBERNOMMEN.md`)*

> **Regel.** Eine Übernahme braucht **zwei** Durchgänge mit verschiedenen Fragen:
> **„Wie ist es gebaut?"** und **„Was kann es?"** Der zweite geht über die Funktionsliste
> jedes Moduls, nicht über die Kopfkommentare.

**Grund.** Architektur beantwortet, wie man etwas nachbaut. Sie beantwortet **nicht**, was
ein Programm alles tut. Und der Alltag eines Programms steckt in den kleinen Funktionen —
Papierkorb statt Löschen, Einzelinstanz, `.bak` vor dem Tausch, ein Farbpunkt im
Infobereich. **Nichts davon steht je in einer Vision, und jedes einzelne fehlt sofort, wenn
es weg ist.**

**Nebenregel.** Eine Übernahmeliste, die nur aus **Ja** besteht, ist keine Liste, sondern ein
Umzug. Vier begründete **Nein** waren in dieser Sitzung der wertvollere Teil.

**Geltung:** jede Ablösung eines Vorgängersystems. **Art:** Leitplanke.

---

## L4 · Wiederlesen findet die Fehler nicht, die man beim Schreiben gemacht hat

**Vorfall.** Auf die Frage *„steht das Grundgerüst?"* wurde nicht geantwortet, sondern
gesucht — mit drei mechanischen Suchen. Sie fanden **drei Lücken auf einmal**, die vorher
durch mehrfaches Lesen nicht aufgefallen waren.

| Suche | Was sie findet |
|---|---|
| **Oft genannt, nie erklärt** | Zähle jeden Eigennamen. Steht einer ≥ 5-mal da und hat nie einen eigenen Abschnitt, ist er ein **leerer Raum, auf den Entscheidungen zeigen** |
| **Kommt gar nicht vor** | Suche Wörter, die in *jedem* Vorhaben dieser Art vorkommen müssen — *leer · kein Treffer · antwortet nicht · abgebrochen · Zeitüberschreitung* |
| **Handlung ohne Weg** | Spiele eine gewöhnliche Handlung durch und suche den Entwurf dazu. Findest du keinen, fehlt er |

> **Regel.** Prüfe ein eigenes Dokument **mechanisch**, nicht durch Lesen. Wer sein Dokument
> liest, liest, was er gemeint hat.

**Grund.** Beim Wiederlesen ergänzt der Kopf, was fehlt — er hat den Text ja geschrieben.
Eine Zählung kann das nicht.

**Geltung:** jedes Pflichtenheft, jede Spezifikation, jeder längere Entwurf.
**Art:** Faustregel, monatlich oder alle zehn neuen Entscheidungen.
**Betriebsanleitung:** `Doku/PFLEGE.md`, Prüfung 9.

---

## L5 · Eine geerbte Faustregel gilt erst, wenn sie auf die konkrete Anlage gerechnet wurde

**Vorfall.** Für die Datensicherung wurde die **3-2-1-Regel** übernommen: drei Kopien, zwei
Datenträger, eine außer Haus. Sauber begründet, seit Jahrzehnten Standard. JB fragte: *„Was
bringt eine Kopie auf dem NAS, wenn die Daten eh auf dem NAS sind?"* — **Gar nichts.** Die
Regel stammt aus Serverräumen; bei einem Menschen mit **einem** NAS heißt „zwei Datenträger"
nichts, solange beide im selben Gehäuse stecken. Aus drei Ringen wurden zwei. *(→ E166)*

> **Regel.** Jede übernommene Best Practice einmal **gegen die tatsächliche Anlage
> durchrechnen**, bevor sie im Entwurf steht. Frage: *Welche Annahme über die Umgebung steckt
> in dieser Regel — und stimmt sie hier?*

**Grund.** Etablierte Regeln sind Antworten auf eine Umgebung, die im Regelwortlaut nicht
mehr vorkommt. Sie klingen dadurch allgemeingültiger, als sie sind.

**Zugabe aus demselben Vorfall:** *RAID ist Verfügbarkeit, keine Sicherung.* Es überlebt den
Ausfall **einer Platte** — nicht Löschen, nicht Verschlüsselung, nicht Diebstahl.

**Geltung:** immer. **Art:** Leitplanke.

---

## L6 · Eine Übergabe ist erst vollständig, wenn der Empfänger jeden Verweis öffnen kann

**Vorfall.** Ein Übergabe-Prompt für eine zweite KI war fertig geschrieben, als auffiel: die
**22 Entwürfe**, auf die das Pflichtenheft dutzendfach verweist, lagen nur als **private
Links** (nur für JB zu öffnen) und in einem **flüchtigen Zwischenspeicher**, der mit der
Sitzung stirbt. Der Empfänger hätte kein einziges Bild gesehen. Beinahe-Unfall, im letzten
Moment behoben.

> **Regel.** Vor jeder Übergabe: nimm die Sicht des Empfängers ein und prüfe **jeden Verweis**
> — Datei, Link, Pfad, Werkzeug, Zugang. Was er nicht öffnen kann, existiert für ihn nicht.

**Grund.** Wer die Übergabe schreibt, sieht alles. Genau deshalb prüft er es nicht.

**Zusatzprüfung:** Was in der Übergabe steht, muss **den Kanal überleben**. Ein Chat endet,
ein Zwischenspeicher wird gelöscht, ein privater Link braucht ein Konto. **Dauerhaft ist nur,
was in der Ablage liegt, die der Empfänger ohnehin bekommt.**

**Geltung:** jede Übergabe an Mensch oder Maschine. **Art:** Leitplanke.

---

## L7 · Bei asymmetrischem Risiko entscheidet die Schadenshöhe, nicht die Wahrscheinlichkeit

**Vorfall.** Frage: sollen zwei Datendateien aus einem öffentlichen Repo verschwinden? JB
konnte es nicht einschätzen und delegierte. Die Abwägung war unentschieden, bis die
Asymmetrie sichtbar wurde: **Bleiben sie liegen und nichts passiert, gewinnt man null.
Bleiben sie liegen und es passiert etwas, ist das Repo weg — unumkehrbar.** *(→ E163)*

> **Regel.** Prüfe bei jeder Risikofrage zuerst, ob Gewinn und Verlust dieselbe Größenordnung
> haben. Sind sie **asymmetrisch und der Verlust unumkehrbar**, entscheidet die Schadenshöhe —
> und dann ist die Eintrittswahrscheinlichkeit fast gleichgültig.

**Nebenbefund aus demselben Fall:** Bei Repos reicht `git rm` nicht — die Historie behält
alles. Wer wirklich entfernen will, schreibt Historie um, und **das entwertet jede vorhandene
Kopie**. Ein Eingriff, der ausdrückliche Zustimmung braucht.

**Geltung:** immer. **Art:** Faustregel — es gibt Fälle, in denen die Wahrscheinlichkeit so
klein ist, dass sie doch entscheidet. Dann schreib dazu, warum.

---

## L8 · Höhen und Breiten werden gemessen, nie geraten

**Vorfall.** Eine Bedienleiste bekam den Abstand `bottom: 62px`. Beim nächsten Bauteil
stimmte er nicht mehr — mal ragte Inhalt darunter, mal klaffte eine Lücke. *(→ E121)*

> **Regel.** Jede Zahl, die die Größe eines **anderen** Elements beschreibt, wird zur
> Laufzeit gemessen und weitergereicht. Eine geratene Konstante ist ein Fehler mit
> Verzögerungszünder — sie stimmt genau so lange, bis jemand eine Beschriftung ändert.

**Grund.** Die Zahl ist nicht falsch, sie ist **abgeleitet**. Wer eine Ableitung als Konstante
schreibt, trennt sie von ihrer Quelle.

**Geltung:** Oberflächen; sinngemäß überall, wo eine Zahl aus einer anderen folgt.
**Art:** Leitplanke.

---

## L9 · Zeig Alternativen, die du ernst meinst

**Vorfall.** Zweimal wurden drei Entwürfe mit einer Empfehlung vorgelegt, und **zweimal
wurde die Empfehlung überstimmt** — beide Male mit einem Argument, das besser war als meines.
Bei der Warteschlange lautete es: *„Die wird eh überbewertet, es ist halt ein Progress."*
Damit war meine Begründung („man muss darin suchen können") hinfällig: Wenn man eine Tafel
**nur ansieht und nie durchsucht**, gewinnt die Anordnung, die auf einen Blick zeigt, wo es
klemmt.

> **Regel.** Leg mehrere echte Möglichkeiten vor, mit Empfehlung — aber **ohne
> Vogelscheuchen**. Der Auftraggeber soll dich mit **Wissen** überstimmen können, nicht nach
> Gefühl. Zeigst du nur deinen Favoriten, bekommst du deine eigene Meinung zurück.

**Grund.** Der Auftraggeber kennt die Nutzung, du kennst die Bauart. Die Entscheidung braucht
beides, und sie fällt nur dann informiert, wenn er sieht, was er wegwirft.

**Geltung:** jede Gestaltungsfrage mit mehr als einer tragfähigen Antwort.
**Art:** Faustregel.

---

## L10 · Sag nie „vollständig", ohne eine Suche, die das Gegenteil beweisen könnte

**Vorfall.** In einer einzigen Sitzung wurde zweimal „vollständig" behauptet und zweimal
widerlegt: einmal die Übernahme aus den Vorgängern (878 Zeilen übersehen, L3), einmal die
Fortschrittsregel (durch einen Satz des Auftraggebers zerlegt, L2). Beide Male fand es
jemand, der **aus einem neuen Winkel** fragte.

> **Regel.** „Fertig", „vollständig" und „steht" sind Behauptungen über etwas, das man nicht
> sehen kann — nämlich das eigene blinde Feld. Sie werden nur ausgesprochen **zusammen mit
> der Prüfung, die sie hätte widerlegen können** — und mit dem, was diese Prüfung nicht
> abdeckt.

**Grund.** Vollständigkeit ist keine Eigenschaft eines Dokuments, sondern eine Aussage über
den Prüfenden.

**Folge fürs Vorgehen.** Das ist das stärkste Argument fürs frühe Bauen: **eine Stunde Code
findet, was drei Tage Lesen nicht gefunden haben.** Wenn ein Entwurf und eine Umsetzung um
dieselbe Zeit konkurrieren, gewinnt ab einem gewissen Punkt die Umsetzung.

**Geltung:** immer. **Art:** Leitplanke.
