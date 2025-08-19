"""Sensor module for Alternative Time Systems integration."""
from __future__ import annotations

import os
import logging
from typing import Dict, Any, Optional, Type
from importlib import import_module
import asyncio

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Global cache for discovered calendars
_DISCOVERED_CALENDARS_CACHE: Optional[Dict[str, Dict[str, Any]]] = None
_DISCOVERY_LOCK = asyncio.Lock()

# Global storage for config entries
_CONFIG_ENTRIES: Dict[str, ConfigEntry] = {}

# Mapping von calendar_id zu Dateinamen
CALENDAR_FILE_MAPPING: Dict[str, str] = {}  # Will be populated during discovery


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Alternative Time System sensors from a config entry."""
    # Store config entry globally for access by sensors
    entry_id = entry.entry_id
    _CONFIG_ENTRIES[entry_id] = entry
    
    # Get configuration from entry
    name = entry.data.get("name", "Alternative Time")
    selected_calendars = entry.data.get("calendars", [])
    
    # FIX: Hole die richtigen Options-Daten
    calendar_options = entry.data.get("calendar_options", {})
    
    _LOGGER.info(f"Setting up Alternative Time sensors for '{name}'")
    _LOGGER.debug(f"Selected calendars: {selected_calendars}")
    _LOGGER.debug(f"Calendar options: {calendar_options}")
    
    # Discover all available calendars
    discovered_calendars = await async_discover_all_calendars(hass)
    
    if not discovered_calendars:
        _LOGGER.error("No calendar implementations found!")
        return
    
    _LOGGER.info(f"Discovered calendars: {list(discovered_calendars.keys())}")
    
    # Create sensors for selected calendars
    sensors = []
    for calendar_id in selected_calendars:
        if calendar_id not in discovered_calendars:
            _LOGGER.error(f"Calendar '{calendar_id}' is enabled but not found in registry")
            _LOGGER.debug(f"Available calendars: {list(discovered_calendars.keys())}")
            continue
        
        calendar_info = discovered_calendars[calendar_id]
        
        try:
            # Get the actual module name from our mapping
            module_name = CALENDAR_FILE_MAPPING.get(calendar_id)
            if not module_name:
                _LOGGER.error(f"No module mapping found for calendar_id: {calendar_id}")
                continue
                
            # Import the calendar module asynchronously
            module = await async_import_calendar_module(hass, module_name)
            
            if not module:
                _LOGGER.error(f"Failed to import calendar module: {module_name} for {calendar_id}")
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
            
            # Create sensor instance with config entry
            sensor = sensor_class(name, hass)
            sensor._calendar_id = calendar_id  # Store for plugin options lookup
            sensor._config_entry_id = entry_id  # Store entry ID
            
            # FIX: Direkt die Options setzen
            sensor._plugin_options = calendar_options.get(calendar_id, {})
            _LOGGER.debug(f"Set options for {calendar_id}: {sensor._plugin_options}")
            
            sensors.append(sensor)
            _LOGGER.info(f"Created sensor for calendar: {calendar_id}")
            
        except Exception as e:
            _LOGGER.error(f"Failed to create sensor for calendar {calendar_id}: {e}")
            import traceback
            _LOGGER.debug(traceback.format_exc())
            continue
    
    if sensors:
        async_add_entities(sensors)
        _LOGGER.info(f"Added {len(sensors)} sensors to Home Assistant")


class AlternativeTimeSensorBase(SensorEntity):
    """Base class for Alternative Time System sensors."""

    def __init__(self, base_name: str, hass: HomeAssistant) -> None:
        """Initialize the sensor."""
        self._base_name = base_name
        self._hass = hass
        self._state = None
        self._attr_should_poll = True
        self._calendar_id = None  # Will be set by async_setup_entry
        self._config_entry_id = None  # Will be set by async_setup_entry
        self._plugin_options = {}  # FIX: Direkte Storage für Options
        
        # Set update interval from class attribute if available
        if hasattr(self.__class__, 'UPDATE_INTERVAL'):
            self._update_interval = self.__class__.UPDATE_INTERVAL
        else:
            self._update_interval = 3600  # Default 1 hour
    
    def get_plugin_options(self) -> Dict[str, Any]:
        """Get plugin options for this sensor."""
        # FIX: Direkt die gespeicherten Options zurückgeben
        return self._plugin_options
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return state attributes."""
        # Ensure we always return a dict
        return {}
    
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
        """Translate a CALENDAR_INFO text block for the user's language."""
        if not hasattr(self, '_calendar_info'):
            # Try to get CALENDAR_INFO from the module
            try:
                import sys
                for module_name, module in sys.modules.items():
                    if hasattr(module, self.__class__.__name__):
                        if hasattr(module, 'CALENDAR_INFO'):
                            self._calendar_info = module.CALENDAR_INFO
                            break
            except:
                pass
                
        if not hasattr(self, '_calendar_info'):
            return default
        
        info = self._calendar_info.get(key, {})
        if isinstance(info, dict):
            try:
                lang = self._hass.config.language
            except:
                lang = 'en'
            return info.get(lang, info.get("en", default))
        return str(info or default)


