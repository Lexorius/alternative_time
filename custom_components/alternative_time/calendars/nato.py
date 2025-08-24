"""NATO Date Time Group calendar formats for Alternative Time integration."""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import pytz

_LOGGER = logging.getLogger(__name__)

# NATO Calendar Information
CALENDAR_INFO = {
    "id": "nato",
    "name": {
        "en": "NATO Date Time Group",
        "de": "NATO Datum-Zeit-Gruppe",
        "es": "Grupo Fecha-Hora OTAN",
        "fr": "Groupe Date-Heure OTAN",
        "it": "Gruppo Data-Ora NATO",
        "nl": "NAVO Datum-Tijd Groep",
        "pl": "Grupa Data-Czas NATO",
        "pt": "Grupo Data-Hora OTAN",
        "ru": "Группа дата-время НАТО",
        "ja": "NATO日時グループ",
        "zh": "北约日期时间组",
        "ko": "NATO 날짜 시간 그룹"
    },
    "description": {
        "en": "Military date-time format (DTG) used by NATO forces",
        "de": "Militärisches Datums-Zeit-Format (DTG) der NATO-Streitkräfte",
        "es": "Formato militar de fecha-hora (DTG) usado por fuerzas de la OTAN",
        "fr": "Format militaire date-heure (DTG) utilisé par les forces de l'OTAN",
        "it": "Formato militare data-ora (DTG) usato dalle forze NATO",
        "nl": "Militair datum-tijd formaat (DTG) gebruikt door NAVO-troepen",
        "pl": "Wojskowy format daty i czasu (DTG) używany przez siły NATO",
        "pt": "Formato militar de data-hora (DTG) usado pelas forças da OTAN",
        "ru": "Военный формат даты-времени (DTG), используемый силами НАТО",
        "ja": "NATO軍が使用する軍事日時形式（DTG）",
        "zh": "北约部队使用的军事日期时间格式（DTG）",
        "ko": "NATO군이 사용하는 군사 날짜-시간 형식(DTG)"
    },
    "icon": "mdi:shield-star",
    "category": "military",
    "update_interval": 1,
    "accuracy": "1 second",
    "version": "2.5.0",
    
    # Configuration options
    "config_options": {
        "nato_format": {
            "type": "select",
            "default": "basic",
            "options": ["basic", "zone", "rescue"],
            "label": {
                "en": "NATO Format",
                "de": "NATO-Format",
                "es": "Formato OTAN",
                "fr": "Format OTAN",
                "it": "Formato NATO",
                "nl": "NAVO-formaat",
                "pl": "Format NATO",
                "pt": "Formato OTAN",
                "ru": "Формат НАТО",
                "ja": "NATO形式",
                "zh": "北约格式",
                "ko": "NATO 형식"
            },
            "description": {
                "en": "Select NATO DTG format style",
                "de": "NATO DTG-Formatstil auswählen",
                "es": "Seleccionar estilo de formato DTG de la OTAN",
                "fr": "Sélectionner le style de format DTG de l'OTAN",
                "it": "Seleziona lo stile del formato DTG NATO",
                "nl": "Selecteer NAVO DTG-formaatstijl",
                "pl": "Wybierz styl formatu DTG NATO",
                "pt": "Selecionar estilo de formato DTG da OTAN",
                "ru": "Выберите стиль формата DTG НАТО",
                "ja": "NATO DTGフォーマットスタイルを選択",
                "zh": "选择北约DTG格式样式",
                "ko": "NATO DTG 형식 스타일 선택"
            }
        },
        "timezone_for_zone": {
            "type": "select",
            "default": "UTC",
            "options": [
                "UTC", "Alpha", "Bravo", "Charlie", "Delta", "Echo", "Foxtrot",
                "Golf", "Hotel", "India", "Juliet", "Kilo", "Lima", "Mike",
                "November", "Oscar", "Papa", "Quebec", "Romeo", "Sierra", "Tango",
                "Uniform", "Victor", "Whiskey", "X-ray", "Yankee", "Zulu"
            ],
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
                "en": "Select NATO time zone letter",
                "de": "NATO-Zeitzonenbuchstabe auswählen",
                "es": "Seleccionar letra de zona horaria OTAN",
                "fr": "Sélectionner la lettre de fuseau horaire OTAN",
                "it": "Seleziona la lettera del fuso orario NATO",
                "nl": "Selecteer NAVO tijdzone letter",
                "pl": "Wybierz literę strefy czasowej NATO",
                "pt": "Selecionar letra de fuso horário da OTAN",
                "ru": "Выберите букву часового пояса НАТО",
                "ja": "NATOタイムゾーン文字を選択",
                "zh": "选择北约时区字母",
                "ko": "NATO 시간대 문자 선택"
            }
        },
        "show_zone_letter": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show Zone Letter",
                "de": "Zonenbuchstabe anzeigen",
                "es": "Mostrar Letra de Zona",
                "fr": "Afficher la Lettre de Zone",
                "it": "Mostra Lettera di Zona",
                "nl": "Toon Zone Letter",
                "pl": "Pokaż Literę Strefy",
                "pt": "Mostrar Letra de Zona",
                "ru": "Показать букву зоны",
                "ja": "ゾーン文字を表示",
                "zh": "显示区域字母",
                "ko": "구역 문자 표시"
            },
            "description": {
                "en": "Display NATO time zone letter in output",
                "de": "NATO-Zeitzonenbuchstabe in der Ausgabe anzeigen",
                "es": "Mostrar letra de zona horaria OTAN en la salida",
                "fr": "Afficher la lettre de fuseau horaire OTAN dans la sortie",
                "it": "Visualizza la lettera del fuso orario NATO nell'output",
                "nl": "NAVO tijdzone letter in uitvoer weergeven",
                "pl": "Wyświetl literę strefy czasowej NATO w wyjściu",
                "pt": "Exibir letra de fuso horário da OTAN na saída",
                "ru": "Отображать букву часового пояса НАТО в выводе",
                "ja": "出力にNATOタイムゾーン文字を表示",
                "zh": "在输出中显示北约时区字母",
                "ko": "출력에 NATO 시간대 문자 표시"
            }
        },
        "uppercase_month": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Uppercase Month",
                "de": "Monat in Großbuchstaben",
                "es": "Mes en Mayúsculas",
                "fr": "Mois en Majuscules",
                "it": "Mese in Maiuscolo",
                "nl": "Maand in Hoofdletters",
                "pl": "Miesiąc Wielkimi Literami",
                "pt": "Mês em Maiúsculas",
                "ru": "Месяц заглавными буквами",
                "ja": "月を大文字で",
                "zh": "月份大写",
                "ko": "월 대문자"
            },
            "description": {
                "en": "Display month names in uppercase",
                "de": "Monatsnamen in Großbuchstaben anzeigen",
                "es": "Mostrar nombres de meses en mayúsculas",
                "fr": "Afficher les noms de mois en majuscules",
                "it": "Visualizza i nomi dei mesi in maiuscolo",
                "nl": "Maandnamen in hoofdletters weergeven",
                "pl": "Wyświetl nazwy miesięcy wielkimi literami",
                "pt": "Exibir nomes de meses em maiúsculas",
                "ru": "Отображать названия месяцев заглавными буквами",
                "ja": "月名を大文字で表示",
                "zh": "以大写显示月份名称",
                "ko": "월 이름을 대문자로 표시"
            }
        }
    },
    
    # NATO timezone mappings
    "nato_zones": {
        "Alpha": 1, "Bravo": 2, "Charlie": 3, "Delta": 4, "Echo": 5,
        "Foxtrot": 6, "Golf": 7, "Hotel": 8, "India": 9, "Juliet": 10,
        "Kilo": 10, "Lima": 11, "Mike": 12, "November": -1, "Oscar": -2,
        "Papa": -3, "Quebec": -4, "Romeo": -5, "Sierra": -6, "Tango": -7,
        "Uniform": -8, "Victor": -9, "Whiskey": -10, "X-ray": -11,
        "Yankee": -12, "Zulu": 0, "UTC": 0
    },
    
    # Zone letters for display
    "zone_letters": {
        "Alpha": "A", "Bravo": "B", "Charlie": "C", "Delta": "D", "Echo": "E",
        "Foxtrot": "F", "Golf": "G", "Hotel": "H", "India": "I", "Juliet": "J",
        "Kilo": "K", "Lima": "L", "Mike": "M", "November": "N", "Oscar": "O",
        "Papa": "P", "Quebec": "Q", "Romeo": "R", "Sierra": "S", "Tango": "T",
        "Uniform": "U", "Victor": "V", "Whiskey": "W", "X-ray": "X",
        "Yankee": "Y", "Zulu": "Z", "UTC": "Z"
    },
    
    # Month names for different formats
    "months": {
        "standard": ["JAN", "FEB", "MAR", "APR", "MAY", "JUN",
                    "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"],
        "rescue": ["JANUAR", "FEBRUAR", "MARCH", "APRIL", "MAI", "JUNI",
                  "JULI", "AUGUST", "SEPTEMBER", "OKTOBER", "NOVEMBER", "DEZEMBER"]
    }
}


