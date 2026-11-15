"""Sensor platform for Alternative Time Systems."""
from __future__ import annotations

import asyncio
import logging
import os
import sys
from datetime import datetime, timedelta
from importlib import import_module
from typing import Any, Dict, List, Optional

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import MATCH_ALL
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.util import dt as dt_util

from .const import DOMAIN, ENTITY_ID_PREFIX
from .i18n import pick_language

_LOGGER = logging.getLogger(__name__)

# Discovered calendars: CALENDAR_INFO per calendar id, the module each id lives
# in, and that module's file name (id and file name can differ: suriyakati.py
# declares the id "suriyakati_thai"). Filled once per process; the files cannot
# change without a restart.
_DISCOVERED_CALENDARS_CACHE: Optional[Dict[str, Dict[str, Any]]] = None
_CALENDAR_MODULES: Dict[str, Any] = {}
_CALENDAR_MODULE_NAMES: Dict[str, str] = {}
_DISCOVERY_LOCK = asyncio.Lock()

# Config entries, for the sensors to read their options from
_CONFIG_ENTRIES: Dict[str, ConfigEntry] = {}

# Live sensor objects per config entry, used by the options flow to offer an
# entity_id migration (it needs entity_id -> calendar_id without parsing
# unique_ids). Reset on every setup of the entry, dropped on unload.
_ENTITIES_BY_ENTRY: Dict[str, List["AlternativeTimeSensorBase"]] = {}


def entities_for_entry(entry_id: str) -> List[tuple[str, str]]:
    """Return [(entity_id, calendar_id)] for the entry's currently added sensors."""
    out: List[tuple[str, str]] = []
    for sensor in _ENTITIES_BY_ENTRY.get(entry_id, []):
        eid = getattr(sensor, "entity_id", None)
        cid = getattr(sensor, "_calendar_id", None)
        if eid and cid:
            out.append((eid, cid))
    return out


def forget_config_entry(entry_id: str) -> None:
    """Drop a config entry from the module-level registries (called on unload)."""
    _CONFIG_ENTRIES.pop(entry_id, None)
    _ENTITIES_BY_ENTRY.pop(entry_id, None)


def discover_calendars() -> Dict[str, Dict[str, Any]]:
    """Import every calendar module and return {calendar_id: CALENDAR_INFO}.

    Blocking (lists a directory, imports modules): call it from an executor,
    or use async_discover_all_calendars(). The result is cached.
    """
    global _DISCOVERED_CALENDARS_CACHE
    if _DISCOVERED_CALENDARS_CACHE is not None:
        return _DISCOVERED_CALENDARS_CACHE

    discovered: Dict[str, Dict[str, Any]] = {}
    calendars_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "calendars")
    for filename in sorted(os.listdir(calendars_dir)):
        module_name = filename[:-3]
        if not filename.endswith(".py") or module_name.startswith(("_", "test_")):
            continue
        try:
            module = import_module(f".calendars.{module_name}", package=__package__)
        except Exception as err:  # noqa: BLE001 — one broken plugin must not hide the others
            _LOGGER.error("Calendar %s could not be imported: %r", module_name, err)
            continue
        info = getattr(module, "CALENDAR_INFO", None)
        if not isinstance(info, dict):
            continue
        calendar_id = info.get("id", module_name)
        discovered[calendar_id] = info
        _CALENDAR_MODULES[calendar_id] = module
        _CALENDAR_MODULE_NAMES[calendar_id] = module_name

    if discovered:
        _LOGGER.debug("Discovered %d calendars", len(discovered))
    else:
        _LOGGER.error("No calendars found in %s", calendars_dir)

    _DISCOVERED_CALENDARS_CACHE = discovered
    return discovered


