# Alternative Zeitsysteme für Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/Lexorius/alternative_time.svg)](https://github.com/Lexorius/alternative_time/releases)
[![GitHub Activity](https://img.shields.io/github/commit-activity/y/Lexorius/alternative_time.svg)](https://github.com/Lexorius/alternative_time/commits/main)
[![License](https://img.shields.io/github/license/Lexorius/alternative_time.svg)](LICENSE)

Eine umfassende Home Assistant Integration für alternative Zeitsysteme aus Wissenschaft, Science-Fiction, Fantasy, Geschichte und verschiedenen Kulturen. Von der Sternzeit bis zum Maya-Kalender, vom Auenland bis zur Scheibenwelt, von Tamriel bis ins alte Ägypten - diese Integration bietet 24 verschiedene Zeitsysteme als Sensoren.

## 🎯 Übersicht

Diese Integration verwandelt Home Assistant in eine universelle Zeituhr mit Unterstützung für:
- 🚀 **Science-Fiction Zeiten** (Star Trek Sternzeit, EVE Online)
- 🧙 **Fantasy-Kalender** (Tolkien, Elder Scrolls, Discworld)
- 🏺 **Historische Kalender** (Maya, Attisch, Ägyptisch, Französische Revolution)
- 🔴 **Mars-Zeitsysteme** (Darischer Kalender, Mars-Zeitzonen)
- 🌐 **Internet-Standards** (Unix, Swatch Internet Time)
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
- **Beschreibung**: New Eden Standard Time (NEST)
- **Besonderheiten**:
  - YC = Yoiul Conference Jahr
  - Verwendet UTC als Basis
  - YC 105 = 2003 (EVE Launch)
- **Update**: Jede Sekunde

### 🍄 **Auenland-Kalender (Shire Reckoning)**
- **Format**: `S.R. Jahr, Tag Monat (Wochentag) | Mahlzeit`
- **Beispiel**: `S.R. 1445, 22 Halimath (Highdei) | 🍖 Luncheon`
- **Besonderheiten**:
  - 12 Monate à 30 Tage
  - Spezielle Tage (Yule, Lithe)
  - 7 Hobbit-Mahlzeiten täglich
  - Wichtige Ereignisse (Bilbos Geburtstag)
- **Monate**: Afteryule, Solmath, Rethe, Astron, Thrimidge, Forelithe, Afterlithe, Wedmath, Halimath, Winterfilth, Blotmath, Foreyule
- **Update**: Stündlich

### 🍃 **Kalender von Imladris (Elben)**
- **Format**: `F.A. Jahr, Jahreszeit Tag (Wochentag) | Tageszeit`
- **Beispiel**: `F.A. 6025, Tuilë 22 (Elenya) | 🌞 Ára`
- **Besonderheiten**:
  - 6 Jahreszeiten statt Monate
  - 6-Tage-Woche
  - Spezielle Tage (Yestarë, Loëndë, Mettarë)
  - Elbische Tageszeiten
- **Jahreszeiten**: Tuilë (Frühling), Lairë (Sommer), Yávië (Herbst), Quellë (Schwinden), Hrívë (Winter), Coirë (Erwachen)
- **Update**: Stündlich

### 🎮 **Tamriel-Kalender (Elder Scrolls)**
- **Format**: `4E Jahr, Tag Monat (Wochentag) | Zeit | Segen | Ereignis`
- **Beispiel**: `4E 201, 17 Last Seed (Fredas) | Dusk 🌆 | Blessing: Talos | 🌕🌗`
- **Besonderheiten**:
  - 12 Monate mit einzigartigen Namen
  - 8-Tage-Woche mit Octeday
  - Göttliche Segnungen (9 Divines)
  - Daedric Princes Einfluss
  - Zwei Monde (Masser & Secunda)
  - Feiertage und Festivals
- **Monate**: Morning Star, Sun's Dawn, First Seed, Rain's Hand, Second Seed, Midyear, Sun's Height, Last Seed, Hearthfire, Frostfall, Sun's Dusk, Evening Star
- **Update**: Stündlich

### 🏺 **Ägyptischer Kalender**
- **Format**: `Dynastie Jahr, Hieroglyphen Tag Monat (Jahreszeit) | Dekan | Stunde | Gott | Nil`
- **Beispiel**: `Dynasty 1 Year 25, 𓏤𓏨 15 Thoth (Akhet) | Second Decan | ☀️ Sixth Hour | Thoth | 🌊`
- **Besonderheiten**:
  - 3 Jahreszeiten (Akhet, Peret, Shemu)
  - 12 Monate à 30 Tage
  - 5 Epagomenale Tage
  - Dekaden (10-Tage-Wochen)
  - Hieroglyphen-Zahlen
  - 12 Tag- und 12 Nachtstunden
  - Nil-Überschwemmungszyklus
- **Jahreszeiten**: Akhet (Überschwemmung), Peret (Aussaat), Shemu (Ernte)
- **Update**: Stündlich

### 🐢 **Scheibenwelt-Kalender (Discworld)**
- **Format**: `Century Jahr, Tag Monat (Wochentag) | Zeit | Ort | Gilde | Ereignis`
- **Beispiel**: `Century of the Anchovy, UC 25, 32 Offle (Octeday) | 🌙 Dead of Night | 📍 The Shades | Thieves' Guild`
- **Besonderheiten**:
  - 13 Monate mit Pratchett-Humor
  - 8-Tage-Woche mit Octeday
  - Unmögliche Tage (32. April)
  - Gilden von Ankh-Morpork
  - Tod-Zitate um Mitternacht
  - L-Space Bibliotheksverbindungen
  - Stadtviertel-Rotation
- **Monate**: Ick, Offle, February, March, April, May, June, Grune, August, Spune, Sektober, Ember, December
- **Update**: Stündlich

## 🎯 Verwendung

### Sensor-Entitäten

Nach der Konfiguration werden folgende Sensoren erstellt (je nach Auswahl):

| Sensor | Entitäts-ID |
|--------|-------------|
| Zeitzone | `sensor.[name]_timezone` |
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
| Imladris | `sensor.[name]_rivendell` |
| Tamriel | `sensor.[name]_tamriel` |
| Ägyptisch | `sensor.[name]_egyptian` |
| Scheibenwelt | `sensor.[name]_discworld` |

## 📊 Dashboard-Beispiele

### Fantasy-Welten Dashboard
```yaml
type: vertical-stack
cards:
  - type: markdown
    content: |
      ## 🧙 Fantasy & Gaming Welten
      **Auenland:** {{ states('sensor.alternative_time_shire') }}
      **Imladris:** {{ states('sensor.alternative_time_rivendell') }}
      **Tamriel:** {{ states('sensor.alternative_time_tamriel') }}
      **Scheibenwelt:** {{ states('sensor.alternative_time_discworld') }}
      **EVE Online:** {{ states('sensor.alternative_time_eve_online') }}
  
  - type: entities
    title: Fantasy & Sci-Fi Zeiten
    entities:
      - entity: sensor.alternative_time_shire
        name: Hobbit Zeit
      - entity: sensor.alternative_time_rivendell
        name: Elben Zeit
      - entity: sensor.alternative_time_tamriel
        name: Elder Scrolls
      - entity: sensor.alternative_time_discworld
        name: Scheibenwelt
      - entity: sensor.alternative_time_eve_online
        name: New Eden Zeit
```

### Historische Kalender Dashboard
```yaml
type: vertical-stack
cards:
  - type: markdown
    content: |
      ## 🏺 Historische Zeitsysteme
      **Ägypten:** {{ states('sensor.alternative_time_egyptian') }}
      **Maya:** {{ states('sensor.alternative_time_maya_calendar') }}
      **Athen:** {{ states('sensor.alternative_time_attic_calendar') }}
      
  - type: entities
    title: Antike Kalender
    entities:
      - entity: sensor.alternative_time_egyptian
        name: Ägyptischer Kalender
      - entity: sensor.alternative_time_maya_calendar
        name: Maya Kalender
      - entity: sensor.alternative_time_attic_calendar
        name: Attischer Kalender
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
      **Mars:** {{ states('sensor.alternative_time_mars_time') }}
      **Auenland:** {{ states('sensor.alternative_time_shire') }}
      **Imladris:** {{ states('sensor.alternative_time_rivendell') }}
  
  - type: glance
    entities:
      - entity: sensor.alternative_time_nato_time_with_zone
        name: NATO DTG
      - entity: sensor.alternative_time_unix
        name: Unix
      - entity: sensor.alternative_time_eve_online
        name: EVE
```

### Mars-Mission Dashboard
```yaml
type: vertical-stack
cards:
  - type: markdown
    content: |
      ## 🔴 Mars Mission Control
      
      **Mars-Zeit:** {{ states('sensor.alternative_time_mars_time') }}
      **Darischer Kalender:** {{ states('sensor.alternative_time_darian_calendar') }}
      
  - type: entities
    title: Mars-Zeitzonen
    entities:
      - entity: sensor.alternative_time_mars_time
        name: Aktuelle Mars-Zeit
      - entity: sensor.alternative_time_darian_calendar
        name: Mars-Datum
```

## 🤖 Automatisierungen

### Elder Scrolls Feiertag
```yaml
automation:
  - alias: "Tamriel New Life Festival"
    trigger:
      - platform: template
        value_template: >
          {{ 'New Life Festival' in states('sensor.alternative_time_tamriel') }}
    action:
      - service: notify.mobile_app
        data:
          title: "🎮 Tamriel Feiertag"
          message: "Das New Life Festival beginnt in Tamriel!"
```

### Ägyptische Epagomenale Tage
```yaml
automation:
  - alias: "Geburtstag der Götter"
    trigger:
      - platform: template
        value_template: >
          {{ 'Birthday of' in states('sensor.alternative_time_egyptian') }}
    action:
      - service: notify.mobile_app
        data:
          title: "🏺 Ägyptischer Kalender"
          message: "{{ states('sensor.alternative_time_egyptian') }}"
```

### Scheibenwelt Tod-Zitat
```yaml
automation:
  - alias: "Death Says"
    trigger:
      - platform: time
        at: "00:00:00"
    condition:
      - condition: template
        value_template: "{{ states('sensor.alternative_time_discworld') != 'unknown' }}"
    action:
      - service: tts.google_say
        data:
          entity_id: media_player.schlafzimmer
          message: "Tod sagt: ES IST KEINE GERECHTIGKEIT. ES GIBT NUR MICH."
```

### EVE Online Tägliche Aufgaben
```yaml
automation:
  - alias: "EVE Daily Reset"
    trigger:
      - platform: template
        value_template: >
          {{ '11:00:00' in states('sensor.alternative_time_eve_online') }}
    action:
      - service: notify.mobile_app
        data:
          title: "🚀 EVE Online"
          message: "Daily tasks haben resettet!"
```

### Elbisches Neujahr
```yaml
automation:
  - alias: "Yestarë - Elbisches Neujahr"
    trigger:
      - platform: template
        value_template: >
          {{ 'Yestarë' in states('sensor.alternative_time_rivendell') }}
    action:
      - service: notify.mobile_app
        data:
          title: "🍃 Elbisches Neujahr"
          message: "Die Elben feiern Yestarë - ein neues Jahr beginnt in Mittelerde!"
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

### Maya-Kalender Tageswechsel
```yaml
automation:
  - alias: "Maya Neuer Tag"
    trigger:
      - platform: state
        entity_id: sensor.alternative_time_maya_calendar
    action:
      - service: notify.mobile_app
        data:
          title: "Maya-Kalender"
          message: "Neuer Tag: {{ trigger.to_state.state }}"
```

## 🎮 Elder Scrolls Kalendersystem

### Tamriel-Kalender
Der Kalender von Tamriel aus der Elder Scrolls Spielreihe:

#### Die 12 Monate:
1. **Morning Star** (Januar) ❄️
2. **Sun's Dawn** (Februar) 🌅
3. **First Seed** (März) 🌱
4. **Rain's Hand** (April) 🌧️
5. **Second Seed** (Mai) 🌿
6. **Midyear** (Juni) ☀️
7. **Sun's Height** (Juli) 🌞
8. **Last Seed** (August) 🌾
9. **Hearthfire** (September) 🔥
10. **Frostfall** (Oktober) 🍂
11. **Sun's Dusk** (November) 🌆
12. **Evening Star** (Dezember) ⭐

#### Features:
- **8-Tage-Woche** mit Octeday als achtem Tag
- **Göttliche Segnungen** der 9 Divines
- **Daedric Princes** Einfluss an bestimmten Tagen
- **Zwei Monde**: Masser und Secunda mit unterschiedlichen Phasen
- **Viele Feiertage**: New Life Festival, Witches Festival, Warriors Festival

## 🏺 Altägyptisches Kalendersystem

### Ägyptischer Kalender
Der Kalender des alten Ägyptens mit seinen einzigartigen Features:

#### Die 3 Jahreszeiten:
- **Akhet** (Überschwemmung) 🌊 - 4 Monate
- **Peret** (Aussaat) 🌱 - 4 Monate
- **Shemu** (Ernte) ☀️ - 4 Monate

#### Features:
- **365 Tage**: 12 Monate à 30 Tage + 5 Epagomenale Tage
- **Dekaden**: 10-Tage-Wochen
- **Hieroglyphen-Zahlen**: 𓏤𓏥𓏦𓏧𓏨
- **12 Tag- und 12 Nachtstunden**
- **Götter-Patronate** für jeden Monat
- **Nil-Status** abhängig von der Jahreszeit
- **Epagomenale Tage**: Geburtstage von Osiris, Horus, Set, Isis, Nephthys

## 🐢 Scheibenwelt-Kalendersystem

### Discworld Kalender (Terry Pratchett)
Der humorvolle Kalender der Scheibenwelt:

#### Die 13 Monate:
1. **Ick** ❄️
2. **Offle** ❄️
3. **February** 🌨️ (ja, wirklich February!)
4. **March** 🌬️
5. **April** 🌧️
6. **May** 🌸
7. **June** ☀️
8. **Grune** 🌿
9. **August** 🌞
10. **Spune** 🍂
11. **Sektober** 🍺 (Trinkmonat!)
12. **Ember** 🔥
13. **December** ⭐

#### Features:
- **8-Tage-Woche** mit Octeday
- **Unmögliche Tage**: 32. April und 32. Dezember
- **Gilden von Ankh-Morpork**: Täglicher Einfluss verschiedener Gilden
- **Tod-Zitate** um Mitternacht
- **L-Space**: Bibliotheksverbindungen um 03:33 Uhr
- **Stadtviertel**: The Shades, Unseen University, Patrician's Palace
- **Century of the Anchovy**: Aktuelle Ära

### Tod's beste Zitate:
- "ES GIBT KEINE GERECHTIGKEIT. ES GIBT NUR MICH."
- "ICH KÖNNTE EINEN CURRY ERMORDEN."
- "KATZEN. KATZEN SIND NETT."
- "QUIETSCH." (Tod der Ratten)

## 🚀 EVE Online Zeitsystem

### New Eden Standard Time (NEST)
EVE Online verwendet ein eigenes Kalendersystem:

- **YC** = Yoiul Conference (Jahr)
- **Basis**: UTC Erdzeit
- **Epoche**: YC 0 = 23236 AD
- **Spielstart**: YC 105 = 2003
- **Format**: YC XXX.MM.DD HH:MM:SS

Wichtige EVE-Zeiten:
- **11:00 UTC**: Daily Downtime & Reset
- **Jita Time**: Haupthandelszeit
- **Fleet Ops**: Meist 19:00-23:00 UTC

## 🚀 Performance

Die Integration ist optimiert für minimale Systembelastung:

| Zeitsystem | Update-Intervall | Grund |
|------------|-----------------|-------|
| Zeitzonen, Unix, Swatch, EVE | 1 Sekunde | Sekundengenaue Anzeige |
| Hexadezimal | 5 Sekunden | Mittlere Änderungsrate |
| Sternzeit | 10 Sekunden | Langsame Änderung |
| Julian Date | 60 Sekunden | Sehr langsame Änderung |
| Kalender (Maya, Attisch, etc.) | 1 Stunde | Täglicher Wechsel |
| Mars-Zeit | 30 Sekunden | Sol-Zeit Präzision |
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

### v1.6.0 (Latest)
- ✨ Tamriel-Kalender (Elder Scrolls) hinzugefügt
- ✨ Ägyptischer Kalender hinzugefügt
- ✨ Scheibenwelt-Kalender (Discworld) hinzugefügt
- 🎮 Gaming-Welten erweitert
- 🏺 Historische Kalender erweitert
- 🐢 Terry Pratchett's Humor integriert
- 💀 Tod-Zitate und L-Space Features

### v1.5.0
- ✨ EVE Online Zeit (New Eden Standard Time) hinzugefügt
- ✨ Auenland-Kalender (Shire Reckoning) hinzugefügt
- ✨ Kalender von Imladris (Elben) hinzugefügt
- 🧙 Komplette Tolkien-Zeitsysteme
- 🚀 Sci-Fi Erweiterung mit EVE Online
- 🍄 7 Hobbit-Mahlzeiten Integration
- 🍃 6 Elbische Jahreszeiten

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

## 📝 Geplante Features

- [ ] Weitere Sci-Fi Zeitsysteme (Star Wars, Stargate, Doctor Who, The Expanse)
- [ ] Historische Kalender (Römisch, Ägyptisch, Chinesisch, Aztekisch)
- [ ] Religiöse Kalender (Islamisch, Jüdisch, Koptisch, Hindu)
- [ ] Weitere Fantasy-Kalender (Game of Thrones, Warhammer, D&D)
- [ ] Weitere Mars-Features (Phobos/Deimos Orbits, Erdzeit-Konverter)
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
- **J.R.R. Tolkien** für die detaillierten Kalendersysteme von Mittelerde
- **Bethesda Game Studios** für The Elder Scrolls und Tamriel
- **Terry Pratchett** für die Scheibenwelt und ihren einzigartigen Humor
- **Alte Ägypter** für einen der ersten präzisen Kalender der Menschheit
- **CCP Games** für EVE Online und das New Eden Universum
- **Star Trek** für die Inspiration zur Sternzeit
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
- [Swatch Internet Time](https://www.swatch.com/en-us/internet-time.html)
- [Maya Calendar Converter](https://maya.nmai.si.edu/calendar/maya-calendar-converter)
- [NATO Date Time Group](https://en.wikipedia.org/wiki/Date-time_group)
- [Buddhist Era Calendar](https://en.wikipedia.org/wiki/Buddhist_calendar)
- [Minguo Calendar](https://en.wikipedia.org/wiki/Minguo_calendar)
- [Darian Calendar](https://en.wikipedia.org/wiki/Darian_calendar)
- [Mars24 Sunclock](https://mars.nasa.gov/mars24/)
- [Mars Time Zones](https://marsclock.com/)
- [Tolkien Gateway - Shire Calendar](http://tolkiengateway.net/wiki/Shire_Calendar)
- [Encyclopedia of Arda - Calendar of Imladris](https://www.glyphweb.com/arda/c/calendarofimladris.html)
- [EVE Online Time](https://wiki.eveuniversity.org/Time)

---

**Made with ❤️ by [Lexorius](https://github.com/Lexorius)**

*"Zeit ist eine Illusion. Mittagszeit doppelt so. Zweites Frühstück dreifach. Octeday vierfach." - Frei nach Douglas Adams, Tolkien & Pratchett*