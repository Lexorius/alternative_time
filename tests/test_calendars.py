"""Calendars against known answers, and every calendar on every day of a year.

The reference values are published facts (Julian Dates, Mars landing sols,
the Darian dates of Mars missions, moon phases, religious holidays), not
values taken from this code.
"""
from __future__ import annotations

import asyncio
import importlib
import re
import zoneinfo
from datetime import date, datetime, timedelta, timezone

import pytest
from conftest import INTEGRATION, REPO_ROOT, run

U = timezone.utc
CALENDARS_DIR = REPO_ROOT / "custom_components" / "alternative_time" / "calendars"


# --------------------------------------------------------------------------
# Every calendar, every day
# --------------------------------------------------------------------------
def _sweep_instants():
    out = []
    day = datetime(2024, 1, 1, 12, tzinfo=U)  # a leap year
    while day.year == 2024:
        out.append(day)
        day += timedelta(days=1)
    for y, m, d in [(2024, 2, 29), (2024, 12, 31), (2025, 1, 1), (2026, 12, 31), (2027, 1, 1), (2028, 2, 29)]:
        out += [datetime(y, m, d, 0, 0, 0, tzinfo=U), datetime(y, m, d, 23, 59, 59, tzinfo=U)]
    out += [datetime(2038, 1, 19, 3, 14, 8, tzinfo=U), datetime(2100, 3, 1, 12, tzinfo=U)]
    return out


def test_every_calendar_runs_on_every_day(discovered, make_sensor, freeze):
    """No calendar may raise or show an error state on any day.

    (The Warcraft calendar used to raise IndexError on 52 days a year.)
    """
    entities = {cid: make_sensor(cid) for cid in sorted(discovered)}
    entities["solar_system"]._enable_visualization = False  # no map files per step
    failures = {}
    for instant in _sweep_instants():
        freeze(instant)
        for cid, entity in entities.items():
            if cid in failures:
                continue
            try:
                entity.update()
                state = entity.state
                dict(entity.extra_state_attributes or {})
            except zoneinfo.ZoneInfoNotFoundError:  # no tz database on this machine
                continue
            except Exception as exc:  # noqa: BLE001
                failures[cid] = f"{instant:%Y-%m-%d %H:%M:%S}: {exc!r}"
                continue
            if state is None or "error" in str(state).lower():
                failures[cid] = f"{instant:%Y-%m-%d %H:%M:%S}: state {state!r}"
    assert not failures, failures


# --------------------------------------------------------------------------
# Options
# --------------------------------------------------------------------------
def test_every_calendar_with_options_loads_them(discovered, module_names):
    """Seven calendars once defined set_options() and never called anything."""
    missing = [
        cid for cid, info in discovered.items()
        if info.get("config_options")
        and "get_plugin_options(" not in (CALENDARS_DIR / f"{module_names[cid]}.py").read_text(encoding="utf-8")
    ]
    assert not missing, missing


def test_no_option_is_defined_but_never_read(discovered, module_names):
    dead = []
    for cid, info in discovered.items():
        source = (CALENDARS_DIR / f"{module_names[cid]}.py").read_text(encoding="utf-8")
        for key in info.get("config_options") or {}:
            if len(re.findall(r"""["']%s["']""" % re.escape(key), source)) < 2:
                dead.append(f"{cid}.{key}")
    assert not dead, dead


@pytest.mark.parametrize("calendar_id,key,value,attr", [
    ("stardate", "format", "tos", "_format"),
    ("discworld", "show_guild", False, "_show_guild"),
    ("eve", "show_nest", False, "_show_nest"),
    ("islamic", "offset_days", 1, "_offset_days"),
    ("rivendell", "show_yen", False, "_show_yen"),
    ("shire", "show_meals", False, "_show_meals"),
    ("tamriel", "show_moons", False, "_show_moons"),
])
def test_options_reach_the_sensor(calendar_id, key, value, attr, make_sensor, test_entry):
    test_entry.data = {"calendars": [calendar_id], "calendar_options": {calendar_id: {key: value}}}
    try:
        entity = make_sensor(calendar_id)
        assert getattr(entity, attr) != value, "probe value must differ from the default"

        async def start():
            await entity.async_added_to_hass()
            await asyncio.gather(*entity._hass.tasks)

        run(start())
        assert getattr(entity, attr) == value
    finally:
        test_entry.data = {"calendar_options": {}, "calendars": []}


