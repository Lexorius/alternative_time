# Alternative Time Systems for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/Lexorius/alternative_time.svg)](https://github.com/Lexorius/alternative_time/releases)
[![GitHub Activity](https://img.shields.io/github/commit-activity/y/Lexorius/alternative_time.svg)](https://github.com/Lexorius/alternative_time/commits/main)
[![License](https://img.shields.io/github/license/Lexorius/alternative_time.svg)](LICENSE)

Eine Home Assistant Integration, die verschiedene alternative Zeitsysteme als Sensoren bereitstellt. Perfekt für Science-Fiction-Fans, Technik-Enthusiasten oder alle, die gerne mit alternativen Zeitkonzepten experimentieren!

## 🌟 Features

Diese Integration bietet folgende Zeitsysteme:

### 🌍 **Zeitzone**
- Zeigt die aktuelle Uhrzeit in einer beliebigen Zeitzone an
- Wähle aus allen verfügbaren Zeitzonen weltweit
- Ideal für internationale Teams oder Reiseplanung

### 🚀 **Sternzeit (Stardate)**
- Star Trek TNG-Style Sternzeit-Berechnung
- Basiert auf dem Jahr 2323 als Ausgangspunkt
- Für alle Trekkies und Science-Fiction-Fans

### 🌐 **Swatch Internet Time**
- Die revolutionäre Internetzeit aus den 90ern
- Ein Tag = 1000 Beats
- Keine Zeitzonen, überall gleich (Biel Mean Time)

### 🔢 **Unix Timestamp**
- Sekunden seit dem 1. Januar 1970
- Standard in der Informatik
- Nützlich für Entwickler und System-Administratoren

### 📅 **Julianisches Datum**
- Astronomische Zeitrechnung
- Kontinuierliche Tageszählung seit 4713 v. Chr.
- Verwendet in der Astronomie und Wissenschaft

### 🔟 **Dezimalzeit**
- Französische Revolutionszeit
- 10 Stunden pro Tag, 100 Minuten pro Stunde
- Ein faszinierendes historisches Zeitkonzept

### 🔤 **Hexadezimalzeit**
- Der Tag in 65536 (0x10000) Teile geteilt
- Zeitangabe im Hexadezimalsystem
- Für Programmierer und Technik-Begeisterte

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
  - entity: sensor.alternative_time_dezimalzeit
    name: Revolutionszeit
```

#### Glance Card
```yaml
type: glance
title: Zeiten
entities:
  - entity: sensor.alternative_time_zeitzone
  - entity: sensor.alternative_time_sternzeit
  - entity: sensor.alternative_time_swatch_internet_time
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

#### Beispiel: Beat-Time Notification
```yaml
automation:
  - alias: "Internet Time @500"
    trigger:
      - platform: template
        value_template: >
          {{ states('sensor.alternative_time_swatch_internet_time')
             | regex_replace('@', '') | float >= 500.0 
             and states('sensor.alternative_time_swatch_internet_time')
             | regex_replace('@', '') | float < 501.0 }}
    action:
      - service: notify.mobile_app
        data:
          message: "Es ist @500 Swatch Internet Time!"
```

## 🌐 Mehrere Instanzen

Du kannst beliebig viele Instanzen der Integration hinzufügen, um verschiedene Zeitzonen oder Konfigurationen zu haben:

1. **Weltzeituhr**: Erstelle mehrere Instanzen mit verschiedenen Zeitzonen
2. **Thematische Gruppen**: Eine Instanz für Sci-Fi-Zeiten, eine für historische Zeiten
3. **Raum-basiert**: Verschiedene Zeitsysteme für verschiedene Räume

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

## 📝 Geplante Features

- [ ] Weitere Sci-Fi Zeitsysteme (Star Wars, Stargate, etc.)
- [ ] Historische Kalender (Maya, Römisch, etc.)
- [ ] Anpassbare Sternzeit-Formeln
- [ ] Zeitkonvertierung zwischen Systemen
- [ ] Grafische Uhren-Cards
- [ ] Weltzeit-Dashboard-Template

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
- Alle Contributor und Tester

## 📧 Support

- **Issues**: [GitHub Issues](https://github.com/Lexorius/alternative_time/issues)
- **Diskussionen**: [GitHub Discussions](https://github.com/Lexorius/alternative_time/discussions)

---

Made with ❤️ by [Lexorius](https://github.com/Lexorius)