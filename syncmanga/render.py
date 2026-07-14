# -*- coding: utf-8 -*-
"""
HTML-Ausgabe der Manga-Leseliste.

Aus SyncEngine/manga_update.py herausgelöst (Phase 2.3). Verhalten 1:1 (byte-identische
Ausgabe gegen die vorherige render()-Funktion, per Golden-Vergleich verifiziert). CSS und JS
liegen jetzt in templates/list.css bzw. templates/list.js (statt inline mit {{ }}-Escapes),
damit sie z.B. per `node --check` geprueft werden koennen und der HTML-Code lesbar bleibt.

Neu als eigenständige, testbare Funktionen extrahiert:
  - chapter_label(ch): Kapitel-Anzeige ('?' bei None, ganze Zahl ohne Nachkomma, sonst float).
  - next_and_unread(chap, latest): naechstes Kapitel, offene Kapitel, bereinigtes latest.
"""
import os
import re
import json
import html
import time
import urllib.parse
from datetime import datetime, timezone
from collections import Counter

from .parse import norm, is_dynamic, host
from . import config as _config           # Modul-Zugriff: PAUSED_READERS wird zur Laufzeit gesetzt
from .config import NAMELEN, UNSAFE_SITES, is_dead_reader, is_paused_reader
from .readerlink import is_chapter_url
from .catalog import cover_url
from . import i18n
from . import enrich as _enrich                  # recs_load (Empfehlungen, frueher recs.py)
from . import health as srcstatus                # Quellen-Status (frueher srcstatus.py)

# Quellen-Status-Panel (JBs Anforderung): Farbe je Quelle, damit JB SIEHT, was klemmt.
_STATUS_COLOR = {"ok": "#3a7d3a", "degraded": "#c9952b", "down": "#c0392b"}
SRC_MAXLEN = 22        # Quelle-Spalte: lange Reader-Domains kuerzen (voller Name im Tooltip)

# Startseiten der Datenquellen -> Klick auf Punkt+Name oeffnet die Quelle im neuen Tab (JB-Wunsch).
_SOURCE_URL = {"mangabaka": "https://mangabaka.org", "anilist": "https://anilist.co",
               "mangaupdates": "https://www.mangaupdates.com", "kitsu": "https://kitsu.app",
               "myanimelist": "https://myanimelist.net", "jikan": "https://myanimelist.net",
               "mangadex": "https://mangadex.org"}


# Huebsche Anzeigenamen — intern werden die Quellen klein/roh gefuehrt (mangabaka, myanimelist,
# fallback ...). Fuers Panel schoen schreiben, ohne die Logik-Keys zu aendern.
_SOURCE_LABEL = {"mangabaka": "MangaBaka", "anilist": "AniList", "mangaupdates": "MangaUpdates",
                 "kitsu": "Kitsu", "myanimelist": "MyAnimeList", "jikan": "MyAnimeList",
                 "mangadex": "MangaDex", "fallback": "Reserve-Suche"}


def _src_key(name):
    return (name or "").lower().replace(" ", "").replace("-", "")


def _source_url(name):
    """Homepage einer Datenquelle fuer den Klick; None, wenn unbekannt (dann nur Anzeige)."""
    return _SOURCE_URL.get(_src_key(name))


def _source_label(name):
    """Huebscher Anzeigename der Datenquelle (Fallback: Rohname)."""
    return _SOURCE_LABEL.get(_src_key(name), name)


def _chip(url, color, label, tip, symbol="●", extra=""):
    """Ein Ampel-Chip: farbiger Punkt + Name. Mit URL -> klickbarer Link (neuer Tab,
    rel=noopener); der Tooltip nennt bei Problemen die Ursache, sonst 'oeffnen'. Ohne URL
    bleibt es reine Anzeige. Alles wird HTML-escaped.
    symbol: '●' normal, '⏸' fuer PAUSIERTE Seiten (JB Runde 37) — in der Ampelfarbe.
    extra: fertige Zusatz-Attribute (z.B. data-rh fuer den Client-Pause-Schalter)."""
    inner = f'<span class=dot style="color:{color}">{symbol}</span> {html.escape(label)}'
    t = f' title="{html.escape(tip)}"' if tip else ""
    if url:
        return (f'<a class=srcchip{extra} href="{html.escape(url)}" target="_blank" '
                f'rel="noopener noreferrer"{t}>{inner}</a>')
    return f'<span class=srcchip{extra}{t}>{inner}</span>'


def _pl(label):
    """Pill-Label 'ICON Text' -> Icon + <span class=pl>Text</span>: auf Mobile blendet CSS den
    Text aus, nur das Symbol bleibt (JB 09.07.2026: 'Aktion sollte … als Symbol anzeigen').
    Labels ohne Icon-Praefix bleiben unveraendert (dann gibt es mobil nichts abzukuerzen)."""
    icon, sep, rest = (label or "").partition(" ")
    if not sep or not rest or icon.isalnum():
        return html.escape(label or "")
    return f'{html.escape(icon)}<span class=pl> {html.escape(rest)}</span>'


def _short(s):
    """Lange Quellen-Domain auf SRC_MAXLEN kuerzen (… am Ende)."""
    s = s or ""
    return s if len(s) <= SRC_MAXLEN else s[:SRC_MAXLEN - 1] + "…"

# User-Fortschritt (Leser): wenige, klare Werte, automatisch abgeleitet (JB-Entscheidung).
PAUSE_DAYS = 60        # ab so vielen Tagen ohne Besuch gilt eine offene Serie als "Pausiert"
OPEN_FRESH_DAYS = 365  # nur bis hier ist dein gespeicherter Lese-Link "frisch" genug fuer "oeffnen"
# user_progress liefert stabile KEYS (i18n-uebersetzt erst bei der Anzeige), zugleich CSS-Klasse.
PROGRESS_CLASS = {"prog_reading": "r", "prog_caught": "f", "prog_finished": "fin",
                  "prog_paused": "u", "prog_backlog": ""}
# Tooltip je User-Status (CSS-Klasse -> i18n-Key) — erklaert die Farbe beim Hovern (JB-Wunsch).
STATUS_TIP = {"r": "st_tip_reading", "u": "st_tip_paused", "ulong": "st_tip_paused_long",
              "f": "st_tip_caught", "fin": "st_tip_finished", "": "st_tip_backlog"}
# User-Fortschritt -> MAL-Status (fuer den Listen-Export 3b; MAL/AniList-Import-Vokabular).
MAL_STATUS = {"prog_reading": "Reading", "prog_caught": "Reading", "prog_finished": "Completed",
              "prog_paused": "On-Hold", "prog_backlog": "Plan to Read"}

# Label fuer fehlende Autor/Status-Angaben. Per Spec §2.4 die ABSOLUTE Ausnahme (meist ein
# Matching-Fehler, nicht fehlende Daten) — wird in 4.4 in den "Braucht Hilfe"-Flow gefuehrt.
UNKNOWN = "unbekannt"

# Typ/Medium aus dem Herkunftsland (Originalsprache der Quelle): Japan=Manga, Korea=Manhwa,
# China/Taiwan=Manhua, USA=Comic. Webtoon ist ein FORMAT (orthogonal) -> eigene is_dynamic-Erkennung.
MEDIUM_BY_COUNTRY = {"Japan": "Manga", "Korea": "Manhwa", "China": "Manhua",
                     "Taiwan": "Manhua", "USA": "Comic"}
# Reihenfolge der Typ-Filter oben (Webtoon filtert ueber data-dyn, nicht ueber data-medium).
MEDIA_FILTER = ("Manga", "Manhwa", "Manhua", "Webtoon", "Comic")


def medium(country):
    """Serien-Typ aus dem Herkunftsland ableiten (Manga/Manhwa/Manhua/Comic) oder '' (unbekannt)."""
    return MEDIUM_BY_COUNTRY.get(country or "", "")


def is_unresolved(e):
    """Genuin ungeloest (Spec §2.4): WURDE angereichert, hat aber kein Autor UND kein md_id.

    Wichtig: nur tatsaechlich angereicherte Eintraege (`enriched`) zaehlen — noch ausstehende
    (Cap pro Lauf / Kaltstart) sind NICHT "braucht Hilfe", sondern nur noch nicht dran. Ein
    echtes Ungeloest entsteht fast immer durch einen Matching-Fehler (schlechter Name aus
    URL/Titel) und gehoert in den "Braucht Hilfe"-Flow. Reine Funktion, ohne Netz/Seiteneffekt."""
    return bool(e.get('enriched')) and not (e.get('author') or '').strip() and not e.get('md_id')


_DONE_WORDS = ("abgeschloss", "completed", "finished", "beendet", "ended")


