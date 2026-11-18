# Installer-Prüfung und Freigabeplan

Stand 2026-11-06. Nur Quell-/Releaseprüfung; keine Software heruntergeladen,
entpackt, installiert oder ausgeführt.

## Festgehaltener Kandidat

Apps2Samsung CLI v3.1.0, Release-Quelle
`dea1eb391d559b3176f40f612550bdae0cebc493`.
Asset: `Apps2Samsung-cli-v3.1.0-osx-arm64.tar.gz`, 32739187 Bytes.
Vom GitHub-Release gemeldeter SHA-256:
`a4a6557427b6dfd6b00399f24f04f3651e30f955eb21dc90e1826d0f604a914a`.
Dies ist eine erwartete Prüfsumme aus Release-Metadaten, keine lokal nachgewiesene
Dateiintegrität und keine unabhängige Hersteller-Signatur.
Die CLI-Verzeichnisübersicht wurde zunächst auf beta gelesen; relevante
Quellbefunde danach am festen Release v3.1.0 geprüft.

## Befunde am Release

1. CliPaths unterstützt --data-dir und APPS2SAMSUNG_DATA_DIR.
   Zertifikate und SDB-Schlüssel können dadurch unter einem Projektpfad liegen.
   Die Variable muss bereits beim Prozessstart gesetzt sein: die statische
   DefaultDataDir-Initialisierung berücksichtigt sie; --data-dir allein wird erst
   später durch Use verarbeitet.
2. CliPaths.Downloads delegiert jedoch an UserPaths.Cache. Unter macOS sieht
   UserPaths weiterhin Library/Caches/Apps2Samsung und Library/Logs/Apps2Samsung
   unter dem Benutzerprofil vor. Ein Datenordner-Schalter ist deshalb **kein
   Nachweis für ausschließlich projektinterne Schreibzugriffe**. Nicht jeder
   einzelne Pfad wurde durch reale Ausführung beobachtet.
3. CliServices verdrahtet ClearCompetingSdbServer mit ProcessHelper.KillSdbServers.
   Vor einer neuen Verbindung wird der Callback aufgerufen. Er sucht Prozesse
   namens sdb und versucht proc.Kill(). Das kann andere Entwicklungsarbeit
   beeinflussen. Keine solche Funktion hier ausgeführt.
4. InProcessSdbEngine erstellt SdbTcpDevice aus IPAddress.Parse(ip) und ruft
   ConnectAsync() auf. In dieser Integrationsschicht ist kein CONNECT-Proxy
   konfiguriert. Die externe TizenSdb-Abhängigkeit wurde noch nicht vollständig
   geprüft; Proxy-Kompatibilität ist **nicht nachgewiesen**, nicht ausgeschlossen.
   Unser erfolgreicher CONNECT-Test ist kein Erfolgstest dieses Installers.
5. Explizites --tv ist vorhanden; InstallCommand validiert diese Adresse.
   Ein pauschaler scan-Befehl ist nicht erforderlich und bleibt außerhalb der
   Freigabe. --local-ip erlaubt die explizite Hostadresse. Start nach Installation
   ist standardmäßig aus; --remove-first/--allow-remove werden nicht verwendet.
   Diese Optionen ersetzen keine technische Netzwerk-/Dateisperre.
6. CertificateEndpoints verwendet svdca.samsungqbe.com. BrowserSamsungLogin
   öffnet für die Anmeldung einen lokalen TCP-Listener und bei entsprechender
   Option einen Browser. Vollständige Login-/Download-Zielliste und Portbelegung
   sind noch zu prüfen. Anmeldung erfolgt durch Besitzer, Geheimnisse nicht im Chat.

## Entscheidung

