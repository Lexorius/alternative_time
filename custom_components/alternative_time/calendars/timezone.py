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
        "pt": "Exibir hora em diferentes fusos horários ao redor do mundo",
        "ru": "Отображение времени в разных часовых поясах мира",
        "ja": "世界中の異なるタイムゾーンの時刻を表示",
        "zh": "显示世界各地不同时区的时间",
        "ko": "전 세계 다양한 시간대의 시간 표시"
    },
    
    # Timezone data
    "timezone_data": {
        "regions": {
            "Americas": [
                "America/New_York",
                "America/Chicago",
                "America/Denver",
                "America/Los_Angeles",
                "America/Toronto",
                "America/Mexico_City",
                "America/Sao_Paulo",
                "America/Buenos_Aires"
            ],
            "Europe": [
                "Europe/London",
                "Europe/Paris",
                "Europe/Berlin",
                "Europe/Moscow",
                "Europe/Rome",
                "Europe/Madrid",
                "Europe/Amsterdam",
                "Europe/Stockholm",
                "Europe/Zurich"
            ],
            "Asia": [
                "Asia/Tokyo",
                "Asia/Shanghai",
                "Asia/Hong_Kong",
                "Asia/Singapore",
                "Asia/Dubai",
                "Asia/Kolkata",
                "Asia/Bangkok",
                "Asia/Seoul"
            ],
            "Pacific": [
                "Pacific/Auckland",
                "Pacific/Sydney",
                "Australia/Melbourne",
                "Australia/Perth",
                "Pacific/Honolulu",
                "Pacific/Fiji"
            ],
            "Africa": [
                "Africa/Cairo",
                "Africa/Johannesburg",
                "Africa/Lagos",
                "Africa/Nairobi"
            ]
        }
    },
    
    # Additional metadata
    "reference_url": "https://en.wikipedia.org/wiki/Time_zone",
    "documentation_url": "https://www.timeanddate.com/time/map/",
    "origin": "IANA Time Zone Database",
    "created_by": "International standards",
    
    # Example format
    "example": "14:30:00 CET (UTC+1)",
    "example_meaning": "2:30 PM Central European Time",
    
    # Related calendars
    "related": ["unix", "julian", "gregorian"],
    
    # Tags for searching and filtering
    "tags": [
        "timezone", "world", "clock", "time", "global",
        "utc", "gmt", "dst", "international", "travel"
    ],
    
    # Special features
    "features": {
        "supports_dst": True,
        "supports_abbreviations": True,
        "supports_offsets": True,
        "precision": "second",
        "real_time": True
    },
    
    # Configuration options
    "config_options": {
        "timezone": {
            "type": "select",
            "default": "UTC",
            "options": [],  # Will be populated from timezone_data
            "label": {
                "en": "Timezone",
                "de": "Zeitzone",
                "fr": "Fuseau horaire",
                "es": "Zona horaria"
            },
            "description": {
                "en": "Select timezone to display",
                "de": "Zeitzone zur Anzeige auswählen",
                "fr": "Sélectionner le fuseau horaire à afficher",
                "es": "Seleccionar zona horaria para mostrar"
            }
        },
        "show_offset": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show UTC offset",
                "de": "UTC-Versatz anzeigen",
                "fr": "Afficher le décalage UTC",
                "es": "Mostrar desplazamiento UTC"
            },
            "description": {
                "en": "Display UTC offset (e.g. UTC+1)",
                "de": "UTC-Versatz anzeigen (z.B. UTC+1)",
                "fr": "Afficher le décalage UTC (ex. UTC+1)",
                "es": "Mostrar desplazamiento UTC (ej. UTC+1)"
            }
        },
        "show_dst": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show DST indicator",
                "de": "Sommerzeit-Indikator",
                "fr": "Indicateur d'heure d'été",
                "es": "Indicador de horario de verano"
            },
            "description": {
                "en": "Show when daylight saving time is active",
                "de": "Anzeigen wenn Sommerzeit aktiv ist",
                "fr": "Afficher quand l'heure d'été est active",
                "es": "Mostrar cuando el horario de verano está activo"
            }
        },
        "format_24h": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "24-hour format",
                "de": "24-Stunden-Format",
                "fr": "Format 24 heures",
                "es": "Formato 24 horas"
            },
            "description": {
                "en": "Use 24-hour time format",
                "de": "24-Stunden-Zeitformat verwenden",
                "fr": "Utiliser le format 24 heures",
                "es": "Usar formato de 24 horas"
            }
        },
        "show_date": {
            "type": "boolean",
            "default": False,
            "label": {
                "en": "Show date",
                "de": "Datum anzeigen",
                "fr": "Afficher la date",
                "es": "Mostrar fecha"
            },
            "description": {
                "en": "Include date in display",
                "de": "Datum in Anzeige einbeziehen",
                "fr": "Inclure la date dans l'affichage",
                "es": "Incluir fecha en la pantalla"
            }
        }
    }
}


