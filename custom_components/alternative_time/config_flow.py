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

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema({
    vol.Required("name", default="Alternative Time"): str,
})


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    return {"title": data.get("name", "Alternative Time")}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Alternative Time Systems."""

    # -----------------------------
    # Grouping & details helpers
    # -----------------------------
    def _build_groups(self, selected_ids: list[str], info_map: dict[str, dict]) -> dict[str, list[str]]:
        """Return mapping {category: [ids...]} for selected calendars."""
        groups: dict[str, list[str]] = {}
        for cid in selected_ids:
            info = (info_map or {}).get(cid, {}) or {}
            cat = str(info.get("category") or "uncategorized")
            # Normalize common synonyms
            if cat == "religious":
                cat = "religion"
            groups.setdefault(cat, []).append(cid)
        for k in list(groups):
            groups[k] = sorted(groups[k])
        return groups

    def _details_text(self, discovered: dict[str, dict]) -> str:
        """Build a compact details string for the form description."""
        try:
            lines = []
            # Category counts
            cat_counts: dict[str, int] = {}
            for cid, info in (discovered or {}).items():
                cat = str(info.get("category") or "uncategorized")
                cat_counts[cat] = cat_counts.get(cat, 0) + 1
            if cat_counts:
                cats_line = ", ".join(f"{c} ({n})" for c, n in sorted(cat_counts.items()))
                lines.append(f"Categories: {cats_line}")
            # Per-calendar details
            for cid, info in sorted((discovered or {}).items()):
                name = self._lcal(info, "name", default=cid) if hasattr(self, "_lcal") else (info.get("name", {}) or {}).get("en", cid)
                cat = str(info.get("category") or "?")
                ver = str(info.get("version") or "")
                acc = str(info.get("accuracy") or "")
                upd = info.get("update_interval")
                upd_txt = f"{upd}s" if isinstance(upd, (int, float)) else str(upd or "")
                lines.append(f"- {name} [{cid}] — cat={cat}, v={ver}, acc={acc}, update={upd_txt}")
            return "\n".join(lines)
        except Exception:
            return ""

    # -----------------------------
    # Localization helpers
    # -----------------------------
    def _lang(self) -> str:
        """Return HA language like 'de-DE' or fallback 'en'."""
        try:
            lang = getattr(self.hass.config, "language", None) or "en"
        except Exception:
            lang = "en"
        return str(lang).lower()

    def _lcal(self, info: dict, key: str, *, default: str = "") -> str:
        """Localized lookup from a CALENDAR_INFO mapping block (e.g. 'name', 'description')."""
        block = (info or {}).get(key, {})
        if isinstance(block, dict):
            lang = self._lang()
            if lang in block:
                return str(block[lang])
            primary = lang.split("-")[0]
            if primary in block:
                return str(block[primary])
            if "en" in block:
                return str(block["en"])
            if block:
                return str(next(iter(block.values())))
            return default
        return str(block) if block else default

    VERSION = 1

    def __init__(self):
        """Initialize the config flow."""
        self._discovered_calendars: Dict[str, Dict[str, Any]] = {}
        self._selected_calendars: List[str] = []

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            # Discover calendars asynchronously
            await self._async_discover_calendars()
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA,
                description_placeholders={
                    "available_calendars": ", ".join(
                        sorted(self._lcal(ci, "name", default=cid) for cid, ci in self._discovered_calendars.items())
                    )
                ,
                    "details": self._details_text(self._discovered_calendars)
                }
            )

        errors = {}

        try:
            info = await validate_input(self.hass, user_input)
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:
            # Store the name and proceed to calendar selection
            self.context["title_placeholders"] = {"name": info["title"]}
            self._user_input = user_input
            return await self.async_step_select_calendars()

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    async def async_step_select_calendars(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle calendar selection."""
        if user_input is None:
            # Discover calendars if not already done
            if not self._discovered_calendars:
                await self._async_discover_calendars()

            # Create schema for calendar selection
            calendar_schema = {}
            for cal_id, cal_info in sorted(self._discovered_calendars.items()):
                name = self._lcal(cal_info, "name", default=cal_id)
                description = self._lcal(cal_info, "description", default="")
                label = f"{name}"
                if description:
                    label = f"{name} - {description[:50]}..."
                calendar_schema[vol.Optional(cal_id, default=False)] = bool

            if not calendar_schema:
                # No calendars found
                return self.async_abort(reason="no_calendars_found")

            return self.async_show_form(
                step_id="select_calendars",
                data_schema=vol.Schema(calendar_schema),
                description_placeholders={"calendars_found": str(len(calendar_schema)),
                    "details": self._details_text(self._discovered_calendars)}
            )

        # Process selected calendars
        self._selected_calendars = [
            cal_id for cal_id, selected in user_input.items() if selected
        ]

        if not self._selected_calendars:
            # No calendars selected
            return self.async_show_form(
                step_id="select_calendars",
                data_schema=vol.Schema({}),
                errors={"base": "no_calendars_selected"}
            )

        # Create the config entry
        data = {
            **self._user_input,
            "calendars": self._selected_calendars,
            "groups": self._build_groups(self._selected_calendars, self._discovered_calendars)
        }
        
        return self.async_create_entry(
            title=self._user_input.get("name", "Alternative Time"),
            data=data
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

    # -----------------------------
    # Grouping & details helpers
    # -----------------------------
    def _build_groups(self, selected_ids: list[str], info_map: dict[str, dict]) -> dict[str, list[str]]:
        """Return mapping {category: [ids...]} for selected calendars."""
        groups: dict[str, list[str]] = {}
        for cid in selected_ids:
            info = (info_map or {}).get(cid, {}) or {}
            cat = str(info.get("category") or "uncategorized")
            # Normalize common synonyms
            if cat == "religious":
                cat = "religion"
            groups.setdefault(cat, []).append(cid)
        for k in list(groups):
            groups[k] = sorted(groups[k])
        return groups

    def _details_text(self, discovered: dict[str, dict]) -> str:
        """Build a compact details string for the form description."""
        try:
            lines = []
            cat_counts: dict[str, int] = {}
            for cid, info in (discovered or {}).items():
                cat = str(info.get("category") or "uncategorized")
                cat_counts[cat] = cat_counts.get(cat, 0) + 1
            if cat_counts:
                cats_line = ", ".join(f"{c} ({n})" for c, n in sorted(cat_counts.items()))
                lines.append(f"Categories: {cats_line}")
            for cid, info in sorted((discovered or {}).items()):
                name = self._lcal(info, "name", default=cid) if hasattr(self, "_lcal") else (info.get("name", {}) or {}).get("en", cid)
                cat = str(info.get("category") or "?")
                ver = str(info.get("version") or "")
                acc = str(info.get("accuracy") or "")
                upd = info.get("update_interval")
                upd_txt = f"{upd}s" if isinstance(upd, (int, float)) else str(upd or "")
                lines.append(f"- {name} [{cid}] — cat={cat}, v={ver}, acc={acc}, update={upd_txt}")
            return "\n".join(lines)
        except Exception:
            return ""

    # -----------------------------
    # Localization helpers
    # -----------------------------
    def _lang(self) -> str:
        """Return HA language like 'de-DE' or fallback 'en'."""
        try:
            lang = getattr(self.hass.config, "language", None) or "en"
        except Exception:
            lang = "en"
        return str(lang).lower()

    def _lcal(self, info: dict, key: str, *, default: str = "") -> str:
        """Localized lookup from a CALENDAR_INFO mapping block (e.g. 'name', 'description')."""
        block = (info or {}).get(key, {})
        if isinstance(block, dict):
            lang = self._lang()
            if lang in block:
                return str(block[lang])
            primary = lang.split("-")[0]
            if primary in block:
                return str(block[primary])
            if "en" in block:
                return str(block["en"])
            if block:
                return str(next(iter(block.values())))
            return default
        return str(block) if block else default

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
                        # Compute groups mapping based on selected calendars
            if isinstance(user_input, dict):
                selected = user_input.get('calendars')
                if isinstance(selected, list):
                    discovered = await self._async_discover_calendars()
                    user_input['groups'] = self._build_groups(selected, discovered)
            return self.async_create_entry(title="", data=user_input)

        # Discover available calendars
        discovered_calendars = await self._async_discover_calendars()
        
        # Get currently selected calendars
        current_calendars = self.config_entry.data.get("calendars", [])
        
        # Create schema for calendar selection
        calendar_schema = {}
        for cal_id, cal_info in sorted(discovered_calendars.items()):
            name = self._lcal(cal_info, "name", default=cal_id)
            description = self._lcal(cal_info, "description", default="")
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