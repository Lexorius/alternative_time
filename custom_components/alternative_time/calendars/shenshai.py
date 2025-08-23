"""Zoroastrian Shenshai Calendar Plugin for Alternative Time Systems.

Implements the traditional Parsi calendar as used by the majority of Zoroastrians in India.
This calendar has 12 months of 30 days plus 5 Gatha days, totaling 365 days.

IMPORTANT: This calendar does not use leap years and therefore drifts from the solar year
by approximately 1 day every 4 years. This is intentional and reflects traditional practice.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import logging

from ..sensor_base import AlternativeTimeSensorBase

_LOGGER = logging.getLogger(__name__)

# Calendar metadata and configuration
CALENDAR_INFO = {
    "id": "shenshai",
    "version": "2.5.0",
    "name": {
        "en": "Shenshai Calendar (Zoroastrian)",
        "de": "Shenshai-Kalender (Zoroastrisch)",
        "es": "Calendario Shenshai (Zoroástrico)",
        "fr": "Calendrier Shenshai (Zoroastrien)",
        "it": "Calendario Shenshai (Zoroastriano)",
        "nl": "Shenshai Kalender (Zoroastrisch)",
        "pl": "Kalendarz Shenshai (Zoroastryjski)",
        "pt": "Calendário Shenshai (Zoroastriano)",
        "ru": "Календарь Шеншай (Зороастрийский)",
        "ja": "シェンシャイ暦（ゾロアスター教）",
        "zh": "申沙历（琐罗亚斯德教）",
        "ko": "셴샤이 달력 (조로아스터교)"
    },
    "description": {
        "en": "Traditional Parsi calendar with 365 days, no leap years (drifts ~1 day/4 years)",
        "de": "Traditioneller Parsi-Kalender mit 365 Tagen, keine Schaltjahre (driftet ~1 Tag/4 Jahre)",
        "es": "Calendario Parsi tradicional con 365 días, sin años bisiestos (deriva ~1 día/4 años)",
        "fr": "Calendrier Parsi traditionnel avec 365 jours, sans années bissextiles (dérive ~1 jour/4 ans)",
        "it": "Calendario Parsi tradizionale con 365 giorni, senza anni bisestili (deriva ~1 giorno/4 anni)",
        "nl": "Traditionele Parsi kalender met 365 dagen, geen schrikkeljaren (drift ~1 dag/4 jaar)",
        "pl": "Tradycyjny kalendarz Parsi z 365 dniami, bez lat przestępnych (dryfuje ~1 dzień/4 lata)",
        "pt": "Calendário Parsi tradicional com 365 dias, sem anos bissextos (deriva ~1 dia/4 anos)",
        "ru": "Традиционный календарь парсов с 365 днями, без високосных лет (дрейф ~1 день/4 года)",
        "ja": "365日の伝統的パールシー暦、閏年なし（4年で約1日ずれる）",
        "zh": "传统帕西历365天，无闰年（每4年偏移约1天）",
        "ko": "365일 전통 파르시 달력, 윤년 없음 (4년마다 약 1일 편차)"
    },
    "category": "religious",
    "update_interval": 3600,
    "accuracy": "day",
    "icon": "mdi:fire",
    "reference_url": "https://en.wikipedia.org/wiki/Zoroastrian_calendar",
    
    # Important disclaimer about calendar drift
    "disclaimer": {
        "en": "⚠️ TRADITIONAL CALENDAR: This Shenshai calendar intentionally has no leap years and drifts from the solar year (~1 day per 4 years). Currently offset by ~200+ days from the original seasonal alignment. This is the authentic practice maintained by the Parsi community since 1006 CE.",
        "de": "⚠️ TRADITIONELLER KALENDER: Dieser Shenshai-Kalender hat absichtlich keine Schaltjahre und driftet vom Sonnenjahr (~1 Tag pro 4 Jahre). Derzeit ~200+ Tage von der ursprünglichen saisonalen Ausrichtung versetzt. Dies ist die authentische Praxis der Parsi-Gemeinschaft seit 1006 n.Chr.",
        "es": "⚠️ CALENDARIO TRADICIONAL: Este calendario Shenshai intencionalmente no tiene años bisiestos y deriva del año solar (~1 día cada 4 años). Actualmente desplazado ~200+ días de la alineación estacional original. Esta es la práctica auténtica mantenida por la comunidad Parsi desde 1006 EC.",
        "fr": "⚠️ CALENDRIER TRADITIONNEL: Ce calendrier Shenshai n'a intentionnellement pas d'années bissextiles et dérive de l'année solaire (~1 jour par 4 ans). Actuellement décalé de ~200+ jours par rapport à l'alignement saisonnier d'origine. C'est la pratique authentique maintenue par la communauté Parsi depuis 1006 EC.",
        "it": "⚠️ CALENDARIO TRADIZIONALE: Questo calendario Shenshai intenzionalmente non ha anni bisestili e deriva dall'anno solare (~1 giorno ogni 4 anni). Attualmente spostato di ~200+ giorni dall'allineamento stagionale originale. Questa è la pratica autentica mantenuta dalla comunità Parsi dal 1006 d.C.",
        "nl": "⚠️ TRADITIONELE KALENDER: Deze Shenshai kalender heeft opzettelijk geen schrikkeljaren en drijft af van het zonnejaar (~1 dag per 4 jaar). Momenteel ~200+ dagen verschoven van de oorspronkelijke seizoensuitlijning. Dit is de authentieke praktijk van de Parsi gemeenschap sinds 1006 n.Chr.",
        "pl": "⚠️ KALENDARZ TRADYCYJNY: Ten kalendarz Shenshai celowo nie ma lat przestępnych i dryfuje od roku słonecznego (~1 dzień na 4 lata). Obecnie przesunięty o ~200+ dni od pierwotnego wyrównania sezonowego. To autentyczna praktyka społeczności Parsi od 1006 r.",
        "pt": "⚠️ CALENDÁRIO TRADICIONAL: Este calendário Shenshai intencionalmente não tem anos bissextos e deriva do ano solar (~1 dia a cada 4 anos). Atualmente deslocado ~200+ dias do alinhamento sazonal original. Esta é a prática autêntica mantida pela comunidade Parsi desde 1006 EC.",
        "ru": "⚠️ ТРАДИЦИОННЫЙ КАЛЕНДАРЬ: Этот календарь Шеншай намеренно не имеет високосных лет и дрейфует от солнечного года (~1 день за 4 года). В настоящее время смещен на ~200+ дней от первоначального сезонного выравнивания. Это аутентичная практика общины парсов с 1006 г. н.э.",
        "ja": "⚠️ 伝統的暦：このシェンシャイ暦は意図的に閏年を持たず、太陽年から逸脱します（4年で約1日）。現在、元の季節の配置から200日以上ずれています。これは1006年以来パールシー共同体が維持している本物の慣習です。",
        "zh": "⚠️ 传统历法：此申沙历故意没有闰年，与太阳年偏离（每4年约1天）。目前与原始季节对齐偏移约200多天。这是帕西社区自公元1006年以来保持的真实做法。",
        "ko": "⚠️ 전통 달력: 이 셴샤이 달력은 의도적으로 윤년이 없으며 태양년에서 벗어납니다 (4년마다 약 1일). 현재 원래 계절 정렬에서 200일 이상 차이. 이것은 1006년 이래 파르시 공동체가 유지해온 진정한 관습입니다."
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
            },
            "description": {
                "en": "Display which divine being (Yazata) each day is dedicated to",
                "de": "Zeigt welchem göttlichen Wesen (Yazata) jeder Tag gewidmet ist",
                "es": "Muestra a qué ser divino (Yazata) está dedicado cada día",
                "fr": "Affiche à quel être divin (Yazata) chaque jour est dédié"
            }
        },
        "show_gregorian_drift": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show Calendar Drift",
                "de": "Kalenderdrift anzeigen",
                "es": "Mostrar deriva del calendario",
                "fr": "Afficher la dérive du calendrier",
                "it": "Mostra deriva del calendario",
                "nl": "Toon kalender drift",
                "pl": "Pokaż dryf kalendarza",
                "pt": "Mostrar deriva do calendário",
                "ru": "Показать дрейф календаря",
                "ja": "暦のずれを表示",
                "zh": "显示历法偏移",
                "ko": "달력 편차 표시"
            },
            "description": {
                "en": "Display how many days the calendar has drifted from original seasonal position",
                "de": "Zeigt wie viele Tage der Kalender von der ursprünglichen saisonalen Position abgewichen ist",
                "es": "Muestra cuántos días ha derivado el calendario de la posición estacional original",
                "fr": "Affiche de combien de jours le calendrier a dérivé de sa position saisonnière d'origine"
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
        },
        "year_offset": {
            "type": "number",
            "default": 1395,
            "label": {
                "en": "Year Offset from Gregorian",
                "de": "Jahresversatz vom Gregorianischen",
                "es": "Desplazamiento de año desde gregoriano",
                "fr": "Décalage d'année du grégorien",
                "it": "Offset anno dal gregoriano",
                "nl": "Jaar offset van Gregoriaans",
                "pl": "Przesunięcie roku od gregoriańskiego",
                "pt": "Deslocamento de ano do gregoriano",
                "ru": "Смещение года от григорианского",
                "ja": "グレゴリオ暦からの年オフセット",
                "zh": "与公历的年偏移",
                "ko": "그레고리력 연도 오프셋"
            },
            "description": {
                "en": "Zoroastrian year = Gregorian year + offset (traditional: 1395)",
                "de": "Zoroastrisches Jahr = Gregorianisches Jahr + Versatz (traditionell: 1395)",
                "es": "Año zoroástrico = Año gregoriano + desplazamiento (tradicional: 1395)",
                "fr": "Année zoroastrienne = Année grégorienne + décalage (traditionnel: 1395)"
            }
        }
    },
    
    # Shenshai calendar data
    "shenshai_data": {
        # 12 months of 30 days each
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
        
        # 5 Gatha days (intercalary days at year end)
        "gatha_days": [
            {"name": "Ahunavad", "meaning": "Possessing Ahu"},
            {"name": "Ushtavad", "meaning": "Possessing Happiness"},
            {"name": "Spentomad", "meaning": "Possessing Holy Devotion"},
            {"name": "Vohukshathra", "meaning": "Possessing Good Dominion"},
            {"name": "Vahishtoisht", "meaning": "Best Righteousness"}
        ],
        
        # 30 day dedications (Yazatas)
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
        
        # Important festivals (when day and month names match)
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
        
        # Reference epoch (when last synchronized)
        # Shenshai New Year 2024 = August 15, 2024 (Gregorian)
        "epoch": {
            "gregorian_date": datetime(2024, 8, 15),
            "shenshai_year": 1393,  # Year 1393 Y.Z. (Yazdegerdi)
            "note": "Last Nowruz in Shenshai reckoning"
        },
        
        # Historical note
        "history": {
            "last_sync": "1006 CE",
            "drift_days": 240,  # Approximate days drifted from spring equinox
            "original_nowruz": "Spring Equinox (March 21)",
            "current_nowruz": "Mid-August (drifting)"
        }
    }
}

# Update interval for this sensor
UPDATE_INTERVAL = CALENDAR_INFO["update_interval"]

class ShenshaiCalendarSensor(AlternativeTimeSensorBase):
    """Sensor for Zoroastrian Shenshai Calendar."""
    
    # Class-level update interval
    UPDATE_INTERVAL = UPDATE_INTERVAL
    
    def __init__(self, base_name: str, hass) -> None:
        """Initialize the Shenshai calendar sensor."""
        super().__init__(base_name, hass)
        
        # Get translated name from metadata
        calendar_name = self._translate('name', 'Shenshai Calendar')
        
        # Set sensor attributes
        self._attr_name = f"{base_name} {calendar_name}"
        self._attr_unique_id = f"{base_name}_shenshai_calendar"
        self._attr_icon = CALENDAR_INFO.get("icon", "mdi:fire")
        
        # Default configuration options
        self._show_yazata = True
        self._show_gregorian_drift = True
        self._show_festivals = True
        self._year_offset = 1395
        
        # Calendar data
        self._shenshai_data = CALENDAR_INFO["shenshai_data"]
        
        # Track if options have been loaded
        self._options_loaded = False
        
        _LOGGER.debug(f"Initialized Shenshai Calendar sensor: {self._attr_name}")
    
    def _load_options(self) -> None:
        """Load configuration options from config entry."""
        if self._options_loaded:
            return
            
        try:
            options = self.get_plugin_options()
            if options:
                # Update configuration from plugin options
                self._show_yazata = options.get("show_yazata", self._show_yazata)
                self._show_gregorian_drift = options.get("show_gregorian_drift", self._show_gregorian_drift)
                self._show_festivals = options.get("show_festivals", self._show_festivals)
                self._year_offset = options.get("year_offset", self._year_offset)
                
                _LOGGER.debug(f"Shenshai sensor loaded options: yazata={self._show_yazata}, "
                            f"drift={self._show_gregorian_drift}, festivals={self._show_festivals}, "
                            f"offset={self._year_offset}")
            else:
                _LOGGER.debug("Shenshai sensor using default options - no custom options found")
                
            self._options_loaded = True
        except Exception as e:
            _LOGGER.debug(f"Shenshai sensor could not load options yet: {e}")
    
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
        
        # Add Shenshai-specific attributes
        if hasattr(self, '_shenshai_calendar'):
            attrs.update(self._shenshai_calendar)
            
            # Add description in user's language
            attrs["description"] = self._translate('description')
            
            # Add disclaimer
            attrs["disclaimer"] = self._translate('disclaimer')
            
            # Add reference
            attrs["reference"] = CALENDAR_INFO.get('reference_url', '')
            
            # Add historical information
            attrs["historical_note"] = self._shenshai_data["history"]
            
            # Add configuration status
            attrs["config"] = {
                "show_yazata": self._show_yazata,
                "show_gregorian_drift": self._show_gregorian_drift,
                "show_festivals": self._show_festivals,
                "year_offset": self._year_offset
            }
        
        return attrs
    
    def _calculate_shenshai_date(self, gregorian_date: datetime) -> tuple:
        """Calculate Shenshai date from Gregorian date."""
        # Get epoch information
        epoch = self._shenshai_data["epoch"]
        epoch_date = epoch["gregorian_date"]
        epoch_year = epoch["shenshai_year"]
        
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
            return self._shenshai_data["day_yazatas"][day - 1]
        return {"name": "Unknown", "meaning": ""}
    
    def _check_festival(self, month_name: str, day: int, is_gatha: bool) -> Optional[str]:
        """Check if current day is a festival."""
        if is_gatha:
            if day == 5:
                return self._shenshai_data["festivals"].get("Gatha 5", None)
        else:
            date_key = f"{month_name} {day}"
            return self._shenshai_data["festivals"].get(date_key, None)
    
    def _calculate_drift(self, gregorian_date: datetime) -> int:
        """Calculate how many days the calendar has drifted from original position."""
        # Original Nowruz was at spring equinox (March 21)
        # Current Nowruz is around August 15
        # This is approximately 147 days of drift
        
        # More precise calculation based on years since last sync (1006 CE)
        years_since_sync = gregorian_date.year - 1006
        # Drift is approximately 0.2422 days per year (difference between 365 and 365.2422)
        drift_days = int(years_since_sync * 0.2422)
        
        return drift_days
    
    def _format_shenshai_date(self, gregorian_date: datetime) -> str:
        """Format the Shenshai date."""
        # Reload options
        self._load_options()
        
        # Calculate date
        year, month_idx, day, is_gatha = self._calculate_shenshai_date(gregorian_date)
        
        # Format based on whether it's a Gatha day
        if is_gatha:
            gatha = self._shenshai_data["gatha_days"][month_idx]
            result = f"{day} {gatha['name']}, {year} Y.Z."
        else:
            month = self._shenshai_data["months"][month_idx]
            result = f"{day} {month['name']}, {year} Y.Z."
        
        # Add Yazata if requested and not Gatha day
        if self._show_yazata and not is_gatha:
            yazata = self._get_yazata(day)
            result += f" ({yazata['name']})"
        
        # Add drift warning if requested
        if self._show_gregorian_drift:
            drift = self._calculate_drift(gregorian_date)
            result += f" [Drift: {drift} days]"
        
        return result
    
    def _calculate_time(self, gregorian_date: datetime) -> None:
        """Calculate Shenshai calendar date."""
        try:
            # Format the main date string
            shenshai_date = self._format_shenshai_date(gregorian_date)
            
            # Calculate date components
            year, month_idx, day, is_gatha = self._calculate_shenshai_date(gregorian_date)
            
            # Build attribute data
            self._shenshai_calendar = {
                "formatted_date": shenshai_date,
                "year": {
                    "yazdegerdi": year,
                    "gregorian": gregorian_date.year,
                    "era": "Y.Z. (Yazdegerdi Era)"
                },
                "is_gatha_day": is_gatha
            }
            
            if is_gatha:
                # Gatha day information
                gatha = self._shenshai_data["gatha_days"][month_idx]
                self._shenshai_calendar["gatha"] = {
                    "day": day,
                    "name": gatha["name"],
                    "meaning": gatha["meaning"],
                    "total_gatha_days": 5
                }
            else:
                # Regular month information
                month = self._shenshai_data["months"][month_idx]
                self._shenshai_calendar["month"] = {
                    "name": month["name"],
                    "meaning": month["meaning"],
                    "number": month_idx + 1,
                    "days": month["days"]
                }
                self._shenshai_calendar["day"] = {
                    "number": day,
                    "total_days": 30
                }
                
                # Add Yazata information
                if self._show_yazata:
                    yazata = self._get_yazata(day)
                    self._shenshai_calendar["yazata"] = {
                        "name": yazata["name"],
                        "meaning": yazata["meaning"],
                        "day_dedication": day
                    }
                
                # Check for festival
                if self._show_festivals:
                    festival = self._check_festival(month["name"], day, False)
                    if festival:
                        self._shenshai_calendar["festival"] = festival
            
            # Add drift information
            if self._show_gregorian_drift:
                drift = self._calculate_drift(gregorian_date)
                self._shenshai_calendar["calendar_drift"] = {
                    "days": drift,
                    "years": round(drift / 365.2422, 1),
                    "original_nowruz": "Spring Equinox (March 21)",
                    "current_nowruz": "Mid-August (drifting)",
                    "last_synchronized": "1006 CE"
                }
            
            # Calculate days until New Year (Nowruz)
            days_in_year = (day if not is_gatha else 360 + day)
            days_to_nowruz = 365 - days_in_year
            self._shenshai_calendar["days_to_nowruz"] = days_to_nowruz
            
            # Set state
            self._state = shenshai_date
            
        except Exception as e:
            _LOGGER.error(f"Error calculating Shenshai calendar: {e}")
            self._state = "Error"
            self._shenshai_calendar = {"error": str(e)}
    
    def get_calendar_metadata(self) -> Dict[str, Any]:
        """Return calendar metadata."""
        return CALENDAR_INFO