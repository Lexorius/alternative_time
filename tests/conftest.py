"""Test scaffolding: run the integration without a Home Assistant install.

Everything under ``homeassistant.*`` is served by a permissive stub module
(attribute access yields a MagicMock), except the handful of names the
integration *subclasses* or *calls with real semantics*, which are provided
as small real classes/functions below. ``voluptuous`` is stubbed as well.

This makes the tests fast (no HA bootstrap) and independent of the HA
version installed on the developer machine or CI runner. They exercise the
integration's own logic — discovery, scheduling, error handling, calendar
maths, recorder behaviour, translations — not HA itself.
"""
from __future__ import annotations

import asyncio
import importlib
import importlib.abc
import importlib.machinery
import logging
import sys
import time
import types
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import MagicMock
from zoneinfo import ZoneInfo

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

INTEGRATION = "custom_components.alternative_time"
TEST_ENTRY_ID = "test-entry"
HA_TIME_ZONE = "Europe/Berlin"

try:
    HA_TZ = ZoneInfo(HA_TIME_ZONE)
except Exception:  # no tz database on this machine (pip install tzdata)
    HA_TZ = timezone(timedelta(hours=1))


# --------------------------------------------------------------------------
# Minimal real base classes (the integration subclasses these)
# --------------------------------------------------------------------------
class FakeEntity:
    """Just enough of homeassistant.helpers.entity.Entity."""

    _attr_unique_id = None
    _attr_name = None
    _attr_icon = None
    _attr_available = True
    entity_id = None

    @property
    def extra_state_attributes(self):
        return None

    @property
    def name(self):
        return self._attr_name

    @property
    def available(self):
        return self._attr_available

    @property
    def unique_id(self):
        return self._attr_unique_id

    @property
    def hass(self):
        return getattr(self, "_hass_obj", None)

    @hass.setter
    def hass(self, value):
        self._hass_obj = value

    async def async_added_to_hass(self):
        return None

    def async_write_ha_state(self):
        self.writes = getattr(self, "writes", 0) + 1


class FakeSensorEntity(FakeEntity):
    """homeassistant.components.sensor.SensorEntity stand-in."""


class FakeConfig:
    language = "de"
    latitude = 49.14
    longitude = 9.22
    time_zone = HA_TIME_ZONE

    def path(self, *parts):
        import tempfile
        return str(Path(tempfile.gettempdir(), *parts))


class FakeHass:
    """Runs executor jobs inline and tasks on the current loop."""

    config = FakeConfig()

    def __init__(self):
        self.tasks: list[asyncio.Task] = []

    async def async_add_executor_job(self, fn, *args):
        return fn(*args)

    def async_create_task(self, coro):
        task = asyncio.get_event_loop().create_task(coro)
        self.tasks.append(task)
        return task


class FakeConfigEntry:
    """Minimal stand-in for homeassistant.config_entries.ConfigEntry."""

    def __init__(self, entry_id: str, data: dict | None = None):
        self.entry_id = entry_id
        self.title = "Alternative Time"
        self.data = data or {"calendar_options": {}, "calendars": []}
        self.options: dict = {}


# --------------------------------------------------------------------------
# Stub loader for homeassistant.*
# --------------------------------------------------------------------------
class _StubLoader(importlib.abc.Loader):
    def create_module(self, spec):
        module = types.ModuleType(spec.name)
        module.__path__ = []  # behave like a package so submodules resolve
        module.__getattr__ = lambda name, _m=module: _stub_attr(_m, name)
        return module

    def exec_module(self, module):
        return None


def _stub_attr(module, name):
    if name.startswith("__"):
        raise AttributeError(name)
    value = MagicMock(name=f"{module.__name__}.{name}")
    setattr(module, name, value)
    return value


