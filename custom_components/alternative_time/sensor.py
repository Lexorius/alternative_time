"""Sensor platform for Alternative Time integration - Version 2.5 Dynamic Discovery."""
from __future__ import annotations

import logging
import os
import sys
from datetime import datetime, timedelta
import traceback
from importlib import import_module
from typing import Dict, Any, Optional, List

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

_LOGGER = logging.getLogger(__name__)

# Domain constant - the only one we really need
DOMAIN = "alternative_time"

# Track discovered calendar modules
DISCOVERED_CALENDARS = {}
CALENDAR_REGISTRY = {}


def discover_all_calendars() -> Dict[str, Any]:
    """Discover all available calendar modules dynamically."""
    calendars = {}
    
    # Get the calendars directory path
    calendars_dir = os.path.join(os.path.dirname(__file__), 'calendars')
    
    if not os.path.exists(calendars_dir):
        _LOGGER.error(f"Calendars directory not found: {calendars_dir}")
        # Try alternative path for debugging
        _LOGGER.debug(f"Current file location: {__file__}")
        _LOGGER.debug(f"Directory contents: {os.listdir(os.path.dirname(__file__))}")
        return calendars
    
    _LOGGER.debug(f"Scanning calendars directory: {calendars_dir}")
    
    # Scan all .py files in the calendars directory
    try:
        files = os.listdir(calendars_dir)
        _LOGGER.debug(f"Found files in calendars directory: {files}")
    except Exception as e:
        _LOGGER.error(f"Error listing calendars directory: {e}")
        return calendars
    
    for filename in files:
        if filename.endswith('.py') and not filename.startswith('__'):
            module_name = filename[:-3]  # Remove .py extension
            _LOGGER.debug(f"Attempting to import calendar module: {module_name}")
            
            try:
                # Import the module - try different import methods
                try:
                    # Method 1: Relative import with package
                    module = import_module(f'.calendars.{module_name}', package='custom_components.alternative_time')
                except ImportError as e1:
                    _LOGGER.debug(f"Relative import failed for {module_name}: {e1}")
                    try:
                        # Method 2: Direct import
                        module = import_module(f'custom_components.alternative_time.calendars.{module_name}')
                    except ImportError as e2:
                        _LOGGER.debug(f"Direct import failed for {module_name}: {e2}")
                        # Method 3: Add to path and import
                        if calendars_dir not in sys.path:
                            sys.path.insert(0, calendars_dir)
                        module = import_module(module_name)
                
                # Check if it has CALENDAR_INFO (v2.5 format)
                if hasattr(module, 'CALENDAR_INFO'):
                    info = module.CALENDAR_INFO
                    calendar_id = info.get('id', module_name)
                    
                    # Find all sensor classes in the module
                    sensor_classes = []
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (isinstance(attr, type) and 
                            issubclass(attr, SensorEntity) and 
                            attr.__name__ != 'AlternativeTimeSensorBase' and
                            attr.__name__ != 'SensorEntity'):
                            sensor_classes.append({
                                'class': attr,
                                'name': attr.__name__
                            })
                    
                    if sensor_classes:
                        calendars[calendar_id] = {
                            'module': module,
                            'module_name': module_name,
                            'info': info,
                            'sensors': sensor_classes,
                            'update_interval': getattr(module, 'UPDATE_INTERVAL', info.get('update_interval', 60))
                        }
                        
                        _LOGGER.info(
                            f"✓ Discovered calendar: {calendar_id} "
                            f"[{info.get('category', 'uncategorized')}] "
                            f"with {len(sensor_classes)} sensor(s)"
                        )
                    else:
                        _LOGGER.debug(f"Module {module_name} has CALENDAR_INFO but no sensor classes")
                        
                # Check for old format (backward compatibility)
                elif hasattr(module, '__all__'):
                    # Old format - try to adapt it
                    _LOGGER.debug(f"Module {module_name} appears to be old format (has __all__)")
                    
                    # Try to find sensor classes
                    sensor_classes = []
                    for export_name in module.__all__:
                        if hasattr(module, export_name):
                            exported = getattr(module, export_name)
                            if (isinstance(exported, type) and 
                                issubclass(exported, SensorEntity)):
                                sensor_classes.append({
                                    'class': exported,
                                    'name': export_name
                                })
                    
                    if sensor_classes:
                        # Create minimal info for old format
                        calendar_id = module_name
                        info = {
                            'id': calendar_id,
                            'name': {'en': calendar_id.replace('_', ' ').title()},
                            'description': {'en': f'Legacy calendar: {calendar_id}'},
                            'category': 'uncategorized'
                        }
                        
                        calendars[calendar_id] = {
                            'module': module,
                            'module_name': module_name,
                            'info': info,
                            'sensors': sensor_classes,
                            'update_interval': 60
                        }
                        
                        _LOGGER.info(f"✓ Discovered legacy calendar: {calendar_id} with {len(sensor_classes)} sensor(s)")
                else:
                    _LOGGER.debug(f"Module {module_name} has no CALENDAR_INFO or __all__, skipping")
                    
            except ImportError as e:
                _LOGGER.warning(f"Could not import calendar module {module_name}: {e}")
            except Exception as e:
                _LOGGER.error(f"Error discovering calendar {module_name}: {e}")
                _LOGGER.debug(traceback.format_exc())
    
    # If no calendars found, log directory contents for debugging
    if not calendars:
        _LOGGER.warning(f"No calendars discovered! Directory contents: {files}")
    
    return calendars


