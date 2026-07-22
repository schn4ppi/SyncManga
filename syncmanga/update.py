# -*- coding: utf-8 -*-
"""
Self-Update der App „SyncManga" — non-destruktiv, nur user-space.

Aktualisiert die Reader-Quellen (sources.json) und meldet neue Programm-Versionen aus dem
GitHub-Repo. HARTE REGELN: nichts loeschen, keine System-/Rechte-Aenderungen; vor jedem
Tausch ein .bak des Alten behalten; heruntergeladene Daten VOR dem Tausch validieren
(ungueltig -> alte Datei bleibt). Schreiben immer atomar (tmp + os.replace).

Netzzugriffe sind injizierbar (Parameter `fetch`), damit Tests ohne echtes Netz laufen.
Seit Task #34 tauscht sich auch die gepackte .exe selbst (unten: Selbst-Update).
"""
import json
import os
import shutil

# JBs oeffentliches Repo der Standalone-App. NUR von hier wird aktualisiert: Versions-Check
# und exe-Download laufen ausschliesslich per HTTPS gegen dieses Repo (Release-Assets).
REPO = "schn4ppi/SyncManga"
BRANCH = "main"


def raw_url(path, repo=REPO, branch=BRANCH):
    """GitHub-Raw-URL einer Datei im Repo."""
    return f"https://raw.githubusercontent.com/{repo}/{branch}/{path}"


def parse_version(v):
    """'v1.2.3' / '1.2' / 'v.1.2.3' -> (1,2,3) / (1,2) / (1,2,3). Nicht-numerische Teile -> 0.

    Fuehrende v/V UND Punkte werden entfernt — JB taggt real z.B. `v.0.3.0`; das darf nie
    als (0,0,3,0) gelesen werden, sonst haelt sich die App faelschlich fuer aktuell."""
    parts = []
    for p in str(v or "").strip().lstrip("vV.").split("."):
        digits = "".join(ch for ch in p if ch.isdigit())
        parts.append(int(digits) if digits else 0)
    return tuple(parts) or (0,)


def is_newer(remote, local):
    """True, wenn Version `remote` neuer ist als `local` (laengenunabhaengig)."""
    a, b = parse_version(remote), parse_version(local)
    n = max(len(a), len(b))
    return a + (0,) * (n - len(a)) > b + (0,) * (n - len(b))


def backup_and_write(path, content):
    """Datei non-destruktiv ersetzen: erst `.bak` des Alten, dann atomar schreiben.

    `content` darf bytes oder str sein. Gibt den Backup-Pfad zurueck (oder None, wenn es
    vorher keine Datei gab)."""
    data = content.encode("utf-8") if isinstance(content, str) else content
    bak = None
    if os.path.exists(path):
        bak = path + ".bak"
        shutil.copy2(path, bak)
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "wb") as f:
        f.write(data)
    os.replace(tmp, path)
    return bak


def _valid_sources(data):
    return isinstance(data, dict) and bool(data.get("manga") or data.get("manhwa"))


def update_sources(local_path, fetch):
    """sources.json non-destruktiv aktualisieren -> (changed: bool, msg: str).

    `fetch()` liefert den Remote-Inhalt (bytes/str). Ablauf: laden -> als JSON parsen ->
    VALIDIEREN (manga/manhwa vorhanden) -> nur bei Aenderung tauschen (mit .bak). Bei
    ungueltigem Download oder Fehler bleibt die alte Datei unangetastet."""
    try:
        raw = fetch()
        text = raw.decode("utf-8") if isinstance(raw, bytes) else raw
        data = json.loads(text)
    except Exception as e:
        return False, f"Download/Parsing fehlgeschlagen, alte Quellen behalten: {e}"
    if not _valid_sources(data):
        return False, "ungueltige sources.json -> nicht uebernommen (alte behalten)"
    if os.path.exists(local_path):
        try:
            with open(local_path, encoding="utf-8") as f:
                if json.load(f) == data:
                    return False, "Reader-Quellen bereits aktuell"
        except Exception:
            pass
    backup_and_write(local_path, text)
    return True, "Reader-Quellen aktualisiert (Backup .bak behalten)"


