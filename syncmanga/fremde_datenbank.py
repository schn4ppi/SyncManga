# -*- coding: utf-8 -*-
"""Lese-Kopie fremder SQLite-Datenbanken — samt WAL und Rollback-Journal.

Ein Browser hält seine Datenbanken im Betrieb gesperrt, also liest man eine
Kopie. Die naheliegende Kopie liest zu wenig: Firefox und Safari schreiben im
WAL-Modus, der jüngste Stand steht im Write-Ahead-Log neben der Hauptdatei. Wer
nur die Hauptdatei kopiert oder die Kopie mit `immutable=1` öffnet (dieser Modus
liest das WAL nicht), verliert alles seit dem letzten Checkpoint des Browsers:
neue Kapitel, jüngere Zeitpunkte, höhere Zähler (gemessen am 17.09.2026).

Der eine Weg zu einer fremden Browser-Datenbank:

1. Ein frischer, privater Ordner je Lesevorgang — nie ein fester Name und nie
   einer mit der PID. Ein liegengebliebenes `-wal` spielt SQLite sonst auf eine
   neuere Hauptdatei (gemessen: Kapitel 12 fehlte, ein Zähler sprang von 9 auf
   4, `integrity_check` meldete „ok"). Zwei Fäden eines Prozesses teilen sich
   ausserdem die PID.
2. Hauptdatei, `-wal` und `-journal` kopieren. Das `-shm` braucht es nicht:
   Die erste Verbindung auf der Kopie baut den Index aus dem WAL neu auf.
   Ein heißes Rollback-Journal wird ausschließlich in der Kopie zurückgespielt.
3. Der WAL-Kopf wird VOR der Hauptdatei gelesen und mit dem der Kopie
   verglichen. Weicht er ab, hat der Browser das WAL dazwischen neu begonnen, und
   Hauptdatei und WAL passen nicht zusammen: Was der Checkpoint in die
   Hauptdatei geschrieben hat, stünde in keiner der beiden Kopien. Dann beginnt
   der Lauf in einem neuen Unterordner von vorn, höchstens `VERSUCHE` Mal —
   danach `KopieUnstimmig` statt eines Teilstands.
   Auch der Journal-Kopf muss vor und nach der Kopie sowie in der Kopie
   übereinstimmen: Ein beendeter oder neu begonnener Schreibvorgang verlangt
   einen neuen Versuch, statt Hauptdatei und falsches Journal zu verbinden.
4. Das WAL wird mit einer normalen Verbindung IN DER KOPIE eingespielt
   (`PRAGMA wal_checkpoint(TRUNCATE)`). Danach trägt schon die Hauptdatei der
   Kopie den ganzen Stand — auch für Leser, die nur sie weitergeben (yt-dlp).
   `PRAGMA quick_check` prüft anschließend die Struktur der Kopie. Eine beim
   Kopieren zerrissene Datenbank wird ebenfalls bis zu `VERSUCHE` Mal neu
   kopiert, bevor `KopieUnstimmig` den vorübergehenden Lesefehler meldet.
5. Nach dem Block ist die Kopie weg. Kopien des Browserverlaufs bleiben nicht
   im Temp liegen.

Das Original wird nie als Datenbank geöffnet, nur als Datei gelesen.

Diese Datei liegt BYTE-GLEICH in SyncFindus (`System/fremde_datenbank.py`, das
Original) und in SyncManga (`System/syncmanga/fremde_datenbank.py`). Geändert
wird nur das Original, danach die Kopie ersetzt; je Programm hält ein Wächter
die Zusagen und die Gleichheit fest.
"""
from __future__ import annotations

import contextlib
import os
import shutil
import sqlite3
import tempfile

#: Höchstens so viele Kopien bei wechselndem WAL/Journal oder beschädigter
#: Struktur. Jeder Versuch bekommt einen eigenen, vollständig frischen Ordner.
VERSUCHE = 3

