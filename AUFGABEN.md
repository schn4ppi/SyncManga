# SyncManga — Aufgabenliste

> **Herkunft:** Vergleich SyncManga ↔ SyncFindus vom 24.09.2026 (8 Bereiche, jeder Vorschlag von
> einem zweiten Agenten gegengeprüft). Die Zeilenangaben beziehen sich auf **Stand `8b74a8c`**
> (v0.4.4, vor PR „Befunde 24.09.2026“) und können sich inzwischen verschoben haben.

## ⚠️ Regel: Gegenprüfung vor jeder Umsetzung (Pflicht)

Jeder Eintrag hier ist eine **Behauptung**, kein Auftrag. Der Chat, der eine Aufgabe umsetzt, muss
sie **vorher selbst gegenprüfen** und das Ergebnis in die Zeile *Gegenprüfung* schreiben:

1. **Nachstellen:** den Befund im aktuellen Code reproduzieren, am besten als Test, der **vorher rot**
   ist. Gelingt das nicht, wird nichts umgesetzt.
2. **Belege prüfen:** Stimmen die Stellen noch, und sagen sie das, was behauptet wird?
3. **Bewusste Entscheidungen respektieren:** Steht ein Kommentar mit „JB“ und Datum dagegen, oder eine
   E-Nummer aus der SyncFindus-Planung? Dann nicht umsetzen, sondern JB fragen.
4. **Eintragen:** `Gegenprüfung: bestätigt | abgeschwächt (wie) | widerlegt (warum) — Datum, Chat`.
   Bei *widerlegt* bleibt der Eintrag mit Begründung stehen, damit er nicht wieder auftaucht.
5. **Erst dann umsetzen.** Danach muss derselbe Test grün sein. Erledigtes wandert nach unten.

Markierungen: 🔒 = braucht vorher JBs Freigabe · ⭐ = hoher Nutzen bei kleinem Aufwand.

---

## Offen

### A-01 ⭐ Adult-Filter für Reader wirkt nicht
- **Befund:** Den Typ 'adult' kann `verify_reader` nie bestätigen, weil es keine Testserien dafür gibt. Deshalb
  verschwinden Adult-Reader bei jeder Discovery. `import_keiyoushi` ignoriert `nsfw`. manga18/manhwa18-Hosts
  stehen deshalb als 'manga'/'manhwa' in der Liste, und `find_chapters` fragt sie für normale Serien ab.
- **Belege:** `readerlink.py:768, 1212-1215, 1231-1239`; `data/readers_pattern.json`;
  `tools/import_keiyoushi.py:116, 124`; `tools/reader_atlas.py:185`; Vergleich `git show fe218e6:data/readers_pattern.json`.
- **Vorschlag:** 'adult' mit den manga/manhwa-Testserien prüfen. `merge_readers` behält einen gesetzten Typ.
  `import_keiyoushi` übernimmt `ext.nsfw`. Dazu ein Test, dass `adult=False` nie einen nsfw-Host liefert.
- **Gegenprüfung:** _offen_

### A-02 ⭐ exe: Zustands-Wiederherstellung und Listen-Import lesen aus dem Bundle
- **Befund:** Die exe hält ihre Daten in `%LOCALAPPDATA%\SyncManga`. `render` liest `list_state.json` (SEED)
  und `scan` liest `imported_series.json` aber aus `syncmanga/../data`, in der exe also aus dem PyInstaller-Bundle.
  Die 💾-Wiederherstellung und der MAL/AniList-Import wirken dort deshalb nicht.
- **Belege:** `build/SyncManga.py:13-18`; `render.py:291, 981`; `scan.py:50`; `build/SyncManga.spec:18-37`;
  `anilist.py:144, 164`.
- **Vorschlag:** Beide Pfade aus `data_dir` ableiten und mit einem Test unter `sys.frozen` absichern.
  Das ist Voraussetzung für A-10.
- **Gegenprüfung:** _offen (Hinweis Gutachter: „wahrscheinlich“, nicht in einer echten exe nachgestellt)_

