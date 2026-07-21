#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tote mangafire-/read/-Overrides regenerieren (JB-GO 14.07.2026: 'ich will keine toten
Links, ich will immer das Kapitel').

Hintergrund: Der MangaFire-Umbau hat das alte Kapitel-Schema /read/{slug}.{id}/en/chapter-{n}
getoetet (leitet per 200 auf die Titelseite um) — load_overrides ueberspringt diese Eintraege
seither, ~520 kuratierte Zuordnungen lagen brach. Die SERIEN-Zuordnung ({slug}.{id}) ist aber
weiterhin Gold wert: dieses Tool schreibt jeden /read/-Eintrag auf die KANONISCHE Serien-Seite
um (live verifiziert 14.07.: /manga/{slug}.{id} -> 301 -> /title/{id}-{slug}).

Warum Serien-SEITE statt Kapitel: das neue Schema traegt OPAKE Kapitel-IDs (nicht ratbar,
kein {n}-Template moeglich). Ein Seiten-Override ist der richtige Baustein: die Ernte-Stufe
(_harvest_pages/harvest_chapter_link) zieht daraus ZUR LAUFZEIT das exakte aktuelle Kapitel —
nichts veraltet; und seit der Kapitel-vor-Seite-Regel (14.07.) verdraengt die Seite nie einen
echten Kapitel-Link anderer Anbieter.

Verdikt je Eintrag (mangafire-freundlich gepaced, 1.2s):
  ok      = finale URL ist eine /title/-Seite -> kanonische URL uebernehmen.
  blocked = 403/429/503 (mangafire-Bot-Sperre, im Browser nutzbar — JB-verifiziert):
            kanonische Form LOKAL aus {slug}.{id} gebaut ({id} = Teil nach dem letzten Punkt).
  tot     = 200 ohne /title/-Ziel oder 404: Eintrag bleibt UNANGETASTET (harmlos, wird beim
            Laden eh uebersprungen) und wird gemeldet.

Nicht-destruktiv: datiertes Backup vor dem Schreiben, atomares Ersetzen, name/pin/trust der
Eintraege bleiben erhalten; tote Serien bleiben unangetastet. Schreiben ist DEFAULT (laeuft
unbeaufsichtigt im woechentlichen refresh_overrides als Schema-Wachposten); --probe zeigt nur.
Idempotent: nach der Regeneration matcht kein Eintrag mehr das /read/-Schema -> no-op.

Aufruf:  python -m tools.regen_read_scheme [--probe] [--limit N]
"""
import json
import os
import re
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.normpath(os.path.join(HERE, ".."))
if PKG not in sys.path:
    sys.path.insert(0, PKG)
from syncmanga.common import Pacer  # noqa: E402
from syncmanga.readerlink import fetch_status, is_dead_read_scheme  # noqa: E402

OV = os.path.join(PKG, "data", "series_overrides.json")
BACKUPS = os.path.join(PKG, "data", "backups")

_READ = re.compile(r"^https?://(?:www\.)?mangafire\.to/read/([^/]+)/", re.I)
_TITLE_FINAL = re.compile(r"^https?://(?:www\.)?mangafire\.to/title/[^/?#]+", re.I)
MF_PACER = Pacer(1.2)         # mangafire blockt schnelle Bots (403-Salven) -> hoeflicher Takt


def canonical_guess(slug_id):
    """{slug}.{id} -> lokal gebaute kanonische /title/{id}-{slug}-URL ('' wenn unlesbar)."""
    if "." not in slug_id:
        return ""
    slug, sid = slug_id.rsplit(".", 1)
    if not slug or not sid:
        return ""
    return f"https://mangafire.to/title/{sid}-{slug}"


def regen_one(tpl, fetch=None):
    """Ein totes /read/-Template -> (verdikt, serien_url). Rein bis auf den Netz-Abruf."""
    m = _READ.match(tpl or "")
    if not m:
        return "skip", ""
    slug_id = m.group(1)
    if fetch is None:                   # echtes Netz -> mangafire-hoeflich pacen
        MF_PACER.wait()
        fetch = lambda u: fetch_status(u, timeout=12, body_bytes=2000)   # noqa: E731
    st, final, _body = fetch(f"https://mangafire.to/manga/{slug_id}")
    if st == 200 and _TITLE_FINAL.match(final or ""):
        return "ok", (final or "").split("?")[0].rstrip("/")
    if st in (403, 429, 503):
        guess = canonical_guess(slug_id)
        return ("blocked", guess) if guess else ("tot", "")
    return "tot", ""


def main(argv=None):
    args = list(argv if argv is not None else sys.argv[1:])
    apply_ = "--probe" not in args
    limit = 0
    if "--limit" in args:
        try:
            limit = int(args[args.index("--limit") + 1])
        except (IndexError, ValueError):
            limit = 0
    try:
        data = json.load(open(OV, encoding="utf-8"))
    except Exception as e:
        print(f"series_overrides.json nicht lesbar: {type(e).__name__}: {e}", flush=True)
        return 1
    ov = data.get("overrides") or {}
    todo = [(k, v) for k, v in ov.items()
            if isinstance(v, dict) and is_dead_read_scheme(v.get("chapter") or "")]
    if limit:
        todo = todo[:limit]
    print(f"{len(todo)} Overrides im toten /read/-Schema"
          + ("" if apply_ else "  (PROBELAUF - nichts wird geschrieben)"), flush=True)
    stats = {"ok": 0, "blocked": 0, "tot": 0}
    t0 = time.time()
    for i, (k, v) in enumerate(todo, 1):
        verdikt, url = regen_one(v.get("chapter") or "")
        if verdikt == "skip":
            continue
        stats[verdikt] += 1
        if verdikt in ("ok", "blocked") and url:
            neu = dict(v)
            neu["chapter"] = url            # Serien-Seite ohne {n}: Ernte zieht das Kapitel
            neu["trust"] = True
            ov[k] = neu
        else:
            print(f"  tot gelassen: {k} ({v.get('name')})", flush=True)
        if i % 25 == 0:
            print(f"  ... {i}/{len(todo)} ({int(time.time() - t0)}s) "
                  f"ok={stats['ok']} blocked={stats['blocked']} tot={stats['tot']}", flush=True)
    print(f"Fertig geprueft: ok={stats['ok']} blocked={stats['blocked']} tot={stats['tot']} "
          f"({int(time.time() - t0)}s)", flush=True)
    if not apply_:
        print("PROBELAUF: nichts geschrieben.", flush=True)
        return 0
    if stats["ok"] + stats["blocked"] == 0:
        print("Nichts umzuschreiben.", flush=True)
        return 0
    os.makedirs(BACKUPS, exist_ok=True)
    ts = time.strftime("%Y%m%d-%H%M%S")
    shutil.copy(OV, os.path.join(BACKUPS, f"series_overrides-vor-regen-{ts}.json"))
    data["overrides"] = ov
    tmp = OV + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    os.replace(tmp, OV)
    print(f"Geschrieben: {stats['ok'] + stats['blocked']} Eintraege auf Serien-Seiten "
          f"umgestellt (Backup: backups/series_overrides-vor-regen-{ts}.json).", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