# --------------------------------------------------------------------------
# Known answers
# --------------------------------------------------------------------------
@pytest.mark.parametrize("instant,expected", [
    (datetime(2000, 1, 1, 12, tzinfo=U), 2451545.0),   # J2000.0
    (datetime(2026, 3, 20, 0, tzinfo=U), 2461119.5),
    (datetime(2026, 3, 20, 12, tzinfo=U), 2461120.0),
])
def test_julian_date(make_sensor, freeze, instant, expected):
    entity = make_sensor("julian_date")
    freeze(instant)
    entity.update()
    attrs = entity.extra_state_attributes
    assert attrs["julian_date"] == pytest.approx(expected, abs=1e-6)
    assert attrs["julian_day_number"] == int(expected + 0.5)


@pytest.mark.parametrize("instant,sol", [
    (datetime(2012, 8, 6, 5, 17, 57, tzinfo=U), 49269),   # Curiosity landing = its Sol 0
    (datetime(2021, 2, 18, 20, 55, tzinfo=U), 52304),     # Perseverance landing = its Sol 0
])
def test_mars_sol_date(make_sensor, freeze, instant, sol):
    entity = make_sensor("mars")
    freeze(instant)
    entity.update()
    assert entity.extra_state_attributes["sol_number"] == sol


# Darian dates of Mars missions as published (Wikipedia, "Darian calendar")
@pytest.mark.parametrize("instant,expected", [
    (datetime(1965, 7, 15, 1, 0, 57, tzinfo=U), "26 Taurus 189"),      # Mariner 4 flyby
    (datetime(1976, 7, 20, 11, 53, tzinfo=U), "14 Mina 195"),          # Viking 1 landing
    (datetime(1997, 7, 4, 16, 57, tzinfo=U), "26 Taurus 206"),         # Pathfinder landing
    (datetime(2004, 1, 4, 4, 35, tzinfo=U), "26 Tula 209"),            # Spirit landing
    (datetime(2008, 5, 25, 23, 54, tzinfo=U), "25 Kumbha 212"),        # Phoenix landing
    (datetime(2012, 8, 6, 5, 17, tzinfo=U), "13 Rishabha 214"),        # Curiosity landing
    (datetime(2014, 9, 22, 2, 24, tzinfo=U), "18 Cancer 215"),         # MAVEN orbit insertion
    # (The published InSight row, "26 Kanya 217", contradicts its own sol
    #  number 145640, which is 28 Kanya; it is left out.)
    (datetime(1873, 12, 29, 0, 2, 53, tzinfo=U), "25 Virgo 140"),      # epoch of the Mars Sol Date
    (datetime(2021, 2, 18, 20, 55, tzinfo=U), "13 Sagittarius 219"),   # Perseverance landing
])
def test_darian_calendar(make_sensor, instant, expected):
    result = make_sensor("darian")._calculate_darian_date(instant)
    assert f"{result['sol']} {result['month_name']} {result['year']}" == expected


def test_darian_year_lengths(make_sensor, discovered):
    months = discovered["darian"]["darian_data"]["months"]
    assert len(months) == 24 and sum(m["sols"] for m in months) == 668
    assert [i + 1 for i, m in enumerate(months) if m["sols"] == 27] == [6, 12, 18, 24]
    leap = make_sensor("darian")._is_leap_year
    assert [leap(y) for y in (0, 1, 2, 10, 100, 200, 210, 221)] == [True, True, False, True, False, False, True, True]


def test_swatch_beats_have_no_daylight_saving(make_sensor):
    """Biel Mean Time is UTC+1 all year: 12:00 UTC is @541 in winter and summer."""
    entity = make_sensor("swatch")
    assert entity._calculate_swatch_time(datetime(2026, 1, 15, 12, tzinfo=U))["formatted"] == "@541"
    assert entity._calculate_swatch_time(datetime(2026, 7, 1, 12, tzinfo=U))["formatted"] == "@541"
    # the instant from a real log where the sensor showed @939
    assert entity._calculate_swatch_time(datetime(2026, 10, 2, 20, 33, 15, tzinfo=U))["formatted"] == "@898"


def test_islamic_weekday(make_sensor, freeze):
    entity = make_sensor("islamic")
    for instant in (datetime(2026, 3, 20, 12, tzinfo=U), datetime(2026, 11, 15, 12, tzinfo=U)):
        freeze(instant)
        entity.update()
        assert entity.extra_state_attributes["weekday_en"] == instant.strftime("%A")


def test_thai_zodiac(make_sensor):
    entity = make_sensor("suriyakati_thai")
    assert entity._calculate_thai_date(datetime(2024, 6, 15))["zodiac_english"] == "Dragon"
    assert entity._calculate_thai_date(datetime(2026, 6, 15))["zodiac_english"] == "Horse"


