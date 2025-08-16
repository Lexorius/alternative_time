"""Julian Date Calendar implementation - Version 2.5."""
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

# Update interval in seconds (60 seconds - minute precision is sufficient)
UPDATE_INTERVAL = 60

# Complete calendar information for auto-discovery
CALENDAR_INFO = {
    "id": "julian",
    "version": "2.5.0",
    "icon": "mdi:calendar-clock",
    "category": "technical",
    "accuracy": "astronomical",
    "update_interval": UPDATE_INTERVAL,
    
    # Multi-language names
    "name": {
        "en": "Julian Date",
        "de": "Julianisches Datum",
        "es": "Fecha Juliana",
        "fr": "Date Julienne",
        "it": "Data Giuliana",
        "nl": "Juliaanse Datum",
        "pt": "Data Juliana",
        "ru": "Юлианская дата",
        "ja": "ユリウス通日",
        "zh": "儒略日",
        "ko": "율리우스일"
    },
    
    # Short descriptions for UI
    "description": {
        "en": "Astronomical day count since 4713 BCE (e.g. 2460000.5)",
        "de": "Astronomische Tageszählung seit 4713 v.Chr. (z.B. 2460000.5)",
        "es": "Conteo astronómico de días desde 4713 a.C. (ej. 2460000.5)",
        "fr": "Comptage astronomique des jours depuis 4713 av. J.-C. (ex. 2460000.5)",
        "it": "Conteggio astronomico dei giorni dal 4713 a.C. (es. 2460000.5)",
        "nl": "Astronomische dagentelling sinds 4713 v.Chr. (bijv. 2460000.5)",
        "pt": "Contagem astronômica de dias desde 4713 a.C. (ex. 2460000.5)",
        "ru": "Астрономический счет дней с 4713 г. до н.э. (напр. 2460000.5)",
        "ja": "紀元前4713年からの天文学的日数（例：2460000.5）",
        "zh": "自公元前4713年起的天文日计数（例：2460000.5）",
        "ko": "기원전 4713년부터의 천문학적 일수 (예: 2460000.5)"
    },
    
    # Detailed information for documentation
    "detailed_info": {
        "en": {
            "overview": "The Julian Date is a continuous count of days since the beginning of the Julian Period",
            "epoch": "JD 0 = January 1, 4713 BCE at noon UTC in the proleptic Julian calendar",
            "structure": "Integer days + decimal fraction for time of day",
            "j2000": "JD 2451545.0 = January 1, 2000 at noon UTC (J2000.0 epoch)",
            "usage": "Used primarily in astronomy for calculating time intervals and avoiding calendar discontinuities",
            "precision": "Format: XXXXXXX.XXXXX (5 decimal places = precision to about 1 second)",
            "calculation": "Based on Meeus 'Astronomical Algorithms' formula",
            "note": "JD starts at noon UTC, not midnight"
        },
        "de": {
            "overview": "Das Julianische Datum ist eine kontinuierliche Tageszählung seit Beginn der Julianischen Periode",
            "epoch": "JD 0 = 1. Januar 4713 v.Chr. um 12:00 UTC im proleptischen Julianischen Kalender",
            "structure": "Ganzzahlige Tage + Dezimalbruch für die Tageszeit",
            "j2000": "JD 2451545.0 = 1. Januar 2000 um 12:00 UTC (J2000.0 Epoche)",
            "usage": "Hauptsächlich in der Astronomie für Zeitintervallberechnungen verwendet",
            "precision": "Format: XXXXXXX.XXXXX (5 Dezimalstellen = Genauigkeit etwa 1 Sekunde)",
            "calculation": "Basiert auf Meeus 'Astronomical Algorithms' Formel",
            "note": "JD beginnt um 12:00 UTC, nicht um Mitternacht"
        }
    },
    
    # Julian Date specific data
    "julian_data": {
        "epoch_jd": 0,
        "epoch_date": "January 1, 4713 BCE, 12:00 UTC",
        "j2000_jd": 2451545.0,
        "j2000_date": "January 1, 2000, 12:00 UTC",
        "mjd_offset": 2400000.5,  # Modified Julian Date offset
        "unix_epoch_jd": 2440587.5,  # Unix epoch in JD
        
        # Important astronomical epochs in JD
        "epochs": {
            "B1900.0": 2415020.0,
            "B1950.0": 2433282.5,
            "J2000.0": 2451545.0,
            "J2050.0": 2469807.5
        },
        
        # Conversion factors
        "julian_century": 36525,  # Days in Julian century
        "julian_year": 365.25,    # Days in Julian year
        
        # Common JD ranges
        "ranges": {
            "gregorian_adoption": 2299161,  # October 15, 1582
            "unix_epoch": 2440587.5,  # January 1, 1970
            "y2k": 2451544.5,  # January 1, 2000, 00:00 UTC
            "current_century": (2451545, 2488070)  # 2000-2100
        }
    },
    
    # Additional metadata
    "reference_url": "https://en.wikipedia.org/wiki/Julian_day",
    "documentation_url": "https://aa.usno.navy.mil/data/JulianDate",
    "origin": "Joseph Justus Scaliger, 1583",
    "created_by": "Joseph Justus Scaliger",
    
    # Example format
    "example": "2460000.50000",
    "example_meaning": "2460000 days and 12 hours since JD epoch",
    
    # Related calendars
    "related": ["unix", "decimal", "gregorian"],
    
    # Tags for searching and filtering
    "tags": [
        "technical", "astronomical", "scientific", "continuous",
        "julian", "scaliger", "astronomy", "time_interval",
        "ephemeris", "orbital", "celestial"
    ],
    
    # Special features
    "features": {
        "supports_bc_dates": True,
        "continuous_count": True,
        "decimal_time": True,
        "timezone_independent": True,  # Always UTC based
        "leap_second_aware": False,
        "precision": "second",
        "range": "unlimited"
    },
    
    # Configuration options for this calendar
    "config_options": {
        "show_mjd": {
            "type": "boolean",
            "default": True,
            "description": {
                "en": "Also show Modified Julian Date (MJD)",
                "de": "Auch Modifiziertes Julianisches Datum (MJD) anzeigen"
            }
        },
        "decimal_places": {
            "type": "select",
            "default": 5,
            "options": [1, 2, 3, 4, 5, 6],
            "description": {
                "en": "Number of decimal places to display",
                "de": "Anzahl der anzuzeigenden Dezimalstellen"
            }
        },
        "show_fraction_as_time": {
            "type": "boolean",
            "default": False,
            "description": {
                "en": "Show decimal fraction as HH:MM:SS",
                "de": "Dezimalbruch als HH:MM:SS anzeigen"
            }
        }
    }
}


