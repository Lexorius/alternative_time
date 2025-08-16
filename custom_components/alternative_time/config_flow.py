"""Config flow for Alternative Time integration - Version 2.5 with Auto-Discovery."""
from __future__ import annotations

import logging
from typing import Any, Dict, List
from collections import defaultdict

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

from .const import DEFAULT_NAME, MARS_TIMEZONES, DOMAIN

_LOGGER = logging.getLogger(__name__)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Alternative Time with auto-discovery."""

    VERSION = 1

    def __init__(self):
        """Initialize the config flow."""
        self._data = {}
        self._discovered_calendars = None
        self._categories = None
        self._current_category_index = 0
        self._category_list = []
        
    def _discover_calendars(self):
        """Discover available calendars and organize by category."""
        if self._discovered_calendars is None:
            try:
                # Import the discovery function when needed
                from .sensor import export_discovered_calendars
                self._discovered_calendars = export_discovered_calendars()
                
                if not self._discovered_calendars:
                    _LOGGER.warning("No calendars discovered by sensor module")
                    # Try direct discovery as fallback
                    self._discovered_calendars = self._direct_discovery()
                
            except ImportError as e:
                _LOGGER.error(f"Could not import discovery function: {e}")
                # Fallback to direct discovery
                self._discovered_calendars = self._direct_discovery()
            
            # Organize calendars by category
            self._categories = defaultdict(list)
            for cal_id, cal_data in self._discovered_calendars.items():
                category = cal_data['info'].get('category', 'uncategorized')
                self._categories[category].append((cal_id, cal_data))
            
            # Sort categories for consistent ordering
            self._category_list = sorted(self._categories.keys())
            
            _LOGGER.info(f"Config flow discovered {len(self._discovered_calendars)} calendars in {len(self._categories)} categories")

    def _direct_discovery(self) -> Dict[str, Any]:
        """Direct discovery of calendars as fallback."""
        import os
        import sys
        from importlib import import_module
        
        calendars = {}
        
        # Get the calendars directory path
        base_dir = os.path.dirname(__file__)
        calendars_dir = os.path.join(base_dir, 'calendars')
        
        if not os.path.exists(calendars_dir):
            _LOGGER.error(f"Calendars directory not found for config flow: {calendars_dir}")
            return calendars
        
        _LOGGER.debug(f"Config flow scanning calendars directory: {calendars_dir}")
        
        # Add to path if needed
        if calendars_dir not in sys.path:
            sys.path.insert(0, calendars_dir)
        
        try:
            files = os.listdir(calendars_dir)
            _LOGGER.debug(f"Config flow found files: {files}")
        except Exception as e:
            _LOGGER.error(f"Error listing calendars directory in config flow: {e}")
            return calendars
        
        for filename in files:
            if filename.endswith('.py') and not filename.startswith('__'):
                module_name = filename[:-3]
                
                try:
                    # Try to import the module
                    try:
                        module = import_module(f'.calendars.{module_name}', package='custom_components.alternative_time')
                    except:
                        try:
                            module = import_module(f'custom_components.alternative_time.calendars.{module_name}')
                        except:
                            module = import_module(module_name)
                    
                    # Check for CALENDAR_INFO
                    if hasattr(module, 'CALENDAR_INFO'):
                        info = module.CALENDAR_INFO
                        calendar_id = info.get('id', module_name)
                        
                        calendars[calendar_id] = {
                            'module': module,
                            'module_name': module_name,
                            'info': info,
                            'update_interval': getattr(module, 'UPDATE_INTERVAL', 60)
                        }
                        
                        _LOGGER.debug(f"Config flow discovered: {calendar_id}")
                        
                except Exception as e:
                    _LOGGER.debug(f"Config flow could not import {module_name}: {e}")
        
        return calendars

    def _get_translated_text(self, calendar_info: Dict, key: str, language: str = "en") -> str:
        """Get translated text from calendar info."""
        texts = calendar_info.get(key, {})
        if isinstance(texts, dict):
            return texts.get(language, texts.get("en", key))
        return texts or key

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step - basic configuration."""
        if user_input is not None:
            self._data.update(user_input)
            
            # Discover calendars if not already done
            self._discover_calendars()
            
            # If no calendars discovered, show error
            if not self._discovered_calendars:
                return self.async_show_form(
                    step_id="user",
                    data_schema=self._get_base_schema(),
                    errors={"base": "no_calendars_found"},
                )
            
            # Start with first category
            self._current_category_index = 0
            if self._category_list:
                return await self._async_step_category(self._category_list[0])
            else:
                return await self.async_step_confirm()

        return self.async_show_form(
            step_id="user",
            data_schema=self._get_base_schema(),
            description_placeholders={
                "intro": "Configure Alternative Time Systems v2.5"
            },
        )

    def _get_base_schema(self) -> vol.Schema:
        """Get the base configuration schema."""
        return vol.Schema({
            vol.Required("name", default=DEFAULT_NAME): TextSelector(
                TextSelectorConfig()
            ),
        })

    async def _async_step_category(self, category: str) -> FlowResult:
        """Dynamic step for each category."""
        # Create a unique step name
        step_id = f"category_{category.replace(' ', '_').lower()}"
        
        # Register this as a step method dynamically
        if not hasattr(self, f"async_step_{step_id}"):
            setattr(self, f"async_step_{step_id}", 
                   lambda user_input=None: self._async_handle_category(category, user_input))
        
        return await self._async_handle_category(category, None)

    async def _async_handle_category(
        self, category: str, user_input: dict[str, Any] | None
    ) -> FlowResult:
        """Handle a category configuration step."""
        if user_input is not None:
            # Store the user input
            self._data.update(user_input)
            
            # Move to next category or finish
            self._current_category_index += 1
            if self._current_category_index < len(self._category_list):
                next_category = self._category_list[self._current_category_index]
                return await self._async_step_category(next_category)
            else:
                return await self.async_step_confirm()

        # Get calendars for this category
        calendars = self._categories[category]
        
        # Get user's language
        language = self.hass.config.language if hasattr(self, 'hass') else "en"
        
        # Build schema for this category
        schema_dict = {}
        
        for cal_id, cal_data in calendars:
            info = cal_data['info']
            
            # Create enable key
            enable_key = f"enable_{cal_id}"
            
            # Get translated name and description
            cal_name = self._get_translated_text(info, 'name', language)
            cal_desc = self._get_translated_text(info, 'description', language)
            
            # Add to schema with description as label
            schema_dict[vol.Required(
                enable_key, 
                default=False,
                description={"suggested_value": False}
            )] = BooleanSelector()
            
            # Add special options if needed
            if cal_id == 'timezone':
                # Add timezone selector
                timezone_list = sorted(pytz.all_timezones)
                schema_dict[vol.Optional('timezone', default='UTC')] = SelectSelector(
                    SelectSelectorConfig(
                        options=timezone_list,
                        mode=SelectSelectorMode.DROPDOWN,
                    )
                )
            elif cal_id == 'mars' or cal_id == 'mars_time':
                # Add Mars timezone selector
                schema_dict[vol.Optional('mars_timezone', default='MTC')] = SelectSelector(
                    SelectSelectorConfig(
                        options=MARS_TIMEZONES,
                        mode=SelectSelectorMode.DROPDOWN,
                    )
                )
            
            # Check for custom config options in calendar info
            if 'config_options' in info:
                for option_key, option_config in info['config_options'].items():
                    full_key = f"{cal_id}_{option_key}"
                    
                    # Build the selector based on option type
                    if option_config['type'] == 'select':
                        schema_dict[vol.Optional(
                            full_key, 
                            default=option_config.get('default')
                        )] = SelectSelector(
                            SelectSelectorConfig(
                                options=option_config['options'],
                                mode=SelectSelectorMode.DROPDOWN,
                            )
                        )
                    elif option_config['type'] == 'boolean':
                        schema_dict[vol.Required(
                            full_key,
                            default=option_config.get('default', False)
                        )] = BooleanSelector()
                    else:
                        # Default to text
                        schema_dict[vol.Optional(
                            full_key,
                            default=option_config.get('default', '')
                        )] = TextSelector(TextSelectorConfig())

        # Create form schema
        data_schema = vol.Schema(schema_dict)
        
        # Category title and description
        category_title = category.replace('_', ' ').title()
        
        # Count calendars in this category
        cal_count = len(calendars)
        
        # Build description with calendar names
        cal_names = [self._get_translated_text(cal[1]['info'], 'name', language) 
                    for cal in calendars]
        
        return self.async_show_form(
            step_id=f"category_{category.replace(' ', '_').lower()}",
            data_schema=data_schema,
            description_placeholders={
                "category": category_title,
                "count": str(cal_count),
                "calendars": ", ".join(cal_names),
                "progress": f"{self._current_category_index + 1}/{len(self._category_list)}"
            },
        )

    async def async_step_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the confirmation step."""
        if user_input is not None:
            # User confirmed, create the entry
            title = self._data.get('name', DEFAULT_NAME)
            
            # Log what was configured
            enabled_calendars = [
                key[7:] for key, value in self._data.items() 
                if key.startswith('enable_') and value
            ]
            _LOGGER.info(f"Creating config entry with {len(enabled_calendars)} calendars: {enabled_calendars}")
            
            return self.async_create_entry(title=title, data=self._data)

        # Build summary of selected calendars
        language = self.hass.config.language if hasattr(self, 'hass') else "en"
        selected_calendars = []
        
        for key, value in self._data.items():
            if key.startswith('enable_') and value:
                cal_id = key[7:]  # Remove 'enable_' prefix
                
                # Find calendar info
                if cal_id in self._discovered_calendars:
                    info = self._discovered_calendars[cal_id]['info']
                    cal_name = self._get_translated_text(info, 'name', language)
                    selected_calendars.append(cal_name)

        # Group selected calendars by category for display
        selected_by_category = defaultdict(list)
        for key, value in self._data.items():
            if key.startswith('enable_') and value:
                cal_id = key[7:]
                if cal_id in self._discovered_calendars:
                    info = self._discovered_calendars[cal_id]['info']
                    category = info.get('category', 'uncategorized')
                    cal_name = self._get_translated_text(info, 'name', language)
                    selected_by_category[category].append(cal_name)
        
        # Build summary text
        summary_lines = []
        for category in sorted(selected_by_category.keys()):
            cals = selected_by_category[category]
            summary_lines.append(f"{category.title()}: {', '.join(cals)}")
        
        summary_text = "\n".join(summary_lines) if summary_lines else "No calendars selected"

        return self.async_show_form(
            step_id="confirm",
            description_placeholders={
                "name": self._data.get('name', DEFAULT_NAME),
                "count": str(len(selected_calendars)),
                "summary": summary_text,
            },
        )

    @staticmethod
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Alternative Time with auto-discovery."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry
        self._discovered_calendars = None
        self._data = {}

    def _discover_calendars(self):
        """Discover available calendars."""
        if self._discovered_calendars is None:
            try:
                from .sensor import export_discovered_calendars
                self._discovered_calendars = export_discovered_calendars()
            except ImportError:
                _LOGGER.error("Could not import discovery function in options flow")
                self._discovered_calendars = {}
            
            _LOGGER.info(f"Options flow discovered {len(self._discovered_calendars)} calendars")

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            # Check if at least one calendar is enabled
            enabled = [k for k, v in user_input.items() if k.startswith('enable_') and v]
            
            if not enabled:
                return self.async_show_form(
                    step_id="init",
                    data_schema=self._build_options_schema(),
                    errors={"base": "no_systems_selected"},
                )
            
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=self._build_options_schema(),
        )

    def _build_options_schema(self) -> vol.Schema:
        """Build options schema from discovered calendars."""
        self._discover_calendars()
        
        # Get current configuration
        current_data = self.config_entry.options or self.config_entry.data
        
        # Get user's language
        language = self.hass.config.language if hasattr(self, 'hass') else "en"
        
        schema_dict = {}
        
        # Group calendars by category
        categories = defaultdict(list)
        for cal_id, cal_data in self._discovered_calendars.items():
            category = cal_data['info'].get('category', 'uncategorized')
            categories[category].append((cal_id, cal_data))
        
        # Build schema for each category
        for category in sorted(categories.keys()):
            for cal_id, cal_data in categories[category]:
                info = cal_data['info']
                enable_key = f"enable_{cal_id}"
                
                # Add enable option
                schema_dict[vol.Required(
                    enable_key,
                    default=current_data.get(enable_key, False)
                )] = BooleanSelector()
                
                # Add special options
                if cal_id == 'timezone' and current_data.get(enable_key, False):
                    timezone_list = sorted(pytz.all_timezones)
                    schema_dict[vol.Optional(
                        'timezone',
                        default=current_data.get('timezone', 'UTC')
                    )] = SelectSelector(
                        SelectSelectorConfig(
                            options=timezone_list,
                            mode=SelectSelectorMode.DROPDOWN,
                        )
                    )
                elif (cal_id == 'mars' or cal_id == 'mars_time') and current_data.get(f"enable_{cal_id}", False):
                    schema_dict[vol.Optional(
                        'mars_timezone',
                        default=current_data.get('mars_timezone', 'MTC')
                    )] = SelectSelector(
                        SelectSelectorConfig(
                            options=MARS_TIMEZONES,
                            mode=SelectSelectorMode.DROPDOWN,
                        )
                    )
        
        return vol.Schema(schema_dict)