"""Star Trek Stardate implementation - Version 3.0."""
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

# Update interval in seconds (10 seconds for stardate precision)
UPDATE_INTERVAL = 10

# Complete calendar information for auto-discovery
CALENDAR_INFO = {
    "id": "stardate",
    "version": "3.0.0",
    "icon": "mdi:star-four-points",
    "category": "scifi",
    "accuracy": "fictional",
    "update_interval": UPDATE_INTERVAL,

    # Multi-language names
    "name": {
        "en": "Star Trek Stardate",
        "de": "Star Trek Sternzeit",
        "es": "Fecha Estelar Star Trek",
        "fr": "Date Stellaire Star Trek",
        "it": "Data Stellare Star Trek",
        "nl": "Star Trek Sterrendatum",
        "pl": "Gwiezdna Data Star Trek",
        "pt": "Data Estelar Star Trek",
        "ru": "Звездная дата Star Trek",
        "ja": "スタートレック宇宙暦",
        "zh": "星际迷航星历",
        "ko": "스타트렉 우주력"
    },

    # Short descriptions for UI
    "description": {
        "en": "Star Trek stardate system from various series (TNG, TOS, Discovery)",
        "de": "Star Trek Sternzeit-System aus verschiedenen Serien (TNG, TOS, Discovery)",
        "es": "Sistema de fecha estelar de Star Trek de varias series (TNG, TOS, Discovery)",
        "fr": "Système de date stellaire Star Trek de diverses séries (TNG, TOS, Discovery)",
        "it": "Sistema di data stellare Star Trek da varie serie (TNG, TOS, Discovery)",
        "nl": "Star Trek sterrendatum systeem uit verschillende series (TNG, TOS, Discovery)",
        "pl": "System gwiezdnej daty Star Trek z różnych serii (TNG, TOS, Discovery)",
        "pt": "Sistema de data estelar Star Trek de várias séries (TNG, TOS, Discovery)",
        "ru": "Система звездных дат Star Trek из различных серий (TNG, TOS, Discovery)",
        "ja": "様々なシリーズのスタートレック宇宙暦（TNG、TOS、ディスカバリー）",
        "zh": "来自不同系列的星际迷航星历系统（TNG、TOS、发现号）",
        "ko": "다양한 시리즈의 스타트렉 우주력 (TNG, TOS, 디스커버리)"
    },

    # Detailed information for documentation
    "detailed_info": {
        "en": {
            "overview": "Stardates are the standard time measurement in Star Trek",
            "tng_format": "TNG format: [Century][Year].[Day fraction]",
            "calculation": "1000 units per Earth year, starting from 2323",
            "precision": "Decimal places indicate time of day",
            "series": "Different series use different stardate systems",
            "tos": "TOS: Arbitrary 4-digit numbers",
            "tng": "TNG/DS9/VOY: Systematic 5-digit system",
            "discovery": "DIS: 4-digit year-based system"
        },
        "de": {
            "overview": "Sternzeiten sind die Standard-Zeitmessung in Star Trek",
            "tng_format": "TNG-Format: [Jahrhundert][Jahr].[Tagesbruchteil]",
            "calculation": "1000 Einheiten pro Erdjahr, beginnend ab 2323",
            "precision": "Dezimalstellen zeigen die Tageszeit an",
            "series": "Verschiedene Serien verwenden verschiedene Sternzeitsysteme",
            "tos": "TOS: Willkürliche 4-stellige Zahlen",
            "tng": "TNG/DS9/VOY: Systematisches 5-stelliges System",
            "discovery": "DIS: 4-stelliges jahresbasiertes System"
        }
    },

    # Configuration options
    "config_options": {
        "format": {
            "type": "select",
            "default": "tng",
            "options": ["tng", "tos", "discovery", "kelvin"],
            "label": {
                "en": "Stardate Format",
                "de": "Sternzeit-Format",
                "es": "Formato de Fecha Estelar",
                "fr": "Format de Date Stellaire",
                "it": "Formato Data Stellare",
                "nl": "Sterrendatum Formaat",
                "pl": "Format Gwiezdnej Daty",
                "pt": "Formato de Data Estelar",
                "ru": "Формат звездной даты",
                "ja": "宇宙暦形式",
                "zh": "星历格式",
                "ko": "우주력 형식"
            },
            "description": {
                "en": "Choose which Star Trek series' stardate system to use",
                "de": "Wähle welches Star Trek Serien-Sternzeitsystem verwendet werden soll",
                "es": "Elige qué sistema de fecha estelar de la serie Star Trek usar",
                "fr": "Choisissez quel système de date stellaire de la série Star Trek utiliser",
                "it": "Scegli quale sistema di data stellare della serie Star Trek usare",
                "nl": "Kies welk Star Trek serie sterrendatum systeem te gebruiken",
                "pl": "Wybierz, który system gwiezdnej daty z serii Star Trek użyć",
                "pt": "Escolha qual sistema de data estelar da série Star Trek usar",
                "ru": "Выберите систему звездных дат из серий Star Trek",
                "ja": "使用するスタートレックシリーズの宇宙暦システムを選択",
                "zh": "选择使用哪个星际迷航系列的星历系统",
                "ko": "사용할 스타트렉 시리즈의 우주력 시스템 선택"
            },
            "options_label": {
                "tng": {
                    "en": "The Next Generation / Deep Space Nine / Voyager",
                    "de": "The Next Generation / Deep Space Nine / Voyager",
                    "es": "La Nueva Generación / Espacio Profundo Nueve / Voyager",
                    "fr": "La Nouvelle Génération / Deep Space Nine / Voyager",
                    "it": "The Next Generation / Deep Space Nine / Voyager",
                    "nl": "The Next Generation / Deep Space Nine / Voyager",
                    "pl": "Następne Pokolenie / Deep Space Nine / Voyager",
                    "pt": "A Nova Geração / Deep Space Nine / Voyager",
                    "ru": "Следующее поколение / Глубокий космос 9 / Вояджер",
                    "ja": "新スタートレック / ディープ・スペース・ナイン / ヴォイジャー",
                    "zh": "下一代 / 深空九号 / 航海家号",
                    "ko": "넥스트 제너레이션 / 딥 스페이스 나인 / 보이저"
                },
                "tos": {
                    "en": "The Original Series / The Animated Series",
                    "de": "Die Originalserie / Die Animierte Serie",
                    "es": "La Serie Original / La Serie Animada",
                    "fr": "La Série Originale / La Série Animée",
                    "it": "La Serie Originale / La Serie Animata",
                    "nl": "De Originele Serie / De Geanimeerde Serie",
                    "pl": "Seria Oryginalna / Seria Animowana",
                    "pt": "A Série Original / A Série Animada",
                    "ru": "Оригинальный сериал / Анимационный сериал",
                    "ja": "宇宙大作戦 / まんが宇宙大作戦",
                    "zh": "原初系列 / 动画系列",
                    "ko": "오리지널 시리즈 / 애니메이션 시리즈"
                },
                "discovery": {
                    "en": "Discovery / Strange New Worlds",
                    "de": "Discovery / Strange New Worlds",
                    "es": "Discovery / Nuevos Mundos Extraños",
                    "fr": "Discovery / Nouveaux Mondes Étranges",
                    "it": "Discovery / Strange New Worlds",
                    "nl": "Discovery / Strange New Worlds",
                    "pl": "Discovery / Dziwne Nowe Światy",
                    "pt": "Discovery / Novos Mundos Estranhos",
                    "ru": "Дискавери / Странные новые миры",
                    "ja": "ディスカバリー / ストレンジ・ニュー・ワールド",
                    "zh": "发现号 / 奇异新世界",
                    "ko": "디스커버리 / 스트레인지 뉴 월드"
                },
                "kelvin": {
                    "en": "Kelvin Timeline (2009 Movies)",
                    "de": "Kelvin-Zeitlinie (2009 Filme)",
                    "es": "Línea Temporal Kelvin (Películas 2009)",
                    "fr": "Chronologie Kelvin (Films 2009)",
                    "it": "Linea Temporale Kelvin (Film 2009)",
                    "nl": "Kelvin Tijdlijn (2009 Films)",
                    "pl": "Linia Czasu Kelvina (Filmy 2009)",
                    "pt": "Linha Temporal Kelvin (Filmes 2009)",
                    "ru": "Временная линия Кельвина (Фильмы 2009)",
                    "ja": "ケルヴィン・タイムライン（2009年映画）",
                    "zh": "开尔文时间线（2009年电影）",
                    "ko": "켈빈 타임라인 (2009년 영화)"
                }
            }
        },
        "show_event": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show Notable Events",
                "de": "Bemerkenswerte Ereignisse anzeigen",
                "es": "Mostrar eventos notables",
                "fr": "Afficher les événements notables",
                "it": "Mostra eventi notevoli",
                "nl": "Toon opmerkelijke gebeurtenissen",
                "pl": "Pokaż znaczące wydarzenia",
                "pt": "Mostrar eventos notáveis",
                "ru": "Показать значимые события",
                "ja": "注目すべきイベントを表示",
                "zh": "显示重要事件",
                "ko": "주목할만한 사건 표시"
            },
            "description": {
                "en": "Display notable Star Trek episodes and events for nearby stardates",
                "de": "Zeige bemerkenswerte Star Trek Episoden und Ereignisse für nahe Sternzeiten",
                "es": "Mostrar episodios y eventos notables de Star Trek para fechas estelares cercanas",
                "fr": "Afficher les épisodes et événements notables de Star Trek pour les dates stellaires proches",
                "it": "Mostra episodi ed eventi notevoli di Star Trek per date stellari vicine",
                "nl": "Toon opmerkelijke Star Trek afleveringen en gebeurtenissen voor nabije sterrendata",
                "pl": "Pokaż znaczące odcinki i wydarzenia Star Trek dla pobliskich gwiezdnych dat",
                "pt": "Mostrar episódios e eventos notáveis de Star Trek para datas estelares próximas",
                "ru": "Показать значимые эпизоды и события Star Trek для близких звездных дат",
                "ja": "近い宇宙暦のスタートレックの注目エピソードとイベントを表示",
                "zh": "显示附近星历的星际迷航重要剧集和事件",
                "ko": "가까운 우주력의 스타트렉 주요 에피소드와 사건 표시"
            }
        },
        "show_ship": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show Starship",
                "de": "Raumschiff anzeigen",
                "es": "Mostrar nave estelar",
                "fr": "Afficher le vaisseau",
                "it": "Mostra astronave",
                "nl": "Toon ruimteschip",
                "pl": "Pokaż statek kosmiczny",
                "pt": "Mostrar nave estelar",
                "ru": "Показать звездолет",
                "ja": "宇宙船を表示",
                "zh": "显示星舰",
                "ko": "우주선 표시"
            },
            "description": {
                "en": "Display a rotating selection of famous Starfleet vessels",
                "de": "Zeige eine rotierende Auswahl berühmter Sternenflotten-Schiffe",
                "es": "Mostrar una selección rotativa de naves famosas de la Flota Estelar",
                "fr": "Afficher une sélection rotative de vaisseaux célèbres de Starfleet",
                "it": "Mostra una selezione rotante di famose navi della Flotta Stellare",
                "nl": "Toon een roterende selectie van beroemde Starfleet schepen",
                "pl": "Pokaż rotującą selekcję słynnych statków Gwiezdnej Floty",
                "pt": "Mostrar uma seleção rotativa de naves famosas da Frota Estelar",
                "ru": "Показать чередующийся выбор знаменитых кораблей Звездного флота",
                "ja": "有名な宇宙艦隊の船のローテーション選択を表示",
                "zh": "显示著名星际舰队舰船的轮换选择",
                "ko": "유명한 스타플릿 함선의 순환 선택 표시"
            }
        },
        "precision": {
            "type": "select",
            "default": "2",
            "options": ["0", "1", "2", "3", "4"],
            "label": {
                "en": "Decimal Precision",
                "de": "Dezimalgenauigkeit",
                "es": "Precisión decimal",
                "fr": "Précision décimale",
                "it": "Precisione decimale",
                "nl": "Decimale precisie",
                "pl": "Precyzja dziesiętna",
                "pt": "Precisão decimal",
                "ru": "Десятичная точность",
                "ja": "小数点精度",
                "zh": "小数精度",
                "ko": "소수점 정밀도"
            },
            "description": {
                "en": "Number of decimal places to display (e.g., 47634.44)",
                "de": "Anzahl der anzuzeigenden Dezimalstellen (z.B. 47634,44)",
                "es": "Número de decimales a mostrar (ej. 47634.44)",
                "fr": "Nombre de décimales à afficher (ex. 47634.44)",
                "it": "Numero di decimali da visualizzare (es. 47634.44)",
                "nl": "Aantal decimalen om weer te geven (bijv. 47634.44)",
                "pl": "Liczba miejsc dziesiętnych do wyświetlenia (np. 47634.44)",
                "pt": "Número de casas decimais a exibir (ex. 47634.44)",
                "ru": "Количество десятичных знаков для отображения (напр. 47634.44)",
                "ja": "表示する小数点以下の桁数（例：47634.44）",
                "zh": "要显示的小数位数（例如：47634.44）",
                "ko": "표시할 소수 자릿수 (예: 47634.44)"
            },
            "options_label": {
                "0": {
                    "en": "No decimals (47634)",
                    "de": "Keine Dezimalstellen (47634)",
                    "es": "Sin decimales (47634)",
                    "fr": "Sans décimales (47634)",
                    "it": "Senza decimali (47634)",
                    "nl": "Geen decimalen (47634)",
                    "pl": "Bez miejsc dziesiętnych (47634)",
                    "pt": "Sem decimais (47634)",
                    "ru": "Без десятичных знаков (47634)",
                    "ja": "小数点なし (47634)",
                    "zh": "无小数 (47634)",
                    "ko": "소수점 없음 (47634)"
                },
                "1": {
                    "en": "1 decimal (47634.4)",
                    "de": "1 Dezimalstelle (47634,4)",
                    "es": "1 decimal (47634.4)",
                    "fr": "1 décimale (47634.4)",
                    "it": "1 decimale (47634.4)",
                    "nl": "1 decimaal (47634.4)",
                    "pl": "1 miejsce dziesiętne (47634.4)",
                    "pt": "1 decimal (47634.4)",
                    "ru": "1 десятичный знак (47634.4)",
                    "ja": "小数点1桁 (47634.4)",
                    "zh": "1位小数 (47634.4)",
                    "ko": "소수점 1자리 (47634.4)"
                },
                "2": {
                    "en": "2 decimals (47634.44)",
                    "de": "2 Dezimalstellen (47634,44)",
                    "es": "2 decimales (47634.44)",
                    "fr": "2 décimales (47634.44)",
                    "it": "2 decimali (47634.44)",
                    "nl": "2 decimalen (47634.44)",
                    "pl": "2 miejsca dziesiętne (47634.44)",
                    "pt": "2 decimais (47634.44)",
                    "ru": "2 десятичных знака (47634.44)",
                    "ja": "小数点2桁 (47634.44)",
                    "zh": "2位小数 (47634.44)",
                    "ko": "소수점 2자리 (47634.44)"
                },
                "3": {
                    "en": "3 decimals (47634.440)",
                    "de": "3 Dezimalstellen (47634,440)",
                    "es": "3 decimales (47634.440)",
                    "fr": "3 décimales (47634.440)",
                    "it": "3 decimali (47634.440)",
                    "nl": "3 decimalen (47634.440)",
                    "pl": "3 miejsca dziesiętne (47634.440)",
                    "pt": "3 decimais (47634.440)",
                    "ru": "3 десятичных знака (47634.440)",
                    "ja": "小数点3桁 (47634.440)",
                    "zh": "3位小数 (47634.440)",
                    "ko": "소수점 3자리 (47634.440)"
                },
                "4": {
                    "en": "4 decimals (47634.4400)",
                    "de": "4 Dezimalstellen (47634,4400)",
                    "es": "4 decimales (47634.4400)",
                    "fr": "4 décimales (47634.4400)",
                    "it": "4 decimali (47634.4400)",
                    "nl": "4 decimalen (47634.4400)",
                    "pl": "4 miejsca dziesiętne (47634.4400)",
                    "pt": "4 decimais (47634.4400)",
                    "ru": "4 десятичных знака (47634.4400)",
                    "ja": "小数点4桁 (47634.4400)",
                    "zh": "4位小数 (47634.4400)",
                    "ko": "소수점 4자리 (47634.4400)"
                }
            }
        }
    },

    # Stardate-specific data
    "stardate_data": {
        "base_year": 2323,
        "units_per_year": 1000,
        "units_per_day": 2.73785,

        # Notable stardates and events
        "notable_events": {
            41153.7: "📺 Encounter at Farpoint (TNG Pilot)",
            41986.0: "🔷 The Best of Both Worlds Part 1",
            44001.4: "🔷 The Best of Both Worlds Part 2",
            45854.2: "🎭 The Inner Light",
            47457.1: "🎬 All Good Things... (TNG Finale)",
            48315.6: "🚀 Caretaker (VOY Pilot)",
            49827.5: "🦂 Scorpion Part 1",
            51721.3: "⚔️ Way of the Warrior (DS9)",
            52861.3: "🌟 What You Leave Behind (DS9 Finale)",
            54868.6: "🏁 Endgame (VOY Finale)",
            56844.9: "🎬 Star Trek (2009 Film)",
            57436.2: "🎬 Star Trek Into Darkness",
            59796.7: "🎬 Star Trek Beyond"
        },

        # Starfleet ships
        "ships": [
            {"registry": "NCC-1701", "name": "USS Enterprise", "class": "Constitution", "era": "TOS"},
            {"registry": "NCC-1701-A", "name": "USS Enterprise-A", "class": "Constitution", "era": "TOS Movies"},
            {"registry": "NCC-1701-B", "name": "USS Enterprise-B", "class": "Excelsior", "era": "Lost Era"},
            {"registry": "NCC-1701-C", "name": "USS Enterprise-C", "class": "Ambassador", "era": "Lost Era"},
            {"registry": "NCC-1701-D", "name": "USS Enterprise-D", "class": "Galaxy", "era": "TNG"},
            {"registry": "NCC-1701-E", "name": "USS Enterprise-E", "class": "Sovereign", "era": "TNG Movies"},
            {"registry": "NCC-74205", "name": "USS Defiant", "class": "Defiant", "era": "DS9"},
            {"registry": "NCC-74656", "name": "USS Voyager", "class": "Intrepid", "era": "VOY"},
            {"registry": "NX-01", "name": "Enterprise NX-01", "class": "NX", "era": "ENT"},
            {"registry": "NCC-1031", "name": "USS Discovery", "class": "Crossfield", "era": "DIS"}
        ],

        # Quadrants
        "quadrants": ["Alpha", "Beta", "Gamma", "Delta"],

        # Major powers
        "powers": [
            "United Federation of Planets",
            "Klingon Empire",
            "Romulan Star Empire",
            "Cardassian Union",
            "Dominion",
            "Borg Collective"
        ]
    },

    # Additional metadata
    "reference_url": "https://memory-alpha.fandom.com/wiki/Stardate",
    "documentation_url": "https://www.startrek.com/database_article/stardate",
    "origin": "Star Trek (Gene Roddenberry)",
    "created_by": "Gene Roddenberry",
    "introduced": "Star Trek: The Original Series (1966)",

    # Example format
    "example": "47634.44",
    "example_meaning": "Year 47 of the 24th century, day 634.44",

    # Related calendars
    "related": ["gregorian", "julian", "scifi"],

    # Tags for searching and filtering
    "tags": [
        "scifi", "star_trek", "stardate", "starfleet", "federation",
        "tng", "voyager", "ds9", "enterprise", "discovery", "space"
    ],

    # Special features
    "features": {
        "decimal_time": True,
        "fictional_future": True,
        "series_variations": True,
        "precision": "fractional_day"
    }
}


