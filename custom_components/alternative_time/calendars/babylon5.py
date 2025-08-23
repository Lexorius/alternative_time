"""Babylon 5 Calendar implementation - Version 2.5.1.0."""
from __future__ import annotations

from datetime import datetime
import logging
from typing import Dict, Any, Optional

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
    "id": "babylon5",
    "version": "2.5.1.0",
    "icon": "mdi:space-station",
    "category": "scifi",
    "accuracy": "fictional",
    "update_interval": UPDATE_INTERVAL,
    
    # Multi-language names
    "name": {
        "en": "Babylon 5 Station Time",
        "de": "Babylon 5 Stationszeit",
        "es": "Hora de la Estación Babylon 5",
        "fr": "Heure de la Station Babylon 5",
        "it": "Ora della Stazione Babylon 5",
        "nl": "Babylon 5 Station Tijd",
        "pl": "Czas Stacji Babylon 5",
        "pt": "Hora da Estação Babylon 5",
        "ru": "Время станции Вавилон 5",
        "ja": "バビロン5ステーション時間",
        "zh": "巴比伦5号站时间",
        "ko": "바빌론 5 스테이션 시간"
    },
    
    # Short descriptions for UI
    "description": {
        "en": "Earth Alliance Standard Time from Babylon 5 universe with station events",
        "de": "Erdallianz-Standardzeit aus dem Babylon 5 Universum mit Stationsereignissen",
        "es": "Hora Estándar de la Alianza Terrestre del universo Babylon 5 con eventos de la estación",
        "fr": "Heure Standard de l'Alliance Terrienne de l'univers Babylon 5 avec événements de la station",
        "it": "Ora Standard dell'Alleanza Terrestre dall'universo Babylon 5 con eventi della stazione",
        "nl": "Aarde Alliantie Standaard Tijd uit het Babylon 5 universum met station gebeurtenissen",
        "pl": "Standardowy Czas Sojuszu Ziemi z uniwersum Babylon 5 z wydarzeniami stacji",
        "pt": "Hora Padrão da Aliança da Terra do universo Babylon 5 com eventos da estação",
        "ru": "Стандартное время Земного Альянса из вселенной Вавилон 5 с событиями станции",
        "ja": "バビロン5宇宙の地球同盟標準時とステーションイベント",
        "zh": "巴比伦5宇宙地球联盟标准时间及站点事件",
        "ko": "바빌론 5 우주의 지구 동맹 표준시와 스테이션 이벤트"
    },
    
    # Detailed information for documentation
    "detailed_info": {
        "en": {
            "overview": "Babylon 5 uses Earth Alliance Standard Time, based on Earth's 24-hour day",
            "station": "The last of the Babylon stations, a five-mile long diplomatic station",
            "location": "Located in neutral space at the L5 point between Epsilon III and its moon",
            "purpose": "A port of call for refugees, smugglers, businessmen, diplomats, and travelers",
            "year": "The year 2258 marks the beginning of the series",
            "races": "Home to humans, Minbari, Centauri, Narn, Vorlons, and many others",
            "sectors": "Divided into colored sectors: Blue (command), Red (commercial), Green (diplomatic), Brown (industrial), Gray (undeveloped)",
            "motto": "Our last, best hope for peace"
        },
        "de": {
            "overview": "Babylon 5 verwendet die Erdallianz-Standardzeit, basierend auf dem 24-Stunden-Tag der Erde",
            "station": "Die letzte der Babylon-Stationen, eine fünf Meilen lange diplomatische Station",
            "location": "Befindet sich im neutralen Raum am L5-Punkt zwischen Epsilon III und seinem Mond",
            "purpose": "Ein Anlaufpunkt für Flüchtlinge, Schmuggler, Geschäftsleute, Diplomaten und Reisende",
            "year": "Das Jahr 2258 markiert den Beginn der Serie",
            "races": "Heimat für Menschen, Minbari, Centauri, Narn, Vorlonen und viele andere",
            "sectors": "Unterteilt in farbige Sektoren: Blau (Kommando), Rot (Kommerziell), Grün (Diplomatisch), Braun (Industriell), Grau (Unerschlossen)",
            "motto": "Unsere letzte, beste Hoffnung auf Frieden"
        }
    },
    
    # Configuration options
    "config_options": {
        "show_sector": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show Station Sector",
                "de": "Stationssektor anzeigen",
                "es": "Mostrar sector de la estación",
                "fr": "Afficher le secteur de la station",
                "it": "Mostra settore della stazione",
                "nl": "Toon station sector",
                "pl": "Pokaż sektor stacji",
                "pt": "Mostrar setor da estação",
                "ru": "Показать сектор станции",
                "ja": "ステーションセクターを表示",
                "zh": "显示站点扇区",
                "ko": "스테이션 섹터 표시"
            },
            "description": {
                "en": "Display current station sector (Blue, Red, Green, Brown, Gray)",
                "de": "Aktuellen Stationssektor anzeigen (Blau, Rot, Grün, Braun, Grau)",
                "es": "Mostrar sector actual de la estación (Azul, Rojo, Verde, Marrón, Gris)",
                "fr": "Afficher le secteur actuel de la station (Bleu, Rouge, Vert, Brun, Gris)",
                "it": "Mostra settore attuale della stazione (Blu, Rosso, Verde, Marrone, Grigio)",
                "nl": "Toon huidige station sector (Blauw, Rood, Groen, Bruin, Grijs)",
                "pl": "Pokaż aktualny sektor stacji (Niebieski, Czerwony, Zielony, Brązowy, Szary)",
                "pt": "Mostrar setor atual da estação (Azul, Vermelho, Verde, Marrom, Cinza)",
                "ru": "Показать текущий сектор станции (Синий, Красный, Зеленый, Коричневый, Серый)",
                "ja": "現在のステーションセクターを表示（青、赤、緑、茶、灰）",
                "zh": "显示当前站点扇区（蓝、红、绿、棕、灰）",
                "ko": "현재 스테이션 섹터 표시 (파랑, 빨강, 초록, 갈색, 회색)"
            }
        },
        "show_race": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show Ambassador Race",
                "de": "Botschafter-Rasse anzeigen",
                "es": "Mostrar raza del embajador",
                "fr": "Afficher la race de l'ambassadeur",
                "it": "Mostra razza dell'ambasciatore",
                "nl": "Toon ambassadeur ras",
                "pl": "Pokaż rasę ambasadora",
                "pt": "Mostrar raça do embaixador",
                "ru": "Показать расу посла",
                "ja": "大使の種族を表示",
                "zh": "显示大使种族",
                "ko": "대사 종족 표시"
            },
            "description": {
                "en": "Display current ambassador on duty (Delenn, G'Kar, Londo, Kosh)",
                "de": "Aktuellen diensthabenden Botschafter anzeigen (Delenn, G'Kar, Londo, Kosh)",
                "es": "Mostrar embajador de turno actual (Delenn, G'Kar, Londo, Kosh)",
                "fr": "Afficher l'ambassadeur de service actuel (Delenn, G'Kar, Londo, Kosh)",
                "it": "Mostra ambasciatore di turno attuale (Delenn, G'Kar, Londo, Kosh)",
                "nl": "Toon huidige dienstdoende ambassadeur (Delenn, G'Kar, Londo, Kosh)",
                "pl": "Pokaż aktualnego dyżurnego ambasadora (Delenn, G'Kar, Londo, Kosh)",
                "pt": "Mostrar embaixador de plantão atual (Delenn, G'Kar, Londo, Kosh)",
                "ru": "Показать текущего дежурного посла (Деленн, Г'Кар, Лондо, Кош)",
                "ja": "現在の当直大使を表示（デレン、ガカール、ロンド、コッシュ）",
                "zh": "显示当前值班大使（德伦、贾卡、朗多、科什）",
                "ko": "현재 근무 중인 대사 표시 (델렌, 지카르, 론도, 코쉬)"
            }
        },
        "show_events": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show Station Events",
                "de": "Stationsereignisse anzeigen",
                "es": "Mostrar eventos de la estación",
                "fr": "Afficher les événements de la station",
                "it": "Mostra eventi della stazione",
                "nl": "Toon station gebeurtenissen",
                "pl": "Pokaż wydarzenia stacji",
                "pt": "Mostrar eventos da estação",
                "ru": "Показать события станции",
                "ja": "ステーションイベントを表示",
                "zh": "显示站点事件",
                "ko": "스테이션 이벤트 표시"
            },
            "description": {
                "en": "Display historical events from the series timeline",
                "de": "Historische Ereignisse aus der Serien-Zeitlinie anzeigen",
                "es": "Mostrar eventos históricos de la línea temporal de la serie",
                "fr": "Afficher les événements historiques de la chronologie de la série",
                "it": "Mostra eventi storici dalla linea temporale della serie",
                "nl": "Toon historische gebeurtenissen uit de serie tijdlijn",
                "pl": "Pokaż wydarzenia historyczne z osi czasu serialu",
                "pt": "Mostrar eventos históricos da linha do tempo da série",
                "ru": "Показать исторические события из временной линии сериала",
                "ja": "シリーズのタイムラインから歴史的イベントを表示",
                "zh": "显示系列时间线中的历史事件",
                "ko": "시리즈 타임라인의 역사적 사건 표시"
            }
        },
        "year_offset": {
            "type": "select",
            "default": "2258",
            "options": ["2258", "2259", "2260", "2261", "2262"],
            "label": {
                "en": "Station Year",
                "de": "Stationsjahr",
                "es": "Año de la estación",
                "fr": "Année de la station",
                "it": "Anno della stazione",
                "nl": "Station jaar",
                "pl": "Rok stacji",
                "pt": "Ano da estação",
                "ru": "Год станции",
                "ja": "ステーション年",
                "zh": "站点年份",
                "ko": "스테이션 연도"
            },
            "description": {
                "en": "Select which year of the series to display",
                "de": "Wähle welches Jahr der Serie angezeigt werden soll",
                "es": "Selecciona qué año de la serie mostrar",
                "fr": "Sélectionnez quelle année de la série afficher",
                "it": "Seleziona quale anno della serie visualizzare",
                "nl": "Selecteer welk jaar van de serie weer te geven",
                "pl": "Wybierz, który rok serialu wyświetlić",
                "pt": "Selecione qual ano da série exibir",
                "ru": "Выберите какой год сериала отображать",
                "ja": "表示するシリーズの年を選択",
                "zh": "选择要显示的系列年份",
                "ko": "표시할 시리즈 연도 선택"
            },
            "options_label": {
                "2258": {
                    "en": "2258 - Season 1: Signs and Portents",
                    "de": "2258 - Staffel 1: Zeichen und Wunder",
                    "es": "2258 - Temporada 1: Señales y Portentos",
                    "fr": "2258 - Saison 1: Signes et Présages",
                    "it": "2258 - Stagione 1: Segni e Portenti",
                    "nl": "2258 - Seizoen 1: Tekenen en Voortekenen",
                    "pl": "2258 - Sezon 1: Znaki i Zapowiedzi",
                    "pt": "2258 - Temporada 1: Sinais e Portentos",
                    "ru": "2258 - Сезон 1: Знаки и Предзнаменования",
                    "ja": "2258 - シーズン1：兆候と前兆",
                    "zh": "2258 - 第1季：征兆与预兆",
                    "ko": "2258 - 시즌 1: 징조와 전조"
                },
                "2259": {
                    "en": "2259 - Season 2: The Coming of Shadows",
                    "de": "2259 - Staffel 2: Das Kommen der Schatten",
                    "es": "2259 - Temporada 2: La Llegada de las Sombras",
                    "fr": "2259 - Saison 2: L'Arrivée des Ombres",
                    "it": "2259 - Stagione 2: L'Arrivo delle Ombre",
                    "nl": "2259 - Seizoen 2: De Komst van de Schaduwen",
                    "pl": "2259 - Sezon 2: Nadejście Cieni",
                    "pt": "2259 - Temporada 2: A Chegada das Sombras",
                    "ru": "2259 - Сезон 2: Приход Теней",
                    "ja": "2259 - シーズン2：影の到来",
                    "zh": "2259 - 第2季：暗影降临",
                    "ko": "2259 - 시즌 2: 그림자의 도래"
                },
                "2260": {
                    "en": "2260 - Season 3: Point of No Return",
                    "de": "2260 - Staffel 3: Kein Zurück",
                    "es": "2260 - Temporada 3: Punto Sin Retorno",
                    "fr": "2260 - Saison 3: Point de Non-Retour",
                    "it": "2260 - Stagione 3: Punto di Non Ritorno",
                    "nl": "2260 - Seizoen 3: Punt van Geen Terugkeer",
                    "pl": "2260 - Sezon 3: Punkt Bez Powrotu",
                    "pt": "2260 - Temporada 3: Ponto Sem Retorno",
                    "ru": "2260 - Сезон 3: Точка Невозврата",
                    "ja": "2260 - シーズン3：帰還不能点",
                    "zh": "2260 - 第3季：不归点",
                    "ko": "2260 - 시즌 3: 돌아올 수 없는 지점"
                },
                "2261": {
                    "en": "2261 - Season 4: No Surrender, No Retreat",
                    "de": "2261 - Staffel 4: Keine Kapitulation, Kein Rückzug",
                    "es": "2261 - Temporada 4: Sin Rendición, Sin Retirada",
                    "fr": "2261 - Saison 4: Pas de Reddition, Pas de Retraite",
                    "it": "2261 - Stagione 4: Nessuna Resa, Nessuna Ritirata",
                    "nl": "2261 - Seizoen 4: Geen Overgave, Geen Terugtocht",
                    "pl": "2261 - Sezon 4: Bez Kapitulacji, Bez Odwrotu",
                    "pt": "2261 - Temporada 4: Sem Rendição, Sem Recuo",
                    "ru": "2261 - Сезон 4: Не Сдаваться, Не Отступать",
                    "ja": "2261 - シーズン4：降伏なし、撤退なし",
                    "zh": "2261 - 第4季：绝不投降，绝不撤退",
                    "ko": "2261 - 시즌 4: 항복 없음, 후퇴 없음"
                },
                "2262": {
                    "en": "2262 - Season 5: The Wheel of Fire",
                    "de": "2262 - Staffel 5: Das Rad des Feuers",
                    "es": "2262 - Temporada 5: La Rueda de Fuego",
                    "fr": "2262 - Saison 5: La Roue de Feu",
                    "it": "2262 - Stagione 5: La Ruota di Fuoco",
                    "nl": "2262 - Seizoen 5: Het Wiel van Vuur",
                    "pl": "2262 - Sezon 5: Koło Ognia",
                    "pt": "2262 - Temporada 5: A Roda de Fogo",
                    "ru": "2262 - Сезон 5: Колесо Огня",
                    "ja": "2262 - シーズン5：火の輪",
                    "zh": "2262 - 第5季：火之轮",
                    "ko": "2262 - 시즌 5: 불의 바퀴"
                }
            }
        }
    },
    
    # Babylon 5 specific data
    "babylon5_data": {
        # Station sectors
        "sectors": [
            {"name": "Blue Sector", "purpose": "Command & Control", "emoji": "🔵"},
            {"name": "Red Sector", "purpose": "Commercial District", "emoji": "🔴"},
            {"name": "Green Sector", "purpose": "Diplomatic Quarter", "emoji": "🟢"},
            {"name": "Brown Sector", "purpose": "Industrial Zone", "emoji": "🟤"},
            {"name": "Gray Sector", "purpose": "Undeveloped Areas", "emoji": "⚫"},
            {"name": "Downbelow", "purpose": "Undercity", "emoji": "⬇️"}
        ],
        
        # Major races and ambassadors
        "ambassadors": [
            {"race": "Minbari", "name": "Delenn", "emoji": "🔷"},
            {"race": "Narn", "name": "G'Kar", "emoji": "🟠"},
            {"race": "Centauri", "name": "Londo Mollari", "emoji": "🟣"},
            {"race": "Vorlon", "name": "Kosh", "emoji": "⚪"},
            {"race": "Human", "name": "John Sheridan", "emoji": "🔵"}
        ],
        
        # Important locations
        "locations": {
            "C&C": "Command & Control",
            "Zocalo": "Main marketplace",
            "Garden": "Rotating garden section",
            "Medlab": "Medical facility",
            "Cobra Bay": "Docking area",
            "Core Shuttle": "Transport system"
        },
        
        # Station events by year
        "events": {
            2258: {
                1: "Sinclair assumes command",
                3: "Deathwalker arrives",
                6: "Babylon 4 reappears",
                9: "President Santiago assassinated",
                12: "Battle of the Line truth revealed"
            },
            2259: {
                1: "Sheridan takes command",
                4: "Shadow War begins",
                8: "Narn-Centauri War",
                11: "Rangers revealed",
                12: "Shadows return"
            },
            2260: {
                2: "Army of Light forms",
                5: "Severed Dreams",
                8: "Z'ha'dum mission",
                10: "Vorlons leave",
                12: "Shadow War ends"
            },
            2261: {
                3: "Earth Civil War",
                6: "Mars rebellion",
                9: "Liberation of Earth",
                11: "Interstellar Alliance formed",
                12: "Sheridan becomes President"
            },
            2262: {
                2: "Telepath crisis",
                5: "Centauri Prime falls",
                8: "Drakh plague",
                10: "Rangers expand",
                12: "Babylon 5 decommissioned"
            }
        },
        
        # Quotes
        "quotes": [
            "The Babylon Project was our last, best hope for peace.",
            "Who are you? What do you want?",
            "Understanding is a three-edged sword.",
            "No one here is exactly what he appears.",
            "The avalanche has already started. It is too late for the pebbles to vote.",
            "We are star stuff. We are the universe made manifest.",
            "Faith manages.",
            "In fire, there is cleansing."
        ]
    },
    
    # Additional metadata
    "reference_url": "https://babylon5.fandom.com/wiki/Babylon_5",
    "documentation_url": "https://www.imdb.com/title/tt0105946/",
    "origin": "Babylon 5 (J. Michael Straczynski)",
    "created_by": "J. Michael Straczynski",
    "introduced": "Babylon 5 (1993-1998)",
    
    # Example format
    "example": "2260.045 14:30:00 EST",
    "example_meaning": "Year 2260, day 45, 14:30:00 Earth Standard Time",
    
    # Related calendars
    "related": ["stardate", "eve", "scifi"],
    
    # Tags for searching and filtering
    "tags": [
        "scifi", "babylon5", "space_station", "earth_alliance", "shadows",
        "vorlons", "minbari", "centauri", "narn", "rangers", "jms"
    ],
    
    # Special features
    "features": {
        "station_sectors": True,
        "ambassador_rotation": True,
        "historical_events": True,
        "quotes": True,
        "precision": "day"
    }
}


