# -*- coding: utf-8 -*-
"""
Link-Gesundheit: EIN reiches, handlungsorientiertes Verdikt pro Reader-URL (JB 07.07.2026).

Warum ein eigenes Modul statt readerlink._alive_status?
    _alive_status liefert nur ok/no/blocked/odd und wirft dabei DREI voellig verschiedene Faelle
    in denselben Topf 'no': einen TIMEOUT (transient — Link behalten!), ein echtes 404 (totes
    Kapitel — Reserve/Neuaufloesung) und einen SERIEN-Redirect (Kapitel gibt es nicht mehr —
    Kapitel neu ableiten). Fuer die Selbstheilung muessen wir sie unterscheiden.

Kernprinzip (JB-No-Go 'Links bei schlechtem Netz weg'): Dieses Modul LOESCHT nie etwas. Es liefert
nur das Verdikt + die empfohlene Aktion; die eigentliche, nicht-destruktive Anwendung (Quarantaene
statt Loeschen, Neuaufloesung) macht der Aufrufer. Herabgestuft wird ausserdem erst nach ZWEI
bestaetigten Negativ-Messungen (`decide`), und BLOCKED/DOWN werden NIE herabgestuft.

Fast + schonend: `classify_result` ist rein (kein Netz, voll testbar); `check_url` ist der duenne
Netz-Wrapper ueber readerlink.fetch_status (mit dessen Pacing/UA).
"""
from enum import Enum
from urllib.parse import urlparse

from . import readerlink as _rl


class Verdict(str, Enum):
    """Zustand eines Kapitel-Links. `str`-Enum -> JSON-/Vergleich-freundlich ('alive' == Verdict.ALIVE)."""
    ALIVE = "alive"              # Kapitel existiert: 200, Pfad + Kapitel-Token erhalten (ggf. Identitaet bestaetigt)
    MOVED = "moved"             # existiert, aber unter anderer URL (Redirect, Token stimmt) -> Link updaten
    SERIES_PAGE = "series_page"  # 200, aber Serien-Root / Kapitel-Token verloren -> Kapitel neu ableiten
    GONE = "gone"               # bewiesen weg: echtes 404 (nur bei Hard-404-Readern verlaesslich)
    BLOCKED = "blocked"         # 403/429/503/Cloudflare-Challenge -> im Browser nutzbar, NICHT anfassen
    DOWN = "down"               # Timeout/Verbindungsfehler/5xx -> transient, behalten + spaeter erneut
    UNSURE = "unsure"           # 200 ohne Beweis (Soft-404-Reader / fremder Inhalt) -> vertrauen/last-good


# Empfohlene Aktion je Verdikt (alle nicht-destruktiv). Der Aufrufer setzt sie um.
ACTION = {
    Verdict.ALIVE: "keep",
    Verdict.MOVED: "update",         # final_url als neuen Link uebernehmen
    Verdict.SERIES_PAGE: "reresolve",  # Kapitel per Muster/Suche neu ableiten
    Verdict.GONE: "quarantine",      # nach Bestaetigung: in Quarantaene + Reserve/Neuaufloesung
    Verdict.BLOCKED: "keep",
    Verdict.DOWN: "keep",
    Verdict.UNSURE: "keep",
}

# Nur diese Verdikte duerfen (nach Hysterese) eine Herabstufung ausloesen. DOWN/BLOCKED NIE —
# sie bedeuten 'gerade nicht pruefbar', nicht 'kaputt'.
CONDEMNABLE = frozenset({Verdict.GONE, Verdict.SERIES_PAGE})

# Soft-404-Reader: liefern 200 fuer ALLES (auch nicht-existente Kapitel) -> ein 200 beweist nichts,
# ein echtes 404 kommt nie. Quelle: die im readerlink-Kopf gepflegte Liste. Fuer diese Hosts kann
# nur der Identitaets-Check (Seitentitel) ein 200 zu ALIVE aufwerten; sonst bleibt es UNSURE.
SOFT_404_HOSTS = frozenset({
    "mangahub", "mangaread", "mangak", "readmanga", "linkmanga",
    "flamescans", "cocomic", "mangazin",
})


def host_of(url):
    """netloc einer URL, klein, ohne Port. Leerstring bei Muell."""
    try:
        return urlparse(url or "").netloc.split(":")[0].lower()
    except ValueError:
        return ""


