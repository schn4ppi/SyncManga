# -*- coding: utf-8 -*-
"""
Reader-Kapitel-Link konstruieren + VERIFIZIEREN (JBs Idee statt MangaDex).

Viele freie Reader nutzen deterministische, ratbare Kapitel-URLs und liefern ein ECHTES 404,
wenn es das Kapitel/die Serie nicht gibt (z.B. mangabolt.com/chapter/<slug>-chapter-<n>/).
Damit laesst sich ein exakter Kapitel-Link bauen und per HTTP bestaetigen — ohne MangaDex
(Gast-Leselimits, fehlende EN-Uebersetzung, Verlags-Paywalls, Fehlmatches).

Vorgehen je Serie: aus EN-/Romaji-/Alt-Titeln Slug-Kandidaten erzeugen, fuer jeden Pattern-Reader
die Kapitel-URL bauen und verifizieren (200, kein Redirect weg); der erste Treffer gewinnt.
Mehrere Kandidaten werden parallel/gepaced geprueft ("ein Programm ist schneller als die Finger").

Netzzugriff injizierbar (Tests). Konservativ gepaced gegen Sperren.
"""
import difflib
import glob
import gzip
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from urllib.parse import urlparse

from .common import Pacer
from .config import is_dead_reader
from .parse import norm, host, clean_title, CH

READER_PACER = Pacer(0.25)
# Hoefliche Zusatz-Bremse je HOST: mangafire blockt Bots nach zu vielen schnellen Anfragen (403-
# Salven mitten im Lauf -> zufaellig verlorene Treffer). Ein eigener 1.2s-Takt senkt die Blockrate.
_HOST_PACERS = {"mangafire.to": Pacer(1.2)}
_UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                     "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"}

# Eingebaute Standard-Reader (Fallback). Die EDITIERBARE Quelle der Wahrheit ist
# data/readers_pattern.json (load_readers); das Discovery-Tool pflegt sie automatisch.
# Felder: name, host, type (manga/manhwa/any), chapter (URL-Vorlage mit {slug}/{n}).
# NUR Reader mit ECHTEM 404 (per Garbage-Kapitel-Check verifiziert). Soft-404-Seiten (mangahub,
# mangaread, mangak, readmanga, linkmanga, flamescans, cocomic, mangazin) liefern 200 fuer ALLES
# und erzeugen Falschlinks -> bewusst NICHT drin. Mehr findet tools/discover_readers.py (off-peak).
DEFAULT_READERS = (
    {"name": "MangaBolt", "host": "mangabolt.com", "type": "manga",
     "chapter": "https://mangabolt.com/chapter/{slug}-chapter-{n}/"},
    {"name": "MangAck", "host": "mangack.com", "type": "manhwa",
     "chapter": "https://mangack.com/chapter/{slug}-chapter-{n}/"},
    {"name": "KingOfShojo", "host": "kingofshojo.com", "type": "manhwa",
     "chapter": "https://kingofshojo.com/{slug}-chapter-{n}/"},
)
# Aktive Reader-Liste (Modul-global, ueberschreibbar via load_readers). Start = Defaults.
PATTERN_READERS = list(DEFAULT_READERS)
# Kandidaten-Muster fuer die Discovery (welche URL-Strukturen ein Reader haben koennte).
CANDIDATE_PATTERNS = (
    "https://{h}/chapter/{slug}-chapter-{n}/",
    "https://{h}/manga/{slug}/chapter-{n}/",
    "https://{h}/read/{slug}/chapter-{n}/",
    "https://{h}/{slug}-chapter-{n}/",
    "https://{h}/comic/{slug}/chapter-{n}/",
    "https://{h}/series/{slug}/chapter-{n}/",
    "https://{h}/webtoon/{slug}/chapter-{n}/",
)
MAX_SLUGS = 6            # Slug-Kandidaten je Serie deckeln (Hoeflichkeit/Tempo)
SEARCH_SLUGS = 3         # bei der Mehr-Reader-Suche (Ruecklagen) weniger Slugs je Reader (Tempo)


def _valid_reader(r):
    return (isinstance(r, dict) and r.get("name") and r.get("host") and r.get("chapter")
            and "{slug}" in r["chapter"] and "{n}" in r["chapter"])


def load_readers(path):
    """Reader-Liste aus data/readers_pattern.json laden -> setzt PATTERN_READERS (Modul-global).

    Fehlt/kaputt/leer -> die eingebauten DEFAULT_READERS bleiben (kein Datenverlust). Idiotensicher:
    nur Eintraege mit name/host/chapter ({slug}+{n}) werden uebernommen. Gibt die aktive Liste zurueck.
    """
    global PATTERN_READERS
    readers = None
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        readers = [r for r in (data.get("readers") or []) if _valid_reader(r)]
    except (OSError, ValueError, AttributeError):
        readers = None
    PATTERN_READERS = readers if readers else list(DEFAULT_READERS)   # fehlt/leer -> Defaults
    return PATTERN_READERS


def slugify(title):
    """Titel -> URL-Slug (klein, nur a-z0-9, Bindestriche). Leer, wenn nichts Lateinisches uebrig.

    Apostrophe werden ENTFERNT (nicht zu Bindestrich): "Tyrant's" -> tyrants, "Demon's" -> demons
    (so machen es die Reader-Seiten) -> trifft Possessiv-Titel."""
    t = re.sub(r"['’ʼ`]", "", (title or "").lower())   # ' ’ ʼ ` raus
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def slug_candidates(titles):
    """Aus mehreren Titeln (EN/Romaji/Alt) Slug-Kandidaten.

    Varianten je Titel: der Slug selbst, ohne fuehrendes 'the-', und mit verdoppeltem Endvokal
    (japanische Langvokal-Romanisierung, z.B. 'haikyu' -> 'haikyuu'). Reihenfolge = Prioritaet.
    """
    out, seen = [], set()

    def add(s):
        if s and len(s) >= 2 and s not in seen:
            seen.add(s)
            out.append(s)

    for t in titles:
        base = slugify(t)
        add(base)
        add(re.sub(r"^the-", "", base))
        if base and base[-1] in "aeiou":
            add(base + base[-1])
        if len(out) >= MAX_SLUGS:
            break
    return out[:MAX_SLUGS]


def entry_slugs(e):
    """Slug-Kandidaten aus ALLEN lateinischen Titel-Varianten einer Cache-Serie.

    Nutzt title (EN), title_native, title_romaji und alt_titles -> trifft auch Romaji-Slugs
    (toaru-majutsu-no-index, raise-wa-tanin-ga-ii). Fuer die Sitemap-Discovery-Tools.
    """
    titles = [e.get("title"), e.get("title_native"), e.get("title_romaji")]
    titles += (e.get("alt_titles") or [])
    return slug_candidates([t for t in titles if t])


def _chapter_str(chapter):
    try:
        return str(int(chapter)) if float(chapter) == int(chapter) else str(chapter)
    except (TypeError, ValueError):
        return ""


# Kapitel-Token in einem URL-Pfad (chapter-100, chapter/100, ch_12.5, episode-3 ...)
_CHAPTOK = re.compile(r'(?:chapter|episode|chap|ch)[-_/]?(\d+(?:[.-]\d+)?)', re.I)


