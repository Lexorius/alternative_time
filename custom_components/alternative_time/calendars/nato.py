"""NATO Time formats implementation - Version 2.5."""
from __future__ import annotations

from datetime import datetime
import logging
from typing import Dict, Any

from homeassistant.core import HomeAssistant

# WICHTIG: Import der Basis-Klasse direkt aus sensor.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from ..sensor import AlternativeTimeSensorBase
except ImportError:
    # Fallback für direkten Import
    from sensor import AlternativeTimeSensorBase

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
        "en": "Military date-time format (DTG)",
        "de": "Militärisches Datum-Zeit-Format (DTG)",
        "es": "Formato militar de fecha-hora (DTG)",
        "fr": "Format militaire date-heure (DTG)",
        "it": "Formato militare data-ora (DTG)",
        "nl": "Militair datum-tijd formaat (DTG)",
        "pt": "Formato militar data-hora (DTG)",
        "ru": "Военный формат даты-времени (DTG)",
        "ja": "軍事日時フォーマット（DTG）",
        "zh": "军事日期时间格式（DTG）",
        "ko": "군사 날짜-시간 형식 (DTG)"
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
        
        # German month abbreviations for rescue service format
        "german_months": {
            1: "JAN", 2: "FEB", 3: "MÄR", 4: "APR",
            5: "MAI", 6: "JUN", 7: "JUL", 8: "AUG",
            9: "SEP", 10: "OKT", 11: "NOV", 12: "DEZ"
        }
    },
    
    # Configuration options for this calendar
    "config_options": {
        "format_type": {
            "type": "select",
            "default": "basic",
            "options": ["basic", "zone", "rescue"],
            "description": {
                "en": "NATO time format variant",
                "de": "NATO-Zeitformat-Variante"
            }
        },
        "show_zone_name": {
            "type": "boolean",
            "default": False,
            "description": {
                "en": "Show phonetic zone name (e.g., Zulu)",
                "de": "Phonetischen Zonennamen anzeigen (z.B. Zulu)"
            }
        },
        "use_local_zone": {
            "type": "boolean",
            "default": True,
            "description": {
                "en": "Use local timezone (otherwise UTC/Zulu)",
                "de": "Lokale Zeitzone verwenden (sonst UTC/Zulu)"
            }
        }
    }
}


