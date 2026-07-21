# -*- coding: utf-8 -*-
"""
everythingmoe-Reader-Verzeichnis — gepflegte, AKTUELL LEBENDE Lese-Seiten als gecachter Snapshot.

everythingmoe listet Reader je Sektion (manga/manhwa/database) und verlinkt sie via
`<a href="/s/<slug>" data-link="<live-url>">Name</a>` (+ `<span class="addtag">TAG</span>`),
wobei `data-link` immer auf die derzeit lebende Domain zeigt. Wir ernten Name->Live-URL+Tags,
cachen sie lokal (`data/readers_moe.json`) und nutzen sie fuer:
  - `live_hosts()`  : Seed fuer die Tot-Erkennung (kuratiert lebend) -> weniger Raten,
  - `alt_for(type)` : die ＋Alt-Liste je Veroeffentlichungsart.

Defensiv: liefert die Ernte 0 Treffer (Seitenumbau/Ausfall), bleibt der alte Snapshot bestehen.
Netzzugriff injizierbar (Tests), keine echten Calls in Tests.
"""
import json
import os
import time
import urllib.request

from .parse import host

SECTIONS = (
    ("manga", "https://everythingmoe.com/section/manga"),
    ("manhwa", "https://everythingmoe.com/section/manhwa"),
    ("database", "https://everythingmoe.com/section/database"),
)
# Tags, die als ＋Alt-Reader ungeeignet sind (Rohscans/Login/Print/Datenbank) — plus alles
# hinter einer PAYWALL (JB Runde 38: "Wichtig ist dass die Mangas hinter keiner paywall sind").
SKIP_TAGS = {"raw", "raw manhua", "login", "physical",
             "paid", "paywall", "subscription", "premium", "official", "coins", "points"}
REFRESH_DAYS = 7
_UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                     "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"}

import re

_ANCHOR = re.compile(
    r'<a\s+href="/s/([^"]*)"\s+data-link="([^"]+)"[^>]*>(?:\s*<img[^>]*>)?\s*([^<]+?)\s*</a>'
    r'(.*?)(?=<a\s+href="/s/|\Z)', re.S)
_TAG = re.compile(r'class="addtag">([^<]+)<')


def parse_section(html, category):
    """HTML einer Sektionsseite -> [{name,url,host,tags,slug,category}, ...]."""
    out = []
    for slug, url, name, tail in _ANCHOR.findall(html or ""):
        h = host(url)
        if not h:
            continue
        tags = [t.strip() for t in _TAG.findall(tail) if t.strip()]
        out.append({"name": name.strip(), "url": url, "host": h, "tags": tags,
                    "slug": slug, "category": category})
    return out


def _fetch(url, timeout=15):
    req = urllib.request.Request(url, headers=_UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def harvest(fetch=None, sections=SECTIONS):
    """Alle Sektionen ernten -> Liste (eine Quelle je host+category). Ausfall einer Sektion -> ueberspringen."""
    fetch = fetch or _fetch
    out, seen = [], set()
    for cat, url in sections:
        try:
            html = fetch(url)
        except Exception:
            continue
        for it in parse_section(html, cat):
            key = (it["host"], it["category"])
            if key in seen:
                continue
            seen.add(key)
            out.append(it)
    return out


def load(path):
    """Snapshot laden -> {'ts':..., 'items':[...]} (fehlt/kaputt -> leer)."""
    try:
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        if isinstance(d, dict) and isinstance(d.get("items"), list):
            return d
    except (OSError, ValueError):
        pass
    return {"ts": 0, "items": []}


def refresh_if_stale(path, days=REFRESH_DAYS, fetch=None, now=None, sections=SECTIONS):
    """Snapshot zurueckgeben; wenn aelter als `days`, neu ernten und speichern.

    Liefert die Ernte 0 Treffer (Seitenumbau/Ausfall), wird der alte Snapshot NICHT
    ueberschrieben (kein Datenverlust) und unveraendert zurueckgegeben.
    """
    now = now if now is not None else time.time()
    snap = load(path)
    if snap["items"] and (now - snap.get("ts", 0)) < days * 86400:
        return snap
    items = harvest(fetch, sections)
    if not items:
        return snap
    snap = {"ts": now, "items": items}
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(snap, f, ensure_ascii=False)
    except OSError:
        pass
    return snap


def live_hosts(snap):
    """Menge der kuratiert lebenden Reader-Hosts (Seed fuer die Tot-Erkennung)."""
    return {it["host"] for it in (snap.get("items") or []) if it.get("host")}


def alt_for(snap, mtype):
    """＋Alt-Reader fuer eine Veroeffentlichungsart -> [(name, url), ...].

    Nimmt die Reader der passenden Sektion (manhwa/manhua -> manhwa-Sektion, sonst manga),
    plus universelle Hubs; ueberspringt Roh-/Login-/Print-/Datenbank-Quellen.
    """
    want = "manhwa" if (mtype or "").lower() in ("manhwa", "manhua", "webtoon") else "manga"
    cats = [want, "manga"] if want != "manga" else ["manga"]   # typ-spezifisch zuerst, dann Hubs
    items = snap.get("items") or []
    out, seen = [], set()
    for cat in cats:
        for it in items:
            if it.get("category") != cat:
                continue
            if {t.lower() for t in it.get("tags", [])} & SKIP_TAGS:
                continue
            if it["host"] in seen:
                continue
            seen.add(it["host"])
            out.append((it["name"], it["url"]))
    return out


# ---------------- Status-Ampel der Lese-Seiten (frueher readercheck.py) ----------------
# Probt je Haupt-Host parallel eine bekannte Beispiel-URL -> data/reader_status.json:
#   ok          200                                  -> gruen  (funktioniert)
#   cloudflare  403 (Bot-Sperre, im Browser nutzbar) -> gelb
#   maintenance 503/Wartungsseite                    -> orange
#   down        Timeout/Verbindungsfehler/5xx        -> rot
# KEIN Bild-Check hier: die Haupt-Hosts (MangaFire, mangaread) laden Bilder per JS -> das HTML
# ist bilderlos, obwohl die Seite funktioniert. Wird vor jedem Render aufgerufen (best-effort).

STATUS_OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data",
                          "reader_status.json")