def _ok(status, final_url, req_url=None):
    """200 UND nicht auf die Startseite umgeleitet (Pfad bleibt). Erlaubt w1/w7-Subdomain-Redirects,
    lehnt aber Startseiten-Redirects ab (typischer Soft-404 der Einzelserien-Domains).

    Mit `req_url` zusaetzlich: das ANGEFRAGTE Kapitel muss in der finalen URL erhalten bleiben.
    Faengt Serien-Seiten-Redirects (JB-Fund: toongod leitet nicht-existente Kapitel wie chapter-161
    per 200 auf die Serienseite um -> der Link galt faelschlich als ok und fuehrte ins Leere)."""
    if status != 200 or not urlparse(final_url or "").path.strip("/"):
        return False
    if req_url:
        want = _CHAPTOK.search(urlparse(req_url).path)
        if want:
            got = _CHAPTOK.search(urlparse(final_url or "").path)
            if not got or got.group(1) != want.group(1):
                return False
    return True


_TITLE_TAG = re.compile(r'<title[^>]*>(.*?)</title>', re.I | re.S)


_OG_TITLE = re.compile(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']+)', re.I)


def _page_matches(body, titles):
    """IDENTITAETS-CHECK (JB: 'wie finden wir heraus, dass ein Link zum falschen Manga fuehrt?'):
    <title> der Zielseite extrahieren, per clean_title von Kapitel-/Seiten-Zusaetzen befreien und
    gegen die Serien-Titel vergleichen. Teilstring ODER Aehnlichkeit >= 0.5 = derselbe Manga.
    Fehlt <title> (SPA/JS-Seite), zaehlt og:title als ZWEITE Quelle (JB Runde 42 — SPAs
    setzen die Meta fast immer serverseitig); fehlt beides -> KEIN Urteil (True,
    nicht ueber-verwerfen). Rein/testbar."""
    m = _TITLE_TAG.search(body or "") or _OG_TITLE.search(body or "")
    if not m:
        return True
    page = norm(clean_title(m.group(1)))
    if not page:
        return True
    for t in titles or []:
        nt = norm(t or "")
        if nt and (nt in page or page in nt):
            return True
    best = max((difflib.SequenceMatcher(None, page, norm(t)).ratio()
                for t in (titles or []) if t and norm(t)), default=0.0)
    return best >= 0.5


# Cloudflare-/Bot-Schutz-Zwischenseiten kommen oft mit HTTP 200 (JB-Fund Runde 31, Jigokuraku:
# 'Just a moment…' als 200 -> Identitaets-Check sah die falsche Seite -> korrekter Link galt
# als tot). Solche Marker bedeuten 'blocked', nie 'no'.
_CF_MARKERS = ("just a moment", "checking your browser", "cf-chl", "attention required",
               "enable javascript and cookies", "ddos-guard", "cf_chl_opt")


_PAGE_IMG = re.compile(r'(?:data-src|data-lazy-src|src)=["\']([^"\']+\.(?:jpe?g|png|webp)[^"\']*)["\']', re.I)
_IMG_NOISE = re.compile(r'logo|icon|avatar|banner|sprite|ads?|/flags?/|emoji|cover|thumb|profile', re.I)


def _images_hard_blocked(body, page_url, fetch_img=None):
    """True, wenn die Kapitel-Seite Seitenbilder LISTET, deren CDN sie aber hart sperrt
    (JB-Fund 14.07., comicasura 'zeigt keine Bilder': HTML 200 + Titel ok, aber alle
    Bild-Dateien des Kapitels 403 auf imgs-2.2xstorage.com — nur einzelne Kapitel betroffen).

    Konservativ: OHNE gelistete Seitenbilder (JS-Reader laden per Script nach) KEIN Urteil
    (False); nur ein bewiesenes 404/410 aufs ERSTE echte Seitenbild zaehlt. 403 zaehlt
    BEWUSST NICHT: Bild-CDNs (2xstorage) kippen nach wenigen Probes in ein IP-Rate-Limit
    mit pauschal 403 (live beobachtet: dieselbe Datei 200 -> Minuten spaeter 403) — ein
    403-Urteil wuerde gute Links in Serie verwerfen (JB-No-Go, manga-link-audit-regel).
    Netz injizierbar (Tests)."""
    pages = [u for u in _PAGE_IMG.findall(body or "") if not _IMG_NOISE.search(u)]
    if not pages:
        return False
    img = pages[0]
    if img.startswith("//"):
        img = "https:" + img
    elif img.startswith("/"):
        img = f"https://{host(page_url)}{img}"
    elif not img.startswith("http"):
        return False
    if fetch_img is None:
        def fetch_img(u):
            # Browser-typische Bild-Header: moderne CDN-Hotlink-Schutze (2xstorage) geben
            # ohne Sec-Fetch-* pauschal 403 — das waere ein falsches 'gesperrt'-Urteil.
            req = urllib.request.Request(u, headers={**_UA, "Referer": page_url,
                                                     "Accept": "image/avif,image/webp,image/*,*/*",
                                                     "Sec-Fetch-Dest": "image",
                                                     "Sec-Fetch-Mode": "no-cors",
                                                     "Sec-Fetch-Site": "cross-site"})
            try:
                with urllib.request.urlopen(req, timeout=8) as r:
                    return getattr(r, "status", 200)
            except urllib.error.HTTPError as e:
                return e.code
            except Exception:
                return 0            # Timeout/Netz -> KEIN Urteil (nie ueber-verwerfen)
    return fetch_img(img) in (404, 410)


def _alive_status(url, titles=None):
    """GET -> 'ok' | 'no' | 'blocked' | 'odd'.

    'ok'      = Kapitel-Seite existiert (200, Pfad erhalten, Identitaet bestaetigt).
    'no'      = BEWIESEN nicht vorhanden: 404, oder Redirect mit verlorenem/falschem
                Kapitel-Token (toongod-Fall: nicht existentes Kapitel -> Serienseite).
    'blocked' = Bot-Sperre: 403/429/503 oder Cloudflare-Challenge MIT 200.
    'odd'     = 200, aber NICHT einordenbar: Root-Redirect oder fremder Seiteninhalt
                (Identitaets-Check schlaegt fehl — unter Last liefern Reader Drossel-
                Seiten ohne bekannte Marker, JB-Fund Runde 31 Jigokuraku). Kuratierte
                Map-Treffer duerfen 'odd' vertrauen; GERATENE Links niemals."""
    READER_PACER.wait()
    hp = _HOST_PACERS.get(host(url) or "")
    if hp:
        hp.wait()
    req = urllib.request.Request(url, headers=_UA)
    try:
        with urllib.request.urlopen(req, timeout=8) as r:
            status = getattr(r, "status", 200)
            final = r.geturl() or url
            if status != 200:
                return "no"
            if not urlparse(final).path.strip("/"):
                return "odd"                      # Startseiten-Redirect = Soft-Drossel
            want = _CHAPTOK.search(urlparse(url).path)
            if want:
                got = _CHAPTOK.search(urlparse(final).path)
                if not got or got.group(1) != want.group(1):
                    return "no"                   # Kapitel nachweislich weg (Serien-Redirect)
            body = r.read(40000).decode("utf-8", "replace")
            if any(m in body[:6000].lower() for m in _CF_MARKERS):
                return "blocked"
            if titles and not _page_matches(body, titles):
                return "odd"                      # 200, aber fremder Inhalt -> nicht einordenbar
            # Bild-BEWEIS nur fuer Ok-Kandidaten: Seitenbilder stehen oft erst tief im HTML
            # (comicasura ~59KB) -> gezielt nachlesen, statt jeden Check zu verteuern.
            body += r.read(160000).decode("utf-8", "replace")
            if _images_hard_blocked(body, url):
                return "odd"                      # Seite ok, aber Seitenbilder hart gesperrt
                                                  # (comicasura-Fall) -> als Rate-Link nie 'ok'
            return "ok"
    except urllib.error.HTTPError as e:
        return "blocked" if e.code in (403, 429, 503) else "no"   # 404 = gibt es dort nicht
    except Exception:
        return "no"           # Timeout/Verbindungsfehler -> als nicht verfuegbar werten


