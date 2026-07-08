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


def _entry_titles(e):
    """Titel-Kandidaten eines Cache-Eintrags fuer den Identitaets-Check (Soft-404-Reader brauchen ihn)."""
    return [t for t in (e.get("title_en"), e.get("title"), e.get("title_romaji")) if t] + \
           (e.get("alt_titles") or [])


def _owner_titles(cache, url):
    """Serie zu einer URL finden (read_urls/Quarantaene/Primaer) -> deren Titel, sonst None."""
    for e in cache.values():
        if not isinstance(e, dict):
            continue
        if (any(ln and ln[0] == url for ln in (e.get("read_urls") or []))
                or any(q.get("url") == url for q in (e.get("quarantine") or []))
                or e.get("read_url") == url):
            return _entry_titles(e) or None
    return None


def sweep(cache, apply=False, deep=False, cap=200, check=None, recheck_urls=None):
    """Reiner Sweep-Kern (Netz-Paesse nutzen `check`, in Tests injizierbar) -> (summary, status).

    Vier Paesse: 1) Schema (kein Netz)  2) Health der Verdaechtigen  3) SELBSTHEILUNG: Quarantaene
    erneut pruefen — als gesund verifizierte Links (ALIVE/MOVED) kommen ZURUECK an die Spitze
    (JB 08.07.2026: 'tote Links koennen vom System wiedergeholt werden'). Asymmetrie mit Absicht:
    VERURTEILEN braucht 2 Messungen (Hysterese), HEILEN nur eine — Irrtum kostet so nie einen Link.
    4) vom Nutzer gemeldete URLs (⚠/dud) verifizieren. Alle als gesund bestaetigten URLs landen in
    summary['alive_urls'] ({url: ts}) — das Signal, mit dem die Liste rote Striche selbst entfernt."""
    check = check or lh.check_url
    schema_q = health_q = watched = recovered = 0
    alive = {}
    now = int(time.time())
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
        # Kandidaten: Verdaechtige (lh_fails) + Serien, deren PRIMAER-Host gerade auto-pausiert
        # ist (JB 08.07.2026 'Ja' — die hingen beim mangahub-Ausfall fest, ohne je geprueft zu werden)
        def _suspect(e):
            if e.get("lh_fails", 0) > 0:
                return True
            u = e["read_urls"][0][0] if (e["read_urls"][0] and e["read_urls"][0][0]) else ""
            return bool(u) and config.is_paused_reader(lh.host_of(u))
        todo = [e for e in cache.values()
                if isinstance(e, dict) and (e.get("read_urls")) and not e.get("novel")
                and _suspect(e)][:cap]
        for e in todo:
            v, action = lh.sweep_entry(e, check=check)
            health_q += action == "quarantined"
            watched += action == "watch"
            if action == "ok" and v in (lh.Verdict.ALIVE, lh.Verdict.MOVED) and e.get("read_urls"):
                alive[e["read_urls"][0][0]] = now          # entwarnt -> Signal an die Liste
        # --- Pass 3 (Selbstheilung): quarantaenierte Links erneut pruefen -> gesund = zurueckholen ---
        qtodo = [e for e in cache.values() if isinstance(e, dict) and e.get("quarantine")][:RECOVER_CAP]
        for e in qtodo:
            titles = _entry_titles(e) or None
            for item in list(e.get("quarantine") or [])[:2]:       # je Serie max 2 (schonend)
                u = item.get("url")
                if not u:
                    continue
                if check(u, titles) in (lh.Verdict.ALIVE, lh.Verdict.MOVED):
                    alive[u] = now
                    if apply:
                        lh.restore_link(e, u)
                    recovered += 1
        # --- Pass 4: vom Nutzer gemeldete URLs (⚠/dud) verifizieren ---
        for u in list(dict.fromkeys(recheck_urls or []))[:60]:
            if u in alive:
                continue
            if check(u, _owner_titles(cache, u)) in (lh.Verdict.ALIVE, lh.Verdict.MOVED):
                alive[u] = now
    status = {"count": {"series_page": 0, "gone": 0, "blocked": 0, "down": 0}}
    for e in cache.values():
        st = isinstance(e, dict) and e.get("lh_status")
        if st in status["count"]:
            status["count"][st] += 1
    summary = {"schema_quarantined": schema_q, "health_quarantined": health_q, "watched": watched,
               "recovered": recovered, "alive_urls": alive}
    return summary, status


