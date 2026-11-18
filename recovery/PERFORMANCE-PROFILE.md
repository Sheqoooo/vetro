**Weitere Bestätigung vom 18. November 2026:** AirPlay funktioniert laut Besitzer.
Bildschirmspiegelung und Einstellungen bleiben gesondert ungeprüft.

**Bestätigung vom 18. November 2026:** Der Besitzer bestätigt auf die Frage
nach Home, normalem Fernsehen und Samsung TV Plus: funktioniert weiterhin.
AirPlay, Bildschirmspiegelung und Einstellungen wurden damit nicht gesondert
bestätigt. Keine weitere Änderung am TV vorgenommen.

**Boot-Ergebnis:** Neuer Kernelboot bestätigt, passive Messung vollständig.
Erste native Anfrage 12,567 s, Erfolg/Exit 0 bei 14,630 s. Vetro-Dienstprozess
12,592 s; erster HTTP-Sichtpunkt 18,27 s; Launcherprozess 44,732 s, laufend.
Vorheriges 30-s-Profil: Launcher 49,464 s. Zusätzlicher Gewinn nur etwa 4,7 s;
kein Beleg für eine fertige UI bei 12 s. Zwischen Modulinitialisierung und
Root-Agent lagen 19,53 s. Da Timing und optionale Komponenten gemeinsam
verändert wurden, ist der isolierte Debloat-Beitrag nicht bestimmt.

Alle 15 Disable-Flags bleiben nach Boot gesetzt; keiner der Zieleinträge in der
laufenden App-Liste. MultiScreen-Unit inactive/dead mit ConditionResult=no;
auch nicht in laufender App-Liste. Zu erhaltende Komponenten bleiben enabled.
Das sind Prozess-/Registrierungsprüfungen, noch kein praktischer Test von TV Plus,
AirPlay, Spiegelung oder Einstellungen. Home-Sichttest nach diesem Boot offen.
Timer nächste Auslösung infinity, keine weiteren Anfragen geplant.
[Messbeleg](PERFORMANCE-RESULT.json). Konfiguration bleibt eingerichtet.

Die nachfolgenden Abschnitte dokumentieren den vorherigen Einrichtungsstand.

# Schnellstart und begrenzte Samsung-Reduktion

Stand 17. November 2026: **eingerichtet und zurückgelesen, noch kein Neustarttest.**
Vorherige bestätigte Messung: Vetro-Dienst 30,86 s, Leiste 49,464 s.
Neue 12 Sekunden sind die erste **Startanfrage**, keine garantierte fertige Leiste.
[Anonymisierter Einrichtungsbeleg](PERFORMANCE-RESULT.json).

## Gewünschte Funktionen

Besitzer möchte normales Fernsehen, Samsung TV Plus, AirPlay und
Bildschirmspiegelung behalten. Streaming, HDMI, Bild/Ton, Fernbedienung und
Einstellungen bleiben im Erhaltungsumfang. Sprachassistenten und Multi View
wurden nicht als zu erhalten genannt.

Nach der allgemeinen Freigabe zur weiteren Beschleunigung und Samsung-Reduktion
gezielte Änderungen durchgeführt. Keine zusätzlichen Mac-Rechte angefordert.

## Was genau geändert wurde

1. Bestehende eigene Benutzer-Startdateien auf festen Hash geprüft. Nur diese
   beiden Dateien aktualisiert: erster Timertermin 12 s, bisherige 30/50/70 s
   bleiben als Rückfälle. StartLimitBurst von drei auf vier erhöht. Jeder Aufruf
   maximal acht Sekunden; nach einem Erfolg keine weiteren Anfragen.
   Keine Hersteller-Startdienste verändert, kein Reload oder Live-Appstart.
2. 15 tatsächlich installierte Komponenten einzeln über Vetros geprüften
   /debloat-Endpunkt per pkgcmd --global deaktiviert. Fünf zuvor im Vetro-Code
   als getestet aufgeführte ACR-/Bildinhalts-Erkennungskomponenten sowie zehn
   eigenständige Alexa-/Bixby-/Google-Komponenten. Die exakte Liste steht im
   Ergebnisbeleg. Alexa Jump Starter war nicht installiert und wurde übersprungen.
   Alle ursprünglichen disabled/onboot/autorestart-Werte vorher privat gesichert;
   jede Änderungsabsicht vor dem Netzaufruf journalisiert.
3. Leere disable_preloading-Datei im bestehenden MultiScreen-Datenordner erstellt,
   Besitzer numerisch 5001, Gruppe system_share, Mode 0664. Die auf genau diesem
   Gerät gelesene Hersteller-Unit enthält die entsprechende ConditionPathExists.
   Nur automatisches Vorladen unterdrückt; keine App deinstalliert oder jetzt
   gestoppt. On-demand-Verhalten zusammen mit AirPlay/Mirroring noch zu testen.

## Was bewusst erhalten bleibt

Samsung Home als Rückfall und als Zugang zu Teilen von Einstellungen/Quellen;
Vetro hält seinen sichtbaren Auftritt bereits klein. Auch der von Home geladene
CoBA-Adagent bleibt. Keine pauschale Abschaltung nach Namensmuster.

TV-Viewer, Kanäle, TV-Plus-/Werbe-Wiedergabekomponenten, AirPlay, ScreenMirroring,
gemeinsame Voice-/TTS-Bibliotheken, Webruntime, Ton/Bild/Input und Netzwerkdienste
werden nicht abgeschaltet. Voice-App/Voice-Client haben Querreferenzen aus
TV-Plus-/Menü-/Wiedergabekomponenten; deshalb nicht die breite voice-all-Gruppe.