def _alive(url, titles=None):
    """GET -> True, wenn die Kapitel-Seite BESTAETIGT existiert (Bot-Block zaehlt als nein)."""
    return _alive_status(url, titles) == "ok"


def fetch_status(url, timeout=10, body_bytes=80000):
    """GET -> (status, final_url, body). Fuer Reader-Status/Bild-Check.
    status 403 = Cloudflare (im Browser nutzbar), 0 = Timeout/Verbindungsfehler (down)."""
    req = urllib.request.Request(url, headers=_UA)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return getattr(r, "status", 200), (r.geturl() or url), r.read(body_bytes).decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, url, ""
    except Exception:
        return 0, url, ""


def has_images(html_text):
    """Heuristik: enthaelt eine (WP/Madara-)Kapitelseite echte Seitenbilder? Logos/Icons gefiltert.
    Konservativ: True ab >=2 Bild-URLs. Erkennt tote Eigendomains, die 200 geben aber leer sind.
    (Unzuverlaessig bei JS-Readern, die Bilder per Script nachladen -> nur fuer WP/Madara-Seiten.)"""
    imgs = re.findall(r'(?:src|data-src|data-lazy-src)=["\']([^"\']+\.(?:jpe?g|png|webp)[^"\']*)["\']',
                      html_text or "", re.I)
    pages = [u for u in imgs if not re.search(r'logo|icon|avatar|banner|sprite|ads?|/flags?/|emoji', u, re.I)]
    return len(pages) >= 2


# Discovery-Datenbanken (data/*_map.json[.gz], z.B. mangafire ~53k Serien) als DIREKTE Link-Quelle.
# JB-Punkt: die Maps wurden bisher nur woechentlich in Overrides gegossen — jetzt schlaegt der
# Link-Bau SOFORT darin nach. Deckt auch Slugs mit unratbaren ID-Suffixen (…witchh.529n9) und
# ALTERNATIVE Titel ab (alle Titel-Varianten werden normiert nachgeschlagen).
_SITEMAPS = None
_SM_KEYS = None          # sortierte Keys           -> Praefix-Suche per bisect
_SM_RKEYS = None         # sortierte UMGEDREHTE Keys -> Suffix-Suche per bisect
_SM_SRC = None           # zuletzt indexiertes Dict (erkennt Test-Injektionen)
_AFFIX_MIN = 12          # ab dieser Laenge ist ein Titel-TEIL beweiskraeftig (JB-Guard: nie <4)
_NEAR_RATIO = 0.9        # Beinahe-Treffer-Schwelle (TSUEEE vs tueee, Dahlia vs Dahliya)


def _index_sitemaps(mapping):
    """Sitemap-Dict indexieren (auch fuer Tests): exakter Lookup + beide Sortier-Listen."""
    global _SITEMAPS, _SM_KEYS, _SM_RKEYS, _SM_SRC
    _SITEMAPS = dict(mapping)
    _SM_KEYS = sorted(_SITEMAPS)
    _SM_RKEYS = sorted(k[::-1] for k in _SITEMAPS)
    _SM_SRC = _SITEMAPS


def _load_sitemaps():
    if _SITEMAPS is not None:
        # Tests injizieren _SITEMAPS direkt (monkeypatch) -> Sortier-Indizes nachziehen,
        # sobald das Dict ein anderes Objekt ist als das zuletzt indexierte.
        if _SM_SRC is not _SITEMAPS:
            _index_sitemaps(_SITEMAPS)
        return
    m = {}
    data = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
    for p in glob.glob(os.path.join(data, "*_map.json.gz")) + glob.glob(os.path.join(data, "*_map.json")):
        try:
            opener = gzip.open(p, "rt", encoding="utf-8") if p.endswith(".gz") else open(p, encoding="utf-8")
            with opener as f:
                raw = json.load(f)
            # AUCH Eintraege OHNE {n} aufnehmen (JB-Fund Runde 31: roliascan/weebcentral sind
            # SERIEN-Seiten-Maps, 3541 Serien — die flogen hier komplett raus). Kapitel dazu
            # liefert die Ernte (harvest_chapter_link) direkt von der Serien-Seite.
            for k, tpl in raw.items():
                if not (isinstance(tpl, str) and tpl.startswith("https://")):
                    continue
                # Totes mangafire-/read/-Schema (JB 07.07.2026) wird seit 14.07. GEHEILT statt
                # gefiltert: lokal zur kanonischen /title/-Serien-Seite umgebaut (Ernte zieht
                # das Kapitel) -> die 53k-Map lebt wieder, auch mit gebuendelter alter DB.
                if is_dead_read_scheme(tpl):
                    tpl = heal_read_scheme(tpl)
                    if not tpl:
                        continue
                m.setdefault(norm(k), tpl)
        except Exception:
            continue
    _index_sitemaps(m)


def _shared_prefix_len(a, b):
    n = 0
    while n < min(len(a), len(b)) and a[n] == b[n]:
        n += 1
    return n


def _affix_keys(nt):
    """Map-Keys, bei denen `nt` ein beweiskraeftiger PRAEFIX/SUFFIX ist — oder umgekehrt.

    MangaFire-Keys kleben oft Romaji+Englisch aneinander (…utsumukanai-dahliya-wilts-no-more);
    ein exakter Lookup verfehlt sie, obwohl wir BEIDE Teile als Titel kennen (JB-Faelle Dahlia,
    'Love Revolution (232)'). Guards gegen Fehltreffer: der Teil muss >= _AFFIX_MIN Zeichen haben
    UND mindestens die halbe Laenge des Ganzen ODER >= 16 Zeichen (so lang = quasi eindeutig)."""
    import bisect

    def _fits(part, whole):
        # >= 14 Zeichen exakter Praefix/Suffix ist praktisch eindeutig (JB-Fall Runde 29:
        # Map-Key 'mushokunoeiyuu' (14) ist Praefix des vollen Romaji-Titels).
        return len(part) >= _AFFIX_MIN and (2 * len(part) >= len(whole) or len(part) >= 14)

    hits = []
    for arr, needle, unrev in ((_SM_KEYS, nt, lambda k: k),
                               (_SM_RKEYS, nt[::-1], lambda k: k[::-1])):
        i = bisect.bisect_left(arr, needle)
        for j in range(i, min(i + 40, len(arr))):          # Keys, die mit dem Titel BEGINNEN
            k = arr[j]
            if not k.startswith(needle):
                break
            if _fits(needle, k):
                hits.append(unrev(k))
        for j in range(i - 1, max(i - 40, -1), -1):        # Keys, die ein TEIL des Titels sind
            k = arr[j]
            if not k or k[0] != needle[:1]:
                break
            if needle.startswith(k) and _fits(k, needle):
                hits.append(unrev(k))
    return hits


def _near_key(nt):
    """Beinahe-Treffer: DB-Romaji weicht oft um 1-2 Zeichen vom Reader-Slug ab (MangaBaka
    'TSUEEE' vs mangafire 'tueee', 'Dahlia' vs 'Dahliya'). Kandidaten = Nachbarn im sortierten
    Index mit >= _AFFIX_MIN gemeinsamen Anfangszeichen; Urteil per difflib gegen den auf
    Titellaenge gekappten Key. Bei ZWEI aehnlich guten Kandidaten (Serien-Familien wie die
    beiden Dahlia-Ableger) wird bewusst NICHTS geliefert — kein Ratespiel."""
    import bisect
    if len(nt) < _AFFIX_MIN:
        return ""
    i = bisect.bisect_left(_SM_KEYS, nt)
    best, best_r, second = "", 0.0, 0.0
    for j in range(max(0, i - 25), min(i + 25, len(_SM_KEYS))):
        k = _SM_KEYS[j]
        if _shared_prefix_len(k, nt) < _AFFIX_MIN or 2 * len(nt) < len(k):
            continue
        r = difflib.SequenceMatcher(None, nt, k[:len(nt) + 3]).ratio()
        if r > best_r:
            best, best_r, second = k, r, best_r
        elif r > second:
            second = r
    if best_r >= _NEAR_RATIO and best_r - second > 0.02:
        return best
    return ""


