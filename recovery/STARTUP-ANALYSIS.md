**Aktueller Nachtrag:** Der alte Benutzer-Helfer wurde beim Boot nachweislich
bei 8,029 s ausgeführt und endete mit Exit 1; frühere Vermutung aus fehlendem
Log korrigiert. Seine Dateien wurden entfernt. Direkter nativer Startweg
vorbereitet, noch nicht installiert: [Befund und Rücknahme](NATIVE-START-TRIAL.md).

# Startverzögerung: gemessen, noch nicht behoben

Stand 17. November 2026. Ausschließlich lesende Diagnose und lokale Vorbereitung,
keine TV-Einstellung oder Startreihenfolge geändert, kein weiterer Neustart
durch ein Werkzeug ausgelöst.

**Nachtrag:** Der Besitzer hat den passiven Test-Neustart durchgeführt. Capture
beendet, neuer Kernelboot und vollständige passive Messung bestätigt:
Dienstprozess 103,092 s, Launcher 107,296 s.
[Datensparsamer Ergebnisbeleg](STARTUP-PASSIVE-RESULT.json).
Ein reversibler Benutzer-Startversuch ist lokal vorbereitet, aber noch nicht
auf dem TV eingerichtet: [Plan und Rücknahme](EARLY-START-TRIAL.md).

## Einfach erklärt

Beim beobachteten Kernelstart entstand der größte Teil der Wartezeit, **bevor
Vetros Dienst überhaupt als Prozess lief**. Root und Launcher sind danach schnell:

| Prozess | Start seit Kernelboot |
| --- | ---: |
| Vetro-Dienst | 104,11 Sekunden |
| Root-Agent | 107,08 Sekunden |
| Launcher | 108,22 Sekunden |

Der Root-Agent war 1,65 Sekunden nach dem Laden des Vetro-Moduls verbunden;
der erste SDB-Startversuch gelang. Das ist kein Fall von vielen Root-Retries.
Vetros Dienst hat bereits onboot=true und autorestart=true. Die UI-App selbst
hat beide Flags false; sie wird nicht auf Verdacht zum Autostart umgestellt.

Die Zeiten stammen aus `/proc/<pid>/stat` und dem gelesenen CLK_TCK-Wert, nicht
aus einer geschätzten Wartezeit des Besitzers. Der Abstand zum Drücken der
Power-Taste wurde damit **nicht** gemessen. Ein einzelner Kernelboot beweist
auch noch keinen festen 104-Sekunden-Timer oder dessen konkreten Verursacher.
Deshalb noch kein pauschales Versprechen eines Starts ohne Samsung-Oberfläche.

## Was gelesen wurde

- `/status`, dessen Initialisierungszeit und Zeitpunkte der Root-Versuche.
- `/proc/uptime`, CLK_TCK sowie stat-Zeilen des Dienstes, Root-Agenten und Dock.
- Ausschließlich Vetro-Zeilen der Paketdatenbank: onboot/autorestart/component.
- Service-cgroup sowie ausgewählte Boot-Units und monotone Startzeitpunkte.
  Predelayed/Delayed/Idle/Preload lagen in diesem Lauf ungefähr bei 29,52 / 34,59 /
  46,64 / 56,58 Sekunden. Das beweist nicht die Ursache des späteren Vetro-Starts.
- Gefiltertes Journal zu Vetro lieferte keine Zeilen. Ein erfolgreicher letzter
  Pipelinebefehl ist kein Nachweis für vollständige Journalverfügbarkeit.
- Ein System-Marker-Dienst war bei ungefähr 45,3 Sekunden mit Exitstatus 1
  fehlgeschlagen (touch eines Laufzeitmarkers). Kein Beleg, dass er den
  Vetro-Start bei 104 Sekunden verursacht hat. Nicht gestartet/repariert/geändert.

Rohe Prozess-IDs, Zeitstempel, Bootdaten, Pfade und Hersteller-Unitdateien bleiben
im privaten Projektordner. Nur nicht-identifizierende Messwerte werden veröffentlicht.
Ordner-/Dateirechte auf 0700/0600 beschränkt. Eine erste Parserfassung scheiterte
an einem fehlenden Zeilenumbruch der PID-Datei vor einer Markierung; rein lesende
Messung mit getrennten Markierungen korrigiert. Keine TV-Datei dafür verändert.

