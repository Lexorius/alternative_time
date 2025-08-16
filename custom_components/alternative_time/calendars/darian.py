"""Darian Calendar (Mars) implementation - Version 2.5."""
from __future__ import annotations

from datetime import datetime
import logging
import math
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
    "id": "darian",
    "version": "2.5.0",
    "icon": "mdi:earth",
    "category": "space",
    "accuracy": "scientific",
    "update_interval": UPDATE_INTERVAL,
    
    # Multi-language names
    "name": {
        "en": "Darian Calendar (Mars)",
        "de": "Darischer Kalender (Mars)",
        "es": "Calendario Dariano (Marte)",
        "fr": "Calendrier Darien (Mars)",
        "it": "Calendario Dariano (Marte)",
        "nl": "Dariaanse Kalender (Mars)",
        "pt": "Calendário Dariano (Marte)",
        "ru": "Дарианский календарь (Марс)",
        "ja": "ダリアン暦（火星）",
        "zh": "达里安历（火星）",
        "ko": "다리안 달력 (화성)"
    },
    
    # Short descriptions for UI
    "description": {
        "en": "Mars calendar with 24 months and 668 sols per year (e.g. 15 Gemini 217)",
        "de": "Mars-Kalender mit 24 Monaten und 668 Sols pro Jahr (z.B. 15 Gemini 217)",
        "es": "Calendario marciano con 24 meses y 668 soles por año (ej. 15 Gemini 217)",
        "fr": "Calendrier martien avec 24 mois et 668 sols par an (ex. 15 Gemini 217)",
        "it": "Calendario marziano con 24 mesi e 668 sol per anno (es. 15 Gemini 217)",
        "nl": "Mars kalender met 24 maanden en 668 sols per jaar (bijv. 15 Gemini 217)",
        "pt": "Calendário marciano com 24 meses e 668 sóis por ano (ex. 15 Gemini 217)",
        "ru": "Марсианский календарь с 24 месяцами и 668 солами в году (напр. 15 Gemini 217)",
        "ja": "24ヶ月、年間668ソルの火星暦（例：15 Gemini 217）",
        "zh": "24个月，每年668火星日的火星历（例：15 Gemini 217）",
        "ko": "24개월, 연간 668솔의 화성 달력 (예: 15 Gemini 217)"
    },
    
    # Detailed information for documentation
    "detailed_info": {
        "en": {
            "overview": "The Darian calendar is a proposed calendar for Mars created by Thomas Gangale",
            "structure": "24 months alternating between 27 and 28 sols (Mars days)",
            "year_length": "668 or 669 sols per Mars year (approximately 687 Earth days)",
            "months": "Months named after zodiac constellations in Latin and Sanskrit",
            "weeks": "7-sol weeks with names derived from Latin: Sol Solis, Sol Lunae, etc.",
            "epoch": "Mars Year 0 begins at the vernal equinox of April 28, 1608 (telescopic epoch)",
            "usage": "Proposed standard for Mars colonization and scientific missions",
            "leap_years": "Complex leap year pattern to maintain seasonal alignment"
        },
        "de": {
            "overview": "Der Darische Kalender ist ein vorgeschlagener Kalender für Mars, erstellt von Thomas Gangale",
            "structure": "24 Monate abwechselnd zwischen 27 und 28 Sols (Marstage)",
            "year_length": "668 oder 669 Sols pro Marsjahr (ungefähr 687 Erdtage)",
            "months": "Monate benannt nach Tierkreissternbildern in Latein und Sanskrit",
            "weeks": "7-Sol-Wochen mit Namen abgeleitet vom Lateinischen: Sol Solis, Sol Lunae, usw.",
            "epoch": "Marsjahr 0 beginnt beim Frühlingsäquinoktium am 28. April 1608 (teleskopische Epoche)",
            "usage": "Vorgeschlagener Standard für Mars-Kolonisation und wissenschaftliche Missionen",
            "leap_years": "Komplexes Schaltjahresmuster zur Aufrechterhaltung der saisonalen Ausrichtung"
        }
    },
    
    # Darian-specific data
    "darian_data": {
        # Constants
        "mars_tropical_year": 686.9725,  # Earth days
        "mars_sol_seconds": 88775.244,  # seconds
        "earth_day_seconds": 86400.0,
        "sols_per_year": 668,  # standard year
        "sols_per_leap_year": 669,
        
        # Darian months (24 months)
        "months": [
            {"name": "Sagittarius", "sols": 28, "type": "zodiac", "season": "Spring (North)"},
            {"name": "Dhanus", "sols": 28, "type": "sanskrit", "season": "Spring (North)"},
            {"name": "Capricornus", "sols": 28, "type": "zodiac", "season": "Spring (North)"},
            {"name": "Makara", "sols": 28, "type": "sanskrit", "season": "Spring (North)"},
            {"name": "Aquarius", "sols": 28, "type": "zodiac", "season": "Spring (North)"},
            {"name": "Kumbha", "sols": 28, "type": "sanskrit", "season": "Spring (North)"},
            {"name": "Pisces", "sols": 28, "type": "zodiac", "season": "Summer (North)"},
            {"name": "Mina", "sols": 28, "type": "sanskrit", "season": "Summer (North)"},
            {"name": "Aries", "sols": 28, "type": "zodiac", "season": "Summer (North)"},
            {"name": "Mesha", "sols": 28, "type": "sanskrit", "season": "Summer (North)"},
            {"name": "Taurus", "sols": 28, "type": "zodiac", "season": "Summer (North)"},
            {"name": "Rishabha", "sols": 28, "type": "sanskrit", "season": "Summer (North)"},
            {"name": "Gemini", "sols": 28, "type": "zodiac", "season": "Autumn (North)"},
            {"name": "Mithuna", "sols": 28, "type": "sanskrit", "season": "Autumn (North)"},
            {"name": "Cancer", "sols": 27, "type": "zodiac", "season": "Autumn (North)"},
            {"name": "Karka", "sols": 27, "type": "sanskrit", "season": "Autumn (North)"},
            {"name": "Leo", "sols": 27, "type": "zodiac", "season": "Autumn (North)"},
            {"name": "Simha", "sols": 27, "type": "sanskrit", "season": "Autumn (North)"},
            {"name": "Virgo", "sols": 27, "type": "zodiac", "season": "Winter (North)"},
            {"name": "Kanya", "sols": 27, "type": "sanskrit", "season": "Winter (North)"},
            {"name": "Libra", "sols": 27, "type": "zodiac", "season": "Winter (North)"},
            {"name": "Tula", "sols": 27, "type": "sanskrit", "season": "Winter (North)"},
            {"name": "Scorpius", "sols": 27, "type": "zodiac", "season": "Winter (North)"},
            {"name": "Vrishika", "sols": 27, "type": "sanskrit", "season": "Winter (North)"}
        ],
        
        # Week sol names (7-sol week)
        "week_sols": [
            {"name": "Sol Solis", "meaning": "Sun's day"},
            {"name": "Sol Lunae", "meaning": "Moon's day"},
            {"name": "Sol Martis", "meaning": "Mars' day"},
            {"name": "Sol Mercurii", "meaning": "Mercury's day"},
            {"name": "Sol Jovis", "meaning": "Jupiter's day"},
            {"name": "Sol Veneris", "meaning": "Venus' day"},
            {"name": "Sol Saturni", "meaning": "Saturn's day"}
        ],
        
        # Seasons
        "seasons": [
            {"name": "Northern Spring / Southern Autumn", "months": [0, 5]},
            {"name": "Northern Summer / Southern Winter", "months": [6, 11]},
            {"name": "Northern Autumn / Southern Spring", "months": [12, 17]},
            {"name": "Northern Winter / Southern Summer", "months": [18, 23]}
        ],
        
        # Epoch data
        "epoch": {
            "earth_date": "1608-04-28",
            "description": "Telescopic epoch - vernal equinox",
            "mars_year_0": 0
        },
        
        # MSD epoch for calculations
        "msd_epoch_jd": 2405522.0,  # December 29, 1873
        "j2000_jd": 2451545.0  # January 1, 2000, 12:00 UTC
    },
    
    # Additional metadata
    "reference_url": "https://en.wikipedia.org/wiki/Darian_calendar",
    "documentation_url": "http://ops-alaska.com/time/gangale_mst/darian.htm",
    "origin": "Thomas Gangale, 1985",
    "created_by": "Thomas Gangale",
    
    # Example format
    "example": "217 Gemini 15 (Sol Martis)",
    "example_meaning": "Mars year 217, month Gemini, sol 15, Sol Martis (Mars' day)",
    
    # Related calendars
    "related": ["mars_time", "gregorian", "julian"],
    
    # Tags for searching and filtering
    "tags": [
        "space", "mars", "darian", "planetary", "colonization",
        "scientific", "gangale", "sol", "future", "proposed"
    ],
    
    # Special features
    "features": {
        "mars_specific": True,
        "scientific_basis": True,
        "week_system": True,
        "dual_naming": True,  # Latin and Sanskrit
        "seasonal_calendar": True,
        "precision": "sol"
    },
    
    # Configuration options for this calendar
    "config_options": {
        "month_names": {
            "type": "select",
            "default": "zodiac",
            "options": ["zodiac", "sanskrit", "both"],
            "description": {
                "en": "Month name style (Zodiac/Sanskrit)",
                "de": "Monatsnamen-Stil (Tierkreis/Sanskrit)"
            }
        },
        "show_week_sol": {
            "type": "boolean",
            "default": True,
            "description": {
                "en": "Show week sol name",
                "de": "Wochensol-Name anzeigen"
            }
        },
        "show_msd": {
            "type": "boolean",
            "default": True,
            "description": {
                "en": "Show Mars Sol Date",
                "de": "Mars Sol-Datum anzeigen"
            }
        },
        "show_ls": {
            "type": "boolean",
            "default": True,
            "description": {
                "en": "Show solar longitude (Ls)",
                "de": "Sonnenlänge (Ls) anzeigen"
            }
        }
    }
}


