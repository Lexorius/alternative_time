"""Swatch Internet Time Calendar implementation - Version 2.8."""
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
    "version": "2.8.0",
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
        "en": "Internet Time in Beats @000-@999. One day = 1000 beats, no time zones (e.g. @500)",
        "de": "Internet-Zeit in Beats @000-@999. Ein Tag = 1000 Beats, keine Zeitzonen (z.B. @500)",
        "es": "Tiempo de Internet en Beats @000-@999. Un día = 1000 beats, sin zonas horarias (ej. @500)",
        "fr": "Temps Internet en Beats @000-@999. Un jour = 1000 beats, pas de fuseaux horaires (ex. @500)",
        "it": "Tempo Internet in Beat @000-@999. Un giorno = 1000 beat, nessun fuso orario (es. @500)",
        "nl": "Internet Tijd in Beats @000-@999. Eén dag = 1000 beats, geen tijdzones (bijv. @500)",
        "pt": "Tempo da Internet em Beats @000-@999. Um dia = 1000 beats, sem fusos horários (ex. @500)",
        "ru": "Интернет-время в битах @000-@999. Один день = 1000 битов, без часовых поясов (напр. @500)",
        "ja": "インターネットタイムをビート@000-@999で表示。1日=1000ビート、タイムゾーンなし（例：@500）",
        "zh": "互联网时间以节拍@000-@999表示。一天=1000节拍，无时区（例：@500）",
        "ko": "비트 @000-@999로 표시되는 인터넷 시간. 하루 = 1000비트, 시간대 없음 (예: @500)"
    },
    
    # Swatch-specific data
    "swatch_data": {
        "base_timezone": "Europe/Zurich",  # BMT (Biel Mean Time)
        "beats_per_day": 1000,
        "seconds_per_beat": 86.4,  # 86400 seconds / 1000 beats
        "reference_meridian": 7.5,  # Biel/Bienne longitude
    },
    
    # Additional metadata
    "reference_url": "https://en.wikipedia.org/wiki/Swatch_Internet_Time",
    "documentation_url": "https://www.swatch.com/en-us/internet-time/",
    "origin": "Swatch Corporation",
    "created_by": "Nicholas Negroponte & Swatch",
    "introduced": "October 23, 1998",
    
    # Example format
    "example": "@500",
    "example_meaning": "Noon in Biel, Switzerland (BMT)",
    
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
        "precision": {
            "type": "select",
            "default": "beat",  # Standard ist jetzt "beat"
            "options": ["beat", "decibeat", "centibeat"],
            "label": {
                "en": "Display Precision",
                "de": "Anzeigegenauigkeit",
                "es": "Precisión de Visualización",
                "fr": "Précision d'Affichage",
                "it": "Precisione di Visualizzazione",
                "nl": "Weergaveprecisie",
                "pt": "Precisão de Exibição",
                "ru": "Точность отображения",
                "ja": "表示精度",
                "zh": "显示精度",
                "ko": "표시 정밀도"
            },
            "description": {
                "en": "Standard (@500) | Decibeat (@500.5) | Centibeat (@500.50)",
                "de": "Standard (@500) | Decibeat (@500.5) | Centibeat (@500.50)",
                "es": "Estándar (@500) | Decibeat (@500.5) | Centibeat (@500.50)",
                "fr": "Standard (@500) | Decibeat (@500.5) | Centibeat (@500.50)",
                "it": "Standard (@500) | Decibeat (@500.5) | Centibeat (@500.50)",
                "nl": "Standaard (@500) | Decibeat (@500.5) | Centibeat (@500.50)",
                "pt": "Padrão (@500) | Decibeat (@500.5) | Centibeat (@500.50)",
                "ru": "Стандарт (@500) | Децибит (@500.5) | Сантибит (@500.50)",
                "ja": "標準 (@500) | デシビート (@500.5) | センチビート (@500.50)",
                "zh": "标准 (@500) | 分节拍 (@500.5) | 厘节拍 (@500.50)",
                "ko": "표준 (@500) | 데시비트 (@500.5) | 센티비트 (@500.50)"
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
        
        # Configuration option with default "beat"
        self._precision = options.get("precision", "beat")
        
        # Swatch data
        self._swatch_data = CALENDAR_INFO["swatch_data"]
        
        # WICHTIG: Timezone wird NICHT im __init__ geladen (blocking call)
        # Wird stattdessen lazy beim ersten Update geladen
        self._bmt = None
        self._bmt_initialized = False
        
        # Initialize state
        self._state = None
        
        _LOGGER.debug(f"Initialized Swatch Internet Time sensor: {self._attr_name}")
        _LOGGER.debug(f"  Precision: {self._precision}")
    
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
            
            # Add current configuration
            attrs["precision_setting"] = self._precision
        
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
        
        # Format based on precision setting
        if self._precision == "decibeat":
            formatted = f"@{beats:03d}.{decibeats:01d}"
        elif self._precision == "centibeat":
            formatted = f"@{beats:03d}.{centibeats:02d}"
        else:  # beat (default)
            formatted = f"@{beats:03d}"
        
        # Calculate percentage of day
        day_progress = (beats_raw / self._swatch_data["beats_per_day"]) * 100
        
        result = {
            "beats": beats,
            "centibeats": centibeats,
            "decibeats": decibeats,
            "fractional": round(fractional_beat, 4),
            "formatted": formatted,
            "bmt_time": bmt_time.strftime("%H:%M:%S BMT"),
            "local_time": earth_time.strftime("%H:%M:%S %Z"),
            "seconds_since_midnight_bmt": round(seconds_since_midnight, 2),
            "day_progress": f"{day_progress:.1f}%"
        }
        
        # Add time conversions
        result["utc_time"] = earth_time.astimezone(datetime.now().astimezone().tzinfo).strftime("%H:%M:%S UTC%z")
        
        return result
    
    def update(self) -> None:
        """Update the sensor."""
        now = datetime.now()
        self._swatch_time = self._calculate_swatch_time(now)
        
        # Set state to formatted Swatch time
        self._state = self._swatch_time["formatted"]
        
        _LOGGER.debug(f"Updated Swatch Internet Time to {self._state}")