class _StubFinder(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == "homeassistant" or fullname.startswith("homeassistant."):
            return importlib.machinery.ModuleSpec(fullname, _StubLoader(), is_package=True)
        return None


def ha_now() -> datetime:
    """Stand-in for homeassistant.util.dt.now(): aware, in the HA time zone."""
    return datetime.now(HA_TZ)


def install_ha_stub() -> None:
    """Idempotently install the stub and the real replacement names."""
    if not any(isinstance(f, _StubFinder) for f in sys.meta_path):
        sys.meta_path.insert(0, _StubFinder())

    sensor_mod = importlib.import_module("homeassistant.components.sensor")
    sensor_mod.SensorEntity = FakeSensorEntity
    entity_mod = importlib.import_module("homeassistant.helpers.entity")
    entity_mod.Entity = FakeEntity
    core = importlib.import_module("homeassistant.core")
    core.HomeAssistant = object
    core.callback = lambda f: f
    const = importlib.import_module("homeassistant.const")
    const.MATCH_ALL = "*"
    event = importlib.import_module("homeassistant.helpers.event")
    event.async_track_time_interval = lambda hass, cb, interval: (lambda: None)
    config_entries = importlib.import_module("homeassistant.config_entries")
    config_entries.ConfigFlow = type(
        "ConfigFlow", (), {"__init_subclass__": classmethod(lambda cls, **kw: None)}
    )
    config_entries.OptionsFlow = type("OptionsFlow", (), {})
    # `from homeassistant.util import dt` must give a module with a real now()
    util = importlib.import_module("homeassistant.util")
    dt_mod = importlib.import_module("homeassistant.util.dt")
    dt_mod.now = ha_now
    util.dt = dt_mod
    sys.modules.setdefault("voluptuous", MagicMock(name="voluptuous"))


install_ha_stub()

# Keep plugin DEBUG noise out of test output; tests that assert on logs
# attach their own handler.
logging.getLogger("custom_components").setLevel(logging.WARNING)


# --------------------------------------------------------------------------
# Frozen time
# --------------------------------------------------------------------------
class FrozenDatetime(datetime):
    """datetime subclass whose now()/utcnow()/today() return a fixed instant."""

    instant: datetime = datetime(2026, 3, 20, 12, 0, 0, tzinfo=timezone.utc)

    @classmethod
    def now(cls, tz=None):
        if tz is None:
            # like the real datetime.now(): naive local time for the instant
            return cls.instant.astimezone().replace(tzinfo=None)
        return cls.instant.astimezone(tz)

    @classmethod
    def utcnow(cls):
        return cls.instant.replace(tzinfo=None)

    @classmethod
    def today(cls):
        return cls.now()


@pytest.fixture
def freeze(monkeypatch, discovered):
    """Return a function that freezes "now" for every calendar module.

    Covers the three clocks the plugins use: the module-level ``datetime``
    class, ``time.time`` and Home Assistant's ``dt_util.now()``.
    """
    dt_mod = importlib.import_module("homeassistant.util.dt")
    modules = [m for n, m in list(sys.modules.items())
               if n.startswith(f"{INTEGRATION}.calendars.") and m is not None]

    patched = False

    def _set(instant: datetime) -> None:
        nonlocal patched
        FrozenDatetime.instant = instant
        if patched:
            return
        for mod in modules:
            if getattr(mod, "datetime", None) is datetime:
                monkeypatch.setattr(mod, "datetime", FrozenDatetime)
        monkeypatch.setattr(time, "time", lambda: FrozenDatetime.instant.timestamp())
        monkeypatch.setattr(dt_mod, "now", lambda: FrozenDatetime.instant.astimezone(HA_TZ))
        patched = True

    return _set


# --------------------------------------------------------------------------
# Fixtures
# --------------------------------------------------------------------------
@pytest.fixture(scope="session")
def sensor_module():
    return importlib.import_module(f"{INTEGRATION}.sensor")


@pytest.fixture(scope="session")
def discovered(sensor_module):
    """All discovered calendars, keyed by CALENDAR_INFO['id']."""
    return sensor_module.discover_calendars()


@pytest.fixture(scope="session")
def module_names(sensor_module, discovered):
    return dict(sensor_module._CALENDAR_MODULE_NAMES)


@pytest.fixture(autouse=True, scope="session")
def test_entry(sensor_module):
    """A config entry the sensors can read their options from."""
    entry = FakeConfigEntry(TEST_ENTRY_ID)
    sensor_module._CONFIG_ENTRIES[TEST_ENTRY_ID] = entry
    yield entry
    sensor_module._CONFIG_ENTRIES.pop(TEST_ENTRY_ID, None)


@pytest.fixture
def fake_hass():
    return FakeHass()


@pytest.fixture
def make_sensor(sensor_module, module_names):
    """Factory: instantiate the sensor class of a calendar id with a fake hass."""

    def _make(calendar_id: str, base_name: str = "Alternative Time"):
        mod = importlib.import_module(
            f".calendars.{module_names.get(calendar_id, calendar_id)}", package=INTEGRATION
        )
        cls = next(
            v for v in vars(mod).values()
            if isinstance(v, type)
            and issubclass(v, sensor_module.AlternativeTimeSensorBase)
            and v is not sensor_module.AlternativeTimeSensorBase
        )
        entity = cls(base_name, FakeHass())
        entity.hass = entity._hass
        entity._calendar_id = calendar_id
        entity._config_entry_id = TEST_ENTRY_ID
        return entity

    return _make


class LogCapture(logging.Handler):
    """Collect log records from the integration's logger tree."""

    def __init__(self):
        super().__init__(level=logging.DEBUG)
        self.records: list[logging.LogRecord] = []

    def emit(self, record):
        self.records.append(record)

    def count(self, level: int, needle: str = "") -> int:
        return sum(1 for r in self.records if r.levelno == level and needle in r.getMessage())


@pytest.fixture
def caplog_integration():
    logger = logging.getLogger("custom_components.alternative_time")
    handler = LogCapture()
    previous = logger.level
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    try:
        yield handler
    finally:
        logger.removeHandler(handler)
        logger.setLevel(previous)


def run(coro):
    """Run a coroutine to completion (tests stay sync; no pytest-asyncio needed)."""
    return asyncio.run(coro)
