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
