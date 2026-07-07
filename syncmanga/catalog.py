# -*- coding: utf-8 -*-
"""
Katalog-Schicht — primaer MangaBaka, mit Fallback-Kette auf die Unterquellen.

Liefert je Serie EINEN normalisierten Datensatz: beide Titel (EN + Original/Romaji), Typ
(manga/manhwa/manhua), DB-Einzel-Scores (nur Datenbanken, nie Reader), content_rating,
Genres/Tags, Autoren, Status, Kapitelzahl, alle Quell-IDs. Dedup ist eingebaut: MangaBaka
fuehrt Dubletten ueber `merged_with` auf den kanonischen Eintrag zusammen.

Resilienz (JBs Anforderung): faellt MangaBaka aus, fragt `lookup` direkt die Unterquellen
(AniList/MAL/Kitsu/MangaUpdates) ab und baut denselben Record-Shape, nur mit weniger Feldern.
Jeder Aufruf meldet Erfolg/Fehler an `srcstatus` -> Fallback-Kette + Dashboard-Panel + Tray.

WICHTIG fuer Tests: Netzzugriff laeuft ueber das Modul-Attribut `get_json` (mockbar).
"""
import difflib
import re
import threading
import time
import urllib.error
from urllib.parse import quote

from . import health as srcstatus     # Quellen-Status (frueher srcstatus.py, jetzt in health)
from .common import Pacer, get_json
from .parse import norm

API_MB = "https://api.mangabaka.dev/v1/series"
MB_PACER = Pacer(0.6)         # MangaBaka drosselt hart (~429 nach 5-6 schnellen Calls)
MB_MAX_RETRY = 6              # 429 -> kurz warten und erneut (Cooldown real ~2s)
SIM_WINDOW = 0.12            # Titel-Match-Fenster: nur so viel schlechter als der beste darf ein
#                             Kandidat sein, um noch per Popularitaet gewaehlt zu werden (sonst Fehlmatch)
# MangaBaka vertraegt keine Parallelitaet (Rate-Limit) -> auf EINEN gleichzeitigen Aufruf
# serialisieren. Der restliche Per-Serie-Aufwand (Fallback-Quellen, link_ok) bleibt parallel.
_MB_SEM = threading.Semaphore(1)
# MangaBaka blockt den Default-UA (403) -> Browser-UA wie in health._fetch.
MB_HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                            "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
              "Accept": "application/json"}
# Land/Sprache -> Veroeffentlichungsart (Fallback, wenn MangaBaka keinen type liefert).
_TYPE_BY_COUNTRY = {"jp": "manga", "japan": "manga", "kr": "manhwa", "korea": "manhwa",
                    "cn": "manhua", "china": "manhua", "tw": "manhua", "taiwan": "manhua",
                    # MangaDex nutzt SPRACH-Codes (originalLanguage) statt Laender-Codes:
                    "ja": "manga", "ko": "manhwa", "zh": "manhua", "zh-hk": "manhua",
                    # englische Originale (JB-Fall Soul Anomaly: MD sagt USA) -> OEL/🇺🇸
                    "en": "oel", "us": "oel", "usa": "oel", "gb": "oel"}


# ---------------- MangaBaka ----------------

def _titles(rec):
    """Alle Titelvarianten eines MangaBaka-Records (fuer den Aehnlichkeitsvergleich)."""
    out = [rec.get("title"), rec.get("native_title"), rec.get("romanized_title")]
    sec = rec.get("secondary_titles") or {}
    if isinstance(sec, dict):
        for lst in sec.values():
            for it in (lst or []):
                out.append(it.get("title") if isinstance(it, dict) else it)
    out += [t for t in (rec.get("titles") or []) if isinstance(t, str)]
    return [t for t in out if t]


