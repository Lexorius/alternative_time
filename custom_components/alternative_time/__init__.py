from __future__ import annotations

import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Alternative Time from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
```

## 4. config_flow.py
```python
"""Config flow for Alternative Time integration."""
from __future__ import annotations

import logging
from typing import Any
import voluptuous as vol

try:
    import pytz
except ImportError:
    import sys
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pytz"])
    import pytz

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import (
    DOMAIN,
    CONF_NAME,
    CONF_TIMEZONE,
    CONF_ENABLE_TIMEZONE,
    CONF_ENABLE_STARDATE,
    CONF_ENABLE_SWATCH,
    CONF_ENABLE_UNIX,
    CONF_ENABLE_JULIAN,
    CONF_ENABLE_DECIMAL,
    CONF_ENABLE_HEXADECIMAL,
    DEFAULT_NAME,
)

_LOGGER = logging.getLogger(__name__)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Alternative Time."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Validate that at least one time system is selected
            time_systems_selected = any([
                user_input.get(CONF_ENABLE_TIMEZONE, False),
                user_input.get(CONF_ENABLE_STARDATE, False),
                user_input.get(CONF_ENABLE_SWATCH, False),
                user_input.get(CONF_ENABLE_UNIX, False),
                user_input.get(CONF_ENABLE_JULIAN, False),
                user_input.get(CONF_ENABLE_DECIMAL, False),
                user_input.get(CONF_ENABLE_HEXADECIMAL, False),
            ])

            if not time_systems_selected:
                errors["base"] = "no_time_system_selected"
            else:
                # Create unique ID based on name
                await self.async_set_unique_id(user_input[CONF_NAME])
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=user_input[CONF_NAME],
                    data=user_input
                )

        # Get list of timezones for dropdown
        if HAS_PYTZ:
            timezone_list = sorted(pytz.all_timezones)
        else:
            # Fallback list of common timezones
            timezone_list = [
                "Europe/Berlin",
                "Europe/London", 
                "Europe/Paris",
                "America/New_York",
                "America/Los_Angeles",
                "Asia/Tokyo",
                "Australia/Sydney",
                "UTC"
            ]

        data_schema = vol.Schema({
            vol.Required(CONF_NAME, default=DEFAULT_NAME): str,
            vol.Optional(CONF_ENABLE_TIMEZONE, default=True): bool,
            vol.Optional(CONF_TIMEZONE, default="Europe/Berlin"): vol.In(timezone_list),
            vol.Optional(CONF_ENABLE_STARDATE, default=True): bool,
            vol.Optional(CONF_ENABLE_SWATCH, default=True): bool,
            vol.Optional(CONF_ENABLE_UNIX, default=False): bool,
            vol.Optional(CONF_ENABLE_JULIAN, default=False): bool,
            vol.Optional(CONF_ENABLE_DECIMAL, default=False): bool,
            vol.Optional(CONF_ENABLE_HEXADECIMAL, default=False): bool,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors
        )