"""Star Trek Stardate implementation - Version 2.5."""
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

# Update interval in seconds (10 seconds for stardate precision)
UPDATE_INTERVAL = 10

# Complete calendar information for auto-discovery
CALENDAR_INFO = {
    "id": "stardate",
    "version": "2.5.0",
    "icon": "mdi:star-four-points",
    "category": "scifi",
    "accuracy": "fictional",
    "update_interval": UPDATE_INTERVAL,
    
    # Multi-language names
    "name": {
        "en": "Star Trek Stardate",
        "de": "Star Trek Sternzeit",
        "es": "Fecha Estelar Star Trek",
        "fr": "Date Stellaire Star Trek",
        "it": "Data Stellare Star Trek",
        "nl": "Star Trek Sterrendatum",
        "pt": "Data Estelar Star Trek",
        "ru": "Звездная дата Star Trek",
        "ja": "スタートレック宇宙暦",
        "zh": "星际迷航星历",
        "ko": "스타트렉 우주력"
    },
    
    # Short descriptions for UI
    "description": {
        "en": "Star Trek TNG stardate (e.g. 47634.44). Based on the year 2323",
        "de": "Star Trek TNG Sternzeit (z.B. 47634.44). Basiert auf dem Jahr 2323",
        "es": "Fecha estelar de Star Trek TNG (ej. 47634.44). Basado en el año 2323",
        "fr": "Date stellaire Star Trek TNG (ex. 47634.44). Basé sur l'année 2323",
        "it": "Data stellare Star Trek TNG (es. 47634.44). Basato sull'anno 2323"
    },
    
    # Detailed information for documentation
    "detailed_info": {
        "en": {
            "overview": "Stardates are the standard time measurement in Star Trek",
            "tng_format": "TNG format: [Century][Year].[Day fraction]",
            "calculation": "1000 units per Earth year, starting from 2323",
            "precision": "Decimal places indicate time of day",
            "series": "Different series use different stardate systems",
            "tos": "TOS: Arbitrary 4-digit numbers",
            "tng": "TNG/DS9/VOY: Systematic 5-digit system",
            "discovery": "DIS: 4-digit year-based system"
        },
        "de": {
            "overview": "Sternzeiten sind die Standard-Zeitmessung in Star Trek",
            "tng_format": "TNG-Format: [Jahrhundert][Jahr].[Tagesbruchteil]",
            "calculation": "1000 Einheiten pro Erdjahr, beginnend ab 2323",
            "precision": "Dezimalstellen zeigen die Tageszeit an",
            "series": "Verschiedene Serien verwenden verschiedene Sternzeitsysteme",
            "tos": "TOS: Willkürliche 4-stellige Zahlen",
            "tng": "TNG/DS9/VOY: Systematisches 5-stelliges System",
            "discovery": "DIS: 4-stelliges jahresbasiertes System"
        }
    },
    
    # Stardate-specific data
    "stardate_data": {
        "base_year": 2323,
        "units_per_year": 1000,
        "units_per_day": 2.73785,  # 1000/365.25
        
        # Notable stardates
        "notable_events": {
            41153.7: "Encounter at Farpoint (TNG pilot)",
            41986.0: "The Best of Both Worlds Part 1",
            44001.4: "The Best of Both Worlds Part 2",
            45854.2: "Inner Light",
            47457.1: "All Good Things... (TNG finale)",
            48315.6: "Caretaker (VOY pilot)",
            49827.5: "Scorpion Part 1",
            51721.3: "Way of the Warrior (DS9)",
            52861.3: "What You Leave Behind (DS9 finale)",
            54868.6: "Endgame (VOY finale)",
            56844.9: "Star Trek (2009 film)",
            57436.2: "Star Trek Into Darkness",
            59796.7: "Star Trek Beyond"
        },
        
        # Starfleet ships
        "ships": {
            "NCC-1701": "USS Enterprise (TOS)",
            "NCC-1701-A": "USS Enterprise-A",
            "NCC-1701-B": "USS Enterprise-B",
            "NCC-1701-C": "USS Enterprise-C",
            "NCC-1701-D": "USS Enterprise-D (TNG)",
            "NCC-1701-E": "USS Enterprise-E",
            "NCC-74205": "USS Defiant (DS9)",
            "NCC-74656": "USS Voyager"
        },
        
        # Quadrants
        "quadrants": ["Alpha", "Beta", "Gamma", "Delta"],
        
        # Major powers
        "powers": [
            "United Federation of Planets",
            "Klingon Empire",
            "Romulan Star Empire",
            "Cardassian Union",
            "Dominion",
            "Borg Collective"
        ]
    },
    
    # Additional metadata
    "reference_url": "https://en.wikipedia.org/wiki/Stardate",
    "documentation_url": "https://memory-alpha.fandom.com/wiki/Stardate",
    "origin": "Star Trek (Gene Roddenberry)",
    "created_by": "Gene Roddenberry",
    "introduced": "Star Trek: The Original Series (1966)",
    
    # Example format
    "example": "47634.44",
    "example_meaning": "Year 47 of the 24th century, day 634.44",
    
    # Related calendars
    "related": ["gregorian", "julian", "scifi"],
    
    # Tags for searching and filtering
    "tags": [
        "scifi", "star_trek", "stardate", "starfleet", "federation",
        "tng", "voyager", "ds9", "enterprise", "space"
    ],
    
    # Special features
    "features": {
        "decimal_time": True,
        "fictional_future": True,
        "series_variations": True,
        "precision": "fractional_day"
    },
    
    # Configuration options
    "config_options": {
        "format": {
            "type": "select",
            "default": "tng",
            "options": ["tng", "tos", "discovery"],
            "description": {
                "en": "Stardate format (TNG/TOS/Discovery)",
                "de": "Sternzeit-Format (TNG/TOS/Discovery)"
            }
        },
        "show_event": {
            "type": "boolean",
            "default": True,
            "description": {
                "en": "Show notable Star Trek events",
                "de": "Bemerkenswerte Star Trek Ereignisse anzeigen"
            }
        },
        "precision": {
            "type": "select",
            "default": 2,
            "options": [0, 1, 2, 3],
            "description": {
                "en": "Decimal precision",
                "de": "Dezimalgenauigkeit"
            }
        }
    }
}


