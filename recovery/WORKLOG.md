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

## 2026-11-06 — Installationswerkzeug gegen Sicherheitsanforderungen geprüft

**Status/Freigabe:** Auf Wunsch Ablauf konkretisiert, ausschließlich öffentliche
Quellen und Release-Metadaten gelesen. Keine Installationsfreigabe abgeleitet.

**Ergebnis:** Apps2Samsung CLI v3.1.0/macOS arm64 mit Release-Commit und erwarteter
Prüfsumme festgehalten. --data-dir deckt laut Quellcode nicht alle macOS-Pfade ab;
zusätzlich automatischer KillSdbServers-Callback vor Verbindungen gefunden.
Proxy-Kompatibilität der SDB-Integration noch nicht bestätigt. Daher unveränderte
CLI nicht ausgeführt oder als einsatzbereit eingestuft. Vollständige Befunde,
erfolgreiche/fehlgeschlagene Quellabrufe, Einschränkungen, Quellen und Phasen:
[INSTALLER-REVIEW.md](INSTALLER-REVIEW.md).

**Änderungen/Rücknahme:** Nur dieses Protokoll und neue Prüfungsdokumentation
geschrieben/veröffentlicht; keine Binärdateien, Werkzeuginstallation,
TV-Kommandos, Zertifikatserzeugung oder globalen Konfigurationsänderungen.
Anpassung/Alternative bleibt vorzubereiten. Bisherige Isolation bleibt bestehen.

## 2026-11-06 — Unveränderten Installer auf Besitzerwunsch versucht

**Freigabe:** Besitzer möchte die normale Apps2Samsung-Version mit bestehenden
Berechtigungen ausprobieren; kein zweiter Fork. Vorbereitung und Startprüfung,
noch keine TV-Installation oder Root-Ausführung.

**Durchführung:** Projektinterne Ordner tools/downloads, tools/apps2samsung,
recovery/private/apps2samsung und recovery/private/tool-tmp angelegt. Download
des festgehaltenen originalen macOS-arm64-CLI-Assets v3.1.0 über curl versucht.
Die verwaltete Netzwerkprüfung blockierte github.com, weil die Domain nicht auf
der Allowlist steht. Anschließend für genau denselben Download eine einzelne
erweiterte Ausführung angefordert; auch dieser Versuch wurde mit derselben
Netzwerk-Allowlist-Meldung blockiert. Kein alternativer Downloadweg verwendet.

**Ergebnis:** Download nicht erfolgreich; keine Prüfsummenvalidierung,
Entpackung oder Werkzeugausführung. Keine Verbindung zum TV in diesem Schritt,
keine TV-Änderung, keine Änderung der globalen Berechtigungen.
Nächste Option: Besitzer lädt das genau verlinkte Release-Asset selbst herunter
und legt es im Projektordner tools/downloads ab. Erst danach Integrität,
Archivpfade und unveränderten Start mit weiterhin bestehenden Grenzen prüfen.

**Rücknahme:** Nur neue leere Vorbereitungsordner angelegt; nichts gelöscht.

## 2026-11-16 — Originalinstaller und Vetro vollständig offline vorbereitet

**Status:** durchgeführt und offline geprüft; keine Hardwareprüfung.

**Freigabe und Ausgangslage:** Besitzer erlaubt jetzt den Download der normalen
Apps2Samsung-Version und bittet um vollständige Vorbereitung mit einfacher
Dokumentation. Besitzer ist in einem anderen Netz; deshalb heute keinerlei
TV-Kontakt, Netzscan, SDB-Verbindung, Anmeldung oder TV-Schreiboperation.
Vorherige geplante Apps2Samsung-Anpassung wird nicht umgesetzt. Die historischen
Quellbefunde werden nicht entfernt und bleiben für den späteren Installationspfad
relevant.

**Durchführung, in Reihenfolge:**
1. Lokale Prüfunterlagen und Repo-Anweisungen gelesen. GitHub-Release-Metadaten für
   das bereits festgehaltene v3.1.0 erneut gelesen, kein automatisches Versionsupdate.
2. Original-Asset macOS arm64 mit curl über den verwalteten Proxy nach
   tools/downloads geladen; erfolgreich, ohne zusätzliche Freigabeanforderung.
   SHA-256 stimmt mit dem Release überein. Archivpfade und Dateitypen vor Extraktion
   geprüft; genau Verzeichnis plus reguläre Programmdatei. Nur diese Datei ins
   Projekt extrahiert und dort ausführbar gemacht; kein Systeminstaller.
3. codesign-Integritätsprüfung erfolgreich. Ausführliche Anzeige bestätigt eine
   Ad-hoc-Signatur ohne TeamIdentifier: kein Beleg einer Entwickleridentität oder
   Notarisierung. Keine Quarantäneattribute entfernt. Exakte Hashes in TOOLS.json.