Ambient bleibt erhalten: Hersteller-Startskript und Screen-Daemon können es
erneut starten; blindes Disable kann eine Wiederholungsschleife auslösen.
HbbTV bleibt in dieser ersten Stufe erhalten, ebenso SmartThings und
Samsung-Konto-/Anmeldedienste mit unklaren Querabhängigkeiten. Firmware-
Auto-Update-Einstellung bleibt beim gelesenen ursprünglichen Wert 1.

## Prüfung und tatsächliche Grenzen

Nachher gesamte App-Inventarliste erneut gelesen und gegen vorher verglichen:
genau 15 disabled-Flags geändert, andere beobachtete Flags unverändert;
sämtliche onboot-/autorestart-Felder unverändert. Erhaltungs-Komponenten noch
enabled. Beide neuen Timer-/Service-Hashes stimmen mit lokalen Vorlagen,
Preload-Datei regulär, leer, Mode 0664. Launcher läuft weiterhin.

Das ist eine Zustandsprüfung, kein Beweis für TV-Plus-DRM oder AirPlay-Funktion.
Niemand hat in diesem Schritt Programme gestoppt, Pakete entfernt, Senderlisten
oder Zugangsdaten verändert. Kein neuer Kernelboot und noch keine RAM-/
Startzeitverbesserung für dieses Profil gemessen. Unbekannte, nicht deklarierte
Firmware-Abhängigkeiten sind möglich.

Die offizielle Tizen-Dokumentation beschreibt Paketverwaltung als Kernfunktion;
sie garantiert diese internen Root-Eingriffe auf Consumer-Firmware nicht.
Die konkreten Disable-Aufrufe basieren auf dem vorhandenen Vetro-Code und den
auf dem Gerät zurückgelesenen Zuständen. Kein offizieller Samsung-Debloat-Support
behauptet. Echte Read-only-Sicherheitsgrenzen auf dem Mac bleiben unverändert.

## Bedienung und Rücknahme

Aus dem Repository, TV_IP bezeichnet nur das freigegebene Gerät:

    python3 -B recovery/performance_trial.py plan
    # Bereits im freigegebenen Umfang ausgeführt; NICHT blind wiederholen:
    python3 -B recovery/performance_trial.py apply --tv TV_IP --owner-approved
    # Zurück zum bestätigten 30-Sekunden-Profil:
    python3 -B recovery/performance_trial.py restore --tv TV_IP --owner-approved --journal PRIVATE_JOURNAL

Der tatsächliche Journalpfad ist nur lokal unter recovery/private/startup-analysis
gespeichert; nicht veröffentlichen. Originale per-Komponente-Werte bleiben dort.
Restore verifiziert die neuen Timer-Dateien gegen statische Hashes und ersetzt
sie durch die exakten 30-Sekunden-Vorlagen. Es entfernt ausschließlich die eigene
leere reguläre Preload-Datei und stellt die vorherigen effektiven App-Flags
über dieselbe API wieder her. Vorher schon deaktivierte Apps bleiben deaktiviert.

**Reihenfolge:** Erst dieses Profil zurücknehmen. Danach, falls gewünscht, den
ursprünglichen nativen Frühstart über native_start_trial.py remove entfernen.
Dessen alte Hashes passen absichtlich nicht zur 12-Sekunden-Variante.
Datei-Rücknahmen werden beim nächsten Boot vollständig wirksam; kein automatischer
Reboot. App-Prozesse werden beim Wiederaktivieren nicht zwangsläufig gestartet.

Rücknahme stellt effektive Flags wieder her, nicht bytegenaue Datenbanktabellen,
Prozesszustände, Cachedateien oder zeitliche Nebenwirkungen. Sie benötigt den
erreichbaren Vetro-Agenten. Bei Timeout oder Teilfehler stoppen und Journal prüfen:
ein halber Dateiaustausch/angelegtes temporäres File kann manuelle gezielte
Reparatur erfordern. Keine blinde Wiederholung, keine automatische Garantie.
Vier Mocktests bestanden: ursprüngliches Disable erhalten, verlorene Antwort
nach Änderung rücknehmbar, unbekannter Originalzustand verhindert Schreiben,
gefälschte fremde Rücknahme-ID verweigert. Timing-Shellsyntax für beide Richtungen
geprüft; echter Timing-Datei-Rundlauf/Hardware-Rücknahme noch ungeprüft.

## Nächster Test

Passive Messung vor Neustart starten; Besitzer startet mit der Fernbedienung neu.
Neue Boot-ID, erste native Anfrage, Erfolg/Fehler, Dienst- und Leisten-PID-Zeiten
prüfen. Da Starttermin und optionale Preloads gemeinsam verändert wurden, kann
dieser Vergleich den Gesamteffekt, aber keine isolierte Ursache beweisen.
Danach Besitzer: Home, Einstellungen, normaler Sender, TV Plus, AirPlay und
Spiegelung testen. Bei Problem Profil gezielt zurücknehmen, nicht weiter entfernen.

Quellen:
- [Samsung: Autorun Smart Hub abschalten](https://www.samsung.com/sg/support/tv-audio-video/how-to-activate-or-deactivate-the-smart-hub/).
- [Samsung/Tizen: Paketverwaltung](https://github.com/Samsung/tizen-docs/blob/master/docs/application/native/guides/app-management/package-manager.md).
- [systemd v244: Timer](https://github.com/systemd/systemd/blob/v244/man/systemd.timer.xml).
- Repo: app/service/debloat.js, quick-settings.js, quick-wins.js, app-facts.js.
  Diese Vetro-Klassifikationen sind Hinweise, keine Sicherheits- oder
  Kompatibilitätsgarantie für jede Firmware.
