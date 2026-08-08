# Was noch nicht übernommen wurde

> Begleitmaterial zu `VISION_SYNCFINDUS.md`.
> **JB-Frage 08.08.2026:** *„Was aus den Programmen, die mit diesem hier zusammenhängen, hast
> du nicht übernommen? Gib mir eine Liste an Funktionen, die nicht mitgenommen wurde."*
>
> **Methode:** beide Repos gelesen, nicht aus dem Gedächtnis beantwortet.
> `schn4ppi/SyncManga` (9.150 Zeilen, 18 Module) und `schn4ppi/SyncYouTube`
> (18.446 Zeilen, 11 Module, Stand `558d183`). Jede Funktionsliste kommt aus dem Quelltext,
> jeder Abgleich aus einer Suche im Pflichtenheft.

---

## 0. Das Ergebnis in einem Satz

**Von den großen Bausteinen fehlt genau einer: `filme.py`.** Der Rest sind
**Betriebsfunktionen** — Dinge, die kein Mensch als Feature beschreiben würde, die aber
darüber entscheiden, ob ein Programm im Alltag benutzbar ist. Genau die fallen beim Entwerfen
immer hinten runter, weil sie in keiner Vision vorkommen.

| | Anzahl | |
|---|---|---|
| **Übersehen — gehört ins Pflichtenheft** | **18** | Abschnitt 1–3 |
| **Bewusst ersetzt** | 7 | Abschnitt 4 |
| **Bewusst weggelassen** | 4 | schon in `UEBERNAHME_AUS_SYNCYOUTUBE.md` §4 |

---

## 1. Der große Fund: `filme.py` (878 Zeilen)

