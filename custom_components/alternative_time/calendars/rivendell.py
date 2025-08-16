"""Rivendell Calendar (Elven/Imladris) implementation."""
from __future__ import annotations

from datetime import datetime
import logging
import math

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)


class RivendellCalendarSensor(SensorEntity):
    """Sensor for displaying Rivendell/Elven Calendar from Middle-earth."""

    def __init__(self, base_name: str) -> None:
        """Initialize the Rivendell calendar sensor."""
        self._attr_name = f"{base_name} Rivendell Calendar"
        self._attr_unique_id = f"{base_name}_rivendell_calendar"
        self._attr_icon = "mdi:forest"
        self._state = None

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        elven_date = self._calculate_elven_date(datetime.now())
        
        return {
            "elven_year": elven_date["year"],
            "yén": elven_date["yen"],
            "loa": elven_date["loa"],
            "season": elven_date["season"],
            "season_quenya": elven_date["season_quenya"],
            "day_in_season": elven_date["day_in_season"],
            "day_name": elven_date["day_name"],
            "day_name_quenya": elven_date["day_name_quenya"],
            "special_day": elven_date["special_day"],
            "moon_phase_sindarin": elven_date["moon_phase_sindarin"],
            "star_sign": elven_date["star_sign"],
            "time_of_day_quenya": elven_date["time_of_day_quenya"],
            "age": elven_date["age"],
            "gregorian_date": datetime.now().strftime("%Y-%m-%d"),
        }

    def _calculate_elven_date(self, earth_date: datetime) -> dict:
        """Calculate Elven Calendar date from Earth date."""
        
        # Elven calendar has 6 seasons of varying length
        # A yén (Elven long-year) = 144 solar years
        # A loa (Elven year) = 365 days (or 366 in leap years)
        
        # Calculate years from a reference point
        # Using year 2000 as the start of the Fourth Age
        years_since_2000 = earth_date.year - 2000
        fourth_age_year = 1 + years_since_2000
        
        # Calculate yén (144-year cycle)
        yen = (fourth_age_year - 1) // 144 + 1
        loa = (fourth_age_year - 1) % 144 + 1
        
        # Elven seasons with Quenya names
        # The Elven calendar starts with Spring (March 20)
        day_of_year = earth_date.timetuple().tm_yday
        
        # Adjust for calendar starting on March 20
        if earth_date.month < 3 or (earth_date.month == 3 and earth_date.day < 20):
            # Still in previous Elven year
            day_of_year = day_of_year + 365 - 79  # 79 days from Mar 20 to Jan 1
        else:
            day_of_year = day_of_year - 79
        
        # Elven seasons
        if day_of_year <= 0:
            day_of_year += 365
        
        if day_of_year <= 54:
            season = "Spring"
            season_quenya = "Tuilë"
            day_in_season = day_of_year
            season_emoji = "🌸"
        elif day_of_year <= 54 + 72:
            season = "Summer"
            season_quenya = "Lairë"
            day_in_season = day_of_year - 54
            season_emoji = "☀️"
        elif day_of_year <= 54 + 72 + 54:
            season = "Autumn"
            season_quenya = "Yávië"
            day_in_season = day_of_year - 126
            season_emoji = "🍂"
        elif day_of_year <= 54 + 72 + 54 + 72:
            season = "Fading"
            season_quenya = "Quellë"
            day_in_season = day_of_year - 180
            season_emoji = "🍃"
        elif day_of_year <= 54 + 72 + 54 + 72 + 72:
            season = "Winter"
            season_quenya = "Hrívë"
            day_in_season = day_of_year - 252
            season_emoji = "❄️"
        else:
            season = "Stirring"
            season_quenya = "Coirë"
            day_in_season = day_of_year - 324
            season_emoji = "🌱"
        
        # Elven day names (6-day week)
        elven_days = [
            ("Elenya", "Stars-day"),
            ("Anarya", "Sun-day"),
            ("Isilya", "Moon-day"),
            ("Aldúya", "Two Trees-day"),
            ("Menelya", "Heavens-day"),
            ("Valanya", "Valar-day")
        ]
        
        day_index = earth_date.weekday() % 6
        day_name_quenya, day_name = elven_days[day_index]
        
        # Special Elven days
        special_day = ""
        if earth_date.month == 3 and earth_date.day == 20:
            special_day = "🌅 Yestarë - First Day of the Year"
        elif earth_date.month == 3 and earth_date.day == 25:
            special_day = "🌟 Lady Day - Elven New Year"
        elif earth_date.month == 6 and earth_date.day == 21:
            special_day = "☀️ Loëndë - Mid-year's Day"
        elif earth_date.month == 9 and earth_date.day == 22:
            special_day = "🍂 Yáviérë - Harvest Festival"
        elif earth_date.month == 12 and earth_date.day == 21:
            special_day = "⭐ Mettarë - Last Day of the Year"
        elif earth_date.month == 9 and earth_date.day == 29:
            special_day = "🌙 Durin's Day" if self._is_durins_day(earth_date) else ""
        
        # Moon phases in Sindarin
        day_in_lunar = earth_date.day % 29.5
        if day_in_lunar < 2:
            moon_phase = "Ithil Dú"  # Dark Moon
        elif day_in_lunar < 7:
            moon_phase = "Ithil Orthad"  # Rising Moon
        elif day_in_lunar < 9:
            moon_phase = "Ithil Perian"  # Half Moon
        elif day_in_lunar < 14:
            moon_phase = "Ithil Síla"  # Bright Moon
        elif day_in_lunar < 16:
            moon_phase = "Ithil Pennas"  # Full Moon
        elif day_in_lunar < 21:
            moon_phase = "Ithil Dant"  # Falling Moon
        elif day_in_lunar < 23:
            moon_phase = "Ithil Harn"  # Wounded Moon
        else:
            moon_phase = "Ithil Fuin"  # Shadow Moon
        
        # Elven star signs (constellations)
        star_signs = [
            "Menelmacar (Orion)",
            "Valacirca (Great Bear)",
            "Wilwarin (Butterfly)",
            "Telumendil (Lover of the Heavens)",
            "Soronúmë (Eagle)",
            "Anarríma (Sun-border)",
            "Gil-galad (Star of Radiance)",
            "Elemmírë (Star-jewel)",
            "Helluin (Sirius)",
            "Carnil (Red Star)",
            "Luinil (Blue Star)",
            "Nénar (Water Star)"
        ]
        star_sign = star_signs[earth_date.month - 1]
        
        # Time of day in Quenya
        hour = earth_date.hour
        if 5 <= hour < 7:
            time_quenya = "Tindómë - Dawn Twilight"
        elif 7 <= hour < 9:
            time_quenya = "Ára - Dawn"
        elif 9 <= hour < 12:
            time_quenya = "Arië - Morning"
        elif 12 <= hour < 15:
            time_quenya = "Endë - Midday"
        elif 15 <= hour < 17:
            time_quenya = "Undómë - Afternoon"
        elif 17 <= hour < 19:
            time_quenya = "Andúnë - Sunset"
        elif 19 <= hour < 21:
            time_quenya = "Lómë - Dusk"
        elif 21 <= hour < 23:
            time_quenya = "Dú - Night"
        else:
            time_quenya = "Fuin - Deep Night"
        
        # Age of Middle-earth
        age = "Fourth Age" if years_since_2000 >= 0 else "Third Age"
        
        return {
            "year": fourth_age_year,
            "yen": yen,
            "loa": loa,
            "season": season,
            "season_quenya": season_quenya,
            "day_in_season": day_in_season,
            "day_name": day_name,
            "day_name_quenya": day_name_quenya,
            "special_day": special_day,
            "moon_phase_sindarin": moon_phase,
            "star_sign": star_sign,
            "time_of_day_quenya": time_quenya,
            "age": age,
        }
    
    def _is_durins_day(self, date: datetime) -> bool:
        """Check if it's Durin's Day (first day of last moon of autumn)."""
        # Durin's Day: When the last moon of autumn and the sun are in the sky together
        # This happens when there's a new moon in late October/early November
        # Simplified check
        if date.month == 10 and 20 <= date.day <= 31:
            # Check if near new moon
            day_in_lunar = date.day % 29.5
            return day_in_lunar < 2
        return False

    def update(self) -> None:
        """Update the sensor."""
        elven_date = self._calculate_elven_date(datetime.now())
        
        # Format: F.A. Year, Season Day (Elven Day)
        # Example: "F.A. 24, Tuilë 35 (Elenya)"
        self._state = f"F.A. {elven_date['year']}, {elven_date['season_quenya']} {elven_date['day_in_season']}"