# Zertifikate: aktueller Stand am 17. November 2026

**Nachtrag:** Der unten vorbereitete Vetro-Weg wurde inzwischen genehmigt und
erfolgreich ausgeführt. Das Paket ist signiert und lokal geprüft; noch nicht am
TV installiert. Details: [Signierung mit Vetro](SIGNING-WITH-VETRO.md).
Die folgenden Abschnitte dokumentieren die vorausgegangene Diagnose.

## Einfach erklärt

**Die Samsung-Anmeldung und die Ausstellung haben funktioniert.** Es gibt jetzt
ein Author- und ein Partner-Distributor-Zertifikat im privaten Projektordner.
Du musst dich dafür gerade nicht noch einmal anmelden.

**Das Originalprogramm kann die Dateien hier aber nicht laden.** Es scheitert
beim Zugriff auf einen temporären macOS-Schlüsselbund mit:

> The specified keychain could not be found.

Das ist ein lokaler Ladefehler. Es ist kein Beleg für ein falsches Samsung-Passwort
oder abgelaufene Zertifikate. Ob die verwalteten Einschränkungen den temporären
Schlüsselbund verhindern oder ein anderer macOS-Fehler vorliegt, ist noch nicht
abschließend bewiesen. Keine Einschränkung wurde dafür gelockert.

## Was konkret geprüft wurde

- Zertifikatserstellung mit der originalen CLI beendet: Exitcode 0 und `ok: true`.
- Die gleiche Antwort meldet das Profil trotzdem als `usable: false`, ohne
  erkannte Geräteabdeckung. Diese Widersprüchlichkeit wird nicht als Erfolg
  der Signierung dargestellt.
- Beide PKCS#12-Dateien lassen sich mit dem vorhandenen OpenSSL und der lokalen
  Passwortdatei öffnen. Passwort und Schlüssel wurden nicht ausgegeben.
- Die separat ausgestellten Zertifikate sind vom 17. November 2026 bis zum
  17. November 2027 gültig. Das allein beweist keine erfolgreiche TV-Installation.
- Empfangsprozess beendet. Verbindungen zu Port 4794 auf IPv4- und IPv6-Loopback
  werden abgewiesen (jeweils ECONNREFUSED). Kein eigener Login-Empfänger mehr aktiv.
- Zertifikatsordner auf 0700 und seine Dateien auf 0600 beschränkt. Private
  Dateien bleiben im ignorierten Projektverzeichnis und werden nicht veröffentlicht.
- Lokale Zertifikatsprüfung ohne TV wiederholt: weiterhin `usable: false`.
- Mit Microsofts EventPipe nur diesen lokalen Prüfprozess diagnostiziert.
  Die private Diagnosedatei ist auf 0600 beschränkt und nicht zur Veröffentlichung
  vorgesehen. Darin sind `CreateTemporaryKeychain` und die oben genannte konkrete
  Fehlermeldung sichtbar. Kein neues Diagnoseprogramm installiert.

Microsoft dokumentiert, dass .NET unter macOS beim Laden privater Schlüssel aus
PKCS#12-Dateien ein Schlüsselbundobjekt mit Schreibzugriff benötigt. Das passt
zum beobachteten Fehler; seine genaue Berechtigungsursache bleibt eine Vermutung.

## Vorbereiteter nächster Weg

Vetro selbst enthält zusätzlich einen JavaScript-Signierungsweg in
`rooting/build.cjs`. Er liest PKCS#12-Dateien mit node-forge und umgeht damit
den beschriebenen .NET-/macOS-Ladepfad. Er wurde noch nicht ausgeführt.

Dafür sind zusätzliche, nur projektlokale Build-Bibliotheken nötig:
node-forge, jszip und tizen.js samt den im vorhandenen Lockfile festgehaltenen
Abhängigkeiten. Die tizen.js-Quelle ist auf Commit
`45b00106149d0c8eff74ead4a979c909dd80efd6` festgelegt; npm-Dateien besitzen
Integritätshashes. Das Lockfile meldet keine Installationsskripte. Es ist keine
vollständige Sicherheitsprüfung sämtlicher Abhängigkeiten. GPL-Lizenz von
tizen.js und übrige Lizenzen bleiben zu beachten.

Vor einem Download/Ausführen dieses zusätzlichen Werkzeugs wird die konkrete
Freigabe des Besitzers eingeholt. Keine globale Installation, keine Erweiterung
von Dateirechten und kein Zugriff auf persönliche Schlüsselbünde geplant.
Ein damit signiertes Paket wäre anschließend unabhängig zu prüfen.
Der weitere Installationsweg ist separat zu klären: Die normale Apps2Samsung-CLI
prüft und signiert bei `install` erneut und würde am aktuellen Ladefehler wieder
scheitern. Ein signiertes Paket allein löst diese zweite Hürde also nicht.

Am TV ist weiterhin nichts installiert und kein Root ausgeführt.

## Quellen

- [Microsoft: PKCS#12 unter macOS](https://learn.microsoft.com/en-us/dotnet/standard/security/cross-platform-cryptography)
- [Microsoft: EventPipe](https://learn.microsoft.com/en-us/dotnet/core/diagnostics/eventpipe)
- [Apps2Samsung: Profilprüfung](https://github.com/Apps2Samsung/Apps2Samsung/blob/v3.1.0/Apps2Samsung.Core/Certificate/CertificateProvisioningService.cs)
- [Apps2Samsung: macOS-Zertifikatsflags](https://github.com/Apps2Samsung/Apps2Samsung/blob/v3.1.0/Apps2Samsung.Core/Core/PlatformService.cs)
- [Apps2Samsung: Installationsablauf](https://github.com/Apps2Samsung/Apps2Samsung/blob/v3.1.0/Apps2Samsung.Cli/Commands/InstallCommand.cs)
