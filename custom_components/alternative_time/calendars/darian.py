"""Darian Calendar (Mars) implementation - Version 2.5.1."""
from __future__ import annotations

import logging
import math
from datetime import datetime, timezone
from typing import Any, Dict

from homeassistant.core import HomeAssistant

from ..astro import mars_sol_date, mars_solar_longitude
from ..sensor import AlternativeTimeSensorBase

_LOGGER = logging.getLogger(__name__)

# ============================================
# CALENDAR METADATA
# ============================================

# Update interval in seconds (3600 seconds = 1 hour)
UPDATE_INTERVAL = 3600

# Complete calendar information for auto-discovery
CALENDAR_INFO = {
    "id": "darian",
    "version": "2.5.1",
    "icon": "mdi:rocket-launch",
    "category": "space",
    "accuracy": "scientific",
    "update_interval": UPDATE_INTERVAL,

    # Multi-language names
    "name": {
        "en": "Darian Calendar (Mars)",
        "de": "Darischer Kalender (Mars)",
        "es": "Calendario Dariano (Marte)",
        "fr": "Calendrier Darien (Mars)",
        "it": "Calendario Dariano (Marte)",
        "nl": "Dariaanse Kalender (Mars)",
        "pl": "Kalendarz Dariański (Mars)",
        "pt": "Calendário Dariano (Marte)",
        "ru": "Дарианский календарь (Марс)",
        "ja": "ダリアン暦（火星）",
        "zh": "达里安历（火星）",
        "ko": "다리안 달력 (화성)"
    },

    # Translations for compatibility
    "translations": {
        "en": {
            "name": "Darian Calendar (Mars)",
            "description": "Mars calendar with 24 months and 668 sols per year"
        },
        "de": {
            "name": "Darischer Kalender (Mars)",
            "description": "Mars-Kalender mit 24 Monaten und 668 Sols pro Jahr"
        },
        "es": {
            "name": "Calendario Dariano (Marte)",
            "description": "Calendario marciano con 24 meses y 668 soles por año"
        },
        "fr": {
            "name": "Calendrier Darien (Mars)",
            "description": "Calendrier martien avec 24 mois et 668 sols par an"
        },
        "it": {
            "name": "Calendario Dariano (Marte)",
            "description": "Calendario marziano con 24 mesi e 668 sol per anno"
        },
        "nl": {
            "name": "Dariaanse Kalender (Mars)",
            "description": "Mars kalender met 24 maanden en 668 sols per jaar"
        },
        "pl": {
            "name": "Kalendarz Dariański (Mars)",
            "description": "Kalendarz marsjański z 24 miesiącami i 668 solami rocznie"
        },
        "pt": {
            "name": "Calendário Dariano (Marte)",
            "description": "Calendário marciano com 24 meses e 668 sóis por ano"
        },
        "ru": {
            "name": "Дарианский календарь (Марс)",
            "description": "Марсианский календарь с 24 месяцами и 668 солами в году"
        },
        "ja": {
            "name": "ダリアン暦（火星）",
            "description": "24ヶ月、年間668ソルの火星暦"
        },
        "zh": {
            "name": "达里安历（火星）",
            "description": "24个月，每年668火星日的火星历"
        },
        "ko": {
            "name": "다리안 달력 (화성)",
            "description": "24개월, 연간 668솔의 화성 달력"
        }
    },

    # Short descriptions for UI
    "description": {
        "en": "Mars calendar with 24 months and 668 sols per year (e.g. 15 Gemini 217)",
        "de": "Mars-Kalender mit 24 Monaten und 668 Sols pro Jahr (z.B. 15 Gemini 217)",
        "es": "Calendario marciano con 24 meses y 668 soles por año (ej. 15 Gemini 217)",
        "fr": "Calendrier martien avec 24 mois et 668 sols par an (ex. 15 Gemini 217)",
        "it": "Calendario marziano con 24 mesi e 668 sol per anno (es. 15 Gemini 217)",
        "nl": "Mars kalender met 24 maanden en 668 sols per jaar (bijv. 15 Gemini 217)",
        "pl": "Kalendarz marsjański z 24 miesiącami i 668 solami rocznie (np. 15 Gemini 217)",
        "pt": "Calendário marciano com 24 meses e 668 sóis por ano (ex. 15 Gemini 217)",
        "ru": "Марсианский календарь с 24 месяцами и 668 солами в году (напр. 15 Gemini 217)",
        "ja": "24ヶ月、年間668ソルの火星暦（例：15 Gemini 217）",
        "zh": "24个月，每年668火星日的火星历（例：15 Gemini 217）",
        "ko": "24개월, 연간 668솔의 화성 달력 (예: 15 Gemini 217)"
    },

    # Darian-specific data
    "darian_data": {
        "sols_per_year": 668,  # standard year
        "sols_per_leap_year": 669,

        # 24 months in four quarters. The first five months of a quarter have
        # 28 sols, the sixth has 27. In a leap year the last month (Vrishika)
        # gets the leap sol and has 28.
        "months": [
            {"name": "Sagittarius", "sols": 28, "type": "zodiac", "season": "Spring (North)"},
            {"name": "Dhanus", "sols": 28, "type": "sanskrit", "season": "Spring (North)"},
            {"name": "Capricornus", "sols": 28, "type": "zodiac", "season": "Spring (North)"},
            {"name": "Makara", "sols": 28, "type": "sanskrit", "season": "Spring (North)"},
            {"name": "Aquarius", "sols": 28, "type": "zodiac", "season": "Spring (North)"},
            {"name": "Kumbha", "sols": 27, "type": "sanskrit", "season": "Spring (North)"},
            {"name": "Pisces", "sols": 28, "type": "zodiac", "season": "Summer (North)"},
            {"name": "Mina", "sols": 28, "type": "sanskrit", "season": "Summer (North)"},
            {"name": "Aries", "sols": 28, "type": "zodiac", "season": "Summer (North)"},
            {"name": "Mesha", "sols": 28, "type": "sanskrit", "season": "Summer (North)"},
            {"name": "Taurus", "sols": 28, "type": "zodiac", "season": "Summer (North)"},
            {"name": "Rishabha", "sols": 27, "type": "sanskrit", "season": "Summer (North)"},
            {"name": "Gemini", "sols": 28, "type": "zodiac", "season": "Autumn (North)"},
            {"name": "Mithuna", "sols": 28, "type": "sanskrit", "season": "Autumn (North)"},
            {"name": "Cancer", "sols": 28, "type": "zodiac", "season": "Autumn (North)"},
            {"name": "Karka", "sols": 28, "type": "sanskrit", "season": "Autumn (North)"},
            {"name": "Leo", "sols": 28, "type": "zodiac", "season": "Autumn (North)"},
            {"name": "Simha", "sols": 27, "type": "sanskrit", "season": "Autumn (North)"},
            {"name": "Virgo", "sols": 28, "type": "zodiac", "season": "Winter (North)"},
            {"name": "Kanya", "sols": 28, "type": "sanskrit", "season": "Winter (North)"},
            {"name": "Libra", "sols": 28, "type": "zodiac", "season": "Winter (North)"},
            {"name": "Tula", "sols": 28, "type": "sanskrit", "season": "Winter (North)"},
            {"name": "Scorpius", "sols": 28, "type": "zodiac", "season": "Winter (North)"},
            {"name": "Vrishika", "sols": 27, "type": "sanskrit", "season": "Winter (North)"}
        ],

        # Week sols (7-sol week, restarts on Sol Solis every month)
        "week_sols": [
            {"name": "Sol Solis", "meaning": "Sun's day"},
            {"name": "Sol Lunae", "meaning": "Moon's day"},
            {"name": "Sol Martis", "meaning": "Mars' day"},
            {"name": "Sol Mercurii", "meaning": "Mercury's day"},
            {"name": "Sol Jovis", "meaning": "Jupiter's day"},
            {"name": "Sol Veneris", "meaning": "Venus' day"},
            {"name": "Sol Saturni", "meaning": "Saturn's day"}
        ]
    },

    # Configuration options for this calendar
    "config_options": {
        "show_week_sol": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show Week Sol Name",
                "de": "Wochensol-Name anzeigen",
                "es": "Mostrar Nombre del Sol Semanal",
                "fr": "Afficher le Nom du Sol de la Semaine",
                "it": "Mostra Nome del Sol Settimanale",
                "nl": "Toon Week Sol Naam",
                "pl": "Pokaż nazwę tygodniowego sola",
                "pt": "Mostrar Nome do Sol Semanal",
                "ru": "Показать название недельного сола",
                "ja": "週ソル名を表示",
                "zh": "显示周火星日名称",
                "ko": "주 솔 이름 표시"
            },
            "description": {
                "en": "Display day of week (Sol Solis, Sol Lunae, etc.)",
                "de": "Wochentag anzeigen (Sol Solis, Sol Lunae, usw.)",
                "es": "Mostrar día de la semana (Sol Solis, Sol Lunae, etc.)",
                "fr": "Afficher le jour de la semaine (Sol Solis, Sol Lunae, etc.)"
            }
        },
        "show_msd": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show Mars Sol Date",
                "de": "Mars Sol-Datum anzeigen",
                "es": "Mostrar Fecha Sol de Marte",
                "fr": "Afficher la Date Sol de Mars",
                "it": "Mostra Data Sol di Marte",
                "nl": "Toon Mars Sol Datum",
                "pl": "Pokaż datę Sol Marsa",
                "pt": "Mostrar Data Sol de Marte",
                "ru": "Показать марсианскую солнечную дату",
                "ja": "火星ソル日付を表示",
                "zh": "显示火星太阳日期",
                "ko": "화성 솔 날짜 표시"
            },
            "description": {
                "en": "Display MSD (Mars Sol Date) number",
                "de": "MSD (Mars Sol-Datum) Nummer anzeigen",
                "es": "Mostrar número MSD (Fecha Sol de Marte)",
                "fr": "Afficher le numéro MSD (Date Sol de Mars)"
            }
        }
    }
}


