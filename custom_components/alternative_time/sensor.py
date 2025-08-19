"""Sensor platform for Alternative Time Systems."""
from __future__ import annotations

import os
import logging
import asyncio
from datetime import timedelta
from typing import Any, Dict, List, Optional
from importlib import import_module

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, EVENT_HOMEASSISTANT_STARTED
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Global cache for discovered calendars
_DISCOVERED_CALENDARS_CACHE: Optional[Dict[str, Dict[str, Any]]] = None
_DISCOVERY_LOCK = asyncio.Lock()

# Store config entries globally for sensor access
_CONFIG_ENTRIES: Dict[str, ConfigEntry] = {}


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Alternative Time Systems sensors from a config entry."""
    
    # Store config entry for sensor access
    entry_id = config_entry.entry_id
    _CONFIG_ENTRIES[entry_id] = config_entry
    
    # Get selected calendars from config
    selected_calendars = config_entry.data.get("calendars", [])
    name = config_entry.data.get("name", "Alternative Time")
    
    if not selected_calendars:
        _LOGGER.warning("No calendars selected")
        return
    
    _LOGGER.info(f"Setting up sensors for calendars: {selected_calendars}")
    
    # Clear cache to force re-discovery
    global _DISCOVERED_CALENDARS_CACHE
    _DISCOVERED_CALENDARS_CACHE = None
    
    # Discover all available calendars
    discovered_calendars = await async_discover_all_calendars(hass)
    
    if not discovered_calendars:
        _LOGGER.error("No calendars could be discovered!")
        return
    
    _LOGGER.info(f"Discovered calendars: {list(discovered_calendars.keys())}")
    
    # Create sensors for selected calendars
    sensors = []
    entities_to_exclude = []  # Sammle Entities für Recorder-Exclusion
    
    for calendar_id in selected_calendars:
        if calendar_id not in discovered_calendars:
            _LOGGER.error(f"Calendar '{calendar_id}' is enabled but not found in registry")
            _LOGGER.debug(f"Available calendars: {list(discovered_calendars.keys())}")
            continue
        
        calendar_info = discovered_calendars[calendar_id]
        
        try:
            # Import the calendar module asynchronously
            module = await async_import_calendar_module(hass, calendar_id)
            
            if not module:
                _LOGGER.error(f"Failed to import calendar module: {calendar_id}")
                continue
            
            # Find the sensor class
            sensor_class = None
            for item_name in dir(module):
                item = getattr(module, item_name)
                if (isinstance(item, type) and 
                    issubclass(item, AlternativeTimeSensorBase) and 
                    item != AlternativeTimeSensorBase):
                    sensor_class = item
                    break
            
            if not sensor_class:
                _LOGGER.error(f"No sensor class found in calendar module: {calendar_id}")
                continue
            
            # Create sensor instance - store calendar_id for later lookup
            sensor = sensor_class(name, hass)
            sensor._calendar_id = calendar_id  # Store for plugin options lookup
            sensor._config_entry_id = entry_id  # Store entry ID
            sensors.append(sensor)
            
            # Check if this sensor should be excluded from recorder
            update_interval = calendar_info.get("update_interval", 3600)
            if update_interval <= 10:  # 10 seconds or faster
                entity_id = f"sensor.{name.lower().replace(' ', '_')}_{calendar_id}"
                entities_to_exclude.append(entity_id)
                _LOGGER.info(f"Marking {entity_id} for recorder exclusion (updates every {update_interval}s)")
            
            _LOGGER.info(f"Created sensor for calendar: {calendar_id}")
            
        except Exception as e:
            _LOGGER.error(f"Failed to create sensor for calendar {calendar_id}: {e}")
            import traceback
            _LOGGER.debug(traceback.format_exc())
            continue
    
    if sensors:
        async_add_entities(sensors)
        _LOGGER.info(f"Added {len(sensors)} sensors to Home Assistant")
        
        # Register entities for recorder exclusion
        if entities_to_exclude:
            await _register_recorder_exclusion(hass, entities_to_exclude)


async def _register_recorder_exclusion(hass: HomeAssistant, entity_ids: List[str]) -> None:
    """Register entities to be excluded from recorder."""
    
    async def _exclude_from_recorder(_event=None):
        """Exclude entities from recorder after startup."""
        try:
            # Try to access recorder component
            recorder = hass.components.recorder
            if hasattr(recorder, 'exclude_t'):
                # This is the internal way, might not always work
                for entity_id in entity_ids:
                    _LOGGER.info(f"Attempting to exclude {entity_id} from recorder")
            
            # Alternative method: Set attribute on the entity registry
            from homeassistant.helpers import entity_registry as er
            registry = er.async_get(hass)
            
            for entity_id in entity_ids:
                entry = registry.async_get(entity_id)
                if entry:
                    # Set a custom attribute that recorder might respect
                    registry.async_update_entity(
                        entity_id,
                        entity_category="diagnostic"  # Diagnostic entities have lower priority
                    )
                    _LOGGER.info(f"Set {entity_id} as diagnostic entity")
                    
        except Exception as e:
            _LOGGER.warning(f"Could not automatically exclude entities from recorder: {e}")
            _LOGGER.info("Please add the following to your configuration.yaml:")
            _LOGGER.info("recorder:")
            _LOGGER.info("  exclude:")
            _LOGGER.info("    entities:")
            for entity_id in entity_ids:
                _LOGGER.info(f"      - {entity_id}")
    
    # Try to exclude immediately if recorder is loaded
    if hass.components.recorder:
        await _exclude_from_recorder()
    else:
        # Wait for startup to complete
        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STARTED, _exclude_from_recorder)


async def async_discover_all_calendars(hass: HomeAssistant) -> Dict[str, Dict[str, Any]]:
    """Discover all available calendar implementations asynchronously."""
    global _DISCOVERED_CALENDARS_CACHE
    
    async with _DISCOVERY_LOCK:
        # Return cached result if available
        if _DISCOVERED_CALENDARS_CACHE is not None:
            return _DISCOVERED_CALENDARS_CACHE
        
        discovered = {}
        
        # Get calendars directory path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        calendars_dir = os.path.join(current_dir, "calendars")
        
        if not os.path.exists(calendars_dir):
            _LOGGER.warning(f"Calendars directory not found: {calendars_dir}")
            _DISCOVERED_CALENDARS_CACHE = discovered
            return discovered
        
        # List files asynchronously
        files = await hass.async_add_executor_job(os.listdir, calendars_dir)
        _LOGGER.debug(f"Found files in calendars directory: {files}")
        
        for filename in files:
            if filename.endswith(".py") and not filename.startswith("__"):
                module_name = filename[:-3]  # Remove .py extension
                
                # Skip template and example files
                if "template" in module_name.lower() or "example" in module_name.lower():
                    continue
                
                try:
                    # Import module asynchronously
                    module = await async_import_calendar_module(hass, module_name)
                    
                    if module and hasattr(module, 'CALENDAR_INFO'):
                        cal_info = module.CALENDAR_INFO
                        cal_id = cal_info.get('id', module_name)
                        discovered[cal_id] = cal_info
                        _LOGGER.debug(f"Discovered calendar: {cal_id}")
                    elif module:
                        _LOGGER.debug(f"Module {module_name} has no CALENDAR_INFO")
                    else:
                        _LOGGER.debug(f"Could not import module {module_name}")
                        
                except Exception as e:
                    _LOGGER.warning(f"Failed to discover calendar {module_name}: {e}")
                    import traceback
                    _LOGGER.debug(traceback.format_exc())
                    continue
        
        if not discovered:
            _LOGGER.error(f"No calendars discovered! Directory contents: {files}")
        else:
            _LOGGER.info(f"Discovered {len(discovered)} calendars: {list(discovered.keys())}")
        
        _DISCOVERED_CALENDARS_CACHE = discovered
        return discovered


async def async_import_calendar_module(hass: HomeAssistant, module_name: str):
    """Import a calendar module asynchronously."""
    def _import():
        try:
            # Add parent directory to path for imports
            import sys
            current_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(current_dir)
            if parent_dir not in sys.path:
                sys.path.insert(0, parent_dir)
            
            # Try different import methods
            try:
                module = import_module(f'.calendars.{module_name}', 
                                   package='custom_components.alternative_time')
                _LOGGER.debug(f"Successfully imported {module_name} via method 1")
                return module
            except ImportError as e1:
                _LOGGER.debug(f"Method 1 failed for {module_name}: {e1}")
                try:
                    module = import_module(
                        f'custom_components.alternative_time.calendars.{module_name}'
                    )
                    _LOGGER.debug(f"Successfully imported {module_name} via method 2")
                    return module
                except ImportError as e2:
                    _LOGGER.debug(f"Method 2 failed for {module_name}: {e2}")
                    try:
                        module = import_module(module_name)
                        _LOGGER.debug(f"Successfully imported {module_name} via method 3")
                        return module
                    except ImportError as e3:
                        _LOGGER.debug(f"Method 3 failed for {module_name}: {e3}")
                        raise e3
        except Exception as e:
            _LOGGER.error(f"Failed to import calendar module {module_name}: {e}")
            import traceback
            _LOGGER.debug(traceback.format_exc())
            return None
    
    return await hass.async_add_executor_job(_import)


def export_discovered_calendars() -> Dict[str, Dict[str, Any]]:
    """Export discovered calendars for use by config flow.
    
    This function is synchronous for backward compatibility,
    but should only be called from an executor.
    """
    global _DISCOVERED_CALENDARS_CACHE
    
    if _DISCOVERED_CALENDARS_CACHE is not None:
        return _DISCOVERED_CALENDARS_CACHE
    
    # Perform synchronous discovery if cache is empty
    discovered = {}
    current_dir = os.path.dirname(os.path.abspath(__file__))
    calendars_dir = os.path.join(current_dir, "calendars")
    
    if not os.path.exists(calendars_dir):
        _LOGGER.warning(f"Calendars directory not found in export: {calendars_dir}")
        return discovered
    
    files = os.listdir(calendars_dir)
    _LOGGER.debug(f"Export discovery - found files: {files}")
    
    for filename in files:
        if filename.endswith(".py") and not filename.startswith("__"):
            module_name = filename[:-3]
            
            # Skip template and example files
            if "template" in module_name.lower() or "example" in module_name.lower():
                continue
            
            try:
                module = import_module(f'.calendars.{module_name}', 
                                     package='custom_components.alternative_time')
                
                if hasattr(module, 'CALENDAR_INFO'):
                    cal_info = module.CALENDAR_INFO
                    cal_id = cal_info.get('id', module_name)
                    discovered[cal_id] = cal_info
                    _LOGGER.debug(f"Export discovered: {cal_id}")
                else:
                    _LOGGER.debug(f"Export - no CALENDAR_INFO in {module_name}")
                    
            except Exception as e:
                _LOGGER.debug(f"Export failed for {module_name}: {e}")
                continue
    
    if not discovered:
        _LOGGER.error(f"Export - no calendars discovered! Files: {files}")
    else:
        _LOGGER.info(f"Export discovered {len(discovered)} calendars")
    
    _DISCOVERED_CALENDARS_CACHE = discovered
    return discovered


def get_config_entry(entry_id: str) -> Optional[ConfigEntry]:
    """Get a config entry by ID."""
    return _CONFIG_ENTRIES.get(entry_id)


class AlternativeTimeSensorBase(SensorEntity):
    """Base class for Alternative Time System sensors."""
    
    # Class-level flag for recorder exclusion
    _exclude_from_recorder: bool = False

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Normalized parent attributes as a dict (never None).

        HA's SensorEntity.extra_state_attributes returns None by default.
        Returning a dict here ensures plugin code that calls
        ``super().extra_state_attributes.update(...)`` won't crash.
        """
        parent = getattr(super(), "extra_state_attributes", None)
        try:
            # If parent is a property on base class, access its value
            parent_val = super().extra_state_attributes  # type: ignore[attr-defined]
        except Exception:
            parent_val = None
        base_attrs = parent_val if isinstance(parent_val, dict) else (parent_val or {})
        
        # Füge History-Exclusion Marker hinzu für schnell aktualisierende Sensoren
        attrs = dict(base_attrs)
        if hasattr(self, '_update_interval') and self._update_interval <= 10:
            attrs["recorder_exclude_suggested"] = True
            attrs["update_interval_seconds"] = self._update_interval
        
        return attrs
    
    def __init__(self, base_name: str, hass: HomeAssistant) -> None:
        """Initialize the sensor."""
        self._base_name = base_name
        self._hass = hass
        self._state = None
        self._attr_should_poll = True
        self._calendar_id = None  # Will be set by async_setup_entry
        self._config_entry_id = None  # Will be set by async_setup_entry
        
        # Set update interval from class attribute if available
        if hasattr(self.__class__, 'UPDATE_INTERVAL'):
            self._update_interval = self.__class__.UPDATE_INTERVAL
        else:
            self._update_interval = 3600  # Default 1 hour
        
        # HISTORY CONTROL: State Class explizit auf None setzen
        # Dies verhindert die Erstellung von Langzeit-Statistiken
        self._attr_state_class = None
        
        # Markiere schnell aktualisierende Sensoren für Exclusion
        if self._update_interval <= 10:  # 10 Sekunden oder schneller
            self._exclude_from_recorder = True
            # Optional: Als diagnostic entity markieren (hat niedrigere Priorität)
            from homeassistant.helpers.entity import EntityCategory
            self._attr_entity_category = EntityCategory.DIAGNOSTIC
            
            _LOGGER.info(
                f"Sensor {base_name} updates every {self._update_interval}s - "
                f"marked as diagnostic entity to reduce database load"
            )
    
    @property
    def state_class(self):
        """Return None to disable statistics.
        
        This prevents Home Assistant from creating long-term statistics
        for this sensor, which is appropriate for time display sensors.
        """
        return None
    
    @property
    def entity_category(self):
        """Return entity category.
        
        Fast-updating sensors are marked as diagnostic to reduce their priority
        in the database and UI.
        """
        if hasattr(self, '_attr_entity_category'):
            return self._attr_entity_category
        return None
    
    def get_plugin_options(self) -> Dict[str, Any]:
        """Get plugin options for this sensor."""
        if not self._config_entry_id or not self._calendar_id:
            return {}
        
        config_entry = _CONFIG_ENTRIES.get(self._config_entry_id)
        if not config_entry:
            return {}
        
        # FIX: Verwende "calendar_options" statt "plugin_options"
        calendar_options = config_entry.data.get("calendar_options", {})
        return calendar_options.get(self._calendar_id, {})
    
    @property
    def update_interval(self) -> int:
        """Return the update interval in seconds."""
        return self._update_interval
    
    @property
    def should_poll(self) -> bool:
        """Return True if entity has to be polled for state."""
        return True
    
    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return True
    
    def _translate(self, key: str, default: str = "") -> str:
        """Translate a CALENDAR_INFO text block for the user's language.
        
        - Reads the integration's CALENDAR_INFO from the concrete sensor module.
        - Chooses hass.config.language if available; falls back to primary subtag (e.g. "de" from "de-DE"),
          then to English ("en"), and finally to the provided default.
        - If CALENDAR_INFO[key] is not a mapping (e.g. a plain string), that value is returned.
        """
        # Lazy-load CALENDAR_INFO from module
        info = {}
        try:
            mod = __import__(self.__class__.__module__, fromlist=["CALENDAR_INFO"])
            if hasattr(mod, "CALENDAR_INFO"):
                info = getattr(mod, "CALENDAR_INFO") or {}
        except Exception:
            info = {}
        
        item = info.get(key)
        if not item:
            return default
        
        # If not a dict (plain string), return as-is
        if not isinstance(item, dict):
            return str(item)
        
        # Get user language preference
        user_lang = "en"  # default
        try:
            user_lang = self._hass.config.language or "en"
        except Exception:
            pass
        
        # Extract primary language tag (e.g., "de" from "de-DE")
        primary = user_lang.split("-")[0].lower() if user_lang else "en"
        
        # Check in order: full lang code, primary lang code, "en", then any key
        for lang_key in [user_lang, primary, "en"]:
            if lang_key in item:
                return str(item[lang_key])
        
        # Return any available translation
        if item:
            return str(next(iter(item.values())))
        
        return default
    
    @property
    def device_info(self):
        """Return device information for grouping sensors."""
        # Lazy-load CALENDAR_INFO from module
        info = {}
        try:
            mod = __import__(self.__class__.__module__, fromlist=["CALENDAR_INFO"])
            if hasattr(mod, "CALENDAR_INFO"):
                info = getattr(mod, "CALENDAR_INFO") or {}
        except Exception:
            info = {}
        category = str(info.get("category") or "uncategorized")
        if category == "religious":
            category = "religion"
        device_name = f"Alternative Time — {category.title()}"
        return {
            "identifiers": {(DOMAIN, f"group:{category}")},
            "manufacturer": "Alternative Time Systems",
            "model": "Category Group",
            "name": device_name,
        }

    async def async_added_to_hass(self) -> None:
        """Schedule periodic updates in a non-blocking way."""
        # Determine interval from CALENDAR_INFO or class constant
        interval = None
        try:
            mod = __import__(self.__class__.__module__, fromlist=["CALENDAR_INFO"])
            info = getattr(mod, "CALENDAR_INFO", {}) or {}
            interval = info.get("update_interval")
        except Exception:
            interval = None
        if not isinstance(interval, (int, float)):
            interval = getattr(self.__class__, "UPDATE_INTERVAL", None)
        try:
            seconds = max(1, int(interval)) if interval else 3600
        except Exception:
            seconds = 3600

        # Avoid platform-wide polling
        self._attr_should_poll = False

        # Start scheduler
        from datetime import timedelta as _td
        self._unsub_timer = async_track_time_interval(self._hass, self._async_timer_tick, _td(seconds=seconds))
        # Trigger first run
        self._hass.async_create_task(self._async_timer_tick(None))

    async def async_will_remove_from_hass(self) -> None:
        """Cancel the scheduled timer when entity is removed."""
        unsub = getattr(self, "_unsub_timer", None)
        if unsub:
            try:
                unsub()
            except Exception:
                pass
            self._unsub_timer = None

    async def _async_timer_tick(self, _now) -> None:
        """Call plugin update without blocking the event loop."""
        try:
            # Prefer plugin's async_update if available
            if hasattr(self, "async_update") and callable(getattr(self, "async_update")):
                await getattr(self, "async_update")()
            else:
                await self._hass.async_add_executor_job(getattr(self, "update"))
        except Exception as exc:
            _LOGGER.debug(f"Scheduled update failed for {self.name}: {exc}")
        finally:
            try:
                self.async_write_ha_state()
            except Exception:
                pass