class JulianDateSensor(AlternativeTimeSensorBase):
    """Sensor for displaying Julian Date."""
    
    # Class-level update interval
    UPDATE_INTERVAL = 60  # Update every minute
    
    def __init__(self, base_name: str, hass: HomeAssistant) -> None:
        """Initialize the Julian date sensor."""
        super().__init__(base_name, hass)
        
        # Get translated name from metadata
        calendar_name = self._translate('name', 'Julian Date')
        
        # Set sensor attributes
        self._attr_name = f"{base_name} {calendar_name}"
        self._attr_unique_id = f"{base_name}_julian"
        self._attr_icon = CALENDAR_INFO.get("icon", "mdi:calendar-clock")
        
        # Configuration options
        self._show_mjd = True
        self._decimal_places = 5
        self._show_fraction_as_time = False
        
        # Julian data
        self._julian_data = CALENDAR_INFO["julian_data"]
        
        _LOGGER.debug(f"Initialized Julian Date sensor: {self._attr_name}")
    
    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes."""
        attrs = super().extra_state_attributes
        
        # Add Julian-specific attributes
        if hasattr(self, '_julian_date_info'):
            attrs.update(self._julian_date_info)
            
            # Add description in user's language
            attrs["description"] = self._translate('description')
            
            # Add reference
            attrs["reference"] = CALENDAR_INFO.get('reference_url', '')
            
            # Add epoch information
            attrs["epoch"] = self._julian_data["epoch_date"]
            attrs["j2000_offset"] = round(self._julian_date_info["jd"] - self._julian_data["j2000_jd"], 5)
        
        return attrs
    
    def _calculate_julian_date(self, earth_time: datetime) -> Dict[str, Any]:
        """Calculate Julian Date from standard time."""
        
        # Algorithm from Meeus, "Astronomical Algorithms"
        a = (14 - earth_time.month) // 12
        y = earth_time.year + 4800 - a
        m = earth_time.month + 12 * a - 3
        
        # Calculate Julian Day Number (JDN) for the date at noon
        jdn = earth_time.day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
        
        # Add fractional day for time
        # JD starts at noon, so subtract 12 hours
        fraction = (earth_time.hour - 12) / 24 + earth_time.minute / 1440 + earth_time.second / 86400
        
        jd = jdn + fraction
        
        # Calculate Modified Julian Date (MJD = JD - 2400000.5)
        mjd = jd - self._julian_data["mjd_offset"]
        
        # Calculate time since J2000.0 epoch
        j2000_offset = jd - self._julian_data["j2000_jd"]
        julian_centuries = j2000_offset / self._julian_data["julian_century"]
        
        # Format fraction as time if requested
        fraction_time = ""
        if self._show_fraction_as_time:
            # Convert fraction to hours, minutes, seconds
            total_seconds = abs(fraction) * 86400
            hours = int(total_seconds // 3600)
            minutes = int((total_seconds % 3600) // 60)
            seconds = int(total_seconds % 60)
            fraction_time = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
        # Determine which epoch we're closest to
        closest_epoch = "Custom"
        min_diff = float('inf')
        for epoch_name, epoch_jd in self._julian_data["epochs"].items():
            diff = abs(jd - epoch_jd)
            if diff < min_diff:
                min_diff = diff
                closest_epoch = epoch_name
        
        # Format with configurable decimal places
        jd_formatted = f"{jd:.{self._decimal_places}f}"
        mjd_formatted = f"{mjd:.{self._decimal_places}f}"
        
        result = {
            "jd": jd,
            "jd_formatted": jd_formatted,
            "jdn": jdn,
            "fraction": round(fraction, self._decimal_places),
            "mjd": mjd,
            "mjd_formatted": mjd_formatted,
            "j2000_offset_days": round(j2000_offset, 2),
            "julian_centuries": round(julian_centuries, 4),
            "closest_epoch": closest_epoch,
            "unix_days": round(jd - self._julian_data["unix_epoch_jd"], 2),
            "gregorian_date": earth_time.strftime("%Y-%m-%d %H:%M:%S UTC"),
            "full_display": jd_formatted
        }
        
        if self._show_mjd:
            result["full_display"] = f"JD {jd_formatted} (MJD {mjd_formatted})"
        
        if fraction_time:
            result["fraction_as_time"] = fraction_time
            result["full_display"] += f" [{fraction_time}]"
        
        return result
    
    def update(self) -> None:
        """Update the sensor."""
        now = datetime.now()
        self._julian_date_info = self._calculate_julian_date(now)
        
        # Set state to formatted Julian Date
        self._state = self._julian_date_info["jd_formatted"]
        
        _LOGGER.debug(f"Updated Julian Date to {self._state}")