"""Mars Time Calendar implementation - Version 2.5."""
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

# Update interval in seconds (60 seconds for Mars time)
UPDATE_INTERVAL = 60

# Complete calendar information for auto-discovery
CALENDAR_INFO = {
    "id": "mars_time",
    "version": "2.5.0",
    "icon": "mdi:rocket-launch",
    "category": "space",
    "accuracy": "scientific",
    "update_interval": UPDATE_INTERVAL,
    
    # Multi-language names
    "name": {
        "en": "Mars Sol Time",
        "de": "Mars Sol-Zeit",
        "es": "Tiempo Solar de Marte",
        "fr": "Temps Solaire Martien",
        "it": "Tempo Solare Marziano",
        "nl": "Mars Sol Tijd",
        "pt": "Tempo Solar de Marte",
        "ru": "Марсианское солнечное время",
        "ja": "火星太陽時",
        "zh": "火星太阳时",
        "ko": "화성 태양시"
    },
    
    # Short descriptions for UI
    "description": {
        "en": "Martian solar time with timezone support (e.g. 14:23:45 MTC)",
        "de": "Marsianische Sonnenzeit mit Zeitzonenunterstützung (z.B. 14:23:45 MTC)",
        "es": "Tiempo solar marciano con soporte de zona horaria (ej. 14:23:45 MTC)",
        "fr": "Temps solaire martien avec support de fuseau horaire (ex. 14:23:45 MTC)",
        "it": "Tempo solare marziano con supporto fuso orario (es. 14:23:45 MTC)",
        "nl": "Martiaanse zonnetijd met tijdzone ondersteuning (bijv. 14:23:45 MTC)",
        "pt": "Tempo solar marciano com suporte de fuso horário (ex. 14:23:45 MTC)",
        "ru": "Марсианское солнечное время с поддержкой часовых поясов (напр. 14:23:45 MTC)",
        "ja": "タイムゾーン対応の火星太陽時（例：14:23:45 MTC）",
        "zh": "支持时区的火星太阳时（例：14:23:45 MTC）",
        "ko": "시간대를 지원하는 화성 태양시 (예: 14:23:45 MTC)"
    },
    
    # Detailed information for documentation
    "detailed_info": {
        "en": {
            "overview": "Mars Sol Time tracks time on Mars using sols (Martian days)",
            "sol_length": "One sol = 24 hours, 39 minutes, 35.244 seconds (88775.244 Earth seconds)",
            "msd": "Mars Sol Date (MSD) - continuous count since December 29, 1873",
            "timezones": "15 Mars time zones based on 15-degree longitude increments",
            "mtc": "Coordinated Mars Time (MTC) - Mars equivalent of UTC, based at Airy-0 crater",
            "missions": "Each Mars mission uses local solar time at their landing site",
            "year": "Mars year = 668.6 sols (approximately 687 Earth days)",
            "seasons": "Mars has seasons due to 25.2° axial tilt, but they're nearly twice as long as Earth's"
        },
        "de": {
            "overview": "Mars Sol-Zeit verfolgt die Zeit auf dem Mars mit Sols (Marstagen)",
            "sol_length": "Ein Sol = 24 Stunden, 39 Minuten, 35,244 Sekunden (88775,244 Erdsekunden)",
            "msd": "Mars Sol Date (MSD) - kontinuierliche Zählung seit 29. Dezember 1873",
            "timezones": "15 Mars-Zeitzonen basierend auf 15-Grad-Längengrad-Schritten",
            "mtc": "Coordinated Mars Time (MTC) - Mars-Äquivalent zu UTC, basiert am Airy-0 Krater",
            "missions": "Jede Mars-Mission verwendet lokale Sonnenzeit an ihrem Landeplatz",
            "year": "Marsjahr = 668,6 Sols (ungefähr 687 Erdtage)",
            "seasons": "Mars hat Jahreszeiten durch 25,2° Achsenneigung, aber sie sind fast doppelt so lang wie auf der Erde"
        }
    },
    
    # Mars-specific data
    "mars_data": {
        "sol_seconds": 88775.244,  # Mars sol in Earth seconds
        "earth_day_seconds": 86400.0,
        "tropical_year_sols": 668.6,  # Mars solar days per Mars year
        "tropical_year_days": 686.9725,  # Earth days per Mars year
        "msd_epoch_jd": 2405522.0,  # MSD epoch in Julian Date
        "axial_tilt": 25.19,  # degrees
        
        # Mars timezones (offset from MTC in Mars hours)
        "timezones": {
            "MTC": {"offset": 0, "name": "Coordinated Mars Time", "longitude": 0},
            "AMT": {"offset": 0, "name": "Airy Mean Time", "longitude": 0},
            "OLY": {"offset": -9, "name": "Olympus Mons Time", "longitude": -135},
            "ELY": {"offset": 4, "name": "Elysium Time", "longitude": 60},
            "CHA": {"offset": 12, "name": "Chryse Time", "longitude": 180},
            "MAR": {"offset": -6, "name": "Mariner Valley Time", "longitude": -90},
            "ARA": {"offset": 3, "name": "Arabia Terra Time", "longitude": 45},
            "THR": {"offset": -3, "name": "Tharsis Time", "longitude": -45},
            "HEL": {"offset": 7, "name": "Hellas Basin Time", "longitude": 105},
            "VIK": {"offset": -2, "name": "Viking 1 Landing Site", "longitude": -30},
            "PTH": {"offset": 2, "name": "Pathfinder Landing Site", "longitude": 30},
            "OPP": {"offset": 11, "name": "Opportunity Landing Site", "longitude": 165},
            "SPI": {"offset": 10, "name": "Spirit Landing Site", "longitude": 150},
            "CUR": {"offset": 9, "name": "Curiosity/Gale Crater", "longitude": 135},
            "PER": {"offset": 5, "name": "Perseverance/Jezero", "longitude": 75}
        },
        
        # Mission landing dates (MSD)
        "missions": {
            "Viking 1": 34816,
            "Viking 2": 34878,
            "Pathfinder": 49270,
            "Spirit": 50903,
            "Opportunity": 50924,
            "Phoenix": 51738,
            "Curiosity": 51505,
            "InSight": 52224,
            "Perseverance": 52304.5
        },
        
        # Mars months (for Darian calendar reference)
        "seasons": [
            {"name": "Northern Spring", "ls_start": 0, "ls_end": 90},
            {"name": "Northern Summer", "ls_start": 90, "ls_end": 180},
            {"name": "Northern Autumn", "ls_start": 180, "ls_end": 270},
            {"name": "Northern Winter", "ls_start": 270, "ls_end": 360}
        ]
    },
    
    # Additional metadata
    "reference_url": "https://en.wikipedia.org/wiki/Timekeeping_on_Mars",
    "documentation_url": "https://www.giss.nasa.gov/tools/mars24/",
    "origin": "NASA/JPL Mars missions",
    "created_by": "Various space agencies",
    
    # Example format
    "example": "14:23:45 MTC (Sol 52984)",
    "example_meaning": "14 hours, 23 minutes, 45 seconds Coordinated Mars Time, Sol 52984",
    
    # Related calendars
    "related": ["darian", "julian", "unix"],
    
    # Tags for searching and filtering
    "tags": [
        "space", "mars", "planetary", "sol", "nasa", "jpl",
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
        "show_mission_sol": {
            "type": "boolean",
            "default": True,
            "description": {
                "en": "Show mission sol for selected timezone",
                "de": "Zeige Missions-Sol für ausgewählte Zeitzone"
            }
        },
        "show_solar_longitude": {
            "type": "boolean",
            "default": True,
            "description": {
                "en": "Show solar longitude (Ls)",
                "de": "Zeige Sonnenlänge (Ls)"
            }
        },
        "show_earth_time": {
            "type": "boolean",
            "default": False,
            "description": {
                "en": "Also show Earth UTC time",
                "de": "Auch Erd-UTC-Zeit anzeigen"
            }
        }
    }
}


