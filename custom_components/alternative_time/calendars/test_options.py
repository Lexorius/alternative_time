"""Test Calendar - Plugin Options Testing and Debugging
Version 1.0.0 - Comprehensive testing of all option types and lifecycle
"""
from __future__ import annotations

from datetime import datetime
import logging
import json
from typing import Dict, Any

from homeassistant.core import HomeAssistant
from ..sensor import AlternativeTimeSensorBase

_LOGGER = logging.getLogger(__name__)

# ============================================
# CALENDAR METADATA
# ============================================

UPDATE_INTERVAL = 60  # Update every minute

CALENDAR_INFO = {
    "id": "test_options",
    "version": "1.0.0",
    "icon": "mdi:test-tube",
    "category": "technical",
    "accuracy": "debug",
    "update_interval": UPDATE_INTERVAL,
    
    # Multi-language names
    "name": {
        "en": "Test Options Calendar",
        "de": "Test-Optionen Kalender",
        "es": "Calendario de Prueba de Opciones",
        "fr": "Calendrier Test des Options"
    },
    
    # Descriptions
    "description": {
        "en": "Tests all plugin option types and shows debug info",
        "de": "Testet alle Plugin-Optionstypen und zeigt Debug-Infos",
        "es": "Prueba todos los tipos de opciones y muestra información de depuración",
        "fr": "Teste tous les types d'options et affiche les infos de débogage"
    },
    
    # Reference
    "reference_url": "https://github.com/Lexorius/alternative_time",
    "documentation_url": "https://github.com/Lexorius/alternative_time/wiki",
    
    # Tags
    "tags": ["test", "debug", "options", "development", "diagnostic"],
    
    # Features
    "features": {
        "test_mode": True,
        "debug_output": True,
        "option_validation": True
    },
    
    # Configuration options - Testing ALL types
    "config_options": {
        # Boolean option
        "test_boolean": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Test Boolean",
                "de": "Test Boolean"
            },
            "description": {
                "en": "Tests boolean option type",
                "de": "Testet Boolean-Optionstyp"
            }
        },
        
        # Select/Dropdown option
        "test_select": {
            "type": "select",
            "default": "option2",
            "options": ["option1", "option2", "option3", "option4"],
            "label": {
                "en": "Test Select",
                "de": "Test Auswahl"
            },
            "description": {
                "en": "Tests select/dropdown option type",
                "de": "Testet Auswahl/Dropdown-Optionstyp"
            }
        },
        
        # Text/String option
        "test_text": {
            "type": "text",
            "default": "Default Text Value",
            "label": {
                "en": "Test Text",
                "de": "Test Text"
            },
            "description": {
                "en": "Tests text input option type",
                "de": "Testet Text-Eingabe-Optionstyp"
            }
        },
        
        # Number option with min/max
        "test_number": {
            "type": "number",
            "default": 42,
            "min": 0,
            "max": 100,
            "label": {
                "en": "Test Number (0-100)",
                "de": "Test Zahl (0-100)"
            },
            "description": {
                "en": "Tests number option with min/max",
                "de": "Testet Zahlen-Option mit Min/Max"
            }
        },
        
        # Float option
        "test_float": {
            "type": "float",
            "default": 3.14159,
            "label": {
                "en": "Test Float",
                "de": "Test Gleitkommazahl"
            },
            "description": {
                "en": "Tests floating point number option",
                "de": "Testet Gleitkommazahl-Option"
            }
        },
        
        # Integer option
        "test_integer": {
            "type": "integer",
            "default": 10,
            "label": {
                "en": "Test Integer",
                "de": "Test Ganzzahl"
            },
            "description": {
                "en": "Tests integer number option",
                "de": "Testet Ganzzahl-Option"
            }
        },
        
        # String option (alternative to text)
        "test_string": {
            "type": "string",
            "default": "String Default",
            "label": {
                "en": "Test String",
                "de": "Test Zeichenkette"
            },
            "description": {
                "en": "Tests string option type",
                "de": "Testet String-Optionstyp"
            }
        }
    }
}


