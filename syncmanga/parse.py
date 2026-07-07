# -*- coding: utf-8 -*-
"""
Reine Parser-/Normalisierungs-Funktionen des Manga-Kerns.

Verbatim aus SyncEngine/manga_update.py herausgelöst (Phase 2) — KEINE Verhaltensänderung.
Diese Funktionen sind seiteneffektfrei (kein Netz, kein Dateizugriff) und vollständig getestet
(siehe SyncEngine/docs/tests/test_manga_parsing.py bzw. die mitgewanderten Tests).

Enthält:
  host, slug_from_url, clean_title, chapter_of, series_from, norm, is_junk,
  romaji_score, pick_english  + die zugehörigen Regex-Konstanten
  (SITE_SUFFIX, CH, URLCH, GARB, ROM_PART, ROM_WORD).
"""
import html
import re

# Seiten-/Reader-Suffixe, die clean_title vom echten Titel abschneidet.
SITE_SUFFIX = (r'mangadex|mgeko|mangasupa|jaimini.?s? ?box|line ?webtoon|webtoon|mangasushi|fascans|night ?scans|'
    r'asura.*|flame.*|comix.*|mangasee|kissmanga|manga ?kakalot|bato.*|mangareader|manga ?plus|'
    r'read.*online.*|thunder ?scans.*|qi ?manhwa.*|leviatan.*|kireicake.*|reaper.*|all chapters|'
    r'valhalla.*|rizz.*|killberos|kingofshojo|king ?of ?shojo|mangatoda.*|mangabuddy|mangan[ae]lo|manganato|manga ?clash|manga ?freak|manga ?here|manga ?panda|manga ?owl|manhuaplus|'
    r'nani\W*scans|inept\W*bastards|kissxdeath|reset ?scans|read first at.*|free manga|novel|manhwa|manhua|manga')
CH = re.compile(r'\b(?:Chapter|Episode|Chap\.?|Ch\.?|Ep\.?)\s*([0-9]+(?:\.[0-9]+)?)', re.I)
URLCH = re.compile(r'(?:chapter|episode|chap)[-_/]?(\d+(?:\.\d+)?)', re.I)
# Webtoons traegt die GLOBALE Episodennummer im Query (episode_no=608) — Pfad ('s3-ep-145')
# und Seitentitel ('(S3) Ep. 145') zaehlen je SEASON neu, und der Pfad hinkt teils sogar um
# eins hinterher (JB-Beleg Runde 32: Orion 'chapter-21' im Pfad, episode_no=22). Der
# Query-Wert hat deshalb VORRANG vor Titel/Pfad. Bewusst NUR 'episode_no' (eindeutig
# webtoons-artig); generische Parameter wie 'no=' waeren Falschtreffer-Risiko.
EPQ = re.compile(r'[?&]episode_no=(\d+(?:\.\d+)?)', re.I)
GARB = re.compile(r'^https?://|backend|moment|cloudflare|^\(s\d+\)$|^\d+$|just a moment|^manga$|'
    r'error|^asura.?scans$|^allcuffs$|^kiss ?x ?death$|notification|bookmark|^settings|^profile|sign ?in|log ?in|^klb\b|'
    r'mangasupa|kingofshojo|howlongtobeat|rizz ?fables|valhalla|^wsr$|^notifications?$|'
    r'\.(?:pdf|jsonl?|txt|html?|epub|cbz|cbr|zip)$|'                       # Datei-Lesezeichen (CHAPTER1.pdf)
    r'^(?:lewdmanhwa|mangadotnet|mangadot|manhuatop|mangakakalot|weebcentral|roliascan|mgread|'  # ent-punktierte
    r'comix|mangafire|mangaread|mangatown|mangabuddy|natomanga|mgeko|toonily|bato)$|'            # Seitennamen
    r'^[a-z0-9][a-z0-9-]*\.(?:com|net|cc|org|io|to|xyz|me)$', re.I)


def host(u):
    m = re.search(r'https?://([^/]+)', u or "")
    return m.group(1).replace('www.', '') if m else ""


# Webtoon-/dynamische Reader: episodenbasiert/Infinite-Scroll -> Kapitel aus der URL ist unzuverlaessig.
# Fortschritt wird hier aus den Browser-DBs (Besuche) genommen; die Liste zeigt einen Info-Badge.
# (Konservativ gehalten, um Fehlalarme zu vermeiden; echte Automation ist eine spaetere Ausbaustufe.)
DYNAMIC_SITES = re.compile(r'webtoons?\.com|tapas\.io|tappytoon|lezhin|webcomicsapp|'
                           r'comic\.naver|webtoon\.kakao|bilibilicomics|inkr\.', re.I)


