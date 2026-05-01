"""The Alternative Time integration."""
from __future__ import annotations

import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Platform list - sensor.py must exist in the same directory as this file
PLATFORMS: list[Platform] = [Platform.SENSOR]

# This integration is configured exclusively via the UI (config entries).
# We declare a config_entry_only_config_schema to satisfy hassfest, since we
# still keep an async_setup() for backward compatibility.
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Alternative Time component (YAML not supported)."""
    # This integration only supports config entries (UI flow).
    # Keeping this method for backward compatibility.
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Alternative Time from a config entry."""
    _LOGGER.debug(f"Setting up Alternative Time integration for {entry.title}")
    _LOGGER.debug(f"Config data: {entry.data}")

    # Initialize the domain in hass.data if needed
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    # Store config entry data
    hass.data[DOMAIN][entry.entry_id] = entry.data

    # Forward setup to sensor platform
    # This will look for sensor.py in the same directory as __init__.py
    try:
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
        _LOGGER.info(f"Successfully set up Alternative Time integration for {entry.title}")
    except Exception as e:
        _LOGGER.error(f"Error setting up platforms: {e}")
        return False

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.debug(f"Unloading Alternative Time integration for {entry.title}")

    # Unload sensor platform
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        # Remove config entry from hass.data
        hass.data[DOMAIN].pop(entry.entry_id, None)

        # Clean up domain if no more entries
        if not hass.data[DOMAIN]:
            hass.data.pop(DOMAIN)

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
