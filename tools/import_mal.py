#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Import-Assistent (JB-Wunsch, Gegenrichtung zum ⤴-Export): eine MAL-XML (Export von MyAnimeList/
AniList — auch der Weg zurueck nach dem MangaBaka-Roundtrip, oder die Liste eines Freundes)
in die Leseliste einspielen. Unkompliziert: Datei nach Manga/data/import_mal.xml legen, Tool laeuft
(oder: python -m tools.import_mal pfad.xml).

Wirkung, zweigleisig:
  1. BEKANNTE Serien (via MAL-ID [persistiert seit v27] oder Titel): ist der importierte Lesestand
     WEITER als unserer, wird er als chapFix in data/list_state.json gemergt -> der SEED stellt ihn
     in jedem Browser her (Anzeige, Export, Aktion-Links folgen).
  2. UNBEKANNTE Serien: landen in data/imported_series.json -> der naechste Lauf zieht sie als
     normale Eintraege durch Match/Anreicherung/Render (Status uebersetzt: Reading->Am Lesen,
     Completed->Fertig, Plan to Read->Backlog).

Nicht-destruktiv: bestehende chapFix-/State-Eintraege werden nur ERHOEHT, nie gesenkt; die XML
wandert danach ins .done-Archiv. Aufruf:  python -m tools.import_mal [pfad.xml]
"""
import json
import os
import sys
import time
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.normpath(os.path.join(HERE, ".."))
if PKG not in sys.path:
    sys.path.insert(0, PKG)
from syncmanga.parse import norm  # noqa: E402

DATA = os.path.join(PKG, "data")
DEFAULT_XML = os.path.join(DATA, "import_mal.xml")
STATE = os.path.join(DATA, "list_state.json")
IMPORTED = os.path.join(DATA, "imported_series.json")
DEFAULT_CACHE = os.path.normpath(os.path.join(PKG, "..", "..", "SyncDashTray", "System", "md_cache.json"))

# MAL-Status -> unsere Scan-Status (FOLDER_STATUS-Vokabular; Plan to Read = Backlog via chap=None)
MAL_TO_STATUS = {"Reading": "Am Lesen", "Completed": "Fertig", "On-Hold": "Gelesen",
                 "Dropped": "Gelesen", "Plan to Read": "Gelesen"}


def parse_mal(xml_text):
    """MAL-XML -> [{'mal_id', 'title', 'chapters', 'status'}] (rein/testbar, tolerant)."""
    out = []
    root = ET.fromstring(xml_text)
    for m in root.iter("manga"):
        def g(tag, m=m):                      # m gebunden (B023-Haertung)
            el = m.find(tag)
            return (el.text or "").strip() if el is not None and el.text else ""
        try:
            mal_id = int(g("series_mangadb_id") or g("manga_mangadb_id") or 0) or None
        except ValueError:
            mal_id = None
        try:
            ch = float(g("my_read_chapters") or 0) or None
        except ValueError:
            ch = None
        title = g("series_title")
        if title or mal_id:
            out.append({"mal_id": mal_id, "title": title, "chapters": ch,
                        "status": g("my_status") or "Reading"})
    return out


def plan(entries, cache):
    """Import-Plan (rein/testbar): -> (fixes {key: kapitel}, neue [{key,name,chap,status}]).
    Bekannt = MAL-ID- oder Titel-Treffer im Cache; Fix nur, wenn der Import WEITER ist."""
    by_mal, by_title = {}, {}
    for k, v in cache.items():
        if not isinstance(v, dict):
            continue
        if v.get("mal_id"):
            by_mal[v["mal_id"]] = (k, v)
        for t in [v.get("title"), v.get("title_romaji")] + (v.get("alt_titles") or []):
            nt = norm(t or "")
            if nt:
                by_title.setdefault(nt, (k, v))
    fixes, new = {}, []
    for e in entries:
        hit = by_mal.get(e["mal_id"]) or by_title.get(norm(e["title"] or ""))
        if hit:
            k, v = hit
            ours = float(v.get("read_chap") or 0)
            if e["chapters"] and e["chapters"] > ours:
                fixes[k] = e["chapters"]
        elif e["title"]:
            key = norm(e["title"])
            if key:
                new.append({"key": key, "name": e["title"],
                            "chap": e["chapters"] if e["status"] != "Plan to Read" else None,
                            "status": MAL_TO_STATUS.get(e["status"], "Gelesen"),
                            "mal_id": e["mal_id"]})
    return fixes, new


def main():
    xml_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_XML
    if not os.path.exists(xml_path):
        print(f"Keine Import-Datei ({xml_path}) — nichts zu tun.")
        return
    cache = json.load(open(DEFAULT_CACHE, encoding="utf-8")) if os.path.exists(DEFAULT_CACHE) else {}
    entries = parse_mal(open(xml_path, encoding="utf-8").read())
    fixes, new = plan(entries, cache)

    # 1) Lesestaende -> list_state.json (SEED; nur erhoehen, vorhandene fremde Keys bleiben)
    state = json.load(open(STATE, encoding="utf-8")) if os.path.exists(STATE) else {}
    cf = json.loads(state.get("chapFix") or "{}")
    raised = 0
    for k, n in fixes.items():
        if n > float(cf.get(k) or 0):
            cf[k] = n
            raised += 1
    if raised:
        state["chapFix"] = json.dumps(cf, ensure_ascii=False)
        json.dump(state, open(STATE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    # 2) Unbekannte Serien -> imported_series.json (naechster Lauf reichert sie an)
    imported = json.load(open(IMPORTED, encoding="utf-8")) if os.path.exists(IMPORTED) else {}
    added = 0
    for e in new:
        if e["key"] not in imported:
            imported[e["key"]] = {"name": e["name"], "chap": e["chap"], "status": e["status"],
                                  "mal_id": e["mal_id"], "ts": time.time()}
            added += 1
    if added:
        json.dump(imported, open(IMPORTED, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    done = xml_path + f".done-{time.strftime('%Y%m%d-%H%M')}"
    os.replace(xml_path, done)
    print(f"Import: {len(entries)} Eintraege gelesen -> {raised} Lesestaende angehoben, "
          f"{added} neue Serien vorgemerkt (naechster Lauf reichert an). XML -> {os.path.basename(done)}")


if __name__ == "__main__":
    main()