class StardateSensor(AlternativeTimeSensorBase):
    """Sensor for displaying Stardate (Star Trek style)."""
    
    # Class-level update interval
    UPDATE_INTERVAL = 10  # Update every 10 seconds
    
    def __init__(self, base_name: str, hass: HomeAssistant) -> None:
        """Initialize the stardate sensor."""
        super().__init__(base_name, hass)
        
        # Get translated name from metadata
        calendar_name = self._translate('name', 'Star Trek Stardate')
        
        # Set sensor attributes
        self._attr_name = f"{base_name} {calendar_name}"
        self._attr_unique_id = f"{base_name}_stardate"
        self._attr_icon = CALENDAR_INFO.get("icon", "mdi:star-four-points")
        
        # Configuration options
        self._format = "tng"
        self._show_event = True
        self._precision = 2
        
        # Stardate data
        self._stardate_data = CALENDAR_INFO["stardate_data"]
        
        _LOGGER.debug(f"Initialized Stardate sensor: {self._attr_name}")
    
    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes."""
        attrs = super().extra_state_attributes
        
        # Add Stardate-specific attributes
        if hasattr(self, '_stardate'):
            attrs.update(self._stardate)
            
            # Add description in user's language
            attrs["description"] = self._translate('description')
            
            # Add reference
            attrs["reference"] = CALENDAR_INFO.get('reference_url', '')
        
        return attrs
    
    def _calculate_tng_stardate(self, earth_date: datetime) -> float:
        """Calculate TNG-style stardate."""
        base_year = self._stardate_data["base_year"]
        current_year = earth_date.year
        day_of_year = earth_date.timetuple().tm_yday
        
        # Calculate stardate
        stardate = 1000 * (current_year - base_year)
        stardate += (1000 * day_of_year / 365.25)
        
        # Add time of day as fraction
        time_fraction = (earth_date.hour * 60 + earth_date.minute) / 1440 * 10
        stardate += time_fraction
        
        return stardate
    
    def _calculate_tos_stardate(self, earth_date: datetime) -> float:
        """Calculate TOS-style stardate (simplified)."""
        # TOS stardates were somewhat arbitrary
        # We'll use a simplified version
        base = 1312.4  # Starting point
        days_since_2000 = (earth_date - datetime(2000, 1, 1)).days
        return base + (days_since_2000 * 0.5)
    
    def _calculate_discovery_stardate(self, earth_date: datetime) -> float:
        """Calculate Discovery-style stardate."""
        # Discovery uses year.day format
        year = earth_date.year
        day_of_year = earth_date.timetuple().tm_yday
        return year + (day_of_year / 365.25)
    
    def _find_notable_event(self, stardate: float) -> str:
        """Find notable event near this stardate."""
        if not self._show_event:
            return ""
        
        closest_event = None
        min_diff = float('inf')
        
        for event_stardate, event in self._stardate_data["notable_events"].items():
            diff = abs(stardate - event_stardate)
            if diff < 100 and diff < min_diff:  # Within 100 units
                min_diff = diff
                closest_event = event
        
        return closest_event or ""
    
    def _calculate_stardate(self, earth_date: datetime) -> Dict[str, Any]:
        """Calculate Stardate from Earth date."""
        
        # Calculate based on format
        if self._format == "tos":
            stardate = self._calculate_tos_stardate(earth_date)
            era = "TOS Era"
        elif self._format == "discovery":
            stardate = self._calculate_discovery_stardate(earth_date)
            era = "Discovery Era"
        else:  # tng
            stardate = self._calculate_tng_stardate(earth_date)
            era = "TNG Era"
        
        # Format with precision
        formatted = f"{stardate:.{self._precision}f}"
        
        # Determine century
        if stardate < 10000:
            century = "23rd Century"
        elif stardate < 50000:
            century = "24th Century"
        else:
            century = "25th Century"
        
        # Calculate quadrant (simplified)
        quadrant_index = int((earth_date.hour / 6)) % 4
        current_quadrant = self._stardate_data["quadrants"][quadrant_index]
        
        # Get notable event
        event = self._find_notable_event(stardate) if self._format == "tng" else ""
        
        result = {
            "stardate": stardate,
            "formatted": formatted,
            "era": era,
            "century": century,
            "quadrant": f"{current_quadrant} Quadrant",
            "earth_date": earth_date.strftime("%Y-%m-%d %H:%M:%S"),
            "year_component": int(stardate // 1000),
            "day_component": stardate % 1000,
            "full_display": formatted
        }
        
        if event:
            result["notable_event"] = event
            result["full_display"] += f" | {event}"
        
        return result
    
    def update(self) -> None:
        """Update the sensor."""
        now = datetime.now()
        self._stardate = self._calculate_stardate(now)
        
        # Set state to formatted stardate
        self._state = self._stardate["formatted"]
        
        _LOGGER.debug(f"Updated Stardate to {self._state}")