def _sitemap_lookup(titles):
    """Alle Titel-Varianten in den Sitemap-DBs nachschlagen -> [(url_template, host), ...].

    Drei Stufen je Titel: exakt -> Praefix/Suffix (zusammengeklebte Keys) -> Beinahe-Treffer.
    Gibt es irgendeinen EXAKTEN Treffer, werden die unschaerferen Stufen uebersprungen."""
    _load_sitemaps()
    exact, fuzzy, seen = [], [], set()

    def add(bucket, key):
        tpl = _SITEMAPS.get(key)
        if tpl and tpl not in seen and not is_dead_reader(host(tpl)):
            seen.add(tpl)
            bucket.append((tpl, host(tpl) or "map"))

    norms = []
    for t in titles or []:
        k = norm(t or "")
        # Schutz vor Mehrdeutigkeit: zu kurze/leere Keys matchen ALLES Moegliche (JB-Fund: Serie
        # '2055' -> norm entfernt die Jahreszahl -> LEERER Key, den jeder CJK-Alt-Titel traf ->
        # voellig fremder Manga als 'geprüfter' Link). Unter 4 Zeichen ist ein Titel kein Beweis.
        if len(k) >= 4 and k not in norms:
            norms.append(k)
    for k in norms:
        add(exact, k)
    if not exact:
        for k in norms:
            for hit in _affix_keys(k):
                add(fuzzy, hit)
            nk = _near_key(k)
            if nk:
                add(fuzzy, nk)
    return exact + fuzzy


def _harvest_num(token):
    """Kapitel-Zahl aus einem URL-Token: 'chapter-8' -> 8.0; roliascan 'ch1-57261' -> 1.0
    (ID-Anhang ab 4 Ziffern abtrennen); nicht deutbar -> None. Rein, testbar."""
    if "-" in token:
        head, tail = token.split("-", 1)
        if tail.isdigit() and len(tail) >= 4:
            token = head                      # ch1-57261: 57261 ist die Kapitel-ID, nicht die Zahl
        else:
            token = token.replace("-", ".")   # chapter-10-5 -> 10.5
    try:
        return float(token)
    except ValueError:
        return None


_CNUM = re.compile(r'/c0*(\d+(?:\.\d+)?)/?(?:$|[?#])')   # mangatown-Stil: /manga/x/c016/
_TAGS = re.compile(r'<[^>]+>')
_ANCHOR = re.compile(r'<a\b[^>]*?href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', re.S | re.I)


def harvest_chapter_link(page_url, chapter, fetch=None):
    """Den DIREKTEN Kapitel-Link von einer SERIEN-Seite ernten -> URL oder ''.

    JB Runde 31+32: Seiten mit opaken Kapitel-IDs sind nicht RATBAR — aber ihre Serien-Seite
    listet die echten Links. Erkannt wird die Kapitelzahl (v2, drei Wege):
      1. im URL-Pfad (comix …/7468952-chapter-8, roliascan /ch1-57261/),
      2. im mangatown-Stil /c016/,
      3. im LINK-TEXT (<a href="/chapters/01JQ…">Chapter 16</a> — weebcentral traegt die
         Zahl NUR im Text, die URL ist eine reine ID).
    Links von der Seite selbst sind Ground-Truth; akzeptiert wird nur derselbe Host + exakt
    die gesuchte Zahl."""
    from urllib.parse import urljoin
    fetch = fetch or (lambda u: fetch_status(u, timeout=10, body_bytes=300000))
    try:
        want = float(_chapter_str(chapter))
    except (TypeError, ValueError):
        return ""
    st, final, body = fetch(page_url)
    if st != 200 or not body:
        return ""
    base = host(page_url)
    for href, text in _ANCHOR.findall(body):
        full = urljoin(final or page_url, href)
        if host(full) != base:
            continue
        path = urlparse(full).path
        num = None
        m = _CHAPTOK.search(path)
        if m:
            num = _harvest_num(m.group(1))
        if num is None:
            m = _CNUM.search(path)
            if m:
                num = _harvest_num(m.group(1))
        if num is None:
            m = CH.search(_TAGS.sub(" ", text)[:160])
            if m:
                num = _harvest_num(m.group(1))
        if num == want:
            return full
    return ""


def _series_page(tpl):
    """Kapitel-Template -> Serien-SEITE (falls ableitbar). Ruecklage, wenn das konkrete Kapitel
    nicht verifizierbar ist (falsche Zaehlung/Botblock): die Serienseite existiert laut Sitemap
    sicher — besser 'öffnen' auf die richtige Serie als gar kein Link (JB-Funde, alle mangafire)."""
    m = re.match(r"(https://mangafire\.to)/read/([^/]+)/", tpl or "")
    if m:
        return f"{m.group(1)}/manga/{m.group(2)}"
    return ""


def has_chapter_token(url):
    """True, wenn die URL ein Kapitel-Token traegt (chapter-12, ch1-57261, episode-3, /c016/)."""
    path = urlparse(url or "").path
    return bool(_CHAPTOK.search(path) or _CNUM.search(path))


# mangadex-URLs: /title/<uuid> = Serien-Seite, /chapter/<uuid> = Kapitel. Die UUID traegt kein
# zaehlbares Token -> has_chapter_token verfehlt mangadex-Kapitel (und trifft sie zufaellig,
# wenn die UUID mit Ziffern beginnt). Fuer die Kapitel-vor-Seite-Regel braucht es beide Formen.
_MD_URL = re.compile(r"https?://(?:www\.)?mangadex\.org/(title|chapter)/([0-9a-fA-F-]{36})", re.I)
# MangaFire-API-Lese-URL: /title/{hid}-{slug}/read/{lang}/{chapterId} — opake Kapitel-ID, KEIN
# 'chapter'-Token. Ohne diese Erkennung galt ein MangaFire-API-Kapitel als Serien-Seite (Bug
# 14.07.: der Heal zaehlte 0, die Kapitel-vor-Seite-Regel haette den API-Link demotet).
_MF_READ_URL = re.compile(r"https?://(?:www\.)?mangafire\.to/title/[^/]+/read/[a-z-]+/\d+", re.I)


def md_title_uuid(url):
    """UUID aus einer mangadex-SERIEN-URL (/title/<uuid>) -> uuid oder ''. Kapitel-URLs -> ''."""
    m = _MD_URL.match(url or "")
    return m.group(2) if m and m.group(1).lower() == "title" else ""


def is_chapter_url(url):
    """True, wenn die URL ein KAPITEL ist (JB-Regel 14.07. 'Kapitel vor Seite'): erkennbares
    Kapitel-Token, mangadex /chapter/<uuid> ODER MangaFire-API-Lese-URL (/read/{lang}/{id}).
    mangadex /title/ und MangaFire-/title/-Serienseiten (ohne /read/) zaehlen NIE."""
    m = _MD_URL.match(url or "")
    if m:
        return m.group(1).lower() == "chapter"
    if _MF_READ_URL.match(url or ""):
        return True
    return has_chapter_token(url)