def is_hard_404(host):
    """True, wenn der Host bei nicht-existenten Kapiteln ein ECHTES 404 liefert (Standard) —
    False fuer bekannte Soft-404-Reader (200-fuer-alles). Teilstring-Match wie im Projekt ueblich."""
    h = (host or "").lower()
    return not any(s in h for s in SOFT_404_HOSTS)


def _chap_token(path):
    m = _rl._CHAPTOK.search(path or "")
    return m.group(1) if m else None


def classify_result(req_url, status, final_url, body="", titles=None, hard_404=None):
    """REINE Klassifikation eines bereits abgerufenen Ergebnisses -> Verdict. Kein Netz, voll testbar.

    req_url    : die angefragte Kapitel-URL.
    status     : HTTP-Status (0 = Timeout/Verbindungsfehler, wie readerlink.fetch_status).
    final_url  : URL nach Redirects.
    body       : Antworttext (fuer CF-Marker + optionalen Identitaets-Check).
    titles     : bekannte Serien-Titel; wenn gesetzt, wird bei 200 die Seiten-Identitaet geprueft.
    hard_404   : liefert der Host echte 404 (True) oder 200-fuer-alles (False)? None = aus dem Host
                 ableiten (Standard: hart).
    """
    if hard_404 is None:
        hard_404 = is_hard_404(host_of(final_url) or host_of(req_url))
    req_path = urlparse(req_url or "").path
    fin_path = urlparse(final_url or req_url or "").path
    cf = any(m in (body or "")[:6000].lower() for m in _rl._CF_MARKERS)

    # 1) Netzfehler / Origin unten (transient) -> DOWN. 0 = Timeout/Verbindung; 5xx = Serverfehler
    #    (503 zaehlt bewusst NICHT hierher, sondern zu BLOCKED — Wartung/Bot ist im Browser nutzbar).
    if status == 0 or (500 <= status <= 599 and status != 503):
        return Verdict.DOWN
    # 2) Bot-/Cloudflare-Sperre -> BLOCKED (nie herabstufen; im Browser nutzbar)
    if status in (403, 429, 503) or cf:
        return Verdict.BLOCKED
    # 3) echtes 404 -> GONE (nur bei Hard-404-Readern verlaesslich; sonst kann 404 nicht auftreten)
    if status == 404:
        return Verdict.GONE if hard_404 else Verdict.UNSURE
    # 4) alles ausser 200 (3xx-Endzustand ohne Pfad faellt unten, sonstige Codes) -> nie hart urteilen
    if status != 200:
        return Verdict.UNSURE
    # 5) 200: Startseiten-/Serien-Root-Redirect (Pfad komplett weg) -> Serien-Seite
    if not fin_path.strip("/"):
        return Verdict.SERIES_PAGE
    # 6) 200 mit Kapitel-Anspruch: das angefragte Kapitel-Token muss in der Ziel-URL erhalten bleiben
    want = _chap_token(req_path)
    if want and _chap_token(fin_path) != want:
        return Verdict.SERIES_PAGE          # Kapitel-Token verloren/geaendert (toongod-Fall)
    # 7) Identitaet (falls Titel bekannt): fremder Seiteninhalt = nicht einordenbar
    identity = _rl._page_matches(body, titles) if titles else None
    if identity is False:
        return Verdict.UNSURE
    moved = bool(want) and fin_path != req_path
    if hard_404:
        return Verdict.MOVED if moved else Verdict.ALIVE
    # Soft-404-Reader: 200 beweist nichts -> nur ein bestaetigter Identitaets-Treffer macht ALIVE
    if identity is True:
        return Verdict.MOVED if moved else Verdict.ALIVE
    return Verdict.UNSURE


def check_url(url, titles=None, timeout=8):
    """Netz-Wrapper: eine URL abrufen (readerlink.fetch_status) und klassifizieren -> Verdict.
    Nutzt das Pacing/den User-Agent von readerlink. Reine Logik steckt in classify_result."""
    status, final, body = _rl.fetch_status(url, timeout=timeout)
    return classify_result(url, status, final, body, titles=titles)


