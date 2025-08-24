"""Config flow for Alternative Time Systems integration."""
from __future__ import annotations

import os
import logging
from typing import Any, Dict, List, Optional
import asyncio
import importlib
import sys

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.selector import (
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
    BooleanSelector
)

from .const import DOMAIN

# Fixed category order for the wizard
FIXED_CATEGORY_ORDER = [
    'technical', 'historical', 'cultural', 'military', 'space', 'fantasy', 'scifi', 'religion', 'uncategorized', 'gaming'
]

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema({
    vol.Required("name", default="Alternative Time"): str,
})


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    return {"title": data.get("name", "Alternative Time")}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Alternative Time Systems."""

    VERSION = 1

    def __init__(self):
        """Initialize the config flow."""
        self._discovered_calendars: Dict[str, Dict[str, Any]] = {}
        self._selected_calendars: List[str] = []
        self._selected_categories: List[str] = []
        self._category_order: List[str] = []
        self._category_index: int = 0
        self._selected_options: Dict[str, Dict[str, Any]] = {}
        self._option_calendars: List[str] = []
        self._option_index: int = 0
        self._user_input: Dict[str, Any] = {}
        # Store mapping between displayed labels and actual keys for each calendar
        self._option_key_mapping: Dict[str, Dict[str, str]] = {}

    def _categories(self) -> List[str]:
        """Get list of available categories from discovered calendars."""
        cats = set()
        for _cid, info in (self._discovered_calendars or {}).items():
            cat = str((info or {}).get("category") or "uncategorized")
            if cat == "religious":
                cat = "religion"
            cats.add(cat)
        # Intersect with fixed order to get a stable sequence
        ordered = [c for c in FIXED_CATEGORY_ORDER if c in cats]
        return ordered

    def _lcal(self, info: dict, key: str, default: str = "") -> str:
        """Get localized value from calendar info or option metadata."""
        # Try the current user's language first
        lang = self.hass.config.language if self.hass else "en"
        
        # Navigate through nested dictionaries
        value = info
        for k in key.split('.'):
            if isinstance(value, dict):
                value = value.get(k, {})
            else:
                return default
        
        # If value is a dict with language keys, return the appropriate translation
        if isinstance(value, dict):
            # Try exact language match first
            if lang in value:
                return value[lang]
            # Try language without region (e.g., "en" from "en_US")
            lang_base = lang.split('_')[0].split('-')[0]
            if lang_base in value:
                return value[lang_base]
            # Fallback to English or first available
            if "en" in value:
                return value["en"]
            # Return first available translation
            if value:
                return next(iter(value.values()))
        
        # If value is a string, return it directly
        if isinstance(value, str):
            return value
        
        return default

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is not None:
            self._user_input = user_input
            # Discover calendars
            self._discovered_calendars = await self._async_discover_calendars()
            
            if not self._discovered_calendars:
                return self.async_abort(reason="no_calendars_found")
            
            # Get categories
            self._category_order = self._categories()
            
            # Go to category selection
            return await self.async_step_select_categories()

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA
        )

    async def async_step_select_categories(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Let user select which categories to configure."""
        if user_input is not None:
            selected = user_input.get("categories", [])
            if selected:
                self._selected_categories = selected
                self._category_index = 0
                # Start category-by-category selection
                return await self.async_step_select_calendars_by_category()
            else:
                # No categories selected, skip to disclaimer
                return await self.async_step_disclaimer()

        # Build category descriptions
        details = []
        for cat in self._category_order:
            count = sum(1 for info in self._discovered_calendars.values() 
                       if info.get("category", "uncategorized") == cat)
            cat_name = cat.replace('_', ' ').title()
            details.append(f"• **{cat_name}**: {count} calendars")
        
        details_text = "\n".join(details) if details else "No calendars found"

        return self.async_show_form(
            step_id="select_categories",
            description_placeholders={"details": details_text},
            data_schema=vol.Schema({
                vol.Required("categories", default=self._category_order): 
                    SelectSelector(SelectSelectorConfig(
                        options=[
                            {"value": cat, "label": cat.replace('_', ' ').title()}
                            for cat in self._category_order
                        ],
                        multiple=True,
                        mode=SelectSelectorMode.LIST
                    ))
            })
        )

    async def async_step_select_calendars_by_category(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Let user select calendars from a specific category."""
        if user_input is not None:
            # Store selected calendars
            selected = user_input.get("calendars", [])
            self._selected_calendars.extend(selected)
            
            # Move to next category
            self._category_index += 1
            
            # Check if more categories to process
            if self._category_index < len(self._selected_categories):
                return await self.async_step_select_calendars_by_category()
            
            # All categories done, configure plugins with options
            if self._selected_calendars:
                # Build list of calendars that have config options
                self._option_calendars = []
                for cal_id in self._selected_calendars:
                    cal_info = self._discovered_calendars.get(cal_id, {})
                    if cal_info.get("config_options"):
                        self._option_calendars.append(cal_id)
                
                if self._option_calendars:
                    self._option_index = 0
                    return await self.async_step_plugin_options()
            
            # No options to configure, go to disclaimer
            return await self.async_step_disclaimer()

        # Get current category
        current_category = self._selected_categories[self._category_index]
        
        # Get calendars for this category
        category_calendars = []
        for cal_id, info in self._discovered_calendars.items():
            cat = info.get("category", "uncategorized")
            if cat == current_category:
                cal_name = self._lcal(info, 'name', cal_id)
                cal_desc = self._lcal(info, 'description', '')
                category_calendars.append({
                    "id": cal_id,
                    "name": cal_name,
                    "description": cal_desc
                })
        
        # Sort by name
        category_calendars.sort(key=lambda x: x["name"])
        
        # Build details text
        details = []
        for cal in category_calendars:
            desc_preview = cal["description"][:100] + "..." if len(cal["description"]) > 100 else cal["description"]
            details.append(f"• **{cal['name']}**: {desc_preview}")
        
        details_text = "\n".join(details) if details else "No calendars in this category"
        
        # Create form
        cat_display = current_category.replace('_', ' ').title()
        
        return self.async_show_form(
            step_id="select_calendars_by_category",
            description_placeholders={
                "category": cat_display,
                "details": details_text
            },
            data_schema=vol.Schema({
                vol.Optional("calendars", default=[]): 
                    SelectSelector(SelectSelectorConfig(
                        options=[
                            {"value": cal["id"], "label": cal["name"]}
                            for cal in category_calendars
                        ],
                        multiple=True,
                        mode=SelectSelectorMode.LIST
                    ))
            })
        )

    async def async_step_plugin_options(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Configure options for calendars that have them."""
        if user_input is not None:
            # Store the options for the current calendar
            current_cal_id = self._option_calendars[self._option_index]
            
            # Convert displayed labels back to actual keys
            if current_cal_id in self._option_key_mapping:
                actual_options = {}
                mapping = self._option_key_mapping[current_cal_id]
                for display_label, value in user_input.items():
                    actual_key = mapping.get(display_label, display_label)
                    actual_options[actual_key] = value
                self._selected_options[current_cal_id] = actual_options
            else:
                self._selected_options[current_cal_id] = user_input
            
            # Move to next calendar with options
            self._option_index += 1
            
            if self._option_index < len(self._option_calendars):
                return await self.async_step_plugin_options()
            
            # All options configured, go to disclaimer
            return await self.async_step_disclaimer()

        # Get current calendar
        current_cal_id = self._option_calendars[self._option_index]
        cal_info = self._discovered_calendars.get(current_cal_id, {})
        
        # Get localized calendar name and description
        cal_name = self._lcal(cal_info, 'name', current_cal_id)
        cal_desc = self._lcal(cal_info, 'description', '')
        
        # Build schema for options
        config_options = cal_info.get("config_options", {})
        schema_dict = {}
        
        # Create mapping for this calendar
        self._option_key_mapping[current_cal_id] = {}
        
        for opt_key, opt_info in config_options.items():
            opt_type = opt_info.get("type", "text")
            opt_default = opt_info.get("default")
            opt_label = self._lcal(opt_info, 'label', opt_key)
            opt_desc = self._lcal(opt_info, 'description', '')
            
            # Store the mapping between displayed label and actual key
            self._option_key_mapping[current_cal_id][opt_label] = opt_key
            
            # Create the appropriate selector based on type
            if opt_type == "boolean":
                schema_dict[vol.Optional(opt_label, default=opt_default)] = BooleanSelector()
            
            elif opt_type == "select":
                options = opt_info.get("options", [])
                schema_dict[vol.Optional(opt_label, default=opt_default)] = SelectSelector(
                    SelectSelectorConfig(
                        options=[{"value": opt, "label": str(opt)} for opt in options],
                        mode=SelectSelectorMode.DROPDOWN
                    )
                )
            
            elif opt_type == "number":
                schema_dict[vol.Optional(opt_label, default=opt_default)] = NumberSelector(
                    NumberSelectorConfig(
                        min=opt_info.get("min", 0),
                        max=opt_info.get("max", 100),
                        step=opt_info.get("step", 1),
                        mode=NumberSelectorMode.BOX
                    )
                )
            
            else:  # text
                schema_dict[vol.Optional(opt_label, default=opt_default)] = TextSelector(
                    TextSelectorConfig(type=TextSelectorType.TEXT)
                )
        
        return self.async_show_form(
            step_id="plugin_options",
            description_placeholders={
                "calendar_name": cal_name,
                "calendar_description": cal_desc
            },
            data_schema=vol.Schema(schema_dict) if schema_dict else vol.Schema({})
        )

    async def async_step_disclaimer(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Show disclaimer and create entry."""
        if user_input is not None:
            # Create the config entry with all collected data
            # IMPORTANT: Store options as "plugin_options" to match what sensor.py expects
            data = {
                "name": self._user_input.get("name", "Alternative Time"),
                "calendars": self._selected_calendars,
                "plugin_options": self._selected_options  # Use plugin_options, NOT calendar_options!
            }
            
            title = self._user_input.get("name", "Alternative Time")
            
            # Log what we're saving
            _LOGGER.info(f"Creating config entry '{title}' with {len(self._selected_calendars)} calendars")
            _LOGGER.debug(f"Selected calendars: {self._selected_calendars}")
            _LOGGER.debug(f"Plugin options: {self._selected_options}")
            
            return self.async_create_entry(title=title, data=data)

        return self.async_show_form(
            step_id="disclaimer",
            data_schema=vol.Schema({})
        )

    async def _async_discover_calendars(self) -> Dict[str, Dict[str, Any]]:
        """Discover available calendar implementations using executor for blocking operations."""
        discovered = {}
        
        # Get calendars directory path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        calendars_dir = os.path.join(current_dir, "calendars")
        
        if not os.path.exists(calendars_dir):
            _LOGGER.warning(f"Calendars directory not found: {calendars_dir}")
            return discovered

        # List files asynchronously
        files = await self.hass.async_add_executor_job(
            os.listdir, calendars_dir
        )
        
        for filename in files:
            if filename.endswith(".py") and not filename.startswith("__"):
                module_name = filename[:-3]  # Remove .py extension
                
                # Skip template and example files
                if "template" in module_name.lower() or "example" in module_name.lower():
                    continue
                
                try:
                    # Import module asynchronously using executor
                    module = await self.hass.async_add_executor_job(
                        self._import_calendar_module, module_name
                    )
                    
                    if module and hasattr(module, 'CALENDAR_INFO'):
                        cal_info = module.CALENDAR_INFO
                        cal_id = cal_info.get('id', module_name)
                        discovered[cal_id] = cal_info
                        _LOGGER.debug(f"Discovered calendar: {cal_id}")
                        
                except Exception as e:
                    _LOGGER.warning(f"Failed to load calendar {module_name}: {e}")
                    continue
        
        _LOGGER.info(f"Discovered {len(discovered)} calendars")
        return discovered

    def _import_calendar_module(self, module_name: str):
        """Import a calendar module (blocking operation for executor)."""
        try:
            # Build the full module path
            full_module_name = f"custom_components.alternative_time.calendars.{module_name}"
            
            # Check if module is already imported
            if full_module_name in sys.modules:
                return sys.modules[full_module_name]
            
            # Import the module
            module = importlib.import_module(f".calendars.{module_name}", package="custom_components.alternative_time")
            return module
            
        except Exception as e:
            _LOGGER.error(f"Failed to import calendar module {module_name}: {e}")
            return None

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Alternative Time Systems."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow.
        
        NOTE: We store the config_entry for compatibility but don't set it
        as self.config_entry to avoid the deprecation warning in HA 2025.12.
        """
        self._config_entry = config_entry  # Use private attribute instead

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        # For now, just show the current configuration
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional(
                    "show_info",
                    default=self._config_entry.options.get("show_info", True),
                ): bool,
            })
        )