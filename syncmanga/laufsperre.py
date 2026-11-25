"""Gemeinsame SyncManga-Laufsperre mit gebundenen Windows-Dateigriffen.

Verwaiste Fremdsperren bleiben als Rohbeleg erhalten. Unklare Zustände sperren.
Eigene Besitznahme ist CREATE_NEW; nur deren eigener gehaltener Griff darf beim
Abschluss gelöscht werden. Keine Prozesssignale, Altersheilung oder Path-Renames.
"""

import ctypes
import hashlib
import math
import os
import uuid
from dataclasses import dataclass

_MAX_BYTES = 128
_KERNEL = None
_DWORD = ctypes.c_uint32
_HANDLE = ctypes.c_void_p


class _FILETIME(ctypes.Structure):
    _fields_ = [("low", _DWORD), ("high", _DWORD)]


class _FILEINFO(ctypes.Structure):
    _fields_ = [("attribute", _DWORD), ("erstellt", _FILETIME),
                ("gelesen", _FILETIME), ("geschrieben", _FILETIME),
                ("volume", _DWORD), ("size_high", _DWORD), ("size_low", _DWORD),
                ("links", _DWORD), ("index_high", _DWORD), ("index_low", _DWORD)]


class _RENAME_OPTIONEN(ctypes.Union):
    _fields_ = [("ReplaceIfExists", ctypes.c_ubyte), ("Flags", _DWORD)]


def _rename_info(pointer):
    class RenameInfo(ctypes.Structure):
        _fields_ = [("Optionen", _RENAME_OPTIONEN), ("RootDirectory", pointer),
                    ("FileNameLength", _DWORD), ("FileName", ctypes.c_uint16 * 1)]
    return RenameInfo


_RENAME_INFO = _rename_info(_HANDLE)


class _DISPOSITION_INFO(ctypes.Structure):
    _fields_ = [("DeleteFile", ctypes.c_ubyte)]


@dataclass(frozen=True)
class _Stand:
    identitaet: tuple
    roh: bytes

    @property
    def sha256(self):
        return hashlib.sha256(self.roh).hexdigest()


def _kernel():
    global _KERNEL
    if os.name != "nt":
        raise OSError("Die gebundene Manga-Sperre erfordert Windows.")
    if _KERNEL is not None:
        return _KERNEL
    api = ctypes.WinDLL("kernel32", use_last_error=True)
    signaturen = {
        "CreateFileW": (_HANDLE, (ctypes.c_wchar_p, _DWORD, _DWORD, _HANDLE,
                                 _DWORD, _DWORD, _HANDLE)),
        "CloseHandle": (ctypes.c_int32, (_HANDLE,)),
        "GetFileType": (_DWORD, (_HANDLE,)),
        "GetFileInformationByHandle": (ctypes.c_int32, (_HANDLE, ctypes.c_void_p)),
        "SetFilePointerEx": (ctypes.c_int32, (_HANDLE, ctypes.c_int64,
                                            ctypes.c_void_p, _DWORD)),
        "ReadFile": (ctypes.c_int32, (_HANDLE, ctypes.c_void_p, _DWORD,
                                    ctypes.c_void_p, ctypes.c_void_p)),
        "WriteFile": (ctypes.c_int32, (_HANDLE, ctypes.c_void_p, _DWORD,
                                     ctypes.c_void_p, ctypes.c_void_p)),
        "FlushFileBuffers": (ctypes.c_int32, (_HANDLE,)),
        "SetFileInformationByHandle": (ctypes.c_int32, (_HANDLE, ctypes.c_int32,
                                                      ctypes.c_void_p, _DWORD)),
    }
    for name, (resultat, argumente) in signaturen.items():
        funktion = getattr(api, name)
        funktion.restype = resultat
        funktion.argtypes = argumente
    _KERNEL = api
    return api


def _rename_puffer(name):
    if "\x00" in name:
        raise ValueError("Unzulässiger Belegname.")
    roh = name.encode("utf-16-le")
    abstand = _RENAME_INFO.FileName.offset
    puffer = ctypes.create_string_buffer(max(ctypes.sizeof(_RENAME_INFO),
                                            abstand + len(roh) + 2))
    info = _RENAME_INFO.from_buffer(puffer)
    info.Optionen.ReplaceIfExists = 0
    info.RootDirectory = None
    info.FileNameLength = len(roh)
    ctypes.memmove(ctypes.addressof(puffer) + abstand, roh, len(roh))
    return puffer