def decide(prev_fails, verdict):
    """Confirm-before-condemn (Hysterese): eine Herabstufung (GONE/SERIES_PAGE) greift erst nach
    ZWEI aufeinanderfolgenden Negativ-Messungen — ein einzelner Flacker togglet sonst die Links.
    Positive/transiente Verdikte setzen den Zaehler zurueck (schnelle Heilung).

    Gibt (neuer_fehlerzaehler, condemn) zurueck: condemn=True erst, wenn wirklich gehandelt werden soll."""
    if verdict in CONDEMNABLE:
        n = int(prev_fails or 0) + 1
        return n, n >= 2
    return 0, False


def quarantine_link(cache_entry, url, reason):
    """NICHT-destruktiv: den Link `url` aus read_urls nach cache_entry['quarantine'] verschieben
    (mit Grund + Zeitstempel), NIE loeschen. Idempotent. Gibt True zurueck, wenn verschoben wurde.

    So bleibt ein 'toter' Link erhalten und kann per restore_link zurueckkehren, wenn sich die Seite
    erholt — das ist die 'selbst-erneuernde' Absicherung gegen faelschlich verworfene Links."""
    import time
    reads = cache_entry.get("read_urls") or []
    keep, moved = [], None
    for ln in reads:
        if ln and ln[0] == url:
            moved = ln
        else:
            keep.append(ln)
    if not moved:
        return False
    q = cache_entry.setdefault("quarantine", [])
    if not any(item.get("url") == url for item in q):
        q.append({"url": moved[0], "site": (moved[1] if len(moved) > 1 else host_of(moved[0])),
                  "reason": str(reason), "ts": int(time.time())})
    cache_entry["read_urls"] = keep
    if cache_entry.get("read_url") == url:
        cache_entry["read_url"], cache_entry["read_site"] = (
            tuple(keep[0]) if keep else ("", ""))
    return True


def restore_link(cache_entry, url):
    """Einen quarantaenierten Link zurueck an die SPITZE von read_urls holen (Selbst-Erneuerung).
    Gibt True zurueck, wenn wiederhergestellt wurde."""
    q = cache_entry.get("quarantine") or []
    item = next((it for it in q if it.get("url") == url), None)
    if not item:
        return False
    cache_entry["quarantine"] = [it for it in q if it.get("url") != url]
    reads = [ln for ln in (cache_entry.get("read_urls") or []) if ln and ln[0] != url]
    cache_entry["read_urls"] = [[item["url"], item.get("site") or host_of(item["url"])]] + reads
    cache_entry["read_url"], cache_entry["read_site"] = cache_entry["read_urls"][0]
    return True


def sweep_entry(cache_entry, check, titles=None):
    """Den PRIMAER-Reader-Link eines Cache-Eintrags pruefen und das Verdikt NICHT-destruktiv anwenden.

    `check(url, titles) -> Verdict` ist injizierbar (im Betrieb check_url, in Tests ein Fake — so ist
    die ganze Zustandsmaschine ohne Netz testbar). confirm-before-condemn via `decide`: erst nach der
    ZWEITEN bestaetigten Negativ-Messung (GONE/SERIES_PAGE) wird der Link quarantaeniert und die erste
    Reserve rueckt nach; BLOCKED/DOWN/UNSURE aendern nie etwas. Setzt `lh_status` (fuer die Anzeige, R7)
    und `lh_fails` (Hysterese-Zaehler). Rueckgabe: (verdict, action) mit action in
    {'skip','ok','watch','quarantined'}."""
    reads = cache_entry.get("read_urls") or []
    if cache_entry.get("novel") or not reads or not reads[0] or not reads[0][0]:
        return None, "skip"
    primary = reads[0][0]
    verdict = check(primary, titles)
    cache_entry["lh_status"] = verdict.value          # 'alive'/'series_page'/… (nicht 'Verdict.ALIVE')
    fails, condemn = decide(cache_entry.get("lh_fails", 0), verdict)
    if not condemn:
        if verdict in CONDEMNABLE:
            cache_entry["lh_fails"] = fails            # 1. Negativ gemerkt -> beobachten
            return verdict, "watch"
        cache_entry.pop("lh_fails", None)              # gesund/transient -> Zaehler weg
        return verdict, "ok"
    quarantine_link(cache_entry, primary, verdict.value)   # 2x Negativ -> raus, Reserve rueckt nach
    cache_entry["lh_fails"] = 0
    return verdict, "quarantined"
