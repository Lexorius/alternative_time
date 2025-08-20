"""Mars Time (Darian Calendar) implementation - Version 2.6."""
from __future__ import annotations

from datetime import datetime
import math
import logging
from typing import Dict, Any, Optional

from homeassistant.core import HomeAssistant
from ..sensor import AlternativeTimeSensorBase

_LOGGER = logging.getLogger(__name__)

# ============================================
# CALENDAR METADATA
# ============================================

# Update interval in seconds (60 seconds = 1 minute)
UPDATE_INTERVAL = 60

# Complete calendar information for auto-discovery
CALENDAR_INFO = {
    "id": "mars",
    "version": "2.6.0",
    "icon": "mdi:rocket-launch",
    "category": "space",
    "accuracy": "scientific",
    "update_interval": UPDATE_INTERVAL,

    # Optional UI header (used by the config wizard to render a heading/intro)
    "header": {
        "en": "# 🚀 Mars Time (Darian)\n\n_Configure Mars time with localized timezones and mission context._",
        "de": "# 🚀 Marszeit (Darian)\n\n_Konfiguriere Mars-Zeit mit lokalisierten Zeitzonen und Missions-Kontext._",
    },

    # Multi-language names
    "name": {
        "en": "Mars Sol Time",
        "de": "Mars Sol-Zeit",
        "es": "Tiempo Sol de Marte",
        "fr": "Temps Sol de Mars",
        "it": "Tempo Sol di Marte",
        "nl": "Mars Sol Tijd",
        "pt": "Tempo Sol de Marte",
        "ru": "Марсианское солнечное время",
        "ja": "火星ソル時間",
        "zh": "火星太阳时",
        "ko": "화성 솔 시간",
    },

    # Short descriptions for UI
    "description": {
        "en": "Mars Sol Date (MSD) and local solar time on Mars",
        "de": "Mars Sol-Datum (MSD) und lokale Sonnenzeit auf dem Mars",
        "es": "Fecha Sol de Marte (MSD) y hora solar local en Marte",
        "fr": "Date Sol de Mars (MSD) et heure solaire locale sur Mars",
        "it": "Data Sol di Marte (MSD) e ora solare locale su Marte",
        "nl": "Mars Sol Datum (MSD) en lokale zonnetijd op Mars",
        "pt": "Data Sol de Marte (MSD) e hora solar local em Marte",
        "ru": "Марсианская солнечная дата (MSD) и местное солнечное время на Марсе",
        "ja": "火星ソル日付（MSD）と火星の地方太陽時",
        "zh": "火星太阳日（MSD）和火星当地太阳时",
        "ko": "화성 솔 날짜(MSD)와 화성 현지 태양시",
    },

    # ===== Extra data consumed by the config flow (builds the timezone dropdown) =====
    # If present, the wizard uses these groups to populate the "timezone" selector.
    "timezone_data": {
        "regions": {
            "Standard": ["MTC"],
            "Provinces": ["AMT", "OLY", "ELY", "CHA", "MAR", "ARA", "THR", "HEL"],
            "Missions": ["VIK", "PTH", "OPP", "SPI", "CUR", "PER"],
        }
    },

    # Mars-specific data
    "mars_data": {
        # Physical constants
        "sol_duration_seconds": 88775.244147,  # Mars solar day in Earth seconds
        "tropical_year_sols": 668.5991,        # Mars year in sols
        "j2000_epoch": 946727935.816,          # J2000 epoch in Unix timestamp
        "mars_epoch_msd": 44796.0,             # MSD at J2000 epoch

        # === Localized Mars timezones ===
        # Each entry provides:
        # - abbr: short code
        # - longitude: reference meridian (degrees East, −West)
        # - names: localized long name
        # - description: localized extra label (area/feature)
        # - group: for UI grouping (Standard/Provinces/Missions)
        "timezones": {
            "MTC": {
                "abbr": "MTC",
                "longitude": 0,
                "group": "Standard",
                "names": {"en": "Mars Coordinated Time", "de": "Mars-Koordinierte Zeit"},
                "description": {"en": "Prime Meridian (0°)", "de": "Nullmeridian (0°)"},
            },
            "AMT": {
                "abbr": "AMT",
                "longitude": -158,
                "group": "Provinces",
                "names": {"en": "Amazonis Time", "de": "Amazonis-Zeit"},
                "description": {"en": "Amazonis Planitia (~158°W)", "de": "Amazonis Planitia (~158°W)"},
            },
            "OLY": {
                "abbr": "OLY",
                "longitude": -134,
                "group": "Provinces",
                "names": {"en": "Olympus Time", "de": "Olympus-Zeit"},
                "description": {"en": "Olympus Mons (~134°W)", "de": "Olympus Mons (~134°W)"},
            },
            "ELY": {
                "abbr": "ELY",
                "longitude": 135,
                "group": "Provinces",
                "names": {"en": "Elysium Time", "de": "Elysium-Zeit"},
                "description": {"en": "Elysium Planitia (~135°E)", "de": "Elysium Planitia (~135°O)"},
            },
            "CHA": {
                "abbr": "CHA",
                "longitude": -33,
                "group": "Provinces",
                "names": {"en": "Chryse Time", "de": "Chryse-Zeit"},
                "description": {"en": "Chryse Planitia (~33°W)", "de": "Chryse Planitia (~33°W)"},
            },
            "MAR": {
                "abbr": "MAR",
                "longitude": -59,
                "group": "Provinces",
                "names": {"en": "Marineris Time", "de": "Marineris-Zeit"},
                "description": {"en": "Valles Marineris (~59°W)", "de": "Valles Marineris (~59°W)"},
            },
            "ARA": {
                "abbr": "ARA",
                "longitude": 20,
                "group": "Provinces",
                "names": {"en": "Arabia Time", "de": "Arabia-Zeit"},
                "description": {"en": "Arabia Terra (~20°E)", "de": "Arabia Terra (~20°O)"},
            },
            "THR": {
                "abbr": "THR",
                "longitude": -125,
                "group": "Provinces",
                "names": {"en": "Tharsis Time", "de": "Tharsis-Zeit"},
                "description": {"en": "Tharsis region (~125°W)", "de": "Region Tharsis (~125°W)"},
            },
            "HEL": {
                "abbr": "HEL",
                "longitude": 70,
                "group": "Provinces",
                "names": {"en": "Hellas Time", "de": "Hellas-Zeit"},
                "description": {"en": "Hellas Planitia (~70°E)", "de": "Hellas Planitia (~70°O)"},
            },
            # Mission landing zones (nominal longitudes)
            "VIK": {
                "abbr": "VIK",
                "longitude": -48.0,
                "group": "Missions",
                "names": {"en": "Viking Lander Time", "de": "Viking-Lander-Zeit"},
                "description": {"en": "Viking landers (Chryse/Utopia)", "de": "Viking-Lander (Chryse/Utopia)"},
            },
            "PTH": {
                "abbr": "PTH",
                "longitude": -33.55,
                "group": "Missions",
                "names": {"en": "Pathfinder Time", "de": "Pathfinder-Zeit"},
                "description": {"en": "Mars Pathfinder (Ares Vallis)", "de": "Mars Pathfinder (Ares Vallis)"},
            },
            "OPP": {
                "abbr": "OPP",
                "longitude": -5.53,
                "group": "Missions",
                "names": {"en": "Opportunity Time", "de": "Opportunity-Zeit"},
                "description": {"en": "MER-B Opportunity (Meridiani)", "de": "MER-B Opportunity (Meridiani)"},
            },
            "SPI": {
                "abbr": "SPI",
                "longitude": 175.47,
                "group": "Missions",
                "names": {"en": "Spirit Time", "de": "Spirit-Zeit"},
                "description": {"en": "MER-A Spirit (Gusev Crater)", "de": "MER-A Spirit (Gusev-Krater)"},
            },
            "CUR": {
                "abbr": "CUR",
                "longitude": 137.44,
                "group": "Missions",
                "names": {"en": "Curiosity Time", "de": "Curiosity-Zeit"},
                "description": {"en": "MSL Curiosity (Gale Crater)", "de": "MSL Curiosity (Gale-Krater)"},
            },
            "PER": {
                "abbr": "PER",
                "longitude": 77.45,
                "group": "Missions",
                "names": {"en": "Perseverance Time", "de": "Perseverance-Zeit"},
                "description": {"en": "Mars 2020 Perseverance (Jezero)", "de": "Mars 2020 Perseverance (Jezero)"},
            },
        },

        # Mission landing dates (MSD) for sol counters
        "missions": {
            "Viking 1": 34809,
            "Viking 2": 34895,
            "Pathfinder": 46236,
            "Spirit": 49269,
            "Opportunity": 49290,
            "Curiosity": 49269,
            "Perseverance": 52304,
        },

        # Map timezone -> canonical mission name (for sol counters in attributes)
        "timezone_missions": {
            "VIK": "Viking 1",
            "PTH": "Pathfinder",
            "OPP": "Opportunity",
            "SPI": "Spirit",
            "CUR": "Curiosity",
            "PER": "Perseverance",
        },
    },

    # Additional metadata
    "reference_url": "https://en.wikipedia.org/wiki/Timekeeping_on_Mars",
    "documentation_url": "https://www.giss.nasa.gov/tools/mars24/",
    "origin": "NASA/JPL",
    "created_by": "Various Mars missions",

    # Example format
    "example": "Sol 52304, 14:26:35 MTC",
    "example_meaning": "Mars Sol Date 52304, Mars Coordinated Time",

    # Related calendars
    "related": ["julian", "gregorian", "unix"],

    # Tags for searching and filtering
    "tags": [
        "mars",
        "space",
        "planetary",
        "sol",
        "msd",
        "nasa",
        "jpl",
        "scientific",
        "astronomical",
        "mission",
        "exploration",
        "rover",
        "perseverance",
        "curiosity",
        "mtc",
    ],

    # Special features
    "features": {
        "supports_timezones": True,
        "supports_missions": True,
        "supports_seasons": True,
        "continuous_count": True,
        "precision": "second",
        "solar_longitude": True,
    },

    # Configuration options for this calendar
    # NOTE: we intentionally omit an explicit "options" list for "timezone"
    # so the config flow can auto-build the select from "timezone_data".
    "config_options": {
        "timezone": {
            "type": "select",
            "default": "MTC",
            "label": {
                "en": "Mars timezone",
                "de": "Mars-Zeitzone",
                "fr": "Fuseau horaire martien",
                "es": "Zona horaria marciana",
            },
            "description": {
                "en": "Choose Mars timezone (localized labels shown in attributes).",
                "de": "Mars-Zeitzone wählen (lokalisierte Bezeichnungen in den Attributen).",
                "fr": "Choisissez le fuseau horaire martien (libellés localisés dans les attributs).",
                "es": "Elige la zona horaria marciana (etiquetas localizadas en atributos).",
            },
        },
        "show_mission_sol": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show mission sol",
                "de": "Missions-Sol anzeigen",
                "fr": "Afficher sol de mission",
                "es": "Mostrar sol de misión",
            },
            "description": {
                "en": "Show mission sol for selected timezone (if applicable).",
                "de": "Zeige Missions-Sol für die gewählte Zeitzone (falls zutreffend).",
                "fr": "Afficher le sol de mission pour le fuseau choisi (si applicable).",
                "es": "Mostrar el sol de misión para la zona elegida (si procede).",
            },
        },
        "show_solar_longitude": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show solar longitude (Ls)",
                "de": "Sonnenlänge (Ls) anzeigen",
                "fr": "Afficher la longitude solaire (Ls)",
                "es": "Mostrar longitud solar (Ls)",
            },
            "description": {
                "en": "Include Ls/EoT diagnostics in attributes.",
                "de": "Ls/EoT-Diagnose in den Attributen anzeigen.",
                "fr": "Inclure Ls/EoT dans les attributs.",
                "es": "Incluir Ls/EoT en los atributos.",
            },
        },
        "show_earth_time": {
            "type": "boolean",
            "default": False,
            "label": {
                "en": "Show Earth time (UTC)",
                "de": "Erdzeit (UTC) anzeigen",
                "fr": "Afficher l'heure terrestre (UTC)",
                "es": "Mostrar hora terrestre (UTC)",
            },
            "description": {
                "en": "Also show Earth UTC time in attributes.",
                "de": "Auch Erd-UTC in den Attributen anzeigen.",
                "fr": "Afficher aussi l'heure UTC terrestre dans les attributs.",
                "es": "Mostrar además la hora UTC terrestre en los atributos.",
            },
        },
    },
}


