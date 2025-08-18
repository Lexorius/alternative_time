"""Traditional Chinese Lunisolar Calendar implementation - Version 1.0."""
from __future__ import annotations

from datetime import datetime, date
import logging
from typing import Dict, Any

from homeassistant.core import HomeAssistant

# Import base class
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from ..sensor import AlternativeTimeSensorBase
except ImportError:
    from sensor import AlternativeTimeSensorBase

_LOGGER = logging.getLogger(__name__)

# Try to import lunarcalendar library
try:
    from lunarcalendar import Converter, Solar, Lunar
    HAS_LUNAR = True
except ImportError:
    HAS_LUNAR = False
    _LOGGER.warning("lunarcalendar not installed. Install with: pip install LunarCalendar")

# ============================================
# CALENDAR METADATA
# ============================================

# Update interval in seconds (3600 = 1 hour, changes daily)
UPDATE_INTERVAL = 3600

# Complete calendar information for auto-discovery
CALENDAR_INFO = {
    "id": "chinese_lunar",
    "version": "1.0.0",
    "icon": "mdi:yin-yang",
    "category": "cultural",
    "accuracy": "official",
    "update_interval": UPDATE_INTERVAL,
    
    # Multi-language names
    "name": {
        "en": "Chinese Lunar Calendar",
        "de": "Chinesischer Mondkalender",
        "es": "Calendario Lunar Chino",
        "fr": "Calendrier Lunaire Chinois",
        "it": "Calendario Lunare Cinese",
        "nl": "Chinese Maankalender",
        "pt": "Calendário Lunar Chinês",
        "ru": "Китайский лунный календарь",
        "ja": "中国旧暦",
        "zh": "农历",
        "ko": "중국 음력"
    },
    
    # Short descriptions for UI
    "description": {
        "en": "Traditional Chinese lunisolar calendar with zodiac and festivals",
        "de": "Traditioneller chinesischer Lunisolarkalender mit Tierkreiszeichen und Festen",
        "es": "Calendario lunisolar chino tradicional con zodiaco y festivales",
        "fr": "Calendrier lunisolaire chinois traditionnel avec zodiaque et festivals",
        "it": "Calendario lunisolare cinese tradizionale con zodiaco e festival",
        "nl": "Traditionele Chinese lunisolaire kalender met dierenriem en festivals",
        "pt": "Calendário lunissolar chinês tradicional com zodíaco e festivais",
        "ru": "Традиционный китайский лунно-солнечный календарь с зодиаком и праздниками",
        "ja": "干支と祭日を含む伝統的な中国の太陰太陽暦",
        "zh": "传统农历，包含生肖、节气和节日",
        "ko": "띠와 명절이 포함된 전통 중국 음력"
    },
    
    # Chinese calendar specific data
    "chinese_data": {
        # Heavenly Stems (天干)
        "heavenly_stems": [
            {"cn": "甲", "pinyin": "jiǎ", "element": "Wood", "yin_yang": "Yang"},
            {"cn": "乙", "pinyin": "yǐ", "element": "Wood", "yin_yang": "Yin"},
            {"cn": "丙", "pinyin": "bǐng", "element": "Fire", "yin_yang": "Yang"},
            {"cn": "丁", "pinyin": "dīng", "element": "Fire", "yin_yang": "Yin"},
            {"cn": "戊", "pinyin": "wù", "element": "Earth", "yin_yang": "Yang"},
            {"cn": "己", "pinyin": "jǐ", "element": "Earth", "yin_yang": "Yin"},
            {"cn": "庚", "pinyin": "gēng", "element": "Metal", "yin_yang": "Yang"},
            {"cn": "辛", "pinyin": "xīn", "element": "Metal", "yin_yang": "Yin"},
            {"cn": "壬", "pinyin": "rén", "element": "Water", "yin_yang": "Yang"},
            {"cn": "癸", "pinyin": "guǐ", "element": "Water", "yin_yang": "Yin"}
        ],
        
        # Earthly Branches (地支) with Zodiac Animals
        "earthly_branches": [
            {"cn": "子", "pinyin": "zǐ", "animal": "Rat", "emoji": "🐀"},
            {"cn": "丑", "pinyin": "chǒu", "animal": "Ox", "emoji": "🐂"},
            {"cn": "寅", "pinyin": "yín", "animal": "Tiger", "emoji": "🐅"},
            {"cn": "卯", "pinyin": "mǎo", "animal": "Rabbit", "emoji": "🐇"},
            {"cn": "辰", "pinyin": "chén", "animal": "Dragon", "emoji": "🐉"},
            {"cn": "巳", "pinyin": "sì", "animal": "Snake", "emoji": "🐍"},
            {"cn": "午", "pinyin": "wǔ", "animal": "Horse", "emoji": "🐴"},
            {"cn": "未", "pinyin": "wèi", "animal": "Goat", "emoji": "🐐"},
            {"cn": "申", "pinyin": "shēn", "animal": "Monkey", "emoji": "🐵"},
            {"cn": "酉", "pinyin": "yǒu", "animal": "Rooster", "emoji": "🐓"},
            {"cn": "戌", "pinyin": "xū", "animal": "Dog", "emoji": "🐕"},
            {"cn": "亥", "pinyin": "hài", "animal": "Pig", "emoji": "🐖"}
        ],
        
        # Chinese months
        "months": [
            "正月", "二月", "三月", "四月", "五月", "六月",
            "七月", "八月", "九月", "十月", "冬月", "腊月"
        ],
        
        # Chinese numbers for days
        "day_names": [
            "初一", "初二", "初三", "初四", "初五", "初六", "初七", "初八", "初九", "初十",
            "十一", "十二", "十三", "十四", "十五", "十六", "十七", "十八", "十九", "二十",
            "廿一", "廿二", "廿三", "廿四", "廿五", "廿六", "廿七", "廿八", "廿九", "三十"
        ],
        
        # Major traditional festivals (lunar dates)
        "festivals": {
            (1, 1): {"name": "春节", "english": "Spring Festival", "emoji": "🧧"},
            (1, 15): {"name": "元宵节", "english": "Lantern Festival", "emoji": "🏮"},
            (2, 2): {"name": "龙抬头", "english": "Dragon Raises Head", "emoji": "🐲"},
            (5, 5): {"name": "端午节", "english": "Dragon Boat Festival", "emoji": "🛶"},
            (7, 7): {"name": "七夕节", "english": "Qixi Festival", "emoji": "💑"},
            (7, 15): {"name": "中元节", "english": "Ghost Festival", "emoji": "👻"},
            (8, 15): {"name": "中秋节", "english": "Mid-Autumn Festival", "emoji": "🥮"},
            (9, 9): {"name": "重阳节", "english": "Double Ninth Festival", "emoji": "🍃"},
            (12, 8): {"name": "腊八节", "english": "Laba Festival", "emoji": "🥣"},
            (12, 23): {"name": "小年", "english": "Little New Year", "emoji": "🎊"}
        },
        
        # Solar terms (节气) - approximate dates
        "solar_terms": [
            {"name": "立春", "english": "Spring Begins", "month": 2, "day": 4},
            {"name": "雨水", "english": "Rain Water", "month": 2, "day": 19},
            {"name": "惊蛰", "english": "Insects Awaken", "month": 3, "day": 6},
            {"name": "春分", "english": "Spring Equinox", "month": 3, "day": 21},
            {"name": "清明", "english": "Clear and Bright", "month": 4, "day": 5},
            {"name": "谷雨", "english": "Grain Rain", "month": 4, "day": 20},
            {"name": "立夏", "english": "Summer Begins", "month": 5, "day": 6},
            {"name": "小满", "english": "Grain Buds", "month": 5, "day": 21},
            {"name": "芒种", "english": "Grain in Ear", "month": 6, "day": 6},
            {"name": "夏至", "english": "Summer Solstice", "month": 6, "day": 21},
            {"name": "小暑", "english": "Minor Heat", "month": 7, "day": 7},
            {"name": "大暑", "english": "Major Heat", "month": 7, "day": 23},
            {"name": "立秋", "english": "Autumn Begins", "month": 8, "day": 8},
            {"name": "处暑", "english": "End of Heat", "month": 8, "day": 23},
            {"name": "白露", "english": "White Dew", "month": 9, "day": 8},
            {"name": "秋分", "english": "Autumn Equinox", "month": 9, "day": 23},
            {"name": "寒露", "english": "Cold Dew", "month": 10, "day": 8},
            {"name": "霜降", "english": "Frost Descends", "month": 10, "day": 23},
            {"name": "立冬", "english": "Winter Begins", "month": 11, "day": 7},
            {"name": "小雪", "english": "Minor Snow", "month": 11, "day": 22},
            {"name": "大雪", "english": "Major Snow", "month": 12, "day": 7},
            {"name": "冬至", "english": "Winter Solstice", "month": 12, "day": 22},
            {"name": "小寒", "english": "Minor Cold", "month": 1, "day": 6},
            {"name": "大寒", "english": "Major Cold", "month": 1, "day": 20}
        ]
    },
    
    # Configuration options
    "config_options": {
        "show_zodiac": {
            "type": "boolean",
            "default": True,
            "description": {
                "en": "Show zodiac animal",
                "de": "Tierkreiszeichen anzeigen",
                "zh": "显示生肖"
            }
        },
        "show_festivals": {
            "type": "boolean",
            "default": True,
            "description": {
                "en": "Show traditional festivals",
                "de": "Traditionelle Feste anzeigen",
                "zh": "显示传统节日"
            }
        },
        "show_solar_terms": {
            "type": "boolean",
            "default": True,
            "description": {
                "en": "Show 24 solar terms",
                "de": "24 Solarterme anzeigen",
                "zh": "显示二十四节气"
            }
        },
        "display_format": {
            "type": "select",
            "default": "chinese",
            "options": ["chinese", "pinyin", "english", "mixed"],
            "description": {
                "en": "Display format",
                "de": "Anzeigeformat",
                "zh": "显示格式"
            }
        }
    }
}


