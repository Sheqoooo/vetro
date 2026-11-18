# Offline-Vorbereitung vom 16. November 2026

## Umfang und tatsächlicher Stand

Der Besitzer hat Download und Vorbereitung der normalen Apps2Samsung-Version
autorisiert. Er befindet sich in einem anderen Netzwerk. Es wurde deshalb kein
TV-Ziel kontaktiert: keine Statusabfrage, kein Ping, kein SDB, kein Scan.
Keine Zertifikatserzeugung, Samsung-Anmeldung, TV-Installation oder Root-Ausführung.

Die ursprüngliche Anpassungs-/Fork-Idee für Apps2Samsung wird nicht umgesetzt.
Die frühere Bewertung in INSTALLER-REVIEW.md bleibt als Quellbefund erhalten;
die Entscheidung ist nun, das Original unter den bestehenden Grenzen zu versuchen.
Die gelungenen Offline-Starts beweisen nicht, dass dessen Installationspfad alle
Berechtigungsgrenzen erfüllt. Insbesondere Cache-/Logpfade, SDB-Proxy-Unterstützung
und das automatische Beenden anderer SDB-Prozesse bleiben beim Verbindungstest
zu berücksichtigen. Kein Verbindungsbefehl wurde heute ausgeführt.

## Verzeichnisaufteilung

`PROJECT` bezeichnet den vorhandenen TVBuild-Ordner. Der neue vollständige
Checkout liegt in `PROJECT/vetro`; die älteren Unterlagen in `PROJECT/recovery`
wurden nicht gelöscht. Die maßgeblichen neuen Repo-Dateien liegen unter
`PROJECT/vetro/recovery`. Download und Laufzeitdaten liegen neben dem Checkout.

```text
PROJECT/
  tools/downloads/Apps2Samsung-cli-v3.1.0-osx-arm64.tar.gz
  tools/apps2samsung/apps2samsung-cli
  recovery/private/apps2samsung/
  recovery/private/tool-tmp/
  vetro/                         vollständiger Git-Checkout
    recovery/START-HIER.md       kurze Anleitung
    recovery/apps2samsung_offline.py
    recovery/build-unsigned.cjs
    dist/                       ignorierte unsignierte Pakete und Manifest
```

Die vorhandenen privaten/temporären Ordner bleiben durch .gitignore vom üblichen
Commit ausgeschlossen. Ein zusätzlicher lokaler `tools/.gitignore` ignoriert
Download und Originalprogramm. Gitignore ist keine Zugriffssperre.
Dateien außerhalb des Projektordners wurden nicht freigegeben. Bestehende
Rechte auf Entwicklerwerkzeuge und das gebündelte Node wurden verwendet.

## Download und Originalprüfung

Bewusst das bereits geprüfte Release **v3.1.0**, kein automatisches Update auf
ein ungeprüftes neueres Release. GitHub-Release-Metadaten erneut gelesen.

