# N₂O Gewerbe-Guide

Interaktives Step-by-Step-Programm für den **legalen, gewerblichen Bezug von Distickstoffmonoxid
(N₂O / Lachgas)** in Deutschland – Rechtslage (Stand Juli 2026), Compliance-Checkliste,
Dokumenten-Generator, Anbieter, Bestandsverwaltung und Kostenrechner.

## Nutzung

Kein Build, keine Abhängigkeiten: `index.html` im Browser öffnen. Alle Eingaben bleiben lokal
im Browser (localStorage); es werden keine Daten übertragen. Zwei Ansichten:

- **Geführt** (Standard): 9 Schritte mit Fortschritts-Ring, Step-Leiste und Weiter/Zurück-Navigation
- **Handbuch**: alles auf einer Seite zum Nachschlagen

## Die 9 Schritte

1. **Realitäts-Check** – 4 Grundvoraussetzungen mit ehrlicher Grün/Gelb/Rot-Bewertung
2. **Grundlagen** – Chemie, Mythen-Check (Schweißen/Lackieren/Gasgemische), Temperaturleiter,
   echte Einsatzgebiete, **Wissens-Quiz mit 7 Fragen** und Sofort-Feedback
3. **Qualität** – Vergleichstabelle (technisch/E942/medizinisch/denaturiert), Qualitäts-Auswahl,
   Wareneingangsprüfung per Analysenzertifikat (CoA)
4. **Rechtslage** – NpSG-Änderung (in Kraft seit 12.04.2026), Gefahrstoff-/Transportrecht,
   Rahmen für Privatpersonen
5. **Betriebsdaten & Dokumenten-Generator** – Formular füllt automatisch die
   **Verwendungszweck-Dokumentation** (einzeln druckbar) und die Anfrage-Mail
6. **Compliance-Checkliste** – 25 Punkte in 5 Gruppen mit „Warum?"-Erklärungen,
   Fortschrittsbalken und integriertem **ADR-Kleinmengen-Rechner** (1000-Punkte-Regel)
7. **Anbieter & Anfrage** – Lieferantenübersicht, Gebinde/Mindestmengen, Bestellprozess,
   automatisch befüllte Anfrage-Mail mit Copy-Button
8. **Kosten & Angebotsvergleich** – Jahreskalkulation plus Vergleich von bis zu 3 realen
   Angeboten mit Balkendiagramm und Bester-Preis-Markierung
9. **Verwaltung** – **Flaschen-Bestand** (mit Prüffrist-Warnung) und **Verbrauchs-Log**
   (beides CSV-exportierbar), JSON-Backup/Restore, Betriebsdossier-Druck

Dazu: Hell/Dunkel-Umschalter, Print-Stylesheets (ganzes Dossier oder nur die
Verwendungszweck-Doku), Gesamtfortschritt als Score-Ring.

## Was der Guide bewusst NICHT ist

- **Keine Umgehungsanleitung.** Die Checkboxen bilden reale Voraussetzungen ab – sie zeigen nicht,
  „welche Antworten man geben muss, damit es durchgeht". Ein Gewerbe ohne echte Tätigkeit
  anzumelden, um an größere Gebinde zu kommen, ist eine Umgehung des NpSG und strafbar.
- **Kein Gasmisch-Rechner.** Das Mischen/Umfüllen von Druckgasen ist zertifizierten
  Abfüllbetrieben vorbehalten und für Laien gefährlich.
- **Keine Rechtsberatung.** Angaben nach bestem Wissen, Stand Juli 2026 – die Rechtslage
  ist in Bewegung (allein 2025/2026 zwei Änderungen).

## Technik

Statisches HTML + CSS + Vanilla-JavaScript, keine externen Abhängigkeiten.
Eingebauter Selbsttest: `index.html?selftest=1` öffnen – das Ergebnis steht im Seitentitel
(`SELFTEST PASS 13/13`), geprüft werden Wizard, Quiz, Checkliste, Generatoren, ADR-Rechner,
Angebotsvergleich, Bestand und Log.
