# -*- coding: utf-8 -*-
"""
Quellen-Adapter des Manga-Kerns (MangaDex, AniList, MangaUpdates, Kitsu, MyAnimeList/Jikan)
+ MangaDex-Statistik (md_rating) + Link-Erreichbarkeit (link_ok).

Aus SyncEngine/manga_update.py herausgelöst (Phase 2.2). Verhalten unveraendert; der
HTTP-Aufbau läuft jetzt über syncmanga.common (get_json/post_json), die Tempo-Bremsen
über common.Pacer. Jeder Lookup liefert ein Dict mit normalisierten Feldern (Titel,
Flagge/Land, Status, Bewertung, Autor, …). KEINE Verhaltensänderung gegenüber vorher.

Ergänzen einer Quelle = neue lookup-Funktion hier + eine Zeile in enrich_one / probe_sources.
(Eine echte Registry-Datenstruktur folgt bei Bedarf in einer späteren Phase.)
"""
import re
import time
import difflib
import urllib.parse
import urllib.request
import urllib.error

from .common import UA, Pacer, get_json, post_json
from .parse import norm, pick_english

# Tempo-Bremsen je Quelle (threadsicher, global) — Limits siehe Kommentare.
AL_PACER = Pacer(0.7)    # AniList: < ~85 Anfragen/Min
MD_PACER = Pacer(0.2)    # MangaDex: < ~5 Anfragen/Sek
MU_PACER = Pacer(0.3)    # MangaUpdates: konservative Bremse gegen Drosselung (10 Threads parallel)
KITSU_PACER = Pacer(0.3)  # Kitsu: konservative Bremse gegen Drosselung
JK_PACER = Pacer(1.1)    # Jikan/MyAnimeList: < 60 Anfragen/Min


# ---------------- MangaDex ----------------
API_MD = "https://api.mangadex.org"
LANG_FLAG = {"ja": ("Japan", "🇯🇵"), "ko": ("Korea", "🇰🇷"), "zh": ("China", "🇨🇳"),
             "zh-hk": ("China", "🇨🇳"), "en": ("USA", "🇺🇸")}
MD_STATUS = {"completed": "Abgeschlossen", "ongoing": "Laufend",
             "hiatus": "Hiatus", "cancelled": "Abgebrochen"}


def md_lookup(name):
    out = {"md_id": None, "flag": "", "country": "", "latest": None, "pub_status": "", "title": "",
           "md_url": "", "author": "", "content_rating": "", "ecchi": False, "gore": False}
    try:
        q = urllib.parse.urlencode(
            {"title": name, "limit": 5,
             "contentRating[]": ["safe", "suggestive", "erotica", "pornographic"],
             "includes[]": ["author", "artist"]}, doseq=True)
        MD_PACER.wait()
        data = get_json(f"{API_MD}/manga?{q}").get("data", [])
        if not data:
            return out
        nn = norm(name)

        def titles_of(m):
            a = m.get("attributes", {})
            ts = list(a.get("title", {}).values())
            for alt in a.get("altTitles", []):
                ts += list(alt.values())
            return ts

        def score(m):
            ratio = max((difflib.SequenceMatcher(None, nn, norm(t)).ratio() for t in titles_of(m)), default=0)
            # Bei (fast) gleichem Titel die kanonische Serie bevorzugen statt eines gleichnamigen
            # Porno-Doujins (sonst falsches 18+/Bewertung/Autor). Kleiner Malus bricht nur den Gleichstand.
            cr = (m.get("attributes", {}) or {}).get("contentRating", "")
            return ratio - (0.05 if cr in ("erotica", "pornographic") else 0.0)
        best = max(data, key=score)
        a = best.get("attributes", {})
        out["md_id"] = best.get("id")
        out["md_url"] = f"https://mangadex.org/title/{best.get('id')}"
        # ALLE Titel-Varianten des Treffers (JB Runde 40): der Aehnlichkeits-Waechter des
        # Reserve-Auffuellers vergleicht dagegen — 'The Lie Eater' matcht MDs 'Usogui' nur
        # ueber die altTitles, nicht ueber den Haupttitel.
        out["all_titles"] = titles_of(best)[:12]
        # Immer englischen Titel bevorzugen: title.en -> altTitles.en -> erstes lateinisches -> erstes
        ttl = a.get("title", {})
        alts = a.get("altTitles", [])
        # ALLE englischen Kandidaten (Haupttitel + alle Alt-Titel) -> den englischsten waehlen.
        # MangaDex fuehrt oft den Romaji unter "en"; der echte EN-Titel steckt in altTitles.
        en_cands = ([ttl["en"]] if ttl.get("en") else []) + [alt["en"] for alt in alts if alt.get("en")]
        if en_cands:
            out["title"] = pick_english(en_cands)
        else:
            lat = next((v for d in [ttl] + alts for v in d.values() if re.search(r'[A-Za-z]', v)), "")
            out["title"] = lat or next(iter(ttl.values()), "")
        cn, fl = LANG_FLAG.get(a.get("originalLanguage", ""), ("", ""))
        out["country"], out["flag"] = cn, fl
        out["pub_status"] = MD_STATUS.get(a.get("status", ""), "")
        out["content_rating"] = a.get("contentRating", "")    # safe/suggestive/erotica/pornographic
        tag_names = {(((t.get("attributes") or {}).get("name") or {}).get("en") or "").lower()
                     for t in (a.get("tags") or [])}
        out["ecchi"] = bool(tag_names & {"ecchi", "smut"})    # sexuell/fetisch-orientiert
        out["gore"] = "gore" in tag_names                     # Gewalt/Gore (z.B. Berserk)
        lc = a.get("lastChapter")
        if lc and re.match(r'^\d', str(lc)):
            try: out["latest"] = float(lc)
            except ValueError: pass
        names = []
        for rel in best.get("relationships", []):
            if rel.get("type") in ("author", "artist"):
                nm = (rel.get("attributes") or {}).get("name")
                if nm and nm not in names:
                    names.append(nm)
        out["author"] = ", ".join(names[:2])
    except Exception:
        pass
    return out


