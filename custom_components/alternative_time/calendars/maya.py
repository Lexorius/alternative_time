"""Maya Calendar implementation."""
from __future__ import annotations

from datetime import datetime, timedelta

from .base import AlternativeTimeSensorBase


class MayaCalendarSensor(AlternativeTimeSensorBase):
    """Sensor for displaying Maya Calendar."""

    def __init__(self, base_name: str) -> None:
        """Initialize the Maya calendar sensor."""
        super().__init__(base_name, "maya_calendar", "Maya Calendar")
        self._attr_icon = "mdi:pyramid"
        self._update_interval = timedelta(hours=1)  # Update every hour
        
        # Tzolk'in day names (20-day cycle)
        self.tzolkin_day_names = [
            "Imix", "Ik", "Akbal", "Kan", "Chicchan", 
            "Cimi", "Manik", "Lamat", "Muluc", "Oc", 
            "Chuen", "Eb", "Ben", "Ix", "Men", 
            "Cib", "Caban", "Etznab", "Cauac", "Ahau"
        ]
        
        # Haab month names (365-day solar calendar)
        self.haab_months = [
            "Pop", "Uo", "Zip", "Zotz", "Tzec", 
            "Xul", "Yaxkin", "Mol", "Chen", "Yax", 
            "Zac", "Ceh", "Mac", "Kankin", "Muan", 
            "Pax", "Kayab", "Cumku", "Uayeb"  # Uayeb is only 5 days
        ]

    def calculate_time(self) -> str:
        """Calculate current Maya Calendar date.
        
        The Maya calendar system consists of three main components:
        
        1. Long Count: A linear count of days in Maya units
           - Kin = 1 day
           - Uinal = 20 kin (20 days)
           - Tun = 18 uinal (360 days)
           - Katun = 20 tun (7,200 days)
           - Baktun = 20 katun (144,000 days)
           
        2. Tzolk'in: 260-day sacred calendar
           - Combines 13 numbers with 20 day names
           - Used for religious and ceremonial purposes
           
        3. Haab: 365-day solar calendar
           - 18 months of 20 days + 1 month of 5 days (Uayeb)
           - Used for agricultural and civil purposes
           
        Correlation: Using GMT correlation (584283)
        December 21, 2012 = 13.0.0.0.0 (end of 13th baktun)
        
        Format: B.K.T.U.K | TZ TN | HD HM
        Example: 13.0.12.1.15 | 8 Ahau | 3 Pop
        """
        now = datetime.now()
        
        # Using December 21, 2012 as reference (13.0.0.0.0 in Maya Long Count)
        # This is a well-known date in Maya calendar (end of 13th baktun)
        reference_date = datetime(2012, 12, 21)
        days_since_reference = (now - reference_date).days
        
        # Calculate Long Count components
        # Working backwards from the reference date
        total_days = days_since_reference
        
        # Each unit in the Long Count
        kin = total_days % 20
        uinal = (total_days // 20) % 18
        tun = (total_days // 360) % 20
        katun = (total_days // 7200) % 20
        baktun = 13 + (total_days // 144000)  # Starting from baktun 13
        
        # Calculate Tzolk'in (260-day cycle)
        # The Tzolk'in combines a 13-day number cycle with 20 day names
        # December 21, 2012 was 4 Ahau (4th day, 20th name)
        tzolkin_day_number = ((days_since_reference + 4 - 1) % 13) + 1
        tzolkin_day_name_index = (days_since_reference + 19) % 20  # Ahau is index 19
        tzolkin_day_name = self.tzolkin_day_names[tzolkin_day_name_index]
        
        # Calculate Haab (365-day cycle)
        # December 21, 2012 was 3 Kankin (3rd day of Kankin month)
        # Kankin is the 14th month (index 13), starts at day 241
        haab_reference = 243 + 3  # Day 3 of Kankin
        haab_day_total = (haab_reference + days_since_reference) % 365
        
        # Determine month and day
        if haab_day_total < 360:  # First 18 months (20 days each)
            haab_month_index = haab_day_total // 20
            haab_day_of_month = haab_day_total % 20
        else:  # Uayeb (5-day month)
            haab_month_index = 18
            haab_day_of_month = haab_day_total - 360
        
        haab_month = self.haab_months[haab_month_index]
        
        # Format: Long Count | Tzolk'in | Haab
        return f"{baktun}.{katun}.{tun}.{uinal}.{kin} | {tzolkin_day_number} {tzolkin_day_name} | {haab_day_of_month} {haab_month}"