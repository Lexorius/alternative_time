"""Shire Calendar (Hobbit/LOTR) implementation - Version 2.5."""
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
    "id": "shire",
    "version": "2.5.0",
    "icon": "mdi:pipe",
    "category": "fantasy",
    "accuracy": "fictional",
    "update_interval": UPDATE_INTERVAL,
    
    # Multi-language names
    "name": {
        "en": "Shire Calendar (LOTR)",
        "de": "Auenland-Kalender (HdR)",
        "es": "Calendario de la Comarca (ESDLA)",
        "fr": "Calendrier de la Comté (SdA)",
        "it": "Calendario della Contea (SdA)",
        "nl": "Gouw Kalender (LOTR)",
        "pt": "Calendário do Condado (SdA)",
        "ru": "Календарь Шира (ВК)",
        "ja": "ホビット庄暦",
        "zh": "夏尔历",
        "ko": "샤이어 달력"
    },
    
    # Short descriptions for UI
    "description": {
        "en": "Hobbit calendar from Lord of the Rings (e.g. S.R. 1624, Afteryule 16)",
        "de": "Hobbit-Kalender aus Herr der Ringe (z.B. A.Z. 1624, Nachjul 16)",
        "es": "Calendario hobbit de El Señor de los Anillos",
        "fr": "Calendrier hobbit du Seigneur des Anneaux",
        "it": "Calendario hobbit del Signore degli Anelli"
    },
    
    # Detailed information for documentation
    "detailed_info": {
        "en": {
            "overview": "The Shire Calendar is used by Hobbits in Middle-earth",
            "structure": "12 months of 30 days each, plus special days (Yule and Lithe)",
            "year_start": "Year begins at 2 Yule (around December 21)",
            "weeks": "7-day weeks from Sterday to Highday",
            "reckoning": "Shire Reckoning (S.R.) counts from colonization of the Shire",
            "meals": "Seven daily meals: First Breakfast, Second Breakfast, Elevenses, Luncheon, Afternoon Tea, Dinner, Supper",
            "special": "Bilbo and Frodo's birthday on September 22",
            "note": "LOTR ends in T.A. 3021 = S.R. 1421"
        },
        "de": {
            "overview": "Der Auenland-Kalender wird von Hobbits in Mittelerde verwendet",
            "structure": "12 Monate mit je 30 Tagen, plus Sondertage (Jul und Lithe)",
            "year_start": "Jahr beginnt am 2. Jul (um den 21. Dezember)",
            "weeks": "7-Tage-Wochen von Sterntag bis Hochtag",
            "reckoning": "Auenland-Zeitrechnung (A.Z.) zählt seit Besiedlung des Auenlandes",
            "meals": "Sieben tägliche Mahlzeiten: Erstes Frühstück, Zweites Frühstück, Elfuhrtee, Mittagessen, Nachmittagstee, Abendessen, Nachtmahl",
            "special": "Bilbos und Frodos Geburtstag am 22. September",
            "note": "HdR endet in D.Z. 3021 = A.Z. 1421"
        }
    },
    
    # Shire-specific data
    "shire_data": {
        # Shire months
        "months": [
            {"name": "Afteryule", "days": 30, "season": "Winter"},
            {"name": "Solmath", "days": 30, "season": "Winter"},
            {"name": "Rethe", "days": 30, "season": "Spring"},
            {"name": "Astron", "days": 30, "season": "Spring"},
            {"name": "Thrimidge", "days": 30, "season": "Spring"},
            {"name": "Forelithe", "days": 30, "season": "Summer"},
            {"name": "Afterlithe", "days": 30, "season": "Summer"},
            {"name": "Wedmath", "days": 30, "season": "Summer"},
            {"name": "Halimath", "days": 30, "season": "Harvest"},
            {"name": "Winterfilth", "days": 30, "season": "Harvest"},
            {"name": "Blotmath", "days": 30, "season": "Harvest"},
            {"name": "Foreyule", "days": 30, "season": "Winter"}
        ],
        
        # Shire weekdays
        "weekdays": [
            "Sterday",    # Saturday (Stars)
            "Sunday",     # Sunday (Sun)
            "Monday",     # Monday (Moon)
            "Trewsday",   # Tuesday (Trees)
            "Hevensday",  # Wednesday (Heavens)
            "Mersday",    # Thursday (Sea)
            "Highday"     # Friday (High day)
        ],
        
        # Special days
        "special_days": {
            (1, 1): "🎊 2 Yule - New Year's Day",
            (3, 25): "🌸 Elven New Year",
            (6, 21): "☀️ 1 Lithe - Midsummer's Eve",
            (6, 22): "🎉 Mid-year's Day",
            (6, 23): "🎊 Overlithe (leap years only)",
            (6, 24): "☀️ 2 Lithe",
            (9, 22): "🎂 Bilbo & Frodo's Birthday!",
            (12, 21): "❄️ 1 Yule - Midwinter"
        },
        
        # Hobbit meals
        "meals": {
            (6, 8): {"name": "First Breakfast", "emoji": "🍳"},
            (8, 9): {"name": "Second Breakfast", "emoji": "🥐"},
            (11, 12): {"name": "Elevenses", "emoji": "☕"},
            (12, 14): {"name": "Luncheon", "emoji": "🍽️"},
            (15, 16): {"name": "Afternoon Tea", "emoji": "🫖"},
            (18, 20): {"name": "Dinner", "emoji": "🍖"},
            (20, 22): {"name": "Supper", "emoji": "🍷"}
        },
        
        # Time periods
        "time_periods": {
            (5, 7): "Dawn - The Shire awakens",
            (7, 12): "Morning - Time for adventures",
            (12, 17): "Afternoon - Pleasant walking weather",
            (17, 20): "Evening - Smoke rings and tales",
            (20, 23): "Night - Stars are out",
            (23, 5): "Late Night - All respectable hobbits abed"
        },
        
        # Hobbit family names for name days
        "name_days": {
            1: "Baggins", 5: "Took", 10: "Brandybuck",
            15: "Gamgee", 20: "Cotton", 25: "Proudfoot", 30: "Bracegirdle"
        },
        
        # Shire Reckoning base year
        "sr_base": 1600,  # Year 2000 = S.R. 1600 for our conversion
        "earth_base": 2000
    },
    
    # Additional metadata
    "reference_url": "https://tolkiengateway.net/wiki/Shire_Calendar",
    "documentation_url": "http://shire-reckoning.com/calendar.html",
    "origin": "J.R.R. Tolkien's Middle-earth",
    "created_by": "J.R.R. Tolkien",
    "introduced": "The Hobbit (1937) / The Lord of the Rings (1954-1955)",
    
    # Example format
    "example": "S.R. 1624, Afteryule 16 (Trewsday)",
    "example_meaning": "Shire Reckoning year 1624, 16th of Afteryule, Trewsday",
    
    # Related calendars
    "related": ["rivendell", "gregorian"],
    
    # Tags for searching and filtering
    "tags": [
        "fantasy", "tolkien", "hobbit", "lotr", "shire",
        "middle_earth", "bilbo", "frodo", "gandalf"
    ],
    
    # Special features
    "features": {
        "seven_meals": True,
        "special_days": True,
        "moon_phases": True,
        "hobbit_customs": True,
        "precision": "day"
    },
    
    # Configuration options
    "config_options": {
        "show_meals": {
            "type": "boolean",
            "default": True,
            "description": {
                "en": "Show current Hobbit meal time",
                "de": "Aktuelle Hobbit-Mahlzeit anzeigen"
            }
        },
        "show_moon": {
            "type": "boolean",
            "default": True,
            "description": {
                "en": "Show moon phase",
                "de": "Mondphase anzeigen"
            }
        },
        "show_name_day": {
            "type": "boolean",
            "default": True,
            "description": {
                "en": "Show Hobbit family name day",
                "de": "Hobbit-Familiennamentag anzeigen"
            }
        }
    }
}


