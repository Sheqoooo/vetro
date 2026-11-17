# Nächster Schritt: Vetro installieren

**Stand 17. November 2026: vorbereitet, noch nicht ausgeführt.**
Der Fernseher wurde nur lesend geprüft; die laufende Wiedergabe wurde nicht
gezielt verändert. Vor der Installation muss der Besitzer bestätigen, dass
der TV frei ist und die Installation jetzt stattfinden darf.

## Einfach erklärt

Das signierte Paket kann über den vorhandenen Vetro-Verbindungsbaustein übertragen
werden. Kein weiterer Download und keine neuen Mac-Rechte sind dafür vorgesehen.
Der Ablauf umgeht das fehlschlagende erneute Zertifikatsladen von Apps2Samsung.

Nach deiner Freigabe würde der Helfer:

1. Paket und Signaturen nochmals prüfen.
2. Gerätekennung gegen das ausgestellte Distributor-Zertifikat abgleichen,
   App-Liste lesen und abbrechen, wenn bereits Vetro erwähnt wird.
3. Prüfen, dass die vorgesehenen beiden temporären TV-Dateien fehlen.
   Bei fehlendem Lesezugriff oder unklarem Zustand wird nicht überschrieben.
4. Das persönliche `device-profile.xml` und das signierte WGT in den vom TV
   gemeldeten SDK-Stagingordner übertragen und bytegenau zurücklesen.
5. Die Installation von **vetrotvapp.app**, Paket **vetrotvapp**, anfordern.
6. Antwort und App-Liste erneut prüfen. Bei unklarem Ergebnis stoppen;
   keine automatische Wiederholung oder Deinstallation.

**Das kann die Wiedergabe unterbrechen.** Ein expliziter App-Start, Neustart oder
Wechsel der Developer-Host-IP ist nicht Bestandteil dieses Schritts.
Das Paket registriert jedoch einen Dienst mit On-Boot/Auto-Restart und enthält
Root-Komponenten. Ohne expliziten Startbefehl ist deshalb keine absolute Zusage
möglich, dass während/nach der Installation kein Hintergrundcode startet.
Ein späterer Root-Test und das Aktivieren des Launchers bleiben weitere Schritte.

## Was bereits am Gerät gelesen wurde

- Vetros vorhandener SDB-Client verbindet sich und liest `capability:`.
- Tizen 6.0; bestätigter `sdk_toolpath`:
  `/home/owner/share/tmp/sdk_tools`.
- `shell:0 vd_applist`: nichtleere Antwort, 103183 Bytes, keine Erwähnung von
  `vetrotvapp`. Die Rohdaten bleiben in einer privaten lokalen Baseline.
- Lesen von `device-profile.xml` über SYNC/RECV lieferte ausdrücklich
  `No such file or directory`. Es wurde kein unbekannter Fehler als Abwesenheit
  ausgelegt. Direkt vor einem Schreibversuch wird dies nochmals geprüft.

Die neuen Upload-/Installationsschritte wurden nur mit Mocks beziehungsweise als
lokaler Plan geprüft. Noch kein erfolgreicher Hardware-Upload oder Installationslauf.

## Technischer Ablauf und geprüfte Quellen

Kein Einsatz der Shell-Injektions-/Root-Hilfen aus den mitgelieferten
Forschungswerkzeugen. Deren SDB-Wrapper setzt außerdem ein externes SDB-Binary
voraus und passt nicht zu unserem minimalen Weg.

