# Alternative Time Systems for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/Lexorius/alternative_time.svg)](https://github.com/Lexorius/alternative_time/releases)
[![GitHub Activity](https://img.shields.io/github/commit-activity/y/Lexorius/alternative_time.svg)](https://github.com/Lexorius/alternative_time/commits/main)
[![License](https://img.shields.io/github/license/Lexorius/alternative_time.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-2.6.0.1-blue)](https://github.com/Lexorius/alternative_time)

A comprehensive Home Assistant integration providing **30+ alternative time systems** from science, science fiction, fantasy, history, religion, and various cultures.

## 🎯 Overview

- 🌙 **Lunar Time** (Relativistic Moon time based on LTE440 ephemeris)
- ⭐ **Stellar Distances** (Real-time distances to stars & pulsars with accuracy data)
- 🪐 **Solar System Tracker** (Real-time planetary positions with visual maps)
- 🚀 **Science Fiction** (Star Trek, Star Wars, EVE Online, Warhammer 40K)
- 🧙 **Fantasy Worlds** (Tolkien, Elder Scrolls, Discworld, Warcraft)
- 🏛️ **Historical Calendars** (Maya, Egyptian, Attic, Roman, French Revolutionary)
- 🔴 **Mars Colonization** (Darian Calendar, Mars Time Zones)
- 🌏 **Cultural Calendars** (Islamic, Thai, Taiwanese, Chinese, Japanese, Hindu, Ethiopian)
- 💻 **Technical Formats** (Unix, Hexadecimal, Julian Date, Swatch, TAI, UT1)
- 🎖️ **Military Systems** (NATO DTG in multiple formats)

## ✨ New in Version 2.5.2.180

### 🌙 Lunar Coordinate Time (TCL)
Actual lunar clock time based on the LTE440 Lunar Time Ephemeris.

| Parameter | Value |
|-----------|-------|
| Display | `14:30:45 TCL` (actual Moon time) |
| Daily Drift | ~56.7 µs/day (Moon clock runs faster) |
| Accumulated | ~1-2 ms since J2000.0 epoch |
| Accuracy | <0.15 ns until 2050 |
| Scientific Basis | JPL DE440, IAU 2024 Resolution II |

**Features:**
- Shows actual TCL time (what a clock on the Moon would show)
- Multiple display formats: Time, DateTime, Time+Drift, Drift only
- Relativistic calculation (general + special relativity)
- 13 periodic variation terms from orbital mechanics
- Based on peer-reviewed research (Lu, Yang & Xie, A&A 704, A76, 2025)

**Reference:** [DOI: 10.1051/0004-6361/202557345](https://doi.org/10.1051/0004-6361/202557345)

---

## 🌟 Available Time Systems

### 🌙 Lunar Time

#### **Lunar Coordinate Time (TCL)** 🆕
- **ID**: `lunar_tcl`
- **Format**: `14:30:45 TCL` or `2026-01-24 14:30:45 TCL`
- **Features**:
  - Actual lunar clock time (UTC + relativistic drift)
  - Relativistic time dilation between Earth and Moon
  - Based on LTE440 ephemeris (JPL DE440)
  - Daily drift ~56.7 µs (Moon clock runs faster)
  - Accumulated difference since epoch (currently ~1-2 ms)
  - IAU 2024 Resolution II compliant
  - Scientific reference: Lu, Yang & Xie (2025), A&A 704, A76
- **Display options**: TCL Time, TCL DateTime, TCL+Drift, Daily Drift (µs), Accumulated (ms)
- **Update**: Every 60 seconds

#### **ESA Lunar Time (LTC)**
- **ID**: `lunar_time`
- **Format**: `LTC 14:30:45 | 🌓 Day 8`
- **Features**:
  - ESA's proposed Lunar Time Coordinated system
  - Lunar timezones (Apollo, Chang'e, Luna landing sites)
  - Moon phase display
  - Time dilation indicator (56 µs/day)
- **Update**: Every 60 seconds

### ⭐ Stellar Distances

#### **Stellar Distance Calculator**
Real-time distances to notable stars and pulsars with measurement accuracy.

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

### 🪐 Solar System

#### **Solar System Tracker**
- **Features**: Real-time planetary positions, visual orbit maps
- **Update**: Hourly

### 🚀 Science Fiction

#### **Stardate (Star Trek TNG)**
- **Format**: `[41]XXX.X` (e.g., `[41]986.0`)
- **Features**: TNG-style calculation, configurable year offset
- **Update**: Every 10 seconds

#### **Star Wars Galactic Calendar**
- **Format**: `35:3:21 GrS | Taungsday | Expansion Week`
- **Features**: Galactic Standard Calendar, 10 months, 7 weeks, 5 days per week, 368-day year
- **Update**: Hourly

#### **EVE Online Time**
- **Format**: `YC 127.03.15 14:30:45`
- **Features**: New Eden Standard Time, YC dating
- **Update**: Every second

#### **Warhammer 40K Imperial Dating**
- **Format**: `0.523.025.M42`
- **Features**: Check number, year fraction, millennium designation
- **Update**: Every 5 minutes

### 🧙 Fantasy Calendars

#### **Middle-earth Collection**
- **Shire Calendar**: Hobbit time with 7 meals
- **Calendar of Imladris**: Elvish 6-season year
- **Calendar of Gondor**: Númenórean system

#### **Elder Scrolls (Tamriel)**
- **Format**: `4E 201, 17 Last Seed (Fredas)`
- **Features**: 8-day weeks, Divine blessings, Daedric influence
- **Update**: Hourly

#### **Discworld Calendar**
- **Format**: `Century of the Anchovy, UC 25, 32 Offle`
- **Features**: Impossible dates (32nd of months), Guild influences, L-Space anomalies
- **Update**: Hourly

#### **World of Warcraft Calendar**
- **Format**: `Year 35, Day of the Wisp, 4th of Deepwood`
- **Features**: Azeroth dates, seasonal events, moon phases
- **Update**: Hourly

### 🏛️ Historical Calendars

#### **Ancient Egyptian**
- **Format**: `Dynasty 1 Year 25, 𓊖 15 Thoth`
- **Features**: Hieroglyphic numbers, 3 seasons, Nile status
- **Update**: Hourly

#### **Maya Long Count**
- **Format**: `13.0.12.1.15 | 8 Ahau | 3 Pop`
- **Features**: Long Count, Tzolk'in, Haab calendars
- **Update**: Hourly

#### **Roman Calendar**
- **Format**: `a.d. XVII Kal. Ian. MMDCCLXXVIII A.U.C.`
- **Features**: Kalends, Nones, Ides system, Roman numerals, A.U.C. dating
- **Update**: Hourly

#### **Attic Calendar**
- **Format**: `5 histamenou Hekatombaion | Ol.700.2`
- **Features**: Archon years, Olympiad counting
- **Update**: Hourly

#### **French Revolutionary Calendar**
- **Features**: Decimal time (10 hours/day, 100 minutes/hour), Revolutionary months
- **Update**: Every second

### ☪️ Religious Calendars

#### **Islamic (Hijri) Calendar**
- **Format**: `15 Ramadan 1447 AH`
- **Features**: Tabular calculation, Arabic month names, Islamic holidays
- **Update**: Hourly

#### **Hebrew Calendar**
- **Format**: `15 Tishrei 5785`
- **Features**: Jewish holidays, Sabbath indication
- **Update**: Hourly

#### **Chinese Calendar**
- **Format**: `甲辰年 十月 十五 | Wood Dragon`
- **Features**: Lunar calendar, Zodiac animals, Heavenly stems & Earthly branches
- **Update**: Hourly

### 🌍 Cultural Calendars

#### **Suriyakati (Thai Buddhist)**
- **Format**: `๒๕ ธันวาคม ๒๕๖๘`
- **Features**: Buddhist Era (BE = CE + 543), Thai numerals
- **Update**: Hourly

#### **Minguo (Taiwan/ROC)**
- **Format**: `民國114年 十二月 二十五日`
- **Features**: Republic Era (Year 1 = 1912 CE)
- **Update**: Hourly

#### **Japanese Era Calendar**
- **Format**: `令和7年1月24日`
- **Features**: Imperial era names, Japanese holidays, Rokuyou
- **Update**: Hourly

#### **Hindu Panchang**
- **Features**: Tithi, Nakshatra, Yoga, Karana, festivals
- **Update**: Hourly

#### **Ge'ez (Ethiopian) Calendar**
- **Format**: `15 መስከረም 2017` or `፲፭ መስከረም ፳፻፲፯`
- **Features**: 13-month calendar, native Ge'ez script and numerals
- **Update**: Hourly

### 🔴 Mars Time Systems

#### **Darian Calendar**
- **Format**: `Sol 15 Gemini 217`
- **Features**: 24 months, 668 sols per year
- **Update**: Hourly

#### **Mars Time with Zones**
- **Format**: `14:25:30 Olympus Mons | Sol 234/MY36`
- **Features**: 24 Mars timezones, mission sol tracking
- **Update**: Every 30 seconds

### 💻 Technical Formats

#### **Unix Timestamp**
- **Format**: `1735689600`
- **Update**: Every second

#### **Swatch Internet Time**
- **Format**: `@500.00`
- **Features**: 1000 .beats per day
- **Update**: Every second

#### **Hexadecimal Time**
- **Format**: `A.F3.C8`
- **Update**: Every 5 seconds

#### **Julian Date**
- **Format**: `2460678.50000`
- **Update**: Every 30 seconds

#### **TAI (International Atomic Time)**
- **Format**: `2026-01-24T00:36:52 TAI`
- **Features**: Continuous atomic timescale, leap second history
- **Update**: Every second

#### **UT1 (Universal Time 1)**
- **Format**: `2026-01-24T00:43:31.767 UT1`
- **Features**: Earth rotation time, IERS API integration
- **Update**: Configurable (5 min to 24 hours)

### 🎖️ Military Systems

#### **NATO Date-Time Group**
- **German Format**: `241530AJAN26`
- **US/UK Format**: `241530Z JAN 26`
- **Features**: Multiple timezone designators, configurable formats

---

## 📦 Installation

### Via HACS (Recommended)

1. Open HACS in your Home Assistant
2. Click the three dots → "Custom repositories"
3. Add URL: `https://github.com/Lexorius/alternative_time`
4. Select "Integration" as category
5. Click "Add"
6. Search for "Alternative Time Systems" and install
7. Restart Home Assistant

### Manual Installation

1. Download the `alternative_time` folder from the repository
2. Copy to `/config/custom_components/`
3. Restart Home Assistant

---

## ⚙️ Configuration

### Via User Interface (Config Flow 2.5)

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for **Alternative Time Systems**
4. Follow the configuration wizard:
   - **Step 1**: Name your instance
   - **Step 2**: Select categories (Technical, Historical, Cultural, Space, etc.)
   - **Step 3**: Choose calendars from each category
   - **Step 4**: Configure calendar-specific options

---

## 🎨 Architecture

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
- **space**: Lunar TCL, ESA Lunar Time, Solar System, Stellar Distances, Mars calendars
- **technical**: Unix, Swatch, Hexadecimal, Decimal, TAI, UT1
- **historical**: Egyptian, Maya, Roman, Attic
- **cultural**: Thai, Taiwan, Chinese, Japanese, Ethiopian
- **religious**: Islamic, Hebrew
- **fantasy**: Middle-earth, Tamriel, Discworld
- **scifi**: Star Trek, Star Wars, EVE, Warhammer

---

## 🚀 Performance Optimization

| Category | Update Interval | Calendars |
|----------|-----------------|-----------|
| Real-time | 1 second | Unix, Swatch, TAI |
| Near real-time | 5-10 seconds | Hexadecimal, Stardate |
| Time-based | 30-60 seconds | Mars Time, Julian Date, Lunar Time |
| Date-based | 1 hour | Calendar systems, Stellar Distances |
| Event-based | 5 minutes | Warhammer 40K |

---

## 📈 Version History

### v2.6.0.1 (Current)
- 🧹 **Code cleanup**: all calendar plugin files are now ruff-clean (E, F, W, I — `--ignore E501`)
- 🐛 **Bare excepts** in `dtg.py`, `german_rescue_dtg.py`, `mars.py`, `hindu_panchang.py`, `japanese_era.py`, `japanese_lunar.py`, `stellar_distances.py` replaced with `except Exception:`
- 🗑️ **Dead variables** removed in `geez.py`, `japanese_lunar.py`, `lunar_tcl.py`, `maya.py`, `solar_system.py`, `star_wars.py`
- 🔑 **Duplicate dict key** `"holidays"` in `star_wars.py` resolved
- 📦 **Unused import** `Lunar` removed from `chinese_lunar.py`
- ✂️ **One-line if/else statements** in `stellar_distances.py` split into multi-line form
- 🔧 **`scripts/bump-version.sh`**: now supports 4-component versions (`x.y.z.b`) and a new `build` subcommand that increments only the 4th component

### v2.5.2.180
- 🌙 **Lunar Coordinate Time (TCL)**: New plugin `lunar_tcl.py` showing actual lunar clock time
- 🕐 **TCL Time Display**: Shows what time it would be on the Moon (`14:30:45 TCL`)
- ⏱️ **LTE440 Ephemeris**: Based on JPL DE440, scientific accuracy <0.15 ns until 2050
- 📊 **Daily drift**: ~56.7 µs/day (Moon clock faster than Earth)
- 📈 **13 periodic terms**: Annual (~1.65 ms), monthly (~126 µs), and 11 minor terms
- 🔬 **Scientific basis**: Lu, Yang & Xie (2025), Astronomy & Astrophysics 704, A76
- 📐 **IAU compliant**: IAU 2024 Resolution II (LCRS/TCL standard)
- 🌙 **ESA Lunar Time**: Updated config options with emoji labels for landing sites
- 🛠️ **Config Flow Fix**: Fixed dropdown labels for select options

### v2.5.2.170
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

---

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

---

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

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.

---

## 📮 Support

- **Bug Reports**: [GitHub Issues](https://github.com/Lexorius/alternative_time/issues)
- **Feature Requests**: Open a GitHub issue with [Enhancement] tag

---

## 🔗 Links

- [GitHub Repository](https://github.com/Lexorius/alternative_time)
- [HACS](https://hacs.xyz/)
- [Home Assistant](https://www.home-assistant.io/)

---

**Version 2.6.0.1**