### A-03 ⭐ Fehler verschwinden im Fensterprogramm (kein Log, Browser-Ausfall still)
- **Befund:** Es gibt kein `logging`. Der Code hat viele `except Exception: pass`. Unter `pythonw`/`console=False`
  sind `stdout`/`stderr` None. `tray._do_update` schluckt Abstürze. Scheitert ein Browser (z. B. Chrome), fehlen
  dessen Serien, und niemand sieht den Grund.
- **Belege:** `tray.py:457-481`; `enrich.py:728-737`; `update.py:135-145`; `scan.py:574-579`; `build/SyncManga.spec:60`.
- **Vorschlag:** `RotatingFileHandler` im Datenordner und Tray-Hinweis „Lauf fehlgeschlagen – siehe Log“.
  Dazu je Browser `{browser, profil, gelesen/übersprungen, grund, anzahl}` im Stil von `source_health.json`.
- **Gegenprüfung:** _offen_

### A-04 ⭐ Konfidenz beschreibt nicht den gewählten Treffer
- **Befund:** `mb_search` meldet `best_sim` über **alle** Kandidaten. Tauscht `_stub_guard` auf einen beliebteren
  Kandidaten, bleibt die conf hoch (z. B. 'Kingdom Hearts' → 'Kingdom', gemeldet 1.0, echt 0.7). Das überspringt
  Zweit- und Drittmeinung.
- **Belege:** `catalog.py:268-301, 323-335, 437, 440-481`; `enrich.py:64, 104-112, 128`.
- **Vorschlag:** `score(best)` als conf zurückgeben, nach einem Tausch auf ≤ 0.61 deckeln. Vorher prüfen, ob die
  Query-Auswahl in `lookup` (`c > conf`) kippt. Optional ein leises `data-unsure` mit eigenem Filter;
  „Braucht Hilfe“ bleibt unverändert (JB-Regel).
- **Gegenprüfung:** _offen_

### A-05 ⭐ Suche findet lange, romanisierte und alternative Titel nicht
- **Befund:** `ap()` durchsucht nur `cells[0].textContent`, also den auf 40 Zeichen gekürzten Namen, den Autor
  und das Original. Voller Titel, Romaji und `alt_titles` fehlen, ebenso Akzent-Faltung ('Shumatsu' ≠ 'Shūmatsu').
- **Belege:** `templates/list.js:37`; `render.py:797-798, 898-903, 940`.
- **Vorschlag:** Einen versteckten Suchtext `data-q` aus vollem Titel, Romaji, alt_titles und Original bilden.
  Anfrage und `data-q` gleich falten (NFD, Akzente weg, × → x, Satzzeichen → Leerzeichen). Reine Anzeige.
- **Gegenprüfung:** _offen_

### A-06 Updater: Rest nach dem Setup-Fix
- **Befund:**
  - (b) Fehlt `.sha256` oder scheitert der Abruf, prüft der exe-Weg nur die Größe.
  - (d) `update_sources`, `check_program_version`, `raw_url` und `backup_and_write` haben keinen Aufrufer.
  - (c) `parse_version('0.4.4-rc1')` ergibt `(0,4,41)`.
  - (e) Es gibt keine Authenticode-Prüfung vor dem Tausch.
- **Belege:** `update.py:19-103, 234-254, 257-271`.
- **Vorschlag:** Für die exe den `digest` aus der API nehmen und bei Fehlen abbrechen (fail-closed).
  Toten Code löschen oder anschließen. Authenticode („JBK-Holding GmbH“) als eigene Runde.
- **Gegenprüfung:** _offen_

### A-07 Quellenausfälle während eines Laufs richten Dauerschaden an
- **Befund:**
  - (a) `cache[k] = nc` ersetzt den Eintrag komplett. Fällt AniList oder MU mitten im Lauf aus, gehen Titel,
    Übersetzungsstand und Empfehlungen verloren, bis ein neuer CACHE_VER-Lauf kommt.
  - (b) Wirft MangaBaka und liefert der Fallback etwas, geht `mb_erred` verloren, und `tries` steigt.
    MangaBaka ruft nie `_fehler_merken`, und `is_down` hat keinen Aufrufer.