class StardateSensor(AlternativeTimeSensorBase):
    """Sensor for displaying Stardate (Star Trek style)."""

    # Class-level update interval
    UPDATE_INTERVAL = UPDATE_INTERVAL

    def __init__(self, base_name: str, hass: HomeAssistant) -> None:
        """Initialize the stardate sensor."""
        super().__init__(base_name, hass)

        # Get translated name from metadata
        calendar_name = self._translate('name', 'Star Trek Stardate')

        # Set sensor attributes
        self._attr_name = f"{base_name} {calendar_name}"
        self._attr_unique_id = f"{base_name}_stardate"
        self._attr_icon = CALENDAR_INFO.get("icon", "mdi:star-four-points")

        # Configuration options with defaults
        config_defaults = CALENDAR_INFO.get("config_options", {})
        self._format = config_defaults.get("format", {}).get("default", "tng")
        self._show_event = config_defaults.get("show_event", {}).get("default", True)
        self._show_ship = config_defaults.get("show_ship", {}).get("default", True)
        self._precision = int(config_defaults.get("precision", {}).get("default", "2"))

        # Stardate data
        self._stardate_data = CALENDAR_INFO["stardate_data"]

        # Initialize state
        self._state = None
        self._stardate = {}

        # Ship rotation index
        self._ship_index = 0

        _LOGGER.debug(f"Initialized Stardate sensor: {self._attr_name}")

    def set_options(self, options: Dict[str, Any]) -> None:
        """Set options from config flow."""
        if options:
            self._format = options.get("format", self._format)
            self._show_event = options.get("show_event", self._show_event)
            self._show_ship = options.get("show_ship", self._show_ship)
            self._precision = int(options.get("precision", self._precision))

            _LOGGER.debug(f"Stardate sensor options updated: format={self._format}, "
                         f"show_event={self._show_event}, show_ship={self._show_ship}, "
                         f"precision={self._precision}")

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes."""
        attrs = super().extra_state_attributes

        # Add Stardate-specific attributes
        if self._stardate:
            attrs.update(self._stardate)

            # Add description in user's language
            attrs["description"] = self._translate('description')

            # Add reference
            attrs["reference"] = CALENDAR_INFO.get('reference_url', '')

            # Add configuration status
            attrs["config"] = {
                "format": self._format,
                "show_event": self._show_event,
                "show_ship": self._show_ship,
                "precision": self._precision
            }

        return attrs

    def _calculate_tng_stardate(self, earth_date: datetime) -> float:
        """Calculate TNG-style stardate."""
        base_year = self._stardate_data["base_year"]
        current_year = earth_date.year
        day_of_year = earth_date.timetuple().tm_yday

        # Calculate stardate
        stardate = 1000 * (current_year - base_year)
        stardate += (1000 * day_of_year / 365.25)

        # Add time of day as fraction
        time_fraction = (earth_date.hour * 60 + earth_date.minute) / 1440 * 10
        stardate += time_fraction

        return stardate

    def _calculate_tos_stardate(self, earth_date: datetime) -> float:
        """Calculate TOS-style stardate (simplified)."""
        # TOS stardates were somewhat arbitrary
        # We'll use a simplified version
        base = 1312.4  # Starting point
        days_since_2000 = (earth_date - datetime(2000, 1, 1)).days
        return base + (days_since_2000 * 0.5)

    def _calculate_discovery_stardate(self, earth_date: datetime) -> float:
        """Calculate Discovery-style stardate."""
        # Discovery uses year.day format
        year = earth_date.year
        day_of_year = earth_date.timetuple().tm_yday
        hour_fraction = earth_date.hour / 24
        return year + (day_of_year + hour_fraction) / 365.25

    def _calculate_kelvin_stardate(self, earth_date: datetime) -> float:
        """Calculate Kelvin Timeline stardate."""
        # Kelvin timeline uses a different system (YYYY.DD format)
        year = earth_date.year
        day_of_year = earth_date.timetuple().tm_yday
        return year + (day_of_year / 1000)

    def _find_notable_event(self, stardate: float) -> str:
        """Find notable event near this stardate."""
        if not self._show_event or self._format != "tng":
            return ""

        closest_event = None
        min_diff = float('inf')

        for event_stardate, event in self._stardate_data["notable_events"].items():
            diff = abs(stardate - event_stardate)
            if diff < 100 and diff < min_diff:  # Within 100 units
                min_diff = diff
                closest_event = event

        return closest_event or ""

    def _get_current_ship(self) -> Dict[str, str]:
        """Get current ship from rotation."""
        if not self._show_ship:
            return {}

        ship = self._stardate_data["ships"][self._ship_index]
        self._ship_index = (self._ship_index + 1) % len(self._stardate_data["ships"])
        return ship

    def _calculate_stardate(self, earth_date: datetime) -> Dict[str, Any]:
        """Calculate Stardate from Earth date."""

        # Calculate based on format
        if self._format == "tos":
            stardate = self._calculate_tos_stardate(earth_date)
            era = "The Original Series Era"
            series = "TOS"
        elif self._format == "discovery":
            stardate = self._calculate_discovery_stardate(earth_date)
            era = "Discovery Era"
            series = "DIS"
        elif self._format == "kelvin":
            stardate = self._calculate_kelvin_stardate(earth_date)
            era = "Kelvin Timeline"
            series = "Kelvin"
        else:  # tng
            stardate = self._calculate_tng_stardate(earth_date)
            era = "The Next Generation Era"
            series = "TNG"

        # Format with precision
        formatted = f"{stardate:.{self._precision}f}"

        # Determine century
        if stardate < 10000:
            century = "23rd Century"
        elif stardate < 50000:
            century = "24th Century"
        else:
            century = "25th Century"

        # Calculate quadrant (simplified - rotates every 6 hours)
        quadrant_index = int((earth_date.hour / 6)) % 4
        current_quadrant = self._stardate_data["quadrants"][quadrant_index]

        # Get notable event
        event = self._find_notable_event(stardate) if self._format == "tng" else ""

        # Get current ship
        ship_data = self._get_current_ship() if self._show_ship else {}

        # Build result
        result = {
            "stardate": stardate,
            "formatted": formatted,
            "era": era,
            "series": series,
            "century": century,
            "quadrant": f"{current_quadrant} Quadrant",
            "earth_date": earth_date.strftime("%Y-%m-%d %H:%M:%S"),
            "year_component": int(stardate // 1000) if self._format == "tng" else 0,
            "day_component": stardate % 1000 if self._format == "tng" else 0
        }

        # Add optional data
        if event:
            result["notable_event"] = event

        if ship_data:
            result["current_ship"] = f"🚀 {ship_data['name']}"
            result["ship_registry"] = ship_data['registry']
            result["ship_class"] = f"{ship_data['class']} class"
            result["ship_era"] = ship_data['era']

        return result

    def update(self) -> None:
        """Update the sensor."""
        now = datetime.now()
        self._stardate = self._calculate_stardate(now)

        # Set state to formatted stardate
        self._state = self._stardate["formatted"]

        _LOGGER.debug(f"Updated Stardate to {self._state}")