# Sprach-Marker (eigenstaendige Woerter), die einen 'unknown'-Zweittitel als NICHT-englisch
# entlarven (JB Runde 37): genau die Klasse, die die Titel-Regression ausloeste — Spanisch
# ('Ataque a los titanes'), Franzoesisch ('Les conseils d'amour…'), Deutsch, Portugiesisch.
# Bewusst nur eindeutige Funktionswoerter; englische Titel nutzen keins davon als Wort.
_NON_EN_WORDS = {"los", "las", "el", "les", "le", "la", "un", "une", "der", "die", "das",
                 "und", "ein", "eine", "del", "de", "du", "des", "et", "y", "para", "por",
                 "dos", "das", "uma", "um", "il", "gli", "lo", "una", "che", "di",
                 "fille", "fils", "mon", "ma", "mes", "avec"}
_NON_EN_PREFIX = ("d'", "l'", "d’", "l’")
# Sprach-ANNOTATIONEN in Titeln (JB Runde 42, 'Stranger Case (French)'): MangaBaka haengt
# die Sprache manchmal als Klammer-Zusatz an den unknown-Titel — solche Eintraege sind NIE
# der englische Handelstitel.
# Sprachnamen offen ('(french' faengt '(French)' und '(french ver.)'), KURZ-Codes nur MIT
# schliessender Klammer — '(vi'/'(br' offen wuerde legitime Titel wie '(Violet …)' oder
# '(Brothers)' fressen (Selbst-Audit Runde 42).
_LANG_ANNOT = ("(french", "(spanish", "(german", "(italian", "(portuguese", "(polish",
               "(russian", "(thai", "(arabic", "(turkish", "(vietnamese", "(indonesian",
               "(vf)", "(fr)", "(es)", "(de)", "(it)", "(pt)", "(pt-br)", "(br)", "(pl)",
               "(ru)", "(vi)", "(id)", "(tr)")


# NUR typografische Zeichen zaehlen als ASCII (englische Titel nutzen ’ “ ” –);
# akzentuierte BUCHSTABEN (é/ñ/ü/…) bleiben absichtlich draussen — Akzente sind
# ein starkes NICHT-Englisch-Signal.
_TYPO_ASCII = str.maketrans({"’": "'", "‘": "'", "“": '"', "”": '"', "–": "-", "—": "-", "…": "."})


def _looks_english(t):
    """True, wenn ein unetikettierter Zweittitel plausibel ENGLISCH ist: reine Latein-Schrift
    (Kyrillisch/Kana/Hangul/CJK/Akzente fliegen ueber Nicht-ASCII raus) und kein romanisches/
    deutsches Funktionswort ('los'/'les'/'der' …). Konservativ: lieber einen englischen Titel
    verpassen als eine neue Fremdsprachen-Regression."""
    if not t or not all(ord(ch) < 128 for ch in t.translate(_TYPO_ASCII)):
        return False
    low = t.lower()
    if any(a in low for a in _LANG_ANNOT):
        return False
    # Bindestrich-Teile einzeln pruefen ('Zom-fille' -> 'fille' ist franzoesisch)
    words = [p for w in low.replace("-", " ").split()
             for p in [w.strip(".,!?:;()[]\"'")] if p]
    if any(w in _NON_EN_WORDS for w in words):
        return False
    return not any(w.startswith(_NON_EN_PREFIX) for w in words)


def _en_titles(rec):
    """Die ENGLISCHEN Zweittitel — fuer die Anzeigename-Wahl. Zwei Guetestufen:

    1. secondary_titles['en'] (von MangaBaka ETIKETTIERT — zuerst, hoechstes Vertrauen).
    2. secondary_titles['unknown'] nach Sprachfilter (JB Runde 37, Kagekuri/Chikotan/
       Daijukai: bei Nischenserien etikettiert MangaBaka NICHTS — 'Shadow Princess' steckt
       zwischen Koreanisch/Chinesisch/Russisch in der unknown-Liste). _looks_english wirft
       Nicht-Latein und romanische/deutsche Titel raus (die Ataque-Regression, Runde 35).
    JB Runde 35: die flache alt_titles-Liste mischt ALLE Sprachen ungefiltert — nie daraus waehlen."""
    sec = rec.get("secondary_titles") or {}
    if not isinstance(sec, dict):
        return []
    out = []
    for it in (sec.get("en") or []):
        t = it.get("title") if isinstance(it, dict) else it
        if t:
            out.append(t)
    for it in (sec.get("unknown") or []):
        t = it.get("title") if isinstance(it, dict) else it
        if t and t not in out and _looks_english(t):
            out.append(t)
    return out


