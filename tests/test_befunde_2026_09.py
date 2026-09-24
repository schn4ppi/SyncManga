# -*- coding: utf-8 -*-
"""Regressionstests zu den Befunden vom 24.09.2026 (Vergleich SyncManga <-> SyncFindus).

Jeder Test haelt einen Fehler fest, der vorher nachweislich auftrat. Kein Netz, keine echten
Nutzerdaten; Dateien nur unter tmp_path. Lauf:  python -m pytest tests -q   (Python >= 3.12,
render.py nutzt verschachtelte f-Strings). Die JS-Tests laufen nur, wenn `node` vorhanden ist.
"""
import io
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import urllib.error

import pytest

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from syncmanga import config, enrich, readerlink, update  # noqa: E402
from syncmanga.parse import (  # noqa: E402
    chapter_of, clean_title, key_ratio, series_from, sim_norm, slug_from_url,
)


# ---------------- XSS: eingebettetes JSON (render._js) ----------------

def test_js_maskiert_script_ende_und_bleibt_gleicher_wert():
    from syncmanga.render import _js
    obj = {"t": "</script><svg onload=alert(1)>", "z": "a b & c"}
    out = _js(obj)
    assert "</script" not in out and "<" not in out and ">" not in out
    assert " " not in out and "&" not in out
    assert json.loads(out) == obj                    # derselbe JS-/JSON-Wert


def test_statistik_escaped_typ_aus_fremder_datenbank():
    from syncmanga import i18n
    from syncmanga.render import stats_panel
    rows = [{"name": "X", "type": "<img src=x onerror=alert(1)>", "chap": 3}]
    html_out = stats_panel(rows, {}, i18n.strings("de"))
    assert "<img" not in html_out and "&lt;img" in html_out


# ---------------- Titel-Parser (G1) ----------------

@pytest.mark.parametrize("titel,erwartet", [
    ("Blue Lock Chapter 250 | Weeb Central", "Blue Lock"),        # Pipe-Regel: war 'Weeb Central'
    ("Berserk Chapter 350 | TCB Scans", "Berserk"),
    ("Kaiju No. 8 - Ch. 100 - MangaDex", "Kaiju No. 8"),         # war 'Kaiju No'
    ("Zom 100 Chapter 5", "Zom 100"),                              # war 'Zom'
    ("Mob Psycho 100 Chapter 3", "Mob Psycho 100"),
    ("Class 1-9 Chapter 5", "Class 1-9"),                          # war 'Class'
    ("One Piece Vol. 3 Chapter 20", "One Piece"),
    ("Episode 12 | Tower of God", "Tower of God"),                 # bleibt richtig
    ("Solo Leveling Chapter 57", "Solo Leveling"),
    ("Naruto 700", "Naruto"),                                       # nackte End-Nummer = Kapitel
    ("Vol. 1 Ch. 5 | Blue Lock", "Blue Lock"),                      # Band vor der Kapitel-Marke
])
def test_clean_title(titel, erwartet):
    assert clean_title(titel) == erwartet


# ---------------- Kapitel-Token mit Wortgrenze (G2) ----------------

@pytest.mark.parametrize("url,kapitel", [
    ("https://x.com/manga/switch-2-1/chapter-40/", 40.0),          # war 2.1
    ("https://x.com/chapter/1-2-prince-chapter-7/", 7.0),          # war 1.2
    ("https://x.com/chapter/2-5-dimensional-seduction-chapter-150/", 150.0),   # war 2.5
    ("https://x.com/chapter/1000-yen-hero-chapter-7/", 7.0),       # war 1000
    ("https://x.com/manga/one-piece/chapter-953-5/", 953.5),       # Bindestrich-Dezimale bleibt
    ("https://mgeko.cc/reader/en/solo-leveling-chapter-57-eng/", 57.0),
    ("https://x.com/manga/y/chapter-100th/", 100.0),               # kein Zurueckschneiden auf 10
    ("https://x.com/manga/y/chapter-5eng/", 5.0),
])
def test_chapter_of(url, kapitel):
    assert chapter_of(url, "") == kapitel


@pytest.mark.parametrize("url,slug", [
    ("https://x.com/manga/the-witch-2/chapter-9", "The Witch 2"),  # war 'The Wit'
    ("https://x.com/manga/rich-2-life/chapter-3/", "Rich 2 Life"),  # war verloren
])
def test_slug_behaelt_ch_im_wort(url, slug):
    assert slug_from_url(url) == slug