def check_program_version(current, fetch_version):
    """Neue Programm-Version pruefen -> (update_verfuegbar: bool, remote_version: str).

    `fetch_version()` liefert die neueste Versionsnummer (z.B. aus VERSION im Repo).
    Reines Melden — der eigentliche Programm-Tausch ist bei einer .exe der Installer/Phase 7."""
    try:
        remote = (fetch_version() or "").strip()
    except Exception:
        return False, ""
    return (is_newer(remote, current), remote)


# ---------------- Selbst-Update der gepackten .exe (Task #34) ----------------
# Windows-Trick, ganz ohne Adminrechte: die LAUFENDE exe kann nicht ueberschrieben, aber
# UMBENANNT werden -> alte exe wird ".old", die verifizierte neue rueckt an den Originalpfad,
# Neustart. Beim naechsten Start raeumt cleanup_old_exe() den Rest weg. Alles Netz ist
# injizierbar (fetch_json/fetch) -> die komplette Entscheidungslogik laeuft in Tests ohne Netz.

RELEASE_API = f"https://api.github.com/repos/{REPO}/releases/latest"
EXE_ASSET = "syncmanga.exe"          # erwarteter Asset-Name (case-insensitiv verglichen)
SETUP_ASSET = "syncmanga-setup.exe"  # Installer-Asset (seit v0.4.1); Update-Weg der installierten Variante
INNO_UNINSTALL_KEY = r"Software\Microsoft\Windows\CurrentVersion\Uninstall\{7E4A2C1B-5B7E-4C93-9C41-3A5F92D8B0E4}_is1"   # AppId aus build/SyncManga.iss
MIN_EXE_SIZE = 5 * 2 ** 20           # Plausibilitaets-Untergrenze: kleiner = kaputter Download


def frozen_exe():
    """Pfad der laufenden .exe — oder None im Quellbaum (dann gibt es nichts zu tauschen)."""
    import sys
    return sys.executable if getattr(sys, "frozen", False) else None


def installiert_via_setup(exe=None, _reg_check=None):
    """True, wenn die App per Inno-Setup installiert wurde (JB-Befund 22.07.: der alte
    Updater drehte Setup-Nutzer beim exe-Tausch zurueck in die riskante onefile-Form).

    Zwei unabhaengige Zeichen: der _internal-Ordner neben der exe (onedir-Layout) ODER der
    Inno-Uninstall-Eintrag in der Registry. Letzterer ueberlebt auch, wenn ein Alt-Updater
    die exe schon einmal durch onefile ersetzt hat -> solche Nutzer werden beim naechsten
    Update in die Setup-Welt ZURUECKGEHEILT. `_reg_check` ist fuer Tests injizierbar."""
    exe = exe or frozen_exe()
    if exe and os.path.isdir(os.path.join(os.path.dirname(exe), "_internal")):
        return True
    if _reg_check is not None:
        return bool(_reg_check())
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, INNO_UNINSTALL_KEY):
            return True
    except (OSError, ImportError):
        return False


def pick_setup_asset(assets, repo=REPO):
    """(setup_asset, sha256_aus_digest) — rein, testbar. Gleicher Repo-Pin wie pick_assets;
    die Pruefsumme kommt aus GitHubs Asset-`digest` ("sha256:<hex>"), NICHT aus einem
    .sha256-Asset (das wuerde der sha-Matcher der Alt-Clients faelschlich greifen)."""
    prefix = f"https://github.com/{repo}/releases/download/"
    for a in assets or []:
        if not isinstance(a, dict) or not str(a.get("browser_download_url", "")).startswith(prefix):
            continue
        if str(a.get("name", "")).lower() == SETUP_ASSET:
            digest = str(a.get("digest") or "")
            sha = digest.split(":", 1)[1].lower() if digest.lower().startswith("sha256:") else ""
            return a, sha
    return None, ""


