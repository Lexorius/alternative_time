"""NATO Time Format Calendar Plugin for Alternative Time Systems.

Provides military-standard Date-Time Group (DTG) formatting with multiple output formats.
"""

from datetime import datetime
from typing import Dict, Any, Optional
import logging
import pytz

from ..sensor import AlternativeTimeSensorBase

_LOGGER = logging.getLogger(__name__)

# Calendar metadata and configuration
CALENDAR_INFO = {
    "id": "nato",
    "version": "2.5.0",
    "name": {
        "en": "NATO Time",
        "de": "NATO-Zeit",
        "es": "Hora OTAN",
        "fr": "Heure OTAN",
        "it": "Ora NATO",
        "nl": "NAVO-tijd",
        "pl": "Czas NATO",
        "pt": "Hora OTAN",
        "ru": "Время НАТО",
        "ja": "NATO時間",
        "zh": "北约时间",
        "ko": "NATO 시간"
    },
    "description": {
        "en": "Military Date-Time Group (DTG) format used by NATO forces for precise time coordination",
        "de": "Militärisches Datum-Zeit-Gruppen (DTG) Format der NATO-Streitkräfte für präzise Zeitkoordination",
        "es": "Formato de Grupo de Fecha-Hora (DTG) militar usado por las fuerzas de la OTAN",
        "fr": "Format de Groupe Date-Heure (DTG) militaire utilisé par les forces de l'OTAN",
        "it": "Formato militare Date-Time Group (DTG) usato dalle forze NATO",
        "nl": "Militair Datum-Tijd-Groep (DTG) formaat gebruikt door NAVO-strijdkrachten",
        "pl": "Wojskowy format grupy daty i czasu (DTG) używany przez siły NATO",
        "pt": "Formato militar de Grupo Data-Hora (DTG) usado pelas forças da OTAN",
        "ru": "Военный формат группы даты-времени (DTG), используемый силами НАТО",
        "ja": "NATO軍が使用する軍事日時グループ（DTG）フォーマット",
        "zh": "北约部队使用的军事日期时间组（DTG）格式",
        "ko": "NATO군이 사용하는 군사 날짜-시간 그룹(DTG) 형식"
    },
    "category": "military",
    "update_interval": 60,
    "accuracy": "minute",
    "icon": "mdi:clock-time-eight",
    "reference_url": "https://en.wikipedia.org/wiki/Date-time_group",
    
    # Configuration options for this calendar
    "config_options": {
        "format_type": {
            "type": "select",
            "options": {
                "basic": {
                    "en": "Basic (DDHHMM)",
                    "de": "Basis (TTSSMMM)",
                    "es": "Básico (DDHHMM)",
                    "fr": "Basique (JJHHMM)",
                    "it": "Base (GGHHMM)",
                    "nl": "Basis (DDUUMM)",
                    "pl": "Podstawowy (DDGGMM)",
                    "pt": "Básico (DDHHMM)",
                    "ru": "Базовый (ДДЧЧММ)",
                    "ja": "基本 (DDHHMM)",
                    "zh": "基本 (DDHHMM)",
                    "ko": "기본 (DDHHMM)"
                },
                "zone": {
                    "en": "Zone DTG (DDHHMM[Z] MON YY)",
                    "de": "Zonen-DTG (TTSSMMZ MON JJ)",
                    "es": "DTG con Zona (DDHHMMZ MES AA)",
                    "fr": "DTG avec Zone (JJHHMMZ MOIS AA)",
                    "it": "DTG con Zona (GGHHMMZ MESE AA)",
                    "nl": "Zone DTG (DDUUMMZ MAAND JJ)",
                    "pl": "DTG ze strefą (DDGGMMZ MIESIĄC RR)",
                    "pt": "DTG com Zona (DDHHMMZ MÊS AA)",
                    "ru": "DTG с зоной (ДДЧЧММZ МЕСЯЦ ГГ)",
                    "ja": "ゾーンDTG (DDHHMMZ 月 YY)",
                    "zh": "区域DTG (DDHHMMZ 月 YY)",
                    "ko": "구역 DTG (DDHHMMZ 월 YY)"
                },
                "rescue": {
                    "en": "Rescue Format (DD HHMM MON YY)",
                    "de": "Rettungsformat (TT SSMM MON JJ)",
                    "es": "Formato Rescate (DD HHMM MES AA)",
                    "fr": "Format Sauvetage (JJ HHMM MOIS AA)",
                    "it": "Formato Soccorso (GG HHMM MESE AA)",
                    "nl": "Reddingsformaat (DD UUMM MAAND JJ)",
                    "pl": "Format ratunkowy (DD GGMM MIESIĄC RR)",
                    "pt": "Formato Resgate (DD HHMM MÊS AA)",
                    "ru": "Формат спасения (ДД ЧЧММ МЕСЯЦ ГГ)",
                    "ja": "救助フォーマット (DD HHMM 月 YY)",
                    "zh": "救援格式 (DD HHMM 月 YY)",
                    "ko": "구조 형식 (DD HHMM 월 YY)"
                },
                "aviation": {
                    "en": "Aviation (DDHHMM + Phonetic)",
                    "de": "Luftfahrt (TTSSMM + Phonetisch)",
                    "es": "Aviación (DDHHMM + Fonético)",
                    "fr": "Aviation (JJHHMM + Phonétique)",
                    "it": "Aviazione (GGHHMM + Fonetico)",
                    "nl": "Luchtvaart (DDUUMM + Fonetisch)",
                    "pl": "Lotnictwo (DDGGMM + Fonetyczny)",
                    "pt": "Aviação (DDHHMM + Fonético)",
                    "ru": "Авиация (ДДЧЧММ + Фонетический)",
                    "ja": "航空 (DDHHMM + フォネティック)",
                    "zh": "航空 (DDHHMM + 语音)",
                    "ko": "항공 (DDHHMM + 음성)"
                },
                "extended": {
                    "en": "Extended (DDHHMMSS[Z] MON YYYY)",
                    "de": "Erweitert (TTSSMMSSZ MON JJJJ)",
                    "es": "Extendido (DDHHMMSSZ MES AAAA)",
                    "fr": "Étendu (JJHHMMSSZ MOIS AAAA)",
                    "it": "Esteso (GGHHMMSSZ MESE AAAA)",
                    "nl": "Uitgebreid (DDUUMMSSZ MAAND JJJJ)",
                    "pl": "Rozszerzony (DDGGMMSSZ MIESIĄC RRRR)",
                    "pt": "Estendido (DDHHMMSSZ MÊS AAAA)",
                    "ru": "Расширенный (ДДЧЧММССZ МЕСЯЦ ГГГГ)",
                    "ja": "拡張 (DDHHMMSSZ 月 YYYY)",
                    "zh": "扩展 (DDHHMMSSZ 月 YYYY)",
                    "ko": "확장 (DDHHMMSSZ 월 YYYY)"
                }
            },
            "default": "zone",
            "label": {
                "en": "Format Type",
                "de": "Formattyp",
                "es": "Tipo de formato",
                "fr": "Type de format",
                "it": "Tipo di formato",
                "nl": "Formaattype",
                "pl": "Typ formatu",
                "pt": "Tipo de formato",
                "ru": "Тип формата",
                "ja": "フォーマットタイプ",
                "zh": "格式类型",
                "ko": "형식 유형"
            },
            "description": {
                "en": "Choose the NATO time format style",
                "de": "Wählen Sie den NATO-Zeitformatstil",
                "es": "Elija el estilo de formato de hora OTAN",
                "fr": "Choisissez le style de format d'heure OTAN",
                "it": "Scegli lo stile del formato ora NATO",
                "nl": "Kies de NAVO-tijdformaatstijl",
                "pl": "Wybierz styl formatu czasu NATO",
                "pt": "Escolha o estilo de formato de hora OTAN",
                "ru": "Выберите стиль формата времени НАТО",
                "ja": "NATO時間フォーマットスタイルを選択",
                "zh": "选择北约时间格式样式",
                "ko": "NATO 시간 형식 스타일 선택"
            }
        },
        "timezone": {
            "type": "select",
            "options": ["UTC", "Local", "Alpha", "Bravo", "Charlie", "Delta", "Echo", "Foxtrot", "Golf", "Hotel", "India", "Kilo", "Lima", "Mike"],
            "default": "UTC",
            "label": {
                "en": "Time Zone",
                "de": "Zeitzone",
                "es": "Zona horaria",
                "fr": "Fuseau horaire",
                "it": "Fuso orario",
                "nl": "Tijdzone",
                "pl": "Strefa czasowa",
                "pt": "Fuso horário",
                "ru": "Часовой пояс",
                "ja": "タイムゾーン",
                "zh": "时区",
                "ko": "시간대"
            },
            "description": {
                "en": "Select time zone (UTC/Zulu, Local, or NATO zone)",
                "de": "Zeitzone wählen (UTC/Zulu, Lokal oder NATO-Zone)",
                "es": "Seleccionar zona horaria (UTC/Zulu, Local o zona OTAN)",
                "fr": "Sélectionner le fuseau horaire (UTC/Zulu, Local ou zone OTAN)",
                "it": "Seleziona fuso orario (UTC/Zulu, Locale o zona NATO)",
                "nl": "Selecteer tijdzone (UTC/Zulu, Lokaal of NAVO-zone)",
                "pl": "Wybierz strefę czasową (UTC/Zulu, Lokalna lub strefa NATO)",
                "pt": "Selecionar fuso horário (UTC/Zulu, Local ou zona OTAN)",
                "ru": "Выберите часовой пояс (UTC/Zulu, местный или зона НАТО)",
                "ja": "タイムゾーンを選択（UTC/Zulu、ローカル、またはNATOゾーン）",
                "zh": "选择时区（UTC/Zulu、本地或北约区）",
                "ko": "시간대 선택 (UTC/Zulu, 로컬 또는 NATO 구역)"
            }
        },
        "show_seconds": {
            "type": "boolean",
            "default": False,
            "label": {
                "en": "Show Seconds",
                "de": "Sekunden anzeigen",
                "es": "Mostrar segundos",
                "fr": "Afficher les secondes",
                "it": "Mostra secondi",
                "nl": "Toon seconden",
                "pl": "Pokaż sekundy",
                "pt": "Mostrar segundos",
                "ru": "Показать секунды",
                "ja": "秒を表示",
                "zh": "显示秒",
                "ko": "초 표시"
            },
            "description": {
                "en": "Include seconds in extended and aviation formats",
                "de": "Sekunden in erweiterten und Luftfahrt-Formaten einschließen",
                "es": "Incluir segundos en formatos extendido y aviación",
                "fr": "Inclure les secondes dans les formats étendu et aviation",
                "it": "Includi secondi nei formati esteso e aviazione",
                "nl": "Seconden opnemen in uitgebreide en luchtvaartformaten",
                "pl": "Uwzględnij sekundy w formatach rozszerzonym i lotniczym",
                "pt": "Incluir segundos nos formatos estendido e aviação",
                "ru": "Включить секунды в расширенном и авиационном форматах",
                "ja": "拡張および航空フォーマットに秒を含める",
                "zh": "在扩展和航空格式中包括秒",
                "ko": "확장 및 항공 형식에 초 포함"
            }
        },
        "uppercase": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Use Uppercase",
                "de": "Großbuchstaben verwenden",
                "es": "Usar mayúsculas",
                "fr": "Utiliser les majuscules",
                "it": "Usa maiuscole",
                "nl": "Gebruik hoofdletters",
                "pl": "Użyj wielkich liter",
                "pt": "Usar maiúsculas",
                "ru": "Использовать заглавные буквы",
                "ja": "大文字を使用",
                "zh": "使用大写",
                "ko": "대문자 사용"
            }
        },
        "include_year": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Include Year",
                "de": "Jahr einschließen",
                "es": "Incluir año",
                "fr": "Inclure l'année",
                "it": "Includi anno",
                "nl": "Jaar opnemen",
                "pl": "Uwzględnij rok",
                "pt": "Incluir ano",
                "ru": "Включить год",
                "ja": "年を含める",
                "zh": "包括年份",
                "ko": "연도 포함"
            }
        }
    },
    
    # NATO timezone data
    "nato_data": {
        "zones": {
            -12: ("Y", "Yankee"),
            -11: ("X", "X-ray"),
            -10: ("W", "Whiskey"),
            -9: ("V", "Victor"),
            -8: ("U", "Uniform"),
            -7: ("T", "Tango"),
            -6: ("S", "Sierra"),
            -5: ("R", "Romeo"),
            -4: ("Q", "Quebec"),
            -3: ("P", "Papa"),
            -2: ("O", "Oscar"),
            -1: ("N", "November"),
            0: ("Z", "Zulu"),
            1: ("A", "Alpha"),
            2: ("B", "Bravo"),
            3: ("C", "Charlie"),
            4: ("D", "Delta"),
            5: ("E", "Echo"),
            6: ("F", "Foxtrot"),
            7: ("G", "Golf"),
            8: ("H", "Hotel"),
            9: ("I", "India"),
            10: ("K", "Kilo"),
            11: ("L", "Lima"),
            12: ("M", "Mike")
        },
        "months": {
            "en": ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"],
            "de": ["JAN", "FEB", "MÄR", "APR", "MAI", "JUN", "JUL", "AUG", "SEP", "OKT", "NOV", "DEZ"]
        }
    }
}

