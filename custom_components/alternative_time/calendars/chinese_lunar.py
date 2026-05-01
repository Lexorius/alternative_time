"""Chinese Lunar Calendar implementation - Version 3.0.
Config Flow Compatible with Enhanced Features.

The Chinese lunar calendar is a lunisolar calendar that combines lunar months with solar years.
It has been used for thousands of years to determine festivals and agricultural timing.
"""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, Optional

from homeassistant.core import HomeAssistant

from ..sensor import AlternativeTimeSensorBase

_LOGGER = logging.getLogger(__name__)

# Try to import the lunar calendar library
try:
    from lunarcalendar import Converter, Solar
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
    "version": "3.0.0",
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

    # Configuration options for config_flow
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
                "zh-tw": "顯示當年的生肖動物",
                "de": "Zeige das Tierkreiszeichen für das aktuelle Jahr",
                "es": "Mostrar el animal del zodiaco para el año actual",
                "fr": "Afficher l'animal du zodiaque pour l'année en cours",
                "it": "Mostra l'animale dello zodiaco per l'anno corrente",
                "nl": "Toon het dierenriem dier voor het huidige jaar",
                "pt": "Mostrar o animal do zodíaco para o ano atual",
                "ru": "Показывать животное зодиака для текущего года",
                "ja": "現在の年の干支を表示",
                "ko": "현재 연도의 띠 동물 표시"
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
                "zh-tw": "顯示傳統中國節日",
                "de": "Zeige traditionelle chinesische Feste",
                "es": "Mostrar festivales chinos tradicionales",
                "fr": "Afficher les festivals chinois traditionnels",
                "it": "Mostra festival cinesi tradizionali",
                "nl": "Toon traditionele Chinese festivals",
                "pt": "Mostrar festivais chineses tradicionais",
                "ru": "Показывать традиционные китайские праздники",
                "ja": "伝統的な中国の祭りを表示",
                "ko": "전통 중국 축제 표시"
            }
        },
        "show_solar_terms": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show Solar Terms",
                "zh": "显示节气",
                "zh-tw": "顯示節氣",
                "de": "Solarterme anzeigen",
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
                "zh-tw": "顯示二十四節氣",
                "de": "Zeige die 24 Solarterme",
                "es": "Mostrar los 24 términos solares",
                "fr": "Afficher les 24 termes solaires",
                "it": "Mostra i 24 termini solari",
                "nl": "Toon de 24 zonnetermen",
                "pt": "Mostrar os 24 termos solares",
                "ru": "Показывать 24 солнечных термина",
                "ja": "二十四節気を表示",
                "ko": "24절기 표시"
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
                "en": "Choose how to display the calendar",
                "zh": "选择如何显示日历",
                "zh-tw": "選擇如何顯示日曆",
                "de": "Wähle wie der Kalender angezeigt wird",
                "es": "Elegir cómo mostrar el calendario",
                "fr": "Choisir comment afficher le calendrier",
                "it": "Scegli come visualizzare il calendario",
                "nl": "Kies hoe de kalender wordt weergegeven",
                "pt": "Escolher como exibir o calendário",
                "ru": "Выбрать как отображать календарь",
                "ja": "カレンダーの表示方法を選択",
                "ko": "달력 표시 방법 선택"
            }
        }
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
            "zodiac_chinese": ["鼠", "牛", "虎", "兔", "龙", "蛇", "马", "羊", "猴", "鸡", "狗", "猪"]
        },

        # Lunar months
        "months": {
            "names": ["正月", "二月", "三月", "四月", "五月", "六月",
                     "七月", "八月", "九月", "十月", "冬月", "腊月"],
            "english": ["First", "Second", "Third", "Fourth", "Fifth", "Sixth",
                       "Seventh", "Eighth", "Ninth", "Tenth", "Eleventh", "Twelfth"]
        },

        # Traditional festivals
        "festivals": {
            "1-1": {"chinese": "春节", "english": "Spring Festival"},
            "1-15": {"chinese": "元宵节", "english": "Lantern Festival"},
            "2-2": {"chinese": "龙抬头", "english": "Dragon Head Raising"},
            "5-5": {"chinese": "端午节", "english": "Dragon Boat Festival"},
            "7-7": {"chinese": "七夕节", "english": "Qixi Festival"},
            "7-15": {"chinese": "中元节", "english": "Ghost Festival"},
            "8-15": {"chinese": "中秋节", "english": "Mid-Autumn Festival"},
            "9-9": {"chinese": "重阳节", "english": "Double Ninth Festival"},
            "12-8": {"chinese": "腊八节", "english": "Laba Festival"}
        },

        # Solar terms (24 节气) - simplified list
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

    # Extended notes
    "notes": {
        "en": (
            "The Chinese lunar calendar is a lunisolar calendar combining lunar months with solar years. "
            "It has been used for over 4000 years for agricultural timing and traditional festivals. "
            "Requires the 'lunarcalendar' Python library to be installed."
        ),
        "zh": (
            "中国农历是一种阴阳历，结合了阴历月份和阳历年份。"
            "它已经使用了4000多年，用于农业时间和传统节日。"
            "需要安装'lunarcalendar' Python库。"
        ),
        "de": (
            "Der chinesische Mondkalender ist ein Lunisolarkalender, der Mondmonate mit Sonnenjahren kombiniert. "
            "Er wird seit über 4000 Jahren für landwirtschaftliche Zeitplanung und traditionelle Feste verwendet. "
            "Benötigt die Installation der 'lunarcalendar' Python-Bibliothek."
        )
    }
}


