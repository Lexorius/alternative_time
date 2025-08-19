"""Swatch Internet Time Calendar implementation - Version 2.5."""
from __future__ import annotations

from datetime import datetime, timedelta
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
    _LOGGER.warning("pytz not installed, using UTC+1 approximation for Biel Mean Time")

# ============================================
# CALENDAR METADATA
# ============================================

# Update interval in seconds (1 second for smooth beat transitions)
UPDATE_INTERVAL = 1

# Complete calendar information for auto-discovery
CALENDAR_INFO = {
    "id": "swatch",
    "version": "2.5.0",
    "icon": "mdi:web-clock",
    "category": "technical",
    "accuracy": "commercial",
    "update_interval": UPDATE_INTERVAL,
    
    # Multi-language names
    "name": {
        "en": "Swatch Internet Time",
        "de": "Swatch Internet-Zeit",
        "es": "Hora Internet Swatch",
        "fr": "Temps Internet Swatch",
        "it": "Ora Internet Swatch",
        "nl": "Swatch Internet Tijd",
        "pt": "Hora da Internet Swatch",
        "ru": "Интернет-время Swatch",
        "ja": "スウォッチ・インターネットタイム",
        "zh": "斯沃琪互联网时间",
        "ko": "스와치 인터넷 시간"
    },
    
    # Short descriptions for UI
    "description": {
        "en": "Internet Time in Beats @000-@999. One day = 1000 beats, no time zones (e.g. @500.00)",
        "de": "Internet-Zeit in Beats @000-@999. Ein Tag = 1000 Beats, keine Zeitzonen (z.B. @500.00)",
        "es": "Tiempo de Internet en Beats @000-@999. Un día = 1000 beats, sin zonas horarias (ej. @500.00)",
        "fr": "Temps Internet en Beats @000-@999. Un jour = 1000 beats, pas de fuseaux horaires (ex. @500.00)",
        "it": "Tempo Internet in Beat @000-@999. Un giorno = 1000 beat, nessun fuso orario (es. @500.00)",
        "nl": "Internet Tijd in Beats @000-@999. Eén dag = 1000 beats, geen tijdzones (bijv. @500.00)",
        "pt": "Tempo da Internet em Beats @000-@999. Um dia = 1000 beats, sem fusos horários (ex. @500.00)",
        "ru": "Интернет-время в битах @000-@999. Один день = 1000 битов, без часовых поясов (напр. @500.00)",
        "ja": "インターネットタイムをビート@000-@999で表示。1日=1000ビート、タイムゾーンなし（例：@500.00）",
        "zh": "互联网时间以节拍@000-@999表示。一天=1000节拍，无时区（例：@500.00）",
        "ko": "비트 @000-@999로 표시되는 인터넷 시간. 하루 = 1000비트, 시간대 없음 (예: @500.00)"
    },
    
    # Swatch-specific data
    "swatch_data": {
        "base_timezone": "Europe/Zurich",  # BMT (Biel Mean Time)
        "beats_per_day": 1000,
        "seconds_per_beat": 86.4,  # 86400 seconds / 1000 beats
        "reference_meridian": 7.5,  # Biel/Bienne longitude
        
        # Beat periods (unofficial but commonly used)
        "periods": {
            "@000-@124": "Night",
            "@125-@374": "Morning", 
            "@375-@624": "Afternoon",
            "@625-@874": "Evening",
            "@875-@999": "Late Night"
        },
        
        # Notable beat times
        "milestones": {
            "@000": "Midnight BMT",
            "@500": "Noon BMT",
            "@250": "6 AM BMT",
            "@750": "6 PM BMT"
        }
    },
    
    # Additional metadata
    "reference_url": "https://en.wikipedia.org/wiki/Swatch_Internet_Time",
    "documentation_url": "https://www.swatch.com/en-us/internet-time/",
    "origin": "Swatch Corporation",
    "created_by": "Nicholas Negroponte & Swatch",
    "introduced": "October 23, 1998",
    
    # Example format
    "example": "@500.00",
    "example_meaning": "Noon in Biel, Switzerland (approximately 13:45 CET)",
    
    # Related calendars
    "related": ["decimal", "unix", "hexadecimal"],
    
    # Tags for searching and filtering
    "tags": [
        "modern", "decimal", "internet", "swatch", "switzerland",
        "biel", "bmt", "no_timezone", "global_time", "beats",
        "1990s", "commercial", "experimental"
    ],
    
    # Special features
    "features": {
        "supports_timezones": False,  # By design - no timezones
        "supports_fractional": True,   # Supports decimal beats
        "supports_date": False,        # Time only, no date component
        "precision": "centibeat",      # Can show to 0.01 beat precision
        "global_sync": True,           # Same time everywhere
        "mathematical_base": 10        # Decimal system
    },
    
    # Configuration options for this calendar
    "config_options": {
        "show_fractional": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show fractional beats",
                "de": "Bruchteile anzeigen"
            },
            "description": {
                "en": "Show fractional beats (e.g. @500.25)",
                "de": "Zeige Bruchteile von Beats (z.B. @500.25)"
            }
        },
        "show_period": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show period",
                "de": "Periode anzeigen"
            },
            "description": {
                "en": "Show period of day (Morning, Afternoon, etc.)",
                "de": "Zeige Tagesperiode (Morgen, Nachmittag, usw.)"
            }
        },
        "precision": {
            "type": "select",
            "default": "centibeat",
            "options": ["beat", "decibeat", "centibeat"],
            "label": {
                "en": "Precision",
                "de": "Genauigkeit"
            },
            "description": {
                "en": "Precision level for beat display",
                "de": "Präzisionsstufe für Beat-Anzeige"
            }
        }
    }
}


