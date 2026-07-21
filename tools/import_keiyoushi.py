#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Externe Reader-Quellen im GROSSEN Stil (JB Runde 38: "Hol extern mehr Quellen"):
Der Keiyoushi-Index (Nachfolger der Tachiyomi-Extensions, github.com/keiyoushi/extensions)
ist die umfassendste maschinenlesbare Reader-Liste (~2000 Quellen, ~500 englische).

Jeder englische Kandidat laeuft durch DIESELBE strenge Verifikation wie everythingmoe
(readerlink.discover: echtes Kapitel = 200, Muell-Slug = 404, Muell-Kapitel = 404 —
filtert Soft-404-Seiten). Nur bestandene Reader landen in data/readers_pattern.json
(merge, nie ersetzen). Fehlschlaege als manga werden als manhwa nachgeprobt.

Aufruf:  python -m tools.import_keiyoushi [pfad/zu/index.min.json] [--limit N]
OHNE Pfad wird der offizielle Index automatisch gezogen (JB 14.07.: „wenn eine mega gute
neue Seite erscheint, gucken wir dann bei einer Datenbank vorbei?" — ja, jetzt von selbst:
im woechentlichen refresh_overrides). Neue Reader-Seiten der Szene erscheinen dort zuerst.
"""
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.normpath(os.path.join(HERE, ".."))
if PKG not in sys.path:
    sys.path.insert(0, PKG)

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from syncmanga import readerlink  # noqa: E402
from syncmanga.config import UNSAFE_SITES, is_dead_reader, is_paywall_site  # noqa: E402
from syncmanga.parse import host as host_of  # noqa: E402

OUT = os.path.join(PKG, "data", "readers_pattern.json")
# Offizieller, maschinenlesbarer Quellen-Index (Nachfolger der Tachiyomi-Extensions).
INDEX_URL = "https://raw.githubusercontent.com/keiyoushi/extensions/repo/index.min.json"


def _load_index(path):
    """Index laden: lokale Datei ODER (ohne Pfad) Auto-Pull vom offiziellen Repo."""
    if path:
        return json.load(open(path, encoding="utf-8"))
    import urllib.request
    req = urllib.request.Request(INDEX_URL, headers={"User-Agent": "SyncManga"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def main():
    args = sys.argv[1:]
    limit = int(args[args.index("--limit") + 1]) if "--limit" in args else 0
    path = next((a for a in args if not a.startswith("--") and not a.isdigit()), "")
    index = _load_index(path)
    existing = list(readerlink.load_readers(OUT))
    known = {r["host"] for r in existing}
    cands, seen = [], set()
    for ext in index:
        for src in (ext.get("sources") or []):
            if src.get("lang") not in ("en",):
                continue
            h = host_of(src.get("baseUrl") or "")
            # Paywall-Filter (JB Runde 38): "Volume 1 frei, Rest kaufen"-Plattformen raus.
            # (Frueh-Zugang wie asurascans ist ok — steht nicht in PAYWALL_SITES.)
            if (not h or h in seen or h in known or is_dead_reader(h) or is_paywall_site(h)
                    or any(u in h for u in UNSAFE_SITES)):
                continue
            seen.add(h)
            cands.append({"name": src.get("name") or h, "host": h, "tags": [],
                          "category": "manga"})
    if limit:
        cands = cands[:limit]
    print(f"Keiyoushi: {len(cands)} neue EN-Kandidaten (bekannt/tot/unsicher gefiltert).",
          flush=True)
    found = readerlink.discover({"items": cands}, workers=14)
    ok_hosts = {r["host"] for r in found}
    print(f"  Pass 1 (manga): {len(found)} verifiziert.", flush=True)
    retry = [dict(c, category="manhwa") for c in cands if c["host"] not in ok_hosts]
    found2 = readerlink.discover({"items": retry}, workers=14)
    print(f"  Pass 2 (manhwa): {len(found2)} verifiziert.", flush=True)
    merged = readerlink.merge_readers(existing, found + found2)
    new = [r["host"] for r in merged if r["host"] not in known]
    readerlink.save_readers(OUT, merged)
    print(f"FERTIG: {len(merged)} Reader aktiv | neu: {new or '-'}", flush=True)


if __name__ == "__main__":
    main()
