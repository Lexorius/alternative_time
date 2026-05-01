"""Tamriel Calendar (Elder Scrolls) implementation - Version 3.0."""
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

# Update interval in seconds (3600 seconds = 1 hour)
UPDATE_INTERVAL = 3600

# Complete calendar information for auto-discovery
CALENDAR_INFO = {
    "id": "tamriel",
    "version": "3.0.0",
    "icon": "mdi:sword-cross",
    "category": "fantasy",
    "accuracy": "fictional",
    "update_interval": UPDATE_INTERVAL,

    # Multi-language names
    "name": {
        "en": "Tamriel Calendar (Elder Scrolls)",
        "de": "Tamriel-Kalender (Elder Scrolls)",
        "es": "Calendario de Tamriel (Elder Scrolls)",
        "fr": "Calendrier de Tamriel (Elder Scrolls)",
        "it": "Calendario di Tamriel (Elder Scrolls)",
        "nl": "Tamriel Kalender (Elder Scrolls)",
        "pl": "Kalendarz Tamriel (Elder Scrolls)",
        "pt": "Calendário de Tamriel (Elder Scrolls)",
        "ru": "Календарь Тамриэля (Elder Scrolls)",
        "ja": "タムリエル暦 (エルダースクロール)",
        "zh": "泰姆瑞尔历 (上古卷轴)",
        "ko": "탐리엘 달력 (엘더스크롤)"
    },

    # Short descriptions for UI
    "description": {
        "en": "Elder Scrolls calendar with two moons, birthsigns, and Daedric summoning days",
        "de": "Elder Scrolls Kalender mit zwei Monden, Geburtszeichen und Daedrischen Beschwörungstagen",
        "es": "Calendario de Elder Scrolls con dos lunas, signos de nacimiento y días de invocación daédrica",
        "fr": "Calendrier Elder Scrolls avec deux lunes, signes de naissance et jours d'invocation daedrique",
        "it": "Calendario di Elder Scrolls con due lune, segni zodiacali e giorni di evocazione daedrica",
        "nl": "Elder Scrolls kalender met twee manen, geboortetekens en Daedrische oproepingsdagen",
        "pl": "Kalendarz Elder Scrolls z dwoma księżycami, znakami urodzenia i dniami przyzywania daedr",
        "pt": "Calendário Elder Scrolls com duas luas, signos de nascimento e dias de invocação daédrica",
        "ru": "Календарь Elder Scrolls с двумя лунами, знаками рождения и днями призыва даэдра",
        "ja": "2つの月、誕生星座、デイドラ召喚日を含むエルダースクロールズの暦",
        "zh": "上古卷轴日历，包含双月、诞生星座和魔神召唤日",
        "ko": "두 개의 달, 탄생 별자리, 데이드라 소환일이 있는 엘더스크롤 달력"
    },

    # Detailed information for documentation
    "detailed_info": {
        "en": {
            "overview": "The Tamrielic calendar is used throughout the continent of Tamriel in The Elder Scrolls universe",
            "structure": "12 months with varying days (28-31), 7-day weeks from Morndas to Sundas",
            "eras": "Currently in the Fourth Era (4E) following the Oblivion Crisis",
            "moons": "Two moons: Masser (24-day cycle) and Secunda (32-day cycle), important for Khajiit births",
            "birthsigns": "13 constellations determine character traits: The Warrior, The Mage, The Thief, and their charges",
            "daedric": "Specific days are sacred to the 16 Daedric Princes for summoning rituals",
            "holidays": "Numerous festivals throughout the year, from New Life Festival to Saturalia",
            "note": "Based on Skyrim's timeline where 4E 201 = Earth year 2011"
        },
        "de": {
            "overview": "Der tamrielische Kalender wird auf dem gesamten Kontinent Tamriel im Elder Scrolls Universum verwendet",
            "structure": "12 Monate mit unterschiedlichen Tagen (28-31), 7-Tage-Wochen von Morndas bis Sundas",
            "eras": "Aktuell in der Vierten Ära (4Ä) nach der Oblivion-Krise",
            "moons": "Zwei Monde: Masser (24-Tage-Zyklus) und Secunda (32-Tage-Zyklus), wichtig für Khajiit-Geburten",
            "birthsigns": "13 Sternbilder bestimmen Charaktereigenschaften: Der Krieger, Der Magier, Der Dieb und ihre Schützlinge",
            "daedric": "Bestimmte Tage sind den 16 Daedrischen Prinzen für Beschwörungsrituale heilig",
            "holidays": "Zahlreiche Feste im Jahr, vom Neujahrsfest bis Saturalia",
            "note": "Basierend auf Skyrims Zeitlinie, wo 4Ä 201 = Erdjahr 2011"
        }
    },

    # Configuration options
    "config_options": {
        "show_moons": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show Moon Phases",
                "de": "Mondphasen anzeigen",
                "es": "Mostrar fases lunares",
                "fr": "Afficher les phases lunaires",
                "it": "Mostra fasi lunari",
                "nl": "Toon maanfasen",
                "pl": "Pokaż fazy księżyca",
                "pt": "Mostrar fases da lua",
                "ru": "Показать фазы лун",
                "ja": "月相を表示",
                "zh": "显示月相",
                "ko": "달의 위상 표시"
            },
            "description": {
                "en": "Show Masser and Secunda moon phases (affects Khajiit forms)",
                "de": "Zeige Masser und Secunda Mondphasen (beeinflusst Khajiit-Formen)",
                "es": "Mostrar fases de Masser y Secunda (afecta formas Khajiit)",
                "fr": "Afficher les phases de Masser et Secunda (affecte les formes Khajiit)",
                "it": "Mostra le fasi di Masser e Secunda (influenza le forme Khajiit)",
                "nl": "Toon Masser en Secunda maanfasen (beïnvloedt Khajiit vormen)",
                "pl": "Pokaż fazy Masser i Secunda (wpływa na formy Khajiit)",
                "pt": "Mostrar fases de Masser e Secunda (afeta formas Khajiit)",
                "ru": "Показать фазы Массера и Секунды (влияет на формы каджитов)",
                "ja": "マッサーとセクンダの月相を表示（カジートの形態に影響）",
                "zh": "显示马瑟和塞康达月相（影响虎人形态）",
                "ko": "마서와 세쿤다 달의 위상 표시 (카짓 형태에 영향)"
            }
        },
        "show_holidays": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show Holidays",
                "de": "Feiertage anzeigen",
                "es": "Mostrar festividades",
                "fr": "Afficher les fêtes",
                "it": "Mostra festività",
                "nl": "Toon feestdagen",
                "pl": "Pokaż święta",
                "pt": "Mostrar feriados",
                "ru": "Показать праздники",
                "ja": "祝日を表示",
                "zh": "显示节日",
                "ko": "휴일 표시"
            },
            "description": {
                "en": "Display Tamrielic holidays and festivals",
                "de": "Tamrielische Feiertage und Feste anzeigen",
                "es": "Mostrar festividades y festivales tamriélicos",
                "fr": "Afficher les fêtes et festivals tamriéliques",
                "it": "Mostra festività e festival tamrielici",
                "nl": "Toon Tamrielische feestdagen en festivals",
                "pl": "Pokaż tamrielskie święta i festiwale",
                "pt": "Mostrar feriados e festivais tamriélicos",
                "ru": "Показать тамриэльские праздники и фестивали",
                "ja": "タムリエルの祝日と祭りを表示",
                "zh": "显示泰姆瑞尔节日和庆典",
                "ko": "탐리엘 휴일과 축제 표시"
            }
        },
        "show_daedric": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show Daedric Days",
                "de": "Daedrische Tage anzeigen",
                "es": "Mostrar días daédricos",
                "fr": "Afficher les jours daedriques",
                "it": "Mostra giorni daedrici",
                "nl": "Toon Daedrische dagen",
                "pl": "Pokaż dni daedr",
                "pt": "Mostrar dias daédricos",
                "ru": "Показать даэдрические дни",
                "ja": "デイドラの日を表示",
                "zh": "显示魔神日",
                "ko": "데이드라의 날 표시"
            },
            "description": {
                "en": "Display Daedric Prince summoning days",
                "de": "Daedrische Prinzen-Beschwörungstage anzeigen",
                "es": "Mostrar días de invocación de Príncipes Daédricos",
                "fr": "Afficher les jours d'invocation des Princes Daedriques",
                "it": "Mostra i giorni di evocazione dei Principi Daedrici",
                "nl": "Toon Daedrische Prinsen oproepingsdagen",
                "pl": "Pokaż dni przyzywania Książąt Daedr",
                "pt": "Mostrar dias de invocação dos Príncipes Daédricos",
                "ru": "Показать дни призыва Даэдрических Принцев",
                "ja": "デイドラの王子召喚日を表示",
                "zh": "显示魔神王子召唤日",
                "ko": "데이드라 군주 소환일 표시"
            }
        },
        "show_birthsign": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show Birthsign",
                "de": "Geburtszeichen anzeigen",
                "es": "Mostrar signo de nacimiento",
                "fr": "Afficher le signe de naissance",
                "it": "Mostra segno di nascita",
                "nl": "Toon geboorteteken",
                "pl": "Pokaż znak urodzenia",
                "pt": "Mostrar signo de nascimento",
                "ru": "Показать знак рождения",
                "ja": "誕生星座を表示",
                "zh": "显示诞生星座",
                "ko": "탄생 별자리 표시"
            },
            "description": {
                "en": "Display the current birthsign constellation",
                "de": "Aktuelles Geburtszeichen-Sternbild anzeigen",
                "es": "Mostrar la constelación del signo de nacimiento actual",
                "fr": "Afficher la constellation du signe de naissance actuel",
                "it": "Mostra la costellazione del segno di nascita attuale",
                "nl": "Toon het huidige geboorteteken sterrenbeeld",
                "pl": "Pokaż aktualną konstelację znaku urodzenia",
                "pt": "Mostrar a constelação do signo de nascimento atual",
                "ru": "Показать текущее созвездие знака рождения",
                "ja": "現在の誕生星座を表示",
                "zh": "显示当前诞生星座",
                "ko": "현재 탄생 별자리 표시"
            }
        },
        "era": {
            "type": "select",
            "default": "4E",
            "options": ["1E", "2E", "3E", "4E", "5E"],
            "label": {
                "en": "Era",
                "de": "Ära",
                "es": "Era",
                "fr": "Ère",
                "it": "Era",
                "nl": "Tijdperk",
                "pl": "Era",
                "pt": "Era",
                "ru": "Эра",
                "ja": "紀元",
                "zh": "纪元",
                "ko": "시대"
            },
            "description": {
                "en": "Select the Tamrielic Era to display",
                "de": "Wähle die anzuzeigende Tamrielische Ära",
                "es": "Selecciona la Era Tamriélica a mostrar",
                "fr": "Sélectionnez l'Ère Tamriélique à afficher",
                "it": "Seleziona l'Era Tamrielica da visualizzare",
                "nl": "Selecteer het Tamrielische Tijdperk om weer te geven",
                "pl": "Wybierz Erę Tamriel do wyświetlenia",
                "pt": "Selecione a Era Tamriélica para exibir",
                "ru": "Выберите Тамриэльскую Эру для отображения",
                "ja": "表示するタムリエル紀元を選択",
                "zh": "选择要显示的泰姆瑞尔纪元",
                "ko": "표시할 탐리엘 시대 선택"
            },
            "options_label": {
                "1E": {
                    "en": "First Era (Dawn Era)",
                    "de": "Erste Ära (Ära der Dämmerung)",
                    "es": "Primera Era (Era del Amanecer)",
                    "fr": "Première Ère (Ère de l'Aube)",
                    "it": "Prima Era (Era dell'Alba)",
                    "nl": "Eerste Tijdperk (Dageraad Tijdperk)",
                    "pl": "Pierwsza Era (Era Świtu)",
                    "pt": "Primeira Era (Era do Amanhecer)",
                    "ru": "Первая Эра (Эра Рассвета)",
                    "ja": "第一紀（黎明の時代）",
                    "zh": "第一纪元（黎明纪元）",
                    "ko": "제1시대 (여명의 시대)"
                },
                "2E": {
                    "en": "Second Era (Interregnum)",
                    "de": "Zweite Ära (Interregnum)",
                    "es": "Segunda Era (Interregno)",
                    "fr": "Deuxième Ère (Interrègne)",
                    "it": "Seconda Era (Interregno)",
                    "nl": "Tweede Tijdperk (Interregnum)",
                    "pl": "Druga Era (Bezkrólewie)",
                    "pt": "Segunda Era (Interregno)",
                    "ru": "Вторая Эра (Междуцарствие)",
                    "ja": "第二紀（空位時代）",
                    "zh": "第二纪元（空位期）",
                    "ko": "제2시대 (공위기)"
                },
                "3E": {
                    "en": "Third Era (Septim Dynasty)",
                    "de": "Dritte Ära (Septim-Dynastie)",
                    "es": "Tercera Era (Dinastía Septim)",
                    "fr": "Troisième Ère (Dynastie Septim)",
                    "it": "Terza Era (Dinastia Septim)",
                    "nl": "Derde Tijdperk (Septim Dynastie)",
                    "pl": "Trzecia Era (Dynastia Septim)",
                    "pt": "Terceira Era (Dinastia Septim)",
                    "ru": "Третья Эра (Династия Септимов)",
                    "ja": "第三紀（セプティム朝）",
                    "zh": "第三纪元（赛普汀王朝）",
                    "ko": "제3시대 (셉팀 왕조)"
                },
                "4E": {
                    "en": "Fourth Era (Current - Skyrim)",
                    "de": "Vierte Ära (Aktuell - Skyrim)",
                    "es": "Cuarta Era (Actual - Skyrim)",
                    "fr": "Quatrième Ère (Actuelle - Skyrim)",
                    "it": "Quarta Era (Attuale - Skyrim)",
                    "nl": "Vierde Tijdperk (Huidig - Skyrim)",
                    "pl": "Czwarta Era (Obecna - Skyrim)",
                    "pt": "Quarta Era (Atual - Skyrim)",
                    "ru": "Четвертая Эра (Текущая - Скайрим)",
                    "ja": "第四紀（現在 - スカイリム）",
                    "zh": "第四纪元（当前 - 天际）",
                    "ko": "제4시대 (현재 - 스카이림)"
                },
                "5E": {
                    "en": "Fifth Era (Future)",
                    "de": "Fünfte Ära (Zukunft)",
                    "es": "Quinta Era (Futuro)",
                    "fr": "Cinquième Ère (Futur)",
                    "it": "Quinta Era (Futuro)",
                    "nl": "Vijfde Tijdperk (Toekomst)",
                    "pl": "Piąta Era (Przyszłość)",
                    "pt": "Quinta Era (Futuro)",
                    "ru": "Пятая Эра (Будущее)",
                    "ja": "第五紀（未来）",
                    "zh": "第五纪元（未来）",
                    "ko": "제5시대 (미래)"
                }
            }
        }
    },

    # Tamriel-specific data
    "tamriel_data": {
        "months": [
            {"name": "Morning Star", "days": 31, "earth": "January"},
            {"name": "Sun's Dawn", "days": 28, "earth": "February"},
            {"name": "First Seed", "days": 31, "earth": "March"},
            {"name": "Rain's Hand", "days": 30, "earth": "April"},
            {"name": "Second Seed", "days": 31, "earth": "May"},
            {"name": "Mid Year", "days": 30, "earth": "June"},
            {"name": "Sun's Height", "days": 31, "earth": "July"},
            {"name": "Last Seed", "days": 31, "earth": "August"},
            {"name": "Hearthfire", "days": 30, "earth": "September"},
            {"name": "Frostfall", "days": 31, "earth": "October"},
            {"name": "Sun's Dusk", "days": 30, "earth": "November"},
            {"name": "Evening Star", "days": 31, "earth": "December"}
        ],
        "weekdays": [
            "Morndas", "Tirdas", "Middas", "Turdas",
            "Fredas", "Loredas", "Sundas"
        ],
        "birthsigns": [
            {"name": "The Ritual", "month": 1},
            {"name": "The Lover", "month": 2},
            {"name": "The Lord", "month": 3},
            {"name": "The Mage", "month": 4},
            {"name": "The Shadow", "month": 5},
            {"name": "The Steed", "month": 6},
            {"name": "The Apprentice", "month": 7},
            {"name": "The Warrior", "month": 8},
            {"name": "The Lady", "month": 9},
            {"name": "The Tower", "month": 10},
            {"name": "The Atronach", "month": 11},
            {"name": "The Thief", "month": 12}
        ],
        "divines": [
            "Akatosh", "Arkay", "Dibella", "Julianos",
            "Kynareth", "Mara", "Stendarr", "Talos", "Zenithar"
        ],
        "guild_days": {
            "Morndas": "Mages Guild studies",
            "Tirdas": "Fighters Guild training",
            "Middas": "Merchants' market day",
            "Turdas": "Thieves Guild planning",
            "Fredas": "Temple prayers",
            "Loredas": "Dark Brotherhood contracts",
            "Sundas": "Day of rest and worship"
        },
        "era_info": {
            "1E": {"name": "First Era", "start": -2920, "end": 1},
            "2E": {"name": "Second Era", "start": 1, "end": 896},
            "3E": {"name": "Third Era", "start": 1, "end": 433},
            "4E": {"name": "Fourth Era", "start": 1, "end": None},
            "5E": {"name": "Fifth Era", "start": 1, "end": None}
        }
    },

    # Additional metadata
    "reference_url": "https://en.uesp.net/wiki/Lore:Calendar",
    "documentation_url": "https://elderscrolls.fandom.com/wiki/Calendar",
    "origin": "The Elder Scrolls series by Bethesda Game Studios",
    "created_by": "Bethesda Game Studios",
    "introduced": "The Elder Scrolls: Arena (1994)",

    # Example format
    "example": "4E 201, Last Seed 17 (Tirdas)",
    "example_meaning": "Fourth Era year 201, 17th day of Last Seed, Tirdas (Tuesday)",

    # Related calendars
    "related": ["shire", "rivendell", "warcraft"],

    # Tags for searching and filtering
    "tags": [
        "fantasy", "elder_scrolls", "skyrim", "tamriel", "gaming",
        "rpg", "bethesda", "tes", "oblivion", "morrowind", "eso",
        "fourth_era", "daedric", "aedric", "khajiit", "argonian"
    ],

    # Special features
    "features": {
        "supports_eras": True,
        "supports_moons": True,
        "supports_birthsigns": True,
        "supports_holidays": True,
        "supports_divine_blessings": True,
        "supports_daedric_days": True,
        "precision": "day"
    }
}


