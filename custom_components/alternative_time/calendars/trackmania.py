
"""Trackmania Events (COTD, Weekly Shorts, Bonk Cup) - Version 1.0."""
from __future__ import annotations

from datetime import datetime, timedelta
import logging
from typing import Dict, Any, List
try:
    from zoneinfo import ZoneInfo  # Python 3.9+
except Exception:  # pragma: no cover
    ZoneInfo = None  # type: ignore

from homeassistant.core import HomeAssistant
from ..sensor import AlternativeTimeSensorBase

_LOGGER = logging.getLogger(__name__)

# ============================================
# CALENDAR METADATA
# ============================================

UPDATE_INTERVAL = 60  # seconds

CALENDAR_INFO = {
    "id": "trackmania",
    "version": "1.0.0",
    "icon": "mdi:flag-checkered",
    "category": "gaming",
    "accuracy": "official/community",
    "update_interval": UPDATE_INTERVAL,

    # Multi-language names
    "name": {
        "en": "Trackmania Events",
        "de": "Trackmania Ereignisse"
    },

    # Short descriptions for UI
    "description": {
        "en": "Shows the next start times for Cup of the Day (03:00 / 11:00 / 19:00 CE(S)T), Weekly Shorts release (Sundays 18:00 CE(S)T) and Bonk Cup (Thursdays 20:00 CE(S)T).",
        "de": "Zeigt die nächsten Startzeiten für Cup of the Day (03:00 / 11:00 / 19:00 ME(S)Z), Weekly Shorts Release (Sonntags 18:00 ME(S)Z) und Bonk Cup (Donnerstags 20:00 ME(S)Z)."
    },

    # Links to sources
    "sources": {
        "cotd_doc": "https://doc.trackmania.com/play/how-to-play-cotd/",
        "weekly_shorts_news": "https://www.trackmania.com/news/8431",
        "weekly_shorts_guidelines": "https://doc.trackmania.com/create/map-review/weekly-shorts-guidelines/",
        "bonk_info_example": "https://www.youtube.com/watch?v=AAkG2NSLZdw"
    },

    # Configuration options for this calendar
    "config_options": {
        "timezone": {
            "type": "text",
            "default": "Europe/Berlin",
            "description": {
                "en": "IANA timezone to compute local event times",
                "de": "IANA-Zeitzone zur Berechnung lokaler Zeiten"
            }
        },
        "enable_cotd": {
            "type": "boolean",
            "default": True,
            "description": {"en": "Enable Cup of the Day", "de": "Cup of the Day aktivieren"}
        },
        "enable_weekly_shorts": {
            "type": "boolean",
            "default": True,
            "description": {"en": "Enable Weekly Shorts (release)", "de": "Weekly Shorts (Release) aktivieren"}
        },
        "enable_bonk_cup": {
            "type": "boolean",
            "default": True,
            "description": {"en": "Enable Bonk Cup", "de": "Bonk Cup aktivieren"}
        },
        "horizon_days": {
            "type": "number",
            "default": 14,
            "description": {"en": "How many days ahead to list events", "de": "Vorschau in Tagen"}
        }
    }
}


