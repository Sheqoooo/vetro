# TV Plus: nativer Vergleich läuft, zweiter Off-Boot noch offen

Stand 18. November 2026. Besitzer hat rücknehmbaren TV-Plus-Test mit mehreren
Neustarts freigegeben. Aktuell über Samsungs normale Funktion deaktiviert;
Besitzer bestätigt nach echtem Boot kein automatisch laufendes TV-Plus-Programm.
Kein Leistungsurteil, bis der zweite echte Off-Lauf vorliegt.
[Anonymisierter Stand](TVPLUS-COMPARISON-RESULT.json).

| Zustand | Lauf | Dienstprozess ab Boot | Leistenprozess ab Boot | Einschränkung |
| --- | --- | ---: | ---: | --- |
| Vor nativer Deaktivierung | A1 | 13,036 s | 36,216 s | Späte proc/stat-Nachlese nach bestätigtem Boot-ID-Wechsel |
| Vor nativer Deaktivierung | A2 | 12,556 s | 42,024 s | Regulär beobachtet |
| Nativ deaktiviert, Programm aus bestätigt | B1 | 12,312 s | 56,464 s | Regulär beobachtet |
| Nativ deaktiviert | B2 | offen | offen | Besitzer-Neustart steht aus |

Primärmetrik ist Prozessstart der Leiste, **keine visuell bestätigte vollständige
Bedienbereitschaft**. Alte ~45-s-Werte stammen aus einem anderen Profilstand.
Kleine Stichprobe/feste Reihenfolge, andere Beobachtungszeitpunkte, wechselnde
Boot-/Netz-/CPU-Last und ein verworfener Zwischenboot schränken Kausalität ein.
Kein statistischer Beweis. B1 liegt bereits über der On-Spannweite; derzeit
kein Hinweis auf einen verlässlichen Geschwindigkeitsgewinn.

## Der zunächst falsche Abschaltweg

Zwei vorhandene App-IDs zunächst einzeln mit festem Allowlist-Skript per
pkgcmd --global deaktiviert: TV Plus und TVPlusDeeplinker. Frisches vollständiges
Flag-Inventar/Filterkonfiguration privat gesichert; Registry-Kontrollen erfolgreich.

Trotzdem bestätigte der Besitzer nach diesem vermeintlichen Off-Boot laufendes
TV-Plus-Programm. Die Senderwiedergabe läuft hier nicht ausschließlich über
diese App-Einträge. Dieser Zwischenboot (Dienst 13,056 s, Leiste 41,424 s) ist
**ungültig für einen TV-Plus-Off-Vergleich** und wird nicht in Mittelwerte übernommen.

Versuch per privatem CANCEL gestoppt; Originalflags zurückgestellt und gegen
gesamtes Ausgangsinventar/Filterzustand unabhängig geprüft. Effektive Hardware-
Rücknahme dieses App-Flag-Versuchs damit bestätigt. Keine Deinstallation,
gemeinsame Bibliothek oder Senderdatenbank durch den Agenten verändert.

Das Komponenten-only-Skript tvplus_comparison.py ist für run/resume nun ausdrücklich
gesperrt. Plan erklärt den Gegenbefund. Die Auswertung verweigert B-Messungen ohne
zusätzlichen tvPlusOffVerified-Nachweis, auch bei scheinbar sehr großem Gewinn.
restore/lesende Nachlese bleiben verfügbar. Neun lokale Tests bestanden.

## Wirksame native Deaktivierung

Samsung-Home normal aufgerufen, Besitzer führte für 2020/2021-Geräte aus:

1. TV-Plus-Kachel markieren, am Ring nach unten.
2. Entfernen, danach ausdrücklich Deaktivieren.

Besitzer bestätigt Ausführung und nach neuem Power-Neustart kein automatisch
laufendes TV-Plus-Programm. Diese normale Samsung-Funktion nimmt TV-Plus-Sender
aus dem Guide. Keine fremden Sender oder Kanaldatenbanken direkt bearbeitet.

Frisches Inventar nach nativer Deaktivierung zeigt **keinerlei App-Flag-Unterschied
zur ursprünglichen A-Baseline**: Beide TV-Plus-App-IDs sind wieder enabled und
deren onboot/autorestart weiterhin false. Native Service-/Guide-Deaktivierung
und App-Disable sind auf diesem Gerät unterschiedliche Zustände.
Deshalb weder Paketflags allein noch ein bloßer API-Erfolg als Off-Beweis werten.

