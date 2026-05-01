"""Japanese Traditional Lunar Calendar (旧暦, Kyūreki) implementation - Version 2.5."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Tuple
from zoneinfo import ZoneInfo

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
    "id": "japanese_lunar",
    "version": "2.5.0",
    "icon": "mdi:moon-waning-crescent",
    "category": "cultural",
    "accuracy": "traditional",
    "update_interval": UPDATE_INTERVAL,

    # Multi-language names
    "name": {
        "en": "Japanese Lunar Calendar",
        "de": "Japanischer Mondkalender",
        "es": "Calendario Lunar Japonés",
        "fr": "Calendrier Lunaire Japonais",
        "it": "Calendario Lunare Giapponese",
        "nl": "Japanse Maankalender",
        "pl": "Japoński Kalendarz Księżycowy",
        "pt": "Calendário Lunar Japonês",
        "ru": "Японский лунный календарь",
        "ja": "旧暦",
        "zh": "日本阴历",
        "ko": "일본 음력"
    },

    # Short descriptions for UI
    "description": {
        "en": "Traditional Japanese lunisolar calendar (Kyūreki) used for festivals and agricultural timing",
        "de": "Traditioneller japanischer Lunisolarkalender (Kyūreki) für Feste und landwirtschaftliche Zeitplanung",
        "es": "Calendario lunisolar japonés tradicional (Kyūreki) usado para festivales y calendario agrícola",
        "fr": "Calendrier lunisolaire japonais traditionnel (Kyūreki) utilisé pour les festivals et le calendrier agricole",
        "it": "Calendario lunisolare giapponese tradizionale (Kyūreki) usato per festival e calendario agricolo",
        "nl": "Traditionele Japanse lunisolaire kalender (Kyūreki) gebruikt voor festivals en landbouwtiming",
        "pl": "Tradycyjny japoński kalendarz księżycowo-słoneczny (Kyūreki) używany do festiwali i kalendarza rolniczego",
        "pt": "Calendário lunissolar japonês tradicional (Kyūreki) usado para festivais e calendário agrícola",
        "ru": "Традиционный японский лунно-солнечный календарь (Кюрэки) для праздников и сельскохозяйственного календаря",
        "ja": "祭りや農業の暦として使われる日本の伝統的な太陰太陽暦",
        "zh": "用于节日和农业时令的日本传统阴阳历（旧历）",
        "ko": "축제와 농업 시기에 사용되는 일본 전통 태음태양력 (구력)"
    },

    # Extended information for tooltips
    "notes": {
        "en": "The Kyūreki (旧暦) is Japan's traditional lunisolar calendar, still used for determining traditional festivals, agricultural activities, and auspicious dates. Each month begins with the new moon. Time is displayed in Japan Standard Time (JST).",
        "de": "Der Kyūreki (旧暦) ist Japans traditioneller Lunisolarkalender, der noch zur Bestimmung traditioneller Feste, landwirtschaftlicher Aktivitäten und glückverheißender Daten verwendet wird. Jeder Monat beginnt mit dem Neumond. Die Zeit wird in Japan Standard Time (JST) angezeigt.",
        "es": "El Kyūreki (旧暦) es el calendario lunisolar tradicional de Japón, todavía utilizado para determinar festivales tradicionales, actividades agrícolas y fechas auspiciosas. Cada mes comienza con la luna nueva. La hora se muestra en Hora Estándar de Japón (JST).",
        "fr": "Le Kyūreki (旧暦) est le calendrier lunisolaire traditionnel du Japon, encore utilisé pour déterminer les festivals traditionnels, les activités agricoles et les dates propices. Chaque mois commence avec la nouvelle lune. L'heure est affichée en heure normale du Japon (JST).",
        "it": "Il Kyūreki (旧暦) è il calendario lunisolare tradizionale del Giappone, ancora usato per determinare festival tradizionali, attività agricole e date propizie. Ogni mese inizia con la luna nuova. L'ora è visualizzata in Japan Standard Time (JST).",
        "nl": "De Kyūreki (旧暦) is Japans traditionele lunisolaire kalender, nog steeds gebruikt voor het bepalen van traditionele festivals, landbouwactiviteiten en gunstige data. Elke maand begint met nieuwe maan. De tijd wordt weergegeven in Japan Standard Time (JST).",
        "pl": "Kyūreki (旧暦) to tradycyjny japoński kalendarz księżycowo-słoneczny, nadal używany do określania tradycyjnych festiwali, działań rolniczych i pomyślnych dat. Każdy miesiąc zaczyna się od nowiu. Czas jest wyświetlany w Japan Standard Time (JST).",
        "pt": "O Kyūreki (旧暦) é o calendário lunissolar tradicional do Japão, ainda usado para determinar festivais tradicionais, atividades agrícolas e datas auspiciosas. Cada mês começa com a lua nova. A hora é exibida em Horário Padrão do Japão (JST).",
        "ru": "Кюрэки (旧暦) - традиционный лунно-солнечный календарь Японии, все еще используемый для определения традиционных праздников, сельскохозяйственной деятельности и благоприятных дат. Каждый месяц начинается с новолуния. Время отображается в японском стандартном времени (JST).",
        "ja": "旧暦は日本の伝統的な太陰太陽暦で、伝統的な祭り、農業活動、吉日の決定に今も使用されています。各月は新月から始まります。時刻は日本標準時（JST）で表示されます。",
        "zh": "旧历是日本的传统阴阳历，仍用于确定传统节日、农业活动和吉日。每月从新月开始。时间以日本标准时间（JST）显示。",
        "ko": "구력(旧暦)은 일본의 전통 태음태양력으로, 여전히 전통 축제, 농업 활동, 길일 결정에 사용됩니다. 매달 초승달부터 시작됩니다. 시간은 일본 표준시(JST)로 표시됩니다."
    },

    # Configuration options
    "config_options": {
        "timezone": {
            "type": "select",
            "default": "Asia/Tokyo",
            "options": ["Asia/Tokyo", "local", "UTC"],
            "label": {
                "en": "Time Zone",
                "de": "Zeitzone",
                "es": "Zona Horaria",
                "fr": "Fuseau Horaire",
                "it": "Fuso Orario",
                "nl": "Tijdzone",
                "pl": "Strefa Czasowa",
                "pt": "Fuso Horário",
                "ru": "Часовой пояс",
                "ja": "タイムゾーン",
                "zh": "时区",
                "ko": "시간대"
            },
            "description": {
                "en": "Choose timezone for lunar date calculation (JST recommended)",
                "de": "Zeitzone für Monddatumsberechnung wählen (JST empfohlen)",
                "es": "Elegir zona horaria para el cálculo de fecha lunar (JST recomendado)",
                "fr": "Choisir le fuseau horaire pour le calcul de la date lunaire (JST recommandé)",
                "it": "Scegli il fuso orario per il calcolo della data lunare (JST consigliato)",
                "nl": "Kies tijdzone voor maandatumberekening (JST aanbevolen)",
                "pl": "Wybierz strefę czasową do obliczania daty księżycowej (zalecane JST)",
                "pt": "Escolher fuso horário para cálculo de data lunar (JST recomendado)",
                "ru": "Выберите часовой пояс для расчета лунной даты (рекомендуется JST)",
                "ja": "旧暦計算のタイムゾーンを選択（JST推奨）",
                "zh": "选择阴历日期计算的时区（推荐JST）",
                "ko": "음력 날짜 계산을 위한 시간대 선택 (JST 권장)"
            }
        },
        "show_moon_phase": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show Moon Phase",
                "de": "Mondphase anzeigen",
                "es": "Mostrar Fase Lunar",
                "fr": "Afficher la Phase Lunaire",
                "it": "Mostra Fase Lunare",
                "nl": "Maanfase Tonen",
                "pl": "Pokaż Fazę Księżyca",
                "pt": "Mostrar Fase Lunar",
                "ru": "Показать фазу луны",
                "ja": "月相を表示",
                "zh": "显示月相",
                "ko": "달의 위상 표시"
            },
            "description": {
                "en": "Display current moon phase with traditional names",
                "de": "Zeigt die aktuelle Mondphase mit traditionellen Namen an",
                "es": "Muestra la fase lunar actual con nombres tradicionales",
                "fr": "Affiche la phase lunaire actuelle avec des noms traditionnels",
                "it": "Visualizza la fase lunare corrente con nomi tradizionali",
                "nl": "Toont de huidige maanfase met traditionele namen",
                "pl": "Wyświetla aktualną fazę księżyca z tradycyjnymi nazwami",
                "pt": "Exibe a fase lunar atual com nomes tradicionais",
                "ru": "Отображает текущую фазу луны с традиционными названиями",
                "ja": "伝統的な名称で現在の月相を表示します",
                "zh": "用传统名称显示当前月相",
                "ko": "전통적인 이름으로 현재 달의 위상 표시"
            }
        },
        "show_solar_terms": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show Solar Terms",
                "de": "Solarterme anzeigen",
                "es": "Mostrar Términos Solares",
                "fr": "Afficher les Termes Solaires",
                "it": "Mostra Termini Solari",
                "nl": "Zonnetermen Tonen",
                "pl": "Pokaż Terminy Słoneczne",
                "pt": "Mostrar Termos Solares",
                "ru": "Показать солнечные термины",
                "ja": "二十四節気を表示",
                "zh": "显示二十四节气",
                "ko": "24절기 표시"
            },
            "description": {
                "en": "Display the 24 solar terms (Nijūshi Sekki) used in agriculture",
                "de": "Zeigt die 24 Solarterme (Nijūshi Sekki) für die Landwirtschaft an",
                "es": "Muestra los 24 términos solares (Nijūshi Sekki) usados en agricultura",
                "fr": "Affiche les 24 termes solaires (Nijūshi Sekki) utilisés en agriculture",
                "it": "Visualizza i 24 termini solari (Nijūshi Sekki) usati in agricoltura",
                "nl": "Toont de 24 zonnetermen (Nijūshi Sekki) gebruikt in landbouw",
                "pl": "Wyświetla 24 terminy słoneczne (Nijūshi Sekki) używane w rolnictwie",
                "pt": "Exibe os 24 termos solares (Nijūshi Sekki) usados na agricultura",
                "ru": "Отображает 24 солнечных термина (Нидзюси Сэкки) для сельского хозяйства",
                "ja": "農業で使用される二十四節気を表示します",
                "zh": "显示农业中使用的二十四节气",
                "ko": "농업에 사용되는 24절기 표시"
            }
        },
        "show_traditional_events": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show Traditional Events",
                "de": "Traditionelle Ereignisse anzeigen",
                "es": "Mostrar Eventos Tradicionales",
                "fr": "Afficher les Événements Traditionnels",
                "it": "Mostra Eventi Tradizionali",
                "nl": "Traditionele Gebeurtenissen Tonen",
                "pl": "Pokaż Tradycyjne Wydarzenia",
                "pt": "Mostrar Eventos Tradicionais",
                "ru": "Показать традиционные события",
                "ja": "伝統行事を表示",
                "zh": "显示传统节日",
                "ko": "전통 행사 표시"
            },
            "description": {
                "en": "Display traditional festivals and observances based on lunar calendar",
                "de": "Zeigt traditionelle Feste und Bräuche basierend auf dem Mondkalender an",
                "es": "Muestra festivales y observancias tradicionales basados en el calendario lunar",
                "fr": "Affiche les festivals et observances traditionnels basés sur le calendrier lunaire",
                "it": "Visualizza festival e osservanze tradizionali basati sul calendario lunare",
                "nl": "Toont traditionele festivals en observanties gebaseerd op de maankalender",
                "pl": "Wyświetla tradycyjne festiwale i obchody oparte na kalendarzu księżycowym",
                "pt": "Exibe festivais e observâncias tradicionais baseados no calendário lunar",
                "ru": "Отображает традиционные праздники и обряды на основе лунного календаря",
                "ja": "旧暦に基づく伝統的な祭りや行事を表示します",
                "zh": "显示基于阴历的传统节日和习俗",
                "ko": "음력 기반 전통 축제 및 행사 표시"
            }
        },
        "show_zodiac": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show Zodiac Animals",
                "de": "Tierkreiszeichen anzeigen",
                "es": "Mostrar Animales del Zodiaco",
                "fr": "Afficher les Animaux du Zodiaque",
                "it": "Mostra Animali dello Zodiaco",
                "nl": "Dierenriem Tonen",
                "pl": "Pokaż Zwierzęta Zodiaku",
                "pt": "Mostrar Animais do Zodíaco",
                "ru": "Показать животных зодиака",
                "ja": "十二支を表示",
                "zh": "显示生肖",
                "ko": "십이지 표시"
            },
            "description": {
                "en": "Display the 12 zodiac animals (Eto) for year, month and day",
                "de": "Zeigt die 12 Tierkreiszeichen (Eto) für Jahr, Monat und Tag an",
                "es": "Muestra los 12 animales del zodiaco (Eto) para año, mes y día",
                "fr": "Affiche les 12 animaux du zodiaque (Eto) pour l'année, le mois et le jour",
                "it": "Visualizza i 12 animali dello zodiaco (Eto) per anno, mese e giorno",
                "nl": "Toont de 12 dierenriemtekens (Eto) voor jaar, maand en dag",
                "pl": "Wyświetla 12 zwierząt zodiaku (Eto) dla roku, miesiąca i dnia",
                "pt": "Exibe os 12 animais do zodíaco (Eto) para ano, mês e dia",
                "ru": "Отображает 12 животных зодиака (Это) для года, месяца и дня",
                "ja": "年、月、日の十二支を表示します",
                "zh": "显示年、月、日的十二生肖",
                "ko": "년, 월, 일의 십이지 표시"
            }
        },
        "display_language": {
            "type": "select",
            "default": "auto",
            "options": ["auto", "japanese", "english"],
            "label": {
                "en": "Display Language",
                "de": "Anzeigesprache",
                "es": "Idioma de Visualización",
                "fr": "Langue d'Affichage",
                "it": "Lingua di Visualizzazione",
                "nl": "Weergavetaal",
                "pl": "Język Wyświetlania",
                "pt": "Idioma de Exibição",
                "ru": "Язык отображения",
                "ja": "表示言語",
                "zh": "显示语言",
                "ko": "표시 언어"
            },
            "description": {
                "en": "Choose display language (auto uses Home Assistant language)",
                "de": "Anzeigesprache wählen (auto verwendet Home Assistant Sprache)",
                "es": "Elegir idioma de visualización (auto usa el idioma de Home Assistant)",
                "fr": "Choisir la langue d'affichage (auto utilise la langue de Home Assistant)",
                "it": "Scegli la lingua di visualizzazione (auto usa la lingua di Home Assistant)",
                "nl": "Kies weergavetaal (auto gebruikt Home Assistant taal)",
                "pl": "Wybierz język wyświetlania (auto używa języka Home Assistant)",
                "pt": "Escolher idioma de exibição (auto usa o idioma do Home Assistant)",
                "ru": "Выберите язык отображения (auto использует язык Home Assistant)",
                "ja": "表示言語を選択（autoはHome Assistantの言語を使用）",
                "zh": "选择显示语言（auto使用Home Assistant语言）",
                "ko": "표시 언어 선택 (auto는 Home Assistant 언어 사용)"
            }
        },
        "display_format": {
            "type": "select",
            "default": "traditional",
            "options": ["traditional", "modern", "numeric"],
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
                "en": "Choose how to display the lunar date",
                "de": "Wählen Sie, wie das Monddatum angezeigt werden soll",
                "es": "Elija cómo mostrar la fecha lunar",
                "fr": "Choisissez comment afficher la date lunaire",
                "it": "Scegli come visualizzare la data lunare",
                "nl": "Kies hoe de maandatum wordt weergegeven",
                "pl": "Wybierz sposób wyświetlania daty księżycowej",
                "pt": "Escolha como exibir a data lunar",
                "ru": "Выберите формат отображения лунной даты",
                "ja": "旧暦日付の表示方法を選択",
                "zh": "选择如何显示阴历日期",
                "ko": "음력 날짜 표시 방법 선택"
            }
        }
    },

    # Lunar calendar data
    "lunar_data": {
        "months": {
            "traditional": ["睦月", "如月", "弥生", "卯月", "皐月", "水無月",
                          "文月", "葉月", "長月", "神無月", "霜月", "師走"],
            "modern": ["正月", "二月", "三月", "四月", "五月", "六月",
                      "七月", "八月", "九月", "十月", "十一月", "十二月"]
        },
        "moon_phases": {
            "names": {
                "ja": ["新月", "二日月", "三日月", "上弦", "十三夜", "小望月", "満月",
                      "十六夜", "立待月", "居待月", "寝待月", "更待月", "下弦", "有明月"],
                "en": ["New Moon", "Young Moon", "Crescent", "First Quarter", "Waxing Gibbous",
                      "Near Full", "Full Moon", "Waning Full", "Waning Gibbous", "Third Quarter",
                      "Waning Crescent", "Old Crescent", "Last Quarter", "Dawn Moon"]
            }
        },
        "zodiac_animals": {
            "ja": ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"],
            "en": ["Rat", "Ox", "Tiger", "Rabbit", "Dragon", "Snake",
                   "Horse", "Goat", "Monkey", "Rooster", "Dog", "Boar"],
            "emoji": ["🐀", "🐂", "🐅", "🐰", "🐉", "🐍", "🐴", "🐐", "🐵", "🐓", "🐕", "🐗"]
        },
        "solar_terms": [
            {"ja": "立春", "en": "Start of Spring", "date": "Feb 4"},
            {"ja": "雨水", "en": "Rain Water", "date": "Feb 19"},
            {"ja": "啓蟄", "en": "Awakening of Insects", "date": "Mar 6"},
            {"ja": "春分", "en": "Spring Equinox", "date": "Mar 21"},
            {"ja": "清明", "en": "Clear and Bright", "date": "Apr 5"},
            {"ja": "穀雨", "en": "Grain Rain", "date": "Apr 20"},
            {"ja": "立夏", "en": "Start of Summer", "date": "May 6"},
            {"ja": "小満", "en": "Grain Full", "date": "May 21"},
            {"ja": "芒種", "en": "Grain in Ear", "date": "Jun 6"},
            {"ja": "夏至", "en": "Summer Solstice", "date": "Jun 21"},
            {"ja": "小暑", "en": "Minor Heat", "date": "Jul 7"},
            {"ja": "大暑", "en": "Major Heat", "date": "Jul 23"},
            {"ja": "立秋", "en": "Start of Autumn", "date": "Aug 8"},
            {"ja": "処暑", "en": "End of Heat", "date": "Aug 23"},
            {"ja": "白露", "en": "White Dew", "date": "Sep 8"},
            {"ja": "秋分", "en": "Autumn Equinox", "date": "Sep 23"},
            {"ja": "寒露", "en": "Cold Dew", "date": "Oct 8"},
            {"ja": "霜降", "en": "Frost Descent", "date": "Oct 23"},
            {"ja": "立冬", "en": "Start of Winter", "date": "Nov 7"},
            {"ja": "小雪", "en": "Minor Snow", "date": "Nov 22"},
            {"ja": "大雪", "en": "Major Snow", "date": "Dec 7"},
            {"ja": "冬至", "en": "Winter Solstice", "date": "Dec 22"},
            {"ja": "小寒", "en": "Minor Cold", "date": "Jan 5"},
            {"ja": "大寒", "en": "Major Cold", "date": "Jan 20"}
        ],
        "traditional_events": {
            "1-1": {"ja": "元日", "en": "New Year's Day"},
            "1-7": {"ja": "七草", "en": "Seven Herbs Festival"},
            "1-15": {"ja": "小正月", "en": "Little New Year"},
            "3-3": {"ja": "雛祭り", "en": "Girls' Festival"},
            "5-5": {"ja": "端午の節句", "en": "Boys' Festival"},
            "7-7": {"ja": "七夕", "en": "Star Festival"},
            "7-15": {"ja": "お盆", "en": "Obon"},
            "8-15": {"ja": "中秋の名月", "en": "Harvest Moon"},
            "9-9": {"ja": "重陽の節句", "en": "Chrysanthemum Festival"}
        }
    },

    # Additional metadata
    "reference_url": "https://eco.mtk.nao.ac.jp/koyomi/",
    "documentation_url": "https://en.wikipedia.org/wiki/Japanese_calendar#Lunar_calendar",
    "created_by": "Traditional Japanese System",
    "introduced": "6th century (from China)",

    # Example format
    "example": "旧暦 睦月十五日（満月）子年",
    "example_meaning": "Lunar Calendar: 15th day of Mutsuki (Full Moon), Year of the Rat",

    # Related calendars
    "related": ["japanese_era", "chinese_lunar", "korean_lunar"],

    # Tags for searching and filtering
    "tags": [
        "japanese", "lunar", "traditional", "kyureki", "agriculture",
        "moon", "festivals", "zodiac", "cultural", "asia", "japan"
    ],

    # Special features
    "features": {
        "supports_lunar_months": True,
        "supports_moon_phases": True,
        "supports_solar_terms": True,
        "supports_zodiac": True,
        "supports_traditional_events": True,
        "precision": "day"
    }
}


class JapaneseLunarCalendarSensor(AlternativeTimeSensorBase):
    """Sensor for displaying Japanese Traditional Lunar Calendar (Kyūreki)."""

    # Class-level update interval
    UPDATE_INTERVAL = UPDATE_INTERVAL

    def __init__(self, base_name: str, hass: HomeAssistant) -> None:
        """Initialize the Japanese Lunar calendar sensor."""
        super().__init__(base_name, hass)

        # Store CALENDAR_INFO as instance variable for _translate method
        self._calendar_info = CALENDAR_INFO

        # Get translated name from metadata
        calendar_name = self._translate('name', 'Japanese Lunar Calendar')

        # Set sensor attributes
        self._attr_name = f"{base_name} {calendar_name}"
        self._attr_unique_id = f"{base_name}_japanese_lunar"
        self._attr_icon = CALENDAR_INFO.get("icon", "mdi:moon-waning-crescent")

        # Configuration options with defaults from CALENDAR_INFO
        config_defaults = CALENDAR_INFO.get("config_options", {})
        self._timezone = config_defaults.get("timezone", {}).get("default", "Asia/Tokyo")
        self._display_language = config_defaults.get("display_language", {}).get("default", "auto")
        self._display_format = config_defaults.get("display_format", {}).get("default", "traditional")
        self._show_moon_phase = config_defaults.get("show_moon_phase", {}).get("default", True)
        self._show_solar_terms = config_defaults.get("show_solar_terms", {}).get("default", True)
        self._show_traditional_events = config_defaults.get("show_traditional_events", {}).get("default", True)
        self._show_zodiac = config_defaults.get("show_zodiac", {}).get("default", True)

        # Lunar data
        self._lunar_data = CALENDAR_INFO["lunar_data"]

        # Flag to track if options have been loaded
        self._options_loaded = False

        # Initialize state
        self._state = None
        self._lunar_date = {}

        _LOGGER.debug(f"Initialized Japanese Lunar Calendar sensor: {self._attr_name}")

    def _load_options(self) -> None:
        """Load plugin options after IDs are set."""
        if self._options_loaded:
            return

        # Get plugin options from config entry
        plugin_options = self.get_plugin_options()

        if plugin_options:
            _LOGGER.debug(f"Loading Japanese Lunar options: {plugin_options}")

            # Apply options using set_options method
            self.set_options(
                timezone=plugin_options.get("timezone"),
                display_language=plugin_options.get("display_language"),
                show_moon_phase=plugin_options.get("show_moon_phase"),
                show_solar_terms=plugin_options.get("show_solar_terms"),
                show_traditional_events=plugin_options.get("show_traditional_events"),
                show_zodiac=plugin_options.get("show_zodiac"),
                display_format=plugin_options.get("display_format")
            )

        self._options_loaded = True

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added to hass."""
        await super().async_added_to_hass()

        # Load options after entity is registered
        self._load_options()

        _LOGGER.debug(f"Japanese Lunar sensor added to hass with options: "
                     f"timezone={self._timezone}, moon_phase={self._show_moon_phase}, "
                     f"solar_terms={self._show_solar_terms}, events={self._show_traditional_events}")

    def set_options(
        self,
        *,
        timezone: Optional[str] = None,
        display_language: Optional[str] = None,
        show_moon_phase: Optional[bool] = None,
        show_solar_terms: Optional[bool] = None,
        show_traditional_events: Optional[bool] = None,
        show_zodiac: Optional[bool] = None,
        display_format: Optional[str] = None
    ) -> None:
        """Set calendar options from config flow."""
        if timezone is not None and timezone in ["Asia/Tokyo", "local", "UTC"]:
            self._timezone = timezone
            _LOGGER.debug(f"Set timezone to: {timezone}")

        if display_language is not None and display_language in ["auto", "japanese", "english"]:
            self._display_language = display_language
            _LOGGER.debug(f"Set display_language to: {display_language}")

        if show_moon_phase is not None:
            self._show_moon_phase = bool(show_moon_phase)
            _LOGGER.debug(f"Set show_moon_phase to: {show_moon_phase}")

        if show_solar_terms is not None:
            self._show_solar_terms = bool(show_solar_terms)
            _LOGGER.debug(f"Set show_solar_terms to: {show_solar_terms}")

        if show_traditional_events is not None:
            self._show_traditional_events = bool(show_traditional_events)
            _LOGGER.debug(f"Set show_traditional_events to: {show_traditional_events}")

        if show_zodiac is not None:
            self._show_zodiac = bool(show_zodiac)
            _LOGGER.debug(f"Set show_zodiac to: {show_zodiac}")

        if display_format is not None and display_format in ["traditional", "modern", "numeric"]:
            self._display_format = display_format
            _LOGGER.debug(f"Set display_format to: {display_format}")

    def _get_timezone(self) -> ZoneInfo:
        """Get the configured timezone."""
        if self._timezone == "Asia/Tokyo":
            return ZoneInfo("Asia/Tokyo")
        elif self._timezone == "UTC":
            return ZoneInfo("UTC")
        else:  # local
            # Try to get system timezone, fallback to UTC
            try:
                import tzlocal
                return tzlocal.get_localzone()
            except Exception:
                return ZoneInfo("UTC")

    def _calculate_moon_phase(self, japan_date: datetime) -> Tuple[float, str, str]:
        """Calculate moon phase for given date."""
        # Simplified moon phase calculation
        # Based on lunar synodic month of 29.53 days

        # Reference new moon (January 6, 2000, 18:14 UTC)
        ref_new_moon = datetime(2000, 1, 6, 18, 14, tzinfo=timezone.utc)

        # Calculate days since reference
        delta = japan_date.astimezone(timezone.utc) - ref_new_moon
        days_since = delta.total_seconds() / 86400

        # Calculate moon age (0-29.53)
        synodic_month = 29.530588
        moon_age = days_since % synodic_month

        # Determine phase name
        phase_index = int(moon_age / 2.1)
        if phase_index >= len(self._lunar_data["moon_phases"]["names"]["ja"]):
            phase_index = 0

        phase_ja = self._lunar_data["moon_phases"]["names"]["ja"][phase_index]
        phase_en = self._lunar_data["moon_phases"]["names"]["en"][phase_index]

        return moon_age, phase_ja, phase_en

    def _calculate_lunar_month_day(self, japan_date: datetime) -> Tuple[int, int, bool]:
        """Calculate lunar month and day for given date."""
        # Simplified lunar calendar calculation
        # This is a basic approximation - actual calculation is complex

        year = japan_date.year
        month = japan_date.month

        # Basic conversion (simplified)
        # Lunar calendar is approximately 11 days behind solar
        days_diff = 11
        lunar_date = japan_date - timedelta(days=days_diff)

        # Adjust for lunar month (29.5 days average)
        lunar_month = lunar_date.month
        lunar_day = lunar_date.day

        # Check for leap month (simplified - occurs roughly every 3 years)
        is_leap = (year % 3 == 0 and month == 6)

        return lunar_month, lunar_day, is_leap

    def _get_zodiac_animal(self, year: int) -> Dict[str, str]:
        """Get zodiac animal for given year."""
        zodiac_index = (year - 4) % 12
        return {
            "ja": self._lunar_data["zodiac_animals"]["ja"][zodiac_index],
            "en": self._lunar_data["zodiac_animals"]["en"][zodiac_index],
            "emoji": self._lunar_data["zodiac_animals"]["emoji"][zodiac_index]
        }

    def _get_solar_term(self, japan_date: datetime) -> Optional[Dict[str, str]]:
        """Get current or nearest solar term."""
        month = japan_date.month
        day = japan_date.day

        # Find matching or nearest solar term
        for term in self._lunar_data["solar_terms"]:
            # Parse approximate date from term
            term_month_day = term["date"].split()
            if len(term_month_day) == 2:
                term_month = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
                             "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}.get(term_month_day[0], 0)
                term_day = int(term_month_day[1])

                # Check if within 3 days of solar term
                if month == term_month and abs(day - term_day) <= 3:
                    return {"ja": term["ja"], "en": term["en"]}

        return None

    def _get_traditional_event(self, lunar_month: int, lunar_day: int) -> Optional[Dict[str, str]]:
        """Get traditional event for lunar date."""
        date_key = f"{lunar_month}-{lunar_day}"
        if date_key in self._lunar_data["traditional_events"]:
            return self._lunar_data["traditional_events"][date_key]
        return None

    def _format_lunar_date(self, lunar_month: int, lunar_day: int, moon_phase_ja: str, moon_phase_en: str,
                          zodiac: Dict, japan_date: datetime, is_leap: bool) -> str:
        """Format the lunar date according to display settings and language."""
        # Determine display language
        if self._display_language == "japanese":
            use_english = False
        elif self._display_language == "english":
            use_english = True
        else:  # auto
            lang = getattr(self._hass.config, "language", "en")
            use_english = lang not in ["ja", "zh", "ko"]  # Use English for non-Asian languages

        if self._display_format == "traditional":
            # Traditional format with old month names
            if use_english:
                # English format
                month_name = self._lunar_data["months"]["traditional"][lunar_month - 1]
                result = f"Lunar {month_name} {lunar_day}"
                if is_leap:
                    result += " (Leap)"
                if self._show_moon_phase:
                    result += f" ({moon_phase_en})"
                if self._show_zodiac:
                    result += f", Year of {zodiac['en']}"
            else:
                # Japanese format
                month_name = self._lunar_data["months"]["traditional"][lunar_month - 1]
                result = f"旧暦 {month_name}"
                if is_leap:
                    result += "（閏）"
                result += f"{lunar_day}日"
                if self._show_moon_phase:
                    result += f"（{moon_phase_ja}）"
                if self._show_zodiac:
                    result += f" {zodiac['ja']}年"

        elif self._display_format == "modern":
            # Modern format
            if use_english:
                result = f"Lunar {lunar_month}/{lunar_day}"
                if is_leap:
                    result += " (Leap)"
                if self._show_zodiac:
                    result += f" {zodiac['emoji']}"
            else:
                result = f"旧暦 {lunar_month}月"
                if is_leap:
                    result += "（閏）"
                result += f"{lunar_day}日"
                if self._show_zodiac:
                    result += f" {zodiac['emoji']}"

        else:  # numeric
            # Numeric format (same for all languages)
            if use_english:
                result = f"L{lunar_month:02d}/{lunar_day:02d}"
                if is_leap:
                    result += "*"
            else:
                result = f"旧{lunar_month:02d}/{lunar_day:02d}"
                if is_leap:
                    result += "閏"

        return result

    def _calculate_japanese_lunar_date(self, now: datetime) -> Dict[str, Any]:
        """Calculate the Japanese lunar date."""
        # Convert to configured timezone
        tz = self._get_timezone()
        japan_time = now.astimezone(tz)

        # If using JST, ensure we're getting Japan time
        if self._timezone == "Asia/Tokyo":
            japan_time = now.astimezone(ZoneInfo("Asia/Tokyo"))

        # Calculate lunar month and day
        lunar_month, lunar_day, is_leap = self._calculate_lunar_month_day(japan_time)

        # Calculate moon phase
        moon_age, moon_phase_ja, moon_phase_en = self._calculate_moon_phase(japan_time)

        # Get zodiac animal
        zodiac = self._get_zodiac_animal(japan_time.year)

        # Format the date
        formatted = self._format_lunar_date(
            lunar_month, lunar_day, moon_phase_ja, moon_phase_en,
            zodiac, japan_time, is_leap
        )

        result = {
            "lunar_month": lunar_month,
            "lunar_day": lunar_day,
            "is_leap_month": is_leap,
            "month_name_traditional": self._lunar_data["months"]["traditional"][lunar_month - 1],
            "month_name_modern": self._lunar_data["months"]["modern"][lunar_month - 1],
            "moon_age": round(moon_age, 1),
            "moon_phase_ja": moon_phase_ja,
            "moon_phase_en": moon_phase_en,
            "zodiac_ja": zodiac["ja"],
            "zodiac_en": zodiac["en"],
            "zodiac_emoji": zodiac["emoji"],
            "gregorian_date": f"{japan_time.year}/{japan_time.month:02d}/{japan_time.day:02d}",
            "formatted": formatted
        }

        # Add solar term if applicable
        if self._show_solar_terms:
            solar_term = self._get_solar_term(japan_time)
            if solar_term:
                result["solar_term_ja"] = solar_term["ja"]
                result["solar_term_en"] = solar_term["en"]

        # Add traditional event if applicable
        if self._show_traditional_events:
            event = self._get_traditional_event(lunar_month, lunar_day)
            if event:
                result["event_ja"] = event["ja"]
                result["event_en"] = event["en"]

        return result

    def update(self) -> None:
        """Update the sensor."""
        # Ensure options are loaded (in case async_added_to_hass hasn't run yet)
        if not self._options_loaded:
            self._load_options()

        now = datetime.now(timezone.utc)
        self._lunar_date = self._calculate_japanese_lunar_date(now)

        # Set state to formatted lunar date
        self._state = self._lunar_date["formatted"]

        _LOGGER.debug(f"Updated Japanese Lunar Calendar to {self._state}")

    @property
    def state(self) -> str:
        """Return the state of the sensor."""
        return self._state or "Unknown"

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return additional attributes."""
        if not self._lunar_date:
            return {}

        # Build attributes dictionary
        attrs = {
            "lunar_month": self._lunar_date.get("lunar_month"),
            "lunar_day": self._lunar_date.get("lunar_day"),
            "is_leap_month": self._lunar_date.get("is_leap_month"),
            "month_name_traditional": self._lunar_date.get("month_name_traditional"),
            "month_name_modern": self._lunar_date.get("month_name_modern"),
            "moon_age_days": self._lunar_date.get("moon_age"),
            "moon_phase_ja": self._lunar_date.get("moon_phase_ja"),
            "moon_phase_en": self._lunar_date.get("moon_phase_en"),
            "zodiac_ja": self._lunar_date.get("zodiac_ja"),
            "zodiac_en": self._lunar_date.get("zodiac_en"),
            "zodiac_emoji": self._lunar_date.get("zodiac_emoji"),
            "gregorian_date": self._lunar_date.get("gregorian_date"),
            "icon": self._attr_icon,
            "calendar_type": "Japanese Lunar Calendar",
            "accuracy": CALENDAR_INFO.get("accuracy", "traditional"),
            "reference": CALENDAR_INFO.get("reference_url"),
            "notes": self._translate("notes")
        }

        # Add optional attributes
        if "solar_term_ja" in self._lunar_date:
            attrs["solar_term_ja"] = self._lunar_date["solar_term_ja"]
            attrs["solar_term_en"] = self._lunar_date["solar_term_en"]

        if "event_ja" in self._lunar_date:
            attrs["traditional_event_ja"] = self._lunar_date["event_ja"]
            attrs["traditional_event_en"] = self._lunar_date["event_en"]

        # Add configuration state
        attrs["config_timezone"] = self._timezone
        attrs["config_display_language"] = self._display_language
        attrs["config_display_format"] = self._display_format
        attrs["config_show_moon_phase"] = self._show_moon_phase
        attrs["config_show_solar_terms"] = self._show_solar_terms
        attrs["config_show_traditional_events"] = self._show_traditional_events
        attrs["config_show_zodiac"] = self._show_zodiac

        return attrs


# ============================================
# MODULE EXPORTS
# ============================================

# Export the sensor class
__all__ = ["JapaneseLunarCalendarSensor"]
