# -*- coding: utf-8 -*-
"""
AniList-Auto-Sync (3b Etappe 2, JB): schreibt den Lese-Fortschritt nach AniList hoch —
MangaBaka kann die Bibliothek von dort importieren/spiegeln. Ein Klick weniger als der ⤴-Export.

Sicherheit (harte Regel): das OAuth-Token liegt NUR im Windows-Anmeldeinformationsspeicher
(keyring, Dienst 'claude-sync-anilist') — nie in Dateien/Code/Logs. Einrichtung einmalig ueber
`python -m tools.anilist_auth` (PIN-Verfahren, wir sehen nie das Passwort).

Sync-Logik: nur Serien mit AniList-ID (al_id, seit v27 persistiert) und GEAENDERTEM Fortschritt
(Delta-Datei data/anilist_synced.json: al_id -> zuletzt gesendetes Kapitel). Max. `CAP_PER_RUN`
Mutationen pro Lauf (AniList-Limit ~90/min; die Erstbefuellung verteilt sich auf wenige Laeufe).
Best-effort: jeder Fehler wird gezaehlt, nie eine Exception nach aussen.
"""
import json
import os
import time

from .common import Pacer, post_json

API = "https://graphql.anilist.co"
TOKEN_SERVICE = "claude-sync-anilist"
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
SYNCED = os.path.join(DATA, "anilist_synced.json")
CAP_PER_RUN = 120                 # ~4 Min bei 2.1s-Pacer; Rest kommt im naechsten 6h-Lauf
# AniList drosselt die API zurzeit auf ~30 Anfragen/Minute (offiziell 90, aber seit langem
# reduziert). 0.75s riss das Limit nach ~30 Mutationen -> 429-Salven (JB-Lauf: 32 ok, 88 Fehler).
AL_PACER = Pacer(2.1)

_MUTATION = """mutation($id:Int,$p:Int){SaveMediaListEntry(mediaId:$id,progress:$p){id progress}}"""
_VIEWER = """{Viewer{id name}}"""
_LIBRARY = """query($u:Int){MediaListCollection(userId:$u,type:MANGA){
  lists{entries{status progress media{id idMal chapters title{english romaji}}}}}}"""
# AniList-Status -> MAL-Vokabular (dasselbe, das tools/import_mal versteht) -> unsere Scan-Status.
_AL_TO_MAL = {"CURRENT": "Reading", "REPEATING": "Reading", "COMPLETED": "Completed",
              "PLANNING": "Plan to Read", "PAUSED": "On-Hold", "DROPPED": "Dropped"}
_MAL_TO_STATUS = {"Reading": "Am Lesen", "Completed": "Fertig", "On-Hold": "Gelesen",
                  "Dropped": "Gelesen", "Plan to Read": "Gelesen"}


def get_token():
    """Token aus dem Windows-Keyring (None = nicht verbunden -> Sync still uebersprungen)."""
    try:
        import keyring
        return keyring.get_password(TOKEN_SERVICE, "token")
    except Exception:
        return None


def plan_updates(rows, synced):
    """Rein/testbar: welche (al_id, progress)-Updates stehen an? Nur mit al_id, nur ganze Kapitel,
    nur wenn NEUER Fortschritt > zuletzt gesendetem (nie senken, kein Rauschen)."""
    ups = []
    for e in rows or []:
        al = e.get("al_id")
        ch = e.get("chap")
        if not al or not ch:
            continue
        p = int(ch)
        if p > int(synced.get(str(al), 0) or 0):
            ups.append((int(al), p))
    return ups


def lib_entries(data):
    """MediaListCollection-Antwort -> flache Eintraege (rein/testbar):
    [{"al_id", "mal_id", "title", "chapters", "status"}] mit MAL-Status-Vokabular."""
    out = []
    lists = (((data or {}).get("data") or {}).get("MediaListCollection") or {}).get("lists") or []
    for lst in lists:
        for e in (lst or {}).get("entries") or []:
            m = e.get("media") or {}
            t = m.get("title") or {}
            title = t.get("english") or t.get("romaji") or ""
            if not (m.get("id") and title):
                continue
            out.append({"al_id": m["id"], "mal_id": m.get("idMal"), "title": title,
                        "chapters": float(e.get("progress") or 0),
                        "status": _AL_TO_MAL.get((e.get("status") or "").upper(), "Reading")})
    return out


def plan_pull(entries, cache):
    """RUECKWEG-Plan (rein/testbar): AniList-Bibliothek gegen unseren Cache halten.
    -> (fixes {cache_key: kapitel}, neue [{key,name,chap,status,mal_id}]).
    Bekannt = al_id- oder Titel-Treffer; Fix NUR wenn AniList WEITER ist (nie senken).
    Unbekannte laufen ueber die imported_series-Mechanik (naechster Lauf reichert an)."""
    from .parse import norm
    by_al, by_title = {}, {}
    for k, v in (cache or {}).items():
        if not isinstance(v, dict):
            continue
        if v.get("al_id"):
            by_al[int(v["al_id"])] = k
        for t in [v.get("title")] + (v.get("alt_titles") or []):
            if t:
                by_title.setdefault(norm(t), k)
    fixes, new = {}, []
    for e in entries or []:
        k = by_al.get(int(e["al_id"])) if e.get("al_id") else None
        if k is None:
            k = by_title.get(norm(e["title"]))
        if k is not None:
            ours = float((cache.get(k) or {}).get("read_chap") or 0)
            if e["chapters"] and e["chapters"] > ours:
                fixes[k] = e["chapters"]
        else:
            key = norm(e["title"])
            if key:
                new.append({"key": key, "name": e["title"],
                            "chap": e["chapters"] if e["status"] != "Plan to Read" and e["chapters"] else None,
                            "status": _MAL_TO_STATUS.get(e["status"], "Gelesen"),
                            "mal_id": e.get("mal_id")})
    return fixes, new