def is_dynamic(site):
    """True bei Webtoon-/dynamischen Seiten, wo das Kapitel aus der URL ungenau ist."""
    return bool(site and DYNAMIC_SITES.search(site))


def slug_from_url(u):
    cands = []
    m = re.search(r'webtoons\.com/[a-z]{2}/[^/]+/([a-z0-9\-]+)/(?:list|viewer|episode|ep|canvas)', u or '', re.I)
    if m:
        cands.append(m.group(1))
    for m in re.finditer(r'/(?:series|title|manga|comic|comics|read|reader|book)/([^/?#]+)', u or '', re.I):
        cands.append(m.group(1))
    # Host-spezifische Slug-Kosmetik (JB Runde 33: Pruef-Klicks erzeugten Fragment-Serien wie
    # 'Search And Destroyy' und 'Mnwgy Inspectre' — die matchen keine Datenbank -> keine Wertung):
    #   mangafire verdoppelt den LETZTEN Buchstaben des Slugs (search-and-destroyy.803lv),
    #   comix stellt eine ID ohne Ziffern-Garantie voran (mnwgy-inspectre).
    _mf = 'mangafire.to/' in (u or '')
    _cx = 'comix.to/title/' in (u or '')
    best = None
    for s in cands:
        s = s.lower()
        s = re.sub(r'\.[a-z0-9]{3,8}$', '', s)
        if _cx:
            s = re.sub(r'^[a-z0-9]{4,6}-(?=[a-z0-9])', '', s, count=1)
        if _mf and len(s) >= 5 and s[-1] == s[-2]:
            s = s[:-1]
        s = re.sub(r'[-_/]?(chapter|chap|episode|ep|ch)[-_]?\d.*$', '', s)
        s = re.sub(r'^\d+-(en|de|raw)-', '', s)
        s = re.sub(r'^\d+-', '', s)
        if re.match(r'^[a-z]*\d[a-z0-9]*-(?=[a-z])', s):
            s = re.sub(r'^[a-z0-9]+-', '', s)
        s = re.sub(r'-[0-9a-f]{6,12}$', '', s)
        s = re.sub(r'-(en|de|raw)$', '', s).strip('-_')
        s = re.sub(r'^(?:anime|ylgn)-(?=[a-z])', '', s)   # Reader-/Scanlation-Slug-Praefix ("anime-...", "ylgn-...") weg
        if len(s) >= 4 and not s.isdigit():
            if best is None or len(s) > len(best):
                best = s
    return re.sub(r'\s+', ' ', best.replace('-', ' ').replace('_', ' ')).strip().title() if best else None