class DarianCalendarSensor(AlternativeTimeSensorBase):
    """Sensor for displaying Darian Mars Calendar."""
    
    # Class-level update interval
    UPDATE_INTERVAL = 3600  # Update every hour
    
    def __init__(self, base_name: str, hass: HomeAssistant) -> None:
        """Initialize the Darian calendar sensor."""
        super().__init__(base_name, hass)
        
        # Get translated name from metadata
        calendar_name = self._translate('name', 'Darian Calendar')
        
        # Set sensor attributes
        self._attr_name = f"{base_name} {calendar_name}"
        self._attr_unique_id = f"{base_name}_darian_calendar"
        self._attr_icon = CALENDAR_INFO.get("icon", "mdi:earth")
        
        # Configuration options
        self._month_names = "zodiac"  # or "sanskrit" or "both"
        self._show_week_sol = True
        self._show_msd = True
        self._show_ls = True
        
        # Darian data
        self._darian_data = CALENDAR_INFO["darian_data"]
        
        _LOGGER.debug(f"Initialized Darian Calendar sensor: {self._attr_name}")
    
    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes."""
        attrs = super().extra_state_attributes
        
        # Add Darian-specific attributes
        if hasattr(self, '_darian_date'):
            attrs.update(self._darian_date)
            
            # Add description in user's language
            attrs["description"] = self._translate('description')
            
            # Add reference
            attrs["reference"] = CALENDAR_INFO.get('reference_url', '')
            
            # Add epoch info
            attrs["epoch"] = self._darian_data["epoch"]["description"]
        
        return attrs
    
    def _calculate_darian_date(self, earth_date: datetime) -> Dict[str, Any]:
        """Calculate Darian calendar date from Earth date."""
        
        # Calculate days since J2000 epoch
        j2000_epoch = datetime(2000, 1, 1, 12, 0, 0)
        delta = earth_date - j2000_epoch
        days_since_j2000 = delta.total_seconds() / self._darian_data["earth_day_seconds"]
        
        # Calculate current Julian Date
        current_jd = self._darian_data["j2000_jd"] + days_since_j2000
        
        # Calculate Mars Sol Date (MSD)
        msd = (current_jd - self._darian_data["msd_epoch_jd"]) / (
            self._darian_data["mars_sol_seconds"] / self._darian_data["earth_day_seconds"]
        )
        total_sols = int(msd)
        
        # Calculate Darian date
        mars_years_elapsed = int(msd / self._darian_data["mars_tropical_year"])
        sols_in_current_year = int(msd % self._darian_data["mars_tropical_year"])
        
        # Determine month and sol
        sols_counted = 0
        current_month_index = 0
        current_sol = 0
        
        for i, month_data in enumerate(self._darian_data["months"]):
            if sols_counted + month_data["sols"] > sols_in_current_year:
                current_month_index = i
                current_sol = sols_in_current_year - sols_counted + 1
                break
            sols_counted += month_data["sols"]
        else:
            # Last month of year
            current_month_index = 23
            current_sol = sols_in_current_year - sols_counted + 1
        
        month_data = self._darian_data["months"][current_month_index]
        
        # Get month name based on configuration
        if self._month_names == "sanskrit" and month_data["type"] == "zodiac":
            # Use next month (Sanskrit version)
            month_name = self._darian_data["months"][current_month_index + 1]["name"] if current_month_index < 23 else month_data["name"]
        elif self._month_names == "both":
            sanskrit_index = current_month_index + 1 if month_data["type"] == "zodiac" and current_month_index < 23 else current_month_index - 1
            if 0 <= sanskrit_index < 24:
                sanskrit_name = self._darian_data["months"][sanskrit_index]["name"]
                month_name = f"{month_data['name']}/{sanskrit_name}"
            else:
                month_name = month_data["name"]
        else:
            month_name = month_data["name"]
        
        # Calculate week sol
        week_sol_index = total_sols % 7
        week_sol_data = self._darian_data["week_sols"][week_sol_index]
        
        # Determine season
        season = month_data["season"]
        
        # Calculate approximate Ls (solar longitude)
        ls = (sols_in_current_year / self._darian_data["mars_tropical_year"]) * 360
        
        # Format the date
        full_date = f"{mars_years_elapsed} {month_name} {current_sol}"
        if self._show_week_sol:
            full_date += f" ({week_sol_data['name']})"
        
        result = {
            "year": mars_years_elapsed,
            "month_number": current_month_index + 1,
            "month_name": month_name,
            "month_type": month_data["type"],
            "sol": current_sol,
            "sols_in_month": month_data["sols"],
            "week_sol": week_sol_index + 1,
            "week_sol_name": week_sol_data["name"],
            "week_sol_meaning": week_sol_data["meaning"],
            "season": season,
            "total_sols": total_sols,
            "sols_in_year": sols_in_current_year,
            "earth_date": earth_date.strftime("%Y-%m-%d"),
            "full_date": full_date
        }
        
        if self._show_msd:
            result["mars_sol_date"] = round(msd, 4)
        
        if self._show_ls:
            result["solar_longitude"] = round(ls, 1)
        
        return result
    
    def update(self) -> None:
        """Update the sensor."""
        now = datetime.now()
        self._darian_date = self._calculate_darian_date(now)
        
        # Set state to formatted Darian date
        self._state = self._darian_date["full_date"]
        
        _LOGGER.debug(f"Updated Darian Calendar to {self._state}")