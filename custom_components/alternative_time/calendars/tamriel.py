"""Tamriel Calendar (Elder Scrolls) implementation."""
from __future__ import annotations

from datetime import datetime
import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)


class TamrielCalendarSensor(SensorEntity):
    """Sensor for displaying Tamrielic Calendar from Elder Scrolls."""

    def __init__(self, base_name: str) -> None:
        """Initialize the Tamriel calendar sensor."""
        self._attr_name = f"{base_name} Tamriel Calendar"
        self._attr_unique_id = f"{base_name}_tamriel_calendar"
        self._attr_icon = "mdi:dragon"
        self._state = None

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        tamriel_date = self._calculate_tamriel_date(datetime.now())
        
        return {
            "era": tamriel_date["era"],
            "year": tamriel_date["year"],
            "month": tamriel_date["month"],
            "day": tamriel_date["day"],
            "weekday": tamriel_date["weekday"],
            "birthsign": tamriel_date["birthsign"],
            "season": tamriel_date["season"],
            "holiday": tamriel_date["holiday"],
            "divine_blessing": tamriel_date["divine_blessing"],
            "daedric_prince": tamriel_date["daedric_prince"],
            "moon_phase_masser": tamriel_date["moon_phase_masser"],
            "moon_phase_secunda": tamriel_date["moon_phase_secunda"],
            "time_period": tamriel_date["time_period"],
            "guild_day": tamriel_date["guild_day"],
            "gregorian_date": datetime.now().strftime("%Y-%m-%d"),
        }

    def _calculate_tamriel_date(self, earth_date: datetime) -> dict:
        """Calculate Tamrielic date from Earth date."""
        
        # Tamriel months (12 months, varying days)
        tamriel_months = [
            ("Morning Star", 31),    # January
            ("Sun's Dawn", 28),      # February
            ("First Seed", 31),      # March
            ("Rain's Hand", 30),     # April
            ("Second Seed", 31),     # May
            ("Mid Year", 30),        # June
            ("Sun's Height", 31),    # July
            ("Last Seed", 31),       # August
            ("Hearthfire", 30),      # September
            ("Frostfall", 31),       # October
            ("Sun's Dusk", 30),      # November
            ("Evening Star", 31)     # December
        ]
        
        # Tamriel weekdays
        tamriel_weekdays = [
            "Morndas",    # Monday
            "Tirdas",     # Tuesday
            "Middas",     # Wednesday
            "Turdas",     # Thursday
            "Fredas",     # Friday
            "Loredas",    # Saturday
            "Sundas"      # Sunday
        ]
        
        # Birthsigns (Zodiac)
        birthsigns = [
            "The Ritual",        # January
            "The Lover",         # February
            "The Lord",          # March
            "The Mage",          # April
            "The Shadow",        # May
            "The Steed",         # June
            "The Apprentice",    # July
            "The Warrior",       # August
            "The Lady",          # September
            "The Tower",         # October
            "The Atronach",      # November
            "The Thief"          # December
        ]
        
        # Calculate Tamrielic Era and Year
        # 4E 201 is when Skyrim takes place (2011 Earth year)
        # So 2011 = 4E 201
        years_since_2011 = earth_date.year - 2011
        tamriel_year = 201 + years_since_2011
        
        # Determine Era
        if tamriel_year <= 433:
            era = "4E"  # Fourth Era
            era_name = "Fourth Era"
        else:
            # After 4E 433, we'll say Fifth Era begins
            era = "5E"
            era_name = "Fifth Era"
            tamriel_year = tamriel_year - 433
        
        # Get month and day
        month_index = earth_date.month - 1
        tamriel_month, _ = tamriel_months[month_index]
        tamriel_day = earth_date.day
        
        # Get weekday
        weekday_index = earth_date.weekday()
        tamriel_weekday = tamriel_weekdays[weekday_index]
        
        # Get birthsign
        birthsign = birthsigns[month_index]
        
        # Determine season
        if earth_date.month in [12, 1, 2]:
            season = "Winter"
        elif earth_date.month in [3, 4, 5]:
            season = "Spring"
        elif earth_date.month in [6, 7, 8]:
            season = "Summer"
        else:
            season = "Autumn"
        
        # Check for Tamrielic holidays
        holiday = self._get_tamriel_holiday(earth_date.month, earth_date.day)
        
        # Divine blessing (cycles through the Nine Divines)
        divines = [
            "Akatosh", "Arkay", "Dibella", "Julianos", 
            "Kynareth", "Mara", "Stendarr", "Talos", "Zenithar"
        ]
        divine_index = (earth_date.day - 1) % 9
        divine_blessing = divines[divine_index]
        
        # Daedric Prince summon days
        daedric_prince = self._get_daedric_summoning_day(earth_date.month, earth_date.day)
        
        # Masser (larger moon) - 24 day cycle
        masser_phase = self._get_moon_phase(earth_date.day % 24, 24)
        
        # Secunda (smaller moon) - 32 day cycle  
        secunda_phase = self._get_moon_phase(earth_date.day % 32, 32)
        
        # Time period descriptions
        hour = earth_date.hour
        if 5 <= hour < 8:
            time_period = "Dawn - The stars fade"
        elif 8 <= hour < 12:
            time_period = "Morning - Work begins"
        elif 12 <= hour < 17:
            time_period = "Afternoon - Sun at its peak"
        elif 17 <= hour < 20:
            time_period = "Dusk - Shadows lengthen"
        elif 20 <= hour < 24:
            time_period = "Night - Masser and Secunda rise"
        else:
            time_period = "Witching Hour - Daedra are strongest"
        
        # Guild activities by day
        guild_days = {
            "Morndas": "Mages Guild studies",
            "Tirdas": "Fighters Guild training",
            "Middas": "Merchants' market day",
            "Turdas": "Thieves Guild planning",
            "Fredas": "Temple prayers",
            "Loredas": "Dark Brotherhood contracts",
            "Sundas": "Day of rest and worship"
        }
        guild_day = guild_days.get(tamriel_weekday, "")
        
        return {
            "era": era,
            "year": tamriel_year,
            "month": tamriel_month,
            "day": tamriel_day,
            "weekday": tamriel_weekday,
            "birthsign": birthsign,
            "season": season,
            "holiday": holiday,
            "divine_blessing": divine_blessing,
            "daedric_prince": daedric_prince,
            "moon_phase_masser": masser_phase,
            "moon_phase_secunda": secunda_phase,
            "time_period": time_period,
            "guild_day": guild_day,
        }
    
    def _get_tamriel_holiday(self, month: int, day: int) -> str:
        """Get Tamrielic holiday for given date."""
        holidays = {
            (1, 1): "🎊 New Life Festival",
            (1, 15): "🏔️ South Wind's Prayer",
            (1, 16): "📚 Day of Lights",
            (2, 5): "⚔️ Othroktide",
            (2, 16): "💕 Heart's Day",
            (3, 7): "🌱 First Planting",
            (3, 21): "🏛️ Hogithum",
            (4, 1): "🤡 Jester's Day",
            (4, 28): "🌸 Day of Shame",
            (5, 7): "🌾 Second Planting",
            (5, 30): "🔥 Fire Festival",
            (6, 16): "🏪 Mid Year Celebration",
            (6, 24): "⚡ Tibedetha",
            (7, 10): "🛍️ Merchants' Festival",
            (7, 12): "🗡️ Divad Etep't",
            (8, 21): "🍃 Harvest's End",
            (9, 8): "⚒️ Tales and Tallows",
            (10, 13): "👻 Witches' Festival",
            (10, 30): "🦴 Old Life Festival",
            (11, 18): "🛡️ Warriors' Festival",
            (11, 20): "🐺 Moon Festival",
            (12, 15): "🌟 North Wind's Prayer",
            (12, 31): "🎭 Saturalia"
        }
        return holidays.get((month, day), "")
    
    def _get_daedric_summoning_day(self, month: int, day: int) -> str:
        """Get Daedric Prince summoning day."""
        daedric_days = {
            (1, 1): "🌙 Sheogorath",
            (1, 13): "⚔️ Mehrunes Dagon",
            (2, 13): "🕷️ Sanguine",
            (3, 5): "📖 Hermaeus Mora",
            (3, 21): "🌑 Namira",
            (4, 9): "🦌 Hircine",
            (5, 9): "💎 Clavicus Vile",
            (6, 5): "🕸️ Peryite",
            (7, 10): "☠️ Vaermina",
            (8, 8): "🔮 Azura",
            (9, 19): "⚖️ Meridia",
            (10, 13): "🔥 Boethiah",
            (11, 8): "🗿 Malacath",
            (11, 20): "🕷️ Mephala",
            (12, 20): "🌑 Nocturnal",
            (12, 31): "⚔️ Molag Bal"
        }
        return daedric_days.get((month, day), "")
    
    def _get_moon_phase(self, day_in_cycle: int, cycle_length: int) -> str:
        """Calculate moon phase."""
        phase_portion = day_in_cycle / cycle_length
        
        if phase_portion < 0.125:
            return "New Moon"
        elif phase_portion < 0.25:
            return "Waxing Crescent"
        elif phase_portion < 0.375:
            return "First Quarter"
        elif phase_portion < 0.5:
            return "Waxing Gibbous"
        elif phase_portion < 0.625:
            return "Full Moon"
        elif phase_portion < 0.75:
            return "Waning Gibbous"
        elif phase_portion < 0.875:
            return "Last Quarter"
        else:
            return "Waning Crescent"

    def update(self) -> None:
        """Update the sensor."""
        tamriel_date = self._calculate_tamriel_date(datetime.now())
        
        # Format: Era Year, Month Day (Weekday)
        # Example: "4E 225, Morning Star 16 (Tirdas)"
        self._state = f"{tamriel_date['era']} {tamriel_date['year']}, {tamriel_date['month']} {tamriel_date['day']}"