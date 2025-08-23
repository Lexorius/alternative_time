# Alternative Time Systems for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/Lexorius/alternative_time.svg)](https://github.com/Lexorius/alternative_time/releases)
[![GitHub Activity](https://img.shields.io/github/commit-activity/y/Lexorius/alternative_time.svg)](https://github.com/Lexorius/alternative_time/commits/main)
[![License](https://img.shields.io/github/license/Lexorius/alternative_time.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-2.5.1.0-blue)](https://github.com/Lexorius/alternative_time)

A comprehensive Home Assistant integration providing **30+ alternative time systems** from science, science fiction, fantasy, history, religion, and various cultures. Transform your Home Assistant into a universal time machine!

## 🎯 Overview

Transform your Home Assistant into a multiversal clock supporting:
- 🚀 **Science Fiction** (Star Trek, Star Wars, EVE Online, Warhammer 40K)
- 🧙 **Fantasy Worlds** (Tolkien, Elder Scrolls, Discworld, Warcraft)
- 🏛️ **Historical Calendars** (Maya, Egyptian, Attic, Roman, French Revolutionary)
- 🔴 **Mars Colonization** (Darian Calendar, Mars Time Zones)
- 🌍 **Cultural Calendars** (Islamic, Thai, Taiwanese, Chinese)
- 💻 **Technical Formats** (Unix, Hexadecimal, Julian Date, Swatch Internet Time)
- 🎖️ **Military Systems** (NATO DTG in multiple formats)

## ✨ New in Version 2.5.1.0

- 🎨 **Enhanced Config Flow** with full calendar-specific options
- 🌐 **Multi-language Support** for 12 languages
- 🔧 **Per-calendar Configuration** with detailed options
- 📱 **Improved UI** with full text labels (no abbreviations!)
- 🎯 **Smart Categories** for easier calendar selection
- ⚡ **Performance Optimizations** for real-time calendars

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

### Via User Interface

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for **Alternative Time Systems**
4. Follow the configuration wizard:
   - **Step 1**: Name your instance
   - **Step 2**: Select calendar categories
   - **Step 3**: Choose specific calendars
   - **Step 4**: Configure individual calendar options
5. Click **Submit**

### 💡 Configuration Tips

- Create multiple instances for themed displays
- Each calendar has specific configuration options
- Options include display formats, precision, special features
- All options have full descriptions in your language

## 🌟 Available Time Systems

### 🚀 Science Fiction

#### Star Trek Stardate
- **Formats**: The Next Generation, Original Series, Discovery, Kelvin Timeline
- **Features**: Episode references, starship rotation, customizable precision
- **Example**: `47634.44`

#### Star Wars Galactic Calendar
- **Format**: `35:3:21 GrS | Taungsday`
- **Features**: 368-day years, festival weeks, era systems

#### EVE Online Time
- **Format**: `YC 127.03.15 14:30:45 NEST`
- **Features**: Real-time updates, empire rotation, trade hub info

#### Warhammer 40K Imperial Dating
- **Format**: `0.523.025.M42`
- **Features**: Check numbers, millennium designation, Imperial prayers

### 🧙 Fantasy Calendars

#### Tolkien's Middle-earth
- **Shire Calendar**: 7 daily meals, special days, moon phases
- **Rivendell Calendar**: 6 Elvish seasons, yén cycles, multiple languages
- **Format options**: Quenya, Sindarin, English, or mixed

#### Elder Scrolls (Tamriel)
- **Features**: Two moons (Masser & Secunda), Daedric days, birthsigns
- **Khajiit forms**: Based on moon phase combinations
- **Guild activities**: Daily guild schedules

#### Discworld
- **8-day weeks**: Including Octeday!
- **Impossible dates**: 32nd of December
- **Death quotes**: Daily wisdom at midnight
- **L-Space detection**: At 3:33

#### World of Warcraft
- **Azeroth calendar**: With seasonal events
- **Features**: Moon phases, guild events, PvP seasons

### 🏛️ Historical Calendars

#### Maya Calendar
- **Long Count**: `13.0.12.1.15`
- **Tzolk'in & Haab**: Sacred and civil calendars
- **Features**: Lord of the Night, Venus cycle

#### Ancient Egyptian
- **Format**: `Dynasty 1 Year 25, 𓈔𓈨 15 Thoth`
- **Features**: Hieroglyphs, flood predictions, pharaoh info

#### Attic Calendar (Ancient Athens)
- **Features**: Lunar months, archon years, festival days
- **Democracy events**: Assembly meetings, court days

#### Roman Calendar
- **Format**: `a.d. XVI Kal. Ian. MMDCCLXXVIII A.U.C.`
- **Features**: Kalends/Nones/Ides, consular dating

### 🌍 Cultural Calendars

#### Islamic (Hijri)
- **Lunar calendar**: 354/355 days
- **Features**: Prayer times, holy days

#### Thai (Suriyakati)
- **Buddhist Era**: BE = CE + 543
- **Features**: Thai numerals, zodiac animals

#### Taiwanese (Minguo)
- **ROC calendar**: Year 1 = 1912 CE
- **Features**: Traditional festivals

#### Chinese Lunar
- **Features**: Zodiac animals, solar terms, festivals

### 🔴 Mars Time Systems

#### Darian Calendar
- **24 Martian months**: 668-669 sols per year
- **Example**: `Sol 15 Gemini 217`

#### Mars Sol Time
- **24 time zones**: From Olympus Mons to Gale Crater
- **Features**: Sol tracking, Earth time conversion

### 💻 Technical Formats

#### Unix Timestamp
- **Format**: `1735689600`
- **Updates**: Every second

#### Swatch Internet Time
- **Format**: `@750.00`
- **Features**: No time zones, 1000 beats per day

#### Hexadecimal Time
- **Format**: `.8000`
- **Features**: Day in 65536 parts

#### Julian Date
- **Format**: `2460000.50000`
- **Features**: Modified Julian Date option

### 🎖️ Military Time

- **NATO Basic**: `151430`
- **NATO DTG**: `151430Z JAN 25`
- **NATO Rescue**: `15 1430 JANUAR 25`

## 📊 Example Dashboards

### Sci-Fi Command Center
```yaml
type: vertical-stack
cards:
  - type: markdown
    content: |
      # 🚀 Sci-Fi Command Center
      **Stardate:** {{ states('sensor.scifi_stardate') }}
      **Star Wars:** {{ states('sensor.scifi_star_wars') }}
      **EVE Online:** {{ states('sensor.scifi_eve_online') }}
      **Warhammer 40K:** {{ states('sensor.scifi_warhammer40k') }}
```

### Fantasy Realms
```yaml
type: entities
title: 🧙 Fantasy Worlds
entities:
  - entity: sensor.fantasy_shire
    name: The Shire
  - entity: sensor.fantasy_rivendell
    name: Rivendell
  - entity: sensor.fantasy_tamriel
    name: Tamriel
  - entity: sensor.fantasy_discworld
    name: Ankh-Morpork
```

### Historical Timeline
```yaml
type: glance
title: 🏛️ Ancient Calendars
entities:
  - entity: sensor.history_maya
    name: Maya
  - entity: sensor.history_egyptian
    name: Egypt
  - entity: sensor.history_attic
    name: Athens
  - entity: sensor.history_roman
    name: Rome
```

## 🤖 Automations

### Hobbit Meal Reminder
```yaml
automation:
  - alias: "Hobbit Meal Time"
    trigger:
      - platform: template
        value_template: >
          {{ 'First Breakfast' in state_attr('sensor.fantasy_shire', 'meal_time') }}
    action:
      - service: notify.mobile_app
        data:
          title: "🍳 Hobbit Meal Time!"
          message: "Time for First Breakfast!"
```

### Death's Daily Quote (Discworld)
```yaml
automation:
  - alias: "Death Says"
    trigger:
      - platform: time
        at: "00:00:00"
    action:
      - service: notify.mobile_app
        data:
          title: "💀 DEATH SAYS"
          message: >
            {{ state_attr('sensor.fantasy_discworld', 'death_says') }}
```

## 🌐 Multi-Language Support

Full support for 12 languages:
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

| Calendar Type | Update Interval | Performance Impact |
|--------------|-----------------|-------------------|
| Real-time (Unix, EVE) | 1 second | Low |
| Stardate | 10 seconds | Minimal |
| Date-based | 1 hour | Negligible |
| Static | On demand | None |

## 🛠️ Development

### Adding a New Calendar

1. Create `calendars/your_calendar.py`
2. Implement `CALENDAR_INFO` dictionary
3. Extend `AlternativeTimeSensorBase`
4. Add `set_options()` method for config flow
5. Include all 12 language translations

### Calendar Structure
```python
CALENDAR_INFO = {
    "id": "unique_id",
    "version": "2.5.1.0",
    "icon": "mdi:calendar",
    "category": "fantasy|scifi|historical|etc",
    "name": {...},  # 12 languages
    "description": {...},  # 12 languages
    "config_options": {...}  # With full labels!
}
```

## 🐛 Troubleshooting

### Common Issues

1. **Calendar not showing up**
   - Check logs for errors
   - Verify installation path
   - Restart Home Assistant

2. **Wrong time displayed**
   - Check timezone settings
   - Verify calendar configuration
   - Some calendars are fictional!

3. **Missing translations**
   - Update to latest version
   - Report missing translations on GitHub

## 📝 License

MIT License - See [LICENSE](LICENSE) file

## 🙏 Credits

- **Terry Pratchett** - Discworld Calendar (GNU Terry Pratchett)
- **J.R.R. Tolkien** - Middle-earth Calendars
- **Gene Roddenberry** - Star Trek Stardate
- **CCP Games** - EVE Online Time
- **Bethesda** - Elder Scrolls Calendar
- All contributors and testers!

## 🔗 Links

- [GitHub Repository](https://github.com/Lexorius/alternative_time)
- [Report Issues](https://github.com/Lexorius/alternative_time/issues)
- [HACS](https://hacs.xyz/)
- [Home Assistant](https://www.home-assistant.io/)

## 📮 Support

Found a bug? Have a feature request?
- Open an [issue on GitHub](https://github.com/Lexorius/alternative_time/issues)
- Check [existing issues](https://github.com/Lexorius/alternative_time/issues) first
- Include logs and configuration details

---

**Made with ❤️ for the Home Assistant Community**

*"Time is an illusion. Lunchtime doubly so."* - Douglas Adams