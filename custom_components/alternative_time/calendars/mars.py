"""Mars Time implementation with timezone support."""
from __future__ import annotations

from datetime import datetime, timedelta
import logging
import math

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant

from ..const import CONF_MARS_TIMEZONE

_LOGGER = logging.getLogger(__name__)


class MarsTimeSensor(SensorEntity):
    """Sensor for displaying Mars time with timezone support."""

    def __init__(self, base_name: str, mars_timezone: str = "MTC") -> None:
        """Initialize the Mars time sensor."""
        self._attr_name = f"{base_name} Mars Time"
        self._attr_unique_id = f"{base_name}_mars_time"
        self._attr_icon = "mdi:clock-digital"
        self._state = None
        self._mars_timezone = mars_timezone

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        mars_time = self._calculate_mars_time(datetime.utcnow())
        
        return {
            "mars_sol_date": mars_time["msd"],
            "coordinated_mars_time": mars_time["mtc"],
            "local_mars_time": mars_time["local_time"],
            "timezone": self._mars_timezone,
            "timezone_offset": mars_time["timezone_offset"],
            "sol_number": mars_time["sol_number"],
            "mission_sol": mars_time["mission_sol"],
            "ls": mars_time["ls"],  # Solar longitude
            "earth_time_utc": datetime.utcnow().isoformat(),
            "subsolar_longitude": mars_time["subsolar_longitude"],
            "equation_of_time": mars_time["equation_of_time"],
            "sunrise": mars_time["sunrise"],
            "sunset": mars_time["sunset"],
            "solar_elevation": mars_time["solar_elevation"],
        }

    def _calculate_mars_time(self, earth_utc: datetime) -> dict:
        """Calculate Mars time from Earth UTC time."""
        # Mars constants
        MARS_DAY_IN_SECONDS = 88775.244  # Mars sol in Earth seconds
        EARTH_DAY_IN_SECONDS = 86400.0
        MARS_TROPICAL_YEAR = 686.9725  # Mars solar days
        
        # Calculate Julian Date
        a = (14 - earth_utc.month) // 12
        y = earth_utc.year + 4800 - a
        m = earth_utc.month + 12 * a - 3
        
        jdn = earth_utc.day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
        jd = jdn + (earth_utc.hour - 12) / 24.0 + earth_utc.minute / 1440.0 + earth_utc.second / 86400.0
        
        # Calculate Mars Sol Date (MSD)
        # MSD epoch is December 29, 1873, 00:00:00 UTC (JD 2405522.0)
        msd_epoch_jd = 2405522.0
        msd = (jd - msd_epoch_jd) / (MARS_DAY_IN_SECONDS / EARTH_DAY_IN_SECONDS)
        
        # Calculate Coordinated Mars Time (MTC)
        # MTC is analogous to UTC on Earth
        mtc_hours = (msd % 1) * 24
        mtc_hour = int(mtc_hours)
        mtc_minutes = (mtc_hours - mtc_hour) * 60
        mtc_minute = int(mtc_minutes)
        mtc_second = int((mtc_minutes - mtc_minute) * 60)
        
        mtc_time = f"{mtc_hour:02d}:{mtc_minute:02d}:{mtc_second:02d}"
        
        # Mars timezone offsets (in Mars hours)
        # Based on 15-degree longitude zones similar to Earth
        mars_timezones = {
            "MTC": 0,           # Coordinated Mars Time (0° - Airy-0 crater)
            "AMT": 0,           # Airy Mean Time (same as MTC)
            "OLY": -9,          # Olympus Mons Time (≈ -135°)
            "ELY": 4,           # Elysium Time (≈ +60°)
            "CHA": 12,          # Chryse Time (≈ +180°)
            "MAR": -6,          # Mariner Valley Time (≈ -90°)
            "ARA": 3,           # Arabia Terra Time (≈ +45°)
            "THR": -3,          # Tharsis Time (≈ -45°)
            "HEL": 7,           # Hellas Basin Time (≈ +105°)
            "VIK": -2,          # Viking 1 Landing Site (≈ -30°)
            "PTH": 2,           # Pathfinder Landing Site (≈ +30°)
            "OPP": 11,          # Opportunity Landing Site (≈ +165°)
            "SPI": 10,          # Spirit Landing Site (≈ +150°)
            "CUR": 9,           # Curiosity/Gale Crater Time (≈ +135°)
            "PER": 5,           # Perseverance/Jezero Time (≈ +75°)
        }
        
        # Calculate local Mars time based on timezone
        timezone_offset = mars_timezones.get(self._mars_timezone, 0)
        local_hours = mtc_hours + timezone_offset
        
        # Handle day boundary crossing
        if local_hours >= 24:
            local_hours -= 24
        elif local_hours < 0:
            local_hours += 24
            
        local_hour = int(local_hours)
        local_minutes = (local_hours - local_hour) * 60
        local_minute = int(local_minutes)
        local_second = int((local_minutes - local_minute) * 60)
        
        local_time = f"{local_hour:02d}:{local_minute:02d}:{local_second:02d}"
        
        # Calculate solar longitude (Ls)
        # Approximate calculation
        mars_year_fraction = (msd / MARS_TROPICAL_YEAR) % 1
        ls = mars_year_fraction * 360
        
        # Calculate subsolar longitude
        subsolar_longitude = (msd * 360) % 360 - 180
        
        # Equation of time (approximate)
        # Mars has a more eccentric orbit than Earth
        eot_minutes = 50 * math.sin(math.radians(2 * ls)) - 3 * math.sin(math.radians(4 * ls))
        
        # Calculate approximate sunrise/sunset times (varies by latitude)
        # Using equatorial approximation
        sunrise_hour = 6 - eot_minutes / 60
        sunset_hour = 18 - eot_minutes / 60
        
        sunrise_time = f"{int(sunrise_hour):02d}:{int((sunrise_hour % 1) * 60):02d}"
        sunset_time = f"{int(sunset_hour):02d}:{int((sunset_hour % 1) * 60):02d}"
        
        # Solar elevation (approximate, at local noon)
        solar_elevation = 90 - abs(subsolar_longitude - timezone_offset * 15)
        
        # Mission sol (example: sols since Perseverance landing)
        perseverance_landing_msd = 52304.5  # February 18, 2021
        mission_sol = int(msd - perseverance_landing_msd) if self._mars_timezone == "PER" else None
        
        return {
            "msd": round(msd, 4),
            "mtc": mtc_time,
            "local_time": local_time,
            "timezone_offset": timezone_offset,
            "sol_number": int(msd),
            "mission_sol": mission_sol,
            "ls": round(ls, 1),
            "subsolar_longitude": round(subsolar_longitude, 1),
            "equation_of_time": round(eot_minutes, 1),
            "sunrise": sunrise_time,
            "sunset": sunset_time,
            "solar_elevation": round(solar_elevation, 1),
        }

    def update(self) -> None:
        """Update the sensor."""
        mars_time = self._calculate_mars_time(datetime.utcnow())
        
        # Format: HH:MM:SS TZ (Sol XXXXX)
        # Example: "14:23:45 MTC (Sol 52984)"
        self._state = f"{mars_time['local_time']} {self._mars_timezone}"