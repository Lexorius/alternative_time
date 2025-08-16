"""Base class for all alternative time sensors."""
from __future__ import annotations

from datetime import timedelta
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.event import async_track_time_interval


class AlternativeTimeSensorBase(SensorEntity):
    """Base class for Alternative Time sensors."""

    _attr_should_poll = False  # We'll use time-based updates instead

    def __init__(self, base_name: str, sensor_type: str, friendly_name: str) -> None:
        """Initialize the sensor."""
        self._base_name = base_name
        self._sensor_type = sensor_type
        self._attr_name = f"{base_name} {friendly_name}"
        self._attr_unique_id = f"{base_name}_{sensor_type}"
        self._state = None
        self._update_interval = timedelta(seconds=1)  # Default 1 second update
        self._unsub_timer = None

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def update_interval(self) -> timedelta:
        """Return the update interval."""
        return self._update_interval

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        await super().async_added_to_hass()
        
        # Set up the update interval
        self._unsub_timer = async_track_time_interval(
            self.hass,
            self._async_update_time,
            self._update_interval
        )
        
        # Initial update
        await self._async_update_time(None)

    async def async_will_remove_from_hass(self) -> None:
        """When entity will be removed from hass."""
        if self._unsub_timer:
            self._unsub_timer()
        await super().async_will_remove_from_hass()

    async def _async_update_time(self, now) -> None:
        """Update the time."""
        self._state = self.calculate_time()
        self.async_write_ha_state()

    def calculate_time(self) -> str:
        """Calculate the time value. To be overridden by subclasses."""
        return ""