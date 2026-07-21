#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reader-Links aus den freien Sitemaps mehrerer Seiten finden -> data/series_overrides.json (off-peak).

EIN konfigurierbares Tool fuer alle Sitemap-Quellen (ersetzt die frueher 4 fast-gleichen Tools).
Jede Quelle in SITES beschreibt: woher der Sitemap kommt und wie daraus (slug -> Reader-URL) wird.
Pro Quelle wird die Map als persistente DB (data/<name>_map.json) gespeichert und bei jedem Lauf
erneuert; ist die Quelle nicht erreichbar (z.B. Cloudflare), wird die gespeicherte DB genutzt
(Offline-Matching). Gematcht wird ueber ALLE Titel-Varianten (entry_slugs -> auch Romaji-Slugs).
Reihenfolge in SITES = Prioritaet; nur Serien OHNE bestehenden Override werden gefuellt.

Aufruf:  python -m tools.discover_sitemap   (off-peak, NICHT waehrend eines Manga-Laufs)
"""
import gzip
import json
import os
import re
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.normpath(os.path.join(HERE, ".."))
if PKG not in sys.path:
    sys.path.insert(0, PKG)
from syncmanga.parse import norm  # noqa: E402
from syncmanga.readerlink import entry_slugs  # noqa: E402

CACHE = os.path.normpath(os.path.join(PKG, "..", "..", "SyncDashTray", "System", "md_cache.json"))
OV = os.path.join(PKG, "data", "series_overrides.json")
DATA = os.path.join(PKG, "data")
_UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0",
       "Accept-Encoding": "gzip"}


def _get(url):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=_UA), timeout=25) as r:
            raw = r.read()
            if r.headers.get("Content-Encoding") == "gzip":
                raw = gzip.decompress(raw)
            return raw.decode("utf-8", "replace")
    except Exception:
        return ""


def _undouble(base):
    """MangaFire-Slug-Basis ent-doppeln (one-piecee -> one-piece)."""
    return base[:-1] if len(base) > 1 and base[-1] == base[-2] else base


# -- pro Quelle: aus dem Sitemap-Text die (slug -> Reader-URL-Vorlage)-Paare ziehen --------------
def _pairs_mangafire(text):                                    # Serien-Seite (Kapitel = opake ID)
    # WURZELFIX 14.07.2026: das alte /read/{sid}/en/chapter-{n}-Schema ist seit dem
    # MangaFire-Umbau TOT (Redirect auf die Titelseite) — readerlink filtert solche Eintraege
    # beim Laden komplett raus, d.h. die 53k-Map war wirkungslos UND wurde hier jede Woche
    # wieder tot geschrieben. Jetzt: kanonische Serien-Seite /title/{id}-{slug} (live
    # verifiziert: /manga/{slug}.{id} -> 301 -> /title/{id}-{slug}); das exakte Kapitel
    # zieht die Ernte-Stufe (harvest_chapter_link) zur Laufzeit.
    for sid in re.findall(r"mangafire\.to/manga/([a-z0-9-]+\.[a-z0-9]+)", text):
        slug, fid = sid.rsplit(".", 1)
        yield _undouble(slug), f"https://mangafire.to/title/{fid}-{slug}"


def _pairs_mangaread(text):                                    # chapter-direkt
    for s in re.findall(r"/manga/([a-z0-9-]+)/chapter", text):
        yield s, f"https://www.mangaread.org/manga/{s}/chapter-{{n}}/"


def _pairs_weebcentral(text):                                  # Serien-Seite (Kapitel = ULID)
    for full, slug in re.findall(r"(weebcentral\.com/series/[A-Z0-9]+/([a-z0-9-]+))", text):
        yield slug, "https://" + full


def _pairs_roliascan(text):                                    # Serien-Seite (Kapitel = per-id)
    for s in re.findall(r"roliascan\.com/manga/([a-z0-9-]+)", text):
        yield s, f"https://roliascan.com/read/{s}/"


def _pairs_mgread(text):                                       # chapter-direkt, echtes 404
    for s in re.findall(r"mgread\.io/manga/([a-z0-9-]+)", text):
        yield s, f"https://mgread.io/manga/{s}/chapter-{{n}}/"


SITES = [
    # Reihenfolge = Prioritaet. MangaFire zuerst (groesster Katalog, chapter-direkt).
    {"name": "mangafire", "index": "https://mangafire.to/sitemap.xml",
     "sub_re": r"<loc>([^<]+sitemap-list[^<]+)</loc>", "pairs": _pairs_mangafire, "min": 1000, "workers": 12},
    {"name": "mangaread", "sitemap": "https://www.mangaread.org/wp-sitemap-posts-wp-manga-1.xml",
     "pairs": _pairs_mangaread, "min": 50},
    {"name": "weebcentral", "sitemap": "https://weebcentral.com/sitemap.xml",
     "pairs": _pairs_weebcentral, "min": 50},
    {"name": "roliascan", "sitemap": "https://roliascan.com/sitemap-manga.xml",
     "pairs": _pairs_roliascan, "min": 50},
    {"name": "mgread", "sitemap": "https://mgread.io/sitemap.xml", "pairs": _pairs_mgread, "min": 50},
]


def build_map(site):
    """slug -> Reader-URL-Vorlage fuer eine Quelle. Erfolgreich -> DB erneuern; sonst gespeicherte DB."""
    if site.get("index"):                                      # Index-Sitemap -> Sub-Sitemaps parallel
        subs = re.findall(site["sub_re"], _get(site["index"]))
        with ThreadPoolExecutor(max_workers=site.get("workers", 8)) as ex:
            text = "\n".join(ex.map(_get, subs))
    else:
        text = _get(site["sitemap"])
    m = {}
    for k, url in site["pairs"](text):
        m.setdefault(k, url)
    mapfile = os.path.join(DATA, f"{site['name']}_map.json")
    if len(m) >= site["min"]:                                  # plausibel gefuellt -> DB erneuern
        save_map(mapfile, m)
        return m
    db = load_map(mapfile)
    if db:
        print(f"  ({site['name']} nicht erreichbar - gespeicherte DB: {len(db)})", flush=True)
    return db


def load_map(mapfile):
    """Persistente Map lesen: komprimiert (.json.gz) bevorzugt, altes .json als Fallback (Migration)."""
    try:
        if os.path.exists(mapfile + ".gz"):
            with gzip.open(mapfile + ".gz", "rt", encoding="utf-8") as f:
                return json.load(f)
        return json.load(open(mapfile, encoding="utf-8"))
    except Exception:
        return {}


def save_map(mapfile, m):
    """Persistente Map KOMPRIMIERT speichern (~80% kleiner; mangafire allein war 5,5 MB).
    Ein altes unkomprimiertes .json wird nach erfolgreichem Schreiben entfernt (Migration)."""
    with gzip.open(mapfile + ".gz", "wt", encoding="utf-8") as f:
        json.dump(m, f, ensure_ascii=False)
    if os.path.exists(mapfile):
        os.remove(mapfile)


def main():
    try:
        c = json.load(open(CACHE, encoding="utf-8"))
    except Exception:
        c = {}
    try:
        data = json.load(open(OV, encoding="utf-8"))
    except Exception:
        data = {"overrides": {}}
    ov = data.get("overrides") or {}
    # Bestehende Keys NORMALISIERT vergleichen (Fix 14.07., 'dukependragon'-Dublette:
    # Roh-Keys wie 'Duke Pendragon, Master of ...' matchten norm(t) nie -> stilles Duplikat,
    # das sich beim Laden gegenseitig ueberschreibt).
    known = {norm(k) for k in ov}
    total = 0
    for site in SITES:
        print(f"{site['name']}: Sitemap laden ...", flush=True)
        m = build_map(site)
        found = 0
        for e in c.values():
            t = e.get("title")
            if not t or e.get("novel") or norm(t) in known:
                continue
            url = next((m[s] for s in entry_slugs(e) if s in m), None)
            if url:
                # Gespeicherte Alt-DBs koennen noch totes /read/-Schema tragen (Fallback bei
                # nicht erreichbarer Sitemap) -> beim Schreiben heilen, NIE tot eintragen.
                from syncmanga.readerlink import heal_read_scheme, is_dead_read_scheme
                if is_dead_read_scheme(url):
                    url = heal_read_scheme(url)
                    if not url:
                        continue
                ov[norm(t)] = {"name": t, "chapter": url, "trust": True, "auto": site["name"]}
                known.add(norm(t))
                found += 1
        total += found
        print(f"  {len(m)} Serien in DB, {found} neue Overrides.", flush=True)
    data["overrides"] = ov
    tmp = OV + ".tmp"                              # atomar schreiben -> nie eine halb geschriebene
    with open(tmp, "w", encoding="utf-8") as f:    # Datei; gefahrlos parallel zu einem Manga-Lauf.
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, OV)
    print(f"Fertig: {total} Sitemap-Overrides ergaenzt -> {OV}", flush=True)


if __name__ == "__main__":
    main()