# Import base class
try:
    from . import AlternativeTimeSensorBase
except ImportError:
    try:
        from sensor import AlternativeTimeSensorBase
    except ImportError:
        # Fallback for testing
        AlternativeTimeSensorBase = object


class NatoSensor(AlternativeTimeSensorBase if AlternativeTimeSensorBase != object else object):
    """NATO Date Time Group sensor implementation."""
    
    def __init__(self, hass, entry_data: Dict[str, Any], name: str):
        """Initialize the NATO sensor."""
        if AlternativeTimeSensorBase != object:
            super().__init__(hass, entry_data, name, CALENDAR_INFO)
        else:
            # Fallback initialization
            self._hass = hass
            self._entry_data = entry_data
            self._base_name = name
            self._calendar_info = CALENDAR_INFO
            
        self._state = None
        self._attributes = {}
        
        # Get configuration from entry data
        self._load_config()
        
        # Set sensor name based on format
        self._update_sensor_name()
    
    def _load_config(self):
        """Load configuration from entry data."""
        # Try to get options from plugin system first
        if hasattr(self, 'get_plugin_options'):
            options = self.get_plugin_options()
        else:
            # Fallback to direct access
            calendar_options = self._entry_data.get("calendar_options", {})
            options = calendar_options.get("nato", {})
        
        # Apply configuration with proper defaults
        self._format = options.get("nato_format", "basic")
        self._timezone_name = options.get("timezone_for_zone", "UTC")
        self._show_zone_letter = options.get("show_zone_letter", True)
        self._uppercase_month = options.get("uppercase_month", True)
        
        # Log configuration for debugging
        _LOGGER.debug(f"NATO sensor config loaded: format={self._format}, zone={self._timezone_name}, "
                     f"show_letter={self._show_zone_letter}, uppercase={self._uppercase_month}")
        
        # Get timezone offset
        self._zone_offset = CALENDAR_INFO["nato_zones"].get(self._timezone_name, 0)
        self._zone_letter = CALENDAR_INFO["zone_letters"].get(self._timezone_name, "Z")
    
    def _update_sensor_name(self):
        """Update sensor name based on format."""
        format_names = {
            "basic": "NATO DTG",
            "zone": "NATO Zone DTG",
            "rescue": "NATO Rescue DTG"
        }
        suffix = format_names.get(self._format, "NATO DTG")
        
        # Update the name
        if hasattr(self, '_attr_name'):
            self._attr_name = f"{self._base_name} {suffix}"
        else:
            self._name = f"{self._base_name} {suffix}"
    
    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        if hasattr(self, '_attr_name'):
            return self._attr_name
        return getattr(self, '_name', f"{self._base_name} NATO DTG")
    
    @property
    def unique_id(self) -> str:
        """Return unique ID for the sensor."""
        base_id = self._entry_data.get('entry_id', 'nato')
        return f"{base_id}_nato_{self._format}"
    
    @property
    def state(self) -> str:
        """Return the state of the sensor."""
        return self._state
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return additional state attributes."""
        return self._attributes
    
    def _get_zone_time(self) -> datetime:
        """Get the current time in the configured NATO zone."""
        now = datetime.now(pytz.UTC)
        
        # Apply zone offset
        if self._zone_offset != 0:
            now = now + timedelta(hours=self._zone_offset)
        
        return now
    
    def _format_basic(self, dt: datetime) -> str:
        """Format as basic NATO DTG: DDHHMMZ MON YY."""
        day = f"{dt.day:02d}"
        time = dt.strftime("%H%M")
        zone = self._zone_letter if self._show_zone_letter else ""
        
        month_idx = dt.month - 1
        month = CALENDAR_INFO["months"]["standard"][month_idx]
        if self._uppercase_month:
            month = month.upper()
        else:
            month = month.capitalize()
        
        year = dt.strftime("%y")
        
        if zone:
            return f"{day}{time}{zone} {month} {year}"
        else:
            return f"{day}{time} {month} {year}"
    
    def _format_zone(self, dt: datetime) -> str:
        """Format with full zone name: DD HHMM ZONE_NAME MON YY."""
        day = f"{dt.day:02d}"
        time = dt.strftime("%H%M")
        
        # Use full zone name for zone format
        zone_display = self._timezone_name if self._show_zone_letter else ""
        
        month_idx = dt.month - 1
        month = CALENDAR_INFO["months"]["standard"][month_idx]
        if self._uppercase_month:
            month = month.upper()
        else:
            month = month.capitalize()
        
        year = dt.strftime("%y")
        
        if zone_display:
            return f"{day} {time} {zone_display} {month} {year}"
        else:
            return f"{day} {time} {month} {year}"
    
    def _format_rescue(self, dt: datetime) -> str:
        """Format for rescue operations: DD HHMM MONTHNAME YY."""
        day = f"{dt.day:02d}"
        time = dt.strftime("%H%M")
        
        month_idx = dt.month - 1
        month = CALENDAR_INFO["months"]["rescue"][month_idx]
        if self._uppercase_month:
            month = month.upper()
        else:
            month = month.capitalize()
        
        year = dt.strftime("%y")
        
        # Rescue format typically doesn't use zone letters
        return f"{day} {time} {month} {year}"
    
    def _update(self):
        """Update the sensor state."""
        try:
            # Get time in configured zone
            zone_time = self._get_zone_time()
            
            # Format based on selected format
            if self._format == "zone":
                self._state = self._format_zone(zone_time)
            elif self._format == "rescue":
                self._state = self._format_rescue(zone_time)
            else:  # basic
                self._state = self._format_basic(zone_time)
            
            # Update attributes
            self._attributes = {
                "format": self._format,
                "timezone": self._timezone_name,
                "zone_letter": self._zone_letter,
                "zone_offset": f"UTC{self._zone_offset:+d}" if self._zone_offset != 0 else "UTC",
                "show_zone_letter": self._show_zone_letter,
                "uppercase_month": self._uppercase_month,
                "day": zone_time.day,
                "hour": zone_time.hour,
                "minute": zone_time.minute,
                "second": zone_time.second,
                "month": zone_time.month,
                "year": zone_time.year,
                "full_date": zone_time.strftime("%Y-%m-%d"),
                "full_time": zone_time.strftime("%H:%M:%S"),
                "iso_format": zone_time.isoformat(),
                "icon": CALENDAR_INFO.get("icon", "mdi:shield-star")
            }
            
            _LOGGER.debug(f"NATO sensor updated: {self._state}")
            
        except Exception as e:
            _LOGGER.error(f"Error updating NATO sensor: {e}", exc_info=True)
            self._state = "ERROR"
            self._attributes = {"error": str(e)}
    
    async def async_added_to_hass(self):
        """When entity is added to hass."""
        if hasattr(super(), 'async_added_to_hass'):
            await super().async_added_to_hass()
        
        # Reload configuration when added
        self._load_config()
        self._update_sensor_name()
        
        _LOGGER.info(f"NATO sensor added to Home Assistant: {self.name}")
    
    async def async_update(self):
        """Async update wrapper."""
        if hasattr(super(), 'async_update'):
            await super().async_update()
        else:
            await self._hass.async_add_executor_job(self._update)


# Legacy support - provide both class names
NATOSensor = NatoSensor


# Module-level function for calendar discovery
def get_calendar_info() -> Dict[str, Any]:
    """Get calendar information for discovery."""
    return CALENDAR_INFO