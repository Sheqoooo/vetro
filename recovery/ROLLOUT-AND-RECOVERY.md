# Vetro: kontrollierte Einführung und Rücknahme

## Ziel und Grenzen

Erste Stufe: eigener Launcher, Home-Taste, Start aus Standby und Kaltstart.
Keine Systempakete entfernen oder deaktivieren, kein DNS-Filter, kein MQTT,
keine Änderungen an Bild-/Service-Menü-Einstellungen oder Firmwareupdates.
Root am TV ist vom Eigentümer grundsätzlich akzeptiert; Mac-Administratorrechte
und breiter Heimnetzzugriff sind weiterhin nicht freigegeben.

Ein Restore-Skript kann nur bekannte Änderungen zurücknehmen, solange ein geeigneter
Zugriffsweg zum TV besteht. Es ersetzt kein Firmware-Abbild und hilft nicht zuverlässig
bei einem nicht mehr startenden TV. Ein Werksreset ist kein zugesicherter Rückweg.

## Gerätezuordnung bleibt lokal

Modell, Firmware, IP, DUID, Seriennummern und echte Exporte nicht in diesen
öffentlichen Plan eintragen. Die konkrete Modell-/Firmware-Kombination vor
Installation bestätigen und die lokale Baseline separat verwahren.

## Quellcodebefunde

Geprüft: Sheqoooo/vetro, app/package.json meldet 0.3.5. Die untersuchten
Datei-Hashes stehen in SOURCE-REVIEW.json. Vor einem Build zusätzlich den exakten
Commit erfassen, den gesamten Stand beziehen und dessen Anweisungen prüfen.

1. `app/service/dock.js`: Der Launcher fängt Home ab und schließt Samsung Home.
   Die Default-Home-Zuordnung bleibt unverändert. Das Aktivieren kann Autorun
   Smart Hub von 1 auf 0 ändern; der vorherige Wert wird in `vetro-dock.json`
   gespeichert. Ausschalten versucht diesen Wert wiederherzustellen.
2. `app/service/main.js`: Nach Root-Verbindung werden Vetros eigene Serviceflags
   onboot/autorestart bei Bedarf automatisch verändert. Die Installation ist daher
   nicht erst beim manuellen Aktivieren des Launchers zustandsändernd.
3. `app/service/component-actions.js`: Originalflags werden TV-lokal unter
   `/home/owner/share/vetro/startup-backups/` abgelegt. Diese Dateien müssen vor
   Entfernung der Integration extern gesichert werden. Nachträgliches `/startup`
   allein rekonstruiert den Vorzustand nicht.
4. `app/service/home-order.js`: Restore und lokale Cache-Backups existieren für
   die Samsung-App-Reihenfolge. Das ist kein vollständiges Systembackup.
5. `rooting/service/platform.js`: Die Integration schreibt Staging-Artefakte,
   Schlüssel/Token und Logs auf dem TV; sie entfernt außerdem alte passende
   Staging-Artefakte. Ein vollständiger Rückweg muss deren Eigentümerschaft und
   etwaige vorbestehende Nutzung prüfen, statt pauschal Verzeichnisse zu löschen.
6. `app/service/main.js` und SECURITY.md: Das Dashboard bindet ohne Anmeldung
   einen HTTP-Port; die Root-Agent-Authentifizierung schützt diese Oberfläche nicht.

## Reihenfolge und Freigaben

### 1. Vorbereitung ohne TV-Verbindung

- Exakten Fork-Commit festhalten und vollständigen Checkout mit dessen Anweisungen prüfen.
- Keine fremden Installationsskripte ausführen, bevor Quelle und Auswirkungen geprüft sind.
- Benötigte Werkzeuge nach Quelle, Version und Zielpfad zur Installation vorlegen.
- Nur gezielte Werkzeug-Leserechte und Projekt-Schreibrechte verwenden.
- Der öffentliche Fork enthält ausschließlich generische Werkzeuge/Dokumentation.
- Offline-Archivierungswerkzeug: 10 Tests mit Python 3.9.6 erfolgreich; kein
  Hardware-Restore-Test und kein Vollbackup. Details in README.md.

### 2. Netzwerkgrenze außerhalb des Agenten herstellen

- TV-IP und Entwicklungs-IP festlegen, TV in isoliertes Segment verschieben.
- Nur das Entwicklungsgerät darf Vetros Dashboard erreichen; TV darf weder
  Unraid noch andere private Heimnetzgeräte erreichen. Auch übrige Clients
  dürfen den Root-Dashboard-Port nicht erreichen.
- Gleiches Layer-2-Segment, IPv6, WLAN, Ethernet und alternative Routen beachten.
- Keine Portweiterleitung/UPnP. Keine Netzwerksuche; Ziel ausschließlich fest vorgeben.
- Codex-Netzwerkschalter allein setzt diese Grenze nicht durch.
- Zur Installation SDB TCP 26101, zur Verwaltung der geprüfte Dashboard-Port
  (Standard TCP 8099); weitere Ports nur nach begründetem Bedarf freigeben.
- Netzwerkregeln und erforderliche Codex-Dienstziele müssen vorab geprüft werden.

### 3. Vor Root/Installation sichern