def user_progress(chap, latest, lv, now_ts, pause_days=PAUSE_DAYS, pub_status=""):
    """User-Fortschritt ableiten -> Abgeschlossen / Lese gerade / Aufgeholt / Pausiert / Backlog.

    - Backlog:    gemerkt, aber (noch) ungelesen (kein gelesenes Kapitel).
    - Aufgeholt:  kein neueres Kapitel offen (beim neuesten / keins bekannt).
    - Pausiert:   es gibt offene Kapitel, aber zuletzt vor > pause_days Tagen gelesen.
                  UNBEKANNTER letzter Besuch (lv fehlt) zaehlt ebenfalls als > pause_days
                  (sonst wuerden die vielen Lesezeichen-only-Serien faelschlich "Lese gerade").
    - Lese gerade: offene Kapitel und nachweislich kuerzlich gelesen.
    `latest` ist bereits bereinigt (next_and_unread verwirft latest <= chap).
    Rueckgabe = stabiler i18n-Key (prog_*), nicht der angezeigte Text."""
    read = chap or 0
    if not read:
        return "prog_backlog"
    if not (latest and latest > read):
        # alles Verfuegbare gelesen -> bei abgeschlossenem Manga "Abgeschlossen", sonst nur "Aufgeholt"
        done = any(w in (pub_status or "").lower() for w in _DONE_WORDS)
        return "prog_finished" if done else "prog_caught"
    recent = lv and (now_ts - lv) <= pause_days * 86400
    return "prog_reading" if recent else "prog_paused"

_TPL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")


def _load(name):
    with open(os.path.join(_TPL, name), encoding="utf-8") as f:
        return f.read().rstrip("\n")


def _minify_css(css):
    """CSS fuer die Auslieferung verkleinern (die QUELLE list.css bleibt lesbar+kommentiert).
    Konservativ & semantisch identisch: /* Kommentare */ raus, Whitespace-Laeufe zu EINEM Space
    (Nachfahren-/Kind-Kombinatoren bleiben so erhalten), dann Space um { } ; , entfernen.
    Bewusst NICHT um ':' (Pseudo-Selektoren) -> keine Selektor-Bedeutung geaendert."""
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
    css = re.sub(r'\s+', ' ', css)
    css = re.sub(r'\s*([{};,])\s*', r'\1', css)
    return css.strip()


def _minify_js(js):
    """JS fuer die Auslieferung verkleinern - KONSERVATIV & sicher (die QUELLE list.js bleibt
    lesbar+kommentiert): nur Leerzeilen und ganze //-Kommentarzeilen weg + Einrueckung strippen.
    KEIN Zeilen-Zusammenziehen (jede Anweisung behaelt ihr Zeilenende -> ASI-sicher), keine
    Token-Aenderung -> Verhalten bleibt 1:1. (Kein '//' steht im Code selbst, nur in Kommentaren.)"""
    return "\n".join(t for ln in js.split("\n")
                     if (t := ln.strip()) and not t.startswith("//"))


CSS = _minify_css(_load("list.css"))
JS = _minify_js(_load("list.js"))


def chapter_label(ch):
    """Kapitel als String: None -> '?', ganze Zahl ohne Nachkomma, sonst float-String."""
    if ch is None:
        return '?'
    return str(int(ch)) if ch == int(ch) else str(ch)


def next_and_unread(chap, latest):
    """Ziel-Kapitel (= dein AKTUELLES, JB: man hoert mitten im Kapitel auf; '' ohne chap),
    offene Kapitel und bereinigtes latest. Liegt 'latest' <= gelesenem Kapitel (Quelle hinkt
    hinterher), wird latest verworfen -> kein falsches 'neu' unter dem Gelesenen."""
    nxt = int(chap) if chap else ''
    if latest and chap and latest <= chap:
        latest = None
    unread = max(0, int(round((latest or 0) - (chap or 0)))) if latest else 0
    return nxt, unread, latest


def status_panel(s):
    """Quellen-Status-Panel aus srcstatus.snapshot() -> HTML (leer, wenn kein Status vorliegt).

    Zeigt je externer Quelle einen farbigen Punkt (gruen ok / gelb degraded / rot down) und
    bei Problemen die letzte Fehlermeldung als Tooltip -> sofort sichtbar, was klemmt."""
    snap = srcstatus.snapshot()
    if not snap:
        return ""
    hint = s.get("src_open_hint", "im neuen Tab öffnen")
    chips = []
    for name in sorted(snap):
        st = snap[name]
        col = _STATUS_COLOR.get(st.get("status"), "#888")
        label = _source_label(name)
        # Tooltip: bei Problem die Fehlerursache (wie bisher), sonst ein Hinweis aufs Oeffnen.
        tip = st.get("error") or f"{label} — {hint}"
        # Pausiert (JB Runde 37): ⏸ statt Punkt, in der Ampelfarbe — gilt auch fuer Datenquellen.
        dom = host(_source_url(name) or "")
        paused = is_paused_reader(dom)
        chips.append(_chip(_source_url(name), col, label,
                           s.get("paused_tip", tip) if paused else tip,
                           "⏸" if paused else "●", f' data-rh="{html.escape(dom)}"'))
    label = s.get("source_status_label", "Quellen")
    # Leerzeichen zwischen den Chips = Umbruch-Gelegenheit (Chips selbst sind nowrap) —
    # ohne sie war die Zeile UNBRECHBAR und zwang Mobile in >1000px Breite (JB 08.07.2026).
    return f'<div class=statusrow>{label}: {" ".join(chips)}</div>'


_READER_COLOR = {"ok": "#3a7d3a", "cloudflare": "#c9952b", "no-images": "#c9952b",
                 "maintenance": "#d2691e", "down": "#c0392b"}
_READER_DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "reader_status.json")

# Kern-Lese-Seiten fuer die kombinierte +Alt-Google-Suche (falls reader_status.json fehlt/duenn).
_CORE_SITES = ["comix.to", "mangadex.org", "weebcentral.com", "mangaread.org", "mangafire.to",
               "bato.to", "mgeko.cc"]


def search_sites():
    """Domains der GELISTETEN Lese-Seiten (reader_status.json) + Kern -> fuer EINE Google-Suche
    ueber genau diese Seiten (site:-Filter). JB-Wunsch: statt jede Seite einzeln als (403-anfaellige)
    Einzel-Suche zu listen, eine kombinierte Suche. Die Suche selbst 403t nie; sie fuehrt gezielt auf
    die richtigen Reader-Treffer. MangaFire bleibt bewusst dabei (JB nannte es ausdruecklich)."""
    try:
        with open(_READER_DATA, encoding="utf-8") as f:
            doms = [h for h in (json.load(f).get("readers") or {}) if h]
    except Exception:
        doms = []
    return list(dict.fromkeys(doms + _CORE_SITES))[:10]


def reader_panel(s):
    """Reader-Ampel aus data/reader_status.json -> HTML (leer, wenn keine Daten).

    Zeigt je geteilter Lese-Seite einen farbigen Punkt: gruen = funktioniert, gelb = Cloudflare
    (im Browser nutzbar) / keine Bilder, rot = down. JBs Wunsch: sofort sehen, welche Reader gehen."""
    import json as _json
    try:
        with open(_READER_DATA, encoding="utf-8") as f:
            data = _json.load(f)
    except Exception:
        return ""
    readers = data.get("readers") or {}
    if not readers:
        return ""
    hint = s.get("src_open_hint", "im neuen Tab öffnen")
    chips = []
    # Reihenfolge = Serienzahl in DEINER Liste (JB 08.07.2026: 'immer die Seiten mit den meisten
    # Serien'), erst dann alphabetisch. 'n' kommt aus readers.refresh_status/ampel_targets.
    for hostn in sorted(readers, key=lambda h: (-(readers[h].get("n") or 0),
                                                readers[h].get("name", h).lower())):
        r = readers[hostn]
        col = _READER_COLOR.get(r.get("status"), "#888")
        name = r.get("name", hostn)
        cnt = f' · {r["n"]} {s.get("ampel_series", "Serien")}' if r.get("n") else ""
        # Tooltip: bei anderer Ampelfarbe als gruen die Ursache (note), bei gruen ein Oeffnen-Hinweis;
        # dahinter immer die Serienzahl dieser Seite in der Liste.
        tip = (r.get("note", "") if r.get("status") != "ok" else f"{name} — {hint}") + cnt
        url = f"https://{hostn}" if hostn else None
        # Pausiert (JB Runde 37, MangaFire-Umbau): ⏸ in der Ampelfarbe statt Punkt.
        paused = is_paused_reader(hostn)
        chips.append(_chip(url, col, name, s.get("paused_tip", tip) if paused else tip,
                           "⏸" if paused else "●", f' data-rh="{html.escape(hostn)}"'))
    label = s.get("reader_status_label", "Lese-Seiten")
    return f'<div class=statusrow>{label}: {" ".join(chips)}</div>'  # Leerzeichen = Umbruch (s.o.)


