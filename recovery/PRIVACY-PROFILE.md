**Abschließender Zustandsnachweis:** Interessenwerbung und
Anzeigeinformationsdienste sind jetzt beide regulär abgewählt. Unmittelbar
aufeinanderfolgende nur lesende Abfragen im Root-Kontext und im Mount-Namensraum
des tatsächlich laufenden HomeDataControl-Dienstes liefern jeweils 0 für beide
Zustimmungen. Die vorherige aktive Anzeigeinformations-Zustimmung ist damit
aufgehoben. Keine Consent-Datenbank direkt verändert.

Die zeitlich getrennten älteren Messungen belegen keinen Namespacefehler.
Der Besitzer präzisierte, dass die Anzeigeinformations-Zustimmung zuvor doch
gegeben war. Keine fehlerhafte Diagnose oder Produktcodeänderung aus der bloßen
zeitlichen Differenz abgeleitet. Nach früherer Unsicherheit nun aktuellen
Speicherstand unabhängig rückgelesen. LAT-API/Null-Tracking bleiben unbestätigt.
AirPlay sollte nach dieser neuesten Stufe noch praktisch getestet werden.

**Nachtrag: gemeldeten Besitzer-Neustart geprüft.** Alle 25 optionalen Ziel-IDs
aus Leistungs- und Datenschutzprofil weiterhin disabled und nicht in der laufenden
App-Liste. Analysefilter automatisch wieder enabled/applied, sieben Namen.
Kein kontrollierter Capture vor diesem Neustart, keine neue Startzeitbehauptung.
TV-Plus-Wiedergabe wurde nach Apply vom Besitzer bestätigt.

Native HomeSetting-Starts und entfernte Menü-Tastendrücke zeigten laut Besitzer
keine sichtbare Seite. Nicht weiter blind wiederholt. Besitzer hat die Samsung-
Einstellungen erfolgreich selbst über Vetros Zahnrad geöffnet; damit ist dieser
Zugang bestätigt. Reguläre Abwahl der Anzeigeinformations-Zustimmung noch offen.
Keine Consent-Datenbank geschrieben.

# Werbe- und Tracking-Reduktion: Zustand und verbleibende Grenzen

Stand 18. November 2026. **Zehn weitere Komponenten deaktiviert und geprüft;
sieben exakte Analyse-/Diagnose-Hostnamen gefiltert.** Kein vollständiger Beweis
eines trackingfreien Fernsehers. [Anonymisierter Beleg](PRIVACY-RESULT.json).

## Erhaltungsumfang und Klarstellung

Besitzer verlangt alles nicht notwendige an Werbung/Tracking abzutrennen.
Streaming-Apps, HDMI, AirPlay, Bild/Ton, Fernbedienung und Einstellungen erhalten.
Es gibt keinen angeschlossenen Antennen-/Kabelempfang: Frühere pauschale
Bestätigungen von „normalem Fernsehen“ bezogen sich auf Samsung TV Plus.
Nach gesonderter Nachfrage **TV Plus ausdrücklich behalten**. Besitzer bestätigt
TV-Plus-Bild/Ton auch nach dieser neuen Reduktion. AirPlay wurde beim vorherigen
Profil bestätigt; erneuter Test nach dieser Stufe ausstehend. Spiegelungstest
wurde vom Besitzer als unwichtig abgewählt, Funktion nicht zusätzlich deaktiviert.

## Tatsächliche Änderungen

Frisches Inventar, ausgewählte Hersteller-Manifeste und Vetro-Schutzregeln
geprüft. Fest erlaubte neue IDs stehen in privacy_profile.py und Ergebnisbeleg:

- Samsung Analytics.
- CIS und CIS-API als weitere ACR-Zulieferer.
- Content-Grab-Dienst.
- Targeted-Ad-Dienst.
- Die drei eigenständigen PISA-/Adagent-Service-Komponenten.
- AdPlayer und der eigenständige ADPlayer von adplatform.

Jeweils Originalzustand vorab privat gespeichert; Änderungsabsicht vor dem
Netzaufruf journalisiert; pkgcmd -D für exakt eine feste ID mit --global;
Inventar mit refresh=1 für jede Änderung zurückgelesen. Diese neu geprüften
Root-Aufrufe erweitern die bisher schmale Liste im Vetro-UI nicht global:
Produktcode und dortige Schutzregeln bleiben unverändert. Keine Wildcard-
Abschaltung, Deinstallation oder ungeprüfte automatische Musterklassifikation.

