#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Duplikat-Waechter (JB-Wunsch): findet Zeilen, die in Wahrheit DIESELBE Serie sind, und heilt sie.

Drei Klassen (Vorbild: 'I Picked Up This World's Strategy Guide' existierte doppelt):
  1. Fallback-Duplikat: ein Eintrag OHNE MangaBaka-ID, dessen Titel (normiert) exakt dem Titel
     eines Eintrags MIT MangaBaka-ID entspricht -> AUTO-PIN: der ID-lose Key bekommt einen
     mb_id-Override (overrides.json) und verschmilzt beim naechsten Lauf mit dem Zwilling.
  2. (nur Zaehler im Report) Gleiche mb_id unter mehreren CACHE-Keys ist NORMAL: JP-/EN-Varianten
     derselben Serie verschmelzen beim Rendern ueber die kanonische ID zu EINER Zeile.
  3. COVER-ZWILLINGE (JB 10.07.2026, Baum-Fall): identische Cover-URL, aber VERSCHIEDENE
     effektive IDs (Cache-ID nach angewandtem Override-Pin) -> dasselbe Bild kann kaum zwei
     Serien sein; meist ein Fehlmatch oder ein falscher Pin (Evolution Begins With A Big Tree
     zeigte per Alt-Pin auf die NOVEL-ID und blieb neben seinem Zwilling stehen). NUR Meldung
     im Report, NIE Auto-Pin — gleiche Artworks koennen legitim sein (Editionen/Spinoffs).

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
from syncmanga.parse import norm  # noqa: E402

DEFAULT_CACHE = os.path.normpath(os.path.join(PKG, "..", "..", "SyncDashTray", "System", "md_cache.json"))
OV = os.path.join(PKG, "data", "overrides.json")
REPORT = os.path.join(PKG, "data", "duplicate_report.json")


def _cover_url(v):
    """Cover-Feld normalisieren: mal String, mal Dict (Quellen-abhaengig) -> URL-String."""
    c = v.get("cover")
    if isinstance(c, dict):
        c = c.get("url") or c.get("large") or c.get("src") or ""
    return (c or "").strip() if isinstance(c, str) else ""


def cover_suspects(ent, ov):
    """Klasse 3 (rein/testbar): gleiche Cover-URL bei VERSCHIEDENEN effektiven IDs.

    Effektive ID = Override-Pin (baka/mb_id) falls vorhanden, sonst Cache-md_id — genau die
    Sicht, mit der der Render dedupliziert. Eintraege ohne Cover oder ohne jede ID zaehlen
    nicht (zu viel Rauschen). -> Liste [{cover, serien:{id: titel}}], nur Gruppen > 1 ID."""
    by_cover = {}
    for k, v in ent.items():
        cu = _cover_url(v)
        if not cu:
            continue
        fx = ov.get(k) or {}
        pin = fx.get("baka") or fx.get("mb_id")
        eff = f"mb:{pin}" if pin else str(v.get("md_id") or "")
        if not eff:
            continue
        by_cover.setdefault(cu, {})[eff] = v.get("title") or k
    return [{"cover": cu, "serien": ids}
            for cu, ids in sorted(by_cover.items()) if len(ids) > 1]


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
    suspects = cover_suspects(ent, ov)             # Klasse 3: nach den Auto-Pins = effektive Sicht
    json.dump({"ts": time.time(), "auto_pins": pinned, "cache_zwillinge_normal": n_groups,
               "cover_verdacht": suspects},
              open(REPORT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for p in pinned:
        print(f"  AUTO-PIN: {p['key'][:40]} -> mb:{p['mb_id']} ({p['titel']!r})")
    for sus in suspects:
        namen = " | ".join(f"{i}={t!r}" for i, t in sus["serien"].items())
        print(f"  COVER-VERDACHT (gleiches Bild, verschiedene IDs): {namen}")
    print(f"Duplikat-Waechter: {len(pinned)} Auto-Pins, {len(suspects)} Cover-Verdachtsfälle "
          f"({n_groups} Cache-Zwillinge = normal) -> {REPORT}")


if __name__ == "__main__":
    main()
