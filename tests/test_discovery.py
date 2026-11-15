"""Calendar discovery and sensor setup.

Every calendar id maps to an importable module with a sensor class
(v2.6.0.7: three calendars whose id differs from the file name never created
a sensor), and setup gives every sensor the stable entity_id the recorder
glob in the README relies on.
"""
from __future__ import annotations

import importlib

import pytest
from conftest import INTEGRATION, FakeConfigEntry, FakeHass, run

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


def test_setup_creates_every_sensor_with_stable_ids(sensor_module, discovered):
    """async_setup_entry: one sensor per configured calendar, each with the
    entity_id sensor.alternative_time_<calendar_id> and a per-entry unique_id."""
    entry = FakeConfigEntry("entry-setup", {
        "name": "Whatever The User Typed",
        "calendars": sorted(discovered),
        "calendar_options": {},
    })
    added = []
    try:
        run(sensor_module.async_setup_entry(FakeHass(), entry, added.extend))
        assert len(added) == len(discovered)
        by_calendar = {e._calendar_id: e for e in added}
        assert set(by_calendar) == set(discovered)
        wrong = {cid: e.entity_id for cid, e in by_calendar.items()
                 if e.entity_id != f"sensor.alternative_time_{cid}"}
        assert not wrong, wrong
        unique_ids = [e.unique_id for e in added]
        assert all(uid and uid.startswith("entry-setup_") for uid in unique_ids)
        assert len(set(unique_ids)) == len(unique_ids)
        assert len(sensor_module.entities_for_entry("entry-setup")) == len(discovered)
    finally:
        sensor_module.forget_config_entry("entry-setup")


def test_setup_skips_calendars_that_no_longer_exist(sensor_module):
    entry = FakeConfigEntry("entry-gone", {"name": "X", "calendars": ["test_debug", "unix"]})
    added = []
    try:
        run(sensor_module.async_setup_entry(FakeHass(), entry, added.extend))
        assert [e._calendar_id for e in added] == ["unix"]
    finally:
        sensor_module.forget_config_entry("entry-gone")


def test_language_matching_is_the_same_everywhere():
    """Sensors and config flow must resolve "zh-Hans" / "pt-BR" the same way."""
    i18n = importlib.import_module(f"{INTEGRATION}.i18n")
    cf = importlib.import_module(f"{INTEGRATION}.config_flow")
    texts = {"en": "English", "zh": "中文", "pt": "Português"}
    for lang, expected in [("zh-Hans", "中文"), ("pt-BR", "Português"), ("pt", "Português"),
                           ("en-GB", "English"), ("xx", "English")]:
        assert i18n.pick_language(texts, lang) == expected
        assert cf.lcal({"label": texts}, "label", lang, "key") == expected
    assert cf.lcal({"label": {"de": "nur deutsch"}}, "label", "fr", "key") == "key"