- Datei: `Apps2Samsung-cli-v3.1.0-osx-arm64.tar.gz`
- Herkunft: [Originalrelease](https://github.com/Apps2Samsung/Apps2Samsung/releases/tag/v3.1.0)
- Größe: **32739187 Bytes**
- Erwarteter und lokal gemessener SHA-256:
  `a4a6557427b6dfd6b00399f24f04f3651e30f955eb21dc90e1826d0f604a914a`
- Archiv: nur ein Verzeichnis und eine reguläre ausführbare Datei;
  keine Symlinks, absoluten Pfade oder übergeordneten `..`-Pfade.
- Extrahierte Datei: **86236145 Bytes**, unverändert, im Projekt ausführbar gemacht.
- `codesign --verify --verbose=2`: erfolgreich. Genauere Anzeige:
  **Ad-hoc-Signatur, keine TeamIdentifier**. Das ist keine Prüfung einer
  Entwickleridentität oder Notarisierung. Keine Quarantänemarkierung entfernt.
- `--version`: `3.1.0+dea1eb391d559b3176f40f612550bdae0cebc493`.

Der frühere blockierte Download ist damit überholt; es wurden dafür keine
globalen Codex- oder macOS-Einstellungen geändert.

## Originalprogramm offline starten

Der neue Python-Starthelfer verändert das Programm nicht. Er prüft bei jedem
Aufruf zuerst den Archivhash und vergleicht das Programm mit dem Originalarchiv.
Er erlaubt ausschließlich vier Aktionen: Version, Hilfe, lokale Zertifikatsliste
und Installationshilfe. Ein Versuch mit `scan` wurde vor Programmstart mit
Exitcode 2 abgewiesen. Das ist eine Bedienbegrenzung des Helfers, keine eigenständige
technische Isolation gegen direkten Programmstart.

Aus dem PROJECT-Ordner, mit dem bereits erlaubten Python:

```sh
/Library/Developer/CommandLineTools/usr/bin/python3 -B vetro/recovery/apps2samsung_offline.py version
/Library/Developer/CommandLineTools/usr/bin/python3 -B vetro/recovery/apps2samsung_offline.py help
/Library/Developer/CommandLineTools/usr/bin/python3 -B vetro/recovery/apps2samsung_offline.py cert-status
/Library/Developer/CommandLineTools/usr/bin/python3 -B vetro/recovery/apps2samsung_offline.py install-help
```

Version, Hilfe, lokale Zertifikatsliste und Installationshilfe liefen erfolgreich.
Die Zertifikatsliste meldete für Public und Partner jeweils `exists: false` und
`usable: false`. Keine alten oder privaten Zertifikatsspeicher wurden übernommen.
Ohne TV-Adresse und ohne --prepare bleibt diese Aktion lokal (Quellpfad am
festen Release geprüft).

Prozesslokal gesetzt: APPS2SAMSUNG_DATA_DIR, TMPDIR,
DOTNET_BUNDLE_EXTRACT_BASE_DIR, DOTNET_CLI_HOME und DOTNET_CLI_TELEMETRY_OPTOUT.
Nur der jeweilige Prozess erhält diese Werte. HOME wird nicht umgebogen.
Der Daten- und Temporärordner wird auf Modus 0700 gesetzt. Aus dem Elternprozess
werden keine GitHub-Tokens oder sonstigen beliebigen Umgebungsvariablen übernommen.
Diese Maßnahmen decken die bekannten fest eingebauten macOS-Cachepfade nicht
automatisch ab; die verwalteten Dateisperren bleiben die technische Grenze.

## Vollständiger Fork und unsignierte Builds

Öffentlicher Fork per Git in ein neues Unterverzeichnis geklont, ohne die
bestehenden Workspace-Dateien zu überschreiben:

```sh
GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null GIT_TERMINAL_PROMPT=0 \
/Library/Developer/CommandLineTools/usr/bin/git clone --single-branch \
  --branch codex/recovery-preparation https://github.com/Sheqoooo/vetro.git vetro
```

Build-Ausgangsstand: **af64ee55d0af29c6d87aa360adb02ce70c17f176**,
Vetro-Version **0.3.5**. App-, Rooting- und Dock-Quellen unverändert.
Neue Vorbereitungshelfer und Dokumentation liegen außerhalb dieser Produktpfade.
Git liest für die ausgeführten Vorgänge keine globale Benutzerkonfiguration.

`build-unsigned.cjs` verwendet die bestehenden Funktionen `collectFiles`,
`collectIntegration` und `zip`. Die enthaltenen TV-Payloads werden nur eingepackt,
nicht ausgeführt. Es wurden keine npm-Pakete, Tizen Studio oder zusätzliche
Node-/Python-Runtimes installiert. Der signierende Upstream-Build wurde nicht
ausgeführt. Die Apps2Samsung-Installationshilfe bestätigt die spätere Installation
lokaler WGT-Dateien samt Signierung einer Arbeitskopie.

Erzeugt unter `vetro/dist`:

| Datei | Bytes | Einträge | SHA-256 |
| --- | ---: | ---: | --- |
| vetro-app-only-UNSIGNED.wgt | 775968 | 64 | b54496c9203a4b74fb36e3d52ef725fa019968f3f8763cb21e9347a654001953 |
| vetro-integration-UNSIGNED.wgt | 901117 | 79 | fcb0a7343f0fe3128f4d1903a143b9996d19664b076f8e0b33131ea75e8688c4 |

Das Manifest `OFFLINE-BUILD.json` hält Quellcommit, Dateihashes, Modus und die
ausdrücklichen Werte `signed: false`, `hardwareTested: false`, `installReady: false`
fest. Ein separater Python-ZIP-Leser prüfte beide ZIP-CRCs, XML-Manifeste,
Anzahl/eindeutige Dateinamen, Hashes, fehlende Signaturen und die Trennung der
Root-Payloads. Beides erfolgreich. Noch kein installierbares signiertes Paket.

## Tests und Wiederholung

Die vorhandene leere OpenSSL-Konfiguration im privaten Projekt-Testordner
vermeidet den gesperrten Zugriff auf die systemweite OpenSSL-Konfiguration.
Der bereits dokumentierte Offline-Preload ersetzt nur die gesperrte Host-Uptime;
die Boot-Szenarien der Docktests verwenden ihre eigenen Zeitmodelle.

Mit gebündeltem Node, OPENSSL_CONF und TMPDIR im Projekt sowie Git aus den
erlaubten Command Line Tools bestanden:

1. `app/tests/build.test.cjs`: Paketinhalt und Portvarianten.
2. `rooting/tests/package-boundary.test.cjs`: App/Integration getrennt,
   TV-Payloads vorhanden, keine Zertifikate oder historischen Werkzeuge im Paket.
3. `rooting/tests/node4-syntax.test.cjs`: Syntaxwächter für 44 Service-Dateien.
4. `app/tests/dock.test.cjs`: Launcher-Lebenszyklus und simulierte Rückkehr.
5. `app/tests/dock-catalog.test.cjs`: Katalog und Pfadfilter.

Keine komplette Testsuite und keine Hardware-Tests. Es wurde insbesondere kein
Vetro-HTTP-Server auf dem Mac gestartet.

Beispiel zur Wiederholung aus PROJECT; NODE ist das bereits vorhandene
Node-Binary, kein neu heruntergeladenes Werkzeug:

```sh
OPENSSL_CONF="$PWD/recovery/private/offline-tmp/openssl.cnf" \
TMPDIR="$PWD/recovery/private/tool-tmp" \
PATH=/Library/Developer/CommandLineTools/usr/bin:/usr/bin:/bin \
GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null \
"$NODE" --require ./vetro/recovery/offline-test-host.cjs vetro/app/tests/build.test.cjs

# Offline-Verpackung, führt die TV-Programme nicht aus:
OPENSSL_CONF="$PWD/recovery/private/offline-tmp/openssl.cnf" \
TMPDIR="$PWD/recovery/private/tool-tmp" \
PATH=/Library/Developer/CommandLineTools/usr/bin:/usr/bin:/bin \
GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null \
"$NODE" vetro/recovery/build-unsigned.cjs
```

Der Buildhelfer verweigert geänderte App-/Rooting-/Dock-Quellen sowie ein
Überschreiben abweichender vorhandener Pakete. Nach einem neuen Commit kann
die eingebettete Revision und damit der Pakethash wechseln. Bestehende Builds
dann zuerst aufbewahren und einen neuen Ausgabeordner gezielt vorbereiten;
nicht die alten Dateien still überschreiben.

## Was später fehlt und wie wir zurückgehen

Die TV-/Hostadressen aus der früheren Sitzung sind **keine aktuelle Bestätigung**.
Zu Hause zuerst Adresse und Entwicklermodus neu prüfen, dann genau einen
TV-Verbindungsversuch. Keine Netzsuche. Danach gegebenenfalls Samsung-Anmeldung
und Partner-Signierung für das Integrationspaket, mit separater Freigabe zur
TV-Installation und zum Root-Start. Ein abweichender Ort oder blockierter Zugriff
wird konkret gemeldet; Berechtigungen werden nicht automatisch erweitert.

Die heutige Vorbereitung ist auf Projektdateien begrenzt. Zur Rücknahme können
die neu erstellten Werkzeug-/Downloadordner, synthetischen temporären Daten und
Buildausgaben gezielt entfernt werden. Vor später vorhandenen Zertifikaten und
echten Sicherungen erst separat sichern und Freigabe einholen. Der vollständige
Checkout kann aufbewahrt werden. Heute wurde keine Löschung vorgenommen.
Keine heutige TV-Änderung rückgängig zu machen; die frühere manuelle
Entwicklermodus-Aktivierung bleibt davon unberührt. Vollständige Root-Rücknahme
weiterhin nicht nachgewiesen.
