# Arbeitsprotokoll dieses Forks

Dieses Protokoll beschreibt unsere Änderungen am Fork, nicht die gesamte
Entwicklungsgeschichte von Upstream-Vetro. Historische Befunde werden als solche
gekennzeichnet. Die Git-Commits sind die technische Änderungshistorie.

## Aktueller Stand

- Stand der Dokumentation: 2026-11-05, Datum nach Europe/Berlin.
- Arbeitsbranch: `codex/recovery-preparation`.
- Review: [Entwurf PR #1](https://github.com/Sheqoooo/vetro/pull/1).
- Ausgangscommit des PR: `52b02b4cf575aae64af149b77de400c873fc14fc`.
- Vorbereitung und Offline-Tests durchgeführt; keine TV-Installation, keine
  Root-Ausführung, kein TV-Netzwerkzugriff und kein Hardware-Restore-Test.
- Keine generelle Zusicherung, dass das Zielgerät kompatibel oder vollständig
  wiederherstellbar ist. Kein vollständiger lokaler Checkout von Vetro vorhanden.

## 2026-11-05 — Recherche und Quellcodeprüfung

**Zweck:** Vor einer Installation feststellen, welche Zustände Vetro verändert und
welche Daten für eine Rücknahme benötigt werden.

**Durchgeführt:** README, Installation, Sicherheits- und Beitragsregeln über den
GitHub-Connector gelesen. Ausgewählte Dateien in `app/service/` und
`rooting/service/platform.js` geprüft. Dateihashes der ausgewählten Quellen sind
in [SOURCE-REVIEW.json](SOURCE-REVIEW.json) erfasst. Diese Liste enthält Blob-Hashes;
sie ist kein Beleg für einen vollständig geprüften oder getesteten Build.

**Ergebnisse:**

1. Vetros Dock lässt die Default-Home-Zuordnung bestehen, fängt die Taste ab und
   schließt Samsung Home. Beim Einschalten kann Samsung-Oberfläche sichtbar werden.
2. Launcheraktivierung kann Autorun Smart Hub ändern. `autorunWas` wird TV-lokal
   gespeichert; eine erfolgreiche HTTP-Antwort allein beweist keinen Restore.
3. Die Integration kann nach Root-Verbindung die eigenen Startflags automatisch
   reparieren. Der Zustand vor Root/Installation muss gesondert dokumentiert werden.
4. Lokale Originalflag- und Home-Reihenfolge-Backups existieren; sie ergeben kein
   vollständiges Firmware-Backup und müssen vor Entfernung extern gesichert werden.
5. Das Browser-Dashboard verwendet HTTP ohne Benutzeranmeldung. Root-Agent-
   Authentifizierung ersetzt keine Zugriffskontrolle für das Dashboard.
6. Bei TV-Host-PC-IP `127.0.0.1` ist laut Installationsanleitung der normale
   Mac-SDB-Zugang nicht verfügbar. Updates und Rücknahme brauchen einen geplanten
   Wechsel und einen funktionierenden Zugang zu Samsungs Einstellungen.

Details und Quellen: [Einrichtungs- und Rücknahmeplan](ROLLOUT-AND-RECOVERY.md).

## 2026-11-05 — Lokale Vorbereitung und anfängliche Blockaden

**Durchgeführt:** Eigenes `recovery/`-Verzeichnis im dedizierten Projekt erstellt.
Kein Vetro-Dienst und kein fremdes Installationsskript gestartet.

- GitHub erlaubte zunächst Lesen, verweigerte aber das Anlegen des Arbeitsbranches
  mit HTTP 403, `Resource not accessible by integration`. Bis zur Behebung wurden
  die Dateien ausschließlich lokal vorbereitet. Kein anderer Schreibkanal wurde
  zur Umgehung des Fehlers benutzt.
- Die Aufrufe über `/usr/bin/git` und `/usr/bin/python3` meldeten zunächst fehlende
  Entwicklerwerkzeuge. Fehlende Installation und sandboxbedingt fehlender Zugriff
  wurden als mögliche Ursachen unterschieden; es wurde nichts nachinstalliert.
- Die Arbeit wurde auf ausdrücklichen Wunsch des Eigentümers pausiert.
- Der Eigentümer ergänzte selbst eine gezielte Lesefreigabe für
  `/Library/Developer/CommandLineTools`. Der Agent bearbeitete keine globale
  Codex-Konfiguration.
- Nach Wiederaufnahme funktionierten die direkten Werkzeugpfade. Git meldete
  2.39.3 (Apple Git-146), Python 3.9.6. Die Starter unter `/usr/bin` versuchten
  weiterhin Cache-Dateien im gesperrten System-Temp anzulegen; diese Versuche
  wurden blockiert. Direkte Aufrufe zeigten diese Meldung nicht.
- Eine unkritische Datei im Workspace war lesbar; eine vom Eigentümer angelegte
  Testdatei außerhalb wurde mit `Operation not permitted` blockiert. Das ist ein
  begrenzter Test dieser Pfade, kein Nachweis für jede mögliche Zugriffsmethode.
- Eine bereits mit der App gelieferte Node-Laufzeit meldete v24.22.1. Eine
  zwischenzeitlich erwogene Umstellung des Hilfswerkzeugs auf Node wurde nicht
  umgesetzt; das veröffentlichte Archivwerkzeug ist Python.

**Befehle zur Werkzeugprüfung:**

```sh
/Library/Developer/CommandLineTools/usr/bin/git --version
/Library/Developer/CommandLineTools/usr/bin/python3 --version
```

Die tatsächlichen Pfade privater Testdateien bleiben im lokalen Sitzungsverlauf.

## 2026-11-05 — Offline-Archivierungswerkzeug

**Problem:** Vor späteren Launcher-Änderungen brauchen wir eine lokale, nicht
versehentlich überschriebene Kopie der erfassten Exporte.

**Erstellt:**

| Datei | Zweck |
| --- | --- |
| `recovery/backup_exports.py` | Vorhandene JSON-Exporte archivieren und SHA-256 prüfen |
| `recovery/test_backup_exports.py` | Offline-Tests mit synthetischen Daten |
| `recovery/.gitignore` | Inbox, private Sicherungen und Python-Cache aus Git ausschließen |
| `recovery/README.md` | Bedienung, Voraussetzungen und Aussagegrenzen |
| `recovery/ROLLOUT-AND-RECOVERY.md` | Einführung, Sicherung, Rücknahme und Abnahmetests |
| `recovery/SOURCE-REVIEW.json` | Nachweis der ausgewählten gelesenen Quellversionen |

**Verhalten:** `capture` liest ausschließlich die sechs vorgesehenen Dateien
unter `recovery/inbox/` und erzeugt eine neue Sicherung unter `recovery/private/`.
Dateien werden exklusiv und mit 0600, Sicherungsverzeichnisse mit 0700 angelegt.
Das Manifest wird zuletzt geschrieben. `verify` prüft den vollständigen Dateisatz
gegen Größen und SHA-256 im Manifest. Das Werkzeug enthält keinen Netzwerkcode,
startet keine Unterprozesse und führt keine Inhalte aus den Exporten aus.

**Grenzen:** Es prüft keine vollständigen Vetro-API-Schemata und bestätigt keine
Geräteidentität. Die geforderten Exporte stammen aus der Phase nach Installation,
vor manuellen Nutzeränderungen. Sie ersetzen keine Vor-Root-Sicherung. Ein Angreifer,
der Daten und Manifest austauscht, wird durch SHA-256 allein nicht erkannt.
Es gibt noch keinen ausführbaren TV-Restore und keinen Netzwerk-Collector.

**Validierung:**

```sh
/Library/Developer/CommandLineTools/usr/bin/python3 -B -m unittest discover -s recovery -p 'test_*.py' -v
```

Ergebnis: **10 Tests erfolgreich**, Python 3.9.6. Geprüft wurden Rundlauf und
Dateirechte, fehlende Exporte, JSON-Fehlerantworten, Symlinks, Pfadüberschreitung,
nachträglich geänderte JSON-Daten, unvollständige Manifeste, Überschreibschutz,
unzulässige Erfassungsphase und Größenlimit. Ausschließlich lokale Testdaten;
temporäre Testverzeichnisse lagen innerhalb des Projekts und wurden entfernt.
Vetros App-/Root-Integrationssuite wurde nicht ausgeführt; App und Integration
wurden durch diese Änderungen nicht bearbeitet.

## 2026-11-05 — Übertragung in den Fork

Nach Behebung des GitHub-Zugriffs durch den Eigentümer funktionierte die
Branch-Erstellung. Alle folgenden Mutationen erfolgten über den GitHub-Connector:

1. `codex/recovery-preparation` von `main` angelegt.
2. Öffentliche Version der Anleitung hergestellt: lokale Gerätezuordnung entfernt
   und lokale Einrichtungsdetails verallgemeinert. Keine echten Exporte übertragen.
3. Sechs Dateien sequenziell über die Contents-API angelegt. Die API erzeugte
   dafür jeweils einen Commit; keine Änderung auf `main` und kein Merge.
4. Alle sechs Dateien aus dem Arbeitsbranch zurückgelesen und mit den vorbereiteten
   Inhalten verglichen: **6 von 6 identisch**.
5. Entwurf PR #1 ausschließlich innerhalb dieses Forks geöffnet, nicht bei Upstream.

| Commit | Datei |
| --- | --- |
| `d383358c9e7adc8c4e1a7cdd6d60fdeee0ef20e3` | `recovery/.gitignore` |
| `93578368bc50a74f3bd536e5f311f998bdc9a09d` | `recovery/backup_exports.py` |
| `4abe40446fc1336c190e7a9b9b9c09eef18915ca` | `recovery/test_backup_exports.py` |
| `035d6fd7cbca821b3863faea4dd568f7eb01d076` | `recovery/README.md` |
| `61483a805a1c33ab3a6116e5ee2eab6e796c1810` | `recovery/SOURCE-REVIEW.json` |
| `794d18963a34c99086f6623a3b613694144b43f7` | `recovery/ROLLOUT-AND-RECOVERY.md` |

Ein Versuch, lokale Inhalte über einen Shell-Heredoc einzulesen, wurde wegen der
gesperrten System-Temp-Datei blockiert. Danach wurde derselbe reine Lesevorgang
über `python3 -B -c` ohne temporäre Datei ausgeführt. Keine Temp-Freigabe erweitert.

## 2026-11-05 — Dokumentationsstandard ergänzt

Auf ausdrücklichen Wunsch des Eigentümers dieses Arbeitsprotokoll und eine
Vorlage für alle weiteren Arbeitsschritte ergänzt. Die README verlinkt die
Dokumente. Repository-Anweisungen verlangen künftig die Aktualisierung des
Arbeitsprotokolls bei jeder relevanten Änderung, Prüfung und Blockade.

Diese Ergänzung betrifft Dokumentation, keine TV-Funktionen. Für sie wird kein
erneuter Hardware- oder App-Test behauptet. Commitnummern dieser Ergänzung sind
in der Git-Historie des PR nachzulesen; ein Dokument kann seinen eigenen finalen
Commit-Hash nicht ohne eine weitere Änderung enthalten.

## 2026-11-05 — Netztrennung des Heimrouters geprüft

**Durchgeführt:** Offizielle FRITZ!-Dokumentation zum Gastzugang gelesen, keine
Routeroberfläche geöffnet und keine Netzwerkgeräte kontaktiert.

**Belegt:** Gast- und Heimnetz sind getrennt. Kommunikation innerhalb des
Gast-WLANs ist eine separate, gemeinsam geltende Option. Alle Gastgeräte
verwenden das Gast-Zugangsprofil. Das dokumentierte Menü ist keine belegte
Regelverwaltung für einzelne Client-/TV-Portpaare.

**Folgerung für die Planung:** TV und Entwicklungsumgebung könnten gemeinsam
ein ausschließlich für sie verwendetes Gastnetz nutzen, wenn Kommunikation
zwischen Gästen erlaubt wird. Dann dürfen keine weiteren Gastgeräte dort
sein. Zusätzliche Heimnetzverbindungen des Entwicklungsgeräts, etwa Ethernet,
VPN oder eine zweite Schnittstelle, würden die gewünschte Abschottung gefährden.

Diese Variante isoliert das Heimnetz, aber nicht den Entwicklungs-Mac vom TV
und beschränkt das Internet nicht automatisch auf notwendige Codex-Ziele.
Sie erfüllt daher allein nicht alle bisherigen Sicherheitsanforderungen.
Eine unabhängig kontrollierte Firewall/isolierte Entwicklungsumgebung bleibt
für diese weitergehenden Anforderungen zu planen. Keine Freigabe erweitert.

**Noch zu klären:** Bestehende Gastnetz-Nutzung, Anschluss des Entwicklungsgeräts,
FRITZ!OS-Stand und zusätzliche Netzwerkkomponenten. Keine IP-Adressen oder
Zugangsdaten veröffentlicht. Kein technischer Isolationstest durchgeführt.

**Quelle:** [FRITZ!: WLAN-Gastzugang, Dokument 294](https://uk.fritz.com/service/knowledge-base/dok/FRITZ-Box-6660-Cable/294_Setting-up-Wi-Fi-guest-access-in-the-FRITZ-Box/).
Die konkrete installierte FRITZ!OS-Oberfläche wurde nicht eingesehen.

## 2026-11-06 — Erster gezielter Verbindungsversuch

Der Eigentümer möchte vorerst im vorhandenen Heimnetz weiterarbeiten, ohne
VM oder Gastnetz. Es wurde erläutert und akzeptiert, dass die Beschränkung
auf den TV damit eine Arbeitsregel und keine technische Zielnetz-Sperre ist.
Die ursprüngliche Vorgabe zur technischen Isolation ist damit für diesen
vorläufigen Ablauf nicht erfüllt; die Dateilesesperre bleibt bestehen.

**Autorisierter Test:** Einmaliger HTTP-GET an den vom Eigentümer genannten
TV, TCP 8001, Pfad /api/v2/. Python http.client mit numerischer Zieladresse,
5 Sekunden Timeout, begrenzter Antwortgröße, ohne Proxy, Redirect-Verfolgung,
Gerätesuche, Installation oder Root. Die echte IP bleibt privat.

**Ergebnis:** Der normale Sandbox-Aufruf lieferte PermissionError,
Errno 1, Operation not permitted. Auch der daraufhin separat angefragte
Ausführungsversuch lieferte denselben Fehler. Keine HTTP-Antwort erhalten;
Geräteidentität, Erreichbarkeit und API-Inhalt bleiben unbestätigt.
Aus dem Fehler lässt sich nicht sicher zwischen Harness-/Sandbox-Regeln
und macOS-Netzwerk-Datenschutz unterscheiden.

**Nächste Diagnose:** Lokale Netzwerkfreigabe der ausführenden App in macOS
zunächst vom Eigentümer prüfen lassen; nicht automatisch ändern oder die
Blockade über Browser/andere Werkzeuge umgehen. Keine weiteren Geräte
angesprochen und keine TV-Einstellungen verändert.

Quelle für die macOS-Berechtigung:
[Apple: Zugriff auf das lokale Netzwerk steuern](https://support.apple.com/de-de/guide/mac-help/mchla4f49138/mac).

## 2026-11-06 — Geräteabfrage auf Wunsch wiederholt

Denselben begrenzten GET /api/v2/ an den privat festgelegten TV auf TCP 8001
erneut ausgeführt, ohne Scan, Proxy oder Redirect-Verfolgung.
Normaler Sandbox-Versuch und separat angefragter erweiterter Versuch lieferten
erneut PermissionError, Errno 1, Operation not permitted. Keine HTTP-Antwort;
keine Installation oder TV-Schreiboperation. Die konkrete blockierende Schicht
bleibt ungeklärt. Keine Umgehung über andere Verbindungswerkzeuge versucht.

## 2026-11-06 — IP-Freigabe über den verwalteten Proxy bestätigt

**Anlass:** Der Eigentümer hat eine auf die TV-IP begrenzte Netzwerkfreigabe
eingerichtet und um eine positive und negative Gegenprobe gebeten.

**Durchführung und Ergebnis:**

1. Direkter Python-HTTP-Zugriff auf die freigegebene TV-IP, TCP 8001:
   PermissionError / EPERM.
2. Direkter TCP-Verbindungsversuch zur öffentlichen Kontrolladresse 1.1.1.1,
   TCP 443: ebenfalls EPERM. Keine weiteren Heimnetzgeräte als Kontrollziele benutzt.
3. Proxy-Variablen sind vorhanden (nur deren Vorhandensein geprüft, keine
   Zugangsdaten oder vollständigen Proxy-URLs protokolliert).
4. Gezielte TV-Abfrage mit curl über den konfigurierten Proxy, GET /api/v2/:
   HTTP 200, Tizen und mit dem lokal bekannten Modell übereinstimmende Gerätekennung.
   Entwicklerstatus 0, also Entwicklermodus laut API aus.
5. HTTPS-Gegenprobe zu 1.1.1.1 über denselben Proxy: Der Harness verweigerte sie
   ausdrücklich mit "domain is not on the allowlist for the current sandbox mode".
   Keine Eskalation oder alternative Umgehung dieser erwarteten Sperre angefordert.
   Der kombinierte Aufruf lieferte wegen dieser Sperre kein positives Teilergebnis;
   deshalb wurde die erlaubte TV-Abfrage anschließend separat ausgeführt.

**Parameter:** Direkte Versuche mit 4 Sekunden Timeout; curl mit 4 Sekunden
Verbindungs- und 6 Sekunden Gesamttimeout, ohne Weiterleitung und mit 256-KiB-
Antwortlimit. curl verwendete die vorhandenen Proxy-Variablen; --noproxy mit
leerem Wert verhinderte einen direkten lokalen Bypass. Kein Netzwerkscan,
keine Installation und keine TV-Schreiboperation.

**Korrektur früherer Diagnose:** Die vorherigen direkten Python-Abfragen nutzten
den verwalteten Proxy nicht. Ihr EPERM allein belegte weder Unerreichbarkeit
des TVs noch eine fehlende macOS-Lokalnetzfreigabe. Der nun funktionierende
Proxy-Weg ist für weitere HTTP-Abfragen zu verwenden.

**Aussagegrenze:** Positiver Test des TV-Ziels und negativer Test einer öffentlichen
Kontrolladresse, keine vollständige Prüfung aller IPs, Ports, IPv6-/DNS-Wege oder
des gesamten effektiven Regelwerks. Websuche, Connectoren, Browser und externe
MCP-Prozesse können eigenen Richtlinien unterliegen. SDB-Zugriff und die
Root-/Installationsverbindung sind noch nicht geprüft; ein funktionierendes
HTTP-GET beweist keine SDB-Kompatibilität mit dem Proxy.
Die reale TV-IP und private Gerätekennung bleiben außerhalb dieses Protokolls.

## Noch offen

- Netzwerkisolation und erlaubte Verbindungsziele konkret einrichten und abnehmen.
- Exakten Build-Commit und vollständigen Checkout für spätere Builds festhalten.
- Werkzeuginstallation und Signierung einzeln vorbereiten und freigeben.
- Vor-Root-Baseline am Zielgerät erfassen, soweit ohne Root möglich; Lücken nennen.
- Gerätespezifischen Restore implementieren und klein beginnen: Launcher an/aus
  mit Rückleseprüfung, bevor weitere Funktionen geändert werden.
- Standby, Home aus Apps/HDMI und echten Kaltstart am Zielgerät testen.

Für weitere Einträge die [Protokollvorlage](STEP-TEMPLATE.md) verwenden. Frühere
Fehler und Einschränkungen nicht stillschweigend aus der Historie entfernen;
Korrekturen als neuen Eintrag kenntlich machen.

## 2026-11-06 — Launcher offline geprüft, Geräteschritt vorbereitet

**Status:** durchgeführt; kein Hardware-Funktionstest und keine Installation.

**Ziel/Freigabe:** Projekt auf Wunsch des Besitzers fortsetzen, vorhandene
Launcher- und Rückweglogik vor einem TV-Schreibzugriff prüfen. Die Freigabe zur
Weiterarbeit wurde nicht als neue Installations- oder Root-Freigabe ausgelegt.

**Ausgangsstand:** Fork-Head e35b8548f8d81377209a6434bd5051f06885baa5.
GitHub-PR-Metadaten und rekursiven Git-Baum über den Connector gelesen. Ein
vorheriger Branch-URL-Aufruf mit kodiertem Schrägstrich wurde vom Connector als
ungültiger Repositorypfad abgewiesen; keine Änderung. Eine ausgewählte lokale
Quellkopie mit Blob-Manifest angelegt, ausdrücklich kein vollständiger Checkout.
AGENTS.md, CONTRIBUTING.md und LICENSE mit aufgenommen. Keine Fernskripte
installiert oder Buildskripte ausgeführt.

**Durchführung/Ergebnis:** Vorhandenes gebündeltes Node 24.22.1 für zwei
Launcher-Tests verwendet. Erster Start beider Tests scheiterte am gesperrten
System-OpenSSL-Konfigurationszugriff. Prozesslokale leere Konfiguration und
TMPDIR im ignorierten Projektunterordner verwendet, ohne zusätzliche Rechte.
Katalogtest danach bestanden. Docktest zunächst wegen gesperrter Host-Uptime
abgebrochen; ausschließlich im Testprozess os.uptime auf 3600 Sekunden gesetzt
(`offline-test-host.cjs`). Explizite Boot-Zeitmodelle der Tests bleiben wirksam.
Docktest danach bestanden. Keine Produktänderung.
Aufrufe und Grenzen: [LAUNCHER-PREFLIGHT.md](LAUNCHER-PREFLIGHT.md).

**TV-Prüfung:** Erneutes ausschließlich lesendes GET auf TV_IP:8001/api/v2/
über curl mit erzwungenem verwaltetem Proxy und Zeitlimit. Nur OS und
developerMode ausgegeben: Tizen, Modus 0. Keine private API-Antwort gespeichert
oder veröffentlicht, keine anderen LAN-Ziele, keine SDB-Verbindung.
Mac-Architektur über uname -m als arm64 festgestellt.

**Quellen/Plan:** Samsung-Geräteanleitung und Apps2Samsung-Projektinformationen
gelesen. Ein vermuteter Apps2Samsung.Cli/README.md-Rawpfad lieferte 404; stattdessen
den vorhandenen README-Abschnitt Command line gelesen. CLI als noch zu prüfender
Kandidat, kein Download. Projektinterne Datenhaltung und SDB-Transport noch offen.
Aktuelle Quellen und Reihenfolge in LAUNCHER-PREFLIGHT.md.

**Rücknahme/Risiken:** Neue Vorbereitung lässt sich durch Entfernen genau der neu
angelegten Quellkopie, Testhilfsdatei, synthetischen temporären Testdaten und
Dokumente rückgängig machen; kein TV- oder System-Rollback erforderlich.
Keine Löschung ausgeführt. Der Dock-Quellcode meldet fehlgeschlagene
Autostart-Wiederherstellung über einen Statusfehler; das ist noch nicht auf
Hardware geprüft. Kein Nachweis für vollständige Root-Rücknahme. Nächster
Besitzerschritt ist zunächst nur das Öffnen des Entwicklermenüs.

## 2026-11-06 — Entwicklermodus nach Besitzer-Neustart bestätigt

**Status/Freigabe:** Besitzer hat das Entwicklermenü geöffnet, die lokale
Host-PC-Adresse angegeben und den TV auf Anleitung neu gestartet. Diese manuelle
TV-Einstellung wurde vom Besitzer vorgenommen, nicht durch Agenten-Schreibzugriff.
Reale Host-/TV-Adressen bleiben außerhalb des öffentlichen Protokolls.

**Validierung:** Ausschließlich lesendes GET auf TV_IP:8001/api/v2/ über
curl mit erzwungenem verwaltetem Proxy, 3 Sekunden Verbindungs- und 6 Sekunden
Gesamtlimit. Ausgabe auf OS und developerMode begrenzt: Tizen, developerMode "1".
Zuvor wurde "0" gelesen. Dies bestätigt den Entwicklermodus, nicht die eingetragene
Host-PC-Adresse oder eine erfolgreiche Geräteautorisierung.

**Transportprüfung:** Anschließend Python-Standardbibliothek http.client mit
dem vorhandenen verwalteten Proxy verwendet: HTTP CONNECT ausschließlich zu
TV_IP:26101, 4 Sekunden Timeout; Tunnel erfolgreich aufgebaut und sofort geschlossen.
Keine SDB-Protokollnachrichten, Authentifizierungsbefehle oder Installationsdaten
gesendet. Proxy-Zugangsdaten wurden weder ausgegeben noch gespeichert.
Der erfolgreiche CONNECT bestätigt den Tunnelaufbau; eine vollständige
SDB-Protokollverbindung oder die Proxy-Unterstützung eines späteren Installers
ist damit noch nicht bewiesen. Keine Umgehung der bestehenden Netzfreigabe.

**Änderungen/Rücknahme:** Keine Software installiert, kein Root, keine App
gestartet oder ersetzt. Einziger TV-Änderungsschritt in dieser Phase ist die vom
Besitzer vorgenommene Entwicklermodus-Konfiguration. Für deren Rücknahme ursprüngliche
Host-PC-Einstellung wiederherstellen, Entwicklermodus wie ursprünglich ausschalten
und TV neu starten; dieser Rückweg wurde noch nicht durchgeführt. Ursprünglich
war der Modus ausgeschaltet, der genaue frühere Feldinhalt wurde nicht archiviert.

**Nächster Schritt:** Installer-Version, projektinterne Daten-/Zertifikatsablage
und Nutzung des verwalteten TV-Tunnels konkret prüfen. Werkzeugdownload und
Installation bleiben separat freizugebende Schritte.
