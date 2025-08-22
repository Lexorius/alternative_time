"""Maya Calendar implementation - Version 2.6."""
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

# Update interval in seconds (3600 seconds = 1 hour, dates change slowly)
UPDATE_INTERVAL = 3600

# Complete calendar information for auto-discovery
CALENDAR_INFO = {
    "id": "maya",
    "version": "2.6.0", 
    "icon": "mdi:pyramid",
    "category": "historical",
    "accuracy": "cultural",
    "update_interval": UPDATE_INTERVAL,
    
    # Multi-language names
    "name": {
        "en": "Maya Calendar",
        "de": "Maya-Kalender",
        "es": "Calendario Maya",
        "fr": "Calendrier Maya",
        "it": "Calendario Maya",
        "nl": "Maya Kalender",
        "pt": "Calendário Maia",
        "ru": "Календарь майя",
        "ja": "マヤ暦",
        "zh": "玛雅历",
        "ko": "마야 달력"
    },
    
    # Short descriptions for UI
    "description": {
        "en": "Long Count, Tzolk'in and Haab calendars (e.g. 13.0.12.1.15 | 8 Ahau | 3 Pop)",
        "de": "Lange Zählung, Tzolk'in und Haab Kalender (z.B. 13.0.12.1.15 | 8 Ahau | 3 Pop)",
        "es": "Cuenta Larga, calendarios Tzolk'in y Haab (ej. 13.0.12.1.15 | 8 Ahau | 3 Pop)",
        "fr": "Compte long, calendriers Tzolk'in et Haab (ex. 13.0.12.1.15 | 8 Ahau | 3 Pop)",
        "it": "Conto lungo, calendari Tzolk'in e Haab (es. 13.0.12.1.15 | 8 Ahau | 3 Pop)",
        "nl": "Lange Telling, Tzolk'in en Haab kalenders (bijv. 13.0.12.1.15 | 8 Ahau | 3 Pop)",
        "pt": "Contagem Longa, calendários Tzolk'in e Haab (ex. 13.0.12.1.15 | 8 Ahau | 3 Pop)",
        "ru": "Длинный счёт, календари Цолькин и Хааб (напр. 13.0.12.1.15 | 8 Ахау | 3 Поп)",
        "ja": "長期暦、ツォルキン暦、ハアブ暦（例：13.0.12.1.15 | 8 アハウ | 3 ポップ）",
        "zh": "长计数、卓尔金历和哈布历（例：13.0.12.1.15 | 8 阿豪 | 3 波普）",
        "ko": "장기력, 촐킨력, 하브력 (예: 13.0.12.1.15 | 8 아하우 | 3 팝)"
    },
    
    # Maya calendar data
    "maya_data": {
        # Tzolk'in (Sacred Calendar) - 260 days
        "tzolkin": {
            "days": 260,
            "numbers": 13,
            "names": [
                "Imix", "Ik", "Akbal", "Kan", "Chicchan",
                "Cimi", "Manik", "Lamat", "Muluc", "Oc",
                "Chuen", "Eb", "Ben", "Ix", "Men",
                "Cib", "Caban", "Etznab", "Cauac", "Ahau"
            ],
            "meanings": {
                "Imix": "Crocodile/Water lily",
                "Ik": "Wind",
                "Akbal": "Night/Darkness",
                "Kan": "Maize/Seed",
                "Chicchan": "Serpent",
                "Cimi": "Death",
                "Manik": "Deer",
                "Lamat": "Venus/Star",
                "Muluc": "Water",
                "Oc": "Dog",
                "Chuen": "Monkey",
                "Eb": "Grass/Road",
                "Ben": "Reed",
                "Ix": "Jaguar",
                "Men": "Eagle",
                "Cib": "Vulture/Owl",
                "Caban": "Earth",
                "Etznab": "Flint/Knife",
                "Cauac": "Storm",
                "Ahau": "Lord/Sun"
            }
        },
        
        # Haab (Civil Calendar) - 365 days
        "haab": {
            "days": 365,
            "months": 18,
            "days_per_month": 20,
            "wayeb": 5,  # Unlucky days at end of year
            "month_names": [
                "Pop", "Wo", "Sip", "Sotz", "Sek",
                "Xul", "Yaxkin", "Mol", "Chen", "Yax",
                "Sac", "Ceh", "Mac", "Kankin", "Muan",
                "Pax", "Kayab", "Cumku", "Wayeb"
            ],
            "month_meanings": {
                "Pop": "Mat",
                "Wo": "Black conjunction",
                "Sip": "Red conjunction",
                "Sotz": "Bat",
                "Sek": "?",
                "Xul": "Dog",
                "Yaxkin": "New sun",
                "Mol": "Water",
                "Chen": "Black storm",
                "Yax": "Green storm",
                "Sac": "White storm",
                "Ceh": "Red storm",
                "Mac": "Enclosed",
                "Kankin": "Yellow sun",
                "Muan": "Owl",
                "Pax": "Planting time",
                "Kayab": "Turtle",
                "Cumku": "Dark god",
                "Wayeb": "Unlucky days"
            }
        },
        
        # Long Count periods
        "long_count": {
            "kin": 1,           # 1 day
            "uinal": 20,        # 20 days
            "tun": 360,         # 360 days (18 uinals)
            "katun": 7200,      # 7,200 days (20 tuns)
            "baktun": 144000    # 144,000 days (20 katuns)
        },
        
        # Correlation constants (days to add to Long Count to get Julian Day)
        "correlation": {
            "GMT": 584283,        # Goodman-Martinez-Thompson (most accepted)
            "Thompson": 584285,   # Thompson's correlation
            "Spinden": 489384     # Spinden's correlation (earlier)
        },
        
        # Calendar Round (52 Haab years = 73 Tzolk'in years)
        "calendar_round": 18980,  # Days in complete cycle
        
        # Glyphs (Unicode approximations)
        "glyphs": {
            "numbers": ["𝋠", "𝋡", "𝋢", "𝋣", "𝋤", "𝋥", "𝋦", "𝋧", "𝋨", "𝋩", "𝋪", "𝋫", "𝋬", "𝋭", "𝋮", "𝋯", "𝋰", "𝋱", "𝋲", "𝋳"],
            "zero": "𝋠"
        }
    },
    
    # Additional metadata
    "reference_url": "https://en.wikipedia.org/wiki/Maya_calendar",
    "documentation_url": "http://www.famsi.org/research/pitts/MayaGlyphsBook.pdf",
    "origin": "Mesoamerica",
    "created_by": "Maya civilization",
    "period": "Pre-Classic to Post-Classic period (2000 BCE - 1500 CE)",
    
    # Example format
    "example": "13.0.12.1.15 | 8 Ahau | 3 Pop",
    "example_meaning": "Long Count | Tzolk'in | Haab",
    
    # Related calendars
    "related": ["aztec", "gregorian"],
    
    # Tags for searching and filtering
    "tags": [
        "historical", "maya", "mesoamerican", "ancient", "sacred",
        "astronomical", "tzolkin", "haab", "long_count", "baktun",
        "cultural", "religious", "agricultural"
    ],
    
    # Special features
    "features": {
        "multiple_cycles": True,
        "sacred_calendar": True,
        "solar_calendar": True,
        "long_count": True,
        "venus_cycle": True,
        "precision": "day"
    },
    
    # Configuration options for this calendar
    "config_options": {
        "show_meanings": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show Meanings",
                "de": "Bedeutungen anzeigen",
                "es": "Mostrar significados",
                "fr": "Afficher les significations",
                "it": "Mostra significati",
                "nl": "Toon betekenissen",
                "pt": "Mostrar significados",
                "ru": "Показать значения",
                "ja": "意味を表示",
                "zh": "显示含义",
                "ko": "의미 표시"
            },
            "description": {
                "en": "Show meanings of day and month names",
                "de": "Zeige Bedeutungen der Tages- und Monatsnamen",
                "es": "Mostrar significados de nombres de días y meses",
                "fr": "Afficher les significations des noms de jours et de mois",
                "it": "Mostra i significati dei nomi di giorni e mesi",
                "nl": "Toon betekenissen van dag- en maandnamen",
                "pt": "Mostrar significados dos nomes de dias e meses",
                "ru": "Показать значения названий дней и месяцев",
                "ja": "日と月の名前の意味を表示",
                "zh": "显示日和月名称的含义",
                "ko": "일과 월 이름의 의미 표시"
            }
        },
        "show_glyphs": {
            "type": "boolean",
            "default": False,
            "label": {
                "en": "Show Glyphs",
                "de": "Glyphen anzeigen",
                "es": "Mostrar glifos",
                "fr": "Afficher les glyphes",
                "it": "Mostra glifi",
                "nl": "Toon glyphs",
                "pt": "Mostrar glifos",
                "ru": "Показать глифы",
                "ja": "グリフを表示",
                "zh": "显示字形",
                "ko": "글리프 표시"
            },
            "description": {
                "en": "Show Unicode approximations of Maya glyphs",
                "de": "Zeige Unicode-Näherungen der Maya-Glyphen",
                "es": "Mostrar aproximaciones Unicode de glifos mayas",
                "fr": "Afficher les approximations Unicode des glyphes mayas",
                "it": "Mostra approssimazioni Unicode dei glifi maya",
                "nl": "Toon Unicode-benaderingen van Maya glyphs",
                "pt": "Mostrar aproximações Unicode de glifos maias",
                "ru": "Показать Unicode-приближения глифов майя",
                "ja": "マヤグリフのUnicode近似を表示",
                "zh": "显示玛雅字形的Unicode近似",
                "ko": "마야 글리프의 유니코드 근사치 표시"
            }
        },
        "correlation_constant": {
            "type": "select",
            "default": "GMT",
            "options": ["GMT", "Thompson", "Spinden"],
            "label": {
                "en": "Correlation Constant",
                "de": "Korrelationskonstante",
                "es": "Constante de correlación",
                "fr": "Constante de corrélation",
                "it": "Costante di correlazione",
                "nl": "Correlatieconstante",
                "pt": "Constante de correlação",
                "ru": "Константа корреляции",
                "ja": "相関定数",
                "zh": "相关常数",
                "ko": "상관 상수"
            },
            "description": {
                "en": "Select correlation constant for date conversion (GMT is most accepted)",
                "de": "Wähle Korrelationskonstante für Datumsumrechnung (GMT ist am weitesten akzeptiert)",
                "es": "Seleccionar constante de correlación para conversión de fecha (GMT es la más aceptada)",
                "fr": "Sélectionner la constante de corrélation pour la conversion de date (GMT est la plus acceptée)",
                "it": "Seleziona la costante di correlazione per la conversione della data (GMT è la più accettata)",
                "nl": "Selecteer correlatieconstante voor datumconversie (GMT is meest geaccepteerd)",
                "pt": "Selecionar constante de correlação para conversão de data (GMT é a mais aceita)",
                "ru": "Выберите константу корреляции для преобразования даты (GMT наиболее принята)",
                "ja": "日付変換の相関定数を選択（GMTが最も受け入れられています）",
                "zh": "选择日期转换的相关常数（GMT最被接受）",
                "ko": "날짜 변환을 위한 상관 상수 선택 (GMT가 가장 널리 받아들여짐)"
            }
        }
    }
}


