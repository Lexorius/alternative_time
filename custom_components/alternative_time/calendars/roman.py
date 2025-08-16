"""Roman Calendar implementation - Version 2.5."""
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

# Update interval in seconds (3600 seconds = 1 hour)
UPDATE_INTERVAL = 3600

# Complete calendar information for auto-discovery
CALENDAR_INFO = {
    "id": "roman",
    "version": "2.5.0",
    "icon": "mdi:pillar",
    "category": "historical",
    "accuracy": "historical",
    "update_interval": UPDATE_INTERVAL,
    
    # Multi-language names
    "name": {
        "en": "Roman Calendar",
        "de": "Römischer Kalender",
        "es": "Calendario Romano",
        "fr": "Calendrier Romain",
        "it": "Calendario Romano",
        "nl": "Romeinse Kalender",
        "pt": "Calendário Romano",
        "ru": "Римский календарь",
        "ja": "ローマ暦",
        "zh": "罗马历",
        "ko": "로마 달력",
        "la": "Calendarium Romanum"
    },
    
    # Short descriptions for UI
    "description": {
        "en": "Ancient Roman calendar with Kalends, Nones, and Ides (e.g. AUC 2777, ante diem III Kalendas)",
        "de": "Antiker römischer Kalender mit Kalenden, Nonen und Iden (z.B. AUC 2777, ante diem III Kalendas)",
        "es": "Calendario romano antiguo con Calendas, Nonas e Idus",
        "fr": "Calendrier romain antique avec Calendes, Nones et Ides",
        "it": "Calendario romano antico con Calende, None e Idi",
        "la": "Calendarium antiquum cum Kalendis, Nonis et Idibus"
    },
    
    # Detailed information for documentation
    "detailed_info": {
        "en": {
            "overview": "The Roman calendar evolved from lunar to solar, with Julius Caesar's reform in 46 BCE",
            "structure": "Months divided by Kalends (1st), Nones (5th/7th), and Ides (13th/15th)",
            "counting": "Days counted backwards from these fixed points, inclusively",
            "auc": "Years counted 'Ab Urbe Condita' (from founding of Rome, 753 BCE)",
            "nundinae": "8-day market week cycle, labeled A through H",
            "hours": "12 day hours and 12 night hours of varying length",
            "fasti": "Calendar of lucky (fastus) and unlucky (nefastus) days"
        },
        "de": {
            "overview": "Der römische Kalender entwickelte sich vom Mond- zum Sonnenkalender, mit Julius Caesars Reform 46 v.Chr.",
            "structure": "Monate unterteilt durch Kalenden (1.), Nonen (5./7.) und Iden (13./15.)",
            "counting": "Tage wurden rückwärts von diesen Fixpunkten gezählt, inklusiv",
            "auc": "Jahre gezählt 'Ab Urbe Condita' (seit Gründung Roms, 753 v.Chr.)",
            "nundinae": "8-tägiger Marktwochen-Zyklus, bezeichnet A bis H",
            "hours": "12 Tagesstunden und 12 Nachtstunden von variabler Länge",
            "fasti": "Kalender der glücklichen (fastus) und unglücklichen (nefastus) Tage"
        }
    },
    
    # Roman-specific data
    "roman_data": {
        # Roman months
        "months": [
            {"latin": "Ianuarius", "english": "January", "days": 31, "nones": 5, "ides": 13},
            {"latin": "Februarius", "english": "February", "days": 28, "nones": 5, "ides": 13},
            {"latin": "Martius", "english": "March", "days": 31, "nones": 7, "ides": 15},
            {"latin": "Aprilis", "english": "April", "days": 30, "nones": 5, "ides": 13},
            {"latin": "Maius", "english": "May", "days": 31, "nones": 7, "ides": 15},
            {"latin": "Iunius", "english": "June", "days": 30, "nones": 5, "ides": 13},
            {"latin": "Iulius", "english": "July", "days": 31, "nones": 7, "ides": 15},
            {"latin": "Augustus", "english": "August", "days": 31, "nones": 5, "ides": 13},
            {"latin": "September", "english": "September", "days": 30, "nones": 5, "ides": 13},
            {"latin": "October", "english": "October", "days": 31, "nones": 7, "ides": 15},
            {"latin": "November", "english": "November", "days": 30, "nones": 5, "ides": 13},
            {"latin": "December", "english": "December", "days": 31, "nones": 5, "ides": 13}
        ],
        
        # Month cases for Latin grammar
        "ablatives": {
            "Ianuarius": "Ianuariis", "Februarius": "Februariis", "Martius": "Martiis",
            "Aprilis": "Aprilibus", "Maius": "Maiis", "Iunius": "Iuniis",
            "Iulius": "Iuliis", "Augustus": "Augustis", "September": "Septembribus",
            "October": "Octobribus", "November": "Novembribus", "December": "Decembribus"
        },
        
        "accusatives": {
            "Ianuarius": "Ianuarias", "Februarius": "Februarias", "Martius": "Martias",
            "Aprilis": "Apriles", "Maius": "Maias", "Iunius": "Iunias",
            "Iulius": "Iulias", "Augustus": "Augustas", "September": "Septembres",
            "October": "Octobres", "November": "Novembres", "December": "Decembres"
        },
        
        # Nundinal letters (8-day market week)
        "nundinal_letters": ["A", "B", "C", "D", "E", "F", "G", "H"],
        
        # Roman hours
        "day_hours": [
            "Prima", "Secunda", "Tertia", "Quarta", "Quinta", "Sexta",
            "Septima", "Octava", "Nona", "Decima", "Undecima", "Duodecima"
        ],
        
        "night_watches": [
            "Prima Vigilia", "Secunda Vigilia", "Tertia Vigilia", "Quarta Vigilia"
        ],
        
        # Major festivals
        "festivals": {
            (1, 1): "🎊 Kalendae Ianuariae - New Year",
            (1, 9): "⚖️ Agonalia",
            (2, 13): "🐺 Lupercalia",
            (2, 15): "🐺 Lupercalia",
            (2, 21): "👻 Feralia",
            (3, 1): "🔥 Matronalia",
            (3, 15): "🗡️ Anna Perenna",
            (3, 17): "🍷 Liberalia",
            (4, 21): "🏛️ Parilia - Founding of Rome",
            (5, 1): "🌺 Floralia",
            (6, 9): "🍞 Vestalia",
            (7, 23): "🌊 Neptunalia",
            (8, 13): "🌙 Diana Festival",
            (8, 23): "🔥 Vulcanalia",
            (10, 15): "🐴 October Horse",
            (12, 17): "🎉 Saturnalia",
            (12, 25): "☀️ Dies Natalis Solis Invicti"
        },
        
        # Founding of Rome
        "founding_year": 753  # BCE
    },
    
    # Additional metadata
    "reference_url": "https://en.wikipedia.org/wiki/Roman_calendar",
    "documentation_url": "https://www.britannica.com/science/Roman-calendar",
    "origin": "Ancient Rome",
    "created_by": "Roman civilization",
    "period": "753 BCE - 1582 CE",
    
    # Example format
    "example": "AUC 2777, ante diem III Kalendas Ianuarias",
    "example_meaning": "Year 2777 from founding of Rome, 3 days before January Kalends (Dec 30)",
    
    # Related calendars
    "related": ["julian", "gregorian", "attic"],
    
    # Tags for searching and filtering
    "tags": [
        "historical", "ancient", "roman", "latin", "kalends",
        "nones", "ides", "auc", "classical", "imperial"
    ],
    
    # Special features
    "features": {
        "backward_counting": True,
        "inclusive_counting": True,
        "nundinal_cycle": True,
        "variable_hours": True,
        "fasti": True,
        "precision": "day"
    },
    
    # Configuration options
    "config_options": {
        "show_latin": {
            "type": "boolean",
            "default": True,
            "description": {
                "en": "Show Latin date format",
                "de": "Lateinisches Datumsformat anzeigen",
                "la": "Forma Latina ostendere"
            }
        },
        "show_festivals": {
            "type": "boolean",
            "default": True,
            "description": {
                "en": "Show Roman festivals",
                "de": "Römische Feste anzeigen",
                "la": "Festa Romana ostendere"
            }
        },
        "show_hours": {
            "type": "boolean",
            "default": True,
            "description": {
                "en": "Show Roman hours",
                "de": "Römische Stunden anzeigen",
                "la": "Horas Romanas ostendere"
            }
        }
    }
}