Eine geprüfte Variante ist der reine Transport-/Installationspfad des bereits
von Apps2Samsung verwendeten TizenSdb.Core 1.1.8. Die NuGet-Metadaten verweisen
auf [Commit 95f6492](https://github.com/PatrickSt1991/tizen-sdb/tree/95f6492c3413f0c98e0e6696b369e3382d280e81).
TizenInstaller.cs überträgt Profile/Pakete und ruft `0 vd_appinstall` auf, ohne
im Installationsschritt neu zu signieren. Seine separate native CLI wurde nicht
heruntergeladen: Sie sieht standardmäßig einen Schlüsselpfad außerhalb unseres
Projekts vor. Neuere Apps2Samsung-CLI-Quellen bieten weiterhin keinen passenden
ungeprüften "einfach signiertes Paket installieren"-Umweg.

`sdb-sync.cjs` ergänzt Vetros vorhandenen, erfolgreich lesend getesteten Client
um eng begrenztes RECV/SEND für Dateien unmittelbar im bestätigten Stagingordner.
Framing und DONE-Verhalten wurden gegen die genannte Engine gelesen.
Die reine Übertragungslogik verwendet keine privaten Schlüssel oder Keychain.
Es wird keine privilegierte TV-Shell injiziert.

Konkrete geplante Stagingdateien:

```text
/home/owner/share/tmp/sdk_tools/device-profile.xml
/home/owner/share/tmp/sdk_tools/vetro-f4229886fd551c59.wgt
```

Danach genau dieser Installationsaufruf über die SDB-Verbindung:

```text
shell:0 vd_appinstall vetrotvapp.app /home/owner/share/tmp/sdk_tools/vetro-f4229886fd551c59.wgt
```

Der Hash des Pakets bleibt
`f4229886fd551c599689c5671242dd00fe2267d224a193a198801cb32a2ceedb`.

## Bedienung — zunächst nur Plan

Aus PROJECT, mit bereits vorhandenem Node und projektinternem OPENSSL_CONF:

```sh
"$NODE" vetro/recovery/deploy_signed.cjs --plan
```

Dieser Aufruf öffnet keine TV-Verbindung. Der Schreibpfad ist nur über
`--confirm-install TV_IP` erreichbar und darf erst nach ausdrücklicher Freigabe
des Besitzers ausgeführt werden. Das Flag ist eine Bedienhürde, keine technische
Isolation oder Ersatz für die Freigabe. Kein Schreibaufruf bisher ausgeführt.
Private Journaldateien würden unter `recovery/private/deployments` liegen.

## Tests, Grenzen und Rücknahme

`sdb-sync.test.cjs`: fragmentierte Antworten, fehlende Datei, verweigerter Zugriff,
Größenbegrenzung, Pfadbegrenzung, SEND/DATA/DONE-Chunks und Erfolg/Fehlerantworten
mit Mocks geprüft. Vorhandene oder nicht lesbare Dateien werden als Hindernis
behandelt. Null-Byte-Dateien gelten ebenfalls als vorhanden.

Der Signaturprüfer wurde nach einem Dokumentationscommit korrigiert: Er prüft
nun die Produktquellen gegen den im Buildbeleg festgehaltenen Commit. Nur die
generierte Build-Metadatei wird gegen diese festgehaltene Revision verglichen.
Ein neuer Dokumentationscommit darf ein unverändertes signiertes Paket nicht
fälschlich als veränderte Nutzdaten melden. Positiver Signaturtest und beide
Manipulationstests danach erneut bestanden. Das Paket wurde nicht neu signiert
oder geändert.

Ein geplanter Rückweg wäre ausschließlich Vetro wieder zu deinstallieren und
nur die von uns neu angelegten Stagingdateien zu entfernen. **Dieser Rückweg ist
noch nicht auf Hardware getestet.** Kein pauschales `0 rmfile`, weil es fremde
Stagingdateien löschen könnte. Ein Fehler nach dem Übertragungsbeginn kann neue
Dateien hinterlassen; der private Journalstatus und Rückleseprüfung entscheiden
über die weitere gezielte Rücknahme. Automatische Bereinigung ist nicht eingebaut.
Eine vollständige Root-Rücknahme ist weiterhin nicht garantiert.

Offizielle Einordnung des üblichen SDK-Installationswegs:
[Samsung: Command Line Interface](https://developer.samsung.com/smarttv/develop/getting-started/using-sdk/command-line-interface.html).
Unser konkret vorbereiteter Helfer ist eine eigene Adaption der gelesenen
SDB-Engine, kein bereits hardwarevalidierter offizieller Tizen-CLI-Installationslauf.