4. --version und --help erfolgreich mit prozesslokalen Daten-/Temp-/Dotnet-Pfaden.
   Meldung 3.1.0+dea1eb391d559b3176f40f612550bdae0cebc493.
5. Den vollständigen öffentlichen Vetro-Fork in neues Unterverzeichnis vetro
   geklont; Branch codex/recovery-preparation, Ausgangscommit
   af64ee55d0af29c6d87aa360adb02ce70c17f176. Bestehende Workspace-Dateien erhalten.
   Git dabei ohne globale Benutzer-/Systemkonfiguration und ohne Terminalprompt.
6. Original-CLI-Quellen Program.cs und CertCommand.cs am festen Release gelesen.
   cert --json ohne TV-Adresse/--prepare erfolgreich: Public und Partner fehlen.
   Keine Zertifikate erzeugt. Daten liegen im eigenen privaten Projektunterordner.
7. apps2samsung_offline.py angelegt: prüft Archivhash plus Programmvergleich,
   setzt nur Prozesspfade, erhält echten HOME-Wert und erlaubt nur vier lokale
   Aktionen. Zertifikatsliste und Installationshilfe darüber erfolgreich.
   Negativtest scan: Exitcode 2 vor Start der CLI, keine Netzsuche.
8. build-unsigned.cjs angelegt: nutzt unveränderte Upstream-Kollektoren und
   ZIP-Funktion. Zwei unsignierte Pakete erzeugt, ohne npm-Installation,
   Signierungsabhängigkeiten oder Ausführen der eingepackten TV-Payloads.
   Quellstand und Hashes in dist/OFFLINE-BUILD.json. Keine Produktquelle geändert.
9. Fünf gezielte vorhandene Offline-Tests bestanden: App-Build, Integrationsgrenze,
   Node-4-Syntaxwächter, Dock-Lebenszyklus und Dock-Katalog. Node 24.22.1, bestehender
   Test-Preload für Host-Uptime; OPENSSL_CONF und TMPDIR projektintern.
10. Beide Pakete zusätzlich mit unabhängigem Python-ZIP/XML-Leser auf CRC,
    Hash, Manifest, eindeutige Einträge, fehlende Signaturen und korrekte
    Payload-Trennung geprüft; erfolgreich.
11. Einfache Anleitung START-HIER.md, technische Reproduktion
    OFFLINE-PREPARATION.md, Werkzeugmanifest TOOLS.json und README-Verweis
    vorbereitet. Keine Binärdateien, echten Exporte oder persönlichen Pfade
    werden veröffentlicht.

**Ergebnis/Validierung:** Originalwerkzeug startet und kann seinen leeren lokalen
Zertifikatsspeicher lesen. App-Paket: 775968 Bytes/64 Einträge; Integrationspaket:
901117 Bytes/79 Einträge. Beide unsigniert, nicht auf Hardware getestet, nicht
installationsbereit. Exakte Kommandos/Hashes stehen in OFFLINE-PREPARATION.md.
Kein vollständiger Testlauf aller Tests, keine Vetro-Serverinstanz auf dem Mac.

**Sicherheitsgrenzen:** Bestehende verwaltete Dateisperren bleiben die technische
Grenze. Umgebungsvariablen, Gitignore und der Offline-Starthelfer ersetzen sie nicht.
SDB über den Proxy sowie produktive Cache-/Logpfade der Original-CLI sind weiterhin
nicht geprüft. Kein automatisches Beenden eines SDB-Prozesses ausgelöst, weil
keine Verbindung aufgebaut wurde. Keine globalen Codex-/macOS-Einstellungen
verändert, kein sudo und keine neuen Administratorrechte.

**Rücknahme/offen:** Neu angelegte Werkzeugdateien, Checkout, Buildausgaben und
synthetische temporäre Daten sind projektlokal und können gezielt entfernt werden;
keine Löschung durchgeführt. Vor später vorhandenen Zertifikaten/Sicherungen
separate Sicherung/Freigabe. Heute kein TV-Rollback nötig. Frühere manuelle
Entwicklermodus-Einstellung bleibt bestehen; aktuelle Adressen erst zu Hause
erneut prüfen. Samsung-Zertifikat, Signierung, Installation, Root und echter
Launcher-Rückweg bleiben die nächsten einzeln zu bestätigenden Schritte.

## 2026-11-17 — Original-Apps2Samsung erfolgreich mit dem TV verbunden

**Status/Freigabe:** Besitzer meldet TV bereit. Wie angekündigt ausschließlich
Verbindungs-/Informationsprüfung, keine Installations- oder Root-Freigabe abgeleitet.

