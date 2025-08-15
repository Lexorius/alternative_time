from __future__ import annotations

import logging
from datetime import datetime, timedelta
import math

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_time_interval

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
)

_LOGGER = logging.getLogger(__name__)

try:
    import pytz
    HAS_PYTZ = True
except ImportError:
    HAS_PYTZ = False
    _LOGGER.warning("pytz not installed, timezone support will be limited")


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
        sensors.append(TimezoneSensor(base_name, config.get(CONF_TIMEZONE, "UTC")))
    
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
    
    if config.get(CONF_ENABLE_MAYA, False):
        sensors.append(MayaCalendarSensor(base_name))
    
    if config.get(CONF_ENABLE_NATO, False):
        sensors.append(NatoTimeSensor(base_name))
    
    if config.get(CONF_ENABLE_NATO_ZONE, False):
        sensors.append(NatoTimeZoneSensor(base_name))
    
    if config.get(CONF_ENABLE_NATO_RESCUE, False):
        sensors.append(NatoTimeRescueSensor(base_name))
    
    if config.get(CONF_ENABLE_ATTIC, False):
        sensors.append(AtticCalendarSensor(base_name))
    
    if config.get(CONF_ENABLE_SURIYAKATI, False):
        sensors.append(SuriyakatiCalendarSensor(base_name))
    
    if config.get(CONF_ENABLE_MINGUO, False):
        sensors.append(MinguoCalendarSensor(base_name))
    
    if config.get(CONF_ENABLE_DARIAN, False):
        sensors.append(DarianCalendarSensor(base_name))
    
    if config.get(CONF_ENABLE_MARS_TIME, False):
        sensors.append(MarsTimeSensor(base_name, config.get(CONF_MARS_TIMEZONE, "MTC+0 (Airy-0)")))
    
    if config.get(CONF_ENABLE_EVE, False):
        sensors.append(EveOnlineTimeSensor(base_name))
    
    if config.get(CONF_ENABLE_SHIRE, False):
        sensors.append(ShireCalendarSensor(base_name))
    
    if config.get(CONF_ENABLE_RIVENDELL, False):
        sensors.append(RivendellCalendarSensor(base_name))

    async_add_entities(sensors, True)


class AlternativeTimeSensorBase(SensorEntity):
    """Base class for Alternative Time sensors."""

    _attr_should_poll = False  # We'll use time-based updates instead

    def __init__(self, base_name: str, sensor_type: str, friendly_name: str) -> None:
        """Initialize the sensor."""
        self._base_name = base_name
        self._sensor_type = sensor_type
        self._attr_name = f"{base_name} {friendly_name}"
        self._attr_unique_id = f"{base_name}_{sensor_type}"
        self._state = None
        self._update_interval = timedelta(seconds=1)  # Default 1 second update
        self._unsub_timer = None

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def update_interval(self) -> timedelta:
        """Return the update interval."""
        return self._update_interval

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        await super().async_added_to_hass()
        
        # Set up the update interval
        self._unsub_timer = async_track_time_interval(
            self.hass,
            self._async_update_time,
            self._update_interval
        )
        
        # Initial update
        await self._async_update_time(None)

    async def async_will_remove_from_hass(self) -> None:
        """When entity will be removed from hass."""
        if self._unsub_timer:
            self._unsub_timer()
        await super().async_will_remove_from_hass()

    async def _async_update_time(self, now) -> None:
        """Update the time."""
        self._state = self.calculate_time()
        self.async_write_ha_state()

    def calculate_time(self) -> str:
        """Calculate the time value. To be overridden by subclasses."""
        return ""