# (Anzeigename, Host, Beispiel-URL) — KERN-Checks mit praezisen Tiefen-URLs (aussagekraeftiger
# als ein Root-Ping). Die Ampel selbst ist seit 08.07.2026 DYNAMISCH (ampel_targets): sie zeigt
# immer die Seiten mit den MEISTEN Serien in der Liste; diese Kern-Checks liefern dafuer die
# besseren Pruef-URLs und ergaenzen hinten, falls die Liste einen Kern-Host kaum nutzt.
READERS = [
    ("MangaFire", "mangafire.to", "https://mangafire.to/read/one-piecee.dkw/en/chapter-1"),
    ("comix.to", "comix.to", "https://comix.to/title/mnwgy-inspectre"),
    ("weebcentral", "weebcentral.com",
     "https://weebcentral.com/series/01J76XYC6TC9WBY9EH2KVHFDHA/Grancrest-Senki"),
    ("roliascan", "roliascan.com", "https://roliascan.com/read/volcanic-age/"),
    ("mangaread", "mangaread.org",
     "https://www.mangaread.org/manga/accomplishments-of-the-dukes-daughter/chapter-1/"),
    ("MangaDex", "mangadex.org", "https://api.mangadex.org/ping"),
    ("Webtoons", "webtoons.com", "https://www.webtoons.com/en/"),
    ("arenascan", "arenascan.com", "https://arenascan.com/the-housekeeper-in-the-dungeon-24/"),
]

AMPEL_MAX = 14           # so viele Seiten zeigt die Ampel hoechstens (JB 08.07.2026: "mehr!")


def _cache_host_counts(cache_path=None):
    """Serien je Host (PRIMAERLINK) aus dem Cache zaehlen -> Counter. Best-effort, wirft nie.
    Das ist JBs Mass fuer die Ampel: 'immer die Seiten mit den meisten Serien in der Liste'."""
    from collections import Counter
    here = os.path.dirname(os.path.abspath(__file__))
    cands = [cache_path] if cache_path else [
        os.path.join(here, "..", "..", "..", "SyncDashTray", "System", "md_cache.json"),
        os.path.join(os.getcwd(), "cache", "md_cache.json"),
        os.path.join(os.getcwd(), "md_cache.json")]
    ct = Counter()
    for p in cands:
        p = os.path.normpath(p or "")
        if not p or not os.path.exists(p):
            continue
        try:
            cache = json.load(open(p, encoding="utf-8"))
        except (OSError, ValueError):
            return ct
        for e in cache.values():
            if not isinstance(e, dict) or e.get("novel"):
                continue
            ru = e.get("read_urls") or []
            h = host(ru[0][0]) if ru and ru[0] and ru[0][0] else ""
            if h.startswith("www."):
                h = h[4:]
            if h:
                ct[h] += 1
        break
    return ct


