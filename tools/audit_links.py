#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Woechentlicher Link-Audit (off-peak, NICHT waehrend eines Manga-Laufs): prueft die gespeicherten
"weiterlesen"-Links ALLER Serien erneut — inkl. Redirect-Ziel- und IDENTITAETS-Check (fuehrt der
Link noch zu DIESER Serie?). Nicht-destruktiv/selbstheilend:

  - Ein nachweislich toter Hauptlink ("no", "gone" bei funktionierendem Netz) wird erst beim
    ZWEITEN Audit in Folge verurteilt (linkhealth.decide, Zaehler `audit_tot` je Adresse).
  - Dann wandert er per linkhealth.quarantine_link in die Quarantaene des Eintrags: die
    Ersatzlinks bleiben, der naechste rueckt nach; read_chap=None laesst den naechsten Lauf
    frisch verifizieren. Der Verlaufs-Pass (enrich.promote_history_chapters) holt eine Adresse
    in Quarantaene nicht zurueck.
  - Nach 30 Tagen wird jede Quarantaene-Adresse einmal neu geprueft: "ok" gibt sie frei (sie
    kommt NICHT automatisch nach vorn), weiter tot erneuert den Zeitstempel.
  - blocked/down gelten als nicht pruefbar, "odd" (fremde Serie oder Drosselseite) wird nur
    gezaehlt; beides verurteilt nie und setzt den Zaehler zurueck.

Befund 25.11.2026, warum nicht mehr leeren: Der Audit setzte read_url und ALLE read_urls leer und
merkte sich nichts. Beim naechsten Listenbau holte der Verlaufs-Pass dieselbe tote Adresse aus
JBs Verlauf zurueck (Dur-An-Ki, Maerchen Crown, Planetes auf mangabolt.com: am 22.11. geleert,
am 25.11. wieder vorn). Report -> data/link_audit.json.

Aufruf:  python -m tools.audit_links [pfad/zu/md_cache.json] [--limit N]
Default-Cache: ../../SyncDashTray/System/md_cache.json (JBs Vollsuite).
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.normpath(os.path.join(HERE, ".."))
if PKG not in sys.path:
    sys.path.insert(0, PKG)
from syncmanga import linkhealth, readerlink  # noqa: E402
from syncmanga.common import json_aendern  # noqa: E402

DEFAULT_CACHE = os.path.normpath(os.path.join(PKG, "..", "..", "SyncDashTray", "System", "md_cache.json"))
REPORT = os.path.join(PKG, "data", "link_audit.json")
# Wie das 404-Gedaechtnis in SyncFindus (JB-Entscheid I22: "nicht gefunden" wird 30 Tage gemerkt).
NEUPRUEFUNG_NACH_S = 30 * 24 * 3600


def _titel(v):
    return [t for t in [v.get("title"), v.get("title_romaji")] + (v.get("alt_titles") or []) if t]


