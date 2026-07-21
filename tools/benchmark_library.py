# -*- coding: utf-8 -*-
"""
Trefferquoten-Benchmark (JB: "zufaellige Bibliothek mit 1000 Titeln ueber 10 Jahre von
unterschiedlichen Quellen — wie hoch waere die Trefferquote?").

Baut eine TESTBIBLIOTHEK aus AniList — je Jahrzehnt-Fenster zwei Popularitaets-Stufen
(Top + Mittelfeld, dort wohnen die schweren Faelle) — und jagt jeden Titel durch UNSERE
Pipeline, exakt wie ein echter Lauf:
  1. catalog.lookup(titel)                -> Katalog-Match (conf, Quelle)
  2. readerlink.find_read_links(...)      -> verifizierter Lese-Link (Kapitel ODER Serien-Seite)

Gemessen wird:
  match  = Katalog-Treffer mit conf >= 0.62 (dieselbe Grenze wie needs_help im echten Lauf)
  link   = mindestens ein verifizierter Link (Kapitel-Genauigkeit separat ausgewiesen)

Aufruf:   python -m tools.benchmark_library [titel_gesamt=64] [link_stichprobe=32]
Ausgabe:  Konsole + data/benchmark_report.json (Verlauf vergleichbar halten).
Netz: alle Aufrufe laufen durch die normalen Pacer (MangaBaka/AniList/mangafire) — hoeflich,
aber deshalb dauert ein Lauf ein paar Minuten. NICHT parallel zu einem Voll-Sync starten.
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.normpath(os.path.join(HERE, ".."))
if PKG not in sys.path:
    sys.path.insert(0, PKG)

from syncmanga import catalog, readerlink  # noqa: E402
from syncmanga.common import post_json, use_utf8_stdio  # noqa: E402
from syncmanga.config import load_overrides  # noqa: E402
from syncmanga.readerlink import is_chapter_url  # noqa: E402

DATA = os.path.join(PKG, "data")
REPORT = os.path.join(DATA, "benchmark_report.json")
AL = "https://graphql.anilist.co"
_Q = """query($page:Int,$pp:Int,$ys:FuzzyDateInt,$ye:FuzzyDateInt){
Page(page:$page,perPage:$pp){media(type:MANGA,startDate_greater:$ys,startDate_lesser:$ye,
sort:POPULARITY_DESC,isAdult:false){title{english romaji}countryOfOrigin format}}}"""
# Jahrzehnt-Fenster x Popularitaets-Stufe (Seite 1 = Top, Seite 6 = Mittelfeld/Langschwanz)
BUCKETS = [("1985-1995", 19850101, 19951231), ("1996-2005", 19960101, 20051231),
           ("2006-2015", 20060101, 20151231), ("2016-2026", 20160101, 20261231)]
TIERS = [("top", 1), ("mittel", 6)]
# --tief (JB 14.07., 'mach es dir schwer'): Langschwanz statt Top — Popularitaets-Rang
# ~290-300 und ~700-720 je Jahrzehnt-Fenster (dort wohnen die vergessenen Archiv-Titel).
TIERS_TIEF = [("tief", 25), ("langschwanz", 60)]
CONF_OK = 0.62


def build_sample(total):
    """Testbibliothek: total Titel gleichmaessig ueber Jahrzehnte x Stufen (dedupliziert)."""
    per_cell = max(2, total // (len(BUCKETS) * len(TIERS)))
    out, seen = [], set()
    for bname, ys, ye in BUCKETS:
        for tname, page in TIERS:
            try:
                d = post_json(AL, {"query": _Q, "variables":
                                   {"page": page, "pp": per_cell, "ys": ys, "ye": ye}}, timeout=15)
                media = (((d.get("data") or {}).get("Page") or {}).get("media")) or []
            except Exception as ex:
                print(f"  ! Stichprobe {bname}/{tname}: {ex}")
                media = []
            for m in media:
                t = (m.get("title") or {}).get("english") or (m.get("title") or {}).get("romaji")
                if t and t.lower() not in seen:
                    seen.add(t.lower())
                    out.append({"title": t, "bucket": bname, "tier": tname,
                                "country": m.get("countryOfOrigin") or "?"})
            time.sleep(2.1)                     # AniList-Limit (~30/min)
    return out[:total]


def main():
    use_utf8_stdio()
    global TIERS
    args = [a for a in sys.argv[1:] if a != "--tief"]
    if "--tief" in sys.argv:
        TIERS = TIERS_TIEF
        print("Langschwanz-Modus: Popularitaets-Raenge ~290+/~710+ je Jahrzehnt.")
    total = int(args[0]) if len(args) > 0 else 64
    link_n = int(args[1]) if len(args) > 1 else 32
    load_overrides(os.path.join(DATA, "series_overrides.json"))
    readerlink.load_readers(os.path.join(DATA, "readers_pattern.json"))
    print(f"Benchmark: {total} Titel (Testbibliothek von AniList), Link-Stichprobe {link_n} ...")
    sample = build_sample(total)
    print(f"  {len(sample)} Titel gesammelt ({len(BUCKETS)} Jahrzehnte x {len(TIERS)} Stufen)")

    stats = {}
    for i, s in enumerate(sample):
        rec, conf, src = catalog.lookup(s["title"])
        s["conf"], s["src"] = round(conf, 2), src
        s["match"] = bool(rec) and conf >= CONF_OK
        s["rec_titles"] = ([rec.get("title_en"), rec.get("title_romaji")]
                           + (rec.get("alt_titles") or [])[:6]) if rec else []
        s["mtype"] = (rec.get("type") or "") if rec else ""
        key = (s["bucket"], s["tier"])
        st = stats.setdefault(key, {"n": 0, "match": 0})
        st["n"] += 1
        st["match"] += 1 if s["match"] else 0
        if (i + 1) % 16 == 0:
            print(f"  ... Katalog {i + 1}/{len(sample)}")

    # Link-Stichprobe: gleichmaessig ueber die Zellen (nicht nur die Top-Titel testen)
    probe = [s for pair in zip(sample[::2], sample[1::2], strict=False)
             for s in pair][:link_n] or sample[:link_n]
    link_ok = chap_ok = 0
    for i, s in enumerate(probe):
        titles = [t for t in ([s["title"]] + s.get("rec_titles", [])) if t]
        hits = readerlink.find_chapters(titles, 1, mtype=s.get("mtype") or None, limit=1)
        if not hits:
            # MD-RUECKLAGE wie die echte Pipeline (14.07.: der Benchmark unterschaetzte sie —
            # beide Langschwanz-Misses existierten auf MangaDex mit lesbarem EN). Gleicher
            # Waechter wie fill_one_reserves: Treffer-Titel muss norm-gleich/>=0.93 sitzen.
            try:
                import difflib

                from syncmanga.parse import norm as _norm
                from syncmanga.sources import md_chapter_link, md_lookup
                hit = md_lookup(s["title"]) or {}
                cand = [hit.get("title") or ""] + (hit.get("all_titles") or [])
                okt = any(h and (_norm(h) == _norm(s["title"]) or difflib.SequenceMatcher(
                    None, _norm(h), _norm(s["title"])).ratio() >= 0.93) for h in cand)
                if hit.get("md_id") and okt:
                    u, nm = md_chapter_link(hit["md_id"], 1)
                    if u:
                        hits = [(u, nm)]
            except Exception:
                pass
        s["link"] = bool(hits)
        if hits:
            link_ok += 1
            if is_chapter_url(hits[0][0]):     # zaehlt auch mangadex-/chapter/-UUIDs (14.07.)
                chap_ok += 1
        if (i + 1) % 8 == 0:
            print(f"  ... Links {i + 1}/{len(probe)}")

    n = len(sample) or 1
    match_total = sum(1 for s in sample if s["match"])
    print("\n=== Ergebnis ===")
    print(f"Katalog-Match: {match_total}/{n} = {100 * match_total // n}%")
    for (b, t), st in sorted(stats.items()):
        print(f"  {b} {t:6}: {st['match']}/{st['n']}")
    pn = len(probe) or 1
    print(f"Lese-Link:     {link_ok}/{pn} = {100 * link_ok // pn}%  "
          f"(davon kapitelgenau {chap_ok}, Serien-Seite {link_ok - chap_ok})")
    misses = [s["title"] for s in sample if not s["match"]][:15]
    if misses:
        print("Ohne Katalog-Match:", "; ".join(misses))
    try:
        json.dump({"ts": time.time(), "total": n, "match": match_total,
                   "link_probe": pn, "link_ok": link_ok, "chapter_exact": chap_ok,
                   "sample": sample},
                  open(REPORT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"Report -> {REPORT}")
    except OSError:
        pass


if __name__ == "__main__":
    main()