# ============================================
# SENSOR CLASS
# ============================================

class ChineseLunarCalendarSensor(AlternativeTimeSensorBase):
    """Sensor for displaying Chinese Lunar calendar dates."""

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

        # Get plugin options from config entry
        plugin_options = self._get_plugin_options()

        if plugin_options:
            _LOGGER.debug(f"Loading Chinese Lunar options: {plugin_options}")

            # Apply options using set_options method
            self.set_options(
                show_zodiac=plugin_options.get("show_zodiac"),
                show_festivals=plugin_options.get("show_festivals"),
                show_solar_terms=plugin_options.get("show_solar_terms"),
                display_format=plugin_options.get("display_format")
            )

        self._options_loaded = True

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added to hass."""
        await super().async_added_to_hass()

        # Load options after entity is registered
        self._load_options()

        _LOGGER.debug(f"Chinese Lunar sensor added to hass with options: "
                     f"zodiac={self._show_zodiac}, festivals={self._show_festivals}, "
                     f"solar_terms={self._show_solar_terms}, format={self._display_format}")

    def set_options(
        self,
        *,
        show_zodiac: Optional[bool] = None,
        show_festivals: Optional[bool] = None,
        show_solar_terms: Optional[bool] = None,
        display_format: Optional[str] = None
    ) -> None:
        """Set calendar options from config flow."""
        if show_zodiac is not None:
            self._show_zodiac = bool(show_zodiac)
            _LOGGER.debug(f"Set show_zodiac to: {show_zodiac}")

        if show_festivals is not None:
            self._show_festivals = bool(show_festivals)
            _LOGGER.debug(f"Set show_festivals to: {show_festivals}")

        if show_solar_terms is not None:
            self._show_solar_terms = bool(show_solar_terms)
            _LOGGER.debug(f"Set show_solar_terms to: {show_solar_terms}")

        if display_format is not None and display_format in ["chinese", "english", "both"]:
            self._display_format = display_format
            _LOGGER.debug(f"Set display_format to: {display_format}")

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes."""
        attrs = super().extra_state_attributes

        # Add Chinese calendar-specific attributes
        if self._chinese_date and "error" not in self._chinese_date:
            attrs.update(self._chinese_date)

            # Add metadata
            attrs["calendar_type"] = "Chinese Lunar"
            attrs["accuracy"] = CALENDAR_INFO.get("accuracy", "traditional")
            attrs["reference"] = CALENDAR_INFO.get("reference_url")
            attrs["notes"] = self._translate("notes")

            # Add configuration state
            attrs["config_show_zodiac"] = self._show_zodiac
            attrs["config_show_festivals"] = self._show_festivals
            attrs["config_show_solar_terms"] = self._show_solar_terms
            attrs["config_display_format"] = self._display_format

            # Add library status
            attrs["library_installed"] = HAS_LUNAR

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
            return "三十"

    def _chinese_number(self, num: int) -> str:
        """Convert number to Chinese character."""
        numbers = ["", "一", "二", "三", "四", "五", "六", "七", "八", "九", "十"]
        if 0 <= num <= 10:
            return numbers[num]
        return str(num)

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


# ============================================
# MODULE EXPORTS
# ============================================

# Export the sensor class
__all__ = ["ChineseLunarCalendarSensor"]