def audit(cache_path, limit=0, jetzt=None):
    jetzt = time.time() if jetzt is None else jetzt
    cache = json.load(open(cache_path, encoding="utf-8"))
    entries = [(k, v) for k, v in cache.items()
               if isinstance(v, dict) and v.get("read_url") and not v.get("novel")]
    if limit:
        entries = entries[:limit]
    checked, verdacht, zaehler_weg, uncheckable, unclear = 0, [], [], 0, 0
    netz = [None]   # erst beim ersten 'gone' pruefen, danach je 'gone' neu (Netzabriss im Lauf)

    def nachweislich_tot(status):
        if status == "gone" and netz[0] is not False:
            netz[0] = readerlink.netz_ok()
        return status == "no" or (status == "gone" and bool(netz[0]))

    for k, v in entries:
        checked += 1
        status = readerlink._alive_status(v["read_url"], _titel(v))
        if nachweislich_tot(status):
            verdacht.append({"key": k, "title": v.get("title"), "url": v.get("read_url")})
        else:
            if status == "odd":
                unclear += 1
            elif status in ("blocked", "down", "gone"):
                uncheckable += 1
            if v.get("audit_tot"):
                zaehler_weg.append(k)            # nicht verurteilbar -> Zaehler zurueck (decide)
        if checked % 50 == 0:
            print(f"  ... {checked}/{len(entries)} geprueft, {len(verdacht)} tot gemessen", flush=True)

    neu_geprueft = []                            # (key, url, "frei" | "tot")
    for k, v in cache.items():
        if not isinstance(v, dict):
            continue
        for q in v.get("quarantine") or []:
            if not isinstance(q, dict) or not q.get("url"):
                continue
            if jetzt - (q.get("ts") or 0) < NEUPRUEFUNG_NACH_S:
                continue
            status = readerlink._alive_status(q["url"], _titel(v))
            if status == "ok":
                neu_geprueft.append((k, q["url"], "frei"))
            elif nachweislich_tot(status):
                neu_geprueft.append((k, q["url"], "tot"))

    verurteilt, beobachtet = [], []
    if verdacht or zaehler_weg or neu_geprueft:
        def aenderung(c):
            verurteilt.clear()
            beobachtet.clear()
            for rep in verdacht:
                v = c.get(rep["key"])
                if not isinstance(v, dict) or v.get("read_url") != rep["url"]:
                    continue                     # inzwischen repariert -> nicht anfassen
                alt = v.get("audit_tot") or {}
                vorher = alt.get("n", 0) if alt.get("url") == rep["url"] else 0
                n, verurteilen = linkhealth.decide(vorher, linkhealth.Verdict.GONE)
                if verurteilen:
                    _beiseitelegen(v, rep["url"], jetzt)
                    v["read_chap"] = None        # naechster Lauf verifiziert frisch
                    v.pop("audit_tot", None)
                    verurteilt.append(rep)
                else:
                    v["audit_tot"] = {"url": rep["url"], "n": n, "ts": int(jetzt)}
                    beobachtet.append(rep)
            for k in zaehler_weg:
                if isinstance(c.get(k), dict):
                    c[k].pop("audit_tot", None)
            for k, url, ergebnis in neu_geprueft:
                v = c.get(k)
                if not isinstance(v, dict):
                    continue
                if ergebnis == "frei":
                    v["quarantine"] = [q for q in v.get("quarantine") or []
                                       if not (isinstance(q, dict) and q.get("url") == url)]
                else:
                    for q in v.get("quarantine") or []:
                        if isinstance(q, dict) and q.get("url") == url:
                            q["ts"] = int(jetzt)
        if json_aendern(cache_path, aenderung, standard={}, streng=True) is None:
            print("Link-Audit: Cache gesperrt; Links bleiben fuer den naechsten Lauf erhalten.")
            return None
    freigegeben = sum(1 for _, _, e in neu_geprueft if e == "frei")
    report = {"ts": jetzt, "checked": checked, "dead": len(verurteilt), "entries": verurteilt[:200],
              "watch": len(beobachtet), "freigegeben": freigegeben,
              "uncheckable": uncheckable, "unclear": unclear}
    json.dump(report, open(REPORT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"Link-Audit: {checked} geprueft, {len(verurteilt)} in Quarantaene, {len(beobachtet)} "
          f"beim ersten Mal tot (beobachtet), {freigegeben} aus der Quarantaene freigegeben, "
          f"{uncheckable} nicht pruefbar, {unclear} unklar -> {REPORT}")
    return report


def _beiseitelegen(v, url, jetzt):
    """Hauptlink in die Quarantaene; die Ersatzlinks bleiben, der naechste rueckt nach."""
    if linkhealth.quarantine_link(v, url, "audit"):
        for q in v.get("quarantine") or []:         # Zeitpunkt des Audits, nicht die Wanduhr:
            if isinstance(q, dict) and q.get("url") == url:   # die 30-Tage-Frist zaehlt ab hier
                q["ts"] = int(jetzt)
        return
    # Hauptlink stand nicht in read_urls (Alt-Daten): von Hand beiseitelegen.
    q = v.setdefault("quarantine", [])
    if not any(isinstance(x, dict) and x.get("url") == url for x in q):
        q.append({"url": url, "site": v.get("read_site") or "", "reason": "audit", "ts": int(jetzt)})
    rest = [ln for ln in (v.get("read_urls") or []) if ln and ln[0] != url]
    v["read_urls"] = rest
    v["read_url"], v["read_site"] = (rest[0][0], rest[0][1] if len(rest[0]) > 1 else "") if rest else ("", "")


def main():
    args = [a for a in sys.argv[1:]]
    limit = 0
    if "--limit" in args:
        i = args.index("--limit")
        limit = int(args[i + 1]) if i + 1 < len(args) else 0
        del args[i:i + 2]
    cache_path = args[0] if args else DEFAULT_CACHE
    if not os.path.exists(cache_path):
        sys.exit(f"Cache nicht gefunden: {cache_path}")
    audit(cache_path, limit=limit)


if __name__ == "__main__":
    main()
