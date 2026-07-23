# -*- coding: utf-8 -*-
"""
Browser-Scan des Manga-Kerns — Verlauf UND Lesezeichen, read-only.

Phase 3.1: Firefox/Waterfox (`places.sqlite`). Verbatim aus SyncEngine/manga_update.py
herausgeloest (build/find_places/load_db/kids) — KEINE Verhaltensaenderung. Die spaeteren
Schritte ergaenzen die Chromium-Familie (History-SQLite + Bookmarks-JSON) und den
Cross-Browser-Dedup-Merge; Firefox bleibt dabei 1:1.

HARTE REGELN (CLAUDE.md): Browser-DBs werden NUR read-only in einen Temp-Ordner kopiert
(gesperrte DB -> immutable-Kopie); in den Browsern wird nichts veraendert.

Liefert pro Serie ein Dict `items`, keyed by `norm(name)`:
  {'name', 'status', 'chap', 'site', 'lv', 'url'}
"""
import glob
import json
import os
import re
import shutil
import sqlite3
import sys
import tempfile

from .parse import CH, GARB, URLCH, host, norm, series_from

# Hosts, die nie eine Manga-Serie sind (Verlauf-/Lesezeichen-Rauschen filtern).
BLACKLIST = re.compile(r'google|youtube|reddit|amazon|steampowered|store\.steam|steamcommunity|'
    r'twitch|facebook|twitter|x\.com|netflix|disney|github|stackoverflow|chatgpt|openai|\bmail\.|'
    r'docs\.google|drive\.google|paypal|lzo\.com|sparkasse|ebay|gportal|g-portal|maxroll|maxon|'
    r'ebookrenta|renta\.papy|'        # EbookRenta! (Ebook-Verleih, kein Reader) -> generisch raus
    r'mangamirai|'                    # mangamirai.com = Manga-SHOP (JB-Fund: Produktseite wurde 'MANGA MIRAI'-Serie)
    r'inkr\.com|'                     # comics.inkr.com = Kauf-/Shop-Seite, kein Reader (JB-Fund)
    r'web\.archive\.org|'             # Wayback-Besuche wurden zur Fake-Serie 'Wayback Machine' (JB-Fund)
    r'scrmbl|'                        # Presse-Blog: 'Your Manga Week #16' wurde Human-Crossing-"Reader" (JB-Fund)
    r'substack|mangasplaining|'       # Newsletter/Presse: 'Search and Destroy Ch. 13'-POST wurde "Reader" (JB-Fund)

    r'lastepoch|d2jsp|imdb|wikipedia|fandom|spotify|hearthis|soundcloud|bandcamp|co-optimus|9gag|'
    r'pr0gramm|nexus|notion|linkedin|accounts\.|auth\.|^api\.|booking|klm|stoneisland|battle\.net|'
    r'44label|hotel|checkout|klb|epoxy|epoxid|kleb|howlongtobeat|kingofshojo|rizzfables|rizzcomic', re.I)
# Reader-typische URL-Pfade (zusammen mit einer Kapitelnummer ein starkes Manga-Signal).
MPATH = re.compile(r'/(?:manga|series|title|chapter|read|reader|comic|comics|book)/', re.I)

# everythingmoe-Reader-Domains (kuratiert, ~172) als DATENBANK bekannter Manga-Seiten: ein bekannter
# Reader-Host + Kapitelnummer ist auch dann ein Manga, wenn der URL-Pfad untypisch ist (JB-Wunsch:
# keine Reader-Seite uebersehen, auch Seiten die nicht nach Manga "klingen").
_KNOWN_READERS = None
# Pfad des Listen-Imports als Modul-Konstante -> Tests koennen ihn umbiegen (Isolation: eine echte
# imported_series.json auf dem Rechner darf nie Unit-Tests beeinflussen; JB-Vorfall Runde 22).
IMPORTED_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "imported_series.json")