**Ablauf:** Repo-Anweisungen und vorhandenen Offline-Helfer gelesen. Zuerst
GET auf TV_IP:8001/api/v2/ per curl über den verwalteten Proxy mit 3 Sekunden
Verbindungs-/6 Sekunden Gesamtlimit: OS Tizen und developerMode "1".
Anschließend TvCommand.cs am originalen Release v3.1.0 gelesen und den originalen
Installer erneut gegen Archivhash/Archivinhalt geprüft. Aufruf:
apps2samsung-cli tv TV_IP --local-ip HOST_IP --json, ohne scan, install oder launch.
Prozesslokale Daten-/Temp-/Dotnet-Pfade wie am Vortag; vorhandene Proxyvariablen
übernommen und NO_PROXY für diesen Prozess geleert. Der Offline-Helfer wurde
nicht um Netzwerkaktionen erweitert; Aufruf erfolgte separat mit festem Ziel.
Gesamtzeitlimit des Elternprozesses: 40 Sekunden.

**Tatsächliches Ergebnis:** Exitcode 0, ok=true, developerMode=true,
debugPortOpen=true, ready=true. Tizen-Version "6.0" und gültige DUID gelesen.
Private Gerätewerte/Adressen wurden nicht ausgegeben, gespeichert oder veröffentlicht;
nur Vorhandensein der DUID und die genannten nicht-identifizierenden Statuswerte.
TizenDeviceInfoService.cs anschließend am festen Release gegengeprüft:
DUID-/Capability-Leseaufrufe und HTTP-Geräteinformationen, kein Diagnose-,
Installations-, Deinstallations- oder Root-Aufruf.

**Korrektur bisher offener Einschränkung:** Eine echte SDB-Informationsabfrage
mit dem unveränderten Originalprogramm funktioniert nun in der aktuellen Sitzung.
Das beweist nicht die Freigabe aller später nötigen Ziele oder aller Installationspfade.
Kein allgemeiner Netzwerkscan und kein anderes Heimnetzgerät angesprochen.
Die lokale SDB-Verbindungsroutine kann laut früherer Quellprüfung konkurrierende
sdb-Prozesse zu beenden versuchen; ob dabei ein vorhandener Prozess betroffen war,
wurde nicht unabhängig beobachtet. SDB-Authentifizierung kann lokale Schlüssel
im privaten Projekt-Datenverzeichnis erzeugen; das ist von TV-Einstellungen zu
unterscheiden.

**Rücknahme/offen:** Keine TV-App oder TV-Einstellung geändert; Debug-Verbindung
mit Prozessende geschlossen. Keine Zertifikatserzeugung, keine Samsung-Anmeldung
oder Installation durchgeführt. Nächster genehmigungspflichtiger Schritt ist die
Vorbereitung eines eigenen Signierungszertifikats; Anmeldung durch Besitzer,
keine Passwörter im Chat. Allgemeine Root-Rücknahme weiterhin nicht nachgewiesen.

## 2026-11-17 — Zertifikatserstellung vor Empfangsport angehalten

**Freigabe:** Besitzer erlaubt Erstellung des eigenen Signierungszertifikats.
Vor Ausführung Login-/Zertifikatspfad des Originalprogramms genauer gelesen.

**Konkreter neuer Befund:** BrowserSamsungLogin.cs am festen v3.1.0 erstellt
TcpListener(IPAddress.IPv6Any, CallbackPort) mit DualMode=true. SamsungOAuth.cs
setzt CallbackPort=4794 und CallbackPath=/signin/callback. Der Listener ist damit
programmseitig nicht auf Loopback begrenzt, obwohl die Redirect-URL localhost
verwendet. Ob eine vorhandene Host-/Netzwerksperre externe Verbindungen abweist,
wurde nicht getestet und nicht vorausgesetzt. Die Anmeldeantwort wird im Code
gegen einen fest hinterlegten state-Wert geprüft; dieser ist keine zufällige
pro-Sitzung erzeugte Freigabe.

**Aktualitätsprüfung:** Aktuelles Originalrelease über GitHub-Metadaten gelesen:
v3.3.0 vom 2026-11-11, Commit cc92eec46a756479c74adcbd9e297d7a8d82e6cd.
Dort im gleichen Login-Quellpfad weiterhin IPv6Any/DualMode. Kein neues Release
heruntergeladen oder ausgeführt; vorhandenes Werkzeug bleibt v3.1.0.
Certificates.cs am festen v3.1.0 ebenfalls gelesen; Partnerauswahl wäre
für unseren Integrationsweg explizit zu setzen.

