# SyncManga

*(Deutsch unten — English below.)*

---

## 🇩🇪 Deutsch

**SyncManga** liest deine Browser (Verlauf **und** Lesezeichen) und baut daraus eine schöne,
browser-unabhängige **Manga-Leseliste** als HTML-Seite — mit Titel, Flagge, Status, Autor,
Bewertung und deinem Lese-Fortschritt. Es läuft als schlankes Tray-Symbol.

Unterstützte Browser: **Firefox, Waterfox, Chrome, Edge, Brave, Vivaldi, Opera (GX)** — und
**Safari** (macOS). Alle gefundenen Browser/Profile werden zusammengeführt; der größte
Fortschritt gewinnt. Die Liste ist **voll mobil-optimiert** (seit v0.3.4).

### Datenschutz
**100 % lokal — es werden keine Daten hochgeladen.** SyncManga liest deine Browser-Datenbanken
nur **lesend** (über eine Kopie) und verändert in den Browsern nichts. Es werden nur öffentliche
Manga-Datenbanken im Internet abgefragt (Titel/Bewertung/Status), niemals deine Daten gesendet.

### Starten
- **Fertige App:** `SyncManga.exe` doppelklicken. Beim ersten Start warnt Windows-SmartScreen
  evtl. vor einer „unbekannten" App (die Datei ist nicht teuer signiert) → *Weitere Informationen*
  → *Trotzdem ausführen*.
- **Mit Python:** `python -m syncmanga` (einmaliger Lauf) oder `python -m syncmanga.tray` (Tray).

### Tray-Menü
- **Liste öffnen** (auch Linksklick aufs Symbol) · **Aktualisieren** · **Sprache** (Auto/Deutsch/
  English) · **Hilfe** · **Beenden**.

### Dein Lese-Fortschritt (Spalte „User")
Automatisch abgeleitet — du musst nichts pflegen:
- **Lese gerade** – offene Kapitel, kürzlich gelesen.
- **Aufgeholt** – beim neuesten bekannten Kapitel.
- **Abgeschlossen** 🏁 – komplett gelesen UND der Manga ist abgeschlossen.
- **Pausiert** – offene Kapitel, aber länger (>60 Tage) nicht gelesen.
- **Backlog** – gemerkt, aber noch nicht gelesen.

### Lesen, Quellen & Ampel
- **weiterlesen** springt direkt auf dein nächstes Kapitel auf einer funktionierenden Lese-Seite;
  **＋Alt** zeigt Alternativen, **⚠** meldet einen kaputten Link (mit 1 Klick) + zeigt sofort Alternativen.
- **Quellen-Ampel** oben: 🟢 funktioniert · 🟡 nur im Browser (Cloudflare) · 🔴 nicht erreichbar.
- **📊 Statistik** (einklappbar) + **🆕 Neue-Kapitel-Filter** zeigen deinen Überblick auf einen Blick.
- **Kapitel-Zelle anklicken** = Lesestand von Hand setzen — alle Links der Zeile (weiterlesen
  **und** Reserven) folgen; Reader ohne dieses Kapitel verweisen auf die Serien-Seite.

### „Braucht Hilfe"
Findet SyncManga zu einer Serie keinen Treffer (meist ein Namens-Wirrwarr aus der URL), erscheint
ein **„⚠ Hilfe"-Filter**. Du kannst die Serienseite öffnen, neu suchen oder den richtigen Titel
als Korrektur speichern (`overrides.json`, reine Daten) — danach bleibt sie aufgelöst.

### 📱 Unterwegs
Die Liste ist **eine einzelne HTML-Datei** und für Handys optimiert (keine Seitwärts-Scrollerei,
Symbol-Knöpfe, 4er-Cover-Raster). Leg sie z.B. in deinen OneDrive-/Google-Drive-Ordner und
öffne sie unterwegs — oder serviere sie im Heim-WLAN (`python -m tools.serve`).