def _reader_legend(s):
    """Gemeinsame Ampel-Legende — gilt fuer Datenquellen UND Lese-Seiten (eine reicht)."""
    return (f'<div class=rlegend>'
            f'<span><span style="color:{_READER_COLOR["ok"]}">●</span> {html.escape(s["legend_ok"])}</span>'
            f'<span><span style="color:{_READER_COLOR["cloudflare"]}">●</span> {html.escape(s["legend_browser"])}</span>'
            f'<span><span style="color:{_READER_COLOR["maintenance"]}">●</span> {html.escape(s["legend_maint"])}</span>'
            f'<span><span style="color:{_READER_COLOR["down"]}">●</span> {html.escape(s["legend_down"])}</span></div>')


def status_block(s):
    """Datenquellen- + Lese-Seiten-Zeile eng untereinander, EINE Ampel-Legende rechts mittig."""
    rows = status_panel(s) + reader_panel(s)
    if not rows:
        return ""
    return f'<div class=statusbar><div class=statusrows>{rows}</div>{_reader_legend(s)}</div>'


def _type_label(t):
    """Typ huebsch: bekannte Akronyme (OEL) gross, sonst Title-Case."""
    t = (t or "").strip()
    return t.upper() if t.lower() == "oel" else t.capitalize()


def stats_panel(rows, pcnt, s):
    """Lese-Statistik/Insights als einklappbares Panel — aus den vorhandenen Cache-Feldern.

    Zeigt Serienzahl, Status-Verteilung, Ø-Bewertung, gelesene Kapitel, Land-/Typ-Verteilung,
    Top-Serie und 18+. Reine Anzeige (kein Netz), einklappbar -> stoert die Liste nicht."""
    n = len(rows)
    if not n:
        return ""
    rated = [e["rating"] for e in rows if e.get("rating")]
    avg = sum(rated) / len(rated) if rated else 0
    chaps = sum(min(int(e["chap"]), 5000) for e in rows if e.get("chap"))   # Ausreißer kappen
    by_flag = Counter(e.get("flag") for e in rows if e.get("flag"))
    by_type = Counter(_type_label(e.get("type")) for e in rows if e.get("type"))
    adult = sum(1 for e in rows if e.get("adult_kind"))
    top = max(rows, key=lambda e: e.get("rating") or 0, default=None)
    # (Text, Tooltip) -> jede Kachel erklaert sich beim Hovern (JBs Wunsch)
    tiles = [(f'<b>{n}</b> {s["series"]}', s["stats_tip_count"]),
             (f'📖 {pcnt.get("prog_reading", 0)} · 🏁 {pcnt.get("prog_finished", 0)} · '
              f'✅ {pcnt.get("prog_caught", 0)} · ⏸ {pcnt.get("prog_paused", 0)} · '
              f'📋 {pcnt.get("prog_backlog", 0)}', s["stats_tip_status"])]
    if avg:
        tiles.append((f'Ø ⭐ {avg:.1f}', s["stats_tip_rating"]))
    tiles.append((f'📚 {chaps} {s["stats_chapters"]}', s["stats_tip_chapters"]))
    if by_flag:
        tiles.append((" · ".join(f"{fl} {c}" for fl, c in by_flag.most_common(6)), s["stats_tip_country"]))
    if by_type:
        tiles.append((" · ".join(f"{t} {c}" for t, c in by_type.most_common(5)), s["stats_tip_type"]))
    if adult:
        tiles.append((f'🔞 {adult}', s["stats_tip_adult"]))
    if top and top.get("rating"):
        tiles.append((f'🏆 {html.escape(top["name"][:34])} ({top["rating"]})', s["stats_tip_top"]))
    # 🛟 Absicherung (JB 09.07.2026, 'nicht aufdringlich'): wie viele Serien haetten beim
    # Ausfall ihrer Primaer-Seite eine Reserve auf einem ANDEREN Host? Kein Netz, nur Cache.
    linked = [e for e in rows if e.get("read_url") or e.get("read_urls")]
    if linked:
        def _hosts(e):
            return {host(u) or "" for u in
                    [e.get("read_url") or ""] + [u for u, _nm in (e.get("read_urls") or [])] if u}
        mono = sum(1 for e in linked if len(_hosts(e)) < 2)
        pct = round(100 * (len(linked) - mono) / len(linked))
        tiles.append((f'🛟 {pct}% · {mono} {s["stats_mono"]}', s["stats_tip_cover"]))
    body = "".join(f'<span class=stile title="{html.escape(tip)}">{t}</span>' for t, tip in tiles)
    return (f'<details class=stats><summary class="pill alt" title="{html.escape(s["stats_toggle"])}">📊 {s["stats_title"]}</summary>'
            f'<div class=pdrop><div class=statgrid>{body}</div></div></details>')


def recommendations_panel(rows, s):
    """EXTERNE Empfehlungen (JB-Wunsch): AniList-Top-Titel zum Genre-Profil ALLER Serien der Liste,
    als Links auf die externe Seite; nichts, was schon in der Liste steht. Liest NUR den vom
    Update-Lauf gefuellten Cache (recs_refresh) — kein Netz beim Rendern."""
    meta, items = _enrich.recs_load(rows=rows)
    if not items:
        return ""
    def _rchip(r):
        # 📖 = verifizierter Kapitel-1-Link (JB Runde 38, Feature 4) NEBEN dem DB-Verweis;
        # zwei Anker nebeneinander (nie verschachtelt), Wrapper haelt sie zusammen.
        rd = (f'<a class=rgo href="{html.escape(r["read"])}" target=_blank rel=noopener '
              f'title="{html.escape(s["recs_read_tip"])}">📖</a>' if r.get("read") else '')
        return (f'<span class=rwrap><a class=stile href="{html.escape(r["url"])}" target=_blank rel=noopener '
                f'title="{html.escape(", ".join(r.get("genres") or []))}">'
                f'{html.escape(str(r["title"])[:38])} <b>⭐{r.get("score") or "?"}</b></a>{rd}</span>')
    chips = "".join(_rchip(r) for r in items[:12])
    def _slim(r):
        return {"t": str(r["title"])[:38], "u": r["url"], "s": r.get("score") or "?",
                "g": ", ".join(r.get("genres") or []), "r": r.get("read") or ""}
    # Pool (bis 30) einbetten -> der ↻-Knopf mischt clientseitig neue 12 heraus (JB-Wunsch), kein Netz.
    pool = json.dumps([_slim(r) for r in items[:30]], ensure_ascii=False)
    # v2 (JB 10.07.2026): je-Genre-Pools + Genre-Chips (an/★Prio) — der Client kombiniert live.
    by_genre = meta.get("by_genre") or {}
    bg = json.dumps({g: [_slim(r) for r in rs] for g, rs in by_genre.items()}, ensure_ascii=False)
    top = json.dumps(meta.get("genres") or [], ensure_ascii=False)
    order = [g for g in (meta.get("order") or sorted(by_genre)) if g in by_genre]
    gchips = "".join(f'<button type=button class=rchip data-rg="{html.escape(g)}" '
                     f'onclick="recsCycle(this)" title="{html.escape(s["recs_genre_tip"])}">'
                     f'{html.escape(g)}</button>' for g in order)
    gbar = f'<div class=rchips>{gchips}</div>' if gchips else ''
    return (f'<details class=stats><summary class="pill alt" title="{html.escape(s["recs_toggle"])}">💡 {s["recs_title"]}</summary>'
            f'<div class=pdrop>'
            f'<div class="muted" style="margin:0 0 6px;font-size:12px">'
            f'{s["recs_hint"].format(g=", ".join(meta.get("genres") or []))} '
            f'<button class=btn onclick="shuffleRecs()" title="{html.escape(s["recs_shuffle_title"])}">{s["recs_shuffle"]}</button></div>'
            f'{gbar}'
            f'<div id=recsgrid class=statgrid>{chips}</div></div>'
            f'<script>var RECSPOOL={pool},RECSBG={bg},RECSTOP={top};</script></details>')


def _db_pill(e):
    """DB-Pille (Baka/AL) aus der md_id: mangabaka.org/<n> bzw. anilist.co/manga/<id>. Leer ohne ID."""
    mid = str(e.get('md_id') or '')
    if mid.startswith('mb:'):
        md, label = f'https://mangabaka.org/{mid[3:]}', 'Baka'
    elif mid.startswith('al:'):
        md, label = f'https://anilist.co/manga/{mid[3:]}', 'AL'
    else:
        return ''
    return (f'<a class="pill md" href="{html.escape(md)}" target=_blank '
            f'title="In der Datenbank ansehen">{label}</a>')