def _ratings(rec):
    """DB-Einzel-Scores (0-10) aus source[*].rating_normalized (0-100) + Aggregat. NUR Datenbanken."""
    out = []
    for v in (rec.get("source") or {}).values():
        if isinstance(v, dict) and v.get("rating_normalized"):
            out.append(round(v["rating_normalized"] / 10.0, 2))
    agg = rec.get("rating")
    if agg:
        out.append(round(agg / 10.0, 2))
    return out


_SMALL = {"no", "of", "on", "the", "to", "a", "an", "and", "in", "wa", "ga", "wo", "x", "vs"}


def _pretty(t):
    """All-Caps-Titel (MangaBaka liefert oft GROSS) in lesbare Schreibweise; sonst unveraendert."""
    if not t or not t.isupper():
        return t or ""
    words = t.split()
    return " ".join(w.title() if (i == 0 or w.lower() not in _SMALL) else w.lower()
                    for i, w in enumerate(words))


def _num(x):
    """Zu float/None robust konvertieren (MangaBaka liefert Kapitelzahlen mal als String)."""
    try:
        return float(x) if x not in (None, "") else None
    except (TypeError, ValueError):
        return None


def cover_url(c):
    """MangaBaka-`cover` -> EINE Bild-URL (rein/testbar). Das Feld kommt als String ODER als
    verschachteltes dict ({'raw': {'url': ...}, 'small': ...}) — JB-Crash Runde 24:
    html.escape(dict) toetete jeden Render inkl. des v30-Laufs. Nichts Passendes -> ''."""
    if isinstance(c, str):
        return c
    if isinstance(c, dict):
        for k in ("small", "medium", "default", "raw", "large"):
            v = c.get(k)
            if isinstance(v, str) and v.startswith("http"):
                return v
            if isinstance(v, dict) and isinstance(v.get("url"), str):
                return v["url"]
        if isinstance(c.get("url"), str):
            return c["url"]
    return ""


def _source_ids(rec):
    return {k: (v.get("id") if isinstance(v, dict) else v)
            for k, v in (rec.get("source") or {}).items() if v}


def _normalize(rec):
    """MangaBaka-Record -> flacher, stabiler Katalog-Record."""
    return {
        "mb_id": rec.get("id"),
        "title_en": _pretty(rec.get("title")),
        "title_native": rec.get("native_title") or "",
        "title_romaji": rec.get("romanized_title") or "",
        "alt_titles": _titles(rec),
        "alt_en": _en_titles(rec),
        "type": (rec.get("type") or "").lower(),
        "ratings": _ratings(rec),
        "content_rating": (rec.get("content_rating") or "").lower(),
        "genres": [str(g).lower() for g in (rec.get("genres") or [])],
        "tags": [str(t).lower() for t in (rec.get("tags") or [])],
        "authors": [a for a in (rec.get("authors") or []) if a],
        "status": rec.get("status") or "",
        "total_chapters": _num(rec.get("total_chapters")),
        "source_ids": _source_ids(rec),
        "cover": cover_url(rec.get("cover")),
        "year": rec.get("year"),
    }


def _mb_fetch(path):
    """MangaBaka-GET, serialisiert (Semaphore=1) + Pacer + 429-Backoff. Wie der Einzel-Thread-Pfad."""
    with _MB_SEM:
        for attempt in range(MB_MAX_RETRY):
            MB_PACER.wait()
            try:
                return get_json(API_MB + path, headers=MB_HEADERS, timeout=12)
            except urllib.error.HTTPError as e:
                if e.code == 429 and attempt < MB_MAX_RETRY - 1:
                    time.sleep(min(int(e.headers.get("Retry-After", "2") or 2), 3) + 0.4)
                    continue
                raise
    return {}


