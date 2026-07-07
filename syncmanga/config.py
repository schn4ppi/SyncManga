# -*- coding: utf-8 -*-
"""
Build-agnostische Konfiguration/Konstanten des Manga-Kerns.

Enthält bewusst KEINE Mail-/Privatpfade und keine Secrets. Pfade (Ausgabe, Cache)
bleiben vorerst in der Fassade SyncEngine/manga_update.py, damit das laufende System
unveraendert weiterlaeuft; die Standalone-App setzt sie spaeter selbst (Phase 5/7).
"""

# Datenversion: hochzaehlen erzwingt beim naechsten Lauf eine vollstaendige Neu-Anreicherung
# (Titel/Flaggen/Bewertung/Autor), sonst nur fehlende/veraltete Eintraege ("resume").
CACHE_VER = 31         # 31: Titelwahl NUR aus alt_en (JB Runde 35: fremdsprachige Titel raus)
NAMELEN = 40           # ab hier Anzeige-Titel mit … kuerzen

# Alternativ-Reader (aktuelle Community-Top 2026, getrennt nach Manga vs. Manhwa/Manhua).
# Eingebaute DEFAULTS; die editierbare Quelle der Wahrheit ist data/sources.json
# (load_sources/apply_sources) — spaeter ueber das Dashboard auswaehlbar.
# MangaDex ist absichtlich NICHT dabei: dafuer gibt es bereits den direkten "MD"-Link je Zeile.
ALT_MANGA = [("MangaFire", "mangafire.to"), ("WeebCentral", "weebcentral.com"), ("Bato", "bato.to"),
             ("Comick", "comick.io"), ("MangaKatana", "mangakatana.com")]
ALT_MANHWA = [("Bato", "bato.to"), ("Comick", "comick.io"), ("WeebCentral", "weebcentral.com"),
              ("Toonily", "toonily.com"), ("Webtoons", "webtoons.com")]

# Bekannte unsichere / aggressiv werbende Aggregatoren -> "öffnen" auf sichere Alternative umleiten
UNSAFE_SITES = ("mangahasu",)

# Bekannte BEZAHL-Plattformen (JB Runde 38): "nur Volume 1 frei, Rest kaufen/Coins" = NIE als
# Reader aufnehmen. Frueh-Zugang-Modelle (asurascans: neuestes Kapitel kurz fuer Subs) sind OK
# und stehen deshalb NICHT hier. webtoons.com bleibt drin erlaubt (Fast-Pass, Katalog frei).
# Zweite Verteidigungslinie neben der Hoch-Kapitel-Probe der Discovery (Kapitel 100/1000 mitten
# in der Serie — daran scheitern Volume-1-frei-Modelle strukturell).
PAYWALL_SITES = ("viz.com", "bookwalker", "mangaplus.shueisha", "comikey", "azuki.co",
                 "mangamo", "kmanga.kodansha", "tappytoon", "tapas.io", "toomics",
                 "lezhin", "netcomics", "coolmic", "manga-planet", "futekiya", "renta",
                 "inky-pen", "comic-days", "pocket.shonenmagazine")


def is_paywall_site(site):
    """True, wenn der Host zu einer bekannten Bezahl-Plattform gehoert (nie als Reader nutzen)."""
    s = (site or "").lower()
    return any(p in s for p in PAYWALL_SITES)

# Bekannte TOTE/kaputte Reader-Domains (gespeicherter Link fuehrt ins Leere: Startseiten-Redirect,
# Cloudflare-Timeout, Werbe-/Parkseite, umgezogen). Fuer diese geht "öffnen" NIE auf den gespeicherten
# Link, sondern direkt auf die Suche nach einer lebenden Quelle. Von JB beim Durchklicken ermittelt;
# editierbar/erweiterbar in data/sources.json ("dead"). Teilstring-Match gegen den Host.
DEAD_READERS = (
    # 'asuracomic'/'asurascans' ENTSPERRT (JB Runde 35: 'prio 1, hervorragende Scanlation-
    # Seite') — die alte Sperre galt den kaputt gezaehlten Alt-Domains; asurascans.com lebt
    # mit sauberen /chapter/{n}-URLs. Auch aus data/sources.json 'dead' entfernt (Vereinigung!).
    "automanga", "bato.si", "comick.dev", "ineptbastards", "kunmanga",
    "fascans", "mangarock", "manhwaclan", "mangasushi", "zeroscan", "ninjascans", "readheroacademia",
    "valhalla", "trashscanlation", "lhtranslation", "1stkissmanga", "arangscans", "kissmanga",
    "merakiscans", "immanitys", "wuxiaworld",
    # "mgeko" entfernt (JB-Fund 2026-07: mgeko.cc lebt, Kapitel-Links bestehen den Identitaets-Check)
    "inkr",        # comics.inkr.com = KAUF-Seite, kein Reader (JB-Fund: fuehrte auf Aposimz-Shop)
    # Interstitial-Netzwerk (JB-Fund: vinlandsagamanga.net -> "click to read" -> jjk0.com mit
    # FALSCHEM Slug 'jujutsu-kaisen-...' fuer Vinland-Kapitel -> maximal verwirrend, nie verlinken)
    "vinlandsagamanga", "jjk0",
)