def generate_config_schema() -> Dict[str, Any]:
    """Generate configuration schema based on discovered calendars."""
    schema = {
        'name': {
            'type': 'string',
            'default': 'Alternative Time',
            'required': True
        }
    }
    
    # Add enable option for each discovered calendar
    for calendar_id, calendar_data in DISCOVERED_CALENDARS.items():
        info = calendar_data['info']
        
        # Generate config key
        config_key = f"enable_{calendar_id}"
        
        schema[config_key] = {
            'type': 'boolean',
            'default': False,
            'required': False,
            'name': info.get('name', {}).get('en', calendar_id),
            'description': info.get('description', {}).get('en', ''),
            'category': info.get('category', 'uncategorized')
        }
        
        # Add extra config options if calendar needs them
        if 'config_options' in info:
            for option_key, option_config in info['config_options'].items():
                schema[f"{calendar_id}_{option_key}"] = option_config
    
    return schema


# Discover calendars on module load
_LOGGER.info("=" * 60)
_LOGGER.info("Alternative Time v2.5 - Dynamic Calendar Discovery")
_LOGGER.info("=" * 60)

DISCOVERED_CALENDARS = discover_all_calendars()

# Group calendars by category for logging
categories = {}
for cal_id, cal_data in DISCOVERED_CALENDARS.items():
    category = cal_data['info'].get('category', 'uncategorized')
    if category not in categories:
        categories[category] = []
    categories[category].append(cal_id)

if DISCOVERED_CALENDARS:
    _LOGGER.info(f"Discovery complete! Found {len(DISCOVERED_CALENDARS)} calendars:")
    for category, cals in sorted(categories.items()):
        _LOGGER.info(f"  {category}: {', '.join(cals)}")
else:
    _LOGGER.warning("No calendars discovered! Check the calendars/ directory")
    
_LOGGER.info("=" * 60)