def known_readers():
    """Menge der kuratierten Reader-Hosts (data/readers_moe.json), lazy + gecacht. Fehlt -> leer."""
    global _KNOWN_READERS
    if _KNOWN_READERS is None:
        try:
            p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "readers_moe.json")
            with open(p, encoding="utf-8") as f:
                _KNOWN_READERS = {it["host"].lower() for it in (json.load(f).get("items") or []) if it.get("host")}
        except Exception:
            _KNOWN_READERS = set()
    return _KNOWN_READERS

# Lesezeichen-Ordnernamen -> User-Status. Reihenfolge = Prioritaet (erste Treffer gewinnt).
# Wird fuer die Chromium-Familie analog genutzt (Ordnernamen aus Bookmarks-JSON).
FOLDER_STATUS = (("manga incomplete", "Am Lesen"),
                 ("forgotten chapter", "Unsicher"),
                 ("manga complete", "Fertig"))


def folder_status(title):
    """Ordnertitel -> User-Status (Am Lesen/Unsicher/Fertig) oder None, wenn kein Manga-Ordner."""
    low = (title or '').lower()
    for sub, status in FOLDER_STATUS:
        if sub in low:
            return status
    return None


# ---------------- gemeinsame DB-Helfer (read-only) ----------------

def copy_locked(src, name):
    """Eine evtl. gesperrte DB read-only nach Temp kopieren (+ -wal/-shm). Gibt den Temp-Pfad.

    `name` = Zieldateiname im Temp-Ordner (z.B. "places_copy.sqlite"). Der Browser kann
    laufen; gelesen wird ausschliesslich die Kopie, nie das Original.

    PROZESS-EIGENER Name (Befund 23.07.): der Zielname bekommt die PID angehaengt.
    Vorher war er FEST — liefen zwei Scans gleichzeitig, ueberschrieben sie einander
    die Kopie und lasen fremde Daten. Im Gate (8 Parallel-Prozesse) kippte dadurch
    test_scan_firefox_history_bookmarks_and_merge sporadisch (Lesezeichen-Status
    'Gelesen' statt 'Am Lesen'); produktiv trifft dieselbe Falle Tray-Sync + manuellen
    Lauf zur gleichen Zeit. Aufraeumen bleibt Sache des Temp-Ordners (nie loeschen wir
    fremde Dateien).
    """
    stamm, endung = os.path.splitext(name)
    tmp = os.path.join(tempfile.gettempdir(), f"{stamm}_{os.getpid()}{endung}")
    shutil.copy(src, tmp)
    for ext in ("-wal", "-shm"):
        if os.path.exists(src + ext):
            try:
                shutil.copy(src + ext, tmp + ext)
            except OSError:
                pass
    return tmp


def open_immutable(path):
    """SQLite-Verbindung im immutable-Modus (rein lesend, ignoriert Locks der Kopie)."""
    return sqlite3.connect(f"file:{path}?immutable=1", uri=True)


# ---------------- Zeit-Umrechnung der Verlauf-Zeitstempel ----------------
# Firefox `last_visit_date`: Mikrosekunden seit 1970-01-01 (Unix).
# Chromium `last_visit_time`: Mikrosekunden seit 1601-01-01 -> Offset zu Unix abziehen.
CHROMIUM_EPOCH_OFFSET = 11644473600   # Sekunden zwischen 1601-01-01 und 1970-01-01 (UTC)


def firefox_time(val):
    """Firefox-Verlaufszeit (us seit 1970) -> Unix-Sekunden (0 bei leer)."""
    return val / 1e6 if val else 0


def chromium_time(val):
    """Chromium-Verlaufszeit (us seit 1601) -> Unix-Sekunden (0 bei leer)."""
    return val / 1e6 - CHROMIUM_EPOCH_OFFSET if val else 0


SAFARI_EPOCH_OFFSET = 978307200   # Sekunden zwischen 1970-01-01 und 2001-01-01 (Core-Data-Epoche)


