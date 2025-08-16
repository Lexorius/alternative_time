"""Star Wars Galactic Standard Calendar implementation - Version 2.5."""
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
    "id": "star_wars",
    "version": "2.5.0",
    "icon": "mdi:death-star-variant",
    "category": "scifi",
    "accuracy": "fictional",
    "update_interval": UPDATE_INTERVAL,
    
    # Multi-language names
    "name": {
        "en": "Star Wars Galactic Calendar",
        "de": "Star Wars Galaktischer Kalender",
        "es": "Calendario Galáctico de Star Wars",
        "fr": "Calendrier Galactique Star Wars",
        "it": "Calendario Galattico di Star Wars",
        "nl": "Star Wars Galactische Kalender",
        "pt": "Calendário Galáctico Star Wars",
        "ru": "Галактический календарь Звездных войн",
        "ja": "スター・ウォーズ銀河標準暦",
        "zh": "星球大战银河标准历",
        "ko": "스타워즈 은하 표준력"
    },
    
    # Short descriptions for UI
    "description": {
        "en": "Galactic Standard Calendar from Star Wars (e.g. 35:3:21 GrS)",
        "de": "Galaktischer Standardkalender aus Star Wars (z.B. 35:3:21 GrS)",
        "es": "Calendario Estándar Galáctico de Star Wars (ej. 35:3:21 GrS)",
        "fr": "Calendrier Standard Galactique de Star Wars (ex. 35:3:21 GrS)",
        "it": "Calendario Standard Galattico di Star Wars (es. 35:3:21 GrS)",
        "nl": "Galactische Standaard Kalender uit Star Wars (bijv. 35:3:21 GrS)",
        "pt": "Calendário Padrão Galáctico de Star Wars (ex. 35:3:21 GrS)",
        "ru": "Галактический стандартный календарь из Звездных войн (напр. 35:3:21 GrS)",
        "ja": "スター・ウォーズの銀河標準暦（例：35:3:21 GrS）",
        "zh": "星球大战银河标准历（例：35:3:21 GrS）",
        "ko": "스타워즈 은하 표준력 (예: 35:3:21 GrS)"
    },
    
    # Detailed information for documentation
    "detailed_info": {
        "en": {
            "overview": "The Galactic Standard Calendar is the primary calendar system used in the Star Wars galaxy",
            "structure": "368-day year, 10 months, 7 weeks per month, 5 days per week",
            "epoch": "Based on the Treaty of Coruscant (BTC/ATC) or Great ReSynchronization (GrS)",
            "months": "Each month has 7 weeks of 5 days, plus 3 festival weeks and 3 holidays",
            "time": "24 standard hours per day, 60 minutes per hour",
            "usage": "Used throughout the galaxy for commerce, government, and military operations",
            "eras": "Multiple era systems: BBY/ABY (Battle of Yavin), BTC/ATC (Treaty of Coruscant), GrS (Great ReSynchronization)",
            "note": "The calendar includes galactic festivals that span entire weeks"
        },
        "de": {
            "overview": "Der Galaktische Standardkalender ist das primäre Kalendersystem in der Star Wars Galaxie",
            "structure": "368-Tage-Jahr, 10 Monate, 7 Wochen pro Monat, 5 Tage pro Woche",
            "epoch": "Basiert auf dem Vertrag von Coruscant (BTC/ATC) oder der Großen ReSynchronisation (GrS)",
            "months": "Jeder Monat hat 7 Wochen mit 5 Tagen, plus 3 Festwochen und 3 Feiertage",
            "time": "24 Standardstunden pro Tag, 60 Minuten pro Stunde",
            "usage": "Wird galaxisweit für Handel, Regierung und Militär verwendet",
            "eras": "Mehrere Ära-Systeme: BBY/ABY (Schlacht von Yavin), BTC/ATC (Vertrag von Coruscant), GrS (Große ReSynchronisation)",
            "note": "Der Kalender enthält galaktische Festivals, die ganze Wochen dauern"
        }
    },
    
    # Star Wars-specific data
    "star_wars_data": {
        # Galactic Standard months
        "months": [
            {"num": 1, "name": "Month 1", "festival": "New Year Fete Week", "days": 35},
            {"num": 2, "name": "Month 2", "festival": None, "days": 35},
            {"num": 3, "name": "Month 3", "festival": None, "days": 35},
            {"num": 4, "name": "Month 4", "festival": None, "days": 35},
            {"num": 5, "name": "Month 5", "festival": "Festival of Stars Week", "days": 35},
            {"num": 6, "name": "Month 6", "festival": None, "days": 35},
            {"num": 7, "name": "Month 7", "festival": None, "days": 35},
            {"num": 8, "name": "Month 8", "festival": None, "days": 35},
            {"num": 9, "name": "Month 9", "festival": None, "days": 35},
            {"num": 10, "name": "Month 10", "festival": "Festival of Life Week", "days": 35}
        ],
        
        # Days of the week
        "weekdays": [
            {"name": "Primeday", "abbr": "Pri", "work": True},
            {"name": "Centaxday", "abbr": "Cen", "work": True},
            {"name": "Taungsday", "abbr": "Tau", "work": True},
            {"name": "Zhellday", "abbr": "Zhe", "work": True},
            {"name": "Benduday", "abbr": "Ben", "work": False}
        ],
        
        # Week types
        "week_types": [
            "First Week",
            "Second Week", 
            "Third Week",
            "Fourth Week",
            "Fifth Week",
            "Sixth Week",
            "Seventh Week"
        ],
        
        # Galactic holidays (in addition to festival weeks)
        "holidays": [
            {"name": "Empire Day", "date": (6, 24), "era": "Imperial"},
            {"name": "Republic Day", "date": (3, 14), "era": "Republic"},
            {"name": "Boonta Eve", "date": (4, 15), "era": "All"}
        ],
        
        # Era systems
        "eras": {
            "grs": {"name": "Great ReSynchronization", "abbr": "GrS", "epoch_year": 35},
            "bby_aby": {"name": "Battle of Yavin", "abbr_before": "BBY", "abbr_after": "ABY", "epoch_year": 0},
            "btc_atc": {"name": "Treaty of Coruscant", "abbr_before": "BTC", "abbr_after": "ATC", "epoch_year": 3653}
        },
        
        # Time periods
        "time_periods": [
            {"name": "Night", "hours": (0, 6), "emoji": "🌙"},
            {"name": "Dawn", "hours": (6, 8), "emoji": "🌅"},
            {"name": "Morning", "hours": (8, 12), "emoji": "☀️"},
            {"name": "Midday", "hours": (12, 14), "emoji": "🌞"},
            {"name": "Afternoon", "hours": (14, 18), "emoji": "🌤️"},
            {"name": "Dusk", "hours": (18, 20), "emoji": "🌇"},
            {"name": "Evening", "hours": (20, 24), "emoji": "🌃"}
        ],
        
        # Galactic regions (for flavor)
        "regions": [
            "Core Worlds",
            "Inner Rim",
            "Mid Rim",
            "Outer Rim",
            "Unknown Regions",
            "Wild Space"
        ],
        
        # Major planets (for time zone reference)
        "major_planets": {
            "Coruscant": {"region": "Core Worlds", "timezone": 0, "capital": True},
            "Tatooine": {"region": "Outer Rim", "timezone": -3, "capital": False},
            "Naboo": {"region": "Mid Rim", "timezone": 1, "capital": False},
            "Alderaan": {"region": "Core Worlds", "timezone": 0, "capital": False},
            "Endor": {"region": "Outer Rim", "timezone": -5, "capital": False},
            "Hoth": {"region": "Outer Rim", "timezone": -4, "capital": False},
            "Dagobah": {"region": "Outer Rim", "timezone": -6, "capital": False},
            "Mandalore": {"region": "Outer Rim", "timezone": -2, "capital": False}
        }
    },
    
    # Additional metadata
    "reference_url": "https://starwars.fandom.com/wiki/Galactic_Standard_Calendar",
    "documentation_url": "https://starwars.fandom.com/wiki/Time",
    "origin": "Star Wars Universe",
    "created_by": "George Lucas / Lucasfilm",
    "introduced": "Star Wars Expanded Universe",
    
    # Example format
    "example": "35:3:21 GrS | Taungsday | Third Week",
    "example_meaning": "Year 35, Month 3, Day 21 (Great ReSynchronization) | Taungsday | Third Week",
    
    # Related calendars
    "related": ["stardate", "eve_online", "warhammer40k_imperial"],
    
    # Tags for searching and filtering
    "tags": [
        "scifi", "star_wars", "galactic", "space", "fictional",
        "coruscant", "republic", "empire", "jedi", "sith"
    ],
    
    # Special features
    "features": {
        "festival_weeks": True,
        "multiple_eras": True,
        "galactic_holidays": True,
        "regional_time": True,
        "precision": "day"
    },
    
    # Configuration options for this calendar
    "config_options": {
        "era_system": {
            "type": "select",
            "default": "grs",
            "options": ["grs", "bby_aby", "btc_atc"],
            "description": {
                "en": "Era system to use (GrS, BBY/ABY, or BTC/ATC)",
                "de": "Zu verwendendes Ära-System (GrS, BBY/ABY oder BTC/ATC)"
            }
        },
        "show_week": {
            "type": "boolean",
            "default": True,
            "description": {
                "en": "Show week number and type",
                "de": "Wochennummer und -typ anzeigen"
            }
        },
        "show_festivals": {
            "type": "boolean",
            "default": True,
            "description": {
                "en": "Show festival weeks and holidays",
                "de": "Festwochen und Feiertage anzeigen"
            }
        },
        "planet_time": {
            "type": "select",
            "default": "Coruscant",
            "options": ["Coruscant", "Tatooine", "Naboo", "Mandalore", "Endor", "Hoth"],
            "description": {
                "en": "Planet for local time reference",
                "de": "Planet für lokale Zeitreferenz"
            }
        }
    }
}


