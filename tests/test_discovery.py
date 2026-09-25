"""Calendar discovery: every id maps to an importable module with a sensor class.

Regression for v2.6.0.7 #3 (three calendars whose CALENDAR_INFO['id'] differs
from the file name were selectable but never created a sensor), #7 (test_debug
shipped as a real calendar) and #1 (stable entity_id via suggested_object_id).
"""
from __future__ import annotations

import importlib

import pytest
from conftest import INTEGRATION

EXPECTED_ID_TO_MODULE = {
    "suriyakati_thai": "suriyakati",
    "minguo_taiwan": "minguo",
    "julian_date": "julian",
}


def test_discovery_finds_calendars(discovered):
    assert len(discovered) >= 45, f"only {len(discovered)} calendars discovered"


def test_debug_tooling_is_not_a_calendar(discovered):
    assert "test_debug" not in discovered


@pytest.mark.parametrize("calendar_id,module_name", EXPECTED_ID_TO_MODULE.items())
def test_id_differs_from_module_name_is_mapped(module_names, calendar_id, module_name):
    assert module_names.get(calendar_id) == module_name


def test_every_discovered_id_imports_and_has_sensor_class(sensor_module, discovered, module_names):
    failures = []
    for calendar_id in sorted(discovered):
        module_name = module_names.get(calendar_id, calendar_id)
        try:
            mod = importlib.import_module(f".calendars.{module_name}", package=INTEGRATION)
        except Exception as exc:  # noqa: BLE001
            failures.append(f"{calendar_id}: import failed: {exc!r}")
            continue
        has_cls = any(
            isinstance(v, type)
            and issubclass(v, sensor_module.AlternativeTimeSensorBase)
            and v is not sensor_module.AlternativeTimeSensorBase
            for v in vars(mod).values()
        )
        if not has_cls:
            failures.append(f"{calendar_id}: no AlternativeTimeSensorBase subclass")
    assert not failures, "\n".join(failures)


def test_calendar_info_has_required_keys(discovered):
    required = {"id", "version", "icon", "category", "name", "description", "update_interval"}
    missing = {cid: sorted(required - set(info)) for cid, info in discovered.items() if required - set(info)}
    assert not missing, missing


def test_every_calendar_has_en_and_de_names(discovered):
    bad = [cid for cid, info in discovered.items()
           if not ({"en", "de"} <= set(info.get("name", {})))]
    assert not bad, bad


def test_config_options_selects_are_lists(discovered):
    """A select's options must be a list (v2.6.0.7 fixed two malformed ones)."""
    bad = []
    for cid, info in discovered.items():
        for key, meta in (info.get("config_options") or {}).items():
            if meta.get("type") == "select" and not isinstance(meta.get("options"), list):
                bad.append(f"{cid}.{key}: {type(meta.get('options')).__name__}")
    assert not bad, bad


def test_no_plugin_uses_legacy_plugin_options_key(discovered):
    assert not [cid for cid, info in discovered.items() if "plugin_options" in info]


def test_suggested_object_id_uses_calendar_id(make_sensor):
    entity = make_sensor("suriyakati_thai", base_name="Irgendein Name")
    assert entity.suggested_object_id == "alternative_time_suriyakati_thai"
