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


class MayaCalendarSensor(AlternativeTimeSensorBase):
    """Sensor for displaying Maya Calendar."""

    def __init__(self, base_name: str) -> None:
        """Initialize the Maya calendar sensor."""
        super().__init__(base_name, "maya_calendar", "Maya-Kalender")
        self._attr_icon = "mdi:pyramid"
        self._update_interval = timedelta(hours=1)  # Update every hour

    def calculate_time(self) -> str:
        """Calculate current Maya Calendar date."""
        # Maya Long Count calculation
        # Correlation constant: August 11, 3114 BCE (Gregorian)
        maya_epoch = datetime(year=-3113, month=8, day=11)  # Note: Python doesn't support BCE directly
        
        # Use a simplified calculation for demonstration
        # The actual Maya calendar is complex with multiple cycles
        now = datetime.now()
        
        # Calculate days since a more recent epoch for simplicity
        # Using December 21, 2012 as reference (13.0.0.0.0 in Maya)
        reference_date = datetime(2012, 12, 21)
        days_since_reference = (now - reference_date).days
        
        # Maya calendar units
        kin = days_since_reference % 20
        uinal = (days_since_reference // 20) % 18
        tun = (days_since_reference // 360) % 20
        katun = (days_since_reference // 7200) % 20
        baktun = 13 + (days_since_reference // 144000)
        
        # Tzolk'in (260-day cycle)
        tzolkin_day_number = ((days_since_reference + 4) % 13) + 1
        tzolkin_day_names = ["Imix", "Ik", "Akbal", "Kan", "Chicchan", "Cimi", "Manik", 
                            "Lamat", "Muluc", "Oc", "Chuen", "Eb", "Ben", "Ix", "Men", 
                            "Cib", "Caban", "Etznab", "Cauac", "Ahau"]
        tzolkin_day_name = tzolkin_day_names[days_since_reference % 20]
        
        # Haab (365-day cycle)
        haab_months = ["Pop", "Uo", "Zip", "Zotz", "Tzec", "Xul", "Yaxkin", "Mol", 
                      "Chen", "Yax", "Zac", "Ceh", "Mac", "Kankin", "Muan", "Pax", 
                      "Kayab", "Cumku", "Uayeb"]
        haab_day = days_since_reference % 365
        haab_month_index = min(haab_day // 20, 18)
        haab_day_of_month = (haab_day % 20)
        haab_month = haab_months[haab_month_index]
        
        return f"{baktun}.{katun}.{tun}.{uinal}.{kin} | {tzolkin_day_number} {tzolkin_day_name} | {haab_day_of_month} {haab_month}"


class NatoTimeSensor(AlternativeTimeSensorBase):
    """Sensor for displaying NATO Time (basic format)."""

    def __init__(self, base_name: str) -> None:
        """Initialize the NATO time sensor."""
        super().__init__(base_name, "nato_time", "NATO-Zeit")
        self._attr_icon = "mdi:clock-time-eight"
        self._update_interval = timedelta(seconds=1)

    def calculate_time(self) -> str:
        """Calculate current NATO Time."""
        now = datetime.now()
        return now.strftime("%d%H%M")


class NatoTimeZoneSensor(AlternativeTimeSensorBase):
    """Sensor for displaying NATO Time with Zone indicator."""

    def __init__(self, base_name: str) -> None:
        """Initialize the NATO time zone sensor."""
        super().__init__(base_name, "nato_time_with_zone", "NATO-Zeit mit Zone")
        self._attr_icon = "mdi:earth"
        self._update_interval = timedelta(seconds=1)

    def calculate_time(self) -> str:
        """Calculate current NATO Time with zone."""
        now = datetime.now()
        
        # Determine NATO time zone letter
        # This is simplified - actual implementation would need proper timezone handling
        if HAS_PYTZ:
            try:
                local_tz = pytz.timezone('Europe/Berlin')
                local_time = local_tz.localize(datetime.now())
                utc_offset = local_time.utcoffset().total_seconds() / 3600
                
                # Map UTC offset to NATO letter
                nato_zones = {
                    0: 'Z', 1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'E',
                    6: 'F', 7: 'G', 8: 'H', 9: 'I', 10: 'K', 11: 'L',
                    12: 'M', -1: 'N', -2: 'O', -3: 'P', -4: 'Q', -5: 'R',
                    -6: 'S', -7: 'T', -8: 'U', -9: 'V', -10: 'W', -11: 'X', -12: 'Y'
                }
                zone_letter = nato_zones.get(int(utc_offset), 'Z')
            except:
                zone_letter = 'Z'  # Default to Zulu time
        else:
            zone_letter = 'Z'
        
        return now.strftime(f"%d%H%M{zone_letter} %b %y").upper()


class NatoTimeRescueSensor(AlternativeTimeSensorBase):
    """Sensor for displaying NATO Time in German rescue service format."""

    def __init__(self, base_name: str) -> None:
        """Initialize the NATO rescue time sensor."""
        super().__init__(base_name, "nato_rescue_time", "NATO-Zeit Rettungsdienst")
        self._attr_icon = "mdi:ambulance"
        self._update_interval = timedelta(seconds=1)

    def calculate_time(self) -> str:
        """Calculate current NATO Rescue Service Time."""
        now = datetime.now()
        
        # German month abbreviations
        german_months = {
            1: "JAN", 2: "FEB", 3: "MÄR", 4: "APR", 5: "MAI", 6: "JUN",
            7: "JUL", 8: "AUG", 9: "SEP", 10: "OKT", 11: "NOV", 12: "DEZ"
        }
        
        month = german_months[now.month]
        return f"{now.day:02d} {now.hour:02d}{now.minute:02d} {month} {now.year % 100:02d}"


class AtticCalendarSensor(AlternativeTimeSensorBase):
    """Sensor for displaying Attic Calendar (Ancient Athens)."""

    def __init__(self, base_name: str) -> None:
        """Initialize the Attic calendar sensor."""
        super().__init__(base_name, "attic_calendar", "Attischer Kalender")
        self._attr_icon = "mdi:pillar"
        self._update_interval = timedelta(hours=1)

    def calculate_time(self) -> str:
        """Calculate current Attic Calendar date."""
        now = datetime.now()
        
        # Attic months
        months = [
            "Hekatombaion", "Metageitnion", "Boedromion", "Pyanepsion",
            "Maimakterion", "Poseideon", "Gamelion", "Anthesterion",
            "Elaphebolion", "Mounichion", "Thargelion", "Skirophorion"
        ]
        
        # Simplified calculation - actual Attic calendar was lunisolar
        days_since_summer_solstice = (now.timetuple().tm_yday - 172) % 365
        month_index = min(days_since_summer_solstice // 30, 11)
        day_of_month = (days_since_summer_solstice % 30) + 1
        
        # Dekad (10-day period)
        if day_of_month <= 10:
            period = "ἱσταμένου"  # waxing
        elif day_of_month <= 20:
            period = "μεσοῦντος"  # middle
        else:
            period = "φθίνοντος"  # waning
            day_of_month = 31 - day_of_month  # Count backwards in waning period
        
        # Archon (simplified - would rotate yearly)
        archons = ["Nikias", "Kallias", "Kritias", "Alkibiades", "Kleisthenes"]
        archon = archons[now.year % len(archons)]
        
        # Olympiad calculation
        olympiad_year = ((now.year + 776) // 4)
        olympiad_cycle = ((now.year + 776) % 4) + 1
        
        return f"{day_of_month} {period} {months[month_index]} | {archon} | Ol.{olympiad_year}.{olympiad_cycle}"


class SuriyakatiCalendarSensor(AlternativeTimeSensorBase):
    """Sensor for displaying Suriyakati Calendar (Thai)."""

    def __init__(self, base_name: str) -> None:
        """Initialize the Suriyakati calendar sensor."""
        super().__init__(base_name, "suriyakati_calendar", "Suriyakati-Kalender")
        self._attr_icon = "mdi:buddhism"
        self._update_interval = timedelta(hours=1)

    def calculate_time(self) -> str:
        """Calculate current Suriyakati Calendar date."""
        now = datetime.now()
        
        # Buddhist Era = CE + 543
        buddhist_year = now.year + 543
        
        # Thai month names
        thai_months = {
            1: "มกราคม", 2: "กุมภาพันธ์", 3: "มีนาคม", 4: "เมษายน",
            5: "พฤษภาคม", 6: "มิถุนายน", 7: "กรกฎาคม", 8: "สิงหาคม",
            9: "กันยายน", 10: "ตุลาคม", 11: "พฤศจิกายน", 12: "ธันวาคม"
        }
        
        # Thai numerals
        thai_digits = "๐๑๒๓๔๕๖๗๘๙"
        
        def to_thai_number(n):
            return ''.join(thai_digits[int(d)] for d in str(n))
        
        thai_day = to_thai_number(now.day)
        thai_year = to_thai_number(buddhist_year)
        thai_month = thai_months[now.month]
        
        # Romanized version
        roman_months = {
            1: "Makarakhom", 2: "Kumphaphan", 3: "Minakhom", 4: "Mesayon",
            5: "Phruetsaphakhom", 6: "Mithunayon", 7: "Karakadakhom", 8: "Singhakhom",
            9: "Kanyayon", 10: "Tulakhom", 11: "Phruetsachikayon", 12: "Thanwakhom"
        }
        
        return f"{thai_day} {thai_month} {thai_year} | {now.day} {roman_months[now.month]} {buddhist_year} BE"


class MinguoCalendarSensor(AlternativeTimeSensorBase):
    """Sensor for displaying Minguo Calendar (Taiwan/ROC)."""

    def __init__(self, base_name: str) -> None:
        """Initialize the Minguo calendar sensor."""
        super().__init__(base_name, "minguo_calendar", "Minguo-Kalender")
        self._attr_icon = "mdi:calendar-text"
        self._update_interval = timedelta(hours=1)

    def calculate_time(self) -> str:
        """Calculate current Minguo Calendar date."""
        now = datetime.now()
        
        # Minguo year = CE - 1911 (Year 1 = 1912 CE)
        minguo_year = now.year - 1911
        
        # Chinese month names
        chinese_months = {
            1: "一月", 2: "二月", 3: "三月", 4: "四月",
            5: "五月", 6: "六月", 7: "七月", 8: "八月",
            9: "九月", 10: "十月", 11: "十一月", 12: "十二月"
        }
        
        # Chinese number conversion for day
        chinese_numbers = ["", "一", "二", "三", "四", "五", "六", "七", "八", "九", "十"]
        
        def to_chinese_day(day):
            if day <= 10:
                return chinese_numbers[day] + "日"
            elif day < 20:
                return "十" + chinese_numbers[day - 10] + "日"
            elif day == 20:
                return "二十日"
            elif day < 30:
                return "二十" + chinese_numbers[day - 20] + "日"
            elif day == 30:
                return "三十日"
            else:
                return "三十一日"
        
        chinese_date = f"民國{minguo_year}年 {chinese_months[now.month]} {to_chinese_day(now.day)}"
        roman_date = f"Minguo {minguo_year}/{now.month:02d}/{now.day:02d}"
        
        return f"{chinese_date} | {roman_date}"


class DarianCalendarSensor(AlternativeTimeSensorBase):
    """Sensor for displaying Darian Calendar (Mars)."""

    def __init__(self, base_name: str) -> None:
        """Initialize the Darian calendar sensor."""
        super().__init__(base_name, "darian_calendar", "Darischer Kalender")
        self._attr_icon = "mdi:rocket"
        self._update_interval = timedelta(hours=1)

    def calculate_time(self) -> str:
        """Calculate current Darian Calendar date."""
        # Mars calendar calculation
        # Reference: March 1, 1609 = Darian Year 0, Sol 1
        
        now = datetime.now()
        reference_date = datetime(1609, 3, 1)
        days_since_reference = (now - reference_date).days
        
        # Mars sol = 24h 39m 35s = 88775 seconds
        # Mars year = 668.6 sols ≈ 687 Earth days
        sols_since_reference = days_since_reference * 86400 / 88775
        
        mars_year = int(sols_since_reference / 668.6)
        sol_of_year = int(sols_since_reference % 668.6) + 1
        
        # Darian months (24 months, alternating 27-28 sols)
        months = [
            "Sagittarius", "Dhanus", "Capricornus", "Makara",
            "Aquarius", "Kumbha", "Pisces", "Mina",
            "Aries", "Mesha", "Taurus", "Rishabha",
            "Gemini", "Mithuna", "Cancer", "Karka",
            "Leo", "Simha", "Virgo", "Kanya",
            "Libra", "Tula", "Scorpius", "Vrishchika"
        ]
        
        # Calculate month and sol
        month_index = 0
        sols_counted = 0
        for i in range(24):
            month_sols = 28 if i % 6 == 5 else 27  # Every 6th month has 28 sols
            if sols_counted + month_sols >= sol_of_year:
                month_index = i
                sol_of_month = sol_of_year - sols_counted
                break
            sols_counted += month_sols
        
        # Week day (7-sol week)
        weekdays = ["Sol Solis", "Sol Lunae", "Sol Martis", "Sol Mercurii", 
                   "Sol Jovis", "Sol Veneris", "Sol Saturni"]
        weekday = weekdays[int(sols_since_reference) % 7]
        
        # Season
        if month_index < 6:
            season = "Spring"
        elif month_index < 12:
            season = "Summer"
        elif month_index < 18:
            season = "Autumn"
        else:
            season = "Winter"
        
        return f"Sol {sol_of_month} {months[month_index]} {mars_year} | {weekday} | {season}"


class MarsTimeSensor(AlternativeTimeSensorBase):
    """Sensor for displaying Mars Time with timezone."""

    def __init__(self, base_name: str, mars_timezone: str) -> None:
        """Initialize the Mars time sensor."""
        super().__init__(base_name, "mars_time", "Mars-Zeit")
        self._attr_icon = "mdi:planet"
        self._mars_timezone = mars_timezone
        self._update_interval = timedelta(seconds=30)

    def calculate_time(self) -> str:
        """Calculate current Mars Time."""
        now = datetime.now()
        
        # Extract timezone offset from string (e.g., "MTC+0 (Airy-0)" -> 0)
        import re
        match = re.search(r'MTC([+-]\d+)', self._mars_timezone)
        if match:
            offset = int(match.group(1))
        else:
            offset = 0
        
        # Extract location name
        location_match = re.search(r'\((.*?)\)', self._mars_timezone)
        location = location_match.group(1) if location_match else "Airy-0"
        
        # Mars sol duration in seconds
        sol_duration = 88775.244
        
        # Calculate Mars Sol Date (MSD)
        # Epoch: December 29, 1873 (MSD 0)
        epoch = datetime(1873, 12, 29, 0, 0, 0)
        seconds_since_epoch = (now - epoch).total_seconds()
        msd = seconds_since_epoch / sol_duration
        
        # Current sol of Mars Year
        # Mars Year 1 began April 11, 1955
        mars_year_epoch = datetime(1955, 4, 11)
        seconds_since_mars_epoch = (now - mars_year_epoch).total_seconds()
        sols_since_mars_epoch = seconds_since_mars_epoch / sol_duration
        
        mars_year = int(sols_since_mars_epoch / 668.6) + 1
        sol_of_year = int(sols_since_mars_epoch % 668.6) + 1
        
        # Calculate Mars time of day
        sol_fraction = msd % 1
        # Adjust for timezone
        sol_fraction = (sol_fraction + offset / 24) % 1
        
        mars_hours = int(sol_fraction * 24)
        mars_minutes = int((sol_fraction * 24 * 60) % 60)
        mars_seconds = int((sol_fraction * 24 * 3600) % 60)
        
        # Day/Night indicator
        if 6 <= mars_hours < 18:
            day_night = "☉ Tag"
        else:
            day_night = "☽ Nacht"
        
        return f"{mars_hours:02d}:{mars_minutes:02d}:{mars_seconds:02d} {location} | Sol {sol_of_year}/MY{mars_year} | {day_night}"


class EveOnlineTimeSensor(AlternativeTimeSensorBase):
    """Sensor for displaying EVE Online Time (New Eden Standard Time)."""

    def __init__(self, base_name: str) -> None:
        """Initialize the EVE Online time sensor."""
        super().__init__(base_name, "eve_online", "EVE Online Zeit")
        self._attr_icon = "mdi:space-station"
        self._update_interval = timedelta(seconds=1)

    def calculate_time(self) -> str:
        """Calculate current EVE Online Time."""
        # EVE Online uses UTC and has its own calendar
        # YC (Yoiul Conference) year starts from YC 0 = 23236 AD
        # For gameplay purposes, YC 105 = 2003 (EVE launch year)
        
        now = datetime.utcnow()  # EVE uses UTC
        
        # Calculate YC year (starts from 2003 = YC 105)
        eve_year = 105 + (now.year - 2003)
        
        # EVE uses standard Earth months and days
        # Format: YC XXX.MM.DD HH:MM:SS
        
        return f"YC {eve_year}.{now.month:02d}.{now.day:02d} {now.hour:02d}:{now.minute:02d}:{now.second:02d}"


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