def _agg_chapters(agg):
    """Kapitelnummern aus einer MangaDex-Aggregate-Antwort -> Liste floats (plausible Werte)."""
    out = []
    for v in ((agg or {}).get("volumes") or {}).values():
        for cn in (v.get("chapters") or {}):
            try:
                f = float(cn)
                if 0 < f <= 5000:          # unplausible Riesen-/Spam-Nummern verwerfen (wie parse.MAX_CHAPTER)
                    out.append(f)
            except (TypeError, ValueError):
                pass
    return out


def md_latest(md_id):
    """Aktuellstes verfuegbares Kapitel via MangaDex-Aggregate. Fuer LAUFENDE Serien, deren DB keine
    total_chapters kennt (dann blieben 'aktueller Stand' und 'neu' leer). Braucht die MangaDex-UUID
    (kein Fehlmatch-Risiko). Zuerst EN (was JB lesen kann), sonst alle Sprachen (Stand der Story).
    Gibt float | None. Netz ueber get_json (mockbar)."""
    if not md_id:
        return None
    try:
        MD_PACER.wait()
        chaps = _agg_chapters(get_json(f"{API_MD}/manga/{md_id}/aggregate?translatedLanguage[]=en"))
        if not chaps:
            MD_PACER.wait()
            chaps = _agg_chapters(get_json(f"{API_MD}/manga/{md_id}/aggregate"))
        return max(chaps) if chaps else None
    except Exception:
        return None


def _agg_chapter_id(agg, chapter):
    """Aggregate-JSON -> Kapitel-UUID fuer `chapter` (exakter Vergleich, sonst '') — rein, testbar."""
    try:
        want = float(chapter)
    except (TypeError, ValueError):
        return ""
    for vol in (agg.get("volumes") or {}).values():
        for ch in (vol.get("chapters") or {}).values():
            try:
                if float(ch.get("chapter")) == want and ch.get("id"):
                    return ch["id"]
            except (TypeError, ValueError):
                continue
    return ""


def _agg_first_chapter_id(agg):
    """Kleinste existierende Kapitelnummer im Aggregate -> UUID ('' wenn leer) — rein, testbar."""
    best_n, best_id = None, ""
    for vol in (agg.get("volumes") or {}).values():
        for ch in (vol.get("chapters") or {}).values():
            try:
                n = float(ch.get("chapter"))
            except (TypeError, ValueError):
                continue
            if ch.get("id") and (best_n is None or n < best_n):
                best_n, best_id = n, ch["id"]
    return best_id


def _md_chapter_readable(cid):
    """True, wenn das MangaDex-Kapitel dort WIRKLICH lesbar ist (JB 14.07.: 'wir hatten da
    schon haeufiger tote Links'). Das Aggregate listet auch EN-Kapitel, die auf MangaDex
    selbst keine Seiten haben: extern gehostete (externalUrl, z.B. MangaPlus — dort oft
    laender-gesperrt) und entfernte (isUnavailable). Live geprueft 14.07.2026: One Piece
    EN traegt pages=0 + externalUrl. API-Fehler -> False (nur BEWIESEN Lesbares zaehlt)."""
    try:
        MD_PACER.wait()
        a = ((get_json(f"{API_MD}/chapter/{cid}") or {}).get("data") or {}).get("attributes") or {}
        return (not a.get("isUnavailable") and not a.get("externalUrl")
                and (a.get("pages") or 0) > 0)
    except Exception:
        return False


