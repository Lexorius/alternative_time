"""NATO Time formats implementation."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta

from .base import AlternativeTimeSensorBase

_LOGGER = logging.getLogger(__name__)

try:
    import pytz
    HAS_PYTZ = True
except ImportError:
    HAS_PYTZ = False
    _LOGGER.warning("pytz not installed, NATO timezone detection will be limited")


class NatoTimeSensor(AlternativeTimeSensorBase):
    """Sensor for displaying NATO Time (basic format)."""

    def __init__(self, base_name: str) -> None:
        """Initialize the NATO time sensor."""
        super().__init__(base_name, "nato_time", "NATO Time")
        self._attr_icon = "mdi:clock-time-eight"
        self._update_interval = timedelta(seconds=1)

    def calculate_time(self) -> str:
        """Calculate current NATO Time.
        
        Basic NATO time format: DDHHMM
        - DD: Day of month (01-31)
        - HH: Hour (00-23)
        - MM: Minute (00-59)
        
        This is the simplest NATO time format without timezone or date information.
        Used for quick time references in military communications.
        
        Format: DDHHMM (e.g., 151430 for 15th day, 14:30)
        """
        now = datetime.now()
        return now.strftime("%d%H%M")


class NatoTimeZoneSensor(AlternativeTimeSensorBase):
    """Sensor for displaying NATO Time with Zone indicator (DTG)."""

    def __init__(self, base_name: str) -> None:
        """Initialize the NATO time zone sensor."""
        super().__init__(base_name, "nato_time_with_zone", "NATO Time with Zone")
        self._attr_icon = "mdi:earth"
        self._update_interval = timedelta(seconds=1)
        
        # NATO timezone letters mapping (UTC offset to letter)
        self.nato_zones = {
            0: 'Z',   # Zulu (UTC)
            1: 'A',   # Alpha
            2: 'B',   # Bravo
            3: 'C',   # Charlie
            4: 'D',   # Delta
            5: 'E',   # Echo
            6: 'F',   # Foxtrot
            7: 'G',   # Golf
            8: 'H',   # Hotel
            9: 'I',   # India
            10: 'K',  # Kilo (J/Juliet is skipped)
            11: 'L',  # Lima
            12: 'M',  # Mike
            -1: 'N',  # November
            -2: 'O',  # Oscar
            -3: 'P',  # Papa
            -4: 'Q',  # Quebec
            -5: 'R',  # Romeo
            -6: 'S',  # Sierra
            -7: 'T',  # Tango
            -8: 'U',  # Uniform
            -9: 'V',  # Victor
            -10: 'W', # Whiskey
            -11: 'X', # X-ray
            -12: 'Y'  # Yankee
        }

    def calculate_time(self) -> str:
        """Calculate current NATO Time with zone.
        
        Full NATO Date-Time Group (DTG) format: DDHHMM[Z] MON YY
        - DD: Day of month (01-31)
        - HH: Hour (00-23)  
        - MM: Minute (00-59)
        - Z: Timezone letter (A-Z except J)
        - MON: Month abbreviation (JAN, FEB, etc.)
        - YY: Year (last 2 digits)
        
        Timezone letters:
        - Z = Zulu (UTC)
        - A-M (except J) = UTC+1 to UTC+12
        - N-Y = UTC-1 to UTC-12
        - J is not used (avoided to prevent confusion with I)
        
        Format: DDHHMM[Z] MON YY (e.g., 151430Z JAN 25)
        """
        now = datetime.now()
        
        # Determine NATO timezone letter
        zone_letter = 'Z'  # Default to Zulu time
        
        if HAS_PYTZ:
            try:
                # Try to get local timezone offset
                local_tz = pytz.timezone('Europe/Berlin')  # Default to Berlin
                local_time = local_tz.localize(datetime.now())
                utc_offset = local_time.utcoffset().total_seconds() / 3600
                zone_letter = self.nato_zones.get(int(utc_offset), 'Z')
            except Exception:
                zone_letter = 'Z'
        
        # Format: DDHHMM[Zone] MON YY
        return now.strftime(f"%d%H%M{zone_letter} %b %y").upper()


class NatoTimeRescueSensor(AlternativeTimeSensorBase):
    """Sensor for displaying NATO Time in German rescue service format."""

    def __init__(self, base_name: str) -> None:
        """Initialize the NATO rescue time sensor."""
        super().__init__(base_name, "nato_rescue_time", "NATO Rescue Service Time")
        self._attr_icon = "mdi:ambulance"
        self._update_interval = timedelta(seconds=1)
        
        # German month abbreviations used in BOS (emergency services)
        self.german_months = {
            1: "JAN", 2: "FEB", 3: "MÄR", 4: "APR", 
            5: "MAI", 6: "JUN", 7: "JUL", 8: "AUG", 
            9: "SEP", 10: "OKT", 11: "NOV", 12: "DEZ"
        }

    def calculate_time(self) -> str:
        """Calculate current NATO Rescue Service Time.
        
        German BOS (Behörden und Organisationen mit Sicherheitsaufgaben) format:
        DD HHMM MONAT YY
        
        Differences from standard NATO DTG:
        - Space between day and time (DD HHMM instead of DDHHMM)
        - No timezone indicator (always local time)
        - German month abbreviations (MÄR, MAI, OKT, DEZ)
        
        Used by:
        - Feuerwehr (Fire Department)
        - Rettungsdienst (Emergency Medical Services)
        - THW (Federal Agency for Technical Relief)
        - Katastrophenschutz (Disaster Control)
        
        Format: DD HHMM MONTH YY (e.g., 15 1430 JAN 25)
        """
        now = datetime.now()
        
        # Get German month abbreviation
        month = self.german_months[now.month]
        
        # Format with space between day and time
        return f"{now.day:02d} {now.hour:02d}{now.minute:02d} {month} {now.year % 100:02d}"