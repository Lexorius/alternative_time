"""NATO Time formats implementation - Version 2.5."""
from __future__ import annotations

from datetime import datetime
import logging
from typing import Dict, Any

from homeassistant.core import HomeAssistant
from ..sensor import AlternativeTimeSensorBase

_LOGGER = logging.getLogger(__name__)

try:
    import pytz
    HAS_PYTZ = True
except ImportError:
    HAS_PYTZ = False
    _LOGGER.warning("pytz not installed, NATO timezone detection will be limited")

# ============================================
# CALENDAR METADATA
# ============================================

# Update interval in seconds (1 second for real-time display)
UPDATE_INTERVAL = 1

# Complete calendar information for auto-discovery
CALENDAR_INFO = {
    "id": "nato",
    "version": "2.5.0",
    "icon": "mdi:clock-time-eight",
    "category": "military",
    "accuracy": "official",
    "update_interval": UPDATE_INTERVAL,
    
    # Multi-language names
    "name": {
        "en": "NATO Time",
        "de": "NATO-Zeit",
        "es": "Hora OTAN",
        "fr": "Heure OTAN",
        "it": "Ora NATO",
        "nl": "NAVO Tijd",
        "pt": "Hora OTAN",
        "ru": "Время НАТО",
        "ja": "NATO時間",
        "zh": "北约时间",
        "ko": "NATO 시간"
    },
    
    # Short descriptions for UI
    "description": {
        "en": "Military date-time without zone: DDHHMM (e.g. 151430)",
        "de": "Militärische Datum-Zeit ohne Zone: DDHHMM (z.B. 151430)",
        "es": "Fecha-hora militar sin zona: DDHHMM (ej. 151430)",
        "fr": "Date-heure militaire sans zone : DDHHMM (ex. 151430)",
        "it": "Data-ora militare senza zona: DDHHMM (es. 151430)",
        "nl": "Militaire datum-tijd zonder zone: DDHHMM (bijv. 151430)",
        "pt": "Data-hora militar sem zona: DDHHMM (ex. 151430)",
        "ru": "Военное время-дата без зоны: DDHHMM (напр. 151430)",
        "ja": "ゾーンなし軍事日時：DDHHMM（例：151430）",
        "zh": "无时区军事日期时间：DDHHMM（例：151430）",
        "ko": "시간대 없는 군사 날짜-시간: DDHHMM (예: 151430)"
    },
    
    # Detailed information for documentation
    "detailed_info": {
        "en": {
            "overview": "NATO Date-Time Group (DTG) is the standard military time format",
            "basic": "Basic format: DDHHMM (day, hour, minute)",
            "zone": "With zone: DDHHMM[Z] MON YY (Z=Zulu/UTC)",
            "zones": "A-Z (except J) represent time zones from UTC+1 to UTC-12",
            "j_omitted": "J is omitted to avoid confusion with I",
            "usage": "Used by NATO forces and many military organizations worldwide",
            "precision": "Provides unambiguous time references across time zones",
            "communications": "Critical for coordinated military operations"
        },
        "de": {
            "overview": "NATO Date-Time Group (DTG) ist das militärische Standardzeitformat",
            "basic": "Basisformat: DDHHMM (Tag, Stunde, Minute)",
            "zone": "Mit Zone: DDHHMM[Z] MON YY (Z=Zulu/UTC)",
            "zones": "A-Z (außer J) repräsentieren Zeitzonen von UTC+1 bis UTC-12",
            "j_omitted": "J wird ausgelassen, um Verwechslung mit I zu vermeiden",
            "usage": "Verwendet von NATO-Streitkräften und vielen Militärorganisationen weltweit",
            "precision": "Bietet eindeutige Zeitreferenzen über Zeitzonen hinweg",
            "communications": "Kritisch für koordinierte militärische Operationen"
        }
    },
    
    # NATO-specific data
    "nato_data": {
        # NATO timezone letters
        "zones": {
            0: {"letter": "Z", "name": "Zulu", "offset": 0},
            1: {"letter": "A", "name": "Alpha", "offset": 1},
            2: {"letter": "B", "name": "Bravo", "offset": 2},
            3: {"letter": "C", "name": "Charlie", "offset": 3},
            4: {"letter": "D", "name": "Delta", "offset": 4},
            5: {"letter": "E", "name": "Echo", "offset": 5},
            6: {"letter": "F", "name": "Foxtrot", "offset": 6},
            7: {"letter": "G", "name": "Golf", "offset": 7},
            8: {"letter": "H", "name": "Hotel", "offset": 8},
            9: {"letter": "I", "name": "India", "offset": 9},
            10: {"letter": "K", "name": "Kilo", "offset": 10},
            11: {"letter": "L", "name": "Lima", "offset": 11},
            12: {"letter": "M", "name": "Mike", "offset": 12},
            -1: {"letter": "N", "name": "November", "offset": -1},
            -2: {"letter": "O", "name": "Oscar", "offset": -2},
            -3: {"letter": "P", "name": "Papa", "offset": -3},
            -4: {"letter": "Q", "name": "Quebec", "offset": -4},
            -5: {"letter": "R", "name": "Romeo", "offset": -5},
            -6: {"letter": "S", "name": "Sierra", "offset": -6},
            -7: {"letter": "T", "name": "Tango", "offset": -7},
            -8: {"letter": "U", "name": "Uniform", "offset": -8},
            -9: {"letter": "V", "name": "Victor", "offset": -9},
            -10: {"letter": "W", "name": "Whiskey", "offset": -10},
            -11: {"letter": "X", "name": "X-ray", "offset": -11},
            -12: {"letter": "Y", "name": "Yankee", "offset": -12}
        },
        
        # Variants
        "variants": {
            "basic": "NatoTimeSensor",
            "zone": "NatoTimeZoneSensor",
            "rescue": "NatoTimeRescueSensor"
        }
    },
    
    # Additional metadata
    "reference_url": "https://en.wikipedia.org/wiki/Date-time_group",
    "documentation_url": "https://www.nato.int",
    "origin": "NATO military standards",
    "created_by": "NATO",
    
    # Example format
    "example": "151430",
    "example_meaning": "15th day of month, 14:30 local time",
    
    # Related calendars
    "related": ["gregorian", "utc", "military"],
    
    # Tags for searching and filtering
    "tags": [
        "military", "nato", "dtg", "tactical", "operational",
        "zulu", "utc", "coordination", "defense"
    ],
    
    # Special features
    "features": {
        "timezone_letters": True,
        "unambiguous": True,
        "compact_format": True,
        "military_standard": True,
        "precision": "minute"
    },
    
    # Configuration options for this calendar
    "config_options": {}
}


