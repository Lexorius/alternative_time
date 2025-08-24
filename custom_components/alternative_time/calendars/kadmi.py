"""Zoroastrian Kadmi Calendar Plugin for Alternative Time Systems.

Implements the reformed Parsi calendar introduced in 1746 CE, which is 30 days ahead of Shenshai.
This calendar also has 12 months of 30 days plus 5 Gatha days, totaling 365 days.

IMPORTANT: The Kadmi reform of 1746 was an attempt to "correct" a perceived month error.
This caused a significant schism in the Parsi community that persists to this day.
Like Shenshai, it has no leap years and continues to drift from the solar year.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import logging

try:
    from . import AlternativeTimeSensorBase
except ImportError:
    try:
        from sensor import AlternativeTimeSensorBase
    except ImportError:
        # Fallback for testing
        AlternativeTimeSensorBase = object

_LOGGER = logging.getLogger(__name__)

# Calendar metadata and configuration
CALENDAR_INFO = {
    "id": "kadmi",
    "version": "2.5.0",
    "name": {
        "en": "Kadmi Calendar (Zoroastrian)",
        "de": "Kadmi-Kalender (Zoroastrisch)",
        "es": "Calendario Kadmi (Zoroástrico)",
        "fr": "Calendrier Kadmi (Zoroastrien)",
        "it": "Calendario Kadmi (Zoroastriano)",
        "nl": "Kadmi Kalender (Zoroastrisch)",
        "pl": "Kalendarz Kadmi (Zoroastryjski)",
        "pt": "Calendário Kadmi (Zoroastriano)",
        "ru": "Календарь Кадми (Зороастрийский)",
        "ja": "カドミ暦（ゾロアスター教）",
        "zh": "卡德米历（琐罗亚斯德教）",
        "ko": "카드미 달력 (조로아스터교)"
    },
    "description": {
        "en": "Reformed Parsi calendar (1746), 30 days ahead of Shenshai, no leap years",
        "de": "Reformierter Parsi-Kalender (1746), 30 Tage vor Shenshai, keine Schaltjahre",
        "es": "Calendario Parsi reformado (1746), 30 días antes que Shenshai, sin años bisiestos",
        "fr": "Calendrier Parsi réformé (1746), 30 jours avant Shenshai, sans années bissextiles",
        "it": "Calendario Parsi riformato (1746), 30 giorni prima di Shenshai, senza anni bisestili",
        "nl": "Hervormde Parsi kalender (1746), 30 dagen voor Shenshai, geen schrikkeljaren",
        "pl": "Zreformowany kalendarz Parsi (1746), 30 dni przed Shenshai, bez lat przestępnych",
        "pt": "Calendário Parsi reformado (1746), 30 dias antes de Shenshai, sem anos bissextos",
        "ru": "Реформированный календарь парсов (1746), на 30 дней впереди Шеншай, без високосных лет",
        "ja": "改革パールシー暦（1746年）、シェンシャイより30日早い、閏年なし",
        "zh": "改革帕西历（1746年），比申沙历早30天，无闰年",
        "ko": "개혁 파르시 달력 (1746), 셴샤이보다 30일 앞, 윤년 없음"
    },
    "category": "religious",
    "update_interval": 3600,
    "accuracy": "day",
    "icon": "mdi:fire",
    "reference_url": "https://en.wikipedia.org/wiki/Zoroastrian_calendar#Kadmi_calendar",
    
    # Important historical and community context - FIXED: Added closing quote and brace
    "disclaimer": {
        "en": "⚠️ REFORMED CALENDAR (1746): The Kadmi reform attempted to 'correct' a perceived calendrical error by moving the calendar 30 days forward. This created a SECOND faction in the Parsi community that persists today. Used by ~20% of Parsis. The community remains divided between Shenshai (traditional) and Kadmi (reformed), with both calendars still drifting from the solar year.",
        "de": "⚠️ REFORMIERTER KALENDER (1746): Die Kadmi-Reform versuchte einen wahrgenommenen kalendarischen Fehler zu 'korrigieren', indem der Kalender 30 Tage nach vorne verschoben wurde. Dies schuf eine ZWEITE Fraktion in der Parsi-Gemeinde, die bis heute besteht. Wird von ~20% der Parsis verwendet. Die Gemeinde bleibt zwischen Shenshai (traditionell) und Kadmi (reformiert) geteilt, wobei beide Kalender weiterhin vom Sonnenjahr abweichen.",
        "es": "⚠️ CALENDARIO REFORMADO (1746): La reforma Kadmi intentó 'corregir' un error calendárico percibido moviendo el calendario 30 días hacia adelante. Esto creó una SEGUNDA facción en la comunidad Parsi que persiste hoy. Usado por ~20% de los Parsis. La comunidad permanece dividida entre Shenshai (tradicional) y Kadmi (reformado), con ambos calendarios aún derivando del año solar.",
        "fr": "⚠️ CALENDRIER RÉFORMÉ (1746): La réforme Kadmi a tenté de 'corriger' une erreur calendaire perçue en avançant le calendrier de 30 jours. Cela a créé une DEUXIÈME faction dans la communauté Parsi qui persiste aujourd'hui. Utilisé par ~20% des Parsis. La communauté reste divisée entre Shenshai (traditionnel) et Kadmi (réformé), les deux calendriers dérivant toujours de l'année solaire.",
        "it": "⚠️ CALENDARIO RIFORMATO (1746): La riforma Kadmi tentò di 'correggere' un errore calendariale percepito spostando il calendario 30 giorni avanti. Questo creò una SECONDA fazione nella comunità Parsi che persiste oggi. Usato da ~20% dei Parsi. La comunità rimane divisa tra Shenshai (tradizionale) e Kadmi (riformato), con entrambi i calendari che ancora derivano dall'anno solare.",
        "nl": "⚠️ HERVORMD KALENDER (1746): De Kadmi-hervorming probeerde een vermeende kalenderfout te 'corrigeren' door de kalender 30 dagen vooruit te schuiven. Dit creëerde een TWEEDE factie in de Parsi-gemeenschap die vandaag voortduurt. Gebruikt door ~20% van de Parsi's. De gemeenschap blijft verdeeld tussen Shenshai (traditioneel) en Kadmi (hervormd), waarbij beide kalenders nog steeds afdrijven van het zonnejaar.",
        "pl": "⚠️ KALENDARZ ZREFORMOWANY (1746): Reforma Kadmi próbowała 'naprawić' postrzegany błąd kalendarzowy przesuwając kalendarz o 30 dni do przodu. To stworzyło DRUGĄ frakcję w społeczności Parsi, która trwa do dziś. Używany przez ~20% Parsów. Społeczność pozostaje podzielona między Shenshai (tradycyjny) i Kadmi (zreformowany), przy czym oba kalendarze nadal dryfują od roku słonecznego.",
        "pt": "⚠️ CALENDÁRIO REFORMADO (1746): A reforma Kadmi tentou 'corrigir' um erro calendárico percebido movendo o calendário 30 dias para frente. Isso criou uma SEGUNDA facção na comunidade Parsi que persiste hoje. Usado por ~20% dos Parsis. A comunidade permanece dividida entre Shenshai (tradicional) e Kadmi (reformado), com ambos os calendários ainda derivando do ano solar.",
        "ru": "⚠️ РЕФОРМИРОВАННЫЙ КАЛЕНДАРЬ (1746): Реформа Кадми попыталась 'исправить' воспринимаемую календарную ошибку, сдвинув календарь на 30 дней вперед. Это создало ВТОРУЮ фракцию в общине парсов, которая существует до сих пор. Используется ~20% парсов. Община остается разделенной между Шеншай (традиционный) и Кадми (реформированный), причем оба календаря продолжают отклоняться от солнечного года.",
        "ja": "⚠️ 改革暦（1746年）：カドミ改革は、暦を30日前進させることで認識された暦の誤りを「修正」しようとしました。これはパールシー共同体に第二の派閥を作り、今日まで続いています。パールシーの約20％が使用。共同体はシェンシャイ（伝統的）とカドミ（改革）の間で分裂したままで、両方の暦が太陽年からずれ続けています。",
        "zh": "⚠️ 改革历法（1746年）：卡德米改革试图通过将日历向前移动30天来"纠正"感知的历法错误。这在帕西社区中创建了第二个派系，至今仍然存在。约20%的帕西人使用。社区仍然分裂在申沙（传统）和卡德米（改革）之间，两个日历都继续偏离太阳年。",
        "ko": "⚠️ 개혁 달력 (1746년): 카드미 개혁은 달력을 30일 앞으로 이동시켜 인식된 달력 오류를 '수정'하려고 시도했습니다. 이것은 오늘날까지 지속되는 파르시 공동체에 두 번째 파벌을 만들었습니다. 파르시의 약 20%가 사용. 공동체는 셴샤이(전통)와 카드미(개혁) 사이에 분열되어 있으며, 두 달력 모두 태양년에서 계속 표류하고 있습니다."
    },
    
    # Configuration options
    "config_options": {
        "show_yazata": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show Yazata (Guardian Angel)",
                "de": "Zeige Yazata (Schutzengel)",
                "es": "Mostrar Yazata (Ángel Guardián)",
                "fr": "Afficher Yazata (Ange Gardien)",
                "it": "Mostra Yazata (Angelo Custode)",
                "nl": "Toon Yazata (Beschermengel)",
                "pl": "Pokaż Yazata (Anioł Stróż)",
                "pt": "Mostrar Yazata (Anjo Guardião)",
                "ru": "Показать Язата (Ангел-хранитель)",
                "ja": "ヤザタ（守護天使）を表示",
                "zh": "显示亚扎塔（守护天使）",
                "ko": "야자타 (수호천사) 표시"
            },
            "description": {
                "en": "Display the Yazata (divine being) associated with each day",
                "de": "Zeigt das Yazata (göttliches Wesen) das mit jedem Tag verbunden ist",
                "es": "Muestra el Yazata (ser divino) asociado con cada día",
                "fr": "Affiche le Yazata (être divin) associé à chaque jour",
                "it": "Visualizza lo Yazata (essere divino) associato a ogni giorno",
                "nl": "Toont de Yazata (goddelijk wezen) geassocieerd met elke dag",
                "pl": "Wyświetla Yazata (boską istotę) związaną z każdym dniem",
                "pt": "Exibe o Yazata (ser divino) associado a cada dia",
                "ru": "Отображает Язата (божественное существо), связанное с каждым днем",
                "ja": "各日に関連するヤザタ（神聖な存在）を表示",
                "zh": "显示与每天相关的亚扎塔（神圣存在）",
                "ko": "매일과 관련된 야자타 (신성한 존재) 표시"
            }
        },
        "show_shenshai_difference": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show Shenshai Difference",
                "de": "Zeige Shenshai-Differenz",
                "es": "Mostrar Diferencia Shenshai",
                "fr": "Afficher la Différence Shenshai",
                "it": "Mostra Differenza Shenshai",
                "nl": "Toon Shenshai Verschil",
                "pl": "Pokaż Różnicę Shenshai",
                "pt": "Mostrar Diferença Shenshai",
                "ru": "Показать разницу с Шеншай",
                "ja": "シェンシャイとの差を表示",
                "zh": "显示申沙差异",
                "ko": "셴샤이 차이 표시"
            },
            "description": {
                "en": "Display that Kadmi is 30 days ahead of Shenshai calendar",
                "de": "Zeigt dass Kadmi 30 Tage vor dem Shenshai-Kalender liegt",
                "es": "Muestra que Kadmi está 30 días adelante del calendario Shenshai",
                "fr": "Affiche que Kadmi est 30 jours en avance sur le calendrier Shenshai",
                "it": "Visualizza che Kadmi è 30 giorni avanti rispetto al calendario Shenshai",
                "nl": "Toont dat Kadmi 30 dagen voor ligt op de Shenshai kalender",
                "pl": "Wyświetla że Kadmi jest 30 dni przed kalendarzem Shenshai",
                "pt": "Exibe que Kadmi está 30 dias à frente do calendário Shenshai",
                "ru": "Отображает что Кадми на 30 дней впереди календаря Шеншай",
                "ja": "カドミがシェンシャイ暦より30日進んでいることを表示",
                "zh": "显示卡德米比申沙历提前30天",
                "ko": "카드미가 셴샤이 달력보다 30일 앞서 있음을 표시"
            }
        },
        "show_schism_note": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show Historical Schism Note",
                "de": "Historische Schisma-Notiz anzeigen",
                "es": "Mostrar nota del cisma histórico",
                "fr": "Afficher la note du schisme historique",
                "it": "Mostra nota dello scisma storico",
                "nl": "Toon historische schisma notitie",
                "pl": "Pokaż notę o schizmie historycznej",
                "pt": "Mostrar nota do cisma histórico",
                "ru": "Показать заметку об историческом расколе",
                "ja": "歴史的分裂の注記を表示",
                "zh": "显示历史分裂注释",
                "ko": "역사적 분열 메모 표시"
            },
            "description": {
                "en": "Display information about the 1746 calendar reform controversy",
                "de": "Zeigt Informationen über die Kalenderreform-Kontroverse von 1746",
                "es": "Muestra información sobre la controversia de la reforma del calendario de 1746",
                "fr": "Affiche des informations sur la controverse de la réforme du calendrier de 1746",
                "it": "Visualizza informazioni sulla controversia della riforma del calendario del 1746",
                "nl": "Toont informatie over de kalenderhervorming controverse van 1746",
                "pl": "Wyświetla informacje o kontrowersji reformy kalendarza z 1746",
                "pt": "Exibe informações sobre a controvérsia da reforma do calendário de 1746",
                "ru": "Отображает информацию о споре о календарной реформе 1746 года",
                "ja": "1746年の暦改革論争に関する情報を表示",
                "zh": "显示关于1746年历法改革争议的信息",
                "ko": "1746년 달력 개혁 논란에 대한 정보 표시"
            }
        },
        "show_festivals": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show Festivals",
                "de": "Feste anzeigen",
                "es": "Mostrar Festivales",
                "fr": "Afficher les Festivals",
                "it": "Mostra Festival",
                "nl": "Toon Festivals",
                "pl": "Pokaż Festiwale",
                "pt": "Mostrar Festivais",
                "ru": "Показать праздники",
                "ja": "祭りを表示",
                "zh": "显示节日",
                "ko": "축제 표시"
            },
            "description": {
                "en": "Display Zoroastrian festivals and holy days",
                "de": "Zeigt zoroastrische Feste und heilige Tage",
                "es": "Muestra festivales y días sagrados zoroástricos",
                "fr": "Affiche les festivals et jours sacrés zoroastriens",
                "it": "Visualizza festival e giorni sacri zoroastriani",
                "nl": "Toont Zoroastrische festivals en heilige dagen",
                "pl": "Wyświetla zoroastryjskie festiwale i święte dni",
                "pt": "Exibe festivais e dias sagrados zoroastrianos",
                "ru": "Отображает зороастрийские праздники и святые дни",
                "ja": "ゾロアスター教の祭りと聖日を表示",
                "zh": "显示琐罗亚斯德教节日和圣日",
                "ko": "조로아스터교 축제와 성일 표시"
            }
        }
    },
    
    # Kadmi calendar data
    "kadmi_data": {
        # 12 months of 30 days each
        "months": [
            {"name": "Farvardin", "days": 30, "meaning": "Guardian Spirits"},
            {"name": "Ardibehesht", "days": 30, "meaning": "Best Truth"},
            {"name": "Khordad", "days": 30, "meaning": "Perfection"},
            {"name": "Tir", "days": 30, "meaning": "Sirius"},
            {"name": "Amardad", "days": 30, "meaning": "Immortality"},
            {"name": "Shahrivar", "days": 30, "meaning": "Desirable Kingdom"},
            {"name": "Mehr", "days": 30, "meaning": "Covenant"},
            {"name": "Aban", "days": 30, "meaning": "Waters"},
            {"name": "Azar", "days": 30, "meaning": "Fire"},
            {"name": "Dey", "days": 30, "meaning": "Creator"},
            {"name": "Bahman", "days": 30, "meaning": "Good Mind"},
            {"name": "Esfand", "days": 30, "meaning": "Holy Devotion"}
        ],
        
        # 5 Gatha days at year end
        "gatha_days": [
            {"name": "Ahunavad", "meaning": "Possessing Ahu"},
            {"name": "Ushtavad", "meaning": "Possessing Happiness"},
            {"name": "Spentomad", "meaning": "Possessing Holy Devotion"},
            {"name": "Vohukhshathra", "meaning": "Possessing Good Dominion"},
            {"name": "Vahishtoisht", "meaning": "Best Righteousness"}
        ],
        
        # Yazatas (30 divine beings for each day)
        "yazatas": [
            {"day": 1, "name": "Ohrmazd", "meaning": "Lord of Wisdom"},
            {"day": 2, "name": "Bahman", "meaning": "Good Mind"},
            {"day": 3, "name": "Ardibehesht", "meaning": "Best Truth"},
            {"day": 4, "name": "Shahrivar", "meaning": "Desirable Kingdom"},
            {"day": 5, "name": "Esfand", "meaning": "Holy Devotion"},
            {"day": 6, "name": "Khordad", "meaning": "Perfection"},
            {"day": 7, "name": "Amardad", "meaning": "Immortality"},
            {"day": 8, "name": "Dey-pa-Adar", "meaning": "Creator of Fire"},
            {"day": 9, "name": "Azar", "meaning": "Fire"},
            {"day": 10, "name": "Aban", "meaning": "Waters"},
            {"day": 11, "name": "Khorshed", "meaning": "Sun"},
            {"day": 12, "name": "Mohor", "meaning": "Moon"},
            {"day": 13, "name": "Tir", "meaning": "Sirius"},
            {"day": 14, "name": "Gosh", "meaning": "Cattle"},
            {"day": 15, "name": "Dey-pa-Mehr", "meaning": "Creator of Covenant"},
            {"day": 16, "name": "Mehr", "meaning": "Covenant"},
            {"day": 17, "name": "Srosh", "meaning": "Obedience"},
            {"day": 18, "name": "Rashnu", "meaning": "Justice"},
            {"day": 19, "name": "Fravardin", "meaning": "Guardian Spirits"},
            {"day": 20, "name": "Bahram", "meaning": "Victory"},
            {"day": 21, "name": "Ram", "meaning": "Joy"},
            {"day": 22, "name": "Govad", "meaning": "Wind"},
            {"day": 23, "name": "Dey-pa-Din", "meaning": "Creator of Religion"},
            {"day": 24, "name": "Din", "meaning": "Religion"},
            {"day": 25, "name": "Ashishvangh", "meaning": "Blessings"},
            {"day": 26, "name": "Ashtad", "meaning": "Justice"},
            {"day": 27, "name": "Asman", "meaning": "Sky"},
            {"day": 28, "name": "Zamyad", "meaning": "Earth"},
            {"day": 29, "name": "Mahraspand", "meaning": "Holy Word"},
            {"day": 30, "name": "Aneran", "meaning": "Endless Light"}
        ],
        
        # Festivals (same as Shenshai)
        "festivals": {
            "Farvardin 19": "Fravardingan (All Souls)",
            "Ardibehesht 3": "Ardibehesht Festival",
            "Khordad 6": "Khordad Sal (Birthday of Zoroaster)",
            "Tir 13": "Tiragan (Rain Festival)",
            "Amardad 7": "Amardadgan",
            "Shahrivar 4": "Shahrivargan",
            "Mehr 16": "Mehragan (Harvest Festival)",
            "Aban 10": "Abangan (Water Festival)",
            "Azar 9": "Azargan (Fire Festival)",
            "Dey 1": "Deygan",
            "Dey 8": "Dey-pa-Adar Festival",
            "Dey 15": "Dey-pa-Mehr Festival",
            "Dey 23": "Dey-pa-Din Festival",
            "Bahman 2": "Bahmanagan",
            "Esfand 5": "Esfandgan",
            "Gatha 5": "Pateti (Day of Repentance)"
        },
        
        # Reference epoch - Kadmi is 30 days ahead of Shenshai
        # Kadmi New Year 2024 = July 16, 2024 (30 days before Shenshai's August 15)
        "epoch": {
            "gregorian_date": datetime(2024, 7, 16),
            "kadmi_year": 1393,  # Year 1393 Y.Z. (Yazdegerdi)
            "note": "30 days ahead of Shenshai reckoning"
        },
        
        # Historical context of the schism
        "schism_history": {
            "reform_year": 1746,
            "reform_location": "Surat, India",
            "reformer": "Jamasp Peshotan Velati",
            "reasoning": "Believed a month intercalation was missed in 1129 CE",
            "opposition": "Majority of Parsis rejected the change",
            "result": "Permanent split: ~20% Kadmi, ~75% Shenshai, ~5% later Fasli",
            "current_status": "Both communities maintain separate fire temples and priests",
            "difference": "Kadmi always 30 days ahead of Shenshai",
            "irony": "Both calendars drift equally - reform didn't fix the solar year problem"
        }
    }
}

# Update interval for this sensor
UPDATE_INTERVAL = CALENDAR_INFO["update_interval"]


class KadmiCalendarSensor(AlternativeTimeSensorBase if AlternativeTimeSensorBase != object else object):
    """Sensor for Zoroastrian Kadmi Calendar."""
    
    # Class-level update interval
    UPDATE_INTERVAL = UPDATE_INTERVAL
    
    def __init__(self, hass, entry_data: Dict[str, Any], name: str):
        """Initialize the Kadmi calendar sensor."""
        if AlternativeTimeSensorBase != object:
            super().__init__(hass, entry_data, name, CALENDAR_INFO)
        else:
            # Fallback initialization
            self._hass = hass
            self._entry_data = entry_data
            self._base_name = name
            self._calendar_info = CALENDAR_INFO
            
        self._state = None
        self._kadmi_calendar = {}
        
        # Default configuration options
        self._show_yazata = True
        self._show_shenshai_difference = True
        self._show_schism_note = True
        self._show_festivals = True
        
        # Calendar data
        self._kadmi_data = CALENDAR_INFO["kadmi_data"]
        
        # Track if options have been loaded
        self._options_loaded = False
        
        # Set sensor name
        calendar_name = self._translate('name', 'Kadmi Calendar') if hasattr(self, '_translate') else 'Kadmi Calendar'
        if hasattr(self, '_attr_name'):
            self._attr_name = f"{name} {calendar_name}"
        else:
            self._name = f"{name} {calendar_name}"
            
        if hasattr(self, '_attr_unique_id'):
            self._attr_unique_id = f"{name}_kadmi_calendar"
        if hasattr(self, '_attr_icon'):
            self._attr_icon = CALENDAR_INFO.get("icon", "mdi:fire")
        
        _LOGGER.debug(f"Initialized Kadmi Calendar sensor: {name}")
    
    def _load_options(self) -> None:
        """Load configuration options from config entry."""
        if self._options_loaded:
            return
            
        try:
            if hasattr(self, 'get_plugin_options'):
                options = self.get_plugin_options()
            else:
                calendar_options = self._entry_data.get("calendar_options", {})
                options = calendar_options.get("kadmi", {})
                
            if options:
                # Update configuration from plugin options
                self._show_yazata = options.get("show_yazata", self._show_yazata)
                self._show_shenshai_difference = options.get("show_shenshai_difference", self._show_shenshai_difference)
                self._show_schism_note = options.get("show_schism_note", self._show_schism_note)
                self._show_festivals = options.get("show_festivals", self._show_festivals)
                
                _LOGGER.debug(f"Kadmi sensor loaded options: yazata={self._show_yazata}, "
                            f"difference={self._show_shenshai_difference}, schism={self._show_schism_note}, "
                            f"festivals={self._show_festivals}")
            else:
                _LOGGER.debug("Kadmi sensor using default options - no custom options found")
                
            self._options_loaded = True
        except Exception as e:
            _LOGGER.debug(f"Kadmi sensor could not load options yet: {e}")
    
    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        if hasattr(self, '_attr_name'):
            return self._attr_name
        return getattr(self, '_name', f"{self._base_name} Kadmi Calendar")
    
    @property
    def unique_id(self) -> str:
        """Return unique ID for the sensor."""
        if hasattr(self, '_attr_unique_id'):
            return self._attr_unique_id
        base_id = self._entry_data.get('entry_id', 'kadmi')
        return f"{base_id}_kadmi_calendar"
    
    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes."""
        attrs = {}
        
        # Get parent attributes if available
        if hasattr(super(), 'extra_state_attributes'):
            attrs = super().extra_state_attributes
        
        # Add Kadmi-specific attributes
        if self._kadmi_calendar:
            attrs.update(self._kadmi_calendar)
            
            # Add description in user's language
            if hasattr(self, '_translate'):
                attrs["description"] = self._translate('description')
                attrs["disclaimer"] = self._translate('disclaimer')
            
            # Add reference
            attrs["reference"] = CALENDAR_INFO.get('reference_url', '')
            
            # Add schism history if enabled
            if self._show_schism_note:
                attrs["schism_history"] = self._kadmi_data["schism_history"]
            
            # Add configuration status
            attrs["config"] = {
                "show_yazata": self._show_yazata,
                "show_shenshai_difference": self._show_shenshai_difference,
                "show_schism_note": self._show_schism_note,
                "show_festivals": self._show_festivals
            }
        
        return attrs
    
    def _calculate_kadmi_date(self, gregorian_date: datetime) -> tuple:
        """Calculate Kadmi date from Gregorian date.
        Returns: (year, month_index, day, is_gatha_day)
        """
        epoch = self._kadmi_data["epoch"]
        epoch_date = epoch["gregorian_date"]
        epoch_year = epoch["kadmi_year"]
        
        # Calculate days since epoch
        delta = gregorian_date - epoch_date
        days_since_epoch = delta.days
        
        # Calculate Kadmi year
        years_passed = days_since_epoch // 365
        year = epoch_year + years_passed
        
        # Calculate day in year
        day_in_year = days_since_epoch % 365 + 1
        
        # Check if it's a Gatha day (last 5 days)
        if day_in_year > 360:
            # Gatha days
            gatha_day = day_in_year - 360
            return year, gatha_day - 1, gatha_day, True
        else:
            # Regular month/day
            month_idx = (day_in_year - 1) // 30
            day = ((day_in_year - 1) % 30) + 1
            return year, month_idx, day, False
    
    def _get_yazata(self, day: int) -> Dict[str, str]:
        """Get Yazata for a specific day."""
        for yazata in self._kadmi_data["yazatas"]:
            if yazata["day"] == day:
                return yazata
        return {"name": "Unknown", "meaning": "Unknown"}
    
    def _check_festival(self, month_name: str, day: int, is_gatha: bool) -> Optional[str]:
        """Check if current date is a festival."""
        if is_gatha:
            if day == 5:
                return self._kadmi_data["festivals"].get("Gatha 5", None)
        else:
            date_key = f"{month_name} {day}"
            return self._kadmi_data["festivals"].get(date_key, None)
    
    def _calculate_shenshai_equivalent(self, gregorian_date: datetime) -> str:
        """Calculate what the date would be in Shenshai calendar."""
        # Shenshai is 30 days behind Kadmi
        shenshai_date = gregorian_date + timedelta(days=30)
        
        # Simple calculation for display
        year, month_idx, day, is_gatha = self._calculate_kadmi_date(shenshai_date)
        
        if is_gatha:
            gatha = self._kadmi_data["gatha_days"][month_idx]
            return f"{day} {gatha['name']}"
        else:
            month = self._kadmi_data["months"][month_idx]
            return f"{day} {month['name']}"
    
    def _format_kadmi_date(self, gregorian_date: datetime) -> str:
        """Format the Kadmi date."""
        # Reload options
        self._load_options()
        
        # Calculate date
        year, month_idx, day, is_gatha = self._calculate_kadmi_date(gregorian_date)
        
        # Format based on whether it's a Gatha day
        if is_gatha:
            gatha = self._kadmi_data["gatha_days"][month_idx]
            result = f"{day} {gatha['name']}, {year} Y.Z."
        else:
            month = self._kadmi_data["months"][month_idx]
            result = f"{day} {month['name']}, {year} Y.Z."
        
        # Add Yazata if requested and not Gatha day
        if self._show_yazata and not is_gatha:
            yazata = self._get_yazata(day)
            result += f" ({yazata['name']})"
        
        # Add difference from Shenshai if requested
        if self._show_shenshai_difference:
            result += " [+30 days vs Shenshai]"
        
        # Add schism note if requested
        if self._show_schism_note:
            result += " [Reformed 1746]"
        
        return result
    
    def _update(self):
        """Update the sensor state."""
        gregorian_date = datetime.now()
        
        try:
            # Format the main date string
            kadmi_date = self._format_kadmi_date(gregorian_date)
            
            # Calculate date components
            year, month_idx, day, is_gatha = self._calculate_kadmi_date(gregorian_date)
            
            # Build attribute data
            self._kadmi_calendar = {
                "formatted_date": kadmi_date,
                "year": {
                    "yazdegerdi": year,
                    "gregorian": gregorian_date.year,
                    "era": "Y.Z. (Yazdegerdi Era)"
                },
                "is_gatha_day": is_gatha,
                "reform_status": {
                    "type": "Kadmi (Reformed)",
                    "year_of_reform": 1746,
                    "days_ahead_of_shenshai": 30,
                    "percentage_of_community": "~20% of Parsis"
                }
            }
            
            if is_gatha:
                # Gatha day information
                gatha = self._kadmi_data["gatha_days"][month_idx]
                self._kadmi_calendar["gatha"] = {
                    "day": day,
                    "name": gatha["name"],
                    "meaning": gatha["meaning"],
                    "total_gatha_days": 5
                }
            else:
                # Regular month information
                month = self._kadmi_data["months"][month_idx]
                self._kadmi_calendar["month"] = {
                    "name": month["name"],
                    "meaning": month["meaning"],
                    "number": month_idx + 1,
                    "days": month["days"]
                }
                self._kadmi_calendar["day"] = {
                    "number": day,
                    "total_days": 30
                }
                
                # Add Yazata information
                if self._show_yazata:
                    yazata = self._get_yazata(day)
                    self._kadmi_calendar["yazata"] = {
                        "name": yazata["name"],
                        "meaning": yazata["meaning"],
                        "day_dedication": day
                    }
                
                # Check for festival
                if self._show_festivals:
                    festival = self._check_festival(month["name"], day, False)
                    if festival:
                        self._kadmi_calendar["festival"] = festival
            
            # Add Shenshai equivalent if requested
            if self._show_shenshai_difference:
                shenshai_equiv = self._calculate_shenshai_equivalent(gregorian_date)
                self._kadmi_calendar["shenshai_equivalent"] = {
                    "date": shenshai_equiv,
                    "difference_days": 30,
                    "note": "Kadmi is always 30 days ahead of Shenshai"
                }
            
            # Calculate days until New Year (Nowruz)
            days_in_year = (day if not is_gatha else 360 + day)
            days_to_nowruz = 365 - days_in_year
            self._kadmi_calendar["days_to_nowruz"] = days_to_nowruz
            
            # Calculate drift from solar year (same as Shenshai)
            years_since_1746 = gregorian_date.year - 1746
            drift_days = int(years_since_1746 * 0.2422)
            self._kadmi_calendar["solar_drift"] = {
                "days": drift_days,
                "note": "Drifts same as Shenshai despite reform",
                "irony": "Reform moved calendar but didn't add leap years"
            }
            
            # Set state
            self._state = kadmi_date
            
        except Exception as e:
            _LOGGER.error(f"Error calculating Kadmi calendar: {e}", exc_info=True)
            self._state = "Error"
            self._kadmi_calendar = {"error": str(e)}
    
    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        if hasattr(super(), 'async_added_to_hass'):
            await super().async_added_to_hass()
        
        # Try to load options now that IDs should be set
        self._load_options()
    
    async def async_update(self):
        """Async update wrapper."""
        if hasattr(super(), 'async_update'):
            await super().async_update()
        else:
            await self._hass.async_add_executor_job(self._update)
    
    def get_calendar_metadata(self) -> Dict[str, Any]:
        """Return calendar metadata."""
        return CALENDAR_INFO


# Module-level function for calendar discovery
def get_calendar_info() -> Dict[str, Any]:
    """Get calendar information for discovery."""
    return CALENDAR_INFO


# Export the sensor class
__all__ = ["KadmiCalendarSensor", "CALENDAR_INFO", "UPDATE_INTERVAL"]