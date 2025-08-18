# Alternative Time Systems for Home Assistant

![Version](https://img.shields.io/badge/version-2.5.0.8-blue)
![HACS](https://img.shields.io/badge/HACS-Custom-orange)
![License](https://img.shields.io/badge/license-MIT-green)

A comprehensive Home Assistant integration for alternative time systems from science, science fiction, fantasy, history, and various cultures. From Stardate to Maya Calendar, from the Shire to Discworld, from Tamriel to ancient Egypt - this integration provides 24 different time systems as sensors.

## 🌟 Features Overview

This integration transforms Home Assistant into a universal time clock with support for:
- 🚀 **Science Fiction Times** (Star Trek Stardate, EVE Online)
- 🧙 **Fantasy Calendars** (Tolkien, Elder Scrolls, Discworld)
- 🏺 **Historical Calendars** (Maya, Attic, Egyptian, French Revolution)
- 🔴 **Mars Time Systems** (Darian Calendar, Mars Time Zones)
-    **ESA Lunar Time System** (experimental) 
- 🌐 **Internet Standards** (Unix, Swatch Internet Time)
- 🎖️ **Military Time Systems** (NATO DTG in 3 variants)
- 🌏 **Cultural Calendars** (Thai, Taiwan)
- 💻 **Technical Formats** (Hexadecimal, Julian Date)

## 📅 Available Calendar Systems

### 🚀 Science Fiction & Technical

| Calendar | Description | Format Example |
|----------|-------------|----------------|
| **Stardate** | Star Trek TNG-style stardate | `47634.44` |
| **EVE Online Time** | New Eden Standard Time (NEST) | `YC 127.03.15 14:30:45` |
| **Swatch Internet Time** | Universal internet time in beats | `@750.00` |
| **Unix Timestamp** | Seconds since 1970-01-01 | `1735689600` |
| **Julian Date** | Continuous day count since 4713 BCE | `2460000.50000` |
| **Hexadecimal Time** | Day divided into 65536 parts | `.8000` |

### 🧙 Fantasy Worlds

| Calendar | Description | Format Example |
|----------|-------------|----------------|
| **Shire Calendar** | Tolkien's Hobbit calendar with meals | `S.R. 1445, 22 Halimath (Highdei)` |
| **Calendar of Imladris** | Elvish calendar with 6 seasons | `F.A. 6025, Tuilë 22 (Elenya)` |
| **Tamriel Calendar** | Elder Scrolls with Divine blessings | `4E 201, 17 Last Seed (Fredas)` |
| **Discworld Calendar** | Terry Pratchett's humorous calendar | `Century of the Anchovy, UC 25, 32 Offle` |

### 🏺 Historical Calendars

| Calendar | Description | Format Example |
|----------|-------------|----------------|
| **Maya Calendar** | Long Count, Tzolk'in, and Haab | `13.0.12.1.15 \| 8 Ahau \| 3 Pop` |
| **Attic Calendar** | Ancient Athens lunar calendar | `5 histamenou Hekatombaion` |
| **Egyptian Calendar** | Ancient Egypt with hieroglyphs | `Dynasty 1 Year 25, 𓏤𓏨 15 Thoth` |
| **French Revolutionary** | Decimal time (10 hours/day) | `5:50:00` |

### 🌏 Cultural Calendars

| Calendar | Description | Format Example |
|----------|-------------|----------------|
| **Suriyakati (Thai)** | Thai Buddhist Era calendar | `๒๕ ธันวาคม ๒๕๖๘` |
| **Minguo (Taiwan)** | Republic of China calendar | `民國114年 十二月 二十五日` |

### 🔴 Mars Time Systems

| Calendar | Description | Format Example |
|----------|-------------|----------------|
| **Darian Calendar** | Mars calendar with 24 months | `Sol 15 Gemini 217` |
| **Mars Time** | 24 Mars time zones with sol tracking | `14:25:30 Olympus Mons` |

### 🎖️ Military Time Systems

| Calendar | Description | Format Example |
|----------|-------------|----------------|
| **NATO Time** | Simple military format | `151430` |
| **NATO DTG** | Date-Time Group with timezone | `151430Z JAN 25` |
| **NATO Rescue** | German emergency services | `15 1430 JAN 25` |

### 🌍 Standard Time

| Calendar | Description | Format Example |
|----------|-------------|----------------|
| **Timezone** | Any Earth timezone | `14:30:45 CEST` |

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

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for **Alternative Time Systems**
4. Follow the configuration wizard
5. Select the desired time systems
6. Click Submit

You can create multiple instances with different configurations:
- **World Clock**: Multiple instances with different time zones
- **Thematic Groups**: Sci-Fi, Fantasy, Historical, Military
- **Room-based**: Different time systems for different rooms

## 📊 Entities Created

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

## 🎨 Dashboard Examples

### Fantasy & Gaming Worlds Dashboard

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

### Mars Mission Control Dashboard

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

## 🤖 Automation Examples

### Tamriel Holiday Notification

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

### Death Says (Discworld)

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

### EVE Online Daily Reset

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

## 📈 Performance

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

## 🛠️ Troubleshooting

### Integration Not Loading

```bash
# Check folder structure
ls -la /config/custom_components/alternative_time/
# Should contain:
# __init__.py, manifest.json, config_flow.py, sensor.py, const.py, translations/
```

### No Sensors Created

- Check logs: Settings → System → Logs
- Ensure at least one time system is enabled
- Clear cache: `find /config -name "__pycache__" -exec rm -rf {} +`
- Restart Home Assistant

### Async Call Warning

The integration uses asynchronous operations. If warning persists:
```bash
ha core restart
```

## 📝 Changelog

### v2.5.0.8 (Current)
- ✨ All 24 time systems fully integrated
- 🎮 Complete fantasy and gaming calendar collection
- 🏺 Extensive historical calendar support
- 🔴 Full Mars colonization time support
- 🌏 Asian cultural calendars included
- 🎖️ Military time formats complete
- 🐛 Performance optimizations
- 📚 Comprehensive documentation

### Previous Versions
- Added Tamriel Calendar (Elder Scrolls)
- Added Egyptian Calendar with hieroglyphs
- Added Discworld Calendar with Terry Pratchett humor
- Added EVE Online Time (New Eden Standard Time)
- Added complete Tolkien time systems (Shire & Imladris)
- Added Darian Calendar and Mars Time with 24 zones
- Added Suriyakati (Thai) and Minguo (Taiwan) calendars
- Added Attic Calendar (Ancient Athens)
- Added NATO time formats (3 variants)
- Added Maya Calendar with Long Count
- Added French Revolutionary decimal time
- Added Hexadecimal time
- Initial release with basic time systems

## 🤝 Contributing

Contributions are welcome!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/NewTimeSystem`)
3. Commit your changes (`git commit -m 'Add: New time system'`)
4. Push to the branch (`git push origin feature/NewTimeSystem`)
5. Open a Pull Request

### 🔧 Create Your Own Calendar Plugin

Want to add your own time system? It's easy! 

1. **Copy an existing calendar as template** from `/custom_components/alternative_time/calendars/`
2. **Modify the calculation logic** for your time system
3. **Place your new calendar file** in the `/calendars/` folder - it will be dynamically loaded
4. **Include translations** directly in your plugin file
5. **Test your implementation** thoroughly
6. **Submit a Pull Request** with your new calendar system

Example structure for a new calendar plugin:
```python
class YourCustomCalendar:
    def __init__(self):
        self.name = "Your Calendar Name"
        
    def get_current_time(self):
        # Your time calculation logic here
        return formatted_time_string
```

Check existing calendars in the `/calendars/` folder for detailed examples! The plugins are dynamically loaded - no configuration changes needed.

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.


## 📚 Resources

- **Issues**: [GitHub Issues](https://github.com/Lexorius/alternative_time/issues)

## 🔗 References

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

Made with ❤️ by [Lexorius](https://github.com/Lexorius)


*Translated with [Claude.ai](https://claude.ai)*