# -*- coding: utf-8 -*-
"""
Schlankes Standalone-Tray der App „SyncManga".

Linksklick = Liste öffnen. Menü: Aktualisieren · Liste öffnen · Sprache · Hilfe · Beenden.
Single-Instance (PID-Lock, neue Instanz übernimmt). Mehrsprachig über syncmanga.i18n.
Gleicher Look wie die Vollsuite: Familien-Emblem (S im Gleichdick) in Manga-GRÜN.

Aufruf:  python -m syncmanga.tray [DATENORDNER] [--lang de|en]

Die GUI (pystray/PIL/tkinter) wird manuell getestet; die reinen Helfer
(menu_labels, emblem_bild, punkt_farbe, single_instance) sind unit-getestet.
"""
import math
import os
import sys
import threading
import webbrowser

from . import __version__, config, i18n, update
from .__main__ import choose_lang, parse_args, resolve_paths, run

PKG_DIR = os.path.dirname(os.path.abspath(__file__))


# ---------------- reine, testbare Helfer ----------------

# --- Familien-Emblem (S im Gleichdick, JB 22.07.2026) -------------------------
# Geometrie aus Doku/Branding/sync_emblem.svg (Familien-Repo) — bewusst als Kopie,
# damit die giveable exe autark bleibt. Manga-Emblem = GRÜN (SCHEMA.md-Palette:
# die Emblem-Farbe folgt der Oberfläche). Sync läuft = berührend umschließender
# Gleichdick-Rahmen; hier in Familien-GOLD, denn Grün auf Grün wäre unsichtbar
# (die Vollsuite spiegelt es: Gold-Emblem + grüner Rahmen).
EMBLEM_GRUEN = (127, 176, 105)   # #7fb069
EMBLEM_RILLE = (20, 17, 16)      # #141110 (S-Rille wie im SVG)
RAHMEN_GOLD = (201, 149, 43)     # #c9952b
_ECKEN = ((10.0, 96.6), (110.0, 96.6), (60.0, 10.0))
_S_BEZIER = ((73, 34), (70, 26), (57, 23), (49, 26), (40, 29), (38, 37), (41, 44),
             (44, 51), (54, 53), (60, 55), (68, 57), (75, 61), (75, 69),
             (75, 79), (65, 85), (55, 84), (46, 83), (40, 78), (39, 71))


def punkt_farbe(dead=0):
    """Status-Punkt unten rechts (Calm): None = alles ruhig, gelb = 1-2 Datenquellen
    offline, rot = 3+ (das alte Neon-Magenta ist abgeschafft, JB 22.07.)."""
    if dead >= 3:
        return (230, 30, 30)
    if dead >= 1:
        return (235, 205, 30)
    return None