class Babylon5CalendarSensor(AlternativeTimeSensorBase):
    """Sensor for displaying Babylon 5 Station Time."""
    
    # Class-level update interval
    UPDATE_INTERVAL = UPDATE_INTERVAL
    
    def __init__(self, base_name: str, hass: HomeAssistant) -> None:
        """Initialize the Babylon 5 calendar sensor."""
        super().__init__(base_name, hass)
        
        # Get translated name from metadata
        calendar_name = self._translate('name', 'Babylon 5 Station Time')
        
        # Set sensor attributes
        self._attr_name = f"{base_name} {calendar_name}"
        self._attr_unique_id = f"{base_name}_babylon5"
        self._attr_icon = CALENDAR_INFO.get("icon", "mdi:space-station")
        
        # Configuration options with defaults
        config_defaults = CALENDAR_INFO.get("config_options", {})
        self._show_sector = config_defaults.get("show_sector", {}).get("default", True)
        self._show_race = config_defaults.get("show_race", {}).get("default", True)
        self._show_events = config_defaults.get("show_events", {}).get("default", True)
        self._year_offset = int(config_defaults.get("year_offset", {}).get("default", "2258"))
        
        # Babylon 5 data
        self._b5_data = CALENDAR_INFO["babylon5_data"]
        
        # Initialize state
        self._state = None
        self._b5_time = {}
        
        # Rotation indices
        self._sector_index = 0
        self._ambassador_index = 0
        self._quote_index = 0
        
        _LOGGER.debug(f"Initialized Babylon 5 sensor: {self._attr_name}")
    
    def set_options(self, options: Dict[str, Any]) -> None:
        """Set options from config flow."""
        if options:
            self._show_sector = options.get("show_sector", self._show_sector)
            self._show_race = options.get("show_race", self._show_race)
            self._show_events = options.get("show_events", self._show_events)
            self._year_offset = int(options.get("year_offset", str(self._year_offset)))
            
            _LOGGER.debug(f"Babylon 5 sensor options updated: show_sector={self._show_sector}, "
                         f"show_race={self._show_race}, show_events={self._show_events}, "
                         f"year_offset={self._year_offset}")
    
    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes."""
        attrs = super().extra_state_attributes
        
        # Add Babylon 5 specific attributes
        if self._b5_time:
            attrs.update(self._b5_time)
            
            # Add description in user's language
            attrs["description"] = self._translate('description')
            
            # Add reference
            attrs["reference"] = CALENDAR_INFO.get('reference_url', '')
            
            # Add configuration status
            attrs["config"] = {
                "show_sector": self._show_sector,
                "show_race": self._show_race,
                "show_events": self._show_events,
                "year_offset": self._year_offset
            }
        
        return attrs
    
    def _get_station_event(self, month: int) -> str:
        """Get station event for the current month."""
        if not self._show_events:
            return ""
        
        events = self._b5_data["events"].get(self._year_offset, {})
        return events.get(month, "")
    
    def _get_daily_quote(self) -> str:
        """Get daily rotating quote."""
        quote = self._b5_data["quotes"][self._quote_index]
        self._quote_index = (self._quote_index + 1) % len(self._b5_data["quotes"])
        return quote
    
    def _calculate_b5_time(self, earth_date: datetime) -> Dict[str, Any]:
        """Calculate Babylon 5 time from Earth date."""
        
        # Calculate Babylon 5 year (offset from current year)
        current_year = earth_date.year
        years_since_2000 = current_year - 2000
        b5_year = self._year_offset
        
        # Calculate day of year
        day_of_year = earth_date.timetuple().tm_yday
        
        # Get current sector (rotates every 4 hours)
        if self._show_sector:
            sector_index = (earth_date.hour // 4) % len(self._b5_data["sectors"])
            current_sector = self._b5_data["sectors"][sector_index]
        else:
            current_sector = None
        
        # Get current ambassador (rotates daily)
        if self._show_race:
            days_since_epoch = (earth_date - datetime(2000, 1, 1)).days
            ambassador_index = days_since_epoch % len(self._b5_data["ambassadors"])
            current_ambassador = self._b5_data["ambassadors"][ambassador_index]
        else:
            current_ambassador = None
        
        # Get station event
        event = self._get_station_event(earth_date.month)
        
        # Get daily quote
        quote = self._get_daily_quote()
        
        # Determine shift
        hour = earth_date.hour
        if 6 <= hour < 14:
            shift = "Alpha Shift"
            shift_emoji = "☀️"
        elif 14 <= hour < 22:
            shift = "Beta Shift"
            shift_emoji = "🌤️"
        else:
            shift = "Gamma Shift"
            shift_emoji = "🌙"
        
        # Format time
        formatted_time = f"{b5_year}.{day_of_year:03d} {earth_date.hour:02d}:{earth_date.minute:02d}:{earth_date.second:02d} EST"
        
        # Build result
        result = {
            "year": b5_year,
            "day_of_year": day_of_year,
            "hour": earth_date.hour,
            "minute": earth_date.minute,
            "second": earth_date.second,
            "shift": f"{shift_emoji} {shift}",
            "earth_date": earth_date.strftime("%Y-%m-%d"),
            "formatted": formatted_time,
            "quote": f"📜 {quote}"
        }
        
        # Add season subtitle based on year
        season_titles = {
            2258: "Signs and Portents",
            2259: "The Coming of Shadows",
            2260: "Point of No Return",
            2261: "No Surrender, No Retreat",
            2262: "The Wheel of Fire"
        }
        result["season"] = season_titles.get(b5_year, "Unknown")
        
        # Add optional data
        if current_sector:
            result["sector"] = f"{current_sector['emoji']} {current_sector['name']}"
            result["sector_purpose"] = current_sector['purpose']
        
        if current_ambassador:
            result["ambassador"] = f"{current_ambassador['emoji']} {current_ambassador['name']}"
            result["ambassador_race"] = current_ambassador['race']
        
        if event:
            result["station_event"] = f"📅 {event}"
        
        # Add station status
        if earth_date.hour == 0 and earth_date.minute < 5:
            result["station_status"] = "🔧 Daily maintenance cycle"
        elif 7 <= earth_date.hour < 8:
            result["station_status"] = "📢 Morning announcements"
        elif earth_date.hour == 12:
            result["station_status"] = "🍽️ Midday break"
        elif earth_date.hour == 18:
            result["station_status"] = "👥 Council meeting time"
        else:
            result["station_status"] = "✅ Normal operations"
        
        return result
    
    def update(self) -> None:
        """Update the sensor."""
        now = datetime.now()
        self._b5_time = self._calculate_b5_time(now)
        
        # Set state to formatted time
        self._state = self._b5_time["formatted"]
        
        _LOGGER.debug(f"Updated Babylon 5 time to {self._state}")
