"""Swatch Internet Time implementation."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta

from .base import AlternativeTimeSensorBase

_LOGGER = logging.getLogger(__name__)

try:
    import pytz
    HAS_PYTZ = True
except ImportError:
    HAS_PYTZ = False
    _LOGGER.warning("pytz not installed, using UTC+1 approximation for Biel Mean Time")


class SwatchTimeSensor(AlternativeTimeSensorBase):
    """Sensor for displaying Swatch Internet Time."""

    def __init__(self, base_name: str) -> None:
        """Initialize the Swatch time sensor."""
        super().__init__(base_name, "swatch", "Swatch Internet Time")
        self._attr_icon = "mdi:web-clock"
        self._update_interval = timedelta(seconds=1)  # Update every second for smooth beats
        self._bmt = None  # Will be initialized in async_added_to_hass

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        # Initialize timezone in executor to avoid blocking
        if HAS_PYTZ:
            try:
                # Biel Mean Time (BMT) = UTC+1 (Swatch headquarters in Biel, Switzerland)
                self._bmt = await self.hass.async_add_executor_job(
                    pytz.timezone, 'Europe/Zurich'
                )
            except Exception:
                _LOGGER.warning("Could not load timezone Europe/Zurich for Swatch time")
                self._bmt = None
        
        await super().async_added_to_hass()

    def calculate_time(self) -> str:
        """Calculate current Swatch Internet Time.
        
        Swatch Internet Time divides the day into 1000 beats:
        - No time zones - same time everywhere
        - @000 = midnight BMT (Biel Mean Time, UTC+1)
        - @500 = noon BMT
        - @999 = 23:59:24 BMT
        - 1 beat = 1 minute 26.4 seconds = 86.4 seconds
        
        Format: @XXX.XX (with two decimal places for precision)
        """
        if HAS_PYTZ and self._bmt:
            # Use proper Biel timezone
            now = datetime.now(self._bmt)
        else:
            # Fallback: use UTC+1 as approximation for Biel Mean Time
            now = datetime.utcnow() + timedelta(hours=1)
        
        # Calculate seconds since midnight BMT
        seconds_since_midnight = (now.hour * 3600 + now.minute * 60 + now.second)
        
        # Convert to beats (1 beat = 86.4 seconds)
        beats = seconds_since_midnight / 86.4
        
        # Format with @ symbol and 2 decimal places
        return f"@{beats:06.2f}"