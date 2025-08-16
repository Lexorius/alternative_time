"""Attic Calendar (Ancient Athens) implementation - Version 2.5."""
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

# Update interval in seconds (3600 seconds = 1 hour, dates change slowly)
UPDATE_INTERVAL = 3600

# Complete calendar information for auto-discovery
CALENDAR_INFO = {
    "id": "attic",
    "version": "2.5.0",
    "icon": "mdi:pillar",
    "category": "historical",
    "accuracy": "approximate",
    "update_interval": UPDATE_INTERVAL,
    
    # Multi-language names
    "name": {
        "en": "Attic Calendar",
        "de": "Attischer Kalender",
        "es": "Calendario Ático",
        "fr": "Calendrier Attique",
        "it": "Calendario Attico",
        "nl": "Attische Kalender",
        "pt": "Calendário Ático",
        "ru": "Аттический календарь",
        "ja": "アッティカ暦",
        "zh": "雅典历",
        "ko": "아티카 달력",
        "el": "Αττικό Ημερολόγιο"
    },
    
    # Short descriptions for UI
    "description": {
        "en": "Ancient Athenian lunisolar calendar with Archon and Olympiad (e.g. 5 ἱσταμένου Hekatombaion)",
        "de": "Antiker Athener Lunisolarkalender mit Archon und Olympiade (z.B. 5 ἱσταμένου Hekatombaion)",
        "es": "Calendario lunisolar ateniense antiguo con Arconte y Olimpiada",
        "fr": "Calendrier lunisolaire athénien antique avec Archonte et Olympiade",
        "it": "Calendario lunisolare ateniese antico con Arconte e Olimpiade",
        "nl": "Oude Atheense lunisolaire kalender met Archont en Olympiade",
        "pt": "Calendário lunissolar ateniense antigo com Arconte e Olimpíada",
        "ru": "Древний афинский лунно-солнечный календарь с архонтом и олимпиадой",
        "ja": "アルコンとオリンピアードを含む古代アテネの太陰太陽暦",
        "zh": "带执政官和奥林匹克纪年的古雅典阴阳历",
        "ko": "아르콘과 올림피아드가 있는 고대 아테네 태음태양력",
        "el": "Αρχαίο αθηναϊκό σεληνιακό-ηλιακό ημερολόγιο με Άρχοντα και Ολυμπιάδα"
    },
    
    # Detailed information for documentation
    "detailed_info": {
        "en": {
            "overview": "The Attic calendar was the lunisolar calendar of ancient Athens",
            "structure": "12 lunar months of 29-30 days (alternating hollow/full months)",
            "new_year": "Year began at first new moon after summer solstice",
            "dekads": "Months divided into three dekads (10-day periods)",
            "day_counting": "Days 1-10: waxing moon, Days 11-20: middle, Days 21-29/30: waning (counted backward!)",
            "intercalation": "Intercalary months added to align with solar year",
            "dating": "Dating formula: Day + Period + Month + Archon + Olympiad",
            "note": "This is a simplified approximation of the complex ancient calendar"
        },
        "de": {
            "overview": "Der attische Kalender war der Lunisolarkalender des antiken Athen",
            "structure": "12 Mondmonate mit 29-30 Tagen (abwechselnd hohle/volle Monate)",
            "new_year": "Jahr begann beim ersten Neumond nach der Sommersonnenwende",
            "dekads": "Monate unterteilt in drei Dekaden (10-Tage-Perioden)",
            "day_counting": "Tag 1-10: zunehmender Mond, Tag 11-20: Mitte, Tag 21-29/30: abnehmend (rückwärts gezählt!)",
            "intercalation": "Schaltmonate wurden hinzugefügt, um mit dem Sonnenjahr übereinzustimmen",
            "dating": "Datierungsformel: Tag + Periode + Monat + Archon + Olympiade",
            "note": "Dies ist eine vereinfachte Annäherung des komplexen antiken Kalenders"
        },
        "el": {
            "overview": "Το Αττικό ημερολόγιο ήταν το σεληνιακό-ηλιακό ημερολόγιο της αρχαίας Αθήνας",
            "structure": "12 σεληνιακοί μήνες των 29-30 ημερών (εναλλασσόμενοι κοίλοι/πλήρεις μήνες)",
            "new_year": "Το έτος άρχιζε με την πρώτη νέα σελήνη μετά το θερινό ηλιοστάσιο",
            "dekads": "Οι μήνες χωρίζονταν σε τρεις δεκάδες (περίοδοι 10 ημερών)",
            "day_counting": "Ημέρες 1-10: αύξουσα σελήνη, 11-20: μέσον, 21-29/30: φθίνουσα (μετρώνται ανάποδα!)",
            "intercalation": "Εμβόλιμοι μήνες προστίθενταν για ευθυγράμμιση με το ηλιακό έτος",
            "dating": "Τύπος χρονολόγησης: Ημέρα + Περίοδος + Μήνας + Άρχοντας + Ολυμπιάδα",
            "note": "Αυτή είναι μια απλοποιημένη προσέγγιση του πολύπλοκου αρχαίου ημερολογίου"
        }
    },
    
    # Attic-specific data
    "attic_data": {
        # Attic months (lunisolar calendar)
        "months": [
            {"name": "Hekatombaion", "meaning": "Month of hundred oxen", "days": 30},
            {"name": "Metageitnion", "meaning": "Month of changing neighbors", "days": 29},
            {"name": "Boedromion", "meaning": "Month of running for help", "days": 30},
            {"name": "Pyanepsion", "meaning": "Bean-stewing month", "days": 29},
            {"name": "Maimakterion", "meaning": "Month of storms", "days": 30},
            {"name": "Poseideon", "meaning": "Poseidon's month", "days": 29},
            {"name": "Gamelion", "meaning": "Wedding month", "days": 30},
            {"name": "Anthesterion", "meaning": "Flower month", "days": 29},
            {"name": "Elaphebolion", "meaning": "Deer-hunting month", "days": 30},
            {"name": "Mounichion", "meaning": "Month of Mounichia festival", "days": 29},
            {"name": "Thargelion", "meaning": "Month of Thargelia festival", "days": 30},
            {"name": "Skirophorion", "meaning": "Month of parasol-bearing", "days": 29}
        ],
        
        # Dekad periods (10-day periods)
        "dekad_periods": [
            {"greek": "ἱσταμένου", "transliteration": "histamenou", "meaning": "waxing moon", "days": "1-10"},
            {"greek": "μεσοῦντος", "transliteration": "mesountos", "meaning": "middle", "days": "11-20"},
            {"greek": "φθίνοντος", "transliteration": "phthinontos", "meaning": "waning", "days": "21-29/30"}
        ],
        
        # Sample Archons (chief magistrates)
        "archons": [
            "Nikias", "Kallias", "Kritias", "Alkibiades",
            "Kleisthenes", "Perikles", "Themistokles", "Solon",
            "Drakon", "Aristides", "Kimon", "Ephialtes"
        ],
        
        # Important festivals
        "festivals": {
            "Hekatombaion": ["Kronia", "Synoikia", "Panathenaia"],
            "Metageitnion": ["Metageitnia", "Karneia"],
            "Boedromion": ["Genesia", "Eleusinian Mysteries", "Plataia"],
            "Pyanepsion": ["Pyanopsia", "Theseia", "Oschophoria", "Apaturia"],
            "Maimakterion": ["Maimakteria", "Pompaia"],
            "Poseideon": ["Poseideia", "Haloa"],
            "Gamelion": ["Gamelia", "Lenaia"],
            "Anthesterion": ["Anthesteria", "Diasia"],
            "Elaphebolion": ["Elaphebolia", "City Dionysia", "Pandia"],
            "Mounichion": ["Mounichia", "Olympieia"],
            "Thargelion": ["Thargelia", "Bendideia", "Plynteria"],
            "Skirophorion": ["Skira", "Dipolia", "Bouphonia", "Arrephoria"]
        },
        
        # Olympiad data
        "olympiad_epoch": -776,  # 776 BCE
        "olympiad_length": 4  # years
    },
    
    # Additional metadata
    "reference_url": "https://en.wikipedia.org/wiki/Attic_calendar",
    "documentation_url": "https://www.csun.edu/~hcfll004/atticcal.html",
    "origin": "Ancient Athens, Greece",
    "created_by": "Ancient Athenians",
    "period": "6th century BCE - 4th century CE",
    
    # Example format
    "example": "5 ἱσταμένου Hekatombaion | Nikias | Ol.700.2",
    "example_meaning": "5th day of waxing moon, Hekatombaion month, Archon Nikias, Olympiad 700 year 2",
    
    # Related calendars
    "related": ["gregorian", "julian", "macedonian"],
    
    # Tags for searching and filtering
    "tags": [
        "historical", "ancient", "greek", "athens", "lunisolar",
        "archon", "olympiad", "dekad", "classical", "hellenic"
    ],
    
    # Special features
    "features": {
        "lunisolar": True,
        "dekads": True,
        "backward_counting": True,
        "archons": True,
        "olympiads": True,
        "festivals": True,
        "precision": "day"
    },
    
    # Configuration options for this calendar
    "config_options": {
        "show_greek": {
            "type": "boolean",
            "default": True,
            "description": {
                "en": "Show period names in Greek",
                "de": "Periodennamen auf Griechisch anzeigen",
                "el": "Εμφάνιση ονομάτων περιόδων στα ελληνικά"
            }
        },
        "show_festivals": {
            "type": "boolean",
            "default": True,
            "description": {
                "en": "Show Athenian festivals",
                "de": "Athenische Feste anzeigen",
                "el": "Εμφάνιση αθηναϊκών εορτών"
            }
        },
        "show_meanings": {
            "type": "boolean",
            "default": False,
            "description": {
                "en": "Show month name meanings",
                "de": "Monatsnamen-Bedeutungen anzeigen",
                "el": "Εμφάνιση σημασίας ονομάτων μηνών"
            }
        }
    }
}