def _primary_action(e, s, now_ts, unsafe, g, uprog=None):
    """Primaerer Aktions-Link (anfangen/weiterlesen/beendet) + Quelle-Spalte -> (prim, srccell).

    Waehlt aus ALLEN gespeicherten Reader-Links den besten LEBENDEN mit dem hoechsten dort gelesenen
    Kapitel (direkt zum Kapitel, kein Suchen). Keine lebende eigene Quelle -> per 404 verifizierter
    readerlink; sonst Google-Suche als Ausweg. Ein kuratierter Override (`ov`) schlaegt das Bookmark."""
    recent = e['lv'] and (now_ts - e['lv']) < OPEN_FRESH_DAYS * 86400
    readers = e.get('readers') or ([{'host': host(e.get('url')), 'url': e.get('url'),
                                     'chap': e.get('chap'), 'visits': 0, 'lv': e.get('lv')}]
                                   if e.get('url') else [])
    direct = None
    if recent and not unsafe:
        alive = [r for r in readers if r.get('url')
                 and not is_dead_reader(r.get('host') or host(r.get('url')))
                 and not is_paused_reader(r.get('host') or host(r.get('url')))]
        if alive:
            direct = max(alive, key=lambda r: (r.get('chap') or 0, r.get('visits', 0), r.get('lv') or 0))
    if e.get('ov'):                          # kuratierter Override hat Vorrang vor dem Bookmark
        direct = None
    # Verifizierter Kapitel-Link; Reserve: erster read_urls-Eintrag, falls der Singular beim
    # Zwillings-Merge verloren ging (JB Runde 35, Million Lives -> Zeile fiel auf Google zurueck).
    # PAUSIERTE Reader (Wartung/Umbau, JB Runde 36: MangaFire zeigt 1-3 Tage nur Platzhalter)
    # werden NUR hier in der Anzeige uebersprungen -> erste lebende Reserve; der Cache bleibt
    # unangetastet, nach Aufheben der Pause gilt sofort wieder der urspruengliche Link.
    cand = ([(e.get('read_url') or '', e.get('read_site') or '')]
            + [tuple(x) for x in (e.get('read_urls') or [])])
    rl, rsite0 = next(((u, nm) for u, nm in cand if u and not is_paused_reader(host(u))),
                      ('', ''))
    # Kapitel schlaegt Serien-Seite (JB Runde 35, Farmer/Murim: der frische eigene Klick auf die
    # SERIEN-Root verdraengte den verifizierten Kapitel-Link). Nur bei bekanntem Lesestand —
    # bei '?' ist die Serien-Seite ausdruecklich gewollt (Runde 31).
    if (direct and rl and e.get('chap')
            and not is_chapter_url(direct.get('url') or '') and is_chapter_url(rl)):
        direct = None
    # Label-DREIKLANG (JB Runde 42): das Label beschreibt den ZUSTAND, nicht die URL —
    # '?' -> "anfangen", abgeschlossen+durch -> "beendet", sonst "weiterlesen" (beim
    # aktuellen Kapitel einsteigen). Ersetzt die alte URL-Token-Kosmetik ("oeffnen").
    def _label(_url=None):
        if not e.get('chap'):
            return s["start_reading"]
        if uprog == "prog_finished":
            return s["finished_label"]
        return s["continue"]

    if direct:
        dsite = direct.get('host') or host(direct.get('url')) or '–'
        link = html.escape(direct["url"])
        # Quelle einheitlich (JB: kursiv/grau war verwirrend); Herkunft steht im Tooltip.
        tip = dsite if (direct.get('chap') or 0) >= (e['chap'] or 0) else f"{dsite} — {s['source_stale_hint']}"
        return (f'<a class="pill go" href="{link}" target=_blank>{_pl(_label(direct["url"]))}</a>',
                f'<span title="{html.escape(tip)}">{html.escape(_short(dsite))}</span>')
    # Der verifizierte Link zaehlt auch, wenn JBs EIGENE Lese-Seite unsicher ist (mangahasu):
    # genau dann ist der sichere Kapitel-Link die beste Umleitung — nicht die Google-Suche
    # (JB Runde 35, Million Lives). Nur ein selbst unsicherer read_url bleibt tabu.
    if rl and not any(u in rl for u in UNSAFE_SITES):
        # keine lebende EIGENE Quelle -> verifizierter Reader-Kapitel-Link statt Suche
        rsite = rsite0 or host(rl) or '–'
        # "zuletzt von <Gruppe>" (JB Runde 39, Idee 4): die Scan-Gruppe aus der Comick-API
        # wandert in den Quelle-Tooltip — zeigt, wo neue Kapitel zuerst erscheinen.
        _grp = f' · {s["last_group_tip"].format(g=e["last_group"])}' if e.get('last_group') else ''
        return (f'<a class="pill go" href="{html.escape(rl)}" target=_blank>{_pl(_label(rl))}</a>',
                f'<span title="{html.escape(rsite)} — {html.escape(s["source_auto_hint"] + _grp)}">{html.escape(_short(rsite))}</span>')
    # nirgends ein Kapitel-Link -> Suche (Label bleibt zustandsbasiert; Quelle-Spalte
    # zeigt "Quelle unsicher", der Klick fuehrt zur eingegrenzten Suche)
    return (f'<a class="pill go" href="{g}" target=_blank>{_pl(_label())}</a>',
            f'<span style="color:#c66">{s["source_unsafe"]}</span>' if unsafe
            else f'<span class="unk" title="{html.escape(s["source_stale_hint"])}">{s["source_alt"]}</span>')


def _alt_cell(e, s, sites_q, nxt, full):
    """+Alt-Menue: EINE kombinierte Google-Suche ueber alle gelisteten Lese-Seiten (site:-Filter, nie
    403) + die GEPRUEFTEN Direktlinks (read_urls) einzeln. Keine 403-anfaelligen Einzel-Seiten-Suchen."""
    urls = e.get('read_urls') or []
    reserves = [(u, nm, '') for u, nm in urls[1:]]
    # Ist der Primaerlink gerade PAUSIERT (Reader-Wartung), zeigt die Aktion eine Reserve —
    # der pausierte Link wandert dann hierher ins Alt-Menue (bleibt fuer Menschen erreichbar).
    # data-pp markiert ihn als Ex-Primaerlink: hebt der Nutzer die Pause im ⏸-Menue auf,
    # macht applyPause() im JS genau diesen Link wieder zur Aktion.
    if urls and urls[0] and urls[0][0] and is_paused_reader(host(urls[0][0])):
        reserves.append((urls[0][0], urls[0][1], ' data-pp=1'))
    def _res_tip(u):
        # ✓-Kennzeichen (JB Runde 39, Idee 3): API-bestaetigte EN-Kapitel (MangaDex-Kapitel-
        # UUID) sind die verlaesslichsten Reserven -> eigener Tooltip. (comick raus, Runde 40:
        # Tracker ohne Reader.)
        if "mangadex.org/chapter/" in u:
            return s["alt_verified_en"]
        return s["alt_verified_tip"]
    # Jede Kandidaten-Quelle bekommt ein ✔-Pin: EIN Klick bestaetigt sie als richtige Quelle
    # (JB 07.07.2026) -> localStorage -> naechster Sync pinnt sie fest (apply_source_confirms).
    res_inner = ''.join(
        f'<span class=altrow>'
        f'<a class="pill go"{pp} href="{html.escape(u)}" target=_blank title="{html.escape(_res_tip(u))}">'
        f'{html.escape(nm)}</a>'
        f'<button type=button class=pin onclick="cfmSrc(this)" title="{html.escape(s["src_confirm"])}">✔</button>'
        f'</span>' for u, nm, pp in reserves if u)
    # …und fuer Serien ohne Kandidat (die 'Alternative'-Faelle): eigenen, per 'suchen' gefundenen
    # Link einfuegen und bestaetigen.
    own = (f'<button type=button class="pill alt srcown" onclick="cfmSrcOwn(this)">'
           f'{s["src_confirm_own"]}</button>')
    # HTML-Diaet: die Kombi-Such-URL (enthaelt die IDENTISCHE Reader-Domain-Liste, frueher x786 im
    # HTML) baut das JS-Boot aus data-n/data-rc + I.sq -> hier nur ein leerer galt-Anker.
    gcombined = '<a class="pill go galt" href="#" target=_blank>🔍 Google</a>'
    # 🕰 Wayback ENTFERNT (JB-Entscheidung Runde 25): das Archiv spielte auf toten Seiten deren
    # Weiterleitungs-Skripte ab und landete auf fremden Mangas — mehr Verwirrung als Rettung.
    # Manuelle Funde (z.B. Blogspot-Archive) laufen stattdessen als series_overrides-Eintrag.
    return (f'<details class=alt><summary class="pill alt">{_pl(s["alt_menu"])}</summary>'
            f'{gcombined}{res_inner}{own}</details>')


