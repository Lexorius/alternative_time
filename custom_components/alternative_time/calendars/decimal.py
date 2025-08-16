"""Decimal Time (French Revolutionary Time) implementation."""
from __future__ import annotations

from datetime import datetime, timedelta

from .base import AlternativeTimeSensorBase


class DecimalTimeSensor(AlternativeTimeSensorBase):
    """Sensor for displaying Decimal Time (French Revolutionary)."""

    def __init__(self, base_name: str) -> None:
        """Initialize the decimal time sensor."""
        super().__init__(base_name, "decimal", "Decimal Time")
        self._attr_icon = "mdi:clock-digital"
        self._update_interval = timedelta(seconds=1)  # Update every second

    def calculate_time(self) -> str:
        """Calculate current Decimal Time.
        
        French Revolutionary/Decimal Time divides the day into:
        - 10 decimal hours (1 hour = 2.4 standard hours = 144 minutes)
        - 100 decimal minutes per hour (1 minute = 1.44 standard minutes = 86.4 seconds)
        - 100 decimal seconds per minute (1 second = 0.864 standard seconds)
        
        Total: 10 × 100 × 100 = 100,000 decimal seconds per day
        (vs 24 × 60 × 60 = 86,400 standard seconds)
        
        This system was officially used in France from 1793 to 1805 during
        the French Revolution as part of the decimalization of measurements.
        
        Midnight = 0:00:00
        Noon = 5:00:00
        6 PM = 7:50:00
        
        Format: H:MM:SS (single digit hour, two digit minutes and seconds)
        """
        now = datetime.now()
        
        # Calculate seconds since midnight (standard time)
        seconds_since_midnight = now.hour * 3600 + now.minute * 60 + now.second
        
        # Convert to decimal seconds (100,000 per day)
        decimal_seconds = seconds_since_midnight * 100000 / 86400
        
        # Extract decimal hours, minutes, and seconds
        decimal_hours = int(decimal_seconds // 10000)
        decimal_minutes = int((decimal_seconds % 10000) // 100)
        decimal_seconds_remainder = int(decimal_seconds % 100)
        
        # Format: H:MM:SS (revolutionary time format)
        return f"{decimal_hours:01d}:{decimal_minutes:02d}:{decimal_seconds_remainder:02d}"