class TimezoneSensor(AlternativeTimeSensorBase):
    """Sensor for displaying time in a specific timezone."""

    def __init__(self, base_name: str, timezone: str) -> None:
        """Initialize the timezone sensor."""
        super().__init__(base_name, "timezone", "Zeitzone")
        self._timezone_str = timezone
        self._attr_icon = "mdi:clock-time-four-outline"
        self._update_interval = timedelta(seconds=1)  # Update every second
        self._timezone = None  # Will be initialized in async_added_to_hass

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        # Initialize timezone in executor to avoid blocking
        if HAS_PYTZ:
            try:
                self._timezone = await self.hass.async_add_executor_job(
                    pytz.timezone, self._timezone_str
                )
            except Exception:
                _LOGGER.warning(f"Could not load timezone {self._timezone_str}")
                self._timezone = None
        
        await super().async_added_to_hass()

    def calculate_time(self) -> str:
        """Calculate current time in specified timezone."""
        if HAS_PYTZ and self._timezone:
            now = datetime.now(self._timezone)
            return now.strftime("%H:%M:%S %Z")
        else:
            # Fallback without pytz
            now = datetime.now()
            return now.strftime("%H:%M:%S") + f" {self._timezone_str}"


class StardateSensor(AlternativeTimeSensorBase):
    """Sensor for displaying Stardate (Star Trek style)."""

    def __init__(self, base_name: str) -> None:
        """Initialize the stardate sensor."""
        super().__init__(base_name, "stardate", "Sternzeit")
        self._attr_icon = "mdi:star-four-points"
        self._update_interval = timedelta(seconds=10)  # Update every 10 seconds

    def calculate_time(self) -> str:
        """Calculate current Stardate."""
        now = datetime.now()
        base_year = 2323
        current_year = now.year
        day_of_year = now.timetuple().tm_yday
        
        stardate = 1000 * (current_year - base_year) + (1000 * day_of_year / 365.25)
        stardate += (now.hour * 60 + now.minute) / 1440 * 10
        
        return f"{stardate:.2f}"


class SwatchTimeSensor(AlternativeTimeSensorBase):
    """Sensor for displaying Swatch Internet Time."""

    def __init__(self, base_name: str) -> None:
        """Initialize the Swatch time sensor."""
        super().__init__(base_name, "swatch", "Swatch Internet Time")
        self._attr_icon = "mdi:web-clock"
        self._update_interval = timedelta(seconds=1)  # Update every second for smooth beats
        self._bmt = None  # Will be initialized in async_added_to_hass

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        # Initialize timezone in executor to avoid blocking
        if HAS_PYTZ:
            try:
                self._bmt = await self.hass.async_add_executor_job(
                    pytz.timezone, 'Europe/Zurich'
                )
            except Exception:
                _LOGGER.warning("Could not load timezone Europe/Zurich for Swatch time")
                self._bmt = None
        
        await super().async_added_to_hass()

    def calculate_time(self) -> str:
        """Calculate current Swatch Internet Time."""
        if HAS_PYTZ and self._bmt:
            now = datetime.now(self._bmt)
        else:
            # Fallback: use UTC+1 as approximation for Biel Mean Time
            now = datetime.utcnow() + timedelta(hours=1)
        
        seconds_since_midnight = (now.hour * 3600 + now.minute * 60 + now.second)
        beats = seconds_since_midnight / 86.4
        
        return f"@{beats:06.2f}"


class UnixTimeSensor(AlternativeTimeSensorBase):
    """Sensor for displaying Unix timestamp."""

    def __init__(self, base_name: str) -> None:
        """Initialize the Unix time sensor."""
        super().__init__(base_name, "unix", "Unix Timestamp")
        self._attr_icon = "mdi:counter"
        self._update_interval = timedelta(seconds=1)  # Update every second

    def calculate_time(self) -> str:
        """Calculate current Unix timestamp."""
        return str(int(datetime.now().timestamp()))


