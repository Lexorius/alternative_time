"""Alternative Time inside a real Home Assistant core.

Covers what the stub-based suite in ``tests/`` cannot see: the ids the entity
registry hands out, the setup wizard, the options dialog and the entity id
migration. (The migration called a Home Assistant function that does not
exist; only a real core could show that.)
"""
import logging

import pytest

pytest.importorskip("pytest_homeassistant_custom_component")

from homeassistant import config_entries  # noqa: E402
from homeassistant.data_entry_flow import FlowResultType  # noqa: E402
from homeassistant.helpers import entity_registry as er  # noqa: E402
from homeassistant.setup import async_setup_component  # noqa: E402
from pytest_homeassistant_custom_component.common import MockConfigEntry  # noqa: E402

from custom_components.alternative_time import config_flow  # noqa: E402
from custom_components.alternative_time import sensor as at_sensor  # noqa: E402

DOMAIN = "alternative_time"
PREFIX = "sensor.alternative_time_"
NEEDS_NETWORK = {PREFIX + "ut1"}  # sockets are blocked in the test harness
DEAD = ("unknown", "unavailable", "")


async def _discovered(hass):
    return await hass.async_add_executor_job(at_sensor.discover_calendars)


async def _setup(hass, title, calendars, options=None):
    entry = MockConfigEntry(
        domain=DOMAIN, title=title,
        data={"name": title, "calendars": list(calendars), "calendar_options": options or {}},
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    assert entry.state is config_entries.ConfigEntryState.LOADED
    return entry


async def _unload(hass, entry):
    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()


def _entity_ids(hass, entry):
    registry = er.async_get(hass)
    return {e.entity_id for e in er.async_entries_for_config_entry(registry, entry.entry_id)}


def _broken_states(hass, entity_ids):
    bad = {}
    for entity_id in sorted(entity_ids):
        state = hass.states.get(entity_id)
        value = None if state is None else state.state
        if value is None or value in DEAD or "error" in value.lower() or "missing" in value.lower():
            bad[entity_id] = value
    return {k: v for k, v in bad.items() if k not in NEEDS_NETWORK}


def _errors(caplog):
    return [
        f"{r.name}: {r.getMessage()[:200]}" for r in caplog.records
        if r.levelno >= logging.ERROR and "ut1" not in r.name
    ]


async def _open_options_step(hass, entry, step):
    options = hass.config_entries.options
    result = await options.async_init(entry.entry_id)
    assert result["type"] is FlowResultType.MENU
    assert result["menu_options"] == ["select_calendar", "migrate_entity_ids"]
    return await options.async_configure(result["flow_id"], {"next_step_id": step})


# --------------------------------------------------------------------------
# Setup and entity ids
# --------------------------------------------------------------------------
async def test_all_calendars_set_up_with_fixed_ids(hass, caplog):
    """Every calendar becomes sensor.alternative_time_<id>, whatever the entry is called."""
    ids = sorted(await _discovered(hass))
    caplog.set_level(logging.WARNING)
    entry = await _setup(hass, "Meine Zeiten im Wohnzimmer", ids)

    got = _entity_ids(hass, entry)
    assert got == {PREFIX + cid for cid in ids}
    assert not _broken_states(hass, got)
    assert not _errors(caplog), _errors(caplog)
    await _unload(hass, entry)


async def test_second_entry_gets_numbered_ids(hass):
    first = await _setup(hass, "Eins", ["unix", "mars"])
    second = await _setup(hass, "Zwei", ["unix"])
    assert _entity_ids(hass, second) == {PREFIX + "unix_2"}
    await _unload(hass, second)
    await _unload(hass, first)


async def test_existing_entities_keep_their_id_after_reload(hass):
    """Upgrade path: an id that is already in the registry is never overwritten."""
    entry = await _setup(hass, "Alt", ["unix", "swatch"])
    er.async_get(hass).async_update_entity(PREFIX + "unix", new_entity_id="sensor.alt_unix_zeit")
    await hass.async_block_till_done()
    assert hass.states.get("sensor.alt_unix_zeit") is not None

    assert await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()
    assert _entity_ids(hass, entry) == {"sensor.alt_unix_zeit", PREFIX + "swatch"}
    assert hass.states.get("sensor.alt_unix_zeit").state not in DEAD
    await _unload(hass, entry)


async def test_removed_calendar_does_not_break_the_entry(hass):
    entry = await _setup(hass, "Weg", ["test_debug", "unix"])
    assert _entity_ids(hass, entry) == {PREFIX + "unix"}
    await _unload(hass, entry)


# --------------------------------------------------------------------------
# Setup wizard
# --------------------------------------------------------------------------
@pytest.mark.parametrize("language", ["en", "de", "zh-Hans", "pt-BR", "ja"])
async def test_setup_wizard(hass, language, caplog):
    """Click through the whole wizard, every calendar, every option form."""
    hass.config.language = language
    caplog.set_level(logging.WARNING)
    discovered = await _discovered(hass)
    by_category = {}
    for cid, info in discovered.items():
        by_category.setdefault(config_flow._category(info), []).append(cid)
    categories = [c for c in config_flow.FIXED_CATEGORY_ORDER if c in by_category]

    flow = hass.config_entries.flow
    result = await flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})
    assert result["type"] is FlowResultType.FORM and result["step_id"] == "user"
    result = await flow.async_configure(result["flow_id"], {"name": f"Wizard {language}"})
    assert result["step_id"] == "select_categories"
    result = await flow.async_configure(result["flow_id"], {"categories": categories})

    seen = []
    while result["type"] is FlowResultType.FORM and result["step_id"] == "select_calendars_by_category":
        category = result["description_placeholders"]["category"].lower()
        seen.append(category)
        result = await flow.async_configure(result["flow_id"], {"calendars": sorted(by_category[category])})
    assert seen == categories

    option_forms = 0
    while result["type"] is FlowResultType.FORM and result["step_id"] == "plugin_options":
        option_forms += 1
        assert result["description_placeholders"]["calendar_name"]
        result = await flow.async_configure(result["flow_id"], {})  # accept every default
    assert option_forms >= 20, option_forms

    assert result["type"] is FlowResultType.FORM and result["step_id"] == "disclaimer", result
    result = await flow.async_configure(result["flow_id"], {})
    assert result["type"] is FlowResultType.CREATE_ENTRY, result
    assert sorted(result["data"]["calendars"]) == sorted(discovered)
    assert len(result["data"]["calendar_options"]) == option_forms
    await hass.async_block_till_done()

    entry = result["result"]
    assert entry.state is config_entries.ConfigEntryState.LOADED
    got = _entity_ids(hass, entry)
    assert got == {PREFIX + cid for cid in discovered}
    assert not _broken_states(hass, got)
    assert not _errors(caplog), _errors(caplog)
    await _unload(hass, entry)


