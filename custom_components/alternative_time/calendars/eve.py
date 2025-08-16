"""EVE Online Time (New Eden Standard Time) implementation - Version 2.5."""
from __future__ import annotations

from datetime import datetime
import logging
from typing import Dict, Any

from homeassistant.core import HomeAssistant
from ..sensor import AlternativeTimeSensorBase

_LOGGER = logging.getLogger(__name__)

# ============================================
# CALENDAR METADATA
# ============================================

# Update interval in seconds (1 second for real-time display)
UPDATE_INTERVAL = 1

# Complete calendar information for auto-discovery
CALENDAR_INFO = {
    "id": "eve",
    "version": "2.5.0",
    "icon": "mdi:space-station",
    "category": "scifi",
    "accuracy": "fictional",
    "update_interval": UPDATE_INTERVAL,
    
    # Multi-language names
    "name": {
        "en": "EVE Online Time",
        "de": "EVE Online Zeit",
        "es": "Tiempo de EVE Online",
        "fr": "Temps EVE Online",
        "it": "Tempo di EVE Online",
        "nl": "EVE Online Tijd",
        "pt": "Tempo de EVE Online",
        "ru": "Время EVE Online",
        "ja": "EVE Online時間",
        "zh": "EVE Online时间",
        "ko": "EVE 온라인 시간"
    },
    
    # Short descriptions for UI
    "description": {
        "en": "New Eden Standard Time (NEST) from EVE Online universe (e.g. YC 127.01.15 14:30:00)",
        "de": "New Eden Standardzeit (NEST) aus dem EVE Online Universum (z.B. YC 127.01.15 14:30:00)",
        "es": "Hora Estándar de Nuevo Edén (NEST) del universo EVE Online",
        "fr": "Temps Standard de New Eden (NEST) de l'univers EVE Online",
        "it": "Ora Standard di New Eden (NEST) dall'universo EVE Online",
        "nl": "New Eden Standaard Tijd (NEST) uit het EVE Online universum",
        "pt": "Hora Padrão de New Eden (NEST) do universo EVE Online",
        "ru": "Стандартное время Нового Эдема (NEST) из вселенной EVE Online",
        "ja": "EVE Onlineユニバースのニューエデン標準時（NEST）",
        "zh": "EVE Online宇宙的新伊甸标准时间（NEST）",
        "ko": "EVE 온라인 우주의 뉴 에덴 표준시 (NEST)"
    },
    
    # Detailed information for documentation
    "detailed_info": {
        "en": {
            "overview": "EVE Online uses New Eden Standard Time (NEST) based on UTC",
            "calendar": "Yoiul Conference (YC) calendar system",
            "epoch": "YC 0 corresponds to 23236 AD in Earth time",
            "game_start": "YC 105 = 2003 (EVE Online launch year)",
            "structure": "Uses standard Earth months and days, all times in UTC",
            "lore": "The Yoiul Conference established a universal calendar after the collapse of the EVE Gate",
            "empires": "Used by all four major empires: Amarr, Caldari, Gallente, and Minmatar",
            "format": "Standard format: YC XXX.MM.DD HH:MM:SS"
        },
        "de": {
            "overview": "EVE Online verwendet New Eden Standardzeit (NEST) basierend auf UTC",
            "calendar": "Yoiul Conference (YC) Kalendersystem",
            "epoch": "YC 0 entspricht 23236 n.Chr. in Erdzeit",
            "game_start": "YC 105 = 2003 (EVE Online Startjahr)",
            "structure": "Verwendet Standard-Erdmonate und -tage, alle Zeiten in UTC",
            "lore": "Die Yoiul-Konferenz etablierte einen universellen Kalender nach dem Kollaps des EVE-Tors",
            "empires": "Verwendet von allen vier großen Imperien: Amarr, Caldari, Gallente und Minmatar",
            "format": "Standardformat: YC XXX.MM.DD HH:MM:SS"
        }
    },
    
    # EVE-specific data
    "eve_data": {
        "yc_epoch_year": 2003,  # Real year when YC 105 started
        "yc_epoch_value": 105,  # YC year in 2003
        "eve_gate_collapse": "YC 0",
        
        # Major empires
        "empires": {
            "amarr": {"name": "Amarr Empire", "capital": "Amarr Prime"},
            "caldari": {"name": "Caldari State", "capital": "New Caldari"},
            "gallente": {"name": "Gallente Federation", "capital": "Villore"},
            "minmatar": {"name": "Minmatar Republic", "capital": "Pator"}
        },
        
        # Notable events in YC timeline
        "events": {
            105: "Capsuleer program begins",
            106: "Empyrean Age",
            110: "Sansha's Nation incursions",
            111: "Arek'Jaalan Project",
            113: "Battle of Asakai",
            114: "Bloodbath of B-R5RB",
            116: "Caroline's Star",
            117: "Drifters appear",
            118: "Citadel expansion",
            119: "Lifeblood expansion",
            120: "Into the Abyss",
            122: "Invasion begins",
            124: "Pochven established"
        },
        
        # Notable systems
        "systems": {
            "jita": "Major trade hub",
            "amarr": "Amarr Empire capital",
            "dodixie": "Gallente trade hub",
            "rens": "Minmatar trade hub",
            "hek": "Regional trade center"
        },
        
        # Time zones (all use UTC but with lore names)
        "time_references": {
            "NEST": "New Eden Standard Time (UTC)",
            "CONCORD": "CONCORD Universal Time",
            "Capsuleer": "Capsuleer Standard Time"
        }
    },
    
    # Additional metadata
    "reference_url": "https://wiki.eveuniversity.org/Lore",
    "documentation_url": "https://www.eveonline.com",
    "origin": "CCP Games, Iceland",
    "created_by": "CCP Games",
    "introduced": "May 6, 2003",
    
    # Example format
    "example": "YC 127.01.15 14:30:00",
    "example_meaning": "Yoiul Conference year 127, January 15th, 14:30:00 NEST",
    
    # Related calendars
    "related": ["gregorian", "stardate", "scifi"],
    
    # Tags for searching and filtering
    "tags": [
        "scifi", "eve", "online", "gaming", "mmorpg", "space",
        "new_eden", "capsuleer", "yoiul", "concord", "nest"
    ],
    
    # Special features
    "features": {
        "real_time": True,
        "utc_based": True,
        "lore_rich": True,
        "game_events": True,
        "precision": "second"
    },
    
    # Configuration options for this calendar
    "config_options": {
        "show_nest": {
            "type": "boolean",
            "default": True,
            "description": {
                "en": "Show NEST (New Eden Standard Time) label",
                "de": "NEST (New Eden Standardzeit) Label anzeigen"
            }
        },
        "show_event": {
            "type": "boolean",
            "default": True,
            "description": {
                "en": "Show notable YC events",
                "de": "Bemerkenswerte YC-Ereignisse anzeigen"
            }
        },
        "format": {
            "type": "select",
            "default": "full",
            "options": ["full", "date", "time"],
            "description": {
                "en": "Display format",
                "de": "Anzeigeformat"
            }
        }
    }
}