## Geprüfte Abkürzungen

- Vetro-eigene Root-Start-/Retry-/Dock-Timer gelesen. Ein kürzerer Retry-Timer
  würde diesen erfolgreichen ersten Versuch und den späten Prozessstart nicht
  beseitigen; deshalb nicht geändert.
- Offizielle Samsung-Prelaunch-Dokumentation gelesen: dieser alte Mechanismus
  wird seit Modelljahr 2019 nicht mehr unterstützt. Kein altes Manifest-Tag als
  angebliche Lösung für unseren neueren TV eingebaut.
- Kein Systemdienst deaktiviert, kein Hersteller-Unitfile überschrieben und
  kein eigener früher Root-Systemdienst auf dem TV eingerichtet.

## Passive Aufzeichnung vorbereitet

Vetro enthält bereits `app/scripts/boot-test.py`. Dessen Lese-/Prozesssnapshot-
Pfade wurden geprüft. Der normale Netzwerkpfad deaktiviert jedoch explizit
Proxies. Deshalb gibt es einen kleinen lokalen Transportadapter
`recovery/boot_observer.py`: Er verwendet dieselbe Auswertelogik mit dem bereits
funktionierenden curl-/Proxyweg, beschränkt Routen auf die Beobachtung und legt
Capture-Daten nur unter dem privaten startup-analysis-Verzeichnis ab.
Produktcode/TV-Paket bleiben unverändert.

Preflight: `/status`, `/telemetry` und `/probe` lesbar, READY. Die sechs vorhandenen
Recorder-Tests bestanden lokal (simulierter HTTP-Server, echte Kernelbootwechsel
vs. bloße Dienstneustarts/HTTP-Ausfälle, alte Probe, Marker, Dateien).
Das ist kein zusätzlicher Hardware-Neustarttest und keine Zusage über den Adapter
bei einem späteren Netzausfall. Captures überschreiben keine bestehenden Ordner.

Aus PROJECT, mit dem erlaubten Python:

```sh
/Library/Developer/CommandLineTools/usr/bin/python3 -B \
  vetro/recovery/boot_observer.py preflight --base http://TV_IP:8099

/Library/Developer/CommandLineTools/usr/bin/python3 -B -u \
  vetro/recovery/boot_observer.py record --mode passive --base http://TV_IP:8099 \
  --out "$PWD/recovery/private/startup-analysis/passive-YYYYMMDD-01" --duration 600
```

Erst auf **ARMED** warten. Ein auf diesem Weg vorbereiteter Recorder wurde für
den nächsten Besitzerschritt gestartet; er installiert nichts, öffnet keine App
und startet den TV nicht neu. `r` markiert die Aufforderung zum Neustart; die
Reaktionszeit des Besitzers ist damit keine exakte Kernelboot-Zeitmessung.
Den Neustart führt der Besitzer mit der Fernbedienung durch. Währenddessen
Vetro nicht manuell öffnen. Eine neue Boot-ID muss den Neustart bestätigen;
ein bloßer HTTP-Ausfall genügt nicht. Nach verbundenem Agenten noch mindestens
20 Sekunden beobachten, dann `q`. Maximal zehn Minuten; Ctrl-C speichert
Teilergebnisse. Kein abgeschlossener Capture-Erfolg für diesen Lauf behauptet.

## Rücknahme und nächster Schritt

Heute nur private Messungen und lokale Helfer/Dokumentation angelegt. Der Recorder
lässt sich mit q beenden. Keine TV-Rücknahme notwendig. Ein schnellerer Startweg
müsste erst anhand der getrennten Startphasen begründet, mit Originalwerten und
Rücknahme vorbereitet und vor TV-Schreibzugriff freigegeben werden.

Quellen: [Vetro-Boot-Test](../app/docs/BOOT-TEST.md),
[Samsung: Prelaunching](https://developer.samsung.com/smarttv/develop/guides/fundamentals/prelaunching-applications.html).
