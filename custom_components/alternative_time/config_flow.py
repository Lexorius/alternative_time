"""Config flow for Alternative Time Systems integration."""
from __future__ import annotations

import os
import logging
from typing import Any, Dict, List, Optional
from importlib import import_module
import asyncio

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.selector import SelectSelector, SelectSelectorConfig, SelectSelectorMode

from .const import DOMAIN

# Fixed category order for the wizard
FIXED_CATEGORY_ORDER = [
    'technical', 'historical', 'cultural', 'military', 'space', 'fantasy', 'scifi', 'religion','gaming', 'uncategorized'
]

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema({
    vol.Required("name", default="Alternative Time"): str,
})


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    return {"title": data.get("name", "Alternative Time")}


def format_key_name(key: str) -> str:
    """Format a key name to be more readable."""
    # Replace underscores with spaces and capitalize words
    formatted = key.replace('_', ' ')
    # Capitalize first letter of each word
    formatted = ' '.join(word.capitalize() for word in formatted.split())
    return formatted


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
        # NEU: Mapping von Display-Keys zu Original-Keys
        self._option_key_mapping: Dict[str, str] = {}

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

    def _lcal(self, info: dict, key: str, default: str = "", lang: str = None) -> str:
        """Get localized value from calendar info."""
        val = info.get(key, {})
        if isinstance(val, dict):
            # Try to get user's language first, fallback to English
            if lang is None:
                try:
                    lang = self.hass.config.language
                except:
                    lang = 'en'
            return val.get(lang, val.get("en", default))
        return str(val or default)

    def _build_groups(self, calendars: List[str], discovered: Dict[str, Dict[str, Any]]) -> Dict[str, List[str]]:
        """Build device groups based on calendar categories."""
        groups = {}
        for cal_id in calendars:
            info = discovered.get(cal_id, {})
            category = str(info.get("category", "uncategorized"))
            if category == "religious":
                category = "religion"
            if category not in groups:
                groups[category] = []
            groups[category].append(cal_id)
        return groups

    def _details_text(self, discovered: Dict[str, Dict[str, Any]]) -> str:
        """Generate a details text for a set of discovered calendars."""
        lines = []
        for cid, info in sorted(discovered.items()):
            name = self._lcal(info, "name", default=cid)
            desc = self._lcal(info, "description", default="")
            line = f"• {name}"
            if desc:
                line += f": {desc}"
            lines.append(line)
        return "\n".join(lines) if lines else "No calendars found"

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            # Discover calendars asynchronously
            await self._async_discover_calendars()
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        errors = {}

        try:
            info = await validate_input(self.hass, user_input)
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            return self.async_show_form(
                step_id="user", 
                data_schema=STEP_USER_DATA_SCHEMA, 
                errors={"base": "unknown"}
            )
        
        # Store user input and move to category selection
        self._user_input = user_input
        await self._async_discover_calendars()
        return await self.async_step_select_categories()

    async def async_step_select_categories(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Step to select which categories to configure."""
        categories = self._categories()
        if not categories:
            return self.async_abort(reason="no_calendars_found")
        
        if user_input is None:
            options = [{"label": c.title(), "value": c} for c in categories]
            schema = vol.Schema({
                vol.Required("categories", default=categories): SelectSelector(
                    SelectSelectorConfig(
                        options=options, 
                        multiple=True, 
                        mode=SelectSelectorMode.LIST  # FIX: Geändert von DROPDOWN zu LIST
                    )
                )
            })
            return self.async_show_form(
                step_id="select_categories", 
                data_schema=schema,
                description_placeholders={
                    "details": self._details_text(self._discovered_calendars)
                }
            )
        
        # Save and proceed
        selected = user_input.get("categories") or []
        self._selected_categories = [c for c in selected if c in categories]
        self._category_order = [c for c in FIXED_CATEGORY_ORDER if c in self._selected_categories]
        self._category_index = 0
        self._selected_calendars = []
        return await self.async_step_select_calendars_by_category()

    async def async_step_select_calendars_by_category(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Iterate category list and collect calendars with checkbox UI and detailed labels."""
        
        # Process user input if we're coming back from a form
        if user_input is not None and self._category_index > 0:
            # Save selected for previous category
            selected = list(user_input.get("calendars") or [])
            # Get calendars from previous category
            prev_cat = self._category_order[self._category_index - 1]
            prev_cals = [
                cid for cid, info in (self._discovered_calendars or {}).items() 
                if str(info.get("category") or "uncategorized").replace("religious", "religion") == prev_cat
            ]
            selected = [cid for cid in selected if cid in prev_cals]
            
            # Merge with existing selections
            merged = [c for c in self._selected_calendars if c not in prev_cals]
            merged.extend(selected)
            self._selected_calendars = merged
        
        # Check if we're done with all categories
        if self._category_index >= len(self._category_order):
            # Done with categories -> go to plugin options
            self._option_calendars = [
                cid for cid in self._selected_calendars 
                if isinstance(
                    (self._discovered_calendars.get(cid, {}) or {}).get("config_options"), 
                    dict
                ) and len((self._discovered_calendars.get(cid, {}) or {}).get("config_options", {})) > 0
            ]
            self._option_index = 0
            
            if self._option_calendars:
                return await self.async_step_plugin_options()
            
            data = {
                **self._user_input,
                "calendars": self._selected_calendars,
                "groups": self._build_groups(self._selected_calendars, self._discovered_calendars)
            }
            return self.async_create_entry(
                title=self._user_input.get("name", "Alternative Time"), 
                data=data
            )

        current_cat = self._category_order[self._category_index]
        
        # Calendars in this category
        cals = [
            (cid, info) for cid, info in (self._discovered_calendars or {}).items() 
            if str(info.get("category") or "uncategorized").replace("religious", "religion") == current_cat
        ]
        
        # If category is empty, skip to next
        if not cals:
            self._category_index += 1
            return await self.async_step_select_calendars_by_category()
        
        # Build labels with separators between items
        options_dict = {}
        separator = "─" * 50  # Visual separator
        
        for i, (cid, info) in enumerate(sorted(cals)):
            name = self._lcal(info, "name", default=cid)
            desc = self._lcal(info, "description", default="")
            upd = info.get("update_interval")
            upd_txt = f"{int(upd)}s" if isinstance(upd, (int, float)) else ""
            acc = str(info.get("accuracy") or "")
            
            # Build extra info line
            extra_parts = []
            if upd_txt:
                extra_parts.append(f"Update: {upd_txt}")
            if acc:
                extra_parts.append(f"Accuracy: {acc}")
            extra = " • ".join(extra_parts)
            
            # Format the label with proper line breaks
            label_parts = []
            label_parts.append(name)
            if desc:
                label_parts.append(f"\n  ↳ {desc}")
            if extra:
                label_parts.append(f"\n  ↳ {extra}")
            
            # Add separator after each item except the last
            if i < len(cals) - 1:
                label_parts.append(f"\n  {separator}")
            
            label = "".join(label_parts)
            options_dict[cid] = label
        
        # Defaults: keep already chosen in this category, else select all
        already = [cid for cid, _ in cals if cid in self._selected_calendars]
        default = already or [cid for cid, _ in cals]
        
        schema = vol.Schema({
            vol.Required("calendars", default=default): cv.multi_select(options_dict)
        })
        
        # Increment index for next iteration
        self._category_index += 1
        
        return self.async_show_form(
            step_id="select_calendars_by_category",
            data_schema=schema,
            description_placeholders={
                "category": current_cat.title(),
                "details": self._details_text(dict(cals))
            }
        )

    async def async_step_plugin_options(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Iterate selected calendars that expose CALENDAR_INFO['config_options'] and collect values."""
        
        # Process user input from previous form
        if user_input is not None and self._option_index > 0:
            # Store data from the previous calendar
            prev_cal_id = self._option_calendars[self._option_index - 1]
            
            # Process the user input for the previous calendar
            cal_options = {}
            
            _LOGGER.debug(f"Processing options for {prev_cal_id}, raw input: {user_input}")
            _LOGGER.debug(f"Key mapping: {self._option_key_mapping}")
            
            # Verwende das Key-Mapping um die Original-Keys wiederherzustellen
            for display_key, value in user_input.items():
                if display_key in self._option_key_mapping:
                    original_key = self._option_key_mapping[display_key]
                    # WICHTIG: Bei Select-Feldern könnte der Wert None sein wenn nichts ausgewählt
                    if value is not None:
                        cal_options[original_key] = value
                        _LOGGER.debug(f"Mapped {display_key} -> {original_key} = {value}")
                else:
                    _LOGGER.warning(f"No mapping found for display key: {display_key}")
            
            # Store in selected_options with the actual calendar id
            if cal_options:
                self._selected_options[prev_cal_id] = cal_options
                _LOGGER.debug(f"Stored options for {prev_cal_id}: {cal_options}")
        
        # Check if we're done with all option calendars
        if self._option_index >= len(self._option_calendars):
            # Done - create the entry with all options
            data = {
                **self._user_input,
                "calendars": self._selected_calendars,
                "groups": self._build_groups(self._selected_calendars, self._discovered_calendars),
                "calendar_options": self._selected_options  # Add per-calendar options
            }
            _LOGGER.debug(f"Creating entry with calendar_options: {self._selected_options}")
            return self.async_create_entry(
                title=self._user_input.get("name", "Alternative Time"), 
                data=data
            )
        
        # Get current calendar to configure
        cid = self._option_calendars[self._option_index]
        info = self._discovered_calendars.get(cid, {})
        name = self._lcal(info, "name", default=cid)
        
        # Get config options for this calendar
        config_opts = info.get("config_options", {})
        
        # Clear mapping for new calendar
        self._option_key_mapping = {}
        
        # Build schema for this calendar's options
        schema_dict = {}
        for key, config in (config_opts or {}).items():
            try:
                # Get the display label (but keep the original key for later)
                label = config.get("label")
                if isinstance(label, dict):
                    try:
                        user_lang = self.hass.config.language
                    except:
                        user_lang = 'en'
                    pretty_key = label.get(user_lang, label.get("en", format_key_name(key)))
                elif label:
                    pretty_key = label
                else:
                    # Format the key name to be more readable
                    pretty_key = format_key_name(key)
                
                # Full display key with plugin name prefix
                full_display_key = f"[{name}] {pretty_key}"
                
                # WICHTIG: Speichere das Mapping von Display-Key zu Original-Key
                self._option_key_mapping[full_display_key] = key
                
                typ = config.get("type", "string")
                default = config.get("default")
                
                # Get the translated description
                desc = config.get("description", "")
                if isinstance(desc, dict):
                    try:
                        user_lang = self.hass.config.language
                    except:
                        user_lang = 'en'
                    desc_text = desc.get(user_lang, desc.get("en", ""))
                else:
                    desc_text = desc if desc else ""
                
                _LOGGER.debug(f"Building field {key} ({full_display_key}): type={typ}, default={default}")
                
                # Build field based on type
                if typ == "bool" or typ == "boolean":
                    default_bool = bool(default) if default is not None else False
                    schema_dict[vol.Optional(full_display_key, default=default_bool, description=desc_text)] = bool
                    
                elif typ == "int" or typ == "integer":
                    default_num = int(default) if default is not None else 0
                    min_val = config.get("min")
                    max_val = config.get("max")
                    
                    if min_val is not None and max_val is not None:
                        schema_dict[vol.Optional(full_display_key, default=default_num, description=desc_text)] = vol.All(
                            vol.Coerce(int),
                            vol.Range(min=min_val, max=max_val)
                        )
                    else:
                        schema_dict[vol.Optional(full_display_key, default=default_num, description=desc_text)] = vol.Coerce(int)
                        
                elif typ == "float" or typ == "number":
                    default_num = float(default) if default is not None else 0.0
                    schema_dict[vol.Optional(full_display_key, default=default_num, description=desc_text)] = vol.Coerce(float)
                
                elif typ == "select":
                    # Handle select with options
                    options = config.get("options", [])
                    if options:
                        # WICHTIG: Bei Integer-Options müssen wir sie als Strings behandeln
                        select_options = []
                        for opt in options:
                            if isinstance(opt, dict):
                                # Option has its own label/value structure
                                select_options.append(opt)
                            else:
                                # Simple value - convert to string for display
                                opt_str = str(opt)
                                select_options.append({"label": opt_str, "value": opt_str})
                        
                        # Convert default to string if it exists
                        default_str = str(default) if default is not None else ""
                        
                        # Ensure default is in options
                        option_values = [o["value"] for o in select_options]
                        if default_str not in option_values and option_values:
                            default_str = option_values[0]
                        
                        _LOGGER.debug(f"Select field {key}: options={select_options}, default={default_str}")
                        
                        # Use vol.In validator with string values
                        schema_dict[vol.Optional(full_display_key, default=default_str, description=desc_text)] = vol.In(option_values)
                    else:
                        # Fallback to string if no options
                        schema_dict[vol.Optional(full_display_key, default=str(default) if default is not None else "", description=desc_text)] = str
                        
                elif typ == "string" or typ == "text":
                    schema_dict[vol.Optional(full_display_key, default=str(default) if default is not None else "", description=desc_text)] = str
                    
                else:
                    # Fallback for unknown types
                    _LOGGER.warning(f"Unknown config option type '{typ}' for {key} in {cid}, using string")
                    schema_dict[vol.Optional(full_display_key, default=str(default) if default is not None else "", description=desc_text)] = str
                    
            except Exception as e:
                _LOGGER.error(f"Error building schema for {key} in {cid}: {e}", exc_info=True)
                continue
        
        # If no valid options, skip to next
        if not schema_dict:
            _LOGGER.debug(f"No valid config options for {cid}, skipping")
            self._option_index += 1
            return await self.async_step_plugin_options()
        
        # Increment index for next iteration
        self._option_index += 1
        
        schema = vol.Schema(schema_dict)
        
        return self.async_show_form(
            step_id="plugin_options",
            data_schema=schema,
            description_placeholders={
                "plugin": name,
                "details": self._details_text({cid: info}),
                "description": f"Configure options for {name}"
            }
        )

    async def _async_discover_calendars(self) -> None:
        """Discover available calendar implementations asynchronously."""
        try:
            # Try to import from sensor module first (if already loaded)
            try:
                from .sensor import export_discovered_calendars
                discovered = await self.hass.async_add_executor_job(
                    export_discovered_calendars
                )
                if discovered:
                    self._discovered_calendars = discovered
                    return
            except ImportError:
                pass

            # Fallback to direct discovery
            self._discovered_calendars = await self._async_direct_discovery()
            
        except Exception as e:
            _LOGGER.error(f"Failed to discover calendars: {e}")
            self._discovered_calendars = {}

    async def _async_direct_discovery(self) -> Dict[str, Dict[str, Any]]:
        """Directly discover calendar modules from the calendars directory asynchronously."""
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
                    # Import module asynchronously
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
            # Try different import methods
            try:
                module = import_module(f'.calendars.{module_name}', package='custom_components.alternative_time')
            except ImportError:
                try:
                    module = import_module(f'custom_components.alternative_time.calendars.{module_name}')
                except ImportError:
                    module = import_module(module_name)
            
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
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        # Discover available calendars
        discovered_calendars = await self._async_discover_calendars()
        
        # Get currently selected calendars
        current_calendars = self.config_entry.data.get("calendars", [])
        
        # Create schema for calendar selection
        calendar_schema = {}
        for cal_id, cal_info in sorted(discovered_calendars.items()):
            name = cal_info.get("name", {}).get("en", cal_id)
            description = cal_info.get("description", {}).get("en", "")
            label = f"{name}"
            if description:
                label = f"{name} - {description[:50]}..."
            default = cal_id in current_calendars
            calendar_schema[vol.Optional(cal_id, default=default)] = bool

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(calendar_schema)
        )

    async def _async_discover_calendars(self) -> Dict[str, Dict[str, Any]]:
        """Discover available calendar implementations asynchronously."""
        discovered = {}
        
        # Get calendars directory path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        calendars_dir = os.path.join(current_dir, "calendars")
        
        if not os.path.exists(calendars_dir):
            return discovered

        # List files asynchronously
        files = await self.hass.async_add_executor_job(
            os.listdir, calendars_dir
        )
        
        for filename in files:
            if filename.endswith(".py") and not filename.startswith("__"):
                module_name = filename[:-3]
                
                # Skip template and example files
                if "template" in module_name.lower() or "example" in module_name.lower():
                    continue
                
                try:
                    # Import module asynchronously
                    module = await self.hass.async_add_executor_job(
                        self._import_calendar_module, module_name
                    )
                    
                    if module and hasattr(module, 'CALENDAR_INFO'):
                        cal_info = module.CALENDAR_INFO
                        cal_id = cal_info.get('id', module_name)
                        discovered[cal_id] = cal_info
                        
                except Exception as e:
                    _LOGGER.debug(f"Failed to load calendar {module_name}: {e}")
                    continue
        
        return discovered
    
    def _import_calendar_module(self, module_name: str):
        """Import a calendar module (blocking operation for executor)."""
        try:
            module = import_module(f'.calendars.{module_name}', package='custom_components.alternative_time')
            return module
        except Exception:
            return None