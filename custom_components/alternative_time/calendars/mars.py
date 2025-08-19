"""Mars Time (Darian Calendar) implementation - Version 2.5."""
from __future__ import annotations

from datetime import datetime
import math
import logging
from typing import Dict, Any

from homeassistant.core import HomeAssistant
from ..sensor import AlternativeTimeSensorBase

_LOGGER = logging.getLogger(__name__)

# ============================================
# CALENDAR METADATA
# ============================================

# Update interval in seconds (60 seconds = 1 minute)
UPDATE_INTERVAL = 60

# Complete calendar information for auto-discovery
CALENDAR_INFO = {
    "id": "mars",
    "version": "2.5.0",
    "icon": "mdi:rocket-launch",
    "category": "space",
    "accuracy": "scientific",
    "update_interval": UPDATE_INTERVAL,
    
    # Multi-language names
    "name": {
        "en": "Mars Sol Time",
        "de": "Mars Sol-Zeit",
        "es": "Tiempo Sol de Marte",
        "fr": "Temps Sol de Mars",
        "it": "Tempo Sol di Marte",
        "nl": "Mars Sol Tijd",
        "pt": "Tempo Sol de Marte",
        "ru": "Марсианское солнечное время",
        "ja": "火星ソル時間",
        "zh": "火星太阳时",
        "ko": "화성 솔 시간"
    },
    
    # Short descriptions for UI
    "description": {
        "en": "Mars Sol Date (MSD) and local solar time on Mars",
        "de": "Mars Sol-Datum (MSD) und lokale Sonnenzeit auf dem Mars",
        "es": "Fecha Sol de Marte (MSD) y hora solar local en Marte",
        "fr": "Date Sol de Mars (MSD) et heure solaire locale sur Mars",
        "it": "Data Sol di Marte (MSD) e ora solare locale su Marte",
        "nl": "Mars Sol Datum (MSD) en lokale zonnetijd op Mars",
        "pt": "Data Sol de Marte (MSD) e hora solar local em Marte",
        "ru": "Марсианская солнечная дата (MSD) и местное солнечное время на Марсе",
        "ja": "火星ソル日付（MSD）と火星の地方太陽時",
        "zh": "火星太阳日（MSD）和火星当地太阳时",
        "ko": "화성 솔 날짜(MSD)와 화성 현지 태양시"
    },
    
    # Mars-specific data
    "mars_data": {
        # Physical constants
        "sol_duration_seconds": 88775.244147,  # Mars solar day in Earth seconds
        "tropical_year_sols": 668.5991,  # Mars year in sols
        "j2000_epoch": 946727935.816,  # J2000 epoch in Unix timestamp
        "mars_epoch_msd": 44796.0,  # MSD at J2000 epoch
        
        # Mars timezones (based on landing sites and features)
        "timezones": {
            "MTC": {"name": "Mars Coordinated Time", "longitude": 0},
            "AMT": {"name": "Amazonis Time", "longitude": -158},
            "OLY": {"name": "Olympus Time", "longitude": -134},
            "ELY": {"name": "Elysium Time", "longitude": 135},
            "CHA": {"name": "Chryse Time", "longitude": -33},
            "MAR": {"name": "Marineris Time", "longitude": -59},
            "ARA": {"name": "Arabia Time", "longitude": 20},
            "THR": {"name": "Tharsis Time", "longitude": -125},
            "HEL": {"name": "Hellas Time", "longitude": 70},
            # Mission landing sites
            "VIK": {"name": "Viking Lander Time", "longitude": -48},
            "PTH": {"name": "Pathfinder Time", "longitude": -33.55},
            "OPP": {"name": "Opportunity Time", "longitude": -5.53},
            "SPI": {"name": "Spirit Time", "longitude": 175.47},
            "CUR": {"name": "Curiosity Time", "longitude": 137.44},
            "PER": {"name": "Perseverance Time", "longitude": 77.45}
        },
        
        # Mission landing dates (in MSD)
        "missions": {
            "Viking 1": 34809,
            "Viking 2": 34895,
            "Pathfinder": 46236,
            "Spirit": 49269,
            "Opportunity": 49290,
            "Curiosity": 49269,
            "Perseverance": 52304
        }
    },
    
    # Additional metadata
    "reference_url": "https://en.wikipedia.org/wiki/Timekeeping_on_Mars",
    "documentation_url": "https://www.giss.nasa.gov/tools/mars24/",
    "origin": "NASA/JPL",
    "created_by": "Various Mars missions",
    
    # Example format
    "example": "Sol 52304, 14:26:35 MTC",
    "example_meaning": "Mars Sol Date 52304, Mars Coordinated Time",
    
    # Related calendars
    "related": ["julian", "gregorian", "unix"],
    
    # Tags for searching and filtering
    "tags": [
        "mars", "space", "planetary", "sol", "msd", "nasa", "jpl",
        "scientific", "astronomical", "mission", "exploration",
        "rover", "perseverance", "curiosity", "mtc"
    ],
    
    # Special features
    "features": {
        "supports_timezones": True,
        "supports_missions": True,
        "supports_seasons": True,
        "continuous_count": True,
        "precision": "second",
        "solar_longitude": True
    },
    
    # Configuration options for this calendar
    "config_options": {
        "timezone": {
            "type": "select",
            "default": "MTC",
            "options": [
                "MTC", "AMT", "OLY", "ELY", "CHA", "MAR", "ARA", "THR",
                "HEL", "VIK", "PTH", "OPP", "SPI", "CUR", "PER"
            ],
            "label": {
                "en": "Mars timezone",
                "de": "Mars-Zeitzone",
                "fr": "Fuseau horaire martien",
                "es": "Zona horaria marciana"
            },
            "description": {
                "en": "Select Mars timezone",
                "de": "Mars-Zeitzone auswählen",
                "fr": "Sélectionner le fuseau horaire martien",
                "es": "Seleccionar zona horaria marciana"
            }
        },
        "show_mission_sol": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show mission sol",
                "de": "Missions-Sol anzeigen",
                "fr": "Afficher sol de mission",
                "es": "Mostrar sol de misión"
            },
            "description": {
                "en": "Show mission sol for selected timezone",
                "de": "Zeige Missions-Sol für ausgewählte Zeitzone",
                "fr": "Afficher le sol de mission pour le fuseau horaire sélectionné",
                "es": "Mostrar sol de misión para la zona horaria seleccionada"
            }
        },
        "show_solar_longitude": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show solar longitude",
                "de": "Sonnenlänge anzeigen",
                "fr": "Afficher longitude solaire",
                "es": "Mostrar longitud solar"
            },
            "description": {
                "en": "Show solar longitude (Ls)",
                "de": "Zeige Sonnenlänge (Ls)",
                "fr": "Afficher la longitude solaire (Ls)",
                "es": "Mostrar longitud solar (Ls)"
            }
        },
        "show_earth_time": {
            "type": "boolean",
            "default": False,
            "label": {
                "en": "Show Earth time",
                "de": "Erdzeit anzeigen",
                "fr": "Afficher heure terrestre",
                "es": "Mostrar hora terrestre"
            },
            "description": {
                "en": "Also show Earth UTC time",
                "de": "Auch Erd-UTC-Zeit anzeigen",
                "fr": "Afficher aussi l'heure UTC terrestre",
                "es": "Mostrar también hora UTC terrestre"
            }
        }
    }
}


