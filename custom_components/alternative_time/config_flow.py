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
        self._current_step_data = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step - basic configuration."""
        errors = {}

        if user_input is not None:
            self._data.update(user_input)
            # Move to the next step for selecting time systems
            return await self.async_step_select_modern()

        data_schema = vol.Schema({
            vol.Required(CONF_NAME, default=DEFAULT_NAME): str,
            vol.Required(CONF_ENABLE_TIMEZONE, default=False): bool,
            vol.Optional(CONF_TIMEZONE, default="UTC"): SelectSelector(
                SelectSelectorConfig(
                    options=sorted(pytz.all_timezones),
                    mode=SelectSelectorMode.DROPDOWN,
                )
            ),
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "intro": "Configure the base settings for Alternative Time Systems"
            },
        )

    async def async_step_select_modern(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Select modern/technical time systems."""
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_select_historical()

        data_schema = vol.Schema({
            # Technical Time Systems
            vol.Optional("group_technical"): section,
            vol.Required(CONF_ENABLE_UNIX, default=False): bool,
            vol.Required(CONF_ENABLE_JULIAN, default=False): bool,
            vol.Required(CONF_ENABLE_DECIMAL, default=False): bool,
            vol.Required(CONF_ENABLE_HEXADECIMAL, default=False): bool,
            vol.Required(CONF_ENABLE_SWATCH, default=False): bool,
            
            # Military/NATO Systems
            vol.Optional("group_military"): section,
            vol.Required(CONF_ENABLE_NATO, default=False): bool,
            vol.Required(CONF_ENABLE_NATO_ZONE, default=False): bool,
            vol.Required(CONF_ENABLE_NATO_RESCUE, default=False): bool,
        })

        return self.async_show_form(
            step_id="select_modern",
            data_schema=data_schema,
            description_placeholders={
                "title": "Modern & Technical Time Systems"
            },
        )

    async def async_step_select_historical(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Select historical calendar systems."""
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_select_cultural()

        data_schema = vol.Schema({
            # Ancient Calendars
            vol.Optional("group_ancient"): section,
            vol.Required(CONF_ENABLE_MAYA, default=False): bool,
            vol.Required(CONF_ENABLE_EGYPTIAN, default=False): bool,
            vol.Required(CONF_ENABLE_ROMAN, default=False): bool,
            vol.Required(CONF_ENABLE_ATTIC, default=False): bool,
            
            # Asian Calendars
            vol.Optional("group_asian"): section,
            vol.Required(CONF_ENABLE_SURIYAKATI, default=False): bool,
            vol.Required(CONF_ENABLE_MINGUO, default=False): bool,
        })

        return self.async_show_form(
            step_id="select_historical",
            data_schema=data_schema,
            description_placeholders={
                "title": "Historical Calendar Systems"
            },
        )

    async def async_step_select_cultural(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Select cultural/regional calendar systems."""
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_select_scifi()

        data_schema = vol.Schema({
            # Space/Mars Calendars
            vol.Optional("group_space"): section,
            vol.Required(CONF_ENABLE_DARIAN, default=False): bool,
            vol.Required(CONF_ENABLE_MARS_TIME, default=False): bool,
            vol.Optional(CONF_MARS_TIMEZONE, default="MTC"): SelectSelector(
                SelectSelectorConfig(
                    options=MARS_TIMEZONES,
                    mode=SelectSelectorMode.DROPDOWN,
                )
            ),
        })

        return self.async_show_form(
            step_id="select_cultural",
            data_schema=data_schema,
            description_placeholders={
                "title": "Space & Mars Time Systems"
            },
        )

    async def async_step_select_scifi(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Select sci-fi and fantasy calendar systems."""
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_select_fantasy()

        data_schema = vol.Schema({
            # Sci-Fi Time Systems
            vol.Optional("group_scifi"): section,
            vol.Required(CONF_ENABLE_STARDATE, default=False): bool,
            vol.Required(CONF_ENABLE_EVE, default=False): bool,
        })

        return self.async_show_form(
            step_id="select_scifi",
            data_schema=data_schema,
            description_placeholders={
                "title": "Science Fiction Time Systems"
            },
        )

    async def async_step_select_fantasy(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Select fantasy calendar systems."""
        if user_input is not None:
            self._data.update(user_input)
            
            # Check if at least one time system is enabled
            enabled_systems = [
                key for key, value in self._data.items() 
                if key.startswith("enable_") and value is True
            ]
            
            if not enabled_systems:
                # Go back to first selection with error
                return await self.async_step_select_modern()
            
            return await self.async_step_confirm()

        data_schema = vol.Schema({
            # Fantasy Calendars
            vol.Optional("group_fantasy"): section,
            vol.Required(CONF_ENABLE_SHIRE, default=False): bool,
            vol.Required(CONF_ENABLE_RIVENDELL, default=False): bool,
            vol.Required(CONF_ENABLE_TAMRIEL, default=False): bool,
            vol.Required(CONF_ENABLE_DISCWORLD, default=False): bool,
        })

        return self.async_show_form(
            step_id="select_fantasy",
            data_schema=data_schema,
            description_placeholders={
                "title": "Fantasy World Calendars"
            },
        )

    async def async_step_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the confirmation step."""
        if user_input is not None:
            # User confirmed, create the entry
            title = self._data.get(CONF_NAME, DEFAULT_NAME)
            # Remove any group markers from data
            cleaned_data = {k: v for k, v in self._data.items() if not k.startswith("group_")}
            return self.async_create_entry(title=title, data=cleaned_data)

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
                "systems": ", ".join(selected_systems[:5]) + ("..." if len(selected_systems) > 5 else ""),
                "count": str(len(selected_systems)),
            },
        )

    @staticmethod
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)


# Dummy section marker for visual grouping
section = vol.Marker("section")


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Alternative Time."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options - show all in one page for options."""
        if user_input is not None:
            # Check if at least one time system is enabled
            enabled_systems = [
                key for key, value in user_input.items() 
                if key.startswith("enable_") and value is True
            ]
            
            if not enabled_systems:
                errors = {"base": "no_systems_selected"}
            else:
                return self.async_create_entry(title="", data=user_input)

        # Get current options or use defaults from config
        current_data = self.config_entry.options or self.config_entry.data
        
        # For options, we show everything on one page but with visual grouping
        data_schema = vol.Schema({
            # Basic Settings
            vol.Optional("_group_basic"): section,
            vol.Required(
                CONF_ENABLE_TIMEZONE,
                default=current_data.get(CONF_ENABLE_TIMEZONE, False)
            ): bool,
            vol.Optional(
                CONF_TIMEZONE,
                default=current_data.get(CONF_TIMEZONE, "UTC")
            ): SelectSelector(
                SelectSelectorConfig(
                    options=sorted(pytz.all_timezones),
                    mode=SelectSelectorMode.DROPDOWN,
                )
            ),
            
            # Technical/Modern
            vol.Optional("_group_technical"): section,
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
            
            # Military
            vol.Optional("_group_military"): section,
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
            
            # Historical
            vol.Optional("_group_historical"): section,
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
            
            # Asian
            vol.Optional("_group_asian"): section,
            vol.Required(
                CONF_ENABLE_SURIYAKATI,
                default=current_data.get(CONF_ENABLE_SURIYAKATI, False)
            ): bool,
            vol.Required(
                CONF_ENABLE_MINGUO,
                default=current_data.get(CONF_ENABLE_MINGUO, False)
            ): bool,
            
            # Space/Mars
            vol.Optional("_group_space"): section,
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
            
            # Sci-Fi
            vol.Optional("_group_scifi"): section,
            vol.Required(
                CONF_ENABLE_STARDATE,
                default=current_data.get(CONF_ENABLE_STARDATE, False)
            ): bool,
            vol.Required(
                CONF_ENABLE_EVE,
                default=current_data.get(CONF_ENABLE_EVE, False)
            ): bool,
            
            # Fantasy
            vol.Optional("_group_fantasy"): section,
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
            errors={} if user_input is None else {"base": "no_systems_selected"},
        )