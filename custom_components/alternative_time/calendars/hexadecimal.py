"""Hexadecimal Time implementation - Version 2.5."""
from __future__ import annotations

from datetime import datetime
import logging
from typing import Dict, Any

from homeassistant.core import HomeAssistant
from ..sensor import AlternativeTimeSensorBase

_LOGGER = logging.getLogger(__name__)

# ============================================
# CALENDAR METADATA
# ============================================

# Update interval in seconds (5 seconds for hexadecimal time)
UPDATE_INTERVAL = 5

# Complete calendar information for auto-discovery
CALENDAR_INFO = {
    "id": "hexadecimal",
    "version": "2.5.0",
    "icon": "mdi:hexadecimal",
    "category": "technical",
    "accuracy": "mathematical",
    "update_interval": UPDATE_INTERVAL,
    
    # Multi-language names
    "name": {
        "en": "Hexadecimal Time",
        "de": "Hexadezimalzeit",
        "es": "Tiempo Hexadecimal",
        "fr": "Temps Hexadécimal",
        "it": "Tempo Esadecimale",
        "nl": "Hexadecimale Tijd",
        "pt": "Tempo Hexadecimal",
        "ru": "Шестнадцатеричное время",
        "ja": "16進時間",
        "zh": "十六进制时间",
        "ko": "16진 시간"
    },
    
    # Short descriptions for UI
    "description": {
        "en": "Day divided into 65536 parts, displayed in hex (e.g. .8000 = noon)",
        "de": "Tag in 65536 Teile geteilt, Anzeige hexadezimal (z.B. .8000 = Mittag)",
        "es": "Día dividido en 65536 partes, mostrado en hex (ej. .8000 = mediodía)",
        "fr": "Jour divisé en 65536 parties, affiché en hex (ex. .8000 = midi)",
        "it": "Giorno diviso in 65536 parti, visualizzato in hex (es. .8000 = mezzogiorno)",
        "nl": "Dag verdeeld in 65536 delen, weergegeven in hex (bijv. .8000 = middag)",
        "pt": "Dia dividido em 65536 partes, exibido em hex (ex. .8000 = meio-dia)",
        "ru": "День разделен на 65536 частей, отображается в hex (напр. .8000 = полдень)",
        "ja": "1日を65536分割、16進表示（例：.8000 = 正午）",
        "zh": "一天分为65536部分，以十六进制显示（例：.8000 = 中午）",
        "ko": "하루를 65536 부분으로 나누어 16진수로 표시 (예: .8000 = 정오)"
    },
    
    # Detailed information for documentation
    "detailed_info": {
        "en": {
            "overview": "Hexadecimal time divides the day into 65,536 (0x10000 or 2^16) parts",
            "structure": "Each hexadecimal second = 1.318359375 standard seconds",
            "advantages": "Powers of 2 align perfectly with binary computing",
            "conversion": "No rounding errors in binary representation",
            "notation": ".0000 = midnight, .8000 = noon, .FFFF = 23:59:59",
            "precision": "16-bit precision provides smooth time progression",
            "computing": "Ideal for computer systems and binary calculations",
            "format": "Written with leading dot: .XXXX (4 hexadecimal digits)"
        },
        "de": {
            "overview": "Hexadezimalzeit teilt den Tag in 65.536 (0x10000 oder 2^16) Teile",
            "structure": "Jede hexadezimale Sekunde = 1,318359375 Standardsekunden",
            "advantages": "Zweierpotenzen passen perfekt zu binären Computern",
            "conversion": "Keine Rundungsfehler in binärer Darstellung",
            "notation": ".0000 = Mitternacht, .8000 = Mittag, .FFFF = 23:59:59",
            "precision": "16-Bit-Präzision bietet sanfte Zeitprogression",
            "computing": "Ideal für Computersysteme und binäre Berechnungen",
            "format": "Geschrieben mit führendem Punkt: .XXXX (4 Hexadezimalziffern)"
        }
    },
    
    # Hexadecimal time specific data
    "hex_data": {
        "units_per_day": 65536,  # 2^16
        "hex_max": "FFFF",
        "seconds_per_unit": 1.318359375,  # 86400/65536
        
        # Notable hex times
        "notable_times": {
            ".0000": {"time": "00:00:00", "description": "Midnight"},
            ".1000": {"time": "01:30:00", "description": "Early morning"},
            ".2000": {"time": "03:00:00", "description": "Late night"},
            ".3000": {"time": "04:30:00", "description": "Before dawn"},
            ".4000": {"time": "06:00:00", "description": "Dawn"},
            ".5000": {"time": "07:30:00", "description": "Early morning"},
            ".6000": {"time": "09:00:00", "description": "Morning"},
            ".7000": {"time": "10:30:00", "description": "Late morning"},
            ".8000": {"time": "12:00:00", "description": "Noon"},
            ".9000": {"time": "13:30:00", "description": "Early afternoon"},
            ".A000": {"time": "15:00:00", "description": "Afternoon"},
            ".B000": {"time": "16:30:00", "description": "Late afternoon"},
            ".C000": {"time": "18:00:00", "description": "Evening"},
            ".D000": {"time": "19:30:00", "description": "Dusk"},
            ".E000": {"time": "21:00:00", "description": "Night"},
            ".F000": {"time": "22:30:00", "description": "Late night"},
            ".FFFF": {"time": "23:59:59", "description": "End of day"}
        },
        
        # Binary breakdown
        "binary_info": {
            "bits": 16,
            "nibbles": 4,
            "bytes": 2,
            "max_value": 65535
        },
        
        # Conversion factors
        "conversions": {
            "hex_to_seconds": 1.318359375,
            "seconds_to_hex": 0.758518518,
            "hex_to_minutes": 0.021972656,
            "minutes_to_hex": 45.511111111
        }
    },
    
    # Additional metadata
    "reference_url": "https://en.wikipedia.org/wiki/Hexadecimal_time",
    "documentation_url": "https://www.mentalfloss.com/article/82696/brief-history-hexadecimal-time",
    "origin": "Computer science concept",
    "created_by": "Various computer scientists",
    
    # Example format
    "example": ".8F5C",
    "example_meaning": "Approximately 12:56 PM (halfway through afternoon)",
    
    # Related calendars
    "related": ["decimal", "binary", "unix"],
    
    # Tags for searching and filtering
    "tags": [
        "technical", "hexadecimal", "binary", "computer", "mathematical",
        "base16", "power_of_two", "digital", "programming"
    ],
    
    # Special features
    "features": {
        "binary_aligned": True,
        "computer_friendly": True,
        "no_rounding_errors": True,
        "power_of_two": True,
        "precision": "hexsecond"
    },
    
    # Configuration options for this calendar
    "config_options": {
        "show_decimal": {
            "type": "boolean",
            "default": False,
            "description": {
                "en": "Show decimal equivalent",
                "de": "Dezimaläquivalent anzeigen"
            }
        },
        "show_binary": {
            "type": "boolean",
            "default": False,
            "description": {
                "en": "Show binary representation",
                "de": "Binärdarstellung anzeigen"
            }
        },
        "uppercase": {
            "type": "boolean",
            "default": True,
            "description": {
                "en": "Use uppercase hex letters (A-F)",
                "de": "Großbuchstaben für Hex verwenden (A-F)"
            }
        }
    }
}


