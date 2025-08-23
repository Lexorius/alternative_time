"""Zoroastrian Fasli Calendar Plugin for Alternative Time Systems.

Implements the modernized Parsi calendar introduced in 1906 CE, which includes leap years.
This calendar keeps Nowruz fixed at the spring equinox (March 21) using intercalation.

IMPORTANT: The Fasli calendar was a scientific reform to align with the solar year.
While solving the drift problem, it created a third faction in an already divided community.
It is primarily used by Iranian Zoroastrians and progressive Parsis.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import logging

from ..sensor import AlternativeTimeSensorBase

_LOGGER = logging.getLogger(__name__)

# Calendar metadata and configuration
CALENDAR_INFO = {
    "id": "fasli",
    "version": "2.5.0",
    "name": {
        "en": "Fasli Calendar (Zoroastrian)",
        "de": "Fasli-Kalender (Zoroastrisch)",
        "es": "Calendario Fasli (Zoroástrico)",
        "fr": "Calendrier Fasli (Zoroastrien)",
        "it": "Calendario Fasli (Zoroastriano)",
        "nl": "Fasli Kalender (Zoroastrisch)",
        "pl": "Kalendarz Fasli (Zoroastryjski)",
        "pt": "Calendário Fasli (Zoroastriano)",
        "ru": "Календарь Фасли (Зороастрийский)",
        "ja": "ファスリ暦（ゾロアスター教）",
        "zh": "法斯利历（琐罗亚斯德教）",
        "ko": "파슬리 달력 (조로아스터교)"
    },
    "description": {
        "en": "Solar-fixed Zoroastrian calendar (1906) with leap years, Nowruz at spring equinox",
        "de": "Solar-fixierter zoroastrischer Kalender (1906) mit Schaltjahren, Nowruz am Frühlingsäquinoktium",
        "es": "Calendario zoroástrico fijado al sol (1906) con años bisiestos, Nowruz en equinoccio de primavera",
        "fr": "Calendrier zoroastrien fixé au soleil (1906) avec années bissextiles, Nowruz à l'équinoxe de printemps",
        "it": "Calendario zoroastriano fisso solare (1906) con anni bisestili, Nowruz all'equinozio di primavera",
        "nl": "Zonne-gefixeerde Zoroastrische kalender (1906) met schrikkeljaren, Nowruz op lente-equinox",
        "pl": "Kalendarz zoroastryjski ustalony słonecznie (1906) z latami przestępnymi, Nowruz w równonocy wiosennej",
        "pt": "Calendário zoroastriano fixo solar (1906) com anos bissextos, Nowruz no equinócio da primavera",
        "ru": "Солнечно-фиксированный зороастрийский календарь (1906) с високосными годами, Навруз в весеннее равноденствие",
        "ja": "太陽固定ゾロアスター暦（1906年）、閏年あり、春分にノウルーズ",
        "zh": "太阳固定琐罗亚斯德历（1906年），有闰年，诺鲁孜在春分",
        "ko": "태양 고정 조로아스터 달력 (1906), 윤년 있음, 춘분에 노루즈"
    },
    "category": "religious",
    "update_interval": 3600,
    "accuracy": "day",
    "icon": "mdi:white-balance-sunny",
    "reference_url": "https://en.wikipedia.org/wiki/Zoroastrian_calendar#Fasli_calendar",
    
    # Context about the three-way split
    "disclaimer": {
        "en": "⚠️ MODERNIZED CALENDAR (1906): The Fasli reform by Kharshedji Cama added leap years to fix Nowruz at the spring equinox, solving the drift problem. However, it created a THIRD faction in the already split Parsi community. Used primarily by Iranian Zoroastrians and ~5% of Parsis. While scientifically accurate, it broke with centuries of tradition. The community remains divided: Shenshai (traditional), Kadmi (1746 reform), and Fasli (modern).",
        "de": "⚠️ MODERNISIERTER KALENDER (1906): Die Fasli-Reform von Kharshedji Cama fügte Schaltjahre hinzu um Nowruz am Frühlingsäquinoktium zu fixieren und löste das Driftproblem. Sie schuf jedoch eine DRITTE Fraktion in der bereits gespaltenen Parsi-Gemeinde. Hauptsächlich von iranischen Zoroastriern und ~5% der Parsis verwendet. Wissenschaftlich genau, brach aber mit jahrhundertealter Tradition. Die Gemeinde bleibt geteilt: Shenshai (traditionell), Kadmi (1746 Reform) und Fasli (modern).",
        "es": "⚠️ CALENDARIO MODERNIZADO (1906): La reforma Fasli de Kharshedji Cama agregó años bisiestos para fijar Nowruz en el equinoccio de primavera, resolviendo el problema de deriva. Sin embargo, creó una TERCERA facción en la ya dividida comunidad Parsi. Usado principalmente por zoroástricos iraníes y ~5% de Parsis. Aunque científicamente preciso, rompió con siglos de tradición. La comunidad permanece dividida: Shenshai (tradicional), Kadmi (reforma 1746) y Fasli (moderno).",
        "fr": "⚠️ CALENDRIER MODERNISÉ (1906): La réforme Fasli de Kharshedji Cama a ajouté des années bissextiles pour fixer Nowruz à l'équinoxe de printemps, résolvant le problème de dérive. Cependant, elle a créé une TROISIÈME faction dans la communauté Parsi déjà divisée. Utilisé principalement par les zoroastriens iraniens et ~5% des Parsis. Bien que scientifiquement précis, il a rompu avec des siècles de tradition. La communauté reste divisée: Shenshai (traditionnel), Kadmi (réforme 1746) et Fasli (moderne).",
        "it": "⚠️ CALENDARIO MODERNIZZATO (1906): La riforma Fasli di Kharshedji Cama ha aggiunto anni bisestili per fissare Nowruz all'equinozio di primavera, risolvendo il problema della deriva. Tuttavia, ha creato una TERZA fazione nella già divisa comunità Parsi. Usato principalmente dagli zoroastriani iraniani e ~5% dei Parsi. Sebbene scientificamente accurato, ha rotto con secoli di tradizione. La comunità rimane divisa: Shenshai (tradizionale), Kadmi (riforma 1746) e Fasli (moderno).",
        "nl": "⚠️ GEMODERNISEERDE KALENDER (1906): De Fasli-hervorming van Kharshedji Cama voegde schrikkeljaren toe om Nowruz op de lente-equinox te fixeren, wat het driftprobleem oploste. Het creëerde echter een DERDE factie in de al verdeelde Parsi-gemeenschap. Vooral gebruikt door Iraanse Zoroastriërs en ~5% van de Parsi's. Hoewel wetenschappelijk nauwkeurig, brak het met eeuwen van traditie. De gemeenschap blijft verdeeld: Shenshai (traditioneel), Kadmi (1746 hervorming) en Fasli (modern).",
        "pl": "⚠️ ZMODERNIZOWANY KALENDARZ (1906): Reforma Fasli Kharshedjiego Camy dodała lata przestępne, aby ustalić Nowruz na równonocy wiosennej, rozwiązując problem dryftu. Jednak stworzyła TRZECIĄ frakcję w już podzielonej społeczności Parsi. Używany głównie przez irańskich zoroastrian i ~5% Parsów. Choć naukowo dokładny, zerwał z wielowiekową tradycją. Społeczność pozostaje podzielona: Shenshai (tradycyjny), Kadmi (reforma 1746) i Fasli (nowoczesny).",
        "pt": "⚠️ CALENDÁRIO MODERNIZADO (1906): A reforma Fasli de Kharshedji Cama adicionou anos bissextos para fixar Nowruz no equinócio da primavera, resolvendo o problema de deriva. No entanto, criou uma TERCEIRA facção na já dividida comunidade Parsi. Usado principalmente por zoroastrianos iranianos e ~5% dos Parsis. Embora cientificamente preciso, rompeu com séculos de tradição. A comunidade permanece dividida: Shenshai (tradicional), Kadmi (reforma 1746) e Fasli (moderno).",
        "ru": "⚠️ МОДЕРНИЗИРОВАННЫЙ КАЛЕНДАРЬ (1906): Реформа Фасли Харшеджи Камы добавила високосные годы, чтобы зафиксировать Навруз на весеннем равноденствии, решив проблему дрейфа. Однако она создала ТРЕТЬЮ фракцию в уже расколотой общине парсов. Используется в основном иранскими зороастрийцами и ~5% парсов. Хотя научно точен, он порвал с многовековой традицией. Община остается разделенной: Шеншай (традиционный), Кадми (реформа 1746) и Фасли (современный).",
        "ja": "⚠️ 近代化された暦（1906年）：カルシェジ・カマのファスリ改革は閏年を追加してノウルーズを春分に固定し、ずれの問題を解決しました。しかし、すでに分裂していたパールシー共同体に第三の派閥を作りました。主にイランのゾロアスター教徒と約5％のパールシーが使用。科学的に正確ですが、何世紀もの伝統を破りました。共同体は分裂したまま：シェンシャイ（伝統）、カドミ（1746年改革）、ファスリ（現代）。",
        "zh": "⚠️ 现代化历法（1906年）：卡尔谢吉·卡马的法斯利改革增加了闰年，将诺鲁孜固定在春分，解决了偏移问题。然而，它在已经分裂的帕西社区中创造了第三个派系。主要由伊朗琐罗亚斯德教徒和约5%的帕西人使用。虽然科学准确，但打破了几个世纪的传统。社区仍然分裂：申沙（传统）、卡德米（1746年改革）和法斯利（现代）。",
        "ko": "⚠️ 현대화된 달력 (1906): 카르셰지 카마의 파슬리 개혁은 윤년을 추가하여 노루즈를 춘분에 고정시켜 편차 문제를 해결했습니다. 그러나 이미 분열된 파르시 공동체에 세 번째 분파를 만들었습니다. 주로 이란 조로아스터교도와 약 5%의 파르시가 사용. 과학적으로 정확하지만 수세기의 전통을 깨뜨렸습니다. 공동체는 여전히 분열: 셴샤이(전통), 카드미(1746 개혁), 파슬리(현대)."
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
        "show_leap_year": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show Leap Year Status",
                "de": "Schaltjahr-Status anzeigen",
                "es": "Mostrar estado de año bisiesto",
                "fr": "Afficher le statut d'année bissextile",
                "it": "Mostra stato anno bisestile",
                "nl": "Toon schrikkeljaar status",
                "pl": "Pokaż status roku przestępnego",
                "pt": "Mostrar status de ano bissexto",
                "ru": "Показать статус високосного года",
                "ja": "閏年の状態を表示",
                "zh": "显示闰年状态",
                "ko": "윤년 상태 표시"
            },
            "description": {
                "en": "Display whether current year is a leap year (366 days)",
                "de": "Zeigt ob das aktuelle Jahr ein Schaltjahr ist (366 Tage)",
                "es": "Muestra si el año actual es bisiesto (366 días)",
                "fr": "Affiche si l'année en cours est bissextile (366 jours)"
            }
        },
        "show_comparison": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show Comparison with Other Calendars",
                "de": "Vergleich mit anderen Kalendern anzeigen",
                "es": "Mostrar comparación con otros calendarios",
                "fr": "Afficher la comparaison avec d'autres calendriers",
                "it": "Mostra confronto con altri calendari",
                "nl": "Toon vergelijking met andere kalenders",
                "pl": "Pokaż porównanie z innymi kalendarzami",
                "pt": "Mostrar comparação com outros calendários",
                "ru": "Показать сравнение с другими календарями",
                "ja": "他の暦との比較を表示",
                "zh": "显示与其他历法的比较",
                "ko": "다른 달력과 비교 표시"
            },
            "description": {
                "en": "Show how Fasli aligns with Shenshai and Kadmi calendars",
                "de": "Zeigt wie Fasli mit Shenshai und Kadmi Kalendern übereinstimmt",
                "es": "Muestra cómo Fasli se alinea con los calendarios Shenshai y Kadmi",
                "fr": "Montre comment Fasli s'aligne avec les calendriers Shenshai et Kadmi"
            }
        },
        "show_reform_note": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show Reform Information",
                "de": "Reforminformationen anzeigen",
                "es": "Mostrar información de reforma",
                "fr": "Afficher les informations de réforme",
                "it": "Mostra informazioni riforma",
                "nl": "Toon hervorming informatie",
                "pl": "Pokaż informacje o reformie",
                "pt": "Mostrar informação da reforma",
                "ru": "Показать информацию о реформе",
                "ja": "改革情報を表示",
                "zh": "显示改革信息",
                "ko": "개혁 정보 표시"
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
    
    # Fasli calendar data
    "fasli_data": {
        # 12 months of 30 days each (same as other variants)
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
        
        # Gatha days - 5 in regular years, 6 in leap years
        "gatha_days": [
            {"name": "Ahunavad", "meaning": "Possessing Ahu"},
            {"name": "Ushtavad", "meaning": "Possessing Happiness"},
            {"name": "Spentomad", "meaning": "Possessing Holy Devotion"},
            {"name": "Vohukshathra", "meaning": "Possessing Good Dominion"},
            {"name": "Vahishtoisht", "meaning": "Best Righteousness"},
            {"name": "Avardad-sal-gah", "meaning": "Leap Day", "leap_only": True}
        ],
        
        # 30 day dedications (same as other variants)
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
        
        # Festivals (same dates but always on fixed solar dates)
        "festivals": {
            "Farvardin 1": "Nowruz (New Year - Spring Equinox)",
            "Farvardin 19": "Fravardingan (All Souls)",
            "Ardibehesht 3": "Ardibehesht Festival",
            "Khordad 6": "Khordad Sal (Birthday of Zoroaster)",
            "Tir 13": "Tiragan (Rain Festival)",
            "Amardad 7": "Amardadgan",
            "Shahrivar 4": "Shahrivargan",
            "Mehr 16": "Mehragan (Harvest Festival - Autumn Equinox)",
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
        
        # Reform history
        "reform_history": {
            "reform_year": 1906,
            "reformer": "Kharshedji Rustamji Cama",
            "location": "Mumbai, India",
            "reasoning": "Scientific accuracy - align with solar year",
            "method": "Added leap years following Gregorian pattern",
            "adoption": "Iranian Zoroastrians (majority), ~5% of Parsis",
            "opposition": "Most Parsis saw it as too radical",
            "result": "Three-way split: Shenshai (~75%), Kadmi (~20%), Fasli (~5%)",
            "advantage": "No drift, festivals stay seasonal",
            "disadvantage": "Broke with tradition, created third faction",
            "iranian_adoption": "Officially adopted in Iran in 1939"
        },
        
        # Year calculation offset
        # Fasli year = Gregorian year + 1368 (before March 21)
        # Fasli year = Gregorian year + 1369 (after March 21)
        "year_offset": {
            "before_nowruz": 1368,
            "after_nowruz": 1369
        }
    }
}

# Update interval for this sensor
UPDATE_INTERVAL = CALENDAR_INFO["update_interval"]

class FasliCalendarSensor(AlternativeTimeSensorBase):
    """Sensor for Zoroastrian Fasli Calendar."""
    
    # Class-level update interval
    UPDATE_INTERVAL = UPDATE_INTERVAL
    
    def __init__(self, base_name: str, hass) -> None:
        """Initialize the Fasli calendar sensor."""
        super().__init__(base_name, hass)
        
        # Get translated name from metadata
        calendar_name = self._translate('name', 'Fasli Calendar')
        
        # Set sensor attributes
        self._attr_name = f"{base_name} {calendar_name}"
        self._attr_unique_id = f"{base_name}_fasli_calendar"
        self._attr_icon = CALENDAR_INFO.get("icon", "mdi:white-balance-sunny")
        
        # Default configuration options
        self._show_yazata = True
        self._show_leap_year = True
        self._show_comparison = True
        self._show_reform_note = True
        self._show_festivals = True
        
        # Calendar data
        self._fasli_data = CALENDAR_INFO["fasli_data"]
        
        # Track if options have been loaded
        self._options_loaded = False
        
        _LOGGER.debug(f"Initialized Fasli Calendar sensor: {self._attr_name}")
    
    def _load_options(self) -> None:
        """Load configuration options from config entry."""
        if self._options_loaded:
            return
            
        try:
            options = self.get_plugin_options()
            if options:
                # Update configuration from plugin options
                self._show_yazata = options.get("show_yazata", self._show_yazata)
                self._show_leap_year = options.get("show_leap_year", self._show_leap_year)
                self._show_comparison = options.get("show_comparison", self._show_comparison)
                self._show_reform_note = options.get("show_reform_note", self._show_reform_note)
                self._show_festivals = options.get("show_festivals", self._show_festivals)
                
                _LOGGER.debug(f"Fasli sensor loaded options: yazata={self._show_yazata}, "
                            f"leap={self._show_leap_year}, comparison={self._show_comparison}, "
                            f"reform={self._show_reform_note}, festivals={self._show_festivals}")
            else:
                _LOGGER.debug("Fasli sensor using default options - no custom options found")
                
            self._options_loaded = True
        except Exception as e:
            _LOGGER.debug(f"Fasli sensor could not load options yet: {e}")
    
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
        
        # Add Fasli-specific attributes
        if hasattr(self, '_fasli_calendar'):
            attrs.update(self._fasli_calendar)
            
            # Add description in user's language
            attrs["description"] = self._translate('description')
            
            # Add disclaimer
            attrs["disclaimer"] = self._translate('disclaimer')
            
            # Add reference
            attrs["reference"] = CALENDAR_INFO.get('reference_url', '')
            
            # Add reform history if enabled
            if self._show_reform_note:
                attrs["reform_history"] = self._fasli_data["reform_history"]
            
            # Add configuration status
            attrs["config"] = {
                "show_yazata": self._show_yazata,
                "show_leap_year": self._show_leap_year,
                "show_comparison": self._show_comparison,
                "show_reform_note": self._show_reform_note,
                "show_festivals": self._show_festivals
            }
        
        return attrs
    
    def _is_leap_year(self, gregorian_year: int) -> bool:
        """Check if a Gregorian year is a leap year (Fasli follows Gregorian leap rules)."""
        return (gregorian_year % 4 == 0 and gregorian_year % 100 != 0) or (gregorian_year % 400 == 0)
    
    def _calculate_fasli_date(self, gregorian_date: datetime) -> tuple:
        """Calculate Fasli date from Gregorian date."""
        # Fasli New Year is fixed at March 21 (Spring Equinox)
        year = gregorian_date.year
        
        # Create Nowruz date for current year
        nowruz = datetime(year, 3, 21)
        
        # Determine Fasli year
        if gregorian_date < nowruz:
            # Before Nowruz - previous Fasli year
            fasli_year = year + self._fasli_data["year_offset"]["before_nowruz"]
            # Recalculate from previous year's Nowruz
            nowruz = datetime(year - 1, 3, 21)
        else:
            # After Nowruz - current Fasli year
            fasli_year = year + self._fasli_data["year_offset"]["after_nowruz"]
        
        # Calculate days since Nowruz
        days_since_nowruz = (gregorian_date.date() - nowruz.date()).days
        
        # Check if it's a leap year
        is_leap = self._is_leap_year(nowruz.year)
        
        # Find month and day
        if days_since_nowruz < 360:
            # Regular months (1-360)
            month_idx = days_since_nowruz // 30
            day = (days_since_nowruz % 30) + 1
            is_gatha = False
        else:
            # Gatha days (361-365/366)
            gatha_day = days_since_nowruz - 359
            if is_leap and gatha_day == 6:
                # Leap day (6th Gatha day)
                month_idx = 5  # Index for leap day
                day = 6
            else:
                # Regular Gatha days
                if is_leap and gatha_day > 6:
                    gatha_day -= 1  # Adjust for leap day
                month_idx = gatha_day - 1
                day = gatha_day
            is_gatha = True
        
        return fasli_year, month_idx, day, is_gatha, is_leap
    
    def _get_yazata(self, day: int) -> Dict[str, str]:
        """Get the Yazata (divine being) for a given day."""
        if 1 <= day <= 30:
            return self._fasli_data["day_yazatas"][day - 1]
        return {"name": "Unknown", "meaning": ""}
    
    def _check_festival(self, month_name: str, day: int, is_gatha: bool) -> Optional[str]:
        """Check if current day is a festival."""
        if is_gatha:
            if day == 5:
                return self._fasli_data["festivals"].get("Gatha 5", None)
        else:
            date_key = f"{month_name} {day}"
            return self._fasli_data["festivals"].get(date_key, None)
    
    def _calculate_other_calendar_dates(self, gregorian_date: datetime) -> Dict[str, str]:
        """Calculate approximate dates in Shenshai and Kadmi calendars."""
        # This is simplified - actual calculation would need full implementation
        # Shenshai drifts ~0.2422 days/year since 1006 CE
        # Kadmi is 30 days ahead of Shenshai
        
        years_since_1006 = gregorian_date.year - 1006
        shenshai_drift = int(years_since_1006 * 0.2422)
        
        # Very approximate - for display purposes only
        shenshai_offset = shenshai_drift
        kadmi_offset = shenshai_drift - 30
        
        return {
            "shenshai_drift": f"~{shenshai_drift} days behind solar year",
            "kadmi_drift": f"~{shenshai_drift} days behind solar year (30 days ahead of Shenshai)",
            "fasli_drift": "No drift (fixed to solar year)"
        }
    
    def _format_fasli_date(self, gregorian_date: datetime) -> str:
        """Format the Fasli date."""
        # Reload options
        self._load_options()
        
        # Calculate date
        year, month_idx, day, is_gatha, is_leap = self._calculate_fasli_date(gregorian_date)
        
        # Format based on whether it's a Gatha day
        if is_gatha:
            if is_leap and day == 6:
                # Leap day
                gatha = self._fasli_data["gatha_days"][5]  # Avardad-sal-gah
                result = f"{gatha['name']} (Leap Day), {year} Y.Z."
            else:
                # Regular Gatha day
                gatha = self._fasli_data["gatha_days"][month_idx]
                result = f"{day} {gatha['name']}, {year} Y.Z."
        else:
            month = self._fasli_data["months"][month_idx]
            result = f"{day} {month['name']}, {year} Y.Z."
        
        # Add Yazata if requested and not Gatha day
        if self._show_yazata and not is_gatha:
            yazata = self._get_yazata(day)
            result += f" ({yazata['name']})"
        
        # Add leap year indicator if requested
        if self._show_leap_year and is_leap:
            result += " [Leap Year]"
        
        # Add reform note if requested
        if self._show_reform_note:
            result += " [Solar-fixed]"
        
        return result
    
    def _calculate_time(self, gregorian_date: datetime) -> None:
        """Calculate Fasli calendar date."""
        try:
            # Format the main date string
            fasli_date = self._format_fasli_date(gregorian_date)
            
            # Calculate date components
            year, month_idx, day, is_gatha, is_leap = self._calculate_fasli_date(gregorian_date)
            
            # Build attribute data
            self._fasli_calendar = {
                "formatted_date": fasli_date,
                "year": {
                    "yazdegerdi": year,
                    "gregorian": gregorian_date.year,
                    "era": "Y.Z. (Yazdegerdi Era)",
                    "is_leap_year": is_leap,
                    "days_in_year": 366 if is_leap else 365
                },
                "is_gatha_day": is_gatha,
                "reform_status": {
                    "type": "Fasli (Modernized)",
                    "year_of_reform": 1906,
                    "fixed_to": "Solar Year (Spring Equinox)",
                    "percentage_of_community": "~5% of Parsis, majority in Iran",
                    "advantage": "No calendar drift"
                }
            }
            
            if is_gatha:
                # Gatha day information
                if is_leap and day == 6:
                    gatha = self._fasli_data["gatha_days"][5]  # Leap day
                    self._fasli_calendar["gatha"] = {
                        "day": day,
                        "name": gatha["name"],
                        "meaning": gatha["meaning"],
                        "is_leap_day": True,
                        "total_gatha_days": 6
                    }
                else:
                    gatha = self._fasli_data["gatha_days"][month_idx]
                    self._fasli_calendar["gatha"] = {
                        "day": day,
                        "name": gatha["name"],
                        "meaning": gatha["meaning"],
                        "is_leap_day": False,
                        "total_gatha_days": 6 if is_leap else 5
                    }
            else:
                # Regular month information
                month = self._fasli_data["months"][month_idx]
                self._fasli_calendar["month"] = {
                    "name": month["name"],
                    "meaning": month["meaning"],
                    "number": month_idx + 1,
                    "days": month["days"]
                }
                self._fasli_calendar["day"] = {
                    "number": day,
                    "total_days": 30
                }
                
                # Add Yazata information
                if self._show_yazata:
                    yazata = self._get_yazata(day)
                    self._fasli_calendar["yazata"] = {
                        "name": yazata["name"],
                        "meaning": yazata["meaning"],
                        "day_dedication": day
                    }
                
                # Check for festival
                if self._show_festivals:
                    festival = self._check_festival(month["name"], day, False)
                    if festival:
                        self._fasli_calendar["festival"] = festival
            
            # Add comparison with other calendars if requested
            if self._show_comparison:
                comparison = self._calculate_other_calendar_dates(gregorian_date)
                self._fasli_calendar["calendar_comparison"] = comparison
                self._fasli_calendar["community_division"] = {
                    "shenshai": "~75% (traditional, drifting)",
                    "kadmi": "~20% (1746 reform, drifting)",
                    "fasli": "~5% (1906 reform, solar-fixed)"
                }
            
            # Calculate days until Nowruz (always March 21)
            next_nowruz = datetime(gregorian_date.year + 1, 3, 21)
            if gregorian_date >= datetime(gregorian_date.year, 3, 21):
                days_to_nowruz = (next_nowruz.date() - gregorian_date.date()).days
            else:
                current_nowruz = datetime(gregorian_date.year, 3, 21)
                days_to_nowruz = (current_nowruz.date() - gregorian_date.date()).days
            
            self._fasli_calendar["days_to_nowruz"] = days_to_nowruz
            self._fasli_calendar["nowruz_fixed_date"] = "March 21 (Spring Equinox)"
            
            # Set state
            self._state = fasli_date
            
        except Exception as e:
            _LOGGER.error(f"Error calculating Fasli calendar: {e}")
            self._state = "Error"
            self._fasli_calendar = {"error": str(e)}
    
    def get_calendar_metadata(self) -> Dict[str, Any]:
        """Return calendar metadata."""
        return CALENDAR_INFO