def ampel_targets(cache_path=None, cap=AMPEL_MAX):
    """[(Name, Host, Pruef-URL, Serienzahl)] fuer die Ampel: Top-Hosts nach Serienzahl in DEINER
    Liste zuerst (JB 08.07.2026), dann die Kern-Checks, die noch fehlen. Tote Hosts nie."""
    from . import config
    ct = _cache_host_counts(cache_path)
    fixed = {h: (n, u) for n, h, u in READERS}
    out, seen = [], set()
    for h, n_series in ct.most_common():
        if len(out) >= cap:
            break
        if not h or config.is_dead_reader(h):
            continue
        name, url = fixed.get(h, (h, f"https://{h}/"))
        out.append((name, h, url, n_series))
        seen.add(h)
    for n, h, u in READERS:                     # Kern hinten anfuegen, falls Platz
        if h not in seen and len(out) < cap:
            out.append((n, h, u, ct.get(h, 0)))
            seen.add(h)
    return out


# Bekannt Cloudflare-/Bot-geschuetzte Hosts: der automatische Host-Root-Check ist hier
# UNZUVERLAESSIG (503/Bot-Challenge, obwohl die Seite im Browser laeuft — JB-Saga MangaFire).
# Fuer diese Hosts wird ein 503/Wartung/timeout NICHT als Ausfall gewertet (also keine
# Auto-Pause), sondern als 'cloudflare' (gelb, im Browser nutzbar). Echte Kapitel-Link-
# Brueche fangen weiterhin der Link-Sweep + Redirect-/Identity-Checks pro URL ab.
BOT_FRONTED = {"mangafire.to"}


def _classify_status(url, host=""):
    from .readerlink import fetch_status
    st, _final, body = fetch_status(url, timeout=8)
    low = (body or "").lower()[:6000]
    cf = any(m in low for m in ("just a moment", "attention required", "checking your browser",
                                "cf-ray", "cloudflare"))
    maint = any(m in low for m in ("under maintenance", "site maintenance", "be right back",
                                   "wartung", "temporarily down for maintenance", "down for maintenance"))
    # 1) Cloudflare/Bot-Abweisung (im Browser nutzbar) -> gelb
    if st in (400, 401, 403, 406, 429) or cf:
        return "cloudflare", "Cloudflare/Bot-Sperre - im Browser nutzbar"
    # Bot-geschuetzte Hosts: ein 503/Wartung/timeout am Root ist unzuverlaessig -> gelb statt
    # Auto-Pause (nicht-destruktiv, JB-Regel: nie einen Host pausieren, der im Browser laeuft).
    bot = any(host.endswith(b) or b in (host or "") for b in BOT_FRONTED)
    if bot and (st == 503 or maint or st == 0 or st >= 500):
        return "cloudflare", "Bot-/Cloudflare-Schutz - im Browser nutzbar (Root nicht pruefbar)"
    # 2) Wartung / kurzzeitig nicht verfuegbar (503 oder Wartungs-Seite) -> orange, spaeter erneut
    if st == 503 or maint:
        return "maintenance", "Wartung / kurz nicht verfuegbar - spaeter erneut versuchen"
    # 3) Cloudflare meldet den Origin-Server als nicht erreichbar (52x) -> rot
    if 520 <= st <= 527:
        return "down", "Cloudflare meldet: Server der Seite nicht erreichbar"
    if st == 0 or st >= 500:
        return "down", "nicht erreichbar"
    if st != 200:
        return "down", f"HTTP {st}"
    return "ok", "funktioniert"


