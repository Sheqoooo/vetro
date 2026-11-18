**Aktueller Auftrag: rücknehmbaren TV-Plus-Geschwindigkeitsvergleich durchführen.**
Besitzer stimmt zu. Zwei Neustarts mit und zwei ohne geplant; erste frische
Vergleichsmessung mit TV Plus vorbereitet. Noch keine TV-Plus-Flagänderung.
Fern-Neustartversuch ohne neue Boot-ID abgebrochen; aktueller Ablauf nutzt
ausschließlich die Fernbedienung des Besitzers.
[Messprotokoll und Rücknahme](TVPLUS-COMPARISON.md).

**Aktueller Abschluss dieser Datenschutzstufe:** Beide optionalen Zustimmungen
(Interessenwerbung und Anzeigeinformationsdienste) nun lesend als aus bestätigt,
auch aus dem tatsächlich laufenden Consent-Dienst heraus. 25 optionale
Komponenten aus beiden Profilen deaktiviert, sieben Analyse-/Loghosts gefiltert;
Komponenten/Filter haben den vom Besitzer gemeldeten Neustart überstanden.
TV Plus bleibt ausdrücklich erhalten, Werbung im Stream kann bleiben.
AirPlay nach der neuesten Stufe noch praktisch prüfen.
[Umfang und Rücknahme](PRIVACY-PROFILE.md), [Beleg](PRIVACY-RESULT.json).

Die folgenden älteren Statusblöcke dokumentieren die zeitliche Entwicklung.

**Nach Besitzer-Neustart geprüft:** Alle 25 optionalen Komponenten aus beiden
Profilen weiter deaktiviert und nicht als laufende Apps gelistet. Filter mit
sieben Hostnamen wieder aktiv. TV Plus bleibt auf ausdrücklichen Wunsch erhalten.
Samsung-Einstellungen über Vetro-Zahnrad vom Besitzer bestätigt.
Eine separate Anzeigeinformations-Zustimmung ist noch aktiv; regulärer UI-Opt-out
läuft. Keine vollständige Trackingfreiheit behauptet.

**18. November: weitere Werbe-/Tracking-Reduktion eingerichtet.**
Zehn weitere eigenständige Komponenten deaktiviert, sieben exakte Analyse-/Log-
Hosts lokal am TV gefiltert. TV Plus soll ausdrücklich erhalten bleiben und
funktioniert laut Besitzer weiterhin. Antennen-/Kabelempfang ist nicht angeschlossen;
frühere allgemeine Fernseh-Bestätigung bezog sich auf TV Plus.
Interessenwerbung gespeichert aus; separate Anzeigeinformations-Zustimmung
noch aktiv und regulärer UI-Opt-out offen. Kein Null-Tracking-Nachweis.
[Umfang, Grenzen und Rücknahme](PRIVACY-PROFILE.md), [Beleg](PRIVACY-RESULT.json).

Die folgenden älteren Abschnitte sind Änderungsgeschichte.

**Besitzerpräferenz, 18. November 2026:** Bildschirmspiegelung ist nicht wichtig;
der entsprechende Funktionstest entfällt. Keine weitere Abschaltung daraus
abgeleitet. AirPlay bleibt bestätigt und soll erhalten bleiben.

**Weitere Bestätigung vom 18. November 2026:** AirPlay funktioniert laut Besitzer.
Bildschirmspiegelung und Einstellungen bleiben gesondert ungeprüft.

**Bestätigung vom 18. November 2026:** Der Besitzer bestätigt auf die Frage
nach Home, normalem Fernsehen und Samsung TV Plus: funktioniert weiterhin.
AirPlay, Bildschirmspiegelung und Einstellungen wurden damit nicht gesondert
bestätigt. Keine weitere Änderung am TV vorgenommen.

**Aktueller Neustart gemessen:** Vetro-Dienst 12,592 s, Leiste 44,732 s.
Gegenüber vorher 49,464 s etwa 4,7 s gewonnen. Alle 15 optionalen Komponenten
bleiben deaktiviert und fehlen in laufender App-Liste; Multi-View-Vorladen
unterdrückt. Gewünschte Komponenten enabled, praktischer Funktionstest und
Home-Sichttest nach diesem Boot noch offen.
[Messbeleg und Grenzen](PERFORMANCE-RESULT.json).

Die folgenden älteren Statusabschnitte bewahren die Änderungsgeschichte.

