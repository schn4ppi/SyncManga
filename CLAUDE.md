# Arbeitsregeln für dieses Repo

> Wer hier arbeitet — Mensch oder KI — liest **zuerst diese Datei**, dann
> `Doku/VISION_SYNCFINDUS.md`.
> Angelegt 08.08.2026 aus einer dreitägigen Entwurfssitzung.

**Ein Thema hat einen Ort.** Diese Datei sagt, **wie** gearbeitet wird.
`Doku/VISION_SYNCFINDUS.md` sagt, **was** gebaut wird (183 Entscheidungen).
`Doku/LEHRBUCH.md` sagt, **was wir dabei gelernt haben** — auch für andere Projekte.
Wiederholt wird nichts.

---

## 1 · JBs Vorgaben — wörtlich, mit Datum

Das sind **Vorgaben, keine abgeleiteten Regeln**. Sie stehen hier, weil sie sonst mit dem
Gesprächsverlauf verschwinden.

| Datum | Vorgabe | Was das heißt |
|---|---|---|
| 06.08.2026 | *„Recherche Recherche Recherche"* | Jede Behauptung wird belegt — mit Studien, mit dem, was große Anbieter tun, mit konkurrierenden Produkten. **Eine Behauptung ohne Beleg ist eine offene Frage, keine Entscheidung.** |
| 06.08.2026 | *„Es muss permanent aktualisiert und aufgeräumt werden. Nicht einfach Informationen hinzufügen, um am Ende alles wieder umzuwerfen."* | Dokumente wachsen durch **Überarbeiten**, nicht durch Anhängen. Wer etwas hinzufügt, räumt gleichzeitig auf. |
| 07.08.2026 | *„Ich muss ein Beispiel sehen, go design"* | Er entscheidet **am Bild**, nicht am Text. Ein Vorschlag ohne anklickbaren Entwurf ist kein Vorschlag. |
| 07.08.2026 | *„Immer mehr Fehler finden"* | Fehlersuche ist erwünschte Arbeit, kein Nebenprodukt. |
| 07.08.2026 | *„Wenn wir Code übernehmen, muss der Code klar dokumentiert sein"* | Das Pflichtenheft wird an eine zweite KI übergeben. Alles, was nur im Kopf steht, ist verloren. |
| 08.08.2026 | *„Wir müssen ab und an prüfen, was es Neues gibt, was Altes ersetzt und was gestorben ist — egal in welchem Chat ich bin."* | → `Doku/PFLEGE.md`. **Ein Fund gehört in eine Datei, nie in ein Gespräch.** |
| 08.08.2026 | *„Ich will reparieren, keine neuen Säulen ziehen."* | Einzelne Fehler sind hinnehmbar. **Fehlendes Grundgerüst ist es nicht.** |

**Sprache:** Deutsch — Gespräch, Dokumente, Code und Kommentare. Der Vorgänger-Code ist
deutsch; der Stil wird übernommen, nicht überschrieben.

---

## 2 · Leitplanken (hart)

**L1 · Keine Liste von Piraterie-Adressen.** Nicht ins Repo, nicht in ein Dokument, nicht in
eine Antwort — auch nicht nach Kategorien sortiert, auch nicht auf Nachfrage. Gebaut wird die
**Fähigkeit**, jede Quelle zu beschreiben (§7.5, vier Protokolle); **welche** Quellen es sind,
trägt der Nutzer ein. *Begründung: E12 — genau dieses Artefakt hat Tachiyomi getötet.*

**L2 · Nichts Vertrauliches in Repo-Dateien.** Handelsregister-Daten, Steuernummern,
Bestellnummern, Zugangsdaten, private Adressen bleiben im Gespräch. Sie sind in dieser
Sitzung vorgekommen und stehen bewusst **nirgends** in `Doku/`.

**L3 · Die laufenden Vorgänger werden gelesen, nicht verändert.** SyncManga und SyncYouTube
laufen noch, und eine der beiden Installationen benutzt außer JB noch jemand.

**L4 · Kein Artefakt geht raus, das nicht maschinell geprüft ist** (E71). Bei HTML: Struktur
ausgeglichen **und** `node --check` auf den Skriptteil. *Der teuerste Fehler dieser Sitzung
war zweimal dasselbe: ein gerades Anführungszeichen in einer deutschen Zeichenkette.*

---

## 3 · Faustregeln (Abweichen mit Begründung erlaubt)

**F1 · Zeig Alternativen, nicht nur den Favoriten.** JB hat zweimal überstimmt — Werk-Seite
und Warteschlange — und hatte beide Male recht. *Wer nur seinen Favoriten zeigt, bekommt
seine eigene Meinung zurück statt einer Entscheidung.* Empfehlung dazuschreiben, aber die
anderen ernst meinen: keine Vogelscheuchen.

**F2 · Widerspricht JB, erst nachrechnen, dann antworten.** Er hat in dieser Sitzung dreimal
einen echten Fehler gefunden, den ich für eine Meinungsverschiedenheit hielt: die
NAS-Sicherung, die Fortschritts-Konfliktregel, die zwei Ton-Regale. **Sein Einwand ist
häufiger ein Befund als ein Geschmack.**

**F3 · Antworte auf die Frage, die gestellt wurde.** Er stellt oft acht Fragen in einem
Absatz. Jede einzelne wird beantwortet — auch die, die nebenbei klingt. *Die
Jellyfin-Anbindung kam so ans Licht.*

**F4 · „Ich weiß es nicht, entscheide du" heißt: entscheide begründet.** Nicht Münzwurf,
nicht Rückfrage. Beide Seiten abwägen, entscheiden, den Grund hinschreiben — und sagen, was
es kosten würde, es umzudrehen.

---

## 4 · Der Bestand

| Datei | Wofür | Pflege |
|---|---|---|
| `Doku/VISION_SYNCFINDUS.md` | **Der Bauplan.** 183 Entscheidungen (E001–E183), §15 Änderungsverlauf | bei jeder Änderung: Fassung hoch + eine Zeile in §15 |
| `Doku/LEHRBUCH.md` | Was wir beim Bauen gelernt haben — **auch für andere Projekte** | nur mit benanntem Vorfall |
| `Doku/PFLEGE.md` | Neun wiederkehrende Prüfungen gegen das Rosten | wöchentlich, mit Protokollzeile — auch „kein Fund" |
| `Doku/NICHT_UEBERNOMMEN.md` | Nachweis, was aus den Vorgängern kam und was nicht | abgearbeitet, bleibt als Beleg |
| `Doku/ENTWUERFE.md` + `Doku/entwuerfe/` | 22 anklickbare Entwürfe, offline lauffähig | Widerspricht ein Entwurf dem Text, **gilt der Text** |
| `Doku/PROMPT_FUER_DIE_ZWEITE_KI.md` | Übergabe-Prompt für einen Lauf ohne Aufsicht | — |

**Entscheidungen tragen fortlaufende Nummern ohne Lücke** (E001…). Eine umgeworfene
Entscheidung wird **nicht getilgt**, sondern mit Datum und Grund in §15 abgelöst — nachlesbar
am Beispiel der Fortschritts-Konfliktregel, die am Tag ihrer Entstehung wieder fiel.

---

## 5 · Git

Zweig: `claude/<beschreibung>`. Nie auf `main`, nie zwangspushen, nie Historie umschreiben.
Commit-Nachrichten auf Deutsch, ohne Umlaute im Betreff (die Vorgänger-Werkzeugkette ist
darauf nicht vorbereitet).