def pick_assets(assets, repo=REPO):
    """(exe_asset, sha_asset) aus einer Release-Asset-Liste — rein, testbar.

    Akzeptiert NUR Assets, deren Download-URL auf das eigene Repo zeigt
    (https://github.com/<repo>/releases/download/…). Ein fremder/manipulierter Eintrag in
    der API-Antwort kann so nie zu einem Download von woanders fuehren."""
    prefix = f"https://github.com/{repo}/releases/download/"
    exe = sha = None
    for a in assets or []:
        if not isinstance(a, dict) or not str(a.get("browser_download_url", "")).startswith(prefix):
            continue
        name = str(a.get("name", "")).lower()
        if name == EXE_ASSET:
            exe = a
        elif name.endswith(".sha256") and "syncmanga" in name:
            sha = a
    return exe, sha


def parse_sha256(text):
    """Erste 64-stellige Hex-Folge aus einer .sha256-Datei ('HASH' / 'HASH  datei') -> lowercase."""
    import re
    m = re.search(r"[0-9a-fA-F]{64}", str(text or ""))
    return m.group(0).lower() if m else ""


def check_release(current, fetch_json):
    """Neuestes GitHub-Release auswerten -> {available, version, exe_url, size, sha_url}.

    `fetch_json()` liefert die /releases/latest-Antwort (injizierbar). Fehler, kein Release
    oder kein exe-Asset -> available=False, die App laeuft einfach normal weiter.
    /releases/latest liefert nie Prereleases -> entspricht update_channel "stable"."""
    try:
        data = fetch_json() or {}
    except Exception:
        return {"available": False, "version": ""}
    tag = str(data.get("tag_name") or "").strip()
    exe, sha = pick_assets(data.get("assets"))
    setup, setup_sha = pick_setup_asset(data.get("assets"))
    return {"available": bool(exe) and is_newer(tag, current),
            "version": tag.lstrip("vV."),
            "exe_url": (exe or {}).get("browser_download_url", ""),
            "size": int((exe or {}).get("size") or 0),
            "sha_url": (sha or {}).get("browser_download_url", ""),
            "setup_url": (setup or {}).get("browser_download_url", ""),
            "setup_size": int((setup or {}).get("size") or 0),
            "setup_sha": setup_sha}


def verify_exe(data, expected_size=0, expected_sha=""):
    """Download pruefen -> (ok, grund) — rein, testbar.

    Erst wenn ALLE verfuegbaren Pruefungen bestehen (Groesse plausibel, Groesse exakt wie im
    Release vermerkt, SHA256 wie im .sha256-Asset), darf die exe getauscht werden."""
    import hashlib
    n = len(data or b"")
    if n < MIN_EXE_SIZE:
        return False, f"nur {n} Bytes (kaputter/abgebrochener Download)"
    if expected_size and n != int(expected_size):
        return False, f"Groesse {n} != erwartet {expected_size}"
    if expected_sha:
        if hashlib.sha256(data).hexdigest() != expected_sha.lower():
            return False, "SHA256-Pruefsumme stimmt nicht"
    return True, ""


