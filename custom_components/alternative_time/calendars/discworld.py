"""Discworld Calendar (Terry Pratchett) implementation."""
from __future__ import annotations

from datetime import datetime, timedelta

from .base import AlternativeTimeSensorBase


class DiscworldCalendarSensor(AlternativeTimeSensorBase):
    """Sensor for displaying Discworld Calendar (Terry Pratchett)."""

    def __init__(self, base_name: str) -> None:
        """Initialize the Discworld calendar sensor."""
        super().__init__(base_name, "discworld", "Discworld Calendar")
        self._attr_icon = "mdi:turtle"
        self._update_interval = timedelta(hours=1)
        
        # Discworld months (13 months + special days)
        self.discworld_months = [
            ("Ick", "❄️"),           # January (Winter)
            ("Offle", "❄️"),         # February
            ("February", "🌨️"),      # Yes, February (Pratchett humor)
            ("March", "🌬️"),         # March
            ("April", "🌧️"),         # April
            ("May", "🌸"),           # May
            ("June", "☀️"),          # June
            ("Grune", "🌿"),         # July (Summer)
            ("August", "🌞"),        # August
            ("Spune", "🍂"),         # September
            ("Sektober", "🍺"),      # October (drinking month)
            ("Ember", "🔥"),         # November
            ("December", "⭐")       # December
        ]
        
        # Discworld weekdays (8 days)
        self.discworld_days = [
            "Sunday", "Monday", "Tuesday", "Wednesday",
            "Thursday", "Friday", "Saturday", "Octeday"
        ]
        
        # Guilds of Ankh-Morpork (for daily influence)
        self.guilds = [
            "Assassins' Guild", "Thieves' Guild", "Seamstresses' Guild",
            "Beggars' Guild", "Merchants' Guild", "Alchemists' Guild",
            "Wizards (Unseen University)", "Watch (City Guard)",
            "Fools' Guild", "Musicians' Guild"
        ]
        
        # Special Discworld events/holidays
        self.discworld_events = {
            (1, 1): "Hogswatchday 🎅",
            (2, 14): "Day of Small Gods",
            (3, 25): "The Rag Week",
            (4, 1): "All Fools' Day",
            (4, 32): "Day That Never Happens",  # Discworld joke
            (5, 1): "May Day",
            (5, 25): "Glorious Revolution Day",
            (6, 21): "Midsummer's Eve",
            (7, 15): "Patrician's Birthday",
            (8, 12): "Thieves' Guild Day",
            (9, 9): "Mrs. Cake Day",
            (10, 31): "Soul Cake Night 🎃",
            (11, 11): "Elevenses Day",
            (12, 32): "Hogswatch Eve"  # Another impossible day
        }
        
        # Death's appearances (random quotes)
        self.death_quotes = [
            "THERE IS NO JUSTICE. THERE IS JUST ME.",
            "I COULD MURDER A CURRY.",
            "CATS. CATS ARE NICE.",
            "SQUEAK.",  # Death of Rats
            "THE DUTY IS MINE.",
            "WHAT CAN THE HARVEST HOPE FOR, IF NOT FOR THE CARE OF THE REAPER MAN?"
        ]
        
        # Ankh-Morpork city areas
        self.city_areas = [
            "The Shades", "Patrician's Palace", "Unseen University",
            "The Docks", "Treacle Mine Road", "Cable Street",
            "The Hippo", "Isle of Gods", "Pseudopolis Yard"
        ]

    def calculate_time(self) -> str:
        """Calculate current Discworld Calendar date."""
        now = datetime.now()
        
        # Discworld year (Century of the Fruitbat, etc.)
        # Let's use "Century of the Anchovy" as current
        year_since_2000 = now.year - 2000
        discworld_year = 1 + year_since_2000  # Year 1 of Century of the Anchovy = 2000
        
        # Get month and day
        month_index = min(now.month - 1, 12)
        day = now.day
        
        # Handle special 32nd days (Discworld has them!)
        if day == 31 and now.month in [4, 12]:
            day = 32  # Discworld logic!
        
        # Get month name
        if month_index < len(self.discworld_months):
            month_name, month_emoji = self.discworld_months[month_index]
        else:
            month_name, month_emoji = "Backspindlemonth", "🌀"  # Extra month
        
        # Calculate weekday (8-day week)
        days_since_epoch = (now - datetime(2000, 1, 1)).days
        weekday_index = days_since_epoch % 8
        discworld_weekday = self.discworld_days[weekday_index]
        
        # Check for events
        event = self.discworld_events.get((now.month, day), "")
        event_str = f" | {event}" if event else ""
        
        # Guild influence (rotates daily)
        guild_index = days_since_epoch % len(self.guilds)
        guild_influence = self.guilds[guild_index]
        
        # Random Death quote (changes daily)
        death_index = days_since_epoch % len(self.death_quotes)
        death_says = self.death_quotes[death_index]
        
        # City location (changes hourly)
        location_index = (days_since_epoch + now.hour) % len(self.city_areas)
        current_location = self.city_areas[location_index]
        
        # Time of day (Discworld style)
        hour = now.hour
        if 0 <= hour < 3:
            time_desc = "🌙 Dead of Night (Graveyard Shift)"
        elif 3 <= hour < 6:
            time_desc = "⭐ Small Hours (Thieves' Time)"
        elif 6 <= hour < 9:
            time_desc = "🌅 Dawn (Milkmen About)"
        elif 9 <= hour < 12:
            time_desc = "☀️ Morning (Shops Open)"
        elif 12 <= hour < 13:
            time_desc = "🍽️ Noon (Lunch at Harga's)"
        elif 13 <= hour < 17:
            time_desc = "🌤️ Afternoon (Siesta Time)"
        elif 17 <= hour < 19:
            time_desc = "🍺 Evening (Pub O'Clock)"
        elif 19 <= hour < 21:
            time_desc = "🌆 Dusk (Theatre Time)"
        elif 21 <= hour < 24:
            time_desc = "🌃 Night (Watch Patrol)"
        else:
            time_desc = "⏰ Temporal Anomaly"
        
        # L-Space probability (libraries connect)
        l_space = "📚 L-Space detected!" if hour == 3 and now.minute == 33 else ""
        
        # Special Octeday message
        octeday_msg = " | 🎉 It's Octeday!" if weekday_index == 7 else ""
        
        # Format output
        base_str = f"Century of the Anchovy, UC {discworld_year}, {day} {month_name} ({discworld_weekday}){octeday_msg} | {time_desc} | 📍 {current_location} | {guild_influence}{event_str}"
        
        # Add Death quote occasionally (at midnight)
        if hour == 0:
            base_str += f"\n💀 Death says: {death_says}"
        
        # Add L-Space notification
        if l_space:
            base_str += f"\n{l_space}"
        
        return base_str