Danach Vetros vorhandenen lokalen Domainfilter für genau sieben Hostnamen
aktiviert (Liste im Ergebnisbeleg). Namen stammen aus vorhandener Vetro-
Firmwareanalyse; Verwendungszweck teils aus referenzierenden Komponenten
abgeleitet, nicht durch vollständige Analyse unseres gesamten Netzverkehrs
bewiesen. Die spezielle TV-Plus-Werbedomänengruppe blieb aus Kompatibilitätsgründen
unangetastet. Keine breite Sperre von samsung.com/Samsung-Cloud-Domänen.

Filter ändert ausschließlich TV-Zustand: Konfigurations-/Original-/Filterdatei
unter /home/owner/share/vetro/dns und Bindmount der ergänzten hosts-Datei in
erreichbaren TV-Mount-Namensräumen. Originale hosts-Datei auf der Systempartition
wird nicht überschrieben/remountet. Resolveradressen bleiben erhalten.
Keine Router-/Mac-Einstellung, neue Mac-Rechte oder Installation.
Nach geprüftem vorherigem disabled/empty Filterzustand keine fremde Filterliste
überschrieben. API meldet enabled/applied=true und keine Namespacewarnungen.
Read-only-Test im PID-1- und Vetro-Dienst-Namensraum bestätigt sieben IPv4-
Sperreinträge und Auflösung eines Analysehosts auf die IPv6-Nulladresse.

## Was erhalten bleibt und warum

- com.samsung.tv.coba.adagent: Home lädt Teile dieser gemeinsam genutzten
  Bibliothek. Sie zu deaktivieren kann Home/Teile von Einstellungen beschädigen.
- com.samsung.tv.ad-web-framework: von TV Plus referenzierte Werbe-Wiedergabe.
  TV Plus soll ausdrücklich weiter funktionieren.
- Beide Privacy-Choices-Komponenten: Einstellungsoberflächen, nicht allein wegen
  der groben Vetro-Kategorie als Tracker abgeschaltet.
- Webruntime, Inhaltewiedergabe, Netzwerk, Konto-/Anmeldedienste, Uhrzeit,
  Zertifikats- und Internetprüfung sowie andere unklar gemeinsam genutzte
  Komponenten. Keine Heuristik „Samsung im Namen = entbehrlich“.

Samsung beschreibt TV Plus als werbefinanziert. Werbung im Stream kann daher
bleiben. Eine funktionierende Wiedergabekomponente darf nicht als Beweis für
weiterhin aktive separate Personalisierungs-/Erfassungsdienste missverstanden
werden; umgekehrt ist ihr Erhalt kein Beweis für vollständige Datenfreiheit.

## Einwilligungen: belegter Befund statt pauschalem Alles-aus

Besitzer fand zunächst die Optionen nicht. Direkter normaler Start der vorhandenen
Privacy-Choices-Webapp vom TV bestätigt; Besitzer sah die Datenschutzseite und
meldete dort „alle abgelehnt“. Keine Einwilligung per Datenbankschreibzugriff
geändert. Nur gezielte lesende Schema-/Titel-/Statusabfragen durchgeführt.

Zuordnung anhand der geräteeigenen Beschriftungen bestätigt:
- Interessenbasierte Werbung: gespeicherte Zustimmung false.
- Anzeigeinformationsdienste: zunächst gespeicherte Zustimmung true; nach der
  regulären Besitzeraktion jetzt in beiden aktuellen Abfragen false.
- Allgemeine Bedingungen/Smart-Hub-Datenschutzhinweis bleiben akzeptiert.

Die erste Weboberfläche ändert offenbar nicht dieselben Einwilligungen. Deshalb
nicht sämtliche Zustimmungen als ausgeschaltet bestätigt. TCFEnabled ist allein
kein Beweis persönlicher Zustimmung, ACR recognition_status=10 kein ohne
Enumbeleg interpretierter Ein/Aus-Schalter. Offizielle LAT-API ist aus diesem
Service nicht verfügbar; LAT bleibt unbestätigt, keine Werbe-ID ausgelesen.

Zwei Starts der nativen HomeSetting-App wurden vom TV bestätigt, sichtbar
erschien laut Besitzer nichts. Keine weiteren Argumente erraten. Anschließend
normale Menü-Taste ausgelöst und zum Menüpunkt AGB/Datenschutz angeleitet.
Besitzer meldete zwischendurch einen eigenen Neustart und bat um erneuten Versuch.
Dieser zunächst offene Punkt ist inzwischen abgeschlossen: nach regulärer
Besitzeraktion beide optionalen Zustimmungen in zwei aktuellen Leseabfragen aus. Nicht direkt isAgreed
in SQLite auf null setzen: das würde eine ordentliche Opt-out-Verarbeitung nicht
beweisen und könnte Zustimmungskonsistenz/Benachrichtigungen umgehen.

