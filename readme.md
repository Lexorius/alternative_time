# Alternative Time Systems for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/Lexorius/alternative_time.svg)](https://github.com/Lexorius/alternative_time/releases)
[![GitHub Activity](https://img.shields.io/github/commit-activity/y/Lexorius/alternative_time.svg)](https://github.com/Lexorius/alternative_time/commits/main)
[![License](https://img.shields.io/github/license/Lexorius/alternative_time.svg)](LICENSE)

A comprehensive Home Assistant integration for alternative time systems from science, science fiction, history, and various cultures. From Stardate to Maya Calendar, from Unix timestamp to Mars time - this integration provides 18 different time systems as sensors.

## 🎯 Overview

This integration transforms Home Assistant into a universal time clock with support for:
- 🚀 **Science Fiction Times** (Star Trek Stardate)
- 🔴 **Mars Time Systems** (Darian Calendar, Mars Time Zones)
- 🌐 **Internet Standards** (Unix, Swatch Internet Time)
- 🏛️ **Historical Calendars** (Maya, Attic, French Revolution)
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
- **Thematic Groups**: Sci-Fi, Historical, Military
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

### 🌐 **NATO Time with Zone (DTG)**
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

## 🎯 Usage

### Sensor Entities

After configuration, the following sensors are created (depending on selection):

| Sensor | Entity ID |
|--------|-----------|
| Timezone | `sensor.[name]_timezone` |
| Stardate | `sensor.[name]_stardate` |
| Swatch Time | `sensor.[name]_swatch_internet_time` |
| Unix Timestamp | `sensor.[name]_unix_timestamp` |
| Julian Date | `sensor.[name]_julian_date` |
| Decimal Time | `sensor.[name]_decimal_time` |
| Hexadecimal Time | `sensor.[name]_hexadecimal_time` |
| Maya Calendar | `sensor.[name]_maya_calendar` |
| NATO Time | `sensor.[name]_nato_time` |
| NATO DTG | `sensor.[name]_nato_time_with_zone` |
| NATO Rescue | `sensor.[name]_nato_rescue_time` |
| Attic Calendar | `sensor.[name]_attic_calendar` |
| Suriyakati | `sensor.[name]_suriyakati_calendar` |
| Minguo | `sensor.[name]_minguo_calendar` |
| Darian Calendar | `sensor.[name]_darian_calendar` |
| Mars Time | `sensor.[name]_mars_time` |

## 📊 Dashboard Examples

### Simple Entity Card
```yaml
type: entities
title: Alternative Time Systems
entities:
  - entity: sensor.alternative_time_stardate
  - entity: sensor.alternative_time_maya_calendar
  - entity: sensor.alternative_time_nato_time_with_zone
  - entity: sensor.alternative_time_mars_time
```

### World Clock Dashboard
```yaml
type: vertical-stack
cards:
  - type: markdown
    content: |
      ## 🌍 World Times
      **Stardate:** {{ states('sensor.alternative_time_stardate') }}
      **Internet Time:** {{ states('sensor.alternative_time_swatch_internet_time') }}
      **Maya:** {{ states('sensor.alternative_time_maya_calendar') }}
      **Athens:** {{ states('sensor.alternative_time_attic_calendar') }}
      **Thailand:** {{ states('sensor.alternative_time_suriyakati_calendar') }}
      **Taiwan:** {{ states('sensor.alternative_time_minguo_calendar') }}
      **Mars:** {{ states('sensor.alternative_time_mars_time') }}
  
  - type: glance
    entities:
      - entity: sensor.alternative_time_nato_time_with_zone
        name: NATO DTG
      - entity: sensor.alternative_time_unix_timestamp
        name: Unix
      - entity: sensor.alternative_time_decimal_time
        name: Decimal
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

### Mission Timestamp (Rescue Service)
```yaml
automation:
  - alias: "Mission Log"
    trigger:
      - platform: state
        entity_id: input_boolean.mission_active
        to: 'on'
    action:
      - service: input_text.set_value
        data:
          entity_id: input_text.mission_start
          value: "{{ states('sensor.alternative_time_nato_rescue_time') }}"
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

### Mars Sol Alarm
```yaml
automation:
  - alias: "Mars Sol Change"
    trigger:
      - platform: template
        value_template: >
          {{ 'Sol 1/' in states('sensor.alternative_time_mars_time') }}
    action:
      - service: notify.mobile_app
        data:
          title: "🔴 New Mars Year"
          message: "A new Mars year has begun!"
```

## 🔴 Mars Time Systems

### Darian Calendar
The Darian Calendar was developed by Thomas Gangale in 1985 for Mars colonization:

#### Structure:
- **24 months** (alternating Latin/Sanskrit names)
- **668 sols** per Mars year (≈ 687 Earth days)
- **27-28 sols** per month
- **7-sol week**: Sol Solis to Sol Saturni

#### Months:
1. Sagittarius/Dhanus
2. Capricornus/Makara
3. Aquarius/Kumbha
4. Pisces/Mina
5. Aries/Mesha
6. Taurus/Rishabha
7. Gemini/Mithuna
8. Cancer/Karka
9. Leo/Simha
10. Virgo/Kanya
11. Libra/Tula
12. Scorpius/Vrishchika

### Mars Time Zones (MTC)
24 time zones from MTC-12 to MTC+12, named after Mars landmarks:

#### Important Time Zones:
- **MTC+0 (Airy-0)**: Prime Meridian
- **MTC-1 (Olympus Mons)**: Tallest volcano in the solar system
- **MTC-3 (Valles Marineris)**: Largest canyon
- **MTC-9 (Chryse)**: Viking 1 landing site
- **MTC+11 (Aeolis)**: Gale Crater (Curiosity)
- **MTC+1 (Meridiani)**: Opportunity Rover

### Sol Time:
- **1 Sol** = 24h 39m 35s (Mars day)
- **Mars hour** ≈ 61.65 minutes
- **Mars minute** ≈ 61.65 seconds

## 🚀 Performance

The integration is optimized for minimal system load:

| Time System | Update Interval | Reason |
|-------------|-----------------|--------|
| Timezones, Unix, Swatch | 1 second | Second-accurate display |
| Hexadecimal | 5 seconds | Medium change rate |
| Stardate | 10 seconds | Slow change |
| Julian Date | 60 seconds | Very slow change |
| Calendars (Maya, Attic, etc.) | 1 hour | Daily change |
| Mars Time | 30 seconds | Sol time precision |

## 🐛 Troubleshooting

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

### v1.4.0 (Latest)
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
- **Star Trek** for the stardate inspiration
- **Swatch** for the revolutionary Internet Beat Time
- **Maya Culture** for their fascinating calendar system
- **NATO/Military** for standardized time notation
- **Ancient Greece** for the precise lunisolar calendar
- **Thailand & Taiwan** for their unique calendar systems
- **Thomas Gangale** for the Darian Mars Calendar
- **NASA/ESA** for Mars missions and time zone concepts
- **All Contributors and Testers** who contribute to the project

## 📧 Support

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

---

**Made with ❤️ by [Lexorius](https://github.com/Lexorius)**

*"Time is an illusion. Lunchtime doubly so. Mars time triply so." - After Douglas Adams*