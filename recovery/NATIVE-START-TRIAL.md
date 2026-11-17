**Einrichtungsnachtrag:** Nach der fortgesetzten Besitzeranweisung, eine Lösung
zu finden, im bereits freigegebenen Frühstartversuchsrahmen eingerichtet. Alle
Datei-Hashes, Linkziel und numerischen Besitzer/Rechte unabhängig zurückgelesen.
Kein Live-Start; Wirkung nach Neustart noch ungeprüft.
[Einrichtungsbeleg](NATIVE-START-RESULT.json).

Die folgenden Abschnitte bewahren den Vorbereitungsstand.

# Nativer Frühstart: eingerichtet, Bootmessung ausstehend

Stand 17. November 2026. Konkreter nächster Versuch, kein bestätigter schnellerer
Boot. Bestehender Vetro-Autostart und TV-Systemdateien bleiben unverändert.

## Was wir inzwischen wirklich wissen

Der erste Helfer wurde entgegen der ersten Vermutung **geladen und ausgeführt**:
Der gecachte Benutzer-Manager meldet Start 8,029 s, Ende 8,228 s, Exitcode 1.
ConditionResult=yes, LoadState=loaded, Result=exit-code. Das fehlende attempt.log
beweist daher nicht, dass Samsung den Benutzer-Unitpfad ignoriert. Der genaue
Fehler innerhalb des Skriptaufrufs ist nicht identifiziert. Gefilterte
Journal-/dlog-Abfragen lieferten dazu keine Zeilen.

Mit der tatsächlich konfigurierten Kernel-Bus-Adresse ist die reine Abfrage des
Benutzer-Managers möglich. Die zuvor versuchte Unix-Busadresse war ungeeignet.
UnitPath enthält den owner-Konfigurationspfad; default.target enthielt unseren
alten Helfer als Wants. Dateien sind entfernt, der alte Fehlerzustand bleibt bis
zum nächsten Reload/Boot nur im Manager-Cache. Dies ist keine weiter bestehende
Datei oder neue Startinstallation.

Owner und Manager laufen nach numerischer Prüfung tatsächlich als 5001:100.
Ein Namensalias auf UID 0 wurde hier ausgeschlossen. basic.target war nach
8,014 s aktiv, default.target nach 11,224 s.

Zwei vorübergehende, automatisch eingesammelte Benutzer-Units wurden geprüft:
1. Samsungs originales app_launcher -r vetrotvapp.svc meldete running, Exit 0.
2. app_launcher -s vetrotvapp.svc bestätigte den **bereits laufenden** Dienst,
   Exit 0, Laufzeit 179 ms. Die bestätigte PID entsprach dem vorherigen Dienst:
   kein Dienstneustart, kein App-Stop, kein Home-Wechsel.

Das ist ein Test des direkten Startaufrufs im laufenden System, **kein Beweis
für erfolgreichen Kaltstart bei Sekunde 30**. Die Unit-Definitionsdateien des
neuen Versuchs wurden noch nicht an den TV übertragen.

## Konkreter Vorschlag

Zwei kleine Benutzer-Unitdateien ersetzen den früheren Shellhelfer:
- Timer: Startgelegenheiten bei Bootsekunde 30, 50 und 70, Genauigkeit 1 s.
- Dienst: direkt /usr/bin/app_launcher -s vetrotvapp.svc, ohne eigenes Shellskript.
- Jede Anfrage maximal acht Sekunden. Höchstens drei Anfragen, kein Dauerloop.
- Nach erfolgreichem Rückgabestatus bleibt die Einmal-Unit aktiv; weitere
  Timergelegenheiten starten sie nicht erneut.
- Ein erfolgreicher Startauftrag ist noch kein Beleg für funktionierende Vetro-
  Leiste; das wird anschließend separat mit Bootmessung/PID und Sichttest geprüft.
- Scheitern alle Anfragen, bleibt der originale späte Vetro-Autostart erhalten.
  Ob frühe Fehlversuche dessen Timing beeinflussen, muss am Gerät geprüft werden.