class TestOptionsCalendarSensor(AlternativeTimeSensorBase):
    """Test sensor for debugging plugin options."""
    
    UPDATE_INTERVAL = UPDATE_INTERVAL
    
    def __init__(self, base_name: str, hass: HomeAssistant) -> None:
        """Initialize the test sensor."""
        super().__init__(base_name, hass)
        
        # Get translated name
        calendar_name = self._translate('name', 'Test Options Calendar')
        
        # Set sensor attributes
        self._attr_name = f"{base_name} {calendar_name}"
        self._attr_unique_id = f"{base_name}_test_options"
        self._attr_icon = CALENDAR_INFO.get("icon", "mdi:test-tube")
        
        # Store all lifecycle events
        self._lifecycle_log = []
        self._log_event("__init__", "Sensor initialized")
        
        # Option values - set defaults
        self._test_boolean = True
        self._test_select = "option2"
        self._test_text = "Default Text Value"
        self._test_number = 42
        self._test_float = 3.14159
        self._test_integer = 10
        self._test_string = "String Default"
        
        # Tracking
        self._options_loaded = False
        self._update_count = 0
        self._first_update = True
        self._options_history = []
        
        # Initialize state
        self._state = "Initializing..."
        self._debug_data = {}
        
        _LOGGER.info(f"TestOptionsCalendarSensor initialized: {self._attr_name}")
    
    def _log_event(self, event: str, details: str = "") -> None:
        """Log lifecycle events with timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        entry = {
            "time": timestamp,
            "event": event,
            "details": details
        }
        self._lifecycle_log.append(entry)
        _LOGGER.info(f"[TEST_OPTIONS] {timestamp} - {event}: {details}")
    
    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        self._log_event("async_added_to_hass", "Starting")
        
        # Call parent
        await super().async_added_to_hass()
        
        # Try to load options
        self._log_event("async_added_to_hass", f"calendar_id={self._calendar_id}, config_entry_id={self._config_entry_id}")
        
        options = self.get_plugin_options()
        if options:
            self._log_event("async_added_to_hass", f"Options loaded: {options}")
            self._apply_options(options, "async_added_to_hass")
        else:
            self._log_event("async_added_to_hass", "No options available yet")
        
        self._log_event("async_added_to_hass", "Completed")
    
    def _apply_options(self, options: Dict[str, Any], source: str) -> None:
        """Apply options and track changes."""
        self._log_event(f"apply_options_{source}", f"Applying: {options}")
        
        # Track history
        self._options_history.append({
            "timestamp": datetime.now().isoformat(),
            "source": source,
            "options": options.copy()
        })
        
        # Apply each option
        old_values = {
            "test_boolean": self._test_boolean,
            "test_select": self._test_select,
            "test_text": self._test_text,
            "test_number": self._test_number,
            "test_float": self._test_float,
            "test_integer": self._test_integer,
            "test_string": self._test_string
        }
        
        # Update values
        self._test_boolean = bool(options.get("test_boolean", True))
        self._test_select = str(options.get("test_select", "option2"))
        self._test_text = str(options.get("test_text", "Default Text Value"))
        
        try:
            self._test_number = float(options.get("test_number", 42))
        except (ValueError, TypeError):
            self._test_number = 42
            
        try:
            self._test_float = float(options.get("test_float", 3.14159))
        except (ValueError, TypeError):
            self._test_float = 3.14159
            
        try:
            self._test_integer = int(options.get("test_integer", 10))
        except (ValueError, TypeError):
            self._test_integer = 10
            
        self._test_string = str(options.get("test_string", "String Default"))
        
        # Log changes
        new_values = {
            "test_boolean": self._test_boolean,
            "test_select": self._test_select,
            "test_text": self._test_text,
            "test_number": self._test_number,
            "test_float": self._test_float,
            "test_integer": self._test_integer,
            "test_string": self._test_string
        }
        
        changes = {}
        for key in old_values:
            if old_values[key] != new_values[key]:
                changes[key] = {
                    "old": old_values[key],
                    "new": new_values[key]
                }
        
        if changes:
            self._log_event(f"options_changed_{source}", f"Changes: {changes}")
        
        self._options_loaded = True
    
    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return detailed debug attributes."""
        attrs = super().extra_state_attributes
        
        # Add all debug information
        attrs.update({
            # Current option values
            "current_options": {
                "test_boolean": self._test_boolean,
                "test_select": self._test_select,
                "test_text": self._test_text,
                "test_number": self._test_number,
                "test_float": self._test_float,
                "test_integer": self._test_integer,
                "test_string": self._test_string
            },
            
            # Option types for verification
            "option_types": {
                "test_boolean": f"{type(self._test_boolean).__name__} = {self._test_boolean}",
                "test_select": f"{type(self._test_select).__name__} = {self._test_select}",
                "test_text": f"{type(self._test_text).__name__} = {self._test_text}",
                "test_number": f"{type(self._test_number).__name__} = {self._test_number}",
                "test_float": f"{type(self._test_float).__name__} = {self._test_float}",
                "test_integer": f"{type(self._test_integer).__name__} = {self._test_integer}",
                "test_string": f"{type(self._test_string).__name__} = {self._test_string}"
            },
            
            # Status information
            "status": {
                "options_loaded": self._options_loaded,
                "update_count": self._update_count,
                "calendar_id": self._calendar_id,
                "config_entry_id": self._config_entry_id,
                "last_update": datetime.now().isoformat()
            },
            
            # Lifecycle log (last 10 events)
            "lifecycle_log": self._lifecycle_log[-10:],
            
            # Options history (last 5 changes)
            "options_history": self._options_history[-5:],
            
            # Description
            "description": self._translate('description'),
            "reference": CALENDAR_INFO.get('reference_url', '')
        })
        
        return attrs
    
    def update(self) -> None:
        """Update the sensor."""
        self._update_count += 1
        self._log_event("update", f"Update #{self._update_count}")
        
        try:
            # Load options
            options = self.get_plugin_options()
            
            # First update special handling
            if self._first_update:
                self._log_event("first_update", "First update execution")
                if options:
                    self._log_event("first_update", f"Options available: {options}")
                    self._apply_options(options, "first_update")
                else:
                    self._log_event("first_update", "No options available")
                self._first_update = False
            elif options and not self._options_loaded:
                # Options became available after initialization
                self._log_event("update", "Options now available")
                self._apply_options(options, "update_delayed")
            elif options:
                # Check for changes
                current = {
                    "test_boolean": self._test_boolean,
                    "test_select": self._test_select,
                    "test_text": self._test_text,
                    "test_number": self._test_number,
                    "test_float": self._test_float,
                    "test_integer": self._test_integer,
                    "test_string": self._test_string
                }
                
                # Apply and check for changes
                self._apply_options(options, f"update_{self._update_count}")
            
            # Build state string
            state_parts = []
            
            # Show current values in state
            if self._options_loaded:
                state_parts.append(f"✓ Options Loaded")
                state_parts.append(f"Bool:{self._test_boolean}")
                state_parts.append(f"Select:{self._test_select}")
                state_parts.append(f"Num:{self._test_number}")
            else:
                state_parts.append("⚠ No Options")
            
            state_parts.append(f"Updates:{self._update_count}")
            
            self._state = " | ".join(state_parts)
            
        except Exception as e:
            self._log_event("update_error", str(e))
            _LOGGER.exception(f"Error in update: {e}")
            self._state = f"Error: {e}"
    
    async def async_will_remove_from_hass(self) -> None:
        """Log when entity is being removed."""
        self._log_event("async_will_remove_from_hass", "Entity being removed")
        await super().async_will_remove_from_hass()