#: Der WAL-Kopf: Magie, Format, Seitengrösse, Checkpoint-Nummer, Salz 1 und 2,
#: Prüfsumme. Ein Neubeginn ändert Checkpoint-Nummer und Salz.
WAL_KOPF_BYTES = 32


class KopieUnstimmig(OSError):
    """Keine in sich stimmige Kopie zustande gekommen — lieber laut als ein Teilstand."""


def _wal_kopf(pfad: str) -> bytes | None:
    """Erste 32 Bytes einer SQLite-Begleitdatei; auch Journal-Köpfe passen hinein."""
    try:
        with open(pfad, "rb") as f:
            return f.read(WAL_KOPF_BYTES)
    except FileNotFoundError:
        return None


def _stimmig_kopieren(quelle: str, ziel: str) -> bool:
    """Kopiert Hauptdatei samt Begleitdateien; True bei passenden Köpfen."""
    vorher = _wal_kopf(f"{quelle}-wal")
    journal_vorher = _wal_kopf(f"{quelle}-journal")
    shutil.copy(quelle, ziel)
    for endung in ("-wal", "-journal"):
        try:
            shutil.copy(f"{quelle}{endung}", f"{ziel}{endung}")
        except FileNotFoundError:
            pass                      # verschwunden: der Vergleich entscheidet
    return (_wal_kopf(f"{ziel}-wal") == vorher
            and _wal_kopf(f"{ziel}-journal") == journal_vorher
            and _wal_kopf(f"{quelle}-journal") == journal_vorher)


def _wal_einspielen(kopie: str) -> None:
    """Stellt Journal/WAL nur in der KOPIE wieder her und prüft ihre Struktur."""
    con = sqlite3.connect(kopie)
    try:
        con.execute("PRAGMA schema_version").fetchone()  # heißes Journal zurückspielen
        con.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        pruefung = con.execute("PRAGMA quick_check").fetchall()
        if pruefung != [("ok",)]:
            raise KopieUnstimmig("; ".join(str(zeile[0]) for zeile in pruefung))
    finally:
        con.close()


@contextlib.contextmanager
def lese_kopie(quelle):
    """Pfad einer privaten, vollständigen Kopie von `quelle`; danach ist sie weg.

    Die Kopie trägt den Dateinamen des Originals, allein in ihrem Ordner — der
    yt-dlp-Extraktor sucht `cookies.sqlite` im Profil-Ordner. Wirft den
    `OSError` des Kopierens oder `KopieUnstimmig`, nie einen stillen Teilstand.
    """
    quelle = os.fspath(quelle)
    with tempfile.TemporaryDirectory(prefix="lesekopie_") as ordner:
        letzter_fehler = "WAL oder Journal wechselten während der Kopie"
        for versuch in range(1, VERSUCHE + 1):
            os.mkdir(os.path.join(ordner, str(versuch)))
            kopie = os.path.join(ordner, str(versuch), os.path.basename(quelle))
            if not _stimmig_kopieren(quelle, kopie):
                letzter_fehler = "WAL oder Journal wechselten während der Kopie"
                continue
            try:
                _wal_einspielen(kopie)
            except (sqlite3.Error, KopieUnstimmig) as exc:
                letzter_fehler = str(exc)
                continue
            break
        else:
            raise KopieUnstimmig(
                f"Keine stimmige SQLite-Kopie nach {VERSUCHE} Versuchen: "
                f"{quelle}; {letzter_fehler}")
        yield kopie


@contextlib.contextmanager
def verbindung(quelle):
    """Verbindung auf `lese_kopie(quelle)`, geschlossen, bevor die Kopie verschwindet.

    Unter Windows liesse sich der Ordner mit offener Verbindung nicht räumen.
    """
    with lese_kopie(quelle) as kopie:
        con = sqlite3.connect(kopie)
        try:
            yield con
        finally:
            con.close()
