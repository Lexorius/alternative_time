"""Discworld Calendar (Terry Pratchett) implementation - Version 2.5."""
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
    "id": "discworld",
    "version": "2.5.0",
    "icon": "mdi:turtle",
    "category": "fantasy",
    "accuracy": "fictional",
    "update_interval": UPDATE_INTERVAL,
    
    # Multi-language names
    "name": {
        "en": "Discworld Calendar",
        "de": "Scheibenwelt-Kalender",
        "es": "Calendario del Mundodisco",
        "fr": "Calendrier du Disque-Monde",
        "it": "Calendario del Mondo Disco",
        "nl": "Schijfwereld Kalender",
        "pt": "Calendário do Discworld",
        "ru": "Календарь Плоского мира",
        "ja": "ディスクワールド暦",
        "zh": "碟形世界历",
        "ko": "디스크월드 달력"
    },
    
    # Short descriptions for UI
    "description": {
        "en": "Terry Pratchett's Discworld calendar with 8-day weeks and guild influences",
        "de": "Terry Pratchetts Scheibenwelt-Kalender mit 8-Tage-Wochen und Gildeneinflüssen",
        "es": "Calendario del Mundodisco de Terry Pratchett con semanas de 8 días e influencias gremiales",
        "fr": "Calendrier du Disque-Monde de Terry Pratchett avec semaines de 8 jours et influences des guildes",
        "it": "Calendario del Mondo Disco di Terry Pratchett con settimane di 8 giorni e influenze delle gilde",
        "nl": "Terry Pratchett's Schijfwereld kalender met 8-daagse weken en gilde-invloeden",
        "pt": "Calendário do Discworld de Terry Pratchett com semanas de 8 dias e influências das guildas",
        "ru": "Календарь Плоского мира Терри Пратчетта с 8-дневными неделями и влиянием гильдий",
        "ja": "テリー・プラチェットのディスクワールド暦、8日週とギルドの影響",
        "zh": "特里·普拉切特的碟形世界历，8天周和公会影响",
        "ko": "테리 프래쳇의 디스크월드 달력, 8일 주와 길드 영향"
    },
    
    # Detailed information for documentation
    "detailed_info": {
        "en": {
            "overview": "The Discworld calendar is used on Terry Pratchett's fictional Disc, carried by four elephants on the Great A'Tuin",
            "structure": "13 months with varying days, 8-day weeks including Octeday",
            "year": "The year is divided into common months plus the special Century of the Fruitbat",
            "weeks": "8-day weeks: Sunday through Saturday plus Octeday",
            "guilds": "Each day is influenced by different Ankh-Morpork guilds",
            "events": "Includes Hogswatchday (like Christmas), Soul Cake Night (Halloween), and other festivals",
            "humor": "Contains impossible dates like the 32nd of December as Pratchett humor",
            "death": "Death (THE ANTHROPOMORPHIC PERSONIFICATION) makes regular appearances"
        },
        "de": {
            "overview": "Der Scheibenwelt-Kalender wird auf Terry Pratchetts fiktiver Scheibe verwendet, getragen von vier Elefanten auf der Großen A'Tuin",
            "structure": "13 Monate mit unterschiedlichen Tagen, 8-Tage-Wochen einschließlich Okttag",
            "year": "Das Jahr ist in gewöhnliche Monate plus das besondere Jahrhundert der Flughunde unterteilt",
            "weeks": "8-Tage-Wochen: Sonntag bis Samstag plus Okttag",
            "guilds": "Jeder Tag wird von verschiedenen Ankh-Morpork-Gilden beeinflusst",
            "events": "Beinhaltet Schweinswacht (wie Weihnachten), Seelenkuchennacht (Halloween) und andere Feste",
            "humor": "Enthält unmögliche Daten wie den 32. Dezember als Pratchett-Humor",
            "death": "Tod (DIE ANTHROPOMORPHE PERSONIFIKATION) erscheint regelmäßig"
        }
    },
    
    # Discworld-specific data
    "discworld_data": {
        # Discworld months
        "months": [
            {"name": "Ick", "emoji": "❄️", "season": "Winter"},
            {"name": "Offle", "emoji": "❄️", "season": "Winter"},
            {"name": "February", "emoji": "🌨️", "season": "Winter"},  # Yes, February
            {"name": "March", "emoji": "🌬️", "season": "Spring"},
            {"name": "April", "emoji": "🌧️", "season": "Spring"},
            {"name": "May", "emoji": "🌸", "season": "Spring"},
            {"name": "June", "emoji": "☀️", "season": "Summer"},
            {"name": "Grune", "emoji": "🌿", "season": "Summer"},
            {"name": "August", "emoji": "🌞", "season": "Summer"},
            {"name": "Spune", "emoji": "🍂", "season": "Autumn"},
            {"name": "Sektober", "emoji": "🍺", "season": "Autumn"},  # Drinking month
            {"name": "Ember", "emoji": "🔥", "season": "Autumn"},
            {"name": "December", "emoji": "⭐", "season": "Winter"}
        ],
        
        # 8-day week
        "weekdays": [
            "Sunday", "Monday", "Tuesday", "Wednesday",
            "Thursday", "Friday", "Saturday", "Octeday"
        ],
        
        # Guilds of Ankh-Morpork
        "guilds": [
            "Assassins' Guild", "Thieves' Guild", "Seamstresses' Guild",
            "Beggars' Guild", "Merchants' Guild", "Alchemists' Guild",
            "Wizards (Unseen University)", "Watch (City Guard)",
            "Fools' Guild", "Musicians' Guild", "Bakers' Guild",
            "Butchers' Guild", "Candlemakers' Guild"
        ],
        
        # Special events
        "events": {
            (1, 1): "Hogswatchday 🎅",
            (2, 14): "Day of Small Gods",
            (3, 25): "The Rag Week",
            (4, 1): "All Fools' Day",
            (4, 32): "Day That Never Happens",
            (5, 1): "May Day",
            (5, 25): "Glorious Revolution Day",
            (6, 21): "Midsummer's Eve",
            (7, 15): "Patrician's Birthday",
            (8, 12): "Thieves' Guild Day",
            (9, 9): "Mrs. Cake Day",
            (10, 31): "Soul Cake Night 🎃",
            (11, 11): "Elevenses Day",
            (12, 32): "Hogswatch Eve"
        },
        
        # Death quotes
        "death_quotes": [
            "THERE IS NO JUSTICE. THERE IS JUST ME.",
            "I COULD MURDER A CURRY.",
            "CATS. CATS ARE NICE.",
            "SQUEAK.",
            "THE DUTY IS MINE.",
            "WHAT CAN THE HARVEST HOPE FOR, IF NOT FOR THE CARE OF THE REAPER MAN?",
            "I DON'T HOLD WITH CRUELTY TO CATS.",
            "LORD, WHAT CAN THE HARVEST HOPE FOR, IF NOT THE CARE OF THE REAPER MAN?",
            "YOU NEED TO BELIEVE IN THINGS THAT AREN'T TRUE. HOW ELSE CAN THEY BECOME?"
        ],
        
        # City areas
        "city_areas": [
            "The Shades", "Patrician's Palace", "Unseen University",
            "The Docks", "Treacle Mine Road", "Cable Street",
            "The Hippo", "Isle of Gods", "Pseudopolis Yard",
            "Sator Square", "The Maul", "Dolly Sisters"
        ],
        
        # Time periods
        "time_periods": {
            (0, 3): {"name": "Dead of Night", "description": "Graveyard Shift", "emoji": "🌙"},
            (3, 6): {"name": "Small Hours", "description": "Thieves' Time", "emoji": "⭐"},
            (6, 9): {"name": "Dawn", "description": "Milkmen About", "emoji": "🌅"},
            (9, 12): {"name": "Morning", "description": "Shops Open", "emoji": "☀️"},
            (12, 13): {"name": "Noon", "description": "Lunch at Harga's", "emoji": "🍽️"},
            (13, 17): {"name": "Afternoon", "description": "Siesta Time", "emoji": "🌤️"},
            (17, 19): {"name": "Evening", "description": "Pub O'Clock", "emoji": "🍺"},
            (19, 21): {"name": "Dusk", "description": "Theatre Time", "emoji": "🌆"},
            (21, 24): {"name": "Night", "description": "Watch Patrol", "emoji": "🌃"}
        }
    },
    
    # Additional metadata
    "reference_url": "https://wiki.lspace.org/Discworld_calendar",
    "documentation_url": "https://www.terrypratchettbooks.com/",
    "origin": "Terry Pratchett's Discworld series",
    "created_by": "Terry Pratchett",
    "introduced": "The Colour of Magic (1983)",
    
    # Example format
    "example": "Century of the Anchovy, UC 25, 15 Grune (Octeday)",
    "example_meaning": "Century of the Anchovy, UC (University Calendar) year 25, 15th of Grune, Octeday",
    
    # Related calendars
    "related": ["gregorian", "fictional"],
    
    # Tags for searching and filtering
    "tags": [
        "fantasy", "discworld", "pratchett", "ankh-morpork", "fictional",
        "humor", "death", "guilds", "octeday", "turtle", "atuin"
    ],
    
    # Special features
    "features": {
        "eight_day_week": True,
        "guild_system": True,
        "impossible_dates": True,
        "death_appearances": True,
        "l_space": True,
        "precision": "day"
    },
    
    # Configuration options for this calendar
    "config_options": {
        "show_death_quotes": {
            "type": "boolean",
            "default": True,
            "description": {
                "en": "Show Death's daily quote at midnight",
                "de": "Tods tägliches Zitat um Mitternacht anzeigen"
            }
        },
        "show_guild": {
            "type": "boolean",
            "default": True,
            "description": {
                "en": "Show daily guild influence",
                "de": "Täglichen Gildeneinfluss anzeigen"
            }
        },
        "show_location": {
            "type": "boolean",
            "default": True,
            "description": {
                "en": "Show current Ankh-Morpork location",
                "de": "Aktuellen Ankh-Morpork Standort anzeigen"
            }
        },
        "detect_l_space": {
            "type": "boolean",
            "default": True,
            "description": {
                "en": "Detect L-Space anomalies",
                "de": "L-Raum-Anomalien erkennen"
            }
        }
    }
}