# ---------------- Regel-gesteuerter Auto-Sweep (Tray-Zyklus, JB 07.07.2026) ----------------
DEEP_EVERY_H = 20        # Regel 1: Deep-Pass (Netz) hoechstens ~1x taeglich
DEEP_CAP = 150           # Regel 2: max. gepruefte URLs je Deep-Pass (schonend, kein Hammer)
NET_PROBE = 15           # Regel 3: Netz-Gesundheit — unter den ersten 15 Checks ...
NET_BAD_MAX = 8          #          ... >= 8x DOWN/BLOCKED -> Abbruch (schlechtes Netz != tote Links)
RECOVER_CAP = 40         # Selbstheilung (JB 08.07.2026): max. Quarantaene-Serien je Deep-Pass re-checken
ALIVE_KEEP_S = 30 * 86400  # verifiziert-gesunde URLs 30 Tage als Signal merken (link_health.js/LHOK)


def _reported_urls(now):
    """Kuerzlich per ⚠ gemeldete URLs (broken_links.done.json-Historie) -> Verifikations-Pass 4.
    So bekommt jede Nutzer-Meldung ein ehrliches System-Verdikt: gesund -> die Liste entfernt den
    roten Strich von selbst; wirklich tot -> er bleibt."""
    hist = _load_json(os.path.join(PKG, "data", "broken_links.done.json"))
    if not isinstance(hist, list):
        hist = []
    urls = []
    for batch in hist:
        if not isinstance(batch, dict):
            continue
        bts = batch.get("ts") or 0
        for r in (batch.get("reports") or []):
            u = isinstance(r, dict) and r.get("url")
            ts = (r.get("ts") or 0) / 1000.0 if isinstance(r, dict) else 0   # Client schickt ms
            if u and now - max(ts, bts) <= ALIVE_KEEP_S:
                urls.append(u)
    return list(dict.fromkeys(urls))


def _merge_alive(prev, fresh, now):
    """alive_urls fortschreiben: alte Signale > 30 Tage verfallen, frische ueberschreiben."""
    out = {u: ts for u, ts in (prev.get("alive_urls") or {}).items()
           if isinstance(ts, (int, float)) and now - ts <= ALIVE_KEEP_S}
    out.update(fresh)
    return out


