"""Sensor platform for Alternative Time integration."""
from __future__ import annotations

import logging
from datetime import datetime
import traceback

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    CONF_NAME,
    CONF_TIMEZONE,
    CONF_ENABLE_TIMEZONE,
    CONF_ENABLE_STARDATE,
    CONF_ENABLE_SWATCH,
    CONF_ENABLE_UNIX,
    CONF_ENABLE_JULIAN,
    CONF_ENABLE_DECIMAL,
    CONF_ENABLE_HEXADECIMAL,
    CONF_ENABLE_MAYA,
    CONF_ENABLE_NATO,
    CONF_ENABLE_NATO_ZONE,
    CONF_ENABLE_NATO_RESCUE,
    CONF_ENABLE_ATTIC,
    CONF_ENABLE_SURIYAKATI,
    CONF_ENABLE_MINGUO,
    CONF_ENABLE_DARIAN,
    CONF_ENABLE_MARS_TIME,
    CONF_MARS_TIMEZONE,
    CONF_ENABLE_EVE,
    CONF_ENABLE_SHIRE,
    CONF_ENABLE_RIVENDELL,
    CONF_ENABLE_TAMRIEL,
    CONF_ENABLE_EGYPTIAN,
    CONF_ENABLE_DISCWORLD,
    CONF_ENABLE_ROMAN,
)

_LOGGER = logging.getLogger(__name__)

# Track which calendar modules are available
AVAILABLE_CALENDARS = {}


def try_import_calendar(module_name: str, class_name: str) -> bool:
    """Try to import a calendar module and register it."""
    try:
        # Fix: Use correct import path
        from importlib import import_module
        module = import_module(f'.calendars.{module_name}', package='custom_components.alternative_time')
        AVAILABLE_CALENDARS[module_name] = getattr(module, class_name)
        _LOGGER.debug(f"✓ Successfully imported {class_name} from calendars.{module_name}")
        return True
    except ImportError as e:
        _LOGGER.warning(f"✗ Could not import {class_name} from calendars.{module_name}: {e}")
        return False
    except AttributeError as e:
        _LOGGER.warning(f"✗ Module calendars.{module_name} exists but {class_name} not found: {e}")
        return False
    except Exception as e:
        _LOGGER.error(f"✗ Unexpected error importing calendars.{module_name}: {e}")
        return False


# Try to import all calendar implementations
_LOGGER.info("Starting import of calendar modules...")

# Technical/Modern
try_import_calendar('timezone', 'TimezoneSensor')
try_import_calendar('stardate', 'StardateSensor')
try_import_calendar('swatch', 'SwatchTimeSensor')
try_import_calendar('unix', 'UnixTimeSensor')
try_import_calendar('julian', 'JulianDateSensor')
try_import_calendar('decimal', 'DecimalTimeSensor')
try_import_calendar('hexadecimal', 'HexadecimalTimeSensor')

# Historical
try_import_calendar('maya', 'MayaCalendarSensor')
try_import_calendar('attic', 'AtticCalendarSensor')
try_import_calendar('suriyakati', 'SuriyakatiCalendarSensor')
try_import_calendar('egyptian', 'EgyptianCalendarSensor')
try_import_calendar('roman', 'RomanCalendarSensor')

# Asian
try_import_calendar('minguo', 'MinguoCalendarSensor')

# Military/NATO - Special handling for multiple classes in one module
nato_imported = try_import_calendar('nato', 'NatoTimeSensor')
if nato_imported:
    try:
        from importlib import import_module
        nato_module = import_module('.calendars.nato', package='custom_components.alternative_time')
        if hasattr(nato_module, 'NatoTimeZoneSensor'):
            AVAILABLE_CALENDARS['nato_zone'] = nato_module.NatoTimeZoneSensor
            _LOGGER.debug("✓ Successfully imported NatoTimeZoneSensor from calendars.nato")
        if hasattr(nato_module, 'NatoTimeRescueSensor'):
            AVAILABLE_CALENDARS['nato_rescue'] = nato_module.NatoTimeRescueSensor
            _LOGGER.debug("✓ Successfully imported NatoTimeRescueSensor from calendars.nato")
    except Exception as e:
        _LOGGER.warning(f"Could not import additional NATO sensors: {e}")

