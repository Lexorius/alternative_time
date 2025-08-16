"""Maya Calendar implementation - Version 2.5."""
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

# Update interval in seconds (3600 seconds = 1 hour, dates change slowly)
UPDATE_INTERVAL = 3600

# Complete calendar information for auto-discovery
CALENDAR_INFO = {
    "id": "maya",
    "version": "2.5.0", 
    "icon": "mdi:pyramid",
    "category": "historical",
    "accuracy": "cultural",
    "update_interval": UPDATE_INTERVAL,
    
    # Multi-language names
    "name": {
        "en": "Maya Calendar",
        "de": "Maya-Kalender",
        "es": "Calendario Maya",
        "fr": "Calendrier Maya",
        "it": "Calendario Maya",
        "nl": "Maya Kalender",
        "pt": "Calendário Maia",
        "ru": "Календарь майя",
        "ja": "マヤ暦",
        "zh": "玛雅历",
        "ko": "마야 달력"
    },
    
    # Short descriptions for UI
    "description": {
        "en": "Long Count, Tzolk'in and Haab calendars (e.g. 13.0.12.1.15 | 8 Ahau | 3 Pop)",
        "de": "Lange Zählung, Tzolk'in und Haab Kalender (z.B. 13.0.12.1.15 | 8 Ahau | 3 Pop)",
        "es": "Cuenta Larga, calendarios Tzolk'in y Haab (ej. 13.0.12.1.15 | 8 Ahau | 3 Pop)",
        "fr": "Compte long, calendriers Tzolk'in et Haab (ex. 13.0.12.1.15 | 8 Ahau | 3 Pop)",
        "it": "Conto lungo, calendari Tzolk'in e Haab (es. 13.0.12.1.15 | 8 Ahau | 3 Pop)",
        "nl": "Lange Telling, Tzolk'in en Haab kalenders (bijv. 13.0.12.1.15 | 8 Ahau | 3 Pop)",
        "pt": "Contagem Longa, calendários Tzolk'in e Haab (ex. 13.0.12.1.15 | 8 Ahau | 3 Pop)",
        "ru": "Длинный счёт, календари Цолькин и Хааб (напр. 13.0.12.1.15 | 8 Ahau | 3 Pop)",
        "ja": "長期暦、ツォルキン暦、ハアブ暦（例：13.0.12.1.15 | 8 Ahau | 3 Pop）",
        "zh": "长计历、卓尔金历和哈布历（例：13.0.12.1.15 | 8 Ahau | 3 Pop）",
        "ko": "장기력, 촐킨력, 하브력 (예: 13.0.12.1.15 | 8 Ahau | 3 Pop)"
    },
    
    # Detailed information for documentation
    "detailed_info": {
        "en": {
            "overview": "The Maya calendar system consists of three interlocking calendars",
            "long_count": "Long Count: Linear count of days (Kin=1 day, Uinal=20 kin, Tun=360 days, Katun=7200 days, Baktun=144000 days)",
            "tzolkin": "Tzolk'in: 260-day sacred calendar combining 13 numbers with 20 day names",
            "haab": "Haab: 365-day solar calendar with 18 months of 20 days + 5 day Uayeb period",
            "correlation": "Using GMT correlation constant 584283 (December 21, 2012 = 13.0.0.0.0)",
            "usage": "Used for religious ceremonies, agricultural planning, and historical records",
            "note": "The 13th baktun ended on December 21, 2012, beginning the 14th baktun"
        },
        "de": {
            "overview": "Das Maya-Kalendersystem besteht aus drei ineinandergreifenden Kalendern",
            "long_count": "Lange Zählung: Lineare Tageszählung (Kin=1 Tag, Uinal=20 Kin, Tun=360 Tage, Katun=7200 Tage, Baktun=144000 Tage)",
            "tzolkin": "Tzolk'in: 260-Tage heiliger Kalender kombiniert 13 Zahlen mit 20 Tagesnamen",
            "haab": "Haab: 365-Tage Sonnenkalender mit 18 Monaten zu 20 Tagen + 5 Tage Uayeb-Periode",
            "correlation": "Verwendet GMT-Korrelationskonstante 584283 (21. Dezember 2012 = 13.0.0.0.0)",
            "usage": "Verwendet für religiöse Zeremonien, landwirtschaftliche Planung und historische Aufzeichnungen",
            "note": "Der 13. Baktun endete am 21. Dezember 2012, der 14. Baktun begann"
        }
    },
    
    # Maya-specific data
    "maya_data": {
        # Long Count units
        "long_count_units": {
            "kin": 1,
            "uinal": 20,
            "tun": 360,
            "katun": 7200,
            "baktun": 144000
        },
        
        # Tzolk'in day names (20-day cycle)
        "tzolkin_days": [
            "Imix", "Ik", "Akbal", "Kan", "Chicchan",
            "Cimi", "Manik", "Lamat", "Muluc", "Oc",
            "Chuen", "Eb", "Ben", "Ix", "Men",
            "Cib", "Caban", "Etznab", "Cauac", "Ahau"
        ],
        
        # Tzolk'in day meanings
        "tzolkin_meanings": {
            "Imix": "Crocodile/Water lily",
            "Ik": "Wind",
            "Akbal": "Night/House",
            "Kan": "Seed/Lizard",
            "Chicchan": "Serpent",
            "Cimi": "Death",
            "Manik": "Deer",
            "Lamat": "Rabbit/Venus",
            "Muluc": "Water",
            "Oc": "Dog",
            "Chuen": "Monkey",
            "Eb": "Grass/Road",
            "Ben": "Reed",
            "Ix": "Jaguar",
            "Men": "Eagle",
            "Cib": "Vulture/Owl",
            "Caban": "Earth",
            "Etznab": "Flint/Knife",
            "Cauac": "Storm",
            "Ahau": "Lord/Sun"
        },
        
        # Haab month names (365-day solar calendar)
        "haab_months": [
            "Pop", "Uo", "Zip", "Zotz", "Tzec",
            "Xul", "Yaxkin", "Mol", "Chen", "Yax",
            "Zac", "Ceh", "Mac", "Kankin", "Muan",
            "Pax", "Kayab", "Cumku", "Uayeb"  # Uayeb is only 5 days
        ],
        
        # Haab month meanings
        "haab_meanings": {
            "Pop": "Mat",
            "Uo": "Frog",
            "Zip": "Red",
            "Zotz": "Bat",
            "Tzec": "Skull",
            "Xul": "End",
            "Yaxkin": "New Sun",
            "Mol": "Water",
            "Chen": "Black Storm",
            "Yax": "Green Storm",
            "Zac": "White Storm",
            "Ceh": "Red Storm",
            "Mac": "Enclosed",
            "Kankin": "Yellow Sun",
            "Muan": "Owl",
            "Pax": "Planting Time",
            "Kayab": "Turtle",
            "Cumku": "Dark God",
            "Uayeb": "Nameless Days"
        },
        
        # Reference date: December 21, 2012 = 13.0.0.0.0
        "reference_date": {
            "gregorian": "2012-12-21",
            "long_count": [13, 0, 0, 0, 0],
            "tzolkin_number": 4,
            "tzolkin_day": 19,  # Ahau
            "haab_day": 3,
            "haab_month": 13  # Kankin
        },
        
        # GMT correlation constant
        "gmt_correlation": 584283
    },
    
    # Additional metadata
    "reference_url": "https://en.wikipedia.org/wiki/Maya_calendar",
    "documentation_url": "http://www.famsi.org/research/pitts/MayaGlyphsBook.pdf",
    "origin": "Maya civilization, Mesoamerica",
    "created_by": "Maya civilization",
    "period": "Pre-Classic to Post-Classic period (2000 BCE - 1500 CE)",
    
    # Example format
    "example": "13.0.12.1.15 | 8 Ahau | 3 Pop",
    "example_meaning": "13th baktun, 0 katun, 12 tun, 1 uinal, 15 kin | 8th day Ahau | 3rd day of Pop",
    
    # Related calendars
    "related": ["aztec", "gregorian"],
    
    # Tags for searching and filtering
    "tags": [
        "historical", "maya", "mesoamerican", "ancient", "sacred",
        "astronomical", "tzolkin", "haab", "long_count", "baktun",
        "cultural", "religious", "agricultural"
    ],
    
    # Special features
    "features": {
        "multiple_cycles": True,
        "sacred_calendar": True,
        "solar_calendar": True,
        "long_count": True,
        "venus_cycle": True,
        "precision": "day"
    },
    
    # Configuration options for this calendar
    "config_options": {
        "show_meanings": {
            "type": "boolean",
            "default": True,
            "description": {
                "en": "Show meanings of day and month names",
                "de": "Zeige Bedeutungen der Tages- und Monatsnamen"
            }
        },
        "show_glyphs": {
            "type": "boolean",
            "default": False,
            "description": {
                "en": "Show Unicode approximations of Maya glyphs",
                "de": "Zeige Unicode-Näherungen der Maya-Glyphen"
            }
        },
        "correlation_constant": {
            "type": "select",
            "default": "GMT",
            "options": ["GMT", "Thompson", "Spinden"],
            "description": {
                "en": "Select correlation constant for date conversion",
                "de": "Wähle Korrelationskonstante für Datumsumrechnung"
            }
        }
    }
}