def emblem_bild(dead=0, busy=False, update_pending=False, groesse=64):
    """Tray-Symbol = Familien-Emblem, KONSTANT grün. Sync läuft = GOLD-Rahmen
    (Gleichdick-Form, minimal größer, berührend umschließend); Quellen-Zustand
    als Punkt unten rechts; Update-Badge oben rechts wie gehabt.
    `groesse`: Kantenlänge des gelieferten Bilds (64 = Tray; 256 = exe-Icon-Master)."""
    from PIL import Image, ImageDraw
    gr = 4                               # Überabtastung: gezeichnet 4x, dann verkleinert
    S = groesse * gr
    ein = S / 64.0                       # Layout-Einheit = 1 Pixel der 64er-Tray-Größe
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # Gleichdick = KONSTANTE Breite 100 in jeder Richtung -> BBox exakt 100x100
    # (x 10..110, y 10..110: unten bulgt der Bogen bis y=110); mittig einpassen.
    sk = (S - 6 * ein) / 100.0
    ox = oy = 3 * ein - 10 * sk

    def P(x, y):
        return (x * sk + ox, y * sk + oy)

    pts = []                             # drei 60°-Bögen um die jeweils dritte Ecke
    for i in range(3):
        a, b = _ECKEN[i], _ECKEN[(i + 1) % 3]
        c = _ECKEN[(i + 2) % 3]
        w0 = math.atan2(a[1] - c[1], a[0] - c[0])
        w1 = math.atan2(b[1] - c[1], b[0] - c[0])
        while w1 - w0 > math.pi:
            w1 -= 2 * math.pi
        while w1 - w0 < -math.pi:
            w1 += 2 * math.pi
        for t in range(25):
            w = w0 + (w1 - w0) * t / 24
            pts.append(P(c[0] + 100 * math.cos(w), c[1] + 100 * math.sin(w)))
    if busy:
        band = int(6 * ein)              # Band mittig auf der Kante -> außen ~3 px Rahmen
        d.line(pts + pts[:1], fill=RAHMEN_GOLD, width=band, joint="curve")
        for ecke in _ECKEN:
            x, y = P(*ecke)
            d.ellipse([x - band / 2, y - band / 2, x + band / 2, y + band / 2],
                      fill=RAHMEN_GOLD)
    d.polygon(pts, fill=EMBLEM_GRUEN)
    kurve = []                           # S-Rille: Bezier-Kette abtasten, runde Linie + Kappen
    for s0 in range(0, len(_S_BEZIER) - 3, 3):
        p0, p1, p2, p3 = _S_BEZIER[s0:s0 + 4]
        for t in range(17):
            u = t / 16.0
            v = 1 - u
            kurve.append(P(v**3 * p0[0] + 3 * v * v * u * p1[0] + 3 * v * u * u * p2[0] + u**3 * p3[0],
                           v**3 * p0[1] + 3 * v * v * u * p1[1] + 3 * v * u * u * p2[1] + u**3 * p3[1]))
    breite = int(14 * sk)
    d.line(kurve, fill=EMBLEM_RILLE, width=breite, joint="curve")
    for x, y in (kurve[0], kurve[-1]):
        r = breite / 2
        d.ellipse([x - r, y - r, x + r, y + r], fill=EMBLEM_RILLE)
    punkt = punkt_farbe(dead)
    if punkt:
        r = 11 * ein
        cx = cy = S - r - 2 * ein
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=EMBLEM_RILLE)   # dunkler Ring
        r2 = r - 2 * ein
        d.ellipse([cx - r2, cy - r2, cx + r2, cy + r2], fill=punkt)
    img = img.resize((groesse, groesse), Image.LANCZOS)
    if update_pending:
        draw_update_badge(ImageDraw.Draw(img))   # Badge NACH dem Verkleinern -> bleibt scharf
    return img


def draw_update_badge(d):
    """Kleines rotes Ausrufezeichen oben rechts aufs 64x64-Icon (JB-Regel 14.07.: Update-Badge
    fuer ALLE Tray-Programme). Eigene Ecke -> ueberdeckt das Kern-Symbol nicht. `d` = ImageDraw."""
    d.ellipse([40, 2, 62, 24], fill=(220, 45, 45), outline=(255, 255, 255), width=2)
    d.rectangle([49, 7, 53, 16], fill=(255, 255, 255))     # Ausrufezeichen-Strich
    d.rectangle([49, 18, 53, 21], fill=(255, 255, 255))    # Ausrufezeichen-Punkt


def menu_labels(lang):
    """Menü-Beschriftungen in der gewählten Sprache (rein, testbar)."""
    s = i18n.strings(lang)
    return {"update": s["tray_update"], "force": s["tray_force"], "open": s["tray_open"],
            "selfupdate": s["tray_selfupdate"], "autoupdate": s["tray_autoupdate"],
            "cloud": s["tray_cloud"], "cloud_show": s["tray_cloud_show"],
            "cloud_newcode": s["tray_cloud_newcode"],
            "language": s["tray_language"], "help": s["tray_help"], "quit": s["tray_quit"]}


def tooltip_text(busy=False, dead=0, names=None, lang="de"):
    """Sprechender Tray-Tooltip (rein, testbar): erklärt die Symbolfarbe beim Drüberfahren.

    busy -> „läuft gerade"; dead>0 -> „N Datenquelle(n) offline" (mit Namen, wenn bekannt);
    sonst „alle Datenquellen ok". Gleiche Aussage wie in der Vollsuite, hier ohne Sync-Uhrzeit
    (die Standalone-App hat keinen Zeitplan)."""
    s = i18n.strings(lang)
    if busy:
        return f"SyncManga — {s['tray_tip_running']}"
    if dead:
        who = ", ".join(n for n in (names or []) if n)
        return f"SyncManga — {s['tray_tip_dead'].format(n=dead)}" + (f": {who}" if who else "")
    return f"SyncManga — {s['tray_tip_ok']}"