# Space/Mars
try_import_calendar('darian', 'DarianCalendarSensor')
try_import_calendar('mars', 'MarsTimeSensor')

# Sci-Fi
try_import_calendar('eve', 'EveOnlineTimeSensor')

# Fantasy
try_import_calendar('shire', 'ShireCalendarSensor')
try_import_calendar('rivendell', 'RivendellCalendarSensor')
try_import_calendar('tamriel', 'TamrielCalendarSensor')
try_import_calendar('discworld', 'DiscworldCalendarSensor')

_LOGGER.info(f"Calendar import complete. {len(AVAILABLE_CALENDARS)} calendars available: {', '.join(AVAILABLE_CALENDARS.keys())}")


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Alternative Time sensors from a config entry."""
    _LOGGER.info(f"Setting up Alternative Time sensors for '{config_entry.title}'")
    _LOGGER.debug(f"Config entry ID: {config_entry.entry_id}")
    _LOGGER.debug(f"Config data: {config_entry.data}")
    
    config = config_entry.data
    base_name = config.get(CONF_NAME, "Alternative Time")
    _LOGGER.info(f"Base name for sensors: '{base_name}'")
    
    sensors = []
    enabled_count = 0
    skipped_count = 0
    
    # Configuration mapping
    calendar_configs = [
        (CONF_ENABLE_TIMEZONE, 'timezone', lambda: AVAILABLE_CALENDARS.get('timezone', None)(base_name, config.get(CONF_TIMEZONE, "UTC"))),
        (CONF_ENABLE_STARDATE, 'stardate', lambda: AVAILABLE_CALENDARS.get('stardate', None)(base_name)),
        (CONF_ENABLE_SWATCH, 'swatch', lambda: AVAILABLE_CALENDARS.get('swatch', None)(base_name)),
        (CONF_ENABLE_UNIX, 'unix', lambda: AVAILABLE_CALENDARS.get('unix', None)(base_name)),
        (CONF_ENABLE_JULIAN, 'julian', lambda: AVAILABLE_CALENDARS.get('julian', None)(base_name)),
        (CONF_ENABLE_DECIMAL, 'decimal', lambda: AVAILABLE_CALENDARS.get('decimal', None)(base_name)),
        (CONF_ENABLE_HEXADECIMAL, 'hexadecimal', lambda: AVAILABLE_CALENDARS.get('hexadecimal', None)(base_name)),
        (CONF_ENABLE_MAYA, 'maya', lambda: AVAILABLE_CALENDARS.get('maya', None)(base_name)),
        (CONF_ENABLE_NATO, 'nato', lambda: AVAILABLE_CALENDARS.get('nato', None)(base_name)),
        (CONF_ENABLE_NATO_ZONE, 'nato_zone', lambda: AVAILABLE_CALENDARS.get('nato_zone', None)(base_name)),
        (CONF_ENABLE_NATO_RESCUE, 'nato_rescue', lambda: AVAILABLE_CALENDARS.get('nato_rescue', None)(base_name)),
        (CONF_ENABLE_ATTIC, 'attic', lambda: AVAILABLE_CALENDARS.get('attic', None)(base_name)),
        (CONF_ENABLE_SURIYAKATI, 'suriyakati', lambda: AVAILABLE_CALENDARS.get('suriyakati', None)(base_name)),
        (CONF_ENABLE_MINGUO, 'minguo', lambda: AVAILABLE_CALENDARS.get('minguo', None)(base_name)),
        (CONF_ENABLE_DARIAN, 'darian', lambda: AVAILABLE_CALENDARS.get('darian', None)(base_name)),
        (CONF_ENABLE_MARS_TIME, 'mars', lambda: AVAILABLE_CALENDARS.get('mars', None)(base_name, config.get(CONF_MARS_TIMEZONE, "MTC"))),
        (CONF_ENABLE_EVE, 'eve', lambda: AVAILABLE_CALENDARS.get('eve', None)(base_name)),
        (CONF_ENABLE_SHIRE, 'shire', lambda: AVAILABLE_CALENDARS.get('shire', None)(base_name)),
        (CONF_ENABLE_RIVENDELL, 'rivendell', lambda: AVAILABLE_CALENDARS.get('rivendell', None)(base_name)),
        (CONF_ENABLE_TAMRIEL, 'tamriel', lambda: AVAILABLE_CALENDARS.get('tamriel', None)(base_name)),
        (CONF_ENABLE_EGYPTIAN, 'egyptian', lambda: AVAILABLE_CALENDARS.get('egyptian', None)(base_name)),
        (CONF_ENABLE_DISCWORLD, 'discworld', lambda: AVAILABLE_CALENDARS.get('discworld', None)(base_name)),
        (CONF_ENABLE_ROMAN, 'roman', lambda: AVAILABLE_CALENDARS.get('roman', None)(base_name)),
    ]
    
    # Create sensors for enabled calendars
    for conf_key, calendar_name, sensor_factory in calendar_configs:
        if config.get(conf_key, False):
            enabled_count += 1
            _LOGGER.debug(f"Config {conf_key} is enabled, attempting to create {calendar_name} sensor...")
            
            try:
                # Check if the calendar module is available
                if calendar_name not in AVAILABLE_CALENDARS and calendar_name not in ['nato_zone', 'nato_rescue']:
                    _LOGGER.warning(f"Calendar '{calendar_name}' is enabled but module not available")
                    skipped_count += 1
                    continue
                
                # Create the sensor
                sensor = sensor_factory()
                if sensor:
                    sensors.append(sensor)
                    _LOGGER.info(f"✓ Created {calendar_name} sensor")
                else:
                    _LOGGER.warning(f"✗ Failed to create {calendar_name} sensor (factory returned None)")
                    skipped_count += 1
                    
            except Exception as e:
                _LOGGER.error(f"✗ Error creating {calendar_name} sensor: {e}")
                _LOGGER.debug(traceback.format_exc())
                skipped_count += 1
        else:
            _LOGGER.debug(f"Config {conf_key} is disabled, skipping {calendar_name}")
    
    # Add fallback sensor if nothing was created
    if not sensors:
        _LOGGER.warning("No sensors were created! Adding a fallback sensor...")
        sensors.append(FallbackTimeSensor(base_name))
    
    # Add all sensors
    async_add_entities(sensors, True)
    
    # Summary logging
    _LOGGER.info("=" * 50)
    _LOGGER.info(f"Alternative Time Setup Complete for '{base_name}'")
    _LOGGER.info(f"  Enabled in config: {enabled_count}")
    _LOGGER.info(f"  Successfully created: {len(sensors)}")
    _LOGGER.info(f"  Skipped (missing/error): {skipped_count}")
    _LOGGER.info(f"  Active sensors: {', '.join([s.name for s in sensors])}")
    _LOGGER.info("=" * 50)


class AlternativeTimeSensorBase(SensorEntity):
    """Base class for Alternative Time sensors."""

    def __init__(self, base_name: str) -> None:
        """Initialize the sensor base."""
        self._base_name = base_name
        self._state = None
        _LOGGER.debug(f"Initialized base sensor with name: {base_name}")
        
    @property
    def should_poll(self) -> bool:
        """Return True if entity has to be polled for state."""
        return True
    
    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._state is not None


class FallbackTimeSensor(AlternativeTimeSensorBase):
    """Fallback sensor when no calendars are available."""
    
    def __init__(self, base_name: str) -> None:
        """Initialize the fallback sensor."""
        super().__init__(base_name)
        self._attr_name = f"{base_name} Status"
        self._attr_unique_id = f"{base_name}_fallback"
        self._attr_icon = "mdi:clock-alert"
        _LOGGER.info("Created fallback sensor - check configuration!")
    
    @property
    def state(self):
        """Return the state."""
        return self._state
    
    @property
    def extra_state_attributes(self):
        """Return state attributes."""
        return {
            "message": "No calendars configured",
            "available_calendars": list(AVAILABLE_CALENDARS.keys()),
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
    
    def update(self) -> None:
        """Update the sensor."""
        self._state = "No calendars active"