class MayaCalendarSensor(AlternativeTimeSensorBase):
    """Sensor for displaying Maya Calendar."""
    
    # Class-level update interval
    UPDATE_INTERVAL = UPDATE_INTERVAL
    
    def __init__(self, base_name: str, hass: HomeAssistant) -> None:
        """Initialize the Maya calendar sensor."""
        super().__init__(base_name, hass)
        
        # Get translated name from metadata
        calendar_name = self._translate('name', 'Maya Calendar')
        
        # Set sensor attributes
        self._attr_name = f"{base_name} {calendar_name}"
        self._attr_unique_id = f"{base_name}_maya_calendar"
        self._attr_icon = CALENDAR_INFO.get("icon", "mdi:pyramid")
        
        # Configuration options with defaults from CALENDAR_INFO
        config_defaults = CALENDAR_INFO.get("config_options", {})
        self._show_meanings = config_defaults.get("show_meanings", {}).get("default", True)
        self._show_glyphs = config_defaults.get("show_glyphs", {}).get("default", False)
        self._correlation = config_defaults.get("correlation_constant", {}).get("default", "GMT")
        
        # Maya data
        self._maya_data = CALENDAR_INFO["maya_data"]
        
        # Flag to track if options have been loaded
        self._options_loaded = False
        
        # Initialize state
        self._state = None
        self._maya_date = {}
        
        _LOGGER.debug(f"Initialized Maya Calendar sensor: {self._attr_name}")
    
    def _load_options(self) -> None:
        """Load plugin options after IDs are set."""
        if self._options_loaded:
            return
            
        try:
            options = self.get_plugin_options()
            if options:
                # Update configuration from plugin options
                self._show_meanings = options.get("show_meanings", self._show_meanings)
                self._show_glyphs = options.get("show_glyphs", self._show_glyphs)
                self._correlation = options.get("correlation_constant", self._correlation)
                
                _LOGGER.debug(f"Maya sensor loaded options: show_meanings={self._show_meanings}, "
                            f"show_glyphs={self._show_glyphs}, correlation={self._correlation}")
            else:
                _LOGGER.debug("Maya sensor using default options - no custom options found")
                
            self._options_loaded = True
        except Exception as e:
            _LOGGER.debug(f"Maya sensor could not load options yet: {e}")
    
    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        await super().async_added_to_hass()
        
        # Try to load options now that IDs should be set
        self._load_options()
    
    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes."""
        attrs = super().extra_state_attributes
        
        # Add Maya-specific attributes
        if self._maya_date:
            attrs.update(self._maya_date)
            
            # Add description in user's language
            attrs["description"] = self._translate('description')
            
            # Add reference
            attrs["reference"] = CALENDAR_INFO.get('reference_url', '')
            
            # Add correlation constant used
            attrs["correlation_used"] = self._correlation
        
        return attrs
    
    def _gregorian_to_julian_day(self, date: datetime) -> int:
        """Convert Gregorian date to Julian Day Number."""
        a = (14 - date.month) // 12
        y = date.year + 4800 - a
        m = date.month + 12 * a - 3
        
        jdn = date.day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
        return jdn
    
    def _julian_day_to_long_count(self, jdn: int) -> tuple:
        """Convert Julian Day Number to Maya Long Count."""
        # Get the correlation constant
        correlation = self._maya_data["correlation"][self._correlation]
        
        # Calculate days since Maya epoch
        days_since_epoch = jdn - correlation
        
        # Calculate Long Count components
        baktun = days_since_epoch // self._maya_data["long_count"]["baktun"]
        days_since_epoch %= self._maya_data["long_count"]["baktun"]
        
        katun = days_since_epoch // self._maya_data["long_count"]["katun"]
        days_since_epoch %= self._maya_data["long_count"]["katun"]
        
        tun = days_since_epoch // self._maya_data["long_count"]["tun"]
        days_since_epoch %= self._maya_data["long_count"]["tun"]
        
        uinal = days_since_epoch // self._maya_data["long_count"]["uinal"]
        days_since_epoch %= self._maya_data["long_count"]["uinal"]
        
        kin = days_since_epoch
        
        return (baktun, katun, tun, uinal, kin)
    
    def _calculate_tzolkin(self, jdn: int) -> tuple:
        """Calculate Tzolk'in date."""
        correlation = self._maya_data["correlation"][self._correlation]
        days_since_epoch = jdn - correlation
        
        # Tzolk'in has a 260-day cycle
        tzolkin_day = days_since_epoch % 260
        
        # Calculate number (1-13) and name (20 day names)
        # The base date 0.0.0.0.0 corresponds to 4 Ahau
        number = ((tzolkin_day + 4 - 1) % 13) + 1
        name_index = (tzolkin_day + 19) % 20  # Ahau is at index 19
        
        day_name = self._maya_data["tzolkin"]["names"][name_index]
        
        return (number, day_name)
    
    def _calculate_haab(self, jdn: int) -> tuple:
        """Calculate Haab date."""
        correlation = self._maya_data["correlation"][self._correlation]
        days_since_epoch = jdn - correlation
        
        # Haab has a 365-day cycle
        haab_day = days_since_epoch % 365
        
        # The base date 0.0.0.0.0 corresponds to 8 Cumku (day 348)
        haab_day = (haab_day + 348) % 365
        
        # Calculate month and day
        if haab_day < 360:  # Regular months (18 x 20 days)
            month_index = haab_day // 20
            day = haab_day % 20
        else:  # Wayeb (5 unlucky days)
            month_index = 18
            day = haab_day - 360
        
        month_name = self._maya_data["haab"]["month_names"][month_index]
        
        return (day, month_name)
    
    def _format_with_glyphs(self, number: int) -> str:
        """Format number with Maya glyphs if available."""
        if not self._show_glyphs:
            return str(number)
        
        glyphs = self._maya_data["glyphs"]["numbers"]
        if 0 <= number < len(glyphs):
            return glyphs[number]
        return str(number)
    
    def _calculate_maya_date(self, earth_date: datetime) -> Dict[str, Any]:
        """Calculate Maya calendar date from Gregorian date."""
        
        # Convert to Julian Day Number
        jdn = self._gregorian_to_julian_day(earth_date)
        
        # Calculate Long Count
        long_count = self._julian_day_to_long_count(jdn)
        long_count_str = ".".join(str(x) for x in long_count)
        
        # Calculate Tzolk'in
        tzolkin_number, tzolkin_name = self._calculate_tzolkin(jdn)
        tzolkin_str = f"{tzolkin_number} {tzolkin_name}"
        
        # Calculate Haab
        haab_day, haab_month = self._calculate_haab(jdn)
        haab_str = f"{haab_day} {haab_month}"
        
        # Format complete date
        formatted = f"{long_count_str} | {tzolkin_str} | {haab_str}"
        
        result = {
            "long_count": long_count_str,
            "baktun": long_count[0],
            "katun": long_count[1],
            "tun": long_count[2],
            "uinal": long_count[3],
            "kin": long_count[4],
            "tzolkin": tzolkin_str,
            "tzolkin_number": tzolkin_number,
            "tzolkin_day": tzolkin_name,
            "haab": haab_str,
            "haab_day": haab_day,
            "haab_month": haab_month,
            "formatted": formatted,
            "julian_day": jdn
        }
        
        # Add meanings if configured
        if self._show_meanings:
            tzolkin_meaning = self._maya_data["tzolkin"]["meanings"].get(tzolkin_name, "")
            haab_meaning = self._maya_data["haab"]["month_meanings"].get(haab_month, "")
            
            if tzolkin_meaning:
                result["tzolkin_meaning"] = tzolkin_meaning
            if haab_meaning:
                result["haab_meaning"] = haab_meaning
        
        # Add glyph representations if configured
        if self._show_glyphs:
            result["long_count_glyphs"] = ".".join(
                self._format_with_glyphs(x) for x in long_count
            )
            result["tzolkin_glyphs"] = f"{self._format_with_glyphs(tzolkin_number)} {tzolkin_name}"
        
        # Calculate Calendar Round position (52 Haab years = 73 Tzolk'in years)
        tzolkin_position = (tzolkin_number - 1) * 20 + self._maya_data["tzolkin"]["names"].index(tzolkin_name)
        haab_position = haab_day + (self._maya_data["haab"]["month_names"].index(haab_month) * 20)
        
        # The Calendar Round repeats every 18,980 days (52 × 365 = 73 × 260)
        calendar_round_day = (jdn - self._maya_data["correlation"][self._correlation]) % self._maya_data["calendar_round"]
        result["calendar_round_position"] = f"Day {calendar_round_day} of 18,980"
        
        # Add current K'atun period info (relevant for prophecies)
        current_katun = long_count[1]
        katun_lord = self._maya_data["tzolkin"]["names"][(current_katun * 2) % 20]
        result["katun_lord"] = f"K'atun {current_katun} {katun_lord}"
        
        # Add Venus cycle (important in Maya astronomy)
        # Venus cycle is 584 days, synchronized with Calendar Round
        venus_day = (jdn - self._maya_data["correlation"][self._correlation]) % 584
        venus_phase = ""
        if venus_day < 8:
            venus_phase = "First appearance as Morning Star"
        elif venus_day < 263:
            venus_phase = "Morning Star"
        elif venus_day < 263 + 50:
            venus_phase = "Superior conjunction (invisible)"
        elif venus_day < 263 + 50 + 8:
            venus_phase = "First appearance as Evening Star"
        else:
            venus_phase = "Evening Star"
        
        result["venus_phase"] = venus_phase
        
        return result
    
    def update(self) -> None:
        """Update the sensor."""
        # Ensure options are loaded (in case async_added_to_hass hasn't run yet)
        if not self._options_loaded:
            self._load_options()
        
        now = datetime.now()
        self._maya_date = self._calculate_maya_date(now)
        
        # Set state to formatted Maya date
        self._state = self._maya_date["formatted"]
        
        _LOGGER.debug(f"Updated Maya Calendar to {self._state}")