class EveOnlineTimeSensor(AlternativeTimeSensorBase):
    """Sensor for displaying EVE Online Time (New Eden Standard Time)."""
    
    # Class-level update interval
    UPDATE_INTERVAL = 1  # Update every second
    
    def __init__(self, base_name: str, hass: HomeAssistant) -> None:
        """Initialize the EVE Online time sensor."""
        super().__init__(base_name, hass)
        
        # Get translated name from metadata
        calendar_name = self._translate('name', 'EVE Online Time')
        
        # Set sensor attributes
        self._attr_name = f"{base_name} {calendar_name}"
        self._attr_unique_id = f"{base_name}_eve_online"
        self._attr_icon = CALENDAR_INFO.get("icon", "mdi:space-station")
        
        # Configuration options
        self._show_nest = True
        self._show_event = True
        self._format = "full"
        
        # EVE data
        self._eve_data = CALENDAR_INFO["eve_data"]
        
        _LOGGER.debug(f"Initialized EVE Online Time sensor: {self._attr_name}")
    
    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes."""
        attrs = super().extra_state_attributes
        
        # Add EVE-specific attributes
        if hasattr(self, '_eve_time'):
            attrs.update(self._eve_time)
            
            # Add description in user's language
            attrs["description"] = self._translate('description')
            
            # Add reference
            attrs["reference"] = CALENDAR_INFO.get('reference_url', '')
        
        return attrs
    
    def _calculate_eve_time(self, earth_time: datetime) -> Dict[str, Any]:
        """Calculate EVE Online Time from standard time."""
        
        # EVE uses UTC
        utc_time = datetime.utcnow()
        
        # Calculate YC year
        years_since_launch = utc_time.year - self._eve_data["yc_epoch_year"]
        yc_year = self._eve_data["yc_epoch_value"] + years_since_launch
        
        # Check for notable events
        event = self._eve_data["events"].get(yc_year, "")
        
        # Format time based on configuration
        if self._format == "date":
            formatted = f"YC {yc_year}.{utc_time.month:02d}.{utc_time.day:02d}"
        elif self._format == "time":
            formatted = f"{utc_time.hour:02d}:{utc_time.minute:02d}:{utc_time.second:02d}"
        else:  # full
            formatted = f"YC {yc_year}.{utc_time.month:02d}.{utc_time.day:02d} {utc_time.hour:02d}:{utc_time.minute:02d}:{utc_time.second:02d}"
        
        if self._show_nest:
            formatted += " NEST"
        
        result = {
            "yc_year": yc_year,
            "month": utc_time.month,
            "day": utc_time.day,
            "hour": utc_time.hour,
            "minute": utc_time.minute,
            "second": utc_time.second,
            "formatted": formatted,
            "nest_time": f"{utc_time.hour:02d}:{utc_time.minute:02d}:{utc_time.second:02d}",
            "date_yc": f"YC {yc_year}.{utc_time.month:02d}.{utc_time.day:02d}",
            "utc_time": utc_time.strftime("%Y-%m-%d %H:%M:%S UTC"),
            "full_display": formatted
        }
        
        if self._show_event and event:
            result["notable_event"] = event
            result["full_display"] += f" | {event}"
        
        return result
    
    def update(self) -> None:
        """Update the sensor."""
        now = datetime.now()
        self._eve_time = self._calculate_eve_time(now)
        
        # Set state to formatted EVE time
        self._state = self._eve_time["formatted"]
        
        _LOGGER.debug(f"Updated EVE Online Time to {self._state}")