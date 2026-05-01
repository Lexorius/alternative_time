"""Suriyakati Calendar (Thai Buddhist Calendar) implementation - Version 2.5."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict

from homeassistant.core import HomeAssistant

from ..sensor import AlternativeTimeSensorBase

_LOGGER = logging.getLogger(__name__)

# ============================================
# CALENDAR METADATA
# ============================================

# Update interval in seconds (3600 seconds = 1 hour)
UPDATE_INTERVAL = 3600

# Complete calendar information for auto-discovery
CALENDAR_INFO = {
    "id": "suriyakati_thai",
    "version": "2.5.0",
    "icon": "mdi:buddhism",
    "category": "cultural",
    "accuracy": "official",
    "update_interval": UPDATE_INTERVAL,

    # Multi-language names (English primary)
    "name": {
        "en": "Thai Buddhist Calendar",
        "de": "Thailändischer Buddhistischer Kalender",
        "es": "Calendario Budista Tailandés",
        "fr": "Calendrier Bouddhiste Thaïlandais",
        "it": "Calendario Buddista Thailandese",
        "nl": "Thaise Boeddhistische Kalender",
        "pt": "Calendário Budista Tailandês",
        "ru": "Тайский буддийский календарь",
        "ja": "タイ仏教暦",
        "zh": "泰国佛历",
        "ko": "태국 불교 달력",
        "th": "ปฏิทินสุริยคติไทย"
    },

    # Short descriptions for UI (English primary)
    "description": {
        "en": "Thai solar calendar with Buddhist Era year (BE = CE + 543)",
        "de": "Thailändischer Sonnenkalender mit buddhistischer Ära (BE = CE + 543)",
        "es": "Calendario solar tailandés con Era Budista (EB = EC + 543)",
        "fr": "Calendrier solaire thaïlandais avec Ère Bouddhiste (EB = EC + 543)",
        "it": "Calendario solare thailandese con Era Buddista (EB = EC + 543)",
        "nl": "Thaise zonnekalender met Boeddhistische Era (BE = CE + 543)",
        "pt": "Calendário solar tailandês com Era Budista (EB = EC + 543)",
        "ru": "Тайский солнечный календарь с буддийской эрой (БЭ = НЭ + 543)",
        "ja": "仏暦年のタイ太陽暦（BE = CE + 543）",
        "zh": "泰国太阳历，佛历纪年（BE = CE + 543）",
        "ko": "불기 연도의 태국 태양력 (BE = CE + 543)",
        "th": "ปฏิทินสุริยคติไทย พุทธศักราช (พ.ศ. = ค.ศ. + 543)"
    },

    # Detailed information for documentation
    "detailed_info": {
        "en": {
            "overview": "The official calendar of Thailand based on the Buddhist Era",
            "structure": "Solar calendar identical to Gregorian but with Buddhist Era years",
            "year": "Buddhist Era (BE) = Common Era (CE) + 543",
            "new_year": "Official New Year on January 1, traditional Songkran April 13-15",
            "months": "12 months with Thai names derived from Sanskrit",
            "weeks": "7-day weeks with planetary associations",
            "zodiac": "12-year animal cycle similar to Chinese zodiac",
            "colors": "Each day associated with lucky colors",
            "holy_days": "Buddhist holy days follow lunar calendar",
            "usage": "Official use in Thailand for all government and business"
        },
        "de": {
            "overview": "Der offizielle Kalender Thailands basierend auf der buddhistischen Ära",
            "structure": "Sonnenkalender identisch mit Gregorianisch aber mit buddhistischen Ära-Jahren",
            "year": "Buddhistische Ära (BE) = Christliche Ära (CE) + 543",
            "new_year": "Offizielles Neujahr am 1. Januar, traditionelles Songkran 13.-15. April",
            "months": "12 Monate mit thailändischen Namen aus dem Sanskrit",
            "weeks": "7-Tage-Wochen mit Planetenverbindungen",
            "zodiac": "12-Jahres-Tierzyklus ähnlich dem chinesischen Tierkreis",
            "colors": "Jeder Tag mit Glücksfarben verbunden",
            "holy_days": "Buddhistische Feiertage folgen dem Mondkalender",
            "usage": "Offizielle Verwendung in Thailand für Regierung und Wirtschaft"
        },
        "th": {
            "overview": "ปฏิทินทางการของประเทศไทยตามพุทธศักราช",
            "structure": "ปฏิทินสุริยคติเหมือนเกรกอเรียนแต่ใช้พุทธศักราช",
            "year": "พุทธศักราช (พ.ศ.) = คริสต์ศักราช (ค.ศ.) + 543",
            "new_year": "ปีใหม่ทางการ 1 มกราคม, สงกรานต์ 13-15 เมษายน",
            "months": "12 เดือน ชื่อไทยมาจากภาษาสันสกฤต",
            "weeks": "สัปดาห์ละ 7 วัน ตามดาวเคราะห์",
            "zodiac": "12 นักษัตร คล้ายปีนักษัตรจีน",
            "colors": "แต่ละวันมีสีประจำวัน",
            "holy_days": "วันพระตามจันทรคติ",
            "usage": "ใช้อย่างเป็นทางการในประเทศไทย"
        }
    },

    # Thai-specific data
    "thai_data": {
        # Thai months (solar calendar)
        "months": [
            {"name": "มกราคม", "roman": "Makarakhom", "english": "January", "abbr": "ม.ค."},
            {"name": "กุมภาพันธ์", "roman": "Kumphaphan", "english": "February", "abbr": "ก.พ."},
            {"name": "มีนาคม", "roman": "Minakhom", "english": "March", "abbr": "มี.ค."},
            {"name": "เมษายน", "roman": "Mesayon", "english": "April", "abbr": "เม.ย."},
            {"name": "พฤษภาคม", "roman": "Phruetsaphakhom", "english": "May", "abbr": "พ.ค."},
            {"name": "มิถุนายน", "roman": "Mithunayon", "english": "June", "abbr": "มิ.ย."},
            {"name": "กรกฎาคม", "roman": "Karakadakhom", "english": "July", "abbr": "ก.ค."},
            {"name": "สิงหาคม", "roman": "Singhakhom", "english": "August", "abbr": "ส.ค."},
            {"name": "กันยายน", "roman": "Kanyayon", "english": "September", "abbr": "ก.ย."},
            {"name": "ตุลาคม", "roman": "Tulakhom", "english": "October", "abbr": "ต.ค."},
            {"name": "พฤศจิกายน", "roman": "Phruetsachikayon", "english": "November", "abbr": "พ.ย."},
            {"name": "ธันวาคม", "roman": "Thanwakhom", "english": "December", "abbr": "ธ.ค."}
        ],

        # Thai weekdays
        "weekdays": [
            {"name": "อาทิตย์", "roman": "Wan Athit", "english": "Sunday", "planet": "Sun", "color": "Red"},
            {"name": "จันทร์", "roman": "Wan Chan", "english": "Monday", "planet": "Moon", "color": "Yellow"},
            {"name": "อังคาร", "roman": "Wan Angkhan", "english": "Tuesday", "planet": "Mars", "color": "Pink"},
            {"name": "พุธ", "roman": "Wan Phut", "english": "Wednesday", "planet": "Mercury", "color": "Green"},
            {"name": "พฤหัสบดี", "roman": "Wan Phruehatsabodi", "english": "Thursday", "planet": "Jupiter", "color": "Orange"},
            {"name": "ศุกร์", "roman": "Wan Suk", "english": "Friday", "planet": "Venus", "color": "Blue"},
            {"name": "เสาร์", "roman": "Wan Sao", "english": "Saturday", "planet": "Saturn", "color": "Purple"}
        ],

        # Thai zodiac animals (similar to Chinese)
        "zodiac": [
            {"thai": "ชวด", "roman": "Chuat", "english": "Rat", "emoji": "🐀"},
            {"thai": "ฉลู", "roman": "Chalu", "english": "Ox", "emoji": "🐂"},
            {"thai": "ขาล", "roman": "Khan", "english": "Tiger", "emoji": "🐅"},
            {"thai": "เถาะ", "roman": "Tho", "english": "Rabbit", "emoji": "🐰"},
            {"thai": "มะโรง", "roman": "Marong", "english": "Dragon", "emoji": "🐉"},
            {"thai": "มะเส็ง", "roman": "Maseng", "english": "Snake", "emoji": "🐍"},
            {"thai": "มะเมีย", "roman": "Mamia", "english": "Horse", "emoji": "🐴"},
            {"thai": "มะแม", "roman": "Mamae", "english": "Goat", "emoji": "🐐"},
            {"thai": "วอก", "roman": "Wok", "english": "Monkey", "emoji": "🐵"},
            {"thai": "ระกา", "roman": "Raka", "english": "Rooster", "emoji": "🐓"},
            {"thai": "จอ", "roman": "Cho", "english": "Dog", "emoji": "🐕"},
            {"thai": "กุน", "roman": "Kun", "english": "Pig", "emoji": "🐖"}
        ],

        # Thai numerals
        "thai_digits": ["๐", "๑", "๒", "๓", "๔", "๕", "๖", "๗", "๘", "๙"],

        # Major Thai holidays
        "holidays": {
            (1, 1): {"thai": "วันขึ้นปีใหม่", "english": "New Year's Day"},
            (2, 14): {"thai": "วันวาเลนไทน์", "english": "Valentine's Day"},
            (4, 6): {"thai": "วันจักรี", "english": "Chakri Day"},
            (4, 13): {"thai": "วันสงกรานต์", "english": "Songkran Festival"},
            (5, 1): {"thai": "วันแรงงาน", "english": "Labour Day"},
            (5, 4): {"thai": "วันฉัตรมงคล", "english": "Coronation Day"},
            (7, 28): {"thai": "วันเฉลิมพระชนมพรรษา", "english": "King's Birthday"},
            (8, 12): {"thai": "วันแม่", "english": "Mother's Day"},
            (10, 13): {"thai": "วันคล้ายวันสวรรคต", "english": "Memorial Day"},
            (10, 23): {"thai": "วันปิยมหาราช", "english": "Chulalongkorn Day"},
            (12, 5): {"thai": "วันพ่อ", "english": "Father's Day"},
            (12, 10): {"thai": "วันรัฐธรรมนูญ", "english": "Constitution Day"},
            (12, 31): {"thai": "วันสิ้นปี", "english": "New Year's Eve"}
        }
    },

    # Additional metadata
    "reference_url": "https://en.wikipedia.org/wiki/Thai_solar_calendar",
    "documentation_url": "https://www.thaicalendar.com",
    "origin": "Thailand",
    "created_by": "King Chulalongkorn (Rama V)",
    "official_since": "1888 CE (2431 BE)",

    # Example format
    "example": "25 December 2568 BE | ๒๕ ธันวาคม ๒๕๖๘",
    "example_meaning": "25th December 2568 Buddhist Era (2025 CE)",

    # Related calendars
    "related": ["gregorian", "buddhist", "lunar"],

    # Tags for searching and filtering
    "tags": [
        "cultural", "buddhist", "thai", "thailand", "solar",
        "official", "asian", "southeast_asia", "be", "songkran"
    ],

    # Special features
    "features": {
        "buddhist_era": True,
        "thai_numerals": True,
        "zodiac_animals": True,
        "day_colors": True,
        "lunar_holy_days": True,
        "precision": "day"
    },

    # Configuration options for this calendar
    "config_options": {
        "display_language": {
            "type": "select",
            "default": "english",
            "options": ["english", "thai", "romanized", "combined"],
            "label": {
                "en": "Display Language",
                "de": "Anzeigesprache",
                "es": "Idioma de visualización",
                "fr": "Langue d'affichage",
                "it": "Lingua di visualizzazione",
                "nl": "Weergavetaal",
                "pt": "Idioma de exibição",
                "ru": "Язык отображения",
                "ja": "表示言語",
                "zh": "显示语言",
                "ko": "표시 언어",
                "th": "ภาษาที่แสดง"
            },
            "description": {
                "en": "Choose how to display the date (English, Thai script, romanized Thai, or combined)",
                "de": "Wählen Sie, wie das Datum angezeigt werden soll (Englisch, Thai-Schrift, romanisiertes Thai oder kombiniert)",
                "th": "เลือกวิธีแสดงวันที่ (อังกฤษ, อักษรไทย, ภาษาไทยเป็นอักษรโรมัน, หรือผสม)"
            }
        },
        "use_thai_numerals": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Use Thai Numerals",
                "de": "Thai-Ziffern verwenden",
                "es": "Usar números tailandeses",
                "fr": "Utiliser les chiffres thaïs",
                "it": "Usa numeri thailandesi",
                "nl": "Gebruik Thaise cijfers",
                "pt": "Usar números tailandeses",
                "ru": "Использовать тайские цифры",
                "ja": "タイ数字を使用",
                "zh": "使用泰文数字",
                "ko": "태국 숫자 사용",
                "th": "ใช้ตัวเลขไทย"
            },
            "description": {
                "en": "Display numbers using Thai numerals (๐-๙)",
                "de": "Zahlen mit thailändischen Ziffern anzeigen (๐-๙)",
                "th": "แสดงตัวเลขเป็นเลขไทย (๐-๙)"
            }
        },
        "show_zodiac": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show Zodiac Animal",
                "de": "Tierkreiszeichen anzeigen",
                "es": "Mostrar animal del zodiaco",
                "fr": "Afficher l'animal du zodiaque",
                "it": "Mostra animale zodiacale",
                "nl": "Toon dierenriem dier",
                "pt": "Mostrar animal do zodíaco",
                "ru": "Показывать животное зодиака",
                "ja": "干支を表示",
                "zh": "显示生肖",
                "ko": "띠 동물 표시",
                "th": "แสดงปีนักษัตร"
            },
            "description": {
                "en": "Display the Thai zodiac animal for the current year",
                "de": "Das thailändische Tierkreiszeichen für das aktuelle Jahr anzeigen",
                "th": "แสดงปีนักษัตรของปีปัจจุบัน"
            }
        },
        "show_day_color": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show Day Color",
                "de": "Tagesfarbe anzeigen",
                "es": "Mostrar color del día",
                "fr": "Afficher la couleur du jour",
                "it": "Mostra colore del giorno",
                "nl": "Toon dagkleur",
                "pt": "Mostrar cor do dia",
                "ru": "Показывать цвет дня",
                "ja": "曜日の色を表示",
                "zh": "显示日期颜色",
                "ko": "요일 색상 표시",
                "th": "แสดงสีประจำวัน"
            },
            "description": {
                "en": "Display the traditional lucky color for each day of the week",
                "de": "Die traditionelle Glücksfarbe für jeden Wochentag anzeigen",
                "th": "แสดงสีประจำวันตามประเพณี"
            }
        },
        "show_buddhist_days": {
            "type": "boolean",
            "default": False,
            "label": {
                "en": "Show Buddhist Holy Days",
                "de": "Buddhistische Feiertage anzeigen",
                "es": "Mostrar días sagrados budistas",
                "fr": "Afficher les jours saints bouddhistes",
                "it": "Mostra giorni sacri buddisti",
                "nl": "Toon Boeddhistische heilige dagen",
                "pt": "Mostrar dias sagrados budistas",
                "ru": "Показывать буддийские святые дни",
                "ja": "仏教の聖日を表示",
                "zh": "显示佛教圣日",
                "ko": "불교 성일 표시",
                "th": "แสดงวันพระ"
            },
            "description": {
                "en": "Display Buddhist Uposatha days (lunar-based holy days)",
                "de": "Buddhistische Uposatha-Tage anzeigen (mondbasierte heilige Tage)",
                "th": "แสดงวันพระ (วันธรรมสวนะตามจันทรคติ)"
            }
        },
        "format": {
            "type": "select",
            "default": "full",
            "options": ["full", "medium", "short", "numeric"],
            "label": {
                "en": "Date Format",
                "de": "Datumsformat",
                "es": "Formato de fecha",
                "fr": "Format de date",
                "it": "Formato data",
                "nl": "Datumformaat",
                "pt": "Formato de data",
                "ru": "Формат даты",
                "ja": "日付形式",
                "zh": "日期格式",
                "ko": "날짜 형식",
                "th": "รูปแบบวันที่"
            },
            "description": {
                "en": "Choose how detailed the date display should be",
                "de": "Wählen Sie, wie detailliert die Datumsanzeige sein soll",
                "th": "เลือกความละเอียดในการแสดงวันที่"
            }
        }
    }
}


class SuriyakatiCalendarSensor(AlternativeTimeSensorBase):
    """Sensor for displaying Thai Buddhist Calendar (Suriyakati)."""

    # Class-level update interval
    UPDATE_INTERVAL = UPDATE_INTERVAL

    def __init__(self, base_name: str, hass: HomeAssistant) -> None:
        """Initialize the Suriyakati calendar sensor."""
        super().__init__(base_name, hass)

        # Get translated name from metadata
        calendar_name = self._translate('name', 'Thai Buddhist Calendar')

        # Set sensor attributes
        self._attr_name = f"{base_name} {calendar_name}"
        self._attr_unique_id = f"{base_name}_suriyakati_thai"
        self._attr_icon = CALENDAR_INFO.get("icon", "mdi:buddhism")

        # Default configuration options
        self._display_language = "english"
        self._use_thai_numerals = True
        self._show_zodiac = True
        self._show_day_color = True
        self._show_buddhist_days = False
        self._format = "full"

        # Thai data
        self._thai_data = CALENDAR_INFO["thai_data"]

        # Track if options have been loaded
        self._options_loaded = False

        _LOGGER.debug(f"Initialized Thai Buddhist Calendar sensor: {self._attr_name}")

    def _load_options(self) -> None:
        """Load configuration options from config entry."""
        if self._options_loaded:
            return

        try:
            options = self.get_plugin_options()
            if options:
                # Update configuration from plugin options
                self._display_language = options.get("display_language", self._display_language)
                self._use_thai_numerals = options.get("use_thai_numerals", self._use_thai_numerals)
                self._show_zodiac = options.get("show_zodiac", self._show_zodiac)
                self._show_day_color = options.get("show_day_color", self._show_day_color)
                self._show_buddhist_days = options.get("show_buddhist_days", self._show_buddhist_days)
                self._format = options.get("format", self._format)

                _LOGGER.debug(f"Thai calendar loaded options: language={self._display_language}, "
                            f"numerals={self._use_thai_numerals}, zodiac={self._show_zodiac}, "
                            f"color={self._show_day_color}, buddhist={self._show_buddhist_days}, "
                            f"format={self._format}")
            else:
                _LOGGER.debug("Thai calendar using default options - no custom options found")

            self._options_loaded = True
        except Exception as e:
            _LOGGER.debug(f"Thai calendar could not load options yet: {e}")

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

        # Add Thai-specific attributes
        if hasattr(self, '_thai_date'):
            attrs.update(self._thai_date)

            # Add description in user's language
            attrs["description"] = self._translate('description')

            # Add reference
            attrs["reference"] = CALENDAR_INFO.get('reference_url', '')

            # Add configuration status
            attrs["config"] = {
                "display_language": self._display_language,
                "use_thai_numerals": self._use_thai_numerals,
                "show_zodiac": self._show_zodiac,
                "show_day_color": self._show_day_color,
                "show_buddhist_days": self._show_buddhist_days,
                "format": self._format
            }

        return attrs

    def _to_thai_number(self, n: int) -> str:
        """Convert number to Thai numerals."""
        if not self._use_thai_numerals:
            return str(n)

        thai_digits = self._thai_data["thai_digits"]
        return ''.join(thai_digits[int(d)] for d in str(n))

    def _get_buddhist_day(self, day: int, month: int) -> str:
        """Calculate Buddhist holy day (simplified)."""
        # Simplified calculation - actual dates follow lunar calendar
        # This approximates uposatha days (Buddhist sabbath)
        lunar_approximation = (day + month * 2) % 30

        if lunar_approximation == 8:
            return "🌓 Uposatha (First Quarter)"
        elif lunar_approximation == 15:
            return "🌕 Uposatha (Full Moon)"
        elif lunar_approximation == 23:
            return "🌗 Uposatha (Last Quarter)"
        elif lunar_approximation in [29, 30, 0, 1]:
            return "🌑 Uposatha (New Moon)"

        return ""

    def _calculate_thai_date(self, earth_date: datetime) -> Dict[str, Any]:
        """Calculate Thai Buddhist Calendar date from standard date."""

        # Load options if not loaded yet
        self._load_options()

        # Calculate Buddhist Era year
        buddhist_year = earth_date.year + 543

        # Get month data
        month_data = self._thai_data["months"][earth_date.month - 1]

        # Get weekday (Thai week starts on Sunday)
        weekday_index = (earth_date.weekday() + 1) % 7
        weekday_data = self._thai_data["weekdays"][weekday_index]

        # Calculate zodiac animal
        # Thai zodiac aligned so 2024 CE (2567 BE) = Year of the Dragon (index 4)
        zodiac_index = (buddhist_year - 3) % 12
        zodiac_data = self._thai_data["zodiac"][zodiac_index]

        # Check for holidays
        holiday_data = self._thai_data["holidays"].get((earth_date.month, earth_date.day))

        # Get Buddhist holy day if enabled
        buddhist_day = self._get_buddhist_day(earth_date.day, earth_date.month) if self._show_buddhist_days else ""

        # Format date based on display language and format
        if self._format == "numeric":
            # Numeric format
            if self._use_thai_numerals:
                formatted = f"{self._to_thai_number(earth_date.day)}/{self._to_thai_number(earth_date.month)}/{self._to_thai_number(buddhist_year)}"
            else:
                formatted = f"{earth_date.day}/{earth_date.month}/{buddhist_year}"
        elif self._format == "short":
            # Short format
            if self._display_language == "thai":
                formatted = f"{self._to_thai_number(earth_date.day)} {month_data['abbr']} {self._to_thai_number(buddhist_year)}"
            else:
                formatted = f"{earth_date.day} {month_data['english'][:3]} {buddhist_year} BE"
        elif self._format == "medium":
            # Medium format
            if self._display_language == "thai":
                formatted = f"{self._to_thai_number(earth_date.day)} {month_data['name']} {self._to_thai_number(buddhist_year)}"
            elif self._display_language == "romanized":
                formatted = f"{earth_date.day} {month_data['roman']} {buddhist_year} BE"
            else:
                formatted = f"{earth_date.day} {month_data['english']} {buddhist_year} BE"
        else:  # full
            # Full format
            if self._display_language == "thai":
                formatted = f"{weekday_data['name']} {self._to_thai_number(earth_date.day)} {month_data['name']} พ.ศ. {self._to_thai_number(buddhist_year)}"
            elif self._display_language == "romanized":
                formatted = f"{weekday_data['roman']}, {earth_date.day} {month_data['roman']} {buddhist_year} BE"
            elif self._display_language == "combined":
                formatted = f"{earth_date.day} {month_data['english']} {buddhist_year} BE | {self._to_thai_number(earth_date.day)} {month_data['name']} {self._to_thai_number(buddhist_year)}"
            else:  # english
                formatted = f"{weekday_data['english']}, {earth_date.day} {month_data['english']} {buddhist_year} BE"

        result = {
            "buddhist_year": buddhist_year,
            "gregorian_year": earth_date.year,
            "day": earth_date.day,
            "month": earth_date.month,
            "month_english": month_data["english"],
            "month_thai": month_data["name"],
            "month_romanized": month_data["roman"],
            "weekday_english": weekday_data["english"],
            "weekday_thai": weekday_data["name"],
            "weekday_romanized": weekday_data["roman"],
            "formatted": formatted,
            "gregorian_date": earth_date.strftime("%Y-%m-%d")
        }

        # Add Thai numerals if enabled
        if self._use_thai_numerals:
            result["day_thai"] = self._to_thai_number(earth_date.day)
            result["year_thai"] = self._to_thai_number(buddhist_year)

        # Add zodiac if enabled
        if self._show_zodiac:
            result["zodiac_thai"] = zodiac_data["thai"]
            result["zodiac_english"] = zodiac_data["english"]
            result["zodiac_emoji"] = zodiac_data["emoji"]

        # Add day color if enabled
        if self._show_day_color:
            result["day_color"] = weekday_data["color"]
            result["day_planet"] = weekday_data["planet"]

        # Add Buddhist holy day if applicable
        if buddhist_day:
            result["buddhist_day"] = buddhist_day

        # Add holiday if applicable
        if holiday_data:
            result["holiday_thai"] = holiday_data["thai"]
            result["holiday_english"] = holiday_data["english"]

        return result

    def update(self) -> None:
        """Update the sensor."""
        now = datetime.now()
        self._thai_date = self._calculate_thai_date(now)

        # Set state to formatted date
        self._state = self._thai_date["formatted"]

        _LOGGER.debug(f"Updated Thai Buddhist Calendar to {self._state}")
