#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Link-Sweep (JB 07.07.2026, R1+R2): haelt die Reader-Links im Cache gesund — NICHT-destruktiv.

Zwei Paesse:
  1) Schema-Pass (KEIN Netz, deterministisch): ein Primaerlink im TOTEN mangafire-/read/-Schema
     (leitet seit dem Umbau auf die Titelseite um) wird quarantaeniert -> die erste Reserve
     (= echter /title/-Verlaufslink) rueckt nach. Loest den ~737-fachen "Serienseite statt Kapitel".
  2) Health-Pass (Netz, gedeckelt, nur mit --deep): linkhealth klassifiziert den Primaerlink;
     SERIES_PAGE/GONE erst nach der ZWEITEN Messung (Hysterese) -> Quarantaene + Reserve.

Schreibt data/link_health.json (Zusammenfassung + Status je Serie) fuer die Anzeige (R7).
DRY-RUN ist Default; mit --apply werden die Aenderungen in den Cache geschrieben (Backup vorher).

Aufruf:  python -m tools.link_sweep [--apply] [--deep] [--cap 200]
"""
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.normpath(os.path.join(HERE, ".."))
if PKG not in sys.path:
    sys.path.insert(0, PKG)

from syncmanga import linkhealth as lh, readerlink, config   # noqa: E402


def find_cache():
    """Cache-Ort: Suite (Core/md_cache.json) oder Standalone (%LOCALAPPDATA%/SyncManga bzw. cwd)."""
    for p in (os.path.join(PKG, "..", "Core", "md_cache.json"),
              os.path.join(os.getcwd(), "cache", "md_cache.json"),
              os.path.join(os.getcwd(), "md_cache.json")):
        if os.path.exists(os.path.normpath(p)):
            return os.path.normpath(p)
    return os.path.normpath(os.path.join(PKG, "..", "Core", "md_cache.json"))


def sweep(cache, apply=False, deep=False, cap=200, check=None):
    """Reiner Sweep-Kern (Pass 2 nutzt `check`, in Tests injizierbar). Gibt (summary, status) zurueck."""
    check = check or lh.check_url
    schema_q = health_q = watched = 0
    # --- Pass 1: totes /read/-Schema (kein Netz) ---
    for e in cache.values():
        if not isinstance(e, dict):
            continue
        ru = e.get("read_urls") or []
        if ru and ru[0] and ru[0][0] and readerlink.is_dead_read_scheme(ru[0][0]):
            e["lh_status"] = "series_page"
            if apply:
                lh.quarantine_link(e, ru[0][0], "dead_read_scheme")
            schema_q += 1
    # --- Pass 2: Health-Check der Verdaechtigen (Netz, gedeckelt) ---
    if deep:
        todo = [e for e in cache.values()
                if isinstance(e, dict) and (e.get("read_urls")) and not e.get("novel")
                and (e.get("lh_fails", 0) > 0)][:cap]
        for e in todo:
            _v, action = lh.sweep_entry(e, check=check)
            health_q += action == "quarantined"
            watched += action == "watch"
    status = {"count": {"series_page": 0, "gone": 0, "blocked": 0, "down": 0}}
    for e in cache.values():
        st = isinstance(e, dict) and e.get("lh_status")
        if st in status["count"]:
            status["count"][st] += 1
    summary = {"schema_quarantined": schema_q, "health_quarantined": health_q, "watched": watched}
    return summary, status


def main():
    apply = "--apply" in sys.argv
    deep = "--deep" in sys.argv
    cap = 200
    if "--cap" in sys.argv:
        try:
            cap = int(sys.argv[sys.argv.index("--cap") + 1])
        except (IndexError, ValueError):
            pass
    config.apply_sources(config.load_sources(os.path.join(PKG, "data", "sources.json")))
    readerlink.load_overrides(os.path.join(PKG, "data", "series_overrides.json"))
    readerlink.load_readers(os.path.join(PKG, "data", "readers_pattern.json"))
    cache_path = find_cache()
    cache = json.load(open(cache_path, encoding="utf-8"))
    if apply:
        shutil.copy(cache_path, cache_path + ".bak-sweep-" + time.strftime("%Y%m%d-%H%M%S"))
    summary, status = sweep(cache, apply=apply, deep=deep, cap=cap)
    # Health-Bericht fuer die Anzeige (R7)
    report = {"ts": time.time(), "summary": summary, "count": status["count"],
              "series": {k: e["lh_status"] for k, e in cache.items()
                         if isinstance(e, dict) and e.get("lh_status")}}
    with open(os.path.join(PKG, "data", "link_health.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=1)
    if apply:
        tmp = cache_path + ".tmp"
        json.dump(cache, open(tmp, "w", encoding="utf-8"), ensure_ascii=False)
        os.replace(tmp, cache_path)
    mode = "ANGEWANDT" if apply else "DRY-RUN (nichts geschrieben; --apply zum Anwenden)"
    print(f"[{mode}]  Schema-tot: {summary['schema_quarantined']}  "
          f"Health-quarantaeniert: {summary['health_quarantined']}  beobachtet: {summary['watched']}")
    print(f"  Status-Zaehlung: {status['count']}")


if __name__ == "__main__":
    sys.exit(main())