# TEMPORAER pausierte Reader (JB Runde 36: MangaFire-Umbau, 1-3 Tage Platzhalter-Redirects,
# fuer Skripte hinter Cloudflare unsichtbar -> automatisch NICHT erkennbar). Wirkt NUR auf
# die ANZEIGE (render zeigt die erste lebende Reserve; Cache/Links bleiben unangetastet) —
# Eintrag in data/sources.json "paused" setzen, nach dem Umbau wieder entfernen. Anders als
# "dead" wird die Liste ERSETZT statt vereinigt (Pause ist ein Zustand, keine Sperre).
PAUSED_READERS = ()
# AUTOMATISCH pausierte Reader (JB Runde 38, Feature 1): der Reader-Check (readers.
# refresh_status) stuft einen Haupt-Host als 'down'/'maintenance' ein -> Auto-Pause, bis
# derselbe Check wieder 'ok' meldet (selbstheilend, nicht-destruktiv — Cache unangetastet).
PAUSED_AUTO = ()


def set_auto_paused(hosts):
    """Auto-Pausen setzen/aufheben (Aufrufer: readers.refresh_status + render-Start)."""
    global PAUSED_AUTO
    PAUSED_AUTO = tuple(sorted({(h or "").lower() for h in (hosts or []) if h}))


def all_paused():
    """Manuelle + automatische Pausen vereint (fuer Anzeige/JS-Default)."""
    return tuple(dict.fromkeys(tuple(PAUSED_READERS) + tuple(PAUSED_AUTO)))


def alt_sites(country):
    return ALT_MANHWA if country in ("Korea", "China") else ALT_MANGA


def is_dead_reader(site):
    """True, wenn der Host zu einer bekannten toten/kaputten Reader-Domain gehoert."""
    s = (site or "").lower()
    return any(d in s for d in DEAD_READERS)


def is_paused_reader(site):
    """True, wenn der Host pausiert ist — manuell (PAUSED_READERS) oder automatisch
    (PAUSED_AUTO, Reader-Check meldet down/maintenance)."""
    s = (site or "").lower()
    return any(p in s for p in PAUSED_READERS) or any(p in s for p in PAUSED_AUTO)


def load_sources(path):
    """sources.json -> {"manga": [(name, domain), …], "manhwa": [...]}.

    Self-updatebarer Reader-Vorrat (ersetzt die eingebauten ALT_*-Listen zur Laufzeit).
    Fehlt/defekt die Datei -> {} (Aufrufer behaelt die Defaults; nie versiegen)."""
    import json
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return {}
    out = {}
    for key in ("manga", "manhwa"):
        rows = data.get(key) if isinstance(data, dict) else None
        if isinstance(rows, list):
            pairs = [tuple(r) for r in rows if isinstance(r, (list, tuple)) and len(r) == 2]
            if pairs:
                out[key] = pairs
    dead = data.get("dead") if isinstance(data, dict) else None
    if isinstance(dead, list):
        out["dead"] = tuple(str(d).lower() for d in dead if d)
    paused = data.get("paused") if isinstance(data, dict) else None
    if isinstance(paused, list):                     # leere Liste zaehlt (Pause AUFHEBEN)
        out["paused"] = tuple(str(p).lower() for p in paused if p)
    return out


def apply_sources(data):
    """Geladene Reader-Quellen in die Modul-Listen uebernehmen (Standalone-Start).

    WICHTIG: `dead` wird VEREINIGT, nie ersetzt (Wurzel-Bug, JB-Saga vinlandsagamanga: eine
    veraltete sources.json ueberschrieb die eingebaute Sperrliste -> alle neuen Sperren waren
    zur Laufzeit wirkungslos und Interstitial-Links kamen zurueck). Eingebaute Sperren gelten
    IMMER; die Datei kann nur ergaenzen. Entsperren = Eintrag in config.py UND Datei entfernen."""
    global ALT_MANGA, ALT_MANHWA, DEAD_READERS, PAUSED_READERS
    if data.get("manga"):
        ALT_MANGA = list(data["manga"])
    if data.get("manhwa"):
        ALT_MANHWA = list(data["manhwa"])
    if data.get("dead"):
        DEAD_READERS = tuple(dict.fromkeys(tuple(DEAD_READERS) + tuple(data["dead"])))
    if "paused" in data:                             # ERSETZEN, nicht vereinigen (temporaerer
        PAUSED_READERS = tuple(data["paused"])       # Zustand; leere Liste hebt die Pause auf)