def test_series_from_weeb_central_ist_keine_serie():
    name, ch = series_from("https://weebcentral.com/chapters/01J76XYCH2B6ABC",
                           "Blue Lock Chapter 250 | Weeb Central")
    assert name == "Blue Lock" and ch == 250.0


# ---------------- Aehnlichkeit mit leerem Schluessel (G3) ----------------

def test_leere_seite_ist_nie_aehnlich():
    assert key_ratio("", "") == 0.0
    assert key_ratio(sim_norm("影栗の姫"), sim_norm("俺だけレベルアップな件")) < 0.5
    assert key_ratio(sim_norm("Solo Leveling"), sim_norm("solo-leveling")) == 1.0
    assert sim_norm("Solo Leveling") == "sololeveling"          # lateinisch: exakt wie norm()
    assert key_ratio(sim_norm("影栗の姫 2"), sim_norm("俺だけレベルアップな件 2")) < 0.5   # nicht nur '2' 


def test_mb_search_cjk_trifft_nicht_die_beliebteste_serie(monkeypatch):
    from syncmanga import catalog
    fake = {"data": [
        {"id": 1, "title": "Solo Leveling", "native_title": "나 혼자만 레벨업", "state": "active"},
        {"id": 2, "title": "Kagekuri no Hime", "native_title": "影栗の姫", "state": "active"},
    ]}
    monkeypatch.setattr(catalog, "_mb_fetch", lambda path: fake)
    _rec, conf = catalog.mb_search("影栗の姫")
    assert conf == 1.0                                             # der ECHTE Treffer
    _rec, conf = catalog.mb_search("완전히 다른 제목")
    assert conf < 0.5                                              # war 1.0 fuer jeden Kandidaten


# ---------------- Reader-Pruefung: Timeout ist kein 'gibt es nicht' (S3) ----------------

class _NoPacer:
    def wait(self):
        pass


@pytest.mark.parametrize("fehler,erwartet", [
    (urllib.error.URLError("timed out"), "down"),
    (TimeoutError("timed out"), "down"),
    (urllib.error.HTTPError("u", 500, "x", {}, io.BytesIO()), "down"),
    (urllib.error.HTTPError("u", 404, "x", {}, io.BytesIO()), "no"),
    (urllib.error.HTTPError("u", 403, "x", {}, io.BytesIO()), "blocked"),
    (urllib.error.URLError(socket.gaierror(-2, "Name or service not known")), "gone"),   # tote Domain
    (urllib.error.URLError(ConnectionRefusedError(111, "refused")), "gone"),
    (ConnectionResetError(104, "reset"), "down"),
])
def test_alive_status_trennt_netzfehler_von_404(monkeypatch, fehler, erwartet):
    monkeypatch.setattr(readerlink, "READER_PACER", _NoPacer())

    def boom(*a, **k):
        raise fehler
    monkeypatch.setattr(readerlink.urllib.request, "urlopen", boom)
    assert readerlink._alive_status("https://reader.example/manga/x/chapter-1/") == erwartet


def test_verify_reader_dreiwertig():
    rd = {"host": "r.example", "type": "manga", "chapter": "https://r.example/{slug}/chapter-{n}/"}
    assert readerlink.verify_reader(rd, probe=lambda u: "down") is None       # Netz weg -> bleibt
    assert readerlink.verify_reader(rd, probe=lambda u: "blocked") is None    # Cloudflare -> bleibt
    assert readerlink.verify_reader(rd, probe=lambda u: "no") is False
    echt = lambda u: "ok" if ("zzqx" not in u and "99999" not in u) else "no"  # noqa: E731
    assert readerlink.verify_reader(rd, probe=echt) is True
    assert readerlink.verify_reader(rd, probe=lambda u: "ok") is False        # Soft-404-Reader
    # tote Domain: ohne Netz-Nachweis nicht pruefbar, mit Netz-Nachweis tot
    assert readerlink.verify_reader(rd, probe=lambda u: "gone") is None
    assert readerlink.verify_reader(rd, probe=lambda u: "gone", netz=True) is False


