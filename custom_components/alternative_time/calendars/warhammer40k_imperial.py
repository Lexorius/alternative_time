"""Warhammer 40,000 - Imperial Dating System calendar (Old Style) - v1.0.0

This sensor renders dates in the classic Imperial format:
    C.FFF.YYY.M##
where:
- C   = Check number (0-9), indicating accuracy/source (0 = Terra/most accurate).
- FFF = Year fraction (000-999), i.e., 1,000 equal parts of the year.
- YYY = Year within the millennium (000-999).
- M## = Millennium designator (e.g., M41).

By default we convert the **current Terran (Gregorian) date** per the
Old Style method described in the 3rd Ed. rulebook, summarized on Lexicanum.
You can optionally apply a positive "year_offset" (e.g., 38000) to give the
sensor that M41/M42 feel during present-day years.

References:
- Lexicanum: "Imperial Dating System" (check numbers, year fraction, Makr constant).
- 1000 fractions per year ≈ 8h 45m 36s per fraction; "Makr constant" 0.11407955.

Note: We only implement Old Style here. New Style (post-Great Rift "Vigilus template")
would require a local rift epoch anchor and is not included to keep the sensor lean.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
import logging
from typing import Any, Dict, Optional

from homeassistant.core import HomeAssistant
from ..sensor import AlternativeTimeSensorBase

_LOGGER = logging.getLogger(__name__)

# ============================================
# CALENDAR METADATA
# ============================================

UPDATE_INTERVAL = 300  # seconds; ~5 min is plenty (fraction ticks every ~8h45m)

CALENDAR_INFO: Dict[str, Any] = {
    "id": "warhammer40k_imperial",
    "version": "1.0.0",
    "icon": "mdi:sword-cross",
    "category": "fictional",
    "accuracy": "lore-accurate (Old Style)",
    "update_interval": UPDATE_INTERVAL,
    "name": {
        "en": "Warhammer 40,000 - Imperial Date (Old Style)",
        "de": "Warhammer 40.000 - Imperiales Datum (Old Style)"
    },
    "description": {
        "en": "Formats current Terran time into the Imperial Dating System (C.FFF.YYY.M##).",
        "de": "Formatiert die aktuelle terranische Zeit ins Imperiale Datumsformat (C.FFF.YYY.M##)."
    },
    "reference_url": "https://wh40k.lexicanum.com/wiki/Imperial_Dating_System",
    "notes": {
        "en": (
            "Uses Gregorian AD for year/millennium. Set a positive year_offset "
            "(e.g., 38000) to emulate M41/M42 in present day."
        ),
        "de": (
            "Verwendet gregorianisches AD für Jahr/Jahrtausend. Mit year_offset "
            "(z. B. 38000) lässt sich M41/M42 im Jetzt emulieren."
        )
    },
    # Constants from the lore
    "imperial": {
        "makr_constant": 0.11407955,  # per Lexicanum; 1 fraction ≈ 8h 45m 36s
        "fractions_per_year": 1000
    },
    "config_options": {
        "check_number": {
            "type": "integer",
            "default": 0,
            "min": 0,
            "max": 9,
            "description": {
                "en": "Imperial check number 0-9 (0 = Terra/most accurate).",
                "de": "Imperiale Prüfziffer 0-9 (0 = Terra/höchste Genauigkeit)."
            }
        },
        "year_offset": {
            "type": "integer",
            "default": 0,
            "description": {
                "en": "Add this many years before converting (e.g., 38000 to map 2025 → 40025 → M41).",
                "de": "So viele Jahre vor der Umrechnung addieren (z. B. 38000, um 2025 → 40025 → M41 zu erhalten)."
            }
        },
        "system_designator": {
            "type": "string",
            "default": "SOL",
            "description": {
                "en": "Optional system/sector code to append (e.g., SOL, VCM).",
                "de": "Optionaler System-/Sektorkürzel zum Anhängen (z. B. SOL, VCM)."
            }
        },
        "fraction_method": {
            "type": "select",
            "default": "precise",
            "options": ["precise", "lexicanum"],
            "description": {
                "en": "Year-fraction method: precise (elapsed seconds ÷ total seconds) or Lexicanum (Makr constant).",
                "de": "Berechnung der Jahresfraktion: precise (verstrichene Sekunden ÷ Gesamtsekunden) oder Lexicanum (Makr-Konstante)."
            }
        }
    }
}


@dataclass
class ImperialDate:
    check: int
    fraction: int  # 0..999
    year_in_millennium: int  # 0..999
    millennium: int  # e.g., 41
    system: Optional[str] = None

    def format(self) -> str:
        sys = f" {self.system}" if self.system else ""
        return f"{self.check}.{self.fraction:03d}.{self.year_in_millennium:03d}.M{self.millennium:02d}{sys}"


class WarhammerImperialCalendarSensor(AlternativeTimeSensorBase):
    """Sensor that exposes the Imperial Dating System (Old Style)."""

    UPDATE_INTERVAL = UPDATE_INTERVAL

    def __init__(self, base_name: str, hass: HomeAssistant) -> None:
        super().__init__(base_name, hass)

        calendar_name = self._translate('name', 'Warhammer 40,000 - Imperial Date (Old Style)')
        self._attr_name = f"{base_name} {calendar_name}"
        self._attr_unique_id = f"{base_name}_warhammer40k_imperial_date"
        self._attr_icon = CALENDAR_INFO.get("icon", "mdi:sword-cross")

        # Options (can be set via an options flow or service call)
        self._check_number: int = 0
        self._year_offset: int = 0
        self._system_designator: str | None = "SOL"
        self._fraction_method: str = "precise"  # 'precise' or 'lexicanum'

        _LOGGER.debug("Initialized %s", self._attr_name)

    # -------------------------------
    # Public properties
    # -------------------------------
    @property
    def state(self):
        return getattr(self, "_state", None)

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        attrs = super().extra_state_attributes
        if hasattr(self, "_imperial"):
            attrs.update({
                "imperial_check": self._imperial.check,
                "imperial_fraction": self._imperial.fraction,
                "imperial_year_in_millennium": self._imperial.year_in_millennium,
                "imperial_millennium": self._imperial.millennium,
                "system_designator": self._imperial.system,
                "terran_year": self._terran_year,
                "leap_year": self._leap_year,
                "fraction_method": self._fraction_method,
                "reference": CALENDAR_INFO.get("reference_url"),
                "notes": self._translate("notes"),
            })
        return attrs

    # -------------------------------
    # Options handling
    # -------------------------------
    def set_options(
        self,
        *,
        check_number: int | None = None,
        year_offset: int | None = None,
        system_designator: str | None = None,
        fraction_method: str | None = None,
    ) -> None:
        if check_number is not None:
            try:
                self._check_number = max(0, min(9, int(check_number)))
            except Exception:
                pass
        if year_offset is not None:
            try:
                self._year_offset = int(year_offset)
            except Exception:
                pass
        if system_designator is not None:
            self._system_designator = str(system_designator).strip() or None
        if fraction_method is not None:
            if fraction_method in ("precise", "lexicanum"):
                self._fraction_method = fraction_method

    # -------------------------------
    # Core conversions
    # -------------------------------
    @staticmethod
    def _is_leap_year(y: int) -> bool:
        return y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)

    @staticmethod
    def _millennium_of_year(y: int) -> int:
        # 1-1000 -> M01, 1001-2000 -> M02, etc.
        return (y - 1) // 1000 + 1

    @staticmethod
    def _year_in_millennium(y: int) -> int:
        return (y - 1) % 1000

    def _calc_fraction_precise(self, dt: datetime) -> int:
        # Fraction = floor(1000 * (elapsed seconds since Jan 1) / total seconds in year)
        start = datetime(dt.year, 1, 1, tzinfo=dt.tzinfo)
        end = datetime(dt.year + 1, 1, 1, tzinfo=dt.tzinfo)
        elapsed = (dt - start).total_seconds()
        total = (end - start).total_seconds()
        frac = int((elapsed / total) * 1000.0)
        if frac < 0:
            frac = 0
        if frac > 999:
            frac = 999
        return frac

    def _calc_fraction_lexicanum(self, dt: datetime) -> int:
        # Following Lexicanum's example method (Makr constant 0.11407955).
        # Determine ordinal day (1..365/366)
        ordinal = dt.timetuple().tm_yday  # 1-based
        # Determined hour: day * 24 + hour (per example)
        determined_hour = ordinal * 24 + dt.hour
        # Incorporate minutes/seconds as fractional hour for smoother steps
        determined_hour += dt.minute / 60.0 + dt.second / 3600.0
        makr = CALENDAR_INFO["imperial"]["makr_constant"]
        frac = int((determined_hour * makr))  # floor
        if frac < 0:
            frac = 0
        if frac > 999:
            frac = 999
        return frac

    def _to_imperial(self, dt: datetime) -> ImperialDate:
        # Apply year offset to emulate grimdark millennia if desired.
        terran_year = dt.year + self._year_offset
        millennium = self._millennium_of_year(terran_year)
        yim = self._year_in_millennium(terran_year)  # 0..999
        leap = self._is_leap_year(terran_year if self._year_offset else dt.year)

        if self._fraction_method == "lexicanum":
            fraction = self._calc_fraction_lexicanum(dt)
        else:
            fraction = self._calc_fraction_precise(dt)

        self._leap_year = leap
        self._terran_year = terran_year

        return ImperialDate(
            check=self._check_number,
            fraction=fraction,
            year_in_millennium=yim,
            millennium=millennium,
            system=self._system_designator
        )

    # -------------------------------
    # Update hook
    # -------------------------------
    def update(self) -> None:
        """Update the sensor state."""
        try:
            now = datetime.now()
            self._imperial = self._to_imperial(now)
            self._state = self._imperial.format()
        except Exception as exc:
            _LOGGER.exception("Failed to compute Imperial date: %s", exc)
            self._state = "error"