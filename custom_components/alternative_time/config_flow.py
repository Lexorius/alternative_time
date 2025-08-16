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

    def _categories(self) -> List[str]:
        cats = set()
        for _cid, info in (self._discovered_calendars or {}).items():
            cat = str((info or {}).get("category") or "uncategorized")
            if cat == "religious":
                cat = "religion"
            cats.add(cat)
        # Intersect with fixed order to get a stable sequence
        ordered = [c for c in FIXED_CATEGORY_ORDER if c in cats]
        return ordered

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
            return self.async_show_form(step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors={"base": "unknown"})
        # Store user input and move to category selection
        self._user_input = user_input
        await self._async_discover_calendars()
        return await self.async_step_select_categories()

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


    async def async_step_select_categories(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Step to select which categories to configure."""
        categories = self._categories()
        if not categories:
            return self.async_abort(reason="no_calendars_found")
        if user_input is None:
            options = [{"label": c.title(), "value": c} for c in categories]
            schema = vol.Schema({
                vol.Required("categories", default=categories): SelectSelector(
                    SelectSelectorConfig(options=options, multiple=True, mode=SelectSelectorMode.DROPDOWN)
                )
            })
            return self.async_show_form(step_id="select_categories", data_schema=schema,
                description_placeholders={
                    "details": getattr(self, "_details_text", lambda d: "")(self._discovered_calendars)
                })
        # Save and proceed
        selected = user_input.get("categories") or []
        self._selected_categories = [c for c in selected if c in categories]
        self._category_order = [c for c in FIXED_CATEGORY_ORDER if c in self._selected_categories]
        self._category_index = 0
        self._selected_calendars = []
        return await self.async_step_select_calendars_by_category()

    async def async_step_select_calendars_by_category(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Iterate category list and collect calendars with checkbox UI and detailed labels."""
        if self._category_index >= len(self._category_order):
            # Done with categories -> go to plugin options
            self._option_calendars = [cid for cid in self._selected_calendars if isinstance((self._discovered_calendars.get(cid, {}) or {}).get("config_options"), dict)]
            self._option_index = 0
            if self._option_calendars:
                return await self.async_step_plugin_options()
            data = { **getattr(self, "_user_input", {}), "calendars": self._selected_calendars,
                     "groups": getattr(self, "_build_groups", lambda a,b: {})(self._selected_calendars, self._discovered_calendars) }
            return self.async_create_entry(title=self._user_input.get("name", "Alternative Time"), data=data)

        current_cat = self._category_order[self._category_index]
        # Calendars in this category
        cals = [(cid, info) for cid, info in (self._discovered_calendars or {}).items() if str(info.get("category") or "uncategorized").replace("religious","religion")==current_cat]
        # Build labels: Name — Description
        options_dict = {}
        for cid, info in sorted(cals):
            name = getattr(self, "_lcal", lambda i,k,default="": (i.get("name",{}) or {}).get("en", cid))(info, "name", default=cid)
            desc = getattr(self, "_lcal", lambda i,k,default="": (i.get("description",{}) or {}).get("en",""))(info, "description", default="")
            label = f"{name} — {desc}" if desc else name
            options_dict[cid] = label
        # Defaults: keep already chosen in this category, else select all
        already = [cid for cid,_ in cals if cid in self._selected_calendars]
        default = already or [cid for cid,_ in cals]
        schema = vol.Schema({
            vol.Required("calendars", default=default): cv.multi_select(options_dict)
        })
        if user_input is None:
            return self.async_show_form(
                step_id="select_calendars_by_category",
                data_schema=schema,
                description_placeholders={
                    "category": current_cat.title(),
                    "details": getattr(self, "_details_text", lambda d: "")(dict(cals))
                }
            )
        # Save selected for this category and continue
        selected = user_input.get("calendars") or []
        selected = [cid for cid in selected if any(cid==x[0] for x in cals)]
        merged = [c for c in self._selected_calendars if c not in selected]
        merged.extend(selected)
        self._selected_calendars = merged
        self._category_index += 1
        return await self.async_step_select_calendars_by_category()

    async def async_step_plugin_options(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Iterate selected calendars that expose CALENDAR_INFO['config_options'] and collect values."""
        # If returning from a previous plugin form, store data
        if user_input is not None and self._option_index > 0:
            prev_cid = self._option_calendars[self._option_index - 1]
            self._selected_options[prev_cid] = user_input

        # Are we done with all option-bearing calendars?
        if self._option_index >= len(self._option_calendars):
            data = { **getattr(self, "_user_input", {}), "calendars": self._selected_calendars,
                     "groups": getattr(self, "_build_groups", lambda a,b: {})(self._selected_calendars, self._discovered_calendars),
                     "plugin_options": self._selected_options }
            return self.async_create_entry(title=self._user_input.get("name", "Alternative Time"), data=data)

        cid = self._option_calendars[self._option_index]
        info = self._discovered_calendars.get(cid, {}) or {}
        opts = info.get("config_options") or {}
        # Build schema dynamically
        schema_dict = {}
        for key, meta in (opts or {}).items():
            typ = (meta or {}).get("type")
            default = (meta or {}).get("default")
            desc = getattr(self, "_lcal", lambda i,k,default="": (meta.get("description",{}) or {}).get("en",""))(meta, "description", default="")
            if typ == "boolean":
                schema_dict[vol.Optional(f"{key}", default=bool(default) if default is not None else False)] = bool
            elif typ == "select":
                options = (meta or {}).get("options") or []
                opt_objs = [{"label": str(o), "value": o} for o in options]
                schema_dict[vol.Optional(f"{key}", default=default)] = SelectSelector(SelectSelectorConfig(options=opt_objs, multiple=False, mode=SelectSelectorMode.DROPDOWN))
            elif typ == "number":
                # Accept int/float; coerce to float
                schema_dict[vol.Optional(f"{key}", default=default if default is not None else 0)] = vol.Coerce(float)
            else:
                # string/free text
                schema_dict[vol.Optional(f"{key}", default=default if default is not None else "")] = str

        # Show form for this plugin
        name = getattr(self, "_lcal", lambda i,k,default="": (info.get("name",{}) or {}).get("en", cid))(info, "name", default=cid)
        desc = getattr(self, "_lcal", lambda i,k,default="": (info.get("description",{}) or {}).get("en",""))(info, "description", default="")
        schema = vol.Schema(schema_dict)
        self._option_index += 1
        return self.async_show_form(
            step_id="plugin_options",
            data_schema=schema,
            description_placeholders={
                "plugin": name,
                "details": getattr(self, "_details_text", lambda d: "")({cid: info}),
                "description": desc
            }
        )

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