class MayaCalendarSensor(AlternativeTimeSensorBase):
    """Sensor for displaying Maya Calendar."""
    
    # Class-level update interval
    UPDATE_INTERVAL = 3600  # Update every hour
    
    def __init__(self, base_name: str, hass: HomeAssistant) -> None:
        """Initialize the Maya calendar sensor."""
        super().__init__(base_name, hass)
        
        # Get translated name from metadata
        calendar_name = self._translate('name', 'Maya Calendar')
        
        # Set sensor attributes
        self._attr_name = f"{base_name} {calendar_name}"
        self._attr_unique_id = f"{base_name}_maya_calendar"
        self._attr_icon = CALENDAR_INFO.get("icon", "mdi:pyramid")
        
        # Configuration options
        self._show_meanings = True
        self._show_glyphs = False
        self._correlation = "GMT"
        
        # Maya data
        self._maya_data = CALENDAR_INFO["maya_data"]
        
        _LOGGER.debug(f"Initialized Maya Calendar sensor: {self._attr_name}")
    
    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes."""
        attrs = super().extra_state_attributes
        
        # Add Maya-specific attributes
        if hasattr(self, '_maya_date'):
            attrs.update(self._maya_date)
            
            # Add description in user's language
            attrs["description"] = self._translate('description')
            
            # Add reference
            attrs["reference"] = CALENDAR_INFO.get('reference_url', '')
            
            # Add correlation constant
            attrs["correlation_constant"] = self._correlation
        
        return attrs
    
    def _calculate_maya_date(self, earth_date: datetime) -> Dict[str, Any]:
        """Calculate Maya Calendar date from standard date."""
        
        # Reference date: December 21, 2012 = 13.0.0.0.0
        reference_date = datetime(2012, 12, 21)
        days_since_reference = (earth_date - reference_date).days
        
        # Calculate Long Count components
        total_days = days_since_reference
        
        # Each unit in the Long Count
        kin = total_days % 20
        uinal = (total_days // 20) % 18
        tun = (total_days // 360) % 20
        katun = (total_days // 7200) % 20
        baktun = 13 + (total_days // 144000)  # Starting from baktun 13
        
        # Calculate Tzolk'in (260-day cycle)
        ref_tzolkin = self._maya_data["reference_date"]
        tzolkin_day_number = ((days_since_reference + ref_tzolkin["tzolkin_number"] - 1) % 13) + 1
        tzolkin_day_index = (days_since_reference + ref_tzolkin["tzolkin_day"]) % 20
        tzolkin_day_name = self._maya_data["tzolkin_days"][tzolkin_day_index]
        
        # Calculate Haab (365-day cycle)
        haab_reference = 243 + 3  # Day 3 of Kankin (14th month)
        haab_day_total = (haab_reference + days_since_reference) % 365
        
        # Determine month and day
        if haab_day_total < 360:  # First 18 months (20 days each)
            haab_month_index = haab_day_total // 20
            haab_day_of_month = haab_day_total % 20
        else:  # Uayeb (5-day month)
            haab_month_index = 18
            haab_day_of_month = haab_day_total - 360
        
        haab_month_name = self._maya_data["haab_months"][haab_month_index]
        
        # Calculate Calendar Round position (52-year cycle)
        # Calendar Round repeats every 18,980 days (52 Haab years = 73 Tzolk'in cycles)
        calendar_round_day = days_since_reference % 18980
        calendar_round_position = (calendar_round_day / 18980) * 100  # Percentage through cycle
        
        # Determine if it's a special day
        special_days = []
        if tzolkin_day_name == "Ahau" and tzolkin_day_number == 8:
            special_days.append("🌟 Sacred day of the Sun Lord")
        if haab_month_name == "Uayeb":
            special_days.append("⚠️ Nameless days - time of bad luck")
        if kin == 0 and uinal == 0:
            special_days.append("🎊 New Tun begins")
        if kin == 0 and uinal == 0 and tun == 0:
            special_days.append("🎉 New Katun begins")
        
        # Format Long Count
        long_count = f"{baktun}.{katun}.{tun}.{uinal}.{kin}"
        
        # Format Tzolk'in
        tzolkin = f"{tzolkin_day_number} {tzolkin_day_name}"
        
        # Format Haab
        haab = f"{haab_day_of_month} {haab_month_name}"
        
        # Full format
        full_date = f"{long_count} | {tzolkin} | {haab}"
        
        result = {
            "long_count": long_count,
            "baktun": baktun,
            "katun": katun,
            "tun": tun,
            "uinal": uinal,
            "kin": kin,
            "tzolkin": tzolkin,
            "tzolkin_number": tzolkin_day_number,
            "tzolkin_day": tzolkin_day_name,
            "haab": haab,
            "haab_day": haab_day_of_month,
            "haab_month": haab_month_name,
            "calendar_round_position": f"{calendar_round_position:.1f}%",
            "gregorian_date": earth_date.strftime("%Y-%m-%d"),
            "full_date": full_date
        }
        
        # Add meanings if enabled
        if self._show_meanings:
            if tzolkin_day_name in self._maya_data["tzolkin_meanings"]:
                result["tzolkin_meaning"] = self._maya_data["tzolkin_meanings"][tzolkin_day_name]
            if haab_month_name in self._maya_data["haab_meanings"]:
                result["haab_meaning"] = self._maya_data["haab_meanings"][haab_month_name]
        
        # Add special days
        if special_days:
            result["special_days"] = " | ".join(special_days)
        
        return result
    
    def update(self) -> None:
        """Update the sensor."""
        now = datetime.now()
        self._maya_date = self._calculate_maya_date(now)
        
        # Set state to full Maya date
        self._state = self._maya_date["full_date"]
        
        _LOGGER.debug(f"Updated Maya Calendar to {self._state}")