⚠️ **Das ist die einzige echte Lücke von Bausteingröße.** Im Pflichtenheft kommt *Jellyfin*
dreimal vor — jedes Mal als **Ziel** („Jellyfin kann unsere Dateien lesen"). Dass SyncYouTube
längst als **Klient** mit einem Jellyfin/Emby-Server spricht, steht nirgends.

| Funktion | Was sie tut | Warum das zählt |
|---|---|---|
| `_anmelden`, `_zugang` | Anmeldung am Medienserver, Sitzung halten | Die ganze Zugangsschicht existiert schon |
| `katalog_abzug`, `katalog_lesen`, `sync_faellig` | Serverkatalog abziehen und lokal vorhalten | **Ein zweites Register** — muss mit unserem zusammengeführt werden, nicht daneben |
| `detail`, `episoden`, `reihen` | Werk, Folgen, Reihen vom Server | Deckt sich mit Werk/Gruppe/Einheit (E03) |
| `merkliste_lesen`, `merkliste_toggle` | **Merkliste**, beidseitig | Kommt im Pflichtenheft **null**-mal vor |
| `mehr_wie` | „Ähnliches" vom Server | Zweite Empfehlungsquelle neben §11 |
| `stream_url` | Abspieladresse holen | Ein Werk kann **fern** liegen, nicht nur lokal |
| `fortschritt`, `_fortschritt_senden` | Wiedergabestand **zurückmelden** | ⚠️ Wir haben nur die Richtung *hinein* beschrieben |
| `fortschritt_nachreichen`, `_queue_lesen` | Was offline nicht gesendet wurde, später nachreichen | **Das ist E156, zwei Jahre früher** — und es ist schon gebaut |
| `seerr_suche`, `seerr_anfragen`, `seerr_meine` | **Jellyseerr**: Inhalte anfragen, eigene Anfragen sehen | Ein fertiger Beschaffungsweg, der in §9 nicht auftaucht |
| `snippet_backen`, `snippet_lesen`, `bild_holen` | Vorschaubilder und Ausschnitte lokal backen | Bildzwischenspeicher, den wir neu erfinden würden |
| `_omdb_erlaubt` | OMDb als Zusatzquelle | Ein Glied für die Bewegtbild-Kette (§7.4) |

> 🔑 **Was daraus folgt.** Ein Medienserver ist bei uns **keine Quelle und kein Motor**,
> sondern ein **weiterer Ort, an dem Werke liegen** — mit eigener Identität, eigenem
> Fortschritt und eigener Merkliste. Das ist eine Entscheidung, die im Fundament fehlt, nicht
> in der Beschaffung. Sie gehört zu §4.6 („Ort ≠ Werk"), und dort steht sie bisher nur für
> Platten, nicht für Server.

**Dazu `live_tv.py` (61 Zeilen):** `m3u_parsen`, `kanaele`, `programm` (EPG). **E44 hat
Live-TV ausdrücklich zugelassen** — dass der Code dafür schon existiert, steht nirgends.

---

## 2. Übersehene Betriebsfunktionen — SyncYouTube

| Funktion | Modul | Was fehlt im Pflichtenheft |
|---|---|---|
| **Wachordner** — `ordner_importieren`, `downloads_einsortieren`, `_auto_import_anstossen`, `_einsortieren_hintergrund` | `youtube_app` | Null Treffer. Ein Ordner, in den man etwas legt und es **erscheint**, ist die bequemste Art, eine Bibliothek zu füllen — und die einzige, die ohne Bedienung auskommt |
| **Selbstneustart bei Codeänderung im Leerlauf** — `_quell_signatur`, `_code_leerlauf`, `_neustart_pruefen`, `_selbst_neustart` | `youtube_app` | Das Programm merkt, dass sein eigener Quelltext sich geändert hat, wartet auf Leerlauf und startet sich neu. **Klug und nirgends beschrieben** |
| **Löschen geht in den Papierkorb** — `_in_papierkorb`, `_datei_loeschen` | `youtube_app` | Die zwei Treffer im Pflichtenheft meinen *Endzustände*, nicht die **Sicherheitsregel**. Sie fehlt als Regel → jetzt **E168** |
| **Heilungsfamilie** — `queue_heilen`, `pfade_heilen`, `_abo_heilen`, `dubletten_heilen`, `_dubletten_score`, `untertitel_aufraeumen`, `_vtt_verwaist`, `wiedergabe_sub_altlast_raeumen` | `youtube_app` | §12.6 kennt den **Bruchtest** (finden). Diese acht sind das **Reparieren** — mit Bewertungsfunktion für Dubletten. „Was tun wir mit dem Fund" ist nur für das Postfach beantwortet |
| **Nachträgliche Anreicherung** — `metadaten_backfill`, `technik_backfill`, `biblio_enrich_alle`, `_hat_metadaten` | `youtube_app` | E151/4 sagt „jedes Feld trägt eigenes Alter". Der **Nachziehlauf**, der alte Einträge einholt, ist damit gemeint, aber nie geschrieben |
| **Abos mit Regeln** — `_abo_feed_url`, `_abo_rss_ids`, `_abo_regel_ok`, `_abo_playlist_zuordnen`, `abo_folgen`, `abo_erneuern`, `abo_aufraeumen`, `_abo_baseline` | `youtube_app` | §5.11.1 nennt „Abos mit Regeln" in **einer Zeile**. Acht Funktionen mit Grundlinie (was zählt als „neu"), Regelfilter und Aufräumen stehen dahinter |
| **Zugangsprüfung vor dem Holen** — `_zugang_ok`, `geo_test_lauf`, `_geo_download` | `youtube_app` | E149 sagt „Vorprüfung kostet keine Bytes" — **das ist der fertige Code dafür** und wird nicht als Vorlage genannt |
| **Erweiterungs-Nachschub** — `addon_nachschub`, `addon_hab_liste`, `addon_hab`, `addon_update_info`, `_addon_xpi_pfad` | `youtube_app` | §8.4 beschreibt die Erweiterung, nicht **wie sie zum Nutzer kommt und sich erneuert** |
| **Tonspurwahl beim externen Abspielen** — `_ton_spur_waehlen`, `extern_abspielen` | `youtube_app` | E34 sagt „nie zwei Fenster". Trotzdem gibt es den Fall *„öffne das in VLC"* — er ist nicht entschieden |
| **Familie / Nachbarschaft** — `familie.py` (193 Z.): `familie`, `nachbar`, `status_schreiben/lesen` | `familie` | §12 hat Profile und Kopplung. Der **Austausch zwischen Haushalten** — wer hat was, wer sieht gerade was — fehlt. F09 (LANoMAT) berührt es, beantwortet es nicht |
| **`huelle.py` (216 Z.)** | `huelle` | Die Programmhülle selbst — Fenster, Start, Beenden. F01 ist beantwortet (§12.4), aber der **vorhandene Code** wird nicht als Ausgangspunkt genannt |

---

## 3. Übersehene Betriebsfunktionen — SyncManga

| Funktion | Modul | Was fehlt im Pflichtenheft |
|---|---|---|
| **Tray-Symbol mit Zustandsemblem** — `emblem_bild`, `punkt_farbe`, `draw_update_badge`, `tooltip_text`, `menu_labels` | `tray.py` (619 Z.) | **Null Treffer.** Farbpunkt nach Zahl toter Quellen, Betriebsanzeige, Aktualisierungsabzeichen, Kurzhinweis mit Namen. So weiß man, dass das Programm lebt, **ohne es zu öffnen** |
| **Einzelinstanz-Sperre** — `single_instance`, `_is_own_process`, `_kill_if_ours` | `tray.py` | **Null Treffer** — und nach **E151** gefährlicher als vorher: zwei Kopien auf **einer** Registerdatei ist genau der Fall, den man nie sehen will |
| **Selbst-Aktualisierung** — `update.py` (419 Z.) | `update.py` | Nichts löschen · vor jedem Tausch ein `.bak` · **heruntergeladene Daten vor dem Tausch prüfen** (ungültig → alte Datei bleibt) · atomar schreiben. **Vier erkaufte Regeln**, keine davon im Pflichtenheft |
| **Statistik-Tafel** — 9 Auswertungen (`stats_chapters`, `_country`, `_cover`, `_rating`, `_status`, `_top`, `_type`, `_adult`, `_count`) | `render.py` | Kommt einmal vor — als **Bedürfnis einer Persona**, nicht als Ansicht |
| **Inhaltsfilter** — `nsfw_hide_both`, `_sexual`, `_gore` | `render.py` | **Null Treffer.** E158 regelt das **Kinderprofil**; das hier ist etwas anderes: ein Erwachsener, der Gewaltdarstellung ausblenden will, ohne ein Kind zu sein |
| **Kapitelkorrektur von Hand** — `chapfix`, `chapfix_prompt` | `render.py` | §8 hat den **automatischen** Versatz (≥ 80 %). Was passiert, wenn keiner passt und der Mensch die Zahl selbst setzt, fehlt |
| **Rückmeldeschleife** — `cfm`, `cfmSrc`, `cfmSrcOwn` (Quelle bestätigen) und `rep` (defekt melden) → `broken_links.json` → `_consume_broken` | `render.py`, `enrich.py:687` | Der Nutzer **bestätigt oder verwirft** einen Quell-Link, und das fließt in die Gesundheitsbewertung zurück. Ein geschlossener Kreis, der nirgends steht |
| **Spaltenwahl** — `cols_menu` | `render.py` | Welche Spalten sichtbar sind. E39 hat die Prioritätsleiter für **Breiten**, nicht für **Vorlieben** |
| **Zufallspick** — `luckyPick` 🎲 | `render.py` | §11 hat den **Joker** in den Empfehlungen. Der schlichte Würfel („zeig mir irgendwas aus meinem Regal") ist etwas anderes und fehlt |
| **MAL-XML hinein und hinaus** — `exportMal`, `importMal` | `render.py` | E14 nennt Export ein Grundrecht. Das **XML-Format von MyAnimeList** ist der De-facto-Austauschstandard und wird nicht benannt |
| **Wortmarken-Zustände** — `st_tip_backlog`, `_caught`, `_finished`, `_paused`, `_paused_long`, `_reading` | `i18n.py` | Sechs unterschiedene Lesezustände inklusive *„lange pausiert"*. Wir haben drei |

---

## 4. Bewusst ersetzt — kein Verlust, aber es gehört benannt

| Aus | Wird bei uns | Warum |
|---|---|---|
| **Die HTML-Liste als Anwendung** (`render.py`, 1.033 Z.) | **Export** (E14), nicht Anwendung | E151 — die Anzeige ist eine Sicht, kein Speicher |
| **`localStorage` + 💾-Knopf** | Register (SQLite) | E151 |
| **`CACHE_VER`-Volllauf** | Feldalter je Feld | E151/4 |
| **Reader-Link raten und bestätigen** (`readerlink.py`, 1.312 Z.) | Wir holen die Kapitelliste selbst | ⚠️ **Trotzdem behalten** — als Rückfall, wenn eine Seite keine Liste liefert. Die Idee ist zu gut zum Wegwerfen |
| **Quellen-Ampel als Hauptanzeige** | Güteangabe an der Ausgabe | Eine tote Seite ist kein Drama mehr (E76, E149) |
| **`PAYWALL_SITES` als Sperrliste** | Güteangabe | MANGA Plus ist ein legaler Leseort mit Lücken, kein toter Reader |
| **Cloud-Slot** `manga.j-bk.org` (`cloud.py`, 175 Z.) | Direkte Gerätekopplung (§12) | Kein fremder Server für den eigenen Lesestand — aber die **Datensparsamkeit** der alten Lösung (kein Konto, keine E-Mail, nur die fertige Liste) ist vorbildlich und wird übernommen |

---

## 5. Was zu tun ist

1. **`filme.py` bekommt einen eigenen Abschnitt im Fundament** — „Ein Werk kann fern liegen"
   (§4.6), mit Merkliste, Fortschritt-Rückmeldung und Jellyseerr als Beschaffungsweg.
2. **Die 18 Betriebsfunktionen** aus Abschnitt 2 und 3 werden zu E-Nummern oder zu Zeilen in
   `UEBERNAHME_AUS_SYNCYOUTUBE.md` — keine davon braucht einen Entwurf, alle brauchen eine
   Entscheidung.
3. **Diese Datei wird abgearbeitet und schrumpft.** Was erledigt ist, verschwindet hier und
   steht dort. *Wenn diese Datei leer ist, ist die Übernahme vollständig.*

---

## 6. Warum das passiert ist — die ehrliche Antwort

Ich habe **drei Tage lang entworfen, was das Programm sein soll**, und dabei die Frage
*„was kann das alte schon?"* nur zweimal gestellt: einmal für SyncYouTubes Oberfläche
(§5.11.1) und einmal für SyncMangas Architektur (§16.5). **Beide Male habe ich nach
Architektur gesucht, nicht nach Funktionen.**

> **Die Lehre, die bleibt:** Ein Nachfolger wird nicht daran gemessen, ob er die *Idee* des
> Vorgängers trifft, sondern ob er dessen **Alltag** kann. Und der Alltag steht in den kleinen
> Funktionen: Papierkorb statt Löschen, Einzelinstanz, `.bak` vor dem Tausch, ein Farbpunkt im
> Infobereich. **Nichts davon hätte in einer Vision gestanden — und jedes einzelne fehlt
> sofort, wenn es weg ist.**