- **Belege:** `enrich.py:568-577, 712-757, 1201-1361`; `catalog.py:432-433, 484-495`; `health.py:171-173, 212-216`.
- **Vorschlag:** Je Feld den alten Wert behalten, wenn die liefernde Quelle diesmal einen *Fehler* hatte
  (nicht bei „kein Treffer“). `lookup` liefert 'fallback-error' ohne `tries+1`.
- **Gegenprüfung:** _offen_

### A-08 Rückfallkette und Namens-Dedup ordnen still falsch zu
- **Befund:**
  - (a) `mu_rating`, `al_lookup` und `jikan_lookup` nehmen `max()` ohne Untergrenze ('March Comes in Like a Lion'
    → 'Red Lion'). Die falsche MU-ID zieht Übersetzungsstand und Autor nach.
  - (b) Der zweite Dedup-Durchlauf verschmilzt nach `norm(name)` auch Zeilen mit **verschiedenen** md_ids.
- **Belege:** `sources.py:725, 763-796, 900-924`; `catalog.py:360-401`; `enrich.py:1730-1757`;
  SyncFindus-Commit `a3841f1` (Detail-Titel als Match-Entscheider).
- **Vorschlag:** MU im Fallback nur ab ≥ 0.6 oder bei norm-gleichem associated-Titel. AniList und Jikan ab 0.6.
  Im Dedup überspringen, wenn beide md_ids gesetzt und verschieden sind (vorher am echten Cache zählen).
- **Gegenprüfung:** _offen_

### A-09 🆕-Zähler und 🆕-Filter zählen verschieden; Rundung bei Dezimalkapiteln
- **Befund:** Der Knopf zählt `latest > chap`, der Filter `data-un > 0`. Gemessen zeigt der Knopf 600,
  der Filter 450. `next_and_unread(10.5, 11)` ergibt 0 offene Kapitel (Python rundet zur geraden Zahl).
- **Belege:** `render.py:221-225, 249-257, 973-975`; `templates/list.js:45, 60, 72, 157`.
- **Vorschlag:** Eine gemeinsame Funktion `offene_kapitel = max(0, floor(lesbar) − floor(chap))` in Python und JS.
  Der Knopf zählt `data-un > 0`, `regray` schreibt die Zahl neu.
- **Gegenprüfung:** _offen_

### A-10 🔒 Serien verschwinden mit dem Browserverlauf (Gedächtnis für den Lesestand)
- **Befund:** Die items werden bei jedem Lauf nur aus Browsern und Importen gebaut. Kürzt Chrome den Verlauf
  (90 Tage), verschwindet eine Serie ohne Lesezeichen samt Lesestand.
- **Belege:** `scan.py:199-246, 566-600`; `enrich.py:1621-1629`.
- **Vorschlag:** Nach jedem Lauf `data/lesestand.json` atomar schreiben und beim nächsten Scan wie
  `imported_items()` einmischen. **Braucht JBs Freigabe** (zweite Person nutzt SyncManga), setzt A-02 voraus.
- **Gegenprüfung:** _offen_

### A-11 Service-Worker legt alle 5 s einen neuen Cache-Eintrag an
- **Befund:** `sw.js` cached jede GET-Antwort unter der vollen URL. `pollSync` lädt alle 5 s `…?_=<ts>`,
  hochgerechnet etwa 17.000 Einträge am Tag bei offener Liste.
- **Belege:** `sw.js:6-23`; `templates/list.js:362, 376, 473`.
- **Vorschlag:** `?_=` und `/data/` nicht cachen, nur same-origin, Cache-Name auf v3.
- **Gegenprüfung:** _offen_

### A-12 Cloud-Upload hält „keine Browser-Daten“ nicht; `info_html` escapt nicht
- **Befund:** Hochgeladen wird die komplette HTML-Datei: eigene Verlaufs-URLs als Weiterlesen, `data-ts`,
  pausierte Hosts, im Quellbaum auch der SEED. `info_html` setzt `code`/`url` vom Server ungeprüft ein.
