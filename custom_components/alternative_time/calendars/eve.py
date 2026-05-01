"""EVE Online Time (New Eden Standard Time) implementation - Version 3.0."""
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

# Update interval in seconds (1 second for real-time display)
UPDATE_INTERVAL = 1

# Complete calendar information for auto-discovery
CALENDAR_INFO = {
    "id": "eve",
    "version": "3.0.0",
    "icon": "mdi:space-station",
    "category": "scifi",
    "accuracy": "fictional",
    "update_interval": UPDATE_INTERVAL,

    # Multi-language names
    "name": {
        "en": "EVE Online Time",
        "de": "EVE Online Zeit",
        "es": "Tiempo de EVE Online",
        "fr": "Temps EVE Online",
        "it": "Tempo di EVE Online",
        "nl": "EVE Online Tijd",
        "pl": "Czas EVE Online",
        "pt": "Tempo de EVE Online",
        "ru": "Время EVE Online",
        "ja": "EVE Online時間",
        "zh": "EVE Online时间",
        "ko": "EVE 온라인 시간"
    },

    # Short descriptions for UI
    "description": {
        "en": "New Eden Standard Time (NEST) from EVE Online universe with YC calendar",
        "de": "New Eden Standardzeit (NEST) aus dem EVE Online Universum mit YC-Kalender",
        "es": "Hora Estándar de Nuevo Edén (NEST) del universo EVE Online con calendario YC",
        "fr": "Temps Standard de New Eden (NEST) de l'univers EVE Online avec calendrier YC",
        "it": "Ora Standard di New Eden (NEST) dall'universo EVE Online con calendario YC",
        "nl": "New Eden Standaard Tijd (NEST) uit het EVE Online universum met YC kalender",
        "pl": "Standardowy Czas Nowego Edenu (NEST) z uniwersum EVE Online z kalendarzem YC",
        "pt": "Hora Padrão de New Eden (NEST) do universo EVE Online com calendário YC",
        "ru": "Стандартное время Нового Эдема (NEST) из вселенной EVE Online с календарем YC",
        "ja": "EVE Onlineユニバースのニューエデン標準時（NEST）とYCカレンダー",
        "zh": "EVE Online宇宙的新伊甸标准时间（NEST）和YC历法",
        "ko": "EVE 온라인 우주의 뉴 에덴 표준시 (NEST)와 YC 달력"
    },

    # Detailed information for documentation
    "detailed_info": {
        "en": {
            "overview": "EVE Online uses New Eden Standard Time (NEST) based on UTC",
            "calendar": "Yoiul Conference (YC) calendar system",
            "epoch": "YC 0 corresponds to 23236 AD in Earth time",
            "game_start": "YC 105 = 2003 (EVE Online launch year)",
            "structure": "Uses standard Earth months and days, all times in UTC",
            "lore": "The Yoiul Conference established a universal calendar after the collapse of the EVE Gate",
            "empires": "Used by all four major empires: Amarr, Caldari, Gallente, and Minmatar",
            "format": "Standard format: YC XXX.MM.DD HH:MM:SS"
        },
        "de": {
            "overview": "EVE Online verwendet New Eden Standardzeit (NEST) basierend auf UTC",
            "calendar": "Yoiul Conference (YC) Kalendersystem",
            "epoch": "YC 0 entspricht 23236 n.Chr. in Erdzeit",
            "game_start": "YC 105 = 2003 (EVE Online Startjahr)",
            "structure": "Verwendet Standard-Erdmonate und -tage, alle Zeiten in UTC",
            "lore": "Die Yoiul-Konferenz etablierte einen universellen Kalender nach dem Kollaps des EVE-Tors",
            "empires": "Verwendet von allen vier großen Imperien: Amarr, Caldari, Gallente und Minmatar",
            "format": "Standardformat: YC XXX.MM.DD HH:MM:SS"
        }
    },

    # Configuration options
    "config_options": {
        "show_nest": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show NEST Label",
                "de": "NEST-Label anzeigen",
                "es": "Mostrar etiqueta NEST",
                "fr": "Afficher l'étiquette NEST",
                "it": "Mostra etichetta NEST",
                "nl": "Toon NEST label",
                "pl": "Pokaż etykietę NEST",
                "pt": "Mostrar rótulo NEST",
                "ru": "Показать метку NEST",
                "ja": "NESTラベルを表示",
                "zh": "显示NEST标签",
                "ko": "NEST 라벨 표시"
            },
            "description": {
                "en": "Display 'NEST' (New Eden Standard Time) after the time",
                "de": "Zeige 'NEST' (New Eden Standardzeit) nach der Zeit",
                "es": "Mostrar 'NEST' (Hora Estándar de Nuevo Edén) después de la hora",
                "fr": "Afficher 'NEST' (Temps Standard de New Eden) après l'heure",
                "it": "Mostra 'NEST' (Ora Standard di New Eden) dopo l'ora",
                "nl": "Toon 'NEST' (New Eden Standaard Tijd) na de tijd",
                "pl": "Pokaż 'NEST' (Standardowy Czas Nowego Edenu) po czasie",
                "pt": "Mostrar 'NEST' (Hora Padrão de New Eden) após a hora",
                "ru": "Показать 'NEST' (Стандартное время Нового Эдема) после времени",
                "ja": "時刻の後に'NEST'（ニューエデン標準時）を表示",
                "zh": "在时间后显示'NEST'（新伊甸标准时间）",
                "ko": "시간 뒤에 'NEST' (뉴 에덴 표준시) 표시"
            }
        },
        "show_event": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show Historical Events",
                "de": "Historische Ereignisse anzeigen",
                "es": "Mostrar eventos históricos",
                "fr": "Afficher les événements historiques",
                "it": "Mostra eventi storici",
                "nl": "Toon historische gebeurtenissen",
                "pl": "Pokaż wydarzenia historyczne",
                "pt": "Mostrar eventos históricos",
                "ru": "Показать исторические события",
                "ja": "歴史的イベントを表示",
                "zh": "显示历史事件",
                "ko": "역사적 사건 표시"
            },
            "description": {
                "en": "Display notable events from EVE Online history for the current YC year",
                "de": "Zeige bemerkenswerte Ereignisse aus der EVE Online Geschichte für das aktuelle YC-Jahr",
                "es": "Mostrar eventos notables de la historia de EVE Online para el año YC actual",
                "fr": "Afficher les événements notables de l'histoire d'EVE Online pour l'année YC actuelle",
                "it": "Mostra eventi notevoli dalla storia di EVE Online per l'anno YC attuale",
                "nl": "Toon opmerkelijke gebeurtenissen uit EVE Online geschiedenis voor het huidige YC jaar",
                "pl": "Pokaż znaczące wydarzenia z historii EVE Online dla bieżącego roku YC",
                "pt": "Mostrar eventos notáveis da história de EVE Online para o ano YC atual",
                "ru": "Показать значимые события из истории EVE Online для текущего года YC",
                "ja": "現在のYC年のEVE Onlineの歴史から注目すべきイベントを表示",
                "zh": "显示当前YC年EVE Online历史上的重要事件",
                "ko": "현재 YC 연도의 EVE 온라인 역사상 주목할만한 사건 표시"
            }
        },
        "show_empire": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show Empire Info",
                "de": "Imperium-Info anzeigen",
                "es": "Mostrar información del imperio",
                "fr": "Afficher les infos de l'empire",
                "it": "Mostra info impero",
                "nl": "Toon rijk informatie",
                "pl": "Pokaż informacje o imperium",
                "pt": "Mostrar informação do império",
                "ru": "Показать информацию об империи",
                "ja": "帝国情報を表示",
                "zh": "显示帝国信息",
                "ko": "제국 정보 표시"
            },
            "description": {
                "en": "Display information about the four major empires",
                "de": "Zeige Informationen über die vier großen Imperien",
                "es": "Mostrar información sobre los cuatro imperios principales",
                "fr": "Afficher des informations sur les quatre empires majeurs",
                "it": "Mostra informazioni sui quattro imperi principali",
                "nl": "Toon informatie over de vier grote rijken",
                "pl": "Pokaż informacje o czterech głównych imperiach",
                "pt": "Mostrar informação sobre os quatro impérios principais",
                "ru": "Показать информацию о четырех основных империях",
                "ja": "4つの主要帝国に関する情報を表示",
                "zh": "显示四大帝国的信息",
                "ko": "네 개의 주요 제국에 대한 정보 표시"
            }
        },
        "show_system": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show Trade Hub",
                "de": "Handelszentrum anzeigen",
                "es": "Mostrar centro comercial",
                "fr": "Afficher le hub commercial",
                "it": "Mostra centro commerciale",
                "nl": "Toon handelscentrum",
                "pl": "Pokaż centrum handlowe",
                "pt": "Mostrar centro comercial",
                "ru": "Показать торговый хаб",
                "ja": "トレードハブを表示",
                "zh": "显示贸易中心",
                "ko": "무역 허브 표시"
            },
            "description": {
                "en": "Display current major trade hub system (Jita, Amarr, Dodixie, etc.)",
                "de": "Zeige aktuelles Haupthandelszentrum-System (Jita, Amarr, Dodixie, etc.)",
                "es": "Mostrar sistema de centro comercial principal actual (Jita, Amarr, Dodixie, etc.)",
                "fr": "Afficher le système de hub commercial majeur actuel (Jita, Amarr, Dodixie, etc.)",
                "it": "Mostra il sistema del centro commerciale principale attuale (Jita, Amarr, Dodixie, ecc.)",
                "nl": "Toon huidig groot handelscentrum systeem (Jita, Amarr, Dodixie, etc.)",
                "pl": "Pokaż aktualny główny system centrum handlowego (Jita, Amarr, Dodixie, itp.)",
                "pt": "Mostrar sistema de centro comercial principal atual (Jita, Amarr, Dodixie, etc.)",
                "ru": "Показать текущую основную систему торгового хаба (Jita, Amarr, Dodixie и т.д.)",
                "ja": "現在の主要トレードハブシステムを表示（Jita、Amarr、Dodixieなど）",
                "zh": "显示当前主要贸易中心系统（吉他、阿玛尔、多迪谢等）",
                "ko": "현재 주요 무역 허브 시스템 표시 (지타, 아마르, 도딕시 등)"
            }
        },
        "format": {
            "type": "select",
            "default": "full",
            "options": ["full", "date", "time", "compact"],
            "label": {
                "en": "Display Format",
                "de": "Anzeigeformat",
                "es": "Formato de visualización",
                "fr": "Format d'affichage",
                "it": "Formato di visualizzazione",
                "nl": "Weergaveformaat",
                "pl": "Format wyświetlania",
                "pt": "Formato de exibição",
                "ru": "Формат отображения",
                "ja": "表示形式",
                "zh": "显示格式",
                "ko": "표시 형식"
            },
            "description": {
                "en": "Choose how the EVE time is displayed",
                "de": "Wähle wie die EVE-Zeit angezeigt wird",
                "es": "Elige cómo se muestra el tiempo de EVE",
                "fr": "Choisissez comment le temps EVE est affiché",
                "it": "Scegli come viene visualizzato il tempo di EVE",
                "nl": "Kies hoe de EVE tijd wordt weergegeven",
                "pl": "Wybierz sposób wyświetlania czasu EVE",
                "pt": "Escolha como o tempo EVE é exibido",
                "ru": "Выберите формат отображения времени EVE",
                "ja": "EVE時間の表示方法を選択",
                "zh": "选择EVE时间的显示方式",
                "ko": "EVE 시간 표시 방법 선택"
            },
            "options_label": {
                "full": {
                    "en": "Full (YC 127.01.15 14:30:00 NEST)",
                    "de": "Vollständig (YC 127.01.15 14:30:00 NEST)",
                    "es": "Completo (YC 127.01.15 14:30:00 NEST)",
                    "fr": "Complet (YC 127.01.15 14:30:00 NEST)",
                    "it": "Completo (YC 127.01.15 14:30:00 NEST)",
                    "nl": "Volledig (YC 127.01.15 14:30:00 NEST)",
                    "pl": "Pełny (YC 127.01.15 14:30:00 NEST)",
                    "pt": "Completo (YC 127.01.15 14:30:00 NEST)",
                    "ru": "Полный (YC 127.01.15 14:30:00 NEST)",
                    "ja": "完全 (YC 127.01.15 14:30:00 NEST)",
                    "zh": "完整 (YC 127.01.15 14:30:00 NEST)",
                    "ko": "전체 (YC 127.01.15 14:30:00 NEST)"
                },
                "date": {
                    "en": "Date only (YC 127.01.15)",
                    "de": "Nur Datum (YC 127.01.15)",
                    "es": "Solo fecha (YC 127.01.15)",
                    "fr": "Date seulement (YC 127.01.15)",
                    "it": "Solo data (YC 127.01.15)",
                    "nl": "Alleen datum (YC 127.01.15)",
                    "pl": "Tylko data (YC 127.01.15)",
                    "pt": "Apenas data (YC 127.01.15)",
                    "ru": "Только дата (YC 127.01.15)",
                    "ja": "日付のみ (YC 127.01.15)",
                    "zh": "仅日期 (YC 127.01.15)",
                    "ko": "날짜만 (YC 127.01.15)"
                },
                "time": {
                    "en": "Time only (14:30:00)",
                    "de": "Nur Zeit (14:30:00)",
                    "es": "Solo hora (14:30:00)",
                    "fr": "Heure seulement (14:30:00)",
                    "it": "Solo ora (14:30:00)",
                    "nl": "Alleen tijd (14:30:00)",
                    "pl": "Tylko czas (14:30:00)",
                    "pt": "Apenas hora (14:30:00)",
                    "ru": "Только время (14:30:00)",
                    "ja": "時刻のみ (14:30:00)",
                    "zh": "仅时间 (14:30:00)",
                    "ko": "시간만 (14:30:00)"
                },
                "compact": {
                    "en": "Compact (YC127.01.15 14:30)",
                    "de": "Kompakt (YC127.01.15 14:30)",
                    "es": "Compacto (YC127.01.15 14:30)",
                    "fr": "Compact (YC127.01.15 14:30)",
                    "it": "Compatto (YC127.01.15 14:30)",
                    "nl": "Compact (YC127.01.15 14:30)",
                    "pl": "Kompaktowy (YC127.01.15 14:30)",
                    "pt": "Compacto (YC127.01.15 14:30)",
                    "ru": "Компактный (YC127.01.15 14:30)",
                    "ja": "コンパクト (YC127.01.15 14:30)",
                    "zh": "紧凑 (YC127.01.15 14:30)",
                    "ko": "간결 (YC127.01.15 14:30)"
                }
            }
        }
    },

    # EVE-specific data
    "eve_data": {
        "yc_epoch_year": 2003,  # Real year when YC 105 started
        "yc_epoch_value": 105,  # YC year in 2003
        "eve_gate_collapse": "YC 0",

        # Major empires
        "empires": {
            "amarr": {"name": "Amarr Empire", "capital": "Amarr Prime", "emoji": "⚜️"},
            "caldari": {"name": "Caldari State", "capital": "New Caldari", "emoji": "🏢"},
            "gallente": {"name": "Gallente Federation", "capital": "Villore", "emoji": "🗽"},
            "minmatar": {"name": "Minmatar Republic", "capital": "Pator", "emoji": "⚙️"}
        },

        # Notable events in YC timeline
        "events": {
            105: "Capsuleer program begins",
            106: "Empyrean Age",
            110: "Sansha's Nation incursions",
            111: "Arek'Jaalan Project",
            113: "Battle of Asakai",
            114: "Bloodbath of B-R5RB",
            116: "Caroline's Star",
            117: "Drifters appear",
            118: "Citadel expansion",
            119: "Lifeblood expansion",
            120: "Into the Abyss",
            122: "Invasion begins",
            124: "Pochven established",
            125: "Uprising",
            126: "Viridian",
            127: "Havoc"
        },

        # Notable systems (trade hubs)
        "systems": [
            {"name": "Jita", "region": "The Forge", "type": "Major trade hub", "emoji": "💰"},
            {"name": "Amarr", "region": "Domain", "type": "Amarr trade hub", "emoji": "⚜️"},
            {"name": "Dodixie", "region": "Sinq Laison", "type": "Gallente trade hub", "emoji": "🗽"},
            {"name": "Rens", "region": "Heimatar", "type": "Minmatar trade hub", "emoji": "⚙️"},
            {"name": "Hek", "region": "Metropolis", "type": "Regional trade center", "emoji": "🏪"}
        ],

        # Time zones (all use UTC but with lore names)
        "time_references": {
            "NEST": "New Eden Standard Time (UTC)",
            "CONCORD": "CONCORD Universal Time",
            "Capsuleer": "Capsuleer Standard Time"
        }
    },

    # Additional metadata
    "reference_url": "https://wiki.eveuniversity.org/Lore",
    "documentation_url": "https://www.eveonline.com",
    "origin": "CCP Games, Iceland",
    "created_by": "CCP Games",
    "introduced": "May 6, 2003",

    # Example format
    "example": "YC 127.01.15 14:30:00 NEST",
    "example_meaning": "Yoiul Conference year 127, January 15th, 14:30:00 New Eden Standard Time",

    # Related calendars
    "related": ["gregorian", "stardate", "scifi"],

    # Tags for searching and filtering
    "tags": [
        "scifi", "eve", "online", "gaming", "mmorpg", "space",
        "new_eden", "capsuleer", "yoiul", "concord", "nest", "ccp"
    ],

    # Special features
    "features": {
        "real_time": True,
        "utc_based": True,
        "lore_rich": True,
        "game_events": True,
        "precision": "second"
    }
}


