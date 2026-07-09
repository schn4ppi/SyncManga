# -*- coding: utf-8 -*-
"""Online-Zugriff fuer die Standalone-App (JB Phase 3, 09.07.2026): anonymes Konto auf JBs
Sync-Cloud (manga.j-bk.org) — die App registriert sich einmal und laedt danach nach jedem
Sync ihre Leseliste hoch, damit der Nutzer sie am Handy sieht.

Datensparsam & harmlos: KEINE E-Mail, kein Login-Konto. Der Server vergibt zufaellig
Slot + Upload-Key + Zugangscode; hochgeladen wird NUR die fertige Leseliste (Titel +
Lese-Fortschritt), niemals Verlauf/Lesezeichen/Browser-Daten. Die Zugangsdaten liegen im
Windows-Tresor (keyring) — faellt der aus, in `data/cloud.json` (eigener PC, geringe Stakes).

Alles hier ist rein/injizierbar (http/store) -> ohne Netz testbar. Fehler brechen NIE einen
Sync ab: die Funktionen geben (ok, info) zurueck und werfen nicht nach aussen.
"""
import json
import os
import urllib.request

BASE = "https://manga.j-bk.org"
UA = "SyncManga-App/1.0 (+https://j-bk.org)"
_SERVICE, _USER = "SyncManga-Cloud", "account"


# ---------------- Zugangsdaten speichern/lesen (Tresor bevorzugt, Datei als Rueckfall) --------
def _store_path(data_dir):
    return os.path.join(data_dir, "data", "cloud.json")


def save_account(data_dir, acc):
    """{slot, upload_key, code} sichern. Erst Windows-Tresor, dann Datei (best-effort)."""
    try:
        import keyring
        keyring.set_password(_SERVICE, _USER, json.dumps(acc))
        return
    except Exception:
        pass
    p = _store_path(data_dir)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(acc, f, ensure_ascii=False)
    os.replace(tmp, p)


def load_account(data_dir):
    """Gespeicherte {slot, upload_key, code} oder None."""
    try:
        import keyring
        raw = keyring.get_password(_SERVICE, _USER)
        if raw:
            return json.loads(raw)
    except Exception:
        pass
    try:
        return json.load(open(_store_path(data_dir), encoding="utf-8"))
    except (OSError, ValueError):
        return None


