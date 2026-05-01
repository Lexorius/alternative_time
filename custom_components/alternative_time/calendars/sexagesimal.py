"""Sexagesimal Cycle (干支/Ganzhi) Calendar implementation - Version 2.5.1."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict

from homeassistant.core import HomeAssistant

from ..sensor import AlternativeTimeSensorBase

_LOGGER = logging.getLogger(__name__)

# ============================================
# CALENDAR METADATA
# ============================================

# Update interval in seconds (60 seconds for cycle updates)
UPDATE_INTERVAL = 60

# Complete calendar information for auto-discovery
CALENDAR_INFO = {
    "id": "sexagesimal",
    "version": "2.5.1",
    "icon": "mdi:yin-yang",
    "category": "cultural",
    "accuracy": "traditional",
    "update_interval": UPDATE_INTERVAL,

    # Multi-language names
    "name": {
        "en": "Sexagesimal Cycle",
        "de": "Sexagesimalzyklus",
        "es": "Ciclo Sexagesimal",
        "fr": "Cycle Sexagésimal",
        "it": "Ciclo Sessagesimale",
        "nl": "Sexagesimale Cyclus",
        "pl": "Cykl Sześćdziesiątkowy",
        "pt": "Ciclo Sexagesimal",
        "ru": "Шестидесятеричный цикл",
        "ja": "干支",
        "zh": "干支纪年",
        "ko": "육십갑자"
    },

    # Translations for compatibility
    "translations": {
        "en": {
            "name": "Sexagesimal Cycle",
            "description": "Traditional East Asian 60-year cycle calendar (Heavenly Stems & Earthly Branches)"
        },
        "de": {
            "name": "Sexagesimalzyklus",
            "description": "Traditioneller ostasiatischer 60-Jahres-Zyklus (Himmelsstämme & Erdzweige)"
        },
        "es": {
            "name": "Ciclo Sexagesimal",
            "description": "Calendario tradicional del este asiático de ciclo de 60 años"
        },
        "fr": {
            "name": "Cycle Sexagésimal",
            "description": "Calendrier traditionnel d'Asie de l'Est à cycle de 60 ans"
        },
        "it": {
            "name": "Ciclo Sessagesimale",
            "description": "Calendario tradizionale dell'Asia orientale con ciclo di 60 anni"
        },
        "nl": {
            "name": "Sexagesimale Cyclus",
            "description": "Traditionele Oost-Aziatische 60-jarige cyclus kalender"
        },
        "pl": {
            "name": "Cykl Sześćdziesiątkowy",
            "description": "Tradycyjny wschodnioazjatycki kalendarz 60-letniego cyklu"
        },
        "pt": {
            "name": "Ciclo Sexagesimal",
            "description": "Calendário tradicional do Leste Asiático com ciclo de 60 anos"
        },
        "ru": {
            "name": "Шестидесятеричный цикл",
            "description": "Традиционный восточноазиатский 60-летний цикл (Небесные стволы и Земные ветви)"
        },
        "ja": {
            "name": "干支",
            "description": "十干十二支による60年周期の伝統的な暦"
        },
        "zh": {
            "name": "干支纪年",
            "description": "天干地支六十年循环传统历法"
        },
        "ko": {
            "name": "육십갑자",
            "description": "천간지지 60년 주기 전통 달력"
        }
    },

    # Short descriptions for UI
    "description": {
        "en": "Traditional East Asian 60-year cycle calendar (Heavenly Stems & Earthly Branches)",
        "de": "Traditioneller ostasiatischer 60-Jahres-Zyklus (Himmelsstämme & Erdzweige)",
        "es": "Calendario tradicional del este asiático de ciclo de 60 años",
        "fr": "Calendrier traditionnel d'Asie de l'Est à cycle de 60 ans",
        "it": "Calendario tradizionale dell'Asia orientale con ciclo di 60 anni",
        "nl": "Traditionele Oost-Aziatische 60-jarige cyclus kalender",
        "pl": "Tradycyjny wschodnioazjatycki kalendarz 60-letniego cyklu",
        "pt": "Calendário tradicional do Leste Asiático com ciclo de 60 anos",
        "ru": "Традиционный восточноазиатский 60-летний цикл",
        "ja": "十干十二支による60年周期の伝統的な暦",
        "zh": "天干地支六十年循环传统历法",
        "ko": "천간지지 60년 주기 전통 달력"
    },

    # Sexagesimal system data
    "sexagesimal_data": {
        # Ten Heavenly Stems (十天干)
        "heavenly_stems": [
            {"cn": "甲", "pinyin": "jiǎ", "element": "Wood", "yin_yang": "Yang", "number": 1},
            {"cn": "乙", "pinyin": "yǐ", "element": "Wood", "yin_yang": "Yin", "number": 2},
            {"cn": "丙", "pinyin": "bǐng", "element": "Fire", "yin_yang": "Yang", "number": 3},
            {"cn": "丁", "pinyin": "dīng", "element": "Fire", "yin_yang": "Yin", "number": 4},
            {"cn": "戊", "pinyin": "wù", "element": "Earth", "yin_yang": "Yang", "number": 5},
            {"cn": "己", "pinyin": "jǐ", "element": "Earth", "yin_yang": "Yin", "number": 6},
            {"cn": "庚", "pinyin": "gēng", "element": "Metal", "yin_yang": "Yang", "number": 7},
            {"cn": "辛", "pinyin": "xīn", "element": "Metal", "yin_yang": "Yin", "number": 8},
            {"cn": "壬", "pinyin": "rén", "element": "Water", "yin_yang": "Yang", "number": 9},
            {"cn": "癸", "pinyin": "guǐ", "element": "Water", "yin_yang": "Yin", "number": 10}
        ],

        # Twelve Earthly Branches (十二地支)
        "earthly_branches": [
            {"cn": "子", "pinyin": "zǐ", "animal": "Rat", "emoji": "🐀", "hour": "23:00-01:00"},
            {"cn": "丑", "pinyin": "chǒu", "animal": "Ox", "emoji": "🐂", "hour": "01:00-03:00"},
            {"cn": "寅", "pinyin": "yín", "animal": "Tiger", "emoji": "🐅", "hour": "03:00-05:00"},
            {"cn": "卯", "pinyin": "mǎo", "animal": "Rabbit", "emoji": "🐇", "hour": "05:00-07:00"},
            {"cn": "辰", "pinyin": "chén", "animal": "Dragon", "emoji": "🐉", "hour": "07:00-09:00"},
            {"cn": "巳", "pinyin": "sì", "animal": "Snake", "emoji": "🐍", "hour": "09:00-11:00"},
            {"cn": "午", "pinyin": "wǔ", "animal": "Horse", "emoji": "🐴", "hour": "11:00-13:00"},
            {"cn": "未", "pinyin": "wèi", "animal": "Goat", "emoji": "🐐", "hour": "13:00-15:00"},
            {"cn": "申", "pinyin": "shēn", "animal": "Monkey", "emoji": "🐒", "hour": "15:00-17:00"},
            {"cn": "酉", "pinyin": "yǒu", "animal": "Rooster", "emoji": "🐓", "hour": "17:00-19:00"},
            {"cn": "戌", "pinyin": "xū", "animal": "Dog", "emoji": "🐕", "hour": "19:00-21:00"},
            {"cn": "亥", "pinyin": "hài", "animal": "Pig", "emoji": "🐖", "hour": "21:00-23:00"}
        ],

        # Reference year for calculations (1984 = 甲子年, start of current cycle)
        "reference_year": 1984
    },

    # Configuration options
    "config_options": {
        "cycle_type": {
            "type": "select",
            "default": "year",
            "options": ["year", "month", "day", "hour", "all"],
            "label": {
                "en": "Cycle Type",
                "de": "Zyklustyp",
                "es": "Tipo de Ciclo",
                "fr": "Type de Cycle",
                "it": "Tipo di Ciclo",
                "nl": "Cyclus Type",
                "pl": "Typ Cyklu",
                "pt": "Tipo de Ciclo",
                "ru": "Тип цикла",
                "ja": "サイクルタイプ",
                "zh": "周期类型",
                "ko": "주기 유형"
            },
            "description": {
                "en": "Show year, month, day, hour cycle, or all",
                "de": "Jahr-, Monats-, Tages-, Stundenzyklus oder alle anzeigen",
                "es": "Mostrar ciclo de año, mes, día, hora o todos",
                "fr": "Afficher le cycle année, mois, jour, heure ou tous",
                "it": "Mostra ciclo anno, mese, giorno, ora o tutti",
                "nl": "Toon jaar, maand, dag, uur cyclus of alle",
                "pl": "Pokaż cykl roku, miesiąca, dnia, godziny lub wszystkie",
                "pt": "Mostrar ciclo de ano, mês, dia, hora ou todos",
                "ru": "Показать цикл года, месяца, дня, часа или все",
                "ja": "年、月、日、時のサイクルまたはすべてを表示",
                "zh": "显示年、月、日、时周期或全部",
                "ko": "년, 월, 일, 시 주기 또는 모두 표시"
            },
            "translations": {
                "en": {"label": "Cycle Type", "description": "Show year, month, day, hour cycle, or all"},
                "de": {"label": "Zyklustyp", "description": "Jahr-, Monats-, Tages-, Stundenzyklus oder alle anzeigen"},
                "zh": {"label": "周期类型", "description": "显示年、月、日、时周期或全部"}
            }
        },
        "display_format": {
            "type": "select",
            "default": "chinese",
            "options": ["chinese", "pinyin", "english", "detailed"],
            "label": {
                "en": "Display Format",
                "de": "Anzeigeformat",
                "es": "Formato de Visualización",
                "fr": "Format d'Affichage",
                "it": "Formato di Visualizzazione",
                "nl": "Weergaveformaat",
                "pl": "Format Wyświetlania",
                "pt": "Formato de Exibição",
                "ru": "Формат отображения",
                "ja": "表示形式",
                "zh": "显示格式",
                "ko": "표시 형식"
            },
            "description": {
                "en": "Chinese characters, Pinyin, English names, or detailed",
                "de": "Chinesische Zeichen, Pinyin, englische Namen oder detailliert",
                "es": "Caracteres chinos, Pinyin, nombres en inglés o detallado",
                "fr": "Caractères chinois, Pinyin, noms anglais ou détaillé",
                "it": "Caratteri cinesi, Pinyin, nomi inglesi o dettagliato",
                "nl": "Chinese tekens, Pinyin, Engelse namen of gedetailleerd",
                "pl": "Chińskie znaki, Pinyin, angielskie nazwy lub szczegółowe",
                "pt": "Caracteres chineses, Pinyin, nomes em inglês ou detalhado",
                "ru": "Китайские иероглифы, Пиньинь, английские названия или подробно",
                "ja": "漢字、ピンイン、英語名、または詳細",
                "zh": "中文、拼音、英文或详细",
                "ko": "한자, 병음, 영어 이름 또는 상세"
            }
        },
        "show_zodiac": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show Zodiac Animal",
                "de": "Tierkreiszeichen anzeigen",
                "es": "Mostrar Animal del Zodiaco",
                "fr": "Afficher l'Animal du Zodiaque",
                "it": "Mostra Animale dello Zodiaco",
                "nl": "Toon Dierenriem Dier",
                "pl": "Pokaż Zwierzę Zodiaku",
                "pt": "Mostrar Animal do Zodíaco",
                "ru": "Показать животное зодиака",
                "ja": "干支の動物を表示",
                "zh": "显示生肖",
                "ko": "띠 동물 표시"
            },
            "description": {
                "en": "Display zodiac animal emoji with the cycle",
                "de": "Tierkreis-Emoji mit dem Zyklus anzeigen",
                "es": "Mostrar emoji del animal del zodiaco con el ciclo",
                "fr": "Afficher l'emoji de l'animal du zodiaque avec le cycle",
                "zh": "显示生肖表情符号"
            }
        }
    }
}


class SexagesimalCycleSensor(AlternativeTimeSensorBase):
    """Sensor for displaying Sexagesimal Cycle (干支/Ganzhi) Calendar."""

    # Class-level update interval
    UPDATE_INTERVAL = UPDATE_INTERVAL

    def __init__(self, base_name: str, hass: HomeAssistant) -> None:
        """Initialize the sexagesimal cycle sensor."""
        super().__init__(base_name, hass)

        # Store CALENDAR_INFO as instance variable
        self._calendar_info = CALENDAR_INFO

        # Get translated name from metadata
        calendar_name = self._translate('name', 'Sexagesimal Cycle')

        # Set sensor attributes
        self._attr_name = f"{base_name} {calendar_name}"
        self._attr_unique_id = f"{base_name}_sexagesimal"
        self._attr_icon = CALENDAR_INFO.get("icon", "mdi:yin-yang")

        # Configuration options with defaults
        config_defaults = CALENDAR_INFO.get("config_options", {})
        self._cycle_type = config_defaults.get("cycle_type", {}).get("default", "year")
        self._display_format = config_defaults.get("display_format", {}).get("default", "chinese")
        self._show_zodiac = config_defaults.get("show_zodiac", {}).get("default", True)

        # Sexagesimal data
        self._sexagesimal_data = CALENDAR_INFO["sexagesimal_data"]

        # Initialize state
        self._state = "甲子"
        self._cycle_info = {}

        # Flag to track if options have been loaded
        self._options_loaded = False

        _LOGGER.debug(f"Initialized Sexagesimal Cycle sensor: {self._attr_name}")
        _LOGGER.debug(f"  Default settings: cycle={self._cycle_type}, format={self._display_format}, zodiac={self._show_zodiac}")

    def _load_options(self) -> None:
        """Load plugin options after IDs are set."""
        if self._options_loaded:
            return

        try:
            options = self.get_plugin_options()
            if options:
                # Update configuration from plugin options
                self._cycle_type = options.get("cycle_type", self._cycle_type)
                self._display_format = options.get("display_format", self._display_format)
                self._show_zodiac = options.get("show_zodiac", self._show_zodiac)

                _LOGGER.debug(f"Sexagesimal sensor loaded options: cycle={self._cycle_type}, format={self._display_format}, zodiac={self._show_zodiac}")
            else:
                _LOGGER.debug("Sexagesimal sensor using default options - no custom options found")

            self._options_loaded = True
        except Exception as e:
            _LOGGER.debug(f"Sexagesimal sensor could not load options yet: {e}")

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

        # Add Sexagesimal-specific attributes
        if self._cycle_info:
            attrs.update(self._cycle_info)

            # Add description in user's language
            attrs["description"] = self._translate('description')

            # Add current configuration
            attrs["cycle_type_setting"] = self._cycle_type
            attrs["display_format_setting"] = self._display_format
            attrs["show_zodiac_setting"] = self._show_zodiac

        return attrs

    def _calculate_cycle(self, date: datetime, cycle_type: str = "year") -> Dict[str, Any]:
        """Calculate the stem-branch cycle for a given date and type."""
        result = {}

        if cycle_type == "year":
            # Calculate year cycle (based on Chinese New Year, approximated here)
            year = date.year
            # The cycle starts from 1984 (甲子年)
            years_since = year - self._sexagesimal_data["reference_year"]

            stem_index = years_since % 10
            branch_index = years_since % 12

            stem = self._sexagesimal_data["heavenly_stems"][stem_index]
            branch = self._sexagesimal_data["earthly_branches"][branch_index]

            result = {
                "stem_cn": stem["cn"],
                "stem_pinyin": stem["pinyin"],
                "stem_element": stem["element"],
                "stem_yinyang": stem["yin_yang"],
                "branch_cn": branch["cn"],
                "branch_pinyin": branch["pinyin"],
                "branch_animal": branch["animal"],
                "branch_emoji": branch["emoji"],
                "cycle_position": (years_since % 60) + 1,
                "cycle_name_cn": f"{stem['cn']}{branch['cn']}",
                "cycle_name_pinyin": f"{stem['pinyin']}{branch['pinyin']}",
                "cycle_name_english": f"{stem['element']}-{branch['animal']}"
            }

        elif cycle_type == "month":
            # Simplified month calculation
            month = date.month
            year = date.year

            # Month calculation is more complex in reality
            # This is a simplified version
            months_since = (year - self._sexagesimal_data["reference_year"]) * 12 + month - 1

            stem_index = months_since % 10
            branch_index = months_since % 12

            stem = self._sexagesimal_data["heavenly_stems"][stem_index]
            branch = self._sexagesimal_data["earthly_branches"][branch_index]

            result = {
                "month_stem_cn": stem["cn"],
                "month_branch_cn": branch["cn"],
                "month_cycle": f"{stem['cn']}{branch['cn']}"
            }

        elif cycle_type == "day":
            # Day calculation
            reference_date = datetime(1984, 1, 1)  # 甲子日
            days_since = (date.date() - reference_date.date()).days

            stem_index = days_since % 10
            branch_index = days_since % 12

            stem = self._sexagesimal_data["heavenly_stems"][stem_index]
            branch = self._sexagesimal_data["earthly_branches"][branch_index]

            result = {
                "day_stem_cn": stem["cn"],
                "day_branch_cn": branch["cn"],
                "day_cycle": f"{stem['cn']}{branch['cn']}"
            }

        elif cycle_type == "hour":
            # Hour calculation
            hour = date.hour
            # Determine which 2-hour period
            hour_branch_index = ((hour + 1) // 2) % 12

            # Hour stem calculation requires the day stem
            reference_date = datetime(1984, 1, 1)
            days_since = (date.date() - reference_date.date()).days
            day_stem_index = days_since % 10

            # Formula: hour_stem = (day_stem * 2 + hour_branch) % 10
            hour_stem_index = (day_stem_index * 2 + hour_branch_index) % 10

            stem = self._sexagesimal_data["heavenly_stems"][hour_stem_index]
            branch = self._sexagesimal_data["earthly_branches"][hour_branch_index]

            result = {
                "hour_stem_cn": stem["cn"],
                "hour_branch_cn": branch["cn"],
                "hour_cycle": f"{stem['cn']}{branch['cn']}",
                "hour_period": branch["hour"]
            }

        return result

    def _format_display(self, cycle_info: Dict[str, Any]) -> str:
        """Format the display based on configuration."""
        if "cycle_name_cn" in cycle_info:
            # Year cycle
            if self._display_format == "chinese":
                display = cycle_info["cycle_name_cn"]
            elif self._display_format == "pinyin":
                display = cycle_info["cycle_name_pinyin"]
            elif self._display_format == "english":
                display = cycle_info["cycle_name_english"]
            else:  # detailed
                display = f"{cycle_info['cycle_name_cn']} ({cycle_info['cycle_name_pinyin']}) {cycle_info['cycle_name_english']}"

            if self._show_zodiac:
                display = f"{cycle_info['branch_emoji']} {display}"

            return f"{display}年"

        # For other cycle types, return simple format
        for key in ["month_cycle", "day_cycle", "hour_cycle"]:
            if key in cycle_info:
                return cycle_info[key]

        return "未知"

    def _calculate_sexagesimal_date(self, earth_date: datetime) -> Dict[str, Any]:
        """Calculate Sexagesimal cycle for given date."""
        result = {}
        display_parts = []

        if self._cycle_type == "all":
            # Calculate all cycles
            year_info = self._calculate_cycle(earth_date, "year")
            month_info = self._calculate_cycle(earth_date, "month")
            day_info = self._calculate_cycle(earth_date, "day")
            hour_info = self._calculate_cycle(earth_date, "hour")

            result.update(year_info)
            result.update(month_info)
            result.update(day_info)
            result.update(hour_info)

            # Create display string for all cycles
            if self._show_zodiac and "branch_emoji" in year_info:
                display_parts.append(f"{year_info['branch_emoji']} {year_info['cycle_name_cn']}年")
            else:
                display_parts.append(f"{year_info['cycle_name_cn']}年")

            display_parts.append(f"{month_info.get('month_cycle', '')}月")
            display_parts.append(f"{day_info.get('day_cycle', '')}日")
            display_parts.append(f"{hour_info.get('hour_cycle', '')}时")

            result["formatted"] = " ".join(display_parts)
        else:
            # Calculate specific cycle
            cycle_info = self._calculate_cycle(earth_date, self._cycle_type)
            result.update(cycle_info)
            result["formatted"] = self._format_display(cycle_info)

        # Add current date/time info
        result["gregorian_date"] = earth_date.strftime("%Y-%m-%d %H:%M:%S")

        return result

    def update(self) -> None:
        """Update the sensor."""
        # Ensure options are loaded
        if not self._options_loaded:
            self._load_options()

        try:
            now = datetime.now()
            self._cycle_info = self._calculate_sexagesimal_date(now)

            # Set state to formatted cycle
            self._state = self._cycle_info.get("formatted", "甲子")

            _LOGGER.debug(f"Updated Sexagesimal Cycle to {self._state}")
        except Exception as e:
            _LOGGER.error(f"Error updating Sexagesimal cycle: {e}", exc_info=True)
            self._state = "错误"

    async def async_update(self) -> None:
        """Update sensor asynchronously."""
        # Run synchronous update in executor
        await self.hass.async_add_executor_job(self.update)
