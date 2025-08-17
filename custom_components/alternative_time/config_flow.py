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
    'technical', 'historical', 'cultural', 'military', 'space', 'fantasy', 'scifi', 'religion', 'uncategorized'
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
        """Get localized value from calendar info."""
        if not info:
            return default
        
        value = info.get(key)
        if isinstance(value, dict):
            # Try to get value in user's language
            try:
                lang = getattr(self.hass.config, "language", "en")
            except:
                lang = "en"
            
            # Try exact match, then primary language, then English
            if lang in value:
                return str(value[lang])
            
            primary = lang.split("-")[0] if "-" in lang else lang
            if primary in value:
                return str(value[primary])
            
            if "en" in value:
                return str(value["en"])
            
            # Return first available translation
            if value:
                return str(next(iter(value.values())))
        
        return str(value) if value else default

    def _details_text(self, calendars: dict) -> str:
        """Generate details text for the current step."""
        if not calendars:
            return "No calendars available"
        
        lines = []
        for cal_id, info in list(calendars.items())[:3]:  # Show first 3 as preview
            name = self._lcal(info, "name", cal_id)
            desc = self._lcal(info, "description", "")
            if desc:
                lines.append(f"• {name}: {desc[:60]}...")
            else:
                lines.append(f"• {name}")
        
        if len(calendars) > 3:
            lines.append(f"... and {len(calendars) - 3} more")
        
        return "\n".join(lines) if lines else ""

    def _build_groups(self, selected_calendars: list, discovered_calendars: dict) -> dict:
        """Build groups for organizing sensors by category."""
        groups = {}
        
        for cal_id in selected_calendars:
            info = discovered_calendars.get(cal_id, {})
            category = str(info.get("category", "uncategorized"))
            
            # Normalize category names
            if category == "religious":
                category = "religion"
            
            if category not in groups:
                groups[category] = []
            
            groups[category].append(cal_id)
        
        return groups

    def _build_select_options(self, cid: str, key: str, meta: dict, info: dict) -> list[dict]:
        """Return a list of {label,value} for select fields."""
        opts = (meta or {}).get("options")
        if isinstance(opts, list) and opts:
            return [{"label": str(o), "value": o} for o in opts]
        
        # Special handling for timezone
        if key.lower() == "timezone":
            tzs = []
            # From plugin info
            tzdata = (info or {}).get("timezone_data") or {}
            
            # Handle regions dict structure
            regions = tzdata.get("regions", {})
            if isinstance(regions, dict):
                for _region, tz_list in regions.items():
                    if isinstance(tz_list, list):
                        tzs.extend([str(x) for x in tz_list])
            
            # Also check for direct timezone lists
            for _grp, arr in tzdata.items():
                if isinstance(arr, list) and _grp != "regions":
                    tzs.extend([str(x) for x in arr])
            
            # Unique preserve order
            seen = set()
            tzs_u = []
            for t in tzs:
                if t not in seen:
                    seen.add(t)
                    tzs_u.append(t)
            
            # Ensure system timezone is included and bubbled to top
            try:
                sys_tz = getattr(self.hass.config, "time_zone", None) or "UTC"
            except Exception:
                sys_tz = "UTC"
            
            if sys_tz and sys_tz not in seen:
                tzs_u.insert(0, sys_tz)
            elif sys_tz and tzs_u and tzs_u[0] != sys_tz:
                # move to front
                tzs_u = [sys_tz] + [t for t in tzs_u if t != sys_tz]
            
            if not tzs_u:
                tzs_u = ["UTC"]
            
            return [{"label": z, "value": z} for z in tzs_u]
        
        # Fallback: use default as the only option
        default = (meta or {}).get("default")
        if default is None:
            default = ""
        return [{"label": str(default), "value": default}]

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
                        mode=SelectSelectorMode.DROPDOWN
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
            selected = [cid for cid in selected if cid in [c for c, _ in [(c, None) for c in prev_cals]]]
            
            # Merge with existing selections
            merged = [c for c in self._selected_calendars if c not in [c for c, _ in [(c, None) for c in prev_cals]]]
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
                )
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
            
            # Format the label with name, description and extra info on separate lines
            label_parts = [name]
            if desc:
                label_parts.append(f"  ↳ {desc}")
            if extra:
                label_parts.append(f"  ↳ {extra}")
            
            # Add separator after each item except the last
            if i < len(cals) - 1:
                label_parts.append(f"  {separator}")
            
            label = "\n".join(label_parts)
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
            # Store data from the previous calendar (not current!)
            prev_cid = self._option_calendars[self._option_index - 1]
            normalized = {}
            
            _LOGGER.debug(f"Processing options for {prev_cid}, raw input: {user_input}")
            
            for k, v in (user_input or {}).items():
                if isinstance(k, str) and "] " in k:
                    raw_key = k.split("] ", 1)[1]
                else:
                    raw_key = k
                normalized[raw_key] = v
            
            self._selected_options[prev_cid] = normalized
            _LOGGER.debug(f"Stored options for {prev_cid}: {normalized}")

        # Check if we're done with all calendars
        if self._option_index >= len(self._option_calendars):
            # Create final data
            data = {
                **self._user_input,
                "calendars": self._selected_calendars,
                "groups": self._build_groups(self._selected_calendars, self._discovered_calendars),
                "plugin_options": self._selected_options
            }
            _LOGGER.debug(f"Creating entry with data: {data}")
            return self.async_create_entry(
                title=self._user_input.get("name", "Alternative Time"),
                data=data
            )

        # Get current calendar to configure
        cid = self._option_calendars[self._option_index]
        info = self._discovered_calendars.get(cid, {}) or {}
        opts = info.get("config_options") or {}
        
        # Skip calendars without options
        if not opts:
            _LOGGER.debug(f"Calendar {cid} has no config options, skipping")
            self._option_index += 1
            return await self.async_step_plugin_options()
        
        # Get calendar name for display
        name = self._lcal(info, "name", default=cid)
        _LOGGER.debug(f"Configuring options for calendar {cid} ({name}), options: {list(opts.keys())}")
        
        # Build schema dynamically
        schema_dict = {}
        for key, meta in opts.items():
            if not isinstance(meta, dict):
                _LOGGER.warning(f"Invalid config option metadata for {key} in {cid}")
                continue
            
            try:
                typ = meta.get("type", "string")
                default = meta.get("default")
                desc = self._lcal(meta, "description", default="")
                
                # Special handling for timezone
                if key.lower() == "timezone":
                    try:
                        sys_tz = getattr(self.hass.config, "time_zone", None) or default or "UTC"
                    except Exception:
                        sys_tz = default or "UTC"
                    default = sys_tz
                
                pretty_prefix = f"[{name}] "
                pretty_key = pretty_prefix + key
                
                _LOGGER.debug(f"Building field {key}: type={typ}, default={default}")
                
                if typ == "boolean":
                    schema_dict[vol.Optional(pretty_key, default=bool(default) if default is not None else False)] = bool
                    
                elif typ == "select":
                    options = self._build_select_options(cid, key, meta, info)
                    if options:
                        # Ensure default is in options
                        option_values = [o["value"] for o in options]
                        if default not in option_values and option_values:
                            default = option_values[0]
                        
                        schema_dict[vol.Optional(pretty_key, default=default)] = SelectSelector(
                            SelectSelectorConfig(
                                options=options, 
                                multiple=False, 
                                mode=SelectSelectorMode.DROPDOWN
                            )
                        )
                    else:
                        _LOGGER.warning(f"No options for select field {key} in {cid}")
                        
                elif typ in ("number", "integer", "float"):
                    # Handle min/max if present
                    min_val = meta.get("min")
                    max_val = meta.get("max")
                    default_num = float(default) if default is not None else 0.0
                    
                    if min_val is not None and max_val is not None:
                        schema_dict[vol.Optional(pretty_key, default=default_num)] = vol.All(
                            vol.Coerce(float),
                            vol.Range(min=float(min_val), max=float(max_val))
                        )
                    else:
                        schema_dict[vol.Optional(pretty_key, default=default_num)] = vol.Coerce(float)
                        
                elif typ == "string" or typ == "text":
                    schema_dict[vol.Optional(pretty_key, default=str(default) if default is not None else "")] = str
                    
                else:
                    # Fallback for unknown types
                    _LOGGER.warning(f"Unknown config option type '{typ}' for {key} in {cid}, using string")
                    schema_dict[vol.Optional(pretty_key, default=str(default) if default is not None else "")] = str
                    
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
            
