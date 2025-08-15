# Alternative Zeitsysteme für Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/Lexorius/alternative_time.svg)](https://github.com/Lexorius/alternative_time/releases)
[![GitHub Activity](https://img.shields.io/github/commit-activity/y/Lexorius/alternative_time.svg)](https://github.com/Lexorius/alternative_time/commits/main)
[![License](https://img.shields.io/github/license/Lexorius/alternative_time.svg)](LICENSE)

Eine umfassende Home Assistant Integration für alternative Zeitsysteme aus Wissenschaft, Science-Fiction, Fantasy, Geschichte und verschiedenen Kulturen. Von der Sternzeit bis zum Maya-Kalender, vom Auenland bis nach Rivendell, von Unix-Timestamp bis zur Mars-Zeit - diese Integration bietet **21 verschiedene Zeitsysteme** als Sensoren.

## 🎯 Übersicht

Diese Integration verwandelt Home Assistant in eine universelle Zeituhr mit Unterstützung für:
- 🚀 **Science-Fiction Zeiten** (Star Trek Sternzeit, EVE Online)
- 🧙 **Fantasy-Kalender** (Auenland/Hobbits, Rivendell/Elben)
- 🔴 **Mars-Zeitsysteme** (Darischer Kalender, Mars-Zeitzonen)
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
- **Thematische Gruppen**: Sci-Fi, Fantasy, Historisch, Militärisch
- **Raum-basiert**: Verschiedene Zeitsysteme für verschiedene Räume

## 🌟 Verfügbare Zeitsysteme

### 🌍 **Zeitzone**
- **Format**: `HH:MM:SS TZ` (z.B. `14:30:45 CEST`)
- **Beschreibung**: Zeigt die aktuelle Zeit in einer beliebigen Erdzeit-Zone
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

### 🌍 **NATO-Zeit mit Zone (DTG)**
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

### 🚀 **Darischer Kalender (Mars)**
- **Format**: `Sol Monat Jahr | Wochentag | Jahreszeit`
- **Beispiel**: `15 Gemini 217 | Sol Martis | Summer`
- **Besonderheiten**:
  - 24 Monate mit je 27-28 Sols
  - 668 Sols pro Mars-Jahr
  - 7-Sol-Woche mit lateinischen Namen
- **Update**: Stündlich

### 🔴 **Mars-Zeit mit Zeitzone**
- **Format**: `HH:MM:SS Location | Sol X/MYY | ☉/☽`
- **Beispiel**: `14:25:30 Olympus Mons | Sol 234/MY36 | ☉ Tag`
- **24 Mars-Zeitzonen**: 
  - MTC+0 (Airy-0) bis MTC+12
  - MTC-1 bis MTC-12
  - Benannt nach Mars-Landmarken
- **Features**:
  - Sol-Zeit (24:39:35 Erdzeit)
  - Tag/Nacht-Indikator
  - Mars-Jahr und Sol-Nummer
- **Update**: Alle 30 Sekunden

### 🚀 **EVE Online Zeit**
- **Format**: `YC XXX.MM.DD HH:MM:SS`
- **Beispiel**: `YC 127.03.15 14:30:45`
- **Beschreibung**: New Eden Standard Time aus dem EVE Online Universum
- **Besonderheit**: Yoiul Conference (YC) Kalender, UTC-basiert
- **Geschichte**: YC 105 = 2003 (EVE Launch)
- **Update**: Jede Sekunde

### 🍃 **Auenland-Kalender (Shire Reckoning)**
- **Format**: `S.R. Jahr, Tag Monat (Wochentag) | Mahlzeit`
- **Beispiel**: `S.R. 1445, 22 Halimath (Highdei) | 🍖 Luncheon`
- **Besonderheiten**:
  - 12 Monate à 30 Tage
  - Spezielle Tage (Yule, Lithe)
  - 7 Hobbit-Mahlzeiten täglich
  - Wichtige Ereignisse (Bilbos Geburtstag)
- **Mahlzeiten**: First Breakfast, Second Breakfast, Elevenses, Luncheon, Afternoon Tea, Dinner, Supper
- **Update**: Stündlich

### 🧝 **Kalender von Imladris (Rivendell)**
- **Format**: `F.A. Jahr, Jahreszeit Tag (Wochentag) | Tageszeit`
- **Beispiel**: `F.A. 6025, Tuilë 22 (Elenya) | 🌞 Ára`
- **Besonderheiten**:
  - 6 Jahreszeiten statt Monate
  - 6-Tage-Woche
  - Elbische Tagesnamen
  - Spezielle Tage (Yestarë, Loëndë, Mettarë)
- **Jahreszeiten**: Tuilë (Frühling), Lairë (Sommer), Yávië (Herbst), Quellë (Schwinden), Hrívë (Winter), Coirë (Erwachen)
- **Update**: Stündlich

## 🎯 Verwendung

### Sensor-Entitäten

Nach der Konfiguration werden folgende Sensoren erstellt (je nach Auswahl):

| Sensor | Entitäts-ID |
|--------|-------------|
| Zeitzone | `sensor.[name]_zeitzone` |
| Sternzeit | `sensor.[name]_stardate` |
| Swatch Time | `sensor.[name]_swatch` |
| Unix Timestamp | `sensor.[name]_unix` |
| Julianisches Datum | `sensor.[name]_julian` |
| Dezimalzeit | `sensor.[name]_decimal` |
| Hexadezimalzeit | `sensor.[name]_hexadecimal` |
| Maya-Kalender | `sensor.[name]_maya_calendar` |
| NATO-Zeit | `sensor.[name]_nato_time` |
| NATO DTG | `sensor.[name]_nato_time_with_zone` |
| NATO Rettungsdienst | `sensor.[name]_nato_rescue_time` |
| Attischer Kalender | `sensor.[name]_attic_calendar` |
| Suriyakati | `sensor.[name]_suriyakati_calendar` |
| Minguo | `sensor.[name]_minguo_calendar` |
| Darischer Kalender | `sensor.[name]_darian_calendar` |
| Mars-Zeit | `sensor.[name]_mars_time` |
| EVE Online | `sensor.[name]_eve_online` |
| Auenland | `sensor.[name]_shire` |
| Rivendell | `sensor.[name]_rivendell` |

## 📊 Dashboard-Beispiele

### Einfache Entitätskarte
```yaml
type: entities
title: Alternative Zeitsysteme
entities:
  - entity: sensor.alternative_time_stardate
  - entity: sensor.alternative_time_maya_calendar
  - entity: sensor.alternative_time_shire
  - entity: sensor.alternative_time_eve_online
```

### Fantasy-Zeiten Dashboard
```yaml
type: vertical-stack
cards:
  - type: markdown
    content: |
      ## 🧙 Mittelerde-Zeiten
      **Auenland:** {{ states('sensor.alternative_time_shire') }}
      **Rivendell:** {{ states('sensor.alternative_time_rivendell') }}
      
  - type: entities
    title: Fantasy-Kalender
    entities:
      - entity: sensor.alternative_time_shire
        name: Hobbit-Zeit
      - entity: sensor.alternative_time_rivendell
        name: Elben-Zeit
```

### Sci-Fi Dashboard
```yaml
type: vertical-stack
cards:
  - type: markdown
    content: |
      ## 🚀 Science-Fiction Zeiten
      **Sternzeit:** {{ states('sensor.alternative_time_stardate') }}
      **EVE Online:** {{ states('sensor.alternative_time_eve_online') }}
      **Mars-Zeit:** {{ states('sensor.alternative_time_mars_time') }}
      **Darischer Kalender:** {{ states('sensor.alternative_time_darian_calendar') }}
  
  - type: glance
    entities:
      - entity: sensor.alternative_time_stardate
        name: Star Trek
      - entity: sensor.alternative_time_eve_online
        name: New Eden
      - entity: sensor.alternative_time_mars_time
        name: Mars
```

### Weltzeituhr Dashboard
```yaml
type: vertical-stack
cards:
  - type: markdown
    content: |
      ## 🌍 Weltzeiten
      **Sternzeit:** {{ states('sensor.alternative_time_stardate') }}
      **Internet Time:** {{ states('sensor.alternative_time_swatch') }}
      **Maya:** {{ states('sensor.alternative_time_maya_calendar') }}
      **Athen:** {{ states('sensor.alternative_time_attic_calendar') }}
      **Thailand:** {{ states('sensor.alternative_time_suriyakati_calendar') }}
      **Taiwan:** {{ states('sensor.alternative_time_minguo_calendar') }}
      **Auenland:** {{ states('sensor.alternative_time_shire') }}
      **Rivendell:** {{ states('sensor.alternative_time_rivendell') }}
      **New Eden:** {{ states('sensor.alternative_time_eve_online') }}
      **Mars:** {{ states('sensor.alternative_time_mars_time') }}
```

## 🤖 Automatisierungen

### Hobbit-Mahlzeit-Erinnerung
```yaml
automation:
  - alias: "Zweites Frühstück"
    trigger:
      - platform: time
        at: "09:00:00"
    condition:
      - condition: state
        entity_id: sensor.alternative_time_shire
        state: 'Second Breakfast'
    action:
      - service: tts.google_say
        data:
          entity_id: media_player.küche
          message: "Zeit für das zweite Frühstück! Was ist mit Elevenses?"
```

### Elbisches Neujahr
```yaml
automation:
  - alias: "Yestarë Feier"
    trigger:
      - platform: template
        value_template: >
          {{ 'Yestarë' in states('sensor.alternative_time_rivendell') }}
    action:
      - service: notify.mobile_app
        data:
          title: "🧝 Elbisches Neujahr"
          message: "Yestarë ist angebrochen! Ein neues Jahr in Rivendell beginnt."
```

### EVE Online Downtime Warnung
```yaml
automation:
  - alias: "EVE Downtime"
    trigger:
      - platform: time
        at: "10:45:00"  # 15 Min vor täglicher Downtime
    action:
      - service: notify.mobile_app
        data:
          title: "⚠️ EVE Online"
          message: "Tägliche Downtime in 15 Minuten!"
```

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
          message: "Sternzeit {{ states('sensor.alternative_time_stardate') }}"
```

## 🧙 Fantasy-Kalender Details

### 🍃 Auenland-Kalender (Shire Reckoning)

Der Kalender der Hobbits aus J.R.R. Tolkiens Mittelerde:

#### Struktur:
- **12 Monate** mit je 30 Tagen
- **5-6 Sondertage** außerhalb der Monate (Yule, Lithe)
- **S.R. 1** = Gründung des Auenlandes
- **S.R. 1420** = Ende des Ringkrieges

#### Hobbit-Mahlzeiten (täglich):
1. **First Breakfast** (6-8 Uhr) 🍳
2. **Second Breakfast** (8-11 Uhr) 🥐
3. **Elevenses** (11-13 Uhr) 🍽️
4. **Luncheon** (13-15 Uhr) 🍖
5. **Afternoon Tea** (15-17 Uhr) ☕
6. **Dinner** (17-19 Uhr) 🍰
7. **Supper** (19-21 Uhr) 🍻

#### Wichtige Ereignisse:
- **22. Halimath**: Bilbo & Frodos Geburtstag
- **2. Yule**: Neujahr
- **Mid-year's Day**: Mittsommerfest
- **1. Mai**: Maifest

### 🧝 Kalender von Imladris (Rivendell)

Der elbische Kalender aus Rivendell:

#### Struktur:
- **6 Jahreszeiten** statt Monate
- **6-Tage-Woche** (enquië)
- **360 Tage** + Sondertage
- **F.A.** = Fourth Age (Viertes Zeitalter)

#### Jahreszeiten (jeweils 54-72 Tage):
1. **Tuilë** 🌸 - Frühling (54 Tage)
2. **Lairë** ☀️ - Sommer (72 Tage)
3. **Yávië** 🍂 - Herbst (54 Tage)
4. **Quellë** 🍁 - Schwinden (54 Tage)
5. **Hrívë** ❄️ - Winter (72 Tage)
6. **Coirë** 🌱 - Erwachen (54 Tage)

#### Elbische Tageszeiten:
- **Tindómë** 🌅 - Dämmerung (3-6 Uhr)
- **Anarórë** 🌄 - Sonnenaufgang (6-9 Uhr)
- **Ára** 🌞 - Morgen (9-12 Uhr)
- **Endë** ☀️ - Mittag (12-15 Uhr)
- **Undómë** 🌤️ - Nachmittag (15-18 Uhr)
- **Andúnë** 🌇 - Sonnenuntergang (18-21 Uhr)
- **Lómë** 🌙 - Nacht (21-24 Uhr)
- **Fui** ⭐ - Tiefe Nacht (0-3 Uhr)

## 🚀 Science-Fiction Details

### 🌌 EVE Online Zeit

New Eden Standard Time aus dem EVE Online Universum:

#### YC (Yoiul Conference) Kalender:
- **YC 0** = 23236 AD (Spielhintergrund)
- **YC 105** = 2003 (EVE Launch)
- **Format**: YC Jahr.Monat.Tag Stunde:Minute:Sekunde
- **Zeitzone**: Immer UTC (keine Zeitzonen in New Eden)

#### Wichtige EVE-Ereignisse:
- **Tägliche Downtime**: 11:00-11:15 UTC
- **Jita Handelszeiten**: Rund um die Uhr
- **Fleet Operations**: Primetime 19:00-23:00 UTC

## 🚀 Performance

Die Integration ist optimiert für minimale Systembelastung:

| Zeitsystem | Update-Intervall | Grund |
|------------|-----------------|-------|
| Zeitzonen, Unix, Swatch, EVE | 1 Sekunde | Sekundengenaue Anzeige |
| Hexadezimal | 5 Sekunden | Mittlere Änderungsrate |
| Sternzeit | 10 Sekunden | Langsame Änderung |
| Mars-Zeit | 30 Sekunden | Sol-Zeit Präzision |
| Julian Date | 60 Sekunden | Sehr langsame Änderung |
| Kalender (Maya, Attisch, etc.) | 1 Stunde | Täglicher Wechsel |
| Fantasy-Kalender | 1 Stunde | Ereignis-basiert |

## 🛠 Fehlerbehebung

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

### v1.5.0 (Latest) 🆕
- ✨ EVE Online Zeit (New Eden Standard Time) hinzugefügt
- ✨ Auenland-Kalender (Shire Reckoning) mit 7 Hobbit-Mahlzeiten
- ✨ Kalender von Imladris (Rivendell) mit elbischen Jahreszeiten
- 🧙 Komplette Mittelerde-Zeitunterstützung
- 🚀 Erweiterte Sci-Fi-Funktionen
- 📚 21 Zeitsysteme insgesamt

### v1.4.0
- ✨ Darischer Kalender (Mars) hinzugefügt
- ✨ Mars-Zeit mit 24 wählbaren Zeitzonen
- 🔴 Vollständige Mars-Zeitsystem-Unterstützung
- 🚀 Bereit für Mars-Kolonisation

### v1.3.0
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
- **J.R.R. Tolkien** für die wundervollen Mittelerde-Kalender
- **CCP Games** für EVE Online und New Eden
- **Swatch** für die revolutionäre Internet Beat Time
- **Maya-Kultur** für ihr faszinierendes Kalendersystem
- **NATO/Militär** für standardisierte Zeitnotation
- **Antikes Griechenland** für den präzisen Lunisolarkalender
- **Thailand & Taiwan** für ihre einzigartigen Kalendersysteme
- **Thomas Gangale** für den Darischen Mars-Kalender
- **NASA/ESA** für Mars-Missionen und Zeitzonenkonzepte
- **Alle Contributor und Tester** die zum Projekt beitragen

## 🔧 Support

- **Issues**: [GitHub Issues](https://github.com/Lexorius/alternative_time/issues)
- **Diskussionen**: [GitHub Discussions](https://github.com/Lexorius/alternative_time/discussions)
- **Wiki**: [GitHub Wiki](https://github.com/Lexorius/alternative_time/wiki)

## 🌐 Ressourcen

### Weiterführende Links
- [Star Trek Stardate Calculator](http://trekguide.com/Stardates.htm)
- [Tolkien Gateway - Shire Calendar](http://tolkiengateway.net/wiki/Shire_Calendar)
- [Tolkien Gateway - Calendar of Imladris](http://tolkiengateway.net/wiki/Calendar_of_Imladris)
- [EVE Online Time](https://wiki.eveuniversity.org/Time)
- [Swatch Internet Time](https://www.swatch.com/en-us/internet-time.html)
- [Maya Calendar Converter](https://maya.nmai.si.edu/calendar/maya-calendar-converter)
- [NATO Date Time Group](https://en.wikipedia.org/wiki/Date-time_group)
- [Buddhist Era Calendar](https://en.wikipedia.org/wiki/Buddhist_calendar)
- [Minguo Calendar](https://en.wikipedia.org/wiki/Minguo_calendar)
- [Darian Calendar](https://en.wikipedia.org/wiki/Darian_calendar)
- [Mars24 Sunclock](https://mars.nasa.gov/mars24/)

---

**Made with ❤️ by [Lexorius](https://github.com/Lexorius)**

*"Zeit ist eine Illusion. Mittagszeit doppelt so. Mars-Zeit dreifach. Hobbit-Mahlzeiten sind allerdings sehr real." - Frei nach Douglas Adams*