def pull_library(cache_path, data_dir):
    """AniList-RUECKWEG (JB: 'absolut'): die eigene AniList-Bibliothek lesen und einarbeiten —
    was du unterwegs am Handy pflegst, erscheint hier von selbst. Nicht-destruktiv:
    Lesestaende werden NUR angehoben (chapFix in list_state.json -> SEED/Anzeige), unbekannte
    Serien nur VORGEMERKT (imported_series.json -> naechster Lauf reichert an).
    Best-effort: ohne Token/Netz still None; nie eine Exception nach aussen."""
    token = get_token()
    if not token:
        return None
    try:
        hdr = {"Authorization": f"Bearer {token}"}
        AL_PACER.wait()
        viewer = post_json(API, {"query": _VIEWER}, headers=hdr)
        uid = ((viewer.get("data") or {}).get("Viewer") or {}).get("id")
        if not uid:
            return None
        AL_PACER.wait()
        entries = lib_entries(post_json(API, {"query": _LIBRARY, "variables": {"u": uid}}, headers=hdr))
        cache = json.load(open(cache_path, encoding="utf-8")) if os.path.exists(cache_path) else {}
        fixes, new = plan_pull(entries, cache)
        # Plausibilitaets-Bremse: wirkt der Cache dezimiert (Wartung/Erstlauf), NICHTS vormerken —
        # sonst wuerde die halbe AniList-Bibliothek faelschlich als "neu" importiert (Duplikate).
        # Lesestand-Anhebungen bleiben erlaubt (nicht-destruktiv, nie senkend).
        if len(new) > max(20, len(entries) // 4):
            new = []

        raised = 0
        state_p = os.path.join(data_dir, "list_state.json")
        try:
            state = json.load(open(state_p, encoding="utf-8")) if os.path.exists(state_p) else {}
        except (OSError, ValueError):
            state = {}
        try:
            cf = json.loads(state.get("chapFix") or "{}")
        except ValueError:
            cf = {}
        for k, n in fixes.items():
            if n > float(cf.get(k) or 0):
                cf[k] = n
                raised += 1
        if raised:
            state["chapFix"] = json.dumps(cf, ensure_ascii=False)
            tmp = state_p + ".tmp"
            json.dump(state, open(tmp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            os.replace(tmp, state_p)

        added = 0
        imp_p = os.path.join(data_dir, "imported_series.json")
        try:
            imported = json.load(open(imp_p, encoding="utf-8")) if os.path.exists(imp_p) else {}
        except (OSError, ValueError):
            imported = {}
        for e in new:
            if e["key"] not in imported:
                imported[e["key"]] = {"name": e["name"], "chap": e["chap"], "status": e["status"],
                                      "mal_id": e["mal_id"], "ts": time.time(), "src": "anilist"}
                added += 1
        if added:
            tmp = imp_p + ".tmp"
            json.dump(imported, open(tmp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            os.replace(tmp, imp_p)

        if raised or added:
            print(f"  [AniList-Pull] {raised} Lesestände angehoben, {added} neue Serien vorgemerkt",
                  flush=True)
        return (raised, added)
    except Exception:
        return None


def push_progress(rows):
    """Fortschritt nach AniList schreiben (best-effort, gedeckelt). -> (gesendet, fehler) | None."""
    token = get_token()
    if not token:
        return None
    try:
        synced = json.load(open(SYNCED, encoding="utf-8")) if os.path.exists(SYNCED) else {}
    except (OSError, ValueError):
        synced = {}
    ups = plan_updates(rows, synced)[:CAP_PER_RUN]
    if not ups:
        return (0, 0)
    ok = err = 0
    hdr = {"Authorization": f"Bearer {token}"}
    import urllib.error
    for al, p in ups:
        for attempt in (0, 1):
            try:
                AL_PACER.wait()
                post_json(API, {"query": _MUTATION, "variables": {"id": al, "p": p}}, headers=hdr)
                synced[str(al)] = p
                ok += 1
                break
            except urllib.error.HTTPError as ex:
                # 429 = Rate-Limit -> die vom Server genannte Pause einhalten und EINMAL wiederholen
                # (kein Haemmern; AniList nennt in Retry-After die Sekunden bis zur Freigabe).
                if ex.code == 429 and attempt == 0:
                    try:
                        wait = min(int(ex.headers.get("Retry-After") or 60), 90)
                    except (TypeError, ValueError):
                        wait = 60
                    time.sleep(wait + 1)
                    continue
                err += 1
                break
            except Exception:
                err += 1
                break
        # Nur abbrechen, wenn GAR NICHTS durchgeht (Token tot) — einzelne kaputte IDs
        # (geloeschte Eintraege) blockieren den Rest nicht.
        if err >= 5 and ok == 0:
            break
    json.dump({"_ts": time.time(), **{k: v for k, v in synced.items() if k != "_ts"}},
              open(SYNCED, "w", encoding="utf-8"), ensure_ascii=False)
    print(f"  [AniList-Sync] {ok} Fortschritte hochgeschrieben" + (f", {err} Fehler" if err else ""),
          flush=True)
    return (ok, err)
