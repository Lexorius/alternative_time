"""Harptos Calendar (Dungeons & Dragons / Forgotten Realms) implementation - Version 2.6."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, date, timezone
import logging
from typing import Dict, Any, List, Optional

from homeassistant.core import HomeAssistant
from ..sensor import AlternativeTimeSensorBase

_LOGGER = logging.getLogger(__name__)

# ============================================
# CALENDAR METADATA
# ============================================

# Update nur stündlich – es ändert sich der Tag (nicht die Uhrzeit)
UPDATE_INTERVAL = 3600

CALENDAR_INFO = {
    "id": "dnd_harptos",
    "version": "2.6.0",
    "icon": "mdi:dice-d20",
    "category": "fantasy",
    "accuracy": "fictional",
    "update_interval": UPDATE_INTERVAL,

    # Namen
    "name": {
        "en": "D&D – Harptos Calendar",
        "de": "D&D – Harptos‑Kalender",
    },

    # Kurze Beschreibung
    "description": {
        "en": "Forgotten Realms ‘Calendar of Harptos’: 12×30 days with intercalary festivals (Midwinter, Greengrass, Midsummer, Highharvestide, Feast of the Moon; Shieldmeet on leap years). Weeks are tendays.",
        "de": "Vergessene Reiche ‚Harptos‑Kalender‘: 12×30 Tage mit Zwischentagen/Festen (Midwinter, Greengrass, Midsummer, Highharvestide, Feast of the Moon; Shieldmeet in Schaltjahren). Wochen sind Zehntage (Tendays).",
    },

    # Daten für UI & Docs
    "harptos_data": {
        "months": [
            {"id": "hammer", "en": "Hammer", "de": "Hammer"},
            {"id": "alturiak", "en": "Alturiak", "de": "Alturiak"},
            {"id": "ches", "en": "Ches", "de": "Ches"},
            {"id": "tarsakh", "en": "Tarsakh", "de": "Tarsakh"},
            {"id": "mirtul", "en": "Mirtul", "de": "Mirtul"},
            {"id": "kythorn", "en": "Kythorn", "de": "Kythorn"},
            {"id": "flamerule", "en": "Flamerule", "de": "Flamerule"},
            {"id": "eleasias", "en": "Eleasis", "de": "Eleasias"},
            {"id": "eleint", "en": "Eleint", "de": "Eleint"},
            {"id": "marpenoth", "en": "Marpenoth", "de": "Marpenoth"},
            {"id": "uktar", "en": "Uktar", "de": "Uktar"},
            {"id": "nightal", "en": "Nightal", "de": "Nightal"},
        ],
        # feste NACH welchem Monat eingefügt (1‑basiert)
        "festivals": [
            {"id": "midwinter",      "after_month": 1,  "en": "Midwinter",        "de": "Midwinter"},
            {"id": "greengrass",     "after_month": 4,  "en": "Greengrass",       "de": "Greengrass"},
            {"id": "midsummer",      "after_month": 7,  "en": "Midsummer",        "de": "Midsummer"},
            {"id": "highharvestide", "after_month": 9,  "en": "Highharvestide",   "de": "Highharvestide"},
            {"id": "feast_of_moon",  "after_month": 11, "en": "Feast of the Moon","de": "Fest des Mondes"},
        ],
        "shieldmeet": {"id": "shieldmeet", "en": "Shieldmeet", "de": "Shieldmeet"},  # Schaltjahr‑Fest nach Midsummer
        "weekday_names": {
            "en": [f"Day {i}" for i in range(1, 11)],
            "de": [f"Tag {i}" for i in range(1, 11)],
        }
    },

    # Optionale Konfiguration für den Wizard
    "config_options": {
        "dr_ce_diff": {
            "type": "number",
            "default": 531,   # 2025 CE -> 1494 DR (DR = CE − 531)
            "min": -2000,
            "max": 5000,
            "description": {
                "en": "Offset between Common Era year and Dalereckoning (DR): DR = CE − diff",
                "de": "Versatz zwischen Common Era (CE) und Dalereckoning (DR): DR = CE − Versatz",
            }
        },
        "leap_rule": {
            "type": "select",
            "default": "gregorian",
            "options": ["gregorian", "every_4_years", "never"],
            "description": {
                "en": "Shieldmeet insertion rule",
                "de": "Regel für Shieldmeet (Schalttag)",
            }
        },
        "locale": {
            "type": "select",
            "default": "auto",
            "options": ["auto", "en", "de"],
            "description": {
                "en": "Force language (auto uses Home Assistant language)",
                "de": "Sprache erzwingen (auto nutzt Home‑Assistant‑Sprache)",
            }
        }
    },

    "reference_url": "https://forgottenrealms.fandom.com/wiki/Calendar_of_Harptos",
    "origin": "Dungeons & Dragons (Forgotten Realms)",
    "created_by": "Ed Greenwood",
    "example": "1494 DR, Kythorn 10 (Day 10)",
    "tags": ["fantasy", "dnd", "forgotten_realms", "harptos", "tenday", "festival"],
    "features": {
        "supports_tendays": True,
        "supports_festivals": True,
        "precision": "day"
    }
}

# ============================================
# LOGIC
# ============================================

def _is_gregorian_leap(y: int) -> bool:
    return (y % 4 == 0) and ((y % 100 != 0) or (y % 400 == 0))

@dataclass(frozen=True)
class _Day:
    kind: str           # "month" | "festival"
    month_index: int    # 1..12 for months; month it follows for festivals
    day: int | None     # 1..30 for month day; None for festivals
    fest_id: str | None # festival id when kind == "festival"

def _build_timeline(gyear: int, leap_rule: str, hd: Dict[str, Any]) -> List[_Day]:
    """Linear list of 365/366 Harptos days for the given Gregorian year."""
    months = hd["months"]
    festivals = hd["festivals"]
    shieldmeet = hd["shieldmeet"]["id"]

    timeline: List[_Day] = []

    # 12×30 month days
    for m in range(1, 13):
        for d in range(1, 31):
            timeline.append(_Day("month", m, d, None))
        # regular festivals that come after this month
        for f in festivals:
            if f["after_month"] == m:
                timeline.append(_Day("festival", m, None, f["id"]))
        # after Flamerule (m==7) possibly Shieldmeet
        if m == 7:
            add_shieldmeet = False
            if leap_rule == "gregorian":
                add_shieldmeet = _is_gregorian_leap(gyear)
            elif leap_rule == "every_4_years":
                add_shieldmeet = (gyear % 4 == 0)
            elif leap_rule == "never":
                add_shieldmeet = False
            if add_shieldmeet:
                timeline.append(_Day("festival", m, None, shieldmeet))

    return timeline

def _day_of_year(d: date) -> int:
    start = date(d.year, 1, 1)
    return (d - start).days + 1

def _locale_choice(opts_locale: str, hass_lang: str) -> str:
    if opts_locale and opts_locale != "auto":
        return opts_locale if opts_locale in ("en", "de") else "en"
    # auto -> use hass language primary
    p = (hass_lang or "en").split("-")[0].split("_")[0]
    return "de" if p == "de" else "en"

# ============================================
# SENSOR
# ============================================

class HarptosCalendarSensor(AlternativeTimeSensorBase):
    """Sensor for the D&D Harptos Calendar."""

    UPDATE_INTERVAL = UPDATE_INTERVAL

    def __init__(self, base_name: str, hass: HomeAssistant) -> None:
        super().__init__(base_name, hass)

        cal_name = self._translate("name", "Harptos Calendar")
        self._attr_name = f"{base_name} {cal_name}"
        self._attr_unique_id = f"{base_name}_dnd_harptos"
        self._attr_icon = CALENDAR_INFO.get("icon", "mdi:dice-d20")

        self._hd = CALENDAR_INFO["harptos_data"]

        # defaults (overridden by plugin options at runtime)
        self._dr_ce_diff = 531
        self._leap_rule = "gregorian"
        self._forced_locale = "auto"

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        attrs = super().extra_state_attributes
        if hasattr(self, "_harptos"):
            attrs.update(self._harptos)
            attrs["description"] = self._translate("description")
            attrs["reference"] = CALENDAR_INFO.get("reference_url", "")
        return attrs

    # ---------- core calculation ----------

    def _compute(self, dt: datetime, locale: str) -> Dict[str, Any]:
        d = dt.astimezone(timezone.utc).date() if dt.tzinfo else dt.date()

        # apply plugin options
        opts = self.get_plugin_options() or {}
        self._dr_ce_diff = int(opts.get("dr_ce_diff", self._dr_ce_diff))
        self._leap_rule = str(opts.get("leap_rule", self._leap_rule))
        self._forced_locale = str(opts.get("locale", self._forced_locale))
        use_locale = _locale_choice(self._forced_locale, getattr(self._hass.config, "language", "en"))

        timeline = _build_timeline(d.year, self._leap_rule, self._hd)
        doy = max(1, min(_day_of_year(d), len(timeline)))
        entry = timeline[doy - 1]

        # DR year mapping
        dr_year = d.year - self._dr_ce_diff

        months = self._hd["months"]
        festivals = {f["id"]: f for f in self._hd["festivals"]}
        shieldmeet = self._hd["shieldmeet"]

        # count month-days so far (exclude festivals) to get tenday/day-of-tenday
        month_days_before = sum(1 for x in timeline[:doy - 1] if x.kind == "month")
        if entry.kind == "month":
            month_days_before += 1
        day_of_tenday = ((month_days_before - 1) % 10) + 1 if entry.kind == "month" else None
        tenday_number = ((month_days_before - 1) // 10) + 1 if entry.kind == "month" else None  # 1..36

        if entry.kind == "month":
            m_idx = entry.month_index
            m = months[m_idx - 1]
            m_name = m[use_locale]
            state = f"{m_name} {entry.day}, {dr_year} DR"
            fest_obj = None
        else:
            # festival
            if entry.fest_id == "shieldmeet":
                fest_obj = shieldmeet
            else:
                fest_obj = festivals.get(entry.fest_id)
            fest_name = fest_obj[use_locale] if fest_obj else "Festival"
            state = f"{fest_name}, {dr_year} DR"

        attrs = {
            "calendar_id": CALENDAR_INFO["id"],
            "calendar_name": CALENDAR_INFO["name"][use_locale],
            "calendar_description": CALENDAR_INFO["description"][use_locale],
            "locale": use_locale,
            "dr_year": dr_year,
            "is_gregorian_leap_year": _is_gregorian_leap(d.year),
            "kind": entry.kind,
            "months": [m[use_locale] for m in months],
            "festival_list": [f[use_locale] for f in self._hd["festivals"]] + [shieldmeet[use_locale]],
            "weekday_names": self._hd["weekday_names"][use_locale],
        }

        if entry.kind == "month":
            attrs.update({
                "month_index": entry.month_index,
                "month_id": months[entry.month_index - 1]["id"],
                "month_name": months[entry.month_index - 1][use_locale],
                "day": entry.day,
                "day_of_tenday": day_of_tenday,
                "tenday_number": tenday_number,
                "festival": "",
            })
        else:
            attrs.update({
                "festival_id": fest_obj["id"] if fest_obj else "",
                "festival_name": fest_obj[use_locale] if fest_obj else "",
            })

        return {"state": state, "attrs": attrs}

    # ---------- HA hooks ----------

    def update(self) -> None:
        now = datetime.now()
        result = self._compute(now, getattr(self._hass.config, "language", "en"))
        self._harptos = result["attrs"]
        self._state = result["state"]
        _LOGGER.debug(f"Updated Harptos to {self._state}")