class _Griff:
    def __init__(self, pfad, *, exklusiv=True, erzeugen=False):
        self.handle = None
        self.pfad = os.path.abspath(os.fspath(pfad))
        api = _kernel()
        zugriff = 0x80000000 | (0x00010000 if exklusiv else 0)
        if erzeugen:
            zugriff |= 0x40000000
        handle = api.CreateFileW(self.pfad, zugriff, 1 if exklusiv else 7,
                                 None, 1 if erzeugen else 3, 0x00200000, None)
        if handle == ctypes.c_void_p(-1).value:
            raise ctypes.WinError(ctypes.get_last_error())
        self.handle = handle
        try:
            self._info()
        except BaseException:
            self.schliessen()
            raise

    def __enter__(self):
        return self

    def __exit__(self, typ, wert, spur):
        self.schliessen()

    def schliessen(self):
        handle, self.handle = self.handle, None
        if handle is not None and not _kernel().CloseHandle(handle):
            raise ctypes.WinError(ctypes.get_last_error())

    def _info(self):
        if self.handle is None:
            raise OSError("Der eigene Dateigriff ist geschlossen.")
        api, info = _kernel(), _FILEINFO()
        if api.GetFileType(self.handle) != 1:
            raise OSError("Manga-Sperre ist keine reguläre Datenträgerdatei.")
        if not api.GetFileInformationByHandle(self.handle, ctypes.byref(info)):
            raise ctypes.WinError(ctypes.get_last_error())
        if info.attribute & (0x10 | 0x400):
            raise OSError("Verzeichnis oder Dateiverknüpfung ist keine Manga-Sperre.")
        groesse = (info.size_high << 32) | info.size_low
        if groesse > _MAX_BYTES:
            raise OSError("Manga-Sperre enthält keine begrenzte Prozessnummer.")
        return (info.volume, info.index_high, info.index_low,
                info.erstellt.high, info.erstellt.low, groesse, info.attribute,
                info.geschrieben.high, info.geschrieben.low, info.links)

    def stand(self):
        api, vorher = _kernel(), self._info()
        if not api.SetFilePointerEx(self.handle, 0, None, 0):
            raise ctypes.WinError(ctypes.get_last_error())
        puffer, anzahl = ctypes.create_string_buffer(_MAX_BYTES + 1), _DWORD()
        if not api.ReadFile(self.handle, puffer, len(puffer), ctypes.byref(anzahl), None):
            raise ctypes.WinError(ctypes.get_last_error())
        nachher = self._info()
        if vorher != nachher or anzahl.value != nachher[5]:
            raise OSError("Manga-Sperre änderte sich beim Lesen.")
        return _Stand(nachher, puffer.raw[:anzahl.value])

    def schreiben(self, roh):
        api, anzahl = _kernel(), _DWORD()
        puffer = ctypes.create_string_buffer(roh)
        if not api.WriteFile(self.handle, puffer, len(roh), ctypes.byref(anzahl), None):
            raise ctypes.WinError(ctypes.get_last_error())
        if anzahl.value != len(roh) or not api.FlushFileBuffers(self.handle):
            raise OSError("Eigene Manga-Sperre wurde nicht vollständig geschrieben.")

    def umbenennen(self, ziel):
        puffer = _rename_puffer(os.path.abspath(ziel))
        if not _kernel().SetFileInformationByHandle(self.handle, 3, puffer, len(puffer)):
            raise ctypes.WinError(ctypes.get_last_error())

    def eigene_datei_freigeben(self):
        info = _DISPOSITION_INFO(1)
        if not _kernel().SetFileInformationByHandle(self.handle, 4,
                                                   ctypes.byref(info), ctypes.sizeof(info)):
            raise ctypes.WinError(ctypes.get_last_error())


def _snapshot(pfad):
    try:
        with _Griff(pfad, exklusiv=False) as griff:
            return griff.stand()
    except OSError as ex:
        if getattr(ex, "winerror", None) == 2:
            return None
        raise


def _pid(roh):
    text = roh.decode("ascii").strip()
    if not text or not text.isdecimal():
        raise ValueError("Manga-Sperre ohne gültige Prozessnummer.")
    pid = int(text)
    if not 0 < pid < 0x100000000:
        raise ValueError("Manga-Sperre ohne gültige Prozessnummer.")
    return pid


def _befehl(cmdline):
    if not isinstance(cmdline, (list, tuple)) or not cmdline:
        return None
    if any(not isinstance(wert, str) for wert in cmdline):
        return None
    text = " ".join(cmdline).strip().lower()
    return text or None


def ist_manga_update(pid):
    """True aktiv, False eindeutig fremd/tot, None unklar; keine Prozesssignale."""
    try:
        import psutil
    except ImportError:
        return None
    try:
        prozess = psutil.Process(pid)
        cmdline = prozess.cmdline()
        befehl = _befehl(cmdline)
        if befehl is None:
            return None
        if "manga_update" not in befehl or "--probe" in befehl or "--fix" in befehl:
            return False
        start = prozess.create_time()
        if isinstance(start, bool) or not isinstance(start, (int, float)):
            return None
        if not math.isfinite(start) or start <= 0:
            return None
        erneut = psutil.Process(pid)
        if erneut.create_time() != start or erneut.cmdline() != cmdline:
            return None
        return True
    except (psutil.AccessDenied, psutil.ZombieProcess):
        return None
    except psutil.NoSuchProcess:
        return False
    except (OSError, AttributeError):
        return None


