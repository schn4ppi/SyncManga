# 📚 SyncManga

**Your manga reading list, on autopilot.**

SyncManga reads your browser history (Firefox, Chrome, Edge — read-only!),
automatically detects which series you read and which chapter you're on, and
builds an interactive reading list from it: verified continue-reading links,
ratings, genres, filters, favorites, day/night mode, import/export
(MyAnimeList/AniList) and recommendations.

## Install

1. Download the latest `SyncManga.exe` from **Releases** (right sidebar).
2. Double-click it — that's all. A tray icon appears and the list builds itself
   on the first run (a few minutes, depending on your library size).
3. The finished list lives at `%LOCALAPPDATA%\SyncManga\Manga_Leseliste.html`
   (open it straight from the tray menu). A 📖 guide sits right next to it.

> **Windows note:** On first launch SmartScreen shows "Unknown publisher"
> (the exe is not commercially signed). Click **"More info" → "Run anyway"**.
> Everything runs locally — nothing leaves your PC except the database queries
> (MangaBaka/AniList etc.) used to enrich your list.

## Updates

SyncManga keeps itself up to date: after each sync it checks this repo's
Releases. By default it only notifies you (tray menu → **"Check for updates…"**
installs with one click); enable **"Update automatically"** in the tray menu
and new versions install themselves. Every download is verified before use:
HTTPS only, pinned to this repository, exact size and SHA-256 checksum.

## Languages

English & German — the app follows your Windows display language automatically.

## Report a bug

Inside the list: **⇅ Import/Export → ❓ Quick guide → 🐛 Report a bug** — a short
mail is enough, reports feed straight into fixes.


<img width="1656" height="879" alt="grafik" src="https://github.com/user-attachments/assets/896dab03-31fc-431c-bccd-29c899a9b0d9" />
