"""Ancient Egyptian Calendar implementation - Version 2.5."""
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
    "id": "egyptian",
    "version": "2.5.0",
    "icon": "mdi:pyramid",
    "category": "historical",
    "accuracy": "approximate",
    "update_interval": UPDATE_INTERVAL,
    
    # Multi-language names
    "name": {
        "en": "Egyptian Calendar",
        "de": "Ägyptischer Kalender",
        "es": "Calendario Egipcio",
        "fr": "Calendrier Égyptien",
        "it": "Calendario Egiziano",
        "nl": "Egyptische Kalender",
        "pt": "Calendário Egípcio",
        "ru": "Египетский календарь",
        "ja": "エジプト暦",
        "zh": "埃及历",
        "ko": "이집트 달력",
        "ar": "التقويم المصري"
    },
    
    # Short descriptions for UI
    "description": {
        "en": "Ancient Egyptian civil calendar with 365 days (e.g. Dynasty 1 Year 25, 15 Thoth)",
        "de": "Altägyptischer Zivilkalender mit 365 Tagen (z.B. Dynastie 1 Jahr 25, 15 Thoth)",
        "es": "Calendario civil egipcio antiguo con 365 días (ej. Dinastía 1 Año 25, 15 Thoth)",
        "fr": "Calendrier civil égyptien antique avec 365 jours (ex. Dynastie 1 An 25, 15 Thoth)",
        "it": "Calendario civile egiziano antico con 365 giorni (es. Dinastia 1 Anno 25, 15 Thoth)",
        "nl": "Oude Egyptische burgerlijke kalender met 365 dagen (bijv. Dynastie 1 Jaar 25, 15 Thoth)",
        "pt": "Calendário civil egípcio antigo com 365 dias (ex. Dinastia 1 Ano 25, 15 Thoth)",
        "ru": "Древнеегипетский гражданский календарь с 365 днями (напр. Династия 1 Год 25, 15 Тот)",
        "ja": "365日の古代エジプト市民暦（例：第1王朝25年、トート月15日）",
        "zh": "365天的古埃及民用历（例：第1王朝25年，透特月15日）",
        "ko": "365일의 고대 이집트 민간 달력 (예: 1왕조 25년, 토트 15일)",
        "ar": "التقويم المدني المصري القديم بـ 365 يومًا"
    },
    
    # Detailed information for documentation
    "detailed_info": {
        "en": {
            "overview": "The Egyptian civil calendar was one of the first solar calendars",
            "structure": "365 days: 12 months of 30 days + 5 epagomenal days",
            "seasons": "3 seasons: Akhet (Inundation), Peret (Emergence), Shemu (Harvest)",
            "weeks": "Each month divided into 3 decans (10-day weeks)",
            "new_year": "New Year: Heliacal rising of Sirius (around July 19)",
            "drift": "Calendar drifted through seasons (Sothic cycle of 1,461 years)",
            "hours": "24 hours per day (12 day hours + 12 night hours)",
            "epagomenal": "5 extra days were birthdays of gods: Osiris, Horus, Set, Isis, Nephthys"
        },
        "de": {
            "overview": "Der ägyptische Zivilkalender war einer der ersten Sonnenkalender",
            "structure": "365 Tage: 12 Monate à 30 Tage + 5 Epagomenaltage",
            "seasons": "3 Jahreszeiten: Achet (Überschwemmung), Peret (Aussaat), Schemu (Ernte)",
            "weeks": "Jeder Monat in 3 Dekane (10-Tage-Wochen) unterteilt",
            "new_year": "Neujahr: Heliakischer Aufgang des Sirius (um den 19. Juli)",
            "drift": "Kalender driftete durch die Jahreszeiten (Sothis-Zyklus von 1.461 Jahren)",
            "hours": "24 Stunden pro Tag (12 Tagesstunden + 12 Nachtstunden)",
            "epagomenal": "5 Zusatztage waren Geburtstage der Götter: Osiris, Horus, Seth, Isis, Nephthys"
        },
        "ar": {
            "overview": "كان التقويم المدني المصري أحد أوائل التقاويم الشمسية",
            "structure": "365 يوم: 12 شهر من 30 يوم + 5 أيام نسيء",
            "seasons": "3 فصول: آخت (الفيضان)، بيريت (الإنبات)، شمو (الحصاد)",
            "weeks": "كل شهر مقسم إلى 3 عشريات (أسابيع من 10 أيام)",
            "new_year": "رأس السنة: الشروق الاحتراقي للشعرى اليمانية (حوالي 19 يوليو)",
            "drift": "انحرف التقويم عبر الفصول (دورة سوثية من 1461 سنة)",
            "hours": "24 ساعة في اليوم (12 ساعة نهار + 12 ساعة ليل)",
            "epagomenal": "5 أيام إضافية كانت أعياد ميلاد الآلهة: أوزوريس، حورس، ست، إيزيس، نفتيس"
        }
    },
    
    # Egyptian-specific data
    "egyptian_data": {
        # Egyptian months with seasons
        "months": [
            # Akhet (Inundation/Flood)
            {"name": "Thoth", "hieroglyph": "𓊖", "season": "Akhet", "season_emoji": "🌊", "god": "Thoth"},
            {"name": "Phaophi", "hieroglyph": "𓊖", "season": "Akhet", "season_emoji": "🌊", "god": "Ptah"},
            {"name": "Athyr", "hieroglyph": "𓊖", "season": "Akhet", "season_emoji": "🌊", "god": "Hathor"},
            {"name": "Choiak", "hieroglyph": "𓊖", "season": "Akhet", "season_emoji": "🌊", "god": "Sekhmet"},
            # Peret (Emergence/Winter)
            {"name": "Tybi", "hieroglyph": "🌱", "season": "Peret", "season_emoji": "🌱", "god": "Min"},
            {"name": "Mechir", "hieroglyph": "🌱", "season": "Peret", "season_emoji": "🌱", "god": "Bastet"},
            {"name": "Phamenoth", "hieroglyph": "🌱", "season": "Peret", "season_emoji": "🌱", "god": "Khnum"},
            {"name": "Pharmuthi", "hieroglyph": "🌱", "season": "Peret", "season_emoji": "🌱", "god": "Renenutet"},
            # Shemu (Harvest/Summer)
            {"name": "Pachons", "hieroglyph": "☀️", "season": "Shemu", "season_emoji": "🌾", "god": "Khonsu"},
            {"name": "Payni", "hieroglyph": "☀️", "season": "Shemu", "season_emoji": "🌾", "god": "Horus"},
            {"name": "Epiphi", "hieroglyph": "☀️", "season": "Shemu", "season_emoji": "🌾", "god": "Isis"},
            {"name": "Mesore", "hieroglyph": "☀️", "season": "Shemu", "season_emoji": "🌾", "god": "Ra"}
        ],
        
        # Decan names (10-day weeks)
        "decans": [
            {"name": "First Decan", "symbol": "𓇳"},
            {"name": "Second Decan", "symbol": "𓇴"},
            {"name": "Third Decan", "symbol": "𓇵"}
        ],
        
        # Epagomenal days (birthdays of gods)
        "epagomenal_gods": ["Osiris", "Horus", "Set", "Isis", "Nephthys"],
        
        # Hieroglyphic numbers
        "hieroglyphs": {
            1: "𓏤", 2: "𓏥", 3: "𓏦", 4: "𓏧", 5: "𓏨",
            6: "𓏩", 7: "𓏪", 8: "𓏫", 9: "𓏬",
            10: "𓎆", 20: "𓎇", 30: "𓎈"
        },
        
        # Egyptian hours
        "day_hours": [
            "First Hour of Day", "Second Hour of Day", "Third Hour of Day",
            "Fourth Hour of Day", "Fifth Hour of Day", "Sixth Hour of Day",
            "Seventh Hour of Day", "Eighth Hour of Day", "Ninth Hour of Day",
            "Tenth Hour of Day", "Eleventh Hour of Day", "Twelfth Hour of Day"
        ],
        "night_hours": [
            "First Hour of Night", "Second Hour of Night", "Third Hour of Night",
            "Fourth Hour of Night", "Fifth Hour of Night", "Sixth Hour of Night",
            "Seventh Hour of Night", "Eighth Hour of Night", "Ninth Hour of Night",
            "Tenth Hour of Night", "Eleventh Hour of Night", "Twelfth Hour of Night"
        ],
        
        # Nile status
        "nile_status": {
            "Akhet": {"status": "Nile Flooding", "emoji": "🌊"},
            "Peret": {"status": "Fields Emerging", "emoji": "🌱"},
            "Shemu": {"status": "Harvest Time", "emoji": "🌾"}
        },
        
        # New year
        "new_year": {
            "month": 7,
            "day": 19,
            "description": "Heliacal rising of Sirius"
        }
    },
    
    # Additional metadata
    "reference_url": "https://en.wikipedia.org/wiki/Egyptian_calendar",
    "documentation_url": "https://www.britannica.com/science/Egyptian-calendar",
    "origin": "Ancient Egypt",
    "created_by": "Ancient Egyptians",
    "period": "3000 BCE - 641 CE",
    
    # Example format
    "example": "Dynasty 1 Year 25, 𓏤𓏨 15 Thoth (Akhet)",
    "example_meaning": "Dynasty 1, Year 25, 15th day of Thoth month, Inundation season",
    
    # Related calendars
    "related": ["coptic", "julian", "sothic"],
    
    # Tags for searching and filtering
    "tags": [
        "historical", "ancient", "egyptian", "solar", "civil",
        "nile", "pharaoh", "hieroglyphic", "decan", "sothic"
    ],
    
    # Special features
    "features": {
        "solar_calendar": True,
        "epagomenal_days": True,
        "decans": True,
        "no_leap_year": True,
        "sothic_cycle": True,
        "hieroglyphic_numbers": True,
        "precision": "day"
    },
    
    # Configuration options for this calendar
    "config_options": {
        "show_hieroglyphs": {
            "type": "boolean",
            "default": True,
            "description": {
                "en": "Show hieroglyphic numbers",
                "de": "Hieroglyphische Zahlen anzeigen",
                "ar": "عرض الأرقام الهيروغليفية"
            }
        },
        "show_dynasty": {
            "type": "boolean",
            "default": True,
            "description": {
                "en": "Show dynasty and regnal year",
                "de": "Dynastie und Regierungsjahr anzeigen",
                "ar": "عرض السلالة وسنة الحكم"
            }
        },
        "show_nile_status": {
            "type": "boolean",
            "default": True,
            "description": {
                "en": "Show Nile flood status",
                "de": "Nil-Flutstatus anzeigen",
                "ar": "عرض حالة فيضان النيل"
            }
        }
    }
}


