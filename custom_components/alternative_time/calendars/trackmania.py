"""Trackmania Events (COTD, Weekly Shorts, Bonk Cup)
Version 1.2 – reads options via get_plugin_options() (no get_config() calls).
"""
from __future__ import annotations

from datetime import datetime, timedelta
import logging
from typing import Dict, Any, List

try:
    from zoneinfo import ZoneInfo  # Python 3.9+
except ImportError:  # Besser ImportError statt Exception
    try:
        import pytz  # Fallback zu pytz
        ZoneInfo = None
    except ImportError:
        ZoneInfo = None
        pytz = None

from homeassistant.core import HomeAssistant
from ..sensor import AlternativeTimeSensorBase  # Korrekt!

_LOGGER = logging.getLogger(__name__)

# ============================================
# CALENDAR METADATA
# ============================================

UPDATE_INTERVAL = 60  # seconds

CALENDAR_INFO = {
    "id": "trackmania",
    "version": "1.2.0",
    "icon": "mdi:flag-checkered",
    "category": "gaming",  # Korrekt für Gaming-Kategorie
    "accuracy": "official/community",
    "update_interval": UPDATE_INTERVAL,

    # [Rest des CALENDAR_INFO bleibt gleich...]
}


class TrackmaniaEventsSensor(AlternativeTimeSensorBase):
    """Sensor that lists upcoming Trackmania event times."""

    UPDATE_INTERVAL = UPDATE_INTERVAL  # class-level for HA throttling

    def __init__(self, base_name: str, hass: HomeAssistant) -> None:
        super().__init__(base_name, hass)

        calendar_name = self._translate('name', 'Trackmania Events')

        self._attr_name = f"{base_name} {calendar_name}"
        self._attr_unique_id = f"{base_name}_trackmania_events"  # Unique ID wird von sensor.py angepasst
        self._attr_icon = CALENDAR_INFO.get("icon", "mdi:flag-checkered")

        # Defaults werden in update() überschrieben
        self._tz_name = "Europe/Berlin"
        self._enable_cotd = True
        self._enable_weekly_shorts = True
        self._enable_bonk = True
        self._horizon_days = 14

        # Cached attributes
        self._tm_events: Dict[str, Any] = {}
        self._state = "Initializing..."  # Initialer State

    # -------------------- HA properties --------------------
    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        attrs = super().extra_state_attributes  # Nutzt die Basis-Implementation
        if self._tm_events:
            attrs.update(self._tm_events)
            attrs["description"] = self._translate('description')
            attrs["reference"] = CALENDAR_INFO.get("sources", {})
        return attrs

    # -------------------- Helpers --------------------
    def _tz(self):
        """Get timezone object with better fallback handling."""
        if ZoneInfo is not None:
            try:
                return ZoneInfo(self._tz_name)
            except Exception as e:
                _LOGGER.warning("Invalid timezone %s: %s, falling back to Europe/Berlin", self._tz_name, e)
                try:
                    return ZoneInfo("Europe/Berlin")
                except Exception:
                    _LOGGER.error("Could not load fallback timezone")
                    return None
        
        # Fallback zu pytz wenn verfügbar
        if 'pytz' in globals():
            try:
                import pytz
                return pytz.timezone(self._tz_name)
            except Exception:
                try:
                    return pytz.timezone("Europe/Berlin")
                except Exception:
                    pass
        
        return None

    # [Rest der Methoden bleibt gleich...]

    def update(self) -> None:
        """Synchronous update for Home Assistant."""
        try:
            # Pull options from config_entry via AlternativeTimeSensorBase helper
            opts = self.get_plugin_options()  # Direkt aufrufen, keine extra try/except nötig
            
            # Update configuration from options
            self._tz_name = opts.get("timezone", "Europe/Berlin")  # Fallback direkt angeben
            self._enable_cotd = bool(opts.get("enable_cotd", True))
            self._enable_weekly_shorts = bool(opts.get("enable_weekly_shorts", True))
            self._enable_bonk = bool(opts.get("enable_bonk_cup", True))
            
            try:
                self._horizon_days = int(opts.get("horizon_days", 14))
                self._horizon_days = max(1, min(365, self._horizon_days))  # Clamp zwischen 1-365
            except (ValueError, TypeError):
                self._horizon_days = 14

            tz = self._tz()
            if tz is None:
                self._state = "Timezone error"
                self._tm_events = {"error": "Could not initialize timezone"}
                return
                
            now = datetime.now(tz)
            upcoming = self._generate_upcoming(now)

            if upcoming:
                next_ev = next((e for e in upcoming if e["when_iso"] >= now.isoformat()), upcoming[0])
                self._tm_events = {
                    "timezone": self._tz_name,
                    "now_local": now.strftime("%Y-%m-%d %H:%M:%S %Z"),
                    "next_event": next_ev,
                    "upcoming_events": upcoming[:20]  # Limit auf 20 Events
                }
                # Kürzerer State für bessere Übersicht
                self._state = f"{next_ev['title']} in {next_ev['in']}"
            else:
                self._tm_events = {
                    "timezone": self._tz_name, 
                    "now_local": now.strftime("%Y-%m-%d %H:%M:%S %Z"),
                    "message": "No events scheduled"
                }
                self._state = "No events"
                
        except Exception as exc:
            _LOGGER.exception("Failed to update Trackmania events: %s", exc)
            self._state = "Error"
            self._tm_events = {"error": str(exc)}