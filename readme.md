# Alternative Time Systems for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/Lexorius/alternative_time.svg)](https://github.com/Lexorius/alternative_time/releases)
[![GitHub Activity](https://img.shields.io/github/commit-activity/y/Lexorius/alternative_time.svg)](https://github.com/Lexorius/alternative_time/commits/main)
[![License](https://img.shields.io/github/license/Lexorius/alternative_time.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-2.5.2.170-blue)](https://github.com/Lexorius/alternative_time)

A comprehensive Home Assistant integration providing **30+ alternative time systems** from science, science fiction, fantasy, history, religion, and various cultures. Transform your Home Assistant into a universal time machine!

## 🎯 Overview

Transform your Home Assistant into a multiversal clock supporting:
- ⭐ **Stellar Distances** (Real-time distances to stars & pulsars with accuracy data)
- 🪐 **Solar System Tracker** (Real-time planetary positions with visual maps)
- 🚀 **Science Fiction** (Star Trek, Star Wars, EVE Online, Warhammer 40K)
- 🧙 **Fantasy Worlds** (Tolkien, Elder Scrolls, Discworld, Warcraft)
- 🏛️ **Historical Calendars** (Maya, Egyptian, Attic, Roman, French Revolutionary)
- 🔴 **Mars Colonization** (Darian Calendar, Mars Time Zones)
- 🌏 **Cultural Calendars** (Islamic, Thai, Taiwanese, Chinese, Japanese, Hindu, Ethiopian)
- 💻 **Technical Formats** (Unix, Hexadecimal, Julian Date, Swatch, TAI, UT1)
- 🎖️ **Military Systems** (NATO DTG in multiple formats)

## ✨ New in Version 2.5.2.170

### ⭐ Stellar Distances Calculator 🆕
Real-time distances to notable stars and pulsars with measurement accuracy!

**7 Stars:**
| Star | Distance | Accuracy | Note |
|------|----------|----------|------|
| Proxima Centauri | 4.24 ly | ±0.006% | Nearest star |
| Barnard's Star | 5.95 ly | ±0.007% | Fastest proper motion (10.3"/yr) |
| Scholz's Star | 22.2 ly | ±0.17% | Passed Oort Cloud 70,000 years ago |
| Ross 248 | 10.3 ly | ±0.27% | Will be nearest in 36,000 years |
| Gliese 710 | 62.5 ly | ±0.05% | Collision course - 10,600 AU in 1.35 Myr |
| Polaris | 433 ly | ±1.5% | North Star |
| Betelgeuse | 723 ly | ±18% | Supernova candidate |

**6 Nearest Pulsars:**
| Pulsar | Distance | Accuracy | Note |
|--------|----------|----------|------|
| PSR J0437-4715 | 511 ly | ±0.06% | Nearest millisecond pulsar (173 rot/sec) |
| PSR J0108-1431 | 424 ly | ±13% | Oldest nearby (166 Myr) |
| Vela Pulsar | 932 ly | ±6% | Brightest radio pulsar |
| Geminga | 815 ly | ±32% | First gamma-ray pulsar |
| PSR B0656+14 | 940 ly | ±10% | "Three Musketeers" pulsar |
| PSR B0950+08 | 906 ly | ±8% | Old pulsar in Leo (17.5 Myr) |

**Features:**
- Real-time distance calculation using parallax + radial velocity
- Measurement uncertainty (±%) for each object
- Distance range (min-max) based on parallax error
- Accuracy ratings: excellent / very good / good / moderate / uncertain
- Data sources: Gaia DR3, VLBI parallax, Pulsar Timing
- Approaching/receding motion indicator
- 12 languages supported

### Previous Updates (2.5.2.165)

#### 🕐 TAI - International Atomic Time
- **Continuous atomic timescale**: No leap seconds
- **Related time systems**: GPS Time, Terrestrial Time (TT)
- **Leap second history**: Complete since 1972
- **Example**: `2026-01-05T00:36:52 TAI`

#### 🌍 UT1 - Universal Time 1
- **Earth rotation time**: Based on actual Earth rotation
- **IERS REST API integration**: Real-time DUT1 values
- **Intelligent caching**: Configurable 5 min to 24 hours
- **Example**: `2026-01-05T00:43:31.767 UT1`

#### ✝️ Ge'ez (Ethiopian) Calendar
- **13-month calendar**: 12 × 30 days + Pagume (5-6 days)
- **Native script support**: Ge'ez/Amharic month and weekday names
- **Ge'ez numerals**: Ethiopian number system (፩፪፫...)
- **Example**: `15 መስከረም 2017` or `፲፭ መስከረም ፳፻፲፯`

#### 🪐 Solar System Improvements
- **"You are here" marker**: Earth position clearly marked
- **Corrected month orientation**: January now at top
- **Improved planet positions**: More accurate calculations

## 📦 Installation

### Via HACS (Recommended)

1. Open HACS in your Home Assistant
2. Click the three dots in the top right corner
3. Select "Custom repositories"
4. Add URL: `https://github.com/Lexorius/alternative_time`
5. Select "Integration" as category
6. Click "Add"
7. Search for "Alternative Time Systems" and install
8. Restart Home Assistant

### Manual Installation

1. Download the `alternative_time` folder from the repository
2. Copy it to your `/config/custom_components/` directory
3. Restart Home Assistant

## ⚙️ Configuration

### Via User Interface (Config Flow 2.5)

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for **Alternative Time Systems**
4. Follow the enhanced configuration wizard:
   - **Step 1**: Name your instance
   - **Step 2**: Select categories (Technical, Historical, Cultural, Space, etc.)
   - **Step 3**: Choose calendars from each category
   - **Step 4**: Configure calendar-specific options
5. Done! Your sensors will appear automatically

## 🎨 Version 2.5 Architecture

### Standardized Calendar Format
Each calendar follows the unified `CALENDAR_INFO` structure:
- **Metadata**: ID, version, icon, category, accuracy
- **Multi-language**: Names and descriptions in 12 languages
- **Calendar Data**: Months, weeks, special dates, events
- **Configuration Options**: Customizable per calendar
- **Update Intervals**: Optimized for each calendar type

### Supported Languages
🇬🇧 English (en) | 🇩🇪 Deutsch (de) | 🇪🇸 Español (es) | 🇫🇷 Français (fr) | 🇮🇹 Italiano (it) | 🇳🇱 Nederlands (nl) | 🇵🇱 Polski (pl) | 🇵🇹 Português (pt) | 🇷🇺 Русский (ru) | 🇯🇵 日本語 (ja) | 🇨🇳 中文 (zh) | 🇰🇷 한국어 (ko)

### Categories
- **space**: Solar System, Stellar Distances, Mars calendars
- **technical**: Unix, Swatch, Hexadecimal, Decimal, TAI, UT1
- **historical**: Egyptian, Maya, Roman, Attic
- **cultural**: Thai, Taiwan, Chinese, Ethiopian
- **religious**: Islamic, Hebrew
- **fantasy**: Middle-earth, Tamriel, Discworld
- **scifi**: Star Trek, Star Wars, EVE, Warhammer

## 🚀 Performance Optimization

| Category | Update Interval | Calendars |
|----------|-----------------|-----------|
| Real-time | 1 second | Unix, Swatch, Timezones |
| Near real-time | 5-10 seconds | Hexadecimal, Stardate |
| Time-based | 30-60 seconds | Mars Time, Julian Date |
| Date-based | 1 hour | Calendar systems, Stellar Distances |
| Event-based | 5 minutes | Warhammer 40K |

## 📈 Version History

### v2.5.2.170 (Current) 🆕
- ⭐ **Stellar Distances Calculator**: Real-time distances to 7 stars & 6 pulsars
- 📊 **Measurement Accuracy**: Uncertainty percentages for all objects
- 📏 **Distance Ranges**: Min-max based on parallax errors
- 🎯 **Accuracy Ratings**: excellent/very good/good/moderate/uncertain
- 📡 **Data Sources**: Gaia DR3, VLBI, Pulsar Timing

### v2.5.2.165
- 🕐 **TAI**: International Atomic Time
- 🌍 **UT1**: Universal Time 1 with IERS API
- ✝️ **Ge'ez Calendar**: Ethiopian calendar with native script
- 🪐 **Solar System**: Improved positioning

### v2.5.0
- ⚡ **Complete Architecture Rewrite**
- 🎨 **Standardized Calendar Format**
- 🌍 **Multi-language Support** (12 languages)
- 📁 **Category-based Organization**
- ⚙️ **Enhanced Config Flow** with plugin options

### Previous Versions
- **v1.6.0**: Tamriel, Egyptian, Discworld calendars
- **v1.5.0**: EVE Online, Shire, Imladris calendars
- **v1.4.0**: Mars time systems
- **v1.3.0**: Asian calendars, Attic calendar
- **v1.2.0**: NATO time formats
- **v1.1.0**: Maya calendar, async improvements
- **v1.0.0**: Initial release

## 🛠️ Development

### Adding a New Calendar

1. Create `calendars/your_calendar.py`
2. Follow the standardized format (see existing calendars)
3. Include `CALENDAR_INFO` dictionary with all metadata
4. Implement sensor class extending `AlternativeTimeSensorBase`
5. Test thoroughly

### Minimal Calendar Template
```python
CALENDAR_INFO = {
    "id": "your_calendar",
    "version": "1.0.0",
    "icon": "mdi:calendar",
    "category": "technical",
    "update_interval": 3600,
    "name": {
        "en": "Your Calendar",
        "de": "Dein Kalender",
        # ... other languages
    },
    "description": {
        "en": "Calendar description",
        "de": "Kalenderbeschreibung",
        # ... other languages
    },
    "config_options": {
        "option_key": {
            "type": "boolean",
            "default": True,
            "label": {"en": "Option Label", "de": "Optionsbeschriftung"},
            "description": {"en": "Option description", "de": "Optionsbeschreibung"}
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

### Stellar Distances Issues
- All calculations are based on J2000.0 epoch data
- Uncertainty values come from parallax measurement errors
- Pulsars with unknown radial velocity show 0 km/s

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details

## 🙏 Acknowledgments

- Home Assistant Community for feedback and testing
- Gaia DR3 for stellar parallax data
- VLBI networks for pulsar distance measurements
- IERS for UT1 data services
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

**Version 2.5.2.170** - Made with ❤️ for the Home Assistant Community