def laufende_manga_updates():
    """Zusätzliche bekannte Manga-Prozesse; unklare positive Treffer sperren."""
    try:
        import psutil
    except ImportError:
        return None
    treffer = []
    try:
        for prozess in psutil.process_iter(["pid", "cmdline"]):
            befehl = _befehl(prozess.info.get("cmdline"))
            if not befehl or "manga_update" not in befehl:
                continue
            if "--probe" in befehl or "--fix" in befehl:
                continue
            pid = prozess.info.get("pid")
            if pid == os.getpid():
                continue
            status = ist_manga_update(pid)
            if status is None:
                return None
            if status:
                treffer.append(pid)
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess, OSError):
        return None
    return treffer


def _belegname(pfad):
    return os.fspath(pfad) + ".verwaist." + uuid.uuid4().hex


def _beiseitelegen(griff, stand, pid, melden):
    for _ in range(8):
        ziel = _belegname(griff.pfad)
        try:
            griff.umbenennen(ziel)
        except OSError as ex:
            if getattr(ex, "winerror", None) in (80, 183):
                continue
            raise
        if griff.stand() != stand:
            raise OSError("Gebundener Beleg änderte sich beim Umbenennen.")
        meldung = (f"Manga: verwaiste Sperre {griff.pfad} (PID {pid}) beiseitegelegt: "
                   f"{ziel}; Original-SHA256 {stand.sha256}")
        if melden is None:
            print(meldung, flush=True)
        else:
            melden(meldung)
        return meldung
    raise OSError("Kein kollisionsfreier Name für den verwaisten Sperrbeleg.")


def pruefen(pfad, *, ist_lauf=None, melden=None):
    """-> (gesperrt, Meldung). Quarantäne nur am stabil erneut gebundenen Griff."""
    try:
        vorher = _snapshot(pfad)
        if vorher is None:
            return False, "Keine Manga-Sperrdatei vorhanden."
        pid = _pid(vorher.roh)
        status = (ist_lauf or ist_manga_update)(pid)
        if status is not False:
            return True, f"Manga-Sperre {pfad} (PID {pid}) bleibt aktiv oder unklar."
        with _Griff(pfad) as griff:
            if griff.stand() != vorher:
                return True, f"Manga-Sperre {pfad} änderte sich während der Prozessprüfung."
            if (ist_lauf or ist_manga_update)(pid) is not False:
                return True, f"Manga-Prozessidentität {pid} wurde aktiv oder unklar."
            meldung = _beiseitelegen(griff, vorher, pid, melden)
        return False, meldung
    except Exception as ex:  # noqa: BLE001 — jede unklare Sperrprüfung bleibt geschlossen
        return True, f"Manga-Sperre {pfad} unklar: {type(ex).__name__}: {ex}"


class _EigeneSperre:
    def __init__(self, griff, stand):
        self._griff, self._stand = griff, stand

    def schliessen(self):
        self._griff.schliessen()

    def freigeben(self):
        try:
            if self._griff.stand() != self._stand:
                return False
            self._griff.eigene_datei_freigeben()
            return True
        except OSError:
            return False
        finally:
            self.schliessen()


def erwerben(pfad, *, pid=None, ist_lauf=None, melden=None):
    """-> (eigener gehaltenen Griff | None, Meldung); Besitznahme nur CREATE_NEW."""
    pid = os.getpid() if pid is None else pid
    if isinstance(pid, bool) or not isinstance(pid, int) or not 0 < pid < 0x100000000:
        return None, "Eigene Prozessnummer ist unklar; kein Manga-Lauf gestartet."
    gesperrt, meldung = pruefen(pfad, ist_lauf=ist_lauf, melden=melden)
    if gesperrt:
        return None, meldung
    griff = None
    try:
        griff = _Griff(pfad, erzeugen=True)
        griff.schreiben(str(pid).encode("ascii"))
        stand = griff.stand()
        if stand.roh != str(pid).encode("ascii"):
            raise OSError("Eigene Manga-Sperre wurde nicht vollständig gegengelesen.")
        return _EigeneSperre(griff, stand), "Eigene Manga-Sperre exklusiv erworben."
    except OSError as ex:
        if griff is not None:
            griff.schliessen()
        return None, f"Eigene Manga-Sperre nicht erworben: {type(ex).__name__}: {ex}"
