from __future__ import annotations

import logging
from datetime import datetime, timedelta
import pytz
import math

from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

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
    SENSOR_TYPES,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Alternative Time sensors from a config entry."""
    config = hass.data[DOMAIN][config_entry.entry_id]
    
    sensors = []
    base_name = config[CONF_NAME]

    if config.get(CONF_ENABLE_TIMEZONE, False):
        sensors.append(TimezoneSensor(base_name, config[CONF_TIMEZONE]))
    
    if config.get(CONF_ENABLE_STARDATE, False):
        sensors.append(StardateSensor(base_name))
    
    if config.get(CONF_ENABLE_SWATCH, False):
        sensors.append(SwatchTimeSensor(base_name))
    
    if config.get(CONF_ENABLE_UNIX, False):
        sensors.append(UnixTimeSensor(base_name))
    
    if config.get(CONF_ENABLE_JULIAN, False):
        sensors.append(JulianDateSensor(base_name))
    
    if config.get(CONF_ENABLE_DECIMAL, False):
        sensors.append(DecimalTimeSensor(base_name))
    
    if config.get(CONF_ENABLE_HEXADECIMAL, False):
        sensors.append(HexadecimalTimeSensor(base_name))

    async_add_entities(sensors, True)


class AlternativeTimeSensorBase(SensorEntity):
    """Base class for Alternative Time sensors."""

    _attr_should_poll = True

    def __init__(self, base_name: str, sensor_type: str) -> None:
        """Initialize the sensor."""
        self._base_name = base_name
        self._sensor_type = sensor_type
        self._attr_name = f"{base_name} {SENSOR_TYPES[sensor_type]}"
        self._attr_unique_id = f"{base_name}_{sensor_type}"
        self._state = None

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    async def async_update(self) -> None:
        """Update the sensor."""
        self._state = self.calculate_time()

    def calculate_time(self) -> str:
        """Calculate the time value. To be overridden by subclasses."""
        return ""


class TimezoneSensor(AlternativeTimeSensorBase):
    """Sensor for displaying time in a specific timezone."""

    def __init__(self, base_name: str, timezone: str) -> None:
        """Initialize the timezone sensor."""
        super().__init__(base_name, "timezone")
        self._timezone = pytz.timezone(timezone)
        self._attr_icon = "mdi:clock-time-four-outline"

    def calculate_time(self) -> str:
        """Calculate current time in specified timezone."""
        now = datetime.now(self._timezone)
        return now.strftime("%H:%M:%S %Z")


class StardateSensor(AlternativeTimeSensorBase):
    """Sensor for displaying Stardate (Star Trek style)."""

    def __init__(self, base_name: str) -> None:
        """Initialize the stardate sensor."""
        super().__init__(base_name, "stardate")
        self._attr_icon = "mdi:star-clock"

    def calculate_time(self) -> str:
        """Calculate current Stardate."""
        # TNG-style stardate calculation
        now = datetime.now()
        base_year = 2323  # TNG era base year
        current_year = now.year
        day_of_year = now.timetuple().tm_yday
        
        # Calculate stardate (simplified TNG formula)
        stardate = 1000 * (current_year - base_year) + (1000 * day_of_year / 365.25)
        stardate += (now.hour * 60 + now.minute) / 1440 * 10  # Add time of day
        
        return f"{stardate:.2f}"


class SwatchTimeSensor(AlternativeTimeSensorBase):
    """Sensor for displaying Swatch Internet Time."""

    def __init__(self, base_name: str) -> None:
        """Initialize the Swatch time sensor."""
        super().__init__(base_name, "swatch")
        self._attr_icon = "mdi:web-clock"

    def calculate_time(self) -> str:
        """Calculate current Swatch Internet Time."""
        # Swatch Internet Time (Biel Mean Time)
        bmt = pytz.timezone('Europe/Zurich')
        now = datetime.now(bmt)
        
        # Calculate beats (1000 beats per day)
        seconds_since_midnight = (now.hour * 3600 + now.minute * 60 + now.second)
        beats = seconds_since_midnight / 86.4
        
        return f"@{beats:06.2f}"


class UnixTimeSensor(AlternativeTimeSensorBase):
    """Sensor for displaying Unix timestamp."""

    def __init__(self, base_name: str) -> None:
        """Initialize the Unix time sensor."""
        super().__init__(base_name, "unix")
        self._attr_icon = "mdi:counter"

    def calculate_time(self) -> str:
        """Calculate current Unix timestamp."""
        return str(int(datetime.now().timestamp()))


class JulianDateSensor(AlternativeTimeSensorBase):
    """Sensor for displaying Julian Date."""

    def __init__(self, base_name: str) -> None:
        """Initialize the Julian date sensor."""
        super().__init__(base_name, "julian")
        self._attr_icon = "mdi:calendar-clock"

    def calculate_time(self) -> str:
        """Calculate current Julian Date."""
        now = datetime.now()
        a = (14 - now.month) // 12
        y = now.year + 4800 - a
        m = now.month + 12 * a - 3
        
        jdn = now.day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
        jd = jdn + (now.hour - 12) / 24 + now.minute / 1440 + now.second / 86400
        
        return f"{jd:.5f}"


class DecimalTimeSensor(AlternativeTimeSensorBase):
    """Sensor for displaying Decimal Time (French Revolutionary)."""

    def __init__(self, base_name: str) -> None:
        """Initialize the decimal time sensor."""
        super().__init__(base_name, "decimal")
        self._attr_icon = "mdi:clock-digital"

    def calculate_time(self) -> str:
        """Calculate current Decimal Time."""
        now = datetime.now()
        seconds_since_midnight = now.hour * 3600 + now.minute * 60 + now.second
        
        # Decimal time: 10 hours, 100 minutes per hour, 100 seconds per minute
        decimal_seconds = seconds_since_midnight * 100000 / 86400
        
        decimal_hours = int(decimal_seconds // 10000)
        decimal_minutes = int((decimal_seconds % 10000) // 100)
        decimal_seconds = int(decimal_seconds % 100)
        
        return f"{decimal_hours:01d}:{decimal_minutes:02d}:{decimal_seconds:02d}"


class HexadecimalTimeSensor(AlternativeTimeSensorBase):
    """Sensor for displaying Hexadecimal Time."""

    def __init__(self, base_name: str) -> None:
        """Initialize the hexadecimal time sensor."""
        super().__init__(base_name, "hexadecimal")
        self._attr_icon = "mdi:hexadecimal"

    def calculate_time(self) -> str:
        """Calculate current Hexadecimal Time."""
        now = datetime.now()
        seconds_since_midnight = now.hour * 3600 + now.minute * 60 + now.second
        
        # Hexadecimal time: divide day into 65536 (0x10000) parts
        hex_time = int(seconds_since_midnight * 65536 / 86400)
        
        return f".{hex_time:04X}"