# Früherer Start: eingerichtet, Neustarttest ausstehend

Stand 17. November 2026. Nach ausdrücklicher Besitzerfreigabe eingerichtet.
Datei-Hashes, Linkziel, Besitzer und Rechte am TV zurückgelesen und bestätigt.
Noch nicht gestartet; Wirkung und Rücknahme am TV bleiben ungeprüft.
[Einrichtungsbeleg](EARLY-START-RESULT.json).

Die folgenden Vorbereitungsabschnitte beschreiben den ursprünglichen Plan.
 [Passive Vergleichsmessung](STARTUP-PASSIVE-RESULT.json):
Neuer Kernelboot bestätigt, Vetro-Dienst **103,092 s**, Launcher **107,296 s**.
Die erste Prozessmessung lag bei 104,11 beziehungsweise 108,22 Sekunden.
Das späte Erzeugen des Dienstprozesses ist wiederholt beobachtet; ein bestimmter
interner TV-Timer oder dessen Ursache ist damit noch nicht bewiesen.

## Was ich als Nächstes vorschlage

Ein zusätzlicher **Benutzer-Starthelfer auf dem TV** fordert den schon installierten
Vetro-Dienst über den normalen `app_launcher` früher an. Er ersetzt Vetro nicht,
ändert keine Samsung-Bootdienste und richtet keinen weiteren Root-Daemon ein.
Die originale On-Boot-Registrierung von Vetro bleibt als bisheriger Weg bestehen.

**Das ist ein Versuch.** Ob Samsungs angepasster Benutzer-Manager die neue
Startdatei auswertet, ob er früher läuft und ob die App-Anforderung früh akzeptiert
wird, ist noch nicht hardwaregeprüft. Selbst ein früherer Start garantiert keine
vollständig Samsung-freie Anzeige direkt nach dem Einschalten.

## Warum dieser Weg

Nur lesend festgestellt:

- Der System-Unitpfad liegt unter `/etc`, `/run` und `/usr/lib`; `/` ist ein
  schreibgeschütztes vdfs-Dateisystem. Keine Änderung/Remount durchgeführt.
- Ein systemd-244-Benutzermanager läuft bereits als TV-Benutzer owner (UID 5001).
  `user@5001.service` existiert hier nicht als normale System-Unit; das Fehlen
  dieses Namens bedeutet deshalb nicht, dass kein Benutzermanager läuft.
- Benutzerkonfiguration unter `/home/owner/.config` existiert; darunter war
  noch kein systemd-Verzeichnis zu sehen. Manager-Steuerung über die vermutete
  D-Bus-Adresse war nicht erreichbar; kein daemon-reload ausgeführt.
- Das Originalhandbuch von systemd **v244** sieht `~/.config/systemd/user` als
  Benutzer-Unitpfad vor. Das ist eine begründete Testidee, kein Beweis für
  unverändertes Verhalten der Samsung-Variante.
- `/usr/bin/app_launcher`, `/usr/bin/sha256sum` und owner-Gruppe users sind vorhanden.

Ein erster Versuch, ausgewählte Prozess-Umgebungsfelder mit tr zu lesen, hatte
zu stark maskierte Steuerzeichen. Mit korrekten NUL-/Zeilenumbruchmustern erneut
nur dieselben ausgewählten Pfadfelder gelesen; keine solchen Werte ausgegeben.
Keine unselektierten Umgebungsdaten oder Zugangsdaten gesammelt/veröffentlicht.

## Genau geplante Dateien auf dem TV

```text
/home/owner/.config/systemd/user/vetro-early-start-trial.service
/home/owner/.config/systemd/user/default.target.wants/vetro-early-start-trial.service
    -> ../vetro-early-start-trial.service
/home/owner/share/vetro-early-start-trial/start.sh
/home/owner/share/vetro-early-start-trial/.trial-owned
```

Der Helfer schreibt später ausschließlich sein eigenes `attempt.log` in den
letztgenannten Ordner. Es enthält Uptime und die Antwort auf den einen normalen
Startaufruf für `vetrotvapp.svc`, keine Passwörter oder Zertifikate.

Neue Verzeichnisse gehören owner:users und sind 0700, Startskript 0700,
Unit-/Markierungsdatei 0600. Die schon vorhandene `.config` wird nicht umgestellt.
Der Vorgang verweigert die Einrichtung, sobald das systemd-Verzeichnis oder der
eigene Helferordner bereits existiert oder als Link vorliegt. Dadurch keine
Übernahme/Überschreibung fremder Benutzerkonfiguration.