def md_chapter_link(md_id, chapter, chapter_only=False):
    """VERIFIZIERTER MangaDex-Link als letzte Link-Ruecklage -> (url, 'mangadex.org') | ('', '').

    JB Runde 29 (Penisman/helvetica/Dr. Savior): die MangaDex-API ist Ground-Truth und nie
    bot-blockiert. Exaktes Kapitel als UUID aus dem Aggregate — NUR ENGLISCH (JB Runde 38:
    'viele Mangas bieten dort keine Kapitel auf Englisch an' — der fruehere sprachlose
    Fallback haette sonst tuerkische/polnische Kapitel verlinkt) und NUR WIRKLICH LESBAR
    (_md_chapter_readable; JB 14.07.: extern/gesperrt gelistete Kapitel waren tote Links).
    Existiert kein lesbares EN-Kapitel:
    chapter_only=True  -> ('', '')  (Reserve-Auffueller: NUR eintragen, was wirklich lesbar ist)
    chapter_only=False -> SERIEN-Seite (letzte Ruecklage der Hauptpipeline, Label 'öffnen')."""
    if not md_id:
        return "", ""
    try:
        MD_PACER.wait()
        agg = get_json(f"{API_MD}/manga/{md_id}/aggregate?translatedLanguage[]=en")
        cid = _agg_chapter_id(agg, chapter)
        if cid and not _md_chapter_readable(cid):
            cid = ""                    # gelistet, aber extern/gesperrt -> zaehlt wie 'kein EN'
        if not cid:
            try:
                _backlog = float(chapter) <= 1
            except (TypeError, ValueError):
                _backlog = False
            if _backlog:
                # Backlog-Start (JB Runde 41, Tower into the Clouds): manche MD-Uploads
                # beginnen bei Kapitel 2 -> das KLEINSTE existierende EN-Kapitel ist der
                # ehrliche Einstieg. Mittendrin-Leser bekommen weiter NUR das exakte Kapitel.
                cid = _agg_first_chapter_id(agg)
                if cid and not _md_chapter_readable(cid):
                    cid = ""
        if cid:
            return f"https://mangadex.org/chapter/{cid}", "mangadex.org"
        if chapter_only:
            return "", ""
        return f"https://mangadex.org/title/{md_id}", "mangadex.org"
    except Exception:
        return "", ""


# ---------------- Webtoons (JB Runde 42, Option 2: offizielle Suche -> title_no) ----------
# Live verifiziert 04.07.2026: /en/search/immediate liefert JSON mit titleNo; der Episode-
# Viewer braucht NUR title_no+episode_no (Dummy-Pfad wird auf die kanonische URL
# redirectet), nicht existierende Episoden liefern ein ECHTES 404 -> voll verifizierbar.
# Fast-Pass-Modell ist JB-akzeptiert (Katalog frei, nur das Neueste kurz fuer Subs).
API_WT_SEARCH = "https://www.webtoons.com/en/search/immediate?keyword="
WT_PACER = Pacer(1.0)


def wt_chapter_link(titles, chapter):
    """Offizieller Webtoons-Episode-Link ueber die JSON-Suche -> (kanonische URL,
    'webtoons.com') | ('', ''). Waechter: Suchtreffer-Titel norm-gleich oder >=0.9."""
    try:
        n = int(float(chapter))
    except (TypeError, ValueError):
        return "", ""
    n = max(1, n)
    for q in [t for t in (titles if isinstance(titles, (list, tuple)) else [titles]) if t][:3]:
        try:
            WT_PACER.wait()
            data = get_json(API_WT_SEARCH + urllib.parse.quote(str(q)))
            lst = ((data.get("result") or {}).get("searchedList")) or []
        except Exception:
            continue
        nn = norm(q)
        for m in lst:
            t, tno = m.get("title") or "", m.get("titleNo")
            if not tno:
                continue
            if norm(t) != nn and difflib.SequenceMatcher(None, nn, norm(t)).ratio() < 0.9:
                continue
            u = (f"https://www.webtoons.com/en/x/x/episode-{n}/viewer"
                 f"?title_no={tno}&episode_no={n}")
            try:
                from .readerlink import fetch_status
                st, final, _b = fetch_status(u, timeout=10)
            except Exception:
                continue
            if st == 200 and f"title_no={tno}" in (final or ""):
                return final, "webtoons.com"      # kanonische URL nach dem Redirect
    return "", ""