class TamrielCalendarSensor(AlternativeTimeSensorBase):
    """Sensor for displaying Tamrielic Calendar from Elder Scrolls."""

    # Class-level update interval
    UPDATE_INTERVAL = UPDATE_INTERVAL

    def __init__(self, base_name: str, hass: HomeAssistant) -> None:
        """Initialize the Tamriel calendar sensor."""
        super().__init__(base_name, hass)

        # Get translated name from metadata
        calendar_name = self._translate('name', 'Tamriel Calendar')

        # Set sensor attributes
        self._attr_name = f"{base_name} {calendar_name}"
        self._attr_unique_id = f"{base_name}_tamriel_calendar"
        self._attr_icon = CALENDAR_INFO.get("icon", "mdi:sword-cross")

        # Configuration options with defaults
        config_defaults = CALENDAR_INFO.get("config_options", {})
        self._show_moons = config_defaults.get("show_moons", {}).get("default", True)
        self._show_holidays = config_defaults.get("show_holidays", {}).get("default", True)
        self._show_daedric = config_defaults.get("show_daedric", {}).get("default", True)
        self._show_birthsign = config_defaults.get("show_birthsign", {}).get("default", True)
        self._era = config_defaults.get("era", {}).get("default", "4E")

        # Tamriel data
        self._tamriel_data = CALENDAR_INFO["tamriel_data"]

        # Initialize state
        self._state = None
        self._tamriel_date = {}

        _LOGGER.debug(f"Initialized Tamriel Calendar sensor: {self._attr_name}")

    def set_options(self, options: Dict[str, Any]) -> None:
        """Set options from config flow."""
        if options:
            self._show_moons = options.get("show_moons", self._show_moons)
            self._show_holidays = options.get("show_holidays", self._show_holidays)
            self._show_daedric = options.get("show_daedric", self._show_daedric)
            self._show_birthsign = options.get("show_birthsign", self._show_birthsign)
            self._era = options.get("era", self._era)

            _LOGGER.debug(f"Tamriel sensor options updated: show_moons={self._show_moons}, "
                         f"show_holidays={self._show_holidays}, show_daedric={self._show_daedric}, "
                         f"show_birthsign={self._show_birthsign}, era={self._era}")

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes."""
        attrs = super().extra_state_attributes

        # Add Tamriel-specific attributes
        if self._tamriel_date:
            attrs.update(self._tamriel_date)

            # Add description in user's language
            attrs["description"] = self._translate('description')

            # Add reference
            attrs["reference"] = CALENDAR_INFO.get('reference_url', '')

            # Add configuration status
            attrs["config"] = {
                "show_moons": self._show_moons,
                "show_holidays": self._show_holidays,
                "show_daedric": self._show_daedric,
                "show_birthsign": self._show_birthsign,
                "era": self._era
            }

        return attrs

    def _get_tamriel_holiday(self, month: int, day: int) -> str:
        """Get Tamrielic holiday for given date."""
        holidays = {
            (1, 1): "🎊 New Life Festival",
            (1, 15): "🏔️ South Wind's Prayer",
            (1, 16): "📚 Day of Lights",
            (2, 5): "⚔️ Othroktide",
            (2, 16): "💕 Heart's Day",
            (3, 7): "🌱 First Planting",
            (3, 21): "🏛️ Hogithum",
            (4, 1): "🤡 Jester's Day",
            (4, 28): "🌸 Day of Shame",
            (5, 7): "🌾 Second Planting",
            (5, 30): "🔥 Fire Festival",
            (6, 16): "🪐 Mid Year Celebration",
            (6, 24): "⚡ Tibedetha",
            (7, 10): "🏛️ Merchants' Festival",
            (7, 12): "🗡️ Divad Etep't",
            (8, 21): "🍃 Harvest's End",
            (9, 8): "⚒️ Tales and Tallows",
            (10, 13): "👻 Witches' Festival",
            (10, 30): "🦴 Old Life Festival",
            (11, 18): "🛡️ Warriors' Festival",
            (11, 20): "🌺 Moon Festival",
            (12, 15): "🌟 North Wind's Prayer",
            (12, 31): "🎭 Saturalia"
        }
        return holidays.get((month, day), "")

    def _get_daedric_summoning_day(self, month: int, day: int) -> str:
        """Get Daedric Prince summoning day."""
        daedric_days = {
            (1, 1): "🌙 Sheogorath",
            (1, 13): "⚔️ Mehrunes Dagon",
            (2, 13): "🍷 Sanguine",
            (3, 5): "📖 Hermaeus Mora",
            (3, 21): "🌑 Namira",
            (4, 9): "🦌 Hircine",
            (5, 9): "💎 Clavicus Vile",
            (6, 5): "🕸️ Peryite",
            (7, 10): "☠️ Vaermina",
            (8, 8): "🔮 Azura",
            (9, 19): "⚖️ Meridia",
            (10, 13): "🔥 Boethiah",
            (11, 8): "🗿 Malacath",
            (11, 20): "🕷️ Mephala",
            (12, 20): "🌑 Nocturnal",
            (12, 31): "⚔️ Molag Bal"
        }
        return daedric_days.get((month, day), "")

    def _get_moon_phase(self, day_in_cycle: int, cycle_length: int, moon_name: str) -> str:
        """Calculate moon phase with emoji."""
        phase_portion = day_in_cycle / cycle_length

        if phase_portion < 0.125:
            return f"🌑 {moon_name}: New"
        elif phase_portion < 0.25:
            return f"🌒 {moon_name}: Waxing Crescent"
        elif phase_portion < 0.375:
            return f"🌓 {moon_name}: First Quarter"
        elif phase_portion < 0.5:
            return f"🌔 {moon_name}: Waxing Gibbous"
        elif phase_portion < 0.625:
            return f"🌕 {moon_name}: Full"
        elif phase_portion < 0.75:
            return f"🌖 {moon_name}: Waning Gibbous"
        elif phase_portion < 0.875:
            return f"🌗 {moon_name}: Last Quarter"
        else:
            return f"🌘 {moon_name}: Waning Crescent"

    def _get_khajiit_form(self, masser: str, secunda: str) -> str:
        """Determine Khajiit form based on moon phases (simplified)."""
        if "Full" in masser and "Full" in secunda:
            return "🐯 Senche (Large quadruped)"
        elif "Full" in masser and "New" in secunda:
            return "🐆 Pahmar (Large quadruped)"
        elif "New" in masser and "Full" in secunda:
            return "🐈 Alfiq (Housecat)"
        elif "New" in masser and "New" in secunda:
            return "🧝 Ohmes (Elven appearance)"
        else:
            return "🐱 Cathay (Humanoid)"

    def _calculate_tamriel_date(self, earth_date: datetime) -> Dict[str, Any]:
        """Calculate Tamrielic date from Earth date."""
        # Era calculation based on Skyrim timeline (4E 201 = 2011)
        era_info = self._tamriel_data["era_info"][self._era]
        era = self._era
        era_name = era_info["name"]

        # Calculate year within era (simplified - using Skyrim as reference)
        if era == "4E":
            # 4E 201 = 2011 (Skyrim's year)
            base_year = 201
            base_earth = 2011
            display_year = base_year + (earth_date.year - base_earth)
        else:
            # For other eras, use a simple offset
            display_year = 100 + (earth_date.year - 2000)

        # Get month data
        month_index = earth_date.month - 1
        month_data = self._tamriel_data["months"][month_index]
        tamriel_month = month_data["name"]
        tamriel_day = earth_date.day

        # Get weekday (aligned with Earth weekdays)
        weekday_index = earth_date.weekday()
        tamriel_weekday = self._tamriel_data["weekdays"][weekday_index]

        # Get birthsign
        birthsign_data = self._tamriel_data["birthsigns"][month_index] if self._show_birthsign else None
        birthsign = birthsign_data["name"] if birthsign_data else ""

        # Get divine blessing (cycles through the Nine Divines)
        divines = self._tamriel_data["divines"]
        divine_index = (earth_date.day - 1) % 9
        divine_blessing = divines[divine_index]

        # Season determination
        if month_index in [11, 0, 1]:  # Dec, Jan, Feb
            season = "Winter"
            season_emoji = "❄️"
        elif month_index in [2, 3, 4]:  # Mar, Apr, May
            season = "Spring"
            season_emoji = "🌸"
        elif month_index in [5, 6, 7]:  # Jun, Jul, Aug
            season = "Summer"
            season_emoji = "☀️"
        else:  # Sep, Oct, Nov
            season = "Autumn"
            season_emoji = "🍂"

        # Time period
        hour = earth_date.hour
        if 5 <= hour < 8:
            time_period = "Dawn"
            time_emoji = "🌅"
        elif 8 <= hour < 12:
            time_period = "Morning"
            time_emoji = "🌤️"
        elif 12 <= hour < 17:
            time_period = "Afternoon"
            time_emoji = "☀️"
        elif 17 <= hour < 20:
            time_period = "Dusk"
            time_emoji = "🌆"
        elif 20 <= hour < 24:
            time_period = "Night"
            time_emoji = "🌙"
        else:
            time_period = "Witching Hour"
            time_emoji = "⭐"

        # Guild activity
        guild_day = self._tamriel_data["guild_days"].get(tamriel_weekday, "")

        # Build result
        result = {
            "era": era,
            "era_name": era_name,
            "year": display_year,
            "month": tamriel_month,
            "day": tamriel_day,
            "weekday": tamriel_weekday,
            "season": f"{season_emoji} {season}",
            "divine_blessing": f"⚜️ {divine_blessing}",
            "guild_activity": guild_day,
            "time_period": f"{time_emoji} {time_period}",
            "full_date": f"{era} {display_year}, {tamriel_month} {tamriel_day}"
        }

        # Add birthsign if enabled
        if birthsign and self._show_birthsign:
            result["birthsign"] = f"⭐ {birthsign}"

        # Check for holidays if enabled
        if self._show_holidays:
            holiday = self._get_tamriel_holiday(earth_date.month, earth_date.day)
            if holiday:
                result["holiday"] = holiday

        # Check for Daedric days if enabled
        if self._show_daedric:
            daedric_prince = self._get_daedric_summoning_day(earth_date.month, earth_date.day)
            if daedric_prince:
                result["daedric_prince"] = daedric_prince

        # Calculate moon phases if enabled
        if self._show_moons:
            # Masser (larger moon) - 24 day cycle
            masser_phase = self._get_moon_phase(earth_date.day % 24, 24, "Masser")

            # Secunda (smaller moon) - 32 day cycle
            secunda_phase = self._get_moon_phase(earth_date.day % 32, 32, "Secunda")

            result["moon_phase_masser"] = masser_phase
            result["moon_phase_secunda"] = secunda_phase
            result["khajiit_form"] = self._get_khajiit_form(masser_phase, secunda_phase)

        return result

    def update(self) -> None:
        """Update the sensor."""
        now = datetime.now()
        self._tamriel_date = self._calculate_tamriel_date(now)

        # Format: Era Year, Month Day (Weekday)
        # Example: "4E 225, Morning Star 16 (Tirdas)"
        self._state = f"{self._tamriel_date['full_date']} ({self._tamriel_date['weekday']})"

        _LOGGER.debug(f"Updated Tamriel calendar to {self._state}")
