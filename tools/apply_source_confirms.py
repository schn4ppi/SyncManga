#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quellen-Bestaetigungen verarbeiten (JB 07.07.2026, "1-Klick Quelle bestaetigen"):

Der ✔-Quelle-Knopf in der Liste exportiert `source_confirms.json` in der Form
    { data_h: {"url": "...", "name": "Anzeigename", "site": "host"} , ... }
Der Schluessel ist data-h (stabiler Zeilen-Schluessel: DB-ID oder "n:"+Cache-Key) und wird ueber
md_cache.json auf den Cache-Key aufgeloest — genau danach sucht die Anreicherung.
Lege die Datei nach Manga/data/source_confirms.json (der Knopf schickt sie zusaetzlich per POST an
den lokalen Server, wenn er laeuft) — dieses Tool schreibt jeden bestaetigten Direktlink FEST in
data/series_overrides.json (als {n}-Vorlage, "trust"+"pin"), sodass er ab dem naechsten Lauf der
verbindliche Weiterlesen-Link der Serie ist. Der Backfill (enrich.bake_overrides) zieht ihn dann in
den Cache — nie wieder "Alternative" fuer eine Serie, deren Quelle du bestaetigt hast.

Nicht-destruktiv: ergaenzt/aktualisiert nur den jeweiligen Serien-Eintrag, andere Overrides + der
_hinweis-Kommentar bleiben; in overrides.json bleiben vorhandene Felder (baka, type, author ...)
erhalten. Opake Kapitel-IDs (mangafire /chapter/4807126, MangaDex-UUID) werden UNVERAENDERT gepinnt,
nie als {n}-Vorlage (One-Piece-Regel). Verarbeitete Meldungen wandern ins .done-Archiv.

Aufruf:  python -m tools.apply_source_confirms [pfad/zu/md_cache.json]
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
from syncmanga.enrich import cache_keys_for_h  # noqa: E402
from syncmanga.parse import norm  # noqa: E402

CONFIRMS = os.path.join(PKG, "data", "source_confirms.json")
DONE = os.path.join(PKG, "data", "source_confirms.done.json")
OVERRIDES = os.path.join(PKG, "data", "series_overrides.json")
NAMEFIX = os.path.join(PKG, "data", "overrides.json")
DEFAULT_CACHE = os.path.normpath(os.path.join(PKG, "..", "..", "SyncDashTray", "System", "md_cache.json"))


def _load(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except ValueError:
        return default


def resolve(key, v, cache):
    """data-h + Meldung -> (Cache-Key, Anzeigename). Befund 24.09.2026: frueher wurde unter
    norm(data-n) geschrieben — der kleingeschriebene Anzeigetitel weicht aber oft vom Cache-Key ab,
    dann steuerte der Pin das Matching nicht (und der Eintrag bekam den Kleinbuchstaben-Namen).
    Reihenfolge: data-h ueber den Cache, dann direkter Cache-Key, zuletzt norm(Name)."""
    cks = cache_keys_for_h(cache, key)
    ck = cks[0] if cks else (key[2:] if str(key).startswith("n:") else norm(v.get("name") or key))
    title = (cache.get(ck) or {}).get("title") or v.get("name") or ck
    return ck, title


def apply_confirms(confirms, cache=None, namefix=NAMEFIX, overrides=OVERRIDES):
    """{data_h: {url|mb_id, name, site}} -> Anzahl geschriebener Overrides. Rein testbar (Pfade/Cache
    einspeisbar).

    mb_id -> MangaBaka-Ground-Truth-Pin in overrides.json (Metadaten), vorhandene Felder bleiben.
    url -> Reader-Direktlink in series_overrides.json. Beides keyed auf den Cache-Key der Serie."""
    cache = cache or {}
    written = 0
    for key, v in (confirms or {}).items():
        v = v if isinstance(v, dict) else {"url": v}
        ck, title = resolve(key, v, cache)
        if not ck:
            continue
        if v.get("mb_id"):                          # MangaBaka-ID-Pin -> overrides.json (Metadaten)
            # Vorhandenen Namen/Suchbegriff behalten (kuratiert), sonst den Cache-Titel.
            old = config.load_overrides(namefix).get(ck) or {}
            config.save_override(namefix, ck, old.get("name") or title,
                                 search=old.get("search"), mb_id=v["mb_id"])
            written += 1
        elif v.get("url"):                          # Reader-Direktlink -> series_overrides.json
            url = v["url"]
            readerlink.save_series_override(overrides, ck, title, url,
                                            template=not readerlink.ist_opake_kapitel_id(url))
            written += 1
    return written


def main():
    confirms = _load(CONFIRMS, {})
    if not confirms:
        print("Keine source_confirms.json in Manga/data — nichts zu tun.")
        return
    cache = _load(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CACHE, {})
    n = apply_confirms(confirms, cache)
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