# Update interval for this sensor
UPDATE_INTERVAL = CALENDAR_INFO["update_interval"]

class NATOTimeSensor(AlternativeTimeSensorBase):
    """Sensor for NATO Date-Time Group format."""
    
    # Class-level update interval
    UPDATE_INTERVAL = UPDATE_INTERVAL
    
    def __init__(self, base_name: str, hass) -> None:
        """Initialize the NATO time sensor."""
        super().__init__(base_name, hass)
        
        # Get translated name from metadata
        calendar_name = self._translate('name', 'NATO Time')
        
        # Set sensor attributes
        self._attr_name = f"{base_name} {calendar_name}"
        self._attr_unique_id = f"{base_name}_nato_time"
        self._attr_icon = CALENDAR_INFO.get("icon", "mdi:clock-time-eight")
        
        # Default configuration options
        self._format_type = "zone"
        self._timezone = "UTC"
        self._show_seconds = False
        self._uppercase = True
        self._include_year = True
        
        # NATO data
        self._nato_data = CALENDAR_INFO["nato_data"]
        
        # Track if options have been loaded
        self._options_loaded = False
        
        _LOGGER.debug(f"Initialized NATO Time sensor: {self._attr_name}")
    
    def _load_options(self) -> None:
        """Load configuration options from config entry."""
        if self._options_loaded:
            return
            
        try:
            options = self.get_plugin_options()
            if options:
                # Update configuration from plugin options
                self._format_type = options.get("format_type", self._format_type)
                self._timezone = options.get("timezone", self._timezone)
                self._show_seconds = options.get("show_seconds", self._show_seconds)
                self._uppercase = options.get("uppercase", self._uppercase)
                self._include_year = options.get("include_year", self._include_year)
                
                _LOGGER.debug(f"NATO sensor loaded options: format={self._format_type}, "
                            f"timezone={self._timezone}, seconds={self._show_seconds}, "
                            f"uppercase={self._uppercase}, year={self._include_year}")
            else:
                _LOGGER.debug("NATO sensor using default options - no custom options found")
                
            self._options_loaded = True
        except Exception as e:
            _LOGGER.debug(f"NATO sensor could not load options yet: {e}")
    
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
        
        # Add NATO-specific attributes
        if hasattr(self, '_nato_time'):
            attrs.update(self._nato_time)
            
            # Add description in user's language
            attrs["description"] = self._translate('description')
            
            # Add reference
            attrs["reference"] = CALENDAR_INFO.get('reference_url', '')
            
            # Add format description based on language and type
            format_key = self._format_type
            format_options = CALENDAR_INFO["config_options"]["format_type"]["options"]
            if isinstance(format_options[format_key], dict):
                attrs["format_description"] = format_options[format_key].get(
                    self._user_language, 
                    format_options[format_key].get("en", format_key)
                )
            else:
                attrs["format_description"] = format_key
            
            # Add configuration status
            attrs["config"] = {
                "format_type": self._format_type,
                "timezone": self._timezone,
                "show_seconds": self._show_seconds,
                "uppercase": self._uppercase,
                "include_year": self._include_year
            }
        
        return attrs
    
    def _get_timezone_info(self, earth_time: datetime) -> tuple:
        """Get NATO timezone letter and name based on configuration."""
        if self._timezone == "Local":
            # Use actual local timezone offset
            offset_seconds = earth_time.utcoffset().total_seconds() if earth_time.utcoffset() else 0
            offset_hours = int(offset_seconds / 3600)
        elif self._timezone == "UTC":
            # Use UTC (Zulu time)
            offset_hours = 0
        else:
            # Use specific NATO zone
            nato_zone_map = {
                "Alpha": 1, "Bravo": 2, "Charlie": 3, "Delta": 4,
                "Echo": 5, "Foxtrot": 6, "Golf": 7, "Hotel": 8,
                "India": 9, "Kilo": 10, "Lima": 11, "Mike": 12
            }
            offset_hours = nato_zone_map.get(self._timezone, 0)
        
        # Get zone info from data
        zone_info = self._nato_data["zones"].get(offset_hours, ("Z", "Zulu"))
        return zone_info
    
    def _get_time_for_zone(self, earth_time: datetime) -> datetime:
        """Get the time adjusted for the selected timezone."""
        if self._timezone == "Local":
            return earth_time
        elif self._timezone == "UTC":
            return earth_time.astimezone(pytz.UTC)
        else:
            # Get offset for NATO zone
            nato_zone_map = {
                "Alpha": 1, "Bravo": 2, "Charlie": 3, "Delta": 4,
                "Echo": 5, "Foxtrot": 6, "Golf": 7, "Hotel": 8,
                "India": 9, "Kilo": 10, "Lima": 11, "Mike": 12
            }
            offset_hours = nato_zone_map.get(self._timezone, 0)
            
            # Create timezone with fixed offset
            tz = pytz.FixedOffset(offset_hours * 60)
            return earth_time.astimezone(tz)
    
    def _format_nato_time(self, earth_time: datetime) -> str:
        """Format time according to selected NATO format."""
        # Reload options on each update to catch changes
        self._load_options()
        
        # Get time in selected zone
        zone_time = self._get_time_for_zone(earth_time)
        
        # Get timezone info
        zone_letter, zone_name = self._get_timezone_info(zone_time)
        
        # Get month abbreviation
        lang = self._user_language if self._user_language in ["en", "de"] else "en"
        month = self._nato_data["months"][lang][zone_time.month - 1]
        
        # Format based on type
        if self._format_type == "basic":
            # Basic format: DDHHMM
            result = zone_time.strftime("%d%H%M")
            
        elif self._format_type == "zone":
            # Full DTG: DDHHMM[Zone] MON YY
            base = zone_time.strftime(f"%d%H%M{zone_letter}")
            if self._include_year:
                result = f"{base} {month} {zone_time.strftime('%y')}"
            else:
                result = f"{base} {month}"
                
        elif self._format_type == "rescue":
            # German rescue format: DD HHMM MON JJ
            base = zone_time.strftime("%d %H%M")
            if self._include_year:
                result = f"{base} {month} {zone_time.strftime('%y')}"
            else:
                result = f"{base} {month}"
                
        elif self._format_type == "aviation":
            # Aviation format with phonetic zone name
            if self._show_seconds:
                base = zone_time.strftime(f"%d%H%M%S")
            else:
                base = zone_time.strftime(f"%d%H%M")
            
            # Always show phonetic name for aviation
            result = f"{base} {zone_name}"
                
            if self._include_year:
                result = f"{result} {month} {zone_time.strftime('%y')}"
            else:
                result = f"{result} {month}"
                
        elif self._format_type == "extended":
            # Extended format: DDHHMMSS[Zone] MON YYYY
            if self._show_seconds:
                base = zone_time.strftime(f"%d%H%M%S{zone_letter}")
            else:
                base = zone_time.strftime(f"%d%H%M{zone_letter}")
                
            if self._include_year:
                result = f"{base} {month} {zone_time.strftime('%Y')}"
            else:
                result = f"{base} {month}"
        else:
            # Default to zone format
            result = zone_time.strftime(f"%d%H%M{zone_letter} {month} %y")
        
        # Apply uppercase if configured
        if self._uppercase:
            result = result.upper()
        else:
            result = result.lower()
        
        return result
    
    def _calculate_time(self, earth_time: datetime) -> None:
        """Calculate NATO Date-Time Group."""
        try:
            # Format the main time string
            nato_format = self._format_nato_time(earth_time)
            
            # Get zone info for attributes
            zone_time = self._get_time_for_zone(earth_time)
            zone_letter, zone_name = self._get_timezone_info(zone_time)
            
            # Build attribute data
            self._nato_time = {
                "format": nato_format,
                "zone_letter": zone_letter,
                "zone_name": zone_name,
                "format_type": self._format_type,
                "timezone_setting": self._timezone,
                "day": zone_time.day,
                "hour": zone_time.hour,
                "minute": zone_time.minute,
                "second": zone_time.second if self._show_seconds else None,
                "month": zone_time.strftime("%B"),
                "year": zone_time.year
            }
            
            # Set state
            self._state = nato_format
            
        except Exception as e:
            _LOGGER.error(f"Error calculating NATO time: {e}")
            self._state = "Error"
            self._nato_time = {"error": str(e)}
    
    def get_calendar_metadata(self) -> Dict[str, Any]:
        """Return calendar metadata."""
        return CALENDAR_INFO
