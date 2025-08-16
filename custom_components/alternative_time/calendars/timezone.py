"""Timezone sensor implementation - Version 2.5."""
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
    _LOGGER.warning("pytz not installed, timezone support will be limited")

# ============================================
# CALENDAR METADATA
# ============================================

# Update interval in seconds (1 second for real-time display)
UPDATE_INTERVAL = 1

# Complete calendar information for auto-discovery
CALENDAR_INFO = {
    "id": "timezone",
    "version": "2.5.0",
    "icon": "mdi:clock-time-four-outline",
    "category": "technical",
    "accuracy": "precise",
    "update_interval": UPDATE_INTERVAL,
    
    # Multi-language names
    "name": {
        "en": "World Timezones",
        "de": "Weltzeitzonen",
        "es": "Zonas Horarias Mundiales",
        "fr": "Fuseaux Horaires Mondiaux",
        "it": "Fusi Orari Mondiali",
        "nl": "Wereldtijdzones",
        "pt": "Fusos Horários Mundiais",
        "ru": "Мировые часовые пояса",
        "ja": "世界のタイムゾーン",
        "zh": "世界时区",
        "ko": "세계 시간대"
    },
    
    # Short descriptions for UI
    "description": {
        "en": "Display time in different timezones around the world",
        "de": "Zeit in verschiedenen Zeitzonen weltweit anzeigen",
        "es": "Mostrar la hora en diferentes zonas horarias del mundo",
        "fr": "Afficher l'heure dans différents fuseaux horaires du monde",
        "it": "Mostra l'ora in diversi fusi orari del mondo",
        "nl": "Tijd weergeven in verschillende tijdzones wereldwijd",
        "pt": "Exibir hora em diferentes fusos horários do mundo",
        "ru": "Отображение времени в разных часовых поясах мира",
        "ja": "世界各地のタイムゾーンの時刻を表示",
        "zh": "显示世界各地不同时区的时间",
        "ko": "전 세계 다양한 시간대의 시간 표시"
    },
    
    # Detailed information for documentation
    "detailed_info": {
        "en": {
            "overview": "A timezone sensor that displays current time in any timezone worldwide",
            "structure": "Based on the IANA Time Zone Database (tzdata)",
            "zones": "Supports over 500 timezone identifiers",
            "dst": "Automatic Daylight Saving Time handling",
            "format": "24-hour format with timezone abbreviation",
            "accuracy": "Synchronized with system time",
            "history": "Timezone database maintained since 1986",
            "updates": "Regular updates for political timezone changes"
        },
        "de": {
            "overview": "Ein Zeitzonensensor, der die aktuelle Zeit in jeder Zeitzone weltweit anzeigt",
            "structure": "Basierend auf der IANA Time Zone Database (tzdata)",
            "zones": "Unterstützt über 500 Zeitzonenbezeichner",
            "dst": "Automatische Sommerzeitumstellung",
            "format": "24-Stunden-Format mit Zeitzonenabkürzung",
            "accuracy": "Synchronisiert mit Systemzeit",
            "history": "Zeitzonendatenbank seit 1986 gepflegt",
            "updates": "Regelmäßige Updates für politische Zeitzonenänderungen"
        }
    },
    
    # Timezone-specific data
    "timezone_data": {
        # Major timezone groups
        "regions": {
            "africa": ["Africa/Cairo", "Africa/Lagos", "Africa/Johannesburg", "Africa/Nairobi"],
            "america": ["America/New_York", "America/Chicago", "America/Los_Angeles", "America/Mexico_City", "America/Sao_Paulo"],
            "asia": ["Asia/Tokyo", "Asia/Shanghai", "Asia/Kolkata", "Asia/Dubai", "Asia/Singapore"],
            "europe": ["Europe/London", "Europe/Paris", "Europe/Berlin", "Europe/Moscow", "Europe/Madrid"],
            "pacific": ["Pacific/Sydney", "Pacific/Auckland", "Pacific/Honolulu", "Pacific/Fiji"]
        },
        
        # UTC offsets (standard time)
        "utc_offsets": {
            "UTC-12": ["Pacific/Kwajalein"],
            "UTC-11": ["Pacific/Samoa"],
            "UTC-10": ["Pacific/Honolulu"],
            "UTC-9": ["America/Anchorage"],
            "UTC-8": ["America/Los_Angeles"],
            "UTC-7": ["America/Denver"],
            "UTC-6": ["America/Chicago"],
            "UTC-5": ["America/New_York"],
            "UTC-4": ["America/Halifax"],
            "UTC-3": ["America/Sao_Paulo"],
            "UTC-2": ["Atlantic/South_Georgia"],
            "UTC-1": ["Atlantic/Azores"],
            "UTC+0": ["Europe/London", "Africa/Casablanca"],
            "UTC+1": ["Europe/Paris", "Europe/Berlin"],
            "UTC+2": ["Europe/Athens", "Africa/Cairo"],
            "UTC+3": ["Europe/Moscow", "Asia/Baghdad"],
            "UTC+4": ["Asia/Dubai", "Asia/Baku"],
            "UTC+5": ["Asia/Karachi", "Asia/Tashkent"],
            "UTC+5:30": ["Asia/Kolkata", "Asia/Colombo"],
            "UTC+6": ["Asia/Dhaka", "Asia/Almaty"],
            "UTC+7": ["Asia/Bangkok", "Asia/Jakarta"],
            "UTC+8": ["Asia/Shanghai", "Asia/Singapore"],
            "UTC+9": ["Asia/Tokyo", "Asia/Seoul"],
            "UTC+10": ["Australia/Sydney", "Asia/Vladivostok"],
            "UTC+11": ["Pacific/Noumea"],
            "UTC+12": ["Pacific/Auckland", "Pacific/Fiji"]
        },
        
        # Daylight saving time information
        "dst_info": {
            "northern_hemisphere": {
                "start": "March (2nd Sunday)",
                "end": "November (1st Sunday)",
                "regions": ["USA", "Canada", "Europe"]
            },
            "southern_hemisphere": {
                "start": "October (1st Sunday)",
                "end": "April (1st Sunday)",
                "regions": ["Australia", "New Zealand", "Brazil"]
            },
            "no_dst": ["Japan", "China", "India", "Russia (since 2014)"]
        },
        
        # Special timezones
        "special_zones": {
            "UTC": "Coordinated Universal Time",
            "GMT": "Greenwich Mean Time",
            "EST": "Eastern Standard Time",
            "PST": "Pacific Standard Time",
            "IST": "India Standard Time",
            "JST": "Japan Standard Time",
            "AEST": "Australian Eastern Standard Time"
        },
        
        # Time formats by region
        "regional_formats": {
            "12hour": ["USA", "Canada", "Australia", "Philippines"],
            "24hour": ["Europe", "Asia", "Africa", "South America"]
        }
    },
    
    # Additional metadata
    "reference_url": "https://www.iana.org/time-zones",
    "documentation_url": "https://en.wikipedia.org/wiki/List_of_tz_database_time_zones",
    "origin": "IANA (Internet Assigned Numbers Authority)",
    "created_by": "Arthur David Olson",
    "database": "tzdata",
    
    # Example format
    "example": "14:30:45 CET",
    "example_meaning": "14 hours, 30 minutes, 45 seconds Central European Time",
    
    # Related calendars
    "related": ["gregorian", "utc", "unix"],
    
    # Tags for searching and filtering
    "tags": [
        "timezone", "world", "time", "dst", "utc", "gmt",
        "international", "travel", "global", "iana", "tzdata"
    ],
    
    # Special features
    "features": {
        "real_time": True,
        "dst_aware": True,
        "political_updates": True,
        "historical_data": True,
        "precision": "second"
    },
    
    # Configuration options for this calendar
    "config_options": {
        "timezone": {
            "type": "select",
            "default": "UTC",
            "description": {
                "en": "Select timezone to display",
                "de": "Anzuzeigende Zeitzone auswählen"
            }
        },
        "show_offset": {
            "type": "boolean",
            "default": True,
            "description": {
                "en": "Show UTC offset",
                "de": "UTC-Versatz anzeigen"
            }
        },
        "show_dst": {
            "type": "boolean",
            "default": True,
            "description": {
                "en": "Show DST indicator",
                "de": "Sommerzeit-Indikator anzeigen"
            }
        },
        "format_24h": {
            "type": "boolean",
            "default": True,
            "description": {
                "en": "Use 24-hour format",
                "de": "24-Stunden-Format verwenden"
            }
        },
        "show_date": {
            "type": "boolean",
            "default": False,
            "description": {
                "en": "Show date along with time",
                "de": "Datum zusammen mit Zeit anzeigen"
            }
        }
    }
}