class MarsTimeSensor(AlternativeTimeSensorBase):
    """Sensor for displaying Mars time with timezone support."""
    
    # Class-level update interval
    UPDATE_INTERVAL = 60  # Update every minute
    
    def __init__(self, base_name: str, mars_timezone: str, hass: HomeAssistant) -> None:
        """Initialize the Mars time sensor."""
        super().__init__(base_name, hass)
        
        # Get translated name from metadata
        calendar_name = self._translate('name', 'Mars Sol Time')
        
        # Set sensor attributes
        self._attr_name = f"{base_name} {calendar_name}"
        self._attr_unique_id = f"{base_name}_mars_time"
        self._attr_icon = CALENDAR_INFO.get("icon", "mdi:rocket-launch")
        
        # Mars timezone
        self._mars_timezone = mars_timezone
        
        # Configuration options
        self._show_mission_sol = True
        self._show_solar_longitude = True
        self._show_earth_time = False
        
        # Mars data
        self._mars_data = CALENDAR_INFO["mars_data"]
        
        _LOGGER.debug(f"Initialized Mars Time sensor: {self._attr_name} with timezone {mars_timezone}")
    
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
        
        # Calculate Julian Date
        a = (14 - earth_utc.month) // 12
        y = earth_utc.year + 4800 - a
        m = earth_utc.month + 12 * a - 3
        
        jdn = earth_utc.day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
        jd = jdn + (earth_utc.hour - 12) / 24.0 + earth_utc.minute / 1440.0 + earth_utc.second / 86400.0
        
        # Calculate Mars Sol Date (MSD)
        msd = (jd - self._mars_data["msd_epoch_jd"]) / (self._mars_data["sol_seconds"] / self._mars_data["earth_day_seconds"])
        
        # Calculate Coordinated Mars Time (MTC)
        mtc_hours = (msd % 1) * 24
        mtc_hour = int(mtc_hours)
        mtc_minutes = (mtc_hours - mtc_hour) * 60
        mtc_minute = int(mtc_minutes)
        mtc_second = int((mtc_minutes - mtc_minute) * 60)
        
        mtc_time = f"{mtc_hour:02d}:{mtc_minute:02d}:{mtc_second:02d}"
        
        # Get timezone offset
        timezone_info = self._mars_data["timezones"].get(self._mars_timezone, {"offset": 0})
        timezone_offset = timezone_info["offset"]
        
        # Calculate local Mars time
        local_hours = mtc_hours + timezone_offset
        
        # Handle day boundary crossing
        if local_hours >= 24:
            local_hours -= 24
        elif local_hours < 0:
            local_hours += 24
            
        local_hour = int(local_hours)
        local_minutes = (local_hours - local_hour) * 60
        local_minute = int(local_minutes)
        local_second = int((local_minutes - local_minute) * 60)
        
        local_time = f"{local_hour:02d}:{local_minute:02d}:{local_second:02d}"
        
        # Calculate solar longitude (Ls) - approximate
        mars_year_fraction = (msd / self._mars_data["tropical_year_sols"]) % 1
        ls = mars_year_fraction * 360
        
        # Determine season
        season = "Unknown"
        for season_data in self._mars_data["seasons"]:
            if season_data["ls_start"] <= ls < season_data["ls_end"]:
                season = season_data["name"]
                break
        
        # Calculate subsolar longitude
        subsolar_longitude = (msd * 360) % 360 - 180
        
        # Equation of time (approximate)
        eot_minutes = 50 * math.sin(math.radians(2 * ls)) - 3 * math.sin(math.radians(4 * ls))
        
        # Calculate sunrise/sunset (equatorial approximation)
        sunrise_hour = 6 - eot_minutes / 60
        sunset_hour = 18 - eot_minutes / 60
        
        sunrise_time = f"{int(sunrise_hour):02d}:{int((sunrise_hour % 1) * 60):02d}"
        sunset_time = f"{int(sunset_hour):02d}:{int((sunset_hour % 1) * 60):02d}"
        
        # Calculate mission sol if applicable
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