"""Dependency-free astronomy helpers shared by the calendar plugins.

One place for the maths several calendars need: Julian Dates, real new and
full moons, Sun and Moon longitude, and the lunisolar (Chinese/Japanese)
calendar date. Standard library only.

Accuracy (checked against published values in tests/test_astro.py):
- new/full moon instants: a few minutes (Meeus, "Astronomical Algorithms",
  ch. 49, periodic terms without the planetary corrections)
- Sun longitude ~0.01 deg, Moon longitude ~0.3 deg (Astronomical Almanac
  low-precision series), so lunar-day boundaries are good to about half an
  hour. That is far inside what a wall-clock calendar sensor needs; it is not
  an ephemeris.
"""
from __future__ import annotations

import math
from datetime import date, datetime, timedelta, timezone
from functools import lru_cache

UNIX_EPOCH_JD = 2440587.5
J2000_JD = 2451545.0
SYNODIC_MONTH = 29.530588861

_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)
_NEW_MOON_K0_JDE = 2451550.09766  # new moon of 2000-01-06
# TT - UTC. 69.184 s since 2017 and no leap second is scheduled; one second
# more or less moves a moon phase by one second.
_DELTA_T_DAYS = 69.184 / 86400.0


# --------------------------------------------------------------------------
# Julian Date
# --------------------------------------------------------------------------
def julian_day(dt: datetime) -> float:
    """Julian Date (UTC) of a datetime. Naive datetimes are taken as UTC."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return UNIX_EPOCH_JD + (dt - _EPOCH).total_seconds() / 86400.0


def from_julian_day(jd: float) -> datetime:
    """UTC datetime of a Julian Date."""
    return _EPOCH + timedelta(days=jd - UNIX_EPOCH_JD)


# --------------------------------------------------------------------------
# Moon phases (Meeus ch. 49)
# --------------------------------------------------------------------------
_NEW = (-0.40720, 0.17241, 0.01608, 0.01039, 0.00739, -0.00514, 0.00208)
_FULL = (-0.40614, 0.17302, 0.01614, 0.01043, 0.00734, -0.00515, 0.00209)


def moon_phase_jd(k: float) -> float:
    """UTC Julian Date of a new moon (integer k) or full moon (k + 0.5).

    k = 0 is the new moon of 2000-01-06; each step of 1 is one lunation.
    """
    full = (k % 1) != 0
    t = k / 1236.85
    jde = (_NEW_MOON_K0_JDE + SYNODIC_MONTH * k + 0.00015437 * t * t
           - 0.000000150 * t ** 3 + 0.00000000073 * t ** 4)
    e = 1.0 - 0.002516 * t - 0.0000074 * t * t
    m = math.radians(2.5534 + 29.10535670 * k - 0.0000014 * t * t - 0.00000011 * t ** 3)
    mp = math.radians(201.5643 + 385.81693528 * k + 0.0107582 * t * t
                      + 0.00001238 * t ** 3 - 0.000000058 * t ** 4)
    f = math.radians(160.7108 + 390.67050284 * k - 0.0016118 * t * t
                     - 0.00000227 * t ** 3 + 0.000000011 * t ** 4)
    om = math.radians(124.7746 - 1.56375588 * k + 0.0020672 * t * t + 0.00000215 * t ** 3)
    c = _FULL if full else _NEW
    s = math.sin
    corr = (
        c[0] * s(mp) + c[1] * e * s(m) + c[2] * s(2 * mp) + c[3] * s(2 * f)
        + c[4] * e * s(mp - m) + c[5] * e * s(mp + m) + c[6] * e * e * s(2 * m)
        - 0.00111 * s(mp - 2 * f) - 0.00057 * s(mp + 2 * f) + 0.00056 * e * s(2 * mp + m)
        - 0.00042 * s(3 * mp) + 0.00042 * e * s(m + 2 * f) + 0.00038 * e * s(m - 2 * f)
        - 0.00024 * e * s(2 * mp - m) - 0.00017 * s(om) - 0.00007 * s(mp + 2 * m)
        + 0.00004 * s(2 * mp - 2 * f) + 0.00004 * s(3 * m) + 0.00003 * s(mp + m - 2 * f)
        + 0.00003 * s(2 * mp + 2 * f) - 0.00003 * s(mp + m + 2 * f) + 0.00003 * s(mp - m + 2 * f)
        - 0.00002 * s(mp - m - 2 * f) - 0.00002 * s(3 * mp + m) + 0.00002 * s(4 * mp)
    )
    return jde + corr - _DELTA_T_DAYS


def lunation_index(jd: float) -> int:
    """Index k of the new moon at or before the given Julian Date."""
    k = math.floor((jd - _NEW_MOON_K0_JDE) / SYNODIC_MONTH)
    # A true new moon is at most ~14 h away from the mean one: one step is enough.
    if moon_phase_jd(k + 1) <= jd:
        k += 1
    elif moon_phase_jd(k) > jd:
        k -= 1
    return k


def moon_age_days(jd: float) -> float:
    """Days since the last new moon."""
    return jd - moon_phase_jd(lunation_index(jd))


def nearest_full_moon_jd(jd: float) -> float:
    """UTC Julian Date of the full moon closest to the given Julian Date."""
    k = round((jd - _NEW_MOON_K0_JDE) / SYNODIC_MONTH - 0.5)
    return min((moon_phase_jd(k + d + 0.5) for d in (-1, 0, 1)), key=lambda x: abs(x - jd))


# --------------------------------------------------------------------------
# Sun and Moon longitude (Astronomical Almanac low-precision series)
# --------------------------------------------------------------------------
def sun_longitude(jd: float) -> float:
    """Apparent ecliptic longitude of the Sun in degrees (tropical)."""
    n = jd - J2000_JD
    g = math.radians(357.528 + 0.9856003 * n)
    return (280.460 + 0.9856474 * n + 1.915 * math.sin(g) + 0.020 * math.sin(2 * g)) % 360.0


def moon_longitude(jd: float) -> float:
    """Ecliptic longitude of the Moon in degrees (tropical)."""
    t = (jd - J2000_JD) / 36525.0
    s = lambda deg: math.sin(math.radians(deg))  # noqa: E731
    return (218.32 + 481267.881 * t
            + 6.29 * s(135.0 + 477198.87 * t) - 1.27 * s(259.3 - 413335.36 * t)
            + 0.66 * s(235.7 + 890534.22 * t) + 0.21 * s(269.9 + 954397.74 * t)
            - 0.19 * s(357.5 + 35999.05 * t) - 0.11 * s(186.5 + 966404.03 * t)) % 360.0


def moon_elongation(jd: float) -> float:
    """Angle Moon minus Sun in degrees: 0 new, 90 first quarter, 180 full."""
    return (moon_longitude(jd) - sun_longitude(jd)) % 360.0


def moon_illumination(jd: float) -> float:
    """Lit fraction of the Moon's disc, 0.0 (new) to 1.0 (full)."""
    return (1.0 - math.cos(math.radians(moon_elongation(jd)))) / 2.0