class ShireCalendarSensor(AlternativeTimeSensorBase):
    """Sensor for displaying Shire Calendar from Middle-earth."""
    
    # Class-level update interval
    UPDATE_INTERVAL = 3600  # Update every hour
    
    def __init__(self, base_name: str, hass: HomeAssistant) -> None:
        """Initialize the Shire calendar sensor."""
        super().__init__(base_name, hass)
        
        # Get translated name from metadata
        calendar_name = self._translate('name', 'Shire Calendar')
        
        # Set sensor attributes
        self._attr_name = f"{base_name} {calendar_name}"
        self._attr_unique_id = f"{base_name}_shire_calendar"
        self._attr_icon = CALENDAR_INFO.get("icon", "mdi:pipe")
        
        # Configuration options
        self._show_meals = True
        self._show_moon = True
        self._show_name_day = True
        
        # Shire data
        self._shire_data = CALENDAR_INFO["shire_data"]
        
        _LOGGER.debug(f"Initialized Shire Calendar sensor: {self._attr_name}")
    
    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes."""
        attrs = super().extra_state_attributes
        
        # Add Shire-specific attributes
        if hasattr(self, '_shire_date'):
            attrs.update(self._shire_date)
            
            # Add description in user's language
            attrs["description"] = self._translate('description')
            
            # Add reference
            attrs["reference"] = CALENDAR_INFO.get('reference_url', '')
        
        return attrs
    
    def _get_meal_time(self, hour: int) -> Dict[str, str]:
        """Get current Hobbit meal time."""
        for (start, end), meal in self._shire_data["meals"].items():
            if start <= hour < end:
                return meal
        return {"name": "Resting Time", "emoji": "🌙"}
    
    def _get_time_period(self, hour: int) -> str:
        """Get time of day description."""
        for (start, end), period in self._shire_data["time_periods"].items():
            if start <= hour or (start > end and hour < end):
                return period
        return "Time for adventures"
    
    def _get_moon_phase(self, day: int) -> str:
        """Calculate simplified moon phase."""
        day_in_lunar = day % 29.5
        if day_in_lunar < 2:
            return "🌑 New Moon"
        elif day_in_lunar < 7:
            return "🌒 Waxing Crescent"
        elif day_in_lunar < 9:
            return "🌓 First Quarter"
        elif day_in_lunar < 14:
            return "🌔 Waxing Gibbous"
        elif day_in_lunar < 16:
            return "🌕 Full Moon"
        elif day_in_lunar < 21:
            return "🌖 Waning Gibbous"
        elif day_in_lunar < 23:
            return "🌗 Last Quarter"
        else:
            return "🌘 Waning Crescent"
    
    def _calculate_shire_date(self, earth_date: datetime) -> Dict[str, Any]:
        """Calculate Shire Reckoning date from Earth date."""
        
        # Calculate Shire year
        years_since_base = earth_date.year - self._shire_data["earth_base"]
        shire_year = self._shire_data["sr_base"] + years_since_base
        
        # Map Earth months to Shire months (simplified)
        month_index = min(earth_date.month - 1, 11)
        month_data = self._shire_data["months"][month_index]
        
        # Shire day (1-30 for regular days)
        shire_day = min(earth_date.day, 30)
        
        # Weekday (shift to make Sterday = Saturday)
        weekday_index = (earth_date.weekday() + 2) % 7
        shire_weekday = self._shire_data["weekdays"][weekday_index]
        
        # Check for special days
        special_day = self._shire_data["special_days"].get((earth_date.month, earth_date.day), "")
        
        # Meal time
        meal_data = self._get_meal_time(earth_date.hour) if self._show_meals else {}
        
        # Time period
        time_of_day = self._get_time_period(earth_date.hour)
        
        # Moon phase
        moon_phase = self._get_moon_phase(earth_date.day) if self._show_moon else ""
        
        # Hobbit name day
        name_day = self._shire_data["name_days"].get(shire_day, "") if self._show_name_day else ""
        
        result = {
            "year": shire_year,
            "month": month_data["name"],
            "day": shire_day,
            "weekday": shire_weekday,
            "season": month_data["season"],
            "time_of_day": time_of_day,
            "gregorian_date": earth_date.strftime("%Y-%m-%d"),
            "full_date": f"S.R. {shire_year}, {month_data['name']} {shire_day}"
        }
        
        if special_day:
            result["special_day"] = special_day
        
        if meal_data:
            result["meal_time"] = f"{meal_data['emoji']} {meal_data['name']}"
        
        if moon_phase:
            result["moon_phase"] = moon_phase
        
        if name_day:
            result["hobbit_name_day"] = name_day
        
        return result
    
    def update(self) -> None:
        """Update the sensor."""
        now = datetime.now()
        self._shire_date = self._calculate_shire_date(now)
        
        # Set state to formatted Shire date
        self._state = self._shire_date["full_date"]
        
        _LOGGER.debug(f"Updated Shire Calendar to {self._state}")