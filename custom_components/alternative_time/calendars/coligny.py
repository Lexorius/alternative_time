"""Coligny Calendar Plugin for Alternative Time Systems.

Implements the ancient Gaulish lunisolar calendar based on the Coligny bronze tablets.
This calendar features 12 months of 29-30 days with intercalary months for solar alignment.

IMPORTANT: This is a scholarly reconstruction based on fragmentary archaeological evidence.
Only about 40% of the original bronze tablets survived, and many interpretations remain debated.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import logging

from ..sensor import AlternativeTimeSensorBase

_LOGGER = logging.getLogger(__name__)

# Calendar metadata and configuration
CALENDAR_INFO = {
    "id": "coligny",
    "version": "2.5.1",
    "name": {
        "en": "Coligny Calendar (Archaeological)",
        "de": "Coligny-Kalender (Archäologisch)",
        "es": "Calendario de Coligny (Arqueológico)",
        "fr": "Calendrier de Coligny (Archéologique)",
        "it": "Calendario di Coligny (Archeologico)",
        "nl": "Coligny Kalender (Archeologisch)",
        "pl": "Kalendarz z Coligny (Archeologiczny)",
        "pt": "Calendário de Coligny (Arqueológico)",
        "ru": "Календарь Колиньи (Археологический)",
        "ja": "コリニー暦（考古学的）",
        "zh": "科利尼历（考古学）",
        "ko": "콜리니 달력 (고고학적)"
    },
    "description": {
        "en": "Gaulish calendar from 2nd century CE bronze tablets (scholarly reconstruction, ~40% preserved)",
        "de": "Gallischer Kalender aus Bronzetafeln des 2. Jh. n.Chr. (wissenschaftliche Rekonstruktion, ~40% erhalten)",
        "es": "Calendario galo de tablillas de bronce del siglo II d.C. (reconstrucción académica, ~40% preservado)",
        "fr": "Calendrier gaulois sur tablettes de bronze du 2e siècle ap. J.-C. (reconstruction savante, ~40% préservé)",
        "it": "Calendario gallico da tavolette di bronzo del II secolo d.C. (ricostruzione accademica, ~40% preservato)",
        "nl": "Gallische kalender van bronzen tabletten uit 2e eeuw n.Chr. (wetenschappelijke reconstructie, ~40% bewaard)",
        "pl": "Kalendarz galijski z brązowych tabliczek z II w. n.e. (rekonstrukcja naukowa, ~40% zachowane)",
        "pt": "Calendário gaulês de tábuas de bronze do século II d.C. (reconstrução acadêmica, ~40% preservado)",
        "ru": "Галльский календарь с бронзовых табличек II века н.э. (научная реконструкция, ~40% сохранилось)",
        "ja": "紀元2世紀のブロンズ板からのガリア暦（学術的再構築、約40％保存）",
        "zh": "公元2世纪青铜板上的高卢历（学术重建，约40%保存）",
        "ko": "2세기 청동판의 갈리아 달력 (학술적 재구성, 약 40% 보존)"
    },
    "category": "historical",
    "update_interval": 3600,
    "accuracy": "day",
    "icon": "mdi:celtic-cross",
    "reference_url": "https://en.wikipedia.org/wiki/Coligny_calendar",
    
    # Scientific disclaimer
    "disclaimer": {
        "en": "⚠️ SCHOLARLY RECONSTRUCTION: Based on fragmentary bronze tablets (Musée gallo-romain de Lyon). Many interpretations remain debated among scholars. Correlation with modern calendar is uncertain.",
        "de": "⚠️ WISSENSCHAFTLICHE REKONSTRUKTION: Basiert auf fragmentarischen Bronzetafeln (Musée gallo-romain de Lyon). Viele Interpretationen sind unter Gelehrten umstritten. Korrelation mit modernem Kalender ist unsicher.",
        "es": "⚠️ RECONSTRUCCIÓN ACADÉMICA: Basada en tablillas de bronce fragmentarias (Musée gallo-romain de Lyon). Muchas interpretaciones siguen siendo debatidas. La correlación con el calendario moderno es incierta.",
        "fr": "⚠️ RECONSTRUCTION SAVANTE: Basée sur des tablettes de bronze fragmentaires (Musée gallo-romain de Lyon). De nombreuses interprétations restent débattues. La corrélation avec le calendrier moderne est incertaine.",
        "it": "⚠️ RICOSTRUZIONE ACCADEMICA: Basata su tavolette di bronzo frammentarie (Musée gallo-romain de Lyon). Molte interpretazioni rimangono dibattute. La correlazione con il calendario moderno è incerta.",
        "nl": "⚠️ WETENSCHAPPELIJKE RECONSTRUCTIE: Gebaseerd op fragmentarische bronzen tabletten (Musée gallo-romain de Lyon). Veel interpretaties blijven omstreden. Correlatie met moderne kalender is onzeker.",
        "pl": "⚠️ REKONSTRUKCJA NAUKOWA: Oparta na fragmentarycznych tabliczkach z brązu (Musée gallo-romain de Lyon). Wiele interpretacji pozostaje spornych. Korelacja z nowoczesnym kalendarzem jest niepewna.",
        "pt": "⚠️ RECONSTRUÇÃO ACADÊMICA: Baseada em tábuas de bronze fragmentárias (Musée gallo-romain de Lyon). Muitas interpretações permanecem debatidas. A correlação com o calendário moderno é incerta.",
        "ru": "⚠️ НАУЧНАЯ РЕКОНСТРУКЦИЯ: Основана на фрагментарных бронзовых табличках (Musée gallo-romain de Lyon). Многие интерпретации остаются спорными. Корреляция с современным календарем неопределенна.",
        "ja": "⚠️ 学術的再構築：断片的な青銅板（リヨン・ガロ・ロマン博物館）に基づく。多くの解釈が議論されている。現代暦との相関は不確実。",
        "zh": "⚠️ 学术重建：基于片段青铜板（里昂高卢罗马博物馆）。许多解释仍有争议。与现代日历的相关性不确定。",
        "ko": "⚠️ 학술적 재구성: 단편적인 청동판(리옹 갈로-로만 박물관) 기반. 많은 해석이 논쟁 중. 현대 달력과의 상관관계 불확실."
    },
    
    # Configuration options for this calendar
    "config_options": {
        "show_uncertainty": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show Uncertainty Markers",
                "de": "Unsicherheitsmarkierungen anzeigen",
                "es": "Mostrar marcadores de incertidumbre",
                "fr": "Afficher les marqueurs d'incertitude",
                "it": "Mostra marcatori di incertezza",
                "nl": "Toon onzekerheidsmarkeringen",
                "pl": "Pokaż znaczniki niepewności",
                "pt": "Mostrar marcadores de incerteza",
                "ru": "Показать маркеры неопределенности",
                "ja": "不確実性マーカーを表示",
                "zh": "显示不确定性标记",
                "ko": "불확실성 표시 보기"
            },
            "description": {
                "en": "Mark reconstructed or uncertain elements with [?]",
                "de": "Rekonstruierte oder unsichere Elemente mit [?] markieren",
                "es": "Marcar elementos reconstruidos o inciertos con [?]",
                "fr": "Marquer les éléments reconstruits ou incertains avec [?]"
            }
        },
        "correlation_method": {
            "type": "select",
            "options": {
                "olmsted": {
                    "en": "Olmsted (1992) - Samonios ≈ November",
                    "de": "Olmsted (1992) - Samonios ≈ November",
                    "es": "Olmsted (1992) - Samonios ≈ Noviembre",
                    "fr": "Olmsted (1992) - Samonios ≈ Novembre",
                    "it": "Olmsted (1992) - Samonios ≈ Novembre",
                    "nl": "Olmsted (1992) - Samonios ≈ November",
                    "pl": "Olmsted (1992) - Samonios ≈ Listopad",
                    "pt": "Olmsted (1992) - Samonios ≈ Novembro",
                    "ru": "Олмстед (1992) - Самониос ≈ Ноябрь",
                    "ja": "オルムステッド (1992) - サモニオス ≈ 11月",
                    "zh": "奥姆斯特德 (1992) - 萨莫尼奥斯 ≈ 11月",
                    "ko": "올름스테드 (1992) - 사모니오스 ≈ 11월"
                },
                "mckay": {
                    "en": "McKay (2016) - Samonios ≈ May/June",
                    "de": "McKay (2016) - Samonios ≈ Mai/Juni",
                    "es": "McKay (2016) - Samonios ≈ Mayo/Junio",
                    "fr": "McKay (2016) - Samonios ≈ Mai/Juin",
                    "it": "McKay (2016) - Samonios ≈ Maggio/Giugno",
                    "nl": "McKay (2016) - Samonios ≈ Mei/Juni",
                    "pl": "McKay (2016) - Samonios ≈ Maj/Czerwiec",
                    "pt": "McKay (2016) - Samonios ≈ Maio/Junho",
                    "ru": "МакКей (2016) - Самониос ≈ Май/Июнь",
                    "ja": "マッケイ (2016) - サモニオス ≈ 5月/6月",
                    "zh": "麦凯 (2016) - 萨莫尼奥斯 ≈ 5月/6月",
                    "ko": "맥케이 (2016) - 사모니오스 ≈ 5월/6월"
                }
            },
            "default": "olmsted",
            "label": {
                "en": "Scholar Interpretation",
                "de": "Gelehrten-Interpretation",
                "es": "Interpretación académica",
                "fr": "Interprétation savante",
                "it": "Interpretazione accademica",
                "nl": "Wetenschappelijke interpretatie",
                "pl": "Interpretacja naukowa",
                "pt": "Interpretação acadêmica",
                "ru": "Научная интерпретация",
                "ja": "学者の解釈",
                "zh": "学者解释",
                "ko": "학자 해석"
            }
        },
        "show_preserved_only": {
            "type": "boolean",
            "default": False,
            "label": {
                "en": "Show Only Preserved Text",
                "de": "Nur erhaltenen Text anzeigen",
                "es": "Mostrar solo texto preservado",
                "fr": "Afficher uniquement le texte préservé",
                "it": "Mostra solo testo preservato",
                "nl": "Toon alleen bewaarde tekst",
                "pl": "Pokaż tylko zachowany tekst",
                "pt": "Mostrar apenas texto preservado",
                "ru": "Показать только сохранившийся текст",
                "ja": "保存されたテキストのみ表示",
                "zh": "仅显示保存的文本",
                "ko": "보존된 텍스트만 표시"
            },
            "description": {
                "en": "Hide reconstructed elements, show only what's on the tablets",
                "de": "Rekonstruierte Elemente ausblenden, nur Tafeltexte zeigen",
                "es": "Ocultar elementos reconstruidos, mostrar solo lo que está en las tablillas",
                "fr": "Masquer les éléments reconstruits, afficher uniquement ce qui est sur les tablettes"
            }
        }
    },
    
    # Coligny calendar data - ONLY ARCHAEOLOGICALLY ATTESTED
    "coligny_data": {
        # Month names as preserved on tablets
        "months": [
            {"preserved": "SAMON", "reconstructed": "Samonios", "days": 30, "preserved_days": True},
            {"preserved": "DVMANN", "reconstructed": "Dumannios", "days": 29, "preserved_days": True},
            {"preserved": "RIVROS", "reconstructed": "Riuros", "days": 30, "preserved_days": True},
            {"preserved": "ANAGANTIO", "reconstructed": "Anagantios", "days": 29, "preserved_days": True},
            {"preserved": "OGRONIOS", "reconstructed": "Ogronios", "days": 30, "preserved_days": True},
            {"preserved": "CVTIOS", "reconstructed": "Cutios", "days": 30, "preserved_days": True},
            {"preserved": "GIAMONIOS", "reconstructed": "Giamonios", "days": 29, "preserved_days": False},
            {"preserved": "SIMIVIS", "reconstructed": "Simiuisonna", "days": 30, "preserved_days": False},
            {"preserved": "EQVOS", "reconstructed": "Equos", "days": 29, "preserved_days": True},
            {"preserved": "ELEMBIV", "reconstructed": "Elembiu", "days": 29, "preserved_days": False},
            {"preserved": "EDRINI", "reconstructed": "Edrinios", "days": 30, "preserved_days": True},
            {"preserved": "CANTLOS", "reconstructed": "Cantlos", "days": 29, "preserved_days": True}
        ],
        
        # Intercalary months (preserved on tablets)
        "intercalary": [
            {"preserved": "CIALLOS", "position": "uncertain", "days": 30},
            {"preserved": "QVIMON", "position": "uncertain", "days": 30}
        ],
        
        # Preserved notations (archaeologically attested)
        "preserved_notations": {
            "MAT": "Preserved notation (possibly 'good/complete')",
            "ANM": "Preserved notation (possibly 'not good/incomplete')",
            "ATENOUX": "Preserved notation (possibly 'returning night')",
            "DIVERTOMU": "Preserved notation (meaning unknown)",
            "IVOS": "Preserved notation (meaning unknown)",
            "PRINNI LOUD": "Preserved notation (meaning unknown)",
            "PRINNI LAG": "Preserved notation (meaning unknown)",
            "MD": "Preserved notation (meaning unknown)",
            "AMB": "Preserved notation (meaning unknown)"
        },
        
        # Correlation methods (scholarly interpretations)
        "correlations": {
            "olmsted": {
                "author": "Garrett Olmsted (1992)",
                "start_month": 10,  # November
                "start_day": 1,
                "note": "Based on Irish Samhain correlation"
            },
            "mckay": {
                "author": "Helen McKay (2016)",
                "start_month": 5,  # May
                "start_day": 15,
                "note": "Based on astronomical analysis"
            }
        },
        
        # What we know for certain
        "facts": {
            "location": "Coligny, Ain, France",
            "discovery": 1897,
            "date": "2nd century CE",
            "material": "Bronze",
            "fragments": 153,
            "preserved": "~40%",
            "museum": "Musée gallo-romain de Lyon",
            "language": "Gaulish",
            "script": "Latin letters"
        }
    }
}

# Update interval for this sensor
UPDATE_INTERVAL = CALENDAR_INFO["update_interval"]

class ColignyCalendarSensor(AlternativeTimeSensorBase):
    """Sensor for Coligny Celtic Calendar (Archaeological Reconstruction)."""
    
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
        self._show_uncertainty = True
        self._correlation_method = "olmsted"
        self._show_preserved_only = False
        
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
                self._show_uncertainty = options.get("show_uncertainty", self._show_uncertainty)
                self._correlation_method = options.get("correlation_method", self._correlation_method)
                self._show_preserved_only = options.get("show_preserved_only", self._show_preserved_only)
                
                _LOGGER.debug(f"Coligny sensor loaded options: uncertainty={self._show_uncertainty}, "
                            f"correlation={self._correlation_method}, preserved={self._show_preserved_only}")
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
            
            # Add disclaimer
            attrs["disclaimer"] = self._translate('disclaimer')
            
            # Add reference
            attrs["reference"] = CALENDAR_INFO.get('reference_url', '')
            
            # Add archaeological facts
            attrs["archaeological_facts"] = self._coligny_data["facts"]
            
            # Add configuration status
            attrs["config"] = {
                "show_uncertainty": self._show_uncertainty,
                "correlation_method": self._correlation_method,
                "show_preserved_only": self._show_preserved_only,
                "scholar": self._coligny_data["correlations"][self._correlation_method]["author"]
            }
        
        return attrs
    
    def _calculate_coligny_position(self, earth_date: datetime) -> tuple:
        """Calculate approximate position in Coligny calendar."""
        # Get correlation method
        correlation = self._coligny_data["correlations"][self._correlation_method]
        
        # Create reference date for current year
        ref_year = earth_date.year
        ref_date = datetime(ref_year, correlation["start_month"], correlation["start_day"])
        
        # Calculate days since reference
        days_diff = (earth_date.date() - ref_date.date()).days
        
        # Handle dates before reference
        if days_diff < 0:
            # Go to previous year
            ref_date = datetime(ref_year - 1, correlation["start_month"], correlation["start_day"])
            days_diff = (earth_date.date() - ref_date.date()).days
        
        # Simple calculation (approximation - actual calendar is complex)
        # Total days in regular year: 354 (12 lunar months)
        year_days = 354
        
        # Find month (simple approximation)
        month_index = 0
        days_counted = 0
        
        for idx, month in enumerate(self._coligny_data["months"]):
            if days_counted + month["days"] > days_diff:
                month_index = idx
                day_of_month = days_diff - days_counted + 1
                break
            days_counted += month["days"]
        else:
            # If we're past the end, we're in next year's first month
            month_index = 0
            day_of_month = days_diff - days_counted + 1
        
        # Ensure day is valid
        if day_of_month < 1:
            day_of_month = 1
        elif day_of_month > self._coligny_data["months"][month_index]["days"]:
            day_of_month = self._coligny_data["months"][month_index]["days"]
        
        return month_index, day_of_month
    
    def _format_coligny_date(self, earth_date: datetime) -> str:
        """Format the Coligny date with uncertainty markers."""
        # Reload options
        self._load_options()
        
        # Calculate position
        month_idx, day = self._calculate_coligny_position(earth_date)
        
        # Get month info
        month = self._coligny_data["months"][month_idx]
        
        # Choose name based on settings
        if self._show_preserved_only:
            month_name = month["preserved"]
        else:
            month_name = month["reconstructed"] if not self._show_uncertainty else f"{month['reconstructed']}[?]"
        
        # Format day with Roman numerals
        day_roman = self._roman_numeral(day)
        
        # Build result
        result = f"{month_name} {day_roman}"
        
        # Add preserved notation if exists (simplified)
        if day == 15:
            result += " ATENOUX"
        elif day % 2 == 0:
            result += " MAT" if not self._show_uncertainty else " MAT[?]"
        else:
            result += " ANM" if not self._show_uncertainty else " ANM[?]"
        
        # Add correlation note
        if self._show_uncertainty:
            result += f" [{self._correlation_method}]"
        
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
            month_idx, day = self._calculate_coligny_position(earth_date)
            
            # Get month info
            month = self._coligny_data["months"][month_idx]
            
            # Build attribute data
            self._coligny_calendar = {
                "formatted_date": coligny_date,
                "month": {
                    "preserved_name": month["preserved"],
                    "reconstructed_name": month["reconstructed"],
                    "index": month_idx + 1,
                    "days": month["days"],
                    "preservation_status": "Complete" if month["preserved_days"] else "Partial"
                },
                "day": {
                    "number": day,
                    "roman": self._roman_numeral(day)
                },
                "preserved_notations": list(self._coligny_data["preserved_notations"].keys()),
                "correlation": {
                    "method": self._correlation_method,
                    "scholar": self._coligny_data["correlations"][self._correlation_method]["author"],
                    "note": self._coligny_data["correlations"][self._correlation_method]["note"]
                },
                "gregorian": {
                    "year": earth_date.year,
                    "month": earth_date.month,
                    "day": earth_date.day
                },
                "preservation": {
                    "percentage": "~40%",
                    "fragments": 153,
                    "museum": "Musée gallo-romain de Lyon"
                }
            }
            
            # Add notation interpretation if applicable
            if day == 15:
                self._coligny_calendar["notation"] = {
                    "text": "ATENOUX",
                    "preserved": True,
                    "interpretation": "Possibly 'returning night' or full moon"
                }
            
            # Set state
            self._state = coligny_date
            
        except Exception as e:
            _LOGGER.error(f"Error calculating Coligny calendar: {e}")
            self._state = "Error"
            self._coligny_calendar = {"error": str(e)}
    
    def get_calendar_metadata(self) -> Dict[str, Any]:
        """Return calendar metadata."""
        return CALENDAR_INFO    