def swap_chapter(url, chapter):
    """Kapitel-Token einer URL auf `chapter` tauschen (Server-Seite von cfRelink) -> URL/''.

    Getauscht wird NUR eine reine Zahl (chapter-84 -> chapter-110); Tokens mit ID-Anhang
    (roliascan ch1-57261) bleiben unangetastet — dort wuerde der Tausch die ID zerstoeren."""
    n = _chapter_str(chapter)
    if not n or not url:
        return ""
    m = _CHAPTOK.search(urlparse(url).path)
    if m and re.fullmatch(r"\d+(?:\.\d+)?", m.group(1)):
        return url.replace(m.group(0), m.group(0)[:len(m.group(0)) - len(m.group(1))] + n, 1)
    m = _CNUM.search(urlparse(url).path)
    if m:
        return url.replace(m.group(0), m.group(0).replace(m.group(1), n, 1), 1)
    return ""


def series_page_of(url):
    """Verlaufs-/Override-URL -> Serien-Seiten-Kandidat fuer die Ernte.

    Das Kapitel-Segment am Ende wird abgeschnitten (…/manga/age_matters/c016/ ->
    …/manga/age_matters/); ohne Kapitel-Token ist die URL vermutlich schon die
    Serien-Seite -> unveraendert. '' bei Unbrauchbarem (JB Runde 32: die eigene
    Lese-Seite des Nutzers ist die beste Ernte-Quelle)."""
    from urllib.parse import urlsplit, urlunsplit
    if not (url or "").startswith("http"):
        return ""
    sp = urlsplit(url)
    parts = [p for p in sp.path.split("/") if p]
    if parts and (_CHAPTOK.search("/" + parts[-1]) or _CNUM.search("/" + parts[-1] + "/")):
        parts = parts[:-1]
    if not parts:
        return ""
    return urlunsplit((sp.scheme, sp.netloc, "/" + "/".join(parts) + "/", "", ""))


def find_chapters(titles, chapter, mtype=None, limit=3, fetch=None, prefer_hosts=None, probe=None,
                  prefer_page=False, harvest=None, extra_pages=None, adult=False):
    """Bis zu `limit` VERIFIZIERTE Reader-Kapitel-Links -> [(url, reader_name), ...].

    LEITREGEL (JB Runde 31, Jigokuraku/Baki/Sage): KAPITEL-Links gewinnen ueber ALLE Quellen
    hinweg — eine Serien-Seite ist erst die allerletzte Ruecklage, wenn wirklich keine Quelle
    das Kapitel liefert. Stufen: Map-Kapitel (blocked-Trust) -> Kapitel-ERNTE von Serien-
    Seiten (opake IDs wie comix/roliascan) -> Muster-Reader (streng) -> mangago-Rater ->
    Serien-Seite. `prefer_page=True` (unbekannter Lesestand): SERIEN-Seite statt geratenem
    'Kapitel 1' — dort entscheidet der Leser selbst, wo er einsteigt.
    `prefer_hosts` = Reader-Praeferenz (die Seiten, auf denen der Nutzer WIRKLICH liest).
    `probe` (Tests) liefert 'ok'/'no'/'blocked'; `fetch` (bool) bleibt zur Kompatibilitaet;
    `harvest` ist injizierbar — bei injiziertem Netz (Tests/Discovery) erntet default NICHTS.
    """
    n = _chapter_str(chapter)
    if not n and not prefer_page:
        return []
    injected = fetch is not None or probe is not None
    # Echte Pruefung inkl. Identitaets-Check (Zielseite muss DIESE Serie zeigen); injizierte
    # fetch-Funktionen (Tests/Discovery) bleiben unveraendert bool(url).
    if probe is None:
        probe = (lambda u: "ok" if fetch(u) else "no") if fetch else (lambda u: _alive_status(u, titles))
    if harvest is None:
        harvest = (lambda p, nn: "") if injected else harvest_chapter_link
    check = lambda u: probe(u) == "ok"   # noqa: E731 — strenge Sicht fuer geratene Muster-Links
    hits = _sitemap_lookup(titles)
    # Serien-SEITEN-Kandidaten, PRIORISIERT (JB Runde 32: 'Prioritaet bei Mustern anpassen'):
    # zuerst `extra_pages` — die eigene Lese-Seite des Nutzers und JB-kuratierte Seiten-
    # Overrides —, dann Map-Eintraege ohne {n} (roliascan/weebcentral) und die aus
    # Kapitel-Templates ableitbaren Seiten (mangafire).
    pages = [(p, h) for p, h in (extra_pages or []) if p]
    pages += [(p, h) for p, h in
              (((tpl if "{n}" not in tpl else _series_page(tpl)), h) for tpl, h in hits) if p]
    if prefer_page:
        for purl, h in pages:            # kuratierte Map-Seite -> Bot-Block/odd zaehlt (existiert sicher)
            if probe(purl) in ("ok", "blocked", "odd"):
                return [(purl, h)]
        gp = guess_series_pages(titles, probe)
        if gp or not n:
            return gp                    # keine Seite und kein Lesestand -> ehrlich leer
    out = []
    # 1) Map-KAPITEL: exakte Serien-Templates (inkl. ID-Suffixe/Alternativtitel), die kein
    #    Muster raten kann — jeder Treffer wird verifiziert, ABER: eine Bot-Sperre (403) gilt
    #    NICHT als tot (kuratierte Sitemap; im Browser funktioniert der Link, JB-verifiziert).
    for tpl, h in hits:
        if "{n}" not in tpl:
            continue
        url = tpl.replace("{n}", n)
        # Kuratierter Map-Treffer: nur ein BEWIESENES 'gibt es nicht' (404/Kapitel-Redirect)
        # verwirft — 'blocked' und 'odd' (Drossel-Seiten unter Last) zaehlen als vorhanden.
        if probe(url) in ("ok", "blocked", "odd"):
            out.append((url, h))
        if len(out) >= limit:
            return out
    # 2) Kapitel-ERNTE: Serien-Seiten laden und den echten Kapitel-Link herausziehen —
    #    die einzige Chance bei opaken Kapitel-IDs (comix 7468952-chapter-8, roliascan ch1-57261).
    _taken = {host(u) for u, _ in out}
    for purl, h in pages:
        if host(purl) in _taken:
            continue
        curl = harvest(purl, n)
        if curl:
            out.append((curl, host(curl) or h))
            _taken.add(host(curl))
        if len(out) >= limit:
            return out
    # 3) Muster-Reader als Ergaenzung (ein Host nur einmal — Map-/Ernte-Treffer zaehlen mit)
    slugs = slug_candidates([t for t in titles if t])[:SEARCH_SLUGS]
    mt = (mtype or "").lower()
    group = ("manhwa" if mt in ("manhwa", "manhua", "webtoon")
             else "manga" if mt == "manga" else "")
    # type='adult' (JB-Go Runde 43): Adult-Spezialreader werden AUSSCHLIESSLICH fuer
    # 18+-Serien (adult=True <- adult_kind=='sexual') befragt — nie fuer normale Serien.
    pool = [r for r in PATTERN_READERS if adult or r.get("type") != "adult"]
    readers = ([r for r in pool if r["type"] in (group, "any", "adult")]
               if group else list(pool))
    # Sperrliste auch hier: readers_pattern.json wird automatisch gepflegt — landet ein spaeter
    # gesperrter Host darin, darf er trotzdem nie wieder Links liefern.
    readers = [r for r in readers if not is_dead_reader(r.get("host") or host(r.get("chapter") or ""))]
    if prefer_hosts:
        ph = [h.lower() for h in prefer_hosts if h]
        readers = sorted(readers, key=lambda rd: (ph.index(hh) if (hh := (host(rd.get("chapter") or "") or "").lower()) in ph
                                                  else len(ph)))
    for rd in readers:
        if host(rd.get("chapter") or "") in _taken:
            continue
        for slug in slugs:
            url = rd["chapter"].format(slug=slug, n=n)
            if check(url):
                out.append((url, rd["name"]))
                break
        if len(out) >= limit:
            break
    # 4) Serien-Seite aus den MAPS als Ruecklage (kuratiert > geraten; Label wird 'öffnen').
    if not out:
        for purl, h in pages:
            if probe(purl) in ("ok", "blocked", "odd"):
                out.append((purl, h))
                break
    # 5) Serien-SEITEN-Rater als allerletzte Stufe: besser 'öffnen' auf die richtige Serie
    #    als gar kein Link (JB Runde 29: mangago listet Serien, die sonst niemand hat).
    if not out:
        out += guess_series_pages(titles, probe)
    return out


