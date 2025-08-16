"""Swatch Internet Time Calendar implementation - Version 2.5."""
from __future__ import annotations

from datetime import datetime, timedelta
import logging
from typing import Dict, Any, Optional

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
    "category": "modern",
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
        "ko": "스와치 인터넷 시간",
        "sv": "Swatch Internettid",
        "no": "Swatch Internett-tid",
        "da": "Swatch Internet-tid",
        "fi": "Swatch Internet-aika"
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
        "ja": "ビート単位のインターネット時間 @000-@999。1日 = 1000ビート、タイムゾーンなし（例：@500.00）",
        "zh": "互联网时间以节拍计 @000-@999。一天 = 1000节拍，无时区（例：@500.00）",
        "ko": "비트 단위 인터넷 시간 @000-@999. 하루 = 1000 비트, 시간대 없음 (예: @500.00)"
    },
    
    # Detailed information for documentation
    "detailed_info": {
        "en": {
            "overview": "Swatch Internet Time was introduced in 1998 by the Swatch corporation as a decimal time concept",
            "structure": "The day is divided into 1000 '.beats', each lasting 1 minute and 26.4 seconds (86.4 seconds)",
            "timezone": "No time zones - everyone uses the same time globally. Based on BMT (Biel Mean Time = UTC+1)",
            "format": "Written as @XXX or @XXX.XX where XXX is the beat number from 000 to 999",
            "midnight": "@000 = midnight BMT (23:00 UTC), @500 = noon BMT (11:00 UTC), @999 = 23:59:24 BMT",
            "origin": "Named after Biel, Switzerland, location of Swatch headquarters",
            "marketing": "Marketed with the slogan 'No Time Zones. No Geographical Borders.'",
            "adoption": "Used briefly by some websites and online games in early 2000s, now mostly historical curiosity",
            "calculation": "Beats = (seconds_since_midnight_BMT) / 86.4"
        },
        "de": {
            "overview": "Die Swatch Internet-Zeit wurde 1998 von der Swatch-Firma als dezimales Zeitkonzept eingeführt",
            "structure": "Der Tag wird in 1000 '.beats' unterteilt, jeder dauert 1 Minute und 26,4 Sekunden (86,4 Sekunden)",
            "timezone": "Keine Zeitzonen - alle verwenden weltweit dieselbe Zeit. Basiert auf BMT (Bieler Mittelzeit = UTC+1)",
            "format": "Geschrieben als @XXX oder @XXX.XX, wobei XXX die Beat-Nummer von 000 bis 999 ist",
            "midnight": "@000 = Mitternacht BMT (23:00 UTC), @500 = Mittag BMT (11:00 UTC), @999 = 23:59:24 BMT",
            "origin": "Benannt nach Biel, Schweiz, dem Hauptsitz von Swatch",
            "marketing": "Vermarktet mit dem Slogan 'Keine Zeitzonen. Keine geografischen Grenzen.'",
            "adoption": "Wurde kurz von einigen Websites und Online-Spielen Anfang 2000 verwendet, heute meist historische Kuriosität",
            "calculation": "Beats = (Sekunden_seit_Mitternacht_BMT) / 86,4"
        },
        "fr": {
            "overview": "Le Temps Internet Swatch a été introduit en 1998 par Swatch comme concept de temps décimal",
            "structure": "La journée est divisée en 1000 '.beats', chacun durant 1 minute et 26,4 secondes (86,4 secondes)",
            "timezone": "Pas de fuseaux horaires - tout le monde utilise la même heure. Basé sur BMT (Biel Mean Time = UTC+1)",
            "format": "Écrit @XXX ou @XXX.XX où XXX est le numéro de beat de 000 à 999",
            "midnight": "@000 = minuit BMT (23h00 UTC), @500 = midi BMT (11h00 UTC), @999 = 23h59:24 BMT",
            "origin": "Nommé d'après Bienne, Suisse, siège de Swatch",
            "marketing": "Commercialisé avec le slogan 'Pas de fuseaux horaires. Pas de frontières géographiques.'",
            "adoption": "Utilisé brièvement par certains sites web et jeux en ligne au début des années 2000",
            "calculation": "Beats = (secondes_depuis_minuit_BMT) / 86,4"
        }
    },
    
    # Swatch-specific data
    "swatch_data": {
        "beats_per_day": 1000,
        "seconds_per_beat": 86.4,
        "base_timezone": "Europe/Zurich",
        "bmt_offset": 1,  # UTC+1
        
        # Beat periods (unofficial but commonly used)
        "periods": [
            {"range": (0, 125), "name": "Night", "emoji": "🌙", "color": "#1a237e"},
            {"range": (125, 375), "name": "Morning", "emoji": "🌅", "color": "#fbc02d"},
            {"range": (375, 625), "name": "Afternoon", "emoji": "☀️", "color": "#ff6f00"},
            {"range": (625, 875), "name": "Evening", "emoji": "🌆", "color": "#4a148c"},
            {"range": (875, 1000), "name": "Night", "emoji": "🌙", "color": "#1a237e"}
        ],
        
        # Centibeat subdivisions
        "subdivisions": {
            "centibeat": 0.01,  # 1/100 of a beat = 0.864 seconds
            "decibeat": 0.1,    # 1/10 of a beat = 8.64 seconds
            "millibeat": 0.001  # 1/1000 of a beat = 0.0864 seconds
        },
        
        # Historical milestones
        "milestones": {
            "@000": "Midnight in Biel - Start of the Internet Day",
            "@041": "Traditional start of work day (9:00 CET)",
            "@250": "Morning quarter - Coffee break time",
            "@375": "Traditional lunch time (13:00 CET)",
            "@500": "Noon in Biel - Halfway through the Internet Day",
            "@750": "Evening quarter - Traditional dinner time",
            "@833": "Traditional end of work day (18:00 CET)",
            "@999": "Last beat before midnight"
        }
    },
    
    # Additional metadata
    "reference_url": "https://en.wikipedia.org/wiki/Swatch_Internet_Time",
    "documentation_url": "https://www.swatch.com/en-us/internet-time/",
    "origin": "Swatch Corporation, Switzerland",
    "created_by": "Nicolas G. Hayek and Swatch",
    "introduced": "October 23, 1998",
    "deprecated": "Approximately 2001 (no longer actively promoted)",
    
    # Example format
    "example": "@573.25",
    "example_meaning": "573.25 beats after midnight BMT (approximately 13:45 CET)",
    
    # Related calendars
    "related": ["decimal", "unix", "hexadecimal"],
    
    # Tags for searching and filtering
    "tags": [
        "modern", "decimal", "internet", "swatch", "switzerland",
        "biel", "bmt", "no_timezone", "global_time", "beats",
        "1990s", "commercial", "experimental", "deprecated"
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
            "description": {
                "en": "Show fractional beats (e.g. @500.25)",
                "de": "Zeige Bruchteile von Beats (z.B. @500.25)"
            }
        },
        "show_centibeats": {
            "type": "boolean",
            "default": False,
            "description": {
                "en": "Show centibeats separately (e.g. @500:25)",
                "de": "Zeige Centibeats separat (z.B. @500:25)"
            }
        },
        "show_period": {
            "type": "boolean",
            "default": True,
            "description": {
                "en": "Show period of day (Morning, Afternoon, etc.)",
                "de": "Zeige Tagesperiode (Morgen, Nachmittag, usw.)"
            }
        },
        "use_color_coding": {
            "type": "boolean",
            "default": False,
            "description": {
                "en": "Use color coding for different periods",
                "de": "Verwende Farbcodierung für verschiedene Perioden"
            }
        },
        "show_milestones": {
            "type": "boolean",
            "default": False,
            "description": {
                "en": "Show milestone descriptions at specific beats",
                "de": "Zeige Meilenstein-Beschreibungen bei bestimmten Beats"
            }
        },
        "precision": {
            "type": "select",
            "default": "centibeat",
            "options": ["beat", "decibeat", "centibeat", "millibeat"],
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
        
        # Get translated name from metadata
        calendar_name = self._translate('name', 'Swatch Internet Time')
        
        # Set sensor attributes
        self._attr_name = f"{base_name} {calendar_name}"
        self._attr_unique_id = f"{base_name}_swatch"
        self._attr_icon = CALENDAR_INFO.get("icon", "mdi:web-clock")
        
        # Get configuration options (from config or defaults)
        self._show_fractional = True
        self._show_centibeats = False
        self._show_period = True
        self._use_color_coding = False
        self._show_milestones = False
        self._precision = "centibeat"
        
        # Swatch data
        self._swatch_data = CALENDAR_INFO["swatch_data"]
        
        # Initialize timezone
        self._bmt = None
        if HAS_PYTZ:
            try:
                self._bmt = pytz.timezone(self._swatch_data["base_timezone"])
            except Exception:
                _LOGGER.warning(f"Could not load timezone {self._swatch_data['base_timezone']}")
        
        _LOGGER.debug(f"Initialized Swatch Internet Time sensor: {self._attr_name}")
    
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
    
    def _translate(self, key: str, default: str = "") -> str:
        """Get translated string from metadata."""
        # This would need access to hass.config.language
        # For now, default to English
        lang = "en"
        
        if key in CALENDAR_INFO:
            translations = CALENDAR_INFO[key]
            if isinstance(translations, dict):
                return translations.get(lang, translations.get("en", default))
        
        return default
    
    def _calculate_swatch_time(self, earth_time: datetime) -> Dict[str, Any]:
        """Calculate Swatch Internet Time from standard time."""
        
        # Get time in BMT (Biel Mean Time)
        if HAS_PYTZ and self._bmt:
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
        millibeats = int(fractional_beat * 1000)
        
        # Determine period of day
        period_data = self._get_period(beats)
        
        # Check for milestones
        milestone = self._get_milestone(beats) if self._show_milestones else ""
        
        # Format based on precision setting
        if self._precision == "beat":
            formatted = f"@{beats:03d}"
            display_value = beats
        elif self._precision == "decibeat":
            formatted = f"@{beats:03d}.{decibeats:01d}"
            display_value = beats + decibeats / 10
        elif self._precision == "millibeat":
            formatted = f"@{beats:03d}.{millibeats:03d}"
            display_value = beats + millibeats / 1000
        else:  # centibeat (default)
            formatted = f"@{beats:03d}.{centibeats:02d}"
            display_value = beats + centibeats / 100
        
        # Alternative format with separator
        if self._show_centibeats:
            formatted_alt = f"@{beats:03d}:{centibeats:02d}"
        else:
            formatted_alt = formatted
        
        # Calculate progress through the day
        day_progress = beats_raw / self._swatch_data["beats_per_day"]
        day_progress_percent = day_progress * 100
        
        # Convert to standard time for reference
        standard_time = bmt_time.strftime("%H:%M:%S BMT")
        utc_time = earth_time.astimezone(pytz.UTC).strftime("%H:%M:%S UTC") if HAS_PYTZ else ""
        
        # Build result
        result = {
            "beats": beats,
            "formatted": formatted,
            "formatted_alt": formatted_alt,
            "raw_value": beats_raw,
            "display_value": display_value,
            "centibeats": centibeats,
            "decibeats": decibeats,
            "millibeats": millibeats,
            "fractional": fractional_beat,
            "bmt_time": standard_time,
            "utc_time": utc_time,
            "day_progress": f"{day_progress_percent:.1f}%",
            "full_display": formatted
        }
        
        # Add period if enabled
        if self._show_period:
            result["period"] = f"{period_data['emoji']} {period_data['name']}"
            result["period_name"] = period_data["name"]
            result["full_display"] = f"{formatted} - {period_data['name']}"
        
        # Add color if enabled
        if self._use_color_coding:
            result["color"] = period_data["color"]
        
        # Add milestone if found
        if milestone:
            result["milestone"] = milestone
            result["full_display"] += f" | {milestone}"
        
        # Add beat range info
        result["next_beat_in"] = f"{(1 - fractional_beat) * self._swatch_data['seconds_per_beat']:.1f}s"
        result["seconds_in_beat"] = f"{fractional_beat * self._swatch_data['seconds_per_beat']:.1f}s"
        
        return result
    
    def _get_period(self, beats: int) -> Dict[str, str]:
        """Get period of day for given beat."""
        for period in self._swatch_data["periods"]:
            start, end = period["range"]
            if start <= beats < end:
                return period
        
        # Default to last period
        return self._swatch_data["periods"][-1]
    
    def _get_milestone(self, beats: int) -> str:
        """Get milestone description if beat is near a milestone."""
        milestones = self._swatch_data["milestones"]
        
        # Check if current beat is within 5 beats of a milestone
        for milestone_beat_str, description in milestones.items():
            milestone_beat = int(milestone_beat_str[1:])  # Remove @ symbol
            if abs(beats - milestone_beat) < 5:
                return description
        
        return ""
    
    def update(self) -> None:
        """Update the sensor."""
        now = datetime.now()
        self._swatch_time = self._calculate_swatch_time(now)
        
        # Set state to formatted time
        self._state = self._swatch_time["formatted"]
        
        _LOGGER.debug(f"Updated Swatch Internet Time to {self._state}")