def test_link_sweep_wertet_tote_domain_nur_bei_funktionierendem_netz(tmp_path):
    from syncmanga import readers
    cache = {f"s{i}": {"title": f"S{i}", "read_urls": [[f"https://h{i}.example/manga/s/chapter-1/", "x"]]}
             for i in range(4)}
    cp = tmp_path / "md_cache.json"
    cp.write_text(json.dumps(cache), encoding="utf-8")
    st = str(tmp_path / "reader_status.json")
    readers.link_sweep(str(cp), str(tmp_path), n=4, check=lambda u: "gone", status_out=st)
    assert not (tmp_path / "broken_links.json").exists()           # alles 'gone' = eigenes Netz weg
    readers.link_sweep(str(cp), str(tmp_path), n=4,
                       check=lambda u: "ok" if "h0." in u else "gone", status_out=st)
    gemeldet = json.load(open(tmp_path / "broken_links.json", encoding="utf-8"))
    assert len(gemeldet) == 3 and all(x["h"].startswith("n:") for x in gemeldet)


# ---------------- Opake Kapitel-IDs nie als {n}-Vorlage (S1) ----------------

@pytest.mark.parametrize("url,opak", [
    ("https://mangafire.to/title/one-piece.x/chapter/4807126", True),
    ("https://mangadex.org/chapter/3f2a1b4c-1234-4abc-9def-0123456789ab", True),
    ("https://mgeko.cc/reader/en/solo-leveling-chapter-57/", False),
    ("https://comix.to/title/x/7468952-chapter-8", False),        # comix: Nummer steht im Token
    ("https://x.com/abc-chapter-2-x/chapter/4807126", True),      # letzter Treffer zaehlt
])
def test_ist_opake_kapitel_id(url, opak):
    assert readerlink.ist_opake_kapitel_id(url) is opak


def test_save_series_override_pinnt_opake_id_unveraendert(tmp_path):
    p = str(tmp_path / "series_overrides.json")
    u = "https://mangafire.to/title/one-piece.x/chapter/4807126"
    e = readerlink.save_series_override(p, "onepiece", "One Piece", u)
    assert e["chapter"] == u and "{n}" not in e["chapter"]


def test_vorlage_und_tausch_nehmen_den_letzten_treffer():
    assert (readerlink._templatize_chapter("https://x.com/chapter/1-2-prince-chapter-7/")
            == "https://x.com/chapter/1-2-prince-chapter-{n}/")
    assert (readerlink.swap_chapter("https://x.com/chapter/1-2-prince-chapter-7/", 9)
            == "https://x.com/chapter/1-2-prince-chapter-9/")


def test_save_override_merged_statt_ersetzt(tmp_path):
    p = str(tmp_path / "overrides.json")
    json.dump({"overrides": {"evolutionbeginswithbigtree": {
        "name": "Evolution Begins With a Big Tree", "baka": 910, "type": "manhua"}}},
        open(p, "w", encoding="utf-8"))
    config.save_override(p, "evolutionbeginswithbigtree", "Evolution Begins With a Big Tree", mb_id=4711)
    e = json.load(open(p, encoding="utf-8"))["overrides"]["evolutionbeginswithbigtree"]
    assert e["type"] == "manhua" and e["mb_id"] == 4711
    # baka folgt dem neuen Pin — sonst gewaenne in assemble_rows die ALTE ID (baka or mb_id)
    assert e["baka"] == 4711
    rows = enrich.assemble_rows({"evolutionbeginswithbigtree": {"name": "evo", "chap": 1, "lv": 0}},
                                {}, config.load_overrides(p))
    assert rows[0]["md_id"] == "mb:4711"


# ---------------- data-h statt Titel (S1/S2) ----------------

CACHE = {
    "dungeonmeshi": {"title": "Delicious in Dungeon", "md_id": "mb:2721"},
    "sololeveling": {"title": "Solo Leveling", "md_id": "mb:9", "id_hist": ["al:105398"]},
    "ohneid": {"title": "Ohne ID"},
}


@pytest.mark.parametrize("h,keys", [
    ("mb:2721", ["dungeonmeshi"]),
    ("al:105398", ["sololeveling"]),        # fruehere ID (id_hist) trifft weiter
    ("n:ohneid", ["ohneid"]),
    ("n:gibtsnicht", []),
    ("dungeonmeshi", ["dungeonmeshi"]),     # Altbestand: direkter Cache-Key
    ("", []),
])
def test_cache_keys_for_h(h, keys):
    assert enrich.cache_keys_for_h(CACHE, h) == keys