def _mb_get(series_id):
    d = _mb_fetch(f"/{series_id}")
    return (d or {}).get("data") or {}


def _canonical(rec):
    """merged_with verfolgen -> kanonischer Eintrag (max. 3 Hops gegen Zyklen)."""
    seen = set()
    for _ in range(3):
        mw = rec.get("merged_with")
        if not mw or mw in seen:
            break
        seen.add(mw)
        nxt = _mb_get(mw)
        if not nxt:
            break
        rec = nxt
    return rec


def _pop_rank(r):
    """MangaBaka-Popularitaetsrang (kleiner = beliebter). Fehlt er -> sehr gross."""
    p = r.get("popularity")
    if isinstance(p, dict):
        g = p.get("global")
        if isinstance(g, dict) and isinstance(g.get("current"), (int, float)):
            return g["current"]
    if isinstance(p, (int, float)):
        return p
    return 10 ** 9


# Roman-Typen von MangaBaka. Dies ist eine MANGA-Leseliste (Quelle = Comic-Lese-Verlauf); Romane werden
# NICHT gerendert. Ein als Roman getypter Treffer laesst also den vom Nutzer gelesenen COMIC komplett
# aus der Liste verschwinden -> bei aehnlichem Titel den Comic vorziehen.
_NOVEL_RAW = {"novel", "light_novel", "light novel", "web_novel", "web novel"}


def _is_novel_rec(r):
    return (r.get("type") or "").strip().lower().replace("-", "_") in _NOVEL_RAW


def mb_search(name, read_chap=None, prefer_novel=False):
    """MangaBaka-Suche -> (bester Record, confidence). Kanonisiert.

    Unter den AEHNLICHSTEN Treffern den populaersten (kanonischen) waehlen: MangaBakas
    `romanized_title` ist unzuverlaessig, sodass ein gleichnamiges Spin-off/Volume die reine
    Aehnlichkeit gewinnen kann (z.B. "Attack on Titan Volume 0" statt der Hauptserie). Die
    Popularitaet trennt Hauptserie von Ableger.

    `prefer_novel` = die Lese-Quelle ist eine Roman-Seite -> unter aehnlichen Treffern den Roman waehlen.
    `read_chap` = bereits gelesene Kapitelzahl. Liest der Nutzer DEUTLICH mehr als der Comic umfasst und
    gibt es eine gleichnamige Roman-Fassung passender Laenge, wird der Roman gewaehlt (Xianxia/Wuxia teilen
    oft Titel zwischen Novel + Manhua) -> korrekte Einordnung statt Fehlzahlen.
    """
    d = _mb_fetch(f"/search?q={quote(name)}")
    items = [r for r in ((d or {}).get("data") or [])
             if (r.get("state") or "active") == "active" or r.get("merged_with")]
    if not items:
        return {}, 0.0
    nn = norm(name)

    def score(r):
        return max((difflib.SequenceMatcher(None, nn, norm(t)).ratio() for t in _titles(r)), default=0.0)

    # Auswahl-Pipeline (jede Stufe eine benannte Verteidigungslinie, einzeln getestet):
    #   strong      -> nur Kandidaten nahe am besten Titel-Match (Name schlaegt Popularitaet)
    #   pick        -> Roman-Quelle? sonst Comic vor Roman, darunter der populaerste
    #   stub_guard  -> Pilot-/Stub-Ausgabe darf die Hauptserie nicht schlagen
    #   novel_flip  -> tiefer Lese-Fortschritt verraet die Roman-Fassung
    best_sim = max(score(r) for r in items)
    strong = _strong_candidates(items, score, best_sim)
    best = _pick_by_type(strong, prefer_novel)
    best = _stub_guard(best, items, score)
    best = _deep_reader_novel_flip(best, strong, read_chap)
    return _canonical(best), best_sim


