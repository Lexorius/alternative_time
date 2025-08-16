"""Hexadecimal Time implementation."""
from __future__ import annotations

from datetime import datetime, timedelta

from .base import AlternativeTimeSensorBase


class HexadecimalTimeSensor(AlternativeTimeSensorBase):
    """Sensor for displaying Hexadecimal Time."""

    def __init__(self, base_name: str) -> None:
        """Initialize the hexadecimal time sensor."""
        super().__init__(base_name, "hexadecimal", "Hexadecimal Time")
        self._attr_icon = "mdi:hexadecimal"
        self._update_interval = timedelta(seconds=5)  # Update every 5 seconds

    def calculate_time(self) -> str:
        """Calculate current Hexadecimal Time.
        
        Hexadecimal time divides the day into 65,536 (0x10000 or 2^16) parts.
        This is a power of 2, making it ideal for binary/computer systems.
        
        - .0000 = midnight (00:00:00)
        - .8000 = noon (12:00:00)
        - .FFFF = 23:59:59
        
        Each hexadecimal second = 1.318359375 standard seconds
        
        Advantages:
        - Powers of 2 align well with binary computing
        - Easy bit manipulation and division
        - No rounding errors in binary representation
        
        Format: .XXXX (4 hexadecimal digits with leading dot)
        """
        now = datetime.now()
        
        # Calculate seconds since midnight
        seconds_since_midnight = now.hour * 3600 + now.minute * 60 + now.second
        
        # Convert to hexadecimal units (65536 units per day)
        # Each unit is 86400/65536 = 1.318359375 seconds
        hex_time = int(seconds_since_midnight * 65536 / 86400)
        
        # Format as 4-digit hexadecimal with leading dot
        # The dot prefix is a common notation for hexadecimal time
        return f".{hex_time:04X}"