class MarsTimeSensor(AlternativeTimeSensorBase):
    """Sensor for displaying Mars time with timezone support."""
    
    # Class-level update interval
    UPDATE_INTERVAL = 60  # Update every minute
    
    def __init__(self, base_name: str, hass: HomeAssistant) -> None:
        """Initialize the Mars time sensor."""
        super().__init__(base_name, hass)
        
        # Store CALENDAR_INFO as instance variable
        self._calendar_info = CALENDAR_INFO
        
        # Get translated name from metadata
        calendar_name = self._translate('name', 'Mars Sol Time')
        
        # Set sensor attributes
        self._attr_name = f"{base_name} {calendar_name}"
        self._attr_unique_id = f"{base_name}_mars_time"
        self._attr_icon = CALENDAR_INFO.get("icon", "mdi:rocket-launch")
        
        # Get plugin options
        options = self.get_plugin_options()
        
        # Mars timezone (from config or default)
        self._mars_timezone = options.get("timezone", "MTC")
        
        # Configuration options
        self._show_mission_sol = options.get("show_mission_sol", True)
        self._show_solar_longitude = options.get("show_solar_longitude", True)
        self._show_earth_time = options.get("show_earth_time", False)
        
        # Mars data
        self._mars_data = CALENDAR_INFO["mars_data"]
        
        # Initialize state
        self._state = None
        self._mars_time_info = {}
        
        _LOGGER.debug(f"Initialized Mars Time sensor: {self._attr_name} with timezone {self._mars_timezone}")
    
    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes."""
        attrs = super().extra_state_attributes
        
        # Add Mars-specific attributes
        if hasattr(self, '_mars_time_info'):
            attrs.update(self._mars_time_info)
            
            # Add description in user's language
            attrs["description"] = self._translate('description')
            
            # Add reference
            attrs["reference"] = CALENDAR_INFO.get('reference_url', '')
            
            # Add timezone info
            attrs["timezone"] = self._mars_timezone
            if self._mars_timezone in self._mars_data["timezones"]:
                tz_info = self._mars_data["timezones"][self._mars_timezone]
                attrs["timezone_name"] = tz_info["name"]
                attrs["timezone_longitude"] = tz_info["longitude"]
        
        return attrs
    
    def _calculate_mars_time(self, earth_utc: datetime) -> Dict[str, Any]:
        """Calculate Mars time from Earth UTC time."""
        # Convert to Unix timestamp
        unix_timestamp = earth_utc.timestamp()
        
        # Calculate Mars Sol Date (MSD)
        # MSD = (Unix timestamp - J2000 epoch) / seconds per sol + MSD at J2000
        elapsed_seconds = unix_timestamp - self._mars_data["j2000_epoch"]
        elapsed_sols = elapsed_seconds / self._mars_data["sol_duration_seconds"]
        msd = self._mars_data["mars_epoch_msd"] + elapsed_sols
        
        # Calculate Mars Coordinated Time (MTC) - Mean Solar Time at Prime Meridian
        sol_fraction = msd % 1
        mtc_hours = int(sol_fraction * 24)
        mtc_minutes = int((sol_fraction * 24 - mtc_hours) * 60)
        mtc_seconds = int(((sol_fraction * 24 - mtc_hours) * 60 - mtc_minutes) * 60)
        mtc_time = f"{mtc_hours:02d}:{mtc_minutes:02d}:{mtc_seconds:02d}"
        
        # Calculate solar longitude (Ls) - Mars season indicator
        # Simplified calculation - actual formula is much more complex
        mars_year_fraction = (msd / self._mars_data["tropical_year_sols"]) % 1
        ls = mars_year_fraction * 360  # Degrees
        
        # Determine season
        if 0 <= ls < 90:
            season = "Northern Spring / Southern Fall"
        elif 90 <= ls < 180:
            season = "Northern Summer / Southern Winter"
        elif 180 <= ls < 270:
            season = "Northern Fall / Southern Spring"
        else:
            season = "Northern Winter / Southern Summer"
        
        # Calculate local solar time for selected timezone
        timezone_data = self._mars_data["timezones"].get(self._mars_timezone, {"longitude": 0})
        timezone_offset = timezone_data["longitude"] / 15  # Convert longitude to hours
        
        # Equation of time correction (simplified)
        # Mars has a more eccentric orbit than Earth, causing larger variations
        eot_degrees = 2.861 * math.sin(2 * math.radians(ls)) - 0.071 * math.sin(4 * math.radians(ls))
        eot_minutes = eot_degrees * 4  # Convert degrees to minutes of time
        
        # Subsolar longitude
        subsolar_longitude = (sol_fraction * 360 + eot_degrees) % 360
        
        # Local Mean Solar Time
        lmst_hours = (mtc_hours + timezone_offset) % 24
        lmst_minutes = mtc_minutes
        lmst_seconds = mtc_seconds
        
        # Apply equation of time for Local True Solar Time
        total_minutes = lmst_hours * 60 + lmst_minutes + eot_minutes
        ltst_hours = int(total_minutes // 60) % 24
        ltst_minutes = int(total_minutes % 60)
        
        local_time = f"{ltst_hours:02d}:{ltst_minutes:02d}:{lmst_seconds:02d}"
        
        # Calculate sunrise/sunset (simplified - assumes equatorial location)
        sunrise_hour = 6 - int(eot_minutes / 60)
        sunset_hour = 18 - int(eot_minutes / 60)
        sunrise_time = f"{sunrise_hour:02d}:00"
        sunset_time = f"{sunset_hour:02d}:00"
        
        # Check if any mission landed at this timezone
        mission_sol = None
        mission_name = None
        for mission, landing_msd in self._mars_data["missions"].items():
            if self._mars_timezone in mission.upper() or (self._mars_timezone == "PER" and mission == "Perseverance"):
                mission_sol = int(msd - landing_msd)
                mission_name = mission
                break
        
        result = {
            "msd": round(msd, 4),
            "sol_number": int(msd),
            "mtc": mtc_time,
            "local_time": local_time,
            "timezone_offset": timezone_offset,
            "season": season,
            "sunrise": sunrise_time,
            "sunset": sunset_time,
            "full_display": f"{local_time} {self._mars_timezone}"
        }
        
        if self._show_solar_longitude:
            result["solar_longitude"] = round(ls, 1)
            result["subsolar_longitude"] = round(subsolar_longitude, 1)
            result["equation_of_time"] = round(eot_minutes, 1)
        
        if self._show_mission_sol and mission_sol is not None:
            result["mission_sol"] = mission_sol
            result["mission_name"] = mission_name
            result["full_display"] += f" (Sol {mission_sol})"
        
        if self._show_earth_time:
            result["earth_time_utc"] = earth_utc.strftime("%Y-%m-%d %H:%M:%S UTC")
        
        return result
    
    def update(self) -> None:
        """Update the sensor."""
        now = datetime.utcnow()
        self._mars_time_info = self._calculate_mars_time(now)
        
        # Set state to local Mars time with timezone
        self._state = f"{self._mars_time_info['local_time']} {self._mars_timezone}"
        
        _LOGGER.debug(f"Updated Mars Time to {self._state}")