def safari_time(val):
    """Safari-Verlaufszeit (s seit 2001, Core Data) -> Unix-Sekunden (0 bei leer)."""
    return val + SAFARI_EPOCH_OFFSET if val else 0


def _history_map(rows, time_fn):
    """Verlauf-Zeilen (url, title, last_visit_raw, visit_count) -> hist dict keyed by norm(name).

    Gemeinsam fuer Firefox und Chromium — identische Manga-Erkennung (BLACKLIST/CH/MPATH/
    series_from); nur die Roh-Zeit wird ueber `time_fn` in Unix-Sekunden gewandelt.
    Pro Serie gewinnt das HOECHSTE (= aktuell gelesene) Kapitel; bei gleichem Kapitel die
    meistbesuchte Reader-Seite (visit_count), erst dann der spaetere Besuch. So zeigt 'url'
    auf deinen Lese-Link der meistgenutzten Scanlation, und 'lv' = Besuch deines hoechsten
    Kapitels -> Re-Lesen alter Kapitel resettet die Aktualitaet nicht (nur Fortschritt zaehlt).
    """
    agg = {}    # k -> {'name':..., 'readers':[{host,url,chap,lv,visits}, ...]}
    known = known_readers()
    for u, t, lv, vc in rows:
        h = host(u)
        if not h or BLACKLIST.search(h):
            continue
        # Manga-Signal: (a) "Chapter" im Titel, (b) Reader-Pfad + Kapitelnummer, ODER
        # (c) BEKANNTE Reader-Domain + Kapitelnummer (faengt Seiten mit untypischem Pfad).
        if not (CH.search(t or '') or (MPATH.search(u or '') and URLCH.search(u or '')) or
                (h.lower() in known and URLCH.search(u or ''))):
            continue
        name, chap = series_from(u, t)
        if not name or chap is None:
            continue
        k = norm(name)
        if not k or len(k) < 2:
            continue
        e = agg.get(k)
        if e is None:
            e = agg[k] = {'name': name, 'readers': []}
        upsert_reader(e['readers'], h, u, chap, time_fn(lv), vc or 0)
    return {k: _entry_from_readers(e['name'], e['readers'], status='Gelesen') for k, e in agg.items()}


def upsert_reader(readers, h, url, chap, lv, visits):
    """Eine Quelle je Host in der readers-Liste pflegen: hoechstes Kapitel je Host behalten,
    Besuche aufsummieren (so kennen wir pro Serie ALLE deine Lese-Seiten als direkte Links)."""
    for r in readers:
        if r['host'] == h:
            r['visits'] += visits
            if (chap or 0) > (r['chap'] or 0) or ((chap or 0) == (r['chap'] or 0) and lv > r['lv']):
                r['chap'], r['url'], r['lv'] = chap, url, lv
            return
    readers.append({'host': h, 'url': url, 'chap': chap, 'lv': lv, 'visits': visits})


def merge_readers(into, more):
    """readers-Listen vereinigen (ueber Browser/Dubletten hinweg)."""
    for r in more or []:
        upsert_reader(into, r['host'], r['url'], r.get('chap'), r.get('lv', 0), r.get('visits', 0))


def _entry_from_readers(name, readers, status):
    """Primaer-Felder (url/site/chap/lv) aus der readers-Liste ableiten: dein aktuelles Kapitel
    (hoechstes), bei Gleichstand die meistbesuchte Seite. 'readers' bleibt fuer das Routing erhalten."""
    best = max(readers, key=lambda r: (r['chap'] or 0, r['visits'], r['lv']))
    return {'name': name, 'status': status, 'chap': max((r['chap'] or 0) for r in readers),
            'lv': best['lv'], 'site': best['host'], 'url': best['url'],
            'visits': best['visits'], 'readers': readers}