# ---------------- Comick (JB Runde 39, Idee 2: zweite API-gepruefte EN-Kapitel-Quelle) ----------
# api.comick.dev (getestet 04.07.2026; .fun ist DNS-tot, .io/v1.0 404). Die Reader-URLs zeigen
# auf comick.io. Liefert je Kapitel auch group_name -> "zuletzt von X" (Idee 4) faellt mit ab.
API_CK = "https://api.comick.dev"
CK_PACER = Pacer(1.0)


def ck_chapter_link(title, chapter):
    """Comick-Kapitel-Link, NUR wenn das ENGLISCHE Kapitel nachweislich existiert
    -> (url, 'comick.io', gruppe) | ('', '', '').

    Suche per Titel mit STRENGEM Aehnlichkeits-Waechter (norm-gleich oder >=0.93 — dieselbe
    Anti-Fehlmatch-Huerde wie beim MangaDex-Nachschlag), dann chapters?lang=en&chap=N:
    exakter Kapitel-Treffer noetig (JB-Regel: nur eintragen, was WIRKLICH lesbar ist)."""
    if not title:
        return "", "", ""
    try:
        n = _ck_chapstr(chapter)
        if not n:
            return "", "", ""
        CK_PACER.wait()
        data = get_json(f"{API_CK}/v1.0/search?q={urllib.parse.quote(str(title))}&limit=5&type=comic")
        nn = norm(title)
        best, sim = None, 0.0
        for m in (data if isinstance(data, list) else []):
            r = difflib.SequenceMatcher(None, nn, norm(m.get("title") or "")).ratio()
            if r > sim:
                best, sim = m, r
        if not best or not best.get("hid") or not best.get("slug") \
                or (norm(best.get("title") or "") != nn and sim < 0.93):
            return "", "", ""
        CK_PACER.wait()
        chs = (get_json(f"{API_CK}/comic/{best['hid']}/chapters?lang=en&chap={n}&limit=10")
               .get("chapters") or [])
        # Dasselbe Kapitel liegt oft MEHRFACH vor (mehrere Scan-Gruppen, JB Runde 39):
        # deterministisch EINE Version waehlen — die mit den meisten Community-Upvotes
        # (up_count), bei Gleichstand die erstgelistete (Comick sortiert frisch zuerst).
        cands = [c for c in chs if str(c.get("chap")) == n and c.get("hid")
                 and (c.get("lang") or "en") == "en"]
        if not cands:
            return "", "", ""
        ch = max(enumerate(cands), key=lambda p: ((p[1].get("up_count") or 0), -p[0]))[1]
        grp = (ch.get("group_name") or [""])[0] or ""
        return (f"https://comick.io/comic/{best['slug']}/{ch['hid']}-chapter-{n}-en",
                "comick.io", grp)
    except Exception:
        return "", "", ""


def _ck_chapstr(chapter):
    """Kapitelzahl -> Comick-Query-String ('110', '10.5'); None/Unfug -> ''."""
    try:
        f = float(chapter)
    except (TypeError, ValueError):
        return ""
    return str(int(f)) if f == int(f) else str(f)


_MD_CHAP_URL = re.compile(r'mangadex\.org/chapter/([0-9a-f\-]{8,36}|\d+)', re.I)
_MD_TITLE_URL = re.compile(r'mangadex\.org/title/(\d+|[0-9a-f\-]{36})', re.I)


def md_titles_from_url(url, cap=5):
    """Echte Serien-Titel (ALLE Varianten, EN-Felder zuerst) aus einer MangaDex-URL rekonstruieren —
    die autoritative Rettung fuer Fragment-Namen aus dem Verlauf (JB-Faelle: 'Ryoumin' war in Wahrheit
    'The Frontier Lord Begins with Zero Subjects', 'Yowai' war 'A Herbivorous Dragon of 5,000 Years').

    Gibt eine LISTE von Titeln: MangaDex' `title.en` ist oft der Romaji ('Yowai 5000-nen ...'), der
    englische Handelstitel steckt in den altTitles — der Aufrufer probiert alle gegen den Katalog.
    Unterstuetzt Kapitel-URLs (alte numerische IDs via /legacy/mapping + UUIDs) und Titel-URLs.
    Nie eine Exception (best-effort) -> [] bei Fehlschlag."""
    try:
        manga_id = None
        m = _MD_TITLE_URL.search(url or "")
        if m and "-" in m.group(1):
            manga_id = m.group(1)
        elif m:                                   # alte numerische Titel-ID -> legacy mapping
            MD_PACER.wait()
            d = post_json(f"{API_MD}/legacy/mapping", {"type": "manga", "ids": [int(m.group(1))]})
            manga_id = ((d.get("data") or [{}])[0].get("attributes") or {}).get("newId")
        else:
            m = _MD_CHAP_URL.search(url or "")
            if not m:
                return []
            ch_id = m.group(1)
            if "-" not in ch_id:                  # alte numerische Kapitel-ID -> legacy mapping
                MD_PACER.wait()
                d = post_json(f"{API_MD}/legacy/mapping", {"type": "chapter", "ids": [int(ch_id)]})
                ch_id = ((d.get("data") or [{}])[0].get("attributes") or {}).get("newId")
            if not ch_id:
                return []
            MD_PACER.wait()
            ch = get_json(f"{API_MD}/chapter/{ch_id}")
            manga_id = next((r.get("id") for r in (ch.get("data") or {}).get("relationships", [])
                             if r.get("type") == "manga"), None)
        if not manga_id:
            return []
        MD_PACER.wait()
        at = (get_json(f"{API_MD}/manga/{manga_id}").get("data") or {}).get("attributes") or {}
        titles = [at.get("title") or {}] + (at.get("altTitles") or [])
        out = []
        for t in titles:                          # EN-Felder zuerst (Handelstitel oft in altTitles.en)
            if t.get("en") and t["en"] not in out:
                out.append(t["en"])
        for t in titles:
            for v in t.values():
                if v and v not in out:
                    out.append(v)
        return out[:cap]
    except Exception:
        return []


