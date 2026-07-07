#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Duplikat-Waechter (JB-Wunsch): findet Zeilen, die in Wahrheit DIESELBE Serie sind, und heilt sie.

Zwei Klassen (Vorbild: 'I Picked Up This World's Strategy Guide' existierte doppelt):
  1. Fallback-Duplikat: ein Eintrag OHNE MangaBaka-ID, dessen Titel (normiert) exakt dem Titel
     eines Eintrags MIT MangaBaka-ID entspricht -> AUTO-PIN: der ID-lose Key bekommt einen
     mb_id-Override (overrides.json) und verschmilzt beim naechsten Lauf mit dem Zwilling.
  2. (nur Zaehler im Report) Gleiche mb_id unter mehreren CACHE-Keys ist NORMAL: JP-/EN-Varianten
     derselben Serie verschmelzen beim Rendern ueber die kanonische ID zu EINER Zeile.

Nicht-destruktiv: ergaenzt nur Overrides (nie ueberschreiben), Report -> data/duplicate_report.json.
Im woechentlichen refresh_overrides.bat eingebunden. Aufruf: python -m tools.audit_duplicates [cache]
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.normpath(os.path.join(HERE, ".."))
if PKG not in sys.path:
    sys.path.insert(0, PKG)
from syncmanga.parse import norm                                 # noqa: E402

DEFAULT_CACHE = os.path.normpath(os.path.join(PKG, "..", "Core", "md_cache.json"))
OV = os.path.join(PKG, "data", "overrides.json")
REPORT = os.path.join(PKG, "data", "duplicate_report.json")


def main():
    cache_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CACHE
    cache = json.load(open(cache_path, encoding="utf-8"))
    ent = {k: v for k, v in cache.items() if isinstance(v, dict) and (v.get("title") or "").strip()}

    # Titel-Index der Eintraege MIT MangaBaka-ID
    by_title = {}
    for k, v in ent.items():
        mid = str(v.get("md_id") or "")
        if mid.startswith("mb:"):
            for t in [v.get("title"), v.get("title_romaji")] + (v.get("alt_titles") or []):
                nt = norm(t or "")
                if nt:
                    by_title.setdefault(nt, (k, int(mid[3:]), v.get("title")))

    ovdata = json.load(open(OV, encoding="utf-8")) if os.path.exists(OV) else {"overrides": {}}
    ov = ovdata.get("overrides", {})
    pinned, same_id = [], {}
    for k, v in ent.items():
        mid = str(v.get("md_id") or "")
        if mid.startswith("mb:"):
            same_id.setdefault(mid, []).append(k)
            continue
        hit = by_title.get(norm(v.get("title") or ""))
        if hit and k not in ov:                    # Klasse 1: Fallback-Zwilling -> Auto-Pin
            twin_key, twin_id, twin_title = hit
            ov[k] = {"mb_id": twin_id, "name": twin_title}
            pinned.append({"key": k, "titel": v.get("title"), "zwilling": twin_key, "mb_id": twin_id})
    n_groups = sum(1 for ks in same_id.values() if len(ks) > 1)   # normal (Render verschmilzt sie)

    if pinned:
        ovdata["overrides"] = ov
        json.dump(ovdata, open(OV, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"ts": time.time(), "auto_pins": pinned, "cache_zwillinge_normal": n_groups},
              open(REPORT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for p in pinned:
        print(f"  AUTO-PIN: {p['key'][:40]} -> mb:{p['mb_id']} ({p['titel']!r})")
    print(f"Duplikat-Waechter: {len(pinned)} Auto-Pins ({n_groups} Cache-Zwillinge = normal) -> {REPORT}")


if __name__ == "__main__":
    main()
