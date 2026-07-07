@echo off
REM SyncManga - Build der eigenstaendigen Windows-.exe.
REM Nutzt Python von PATH (oder ein lokales .venv). PyInstaller wird bei Bedarf installiert.
chcp 65001 >nul
cd /d "%~dp0.."
python -m pip install --quiet --upgrade pyinstaller || goto :err
python -m PyInstaller --noconfirm --clean --distpath "." --workpath "%TEMP%\syncmanga_pyi" build\SyncManga.spec || goto :err
echo.
echo Fertig - SyncManga.exe liegt im Repo-Root.
goto :eof
:err
echo.
echo Build fehlgeschlagen.
exit /b 1