- **Belege:** `cloud.py:6-8, 24-41, 80-104, 140-175`; `render.py:533-583, 948, 979-1004`.
- **Vorschlag:** Den Text sofort ehrlich machen. Danach `render(cloud=True)` ohne SEED, `data-ts` auf Tage
  runden, `html.escape` in `info_html`, und prüfen, dass `url` mit BASE beginnt.
- **Gegenprüfung:** _offen_

### A-13 Oberfläche verspricht Server und Funktionen, die es im Repo nicht gibt
- **Befund:**
  - `list.js` POSTet an `127.0.0.1:8765` (`/chapfix`, `/broken`, `/confirm-source`), im Repo gibt es keinen
    Handler. `chapfix.py`, `aufloeser.py` und `lernen.py` sind nicht versioniert.
  - Die apply-Werkzeuge sind nicht in `run()` verdrahtet und schreiben ins Paket statt in den Datenordner.
  - Der Klick-Auflöser leitet auf **jedem** localhost-Port nach `/lesen` um (`tools/serve.py` → 404).
  - Die Liste verspricht einen AniList-Auto-Sync (`anilist_verbinden.bat` fehlt).
- **Belege:** `templates/list.js:16, 136-139, 152, 482-513, 570-600`; `__main__.py:103-130`; `tools/serve.py:24`;
  `i18n.py:124, 150, 381`; `anilist.py:50-61, 117, 144-160`.
- **Vorschlag:** Die Bestätigungsdateien in `run()` aus dem Datenordner einsammeln. Die Umleitung nur bei
  Port 8765. Versprechen entfernen oder als „in Vorbereitung“ kennzeichnen. `.gitignore` um
  `link_health.*`, `*_confirms.json`, `chap_fixes.json` und `vertrauen.json` ergänzen.
- **Gegenprüfung:** _offen_

### A-14 Status nach manuellem Lesestand neu bestimmen
- **Befund:** Seit diesem PR wirkt chapFix nur noch, bis der Scan es überholt, und `data-kap` folgt. `cfSet`
  aktualisiert aber weiterhin weder `data-s`, `data-pc` noch `data-mst`. Die Zeile bleibt z. B. „Pausiert“.
- **Belege:** `templates/list.js` (`cfSet`); `render.py:168-187` (`user_progress`).
- **Vorschlag:** Die Status-Tabelle aus `user_progress` als kleine JS-Funktion spiegeln. Dafür `data-lat`,
  `data-lv` und `data-pub` mitschreiben und die Tabelle in Python und JS mit denselben Fällen testen.
- **Gegenprüfung:** _offen_

### A-15 🔒 `/manhwa/`-Pfade als Slug erkennen (Schlüssel-Migration nötig)
- **Befund:** `slug_from_url` kennt `/manhwa/` und `/manhua/` nicht. In diesem PR bewusst **nicht** geändert:
  Das Einschalten ändert bei Readern mit diesem Pfad den Cache-Schlüssel bestehender Serien (Neuanreicherung,
  Overrides unter altem Schlüssel).
- **Belege:** `parse.py:67`; Korpusvergleich 24.09.2026 (864 URLs mit anderem Slug).
- **Vorschlag:** Nur zusammen mit einer Alias-Übernahme alter Schlüssel (MIG, overrides). JB entscheidet.
- **Gegenprüfung:** _offen_

### A-16 Browser-DB-Kopie: `immutable` ignoriert den WAL; Kopien bleiben liegen
- **Befund:** `copy_locked` kopiert `-wal`/`-shm` mit, öffnet aber `immutable=1`. Die jüngsten Besuche fehlen
  bis zum Checkpoint. Kopien des **ganzen** Verlaufs bleiben in %TEMP% liegen (Datenschutz-Versprechen).
- **Belege:** `scan.py:10-11, 83-111, 300-307, 321-328, 386-395, 549-561`.
- **Vorschlag:** Je Scan ein `TemporaryDirectory`, `mode=ro`, Aufräumen im `finally`. Test mit synthetischer
  WAL-Datenbank. Die dokumentierte Begründung (`scan.py:95-96`) vorher mit JB klären.
- **Gegenprüfung:** _offen_