class NatoTimeSensor(AlternativeTimeSensorBase):
    """Sensor for displaying NATO Time in various formats."""
    
    # Class-level update interval
    UPDATE_INTERVAL = 1  # Update every second
    
    def __init__(self, base_name: str, hass: HomeAssistant) -> None:
        """Initialize the NATO time sensor."""
        super().__init__(base_name, hass)
        
        # Store CALENDAR_INFO as instance variable for _translate method
        self._calendar_info = CALENDAR_INFO
        
        # Get translated name from metadata
        calendar_name = self._translate('name', 'NATO Time')
        
        # Set basic attributes first
        self._attr_name = f"{base_name} {calendar_name}"
        self._attr_unique_id = f"{base_name}_nato_time"
        self._attr_icon = CALENDAR_INFO.get("icon", "mdi:clock-time-eight")
        
        # Initialize configuration with defaults
        self._format_type = "basic"
        self._show_zone_name = False
        self._use_local_zone = True
        
        # NATO data
        self._nato_data = CALENDAR_INFO["nato_data"]
        
        # Flag to track if we need to update attributes after config is loaded
        self._needs_config_update = True
        
        _LOGGER.debug(f"NATO sensor initialized with defaults")
    
    async def async_added_to_hass(self) -> None:
        """When entity is added to hass, load config and set up updates."""
        # Load plugin options if available
        if self._needs_config_update:
            options = self.get_plugin_options()
            
            if options:
                _LOGGER.info(f"NATO: Loading plugin options: {options}")
                
                # Update configuration
                old_format = self._format_type
                self._format_type = options.get("format_type", "basic")
                self._show_zone_name = options.get("show_zone_name", False)
                self._use_local_zone = options.get("use_local_zone", True)
                
                # Update name and icon if format changed
                if old_format != self._format_type:
                    calendar_name = self._translate('name', 'NATO Time')
                    format_suffix = {
                        "basic": "",
                        "zone": " with Zone",
                        "rescue": " (Rescue Service)"
                    }.get(self._format_type, "")
                    
                    self._attr_name = f"{self._base_name} {calendar_name}{format_suffix}"
                    self._attr_unique_id = f"{self._base_name}_nato_time_{self._format_type}"
                    
                    icon_map = {
                        "basic": "mdi:clock-time-eight",
                        "zone": "mdi:earth",
                        "rescue": "mdi:ambulance"
                    }
                    self._attr_icon = icon_map.get(self._format_type, CALENDAR_INFO.get("icon", "mdi:clock-time-eight"))
                    
                    _LOGGER.info(f"NATO: Updated to format={self._format_type}, name={self._attr_name}")
                
                self._needs_config_update = False
            else:
                _LOGGER.debug(f"NATO: No plugin options found, using defaults")
        
        # Call parent implementation for scheduling updates
        await super().async_added_to_hass()
    
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
        
        # Add NATO-specific attributes
        if hasattr(self, '_nato_time'):
            attrs.update(self._nato_time)
            
            # Add description in user's language
            attrs["description"] = self._translate('description')
            
            # Add format-specific description
            if self._format_type == "basic":
                attrs["format_description"] = "Basic format: DDHHMM (day, hour, minute)"
            elif self._format_type == "zone":
                attrs["format_description"] = "Full DTG: DDHHMM[Zone] MON YY"
            elif self._format_type == "rescue":
                attrs["format_description"] = "German rescue service: DD HHMM MONAT YY"
            
            # Add reference
            attrs["reference"] = "https://en.wikipedia.org/wiki/Date-time_group"
            
            # Add current configuration
            attrs["format_type"] = self._format_type
            attrs["show_zone_name"] = self._show_zone_name
            attrs["use_local_zone"] = self._use_local_zone
        
        return attrs
    
    def _get_timezone_info(self, earth_time: datetime) -> tuple:
        """Get NATO timezone letter and name."""
        zone_letter = 'Z'  # Default to Zulu time
        zone_name = 'Zulu'
        utc_offset = 0
        
        if self._use_local_zone and HAS_PYTZ:
            try:
                # Try to get system timezone from Home Assistant
                if hasattr(self._hass.config, 'time_zone'):
                    tz_name = self._hass.config.time_zone
                    local_tz = pytz.timezone(tz_name)
                    local_time = local_tz.localize(earth_time.replace(tzinfo=None))
                    utc_offset = int(local_time.utcoffset().total_seconds() / 3600)
                    
                    if utc_offset in self._nato_data["zones"]:
                        zone_info = self._nato_data["zones"][utc_offset]
                        zone_letter = zone_info["letter"]
                        zone_name = zone_info["name"]
            except Exception as e:
                _LOGGER.debug(f"Could not determine local timezone: {e}")
        
        return zone_letter, zone_name, utc_offset
    
    def _calculate_nato_time(self, earth_time: datetime) -> Dict[str, Any]:
        """Calculate NATO Time based on selected format."""
        
        if self._format_type == "basic":
            return self._calculate_basic_format(earth_time)
        elif self._format_type == "zone":
            return self._calculate_zone_format(earth_time)
        elif self._format_type == "rescue":
            return self._calculate_rescue_format(earth_time)
        else:
            _LOGGER.warning(f"NATO: Unknown format type: {self._format_type}, using basic")
            return self._calculate_basic_format(earth_time)
    
    def _calculate_basic_format(self, earth_time: datetime) -> Dict[str, Any]:
        """Calculate basic NATO Time format (DDHHMM)."""
        
        # Basic format: DDHHMM
        formatted = earth_time.strftime("%d%H%M")
        
        # Get timezone info for attributes
        zone_letter, zone_name, utc_offset = self._get_timezone_info(earth_time)
        
        # Add zone name if configured
        display = formatted
        if self._show_zone_name:
            display = f"{formatted} ({zone_name})"
        
        result = {
            "day": earth_time.day,
            "hour": earth_time.hour,
            "minute": earth_time.minute,
            "second": earth_time.second,
            "zone_letter": zone_letter,
            "zone_name": zone_name,
            "utc_offset": utc_offset,
            "formatted": formatted,
            "standard_time": earth_time.strftime("%Y-%m-%d %H:%M:%S"),
            "full_display": display
        }
        
        return result
    
    def _calculate_zone_format(self, earth_time: datetime) -> Dict[str, Any]:
        """Calculate NATO Time with Zone format (DDHHMM[Zone] MON YY)."""
        
        # Get timezone info
        zone_letter, zone_name, utc_offset = self._get_timezone_info(earth_time)
        
        # Format: DDHHMM[Zone] MON YY
        formatted = earth_time.strftime(f"%d%H%M{zone_letter} %b %y").upper()
        
        # Add zone name if configured
        display = formatted
        if self._show_zone_name:
            display = f"{formatted} ({zone_name})"
        
        result = {
            "day": earth_time.day,
            "hour": earth_time.hour,
            "minute": earth_time.minute,
            "second": earth_time.second,
            "zone_letter": zone_letter,
            "zone_name": zone_name,
            "utc_offset": utc_offset,
            "month": earth_time.strftime("%b").upper(),
            "year": earth_time.year % 100,
            "formatted": formatted,
            "standard_time": earth_time.strftime("%Y-%m-%d %H:%M:%S"),
            "full_display": display
        }
        
        return result
    
    def _calculate_rescue_format(self, earth_time: datetime) -> Dict[str, Any]:
        """Calculate German rescue service format (DD HHMM MONAT YY)."""
        
        # Get German month abbreviation
        month = self._nato_data["german_months"][earth_time.month]
        
        # Format with space between day and time
        formatted = f"{earth_time.day:02d} {earth_time.hour:02d}{earth_time.minute:02d} {month} {earth_time.year % 100:02d}"
        
        # Get timezone info for attributes
        zone_letter, zone_name, utc_offset = self._get_timezone_info(earth_time)
        
        # Add zone name if configured
        display = formatted
        if self._show_zone_name:
            display = f"{formatted} ({zone_name})"
        
        result = {
            "day": earth_time.day,
            "hour": earth_time.hour,
            "minute": earth_time.minute,
            "second": earth_time.second,
            "zone_letter": zone_letter,
            "zone_name": zone_name,
            "utc_offset": utc_offset,
            "month_german": month,
            "year": earth_time.year % 100,
            "formatted": formatted,
            "organizations": "Feuerwehr, Rettungsdienst, THW, Katastrophenschutz",
            "standard_time": earth_time.strftime("%Y-%m-%d %H:%M:%S"),
            "full_display": display
        }
        
        return result
    
    def update(self) -> None:
        """Update the sensor."""
        now = datetime.now()
        self._nato_time = self._calculate_nato_time(now)
        
        # Set state to formatted NATO time
        self._state = self._nato_time["full_display"]
        
        _LOGGER.debug(f"NATO: Updated to {self._state} (format: {self._format_type})")