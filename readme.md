# Alternative Time Systems for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/Lexorius/alternative_time.svg)](https://github.com/Lexorius/alternative_time/releases)
[![GitHub Activity](https://img.shields.io/github/commit-activity/y/Lexorius/alternative_time.svg)](https://github.com/Lexorius/alternative_time/commits/main)
[![License](https://img.shields.io/github/license/Lexorius/alternative_time.svg)](LICENSE)

A comprehensive Home Assistant integration for alternative time systems from science, science fiction, fantasy, history, and various cultures. From Stardate to Maya Calendar, from the Shire to Discworld, from Tamriel to ancient Egypt - this integration provides 24 different time systems as sensors.

## 🎯 Overview

This integration transforms Home Assistant into a universal time clock with support for:
- 🚀 **Science Fiction Times** (Star Trek Stardate, EVE Online)
- 🧙 **Fantasy Calendars** (Tolkien, Elder Scrolls, Discworld)
- 🏺 **Historical Calendars** (Maya, Attic, Egyptian, French Revolution)
- 🔴 **Mars Time Systems** (Darian Calendar, Mars Time Zones)
- 🌐 **Internet Standards** (Unix, Swatch Internet Time)
- 🎖️ **Military Time Systems** (NATO DTG in 3 variants)
- 🌏 **Cultural Calendars** (Thai, Taiwan)
- 💻 **Technical Formats** (Hexadecimal, Julian Date)

## 📦 Installation

### Via HACS (Recommended)

1. Open HACS in your Home Assistant installation
2. Click the three dots in the top right
3. Select "Custom repositories"
4. Add this URL: `https://github.com/Lexorius/alternative_time`
5. Select "Integration" as category
6. Click "Add"
7. Search for "Alternative Time Systems" and install it
8. Restart Home Assistant

### Manual Installation

1. Download the `alternative_time` folder
2. Copy it to your `/config/custom_components/` directory
3. Restart Home Assistant

## ⚙️ Configuration

### Via User Interface

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for **Alternative Time Systems**
4. Follow the configuration wizard
5. Select the desired time systems
6. Click **Submit**

### 💡 Multiple Instances

You can create multiple instances with different configurations:
- **World Clock**: Multiple instances with different time zones
- **Thematic Groups**: Sci-Fi, Fantasy, Historical, Military
- **Room-based**: Different time systems for different rooms

## 🌟 Available Time Systems

### 🌍 **Timezone**
- **Format**: `HH:MM:SS TZ` (e.g., `14:30:45 CEST`)
- **Description**: Shows current time in any Earth timezone
- **Usage**: International teams, travel planning, world clock
- **Update**: Every second

### 🚀 **Stardate**
- **Format**: `XXXXX.XX` (e.g., `47634.44`)
- **Description**: Star Trek TNG-style stardate based on year 2323
- **Feature**: Calculated using TNG formula with day fraction
- **Update**: Every 10 seconds

### 🌐 **Swatch Internet Time**
- **Format**: `@XXX.XX` (e.g., `@750.00`)
- **Description**: One day = 1000 beats, no time zones (BMT)
- **History**: Introduced by Swatch in 1998 as universal internet time
- **Update**: Every second

### 🔢 **Unix Timestamp**
- **Format**: `XXXXXXXXXX` (e.g., `1735689600`)
- **Description**: Seconds since January 1, 1970, 00:00 UTC
- **Usage**: Programming, databases, IT systems
- **Update**: Every second

### 📅 **Julian Date**
- **Format**: `XXXXXXX.XXXXX` (e.g., `2460000.50000`)
- **Description**: Continuous day count since 4713 BCE
- **Usage**: Astronomy, science, historical dating
- **Update**: Every minute

### 🔟 **Decimal Time**
- **Format**: `H:MM:SS` (e.g., `5:50:00`)
- **Description**: French Revolutionary time - 10 hours/day, 100 min/hour
- **History**: Officially used in France 1793-1805
- **Update**: Every second

### 🔤 **Hexadecimal Time**
- **Format**: `.XXXX` (e.g., `.8000`)
- **Description**: Day divided into 65536 (0x10000) parts
- **Feature**: .0000 = midnight, .8000 = noon, .FFFF = 23:59:59
- **Update**: Every 5 seconds

### 🏛️ **Maya Calendar**
- **Format**: `B.K.T.U.K | TZ TN | HD HM`
- **Example**: `13.0.12.1.15 | 8 Ahau | 3 Pop`
- **Components**:
  - Long Count (Baktun.Katun.Tun.Uinal.Kin)
  - Tzolk'in (260-day ritual calendar)
  - Haab (365-day civil calendar)
- **Update**: Hourly

### 🎖️ **NATO Time (Basic)**
- **Format**: `DDHHMM` (e.g., `151430`)
- **Description**: Day + time without timezone
- **Usage**: Simple military time notation
- **Update**: Every second

### 🌍 **NATO Time with Zone (DTG)**
- **Format**: `DDHHMM[Z] MON YY` (e.g., `151430Z JAN 25`)
- **Description**: Complete Date-Time Group with timezone
- **Timezones**: A-Z (except J), Z=UTC, B=UTC+2 (CEST)
- **Update**: Every second

### 🚑 **NATO Rescue Service Time**
- **Format**: `DD HHMM MONTH YY` (e.g., `15 1430 JAN 25`)
- **Description**: German emergency services standard notation
- **Feature**: With spaces, German month abbreviations
- **Usage**: Fire department, rescue services, THW, disaster response
- **Update**: Every second

### 🏛️ **Attic Calendar**
- **Format**: `Day Period Month | Archon | Ol.XXX.Y`
- **Example**: `5 histamenou Hekatombaion | Nikias | Ol.700.2`
- **Components**:
  - Dekad system (3×10 days/month)
  - 12 lunar months
  - Archon (annual magistrate)
  - Olympiad counting
- **Update**: Hourly

### 🇹🇭 **Suriyakati Calendar (Thai)**
- **Format**: Thai + Romanized
- **Example**: `๒๕ ธันวาคม ๒๕๖๘ | 25 Thanwakhom 2568 BE`
- **Feature**: Buddhist Era (BE = CE + 543)
- **Numbers**: Thai numerals ๐๑๒๓๔๕๖๗๘๙
- **Update**: Hourly

### 🇹🇼 **Minguo Calendar (Taiwan)**
- **Format**: Chinese + Romanized
- **Example**: `民國114年 十二月 二十五日 | Minguo 114/12/25`
- **Feature**: Year 1 = 1912 CE (ROC founding)
- **Usage**: Official documents in Taiwan
- **Update**: Hourly

### 🚀 **Darian Calendar (Mars)**
- **Format**: `Sol Month Year | Weekday | Season`
- **Example**: `15 Gemini 217 | Sol Martis | Summer`
- **Features**:
  - 24 months with 27-28 sols each
  - 668 sols per Mars year
  - 7-sol week with Latin names
- **Update**: Hourly

### 🔴 **Mars Time with Timezone**
- **Format**: `HH:MM:SS Location | Sol X/MYY | ☉/☽`
- **Example**: `14:25:30 Olympus Mons | Sol 234/MY36 | ☉ Day`
- **24 Mars Timezones**: 
  - MTC+0 (Airy-0) to MTC+12
  - MTC-1 to MTC-12
  - Named after Mars landmarks
- **Features**:
  - Sol time (24:39:35 Earth time)
  - Day/Night indicator
  - Mars year and sol number
- **Update**: Every 30 seconds

### 🚀 **EVE Online Time**
- **Format**: `YC XXX.MM.DD HH:MM:SS`
- **Example**: `YC 127.03.15 14:30:45`
- **Description**: New Eden Standard Time (NEST)
- **Features**:
  - YC = Yoiul Conference year
  - Uses UTC as base
  - YC 105 = 2003 (EVE Launch)
- **Update**: Every second

### 🍄 **Shire Calendar (Hobbits)**
- **Format**: `S.R. Year, Day Month (Weekday) | Meal`
- **Example**: `S.R. 1445, 22 Halimath (Highdei) | 🍖 Luncheon`
- **Features**:
  - 12 months of 30 days each
  - Special days (Yule, Lithe)
  - 7 Hobbit meals daily
  - Important events (Bilbo's Birthday)
- **Months**: Afteryule, Solmath, Rethe, Astron, Thrimidge, Forelithe, Afterlithe, Wedmath, Halimath, Winterfilth, Blotmath, Foreyule
- **Update**: Hourly

### 🍃 **Calendar of Imladris (Elves)**
- **Format**: `F.A. Year, Season Day (Weekday) | Time`
- **Example**: `F.A. 6025, Tuilë 22 (Elenya) | 🌞 Ára`
- **Features**:
  - 6 seasons instead of months
  - 6-day week
  - Special days (Yestarë, Loëndë, Mettarë)
  - Elvish times of day
- **Seasons**: Tuilë (Spring), Lairë (Summer), Yávië (Autumn), Quellë (Fading), Hrívë (Winter), Coirë (Stirring)
- **Update**: Hourly

### 🎮 **Tamriel Calendar (Elder Scrolls)**
- **Format**: `4E Year, Day Month (Weekday) | Time | Blessing | Event`
- **Example**: `4E 201, 17 Last Seed (Fredas) | Dusk 🌆 | Blessing: Talos | 🌕🌗`
- **Features**:
  - 12 months with unique names
  - 8-day week with Octeday
  - Divine blessings (9 Divines)
  - Daedric Princes influence
  - Two moons (Masser & Secunda)
  - Holidays and festivals
- **Months**: Morning Star, Sun's Dawn, First Seed, Rain's Hand, Second Seed, Midyear, Sun's Height, Last Seed, Hearthfire, Frostfall, Sun's Dusk, Evening Star
- **Update**: Hourly

### 🏺 **Egyptian Calendar**
- **Format**: `Dynasty Year, Hieroglyphs Day Month (Season) | Decan | Hour | God | Nile`
- **Example**: `Dynasty 1 Year 25, 𓏤𓏨 15 Thoth (Akhet) | Second Decan | ☀️ Sixth Hour | Thoth | 🌊`
- **Features**:
  - 3 seasons (Akhet, Peret, Shemu)
  - 12 months of 30 days each
  - 5 epagomenal days
  - Decans (10-day weeks)
  - Hieroglyphic numbers
  - 12 day and 12 night hours
  - Nile flood cycle
- **Seasons**: Akhet (Inundation), Peret (Emergence), Shemu (Harvest)
- **Update**: Hourly

### 🐢 **Discworld Calendar**
- **Format**: `Century Year, Day Month (Weekday) | Time | Location | Guild | Event`
- **Example**: `Century of the Anchovy, UC 25, 32 Offle (Octeday) | 🌙 Dead of Night | 📍 The Shades | Thieves' Guild`
- **Features**:
  - 13 months with Pratchett humor
  - 8-day week with Octeday
  - Impossible days (32nd April)
  - Ankh-Morpork guilds
  - Death quotes at midnight
  - L-Space library connections
  - City district rotation
- **Months**: Ick, Offle, February, March, April, May, June, Grune, August, Spune, Sektober, Ember, December
- **Update**: Hourly

## 🎯 Usage

### Sensor Entities

After configuration, the following sensors are created (depending on selection):

| Sensor | Entity ID |
|--------|-----------|
| Timezone | `sensor.[name]_timezone` |
| Stardate | `sensor.[name]_stardate` |
| Swatch Time | `sensor.[name]_swatch` |
| Unix Timestamp | `sensor.[name]_unix` |
| Julian Date | `sensor.[name]_julian` |
| Decimal Time | `sensor.[name]_decimal` |
| Hexadecimal Time | `sensor.[name]_hexadecimal` |
| Maya Calendar | `sensor.[name]_maya_calendar` |
| NATO Time | `sensor.[name]_nato_time` |
| NATO DTG | `sensor.[name]_nato_time_with_zone` |
| NATO Rescue | `sensor.[name]_nato_rescue_time` |
| Attic Calendar | `sensor.[name]_attic_calendar` |
| Suriyakati | `sensor.[name]_suriyakati_calendar` |
| Minguo | `sensor.[name]_minguo_calendar` |
| Darian Calendar | `sensor.[name]_darian_calendar` |
| Mars Time | `sensor.[name]_mars_time` |
| EVE Online | `sensor.[name]_eve_online` |
| Shire | `sensor.[name]_shire` |
| Imladris | `sensor.[name]_rivendell` |
| Tamriel | `sensor.[name]_tamriel` |
| Egyptian | `sensor.[name]_egyptian` |
| Discworld | `sensor.[name]_discworld` |

## 📊 Dashboard Examples

### Fantasy Worlds Dashboard
```yaml
type: vertical-stack
cards:
  - type: markdown
    content: |
      ## 🧙 Fantasy & Gaming Worlds
      **Shire:** {{ states('sensor.alternative_time_shire') }}
      **Imladris:** {{ states('sensor.alternative_time_rivendell') }}
      **Tamriel:** {{ states('sensor.alternative_time_tamriel') }}
      **Discworld:** {{ states('sensor.alternative_time_discworld') }}
      **EVE Online:** {{ states('sensor.alternative_time_eve_online') }}
  
  - type: entities
    title: Fantasy & Sci-Fi Times
    entities:
      - entity: sensor.alternative_time_shire
        name: Hobbit Time
      - entity: sensor.alternative_time_rivendell
        name: Elven Time
      - entity: sensor.alternative_time_tamriel
        name: Elder Scrolls
      - entity: sensor.alternative_time_discworld
        name: Discworld
      - entity: sensor.alternative_time_eve_online
        name: New Eden Time
```

### Historical Calendars Dashboard
```yaml
type: vertical-stack
cards:
  - type: markdown
    content: |
      ## 🏺 Historical Time Systems
      **Egypt:** {{ states('sensor.alternative_time_egyptian') }}
      **Maya:** {{ states('sensor.alternative_time_maya_calendar') }}
      **Athens:** {{ states('sensor.alternative_time_attic_calendar') }}
      
  - type: entities
    title: Ancient Calendars
    entities:
      - entity: sensor.alternative_time_egyptian
        name: Egyptian Calendar
      - entity: sensor.alternative_time_maya_calendar
        name: Maya Calendar
      - entity: sensor.alternative_time_attic_calendar
        name: Attic Calendar
```

### World Clock Dashboard
```yaml
type: vertical-stack
cards:
  - type: markdown
    content: |
      ## 🌍 World Times
      **Stardate:** {{ states('sensor.alternative_time_stardate') }}
      **Internet Time:** {{ states('sensor.alternative_time_swatch') }}
      **Maya:** {{ states('sensor.alternative_time_maya_calendar') }}
      **Athens:** {{ states('sensor.alternative_time_attic_calendar') }}
      **Thailand:** {{ states('sensor.alternative_time_suriyakati_calendar') }}
      **Taiwan:** {{ states('sensor.alternative_time_minguo_calendar') }}
      **Mars:** {{ states('sensor.alternative_time_mars_time') }}
      **Shire:** {{ states('sensor.alternative_time_shire') }}
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

### Mars Mission Dashboard
```yaml
type: vertical-stack
cards:
  - type: markdown
    content: |
      ## 🔴 Mars Mission Control
      
      **Mars Time:** {{ states('sensor.alternative_time_mars_time') }}
      **Darian Calendar:** {{ states('sensor.alternative_time_darian_calendar') }}
      
  - type: entities
    title: Mars Time Zones
    entities:
      - entity: sensor.alternative_time_mars_time
        name: Current Mars Time
      - entity: sensor.alternative_time_darian_calendar
        name: Mars Date
```

## 🤖 Automations

### Elder Scrolls Holiday
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
          title: "🎮 Tamriel Holiday"
          message: "The New Life Festival begins in Tamriel!"
```

### Egyptian Epagomenal Days
```yaml
automation:
  - alias: "Birthday of the Gods"
    trigger:
      - platform: template
        value_template: >
          {{ 'Birthday of' in states('sensor.alternative_time_egyptian') }}
    action:
      - service: notify.mobile_app
        data:
          title: "🏺 Egyptian Calendar"
          message: "{{ states('sensor.alternative_time_egyptian') }}"
```

### Discworld Death Quote
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
          entity_id: media_player.bedroom
          message: "Death says: THERE IS NO JUSTICE. THERE IS JUST ME."
```

### EVE Online Daily Tasks
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
          message: "Daily tasks have reset!"
```

### Elvish New Year
```yaml
automation:
  - alias: "Yestarë - Elvish New Year"
    trigger:
      - platform: template
        value_template: >
          {{ 'Yestarë' in states('sensor.alternative_time_rivendell') }}
    action:
      - service: notify.mobile_app
        data:
          title: "🍃 Elvish New Year"
          message: "The Elves celebrate Yestarë - a new year begins in Middle-earth!"
```

### Stardate Announcement
```yaml
automation:
  - alias: "Stardate Noon"
    trigger:
      - platform: time
        at: "12:00:00"
    action:
      - service: tts.google_say
        data:
          entity_id: media_player.living_room
          message: "Stardate {{ states('sensor.alternative_time_stardate') }}"
```

### Maya Calendar Day Change
```yaml
automation:
  - alias: "Maya New Day"
    trigger:
      - platform: state
        entity_id: sensor.alternative_time_maya_calendar
    action:
      - service: notify.mobile_app
        data:
          title: "Maya Calendar"
          message: "New day: {{ trigger.to_state.state }}"
```

## 🎮 Elder Scrolls Calendar System

### Tamriel Calendar
The calendar of Tamriel from The Elder Scrolls game series:

#### The 12 Months:
1. **Morning Star** (January) ❄️
2. **Sun's Dawn** (February) 🌅
3. **First Seed** (March) 🌱
4. **Rain's Hand** (April) 🌧️
5. **Second Seed** (May) 🌿
6. **Midyear** (June) ☀️
7. **Sun's Height** (July) 🌞
8. **Last Seed** (August) 🌾
9. **Hearthfire** (September) 🔥
10. **Frostfall** (October) 🍂
11. **Sun's Dusk** (November) 🌆
12. **Evening Star** (December) ⭐

#### Features:
- **8-day week** with Octeday as the eighth day
- **Divine blessings** from the 9 Divines
- **Daedric Princes** influence on certain days
- **Two moons**: Masser and Secunda with different phases
- **Many holidays**: New Life Festival, Witches Festival, Warriors Festival

## 🏺 Ancient Egyptian Calendar System

### Egyptian Calendar
The calendar of ancient Egypt with its unique features:

#### The 3 Seasons:
- **Akhet** (Inundation) 🌊 - 4 months
- **Peret** (Emergence) 🌱 - 4 months
- **Shemu** (Harvest) ☀️ - 4 months

#### Features:
- **365 days**: 12 months of 30 days + 5 epagomenal days
- **Decans**: 10-day weeks
- **Hieroglyphic numbers**: 𓏤𓏥𓏦𓏧𓏨
- **12 day and 12 night hours**
- **Patron gods** for each month
- **Nile status** depending on season
- **Epagomenal days**: Birthdays of Osiris, Horus, Set, Isis, Nephthys

## 🐢 Discworld Calendar System

### Discworld Calendar (Terry Pratchett)
The humorous calendar of the Discworld:

#### The 13 Months:
1. **Ick** ❄️
2. **Offle** ❄️
3. **February** 🌨️ (yes, really February!)
4. **March** 🌬️
5. **April** 🌧️
6. **May** 🌸
7. **June** ☀️
8. **Grune** 🌿
9. **August** 🌞
10. **Spune** 🍂
11. **Sektober** 🍺 (drinking month!)
12. **Ember** 🔥
13. **December** ⭐

#### Features:
- **8-day week** with Octeday
- **Impossible days**: 32nd April and 32nd December
- **Guilds of Ankh-Morpork**: Daily influence of different guilds
- **Death quotes** at midnight
- **L-Space**: Library connections at 03:33
- **City districts**: The Shades, Unseen University, Patrician's Palace
- **Century of the Anchovy**: Current era

### Death's Best Quotes:
- "THERE IS NO JUSTICE. THERE IS JUST ME."
- "I COULD MURDER A CURRY."
- "CATS. CATS ARE NICE."
- "SQUEAK." (Death of Rats)

## 🚀 EVE Online Time System

### New Eden Standard Time (NEST)
EVE Online uses its own calendar system:

- **YC** = Yoiul Conference (Year)
- **Base**: UTC Earth time
- **Epoch**: YC 0 = 23236 AD
- **Game Start**: YC 105 = 2003
- **Format**: YC XXX.MM.DD HH:MM:SS

Important EVE Times:
- **11:00 UTC**: Daily Downtime & Reset
- **Jita Time**: Main trading hours
- **Fleet Ops**: Usually 19:00-23:00 UTC

## 🚀 Performance

The integration is optimized for minimal system load:

| Time System | Update Interval | Reason |
|-------------|-----------------|--------|
| Timezones, Unix, Swatch, EVE | 1 second | Second-accurate display |
| Hexadecimal | 5 seconds | Medium change rate |
| Stardate | 10 seconds | Slow change |
| Julian Date | 60 seconds | Very slow change |
| Calendars (Maya, Attic, etc.) | 1 hour | Daily change |
| Mars Time | 30 seconds | Sol time precision |
| Fantasy Calendars | 1 hour | Event-based |

## 🛠 Troubleshooting

### Integration Not Found
```bash
# Check folder structure
ls -la /config/custom_components/alternative_time/

# Should contain:
# __init__.py, manifest.json, config_flow.py, sensor.py, const.py, translations/
```

### Sensors Show "unavailable"
1. Check logs: Settings → System → Logs
2. Ensure at least one time system is enabled
3. Clear cache: `find /config -name "__pycache__" -exec rm -rf {} +`
4. Restart Home Assistant

### "Blocking call" Warning
The integration uses asynchronous operations. If warning persists:
```bash
ha core restart
```

## 📈 Version History

### v1.6.0 (Latest)
- ✨ Added Tamriel Calendar (Elder Scrolls)
- ✨ Added Egyptian Calendar
- ✨ Added Discworld Calendar
- 🎮 Gaming worlds expanded
- 🏺 Historical calendars expanded
- 🐢 Terry Pratchett's humor integrated
- 💀 Death quotes and L-Space features

### v1.5.0
- ✨ Added EVE Online Time (New Eden Standard Time)
- ✨ Added Shire Calendar (Shire Reckoning)
- ✨ Added Calendar of Imladris (Elves)
- 🧙 Complete Tolkien time systems
- 🚀 Sci-Fi expansion with EVE Online
- 🍄 7 Hobbit meals integration
- 🍃 6 Elvish seasons

### v1.4.0
- ✨ Added Darian Calendar (Mars)
- ✨ Mars Time with 24 selectable time zones
- 🔴 Complete Mars time system support
- 🚀 Ready for Mars colonization

### v1.3.0
- ✨ Added Suriyakati Calendar (Thai)
- ✨ Added Minguo Calendar (Taiwan/ROC)
- ✨ Added Attic Calendar (Ancient Athens)
- 📝 Detailed descriptions in config flow
- 🌏 Extended support for Asian calendar systems

### v1.2.0
- ✨ Added NATO Rescue Service time format
- 🔧 Fixed NATO time (now with date)
- 📝 Extended documentation for all NATO formats

### v1.1.0
- ✨ Added Maya Calendar
- ✨ Added NATO time (with and without zone indicator)
- 🐛 Async timezone initialization for better performance
- 🐛 Fixed blocking call warning

### v1.0.0
- 🎉 Initial release
- ✨ Basic time systems implemented

## 📝 Planned Features

- [ ] More Sci-Fi time systems (Star Wars, Stargate, Doctor Who, The Expanse)
- [ ] Historical calendars (Roman, Egyptian, Chinese, Aztec)
- [ ] Religious calendars (Islamic, Jewish, Coptic, Hindu)
- [ ] More Fantasy calendars (Game of Thrones, Warhammer, D&D)
- [ ] More Mars features (Phobos/Deimos orbits, Earth time converter)
- [ ] Configurable update intervals
- [ ] Time conversion between systems
- [ ] Graphical clock cards
- [ ] Calendar export functions

## 🤝 Contributing

Contributions are welcome! 

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/NewTimeSystem`)
3. Commit your changes (`git commit -m 'Add: New time system'`)
4. Push to the branch (`git push origin feature/NewTimeSystem`)
5. Open a Pull Request

### Development Environment

```bash
# Clone repository
git clone https://github.com/Lexorius/alternative_time.git
cd alternative_time

# Link to Home Assistant custom_components
ln -s $(pwd)/custom_components/alternative_time /config/custom_components/

# Restart Home Assistant
ha core restart

# Watch logs
tail -f /config/home-assistant.log | grep alternative_time
```

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- **Home Assistant Community** for the amazing platform
- **J.R.R. Tolkien** for the detailed calendar systems of Middle-earth
- **Bethesda Game Studios** for The Elder Scrolls and Tamriel
- **Terry Pratchett** for the Discworld and its unique humor
- **Ancient Egyptians** for one of humanity's first precise calendars
- **CCP Games** for EVE Online and the New Eden universe
- **Star Trek** for the stardate inspiration
- **Swatch** for the revolutionary Internet Beat Time
- **Maya Culture** for their fascinating calendar system
- **NATO/Military** for standardized time notation
- **Ancient Greece** for the precise lunisolar calendar
- **Thailand & Taiwan** for their unique calendar systems
- **Thomas Gangale** for the Darian Mars Calendar
- **NASA/ESA** for Mars missions and time zone concepts
- **All Contributors and Testers** who contribute to the project

## 🔧 Support

- **Issues**: [GitHub Issues](https://github.com/Lexorius/alternative_time/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Lexorius/alternative_time/discussions)
- **Wiki**: [GitHub Wiki](https://github.com/Lexorius/alternative_time/wiki)

## 🌐 Resources

### Further Reading
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
- [Elder Scrolls Calendar](https://en.uesp.net/wiki/Lore:Calendar)
- [Ancient Egyptian Calendar](https://en.wikipedia.org/wiki/Egyptian_calendar)
- [Discworld Calendar](https://wiki.lspace.org/Calendar)

---

**Made with ❤️ by [Lexorius](https://github.com/Lexorius)**

*"Time is an illusion. Lunchtime doubly so. Second breakfast triply so. Octeday quadruply so." - After Douglas Adams, Tolkien & Pratchett*