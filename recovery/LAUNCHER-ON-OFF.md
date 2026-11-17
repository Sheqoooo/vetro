# Launcher-An-/Aus-Test am 17. November 2026

**Ergebnis: technischer An-/Aus-Test erfolgreich. Der Launcher ist am Ende aus.**

Der Besitzer hat den Test einschließlich privater Ausgangssicherung freigegeben.
Vor Änderungen wurde der Root-Agent geprüft, der Samsung-Autostartwert gelesen
und der Zustand der zwei Vetro-Dateien `vetro-dock.json` und
`vetro-dock-apps.tsv` als vorhanden/abwesend und gegebenenfalls Base64-Inhalt
gesichert. Zusätzlich liegen Geräte-/Rootstatus und Dock-Antworten privat vor.
Dies ist eine **Post-Installations-/Post-Root-Baseline**, kein Backup vor Root
und kein Firmware-Backup. Rohdaten bleiben in `PROJECT/recovery/private/launcher-tests`.

## Tatsächlicher Ablauf

1. Samsung-Autostartwert **0** gelesen (war bereits ausgeschaltet).
2. Launcher als ausgeschaltet bestätigt, zusätzlich PID-Datei und passende
   Prozess-Commandline unabhängig geprüft: nicht laufend.
3. `POST /dock` mit `action=enable` nach vollständiger Baseline.
4. Antwort: enabled=true, running=true, kein gemeldeter Launcherfehler.
   Samsung-Autostart weiterhin 0.
5. `POST /dock` mit `action=disable` im Rücknahmeblock.
6. Antwort: enabled=false, kein Restorefehler/ausstehender Autostart-Restore.
   Unabhängige Prozessprüfung: gestoppt. Samsung-Autostart weiterhin **0**.

Die neue Hilfsdatei `launcher_smoke.py` enthält diese Reihenfolge. Sie verweigert
einen bereits aktivierten/laufenden Launcher oder einen ungeklärten Ausgangswert.
Ein Timeout/Fehler beim Einschalten führt ebenfalls zum Ausschaltversuch, weil
die Änderung auf dem TV trotz fehlender Antwort angekommen sein könnte. Ein
Fehler beim Ausschalten oder abweichender Ausgangswert beendet weitere Änderungen.

## Wichtige Aussagegrenzen

Der Autostartwert wurde bei diesem Gerät nicht von 1 auf 0 geändert, weil er schon
0 war. Bestätigt ist **0 → 0 → 0**, nicht der Hardware-Restorezweig **1 → 0 → 1**.
Der Wert wurde nicht nur für einen Test künstlich eingeschaltet.

Getestet sind Backendzustand und Prozess, nicht die sichtbare Home-Taste oder
Navigation aus einer anderen App/HDMI. Standby und Neustart mit eingeschaltetem
Launcher bleiben offen. Vetro bleibt installiert und der Root-Agent eingerichtet.

Beim Test werden Vetro-Zustands-/Katalogdateien geschrieben. Der Ausschalter
setzt enabled=false und lässt unter anderem einen historischen Startzeitpunkt
und den Katalog bestehen. Diese Dateien wurden **nicht bytegenau auf ihren
früheren Inhalt zurückgesetzt**; die private Baseline bewahrt den Originalinhalt.
Kein vollständiger Root-/Installations-Rollback behauptet oder ausgeführt.

## Während der Vorbereitung behobene Probleme

- Erster Sicherungsversuch vor jedem Toggle abgebrochen: die printf-Markierung
  enthielt einen zu stark maskierten Zeilenumbruch. Auf einfache echo-Markierung
  umgestellt; keine TV-Einstellung vorher geändert.
- Zweiter Versuch ebenfalls vor jedem Toggle angehalten: Vetros ursprüngliche
  Prozessabfrage meldete running=null. Deren letzter tail-Aufruf scheitert bei
  noch fehlender Launcher-Logdatei und verdeckt dadurch ein bereits ausgegebenes
  `dock=` ohne PID. Nicht als ausgeschaltet angenommen, sondern durch eine
  zusätzliche rein lesende numerisch begrenzte PID-/Commandline-Prüfung geklärt.
- Danach Baseline und An-/Aus-Test erfolgreich. Keine Produktquelle für diese
  Diagnose verändert und keine Logdatei als Scheinlösung auf dem TV angelegt.

## Wiederholung nur mit Freigabe

```sh
/Library/Developer/CommandLineTools/usr/bin/python3 -B \
  vetro/recovery/launcher_smoke.py TV_IP --confirm-on-off
```

Dieser Aufruf verändert die TV-Oberfläche. Er darf nicht als reine Statusprüfung
verwendet werden. Die Flag-Abfrage ist eine Bedienhürde; die Freigabe des Besitzers
und vorhandenen technischen Zugriffsbeschränkungen werden dadurch nicht ersetzt.
