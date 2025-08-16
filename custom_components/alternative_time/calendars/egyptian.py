"""Ancient Egyptian Calendar implementation."""
from __future__ import annotations

from datetime import datetime, timedelta

from .base import AlternativeTimeSensorBase


class EgyptianCalendarSensor(AlternativeTimeSensorBase):
    """Sensor for displaying Ancient Egyptian Calendar."""

    def __init__(self, base_name: str) -> None:
        """Initialize the Egyptian calendar sensor."""
        super().__init__(base_name, "egyptian", "Egyptian Calendar")
        self._attr_icon = "mdi:pyramid"
        self._update_interval = timedelta(hours=1)
        
        # Egyptian months (3 seasons, 4 months each)
        self.egyptian_seasons = [
            # Akhet (Inundation/Flood) - When the Nile flooded
            ("Thoth", "𓊖", "Akhet"),       # Month of Thoth (god of wisdom)
            ("Phaophi", "𓊖", "Akhet"),     # Month of Ptah
            ("Athyr", "𓊖", "Akhet"),       # Month of Hathor
            ("Choiak", "𓊖", "Akhet"),      # Month of Ka-Ha-Ka
            # Peret (Emergence/Winter) - When fields emerged from flood
            ("Tybi", "🌱", "Peret"),        # Month of offering
            ("Mechir", "🌱", "Peret"),      # Month of Mekhir
            ("Phamenoth", "🌱", "Peret"),   # Month of Amenhotep
            ("Pharmuthi", "🌱", "Peret"),   # Month of Renenutet
            # Shemu (Harvest/Summer) - Harvest season
            ("Pachons", "☀️", "Shemu"),     # Month of Khonsu
            ("Payni", "☀️", "Shemu"),       # Month of Khenti-khety
            ("Epiphi", "☀️", "Shemu"),      # Month of Ipi
            ("Mesore", "☀️", "Shemu")       # Month of Ra-Horakhty
        ]
        
        # Decan names (10-day weeks)
        self.decan_names = [
            "First Decan", "Second Decan", "Third Decan"
        ]
        
        # Egyptian gods for each month
        self.month_gods = [
            "Thoth",     # God of wisdom and writing
            "Ptah",      # Creator god of Memphis
            "Hathor",    # Goddess of love and joy
            "Sekhmet",   # Goddess of war and healing
            "Min",       # God of fertility
            "Bastet",    # Cat goddess
            "Khnum",     # Creator of human bodies
            "Renenutet", # Goddess of harvest
            "Khonsu",    # Moon god
            "Horus",     # Sky god
            "Isis",      # Mother goddess
            "Ra"         # Sun god
        ]
        
        # Simplified hieroglyphic numbers
        self.hieroglyphs = {
            1: "𓏤", 2: "𓏥", 3: "𓏦", 4: "𓏧", 5: "𓏨",
            6: "𓏩", 7: "𓏪", 8: "𓏫", 9: "𓏬",
            10: "𓎆", 20: "𓎇", 30: "𓎈"
        }
        
        # Egyptian hours (12 day + 12 night)
        self.egyptian_hours = [
            "First Hour", "Second Hour", "Third Hour", "Fourth Hour",
            "Fifth Hour", "Sixth Hour", "Seventh Hour", "Eighth Hour",
            "Ninth Hour", "Tenth Hour", "Eleventh Hour", "Twelfth Hour"
        ]
        
        # Epagomenal days (birthdays of gods)
        self.epagomenal_gods = ["Osiris", "Horus", "Set", "Isis", "Nephthys"]

    def calculate_time(self) -> str:
        """Calculate current Ancient Egyptian Calendar date.
        
        The Egyptian civil calendar was one of the first solar calendars:
        
        Structure:
        - 365 days (no leap year)
        - 12 months of 30 days each
        - 5 epagomenal days ("days upon the year")
        - 3 seasons of 4 months each
        
        Divisions:
        - Each month: 3 decans (10-day weeks)
        - Each day: 24 hours (12 day + 12 night)
        - New Year: Heliacal rising of Sirius (around July 19)
        
        The calendar slowly drifted through the seasons (Sothic cycle)
        because it lacked leap years. A complete cycle took 1,461 years.
        
        Dynasty system: We simulate regnal years and dynasties
        
        Format: Dynasty X Year Y, 𓏤𓏨 Day Month (Season) | Decan | Hour | God | Nile
        Example: Dynasty 1 Year 25, 𓏤𓏨 15 Thoth (Akhet) | Second Decan | ☀️ Sixth Hour | Thoth | 🌊
        """
        now = datetime.now()
        
        # Egyptian new year around July 19 (Sirius rising)
        egyptian_new_year = datetime(now.year, 7, 19)
        if now < egyptian_new_year:
            egyptian_new_year = datetime(now.year - 1, 7, 19)
        
        days_since_new_year = (now - egyptian_new_year).days
        
        # Simulate dynasty and regnal year
        dynasty = (now.year - 2000) // 30 + 1  # New dynasty every 30 years
        regnal_year = ((now.year - 2000) % 30) + 1
        
        # Check for epagomenal days (last 5 days of year)
        if days_since_new_year >= 360:
            epagomenal_day = days_since_new_year - 359
            if epagomenal_day <= 5:
                god_birthday = self.epagomenal_gods[epagomenal_day - 1]
                return f"Dynasty {dynasty}, Year {regnal_year} | Epagomenal Day {epagomenal_day} - Birthday of {god_birthday} 🎉"
            days_since_new_year = days_since_new_year % 365
        
        # Calculate month and day
        month_index = min(days_since_new_year // 30, 11)
        day_of_month = (days_since_new_year % 30) + 1
        
        month_name, season_emoji, season_name = self.egyptian_seasons[month_index]
        patron_god = self.month_gods[month_index]
        
        # Calculate decan (10-day week)
        decan_index = min((day_of_month - 1) // 10, 2)
        decan_name = self.decan_names[decan_index]
        day_in_decan = ((day_of_month - 1) % 10) + 1
        
        # Create hieroglyphic representation of day
        hieroglyph_day = ""
        if day_of_month <= 9:
            hieroglyph_day = self.hieroglyphs.get(day_of_month, str(day_of_month))
        elif day_of_month <= 19:
            hieroglyph_day = self.hieroglyphs[10] + self.hieroglyphs.get(day_of_month - 10, "")
        elif day_of_month <= 29:
            hieroglyph_day = self.hieroglyphs[20] + self.hieroglyphs.get(day_of_month - 20, "")
        else:
            hieroglyph_day = self.hieroglyphs[30]
        
        # Determine Egyptian hour
        hour = now.hour
        is_night = hour < 6 or hour >= 18
        if is_night:
            if hour >= 18:
                egyptian_hour_index = hour - 18
            else:
                egyptian_hour_index = hour + 6
            time_symbol = "🌙"
            time_period = "Night"
        else:
            egyptian_hour_index = hour - 6
            time_symbol = "☀️"
            time_period = "Day"
        
        egyptian_hour = self.egyptian_hours[min(egyptian_hour_index, 11)]
        
        # Nile flood status based on season
        if season_name == "Akhet":
            nile_status = "🌊 Nile Flooding"
        elif season_name == "Peret":
            nile_status = "🌱 Fields Emerging"
        else:
            nile_status = "🌾 Harvest Time"
        
        # Format output
        return f"Dynasty {dynasty} Year {regnal_year}, {hieroglyph_day} {day_of_month} {month_name} ({season_name}) | {decan_name} Day {day_in_decan} | {time_symbol} {egyptian_hour} | {patron_god} | {nile_status}"