def _marks_map(folder_kids):
    """Lesezeichen-Ordner -> marks dict keyed by norm(name) (Status aus Ordnername).

    `folder_kids` = iterierbar von (status, [(titel, url), ...]) — je Manga-Ordner seine
    (rekursiven) Lesezeichen. Gemeinsam fuer Firefox und Chromium. Erste Serie gewinnt
    (k in marks), geblacklistete Hosts und GARB-Namen fliegen raus.
    """
    marks = {}
    for status, pairs in folder_kids:
        for ttl, url in pairs:
            if not url or (host(url) and BLACKLIST.search(host(url))):
                continue
            name, chap = series_from(url, ttl)
            if not name or GARB.search(name):
                continue
            k = norm(name)
            if not k or len(k) < 2 or k in marks:
                continue
            marks[k] = {'name': name, 'status': status, 'chap': chap, 'site': host(url), 'lv': 0,
                        'url': url, 'visits': 0,
                        'readers': [{'host': host(url), 'url': url, 'chap': chap, 'lv': 0, 'visits': 0}]}
    return marks


def _merge_hist_marks(hist, marks):
    """Lesezeichen (marks) zuerst, dann Verlauf (hist) einfalten -> items dict.

    Verlauf hebt das Kapitel eines gemerkten Eintrags an (nie darunter), setzt den
    letzten Besuch und faellt sonst als Status "Gelesen" neu hinein. Identisch zur
    bisherigen build()-Verschmelzung; in 3.5 Basis des Cross-Browser-Merges.
    """
    items = dict(marks)
    for k, h in hist.items():
        if k in items:
            e = items[k]
            merge_readers(e.setdefault('readers', []), h.get('readers'))
            if h['chap'] and (e['chap'] is None or h['chap'] >= e['chap']):
                e['chap'] = h['chap']; e['url'] = h['url']
            e['lv'] = h['lv']
            if not e['site']:
                e['site'] = h['site']
            e['visits'] = max(e.get('visits', 0), h.get('visits', 0))
        else:
            items[k] = dict(h)
    return items


# ---------------- Firefox / Waterfox ----------------

def find_firefox_places(appdata=None):
    """Neueste places.sqlite in den Firefox-Profilen finden (default-release bevorzugt).

    `appdata` (Windows-Basis) erzwingt den klassischen Windows-Pfad (Tests/expliziter Pfad);
    sonst werden die OS-abhaengigen Firefox-Wurzeln (Win/macOS/Linux) verwendet."""
    if appdata is not None:
        roots = [os.path.join(appdata, "Mozilla", "Firefox", "Profiles")]
    else:
        roots = [r for _n, k, r in _browser_roots(os.environ) if k == "firefox"]
    c = [p for root in roots
         for p in glob.glob(os.path.join(root, "*", "places.sqlite")) if os.path.isfile(p)]
    if not c:
        return None
    rel = [p for p in c if "default-release" in p.lower()]
    return max(rel or c, key=os.path.getmtime)


def _ff_kids(cur, fid):
    """Alle Lesezeichen (rekursiv) unter Ordner fid -> Liste (lesezeichen_titel, url)."""
    st, seen, res = [fid], set(), []
    while st:
        p = st.pop()
        for i, typ, title, fk in cur.execute(
                "select id,type,title,fk from moz_bookmarks where parent=?", (p,)).fetchall():
            if typ == 2 and i not in seen:
                seen.add(i); st.append(i)
            elif typ == 1 and fk:
                row = cur.execute("select url from moz_places where id=?", (fk,)).fetchone()
                if row:
                    res.append((title, row[0]))
    return res


def _firefox_marks(cur):
    """Firefox-Lesezeichen-Ordner -> marks dict (Manga-Ordner an ihrem Namen erkannt)."""
    fmap = {}
    for i, tt in cur.execute(
            "select id,title from moz_bookmarks where type=2 and title is not null"):
        status = folder_status(tt)
        if status:
            fmap[i] = status
    return _marks_map((status, _ff_kids(cur, fid)) for fid, status in fmap.items())


