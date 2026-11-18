# Was Vetro beim Start noch bremst

Stand 18. November 2026. Der Vetro-Dienst startet bei den letzten Messungen
12–13 Sekunden nach Kernelstart. Der Leistenprozess startet nach 36–56 Sekunden.
In drei nachvollziehbaren Aufzeichnungen lagen allein zwischen der Initialisierung
des Dienstes und der Verbindung des Agenten rund 16–21 Sekunden. Die Zeiten
stammen aus vorhandenen Messungen auf dem Gerät. Sie messen den Prozessstart,
die sichtbare Reaktion auf Home wurde dabei nicht mitgestoppt.

Vetro startet die Leiste in der aktuellen Fassung erst mit verbundenem Agenten.
Bei vorhandenem App-Katalog geht das schon aus dem Cache. Drei Leistenlogs zeigen
jeweils rund 0,5 Sekunden zwischen dem Aufruf der Ereignisschleife und dem Ende
der Darstellungs-Vorbereitung. Das deckt nur den letzten Teil der Initialisierung
ab. Die Messungen belegen keinen großen Gewinn durch das Entfernen von TV Plus
oder weiteren zufällig gewählten Samsung-Diensten.

## Zwei verschiedene Einschaltfälle

- **Normales Aus- und Einschalten:** Vetros Leiste ist bereits als eigener Prozess
  vom Hintergrundagenten getrennt. Sie ist dafür ausgelegt, Standby zu überstehen.
  Auf diesem Gerät steht der Test aus. Bei unveränderter Boot-Kennung und
  unverändertem Leistenprozess kann Home nach dem Aufwachen sofort verfügbar sein.
  Falls die Leiste neu startet, erfassen wir, welche Komponente verloren ging.
- **Vollständiger Neustart:** Samsung bietet für diese Modellgeneration das
  frühere App-Prelaunch nicht mehr an. Vetro nutzt für die Oberfläche den
  vorhandenen Bildschirmdienst und für Home die Eingabeverarbeitung des TVs.
  Eine früh sichtbare Oberfläche ist ein separates Ziel von früher Home-Bereitschaft.
  Der vorhandene native Launcher kennt einen sichtbaren Modus, im aktuellen
  Startpfad wird er verborgen gestartet. Ein getrennter Sichttest kann prüfen,
  ob der Launcher unmittelbar nach seiner Initialisierung sinnvoll angezeigt
  werden kann. Das würde den Warteabschnitt davor allein nicht verkürzen.

Eine Entfernung von Systemkomponenten ohne belegte Abhängigkeiten kann HDMI,
AirPlay, Einstellungen oder die Bedienung beschädigen. Die Messdaten liefern
dafür derzeit keinen konkreten Kandidaten. Start und Reaktionszeit im Menü
separat messen. Firmware und Samsung-Systemdienste wurden für diese Analyse
nicht verändert.

Quelle: [Samsung Developer – App-Prelaunch und Modelljahre](https://developer.samsung.com/smarttv/develop/guides/fundamentals/prelaunching-applications.html).