class JulianDateSensor(AlternativeTimeSensorBase):
    """Sensor for displaying Julian Date."""

    def __init__(self, base_name: str) -> None:
        """Initialize the Julian date sensor."""
        super().__init__(base_name, "julian", "Julianisches Datum")
        self._attr_icon = "mdi:calendar-clock"
        self._update_interval = timedelta(seconds=60)  # Update every minute

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
        super().__init__(base_name, "decimal", "Dezimalzeit")
        self._attr_icon = "mdi:clock-digital"
        self._update_interval = timedelta(seconds=1)  # Update every second

    def calculate_time(self) -> str:
        """Calculate current Decimal Time."""
        now = datetime.now()
        seconds_since_midnight = now.hour * 3600 + now.minute * 60 + now.second
        
        decimal_seconds = seconds_since_midnight * 100000 / 86400
        
        decimal_hours = int(decimal_seconds // 10000)
        decimal_minutes = int((decimal_seconds % 10000) // 100)
        decimal_seconds = int(decimal_seconds % 100)
        
        return f"{decimal_hours:01d}:{decimal_minutes:02d}:{decimal_seconds:02d}"


class HexadecimalTimeSensor(AlternativeTimeSensorBase):
    """Sensor for displaying Hexadecimal Time."""

    def __init__(self, base_name: str) -> None:
        """Initialize the hexadecimal time sensor."""
        super().__init__(base_name, "hexadecimal", "Hexadezimalzeit")
        self._attr_icon = "mdi:hexadecimal"
        self._update_interval = timedelta(seconds=5)  # Update every 5 seconds

    def calculate_time(self) -> str:
        """Calculate current Hexadecimal Time."""
        now = datetime.now()
        seconds_since_midnight = now.hour * 3600 + now.minute * 60 + now.second
        
        hex_time = int(seconds_since_midnight * 65536 / 86400)
        
        return f".{hex_time:04X}"

class ShireCalendarSensor(AlternativeTimeSensorBase):
    """Sensor for displaying Shire Reckoning (Hobbit Calendar)."""

    def __init__(self, base_name: str) -> None:
        """Initialize the Shire calendar sensor."""
        super().__init__(base_name, "shire", "Auenland-Kalender")
        self._attr_icon = "mdi:pipe"
        self._update_interval = timedelta(hours=1)  # Update every hour
        
        # Shire months (12 months + special days)
        self.shire_months = [
            "Afteryule",     # January (Nachneujahr)
            "Solmath",       # February (Schlammich)
            "Rethe",         # March (Lenz)
            "Astron",        # April (Ostermond)
            "Thrimidge",     # May (Dreimelch)
            "Forelithe",     # June (Vormittsommer)
            "Afterlithe",    # July (Nachmittsommer)
            "Wedmath",       # August (Weidemond)
            "Halimath",      # September (Herbstmond)
            "Winterfilth",   # October (Winterfülle)
            "Blotmath",      # November (Nebelmond)
            "Foreyule"       # December (Vorneujahr)
        ]
        
        # Shire weekdays (7 days)
        self.shire_days = [
            "Sterrendei",    # Saturday (Stars-day)
            "Sonnendei",     # Sunday (Sun-day)
            "Monendei",      # Monday (Moon-day)
            "Trewesdei",     # Tuesday (Trees-day)
            "Hevenesdei",    # Wednesday (Heavens-day)
            "Meresdei",      # Thursday (Meres/Sea-day)
            "Highdei"        # Friday (High-day)
        ]
        
        # Special days (not part of any month)
        self.special_days = {
            1: "2 Yule",     # January 1
            182: "1 Lithe",  # June 30 (Mid-year's day eve)
            183: "Mid-year's Day",  # July 1
            184: "2 Lithe",  # July 2
            185: "Overlithe", # Leap year only
            365: "1 Yule"    # December 31
        }
        
        # Important Shire dates
        self.shire_events = {
            (2, 2): "Groundhog Day",  # Candlemas
            (3, 25): "Elven New Year",
            (4, 6): "Mallorn Flowering",
            (5, 1): "May Day",
            (6, 22): "Bilbo & Frodo's Birthday",
            (9, 22): "Bilbo & Frodo's Birthday", 
            (11, 2): "Full Harvest"
        }

    def calculate_time(self) -> str:
        """Calculate current Shire Reckoning date."""
        now = datetime.now()
        
        # Shire Reckoning starts from Third Age 1601
        # For game purposes, we'll align it with current year
        # S.R. 1420 = "present day" (end of LOTR)
        # Each real year = 1 Shire year
        base_year = 1420
        years_since_2000 = now.year - 2000
        shire_year = base_year + years_since_2000
        
        # Calculate day of year
        day_of_year = now.timetuple().tm_yday
        
        # Check for special days
        if day_of_year in [1, 182, 183, 184, 365]:
            special = self.special_days.get(day_of_year, "")
            if special:
                # Format for special days
                return f"S.R. {shire_year} - {special}"
        
        # Adjust for special days in middle of year
        if day_of_year > 183:
            day_of_year -= 2  # Account for Lithe days
        
        # Calculate month and day (30 days per month)
        month_index = min((day_of_year - 1) // 30, 11)
        day_of_month = ((day_of_year - 1) % 30) + 1
        
        shire_month = self.shire_months[month_index]
        
        # Calculate weekday
        weekday_index = now.weekday()
        # Adjust to Shire week (starts on Sterrendei/Saturday)
        shire_weekday_index = (weekday_index + 2) % 7
        shire_weekday = self.shire_days[shire_weekday_index]
        
        # Check for events
        event = self.shire_events.get((month_index + 1, day_of_month), "")
        event_str = f" - {event}" if event else ""
        
        # Determine meal time (Hobbits have many meals!)
        hour = now.hour
        if 6 <= hour < 8:
            meal = "🍳 First Breakfast"
        elif 8 <= hour < 11:
            meal = "🥐 Second Breakfast"
        elif 11 <= hour < 13:
            meal = "🍽️ Elevenses"
        elif 13 <= hour < 15:
            meal = "🍖 Luncheon"
        elif 15 <= hour < 17:
            meal = "☕ Afternoon Tea"
        elif 17 <= hour < 19:
            meal = "🍰 Dinner"
        elif 19 <= hour < 21:
            meal = "🍻 Supper"
        else:
            meal = "🛌 Sleep Time"
        
        # Format: S.R. Year, Day Month (Weekday) | Meal Time
        # Example: "S.R. 1445, 22 Halimath (Highdei) | 🍖 Luncheon - Bilbo's Birthday"
        return f"S.R. {shire_year}, {day_of_month} {shire_month} ({shire_weekday}) | {meal}{event_str}"


class RivendellCalendarSensor(AlternativeTimeSensorBase):
    """Sensor for displaying Calendar of Imladris (Elven Calendar)."""

    def __init__(self, base_name: str) -> None:
        """Initialize the Rivendell calendar sensor."""
        super().__init__(base_name, "rivendell", "Kalender von Imladris")
        self._attr_icon = "mdi:leaf"
        self._update_interval = timedelta(hours=1)  # Update every hour
        
        # Elven seasons (6 seasons, not months)
        self.elven_seasons = [
            ("Tuilë", "🌸"),      # Spring (54 days)
            ("Lairë", "☀️"),      # Summer (72 days)
            ("Yávië", "🍂"),      # Autumn (54 days)
            ("Quellë", "🍁"),     # Fading (54 days)
            ("Hrívë", "❄️"),      # Winter (72 days)
            ("Coirë", "🌱")       # Stirring (54 days)
        ]
        
        # Elven day names (6-day week)
        self.elven_days = [
            "Elenya",     # Stars-day
            "Anarya",     # Sun-day
            "Isilya",     # Moon-day
            "Aldúya",     # Two Trees-day
            "Menelya",    # Heavens-day
            "Valanya"     # Valar-day
        ]
        
        # Special days (outside the calendar)
        self.elven_special = {
            1: "Yestarë",        # First day (before Tuilë)
            183: "Loëndë",       # Mid-year (between Yávië and Quellë)
            368: "Mettarë"       # Last day (after Coirë)
        }
        
        # Ages of Middle-earth
        self.ages = [
            "First Age",
            "Second Age",
            "Third Age",
            "Fourth Age"
        ]
        
        # Important Elven dates/events
        self.elven_events = {
            54: "Gates of Summer",
            126: "Height of Summer",
            180: "Harvest Festival",
            234: "Autumn's End",
            306: "Midwinter",
            360: "Spring's Approach"
        }

    def calculate_time(self) -> str:
        """Calculate current Calendar of Imladris date."""
        now = datetime.now()
        
        # Calculate Elven year (loa)
        # Using Years of the Sun counting from First Age
        # For practical purposes, align with current era
        # Fourth Age began ~6000 years ago in Middle-earth time
        fourth_age_year = 6000 + (now.year - 2000)
        
        # Day of year (yen)
        day_of_year = now.timetuple().tm_yday
        
        # Check for special days
        if day_of_year == 1:
            return f"F.A. {fourth_age_year} - Yestarë (New Year) 🎊"
        elif day_of_year == 183:
            return f"F.A. {fourth_age_year} - Loëndë (Mid-year) ☀️"
        elif day_of_year >= 365:
            return f"F.A. {fourth_age_year} - Mettarë (Year's End) 🌟"
        
        # Adjust for Yestarë
        adjusted_day = day_of_year - 1
        
        # Calculate season and day within season
        if adjusted_day <= 54:
            season_index = 0  # Tuilë (Spring)
            day_in_season = adjusted_day
        elif adjusted_day <= 126:
            season_index = 1  # Lairë (Summer)
            day_in_season = adjusted_day - 54
        elif adjusted_day <= 180:
            season_index = 2  # Yávië (Autumn)
            day_in_season = adjusted_day - 126
        elif adjusted_day <= 234:
            season_index = 3  # Quellë (Fading)
            day_in_season = adjusted_day - 181  # After Loëndë
        elif adjusted_day <= 306:
            season_index = 4  # Hrívë (Winter)
            day_in_season = adjusted_day - 234
        else:
            season_index = 5  # Coirë (Stirring)
            day_in_season = adjusted_day - 306
        
        season_name, season_emoji = self.elven_seasons[season_index]
        
        # Calculate enquië (6-day week)
        week_of_season = (day_in_season - 1) // 6 + 1
        day_of_week_index = (day_in_season - 1) % 6
        elven_day = self.elven_days[day_of_week_index]
        
        # Check for events
        event = self.elven_events.get(day_of_year, "")
        event_str = f" - {event}" if event else ""
        
        # Determine time of day in Elven terms
        hour = now.hour
        if 3 <= hour < 6:
            time_name = "Tindómë (Dawn)"
            time_emoji = "🌅"
        elif 6 <= hour < 9:
            time_name = "Anarórë (Sunrise)"
            time_emoji = "🌄"
        elif 9 <= hour < 12:
            time_name = "Ára (Morning)"
            time_emoji = "🌞"
        elif 12 <= hour < 15:
            time_name = "Endë (Midday)"
            time_emoji = "☀️"
        elif 15 <= hour < 18:
            time_name = "Undómë (Afternoon)"
            time_emoji = "🌤️"
        elif 18 <= hour < 21:
            time_name = "Andúnë (Sunset)"
            time_emoji = "🌇"
        elif 21 <= hour < 24:
            time_name = "Lómë (Night)"
            time_emoji = "🌙"
        else:
            time_name = "Fui (Deep Night)"
            time_emoji = "⭐"
        
        # Format: F.A. Year, Season Day (Weekday) | Time
        # Example: "F.A. 6025, Tuilë 22 (Elenya) | 🌞 Ára - Gates of Summer"
        return f"F.A. {fourth_age_year}, {season_name} {day_in_season} ({elven_day}) | {time_emoji} {time_name}{event_str}"        