class RomanCalendarSensor(AlternativeTimeSensorBase):
    """Sensor for displaying Roman Calendar."""
    
    # Class-level update interval
    UPDATE_INTERVAL = 3600  # Update every hour
    
    def __init__(self, base_name: str, hass: HomeAssistant) -> None:
        """Initialize the Roman calendar sensor."""
        super().__init__(base_name, hass)
        
        # Get translated name from metadata
        calendar_name = self._translate('name', 'Roman Calendar')
        
        # Set sensor attributes
        self._attr_name = f"{base_name} {calendar_name}"
        self._attr_unique_id = f"{base_name}_roman_calendar"
        self._attr_icon = CALENDAR_INFO.get("icon", "mdi:pillar")
        
        # Configuration options
        self._show_latin = True
        self._show_festivals = True
        self._show_hours = True
        
        # Roman data
        self._roman_data = CALENDAR_INFO["roman_data"]
        
        _LOGGER.debug(f"Initialized Roman Calendar sensor: {self._attr_name}")
    
    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes."""
        attrs = super().extra_state_attributes
        
        # Add Roman-specific attributes
        if hasattr(self, '_roman_date'):
            attrs.update(self._roman_date)
            
            # Add description in user's language
            attrs["description"] = self._translate('description')
            
            # Add reference
            attrs["reference"] = CALENDAR_INFO.get('reference_url', '')
        
        return attrs
    
    def _to_roman_numeral(self, num: int) -> str:
        """Convert number to Roman numeral."""
        val = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
        syms = ['M', 'CM', 'D', 'CD', 'C', 'XC', 'L', 'XL', 'X', 'IX', 'V', 'IV', 'I']
        roman_num = ''
        i = 0
        while num > 0:
            for _ in range(num // val[i]):
                roman_num += syms[i]
                num -= val[i]
            i += 1
        return roman_num
    
    def _calculate_roman_date(self, earth_date: datetime) -> Dict[str, Any]:
        """Calculate Roman date from modern date."""
        
        # Calculate Ab Urbe Condita
        year_auc = earth_date.year + self._roman_data["founding_year"]
        
        # Consul year (simplified)
        if -27 <= (earth_date.year - 2000) <= 14:
            consul_year = f"Imp. Caesar Augustus, Year {earth_date.year + 27}"
        else:
            consul_year = f"Anno Domini {earth_date.year}"
        
        # Get month info
        month_data = self._roman_data["months"][earth_date.month - 1]
        month_latin = month_data["latin"]
        
        # Calculate Roman day notation
        day = earth_date.day
        nones_day = month_data["nones"]
        ides_day = month_data["ides"]
        
        # Determine day type and Latin notation
        if day == 1:
            day_latin = f"Kalendis {self._roman_data['ablatives'][month_latin]}"
            day_type = "Kalends"
            phase = "Beginning"
        elif day < nones_day:
            days_before = nones_day - day + 1
            day_latin = f"ante diem {self._to_roman_numeral(days_before)} Nonas {self._roman_data['accusatives'][month_latin]}"
            day_type = "Before Nones"
            phase = "Waxing"
        elif day == nones_day:
            day_latin = f"Nonis {self._roman_data['ablatives'][month_latin]}"
            day_type = "Nones"
            phase = "First Quarter"
        elif day < ides_day:
            days_before = ides_day - day + 1
            day_latin = f"ante diem {self._to_roman_numeral(days_before)} Idus {self._roman_data['accusatives'][month_latin]}"
            day_type = "Before Ides"
            phase = "Waxing"
        elif day == ides_day:
            day_latin = f"Idibus {self._roman_data['ablatives'][month_latin]}"
            day_type = "Ides"
            phase = "Full"
        else:
            # Days after Ides
            if earth_date.month < 12:
                next_month = self._roman_data["months"][earth_date.month]["latin"]
            else:
                next_month = self._roman_data["months"][0]["latin"]
            
            days_before = month_data["days"] - day + 2
            day_latin = f"ante diem {self._to_roman_numeral(days_before)} Kalendas {self._roman_data['accusatives'][next_month]}"
            day_type = "Before Kalends"
            phase = "Waning"
        
        # Nundinal cycle
        reference_date = datetime(2000, 1, 1)
        days_since = (earth_date - reference_date).days
        week_letter = self._roman_data["nundinal_letters"][days_since % 8]
        market_day = "🛒 Market Day" if week_letter == 'A' else ""
        
        # Roman hours
        hora = ""
        hora_type = ""
        if self._show_hours:
            hour = earth_date.hour
            if 6 <= hour < 18:
                hora_number = min(hour - 5, 11)
                hora = f"Hora {self._roman_data['day_hours'][hora_number]}"
                hora_type = "Dies (Day)"
            else:
                if hour >= 18:
                    hora_number = hour - 17
                else:
                    hora_number = hour + 7
                watch = self._roman_data["night_watches"][min(hora_number // 3, 3)]
                hora = watch
                hora_type = "Nox (Night)"
        
        # Festival
        festival = ""
        if self._show_festivals:
            festival = self._roman_data["festivals"].get((earth_date.month, earth_date.day), "")
        
        # Lucky/Unlucky
        if day_type in ["Kalends", "Nones", "Ides"]:
            lucky = "Dies Nefastus"
        elif festival:
            lucky = "Dies Festus"
        elif week_letter == 'A':
            lucky = "Dies Nundinae"
        else:
            lucky = "Dies Fastus"
        
        result = {
            "year_auc": year_auc,
            "year_ad": earth_date.year,
            "consul_year": consul_year,
            "month": month_data["english"],
            "month_latin": month_latin,
            "day": day,
            "day_latin": day_latin,
            "day_type": day_type,
            "phase_of_month": phase,
            "week_letter": week_letter,
            "market_day": market_day,
            "lucky_unlucky": lucky,
            "gregorian_date": earth_date.strftime("%Y-%m-%d"),
            "full_date": f"AUC {year_auc}, {day_latin}"
        }
        
        if self._show_hours and hora:
            result["hora"] = hora
            result["hora_type"] = hora_type
        
        if festival:
            result["festival"] = festival
        
        return result
    
    def update(self) -> None:
        """Update the sensor."""
        now = datetime.now()
        self._roman_date = self._calculate_roman_date(now)
        
        # Set state to formatted Roman date
        self._state = self._roman_date["full_date"]
        
        _LOGGER.debug(f"Updated Roman Calendar to {self._state}")