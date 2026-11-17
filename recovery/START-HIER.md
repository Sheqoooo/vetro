# Hier anfangen

**Update 17. November 2026: Vetro ist installiert und der Root-Agent verbunden.**
Nach deinem Host-IP-Wechsel auf TV-Loopback und dem gemeldeten Neustart antwortet
der Agent mit **UID 0/GID 0**. [Root-Prüfung](ROOT-RESULT.json).
Der Launcher wurde inzwischen freigegeben kurz ein- und wieder ausgeschaltet.
Er ist jetzt **aus**, sein Prozess gestoppt und die Samsung-Startoption beim
ursprünglichen Wert 0. [An-/Aus-Test und Grenzen](LAUNCHER-ON-OFF.md).
Home-Taste, Standby und Neustart mit aktivem Launcher sind noch nicht geprüft.

Beide Übertragungen wurden zurückgelesen und geprüft; der TV bestätigt die
Installation und listet Vetro. Der Hintergrunddienst antwortet im Modus
`tv-integration`.
Nach weiterer Freigabe hat der TV auch den ausdrücklichen Start der Vetro-App
bestätigt. Was auf dem Bildschirm sichtbar ist, muss der Besitzer noch bestätigen.
Kein Neustart oder Launcher-Wechsel durch den Agenten.
Installationsbeleg: [Ergebnis](DEPLOYMENT-RESULT.json).
Erster Start: [Beleg und verbleibende Sichtprüfung](FIRST-LAUNCH.json).
Aktueller Stand: [Signierung mit Vetro](SIGNING-WITH-VETRO.md).
Hintergrund des ursprünglichen Fehlers: [Zertifikatsstatus](SIGNING-STATUS.md).

**Verwendeter Installationsweg:** [Ablauf und Grenzen](INSTALL-NEXT.md).
Die sichtbare Vetro-Ansicht wurde vom Besitzer bestätigt. Der Besitzer hat den
Developer-Host auf TV-Loopback geändert und neu gestartet; dazu wurde kein
zusätzlicher Mac-Zugriff freigegeben. Für spätere Installationen muss der Host
wieder auf die dann aktuelle Mac-IP umgestellt werden.
Eine private Post-Root-Baseline liegt vor, der kontrollierte An-/Aus-Test ist
abgeschlossen. Nächster Schritt wäre, den Launcher nach Freigabe eingeschaltet
zu lassen und Home-Taste/Navigation sichtbar mit dem Besitzer zu prüfen.

Die folgende Übersicht beschreibt die Offline-Vorbereitung vom 16. November.

Der Mac ist für den nächsten Versuch vorbereitet. Den Fernseher habe ich heute
nicht angesprochen, weil du in einem anderen Netzwerk bist.

## Was erledigt ist

- **Apps2Samsung ist heruntergeladen und startet.** Das ist die normale,
  unveränderte Version 3.1.0 für deinen Mac. Kein zusätzlicher Fork nötig.
- **Die heruntergeladene Datei ist geprüft.** Ihre Prüfsumme stimmt mit der
  veröffentlichten Prüfsumme überein.
- **Dein kompletter Vetro-Fork ist lokal vorhanden.** Er liegt im Ordner `vetro`.
- **Zwei Vetro-Pakete sind gebaut.** Das Paket mit TV-Integration ist für unser
  späteres Vorhaben vorgesehen. Beide sind noch **unsigniert**: Es fehlt die
  persönliche Installationsfreigabe in Form eines Samsung-Zertifikats.
- **Fünf Offline-Prüfungen sind bestanden.** Das ersetzt keinen Test am Fernseher.
- Keine App am TV installiert, kein Root ausgeführt und keine globalen
  Mac-Einstellungen oder Zugriffsbeschränkungen verändert.

## Wo liegt was?

Alles befindet sich unter deinem vorhandenen Ordner **TVBuild**:

| Ordner/Datei | Einfach erklärt |
| --- | --- |
| `tools/apps2samsung/apps2samsung-cli` | Das originale Installationsprogramm |
| `tools/downloads/` | Die heruntergeladene Originaldatei |
| `vetro/` | Dein vollständiges Vetro-Projekt |
| `vetro/dist/vetro-integration-UNSIGNED.wgt` | Vorbereitetes Paket mit TV-Integration; noch nicht installieren |
| `vetro/dist/vetro-app-only-UNSIGNED.wgt` | Vergleichspaket ohne Root-/TV-Integration |
| `recovery/private/` | Lokale Arbeitsdaten; später auch sensible Zertifikate. Nicht auf GitHub hochladen |
| `vetro/recovery/OFFLINE-PREPARATION.md` | Technische Einzelheiten und genaue Prüfergebnisse |

## Wenn du wieder zu Hause bist

1. Mac wieder mit deinem Heimnetz verbinden und den Fernseher einschalten.
2. Hier schreiben: **„Bin wieder zu Hause, TV ist an.“**
3. Wir prüfen zunächst die aktuelle TV-IP und den Entwicklermodus.
4. Dann testen wir die normale Apps2Samsung-Verbindung ausschließlich zu deinem
   TV. Ob sie mit der eingeschränkten Netzwerkfreigabe klappt, ist noch offen.
5. Falls Samsung eine Anmeldung für das Zertifikat verlangt, meldest **du dich
   selbst** an. Passwort und Zertifikate nicht in den Chat kopieren.
6. Erst mit deiner gesonderten Freigabe installieren wir unser eigenes Paket.
   Danach prüfen wir Launcher an/aus und den Rückweg, dann Home-Taste und Neustart.

Wenn eine Berechtigung fehlt, halten wir bei diesem konkreten Schritt an.
Wir geben nicht vorsorglich den ganzen Rechner oder das Heimnetz frei.

## Kann man alles zurücknehmen?

**Heute wurde am TV nichts verändert.** Die heutige Mac-Vorbereitung besteht aus
Dateien im Projektordner. Die neuen Werkzeug- und Builddateien können dort später
gezielt entfernt werden. Vor dem Löschen echter Zertifikate oder Sicherungen
halten wir Rücksprache.

**Für den Fernseher gilt weiterhin:** Launcher ausschalten und Root vollständig
entfernen sind verschiedene Dinge. Eine vollständige Root-Rücknahme ist noch
nicht geprüft. Das darf kein angebliches Backup-Skript versprechen.
