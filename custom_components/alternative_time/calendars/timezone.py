"""Timezone sensor implementation."""
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
    _LOGGER.warning("pytz not installed, timezone support will be limited")


class TimezoneSensor(AlternativeTimeSensorBase):
    """Sensor for displaying time in a specific timezone."""

    def __init__(self, base_name: str, timezone: str) -> None:
        """Initialize the timezone sensor."""
        super().__init__(base_name, "timezone", "Timezone")
        self._timezone_str = timezone
        self._attr_icon = "mdi:clock-time-four-outline"
        self._update_interval = timedelta(seconds=1)  # Update every second
        self._timezone = None  # Will be initialized in async_added_to_hass

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        # Initialize timezone in executor to avoid blocking
        if HAS_PYTZ:
            try:
                self._timezone = await self.hass.async_add_executor_job(
                    pytz.timezone, self._timezone_str
                )
            except Exception:
                _LOGGER.warning(f"Could not load timezone {self._timezone_str}")
                self._timezone = None
        
        await super().async_added_to_hass()

    def calculate_time(self) -> str:
        """Calculate current time in specified timezone."""
        if HAS_PYTZ and self._timezone:
            now = datetime.now(self._timezone)
            return now.strftime("%H:%M:%S %Z")
        else:
            # Fallback without pytz
            now = datetime.now()
            return now.strftime("%H:%M:%S") + f" {self._timezone_str}"