class TimezoneSensor(AlternativeTimeSensorBase):
    """Sensor for displaying time in a specific timezone."""
    
    # Class-level update interval
    UPDATE_INTERVAL = 1  # Update every second
    
    def __init__(self, base_name: str, timezone: str, hass: HomeAssistant) -> None:
        """Initialize the timezone sensor."""
        super().__init__(base_name, hass)
        
        self._timezone_str = timezone
        self._timezone = None
        
        # Get translated name from metadata
        calendar_name = self._translate('name', 'World Timezones')
        
        # Set sensor attributes
        self._attr_name = f"{base_name} {calendar_name} ({timezone})"
        self._attr_unique_id = f"{base_name}_timezone_{timezone.replace('/', '_')}"
        self._attr_icon = CALENDAR_INFO.get("icon", "mdi:clock-time-four-outline")
        
        # Configuration options
        self._show_offset = True
        self._show_dst = True
        self._format_24h = True
        self._show_date = False
        
        # Timezone data
        self._timezone_data = CALENDAR_INFO["timezone_data"]
        
        _LOGGER.debug(f"Initialized Timezone sensor: {self._attr_name}")
        
        # Initialize timezone
        if HAS_PYTZ:
            try:
                self._timezone = pytz.timezone(self._timezone_str)
            except Exception as e:
                _LOGGER.warning(f"Could not load timezone {self._timezone_str}: {e}")
                self._timezone = None
    
    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes."""
        attrs = super().extra_state_attributes
        
        # Add timezone-specific attributes
        if hasattr(self, '_tz_info'):
            attrs.update(self._tz_info)
            
            # Add description in user's language
            attrs["description"] = self._translate('description')
            
            # Add reference
            attrs["reference"] = CALENDAR_INFO.get('reference_url', '')
            
            # Add timezone database info
            attrs["timezone_id"] = self._timezone_str
            attrs["database"] = "IANA tzdata"
        
        return attrs
    
    def _calculate_timezone_info(self, now_tz: datetime) -> Dict[str, Any]:
        """Calculate timezone information."""
        
        # Format time based on configuration
        if self._format_24h:
            time_format = "%H:%M:%S"
            time_display = now_tz.strftime(time_format)
        else:
            time_format = "%I:%M:%S %p"
            time_display = now_tz.strftime(time_format).lstrip('0')
        
        # Get timezone abbreviation
        tz_abbr = now_tz.strftime("%Z")
        
        # Calculate UTC offset
        offset = now_tz.strftime("%z")
        if offset:
            hours = int(offset[:3])
            minutes = int(offset[3:])
            offset_display = f"UTC{hours:+d}:{minutes:02d}" if minutes else f"UTC{hours:+d}"
        else:
            offset_display = "UTC"
        
        # Check DST status
        is_dst = False
        if HAS_PYTZ and self._timezone:
            is_dst = bool(now_tz.dst())
        
        # Build display string
        display_parts = [time_display, tz_abbr]
        
        if self._show_offset:
            display_parts.append(f"({offset_display})")
        
        if self._show_dst and is_dst:
            display_parts.append("DST")
        
        if self._show_date:
            date_str = now_tz.strftime("%Y-%m-%d")
            display_parts.insert(0, date_str)
        
        full_display = " ".join(display_parts)
        
        # Get day info
        weekday = now_tz.strftime("%A")
        date = now_tz.strftime("%Y-%m-%d")
        
        # Determine time period
        hour = now_tz.hour
        if 5 <= hour < 12:
            period = "Morning"
        elif 12 <= hour < 17:
            period = "Afternoon"
        elif 17 <= hour < 21:
            period = "Evening"
        else:
            period = "Night"
        
        result = {
            "time": time_display,
            "timezone_abbr": tz_abbr,
            "utc_offset": offset_display,
            "is_dst": is_dst,
            "date": date,
            "weekday": weekday,
            "period": period,
            "hour_24": now_tz.hour,
            "minute": now_tz.minute,
            "second": now_tz.second,
            "full_display": full_display,
            "iso_format": now_tz.isoformat()
        }
        
        return result
    
    def update(self) -> None:
        """Update the sensor."""
        if HAS_PYTZ and self._timezone:
            now_tz = datetime.now(self._timezone)
            self._tz_info = self._calculate_timezone_info(now_tz)
            self._state = self._tz_info["full_display"]
        else:
            # Fallback without pytz
            now = datetime.now()
            self._state = now.strftime("%H:%M:%S") + f" {self._timezone_str}"
            self._tz_info = {
                "time": now.strftime("%H:%M:%S"),
                "timezone_id": self._timezone_str,
                "error": "pytz not available"
            }
        
        _LOGGER.debug(f"Updated Timezone to {self._state}")