def md_rating(md_id):
    """MangaDex-Statistik: bayesian rating (0-10). Nutzt die schon bekannte md_id, keine Suche."""
    try:
        MD_PACER.wait()
        st = get_json(f"{API_MD}/statistics/manga/{md_id}").get("statistics", {}).get(md_id, {})
        b = (st.get("rating") or {}).get("bayesian")
        if b:
            return round(float(b), 1)
    except Exception:
        pass
    return None


# ---------------- AniList (zweite Quelle, vor allem offizieller EN-Titel) ----------------
API_AL = "https://graphql.anilist.co"
AL_QUERY = ("query($q:String){Page(perPage:5){media(search:$q,type:MANGA){"
            "id title{english romaji native} countryOfOrigin status chapters synonyms isAdult genres "
            "averageScore popularity staff(perPage:4){edges{role node{name{full}}}}}}}")
AL_COUNTRY = {"JP": ("Japan", "🇯🇵"), "KR": ("Korea", "🇰🇷"), "CN": ("China", "🇨🇳"),
              "TW": ("Taiwan", "🇹🇼"), "HK": ("China", "🇨🇳")}
AL_STATUS = {"FINISHED": "Abgeschlossen", "RELEASING": "Laufend", "HIATUS": "Hiatus",
             "CANCELLED": "Abgebrochen", "NOT_YET_RELEASED": "Angekündigt"}


AL_RECS_QUERY = """query($g:[String]){Page(perPage:50){media(type:MANGA,genre_in:$g,sort:SCORE_DESC,isAdult:false){
siteUrl averageScore genres title{english romaji}}}}"""


def al_top_by_genres(genres):
    """Bestbewertete Manga zu den Genres (AniList) -> [{title,url,score,genres}] fuer die EXTERNEN
    Empfehlungen (JB-Wunsch: echte Vorschlaege mit Link, nicht der eigene Backlog). Best-effort."""
    try:
        AL_PACER.wait()
        media = post_json(API_AL, {"query": AL_RECS_QUERY, "variables": {"g": genres}}) \
            .get("data", {}).get("Page", {}).get("media", []) or []
    except Exception:
        return []
    out = []
    for m in media:
        t = m.get("title") or {}
        title = t.get("english") or t.get("romaji") or ""
        if title and m.get("siteUrl"):
            out.append({"title": title, "url": m["siteUrl"],
                        "score": round((m.get("averageScore") or 0) / 10.0, 1) or None,
                        "genres": (m.get("genres") or [])[:4]})
    return out


AL_EN_QUERY = "query($id:Int){Media(id:$id,type:MANGA){title{english}}}"


def al_english_by_id(al_id):
    """Offizieller englischer AniList-Titel PER ID -> '' wenn unbekannt/kein EN-Titel.

    Fuer den Titel-Nachbrenner (JB Runde 37): die ID kommt aus dem MangaBaka-Record
    (source_ids.anilist) — KEIN Such-Matching, also kein Fehlmatch-Risiko. Nur gerufen,
    wenn der Haupttitel Romaji blieb und MangaBaka nichts Englisches liefert."""
    if not al_id:
        return ""
    try:
        AL_PACER.wait()
        m = (post_json(API_AL, {"query": AL_EN_QUERY, "variables": {"id": int(al_id)}})
             .get("data", {}).get("Media") or {})
        return (m.get("title") or {}).get("english") or ""
    except Exception:
        return ""


