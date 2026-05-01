"""Discworld Calendar (Terry Pratchett) implementation - Version 3.0."""
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
    "id": "discworld",
    "version": "3.0.0",
    "icon": "mdi:turtle",
    "category": "fantasy",
    "accuracy": "fictional",
    "update_interval": UPDATE_INTERVAL,

    # Multi-language names
    "name": {
        "en": "Discworld Calendar",
        "de": "Scheibenwelt-Kalender",
        "es": "Calendario del Mundodisco",
        "fr": "Calendrier du Disque-Monde",
        "it": "Calendario del Mondo Disco",
        "nl": "Schijfwereld Kalender",
        "pl": "Kalendarz Świata Dysku",
        "pt": "Calendário do Discworld",
        "ru": "Календарь Плоского мира",
        "ja": "ディスクワールド暦",
        "zh": "碟形世界历",
        "ko": "디스크월드 달력"
    },

    # Short descriptions for UI
    "description": {
        "en": "Terry Pratchett's Discworld calendar with 8-day weeks, guild influences, and Death appearances",
        "de": "Terry Pratchetts Scheibenwelt-Kalender mit 8-Tage-Wochen, Gildeneinflüssen und Tod-Auftritten",
        "es": "Calendario del Mundodisco de Terry Pratchett con semanas de 8 días, influencias gremiales y apariciones de la Muerte",
        "fr": "Calendrier du Disque-Monde de Terry Pratchett avec semaines de 8 jours, influences des guildes et apparitions de la Mort",
        "it": "Calendario del Mondo Disco di Terry Pratchett con settimane di 8 giorni, influenze delle gilde e apparizioni della Morte",
        "nl": "Terry Pratchett's Schijfwereld kalender met 8-daagse weken, gilde-invloeden en Dood verschijningen",
        "pl": "Kalendarz Świata Dysku Terry'ego Pratchetta z 8-dniowymi tygodniami, wpływami gildii i pojawieniami się Śmierci",
        "pt": "Calendário do Discworld de Terry Pratchett com semanas de 8 dias, influências das guildas e aparições da Morte",
        "ru": "Календарь Плоского мира Терри Пратчетта с 8-дневными неделями, влиянием гильдий и появлениями Смерти",
        "ja": "テリー・プラチェットのディスクワールド暦、8日週、ギルドの影響、死神の出現",
        "zh": "特里·普拉切特的碟形世界历，8天周、公会影响和死神出现",
        "ko": "테리 프래쳇의 디스크월드 달력, 8일 주, 길드 영향 및 죽음의 출현"
    },

    # Detailed information for documentation
    "detailed_info": {
        "en": {
            "overview": "The Discworld calendar is used on Terry Pratchett's fictional Disc, carried by four elephants on the Great A'Tuin",
            "structure": "13 months with varying days, 8-day weeks including Octeday",
            "year": "The year is divided into common months plus the special Century of the Fruitbat",
            "weeks": "8-day weeks: Sunday through Saturday plus Octeday",
            "guilds": "Each day is influenced by different Ankh-Morpork guilds",
            "events": "Includes Hogswatchday (like Christmas), Soul Cake Night (Halloween), and other festivals",
            "humor": "Contains impossible dates like the 32nd of December as Pratchett humor",
            "death": "Death (THE ANTHROPOMORPHIC PERSONIFICATION) makes regular appearances"
        },
        "de": {
            "overview": "Der Scheibenwelt-Kalender wird auf Terry Pratchetts fiktiver Scheibe verwendet, getragen von vier Elefanten auf der Großen A'Tuin",
            "structure": "13 Monate mit unterschiedlichen Tagen, 8-Tage-Wochen einschließlich Okttag",
            "year": "Das Jahr ist in gewöhnliche Monate plus das besondere Jahrhundert der Flughunde unterteilt",
            "weeks": "8-Tage-Wochen: Sonntag bis Samstag plus Okttag",
            "guilds": "Jeder Tag wird von verschiedenen Ankh-Morpork-Gilden beeinflusst",
            "events": "Beinhaltet Schweinswacht (wie Weihnachten), Seelenkuchennacht (Halloween) und andere Feste",
            "humor": "Enthält unmögliche Daten wie den 32. Dezember als Pratchett-Humor",
            "death": "Tod (DIE ANTHROPOMORPHE PERSONIFIKATION) erscheint regelmäßig"
        }
    },

    # Configuration options
    "config_options": {
        "show_death_quotes": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show Death Quotes",
                "de": "Tod-Zitate anzeigen",
                "es": "Mostrar citas de la Muerte",
                "fr": "Afficher les citations de la Mort",
                "it": "Mostra citazioni della Morte",
                "nl": "Toon Dood citaten",
                "pl": "Pokaż cytaty Śmierci",
                "pt": "Mostrar citações da Morte",
                "ru": "Показать цитаты Смерти",
                "ja": "死神の引用を表示",
                "zh": "显示死神语录",
                "ko": "죽음의 인용문 표시"
            },
            "description": {
                "en": "Display Death's daily wisdom at midnight (IN SMALL CAPS)",
                "de": "Zeige Tods tägliche Weisheit um Mitternacht (IN KAPITÄLCHEN)",
                "es": "Mostrar la sabiduría diaria de la Muerte a medianoche (EN VERSALITAS)",
                "fr": "Afficher la sagesse quotidienne de la Mort à minuit (EN PETITES MAJUSCULES)",
                "it": "Mostra la saggezza quotidiana della Morte a mezzanotte (IN MAIUSCOLETTO)",
                "nl": "Toon Dood's dagelijkse wijsheid om middernacht (IN KLEINE HOOFDLETTERS)",
                "pl": "Pokaż codzienną mądrość Śmierci o północy (MAŁYMI LITERAMI)",
                "pt": "Mostrar sabedoria diária da Morte à meia-noite (EM VERSALETE)",
                "ru": "Показать ежедневную мудрость Смерти в полночь (КАПИТЕЛЬЮ)",
                "ja": "真夜中に死神の日々の知恵を表示（小文字で）",
                "zh": "午夜显示死神的每日智慧（小型大写字母）",
                "ko": "자정에 죽음의 일일 지혜 표시 (작은 대문자로)"
            }
        },
        "show_guild": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show Guild Influence",
                "de": "Gildeneinfluss anzeigen",
                "es": "Mostrar influencia gremial",
                "fr": "Afficher l'influence des guildes",
                "it": "Mostra influenza delle gilde",
                "nl": "Toon gilde invloed",
                "pl": "Pokaż wpływ gildii",
                "pt": "Mostrar influência das guildas",
                "ru": "Показать влияние гильдий",
                "ja": "ギルドの影響を表示",
                "zh": "显示公会影响",
                "ko": "길드 영향 표시"
            },
            "description": {
                "en": "Display which Ankh-Morpork guild influences the day",
                "de": "Zeige welche Ankh-Morpork-Gilde den Tag beeinflusst",
                "es": "Mostrar qué gremio de Ankh-Morpork influye en el día",
                "fr": "Afficher quelle guilde d'Ankh-Morpork influence la journée",
                "it": "Mostra quale gilda di Ankh-Morpork influenza il giorno",
                "nl": "Toon welke Ankh-Morpork gilde de dag beïnvloedt",
                "pl": "Pokaż, która gildia Ankh-Morpork wpływa na dzień",
                "pt": "Mostrar qual guilda de Ankh-Morpork influencia o dia",
                "ru": "Показать, какая гильдия Анк-Морпорка влияет на день",
                "ja": "アンク・モルポークのどのギルドが日に影響を与えるかを表示",
                "zh": "显示哪个安克-莫波克公会影响当天",
                "ko": "앙크-모르포크의 어느 길드가 그날에 영향을 미치는지 표시"
            }
        },
        "show_location": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show City Location",
                "de": "Stadtort anzeigen",
                "es": "Mostrar ubicación de la ciudad",
                "fr": "Afficher l'emplacement de la ville",
                "it": "Mostra posizione della città",
                "nl": "Toon stadslocatie",
                "pl": "Pokaż lokalizację miasta",
                "pt": "Mostrar localização da cidade",
                "ru": "Показать местоположение в городе",
                "ja": "都市の場所を表示",
                "zh": "显示城市位置",
                "ko": "도시 위치 표시"
            },
            "description": {
                "en": "Display current location in Ankh-Morpork",
                "de": "Zeige aktuellen Standort in Ankh-Morpork",
                "es": "Mostrar ubicación actual en Ankh-Morpork",
                "fr": "Afficher l'emplacement actuel à Ankh-Morpork",
                "it": "Mostra posizione attuale ad Ankh-Morpork",
                "nl": "Toon huidige locatie in Ankh-Morpork",
                "pl": "Pokaż aktualną lokalizację w Ankh-Morpork",
                "pt": "Mostrar localização atual em Ankh-Morpork",
                "ru": "Показать текущее местоположение в Анк-Морпорке",
                "ja": "アンク・モルポークの現在地を表示",
                "zh": "显示在安克-莫波克的当前位置",
                "ko": "앙크-모르포크의 현재 위치 표시"
            }
        },
        "detect_l_space": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Detect L-Space",
                "de": "L-Raum erkennen",
                "es": "Detectar Espacio-L",
                "fr": "Détecter l'Espace-L",
                "it": "Rileva Spazio-L",
                "nl": "Detecteer L-Ruimte",
                "pl": "Wykryj Przestrzeń-L",
                "pt": "Detectar Espaço-L",
                "ru": "Обнаружить L-пространство",
                "ja": "L空間を検出",
                "zh": "检测L空间",
                "ko": "L-공간 감지"
            },
            "description": {
                "en": "Detect L-Space anomalies at 3:33 (Library Space connections)",
                "de": "Erkenne L-Raum-Anomalien um 3:33 (Bibliotheksraum-Verbindungen)",
                "es": "Detectar anomalías del Espacio-L a las 3:33 (conexiones del Espacio Biblioteca)",
                "fr": "Détecter les anomalies de l'Espace-L à 3:33 (connexions de l'Espace Bibliothèque)",
                "it": "Rileva anomalie dello Spazio-L alle 3:33 (connessioni Spazio Biblioteca)",
                "nl": "Detecteer L-Ruimte anomalieën om 3:33 (Bibliotheekruimte verbindingen)",
                "pl": "Wykryj anomalie Przestrzeni-L o 3:33 (połączenia Przestrzeni Bibliotecznej)",
                "pt": "Detectar anomalias do Espaço-L às 3:33 (conexões do Espaço Biblioteca)",
                "ru": "Обнаружить аномалии L-пространства в 3:33 (связи библиотечного пространства)",
                "ja": "3:33にL空間の異常を検出（図書館空間の接続）",
                "zh": "在3:33检测L空间异常（图书馆空间连接）",
                "ko": "3:33에 L-공간 이상 감지 (도서관 공간 연결)"
            }
        },
        "century": {
            "type": "select",
            "default": "anchovy",
            "options": ["anchovy", "fruitbat", "garlic", "three_lice"],
            "label": {
                "en": "Century",
                "de": "Jahrhundert",
                "es": "Siglo",
                "fr": "Siècle",
                "it": "Secolo",
                "nl": "Eeuw",
                "pl": "Wiek",
                "pt": "Século",
                "ru": "Век",
                "ja": "世紀",
                "zh": "世纪",
                "ko": "세기"
            },
            "description": {
                "en": "Select which Century to display",
                "de": "Wähle welches Jahrhundert angezeigt werden soll",
                "es": "Selecciona qué Siglo mostrar",
                "fr": "Sélectionnez quel Siècle afficher",
                "it": "Seleziona quale Secolo visualizzare",
                "nl": "Selecteer welke Eeuw weer te geven",
                "pl": "Wybierz który Wiek wyświetlić",
                "pt": "Selecione qual Século exibir",
                "ru": "Выберите какой Век отображать",
                "ja": "表示する世紀を選択",
                "zh": "选择要显示的世纪",
                "ko": "표시할 세기 선택"
            },
            "options_label": {
                "anchovy": {
                    "en": "Century of the Anchovy",
                    "de": "Jahrhundert der Sardelle",
                    "es": "Siglo de la Anchoa",
                    "fr": "Siècle de l'Anchois",
                    "it": "Secolo dell'Acciuga",
                    "nl": "Eeuw van de Ansjovis",
                    "pl": "Wiek Sardeli",
                    "pt": "Século da Anchova",
                    "ru": "Век Анчоуса",
                    "ja": "アンチョビの世紀",
                    "zh": "凤尾鱼世纪",
                    "ko": "멸치의 세기"
                },
                "fruitbat": {
                    "en": "Century of the Fruitbat",
                    "de": "Jahrhundert der Flughunde",
                    "es": "Siglo del Murciélago Frugívoro",
                    "fr": "Siècle de la Chauve-souris Frugivore",
                    "it": "Secolo del Pipistrello della Frutta",
                    "nl": "Eeuw van de Fruitvleermuis",
                    "pl": "Wiek Nietoperza Owocowego",
                    "pt": "Século do Morcego-da-fruta",
                    "ru": "Век Фруктовой Летучей Мыши",
                    "ja": "フルーツコウモリの世紀",
                    "zh": "果蝠世纪",
                    "ko": "과일박쥐의 세기"
                },
                "garlic": {
                    "en": "Century of the Garlic",
                    "de": "Jahrhundert des Knoblauchs",
                    "es": "Siglo del Ajo",
                    "fr": "Siècle de l'Ail",
                    "it": "Secolo dell'Aglio",
                    "nl": "Eeuw van de Knoflook",
                    "pl": "Wiek Czosnku",
                    "pt": "Século do Alho",
                    "ru": "Век Чеснока",
                    "ja": "ニンニクの世紀",
                    "zh": "大蒜世纪",
                    "ko": "마늘의 세기"
                },
                "three_lice": {
                    "en": "Century of the Three Lice",
                    "de": "Jahrhundert der Drei Läuse",
                    "es": "Siglo de los Tres Piojos",
                    "fr": "Siècle des Trois Poux",
                    "it": "Secolo dei Tre Pidocchi",
                    "nl": "Eeuw van de Drie Luizen",
                    "pl": "Wiek Trzech Wszy",
                    "pt": "Século dos Três Piolhos",
                    "ru": "Век Трёх Вшей",
                    "ja": "三匹のシラミの世紀",
                    "zh": "三虱世纪",
                    "ko": "세 마리 이의 세기"
                }
            }
        }
    },

    # Discworld-specific data
    "discworld_data": {
        # Discworld months
        "months": [
            {"name": "Ick", "emoji": "❄️", "season": "Winter"},
            {"name": "Offle", "emoji": "❄️", "season": "Winter"},
            {"name": "February", "emoji": "🌨️", "season": "Winter"},
            {"name": "March", "emoji": "🌬️", "season": "Spring"},
            {"name": "April", "emoji": "🌧️", "season": "Spring"},
            {"name": "May", "emoji": "🌸", "season": "Spring"},
            {"name": "June", "emoji": "☀️", "season": "Summer"},
            {"name": "Grune", "emoji": "🌿", "season": "Summer"},
            {"name": "August", "emoji": "🌞", "season": "Summer"},
            {"name": "Spune", "emoji": "🍂", "season": "Autumn"},
            {"name": "Sektober", "emoji": "🍺", "season": "Autumn"},
            {"name": "Ember", "emoji": "🔥", "season": "Autumn"},
            {"name": "December", "emoji": "⭐", "season": "Winter"}
        ],

        # 8-day week
        "weekdays": [
            "Sunday", "Monday", "Tuesday", "Wednesday",
            "Thursday", "Friday", "Saturday", "Octeday"
        ],

        # Guilds of Ankh-Morpork
        "guilds": [
            "Assassins' Guild", "Thieves' Guild", "Seamstresses' Guild",
            "Beggars' Guild", "Merchants' Guild", "Alchemists' Guild",
            "Wizards (Unseen University)", "Watch (City Guard)",
            "Fools' Guild", "Musicians' Guild", "Bakers' Guild",
            "Butchers' Guild", "Candlemakers' Guild"
        ],

        # Special events
        "events": {
            (1, 1): "🎅 Hogswatchday",
            (2, 14): "💘 Day of Small Gods",
            (3, 25): "🎪 The Rag Week",
            (4, 1): "🤡 All Fools' Day",
            (4, 32): "❓ Day That Never Happens",
            (5, 1): "🌺 May Day",
            (5, 25): "🎆 Glorious Revolution Day",
            (6, 21): "☀️ Midsummer's Eve",
            (7, 15): "👑 Patrician's Birthday",
            (8, 12): "🗡️ Thieves' Guild Day",
            (9, 9): "🔮 Mrs. Cake Day",
            (10, 31): "🎃 Soul Cake Night",
            (11, 11): "☕ Elevenses Day",
            (12, 32): "🎄 Hogswatch Eve"
        },

        # Death quotes
        "death_quotes": [
            "THERE IS NO JUSTICE. THERE IS JUST ME.",
            "I COULD MURDER A CURRY.",
            "CATS. CATS ARE NICE.",
            "SQUEAK.",
            "THE DUTY IS MINE.",
            "WHAT CAN THE HARVEST HOPE FOR, IF NOT FOR THE CARE OF THE REAPER MAN?",
            "I DON'T HOLD WITH CRUELTY TO CATS.",
            "YOU NEED TO BELIEVE IN THINGS THAT AREN'T TRUE. HOW ELSE CAN THEY BECOME?",
            "HUMANS NEED FANTASY TO BE HUMAN.",
            "IT IS THE MOST HUMAN THING TO DO.",
            "THERE'S NO POINT IN BELIEVING IN THINGS THAT EXIST.",
            "I REMEMBER WHEN ALL THIS WILL BE AGAIN."
        ],

        # City areas
        "city_areas": [
            "The Shades", "Patrician's Palace", "Unseen University",
            "The Docks", "Treacle Mine Road", "Cable Street",
            "The Hippo", "Isle of Gods", "Pseudopolis Yard",
            "Sator Square", "The Maul", "Dolly Sisters"
        ],

        # Time periods
        "time_periods": {
            (0, 3): {"name": "Dead of Night", "description": "Graveyard Shift", "emoji": "🌙"},
            (3, 6): {"name": "Small Hours", "description": "Thieves' Time", "emoji": "⭐"},
            (6, 9): {"name": "Dawn", "description": "Milkmen About", "emoji": "🌅"},
            (9, 12): {"name": "Morning", "description": "Shops Open", "emoji": "☀️"},
            (12, 13): {"name": "Noon", "description": "Lunch at Harga's", "emoji": "🍽️"},
            (13, 17): {"name": "Afternoon", "description": "Siesta Time", "emoji": "🌤️"},
            (17, 19): {"name": "Evening", "description": "Pub O'Clock", "emoji": "🍺"},
            (19, 21): {"name": "Dusk", "description": "Theatre Time", "emoji": "🌆"},
            (21, 24): {"name": "Night", "description": "Watch Patrol", "emoji": "🌃"}
        },

        # Century names
        "centuries": {
            "anchovy": "Century of the Anchovy",
            "fruitbat": "Century of the Fruitbat",
            "garlic": "Century of the Garlic",
            "three_lice": "Century of the Three Lice"
        }
    },

    # Additional metadata
    "reference_url": "https://wiki.lspace.org/Discworld_calendar",
    "documentation_url": "https://www.terrypratchettbooks.com/",
    "origin": "Terry Pratchett's Discworld series",
    "created_by": "Terry Pratchett",
    "introduced": "The Colour of Magic (1983)",

    # Example format
    "example": "Century of the Anchovy, UC 25, 15 Grune (Octeday)",
    "example_meaning": "Century of the Anchovy, UC (University Calendar) year 25, 15th of Grune, Octeday",

    # Related calendars
    "related": ["gregorian", "fictional"],

    # Tags for searching and filtering
    "tags": [
        "fantasy", "discworld", "pratchett", "ankh-morpork", "fictional",
        "humor", "death", "guilds", "octeday", "turtle", "atuin", "rincewind"
    ],

    # Special features
    "features": {
        "eight_day_week": True,
        "guild_system": True,
        "impossible_dates": True,
        "death_appearances": True,
        "l_space": True,
        "precision": "day"
    }
}


