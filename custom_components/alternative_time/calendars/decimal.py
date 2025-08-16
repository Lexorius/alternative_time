"""Decimal Time (French Revolutionary Time) implementation - Version 2.5."""
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

# Update interval in seconds (1 second for smooth time display)
UPDATE_INTERVAL = 1

# Complete calendar information for auto-discovery
CALENDAR_INFO = {
    "id": "decimal",
    "version": "2.5.0",
    "icon": "mdi:clock-digital",
    "category": "technical",
    "accuracy": "mathematical",
    "update_interval": UPDATE_INTERVAL,
    
    # Multi-language names
    "name": {
        "en": "Decimal Time",
        "de": "Dezimalzeit",
        "es": "Tiempo Decimal",
        "fr": "Temps Décimal",
        "it": "Tempo Decimale",
        "nl": "Decimale Tijd",
        "pt": "Tempo Decimal",
        "ru": "Десятичное время",
        "ja": "十進時間",
        "zh": "十进制时间",
        "ko": "십진 시간"
    },
    
    # Short descriptions for UI
    "description": {
        "en": "French Revolutionary time: 10 hours, 100 minutes, 100 seconds per day",
        "de": "Französische Revolutionszeit: 10 Stunden, 100 Minuten, 100 Sekunden pro Tag",
        "es": "Tiempo revolucionario francés: 10 horas, 100 minutos, 100 segundos por día",
        "fr": "Temps révolutionnaire français : 10 heures, 100 minutes, 100 secondes par jour",
        "it": "Tempo rivoluzionario francese: 10 ore, 100 minuti, 100 secondi al giorno",
        "nl": "Franse revolutionaire tijd: 10 uur, 100 minuten, 100 seconden per dag",
        "pt": "Tempo revolucionário francês: 10 horas, 100 minutos, 100 segundos por dia",
        "ru": "Французское революционное время: 10 часов, 100 минут, 100 секунд в день",
        "ja": "フランス革命暦時間：1日10時間、100分、100秒",
        "zh": "法国革命时间：每天10小时，100分钟，100秒",
        "ko": "프랑스 혁명 시간: 하루 10시간, 100분, 100초"
    },
    
    # Detailed information for documentation
    "detailed_info": {
        "en": {
            "overview": "Decimal Time was part of the French Republican Calendar during the French Revolution",
            "structure": "Day divided into 10 decimal hours, 100 decimal minutes per hour, 100 decimal seconds per minute",
            "total": "10 × 100 × 100 = 100,000 decimal seconds per day (vs 86,400 standard seconds)",
            "conversion": "1 decimal hour = 2.4 standard hours = 144 minutes",
            "minute": "1 decimal minute = 1.44 standard minutes = 86.4 seconds",
            "second": "1 decimal second = 0.864 standard seconds",
            "usage": "Officially used in France from 1793 to 1805",
            "midnight": "Midnight = 0:00:00, Noon = 5:00:00, 6 PM = 7:50:00",
            "clocks": "Special decimal clocks were manufactured with 10-hour faces"
        },
        "de": {
            "overview": "Die Dezimalzeit war Teil des Französischen Revolutionskalenders während der Französischen Revolution",
            "structure": "Tag unterteilt in 10 Dezimalstunden, 100 Dezimalminuten pro Stunde, 100 Dezimalsekunden pro Minute",
            "total": "10 × 100 × 100 = 100.000 Dezimalsekunden pro Tag (vs 86.400 Standardsekunden)",
            "conversion": "1 Dezimalstunde = 2,4 Standardstunden = 144 Minuten",
            "minute": "1 Dezimalminute = 1,44 Standardminuten = 86,4 Sekunden",
            "second": "1 Dezimalsekunde = 0,864 Standardsekunden",
            "usage": "Offiziell in Frankreich von 1793 bis 1805 verwendet",
            "midnight": "Mitternacht = 0:00:00, Mittag = 5:00:00, 18 Uhr = 7:50:00",
            "clocks": "Spezielle Dezimaluhren wurden mit 10-Stunden-Zifferblättern hergestellt"
        },
        "fr": {
            "overview": "Le Temps Décimal faisait partie du Calendrier Républicain Français pendant la Révolution Française",
            "structure": "Jour divisé en 10 heures décimales, 100 minutes décimales par heure, 100 secondes décimales par minute",
            "total": "10 × 100 × 100 = 100 000 secondes décimales par jour (vs 86 400 secondes standard)",
            "conversion": "1 heure décimale = 2,4 heures standard = 144 minutes",
            "minute": "1 minute décimale = 1,44 minutes standard = 86,4 secondes",
            "second": "1 seconde décimale = 0,864 secondes standard",
            "usage": "Officiellement utilisé en France de 1793 à 1805",
            "midnight": "Minuit = 0:00:00, Midi = 5:00:00, 18h = 7:50:00",
            "clocks": "Des horloges décimales spéciales ont été fabriquées avec des cadrans de 10 heures"
        }
    },
    
    # Decimal time specific data
    "decimal_data": {
        "hours_per_day": 10,
        "minutes_per_hour": 100,
        "seconds_per_minute": 100,
        "total_seconds": 100000,
        "standard_seconds": 86400,
        
        # Conversion factors
        "conversions": {
            "decimal_hour_to_minutes": 144,  # standard minutes
            "decimal_minute_to_seconds": 86.4,  # standard seconds
            "decimal_second_to_seconds": 0.864,  # standard seconds
            "standard_hour_to_decimal": 0.41667,  # decimal hours
            "standard_minute_to_decimal": 0.00694,  # decimal hours
        },
        
        # Notable times
        "notable_times": {
            "0:00:00": "Midnight",
            "2:50:00": "Dawn (6:00 AM)",
            "3:75:00": "Morning (9:00 AM)",
            "5:00:00": "Noon",
            "6:25:00": "Afternoon (3:00 PM)",
            "7:50:00": "Evening (6:00 PM)",
            "8:75:00": "Night (9:00 PM)",
            "9:58:33": "11:00 PM"
        },
        
        # French Republican names for time periods
        "republican_names": {
            "hour": "heure décimale",
            "minute": "minute décimale",
            "second": "seconde décimale"
        },
        
        # Historical period
        "period": {
            "start": "1793-10-05",
            "end": "1805-12-31",
            "reason": "Part of metrication during French Revolution"
        }
    },
    
    # Additional metadata
    "reference_url": "https://en.wikipedia.org/wiki/Decimal_time",
    "documentation_url": "https://www.britannica.com/science/decimal-time",
    "origin": "French Revolution",
    "created_by": "French Republican Government",
    "introduced": "October 5, 1793",
    "discontinued": "December 31, 1805",
    
    # Example format
    "example": "5:42:36",
    "example_meaning": "5 decimal hours, 42 decimal minutes, 36 decimal seconds (approximately 1:00 PM)",
    
    # Related calendars
    "related": ["french_republican", "metric", "swatch"],
    
    # Tags for searching and filtering
    "tags": [
        "technical", "decimal", "french", "revolutionary", "metric",
        "mathematical", "historical", "base10", "decimalization"
    ],
    
    # Special features
    "features": {
        "decimal_based": True,
        "metric_time": True,
        "continuous_count": True,
        "precision": "second",
        "mathematical_simplicity": True
    },
    
    # Configuration options for this calendar
    "config_options": {
        "show_conversion": {
            "type": "boolean",
            "default": True,
            "description": {
                "en": "Show standard time conversion",
                "de": "Standardzeit-Umrechnung anzeigen",
                "fr": "Afficher la conversion en temps standard"
            }
        },
        "precision": {
            "type": "select",
            "default": "second",
            "options": ["hour", "minute", "second"],
            "description": {
                "en": "Display precision",
                "de": "Anzeigegenauigkeit",
                "fr": "Précision d'affichage"
            }
        },
        "show_period_name": {
            "type": "boolean",
            "default": False,
            "description": {
                "en": "Show time period name (Dawn, Noon, etc.)",
                "de": "Tageszeitname anzeigen (Morgengrauen, Mittag, usw.)",
                "fr": "Afficher le nom de la période (Aube, Midi, etc.)"
            }
        }
    }
}


