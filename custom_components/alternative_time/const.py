"""Constants for Alternative Time integration."""
DOMAIN = "alternative_time"

# Configuration constants
CONF_NAME = "name"
CONF_TIMEZONE = "timezone"
CONF_ENABLE_TIMEZONE = "enable_timezone"
CONF_ENABLE_STARDATE = "enable_stardate"
CONF_ENABLE_SWATCH = "enable_swatch"
CONF_ENABLE_UNIX = "enable_unix"
CONF_ENABLE_JULIAN = "enable_julian"
CONF_ENABLE_DECIMAL = "enable_decimal"
CONF_ENABLE_HEXADECIMAL = "enable_hexadecimal"
CONF_ENABLE_MAYA = "enable_maya"
CONF_ENABLE_NATO = "enable_nato"
CONF_ENABLE_NATO_ZONE = "enable_nato_zone"
CONF_ENABLE_NATO_RESCUE = "enable_nato_rescue"
CONF_ENABLE_ATTIC = "enable_attic"
CONF_ENABLE_SURIYAKATI = "enable_suriyakati"
CONF_ENABLE_MINGUO = "enable_minguo"
CONF_ENABLE_DARIAN = "enable_darian"
CONF_ENABLE_MARS_TIME = "enable_mars_time"
CONF_MARS_TIMEZONE = "mars_timezone"
CONF_ENABLE_EVE = "enable_eve"
CONF_ENABLE_SHIRE = "enable_shire"
CONF_ENABLE_RIVENDELL = "enable_rivendell"
CONF_ENABLE_TAMRIEL = "enable_tamriel"
CONF_ENABLE_EGYPTIAN = "enable_egyptian"
CONF_ENABLE_DISCWORLD = "enable_discworld"
CONF_ENABLE_ROMAN = "enable_roman"

DEFAULT_NAME = "Alternative Time"

# Sensor types for display
SENSOR_TYPES = {
    "timezone": "Timezone",
    "stardate": "Stardate",
    "swatch": "Swatch Internet Time",
    "unix": "Unix Timestamp",
    "julian": "Julian Date",
    "decimal": "Decimal Time",
    "hexadecimal": "Hexadecimal Time",
    "maya": "Maya Calendar",
    "nato": "NATO DTG",
    "nato_zone": "NATO Zone Time",
    "nato_rescue": "NATO Rescue Time",
    "attic": "Attic Calendar",
    "suriyakati": "Suriyakati Calendar",
    "minguo": "Minguo Calendar",
    "darian": "Darian Mars Calendar",
    "mars_time": "Mars Time",
    "eve": "EVE Online Time",
    "shire": "Shire Calendar",
    "rivendell": "Rivendell Calendar",
    "tamriel": "Tamriel Calendar",
    "egyptian": "Egyptian Calendar",
    "discworld": "Discworld Calendar",
    "roman": "Roman Calendar"
}

# Mars timezone options
MARS_TIMEZONES = [
    "MTC",  # Coordinated Mars Time
    "AMT",  # Airy Mean Time
    "OLY",  # Olympus Mons Time
    "ELY",  # Elysium Time
    "CHA",  # Chryse Time
    "MAR",  # Mariner Valley Time
    "ARA",  # Arabia Terra Time
    "THR",  # Tharsis Time
    "HEL",  # Hellas Basin Time
    "VIK",  # Viking 1 Landing Site
    "PTH",  # Pathfinder Landing Site
    "OPP",  # Opportunity Landing Site
    "SPI",  # Spirit Landing Site
    "CUR",  # Curiosity/Gale Crater
    "PER",  # Perseverance/Jezero
]