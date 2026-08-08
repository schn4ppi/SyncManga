# Was noch nicht übernommen wurde

> Begleitmaterial zu `VISION_SYNCFINDUS.md`.
> **JB-Frage 08.08.2026:** *„Was aus den Programmen, die mit diesem hier zusammenhängen, hast
> du nicht übernommen? Gib mir eine Liste an Funktionen, die nicht mitgenommen wurde."*
>
> **Methode:** beide Repos gelesen, nicht aus dem Gedächtnis beantwortet.
> `schn4ppi/SyncManga` (9.150 Zeilen, 18 Module) und `schn4ppi/SyncYouTube`
> (18.446 Zeilen, 11 Module, Stand `558d183`).

> ✅ **Stand 08.08.2026, abends: alle 18 sind entschieden.** JB: *„ok lass uns entscheiden."*
> Diese Datei hat damit ihren Zweck erfüllt und schrumpft von einer Fundliste zu einem
> **Nachweis**. Was offen bleibt, steht ganz unten — es ist eine einzige Zeile.

---

## 0. Das Ergebnis

**Von den großen Bausteinen fehlte genau einer: `filme.py`.** Der Rest waren
**Betriebsfunktionen** — Dinge, die kein Mensch als Feature beschreiben würde, die aber
darüber entscheiden, ob ein Programm im Alltag benutzbar ist. Genau die fallen beim Entwerfen
immer hinten runter, weil sie in keiner Vision vorkommen.

| | Anzahl | Wohin |
|---|---|---|
| **Zu Entscheidungen geworden** | **10** | E169–E178 |
| **Als „ja" eingeordnet, ohne eigene Nummer** | 10 | §16.6 |
| **Als „nein" abgelehnt, mit Begründung** | **4** | §16.6 |
| **Vertagt** | 1 | F09 |
| **Vorher schon bewusst ersetzt** | 7 | Abschnitt 4 |

---

## 1. Der große Fund: `filme.py` (878 Zeilen) → **E169, E170**

