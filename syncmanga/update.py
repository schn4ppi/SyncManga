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
MIN_EXE_SIZE = 5 * 2 ** 20           # Plausibilitaets-Untergrenze: kleiner = kaputter Download


def frozen_exe():
    """Pfad der laufenden .exe — oder None im Quellbaum (dann gibt es nichts zu tauschen)."""
    import sys
    return sys.executable if getattr(sys, "frozen", False) else None


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
    return {"available": bool(exe) and is_newer(tag, current),
            "version": tag.lstrip("vV."),
            "exe_url": (exe or {}).get("browser_download_url", ""),
            "size": int((exe or {}).get("size") or 0),
            "sha_url": (sha or {}).get("browser_download_url", "")}


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