### A-17 Tests ins Repo und vor dem Release laufen lassen
- **Befund:** Bis zu diesem PR gab es keine Tests im Repo. `winget.yml` veröffentlicht ohne Testlauf.
- **Vorschlag:** Die lokale Suite (Gate) übernehmen, soweit sie keine privaten Daten enthält. Ein pytest-Job
  (windows + ubuntu, Python ≥ 3.12) als `needs` vor dem Release-Job. Golden-Fälle aus `overrides.json`
  (119 Pins als „Suchbegriff → erwartete MangaBaka-ID“).
- **Gegenprüfung:** _offen_

### A-18 Handkorrekturen mit Herkunft speichern
- **Befund:** In `overrides.json` haben Handeinträge, bestätigte Pins und Auto-Pins dieselbe Form. Es gibt
  6 IDs mit widersprüchlichen Namen, 27 Keys mit Rausch-Endung und einen toten Eintrag 'weebcentral'.
  In `series_overrides.json` trägt `trust` zwei Bedeutungen.
- **Belege:** `data/overrides.json`; `tools/apply_confirms.py:59`; `tools/audit_duplicates.py:90-93`.
- **Vorschlag:** Jeder Schreiber setzt `_herkunft` (hand/bestätigt/auto/import) und `_datum`. Dazu ein Lint in
  `audit_duplicates`. Den Eintrag 'weebcentral' prüfen: Mit dem Parser-Fix entsteht der Schlüssel nicht mehr neu.
- **Gegenprüfung:** _offen_

### A-19 Lieferkette und Build
- **Befund:**
  - Die Fremd-Action `winget-releaser@v2` hängt an einem verschiebbaren Tag, und das PAT hat den Scope
    `public_repo`.
  - `build.bat` erwartet das Monorepo, und die `.iss` fehlt.
  - `tools/serve.py` liefert per `0.0.0.0` ein Verzeichnis-Listing aus, einschließlich `data/`.
- **Belege:** `.github/workflows/winget.yml:2-22`; `build/build.bat:6-8`; `build/SyncManga.spec:12, 21-37`;
  `tools/serve.py:23, 39-44`.
- **Vorschlag:** Die Action auf einen SHA pinnen, ein fine-grained PAT, Immutable Releases. In `serve.py`
  nur eine Whitelist ausliefern.
- **Gegenprüfung:** _offen_

### A-20 Kleinere Punkte (je einzeln gegenprüfen)
- **Barrierefreiheit:**
  - Es gibt 0 aria/role-Attribute, und Sortierköpfe und Chips sind nicht fokussierbar.
  - Der Kontrast im hellen Modus liegt bei 2,3–3,4:1 (`render.py:131-133, 585, 597-599`; `list.css:139, 321-341`).
- **`single_instance`** kann fremde Python-Prozesse beenden (`tray.py:152-197`). Besser ein benannter Mutex.
- **Status 'Fertig'** (Lesezeichen-Ordner „manga complete“, MAL „Completed“) geht verloren
  (`scan.py:67-69, 512, 536-537`; `render.py:168-187`).
- **Lesezeichen** werden nur mit JBs Ordnernamen erkannt (`scan.py:67-78, 281-289`).
- **MangaFire-API-Stufe** kann nie bestätigen, weil sie ≥ 15.000 Zeichen erwartet und nur eine 3-KB-Hülle
  bekommt (`sources.py:30, 178, 200`).
- **`linkhealth.is_hard_404`** vergleicht Teilstrings: „mangak“ trifft auch mangakatana/mangakakalot
  (`linkhealth.py:55-58`).
- **overrides-Schreiber** schreiben teils ohne tmp-Datei; `load_overrides` verschluckt eine defekte Datei
  (`apply_confirms.py:39, 63`; `audit_duplicates.py:98`; `config.py:185-186`).
- **`render.py` erst ab Python 3.12** importierbar (verschachtelte f-Strings). Das in der README nennen oder umbauen.
- **Filter:** Aktive Filter sind am Knopf nicht sichtbar, und „lange pausiert“ ist nur Farbe, nicht filterbar
  (`render.py:131, 816-819, 1037`).
