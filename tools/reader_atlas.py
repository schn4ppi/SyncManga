#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
READER-ATLAS (JB-Goal 14.07.2026: 'geh jede der 1900+ Mangaseiten durch').

Erforscht die ~2000 Reader-Quellen des Keiyoushi-Extension-Index NICHT einzeln von Hand,
sondern ueber ihre ENGINE: zehntausende Manga-Seiten weltweit laufen auf einer Handvoll
wiederverwendeter Themes (Madara/WordPress ~50+ Seiten, MangaThemesia ~30+, HeanCMS-SPA
mit echter JSON-API, ...). Wer die Engine kennt, kennt: HTML-Struktur, ob es eine DB/API
gibt, ob per Bot auslesbar, und ob eine ratbare/erntebare Kapitel-URL existiert.

Das Tool
  1. laedt den Keiyoushi-Index (Quelle der Wahrheit fuer 'ist es eine Mangaseite': ja — alle
     stehen im kuratierten Reader-Index; nsfw-Flag + lang kommen mit),
  2. fingerprintet jeden (oder eine Stichprobe) Host live gegen ENGINE_SIGS (parallel, hoeflich),
  3. leitet je Host ab: engine, hat_api (JSON-Endpoint erkannt), bot_lesbar (SSR-HTML mit
     Kapiteln ODER offene API vs. Cloudflare/JS-only), link_strategie (template/harvest/api/none),
  4. schreibt data/reader_atlas.json (Vollbestand) + eine Konsolen-Bilanz je Engine.

Aufruf:  python -m tools.reader_atlas [--limit N] [--lang en] [--full] [--workers 16]
         --full = alle Sprachen (Default: nur EN, das ist was JB liest).
