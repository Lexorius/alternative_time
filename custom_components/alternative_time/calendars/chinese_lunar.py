"""Chinese Lunar Calendar implementation - Version 2.6."""
from __future__ import annotations

from datetime import datetime
import logging
from typing import Dict, Any

from homeassistant.core import HomeAssistant
from ..sensor import AlternativeTimeSensorBase

_LOGGER = logging.getLogger(__name__)

# Try to import the lunar calendar library
try:
    from lunarcalendar import Converter, Solar, Lunar
    HAS_LUNAR = True
except ImportError:
    HAS_LUNAR = False
    _LOGGER.warning("lunarcalendar library not installed. Please install it with: pip install lunarcalendar")

# ============================================
# CALENDAR METADATA
# ============================================

# Update interval in seconds (3600 seconds = 1 hour for daily calendar)
UPDATE_INTERVAL = 3600

# Complete calendar information for auto-discovery
CALENDAR_INFO = {
    "id": "chinese_lunar",
    "version": "2.6.0",
    "icon": "mdi:yin-yang",
    "category": "cultural",
    "accuracy": "traditional",
    "update_interval": UPDATE_INTERVAL,
    
    # Multi-language names
    "name": {
        "en": "Chinese Lunar Calendar",
        "zh": "农历",
        "zh-tw": "農曆",
        "de": "Chinesischer Mondkalender",
        "es": "Calendario Lunar Chino",
        "fr": "Calendrier Lunaire Chinois",
        "it": "Calendario Lunare Cinese",
        "nl": "Chinese Maankalender",
        "pt": "Calendário Lunar Chinês",
        "ru": "Китайский лунный календарь",
        "ja": "中国太陰暦",
        "ko": "중국 음력"
    },
    
    # Short descriptions for UI
    "description": {
        "en": "Traditional Chinese lunar calendar with zodiac animals and festivals",
        "zh": "带有生肖和节日的传统农历",
        "zh-tw": "帶有生肖和節日的傳統農曆",
        "de": "Traditioneller chinesischer Mondkalender mit Tierkreiszeichen und Festen",
        "es": "Calendario lunar chino tradicional con animales del zodiaco y festivales",
        "fr": "Calendrier lunaire chinois traditionnel avec animaux du zodiaque et festivals",
        "it": "Calendario lunare cinese tradizionale con animali dello zodiaco e festival",
        "nl": "Traditionele Chinese maankalender met dierenriem en festivals",
        "pt": "Calendário lunar chinês tradicional com animais do zodíaco e festivais",
        "ru": "Традиционный китайский лунный календарь с животными зодиака и праздниками",
        "ja": "干支と祭りを含む伝統的な中国太陰暦",
        "ko": "띠 동물과 축제가 있는 전통 중국 음력"
    },
    
    # Chinese calendar data
    "chinese_data": {
        # Heavenly Stems (天干)
        "heavenly_stems": {
            "chinese": ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"],
            "pinyin": ["jiǎ", "yǐ", "bǐng", "dīng", "wù", "jǐ", "gēng", "xīn", "rén", "guǐ"],
            "elements": ["Wood", "Wood", "Fire", "Fire", "Earth", "Earth", "Metal", "Metal", "Water", "Water"],
            "yin_yang": ["Yang", "Yin", "Yang", "Yin", "Yang", "Yin", "Yang", "Yin", "Yang", "Yin"]
        },
        
        # Earthly Branches (地支)
        "earthly_branches": {
            "chinese": ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"],
            "pinyin": ["zǐ", "chǒu", "yín", "mǎo", "chén", "sì", "wǔ", "wèi", "shēn", "yǒu", "xū", "hài"],
            "zodiac": ["Rat", "Ox", "Tiger", "Rabbit", "Dragon", "Snake", "Horse", "Goat", "Monkey", "Rooster", "Dog", "Pig"],
            "zodiac_chinese": ["鼠", "牛", "虎", "兔", "龙", "蛇", "马", "羊", "猴", "鸡", "狗", "猪"],
            "hours": ["23-01", "01-03", "03-05", "05-07", "07-09", "09-11", "11-13", "13-15", "15-17", "17-19", "19-21", "21-23"]
        },
        
        # Chinese months
        "months": {
            "names": ["正月", "二月", "三月", "四月", "五月", "六月", 
                     "七月", "八月", "九月", "十月", "冬月", "腊月"],
            "english": ["First Month", "Second Month", "Third Month", "Fourth Month", "Fifth Month", "Sixth Month",
                       "Seventh Month", "Eighth Month", "Ninth Month", "Tenth Month", "Winter Month", "Twelfth Month"]
        },
        
        # Major festivals
        "festivals": {
            "1-1": {"chinese": "春节", "english": "Spring Festival (Chinese New Year)"},
            "1-15": {"chinese": "元宵节", "english": "Lantern Festival"},
            "5-5": {"chinese": "端午节", "english": "Dragon Boat Festival"},
            "7-7": {"chinese": "七夕", "english": "Qixi Festival (Chinese Valentine's Day)"},
            "7-15": {"chinese": "中元节", "english": "Ghost Festival"},
            "8-15": {"chinese": "中秋节", "english": "Mid-Autumn Festival"},
            "9-9": {"chinese": "重阳节", "english": "Double Ninth Festival"},
            "12-8": {"chinese": "腊八节", "english": "Laba Festival"}
        },
        
        # Solar terms (24 节气)
        "solar_terms": [
            {"chinese": "立春", "english": "Start of Spring", "approx": "Feb 4"},
            {"chinese": "雨水", "english": "Rain Water", "approx": "Feb 19"},
            {"chinese": "惊蛰", "english": "Awakening of Insects", "approx": "Mar 6"},
            {"chinese": "春分", "english": "Spring Equinox", "approx": "Mar 21"},
            {"chinese": "清明", "english": "Clear and Bright", "approx": "Apr 5"},
            {"chinese": "谷雨", "english": "Grain Rain", "approx": "Apr 20"},
            {"chinese": "立夏", "english": "Start of Summer", "approx": "May 6"},
            {"chinese": "小满", "english": "Grain Full", "approx": "May 21"},
            {"chinese": "芒种", "english": "Grain in Ear", "approx": "Jun 6"},
            {"chinese": "夏至", "english": "Summer Solstice", "approx": "Jun 21"},
            {"chinese": "小暑", "english": "Minor Heat", "approx": "Jul 7"},
            {"chinese": "大暑", "english": "Major Heat", "approx": "Jul 23"},
            {"chinese": "立秋", "english": "Start of Autumn", "approx": "Aug 8"},
            {"chinese": "处暑", "english": "End of Heat", "approx": "Aug 23"},
            {"chinese": "白露", "english": "White Dew", "approx": "Sep 8"},
            {"chinese": "秋分", "english": "Autumn Equinox", "approx": "Sep 23"},
            {"chinese": "寒露", "english": "Cold Dew", "approx": "Oct 8"},
            {"chinese": "霜降", "english": "Frost Descent", "approx": "Oct 23"},
            {"chinese": "立冬", "english": "Start of Winter", "approx": "Nov 8"},
            {"chinese": "小雪", "english": "Minor Snow", "approx": "Nov 22"},
            {"chinese": "大雪", "english": "Major Snow", "approx": "Dec 7"},
            {"chinese": "冬至", "english": "Winter Solstice", "approx": "Dec 22"},
            {"chinese": "小寒", "english": "Minor Cold", "approx": "Jan 6"},
            {"chinese": "大寒", "english": "Major Cold", "approx": "Jan 20"}
        ]
    },
    
    # Additional metadata
    "reference_url": "https://en.wikipedia.org/wiki/Chinese_calendar",
    "documentation_url": "https://www.timeanddate.com/calendar/chinese-calendar.html",
    "origin": "China",
    "created_by": "Ancient Chinese astronomers",
    "period": "Over 4000 years old",
    
    # Related calendars
    "related": ["gregorian", "vietnamese", "korean"],
    
    # Tags for searching and filtering
    "tags": [
        "lunar", "chinese", "traditional", "cultural", "zodiac",
        "festivals", "solar_terms", "agricultural", "astronomical"
    ],
    
    # Configuration options for this calendar
    "config_options": {
        "show_zodiac": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show Zodiac Animal",
                "zh": "显示生肖",
                "zh-tw": "顯示生肖",
                "de": "Tierkreiszeichen anzeigen",
                "es": "Mostrar animal del zodiaco",
                "fr": "Afficher l'animal du zodiaque",
                "it": "Mostra animale dello zodiaco",
                "nl": "Toon dierenriem dier",
                "pt": "Mostrar animal do zodíaco",
                "ru": "Показать животное зодиака",
                "ja": "干支を表示",
                "ko": "띠 동물 표시"
            },
            "description": {
                "en": "Display the zodiac animal for the current year",
                "zh": "显示当年的生肖动物",
                "de": "Zeige das Tierkreiszeichen für das aktuelle Jahr"
            }
        },
        "show_festivals": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show Festivals",
                "zh": "显示节日",
                "zh-tw": "顯示節日",
                "de": "Feste anzeigen",
                "es": "Mostrar festivales",
                "fr": "Afficher les festivals",
                "it": "Mostra festival",
                "nl": "Toon festivals",
                "pt": "Mostrar festivais",
                "ru": "Показать праздники",
                "ja": "祭りを表示",
                "ko": "축제 표시"
            },
            "description": {
                "en": "Display traditional Chinese festivals",
                "zh": "显示传统中国节日",
                "de": "Zeige traditionelle chinesische Feste"
            }
        },
        "show_solar_terms": {
            "type": "boolean", 
            "default": True,
            "label": {
                "en": "Show Solar Terms",
                "zh": "显示节气",
                "zh-tw": "顯示節氣",
                "de": "Sonnenterme anzeigen",
                "es": "Mostrar términos solares",
                "fr": "Afficher les termes solaires",
                "it": "Mostra termini solari",
                "nl": "Toon zonnetermen",
                "pt": "Mostrar termos solares",
                "ru": "Показать солнечные термины",
                "ja": "節気を表示",
                "ko": "절기 표시"
            },
            "description": {
                "en": "Display the 24 solar terms",
                "zh": "显示二十四节气",
                "de": "Zeige die 24 Sonnenterme"
            }
        },
        "display_format": {
            "type": "select",
            "default": "both",
            "options": ["chinese", "english", "both"],
            "label": {
                "en": "Display Format",
                "zh": "显示格式",
                "zh-tw": "顯示格式",
                "de": "Anzeigeformat",
                "es": "Formato de visualización",
                "fr": "Format d'affichage",
                "it": "Formato di visualizzazione",
                "nl": "Weergaveformaat",
                "pt": "Formato de exibição",
                "ru": "Формат отображения",
                "ja": "表示形式",
                "ko": "표시 형식"
            },
            "description": {
                "en": "Choose display language: Chinese characters, English, or both",
                "zh": "选择显示语言：中文、英文或两者",
                "de": "Wähle Anzeigesprache: Chinesische Zeichen, Englisch oder beides"
            }
        }
    }
}