**Ergebnis/Rücknahme:** Noch kein cert --prepare gestartet, kein Empfangsport
gebunden, keine Anmeldung geöffnet und kein Zertifikat erzeugt. Nichts am TV
installiert oder geändert. Aufgrund der ursprünglichen Vorgabe zum Heimnetzzugriff
wird vor einem solchen Listener die konkrete zusätzliche Freigabe eingeholt.
Eine nur lokal erreichbare Alternative ist noch nicht implementiert oder geprüft.
Keine Rücknahme nötig.

**Quellen:** Apps2Samsung/Apps2Samsung, v3.1.0:
Apps2Samsung.Cli/BrowserSamsungLogin.cs,
Apps2Samsung.Cli/Commands/Certificates.cs,
Apps2Samsung.Core/Samsung/SamsungOAuth.cs;
Aktualitätsabgleich BrowserSamsungLogin.cs am v3.3.0-Tag.

## 2026-11-17 — Partner-Zertifikatsanmeldung wartet auf Besitzer

**Freigabe:** Besitzer erlaubt ausdrücklich die vorübergehende Erreichbarkeit
im Heimnetz für die zuvor erklärte Anmeldung. Das hebt keine Dateisperren auf
und autorisiert keine Zugriffe auf andere Heimnetzgeräte.

**Durchführung:** Unveränderte CLI v3.1.0 gestartet:
cert --tv TV_IP --partner --prepare --no-browser --login-timeout 600 --json.
Daten-/Temp-/Dotnet-Verzeichnisse wie vorbereitet projektintern gesetzt;
NO_PROXY/no_proxy für localhost, 127.0.0.1 und ::1 prozesslokal gesetzt.
Keine globale Einstellung verändert. DUID gelesen, Partnerprofil fehlt,
Login-URL ausgegeben und Callback-Empfänger gestartet. Besitzer öffnet die
offizielle Samsung-Anmeldeseite selbst auf demselben Mac. Keine Passwörter,
Anmeldecodes oder Tokens im Protokoll.

**Status:** Anmeldung wartet auf Besitzer, maximal zehn Minuten ab Prozessstart.
Noch kein Erfolg bei Zertifikatserzeugung bestätigt. Keine TV-App installiert,
kein Root. Bei Abbruch oder Ablauf wird der CLI-Prozess/Empfangsport beendet;
erzeugte private Daten verbleiben bis zur gezielten Prüfung im Projektordner.
Abschlusszustand wird nach der Anmeldung nachgetragen.

## 2026-11-17 — Zertifikate ausgestellt, lokaler Schlüsselbundfehler eingegrenzt

**Status/Freigabe:** Besitzer hat Samsung-Anmeldung abgeschlossen und bittet um
Fortsetzung. Genehmigt sind Zertifikatserstellung/Diagnose; keine TV-Installation.

**Abschluss der Anmeldung:** Ursprünglicher cert-Prozess mit Exitcode 0 beendet.
Fortschrittsausgabe meldet Samsung-Author-/Distributor-Antworten und PFX-Export.
JSON meldet ok=true/Partnerprofil vorhanden, gleichzeitig usable=false und leere
erkannte DUID-Abdeckung. Daher keine pauschale Aussage "signierbereit".
Raw-Ausgabe/DUID werden nicht veröffentlicht.

**Prüfungen:** Vorhandene Zertifikatsdateien nur im privaten Projektordner auf
Größe/Rechte geprüft und anschließend Ordner auf 0700, Dateien auf 0600 gesetzt.
Mit bereits vorhandenem OpenSSL PKCS#12 beider Dateien unter Verwendung von
-passin file:PRIVATE_PASSWORD_FILE und -noout geprüft; jeweils Exitcode 0.
Separat x509 -noout -dates für ausgestellte Author-/Distributor-Dateien gelesen:
17. November 2026 bis 17. November 2027. Kein Passwort/Schlüssel ausgegeben.
Keine Garantie für Geräteabdeckung, Signaturkette oder Hardwareakzeptanz abgeleitet.

**Empfangsport:** CLI-Prozess beendet. Ein lsof-Versuch meldete eine unzugängliche
eingehängte Dateisystemquelle und unvollständige Ergebnisse; kein verlässlicher
Nachweis daraus abgeleitet und keine Mount-/Gerätekennung veröffentlicht.
Danach connect_ex auf ausschließlich 127.0.0.1:4794 und [::1]:4794:
jeweils 61/ECONNREFUSED. Zusammen mit Prozessende kein eigener Listener mehr aktiv.