class NatoTimeSensor(AlternativeTimeSensorBase):
    """Sensor for displaying NATO Time (basic format)."""
    
    # Class-level update interval
    UPDATE_INTERVAL = 1  # Update every second
    
    def __init__(self, base_name: str, hass: HomeAssistant) -> None:
        """Initialize the NATO time sensor."""
        super().__init__(base_name, hass)
        
        # Get translated name from metadata
        calendar_name = self._translate('name', 'NATO Time')
        
        # Set sensor attributes
        self._attr_name = f"{base_name} {calendar_name}"
        self._attr_unique_id = f"{base_name}_nato_time"
        self._attr_icon = CALENDAR_INFO.get("icon", "mdi:clock-time-eight")
        
        # NATO data
        self._nato_data = CALENDAR_INFO["nato_data"]
        
        _LOGGER.debug(f"Initialized NATO Time sensor: {self._attr_name}")
    
    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes."""
        attrs = super().extra_state_attributes
        
        # Add NATO-specific attributes
        if hasattr(self, '_nato_time'):
            attrs.update(self._nato_time)
            
            # Add description in user's language
            attrs["description"] = self._translate('description')
            
            # Add reference
            attrs["reference"] = CALENDAR_INFO.get('reference_url', '')
        
        return attrs
    
    def _calculate_nato_time(self, earth_time: datetime) -> Dict[str, Any]:
        """Calculate NATO Time from standard time."""
        
        # Basic format: DDHHMM
        formatted = earth_time.strftime("%d%H%M")
        
        result = {
            "day": earth_time.day,
            "hour": earth_time.hour,
            "minute": earth_time.minute,
            "formatted": formatted,
            "standard_time": earth_time.strftime("%Y-%m-%d %H:%M:%S"),
            "full_display": formatted
        }
        
        return result
    
    def update(self) -> None:
        """Update the sensor."""
        now = datetime.now()
        self._nato_time = self._calculate_nato_time(now)
        
        # Set state to formatted NATO time
        self._state = self._nato_time["formatted"]
        
        _LOGGER.debug(f"Updated NATO Time to {self._state}")


class NatoTimeZoneSensor(AlternativeTimeSensorBase):
    """Sensor for displaying NATO Time with Zone indicator (DTG)."""
    
    # Class-level update interval
    UPDATE_INTERVAL = 1  # Update every second
    
    def __init__(self, base_name: str, hass: HomeAssistant) -> None:
        """Initialize the NATO time zone sensor."""
        super().__init__(base_name, hass)
        
        # Get translated name from metadata
        calendar_name = "NATO Time with Zone"
        
        # Set sensor attributes
        self._attr_name = f"{base_name} {calendar_name}"
        self._attr_unique_id = f"{base_name}_nato_time_zone"
        self._attr_icon = "mdi:earth"
        
        # NATO data
        self._nato_data = CALENDAR_INFO["nato_data"]
        
        _LOGGER.debug(f"Initialized NATO Time Zone sensor: {self._attr_name}")
    
    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes."""
        attrs = super().extra_state_attributes
        
        # Add NATO-specific attributes
        if hasattr(self, '_nato_time'):
            attrs.update(self._nato_time)
            
            # Add description
            attrs["description"] = "Full military DTG: DDHHMM[Zone] MON YY"
            
            # Add reference
            attrs["reference"] = CALENDAR_INFO.get('reference_url', '')
        
        return attrs
    
    def _calculate_nato_time_zone(self, earth_time: datetime) -> Dict[str, Any]:
        """Calculate NATO Time with Zone from standard time."""
        
        # Determine NATO timezone letter
        zone_letter = 'Z'  # Default to Zulu time
        zone_name = 'Zulu'
        utc_offset = 0
        
        if HAS_PYTZ:
            try:
                # Try to get local timezone offset
                local_tz = pytz.timezone('Europe/Berlin')  # Default
                local_time = local_tz.localize(datetime.now())
                utc_offset = int(local_time.utcoffset().total_seconds() / 3600)
                if utc_offset in self._nato_data["zones"]:
                    zone_info = self._nato_data["zones"][utc_offset]
                    zone_letter = zone_info["letter"]
                    zone_name = zone_info["name"]
            except Exception:
                pass
        
        # Format: DDHHMM[Zone] MON YY
        formatted = earth_time.strftime(f"%d%H%M{zone_letter} %b %y").upper()
        
        result = {
            "day": earth_time.day,
            "hour": earth_time.hour,
            "minute": earth_time.minute,
            "zone_letter": zone_letter,
            "zone_name": zone_name,
            "utc_offset": utc_offset,
            "month": earth_time.strftime("%b").upper(),
            "year": earth_time.year % 100,
            "formatted": formatted,
            "standard_time": earth_time.strftime("%Y-%m-%d %H:%M:%S"),
            "full_display": formatted
        }
        
        return result
    
    def update(self) -> None:
        """Update the sensor."""
        now = datetime.now()
        self._nato_time = self._calculate_nato_time_zone(now)
        
        # Set state to formatted NATO time
        self._state = self._nato_time["formatted"]
        
        _LOGGER.debug(f"Updated NATO Time Zone to {self._state}")


