"""Suriyakati Calendar (Thai Buddhist Calendar) implementation - Version 2.5."""
from __future__ import annotations

from datetime import datetime
import logging
from typing import Dict, Any

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
    "id": "suriyakati",
    "version": "2.5.0",
    "icon": "mdi:buddhism",
    "category": "cultural",
    "accuracy": "official",
    "update_interval": UPDATE_INTERVAL,
    
    # Multi-language names
    "name": {
        "en": "Suriyakati Calendar",
        "de": "Suriyakati-Kalender",
        "es": "Calendario Suriyakati",
        "fr": "Calendrier Suriyakati",
        "it": "Calendario Suriyakati",
        "nl": "Suriyakati Kalender",
        "pt": "Calendário Suriyakati",
        "ru": "Календарь Сурьякати",
        "ja": "スーリヤカティ暦",
        "zh": "素里亚卡提历",
        "ko": "수리야카티 달력",
        "th": "ปฏิทินสุริยคติไทย"
    },
    
    # Short descriptions for UI
    "description": {
        "en": "Thai Buddhist calendar with BE year (543 years ahead)",
        "de": "Thailändischer buddhistischer Kalender mit BE-Jahr (543 Jahre voraus)",
        "es": "Calendario budista tailandés con año BE (543 años adelante)",
        "fr": "Calendrier bouddhiste thaïlandais avec année BE (543 ans d'avance)",
        "it": "Calendario buddista thailandese con anno BE (543 anni avanti)",
        "nl": "Thaise boeddhistische kalender met BE-jaar (543 jaar vooruit)",
        "pt": "Calendário budista tailandês com ano BE (543 anos à frente)",
        "ru": "Тайский буддийский календарь с годом BE (на 543 года вперед)",
        "ja": "仏暦（BE）年のタイ仏教暦（543年先）",
        "zh": "泰国佛历，BE年（提前543年）",
        "ko": "BE 연도의 태국 불교 달력 (543년 앞)",
        "th": "ปฏิทินพุทธศักราชไทย (พ.ศ. = ค.ศ. + 543)"
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
            "months": "12 เดือนชื่อไทยมาจากภาษาสันสกฤต",
            "weeks": "สัปดาห์ 7 วันตามดาวเคราะห์",
            "zodiac": "12 นักษัตรคล้ายจีน",
            "colors": "แต่ละวันมีสีประจำ",
            "holy_days": "วันพระตามจันทรคติ",
            "usage": "ใช้อย่างเป็นทางการในไทยทุกหน่วยงาน"
        }
    },
    
    # Suriyakati-specific data
    "suriyakati_data": {
        # Thai month names with meanings
        "months": [
            {"thai": "มกราคม", "roman": "Makarakhom", "sanskrit": "Makara", "meaning": "Capricorn", "days": 31},
            {"thai": "กุมภาพันธ์", "roman": "Kumphaphan", "sanskrit": "Kumbha", "meaning": "Aquarius", "days": 28},
            {"thai": "มีนาคม", "roman": "Minakhom", "sanskrit": "Mina", "meaning": "Pisces", "days": 31},
            {"thai": "เมษายน", "roman": "Mesayon", "sanskrit": "Mesha", "meaning": "Aries", "days": 30},
            {"thai": "พฤษภาคม", "roman": "Phruetsaphakhom", "sanskrit": "Vrishabha", "meaning": "Taurus", "days": 31},
            {"thai": "มิถุนายน", "roman": "Mithunayon", "sanskrit": "Mithuna", "meaning": "Gemini", "days": 30},
            {"thai": "กรกฎาคม", "roman": "Karakadakhom", "sanskrit": "Karkata", "meaning": "Cancer", "days": 31},
            {"thai": "สิงหาคม", "roman": "Singhakhom", "sanskrit": "Simha", "meaning": "Leo", "days": 31},
            {"thai": "กันยายน", "roman": "Kanyayon", "sanskrit": "Kanya", "meaning": "Virgo", "days": 30},
            {"thai": "ตุลาคม", "roman": "Tulakhom", "sanskrit": "Tula", "meaning": "Libra", "days": 31},
            {"thai": "พฤศจิกายน", "roman": "Phruetsachikayon", "sanskrit": "Vrishchika", "meaning": "Scorpio", "days": 30},
            {"thai": "ธันวาคม", "roman": "Thanwakhom", "sanskrit": "Dhanu", "meaning": "Sagittarius", "days": 31}
        ],
        
        # Thai weekdays with planetary associations
        "weekdays": [
            {"thai": "วันอาทิตย์", "roman": "Wan Athit", "planet": "Sun", "color": "Red", "emoji": "☀️"},
            {"thai": "วันจันทร์", "roman": "Wan Chan", "planet": "Moon", "color": "Yellow", "emoji": "🌙"},
            {"thai": "วันอังคาร", "roman": "Wan Angkhan", "planet": "Mars", "color": "Pink", "emoji": "♂️"},
            {"thai": "วันพุธ", "roman": "Wan Phut", "planet": "Mercury", "color": "Green", "emoji": "☿️"},
            {"thai": "วันพฤหัสบดี", "roman": "Wan Pharuehat", "planet": "Jupiter", "color": "Orange", "emoji": "♃"},
            {"thai": "วันศุกร์", "roman": "Wan Suk", "planet": "Venus", "color": "Blue", "emoji": "♀️"},
            {"thai": "วันเสาร์", "roman": "Wan Sao", "planet": "Saturn", "color": "Purple", "emoji": "♄"}
        ],
        
        # Thai zodiac animals (12-year cycle)
        "zodiac": [
            {"thai": "ชวด", "roman": "Chuad", "animal": "Rat", "emoji": "🐀"},
            {"thai": "ฉลู", "roman": "Chalu", "animal": "Ox", "emoji": "🐂"},
            {"thai": "ขาล", "roman": "Khan", "animal": "Tiger", "emoji": "🐅"},
            {"thai": "เถาะ", "roman": "Tho", "animal": "Rabbit", "emoji": "🐰"},
            {"thai": "มะโรง", "roman": "Marong", "animal": "Dragon", "emoji": "🐉"},
            {"thai": "มะเส็ง", "roman": "Maseng", "animal": "Snake", "emoji": "🐍"},
            {"thai": "มะเมีย", "roman": "Mamia", "animal": "Horse", "emoji": "🐴"},
            {"thai": "มะแม", "roman": "Mamae", "animal": "Goat", "emoji": "🐐"},
            {"thai": "วอก", "roman": "Wok", "animal": "Monkey", "emoji": "🐵"},
            {"thai": "ระกา", "roman": "Raka", "animal": "Rooster", "emoji": "🐓"},
            {"thai": "จอ", "roman": "Cho", "animal": "Dog", "emoji": "🐕"},
            {"thai": "กุน", "roman": "Kun", "animal": "Pig", "emoji": "🐷"}
        ],
        
        # Thai numerals
        "thai_digits": "๐๑๒๓๔๕๖๗๘๙",
        
        # Important Thai holidays
        "holidays": {
            (1, 1): {"thai": "วันขึ้นปีใหม่", "english": "New Year's Day", "type": "public"},
            (2, 14): {"thai": "วันวาเลนไทน์", "english": "Valentine's Day", "type": "observance"},
            (4, 6): {"thai": "วันจักรี", "english": "Chakri Day", "type": "public"},
            (4, 13): {"thai": "วันสงกรานต์", "english": "Songkran", "type": "public"},
            (4, 14): {"thai": "วันสงกรานต์", "english": "Songkran", "type": "public"},
            (4, 15): {"thai": "วันสงกรานต์", "english": "Songkran", "type": "public"},
            (5, 1): {"thai": "วันแรงงาน", "english": "Labour Day", "type": "public"},
            (5, 4): {"thai": "วันฉัตรมงคล", "english": "Coronation Day", "type": "public"},
            (7, 28): {"thai": "วันเฉลิมพระชนมพรรษา ร.10", "english": "King's Birthday", "type": "public"},
            (8, 12): {"thai": "วันแม่แห่งชาติ", "english": "Mother's Day", "type": "public"},
            (10, 13): {"thai": "วันคล้ายวันสวรรคต ร.9", "english": "Memorial Day R.9", "type": "public"},
            (10, 23): {"thai": "วันปิยมหาราช", "english": "Chulalongkorn Day", "type": "public"},
            (12, 5): {"thai": "วันพ่อแห่งชาติ", "english": "Father's Day", "type": "public"},
            (12, 10): {"thai": "วันรัฐธรรมนูญ", "english": "Constitution Day", "type": "public"},
            (12, 31): {"thai": "วันสิ้นปี", "english": "New Year's Eve", "type": "public"}
        },
        
        # Buddhist holy days (simplified - actual dates follow lunar calendar)
        "buddhist_days": {
            "uposatha": "วันพระ",  # Buddhist holy day (4 per lunar month)
            "makha_bucha": "วันมาฆบูชา",  # Full moon of 3rd lunar month
            "visakha_bucha": "วันวิสาขบูชา",  # Full moon of 6th lunar month
            "asanha_bucha": "วันอาสาฬหบูชา",  # Full moon of 8th lunar month
            "khao_phansa": "วันเข้าพรรษา",  # Beginning of Buddhist Lent
            "ok_phansa": "วันออกพรรษา"  # End of Buddhist Lent
        },
        
        # Time periods
        "time_periods": {
            (0, 6): {"thai": "ตี", "roman": "ti", "meaning": "Late night", "emoji": "🌙"},
            (6, 7): {"thai": "เช้าตรู่", "roman": "chao tru", "meaning": "Dawn", "emoji": "🌅"},
            (7, 12): {"thai": "เช้า", "roman": "chao", "meaning": "Morning", "emoji": "☀️"},
            (12, 13): {"thai": "เที่ยง", "roman": "thiang", "meaning": "Noon", "emoji": "🌞"},
            (13, 16): {"thai": "บ่าย", "roman": "bai", "meaning": "Afternoon", "emoji": "🌤️"},
            (16, 18): {"thai": "เย็น", "roman": "yen", "meaning": "Evening", "emoji": "🌇"},
            (18, 20): {"thai": "ค่ำ", "roman": "kham", "meaning": "Early night", "emoji": "🌆"},
            (20, 24): {"thai": "ดึก", "roman": "duek", "meaning": "Late night", "emoji": "🌌"}
        }
    },
    
    # Additional metadata
    "reference_url": "https://en.wikipedia.org/wiki/Thai_solar_calendar",
    "documentation_url": "https://www.thaicalendar.com",
    "origin": "Thailand",
    "created_by": "King Chulalongkorn (Rama V)",
    "official_since": "1888 CE (2431 BE)",
    
    # Example format
    "example": "๒๕ ธันวาคม ๒๕๖๘ | 25 Thanwakhom 2568 BE",
    "example_meaning": "25th December 2568 Buddhist Era (2025 CE)",
    
    # Related calendars
    "related": ["gregorian", "buddhist", "lunar"],
    
    # Tags for searching and filtering
    "tags": [
        "cultural", "buddhist", "thai", "thailand", "official",
        "solar", "suriyakati", "be", "songkran", "lunar"
    ],
    
    # Special features
    "features": {
        "buddhist_era": True,
        "thai_numerals": True,
        "planetary_days": True,
        "zodiac_cycle": True,
        "lunar_holidays": True,
        "color_associations": True,
        "precision": "day"
    },
    
    # Configuration options for this calendar
    "config_options": {
        "use_thai_numerals": {
            "type": "boolean",
            "default": True,
            "description": {
                "en": "Use Thai numerals (๐-๙)",
                "de": "Thailändische Ziffern verwenden (๐-๙)",
                "th": "ใช้เลขไทย (๐-๙)"
            }
        },
        "show_zodiac": {
            "type": "boolean",
            "default": True,
            "description": {
                "en": "Show zodiac animal",
                "de": "Tierkreiszeichen anzeigen",
                "th": "แสดงปีนักษัตร"
            }
        },
        "show_color": {
            "type": "boolean",
            "default": True,
            "description": {
                "en": "Show daily color",
                "de": "Tagesfarbe anzeigen",
                "th": "แสดงสีประจำวัน"
            }
        },
        "show_buddhist_days": {
            "type": "boolean",
            "default": True,
            "description": {
                "en": "Show Buddhist holy days",
                "de": "Buddhistische Feiertage anzeigen",
                "th": "แสดงวันพระ"
            }
        },
        "language": {
            "type": "select",
            "default": "both",
            "options": ["thai", "roman", "both"],
            "description": {
                "en": "Display language",
                "de": "Anzeigesprache",
                "th": "ภาษาที่แสดง"
            }
        }
    }
}


