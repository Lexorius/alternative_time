"""Darian Calendar (Mars) implementation."""
from __future__ import annotations

from datetime import datetime
import logging
import math

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)


class DarianCalendarSensor(SensorEntity):
    """Sensor for displaying Darian Mars Calendar."""

    def __init__(self, base_name: str) -> None:
        """Initialize the Darian calendar sensor."""
        self._attr_name = f"{base_name} Darian Calendar"
        self._attr_unique_id = f"{base_name}_darian_calendar"
        self._attr_icon = "mdi:earth"
        self._state = None

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        darian_date = self._calculate_darian_date(datetime.now())
        
        return {
            "mars_year": darian_date["year"],
            "month_number": darian_date["month_num"],
            "month_name": darian_date["month_name"],
            "sol": darian_date["sol"],
            "week_sol": darian_date["week_sol"],
            "week_sol_name": darian_date["week_sol_name"],
            "season": darian_date["season"],
            "mars_sol_date": darian_date["mars_sol_date"],
            "total_sols": darian_date["total_sols"],
            "ls": darian_date["ls"],  # Solar longitude
            "earth_date": datetime.now().isoformat(),
            "month_type": darian_date["month_type"],
        }

    def _calculate_darian_date(self, earth_date: datetime) -> dict:
        """Calculate Darian calendar date from Earth date."""
        # Mars constants
        MARS_TROPICAL_YEAR = 686.9725  # Mars solar days
        MARS_DAY_IN_SECONDS = 88775.244  # seconds
        EARTH_DAY_IN_SECONDS = 86400.0
        
        # Epoch: January 1, 1970, 00:00:00 UTC (Unix epoch)
        # Mars Year 0 starts at April 28, 1608 (Telescopic epoch)
        # For simplicity, we'll use a modified calculation
        
        # Calculate days since J2000 epoch (January 1, 2000, 12:00 UTC)
        j2000_epoch = datetime(2000, 1, 1, 12, 0, 0)
        delta = earth_date - j2000_epoch
        days_since_j2000 = delta.total_seconds() / EARTH_DAY_IN_SECONDS
        
        # Calculate Mars Sol Date (MSD)
        # MSD epoch is December 29, 1873
        msd_epoch_jd = 2405522.0  # Julian date of MSD epoch
        j2000_jd = 2451545.0  # Julian date of J2000
        current_jd = j2000_jd + days_since_j2000
        
        # Mars Sol Date
        msd = (current_jd - msd_epoch_jd) / (MARS_DAY_IN_SECONDS / EARTH_DAY_IN_SECONDS)
        total_sols = int(msd)
        
        # Calculate Darian date
        # Darian calendar epoch is Mars Year 0, Sol 0
        # Each Mars year has 668 or 669 sols
        mars_years_elapsed = int(msd / MARS_TROPICAL_YEAR)
        sols_in_current_year = int(msd % MARS_TROPICAL_YEAR)
        
        # Darian months (24 months, alternating 27 and 28 sols)
        darian_months = [
            ("Sagittarius", 28), ("Dhanus", 28), ("Capricornus", 28),
            ("Makara", 28), ("Aquarius", 28), ("Kumbha", 28),
            ("Pisces", 28), ("Mina", 28), ("Aries", 28),
            ("Mesha", 28), ("Taurus", 28), ("Rishabha", 28),
            ("Gemini", 28), ("Mithuna", 28), ("Cancer", 27),
            ("Karka", 27), ("Leo", 27), ("Simha", 27),
            ("Virgo", 27), ("Kanya", 27), ("Libra", 27),
            ("Tula", 27), ("Scorpius", 27), ("Vrishika", 27)
        ]
        
        # Week sol names (7-sol week)
        week_sol_names = [
            "Sol Solis", "Sol Lunae", "Sol Martis", "Sol Mercurii",
            "Sol Jovis", "Sol Veneris", "Sol Saturni"
        ]
        
        # Determine month and sol
        sols_counted = 0
        current_month = 0
        current_sol = 0
        
        for i, (month_name, sols_in_month) in enumerate(darian_months):
            if sols_counted + sols_in_month > sols_in_current_year:
                current_month = i + 1
                current_sol = sols_in_current_year - sols_counted + 1
                current_month_name = month_name
                month_type = "28-sol month" if sols_in_month == 28 else "27-sol month"
                break
            sols_counted += sols_in_month
        else:
            # Last month of year
            current_month = 24
            current_month_name = darian_months[-1][0]
            current_sol = sols_in_current_year - sols_counted + 1
            month_type = "27-sol month"
        
        # Calculate week sol
        week_sol = total_sols % 7
        week_sol_name = week_sol_names[week_sol]
        
        # Determine season (4 seasons, 6 months each)
        if current_month <= 6:
            season = "Northern Spring / Southern Autumn"
        elif current_month <= 12:
            season = "Northern Summer / Southern Winter"
        elif current_month <= 18:
            season = "Northern Autumn / Southern Spring"
        else:
            season = "Northern Winter / Southern Summer"
        
        # Calculate approximate Ls (solar longitude)
        ls = (sols_in_current_year / MARS_TROPICAL_YEAR) * 360
        
        return {
            "year": mars_years_elapsed,
            "month_num": current_month,
            "month_name": current_month_name,
            "sol": current_sol,
            "week_sol": week_sol + 1,
            "week_sol_name": week_sol_name,
            "season": season,
            "mars_sol_date": msd,
            "total_sols": total_sols,
            "ls": round(ls, 1),
            "month_type": month_type,
        }

    def update(self) -> None:
        """Update the sensor."""
        darian_date = self._calculate_darian_date(datetime.now())
        
        # Format: Year Month Sol (Week Sol)
        # Example: "216 Gemini 15 (Sol Martis)"
        self._state = f"{darian_date['year']} {darian_date['month_name']} {darian_date['sol']}"