def load_overrides(path):
    """overrides.json (reine DATEN) laden -> {key: {"name":…, "search":…}}.

    Ersetzt das fruehere hartcodierte NAME_FIX. Key = norm(Name aus Verlauf/Lesezeichen);
    bewusst VERBATIM uebernommen (kein erneutes norm), damit gesetzte Keys nicht kollidieren.
    Akzeptiert {"overrides": {...}} oder direkt {...}. Fehlt/defekt -> {} (kein Fehler, der Lauf
    laeuft weiter; im Zweifel keine Korrektur statt falsche Korrektur).
    """
    import json
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return {}
    raw = data.get("overrides", data) if isinstance(data, dict) else {}
    out = {}
    for key, val in (raw or {}).items():
        if not isinstance(val, dict):
            continue
        # Ein Eintrag zaehlt, wenn er die Anreicherung steuert: name/search, mb_id-Pin, hide, author.
        if (val.get("name") or val.get("search") or val.get("mb_id") or val.get("hide")
                or val.get("author")):
            name = val.get("name", "")
            entry = {"name": name, "search": val.get("search") or name}
            if val.get("mb_id"):               # Ground-Truth-Pin: Match FEST auf diese MangaBaka-ID
                entry["mb_id"] = val["mb_id"]
            if val.get("type"):                # optionaler Typ-Hint (Flagge), falls DB nichts findet
                entry["type"] = val["type"]
            if val.get("baka"):                # erzwungene MangaBaka-ID -> Baka-Pill/Link korrekt
                entry["baka"] = val["baka"]
            if val.get("author"):              # Autor als DATUM (Webtoon-Originale, die von der
                entry["author"] = val["author"]   # Plattform verschwunden sind -> kein Fetch moeglich)
            if val.get("hide"):                # kein Manga/Doujin/Novel -> aus der Liste entfernen
                entry["hide"] = True
            out[key] = entry
    return out


def save_override(path, key, name, search=None):
    """Eine Titel-Korrektur in overrides.json schreiben (nicht-destruktiv).

    Laedt die bestehende Datei, ergaenzt/ueberschreibt NUR den einen Key (alle anderen
    Eintraege und der _doc-Kommentar bleiben erhalten) und schreibt sie zurueck. `key` wird
    VERBATIM gesetzt (kein norm). Gibt das gespeicherte {"name","search"} zurueck.
    Das ist die Datei-Haelfte des "Braucht Hilfe"-Flows (Spec §2a) — reine Nutzer-Daten."""
    import os
    import json
    if not (key and name):
        raise ValueError("save_override braucht key und name")
    data = {}
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        data = {}
    if not isinstance(data, dict):
        data = {}
    data.setdefault("_doc", "Seltene Titel-Korrekturen (reine DATEN, kein Code). "
                            "Key = norm(Name aus Verlauf/Lesezeichen). VERBATIM, kein erneutes norm.")
    ov = data.get("overrides")
    if not isinstance(ov, dict):
        ov = {}
        data["overrides"] = ov
    entry = {"name": name, "search": search or name}
    ov[key] = entry
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)            # atomar ersetzen -> kein halb-geschriebenes overrides.json
    return entry


# Standalone-Einstellungen (config.json der eigenstaendigen App). Bewusst getrennt von JBs
# Mail-config.json (archive_dir/interval) — die wird nie angefasst.
# auto_update: True = die exe installiert neue Releases nach dem Sync selbst;
# False (Default) = nur Tray-Hinweis, der Nutzer installiert per Menueklick.
SETTINGS_DEFAULTS = {"lang": None, "out_dir": None, "update_channel": "stable",
                     "auto_update": False}


def load_settings(path):
    """Standalone-Settings laden -> Defaults, ueberschrieben von der Datei (fehlt/defekt -> Defaults)."""
    import json
    out = dict(SETTINGS_DEFAULTS)
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            out.update({k: v for k, v in data.items()})
    except (OSError, ValueError):
        pass
    return out


def save_settings(path, settings):
    """Settings atomar schreiben (tmp + os.replace). Gibt das geschriebene Dict zurueck."""
    import os
    import json
    data = {**SETTINGS_DEFAULTS, **(settings or {})}
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)
    return data
