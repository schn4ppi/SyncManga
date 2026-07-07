#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AniList einmalig verbinden (PIN-Verfahren) — JBs 'undefined'-Problem geloest: die pin-Seite zeigt
den Code NUR bei response_type=code (bei =token landet das Token unsichtbar im URL-Fragment ->
'undefined'). Dieses Tool oeffnet die RICHTIGE URL, fragt Code + Client-Secret ab (Secret wird
nur fuer den einmaligen Tausch gebraucht und NICHT gespeichert) und legt das Zugriffs-Token im
Windows-Anmeldeinformationsspeicher ab (Dienst 'claude-sync-anilist'). Danach schreibt jeder
Sync den Lese-Fortschritt automatisch nach AniList (MangaBaka importiert von dort).

Aufruf:  Core\\venv\\Scripts\\python.exe -m tools.anilist_auth   (im Ordner Manga)
"""
import getpass
import os
import sys
import webbrowser

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.normpath(os.path.join(HERE, ".."))
if PKG not in sys.path:
    sys.path.insert(0, PKG)
from syncmanga.common import post_json                           # noqa: E402
from syncmanga.anilist import TOKEN_SERVICE, API                 # noqa: E402

CLIENT_ID = 44883        # JBs API-Client "Claude Sync" (die ID ist nicht geheim)
AUTH_URL = (f"https://anilist.co/api/v2/oauth/authorize?client_id={CLIENT_ID}"
            f"&redirect_uri=https://anilist.co/api/v2/oauth/pin&response_type=code")


def main():
    print("AniList verbinden — es oeffnet sich der Browser. Dort 'Approve' klicken,")
    print("dann den angezeigten Code hier einfuegen.")
    print(f"(Falls sich nichts oeffnet, diese URL manuell aufrufen:\n  {AUTH_URL})\n")
    webbrowser.open(AUTH_URL)
    code = input("Code von der AniList-Seite: ").strip()
    if not code:
        sys.exit("Kein Code eingegeben - abgebrochen (nichts veraendert).")
    secret = getpass.getpass("Client-Secret (aus anilist.co/settings/developer, wird NICHT gespeichert): ").strip()
    if not secret:
        sys.exit("Kein Secret eingegeben - abgebrochen (nichts veraendert).")

    tok = post_json("https://anilist.co/api/v2/oauth/token", {
        "grant_type": "authorization_code", "client_id": str(CLIENT_ID), "client_secret": secret,
        "redirect_uri": "https://anilist.co/api/v2/oauth/pin", "code": code})
    access = tok.get("access_token")
    if not access:
        sys.exit(f"Kein Token erhalten: {tok}")

    import keyring
    keyring.set_password(TOKEN_SERVICE, "token", access)

    who = post_json(API, {"query": "query{Viewer{name}}"},
                    headers={"Authorization": f"Bearer {access}"})
    name = ((who.get("data") or {}).get("Viewer") or {}).get("name", "?")
    print(f"\n✓ Verbunden als AniList-Nutzer '{name}'. Token sicher im Windows-Keyring abgelegt.")
    print("Ab jetzt schreibt jeder Sync deinen Lese-Fortschritt automatisch nach AniList.")


if __name__ == "__main__":
    main()