# --------------------------------------------------------------------------
# Options dialog
# --------------------------------------------------------------------------
async def test_options_dialog_changes_a_calendar(hass):
    discovered = await _discovered(hass)
    entry = await _setup(hass, "Opt", ["stardate", "unix"])
    before = hass.states.get(PREFIX + "stardate").state
    options = hass.config_entries.options

    result = await _open_options_step(hass, entry, "select_calendar")
    assert result["type"] is FlowResultType.FORM and result["step_id"] == "select_calendar"
    assert result["description_placeholders"] == {"title": "Opt"}
    result = await options.async_configure(result["flow_id"], {"calendar": "stardate"})
    assert result["type"] is FlowResultType.FORM and result["step_id"] == "configure_calendar"

    label = config_flow.lcal(
        discovered["stardate"]["config_options"]["format"], "label", hass.config.language, "format"
    )
    result = await options.async_configure(result["flow_id"], {label: "tos"})
    assert result["type"] is FlowResultType.CREATE_ENTRY
    await hass.async_block_till_done()

    assert entry.data["calendar_options"]["stardate"]["format"] == "tos"
    assert entry.data["calendars"] == ["stardate", "unix"]           # nothing else was dropped
    assert entry.state is config_entries.ConfigEntryState.LOADED     # reloaded by the update listener
    assert hass.states.get(PREFIX + "stardate").state != before

    # the dialog now offers the stored value as the default
    result = await _open_options_step(hass, entry, "select_calendar")
    result = await options.async_configure(result["flow_id"], {"calendar": "stardate"})
    defaults = {str(key): key.default() for key in result["data_schema"].schema}
    assert defaults[label] == "tos"
    options.async_abort(result["flow_id"])
    await _unload(hass, entry)


async def test_migrate_entity_ids(hass):
    assert await async_setup_component(hass, "persistent_notification", {})
    entry = await _setup(hass, "Mig", ["unix", "mars"])
    registry = er.async_get(hass)
    options = hass.config_entries.options

    # nothing to do while every id follows the scheme
    result = await _open_options_step(hass, entry, "migrate_entity_ids")
    assert result["type"] is FlowResultType.ABORT and result["reason"] == "nothing_to_migrate"

    registry.async_update_entity(PREFIX + "unix", new_entity_id="sensor.mig_unix_zeit")
    await hass.async_block_till_done()

    result = await _open_options_step(hass, entry, "migrate_entity_ids")
    assert result["type"] is FlowResultType.FORM and result["step_id"] == "migrate_entity_ids"
    assert result["description_placeholders"]["count"] == "1"
    assert "sensor.mig_unix_zeit" in result["description_placeholders"]["preview"]
    result = await options.async_configure(result["flow_id"], {})
    assert result["type"] is FlowResultType.ABORT and result["reason"] == "migration_done"
    await hass.async_block_till_done()

    assert registry.async_get("sensor.mig_unix_zeit") is None
    assert _entity_ids(hass, entry) == {PREFIX + "unix", PREFIX + "mars"}
    assert hass.states.get(PREFIX + "unix").state not in DEAD
    await _unload(hass, entry)


async def test_migration_steps_aside_when_the_id_is_taken(hass):
    assert await async_setup_component(hass, "persistent_notification", {})
    old = await _setup(hass, "Alt", ["unix"])
    er.async_get(hass).async_update_entity(PREFIX + "unix", new_entity_id="sensor.alt_unix_zeit")
    await hass.async_block_till_done()
    new = await _setup(hass, "Neu", ["unix"])          # takes the free sensor.alternative_time_unix
    assert _entity_ids(hass, new) == {PREFIX + "unix"}

    result = await _open_options_step(hass, old, "migrate_entity_ids")
    assert PREFIX + "unix_2" in result["description_placeholders"]["preview"]
    result = await hass.config_entries.options.async_configure(result["flow_id"], {})
    assert result["reason"] == "migration_done"
    await hass.async_block_till_done()

    assert _entity_ids(hass, old) == {PREFIX + "unix_2"}
    assert _entity_ids(hass, new) == {PREFIX + "unix"}
    await _unload(hass, new)
    await _unload(hass, old)
