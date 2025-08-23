"""Julian Date Calendar implementation - Version 2.6."""
from __future__ import annotations

from datetime import datetime, timezone
import logging
from typing import Dict, Any

from homeassistant.core import HomeAssistant
from ..sensor import AlternativeTimeSensorBase

_LOGGER = logging.getLogger(__name__)

# ============================================
# CALENDAR METADATA
# ============================================

# Update interval in seconds (60 seconds = 1 minute for fractional day updates)
UPDATE_INTERVAL = 60

# Complete calendar information for auto-discovery
CALENDAR_INFO = {
    "id": "julian",
    "version": "2.6.0",
    "icon": "mdi:calendar-clock",
    "category": "technical",
    "accuracy": "scientific",
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
        "ja": "ユリウス日",
        "zh": "儒略日",
        "ko": "율리우스일"
    },
    
    # Short descriptions for UI
    "description": {
        "en": "Continuous day count since January 1, 4713 BCE (e.g. JD 2460000.5)",
        "de": "Fortlaufende Tageszählung seit 1. Januar 4713 v. Chr. (z.B. JD 2460000.5)",
        "es": "Recuento continuo de días desde el 1 de enero de 4713 a.C. (ej. JD 2460000.5)",
        "fr": "Comptage continu des jours depuis le 1er janvier 4713 av. J.-C. (ex. JD 2460000.5)",
        "it": "Conteggio continuo dei giorni dal 1 gennaio 4713 a.C. (es. JD 2460000.5)",
        "nl": "Continue dagtelling sinds 1 januari 4713 v.Chr. (bijv. JD 2460000.5)",
        "pt": "Contagem contínua de dias desde 1 de janeiro de 4713 a.C. (ex. JD 2460000.5)",
        "ru": "Непрерывный счет дней с 1 января 4713 г. до н.э. (напр. JD 2460000.5)",
        "ja": "紀元前4713年1月1日からの連続日数（例：JD 2460000.5）",
        "zh": "自公元前4713年1月1日起的连续天数（例：JD 2460000.5）",
        "ko": "기원전 4713년 1월 1일부터의 연속 일수 (예: JD 2460000.5)"
    },
    
    # Julian Date specific data
    "julian_data": {
        # Epoch (noon UTC on January 1, 4713 BCE in proleptic Julian calendar)
        "epoch": {
            "year": -4712,  # 4713 BCE
            "month": 1,
            "day": 1,
            "hour": 12,  # Noon UTC
            "description": "Julian Day Zero"
        },
        
        # Important Julian Dates
        "milestones": {
            0.0: "Julian Day Zero (January 1, 4713 BCE noon)",
            1721425.5: "January 1, 1 CE (Gregorian)",
            2299160.5: "October 15, 1582 (Gregorian Reform)",
            2400000.5: "November 16, 1858 (MJD Epoch)",
            2415020.5: "January 1, 1900",
            2440587.5: "January 1, 1970 (Unix Epoch)",
            2451545.0: "January 1, 2000 noon (J2000.0)",
            2460000.5: "February 23, 2023",
            2500000.5: "August 31, 2132"
        },
        
        # Related systems
        "related_systems": {
            "MJD": {
                "name": "Modified Julian Date",
                "offset": -2400000.5,
                "description": "MJD = JD - 2400000.5"
            },
            "TJD": {
                "name": "Truncated Julian Date", 
                "offset": -2440000.5,
                "description": "TJD = JD - 2440000.5"
            },
            "RJD": {
                "name": "Reduced Julian Date",
                "offset": -2400000.0,
                "description": "RJD = JD - 2400000"
            },
            "DJD": {
                "name": "Dublin Julian Date",
                "offset": -2415020.0,
                "description": "DJD = JD - 2415020 (from 1900)"
            },
            "CNES": {
                "name": "CNES Julian Date",
                "offset": -2433282.5,
                "description": "CJDN = JD - 2433282.5 (from 1950)"
            },
            "LILIAN": {
                "name": "Lilian Date",
                "offset": -2299159.5,
                "description": "Days since Oct 15, 1582"
            }
        },
        
        # Conversion formulas
        "formulas": {
            "gregorian_to_jd": "JD = 367Y - INT(7(Y + INT((M+9)/12))/4) + INT(275M/9) + D + 1721013.5 + UT/24",
            "jd_to_gregorian": "Complex algorithm - see Meeus 'Astronomical Algorithms'",
            "decimal_day": "Fractional part × 24 = hours from noon UTC"
        },
        
        # Applications
        "applications": [
            "Astronomy",
            "Chronology",
            "Computer Systems",
            "Historical Dating",
            "Ephemeris Calculations",
            "Satellite Tracking"
        ]
    },
    
    # Additional metadata
    "reference_url": "https://en.wikipedia.org/wiki/Julian_day",
    "documentation_url": "https://aa.usno.navy.mil/data/JulianDate",
    "origin": "Joseph Justus Scaliger (1583)",
    "created_by": "Joseph Justus Scaliger",
    "introduced": "1583",
    
    # Example format
    "example": "JD 2460000.500000",
    "example_meaning": "February 23, 2023 at noon UTC",
    
    # Related calendars
    "related": ["gregorian", "unix", "iso8601"],
    
    # Tags for searching and filtering
    "tags": [
        "technical", "julian", "astronomy", "scientific", "continuous",
        "chronology", "ephemeris", "scaliger", "mjd", "tjd"
    ],
    
    # Special features
    "features": {
        "continuous_count": True,
        "fractional_days": True,
        "timezone_independent": True,
        "negative_dates": True,
        "precision": "microsecond",
        "scientific_standard": True
    },
    
    # Configuration options for this calendar
    "config_options": {
        "show_mjd": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show Modified Julian Date",
                "de": "Modifiziertes Julianisches Datum anzeigen",
                "es": "Mostrar Fecha Juliana Modificada",
                "fr": "Afficher la Date Julienne Modifiée",
                "it": "Mostra Data Giuliana Modificata",
                "nl": "Toon Gemodificeerde Juliaanse Datum",
                "pt": "Mostrar Data Juliana Modificada",
                "ru": "Показать модифицированную юлианскую дату",
                "ja": "修正ユリウス日を表示",
                "zh": "显示修正儒略日",
                "ko": "수정 율리우스일 표시"
            },
            "description": {
                "en": "Also display Modified Julian Date (MJD = JD - 2400000.5)",
                "de": "Zeige auch das Modifizierte Julianische Datum (MJD = JD - 2400000.5)"
            }
        },
        "decimal_places": {
            "type": "integer",
            "default": 6,
            "min": 0,
            "max": 10,
            "label": {
                "en": "Decimal Places",
                "de": "Dezimalstellen",
                "es": "Lugares decimales",
                "fr": "Décimales",
                "it": "Cifre decimali",
                "nl": "Decimalen",
                "pt": "Casas decimais",
                "ru": "Десятичные знаки",
                "ja": "小数点以下の桁数",
                "zh": "小数位数",
                "ko": "소수점 자리"
            },
            "description": {
                "en": "Number of decimal places to display (0-10)",
                "de": "Anzahl der anzuzeigenden Dezimalstellen (0-10)"
            }
        },
        "show_fraction_as_time": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show Fraction as Time",
                "de": "Bruch als Zeit anzeigen",
                "es": "Mostrar fracción como hora",
                "fr": "Afficher la fraction comme heure",
                "it": "Mostra frazione come ora",
                "nl": "Toon fractie als tijd",
                "pt": "Mostrar fração como hora",
                "ru": "Показать дробь как время",
                "ja": "小数部を時刻として表示",
                "zh": "将小数显示为时间",
                "ko": "분수를 시간으로 표시"
            },
            "description": {
                "en": "Convert fractional day to hours:minutes:seconds",
                "de": "Konvertiere Tagesbruchteile in Stunden:Minuten:Sekunden"
            }
        },
        "show_other_systems": {
            "type": "boolean",
            "default": False,
            "label": {
                "en": "Show Other Julian Systems",
                "de": "Andere Julianische Systeme anzeigen",
                "es": "Mostrar otros sistemas julianos",
                "fr": "Afficher d'autres systèmes juliens",
                "it": "Mostra altri sistemi giuliani",
                "nl": "Toon andere Juliaanse systemen",
                "pt": "Mostrar outros sistemas julianos",
                "ru": "Показать другие юлианские системы",
                "ja": "他のユリウス系を表示",
                "zh": "显示其他儒略系统",
                "ko": "다른 율리우스 시스템 표시"
            },
            "description": {
                "en": "Display TJD, RJD, and other Julian date variants",
                "de": "Zeige TJD, RJD und andere Julianische Datumsvarianten"
            }
        }
    }
}


