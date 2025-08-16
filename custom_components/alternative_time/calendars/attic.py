"""Attic Calendar (Ancient Athens) implementation."""
from __future__ import annotations

from datetime import datetime, timedelta

from .base import AlternativeTimeSensorBase


class AtticCalendarSensor(AlternativeTimeSensorBase):
    """Sensor for displaying Attic Calendar (Ancient Athens)."""

    def __init__(self, base_name: str) -> None:
        """Initialize the Attic calendar sensor."""
        super().__init__(base_name, "attic_calendar", "Attic Calendar")
        self._attr_icon = "mdi:pillar"
        self._update_interval = timedelta(hours=1)
        
        # Attic months (lunisolar calendar)
        self.attic_months = [
            "Hekatombaion",  # July/August - Month of hundred oxen
            "Metageitnion",  # August/September - Month of changing neighbors
            "Boedromion",    # September/October - Month of running for help
            "Pyanepsion",    # October/November - Bean-stewing month
            "Maimakterion",  # November/December - Month of storms
            "Poseideon",     # December/January - Poseidon's month
            "Gamelion",      # January/February - Wedding month
            "Anthesterion",  # February/March - Flower month
            "Elaphebolion",  # March/April - Deer-hunting month
            "Mounichion",    # April/May - Month of Mounichia festival
            "Thargelion",    # May/June - Month of Thargelia festival
            "Skirophorion"   # June/July - Month of parasol-bearing
        ]
        
        # Attic day periods (dekads - 10-day periods)
        self.dekad_periods = [
            "ἱσταμένου",  # histamenou - waxing moon (days 1-10)
            "μεσοῦντος",  # mesountos - middle (days 11-20)
            "φθίνοντος"   # phthinontos - waning (days 21-29/30)
        ]
        
        # Sample Archons (chief magistrates) - rotating list
        self.archons = [
            "Nikias", "Kallias", "Kritias", "Alkibiades", 
            "Kleisthenes", "Perikles", "Themistokles", "Solon"
        ]

    def calculate_time(self) -> str:
        """Calculate current Attic Calendar date.
        
        The Attic calendar was the lunisolar calendar of ancient Athens:
        
        Structure:
        - 12 lunar months of 29-30 days (alternating hollow/full months)
        - Year began at first new moon after summer solstice
        - Months divided into three dekads (10-day periods)
        - Intercalary months added to align with solar year
        
        Day counting:
        - Days 1-10: "of the waxing moon" (counted forward)
        - Days 11-20: "of the middle" (counted forward)
        - Days 21-29/30: "of the waning moon" (counted backward!)
        
        Dating formula: Day + Period + Month + Archon + Olympiad
        
        Note: This is a simplified approximation. The actual Attic calendar
        was complex with irregular intercalations and local variations.
        
        Format: Day Period Month | Archon | Ol.XXX.Y
        Example: 5 ἱσταμένου Hekatombaion | Nikias | Ol.700.2
        """
        now = datetime.now()
        
        # Simplified calculation - actual Attic calendar was lunisolar
        # We approximate by starting the year around July (summer solstice)
        days_since_summer_solstice = (now.timetuple().tm_yday - 172) % 365
        
        # Calculate month (approximately 30 days each)
        month_index = min(days_since_summer_solstice // 30, 11)
        day_in_month = (days_since_summer_solstice % 30) + 1
        
        # Determine dekad (10-day period) and format day
        if day_in_month <= 10:
            period = self.dekad_periods[0]  # Waxing
            day_display = day_in_month
        elif day_in_month <= 20:
            period = self.dekad_periods[1]  # Middle
            day_display = day_in_month - 10
        else:
            period = self.dekad_periods[2]  # Waning
            # In waning period, days counted backward from end
            days_in_month = 30 if month_index % 2 == 0 else 29  # Alternating full/hollow
            day_display = days_in_month - day_in_month + 1
        
        month_name = self.attic_months[month_index]
        
        # Select archon (chief magistrate) - rotates yearly
        archon = self.archons[now.year % len(self.archons)]
        
        # Calculate Olympiad (4-year cycle)
        # First Olympiad: 776 BCE
        # We use a simplified calculation from current era
        olympiad_number = ((now.year + 776) // 4)
        olympiad_year = ((now.year + 776) % 4) + 1
        
        # Format: Day Period Month | Archon | Olympiad
        return f"{day_display} {period} {month_name} | {archon} | Ol.{olympiad_number}.{olympiad_year}"