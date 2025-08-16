"""Config flow for Alternative Time integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
import pytz

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.selector import (
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    TextSelector,
    TextSelectorConfig,
)

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
    CONF_ENABLE_TAMRIEL,
    CONF_ENABLE_EGYPTIAN,
    CONF_ENABLE_DISCWORLD,
    CONF_ENABLE_ROMAN,
    DEFAULT_NAME,
    MARS_TIMEZONES,
)

_LOGGER = logging.getLogger(__name__)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Alternative Time."""

    VERSION = 1

    def __init__(self):
        """Initialize the config flow."""
        self._data = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Check if at least one time system is enabled
            enabled_systems = [
                key for key, value in user_input.items() 
                if key.startswith("enable_") and value is True
            ]
            
            if not enabled_systems:
                errors["base"] = "no_systems_selected"
            else:
                # Store the configuration temporarily
                self._data = user_input
                # Move to confirmation step
                return await self.async_step_confirm()

        # Get list of timezones for selector
        timezone_list = sorted(pytz.all_timezones)
        
        # Build the data schema with visual groupings using descriptions
        data_schema = vol.Schema({
            # Basic Configuration
            vol.Required(CONF_NAME, default=DEFAULT_NAME): TextSelector(
                TextSelectorConfig()
            ),
            
            # ─────────────── BASIC SETTINGS ───────────────
            vol.Required(CONF_ENABLE_TIMEZONE, default=False): bool,
            vol.Optional(CONF_TIMEZONE, default="UTC"): SelectSelector(
                SelectSelectorConfig(
                    options=timezone_list,
                    mode=SelectSelectorMode.DROPDOWN,
                )
            ),
            
            # ─────────────── TECHNICAL/MODERN ───────────────
            vol.Required(CONF_ENABLE_UNIX, default=False): bool,
            vol.Required(CONF_ENABLE_JULIAN, default=False): bool,
            vol.Required(CONF_ENABLE_DECIMAL, default=False): bool,
            vol.Required(CONF_ENABLE_HEXADECIMAL, default=False): bool,
            vol.Required(CONF_ENABLE_SWATCH, default=False): bool,
            
            # ─────────────── MILITARY/NATO ───────────────
            vol.Required(CONF_ENABLE_NATO, default=False): bool,
            vol.Required(CONF_ENABLE_NATO_ZONE, default=False): bool,
            vol.Required(CONF_ENABLE_NATO_RESCUE, default=False): bool,
            
            # ─────────────── HISTORICAL ───────────────
            vol.Required(CONF_ENABLE_MAYA, default=False): bool,
            vol.Required(CONF_ENABLE_EGYPTIAN, default=False): bool,
            vol.Required(CONF_ENABLE_ROMAN, default=False): bool,
            vol.Required(CONF_ENABLE_ATTIC, default=False): bool,
            
            # ─────────────── ASIAN ───────────────
            vol.Required(CONF_ENABLE_SURIYAKATI, default=False): bool,
            vol.Required(CONF_ENABLE_MINGUO, default=False): bool,
            
            # ─────────────── SPACE/MARS ───────────────
            vol.Required(CONF_ENABLE_DARIAN, default=False): bool,
            vol.Required(CONF_ENABLE_MARS_TIME, default=False): bool,
            vol.Optional(CONF_MARS_TIMEZONE, default="MTC"): SelectSelector(
                SelectSelectorConfig(
                    options=MARS_TIMEZONES,
                    mode=SelectSelectorMode.DROPDOWN,
                )
            ),
            
            # ─────────────── SCIENCE FICTION ───────────────
            vol.Required(CONF_ENABLE_STARDATE, default=False): bool,
            vol.Required(CONF_ENABLE_EVE, default=False): bool,
            
            # ─────────────── FANTASY ───────────────
            vol.Required(CONF_ENABLE_SHIRE, default=False): bool,
            vol.Required(CONF_ENABLE_RIVENDELL, default=False): bool,
            vol.Required(CONF_ENABLE_TAMRIEL, default=False): bool,
            vol.Required(CONF_ENABLE_DISCWORLD, default=False): bool,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    async def async_step_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the confirmation step."""
        if user_input is not None:
            # User confirmed, create the entry
            title = self._data.get(CONF_NAME, DEFAULT_NAME)
            return self.async_create_entry(title=title, data=self._data)

        # Build a summary of selected systems
        selected_systems = []
        system_names = {
            CONF_ENABLE_TIMEZONE: "Timezone",
            CONF_ENABLE_STARDATE: "Stardate",
            CONF_ENABLE_SWATCH: "Swatch Internet Time",
            CONF_ENABLE_UNIX: "Unix Timestamp",
            CONF_ENABLE_JULIAN: "Julian Date",
            CONF_ENABLE_DECIMAL: "Decimal Time",
            CONF_ENABLE_HEXADECIMAL: "Hexadecimal Time",
            CONF_ENABLE_MAYA: "Maya Calendar",
            CONF_ENABLE_NATO: "NATO DTG",
            CONF_ENABLE_NATO_ZONE: "NATO Zone Time",
            CONF_ENABLE_NATO_RESCUE: "NATO Rescue Time",
            CONF_ENABLE_ATTIC: "Attic Calendar",
            CONF_ENABLE_SURIYAKATI: "Suriyakati Calendar",
            CONF_ENABLE_MINGUO: "Minguo Calendar",
            CONF_ENABLE_DARIAN: "Darian Mars Calendar",
            CONF_ENABLE_MARS_TIME: "Mars Time",
            CONF_ENABLE_EVE: "EVE Online Time",
            CONF_ENABLE_SHIRE: "Shire Calendar",
            CONF_ENABLE_RIVENDELL: "Rivendell Calendar",
            CONF_ENABLE_TAMRIEL: "Tamriel Calendar",
            CONF_ENABLE_EGYPTIAN: "Egyptian Calendar",
            CONF_ENABLE_DISCWORLD: "Discworld Calendar",
            CONF_ENABLE_ROMAN: "Roman Calendar",
        }
        
        for key, name in system_names.items():
            if self._data.get(key, False):
                selected_systems.append(name)

        return self.async_show_form(
            step_id="confirm",
            description_placeholders={
                "name": self._data.get(CONF_NAME, DEFAULT_NAME),
                "systems": ", ".join(selected_systems) if selected_systems else "None",
                "count": str(len(selected_systems)),
            },
        )

    @staticmethod
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Alternative Time."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        errors = {}
        
        if user_input is not None:
            # Check if at least one time system is enabled
            enabled_systems = [
                key for key, value in user_input.items() 
                if key.startswith("enable_") and value is True
            ]
            
            if not enabled_systems:
                errors["base"] = "no_systems_selected"
            else:
                return self.async_create_entry(title="", data=user_input)

        # Get list of timezones for selector
        timezone_list = sorted(pytz.all_timezones)
        
        # Get current options or use defaults from config
        current_data = self.config_entry.options or self.config_entry.data
        
        # Build the same schema as in the config flow
        data_schema = vol.Schema({
            # ─────────────── BASIC SETTINGS ───────────────
            vol.Required(
                CONF_ENABLE_TIMEZONE,
                default=current_data.get(CONF_ENABLE_TIMEZONE, False)
            ): bool,
            vol.Optional(
                CONF_TIMEZONE,
                default=current_data.get(CONF_TIMEZONE, "UTC")
            ): SelectSelector(
                SelectSelectorConfig(
                    options=timezone_list,
                    mode=SelectSelectorMode.DROPDOWN,
                )
            ),
            
            # ─────────────── TECHNICAL/MODERN ───────────────
            vol.Required(
                CONF_ENABLE_UNIX,
                default=current_data.get(CONF_ENABLE_UNIX, False)
            ): bool,
            vol.Required(
                CONF_ENABLE_JULIAN,
                default=current_data.get(CONF_ENABLE_JULIAN, False)
            ): bool,
            vol.Required(
                CONF_ENABLE_DECIMAL,
                default=current_data.get(CONF_ENABLE_DECIMAL, False)
            ): bool,
            vol.Required(
                CONF_ENABLE_HEXADECIMAL,
                default=current_data.get(CONF_ENABLE_HEXADECIMAL, False)
            ): bool,
            vol.Required(
                CONF_ENABLE_SWATCH,
                default=current_data.get(CONF_ENABLE_SWATCH, False)
            ): bool,
            
            # ─────────────── MILITARY/NATO ───────────────
            vol.Required(
                CONF_ENABLE_NATO,
                default=current_data.get(CONF_ENABLE_NATO, False)
            ): bool,
            vol.Required(
                CONF_ENABLE_NATO_ZONE,
                default=current_data.get(CONF_ENABLE_NATO_ZONE, False)
            ): bool,
            vol.Required(
                CONF_ENABLE_NATO_RESCUE,
                default=current_data.get(CONF_ENABLE_NATO_RESCUE, False)
            ): bool,
            
            # ─────────────── HISTORICAL ───────────────
            vol.Required(
                CONF_ENABLE_MAYA,
                default=current_data.get(CONF_ENABLE_MAYA, False)
            ): bool,
            vol.Required(
                CONF_ENABLE_EGYPTIAN,
                default=current_data.get(CONF_ENABLE_EGYPTIAN, False)
            ): bool,
            vol.Required(
                CONF_ENABLE_ROMAN,
                default=current_data.get(CONF_ENABLE_ROMAN, False)
            ): bool,
            vol.Required(
                CONF_ENABLE_ATTIC,
                default=current_data.get(CONF_ENABLE_ATTIC, False)
            ): bool,
            
            # ─────────────── ASIAN ───────────────
            vol.Required(
                CONF_ENABLE_SURIYAKATI,
                default=current_data.get(CONF_ENABLE_SURIYAKATI, False)
            ): bool,
            vol.Required(
                CONF_ENABLE_MINGUO,
                default=current_data.get(CONF_ENABLE_MINGUO, False)
            ): bool,
            
            # ─────────────── SPACE/MARS ───────────────
            vol.Required(
                CONF_ENABLE_DARIAN,
                default=current_data.get(CONF_ENABLE_DARIAN, False)
            ): bool,
            vol.Required(
                CONF_ENABLE_MARS_TIME,
                default=current_data.get(CONF_ENABLE_MARS_TIME, False)
            ): bool,
            vol.Optional(
                CONF_MARS_TIMEZONE,
                default=current_data.get(CONF_MARS_TIMEZONE, "MTC")
            ): SelectSelector(
                SelectSelectorConfig(
                    options=MARS_TIMEZONES,
                    mode=SelectSelectorMode.DROPDOWN,
                )
            ),
            
            # ─────────────── SCIENCE FICTION ───────────────
            vol.Required(
                CONF_ENABLE_STARDATE,
                default=current_data.get(CONF_ENABLE_STARDATE, False)
            ): bool,
            vol.Required(
                CONF_ENABLE_EVE,
                default=current_data.get(CONF_ENABLE_EVE, False)
            ): bool,
            
            # ─────────────── FANTASY ───────────────
            vol.Required(
                CONF_ENABLE_SHIRE,
                default=current_data.get(CONF_ENABLE_SHIRE, False)
            ): bool,
            vol.Required(
                CONF_ENABLE_RIVENDELL,
                default=current_data.get(CONF_ENABLE_RIVENDELL, False)
            ): bool,
            vol.Required(
                CONF_ENABLE_TAMRIEL,
                default=current_data.get(CONF_ENABLE_TAMRIEL, False)
            ): bool,
            vol.Required(
                CONF_ENABLE_DISCWORLD,
                default=current_data.get(CONF_ENABLE_DISCWORLD, False)
            ): bool,
        })

        return self.async_show_form(
            step_id="init",
            data_schema=data_schema,
            errors=errors,
        )