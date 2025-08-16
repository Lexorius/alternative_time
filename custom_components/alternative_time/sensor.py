"""Sensor platform for Alternative Time integration."""
from __future__ import annotations

import logging
from datetime import datetime

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

# Import all calendar implementations from subdirectory
from .calendars.timezone import TimezoneSensor
from .calendars.stardate import StardateSensor
from .calendars.swatch import SwatchTimeSensor
from .calendars.unix import UnixTimeSensor
from .calendars.julian import JulianDateSensor
from .calendars.decimal import DecimalTimeSensor
from .calendars.hexadecimal import HexadecimalTimeSensor
from .calendars.maya import MayaCalendarSensor
from .calendars.nato import NatoTimeSensor, NatoTimeZoneSensor, NatoTimeRescueSensor
from .calendars.attic import AtticCalendarSensor
from .calendars.suriyakati import SuriyakatiCalendarSensor
from .calendars.minguo import MinguoCalendarSensor
from .calendars.darian import DarianCalendarSensor
from .calendars.mars import MarsTimeSensor
from .calendars.eve import EveOnlineTimeSensor
from .calendars.shire import ShireCalendarSensor
from .calendars.rivendell import RivendellCalendarSensor
from .calendars.tamriel import TamrielCalendarSensor
from .calendars.egyptian import EgyptianCalendarSensor
from .calendars.discworld import DiscworldCalendarSensor
from .calendars.roman import RomanCalendarSensor

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Alternative Time sensors from a config entry."""
    config = config_entry.data
    base_name = config.get(CONF_NAME, "Alternative Time")
    
    sensors = []
    
    # Add timezone sensor if enabled
    if config.get(CONF_ENABLE_TIMEZONE, False):
        timezone = config.get(CONF_TIMEZONE, "UTC")
        sensors.append(TimezoneSensor(base_name, timezone))
    
    # Add Stardate sensor if enabled
    if config.get(CONF_ENABLE_STARDATE, False):
        sensors.append(StardateSensor(base_name))
    
    # Add Swatch Internet Time sensor if enabled
    if config.get(CONF_ENABLE_SWATCH, False):
        sensors.append(SwatchTimeSensor(base_name))
    
    # Add Unix Timestamp sensor if enabled
    if config.get(CONF_ENABLE_UNIX, False):
        sensors.append(UnixTimeSensor(base_name))
    
    # Add Julian Date sensor if enabled
    if config.get(CONF_ENABLE_JULIAN, False):
        sensors.append(JulianDateSensor(base_name))
    
    # Add Decimal Time sensor if enabled
    if config.get(CONF_ENABLE_DECIMAL, False):
        sensors.append(DecimalTimeSensor(base_name))
    
    # Add Hexadecimal Time sensor if enabled
    if config.get(CONF_ENABLE_HEXADECIMAL, False):
        sensors.append(HexadecimalTimeSensor(base_name))
    
    # Add Maya Calendar sensor if enabled
    if config.get(CONF_ENABLE_MAYA, False):
        sensors.append(MayaCalendarSensor(base_name))
    
    # Add NATO time sensors if enabled
    if config.get(CONF_ENABLE_NATO, False):
        sensors.append(NatoTimeSensor(base_name))
    
    if config.get(CONF_ENABLE_NATO_ZONE, False):
        sensors.append(NatoTimeZoneSensor(base_name))
    
    if config.get(CONF_ENABLE_NATO_RESCUE, False):
        sensors.append(NatoTimeRescueSensor(base_name))
    
    # Add Attic Calendar sensor if enabled
    if config.get(CONF_ENABLE_ATTIC, False):
        sensors.append(AtticCalendarSensor(base_name))
    
    # Add Suriyakati Calendar sensor if enabled
    if config.get(CONF_ENABLE_SURIYAKATI, False):
        sensors.append(SuriyakatiCalendarSensor(base_name))
    
    # Add Minguo Calendar sensor if enabled
    if config.get(CONF_ENABLE_MINGUO, False):
        sensors.append(MinguoCalendarSensor(base_name))
    
    # Add Darian Mars Calendar sensor if enabled
    if config.get(CONF_ENABLE_DARIAN, False):
        sensors.append(DarianCalendarSensor(base_name))
    
    # Add Mars Time sensor if enabled
    if config.get(CONF_ENABLE_MARS_TIME, False):
        mars_timezone = config.get(CONF_MARS_TIMEZONE, "MTC")
        sensors.append(MarsTimeSensor(base_name, mars_timezone))
    
    # Add EVE Online Time sensor if enabled
    if config.get(CONF_ENABLE_EVE, False):
        sensors.append(EveOnlineTimeSensor(base_name))
    
    # Add Shire Calendar sensor if enabled
    if config.get(CONF_ENABLE_SHIRE, False):
        sensors.append(ShireCalendarSensor(base_name))
    
    # Add Rivendell Calendar sensor if enabled
    if config.get(CONF_ENABLE_RIVENDELL, False):
        sensors.append(RivendellCalendarSensor(base_name))
    
    # Add Tamriel Calendar sensor if enabled
    if config.get(CONF_ENABLE_TAMRIEL, False):
        sensors.append(TamrielCalendarSensor(base_name))
    
    # Add Egyptian Calendar sensor if enabled
    if config.get(CONF_ENABLE_EGYPTIAN, False):
        sensors.append(EgyptianCalendarSensor(base_name))
    
    # Add Discworld Calendar sensor if enabled
    if config.get(CONF_ENABLE_DISCWORLD, False):
        sensors.append(DiscworldCalendarSensor(base_name))
    
    # Add Roman Calendar sensor if enabled
    if config.get(CONF_ENABLE_ROMAN, False):
        sensors.append(RomanCalendarSensor(base_name))
    
    if sensors:
        async_add_entities(sensors, True)
        _LOGGER.info(f"Added {len(sensors)} Alternative Time sensors")
    else:
        _LOGGER.warning("No time systems were enabled")


class AlternativeTimeSensorBase(SensorEntity):
    """Base class for Alternative Time sensors."""

    def __init__(self, base_name: str) -> None:
        """Initialize the sensor base."""
        self._base_name = base_name
        self._state = None
        
    @property
    def should_poll(self) -> bool:
        """Return True if entity has to be polled for state."""
        return True