def test_cache_keys_for_h_heutige_id_vor_frueherer():
    cache = {"yserie": {"md_id": "mb:7", "id_hist": ["mb:500"]}, "xserie": {"md_id": "mb:500"}}
    assert enrich.cache_keys_for_h(cache, "mb:500") == ["xserie"]


def test_assemble_rows_veraendert_id_hist_im_cache_nicht():
    cache = {"a": {"title": "A", "md_id": "mb:1", "id_hist": ["al:1"], "v": 99},
             "b": {"title": "A", "md_id": "mb:1", "id_hist": ["al:2"], "v": 99}}
    items = {"a": {"name": "A", "chap": 1, "lv": 0, "url": "https://x/a/chapter-1"},
             "b": {"name": "A", "chap": 2, "lv": 0, "url": "https://x/a/chapter-2"}}
    rows = enrich.assemble_rows(items, cache, {})
    assert sorted(rows[0]["id_hist"]) == ["al:1", "al:2"]
    assert cache["a"]["id_hist"] == ["al:1"] and cache["b"]["id_hist"] == ["al:2"]


def test_quellen_bestaetigung_schreibt_unter_cache_key(tmp_path):
    sys.path.insert(0, ROOT)
    from tools import apply_source_confirms as asc
    nf, so = str(tmp_path / "overrides.json"), str(tmp_path / "series_overrides.json")
    json.dump({"overrides": {"dungeonmeshi": {"name": "Dungeon Meshi (Delicious in Dungeon)", "baka": 2721}}},
              open(nf, "w", encoding="utf-8"))
    confirms = {
        # Liste schickt data-h + kleingeschriebenen Anzeigetitel (data-n)
        "mb:2721": {"mb_id": 2721, "name": "delicious in dungeon"},
        "mb:9": {"url": "https://mangafire.to/title/solo-leveling.x/chapter/4807126",
                 "name": "solo leveling", "site": "mangafire.to"},
    }
    assert asc.apply_confirms(confirms, CACHE, namefix=nf, overrides=so) == 2
    ov = json.load(open(nf, encoding="utf-8"))["overrides"]
    assert "deliciousindungeon" not in ov                               # frueher: norm(data-n)
    assert ov["dungeonmeshi"]["mb_id"] == 2721 and ov["dungeonmeshi"]["baka"] == 2721
    assert ov["dungeonmeshi"]["name"] == "Dungeon Meshi (Delicious in Dungeon)"   # kuratiert bleibt
    so_ov = json.load(open(so, encoding="utf-8"))["overrides"]
    assert so_ov["sololeveling"]["chapter"].endswith("/chapter/4807126")   # opak: keine {n}-Vorlage
    assert so_ov["sololeveling"]["name"] == "Solo Leveling"


def _mig(tmp_path, items, cache):
    from syncmanga import render
    rows = enrich.assemble_rows(items, cache, {})
    out = str(tmp_path / "out")
    render.render(rows, out, os.path.join(out, "l.html"), lang="de")
    html_out = open(os.path.join(out, "l.html"), encoding="utf-8").read()
    return json.loads(re.search(r"var MIG=(\{.*?\});", html_out).group(1))


def test_render_mig_kennt_fruehere_id_aber_nie_einen_lebenden_schluessel(tmp_path):
    """id_hist landet als Alias in MIG — ausser er ist selbst der Schluessel einer anderen Zeile."""
    solo = {"title": "Solo Leveling", "md_id": "mb:9", "id_hist": ["al:105398"], "v": 99}
    items = {"solo": {"name": "Solo Leveling", "chap": 5, "lv": 0}}
    assert _mig(tmp_path / "a", items, {"solo": solo})["al:105398"] == "mb:9"
    items["alt"] = {"name": "Alt ID", "chap": 1, "lv": 0}
    mig = _mig(tmp_path / "b", items, {"solo": solo, "alt": {"title": "Alt ID", "md_id": "al:105398", "v": 99}})
    assert "al:105398" not in mig                                  # lebender Schluessel bleibt, wo er ist


# ---------------- Updater: nicht vom exe-Asset abhaengig (S11a) ----------------

def _asset(name, size=6 * 2 ** 20):
    return {"name": name, "size": size, "digest": "sha256:" + "a" * 64,
            "browser_download_url": f"https://github.com/{update.REPO}/releases/download/v9/{name}"}


