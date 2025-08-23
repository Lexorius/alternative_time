"""Aztec Calendar Plugin for Alternative Time Systems.

Implements the dual calendar system of the Aztec civilization:
- Tonalpohualli: 260-day sacred calendar (20 day signs × 13 numbers)
- Xiuhpohualli: 365-day solar calendar (18 months × 20 days + 5 nemontemi)
- 52-year Calendar Round (xiuhmolpilli)
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging

from ..sensor import AlternativeTimeSensorBase

_LOGGER = logging.getLogger(__name__)

# Calendar metadata and configuration
CALENDAR_INFO = {
    "id": "aztec",
    "version": "2.5.0",
    "name": {
        "en": "Aztec Calendar",
        "de": "Azteken-Kalender",
        "es": "Calendario Azteca",
        "fr": "Calendrier Aztèque",
        "it": "Calendario Azteco",
        "nl": "Azteekse Kalender",
        "pl": "Kalendarz Aztecki",
        "pt": "Calendário Asteca",
        "ru": "Календарь Ацтеков",
        "ja": "アステカ暦",
        "zh": "阿兹特克历",
        "ko": "아즈텍 달력"
    },
    "description": {
        "en": "Dual calendar system of the Aztec Empire: Tonalpohualli (260-day sacred) and Xiuhpohualli (365-day solar) with 52-year cycles",
        "de": "Duales Kalendersystem des Aztekenreichs: Tonalpohualli (260-Tage heilig) und Xiuhpohualli (365-Tage solar) mit 52-Jahres-Zyklen",
        "es": "Sistema de calendario dual del Imperio Azteca: Tonalpohualli (260 días sagrado) y Xiuhpohualli (365 días solar) con ciclos de 52 años",
        "fr": "Système de calendrier double de l'Empire Aztèque: Tonalpohualli (260 jours sacré) et Xiuhpohualli (365 jours solaire) avec cycles de 52 ans",
        "it": "Sistema di calendario doppio dell'Impero Azteco: Tonalpohualli (260 giorni sacro) e Xiuhpohualli (365 giorni solare) con cicli di 52 anni",
        "nl": "Dubbel kalendersysteem van het Aztekenrijk: Tonalpohualli (260 dagen heilig) en Xiuhpohualli (365 dagen zonne) met 52-jaar cycli",
        "pl": "Podwójny system kalendarzowy Imperium Azteków: Tonalpohualli (260 dni święty) i Xiuhpohualli (365 dni słoneczny) z cyklami 52-letnimi",
        "pt": "Sistema de calendário duplo do Império Asteca: Tonalpohualli (260 dias sagrado) e Xiuhpohualli (365 dias solar) com ciclos de 52 anos",
        "ru": "Двойная календарная система Империи Ацтеков: Тональпоуалли (260 дней священный) и Шиупоуалли (365 дней солнечный) с 52-летними циклами",
        "ja": "アステカ帝国の二重暦システム：トナルポワリ（260日の神聖暦）とシウポワリ（365日の太陽暦）、52年周期",
        "zh": "阿兹特克帝国的双历系统：托纳尔波瓦利（260天神圣历）和休波瓦利（365天太阳历），52年周期",
        "ko": "아즈텍 제국의 이중 달력 시스템: 토날포우알리(260일 신성력)와 시우포우알리(365일 태양력), 52년 주기"
    },
    "category": "historical",
    "update_interval": 3600,
    "accuracy": "day",
    "icon": "mdi:pyramid",
    "reference_url": "https://en.wikipedia.org/wiki/Aztec_calendar",
    
    # Configuration options for this calendar
    "config_options": {
        "display_format": {
            "type": "select",
            "options": {
                "combined": {
                    "en": "Combined (Both calendars)",
                    "de": "Kombiniert (Beide Kalender)",
                    "es": "Combinado (Ambos calendarios)",
                    "fr": "Combiné (Les deux calendriers)",
                    "it": "Combinato (Entrambi i calendari)",
                    "nl": "Gecombineerd (Beide kalenders)",
                    "pl": "Połączony (Oba kalendarze)",
                    "pt": "Combinado (Ambos calendários)",
                    "ru": "Комбинированный (Оба календаря)",
                    "ja": "組み合わせ（両方の暦）",
                    "zh": "组合（两个历法）",
                    "ko": "결합 (두 달력)"
                },
                "tonalpohualli": {
                    "en": "Tonalpohualli only (Sacred)",
                    "de": "Nur Tonalpohualli (Heilig)",
                    "es": "Solo Tonalpohualli (Sagrado)",
                    "fr": "Tonalpohualli seulement (Sacré)",
                    "it": "Solo Tonalpohualli (Sacro)",
                    "nl": "Alleen Tonalpohualli (Heilig)",
                    "pl": "Tylko Tonalpohualli (Święty)",
                    "pt": "Apenas Tonalpohualli (Sagrado)",
                    "ru": "Только Тональпоуалли (Священный)",
                    "ja": "トナルポワリのみ（神聖暦）",
                    "zh": "仅托纳尔波瓦利（神圣历）",
                    "ko": "토날포우알리만 (신성력)"
                },
                "xiuhpohualli": {
                    "en": "Xiuhpohualli only (Solar)",
                    "de": "Nur Xiuhpohualli (Solar)",
                    "es": "Solo Xiuhpohualli (Solar)",
                    "fr": "Xiuhpohualli seulement (Solaire)",
                    "it": "Solo Xiuhpohualli (Solare)",
                    "nl": "Alleen Xiuhpohualli (Zonne)",
                    "pl": "Tylko Xiuhpohualli (Słoneczny)",
                    "pt": "Apenas Xiuhpohualli (Solar)",
                    "ru": "Только Шиупоуалли (Солнечный)",
                    "ja": "シウポワリのみ（太陽暦）",
                    "zh": "仅休波瓦利（太阳历）",
                    "ko": "시우포우알리만 (태양력)"
                }
            },
            "default": "combined",
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
            }
        },
        "show_meanings": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show Day Sign Meanings",
                "de": "Tageszeichen-Bedeutungen anzeigen",
                "es": "Mostrar significados de signos diarios",
                "fr": "Afficher les significations des signes du jour",
                "it": "Mostra significati dei segni del giorno",
                "nl": "Toon betekenissen van dagtekens",
                "pl": "Pokaż znaczenia znaków dnia",
                "pt": "Mostrar significados dos signos do dia",
                "ru": "Показать значения дневных знаков",
                "ja": "日の記号の意味を表示",
                "zh": "显示日符号含义",
                "ko": "날 기호 의미 표시"
            }
        },
        "show_year_bearer": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show Year Bearer",
                "de": "Jahresträger anzeigen",
                "es": "Mostrar portador del año",
                "fr": "Afficher le porteur de l'année",
                "it": "Mostra portatore dell'anno",
                "nl": "Toon jaardrager",
                "pl": "Pokaż nosiciela roku",
                "pt": "Mostrar portador do ano",
                "ru": "Показать носителя года",
                "ja": "年の担い手を表示",
                "zh": "显示年份承载者",
                "ko": "연도 운반자 표시"
            }
        },
        "show_52_year_cycle": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show 52-Year Cycle Position",
                "de": "52-Jahres-Zyklus Position anzeigen",
                "es": "Mostrar posición del ciclo de 52 años",
                "fr": "Afficher la position du cycle de 52 ans",
                "it": "Mostra posizione del ciclo di 52 anni",
                "nl": "Toon 52-jaar cyclus positie",
                "pl": "Pokaż pozycję cyklu 52-letniego",
                "pt": "Mostrar posição do ciclo de 52 anos",
                "ru": "Показать позицию 52-летнего цикла",
                "ja": "52年周期の位置を表示",
                "zh": "显示52年周期位置",
                "ko": "52년 주기 위치 표시"
            }
        },
        "use_nahuatl_names": {
            "type": "boolean",
            "default": False,
            "label": {
                "en": "Use Nahuatl Names",
                "de": "Nahuatl-Namen verwenden",
                "es": "Usar nombres náhuatl",
                "fr": "Utiliser les noms nahuatl",
                "it": "Usa nomi nahuatl",
                "nl": "Gebruik Nahuatl namen",
                "pl": "Użyj nazw nahuatl",
                "pt": "Usar nomes nahuatl",
                "ru": "Использовать имена науатль",
                "ja": "ナワトル語の名前を使用",
                "zh": "使用纳瓦特尔名称",
                "ko": "나우아틀 이름 사용"
            },
            "description": {
                "en": "Display names in original Nahuatl language instead of translations",
                "de": "Namen in originaler Nahuatl-Sprache statt Übersetzungen anzeigen",
                "es": "Mostrar nombres en idioma náhuatl original en lugar de traducciones",
                "fr": "Afficher les noms en langue nahuatl originale au lieu des traductions",
                "it": "Mostra i nomi nella lingua nahuatl originale invece delle traduzioni",
                "nl": "Toon namen in originele Nahuatl taal in plaats van vertalingen",
                "pl": "Wyświetl nazwy w oryginalnym języku nahuatl zamiast tłumaczeń",
                "pt": "Exibir nomes no idioma nahuatl original em vez de traduções",
                "ru": "Показывать имена на оригинальном языке науатль вместо переводов",
                "ja": "翻訳の代わりに元のナワトル語で名前を表示",
                "zh": "显示原始纳瓦特尔语名称而不是翻译",
                "ko": "번역 대신 원래 나우아틀 언어로 이름 표시"
            }
        }
    },
    
    # Aztec calendar data
    "aztec_data": {
        # Tonalpohualli - 260-day sacred calendar
        "tonalpohualli": {
            "day_signs": [
                {"nahuatl": "Cipactli", "en": "Crocodile", "de": "Krokodil", "es": "Cocodrilo"},
                {"nahuatl": "Ehecatl", "en": "Wind", "de": "Wind", "es": "Viento"},
                {"nahuatl": "Calli", "en": "House", "de": "Haus", "es": "Casa"},
                {"nahuatl": "Cuetzpalin", "en": "Lizard", "de": "Eidechse", "es": "Lagarto"},
                {"nahuatl": "Coatl", "en": "Serpent", "de": "Schlange", "es": "Serpiente"},
                {"nahuatl": "Miquiztli", "en": "Death", "de": "Tod", "es": "Muerte"},
                {"nahuatl": "Mazatl", "en": "Deer", "de": "Hirsch", "es": "Venado"},
                {"nahuatl": "Tochtli", "en": "Rabbit", "de": "Kaninchen", "es": "Conejo"},
                {"nahuatl": "Atl", "en": "Water", "de": "Wasser", "es": "Agua"},
                {"nahuatl": "Itzcuintli", "en": "Dog", "de": "Hund", "es": "Perro"},
                {"nahuatl": "Ozomatli", "en": "Monkey", "de": "Affe", "es": "Mono"},
                {"nahuatl": "Malinalli", "en": "Grass", "de": "Gras", "es": "Hierba"},
                {"nahuatl": "Acatl", "en": "Reed", "de": "Schilf", "es": "Caña"},
                {"nahuatl": "Ocelotl", "en": "Jaguar", "de": "Jaguar", "es": "Jaguar"},
                {"nahuatl": "Cuauhtli", "en": "Eagle", "de": "Adler", "es": "Águila"},
                {"nahuatl": "Cozcacuauhtli", "en": "Vulture", "de": "Geier", "es": "Buitre"},
                {"nahuatl": "Ollin", "en": "Movement", "de": "Bewegung", "es": "Movimiento"},
                {"nahuatl": "Tecpatl", "en": "Flint", "de": "Feuerstein", "es": "Pedernal"},
                {"nahuatl": "Quiahuitl", "en": "Rain", "de": "Regen", "es": "Lluvia"},
                {"nahuatl": "Xochitl", "en": "Flower", "de": "Blume", "es": "Flor"}
            ],
            "numbers": 13  # 1-13 trecena
        },
        
        # Xiuhpohualli - 365-day solar calendar
        "xiuhpohualli": {
            "months": [
                {"nahuatl": "Izcalli", "en": "Growth", "de": "Wachstum", "es": "Crecimiento"},
                {"nahuatl": "Atlcahualo", "en": "Water Left", "de": "Wasser verlassen", "es": "Agua dejada"},
                {"nahuatl": "Tlacaxipehualiztli", "en": "Flaying of Men", "de": "Häutung der Menschen", "es": "Desollamiento"},
                {"nahuatl": "Tozoztontli", "en": "Small Vigil", "de": "Kleine Wache", "es": "Vigilia pequeña"},
                {"nahuatl": "Hueytozoztli", "en": "Great Vigil", "de": "Große Wache", "es": "Gran vigilia"},
                {"nahuatl": "Toxcatl", "en": "Drought", "de": "Dürre", "es": "Sequía"},
                {"nahuatl": "Etzalcualiztli", "en": "Eating Corn", "de": "Mais essen", "es": "Comer maíz"},
                {"nahuatl": "Tecuilhuitontli", "en": "Small Feast", "de": "Kleines Fest", "es": "Fiesta pequeña"},
                {"nahuatl": "Hueytecuilhuitl", "en": "Great Feast", "de": "Großes Fest", "es": "Gran fiesta"},
                {"nahuatl": "Tlaxochimaco", "en": "Flower Giving", "de": "Blumen geben", "es": "Dar flores"},
                {"nahuatl": "Xocotlhuetzi", "en": "Fruit Falls", "de": "Frucht fällt", "es": "Caída de fruta"},
                {"nahuatl": "Ochpaniztli", "en": "Sweeping", "de": "Kehren", "es": "Barrido"},
                {"nahuatl": "Teotleco", "en": "Gods Arrive", "de": "Götter kommen", "es": "Llegada de dioses"},
                {"nahuatl": "Tepeilhuitl", "en": "Mountain Feast", "de": "Bergfest", "es": "Fiesta montaña"},
                {"nahuatl": "Quecholli", "en": "Precious Feather", "de": "Kostbare Feder", "es": "Pluma preciosa"},
                {"nahuatl": "Panquetzaliztli", "en": "Raising Banners", "de": "Banner heben", "es": "Izar banderas"},
                {"nahuatl": "Atemoztli", "en": "Water Falls", "de": "Wasser fällt", "es": "Caída de agua"},
                {"nahuatl": "Tititl", "en": "Stretching", "de": "Dehnung", "es": "Estiramiento"}
            ],
            "days_per_month": 20,
            "nemontemi": 5  # 5 unlucky days at year end
        },
        
        # Year bearers (4 possible day signs that can start a year)
        "year_bearers": ["Acatl", "Tecpatl", "Calli", "Tochtli"],
        
        # Correlation constant (August 13, 1521 = 1 Coatl, 2 Xochitl)
        # Using Caso correlation
        "correlation_date": datetime(1521, 8, 13)
    }
}

# Update interval for this sensor
UPDATE_INTERVAL = CALENDAR_INFO["update_interval"]

class AztecCalendarSensor(AlternativeTimeSensorBase):
    """Sensor for Aztec Calendar."""
    
    # Class-level update interval
    UPDATE_INTERVAL = UPDATE_INTERVAL
    
    def __init__(self, base_name: str, hass) -> None:
        """Initialize the Aztec calendar sensor."""
        super().__init__(base_name, hass)
        
        # Get translated name from metadata
        calendar_name = self._translate('name', 'Aztec Calendar')
        
        # Set sensor attributes
        self._attr_name = f"{base_name} {calendar_name}"
        self._attr_unique_id = f"{base_name}_aztec_calendar"
        self._attr_icon = CALENDAR_INFO.get("icon", "mdi:pyramid")
        
        # Default configuration options
        self._display_format = "combined"
        self._show_meanings = True
        self._show_year_bearer = True
        self._show_52_year_cycle = True
        self._use_nahuatl_names = False
        
        # Calendar data
        self._aztec_data = CALENDAR_INFO["aztec_data"]
        
        # Correlation date
        self._correlation_date = self._aztec_data["correlation_date"]
        
        # Track if options have been loaded
        self._options_loaded = False
        
        _LOGGER.debug(f"Initialized Aztec Calendar sensor: {self._attr_name}")
    
    def _load_options(self) -> None:
        """Load configuration options from config entry."""
        if self._options_loaded:
            return
            
        try:
            options = self.get_plugin_options()
            if options:
                # Update configuration from plugin options
                self._display_format = options.get("display_format", self._display_format)
                self._show_meanings = options.get("show_meanings", self._show_meanings)
                self._show_year_bearer = options.get("show_year_bearer", self._show_year_bearer)
                self._show_52_year_cycle = options.get("show_52_year_cycle", self._show_52_year_cycle)
                self._use_nahuatl_names = options.get("use_nahuatl_names", self._use_nahuatl_names)
                
                _LOGGER.debug(f"Aztec sensor loaded options: format={self._display_format}, "
                            f"meanings={self._show_meanings}, year_bearer={self._show_year_bearer}, "
                            f"52_cycle={self._show_52_year_cycle}, nahuatl={self._use_nahuatl_names}")
            else:
                _LOGGER.debug("Aztec sensor using default options - no custom options found")
                
            self._options_loaded = True
        except Exception as e:
            _LOGGER.debug(f"Aztec sensor could not load options yet: {e}")
    
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
        
        # Add Aztec-specific attributes
        if hasattr(self, '_aztec_calendar'):
            attrs.update(self._aztec_calendar)
            
            # Add description in user's language
            attrs["description"] = self._translate('description')
            
            # Add reference
            attrs["reference"] = CALENDAR_INFO.get('reference_url', '')
            
            # Add configuration status
            attrs["config"] = {
                "display_format": self._display_format,
                "show_meanings": self._show_meanings,
                "show_year_bearer": self._show_year_bearer,
                "show_52_year_cycle": self._show_52_year_cycle,
                "use_nahuatl_names": self._use_nahuatl_names
            }
        
        return attrs
    
    def _get_day_name(self, sign: dict, lang: str = None) -> str:
        """Get the day sign name in the appropriate language."""
        if self._use_nahuatl_names:
            return sign["nahuatl"]
        
        lang = lang or self._user_language
        if lang in sign:
            return sign[lang]
        elif lang[:2] in sign:  # Try language code without region
            return sign[lang[:2]]
        else:
            return sign.get("en", sign["nahuatl"])
    
    def _get_month_name(self, month: dict, lang: str = None) -> str:
        """Get the month name in the appropriate language."""
        if self._use_nahuatl_names:
            return month["nahuatl"]
        
        lang = lang or self._user_language
        if lang in month:
            return month[lang]
        elif lang[:2] in month:  # Try language code without region
            return month[lang[:2]]
        else:
            return month.get("en", month["nahuatl"])
    
    def _calculate_tonalpohualli(self, days_since_correlation: int) -> tuple:
        """Calculate the Tonalpohualli (260-day) position."""
        # The correlation date is 1 Coatl (5th day sign, number 1)
        # Day signs cycle every 20 days, numbers every 13 days
        
        # Starting position at correlation date
        start_day_sign = 4  # Coatl is the 5th sign (index 4)
        start_number = 1
        
        # Calculate current position
        current_day_sign = (start_day_sign + days_since_correlation) % 20
        current_number = ((start_number - 1 + days_since_correlation) % 13) + 1
        
        return current_number, current_day_sign
    
    def _calculate_xiuhpohualli(self, days_since_correlation: int) -> tuple:
        """Calculate the Xiuhpohualli (365-day) position."""
        # The correlation date is 2 Xochitl (20th month, day 2)
        # Note: Xochitl is actually day 2 of the nemontemi period
        
        # Starting position (day 362 of the year - 2nd nemontemi day)
        start_day_of_year = 361  # 0-indexed
        
        # Calculate current day of year
        current_day_of_year = (start_day_of_year + days_since_correlation) % 365
        
        # Determine month and day
        if current_day_of_year < 360:  # Regular months
            month_index = current_day_of_year // 20
            day_of_month = (current_day_of_year % 20) + 1
            is_nemontemi = False
        else:  # Nemontemi days
            month_index = 18  # Special index for nemontemi
            day_of_month = current_day_of_year - 359
            is_nemontemi = True
        
        return month_index, day_of_month, is_nemontemi
    
    def _calculate_year_info(self, days_since_correlation: int) -> tuple:
        """Calculate year bearer and cycle information."""
        # Years are named after the Tonalpohualli day that falls on the first day of the year
        # Only 4 day signs can be year bearers: Acatl, Tecpatl, Calli, Tochtli
        
        # Calculate which year we're in (365-day years)
        years_since_correlation = days_since_correlation // 365
        
        # Year bearers cycle every 4 years, numbers cycle every 13 years
        # The correlation year (1521) was 3-Calli
        year_bearer_index = (2 + years_since_correlation) % 4  # Calli is index 2
        year_number = ((3 - 1 + years_since_correlation) % 13) + 1
        
        # Map to actual year bearer names
        year_bearers_indices = [12, 17, 2, 7]  # Acatl, Tecpatl, Calli, Tochtli indices
        year_bearer_sign = year_bearers_indices[year_bearer_index]
        
        # Calculate 52-year cycle position
        cycle_year = (years_since_correlation % 52) + 1
        cycle_number = (years_since_correlation // 52) + 1
        
        return year_bearer_sign, year_number, cycle_year, cycle_number
    
    def _format_aztec_date(self, earth_time: datetime) -> str:
        """Format the Aztec date according to display settings."""
        # Reload options
        self._load_options()
        
        # Calculate days since correlation
        days_diff = (earth_time.date() - self._correlation_date.date()).days
        
        # Calculate positions in both calendars
        tonal_number, tonal_sign_index = self._calculate_tonalpohualli(days_diff)
        xiuh_month_index, xiuh_day, is_nemontemi = self._calculate_xiuhpohualli(days_diff)
        year_bearer_index, year_number, cycle_year, cycle_number = self._calculate_year_info(days_diff)
        
        # Get names
        tonal_sign = self._aztec_data["tonalpohualli"]["day_signs"][tonal_sign_index]
        tonal_name = self._get_day_name(tonal_sign)
        
        year_bearer_sign = self._aztec_data["tonalpohualli"]["day_signs"][year_bearer_index]
        year_bearer_name = self._get_day_name(year_bearer_sign)
        
        # Format based on display setting
        if self._display_format == "tonalpohualli":
            result = f"{tonal_number} {tonal_name}"
            if self._show_meanings and not self._use_nahuatl_names:
                result += f" ({tonal_sign['nahuatl']})"
                
        elif self._display_format == "xiuhpohualli":
            if is_nemontemi:
                month_name = "Nemontemi"
                result = f"{month_name} {xiuh_day}"
            else:
                xiuh_month = self._aztec_data["xiuhpohualli"]["months"][xiuh_month_index]
                month_name = self._get_month_name(xiuh_month)
                result = f"{xiuh_day} {month_name}"
            
            if self._show_year_bearer:
                result += f", {year_number}-{year_bearer_name}"
                
        else:  # combined
            # Tonalpohualli part
            tonal_part = f"{tonal_number} {tonal_name}"
            
            # Xiuhpohualli part
            if is_nemontemi:
                xiuh_part = f"Nemontemi {xiuh_day}"
            else:
                xiuh_month = self._aztec_data["xiuhpohualli"]["months"][xiuh_month_index]
                month_name = self._get_month_name(xiuh_month)
                xiuh_part = f"{xiuh_day} {month_name}"
            
            result = f"{tonal_part} | {xiuh_part}"
            
            if self._show_year_bearer:
                result += f" | {year_number}-{year_bearer_name}"
            
            if self._show_52_year_cycle:
                result += f" | Year {cycle_year}/52"
        
        return result
    
    def _calculate_time(self, earth_time: datetime) -> None:
        """Calculate Aztec calendar date."""
        try:
            # Format the main date string
            aztec_date = self._format_aztec_date(earth_time)
            
            # Calculate all components for attributes
            days_diff = (earth_time.date() - self._correlation_date.date()).days
            
            tonal_number, tonal_sign_index = self._calculate_tonalpohualli(days_diff)
            xiuh_month_index, xiuh_day, is_nemontemi = self._calculate_xiuhpohualli(days_diff)
            year_bearer_index, year_number, cycle_year, cycle_number = self._calculate_year_info(days_diff)
            
            # Get all relevant data
            tonal_sign = self._aztec_data["tonalpohualli"]["day_signs"][tonal_sign_index]
            year_bearer_sign = self._aztec_data["tonalpohualli"]["day_signs"][year_bearer_index]
            
            # Build attribute data
            self._aztec_calendar = {
                "formatted_date": aztec_date,
                "tonalpohualli": {
                    "number": tonal_number,
                    "day_sign": self._get_day_name(tonal_sign),
                    "day_sign_nahuatl": tonal_sign["nahuatl"],
                    "day_sign_meaning": tonal_sign.get("en", ""),
                    "position": (tonal_number - 1) * 20 + tonal_sign_index + 1,
                    "total_days": 260
                },
                "xiuhpohualli": {
                    "day": xiuh_day,
                    "is_nemontemi": is_nemontemi
                },
                "year": {
                    "number": year_number,
                    "bearer": self._get_day_name(year_bearer_sign),
                    "bearer_nahuatl": year_bearer_sign["nahuatl"],
                    "gregorian": earth_time.year
                },
                "cycle": {
                    "year_in_cycle": cycle_year,
                    "cycle_number": cycle_number,
                    "total_years": 52
                },
                "new_fire_ceremony": cycle_year == 52
            }
            
            # Add month info if not nemontemi
            if not is_nemontemi:
                xiuh_month = self._aztec_data["xiuhpohualli"]["months"][xiuh_month_index]
                self._aztec_calendar["xiuhpohualli"]["month"] = self._get_month_name(xiuh_month)
                self._aztec_calendar["xiuhpohualli"]["month_nahuatl"] = xiuh_month["nahuatl"]
                self._aztec_calendar["xiuhpohualli"]["month_meaning"] = xiuh_month.get("en", "")
                self._aztec_calendar["xiuhpohualli"]["month_number"] = xiuh_month_index + 1
            
            # Calculate next New Fire Ceremony
            years_to_new_fire = 52 - cycle_year
            if years_to_new_fire == 0:
                self._aztec_calendar["next_new_fire"] = "Today!"
            else:
                self._aztec_calendar["next_new_fire"] = f"In {years_to_new_fire} years"
            
            # Set state
            self._state = aztec_date
            
        except Exception as e:
            _LOGGER.error(f"Error calculating Aztec calendar: {e}")
            self._state = "Error"
            self._aztec_calendar = {"error": str(e)}
    
    def get_calendar_metadata(self) -> Dict[str, Any]:
        """Return calendar metadata."""
        return CALENDAR_INFO

# Export the sensor class
__all__ = ["AztecCalendarSensor", "CALENDAR_INFO", "UPDATE_INTERVAL"]