# Serien-SEITEN-Quellen (JB: 'mangago entschluesseln'): Kapitel-URLs sind dort NICHT ratbar
# (opake Kapitel-IDs wie mpn_chapter-2077894), die Serien-Seite aber schon — und mangago
# liefert ein ECHTES 404 fuer Muell-Slugs (geprueft 04.07.2026). `sep` = Slug-Trennzeichen.
SERIES_GUESSERS = (
    {"name": "mangago.me", "page": "https://www.mangago.me/read-manga/{slug}/", "sep": "_"},
)


def guess_series_pages(titles, probe, limit=1):
    """Serien-Seite per Slug-Raten + STRENGER Verifikation -> [(url, host), ...].

    NUR 'ok' zaehlt: 200 + Identitaets-Check (<title> der Zielseite muss DIESE Serie zeigen,
    steckt im injizierten `probe`). Ein Bot-Block ist hier KEIN Beweis — der Slug ist geraten.
    So koennen neue Quellen ohne Sitemap/Suche angeschlossen werden, ohne Falschlinks."""
    out = []
    for g in SERIES_GUESSERS:
        if is_dead_reader(host(g["page"].format(slug="x")) or g["name"]):
            continue
        for slug in slug_candidates([t for t in titles if t])[:SEARCH_SLUGS]:
            url = g["page"].format(slug=slug.replace("-", g["sep"]))
            if probe(url) == "ok":
                out.append((url, host(url) or g["name"]))
                break
        if len(out) >= limit:
            break
    return out


def find_chapter(titles, chapter, fetch=None):
    """Einen verifizierten Reader-Kapitel-Link -> (url, reader_name) oder ('', '')."""
    hits = find_chapters(titles, chapter, mtype=None, limit=1, fetch=fetch)
    return hits[0] if hits else ("", "")


# ---------------- Serien-spezifische Overrides (JBs manuelle Funde) ----------------
SERIES_OVERRIDES = {}        # norm(name) -> {"name":..., "chapter": "...{n}..."}


_DEAD_MF_READ = re.compile(r"^https?://(?:www\.)?mangafire\.to/read/", re.I)


def is_dead_read_scheme(url):
    """True fuer das ALTE, tote mangafire-Reader-Schema `/read/{slug}.{id}/en/chapter-N` (JB/linkhealth
    07.07.2026): seit dem MangaFire-Umbau leitet es per 200 auf die Titelseite um. Solche Overrides
    duerfen nicht mehr greifen — sonst ueberschatten sie (pin) den echten `/title/`-Link aus dem Verlauf."""
    return bool(_DEAD_MF_READ.match(url or ""))


_MF_READ_SID = re.compile(r"https?://(?:www\.)?mangafire\.to/read/([a-z0-9-]+)\.([a-z0-9]+)/", re.I)


def heal_read_scheme(url):
    """Totes mangafire-/read/-Template LOKAL heilen -> kanonische Serien-Seite oder ''.

    JB-Selbstheilungs-Regel (14.07.2026): statt die 53k-Sitemap-Eintraege im alten Schema
    wegzufiltern (Map war dadurch wirkungslos, auch in der exe mit gebuendelter alter DB),
    wird `/read/{slug}.{id}/...` deterministisch zu `/title/{id}-{slug}` umgebaut (live
    verifiziert: exakt das Redirect-Ziel). Serien-Seite ohne {n} — das Kapitel zieht die
    Ernte. Nicht-mangafire/-parsebares -> '' (Aufrufer entscheidet)."""
    m = _MF_READ_SID.match(url or "")
    if not m:
        return ""
    return f"https://mangafire.to/title/{m.group(2)}-{m.group(1)}"


def load_overrides(path):
    """data/series_overrides.json laden -> SERIES_OVERRIDES (norm(name) -> Eintrag). Fehlt -> leer.
    Eintraege im toten mangafire-`/read/`-Schema werden beim Laden GEHEILT (heal_read_scheme ->
    kanonische Serien-Seite; JB-Selbstheilungs-Regel 14.07.) — so leben auch gebuendelte alte
    Override-Staende (exe) sofort weiter; nur Unheilbares wird uebersprungen."""
    global SERIES_OVERRIDES
    try:
        with open(path, encoding="utf-8") as f:
            ov = (json.load(f).get("overrides") or {})
        out = {}
        for k, v in ov.items():
            if not (isinstance(v, dict) and v.get("chapter")):   # {n} optional (auch Serien-Seite)
                continue
            ch = v["chapter"]
            if is_dead_read_scheme(ch):
                ch = heal_read_scheme(ch)
                if not ch:
                    continue
                v = dict(v, chapter=ch)      # geheilt = Serien-Seite; Ernte zieht das Kapitel
            out[norm(k)] = v
        SERIES_OVERRIDES = out
    except (OSError, ValueError, AttributeError):
        pass
    return SERIES_OVERRIDES


def _templatize_chapter(url):
    """Bestaetigten Kapitel-Link -> {n}-Vorlage: die ERSTE Kapitelnummer wird durch {n} ersetzt,
    damit der Override mit dem Lesefortschritt mitwaechst. Keine Kapitelnummer erkennbar -> URL
    unveraendert (dann ein Serien-Seiten-Override). Vorhandenes {n} bleibt (idempotent)."""
    if not url or "{n}" in url:
        return url or ""

    def _repl(m):
        return m.group(0)[: m.start(1) - m.start(0)] + "{n}"        # Praefix (z.B. 'chapter-') + {n}

    return _CHAPTOK.sub(_repl, url, count=1)


def save_series_override(path, key, name, url, pin=True, template=True):
    """Einen von JB BESTAETIGTEN Direktlink NICHT-destruktiv in series_overrides.json schreiben.

    template=True: Kapitel-Link wird zur {n}-Vorlage (waechst mit dem Lesefortschritt) — richtig fuer
    Reader mit nummern-basierten URLs (chapter-N/episode-N: mgeko, webtoons, mangaread, mangahub …).
    template=False: URL wird UNVERAENDERT gepinnt — noetig fuer Reader mit OPAKEN Kapitel-IDs
    (mangafire /title/…/chapter/8110971, comix, mangadex/chapter/UUID), deren Nummer nicht in der
    URL steht; hier waere eine {n}-Vorlage falsch. "trust" spart die Netz-Pruefung (JB verbuergt sich),
    "pin" macht den Link zur verbindlichen Aktion der Serie. Andere Eintraege + der _hinweis-Kommentar
    bleiben; geschrieben wird atomar. Gibt den geschriebenen Eintrag zurueck."""
    key = norm(key or "")
    if not key or not name or not url:
        raise ValueError("key, name und url sind Pflicht")
    data = {}
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except ValueError:
            data = {}
    if not isinstance(data, dict):
        data = {}
    ov = data.setdefault("overrides", {})
    entry = {"name": name, "chapter": _templatize_chapter(url) if template else url,
             "trust": True, "pin": bool(pin)}
    ov[key] = entry
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path)
    return entry


