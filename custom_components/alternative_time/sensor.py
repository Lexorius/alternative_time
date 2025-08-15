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


class MayaCalendarSensor(AlternativeTimeSensorBase):
    """Sensor for displaying Maya Calendar dates."""

    def __init__(self, base_name: str) -> None:
        """Initialize the Maya calendar sensor."""
        super().__init__(base_name, "maya", "Maya-Kalender")
        self._attr_icon = "mdi:pyramid"
        self._update_interval = timedelta(hours=1)  # Update every hour (date changes daily)
        
        # Maya calendar constants
        self.maya_epoch_jdn = 584283
        
        # Tzolk'in day names (20 days)
        self.tzolkin_days = [
            "Imix", "Ik", "Akbal", "Kan", "Chicchan",
            "Cimi", "Manik", "Lamat", "Muluc", "Oc",
            "Chuen", "Eb", "Ben", "Ix", "Men",
            "Cib", "Caban", "Etznab", "Cauac", "Ahau"
        ]
        
        # Haab month names (18 months + Wayeb)
        self.haab_months = [
            "Pop", "Wo", "Sip", "Sotz", "Tzec",
            "Xul", "Yaxkin", "Mol", "Chen", "Yax",
            "Sac", "Ceh", "Mac", "Kankin", "Muan",
            "Pax", "Kayab", "Cumku", "Wayeb"
        ]

    def calculate_time(self) -> str:
        """Calculate current Maya Calendar date."""
        # Get current Julian Day Number
        now = datetime.now()
        a = (14 - now.month) // 12
        y = now.year + 4800 - a
        m = now.month + 12 * a - 3
        
        jdn = now.day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
        
        # Calculate days since Maya epoch
        days_since_epoch = jdn - self.maya_epoch_jdn
        
        # Calculate Long Count
        baktun = days_since_epoch // 144000
        days_since_epoch %= 144000
        katun = days_since_epoch // 7200
        days_since_epoch %= 7200
        tun = days_since_epoch // 360
        days_since_epoch %= 360
        uinal = days_since_epoch // 20
        kin = days_since_epoch % 20
        
        # Calculate Tzolk'in (260-day cycle)
        tzolkin_number = ((jdn - self.maya_epoch_jdn) % 13) + 1
        tzolkin_day = self.tzolkin_days[(jdn - self.maya_epoch_jdn) % 20]
        
        # Calculate Haab (365-day cycle)
        haab_day_of_year = (jdn - self.maya_epoch_jdn + 348) % 365
        haab_month_index = min(haab_day_of_year // 20, 18)
        haab_day = haab_day_of_year % 20
        
        # Special handling for Wayeb (5-day month)
        if haab_month_index == 18:
            haab_day = haab_day_of_year - 360
        
        haab_month = self.haab_months[haab_month_index]
        
        # Format: Long Count | Tzolk'in | Haab
        return f"{baktun}.{katun}.{tun}.{uinal}.{kin} | {tzolkin_number} {tzolkin_day} | {haab_day} {haab_month}"


class NatoTimeSensor(AlternativeTimeSensorBase):
    """Sensor for displaying NATO/Military Time without zone indicator."""

    def __init__(self, base_name: str) -> None:
        """Initialize the NATO time sensor."""
        super().__init__(base_name, "nato", "NATO-Zeit")
        self._attr_icon = "mdi:clock-time-eight"
        self._update_interval = timedelta(seconds=1)  # Update every second

    def calculate_time(self) -> str:
        """Calculate current NATO/Military Date-Time Group."""
        now = datetime.now()
        # NATO DTG format: DDHHMM (day, hour, minute)
        return now.strftime("%d%H%M")


class NatoTimeZoneSensor(AlternativeTimeSensorBase):
    """Sensor for displaying NATO/Military Time with zone indicator."""

    def __init__(self, base_name: str) -> None:
        """Initialize the NATO time zone sensor."""
        super().__init__(base_name, "nato_zone", "NATO-Zeit mit Zone")
        self._attr_icon = "mdi:earth-box"
        self._update_interval = timedelta(seconds=1)  # Update every second
        
        # NATO timezone letters
        self.nato_zones = {
            0: 'Z',  # Zulu
            1: 'A',  # Alpha
            2: 'B',  # Bravo
            3: 'C',  # Charlie
            4: 'D',  # Delta
            5: 'E',  # Echo
            6: 'F',  # Foxtrot
            7: 'G',  # Golf
            8: 'H',  # Hotel
            9: 'I',  # India
            10: 'K', # Kilo (J is skipped)
            11: 'L', # Lima
            12: 'M', # Mike
            -1: 'N', # November
            -2: 'O', # Oscar
            -3: 'P', # Papa
            -4: 'Q', # Quebec
            -5: 'R', # Romeo
            -6: 'S', # Sierra
            -7: 'T', # Tango
            -8: 'U', # Uniform
            -9: 'V', # Victor
            -10: 'W', # Whiskey
            -11: 'X', # X-ray
            -12: 'Y', # Yankee
        }
        
        # NATO month abbreviations
        self.nato_months = {
            1: 'JAN', 2: 'FEB', 3: 'MAR', 4: 'APR',
            5: 'MAY', 6: 'JUN', 7: 'JUL', 8: 'AUG',
            9: 'SEP', 10: 'OCT', 11: 'NOV', 12: 'DEC'
        }

    def calculate_time(self) -> str:
        """Calculate current NATO/Military Date-Time Group with zone indicator."""
        import time
        
        # Get local time and UTC offset
        now = datetime.now()
        
        # Calculate UTC offset in hours
        if time.daylight and time.localtime().tm_isdst:
            utc_offset_seconds = -time.altzone
        else:
            utc_offset_seconds = -time.timezone
        
        utc_offset_hours = int(utc_offset_seconds / 3600)
        
        # Get NATO zone letter
        zone_letter = self.nato_zones.get(utc_offset_hours, 'J')  # J for local/unknown
        
        # Get month abbreviation
        month_abbr = self.nato_months[now.month]
        
        # Full NATO DTG format: DDHHMM[Zone] MON YY
        return f"{now.strftime('%d%H%M')}{zone_letter} {month_abbr} {now.strftime('%y')}"


class NatoTimeRescueSensor(AlternativeTimeSensorBase):
    """Sensor for displaying NATO/Military Time as used by German rescue services."""

    def __init__(self, base_name: str) -> None:
        """Initialize the NATO rescue time sensor."""
        super().__init__(base_name, "nato_rescue", "NATO-Zeit Rettungsdienst")
        self._attr_icon = "mdi:ambulance"
        self._update_interval = timedelta(seconds=1)  # Update every second
        
        # German month abbreviations as used in rescue services
        self.rescue_months = {
            1: 'JAN', 2: 'FEB', 3: 'MÄR', 4: 'APR',
            5: 'MAI', 6: 'JUN', 7: 'JUL', 8: 'AUG',
            9: 'SEP', 10: 'OKT', 11: 'NOV', 12: 'DEZ'
        }

    def calculate_time(self) -> str:
        """Calculate current NATO Time for rescue services (without zone indicator)."""
        now = datetime.now()
        
        # Get month abbreviation
        month_abbr = self.rescue_months[now.month]
        
        # German rescue service format: DD HHMM MONAT YY
        return f"{now.strftime('%d %H%M')} {month_abbr} {now.strftime('%y')}"


class AtticCalendarSensor(AlternativeTimeSensorBase):
    """Sensor for displaying the ancient Attic (Athenian) calendar."""

    def __init__(self, base_name: str) -> None:
        """Initialize the Attic calendar sensor."""
        super().__init__(base_name, "attic", "Attischer Kalender")
        self._attr_icon = "mdi:pillar"
        self._update_interval = timedelta(hours=1)  # Update every hour
        
        # Attic months (beginning with summer solstice)
        self.attic_months = [
            "Hekatombaion",  # July/August
            "Metageitnion",  # August/September
            "Boedromion",    # September/October
            "Pyanepsion",    # October/November
            "Maimakterion",  # November/December
            "Poseideon",     # December/January
            "Gamelion",      # January/February
            "Anthesterion",  # February/March
            "Elaphebolion",  # March/April
            "Mounichion",    # April/May
            "Thargelion",    # May/June
            "Skirophorion"   # June/July
        ]
        
        self.archon_names = [
            "Nikias", "Kallias", "Eukleides", "Aristion", "Alexias",
            "Theophilos", "Lysandros", "Demokrates", "Philippos", "Sostrates"
        ]
        
        self.prytanies = [
            "Erechtheis", "Aigeis", "Pandionis", "Leontis", "Akamantis",
            "Oineis", "Kekropis", "Hippothontis", "Aiantis", "Antiochis"
        ]

    def calculate_time(self) -> str:
        """Calculate current Attic calendar date."""
        now = datetime.now()
        
        # Calculate days since summer solstice (approximately June 21)
        current_year = now.year
        summer_solstice = datetime(current_year, 6, 21)
        
        if now < summer_solstice:
            summer_solstice = datetime(current_year - 1, 6, 21)
            attic_year = current_year - 1
        else:
            attic_year = current_year
        
        days_since_solstice = (now - summer_solstice).days
        
        # Attic calendar had 12 months of 29-30 days (alternating)
        month_lengths = [30, 29, 30, 29, 30, 29, 30, 29, 30, 29, 30, 29]
        
        # Find current month and day
        current_month_index = 0
        days_remaining = days_since_solstice
        
        for i, month_length in enumerate(month_lengths):
            if days_remaining < month_length:
                current_month_index = i
                break
            days_remaining -= month_length
        else:
            current_month_index = 11
            days_remaining = min(days_remaining, 29)
        
        attic_month = self.attic_months[current_month_index]
        attic_day = days_remaining + 1
        
        # Determine the period of the month (dekad system)
        if attic_day <= 10:
            period = "ἱσταμένου"  # histamenou (waxing)
            day_in_period = attic_day
        elif attic_day <= 20:
            period = "μεσοῦντος"  # mesountos (middle)
            day_in_period = attic_day - 10
        else:
            period = "φθίνοντος"  # phthinontos (waning)
            month_length = month_lengths[current_month_index]
            day_in_period = month_length - attic_day + 1
        
        # Calculate Olympiad
        years_since_776_bce = attic_year + 776
        olympiad = years_since_776_bce // 4 + 1
        olympiad_year = (years_since_776_bce % 4) + 1
        
        # Get archon name
        archon = self.archon_names[attic_year % len(self.archon_names)]
        
        # Format: Day Period Month | Archon | Olympiad
        return f"{day_in_period} {period} {attic_month} | {archon} | Ol.{olympiad}.{olympiad_year}"


class SuriyakatiCalendarSensor(AlternativeTimeSensorBase):
    """Sensor for displaying Thai Solar Calendar (Suriyakati)."""

    def __init__(self, base_name: str) -> None:
        """Initialize the Suriyakati calendar sensor."""
        super().__init__(base_name, "suriyakati", "Suriyakati-Kalender")
        self._attr_icon = "mdi:temple-buddhist"
        self._update_interval = timedelta(hours=1)  # Update every hour
        
        # Thai months
        self.thai_months = [
            "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน",
            "พฤษภาคม", "มิถุนายน", "กรกฎาคม", "สิงหาคม",
            "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"
        ]
        
        # Thai numerals
        self.thai_numerals = ['๐', '๑', '๒', '๓', '๔', '๕', '๖', '๗', '๘', '๙']

    def to_thai_numerals(self, number: int) -> str:
        """Convert number to Thai numerals."""
        return ''.join(self.thai_numerals[int(d)] for d in str(number))

    def calculate_time(self) -> str:
        """Calculate current Thai Solar Calendar date."""
        now = datetime.now()
        
        # Buddhist Era (BE) = CE + 543
        buddhist_year = now.year + 543
        
        # Get Thai month
        thai_month = self.thai_months[now.month - 1]
        
        # Convert day and year to Thai numerals
        thai_day = self.to_thai_numerals(now.day)
        thai_year = self.to_thai_numerals(buddhist_year)
        
        # Romanized month names
        romanized_month = [
            "Makarakhom", "Kumphaphan", "Minakhom", "Mesayon",
            "Phruetsaphakhom", "Mithunayon", "Karakadakhom", "Singhakhom",
            "Kanyayon", "Tulakhom", "Phruetsachikayon", "Thanwakhom"
        ][now.month - 1]
        
        # Format: Thai format and romanized
        return f"{thai_day} {thai_month} {thai_year} | {now.day} {romanized_month} {buddhist_year} BE"


class MinguoCalendarSensor(AlternativeTimeSensorBase):
    """Sensor for displaying Republic of China (Taiwan) Calendar."""

    def __init__(self, base_name: str) -> None:
        """Initialize the Minguo calendar sensor."""
        super().__init__(base_name, "minguo", "Minguo-Kalender")
        self._attr_icon = "mdi:flag-variant"
        self._update_interval = timedelta(hours=1)  # Update every hour
        
        # Traditional Chinese months
        self.chinese_months = [
            "一月", "二月", "三月", "四月",
            "五月", "六月", "七月", "八月",
            "九月", "十月", "十一月", "十二月"
        ]
        
        # Traditional Chinese numbers for day
        self.chinese_numbers = [
            "零", "一", "二", "三", "四", "五",
            "六", "七", "八", "九", "十"
        ]

    def to_chinese_day(self, day: int) -> str:
        """Convert day to traditional Chinese."""
        if day <= 10:
            if day == 10:
                return "十"
            return self.chinese_numbers[day]
        elif day < 20:
            return "十" + self.chinese_numbers[day - 10]
        elif day == 20:
            return "二十"
        elif day < 30:
            return "二十" + self.chinese_numbers[day - 20]
        elif day == 30:
            return "三十"
        else:
            return "三十" + self.chinese_numbers[day - 30]

    def calculate_time(self) -> str:
        """Calculate current Minguo (ROC) Calendar date."""
        now = datetime.now()
        
        # Minguo Era starts from 1912
        minguo_year = now.year - 1911
        
        # Handle years before 1912
        if minguo_year < 1:
            years_before = abs(minguo_year) + 1
            year_display = f"民前{years_before}年"
            year_display_roman = f"Before Minguo {years_before}"
        else:
            year_display = f"民國{minguo_year}年"
            year_display_roman = f"Minguo {minguo_year}"
        
        # Get Chinese month and day
        chinese_month = self.chinese_months[now.month - 1]
        chinese_day = self.to_chinese_day(now.day)
        
        # Format: Traditional Chinese and romanized
        return f"{year_display} {chinese_month} {chinese_day}日 | {year_display_roman}/{now.month}/{now.day}"


class DarianCalendarSensor(AlternativeTimeSensorBase):
    """Sensor for displaying Darian Calendar (Mars calendar)."""

    def __init__(self, base_name: str) -> None:
        """Initialize the Darian calendar sensor."""
        super().__init__(base_name, "darian", "Darischer Kalender")
        self._attr_icon = "mdi:rocket-launch"
        self._update_interval = timedelta(hours=1)  # Update every hour
        
        # Darian months (24 months, 27-28 sols each)
        self.darian_months = [
            "Sagittarius", "Dhanus",      # 1-2
            "Capricornus", "Makara",      # 3-4
            "Aquarius", "Kumbha",         # 5-6
            "Pisces", "Mina",             # 7-8
            "Aries", "Mesha",             # 9-10
            "Taurus", "Rishabha",         # 11-12
            "Gemini", "Mithuna",          # 13-14
            "Cancer", "Karka",            # 15-16
            "Leo", "Simha",               # 17-18
            "Virgo", "Kanya",             # 19-20
            "Libra", "Tula",              # 21-22
            "Scorpius", "Vrishchika"      # 23-24
        ]
        
        # Sol names (7-sol week)
        self.sol_names = [
            "Sol Solis",    # Sunday equivalent
            "Sol Lunae",    # Monday
            "Sol Martis",   # Tuesday  
            "Sol Mercurii", # Wednesday
            "Sol Jovis",    # Thursday
            "Sol Veneris",  # Friday
            "Sol Saturni"   # Saturday
        ]
        
        # Month lengths: odd months have 28 sols, even have 27 (except leap years)
        self.month_lengths = [28, 27] * 12  # Pattern for 24 months

    def calculate_time(self) -> str:
        """Calculate current Darian (Mars) Calendar date."""
        # Mars Sol = 24h 39m 35.244s = 88775.244 seconds
        # Mars Year = 668.5907 sols ≈ 687 Earth days
        
        # Epoch: March 1, 1609 (Telescopic epoch - Galileo's observations)
        # For simplicity, we'll use a more recent epoch
        # Darian Epoch = January 1, 1970 00:00:00 UTC = Darian Year 184
        
        now = datetime.now()
        
        # Calculate days since Unix epoch
        unix_epoch = datetime(1970, 1, 1)
        days_since_epoch = (now - unix_epoch).days
        
        # Convert Earth days to Mars sols
        # 1 sol = 1.02749125 Earth days
        sols_since_epoch = days_since_epoch / 1.02749125
        
        # Mars year length in sols
        mars_year_sols = 668.5907
        
        # Calculate Darian year (starting from year 184)
        base_year = 184
        years_passed = int(sols_since_epoch / mars_year_sols)
        darian_year = base_year + years_passed
        
        # Calculate sol of year
        sol_of_year = int(sols_since_epoch % mars_year_sols)
        
        # Determine month and sol of month
        current_month_index = 0
        sols_remaining = sol_of_year
        
        for i in range(24):
            # Check for leap year (simplified - every 2nd year for demonstration)
            # Real Darian leap years are more complex
            is_leap = (darian_year % 2 == 0) and (i == 23)
            month_length = 28 if i % 2 == 0 else (27 if not is_leap else 28)
            
            if sols_remaining < month_length:
                current_month_index = i
                break
            sols_remaining -= month_length
        
        darian_month = self.darian_months[current_month_index]
        darian_sol = sols_remaining + 1  # 1-indexed
        
        # Calculate sol of week
        total_sols = int(sols_since_epoch)
        sol_of_week_index = total_sols % 7
        sol_of_week = self.sol_names[sol_of_week_index]
        
        # Determine season (6 months each)
        if current_month_index < 6:
            season = "Vernal"  # Spring
        elif current_month_index < 12:
            season = "Summer"
        elif current_month_index < 18:
            season = "Autumnal"
        else:
            season = "Winter"
        
        # Format: Sol Month Year | Sol-of-week | Season
        # Example: "15 Gemini 217 | Sol Martis | Summer"
        return f"{darian_sol} {darian_month} {darian_year} | {sol_of_week} | {season}"


class MarsTimeSensor(AlternativeTimeSensorBase):
    """Sensor for displaying Mars Sol Time in selected timezone."""

    def __init__(self, base_name: str, mars_timezone: str) -> None:
        """Initialize the Mars time sensor."""
        super().__init__(base_name, "mars_time", "Mars-Zeit")
        self._mars_timezone = mars_timezone
        self._attr_icon = "mdi:planet-outline"
        self._update_interval = timedelta(seconds=30)  # Update every 30 seconds
        
        # Extract timezone offset from string (e.g., "MTC+3 (Location)" -> 3)
        import re
        match = re.search(r'MTC([+-]\d+)', mars_timezone)
        self._timezone_offset = int(match.group(1)) if match else 0
        
        # Extract location name
        match_loc = re.search(r'\((.*?)\)', mars_timezone)
        self._location_name = match_loc.group(1) if match_loc else "Airy-0"

    def calculate_time(self) -> str:
        """Calculate current Mars Sol Time for selected timezone."""
        now = datetime.now()
        
        # Mars Sol = 24h 39m 35.244s = 88775.244 seconds
        # One Mars solar day is 1.02749125 Earth days
        sol_duration_seconds = 88775.244
        
        # Calculate Mission Sol Time (MST) - starts at midnight UTC Jan 6, 2000
        # This is approximately when Mars Global Surveyor began mapping
        epoch = datetime(2000, 1, 6, 0, 0, 0)
        
        # Calculate elapsed time since epoch
        elapsed = now - epoch
        elapsed_seconds = elapsed.total_seconds()
        
        # Convert to Mars sols
        total_sols = elapsed_seconds / sol_duration_seconds
        
        # Apply timezone offset (Mars has 24 time zones, each 15° or 1 hour)
        # Mars rotates 14.62 degrees per hour (360° / 24.6229 hours)
        adjusted_sols = total_sols + (self._timezone_offset / 24.0)
        
        # Get current sol number (day count)
        sol_number = int(adjusted_sols)
        
        # Get time of sol (fractional part)
        sol_fraction = adjusted_sols - sol_number
        if sol_fraction < 0:
            sol_fraction += 1
            sol_number -= 1
        
        # Convert to Mars hours, minutes, seconds
        # Mars uses 24-hour clock like Earth
        mars_seconds_of_sol = sol_fraction * sol_duration_seconds
        
        mars_hours = int(mars_seconds_of_sol // 3699)  # 88775.244 / 24 = 3699 seconds per Mars hour
        remaining_seconds = mars_seconds_of_sol % 3699
        
        mars_minutes = int(remaining_seconds // 61.65)  # 3699 / 60 = 61.65 seconds per Mars minute
        mars_seconds = int(remaining_seconds % 61.65)
        
        # Ensure values are in valid range
        mars_hours = mars_hours % 24
        mars_minutes = mars_minutes % 60
        mars_seconds = mars_seconds % 60
        
        # Determine if it's day or night (simple approximation)
        # Sol rises at ~6:00, sets at ~18:00
        if 6 <= mars_hours < 18:
            period = "☉ Tag"  # Day
        else:
            period = "☽ Nacht"  # Night
        
        # Calculate Mars year (for reference)
        # Mars year = 668.5907 sols
        mars_year = int(total_sols / 668.5907) + 1
        sol_of_year = int(total_sols % 668.5907) + 1
        
        # Format: HH:MM:SS Location | Sol X of Year Y | Day/Night
        return f"{mars_hours:02d}:{mars_minutes:02d}:{mars_seconds:02d} {self._location_name} | Sol {sol_of_year}/MY{mars_year} | {period}"        