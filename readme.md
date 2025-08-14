# Alternative Time Systems for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/Lexorius/alternative_time.svg)](https://github.com/Lexorius/alternative_time/releases)
[![GitHub Activity](https://img.shields.io/github/commit-activity/y/Lexorius/alternative_time.svg)](https://github.com/Lexorius/alternative_time/commits/main)
[![License](https://img.shields.io/github/license/Lexorius/alternative_time.svg)](LICENSE)

Eine umfassende Home Assistant Integration für alternative Zeitsysteme aus Wissenschaft, Science-Fiction, Geschichte und verschiedenen Kulturen. Von der Sternzeit bis zum Maya-Kalender, vom Unix-Timestamp bis zur thailändischen Zeitrechnung - diese Integration bietet 16 verschiedene Zeitsysteme als Sensoren.

## 🎯 Übersicht

Diese Integration verwandelt Home Assistant in eine universelle Zeituhr mit Unterstützung für:
- 🚀 **Science-Fiction Zeiten** (Star Trek Sternzeit)
- 🌐 **Internet-Standards** (Unix, Swatch Internet Time)
- 🏛️ **Historische Kalender** (Maya, Attisch, Französische Revolution)
- 🎖️ **Militärische Zeitsysteme** (NATO DTG in 3 Varianten)
- 🌏 **Kulturelle Kalender** (Thai, Taiwan)
- 💻 **Technische Formate** (Hexadezimal, Julian Date)

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
4. Folge dem Konfigurationsassistenten
5. Wähle die gewünschten Zeitsysteme aus
6. Klicke auf **Absenden**

### 💡 Mehrere Instanzen

Du kannst beliebig viele Instanzen mit unterschiedlichen Konfigurationen erstellen:
- **Weltzeituhr**: Mehrere Instanzen mit verschiedenen Zeitzonen
- **Thematische Gruppen**: Sci-Fi, Historisch, Militärisch
- **Raum-basiert**: Verschiedene Zeitsysteme für verschiedene Räume

## 🌟 Verfügbare Zeitsysteme

### 🌍 **Zeitzone**
- **Format**: `HH:MM:SS TZ` (z.B. `14:30:45 CEST`)
- **Beschreibung**: Zeigt die aktuelle Zeit in einer beliebigen Zeitzone
- **Verwendung**: Internationale Teams, Reiseplanung, Weltzeituhr
- **Update**: Jede Sekunde

### 🚀 **Sternzeit (Stardate)**
- **Format**: `XXXXX.XX` (z.B. `47634.44`)
- **Beschreibung**: Star Trek TNG-Style Sternzeit basierend auf dem Jahr 2323
- **Besonderheit**: Berechnet nach TNG-Formel mit Tagesbruchteil
- **Update**: Alle 10 Sekunden

### 🌐 **Swatch Internet Time**
- **Format**: `@XXX.XX` (z.B. `@750.00`)
- **Beschreibung**: Ein Tag = 1000 Beats, keine Zeitzonen (BMT)
- **Geschichte**: 1998 von Swatch eingeführt als universelle Internetzeit
- **Update**: Jede Sekunde

### 🔢 **Unix Timestamp**
- **Format**: `XXXXXXXXXX` (z.B. `1735689600`)
- **Beschreibung**: Sekunden seit 1. Januar 1970, 00:00 UTC
- **Verwendung**: Programmierung, Datenbanken, IT-Systeme
- **Update**: Jede Sekunde

### 📅 **Julianisches Datum**
- **Format**: `XXXXXXX.XXXXX` (z.B. `2460000.50000`)
- **Beschreibung**: Kontinuierliche Tageszählung seit 4713 v.Chr.
- **Verwendung**: Astronomie, Wissenschaft, historische Datierung
- **Update**: Jede Minute

### 🔟 **Dezimalzeit**
- **Format**: `H:MM:SS` (z.B. `5:50:00`)
- **Beschreibung**: Französische Revolutionszeit - 10 Stunden/Tag, 100 Min/Std
- **Geschichte**: 1793-1805 in Frankreich offiziell verwendet
- **Update**: Jede Sekunde

### 🔤 **Hexadezimalzeit**
- **Format**: `.XXXX` (z.B. `.8000`)
- **Beschreibung**: Tag in 65536 (0x10000) Teile geteilt
- **Besonderheit**: .0000 = Mitternacht, .8000 = Mittag, .FFFF = 23:59:59
- **Update**: Alle 5 Sekunden

### 🏛️ **Maya-Kalender**
- **Format**: `B.K.T.U.K | TZ TN | HD HM`
- **Beispiel**: `13.0.12.1.15 | 8 Ahau | 3 Pop`
- **Komponenten**:
  - Lange Zählung (Baktun.Katun.Tun.Uinal.Kin)
  - Tzolk'in (260-Tage ritueller Kalender)
  - Haab (365-Tage Zivilkalender)
- **Update**: Stündlich

### 🎖️ **NATO-Zeit (Basis)**
- **Format**: `DDHHMM` (z.B. `151430`)
- **Beschreibung**: Tag + Uhrzeit ohne Zeitzone
- **Verwendung**: Einfache militärische Zeitangabe
- **Update**: Jede Sekunde

### 🌐 **NATO-Zeit mit Zone (DTG)**
- **Format**: `DDHHMM[Z] MON YY` (z.B. `151430Z JAN 25`)
- **Beschreibung**: Vollständige Date-Time Group mit Zeitzone
- **Zeitzonen**: A-Z (außer J), Z=UTC, B=UTC+2 (CEST)
- **Update**: Jede Sekunde

### 🚑 **NATO-Zeit Rettungsdienst**
- **Format**: `DD HHMM MONAT YY` (z.B. `15 1430 JAN 25`)
- **Beschreibung**: Deutsche BOS-Standard Notation
- **Besonderheit**: Mit Leerzeichen, deutsche Monatsabkürzungen
- **Verwendung**: Feuerwehr, Rettungsdienst, THW, Katastrophenschutz
- **Update**: Jede Sekunde

### 🏛️ **Attischer Kalender**
- **Format**: `Tag Period Monat | Archon | Ol.XXX.Y`
- **Beispiel**: `5 ἱσταμένου Hekatombaion | Nikias | Ol.700.2`
- **Komponenten**:
  - Dekaden-System (3×10 Tage/Monat)
  - 12 Lunarmonate
  - Archon (Jahresbeamter)
  - Olympiaden-Zählung
- **Update**: Stündlich

### 🇹🇭 **Suriyakati-Kalender (Thai)**
- **Format**: Thai + Romanisiert
- **Beispiel**: `๒๕ ธันวาคม ๒๕๖๘ | 25 Thanwakhom 2568 BE`
- **Besonderheit**: Buddhistische Ära (BE = CE + 543)
- **Zahlen**: Thai-Ziffern ๐๑๒๓๔๕๖๗๘๙
- **Update**: Stündlich

### 🇹🇼 **Minguo-Kalender (Taiwan)**
- **Format**: Chinesisch + Romanisiert
- **Beispiel**: `民國114年 十二月 二十五日 | Minguo 114/12/25`
- **Besonderheit**: Jahr 1 = 1912 CE (Gründung ROC)
- **Verwendung**: Offizielle Dokumente in Taiwan
- **Update**: Stündlich

## 🎯 Verwendung

### Sensor-Entitäten

Nach der Konfiguration werden folgende Sensoren erstellt (je nach Auswahl):

| Sensor | Entitäts-ID |
|--------|-------------|
| Zeitzone | `sensor.[name]_zeitzone` |
| Sternzeit | `sensor.[name]_sternzeit` |
| Swatch Time | `sensor.[name]_swatch_internet_time` |
| Unix Timestamp | `sensor.[name]_unix_timestamp` |
| Julianisches Datum | `sensor.[name]_julianisches_datum` |
| Dezimalzeit | `sensor.[name]_dezimalzeit` |
| Hexadezimalzeit | `sensor.[name]_hexadezimalzeit` |
| Maya-Kalender | `sensor.[name]_maya_kalender` |
| NATO-Zeit | `sensor.[name]_nato_zeit` |
| NATO DTG | `sensor.[name]_nato_zeit_mit_zone` |
| NATO Rettungsdienst | `sensor.[name]_nato_zeit_rettungsdienst` |
| Attischer Kalender | `sensor.[name]_attischer_kalender` |
| Suriyakati | `sensor.[name]_suriyakati_kalender` |
| Minguo | `sensor.[name]_minguo_kalender` |

## 📊 Dashboard-Beispiele

### Einfache Entitätskarte
```yaml
type: entities
title: Alternative Zeitsysteme
entities:
  - entity: sensor.alternative_time_sternzeit
  - entity: sensor.alternative_time_maya_kalender
  - entity: sensor.alternative_time_nato_zeit_mit_zone
  - entity: sensor.alternative_time_suriyakati_kalender
```

### Weltzeituhr Dashboard
```yaml
type: vertical-stack
cards:
  - type: markdown
    content: |
      ## 🌍 Weltzeiten
      **Sternzeit:** {{ states('sensor.alternative_time_sternzeit') }}
      **Internet Time:** {{ states('sensor.alternative_time_swatch_internet_time') }}
      **Maya:** {{ states('sensor.alternative_time_maya_kalender') }}
      **Athen:** {{ states('sensor.alternative_time_attischer_kalender') }}
      **Thailand:** {{ states('sensor.alternative_time_suriyakati_kalender') }}
      **Taiwan:** {{ states('sensor.alternative_time_minguo_kalender') }}
  
  - type: glance
    entities:
      - entity: sensor.alternative_time_nato_zeit_mit_zone
        name: NATO DTG
      - entity: sensor.alternative_time_unix_timestamp
        name: Unix
      - entity: sensor.alternative_time_dezimalzeit
        name: Dezimal
```

## 🤖 Automatisierungen

### Sternzeit-Ansage
```yaml
automation:
  - alias: "Sternzeit Mittag"
    trigger:
      - platform: time
        at: "12:00:00"
    action:
      - service: tts.google_say
        data:
          entity_id: media_player.wohnzimmer
          message: "Sternzeit {{ states('sensor.alternative_time_sternzeit') }}"
```

### Einsatz-Zeitstempel (Rettungsdienst)
```yaml
automation:
  - alias: "Einsatz Protokoll"
    trigger:
      - platform: state
        entity_id: input_boolean.einsatz_aktiv
        to: 'on'
    action:
      - service: input_text.set_value
        data:
          entity_id: input_text.einsatz_start
          value: "{{ states('sensor.alternative_time_nato_zeit_rettungsdienst') }}"
```

### Maya-Kalender Tageswechsel
```yaml
automation:
  - alias: "Maya Neuer Tag"
    trigger:
      - platform: state
        entity_id: sensor.alternative_time_maya_kalender
    action:
      - service: notify.mobile_app
        data:
          title: "Maya-Kalender"
          message: "Neuer Tag: {{ trigger.to_state.state }}"
```

## 🚀 Performance

Die Integration ist optimiert für minimale Systembelastung:

| Zeitsystem | Update-Intervall | Grund |
|------------|-----------------|-------|
| Zeitzonen, Unix, Swatch | 1 Sekunde | Sekundengenaue Anzeige |
| Hexadezimal | 5 Sekunden | Mittlere Änderungsrate |
| Sternzeit | 10 Sekunden | Langsame Änderung |
| Julian Date | 60 Sekunden | Sehr langsame Änderung |
| Kalender (Maya, Attisch, etc.) | 1 Stunde | Täglicher Wechsel |

## 🐛 Fehlerbehebung

### Integration wird nicht gefunden
```bash
# Prüfe Ordnerstruktur
ls -la /config/custom_components/alternative_time/

# Sollte enthalten:
# __init__.py, manifest.json, config_flow.py, sensor.py, const.py, translations/
```

### Sensoren zeigen "unavailable"
1. Prüfe die Logs: Einstellungen → System → Logs
2. Stelle sicher, dass mindestens ein Zeitsystem aktiviert ist
3. Cache löschen: `find /config -name "__pycache__" -exec rm -rf {} +`
4. Home Assistant neu starten

### "Blocking call" Warnung
Die Integration verwendet asynchrone Operationen. Falls die Warnung auftritt:
```bash
ha core restart
```

## 📈 Version History

### v1.3.0 (Latest)
- ✨ Suriyakati-Kalender (Thai) hinzugefügt
- ✨ Minguo-Kalender (Taiwan/ROC) hinzugefügt
- ✨ Attischer Kalender (Antikes Athen) hinzugefügt
- 📝 Detaillierte Beschreibungen im Config Flow
- 🌏 Erweiterte Unterstützung für asiatische Kalendersysteme

### v1.2.0
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

## 📝 Geplante Features

- [ ] Weitere Sci-Fi Zeitsysteme (Star Wars, Stargate, Doctor Who)
- [ ] Historische Kalender (Römisch, Ägyptisch, Chinesisch)
- [ ] Religiöse Kalender (Islamisch, Jüdisch, Koptisch)
- [ ] Anpassbare Update-Intervalle
- [ ] Zeitkonvertierung zwischen Systemen
- [ ] Grafische Uhren-Cards
- [ ] Export-Funktionen für Kalender

## 🤝 Beitragen

Contributions sind willkommen! 

1. Fork das Repository
2. Erstelle einen Feature Branch (`git checkout -b feature/NeuesZeitsystem`)
3. Committe deine Änderungen (`git commit -m 'Add: Neues Zeitsystem'`)
4. Push zum Branch (`git push origin feature/NeuesZeitsystem`)
5. Öffne einen Pull Request

### Entwicklungsumgebung

```bash
# Repository klonen
git clone https://github.com/Lexorius/alternative_time.git
cd alternative_time

# In Home Assistant custom_components verlinken
ln -s $(pwd)/custom_components/alternative_time /config/custom_components/

# Home Assistant neu starten
ha core restart

# Logs beobachten
tail -f /config/home-assistant.log | grep alternative_time
```

## 📄 Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert - siehe [LICENSE](LICENSE) für Details.

## 🙏 Danksagungen

- **Home Assistant Community** für die großartige Plattform
- **Star Trek** für die Inspiration zur Sternzeit
- **Swatch** für die revolutionäre Internet Beat Time
- **Maya-Kultur** für ihr faszinierendes Kalendersystem
- **NATO/Militär** für standardisierte Zeitnotation
- **Antikes Griechenland** für den präzisen Lunisolarkalender
- **Thailand & Taiwan** für ihre einzigartigen Kalendersysteme
- **Alle Contributor und Tester** die zum Projekt beitragen

## 📧 Support

- **Issues**: [GitHub Issues](https://github.com/Lexorius/alternative_time/issues)
- **Diskussionen**: [GitHub Discussions](https://github.com/Lexorius/alternative_time/discussions)
- **Wiki**: [GitHub Wiki](https://github.com/Lexorius/alternative_time/wiki)

## 🌐 Ressourcen

### Weiterführende Links
- [Star Trek Stardate Calculator](http://trekguide.com/Stardates.htm)
- [Swatch Internet Time](https://www.swatch.com/en-us/internet-time.html)
- [Maya Calendar Converter](https://maya.nmai.si.edu/calendar/maya-calendar-converter)
- [NATO Date Time Group](https://en.wikipedia.org/wiki/Date-time_group)
- [Buddhist Era Calendar](https://en.wikipedia.org/wiki/Buddhist_calendar)
- [Minguo Calendar](https://en.wikipedia.org/wiki/Minguo_calendar)

### Technische Dokumentation
- [Home Assistant Developer Docs](https://developers.home-assistant.io/)
- [HACS Integration Guide](https://hacs.xyz/docs/develop/start)
- [Python datetime Documentation](https://docs.python.org/3/library/datetime.html)

---

**Made with ❤️ by [Lexorius](https://github.com/Lexorius)**

*"Zeit ist eine Illusion. Mittagszeit doppelt so." - Douglas Adams*