def _strong_candidates(items, score, best_sim):
    """Nur Kandidaten mit AEHNLICH hohem Titel-Match (Fenster unter best_sim). Popularitaet darf einen
    viel besseren Titel-Treffer NICHT schlagen — sonst gewinnt eine populaere, namensfremde Serie gegen
    den exakten Treffer ('Against the Gods' sim 1.0 verlor gegen 'Playing Revenge Against God' sim 0.57).
    So trennt Popularitaet nur echte Gleichstaende (Hauptserie vs. gleichnamiges Spin-off/Volume)."""
    return [r for r in items[:8] if score(r) >= best_sim - SIM_WINDOW] or items[:5]


def _pick_by_type(strong, prefer_novel):
    """Deutet die Lese-Quelle auf einen Roman (wuxiaworld/novel/...), unter aehnlichen Treffern den Roman
    waehlen. Sonst: COMIC vor Roman (Manga-Leseliste; Romane werden ausgeblendet), darunter der
    populaerste. Nur wenn alle aehnlichen Kandidaten Romane sind, gewinnt der populaerste Roman."""
    if prefer_novel:
        novels = [r for r in strong if _is_novel_rec(r)]
        if novels:
            return min(novels, key=_pop_rank)
    return min(strong, key=lambda r: (_is_novel_rec(r), _pop_rank(r)))


def _stub_guard(best, items, score):
    """Stub-Schutz (Name > Popularitaet, JB): Ist der beste Titel-Treffer eine PILOT-/Stub-Ausgabe
    (<=2 Kap. — AUCH 0/unbekannt, JB-Fund: 'Shuumatsu no Valkyrie (2023)' hatte 0 Kap. und schlug
    'Record of Ragnarok') und gibt es eine VIEL populaerere Ausgabe (>=10x) mit noch gutem Titel-Match
    (>=0.55), ist das die Hauptserie -> diese nehmen. Sonst schlaegt die exakt gleichnamige Pilot-Stub
    die Hauptserie, deren Romaji leicht abweicht ('Dungeon Meshi'-Pilot vs 'Delicious in Dungeon')."""
    bt = _num(best.get("total_chapters")) or 0
    if bt > 2:
        return best
    bp = _pop_rank(best)
    main = [r for r in items[:8] if r is not best and score(r) >= 0.55
            and (_num(r.get("total_chapters")) or 0) > 2 and _pop_rank(r) * 10 <= bp]
    return min(main, key=_pop_rank) if main else best


def _deep_reader_novel_flip(best, strong, read_chap):
    """Fortschritts-Erkennung: Hat der Nutzer WEIT mehr Kapitel gelesen als der gewaehlte Comic umfasst
    und existiert eine gleichnamige Roman-Fassung, die diese Zahl abdeckt, liest er den Roman -> diesen
    waehlen ('Against the Gods' 1719 gelesen = Roman 2175, nicht Manhua 784). Konservativ (x1.5), damit
    reine Scanlation-Zaehlweise (~2x) ohne passenden Roman NICHT umkippt."""
    rc = _num(read_chap) or 0
    if not rc or _is_novel_rec(best):
        return best
    ctot = _num(best.get("total_chapters")) or 0
    if not ctot or rc <= ctot * 1.5:
        return best
    novels = [r for r in strong if _is_novel_rec(r) and (_num(r.get("total_chapters")) or 0) >= rc * 0.95]
    return min(novels, key=_pop_rank) if novels else best


# ---------------- Fallback (Unterquellen direkt) ----------------