Sekunde 30 ist ein vorsichtiger Versuch vor dem bisherigen Webappservice-Start.
50/70 sind begrenzte Rückfälle, wenn das System noch nicht bereit ist. Kein
Versprechen eines sofort Samsung-freien Bildschirms.

## Exakter Fußabdruck und Bedienung

Nur neue Pfade, Einrichtung verweigert bereits vorhandenes .config/systemd:

    /home/owner/.config/systemd/user/vetro-native-start-trial.service
    /home/owner/.config/systemd/user/vetro-native-start-trial.timer
    /home/owner/.config/systemd/user/.vetro-native-start-trial
    /home/owner/.config/systemd/user/default.target.wants/vetro-native-start-trial.timer
      -> ../vetro-native-start-trial.timer

Neue Verzeichnisse 0700, Dateien 0600, numerischer Eigentümer 5001:100.
Kein eigener ausführbarer TV-Code, keine Änderung vorhandener Hersteller-Units,
keine Root-Dateisystem-Remounts, keine Mac-Einstellung oder zusätzliche Mac-Rechte.

Aus dem Repository; TV_IP ist ausschließlich das freigegebene Gerät:

    python3 -B recovery/native_start_trial.py plan
    # Erst nach separater ausdrücklicher Freigabe:
    python3 -B recovery/native_start_trial.py apply --tv TV_IP --owner-approved

Apply schreibt nur neue Dateien; kein Start, kein Reboot und kein daemon-reload.
Danach Hashes/Link/Rechte zurücklesen, passive Messung arretieren, Besitzer
Neustart durchführen lassen. Managerzustand des neuen Timers und Dienstes
anschließend über die bekannte Kernel-Busadresse gezielt lesen.

## Rücknahme

    # Im freigegebenen Versuchsumfang, nach Prüfung:
    python3 -B recovery/native_start_trial.py remove --tv TV_IP --owner-approved

Remove prüft alle drei statischen Hashes, Linkziel und Elternverzeichnisse vor
irgendeiner Änderung. Dann stoppt es nur den eigenen Benutzer-Timer, entfernt
genau die eigenen Dateien, entfernt nur leere neu angelegte Verzeichnisse und
führt einen Benutzer-daemon-reload aus. Kein Vetro-App-Stop, kein Systemmanager-
Reload, kein rekursives Löschen. Fremde neue Units bleiben erhalten.
Bei verändertem Inhalt/Link oder unklarem Transportfehler abbrechen und prüfen,
keine blinde Wiederholung. Bei Verlust des Root-Zugangs ist der Rückweg nicht
automatisch garantiert. Noch kein Hardwaretest dieser neuen Rücknahme; kein
vollständiger Root-Rollback.

## Geprüft und noch offen

Sechs lokale Dateisystemtests: exakter Rundlauf, bestehende Konfiguration
verweigern, veränderte Datei verhindert jede Entfernung, fremde neue Datei
bleibt, Anfangssymlink verweigern, nachträglicher Elternlink verweigert Entfernung.
Testläufe nur im privaten Projektverzeichnis, keine TV-Datei benutzt.
TV-Transport und Benutzer-Timer-Stop/Reload sind dadurch nicht simuliert geprüft.
Planmodus erfolgreich, ohne Netzaufruf. Noch kein Apply am TV.
Die v244-Unitdateien sind anhand der Originaldokumentation erstellt, nicht mit
einem separaten Samsung-Unitvalidator hardwaregeprüft.

Quellen:
- [systemd v244: monotone Timer, mehrere Zeitangaben und bereits aktive Units](https://github.com/systemd/systemd/blob/v244/man/systemd.timer.xml).
- [systemd v244: oneshot, TimeoutStartSec und RemainAfterExit](https://github.com/systemd/systemd/blob/v244/man/systemd.service.xml).
- [Samsung/Tizen: systemd und Benutzer-Session beim Boot](https://github.com/Samsung/tizen-docs/blob/master/docs/platform/porting/kernel.md).
- [Vetro-Issue 179](https://github.com/andrearicci93/vetro/issues/179) betrifft dagegen
  einen bereits gestarteten Dienst und einen Dock-Timeout; passt nicht zu unserer
  größten Wartezeit vor Prozessstart. Keine kosmetische Timeoutkorrektur als Lösung.