**Lokale Fehlerdiagnose:** cert-status ohne TV wiederholt: weiterhin unusable.
Profilprüfungs-, Zertifikatshelper- und Plattformquellen am festen v3.1.0 gelesen.
Ein zunächst vermuteter PlatformService-Pfad unter Services lieferte 404; über
den Release-Git-Baum den tatsächlichen Pfad Core/PlatformService.cs gefunden.
Die Implementierung lädt PKCS#12 über X509Certificate2/Exportable und verschluckt
Ladeausnahmen in der Profilanzeige.

Mit bereits eingebautem .NET-EventPipe einen weiteren rein lokalen cert --json
Prozess beobachtet: DOTNET_EnableEventPipe=1,
DOTNET_EventPipeConfig=Microsoft-Windows-DotNETRuntime:8000:5,
DOTNET_EventPipeCircularMB=4, Ausgabepfad im privaten Projektordner.
Nur gefilterte Fehlermeldungen betrachtet; private nettrace-Datei auf 0600.
Befund: AppleCommonCryptoCryptographicException, CreateTemporaryKeychain und
"The specified keychain could not be found." Kein neues Diagnosetool installiert.
Microsofts aktuelle offizielle Dokumentation bestätigt das benötigte
macOS-Keychainobjekt für das Laden privater PKCS#12-Schlüssel.
Dass gerade die verwalteten Einschränkungen den Fehler verursachen, ist weiterhin
eine plausible Erklärung, kein vollständig bewiesener Einzelpfad.

**Nächster Weg vorbereitet:** Upstream-Vetro rooting/build.cjs und vorhandenes
package-lock.json gelesen. Alternative Signierung über node-forge/jszip/tizen.js;
Git-Abhängigkeit auf 45b00106149d0c8eff74ead4a979c909dd80efd6 festgelegt,
npm-Abhängigkeiten mit Integritätshashes, laut Lockfile keine Installationsskripte.
Paketmetadaten und Git-Baum dieser tizen.js-Revision gelesen (GPL-3.0-only).
Noch keine Build-Bibliotheken heruntergeladen oder ausgeführt. Vor diesem
zusätzlichen Werkzeugweg Freigabe einholen. Installation bleibt separat offen,
weil die originale CLI bei install die nicht funktionierende Profilprüfung und
Signierung erneut ausführt. Keine Schlüsselbundrechte erweitert.

**Dokumentation/Rücknahme:** SIGNING-STATUS.md angelegt, START-HIER.md um den
aktuellen Stand ergänzt. Private Zertifikate unverändert aufbewahrt; nur Rechte
enger gesetzt. Diagnosespuren privat ignoriert. Keine Zertifikate neu erzeugt,
kein erneuter Login, keine TV-Änderung, keine Deinstallation oder Root-Ausführung.

## 2026-11-17 — Vetro-Alternative erfolgreich signiert und geprüft

**Freigabe:** Nach Erklärung des zusätzlichen projektinternen Bibliothekswegs
sagt der Besitzer ausdrücklich, mit Vetro fortzufahren. Das deckt Bereitstellung
der festgelegten Signierungsbibliotheken und lokale Signierung, keine TV-Installation.

**Quellprüfung/Bereitstellung:** Repo-Anweisungen, Upstream-Build und vorhandenes
Lockfile erneut gelesen. tizen.js index.js und packageSigner.js am festen Commit
45b00106149d0c8eff74ead4a979c909dd80efd6 gelesen. Git-Baum dieses Commits über den
Connector festgehalten: 15 reguläre Dateien, nicht abgeschnitten. Kontrollierter
Helfer install_locked_signer.py bereitgestellt und ausgeführt:
41 Lockfile-Pakete nur projektintern installiert. npm-Archive mit Integritätshashes,
tizen.js-Archiv über HTTPS mit vollständigem Dateisatz/Git-Blob-Hashabgleich.
Keine npm-/Lifecycle-Skripte und keine heruntergeladenen CLI-Dateien ausgeführt.
Keine globale Installation oder SSH-Zugriffe. Cache/Receipt unter
tools/downloads/signing-deps, Ziel rooting/on-boot-probe/node_modules.
Erster rg-Leseversuch im bereits verschobenen Stagingpfad fehlgeschlagen;
danach korrekte installierte Quellpfade gelesen. Zertifikatserzeuger werden nicht
aufgerufen, nur die benötigte Signierung.

**Signierung:** sign_package.py liest bestehende private Author-/Distributor-P12
und lokale Passwortdatei, übergibt Geheimnisse nur in der Umgebung des kurzlebigen
Node-Prozesses. Unverändertes rooting/build.cjs verwendet. Ausgabe explizit ins
ignorierte dist-Verzeichnis, Dateimodus 0600, keine Überschreibung einer vorhandenen
signierten Ausgabe. Kein neuer Login und keine Zertifikatsänderung.
Build-Quellcommit 11f752b50437fb10c4421d73474e0f5813a5aa8e.
Ergebnis vetro-integration-SIGNED.wgt, 459007 Bytes,
SHA-256 f4229886fd551c599689c5671242dd00fe2267d224a193a198801cb32a2ceedb.