def test_release_nur_mit_setup_ist_verfuegbar():
    info = update.check_release("0.4.4", lambda: {"tag_name": "v.0.5.0",
                                                   "assets": [_asset("SyncManga-Setup.exe")]})
    assert info["available"] is True and info["setup_url"] and not info["exe_url"]


def test_release_ohne_passendes_asset_ist_nicht_verfuegbar():
    info = update.check_release("0.4.4", lambda: {"tag_name": "v.0.5.0", "assets": [_asset("readme.txt")]})
    assert info["available"] is False


def test_tray_meldet_setup_hinweis_einmal_und_ohne_installiert_meldung(monkeypatch):
    import threading

    from syncmanga import tray
    info = {"available": True, "version": "0.5.0", "exe_url": "", "setup_url": "https://x/s.exe"}
    monkeypatch.setattr(update, "check_release", lambda *a: info)
    monkeypatch.setattr(update, "programm_exe", lambda *a: ("C:/SyncManga/SyncManga.exe", ""))
    monkeypatch.setattr(update, "installiert_via_setup", lambda *a: False)
    msgs = []

    class Fake:
        lang, settings, busy = "de", {"auto_update": True}, threading.Lock()
        _upd_seen = _update_pending = ""
        _notify = lambda self, t: msgs.append(t)  # noqa: E731
        _refresh_icon = lambda self: None  # noqa: E731
    f = Fake()
    for _ in range(3):
        tray.TrayApp._self_update(f)
    assert len(msgs) == 1 and "Installer" in msgs[0]


def test_i18n_kennt_setup_hinweis_in_beiden_sprachen():
    from syncmanga import i18n
    for lang in ("de", "en"):
        assert "{v}" in i18n.strings(lang)["upd_need_setup"]


# ---------------- list.js: chapFix + Kapitel-Token (S4/G2) ----------------

def _js_funcs(*names):
    src = open(os.path.join(ROOT, "syncmanga", "templates", "list.js"), encoding="utf-8").read()
    out = []
    for n in names:
        m = re.search(r"^function " + n + r"\(.*$", src, re.M)
        assert m, n
        out.append(m.group(0))
    return "\n".join(out)


def _node(code):
    if not shutil.which("node"):
        pytest.skip("node nicht installiert")
    r = subprocess.run(["node", "-e", code], capture_output=True, text=True, timeout=30)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout)


def test_chapfix_neuerer_scan_gewinnt():
    code = _js_funcs("cfN", "scanRc", "cfLive") + """
function tr(rc){return {dataset:{rc:String(rc)},querySelector:function(){return {dataset:{}}}}}
console.log(JSON.stringify([
  cfLive({n:50,b:50}, tr(50)),   // Scan steht noch -> Handwert gilt
  cfLive({n:50,b:50}, tr(70)),   // danach bis 70 gelesen -> Scan gewinnt (war: fuer immer 50)
  cfLive({n:60,b:50}, tr(55)),   // am Handy weiter als der Scan -> Handwert bleibt
  cfLive({n:20,b:100}, tr(100)), // Korrektur nach unten gilt, solange der Scan steht
  cfLive(3, tr(5)),              // Alt-Zahl unter dem Scan: bleibt (wird zu {n:3,b:5}), nie geloescht
  cfLive(50, tr(40))             // Alt-Zahl ueber dem Scan -> gilt
]))"""
    assert _node(code) == [True, False, True, True, True, True]


def test_cfrelink_ersetzt_nur_das_letzte_eigene_token():
    code = _js_funcs("cfTok") + """
function rel(u,n){var t=cfTok(u);if(!t)return u;var st=t.index+t[1].length+t[2].length;return u.slice(0,st)+n+u.slice(st+t[3].length)}
console.log(JSON.stringify([
  rel('https://x.com/manga/the-witch-2/chapter-5/','9'),
  rel('https://weebcentral.com/chapters/01J76XYCH2B6ABC','9'),
  rel('https://x.com/chapter/1-2-prince-chapter-7/','9'),
  rel('https://x.com/manga/y/chapter-100th/','9')
]))"""
    assert _node(code) == ["https://x.com/manga/the-witch-2/chapter-9/",
                           "https://weebcentral.com/chapters/01J76XYCH2B6ABC",
                           "https://x.com/chapter/1-2-prince-chapter-9/",
                           "https://x.com/manga/y/chapter-9th/"]
