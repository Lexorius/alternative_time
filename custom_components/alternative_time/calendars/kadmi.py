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

from ..sensor_base import AlternativeTimeSensorBase

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
    
    # Important historical and community context
    "disclaimer": {
        "en": "⚠️ REFORMED CALENDAR (1746): The Kadmi reform attempted to 'correct' a perceived calendrical error by moving the calendar 30 days forward. This caused a MAJOR SCHISM in the Parsi community between Kadmis and Shenshais that continues today. Both calendars drift equally from the solar year. The reform was based on disputed historical interpretations.",
        "de": "⚠️ REFORMIERTER KALENDER (1746): Die Kadmi-Reform versuchte einen vermeintlichen Kalenderfehler zu 'korrigieren' durch Vorverlegung um 30 Tage. Dies verursachte ein GROSSES SCHISMA in der Parsi-Gemeinde zwischen Kadmis und Shenshais, das bis heute besteht. Beide Kalender driften gleichermaßen vom Sonnenjahr. Die Reform basierte auf umstrittenen historischen Interpretationen.",
        "es": "⚠️ CALENDARIO REFORMADO (1746): La reforma Kadmi intentó 'corregir' un error calendárico percibido adelantando el calendario 30 días. Esto causó un GRAN CISMA en la comunidad Parsi entre Kadmis y Shenshais que continúa hoy. Ambos calendarios derivan igualmente del año solar. La reforma se basó en interpretaciones históricas disputadas.",
        "fr": "⚠️ CALENDRIER RÉFORMÉ (1746): La réforme Kadmi a tenté de 'corriger' une erreur calendaire perçue en avançant le calendrier de 30 jours. Cela a causé un SCHISME MAJEUR dans la communauté Parsi entre Kadmis et Shenshais qui persiste aujourd'hui. Les deux calendriers dérivent également de l'année solaire. La réforme était basée sur des interprétations historiques contestées.",
        "it": "⚠️ CALENDARIO RIFORMATO (1746): La riforma Kadmi tentò di 'correggere' un errore calendariale percepito spostando il calendario 30 giorni avanti. Questo causò un GRANDE SCISMA nella comunità Parsi tra Kadmi e Shenshai che continua oggi. Entrambi i calendari derivano ugualmente dall'anno solare. La riforma si basava su interpretazioni storiche contestate.",
        "nl": "⚠️ HERVORMDE KALENDER (1746): De Kadmi-hervorming probeerde een vermeende kalenderfout te 'corrigeren' door de kalender 30 dagen vooruit te zetten. Dit veroorzaakte een GROOT SCHISMA in de Parsi-gemeenschap tussen Kadmi's en Shenshai's dat vandaag voortduurt. Beide kalenders drijven evenveel af van het zonnejaar. De hervorming was gebaseerd op betwiste historische interpretaties.",
        "pl": "⚠️ KALENDARZ ZREFORMOWANY (1746): Reforma Kadmi próbowała 'naprawić' postrzegany błąd kalendarzowy przesuwając kalendarz o 30 dni do przodu. To spowodowało WIELKĄ SCHIZMĘ w społeczności Parsi między Kadmi i Shenshai, która trwa do dziś. Oba kalendarze dryfują jednakowo od roku słonecznego. Reforma opierała się na spornych interpretacjach historycznych.",
        "pt": "⚠️ CALENDÁRIO REFORMADO (1746): A reforma Kadmi tentou 'corrigir' um erro calendárico percebido avançando o calendário 30 dias. Isso causou um GRANDE CISMA na comunidade Parsi entre Kadmis e Shenshais que continua hoje. Ambos os calendários derivam igualmente do ano solar. A reforma foi baseada em interpretações históricas disputadas.",
        "ru": "⚠️ РЕФОРМИРОВАННЫЙ КАЛЕНДАРЬ (1746): Реформа Кадми попыталась 'исправить' предполагаемую календарную ошибку, сдвинув календарь на 30 дней вперед. Это вызвало БОЛЬШОЙ РАСКОЛ в общине парсов между кадми и шеншай, который продолжается сегодня. Оба календаря одинаково дрейфуют от солнечного года. Реформа основывалась на спорных исторических интерпретациях.",
        "ja": "⚠️ 改革暦（1746年）：カドミ改革は認識された暦の誤りを「修正」しようと暦を30日進めました。これによりパールシー共同体にカドミとシェンシャイの間で今日まで続く大分裂が起こりました。両暦とも太陽年から同様にずれます。改革は論争のある歴史的解釈に基づいていました。",
        "zh": "⚠️ 改革历法（1746年）：卡德米改革试图通过将日历提前30天来"纠正"感知的历法错误。这在帕西社区的卡德米派和申沙派之间造成了持续至今的重大分裂。两种历法都同样偏离太阳年。改革基于有争议的历史解释。",
        "ko": "⚠️ 개혁 달력 (1746): 카드미 개혁은 인식된 달력 오류를 '수정'하려고 달력을 30일 앞당겼습니다. 이는 오늘날까지 계속되는 카드미와 셴샤이 사이의 파르시 공동체 대분열을 일으켰습니다. 두 달력 모두 태양년에서 동일하게 벗어납니다. 개혁은 논란이 있는 역사적 해석에 기반했습니다."
    },
    
    # Configuration options for this calendar
    "config_options": {
        "show_yazata": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show Day Dedication (Yazata)",
                "de": "Tageswidmung zeigen (Yazata)",
                "es": "Mostrar dedicación del día (Yazata)",
                "fr": "Afficher la dédicace du jour (Yazata)",
                "it": "Mostra dedica del giorno (Yazata)",
                "nl": "Toon dagwijding (Yazata)",
                "pl": "Pokaż dedykację dnia (Yazata)",
                "pt": "Mostrar dedicação do dia (Yazata)",
                "ru": "Показать посвящение дня (Язата)",
                "ja": "日の献身を表示（ヤザタ）",
                "zh": "显示日奉献（亚扎塔）",
                "ko": "일 헌정 표시 (야자타)"
            }
        },
        "show_shenshai_difference": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show Difference from Shenshai",
                "de": "Unterschied zu Shenshai anzeigen",
                "es": "Mostrar diferencia con Shenshai",
                "fr": "Afficher la différence avec Shenshai",
                "it": "Mostra differenza da Shenshai",
                "nl": "Toon verschil met Shenshai",
                "pl": "Pokaż różnicę od Shenshai",
                "pt": "Mostrar diferença de Shenshai",
                "ru": "Показать разницу с Шеншай",
                "ja": "シェンシャイとの差を表示",
                "zh": "显示与申沙的差异",
                "ko": "셴샤이와의 차이 표시"
            },
            "description": {
                "en": "Display that Kadmi is 30 days ahead of Shenshai calendar",
                "de": "Zeigt dass Kadmi 30 Tage vor dem Shenshai-Kalender liegt",
                "es": "Muestra que Kadmi está 30 días adelante del calendario Shenshai",
                "fr": "Affiche que Kadmi est 30 jours en avance sur le calendrier Shenshai"
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
                "fr": "Affiche des informations sur la controverse de la réforme du calendrier de 1746"
            }
        },
        "show_festivals": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show Religious Festivals",
                "de": "Religiöse Feste anzeigen",
                "es": "Mostrar festivales religiosos",
                "fr": "Afficher les fêtes religieuses",
                "it": "Mostra feste religiose",
                "nl": "Toon religieuze festivals",
                "pl": "Pokaż święta religijne",
                "pt": "Mostrar festivais religiosos",
                "ru": "Показать религиозные праздники",
                "ja": "宗教祭を表示",
                "zh": "显示宗教节日",
                "ko": "종교 축제 표시"
            }
        }
    },
    
    # Kadmi calendar data (same structure as Shenshai, but different epoch)
    "kadmi_data": {
        # 12 months of 30 days each (identical to Shenshai)
        "months": [
            {"name": "Farvardin", "meaning": "Guardian Spirits", "days": 30},
            {"name": "Ardibehesht", "meaning": "Best Righteousness", "days": 30},
            {"name": "Khordad", "meaning": "Perfection/Health", "days": 30},
            {"name": "Tir", "meaning": "Sirius/Rain", "days": 30},
            {"name": "Amardad", "meaning": "Immortality", "days": 30},
            {"name": "Shahrivar", "meaning": "Desirable Dominion", "days": 30},
            {"name": "Mehr", "meaning": "Covenant/Sun", "days": 30},
            {"name": "Aban", "meaning": "Waters", "days": 30},
            {"name": "Azar", "meaning": "Fire", "days": 30},
            {"name": "Dey", "meaning": "The Creator", "days": 30},
            {"name": "Bahman", "meaning": "Good Mind", "days": 30},
            {"name": "Esfand", "meaning": "Holy Devotion", "days": 30}
        ],
        
        # 5 Gatha days (identical to Shenshai)
        "gatha_days": [
            {"name": "Ahunavad", "meaning": "Possessing Ahu"},
            {"name": "Ushtavad", "meaning": "Possessing Happiness"},
            {"name": "Spentomad", "meaning": "Possessing Holy Devotion"},
            {"name": "Vohukshathra", "meaning": "Possessing Good Dominion"},
            {"name": "Vahishtoisht", "meaning": "Best Righteousness"}
        ],
        
        # 30 day dedications (identical to Shenshai)
        "day_yazatas": [
            {"day": 1, "name": "Ohrmazd", "meaning": "Lord Wisdom"},
            {"day": 2, "name": "Bahman", "meaning": "Good Mind"},
            {"day": 3, "name": "Ardibehesht", "meaning": "Best Righteousness"},
            {"day": 4, "name": "Shahrivar", "meaning": "Desirable Dominion"},
            {"day": 5, "name": "Esfand", "meaning": "Holy Devotion"},
            {"day": 6, "name": "Khordad", "meaning": "Perfection"},
            {"day": 7, "name": "Amardad", "meaning": "Immortality"},
            {"day": 8, "name": "Dey-pa-Adar", "meaning": "Creator before Fire"},
            {"day": 9, "name": "Azar", "meaning": "Fire"},
            {"day": 10, "name": "Aban", "meaning": "Waters"},
            {"day": 11, "name": "Khorshed", "meaning": "Sun"},
            {"day": 12, "name": "Mohor", "meaning": "Moon"},
            {"day": 13, "name": "Tir", "meaning": "Sirius"},
            {"day": 14, "name": "Gosh", "meaning": "Cattle"},
            {"day": 15, "name": "Dey-pa-Mehr", "meaning": "Creator before Mithra"},
            {"day": 16, "name": "Mehr", "meaning": "Covenant/Mithra"},
            {"day": 17, "name": "Srosh", "meaning": "Obedience"},
            {"day": 18, "name": "Rashnu", "meaning": "Justice"},
            {"day": 19, "name": "Fravardin", "meaning": "Guardian Spirits"},
            {"day": 20, "name": "Behram", "meaning": "Victory"},
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

class KadmiCalendarSensor(AlternativeTimeSensorBase):
    """Sensor for Zoroastrian Kadmi Calendar."""
    
    # Class-level update interval
    UPDATE_INTERVAL = UPDATE_INTERVAL
    
    def __init__(self, base_name: str, hass) -> None:
        """Initialize the Kadmi calendar sensor."""
        super().__init__(base_name, hass)
        
        # Get translated name from metadata
        calendar_name = self._translate('name', 'Kadmi Calendar')
        
        # Set sensor attributes
        self._attr_name = f"{base_name} {calendar_name}"
        self._attr_unique_id = f"{base_name}_kadmi_calendar"
        self._attr_icon = CALENDAR_INFO.get("icon", "mdi:fire")
        
        # Default configuration options
        self._show_yazata = True
        self._show_shenshai_difference = True
        self._show_schism_note = True
        self._show_festivals = True
        
        # Calendar data
        self._kadmi_data = CALENDAR_INFO["kadmi_data"]
        
        # Track if options have been loaded
        self._options_loaded = False
        
        _LOGGER.debug(f"Initialized Kadmi Calendar sensor: {self._attr_name}")
    
    def _load_options(self) -> None:
        """Load configuration options from config entry."""
        if self._options_loaded:
            return
            
        try:
            options = self.get_plugin_options()
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
        
        # Add Kadmi-specific attributes
        if hasattr(self, '_kadmi_calendar'):
            attrs.update(self._kadmi_calendar)
            
            # Add description in user's language
            attrs["description"] = self._translate('description')
            
            # Add disclaimer
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
        """Calculate Kadmi date from Gregorian date."""
        # Get epoch information
        epoch = self._kadmi_data["epoch"]
        epoch_date = epoch["gregorian_date"]
        epoch_year = epoch["kadmi_year"]
        
        # Calculate days since epoch
        days_diff = (gregorian_date.date() - epoch_date.date()).days
        
        # Handle dates before epoch
        if days_diff < 0:
            # Go backwards
            years_back = abs(days_diff) // 365
            remaining_days = abs(days_diff) % 365
            
            year = epoch_year - years_back - 1
            # Calculate from end of year backwards
            if remaining_days == 0:
                month_idx = 11
                day = 30
                is_gatha = False
            else:
                day_of_year = 365 - remaining_days
                month_idx, day, is_gatha = self._get_month_and_day(day_of_year)
        else:
            # Calculate years passed (365 days each, no leap years)
            years_passed = days_diff // 365
            day_of_year = (days_diff % 365) + 1
            
            # Calculate year
            year = epoch_year + years_passed
            
            # Find month and day
            month_idx, day, is_gatha = self._get_month_and_day(day_of_year)
        
        return year, month_idx, day, is_gatha
    
    def _get_month_and_day(self, day_of_year: int) -> tuple:
        """Get month index and day from day of year."""
        # Check if in regular months (1-360)
        if day_of_year <= 360:
            month_idx = (day_of_year - 1) // 30
            day = ((day_of_year - 1) % 30) + 1
            is_gatha = False
        else:
            # In Gatha days (361-365)
            month_idx = day_of_year - 361  # 0-4 for 5 Gatha days
            day = day_of_year - 360
            is_gatha = True
        
        return month_idx, day, is_gatha
    
    def _get_yazata(self, day: int) -> Dict[str, str]:
        """Get the Yazata (divine being) for a given day."""
        if 1 <= day <= 30:
            return self._kadmi_data["day_yazatas"][day - 1]
        return {"name": "Unknown", "meaning": ""}
    
    def _check_festival(self, month_name: str, day: int, is_gatha: bool) -> Optional[str]:
        """Check if current day is a festival."""
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
    
    def _calculate_time(self, gregorian_date: datetime) -> None:
        """Calculate Kadmi calendar date."""
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
            _LOGGER.error(f"Error calculating Kadmi calendar: {e}")
            self._state = "Error"
            self._kadmi_calendar = {"error": str(e)}
    
    def get_calendar_metadata(self) -> Dict[str, Any]:
        """Return calendar metadata."""
        return CALENDAR_INFO