def _is_own_process(tasklist_output):
    """True, wenn die tasklist-Ausgabe zu UNSERER App gehört — Python ODER die gepackte
    SyncManga.exe. So greift die Single-Instance auch im .exe-Build (nicht nur unter Python)."""
    o = (tasklist_output or "").lower()
    return "python" in o or "syncmanga" in o


def _kill_if_ours(pid):
    """Eine evtl. laufende alte Instanz beenden — NUR wenn es unsere App ist (nicht-destruktiv)."""
    try:
        import subprocess
        flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        info = subprocess.run(["tasklist", "/fi", f"PID eq {pid}"],
                              creationflags=flags, capture_output=True, text=True)
        if _is_own_process(info.stdout):
            subprocess.run(["taskkill", "/f", "/pid", pid], creationflags=flags, capture_output=True)
    except Exception:
        pass


def single_instance(lockfile):
    """Genau EINE Instanz: alte Instanz (Python ODER .exe) übernehmen, eigene PID hinterlegen."""
    try:
        if os.path.exists(lockfile):
            old = open(lockfile, encoding="utf-8").read().strip()
            if old.isdigit() and int(old) != os.getpid():
                _kill_if_ours(old)
    except Exception:
        pass
    try:
        with open(lockfile, "w", encoding="utf-8") as f:
            f.write(str(os.getpid()))
    except Exception:
        pass
    # Gleichzeitiger Doppelstart (JB-Fund: 2x Doppelklick in derselben Sekunde -> beide lebten und
    # teilten sich den Cache): kurz warten und nachlesen — steht inzwischen eine FREMDE PID in der
    # Sperrdatei, hat die andere Instanz uebernommen -> diese hier zieht sich leise zurueck.
    try:
        import time as _t
        _t.sleep(0.7)
        cur = open(lockfile, encoding="utf-8").read().strip()
        if cur.isdigit() and int(cur) != os.getpid():
            os._exit(0)
    except Exception:
        pass
    return os.getpid()


def find_readme(data_dir):
    """README für „Hilfe" finden: lokal im Datenordner, sonst die mitgelieferte (de/en je Sprache offen)."""
    for cand in (os.path.join(data_dir, "README.md"),
                 os.path.normpath(os.path.join(PKG_DIR, "..", "docs", "README.md")),
                 os.path.normpath(os.path.join(PKG_DIR, "..", "README.md"))):
        if os.path.isfile(cand):
            return cand
    return None


# ---------------- GUI ----------------