class SwatchTimeSensor(AlternativeTimeSensorBase):
    """Sensor for displaying Swatch Internet Time."""
    
    # Class-level update interval
    UPDATE_INTERVAL = 1  # Update every second for smooth beats
    
    def __init__(self, base_name: str, hass: HomeAssistant) -> None:
        """Initialize the Swatch time sensor."""
        super().__init__(base_name, hass)
        
        # Store CALENDAR_INFO as instance variable for _translate method
        self._calendar_info = CALENDAR_INFO
        
        # Get translated name from metadata
        calendar_name = self._translate('name', 'Swatch Internet Time')
        
        # Set sensor attributes
        self._attr_name = f"{base_name} {calendar_name}"
        self._attr_unique_id = f"{base_name}_swatch"
        self._attr_icon = CALENDAR_INFO.get("icon", "mdi:web-clock")
        
        # Get plugin options
        options = self.get_plugin_options()
        
        # Configuration options with defaults
        self._show_fractional = options.get("show_fractional", True)
        self._show_period = options.get("show_period", True)
        self._precision = options.get("precision", "centibeat")
        
        # Swatch data
        self._swatch_data = CALENDAR_INFO["swatch_data"]
        
        # WICHTIG: Timezone wird NICHT im __init__ geladen (blocking call)
        # Wird stattdessen lazy beim ersten Update geladen
        self._bmt = None
        self._bmt_initialized = False
        
        # Initialize state
        self._state = None
        
        _LOGGER.debug(f"Initialized Swatch Internet Time sensor: {self._attr_name}")
    
    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        await super().async_added_to_hass()
        
        # Initialisiere Timezone async
        if HAS_PYTZ and not self._bmt_initialized:
            try:
                # Führe die blockierende Operation in einem Executor aus
                self._bmt = await self._hass.async_add_executor_job(
                    pytz.timezone, self._swatch_data["base_timezone"]
                )
                self._bmt_initialized = True
                _LOGGER.debug(f"Loaded timezone {self._swatch_data['base_timezone']}")
            except Exception as e:
                _LOGGER.warning(f"Could not load timezone {self._swatch_data['base_timezone']}: {e}")
                self._bmt = None
                self._bmt_initialized = True  # Prevent retry
    
    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes."""
        attrs = super().extra_state_attributes
        
        # Add Swatch-specific attributes
        if hasattr(self, '_swatch_time'):
            attrs.update(self._swatch_time)
            
            # Add description in user's language
            attrs["description"] = self._translate('description')
            
            # Add reference
            attrs["reference"] = CALENDAR_INFO.get('reference_url', '')
            
            # Add calculation info
            attrs["seconds_per_beat"] = self._swatch_data["seconds_per_beat"]
            attrs["beats_per_day"] = self._swatch_data["beats_per_day"]
        
        return attrs
    
    def _calculate_swatch_time(self, earth_time: datetime) -> Dict[str, Any]:
        """Calculate Swatch Internet Time from standard time."""
        # Get time in BMT (Biel Mean Time)
        if HAS_PYTZ and self._bmt and self._bmt_initialized:
            bmt_time = earth_time.astimezone(self._bmt)
        else:
            # Fallback: use UTC+1 as approximation
            from datetime import timezone
            bmt_time = earth_time.astimezone(timezone(timedelta(hours=1)))
        
        # Calculate seconds since midnight BMT
        midnight_bmt = bmt_time.replace(hour=0, minute=0, second=0, microsecond=0)
        seconds_since_midnight = (bmt_time - midnight_bmt).total_seconds()
        
        # Calculate beats (with high precision)
        beats_raw = seconds_since_midnight / self._swatch_data["seconds_per_beat"]
        beats = int(beats_raw)
        fractional_beat = beats_raw - beats
        
        # Calculate subdivisions
        centibeats = int(fractional_beat * 100)
        decibeats = int(fractional_beat * 10)
        
        # Determine period of day
        period_data = self._get_period(beats)
        
        # Check for milestones
        milestone = self._get_milestone(beats)
        
        # Format based on precision setting
        if self._precision == "beat":
            formatted = f"@{beats:03d}"
        elif self._precision == "decibeat":
            formatted = f"@{beats:03d}.{decibeats:01d}"
        else:  # centibeat (default)
            formatted = f"@{beats:03d}.{centibeats:02d}"
        
        # Build display value
        display_parts = [formatted]
        if self._show_period and period_data:
            display_parts.append(f"({period_data})")
        if milestone:
            display_parts.append(f"- {milestone}")
        
        display_value = " ".join(display_parts)
        
        # Calculate percentage of day
        day_progress = (beats_raw / self._swatch_data["beats_per_day"]) * 100
        
        result = {
            "beats": beats,
            "centibeats": centibeats,
            "decibeats": decibeats,
            "fractional": round(fractional_beat, 4),
            "formatted": formatted,
            "display_value": display_value,
            "bmt_time": bmt_time.strftime("%H:%M:%S BMT"),
            "seconds_since_midnight": round(seconds_since_midnight, 2),
            "day_progress": f"{day_progress:.1f}%",
            "full_display": display_value
        }
        
        if period_data:
            result["period"] = period_data
        
        if milestone:
            result["milestone"] = milestone
        
        # Add beat time conversions
        result["standard_time"] = earth_time.strftime("%H:%M:%S %Z")
        result["utc_time"] = earth_time.astimezone(datetime.now().astimezone().tzinfo).strftime("%H:%M:%S UTC%z")
        
        return result
    
    def _get_period(self, beats: int) -> str:
        """Get the period of day for given beats."""
        for period_range, period_name in self._swatch_data["periods"].items():
            start, end = period_range.replace("@", "").split("-")
            if int(start) <= beats <= int(end):
                return period_name
        return ""
    
    def _get_milestone(self, beats: int) -> str:
        """Check if current beat is a milestone."""
        beat_str = f"@{beats:03d}"
        return self._swatch_data["milestones"].get(beat_str, "")
    
    def update(self) -> None:
        """Update the sensor."""
        now = datetime.now()
        self._swatch_time = self._calculate_swatch_time(now)
        
        # Set state to formatted Swatch time
        self._state = self._swatch_time["formatted"]
        
        _LOGGER.debug(f"Updated Swatch Internet Time to {self._state}")