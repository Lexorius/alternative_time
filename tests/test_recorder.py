"""Recorder footprint: what the integration writes per state change (v2.6.2).

Home Assistant only creates a `states` row when the state string OR the
attributes change (StateMachine.async_set: same_state and same_attr -> no
state_changed event). Time is frozen for these tests so they are
deterministic — no minute/beat boundary can be crossed by accident.

1. every plugin's update() runs without raising (this is how the five
   `_get_plugin_options` AttributeErrors would have been caught);
2. two updates at the *same* instant produce identical state + attributes
   (catches counters, random picks and wall-clock timestamps in attributes);
3. plugins whose displayed value has minute/beat resolution must not change
   between T and T+1.1 s (attribute churn regression, v2.6.2);
4. no fast plugin outside the known second-clocks changes per tick;
5. the options-flow entity-id migration planner and the per-entry registry.
"""
from __future__ import annotations

import importlib
import json
import sys
import time
import zoneinfo
from datetime import datetime, timedelta, timezone

import pytest
from conftest import INTEGRATION, FakeHass

# Plugins whose state has minute/beat/10-s resolution: attributes must be
# quantised to the same resolution (v2.6.2).
CHURN_FIXED = {"dtg", "german_rescue_dtg", "swatch", "stardate"}

# Genuine second-resolution clocks: a row per tick is by design.
SECOND_CLOCKS = {
    "decimal", "eve", "hexadecimal", "julian_date", "mass_effect",
    "sidereal", "tai", "timezone", "unix", "ut1",
}

# Frozen instant. Chosen so that +1.1 s crosses no boundary that any of the
# CHURN_FIXED plugins care about:
#   minute:  :20 -> :21.1                       (dtg, german_rescue_dtg, stardate)
#   beat:    BMT = UTC+1 -> 13:00:20 = 46820 s since BMT midnight
#            46820 / 86.4 = 541.90 -> 77.6 s into the beat, +1.1 s < 86.4  (swatch)
FROZEN = datetime(2026, 3, 15, 12, 0, 20, tzinfo=timezone.utc)


class FrozenDatetime(datetime):
    """datetime subclass whose now()/utcnow()/today() return a fixed instant."""

    instant: datetime = FROZEN  # aware UTC

    @classmethod
    def now(cls, tz=None):
        if tz is None:
            # like the real datetime.now(): naive *local* time for the instant
            return cls.instant.astimezone().replace(tzinfo=None)
        return cls.instant.astimezone(tz)

    @classmethod
    def utcnow(cls):
        return cls.instant.replace(tzinfo=None)

    @classmethod
    def today(cls):
        return cls.now()


def _calendar_modules():
    return [m for n, m in list(sys.modules.items())
            if n.startswith(f"{INTEGRATION}.calendars.") and m is not None]


@pytest.fixture
def frozen_time(monkeypatch):
    """Freeze datetime.now/utcnow/today and time.time in every calendar module."""
    def _set(instant: datetime):
        FrozenDatetime.instant = instant
        for mod in _calendar_modules():
            if getattr(mod, "datetime", None) in (datetime, FrozenDatetime):
                monkeypatch.setattr(mod, "datetime", FrozenDatetime)
        monkeypatch.setattr(time, "time", lambda: instant.timestamp())
    _set(FROZEN)
    return _set


@pytest.fixture(scope="module")
def entities():
    """One instance per discovered calendar (import triggers module loading)."""
    sensor_module = importlib.import_module(f"{INTEGRATION}.sensor")
    discovered = sensor_module.export_discovered_calendars()
    module_names = dict(sensor_module._CALENDAR_MODULE_NAMES)
    out = {}
    for cid in sorted(discovered):
        mod = importlib.import_module(f".calendars.{module_names.get(cid, cid)}", package=INTEGRATION)
        cls = next(v for v in vars(mod).values()
                   if isinstance(v, type) and issubclass(v, sensor_module.AlternativeTimeSensorBase)
                   and v is not sensor_module.AlternativeTimeSensorBase)
        e = cls("Alternative Time", FakeHass())
        e.hass = e._hass
        e._calendar_id = cid
        e._config_entry_id = "test-entry"
        out[cid] = (e, discovered[cid])
    return out


def _snapshot(entity):
    return entity.state, dict(entity.extra_state_attributes or {})


def _update(entity):
    """Run update(); returns (snapshot, None) or (None, skip-reason)."""
    try:
        entity.update()
    except zoneinfo.ZoneInfoNotFoundError as exc:  # no tz database on this machine
        return None, repr(exc)
    return _snapshot(entity), None


