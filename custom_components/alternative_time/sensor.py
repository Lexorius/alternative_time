"""Sensor platform for Alternative Time Systems."""
from __future__ import annotations

import os
import logging
import asyncio
from datetime import timedelta
from typing import Any, Dict, List, Optional
from importlib import import_module

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Global cache for discovered calendars
_DISCOVERED_CALENDARS_CACHE: Optional[Dict[str, Dict[str, Any]]] = None
_DISCOVERY_LOCK = asyncio.Lock()


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Alternative Time Systems sensors from a config entry."""
    
    # Get selected calendars from config
    selected_calendars = config_entry.data.get("calendars", [])
    name = config_entry.data.get("name", "Alternative Time")
    
    if not selected_calendars:
        _LOGGER.warning("No calendars selected")
        return
    
    # Discover all available calendars
    discovered_calendars = await async_discover_all_calendars(hass)
    
    # Create sensors for selected calendars
    sensors = []
    for calendar_id in selected_calendars:
        if calendar_id not in discovered_calendars:
            _LOGGER.warning(f"Calendar {calendar_id} not found")
            continue
        
        calendar_info = discovered_calendars[calendar_id]
        
        try:
            # Import the calendar module asynchronously
            module = await async_import_calendar_module(hass, calendar_id)
            
            if not module:
                _LOGGER.error(f"Failed to import calendar module: {calendar_id}")
                continue
            
            # Find the sensor class
            sensor_class = None
            for item_name in dir(module):
                item = getattr(module, item_name)
                if (isinstance(item, type) and 
                    issubclass(item, AlternativeTimeSensorBase) and 
                    item != AlternativeTimeSensorBase):
                    sensor_class = item
                    break
            
            if not sensor_class:
                _LOGGER.error(f"No sensor class found in calendar module: {calendar_id}")
                continue
            
            # Create sensor instance
            sensor = sensor_class(name, hass)
            sensors.append(sensor)
            _LOGGER.info(f"Created sensor for calendar: {calendar_id}")
            
        except Exception as e:
            _LOGGER.error(f"Failed to create sensor for calendar {calendar_id}: {e}")
            continue
    
    if sensors:
        async_add_entities(sensors)


async def async_discover_all_calendars(hass: HomeAssistant) -> Dict[str, Dict[str, Any]]:
    """Discover all available calendar implementations asynchronously."""
    global _DISCOVERED_CALENDARS_CACHE
    
    async with _DISCOVERY_LOCK:
        # Return cached result if available
        if _DISCOVERED_CALENDARS_CACHE is not None:
            return _DISCOVERED_CALENDARS_CACHE
        
        discovered = {}
        
        # Get calendars directory path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        calendars_dir = os.path.join(current_dir, "calendars")
        
        if not os.path.exists(calendars_dir):
            _LOGGER.warning(f"Calendars directory not found: {calendars_dir}")
            _DISCOVERED_CALENDARS_CACHE = discovered
            return discovered
        
        # List files asynchronously
        files = await hass.async_add_executor_job(os.listdir, calendars_dir)
        
        for filename in files:
            if filename.endswith(".py") and not filename.startswith("__"):
                module_name = filename[:-3]  # Remove .py extension
                
                try:
                    # Import module asynchronously
                    module = await async_import_calendar_module(hass, module_name)
                    
                    if module and hasattr(module, 'CALENDAR_INFO'):
                        cal_info = module.CALENDAR_INFO
                        cal_id = cal_info.get('id', module_name)
                        discovered[cal_id] = cal_info
                        _LOGGER.debug(f"Discovered calendar: {cal_id}")
                        
                except Exception as e:
                    _LOGGER.warning(f"Failed to discover calendar {module_name}: {e}")
                    continue
        
        _LOGGER.info(f"Discovered {len(discovered)} calendars")
        _DISCOVERED_CALENDARS_CACHE = discovered
        return discovered


async def async_import_calendar_module(hass: HomeAssistant, module_name: str):
    """Import a calendar module asynchronously."""
    def _import():
        try:
            # Try different import methods
            try:
                return import_module(f'.calendars.{module_name}', 
                                   package='custom_components.alternative_time')
            except ImportError:
                try:
                    return import_module(
                        f'custom_components.alternative_time.calendars.{module_name}'
                    )
                except ImportError:
                    return import_module(module_name)
        except Exception as e:
            _LOGGER.error(f"Failed to import calendar module {module_name}: {e}")
            return None
    
    return await hass.async_add_executor_job(_import)


def export_discovered_calendars() -> Dict[str, Dict[str, Any]]:
    """Export discovered calendars for use by config flow.
    
    This function is synchronous for backward compatibility,
    but should only be called from an executor.
    """
    global _DISCOVERED_CALENDARS_CACHE
    
    if _DISCOVERED_CALENDARS_CACHE is not None:
        return _DISCOVERED_CALENDARS_CACHE
    
    # Perform synchronous discovery if cache is empty
    discovered = {}
    current_dir = os.path.dirname(os.path.abspath(__file__))
    calendars_dir = os.path.join(current_dir, "calendars")
    
    if not os.path.exists(calendars_dir):
        return discovered
    
    for filename in os.listdir(calendars_dir):
        if filename.endswith(".py") and not filename.startswith("__"):
            module_name = filename[:-3]
            
            try:
                module = import_module(f'.calendars.{module_name}', 
                                     package='custom_components.alternative_time')
                
                if hasattr(module, 'CALENDAR_INFO'):
                    cal_info = module.CALENDAR_INFO
                    cal_id = cal_info.get('id', module_name)
                    discovered[cal_id] = cal_info
                    
            except Exception:
                continue
    
    return discovered


class AlternativeTimeSensorBase(SensorEntity):
    """Base class for Alternative Time System sensors."""

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Normalized parent attributes as a dict (never None).

        HA's SensorEntity.extra_state_attributes returns None by default.
        Returning a dict here ensures plugin code that calls
        ``super().extra_state_attributes.update(...)`` won't crash.
        """
        parent = getattr(super(), "extra_state_attributes", None)
        try:
            # If parent is a property on base class, access its value
            parent_val = super().extra_state_attributes  # type: ignore[attr-defined]
        except Exception:
            parent_val = None
        base_attrs = parent_val if isinstance(parent_val, dict) else (parent_val or {})
        return dict(base_attrs)
    
    def __init__(self, base_name: str, hass: HomeAssistant) -> None:
        """Initialize the sensor."""
        self._base_name = base_name
        self._hass = hass
        self._state = None
        self._attr_should_poll = True
        
        # Set update interval from class attribute if available
        if hasattr(self.__class__, 'UPDATE_INTERVAL'):
            self._update_interval = self.__class__.UPDATE_INTERVAL
        else:
            self._update_interval = 3600  # Default 1 hour
    
    @property
    def update_interval(self) -> int:
        """Return the update interval in seconds."""
        return self._update_interval
    
    @property
    def should_poll(self) -> bool:
        """Return True if entity has to be polled for state."""
        return True
    
    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return True
    
    def _translate(self, key: str, default: str = "") -> str:
        """Translate a CALENDAR_INFO text block for the user's language.
        
        - Reads the integration's CALENDAR_INFO from the concrete sensor module.
        - Chooses hass.config.language if available; falls back to primary subtag (e.g. "de" from "de-DE"),
          then to English ("en"), and finally to the provided default.
        - If CALENDAR_INFO[key] is not a mapping (e.g. a plain string), that value is returned.
        """
        # Lazy-load CALENDAR_INFO from the concrete module
        if not hasattr(self, "_calendar_info"):
            module = self.__class__.__module__
            if module:
                try:
                    mod = __import__(module, fromlist=["CALENDAR_INFO"])
                    if hasattr(mod, "CALENDAR_INFO"):
                        self._calendar_info = mod.CALENDAR_INFO  # type: ignore[attr-defined]
                except Exception:  # pragma: no cover - defensive, never crash on translation
                    pass

        info = getattr(self, "_calendar_info", {}) or {}
        block = info.get(key, {})
        if isinstance(block, dict):
            # Detect language from HA, tolerate missing attribute
            lang = "en"
            try:
                lang = getattr(self._hass.config, "language", None) or "en"
            except Exception:
                lang = "en"
            lang = str(lang).lower()
            # Try exact match, then primary subtag, then English
            if lang in block:
                return str(block[lang])
            primary = lang.split("-")[0]
            if primary in block:
                return str(block[primary])
            if "en" in block:
                return str(block["en"])
            # If nothing matched but the dict has at least one value, return the first
            if block:
                return str(next(iter(block.values())))
            return default
        # Non-dict text - return as-is or default
        return str(block) if block else default

    @property
    def device_info(self) -> Dict[str, Any]:
        """Group entities by plugin category as a Device in HA registry."""
        # Lazy-load CALENDAR_INFO from module
        info = {}
        try:
            mod = __import__(self.__class__.__module__, fromlist=["CALENDAR_INFO"])
            if hasattr(mod, "CALENDAR_INFO"):
                info = getattr(mod, "CALENDAR_INFO") or {}
        except Exception:
            info = {}
        category = str(info.get("category") or "uncategorized")
        if category == "religious":
            category = "religion"
        device_name = f"Alternative Time — {category.title()}"
        return {
            "identifiers": {(DOMAIN, f"group:{category}")},
            "manufacturer": "Alternative Time Systems",
            "model": "Category Group",
            "name": device_name,
        }

    async def async_added_to_hass(self) -> None:
        """Schedule periodic updates in a non-blocking way."""
        # Determine interval from CALENDAR_INFO or class constant
        interval = None
        try:
            mod = __import__(self.__class__.__module__, fromlist=["CALENDAR_INFO"])
            info = getattr(mod, "CALENDAR_INFO", {}) or {}
            interval = info.get("update_interval")
        except Exception:
            interval = None
        if not isinstance(interval, (int, float)):
            interval = getattr(self.__class__, "UPDATE_INTERVAL", None)
        try:
            seconds = max(1, int(interval)) if interval else 3600
        except Exception:
            seconds = 3600

        # Avoid platform-wide polling
        self._attr_should_poll = False

        # Start scheduler
        from datetime import timedelta as _td
        self._unsub_timer = async_track_time_interval(self._hass, self._async_timer_tick, _td(seconds=seconds))
        # Trigger first run
        self._hass.async_create_task(self._async_timer_tick(None))

    async def async_will_remove_from_hass(self) -> None:
        """Cancel the scheduled timer when entity is removed."""
        unsub = getattr(self, "_unsub_timer", None)
        if unsub:
            try:
                unsub()
            except Exception:
                pass
            self._unsub_timer = None

    async def _async_timer_tick(self, _now) -> None:
        """Call plugin update without blocking the event loop."""
        try:
            # Prefer plugin's async_update if available
            if hasattr(self, "async_update") and callable(getattr(self, "async_update")):
                await getattr(self, "async_update")()
            else:
                await self._hass.async_add_executor_job(getattr(self, "update"))
        except Exception as exc:
            _LOGGER.debug(f"Scheduled update failed for {self.name}: {exc}")
        finally:
            try:
                self.async_write_ha_state()
            except Exception:
                pass