Netz: strikt gepaced pro Host, ein Fehler killt nie den Lauf (modular-fusioniert).
"""
import concurrent.futures
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.normpath(os.path.join(HERE, ".."))
if PKG not in sys.path:
    sys.path.insert(0, PKG)
from syncmanga.parse import host as host_of                    # noqa: E402

INDEX_URL = "https://raw.githubusercontent.com/keiyoushi/extensions/repo/index.min.json"
OUT = os.path.join(PKG, "data", "reader_atlas.json")
_UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                     "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"}

# ---- Engine-Signaturen (aus Keiyoushi lib-multisrc + Live-Fingerprints) -----------------------
# Jede Engine: Marker im HTML/Header + Fakten fuer JBs Atlas. bot: wie gut per Skript auslesbar.
# link: wie wir daraus einen Kapitel-Link bekaemen. Reihenfolge = Prioritaet beim Matchen.
ENGINE_SIGS = [
    # name,          Regex-Marker (case-insensitive),                          api?,  bot,        link
    ("MangaDex-API", r"mangadex\.org|api\.mangadex",                           True,  "api",      "api"),
    ("Comick-API",   r"comick\.(io|fun|cc)|comick",                            True,  "api",      "api"),
    ("Madara",       r"wp-manga|madara|manga_get_chapters|reading-content",    False, "ssr",      "template/harvest"),
    ("MangaThemesia", r"ts_reader|mangathemesia|wp-content/themes/(ts|manga)",  False, "ssr",      "template/harvest"),
    ("HeanCMS",      r"heancms|/api/(query|chapter)|series_slug|__NEXT_DATA__", True,  "api",      "api"),
    ("Keyoapp",      r"keyoapp|/series/[a-z0-9]+/|data-uploads",               False, "ssr",      "harvest"),
    ("MangaReader-JS", r"reader-area|mangareader|chapter-images|ceo_latest",    False, "ssr",      "harvest"),
    ("FMReader",     r"fmreader|manga-reading|/manga-[a-z0-9-]+\.html",        False, "ssr",      "template"),
    ("Foolslide",    r"foolslide|/read/[^/]+/en/\d",                           True,  "api",      "api"),
    ("WPComics",     r"wpcomics|/truyen-tranh/|nettruyen",                     False, "ssr",      "template"),
    ("MCCMS",        r"mccms|maccms|dedecms",                                  False, "ssr",      "harvest"),
    ("Iken",         r"iken|/api/chapters|__next",                            True,  "api",      "api"),
    ("Zeistmanga",   r"zeistmanga|blogspot|blogger",                          False, "ssr",      "harvest"),
    ("Guya",         r"guya|/api/series/|/proxy/api/",                        True,  "api",      "api"),
    ("Madtheme",     r"madtheme|/ajax/image/list|reader-container",           False, "ssr",      "harvest"),
]
_CF = ("just a moment", "checking your browser", "cf-chl", "attention required",
       "enable javascript and cookies", "ddos-guard")


def load_index():
    req = urllib.request.Request(INDEX_URL, headers=_UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def _fetch(url, timeout=12, nbytes=220000):
    req = urllib.request.Request(url, headers=_UA)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return getattr(r, "status", 200), (r.geturl() or url), r.read(nbytes).decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, url, ""
    except Exception:
        return 0, url, ""


def classify(base_url):
    """Einen Host live fingerprinten -> Fakten-Dict (nie eine Exception)."""
    out = {"reachable": False, "status": 0, "engine": "unbekannt", "has_api": False,
           "bot": "unbekannt", "link": "none", "cloudflare": False, "note": ""}
    st, final, body = _fetch(base_url)
    out["status"] = st
    low = (body or "").lower()
    if st in (403, 503) or any(m in low[:8000] for m in _CF):
        out["cloudflare"] = True
        out["bot"] = "cf-blockiert"
        out["note"] = "Cloudflare/Bot-Schutz — nur mit Browser/Cookies"
        # Engine trotzdem raten (Marker stehen oft in der Challenge-Seite nicht -> bleibt unbekannt)
    if st == 0:
        out["note"] = "nicht erreichbar (Timeout/DNS/down)"
        return out
    out["reachable"] = st < 500
    for name, rx, api, bot, link in ENGINE_SIGS:
        if re.search(rx, body or "", re.I):
            out["engine"], out["has_api"], out["link"] = name, api, link
            if not out["cloudflare"]:
                out["bot"] = bot
            break
    # WordPress-Generator + Theme-Name (viele Madara-Derivate tragen keinen 'wp-manga'-Marker
    # auf der Startseite, aber ein 'generator: WordPress' + /wp-content/themes/<x>): als
    # WordPress-Reader fuehren (SSR, per Serienseite erntbar) statt 'unbekannt'.
    if out["engine"] == "unbekannt" and re.search(r"generator[^>]+WordPress|/wp-content/", body or "", re.I):
        th = re.search(r"/wp-content/themes/([a-z0-9_-]+)", body or "", re.I)
        out["engine"] = f"WordPress:{th.group(1)}" if th else "WordPress"
        if not out["cloudflare"]:
            out["bot"], out["link"] = "ssr", "harvest"
    # generische API-Erkennung, falls Engine unbekannt: liegt ein JSON-App-State/-Endpoint vor?
    if not out["has_api"] and re.search(r"__NEXT_DATA__|__NUXT__|application/json|/api/v?\d", body or "", re.I):
        out["has_api"] = True
        if out["bot"] in ("unbekannt", "ssr", "js-only?"):
            out["bot"] = "api"
            out["link"] = "api" if out["link"] == "none" else out["link"]
    # SSR-Manga-Signal: stehen Serien-/Kapitel-Pfade direkt im gelieferten HTML? (bot-lesbar)
    if not out["cloudflare"] and out["engine"] == "unbekannt":
        if re.search(r'href="[^"]*/(manga|series|title|read|comic|chapter)/', body or "", re.I):
            out["bot"] = "ssr"
            out["link"] = "harvest"
            out["note"] = "generische SSR-Mangaseite (Pfade im HTML)"
        elif out["reachable"] and len(body or "") > 2000:
            out["bot"] = "js-only?"
            out["note"] = "kein SSR-Manga-Signal — evtl. JS-App (API-Weg pruefen)"
    return out


def main(argv=None):
    args = list(argv if argv is not None else sys.argv[1:])
    full = "--full" in args
    lang = args[args.index("--lang") + 1] if "--lang" in args else "en"
    limit = int(args[args.index("--limit") + 1]) if "--limit" in args else 0
    workers = int(args[args.index("--workers") + 1]) if "--workers" in args else 16
    print("Reader-Atlas: Keiyoushi-Index laden ...", flush=True)
    idx = load_index()
    hosts, seen = [], set()
    for ext in idx:
        ext_nsfw = bool(ext.get("nsfw"))              # nsfw steht am EXTENSION-Knoten, nicht der Quelle
        for s in (ext.get("sources") or []):
            if not full and s.get("lang") not in (lang, "all"):
                continue
            h = host_of(s.get("baseUrl") or "")
            if not h or h in seen:
                continue
            seen.add(h)
            hosts.append({"host": h, "url": s["baseUrl"], "name": s.get("name") or h,
                          "lang": s.get("lang"), "nsfw": ext_nsfw})
    if limit:
        hosts = hosts[:limit]
    print(f"  {len(hosts)} eindeutige Hosts ({'alle Sprachen' if full else lang}) — fingerprinten "
          f"mit {workers} Workern ...", flush=True)
    t0 = time.time()
    done = [0]

    def work(h):
        info = classify(h["url"])
        done[0] += 1
        if done[0] % 50 == 0:
            print(f"  ... {done[0]}/{len(hosts)} ({int(time.time() - t0)}s)", flush=True)
        return {**h, **info}

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
        rows = list(ex.map(work, hosts))

    from collections import Counter
    by_engine = Counter(r["engine"] for r in rows)
    by_bot = Counter(r["bot"] for r in rows)
    reachable = sum(1 for r in rows if r["reachable"])
    api = sum(1 for r in rows if r["has_api"])
    cf = sum(1 for r in rows if r["cloudflare"])
    print("\n=== ATLAS-BILANZ ===", flush=True)
    print(f"Hosts gesamt {len(rows)} | erreichbar {reachable} | mit API {api} | Cloudflare {cf} "
          f"({int(time.time() - t0)}s)")
    print("Engines:")
    for name, n in by_engine.most_common():
        print(f"  {name:16} {n}")
    print("Bot-Auslesbarkeit:", dict(by_bot))
    json.dump({"ts": time.time(), "lang": ("all" if full else lang), "count": len(rows),
               "by_engine": dict(by_engine), "by_bot": dict(by_bot),
               "reachable": reachable, "api": api, "cloudflare": cf, "hosts": rows},
              open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"Atlas -> {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