def test_thai_holy_days_follow_the_moon(make_sensor):
    entity = make_sensor("suriyakati_thai")
    # Makha Bucha 2026 is 3 March (full moon); 5 May is no full moon in any year
    assert "Full Moon" in entity._get_buddhist_day(datetime(2026, 3, 3))
    assert entity._get_buddhist_day(datetime(2026, 5, 5)) == ""
    assert "New Moon" in entity._get_buddhist_day(datetime(2026, 3, 19))


def test_lunar_time_illumination(make_sensor):
    entity = make_sensor("lunar_time")
    assert entity._calculate_lunar_phase(datetime(2026, 3, 19, 2, tzinfo=U))["illumination"] < 3    # new moon
    assert entity._calculate_lunar_phase(datetime(2026, 4, 2, 2, tzinfo=U))["illumination"] > 97    # full moon


def test_solar_system_seen_from_earth(make_sensor):
    entity = make_sensor("solar_system")

    saturn = entity._calculate_visibility("saturn", datetime(2026, 10, 4, tzinfo=U))    # opposition
    assert saturn["elongation"] > 170 and saturn["visible"]
    assert saturn["visibility_period"] == "All night"

    venus = entity._calculate_visibility("venus", datetime(2026, 8, 15, tzinfo=U))      # greatest eastern elongation
    assert 40 < venus["elongation"] < 48 and venus["visible"]
    assert venus["visibility_period"] == "Evening star"

    # A planet at opposition moves backwards; months later it does not
    assert entity._is_retrograde("jupiter", datetime(2026, 1, 10, tzinfo=U)) is True
    assert entity._is_retrograde("jupiter", datetime(2026, 6, 1, tzinfo=U)) is False
    assert entity._is_retrograde("mercury", datetime(2026, 3, 8, tzinfo=U)) is True      # 26 Feb - 20 Mar 2026
    assert entity._is_retrograde("earth", datetime(2026, 3, 8, tzinfo=U)) is False


def test_solar_system_picture_is_a_path_not_a_blob(make_sensor, freeze):
    entity = make_sensor("solar_system")
    freeze(datetime(2026, 3, 20, 12, tzinfo=U))
    entity.update()
    attrs = entity.extra_state_attributes
    assert "solar_system_map_svg" not in attrs and "solar_system_map_png" not in attrs
    assert "observer_location" not in attrs
    assert attrs["entity_picture"].startswith("/local/alternative_time/solar_system_map.svg?v=")


@pytest.mark.parametrize("instant,month,paksha,tithi,year", [
    (datetime(2026, 3, 20, 12, tzinfo=U), "Chaitra", "bright", "Dwitiya", 1948),             # day after Ugadi
    (datetime(2026, 5, 1, 12, tzinfo=U), "Vaisakha", "bright", "Purnima/Amavasya", 1948),    # Buddha Purnima
    (datetime(2026, 11, 8, 12, tzinfo=U), "Ashwin", "dark", "Purnima/Amavasya", 1948),       # Diwali (new moon)
    (datetime(2026, 1, 15, 12, tzinfo=U), "Pausha", "dark", None, 1947),                     # before the new year
])
def test_hindu_panchang(make_sensor, instant, month, paksha, tithi, year):
    try:
        result = make_sensor("hindu_panchang")._calculate_panchang(instant)
    except zoneinfo.ZoneInfoNotFoundError:
        pytest.skip("no tz database on this machine")
    assert (result["month_name"], result["paksha"], result["hindu_year"]) == (month, paksha, year)
    if tithi:
        assert result["tithi"] == tithi


def test_hindu_karana_table(make_sensor):
    karana = make_sensor("hindu_panchang")._calculate_karana
    assert [karana(h) for h in (0, 1, 7, 8, 56, 57, 58, 59)] == [10, 0, 6, 0, 6, 7, 8, 9]


@pytest.mark.parametrize("instant,lunar,zodiac", [
    (datetime(2026, 3, 20, 12, tzinfo=U), (2, 2, False), "Horse"),
    (datetime(2026, 1, 15, 12, tzinfo=U), (11, 27, False), "Snake"),     # before the lunar New Year
    (datetime(2025, 8, 1, 3, tzinfo=U), (6, 8, True), "Snake"),          # leap sixth month of 2025
])
def test_japanese_lunar(make_sensor, instant, lunar, zodiac):
    try:
        result = make_sensor("japanese_lunar")._calculate_japanese_lunar_date(instant)
    except zoneinfo.ZoneInfoNotFoundError:
        pytest.skip("no tz database on this machine")
    assert (result["lunar_month"], result["lunar_day"], result["is_leap_month"]) == lunar
    assert result["zodiac_en"] == zodiac


