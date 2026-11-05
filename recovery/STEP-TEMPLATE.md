# Vorlage für weitere Arbeitsschritte

Jeden relevanten Arbeitsschritt in WORKLOG.md ergänzen. Öffentliche Dokumentation
beschreibt nachvollziehbare Änderungen; private Baselines, Rohlogs, Adressen,
Boot-IDs und Zugangsdaten bleiben außerhalb des öffentlichen Repositories.

## YYYY-MM-DD — kurzer Titel

- **Status:** geplant / durchgeführt / fehlgeschlagen / zurückgenommen.
- **Ziel:** Welches konkrete Verhalten soll sich ändern?
- **Ausgangsstand:** Branch, Commit, Werkzeugversionen; Gerätezuordnung nur über
  eine nicht personenbezogene lokale Referenz. Hardware-/Firmware-Abgleich lokal.
- **Umfang und Freigabe:** Welche bestehenden Freigaben decken den Schritt ab?
  Neue Installation, Netzfreigabe oder TV-Schreibzugriff ausdrücklich benennen.
- **Vorher:** Welche Werte/Dateien wurden gelesen und wo liegt die private Baseline?
  Fehlende oder erst nach Installation verfügbare Werte deutlich markieren.
- **Durchführung:** Reihenfolge, Arbeitsverzeichnis, Befehle beziehungsweise
  API-Methode/Endpunkt, relevante Optionen, betroffene Dateien und TV-Einstellungen.
  Platzhalter für vertrauliche Daten benutzen; keine Geheimnisse in Shell-Argumenten.
- **Ergebnis:** Tatsächliche Rückgabe und beobachtetes Verhalten. Versuch und Erfolg
  unterscheiden. Timeout bedeutet unbekannten Zustand, nicht automatisch Fehler.
- **Validierung:** Exakter Testaufruf, Werkzeugversion, Ergebnis und Prüfumfang.
  Offline-Mocktest, Hardwaretest, Standby und Kaltstart getrennt kennzeichnen.
- **Rücknahme:** Originalwerte, getesteter Rückweg, nötige Erreichbarkeit und
  Reihenfolge. Keine pauschale Garantie bei nicht bootendem Gerät.
- **Verbleibende Risiken / offene Fragen:** Nur belegte Aussagen; Unbekanntes benennen.
- **Referenzen:** Commit, PR, Quelldatei, externe Dokumentation. Geräteexports nicht verlinken.

## Regeln für die Pflege

- Dokumentation gemeinsam mit der Änderung aktualisieren; PR beschreibt den finalen Stand.
- Keine unverifizierten Tests oder Rücknahmen als erfolgreich eintragen.
- Korrekturen sichtbar nachtragen. Der Statusabschnitt darf aktualisiert werden;
  historische Einträge müssen nachvollziehbar bleiben.
- Nur vollständige, geprüfte Versions-/Commitangaben verwenden. Ein Blob-Hash ist
  kein Build-Commit. Ohne bekannten Zeitpunkt keine Uhrzeit erfinden.
- Vor Upload auf Gerätemerkmale, personenbezogene Pfade, Tokens, Zertifikate,
  Passwörter und echte Rohlogs prüfen. Ignorierte Dateien nicht zwangsweise hinzufügen.
- Vorlagen und Fake-Daten deutlich als solche kennzeichnen.