class DiscworldCalendarSensor(AlternativeTimeSensorBase):
    """Sensor for displaying Discworld Calendar (Terry Pratchett)."""

    # Class-level update interval
    UPDATE_INTERVAL = UPDATE_INTERVAL

    def __init__(self, base_name: str, hass: HomeAssistant) -> None:
        """Initialize the Discworld calendar sensor."""
        super().__init__(base_name, hass)

        # Get translated name from metadata
        calendar_name = self._translate('name', 'Discworld Calendar')

        # Set sensor attributes
        self._attr_name = f"{base_name} {calendar_name}"
        self._attr_unique_id = f"{base_name}_discworld_calendar"
        self._attr_icon = CALENDAR_INFO.get("icon", "mdi:turtle")

        # Configuration options with defaults
        config_defaults = CALENDAR_INFO.get("config_options", {})
        self._show_death_quotes = config_defaults.get("show_death_quotes", {}).get("default", True)
        self._show_guild = config_defaults.get("show_guild", {}).get("default", True)
        self._show_location = config_defaults.get("show_location", {}).get("default", True)
        self._detect_l_space = config_defaults.get("detect_l_space", {}).get("default", True)
        self._century = config_defaults.get("century", {}).get("default", "anchovy")

        # Discworld data
        self._discworld_data = CALENDAR_INFO["discworld_data"]

        # Initialize state
        self._state = None
        self._discworld_date = {}

        _LOGGER.debug(f"Initialized Discworld Calendar sensor: {self._attr_name}")

    def set_options(self, options: Dict[str, Any]) -> None:
        """Set options from config flow."""
        if options:
            self._show_death_quotes = options.get("show_death_quotes", self._show_death_quotes)
            self._show_guild = options.get("show_guild", self._show_guild)
            self._show_location = options.get("show_location", self._show_location)
            self._detect_l_space = options.get("detect_l_space", self._detect_l_space)
            self._century = options.get("century", self._century)

            _LOGGER.debug(f"Discworld sensor options updated: show_death_quotes={self._show_death_quotes}, "
                         f"show_guild={self._show_guild}, show_location={self._show_location}, "
                         f"detect_l_space={self._detect_l_space}, century={self._century}")

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes."""
        attrs = super().extra_state_attributes

        # Add Discworld-specific attributes
        if self._discworld_date:
            attrs.update(self._discworld_date)

            # Add description in user's language
            attrs["description"] = self._translate('description')

            # Add reference
            attrs["reference"] = CALENDAR_INFO.get('reference_url', '')

            # Add Great A'Tuin status
            attrs["great_atuin"] = "Swimming through space 🐢"
            attrs["elephants"] = "Berilia, Tubul, Great T'Phon, and Jerakeen"

            # Add configuration status
            attrs["config"] = {
                "show_death_quotes": self._show_death_quotes,
                "show_guild": self._show_guild,
                "show_location": self._show_location,
                "detect_l_space": self._detect_l_space,
                "century": self._century
            }

        return attrs

    def _get_time_period(self, hour: int) -> Dict[str, str]:
        """Get the Discworld time period for the hour."""
        for (start, end), period in self._discworld_data["time_periods"].items():
            if start <= hour < end:
                return period
        return {"name": "Temporal Anomaly", "description": "Time is broken", "emoji": "⏰"}

    def _calculate_discworld_date(self, earth_date: datetime) -> Dict[str, Any]:
        """Calculate Discworld Calendar date from standard date."""

        # Discworld year
        year_since_2000 = earth_date.year - 2000
        discworld_year = 1 + year_since_2000

        # Get century name
        century_name = self._discworld_data["centuries"][self._century]

        # Get month and day
        month_index = min(earth_date.month - 1, 12)
        day = earth_date.day

        # Handle special 32nd days (Discworld has them!)
        if day == 31 and earth_date.month in [4, 12]:
            day = 32  # Discworld logic!

        # Get month data
        if month_index < len(self._discworld_data["months"]):
            month_data = self._discworld_data["months"][month_index]
        else:
            month_data = {"name": "Backspindlemonth", "emoji": "🌀", "season": "Temporal"}

        # Calculate weekday (8-day week)
        days_since_epoch = (earth_date - datetime(2000, 1, 1)).days
        weekday_index = days_since_epoch % 8
        weekday = self._discworld_data["weekdays"][weekday_index]
        is_octeday = weekday_index == 7

        # Check for events
        event = self._discworld_data["events"].get((earth_date.month, day), "")

        # Guild influence (rotates daily)
        guild_index = days_since_epoch % len(self._discworld_data["guilds"])
        guild = self._discworld_data["guilds"][guild_index] if self._show_guild else ""

        # Death quote (changes daily)
        death_index = days_since_epoch % len(self._discworld_data["death_quotes"])
        death_quote = self._discworld_data["death_quotes"][death_index]

        # City location (changes hourly)
        location_index = (days_since_epoch + earth_date.hour) % len(self._discworld_data["city_areas"])
        location = self._discworld_data["city_areas"][location_index] if self._show_location else ""

        # Time period
        time_period = self._get_time_period(earth_date.hour)

        # L-Space detection
        l_space_detected = (earth_date.hour == 3 and earth_date.minute == 33) if self._detect_l_space else False

        # Build result
        result = {
            "year": discworld_year,
            "century": century_name,
            "month": month_data["name"],
            "month_emoji": month_data["emoji"],
            "season": month_data["season"],
            "day": day,
            "weekday": weekday,
            "is_octeday": is_octeday,
            "time_period": time_period["name"],
            "time_description": time_period["description"],
            "time_emoji": time_period["emoji"],
            "gregorian_date": earth_date.strftime("%Y-%m-%d"),
            "full_date": f"{century_name}, UC {discworld_year}, {day} {month_data['name']}"
        }

        # Add optional data
        if guild:
            result["guild_influence"] = f"⚔️ {guild}"

        if location:
            result["location"] = f"📍 {location}"

        if event:
            result["event"] = event

        if self._show_death_quotes and earth_date.hour == 0:
            result["death_says"] = f"💀 {death_quote}"

        if l_space_detected:
            result["l_space_anomaly"] = "📚 L-Space portal detected! All libraries are one!"

        if is_octeday:
            result["octeday_special"] = "🎉 It's Octeday! Extra day off work!"

        return result

    def update(self) -> None:
        """Update the sensor."""
        now = datetime.now()
        self._discworld_date = self._calculate_discworld_date(now)

        # Build state string
        state_parts = [
            f"UC {self._discworld_date['year']}",
            f"{self._discworld_date['day']} {self._discworld_date['month']}"
        ]

        if self._discworld_date['is_octeday']:
            state_parts.append("(Octeday!)")
        else:
            state_parts.append(f"({self._discworld_date['weekday']})")

        self._state = " ".join(state_parts)

        _LOGGER.debug(f"Updated Discworld Calendar to {self._state}")