def _scan_firefox_cursor(cur):
    """Kern der Firefox-Erkennung: Verlauf + Lesezeichen-Ordner -> items dict."""
    hist = _history_map(
        cur.execute("select url,title,last_visit_date,visit_count from moz_places where title is not null"),
        firefox_time)
    return _merge_hist_marks(hist, _firefox_marks(cur))


def scan_firefox(places_path, tmp_name="places_copy.sqlite"):
    """places.sqlite read-only kopieren, oeffnen und scannen -> items dict."""
    tmp = copy_locked(places_path, tmp_name)
    con = open_immutable(tmp)
    try:
        return _scan_firefox_cursor(con.cursor())
    finally:
        con.close()


# ---------------- Chromium-Familie: History (SQLite) ----------------
# Chrome/Edge/Brave/Opera/Vivaldi teilen das History-Schema (Tabelle `urls`).
# Lesezeichen (Bookmarks-JSON) folgen in Schritt 3.3, der Cross-Browser-Merge in 3.5.

def scan_chromium_history(history_path, tmp_name="chromium_history_copy.sqlite"):
    """Chromium `History` read-only kopieren und den Verlauf scannen -> hist dict.

    Liefert dieselbe Struktur wie der Firefox-Verlauf (keyed by norm(name)); der Status
    ("Gelesen") bzw. die Verschmelzung mit Lesezeichen passiert erst im Merge (3.5).
    `tmp_name` erlaubt je Browser/Profil einen eigenen Temp-Namen (kein Ueberschreiben).
    """
    tmp = copy_locked(history_path, tmp_name)
    con = open_immutable(tmp)
    try:
        return _history_map(
            con.cursor().execute("select url,title,last_visit_time,visit_count from urls where title is not null"),
            chromium_time)
    finally:
        con.close()


# ---------------- Chromium-Familie: Bookmarks (JSON) ----------------
# Datei `Bookmarks` (kein Schloss) — JSON: roots -> {bookmark_bar, other, synced, ...}.
# Jeder Knoten hat "type": "folder" (mit "children" + "name") oder "url" (mit "name" + "url").

def _chromium_matching_folders(node, out):
    """DFS: sammelt (folder_node, status) fuer alle Ordner mit Manga-Status-Namen."""
    if not isinstance(node, dict):
        return
    if node.get("type") == "folder":
        status = folder_status(node.get("name"))
        if status:
            out.append((node, status))
        for child in node.get("children", []):
            _chromium_matching_folders(child, out)


def _chromium_urls_under(node, out):
    """Alle Lesezeichen (rekursiv) unter node -> Liste (name, url) (wie Firefox _ff_kids)."""
    if not isinstance(node, dict):
        return
    if node.get("type") == "url":
        if node.get("url"):
            out.append((node.get("name"), node.get("url")))
    elif node.get("type") == "folder":
        for child in node.get("children", []):
            _chromium_urls_under(child, out)


def scan_chromium_bookmarks(bookmarks_path):
    """Chromium `Bookmarks` (JSON) lesen -> marks dict (Status aus Ordnernamen)."""
    with open(bookmarks_path, encoding="utf-8") as f:
        data = json.load(f)
    folders = []
    for root in (data or {}).get("roots", {}).values():
        _chromium_matching_folders(root, folders)

    def _kids():
        for folder, status in folders:
            pairs = []
            _chromium_urls_under(folder, pairs)
            yield status, pairs

    return _marks_map(_kids())


# ---------------- Safari (macOS): History.db (SQLite) ----------------
# JB 09.07.2026 ('safari mit integrieren'): Titel haengen an den BESUCHEN (history_visits),
# URLs an den Items. Jeder Besuch wird einzeln eingespeist — _history_map aggregiert selbst
# (hoechstes Kapitel gewinnt, Besuche summieren sich). Lesezeichen (Bookmarks.plist) bewusst
# noch nicht — der Verlauf traegt den Lesestand. Hinweis: macOS verlangt fuer ~/Library/Safari
# Vollzugriff (TCC) — ohne ihn ueberspringt scan_all die Quelle still wie jede andere.