class HexadecimalTimeSensor(AlternativeTimeSensorBase):
    """Sensor for displaying Hexadecimal Time."""
    
    # Class-level update interval
    UPDATE_INTERVAL = 5  # Update every 5 seconds
    
    def __init__(self, base_name: str, hass: HomeAssistant) -> None:
        """Initialize the hexadecimal time sensor."""
        super().__init__(base_name, hass)
        
        # Get translated name from metadata
        calendar_name = self._translate('name', 'Hexadecimal Time')
        
        # Set sensor attributes
        self._attr_name = f"{base_name} {calendar_name}"
        self._attr_unique_id = f"{base_name}_hexadecimal"
        self._attr_icon = CALENDAR_INFO.get("icon", "mdi:hexadecimal")
        
        # Configuration options
        self._show_decimal = False
        self._show_binary = False
        self._uppercase = True
        
        # Hex data
        self._hex_data = CALENDAR_INFO["hex_data"]
        
        _LOGGER.debug(f"Initialized Hexadecimal Time sensor: {self._attr_name}")
    
    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes."""
        attrs = super().extra_state_attributes
        
        # Add Hexadecimal-specific attributes
        if hasattr(self, '_hex_time'):
            attrs.update(self._hex_time)
            
            # Add description in user's language
            attrs["description"] = self._translate('description')
            
            # Add reference
            attrs["reference"] = CALENDAR_INFO.get('reference_url', '')
            
            # Add conversion info
            attrs["units_per_day"] = self._hex_data["units_per_day"]
            attrs["seconds_per_unit"] = self._hex_data["seconds_per_unit"]
        
        return attrs
    
    def _calculate_hex_time(self, earth_time: datetime) -> Dict[str, Any]:
        """Calculate Hexadecimal Time from standard time."""
        
        # Calculate seconds since midnight
        seconds_since_midnight = earth_time.hour * 3600 + earth_time.minute * 60 + earth_time.second + earth_time.microsecond / 1000000
        
        # Convert to hexadecimal units (65536 units per day)
        hex_value = int(seconds_since_midnight * self._hex_data["units_per_day"] / 86400)
        
        # Format as hexadecimal
        if self._uppercase:
            hex_string = f"{hex_value:04X}"
        else:
            hex_string = f"{hex_value:04x}"
        
        formatted = f".{hex_string}"
        
        # Calculate percentage through day
        day_progress = (hex_value / self._hex_data["units_per_day"]) * 100
        
        # Find closest notable time
        closest_notable = None
        min_diff = float('inf')
        for notable_hex, data in self._hex_data["notable_times"].items():
            notable_value = int(notable_hex[1:], 16)
            diff = abs(notable_value - hex_value)
            if diff < min_diff:
                min_diff = diff
                closest_notable = f"{data['description']} ({notable_hex})"
        
        result = {
            "hex_value": hex_value,
            "hex_string": hex_string,
            "formatted": formatted,
            "day_progress": f"{day_progress:.1f}%",
            "standard_time": earth_time.strftime("%H:%M:%S"),
            "closest_notable": closest_notable,
            "full_display": formatted
        }
        
        # Add decimal if enabled
        if self._show_decimal:
            result["decimal_value"] = hex_value
            result["full_display"] += f" ({hex_value})"
        
        # Add binary if enabled
        if self._show_binary:
            binary = f"{hex_value:016b}"
            result["binary"] = binary
            result["binary_formatted"] = f"{binary[:4]} {binary[4:8]} {binary[8:12]} {binary[12:]}"
        
        return result
    
    def update(self) -> None:
        """Update the sensor."""
        now = datetime.now()
        self._hex_time = self._calculate_hex_time(now)
        
        # Set state to formatted hex time
        self._state = self._hex_time["formatted"]
        
        _LOGGER.debug(f"Updated Hexadecimal Time to {self._state}")