# Hier anfangen

**Stand: 16. November 2026. Du musst gerade nichts machen.**

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