def _diff(a, b):
    (s1, a1), (s2, a2) = a, b
    attrs = sorted(k for k in set(a1) | set(a2) if a1.get(k) != a2.get(k))
    return {"state": s1 != s2, "attrs": attrs} if (s1 != s2 or attrs) else None


# ------------------------------------------------------------------ tests --
def test_every_plugin_update_runs(entities, frozen_time):
    errors = {}
    for cid, (e, _) in entities.items():
        try:
            e.update()
        except zoneinfo.ZoneInfoNotFoundError:
            continue
        except Exception as exc:  # noqa: BLE001
            errors[cid] = repr(exc)
    assert not errors, json.dumps(errors, indent=2)


def test_same_instant_twice_is_identical(entities, frozen_time):
    """No counters, random picks or wall-clock timestamps in state/attributes."""
    changed = {}
    for cid, (e, _) in entities.items():
        first, skip = _update(e)
        if skip:
            continue
        second, _ = _update(e)
        if (d := _diff(first, second)):
            changed[cid] = d
    assert not changed, json.dumps(changed, indent=2)


def test_churn_fixed_plugins_do_not_change_within_a_second(entities, frozen_time):
    changed = {}
    for cid in sorted(CHURN_FIXED):
        e, _ = entities[cid]
        frozen_time(FROZEN)
        first, skip = _update(e)
        if skip:
            continue
        frozen_time(FROZEN + timedelta(seconds=1.1))
        second, _ = _update(e)
        if (d := _diff(first, second)):
            changed[cid] = d
    assert not changed, json.dumps(changed, indent=2)


def test_only_second_clocks_change_per_tick(entities, frozen_time):
    """Documents which fast plugins write a row per tick; catches new churn."""
    unexpected = {}
    for cid, (e, info) in entities.items():
        if info.get("update_interval", 3600) > 10 or cid in SECOND_CLOCKS:
            continue
        frozen_time(FROZEN)
        first, skip = _update(e)
        if skip:
            continue
        frozen_time(FROZEN + timedelta(seconds=1.1))
        second, _ = _update(e)
        if (d := _diff(first, second)):
            unexpected[cid] = d
    assert not unexpected, f"new per-tick churn: {json.dumps(unexpected, indent=2)}"


def test_attribute_payload_is_bounded(entities, frozen_time):
    """Attributes are not recorded (MATCH_ALL) but keep the live payload sane.

    solar_system is ~23 KB with the SVG; with Pillow installed the PNG data
    URI adds more. 256 KB is a sanity bound, not a design target.
    """
    big = {}
    for cid, (e, _) in entities.items():
        snap, skip = _update(e)
        if skip:
            continue
        size = len(json.dumps(snap[1], default=str))
        if size > 256 * 1024:
            big[cid] = size
    assert not big, big


# ---------------------------------------------------- entity-id migration --
def test_plan_entity_id_migration():
    cf = importlib.import_module(f"{INTEGRATION}.config_flow")
    taken = {"sensor.alternative_time_swatch"}

    def generate(cid, current):
        base = f"sensor.alternative_time_{cid}"
        cand, n = base, 2
        while cand in taken and cand != current:
            cand, n = f"{base}_{n}", n + 1
        return cand

    pairs = [
        ("sensor.beat_swatch_internet_zeit", "swatch"),           # collides -> _2
        ("sensor.graph_sonnensystem_positionen", "solar_system"),
        ("sensor.alternative_time_lunar_time", "lunar_time"),     # already migrated
        ("", "stardate"),                                         # not added yet
        ("sensor.x_dtg", None),                                   # no calendar id
    ]
    assert cf.plan_entity_id_migration(pairs, generate) == [
        ("sensor.beat_swatch_internet_zeit", "sensor.alternative_time_swatch_2"),
        ("sensor.graph_sonnensystem_positionen", "sensor.alternative_time_solar_system"),
    ]


def test_entities_for_entry_registry(sensor_module, make_sensor):
    sensor_module._ENTITIES_BY_ENTRY.clear()
    e1 = make_sensor("unix")
    e1.entity_id = "sensor.a"
    e2 = make_sensor("tai")
    e2.entity_id = None  # not added to HA yet
    sensor_module._ENTITIES_BY_ENTRY["entry1"] = [e1, e2]
    assert sensor_module.entities_for_entry("entry1") == [("sensor.a", "unix")]
    sensor_module.forget_config_entry("entry1")
    assert sensor_module.entities_for_entry("entry1") == []