class JulianDateSensor(AlternativeTimeSensorBase):
    """Sensor for displaying Julian Date."""
    
    # Class-level update interval
    UPDATE_INTERVAL = UPDATE_INTERVAL
    
    def __init__(self, base_name: str, hass: HomeAssistant) -> None:
        """Initialize the Julian Date sensor."""
        super().__init__(base_name, hass)
        
        # Get translated name from metadata
        calendar_name = self._translate('name', 'Julian Date')
        
        # Set sensor attributes
        self._attr_name = f"{base_name} {calendar_name}"
        self._attr_unique_id = f"{base_name}_julian_date"
        self._attr_icon = CALENDAR_INFO.get("icon", "mdi:calendar-clock")
        
        # Configuration options with defaults from CALENDAR_INFO
        config_defaults = CALENDAR_INFO.get("config_options", {})
        self._show_mjd = config_defaults.get("show_mjd", {}).get("default", True)
        self._decimal_places = config_defaults.get("decimal_places", {}).get("default", 6)
        self._show_fraction_as_time = config_defaults.get("show_fraction_as_time", {}).get("default", True)
        self._show_other_systems = config_defaults.get("show_other_systems", {}).get("default", False)
        
        # Julian data
        self._julian_data = CALENDAR_INFO["julian_data"]
        
        # Flag to track if options have been loaded
        self._options_loaded = False
        
        # Initialize state
        self._state = None
        self._julian_date_info = {}
        
        _LOGGER.debug(f"Initialized Julian Date sensor: {self._attr_name}")
    
    def _load_options(self) -> None:
        """Load plugin options after IDs are set."""
        if self._options_loaded:
            return
            
        try:
            options = self.get_plugin_options()
            if options:
                # Update configuration from plugin options
                self._show_mjd = options.get("show_mjd", self._show_mjd)
                self._decimal_places = options.get("decimal_places", self._decimal_places)
                self._show_fraction_as_time = options.get("show_fraction_as_time", self._show_fraction_as_time)
                self._show_other_systems = options.get("show_other_systems", self._show_other_systems)
                
                # Ensure decimal_places is within valid range
                self._decimal_places = max(0, min(10, int(self._decimal_places)))
                
                _LOGGER.debug(f"Julian sensor loaded options: show_mjd={self._show_mjd}, "
                            f"decimal_places={self._decimal_places}, "
                            f"show_fraction_as_time={self._show_fraction_as_time}")
            else:
                _LOGGER.debug("Julian sensor using default options - no custom options found")
                
            self._options_loaded = True
        except Exception as e:
            _LOGGER.debug(f"Julian sensor could not load options yet: {e}")
    
    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        await super().async_added_to_hass()
        
        # Try to load options now that IDs should be set
        self._load_options()
    
    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes."""
        attrs = super().extra_state_attributes
        
        # Add Julian Date-specific attributes
        if self._julian_date_info:
            attrs.update(self._julian_date_info)
            
            # Add description in user's language
            attrs["description"] = self._translate('description')
            
            # Add reference
            attrs["reference"] = CALENDAR_INFO.get('reference_url', '')
            
            # Add current settings
            attrs["decimal_places_setting"] = self._decimal_places
            attrs["show_fraction_as_time_setting"] = self._show_fraction_as_time
        
        return attrs
    
    def _gregorian_to_julian_date(self, date: datetime) -> float:
        """Convert Gregorian date to Julian Date."""
        # Ensure we're working with UTC
        if date.tzinfo is None:
            date = date.replace(tzinfo=timezone.utc)
        else:
            date = date.astimezone(timezone.utc)
        
        # Extract components
        year = date.year
        month = date.month
        day = date.day
        hour = date.hour
        minute = date.minute
        second = date.second
        microsecond = date.microsecond
        
        # Calculate fractional day from noon UTC
        # Julian Date starts at noon, so we need to adjust
        fractional_day = (hour - 12) / 24.0 + minute / 1440.0 + second / 86400.0 + microsecond / 86400000000.0
        
        # Algorithm from Meeus, "Astronomical Algorithms"
        if month <= 2:
            year -= 1
            month += 12
        
        # Check if date is after Gregorian reform (October 15, 1582)
        gregorian = (year > 1582) or (year == 1582 and month > 10) or (year == 1582 and month == 10 and day >= 15)
        
        if gregorian:
            a = int(year / 100)
            b = 2 - a + int(a / 4)
        else:
            b = 0
        
        jd = int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + b - 1524.5
        jd += fractional_day
        
        return jd
    
    def _fraction_to_time(self, fraction: float) -> str:
        """Convert fractional day to time string."""
        # Fractional part represents time from noon UTC
        # 0.0 = noon, 0.5 = midnight, 1.0 = next noon
        
        # Convert to hours from midnight
        hours_from_noon = fraction * 24
        hours_from_midnight = (hours_from_noon + 12) % 24
        
        hours = int(hours_from_midnight)
        remainder = hours_from_midnight - hours
        
        minutes = int(remainder * 60)
        remainder = (remainder * 60) - minutes
        
        seconds = int(remainder * 60)
        
        return f"{hours:02d}:{minutes:02d}:{seconds:02d} UTC"
    
    def _find_nearest_milestone(self, jd: float) -> tuple:
        """Find the nearest milestone Julian Date."""
        milestones = self._julian_data["milestones"]
        
        nearest_jd = None
        nearest_desc = None
        min_diff = float('inf')
        
        for milestone_jd, description in milestones.items():
            diff = abs(jd - milestone_jd)
            if diff < min_diff:
                min_diff = diff
                nearest_jd = milestone_jd
                nearest_desc = description
        
        return (nearest_jd, nearest_desc, jd - nearest_jd)
    
    def _calculate_julian_date(self, earth_date: datetime) -> Dict[str, Any]:
        """Calculate Julian Date and related information."""
        
        # Calculate Julian Date
        jd = self._gregorian_to_julian_date(earth_date)
        
        # Format JD with specified decimal places
        jd_formatted = f"JD {jd:.{self._decimal_places}f}"
        
        # Get integer and fractional parts
        jd_integer = int(jd)
        jd_fraction = jd - jd_integer
        
        result = {
            "julian_date": jd,
            "julian_date_integer": jd_integer,
            "julian_date_fraction": jd_fraction,
            "formatted": jd_formatted,
            "gregorian_date": earth_date.strftime("%Y-%m-%d %H:%M:%S UTC")
        }
        
        # Add Modified Julian Date if configured
        if self._show_mjd:
            mjd = jd - 2400000.5
            result["modified_julian_date"] = mjd
            result["mjd_formatted"] = f"MJD {mjd:.{self._decimal_places}f}"
        
        # Convert fraction to time if configured
        if self._show_fraction_as_time:
            time_str = self._fraction_to_time(jd_fraction)
            result["fraction_as_time"] = time_str
            result["time_from_noon_utc"] = f"{(jd_fraction * 24):.4f} hours"
        
        # Add other Julian systems if configured
        if self._show_other_systems:
            systems = {}
            for sys_id, sys_info in self._julian_data["related_systems"].items():
                sys_value = jd + sys_info["offset"]
                systems[sys_id] = {
                    "value": sys_value,
                    "formatted": f"{sys_value:.{min(self._decimal_places, 2)}f}",
                    "name": sys_info["name"],
                    "formula": sys_info["description"]
                }
            result["other_systems"] = systems
        
        # Find nearest milestone
        nearest_jd, nearest_desc, diff_days = self._find_nearest_milestone(jd)
        result["nearest_milestone"] = nearest_desc
        result["days_from_milestone"] = f"{diff_days:+.1f} days"
        
        # Calculate century and millennium
        j2000_jd = 2451545.0  # J2000.0 epoch
        days_from_j2000 = jd - j2000_jd
        julian_century = days_from_j2000 / 36525.0  # Julian century = 36525 days
        julian_millennium = julian_century / 10.0
        
        result["julian_century"] = f"T{julian_century:+.8f}"
        result["julian_millennium"] = f"{julian_millennium:+.8f}"
        
        # Add day of week (0 = Monday, following ISO)
        # JD 0.0 was a Monday (January 1, 4713 BCE noon)
        day_of_week = int((jd + 0.5)) % 7
        weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        result["day_of_week"] = weekdays[day_of_week]
        
        # Add Julian Day Number (integer part at noon)
        jdn = int(jd + 0.5)
        result["julian_day_number"] = jdn
        
        return result
    
    def update(self) -> None:
        """Update the sensor."""
        # Ensure options are loaded (in case async_added_to_hass hasn't run yet)
        if not self._options_loaded:
            self._load_options()
        
        now = datetime.now(timezone.utc)
        self._julian_date_info = self._calculate_julian_date(now)
        
        # Set state to formatted Julian Date
        self._state = self._julian_date_info["formatted"]
        
        _LOGGER.debug(f"Updated Julian Date to {self._state}")