def _fallback(name):
    """MangaBaka weg -> Record aus den Unterquellen bauen (Resilienz, weniger Felder)."""
    from . import sources as S
    t0 = time.time()
    try:
        a = S.al_lookup(name) or {}
        j = S.jikan_lookup(name) or {}
        k = S.kitsu_rating(name) or {}
        m = S.mu_rating(name) or {}
        d = S.md_lookup(name) or {}
    except Exception as ex:
        srcstatus.record("fallback", False, ex)
        return {}
    # MangaDex (riesiger Katalog, matcht Serien, die AL/MAL/Kitsu nicht kennen) NUR akzeptieren, wenn der
    # Titel wirklich passt -> kein Fehlmatch bei obskuren Serien (JB-Regel: kein falscher Manga). md_lookup
    # gibt sonst immer den "aehnlichsten" Treffer zurueck. Liefert dann Titel/Status/Autor/latest/mangadex-id.
    if not (d.get("md_id") and difflib.SequenceMatcher(None, norm(name), norm(d.get("title") or "")).ratio() >= 0.8):
        d = {}
    title = a.get("title") or j.get("title") or k.get("title") or d.get("title") or ""
    if not title:
        srcstatus.record("fallback", False, "kein Treffer")
        return {}
    author = a.get("author") or d.get("author") or ""
    if not author and m.get("mu_id"):
        try:
            author = S.mu_authors(m["mu_id"]) or ""
        except Exception:
            author = ""
    ratings = [x for x in (a.get("rating"), j.get("rating"), k.get("rating"), m.get("rating")) if x]
    country = (a.get("country") or d.get("country") or "").lower()
    rec = {
        "mb_id": f"al:{a.get('al_id')}" if a.get("al_id") else (d.get("md_id") or None),
        "title_en": title,
        "title_native": "",
        "title_romaji": a.get("title_romaji") or "",
        "alt_titles": [x for x in (title, a.get("title_romaji"), a.get("title_alt")) if x],
        "type": _TYPE_BY_COUNTRY.get(country, ""),
        "ratings": [round(float(x), 2) for x in ratings],
        "content_rating": "erotica" if (a.get("is_adult") or d.get("content_rating") in ("erotica", "pornographic")) else "",
        "genres": [],
        "tags": [],
        "authors": [author] if author else [],
        "status": a.get("pub_status") or k.get("pub_status") or d.get("pub_status") or "",
        "total_chapters": d.get("latest"),          # MangaDex lastChapter (bei Ongoing None -> enrich fuellt via md_latest)
        "source_ids": {kk: vv for kk, vv in (("anilist", a.get("al_id")),
                                             ("manga_updates", m.get("mu_id")),
                                             ("mangadex", d.get("md_id"))) if vv},
        "cover": "", "year": None,
    }
    srcstatus.record("fallback", True, latency=time.time() - t0)
    return rec


# ---------------- oeffentliche API ----------------

_PART_RE = re.compile(r"^(.*?)\s+(?:part|season|arc)\s*\d+\s*[:\-–]?\s*(.*)$", re.I)


def part_queries(name):
    """Teil-Titel zerlegen -> Zusatz-Suchbegriffe (rein/testbar). Benchmark-Fund: ALLE Misses
    waren 'Part N'-Titel ('JoJo's Bizarre Adventure Part 5: Golden Wind' — MangaBaka listet die
    Teile als 'Golden Wind' bzw. unter dem Stammtitel). -> [Untertitel, Stammtitel] oder []."""
    m = _PART_RE.match(name or "")
    if not m:
        return []
    return [q.strip(" :-–") for q in (m.group(2), m.group(1)) if q and len(q.strip(" :-–")) >= 3]