class EgyptianCalendarSensor(AlternativeTimeSensorBase):
    """Sensor for displaying Ancient Egyptian Calendar."""
    
    # Class-level update interval
    UPDATE_INTERVAL = 3600  # Update every hour
    
    def __init__(self, base_name: str, hass: HomeAssistant) -> None:
        """Initialize the Egyptian calendar sensor."""
        super().__init__(base_name, hass)
        
        # Get translated name from metadata
        calendar_name = self._translate('name', 'Egyptian Calendar')
        
        # Set sensor attributes
        self._attr_name = f"{base_name} {calendar_name}"
        self._attr_unique_id = f"{base_name}_egyptian"
        self._attr_icon = CALENDAR_INFO.get("icon", "mdi:pyramid")
        
        # Configuration options
        self._show_hieroglyphs = True
        self._show_dynasty = True
        self._show_nile_status = True
        
        # Egyptian data
        self._egyptian_data = CALENDAR_INFO["egyptian_data"]
        
        _LOGGER.debug(f"Initialized Egyptian Calendar sensor: {self._attr_name}")
    
    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes."""
        attrs = super().extra_state_attributes
        
        # Add Egyptian-specific attributes
        if hasattr(self, '_egyptian_date'):
            attrs.update(self._egyptian_date)
            
            # Add description in user's language
            attrs["description"] = self._translate('description')
            
            # Add reference
            attrs["reference"] = CALENDAR_INFO.get('reference_url', '')
        
        return attrs
    
    def _get_hieroglyphic_number(self, num: int) -> str:
        """Convert number to hieroglyphic representation."""
        if not self._show_hieroglyphs:
            return str(num)
        
        hieroglyphs = self._egyptian_data["hieroglyphs"]
        result = ""
        
        if num <= 9:
            result = hieroglyphs.get(num, str(num))
        elif num <= 19:
            result = hieroglyphs[10] + hieroglyphs.get(num - 10, "")
        elif num <= 29:
            result = hieroglyphs[20] + hieroglyphs.get(num - 20, "")
        else:
            result = hieroglyphs[30]
        
        return result
    
    def _calculate_egyptian_date(self, earth_date: datetime) -> Dict[str, Any]:
        """Calculate Ancient Egyptian Calendar date from standard date."""
        
        # Egyptian new year around July 19 (Sirius rising)
        new_year_data = self._egyptian_data["new_year"]
        egyptian_new_year = datetime(earth_date.year, new_year_data["month"], new_year_data["day"])
        if earth_date < egyptian_new_year:
            egyptian_new_year = datetime(earth_date.year - 1, new_year_data["month"], new_year_data["day"])
        
        days_since_new_year = (earth_date - egyptian_new_year).days
        
        # Simulate dynasty and regnal year
        dynasty = (earth_date.year - 2000) // 30 + 1
        regnal_year = ((earth_date.year - 2000) % 30) + 1
        
        # Check for epagomenal days (last 5 days of year)
        if days_since_new_year >= 360:
            epagomenal_day = days_since_new_year - 359
            if epagomenal_day <= 5 and epagomenal_day > 0:
                god_birthday = self._egyptian_data["epagomenal_gods"][epagomenal_day - 1]
                
                result = {
                    "epagomenal": True,
                    "epagomenal_day": epagomenal_day,
                    "epagomenal_god": god_birthday,
                    "dynasty": dynasty,
                    "regnal_year": regnal_year,
                    "gregorian_date": earth_date.strftime("%Y-%m-%d"),
                    "full_date": f"Dynasty {dynasty}, Year {regnal_year} | Epagomenal Day {epagomenal_day} - Birthday of {god_birthday} 🎉"
                }
                return result
            
            days_since_new_year = days_since_new_year % 365
        
        # Calculate month and day
        month_index = min(days_since_new_year // 30, 11)
        day_of_month = (days_since_new_year % 30) + 1
        
        month_data = self._egyptian_data["months"][month_index]
        
        # Calculate decan (10-day week)
        decan_index = min((day_of_month - 1) // 10, 2)
        decan_data = self._egyptian_data["decans"][decan_index]
        day_in_decan = ((day_of_month - 1) % 10) + 1
        
        # Get hieroglyphic day
        hieroglyph_day = self._get_hieroglyphic_number(day_of_month)
        
        # Determine Egyptian hour
        hour = earth_date.hour
        is_night = hour < 6 or hour >= 18
        
        if is_night:
            if hour >= 18:
                egyptian_hour_index = hour - 18
            else:
                egyptian_hour_index = hour + 6
            egyptian_hour = self._egyptian_data["night_hours"][min(egyptian_hour_index, 11)]
            time_symbol = "🌙"
            time_period = "Night"
        else:
            egyptian_hour_index = hour - 6
            egyptian_hour = self._egyptian_data["day_hours"][min(egyptian_hour_index, 11)]
            time_symbol = "☀️"
            time_period = "Day"
        
        # Get Nile status
        nile_data = self._egyptian_data["nile_status"][month_data["season"]]
        
        # Format the date
        date_parts = []
        
        if self._show_dynasty:
            date_parts.append(f"Dynasty {dynasty} Year {regnal_year}")
        
        date_parts.append(f"{hieroglyph_day} {day_of_month} {month_data['name']} ({month_data['season']})")
        date_parts.append(f"{decan_data['name']} Day {day_in_decan}")
        date_parts.append(f"{time_symbol} {egyptian_hour}")
        date_parts.append(month_data['god'])
        
        if self._show_nile_status:
            date_parts.append(f"{nile_data['emoji']} {nile_data['status']}")
        
        full_date = " | ".join(date_parts)
        
        result = {
            "dynasty": dynasty,
            "regnal_year": regnal_year,
            "month": month_data["name"],
            "month_index": month_index + 1,
            "day": day_of_month,
            "day_hieroglyph": hieroglyph_day,
            "season": month_data["season"],
            "season_emoji": month_data["season_emoji"],
            "decan": decan_data["name"],
            "decan_symbol": decan_data["symbol"],
            "decan_day": day_in_decan,
            "patron_god": month_data["god"],
            "egyptian_hour": egyptian_hour,
            "time_period": time_period,
            "time_symbol": time_symbol,
            "nile_status": nile_data["status"],
            "nile_emoji": nile_data["emoji"],
            "gregorian_date": earth_date.strftime("%Y-%m-%d"),
            "epagomenal": False,
            "full_date": full_date
        }
        
        return result
    
    def update(self) -> None:
        """Update the sensor."""
        now = datetime.now()
        self._egyptian_date = self._calculate_egyptian_date(now)
        
        # Set state to full Egyptian date
        self._state = self._egyptian_date["full_date"]
        
        _LOGGER.debug(f"Updated Egyptian Calendar to {self._state}")