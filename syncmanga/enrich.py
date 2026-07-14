# -*- coding: utf-8 -*-
"""
Anreicherung des Manga-Kerns — neu auf der Katalog-Schicht (MangaBaka + Fallback-Kette).

Pro Serie EIN Katalog-Lookup (`resolve` -> `catalog.lookup`; das Matching lebt seit Runde 28
direkt hier, frueher match.py): liefert beide Titel,
Typ (manga/manhwa/manhua), DB-Einzel-Scores, content_rating/Genres/Tags (fuer 18+), Autoren,
Status, Kapitelzahl und einen kanonischen Dedup-Schluessel. Das ersetzt das fruehere
Zusammenstueckeln aus 5 Quellen samt Re-Suchen.

Bewertung = Median (+ Ausreisser-Drop) ausschliesslich ueber DATENBANK-Scores (nie Reader).
Dedup: gleiche kanonische ID ⇒ ein Eintrag (JP-Titel und EN-Titel fallen zusammen).
Resilienz: faellt MangaBaka aus, liefert die Fallback-Kette in `catalog`; `srcstatus` haelt fest,
welche Quelle klemmt (Dashboard-Panel + Tray).

Pfade/Overrides kommen als Parameter (cache_path, health_dir, cap, name_fix) — ein Kern, zwei Builds.
"""
import os
import re
import json
import time
import statistics
import threading
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from . import catalog, readerlink
from . import health as srcstatus      # Quellen-Status (frueher srcstatus.py, jetzt in health)
from .config import CACHE_VER, is_dead_reader, is_no_read
from .parse import norm, host, slug_from_url, is_novel_url, is_dynamic, romaji_score
from .sources import md_latest, md_titles_from_url, md_chapter_link, mf_chapter_link, dy_chapter_link
from .sources import link_ok, al_lookup, al_english_by_id

RATING_PRIOR_C = 6.8     # globaler Mittel-Score (0-10) zur Bayes-Glaettung (fuer bayes_adjust-Reuse)
RATING_PRIOR_M = 300     # Pseudo-Stimmen (Gewicht des Priors)

# Veroeffentlichungsart -> Flagge/Land (MangaBaka liefert den Typ direkt, keine Flagge).
TYPE_FLAG = {"manga": ("🇯🇵", "JP"), "manhwa": ("🇰🇷", "KR"), "manhua": ("🇨🇳", "CN"),
             "webtoon": ("🇰🇷", "KR"), "oel": ("🇺🇸", "US"), "comic": ("🇺🇸", "US")}
# MangaBaka-Status -> deutsche Anzeige.
STATUS_DE = {"completed": "Abgeschlossen", "releasing": "Laufend", "ongoing": "Laufend",
             "hiatus": "Pausiert", "cancelled": "Abgebrochen", "discontinued": "Abgebrochen",
             "upcoming": "Angekündigt", "unknown": ""}
NOVEL_TYPES = {"novel", "light_novel", "light novel"}
SEXUAL_TERMS = {"ecchi", "smut", "hentai", "adult", "lolicon", "shotacon"}   # -> pink
GORE_TERMS = {"gore", "guro"}                                               # -> amber


# ---------------- Matching (frueher match.py) ----------------
# Bruecke zwischen Scan (Item mit Name + readers[]) und Katalog: Slugs aus Reader-URLs,
# resolve -> (rec, confidence, used_source, needs_help), dedup_key fuer JP/EN-Verschmelzung.

CONF_MIN = 0.62        # darunter gilt der Treffer als unsicher -> "braucht Hilfe" (Titel pruefen)


def read_hints(item):
    """(read_chap, prefer_novel) aus den Lese-Quellen ableiten.

    Liest der Nutzer die Serie auf einer Roman-Seite (wuxiaworld/novel/...) und NICHT auf einem Comic-Reader,
    dann prefer_novel=True (-> als Roman einordnen, ausgeblendet). Gibt es Comic-Reader, ist es ein Comic:
    dann KEINE Fortschritts-Heuristik (read_chap=None), sonst wuerde die Scanlation-Zaehlweise (~2x) faelschlich
    zum Roman kippen. Ohne jeden Reader zaehlt der Lese-Fortschritt als schwaches Signal weiter.
    """
    readers = item.get("readers") or []
    has_comic = any(not is_novel_url(r.get("url")) for r in readers)
    has_novel = any(is_novel_url(r.get("url")) for r in readers)
    prefer_novel = has_novel and not has_comic
    read_chap = None if has_comic else item.get("chap")
    return read_chap, prefer_novel


def slugs_for(item):
    """Eindeutige Titel-Slugs aus den Reader-URLs des Items (Reihenfolge erhalten)."""
    out, seen = [], set()
    for r in (item.get("readers") or []):
        s = slug_from_url(r.get("url"))
        k = norm(s) if s else ""
        if k and k not in seen:
            seen.add(k)
            out.append(s)
    return out


def resolve(item, extra=None):
    """Item -> (rec, confidence, used_source, needs_help). Sucht mit Name + Reader-Slugs + `extra`.

    `extra` = zusaetzliche Suchbegriffe, v.a. der beim letzten Lauf bereits aufgeloeste (SAUBERE) Titel
    eines Fallback-Treffers. So findet der Retry MangaBaka ueber den sauberen Titel, auch wenn der rohe
    Scan-Name verrauscht ist (Autor im Titel, "chapter"-Reste) -> Fallback-Aussetzer heilen sich."""
    queries = slugs_for(item) + [q for q in (extra or []) if q]
    read_chap, prefer_novel = read_hints(item)
    rec, conf, src = catalog.lookup(item.get("name", ""), queries, read_chap=read_chap, prefer_novel=prefer_novel)
    # MangaDex-Titel-Recovery (autoritativ): Fragment-Namen aus dem Verlauf ('Ryoumin', 'Yowai') matchen
    # unweigerlich falsch — auch mit HOHER Konfidenz (Alias-Verschmutzung: 'Yowai' ist Alias von
    # 'Lyrically', sim 1.0). Deshalb greift die Recovery bei unsicherem Match ODER bei Kurznamen
    # (<=8 Zeichen normiert: inhaerent mehrdeutig). Die mangadex-URL sagt, was WIRKLICH gelesen wurde
    # (alte numerische IDs via /legacy/mapping). JB-Faelle: 'Ryoumin' -> 'The Frontier Lord Begins with
    # Zero Subjects', 'Yowai' -> 'A Herbivorous Dragon of 5,000 Years'. Best-effort.
    short = len(norm(item.get("name", ""))) <= 8
    if (not rec) or conf < CONF_MIN or short:
        from . import sources as S
        md_url = next((r.get("url") for r in (item.get("readers") or [])
                       if "mangadex.org" in (r.get("url") or "")), "")
        if md_url:
            reals = [t for t in S.md_titles_from_url(md_url) if norm(t) != norm(item.get("name", ""))]
            if reals:
                item["md_titles"] = reals[:5]    # auch fuer die Reader-Link-Suche (Alternativ-Slugs)
                # ALLE Titel-Varianten probieren (MangaDex' title.en ist oft Romaji; der englische
                # Handelstitel steckt in altTitles -> der trifft MangaBakas Suche).
                rec2, conf2, src2 = catalog.lookup(reals[0], reals[1:] + queries,
                                                   read_chap=read_chap, prefer_novel=prefer_novel)
                # Der rekonstruierte Titel ist die WAHRHEIT -> uebernehmen, sobald er ordentlich matcht
                # (nicht nur bei conf2 > conf: der falsche Alias-Treffer kann selbst conf 1.0 haben).
                if rec2 and conf2 >= CONF_MIN:
                    rec, conf, src = rec2, conf2, src2
                    item["name"] = rec2.get("title_en") or reals[0]   # echter Name -> Anzeige/Dedup
    needs_help = (not rec) or conf < CONF_MIN
    return rec, conf, src, needs_help


def dedup_key(rec, fallback_name):
    """Stabiler Dedup-Schluessel: kanonische MangaBaka-ID > EN-Titel > Roh-Name.

    Gleiche kanonische ID ⇒ EIN Eintrag (JP-Titel und EN-Titel derselben Serie fallen zusammen).
    """
    if rec and rec.get("mb_id"):
        return f"mb:{rec['mb_id']}"
    if rec and rec.get("title_en"):
        return f"t:{norm(rec['title_en'])}"
    return f"n:{norm(fallback_name or '')}"


# ---------------- Externe Empfehlungen (frueher recs.py) ----------------
# Auf Basis des Genre-Profils der WIRKLICH GELESENEN Serien (>= 20 Kapitel) holt recs_refresh()
# die bestbewerteten AniList-Manga zu den Top-Genres, filtert Bekanntes raus und cacht das
# Ergebnis (TTL 7 Tage). Das Rendern liest NUR den Cache (recs_load) — kein Netz beim Rendern.

RECS_CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data",
                          "recs_cache.json")
RECS_TTL = 7 * 86400          # woechentlich frisch (wie die Discovery)

# MangaBaka-Genres (klein) -> AniList-Genre-Namen (exakte Schreibweise noetig)
_AL_GENRES = {"action": "Action", "adventure": "Adventure", "comedy": "Comedy", "drama": "Drama",
              "ecchi": "Ecchi", "fantasy": "Fantasy", "horror": "Horror", "mahou shoujo": "Mahou Shoujo",
              "mecha": "Mecha", "music": "Music", "mystery": "Mystery", "psychological": "Psychological",
              "romance": "Romance", "sci-fi": "Sci-Fi", "sci fi": "Sci-Fi", "science fiction": "Sci-Fi",
              "slice of life": "Slice of Life", "sports": "Sports", "supernatural": "Supernatural",
              "thriller": "Thriller"}


def _known_titles(rows):
    """Alle Titel-Varianten der Liste (normiert) — nichts davon darf empfohlen werden."""
    known = set()
    for e in rows or []:
        for t in [e.get("name"), e.get("title"), e.get("title_romaji")] + (e.get("alt_titles") or []):
            k = norm(t or "")
            if k:
                known.add(k)
    return known


def recs_top_genres(rows, n=3, min_chap=20):
    """Genre-Profil -> Top-n AniList-Genres. NUR Serien mit >= min_chap gelesenen Kapiteln
    zaehlen (JB: was man WIRKLICH liest, praegt den Geschmack — Ein-Kapitel-Proben und Backlog
    verschieben sonst das Profil). Fallback fuer kleine/frische Bibliotheken: gibt es kaum
    Serien ueber der Schwelle, zaehlen wieder alle (Empfehlungen versiegen nie)."""
    base = [e for e in rows or [] if (e.get("chap") or 0) >= min_chap]
    if len(base) < 5:
        base = list(rows or [])
    cnt = Counter()
    for e in base:
        for g in (e.get("genres") or []):
            al = _AL_GENRES.get((g or "").lower())
            if al:
                cnt[al] += 1
    return [g for g, _ in cnt.most_common(n)]