Die Unit läuft als vorhandener TV-Benutzer, verwendet `Type=simple`, um den
Benutzer-Zielstart nicht bis zum Ende des App-Aufrufs warten zu lassen, und
begrenzt die Helferlaufzeit auf 20 Sekunden plus 2 Sekunden Stopzeit. Kein
automatischer Retry-Loop. Der eigentliche App-Dienst wird wie sonst über Samsungs
Anwendungsverwaltung angefordert. Ob Kindprozesse/TV-Lifecycle im konkreten
Versuch wie erwartet getrennt bleiben, muss am Gerät geprüft werden.

**Vor Freigabe:** nur lokale Dateien, Plan, Syntax-/Dateitests. Kein Helfer auf dem
TV eingerichtet, gestartet oder entfernt. Aktuell bleibt alles beim normalen
Vetro-Start mit der gemessenen Verzögerung.

## Konkrete Bedienung und Rücknahme

Aus PROJECT, wobei TV_IP ausschließlich das freigegebene Gerät bezeichnet:

```sh
# Nur lokalen Plan zeigen:
/Library/Developer/CommandLineTools/usr/bin/python3 -B vetro/recovery/early_start_trial.py plan

# Erst nach ausdrücklicher Freigabe: neue Benutzerdateien anlegen, noch kein Live-Start:
/Library/Developer/CommandLineTools/usr/bin/python3 -B vetro/recovery/early_start_trial.py apply --tv TV_IP --owner-approved

# Zugehörige gezielte Rücknahme, ebenfalls erst nach Freigabe:
/Library/Developer/CommandLineTools/usr/bin/python3 -B vetro/recovery/early_start_trial.py remove --tv TV_IP --owner-approved
```

Apply/Remove verwenden die bestehende Root-Verbindung des TVs, keine neuen
Mac-Rechte. Ein Flag ersetzt die Freigabe nicht. Private übermittelte Skripte
und Antworten werden lokal journalisiert. Bei Fehler/Timeout keine blinde
Wiederholung: ein Teil der Dateien könnte bereits bestehen.

Remove prüft Markierung, Dateihashes, Verzeichnisse und Linkziel **vor** dem
Löschen. Es entfernt nur die oben genannten eigenen Dateien und das eigene Log;
keine rekursive Löschung. Neu hinzugekommene andere Units bleiben erhalten.
Veränderte Dateien/Links stoppen die Rücknahme zur Prüfung. Leere neu erstellte
Verzeichnisse werden entfernt, anderweitig belegte erhalten.

Die Rücknahme ändert keine Vetro-Paketflags und stoppt den laufenden Launcher
nicht. Nach Entfernen und erneutem Neustart soll der ursprüngliche Vetro-On-Boot-
Weg gelten; **auch diese Wirkung ist noch nicht am TV getestet**. Das ist kein
vollständiger Root-Rollback. Bei Verlust des Vetro-Zugangs wäre zunächst wieder
der Entwicklerzugang vom Mac herzustellen; die entfernte Erreichbarkeit ist
keine garantierte Notfall-Recovery für einen nicht startenden Fernseher.

## Lokale Prüfungen

Sechs Dateisystemtests mit synthetischem Projektverzeichnis bestanden:

1. Anlegen und Entfernen stellt ursprüngliche leere Verzeichnisse wieder her.
2. Vorhandene fremde systemd-Konfiguration wird nicht angerührt.
3. Veränderte eigene Unit verhindert automatisches Entfernen.
4. Zwischenzeitlich hinzugekommene fremde Unit bleibt erhalten.
5. Ein symlink-basierter Konfigurationspfad wird vor Schreiben verweigert.
6. Nachträglich ausgetauschter Elternlink verhindert Löschen.

Die erste Fassung offenbarte in zwei Tests eine Shell-Guard-Schwäche:
`set -e` allein beendet nicht jede fehlgeschlagene AND-Liste. Vor irgendeinem
TV-Einsatz durch explizite Abbruchbedingungen korrigiert. Danach alle Tests
bestanden. POSIX-Shellsyntax des Startskripts geprüft. Die Unit wurde vor dem
Gerätetest auf Type=simple mit RuntimeMaxSec umgestellt, anschließend Dateitests
erneut bestanden. Das ersetzt keine Samsung-/systemd-Hardwarevalidierung.

Quellen: [systemd v244: User Unit Search Path](https://github.com/systemd/systemd/blob/v244/man/systemd.unit.xml),
[systemd v244: Service-Laufzeit und Starttypen](https://github.com/systemd/systemd/blob/v244/man/systemd.service.xml).
