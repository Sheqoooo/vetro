# Vetro-Paket signiert — 17. November 2026

## Was jetzt fertig ist

**Die Signierung hat mit Vetros eigenem Build funktioniert.** Die bereits von
Samsung ausgestellten Zertifikate wurden verwendet. Keine erneute Anmeldung.
Apps2Samsung und die Zertifikate wurden nicht verändert; der fehlschlagende
macOS-Schlüsselbundpfad wurde für die Signierung nicht benötigt.

Das neue Paket liegt lokal unter `vetro/dist/vetro-integration-SIGNED.wgt`:

- Größe: **459007 Bytes**, **81 Dateien** einschließlich beider Signaturdateien.
- SHA-256: `f4229886fd551c599689c5671242dd00fe2267d224a193a198801cb32a2ceedb`.
- Build-Quellcommit: `11f752b50437fb10c4421d73474e0f5813a5aa8e`.
- Author- und Distributor-Signatur kryptografisch gegen die ausgestellten
  Zertifikate geprüft. Jeweils sämtliche referenzierten Hashes geprüft.
- Dateisatz und Nutzdaten stimmen bytegenau mit Vetros Integrationskollektor
  am aktuellen lokalen Buildstand überein.

**Noch keine TV-Installation und kein Root.** Ein signiertes Paket ist kein
Beweis, dass der Fernseher es akzeptiert oder dass Root funktioniert. Die
vollständige Zertifikatskette wurde nicht unabhängig gegen einen Truststore
validiert. Der ursprüngliche Apps2Samsung-Installationsweg bleibt wegen seiner
erneuten lokalen Profilprüfung/Signierung zu klären; nicht blind erneut starten.

## Wie es gemacht wurde

Der Besitzer hat nach Erläuterung die Vetro-Alternative freigegeben.
`rooting/build.cjs` ist unverändert geblieben. Dafür wurden die im vorhandenen
`rooting/on-boot-probe/package-lock.json` festgelegten 41 Pakete projektintern
bereitgestellt. Keine globale Installation und kein neuer Paketmanager.

Der neue Helfer `install_locked_signer.py` lädt npm-Archive von registry.npmjs.org
und prüft ihre Lockfile-Integrität. tizen.js wird über HTTPS als Archiv des
festen Commits `45b00106149d0c8eff74ead4a979c909dd80efd6` geladen; Dateisatz und
alle 15 Git-Blob-Hashes werden gegen den am festen Commit gelesenen Git-Baum
geprüft (`tizen-signer-tree.json`). Keine SSH-Verbindung oder privaten SSH-Schlüssel.
Archive mit Pfadüberschreitung, absoluten Pfaden, Links oder Gerätedateien werden
verweigert. Vorhandenes node_modules wird nicht überschrieben.

Entpackt wurde nach `rooting/on-boot-probe/node_modules`, Downloads und Beleg
liegen unter `PROJECT/tools/downloads/signing-deps`. Es wurden keine npm-Hooks,
Installationsskripte oder CLI-Binärdateien der Abhängigkeiten gestartet. Erst beim
Signieren werden die benötigten Bibliotheken ausgeführt. Das ist keine vollständige
Sicherheitsprüfung aller Bibliotheken. Deren ursprüngliche Lizenzen, insbesondere
GPL-3.0-only von tizen.js, bleiben erhalten.

`sign_package.py` liest das vorhandene Passwort aus der privaten Projektdatei
und übergibt es nur in der Umgebung des kurzlebigen Signierungsprozesses. Keine
Passwörter oder Schlüssel in Argumenten, Ausgaben oder öffentlichen Manifesten.
Der unveränderte Upstream-Build verwendet node-forge für PKCS#12, tizen.js für
Signaturen und jszip zum Verpacken. Vorhandene signierte Ausgaben werden nicht
überschrieben. Ausgabe mit Dateimodus 0600; Zertifikate weiter privat.

## Reproduzierbare Aufrufe

Aus PROJECT (TVBuild), mit den bereits vorhandenen Werkzeugen:

```sh
# Einmalig; verweigert bestehendes node_modules:
/Library/Developer/CommandLineTools/usr/bin/python3 -B vetro/recovery/install_locked_signer.py

# Liest nur vorhandene lokale Zertifikate; keine TV-Verbindung:
/Library/Developer/CommandLineTools/usr/bin/python3 -B vetro/recovery/sign_package.py

# NODE bezeichnet das bereits vorhandene gebündelte Node-Binary.
OPENSSL_CONF="$PWD/recovery/private/offline-tmp/openssl.cnf" \
TMPDIR="$PWD/recovery/private/tool-tmp" \
PATH=/Library/Developer/CommandLineTools/usr/bin:/usr/bin:/bin \
GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null \
"$NODE" vetro/recovery/verify_signed.cjs
```

Die Programme sind für die dokumentierte Verzeichnisaufteilung geschrieben.
Sie stellen keine neue technische Sicherheitsgrenze dar; die bestehenden
verwalteten Dateisperren bleiben aktiv. Persönliche Schlüsselbünde wurden nicht
freigegeben oder durchsucht, globale Einstellungen nicht geändert.

## Prüfergebnis und Korrekturen während der Arbeit

`verify_signed.cjs` liest das WGT erneut, prüft ZIP-CRC und Nutzdaten, vergleicht
die eingebetteten Zertifikate mit den separat ausgestellten öffentlichen
Zertifikatsdateien und prüft RSA-SHA512 mit Node/OpenSSL.
Die XML-Kanonisierung erfolgt separat mit dem vorhandenen macOS-xmllint, ohne
Netzwerk/DTD-Kataloge: Exclusive C14N für SignedInfo, C14N 1.1 für #prop.
Author: **80 Referenzen**, Distributor: **81 Referenzen**, alle geprüft.

Die erste Fassung des Prüfers hatte fälschlich auch für #prop Exclusive C14N
angenommen und meldete deshalb Digest mismatch. Das Paket wurde dafür nicht
geändert. Nach Abgleich des tatsächlich deklarierten C14N-1.1-Transforms wurde
der Prüfer korrigiert; beide Signaturen samt Properties-Digest bestehen.
`xmllint --help` meldete in dieser Version eine unbekannte Option und zeigte
die Optionen trotzdem an; der tatsächliche C14N-1.1-Aufruf gelang.
Eine Quelltextsuche im bereits verschobenen Staging-Verzeichnis schlug fehl;
anschließend die tatsächlichen installierten Quellpfade gelesen.

Zusätzliche Tests:

- Fünf Python-Tests bestanden: normale Archivdatei, verweigerte Pfadüberschreitung,
  absoluter Pfad, Symlink und Gerätedatei.
- Zwei Negativfälle bestanden: geänderte Payload-Datei wird verworfen;
  veränderte RSA-Signatur wird verworfen. Die echten Pakete bleiben unverändert.
- `git diff --check` ohne Fehler.

## Aufbewahrung und Rücknahme

Das signierte Paket enthält öffentliche persönliche Zertifikate. Es wird ebenso
wie private Schlüssel/Passwortdateien nicht auf GitHub hochgeladen. Dort stehen
nur Helfer, Prüfungen, Quellreferenzen, Prüfsumme und Dokumentation.

Downloadcache, node_modules und neu erzeugte Builddatei sind projektlokal und
können bei Bedarf gezielt entfernt werden. Keine solche Löschung ausgeführt;
nur synthetische Negativtestdateien wurden nach dem Test entfernt. Zertifikate
werden nicht automatisch gelöscht oder neu erzeugt. Kein TV-Rollback nötig,
weil in diesem Schritt keine TV-Verbindung oder Änderung durchgeführt wurde.