**Neuer Versuch eingerichtet, Messung ausstehend:** erste Vetro-Startchance
ab 12 s statt 30 s; 15 optionale Erkennungs-/Assistenten-Komponenten deaktiviert
und automatisches Multi-View-Vorladen unterdrückt. Gewünschte TV-/TV-Plus-/
AirPlay-/Spiegelungs-Komponenten weiterhin aktiviert, Funktionsprüfung ausstehend.
[Änderungen und Rücknahme](PERFORMANCE-PROFILE.md), [Beleg](PERFORMANCE-RESULT.json).
Die folgenden 49-Sekunden-Ergebnisse gelten für das vorherige 30-Sekunden-Profil.

**Aktueller Erfolg: Frühstart beim ersten Test-Neustart bestätigt.**
Vetro-Dienst nach 30,86 s statt etwa 103 s, Leistenprozess nach 49,464 s statt
etwa 107 s. Direkter Startauftrag erfolgreich; keine weitere Timer-Auslösung
geplant. Konfiguration bleibt eingerichtet. Besitzer bestätigt: Home zeigt nach diesem
Neustart die Vetro-Leiste. Wiederholungsboot steht aus; sofort Samsung-freier
Bildschirm nicht bewiesen.
[Messbeleg](NATIVE-START-RESULT.json), [Einrichtung und Rücknahme](NATIVE-START-TRIAL.md).

# Hier anfangen

**Update 17. November 2026: Vetro ist installiert und der Root-Agent verbunden.**
Nach deinem Host-IP-Wechsel auf TV-Loopback und dem gemeldeten Neustart antwortet
der Agent mit **UID 0/GID 0**. [Root-Prüfung](ROOT-RESULT.json).
Der freigegebene An-/Aus-Test wurde erfolgreich abgeschlossen; dabei blieb die
Samsung-Startoption beim ursprünglichen Wert 0.
[An-/Aus-Test und Grenzen](LAUNCHER-ON-OFF.md).
Nach weiterer Freigabe ist der Launcher jetzt **eingeschaltet und läuft**, um die
Home-Taste sichtbar zu testen. [Aktueller Teststand](HOME-TEST.json).
Der Besitzer hat vor dem Neustart die Vetro-Leiste auf Home bestätigt.
Nach dem Neustart erschien zunächst Samsung Home. Beim ersten Check antwortete
Vetro noch nicht; kurz darauf kamen Dienst, Root-Agent und Launcher ohne
manuellen Start wieder. Der Besitzer hat danach erneut Home gedrückt und die
Vetro-Leiste bestätigt. [Neustart-Beobachtung](REBOOT-OBSERVATION.json).
Ein sofort sauberer Start ohne Samsung-Zwischenanzeige ist nicht bestätigt.

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
abgeschlossen. Home funktioniert auch nach dem verzögerten Wiederanlauf.
Die Startverzögerung ist eingegrenzt: Im untersuchten Kernelboot startete Vetros
Dienst erst bei 104,11 Sekunden, Root bei 107,08 und der Launcher bei 108,22.
Ursache und Abhilfe sind noch nicht bewiesen. Die passive Wiederholungsmessung
ist abgeschlossen: Dienst 103,092 Sekunden,
Launcher 107,296 Sekunden nach bestätigtem neuem Kernelboot.
[Messwerte und Grenzen](STARTUP-ANALYSIS.md).
Der zusätzliche Benutzer-Start wurde eingerichtet und bei einem neuen Kernelboot
getestet: keine Beschleunigung (Dienst 104,12 s, Launcher 108,032 s).
Kein Helferprotokoll; Testdateien anschließend entfernt und Abwesenheit geprüft.
Vetro läuft wieder über den bisherigen Weg.
Neue Diagnose: Der alte Helfer startete schon nach acht Sekunden, scheiterte
aber mit Exit 1. Direkte native Startanfrage erfolgreich im laufenden TV geprüft.
[Nachfolgeversuch ohne Shellhelfer](NATIVE-START-TRIAL.md) ist jetzt eingerichtet
und zurückgelesen; frühe Bootwirkung noch nicht gemessen.
[Test und Rücknahme](EARLY-START-TRIAL.md), [Einrichtungsbeleg](EARLY-START-RESULT.json).
Keine Einstellungen zur Behebung auf Verdacht ändern.
Standby und echter Strom-Aus-/Ein-Test bleiben ungeprüft.

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