# Viele Mangas haben eine EIGENE Lesedomain (SEO-Manga-Seiten). Typische Domain-Endungen + Pfade;
# der Slug wird ent-bindestrichelt fuer die Domain ({ds}) und behaelt Bindestriche fuer den Pfad ({hs}).
DEDICATED_DOMAINS = ("read{ds}.online", "{ds}manga.com", "{ds}chapters.online", "{ds}.com",
                     "{ds}manga.online", "{ds}.online", "{ds}scans.com", "{ds}manga.net",
                     "{ds}manga.site", "{ds}.site", "read{ds}.com", "{ds}manga.org", "{ds}.net")
DEDICATED_PATHS = ("/manga/{hs}-chapter-{n}/", "/comic/{hs}-chapter-{n}/", "/{hs}-chapter-{n}/")


def _real_images(url):
    """True, wenn die Kapitelseite echte Seitenbilder im HTML hat (WP/Madara). Fuer den Bild-Check."""
    st, _f, body = fetch_status(url, timeout=8)
    return st == 200 and has_images(body)


def dedicated_link(slugs, probe_chapter, fetch=None, require_images=False):
    """Eigene Lesedomain einer Serie raten + STRIKT verifizieren -> (template, host) oder ('', '').

    `template` enthaelt {n} (fuer beliebige Kapitel, z.B. als Override speicherbar). Geprueft wird
    mit `probe_chapter` (ein existierendes Kapitel, z.B. 1): Kapitel lebt UND Muell-Kapitel fuehrt
    auf Startseite/404. Nicht-existente Domains fallen per DNS sofort durch. `fetch` injizierbar.
    `require_images` (Discovery): zusaetzlich pruefen, dass die Seite echte Bilder hat -> filtert
    tote SEO-Domains, die 200 liefern aber keine Bilder zeigen (JBs Fall)."""
    n = _chapter_str(probe_chapter)
    if not n:
        return "", ""
    check = fetch or _fast_alive
    for hs in [s for s in slugs if s][:2]:
        ds = hs.replace("-", "")
        if len(ds) < 4:
            continue
        for dpat in DEDICATED_DOMAINS:
            dom = dpat.format(ds=ds)
            if is_dead_reader(dom):     # gesperrte Domain (Interstitial-Netz) NIE raten (JB: vinlandsagamanga)
                continue
            for ppat in DEDICATED_PATHS:
                tpl = "https://" + dom + ppat.replace("{hs}", hs)
                if check(tpl.format(n=n)) and not check(tpl.format(n="99999")):
                    if require_images and not _real_images(tpl.format(n=n)):
                        continue                   # tote Domain (200, aber keine Bilder) -> verwerfen
                    return tpl, dom
    return "", ""


_CX_TITLE = re.compile(r'/title/([a-z0-9]{4,})-([a-z0-9\-]{3,})')


def cx_chapter_link(titles, chapter, fetch=None):
    """comix.to-SUCHE -> Serien-Seite -> Kapitel-ERNTE (JB Runde 42, Option 5).

    EHRLICHE GRENZE (Live-Smoke 04.07.): comix rendert Suchtreffer NUR per JS (SSR-HTML
    leer) und hat KEINE Sitemap — diese Stufe greift derzeit nur, wenn die Serie zufaellig
    in den serverseitigen Listen auftaucht. Bleibt als Rueckfalloption (falls comix wieder
    SSR rendert); comix-Links kommen sonst ueber JBs Overrides/Verlauf (Proto-Eye-Weg).
    Waechter: der Treffer-SLUG muss norm-gleich/>=0.9 zu einem unserer Titel sein."""
    titles = [t for t in (titles if isinstance(titles, (list, tuple)) else [titles]) if t]
    for q in titles[:3]:
        try:
            READER_PACER.wait()
            _st, _f, body = fetch_status(
                "https://comix.to/?s=" + urllib.parse.quote(str(q)), timeout=12,
                body_bytes=_SEARCH_BODY)
        except Exception:
            continue
        seen = set()
        for m in _CX_TITLE.finditer(body or ""):
            sid, slug = m.group(1), m.group(2)
            if slug in seen:
                continue
            seen.add(slug)
            ns = norm(slug.replace("-", " "))
            if not any(ns == norm(t) or difflib.SequenceMatcher(
                    None, ns, norm(t)).ratio() >= 0.9 for t in titles):
                continue
            u = harvest_chapter_link(f"https://comix.to/title/{sid}-{slug}", chapter,
                                     fetch=fetch)
            if u:
                return u, "comix.to"
    return "", ""


# Reader mit funktionierender Madara-/WP-Suche (?s=) — fuer die SUCH-ERNTE, wenn
# Slug-Raten scheitert (JB Runde 42, Option 1: Reader benennen Serien nach ANDEREN
# Alt-Titeln wie 'the-regressed-mercenarys-machinations' — die Suche findet den echten Slug).
SEARCHABLE_READERS = ("mangaread.org", "kaliscan.com", "mangatx.cc", "manganow.to")
# NUR-SUCH-Reader (Runde 42, mangaread-Fund): Soft-404-Seiten sind als MUSTER-Reader tabu
# (Muell-404-Probe scheitert), aber ueber die SUCHE + IDENTITAETS-CHECK der Kapitelseite
# (Titel muss stimmen) werden sie sicher nutzbar — Soft-404 ist damit neutralisiert.
SEARCH_ONLY_READERS = (
    {"name": "MangaRead", "host": "www.mangaread.org", "type": "any",
     "chapter": "https://www.mangaread.org/manga/{slug}/chapter-{n}/"},
)
_WP_MANGA_LINK = re.compile(r'href="https?://[^"]*?/(?:manga|series|webtoon)/([a-z0-9\-]{3,})/?"')
_SEARCH_BODY = 1_500_000     # Suchseiten VOLL lesen (Runde 42: das 80-KB-Cap schnitt die
#                              Trefferlisten ab — sie liegen hinter Sidebar/Skripten)


def search_slug_link(titles, chapter, mtype=None, fetch=None, hosts=None, cap=3):
    """Such-Ernte ueber die Seiten-SUCHE -> (url, name) | ('', '').

    Fragt die ?s=&post_type=wp-manga-Suche ab (Madara-Serienpfad), extrahiert den ECHTEN
    Serien-Slug (Waechter: norm-gleich/>=0.9 zu einem Titel) und verifiziert den Kapitel-
    Link per _ok + IDENTITAETS-CHECK (_page_matches) — damit sind auch Soft-404-Seiten
    sicher (die Kapitelseite muss den SERIENTITEL tragen). `fetch` injizierbar (Tests):
    (status, final_url, body) wie fetch_status."""
    titles = [t for t in (titles if isinstance(titles, (list, tuple)) else [titles]) if t]
    if not titles:
        return "", ""
    grab = fetch or fetch_status
    readers = ([r for r in PATTERN_READERS if r["host"] in (hosts or SEARCHABLE_READERS)
                and (not mtype or r["type"] in (mtype, "any"))]
               + [r for r in SEARCH_ONLY_READERS
                  if not mtype or r["type"] in (mtype, "any")])[:cap]
    n = _chapter_str(chapter)
    if not n or not readers:
        return "", ""
    for r in readers:
        try:
            READER_PACER.wait()
            _st, _f, body = grab(
                f"https://{r['host']}/?s=" + urllib.parse.quote(str(titles[0]))
                + "&post_type=wp-manga", timeout=12, body_bytes=_SEARCH_BODY)
        except Exception:
            continue
        seen = set()
        for m in _WP_MANGA_LINK.finditer(body or ""):
            slug = m.group(1)
            if slug in seen:
                continue
            seen.add(slug)
            ns = norm(slug.replace("-", " "))
            if not any(ns == norm(t) or difflib.SequenceMatcher(
                    None, ns, norm(t)).ratio() >= 0.9 for t in titles):
                continue
            url = r["chapter"].format(slug=slug, n=n)
            try:
                READER_PACER.wait()
                st2, f2, b2 = grab(url, timeout=12, body_bytes=120_000)
            except Exception:
                continue
            if _ok(st2, f2, url) and _page_matches(b2, titles):
                return url, r["name"]
    return "", ""


