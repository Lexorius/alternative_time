"""Config flow for Alternative Time integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
import pytz

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.selector import (
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    TextSelector,
    TextSelectorConfig,
    BooleanSelector,
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
        """Handle the initial step - basic configuration."""
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_technical()

        timezone_list = sorted(pytz.all_timezones)
        
        data_schema = vol.Schema({
            vol.Required(CONF_NAME, default=DEFAULT_NAME): TextSelector(
                TextSelectorConfig()
            ),
            vol.Required(
                CONF_ENABLE_TIMEZONE,
                default=False,
                description={"suggested_value": False}
            ): BooleanSelector(),
            vol.Optional(CONF_TIMEZONE, default="UTC"): SelectSelector(
                SelectSelectorConfig(
                    options=timezone_list,
                    mode=SelectSelectorMode.DROPDOWN,
                )
            ),
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            description_placeholders={
                "intro": "Configure the base settings for Alternative Time Systems"
            },
        )

    async def async_step_technical(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle technical/modern time systems selection."""
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_military()

        data_schema = vol.Schema({
            vol.Required(
                CONF_ENABLE_UNIX,
                default=False,
                description={"suggested_value": False}
            ): BooleanSelector(),
            vol.Required(
                CONF_ENABLE_JULIAN,
                default=False,
                description={"suggested_value": False}
            ): BooleanSelector(),
            vol.Required(
                CONF_ENABLE_DECIMAL,
                default=False,
                description={"suggested_value": False}
            ): BooleanSelector(),
            vol.Required(
                CONF_ENABLE_HEXADECIMAL,
                default=False,
                description={"suggested_value": False}
            ): BooleanSelector(),
            vol.Required(
                CONF_ENABLE_SWATCH,
                default=False,
                description={"suggested_value": False}
            ): BooleanSelector(),
        })

        return self.async_show_form(
            step_id="technical",
            data_schema=data_schema,
            description_placeholders={
                "category": "Technical & Modern Time Systems"
            },
        )

    async def async_step_military(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle military time systems selection."""
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_historical()

        data_schema = vol.Schema({
            vol.Required(
                CONF_ENABLE_NATO,
                default=False,
                description={"suggested_value": False}
            ): BooleanSelector(),
            vol.Required(
                CONF_ENABLE_NATO_ZONE,
                default=False,
                description={"suggested_value": False}
            ): BooleanSelector(),
            vol.Required(
                CONF_ENABLE_NATO_RESCUE,
                default=False,
                description={"suggested_value": False}
            ): BooleanSelector(),
        })

        return self.async_show_form(
            step_id="military",
            data_schema=data_schema,
            description_placeholders={
                "category": "Military Time Systems"
            },
        )

    async def async_step_historical(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle historical calendar systems selection."""
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_cultural()

        data_schema = vol.Schema({
            vol.Required(
                CONF_ENABLE_MAYA,
                default=False,
                description={"suggested_value": False}
            ): BooleanSelector(),
            vol.Required(
                CONF_ENABLE_EGYPTIAN,
                default=False,
                description={"suggested_value": False}
            ): BooleanSelector(),
            vol.Required(
                CONF_ENABLE_ROMAN,
                default=False,
                description={"suggested_value": False}
            ): BooleanSelector(),
            vol.Required(
                CONF_ENABLE_ATTIC,
                default=False,
                description={"suggested_value": False}
            ): BooleanSelector(),
        })

        return self.async_show_form(
            step_id="historical",
            data_schema=data_schema,
            description_placeholders={
                "category": "Historical Calendar Systems"
            },
        )

    async def async_step_cultural(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle cultural/regional calendar systems selection."""
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_space()

        data_schema = vol.Schema({
            vol.Required(
                CONF_ENABLE_SURIYAKATI,
                default=False,
                description={"suggested_value": False}
            ): BooleanSelector(),
            vol.Required(
                CONF_ENABLE_MINGUO,
                default=False,
                description={"suggested_value": False}
            ): BooleanSelector(),
        })

        return self.async_show_form(
            step_id="cultural",
            data_schema=data_schema,
            description_placeholders={
                "category": "Asian Calendar Systems"
            },
        )

    async def async_step_space(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle space/Mars calendar systems selection."""
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_scifi()

        data_schema = vol.Schema({
            vol.Required(
                CONF_ENABLE_DARIAN,
                default=False,
                description={"suggested_value": False}
            ): BooleanSelector(),
            vol.Required(
                CONF_ENABLE_MARS_TIME,
                default=False,
                description={"suggested_value": False}
            ): BooleanSelector(),
            vol.Optional(CONF_MARS_TIMEZONE, default="MTC"): SelectSelector(
                SelectSelectorConfig(
                    options=MARS_TIMEZONES,
                    mode=SelectSelectorMode.DROPDOWN,
                )
            ),
        })

        return self.async_show_form(
            step_id="space",
            data_schema=data_schema,
            description_placeholders={
                "category": "Space & Mars Time Systems"
            },
        )

    async def async_step_scifi(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle science fiction time systems selection."""
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_fantasy()

        data_schema = vol.Schema({
            vol.Required(
                CONF_ENABLE_STARDATE,
                default=False,
                description={"suggested_value": False}
            ): BooleanSelector(),
            vol.Required(
                CONF_ENABLE_EVE,
                default=False,
                description={"suggested_value": False}
            ): BooleanSelector(),
        })

        return self.async_show_form(
            step_id="scifi",
            data_schema=data_schema,
            description_placeholders={
                "category": "Science Fiction Time Systems"
            },
        )

    async def async_step_fantasy(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle fantasy calendar systems selection."""
        if user_input is not None:
            self._data.update(user_input)
            
            # Check if at least one time system is enabled
            enabled_systems = [
                key for key, value in self._data.items() 
                if key.startswith("enable_") and value is True
            ]
            
            if not enabled_systems:
                return self.async_show_form(
                    step_id="fantasy",
                    data_schema=self._get_fantasy_schema(),
                    errors={"base": "no_systems_selected"},
                    description_placeholders={
                        "category": "Fantasy World Calendars"
                    },
                )
            
            return await self.async_step_confirm()

        return self.async_show_form(
            step_id="fantasy",
            data_schema=self._get_fantasy_schema(),
            description_placeholders={
                "category": "Fantasy World Calendars"
            },
        )

    def _get_fantasy_schema(self) -> vol.Schema:
        """Get the schema for fantasy calendars."""
        return vol.Schema({
            vol.Required(
                CONF_ENABLE_SHIRE,
                default=False,
                description={"suggested_value": False}
            ): BooleanSelector(),
            vol.Required(
                CONF_ENABLE_RIVENDELL,
                default=False,
                description={"suggested_value": False}
            ): BooleanSelector(),
            vol.Required(
                CONF_ENABLE_TAMRIEL,
                default=False,
                description={"suggested_value": False}
            ): BooleanSelector(),
            vol.Required(
                CONF_ENABLE_DISCWORLD,
                default=False,
                description={"suggested_value": False}
            ): BooleanSelector(),
        })

    async def async_step_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the confirmation step."""
        if user_input is not None:
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
        self._data = {}

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options - start with technical systems."""
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_military()

        current_data = self.config_entry.options or self.config_entry.data
        timezone_list = sorted(pytz.all_timezones)
        
        data_schema = vol.Schema({
            vol.Required(
                CONF_ENABLE_TIMEZONE,
                default=current_data.get(CONF_ENABLE_TIMEZONE, False)
            ): BooleanSelector(),
            vol.Optional(
                CONF_TIMEZONE,
                default=current_data.get(CONF_TIMEZONE, "UTC")
            ): SelectSelector(
                SelectSelectorConfig(
                    options=timezone_list,
                    mode=SelectSelectorMode.DROPDOWN,
                )
            ),
            vol.Required(
                CONF_ENABLE_UNIX,
                default=current_data.get(CONF_ENABLE_UNIX, False)
            ): BooleanSelector(),
            vol.Required(
                CONF_ENABLE_JULIAN,
                default=current_data.get(CONF_ENABLE_JULIAN, False)
            ): BooleanSelector(),
            vol.Required(
                CONF_ENABLE_DECIMAL,
                default=current_data.get(CONF_ENABLE_DECIMAL, False)
            ): BooleanSelector(),
            vol.Required(
                CONF_ENABLE_HEXADECIMAL,
                default=current_data.get(CONF_ENABLE_HEXADECIMAL, False)
            ): BooleanSelector(),
            vol.Required(
                CONF_ENABLE_SWATCH,
                default=current_data.get(CONF_ENABLE_SWATCH, False)
            ): BooleanSelector(),
        })

        return self.async_show_form(
            step_id="init",
            data_schema=data_schema,
        )

    async def async_step_military(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Military options."""
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_historical()

        current_data = self.config_entry.options or self.config_entry.data
        
        data_schema = vol.Schema({
            vol.Required(
                CONF_ENABLE_NATO,
                default=current_data.get(CONF_ENABLE_NATO, False)
            ): BooleanSelector(),
            vol.Required(
                CONF_ENABLE_NATO_ZONE,
                default=current_data.get(CONF_ENABLE_NATO_ZONE, False)
            ): BooleanSelector(),
            vol.Required(
                CONF_ENABLE_NATO_RESCUE,
                default=current_data.get(CONF_ENABLE_NATO_RESCUE, False)
            ): BooleanSelector(),
        })

        return self.async_show_form(
            step_id="military",
            data_schema=data_schema,
        )

    async def async_step_historical(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Historical options."""
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_finish()

        current_data = self.config_entry.options or self.config_entry.data
        
        # Add remaining calendars here in a simplified form
        data_schema = vol.Schema({
            vol.Required(
                CONF_ENABLE_MAYA,
                default=current_data.get(CONF_ENABLE_MAYA, False)
            ): BooleanSelector(),
            vol.Required(
                CONF_ENABLE_EGYPTIAN,
                default=current_data.get(CONF_ENABLE_EGYPTIAN, False)
            ): BooleanSelector(),
            vol.Required(
                CONF_ENABLE_ROMAN,
                default=current_data.get(CONF_ENABLE_ROMAN, False)
            ): BooleanSelector(),
            vol.Required(
                CONF_ENABLE_STARDATE,
                default=current_data.get(CONF_ENABLE_STARDATE, False)
            ): BooleanSelector(),
        })

        return self.async_show_form(
            step_id="historical",
            data_schema=data_schema,
        )

    async def async_step_finish(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Create the config entry."""
        # Merge all collected data
        if user_input is not None:
            self._data.update(user_input)
        
        # Check if at least one system is enabled
        enabled_systems = [
            key for key, value in self._data.items() 
            if key.startswith("enable_") and value is True
        ]
        
        if not enabled_systems:
            return self.async_show_form(
                step_id="historical",
                errors={"base": "no_systems_selected"},
            )
        
        return self.async_create_entry(title="", data=self._data)