def scan_safari_history(history_path, tmp_name="safari_history_copy.sqlite"):
    """Safari `History.db` read-only kopieren und den Verlauf scannen -> hist dict
    (gleiche Struktur wie Firefox/Chromium, keyed by norm(name))."""
    tmp = copy_locked(history_path, tmp_name)
    con = open_immutable(tmp)
    try:
        rows = con.cursor().execute(
            "select i.url, v.title, v.visit_time, 1 "
            "from history_items i join history_visits v on v.history_item = i.id "
            "where v.title is not null")
        return _history_map(rows, safari_time)
    finally:
        con.close()


# ---------------- Browser-Discovery (generisch, beim Start pruefbar) ----------------
# Datengetriebene Registry: ein neuer Browser = eine neue Zeile. Bewusst NICHT auf einen
# Browser fixiert — die Standalone-App muss bei beliebigen Nutzern/Browsern laufen.
#   kind "firefox":  ein places.sqlite je Profil (Verlauf + Lesezeichen in einer DB).
#   kind "chromium": je Profil eine `History`-DB + eine `Bookmarks`-JSON.
#   env:  Umgebungsvariable des Basisordners ("APPDATA" = Roaming, "LOCALAPPDATA" = Local).
def _browser_roots(env):
    """Profil-Wurzeln der bekannten Browser fuer DIESES Betriebssystem (Windows/macOS/Linux).

    `env` erlaubt Tests, die Windows-Basis (APPDATA/LOCALAPPDATA) zu ueberschreiben. Rueckgabe:
    [(Anzeigename, kind, root), ...]; fehlende Ordner werden beim Discovery still uebersprungen.
    Damit liest die App auf JEDER Plattform die Lesezeichen ein (nicht nur Windows)."""
    home = os.path.expanduser("~")
    if sys.platform == "win32":
        roam, loc = env.get("APPDATA", ""), env.get("LOCALAPPDATA", "")
        return [
            ("Firefox",  "firefox",  os.path.join(roam, "Mozilla", "Firefox", "Profiles")),
            ("Waterfox", "firefox",  os.path.join(roam, "Waterfox", "Profiles")),
            ("Chrome",   "chromium", os.path.join(loc, "Google", "Chrome", "User Data")),
            ("Edge",     "chromium", os.path.join(loc, "Microsoft", "Edge", "User Data")),
            ("Brave",    "chromium", os.path.join(loc, "BraveSoftware", "Brave-Browser", "User Data")),
            ("Vivaldi",  "chromium", os.path.join(loc, "Vivaldi", "User Data")),
            ("Opera",    "chromium", os.path.join(roam, "Opera Software", "Opera Stable")),
            ("Opera GX", "chromium", os.path.join(roam, "Opera Software", "Opera GX Stable")),
        ]
    if sys.platform == "darwin":
        app = os.path.join(home, "Library", "Application Support")
        return [
            ("Firefox",  "firefox",  os.path.join(app, "Firefox", "Profiles")),
            ("Waterfox", "firefox",  os.path.join(app, "Waterfox", "Profiles")),
            ("Chrome",   "chromium", os.path.join(app, "Google", "Chrome")),
            ("Edge",     "chromium", os.path.join(app, "Microsoft Edge")),
            ("Brave",    "chromium", os.path.join(app, "BraveSoftware", "Brave-Browser")),
            ("Vivaldi",  "chromium", os.path.join(app, "Vivaldi")),
            ("Chromium", "chromium", os.path.join(app, "Chromium")),
            ("Safari",   "safari",   os.path.join(home, "Library", "Safari")),
        ]
    # Linux / andere Unixe
    cfg = os.path.join(home, ".config")
    return [
        ("Firefox",  "firefox",  os.path.join(home, ".mozilla", "firefox")),
        ("Waterfox", "firefox",  os.path.join(home, ".waterfox")),
        ("Chrome",   "chromium", os.path.join(cfg, "google-chrome")),
        ("Chromium", "chromium", os.path.join(cfg, "chromium")),
        ("Edge",     "chromium", os.path.join(cfg, "microsoft-edge")),
        ("Brave",    "chromium", os.path.join(cfg, "BraveSoftware", "Brave-Browser")),
        ("Vivaldi",  "chromium", os.path.join(cfg, "vivaldi")),
        ("Opera",    "chromium", os.path.join(cfg, "opera")),
    ]