def moon_quarter_on(day: date, tz_hours: float) -> int | None:
    """Phase that falls on a local civil day: 0 new, 1 first quarter, 2 full,
    3 last quarter; None on all other days."""
    start = julian_day(datetime(day.year, day.month, day.day, tzinfo=timezone.utc)) - tz_hours / 24.0
    before = int(moon_elongation(start) // 90.0)
    after = int(moon_elongation(start + 1.0) // 90.0)
    # The elongation grows ~12 deg a day, so a day crosses at most one boundary.
    return after if after != before else None


def lahiri_ayanamsa(jd: float) -> float:
    """Lahiri ayanamsa in degrees (tropical minus sidereal longitude)."""
    return 23.853 + 0.013969 * (jd - J2000_JD) / 365.25


def sun_longitude_crossing(target: float, jd_guess: float) -> float:
    """Julian Date near jd_guess at which the Sun reaches a longitude."""
    jd = jd_guess
    for _ in range(6):
        jd += ((target - sun_longitude(jd) + 180.0) % 360.0 - 180.0) / 0.9856474
    return jd


# --------------------------------------------------------------------------
# Mars (Allison & McEwen 2000, the algorithm behind NASA's Mars24)
# --------------------------------------------------------------------------
def mars_sol_date(dt: datetime) -> float:
    """Mars Sol Date: Mars days ("sols") since 1873-12-29, from a UTC datetime."""
    jd_tt = julian_day(dt) + _DELTA_T_DAYS
    return (jd_tt - 2405522.0028779) / 1.0274912517


def mars_solar_longitude(dt: datetime) -> float:
    """Mars season angle Ls in degrees: 0 = northern spring equinox,
    90 = summer solstice, 180 = autumn equinox, 270 = winter solstice."""
    d = julian_day(dt) + _DELTA_T_DAYS - J2000_JD
    m = math.radians(19.3871 + 0.52402073 * d)
    equation_of_center = ((10.691 + 3.0e-7 * d) * math.sin(m) + 0.623 * math.sin(2 * m)
                          + 0.050 * math.sin(3 * m) + 0.005 * math.sin(4 * m)
                          + 0.0005 * math.sin(5 * m))
    return (270.3871 + 0.524038496 * d + equation_of_center) % 360.0


# --------------------------------------------------------------------------
# Lunisolar calendar (Chinese rule; Japan's old calendar uses the same rule
# with Japanese day boundaries)
# --------------------------------------------------------------------------
@lru_cache(maxsize=512)
def lunisolar_date(day: date, tz_hours: float = 8.0) -> tuple[int, int, bool, int]:
    """Return (lunar_year, month 1-12, is_leap_month, day 1-30) for a civil day.

    Rule: months start on the day of the new moon; the month holding the
    December solstice is month 11; in a solstice-to-solstice span of 13 months
    the first month without a principal solar term (Sun at a multiple of 30
    degrees) is a leap month. ``lunar_year`` is the Gregorian year in which
    that lunar year's New Year falls (the year the zodiac animal belongs to).
    """
    tz = timedelta(hours=tz_hours)

    def local(jd: float) -> date:
        return (from_julian_day(jd) + tz).date()

    def month_start(k: int) -> date:
        return local(moon_phase_jd(k))

    def lunation_of(d: date, jd: float) -> int:
        k = lunation_index(jd)
        if month_start(k) > d:
            k -= 1
        elif month_start(k + 1) <= d:
            k += 1
        return k

    def solstice_lunation(year: int) -> tuple[int, float]:
        w = sun_longitude_crossing(270.0, julian_day(datetime(year, 12, 21, tzinfo=timezone.utc)))
        return lunation_of(local(w), w), w

    noon = datetime(day.year, day.month, day.day, 12, tzinfo=timezone.utc) - tz
    k = lunation_of(day, julian_day(noon))

    first, w = solstice_lunation(day.year)
    if k >= first:
        sui = day.year + 1
    else:
        sui = day.year
        first, w = solstice_lunation(day.year - 1)
    last, _ = solstice_lunation(sui)

    leap = None
    if last - first == 13:
        terms = [local(sun_longitude_crossing((270.0 + 30.0 * i) % 360.0, w + 30.4369 * i))
                 for i in range(13)]
        for j in range(first, last):
            if not any(month_start(j) <= t < month_start(j + 1) for t in terms):
                leap = j
                break

    offset = k - first
    if leap is not None and k >= leap:
        offset -= 1
    month = (10 + offset) % 12 + 1  # the solstice month is month 11
    lunar_year = sui - 1 if month >= 11 else sui
    return lunar_year, month, k == leap, (day - month_start(k)).days + 1
