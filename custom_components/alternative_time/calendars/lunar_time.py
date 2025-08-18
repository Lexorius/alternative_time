"""ESA Lunar Time Calendar implementation - Version 2.5."""
from __future__ import annotations

from datetime import datetime, timezone
import logging
import math
from typing import Dict, Any

from homeassistant.core import HomeAssistant
from ..sensor import AlternativeTimeSensorBase

_LOGGER = logging.getLogger(__name__)

# ============================================
# CALENDAR METADATA
# ============================================

# Update interval in seconds (60 seconds for lunar time)
UPDATE_INTERVAL = 1

# Complete calendar information for auto-discovery
CALENDAR_INFO = {
    "id": "lunar_time",
    "version": "2.5.0",
    "icon": "mdi:moon-waxing-crescent",
    "category": "space",
    "accuracy": "scientific",
    "update_interval": UPDATE_INTERVAL,
    
    # Multi-language names
    "name": {
        "en": "ESA Lunar Time",
        "de": "ESA Mondzeit",
        "es": "Hora Lunar ESA",
        "fr": "Temps Lunaire ESA",
        "it": "Ora Lunare ESA",
        "nl": "ESA Maantijd",
        "pt": "Hora Lunar ESA",
        "ru": "Лунное время ESA",
        "ja": "ESA月時間",
        "zh": "ESA月球时间",
        "ko": "ESA 달 시간"
    },
    
    # Short descriptions for UI
    "description": {
        "en": "Coordinated Lunar Time (LTC) proposed by ESA for Moon missions",
        "de": "Koordinierte Mondzeit (LTC) von der ESA für Mondmissionen vorgeschlagen",
        "es": "Tiempo Lunar Coordinado (LTC) propuesto por la ESA para misiones lunares",
        "fr": "Temps Lunaire Coordonné (LTC) proposé par l'ESA pour les missions lunaires",
        "it": "Tempo Lunare Coordinato (LTC) proposto dall'ESA per le missioni lunari",
        "nl": "Gecoördineerde Maantijd (LTC) voorgesteld door ESA voor maanmissies",
        "pt": "Tempo Lunar Coordenado (LTC) proposto pela ESA para missões lunares",
        "ru": "Координированное лунное время (LTC), предложенное ESA для лунных миссий",
        "ja": "ESAが月面ミッションのために提案した協定月時間（LTC）",
        "zh": "ESA为月球任务提出的协调月球时间（LTC）",
        "ko": "ESA가 달 임무를 위해 제안한 협정 달 시간(LTC)"
    },
    
    # Detailed information for documentation
    "detailed_info": {
        "en": {
            "overview": "The European Space Agency proposed a unified lunar time system for future Moon missions",
            "time_dilation": "Due to lower gravity, clocks on the Moon run ~56 microseconds faster per Earth day",
            "lunar_day": "One lunar day equals 29.53 Earth days (synodic month)",
            "zones": "Proposed lunar time zones based on 15-degree longitude increments",
            "reference": "LTC-0 at 0° longitude (center of near side)",
            "purpose": "Essential for navigation, communication, and coordination of lunar activities",
            "artemis": "Will be implemented for Artemis and other international lunar programs",
            "relativity": "Accounts for gravitational time dilation effects"
        },
        "de": {
            "overview": "Die Europäische Weltraumorganisation schlug ein einheitliches Mondzeitsystem für zukünftige Mondmissionen vor",
            "time_dilation": "Aufgrund der geringeren Schwerkraft laufen Uhren auf dem Mond ~56 Mikrosekunden pro Erdtag schneller",
            "lunar_day": "Ein Mondtag entspricht 29,53 Erdtagen (synodischer Monat)",
            "zones": "Vorgeschlagene Mondzeitzonen basierend auf 15-Grad-Längengrad-Schritten",
            "reference": "LTC-0 bei 0° Länge (Zentrum der erdzugewandten Seite)",
            "purpose": "Wesentlich für Navigation, Kommunikation und Koordination von Mondaktivitäten",
            "artemis": "Wird für Artemis und andere internationale Mondprogramme implementiert",
            "relativity": "Berücksichtigt gravitative Zeitdilatationseffekte"
        }
    },
    
    # Lunar time specific data
    "lunar_data": {
        # Time dilation factor (microseconds per Earth day)
        "time_dilation_us_per_day": 56,
        
        # Lunar day length in Earth seconds
        "lunar_day_seconds": 2551442.8,  # 29.53 days
        
        # Lunar time zones (15-degree increments)
        "timezones": {
            "LTC-12": {"offset": -12, "longitude": -180, "name": "Far Side West"},
            "LTC-11": {"offset": -11, "longitude": -165, "name": "Far West"},
            "LTC-10": {"offset": -10, "longitude": -150, "name": "West Far"},
            "LTC-9": {"offset": -9, "longitude": -135, "name": "Far Northwest"},
            "LTC-8": {"offset": -8, "longitude": -120, "name": "Northwest Far"},
            "LTC-7": {"offset": -7, "longitude": -105, "name": "Northwest"},
            "LTC-6": {"offset": -6, "longitude": -90, "name": "West Limb"},
            "LTC-5": {"offset": -5, "longitude": -75, "name": "West Northwest"},
            "LTC-4": {"offset": -4, "longitude": -60, "name": "Northwest Near"},
            "LTC-3": {"offset": -3, "longitude": -45, "name": "Near Northwest"},
            "LTC-2": {"offset": -2, "longitude": -30, "name": "West Near"},
            "LTC-1": {"offset": -1, "longitude": -15, "name": "Near West"},
            "LTC": {"offset": 0, "longitude": 0, "name": "Prime Meridian"},
            "LTC+1": {"offset": 1, "longitude": 15, "name": "Near East"},
            "LTC+2": {"offset": 2, "longitude": 30, "name": "East Near"},
            "LTC+3": {"offset": 3, "longitude": 45, "name": "Near Southeast"},
            "LTC+4": {"offset": 4, "longitude": 60, "name": "Southeast Near"},
            "LTC+5": {"offset": 5, "longitude": 75, "name": "East Southeast"},
            "LTC+6": {"offset": 6, "longitude": 90, "name": "East Limb"},
            "LTC+7": {"offset": 7, "longitude": 105, "name": "Southeast"},
            "LTC+8": {"offset": 8, "longitude": 120, "name": "Southeast Far"},
            "LTC+9": {"offset": 9, "longitude": 135, "name": "Far Southeast"},
            "LTC+10": {"offset": 10, "longitude": 150, "name": "East Far"},
            "LTC+11": {"offset": 11, "longitude": 165, "name": "Far East"},
            "LTC+12": {"offset": 12, "longitude": 180, "name": "Far Side East"}
        },
        
        # Lunar landmarks and bases
        "landmarks": {
            "Apollo 11": {"lat": 0.67, "lon": 23.47, "timezone": "LTC+2"},
            "Apollo 17": {"lat": 20.19, "lon": 30.77, "timezone": "LTC+2"},
            "Chang'e 4": {"lat": -45.5, "lon": 177.6, "timezone": "LTC+12"},
            "Artemis Base Camp": {"lat": -89.9, "lon": 0, "timezone": "LTC"},
            "Shackleton Crater": {"lat": -89.9, "lon": 0, "timezone": "LTC"},
            "Tycho Crater": {"lat": -43.3, "lon": -11.2, "timezone": "LTC-1"},
            "Mare Tranquillitatis": {"lat": 8.5, "lon": 31.4, "timezone": "LTC+2"},
            "Mare Imbrium": {"lat": 32.8, "lon": -15.6, "timezone": "LTC-1"}
        },
        
        # Lunar phases for reference
        "phases": [
            {"name": "New Moon", "emoji": "🌑", "illumination": 0},
            {"name": "Waxing Crescent", "emoji": "🌒", "illumination": 0.25},
            {"name": "First Quarter", "emoji": "🌓", "illumination": 0.5},
            {"name": "Waxing Gibbous", "emoji": "🌔", "illumination": 0.75},
            {"name": "Full Moon", "emoji": "🌕", "illumination": 1.0},
            {"name": "Waning Gibbous", "emoji": "🌖", "illumination": 0.75},
            {"name": "Last Quarter", "emoji": "🌗", "illumination": 0.5},
            {"name": "Waning Crescent", "emoji": "🌘", "illumination": 0.25}
        ],
        
        # ESA Lunar Time epoch (proposed start date)
        "epoch": {
            "earth_date": "2025-01-01T00:00:00Z",
            "description": "Proposed LTC epoch start"
        },
        
        # Lunar calendar months (for reference)
        "lunar_months": [
            "Lunarius", "Cynthius", "Selenius", "Artemius",
            "Dianius", "Phoebius", "Hecatius", "Mensius",
            "Noctius", "Crescentius", "Gibbosius", "Plenius"
        ]
    },
    
    # Additional metadata
    "reference_url": "https://www.esa.int/Applications/Navigation/Telling_time_on_the_Moon",
    "documentation_url": "https://www.esa.int/",
    "origin": "European Space Agency (ESA)",
    "created_by": "ESA Navigation Support Office",
    "introduced": "2023 (Proposed)",
    
    # Example format
    "example": "LTC 12:30:45 | LD 15 | 🌔",
    "example_meaning": "Lunar Time Coordinated 12:30:45, Lunar Day 15, Waxing Gibbous",
    
    # Related calendars
    "related": ["mars_time", "darian", "gregorian"],
    
    # Tags for searching and filtering
    "tags": [
        "space", "lunar", "moon", "esa", "scientific",
        "artemis", "future", "coordinated", "ltc"
    ],
    
    # Special features
    "features": {
        "time_dilation": True,
        "multiple_timezones": True,
        "scientific_basis": True,
        "international_standard": True,
        "precision": "microsecond"
    },
    
    # Configuration options for this calendar
    "config_options": {
        "timezone": {
            "type": "select",
            "default": "LTC",
            "options": [
                "LTC-12", "LTC-11", "LTC-10", "LTC-9", "LTC-8", "LTC-7",
                "LTC-6", "LTC-5", "LTC-4", "LTC-3", "LTC-2", "LTC-1",
                "LTC", "LTC+1", "LTC+2", "LTC+3", "LTC+4", "LTC+5",
                "LTC+6", "LTC+7", "LTC+8", "LTC+9", "LTC+10", "LTC+11", "LTC+12"
            ],
            "description": {
                "en": "Select lunar timezone",
                "de": "Mondzeitzone auswählen"
            }
        },
        "show_phase": {
            "type": "boolean",
            "default": True,
            "description": {
                "en": "Show current lunar phase",
                "de": "Aktuelle Mondphase anzeigen"
            }
        },
        "show_earth_time": {
            "type": "boolean",
            "default": True,
            "description": {
                "en": "Show corresponding Earth UTC time",
                "de": "Entsprechende Erd-UTC-Zeit anzeigen"
            }
        },
        "show_lunar_day": {
            "type": "boolean",
            "default": True,
            "description": {
                "en": "Show lunar day number",
                "de": "Mondtag-Nummer anzeigen"
            }
        },
        "show_time_dilation": {
            "type": "boolean",
            "default": False,
            "description": {
                "en": "Show time dilation effect",
                "de": "Zeitdilatationseffekt anzeigen"
            }
        }
    }
}