- **Kapitelzellen** haben kein `tabular-nums` (`list.css:99-109`).
- **Browser-Tabelle:** Unter Windows fehlt „Chromium“, unter macOS Opera (`scan.py:411-422, 483`).
- **Toter Code und Doppelzählung:**
  - `combine_ratings` zählt das MangaBaka-Aggregat doppelt, und `bayes_adjust` ist toter Code
    (`catalog.py:133-142`; `enrich.py:326-349`).
  - `benchmark_library` verwirft die Overrides (`tools/benchmark_library.py:84`).
- **Gegenprüfung:** _je Punkt offen_

---

## Erledigt (PR „Befunde 24.09.2026“, Branch `claude/manga-leseliste-syncfindus-3bzxv5`)

Die Befunde waren vorab gegengeprüft. Bei der Umsetzung wurde jeder erneut nachgestellt: Ein Test in
`tests/test_befunde_2026_09.py` ist auf `8b74a8c` rot und jetzt grün (40 von 48 Tests rot auf dem alten
Stand, die übrigen 8 sichern bewusst unverändertes Verhalten ab). Dazu kamen ein Browser-Durchlauf (Chromium)
und ein Abgleich mit den 71 Parser-Tests aus SyncFindus, die vor und nach der Änderung gleich grün sind.

| # | Befund | Fix |
|---|---|---|
| E-01 | XSS: fremde Titel beenden das Inline-`<script>` (RECSPOOL/SEED/MIG …) | `render._js()` maskiert `< > &` und U+2028/9. Typ und Genres escaped. `escH` maskiert `>` und `'` |
| E-02 | ✔-Quellen-Bestätigung schrieb unter `norm(Anzeigetitel)`, ersetzte den ganzen Eintrag, machte opake Kapitel-IDs zur `{n}`-Vorlage | Auflösung über `data-h` (`enrich.cache_keys_for_h`), `save_override` mergt, `ist_opake_kapitel_id` |
| E-03 | ⚠-Meldung traf über den Titel oft nichts und verschwand trotzdem im Archiv | Die Meldung trägt `h`. `_consume_broken` und `fix_broken` lösen darüber auf. Nicht Gefundenes steht im Archiv |
| E-04 | ID-Wechsel (al:/UUID → mb:) ließ Favorit/Archiv/chapFix verwaisen | `id_hist` im Cache, als Alias in MIG, aber nie ein lebender Schlüssel |
| E-05 | `_alive_status` wertete Timeout/5xx als „nachweislich weg“; eine Discovery bei schlechtem Netz leerte die Reader-Liste | `'down'`, `verify_reader` dreiwertig; `discover_readers` entfernt nur bei `False` |
| E-06 | Alter Handwert (chapFix) überdeckte neuere Scans für immer; `data-kap` blieb alt | `{n, b}`: Überholt der Scan den Handwert, gewinnt der Scan. `data-kap` folgt |
| E-07 | Release ohne `SyncManga.exe` hätte Installer-Nutzer still von Updates abgeschnitten | `available` hängt an exe **oder** Setup. Einzeldatei-Nutzer bekommen einen Hinweis |
| E-08 | Titel-Parser: Pipe-Regel („… \| Weeb Central“ → 'Weeb Central') und abgeschnittene Zahlentitel ('Kaiju No', 'Zom') | `re.match` für die Pipe-Regel. Kein Zahlenschnitt nach expliziter Kapitel-Marke |
| E-09 | Kapitel-Token ohne Wortgrenze ('switch-2-1' → 2.1, 'the-witch-2' → Slug kaputt) | Wortgrenzen in `URLCH`/`URLCH_DASH`/Slug-Schnitt/`cfRelink`, letzter Treffer zählt |
| E-10 | CJK-Suchbegriffe wurden zu '' normiert, Ähnlichkeit 1.0 zu allem | `sim_norm` + `key_ratio`: leere Seite = 0.0 |
| E-11 | `applyPause` warf nach einem ⚠-Klick `NotFoundError` (seit 6db3024) und ließ die restlichen Zeilen unbearbeitet | Einfügen in den Eltern-Knoten von `.srcown` |
