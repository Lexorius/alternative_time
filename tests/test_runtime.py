"""Runtime behaviour of the sensor base class and the UT1 plugin (v2.6.1).

- one scheduler: should_poll is False, overlapping ticks are skipped
- failures: warn once per streak, unavailable after 3, recovery logged
- UT1: shared aiohttp session, exponential backoff, recovery resets
"""
from __future__ import annotations

import asyncio
import importlib
import logging
from datetime import datetime, timedelta, timezone

import pytest
from conftest import INTEGRATION, FakeHass, run

aiohttp = pytest.importorskip("aiohttp")


class _Flaky:
    """Mixin factory: update() raises `fail_times` times, then succeeds."""

    @staticmethod
    def make(sensor_module, fail_times: int):
        class Flaky(sensor_module.AlternativeTimeSensorBase):
            def __init__(self):
                super().__init__("T", FakeHass())
                self.hass = self._hass
                self._attr_name = "T flaky"
                self.entity_id = "sensor.t_flaky"
                self._calendar_id = "flaky"
                self.calls = 0

            def update(self):
                self.calls += 1
                if self.calls <= fail_times:
                    raise RuntimeError(f"boom {self.calls}")
                self._state = "fine"

        return Flaky()


# ------------------------------------------------------------ scheduling --
def test_should_poll_is_false(sensor_module):
    assert _Flaky.make(sensor_module, 0).should_poll is False


def test_base_declares_match_all_unrecorded_attributes(sensor_module):
    attrs = sensor_module.AlternativeTimeSensorBase._unrecorded_attributes
    assert isinstance(attrs, frozenset) and attrs == frozenset({"*"})


def test_overlapping_tick_is_skipped(sensor_module):
    async def scenario():
        gate = asyncio.Event()

        class Slow(sensor_module.AlternativeTimeSensorBase):
            def __init__(self):
                super().__init__("S", FakeHass())
                self.hass = self._hass
                self._attr_name = "S slow"
                self.entity_id = "sensor.s_slow"
                self.runs = 0

            async def async_update(self):
                self.runs += 1
                await gate.wait()

        e = Slow()
        first = asyncio.create_task(e._async_timer_tick(None))
        await asyncio.sleep(0)
        assert e._tick_running is True
        await e._async_timer_tick(None)  # must return immediately
        assert e.runs == 1
        gate.set()
        await first
        assert e._tick_running is False
        await e._async_timer_tick(None)
        assert e.runs == 2

    run(scenario())


def test_no_state_write_after_removal(sensor_module):
    e = _Flaky.make(sensor_module, 0)
    e.hass = None  # HA nulls hass when the entity is removed
    run(e._async_timer_tick(None))
    assert getattr(e, "writes", 0) == 0


# --------------------------------------------------------- error handling --
def test_warn_once_unavailable_after_three_then_recover(sensor_module, caplog_integration):
    e = _Flaky.make(sensor_module, fail_times=4)
    for _ in range(4):
        run(e._async_timer_tick(None))
    assert caplog_integration.count(logging.WARNING, "failed:") == 1
    assert caplog_integration.count(logging.WARNING, "marked unavailable") == 1
    assert caplog_integration.count(logging.DEBUG, "failed again") == 3
    assert e.available is False
    assert e._consecutive_failures == 4

    run(e._async_timer_tick(None))  # 5th call succeeds
    assert e.available is True
    assert e._consecutive_failures == 0
    assert caplog_integration.count(logging.INFO, "recovered after 4") == 1
    assert e.writes == 5, "state is written on every tick, including failed ones"


def test_two_failures_stay_available(sensor_module):
    e = _Flaky.make(sensor_module, fail_times=2)
    for _ in range(2):
        run(e._async_timer_tick(None))
    assert e.available is True


def test_legacy_underscore_get_plugin_options_alias(sensor_module):
    """Five plugins call self._get_plugin_options(); it must exist (v2.6.2)."""
    assert sensor_module.AlternativeTimeSensorBase._get_plugin_options \
        is sensor_module.AlternativeTimeSensorBase.get_plugin_options


# ------------------------------------------------------------------- UT1 --
class _Response:
    def __init__(self, status=200, payload=None):
        self.status = status
        self._payload = {"value": 0.05} if payload is None else payload

    async def json(self):
        return self._payload

    async def text(self):
        return str(self._payload)

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False


class _Session:
    def __init__(self):
        self.calls = 0
        self.mode = "fail"  # fail | ok | http500

    def get(self, url, headers=None, timeout=None):
        self.calls += 1
        if self.mode == "fail":
            raise aiohttp.ClientError("connection refused")
        if self.mode == "http500":
            return _Response(status=500, payload={})
        return _Response()


@pytest.fixture
def ut1(make_sensor, monkeypatch):
    ut1_mod = importlib.import_module(f"{INTEGRATION}.calendars.ut1")
    session = _Session()
    # ut1 binds the name at import time -> patch where it is looked up
    monkeypatch.setattr(ut1_mod, "async_get_clientsession", lambda hass: session)
    entity = make_sensor("ut1")
    entity.entity_id = "sensor.u_ut1"
    return entity, session, ut1_mod


def _expire_backoff(entity):
    entity._iers_next_attempt = datetime.now(timezone.utc) - timedelta(seconds=1)


def test_ut1_failure_schedules_backoff_and_does_not_refetch(ut1, caplog_integration):
    entity, session, _ = ut1
    assert run(entity._async_fetch_iers_data()) is False
    assert session.calls == 1
    assert entity._iers_failures == 1 and entity._iers_next_attempt is not None
    assert entity._dut1_source == "fallback"
    delay = (entity._iers_next_attempt - datetime.now(timezone.utc)).total_seconds()
    assert 55 <= delay <= 61
    assert caplog_integration.count(logging.WARNING, "IERS API fetch failed") == 1
    for _ in range(30):  # 30 more ticks inside the backoff window
        run(entity._async_fetch_iers_data())
    assert session.calls == 1
    assert caplog_integration.count(logging.WARNING) == 1


def test_ut1_backoff_doubles_and_caps(ut1):
    entity, session, ut1_mod = ut1
    delays = []
    for _ in range(8):
        _expire_backoff(entity)
        run(entity._async_fetch_iers_data())
        delays.append(round((entity._iers_next_attempt - datetime.now(timezone.utc)).total_seconds()))
    assert session.calls == 8
    for got, want in zip(delays[:6], [60, 120, 240, 480, 960, 1920]):
        assert abs(got - want) <= 1, delays
    assert delays[6] == ut1_mod.IERS_BACKOFF_MAX and delays[7] == ut1_mod.IERS_BACKOFF_MAX


def test_ut1_recovery_resets_backoff_and_serves_cache(ut1, caplog_integration):
    entity, session, _ = ut1
    run(entity._async_fetch_iers_data())  # one failure
    _expire_backoff(entity)
    session.mode = "ok"
    assert run(entity._async_fetch_iers_data()) is True
    assert entity._iers_failures == 0 and entity._iers_next_attempt is None
    assert entity._dut1_value == 0.05 and entity._dut1_source == "iers_api"
    assert caplog_integration.count(logging.INFO, "reachable again") == 1
    before = session.calls
    run(entity._async_fetch_iers_data())
    assert session.calls == before and entity._dut1_source == "cached"


def test_ut1_http_error_counts_as_failure(ut1):
    entity, session, _ = ut1
    session.mode = "http500"
    assert run(entity._async_fetch_iers_data()) is False
    assert entity._iers_failures == 1