class StarWarsCalendarSensor(AlternativeTimeSensorBase):
    """Sensor for displaying Star Wars Galactic Standard Calendar."""
    
    # Class-level update interval
    UPDATE_INTERVAL = 3600  # Update every hour
    
    def __init__(self, base_name: str, hass: HomeAssistant) -> None:
        """Initialize the Star Wars calendar sensor."""
        super().__init__(base_name, hass)
        
        # Get translated name from metadata
        calendar_name = self._translate('name', 'Star Wars Galactic Calendar')
        
        # Set sensor attributes
        self._attr_name = f"{base_name} {calendar_name}"
        self._attr_unique_id = f"{base_name}_star_wars"
        self._attr_icon = CALENDAR_INFO.get("icon", "mdi:death-star-variant")
        
        # Configuration options
        self._era_system = "grs"
        self._show_week = True
        self._show_festivals = True
        self._planet_time = "Coruscant"
        
        # Star Wars data
        self._star_wars_data = CALENDAR_INFO["star_wars_data"]
        
        _LOGGER.debug(f"Initialized Star Wars Calendar sensor: {self._attr_name}")
    
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
        
        # Add Star Wars-specific attributes
        if hasattr(self, '_star_wars_date'):
            attrs.update(self._star_wars_date)
            
            # Add description in user's language
            attrs["description"] = self._translate('description')
            
            # Add reference
            attrs["reference"] = CALENDAR_INFO.get('reference_url', '')
            
            # Add current era info
            attrs["era_system"] = self._era_system
            attrs["planet_reference"] = self._planet_time
        
        return attrs
    
    def _calculate_star_wars_date(self, earth_date: datetime) -> Dict[str, Any]:
        """Calculate Star Wars Galactic Standard date from Earth date."""
        
        # Map Earth year to Star Wars year
        # Using 2024 as Year 35 After Great ReSynchronization (GrS)
        # This places us in the New Republic era
        base_earth_year = 2024
        base_sw_year = 35  # 35 ABY is around The Force Awakens timeline
        
        sw_year = base_sw_year + (earth_date.year - base_earth_year)
        
        # Calculate day of year (Earth)
        day_of_year = earth_date.timetuple().tm_yday
        
        # Map to Star Wars calendar (368 days)
        # Scale Earth's day of year to Star Wars day of year
        earth_days_in_year = 366 if self._is_leap_year(earth_date.year) else 365
        sw_day_of_year = int((day_of_year / earth_days_in_year) * 368)
        if sw_day_of_year == 0:
            sw_day_of_year = 1
        
        # Determine month and day
        sw_month = 1
        days_counted = 0
        sw_day_in_month = sw_day_of_year
        
        for month_data in self._star_wars_data["months"]:
            month_days = month_data["days"]
            if month_data["festival"]:
                month_days += 5  # Festival weeks add 5 days
            
            if days_counted + month_days >= sw_day_of_year:
                sw_month = month_data["num"]
                sw_day_in_month = sw_day_of_year - days_counted
                break
            days_counted += month_days
        
        # Calculate week and weekday
        week_num = ((sw_day_in_month - 1) // 5) + 1
        weekday_index = (sw_day_in_month - 1) % 5
        
        # Check if we're in a festival week
        month_info = self._star_wars_data["months"][sw_month - 1]
        is_festival = False
        festival_name = ""
        
        if month_info["festival"] and week_num == 1:
            is_festival = True
            festival_name = month_info["festival"]
            week_type = "Festival Week"
        else:
            week_type = self._star_wars_data["week_types"][min(week_num - 1, 6)]
        
        weekday = self._star_wars_data["weekdays"][weekday_index]
        
        # Check for holidays
        holiday = ""
        for hol in self._star_wars_data["holidays"]:
            if hol["date"] == (sw_month, sw_day_in_month):
                holiday = hol["name"]
                break
        
        # Format era
        era_data = self._star_wars_data["eras"][self._era_system]
        if self._era_system == "grs":
            era_str = f"{sw_year} {era_data['abbr']}"
        elif self._era_system == "bby_aby":
            if sw_year < era_data["epoch_year"]:
                era_str = f"{abs(sw_year - era_data['epoch_year'])} {era_data['abbr_before']}"
            else:
                era_str = f"{sw_year - era_data['epoch_year']} {era_data['abbr_after']}"
        else:  # btc_atc
            if sw_year < era_data["epoch_year"]:
                era_str = f"{abs(sw_year - era_data['epoch_year'])} {era_data['abbr_before']}"
            else:
                era_str = f"{sw_year - era_data['epoch_year']} {era_data['abbr_after']}"
        
        # Get time period
        hour = earth_date.hour
        time_period = None
        for period in self._star_wars_data["time_periods"]:
            start, end = period["hours"]
            if start <= hour < end:
                time_period = period
                break
        
        # Get planet info
        planet_info = self._star_wars_data["major_planets"].get(self._planet_time, {})
        region = planet_info.get("region", "Unknown Regions")
        
        # Build date string
        date_str = f"{sw_year}:{sw_month}:{sw_day_in_month:02d} {era_data['abbr']}"
        
        # Build full display
        display_parts = [date_str]
        if self._show_week:
            display_parts.append(f"{weekday['name']} | {week_type}")
        
        if is_festival and self._show_festivals:
            display_parts.append(f"🎉 {festival_name}")
        
        if holiday and self._show_festivals:
            display_parts.append(f"🎊 {holiday}")
        
        if time_period:
            display_parts.append(f"{time_period['emoji']} {time_period['name']}")
        
        full_display = " | ".join(display_parts)
        
        result = {
            "year": sw_year,
            "month": sw_month,
            "day": sw_day_in_month,
            "era": era_str,
            "era_name": era_data["name"],
            "weekday": weekday["name"],
            "weekday_abbr": weekday["abbr"],
            "is_workday": weekday["work"],
            "week_number": week_num,
            "week_type": week_type,
            "is_festival": is_festival,
            "festival_name": festival_name if is_festival else "",
            "holiday": holiday,
            "time_period": time_period["name"] if time_period else "",
            "planet": self._planet_time,
            "region": region,
            "standard_time": earth_date.strftime("%H:%M:%S"),
            "gregorian_date": earth_date.strftime("%Y-%m-%d"),
            "full_display": full_display
        }
        
        # Add Force-related flavor text based on day
        force_messages = [
            "May the Force be with you",
            "The Force is strong today",
            "Trust in the Force",
            "Feel the Force flow through you",
            "The dark side clouds everything",
            "Do or do not, there is no try",
            "The Force will guide you"
        ]
        result["force_message"] = force_messages[sw_day_in_month % len(force_messages)]
        
        return result
    
    def _is_leap_year(self, year: int) -> bool:
        """Check if Earth year is a leap year."""
        return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
    
    def update(self) -> None:
        """Update the sensor."""
        now = datetime.now()
        self._star_wars_date = self._calculate_star_wars_date(now)
        
        # Set state to formatted date
        self._state = self._star_wars_date["full_display"]
        
        _LOGGER.debug(f"Updated Star Wars Calendar to {self._state}")