def al_lookup(name):
    """AniList (GraphQL) – offizieller englischer Titel + Land/Flagge + Status als Fallback/Ergänzung."""
    out = {"al_id": None, "title": "", "title_romaji": "", "title_alt": "", "flag": "", "country": "",
           "pub_status": "", "latest": None, "rating": None, "votes": 0, "author": "", "is_adult": False,
           "sexual_genre": False}
    try:
        data = None
        for attempt in range(2):
            try:
                AL_PACER.wait()
                data = post_json(API_AL, {"query": AL_QUERY, "variables": {"q": name}}) \
                    .get("data", {}).get("Page", {}).get("media", [])
                break
            except urllib.error.HTTPError as e:        # AniList drosselt -> kurz warten, 1x neu
                if e.code == 429 and attempt == 0:
                    time.sleep(min(int(e.headers.get("Retry-After", "3")), 4) + 1)   # max ~5s, kein Minuten-Hang
                    continue
                raise
        if not data:
            return out
        nn = norm(name)

        def titles_of(m):
            t = m.get("title") or {}
            return [x for x in [t.get("english"), t.get("romaji"), t.get("native")]
                    + (m.get("synonyms") or []) if x]
        best = max(data, key=lambda m: max(
            (difflib.SequenceMatcher(None, nn, norm(x)).ratio() for x in titles_of(m)), default=0))
        t = best.get("title") or {}
        out["al_id"] = best.get("id")
        out["title"] = t.get("english") or ""
        out["title_romaji"] = t.get("romaji") or ""
        syns = [s for s in (best.get("synonyms") or []) if re.search(r'[A-Za-z]', s)]
        out["title_alt"] = pick_english(syns)        # englischstes Synonym (oft der EN-Fan-Titel)
        out["country"], out["flag"] = AL_COUNTRY.get(best.get("countryOfOrigin", ""), ("", ""))
        out["pub_status"] = AL_STATUS.get(best.get("status", ""), "")
        out["is_adult"] = bool(best.get("isAdult"))
        gset = {(gg or "").lower() for gg in (best.get("genres") or [])}
        out["sexual_genre"] = bool(gset & {"ecchi", "hentai"})
        ch = best.get("chapters")
        if ch:
            try: out["latest"] = float(ch)
            except (ValueError, TypeError): pass
        sc = best.get("averageScore")
        if sc:
            out["rating"] = round(sc / 10.0, 1)      # 0-100 -> 0-10
        out["votes"] = best.get("popularity") or 0
        anames = []
        for ed in ((best.get("staff") or {}).get("edges") or []):
            role = (ed.get("role") or "").lower()
            nm = (((ed.get("node") or {}).get("name") or {}).get("full"))
            if nm and ("story" in role or "art" in role) and nm not in anames:
                anames.append(nm)
        out["author"] = ", ".join(anames[:2])
    except Exception:
        pass
    return out


# ---------------- MangaUpdates: native Bayes-Bewertung + sehr vollstaendiger Katalog ----------------
API_MU = "https://api.mangaupdates.com/v1/series/search"
MU_FLAG = {"manga": ("Japan", "🇯🇵"), "manhwa": ("Korea", "🇰🇷"), "manhua": ("China", "🇨🇳")}


def mu_rating(name):
    """MangaUpdates – bayesian_rating (schon stimmen-gewichtet) + Typ->Flagge. Beste Abdeckung."""
    out = {"rating": None, "votes": 0, "flag": "", "country": "", "author": "", "novel": False,
           "pub_status": "", "mu_id": None, "sexual_genre": False}
    try:
        MU_PACER.wait()
        results = post_json(API_MU, {"search": name, "perpage": 5}).get("results", [])
        if not results:
            return out
        nn = norm(name)

        def title_of(x):
            return re.sub(r'<[^>]+>', '', x.get("record", {}).get("title", "") or "")
        best = max(results, key=lambda x: difflib.SequenceMatcher(None, nn, norm(title_of(x))).ratio())
        rc = best.get("record", {})
        br = rc.get("bayesian_rating")
        if br:
            try: out["rating"] = round(float(br), 1)
            except (ValueError, TypeError): pass
        out["votes"] = rc.get("rating_votes") or 0
        out["mu_id"] = rc.get("series_id")            # fuer den Autor-Detailabruf (Suche liefert keine Autoren)
        out["country"], out["flag"] = MU_FLAG.get((rc.get("type") or "").lower(), ("", ""))
        mg = {(g.get("genre") or "").lower() for g in (rc.get("genres") or [])}
        out["sexual_genre"] = bool(mg & {"adult", "hentai", "ecchi", "smut"})   # Sex-Genre als Quervalidierung
        auths = [au.get("name", "") for au in (rc.get("authors") or [])]
        out["author"] = ", ".join([x for x in dict.fromkeys(auths) if x][:2])
        out["novel"] = (rc.get("type") or "").strip().lower() in ("novel", "light novel")
        if rc.get("completed") is True:
            out["pub_status"] = "Abgeschlossen"
        elif rc.get("completed") is False:
            out["pub_status"] = "Laufend"
    except Exception:
        pass
    return out


