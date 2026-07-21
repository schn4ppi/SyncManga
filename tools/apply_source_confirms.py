#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quellen-Bestaetigungen verarbeiten (JB 07.07.2026, "1-Klick Quelle bestaetigen"):

Der ✔-Quelle-Knopf in der Liste exportiert `source_confirms.json` in der Form
    { norm_key: {"url": "...", "name": "Anzeigename", "site": "host"} , ... }
Lege die Datei nach Manga/data/source_confirms.json (der Knopf schickt sie zusaetzlich per POST an
den lokalen Server, wenn er laeuft) — dieses Tool schreibt jeden bestaetigten Direktlink FEST in
data/series_overrides.json (als {n}-Vorlage, "trust"+"pin"), sodass er ab dem naechsten Lauf der
verbindliche Weiterlesen-Link der Serie ist. Der Backfill (enrich.bake_overrides) zieht ihn dann in
den Cache — nie wieder "Alternative" fuer eine Serie, deren Quelle du bestaetigt hast.

Nicht-destruktiv: ergaenzt/aktualisiert nur den jeweiligen Serien-Eintrag, andere Overrides + der
_hinweis-Kommentar bleiben. Verarbeitete Meldungen wandern ins .done-Archiv (nicht doppelt anwenden).

Aufruf:  python -m tools.apply_source_confirms
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.normpath(os.path.join(HERE, ".."))
if PKG not in sys.path:
    sys.path.insert(0, PKG)

from syncmanga import config, readerlink  # noqa: E402
from syncmanga.parse import norm  # noqa: E402

CONFIRMS = os.path.join(PKG, "data", "source_confirms.json")
DONE = os.path.join(PKG, "data", "source_confirms.done.json")
OVERRIDES = os.path.join(PKG, "data", "series_overrides.json")
NAMEFIX = os.path.join(PKG, "data", "overrides.json")


def _load(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except ValueError:
        return default


def apply_confirms(confirms):
    """{key: {url|mb_id, name, site}} -> Anzahl geschriebener Overrides. Rein testbar (kein Datei-IO hier).

    mb_id -> MangaBaka-Ground-Truth-Pin in overrides.json (Metadaten). url -> Reader-Direktlink in
    series_overrides.json. Beides keyed auf norm(name) — genau danach sucht die Anreicherung."""
    written = 0
    for key, v in (confirms or {}).items():
        v = v if isinstance(v, dict) else {"url": v}
        name = v.get("name") or key
        if not name:
            continue
        if v.get("mb_id"):                          # MangaBaka-ID-Pin -> overrides.json (Metadaten)
            config.save_override(NAMEFIX, norm(name), name, mb_id=v["mb_id"])
            written += 1
        elif v.get("url"):                          # Reader-Direktlink -> series_overrides.json
            readerlink.save_series_override(OVERRIDES, name, name, v["url"])
            written += 1
    return written


def main():
    confirms = _load(CONFIRMS, {})
    if not confirms:
        print("Keine source_confirms.json in Manga/data — nichts zu tun.")
        return
    n = apply_confirms(confirms)
    print(f"{n} bestaetigte Quelle(n) in series_overrides.json geschrieben.")
    # ins .done-Archiv ueberfuehren (additiv), Eingang leeren
    done = _load(DONE, {})
    done.update({k: {**(v if isinstance(v, dict) else {"url": v}), "applied": time.strftime("%Y-%m-%d %H:%M")}
                 for k, v in confirms.items()})
    with open(DONE, "w", encoding="utf-8") as f:
        json.dump(done, f, ensure_ascii=False, indent=1)
    os.remove(CONFIRMS)
    print(f"Archiviert -> {os.path.basename(DONE)}; Eingang geleert.")


if __name__ == "__main__":
    sys.exit(main())
