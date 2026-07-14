#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Titel-Bestaetigungen verarbeiten (JB-Wunsch D): der ✔-Knopf in der Liste exportiert
`title_confirms.json` ({key: 1, ...}). Lege die Datei nach Manga/data/title_confirms.json —
dieses Tool pinnt jede bestaetigte Serie FEST auf ihre aktuelle MangaBaka-ID (overrides.json
`mb_id`), damit der Match nie wieder kippen kann. Titel + mb_id kommen aus dem Cache
(autoritativ: das, was JB gesehen und bestaetigt hat). Verarbeitete Meldungen -> .done-Archiv.

In refresh_overrides.bat eingebunden (laeuft vor der Discovery). Nicht-destruktiv: ergaenzt nur
Overrides, ueberschreibt keine bestehenden Eintraege.

Aufruf:  python -m tools.apply_confirms [pfad/zu/md_cache.json]
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.normpath(os.path.join(HERE, ".."))
if PKG not in sys.path:
    sys.path.insert(0, PKG)

CONFIRMS = os.path.join(PKG, "data", "title_confirms.json")
DONE = os.path.join(PKG, "data", "title_confirms.done.json")
OV = os.path.join(PKG, "data", "overrides.json")
DEFAULT_CACHE = os.path.normpath(os.path.join(PKG, "..", "..", "SyncDashTray", "System", "md_cache.json"))


def main():
    if not os.path.exists(CONFIRMS):
        print("Keine title_confirms.json in Manga/data — nichts zu tun.")
        return
    cache_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CACHE
    confirms = json.load(open(CONFIRMS, encoding="utf-8"))
    cache = json.load(open(cache_path, encoding="utf-8")) if os.path.exists(cache_path) else {}
    ovdata = json.load(open(OV, encoding="utf-8")) if os.path.exists(OV) else {"overrides": {}}
    ov = ovdata.setdefault("overrides", ovdata if "overrides" not in ovdata else ovdata["overrides"])

    applied, skipped = [], []
    for key in confirms:
        # data-h ist seit Runde 35 ein STABILER Schluessel: "n:"+Cache-Key, eine DB-ID ("mb:123")
        # oder (Altbestand) norm(Anzeigetitel). Alle drei auf den Cache-Key aufloesen — der ist
        # zugleich der Override-Key (norm des Verlaufsnamens).
        ck = key[2:] if key.startswith("n:") else key
        c = cache.get(ck)
        if c is None and (key.startswith("mb:") or "-" in key):
            ck, c = next(((k2, v) for k2, v in cache.items()
                          if str(v.get("md_id") or "") == key), (key, None))
        c = c or {}
        mid = str(c.get("md_id") or "")
        if ck in ov:
            skipped.append((ck, "Override existiert schon"))
            continue
        if not mid.startswith("mb:"):
            skipped.append((ck, f"keine MangaBaka-ID im Cache ({mid or 'leer'})"))
            continue
        ov[ck] = {"mb_id": int(mid[3:]), "name": c.get("title") or ""}
        applied.append((ck, c.get("title")))

    if applied:
        json.dump(ovdata, open(OV, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    # verarbeitete Meldungen archivieren, Eingang leeren (nicht-destruktiv: Historie bleibt)
    hist = json.load(open(DONE, encoding="utf-8")) if os.path.exists(DONE) else []
    hist.append({"ts": time.time(), "applied": [k for k, _ in applied],
                 "skipped": [{"key": k, "warum": w} for k, w in skipped]})
    json.dump(hist, open(DONE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    os.remove(CONFIRMS)
    for k, t in applied:
        print(f"  gepinnt: {k} -> {t!r}")
    for k, w in skipped:
        print(f"  uebersprungen: {k} ({w})")
    print(f"apply_confirms: {len(applied)} gepinnt, {len(skipped)} uebersprungen.")


if __name__ == "__main__":
    main()
