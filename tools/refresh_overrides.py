#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Override-Datenbank erneuern: laeuft alle Discovery-Tools nacheinander (off-peak, NICHT waehrend
eines Manga-Laufs). Jedes Tool fuellt nur Serien OHNE bestehenden Override -> manuelle Eintraege
bleiben unangetastet. Reihenfolge = Prioritaet (verifizierte Eigendomains zuerst, dann die grossen
Sitemap-Quellen). Ein Fehler in einem Tool stoppt die anderen nicht (modular-fusioniert).

Damit erneuert sich die DB selbststaendig, wenn die Quellen neue Mangas aufnehmen (JB-Wunsch).

Aufruf:  python -m tools.refresh_overrides
"""
import importlib
import sys
import time

# apply_source_confirms zuerst: von JB bestaetigte Direktlinks haben Vorrang, danach fuellt die
# Discovery nur noch Serien OHNE Override -> bestaetigte Quellen bleiben unangetastet.
TOOLS = ["tools.apply_source_confirms", "tools.fix_broken", "tools.discover_dedicated", "tools.discover_sitemap"]


def main():
    for name in TOOLS:
        print(f"\n=== {name} ===", flush=True)
        t0 = time.time()
        try:
            importlib.import_module(name).main()
        except Exception as e:                                  # ein Tool-Fehler darf die anderen nicht stoppen
            print(f"  ! {name} fehlgeschlagen: {type(e).__name__}: {e}", flush=True)
        print(f"  ({time.time() - t0:.0f}s)", flush=True)
    print("\nOverride-DB erneuert.", flush=True)


if __name__ == "__main__":
    sys.exit(main())