**Prüfung/Korrektur:** Separater Prüfer verify_signed.cjs liest ZIP und Nutzdaten
erneut, prüft CRC, Dateisatz/Bytes gegen den Upstream-Kollektor, eingebettete
Zertifikate gegen die ausgestellten öffentlichen Dateien und RSA-SHA512.
Erste Prüferfassung verwendete für #prop irrtümlich Exclusive C14N und meldete
Digest mismatch. Der deklarierte C14N-1.1-Transform wurde geprüft; mit vorhandenem
xmllint unabhängig kanonisiert und Prüfer korrigiert. Das Paket blieb unverändert.
xmllint --help meldete unbekannte Option mit eingeblendeter Optionsliste;
der tatsächliche --c14n11-Aufruf war erfolgreich. xmllint beim Prüfen mit
--nocatalogs/--nonet und passenden C14N-Modi, kein DTD-/Netzwerkzugriff.

**Validierung:** Paket 81 Dateien. Author-Signatur 80 Referenzen,
Distributor-Signatur 81 Referenzen: RSA und sämtliche Dateihashes einschließlich
Properties bestätigt. Zertifikatsdaten aktuell gültig. Fünf synthetische
Archivtests bestanden (normal, Traversal, absoluter Pfad, Symlink, Gerätedatei).
Zwei Manipulationsfälle bestanden: Payload-Änderung und Signaturänderung jeweils
verworfen. Synthetische Testdateien danach entfernt, Originalpaket unangetastet.
Positiven Prüflauf nach Export der Testfunktion erneut bestanden.
Öffentliche, nicht-identifizierende Ergebnisse in SIGNED-BUILD.json.
Keine unabhängige vollständige Truststore-Kettenprüfung, keine Hardwareakzeptanz.

**Dokumentation/Rücknahme:** SIGNING-WITH-VETRO.md mit exakten Aufrufen,
Quellen, Fehlern, Ergebnissen und Grenzen; START-HIER.md und SIGNING-STATUS.md
aktualisiert. Original-Bibliothekslizenzen in node_modules erhalten, insbesondere
GPL von tizen.js; keine Binär-/Zertifikatsdateien veröffentlicht.
Die neuen projektlokalen Abhängigkeiten, Cache und signierte Ausgabe lassen sich
gezielt entfernen; keine solche Rücknahme durchgeführt. Private Zertifikate bleiben
erhalten. Keine persönlichen Schlüsselbundrechte angefordert oder erweitert.
In dieser Phase kein TV-Kontakt, keine TV-Änderung, kein Root.
Nächste Aufgabe vor Installationsfreigabe: einen Installationsweg vorbereiten,
der nicht erneut an Apps2Samsungs lokaler Zertifikatsprüfung scheitert.

## 2026-11-17 — Direkte Installation vorbereitet, nur lesend am laufenden TV geprüft

**Freigabe/Unterbrechung:** Besitzer bittet um Fortsetzung und weist darauf hin,
dass am TV gerade etwas läuft. Zusage: bis zu seiner gesonderten Bestätigung nur
lesen/lokal vorbereiten, kein Upload, Installation, Neustart oder Root.

**Quell-/Werkzeugprüfung:** Mitgelieferten Python-SDB-Wrapper und Vetro-SDB/ADB-
Transport gelesen. Python-Wrapper benötigt externes SDB und enthält separate
Shell-Injektionsfunktionen; nicht ausgeführt. Aktuelle Apps2Samsung-Quellen
v3.3.0 weiterhin mit Profil-/Signierungsablauf, kein geeigneter Skip-Sign-Weg.
Offizielle Samsung-CLI-Dokumentation gelesen. Suche nach TizenSdb führte zunächst
nicht zu brauchbarer Primärquelle; Drittanbieter-Suchergebnisse nicht als
Installationsgrundlage verwendet. NuGet-Webseite nicht abrufbar; offizielle
NuGet-Nuspec per curl gelesen: TizenSdb.Core 1.1.8, Originalrepository
PatrickSt1991/tizen-sdb, Commit 95f6492c3413f0c98e0e6696b369e3382d280e81.
Dort TizenInstaller.cs, SdbTcpDevice.cs und CLI-Program.cs gelesen.
Release-Metadaten gelesen, aber kein zusätzliches Binary heruntergeladen.
Standalone-CLI sieht standardmäßig ~/.sdb/adbkey vor; diese Zusatzrechte nicht
angefordert. Stattdessen vorhandenen Vetro-Transport verwenden.

