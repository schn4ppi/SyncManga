#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reserve-Auffüller (JB Runde 37, MangaFire-Umbau): Serien, deren verifizierte Links alle
von EINEM Host stammen (822 Primärlinks waren mangafire — fällt der aus, bleiben 416
Serien ohne Direktlink), bekommen ZUSÄTZLICHE Reserven aus unabhängigen Quellen:

  1. MangaDex-API-Kapitel-Link (Ground-Truth, nie bot-blockiert) über die persistierte UUID
  2. Pattern-Reader + Sitemap-Treffer anderer Hosts (readerlink.find_chapters)

Chirurgisch + nicht-destruktiv: read_urls werden nur ERGÄNZT (ein Link je neuem Host),
read_urls[0]/read_url bleiben unangetastet. NICHT parallel zu einem Manga-Lauf starten
(beide schreiben md_cache.json).

Aufruf:  python -m tools.fill_reserves [--only-single-host mangafire] [--limit N]
"""
import io
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.normpath(os.path.join(HERE, ".."))       # Manga/
if PKG not in sys.path:
    sys.path.insert(0, PKG)

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from syncmanga import readerlink                                    # noqa: E402
from syncmanga.parse import host, norm                              # noqa: E402
from syncmanga.sources import md_chapter_link  # noqa: E402
from syncmanga.config import load_sources, apply_sources  # noqa: E402

CACHE = os.path.normpath(os.path.join(PKG, "..", "Core", "md_cache.json"))
LOCK = os.path.normpath(os.path.join(PKG, "..", "Core", "manga_update.lock"))


def _sim(a, b):
    import difflib
    return difflib.SequenceMatcher(None, norm(a), norm(b)).ratio()


def _md_reserve_cleanup(cache):
    """Frueher eingetragene MangaDex-RESERVEN nachpruefen (JB Runde 38): Pass 1 lief mit dem
    alten md_chapter_link (sprachloser Fallback + Serien-Seiten). Jede mangadex-Reserve wird
    EN-only neu berechnet: existiert das englische Kapitel -> URL ggf. ersetzen; sonst fliegt
    NUR die Reserve raus (read_urls[0] und alles andere bleibt unangetastet)."""
    fixed = dropped = 0
    for k, v in cache.items():
        if not isinstance(v, dict) or not v.get("read_urls"):
            continue
        urls = v["read_urls"]
        md_idx = [i for i, (u, _n) in enumerate(urls)
                  if u and i > 0 and "mangadex.org" in (host(u) or "")]
        if not md_idx or not v.get("mdx"):
            if md_idx:                                   # Reserve ohne UUID -> nicht pruefbar, raus
                v["read_urls"] = [x for i, x in enumerate(urls) if i not in set(md_idx)]
                dropped += len(md_idx)
            continue
        try:
            u_md, s_md = md_chapter_link(v["mdx"], v.get("read_chap") or 1, chapter_only=True)
        except Exception:
            continue
        keep = [x for i, x in enumerate(urls) if i not in set(md_idx)]
        if u_md:
            keep.append([u_md, s_md])
            fixed += 1
        else:
            dropped += 1
        v["read_urls"] = keep
    return fixed, dropped


def _single_host_targets(cache, needle):
    """Einträge, deren SÄMTLICHE read_urls vom needle-Host stammen (oder gar keine haben,
    aber eine MangaDex-UUID -> wenigstens die MD-Rücklage anhängen)."""
    out = []
    for k, v in cache.items():
        if not isinstance(v, dict) or v.get("novel"):
            continue
        urls = [u for u, _ in (v.get("read_urls") or []) if u]
        if urls and all(needle in (host(u) or "") for u in urls):
            out.append(k)
        elif not urls and v.get("mdx") and v.get("read_chap"):
            out.append(k)
    return out


def _fill_one(k, v):
    """Reserven für EINEN Cache-Eintrag — Kernlogik lebt jetzt im Paket (enrich.
    fill_one_reserves, JB Runde 40: läuft auch im regulären Lauf + Standalone)."""
    from syncmanga.enrich import fill_one_reserves
    return fill_one_reserves(v)


def main():
    if os.path.exists(LOCK):
        sys.exit("manga_update.lock existiert — erst den laufenden Lauf beenden lassen.")
    needle = "mangafire"
    if "--only-single-host" in sys.argv:
        needle = sys.argv[sys.argv.index("--only-single-host") + 1]
    limit = 0
    if "--limit" in sys.argv:
        limit = int(sys.argv[sys.argv.index("--limit") + 1])
    apply_sources(load_sources(os.path.join(PKG, "data", "sources.json")))
    readerlink.load_overrides(os.path.join(PKG, "data", "series_overrides.json"))
    readerlink.load_readers(os.path.join(PKG, "data", "readers_pattern.json"))
    cache = json.load(open(CACHE, encoding="utf-8"))
    fixed, dropped = _md_reserve_cleanup(cache)
    print(f"MD-Reserven-Bereinigung (EN-only): {fixed} bestaetigt/ersetzt, {dropped} entfernt.",
          flush=True)
    targets = _single_host_targets(cache, needle)
    if limit:
        targets = targets[:limit]
    print(f"{len(targets)} Serien haben nur {needle}-Links (oder gar keine + MD-UUID).", flush=True)
    done, added, t0 = 0, 0, time.time()

    def work(k):
        return k, _fill_one(k, cache[k])

    with ThreadPoolExecutor(max_workers=6) as ex:
        for k, new in ex.map(work, targets):
            done += 1
            if new:
                cache[k]["read_urls"] = (cache[k].get("read_urls") or []) + new
                if not cache[k].get("read_url"):
                    cache[k]["read_url"], cache[k]["read_site"] = new[0]
                added += 1
            if done % 25 == 0:
                tmp = CACHE + ".tmp"
                json.dump(cache, open(tmp, "w", encoding="utf-8"), ensure_ascii=False)
                os.replace(tmp, CACHE)
                print(f"  ... {done}/{len(targets)} geprüft, {added} ergänzt "
                      f"({int(time.time() - t0)}s)", flush=True)
    tmp = CACHE + ".tmp"
    json.dump(cache, open(tmp, "w", encoding="utf-8"), ensure_ascii=False)
    os.replace(tmp, CACHE)
    print(f"FERTIG: {done} geprüft, {added} Serien mit neuen Reserven.", flush=True)


if __name__ == "__main__":
    main()
