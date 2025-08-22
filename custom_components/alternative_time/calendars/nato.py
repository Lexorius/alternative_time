"""NATO Time formats implementation - Version 2.5."""
from __future__ import annotations

from datetime import datetime
import logging
from typing import Dict, Any

from homeassistant.core import HomeAssistant
from ..sensor import AlternativeTimeSensorBase

_LOGGER = logging.getLogger(__name__)

try:
    import pytz
    HAS_PYTZ = True
except ImportError:
    HAS_PYTZ = False
    _LOGGER.warning("pytz not installed, NATO timezone detection will be limited")

# ============================================
# CALENDAR METADATA
# ============================================

# Update interval in seconds (1 second for real-time display)
UPDATE_INTERVAL = 1

# Complete calendar information for auto-discovery
CALENDAR_INFO = {
    "id": "nato",
    "version": "2.5.0",
    "icon": "mdi:clock-time-eight",
    "category": "military",
    "accuracy": "official",
    "update_interval": UPDATE_INTERVAL,
    
    # Multi-language names (English primary)
    "name": {
        "en": "NATO Time",
        "de": "NATO-Zeit",
        "es": "Hora OTAN",
        "fr": "Heure OTAN",
        "it": "Ora NATO",
        "nl": "NAVO Tijd",
        "pt": "Hora OTAN",
        "ru": "Время НАТО",
        "ja": "NATO時間",
        "zh": "北约时间",
        "ko": "NATO 시간"
    },
    
    # Short descriptions for UI (English primary)
    "description": {
        "en": "Military date-time group format (DTG) with various notations",
        "de": "Militärisches Datum-Zeit-Gruppe Format (DTG) mit verschiedenen Notationen",
        "es": "Formato de grupo fecha-hora militar (DTG) con varias notaciones",
        "fr": "Format de groupe date-heure militaire (DTG) avec diverses notations",
        "it": "Formato gruppo data-ora militare (DTG) con varie notazioni",
        "nl": "Militair datum-tijd groep formaat (DTG) met verschillende notaties",
        "pt": "Formato de grupo data-hora militar (DTG) com várias notações",
        "ru": "Военный формат даты-времени (DTG) с различными нотациями",
        "ja": "軍事日時グループ形式（DTG）各種表記",
        "zh": "军事日期时间组格式（DTG）多种记法",
        "ko": "군사 날짜-시간 그룹 형식 (DTG) 다양한 표기법"
    },
    
    # Detailed information for documentation
    "detailed_info": {
        "en": {
            "overview": "NATO Date-Time Group (DTG) is a standardized format for military communications",
            "basic": "Basic format: DDHHMM - day, hour, minute in 24-hour format",
            "zone": "Zone format: DDHHMM[Zone] MON YY - includes timezone letter and date",
            "rescue": "German rescue format: DD HHMM MONAT YY - used by emergency services",
            "zones": "Uses single letters A-Z (skipping J) for time zones, Z=UTC (Zulu)",
            "precision": "Critical for coordinating operations across time zones",
            "usage": "Standard in military, aviation, emergency services worldwide"
        },
        "de": {
            "overview": "NATO Datum-Zeit-Gruppe (DTG) ist ein standardisiertes Format für militärische Kommunikation",
            "basic": "Basisformat: TTHHMM - Tag, Stunde, Minute im 24-Stunden-Format",
            "zone": "Zonenformat: TTHHMM[Zone] MON JJ - enthält Zeitzonenzeichen und Datum",
            "rescue": "Deutsches Rettungsformat: TT HHMM MON JJ - verwendet von Rettungsdiensten",
            "zones": "Verwendet einzelne Buchstaben A-Z (ohne J) für Zeitzonen, Z=UTC (Zulu)",
            "precision": "Kritisch für die Koordination von Operationen über Zeitzonen hinweg",
            "usage": "Standard in Militär, Luftfahrt, Rettungsdiensten weltweit"
        }
    },
    
    # NATO-specific data
    "nato_data": {
        # NATO timezone letters
        "zones": {
            0: {"letter": "Z", "name": "Zulu", "offset": 0},
            1: {"letter": "A", "name": "Alpha", "offset": 1},
            2: {"letter": "B", "name": "Bravo", "offset": 2},
            3: {"letter": "C", "name": "Charlie", "offset": 3},
            4: {"letter": "D", "name": "Delta", "offset": 4},
            5: {"letter": "E", "name": "Echo", "offset": 5},
            6: {"letter": "F", "name": "Foxtrot", "offset": 6},
            7: {"letter": "G", "name": "Golf", "offset": 7},
            8: {"letter": "H", "name": "Hotel", "offset": 8},
            9: {"letter": "I", "name": "India", "offset": 9},
            10: {"letter": "K", "name": "Kilo", "offset": 10},
            11: {"letter": "L", "name": "Lima", "offset": 11},
            12: {"letter": "M", "name": "Mike", "offset": 12},
            -1: {"letter": "N", "name": "November", "offset": -1},
            -2: {"letter": "O", "name": "Oscar", "offset": -2},
            -3: {"letter": "P", "name": "Papa", "offset": -3},
            -4: {"letter": "Q", "name": "Quebec", "offset": -4},
            -5: {"letter": "R", "name": "Romeo", "offset": -5},
            -6: {"letter": "S", "name": "Sierra", "offset": -6},
            -7: {"letter": "T", "name": "Tango", "offset": -7},
            -8: {"letter": "U", "name": "Uniform", "offset": -8},
            -9: {"letter": "V", "name": "Victor", "offset": -9},
            -10: {"letter": "W", "name": "Whiskey", "offset": -10},
            -11: {"letter": "X", "name": "X-ray", "offset": -11},
            -12: {"letter": "Y", "name": "Yankee", "offset": -12}
        },
        
        # German month abbreviations for rescue service format
        "german_months": {
            1: "JAN", 2: "FEB", 3: "MÄR", 4: "APR",
            5: "MAI", 6: "JUN", 7: "JUL", 8: "AUG",
            9: "SEP", 10: "OKT", 11: "NOV", 12: "DEZ"
        },
        
        # Military phonetic alphabet (for reference)
        "phonetic": {
            "A": "Alpha", "B": "Bravo", "C": "Charlie", "D": "Delta",
            "E": "Echo", "F": "Foxtrot", "G": "Golf", "H": "Hotel",
            "I": "India", "J": "Juliet", "K": "Kilo", "L": "Lima",
            "M": "Mike", "N": "November", "O": "Oscar", "P": "Papa",
            "Q": "Quebec", "R": "Romeo", "S": "Sierra", "T": "Tango",
            "U": "Uniform", "V": "Victor", "W": "Whiskey", "X": "X-ray",
            "Y": "Yankee", "Z": "Zulu"
        }
    },
    
    # Additional metadata
    "reference_url": "https://en.wikipedia.org/wiki/Date-time_group",
    "documentation_url": "https://www.nato.int",
    "origin": "NATO military standard",
    "created_by": "NATO standardization",
    "official_since": "1950s",
    
    # Example format
    "example": "251430Z DEC 25 | 25 1430 DEZ 25",
    "example_meaning": "December 25, 14:30 UTC (Zulu time)",
    
    # Related calendars
    "related": ["gregorian", "unix", "iso8601"],
    
    # Tags for searching and filtering
    "tags": [
        "military", "nato", "dtg", "tactical", "emergency",
        "aviation", "zulu", "utc", "coordination", "official"
    ],
    
    # Special features
    "features": {
        "timezone_aware": True,
        "24_hour_format": True,
        "standardized": True,
        "precision": "minute",
        "real_time": True
    },
    
    # Configuration options for this calendar
    "config_options": {
        "format_type": {
            "type": "select",
            "default": "zone",
            "options": ["basic", "zone", "rescue", "aviation", "extended"],
            "label": {
                "en": "Format Type",
                "de": "Formattyp",
                "es": "Tipo de formato",
                "fr": "Type de format",
                "it": "Tipo di formato",
                "nl": "Formaat type",
                "pt": "Tipo de formato",
                "ru": "Тип формата",
                "ja": "フォーマットタイプ",
                "zh": "格式类型",
                "ko": "형식 유형"
            },
            "description": {
                "en": "Choose NATO time format variant (basic, with zone, rescue service, aviation, or extended)",
                "de": "NATO-Zeitformat-Variante wählen (Basis, mit Zone, Rettungsdienst, Luftfahrt oder erweitert)",
                "es": "Elegir variante de formato de hora OTAN (básico, con zona, servicio de rescate, aviación o extendido)",
                "fr": "Choisir la variante du format d'heure OTAN (basique, avec zone, service de secours, aviation ou étendu)"
            }
        },
        "show_zone_name": {
            "type": "boolean",
            "default": False,
            "label": {
                "en": "Show Phonetic Zone Name",
                "de": "Phonetischen Zonennamen anzeigen",
                "es": "Mostrar nombre fonético de zona",
                "fr": "Afficher le nom phonétique de la zone",
                "it": "Mostra nome fonetico della zona",
                "nl": "Toon fonetische zonenaam",
                "pt": "Mostrar nome fonético da zona",
                "ru": "Показывать фонетическое имя зоны",
                "ja": "音声ゾーン名を表示",
                "zh": "显示语音区域名称",
                "ko": "음성 구역 이름 표시"
            },
            "description": {
                "en": "Display phonetic name alongside zone letter (e.g., Z - Zulu)",
                "de": "Phonetischen Namen neben Zonenzeichen anzeigen (z.B. Z - Zulu)",
                "es": "Mostrar nombre fonético junto a la letra de zona (ej. Z - Zulu)",
                "fr": "Afficher le nom phonétique à côté de la lettre de zone (ex. Z - Zulu)"
            }
        },
        "use_local_zone": {
            "type": "boolean",
            "default": False,
            "label": {
                "en": "Use Local Timezone",
                "de": "Lokale Zeitzone verwenden",
                "es": "Usar zona horaria local",
                "fr": "Utiliser le fuseau horaire local",
                "it": "Usa fuso orario locale",
                "nl": "Gebruik lokale tijdzone",
                "pt": "Usar fuso horário local",
                "ru": "Использовать местный часовой пояс",
                "ja": "ローカルタイムゾーンを使用",
                "zh": "使用本地时区",
                "ko": "로컬 시간대 사용"
            },
            "description": {
                "en": "Use system timezone instead of UTC/Zulu (Z) time",
                "de": "Systemzeitzone statt UTC/Zulu (Z) Zeit verwenden",
                "es": "Usar zona horaria del sistema en lugar de hora UTC/Zulu (Z)",
                "fr": "Utiliser le fuseau horaire du système au lieu de l'heure UTC/Zulu (Z)"
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
                "pt": "Mostrar segundos",
                "ru": "Показывать секунды",
                "ja": "秒を表示",
                "zh": "显示秒",
                "ko": "초 표시"
            },
            "description": {
                "en": "Include seconds in the time display (DDHHMMSS)",
                "de": "Sekunden in der Zeitanzeige einbeziehen (TTHHMMSS)",
                "es": "Incluir segundos en la visualización de la hora (DDHHMMSS)",
                "fr": "Inclure les secondes dans l'affichage de l'heure (JJHHMMSS)"
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
                "pt": "Usar maiúsculas",
                "ru": "Использовать заглавные буквы",
                "ja": "大文字を使用",
                "zh": "使用大写",
                "ko": "대문자 사용"
            },
            "description": {
                "en": "Display month names and zone letters in uppercase",
                "de": "Monatsnamen und Zonenzeichen in Großbuchstaben anzeigen",
                "es": "Mostrar nombres de meses y letras de zona en mayúsculas",
                "fr": "Afficher les noms de mois et les lettres de zone en majuscules"
            }
        },
        "include_year": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Include Year",
                "de": "Jahr einbeziehen",
                "es": "Incluir año",
                "fr": "Inclure l'année",
                "it": "Includi anno",
                "nl": "Jaar opnemen",
                "pt": "Incluir ano",
                "ru": "Включать год",
                "ja": "年を含める",
                "zh": "包含年份",
                "ko": "연도 포함"
            },
            "description": {
                "en": "Include year in the date-time group (applies to zone and rescue formats)",
                "de": "Jahr in der Datum-Zeit-Gruppe einbeziehen (gilt für Zonen- und Rettungsformate)",
                "es": "Incluir año en el grupo fecha-hora (aplica a formatos de zona y rescate)",
                "fr": "Inclure l'année dans le groupe date-heure (s'applique aux formats zone et secours)"
            }
        }
    }
}


