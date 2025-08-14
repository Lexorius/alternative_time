from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

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

# Fallback timezone list if pytz is not available
TIMEZONE_LIST = [
    "Europe/Berlin",
    "Europe/London",
    "Europe/Paris",
    "Europe/Zurich",
    "Europe/Vienna",
    "Europe/Rome",
    "Europe/Madrid",
    "Europe/Amsterdam",
    "Europe/Brussels",
    "Europe/Stockholm",
    "America/New_York",
    "America/Chicago",
    "America/Denver",
    "America/Los_Angeles",
    "America/Toronto",
    "America/Mexico_City",
    "America/Sao_Paulo",
    "Asia/Tokyo",
    "Asia/Shanghai",
    "Asia/Hong_Kong",
    "Asia/Singapore",
    "Asia/Dubai",
    "Asia/Mumbai",
    "Australia/Sydney",
    "Australia/Melbourne",
    "Pacific/Auckland",
    "UTC",
]

try:
    import pytz
    TIMEZONE_LIST = sorted(pytz.all_timezones)
except ImportError:
    pass


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
                user_input.get(CONF_ENABLE_MAYA, False),
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

        data_schema = vol.Schema({
            vol.Required(CONF_NAME, default=DEFAULT_NAME): str,
            vol.Optional(CONF_ENABLE_TIMEZONE, default=True): bool,
            vol.Optional(CONF_TIMEZONE, default="Europe/Berlin"): vol.In(TIMEZONE_LIST),
            vol.Optional(CONF_ENABLE_STARDATE, default=True): bool,
            vol.Optional(CONF_ENABLE_SWATCH, default=True): bool,
            vol.Optional(CONF_ENABLE_UNIX, default=False): bool,
            vol.Optional(CONF_ENABLE_JULIAN, default=False): bool,
            vol.Optional(CONF_ENABLE_DECIMAL, default=False): bool,
            vol.Optional(CONF_ENABLE_HEXADECIMAL, default=False): bool,
            vol.Optional(CONF_ENABLE_MAYA, default=False): bool,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors
        )