# Alternative Time Systems - Calendar Format Documentation

## Overview
This document describes the standardized format for implementing alternative calendar systems in the Home Assistant Alternative Time Systems integration. All calendar implementations must follow this structure to ensure consistency and compatibility.

## File Structure
Each calendar implementation consists of a Python file in the `calendars/` directory with the following components:

```python
"""Calendar Name implementation - Version 2.5."""
from __future__ import annotations
from datetime import datetime
import logging
from typing import Dict, Any

from homeassistant.core import HomeAssistant
from ..sensor import AlternativeTimeSensorBase

_LOGGER = logging.getLogger(__name__)

# Calendar metadata (CALENDAR_INFO)
# Calendar sensor class
```

## CALENDAR_INFO Dictionary Structure

The `CALENDAR_INFO` dictionary is the heart of each calendar implementation. It contains all metadata, configuration options, and calendar-specific data.

### Required Top-Level Keys

#### Basic Information
```python
CALENDAR_INFO = {
    "id": "unique_calendar_id",           # Unique identifier (lowercase, no spaces)
    "version": "2.5.0",                    # Format version
    "icon": "mdi:icon-name",              # Material Design Icon
    "category": "cultural",                # Category: cultural/historical/technical/space/fantasy
    "accuracy": "approximate",             # Accuracy: precise/approximate/fictional/mathematical/official
    "update_interval": 3600,               # Update interval in seconds (1-3600)
}
```

#### Multi-Language Support
```python
"name": {
    "en": "Calendar Name",
    "de": "Kalendername",
    "es": "Nombre del Calendario",
    "fr": "Nom du Calendrier",
    "it": "Nome del Calendario",
    "nl": "Kalendernaam",
    "pt": "Nome do Calendário",
    "ru": "Название календаря",
    "ja": "カレンダー名",
    "zh": "日历名称",
    "ko": "달력 이름"
    # Additional languages as needed
},

"description": {
    "en": "Brief description (max 100 chars)",
    "de": "Kurze Beschreibung",
    # ... other languages
}
```

#### Detailed Information
```python
"detailed_info": {
    "en": {
        "overview": "Complete overview of the calendar system",
        "structure": "How the calendar is structured",
        "year": "Year calculation and length",
        "months": "Month system explanation",
        "weeks": "Week structure if applicable",
        "special": "Special features or rules",
        "usage": "Where and how it's used",
        "history": "Historical context"
    },
    "de": {
        # German translations of all keys
    }
    # Additional languages
}
```

### Calendar-Specific Data

Each calendar has its own data section with a unique key (e.g., `egyptian_data`, `darian_data`):

```python
"[calendar_name]_data": {
    # Calendar-specific structures
    "months": [...],           # Month definitions
    "weekdays": [...],         # Weekday names if applicable
    "special_dates": {...},    # Holidays, events, etc.
    "constants": {...},        # Mathematical constants
    "conversions": {...},      # Conversion factors
    # Additional calendar-specific data
}
```

### Metadata and References
```python
"reference_url": "https://...",           # Primary reference URL
"documentation_url": "https://...",       # Documentation URL
"origin": "Culture/Country/Creator",      # Origin of the calendar
"created_by": "Name",                     # Creator(s)
"introduced": "Date/Period",              # When introduced
"discontinued": "Date/Period",            # If discontinued

"example": "Example date format",
"example_meaning": "Explanation of the example",

"related": ["calendar1", "calendar2"],    # Related calendar systems
"tags": ["tag1", "tag2", "tag3"],        # Search tags

"features": {
    "leap_years": True,
    "lunar_based": False,
    "precision": "day",                   # second/minute/hour/day/month/year
    # Additional boolean feature flags
}
```

### Configuration Options
```python
"config_options": {
    "option_name": {
        "type": "boolean",                # boolean/select/integer/float/string
        "default": True,                  # Default value
        "description": {
            "en": "Option description",
            "de": "Optionsbeschreibung",
            # ... other languages
        },
        # For select type:
        "options": ["option1", "option2", "option3"],
        # For numeric types:
        "min": 0,
        "max": 100,
        "step": 1
    }
}
```

## Sensor Class Implementation