# Chromium-Profilordner heissen "Default" oder "Profile N"; Opera legt die Dateien direkt
# in den Root. System-/Gast-Profile (z.B. "System Profile") werden bewusst ignoriert.
_CHROMIUM_PROFILE = re.compile(r"(Default|Profile \d+)$")


def _chromium_profiles(root):
    """Profilordner unter einem Chromium-User-Data-Root finden (inkl. Opera-Root-Layout)."""
    profiles = []
    if os.path.isfile(os.path.join(root, "History")) or os.path.isfile(os.path.join(root, "Bookmarks")):
        profiles.append(root)          # Opera & Co.: History/Bookmarks direkt im Root
    try:
        entries = sorted(os.listdir(root))
    except OSError:
        entries = []
    for name in entries:
        d = os.path.join(root, name)
        if os.path.isdir(d) and _CHROMIUM_PROFILE.match(name):
            profiles.append(d)
    return profiles


def discover_browsers(environ=None):
    """Alle vorhandenen Browser-Profile dieses PCs finden — generisch, ohne Browser-Annahme.

    Gibt eine Liste von Quellen-Dicts zurueck (fehlende Browser werden still uebersprungen):
      firefox:  {browser, profile, kind:"firefox",  places}
      chromium: {browser, profile, kind:"chromium", history, bookmarks}  (je None, wenn fehlend)
    Reines Auffinden, kein Lesen/Kopieren — fuer den Startup-Check und den Merge (3.5).
    """
    env = environ if environ is not None else os.environ
    sources = []
    for name, kind, root in _browser_roots(env):
        if not root:
            continue
        if kind == "firefox":
            for places in sorted(glob.glob(os.path.join(root, "*", "places.sqlite"))):
                if os.path.isfile(places):
                    sources.append({"browser": name,
                                    "profile": os.path.basename(os.path.dirname(places)),
                                    "kind": "firefox", "places": places})
        elif kind == "safari":
            hist = os.path.join(root, "History.db")
            if os.path.isfile(hist):
                sources.append({"browser": name, "profile": "Safari",
                                "kind": "safari", "history": hist})
        else:
            if not os.path.isdir(root):
                continue
            for prof in _chromium_profiles(root):
                hist = os.path.join(prof, "History")
                bm = os.path.join(prof, "Bookmarks")
                hist = hist if os.path.isfile(hist) else None
                bm = bm if os.path.isfile(bm) else None
                if hist or bm:
                    sources.append({"browser": name,
                                    "profile": os.path.basename(prof) or name,
                                    "kind": "chromium", "history": hist, "bookmarks": bm})
    return sources


# ---------------- Cross-Browser-Merge ("Fortschritt gewinnt") ----------------
# Dieselbe Serie kann in mehreren Browsern/Profilen vorkommen. Dedup ueber norm(name);
# bei Konflikten gewinnt der groessere Fortschritt (hoechstes Kapitel, dann spaetester
# Besuch), der User-Status nach Prioritaet. (JB-Entscheidung 2026-06-28.)
STATUS_RANK = {"Am Lesen": 3, "Unsicher": 2, "Fertig": 1, "Gelesen": 0}


def _more_progress(cur, new):
    """True, wenn `new` mehr Fortschritt zeigt als `cur` (hoeheres Kapitel; sonst spaeterer Besuch)."""
    ca = cur['chap'] if cur['chap'] is not None else -1
    cb = new['chap'] if new['chap'] is not None else -1
    if cb != ca:
        return cb > ca
    return (new['lv'] or 0) > (cur['lv'] or 0)


