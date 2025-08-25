# Alternative Time Systems for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/Lexorius/alternative_time.svg)](https://github.com/Lexorius/alternative_time/releases)
[![GitHub Activity](https://img.shields.io/github/commit-activity/y/Lexorius/alternative_time.svg)](https://github.com/Lexorius/alternative_time/commits/main)
[![License](https://img.shields.io/github/license/Lexorius/alternative_time.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-2.5.1.145-blue)](https://github.com/Lexorius/alternative_time)

A comprehensive Home Assistant integration providing **30+ alternative time systems** from science, science fiction, fantasy, history, religion, and various cultures. Transform your Home Assistant into a universal time machine!

## 🎯 Overview

Transform your Home Assistant into a multiversal clock supporting:
- 🪐 **Solar System Tracker** (Real-time planetary positions with visual maps)
- 🚀 **Science Fiction** (Star Trek, Star Wars, EVE Online, Warhammer 40K)
- 🧙 **Fantasy Worlds** (Tolkien, Elder Scrolls, Discworld, Warcraft)
- 🏛️ **Historical Calendars** (Maya, Egyptian, Attic, Roman, French Revolutionary)
- 🔴 **Mars Colonization** (Darian Calendar, Mars Time Zones)
- 🌍 **Cultural Calendars** (Islamic, Thai, Taiwanese, Chinese)
- 💻 **Technical Formats** (Unix, Hexadecimal, Julian Date, Swatch Internet Time)
- 🎖️ **Military Systems** (NATO DTG in multiple formats)

## ✨ New in Version 2.5.1.148

### 🪐 Solar System Positions Plugin
- **Real-time Planetary Tracking**: Live positions of all planets, dwarf planets, and space probes
- **Interactive SVG/PNG Maps**: Visual representation of the solar system
- **Multiple Coordinate Systems**: Heliocentric and geocentric views
- **Visibility Calculations**: Shows when planets are visible from your location
- **Constellation Tracking**: Displays zodiac position for each planet
- **Distance Information**: AU and kilometer distances from Sun/Earth
- **Configurable Display**: Choose individual planets or track all objects
- **Kuiper Belt Visualization**: Shows the outer solar system region
- **Voyager Probes**: Tracks Voyager 1 & 2 positions
- **James Webb Space Telescope**: Shows position at L2 point

### 🔧 Options Flow Implementation
- **Live Configuration Changes**: Modify calendar settings without reinstalling the integration
- **Per-Calendar Options**: Each calendar's settings can be adjusted individually
- **No Restart Required**: Changes take effect immediately
- **Preserve Existing Data**: All your configurations remain intact

### 🌍 Complete Multi-Language Support
- Full translations for all UI elements in 12 languages
- Calendar-specific descriptions and labels in your language
- Options flow fully localized

## 📦 Installation

### Via HACS (Recommended)

1. Open HACS in your Home Assistant
2. Click the three dots menu → **Custom repositories**
3. Add URL: `https://github.com/Lexorius/alternative_time`
4. Category: **Integration**
5. Click **Add**
6. Search for **Alternative Time Systems** and install
7. Restart Home Assistant

### Manual Installation

1. Download the `alternative_time` folder
2. Copy to `/config/custom_components/`
3. Restart Home Assistant

## ⚙️ Configuration

### Initial Setup

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for **Alternative Time Systems**
4. Follow the configuration wizard:
   - **Step 1**: Name your instance
   - **Step 2**: Select calendar categories
   - **Step 3**: Choose specific calendars
   - **Step 4**: Configure individual calendar options
   - **Step 5**: Review disclaimer
5. Click **Submit**

### Modifying Calendar Options (New!)

1. Go to **Settings** → **Devices & Services**
2. Find your **Alternative Time Systems** instance
3. Click **Configure**
4. Select the calendar you want to modify
5. Adjust the settings
6. Click **Submit** - changes apply immediately!

## 🌟 Available Time Systems

### 🪐 Solar System Tracker (NEW!)

#### Solar System Positions
- **Real-time tracking**: All planets, Pluto, Voyager probes, JWST
- **Visual maps**: SVG and PNG generation with orbits
- **Options**: 
  - Coordinate system (heliocentric/geocentric)
  - Individual planet tracking or all objects
  - Visibility times from your location
  - Distance in AU and kilometers
  - Zodiac constellation positions
  - Retrograde motion indicators
- **Visualization scales**: Logarithmic, linear, or compressed
- **Updates**: Every 5 minutes

### 🚀 Science Fiction

#### Star Trek Stardate
- **Formats**: TNG, TOS, Discovery, Kelvin Timeline
- **Options**: Precision (0-2 decimals), Stardate format selection
- **Example**: `47634.44`

#### Star Wars Galactic Calendar
- **Format**: `35:3:21 GrS | Taungsday`
- **Options**: Era selection (BBY/ABY/GrS), Date format

#### EVE Online Time
- **Format**: `YC 127.03.15 14:30:45 NEST`
- **Options**: Empire rotation, Trade hub display

#### Warhammer 40K Imperial Dating
- **Format**: `0.523.025.M42`
- **Options**: Check number precision, Imperial prayers

### 🧙 Fantasy Calendars

#### Tolkien's Middle-earth
- **Shire Calendar**: Hobbit meal times, special days
- **Rivendell Calendar**: Elvish seasons, multiple languages
- **Options**: Language (Quenya/Sindarin/English), Display format

#### Elder Scrolls (Tamriel)
- **Features**: Moon phases, Daedric days
- **Options**: Khajiit forms, Guild activities

#### Discworld
- **Features**: 8-day weeks, Death quotes
- **Options**: L-Space detection, Quote frequency

#### World of Warcraft
- **Features**: Azeroth calendar with events
- **Options**: Moon phase display, PvP seasons

### 🏛️ Historical Calendars

#### Maya Calendar
- **Long Count**: `13.0.12.1.15`
- **Options**: Display format, Venus cycle

#### Ancient Egyptian
- **Format**: Dynasty and hieroglyphs
- **Options**: Hieroglyph display, Flood predictions

#### Attic Calendar
- **Features**: Lunar months, Festival days
- **Options**: Archon years, Democracy events

#### Roman Calendar
- **Format**: Kalends/Nones/Ides
- **Options**: Consular dating, Latin numerals

### 🌍 Cultural Calendars

#### Islamic (Hijri)
- **Lunar calendar**: 354/355 days
- **Options**: Prayer times display

#### Thai (Suriyakati)
- **Buddhist Era**: BE = CE + 543
- **Options**: Thai numerals, Zodiac display

#### Chinese Lunar
- **Features**: Zodiac animals, Solar terms
- **Options**: Festival display

### 💻 Technical Formats

#### Unix Timestamp
- **Updates**: Every second
- **Options**: Milliseconds display

#### Swatch Internet Time
- **Format**: `@750.00`
- **Options**: Precision

#### Hexadecimal Time
- **Format**: `.8000`
- **Options**: Display format

### 🎖️ Military Time

- **NATO DTG Formats**: Basic, Full, Rescue
- **Options**: Time zone selection, Format style

## 📊 Example Dashboard Configuration

### Solar System Tracker (Visual)
```yaml
type: picture-entity
entity: sensor.alternative_time_solar_system
name: Solar System Live Map
show_state: true
show_name: true
```

### Multi-Calendar Display
```yaml
type: entities
title: Alternative Time Systems
entities:
  - entity: sensor.alternative_time_solar_system
    name: Solar System
  - entity: sensor.alternative_time_stardate
    name: Stardate
  - entity: sensor.alternative_time_shire
    name: Shire Calendar
  - entity: sensor.alternative_time_mars_sol
    name: Mars Sol Date
  - entity: sensor.alternative_time_maya
    name: Maya Long Count
```

## 🤖 Automation Example

### Daily Stardate Log
```yaml
automation:
  - alias: "Captain's Log"
    trigger:
      - platform: time
        at: "09:00:00"
    action:
      - service: notify.persistent_notification
        data:
          title: "Captain's Log"
          message: "Stardate {{ states('sensor.alternative_time_stardate') }}"
```

## 🌐 Supported Languages

Full UI and calendar translations in:
- 🇬🇧 English
- 🇩🇪 Deutsch
- 🇪🇸 Español
- 🇫🇷 Français
- 🇮🇹 Italiano
- 🇳🇱 Nederlands
- 🇵🇱 Polski
- 🇵🇹 Português
- 🇷🇺 Русский
- 🇯🇵 日本語
- 🇨🇳 中文
- 🇰🇷 한국어

## 📈 Performance

| Calendar Type | Update Interval | CPU Impact |
|--------------|-----------------|------------|
| Real-time | 1 second | Minimal |
| Dynamic | 10-60 seconds | Low |
| Solar System | 5 minutes | Low (with visualization) |
| Daily | 1 hour | Negligible |

## 🛠️ Plugin Development

### Creating a Calendar Plugin

1. Create file: `custom_components/alternative_time/calendars/your_calendar.py`
2. Define `CALENDAR_INFO` dictionary with metadata
3. Implement `YourCalendarSensor(AlternativeTimeSensorBase)`
4. Add `config_options` for user configuration
5. Include translations for all 12 languages

### Minimal Calendar Template
```python
CALENDAR_INFO = {
    "id": "your_calendar",
    "version": "1.0.0",
    "icon": "mdi:calendar",
    "category": "technical",
    "update_interval": 3600,
    "translations": {
        "en": {
            "name": "Your Calendar",
            "description": "Calendar description"
        },
        # ... other languages
    },
    "config_options": {
        "option_key": {
            "type": "select",
            "default": "value1",
            "options": ["value1", "value2"],
            "translations": {
                "en": {
                    "label": "Option Label",
                    "description": "Option description"
                }
                # ... other languages
            }
        }
    }
}
```

## 🐛 Troubleshooting

### Calendar Not Appearing
- Check Home Assistant logs for errors
- Verify the calendar file is in the correct directory
- Ensure `CALENDAR_INFO['id']` matches the filename

### Options Not Saving
- Check that your calendar has `config_options` defined
- Verify the option types are supported (text, number, boolean, select)
- Review logs for configuration errors

### Wrong Language Displayed
- Check Home Assistant language settings
- Verify translations exist for your language
- Fallback to English if translation missing

## 📝 License

MIT License - See [LICENSE](LICENSE) file for details

## 🙏 Acknowledgments

- Home Assistant Community for feedback and testing
- Calendar system creators and maintainers
- All contributors to the project

## 📮 Support

- **Bug Reports**: [GitHub Issues](https://github.com/Lexorius/alternative_time/issues)
- **Feature Requests**: Open a GitHub issue with [Enhancement] tag
- **Questions**: Use GitHub Discussions

## 🔗 Links

- [GitHub Repository](https://github.com/Lexorius/alternative_time)
- [HACS](https://hacs.xyz/)
- [Home Assistant](https://www.home-assistant.io/)

---

**Version 2.5.1.145** - Made with ❤️ for the Home Assistant Community