class MarsTimeSensor(AlternativeTimeSensorBase):
    """Sensor for displaying Mars time with localized timezone metadata."""

    # Class-level update interval
    UPDATE_INTERVAL = 60  # Update every minute

    def __init__(self, base_name: str, hass: HomeAssistant) -> None:
        """Initialize the Mars time sensor."""
        super().__init__(base_name, hass)

        # Store CALENDAR_INFO as instance variable
        self._calendar_info = CALENDAR_INFO

        # Localized name for the entity
        calendar_name = self._translate("name", "Mars Sol Time")

        # Set sensor attributes
        self._attr_name = f"{base_name} {calendar_name}"
        self._attr_unique_id = f"{base_name}_mars_time"
        self._attr_icon = CALENDAR_INFO.get("icon", "mdi:rocket-launch")

        # Options (will be refreshed on each update, in case user changes them)
        self._mars_timezone = "MTC"
        self._show_mission_sol = True
        self._show_solar_longitude = True
        self._show_earth_time = False

        # Mars data
        self._mars_data = CALENDAR_INFO["mars_data"]

        # Initialize state
        self._state = None
        self._mars_time_info: Dict[str, Any] = {}

        _LOGGER.debug(f"Initialized Mars Time sensor: {self._attr_name}")

    # ---------- Utilities ----------

    def _lang(self) -> str:
        """Primary language code ('de', 'en', ...)."""
        try:
            lang = getattr(self._hass.config, "language", "en")
        except Exception:
            lang = "en"
        # primary tag
        if "-" in lang:
            return lang.split("-")[0]
        if "_" in lang:
            return lang.split("_")[0]
        return lang or "en"

    def _tz_entry(self, abbr: str) -> Optional[Dict[str, Any]]:
        return self._mars_data.get("timezones", {}).get(abbr)

    def _tz_localized_name(self, abbr: str) -> str:
        tz = self._tz_entry(abbr) or {}
        names = tz.get("names")
        if isinstance(names, dict):
            return names.get(self._lang(), names.get("en", abbr))
        return str(names or abbr)

    def _tz_localized_desc(self, abbr: str) -> str:
        tz = self._tz_entry(abbr) or {}
        desc = tz.get("description")
        if isinstance(desc, dict):
            return desc.get(self._lang(), desc.get("en", ""))
        return str(desc or "")

    # ---------- HA properties ----------

    @property
    def state(self):
        """Return the state of the sensor (short: local time + code)."""
        return self._state

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes (rich, localized metadata)."""
        attrs = super().extra_state_attributes

        if hasattr(self, "_mars_time_info"):
            attrs.update(self._mars_time_info)

            # Add description in user's language
            attrs["description"] = self._translate("description")

            # Add reference
            attrs["reference"] = CALENDAR_INFO.get("reference_url", "")

            # Localized timezone details
            tz = self._mars_timezone
            attrs["timezone_code"] = tz
            attrs["timezone_name"] = self._tz_localized_name(tz)
            attrs["timezone_description"] = self._tz_localized_desc(tz)

            tz_meta = self._tz_entry(tz) or {}
            attrs["timezone_longitude"] = tz_meta.get("longitude", 0)
            attrs["timezone_offset_hours"] = round((tz_meta.get("longitude", 0) / 15.0), 3)
            attrs["timezone_group"] = tz_meta.get("group", "")

            # Catalog of all timezones (localized) for UI/frontend usage
            catalog = {}
            for code, meta in (self._mars_data.get("timezones") or {}).items():
                catalog[code] = {
                    "name": self._tz_localized_name(code),
                    "description": self._tz_localized_desc(code),
                    "longitude": meta.get("longitude", 0),
                    "group": meta.get("group", ""),
                }
            attrs["timezone_catalog"] = catalog

        return attrs

    # ---------- Core calculations ----------

    def _calculate_mars_time(self, earth_utc: datetime) -> Dict[str, Any]:
        """Calculate Mars time from Earth UTC time."""
        # Convert to Unix timestamp
        unix_timestamp = earth_utc.timestamp()

        # Calculate Mars Sol Date (MSD)
        # MSD = (Unix timestamp - J2000 epoch) / seconds per sol + MSD at J2000
        elapsed_seconds = unix_timestamp - self._mars_data["j2000_epoch"]
        elapsed_sols = elapsed_seconds / self._mars_data["sol_duration_seconds"]
        msd = self._mars_data["mars_epoch_msd"] + elapsed_sols

        # Calculate Mars Coordinated Time (MTC) - Mean Solar Time at Prime Meridian
        sol_fraction = msd % 1
        mtc_hours = int(sol_fraction * 24)
        mtc_minutes = int((sol_fraction * 24 - mtc_hours) * 60)
        mtc_seconds = int(((sol_fraction * 24 - mtc_hours) * 60 - mtc_minutes) * 60)
        mtc_time = f"{mtc_hours:02d}:{mtc_minutes:02d}:{mtc_seconds:02d}"

        # Solar longitude (Ls) – simplified seasonal indicator
        mars_year_fraction = (msd / self._mars_data["tropical_year_sols"]) % 1
        ls = mars_year_fraction * 360.0  # Degrees

        # Determine season (hemispheric)
        if 0 <= ls < 90:
            season = "Northern Spring / Southern Fall"
        elif 90 <= ls < 180:
            season = "Northern Summer / Southern Winter"
        elif 180 <= ls < 270:
            season = "Northern Fall / Southern Spring"
        else:
            season = "Northern Winter / Southern Summer"

        # Local solar time for selected timezone
        tz_meta = self._tz_entry(self._mars_timezone) or {"longitude": 0}
        tz_long = float(tz_meta.get("longitude", 0))
        timezone_offset = tz_long / 15.0  # Convert longitude to hours (Mars: 15° per local hour)

        # Equation of time correction (simplified)
        # Mars' eccentric orbit causes larger variations
        eot_degrees = 2.861 * math.sin(2 * math.radians(ls)) - 0.071 * math.sin(4 * math.radians(ls))
        eot_minutes = eot_degrees * 4.0  # Convert degrees to minutes of time

        # Subsolar longitude (approx.)
        subsolar_longitude = (sol_fraction * 360.0 + eot_degrees) % 360.0

        # Local Mean Solar Time (LMST)
        lmst_hours = (mtc_hours + timezone_offset) % 24
        lmst_minutes = mtc_minutes
        lmst_seconds = mtc_seconds

        # Local True Solar Time (LTST) applying EoT
        total_minutes = lmst_hours * 60.0 + lmst_minutes + eot_minutes
        ltst_hours = int(total_minutes // 60) % 24
        ltst_minutes = int(total_minutes % 60)

        local_time = f"{ltst_hours:02d}:{ltst_minutes:02d}:{lmst_seconds:02d}"

        # Sunrise/sunset crude estimate (equatorial assumption)
        sunrise_hour = 6 - int(eot_minutes / 60.0)
        sunset_hour = 18 - int(eot_minutes / 60.0)
        sunrise_time = f"{sunrise_hour:02d}:00"
        sunset_time = f"{sunset_hour:02d}:00"

        # Mission sol lookup by timezone (if mapped)
        mission_name = (self._mars_data.get("timezone_missions") or {}).get(self._mars_timezone)
        mission_sol: Optional[int] = None
        if mission_name:
            landing_msd = (self._mars_data.get("missions") or {}).get(mission_name)
            if landing_msd is not None:
                mission_sol = int(msd - int(landing_msd))

        # Result payload
        result: Dict[str, Any] = {
            "msd": round(msd, 4),
            "sol_number": int(msd),
            "mtc": mtc_time,
            "local_time": local_time,
            "timezone_offset": round(timezone_offset, 4),
            "season": season,
            "sunrise": sunrise_time,
            "sunset": sunset_time,
            "full_display": f"{local_time} {self._mars_timezone}",
        }

        if CALENDAR_INFO["features"].get("solar_longitude") and self._show_solar_longitude:
            result["solar_longitude"] = round(ls, 1)
            result["subsolar_longitude"] = round(subsolar_longitude, 1)
            result["equation_of_time"] = round(eot_minutes, 1)

        if self._show_mission_sol and mission_sol is not None and mission_name:
            result["mission_sol"] = mission_sol
            result["mission_name"] = mission_name
            result["full_display"] += f" (Sol {mission_sol})"

        if self._show_earth_time:
            result["earth_time_utc"] = earth_utc.strftime("%Y-%m-%d %H:%M:%S UTC")

        return result

    # ---------- Update loop ----------

    def update(self) -> None:
        """Update the sensor."""
        # Refresh options on each update (handles user changes live)
        opts = self.get_plugin_options() or {}
        self._mars_timezone = str(opts.get("timezone", self._mars_timezone or "MTC")) or "MTC"
        self._show_mission_sol = bool(opts.get("show_mission_sol", self._show_mission_sol))
        self._show_solar_longitude = bool(opts.get("show_solar_longitude", self._show_solar_longitude))
        self._show_earth_time = bool(opts.get("show_earth_time", self._show_earth_time))

        # Clamp to known codes
        if self._mars_timezone not in (self._mars_data.get("timezones") or {}):
            _LOGGER.warning(f"Unknown Mars timezone '{self._mars_timezone}', falling back to MTC")
            self._mars_timezone = "MTC"

        now = datetime.utcnow()
        self._mars_time_info = self._calculate_mars_time(now)

        # State: keep terse (time + code). Rich details go to attributes.
        self._state = f"{self._mars_time_info['local_time']} {self._mars_timezone}"

        _LOGGER.debug(f"Updated Mars Time to {self._state}")
    