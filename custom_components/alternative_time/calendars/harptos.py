"""Harptos Calendar (Dungeons & Dragons / Forgotten Realms) implementation - Version 2.5."""
from __future__ import annotations

from datetime import datetime
import logging
from typing import Dict, Any

from homeassistant.core import HomeAssistant
from ..sensor import AlternativeTimeSensorBase

_LOGGER = logging.getLogger(__name__)

# ============================================
# CALENDAR METADATA
# ============================================

# Update interval (1h, da sich nur Tage/Monate ändern)
UPDATE_INTERVAL = 3600

CALENDAR_INFO = {
    "id": "harptos",
    "version": "2.5.0",
    "icon": "mdi:dice-d20",
    "category": "fantasy",
    "accuracy": "fictional",
    "update_interval": UPDATE_INTERVAL,

    "name": {
        "en": "Harptos Calendar",
        "de": "Harptos-Kalender",
        "fr": "Calendrier de Harptos",
        "es": "Calendario de Harptos",
        "it": "Calendario di Harptos",
        "ru": "Календарь Харптоса"
    },

    "description": {
        "en": "The standard calendar of the Forgotten Realms (Dungeons & Dragons), with 12 months of 30 days and 5 festivals.",
        "de": "Der Standardkalender der Vergessenen Reiche (Dungeons & Dragons), mit 12 Monaten zu 30 Tagen und 5 Festtagen.",
        "fr": "Le calendrier standard des Royaumes Oubliés (Donjons & Dragons), avec 12 mois de 30 jours et 5 fêtes."
    },

    "detailed_info": {
        "en": {
            "overview": "The Calendar of Harptos divides the year into 12 months of 30 days each, plus 5 special festival days.",
            "structure": "Each month has 3 tendays (10-day weeks). Festivals fall between certain months.",
            "festivals": "Midwinter, Greengrass, Midsummer, Highharvestide, Feast of the Moon",
            "use": "Used throughout the Forgotten Realms for daily life, trade, and religion."
        }
    },

    "harptos_data": {
        "months": [
            "Hammer", "Alturiak", "Ches", "Tarsakh", "Mirtul", "Kythorn",
            "Flamerule", "Eleasis", "Eleint", "Marpenoth", "Uktar", "Nightal"
        ],
        "festivals": {
            (1, 31): "❄️ Midwinter",
            (4, 31): "🌱 Greengrass",
            (7, 31): "☀️ Midsummer",
            (9, 31): "🍂 Highharvestide",
            (11, 31): "🕯️ Feast of the Moon"
        },
        "tenday_names": ["First-day", "Second-day", "Third-day", "Fourth-day", "Fifth-day",
                         "Sixth-day", "Seventh-day", "Eighth-day", "Ninth-day", "Tenth-day"]
    },

    "reference_url": "https://forgottenrealms.fandom.com/wiki/Calendar_of_Harptos",
    "origin": "Dungeons & Dragons (Forgotten Realms)",
    "created_by": "Ed Greenwood",

    "example": "1491 DR, Ches 15 (Third-day)",
    "example_meaning": "The 15th day of Ches, 1491 Dalereckoning (DR).",

    "tags": ["fantasy", "dnd", "forgotten_realms", "harptos", "calendar"],

    "features": {
        "supports_tendays": True,
        "supports_festivals": True,
        "precision": "day"
    }
}


class HarptosCalendarSensor(AlternativeTimeSensorBase):
    """Sensor for the Harptos Calendar (Forgotten Realms)."""

    UPDATE_INTERVAL = 3600

    def __init__(self, base_name: str, hass: HomeAssistant) -> None:
        super().__init__(base_name, hass)

        calendar_name = self._translate("name", "Harptos Calendar")

        self._attr_name = f"{base_name} {calendar_name}"
        self._attr_unique_id = f"{base_name}_harptos_calendar"
        self._attr_icon = CALENDAR_INFO.get("icon", "mdi:dice-d20")

        self._harptos_data = CALENDAR_INFO["harptos_data"]

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        attrs = super().extra_state_attributes
        if hasattr(self, "_harptos_date"):
            attrs.update(self._harptos_date)
            attrs["description"] = self._translate("description")
            attrs["reference"] = CALENDAR_INFO.get("reference_url", "")
        return attrs

    def _calculate_harptos_date(self, earth_date: datetime) -> Dict[str, Any]:
        """Convert Earth date into Harptos date (approximation: 1:1 day mapping)."""

        # Simplified: Use Earth year as DR (Dalereckoning)
        dr_year = earth_date.year

        # Day of year
        day_of_year = earth_date.timetuple().tm_yday

        # Account for festivals
        festivals = self._harptos_data["festivals"]
        months = self._harptos_data["months"]

        month = None
        day = None
        festival = None

        # Each month has 30 days = 360 days + 5 festivals = 365
        if day_of_year in [31, 121, 212, 274, 335]:  # Example festival offsets
            festival = festivals.get((earth_date.month, earth_date.day), None)
        else:
            # Normalize into 12x30 day calendar
            index = (day_of_year - 1) % 360
            month_index = index // 30
            day = (index % 30) + 1
            month = months[month_index]

        # Tenday calculation
        tenday = None
        if day:
            tenday_index = (day - 1) % 10
            tenday = self._harptos_data["tenday_names"][tenday_index]

        result = {
            "year_dr": dr_year,
            "month": month if month else "Festival",
            "day": day if day else "",
            "tenday": tenday if tenday else "",
            "festival": festival if festival else "",
            "full_date": f"{dr_year} DR, {month} {day} ({tenday})" if month else f"{dr_year} DR, {festival}"
        }

        return result

    def update(self) -> None:
        now = datetime.now()
        self._harptos_date = self._calculate_harptos_date(now)
        self._state = self._harptos_date["full_date"]
        _LOGGER.debug(f"Updated Harptos calendar to {self._state}")
