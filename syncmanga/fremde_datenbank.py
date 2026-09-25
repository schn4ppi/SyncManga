# -*- coding: utf-8 -*-
"""Lese-Kopie einer fremden SQLite-Datenbank (Browser-Verlauf, Cookies) — samt WAL, in sich stimmig.

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
2. Hauptdatei und `-wal` kopieren. Das `-shm` braucht es nicht: Die erste
   Verbindung auf der Kopie baut den Index aus dem WAL neu auf.
3. Der WAL-Kopf wird VOR der Hauptdatei gelesen und mit dem der Kopie
   verglichen. Weicht er ab, hat der Browser das WAL dazwischen neu begonnen, und
   Hauptdatei und WAL passen nicht zusammen: Was der Checkpoint in die
   Hauptdatei geschrieben hat, stünde in keiner der beiden Kopien. Dann beginnt
   der Lauf in einem neuen Unterordner von vorn, höchstens `VERSUCHE` Mal —
   danach `KopieUnstimmig` statt eines Teilstands.
4. Das WAL wird mit einer normalen Verbindung IN DER KOPIE eingespielt
   (`PRAGMA wal_checkpoint(TRUNCATE)`). Danach trägt schon die Hauptdatei der
   Kopie den ganzen Stand — auch für Leser, die nur sie weitergeben (yt-dlp).
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

#: So oft darf der Browser das WAL während der Kopie neu beginnen, bevor der
#: Lesevorgang aufgibt. Jeder Neubeginn setzt einen vollständigen Checkpoint
#: voraus — schon zwei in derselben Sekunde sind ungewöhnlich.
VERSUCHE = 3

#: Der WAL-Kopf: Magie, Format, Seitengrösse, Checkpoint-Nummer, Salz 1 und 2,
#: Prüfsumme. Ein Neubeginn ändert Checkpoint-Nummer und Salz.
WAL_KOPF_BYTES = 32


class KopieUnstimmig(OSError):
    """Keine in sich stimmige Kopie zustande gekommen — lieber laut als ein Teilstand."""


def _wal_kopf(pfad: str) -> bytes | None:
    try:
        with open(pfad, "rb") as f:
            return f.read(WAL_KOPF_BYTES)
    except FileNotFoundError:
        return None


def _stimmig_kopieren(quelle: str, ziel: str) -> bool:
    """Kopiert Hauptdatei und -wal; True, wenn beide zum selben WAL-Stand gehören."""
    vorher = _wal_kopf(f"{quelle}-wal")
    shutil.copy(quelle, ziel)
    try:
        shutil.copy(f"{quelle}-wal", f"{ziel}-wal")
    except FileNotFoundError:
        pass                          # kein WAL (mehr): der Vergleich entscheidet
    return _wal_kopf(f"{ziel}-wal") == vorher


def _wal_einspielen(kopie: str) -> None:
    """Schreibt das mitkopierte WAL in die Hauptdatei der KOPIE."""
    con = sqlite3.connect(kopie)
    try:
        con.execute("PRAGMA wal_checkpoint(TRUNCATE)")
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
        for versuch in range(1, VERSUCHE + 1):
            os.mkdir(os.path.join(ordner, str(versuch)))
            kopie = os.path.join(ordner, str(versuch), os.path.basename(quelle))
            if _stimmig_kopieren(quelle, kopie):
                break
        else:
            raise KopieUnstimmig(
                f"Das WAL wurde während {VERSUCHE} Kopien neu begonnen: {quelle}")
        _wal_einspielen(kopie)
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
