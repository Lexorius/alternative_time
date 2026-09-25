"""Test scaffolding: run the integration without a Home Assistant install.

Everything under ``homeassistant.*`` is served by a permissive stub module
(attribute access yields a MagicMock), except the handful of names the
integration *subclasses* or *calls with real semantics*, which are provided
as small real classes/functions below. ``voluptuous`` is stubbed as well.

This makes the tests fast (no HA bootstrap) and independent of the HA
version installed on the developer machine or CI runner. They exercise the
integration's own logic — discovery, scheduling, error handling, recorder
behaviour, translations — not HA itself.
"""
from __future__ import annotations

import asyncio
import importlib
import importlib.abc
import importlib.machinery
import logging
import sys
import types
from pathlib import Path
from unittest.mock import MagicMock

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

INTEGRATION = "custom_components.alternative_time"


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
    def suggested_object_id(self):
        return getattr(self, "_attr_name", None)

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
    time_zone = "Europe/Berlin"

    def path(self, *parts):
        import tempfile
        return str(Path(tempfile.gettempdir(), *parts))


class FakeHass:
    """Runs executor jobs inline and tasks on the current loop."""

    config = FakeConfig()

    async def async_add_executor_job(self, fn, *args):
        return fn(*args)

    def async_create_task(self, coro):
        return asyncio.get_event_loop().create_task(coro)


# --------------------------------------------------------------------------
# Stub loader for homeassistant.* (and voluptuous)
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
    PREFIXES = ("homeassistant",)

    def find_spec(self, fullname, path=None, target=None):
        if fullname in self.PREFIXES or fullname.startswith(tuple(p + "." for p in self.PREFIXES)):
            return importlib.machinery.ModuleSpec(fullname, _StubLoader(), is_package=True)
        return None


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
    sys.modules.setdefault("voluptuous", MagicMock(name="voluptuous"))


install_ha_stub()

# Keep plugin DEBUG noise out of test output; tests that assert on logs
# attach their own handler.
logging.getLogger("custom_components").setLevel(logging.WARNING)


# --------------------------------------------------------------------------
# Fixtures
# --------------------------------------------------------------------------
@pytest.fixture(scope="session")
def sensor_module():
    return importlib.import_module(f"{INTEGRATION}.sensor")


@pytest.fixture(scope="session")
def discovered(sensor_module):
    """All discovered calendars, keyed by CALENDAR_INFO['id']."""
    return sensor_module.export_discovered_calendars()


@pytest.fixture(scope="session")
def module_names(sensor_module, discovered):
    return dict(sensor_module._CALENDAR_MODULE_NAMES)


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
        entity._config_entry_id = "test-entry"
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