Native B-Messungen laufen mit dem vorhandenen read-only boot_observer.py.
Es verändert keine TV-Einstellungen, fordert keinen Fern-Reboot an und startet
keine App. Rohdaten/Boot-IDs bleiben privat. TV Plus muss nach jedem B-Boot auch
laut Besitzer ausbleiben; bei erneutem Programm keine gültige Off-Probe.

## Neustart- und Capture-Geschichte

Eine frühe Version sandte genau einen normalen systemctl-reboot-Aufruf an den
TV; Antwort unklar, innerhalb 180 s keine neue Boot-ID. Kein erzwungener Reboot,
Zusatzrecht oder Wiederholen. Keine Flagänderung in diesem ungültigen Lauf.
Host-pgrep für den eigenen Vergleichsprozess scheiterte an nicht verfügbarer
sysmond-Prozessliste; keine Berechtigung erweitert. Feste Wartefrist beendete
die erste Fassung. Anschließend nur Besitzer-Power-Neustarts verwendet.

Ein wartender manueller 180-s-Lauf vor Boot/Änderung per CANCEL beendet und
durch 900-s-Wartefenster ersetzt. A1 kam dennoch nach Ende dieses Collectors.
Neue Kernel-Boot-ID gegen erhaltene Vorboot-Baseline bestätigt; Prozesszeiten
nachträglich aus proc/stat/CLK_TCK nachgelesen. Kein vollständiger A1-Verlauf,
keine erste HTTP-Bereitschaftszeit erfunden. resume-Reihenfolge/Originalflags
geprüft; A2 danach regulär beobachtet.

A1/A2 und verworfener Flag-B1 hatten vor dem nächsten Lauf mindestens 100 s
Uptime. Nativer B1 wurde deutlich länger beobachtet; neuer B2-Observer erst
danach vorbereitet. B2 zunächst versehentlich vom Besitzer als neugestartet
gemeldet, direkt korrigiert; ohne neue Boot-ID nicht als Messlauf gezählt.

## Vergleich und Rücknahme

Vorab praktische Regel für zwei gültige On-/Off-Werte: mittlerer Gewinn muss
größer sein als zwei Sekunden sowie die Spannweite jeder Zweiergruppe.
Das ist kein statistischer Test. Keine Schlussfolgerung aus dem ungültigen
App-Flag-Boot. Bei fehlendem Gewinn ist das vorher gewünschte TV Plus wieder
herzustellen; die native Rücknahme benötigt jetzt die reguläre Samsung-UI.

Für 2020/2021 dokumentiert Samsung:
**Quelle → Samsung TV Plus markieren → nach oben → Zur Startseite hinzufügen.**
Das soll den nativen Dienst wieder aktivieren. Dieser native UI-Rückweg ist
noch nicht am Gerät geprüft; nicht mit bereits geprüfter Paketflag-Rücknahme
verwechseln. Sender-/Favoriten-/Cachebytes sind dadurch nicht garantiert exakt
wie vorher. Agent ändert keine Kanal-SQL-Daten direkt.

Die vorbereitete Paket-Restore-Routine betrifft nur den inzwischen bereits
zurückgenommenen falschen Abschaltweg und kann nativen Guide-/Servicezustand
nicht ersetzen. Alle früheren Datenschutz-/Startprofile, Einwilligungen,
Ad-Webframework, CoBA-Adagent, TV-Viewer, AirPlay und Webruntime bleiben erhalten.

## Lokale Werkzeuge

Aus Repository, mit ausschließlich der freigegebenen TV-Adresse:

    python3 -B recovery/tvplus_comparison.py plan
    # run/resume des Komponenten-only-Versuchs sind absichtlich gesperrt.
    # Bereits erledigte Paketflag-Rücknahme, bei Bedarf nur mit Originaljournal:
    python3 -B recovery/tvplus_comparison.py restore --tv TV_IP --owner-approved --journal PRIVATE_COMPARISON_JSON

    python3 -B recovery/boot_observer.py record --mode passive --base http://TV_IP:8099 --out PRIVATE_NATIVE_CAPTURE --duration 900

CANCEL im privaten alten Vergleichsordner beendet diesen Vergleich.
Read-only-Observer mit q beenden. Kein automatischer Fern-Neustart im aktuellen
Protokoll. Hardware-Startzeitgewinn und native Rücknahme nicht vorwegnehmen.

Quelle: [Samsung: Disable / Re-enable TV Plus, einschließlich 2020/2021](https://www.samsung.com/au/support/tv-audio-video/disable-samsung-tv-plus/).
Menüs sind modell-/regionsabhängig; wirksame Deaktivierung wurde hier zusätzlich
durch den Besitzer nach dem Boot bestätigt.