class DiscworldCalendarSensor(AlternativeTimeSensorBase):
    """Sensor for displaying Discworld Calendar (Terry Pratchett)."""
    
    # Class-level update interval
    UPDATE_INTERVAL = 3600  # Update every hour
    
    def __init__(self, base_name: str, hass: HomeAssistant) -> None:
        """Initialize the Discworld calendar sensor."""
        super().__init__(base_name, hass)
        
        # Get translated name from metadata
        calendar_name = self._translate('name', 'Discworld Calendar')
        
        # Set sensor attributes
        self._attr_name = f"{base_name} {calendar_name}"
        self._attr_unique_id = f"{base_name}_discworld"
        self._attr_icon = CALENDAR_INFO.get("icon", "mdi:turtle")
        
        # Configuration options
        self._show_death_quotes = True
        self._show_guild = True
        self._show_location = True
        self._detect_l_space = True
        
        # Discworld data
        self._discworld_data = CALENDAR_INFO["discworld_data"]
        
        _LOGGER.debug(f"Initialized Discworld Calendar sensor: {self._attr_name}")
    
    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes."""
        attrs = super().extra_state_attributes
        
        # Add Discworld-specific attributes
        if hasattr(self, '_discworld_date'):
            attrs.update(self._discworld_date)
            
            # Add description in user's language
            attrs["description"] = self._translate('description')
            
            # Add reference
            attrs["reference"] = CALENDAR_INFO.get('reference_url', '')
            
            # Add Great A'Tuin status
            attrs["great_atuin"] = "Swimming through space 🐢"
            attrs["elephants"] = "Berilia, Tubul, Great T'Phon, and Jerakeen"
        
        return attrs
    
    def _get_time_period(self, hour: int) -> Dict[str, str]:
        """Get the Discworld time period for the hour."""
        for (start, end), period in self._discworld_data["time_periods"].items():
            if start <= hour < end:
                return period
        return {"name": "Temporal Anomaly", "description": "Time is broken", "emoji": "⏰"}
    
    def _calculate_discworld_date(self, earth_date: datetime) -> Dict[str, Any]:
        """Calculate Discworld Calendar date from standard date."""
        
        # Discworld year (Century of the Anchovy as current)
        year_since_2000 = earth_date.year - 2000
        discworld_year = 1 + year_since_2000
        
        # Get month and day
        month_index = min(earth_date.month - 1, 12)
        day = earth_date.day
        
        # Handle special 32nd days (Discworld has them!)
        if day == 31 and earth_date.month in [4, 12]:
            day = 32  # Discworld logic!
        
        # Get month data
        if month_index < len(self._discworld_data["months"]):
            month_data = self._discworld_data["months"][month_index]
        else:
            month_data = {"name": "Backspindlemonth", "emoji": "🌀", "season": "Temporal"}
        
        # Calculate weekday (8-day week)
        days_since_epoch = (earth_date - datetime(2000, 1, 1)).days
        weekday_index = days_since_epoch % 8
        weekday = self._discworld_data["weekdays"][weekday_index]
        is_octeday = weekday_index == 7
        
        # Check for events
        event = self._discworld_data["events"].get((earth_date.month, day), "")
        
        # Guild influence (rotates daily)
        guild_index = days_since_epoch % len(self._discworld_data["guilds"])
        guild = self._discworld_data["guilds"][guild_index]
        
        # Death quote (changes daily)
        death_index = days_since_epoch % len(self._discworld_data["death_quotes"])
        death_quote = self._discworld_data["death_quotes"][death_index]
        
        # City location (changes hourly)
        location_index = (days_since_epoch + earth_date.hour) % len(self._discworld_data["city_areas"])
        location = self._discworld_data["city_areas"][location_index]
        
        # Time period
        time_period = self._get_time_period(earth_date.hour)
        
        # L-Space detection
        l_space_detected = (earth_date.hour == 3 and earth_date.minute == 33) if self._detect_l_space else False
        
        # Build the date string
        date_parts = [
            f"Century of the Anchovy, UC {discworld_year}",
            f"{day} {month_data['name']} ({weekday})"
        ]
        
        if is_octeday:
            date_parts[1] += " | 🎉 It's Octeday!"
        
        date_parts.append(f"{time_period['emoji']} {time_period['name']} ({time_period['description']})")
        
        if self._show_location:
            date_parts.append(f"📍 {location}")
        
        if self._show_guild:
            date_parts.append(guild)
        
        if event:
            date_parts.append(event)
        
        full_date = " | ".join(date_parts)
        
        # Add Death quote at midnight if enabled
        if earth_date.hour == 0 and self._show_death_quotes:
            full_date += f"\n💀 Death says: {death_quote}"
        
        # Add L-Space notification
        if l_space_detected:
            full_date += "\n📚 L-Space detected!"
        
        result = {
            "year": discworld_year,
            "century": "Century of the Anchovy",
            "month": month_data["name"],
            "month_emoji": month_data["emoji"],
            "season": month_data["season"],
            "day": day,
            "weekday": weekday,
            "is_octeday": is_octeday,
            "time_period": time_period["name"],
            "time_description": time_period["description"],
            "guild_influence": guild,
            "location": location,
            "death_quote": death_quote if earth_date.hour == 0 else "",
            "l_space": l_space_detected,
            "gregorian_date": earth_date.strftime("%Y-%m-%d"),
            "full_date": full_date
        }
        
        if event:
            result["event"] = event
        
        return result
    
    def update(self) -> None:
        """Update the sensor."""
        now = datetime.now()
        self._discworld_date = self._calculate_discworld_date(now)
        
        # Set state to main date line
        state_parts = [
            f"UC {self._discworld_date['year']}",
            f"{self._discworld_date['day']} {self._discworld_date['month']}",
            f"({self._discworld_date['weekday']})"
        ]
        self._state = " ".join(state_parts)
        
        _LOGGER.debug(f"Updated Discworld Calendar to {self._state}")