async def async_discover_all_calendars(hass: HomeAssistant) -> Dict[str, Dict[str, Any]]:
    """Discover the calendars without blocking the event loop."""
    if _DISCOVERED_CALENDARS_CACHE is not None:
        return _DISCOVERED_CALENDARS_CACHE
    async with _DISCOVERY_LOCK:
        return await hass.async_add_executor_job(discover_calendars)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Alternative Time Systems sensors from a config entry."""
    entry_id = config_entry.entry_id
    _CONFIG_ENTRIES[entry_id] = config_entry
    _ENTITIES_BY_ENTRY[entry_id] = []

    selected_calendars = config_entry.data.get("calendars", [])
    name = config_entry.data.get("name", "Alternative Time")
    _LOGGER.debug("Setting up '%s' with calendars %s", name, selected_calendars)

    if not selected_calendars:
        _LOGGER.warning("No calendars selected for '%s'", name)
        return

    await async_discover_all_calendars(hass)

    sensors = []
    for calendar_id in selected_calendars:
        module = _CALENDAR_MODULES.get(calendar_id)
        if module is None:
            _LOGGER.error("Calendar '%s' is configured in '%s' but does not exist (any more)", calendar_id, name)
            continue

        sensor_class = next(
            (item for item in vars(module).values()
             if isinstance(item, type)
             and issubclass(item, AlternativeTimeSensorBase)
             and item is not AlternativeTimeSensorBase),
            None,
        )
        if sensor_class is None:
            _LOGGER.error("No sensor class found in calendar module: %s", calendar_id)
            continue

        try:
            sensor = sensor_class(name, hass)
        except Exception as err:  # noqa: BLE001 — one broken plugin must not block the others
            _LOGGER.error("Failed to create sensor for calendar %s: %r", calendar_id, err)
            _LOGGER.debug("Traceback:", exc_info=True)
            continue

        # The sensor reads its options through these two ids
        sensor._calendar_id = calendar_id
        sensor._config_entry_id = entry_id

        # Stable entity_id for NEW entities: sensor.alternative_time_<calendar>,
        # whatever the entry is called, so one recorder glob matches them all.
        # A pre-set entity_id is what Home Assistant takes as the wanted id (it
        # adds _2, _3 on a clash); entities already in the registry keep the id
        # they have. Only suggesting an object id is not enough: newer Home
        # Assistant versions put the device and area name in front of it.
        sensor.entity_id = f"sensor.{ENTITY_ID_PREFIX}{calendar_id}"

        # The entry id makes the unique_id unique across entries
        sensor._attr_unique_id = f"{entry_id}_{sensor._attr_unique_id}"

        sensors.append(sensor)
        _ENTITIES_BY_ENTRY[entry_id].append(sensor)

    if sensors:
        async_add_entities(sensors)
        _LOGGER.info("Added %d sensors for '%s'", len(sensors), name)
    else:
        _LOGGER.warning("No sensors were created for '%s'", name)


# NOTE on recorder exclusion: Home Assistant offers no API for an integration
# to keep an entity's *state* out of the recorder — that is user configuration
# only (recorder: exclude: entity_globs: [sensor.alternative_time_*]). What we
# can do integration-side is (a) give every sensor a stable entity_id so that
# one glob matches (see async_setup_entry and the options-flow migration) and
# (b) not record attributes at all (_unrecorded_attributes = MATCH_ALL below).


class AlternativeTimeSensorBase(SensorEntity):
    """Base class for Alternative Time System sensors."""

    # Record only the state string, never the attributes. Attributes stay
    # live in the state machine (dashboards, templates, more-info dialog are
    # unaffected) — they just don't get written to the recorder's
    # state_attributes table. For time sensors attribute *history* is never
    # used. HA keeps friendly_name/device_class/unit/state_class even with
    # MATCH_ALL.
    _unrecorded_attributes = frozenset({MATCH_ALL})

    # After this many consecutive failed updates the entity is marked
    # unavailable instead of silently showing a stale state.
    UNAVAILABLE_AFTER_FAILURES = 3

    def __init__(self, base_name: str, hass: HomeAssistant) -> None:
        """Initialize the sensor."""
        self._base_name = base_name
        self._hass = hass
        self._state = None
        # Scheduling is owned by our own timer (see async_added_to_hass);
        # should_poll is False so HA's platform poller stays out of it.
        self._tick_running = False
        self._consecutive_failures = 0
        self._calendar_id = None  # set by async_setup_entry
        self._config_entry_id = None  # set by async_setup_entry

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Normalized parent attributes as a dict (never None).

        HA's SensorEntity.extra_state_attributes returns None by default.
        Returning a dict here ensures plugin code that calls
        ``super().extra_state_attributes.update(...)`` won't crash.
        """
        try:
            parent_val = super().extra_state_attributes  # type: ignore[attr-defined]
        except Exception:
            parent_val = None
        return dict(parent_val) if isinstance(parent_val, dict) else {}

    @property
    def should_poll(self) -> bool:
        """Never let the platform poll us.

        Each entity runs its own timer at CALENDAR_INFO["update_interval"].
        Returning True here (as older versions did) made HA additionally poll
        every entity at the sensor default of 30 s, so every plugin updated
        twice and sync update() could run concurrently in two executor threads.
        """
        return False

    # `available` is inherited from HA's Entity and driven by _attr_available,
    # which _async_timer_tick flips after repeated failures.

    def _now(self) -> datetime:
        """Wall-clock time in Home Assistant's configured time zone (naive).

        Use this instead of datetime.now(): that returns the time zone of the
        operating system, which in a container without TZ is UTC, not the
        zone the user set in Home Assistant.
        """
        return dt_util.now().replace(tzinfo=None)

    def _calendar_meta(self) -> Dict[str, Any]:
        """CALENDAR_INFO of the module this sensor class is defined in."""
        return getattr(sys.modules.get(type(self).__module__), "CALENDAR_INFO", None) or {}

    def get_plugin_options(self) -> Dict[str, Any]:
        """Options the user chose for this calendar in the config flow."""
        if not self._config_entry_id or not self._calendar_id:
            _LOGGER.warning("%s: options requested before the sensor was set up", type(self).__name__)
            return {}

        config_entry = _CONFIG_ENTRIES.get(self._config_entry_id)
        if not config_entry:
            _LOGGER.error("Config entry %s not found", self._config_entry_id)
            return {}

        # Stored by the config flow under "calendar_options" ("plugin_options"
        # is the key very old entries used).
        all_options = (
            config_entry.data.get("calendar_options")
            or config_entry.data.get("plugin_options", {})
        )
        return all_options.get(self._calendar_id, {})

    # Five plugins call the method under this name.
    _get_plugin_options = get_plugin_options

    def _translate(self, key: str, default: str = "") -> str:
        """Text block ``key`` of CALENDAR_INFO in the user's language.

        A plain string is returned as is; a {language: text} mapping goes
        through i18n.pick_language (exact code, base language, English, default).
        """
        value = self._calendar_meta().get(key, default)
        if not isinstance(value, dict):
            return str(value)
        return pick_language(value, getattr(self._hass.config, "language", "en"), default)

    @property
    def device_info(self):
        """Return device registry information for this entity."""
        category = str(self._calendar_meta().get("category") or "uncategorized")
        if category == "religious":
            category = "religion"
        return {
            "identifiers": {(DOMAIN, f"group:{category}")},
            "manufacturer": "Alternative Time Systems",
            "model": "Category Group",
            "name": f"Alternative Time – {category.title()}",
        }

    async def async_added_to_hass(self) -> None:
        """Schedule periodic updates in a non-blocking way."""
        interval = self._calendar_meta().get("update_interval")
        if not isinstance(interval, (int, float)):
            interval = getattr(type(self), "UPDATE_INTERVAL", None)
        try:
            seconds = max(1, int(interval)) if interval else 3600
        except (TypeError, ValueError):
            seconds = 3600

        _LOGGER.debug("%s added, updates every %s seconds", self._attr_name, seconds)

        self._unsub_timer = async_track_time_interval(
            self._hass, self._async_timer_tick, timedelta(seconds=seconds)
        )

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
        """Call plugin update without blocking the event loop.

        - Skips the tick if the previous one is still running (a slow
          update must not pile up on a short interval).
        - Logs the first failure of a streak at WARNING (traceback at DEBUG),
          further consecutive failures at DEBUG only, recovery at INFO.
        - Flips ``_attr_available`` after UNAVAILABLE_AFTER_FAILURES.
        """
        if self._tick_running:
            _LOGGER.debug(f"{self.entity_id or self.name}: previous update still running, skipping tick")
            return
        self._tick_running = True
        label = self.entity_id or self.name
        try:
            # Prefer plugin's async_update if available
            if hasattr(self, "async_update") and callable(getattr(self, "async_update")):
                await getattr(self, "async_update")()
            else:
                await self._hass.async_add_executor_job(getattr(self, "update"))
        except Exception as exc:  # noqa: BLE001 — plugin code, must never kill the timer
            self._consecutive_failures += 1
            n = self._consecutive_failures
            if n == 1:
                _LOGGER.warning(f"Update of {label} ({self._calendar_id}) failed: {exc!r}")
                _LOGGER.debug("Traceback:", exc_info=True)
            else:
                _LOGGER.debug(f"Update of {label} failed again ({n}x): {exc!r}")
            if n == self.UNAVAILABLE_AFTER_FAILURES:
                self._attr_available = False
                _LOGGER.warning(f"{label} marked unavailable after {n} consecutive failed updates")
        else:
            if self._consecutive_failures:
                _LOGGER.info(f"{label} recovered after {self._consecutive_failures} failed update(s)")
                self._consecutive_failures = 0
            self._attr_available = True
        finally:
            self._tick_running = False
            # Entity may have been removed while the update was running
            if self.hass is not None:
                try:
                    self.async_write_ha_state()
                except Exception as exc:  # noqa: BLE001
                    _LOGGER.debug(f"{label}: writing state failed: {exc!r}")