class TrackmaniaEventsSensor(AlternativeTimeSensorBase):
    """Sensor that lists upcoming Trackmania event times."""

    UPDATE_INTERVAL = UPDATE_INTERVAL  # class-level for HA throttling

    def __init__(self, base_name: str, hass: HomeAssistant) -> None:
        super().__init__(base_name, hass)

        calendar_name = self._translate('name', 'Trackmania Events')

        self._attr_name = f"{base_name} {calendar_name}"
        self._attr_unique_id = f"{base_name}_trackmania_events"
        self._attr_icon = CALENDAR_INFO.get("icon", "mdi:flag-checkered")

        # Options (could later be loaded from config flow)
        self._tz_name = "Europe/Berlin"
        self._enable_cotd = True
        self._enable_weekly_shorts = True
        self._enable_bonk = True
        self._horizon_days = 14

        # Cached attributes
        self._tm_events: Dict[str, Any] = {}

    # -------------------- HA properties --------------------
    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        attrs = super().extra_state_attributes
        if self._tm_events:
            attrs.update(self._tm_events)
            attrs["description"] = self._translate('description')
            attrs["reference"] = CALENDAR_INFO.get("sources", {})
        return attrs

    # -------------------- Helpers --------------------
    def _tz(self):
        if ZoneInfo is not None:
            try:
                return ZoneInfo(self._tz_name)
            except Exception:  # pragma: no cover
                _LOGGER.warning("Invalid tz %s, falling back to Europe/Berlin", self._tz_name)
                return ZoneInfo("Europe/Berlin")
        # Fallback: naive localtime (should not happen in HA)
        return None

    def _make_event(self, when: datetime, title: str, tag: str) -> Dict[str, Any]:
        """Format a single event dict."""
        now = datetime.now(when.tzinfo)
        delta = when - now
        seconds = int(delta.total_seconds())
        sign = "" if seconds >= 0 else "-"
        seconds = abs(seconds)
        dh, rem = divmod(seconds, 3600)
        dm, ds = divmod(rem, 60)
        in_h = f"{sign}{dh:02d}:{dm:02d}:{ds:02d}"
        return {
            "title": title,
            "tag": tag,
            "when_local": when.strftime("%Y-%m-%d %H:%M:%S %Z"),
            "when_iso": when.isoformat(),
            "in": in_h
        }

    def _iter_days(self, start: datetime, days: int):
        for i in range(days+1):
            yield (start + timedelta(days=i)).date()

    def _generate_upcoming(self, now: datetime) -> List[Dict[str, Any]]:
        tz = now.tzinfo
        events: List[Dict[str, Any]] = []

        for d in self._iter_days(now, self._horizon_days):
            # Daily COTD times (03:00, 11:00, 19:00 local)
            if self._enable_cotd:
                for hh in (3, 11, 19):
                    when = datetime(d.year, d.month, d.day, hh, 0, 0, tzinfo=tz)
                    if when >= now - timedelta(hours=1):  # include last hour for context
                        events.append(self._make_event(when, "Cup of the Day", "cotd"))

            # Weekly Shorts: Sundays 18:00 local
            if self._enable_weekly_shorts and now.weekday() <= 6:
                if d.weekday() == 6:  # Sunday
                    when = datetime(d.year, d.month, d.day, 18, 0, 0, tzinfo=tz)
                    if when >= now - timedelta(hours=1):
                        events.append(self._make_event(when, "Weekly Shorts (release)", "weekly_shorts"))

            # Bonk Cup: Thursdays 20:00 local
            if self._enable_bonk:
                if d.weekday() == 3:  # Thursday
                    when = datetime(d.year, d.month, d.day, 20, 0, 0, tzinfo=tz)
                    if when >= now - timedelta(hours=1):
                        events.append(self._make_event(when, "Bonk Cup", "bonk_cup"))

        # sort
        events.sort(key=lambda e: e["when_iso"])
        return events

    # -------------------- Calculation & update --------------------
    def update(self) -> None:
        """Synchronous update for Home Assistant."""
        try:
            tz = self._tz()
            now = datetime.now(tz)
            upcoming = self._generate_upcoming(now)

            if upcoming:
                next_ev = next((e for e in upcoming if e["when_iso"] >= now.isoformat()), upcoming[0])
                self._tm_events = {
                    "timezone": self._tz_name,
                    "now_local": now.strftime("%Y-%m-%d %H:%M:%S %Z"),
                    "next_event": next_ev,
                    "upcoming_events": upcoming[:20]
                }
                self._state = f"Next: {next_ev['title']} @ {next_ev['when_local']} (in {next_ev['in']})"
            else:
                self._tm_events = {"timezone": self._tz_name, "now_local": now.strftime("%Y-%m-%d %H:%M:%S %Z")}
                self._state = "No events found"
        except Exception as exc:  # pragma: no cover
            _LOGGER.exception("Failed to update Trackmania events: %s", exc)
            self._state = "Error"