Im Pflichtenheft kam *Jellyfin* dreimal vor — jedes Mal als **Ziel** („kann unsere Dateien
lesen"). Dass SyncYouTube längst als **Klient** mit einem Jellyfin/Emby-Server spricht, stand
nirgends.

| Funktion | Wurde zu |
|---|---|
| `_anmelden`, `_zugang`, `katalog_abzug`, `katalog_lesen`, `sync_faellig` | **§4.7** — der Serverkatalog wird über einen Adapter **verschmolzen**, nicht danebengehängt (E11) |
| `detail`, `episoden`, `reihen` | deckt sich mit Werk / Gruppe / Einheit (E03) |
| `merkliste_lesen`, `merkliste_toggle` | **die Merkliste ist eine Sammlung** (§4.3), keine neue Sorte Ding |
| `stream_url` | **E169** — ein Werk kann fern liegen; lokal *und* fern sind zwei Ausgaben |
| `fortschritt`, `_fortschritt_senden`, `fortschritt_nachreichen`, `_queue_lesen` | **E170** — Fortschritt fließt in beide Richtungen, mit Nachreich-Schlange **und der Konfliktregel: die weitere Position gewinnt, nicht der neuere Zeitstempel** |
| `seerr_suche`, `seerr_anfragen`, `seerr_meine` | **ein Kandidat im Rennen** (E149), kein Sonderweg |
| `mehr_wie` | zweite Empfehlungsquelle neben §11 |
| `snippet_backen`, `snippet_lesen`, `bild_holen` | Bildzwischenspeicher — wird nicht neu erfunden |
| `_omdb_erlaubt` | ein Glied für die Bewegtbild-Kette (§7.4) |
| `live_tv.py`: `m3u_parsen`, `kanaele`, `programm` | **§4.7** — ein Sender ist ein **Ort ohne Vorrat**. E44 hatte Live-TV längst zugelassen |

---

## 2. Die zehn, die zu Regeln wurden

| Fund | Wurde |
|---|---|
| `_in_papierkorb`, `_datei_loeschen` | **E168** — Löschen geht in den Papierkorb, nie endgültig, auch nicht auf Wunsch |
| `stream_url`, `katalog_abzug`, Merkliste | **E169** — ein Medienserver ist ein Ort, keine Quelle |
| `_fortschritt_senden`, `fortschritt_nachreichen` | **E170** — Fortschritt fließt in beide Richtungen |
| `single_instance`, `_is_own_process`, `_kill_if_ours` | **E171** — eine Registerdatei, ein Programm. Nach E151 Pflicht, nicht Komfort |
| `update.py` (419 Z.) | **E172** — prüfen vor dem Tausch, `.bak`, atomar, nie löschen |
| `queue_heilen`, `pfade_heilen`, `_abo_heilen`, `dubletten_heilen`, `_dubletten_score`, `untertitel_aufraeumen`, `_vtt_verwaist`, `wiedergabe_sub_altlast_raeumen` | **E173** — Heilen ist die zweite Hälfte des Bruchtests: jeder Fund kennt seinen Vorschlag und führt ihn **nie selbst aus** |
| `ordner_importieren`, `downloads_einsortieren`, `_auto_import_anstossen` | **E174** — der Wachordner nimmt an, er räumt nicht auf |
| `tray.py` (619 Z.): `emblem_bild`, `punkt_farbe`, `draw_update_badge`, `tooltip_text` | **E175** — das Programm zeigt sich im Infobereich. Es informiert, es ruft nicht (E164) |
| `nsfw_hide_both`, `_sexual`, `_gore` | **E176** — Inhaltsfilter für Erwachsene, **zwei getrennte Achsen**, nicht dasselbe wie E158 |
| `cfm`, `cfmSrc`, `cfmSrcOwn`, `rep` → `broken_links.json` → `_consume_broken` | **E177** — was der Mensch bestätigt, wiegt schwerer als was wir messen |
| `st_tip_reading/_backlog/_caught/_finished/_paused/_paused_long` | **E178** — sechs Lesezustände; „aufgeholt" ≠ „Rückstand", und „lange pausiert" ist eine Einladung, kein Vorwurf |

---

## 3. Die zehn Ja und vier Nein → §16.6 des Pflichtenhefts

**Ja, ohne eigene Nummer:** Abos mit Regeln · Zugangsprüfung vor dem Holen (ist E149) ·
nachträgliche Anreicherung (ist E151/4) · Erweiterungs-Nachschub · `huelle.py` ·
Statistik-Tafel (in E19) · Kapitelkorrektur von Hand (Postfach-Ausgang) · MAL-XML ·
Zufallspick 🎲 · Familie/Nachbarschaft (vertagt auf **F09**).

**Nein, mit Begründung:**

| Abgelehnt | Weil |
|---|---|
| **Selbstneustart bei Codeänderung** | Ein signiertes Programm, das seinen eigenen Quelltext beobachtet und sich austauscht, ist für jeden Virenscanner Schadsoftware — und macht die Signatur wertlos, für die wir Wochen aufwenden (E172, §12.1) |
| **Spaltenwahl** | Meistens die Ausrede dafür, die **Prioritätsleiter** nicht geschrieben zu haben (E39). Wir haben sie geschrieben. Wer etwas vermisst, hat einen Fehler in der Leiter gefunden — der gehört behoben, nicht umgangen |
| **Tonspurwahl beim externen Abspielen** | **E34**: nie ein zweites Fenster. Die Wahl selbst lebt in „Ton & Text" (E83) |
| **Cloud-Slot** `manga.j-bk.org` | Kein fremder Server für den eigenen Lesestand — ersetzt durch Gerätekopplung (§12). ✅ Die **Datensparsamkeit** (kein Konto, keine E-Mail, nur das Nötige) wird übernommen |

---

## 4. Vorher schon bewusst ersetzt

| Aus | Wird bei uns | Warum |
|---|---|---|
| **HTML-Liste als Anwendung** (`render.py`, 1.033 Z.) | **Export** (E14) | E151 — die Anzeige ist eine Sicht, kein Speicher |
| **`localStorage` + 💾-Knopf** | Register (SQLite) | E151 |
| **`CACHE_VER`-Volllauf** | Feldalter je Feld | E151/4 |
| **Reader-Link raten und bestätigen** (`readerlink.py`, 1.312 Z.) | wir holen die Kapitelliste selbst | ⚠️ **Trotzdem behalten** als Rückfall, wenn eine Seite keine Liste liefert |
| **Quellen-Ampel als Hauptanzeige** | Güteangabe an der Ausgabe | Eine tote Seite ist kein Drama mehr (E76, E149) |
| **`PAYWALL_SITES` als Sperrliste** | Güteangabe | MANGA Plus ist ein legaler Leseort mit Lücken |
| **Cloud-Slot** | Gerätekopplung | siehe oben |

---

## 5. Was noch offen ist

> **Eine Zeile:** `filme.py` ist **entschieden** (§4.7, E169/E170), aber **nicht gezeichnet**.
> Ein Werk, das gleichzeitig lokal und auf einem Server liegt, mit beidseitigem Fortschritt und
> geteilter Merkliste — das ist der letzte Entwurf, der noch etwas beweisen muss.

Alles andere aus dieser Liste ist im Pflichtenheft angekommen.

---

## 6. Warum es passiert ist — die Lehre

Ich habe **drei Tage lang entworfen, was das Programm sein soll**, und die Frage *„was kann das
alte schon?"* nur zweimal gestellt — beide Male habe ich nach **Architektur** gesucht, nicht
nach **Funktionen**.

> **Ein Nachfolger wird nicht daran gemessen, ob er die *Idee* des Vorgängers trifft, sondern
> ob er dessen **Alltag** kann.** Und der Alltag steht in den kleinen Funktionen: Papierkorb
> statt Löschen, Einzelinstanz, `.bak` vor dem Tausch, ein Farbpunkt im Infobereich. Nichts
> davon hätte in einer Vision gestanden — und jedes einzelne fehlt sofort, wenn es weg ist.

**Für die zweite KI:** Bevor du eine Zeile schreibst, lies **beide Vorgänger-Repos** und mach
dieselbe Liste noch einmal. Sie wird kürzer sein als diese — aber sie wird nicht leer sein.