def link_sweep(cache_path, data_dir, n=25, check=None, status_out=STATUS_OUT):
    """Stichproben-Sweep der Primaerlinks (JB Runde 39, Idee 1 — Taktung: je 6h-Sync 25
    Zufalls-Links => der ganze Bestand ist ~woechentlich einmal durchgeprueft, +25 Requests
    je Sync, bewusst hoeflich).

    Echte Ausfaelle (Status 'no' = 404/Redirect-weg) werden als ⚠-Meldung in
    data/broken_links.json eingereiht -> der NAECHSTE Lauf repariert sie ueber den
    bestehenden Reparatur-Weg (enrich._consume_broken). Brechen >=3 Links DERSELBEN
    Domain in einer Stichprobe, wird die Domain zusaetzlich AUTO-pausiert (Anzeige zeigt
    Reserven). 'blocked'/'odd' (Cloudflare & Co.) zaehlen NIE als Ausfall; trust-Overrides
    und bereits pausierte/tote Hosts werden uebersprungen. Best-effort, nie eine Exception."""
    import random
    from collections import Counter as _Counter

    from . import config
    from .readerlink import _alive_status
    try:
        cache = json.load(open(cache_path, encoding="utf-8"))
    except Exception:
        return None
    pool = [(k, v["read_urls"][0][0]) for k, v in cache.items()
            if isinstance(v, dict) and not v.get("ov") and not v.get("novel")
            and v.get("read_urls") and v["read_urls"][0] and v["read_urls"][0][0]]
    random.shuffle(pool)
    chk = check or _alive_status
    fails, per_host, checked = [], _Counter(), 0
    for k, u in pool:
        if checked >= n:
            break
        h = host(u)
        if not h or config.is_paused_reader(h) or config.is_dead_reader(h):
            continue
        try:
            st = chk(u)
        except Exception:
            continue
        checked += 1
        if st == "no":
            fails.append({"name": cache[k].get("title") or k, "url": u, "ts": 0})
            per_host[h] += 1
    if fails:
        # in den bestehenden Reparatur-Eingang einreihen (vereint, dedupe nach Name)
        p = os.path.join(data_dir, "broken_links.json")
        try:
            old = json.load(open(p, encoding="utf-8"))
            if not isinstance(old, list):
                old = []
        except (OSError, ValueError):
            old = []
        seen = {r.get("name") for r in old if isinstance(r, dict)}
        merged = old + [f for f in fails if f["name"] not in seen]
        tmp = p + ".tmp"
        json.dump(merged, open(tmp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        os.replace(tmp, p)
    burst = sorted(h for h, c in per_host.items() if c >= 3)
    if burst:
        # Ausfall-Muster einer Domain -> Auto-Pause ERGAENZEN (reader_status.json + live)
        from . import config as _c
        try:
            data = json.load(open(status_out, encoding="utf-8"))
        except Exception:
            data = {}
        auto = sorted(set(data.get("auto_paused") or []) | set(burst))
        data["auto_paused"] = auto
        try:
            tmp = status_out + ".tmp"
            json.dump(data, open(tmp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
            os.replace(tmp, status_out)
        except Exception:
            pass
        _c.set_auto_paused(auto)
    if fails or burst:
        print(f"  [Link-Sweep] {checked} geprüft, {len(fails)} Ausfälle -> Reparatur"
              + (f", AUTO-PAUSE: {', '.join(burst)}" if burst else ""), flush=True)
    return checked, len(fails), burst


def refresh_status(out=STATUS_OUT, workers=8, cache_path=None):
    """Die Ampel-Seiten parallel pruefen, data/reader_status.json schreiben, dict zurueckgeben.
    Seit 08.07.2026 dynamisch: gezeigt/geprueft werden die Seiten mit den meisten Serien in der
    Liste (ampel_targets); 'n' = Serienzahl wandert mit in die Anzeige."""
    from concurrent.futures import ThreadPoolExecutor

    def one(r):
        name, hostn, url, n = r
        status, note = _classify_status(url, hostn)
        return hostn, {"name": name, "status": status, "note": note, "n": n}

    with ThreadPoolExecutor(max_workers=workers) as ex:
        readers = dict(ex.map(one, ampel_targets(cache_path)))
    # AUTO-PAUSE (JB Runde 38, Feature 1) mit HYSTERESE (Runde 42): pausiert wird erst nach
    # ZWEI aufeinanderfolgenden down/maintenance-Messungen (ein einzelner Flacker beim
    # 10-Minuten-Check togglet sonst die Links hin und her); aufgehoben wird SOFORT bei 'ok'
    # (schnelle Heilung). Manuelle Pausen (sources.json) bleiben davon unberuehrt.
    try:
        prev = json.load(open(out, encoding="utf-8"))
    except Exception:
        prev = {}
    prev_bad = {h for h, r in (prev.get("readers") or {}).items()
                if isinstance(r, dict) and r.get("status") in ("down", "maintenance")}
    prev_auto = set(prev.get("auto_paused") or [])
    bad_now = {h for h, r in readers.items() if r.get("status") in ("down", "maintenance")}
    auto = sorted((bad_now & (prev_bad | prev_auto)))    # 2x schlecht ODER schon pausiert
    data = {"checked": time.strftime("%Y-%m-%d %H:%M"), "readers": readers,
            "auto_paused": auto}
    from . import config
    config.set_auto_paused(auto)
    if auto:
        print(f"  [Reader-Check] AUTO-PAUSE (down/Wartung): {', '.join(auto)}", flush=True)
    try:
        with open(out, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass
    return data