# Build the calendar registry for quick access
for cal_id, cal_data in DISCOVERED_CALENDARS.items():
    CALENDAR_REGISTRY[cal_id] = cal_data
    
    # Register variants (like nato_zone, nato_rescue)
    if 'variants' in cal_data['info']:
        for variant_id, variant_class_name in cal_data['info']['variants'].items():
            full_variant_id = f"{cal_id}_{variant_id}"
            
            # Find the variant class
            for sensor in cal_data['sensors']:
                if sensor['name'] == variant_class_name:
                    CALENDAR_REGISTRY[full_variant_id] = {
                        'module': cal_data['module'],
                        'module_name': cal_data['module_name'],
                        'info': {**cal_data['info'], 'id': full_variant_id},
                        'sensors': [sensor],
                        'update_interval': cal_data['update_interval']
                    }
                    _LOGGER.debug(f"  Registered variant: {full_variant_id}")


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Alternative Time sensors from a config entry."""
    _LOGGER.info(f"Setting up Alternative Time v2.5 sensors for '{config_entry.title}'")
    _LOGGER.debug(f"Config entry ID: {config_entry.entry_id}")
    _LOGGER.debug(f"Config data keys: {config_entry.data.keys()}")
    
    config = config_entry.data
    base_name = config.get('name', 'Alternative Time')
    user_language = hass.config.language or 'en'
    
    _LOGGER.info(f"Base name: '{base_name}', User language: '{user_language}'")
    
    sensors = []
    enabled_count = 0
    created_count = 0
    
    # Process each config entry
    for key, value in config.items():
        # Skip non-enable keys
        if not key.startswith('enable_') or not value:
            continue
        
        # Extract calendar ID from key
        calendar_id = key[7:]  # Remove 'enable_' prefix
        enabled_count += 1
        
        _LOGGER.debug(f"Processing enabled calendar: {calendar_id}")
        
        # Look up calendar in registry
        if calendar_id not in CALENDAR_REGISTRY:
            _LOGGER.warning(f"Calendar '{calendar_id}' is enabled but not found in registry")
            continue
        
        cal_data = CALENDAR_REGISTRY[calendar_id]
        
        try:
            # Create sensor instances
            for sensor_info in cal_data['sensors']:
                sensor_class = sensor_info['class']
                
                # Determine constructor parameters
                if calendar_id == 'timezone':
                    # Special case for timezone sensor
                    timezone = config.get('timezone', 'UTC')
                    sensor = sensor_class(base_name, timezone, hass)
                elif calendar_id == 'mars' or 'mars' in calendar_id:
                    # Special case for Mars time with timezone
                    mars_tz = config.get('mars_timezone', 'MTC')
                    sensor = sensor_class(base_name, mars_tz, hass)
                else:
                    # Standard sensor
                    sensor = sensor_class(base_name, hass)
                
                sensors.append(sensor)
                created_count += 1
                
                info = cal_data['info']
                _LOGGER.info(
                    f"✓ Created {sensor_info['name']} "
                    f"[{info.get('category', 'uncategorized')}]"
                )
                
        except Exception as e:
            _LOGGER.error(f"Error creating sensor for {calendar_id}: {e}")
            _LOGGER.debug(traceback.format_exc())
    
    # Add fallback sensor if nothing was created
    if not sensors:
        _LOGGER.warning("No sensors were created! Adding a fallback sensor...")
        fallback = FallbackTimeSensor(base_name, hass)
        sensors.append(fallback)
    
    # Add all sensors with update enabled
    async_add_entities(sensors, update_before_add=True)
    
    # Summary logging
    _LOGGER.info("=" * 60)
    _LOGGER.info(f"Alternative Time v2.5 Setup Complete")
    _LOGGER.info(f"  Configuration: '{base_name}'")
    _LOGGER.info(f"  Enabled calendars: {enabled_count}")
    _LOGGER.info(f"  Created sensors: {created_count}")
    _LOGGER.info(f"  Total active: {len(sensors)}")
    _LOGGER.info("=" * 60)


def export_discovered_calendars() -> Dict[str, Any]:
    """Export discovered calendars for use by config_flow."""
    return DISCOVERED_CALENDARS


def get_calendar_schema() -> Dict[str, Any]:
    """Get the configuration schema for discovered calendars."""
    return generate_config_schema()


class AlternativeTimeSensorBase(SensorEntity):
    """Base class for Alternative Time sensors - Version 2.5."""

    # Default update interval
    UPDATE_INTERVAL = 60

    def __init__(self, base_name: str, hass: HomeAssistant) -> None:
        """Initialize the sensor base with Home Assistant instance."""
        self._base_name = base_name
        self._hass = hass
        self._state = None
        self._last_update = None
        
        # Get user language from Home Assistant
        self._language = hass.config.language or 'en'
        
        # Use class-level UPDATE_INTERVAL
        self._update_interval = getattr(self.__class__, 'UPDATE_INTERVAL', 60)
        self._next_update = datetime.now()
        
        # Try to get calendar metadata
        self._metadata = self._get_metadata()
        
        _LOGGER.debug(
            f"Initialized {self.__class__.__name__} '{base_name}' "
            f"[{self._metadata.get('category', 'uncategorized')}] "
            f"Update: {self._update_interval}s, Language: {self._language}"
        )
    
    def _get_metadata(self) -> Dict[str, Any]:
        """Get metadata from module or class."""
        # Try to get from module
        module = self.__class__.__module__
        if module:
            try:
                mod = import_module(module)
                if hasattr(mod, 'CALENDAR_INFO'):
                    return mod.CALENDAR_INFO
            except:
                pass
        
        # Try class attribute
        if hasattr(self.__class__, 'CALENDAR_INFO'):
            return self.__class__.CALENDAR_INFO
        
        return {}
    
    def _translate(self, key: str, fallback: str = None) -> str:
        """Get translated string from metadata."""
        if not self._metadata:
            return fallback or key
        
        translations = self._metadata.get(key, {})
        if isinstance(translations, dict):
            # Try user language, then English, then fallback
            return translations.get(
                self._language,
                translations.get('en', fallback or key)
            )
        return translations or fallback or key
    
    @property
    def should_poll(self) -> bool:
        """Return True if entity has to be polled for state."""
        return True
    
    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return True
    
    @property
    def force_update(self) -> bool:
        """Force update even if state hasn't changed."""
        return True
    
    async def async_update(self) -> None:
        """Update the sensor asynchronously."""
        now = datetime.now()
        
        # Check if it's time to update
        if now >= self._next_update:
            if hasattr(self, 'update'):
                try:
                    self.update()
                    self._last_update = now
                    self._next_update = now + timedelta(seconds=self._update_interval)
                except Exception as e:
                    _LOGGER.error(f"Error updating {self._attr_name}: {e}")
                    _LOGGER.debug(traceback.format_exc())
    
    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._base_name)},
            "name": self._base_name,
            "manufacturer": "Alternative Time Systems",
            "model": "Time Calculator",
            "sw_version": "2.5.0",
        }
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return common state attributes."""
        attrs = {
            "update_interval": self._update_interval,
            "last_update": self._last_update.isoformat() if self._last_update else "Never",
            "next_update": self._next_update.isoformat() if self._next_update else "Unknown",
        }
        
        # Add metadata info if available
        if self._metadata:
            attrs["calendar_info"] = {
                "id": self._metadata.get('id', 'unknown'),
                "category": self._metadata.get('category', 'uncategorized'),
                "accuracy": self._metadata.get('accuracy', 'unknown'),
            }
            
            # Add reference URL if available
            if 'reference_url' in self._metadata:
                attrs["calendar_info"]["reference"] = self._metadata['reference_url']
        
        return attrs


class FallbackTimeSensor(AlternativeTimeSensorBase):
    """Fallback sensor when no calendars are configured."""
    
    UPDATE_INTERVAL = 60
    
    def __init__(self, base_name: str, hass: HomeAssistant) -> None:
        """Initialize the fallback sensor."""
        super().__init__(base_name, hass)
        self._attr_name = f"{base_name} Status"
        self._attr_unique_id = f"{base_name}_fallback"
        self._attr_icon = "mdi:clock-alert"
        _LOGGER.info("Created fallback sensor - no calendars configured")
    
    @property
    def state(self):
        """Return the state."""
        return self._state or "No calendars"
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return state attributes."""
        attrs = super().extra_state_attributes
        attrs.update({
            "message": "No calendars configured",
            "discovered_calendars": list(DISCOVERED_CALENDARS.keys()),
            "total_discovered": len(DISCOVERED_CALENDARS),
            "categories": list(set(
                c['info'].get('category', 'uncategorized') 
                for c in DISCOVERED_CALENDARS.values()
            )),
            "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })
        return attrs
    
    def update(self) -> None:
        """Update the sensor."""
        self._state = datetime.now().strftime("%H:%M:%S")