class DarianCalendarSensor(AlternativeTimeSensorBase):
    """Sensor for displaying Darian Mars Calendar."""

    # Class-level update interval
    UPDATE_INTERVAL = UPDATE_INTERVAL

    def __init__(self, base_name: str, hass: HomeAssistant) -> None:
        """Initialize the Darian calendar sensor."""
        super().__init__(base_name, hass)

        # Store CALENDAR_INFO as instance variable
        self._calendar_info = CALENDAR_INFO

        # Get translated name from metadata
        calendar_name = self._translate('name', 'Darian Calendar')

        # Set sensor attributes
        self._attr_name = f"{base_name} {calendar_name}"
        self._attr_unique_id = f"{base_name}_darian_calendar"
        self._attr_icon = CALENDAR_INFO.get("icon", "mdi:rocket-launch")

        # Configuration options with defaults
        config_defaults = CALENDAR_INFO.get("config_options", {})
        self._show_week_sol = config_defaults.get("show_week_sol", {}).get("default", True)
        self._show_msd = config_defaults.get("show_msd", {}).get("default", True)

        # Darian data
        self._darian_data = CALENDAR_INFO["darian_data"]

        # Initialize state
        self._state = "0 Sagittarius 1"
        self._darian_date = {}

        # Flag to track if options have been loaded
        self._options_loaded = False

        _LOGGER.debug(f"Initialized Darian Calendar sensor: {self._attr_name}")
        _LOGGER.debug(f"  Default settings: week_sol={self._show_week_sol}, msd={self._show_msd}")

    def _load_options(self) -> None:
        """Load plugin options after IDs are set."""
        if self._options_loaded:
            return

        try:
            options = self.get_plugin_options()
            if options:
                # Update configuration from plugin options
                self._show_week_sol = options.get("show_week_sol", self._show_week_sol)
                self._show_msd = options.get("show_msd", self._show_msd)

                _LOGGER.debug(f"Darian sensor loaded options: week_sol={self._show_week_sol}, msd={self._show_msd}")
            else:
                _LOGGER.debug("Darian sensor using default options - no custom options found")

            self._options_loaded = True
        except Exception as e:
            _LOGGER.debug(f"Darian sensor could not load options yet: {e}")

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        await super().async_added_to_hass()

        # Try to load options now that IDs should be set
        self._load_options()

        # Perform initial update
        self.update()

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes."""
        attrs = super().extra_state_attributes or {}

        # Add Darian-specific attributes
        if self._darian_date:
            attrs.update(self._darian_date)

            # Add description in user's language
            attrs["description"] = self._translate('description')

            # Add current configuration
            attrs["show_week_sol_setting"] = self._show_week_sol
            attrs["show_msd_setting"] = self._show_msd

        return attrs

    # Sols between the Darian epoch (1 Sagittarius 0, in 1609) and the epoch of
    # the Mars Sol Date (1873): "Mars Julian Sol" = MSD + 94129.
    _EPOCH_OFFSET_SOLS = 94129

    @staticmethod
    def _is_leap_year(year: int) -> bool:
        """Leap years have 669 sols: odd years, and years divisible by 10
        unless they are centuries not divisible by 1000 (rule for years 0-2000)."""
        return year % 2 == 1 or (year % 10 == 0 and (year % 100 != 0 or year % 1000 == 0))

    def _calculate_darian_date(self, earth_date: datetime) -> Dict[str, Any]:
        """Calculate the Darian calendar date for a UTC datetime."""
        msd = mars_sol_date(earth_date)
        total_sols = math.floor(msd) + self._EPOCH_OFFSET_SOLS  # sols since 1 Sagittarius 0

        # Year: walk forward from year 0 (a few hundred steps, once per update)
        year = 0
        remaining = total_sols
        while True:
            sols_in_year = 669 if self._is_leap_year(year) else 668
            if remaining < sols_in_year:
                break
            remaining -= sols_in_year
            year += 1
        sol_of_year = remaining

        # Month and sol
        months = self._darian_data["months"]
        month_index = 0
        sols_in_month = months[0]["sols"]
        for month_index, month_data in enumerate(months):
            sols_in_month = month_data["sols"]
            if month_index == len(months) - 1 and sols_in_year == 669:
                sols_in_month += 1  # the leap sol is the last sol of Vrishika
            if remaining < sols_in_month:
                break
            remaining -= sols_in_month
        current_sol = remaining + 1
        month_data = months[month_index]
        month_name = month_data["name"]

        # The week restarts on Sol Solis at the start of every month
        week_sol_index = (current_sol - 1) % 7
        week_sol_data = self._darian_data["week_sols"][week_sol_index]

        full_date = f"{current_sol} {month_name} {year}"
        if self._show_week_sol:
            full_date += f" ({week_sol_data['name']})"

        result = {
            "year": year,
            "month_number": month_index + 1,
            "month_name": month_name,
            "month_type": month_data["type"],
            "sol": current_sol,
            "sols_in_month": sols_in_month,
            "week_sol": week_sol_index + 1,
            "week_sol_name": week_sol_data["name"],
            "week_sol_meaning": week_sol_data["meaning"],
            "season": month_data["season"],
            "sol_of_year": sol_of_year + 1,
            "total_sols": total_sols,
            "sols_in_year": sols_in_year,
            "earth_date": earth_date.strftime("%Y-%m-%d"),
            "full_date": full_date
        }

        if self._show_msd:
            result["mars_sol_date"] = round(msd, 4)
            result["msd_integer"] = math.floor(msd)

        result["solar_longitude"] = round(mars_solar_longitude(earth_date), 1)

        return result

    def update(self) -> None:
        """Update the sensor."""
        # Ensure options are loaded
        if not self._options_loaded:
            self._load_options()

        try:
            now = datetime.now(timezone.utc)
            self._darian_date = self._calculate_darian_date(now)

            # Set state to formatted Darian date
            self._state = self._darian_date.get("full_date", "0 Sagittarius 1")

            _LOGGER.debug(f"Updated Darian Calendar to {self._state}")
        except Exception as e:
            _LOGGER.error(f"Error updating Darian calendar: {e}", exc_info=True)
            self._state = "ERROR"
