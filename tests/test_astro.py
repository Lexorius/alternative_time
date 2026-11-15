"""astro.py against published values (moon phases, Chinese calendar dates)."""
from __future__ import annotations

import importlib
from datetime import date, datetime, timezone

import pytest
from conftest import INTEGRATION

astro = importlib.import_module(f"{INTEGRATION}.astro")
U = timezone.utc


def _minutes(a: datetime, b: datetime) -> float:
    return abs((a - b).total_seconds()) / 60.0


def test_julian_day_round_trip():
    assert astro.julian_day(datetime(2000, 1, 1, 12, tzinfo=U)) == 2451545.0
    assert astro.julian_day(datetime(2026, 3, 20, 12, tzinfo=U)) == 2461120.0
    assert astro.from_julian_day(2451545.0) == datetime(2000, 1, 1, 12, tzinfo=U)
    # before 1970 (negative Unix time) must work too
    assert astro.from_julian_day(2415020.5) == datetime(1900, 1, 1, tzinfo=U)


@pytest.mark.parametrize("when", [
    datetime(2024, 2, 9, 22, 59, tzinfo=U),
    datetime(2025, 1, 29, 12, 36, tzinfo=U),
    datetime(2025, 12, 20, 1, 43, tzinfo=U),
    datetime(2026, 1, 18, 19, 52, tzinfo=U),
    datetime(2026, 2, 17, 12, 1, tzinfo=U),
    datetime(2026, 3, 19, 1, 23, tzinfo=U),
])
def test_new_moons_within_minutes(when):
    k = astro.lunation_index(astro.julian_day(when) + 1.0)
    assert _minutes(astro.from_julian_day(astro.moon_phase_jd(k)), when) < 5


@pytest.mark.parametrize("when", [
    datetime(2023, 5, 5, 17, 34, tzinfo=U),
    datetime(2024, 5, 23, 13, 53, tzinfo=U),
    datetime(2025, 5, 12, 16, 56, tzinfo=U),
    datetime(2026, 5, 1, 17, 23, tzinfo=U),
])
def test_full_moons_within_minutes(when):
    assert _minutes(astro.from_julian_day(astro.nearest_full_moon_jd(astro.julian_day(when))), when) < 5


def test_longitude_series_agree_with_phase_times():
    """Two independent methods: at a Meeus new/full moon the low-precision
    Sun/Moon series must put the elongation near 0 / 180 degrees."""
    for k in range(320, 336):
        new = astro.moon_elongation(astro.moon_phase_jd(k))
        full = astro.moon_elongation(astro.moon_phase_jd(k + 0.5))
        assert min(new, 360.0 - new) < 0.6, (k, new)
        assert abs(full - 180.0) < 0.6, (k, full)


def test_illumination_extremes():
    k = astro.lunation_index(astro.julian_day(datetime(2026, 3, 25, tzinfo=U)))
    assert astro.moon_illumination(astro.moon_phase_jd(k)) < 0.01
    assert astro.moon_illumination(astro.moon_phase_jd(k + 0.5)) > 0.99


def test_december_solstice():
    jd = astro.sun_longitude_crossing(270.0, astro.julian_day(datetime(2025, 12, 21, tzinfo=U)))
    assert _minutes(astro.from_julian_day(jd), datetime(2025, 12, 21, 15, 3, tzinfo=U)) < 30


@pytest.mark.parametrize("day,expected", [
    # Chinese New Year (month 1, day 1)
    (date(2023, 1, 22), (2023, 1, False, 1)),
    (date(2024, 2, 10), (2024, 1, False, 1)),
    (date(2025, 1, 29), (2025, 1, False, 1)),
    (date(2026, 2, 17), (2026, 1, False, 1)),
    (date(2027, 2, 6), (2027, 1, False, 1)),
    (date(2028, 1, 26), (2028, 1, False, 1)),
    # the day before New Year still belongs to the old year
    (date(2026, 2, 16), (2025, 12, False, 29)),
    (date(2026, 1, 15), (2025, 11, False, 27)),
    # leap months: second month of 2023, sixth month of 2025
    (date(2023, 4, 1), (2023, 2, True, 11)),
    (date(2025, 8, 1), (2025, 6, True, 8)),
    # festivals
    (date(2025, 10, 6), (2025, 8, False, 15)),   # Mid-Autumn 2025 (after the leap month)
    (date(2026, 6, 19), (2026, 5, False, 5)),    # Dragon Boat 2026
    (date(2026, 9, 25), (2026, 8, False, 15)),   # Mid-Autumn 2026
    (date(2026, 3, 20), (2026, 2, False, 2)),
])
def test_lunisolar_date_china(day, expected):
    assert astro.lunisolar_date(day, 8.0) == expected


def test_moon_quarter_on():
    assert astro.moon_quarter_on(date(2026, 5, 1), 0.0) == 2      # full moon 17:23 UTC
    assert astro.moon_quarter_on(date(2026, 3, 19), 0.0) == 0     # new moon 01:23 UTC
    assert astro.moon_quarter_on(date(2026, 5, 5), 0.0) is None


@pytest.mark.parametrize("when", [
    datetime(2021, 2, 7, 12, tzinfo=U),    # start of Mars Year 36
    datetime(2022, 12, 26, 12, tzinfo=U),  # Mars Year 37
    datetime(2024, 11, 12, 12, tzinfo=U),  # Mars Year 38
    datetime(2026, 9, 30, 12, tzinfo=U),   # Mars Year 39
])
def test_mars_year_starts_at_ls_zero(when):
    """A Mars year starts at the northern spring equinox (Ls = 0)."""
    ls = astro.mars_solar_longitude(when)
    assert min(ls, 360.0 - ls) < 1.0, ls


def test_mars_sol_date_reference():
    # MSD 44796.0 is 2000-01-06 00:00 UTC (to within the TT-UTC offset)
    assert astro.mars_sol_date(datetime(2000, 1, 6, tzinfo=U)) == pytest.approx(44796.0, abs=0.001)
