"""Coligny Calendar Plugin for Alternative Time Systems.

Implements the ancient Gaulish lunisolar calendar based on the Coligny bronze tablets.
This calendar features 12 months of 29-30 days with intercalary months for solar alignment.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import logging

from ..sensor_base import AlternativeTimeSensorBase

_LOGGER = logging.getLogger(__name__)

# Calendar metadata and configuration
CALENDAR_INFO = {
    "id": "coligny",
    "version": "2.5.0",
    "name": {
        "en": "Coligny Calendar (Celtic)",
        "de": "Coligny-Kalender (Keltisch)",
        "es": "Calendario de Coligny (Celta)",
        "fr": "Calendrier de Coligny (Celtique)",
        "it": "Calendario di Coligny (Celtico)",
        "nl": "Coligny Kalender (Keltisch)",
        "pl": "Kalendarz z Coligny (Celtycki)",
        "pt": "Calendário de Coligny (Celta)",
        "ru": "Календарь Колиньи (Кельтский)",
        "ja": "コリニー暦（ケルト）",
        "zh": "科利尼历（凯尔特）",
        "ko": "콜리니 달력 (켈트)"
    },
    "description": {
        "en": "Ancient Gaulish lunisolar calendar with 12 months, lucky/unlucky days, and 30-month cycles",
        "de": "Alter gallischer Lunisolarkalender mit 12 Monaten, Glücks-/Unglückstagen und 30-Monats-Zyklen",
        "es": "Antiguo calendario lunisolar galo con 12 meses, días afortunados/desafortunados y ciclos de 30 meses",
        "fr": "Ancien calendrier luni-solaire gaulois avec 12 mois, jours fastes/néfastes et cycles de 30 mois",
        "it": "Antico calendario lunisolare gallico con 12 mesi, giorni fortunati/sfortunati e cicli di 30 mesi",
        "nl": "Oude Gallische lunisolaire kalender met 12 maanden, geluk/ongeluk dagen en 30-maands cycli",
        "pl": "Starożytny galijsko-księżycowo-słoneczny kalendarz z 12 miesiącami, szczęśliwymi/nieszczęśliwymi dniami",
        "pt": "Antigo calendário lunissolar gaulês com 12 meses, dias de sorte/azar e ciclos de 30 meses",
        "ru": "Древний галльский лунно-солнечный календарь с 12 месяцами, счастливыми/несчастливыми днями",
        "ja": "12ヶ月、幸運/不運の日、30ヶ月周期を持つ古代ガリアの太陰太陽暦",
        "zh": "拥有12个月、吉日/凶日和30个月周期的古代高卢阴阳历",
        "ko": "12개월, 행운/불운의 날, 30개월 주기를 가진 고대 갈리아 태음태양력"
    },
    "category": "historical",
    "update_interval": 3600,
    "accuracy": "day",
    "icon": "mdi:celtic-cross",
    "reference_url": "https://en.wikipedia.org/wiki/Coligny_calendar",
    
    # Configuration options for this calendar
    "config_options": {
        "show_day_quality": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show Day Quality (MAT/ANM)",
                "de": "Tagesqualität anzeigen (MAT/ANM)",
                "es": "Mostrar calidad del día (MAT/ANM)",
                "fr": "Afficher la qualité du jour (MAT/ANM)",
                "it": "Mostra qualità del giorno (MAT/ANM)",
                "nl": "Toon dagkwaliteit (MAT/ANM)",
                "pl": "Pokaż jakość dnia (MAT/ANM)",
                "pt": "Mostrar qualidade do dia (MAT/ANM)",
                "ru": "Показать качество дня (MAT/ANM)",
                "ja": "日の質を表示（MAT/ANM）",
                "zh": "显示日期质量（MAT/ANM）",
                "ko": "날짜 품질 표시 (MAT/ANM)"
            },
            "description": {
                "en": "Display whether the day is lucky (MAT/Matus) or unlucky (ANM/Anmatus)",
                "de": "Anzeigen ob der Tag glücklich (MAT/Matus) oder unglücklich (ANM/Anmatus) ist",
                "es": "Mostrar si el día es afortunado (MAT/Matus) o desafortunado (ANM/Anmatus)",
                "fr": "Afficher si le jour est faste (MAT/Matus) ou néfaste (ANM/Anmatus)"
            }
        },
        "show_intercalary": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show Intercalary Months",
                "de": "Schaltmonate anzeigen",
                "es": "Mostrar meses intercalares",
                "fr": "Afficher les mois intercalaires",
                "it": "Mostra mesi intercalari",
                "nl": "Toon schrikkelmaanden",
                "pl": "Pokaż miesiące przestępne",
                "pt": "Mostrar meses intercalares",
                "ru": "Показать вставные месяцы",
                "ja": "閏月を表示",
                "zh": "显示闰月",
                "ko": "윤달 표시"
            }
        },
        "notation_style": {
            "type": "select",
            "options": {
                "abbreviated": {
                    "en": "Abbreviated (SAMON III MAT)",
                    "de": "Abgekürzt (SAMON III MAT)",
                    "es": "Abreviado (SAMON III MAT)",
                    "fr": "Abrégé (SAMON III MAT)",
                    "it": "Abbreviato (SAMON III MAT)",
                    "nl": "Afgekort (SAMON III MAT)",
                    "pl": "Skrócony (SAMON III MAT)",
                    "pt": "Abreviado (SAMON III MAT)",
                    "ru": "Сокращенный (SAMON III MAT)",
                    "ja": "省略形（SAMON III MAT）",
                    "zh": "缩写（SAMON III MAT）",
                    "ko": "약어 (SAMON III MAT)"
                },
                "full": {
                    "en": "Full (Samonios Day 3, Lucky)",
                    "de": "Vollständig (Samonios Tag 3, Glücklich)",
                    "es": "Completo (Samonios Día 3, Afortunado)",
                    "fr": "Complet (Samonios Jour 3, Faste)",
                    "it": "Completo (Samonios Giorno 3, Fortunato)",
                    "nl": "Volledig (Samonios Dag 3, Gelukkig)",
                    "pl": "Pełny (Samonios Dzień 3, Szczęśliwy)",
                    "pt": "Completo (Samonios Dia 3, Sortudo)",
                    "ru": "Полный (Самониос День 3, Счастливый)",
                    "ja": "完全形（サモニオス3日、幸運）",
                    "zh": "完整（萨莫尼奥斯第3天，幸运）",
                    "ko": "전체 (사모니오스 3일, 행운)"
                },
                "mixed": {
                    "en": "Mixed (Samonios III MAT)",
                    "de": "Gemischt (Samonios III MAT)",
                    "es": "Mixto (Samonios III MAT)",
                    "fr": "Mixte (Samonios III MAT)",
                    "it": "Misto (Samonios III MAT)",
                    "nl": "Gemengd (Samonios III MAT)",
                    "pl": "Mieszany (Samonios III MAT)",
                    "pt": "Misto (Samonios III MAT)",
                    "ru": "Смешанный (Самониос III MAT)",
                    "ja": "混合（サモニオスIII MAT）",
                    "zh": "混合（萨莫尼奥斯III MAT）",
                    "ko": "혼합 (사모니오스 III MAT)"
                }
            },
            "default": "mixed",
            "label": {
                "en": "Notation Style",
                "de": "Notationsstil",
                "es": "Estilo de notación",
                "fr": "Style de notation",
                "it": "Stile di notazione",
                "nl": "Notatiestijl",
                "pl": "Styl notacji",
                "pt": "Estilo de notação",
                "ru": "Стиль записи",
                "ja": "表記スタイル",
                "zh": "记法风格",
                "ko": "표기 스타일"
            }
        },
        "show_lustrum": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show 5-Year Lustrum",
                "de": "5-Jahres-Lustrum anzeigen",
                "es": "Mostrar lustro de 5 años",
                "fr": "Afficher le lustre de 5 ans",
                "it": "Mostra lustro di 5 anni",
                "nl": "Toon 5-jarig lustrum",
                "pl": "Pokaż 5-letnie lustrum",
                "pt": "Mostrar lustro de 5 anos",
                "ru": "Показать 5-летний люструм",
                "ja": "5年周期を表示",
                "zh": "显示5年周期",
                "ko": "5년 주기 표시"
            },
            "description": {
                "en": "Display position in the 5-year cycle (62-month lustrum)",
                "de": "Position im 5-Jahres-Zyklus anzeigen (62-Monats-Lustrum)",
                "es": "Mostrar posición en el ciclo de 5 años (lustro de 62 meses)",
                "fr": "Afficher la position dans le cycle de 5 ans (lustre de 62 mois)"
            }
        }
    },
    
    # Coligny calendar data
    "coligny_data": {
        # Month data: name, days, quality (MAT=lucky, ANM=unlucky)
        "months": [
            {"name": "SAMON", "full": "Samonios", "days": 30, "quality": "MAT", "meaning": "Summer's End"},
            {"name": "DVMANN", "full": "Dumannios", "days": 29, "quality": "ANM", "meaning": "Dark Time"},
            {"name": "RIVROS", "full": "Riuros", "days": 30, "quality": "MAT", "meaning": "Frost Time"},
            {"name": "ANAGANTIO", "full": "Anagantios", "days": 29, "quality": "ANM", "meaning": "Indoor Time"},
            {"name": "OGRONIOS", "full": "Ogronios", "days": 30, "quality": "MAT", "meaning": "Ice Time"},
            {"name": "CVTIOS", "full": "Cutios", "days": 30, "quality": "MAT", "meaning": "Wind Time"},
            {"name": "GIAMONIOS", "full": "Giamonios", "days": 29, "quality": "ANM", "meaning": "Winter's End"},
            {"name": "SIMIVIS", "full": "Simiuisonna", "days": 30, "quality": "MAT", "meaning": "Bright Time"},
            {"name": "EQVOS", "full": "Equos", "days": 29, "quality": "ANM", "meaning": "Horse Time"},
            {"name": "ELEMBIV", "full": "Elembiu", "days": 29, "quality": "ANM", "meaning": "Deer Time"},
            {"name": "EDRINI", "full": "Edrinios", "days": 30, "quality": "MAT", "meaning": "Hot Time"},
            {"name": "CANTLOS", "full": "Cantlos", "days": 29, "quality": "ANM", "meaning": "Song Time"}
        ],
        
        # Intercalary months (added for solar alignment)
        "intercalary": [
            {"name": "CIALLOS", "full": "Ciallos", "days": 30, "quality": "MAT", "position": 0},
            {"name": "QVIMON", "full": "Quimon", "days": 30, "quality": "MAT", "position": 30}
        ],
        
        # Special days and markings from the bronze tablets
        "special_days": {
            "IVOS": "Under protection",
            "PRINNI LOUD": "Spring beginning",
            "PRINNI LAG": "Spring waning",
            "INIS R": "Great beginning",
            "AMB": "Around/about",
            "ATENOUX": "Returning night (full moon)"
        },
        
        # Day qualities pattern (simplified from tablet)
        "day_patterns": {
            "standard": ["MAT", "MAT", "ANM", "MAT", "ANM", "MAT", "MAT", "ANM", "MAT", "ANM",
                        "MAT", "MAT", "ANM", "MAT", "ATENOUX", "MAT", "ANM", "MAT", "MAT", "ANM",
                        "MAT", "ANM", "MAT", "MAT", "ANM", "MAT", "ANM", "MAT", "MAT", "ANM"],
            "short": ["MAT", "MAT", "ANM", "MAT", "ANM", "MAT", "MAT", "ANM", "MAT", "ANM",
                     "MAT", "MAT", "ANM", "MAT", "ATENOUX", "MAT", "ANM", "MAT", "MAT", "ANM",
                     "MAT", "ANM", "MAT", "MAT", "ANM", "MAT", "ANM", "MAT", "MAT"]
        },
        
        # 5-year cycle (lustrum) = 62 months total
        "lustrum": {
            "years": 5,
            "months": 62,
            "pattern": [12, 12, 13, 12, 13]  # Months per year (13 = with intercalary)
        },
        
        # Correlation to Gregorian (approximate - debated by scholars)
        # Using 1st Samonios = November 1st as common interpretation
        "correlation": {
            "start_date": datetime(2000, 11, 1),  # Reference date
            "start_month": 0,  # SAMON
            "start_day": 1
        }
    }
}

# Update interval for this sensor
UPDATE_INTERVAL = CALENDAR_INFO["update_interval"]

class ColignyCalendarSensor(AlternativeTimeSensorBase):
    """Sensor for Coligny Celtic Calendar."""
    
    # Class-level update interval
    UPDATE_INTERVAL = UPDATE_INTERVAL
    
    def __init__(self, base_name: str, hass) -> None:
        """Initialize the Coligny calendar sensor."""
        super().__init__(base_name, hass)
        
        # Get translated name from metadata
        calendar_name = self._translate('name', 'Coligny Calendar')
        
        # Set sensor attributes
        self._attr_name = f"{base_name} {calendar_name}"
        self._attr_unique_id = f"{base_name}_coligny_calendar"
        self._attr_icon = CALENDAR_INFO.get("icon", "mdi:celtic-cross")
        
        # Default configuration options
        self._show_day_quality = True
        self._show_intercalary = True
        self._notation_style = "mixed"
        self._show_lustrum = True
        
        # Calendar data
        self._coligny_data = CALENDAR_INFO["coligny_data"]
        
        # Track if options have been loaded
        self._options_loaded = False
        
        _LOGGER.debug(f"Initialized Coligny Calendar sensor: {self._attr_name}")
    
    def _load_options(self) -> None:
        """Load configuration options from config entry."""
        if self._options_loaded:
            return
            
        try:
            options = self.get_plugin_options()
            if options:
                # Update configuration from plugin options
                self._show_day_quality = options.get("show_day_quality", self._show_day_quality)
                self._show_intercalary = options.get("show_intercalary", self._show_intercalary)
                self._notation_style = options.get("notation_style", self._notation_style)
                self._show_lustrum = options.get("show_lustrum", self._show_lustrum)
                
                _LOGGER.debug(f"Coligny sensor loaded options: quality={self._show_day_quality}, "
                            f"intercalary={self._show_intercalary}, style={self._notation_style}, "
                            f"lustrum={self._show_lustrum}")
            else:
                _LOGGER.debug("Coligny sensor using default options - no custom options found")
                
            self._options_loaded = True
        except Exception as e:
            _LOGGER.debug(f"Coligny sensor could not load options yet: {e}")
    
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
        
        # Add Coligny-specific attributes
        if hasattr(self, '_coligny_calendar'):
            attrs.update(self._coligny_calendar)
            
            # Add description in user's language
            attrs["description"] = self._translate('description')
            
            # Add reference
            attrs["reference"] = CALENDAR_INFO.get('reference_url', '')
            
            # Add configuration status
            attrs["config"] = {
                "show_day_quality": self._show_day_quality,
                "show_intercalary": self._show_intercalary,
                "notation_style": self._notation_style,
                "show_lustrum": self._show_lustrum
            }
        
        return attrs
    
    def _calculate_coligny_position(self, earth_date: datetime) -> tuple:
        """Calculate position in Coligny calendar from Gregorian date."""
        # Get reference date
        ref_date = self._coligny_data["correlation"]["start_date"]
        
        # Calculate days since reference
        days_diff = (earth_date.date() - ref_date.date()).days
        
        # Handle negative dates (before reference)
        if days_diff < 0:
            # Go backwards - this is approximate
            days_diff = abs(days_diff)
            years_back = days_diff // 354  # Approximate lunar year
            remaining_days = days_diff % 354
            
            # Calculate position going backwards
            month_index = 11 - (remaining_days // 30)
            day_of_month = 30 - (remaining_days % 30)
            lustrum_year = 5 - (years_back % 5)
            lustrum_number = -(years_back // 5) - 1
            
            return month_index, day_of_month, False, lustrum_year, lustrum_number
        
        # Calculate lustrum position (5-year cycle)
        lustrum_days = 1831  # Approximate days in 5-year cycle (62 months)
        lustrum_number = days_diff // lustrum_days
        days_in_lustrum = days_diff % lustrum_days
        
        # Find year within lustrum
        year_in_lustrum = 0
        days_counted = 0
        
        for year_idx, months_in_year in enumerate(self._coligny_data["lustrum"]["pattern"]):
            year_days = self._calculate_year_days(months_in_year)
            if days_counted + year_days > days_in_lustrum:
                year_in_lustrum = year_idx
                days_in_year = days_in_lustrum - days_counted
                break
            days_counted += year_days
        else:
            year_in_lustrum = 4
            days_in_year = days_in_lustrum - days_counted
        
        # Check if this is an intercalary year
        is_intercalary_year = self._coligny_data["lustrum"]["pattern"][year_in_lustrum] == 13
        
        # Find month and day
        month_index, day_of_month, is_intercalary_month = self._find_month_and_day(
            days_in_year, is_intercalary_year
        )
        
        return month_index, day_of_month, is_intercalary_month, year_in_lustrum + 1, lustrum_number + 1
    
    def _calculate_year_days(self, months_in_year: int) -> int:
        """Calculate total days in a year based on number of months."""
        if months_in_year == 12:
            # Regular year
            return sum(m["days"] for m in self._coligny_data["months"])
        else:
            # Intercalary year (13 months)
            regular_days = sum(m["days"] for m in self._coligny_data["months"])
            intercalary_days = self._coligny_data["intercalary"][0]["days"]
            return regular_days + intercalary_days
    
    def _find_month_and_day(self, days_in_year: int, is_intercalary_year: bool) -> tuple:
        """Find the month and day from days in year."""
        days_counted = 0
        
        # Check for first intercalary month (CIALLOS at beginning)
        if is_intercalary_year and self._coligny_data["intercalary"][0]["position"] == 0:
            intercalary_days = self._coligny_data["intercalary"][0]["days"]
            if days_in_year <= intercalary_days:
                return 0, days_in_year, True  # In CIALLOS
            days_counted += intercalary_days
        
        # Check regular months
        for month_idx, month in enumerate(self._coligny_data["months"]):
            if days_counted + month["days"] >= days_in_year:
                day_of_month = days_in_year - days_counted
                if day_of_month == 0:
                    day_of_month = 1
                return month_idx, day_of_month, False
            days_counted += month["days"]
            
            # Check for mid-year intercalary (QVIMON after 6th month)
            if is_intercalary_year and month_idx == 5:  # After CVTIOS
                intercalary_days = self._coligny_data["intercalary"][1]["days"]
                if days_counted + intercalary_days >= days_in_year:
                    day_of_month = days_in_year - days_counted
                    if day_of_month == 0:
                        day_of_month = 1
                    return 1, day_of_month, True  # In QVIMON
                days_counted += intercalary_days
        
        # Default to last day of last month
        return 11, self._coligny_data["months"][11]["days"], False
    
    def _get_day_quality(self, month_quality: str, day: int, month_days: int) -> str:
        """Determine if a day is MAT (lucky) or ANM (unlucky)."""
        # Special case: ATENOUX (full moon, day 15)
        if day == 15:
            return "ATENOUX"
        
        # Use pattern based on month length
        pattern = self._coligny_data["day_patterns"]["standard" if month_days == 30 else "short"]
        
        if day <= len(pattern):
            day_quality = pattern[day - 1]
        else:
            # For days beyond pattern, use month quality
            day_quality = month_quality
        
        return day_quality
    
    def _format_coligny_date(self, earth_date: datetime) -> str:
        """Format the Coligny date according to display settings."""
        # Reload options
        self._load_options()
        
        # Calculate position
        month_idx, day, is_intercalary, lustrum_year, lustrum_num = self._calculate_coligny_position(earth_date)
        
        # Get month info
        if is_intercalary:
            # Determine which intercalary month
            if month_idx == 0:
                month = self._coligny_data["intercalary"][0]  # CIALLOS
            else:
                month = self._coligny_data["intercalary"][1]  # QVIMON
        else:
            month = self._coligny_data["months"][month_idx]
        
        # Get day quality
        day_quality = self._get_day_quality(month["quality"], day, month["days"])
        
        # Format based on style
        if self._notation_style == "abbreviated":
            # SAMON III MAT
            result = f"{month['name']} {self._roman_numeral(day)}"
            if self._show_day_quality:
                result += f" {day_quality}"
                
        elif self._notation_style == "full":
            # Samonios Day 3, Lucky
            quality_text = {
                "MAT": {"en": "Lucky", "de": "Glücklich", "fr": "Faste"},
                "ANM": {"en": "Unlucky", "de": "Unglücklich", "fr": "Néfaste"},
                "ATENOUX": {"en": "Full Moon", "de": "Vollmond", "fr": "Pleine Lune"}
            }
            
            lang = self._user_language[:2] if self._user_language else "en"
            q_text = quality_text.get(day_quality, {}).get(lang, day_quality)
            
            result = f"{month['full']} Day {day}"
            if self._show_day_quality:
                result += f", {q_text}"
                
        else:  # mixed
            # Samonios III MAT
            result = f"{month['full']} {self._roman_numeral(day)}"
            if self._show_day_quality:
                result += f" {day_quality}"
        
        # Add intercalary marker
        if is_intercalary and self._show_intercalary:
            result = f"[INT] {result}"
        
        # Add lustrum position
        if self._show_lustrum:
            result += f" | L{lustrum_num}.{lustrum_year}"
        
        return result
    
    def _roman_numeral(self, num: int) -> str:
        """Convert number to Roman numeral."""
        values = [
            (30, "XXX"), (20, "XX"), (10, "X"),
            (9, "IX"), (5, "V"), (4, "IV"), (1, "I")
        ]
        result = ""
        for value, numeral in values:
            count = num // value
            if count:
                result += numeral * count
                num -= value * count
        return result or "I"
    
    def _calculate_time(self, earth_date: datetime) -> None:
        """Calculate Coligny calendar date."""
        try:
            # Format the main date string
            coligny_date = self._format_coligny_date(earth_date)
            
            # Calculate position
            month_idx, day, is_intercalary, lustrum_year, lustrum_num = self._calculate_coligny_position(earth_date)
            
            # Get month info
            if is_intercalary:
                if month_idx == 0:
                    month = self._coligny_data["intercalary"][0]
                else:
                    month = self._coligny_data["intercalary"][1]
            else:
                month = self._coligny_data["months"][month_idx]
            
            # Get day quality
            day_quality = self._get_day_quality(month["quality"], day, month["days"])
            
            # Calculate month in year (1-12 or 1-13)
            if is_intercalary:
                if month_idx == 0:  # CIALLOS at start
                    month_in_year = 1
                else:  # QVIMON after month 6
                    month_in_year = 7
            else:
                month_in_year = month_idx + 1
                if lustrum_year in [3, 5] and month_idx >= 6:  # After intercalary
                    month_in_year += 1
            
            # Build attribute data
            self._coligny_calendar = {
                "formatted_date": coligny_date,
                "month": {
                    "name": month["name"],
                    "full_name": month["full"],
                    "days": month["days"],
                    "quality": month["quality"],
                    "meaning": month.get("meaning", ""),
                    "is_intercalary": is_intercalary
                },
                "day": {
                    "number": day,
                    "roman": self._roman_numeral(day),
                    "quality": day_quality,
                    "is_lucky": day_quality == "MAT",
                    "is_unlucky": day_quality == "ANM",
                    "is_atenoux": day_quality == "ATENOUX"
                },
                "lustrum": {
                    "number": lustrum_num,
                    "year": lustrum_year,
                    "total_years": 5,
                    "month_in_cycle": ((lustrum_year - 1) * 12) + month_in_year,
                    "total_months": 62
                },
                "year": {
                    "months": 13 if lustrum_year in [3, 5] else 12,
                    "is_intercalary": lustrum_year in [3, 5],
                    "gregorian": earth_date.year
                }
            }
            
            # Add special day info if applicable
            if day == 15:
                self._coligny_calendar["special"] = "ATENOUX - Full Moon/Returning Night"
            elif day == 1:
                self._coligny_calendar["special"] = "New Month Beginning"
            
            # Set state
            self._state = coligny_date
            
        except Exception as e:
            _LOGGER.error(f"Error calculating Coligny calendar: {e}")
            self._state = "Error"
            self._coligny_calendar = {"error": str(e)}
    
    def get_calendar_metadata(self) -> Dict[str, Any]:
        """Return calendar metadata."""
        return CALENDAR_INFO