def _cols_menu(s):
    """Menue 'Spalten' (neben den Panels): je optionaler Spalte eine Checkbox -> body.hc<n> ein/aus.
    Spalte 1 (Serie) + 8 (Aktion) bleiben immer sichtbar. JS: toggleCol()."""
    cols = [(3, s["col_user"]), (4, s["col_status"]), (5, s["col_chapters"]),
            (6, s["col_last"]), (7, s["col_source"]), (8, s["col_rating"])]
    # KEIN Leerzeichen zwischen Kaestchen und Wort (Abstand macht allein das CSS-gap: 2px, JB-Wunsch).
    boxes = "".join(f'<label class=colbox><input type=checkbox id=col{n} checked '
                    f'onchange="toggleCol({n},this)">{html.escape(nm)}</label>' for n, nm in cols)
    # Autor-Zeile (kein Tabellen-Spalten-Index, eigener Schalter): mobil aus Default, hier
    # wieder zuschaltbar — und am Desktop abwaehlbar (JB 09.07.2026: 'soll hinzugefuegt
    # werden koennen, falls gewuenscht'). Haken-Zustand setzt auApply() beim Laden.
    boxes += (f'<label class=colbox><input type=checkbox id=colau '
              f'onchange="toggleAu(this)">{html.escape(s["col_author"])}</label>')
    return (f'<details class=cols><summary class="pill alt" title="{html.escape(s["cols_menu_title"])}">'
            f'{s["cols_menu"]}</summary><div class=colbxs>{boxes}</div></details>')


# Subdomain-Kosmetik fuers Pausen-Menue (Stufe 1, JB Runde 38): w1./ww2./m./test. sind
# Spiegel-Varianten derselben Seite -> auf die Basisdomain falten (Teilstring-Matching
# der Pause deckt die Subdomains automatisch mit ab).
_WSUB = re.compile(r"^(?:w{1,3}\d*|m|test)\.")
# Kuratierte Betreiber-Familien (Stufe 2): EIN Schalter je Betreiber. Nur exakte Domains
# (NIE generische Teilstrings — 'manga' wuerde mangafire/mangack/… zusammenwerfen, JB-Regel:
# bei zu vielen Matches nicht konsolidieren); greift nur, wenn >=2 Domains real vorkommen.
_FAMILIES = (("Asura", ("asurascans.com", "asuracomic.net", "asuratoons.info")),
             ("Bato", ("bato.to", "bato.si")),
             ("MangaPark", ("mangapark.io", "mangapark.net", "mangapark.com")))
_FAMILY_MAX = 6          # groessere Gruppen bleiben aufgeloest (JB-Regel)


def _pause_menu(s, rows=None):
    """Menue '⏸ Pausen' (neben 'Spalten', JB Runden 37+38): ALLE Lese-Seiten, deren Pause
    etwas bewirken kann — kuratierte Reader + jede real verlinkte Seite. KONSOLIDIERT
    (JB Runde 38, drei Stufen): Subdomains -> Basisdomain, kuratierte Betreiber-Familien,
    Ein-Serien-Domains in eine aufklappbare Sammelgruppe. Konsolidierte Eintraege tragen
    ein ×n-Badge, der Tooltip nennt die enthaltenen Domains. Je Eintrag ein Status-Punkt
    (Ampelfarbe; grau = ungeprueft). Schalter wirken CLIENTSEITIG (localStorage
    'pausedReaders', data-ph = Komma-Liste von Teilstrings); Server-Default: sources.json."""
    try:
        with open(_READER_DATA, encoding="utf-8") as f:
            readers = json.load(f).get("readers") or {}
    except Exception:
        readers = {}
    status = {h: (r.get("status") or "") for h, r in readers.items()}
    names = {h: r.get("name", h) for h, r in readers.items()}
    # Stufe 1: Hosts sammeln + auf Basisdomains falten; je Basisdomain die Serien zaehlen
    groups, series_ct = {}, Counter()
    def _add(h, key=None):
        base = _WSUB.sub("", h)
        groups.setdefault(base, set()).add(h)
        if key is not None:
            series_ct[(base, key)] = 1
    for h in readers:
        _add(h)
    for i, e in enumerate(rows or []):
        for u, _nm in (e.get("read_urls") or []):
            hh = host(u)
            if hh:
                _add(hh, key=i)
        if e.get("site"):
            _add(e["site"], key=i)
    drop = ("google.", "anilist", "mangabaka")
    groups = {b: hs for b, hs in groups.items()
              if b and not is_dead_reader(b) and not any(d in b for d in drop)}
    if not groups:
        return ""
    per_base = Counter(b for (b, _k) in series_ct)
    # Stufe 2: Familien mergen (nur real vorkommende Domains, Deckel _FAMILY_MAX)
    entries = []                     # (label, ph_csv, all_hosts, status_host, kuratiert)
    used = set()
    for fam_name, fam_domains in _FAMILIES:
        present = [b for b in fam_domains if b in groups]
        if 2 <= len(present) <= _FAMILY_MAX:
            allh = sorted(set().union(*(groups[b] for b in present)))
            entries.append((fam_name, ",".join(sorted(present)), allh, present[0], True))
            used.update(present)
    # Stufe 3: Ein-Serien-Domains (nicht kuratiert, genau 1 Serie) -> Sammelgruppe
    singles, main = [], []
    for b in sorted(groups, key=lambda x: names.get(x, x).lower()):
        if b in used:
            continue
        label = names.get(b, b)
        item = (label, b, sorted(groups[b]), b, b in readers)
        if b not in readers and per_base.get(b, 0) <= 1:
            singles.append(item)
        else:
            main.append(item)

    def _box(label, ph, allh, st_host, stop=False):
        col = _READER_COLOR.get(status.get(st_host), "#888")
        badge = f'<sup class=pbadge>×{len(allh)}</sup>' if len(allh) > 1 or "," in ph else ""
        tip = s["pause_covers"].format(doms=", ".join(allh)) if (len(allh) > 1 or "," in ph) else label
        # stop=True: Kaestchen sitzt in einem <summary> -> Klick darf das Aufklappen nicht toggeln
        stopper = ' onclick="event.stopPropagation()"' if stop else ""
        return (f'<label class=colbox title="{html.escape(tip)}"{stopper}>'
                f'<input type=checkbox data-ph="{html.escape(ph)}" '
                f'{"checked " if all(is_paused_reader(p) for p in ph.split(",")) else ""}'
                f'onchange="togglePause(this)">'
                f'<span class=dot style="color:{col}">●</span>{html.escape(label)}{badge}</label>')

    def _key(item):
        label, ph, _allh, st_host, _cur = item
        return (0 if is_paused_reader(ph.split(",")[0])
                else (1 if status.get(st_host, "") not in ("", "ok") else 2), label.lower())
    boxes = [_box(la, ph, ah, sh) for la, ph, ah, sh, _c in sorted(entries + main, key=_key)]
    grp = ""
    if singles:
        g_ph = ",".join(ph for _la, ph, _ah, _sh, _c in singles)
        g_all = [h for _la, _ph, ah, _sh, _c in singles for h in ah]
        inner = "".join(_box(la, ph, ah, sh) for la, ph, ah, sh, _c in singles)
        grp = (f'<details class=ssg><summary title="{html.escape(s["pause_group_title"])}">'
               f'{_box(s["pause_group"].format(n=len(singles)), g_ph, g_all, "", stop=True)}'
               f'</summary><div class=ssgi>{inner}</div></details>')
    return (f'<details class=cols><summary class="pill alt" title="{html.escape(s["pause_menu_title"])}">'
            f'{s["pause_menu"]}</summary><div class="colbxs pausebxs">{"".join(boxes)}{grp}</div></details>')