Unveränderte CLI unter den bestehenden Anforderungen **noch nicht freigegeben**.
Kein pauschales Aufheben der Dateisperre, keine Administratorrechte und keine
breite Netzfreigabe als Lösung. Ein sicherer angepasster Installer müsste
sämtliche Daten-/Cache-/Temporärpfade projektintern halten, automatisches Beenden
fremder Prozesse entfernen und den vorhandenen verwalteten TV-Transport
ausdrücklich unterstützen. Das ist ein Plan, keine bereits existierende oder
getestete Lösung. Auch benötigte Buildwerkzeuge einer Anpassung müssen zunächst
separat bewertet werden. Alternativ ist eine getrennte, vom Besitzer kontrollierte
Installationsumgebung zu planen; sie ist nicht eingerichtet.

## Konkrete nächste Phasen

1. Installer-Anpassung beziehungsweise besser passenden Transportweg zunächst
   als Quelländerung vorbereiten und offline prüfen. Noch keine TV-Schreiboperation.
2. Danach exakt benötigte Downloads und Verbindungsziele mit Zweck/Prüfsumme
   zur Einzelgenehmigung vorlegen. Bestehende TV-Freigabe deckt externe
   Zertifikats-/Builddienste nicht automatisch ab.
3. Erst nach Freigabe projektintern bereitstellen, Start ohne Verbindung prüfen,
   anschließend ausschließlich bekannte TV-Adresse authentifizieren und lesen.
   Falls das nicht innerhalb der Grenzen funktioniert: stoppen und Befund nennen.
4. Signierung vorbereiten, Besitzer meldet sich selbst an. Eigenes Paket aus
   vollständig festgehaltenem Vetro-Fork bauen. Kein Katalogpaket an dessen Stelle.
5. Vorherzustand lokal sichern, TV-Installation und ersten Root-Start einzeln
   freigeben. Post-Installations-Exporte nicht als Vor-Root-Backup bezeichnen.
6. Zuerst nur Launcher an/aus und Rücklesen testen; danach Home aus Apps/HDMI,
   Standby, Kaltstart. Keine Debloat-/Paketentfernung. Vollständige Root-Rücknahme
   ist weiterhin kein bestätigtes Ergebnis.

## Nachvollziehbarkeit

GitHub-API-URLs für Verzeichnis und Release waren über das Webwerkzeug nicht
abrufbar; über den vorhandenen GitHub-Connector erfolgreich ausschließlich
lesend abgerufen. Ein zunächst vermuteter ProcessHelper-Pfad unter Helpers/Core
existiert nicht; der tatsächliche Pfad Core/ProcessHelper.cs wurde anschließend
am festen Release gelesen. Keine Sicherheitsfreigaben verändert.

Quellen:
- [Release v3.1.0](https://github.com/Apps2Samsung/Apps2Samsung/releases/tag/v3.1.0)
- [CliPaths](https://github.com/Apps2Samsung/Apps2Samsung/blob/v3.1.0/Apps2Samsung.Cli/CliPaths.cs)
- [UserPaths](https://github.com/Apps2Samsung/Apps2Samsung/blob/v3.1.0/Apps2Samsung.Core/Portability/UserPaths.cs)
- [CliServices](https://github.com/Apps2Samsung/Apps2Samsung/blob/v3.1.0/Apps2Samsung.Cli/CliServices.cs)
- [ProcessHelper](https://github.com/Apps2Samsung/Apps2Samsung/blob/v3.1.0/Apps2Samsung.Core/Core/ProcessHelper.cs)
- [SDB-Integration](https://github.com/Apps2Samsung/Apps2Samsung/blob/v3.1.0/Apps2Samsung.Core/Sdb/InProcessSdbEngine.cs)
- [CLI-Optionen](https://github.com/Apps2Samsung/Apps2Samsung/blob/v3.1.0/Apps2Samsung.Cli/CliOptions.cs)
- [InstallCommand](https://github.com/Apps2Samsung/Apps2Samsung/blob/v3.1.0/Apps2Samsung.Cli/Commands/InstallCommand.cs)
- [Zertifikatsziele](https://github.com/Apps2Samsung/Apps2Samsung/blob/v3.1.0/Apps2Samsung.Core/Certificate/CertificateEndpoints.cs)
- [Browser-Anmeldung](https://github.com/Apps2Samsung/Apps2Samsung/blob/v3.1.0/Apps2Samsung.Cli/BrowserSamsungLogin.cs)