# ---------------- HTTP (injizierbar) ----------------
def _http(method, path, headers=None, body=None, timeout=60):
    req = urllib.request.Request(BASE + path, data=body, method=method,
                                 headers={"User-Agent": UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.status, resp.read()


# ---------------- Aktionen ----------------
def register(data_dir, http=_http):
    """Anonymes Konto anlegen + sichern -> (ok, account_or_fehlertext). Idempotent-freundlich:
    ein bereits vorhandenes Konto wird NICHT ueberschrieben (gleiche Slot-URL behalten)."""
    have = load_account(data_dir)
    if have and have.get("slot") and have.get("upload_key"):
        return True, have
    try:
        status, raw = http("POST", "/api/register",
                           {"Content-Type": "application/json"}, b"{}")
        data = json.loads(raw or b"{}")
    except Exception as ex:
        return False, f"Registrierung nicht moeglich ({type(ex).__name__})."
    if status != 200 or not data.get("ok"):
        return False, data.get("err") or "Registrierung abgelehnt."
    acc = {"slot": data["slot"], "upload_key": data["upload_key"],
           "code": data["code"], "url": data.get("url") or BASE}
    save_account(data_dir, acc)
    return True, acc


def upload(data_dir, html_path, http=_http):
    """Die Leseliste zum eigenen Slot hochladen -> (ok, info). Ohne Konto/Datei = stiller Skip
    (ok=False, 'nicht eingerichtet'); NIE eine Exception nach aussen (Sync laeuft weiter)."""
    acc = load_account(data_dir)
    if not acc or not acc.get("upload_key") or not acc.get("slot"):
        return False, "nicht eingerichtet"
    try:
        body = open(html_path, "rb").read()
    except OSError:
        return False, "keine Liste"
    if len(body) < 200:
        return False, "Liste leer"
    try:
        status, raw = http("POST", "/api/upload",
                           {"Authorization": "Bearer " + acc["upload_key"],
                            "X-Slot": acc["slot"],
                            "Content-Type": "text/html; charset=utf-8"}, body)
        data = json.loads(raw or b"{}")
    except Exception as ex:
        return False, f"Upload gerade nicht moeglich ({type(ex).__name__})"
    if status == 200 and data.get("ok"):
        return True, f"{data.get('bytes', 0):,} Bytes -> {acc.get('url') or BASE}"
    return False, data.get("err") or f"HTTP {status}"


def change_code(data_dir, wish=None, http=_http):
    """Zugangscode aendern (JB 09.07.2026). `wish`=None -> Server wuerfelt einen neuen; sonst
    Wunschcode (Server prueft Laenge/Eindeutigkeit). Der alte Code wird ungueltig. Gibt
    (ok, code_or_fehlertext) zurueck und speichert den neuen Code lokal. Ohne Konto -> Skip."""
    acc = load_account(data_dir)
    if not acc or not acc.get("upload_key") or not acc.get("slot"):
        return False, "nicht eingerichtet"
    payload = json.dumps({"code": wish} if wish else {}).encode()
    try:
        status, raw = http("POST", "/api/setcode",
                           {"Authorization": "Bearer " + acc["upload_key"],
                            "X-Slot": acc["slot"], "Content-Type": "application/json"}, payload)
        data = json.loads(raw or b"{}")
    except Exception as ex:
        return False, f"gerade nicht moeglich ({type(ex).__name__})"
    if status == 200 and data.get("ok") and data.get("code"):
        acc["code"] = data["code"]
        save_account(data_dir, acc)
        return True, data["code"]
    return False, data.get("err") or f"HTTP {status}"


def is_enabled(settings):
    """Nutzer hat den Online-Zugriff im Tray aktiviert?"""
    return bool((settings or {}).get("cloud_enabled"))


def info_html(acc, lang="de"):
    """Kleine Info-Seite mit Zugangscode + Link (die App oeffnet sie nach dem Aktivieren).
    Zeigt den Code GROSS zum Abtippen am Handy; rein statisch, kein Netz."""
    code = (acc or {}).get("code", "—")
    url = (acc or {}).get("url", BASE)
    de = lang != "en"
    t = {
        "title": "Online-Zugriff aktiv" if de else "Online access enabled",
        "lead": "Öffne diese Seite auf deinem Handy und gib den Code ein:"
                if de else "Open this page on your phone and enter the code:",
        "codelbl": "Dein Zugangscode" if de else "Your access code",
        "note": ("Nach jedem Sync lädt die App deine Liste automatisch hoch. "
                 "Es werden nur Titel + Lesestand übertragen — keine Browser-Daten. "
                 "Zum Abschalten: Tray-Menü → Online-Zugriff.")
        if de else ("After each sync the app uploads your list automatically. "
                    "Only titles + progress are sent — no browser data. "
                    "To turn it off: tray menu → Online access."),
        "open": "Zur Online-Liste" if de else "Open online list",
    }
    return f"""<!doctype html><html lang={"de" if de else "en"}><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1"><title>{t['title']}</title><style>
body{{font:16px/1.6 system-ui,Segoe UI,sans-serif;background:#14100d;color:#e8ddd5;
 display:flex;min-height:100vh;margin:0;align-items:center;justify-content:center}}
.card{{background:#1c1814;border:1px solid #2a2522;border-radius:14px;padding:26px;max-width:400px;text-align:center}}
h1{{color:#d67756;font-size:20px;margin:0 0 6px}}.lead{{color:#c9bdb4;font-size:14px}}
.code{{font:700 30px/1.2 ui-monospace,Consolas,monospace;letter-spacing:1px;color:#e8ddd5;
 background:#14100d;border:1px dashed #4a3f2a;border-radius:10px;padding:14px;margin:14px 0;user-select:all}}
.codelbl{{color:#8a7d74;font-size:12px;text-transform:uppercase;letter-spacing:.05em}}
a.btn{{display:inline-block;margin-top:10px;padding:11px 18px;border-radius:10px;background:#d67756;
 color:#14100d;font-weight:600;text-decoration:none}}
.note{{color:#8a7d74;font-size:12px;margin-top:16px}}
</style></head><body><div class=card>
<h1>📚 {t['title']}</h1><div class=lead>{t['lead']}</div>
<div class=codelbl>{t['codelbl']}</div><div class=code>{code}</div>
<a class=btn href="{url}" target=_blank>{t['open']} ↗</a>
<div class=note>{t['note']}</div></div></body></html>"""
