# Launcher-Vorprüfung und nächster Geräteschritt

Stand: 2026-11-06. Vorbereitung, keine Installationsfreigabe.

## Tatsächlich geprüft

- Quellstand: `e35b8548f8d81377209a6434bd5051f06885baa5`,
  Branch `codex/recovery-preparation`.
- Lokal liegt unter `recovery/source-snapshot/` eine **Auswahl** der
  Launcher-Module und ihrer Tests, kein vollständiger Checkout und kein baubares
  TV-Paket. `SNAPSHOT.json` hält Pfade und Git-Blob-Hashes fest. Die Auswahl ist
  eine unveränderte Kopie der angegebenen Quellen; keine Produktänderung.
- `app/tests/dock.test.cjs`: bestanden mit simulierten TV-Antworten.
  Enthalten sind Launcher an/aus, Wiederherstellung der vorher eingeschalteten
  Samsung-Autostartoption, simulierte Boot-/Crash-Situationen und Wiederholungen.
- `app/tests/dock-catalog.test.cjs`: bestanden; Katalog, Reihenfolge,
  Filter und Pfadprüfung mit künstlichen Daten.
- Erneutes HTTP-GET auf den bekannten TV, Port 8001, Pfad `/api/v2/`,
  über den verwalteten Proxy: Tizen erreichbar, `developerMode: "0"`.
  Keine anderen Heimnetzgeräte angesprochen. Kein SDB-Test, kein Root.
- Mac-Architektur: arm64. Vorhandenes gebündeltes Node reicht für diese Tests;
  Tizen-Werkzeuge und Node-Paketmanager wurden nicht installiert.

## Reproduktion der Offline-Tests

Im vollständigen Checkout werden die Tests aus `app/tests/` gestartet.
In der lokalen Quellauswahl ist davor `recovery/source-snapshot/` zu setzen.

Die eingeschränkte Mac-Umgebung verbietet Nodes Standardzugriff auf die
systemweite OpenSSL-Konfiguration. Für diese Offline-Tests wurde deshalb eine
leere Konfiguration in `recovery/private/offline-tmp/openssl.cnf` verwendet.
`OPENSSL_CONF` und `TMPDIR` gelten ausschließlich für den Testprozess:
keine globale Konfigurationsänderung und keine TLS-Verbindung.

```sh
# NODE bezeichnet das bereits vorhandene Node-Binary, PROJECT den Projektordner.
OPENSSL_CONF="$PROJECT/recovery/private/offline-tmp/openssl.cnf" \
TMPDIR="$PROJECT/recovery/private/offline-tmp" \
"$NODE" --require ./recovery/offline-test-host.cjs app/tests/dock.test.cjs

OPENSSL_CONF="$PROJECT/recovery/private/offline-tmp/openssl.cnf" \
TMPDIR="$PROJECT/recovery/private/offline-tmp" \
"$NODE" app/tests/dock-catalog.test.cjs
```

Der erste Start scheiterte am System-Konfigurationszugriff. Nach Verwendung der
lokalen Konfiguration bestand der Katalogtest; der Docktest scheiterte zunächst
zusätzlich an `os.uptime()` (EPERM). Der Test-Preload ersetzt ausschließlich
diese Hostabfrage durch 3600 Sekunden. Die vorhandenen Bootfalltests überschreiben
die simulierte Laufzeit weiterhin selbst. Danach bestand auch der Docktest.
Die Einschränkungen wurden nicht gelockert. Temporäre künstliche Testdaten bleiben
im ignorierten Projektunterordner; sie sind keine TV-Sicherung.

## Aussagegrenzen und Rückweg

Diese Tests beweisen weder das Home-Tasten-Verhalten der nativen TV-Komponente
noch Standby/Kaltstart auf unserem Gerät. Auch Firmware-Kompatibilität und Root
sind nicht bestätigt. Die Wiederherstellung der Samsung-Autostartoption ist nur
im simulierten Erfolgsfall getestet. Laut Quellcode kann sie scheitern und als
Statusfehler gemeldet werden; ein erfolgreicher HTTP-Aufruf allein genügt später
nicht als Restore-Nachweis. Vollständige Root-Rücknahme bleibt offen.

## Geplante Reihenfolge

1. Besitzer öffnet zunächst nur das Entwicklermenü und prüft die Anzeige.
   Samsung beschreibt: Apps/App Settings öffnen, 12345 eingeben.
   Einschalten, Host-PC-IP und Neustart sind spätere explizite Änderungen.
   Keine Firmware-Aktualisierung im Rahmen dieses Schritts.
2. Vor dem Einschalten Ausgangszustand und passende Mac-Schnittstelle lokal
   festhalten. Bei zwei aktiven Netzwerkinterfaces nicht die Hostadresse raten.
3. Den TV-Transport für die Installation klären: normales SDB nutzt Port 26101;
   der bisher erfolgreiche HTTP-Proxy-Test belegt dessen Nutzbarkeit nicht.
   Kein pauschales Freischalten des Heimnetzes und kein Suchlauf.
4. Werkzeugauswahl vor Download abschließen. Kandidat ist Apps2Samsung CLI
   für macOS arm64, weil es eigene WGT-Pakete signieren/installieren kann.
   Das ist keine Empfehlung für einen ungeprüften Katalog-Installationsbefehl:
   dieser würde nicht automatisch unseren Fork installieren.
   Vor Ausführung müssen Release/Prüfsumme, unterstützter Projekt-Datenordner,
   Zertifikatsspeicher, benötigte Verbindungen und Scan-/Autostartverhalten
   geprüft werden. Falls projektinterner Betrieb nicht möglich ist, Alternative
   konkret planen. Kein Entfernen von macOS-Schutzmarkierungen als Automatismus.
5. Exaktes eigenes Paket aus vollständigem, festgehaltenem Fork-Checkout bauen;
   Abhängigkeiten und Signierung separat freigeben. Samsung-Anmeldung und
   Passwörter gibt der Besitzer selbst ein. Dafür nötige externe Ziele benötigen
   separate Freigabe; die bestehende TV-Freigabe deckt sie nicht ab.
6. Vor-Installations-Baseline, kontrollierte Installation und erster Root-Test;
   anschließend Zustandsaufnahme, Launcher zunächst ausgeschaltet lassen.
7. Erst danach Launcher an/aus mit echter Rückleseprüfung testen; danach Home,
   Standby und Kaltstart. Keine Paketlöschungen oder Debloat-Aktionen.
8. Rücknahme schrittweise am Gerät prüfen. Ein JSON-Archiv ist kein
   Firmware-Backup und keine Garantie bei einem nicht mehr startenden TV.

Bis einschließlich dieser Vorbereitung: nur Dateien im Projekt geschrieben,
öffentliche Quellen gelesen, Offline-Tests und das beschriebene TV-GET ausgeführt.
Keine Installation, kein Root und keine TV-Einstellung geändert.

## Quellen

- [Samsung: TV Device](https://developer.samsung.com/smarttv/develop/getting-started/using-sdk/tv-device.html)
- [Apps2Samsung: Command line](https://github.com/Apps2Samsung/Apps2Samsung#command-line)
- [Vetro-Installationsablauf am geprüften Stand](https://github.com/Sheqoooo/vetro/blob/e35b8548f8d81377209a6434bd5051f06885baa5/app/docs/INSTALLATION.md)
- [Geprüfter Dock-Code](https://github.com/Sheqoooo/vetro/blob/e35b8548f8d81377209a6434bd5051f06885baa5/app/service/dock.js)