## Prüfungen und Grenzen

Vier neue Mocktests bestanden: exakter effektiver Flag-Rundlauf bei ursprünglich
schon deaktivierter Komponente; verlorene Antwort nach Mutation journalisiert
und rücknehmbar; bestehender fremder Domainfilter unverändert; geschützte/
gefälschte IDs verweigert. Vorhandene local-dns- und blocklist-Tests bestanden.
Das ersetzt weder Firmware-/Netzwerk-Audit noch Hardware-Rücknahmetest.

Nach Apply gesamtes Inventar gegen frische private Baseline verglichen:
nur die zehn vorgesehenen disabled-Flags geändert, alle onboot/autorestart-
Felder erhalten. Die zehn neuen Ziel-IDs fehlen in der laufenden App-Liste.
Zu erhaltende Komponenten bleiben enabled. Kein Zeitgewinn dieses Schritts
gemessen oder behauptet. Kein vollständiger Verkehrsmitschnitt durchgeführt.

Systemresolver-Filter ist kein Paketfilter/Firewall: nur exakte Namen; andere
Subdomains, Caches, direkte IPs, eigene Resolver/DoH oder spätere neue
Namensräume können den Filter umgehen. Keinerlei Null-Tracking-Garantie, auch
nicht für Drittanbieter-Streaming-Apps oder Samsung-Konto-/Serverdaten.
Firmwareaktualisierungen können Komponenten/Einwilligungen ändern.

## Bedienung und Rücknahme dieser Stufe

Aus Repository, TV_IP nur das freigegebene Gerät:

    python3 -B recovery/privacy_profile.py plan
    # Bereits durchgeführt; nicht blind wiederholen:
    python3 -B recovery/privacy_profile.py apply --tv TV_IP --owner-approved
    # Nur diese neue Stufe zurücknehmen:
    python3 -B recovery/privacy_profile.py restore --tv TV_IP --owner-approved --journal PRIVATE_JOURNAL

Exakter Journalpfad ausschließlich lokal unter recovery/private abgelegt.
Restore akzeptiert nur die feste Komponenten-Allowlist und boolesche Original-
werte, keine Befehle aus Exporten. Es nimmt nur die eigene Filterliste zurück,
unmountet nur Vetro-markierte hosts-Overlays und stellt die früheren effektiven
Komponentenflags wieder her. Keine fremde zwischenzeitliche Filterliste ersetzen.
Vorher deaktivierte Komponenten bleiben deaktiviert. Bei Timeout/Teilfehler
stoppen, Journal prüfen; kein blindes Wiederholen.

Vetros Filter kann nach Boot aus seiner Konfiguration wiederhergestellt werden;
Komponenten-/Filterpersistenz wurde nach dem gemeldeten Neustart bestätigt.
Die anschließende Consent-Abwahl wurde aktuell lesend bestätigt; ein weiterer
Neustart nach dieser letzten persönlichen Auswahl wurde nicht geprüft. Hardware-Rücknahme bislang ungeprüft.
Filterdateien können bei deaktiviertem Filter als inaktive Rücknahmedaten auf
dem TV verbleiben. Keine Byte-für-Byte-Datenbank- oder vollständige Root-Recovery.
Vorherige Leistungs-/Startkonfiguration wird durch diesen Restore nicht
angefasst; für komplette Rücknahme Stufen in umgekehrter Reihenfolge prüfen.

Die vom Besitzer in Samsungs UI vorgenommenen Datenschutzablehnungen werden
nicht automatisch wieder in Zustimmungen umgewandelt. Das wäre eine separate
persönliche Entscheidung im Samsung-Menü.

Quellen:
- [Samsung: ACR ist optional, Opt-out in Einstellungen](https://www.samsung.com/us/support/answer/ANS10010616/).
- [Samsung Developer: LAT beendet Personalisierung](https://developer.samsung.com/smarttv/develop/guides/unique-identifiers-for-smarttv/tizen-id-for-advertising.html).
- [Samsung Deutschland: TV Plus ist werbefinanziert](https://www.samsung.com/de/tvs/smart-tv/samsung-tv-plus/).
- Vetro app/service/debloat.js, app-facts.js, local-dns.js, blocklist.js und
  geräteeigene ausgewählte Paket-Manifeste/Menümetadaten; keine Kompatibilitäts-
  garantie allein aus Namensregeln abgeleitet.
