"""Shire Calendar (Hobbit/LOTR) implementation."""
from __future__ import annotations

from datetime import datetime
import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)


class ShireCalendarSensor(SensorEntity):
    """Sensor for displaying Shire Calendar from Middle-earth."""

    def __init__(self, base_name: str) -> None:
        """Initialize the Shire calendar sensor."""
        self._attr_name = f"{base_name} Shire Calendar"
        self._attr_unique_id = f"{base_name}_shire_calendar"
        self._attr_icon = "mdi:pipe"
        self._state = None

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        shire_date = self._calculate_shire_date(datetime.now())
        
        return {
            "shire_year": shire_date["year"],
            "month": shire_date["month"],
            "day": shire_date["day"],
            "weekday": shire_date["weekday"],
            "season": shire_date["season"],
            "special_day": shire_date["special_day"],
            "meal_time": shire_date["meal_time"],
            "moon_phase": shire_date["moon_phase"],
            "gregorian_date": datetime.now().strftime("%Y-%m-%d"),
            "time_of_day": shire_date["time_of_day"],
            "hobbit_name_day": shire_date["hobbit_name_day"],
        }

    def _calculate_shire_date(self, earth_date: datetime) -> dict:
        """Calculate Shire Reckoning date from Earth date."""
        
        # The Shire Calendar has 12 months of 30 days each, plus special days
        # Year starts at Yule (around December 21)
        
        # Shire months
        shire_months = [
            "Afteryule",    # January
            "Solmath",      # February  
            "Rethe",        # March
            "Astron",       # April
            "Thrimidge",    # May
            "Forelithe",    # June
            "Afterlithe",   # July
            "Wedmath",      # August
            "Halimath",     # September
            "Winterfilth",  # October
            "Blotmath",     # November
            "Foreyule"      # December
        ]
        
        # Shire weekdays (7-day week)
        shire_weekdays = [
            "Sterday",   # Saturday (Stars)
            "Sunday",    # Sunday (Sun)
            "Monday",    # Monday (Moon)
            "Trewsday",  # Tuesday (Trees)
            "Hevensday", # Wednesday (Heavens)
            "Mersday",   # Thursday (Sea)
            "Highday"    # Friday (High day)
        ]
        
        # Convert to Shire calendar
        # Using a simplified conversion where current year maps to Fourth Age
        # The Lord of the Rings ends in T.A. 3021 = S.R. 1421
        # We'll consider year 2000 as S.R. 1600 for fun
        shire_year = 1600 + (earth_date.year - 2000)
        
        # Map Earth months to Shire months (simplified)
        month_index = earth_date.month - 1
        shire_month = shire_months[month_index]
        
        # Shire day (1-30 for regular days)
        shire_day = min(earth_date.day, 30)
        
        # Weekday
        weekday_index = earth_date.weekday()
        # Shift to make Sterday = Saturday
        weekday_index = (weekday_index + 2) % 7
        shire_weekday = shire_weekdays[weekday_index]
        
        # Determine season
        if earth_date.month in [12, 1, 2]:
            season = "Yule-tide"
        elif earth_date.month in [3, 4, 5]:
            season = "Spring"
        elif earth_date.month in [6, 7, 8]:
            season = "Summer"
        else:
            season = "Harvest"
        
        # Check for special Shire days
        special_day = ""
        if earth_date.month == 1 and earth_date.day == 1:
            special_day = "🎊 2 Yule - New Year's Day"
        elif earth_date.month == 3 and earth_date.day == 25:
            special_day = "🌸 Elven New Year"
        elif earth_date.month == 6 and earth_date.day == 21:
            special_day = "☀️ 1 Lithe - Midsummer's Eve"
        elif earth_date.month == 6 and earth_date.day == 22:
            special_day = "🎉 Mid-year's Day"
        elif earth_date.month == 9 and earth_date.day == 22:
            special_day = "🎂 Bilbo & Frodo's Birthday!"
        elif earth_date.month == 12 and earth_date.day == 21:
            special_day = "❄️ 1 Yule - Midwinter"
        
        # Hobbit meal times
        hour = earth_date.hour
        if 6 <= hour < 8:
            meal_time = "🍳 First Breakfast"
        elif 8 <= hour < 9:
            meal_time = "🥐 Second Breakfast"
        elif 11 <= hour < 12:
            meal_time = "☕ Elevenses"
        elif 12 <= hour < 14:
            meal_time = "🍽️ Luncheon"
        elif 15 <= hour < 16:
            meal_time = "🫖 Afternoon Tea"
        elif 18 <= hour < 20:
            meal_time = "🍖 Dinner"
        elif 20 <= hour < 22:
            meal_time = "🍷 Supper"
        else:
            meal_time = "🌙 Resting Time"
        
        # Time of day descriptions (Hobbit style)
        if 5 <= hour < 7:
            time_of_day = "Dawn - The Shire awakens"
        elif 7 <= hour < 12:
            time_of_day = "Morning - Time for adventures"
        elif 12 <= hour < 17:
            time_of_day = "Afternoon - Pleasant walking weather"
        elif 17 <= hour < 20:
            time_of_day = "Evening - Smoke rings and tales"
        elif 20 <= hour < 23:
            time_of_day = "Night - Stars are out"
        else:
            time_of_day = "Late Night - All respectable hobbits abed"
        
        # Moon phases (simplified)
        day_in_lunar = earth_date.day % 29.5
        if day_in_lunar < 2:
            moon_phase = "🌑 New Moon"
        elif day_in_lunar < 7:
            moon_phase = "🌒 Waxing Crescent"
        elif day_in_lunar < 9:
            moon_phase = "🌓 First Quarter"
        elif day_in_lunar < 14:
            moon_phase = "🌔 Waxing Gibbous"
        elif day_in_lunar < 16:
            moon_phase = "🌕 Full Moon"
        elif day_in_lunar < 21:
            moon_phase = "🌖 Waning Gibbous"
        elif day_in_lunar < 23:
            moon_phase = "🌗 Last Quarter"
        else:
            moon_phase = "🌘 Waning Crescent"
        
        # Hobbit name days (some important hobbit family names)
        name_days = {
            1: "Baggins", 5: "Took", 10: "Brandybuck", 
            15: "Gamgee", 20: "Cotton", 25: "Proudfoot", 30: "Bracegirdle"
        }
        hobbit_name_day = name_days.get(shire_day, "")
        
        return {
            "year": shire_year,
            "month": shire_month,
            "day": shire_day,
            "weekday": shire_weekday,
            "season": season,
            "special_day": special_day,
            "meal_time": meal_time,
            "moon_phase": moon_phase,
            "time_of_day": time_of_day,
            "hobbit_name_day": hobbit_name_day,
        }

    def update(self) -> None:
        """Update the sensor."""
        shire_date = self._calculate_shire_date(datetime.now())
        
        # Format: S.R. YYYY, Month Day (Weekday)
        # Example: "S.R. 1624, Afteryule 16 (Trewsday)"
        self._state = f"S.R. {shire_date['year']}, {shire_date['month']} {shire_date['day']}"