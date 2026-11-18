# TV Plus: freigegebener Vergleich, noch kein Leistungsurteil

Stand 18. November 2026. Besitzer hat dem rücknehmbaren Deaktivierungsversuch
mit mehreren Neustarts ausdrücklich zugestimmt. Zwei frische Läufe mit TV Plus
(A1/A2), danach zwei ohne (B1/B2). Erste manuelle Messung vorbereitet.
**Noch keine TV-Plus-Komponente deaktiviert und kein Geschwindigkeitseffekt
dieses Versuchs gemessen.** Frühere ~45 s stammen aus einem älteren Profilstand.

## Exakter Umfang

Nur zwei aktuelle, einzeln verifizierte App-IDs:
- com.samsung.tv.tvplus
- com.samsung.tv.tvPlusDeeplinker

Beide bei Vorbereitung enabled, onboot=false, autorestart=false.
Frisches komplettes Flag-Inventar und Filterkonfiguration privat gesichert.
Keine Änderung an Ad-Webframework, CoBA-Adagent, TV-Viewer, AirPlay, Webruntime,
Starttimern, Einwilligungen oder vorherigen Datenschutz-/Performanceprofilen.
Keine App-Deinstallation, kein Löschen von Sendern/Konten oder globaler
Mac-/Router-Einstellung. Kein Zugriff auf andere Heimnetzgeräte.

## Messprotokoll

1. Pro Lauf frischen Telemetrie-/Service-Ausgangsstand speichern.
2. Nach WAIT_FOR_OWNER_REBOOT führt Besitzer mit Power einen echten Neustart
   aus. Neue Kernel-Boot-ID muss den Boot bestätigen; HTTP-Ausfall genügt nicht.
3. Dienst/Root beobachten; 20 s nach Root-Verbindung Prozessstartzeiten von
   Dienst und Dock aus proc/stat/CLK_TCK lesen, Launcher-PID muss laufen.
4. Nach jedem Lauf vollständige Registry-Flag-Kontrolle gegen Ausgangsstand:
   nur TV-Plus-disabled darf im B-Zustand abweichen. DNS-Liste identisch, Filter
   weiterhin angewandt. Bei anderem Zustand Versuch stoppen.
5. Nach jedem Lauf bis mindestens 100 s Uptime warten. Dann zweiter Lauf
   desselben Zustands, anschließend einzeln die zwei TV-Plus-disabled-Flags ändern.
6. Pro Zustand zwei Werte. Hauptmetrik: **Start des Leistenprozesses**, nicht
   visuell bestätigte Bedienbereitschaft oder Power-Taste-bis-Bild.

Keine Vetro-UI oder TV-Plus-Wiedergabe für die Messung manuell öffnen.
Aufeinanderfolgende Software-/Power-Neustarts sind keine AC-Kaltstarts.
Vier Läufe sind eine kleine Stichprobe; Netz-/CPU-/Cache-/Temperaturverlauf und
die feste A/A/B/B-Reihenfolge bleiben mögliche Einflussfaktoren. Keine
statistische Signifikanz oder allgemeine Performancegarantie behaupten.

Vorab festgelegte praktische Auswertung: mittlerer Zeitgewinn muss größer sein
als sowohl zwei Sekunden als auch die Spannweite jeder der beiden Zweiergruppen.
Das ist eine konservative praktische Regel, kein statistischer Test.
Ohne solchen Gewinn werden die ursprünglichen TV-Plus-Flags zurückgestellt.
Bei Fehler ebenfalls Rücknahme versuchen; wenn nicht erreichbar, unbestätigten
Zustand ausdrücklich protokollieren und keine blinden Wiederholungen.

## Ein fehlgeschlagener Fern-Neustart vor dem Vergleich

Eine erste Version hatte genau einen normalen systemctl-reboot-Aufruf an den TV
gesendet. Antwort unklar; laufender Beobachter sah innerhalb 180 s keine neue
Kernel-Boot-ID. Lauf deshalb ungültig/abgebrochen, keine Wiederholung des
Rebootbefehls und noch keine Flagänderung. Keine Aussage über die genaue
Ablehnungsursache. Kein erzwungener Reboot, Zusatzprivileg oder MAC-/Systemdienst-
Eingriff als Ausweichweg.

Ein Versuch, den eigenen lokalen Vergleichsprozess über pgrep zu finden,
scheiterte an nicht verfügbarer Prozessliste (sysmond). Keine Rechte erweitert.
Die erste Version endete über ihre bereits eingebaute feste Wartefrist.
Anschließend Code auf ausschließlich vom Besitzer ausgelöste Neustarts geändert,
neuer privater Lauf mit neuem Baselineverzeichnis gestartet. Unvollständigen
ersten Lauf nicht in Mittelwerte aufnehmen.

## Bedienung und Rücknahme

Aus dem Repository, TV_IP bezeichnet nur den freigegebenen TV:

    python3 -B recovery/tvplus_comparison.py plan
    python3 -B -u recovery/tvplus_comparison.py run --tv TV_IP --owner-approved
    # Originalwerte aus genau dem privaten Vergleichsjournal wiederherstellen:
    python3 -B recovery/tvplus_comparison.py restore --tv TV_IP --owner-approved --journal PRIVATE_COMPARISON_JSON

Kein automatischer Neustart im aktuellen Skript. Pro manuellem Boot maximal
900 s beobachten, keine blind wiederholten Bootanforderungen. Neue Laufordner
werden exklusiv privat angelegt, Rohdaten/Boot-IDs nicht veröffentlichen.
CANCEL-Datei im laufenden privaten Vergleichsordner beendet die nächste
Beobachtungsschleife; nach bereits erfolgter Flagänderung wird Rücknahme versucht.

Restore akzeptiert nur exakt die beiden festen TV-Plus-IDs und boolesche
Originalfelder; stellt ursprüngliche effektive disabled-Flags wieder her und
prüft auch ursprüngliches onboot/autorestart. Neue persönliche Daten oder
gemeinsame Systembibliotheken werden nicht angefasst. App-Prozess-/Datenbank-
Bytes und Cacheeffekte sind damit nicht zurückgesetzt. Benötigt weiter
erreichbaren Root-Agenten. Hardware-Rücknahme noch ungeprüft.

Sechs lokale Tests bestanden: kleine/noisige Gewinne nicht überschätzen,
großen konsistenten Gewinn erkennen, unvollständige Stichprobe verweigern,
fremde/schutzbedürftige IDs verweigern, gefälschtes Restore-Journal vor API
stoppen, ursprüngliche effektive TV-Plus-Flags wiederherstellen.
Das ist keine bereits absolvierte Hardwaremessung.

**Nachtrag zur manuellen Wartezeit:** Einen ersten noch wartenden manuellen
Lauf gezielt per CANCEL beendet, bevor ein Boot oder Flagänderung erfolgte.
Danach Beobachtungsfenster auf 900 s verlängert und neuen privaten Lauf
exklusiv angelegt. Aktueller Stand WAIT_FOR_OWNER_REBOOT A1.
Abbruchprüfung auch vor jedem Flagwechsel und während Beruhigungsphasen;
alle sechs Tests anschließend erneut bestanden.
