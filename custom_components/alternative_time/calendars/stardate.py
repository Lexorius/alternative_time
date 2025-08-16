"""Star Trek Stardate implementation."""
from __future__ import annotations

from datetime import datetime, timedelta

from .base import AlternativeTimeSensorBase


class StardateSensor(AlternativeTimeSensorBase):
    """Sensor for displaying Stardate (Star Trek style)."""

    def __init__(self, base_name: str) -> None:
        """Initialize the stardate sensor."""
        super().__init__(base_name, "stardate", "Stardate")
        self._attr_icon = "mdi:star-four-points"
        self._update_interval = timedelta(seconds=10)  # Update every 10 seconds

    def calculate_time(self) -> str:
        """Calculate current Stardate."""
        now = datetime.now()
        base_year = 2323
        current_year = now.year
        day_of_year = now.timetuple().tm_yday
        
        # TNG-style stardate calculation
        stardate = 1000 * (current_year - base_year) + (1000 * day_of_year / 365.25)
        stardate += (now.hour * 60 + now.minute) / 1440 * 10
        
        return f"{stardate:.2f}"