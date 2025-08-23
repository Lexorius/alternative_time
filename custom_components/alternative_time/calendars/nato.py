"""NATO Date-Time Group (DTG) Calendar Plugin for Alternative Time Systems."""
from __future__ import annotations

from datetime import datetime, timedelta
import logging
from typing import Any, Dict, Optional
from zoneinfo import ZoneInfo

from homeassistant.core import HomeAssistant

# Import from parent directory
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from ..sensor import AlternativeTimeSensorBase
except ImportError:
    from sensor import AlternativeTimeSensorBase

_LOGGER = logging.getLogger(__name__)

# Update interval in seconds
UPDATE_INTERVAL = 1

# Calendar Information Dictionary
CALENDAR_INFO = {
    "id": "nato",
    "version": "2.6.0",
    "icon": "mdi:military-tech",
    "category": "military",
    "accuracy": "second",
    "update_interval": UPDATE_INTERVAL,
    
    # Multi-language names
    "name": {
        "en": "NATO Date-Time Group",
        "de": "NATO-Zeitgruppe",
        "es": "Grupo de Fecha-Hora OTAN",
        "fr": "Groupe Date-Heure OTAN",
        "it": "Gruppo Data-Ora NATO",
        "nl": "NAVO Datum-Tijd Groep",
        "pl": "Grupa Data-Czas NATO",
        "pt": "Grupo Data-Hora NATO",
        "ru": "Группа даты и времени НАТО",
        "ja": "NATO日時グループ",
        "zh": "北约日期时间组",
        "ko": "NATO 날짜-시간 그룹"
    },
    
    # Descriptions
    "description": {
        "en": "Military time format used by NATO forces for coordination (e.g., 151430Z JAN 25)",
        "de": "Militärisches Zeitformat der NATO-Streitkräfte zur Koordination (z.B. 151430Z JAN 25)",
        "es": "Formato de hora militar usado por fuerzas de la OTAN para coordinación (ej. 151430Z ENE 25)",
        "fr": "Format horaire militaire utilisé par les forces de l'OTAN pour la coordination (ex. 151430Z JAN 25)",
        "it": "Formato orario militare usato dalle forze NATO per il coordinamento (es. 151430Z GEN 25)",
        "nl": "Militair tijdformaat gebruikt door NAVO-strijdkrachten voor coördinatie (bijv. 151430Z JAN 25)",
        "pl": "Format czasu wojskowego używany przez siły NATO do koordynacji (np. 151430Z STY 25)",
        "pt": "Formato de hora militar usado pelas forças da NATO para coordenação (ex. 151430Z JAN 25)",
        "ru": "Военный формат времени, используемый силами НАТО для координации (напр. 151430Z ЯНВ 25)",
        "ja": "NATO軍が調整に使用する軍事時刻形式 (例: 151430Z JAN 25)",
        "zh": "北约部队用于协调的军事时间格式 (例: 151430Z JAN 25)",
        "ko": "NATO군이 조정에 사용하는 군사 시간 형식 (예: 151430Z JAN 25)"
    },
    
    # NATO timezone letters
    "nato_zones": {
        "Y": {"offset": -12, "name": "Yankee"},
        "X": {"offset": -11, "name": "X-ray"},
        "W": {"offset": -10, "name": "Whiskey"},
        "V": {"offset": -9, "name": "Victor"},
        "U": {"offset": -8, "name": "Uniform"},
        "T": {"offset": -7, "name": "Tango"},
        "S": {"offset": -6, "name": "Sierra"},
        "R": {"offset": -5, "name": "Romeo"},
        "Q": {"offset": -4, "name": "Quebec"},
        "P": {"offset": -3, "name": "Papa"},
        "O": {"offset": -2, "name": "Oscar"},
        "N": {"offset": -1, "name": "November"},
        "Z": {"offset": 0, "name": "Zulu", "special": "UTC"},
        "A": {"offset": 1, "name": "Alpha"},
        "B": {"offset": 2, "name": "Bravo"},
        "C": {"offset": 3, "name": "Charlie"},
        "D": {"offset": 4, "name": "Delta"},
        "E": {"offset": 5, "name": "Echo"},
        "F": {"offset": 6, "name": "Foxtrot"},
        "G": {"offset": 7, "name": "Golf"},
        "H": {"offset": 8, "name": "Hotel"},
        "I": {"offset": 9, "name": "India"},
        "K": {"offset": 10, "name": "Kilo"},
        "L": {"offset": 11, "name": "Lima"},
        "M": {"offset": 12, "name": "Mike"}
    },
    
    # Month abbreviations
    "months": {
        "en": ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"],
        "de": ["JAN", "FEB", "MÄR", "APR", "MAI", "JUN", "JUL", "AUG", "SEP", "OKT", "NOV", "DEZ"],
        "es": ["ENE", "FEB", "MAR", "ABR", "MAY", "JUN", "JUL", "AGO", "SEP", "OCT", "NOV", "DIC"],
        "fr": ["JAN", "FÉV", "MAR", "AVR", "MAI", "JUN", "JUL", "AOÛ", "SEP", "OCT", "NOV", "DÉC"],
        "rescue_de": ["JANUAR", "FEBRUAR", "MÄRZ", "APRIL", "MAI", "JUNI", "JULI", "AUGUST", "SEPTEMBER", "OKTOBER", "NOVEMBER", "DEZEMBER"]
    },
    
    # Configuration options
    "config_options": {
        "format_type": {
            "type": "select",
            "default": "zone",
            "options": ["basic", "zone", "rescue", "aviation", "extended"],
            "label": {
                "en": "Format Type",
                "de": "Formattyp",
                "es": "Tipo de Formato",
                "fr": "Type de Format",
                "it": "Tipo di Formato",
                "nl": "Formaat Type",
                "pl": "Typ Formatu",
                "pt": "Tipo de Formato",
                "ru": "Тип формата",
                "ja": "フォーマットタイプ",
                "zh": "格式类型",
                "ko": "형식 유형"
            },
            "description": {
                "en": "Select NATO DTG format variant",
                "de": "NATO DTG-Formatvariante wählen",
                "es": "Seleccionar variante de formato DTG OTAN",
                "fr": "Sélectionner la variante de format DTG OTAN",
                "it": "Seleziona variante formato DTG NATO",
                "nl": "Selecteer NAVO DTG-formaatvariant",
                "pl": "Wybierz wariant formatu DTG NATO",
                "pt": "Selecionar variante de formato DTG NATO",
                "ru": "Выберите вариант формата DTG НАТО",
                "ja": "NATO DTG形式の変種を選択",
                "zh": "选择北约DTG格式变体",
                "ko": "NATO DTG 형식 변형 선택"
            },
            "options_labels": {
                "basic": {
                    "en": "Basic (151430)",
                    "de": "Basis (151430)",
                    "es": "Básico (151430)",
                    "fr": "Basique (151430)",
                    "it": "Base (151430)",
                    "nl": "Basis (151430)",
                    "pl": "Podstawowy (151430)",
                    "pt": "Básico (151430)",
                    "ru": "Базовый (151430)",
                    "ja": "基本 (151430)",
                    "zh": "基本 (151430)",
                    "ko": "기본 (151430)"
                },
                "zone": {
                    "en": "With Zone (151430Z JAN 25)",
                    "de": "Mit Zone (151430Z JAN 25)",
                    "es": "Con Zona (151430Z ENE 25)",
                    "fr": "Avec Zone (151430Z JAN 25)",
                    "it": "Con Zona (151430Z GEN 25)",
                    "nl": "Met Zone (151430Z JAN 25)",
                    "pl": "Ze Strefą (151430Z STY 25)",
                    "pt": "Com Zona (151430Z JAN 25)",
                    "ru": "С зоной (151430Z ЯНВ 25)",
                    "ja": "ゾーン付き (151430Z JAN 25)",
                    "zh": "带时区 (151430Z JAN 25)",
                    "ko": "시간대 포함 (151430Z JAN 25)"
                },
                "rescue": {
                    "en": "German Rescue (15 1430 JANUAR 25)",
                    "de": "Deutsche Rettung (15 1430 JANUAR 25)",
                    "es": "Rescate Alemán (15 1430 ENERO 25)",
                    "fr": "Sauvetage Allemand (15 1430 JANVIER 25)",
                    "it": "Soccorso Tedesco (15 1430 GENNAIO 25)",
                    "nl": "Duitse Redding (15 1430 JANUARI 25)",
                    "pl": "Niemiecki Ratunek (15 1430 STYCZEŃ 25)",
                    "pt": "Resgate Alemão (15 1430 JANEIRO 25)",
                    "ru": "Немецкий спасательный (15 1430 ЯНВАРЬ 25)",
                    "ja": "ドイツ救助形式 (15 1430 JANUAR 25)",
                    "zh": "德国救援格式 (15 1430 JANUAR 25)",
                    "ko": "독일 구조 형식 (15 1430 JANUAR 25)"
                },
                "aviation": {
                    "en": "Aviation (151430Z ZULU)",
                    "de": "Luftfahrt (151430Z ZULU)",
                    "es": "Aviación (151430Z ZULU)",
                    "fr": "Aviation (151430Z ZULU)",
                    "it": "Aviazione (151430Z ZULU)",
                    "nl": "Luchtvaart (151430Z ZULU)",
                    "pl": "Lotnictwo (151430Z ZULU)",
                    "pt": "Aviação (151430Z ZULU)",
                    "ru": "Авиация (151430Z ZULU)",
                    "ja": "航空 (151430Z ZULU)",
                    "zh": "航空 (151430Z ZULU)",
                    "ko": "항공 (151430Z ZULU)"
                },
                "extended": {
                    "en": "Extended (151430:45Z JAN 2025)",
                    "de": "Erweitert (151430:45Z JAN 2025)",
                    "es": "Extendido (151430:45Z ENE 2025)",
                    "fr": "Étendu (151430:45Z JAN 2025)",
                    "it": "Esteso (151430:45Z GEN 2025)",
                    "nl": "Uitgebreid (151430:45Z JAN 2025)",
                    "pl": "Rozszerzony (151430:45Z STY 2025)",
                    "pt": "Estendido (151430:45Z JAN 2025)",
                    "ru": "Расширенный (151430:45Z ЯНВ 2025)",
                    "ja": "拡張 (151430:45Z JAN 2025)",
                    "zh": "扩展 (151430:45Z JAN 2025)",
                    "ko": "확장 (151430:45Z JAN 2025)"
                }
            }
        },
        "show_zone_name": {
            "type": "boolean",
            "default": False,
            "label": {
                "en": "Show Zone Name",
                "de": "Zonennamen anzeigen",
                "es": "Mostrar Nombre de Zona",
                "fr": "Afficher le Nom de Zone",
                "it": "Mostra Nome Zona",
                "nl": "Toon Zone Naam",
                "pl": "Pokaż Nazwę Strefy",
                "pt": "Mostrar Nome da Zona",
                "ru": "Показать название зоны",
                "ja": "ゾーン名を表示",
                "zh": "显示时区名称",
                "ko": "시간대 이름 표시"
            },
            "description": {
                "en": "Display phonetic zone name (e.g., 'Zulu' for Z)",
                "de": "Phonetischen Zonennamen anzeigen (z.B. 'Zulu' für Z)",
                "es": "Mostrar nombre fonético de zona (ej. 'Zulu' para Z)",
                "fr": "Afficher le nom phonétique de zone (ex. 'Zulu' pour Z)",
                "it": "Mostra nome fonetico zona (es. 'Zulu' per Z)",
                "nl": "Toon fonetische zonenaam (bijv. 'Zulu' voor Z)",
                "pl": "Pokaż fonetyczną nazwę strefy (np. 'Zulu' dla Z)",
                "pt": "Mostrar nome fonético da zona (ex. 'Zulu' para Z)",
                "ru": "Показать фонетическое название зоны (напр. 'Zulu' для Z)",
                "ja": "音声ゾーン名を表示 (例: Zの場合 'Zulu')",
                "zh": "显示语音时区名称 (例如: Z为'Zulu')",
                "ko": "음성 시간대 이름 표시 (예: Z의 경우 'Zulu')"
            }
        },
        "use_local_zone": {
            "type": "boolean",
            "default": False,
            "label": {
                "en": "Use Local Zone",
                "de": "Lokale Zone verwenden",
                "es": "Usar Zona Local",
                "fr": "Utiliser Zone Locale",
                "it": "Usa Zona Locale",
                "nl": "Gebruik Lokale Zone",
                "pl": "Użyj Strefy Lokalnej",
                "pt": "Usar Zona Local",
                "ru": "Использовать местную зону",
                "ja": "ローカルゾーンを使用",
                "zh": "使用本地时区",
                "ko": "로컬 시간대 사용"
            },
            "description": {
                "en": "Use local timezone instead of UTC/Zulu",
                "de": "Lokale Zeitzone statt UTC/Zulu verwenden",
                "es": "Usar zona horaria local en lugar de UTC/Zulu",
                "fr": "Utiliser le fuseau horaire local au lieu d'UTC/Zulu",
                "it": "Usa fuso orario locale invece di UTC/Zulu",
                "nl": "Gebruik lokale tijdzone in plaats van UTC/Zulu",
                "pl": "Użyj lokalnej strefy czasowej zamiast UTC/Zulu",
                "pt": "Usar fuso horário local em vez de UTC/Zulu",
                "ru": "Использовать местный часовой пояс вместо UTC/Zulu",
                "ja": "UTC/Zuluの代わりにローカルタイムゾーンを使用",
                "zh": "使用本地时区而不是UTC/Zulu",
                "ko": "UTC/Zulu 대신 로컬 시간대 사용"
            }
        }
    }
}