async def async_discover_all_calendars(hass: HomeAssistant) -> Dict[str, Dict[str, Any]]:
    """Discover all available calendar implementations asynchronously."""
    global _DISCOVERED_CALENDARS_CACHE
    global CALENDAR_FILE_MAPPING
    
    async with _DISCOVERY_LOCK:
        if _DISCOVERED_CALENDARS_CACHE is not None:
            return _DISCOVERED_CALENDARS_CACHE
        
        discovered = {}
        
        # Get calendars directory path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        calendars_dir = os.path.join(current_dir, "calendars")
        
        if not os.path.exists(calendars_dir):
            _LOGGER.warning(f"Calendars directory not found: {calendars_dir}")
            return discovered
        
        # List files asynchronously
        files = await hass.async_add_executor_job(os.listdir, calendars_dir)
        
        for filename in files:
            if filename.endswith(".py") and not filename.startswith("__"):
                module_name = filename[:-3]  # Remove .py extension
                
                # Skip template and example files
                if "template" in module_name.lower() or "example" in module_name.lower():
                    continue
                
                try:
                    # Import module asynchronously
                    module = await async_import_calendar_module(hass, module_name)
                    
                    if module and hasattr(module, 'CALENDAR_INFO'):
                        cal_info = module.CALENDAR_INFO
                        cal_id = cal_info.get('id', module_name)
                        discovered[cal_id] = cal_info
                        
                        # Store the mapping
                        CALENDAR_FILE_MAPPING[cal_id] = module_name
                        
                        _LOGGER.debug(f"Discovered calendar: {cal_id} from file {module_name}.py")
                        
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
                module = import_module(f'.calendars.{module_name}', 
                                     package='custom_components.alternative_time')
                return module
            except ImportError:
                try:
                    module = import_module(
                        f'custom_components.alternative_time.calendars.{module_name}'
                    )
                    return module
                except ImportError:
                    # Add the calendars directory to the path
                    import sys
                    current_dir = os.path.dirname(os.path.abspath(__file__))
                    calendars_dir = os.path.join(current_dir, "calendars")
                    if calendars_dir not in sys.path:
                        sys.path.insert(0, calendars_dir)
                    
                    module = import_module(module_name)
                    return module
        except Exception as e:
            _LOGGER.error(f"Failed to import calendar module {module_name}: {e}")
            return None
    
    return await hass.async_add_executor_job(_import)


def export_discovered_calendars() -> Dict[str, Dict[str, Any]]:
    """Export discovered calendars for config flow.
    
    This function is synchronous for backward compatibility,
    but should only be called from an executor.
    """
    global _DISCOVERED_CALENDARS_CACHE
    global CALENDAR_FILE_MAPPING
    
    if _DISCOVERED_CALENDARS_CACHE is not None:
        return _DISCOVERED_CALENDARS_CACHE
    
    # Perform synchronous discovery if cache is empty
    discovered = {}
    current_dir = os.path.dirname(os.path.abspath(__file__))
    calendars_dir = os.path.join(current_dir, "calendars")
    
    if not os.path.exists(calendars_dir):
        _LOGGER.warning(f"Calendars directory not found in export: {calendars_dir}")
        return discovered
    
    files = os.listdir(calendars_dir)
    
    for filename in files:
        if filename.endswith(".py") and not filename.startswith("__"):
            module_name = filename[:-3]
            
            # Skip template and example files
            if "template" in module_name.lower() or "example" in module_name.lower():
                continue
            
            try:
                module = import_module(f'.calendars.{module_name}', 
                                     package='custom_components.alternative_time')
                
                if hasattr(module, 'CALENDAR_INFO'):
                    cal_info = module.CALENDAR_INFO
                    cal_id = cal_info.get('id', module_name)
                    discovered[cal_id] = cal_info
                    
                    # Store the mapping
                    CALENDAR_FILE_MAPPING[cal_id] = module_name
                    
                    _LOGGER.debug(f"Export discovered: {cal_id} from file {module_name}.py")
                    
            except Exception as e:
                _LOGGER.debug(f"Export failed for {module_name}: {e}")
                continue
    
    _LOGGER.info(f"Export discovered {len(discovered)} calendars")
    _DISCOVERED_CALENDARS_CACHE = discovered
    return discovered


def get_config_entry(entry_id: str) -> Optional[ConfigEntry]:
    """Get a config entry by ID."""
    return _CONFIG_ENTRIES.get(entry_id)