- Modell/Firmware am Gerät bestätigen; Firmware nicht für den Versuch verändern.
- Originalwerte manuell erfassen: Developer Mode und Host-PC-IP, Autorun Smart Hub,
  letzte-App-Autostart, ursprüngliche Home-/Fernbedienungsfunktion.
- Funktionsprobe und Startverhalten dokumentieren, ohne Bildschirm-Inhalte oder
  private Konten in öffentliche Berichte zu übernehmen.
- Bekannte vorbestehende Tizen-/Root-Installationen und deren Dateien berücksichtigen.
- Wo ohne Root keine Sicherung möglich ist: Lücke ausdrücklich dokumentieren,
  nicht "vollständig gesichert" melden.
- Die konkrete Root-Methode und ihre Entfernung separat prüfen. Dafür gibt es in
  diesem Vorbereitungspaket noch keine vollständig geprüfte Rücknahme.

### 4. Nach gesonderter Installationsfreigabe

- Offizielle Signierung mit eigenen Zertifikaten; Passwörter nur durch den Eigentümer.
- Exakten Fork-Commit bauen; kein unkontrolliertes "latest" oder fremdes Universalpaket.
- Developer-Host-IP-Wechsel berücksichtigen: 127.0.0.1 ermöglicht TV-lokales SDB,
  verhindert dabei laut Installationsanleitung normalen Mac-SDB-Zugriff. Die manuelle
  Rückkehr zur Mac-IP muss über die Samsung-Menüs möglich bleiben.
- Unmittelbar nach Installation und vor Nutzereinstellungen: Originalflag-Backups
  extern sichern und Status-/Launcher-/Remap-/Input-/Startup-Exporte archivieren.
- Prüfen, ob Root und Service tatsächlich laufen; ein App-Icon beweist das nicht.

### 5. Launcher einzeln aktivieren und Rücknahme testen

- Vorherwert von Autorun Smart Hub UND Vetros Zustandsdatei sichern.
- Nur Launcher aktivieren; Antwort und erneute Statusabfrage vergleichen.
- Bei Fehler/unklarem Status stoppen und zuerst Istzustand ermitteln; keine
  blinden Wiederholungen nach Timeout.
- Launcher deaktivieren und Original-Autorun-Wert sowie Home-Funktion prüfen.
  `POST /dock` mit `action=disable` kann in `lastError` einen Restore-Fehler
  melden; HTTP-Erfolg allein zählt daher nicht als Rücknahmebeleg.
- Erst nach erfolgreichem Rücknahmetest erneut aktivieren.

### 6. Abnahmetests

- Home aus laufenden Streaming-Apps und HDMI öffnet Vetro.
- Lautstärke, Zurück, Quelle und Einstellungen bleiben nutzbar.
- Wiederaufnahme nach Standby separat von echtem Kaltstart testen.
- Kaltstart ohne manuelles Öffnen der Vetro-App: Startverzögerung, sichtbare
  Samsung-Oberfläche und Status protokollieren. Bis zu 90 Sekunden sind upstream
  genannt; "Samsung wird niemals geladen" ist nicht zugesichert.
- Mac muss danach nicht dauerhaft verbunden bleiben.

## Vollständige Rücknahme: geplante Abhängigkeiten

Noch keine direkt ausführbare Anleitung: konkrete Originalwerte und Gerätezustand fehlen.

1. Gesicherte Werte, TV-Identität/Firmware und Istzustand vergleichen. Bei Abweichung
   zu Baseline oder unseren protokollierten Änderungen stoppen.
2. Eigene Boot-Wiederholungen/Remaps kontrolliert abschalten, solange Verwaltung
   und alternative Eingabe verfügbar sind. Erreichbarkeit nach jedem Schritt prüfen.
3. Launcher abschalten, Samsung Home und ursprünglichen Autorun-Wert bestätigen.
4. Nur tatsächlich geänderte Werte zurücksetzen. Keine pauschale Aktion "alles aktivieren".
5. Originalflag-Dateien/State und Änderungsjournal extern sichern, bevor App-Daten
   entfernt werden. Systemdatenbanken nicht blind mit alten Komplettkopien überschreiben.
6. Vetro-Integration, Paket und eindeutig zugehörige Restdateien über einen zuvor
   getesteten Weg entfernen. Nicht die letzte Verwaltungsverbindung vorzeitig beenden.
7. Developer Mode/Host-PC-IP und ausschließlich neu angelegte Netzwerkregeln nach
   dokumentiertem Vorzustand zurücksetzen. Kein automatischer Firmware-Downgrade.
8. Home, TV-Einstellungen, Apps, HDMI, Standby und Kaltstart erneut prüfen.

## Quellen

- https://github.com/Sheqoooo/vetro/blob/main/app/service/dock.js
- https://github.com/Sheqoooo/vetro/blob/main/app/service/main.js
- https://github.com/Sheqoooo/vetro/blob/main/app/service/component-actions.js
- https://github.com/Sheqoooo/vetro/blob/main/app/service/home-order.js
- https://github.com/Sheqoooo/vetro/blob/main/rooting/service/platform.js
- https://github.com/Sheqoooo/vetro/blob/main/app/docs/INSTALLATION.md
- https://github.com/Sheqoooo/vetro/blob/main/SECURITY.md