def fetch_release_json(url=None, timeout=20):
    """GET /releases/latest (echtes Netz). GitHub verlangt einen User-Agent."""
    import urllib.request
    req = urllib.request.Request(url or RELEASE_API,
                                 headers={"User-Agent": "SyncManga-Updater",
                                          "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def fetch_https(url, timeout=300):
    """Bytes einer HTTPS-URL (echtes Netz) — alles andere wird abgelehnt, nie umgeschrieben."""
    import urllib.request
    if not str(url).startswith("https://"):
        raise ValueError(f"nur HTTPS erlaubt: {url!r}")
    req = urllib.request.Request(url, headers={"User-Agent": "SyncManga-Updater"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def download_exe(info, dest_dir, fetch=None):
    """Release-exe verifiziert nach `SyncManga_new.exe` laden -> Pfad. Wirft bei jedem Zweifel.

    Reihenfolge bewusst: erst ALLES pruefen (verify_exe), dann atomar in den Zielordner
    schreiben (tmp + os.replace). Ein halber Download liegt nie unter dem Zielnamen."""
    fetch = fetch or fetch_https
    data = fetch(info["exe_url"])
    expected_sha = ""
    if info.get("sha_url"):
        try:
            expected_sha = parse_sha256(fetch(info["sha_url"]).decode("utf-8", "replace"))
        except Exception:
            expected_sha = ""            # .sha256-Asset kaputt -> Groessen-Pruefungen greifen trotzdem
    ok, why = verify_exe(data, info.get("size") or 0, expected_sha)
    if not ok:
        raise ValueError(f"Update verworfen: {why}")
    target = os.path.join(dest_dir, "SyncManga_new.exe")
    tmp = target + ".tmp"
    with open(tmp, "wb") as f:
        f.write(data)
    os.replace(tmp, target)
    return target


def download_setup(info, dest_dir, fetch=None):
    """Installer verifiziert nach `SyncManga_setup_new.exe` laden -> Pfad. OHNE digest-SHA
    wird ABGELEHNT (fail-safe: lieber kein Update, als den Setup-Nutzer ohne Pruefsumme zu
    aktualisieren oder ihn per exe-Tausch in die onefile-Form zu drehen)."""
    if not info.get("setup_sha"):
        raise ValueError("Update verworfen: Release liefert keinen digest fuers Setup")
    fetch = fetch or fetch_https
    data = fetch(info["setup_url"])
    ok, why = verify_exe(data, info.get("setup_size") or 0, info["setup_sha"])
    if not ok:
        raise ValueError(f"Update verworfen: {why}")
    target = os.path.join(dest_dir, "SyncManga_setup_new.exe")
    tmp = target + ".tmp"
    with open(tmp, "wb") as f:
        f.write(data)
    os.replace(tmp, target)
    return target


def apply_setup_update(setup_exe, running_exe):
    """Installierte Variante aktualisieren: Setup STILL ausfuehren und die App sofort
    beenden (gibt die Dateisperren frei; CloseApplications=no im iss). Die cmd-Kette
    wartet auf das Setup und startet die App danach neu."""
    import subprocess
    kette = ('cmd /c ""' + setup_exe + '" /VERYSILENT /SUPPRESSMSGBOXES /NORESTART'
             ' & start "" "' + running_exe + '""')
    subprocess.Popen(kette, close_fds=True,
                     creationflags=getattr(subprocess, "DETACHED_PROCESS", 0x8)
                     | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0x200))
    os._exit(0)                          # wie apply_exe_update: nichts darf festhalten


def apply_exe_update(new_exe, running_exe, restart=True):
    """Selbst-Ersetzen ohne Adminrechte: laufende exe -> `.old` umbenennen (das erlaubt
    Windows), neue exe an den Originalpfad, Neustart. Schlaegt der Tausch fehl, wird die
    alte exe zurueckgerollt — es gibt keinen Moment ohne lauffaehige App."""
    old = running_exe + ".old"
    try:
        if os.path.exists(old):
            os.remove(old)               # Rest vom letzten Update
    except OSError:
        old = running_exe + f".old-{os.getpid()}"   # noch gesperrt -> eindeutigen Namen nehmen
    os.rename(running_exe, old)
    try:
        os.replace(new_exe, running_exe)
    except OSError:
        os.rename(old, running_exe)      # Rollback: Original zurueck an seinen Platz
        raise
    if restart:
        import subprocess
        subprocess.Popen([running_exe], close_fds=True)
        os._exit(0)                      # wie on_quit: atexit/ThreadPool duerfen nicht festhalten


def cleanup_old_exe(running_exe=None):
    """`.old`(-…) frueherer Updates loeschen — best-effort beim Start (die alte Instanz kann
    in der ersten Sekunde noch am Beenden sein; dann klappt es eben beim naechsten Start)."""
    exe = running_exe or frozen_exe()
    if not exe:
        return
    import glob
    for p in glob.glob(exe + ".old*"):
        try:
            os.remove(p)
        except OSError:
            pass