**Hardware-Leseprüfungen:** Vetro-SDB verbindet direkt; capability: antwortet,
sdk_toolpath=/home/owner/share/tmp/sdk_tools und platform_version=6.0.
read_tv_baseline.cjs angelegt und nur lesend ausgeführt: App-Liste 103183 Bytes,
nichtleer, kein vetrotvapp erwähnt. Rohdaten ausschließlich in privatem
tv-baselines-Unterordner (Ordner 0700/Dateien 0600), keine Gerätedaten veröffentlicht.
RECV für device-profile.xml liefert SDB_SYNC_FAIL / No such file or directory.
Erste Baseline klassifizierte jeden Fehler konservativ als unbekannt; nach
Ergänzung der exakt abgegrenzten File-not-found-Klassifikation erneut gelesen:
Datei ausdrücklich abwesend. Permission-/Timeoutfehler bleiben unbekannt.

**Implementierung/Offline-Tests:** sdb-sync.cjs mit begrenzten SYNC-Frames nach
gelesehener Originalengine vorbereitet; RECV hardwaregelesen, SEND/DATA/DONE nur
mit Mocks geprüft. Verzeichnispfad/Größe begrenzt. deploy_signed.cjs default --plan
lokal ausgeführt: zeigt konkrete zwei Stagingdateien und vd_appinstall für
vetrotvapp.app, ohne TV-Verbindung. Schreibpfad nur hinter --confirm-install,
nicht ausgeführt. Vor Schreiben werden Paket, Geräteidentität, App-Liste,
Stagingpfad und ausdrückliche Datei-Abwesenheit geprüft; vorhandene/unklare
Dateien stoppen den Vorgang. Uploads würden zurückgelesen und geprüft, danach
ein Installationsversuch; kein Startbefehl, keine Developer-IP-Änderung,
keine Wiederholung/Entfernung bei Fehler. Private Journaldateien vorgesehen.

Prüfungen mit Mocks: Fragmentierung, DATA/DONE, fehlende/verweigerte Datei,
Größen-/Pfadlimit; SEND/DATA/DATA/DONE für 70000 Bytes; Erfolg und Ablehnung;
bestehende Null-Byte-Datei wird geschützt. Gerätezuordnung mit Fake-IDs für
Übereinstimmung, Längenpräfix und abweichendes Ziel getestet.
Anschließend echte reine getduid-Leseabfrage gegen SAN des ausgestellten
Distributor-Zertifikats verglichen: passend, keine Kennung ausgegeben.
Mocks/Identitätsprüfungen bestanden; kein Hardware-Schreibtest.

**Prüferkorrektur:** Positiver Paketprüflauf scheiterte zunächst nach
Dokumentationscommit an generierter service/build-info.js (HEAD-Revision).
verify_signed.cjs korrigiert: Produktquellen gegen im Buildbeleg festgehaltenen
Commit abgleichen, generierte Metadaten auf genau diese Revision und clean-Flag
prüfen; übrige Nutzdaten weiterhin bytegenau prüfen. Kein Paket neu gebaut oder
geändert. Danach positive RSA/Hash-Prüfung und beide Manipulationstests bestanden.
git diff --check ohne Fehler.

**Plan/Risiken/Rücknahme:** INSTALL-NEXT.md und einfache Anleitung aktualisiert.
Integration enthält On-Boot/Auto-Restart-Service und Root-Komponenten; eine
Installation kann Hintergrundcode starten, auch ohne expliziten App-Start.
Vor Schreibzugriff muss der Besitzer TV-Verfügbarkeit und Installation freigeben.
Vorgesehener Rückweg: nur Vetro deinstallieren und eigene neue Stagingdateien
gezielt entfernen; noch nicht hardwaregetestet. Kein pauschales 0 rmfile, das
fremde Dateien löschen könnte. Keine automatische Bereinigung. Vollständige
Root-Rücknahme weiterhin unbewiesen. Bisher keine Rücknahme nötig: nur private
Baselines und Projektcode/Dokumentation angelegt; kein TV-Upload/Installation.

## 2026-11-17 — Freigegebene Installation erfolgreich, Root noch nicht verbunden

**Freigabe:** Besitzer bestätigt ausdrücklich TV-Verfügbarkeit und Installation
nach Nennung der zwei übertragenen Dateien, möglicher Wiedergabeunterbrechung,
Hintergrunddienst und Root-Komponenten. Kein zusätzlicher Start/Neustart freigegeben.

