# Vetro: Sicherung vor Launcher-Änderungen

Status 16. November 2026: Vollständiger Fork lokal, Original-Apps2Samsung startet,
zwei unsignierte Pakete gebaut und fünf gezielte Offline-Tests bestanden.
Heute kein TV-Kontakt. Noch keine TV-Installation, kein Root und kein echter Restore-Test.

**Einfach anfangen: [Was fertig ist und was du später tun musst](START-HIER.md).**
Technische Einzelheiten: [Offline-Vorbereitung](OFFLINE-PREPARATION.md).

Dieses Verzeichnis enthält ein **Offline-Archivierungswerkzeug**, keinen fertigen
TV-Restore. Es führt keine Befehle auf einem Fernseher aus und hat keinen Netzwerkcode.
Es benötigt Python 3.8+ ohne zusätzliche Pakete.

## Dokumentation und Verlauf

- [Arbeitsprotokoll: Schritte, Befehle, Ergebnisse und offene Punkte](WORKLOG.md)
- [Vorlage für zukünftige Arbeitsschritte](STEP-TEMPLATE.md)
- [Einrichtungs- und Rücknahmeplan](ROLLOUT-AND-RECOVERY.md)
- [Geprüfte Quellversionen](SOURCE-REVIEW.json)

Das Arbeitsprotokoll wird mit den weiteren Änderungen fortgeführt. Echte
Gerätebaselines und Rohlogs bleiben privat. Die Repo-Regeln stehen in [AGENTS.md](../AGENTS.md).

## Was das Werkzeug kann

Später manuell beziehungsweise über einen separat freigegebenen Collector erfasste
JSON-Exporte unter `inbox/` einlesen, eine neue Sicherung unter `private/` erzeugen
und deren SHA-256-Prüfsummen kontrollieren. Bestehende Sicherungen werden nicht
überschrieben; fehlende, zu große und offensichtlich fehlerhafte Exporte führen
zum Abbruch. Symlinks und Pfade außerhalb dieses recovery-Verzeichnisses sind verboten.

Erwartete Dateien:

| Datei | Herkunft / Zweck |
| --- | --- |
| device.json | Manuell bestätigtes Modell, Firmware, exakter Vetro-Commit und Erfassungsphase |
| status.json | Vetro `/status`: Build und Integrationszustand |
| dock.json | Vetro `/dock`: Launcherzustand |
| remap.json | Vetro `/remap`: Tastenregeln |
| input.json | Vetro `/input`: Eingabe-Gerät und Eingabezustand |
| startup.json | Vetro `/startup`: App- und Service-Startflags |

`device.json` benötigt die nichtleeren Zeichenketten `model`, `firmware`,
`source_revision` und `stage`. `stage` muss `after-install-before-user-changes` sein.
Das Modell wird nicht vom Tool am TV überprüft. Die API-Exporte sind erst nach
Installation verfügbar und stellen deshalb **keinen Zustand vor Root/Installation** dar.
Keine Beispielwerte als vermeintlich echte Sicherung verwenden.

```sh
python3 -B recovery/backup_exports.py capture
python3 -B recovery/backup_exports.py verify private/ZEITSTEMPEL
```

Die Pfade sind relativ zum Skriptverzeichnis; der Aufruf kann vom Projektstamm
erfolgen. Das Werkzeug fordert keine Rechte an, stellt keine Verbindung her und
führt nichts aus den Exporten aus. Ein gültiges Archiv bestätigt nur die Integrität,
nicht die Vollständigkeit oder Wiederherstellbarkeit des TV-Zustands.

`private/` und `inbox/` sind ignoriert. Keine Zertifikate, Passwörter, Seriennummern,
IP-Adressen oder echten Geräteexporte auf GitHub hochladen. Gitignore ist keine
Zugriffssperre. Eine zweite Sicherungskopie außerhalb des Agentenzugriffs verwahrt
der Eigentümer selbst.

## Nächster Schritt

Offline-Prüfung am 2026-11-05: 10 Tests erfolgreich mit Python 3.9.6.
Unter der aktuellen Mac-Sandbox direkt ausführen, um Apples temporären
Starter-Cache zu vermeiden:

```sh
/Library/Developer/CommandLineTools/usr/bin/python3 -B -m unittest discover -s recovery -p 'test_*.py' -v
```

Nächster Schritt zu Hause: aktuelle TV-Adresse und Entwicklermodus prüfen, dann
die Original-CLI gezielt mit diesem TV testen. Die vorhandenen Einschränkungen
bleiben bestehen; fehlende Rechte werden konkret gemeldet. TV-Installation und
Root benötigen weiterhin eine ausdrückliche Freigabe. Ein echter Restore wird erst
mit geprüften Originalwerten und gerätespezifischer Rückleseprüfung implementiert.