def mu_foreign_titles(name, fetch_search=None, fetch_series=None):
    """MangaUpdates-DRITTMEINUNG fuer fremdsprachige Archiv-Titel (JB 14.07.2026, 'Die Braut
    des Magiers' fand The Ancient Magus' Bride nur mit conf 0.46): MU fuehrt lizenzierte
    LANDES-Titel (de/fr/pl/tr/vi/fi ...) als associated names — MangaBaka exponiert sie nicht.

    Liefert bis zu 3 Zusatz-Queries (MU-Haupttitel + lateinische associated names) des besten
    Such-Treffers, aber NUR wenn `name` EXAKT (norm-gleich) unter dessen associated names
    steht — sonst []. Streng ohne Fuzzy: ein Fehlmatch waere schlimmer als ein Miss.
    Netz injizierbar (Tests); ~2 Requests, nur im Rettungsfall (conf < 0.62) aufgerufen."""
    nn = norm(name or "")
    if not nn:
        return []
    try:
        if fetch_search is None:
            MU_PACER.wait()
        d = (fetch_search or (lambda q: post_json(API_MU, {"search": q, "perpage": 3})))(name)
        get_series = fetch_series or (lambda sid: get_json(
            f"https://api.mangaupdates.com/v1/series/{sid}",
            headers={**UA, "Accept": "application/json"}))
        for x in ((d or {}).get("results") or [])[:2]:
            rc = (x or {}).get("record") or {}
            sid = rc.get("series_id")
            if not sid:
                continue
            rec = get_series(sid) or {}
            assoc = [(a.get("title") or "") for a in (rec.get("associated") or [])]
            if not any(norm(a) == nn for a in assoc):
                continue                       # Suchname NICHT belegt -> kein Urteil
            import re as _re
            cands = [rec.get("title") or _re.sub(r"<[^>]+>", "", rc.get("title") or "")]
            cands += [a for a in assoc if a and a.isascii()]
            out, seen = [], {nn}
            for c in cands:
                k = norm(c)
                if c and k and k not in seen:
                    seen.add(k)
                    out.append(c)
            return out[:3]
        return []
    except Exception:
        return []


def mu_authors(series_id):
    """MangaUpdates-Detail: Autoren. Im Such-Ergebnis fehlt das authors-Feld - nur im Series-GET vorhanden."""
    if not series_id:
        return ""
    try:
        rec = get_json(f"https://api.mangaupdates.com/v1/series/{series_id}",
                       headers={**UA, "Accept": "application/json"})
        all_a = rec.get("authors") or []
        auths = [a.get("name", "") for a in all_a if (a.get("type") or "").lower() != "artist"] \
            or [a.get("name", "") for a in all_a]
        return ", ".join([x for x in dict.fromkeys(auths) if x][:2])
    except Exception:
        return ""


# ---------------- Kitsu ----------------
API_KITSU = "https://kitsu.io/api/edge/manga"
KITSU_STATUS = {"current": "Laufend", "finished": "Abgeschlossen", "upcoming": "Angekündigt"}


def kitsu_rating(name):
    """Kitsu averageRating (0-100 -> 0-10). Nur bei brauchbarem Titel-Treffer."""
    try:
        KITSU_PACER.wait()
        q = urllib.parse.urlencode({"filter[text]": name, "page[limit]": 3,
                                    "fields[manga]": "canonicalTitle,titles,averageRating,userCount,status"})
        data = get_json(f"{API_KITSU}?{q}", headers={**UA, "Accept": "application/vnd.api+json"}).get("data", [])
        if not data:
            return None
        nn = norm(name)

        def titles_of(m):
            at = m.get("attributes", {})
            return [t for t in [at.get("canonicalTitle", "")]
                    + [v for v in (at.get("titles") or {}).values() if v] if t]
        def ratio(m):
            return max((difflib.SequenceMatcher(None, nn, norm(t)).ratio() for t in titles_of(m)), default=0)
        best = max(data, key=ratio)
        at = best.get("attributes", {})
        if ratio(best) < 0.6:               # zu unsicherer Treffer -> ignorieren
            return None
        titles = [at.get("canonicalTitle", "")] + [v for v in (at.get("titles") or {}).values() if v]
        title = pick_english([t for t in titles if t and re.search(r'[A-Za-z]', t)])
        ar = at.get("averageRating")
        rating = round(float(ar) / 10.0, 1) if ar else None
        return {"rating": rating, "votes": int(at.get("userCount") or 0), "title": title,
                "pub_status": KITSU_STATUS.get(at.get("status") or "", "")}
    except Exception:
        pass
    return None