class SuriyakatiCalendarSensor(AlternativeTimeSensorBase):
    """Sensor for displaying Suriyakati Calendar (Thai Buddhist)."""
    
    # Class-level update interval
    UPDATE_INTERVAL = 3600  # Update every hour
    
    def __init__(self, base_name: str, hass: HomeAssistant) -> None:
        """Initialize the Suriyakati calendar sensor."""
        super().__init__(base_name, hass)
        
        # Get translated name from metadata
        calendar_name = self._translate('name', 'Suriyakati Calendar')
        
        # Set sensor attributes
        self._attr_name = f"{base_name} {calendar_name}"
        self._attr_unique_id = f"{base_name}_suriyakati"
        self._attr_icon = CALENDAR_INFO.get("icon", "mdi:buddhism")
        
        # Configuration options
        self._use_thai_numerals = True
        self._show_zodiac = True
        self._show_color = True
        self._show_buddhist_days = True
        self._language = "both"  # thai, roman, or both
        
        # Suriyakati data
        self._suriyakati_data = CALENDAR_INFO["suriyakati_data"]
        
        _LOGGER.debug(f"Initialized Suriyakati Calendar sensor: {self._attr_name}")
    
    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes."""
        attrs = super().extra_state_attributes
        
        # Add Suriyakati-specific attributes
        if hasattr(self, '_suriyakati_date'):
            attrs.update(self._suriyakati_date)
            
            # Add description in user's language
            attrs["description"] = self._translate('description')
            
            # Add reference
            attrs["reference"] = CALENDAR_INFO.get('reference_url', '')
            
            # Add calendar system info
            attrs["calendar_system"] = "Solar (Suriyakati)"
            attrs["era"] = "Buddhist Era (BE)"
        
        return attrs
    
    def _to_thai_number(self, n: int) -> str:
        """Convert number to Thai numerals."""
        if not self._use_thai_numerals:
            return str(n)
        
        thai_digits = self._suriyakati_data["thai_digits"]
        return ''.join(thai_digits[int(d)] for d in str(n))
    
    def _get_buddhist_day(self, day: int, month: int) -> str:
        """Calculate Buddhist holy day (simplified)."""
        # Simplified calculation - actual dates follow lunar calendar
        # This approximates uposatha days (Buddhist sabbath)
        lunar_approximation = (day + month * 2) % 30
        
        if lunar_approximation == 8:
            return "🌓 วันพระ (First Quarter)"
        elif lunar_approximation == 15:
            return "🌕 วันพระ (Full Moon)"
        elif lunar_approximation == 23:
            return "🌗 วันพระ (Last Quarter)"
        elif lunar_approximation in [29, 30, 0, 1]:
            return "🌑 วันพระ (New Moon)"
        
        return ""
    
    def _get_time_period(self, hour: int) -> Dict[str, str]:
        """Get Thai time period for the hour."""
        for (start, end), period in self._suriyakati_data["time_periods"].items():
            if start <= hour < end or (start > end and (hour >= start or hour < end)):
                return period
        return {"thai": "เที่ยงคืน", "roman": "thiang khuen", "meaning": "Midnight", "emoji": "🕛"}
    
    def _calculate_suriyakati_date(self, earth_date: datetime) -> Dict[str, Any]:
        """Calculate Suriyakati Calendar date from standard date."""
        
        # Calculate Buddhist Era year
        buddhist_year = earth_date.year + 543
        
        # Get month data
        month_data = self._suriyakati_data["months"][earth_date.month - 1]
        
        # Get weekday (Thai week starts on Sunday)
        weekday_index = (earth_date.weekday() + 1) % 7
        weekday_data = self._suriyakati_data["weekdays"][weekday_index]
        
        # Calculate zodiac animal
        # Thai zodiac aligned so 2024 CE (2567 BE) = Year of the Dragon (index 4)
        zodiac_index = (buddhist_year - 3) % 12
        zodiac_data = self._suriyakati_data["zodiac"][zodiac_index]
        
        # Check for holidays
        holiday_data = self._suriyakati_data["holidays"].get((earth_date.month, earth_date.day))
        
        # Get Buddhist holy day
        buddhist_day = self._get_buddhist_day(earth_date.day, earth_date.month) if self._show_buddhist_days else ""
        
        # Get time period
        time_period = self._get_time_period(earth_date.hour)
        
        # Convert numbers to Thai if enabled
        thai_day = self._to_thai_number(earth_date.day)
        thai_year = self._to_thai_number(buddhist_year)
        
        # Format date based on language setting
        if self._language == "thai":
            date_parts = [
                f"{thai_day} {month_data['thai']} {thai_year}",
                weekday_data['thai']
            ]
        elif self._language == "roman":
            date_parts = [
                f"{earth_date.day} {month_data['roman']} {buddhist_year} BE",
                weekday_data['roman']
            ]
        else:  # both
            date_parts = [
                f"{thai_day} {month_data['thai']} {thai_year}",
                f"{earth_date.day} {month_data['roman']} {buddhist_year} BE"
            ]
        
        # Add zodiac if enabled
        if self._show_zodiac:
            zodiac_str = f"{zodiac_data['emoji']} {zodiac_data['thai']} ({zodiac_data['animal']})"
            date_parts.append(zodiac_str)
        
        # Add color if enabled
        if self._show_color:
            color_str = f"🎨 {weekday_data['color']}"
            date_parts.append(color_str)
        
        # Add time period
        date_parts.append(f"{time_period['emoji']} {time_period['thai']} ({time_period['meaning']})")
        
        # Add Buddhist day if applicable
        if buddhist_day:
            date_parts.append(buddhist_day)
        
        # Add holiday if applicable
        if holiday_data:
            holiday_str = f"🎉 {holiday_data['thai']} ({holiday_data['english']})"
            date_parts.append(holiday_str)
        
        full_date = " | ".join(date_parts)
        
        result = {
            "buddhist_year": buddhist_year,
            "common_year": earth_date.year,
            "month_thai": month_data["thai"],
            "month_roman": month_data["roman"],
            "month_number": earth_date.month,
            "day": earth_date.day,
            "day_thai": thai_day,
            "weekday_thai": weekday_data["thai"],
            "weekday_roman": weekday_data["roman"],
            "weekday_planet": weekday_data["planet"],
            "weekday_color": weekday_data["color"],
            "zodiac_thai": zodiac_data["thai"],
            "zodiac_animal": zodiac_data["animal"],
            "time_period_thai": time_period["thai"],
            "time_period_meaning": time_period["meaning"],
            "gregorian_date": earth_date.strftime("%Y-%m-%d"),
            "full_date": full_date
        }
        
        if holiday_data:
            result["holiday_thai"] = holiday_data["thai"]
            result["holiday_english"] = holiday_data["english"]
            result["holiday_type"] = holiday_data["type"]
        
        if buddhist_day:
            result["buddhist_holy_day"] = buddhist_day
        
        return result
    
    def update(self) -> None:
        """Update the sensor."""
        now = datetime.now()
        self._suriyakati_date = self._calculate_suriyakati_date(now)
        
        # Set state to main date line
        if self._language == "thai":
            self._state = f"{self._suriyakati_date['day_thai']} {self._suriyakati_date['month_thai']} {self._to_thai_number(self._suriyakati_date['buddhist_year'])}"
        elif self._language == "roman":
            self._state = f"{self._suriyakati_date['day']} {self._suriyakati_date['month_roman']} {self._suriyakati_date['buddhist_year']} BE"
        else:
            self._state = f"{self._suriyakati_date['buddhist_year']} BE"
        
        _LOGGER.debug(f"Updated Suriyakati Calendar to {self._state}")