def clean_title(t):
    t = html.unescape(t or '').strip()        # HTML-Entities dekodieren (&#039; -> ', &amp; -> &)
    orig = t                                  # Original fuer den End-Range-Guard (s.u.)
    t = re.sub(r'^\s*anime\s+', '', t, flags=re.I)   # Lesezeichen-Ordner-Praefix "Anime ..." weg
    t = re.sub(r'^\s*(?:ylgn|oneshot)\s*[-–—:]?\s+', '', t, flags=re.I)   # weitere Ordner-/Scan-Praefixe
    t = re.sub(r'\s+vol(?:ume)?\.?\s*\d+\s*$', '', t, flags=re.I)   # "... Vol 22"-Suffix weg
    t = re.sub(r'^\s*(Manga:|Read)\s*', '', t, flags=re.I)
    t = re.sub(r'\s+(?:read\s+)?manga\s+online\s+free\b.*$', '', t, flags=re.I)   # "... Manga Online Free - Manganelo"
    t = re.sub(r'^\s*Boredom Society\s*[-–—:]\s*', '', t, flags=re.I)             # Scanlation-Gruppen-Praefix
    t = re.sub(r'^\s*\[#?\d+\]\s*', '', t)
    t = re.sub(r'^\s*\d+\s*\|\s*', '', t)
    # "Ch. 28 (Isekai Meikyuu de Harem wo)" / "Episode 5 [Titel]" -> Titel aus der Klammer
    m = re.match(r'^\s*(?:Ch\.?|Chapter|Chap\.?|Ep\.?|Episode)\s*\d+(?:\.\d+)?\s*[\(\[]([^)\]]+)[\)\]]', t, re.I)
    if m:
        t = m.group(1)
    # "Season 1 Extras | Love Advice ..." -> Teil nach dem letzten |
    if '|' in t and re.search(r'season\s*\d|extras?', t.split('|')[0], re.I):
        t = t.split('|')[-1]
    if '|' in t and re.search(r'(?:Ep|Episode|Chapter|Ch)\.?\s*\d', t.split('|')[0], re.I):
        after = t.split('|')[-1].strip()          # nur nehmen, wenn es KEIN Seitenname ist
        if not re.match(r'(?:' + SITE_SUFFIX + r')\s*$', after, re.I):
            t = after
    t = re.split(r'\s*(?:::|\||—|–|•|-)\s*(?:' + SITE_SUFFIX + r')\b.*$', t, flags=re.I)[0]
    t = re.sub(r'\s*\(Title\).*$', '', t, flags=re.I)
    t = re.sub(r'\s*\(Official\)', '', t, flags=re.I)
    # Trenner vor "Chapter N" darf auch ein Komma/Semikolon sein (Aggregator-Seitentitel wie
    # "Love and Leashes,Chapter 17, Latest chapters, ... - Comicless" -> "Love and Leashes").
    m1 = re.match(r'(.+?)[\s,;]+(?:Chapter|Chap\.?|Ch\.?|Episode|Ep\.?)\s*\d', t, re.I)
    m2 = re.search(r'(?:Chapter|Episode)\s*\d+(?:\.\d+)?\s*[-:•|]\s*(.+)', t, re.I)
    s = (m1.group(1) if m1 else (m2.group(1) if m2 else t))
    s = re.sub(r'\s*[-–—:|]\s*(?:Page|Seite|Pg|Raw|Read Online)\b.*$', '', s, flags=re.I)
    s = re.sub(r'\s*\((?:[A-Z]{2,}\b[^)]*|[A-Z][a-z]+ [A-Z][a-z]+)\)\s*$', '', s)   # Autor-Tag "(KAKU Yuuji)"/"(Nariie Shinichirou)"
    s = re.sub(r'\s*[-–—]\s*(?:Volume|Vol\.?|Season|S)\s*\d+.*$', '', s, flags=re.I)
    s = re.sub(r'\s*[-–—,|:•]\s*\d+(?:\.\d+)?\s*$', '', s)
    # ab freistehender (Kapitel-)Nummer bis Ende abschneiden (faengt "… 100 The End"-Subtitles)
    s = re.sub(r'\s+\d{1,4}(?:\.\d+)?(?:[\s:.\-–—|]+.*)?$', '', s)
    s = re.sub(r'[“”„‟"〝〞「」『』《》〈〉【】«»]', '', s)   # Gänsefüßchen/CJK-Klammern raus
    s = re.sub(r'\s*<[^>]*>\s*$', '', s)                                   # Gruppen-Tag <KillBeros>
    s = re.sub(r'\s*\((?:Manga|Manhwa|Manhua|Novel|Webtoon|Comic|Official)\)\s*$', '', s, flags=re.I)
    s = re.sub(r'[\s\-–—|:,]+$', '', s)                                    # nachlaufende Satzzeichen/Dashes
    s = re.sub(r'\s+(?:Manga|Manhwa|Manhua)$', '', s, flags=re.I)          # "WSR Manga" -> "WSR"
    result = re.sub(r'\s{2,}', ' ', s).strip(' -–—|:,.•\'"')
    # Guard (JB 07.07.2026, 'Class 1-9' -> 'Class'): ein abschliessender Zahlen-RANGE (1-9, 1-99)
    # ist meist Teil des Titels, kein Kapitel. Hat die Reinigung genau diesen Range abgeschnitten
    # (Rest == Titel ohne Range), stellen wir den Originaltitel wieder her. Einzelne End-Nummern
    # ('Naruto 700' = Kapitel) bleiben unberuehrt.
    m_rng = re.match(r'^(.*\S)\s+\d+\s*[-–]\s*\d+$', orig)
    if m_rng and result.replace(' ', '').lower() == m_rng.group(1).replace(' ', '').lower():
        return re.sub(r'\s{2,}', ' ', orig).strip()
    return result


MAX_CHAPTER = 5000   # kein Manga hat >5000 Kapitel -> groessere Zahl = Parse-Fehler (URL-ID/Datum)


def chapter_of(url, title):
    for pat, txt in ((EPQ, url), (CH, title), (URLCH, url)):
        m = pat.search(txt or '')
        if m:
            n = float(m.group(1))
            if 0 < n <= MAX_CHAPTER:     # unplausible Riesenzahlen (No Guns Life 326576) verwerfen
                return n
    return None