def recs_refresh(rows, cache_path=RECS_CACHE, ttl=RECS_TTL, fetch=None):
    """Empfehlungs-Cache erneuern (im Update-Lauf, best-effort). Ueberspringt bei frischem Cache.

    v2 (JB 10.07.2026, 'Empfehlungen mehr steuern'): zusaetzlich zum gemischten Top-3-Pool
    bekommt JEDES unterstuetzte Genre einen eigenen kleinen Pool (`by_genre`) — der Client
    kombiniert daraus live nach den im Panel gewaehlten Genres (an/★Prio), ganz ohne Netz.
    ~19 gepacte AniList-Abfragen 1x pro WOCHE (AL_PACER drosselt) — bewusst kein Dauerfeuer.
    `fetch(genres_list)` ist injizierbar -> ohne Netz testbar."""
    try:
        if os.path.exists(cache_path) and time.time() - os.path.getmtime(cache_path) < ttl:
            return
        gs = recs_top_genres(rows)
        if not gs:
            return
        from . import sources as S
        get = fetch or S.al_top_by_genres
        known = _known_titles(rows)
        # Pool von bis zu 30 -> die Liste zeigt 12, der ↻-Knopf mischt clientseitig neu (JB-Wunsch).
        recs = [r for r in get(gs) if norm(r.get("title") or "") not in known][:30]
        # Kapitel-1-Direktlink fuer die sichtbaren Top-12 (JB Runde 38, Feature 4): jede
        # Empfehlung bekommt einen VERIFIZIERTEN Einstiegslink (📖) statt nur des DB-Verweises.
        # Best effort (ein Muster-Reader-/Sitemap-Treffer je Titel), Fehler bleiben still.
        for r in recs[:12]:
            try:
                links = readerlink.find_chapters([r.get("title")], 1, limit=1)
                if links:
                    r["read"] = links[0][0]
            except Exception:
                pass
        # v2: je Genre ein eigener Pool (<=14) fuer die Client-Steuerung. Profil-Reihenfolge
        # zuerst (meistgelesen vorn), Rest alphabetisch — so sortiert auch das Panel die Chips.
        profile = recs_top_genres(rows, n=99)
        order = profile + sorted(set(_AL_GENRES.values()) - set(profile))
        by_genre = {}
        for g in order:
            try:
                pool = [r for r in get([g]) if norm(r.get("title") or "") not in known][:14]
            except Exception:
                pool = []
            if pool:
                by_genre[g] = pool
        if recs:
            json.dump({"ts": time.time(), "genres": gs, "order": order,
                       "recs": recs, "by_genre": by_genre},
                      open(cache_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    except Exception:
        pass


def recs_load(cache_path=RECS_CACHE, rows=None):
    """Empfehlungs-Cache lesen -> (meta, recs). Mit `rows` nochmal gegen die AKTUELLE Liste
    gefiltert (neu dazugekommene Serien fliegen sofort raus, nicht erst beim naechsten Refresh)."""
    try:
        d = json.load(open(cache_path, encoding="utf-8"))
    except (OSError, ValueError):
        return {}, []
    recs = d.get("recs") or []
    if rows:
        known = _known_titles(rows)
        recs = [r for r in recs if norm(r.get("title") or "") not in known]
    return d, recs


def bayes_adjust(R, v):
    """Schnitt-Wertung R mit v Stimmen Richtung Mittel ziehen -> wenige Stimmen ziehen nicht hoch."""
    return (v * R + RATING_PRIOR_M * RATING_PRIOR_C) / (v + RATING_PRIOR_M)


RATING_SHRINK_M = 2      # Pseudo-Quellen fuer die Bayes-Glaettung bei WENIGEN Quellen (siehe combine_ratings)


def combine_ratings(rs):
    """Bewertungen zusammenfassen: ab 3 Werten Ausreisser (>2.5 vom Median) verwerfen, dann Median.
    Bei nur 1-2 Quellen zusaetzlich Bayes-Glaettung Richtung Mittel (RATING_PRIOR_C), damit ein einzelner
    Extremwert (z.B. obskure Serie mit einer 10.0-Quelle) nicht voll durchschlaegt. Ab 3 Quellen ist der
    Median robust -> unveraendert. -> (rating, anzahl, [rohe werte]) oder None bei leerer Liste."""
    rs = [r for r in rs if r]
    if len(rs) >= 3:
        med = statistics.median(rs)
        rs = [r for r in rs if abs(r - med) <= 2.5] or rs
    if rs:
        n = len(rs)
        med = statistics.median(rs)
        if n <= 2:            # wenige Quellen -> sanft Richtung Mittel ziehen (Bayes, kleines M)
            med = (n * med + RATING_SHRINK_M * RATING_PRIOR_C) / (n + RATING_SHRINK_M)
        return round(med, 1), n, [round(x, 1) for x in rs]
    return None


def md_adult_kind(content_rating, ecchi, gore):
    """18+-Stufe aus den Flags des GLEICHEN Werks (zuverlaessig, kein Doujin-Quermatch):
      'sexual' (pink): Ecchi/Smut, pornographic, oder erotica OHNE Gore;
      'gore'   (amber): Gore (auch bei erotica, z.B. Berserk);
      ''       sonst. Reihenfolge: Gore VOR plain-erotica, damit Berserk amber bleibt."""
    if ecchi or content_rating == "pornographic":
        return "sexual"
    if gore:
        return "gore"
    if content_rating == "erotica":
        return "sexual"
    return ""


def adult_kind(rec):
    """18+-Stufe aus dem MangaBaka-Record (content_rating + Genres/Tags des kanonischen Werks)."""
    terms = set(rec.get("genres") or []) | set(rec.get("tags") or [])
    return md_adult_kind(rec.get("content_rating") or "",
                         bool(terms & SEXUAL_TERMS), bool(terms & GORE_TERMS))


def combine_latest(*latests):
    """Hoechstes bekanntes Kapitel ueber alle Quellen (None, wenn keine eins liefert)."""
    vals = [x for x in latests if x]
    return max(vals) if vals else None


def find_read_links(titles, next_chapter, mtype=None, prefer_hosts=None, prefer_page=False,
                    extra_pages=None, adult=False):
    """Verifizierte Reader-Kapitel-Links (Primaer + Ruecklagen) -> [(url, reader_name), ...].

    Duenner Wrapper um readerlink.find_chapters (konstruiert Kapitel-URLs auf mehreren Pattern-
    Readern und bestaetigt sie per echtem 404). Testbar; die eigentliche Logik liegt in readerlink.
    `prefer_page=True` = unbekannter Lesestand -> Serien-Seite statt geratenem 'Kapitel 1'.
    `extra_pages` = priorisierte Serien-Seiten (Nutzer-Verlauf/Seiten-Overrides) fuer die Ernte.
    `adult=True` (JB-Go Runde 43) = 18+-Serie -> Adult-Spezialreader duerfen mitliefern.
    """
    return readerlink.find_chapters(titles, next_chapter, mtype=mtype, limit=3,
                                    prefer_hosts=prefer_hosts, prefer_page=prefer_page,
                                    extra_pages=extra_pages, adult=adult)


# Japanische Romaji-Woerter kennen kein l/q/v/x und kein 'th' und enden auf Vokal oder n
# ('dorei', 'yuugi', 'kouryuuki' — aber nicht 'slave', 'world', 'grand'). Anteil solcher
# Woerter (>=3 Zeichen) = wie 'japanisch' ein Titel klingt.
_ROMAJI_WORD = re.compile(r"^[^lqvx]*$")
_WORDS = re.compile(r"[a-z']{3,}")


def _jap_ratio(t):
    words = _WORDS.findall((t or "").lower())
    if not words:
        return 0.0
    jap = sum(1 for w in words
              if _ROMAJI_WORD.fullmatch(w) and "th" not in w and w[-1] in "aeioun")
    return jap / len(words)


_TYPO = str.maketrans({"’": "'", "‘": "'", "“": '"', "”": '"', "–": "-", "—": "-"})


def _title_sim(a, b):
    import difflib
    return difflib.SequenceMatcher(None, norm(a), norm(b)).ratio()


def fill_one_reserves(v):
    """Unabhaengige RESERVEN fuer EINEN Cache-Eintrag -> Liste [url, name] NEUER Links.

    (JB Runden 38-40, aus tools/fill_reserves in den Kern gezogen — laeuft jetzt auch im
    regulaeren Lauf + Standalone.) Stufen: fehlende MangaDex-UUID per Titel-Suche
    nachschlagen (Kandidaten: Titel/Romaji/Alt-Titel; Waechter gegen ALLE Treffer-Titel,
    norm-gleich oder >=0.93), dann MD-Kapitel NUR bei nachweislichem EN-Kapitel
    (chapter_only), Comick nur fuer die Gruppen-Info (Tracker, kein Reader!), zuletzt
    Muster-Reader/Sitemaps. Ergaenzt NUR (nie ersetzen, ein Link je neuem Host)."""
    from .sources import md_lookup, ck_chapter_link
    nxt = v.get("read_chap") or 1
    have = {host(u) for u, _ in (v.get("read_urls") or []) if u}
    new = []
    if not v.get("mdx"):
        for q in [t for t in ([v.get("title"), v.get("title_romaji")]
                              + (v.get("alt_titles") or [])[:3]) if t]:
            try:
                hit = md_lookup(q)
            except Exception:
                continue
            if not hit.get("md_id"):
                continue
            hits = [hit.get("title") or ""] + (hit.get("all_titles") or [])
            if any(ht and (norm(ht) == norm(q) or _title_sim(ht, q) >= 0.93) for ht in hits):
                v["mdx"] = hit["md_id"]
                break
    # (MangaDex als Reserve-LESE-Link entfernt, JB 14.07.: 'mangadex ist tot' zum Lesen —
    #  bleibt Datenquelle via md_lookup/md_latest/Cover/Titel-Matching.)
    if v.get("title") and not v.get("last_group"):
        try:
            _u, _s, grp = ck_chapter_link(v["title"], nxt)
            if grp:
                v["last_group"] = grp
        except Exception:
            pass
    titles = [t for t in ([v.get("title"), v.get("title_romaji")]
                          + (v.get("alt_titles") or [])[:4]) if t]
    if titles:
        try:
            # adult=True NUR fuer 18+-Serien (pink) -> Adult-Spezialreader duerfen liefern
            found = readerlink.find_chapters(titles, nxt, mtype=v.get("type"), limit=3,
                                             adult=(v.get("adult_kind") == "sexual"))
        except Exception:
            found = []
        for u, nm in (found or []):
            h = host(u)
            if u and h and h not in have and "mangafire" not in h and not is_dead_reader(h):
                new.append([u, nm])
                have.add(h)
    # SUCH-ERNTE-Stufen (JB Runde 42, Optionen 1/2/5): greifen, wenn Slug-Raten leer blieb —
    # wir suchen dann wie ein Mensch ueber die Suchfunktion der Seiten.
    if titles and not new:
        _typ = (v.get("type") or "").lower()
        if _typ in ("manhwa", "manhua", "webtoon", "oel", ""):
            try:
                from .sources import wt_chapter_link
                u, s2 = wt_chapter_link(titles, nxt)     # offizielle Webtoons-Suche (echtes 404)
                if u and host(u) not in have:
                    new.append([u, s2])
                    have.add(host(u))
            except Exception:
                pass
        if not new:
            try:
                u, s2 = readerlink.cx_chapter_link(titles, nxt)   # comix-Suche -> Ernte
                if u and host(u) not in have:
                    new.append([u, s2])
                    have.add(host(u))
            except Exception:
                pass
        if not new:
            try:
                u, s2 = readerlink.search_slug_link(titles, nxt, mtype=v.get("type"))
                if u and host(u) not in have:                     # Madara-?s= -> echter Slug
                    new.append([u, s2])
                    have.add(host(u))
            except Exception:
                pass
    return new


def reserve_topup(cache_path, cap=30, needle=None):
    """Rotierender Reserve-Auffueller im REGULAEREN Lauf (JB Runde 40: 'enttaeuscht, dass
    Alternativen nicht mehr durchforstet werden'): je Sync bekommen bis zu `cap` Serien,
    deren Links alle an EINEM Host haengen (oder die gar keine haben), unabhaengige
    Zweitquellen. `res_ts`-Stempel rotiert die Auswahl -> der ganze Bestand ist nach
    wenigen Tagen durch und bleibt es. Best-effort, atomares Speichern, nie eine Exception.

    `needle=None` (Default seit 08.07.2026, mangahub-Vorfall: 50 Serien hingen NUR an einem
    Host, der 522-down ging -> alle fielen auf 'Alternative'): JEDE Ein-Host-Monokultur zaehlt
    als Ziel, nicht nur ein bestimmter Host. Mit `needle` weiter gezielt einsetzbar."""
    try:
        cache = json.load(open(cache_path, encoding="utf-8"))
    except Exception:
        return None
    targets = []
    for k, v in cache.items():
        if not isinstance(v, dict) or v.get("novel"):
            continue
        urls = [u for u, _ in (v.get("read_urls") or []) if u]
        if needle:
            single = (urls and all(needle in (host(u) or "") for u in urls))
        else:
            single = (urls and len({host(u) or "" for u in urls}) == 1)
        # Leer zaehlt AUCH ohne read_chap (JB 14.07., Kategorie Pflege: 112 Leer-Eintraege
        # ohne Lesestand warteten sonst ewig auf den naechsten Voll-Lauf) — fill_one_reserves
        # nutzt dann Kapitel 1 = ehrlicher Start, wie der Backlog-Pfad (Runde 41).
        empty = not urls
        if single or empty:
            # GANZ ohne Link zuerst (JB 09.07.2026 'definitiv machen': die 5 Reserve-losen
            # aus dem Ausfall-Test sollen nicht in der Rotation warten), dann Rotation.
            targets.append((0 if empty else 1, v.get("res_ts") or 0, k))
    targets.sort()                                   # (Prioritaet, aeltester Stempel) zuerst
    done = added = 0
    for _prio, _ts, k in targets[:max(0, cap)]:
        v = cache[k]
        try:
            new = fill_one_reserves(v)
        except Exception:
            new = []
        v["res_ts"] = time.time()
        done += 1
        if new:
            v["read_urls"] = (v.get("read_urls") or []) + new
            if not v.get("read_url"):
                v["read_url"], v["read_site"] = new[0]
            added += 1
    if done:
        try:
            tmp = cache_path + ".tmp"
            json.dump(cache, open(tmp, "w", encoding="utf-8"), ensure_ascii=False)
            os.replace(tmp, cache_path)
        except Exception:
            pass
        print(f"  [Reserve-Auffueller] {done} Serien geprüft, {added} ergänzt", flush=True)
    return done, added


def _al_first_title(rec):
    """ANILIST-FIRST (JB Runde 40, 'Was ist so schwer an der Sprache?'): AniLists
    title.english ist REDAKTIONELL gepflegt — wenn er existiert, ist ER der Anzeigename,
    Punkt. Keine Romaji-Quoten-Raterei mehr ('Napad Titana'-Regression: der eigene
    Ratio-Waechter verwarf 'Attack on Titan', weil 'titan' romaji-artig aussieht).
    Nur Basis-Guards: Latein-Schrift + Mindestlaenge. -> '' wenn AniList nichts fuehrt."""
    t = al_english_by_id((rec.get("source_ids") or {}).get("anilist"))
    if t and len(t) >= 3 and catalog._looks_english(t):
        return t
    return ""


def _en_second_source(rec):
    """Titel-NACHBRENNER (JB Runde 37): blieb der Anzeigetitel Romaji und weder AniList
    noch MangaBaka lieferten Englisches, die MangaDex-Titel PER UUID probieren (dort ist
    'title.en' oft Romaji -> Ratio-Guard bleibt HIER sinnvoll). -> '' wenn nichts."""
    ids = rec.get("source_ids") or {}
    if not ids.get("mangadex"):
        return ""
    for c in md_titles_from_url(f"https://mangadex.org/title/{ids['mangadex']}") or []:
        if (c and len(c) >= 5 and catalog._looks_english(c)
                and _jap_ratio(c.translate(_TYPO)) < 0.5):
            return c
    return ""


def _english_title(rec):
    """Anzeigename = der ENGLISCHSTE Titel (Kernregel; beim Katalog-Umbau verloren gegangen,
    JB Runde 34: MangaBakas HAUPTTITEL ist oft Romaji — 'Dorei Yuugi' statt 'SLAVE GO',
    'Yojouhan Isekai Kouryuuki' statt '4.5 Tatami Mat …').

    Konservativ (JB Runden 34+35): gewechselt wird NUR, wenn der Haupttitel UEBERWIEGEND
    Romaji klingt (>= 0.5) — sonst bleibt er unangetastet ('Rascal … Senpai' darf nicht
    kippen). Kandidaten sind AUSSCHLIESSLICH die ENGLISCHEN Zweittitel (alt_en aus
    MangaBakas secondary_titles['en']) — die gemischte alt_titles-Liste brachte
    franzoesische/spanische Titel ('Ataque a los titanes') in die Liste. Mini-Kandidaten
    (<5 Zeichen, 'ADM') und Nicht-Latein fliegen raus; typografische Zeichen zaehlen als
    ASCII. Bei Ratio-Gleichstand gewinnt der Zweittitel: Pinyin-Haupttitel wie 'Quanzhi
    Fashi' erreichen nur die halbe Quote ('q' gilt als un-japanisch), stehen aber englischen
    Titeln in nichts nach — MangaBaka hat den alt_en ja ausdruecklich als ENGLISCH markiert
    ('Versatile Mage')."""
    main = rec.get("title_en") or ""
    if _jap_ratio(main.translate(_TYPO)) < 0.5:
        return main
    cands = (rec.get("alt_en") or []) + [main]
    cands = [c for c in cands
             if c and len(c) >= 5 and all(ord(ch) < 128 for ch in c.translate(_TYPO))]
    if not cands:
        return main
    # Tiebreak (JB Runde 42, 'Zom-fille' vs 'My Daughter is a Zombie', beide ratio 0.5):
    # bei gleicher Romaji-Quote gewinnt der Kandidat mit ENGLISCHEM Funktionswort.
    _EN_SIG = {"the", "of", "is", "a", "an", "my", "to", "in", "and", "on", "with", "who",
               "that", "this", "from", "for"}
    def _has_en(c):
        return 0 if (_EN_SIG & {w.strip(".,!?:;()[]\"'") for w in c.lower().split()}) else 1
    return min(enumerate(cands),
               key=lambda p: (_jap_ratio(p[1].translate(_TYPO)),
                              _has_en(p[1]), romaji_score(p[1]), p[0]))[1]


def _bookmark_link(e, next_chap, titles):
    """STUFE 0 (JB Runde 33): die eigene Verlaufs-URL ist der beste Link.

    a) Traegt eine Verlaufs-URL GENAU die Ziel-Kapitelzahl -> exakt diese URL, ohne Netz
       (der Nutzer war nachweislich dort; loest opake IDs wie roliascan ch164-…).
    b) Sonst: Kapitel-Token der meistbesuchten Kapitel-URL auf das Ziel tauschen und STRENG
       verifizieren ('ok' inkl. Identitaets-Check — der getauschte Link ist geraten).
    -> (url, host) oder ('', '')."""
    try:
        want = float(next_chap)
    except (TypeError, ValueError):
        return "", ""
    from .parse import chapter_of
    swap_cands = []
    for r in sorted(e.get("readers") or [], key=lambda r: -(r.get("visits") or 0)):
        u = r.get("url") or ""
        hh = r.get("host") or host(u)
        if not u or not hh or is_dead_reader(hh) or is_dynamic(hh) or is_no_read(hh) \
                or not readerlink.has_chapter_token(u):
            continue
        if chapter_of(u, "") == want:
            # Auch die eigene URL pruefen: Reader sterben (JB-Fall manhuafast: Kapitel-404).
            # Bot-Block/Drossel der EIGENEN Seite ist ok — nachweislich besucht; nur ein
            # bewiesenes 404/Kapitel-Redirect disqualifiziert.
            if readerlink._alive_status(u, titles) != "no":
                return u, hh
            continue
        swap_cands.append((u, hh))
    for u, hh in swap_cands[:2]:
        v = readerlink.swap_chapter(u, next_chap)
        if v and v != u and readerlink._alive_status(v, titles) == "ok":
            return v, hh
    return "", ""


def _harvest_pages(e, ov_url="", ov_site="", cap=4, no_prog=False):
    """Priorisierte Serien-Seiten fuer die Kapitel-Ernte (JB Runde 32: 'Prioritaet anpassen'):
    ZUERST ein Seiten-Override (JB-kuratiert, z.B. comix), dann die EIGENEN Lese-Seiten des
    Nutzers (meistbesucht zuerst; mangatown & Co. listen die Kapitel auf der Serien-Seite).
    Bei unbekanntem Lesestand (`no_prog`) wird auch aus einem KAPITEL-Override die
    Serien-Seite abgeleitet — sie ist dann das kuratierte 'öffnen'-Ziel.
    Dynamische Seiten (webtoons/tapas) und gesperrte Hosts bleiben draussen."""
    pages, seen = [], set()
    if ov_url:
        pu = ov_url
        if readerlink.is_chapter_url(ov_url):
            pu = (readerlink._series_page(ov_url) or readerlink.series_page_of(ov_url)) \
                if no_prog else ""
        if pu:
            pages.append((pu, ov_site or host(pu)))
            seen.add(host(pu) or ov_site)
    for r in sorted(e.get("readers") or [], key=lambda r: -(r.get("visits") or 0)):
        u = r.get("url") or ""
        hh = r.get("host") or host(u)
        if not u or not hh or hh in seen or is_dead_reader(hh) or is_dynamic(hh) or is_no_read(hh):
            continue
        sp = readerlink.series_page_of(u)
        if sp:
            seen.add(hh)
            pages.append((sp, hh))
        if len(pages) >= cap:
            break
    return pages


def probe_once(fn, retries=1, pause=0.8):
    """Eine Quelle antesten -> True/False. Bei Fehler/leerem Treffer bis zu `retries` mal
    erneut (kurze Pause dazwischen). So faerbt ein EINZELNER Aussetzer/Rate-Limit (429) das
    Tray-Symbol nicht mehr faelschlich gelb — nur ein echter, anhaltender Ausfall zaehlt als tot.
    Rein/testbar (kein Netz, kein Seiteneffekt)."""
    for attempt in range(retries + 1):
        try:
            if bool(fn()):
                return True
        except Exception:
            pass
        if attempt < retries:
            time.sleep(pause)
    return False


def probe_sources(health_dir):
    """Quellen-Check zu Beginn: Antwortzeit + ob jede Quelle liefert. Speist srcstatus + Tray-Ampel."""
    from . import sources as S
    checks = [("MangaBaka", lambda: catalog.mb_search("one piece")[0].get("title")),
              ("AniList", lambda: S.al_lookup("one piece").get("al_id")),
              ("MangaUpdates", lambda: S.mu_rating("one piece").get("mu_id")),
              ("Kitsu", lambda: S.kitsu_rating("one piece").get("title")),
              ("MyAnimeList", lambda: S.jikan_lookup("one piece").get("title"))]
    parts, dead = [], []
    for nm, fn in checks:
        t0 = time.time()
        ok = probe_once(fn)          # zweiter Versuch bei Aussetzer -> weniger Fehlalarme
        srcstatus.record(nm.lower(), ok, "" if ok else "Probe ohne Treffer", latency=time.time() - t0)
        parts.append(f"{nm} {time.time() - t0:.1f}s{'' if ok else ' !!TOT'}")
        if not ok:
            dead.append(nm)
    print("  [Quellen-Check] " + " | ".join(parts), flush=True)
    try:                                  # Gesundheit fuer den Tray hinterlegen (Icon-Farbe)
        with open(os.path.join(health_dir, "source_health.json"), "w", encoding="utf-8") as f:
            json.dump({"ts": datetime.now().isoformat(timespec="seconds"), "dead": dead}, f)
    except Exception:
        pass
    if dead:
        print(f"  ⚠ QUELLE(N) TOT: {', '.join(dead)}", flush=True)
    return dead


RETRY_MAX = 4      # so oft eine ungematchte/Fallback-Serie ueber spaetere Laeufe erneut probieren

def select_todo(items, cache, cache_ver, force=False):
    """Welche Serien anreichern? -> (key, eintrag, cache_eintrag, stale).

    Resume: neue / veraltete (cache_ver gestiegen) / Retry. Retry deckt jetzt auch FALLBACK-Treffer
    ab: MangaBaka drosselt beim Force (429) und wirft einzelne Serien auf die schwaecheren Quellen
    (leerer Status/Flagge/Stand) - die probieren wir ueber die naechsten Laeufe erneut gegen MangaBaka,
    bis es klappt (bis RETRY_MAX). So heilen 429-Aussetzer sich selbst statt "unbekannt" zu bleiben.
    force=True: ALLE neu, mit frischer Link-Pruefung (stale=False)."""
    todo, retries = [], []
    for k, e in items.items():
        c = cache.get(k)
        stale = c is not None and c.get("v", 1) < cache_ver
        weak = (not c.get("md_id")) or c.get("src") == "fallback" if c else False
        retry = c is not None and weak and c.get("tries", 0) < RETRY_MAX
        if force or c is None or retry or stale:
            item = (k, e, c, False if force else stale)
            # R6: hartnaeckige Retry-Faelle ZUERST -> werden im cap nicht von neuen/stale ausgehungert.
            (retries if (retry and not force) else todo).append(item)
    return retries + todo


def _consume_broken(cache):
    """⚠-Meldungen SOFORT verarbeiten (JB): liegt data/broken_links.json (Export aus der Liste) im
    Datenordner, wird jede gemeldete Serie in DIESEM Lauf komplett neu aufgeloest (Cache-Eintrag raus
    -> Match + Links frisch + verifiziert) und ein evtl. kaputter series_override entfernt.
    Meldungen wandern ins .done-Archiv (nicht-destruktiv, Historie bleibt). Best-effort."""
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
    src = os.path.join(data_dir, "broken_links.json")
    if not os.path.exists(src):
        return
    try:
        reports = json.load(open(src, encoding="utf-8"))
        from .parse import norm as _norm
        hit = []
        for rep in reports if isinstance(reports, list) else []:
            k = _norm(rep.get("name") or "")
            for ck in [c for c in cache if c == k or _norm(c) == k]:
                del cache[ck]
                hit.append(ck)
            try:                                  # kaputten kuratierten Link derselben Serie entfernen
                from . import readerlink as _rl
                if k in _rl.SERIES_OVERRIDES:
                    del _rl.SERIES_OVERRIDES[k]
            except Exception:
                pass
        done = os.path.join(data_dir, "broken_links.done.json")
        hist = json.load(open(done, encoding="utf-8")) if os.path.exists(done) else []
        hist.append({"ts": time.time(), "reports": reports, "recheck": hit})
        json.dump(hist, open(done, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        os.remove(src)
        if hit:
            print(f"  [Link kaputt] {len(hit)} gemeldete Serie(n) werden JETZT neu aufgeloest", flush=True)
    except Exception:
        pass


_PROGRESS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")


def _progress(phase, done, total, pdir=None, rendered=False):
    """Fortschritt fuer den Balken auf der Leseliste: sync_progress.json (Tray/Tools) UND
    sync_progress.js (JSONP-Stil `var SYNCP={...}`) — <script src> ist von der file://-Sperre
    ausgenommen, dadurch funktioniert der Balken AUCH bei doppelt geklickter HTML ohne Server
    (JB-Wunsch: Erstaufbau sichtbar machen). Best-effort, nie den Lauf stoeren."""
    try:
        pdir = pdir or _PROGRESS_DIR
        payload = json.dumps({"phase": phase, "done": done, "total": total, "ts": time.time(),
                              "rendered": time.time() if rendered else 0})
        for name, body in (("sync_progress.json", payload),
                           ("sync_progress.js", "var SYNCP=" + payload + ";")):
            p = os.path.join(pdir, name)
            tmp = p + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                f.write(body)
            os.replace(tmp, p)
    except Exception:
        pass


def _snapshot_items(items):
    """Flache, thread-sichere Momentaufnahme fuer Zwischen-Renders: top-level dicts + readers-
    Listen kopieren (assemble_rows haengt dort an). deepcopy waere anfaellig fuer Races mit
    laufenden resolve()-Mutationen und unnoetig teuer."""
    out = {}
    for k, v in list(items.items()):
        d = dict(v)
        if d.get("readers") is not None:
            d["readers"] = list(d["readers"])
        out[k] = d
    return out


def strip_no_read_links(cache):
    """NO_READ_HOSTS (mangadex, JB 14.07.: 'ist tot zum Lesen') aus allen read_urls entfernen.

    Laeuft als eigener Pass NACH bake_overrides/promote/demote (die MangaDex-Pins/Verlaufs-
    Links zurueckschreiben koennen) und VOR enrich. Nicht-destruktiv fuer DATEN: nur die
    read_urls/read_url werden gefiltert; Cover, Bewertung, md_id, latest bleiben unangetastet.
    Der Primaerlink rueckt auf die erste verbleibende Reserve; sonst leer (-> ehrliche Suche).
    Gibt die Zahl geaenderter Serien zurueck."""
    changed = 0
    for e in cache.values():
        if not isinstance(e, dict):
            continue
        urls = e.get("read_urls") or []
        kept = [list(u) for u in urls if u and u[0] and not is_no_read(host(u[0]))]
        if len(kept) != len(urls):
            changed += 1
            e["read_urls"] = kept
            if is_no_read(host(e.get("read_url") or "")) or not e.get("read_url"):
                if kept:
                    e["read_url"] = kept[0][0]
                    e["read_site"] = kept[0][1] if len(kept[0]) > 1 else host(kept[0][0])
                else:
                    e["read_url"], e["read_site"] = "", ""
    return changed


def _live_links(links):
    """read_urls gegen die DEAD_READERS-Sperrliste + NO_READ_HOSTS filtern. WICHTIG auch fuer
    Cache-ALTBESTAND: der Reuse-Zweig kopierte gespeicherte Links wortwoertlich weiter — ein Link,
    der VOR einer Domain-Sperre gebaut wurde, ueberlebte die Sperre sonst fuer immer (JB-Fund:
    vinlandsagamanga blieb 'weiterlesen', obwohl die Domain laengst gesperrt war).
    NO_READ_HOSTS raus (JB 14.07.: mangadex ist als Lese-Link tot, bleibt aber Datenquelle)."""
    out = []
    for ln in (links or []):
        try:
            u = ln[0]
        except (TypeError, IndexError, KeyError):
            continue
        if u and not is_dead_reader(host(u)) and not is_no_read(host(u)):
            out.append(list(ln))
    return out


def keep_last_good(links, cache_entry):
    """FAILSAFE (JB 05.07.2026, No-Go 'Links bei schlechtem Netz weg'): fand/verifizierte ein
    Lauf GAR NICHTS (alle Netz-Stufen gescheitert), behalten wir den letzten bekannten
    NICHT-TOTEN Link aus dem Cache. So verliert eine Serie ihren Link NIE durch einen
    fehlgeschlagenen Lauf — ersetzt wird nur, wenn ein NEUER Link da ist. Tote Domains raus,
    Novels (haben nie Reader-Links) unberuehrt."""
    if links or not cache_entry or cache_entry.get("novel"):
        return links
    return _live_links(cache_entry.get("read_urls")) or links


def _resolve_md_page_override(ov_url, ov_site, ov_tpl, next_chap, no_prog, md_link=None):
    """JB-Regel 14.07. ('Kapitel vor Seite'): ein mangadex-SEITEN-Override (/title/<uuid> —
    opake Kapitel-UUIDs sind nicht ratbar, ein {n}-Template unmoeglich) wird bei bekanntem
    Lesestand ueber die Aggregate-API aufs EXAKTE Kapitel aufgeloest -> (url, site).
    Ohne EN-Kapitel (Lizenz-Titel) bleibt die Serien-Seite das ehrliche Ziel. Netz injizierbar."""
    uuid = readerlink.md_title_uuid(ov_url) if (ov_url and not ov_tpl) else ""
    if not uuid or no_prog:
        return ov_url, ov_site
    u, s = (md_link or md_chapter_link)(uuid, next_chap, chapter_only=True)
    return (u, s) if u else (ov_url, ov_site)


def bake_overrides(cache, items):
    """Kuratierte series_overrides deterministisch (OHNE Netz, ohne Verifikation) in den GESAMTEN
    Cache einbacken und die Zahl reparierter Serien zurueckgeben.

    Warum noetig: Die normale Anreicherung wendet Overrides nur auf die ~cap Serien an, die pro
    Lauf frisch bearbeitet werden. Alt-Eintraege (z.B. aus einer Cache-Panne mit leeren read_urls)
    behalten sonst ihren leeren Link und fallen in der Anzeige auf 'Alternative' zurueck, OBWOHL ein
    kuratierter Direktlink existiert (JB 07.07.2026: 'warum ueberall Alternative?'). Dieser Pass
    laeuft jeden Build und sorgt dafuer, dass ein Override IMMER als Primaerlink erscheint —
    unabhaengig davon, ob die Serie gerade neu angereichert wurde.

    Nicht-destruktiv: der Override wird nur VORNE angestellt, vorhandene Reserven bleiben erhalten;
    Novels und Serien ohne passenden Override bleiben unberuehrt. Die Override-Vorrang-Entscheidung
    ist identisch zum Anreicherungs-Pfad (Kapitel-Override zaehlt nur bei bekanntem Lesestand)."""
    fixed = 0
    for k, c in cache.items():
        if not isinstance(c, dict) or c.get("novel"):
            continue
        it = items.get(k) if items else None
        chap = (it or {}).get("chap") or c.get("read_chap") or c.get("chap")
        chap_known = bool(chap)
        next_chap = int(chap) if chap else 1
        lat = c.get("latest")
        if lat and next_chap > lat and (c.get("conf") or 0) >= 0.7:   # nie ueber das neueste Kapitel
            next_chap = int(lat)
        cands = [c.get("title_en"), c.get("title_romaji"), c.get("title"), k,
                 (it or {}).get("name")] + (c.get("alt_titles") or [])
        ov_url, ov_site, ov_tpl, _pin = readerlink.override_info([x for x in cands if x], next_chap)
        if not ov_url:
            continue
        links = [list(x) for x in (c.get("read_urls") or []) if x and x[0]]
        ov_chap = bool(ov_tpl or readerlink.is_chapter_url(ov_url))
        # Pin nur noch als KAPITEL-Override unantastbar (JB-Regel 14.07. 'Kapitel vor Seite'):
        # eine gepinnte SEITE darf einen echten Kapitel-Link nicht mehr verdraengen.
        ov_used = ((_pin and ov_chap)
                   or (ov_chap and chap_known)
                   or (not ov_chap and (not links or not readerlink.is_chapter_url(links[0][0])))
                   or (ov_chap and not chap_known and not links))
        if not ov_used or (links and links[0][0] == ov_url):    # nichts zu tun / schon vorne
            continue
        c["read_urls"] = [[ov_url, ov_site]] + [ln for ln in links if ln[0] != ov_url]
        c["read_url"], c["read_site"] = ov_url, ov_site
        c["ov"] = True
        if not c.get("read_chap"):
            c["read_chap"] = next_chap
        fixed += 1
    return fixed


def _ov_is_chapter(c, k, it, chap):
    """True, wenn fuer diese Serie ein KAPITEL-Override existiert ({n}-Vorlage oder Kapitel-URL).

    Fuer die Heilpasses (promote/demote): nur ein Kapitel-Override bleibt unantastbar —
    eine Override-SEITE macht Platz fuer echte Kapitel-Links (JB-Regel 14.07.). Ohne Netz:
    fetch=True-Stub, es geht nur um die FORM des kuratierten Links, nicht seine Lebendigkeit."""
    cands = [c.get("title_en"), c.get("title_romaji"), c.get("title"), k,
             (it or {}).get("name")] + (c.get("alt_titles") or [])
    o_url, _os, o_tpl, _op = readerlink.override_info(
        [x for x in cands if x], chap, fetch=lambda u: True)
    return bool(o_url) and (o_tpl or readerlink.is_chapter_url(o_url))


def promote_history_chapters(cache, items):
    """JB 07.07.2026 ('kann man das Kapitel aus dem Verlauf fischen?'): Steht als Primaerlink nur
    eine SERIEN-SEITE (kein Kapitel-Token) oder gar nichts, der Nutzer war aber nachweislich auf
    EXAKT dem Ziel-Kapitel im Verlauf -> genau diese URL als Primaer nach vorne holen.

    Das ist die Ganz-Cache-Verallgemeinerung von `_bookmark_link` Fall (a): waehrend jener nur die
    ~cap frisch angereicherten Serien pro Lauf trifft (und der Cache-Kurzschluss read_chap==next_chap
    ihn sonst ueberspringt), laeuft dieser Pass JEDEN Build ueber ALLE Serien und heilt so alte
    Serien-Seiten-Links (JBs 'fuehrt zur Mangaseite, nicht zum Kapitel') selbst.

    Streng + sicher + ohne Netz (der Nutzer war beweisbar dort):
      - nur wenn der aktuelle Primaer KEIN Kapitel ist (Serien-Seite/leer),
      - nur eine Verlaufs-URL mit ECHTEM Kapitel (Token oder mangadex-/chapter/-UUID),
        lebende + nicht-dynamische Domain,
      - nur bei EXAKTER Uebereinstimmung Kapitel(url) == read_chap (kein Raten),
      - NIE einen Kapitel-Link oder KAPITEL-Override verdraengen; eine Override-SEITE darf
        vom nachweislich besuchten exakten Kapitel ueberholt werden (JB-Regel 14.07.
        'Kapitel vor Seite' — der kuratierte Link bleibt als Reserve erhalten).
    Nicht-destruktiv: Reserven bleiben erhalten, der Kapitel-Link wird nur vorangestellt.
    """
    if not items:
        return 0
    from .parse import chapter_of
    promoted = 0
    for k, c in cache.items():
        if not isinstance(c, dict) or c.get("novel"):
            continue
        cur = c.get("read_url") or ""
        if cur and readerlink.is_chapter_url(cur):
            continue                     # schon ein Kapitel-Link -> nie anfassen (Ratchet-Richtung)
        it = items.get(k)
        if not it:
            continue
        want = c.get("read_chap") or it.get("chap")
        try:
            want = float(want) if want else None
        except (TypeError, ValueError):
            want = None
        if want is None:
            continue                     # '?'-Lesestand will bewusst die Serien-Seite
        if c.get("ov") and _ov_is_chapter(c, k, it, want):
            continue                     # KAPITEL-Override (arenascan: kein Token!) bleibt vorn
        best = None                      # (visits, url, host) der meistbesuchten exakten Kapitel-URL
        for r in sorted(it.get("readers") or [], key=lambda r: -(r.get("visits") or 0)):
            u = r.get("url") or ""
            hh = r.get("host") or host(u)
            if not u or not hh or is_dead_reader(hh) or is_dynamic(hh) or is_no_read(hh):
                continue                 # is_no_read: mangadex nie aus dem Verlauf fischen (JB 14.07.)
            if not readerlink.is_chapter_url(u):
                continue                 # nur echte Kapitel-URLs
            if readerlink.has_chapter_token(u) and readerlink.series_page_of(u) == u:
                continue                 # getarnte Serien-Seite (Token, aber nichts abtrennbar)
            # Kapitelnummer: aus der URL — oder, bei OPAKEN Kapitel-IDs (mangafire
            # /chapter/7544676, JB 08.07.2026 Berserk/One Piece; mangadex /chapter/<uuid>),
            # aus dem SEITENTITEL, den der Scan bereits geparst hat (r['chap']). Kein Raten;
            # bei mangadex zaehlt NUR der Titel (Ziffern in der UUID waeren Zufallstreffer).
            got = None if "mangadex" in hh else chapter_of(u, "")
            if got is None:
                got = r.get("chap")
            elif "mangafire" in hh:
                continue                 # mangafire mit NUMERISCHEM /chapter/N = totes Rate-Schema
                                         # (leitet zur Serienseite; echte Kapitel = opake ID -> oben)
            if got != want:
                continue                 # nur EXAKT das Ziel-Kapitel
            vis = r.get("visits") or 0
            if not best or vis > best[0]:
                best = (vis, u, hh)
        if not best:
            continue
        _, u, hh = best
        links = [list(x) for x in (c.get("read_urls") or []) if x and x[0]]
        c["read_urls"] = [[u, hh]] + [ln for ln in links if ln[0] != u]
        c["read_url"], c["read_site"] = u, hh
        if not c.get("read_chap"):
            c["read_chap"] = int(want)
        promoted += 1
    return promoted


def demote_series_pages(cache, items=None):
    """Kapitel-Link schlaegt Serien-Seite (JB 08.07.2026: 'ohne Ende mangafire als erste Wahl,
    fuehren zur Homepage'): Steht eine blanke SERIEN-Seite vorn, waehrend weiter hinten ein echter
    Kapitel-Link wartet (Token oder opake /chapter/-ID), rueckt der Kapitel-Link nach vorn.

    Nicht-destruktiv (reine Umordnung, kein Link geht verloren). Respektiert KAPITEL-Overrides
    (arenascan: kein Token!) und '?'-Lesestand (der WILL die Serien-Seite); eine Override-SEITE
    macht dagegen Platz (JB-Regel 14.07. 'Kapitel vor Seite', der Link bleibt Reserve).
    mangafire-Links mit NUMERISCHER Kapitelnummer zaehlen nicht als Kapitel (totes Rate-Schema,
    leitet selbst zur Serienseite). Stehen NUR Seiten zur Wahl, rueckt mangadex nach hinten
    (JB 14.07.: 'dann wuerde ich mangafire nehmen')."""
    from .parse import chapter_of as _chof
    moved = 0
    for k, c in cache.items():
        if not isinstance(c, dict) or c.get("novel"):
            continue
        it = (items or {}).get(k) or {}
        chap = it.get("chap") or c.get("read_chap")
        if not chap:
            continue                                     # unbekannter Lesestand -> Seite gewollt
        links = [list(l) for l in (c.get("read_urls") or []) if l and l[0]]
        if len(links) < 2 or readerlink.is_chapter_url(links[0][0]):
            continue
        if c.get("ov") and _ov_is_chapter(c, k, it, chap):
            continue                                     # Kapitel-Override bleibt vorn
        def _is_chapter(u):
            if not readerlink.is_chapter_url(u):
                return False
            if readerlink._MF_READ_URL.match(u or ""):
                return True                              # MangaFire-API-Lese-URL = echtes Kapitel
            if "mangafire" in (host(u) or "") and _chof(u, "") is not None:
                return False                             # numerisches mangafire = totes Rate-Schema
            return True
        best = next((i for i, l in enumerate(links) if _is_chapter(l[0])), None)
        if best is None:
            # Nur Seiten zur Wahl: eine mangadex-Front macht Platz fuer die erste
            # NICHT-mangadex-Seite (JB-Praeferenz MangaFire > MangaDex bei Seiten).
            if "mangadex" not in (host(links[0][0]) or ""):
                continue
            best = next((i for i, l in enumerate(links)
                         if "mangadex" not in (host(l[0]) or "")), None)
            if best is None:
                continue
        links.insert(0, links.pop(best))
        c["read_urls"] = links
        c["read_url"] = links[0][0]
        c["read_site"] = links[0][1] if len(links[0]) > 1 else host(links[0][0])
        moved += 1
    return moved


def _save_cache(cache, cache_path):
    """Cache ATOMAR schreiben (tmp + os.replace, wie ueberall sonst im Projekt). Ein Kill mitten im
    Checkpoint (JB-Vorfall: parallele Laeufe gestoppt) darf die 1-MB-Datei nie halb geschrieben
    zuruecklassen — sonst verwirft der naechste Lauf still den GESAMTEN Cache (Stunden Anreicherung)."""
    tmp = cache_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False)
    os.replace(tmp, cache_path)


def enrich(items, cache_path, health_dir, cap, name_fix=None, cache_ver=CACHE_VER, force=False,
           relink=False, progress_dir=None, checkpoint_render=None):
    name_fix = name_fix or {}
    cache = {}
    if os.path.exists(cache_path):
        try:
            cache = json.load(open(cache_path, encoding="utf-8"))
        except Exception:
            cache = {}
    _consume_broken(cache)          # ⚠-Meldungen -> betroffene Serien in diesem Lauf neu (JB-Wunsch)
    try:                            # kuratierte Direktlinks IMMER einbacken (kein Netz) -> nie 'Alternative'
        _baked = bake_overrides(cache, items)      # trotz vorhandenem Override (JB 07.07.2026)
        if _baked:
            print(f"  {_baked} Serien: kuratierten Direktlink eingebacken (Override-Backfill).", flush=True)
    except Exception as ex:
        print(f"  [Override-Backfill] uebersprungen: {type(ex).__name__}: {ex}", flush=True)
    try:                            # JBs 'Kapitel aus dem Verlauf fischen': Serien-Seiten-Links, zu
        _hp = promote_history_chapters(cache, items)   # denen der Nutzer das exakte Kapitel besucht
        if _hp:                                        # hat, aufs echte Kapitel heben (kein Netz)
            print(f"  {_hp} Serien: Kapitel-Link aus dem eigenen Verlauf gefischt.", flush=True)
    except Exception as ex:
        print(f"  [Verlauf-Kapitel] uebersprungen: {type(ex).__name__}: {ex}", flush=True)
    try:                            # Kapitel-Link schlaegt Serien-Seite (JB 08.07.2026, kein Netz)
        _dm = demote_series_pages(cache, items)
        if _dm:
            print(f"  {_dm} Serien: Kapitel-Reserve vor die Serien-Seite gerueckt.", flush=True)
    except Exception as ex:
        print(f"  [Seiten-Demotion] uebersprungen: {type(ex).__name__}: {ex}", flush=True)
    try:                            # NO-READ-Hosts als LESE-Link entfernen (JB 14.07.: mangadex
        _nr = strip_no_read_links(cache)   # ist tot zum Lesen). Nach allen Passes, VOR enrich.
        if _nr:                            # Cover/Daten bleiben; nur die read_urls werden gefiltert.
            print(f"  {_nr} Serien: mangadex als Lese-Link entfernt (bleibt Datenquelle).", flush=True)
    except Exception as ex:
        print(f"  [No-Read-Filter] uebersprungen: {type(ex).__name__}: {ex}", flush=True)
    if relink:
        # Relink: gecachte Metadaten behalten, NUR den 'weiterlesen'-Link neu aufloesen (Override-Vorrang).
        # Kein MangaBaka -> schnell. Alle bereits gecachten (aktuellen) Serien kommen dran.
        todo = [(k, items[k], cache.get(k), False) for k in items
                if cache.get(k) and cache[k].get("v") == cache_ver][:cap]
    else:
        todo = select_todo(items, cache, cache_ver, force)[:cap]
    lock = threading.Lock()
    done = [0]
    new_chaps = []                  # Serien mit neuen Kapiteln (latest gestiegen) -> Tray-Benachrichtigung
    t_start = time.time()
    # Balken zeigt die GESAMT-Sicht (JB: 'warum nur 681?' — 282 waren schon im Cache):
    # done = bereits fertige + in diesem Lauf geschaffte, total = ganze Bibliothek.
    _base = max(0, len(items) - len(todo))
    if todo:
        print(f"{len(todo)} Serien anzureichern - geschaetzt ~{max(1, round(len(todo) / 150))} Min.", flush=True)
        _progress("anreichern", _base, _base + len(todo), progress_dir)

    def enrich_one(k, e, c, stale):
        if relink and c:
            # Schnell-Pfad: Metadaten aus dem Cache behalten, nur den Reader-Link neu aufloesen.
            nc = dict(c)
            if not nc.get("novel"):
                # GLEICHE Ziel-Logik wie der Vollpfad (Bug-Fix: hier stand noch chap+1 hartcodiert ->
                # relinkte Serien zeigten aufs naechste statt aktuelle Kapitel): Ziel = aktuelles, gedeckelt.
                next_chap = int(e["chap"]) if e.get("chap") else 1
                _lat = nc.get("latest")
                if _lat and next_chap > _lat and (nc.get("conf") or 0) >= 0.7:
                    next_chap = int(_lat)
                links = _live_links(c.get("read_urls"))
                _chap_known = bool(e.get("chap"))
                # Override VORAB (alle Titelvarianten, engl. Alt-Namen!) -> Seiten-Overrides
                # werden zu Ernte-Kandidaten (JB Runde 32: comix/In-Spectre).
                ov_cand = [c.get("title_en"), c.get("title_romaji"), c.get("title"), e.get("name")] + (c.get("alt_titles") or [])
                ov_url, ov_site, _ov_tpl, _ov_pin = readerlink.override_info([x for x in ov_cand if x], next_chap)
                # mangadex-SEITEN-Override -> exaktes Kapitel (JB-Regel 14.07. 'Kapitel vor Seite')
                ov_url, ov_site = _resolve_md_page_override(ov_url, ov_site, _ov_tpl,
                                                            next_chap, not _chap_known)
                if not links or (links and readerlink.is_chapter_url(links[0][0]) != _chap_known):
                    # Reparatur-Pass (JB Runde 27/31/32), SYMMETRISCH: repariert Serien OHNE
                    # Link, Serien-SEITEN trotz bekanntem Lesestand (Jigokuraku-Klasse) UND
                    # Kapitel-Links trotz '?' (Bookworm/gilgamesh-Klasse -> Serien-Seite).
                    # Ersetzt wird nur, wenn die Suche etwas Passenderes findet.
                    _ts = [t for t in ([c.get("title"), e.get("name"), c.get("title_romaji"),
                                        c.get("title_native")] + (c.get("alt_titles") or [])) if t]
                    _hosts = [r.get("host") for r in sorted(e.get("readers") or [],
                                                            key=lambda r: -(r.get("visits") or 0))
                              if r.get("host")]
                    _pages = _harvest_pages(e, ov_url, ov_site, no_prog=not _chap_known)
                    neu = []
                    if _chap_known:
                        bm_url, bm_site = _bookmark_link(e, next_chap, _ts)   # Stufe 0
                        if bm_url:
                            neu = [[bm_url, bm_site]]
                    if not neu:
                        neu = _live_links(find_read_links(_ts, next_chap, mtype=c.get("type"),
                                                          prefer_hosts=_hosts,
                                                          prefer_page=not _chap_known,
                                                          extra_pages=_pages,
                                                          adult=(c.get("adult_kind") == "sexual")))
                    # (MangaDex-Lese-Fallback entfernt, JB 14.07.: 'mangadex ist tot' zum Lesen.)
                    if neu:
                        links = neu
                # MangaFire-API-Upgrade (JB-Goal 14.07.): kein echter Kapitel-Link vorn +
                # bekannter Lesestand -> exaktes Kapitel aus MangaFires JSON-API (Serien-Seite raus).
                if (_chap_known and not (links and readerlink.is_chapter_url(links[0][0]))):
                    _mf_ts = [t for t in ([c.get("title"), c.get("title_en"), c.get("title_romaji"),
                                           c.get("title_native"), e.get("name")]
                                          + (c.get("alt_titles") or [])) if t]
                    try:
                        u_mf, s_mf = mf_chapter_link(_mf_ts, next_chap)
                        if u_mf:
                            links = [[u_mf, s_mf]] + [l for l in (links or []) if l[0] != u_mf]
                    except Exception:
                        pass
                # Override-Vorrang dreistufig (siehe Vollpfad; JB-Wurzelfund Runde 32:
                # auto-{n}-Overrides erzwangen bei '?' wieder chapter-1). Kapitel-Override =
                # {n}-Vorlage ODER Kapitel-URL (Runde 35: arenascan-Muster traegt kein Token).
                # "pin": true schlaegt alle Stufen NUR noch als KAPITEL-Override (JB-Regel
                # 14.07. 'Kapitel vor Seite'); eine gepinnte SEITE macht Kapitel-Links Platz.
                _ov_chap = bool(ov_url) and (_ov_tpl or readerlink.is_chapter_url(ov_url))
                ov_used = bool(ov_url) and (
                    (_ov_pin and _ov_chap)
                    or (_ov_chap and _chap_known)
                    or (not _ov_chap and (not links
                                          or not readerlink.is_chapter_url(links[0][0])))
                    or (_ov_chap and not _chap_known and not links))
                if ov_used:                             # JBs Override -> als Primaerlink
                    links = [[ov_url, ov_site]] + [l for l in links if l[0] != ov_url]
                elif ov_url and all(l[0] != ov_url for l in links):
                    links = links + [[ov_url, ov_site]]  # kuratierter Link bleibt Reserve (+Alt)
                # RATCHET (Bug-Fix 14.07.: ein Voll-Relink degradierte 65 mangafire-Kapitel-Links
                # zurueck auf Serienseiten, als die API unter Throttling nichts lieferte). Wie im
                # Voll-Pfad: hatte der Cache einen KAPITEL-Link und die neue Aufloesung endet auf
                # einer Serien-Seite, den gecachten Kapitel-Link zurueckholen — nur besser, nie
                # schlechter. AUSSER ein kuratierter Override steht bewusst vorn (ov_used).
                if _chap_known and not ov_used and not (links and readerlink.is_chapter_url(links[0][0])):
                    alt = _live_links(c.get("read_urls"))
                    if alt and readerlink.is_chapter_url(alt[0][0]):
                        links = alt + [l for l in links if l[0] != alt[0][0]]
                links = keep_last_good(links, c)         # FAILSAFE (s. Voll-Pfad)
                links = [l for l in links if not is_no_read(host(l[0]))]  # mangadex nie als Lese-Link
                nc["read_urls"] = links
                nc["read_url"], nc["read_site"] = (tuple(links[0]) if links else ("", ""))
                nc["read_chap"] = next_chap
                nc["ov"] = ov_used                  # kuratierter Override -> Vorrang vor Bookmark
            # "Hilfe" nur bei echtem Problem: mit funktionierendem Weiterlesen-Link keine Hilfe noetig.
            nc["needs_help"] = bool(nc.get("needs_help")) and not nc.get("read_urls")
            with lock:
                cache[k] = nc
                done[0] += 1
                if done[0] % 100 == 0:
                    print(f"  ... relink {done[0]}/{len(todo)} ({int(time.time() - t_start)}s)", flush=True)
            return
        tries = (c.get("tries", 0) + 1) if c else 1
        prev_link = c.get("link_ok") if c else None
        fix = name_fix.get(k)
        slugs = slugs_for(e)
        # Ein Override steuert das MATCHING nur mit Pin/Suchbegriff; reine Daten-Overrides
        # (z.B. nur "author") laufen durch die normale Aufloesung.
        if fix and (fix.get("mb_id") or fix.get("search")):
            if fix.get("mb_id"):                # Ground-Truth-Pin: Match FEST auf diese MangaBaka-ID
                rec, conf, src = catalog.lookup_id(fix["mb_id"])
            else:
                rc_fix, pref_fix = read_hints(e)
                rec, conf, src = catalog.lookup(fix["search"], slugs, read_chap=rc_fix, prefer_novel=pref_fix)
            needs_help = not rec
        else:
            # Beim Retry eines ungematchten/Fallback-Eintrags auch mit dem zuletzt aufgeloesten,
            # SAUBEREN Titel gegen MangaBaka suchen (der rohe Scan-Name ist oft verrauscht).
            extra = [c["title"]] if (c and c.get("title") and not str(c.get("md_id") or "").startswith("mb:")) else []
            rec, conf, src, needs_help = resolve(e, extra)
        if src == "error":          # R6 (JB 07.07.2026): transienter Quellen-Fehler (429/Netz) verbraucht
            tries = c.get("tries", 0) if c else 0   # KEINEN Retry -> Serie bleibt dran, bis MangaBaka echt antwortet
        rec = rec or {}
        mb_id = rec.get("mb_id")
        did = (f"mb:{mb_id}" if isinstance(mb_id, int) else mb_id) if mb_id else None
        typ = (rec.get("type") or (fix.get("type") if fix else "") or "").lower()
        # LETZTE Instanz (JB-Regel): die Serie wird auf webtoons.com gelesen und keine DB kennt
        # den Typ (oder nennt ihn nur 'oel' = Original English) -> es IST ein Webtoon (Room of
        # Swords, Ordeal, ...). Bei 'oel' bleibt die US-Flagge (englisches Original, kein KR).
        wt_url = next((r.get("url") for r in (e.get("readers") or [])
                       if "webtoons.com" in (r.get("url") or "")), "")
        _oel = typ == "oel"
        if wt_url and typ in ("", "oel"):
            typ = "webtoon"
        flag, country = TYPE_FLAG.get(typ, ("", ""))
        if _oel:
            flag, country = TYPE_FLAG["oel"]
        link = prev_link if (stale and prev_link is not None) else link_ok(e.get("url"))
        agg = combine_ratings(rec.get("ratings") or [])
        # Titel-Kaskade (JB Runde 40): 1. JBs fix-Override, 2. ANILIST-FIRST (redaktioneller
        # EN-Titel per ID — beendet die Fremdsprachen-Raterei), 3. MangaBaka-Wahl (en-Label +
        # gefilterte unknown), 4. Haupttitel/Rohname. Nachbrenner (MangaDex) nur, wenn der
        # gewaehlte Titel weiter Romaji klingt.
        _title = ((fix.get("name") if fix else "") or _al_first_title(rec)
                  or _english_title(rec) or rec.get("title_en") or e["name"])
        if (not (fix and fix.get("name")) and _title
                and _jap_ratio(_title.translate(_TYPO)) >= 0.5):
            _title = _en_second_source(rec) or _title
        nc = {
            "title": _title,
            "title_native": rec.get("title_native") or rec.get("title_romaji") or "",
            # Romaji + Zweittitel persistieren -> Discovery-Tools (MangaFire/mangaread) koennen auch
            # romaji-Slugs treffen (toaru-majutsu-no-index, raise-wa-tanin-ga-ii, kumo-desu-ga-nani-ka).
            "title_romaji": rec.get("title_romaji") or "",
            "alt_titles": [t for t in (rec.get("alt_titles") or []) if t][:8],
            "genres": [g for g in (rec.get("genres") or []) if g][:12],   # fuer Genre-Filter + Empfehlungen
            "type": typ,
            "flag": flag, "country": country,
            "pub_status": STATUS_DE.get((rec.get("status") or "").lower(), ""),
            "latest": rec.get("total_chapters"),
            "author": (rec.get("authors") or [""])[0] if rec.get("authors") else "",
            "md_id": did,
            # MangaDex-UUID PERSISTIEREN (Runde 29): --relink kann damit ohne MangaBaka die
            # MD-Ruecklage bauen; vorher war die UUID nur waehrend der Voll-Anreicherung greifbar.
            "mdx": (rec.get("source_ids") or {}).get("mangadex")
                   or (did if isinstance(did, str) and "-" in did else None),
            # Plattform-IDs fuer den Listen-Export (3b): MAL-XML braucht die MyAnimeList-ID; AniList-ID
            # dient dem DB-Link + kuenftigem Account-Sync. Kommen beide aus dem MangaBaka-Record.
            "mal_id": (rec.get("source_ids") or {}).get("my_anime_list"),
            "al_id": (rec.get("source_ids") or {}).get("anilist"),
            # DB-Link: MangaBaka hat keine oeffentliche Serien-Webseite (alles 404) -> auf AniList
            # verlinken (echte, funktionierende DB-Seite), wenn die AniList-ID bekannt ist.
            "md_url": (f"https://anilist.co/manga/{rec['source_ids']['anilist']}"
                       if (rec.get("source_ids") or {}).get("anilist") else ""),
            "adult_kind": adult_kind(rec),
            "cover": rec.get("cover") or "",   # Cover-URL -> Hover-Vorschau (laedt NUR bei Hover)
            "novel": typ in NOVEL_TYPES,
            "conf": round(conf, 2), "src": src, "needs_help": needs_help,
            "link_ok": link, "tries": tries, "v": cache_ver,
        }
        # Aktueller Stand fuer LAUFENDE Serien: kennt die DB keine total_chapters, das live-Kapitel
        # von MangaDex holen (Aggregate) -> "aktueller Stand"/"neu" bleiben nicht leer. Nur mit
        # bekannter MangaDex-UUID (kein Fehlmatch). Systemisch: greift auch fuer alle kuenftigen Serien.
        if not nc.get("latest") and not nc.get("novel"):
            mdx = (rec.get("source_ids") or {}).get("mangadex")
            if not mdx and did and "-" in str(did):        # md_id ist bereits eine MangaDex-UUID
                mdx = did
            if mdx:
                lt = md_latest(mdx)
                if lt:
                    nc["latest"] = lt
        if agg:
            nc["rating"], nc["rating_n"], nc["ratings"] = agg
        # Cover-Fallback-Kette (JB: 'wenn eine Quelle kein Bild hat, nimm die naechste'):
        # MangaBaka -> MangaDex ueber bekannte UUID -> MangaDex ueber STRENGE Titelsuche
        # (>=0.8, sonst falsches Bild) -> AniList. Der MangaDex-Treffer fuellt nebenbei ein
        # fehlendes Land auf (JB: Soul Anomaly hat einen japanischen Titel -> 🇯🇵 statt leer).
        if not nc["cover"] and not nc["novel"]:
            try:
                from . import sources as S
                mdx2 = (rec.get("source_ids") or {}).get("mangadex")
                if not mdx2 and did and "-" in str(did):
                    mdx2 = did
                if not mdx2:
                    import difflib as _dl
                    hit = S.md_lookup(nc["title"]) or {}
                    if hit.get("md_id") and _dl.SequenceMatcher(
                            None, norm(nc["title"]), norm(hit.get("title") or "")).ratio() >= 0.8:
                        mdx2 = hit["md_id"]
                        # MangaDex liefert Flagge/Land/Autor gleich mit -> Luecken auffuellen
                        # (JB-Fall Soul Anomaly: laut MD ein ENGLISCHES Original -> 🇺🇸, nicht JP)
                        if hit.get("country") and not nc["country"]:
                            nc["flag"], nc["country"] = hit.get("flag") or "", hit["country"]
                        if hit.get("author") and not nc["author"]:
                            nc["author"] = hit["author"]
                if mdx2:
                    nc["cover"] = S.md_cover(mdx2) or ""
                if not nc["cover"] and nc.get("al_id"):
                    nc["cover"] = S.al_cover(nc["al_id"]) or ""
            except Exception:
                pass
        # Webtoon-Originale: Autor steht auf der webtoons.com-Serienseite (JB: Enjelicious, Mongie,
        # Zogarth, ... - die Manga-DBs kennen diese Werke/Autoren nicht). Best-effort, nie stoerend.
        if not nc["author"] and wt_url:
            try:
                from .sources import webtoon_author
                nc["author"] = webtoon_author(wt_url) or ""
            except Exception:
                pass
        # Autor als Override-DATUM (Serien, die von der Plattform verschwunden sind, z.B. Room of
        # Swords: webtoons-Seite 404 -> kein Fetch der Welt hilft; JB kennt den Autor).
        if fix and fix.get("author") and not nc["author"]:
            nc["author"] = fix["author"]
        # "weiterlesen" = verifizierter Reader-Kapitel-Link (konstruiert + per echtem 404 geprueft).
        # Ziel = dein AKTUELLES Kapitel (JB: man hoert oft MITTEN im Kapitel auf — und der Klick auf
        # Kapitel N+1 wuerde den Verlauf/Zaehler faelschlich hochzaehlen). Backlog (nichts gelesen) -> 1.
        next_chap = int(e["chap"]) if e.get("chap") else 1
        # JB-Entscheidung (Kapitel-Deckelung auch fuers LINK-Ziel): stammt der Lesestand aus einer
        # aufgeblaehten Zaehlung (alte asuracomic-IDs: 160 statt 100), wuerde chapter-161 konstruiert
        # -> existiert nicht (toongod leitet auf die Serienseite um). Bei sicherem Match deshalb aufs
        # letzte EXISTIERENDE Kapitel (DB-Gesamt) deckeln -> aufgeholt = Link zum neuesten Kapitel.
        _lat_cap = nc.get("latest")
        if _lat_cap and next_chap > _lat_cap and (conf or 0) >= 0.7 and not nc["novel"]:
            next_chap = int(_lat_cap)
        if nc["novel"]:
            nc["read_url"], nc["read_site"], nc["read_urls"], nc["read_chap"] = "", "", [], None
        elif (not force) and c and c.get("read_chap") == next_chap and c.get("read_urls") is not None:
            nc["read_urls"] = _live_links(c.get("read_urls"))
            nc["read_url"], nc["read_site"] = (tuple(nc["read_urls"][0]) if nc["read_urls"] else ("", ""))
            nc["read_chap"] = next_chap
            nc["ov"] = bool(c.get("ov"))    # Override-Vorrang MIT-kopieren (BUG-Fix: ging beim
                                            # Wiederverwenden verloren -> Bookmark schlug den Override)
        else:
            # Titel-Varianten fuer die Slug-Suche: Katalog (EN/romaji/native/alt) + Roh-Name +
            # MangaDex-Recovery-Titel. JB-Funde: der ROH-Name aus dem Verlauf ('Love Revolution')
            # und das ROMAJI ('Kono Yuusha ga …') fehlten hier — genau die treffen die
            # MangaFire-Sitemap-Keys, waehrend title_native (Kanji) im Slug zu nichts wird.
            titles = ([rec.get("title_en") or e["name"], e.get("name"), rec.get("title_romaji"),
                       rec.get("title_native")]
                      + (rec.get("alt_titles") or []) + (e.get("md_titles") or []))
            # Reader-Praeferenz (JB): DEINE Lese-Seiten dieser Serie zuerst (meistbesuchte vorn).
            my_hosts = [r.get("host") for r in sorted(e.get("readers") or [],
                                                      key=lambda r: -(r.get("visits") or 0)) if r.get("host")]
            # Unbekannter Lesestand ('?', JB Runde 31 Hinamatsuri/Kengan): Serien-SEITE statt
            # geratenem 'Kapitel 1' — dort entscheidet der Leser selbst, wo er einsteigt.
            no_prog = not e.get("chap")
            # JBs Override VORAB aufloesen (Runde 32): ein SEITEN-Override (comix/In-Spectre)
            # wird zur obersten Ernte-Kandidatin — aus JBs kuratierter Seite wird so das
            # exakte Kapitel gezogen; ALLE Titelvarianten anbieten (engl. Alt-Namen!).
            # Runde 35: nc['title'] (finaler ANZEIGE-Titel aus alt_en) + alt_en dazu — JBs
            # Override-Keys sind nach dem Handelstitel benannt ('topdungeonfarmer'), waehrend
            # title_en oft das Romaji/Original ist ('Solo Farming in the Tower').
            ov_cand = ([nc.get("title"), rec.get("title_en"), rec.get("title_romaji"), e.get("name")]
                       + (rec.get("alt_en") or []) + (rec.get("alt_titles") or []))
            ov_url, ov_site, _ov_tpl, _ov_pin = readerlink.override_info([x for x in ov_cand if x], next_chap)
            # mangadex-SEITEN-Override -> exaktes Kapitel (JB-Regel 14.07. 'Kapitel vor Seite')
            ov_url, ov_site = _resolve_md_page_override(ov_url, ov_site, _ov_tpl,
                                                        next_chap, no_prog)
            extra_pages = _harvest_pages(e, ov_url, ov_site, no_prog=no_prog)
            links = []
            if not no_prog:
                bm_url, bm_site = _bookmark_link(e, next_chap, titles)   # Stufe 0: DEINE Seite
                if bm_url:
                    links = [[bm_url, bm_site]]
            if not links:
                links = find_read_links(titles, next_chap, mtype=typ, prefer_hosts=my_hosts,
                                        prefer_page=no_prog, extra_pages=extra_pages,
                                        adult=(nc.get("adult_kind") == "sexual"))
            if not links:
                # Miss -> nach dem japanischen/Romaji-Titel suchen (JBs Idee): AniList kennt oft den
                # Reader-Slug ("Dungeon Meshi" statt MangaBakas "Danjon Meshi") + ein Synonym.
                a = al_lookup(rec.get("title_en") or e["name"])
                extra = [x for x in (a.get("title_romaji"), a.get("title_alt")) if x]
                if extra:
                    links = find_read_links(titles + extra, next_chap, mtype=typ,
                                            prefer_hosts=my_hosts, prefer_page=no_prog,
                                            extra_pages=extra_pages,
                                            adult=(nc.get("adult_kind") == "sexual"))
            if not links and nc.get("mdx"):
                # 2. Retry (JB Runde 29, Assassin/Memories): MangaDex-AltTitles nachladen —
                # MangaBakas Romaji weicht oft komplett ab ('Ansatsu Kizoku'), erst MangaDex
                # listet die Reader-Schreibweisen ('Sekai Saikyou no Assassin …', 'Her Memories').
                md_ts = md_titles_from_url(f"https://mangadex.org/title/{nc['mdx']}")
                if md_ts:
                    links = find_read_links(titles + md_ts, next_chap, mtype=typ,
                                            prefer_hosts=my_hosts, prefer_page=no_prog,
                                            extra_pages=extra_pages,
                                            adult=(nc.get("adult_kind") == "sexual"))
            links = _live_links(links)          # Sperrliste auch auf frische Treffer (Pattern-Reader)
            # Override-Vorrang (JB Runden 31+32, dreistufig):
            #   Kapitel-Override + ECHTER Lesestand  -> schlaegt alles.
            #   Kapitel-Override + '?'               -> NICHT vorstellen ('?' will die Serien-
            #       Seite; die ~600 auto-mangafire-{n}-Overrides erzwangen sonst 'chapter-1'
            #       direkt NACH der Reparatur — Runde-32-Wurzelfund) — nur wenn sonst NICHTS da.
            #   Seiten-Override                      -> verdraengt keinen Kapitel-Link.
            # Kapitel-Override = {n}-Vorlage ODER Kapitel-URL (Runde 35: arenascan ohne Token).
            # "pin": true schlaegt alle Stufen NUR noch als KAPITEL-Override (JB-Regel 14.07.
            # 'Kapitel vor Seite', Runde 36 Proto-Eye bleibt: dort IST der Pin ein Kapitel);
            # eine gepinnte SEITE macht verifizierten Kapitel-Links Platz und bleibt Reserve.
            _ov_chap = bool(ov_url) and (_ov_tpl or readerlink.is_chapter_url(ov_url))
            ov_used = bool(ov_url) and (
                (_ov_pin and _ov_chap)
                or (_ov_chap and not no_prog)
                or (not _ov_chap and (not links or not readerlink.is_chapter_url(links[0][0])))
                or (_ov_chap and no_prog and not links))
            if ov_used:
                links = [[ov_url, ov_site]] + [l for l in links if l[0] != ov_url]
            elif ov_url and all(l[0] != ov_url for l in links):
                links = links + [[ov_url, ov_site]]      # kuratierter Link bleibt Reserve (+Alt)
            # MangaFire-API (JB-Goal 14.07., GitHub-Fund): steht noch KEIN echter Kapitel-Link
            # vorn (leer oder nur Serien-Seite), loest MangaFires interne JSON-API das exakte
            # Kapitel auf — genau JBs Klage 'viele mangafire-Links fuehren zur Mangaseite'.
            # Nur bei bekanntem Lesestand; der Treffer wird als Kapitel-Link vorangestellt.
            if (not no_prog and not ov_used
                    and not (links and readerlink.is_chapter_url(links[0][0]))):
                try:
                    u_mf, s_mf = mf_chapter_link([t for t in titles if t], next_chap)
                    if u_mf:
                        links = [[u_mf, s_mf]] + [l for l in links if l[0] != u_mf]
                except Exception:
                    pass
            # Dynasty Reader (Guya-API, JB-Goal 14.07.): Doujin/Yuri, die die grossen DBs oft
            # nicht fuehren -> echte Zusatz-Abdeckung. Nur wenn immer noch kein Kapitel-Link da.
            if (not no_prog and not ov_used
                    and not (links and readerlink.is_chapter_url(links[0][0]))):
                try:
                    u_dy, s_dy = dy_chapter_link([t for t in titles if t], next_chap)
                    if u_dy:
                        links = [[u_dy, s_dy]] + [l for l in links if l[0] != u_dy]
                except Exception:
                    pass
            # (MangaDex-LESE-Ruecklage entfernt, JB 14.07.2026: 'mangadex ist tot' zum Lesen —
            #  Kapitel laden ewig/gar nicht. Bleibt Datenquelle. Ohne anderen Link -> ehrliche
            #  Suche statt eines mangadex-Links, der ins Leere laedt.)
            # RATCHET (JB Runde 35, 'wieder und wieder'): ein frueher gefundener KAPITEL-Link
            # darf NIE durch eine blosse Serien-Seite ersetzt werden, nur weil eine Netz-
            # Stufe unter Parallel-Last scheiterte — Links werden nur besser, nie schlechter.
            # AUSSER JBs kuratierter Override steht vorn: der gilt auch dann, wenn sein
            # URL-Muster kein erkennbares Kapitel-Token traegt (arenascan 'solo-leveling-109/'
            # — sonst holte der Ratchet die alte Spam-Seite aus dem Cache zurueck).
            if c and e.get("chap") and c.get("read_chap") == next_chap and not ov_used:
                alt_links = _live_links(c.get("read_urls"))
                if (alt_links and readerlink.is_chapter_url(alt_links[0][0])
                        and not (links and readerlink.is_chapter_url(links[0][0]))):
                    links = alt_links
            links = keep_last_good(links, c)     # FAILSAFE: nie durch einen Fehl-Lauf verlieren
            links = [l for l in links if not is_no_read(host(l[0]))]  # mangadex nie als Lese-Link
            nc["read_urls"] = links
            nc["read_url"], nc["read_site"] = (links[0] if links else ("", ""))
            nc["read_chap"] = next_chap
            nc["ov"] = ov_used                      # kuratierter Override -> Vorrang vor Bookmark
        # "Hilfe" nur bei echtem Problem: wer einen funktionierenden Weiterlesen-Link hat, braucht
        # keine Hilfe (Haikyu/Jujutsu Kaisen 0 waren so faelschlich geflaggt, obwohl alles ging).
        nc["needs_help"] = bool(nc.get("needs_help")) and not nc.get("read_urls")
        old_latest = c.get("latest") if c else None             # neue Kapitel seit letztem Lauf?
        if old_latest and nc.get("latest") and nc["latest"] > old_latest and not nc.get("novel"):
            new_chaps.append(nc["title"])
        snap = None
        with lock:
            cache[k] = nc
            done[0] += 1
            if done[0] % 5 == 0:
                _progress("anreichern", _base + done[0], _base + len(todo), progress_dir)
            if done[0] % 25 == 0:
                _save_cache(cache, cache_path)
                print(f"  ... {done[0]}/{len(todo)} angereichert ({int(time.time() - t_start)}s)", flush=True)
            # Zwischen-Render (JB: 'so oft wie Mangas reinkommen'): alle 5 Serien — seit dem
            # dynamischen Nachladen ist das nur noch ein sanfter Zeilen-Tausch, kein Reload.
            # GERENDERT wird ausserhalb des Locks (<1s), die Threads laufen ungebremst weiter.
            if checkpoint_render and done[0] % 5 == 0:
                try:
                    snap = (_snapshot_items(items), dict(cache), done[0])
                except Exception:
                    snap = None
        if snap:
            try:
                checkpoint_render(assemble_rows(snap[0], snap[1], name_fix))
                _progress("anreichern", _base + snap[2], _base + len(todo), progress_dir, rendered=True)
            except Exception as ex:            # best-effort, aber NIE stumm (JB-Fund: Liste blieb
                print(f"  [Zwischen-Render] übersprungen: {type(ex).__name__}: {ex}", flush=True)

    probe_sources(health_dir)
    with ThreadPoolExecutor(max_workers=10) as ex:
        for fut in [ex.submit(enrich_one, k, e, c, st) for (k, e, c, st) in todo]:
            fut.result()
    _save_cache(cache, cache_path)
    _progress("fertig", _base + len(todo), _base + len(todo), progress_dir)
    try:
        srcstatus.save(os.path.join(os.path.dirname(cache_path), "source_status.json"))
    except Exception:
        pass
    try:                            # neue Kapitel -> data/new_chapters.json (Tray liest + meldet)
        ncp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "new_chapters.json")
        json.dump({"count": len(new_chaps), "names": new_chaps[:50], "ts": time.time()},
                  open(ncp, "w", encoding="utf-8"), ensure_ascii=False)
    except Exception:
        pass

    return assemble_rows(items, cache, name_fix)


def assemble_rows(items, cache, name_fix):
    """ENDMONTAGE (herausgeloest fuer Zwischen-Renders, JB: 'erste Serien schon zeigen'):
    Cache-Werte in die items uebernehmen, Overrides anwenden, Dedup (ID + Name) -> rows.
    ACHTUNG: mutiert `items` — fuer Zwischen-Renders deshalb IMMER mit Kopien aufrufen."""
    # Angereicherte Werte aus dem Cache in die items uebernehmen
    for k, e in items.items():
        c = cache.get(k)
        if c:
            e["enriched"] = True
            e.update({kk: c.get(kk) for kk in ("country", "flag", "type", "latest", "pub_status",
                                               "md_id", "md_url", "link_ok", "rating", "rating_n",
                                               "ratings", "author", "novel", "adult_kind",
                                               "title_native", "needs_help", "conf", "src", "genres",
                                               "read_url", "read_site", "read_urls", "ov",
                                               # read_chap mitkopieren (Runde 35): _merge_action
                                               # vergleicht Zwillinge nach AKTUALITAET des Ziels —
                                               # ohne das Feld gewann der zuerst gesehene 'Vol.'-
                                               # Zwilling (Kapitel 6) gegen den 112er.
                                               "read_chap", "last_group",
                                               "lh_status",     # Link-Health (R7): fuer den Anzeige-Marker
                                               "mal_id", "al_id", "cover",
                                               # Titel-Varianten fuer die Archiv-Migration (Runde 35):
                                               # alte localStorage-Schluessel = norm(alter Anzeigetitel)
                                               # -> render baut daraus die Alias-Map MIG
                                               "title_romaji", "alt_titles")})
            if c.get("title"):
                e["md_title"] = c["title"]

    def _merge_action(o, e):
        """Aktions-Felder (read_url/read_urls/ov) beim Zwillings-Merge VEREINEN — kein Link geht verloren.

        JB 07.07.2026 ('unter einen Deckelhut'): frueher wurden die read_urls des einen Zwillings
        durch die des anderen ERSETZT -> stand der linklose Zwilling 'frischer' da, verschwand der
        Link des anderen und die Zeile fiel auf 'Alternative'. Jetzt: read_urls ALLER Zwillinge werden
        vereint (Dubletten raus); den PRIMAERLINK (vorne) stellt weiterhin der Zwilling mit dem
        aktuellsten Ziel (hoechstes read_chap) bzw. ein Override (JB Runde 35, Million Lives)."""
        merged = [list(ln) for ln in (o.get("read_urls") or []) if ln and ln[0]]
        seen = {ln[0] for ln in merged}
        for ln in (e.get("read_urls") or []):
            if ln and ln[0] and ln[0] not in seen:
                merged.append(list(ln)); seen.add(ln[0])
        fresher = e.get("read_url") and ((e.get("read_chap") or 0) > (o.get("read_chap") or 0)
                                         or not o.get("read_url"))
        ov_win = (e.get("ov") and not o.get("ov")
                  and (e.get("read_chap") or 0) >= (o.get("read_chap") or 0))
        if fresher or ov_win:
            for f in ("ov", "read_url", "read_site", "read_chap"):
                o[f] = e.get(f)
            if e.get("read_url"):               # neuen Primaerlink nach vorne, Rest als Reserve
                merged = [[e["read_url"], e.get("read_site") or ""]] + [ln for ln in merged if ln[0] != e["read_url"]]
        o["read_urls"] = merged
        if not o.get("read_url") and merged:    # o selbst hatte keinen -> ersten vereinten nehmen
            o["read_url"], o["read_site"] = merged[0][0], (merged[0][1] if len(merged[0]) > 1 else "")

    # Dedup: kanonische ID (JP/EN -> ein Eintrag), dann ueber den finalen englischen Namen
    by_id, keep = {}, {}
    for k, e in items.items():
        # Roh-Schluessel MERKEN (Runde 35, Archiv-Reset): k = norm(Verlaufsname) ist stabil ueber
        # Titelkorrekturen hinweg -> render nutzt ihn als data-h, wenn keine DB-ID existiert.
        e.setdefault("hkeys", [k])
        if e.get("md_title"):
            e["name"] = e["md_title"]
        fix = name_fix.get(k) or name_fix.get(norm(e["name"]))
        if fix:
            if fix.get("hide"):                 # kein Manga (Doujin/Novel/Seite) -> ganz raus
                continue
            if fix.get("name"):
                e["name"] = fix["name"]
            pin = fix.get("baka") or fix.get("mb_id")   # erzwungene MangaBaka-ID -> Baka-Pill + Dedup
            if pin:
                e["md_id"] = f"mb:{pin}"
        mid = e.get("md_id")
        if mid and mid in by_id:
            o = by_id[mid]
            (o.setdefault("readers", [])).extend(e.get("readers") or [])
            (o.setdefault("hkeys", [])).extend(e.get("hkeys") or [])
            if (e.get("chap") or 0) > (o.get("chap") or 0):
                o["chap"] = e["chap"]; o["url"] = e["url"]
            o["lv"] = max(o.get("lv", 0), e.get("lv", 0))
            # Fehlende Metadaten aus dem Zwilling ergaenzen: matcht ein Zwilling (z.B. via baka)
            # besser als der andere, darf die gemergte Zeile nicht "unbekannt" bleiben, nur weil der
            # leere Zwilling zuerst gesehen wurde. Fuellt nur LEERE Felder (nie Gutes ueberschreiben).
            for f in ("pub_status", "author", "latest", "rating", "rating_n", "ratings", "genres",
                      "adult_kind", "type", "flag", "country", "title_native", "md_url"):
                if not o.get(f) and e.get(f):
                    o[f] = e[f]
            _merge_action(o, e)
            continue
        if mid:
            by_id[mid] = e
        keep[k] = e
    seen, final = {}, []
    for e in keep.values():
        if e.get("novel"):
            continue
        nk = norm(e["name"])
        o = seen.get(nk)
        if o is None:
            seen[nk] = e
            final.append(e)
            continue
        # Gleicher Name = derselbe Manga auf zwei Seiten -> EINE Zeile. Reader/Kapitel vereinigen.
        (o.setdefault("readers", [])).extend(e.get("readers") or [])
        (o.setdefault("hkeys", [])).extend(e.get("hkeys") or [])
        if (e.get("chap") or 0) > (o.get("chap") or 0):
            o["chap"], o["url"] = e["chap"], e["url"]
        o["lv"] = max(o.get("lv", 0), e.get("lv", 0))
        # WICHTIG (JB-Screenshots): matchte nur EIN Zwilling MangaBaka (md_id) und der andere fiel auf
        # Fallback zurueck (conf 0.5, leer), gewinnt der ECHTE Treffer bei den Metadaten -> nie mehr
        # "unbekannt"/keine Flagge/kein Stand, nur weil der leere Zwilling zuerst gesehen wurde. Sonst
        # nur leere Felder auffuellen (nie Gutes ueberschreiben). needs_help wird beim Render neu bestimmt.
        prefer_e = bool(e.get("md_id")) and not o.get("md_id")
        for f in ("pub_status", "author", "latest", "rating", "rating_n", "ratings", "genres",
                  "adult_kind", "type", "flag", "country", "title_native", "md_url", "md_id", "conf", "name"):
            if e.get(f) and (prefer_e or not o.get(f)):
                o[f] = e[f]
        _merge_action(o, e)
    return final