**Durchführung:** Repo-Anweisungen gelesen. Mit bestehender Node-/OpenSSL-/Git-
Umgebung deploy_signed.cjs --confirm-install TV_IP einmalig ausgeführt.
Paket erneut erfolgreich geprüft (81 Dateien, RSA/Digests für 80/81 Referenzen),
Gerätekennung gegen ausgestelltes Distributor-Zertifikat abgeglichen,
Stagingpfad/App-Liste und Datei-Abwesenheit nochmals geprüft.
Profil und signiertes WGT über SYNC geschrieben und beide zurückgelesen;
Hashes stimmen jeweils. Keine vorhandene Stagingdatei überschrieben.
Danach genau ein vd_appinstall für vetrotvapp.app und das vorbereitete Paket.
Keine automatische Wiederholung, Deinstallation, Root-Shell-Injektion,
App-Launch-Anforderung, Developer-IP-Änderung oder Neustart.

**Ergebnis/Beleg:** Helfer Exitcode 0, installed=true, explicitlyLaunched=false,
rollbackVerified=false. Privates Journal enthält checked-before-write,
für beide Dateien upload-submitting/upload-readback-verified,
install-submitting und installation-confirmed. TV-Antwort enthält install completed,
keinen erkannten Installationsfehler; anschließende App-Liste enthält vetrotvapp.
Private Vorher-/Nachherlisten und Rohantwort bleiben im privaten Projektordner.
Öffentlich nur nicht-identifizierender DEPLOYMENT-RESULT.json, keine Profil-
oder Zertifikatsbytes/Hashes und keine realen Adressen.

**Nachprüfung:** Ausschließlich lesendes HTTP-GET auf TV_IP:8099/status,
maximal 3 Sekunden Verbindung/5 Sekunden insgesamt über bestehenden Proxy.
API erreichbar, mode=tv-integration, agent.connected=false.
Der Hintergrunddienst ist also bereits aktiv, obwohl kein App-Start angefordert
wurde. Keine Behauptung, dass überhaupt kein Hintergrundcode lief.
Root-Verbindung zum Zeitpunkt der Prüfung nicht bestätigt; Launcher nicht aktiviert.

**Dokumentation/Nächster Schritt:** START-HIER, Installationsplan und
Signierungsdokumentation mit klar getrenntem Nachtrag aktualisiert.
Erster sichtbarer App-Start und nachgelagerter Root-Test benötigen weiteren
abgestimmten Schritt; Mac-/Developer-Host-IP bleibt unverändert.

**Rücknahme/Risiken:** Vetro und zwei neue Stagingdateien wurden tatsächlich
installiert/angelegt. Rücknahme nicht ausgeführt oder auf Hardware verifiziert.
Kein pauschales Entfernen von Stagingdateien und kein Full-Root-Restore behauptet.
Exakte ursprüngliche Abwesenheit/Listen und private Journale liegen lokal vor.
Keine globalen Codex-/macOS-Berechtigungen geändert.

## 2026-11-17 — Erster App-Start nach ausdrücklicher Freigabe

**Freigabe:** Auf konkrete Frage nach sichtbarem Öffnen und Verlassen der
Wiedergabeansicht bestätigt der Besitzer "Ja, lets go". Keine zusätzliche
Freigabe für Launcher-Umschaltung, Developer-Host-IP oder Neustart abgeleitet.

**Durchführung:** Repo-Anweisungen gelesen. Über vorhandenen Vetro-SDB-Client
einmalig shell:0 was_execute vetrotvapp.app mit 5 Sekunden Verbindungs- und
15 Sekunden Befehlslimit ausgeführt. Prozesslokale OpenSSL-/Temporärpfade im
Projekt, keine globalen Konfigurationsänderungen.

**Beobachtung:** TV antwortet launch start und app_id[vetrotvapp.app] launched,
Befehlslauf erfolgreich. Dies ist die Gerätebestätigung, noch keine vom Agenten
beobachtete Bildschirmansicht. Besitzer wird um Abgleich der sichtbaren Ansicht
gebeten. Danach lesendes GET auf TV_IP:8099/status mit 3/5 Sekunden Limits:
erreichbar, mode=tv-integration, App-Version 0.3.5, agent.connected=false.
Keine Fehlerbehebung durch blindes erneutes Starten, kein zusätzlicher Root-Befehl.

**Stand/Rücknahme:** Launcher nicht durch Agenten aktiviert, kein Neustart oder
Developer-Host-Wechsel. First-Launch-Beleg ohne private Gerätewerte gespeichert,
einfache Anleitung aktualisiert. Der Vordergrund wurde bewusst auf die
freigegebene App umgeschaltet; kein Schließ-/Umschaltbefehl ausgeführt.
Hintergrundaktivität der installierten Integration ist von unseren expliziten
Befehlen zu unterscheiden. Root-Verbindung zum Prüfzeitpunkt nicht bestätigt,
vollständige Rücknahme weiterhin nicht hardwarevalidiert.