class LunarTimeSensor(AlternativeTimeSensorBase):
    """Sensor for displaying ESA Lunar Time."""
    
    # Class-level update interval
    UPDATE_INTERVAL = 60  # Update every minute
    
    def __init__(self, base_name: str, hass: HomeAssistant) -> None:
        """Initialize the Lunar Time sensor."""
        super().__init__(base_name, hass)
        
        # Get translated name from metadata
        calendar_name = self._translate('name', 'ESA Lunar Time')
        
        # Set sensor attributes
        self._attr_name = f"{base_name} {calendar_name}"
        self._attr_unique_id = f"{base_name}_lunar_time"
        self._attr_icon = CALENDAR_INFO.get("icon", "mdi:moon-waxing-crescent")
        
        # Get plugin options
        options = self.get_plugin_options()
        
        # Configuration options with defaults
        self._timezone = options.get("timezone", "LTC")
        self._show_phase = options.get("show_phase", True)
        self._show_earth_time = options.get("show_earth_time", True)
        self._show_lunar_day = options.get("show_lunar_day", True)
        self._show_time_dilation = options.get("show_time_dilation", False)
        
        # Lunar data
        self._lunar_data = CALENDAR_INFO["lunar_data"]
        
        _LOGGER.debug(f"Initialized Lunar Time sensor: {self._attr_name}")
    
    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes."""
        attrs = super().extra_state_attributes
        
        # Add Lunar-specific attributes
        if hasattr(self, '_lunar_time'):
            attrs.update(self._lunar_time)
            
            # Add description in user's language
            attrs["description"] = self._translate('description')
            
            # Add reference
            attrs["reference"] = CALENDAR_INFO.get('reference_url', '')
            
            # Add timezone info
            if self._timezone in self._lunar_data["timezones"]:
                tz_info = self._lunar_data["timezones"][self._timezone]
                attrs["timezone_name"] = tz_info["name"]
                attrs["timezone_longitude"] = tz_info["longitude"]
        
        return attrs
    
    def _calculate_lunar_phase(self, earth_date: datetime) -> Dict[str, Any]:
        """Calculate current lunar phase."""
        # Lunar phase calculation (simplified)
        # Using synodic month = 29.530588853 days
        
        # Reference: New Moon on Jan 6, 2000, 18:14 UTC
        reference = datetime(2000, 1, 6, 18, 14, 0, tzinfo=timezone.utc)
        
        # Calculate days since reference
        if earth_date.tzinfo is None:
            earth_date = earth_date.replace(tzinfo=timezone.utc)
        
        diff = (earth_date - reference).total_seconds() / 86400
        
        # Calculate phase (0 = new moon, 0.5 = full moon)
        synodic_month = 29.530588853
        phase = (diff % synodic_month) / synodic_month
        
        # Determine phase name and emoji
        phases = self._lunar_data["phases"]
        if phase < 0.0625:
            phase_data = phases[0]  # New Moon
        elif phase < 0.1875:
            phase_data = phases[1]  # Waxing Crescent
        elif phase < 0.3125:
            phase_data = phases[2]  # First Quarter
        elif phase < 0.4375:
            phase_data = phases[3]  # Waxing Gibbous
        elif phase < 0.5625:
            phase_data = phases[4]  # Full Moon
        elif phase < 0.6875:
            phase_data = phases[5]  # Waning Gibbous
        elif phase < 0.8125:
            phase_data = phases[6]  # Last Quarter
        elif phase < 0.9375:
            phase_data = phases[7]  # Waning Crescent
        else:
            phase_data = phases[0]  # New Moon
        
        # Calculate lunar day (1-30)
        lunar_day = int(phase * 29.53) + 1
        
        # Calculate illumination percentage
        illumination = abs(math.cos(phase * 2 * math.pi))
        
        return {
            "phase": phase,
            "phase_name": phase_data["name"],
            "phase_emoji": phase_data["emoji"],
            "lunar_day": lunar_day,
            "illumination": round(illumination * 100, 1)
        }
    
    def _calculate_lunar_time(self, earth_utc: datetime) -> Dict[str, Any]:
        """Calculate ESA Lunar Time from Earth UTC."""
        
        # Get epoch
        epoch_str = self._lunar_data["epoch"]["earth_date"]
        epoch = datetime.fromisoformat(epoch_str.replace('Z', '+00:00'))
        
        if earth_utc.tzinfo is None:
            earth_utc = earth_utc.replace(tzinfo=timezone.utc)
        
        # Calculate seconds since epoch
        seconds_since_epoch = (earth_utc - epoch).total_seconds()
        
        # Apply time dilation (Moon clocks run faster)
        # 56 microseconds per day = 56/86400000000 per second
        dilation_factor = 1 + (self._lunar_data["time_dilation_us_per_day"] / 86400000000)
        lunar_seconds = seconds_since_epoch * dilation_factor
        
        # Calculate lunar time components
        lunar_days = int(lunar_seconds // 86400)
        remaining_seconds = lunar_seconds % 86400
        
        # Get timezone offset
        tz_data = self._lunar_data["timezones"].get(self._timezone, {"offset": 0})
        offset_seconds = tz_data["offset"] * 3600
        
        # Apply timezone offset
        adjusted_seconds = remaining_seconds + offset_seconds
        
        # Handle day boundary crossing
        if adjusted_seconds >= 86400:
            adjusted_seconds -= 86400
            lunar_days += 1
        elif adjusted_seconds < 0:
            adjusted_seconds += 86400
            lunar_days -= 1
        
        # Calculate time components
        hours = int(adjusted_seconds // 3600)
        minutes = int((adjusted_seconds % 3600) // 60)
        seconds = int(adjusted_seconds % 60)
        
        # Format time
        ltc_time = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
        # Calculate lunar phase
        phase_info = self._calculate_lunar_phase(earth_utc)
        
        # Calculate which lunar month we're in
        lunar_month_index = (lunar_days // 30) % 12
        lunar_month_day = (lunar_days % 30) + 1
        lunar_month = self._lunar_data["lunar_months"][lunar_month_index]
        
        # Build result
        result = {
            "ltc_time": ltc_time,
            "lunar_days_since_epoch": lunar_days,
            "lunar_month": lunar_month,
            "lunar_month_day": lunar_month_day,
            "timezone": self._timezone,
            "timezone_offset": tz_data["offset"],
            "full_display": f"{ltc_time} {self._timezone}"
        }
        
        # Add lunar day if enabled
        if self._show_lunar_day:
            result["lunar_day"] = phase_info["lunar_day"]
            result["full_display"] += f" | LD {phase_info['lunar_day']}"
        
        # Add phase if enabled
        if self._show_phase:
            result["phase_name"] = phase_info["phase_name"]
            result["phase_emoji"] = phase_info["phase_emoji"]
            result["illumination"] = phase_info["illumination"]
            result["full_display"] += f" | {phase_info['phase_emoji']}"
        
        # Add Earth time if enabled
        if self._show_earth_time:
            result["earth_utc"] = earth_utc.strftime("%Y-%m-%d %H:%M:%S UTC")
        
        # Add time dilation if enabled
        if self._show_time_dilation:
            dilation_seconds = lunar_seconds - seconds_since_epoch
            result["time_dilation_seconds"] = round(dilation_seconds, 6)
            result["dilation_microseconds_today"] = round(dilation_seconds * 1000000, 2)
        
        # Add nearest landmark
        nearest_landmark = None
        min_distance = float('inf')
        
        for landmark, data in self._lunar_data["landmarks"].items():
            if data["timezone"] == self._timezone:
                if nearest_landmark is None:
                    nearest_landmark = landmark
                    break
        
        if nearest_landmark:
            result["nearest_landmark"] = nearest_landmark
        
        return result
    
    def update(self) -> None:
        """Update the sensor."""
        now = datetime.now(timezone.utc)
        self._lunar_time = self._calculate_lunar_time(now)
        
        # Set state to lunar time
        self._state = self._lunar_time["full_display"]
        
        _LOGGER.debug(f"Updated Lunar Time to {self._state}")