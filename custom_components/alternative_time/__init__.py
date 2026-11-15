"""The Alternative Time integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Alternative Time from a config entry."""
    # Reload the entry whenever its data/options change (options flow).
    # Without this, edits made under "Configure" only took effect after a
    # Home Assistant restart. The listener is unregistered on unload.
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    # Let failures propagate: HA records the error and the entry state.
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle config entry updates by reloading the entry."""
    _LOGGER.debug("Config entry %s updated — reloading", entry.title)
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        # Drop it from the sensor platform's registries, otherwise removed
        # entries stay referenced for the lifetime of the process.
        from .sensor import forget_config_entry
        forget_config_entry(entry.entry_id)

    return unload_ok