# ---------------- MyAnimeList via Jikan ----------------
API_JK = "https://api.jikan.moe/v4/manga"


def jikan_lookup(name):
    """MyAnimeList (via Jikan) – reputable Zusatzquelle: englischer Titel + MAL-Score. Rate-limitiert."""
    out = {"title": "", "rating": None, "votes": 0}
    try:
        JK_PACER.wait()
        q = urllib.parse.urlencode({"q": name, "limit": 3})
        data = get_json(f"{API_JK}?{q}").get("data", [])
        if not data:
            return out
        nn = norm(name)

        def titles_of(m):
            ts = [m.get("title_english"), m.get("title")] + [t.get("title") for t in (m.get("titles") or [])]
            return [t for t in ts if t]
        best = max(data, key=lambda m: max(
            (difflib.SequenceMatcher(None, nn, norm(t)).ratio() for t in titles_of(m)), default=0))
        out["title"] = best.get("title_english") or ""
        sc = best.get("score")
        if sc:
            out["rating"] = round(float(sc), 1)       # MAL-Score ist schon 0-10
            out["votes"] = best.get("scored_by") or 0
    except Exception:
        pass
    return out


# ---------------- Link-Erreichbarkeit ----------------
def md_cover(md_id, timeout=10):
    """Cover-URL von MangaDex (256er-Thumb) -> str | ''. Teil der Cover-Fallback-Kette (JB:
    'wenn eine Quelle kein Bild hat, die naechste'): MangaBaka -> MangaDex -> AniList."""
    try:
        MD_PACER.wait()
        d = get_json(f"{API_MD}/manga/{md_id}?includes[]=cover_art", timeout=timeout)
        for rel in ((d.get("data") or {}).get("relationships") or []):
            if rel.get("type") == "cover_art":
                fn = (rel.get("attributes") or {}).get("fileName")
                if fn:
                    return f"https://uploads.mangadex.org/covers/{md_id}/{fn}.256.jpg"
    except Exception:
        pass
    return ""


def al_cover(al_id, timeout=10):
    """Cover-URL von AniList -> str | ''. Letzte Stufe der Cover-Fallback-Kette."""
    try:
        AL_PACER.wait()
        d = post_json("https://graphql.anilist.co",
                      {"query": "query($id:Int){Media(id:$id,type:MANGA){coverImage{large}}}",
                       "variables": {"id": int(al_id)}}, timeout=timeout)
        return (((d.get("data") or {}).get("Media") or {}).get("coverImage") or {}).get("large") or ""
    except Exception:
        return ""


_WT_TITLE_NO = re.compile(r"[?&]title_no=(\d+)")
_WT_BASE = re.compile(r"(https?://www\.webtoons\.com/[^/]+/[^/]+/[^/]+)/")
_WT_AUTHOR = re.compile(r'property="com-linewebtoon:webtoon:author"\s+content="([^"]+)"')


def webtoon_author(url, timeout=8):
    """Autor(en) einer webtoons.com-Serie von der Serienseite lesen (og-Meta) -> str | ''.

    Webtoon-ORIGINALE (Room of Swords, Let's Play, Age Matters ...) fehlen in den Manga-DBs oft
    komplett — die verlaesslichste Autorenquelle ist die Plattform selbst (JB-Wunsch). Aus einer
    Episoden-URL wird die Serienseite abgeleitet (…/list?title_no=N). Best-effort, nie Exception."""
    try:
        m_no, m_base = _WT_TITLE_NO.search(url or ""), _WT_BASE.search(url or "")
        if not (m_no and m_base):
            return ""
        page = f"{m_base.group(1)}/list?title_no={m_no.group(1)}"
        req = urllib.request.Request(page, headers={**UA, "Accept-Language": "en"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read(60000).decode("utf-8", "replace")
        m = _WT_AUTHOR.search(body)
        return (m.group(1).strip() if m else "")[:80]
    except Exception:
        return ""


def link_ok(url):
    if not url:
        return None
    for method in ("HEAD", "GET"):
        try:
            req = urllib.request.Request(url, method=method, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=8) as r:
                return getattr(r, "status", 200) < 400
        except urllib.error.HTTPError as e:
            return e.code in (403, 405, 429)
        except Exception:
            continue
    return False
