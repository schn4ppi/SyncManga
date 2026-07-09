# -*- coding: utf-8 -*-
"""
Schlankes Standalone-Tray der App „SyncManga".

Linksklick = Liste öffnen. Menü: Aktualisieren · Liste öffnen · Sprache · Hilfe · Beenden.
Single-Instance (PID-Lock, neue Instanz übernimmt). Mehrsprachig über syncmanga.i18n.
Gleicher Look wie Claude Sync (Kreis-Pfeile-Icon), reduziert.

Aufruf:  python -m syncmanga.tray [DATENORDNER] [--lang de|en]

Die GUI (pystray/PIL/tkinter) wird manuell getestet; die reinen Helfer
(menu_labels, icon_color, single_instance) sind unit-getestet.
"""
import os
import sys
import threading
import webbrowser

from . import __version__, config, i18n, update
from .__main__ import run, resolve_paths, parse_args, choose_lang

PKG_DIR = os.path.dirname(os.path.abspath(__file__))


# ---------------- reine, testbare Helfer ----------------

def icon_color(busy=False, dead=0):
    """Icon-Farbe = Zustand (wie Claude Sync): terracotta ok, grün Sync, gelb/magenta/rot tote Quellen."""
    if busy:
        return (90, 175, 95)        # grün: Lauf aktiv
    if dead >= 3:
        return (230, 30, 30)        # rot: 3+ Quellen tot
    if dead == 2:
        return (255, 0, 200)        # neon-magenta: 2 tot
    if dead == 1:
        return (235, 205, 30)       # gelb: 1 tot
    return (214, 119, 86)           # terracotta: alles ok


def menu_labels(lang):
    """Menü-Beschriftungen in der gewählten Sprache (rein, testbar)."""
    s = i18n.strings(lang)
    return {"update": s["tray_update"], "force": s["tray_force"], "open": s["tray_open"],
            "selfupdate": s["tray_selfupdate"], "autoupdate": s["tray_autoupdate"],
            "cloud": s["tray_cloud"], "cloud_show": s["tray_cloud_show"],
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
        self.icon = pystray.Icon("syncmanga", self._image(), self._tooltip(), menu=self._menu())

    # ----- icon -----
    def _image(self):
        from PIL import Image, ImageDraw
        img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.ellipse([5, 5, 59, 59], fill=icon_color(self.busy.locked(), self.dead))
        d.arc([18, 18, 46, 46], 35, 300, fill=(255, 255, 255), width=5)
        d.polygon([(46, 24), (39, 15), (53, 18)], fill=(255, 255, 255))
        d.polygon([(18, 40), (25, 49), (11, 46)], fill=(255, 255, 255))
        return img

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
                from .render import render as _render
                from .__main__ import copy_guides
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
        exe = update.frozen_exe()
        if not exe or not (manual or self.settings.get("auto_update")) or self.busy.locked():
            if manual or v != self._upd_seen:
                self._upd_seen = v
                self._notify(s["upd_available"].format(v=v))
            return
        self._notify(s["upd_installing"].format(v=v))
        try:
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
        try:
            import tkinter as tk
            from tkinter import messagebox
            r = tk.Tk(); r.withdraw()
            messagebox.showinfo("SyncManga", text)
            r.destroy()
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
                import json as _json            # nichts taucht auf') -> sofort weitermachen,
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