def override_info(names, chapter, fetch=None):
    """Wie override_link, mit Zusatz-Flags -> (url, host, is_chapter, pinned).

    is_chapter=True, wenn die kuratierte Vorlage eine {n}-Kapitelnummer traegt. Noetig, weil
    manche Vorlagen KEIN erkennbares Kapitel-Token tragen (JB Runde 35: arenascan
    'solo-leveling-{n}/') — der Override ist trotzdem ein KAPITEL-Link und darf in der
    Dreistufen-Vorrang-Regel nicht als Seiten-Override behandelt werden.
    pinned=True ("pin": true im Eintrag) = JBs Klick-Wahrheit: dieser Link IST die Aktion
    fuer die Serie, alle Heuristiken (Dreistufen-Regel, '?'-Serien-Seite) treten zurueck
    (JB Runde 36, Proto-Eye: '?'-Lesestand zeigte die comix-Serien-Seite, gewuenscht war
    das Kapitel — comix akzeptiert die opake Kapitel-ID auch fuer andere Kapitelnummern)."""
    n = _chapter_str(chapter)
    if not n:
        return "", "", False, False
    check = fetch or _alive
    for name in (names if isinstance(names, (list, tuple)) else [names]):
        o = SERIES_OVERRIDES.get(norm(name or ""))
        if o:
            url = o["chapter"].format(n=n)
            # "trust": true -> ohne Pruefung uebernehmen (Seiten, die Bots blocken, z.B. MangaFire;
            # JB verbuergt sich fuer den Link). Sonst wie immer per echtem 404 verifizieren.
            if o.get("trust") or check(url):
                return (url, (host(url) or o.get("name") or ""),
                        "{n}" in o["chapter"], bool(o.get("pin")))
    return "", "", False, False


def override_link(names, chapter, fetch=None):
    """Verifizierter manueller Reader-Link aus series_overrides -> (url, host) oder ('', '').

    `names` = ein Name oder mehrere Kandidaten (EN-Titel + Roh-Name). Der Link wird wie jeder
    andere per echtem 404 geprueft; nur ein 200er wird zurueckgegeben.
    """
    url, h, _, _ = override_info(names, chapter, fetch)
    return url, h


# ---------------- Selbst-Erweiterung + Selbst-Bereinigung (Discovery-Tool) ----------------
# Bekannte, populaere Test-Serien je Typ (zum Erkennen eines verifizierbaren URL-Musters).
DISCOVERY_SERIES = {
    "manga": [("one-piece", "1000"), ("berserk", "100"), ("naruto", "100")],
    "manhwa": [("solo-leveling", "100"), ("tower-of-god", "300"), ("the-beginning-after-the-end", "100")],
}
_SKIP_TAGS = {"raw", "raw manhua", "login", "physical"}


def _reader_name(host):
    base = host.split(".")[0]
    return base[:1].upper() + base[1:]


def _reliable(tpl, slug, n, check):
    """Muster ist VERLAESSLICH, wenn: echtes Kapitel 200, ABER Muell-Slug UND Muell-Kapitel (99999)
    je 404. Der Muell-Kapitel-Test entlarvt Soft-404-Reader (die 200 fuer alles liefern)."""
    return (check(tpl.format(slug=slug, n=n))
            and not check(tpl.format(slug="zzqx-not-real-xyz", n=n))
            and not check(tpl.format(slug=slug, n="99999")))


def verify_reader(reader, fetch=None, series=None):
    """Prueft, ob ein Reader noch ZUVERLAESSIG funktioniert (echtes Kapitel 200, Muell + Muell-Kapitel 404)."""
    check = fetch or _alive
    series = series or DISCOVERY_SERIES
    cats = ["manga", "manhwa"] if reader.get("type") in ("any", None) else [reader["type"]]
    for cat in cats:
        for slug, n in series.get(cat, []):
            if _reliable(reader["chapter"], slug, n, check):
                return True
    return False


def _fast_alive(url, timeout=5):
    """Wie _alive, aber OHNE globalen Pacer + kuerzerer Timeout (fuer die parallele Discovery)."""
    req = urllib.request.Request(url, headers=_UA)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return _ok(getattr(r, "status", 200), r.geturl() or url, url)
    except urllib.error.HTTPError:
        return False
    except Exception:
        return False


def _probe_host(host, cat, series, patterns, check):
    """Ein Host: das erste Muster finden, das ZUVERLAESSIG verifiziert -> reader-dict oder None."""
    for tpl in patterns:
        full = tpl.replace("{h}", host)        # -> Vorlage mit nur noch {slug}/{n}
        if any(_reliable(full, slug, n, check) for slug, n in series.get(cat, [])):
            return {"name": _reader_name(host), "host": host, "type": cat, "chapter": full}
    return None


def discover(snap, fetch=None, series=None, patterns=CANDIDATE_PATTERNS, workers=1):
    """everythingmoe-Snapshot nach ZUVERLAESSIGEN Readern absuchen -> [reader-dict, ...].

    Je Host (manga/manhwa, ohne raw/login/print) die Kandidaten-Muster streng testen (echtes
    Kapitel 200, Muell-Slug + Muell-Kapitel je 404 -> kein Soft-404). `workers>1` probt die Hosts
    parallel mit kurzem Timeout (deutlich schneller). Reine Funktion (fetch injizierbar fuer Tests).
    """
    series = series or DISCOVERY_SERIES
    check = fetch or (_alive if workers <= 1 else _fast_alive)
    seen, hosts = set(), []
    for it in (snap.get("items") or []):
        cat, host = it.get("category"), it.get("host")
        if cat not in ("manga", "manhwa") or not host or host in seen:
            continue
        if {t.lower() for t in it.get("tags", [])} & _SKIP_TAGS:
            continue
        seen.add(host)
        hosts.append((host, cat))
    if workers <= 1:
        res = [_probe_host(h, c, series, patterns, check) for h, c in hosts]
    else:
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=workers) as ex:
            res = list(ex.map(lambda hc: _probe_host(hc[0], hc[1], series, patterns, check), hosts))
    return [r for r in res if r]


def merge_readers(existing, discovered):
    """Bestehende (zuerst, Reihenfolge erhalten) + neue Reader vereinigen, ein Host nur einmal."""
    out, seen = [], set()
    for r in list(existing) + list(discovered):
        if _valid_reader(r) and r["host"] not in seen:
            seen.add(r["host"])
            out.append({k: r[k] for k in ("name", "host", "type", "chapter")})
    return out


def save_readers(path, readers, note=None):
    """Reader-Liste nach data/readers_pattern.json schreiben (best effort)."""
    import os
    data = {"_hinweis": note or "Automatisch gepflegt vom Discovery-Tool. type: manga/manhwa/any; "
            "chapter: URL-Vorlage mit {slug}/{n}; Links werden per echtem 404 geprueft.",
            "readers": [{k: r[k] for k in ("name", "host", "type", "chapter")} for r in readers
                        if _valid_reader(r)]}
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except OSError:
        return False