class EveOnlineTimeSensor(AlternativeTimeSensorBase):
    """Sensor for displaying EVE Online Time (New Eden Standard Time)."""

    # Class-level update interval
    UPDATE_INTERVAL = UPDATE_INTERVAL

    def __init__(self, base_name: str, hass: HomeAssistant) -> None:
        """Initialize the EVE Online time sensor."""
        super().__init__(base_name, hass)

        # Get translated name from metadata
        calendar_name = self._translate('name', 'EVE Online Time')

        # Set sensor attributes
        self._attr_name = f"{base_name} {calendar_name}"
        self._attr_unique_id = f"{base_name}_eve_online"
        self._attr_icon = CALENDAR_INFO.get("icon", "mdi:space-station")

        # Configuration options with defaults
        config_defaults = CALENDAR_INFO.get("config_options", {})
        self._show_nest = config_defaults.get("show_nest", {}).get("default", True)
        self._show_event = config_defaults.get("show_event", {}).get("default", True)
        self._show_empire = config_defaults.get("show_empire", {}).get("default", True)
        self._show_system = config_defaults.get("show_system", {}).get("default", True)
        self._format = config_defaults.get("format", {}).get("default", "full")

        # EVE data
        self._eve_data = CALENDAR_INFO["eve_data"]

        # Initialize state
        self._state = None
        self._eve_time = {}

        # Current empire and system (rotating)
        self._current_empire_index = 0
        self._current_system_index = 0

        _LOGGER.debug(f"Initialized EVE Online Time sensor: {self._attr_name}")

    def set_options(self, options: Dict[str, Any]) -> None:
        """Set options from config flow."""
        if options:
            self._show_nest = options.get("show_nest", self._show_nest)
            self._show_event = options.get("show_event", self._show_event)
            self._show_empire = options.get("show_empire", self._show_empire)
            self._show_system = options.get("show_system", self._show_system)
            self._format = options.get("format", self._format)

            _LOGGER.debug(f"EVE sensor options updated: show_nest={self._show_nest}, "
                         f"show_event={self._show_event}, show_empire={self._show_empire}, "
                         f"show_system={self._show_system}, format={self._format}")

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes."""
        attrs = super().extra_state_attributes

        # Add EVE-specific attributes
        if self._eve_time:
            attrs.update(self._eve_time)

            # Add description in user's language
            attrs["description"] = self._translate('description')

            # Add reference
            attrs["reference"] = CALENDAR_INFO.get('reference_url', '')

            # Add configuration status
            attrs["config"] = {
                "show_nest": self._show_nest,
                "show_event": self._show_event,
                "show_empire": self._show_empire,
                "show_system": self._show_system,
                "format": self._format
            }

        return attrs

    def _calculate_eve_time(self, earth_time: datetime) -> Dict[str, Any]:
        """Calculate EVE Online Time from standard time."""

        # EVE uses UTC
        utc_time = datetime.utcnow()

        # Calculate YC year
        years_since_launch = utc_time.year - self._eve_data["yc_epoch_year"]
        yc_year = self._eve_data["yc_epoch_value"] + years_since_launch

        # Check for notable events
        event = self._eve_data["events"].get(yc_year, "")

        # Rotate through empires (changes daily)
        days_since_epoch = (utc_time - datetime(2000, 1, 1)).days
        empire_keys = list(self._eve_data["empires"].keys())
        empire_index = days_since_epoch % len(empire_keys)
        current_empire_key = empire_keys[empire_index]
        current_empire = self._eve_data["empires"][current_empire_key]

        # Rotate through trade hubs (changes hourly)
        hours_since_epoch = days_since_epoch * 24 + utc_time.hour
        system_index = hours_since_epoch % len(self._eve_data["systems"])
        current_system = self._eve_data["systems"][system_index]

        # Format time based on configuration
        if self._format == "date":
            formatted = f"YC {yc_year}.{utc_time.month:02d}.{utc_time.day:02d}"
        elif self._format == "time":
            formatted = f"{utc_time.hour:02d}:{utc_time.minute:02d}:{utc_time.second:02d}"
        elif self._format == "compact":
            formatted = f"YC{yc_year}.{utc_time.month:02d}.{utc_time.day:02d} {utc_time.hour:02d}:{utc_time.minute:02d}"
        else:  # full
            formatted = f"YC {yc_year}.{utc_time.month:02d}.{utc_time.day:02d} {utc_time.hour:02d}:{utc_time.minute:02d}:{utc_time.second:02d}"

        if self._show_nest and self._format != "time":
            formatted += " NEST"

        # Build result
        result = {
            "yc_year": yc_year,
            "month": utc_time.month,
            "day": utc_time.day,
            "hour": utc_time.hour,
            "minute": utc_time.minute,
            "second": utc_time.second,
            "nest_time": f"{utc_time.hour:02d}:{utc_time.minute:02d}:{utc_time.second:02d}",
            "date_yc": f"YC {yc_year}.{utc_time.month:02d}.{utc_time.day:02d}",
            "utc_time": utc_time.strftime("%Y-%m-%d %H:%M:%S UTC"),
            "formatted": formatted
        }

        # Add optional data
        if self._show_event and event:
            result["notable_event"] = f"📅 {event}"

        if self._show_empire:
            result["empire_focus"] = f"{current_empire['emoji']} {current_empire['name']}"
            result["empire_capital"] = current_empire['capital']

        if self._show_system:
            result["trade_hub"] = f"{current_system['emoji']} {current_system['name']}"
            result["hub_region"] = current_system['region']
            result["hub_type"] = current_system['type']

        # Add CONCORD status (changes based on time)
        concord_status = self._get_concord_status(utc_time.hour)
        result["concord_status"] = concord_status

        # Add downtime warning (daily at 11:00 UTC)
        if utc_time.hour == 10 and utc_time.minute >= 30:
            result["downtime_warning"] = "⚠️ Daily downtime in 30 minutes!"
        elif utc_time.hour == 11 and utc_time.minute < 15:
            result["downtime_active"] = "🔧 Daily downtime in progress"

        return result

    def _get_concord_status(self, hour: int) -> str:
        """Get CONCORD status based on time."""
        if 0 <= hour < 6:
            return "🌙 CONCORD: Night shift patrols"
        elif 6 <= hour < 12:
            return "☀️ CONCORD: Morning operations"
        elif 12 <= hour < 18:
            return "🛡️ CONCORD: Peak security hours"
        elif 18 <= hour < 21:
            return "🌆 CONCORD: Evening patrols"
        else:
            return "⭐ CONCORD: Late shift active"

    def update(self) -> None:
        """Update the sensor."""
        now = datetime.now()
        self._eve_time = self._calculate_eve_time(now)

        # Set state to formatted EVE time
        self._state = self._eve_time["formatted"]

        _LOGGER.debug(f"Updated EVE Online Time to {self._state}")