class ChineseLunarCalendarSensor(AlternativeTimeSensorBase):
    """Sensor for displaying Chinese Lunar Calendar."""
    
    # Class-level update interval
    UPDATE_INTERVAL = UPDATE_INTERVAL
    
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
        
        # Initialize configuration with defaults from CALENDAR_INFO
        config_defaults = CALENDAR_INFO.get("config_options", {})
        self._show_zodiac = config_defaults.get("show_zodiac", {}).get("default", True)
        self._show_festivals = config_defaults.get("show_festivals", {}).get("default", True)
        self._show_solar_terms = config_defaults.get("show_solar_terms", {}).get("default", True)
        self._display_format = config_defaults.get("display_format", {}).get("default", "both")
        
        # Chinese calendar data
        self._chinese_data = CALENDAR_INFO["chinese_data"]
        
        # Flag to track if options have been loaded
        self._options_loaded = False
        
        # Initialize state
        self._state = None
        self._chinese_date = {}
        
        # Check if library is available
        if not HAS_LUNAR:
            _LOGGER.error("lunarcalendar library not installed. Please install it.")
            self._state = "Library Missing"
        
        _LOGGER.debug(f"Initialized Chinese Lunar Calendar sensor: {self._attr_name}")
    
    def _load_options(self) -> None:
        """Load plugin options after IDs are set."""
        if self._options_loaded:
            return
            
        try:
            options = self.get_plugin_options()
            if options:
                # Update configuration from plugin options
                self._show_zodiac = options.get("show_zodiac", self._show_zodiac)
                self._show_festivals = options.get("show_festivals", self._show_festivals)
                self._show_solar_terms = options.get("show_solar_terms", self._show_solar_terms)
                self._display_format = options.get("display_format", self._display_format)
                
                _LOGGER.debug(f"Chinese Lunar sensor loaded options: show_zodiac={self._show_zodiac}, "
                            f"show_festivals={self._show_festivals}, display_format={self._display_format}")
            else:
                _LOGGER.debug("Chinese Lunar sensor using default options - no custom options found")
                
            self._options_loaded = True
        except Exception as e:
            _LOGGER.debug(f"Chinese Lunar sensor could not load options yet: {e}")
    
    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        await super().async_added_to_hass()
        
        # Try to load options now that IDs should be set
        self._load_options()
    
    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes."""
        attrs = super().extra_state_attributes
        
        # Add Chinese calendar-specific attributes
        if self._chinese_date:
            attrs.update(self._chinese_date)
            
            # Add description in user's language
            attrs["description"] = self._translate('description')
            
            # Add reference
            attrs["reference"] = CALENDAR_INFO.get('reference_url', '')
            
            # Add display format setting
            attrs["display_format"] = self._display_format
        
        return attrs
    
    def _get_zodiac_animal(self, year: int) -> Dict[str, str]:
        """Get zodiac animal for a given year."""
        # The cycle starts from 1900 (Rat year)
        base_year = 1900
        index = (year - base_year) % 12
        
        return {
            "english": self._chinese_data["earthly_branches"]["zodiac"][index],
            "chinese": self._chinese_data["earthly_branches"]["zodiac_chinese"][index],
            "emoji": ["🐀", "🐂", "🐅", "🐇", "🐉", "🐍", "🐴", "🐐", "🐒", "🐓", "🐕", "🐖"][index]
        }
    
    def _get_heavenly_stem_earthly_branch(self, year: int) -> Dict[str, str]:
        """Get the Heavenly Stem and Earthly Branch for a year."""
        # The 60-year cycle starts from 1924 (甲子 year)
        base_year = 1924
        cycle_year = (year - base_year) % 60
        
        stem_index = cycle_year % 10
        branch_index = cycle_year % 12
        
        stem_chinese = self._chinese_data["heavenly_stems"]["chinese"][stem_index]
        branch_chinese = self._chinese_data["earthly_branches"]["chinese"][branch_index]
        
        element = self._chinese_data["heavenly_stems"]["elements"][stem_index]
        yin_yang = self._chinese_data["heavenly_stems"]["yin_yang"][stem_index]
        
        return {
            "chinese": f"{stem_chinese}{branch_chinese}",
            "pinyin": f"{self._chinese_data['heavenly_stems']['pinyin'][stem_index]}{self._chinese_data['earthly_branches']['pinyin'][branch_index]}",
            "element": element,
            "yin_yang": yin_yang
        }
    
    def _check_festival(self, month: int, day: int) -> Optional[Dict[str, str]]:
        """Check if the given lunar date is a festival."""
        date_key = f"{month}-{day}"
        if date_key in self._chinese_data["festivals"]:
            return self._chinese_data["festivals"][date_key]
        return None
    
    def _get_current_solar_term(self, date: datetime) -> Optional[Dict[str, str]]:
        """Get the current or upcoming solar term."""
        # This is a simplified version - in reality, solar terms follow complex astronomical calculations
        # Each solar term occurs approximately every 15 days
        day_of_year = date.timetuple().tm_yday
        term_index = (day_of_year - 5) // 15  # Approximate
        
        if 0 <= term_index < len(self._chinese_data["solar_terms"]):
            return self._chinese_data["solar_terms"][term_index]
        return None
    
    def _calculate_chinese_date(self, earth_date: datetime) -> Dict[str, Any]:
        """Calculate Chinese Lunar calendar date from Gregorian date."""
        
        if not HAS_LUNAR:
            return {"error": "lunarcalendar library not installed"}
        
        try:
            # Convert Gregorian to Lunar
            solar = Solar(earth_date.year, earth_date.month, earth_date.day)
            lunar = Converter.Solar2Lunar(solar)
            
            # Get lunar date components
            lunar_year = lunar.year
            lunar_month = lunar.month
            lunar_day = lunar.day
            is_leap_month = lunar.isleap
            
            # Get month name
            month_chinese = self._chinese_data["months"]["names"][lunar_month - 1]
            month_english = self._chinese_data["months"]["english"][lunar_month - 1]
            if is_leap_month:
                month_chinese = f"闰{month_chinese}"
                month_english = f"Leap {month_english}"
            
            # Format day
            day_chinese = self._format_chinese_day(lunar_day)
            
            # Get year info
            year_info = self._get_heavenly_stem_earthly_branch(lunar_year)
            zodiac = self._get_zodiac_animal(lunar_year)
            
            # Format the complete date based on display format
            if self._display_format == "chinese":
                formatted = f"{year_info['chinese']}年 {month_chinese}{day_chinese}"
            elif self._display_format == "english":
                formatted = f"Year of the {zodiac['english']} {year_info['element']}, {month_english} Day {lunar_day}"
            else:  # both
                formatted = f"{year_info['chinese']}年 {month_chinese}{day_chinese} | {zodiac['english']} Year"
            
            result = {
                "lunar_year": lunar_year,
                "lunar_month": lunar_month,
                "lunar_day": lunar_day,
                "is_leap_month": is_leap_month,
                "month_chinese": month_chinese,
                "month_english": month_english,
                "day_chinese": day_chinese,
                "formatted": formatted,
                "gregorian_date": earth_date.strftime("%Y-%m-%d")
            }
            
            # Add zodiac if configured
            if self._show_zodiac:
                result["zodiac_animal"] = zodiac["english"]
                result["zodiac_chinese"] = zodiac["chinese"]
                result["zodiac_emoji"] = zodiac["emoji"]
                result["element"] = year_info["element"]
                result["yin_yang"] = year_info["yin_yang"]
            
            # Add stem and branch
            result["stem_branch"] = year_info["chinese"]
            result["stem_branch_pinyin"] = year_info["pinyin"]
            
            # Check for festivals if configured
            if self._show_festivals:
                festival = self._check_festival(lunar_month, lunar_day)
                if festival:
                    result["festival_chinese"] = festival["chinese"]
                    result["festival_english"] = festival["english"]
                    result["is_festival"] = True
            
            # Add solar term if configured
            if self._show_solar_terms:
                solar_term = self._get_current_solar_term(earth_date)
                if solar_term:
                    result["solar_term_chinese"] = solar_term["chinese"]
                    result["solar_term_english"] = solar_term["english"]
            
            return result
            
        except Exception as e:
            _LOGGER.error(f"Error calculating Chinese date: {e}")
            return {"error": str(e)}
    
    def _format_chinese_day(self, day: int) -> str:
        """Format day number in Chinese."""
        if day == 10:
            return "初十"
        elif day == 20:
            return "二十"
        elif day == 30:
            return "三十"
        elif day < 10:
            return f"初{self._chinese_number(day)}"
        elif day < 20:
            return f"十{self._chinese_number(day - 10)}"
        elif day < 30:
            return f"廿{self._chinese_number(day - 20)}"
        else:
            return f"三十"
    
    def _chinese_number(self, num: int) -> str:
        """Convert number to Chinese character."""
        numbers = ["", "一", "二", "三", "四", "五", "六", "七", "八", "九", "十"]
        if 0 <= num <= 10:
            return numbers[num]
        return str(num)
    
    def update(self) -> None:
        """Update the sensor."""
        # Ensure options are loaded (in case async_added_to_hass hasn't run yet)
        if not self._options_loaded:
            self._load_options()
        
        if not HAS_LUNAR:
            self._state = "Library Missing - Install lunarcalendar"
            return
        
        now = datetime.now()
        self._chinese_date = self._calculate_chinese_date(now)
        
        # Set state to formatted Chinese date
        if "error" in self._chinese_date:
            self._state = f"Error: {self._chinese_date['error']}"
        else:
            self._state = self._chinese_date.get("formatted", "Unknown")
        
        _LOGGER.debug(f"Updated Chinese Lunar Calendar to {self._state}")