def lookup(name, slugs=None, read_chap=None, prefer_novel=False):
    """Katalog-Lookup mit Fallback-Kette -> (rec_norm, confidence, used_source).

    Probiert MangaBaka mit dem Namen und (bei schwachem Treffer) den URL-Slugs der Reader;
    faellt MangaBaka aus oder findet nichts, greift der Unterquellen-Fallback (Resilienz).
    `read_chap`/`prefer_novel` = Lese-Fortschritt + Roman-Quelle (fuer die Roman-vs-Comic-Wahl in mb_search).
    """
    queries = [name] + [s for s in (slugs or []) if s and norm(s) != norm(name)]
    mb_erred = False
    # MangaBaka pro Serie neu versuchen (KEIN sticky-down): ein 429-Burst darf den Katalog nicht
    # dauerhaft abschalten. Schlaegt der Call (nach Backoff) fehl, faellt NUR diese Serie zurueck.
    try:
        t0 = time.time()
        best, conf = {}, 0.0
        for q in queries:
            r, c = mb_search(q, read_chap=read_chap, prefer_novel=prefer_novel)
            if r and c > conf:
                best, conf = r, c
            if conf >= 0.92:        # klarer Treffer -> Slug-Varianten sparen
                break
        # AniList-Zweitmeinung bei UNSICHEREM Treffer: MangaBakas Suche kennt oft nur EN-Titel + Kurz-
        # Alias ('TenKen'), nicht den vollen Romaji -> ein Spin-off mit dem vollen Namen im Titel gewinnt
        # faelschlich ('Tensei Shitara Ken deshita - Rev' 7 Kap. statt 'Reincarnated as a Sword' 97 Kap.).
        # AniList kennt BEIDE Formen: dessen EN-Titel als Zusatz-Query rettet den Match. Konservativ:
        # nur bei conf<0.8, und der neue Treffer muss nahezu exakt sitzen (>=0.9).
        if conf < 0.8:
            try:
                from . import sources as S
                a = S.al_lookup(name) or {}
                alt = a.get("title") or a.get("title_romaji")
                if alt and norm(alt) != norm(name):
                    r2, c2 = mb_search(alt, read_chap=read_chap, prefer_novel=prefer_novel)
                    if r2 and c2 >= max(conf + 0.1, 0.9):
                        best, conf = r2, c2
            except Exception:
                pass
        # Teil-Titel-Rettung ('Part N'/'Season N'): Untertitel + Stammtitel als Zusatz-Queries.
        # Der Treffer muss nahezu exakt sitzen (>=0.9); die conf wird trotzdem auf 0.75 GEKAPPT:
        # MangaBaka kanonisiert Franchises oft auf EINEN Eintrag (JoJo -> 'Part 1') — der Match
        # ist also Franchise-genau, nicht Part-genau. 0.75 = kein ❓ (>=0.62), aber unter den
        # 0.8-Vertrauens-Schwellen (Deckelung/Zweitmeinung bleiben vorsichtig).
        if conf < 0.8:
            for q2 in part_queries(name):
                r2, c2 = mb_search(q2, read_chap=read_chap, prefer_novel=prefer_novel)
                if r2 and c2 >= max(conf + 0.1, 0.9):
                    best, conf = r2, min(c2, 0.75)
                    break
        srcstatus.record("mangabaka", True, latency=time.time() - t0)
        if best:
            return _normalize(best), conf, "mangabaka"
    except Exception as ex:
        mb_erred = True
        srcstatus.record("mangabaka", False, ex)
    rec = _fallback(name)
    if rec:
        return rec, 0.5, "fallback"
    # "error" (MangaBaka geworfen -> 429/Netz, Fallback leer) vs. "none" (MangaBaka hat geantwortet,
    # aber nichts gefunden): R6 (JB 07.07.2026) zaehlt NUR "none" auf das Retry-Limit; ein transientes
    # "error" wird endlos erneut probiert, statt nach RETRY_MAX Aussetzern dauerhaft "unbekannt".
    return {}, 0.0, ("error" if mb_erred else "none")


def lookup_id(mb_id):
    """Ground-Truth-Pin: Record DIREKT per MangaBaka-ID holen (Override `mb_id`), ohne Suche/Rateuerei.
    Fuer Faelle, in denen die Suche unweigerlich falsch matcht (gleichnamige Stub schlaegt Hauptserie,
    Alias-Verschmutzung). -> (rec_norm, 1.0, "mangabaka-pin"). Fehlschlag -> ({}, 0.0, "error"/"none")."""
    erred = False
    try:
        t0 = time.time()
        rec = _canonical(_mb_get(mb_id))
        srcstatus.record("mangabaka", True, latency=time.time() - t0)
        if rec:
            return _normalize(rec), 1.0, "mangabaka-pin"
    except Exception as ex:
        erred = True
        srcstatus.record("mangabaka", False, ex)
    # 429/Netz beim Pin -> "error" (R6: wird erneut probiert); leere ID-Antwort -> "none".
    return {}, 0.0, ("error" if erred else "none")