def render(rows, out_dir, out_html, namelen=NAMELEN, lang="de", readers_snap=None):
    s = i18n.strings(lang)
    # Auto-Pausen aus dem letzten Reader-Check laden (falls refresh_status nicht in DIESEM
    # Prozess lief) — down/Wartungs-Seiten weichen dann sofort auf Reserven aus (Runde 38).
    try:
        with open(_READER_DATA, encoding="utf-8") as f:
            _config.set_auto_paused(json.load(f).get("auto_paused") or [])
    except Exception:
        pass
    # Standard-Sortierung nach Bewertung (Median ist bereits Bayes-geglaettet), dann A-Z; ohne Wertung ans Ende
    rows.sort(key=lambda e: (-(e.get('rating') or -1.0), e['name'].lower()))
    now_ts = time.time()
    # +Alt = EINE kombinierte Google-Suche ueber alle gelisteten Lese-Seiten (site:-Filter),
    # einmal vorberechnet. Ersetzt die frueheren Einzel-Seiten-Suchen (403-anfaellig/nutzlos).
    sites_q = " OR ".join(f"site:{d}" for d in search_sites())
    pcnt = Counter()
    genre_ct = Counter()
    dead = sum(1 for e in rows if e.get('link_ok') is False)
    help_n = 0
    trs = []
    # Archiv-Migration (Runde 35, "Mein Archiv hat sich resetted"): data-h war norm(Anzeigetitel)
    # -> jede Titelkorrektur invalidierte Archiv/Favoriten/Bestaetigungen im localStorage. Jetzt:
    # STABILER Schluessel (DB-ID bzw. n:+Roh-Verlaufsname) + Alias-Map MIG (alle bekannten
    # Titel-Varianten -> neuer Schluessel), die das JS beim Boot einmalig umschreibt.
    mig, mig_ambig = {}, set()
    for e in rows:
        full = e['name']
        disp = full if len(full) <= namelen else full[:namelen - 1].rstrip() + '…'
        d = datetime.fromtimestamp(e['lv'], timezone.utc).strftime('%d.%m.%Y') if e['lv'] else '–'
        nxt, unread, latest = next_and_unread(e['chap'], e.get('latest'))
        uprog = user_progress(e['chap'], latest, e['lv'], now_ts, pub_status=e.get('pub_status'))
        pcnt[uprog] += 1
        for _g in (e.get('genres') or []):
            genre_ct[_g] += 1
        # Google-Suchformat (JB-erprobt): "<Titel> manga online chapter <n>" -> trifft die Reader gut.
        g = "https://www.google.com/search?q=" + urllib.parse.quote(f"{full} manga online chapter {nxt}".strip())
        unsafe = any(u in (e.get('site') or '') for u in UNSAFE_SITES)
        cls = PROGRESS_CLASS.get(uprog, '')
        # Laenger als ~3 Monate pausiert (seit dem letzten Lesen) -> eigene, deutlichere Farbe
        # (klarer als das normale "Pausiert"-Gelb, JB-Wunsch).
        if uprog == 'prog_paused' and e['lv'] and (now_ts - e['lv']) > 90 * 86400:
            cls = 'ulong'
        flag = e.get('flag') or ''
        # Kapitel-Zelle IMMER "gelesen / gesamt" (eindeutig, welche Zahl was ist):
        #  - kennt die DB ein hoeheres Kapitel  -> "gelesen / neuestes" (die Differenz sind neue Kapitel)
        #  - DB hinkt hinterher / genau aufgeholt -> "gelesen / gelesen" (du bist auf dem Stand)
        #  - Gesamtzahl unbekannt                -> "gelesen / ?"
        _read, _lat = e['chap'], e.get('latest')
        dyn = is_dynamic(e.get('site'))
        # JB-Entscheidung: liest du auf einer Seite mit AUFGEBLAEHTER Nummerierung (z.B. asuracomic zaehlt
        # hoeher als die DB), deckle den gelesenen Stand auf die DB-Gesamtzahl -> "aufgeholt" statt dem
        # verwirrenden "249/112". NUR bei SICHEREM Match (hohe conf, kein Roman); ein Fehlmatch-Verdacht
        # (niedrige conf) bleibt ungedeckelt und mit ❓ sichtbar.
        if _read and _lat and _read > _lat and not dyn and not e.get('novel') and (e.get('conf') or 0) >= 0.7:
            _read = _lat
        # Lesestand deutlich UEBER der bekannten Kapitelzahl -> fast sicher ein Fehlmatch (man kann
        # nicht mehr Kapitel lesen als existieren) oder Parse-Fehler. NICHT bei dynamischen Webtoons
        # (dort ist die Kapitelzahl aus der URL ohnehin unzuverlaessig). -> unten als "braucht Hilfe".
        mismatch = bool(_read and _lat and _read > _lat * 1.2 and not dyn)
        # Kapitel-Zelle "gelesen / gesamt": bei Fehlmatch die ECHTE (kleinere) DB-Zahl zeigen, damit die
        # Diskrepanz SICHTBAR ist (+ ❓). Sonst gesamt = groesste bekannte Zahl; '?' wenn unbekannt.
        _tot = _lat if mismatch else ((_lat if (_lat and _lat > (_read or 0)) else _read) if _lat else None)
        # Gesamt-Teil mit eigenem Tooltip bei NEUEN Kapiteln (JB Runde 38, Feature 3):
        # Hover ueber die Gesamtzahl nennt die neuen Kapitel; der Zell-Tooltip (Klick:
        # Lesestand korrigieren, applyTips) bleibt fuer den Rest der Zelle erhalten.
        _new_tip = (f' title="{html.escape(s["new_chaps_tip"].format(n=unread))}"'
                    if unread else '')
        prog = (f'{chapter_label(_read)} / '
                f'<span class=totc{_new_tip}>{chapter_label(_tot) if _tot else "?"}</span>')
        dyn_badge = f'<span class="unk" title="{html.escape(s["dynamic_hint"])}"> ⓘ</span>' if dyn else ''
        _t = (e.get('type') or '').capitalize()  # Typ jetzt direkt aus dem Katalog (MangaBaka)
        med = _t if _t in MEDIA_FILTER else medium(e.get('country'))   # Fallback: aus Herkunftsland
        med_badge = f'<span class="med">{med}</span> ' if med else ''
        ak = e.get('adult_kind')                 # 'sexual' (pink) / 'gore' (Gewalt) / ''
        if ak == 'sexual':
            adult_badge = '<span class="adult" title="Sexuell/Fetisch">18+</span> '
        elif ak == 'gore':
            adult_badge = '<span class="adult-v" title="Gewalt/Gore">18+</span> '
        else:
            adult_badge = ''
        # Die drei komplexesten Zellen-Bausteine sind in benannte Helfer ausgelagert (oben):
        prim, srccell = _primary_action(e, s, now_ts, unsafe, g, uprog)   # Aktion + Quelle-Spalte
        mdlink = _db_pill(e)                                        # Baka/AL-DB-Pille aus der md_id
        altcell = _alt_cell(e, s, sites_q, nxt, full)              # +Alt: Kombi-Suche + Direktlinks
        rating = e.get('rating')
        if rating:
            comps = e.get('ratings') or []
            tip = s["rating_tip"].format(rating=f"{rating:.1f}", n=len(comps),
                                         vals=", ".join(f"{x:.1f}" for x in comps))
            rt_cell = f'<td class="rt" data-rt="{rating:.2f}" title="{html.escape(tip)}">{rating:.1f}</td>'
        else:
            rt_cell = '<td class="rt" data-rt="-1">–</td>'
        author = e.get('author') or ''
        # Original-Titel bleibt im Cache (title_native), wird aber NICHT angezeigt (JB: unnoetig) -
        # nur als verstecktes Suchfeld, damit man die Serie auch ueber den Originalnamen findet.
        native = e.get('title_native') or ''
        nat_search = (f'<span class="hidden" style="display:none">{html.escape(native)}</span>'
                      if native and norm(native) != norm(full) else '')
        au = (f'<div class="au">{html.escape(author)}{nat_search}</div>' if author
              else f'<div class="au unk">{s["unknown"]}{nat_search}</div>')
        # JB-Regel: "mit funktionierendem Link keine Hilfe". Ein verifizierter Reader-Link
        # (read_urls) macht die Serie lesbar -> nicht mehr als Problem markieren, auch wenn der
        # DB-Match (Autor/md_id) noch fehlt. ABER: ein Fehlmatch (Lesestand > Kapitelzahl) ist ein
        # echtes Problem und wird IMMER markiert (falscher Manga trotz Link).
        needs_help = ((is_unresolved(e) or bool(e.get('needs_help'))) and not e.get('read_urls')) or mismatch
        help_n += needs_help
        help_attr = ' data-help="1"' if needs_help else ''
        _hbadge_tip = s["mismatch_badge_title"] if mismatch else s["help_badge_title"]
        help_badge = (f'<span class="unk" title="{html.escape(_hbadge_tip)}">❓ </span>'
                      if needs_help else '')
        # Titel-Bestaetigung (JB-Wunsch D): bei UNSICHEREM Match ein ✔ zum Anklicken — "dieser Titel
        # stimmt" wird gesammelt (Export ✔-Button) und vom Wochen-Lauf fest gepinnt (apply_confirms).
        cfm_badge = (f'<span class=cfm onclick="cfm(this)" title="{html.escape(s["confirm_title"])}">✔</span>'
                     if (e.get('conf') or 1.0) < 0.62 and str(e.get('md_id') or '').startswith('mb:') else '')
        fin_badge = (f'<span class="finb" title="{html.escape(s["finished_badge_title"])}">🏁 </span>'
                     if uprog == "prog_finished" else '')
        pub = e.get('pub_status') or ''
        pub_cell = (f'<td class="pub">{html.escape(pub)}</td>' if pub
                    else f'<td class="pub unk">{s["unknown"]}</td>')
        # STABILER Archiv-Schluessel: DB-ID ("mb:123"/UUID) ueberdauert alles; sonst der Roh-
        # Verlaufsname ("n:"+k), der sich bei Titelkorrekturen nie aendert. norm(full) nur noch
        # als letzte Reserve (direkt konstruierte Zeilen, z.B. Tests).
        raw_keys = [rk for rk in (e.get('hkeys') or []) if rk]
        key = e.get('md_id') or ('n:' + (raw_keys[0] if raw_keys else norm(full)))
        # Alias-Map fuellen: alles, worunter diese Serie FRUEHER als data-h gespeichert sein kann
        # (norm alter/aktueller Titel, Roh-Schluessel, kuenftig auch n:-Keys wenn spaeter eine
        # DB-ID auftaucht). Mehrdeutige Aliasse (2 Serien) fliegen raus — lieber nicht migrieren
        # als falsch migrieren.
        for al in {norm(full), norm(e.get('title_native') or ''), norm(e.get('title_romaji') or ''),
                   *(norm(t) for t in (e.get('alt_titles') or [])),
                   *raw_keys, *('n:' + rk for rk in raw_keys)}:
            if al and al != key:
                if mig.get(al, key) != key:
                    mig_ambig.add(al)
                else:
                    mig[al] = key
        plabel = s[uprog]
        trs.append(
            f'<tr data-s="{html.escape(plabel)}"{help_attr} data-c="{html.escape(e.get("country") or "")}" data-medium="{med}" data-gen="{html.escape(" ".join(e.get("genres") or []))}" data-adult="{html.escape(e.get("adult_kind") or "")}" data-h="{html.escape(key)}"{f' data-lh="{html.escape(e["lh_status"])}"' if e.get("lh_status") else ""} data-au="{html.escape(author.lower())}" data-n="{html.escape(full.lower())}" data-mal="{e.get("mal_id") or ""}" data-mst="{MAL_STATUS.get(uprog, "Reading")}" data-rc="{int(_read or 0)}"{f' data-cov="{html.escape(_cov)}"' if (_cov := cover_url(e.get("cover"))) else ""}{f' data-q2="{html.escape(_q2.lower())}"' if (_q2 := (e.get("title_romaji") or "")).strip() and norm(_q2) != norm(full) else ""}>'
            # HTML-Diaet (JB): die STATISCHEN Tooltip-Texte stehen NICHT mehr je Zeile im HTML
            # (6 Attribute x ~800 Zeilen = mehrere 100 KB), sondern einmal in I.tt — das JS-Boot
            # setzt sie beim Laden (applyTips). Dynamische Titles (voller Name, dsite) bleiben inline.
            f'<td title="{html.escape(full)}"><div class=nmline><span class=arch onclick="arch(this.closest(\'tr\').dataset.h)">🗃</span><span class=unarch onclick="arch(this.closest(\'tr\').dataset.h)">↩</span>{help_badge}{cfm_badge}{fin_badge}{("<span class=fl>" + flag + "</span>") if flag else ""} {adult_badge}{med_badge}{html.escape(disp)}</div>{au}</td>'
            f'<td class=favcol><span class=favi onclick="fav(this.closest(\'tr\').dataset.h)">⭐</span></td>'
            f'<td class="st {cls}">{html.escape(plabel)}</td>'
            f'{pub_cell}'
            f'<td class="c" data-un="{unread}" data-lat="{int(_tot or 0)}"{" data-dyn=1" if dyn else ""}>{prog}{dyn_badge}</td>'
            f'<td class="d" data-ts="{int(e["lv"])}">{d}</td>'
            f'<td class="src">{srccell}</td>'
            f'{rt_cell}'
            f'<td class=act>{prim}<a class="pill gsr" href="#" target=_blank>{_pl(s["search"])}</a>{mdlink}{altcell}</td>'
            f'<td class=repcell><button class="pill rep" onclick="rep(this)">⚠</button></td></tr>')
    upd = datetime.now().strftime('%d.%m.%Y %H:%M')
    PROG_ORDER = ("prog_reading", "prog_caught", "prog_finished", "prog_paused", "prog_backlog")
    sub = (f"{len(rows)} {s['series']} · "
           + " · ".join(f"{s[k]} {pcnt.get(k, 0)}" for k in PROG_ORDER)
           + f" · {s['dead_sources']} {dead} · {s['updated']} {upd}")
    # KONSOLIDIERT (JB: Zeilenumbruch der 6 Filter-Knoepfe "schlimm"): EIN Dropdown statt sechs
    # Buttons — Live-Counts je Option pflegt regray() im JS (Basistext steckt in data-l).
    filter_btns = (f'<select id=pf class=btn onchange="fsSel(this)" title="{html.escape(s["filter_all_tip"])}">'
                   f'<option value="">{s["filter_all"]} ({len(rows)})</option>'
                   + "".join(f'<option value="{html.escape(s[k])}" title="{html.escape(s["prog_tips"][k])}">'
                             f'{s[k]} ({pcnt.get(k, 0)})</option>' for k in PROG_ORDER)
                   + '</select>')
    # Hilfe-Knopf IMMER zeigen — auch bei 0 (JB: "fuer das gute Gefuehl einer 0").
    help_btn = (f'<button id=hb class=btn onclick="fh(this)" title="{html.escape(s["help_button_title"])}">'
                f'{s["help_button"].format(n=help_n)}</button>')
    new_n = sum(1 for e in rows if e.get("latest") and e.get("chap") and e["latest"] > e["chap"])
    new_btn = (f'<button id=nb class=btn onclick="fn(this)" title="{html.escape(s["new_button_title"])}">'
               f'🆕 {s["new_button"].format(n=new_n)}</button>') if new_n else ''
    # Zustands-SEED (JB-Wunsch 3a): liegt data/list_state.json (💾-Export) vor, wird sie eingebettet.
    # Ein Browser OHNE gespeicherten Zustand (neu/Website-Daten geloescht) stellt Favoriten/Archiv/
    # Bestaetigungen daraus automatisch wieder her -> nichts geht mehr verloren.
    seed = "null"
    try:
        _sp = os.path.join(os.path.dirname(_READER_DATA), "list_state.json")
        if os.path.exists(_sp):
            seed = json.dumps(json.load(open(_sp, encoding="utf-8")), ensure_ascii=False)
    except Exception:
        seed = "null"
    # I.tt = die statischen Zeilen-Tooltips EINMAL (HTML-Diaet); JS applyTips() verteilt sie.
    tt = json.dumps({"c": s["chapfix_tip"], "fav": s["fav_title"], "arch": s["archive_title"],
                     "unarch": s["unarchive_title"], "rep": s["report_broken_title"],
                     "cfm": s["confirm_title"], "galt": s["alt_search_tip"],
                     "sq": sites_q,
                     "st": {k: s.get(v, "") for k, v in STATUS_TIP.items()}}, ensure_ascii=False)
    # MIG = Alias->Schluessel fuer die einmalige localStorage-Migration (mehrdeutige raus, s.o.)
    for al in mig_ambig:
        mig.pop(al, None)
    mig_json = json.dumps(mig, ensure_ascii=False, separators=(",", ":"))
    jsvars = (f'<script>var I={{"arch":"🗃 {s["archive_count"]}","fav":"{s["fav_button"]}",'
              f'"xd":"{s["export_done"]}","xs":"{s["export_skipped"]}","cq":"{s["chapfix_prompt"]}",'
              f'"imu":"{s["import_done"]}","imn":"{s["import_new"]}","sy":"{s["syncbar"]}","syp":"{s["sync_paused"]}","tp":"{s["to_top"]}","rts":{now_ts},'
              f'"op":"{s["open"]}","brkSent":"{s["brk_sent"]}","rgo":"{s["recs_read_tip"]}",'
              f'"altm":"{s["alt_menu"]}",'
              f'"dudArch":"{s["dud_arch"]}","dudBack":"{s["dud_back"]}","dudAll":"{s["dud_all"]}",'
              f'"paused":{json.dumps(sorted(_config.all_paused()), ensure_ascii=False)},'
              f'"tt":{tt}}};'
              f'var SEED={seed};var MIG={mig_json};</script>')
    type_opts = "".join(f"<option>{m}</option>" for m in MEDIA_FILTER)   # Manga/Manhwa/Manhua/Webtoon/Comic
    genre_chips = "".join(f'<span class=gchip data-g="{html.escape(g)}" onclick="toggleGenre(this)">{html.escape(g.capitalize())} <i>{c}</i></span>'
                          for g, c in genre_ct.most_common(30))
    # Struktur der ausgelieferten HTML (mit <!-- Ankern --> zum Zurechtfinden, obwohl minifiziert):
    #   Kopf+Ampel · Statistik/Empfehlungen · Steuerleiste · Tabelle (eine <tr> je Serie) · Skripte.
    # CSS/JS kommen minifiziert aus den lesbaren Templates (list.css/list.js), Zeilen aus `trs`.
    P = f"""<!doctype html><html lang={lang}><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1,minimum-scale=1"><meta name=color-scheme content="dark light"><link rel=manifest href=manifest.json><meta name=theme-color content="#d67756"><link rel=apple-touch-icon href=apple-touch-icon.png><title>{s['title']}</title><style>
{CSS}
</style></head><body>
<!-- Kopf: Titel · Untertitel (Zusammenfassung) · Quellen-/Reader-Ampel --><h1>📚 {s['title']} <a class=hguide href="{s['guide_file']}" target=_blank title="{html.escape(s['guide_title'])}">📖</a></h1>
<div class=sub>{sub}</div>
{status_block(s)}
<!-- Statistik + Empfehlungen (nebeneinander) -->
<div class=panels>{stats_panel(rows, pcnt, s)}{recommendations_panel(rows, s)}{_cols_menu(s)}{_pause_menu(s, rows)}</div>
<!-- Steuerleiste: Fortschritts-Filter · neu/Hilfe · Suche · Typ · Genre · 18+ · Archiv -->
<div class=ctrl>{filter_btns}{new_btn}{help_btn}
<input id=q placeholder="{html.escape(s['search_placeholder'])}" oninput=qf()><select id=cf class=btn onchange=ff()><option value="">{s['type_all']}</option>{type_opts}</select><details class=genres><summary class=btn id=gfs title="{html.escape(s['genre_toggle'])}">{s['genre_all']} ▾</summary><div id=gf class=gchips>{genre_chips}</div></details><select id=nf class=btn onchange="setNsfw(this)" title="{html.escape(s['nsfw_title'])}"><option value="">{s['nsfw_all']}</option><option value="both">{s['nsfw_hide_both']}</option><option value="sexual">{s['nsfw_hide_sexual']}</option><option value="gore">{s['nsfw_hide_gore']}</option></select><button id=rand class=btn onclick="luckyPick()" title="{html.escape(s['lucky_title'])}">🎲</button><span class=spacer></span><button id=gear class=btn onclick="toggleGear()" title="{html.escape(s['gear_title'])}">⚙</button><span class=tools><button id=til class=btn onclick="toggleTiles()" title="{html.escape(s['tiles_title'])}">▦</button><button id=dns class=btn onclick="toggleDense()" title="{html.escape(s['dense_title'])}">⬍</button><button id=thm class=btn onclick="toggleTheme()" title="{html.escape(s['theme_title'])}">☀</button><details class=xport><summary class=btn title="{html.escape(s['export_menu_title'])}">⤴ {s['export_menu']}</summary><div class=xpanel><label><input type=checkbox id=xarch> {s['export_with_arch']}</label><label><input type=checkbox id=xfav> {s['export_fav_only']}</label><button class=btn onclick="exportMal()" title="{html.escape(s['export_mal_title'])}">{s['export_mal']}</button><button class=btn onclick="exportJson()">{s['export_json']}</button><label class=btn title="{html.escape(s['import_mal_title'])}">{s['import_mal']}<input type=file accept=".xml,text/xml" style="display:none" onchange="importMal(this)"></label><details class=xguide><summary>{s['xg_title']}</summary><div class=xhelp>{s['xg_up']}<br>{s['xg_down']}<br>{s['xg_al']}<br>{s['xg_more']}<br>{s['xg_bug']}</div></details></div></details><button id=sb class=btn onclick="saveState()" title="{html.escape(s['state_export_title'])}">💾</button></span><button id=cfb class=btn onclick="showCfm()" title="{html.escape(s['confirm_export_title'])}" style="display:none">✔ 0</button><button id=rb class=btn onclick="showBrk()" title="{html.escape(s['report_export_title'])}" style="display:none">🛠 0</button></div>
<!-- Fortschrittsbalken (JB): zeigt laufende Anreicherung; JS pollt data/sync_progress.json (nur ueber http) -->
<div id=syncbar><span id=synctxt></span><div class=track><div class=fill></div></div></div>
<!-- Angepinnt oben rechts, AUSKLAPPBAR (JB 09.07.2026: 'nimmt auf Mobile sehr viel Platz'):
     Sommary-Griff + 2x2-Raster; Desktop startet offen, Mobile zu (Mini-Script darunter). -->
<details class=pinbox id=pb open><summary class=btn title="{html.escape(s['pinbox_tip'])}">🗃 ⭐ <span class=pbc>▾</span></summary><div class=pbody><button id=vb class=btn onclick="toggleArchview()" title="{html.escape(s['archview_title'])}">🗃 {s['archive_count']}: 0</button><button id=ab class=btn onclick="toggleArchmode()" title="{html.escape(s['archmode_title'])}">{s['archive']}</button><button id=vfb class=btn onclick="toggleFavview(this)" title="{html.escape(s['fav_button_title'])}">⭐ {s['fav_button']}: 0</button><button id=fm class=btn onclick="toggleFavmode()" title="{html.escape(s['fav_mode_title'])}">⭐ {s['fav_mode']}</button></div></details>
<script>if(innerWidth<761){{var _pb=document.getElementById('pb');if(_pb)_pb.removeAttribute('open');}}</script>
<!-- Tabelle: eine <tr> je Serie; Filter/Sortierung/Archiv lesen die data-* Attribute der Zeile -->
{'' if trs else f'<div class=welcome>{s["welcome_empty"]}</div>'}
<div class=wrap><table id=t><thead><tr><th><span class=sh onclick="s(0)">{s['col_series']}&nbsp;↕</span><span class=shau> · <span class=sh onclick="sortAuthor()">{s['col_author']}&nbsp;↕</span></span></th><th class=favh title="{html.escape(s['fav_title'])}">⭐</th><th onclick=s(2) title="{html.escape(s['col_user_title'])}">{s['col_user']}</th><th onclick=s(3)>{s['col_status']}</th><th onclick=s(4) title="{html.escape(s['col_chapters'] + ' — ' + s['col_chapters_title'])}">{s['col_chapters_s']}</th><th onclick=s(5)>{s['col_last']}</th><th onclick=s(6)>{s['col_source']}</th><th onclick=s(7)><span class=hl>{s['col_rating']}</span><span class=hs>{s['col_rating_s']}</span></th><th>{s['col_action']}</th><th title="{html.escape(s['report_broken_title'])}"></th></tr></thead><tbody>{''.join(trs)}</tbody></table></div>
<!-- Skripte: Interaktivität (list.js, minifiziert) + Service-Worker (nur über http) -->
{jsvars}<script>{JS}</script><script>if('serviceWorker'in navigator&&location.protocol.indexOf('http')===0){{navigator.serviceWorker.register('sw.js').catch(function(){{}})}}</script></body></html>"""
    os.makedirs(out_dir, exist_ok=True)
    with open(out_html, "w", encoding="utf-8") as f:
        f.write(P)
    # Roh-Zeilen fuer DYNAMISCHES Nachladen exportieren (JB: 'muss die Seite neu laden?'):
    # die offene Seite tauscht damit NUR die Tabellen-Zeilen aus — kein Reload, Scroll/Filter/
    # Theme bleiben. Best-effort; ohne die Datei faellt die Seite auf den Reload zurueck.
    try:
        ddir = os.path.join(out_dir, "data")
        os.makedirs(ddir, exist_ok=True)
        payload = ("var LROWS=" + json.dumps("".join(trs), ensure_ascii=False)
                   + ",LSUB=" + json.dumps(sub, ensure_ascii=False)
                   + ",LTS=" + str(now_ts) + ";")
        tmp = os.path.join(ddir, "list_rows.js.tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(payload)
        os.replace(tmp, os.path.join(ddir, "list_rows.js"))
    except Exception:
        pass
    return len(rows)