def _write_health(report, merged_alive):
    """link_health.json (Bericht) + link_health.js (LHOK — von der Liste ladbar, file://-sicher)."""
    report["alive_urls"] = merged_alive
    with open(os.path.join(PKG, "data", "link_health.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=1)
    with open(os.path.join(PKG, "data", "link_health.js"), "w", encoding="utf-8") as f:
        f.write("var LHOK=" + json.dumps(merged_alive, ensure_ascii=False) + ";")


class _NetAbort(Exception):
    """Deep-Pass abgebrochen: das Netz ist gerade unzuverlaessig (JB-No-Go: nie bei schlechtem
    Netz urteilen). Der naechste Lauf probiert es erneut."""


def _sane_check(counter):
    """check_url mit Netz-Gesundheits-Waechter umwickeln (Regel 3)."""
    def check(url, titles=None):
        v = lh.check_url(url, titles)
        counter["n"] += 1
        counter["bad"] += v in (lh.Verdict.DOWN, lh.Verdict.BLOCKED)
        if counter["n"] <= NET_PROBE and counter["bad"] >= NET_BAD_MAX:
            raise _NetAbort()
        return v
    return check


def auto_sweep(now=None):
    """Der Tray-Haken: Schema-Pass JEDEN Lauf (kein Netz, deterministisch); Deep-Pass nach Regeln.

    Regeln (JB 07.07.2026, 'bei jedem Start pruefen — aber mit Regeln'):
      1) Deep-Pass hoechstens alle DEEP_EVERY_H Stunden (Zeitstempel in data/link_health.json).
      2) Deckel DEEP_CAP URLs je Lauf (rotiert ueber lh_fails-Kandidaten; schont die Reader).
      3) Netz-Gesundheits-Abbruch: dominieren DOWN/BLOCKED die ersten Checks, wird abgebrochen
         und NICHTS geaendert — schlechtes Netz darf nie Links kosten (No-Go 05.07.).
      4) Nicht-destruktiv sowieso: Quarantaene statt Loeschen + 2x-Hysterese (linkhealth).
    Gibt das Summary-Dict zurueck (fuer Log/Tests)."""
    now = now or time.time()
    health_path = os.path.join(PKG, "data", "link_health.json")
    prev = _load_json(health_path)
    deep_due = (now - (prev.get("deep_ts") or 0)) >= DEEP_EVERY_H * 3600
    cache_path = find_cache()
    if not os.path.exists(cache_path):
        return {"skipped": "kein Cache"}
    cache = json.load(open(cache_path, encoding="utf-8"))
    shutil.copy(cache_path, cache_path + ".bak-autosweep")     # EIN rollierendes Backup je Lauf
    counter = {"n": 0, "bad": 0}
    aborted = False
    try:
        summary, status = sweep(cache, apply=True, deep=deep_due, cap=DEEP_CAP,
                                check=_sane_check(counter), recheck_urls=_reported_urls(now))
    except _NetAbort:
        aborted = True
        summary, status = sweep(cache, apply=True, deep=False)   # nur der netzlose Schema-Pass
    alive = summary.pop("alive_urls", {})                        # Signal separat (nicht doppelt im Report)
    report = {"ts": now, "deep_ts": (now if (deep_due and not aborted) else prev.get("deep_ts") or 0),
              "summary": summary, "count": status["count"], "net_abort": aborted,
              "series": {k: e["lh_status"] for k, e in cache.items()
                         if isinstance(e, dict) and e.get("lh_status")}}
    _write_health(report, _merge_alive(prev, alive, now))
    tmp = cache_path + ".tmp"
    json.dump(cache, open(tmp, "w", encoding="utf-8"), ensure_ascii=False)
    os.replace(tmp, cache_path)
    mode = "NETZ-ABBRUCH (nur Schema)" if aborted else ("deep" if deep_due else "schema-only")
    print(f"  [Auto-Sweep/{mode}] Schema-tot: {summary['schema_quarantined']}  "
          f"quarantaeniert: {summary['health_quarantined']}  beobachtet: {summary['watched']}  "
          f"selbstgeheilt: {summary['recovered']}", flush=True)
    return report


def _load_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


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
    now = time.time()
    prev = _load_json(os.path.join(PKG, "data", "link_health.json"))
    summary, status = sweep(cache, apply=apply, deep=deep, cap=cap,
                            recheck_urls=_reported_urls(now) if deep else None)
    alive = summary.pop("alive_urls", {})
    # Health-Bericht fuer die Anzeige (R7) + Selbstheilungs-Signal (LHOK)
    report = {"ts": now, "deep_ts": prev.get("deep_ts") or 0, "summary": summary,
              "count": status["count"],
              "series": {k: e["lh_status"] for k, e in cache.items()
                         if isinstance(e, dict) and e.get("lh_status")}}
    _write_health(report, _merge_alive(prev, alive, now))
    if apply:
        tmp = cache_path + ".tmp"
        json.dump(cache, open(tmp, "w", encoding="utf-8"), ensure_ascii=False)
        os.replace(tmp, cache_path)
    mode = "ANGEWANDT" if apply else "DRY-RUN (nichts geschrieben; --apply zum Anwenden)"
    print(f"[{mode}]  Schema-tot: {summary['schema_quarantined']}  "
          f"Health-quarantaeniert: {summary['health_quarantined']}  beobachtet: {summary['watched']}  "
          f"selbstgeheilt: {summary['recovered']}")
    print(f"  Status-Zaehlung: {status['count']}")


if __name__ == "__main__":
    sys.exit(main())