class DecimalTimeSensor(AlternativeTimeSensorBase):
    """Sensor for displaying Decimal Time (French Revolutionary)."""
    
    # Class-level update interval
    UPDATE_INTERVAL = 1  # Update every second
    
    def __init__(self, base_name: str, hass: HomeAssistant) -> None:
        """Initialize the decimal time sensor."""
        super().__init__(base_name, hass)
        
        # Get translated name from metadata
        calendar_name = self._translate('name', 'Decimal Time')
        
        # Set sensor attributes
        self._attr_name = f"{base_name} {calendar_name}"
        self._attr_unique_id = f"{base_name}_decimal"
        self._attr_icon = CALENDAR_INFO.get("icon", "mdi:clock-digital")
        
        # Configuration options
        self._show_conversion = True
        self._precision = "second"
        self._show_period_name = False
        
        # Decimal data
        self._decimal_data = CALENDAR_INFO["decimal_data"]
        
        _LOGGER.debug(f"Initialized Decimal Time sensor: {self._attr_name}")
    
    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes."""
        attrs = super().extra_state_attributes
        
        # Add Decimal-specific attributes
        if hasattr(self, '_decimal_time'):
            attrs.update(self._decimal_time)
            
            # Add description in user's language
            attrs["description"] = self._translate('description')
            
            # Add reference
            attrs["reference"] = CALENDAR_INFO.get('reference_url', '')
            
            # Add conversion info
            attrs["decimal_seconds_per_day"] = self._decimal_data["total_seconds"]
            attrs["standard_seconds_per_day"] = self._decimal_data["standard_seconds"]
        
        return attrs
    
    def _get_period_name(self, decimal_hours: float) -> str:
        """Get the period name for decimal time."""
        if decimal_hours < 1.0:
            return "Night"
        elif decimal_hours < 2.5:
            return "Late Night"
        elif decimal_hours < 3.0:
            return "Dawn"
        elif decimal_hours < 4.0:
            return "Morning"
        elif decimal_hours < 5.0:
            return "Late Morning"
        elif decimal_hours < 6.0:
            return "Afternoon"
        elif decimal_hours < 7.5:
            return "Late Afternoon"
        elif decimal_hours < 8.5:
            return "Evening"
        elif decimal_hours < 9.5:
            return "Night"
        else:
            return "Late Night"
    
    def _calculate_decimal_time(self, earth_time: datetime) -> Dict[str, Any]:
        """Calculate Decimal Time from standard time."""
        
        # Calculate seconds since midnight
        seconds_since_midnight = earth_time.hour * 3600 + earth_time.minute * 60 + earth_time.second + earth_time.microsecond / 1000000
        
        # Convert to decimal seconds (100,000 per day)
        decimal_seconds_total = seconds_since_midnight * self._decimal_data["total_seconds"] / self._decimal_data["standard_seconds"]
        
        # Extract decimal hours, minutes, and seconds
        decimal_hours = int(decimal_seconds_total // 10000)
        decimal_minutes = int((decimal_seconds_total % 10000) // 100)
        decimal_seconds = int(decimal_seconds_total % 100)
        decimal_fraction = decimal_seconds_total % 1
        
        # Format based on precision
        if self._precision == "hour":
            formatted = f"{decimal_hours:01d}"
            display_value = f"{decimal_hours:01d}h"
        elif self._precision == "minute":
            formatted = f"{decimal_hours:01d}:{decimal_minutes:02d}"
            display_value = f"{decimal_hours:01d}h {decimal_minutes:02d}m"
        else:  # second
            formatted = f"{decimal_hours:01d}:{decimal_minutes:02d}:{decimal_seconds:02d}"
            display_value = formatted
        
        # Get period name if enabled
        period_name = self._get_period_name(decimal_hours + decimal_minutes/100) if self._show_period_name else ""
        
        # Calculate percentage through day
        day_progress = (decimal_seconds_total / self._decimal_data["total_seconds"]) * 100
        
        # Find closest notable time
        closest_notable = None
        min_diff = float('inf')
        for notable_time, description in self._decimal_data["notable_times"].items():
            parts = notable_time.split(':')
            notable_total = int(parts[0]) * 10000 + int(parts[1]) * 100 + int(parts[2])
            diff = abs(notable_total - decimal_seconds_total)
            if diff < min_diff:
                min_diff = diff
                closest_notable = f"{description} ({notable_time})"
        
        result = {
            "hours": decimal_hours,
            "minutes": decimal_minutes,
            "seconds": decimal_seconds,
            "fraction": round(decimal_fraction, 3),
            "formatted": formatted,
            "display_value": display_value,
            "total_decimal_seconds": round(decimal_seconds_total, 2),
            "day_progress": f"{day_progress:.1f}%",
            "full_display": formatted
        }
        
        # Add conversion if enabled
        if self._show_conversion:
            result["standard_time"] = earth_time.strftime("%H:%M:%S")
            result["conversion"] = f"{formatted} = {earth_time.strftime('%H:%M:%S')}"
            result["full_display"] = f"{formatted} ({earth_time.strftime('%H:%M')})"
        
        # Add period name if enabled
        if period_name:
            result["period"] = period_name
            result["full_display"] += f" - {period_name}"
        
        # Add closest notable time
        if closest_notable:
            result["closest_notable"] = closest_notable
        
        return result
    
    def update(self) -> None:
        """Update the sensor."""
        now = datetime.now()
        self._decimal_time = self._calculate_decimal_time(now)
        
        # Set state to formatted decimal time
        self._state = self._decimal_time["formatted"]
        
        _LOGGER.debug(f"Updated Decimal Time to {self._state}")