class NatoTimeSensor(AlternativeTimeSensorBase):
    """Sensor for displaying NATO Time in various formats."""
    
    # Class-level update interval
    UPDATE_INTERVAL = UPDATE_INTERVAL
    
    def __init__(self, base_name: str, hass: HomeAssistant) -> None:
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
        self._show_zone_name = False
        self._use_local_zone = False
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
                self._show_zone_name = options.get("show_zone_name", self._show_zone_name)
                self._use_local_zone = options.get("use_local_zone", self._use_local_zone)
                self._show_seconds = options.get("show_seconds", self._show_seconds)
                self._uppercase = options.get("uppercase", self._uppercase)
                self._include_year = options.get("include_year", self._include_year)
                
                _LOGGER.debug(f"NATO sensor loaded options: format={self._format_type}, "
                            f"zone_name={self._show_zone_name}, local={self._use_local_zone}, "
                            f"seconds={self._show_seconds}, uppercase={self._uppercase}, "
                            f"year={self._include_year}")
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
            
            # Add format description
            format_descriptions = {
                "basic": "Basic format: DDHHMM (day, hour, minute)",
                "zone": "Full DTG: DDHHMM[Zone] MON YY",
                "rescue": "German rescue: DD HHMM MON JJ",
                "aviation": "Aviation: DDHHMM[Zone] with full phonetic",
                "extended": "Extended: DDHHMMSS[Zone] MON YYYY"
            }
            attrs["format_description"] = format_descriptions.get(self._format_type, "Unknown format")
            
            # Add configuration status
            attrs["config"] = {
                "format_type": self._format_type,
                "show_zone_name": self._show_zone_name,
                "use_local_zone": self._use_local_zone,
                "show_seconds": self._show_seconds,
                "uppercase": self._uppercase,
                "include_year": self._include_year
            }
        
        return attrs
    
    def _get_timezone_info(self, earth_time: datetime) -> tuple:
        """Get NATO timezone letter and name."""
        zone_letter = 'Z'  # Default to Zulu time
        zone_name = 'Zulu'
        utc_offset = 0
        
        if self._use_local_zone and HAS_PYTZ:
            try:
                # Try to get system timezone from Home Assistant
                if hasattr(self._hass.config, 'time_zone'):
                    tz_name = self._hass.config.time_zone
                    local_tz = pytz.timezone(tz_name)
                    local_time = local_tz.localize(earth_time.replace(tzinfo=None))
                    utc_offset = int(local_time.utcoffset().total_seconds() / 3600)
                    
                    if utc_offset in self._nato_data["zones"]:
                        zone_info = self._nato_data["zones"][utc_offset]
                        zone_letter = zone_info["letter"]
                        zone_name = zone_info["name"]
            except Exception as e:
                _LOGGER.debug(f"Could not determine local timezone: {e}")
        
        return zone_letter, zone_name, utc_offset
    
    def _format_output(self, text: str) -> str:
        """Apply uppercase formatting if configured."""
        return text.upper() if self._uppercase else text
    
    def _calculate_nato_time(self, earth_time: datetime) -> Dict[str, Any]:
        """Calculate NATO Time based on selected format."""
        
        # Load options if not loaded yet
        self._load_options()
        
        # Calculate based on format type
        if self._format_type == "basic":
            return self._calculate_basic_format(earth_time)
        elif self._format_type == "zone":
            return self._calculate_zone_format(earth_time)
        elif self._format_type == "rescue":
            return self._calculate_rescue_format(earth_time)
        elif self._format_type == "aviation":
            return self._calculate_aviation_format(earth_time)
        elif self._format_type == "extended":
            return self._calculate_extended_format(earth_time)
        else:
            _LOGGER.warning(f"Unknown format type: {self._format_type}, using zone")
            return self._calculate_zone_format(earth_time)
    
    def _calculate_basic_format(self, earth_time: datetime) -> Dict[str, Any]:
        """Calculate basic NATO Time format (DDHHMM or DDHHMMSS)."""
        
        # Basic format
        if self._show_seconds:
            formatted = earth_time.strftime("%d%H%M%S")
        else:
            formatted = earth_time.strftime("%d%H%M")
        
        # Get timezone info for attributes
        zone_letter, zone_name, utc_offset = self._get_timezone_info(earth_time)
        
        # Add zone letter if using local zone
        if self._use_local_zone:
            formatted += zone_letter
        
        # Add zone name if configured
        display = formatted
        if self._show_zone_name:
            display = f"{formatted} ({zone_name})"
        
        result = {
            "day": earth_time.day,
            "hour": earth_time.hour,
            "minute": earth_time.minute,
            "second": earth_time.second,
            "zone_letter": zone_letter,
            "zone_name": zone_name,
            "utc_offset": utc_offset,
            "formatted": formatted,
            "standard_time": earth_time.strftime("%Y-%m-%d %H:%M:%S"),
            "full_display": display
        }
        
        return result
    
    def _calculate_zone_format(self, earth_time: datetime) -> Dict[str, Any]:
        """Calculate NATO Time with Zone format (DDHHMM[Zone] MON YY)."""
        
        # Get timezone info
        zone_letter, zone_name, utc_offset = self._get_timezone_info(earth_time)
        
        # Build format string
        if self._show_seconds:
            time_part = earth_time.strftime("%d%H%M%S")
        else:
            time_part = earth_time.strftime("%d%H%M")
        
        month = earth_time.strftime("%b")
        
        if self._include_year:
            year = earth_time.strftime("%y")
            formatted = f"{time_part}{zone_letter} {month} {year}"
        else:
            formatted = f"{time_part}{zone_letter} {month}"
        
        formatted = self._format_output(formatted)
        
        # Add zone name if configured
        display = formatted
        if self._show_zone_name:
            display = f"{formatted} ({zone_name})"
        
        result = {
            "day": earth_time.day,
            "hour": earth_time.hour,
            "minute": earth_time.minute,
            "second": earth_time.second,
            "zone_letter": zone_letter,
            "zone_name": zone_name,
            "utc_offset": utc_offset,
            "month": self._format_output(month),
            "year": earth_time.year % 100 if self._include_year else None,
            "formatted": formatted,
            "standard_time": earth_time.strftime("%Y-%m-%d %H:%M:%S"),
            "full_display": display
        }
        
        return result
    
    def _calculate_rescue_format(self, earth_time: datetime) -> Dict[str, Any]:
        """Calculate German rescue service format (DD HHMM MONAT YY)."""
        
        # Get German month abbreviation
        month = self._nato_data["german_months"][earth_time.month]
        
        # Format with space between day and time
        if self._show_seconds:
            time_part = f"{earth_time.hour:02d}{earth_time.minute:02d}{earth_time.second:02d}"
        else:
            time_part = f"{earth_time.hour:02d}{earth_time.minute:02d}"
        
        if self._include_year:
            formatted = f"{earth_time.day:02d} {time_part} {month} {earth_time.year % 100:02d}"
        else:
            formatted = f"{earth_time.day:02d} {time_part} {month}"
        
        formatted = self._format_output(formatted)
        
        # Get timezone info for attributes
        zone_letter, zone_name, utc_offset = self._get_timezone_info(earth_time)
        
        # Add zone name if configured
        display = formatted
        if self._show_zone_name:
            display = f"{formatted} ({zone_name})"
        
        result = {
            "day": earth_time.day,
            "hour": earth_time.hour,
            "minute": earth_time.minute,
            "second": earth_time.second,
            "zone_letter": zone_letter,
            "zone_name": zone_name,
            "utc_offset": utc_offset,
            "month_german": month,
            "year": earth_time.year % 100 if self._include_year else None,
            "formatted": formatted,
            "organizations": "Feuerwehr, Rettungsdienst, THW, Katastrophenschutz",
            "standard_time": earth_time.strftime("%Y-%m-%d %H:%M:%S"),
            "full_display": display
        }
        
        return result
    
    def _calculate_aviation_format(self, earth_time: datetime) -> Dict[str, Any]:
        """Calculate aviation format with full phonetic zone name."""
        
        # Get timezone info
        zone_letter, zone_name, utc_offset = self._get_timezone_info(earth_time)
        
        # Build format string
        if self._show_seconds:
            time_part = earth_time.strftime("%d%H%M%S")
        else:
            time_part = earth_time.strftime("%d%H%M")
        
        # Aviation format always includes full phonetic name
        formatted = f"{time_part} {zone_name}"
        
        if self._include_year:
            month = earth_time.strftime("%b")
            year = earth_time.strftime("%Y")
            formatted += f" {month} {year}"
        
        formatted = self._format_output(formatted)
        
        result = {
            "day": earth_time.day,
            "hour": earth_time.hour,
            "minute": earth_time.minute,
            "second": earth_time.second,
            "zone_letter": zone_letter,
            "zone_name": zone_name,
            "utc_offset": utc_offset,
            "formatted": formatted,
            "standard_time": earth_time.strftime("%Y-%m-%d %H:%M:%S"),
            "full_display": formatted,
            "aviation_use": "NOTAM, Flight Plans, ATC Communications"
        }
        
        return result
    
    def _calculate_extended_format(self, earth_time: datetime) -> Dict[str, Any]:
        """Calculate extended format with full year (DDHHMMSS[Zone] MON YYYY)."""
        
        # Get timezone info
        zone_letter, zone_name, utc_offset = self._get_timezone_info(earth_time)
        
        # Extended format always includes seconds
        time_part = earth_time.strftime("%d%H%M%S")
        month = earth_time.strftime("%b")
        year = earth_time.strftime("%Y")
        
        formatted = f"{time_part}{zone_letter} {month} {year}"
        formatted = self._format_output(formatted)
        
        # Add zone name if configured
        display = formatted
        if self._show_zone_name:
            display = f"{formatted} ({zone_name})"
        
        result = {
            "day": earth_time.day,
            "hour": earth_time.hour,
            "minute": earth_time.minute,
            "second": earth_time.second,
            "zone_letter": zone_letter,
            "zone_name": zone_name,
            "utc_offset": utc_offset,
            "month": self._format_output(month),
            "year": earth_time.year,
            "formatted": formatted,
            "standard_time": earth_time.strftime("%Y-%m-%d %H:%M:%S"),
            "full_display": display,
            "precision": "second"
        }
        
        return result
    
    def update(self) -> None:
        """Update the sensor."""
        now = datetime.now()
        self._nato_time = self._calculate_nato_time(now)
        
        # Set state to formatted NATO time
        self._state = self._nato_time["full_display"]
        
        _LOGGER.debug(f"Updated NATO Time to {self._state}")