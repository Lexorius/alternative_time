"""Sensor platform for Alternative Time Systems."""
from __future__ import annotations

import logging
import os
import importlib
import sys
from typing import Any, Dict, List, Optional, TYPE_CHECKING
from datetime import datetime, timedelta
import asyncio

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator
from homeassistant.util.dt import utcnow
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN

if TYPE_CHECKING:
    from homeassistant.helpers.typing import StateType

_LOGGER = logging.getLogger(__name__)

# Store config entries for access by sensors
_CONFIG_ENTRIES: Dict[str, ConfigEntry] = {}


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Alternative Time Systems sensors from a config entry."""
    
    # Store config entry for sensor access
    entry_id = config_entry.entry_id
    _CONFIG_ENTRIES[entry_id] = config_entry
    
    # Get selected calendars from config
    selected_calendars = config_entry.data.get("calendars", [])
    name = config_entry.data.get("name", "Alternative Time")
    
    # FIX: Try both "plugin_options" and "calendar_options" for compatibility
    plugin_options = config_entry.data.get("plugin_options", {})
    if not plugin_options:
        # Fallback to old key name for backward compatibility
        plugin_options = config_entry.data.get("calendar_options", {})
        if plugin_options:
            _LOGGER.info("Found options under 'calendar_options' (legacy), using them")
    
    _LOGGER.info(f"=== Setting up Alternative Time '{name}' ===")
    _LOGGER.debug(f"Config Entry ID: {entry_id[:8]}...")
    _LOGGER.debug(f"Selected calendars: {selected_calendars}")
    _LOGGER.info(f"Plugin options available: {list(plugin_options.keys())}")
    for cal_id, opts in plugin_options.items():
        _LOGGER.debug(f"  {cal_id}: {opts}")
    
    if not selected_calendars:
        _LOGGER.warning(f"No calendars selected for {name}")
        return
    
    # Load calendar modules and create sensors
    sensors = []
    
    # Group sensors by category for device registry
    category_devices = {}
    
    for calendar_id in selected_calendars:
        try:
            # Load the calendar module
            module = await hass.async_add_executor_job(
                _load_calendar_module, calendar_id
            )
            
            if not module:
                _LOGGER.error(f"Failed to load calendar module: {calendar_id}")
                continue
            
            # Get calendar info for category
            calendar_info = getattr(module, 'CALENDAR_INFO', {})
            category = calendar_info.get('category', 'uncategorized')
            
            # Create device info for this category if not exists
            if category not in category_devices:
                category_devices[category] = {
                    "identifiers": {(DOMAIN, f"{entry_id}_{category}")},
                    "name": f"{name} - {category.replace('_', ' ').title()}",
                    "manufacturer": "Alternative Time Systems",
                    "model": category.replace('_', ' ').title(),
                    "entry_type": DeviceEntryType.SERVICE,
                    "sw_version": calendar_info.get('version', '1.0.0'),
                }
            
            # Find the sensor class in the module
            sensor_class = None
            for item_name in dir(module):
                item = getattr(module, item_name)
                if (isinstance(item, type) and 
                    item_name.endswith('Sensor') and 
                    item_name not in ['AlternativeTimeSensorBase', 'SensorEntity']):
                    sensor_class = item
                    break
            
            if not sensor_class:
                _LOGGER.error(f"No sensor class found in calendar module: {calendar_id}")
                continue
            
            # Create sensor instance
            sensor = sensor_class(name, hass)
            
            # Set the calendar ID and config entry ID for plugin options access
            sensor._calendar_id = calendar_id
            sensor._config_entry_id = entry_id
            
            # Set device info
            sensor._attr_device_info = category_devices[category]
            
            # Log sensor creation
            _LOGGER.info(f"Created sensor: {sensor.__class__.__name__} for calendar {calendar_id}")
            
            sensors.append(sensor)
            
        except Exception as e:
            _LOGGER.error(f"Error loading calendar {calendar_id}: {e}", exc_info=True)
            continue
    
    if sensors:
        _LOGGER.info(f"Adding {len(sensors)} sensors for '{name}'")
        async_add_entities(sensors, update_before_add=True)
    else:
        _LOGGER.warning(f"No sensors created for '{name}'")


def _load_calendar_module(calendar_id: str):
    """Load a calendar module by ID (blocking operation for executor)."""
    try:
        # First, try to import from the calendars subdirectory
        module_name = f"custom_components.alternative_time.calendars.{calendar_id}"
        
        # Check if already imported
        if module_name in sys.modules:
            return sys.modules[module_name]
        
        # Import the module
        module = importlib.import_module(f".calendars.{calendar_id}", package="custom_components.alternative_time")
        return module
        
    except ImportError as e:
        _LOGGER.error(f"Failed to import calendar module {calendar_id}: {e}")
        return None
    except Exception as e:
        _LOGGER.error(f"Unexpected error loading calendar {calendar_id}: {e}")
        return None


class AlternativeTimeSensorBase(SensorEntity):
    """Base class for Alternative Time System sensors."""

    # Default update interval - can be overridden by subclasses
    UPDATE_INTERVAL = timedelta(minutes=1)

    def __init__(self, base_name: str, hass: HomeAssistant) -> None:
        """Initialize the base sensor.
        
        Args:
            base_name: The base name for the sensor
            hass: HomeAssistant instance
        """
        self._base_name = base_name
        self._hass = hass
        
        # These will be set by async_setup_entry after instantiation
        self._calendar_id: Optional[str] = None
        self._config_entry_id: Optional[str] = None
        
        # Initialize basic attributes
        self._attr_name = base_name
        self._attr_unique_id = f"{base_name}_base"
        self._attr_has_entity_name = False
        
        # State and attributes
        self._state: Optional[str] = None
        self._attributes: Dict[str, Any] = {}
        
        # Update tracking
        self._last_update: Optional[datetime] = None
        self._update_interval = self.UPDATE_INTERVAL
        
        _LOGGER.debug(f"Initialized base sensor: {self._attr_name}")

    def _translate(self, key: str, default: str = "") -> str:
        """Get translated value from CALENDAR_INFO.
        
        Args:
            key: The key to look up (e.g., 'name', 'description')
            default: Default value if not found
            
        Returns:
            Translated string or default
        """
        # Get the calendar info if available
        if hasattr(self, '_calendar_info'):
            info = self._calendar_info
        elif hasattr(self, 'CALENDAR_INFO'):
            info = self.CALENDAR_INFO
        else:
            # Try to get from class
            try:
                module = sys.modules[self.__class__.__module__]
                info = getattr(module, 'CALENDAR_INFO', {})
            except:
                return default
        
        # Get the value
        value = info.get(key, {})
        
        # If it's a dict with language keys, get the appropriate translation
        if isinstance(value, dict):
            # Try to get user's language
            lang = self._hass.config.language if self._hass else "en"
            
            # Try exact match
            if lang in value:
                return value[lang]
            
            # Try language without region
            lang_base = lang.split('_')[0].split('-')[0]
            if lang_base in value:
                return value[lang_base]
            
            # Fallback to English
            if "en" in value:
                return value["en"]
            
            # Return first available
            if value:
                return next(iter(value.values()))
        
        # If it's a string, return it
        if isinstance(value, str):
            return value
        
        return default

    def get_plugin_options(self) -> Dict[str, Any]:
        """Get plugin options for this sensor.
        
        Returns:
            Dictionary of plugin options or empty dict if not available
        """
        # Check if IDs are set
        if not self._config_entry_id or not self._calendar_id:
            _LOGGER.debug(f"get_plugin_options called for {self.__class__.__name__}")
            _LOGGER.debug(f"  _config_entry_id: {self._config_entry_id}")
            _LOGGER.debug(f"  _calendar_id: {self._calendar_id}")
            
            if not self._config_entry_id:
                _LOGGER.warning(f"{self.__class__.__name__}: No config_entry_id set - called too early?")
            if not self._calendar_id:
                _LOGGER.warning(f"{self.__class__.__name__}: No calendar_id set - called too early?")
            return {}
        
        config_entry = _CONFIG_ENTRIES.get(self._config_entry_id)
        if not config_entry:
            _LOGGER.error(f"Config entry {self._config_entry_id} not found in _CONFIG_ENTRIES")
            _LOGGER.debug(f"Available entries: {list(_CONFIG_ENTRIES.keys())}")
            return {}
        
        # FIX: Try both "plugin_options" and "calendar_options" for compatibility
        plugin_options = config_entry.data.get("plugin_options", {})
        if not plugin_options:
            # Fallback to old key name for backward compatibility
            plugin_options = config_entry.data.get("calendar_options", {})
            if plugin_options:
                _LOGGER.debug(f"Using 'calendar_options' (legacy) for {self._calendar_id}")
        
        calendar_options = plugin_options.get(self._calendar_id, {})
        
        # Only log if options are actually present
        if calendar_options:
            _LOGGER.debug(f"{self.__class__.__name__} ({self._calendar_id}) loaded options: {calendar_options}")
        
        return calendar_options
    
    # NEW METHOD: For compatibility with calendars using _get_plugin_options()
    def _get_plugin_options(self) -> Dict[str, Any]:
        """Private method for backward compatibility with calendars using _get_plugin_options()."""
        return self.get_plugin_options()

    @property
    def state(self) -> StateType:
        """Return the state of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes."""
        return self._attributes

    @property
    def should_poll(self) -> bool:
        """Return True if entity should be polled."""
        return True

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return True

    async def async_update(self) -> None:
        """Update the sensor."""
        try:
            # Check if enough time has passed since last update
            now = utcnow()
            if self._last_update:
                elapsed = now - self._last_update
                # Get update interval from class or instance
                interval = getattr(self.__class__, 'UPDATE_INTERVAL', self._update_interval)
                if elapsed < interval:
                    return
            
            # Call the synchronous update method in executor
            await self._hass.async_add_executor_job(self.update)
            self._last_update = now
            
        except Exception as e:
            _LOGGER.error(f"Error updating {self._attr_name}: {e}", exc_info=True)

    def update(self) -> None:
        """Update the sensor state and attributes.
        
        This method should be overridden by subclasses to implement
        the actual calendar calculations.
        """
        # Default implementation - override in subclasses
        self._state = "Not Implemented"
        self._attributes = {
            "error": "Sensor update method not implemented",
            "calendar_id": self._calendar_id,
            "class": self.__class__.__name__
        }

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added to hass."""
        await super().async_added_to_hass()
        
        _LOGGER.debug(f"{self.__class__.__name__} added to hass: "
                     f"calendar_id={self._calendar_id}, "
                     f"config_entry_id={self._config_entry_id}")

    async def async_will_remove_from_hass(self) -> None:
        """Run when entity will be removed from hass."""
        await super().async_will_remove_from_hass()
        
        _LOGGER.debug(f"{self.__class__.__name__} removed from hass: {self._attr_name}")