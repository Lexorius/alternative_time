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
    CONF_ENABLE_MAYA,
    CONF_ENABLE_NATO,
    CONF_ENABLE_NATO_ZONE,
    CONF_ENABLE_NATO_RESCUE,
    CONF_ENABLE_ATTIC,
    CONF_ENABLE_SURIYAKATI,
    CONF_ENABLE_MINGUO,
    CONF_ENABLE_DARIAN,
    CONF_ENABLE_MARS_TIME,
    CONF_MARS_TIMEZONE,
    CONF_ENABLE_EVE,
    CONF_ENABLE_SHIRE,
    CONF_ENABLE_RIVENDELL,
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

# Mars timezone definitions
MARS_TIMEZONES = [
    "MTC+0 (Airy-0)",           # Mars Coordinated Time (Prime Meridian at Airy-0 crater)
    "MTC-1 (Olympus Mons)",      # Major volcano
    "MTC-2 (Tharsis)",           # Tharsis region
    "MTC-3 (Valles Marineris)",  # Grand canyon
    "MTC-4 (Arabia Terra)",      # Arabia region
    "MTC-5 (Amazonis)",          # Amazonis Planitia
    "MTC-6 (Elysium)",           # Elysium Mons region
    "MTC-7 (Hellas)",            # Hellas Basin
    "MTC-8 (Argyre)",            # Argyre Basin
    "MTC-9 (Chryse)",            # Chryse Planitia (Viking 1 landing site)
    "MTC-10 (Utopia)",           # Utopia Planitia (Viking 2 landing site)
    "MTC-11 (Isidis)",           # Isidis Basin
    "MTC+1 (Meridiani)",         # Meridiani Planum (Opportunity rover)
    "MTC+2 (Syrtis Major)",      # Syrtis Major
    "MTC+3 (Tyrrhena)",          # Tyrrhena Terra
    "MTC+4 (Cimmeria)",          # Terra Cimmeria
    "MTC+5 (Sirenum)",           # Terra Sirenum
    "MTC+6 (Aonia)",             # Aonia Terra
    "MTC+7 (Noachis)",           # Noachis Terra
    "MTC+8 (Sabaea)",            # Terra Sabaea
    "MTC+9 (Promethei)",         # Promethei Terra
    "MTC+10 (Chronius)",         # Chronius Mons
    "MTC+11 (Aeolis)",           # Aeolis region (Gale Crater - Curiosity rover)
    "MTC+12 (Arcadia)",          # Arcadia Planitia
]


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
                user_input.get(CONF_ENABLE_NATO, False),
                user_input.get(CONF_ENABLE_NATO_ZONE, False),
                user_input.get(CONF_ENABLE_NATO_RESCUE, False),
                user_input.get(CONF_ENABLE_ATTIC, False),
                user_input.get(CONF_ENABLE_SURIYAKATI, False),
                user_input.get(CONF_ENABLE_MINGUO, False),
                user_input.get(CONF_ENABLE_DARIAN, False),
                user_input.get(CONF_ENABLE_MARS_TIME, False),
                user_input.get(CONF_ENABLE_EVE, False),
                user_input.get(CONF_ENABLE_SHIRE, False),
                user_input.get(CONF_ENABLE_RIVENDELL, False),
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
            vol.Optional(CONF_ENABLE_NATO, default=False): bool,
            vol.Optional(CONF_ENABLE_NATO_ZONE, default=False): bool,
            vol.Optional(CONF_ENABLE_NATO_RESCUE, default=False): bool,
            vol.Optional(CONF_ENABLE_ATTIC, default=False): bool,
            vol.Optional(CONF_ENABLE_SURIYAKATI, default=False): bool,
            vol.Optional(CONF_ENABLE_MINGUO, default=False): bool,
            vol.Optional(CONF_ENABLE_DARIAN, default=False): bool,
            vol.Optional(CONF_ENABLE_MARS_TIME, default=False): bool,
            vol.Optional(CONF_MARS_TIMEZONE, default="MTC+0 (Airy-0)"): vol.In(MARS_TIMEZONES),
            vol.Optional(CONF_ENABLE_EVE, default=False): bool,
            vol.Optional(CONF_ENABLE_SHIRE, default=False): bool,
            vol.Optional(CONF_ENABLE_RIVENDELL, default=False): bool,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors
        )