class AtticCalendarSensor(AlternativeTimeSensorBase):
    """Sensor for displaying Attic Calendar (Ancient Athens)."""
    
    # Class-level update interval
    UPDATE_INTERVAL = 3600  # Update every hour
    
    def __init__(self, base_name: str, hass: HomeAssistant) -> None:
        """Initialize the Attic calendar sensor."""
        super().__init__(base_name, hass)
        
        # Get translated name from metadata
        calendar_name = self._translate('name', 'Attic Calendar')
        
        # Set sensor attributes
        self._attr_name = f"{base_name} {calendar_name}"
        self._attr_unique_id = f"{base_name}_attic_calendar"
        self._attr_icon = CALENDAR_INFO.get("icon", "mdi:pillar")
        
        # Configuration options
        self._show_greek = True
        self._show_festivals = True
        self._show_meanings = False
        
        # Attic data
        self._attic_data = CALENDAR_INFO["attic_data"]
        
        _LOGGER.debug(f"Initialized Attic Calendar sensor: {self._attr_name}")
    
    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes."""
        attrs = super().extra_state_attributes
        
        # Add Attic-specific attributes
        if hasattr(self, '_attic_date'):
            attrs.update(self._attic_date)
            
            # Add description in user's language
            attrs["description"] = self._translate('description')
            
            # Add reference
            attrs["reference"] = CALENDAR_INFO.get('reference_url', '')
        
        return attrs
    
    def _calculate_attic_date(self, earth_date: datetime) -> Dict[str, Any]:
        """Calculate Attic Calendar date from standard date."""
        
        # Simplified calculation - actual Attic calendar was complex
        # We approximate by starting the year around July (summer solstice)
        days_since_summer_solstice = (earth_date.timetuple().tm_yday - 172) % 365
        
        # Calculate month (approximately 30 days each)
        month_index = min(days_since_summer_solstice // 30, 11)
        day_in_month = (days_since_summer_solstice % 30) + 1
        
        # Get month data
        month_data = self._attic_data["months"][month_index]
        month_name = month_data["name"]
        month_meaning = month_data["meaning"]
        days_in_month = month_data["days"]
        
        # Adjust day if it exceeds month's actual days
        if day_in_month > days_in_month:
            day_in_month = days_in_month
        
        # Determine dekad (10-day period) and format day
        if day_in_month <= 10:
            dekad_index = 0  # Waxing
            day_display = day_in_month
        elif day_in_month <= 20:
            dekad_index = 1  # Middle
            day_display = day_in_month - 10
        else:
            dekad_index = 2  # Waning
            # In waning period, days counted backward from end
            day_display = days_in_month - day_in_month + 1
        
        dekad_data = self._attic_data["dekad_periods"][dekad_index]
        period_greek = dekad_data["greek"] if self._show_greek else dekad_data["transliteration"]
        period_meaning = dekad_data["meaning"]
        
        # Select archon (chief magistrate) - rotates yearly
        archon = self._attic_data["archons"][earth_date.year % len(self._attic_data["archons"])]
        
        # Calculate Olympiad (4-year cycle)
        years_since_epoch = earth_date.year - self._attic_data["olympiad_epoch"]
        olympiad_number = years_since_epoch // self._attic_data["olympiad_length"]
        olympiad_year = (years_since_epoch % self._attic_data["olympiad_length"]) + 1
        
        # Get festivals for this month if enabled
        festivals = []
        if self._show_festivals and month_name in self._attic_data["festivals"]:
            festivals = self._attic_data["festivals"][month_name]
        
        # Format the date
        full_date = f"{day_display} {period_greek} {month_name} | {archon} | Ol.{olympiad_number}.{olympiad_year}"
        
        result = {
            "day": day_display,
            "period": period_greek,
            "period_meaning": period_meaning,
            "dekad": dekad_index + 1,
            "month": month_name,
            "month_index": month_index + 1,
            "archon": archon,
            "olympiad": f"Ol.{olympiad_number}.{olympiad_year}",
            "olympiad_number": olympiad_number,
            "olympiad_year": olympiad_year,
            "gregorian_date": earth_date.strftime("%Y-%m-%d"),
            "full_date": full_date
        }
        
        # Add month meaning if enabled
        if self._show_meanings:
            result["month_meaning"] = month_meaning
        
        # Add festivals if any
        if festivals:
            result["festivals"] = ", ".join(festivals)
            result["festival_day"] = f"🏛️ Festival day: {festivals[0]}"
        
        # Add season
        if month_index in [0, 1, 2]:
            result["season"] = "θέρος (Summer)"
        elif month_index in [3, 4, 5]:
            result["season"] = "φθινόπωρον (Autumn)"
        elif month_index in [6, 7, 8]:
            result["season"] = "χειμών (Winter)"
        else:
            result["season"] = "ἔαρ (Spring)"
        
        return result
    
    def update(self) -> None:
        """Update the sensor."""
        now = datetime.now()
        self._attic_date = self._calculate_attic_date(now)
        
        # Set state to full Attic date
        self._state = self._attic_date["full_date"]
        
        _LOGGER.debug(f"Updated Attic Calendar to {self._state}")