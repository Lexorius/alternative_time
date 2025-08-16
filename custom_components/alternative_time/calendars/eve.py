"""EVE Online Time (New Eden Standard Time) implementation."""
from __future__ import annotations

from datetime import datetime, timedelta

from .base import AlternativeTimeSensorBase


class EveOnlineTimeSensor(AlternativeTimeSensorBase):
    """Sensor for displaying EVE Online Time (New Eden Standard Time)."""

    def __init__(self, base_name: str) -> None:
        """Initialize the EVE Online time sensor."""
        super().__init__(base_name, "eve_online", "EVE Online Time")
        self._attr_icon = "mdi:space-station"
        self._update_interval = timedelta(seconds=1)

    def calculate_time(self) -> str:
        """Calculate current EVE Online Time.
        
        EVE Online uses UTC and has its own calendar system:
        - YC (Yoiul Conference) year starts from YC 0 = 23236 AD
        - For gameplay purposes, YC 105 = 2003 (EVE launch year)
        - The game uses standard Earth months and days
        - All times are in UTC (New Eden Standard Time)
        """
        # EVE uses UTC
        now = datetime.utcnow()
        
        # Calculate YC year (starts from 2003 = YC 105)
        # Each real year equals one YC year
        eve_year = 105 + (now.year - 2003)
        
        # Format: YC XXX.MM.DD HH:MM:SS
        # Standard EVE time notation used in game
        return f"YC {eve_year}.{now.month:02d}.{now.day:02d} {now.hour:02d}:{now.minute:02d}:{now.second:02d}"