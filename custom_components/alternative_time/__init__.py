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

    # Reload the entry whenever its data/options change (options flow).
    # Without this, edits made under "Configure" only took effect after a
    # Home Assistant restart. The listener is unregistered on unload.
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    # Forward setup to sensor platform. Let failures propagate: HA records
    # the error and the entry state; swallowing it here (as older versions
    # did) hid the real cause and showed a "loaded" entry with no entities.
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    _LOGGER.info(f"Successfully set up Alternative Time integration for {entry.title}")

    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle config entry updates by reloading the entry."""
    _LOGGER.debug(f"Config entry {entry.title} updated — reloading")
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.debug(f"Unloading Alternative Time integration for {entry.title}")

    # Unload sensor platform
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        # Remove config entry from hass.data
        hass.data[DOMAIN].pop(entry.entry_id, None)

        # Drop it from the sensor platform's entry registry as well, otherwise
        # removed entries stay referenced for the lifetime of the process.
        from .sensor import forget_config_entry
        forget_config_entry(entry.entry_id)

        # Clean up domain if no more entries
        if not hass.data[DOMAIN]:
            hass.data.pop(DOMAIN)

    return unload_ok