class TimezoneSensor(AlternativeTimeSensorBase):
    """Sensor for displaying time in different timezones."""
    
    # Class-level update interval
    UPDATE_INTERVAL = 1  # Update every second
    
    def __init__(self, base_name: str, timezone: str, hass: HomeAssistant) -> None:
        """Initialize the timezone sensor."""
        super().__init__(base_name, hass)
        
        # Store CALENDAR_INFO as instance variable
        self._calendar_info = CALENDAR_INFO
        
        self._timezone_str = timezone
        
        # WICHTIG: Timezone wird NICHT im __init__ geladen (blocking call)
        # Wird stattdessen lazy beim ersten Update oder in async_added_to_hass geladen
        self._timezone = None
        self._timezone_initialized = False
        
        # Get translated name from metadata
        calendar_name = self._translate('name', 'World Timezones')
        
        # Set sensor attributes
        self._attr_name = f"{base_name} {calendar_name} ({timezone})"
        self._attr_unique_id = f"{base_name}_timezone_{timezone.replace('/', '_')}"
        self._attr_icon = CALENDAR_INFO.get("icon", "mdi:clock-time-four-outline")
        
        # Get plugin options
        options = self.get_plugin_options()
        
        # Configuration options with defaults
        self._show_offset = options.get("show_offset", True)
        self._show_dst = options.get("show_dst", True)
        self._format_24h = options.get("format_24h", True)
        self._show_date = options.get("show_date", False)
        
        # Timezone data
        self._timezone_data = CALENDAR_INFO["timezone_data"]
        
        # Initialize state
        self._state = None
        self._tz_info = {}
        
        _LOGGER.debug(f"Initialized Timezone sensor: {self._attr_name}")
    
    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        await super().async_added_to_hass()
        
        # Initialisiere Timezone async
        if HAS_PYTZ and not self._timezone_initialized:
            try:
                # Führe die blockierende Operation in einem Executor aus
                self._timezone = await self._hass.async_add_executor_job(
                    pytz.timezone, self._timezone_str
                )
                self._timezone_initialized = True
                _LOGGER.debug(f"Loaded timezone {self._timezone_str}")
            except Exception as e:
                _LOGGER.warning(f"Could not load timezone {self._timezone_str}: {e}")
                self._timezone = None
                self._timezone_initialized = True  # Prevent retry
    
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
            minutes = int(offset[3:]) if len(offset) > 3 else 0
            offset_display = f"UTC{hours:+d}:{minutes:02d}" if minutes else f"UTC{hours:+d}"
        else:
            offset_display = "UTC"
        
        # Check DST status
        is_dst = False
        if HAS_PYTZ and self._timezone and self._timezone_initialized:
            try:
                is_dst = bool(now_tz.dst())
            except:
                is_dst = False
        
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
        if HAS_PYTZ and self._timezone and self._timezone_initialized:
            now_tz = datetime.now(self._timezone)
            self._tz_info = self._calculate_timezone_info(now_tz)
            self._state = self._tz_info["full_display"]
        else:
            # Fallback without pytz or before timezone is loaded
            now = datetime.now()
            self._state = now.strftime("%H:%M:%S") + f" {self._timezone_str}"
            self._tz_info = {
                "time": now.strftime("%H:%M:%S"),
                "timezone_id": self._timezone_str,
                "error": "pytz not available or timezone not loaded"
            }
        
        _LOGGER.debug(f"Updated Timezone to {self._state}")