class ChineseLunarCalendarSensor(AlternativeTimeSensorBase):
    """Sensor for displaying Traditional Chinese Lunisolar Calendar."""
    
    # Class-level update interval
    UPDATE_INTERVAL = 3600  # Update every hour
    
    def __init__(self, base_name: str, hass: HomeAssistant) -> None:
        """Initialize the Chinese Lunar calendar sensor."""
        super().__init__(base_name, hass)
        
        # Store CALENDAR_INFO as instance variable
        self._calendar_info = CALENDAR_INFO
        
        # Get translated name from metadata
        calendar_name = self._translate('name', 'Chinese Lunar Calendar')
        
        # Set sensor attributes
        self._attr_name = f"{base_name} {calendar_name}"
        self._attr_unique_id = f"{base_name}_chinese_lunar"
        self._attr_icon = CALENDAR_INFO.get("icon", "mdi:yin-yang")
        
        # Initialize configuration with defaults
        self._show_zodiac = True
        self._show_festivals = True
        self._show_solar_terms = True
        self._display_format = "chinese"
        
        # Chinese calendar data
        self._chinese_data = CALENDAR_INFO["chinese_data"]
        
        # Check if library is available
        if not HAS_LUNAR:
            _LOGGER.error("lunarcalendar library not installed. Please install it.")
            self._state = "Library Missing"
        
        _LOGGER.debug(f"Initialized Chinese Lunar Calendar sensor: {self._attr_name}")
    
    async def async_added_to_hass(self) -> None:
        """When entity is added to hass, load config and set up updates."""
        # Load plugin options if available
        options = self.get_plugin_options()
        
        if options:
            _LOGGER.debug(f"Chinese Lunar: Loading options: {options}")
            self._show_zodiac = options.get("show_zodiac", True)
            self._show_festivals = options.get("show_festivals", True)
            self._show_solar_terms = options.get("show_solar_terms", True)
            self._display_format = options.get("display_format", "chinese")
        
        # Call parent implementation for scheduling updates
        await super().async_added_to_hass()
    
    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes."""
        attrs = super().extra_state_attributes
        
        # Ensure attrs is a dictionary
        if attrs is None:
            attrs = {}
        
        # Add Chinese calendar-specific attributes
        if hasattr(self, '_chinese_date'):
            attrs.update(self._chinese_date)
            
            # Add description in user's language
            attrs["description"] = self._translate('description')
            
            # Add configuration
            attrs["show_zodiac"] = self._show_zodiac
            attrs["show_festivals"] = self._show_festivals
            attrs["show_solar_terms"] = self._show_solar_terms
            attrs["display_format"] = self._display_format
        
        return attrs
    
    def _get_stem_branch_year(self, year: int) -> Dict[str, Any]:
        """Calculate the Stem-Branch (干支) for a given year."""
        # The cycle starts from 1984 (甲子年)
        cycle_year = (year - 1984) % 60
        
        stem_index = cycle_year % 10
        branch_index = cycle_year % 12
        
        stem = self._chinese_data["heavenly_stems"][stem_index]
        branch = self._chinese_data["earthly_branches"][branch_index]
        
        return {
            "stem": stem,
            "branch": branch,
            "combined_cn": f"{stem['cn']}{branch['cn']}",
            "combined_pinyin": f"{stem['pinyin']}{branch['pinyin']}",
            "animal": branch["animal"],
            "emoji": branch["emoji"],
            "element": stem["element"],
            "yin_yang": stem["yin_yang"]
        }
    
    def _get_festival(self, lunar_month: int, lunar_day: int) -> Dict[str, str] | None:
        """Get festival for a given lunar date."""
        if not self._show_festivals:
            return None
        
        festival_key = (lunar_month, lunar_day)
        if festival_key in self._chinese_data["festivals"]:
            return self._chinese_data["festivals"][festival_key]
        return None
    
    def _get_solar_term(self, solar_date: date) -> Dict[str, str] | None:
        """Get solar term for a given solar date (approximate)."""
        if not self._show_solar_terms:
            return None
        
        for term in self._chinese_data["solar_terms"]:
            # Check if date is within 1 day of solar term
            if solar_date.month == term["month"]:
                if abs(solar_date.day - term["day"]) <= 1:
                    return term
        return None
    
    def _calculate_chinese_date(self, earth_date: datetime) -> Dict[str, Any]:
        """Calculate Chinese Lunar Calendar date from Gregorian date."""
        
        if not HAS_LUNAR:
            return {
                "error": "lunarcalendar library not installed",
                "full_display": "Library Missing - Install lunarcalendar"
            }
        
        try:
            # Convert to lunar date
            solar = Solar(earth_date.year, earth_date.month, earth_date.day)
            lunar = Converter.Solar2Lunar(solar)
            
            # Get stem-branch year
            stem_branch = self._get_stem_branch_year(lunar.year)
            
            # Get month and day names
            month_name = self._chinese_data["months"][lunar.month - 1]
            if lunar.isleap:
                month_name = f"闰{month_name}"
            
            day_name = self._chinese_data["day_names"][lunar.day - 1]
            
            # Check for festivals
            festival = self._get_festival(lunar.month, lunar.day)
            
            # Check for solar terms
            solar_term = self._get_solar_term(earth_date.date())
            
            # Build display string based on format
            if self._display_format == "chinese":
                date_str = f"{stem_branch['combined_cn']}年 {month_name}{day_name}"
            elif self._display_format == "pinyin":
                date_str = f"{stem_branch['combined_pinyin']} nián {lunar.month} yuè {lunar.day} rì"
            elif self._display_format == "english":
                date_str = f"Year of {stem_branch['animal']}, Month {lunar.month}, Day {lunar.day}"
            else:  # mixed
                date_str = f"{stem_branch['combined_cn']}({stem_branch['animal']})年 {month_name}{day_name}"
            
            # Add zodiac if enabled
            if self._show_zodiac:
                date_str = f"{stem_branch['emoji']} {date_str}"
            
            # Add festival if present
            if festival:
                date_str = f"{date_str} | {festival['emoji']} {festival['name']}({festival['english']})"
            
            # Add solar term if present
            if solar_term:
                date_str = f"{date_str} | {solar_term['name']}({solar_term['english']})"
            
            result = {
                "lunar_year": lunar.year,
                "lunar_month": lunar.month,
                "lunar_day": lunar.day,
                "is_leap_month": lunar.isleap,
                "stem_cn": stem_branch["stem"]["cn"],
                "branch_cn": stem_branch["branch"]["cn"],
                "stem_branch_cn": stem_branch["combined_cn"],
                "stem_branch_pinyin": stem_branch["combined_pinyin"],
                "zodiac_animal": stem_branch["animal"],
                "zodiac_emoji": stem_branch["emoji"],
                "element": stem_branch["element"],
                "yin_yang": stem_branch["yin_yang"],
                "month_cn": month_name,
                "day_cn": day_name,
                "festival": festival["name"] if festival else "",
                "festival_english": festival["english"] if festival else "",
                "solar_term": solar_term["name"] if solar_term else "",
                "solar_term_english": solar_term["english"] if solar_term else "",
                "gregorian_date": earth_date.strftime("%Y-%m-%d"),
                "full_display": date_str
            }
            
            return result
            
        except Exception as e:
            _LOGGER.error(f"Error calculating Chinese date: {e}")
            return {
                "error": str(e),
                "full_display": f"Error: {e}"
            }
    
    def update(self) -> None:
        """Update the sensor."""
        now = datetime.now()
        self._chinese_date = self._calculate_chinese_date(now)
        
        # Set state to formatted date
        self._state = self._chinese_date.get("full_display", "Unknown")
        
        _LOGGER.debug(f"Updated Chinese Lunar Calendar to {self._state}")