### Updates
SyncManga hält sich selbst aktuell: nach jedem Sync prüft es die Releases dieses Repos.
Standardmäßig wird nur benachrichtigt (Tray-Menü → **„Nach Updates suchen…"**); optional
installieren sich neue Versionen automatisch. Jeder Download wird vor der Nutzung geprüft:
nur HTTPS, fest an dieses Repository gebunden, exakte Größe + SHA-256-Prüfsumme.

### 📱 Unterwegs & Online-Zugriff
Die Liste ist **eine einzelne, mobil-optimierte HTML-Datei**. Zwei Wege aufs Handy:
- **Ordner-Weg (offline):** leg sie in deinen OneDrive-/Google-Drive-Ordner und öffne sie unterwegs.
- **Online-Zugriff (ein Klick):** Tray-Menü → **🌐 Online-Zugriff (Handy)**. Die App legt ein
  **anonymes** Konto an und zeigt dir einen kurzen Zugangscode. Öffne **manga.j-bk.org** am Handy,
  gib den Code ein — fertig. Deine Liste aktualisiert sich dort nach jedem Sync von selbst.
  **Datensparsam:** keine E-Mail, kein Tracking; hochgeladen werden nur Titel + Lesestand, nie
  Browser-Daten. Jederzeit im Tray abschaltbar.

### Sprache
SyncManga nutzt automatisch die Sprache deines Systems (Deutsch → Deutsch, sonst Englisch).
Im Tray-Menü unter **Sprache** überschreibbar.

---

## 🇬🇧 English

**SyncManga** reads your browsers (history **and** bookmarks) and turns them into a tidy,
browser-independent **manga reading list** as an HTML page — with title, flag, status, author,
rating and your reading progress. It runs as a small tray icon.

Supported browsers: **Firefox, Waterfox, Chrome, Edge, Brave, Vivaldi, Opera (GX)** — and
**Safari** (macOS). All detected browsers/profiles are merged; the biggest progress wins.
The list is **fully mobile-optimized** (since v0.3.4).

### Privacy
**100 % local — nothing is uploaded.** SyncManga reads your browser databases **read-only**
(via a copy) and changes nothing in your browsers. It only queries public manga databases
(title/rating/status); your data never leaves your machine.

### Run it
- **Packaged app:** double-click `SyncManga.exe`. On first launch Windows SmartScreen may warn
  about an "unknown" app (the file is not expensively signed) → *More info* → *Run anyway*.
- **With Python:** `python -m syncmanga` (one run) or `python -m syncmanga.tray` (tray).

### Tray menu
- **Open list** (also left-click the icon) · **Update now** · **Language** (Auto/Deutsch/English) ·
  **Help** · **Quit**.

### Your reading progress (column "You")
Derived automatically — nothing to maintain:
- **Reading** – open chapters, read recently.
- **Caught up** – at the latest known chapter.
- **Finished** 🏁 – fully read AND the manga is completed.
- **Paused** – open chapters, but not read for a while (>60 days).
- **Backlog** – bookmarked but not read yet.

### Reading, sources & status lights
- **Continue** jumps straight to your next chapter on a working reader site; **＋Alt** shows
  alternatives, **⚠** reports a broken link (one click) and shows alternatives instantly.
- **Source status lights** at the top: 🟢 working · 🟡 browser only (Cloudflare) · 🔴 down.
- **📊 Statistics** (collapsible) + **🆕 New-chapters filter** give you the overview at a glance.
- **Click the chapter cell** to set your progress by hand — every link in the row (continue
  **and** backups) follows; readers that don't have that chapter point to the series page.

### "Needs help"
If SyncManga can't match a series (usually a messy name from the URL), a **"⚠ Help" filter**
appears. You can open the series page, search again, or save the correct title as a fix
(`overrides.json`, pure data) — after that it stays resolved.

### 📱 On the go
The list is **a single HTML file**, optimized for phones (no sideways scrolling, icon buttons,
4-per-row cover grid). Drop it into your OneDrive/Google Drive folder and open it anywhere —
or serve it on your home Wi-Fi (`python -m tools.serve`).

### Updates
SyncManga keeps itself up to date: after each sync it checks this repo's Releases. By default
it only notifies you (tray menu → **"Check for updates…"**); optionally new versions install
themselves. Every download is verified before use: HTTPS only, pinned to this repository,
exact size and SHA-256 checksum.

### 📱 On the go & online access
The list is **a single, mobile-optimized HTML file**. Two ways onto your phone:
- **Folder route (offline):** drop it into your OneDrive/Google Drive folder and open it anywhere.
- **Online access (one click):** tray menu → **🌐 Online access (phone)**. The app creates an
  **anonymous** account and shows you a short access code. Open **manga.j-bk.org** on your phone,
  enter the code — done. Your list refreshes there after every sync.
  **Privacy-friendly:** no email, no tracking; only titles + progress are uploaded, never browser
  data. Turn it off anytime from the tray.

### Language
SyncManga uses your system language automatically (German → German, otherwise English).
Override it in the tray menu under **Language**.

---

## 🛠️ Für Entwickler / Build & Beitrag

Dieses Repository ist der **Quellcode** der eigenständigen Manga-Leseliste. Es enthält **bewusst
keine** vorgefertigte Direktlink-Sammlung und keine gescrapten Seiten-Kataloge — deine Liste
entsteht ausschließlich aus **deinem eigenen Browser-Verlauf**. Persönliche Laufzeitdaten
(`Manga_Leseliste.html`, `md_cache.json`, `data/*_map.json.gz` usw.) sind per `.gitignore`
ausgeschlossen.

**Aus dem Quellcode starten**
```bash
pip install -r requirements.txt   # bzw. pystray, Pillow (Tray); Standard-Lib fuer den Rest
python -m syncmanga           # einmaliger Lauf -> Manga_Leseliste.html
python -m syncmanga.tray      # als Tray-Symbol
```

**Eigene .exe bauen** (Windows): `build\build.bat` doppelklicken (oder
`pyinstaller --noconfirm --clean --distpath . build\SyncManga.spec`). Ergebnis: `SyncManga.exe`.

**AniList-Auto-Sync** (optional): `python -m tools.anilist_auth` (PIN-Verfahren, Token landet im
Windows-Keyring — nie in Dateien).

## ⚖️ Hinweis / Disclaimer

SyncManga hostet und verbreitet **keine** Manga-Inhalte. Es organisiert **deine eigenen** bereits
besuchten Lese-Links zu einer übersichtlichen Liste und fragt öffentliche Metadaten-DBs
(MangaDex, AniList, MangaUpdates, Kitsu, MyAnimeList) ab. Nutzung auf eigene Verantwortung,
**nur für den privaten Gebrauch**. Ob eine verlinkte Seite Inhalte rechtmäßig anbietet, liegt
außerhalb dieses Tools.

## 📄 Lizenz

[MIT](LICENSE) © 2026 Jan-Bernd Kalvelage
