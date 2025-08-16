# Calendar Implementations

This directory contains all individual calendar and time system implementations for the Alternative Time Systems integration.

## Structure

Each calendar system is implemented in its own Python file, inheriting from the `AlternativeTimeSensorBase` class defined in `base.py`.

## File Organization

### Base Class
- `base.py` - Base sensor class that all calendars inherit from
- `__init__.py` - Package initialization

### Science Fiction
- `stardate.py` - Star Trek Stardate
- `eve.py` - EVE Online Time (New Eden Standard Time)

### Internet/Technical
- `swatch.py` - Swatch Internet Time
- `unix.py` - Unix Timestamp
- `julian.py` - Julian Date
- `decimal.py` - Decimal Time (French Revolutionary)
- `hexadecimal.py` - Hexadecimal Time
- `timezone.py` - Standard Earth Timezones

### Historical Calendars
- `maya.py` - Maya Calendar (Long Count, Tzolk'in, Haab)
- `attic.py` - Attic Calendar (Ancient Athens)
- `egyptian.py` - Ancient Egyptian Calendar

### Military Time
- `nato.py` - NATO Time formats (Basic, DTG, Rescue Service)

### Cultural Calendars
- `suriyakati.py` - Thai Calendar (Buddhist Era)
- `minguo.py` - Taiwan/ROC Calendar

### Mars Calendars
- `darian.py` - Darian Mars Calendar
- `mars.py` - Mars Time with Timezones

### Fantasy Calendars
- `shire.py` - Tolkien's Shire Reckoning (Hobbits)
- `rivendell.py` - Calendar of Imladris (Elves)
- `tamriel.py` - Elder Scrolls Tamriel Calendar
- `discworld.py` - Terry Pratchett's Discworld Calendar

## Adding a New Calendar

To add a new calendar system:

1. Create a new Python file in this directory (e.g., `my_calendar.py`)

2. Import the base class:
```python
from .base import AlternativeTimeSensorBase
```

3. Create your sensor class:
```python
class MyCalendarSensor(AlternativeTimeSensorBase):
    def __init__(self, base_name: str) -> None:
        super().__init__(base_name, "my_calendar", "My Calendar")
        self._attr_icon = "mdi:calendar"
        self._update_interval = timedelta(hours=1)
    
    def calculate_time(self) -> str:
        # Your calendar calculation logic here
        return "formatted_time_string"
```

4. Add the import to `sensor.py`:
```python
from .calendars.my_calendar import MyCalendarSensor
```

5. Add configuration constant to `const.py`:
```python
CONF_ENABLE_MY_CALENDAR = "enable_my_calendar"
```

6. Update `config_flow.py` and translation files

## Update Intervals

Choose appropriate update intervals based on the precision needed:
- **1 second**: For clocks showing seconds (Unix, Swatch, timezone)
- **5 seconds**: For moderate precision (Hexadecimal)
- **10 seconds**: For slow-changing values (Stardate)
- **30 seconds**: For Mars time
- **60 seconds**: For very slow changes (Julian Date)
- **1 hour**: For daily calendars (Maya, Egyptian, Fantasy calendars)

## Icons

Use appropriate Material Design Icons:
- Calendars: `mdi:calendar`, `mdi:calendar-text`
- Clocks: `mdi:clock`, `mdi:clock-digital`
- Space: `mdi:rocket`, `mdi:planet`, `mdi:star`
- Fantasy: `mdi:sword-cross`, `mdi:leaf`, `mdi:pipe`
- Historical: `mdi:pyramid`, `mdi:pillar`

## Testing

Each calendar should handle:
- Edge cases (leap years, month boundaries)
- Timezone considerations where applicable
- Performance (avoid heavy calculations in frequent updates)
- Error handling for invalid inputs