### Class Structure
```python
class CalendarNameSensor(AlternativeTimeSensorBase):
    """Sensor for displaying Calendar Name."""
    
    # Class-level update interval
    UPDATE_INTERVAL = 3600  # Must match CALENDAR_INFO
    
    def __init__(self, base_name: str, hass: HomeAssistant) -> None:
        """Initialize the calendar sensor."""
        super().__init__(base_name, hass)
        
        # Get translated name from metadata
        calendar_name = self._translate('name', 'Default Name')
        
        # Set sensor attributes
        self._attr_name = f"{base_name} {calendar_name}"
        self._attr_unique_id = f"{base_name}_calendar_id"
        self._attr_icon = CALENDAR_INFO.get("icon", "mdi:calendar")
        
        # Configuration options (match config_options keys)
        self._option1 = True
        self._option2 = "default_value"
        
        # Calendar data
        self._calendar_data = CALENDAR_INFO["[calendar_name]_data"]
        
        _LOGGER.debug(f"Initialized {calendar_name} sensor: {self._attr_name}")
```

### Required Methods

#### State Property
```python
@property
def state(self):
    """Return the state of the sensor."""
    return self._state
```

#### Extra State Attributes
```python
@property
def extra_state_attributes(self) -> Dict[str, Any]:
    """Return the state attributes."""
    attrs = super().extra_state_attributes
    
    # Add calendar-specific attributes
    if hasattr(self, '_calendar_date'):
        attrs.update(self._calendar_date)
        
        # Add description in user's language
        attrs["description"] = self._translate('description')
        
        # Add reference
        attrs["reference"] = CALENDAR_INFO.get('reference_url', '')
        
        # Add any additional attributes
    
    return attrs
```

#### Update Method
```python
def update(self) -> None:
    """Update the sensor."""
    now = datetime.now()
    self._calendar_date = self._calculate_calendar_date(now)
    
    # Set state to formatted date
    self._state = self._calendar_date["full_date"]
    
    _LOGGER.debug(f"Updated Calendar to {self._state}")
```

#### Calculate Method
```python
def _calculate_calendar_date(self, earth_date: datetime) -> Dict[str, Any]:
    """Calculate calendar date from standard date."""
    
    # Perform calendar-specific calculations
    
    result = {
        "year": calculated_year,
        "month": month_name,
        "day": day_number,
        "full_date": formatted_date,
        "gregorian_date": earth_date.strftime("%Y-%m-%d"),
        # Additional fields as needed
    }
    
    return result
```

### Helper Methods (Optional)
```python
def _helper_method(self, param: Any) -> Any:
    """Helper method for specific calculations."""
    # Implementation
    return result
```

## Best Practices

### 1. Update Intervals
- **1 second**: Real-time displays (clocks, decimal time)
- **60 seconds**: Minute-precision calendars
- **3600 seconds**: Day-based calendars
- **86400 seconds**: Slow-changing calendars

### 2. Multi-Language Support
- Always provide at least English (`en`)
- Use native scripts where appropriate (Thai, Arabic, Chinese, etc.)
- Provide romanized versions for non-Latin scripts

### 3. State Display
- Keep state concise (main date/time only)
- Put detailed information in attributes
- Format should be readable at a glance

### 4. Error Handling
```python
try:
    calculation = complex_operation()
except Exception as e:
    _LOGGER.error(f"Error calculating date: {e}")
    return self._get_fallback_date()
```

### 5. Performance
- Cache calculations when possible
- Use appropriate update intervals
- Avoid heavy computations in properties

### 6. Documentation
- Include docstrings for all methods
- Add inline comments for complex calculations
- Reference sources for algorithms

## Example Implementations

### Simple Calendar (Egyptian)
- Fixed 365-day year
- 12 months of 30 days + 5 epagomenal days
- No leap years
- Historical/cultural significance

### Complex Calendar (Darian - Mars)
- Scientific calculations
- Multiple conversion factors
- Leap year system
- Astronomical basis

### Fantasy Calendar (Discworld)
- 8-day weeks
- Impossible dates (32nd of December)
- Dynamic content (quotes, locations)
- Humor and references

### Technical Calendar (Decimal Time)
- Mathematical conversion
- Real-time updates
- High precision
- Historical context

## Testing Checklist

- [ ] Calendar loads without errors
- [ ] State updates correctly
- [ ] All attributes populated
- [ ] Multi-language support works
- [ ] Configuration options apply correctly
- [ ] Update interval is appropriate
- [ ] Icon displays correctly
- [ ] Documentation is complete
- [ ] Edge cases handled (leap years, etc.)
- [ ] Performance is acceptable

## Adding a New Calendar

1. Create a new Python file in `calendars/` directory
2. Copy the template structure
3. Fill in `CALENDAR_INFO` dictionary
4. Implement calendar calculations
5. Test thoroughly
6. Add to `__init__.py` if needed
7. Update main documentation

## Version History

- **2.5.0**: Current version with full metadata structure
- **2.0.0**: Added multi-language support
- **1.0.0**: Initial format specification

## Support

For questions or contributions, please refer to the main project documentation or open an issue in the repository.