class TrayApp:
    def __init__(self, data_dir, lang=None):
        import pystray
        self.data_dir = data_dir
        self.paths = resolve_paths(data_dir)
        self.settings = config.load_settings(self.paths["settings"])
        self.lang = lang or choose_lang(None, self.settings)
        self.dead = 0
        self.dead_names = []
        self.busy = threading.Lock()
        self.lockfile = os.path.join(data_dir, "tray.lock")
        single_instance(self.lockfile)
        update.cleanup_old_exe()             # Rest eines frueheren Selbst-Updates wegputzen
        self._upd_seen = ""                  # zuletzt gemeldete neue Version (1 Hinweis je Version)
        self._update_pending = ""            # Version, fuer die das Ausrufezeichen-Badge leuchtet
        self.icon = pystray.Icon("syncmanga", self._image(), self._tooltip(), menu=self._menu())

    # ----- icon -----
    def _image(self):
        # Familien-Emblem in Manga-Grün; Lauf = Gold-Rahmen, Quellen = Punkt (JB 22.07.)
        return emblem_bild(self.dead, self.busy.locked(), bool(self._update_pending))

    def _refresh_icon(self):
        try:
            self.icon.icon = self._image()
            self.icon.title = self._tooltip()      # Farbe + erklaerender Tooltip synchron halten
        except Exception:
            pass

    def _tooltip(self):
        return tooltip_text(self.busy.locked(), self.dead, self.dead_names, self.lang)

    def _last_sync_label(self):
        """'Zuletzt: …' aus dem Zeitstempel der fertig gerenderten Liste (Datei-Wahrheit)."""
        s = i18n.strings(self.lang)
        if self.busy.locked():
            return s.get("tray_syncing", "Synchronisiert gerade …")
        try:
            import datetime as _dt
            m = _dt.datetime.fromtimestamp(os.path.getmtime(self.paths["out_html"]))
            return f'{s.get("tray_last", "Zuletzt")}: {m:%d.%m. %H:%M}'
        except OSError:
            return s.get("tray_never", "Noch nicht synchronisiert")

    # ----- menu -----
    def _menu(self):
        import pystray
        lab = menu_labels(self.lang)

        def lang_item(code, text):
            return pystray.MenuItem(text, (lambda i, it: self._set_lang(code)),
                                    checked=(lambda it, c=code: self.settings.get("lang") == c),
                                    radio=True)

        language = pystray.Menu(
            lang_item(None, "Auto"),
            lang_item("de", "Deutsch"),
            lang_item("en", "English"),
        )
        return pystray.Menu(
            # Statuszeile (JB: 'auch beim Rechtsklick sollte der letzte Scan stehen') — live aus
            # der DATEI-Wahrheit (mtime der Liste), egal wer/was den Lauf gestartet hat.
            pystray.MenuItem(lambda item: self._last_sync_label(), None, enabled=False),
            pystray.MenuItem(lab["open"], self.on_open, default=True),   # Linksklick = Liste öffnen
            pystray.MenuItem(lab["update"], self.on_update),
            pystray.MenuItem(lab["force"], self.on_force),
            pystray.MenuItem(lab["selfupdate"], self.on_selfupdate),
            pystray.MenuItem(lab["autoupdate"], self.on_autoupdate,
                             checked=lambda it: bool(self.settings.get("auto_update"))),
            # 🌐 Online-Zugriff (JB Phase 3): an = Konto anlegen + Liste nach jedem Sync hochladen;
            # der Haken zeigt den Zustand. Zweiter Menuepunkt oeffnet die Code-/Link-Seite erneut.
            pystray.MenuItem(lab["cloud"], self.on_cloud,
                             checked=lambda it: bool(self.settings.get("cloud_enabled"))),
            pystray.MenuItem(lab["cloud_show"], self.on_cloud_show,
                             visible=lambda it: bool(self.settings.get("cloud_enabled"))),
            pystray.MenuItem(lab["cloud_newcode"], self.on_cloud_newcode,
                             visible=lambda it: bool(self.settings.get("cloud_enabled"))),
            pystray.MenuItem(lab["language"], language),
            pystray.MenuItem(lab["help"], self.on_help),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(lab["quit"], self.on_quit),
        )

    def _rebuild_menu(self):
        try:
            self.icon.menu = self._menu()
            self.icon.update_menu()
        except Exception:
            pass

    # ----- actions -----
    def on_open(self, icon=None, item=None):
        html = self.paths["out_html"]
        if not os.path.isfile(html):
            # Allererster Klick (JB): SOFORT eine leere Liste rendern und oeffnen — sie zeigt den
            # Fortschrittsbalken des Erstaufbaus und laedt sich am Ende von selbst neu. Dazu die
            # Tray-Meldung, damit klar ist, was passiert.
            try:
                from .__main__ import copy_guides
                from .render import render as _render
                copy_guides(self.paths["out_dir"])
                _render([], self.paths["out_dir"], html, lang=self.lang)
            except Exception:
                pass
            try:
                self.icon.notify(i18n.strings(self.lang).get("tray_first_sync", "Building your list..."),
                                 "SyncManga")
            except Exception:
                pass
            threading.Thread(target=self._do_update, daemon=True).start()
        webbrowser.open("file:///" + html.replace("\\", "/"))

    def on_update(self, icon=None, item=None):
        threading.Thread(target=self._do_update, daemon=True).start()

    def on_force(self, icon=None, item=None):
        threading.Thread(target=self._do_update, kwargs={"force": True}, daemon=True).start()

    def on_selfupdate(self, icon=None, item=None):
        threading.Thread(target=self._self_update, kwargs={"manual": True}, daemon=True).start()

    def on_cloud(self, icon=None, item=None):
        """🌐 Online-Zugriff an/aus (JB Phase 3). Anschalten: anonymes Konto anlegen (einmalig),
        Liste sofort hochladen, Code-/Link-Seite oeffnen. Ausschalten: nur lokal deaktivieren
        (Konto/Slot bleiben bestehen -> spaeter derselbe Code)."""
        from . import cloud
        s = i18n.strings(self.lang)
        if self.settings.get("cloud_enabled"):
            self.settings["cloud_enabled"] = False
            config.save_settings(self.paths["settings"], self.settings)
            self._notify(s["cloud_off"])
            self._rebuild_menu()
            return

        def _go():
            ok, acc = cloud.register(self.data_dir)
            if not ok:
                self._notify(s["cloud_fail"].format(e=acc))
                return
            self.settings["cloud_enabled"] = True
            config.save_settings(self.paths["settings"], self.settings)
            cloud.upload(self.data_dir, self.paths["out_html"])   # sofort erste Fassung hochladen
            self._open_cloud_info(acc)
            self._notify(s["cloud_on"].format(code=acc.get("code", "")))
            self._rebuild_menu()

        threading.Thread(target=_go, daemon=True).start()

    def on_cloud_show(self, icon=None, item=None):
        """Code-/Link-Seite erneut oeffnen (Menuepunkt nur sichtbar, wenn aktiv)."""
        from . import cloud
        acc = cloud.load_account(self.data_dir)
        if acc:
            self._open_cloud_info(acc)

    def on_cloud_newcode(self, icon=None, item=None):
        """Neuen Zugangscode erzeugen (JB: 'Code aendern'). Der alte wird sofort ungueltig;
        die Info-Seite mit dem neuen Code oeffnet sich."""
        from . import cloud
        s = i18n.strings(self.lang)

        def _go():
            ok, res = cloud.change_code(self.data_dir)     # None = Server wuerfelt neuen Code
            if ok:
                self._open_cloud_info(cloud.load_account(self.data_dir))
                self._notify(s["cloud_newcode_ok"].format(code=res))
            else:
                self._notify(s["cloud_fail"].format(e=res))

        threading.Thread(target=_go, daemon=True).start()

    def _open_cloud_info(self, acc):
        """Info-Seite (Zugangscode gross + Link) in data/ schreiben und im Browser oeffnen."""
        from . import cloud
        try:
            p = os.path.join(self.data_dir, "data", "cloud_info.html")
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w", encoding="utf-8") as f:
                f.write(cloud.info_html(acc, self.lang))
            webbrowser.open("file:///" + p.replace("\\", "/"))
        except Exception:
            pass

    def on_autoupdate(self, icon=None, item=None):
        """Auto-Update umschalten — der Haken im Menue folgt dem Setting (config.json)."""
        self.settings["auto_update"] = not self.settings.get("auto_update")
        config.save_settings(self.paths["settings"], self.settings)

    def _notify(self, text):
        try:
            self.icon.notify(text, "SyncManga")
        except Exception:
            pass

    def _self_update(self, manual=False):
        """Selbst-Update-Fluss (Task #34): Check -> melden oder installieren.

        manual=True (Menueklick) meldet auch "ist aktuell" und installiert direkt.
        Sonst (stiller Check nach dem Sync): installieren nur mit auto_update=True,
        andernfalls EIN Tray-Hinweis je neuer Version. Waehrend ein Sync laeuft, wird NIE
        getauscht — der Neustart wuerde ihn abbrechen; Hinweis kommt trotzdem."""
        s = i18n.strings(self.lang)
        info = update.check_release(__version__, update.fetch_release_json)
        if not info.get("available"):
            if manual:
                self._notify(s["upd_none"].format(v=__version__))
            return
        v = info["version"]
        # Verteilformunabhaengig: gepackte exe ODER Skripte auf dem mitgelieferten
        # PSF-signierten Python (v2). `arg` ist dort das Startskript fuer den Neustart.
        exe, arg = update.programm_exe()
        if not exe or not (manual or self.settings.get("auto_update")) or self.busy.locked():
            if manual or v != self._upd_seen:
                self._upd_seen = v
                self._notify(s["upd_available"].format(v=v))
            if v != self._update_pending:            # Ausrufezeichen-Badge aufs Icon (JB 14.07.)
                self._update_pending = v
                self._refresh_icon()
            return
        self._notify(s["upd_installing"].format(v=v))
        try:
            if update.installiert_via_setup(exe):
                # Installierte Variante (JB-Befund 22.07.): NIE die exe tauschen — das wuerde
                # den onedir-Nutzer zurueck in die onefile-Form drehen (Defender-Risiko).
                # Stattdessen das Setup still ausfuehren; ohne Setup-Asset/digest im Release
                # lieber beim alten Stand bleiben (fail-safe).
                if not info.get("setup_url"):
                    self._notify(s["upd_failed"].format(e="Release ohne Setup-Asset"))
                    return
                neu = update.download_setup(info, self.data_dir)
                try:
                    os.remove(self.lockfile)     # sauber uebergeben wie bei on_quit
                except OSError:
                    pass
                # kehrt nicht zurueck (Setup + Neustart); `arg` startet bei v2 das Skript
                update.apply_setup_update(neu, exe, arg)
            new = update.download_exe(info, os.path.dirname(exe))
            try:
                os.remove(self.lockfile)         # sauber uebergeben wie bei on_quit
            except OSError:
                pass
            update.apply_exe_update(new, exe)    # kehrt nicht zurueck (Neustart der neuen exe)
        except Exception as e:
            self._notify(s["upd_failed"].format(e=e))

    def _do_update(self, open_after=False, force=False):
        if not self.busy.acquire(blocking=False):
            return
        self._refresh_icon()
        threading.Thread(target=self._tooltip_progress, daemon=True).start()
        try:
            # full=True: der 80er-Haeppchen-Deckel stammt aus der Suite (6h-Schnelllauf) — im
            # Standalone verwirrte er nur (JB: '0/80 zurueckgesprungen... sind es nicht 800?').
            # Ein Lauf arbeitet hier IMMER alles ab; im Alltag ist die Restliste ohnehin winzig.
            run(self.data_dir, lang=self.lang, full=True, force=force)
            self._read_health()
        except Exception:
            pass
        finally:
            self.busy.release()
            self._refresh_icon()
        if self.settings.get("cloud_enabled"):   # 🌐 Liste zur Sync-Cloud hochladen (JB Phase 3)
            try:
                from . import cloud
                cloud.upload(self.data_dir, self.paths["out_html"])
            except Exception:
                pass                             # nie den Sync-Abschluss stoeren
        self._self_update()                      # stiller Update-Check nach jedem Sync (Task #34)
        if open_after:
            self.on_open()

    def _tooltip_progress(self):
        """Sync-Fortschritt im Tooltip (JB): % + Restzeit, aus data/sync_progress.json (vom Kern
        alle paar Serien atomar geschrieben). Laeuft nur solange der Sync laeuft; danach setzt
        _refresh_icon den normalen Tooltip zurueck."""
        import json as _json
        import time as _time
        p = os.path.join(self.data_dir, "data", "sync_progress.json")
        t0 = _time.time()
        while self.busy.locked():
            try:
                d = _json.load(open(p, encoding="utf-8"))
                done, total = int(d.get("done") or 0), int(d.get("total") or 0)
                if total and done and _time.time() - float(d.get("ts") or 0) < 600:
                    pc = 100 * done // total
                    eta = round((_time.time() - t0) / max(done, 1) * (total - done) / 60)
                    self.icon.title = (f"SyncManga — {pc}% ({done}/{total})"
                                       + (f" · ~{eta} min" if eta >= 1 else ""))
            except Exception:
                pass
            _time.sleep(4)

    def _read_health(self):
        import json
        try:
            with open(os.path.join(self.data_dir, "source_health.json"), encoding="utf-8") as f:
                dead = json.load(f).get("dead", [])
            self.dead, self.dead_names = len(dead), list(dead)
        except Exception:
            self.dead, self.dead_names = 0, []

    def _set_lang(self, code):
        self.settings["lang"] = code
        config.save_settings(self.paths["settings"], self.settings)
        self.lang = choose_lang(None, self.settings)
        self._rebuild_menu()
        threading.Thread(target=self._do_update, daemon=True).start()   # Liste in neuer Sprache neu rendern

    def on_help(self, icon=None, item=None):
        readme = find_readme(self.data_dir)
        if readme:
            webbrowser.open("file:///" + readme.replace("\\", "/"))
        else:
            self._info(i18n.strings(self.lang)["privacy"])

    def _info(self, text):
        """Hinweisfenster ueber die Windows-eigene MessageBox (user32).

        Frueher tkinter — das ist seit Verteilform v2 (23.07.) nicht mehr verfuegbar: die
        offizielle Embeddable-Distribution der Python Software Foundation liefert Tcl/Tk
        bewusst nicht mit ("Tcl/tk ... and pip are not included"). user32.MessageBoxW ist
        in jedem Windows da, braucht keine Abhaengigkeit und sieht heimischer aus.
        MB_OK | MB_ICONINFORMATION | MB_SETFOREGROUND = 0x40040."""
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(None, str(text), "SyncManga", 0x40040)
        except Exception:
            print(text)

    def on_quit(self, icon=None, item=None):
        try:
            if os.path.exists(self.lockfile):
                os.remove(self.lockfile)
        except Exception:
            pass
        # Pausiert-Stempel fuer die offene Seite (JB: 'Tray geschlossen — update paused'):
        # laeuft gerade ein Sync, wird sein Stand als 'pausiert' markiert -> Balken wird grau.
        try:
            import json as _json
            pd = os.path.join(self.data_dir, "data")
            d = _json.load(open(os.path.join(pd, "sync_progress.json"), encoding="utf-8"))
            if int(d.get("done") or 0) < int(d.get("total") or 0):
                from .enrich import _progress
                _progress("pausiert", d.get("done") or 0, d.get("total") or 0, pd)
        except Exception:
            pass
        self.icon.stop()
        # HART beenden (JB-Fund: 'im Tray geschlossen, doch die Aktualisierung läuft weiter') —
        # der ThreadPoolExecutor eines laufenden Syncs haelt den Prozess sonst per atexit am Leben,
        # bis ALLE Serien durch sind. Datenverlust droht nicht: der Cache wird alle 25 Serien
        # atomar gesichert, der naechste Start setzt genau dort fort.
        os._exit(0)

    def _on_ready(self, icon):
        # Sichtbar machen + einmalige Start-Meldung, damit klar ist, dass die App laeuft
        # (sonst wirkt der reine Tray-Start wie "nichts passiert").
        try:
            icon.visible = True
            icon.notify(i18n.strings(self.lang).get("tray_started", "SyncManga"), "SyncManga")
        except Exception:
            pass
        threading.Thread(target=self._auto_loop, daemon=True).start()

    def _auto_loop(self):
        """Selbstlaeufer (JB: 'sollte beim ersten Ausfuehren direkt starten'): OHNE Liste beginnt
        der Erstaufbau SOFORT (Seite mit Fortschrittsbalken oeffnet sich von selbst); mit Liste
        laeuft sanft verzoegert (60s nach Start) und dann stuendlich geprueft ein stiller Sync,
        sobald die Liste aelter als 6h ist. Daemon-Thread — 'Beenden' stoppt alles sofort."""
        import time as _time
        first = not os.path.isfile(self.paths["out_html"])
        if not first:
            try:                                # UNFERTIGER Aufbau (JB: '417 in der Liste, aber
                import json as _json  # nichts taucht auf') -> sofort weitermachen,
                d = _json.load(open(os.path.join(self.data_dir, "data", "sync_progress.json"),
                                    encoding="utf-8"))
                first = int(d.get("done") or 0) < int(d.get("total") or 0)
            except Exception:
                pass
        if first:
            _time.sleep(1.5)
            existed = os.path.isfile(self.paths["out_html"])
            self.on_open()                      # Erststart: Leerseite + Browser (+ Aufbau)
            if existed and not self.busy.locked():   # Seite gab es schon -> Aufbau explizit anstossen
                threading.Thread(target=self._do_update, daemon=True).start()
        while True:
            _time.sleep(60)
            try:
                age = _time.time() - os.path.getmtime(self.paths["out_html"])
            except OSError:
                age = 10 ** 9
            if age > 6 * 3600 and not self.busy.locked():
                self._do_update()               # blockiert diesen Thread -> Laeufe stapeln sich nie
            _time.sleep(3300)                   # danach ~stuendlich pruefen

    def run(self):
        self.icon.run(setup=self._on_ready)


def main(argv=None):
    # parse_args liefert (data_dir, lang, full, force) — NUR die ersten beiden interessieren den
    # Tray. Bewusst per Index statt Entpacken: eine kuenftige Erweiterung der Rueckgabe darf den
    # exe-Start NIE wieder crashen (JB-Fund: 'too many values to unpack' beim Erststart der exe).
    args = parse_args(sys.argv[1:] if argv is None else argv)
    TrayApp(args[0], args[1]).run()


if __name__ == "__main__":
    main()