class NATOTimeSensor(AlternativeTimeSensorBase):
    """Sensor for displaying NATO Date-Time Group."""
    
    # Class-level update interval
    UPDATE_INTERVAL = UPDATE_INTERVAL
    
    def __init__(self, base_name: str, hass: HomeAssistant) -> None:
        """Initialize the NATO time sensor."""
        super().__init__(base_name, "nato", CALENDAR_INFO["name"])
        
        self._hass = hass
        self._attr_icon = CALENDAR_INFO["icon"]
        self._update_interval = timedelta(seconds=UPDATE_INTERVAL)
        
        # Configuration defaults
        self._format_type = "zone"
        self._show_zone_name = False
        self._use_local_zone = False
        self._show_seconds = False
        self._uppercase = True
        self._include_year = True
        
        # Will be loaded from config
        self._options_loaded = False
        
        _LOGGER.debug(f"Initialized NATO sensor with base_name: {base_name}")
    
    def _load_options(self) -> None:
        """Load options from config entry."""
        if self._options_loaded:
            return
            
        try:
            # Get the config entry from entity registry
            entity_registry = self._hass.data.get("entity_registry")
            if not entity_registry:
                _LOGGER.debug("Entity registry not available yet")
                return
            
            # Find our entity
            entity_id = self.entity_id
            if not entity_id:
                _LOGGER.debug("Entity ID not set yet")
                return
                
            entity_entry = entity_registry.entities.get(entity_id)
            if not entity_entry:
                _LOGGER.debug(f"Entity not found in registry: {entity_id}")
                return
                
            # Get config entry
            config_entry_id = entity_entry.config_entry_id
            if not config_entry_id:
                _LOGGER.debug("No config entry ID for entity")
                return
                
            config_entries = self._hass.config_entries
            config_entry = config_entries.async_get_entry(config_entry_id)
            if not config_entry:
                _LOGGER.debug(f"Config entry not found: {config_entry_id}")
                return
            
            # Get options from config entry data
            if hasattr(config_entry, 'data') and config_entry.data:
                plugin_options = config_entry.data.get('plugin_options', {})
                nato_options = plugin_options.get('nato', {})
                
                if nato_options:
                    # Load configuration values
                    self._format_type = nato_options.get('format_type', 'zone')
                    self._show_zone_name = nato_options.get('show_zone_name', False)
                    self._use_local_zone = nato_options.get('use_local_zone', False)
                    
                    # Extended format includes seconds
                    self._show_seconds = (self._format_type == 'extended')
                    
                    # Aviation format uses uppercase
                    self._uppercase = (self._format_type in ['zone', 'aviation', 'extended'])
                    
                    # Extended format includes full year
                    self._include_year = (self._format_type in ['zone', 'rescue', 'extended'])
                    
                    self._options_loaded = True
                    
                    _LOGGER.info(
                        f"NATO options loaded - format: {self._format_type}, "
                        f"show_zone: {self._show_zone_name}, use_local: {self._use_local_zone}"
                    )
                else:
                    _LOGGER.debug("No NATO options found in config")
            else:
                _LOGGER.debug("No data in config entry")
                
        except Exception as e:
            _LOGGER.error(f"Error loading NATO options: {e}")
    
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
        if self._use_local_zone:
            # Get local timezone offset
            offset = earth_time.astimezone().strftime('%z')
            if offset:
                hours = int(offset[1:3])
                if offset[0] == '-':
                    hours = -hours
                
                # Find matching NATO zone
                for letter, info in CALENDAR_INFO["nato_zones"].items():
                    if info["offset"] == hours:
                        return letter, info["name"]
            
            # Default to Zulu if no match
            return "Z", "Zulu"
        else:
            # Always use Zulu (UTC)
            return "Z", "Zulu"
    
    def _format_nato_time(self, earth_time: datetime) -> str:
        """Format time according to selected NATO format."""
        # Ensure options are loaded
        if not self._options_loaded:
            self._load_options()
            
        # Get timezone info
        zone_letter, zone_name = self._get_timezone_info(earth_time)
        
        # Get month abbreviation
        month_idx = earth_time.month - 1
        
        # Select month format based on type
        if self._format_type == "rescue":
            # German rescue format uses full month names
            months = CALENDAR_INFO["months"].get("rescue_de", CALENDAR_INFO["months"]["en"])
        else:
            # Standard formats use abbreviations
            months = CALENDAR_INFO["months"]["en"]
        
        month = months[month_idx]
        
        # Format based on selected type
        if self._format_type == "basic":
            # Basic format: DDHHMM
            result = f"{earth_time.day:02d}{earth_time.hour:02d}{earth_time.minute:02d}"
            
        elif self._format_type == "zone":
            # Standard DTG: DDHHMM[Zone] MON YY
            result = f"{earth_time.day:02d}{earth_time.hour:02d}{earth_time.minute:02d}{zone_letter} {month} {earth_time.year % 100:02d}"
            
        elif self._format_type == "rescue":
            # German rescue: DD HHMM MON JJ
            result = f"{earth_time.day:02d} {earth_time.hour:02d}{earth_time.minute:02d} {month} {earth_time.year % 100:02d}"
            
        elif self._format_type == "aviation":
            # Aviation format: DDHHMM[Zone] with phonetic
            if self._show_zone_name:
                result = f"{earth_time.day:02d}{earth_time.hour:02d}{earth_time.minute:02d}{zone_letter} {zone_name.upper()}"
            else:
                result = f"{earth_time.day:02d}{earth_time.hour:02d}{earth_time.minute:02d}{zone_letter}"
                
        elif self._format_type == "extended":
            # Extended format: DDHHMMSS[Zone] MON YYYY
            result = f"{earth_time.day:02d}{earth_time.hour:02d}{earth_time.minute:02d}:{earth_time.second:02d}{zone_letter} {month} {earth_time.year}"
            
        else:
            # Fallback to zone format
            result = f"{earth_time.day:02d}{earth_time.hour:02d}{earth_time.minute:02d}{zone_letter} {month} {earth_time.year % 100:02d}"
        
        # Apply uppercase if needed
        if self._uppercase:
            result = result.upper()
        
        return result
    
    def calculate_time(self) -> Dict[str, Any]:
        """Calculate current NATO DTG."""
        # Get current time
        if self._use_local_zone:
            earth_time = datetime.now()
        else:
            earth_time = datetime.now(ZoneInfo("UTC"))
        
        # Format the time
        formatted = self._format_nato_time(earth_time)
        
        # Get zone info
        zone_letter, zone_name = self._get_timezone_info(earth_time)
        
        # Build result dictionary
        result = {
            "formatted": formatted,
            "day": earth_time.day,
            "hour": earth_time.hour,
            "minute": earth_time.minute,
            "second": earth_time.second,
            "zone_letter": zone_letter,
            "zone_name": zone_name,
            "month": CALENDAR_INFO["months"]["en"][earth_time.month - 1],
            "year": earth_time.year,
            "format_type": self._format_type,
            "earth_time": earth_time.strftime("%Y-%m-%d %H:%M:%S %Z")
        }
        
        # Add phonetic alphabet reference
        if self._show_zone_name:
            result["zone_phonetic"] = f"{zone_letter} - {zone_name}"
        
        return result
    
    def update(self) -> None:
        """Update the sensor."""
        # Calculate NATO time
        self._nato_time = self.calculate_time()
        
        # Set state to formatted time
        self._state = self._nato_time["formatted"]
        
        _LOGGER.debug(f"Updated NATO DTG to {self._state} (format: {self._format_type})")


# Export the sensor class
__all__ = ["NATOTimeSensor", "CALENDAR_INFO", "UPDATE_INTERVAL"]