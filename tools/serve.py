#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Winziger lokaler Webserver fuer SyncManga: serviert die Manga-Liste (+ PWA) ueber HTTP.

Zweck:
  - Die Liste vom HANDY im selben WLAN oeffnen (http://<PC-IP>:8765/Manga_Leseliste.html).
  - Die PWA aktiviert sich nur ueber http(s) -> hier installierbar (Homescreen-Icon, offline).
  - Basis fuer die SERVER-MIGRATION: dasselbe Skript laeuft spaeter auf dem HomeServer
    (mit Firefox-Sync als Datenquelle), das Handy greift direkt darauf zu.

Nur statisches Ausliefern des SyncManga-Ordners (read-only), keine Aktionen/Uploads.

Aufruf:  python -m tools.serve [PORT]
"""
import functools
import http.server
import os
import socket
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "Erstellt"))  # enthaelt Leseliste-HTML + manifest + sw + icons
DEFAULT_PORT = 8765


def _lan_ip():
    """Lokale LAN-IP ermitteln (fuer die Handy-URL)."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


def main(port=DEFAULT_PORT):
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT)
    httpd = http.server.ThreadingHTTPServer(("0.0.0.0", port), handler)
    url = f"http://{_lan_ip()}:{port}/Manga_Leseliste.html"
    print(f"SyncManga-Server laeuft. Am Handy (gleiches WLAN) oeffnen:\n  {url}", flush=True)
    print("  (Strg+C zum Beenden)", flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer beendet.", flush=True)


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PORT)
