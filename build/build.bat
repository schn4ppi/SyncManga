@echo off
chcp 65001 >nul
REM Baut die eigenständige SyncManga.exe (nur der syncmanga-Kern, kein Mail-Code).
REM Nutzt JBs venv (Core\venv); PyInstaller wird bei Bedarf hineininstalliert (dev-only, additiv).
REM Liegt unter Manga\build\ -> zwei Ebenen hoch zum Repo-Root.
cd /d "%~dp0..\.."
Core\venv\Scripts\python.exe -m pip install --quiet --upgrade pyinstaller
Core\venv\Scripts\python.exe -m PyInstaller --noconfirm --clean --distpath "." --workpath "%TEMP%\syncmanga_pyi" Manga\build\SyncManga.spec
if errorlevel 1 (
  echo.
  echo [FEHLER] Build fehlgeschlagen - siehe Meldung oben.
  pause
  exit /b 1
)
echo.
echo Fertig: SyncManga.exe (im Hauptordner)
pause