def series_from(url, title):
    slug = slug_from_url(url)
    ttl = clean_title(title)
    name = None
    for cand in (slug, ttl):
        if cand and len(cand) >= 4 and not GARB.search(cand) and not is_junk(cand):
            name = cand
            break
    if (not name) and ttl and len(ttl) >= 3 and not is_junk(ttl) and not GARB.search(ttl):
        name = ttl                            # Fallback MUSS GARB ebenfalls beachten (sonst Junk-Titel)
    return name, chapter_of(url, title)


def norm(s):
    s = re.sub(r"['’]", '', (s or '').lower())
    s = re.sub(r'\b(?:chapter|chap|episode|ep|ch|vol|volume|season)\.?\s*\d+(?:\.\d+)?', ' ', s)
    s = re.sub(r'\b(20\d\d|the|a|an|s\d|official|manga|manhwa|manhua|webtoon)\b', '', s)
    return re.sub(r'[^a-z0-9]', '', s)


# Reine URL-/Seiten-Infrastruktur-Woerter, die als ALLEINIGER Name nie eine Serie sind (Parser-Reste aus
# URLs oder Ladezustaenden, z.B. cubari.moe/read/gist -> "gist", ein "Loading..."-Seitentitel -> "loading",
# ein Kapitel-Pfadsegment -> "chapter"/"vol"). Nur EINWORT-Namen werden so verworfen (siehe is_junk).
URL_JUNK = {"gist", "viewer", "proxy", "raw", "loading", "chapter", "chapters",
            "vol", "volume", "page", "read", "reader", "series",
            "weebcentral"}   # Reader-HOST als "Serienname" (JB-Fund: Zeile hiess 'weebcentral')

# Lese-URLs, die auf einen ROMAN (statt Comic) hinweisen -> Titel als Novel einordnen (Novels werden
# ausgeblendet; z.B. wuxiaworld.com/novel/against-the-gods). So verwechselt die Liste Manga nicht mit Romanen.
_NOVEL_URL = re.compile(
    r"(wuxiaworld|novelupdates|royalroad|webnovel|light[\-_]?novel|/novels?/|novelbin|novelfull|boxnovel|"
    r"fanmtl|wtr-lab|novelhall|novelusb|readnovel|novelcool|noveltop|scribblehub|fenrirealm)", re.I)


def is_novel_url(u):
    """True, wenn die Lese-URL auf eine Roman-/Light-Novel-Quelle deutet (nicht auf einen Comic-Reader)."""
    return bool(_NOVEL_URL.search(u or ""))


def is_junk(name):
    """True bei Hex/UUID-Müll oder generischem URL-Pfad-Wort als Name (z.B. 'gist' aus einer cubari-URL,
    '971B9B8A 90Ce 4E09 9E96', '61Aff5Bc 1732 4467 Bfce', 'Va920714')."""
    toks = re.findall(r'[A-Za-z0-9]+', name or '')
    if not toks:
        return True
    if len(toks) == 1 and toks[0].lower() in URL_JUNK:        # einzelnes URL-Pfad-Wort -> kein Serien-Name
        return True
    joined = ''.join(toks)
    hexratio = sum(c in '0123456789abcdefABCDEF' for c in joined) / len(joined)
    has_digit = any(c.isdigit() for c in joined)
    if has_digit and len(joined) >= 8 and hexratio >= 0.85:   # UUID/Hex-ID mit Ziffer
        return True
    hexblocks = sum(1 for t in toks if len(t) >= 4 and re.fullmatch(r'[0-9a-fA-F]+', t))
    return hexblocks >= 3 and hexblocks >= len(toks) - 1       # mehrere Hex-Blocks (UUID-Fragmente)


# Romaji-Erkennung (konservativ): kleingeschriebene Partikel + klar-japanische Satzwoerter.
# Dient als Komparator -> aus mehreren EN-Kandidaten den "englischsten" (wenigste Romaji) waehlen.
ROM_PART = re.compile(r' (no|wa|wo|ni|ga|de|na) ')   # case-sensitive: nur kleingeschriebene Partikel
ROM_WORD = re.compile(r'\b(yuusha|isekai|tensei|sareta|dekiru|shitte|shittemashita|desu|tte|maou|ore|'
                      r'boku|watashi|nikki|mahou|kenja|oukoku|reijou|madoshi|saikyou|tenshoku|kiseki|'
                      r'monogatari|shoukan|seikatsu|kanojo)\b', re.I)


def romaji_score(s):
    return len(ROM_PART.findall(s or '')) + len(ROM_WORD.findall(s or ''))


def pick_english(cands):
    """Aus Titel-Kandidaten (in Prioritaet) den englischsten waehlen; bei Gleichstand der erste."""
    cands = [c for c in cands if c]
    return min(cands, key=romaji_score) if cands else ""