class NatoTimeRescueSensor(AlternativeTimeSensorBase):
    """Sensor for displaying NATO Time in German rescue service format."""
    
    # Class-level update interval
    UPDATE_INTERVAL = 1  # Update every second
    
    def __init__(self, base_name: str, hass: HomeAssistant) -> None:
        """Initialize the NATO rescue time sensor."""
        super().__init__(base_name, hass)
        
        # Get translated name from metadata
        calendar_name = "NATO Rescue Service Time"
        
        # Set sensor attributes
        self._attr_name = f"{base_name} {calendar_name}"
        self._attr_unique_id = f"{base_name}_nato_rescue"
        self._attr_icon = "mdi:ambulance"
        
        # German month abbreviations
        self._german_months = {
            1: "JAN", 2: "FEB", 3: "MÄR", 4: "APR",
            5: "MAI", 6: "JUN", 7: "JUL", 8: "AUG",
            9: "SEP", 10: "OKT", 11: "NOV", 12: "DEZ"
        }
        
        _LOGGER.debug(f"Initialized NATO Rescue Time sensor: {self._attr_name}")
    
    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes."""
        attrs = super().extra_state_attributes
        
        # Add NATO-specific attributes
        if hasattr(self, '_nato_time'):
            attrs.update(self._nato_time)
            
            # Add description
            attrs["description"] = "German rescue service notation: DD HHMM MONAT YY"
            attrs["organizations"] = "Feuerwehr, Rettungsdienst, THW, Katastrophenschutz"
            
            # Add reference
            attrs["reference"] = "BOS (Behörden und Organisationen mit Sicherheitsaufgaben)"
        
        return attrs
    
    def _calculate_nato_rescue_time(self, earth_time: datetime) -> Dict[str, Any]:
        """Calculate NATO Rescue Service Time from standard time."""
        
        # Get German month abbreviation
        month = self._german_months[earth_time.month]
        
        # Format with space between day and time
        formatted = f"{earth_time.day:02d} {earth_time.hour:02d}{earth_time.minute:02d} {month} {earth_time.year % 100:02d}"
        
        result = {
            "day": earth_time.day,
            "hour": earth_time.hour,
            "minute": earth_time.minute,
            "month_german": month,
            "year": earth_time.year % 100,
            "formatted": formatted,
            "standard_time": earth_time.strftime("%Y-%m-%d %H:%M:%S"),
            "full_display": formatted
        }
        
        return result
    
    def update(self) -> None:
        """Update the sensor."""
        now = datetime.now()
        self._nato_time = self._calculate_nato_rescue_time(now)
        
        # Set state to formatted NATO rescue time
        self._state = self._nato_time["formatted"]
        
        _LOGGER.debug(f"Updated NATO Rescue Time to {self._state}")