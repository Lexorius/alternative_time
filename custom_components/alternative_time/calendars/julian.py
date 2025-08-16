"""Julian Date implementation."""
from __future__ import annotations

from datetime import datetime, timedelta

from .base import AlternativeTimeSensorBase


class JulianDateSensor(AlternativeTimeSensorBase):
    """Sensor for displaying Julian Date."""

    def __init__(self, base_name: str) -> None:
        """Initialize the Julian date sensor."""
        super().__init__(base_name, "julian", "Julian Date")
        self._attr_icon = "mdi:calendar-clock"
        self._update_interval = timedelta(seconds=60)  # Update every minute

    def calculate_time(self) -> str:
        """Calculate current Julian Date.
        
        The Julian Date (JD) is a continuous count of days since the beginning
        of the Julian Period on January 1, 4713 BCE in the proleptic Julian calendar.
        
        Used primarily in astronomy for:
        - Calculating time intervals between astronomical events
        - Avoiding calendar discontinuities
        - Simplifying date arithmetic
        
        JD 0 = January 1, 4713 BCE at noon UTC
        JD 2451545.0 = January 1, 2000 at noon UTC (J2000.0 epoch)
        
        Format: XXXXXXX.XXXXX (integer days + decimal fraction for time of day)
        """
        now = datetime.now()
        
        # Algorithm from Meeus, "Astronomical Algorithms"
        a = (14 - now.month) // 12
        y = now.year + 4800 - a
        m = now.month + 12 * a - 3
        
        # Calculate Julian Day Number (JDN) for the date at noon
        jdn = now.day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
        
        # Add fractional day for time
        # JD starts at noon, so subtract 12 hours
        fraction = (now.hour - 12) / 24 + now.minute / 1440 + now.second / 86400
        
        jd = jdn + fraction
        
        # Format with 5 decimal places (precision to about 1 second)
        return f"{jd:.5f}"