def test_stem_branch_year_starts_at_chinese_new_year(make_sensor):
    entity = make_sensor("sexagesimal")
    assert entity._calculate_cycle(datetime(2026, 1, 15, 12), "year")["cycle_name_english"] == "Wood-Snake"
    assert entity._calculate_cycle(datetime(2026, 3, 20, 12), "year")["cycle_name_english"] == "Fire-Horse"


# Officially proclaimed Sri Lankan Poya (full-moon) holidays
@pytest.mark.parametrize("poya", [
    date(2023, 1, 6), date(2023, 5, 5), date(2024, 1, 25), date(2024, 5, 23), date(2024, 12, 14),
    date(2025, 1, 13), date(2025, 5, 12), date(2025, 6, 10), date(2025, 7, 10), date(2025, 12, 4),
    date(2026, 5, 1),
])
def test_sri_lankan_poya_days(poya):
    module = importlib.import_module(f"{INTEGRATION}.calendars.sri_lanka_buddhist")
    found, _full_moon = module._next_poya_on_or_after(datetime(poya.year, poya.month, poya.day, tzinfo=U))
    assert found.date() == poya


# --------------------------------------------------------------------------
# Clocks in a named time zone (zoneinfo)
# --------------------------------------------------------------------------
def _options(test_entry, calendar_id, options):
    test_entry.data = {"calendars": [calendar_id], "calendar_options": {calendar_id: options}}


def _started(entity):
    async def start():
        await entity.async_added_to_hass()
        await asyncio.gather(*entity._hass.tasks)

    try:
        run(start())
    except zoneinfo.ZoneInfoNotFoundError:
        pytest.skip("no tz database on this machine")
    return entity


@pytest.mark.parametrize("instant,expected", [
    (datetime(2026, 1, 15, 12, tzinfo=U), "07:00:00 EST (UTC-5)"),
    (datetime(2026, 7, 1, 12, tzinfo=U), "08:00:00 EDT (UTC-4) DST"),
])
def test_world_clock_follows_daylight_saving(make_sensor, freeze, test_entry, instant, expected):
    _options(test_entry, "timezone", {"timezone": "America/New_York"})
    try:
        freeze(instant)
        entity = _started(make_sensor("timezone"))
        assert entity.state == expected  # already right on the first tick
    finally:
        test_entry.data = {"calendar_options": {}, "calendars": []}


def test_world_clock_survives_an_unknown_zone(make_sensor, freeze, test_entry):
    """An unknown zone name used to raise NameError while the entity was added."""
    _options(test_entry, "timezone", {"timezone": "Mars/Olympus_Mons"})
    try:
        freeze(datetime(2026, 7, 1, 12, tzinfo=U))
        entity = _started(make_sensor("timezone"))
        assert entity.state.startswith("12:00:00 UTC")
    finally:
        test_entry.data = {"calendar_options": {}, "calendars": []}


@pytest.mark.parametrize("options,expected,is_dst", [
    ({}, "011200Z JUL 26", False),                                   # Zulu
    ({"timezone": "R"}, "010700R JUL 26", False),                    # Romeo = UTC-5, fixed
    ({"timezone": "B", "use_iana_timezone": True, "iana_timezone": "Europe/Berlin"},
     "011400B JUL 26", True),                                        # Berlin in summer = UTC+2
])
def test_nato_dtg(make_sensor, freeze, test_entry, options, expected, is_dst):
    _options(test_entry, "dtg", options)
    try:
        freeze(datetime(2026, 7, 1, 12, tzinfo=U))
        entity = make_sensor("dtg")
        entity.update()
        assert entity.state == expected
        assert entity.extra_state_attributes["is_dst"] is is_dst
    finally:
        test_entry.data = {"calendar_options": {}, "calendars": []}


@pytest.mark.parametrize("instant,expected,abbreviation", [
    (datetime(2026, 1, 15, 12, tzinfo=U), "15 1300 JAN 2026", "CET"),
    (datetime(2026, 7, 1, 12, tzinfo=U), "01 1400 JUL 2026", "CEST"),
])
def test_german_rescue_dtg_uses_berlin_time(make_sensor, freeze, instant, expected, abbreviation):
    try:
        entity = make_sensor("german_rescue_dtg")
    except zoneinfo.ZoneInfoNotFoundError:
        pytest.skip("no tz database on this machine")
    freeze(instant)
    entity.update()
    assert entity.state == expected
    assert entity.extra_state_attributes["timezone_info"]["abbreviation"] == abbreviation
