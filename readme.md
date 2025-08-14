#### Beispiel: Rettungsdienst-Protokoll
```yaml
automation:
  - alias: "Einsatz-Zeitstempel"
    trigger:
      - platform: state
        entity_id: input_boolean.einsatz_aktiv
        to: 'on'
    action:
      - service: notify.logfile
        data:
          message: >
            Einsatzbeginn: {{ states('sensor.alternative_time_nato_zeit_rettungsdienst') }}
      - service: input_text.set_value
        data:
          entity_id: input_text.einsatz_start
          value: "{{ states('sensor.alternative_time_nato_zeit_rettungsdienst') }}"
```# Alternative Time Systems for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/Lexorius/alternative_time.svg)](https://github.com/Lexorius/alternative_time/releases)
[![GitHub Activity](https://img.shields.io/github/commit-activity/y/Lexorius/alternative_time.svg)](https://github.com/Lexorius/alternative_time/commits/main)
[![License](https://img.shields.io/github/license/Lexorius/alternative_time.svg)](LICENSE)

Eine Home Assistant Integration, die verschiedene alternative Zeitsysteme als Sensoren bereitstellt. Perfekt für Science-Fiction-Fans, Technik-Enthusiasten, Militär-Interessierte oder alle, die gerne mit alternativen Zeitkonzepten experimentieren!

## 🌟 Features

Diese Integration bietet folgende Zeitsysteme:

### 🌍 **Zeitzone**
- Zeigt die aktuelle Uhrzeit in einer beliebigen Zeitzone an
- Wähle aus allen verfügbaren Zeitzonen weltweit
- Ideal für internationale Teams oder Reiseplanung
- Update-Intervall: 1 Sekunde

### 🚀 **Sternzeit (Stardate)**
- Star Trek TNG-Style Sternzeit-Berechnung
- Basiert auf dem Jahr 2323 als Ausgangspunkt
- Für alle Trekkies und Science-Fiction-Fans
- Update-Intervall: 10 Sekunden

### 🌐 **Swatch Internet Time**
- Die revolutionäre Internetzeit aus den 90ern
- Ein Tag = 1000 Beats
- Keine Zeitzonen, überall gleich (Biel Mean Time)
- Update-Intervall: 1 Sekunde

### 🔢 **Unix Timestamp**
- Sekunden seit dem 1. Januar 1970
- Standard in der Informatik
- Nützlich für Entwickler und System-Administratoren
- Update-Intervall: 1 Sekunde

### 📅 **Julianisches Datum**
- Astronomische Zeitrechnung
- Kontinuierliche Tageszählung seit 4713 v. Chr.
- Verwendet in der Astronomie und Wissenschaft
- Update-Intervall: 60 Sekunden

### 🔟 **Dezimalzeit**
- Französische Revolutionszeit
- 10 Stunden pro Tag, 100 Minuten pro Stunde
- Ein faszinierendes historisches Zeitkonzept
- Update-Intervall: 1 Sekunde

### 🔤 **Hexadezimalzeit**
- Der Tag in 65536 (0x10000) Teile geteilt
- Zeitangabe im Hexadezimalsystem
- Für Programmierer und Technik-Begeisterte
- Update-Intervall: 5 Sekunden

### 🏛️ **Maya-Kalender**
- Lange Zählung (Long Count): z.B. `13.0.12.1.15`
- Tzolk'in (260-Tage-Zyklus): z.B. `8 Ahau`
- Haab (365-Tage-Zyklus): z.B. `3 Pop`
- Komplette Maya-Datumsangabe in einem Sensor
- Update-Intervall: 1 Stunde

### 🎖️ **NATO-Zeit (Basis)**
- NATO Date-Time Group im Format `DDHHMM`
- Tag, Stunde und Minute in militärischer Notation
- Beispiel: `151430` für 15. Tag des Monats, 14:30 Uhr
- Update-Intervall: 1 Sekunde

### 🌐 **NATO-Zeit mit Zonenindikator (DTG)**
- Vollständige NATO Date-Time Group
- Format: `DDHHMM[Zone] MON YY`
- Beispiel: `151430Z JAN 25` (15. Januar 2025, 14:30 UTC)
- Inkludiert NATO-Zeitzonenbuchstaben und Monat
- Automatische Erkennung der lokalen Zeitzone
- Update-Intervall: 1 Sekunde

### 🚑 **NATO-Zeit Rettungsdienst**
- Deutsche Rettungsdienst-Notation
- Format: `DD HHMM MONAT YY` (mit Leerzeichen)
- Beispiel: `15 1430 JAN 25` (15. Januar 2025, 14:30 Uhr)
- Deutsche Monatsabkürzungen (MÄR, MAI, OKT, DEZ)
- Standard bei Feuerwehr, Rettungsdienst und THW
- Update-Intervall: 1 Sekunde

## 📦 Installation

### Über HACS (empfohlen)

1. Öffne HACS in deiner Home Assistant Installation
2. Klicke auf die drei Punkte oben rechts
3. Wähle "Custom repositories"
4. Füge diese URL hinzu: `https://github.com/Lexorius/alternative_time`
5. Wähle "Integration" als Kategorie
6. Klicke auf "Add"
7. Suche nach "Alternative Time Systems" und installiere es
8. Starte Home Assistant neu

### Manuelle Installation

1. Lade den `alternative_time` Ordner herunter
2. Kopiere ihn in dein `/config/custom_components/` Verzeichnis
3. Starte Home Assistant neu

## ⚙️ Konfiguration

### Über die Benutzeroberfläche

1. Gehe zu **Einstellungen** → **Geräte & Dienste**
2. Klicke auf **Integration hinzufügen**
3. Suche nach **Alternative Time Systems**
4. Folge dem Konfigurationsassistenten:
   - Vergib einen Namen für die Instanz
   - Wähle die gewünschten Zeitsysteme aus
   - Bei Zeitzone: Wähle deine gewünschte Zeitzone
5. Klicke auf **Absenden**

### Konfigurationsoptionen

| Option | Beschreibung | Standard |
|--------|--------------|----------|
| Name | Name der Instanz | Alternative Time |
| Zeitzone aktivieren | Zeigt Zeit in gewählter Zeitzone | ✓ |
| Zeitzone | Gewünschte Zeitzone | Europe/Berlin |
| Sternzeit aktivieren | Star Trek Sternzeit | ✓ |
| Swatch Time aktivieren | Internet Beat Time | ✓ |
| Unix Timestamp | Unix Zeitstempel | ✗ |
| Julianisches Datum | Astronomische Zeit | ✗ |
| Dezimalzeit | Französische Rev. Zeit | ✗ |
| Hexadezimalzeit | Hex-Zeit | ✗ |
| Maya-Kalender | Maya-Datumsangabe | ✗ |
| NATO-Zeit | Militärzeit ohne Zone | ✗ |
| NATO-Zeit mit Zone | Militärzeit mit Zonenindikator | ✗ |
| NATO-Zeit Rettungsdienst | Deutsche Rettungsdienst-Notation | ✗ |

## 🎯 Verwendung

### Sensor-Entitäten

Nach der Konfiguration werden folgende Sensoren erstellt (je nach Auswahl):

- `sensor.[name]_zeitzone` - Ausgewählte Zeitzone
- `sensor.[name]_sternzeit` - Sternzeit
- `sensor.[name]_swatch_internet_time` - Swatch Beat Time
- `sensor.[name]_unix_timestamp` - Unix Zeit
- `sensor.[name]_julianisches_datum` - Julian Date
- `sensor.[name]_dezimalzeit` - Dezimalzeit
- `sensor.[name]_hexadezimalzeit` - Hex-Zeit
- `sensor.[name]_maya_kalender` - Maya-Datum
- `sensor.[name]_nato_zeit` - NATO-Zeit
- `sensor.[name]_nato_zeit_mit_zone` - NATO-Zeit mit Zone
- `sensor.[name]_nato_zeit_rettungsdienst` - NATO-Zeit Rettungsdienst

### Dashboard-Beispiele

#### Einfache Entitätskarte
```yaml
type: entities
title: Alternative Zeitsysteme
entities:
  - entity: sensor.alternative_time_sternzeit
    name: Sternzeit
  - entity: sensor.alternative_time_swatch_internet_time
    name: Internet Time
  - entity: sensor.alternative_time_maya_kalender
    name: Maya-Kalender
  - entity: sensor.alternative_time_nato_zeit_mit_zone
    name: NATO-Zeit
```

#### Glance Card
```yaml
type: glance
title: Zeiten
entities:
  - entity: sensor.alternative_time_zeitzone
  - entity: sensor.alternative_time_sternzeit
  - entity: sensor.alternative_time_swatch_internet_time
  - entity: sensor.alternative_time_nato_zeit
show_icon: true
show_name: true
show_state: true
```

#### Markdown Card mit allen Zeiten
```yaml
type: markdown
content: |
  ## 🕐 Alternative Zeitsysteme
  
  **Sternzeit:** {{ states('sensor.alternative_time_sternzeit') }}
  
  **Internet Time:** {{ states('sensor.alternative_time_swatch_internet_time') }}
  
  **Maya-Kalender:** {{ states('sensor.alternative_time_maya_kalender') }}
  
  **NATO-Zeit:** {{ states('sensor.alternative_time_nato_zeit_mit_zone') }}
  
  **Unix:** {{ states('sensor.alternative_time_unix_timestamp') }}
  
  **Dezimal:** {{ states('sensor.alternative_time_dezimalzeit') }}
```

### Automatisierungen

#### Beispiel: Tägliche Sternzeit-Ansage
```yaml
automation:
  - alias: "Sternzeit Ansage"
    trigger:
      - platform: time
        at: "12:00:00"
    action:
      - service: tts.google_say
        data:
          entity_id: media_player.wohnzimmer
          message: >
            Sternzeit {{ states('sensor.alternative_time_sternzeit') }}
```

#### Beispiel: NATO-Zeit Benachrichtigung
```yaml
automation:
  - alias: "Zulu Zeit Mittag"
    trigger:
      - platform: template
        value_template: >
          {{ states('sensor.alternative_time_nato_zeit')[2:6] == '1200' }}
    action:
      - service: notify.mobile_app
        data:
          message: "Es ist 1200 Zulu Zeit!"
```

#### Beispiel: Maya-Kalender Tageswechsel
```yaml
automation:
  - alias: "Maya Tageswechsel"
    trigger:
      - platform: state
        entity_id: sensor.alternative_time_maya_kalender
    action:
      - service: notify.mobile_app
        data:
          message: "Neuer Maya-Tag: {{ states('sensor.alternative_time_maya_kalender') }}"
```

## 🌐 Mehrere Instanzen

Du kannst beliebig viele Instanzen der Integration hinzufügen, um verschiedene Zeitzonen oder Konfigurationen zu haben:

1. **Weltzeituhr**: Erstelle mehrere Instanzen mit verschiedenen Zeitzonen
2. **Thematische Gruppen**: Eine Instanz für Sci-Fi-Zeiten, eine für historische Zeiten, eine für militärische Zeiten
3. **Raum-basiert**: Verschiedene Zeitsysteme für verschiedene Räume

## 📊 NATO Date-Time Group (DTG) Formate

### Standard NATO DTG (Militär):
```
DDHHMM[Zone] MON YY
```
Beispiel: `151430Z JAN 25`

### Deutsche Rettungsdienst-Notation:
```
DD HHMM MONAT YY
```
Beispiel: `15 1430 JAN 25`

Die Rettungsdienst-Notation wird in Deutschland bei Feuerwehr, Rettungsdienst, THW und Katastrophenschutz verwendet. Sie unterscheidet sich durch:
- **Leerzeichen** zwischen Tag und Zeit
- **Keine Zeitzone** (immer lokale Zeit)
- **Deutsche Monatsabkürzungen**: MÄR (März), MAI (Mai), OKT (Oktober), DEZ (Dezember)

### Komponenten:
- **DD**: Tag des Monats (01-31)
- **HH**: Stunde (00-23)
- **MM**: Minute (00-59)
- **Zone**: NATO-Zeitzonenbuchstabe (A-Z, außer J)
- **MON**: Monatsabkürzung (JAN, FEB, MAR, etc.)
- **YY**: Jahr (zweistellig)

### Beispiele:
- **Militär**: `151430Z JAN 25` - 15. Januar 2025, 14:30 UTC
- **Rettungsdienst**: `15 1430 JAN 25` - 15. Januar 2025, 14:30 lokale Zeit
- **Mit Zone**: `031200B MAR 25` - 3. März 2025, 12:00 UTC+2 (Bravo)
- **Einsatzprotokoll**: `25 1800 DEZ 25` - 25. Dezember 2025, 18:00 Uhr

### NATO-Zeitzonentabelle

| Buchstabe | Name | UTC-Offset | Beispielregion |
|-----------|------|------------|----------------|
| Z | Zulu | UTC±0 | London (Winter) |
| A | Alpha | UTC+1 | Berlin (Winter) |
| B | Bravo | UTC+2 | Berlin (Sommer) |
| C | Charlie | UTC+3 | Moskau |
| D | Delta | UTC+4 | Dubai |
| E | Echo | UTC+5 | Pakistan |
| F | Foxtrot | UTC+6 | Kasachstan |
| G | Golf | UTC+7 | Thailand |
| H | Hotel | UTC+8 | China |
| I | India | UTC+9 | Japan |
| K | Kilo | UTC+10 | Sydney |
| L | Lima | UTC+11 | Salomonen |
| M | Mike | UTC+12 | Neuseeland |
| N | November | UTC-1 | Azoren |
| O | Oscar | UTC-2 | Brasilien |
| P | Papa | UTC-3 | Argentinien |
| Q | Quebec | UTC-4 | Puerto Rico |
| R | Romeo | UTC-5 | New York |
| S | Sierra | UTC-6 | Chicago |
| T | Tango | UTC-7 | Denver |
| U | Uniform | UTC-8 | Los Angeles |
| V | Victor | UTC-9 | Alaska |
| W | Whiskey | UTC-10 | Hawaii |
| X | X-ray | UTC-11 | Samoa |
| Y | Yankee | UTC-12 | Baker Island |

**Hinweis:** J (Juliet) wird übersprungen, um Verwechslungen mit I zu vermeiden.

## 🐛 Fehlerbehebung

### Integration wird nicht gefunden
- Stelle sicher, dass der Ordner korrekt in `custom_components` liegt
- Prüfe die Ordnerstruktur: `/config/custom_components/alternative_time/`
- Starte Home Assistant komplett neu

### Sensoren zeigen "unavailable"
- Prüfe die Logs unter Einstellungen → System → Logs
- Stelle sicher, dass mindestens ein Zeitsystem aktiviert ist
- Lösche die Integration und füge sie neu hinzu

### Zeitzone zeigt falsche Zeit
- Überprüfe die gewählte Zeitzone in der Konfiguration
- Stelle sicher, dass die System-Zeit deines Home Assistant korrekt ist

### "Blocking call" Warnung
- Die Integration verwendet asynchrone Zeitzoneninitialisierung
- Falls die Warnung weiterhin auftritt, starte Home Assistant neu

## 🚀 Performance

Die Integration ist optimiert für minimale Systembelastung:
- Event-basierte Updates statt Polling
- Individuelle Update-Intervalle pro Sensor
- Asynchrone Operationen für Zeitzonenberechnungen
- Ressourcenschonende Implementierung

## 📝 Geplante Features

- [ ] Weitere Sci-Fi Zeitsysteme (Star Wars, Stargate, etc.)
- [ ] Historische Kalender (Römisch, Chinesisch, etc.)
- [ ] Anpassbare Sternzeit-Formeln
- [ ] Zeitkonvertierung zwischen Systemen
- [ ] Grafische Uhren-Cards
- [ ] Weltzeit-Dashboard-Template
- [ ] Konfigurierbare Update-Intervalle
- [ ] Sonnenzeit und Mondphasen

## 🤝 Beitragen

Contributions sind willkommen! 

1. Fork das Repository
2. Erstelle einen Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Committe deine Änderungen (`git commit -m 'Add some AmazingFeature'`)
4. Push zum Branch (`git push origin feature/AmazingFeature`)
5. Öffne einen Pull Request

## 📄 Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert - siehe [LICENSE](LICENSE) für Details.

## 🙏 Danksagungen

- Home Assistant Community für die großartige Plattform
- Star Trek für die Inspiration zur Sternzeit
- Swatch für die revolutionäre Internet Beat Time
- Die Maya-Kultur für ihr faszinierendes Kalendersystem
- Alle Contributor und Tester

## 📧 Support

- **Issues**: [GitHub Issues](https://github.com/Lexorius/alternative_time/issues)
- **Diskussionen**: [GitHub Discussions](https://github.com/Lexorius/alternative_time/discussions)

## 📈 Version History

### v1.2.0 (Latest)
- ✨ NATO-Zeit Rettungsdienst-Format hinzugefügt
- 🔧 NATO-Zeit korrigiert (jetzt mit Datum)
- 📝 Erweiterte Dokumentation für alle NATO-Formate

### v1.1.0
- ✨ Maya-Kalender hinzugefügt
- ✨ NATO-Zeit (mit und ohne Zonenindikator) hinzugefügt
- 🐛 Async-Zeitzoneninitialisierung für bessere Performance
- 🐛 Blocking call Warnung behoben

### v1.0.0
- 🎉 Erste Veröffentlichung
- ✨ Basis-Zeitsysteme implementiert

---

Made with ❤️ by [Lexorius](https://github.com/Lexorius)