def merge_items(into, more):
    """`more` (items dict eines Browsers) in `into` einfalten -> Dedup nach norm(name)-Key.

    Status = hoechste Prioritaet (Am Lesen>Unsicher>Fertig>Gelesen). Kapitel/URL/Site
    folgen dem groesseren Fortschritt; `lv` = spaetester Besuch ueber alle Quellen.
    Bei nur einer Quelle ist das Ergebnis wertgleich zu dieser Quelle (kein Verhaltensbruch).
    """
    for k, e in more.items():
        cur = into.get(k)
        if cur is None:
            into[k] = dict(e)
            continue
        if STATUS_RANK.get(e['status'], 0) > STATUS_RANK.get(cur['status'], 0):
            cur['status'] = e['status']
        merge_readers(cur.setdefault('readers', []), e.get('readers'))
        if _more_progress(cur, e):
            cur['chap'] = e['chap']; cur['url'] = e['url']
            if e.get('site'):
                cur['site'] = e['site']
        cur['lv'] = max(cur['lv'] or 0, e['lv'] or 0)
        if not cur.get('site'):
            cur['site'] = e.get('site', '')
    return into


def _tmp_tag(src):
    """Dateisystem-sicherer Temp-Praefix je Browser/Profil (kein Kopie-Namensclash)."""
    return re.sub(r'[^A-Za-z0-9]+', '_', f"{src.get('browser', 'x')}_{src.get('profile', 'x')}")


def scan_source(src):
    """Eine Discovery-Quelle (siehe discover_browsers) read-only scannen -> items dict."""
    if src["kind"] == "firefox":
        return scan_firefox(src["places"], tmp_name=f"ff_{_tmp_tag(src)}_places.sqlite")
    if src["kind"] == "safari":
        return scan_safari_history(src["history"], tmp_name=f"sf_{_tmp_tag(src)}_History.sqlite")
    hist = (scan_chromium_history(src["history"], tmp_name=f"cr_{_tmp_tag(src)}_History.sqlite")
            if src.get("history") else {})
    marks = scan_chromium_bookmarks(src["bookmarks"]) if src.get("bookmarks") else {}
    return _merge_hist_marks(hist, marks)


def scan_all(sources=None, environ=None):
    """Alle gefundenen Browser scannen und cross-browser zusammenfuehren -> items dict.

    Ein Fehler in einer einzelnen Quelle ueberspringt nur diese (nicht-destruktiv,
    der Lauf laeuft weiter); nichts wird geloescht oder veraendert (read-only).
    """
    sources = discover_browsers(environ) if sources is None else sources
    merged = {}
    for src in sources:
        try:
            merge_items(merged, scan_source(src))
        except Exception as e:   # eine kaputte/gesperrte Quelle darf den Lauf nicht killen
            print(f"[scan] {src.get('browser')} [{src.get('profile')}] uebersprungen: "
                  f"{type(e).__name__}: {e}", file=sys.stderr)
    merge_items(merged, imported_items())   # Listen-Import (MAL/AniList) als zusaetzliche Quelle
    return merged


def imported_items():
    """Serien aus einem Listen-IMPORT (tools/import_mal.py -> data/imported_series.json): Titel, die
    in keinem Browser-Verlauf stehen (Migration von MyAnimeList/AniList oder von Freunden), fliessen
    als normale items in die Pipeline — Match/Anreicherung/Render exakt wie gescannte Serien.
    Fehlt die Datei -> {} (kein Effekt). Best-effort, nie eine Exception."""
    p = IMPORTED_PATH
    try:
        raw = json.load(open(p, encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    out = {}
    for k, e in (raw or {}).items():
        if isinstance(e, dict) and e.get("name"):
            out[k] = {"name": e["name"], "status": e.get("status") or "Gelesen",
                      "chap": e.get("chap"), "site": "", "lv": e.get("lv") or 0,
                      "url": "", "readers": []}
    return out
