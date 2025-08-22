"""World of Warcraft Calendar implementation - Version 2.6."""
from __future__ import annotations

from datetime import datetime, timedelta
import logging
from typing import Dict, Any

from homeassistant.core import HomeAssistant
from ..sensor import AlternativeTimeSensorBase

_LOGGER = logging.getLogger(__name__)

# ============================================
# CALENDAR METADATA
# ============================================

# Update interval in seconds (3600 seconds = 1 hour for game world dates)
UPDATE_INTERVAL = 3600

# Complete calendar information for auto-discovery
CALENDAR_INFO = {
    "id": "warcraft",
    "version": "2.6.0",
    "icon": "mdi:sword",
    "category": "gaming",
    "accuracy": "fictional",
    "update_interval": UPDATE_INTERVAL,
    
    # Multi-language names
    "name": {
        "en": "World of Warcraft Calendar",
        "de": "World of Warcraft Kalender",
        "es": "Calendario de World of Warcraft",
        "fr": "Calendrier World of Warcraft",
        "it": "Calendario di World of Warcraft",
        "nl": "World of Warcraft Kalender",
        "pt": "Calendário World of Warcraft",
        "ru": "Календарь World of Warcraft",
        "ja": "ワールド・オブ・ウォークラフト暦",
        "zh": "魔兽世界日历",
        "ko": "월드 오브 워크래프트 달력"
    },
    
    # Short descriptions for UI
    "description": {
        "en": "Azeroth calendar with seasonal events and moon phases",
        "de": "Azeroth-Kalender mit saisonalen Events und Mondphasen",
        "es": "Calendario de Azeroth con eventos estacionales y fases lunares",
        "fr": "Calendrier d'Azeroth avec événements saisonniers et phases lunaires",
        "it": "Calendario di Azeroth con eventi stagionali e fasi lunari",
        "nl": "Azeroth kalender met seizoensgebonden evenementen en maanfasen",
        "pt": "Calendário de Azeroth com eventos sazonais e fases da lua",
        "ru": "Календарь Азерота с сезонными событиями и фазами луны",
        "ja": "季節のイベントと月相を含むアゼロスカレンダー",
        "zh": "包含季节活动和月相的艾泽拉斯日历",
        "ko": "계절 이벤트와 달의 위상이 포함된 아제로스 달력"
    },
    
    # Warcraft-specific calendar data
    "warcraft_data": {
        # Months in Azeroth
        "months": [
            {"name": "January", "days": 31, "season": "Winter"},
            {"name": "February", "days": 28, "season": "Winter"},
            {"name": "March", "days": 31, "season": "Spring"},
            {"name": "April", "days": 30, "season": "Spring"},
            {"name": "May", "days": 31, "season": "Spring"},
            {"name": "June", "days": 30, "season": "Summer"},
            {"name": "July", "days": 31, "season": "Summer"},
            {"name": "August", "days": 31, "season": "Summer"},
            {"name": "September", "days": 30, "season": "Fall"},
            {"name": "October", "days": 31, "season": "Fall"},
            {"name": "November", "days": 30, "season": "Fall"},
            {"name": "December", "days": 31, "season": "Winter"}
        ],
        
        # Days of the week in Azeroth
        "weekdays": [
            "Day of the Sun",
            "Day of the Moon", 
            "Day of the Earth",
            "Day of the Storm",
            "Day of the Sky",
            "Day of the Stars",
            "Day of the Wisp"
        ],
        
        # Special annual events
        "events": {
            "1-1": "New Year",
            "1-23": "Lunar Festival Start",
            "2-14": "Love is in the Air",
            "3-17": "Noblegarden",
            "4-30": "Children's Week Start",
            "6-21": "Midsummer Fire Festival Start",
            "7-4": "Fireworks Spectacular",
            "9-19": "Harvest Festival",
            "9-20": "Brewfest Start",
            "10-18": "Hallow's End Start",
            "11-1": "Day of the Dead",
            "11-7": "Pilgrim's Bounty Start",
            "12-15": "Winter Veil Start"
        },
        
        # Moons of Azeroth
        "moons": {
            "white_lady": {
                "name": "The White Lady",
                "cycle_days": 28,
                "phases": ["New", "Waxing Crescent", "First Quarter", "Waxing Gibbous", 
                          "Full", "Waning Gibbous", "Last Quarter", "Waning Crescent"]
            },
            "blue_child": {
                "name": "The Blue Child",
                "cycle_days": 35,
                "phases": ["Hidden", "Visible"]
            }
        },
        
        # Timeline reference (Years since the Dark Portal opened)
        "epoch_event": "Opening of the Dark Portal",
        "current_year": 35,  # Year 35 after the Dark Portal
        
        # Dragon Aspects and their domains
        "dragon_aspects": {
            "Alexstrasza": "Life",
            "Ysera": "Dreams",
            "Nozdormu": "Time",
            "Kalecgos": "Magic",
            "Wrathion": "Earth"
        }
    },
    
    # Additional metadata
    "reference_url": "https://wowpedia.fandom.com/wiki/Calendar",
    "documentation_url": "https://worldofwarcraft.com/",
    "origin": "Blizzard Entertainment",
    "created_by": "World of Warcraft Team",
    "introduced": "2004",
    
    # Related calendars
    "related": ["elder_scrolls", "star_wars"],
    
    # Tags for searching and filtering
    "tags": [
        "gaming", "fantasy", "warcraft", "azeroth", "blizzard",
        "mmorpg", "seasonal", "events", "moons", "dragons"
    ],
    
    # Configuration options for this calendar
    "config_options": {
        "faction": {
            "type": "select",
            "default": "Neutral",
            "options": ["Alliance", "Horde", "Neutral"],
            "label": {
                "en": "Faction",
                "de": "Fraktion",
                "es": "Facción",
                "fr": "Faction",
                "it": "Fazione",
                "nl": "Factie",
                "pt": "Facção",
                "ru": "Фракция",
                "ja": "陣営",
                "zh": "阵营",
                "ko": "진영"
            },
            "description": {
                "en": "Choose your faction for specific holidays",
                "de": "Wähle deine Fraktion für spezifische Feiertage"
            }
        },
        "region": {
            "type": "select",
            "default": "Eastern Kingdoms",
            "options": ["Eastern Kingdoms", "Kalimdor", "Northrend", "Pandaria", "Broken Isles", "Shadowlands"],
            "label": {
                "en": "Region",
                "de": "Region",
                "es": "Región",
                "fr": "Région",
                "it": "Regione",
                "nl": "Regio",
                "pt": "Região",
                "ru": "Регион",
                "ja": "地域",
                "zh": "地区",
                "ko": "지역"
            },
            "description": {
                "en": "Select your current region in Azeroth",
                "de": "Wähle deine aktuelle Region in Azeroth"
            }
        },
        "show_events": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show Events",
                "de": "Events anzeigen",
                "es": "Mostrar eventos",
                "fr": "Afficher les événements",
                "it": "Mostra eventi",
                "nl": "Toon evenementen",
                "pt": "Mostrar eventos",
                "ru": "Показать события",
                "ja": "イベントを表示",
                "zh": "显示事件",
                "ko": "이벤트 표시"
            },
            "description": {
                "en": "Display seasonal and special events",
                "de": "Zeige saisonale und besondere Events"
            }
        },
        "show_moons": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show Moon Phases",
                "de": "Mondphasen anzeigen",
                "es": "Mostrar fases lunares",
                "fr": "Afficher les phases lunaires",
                "it": "Mostra fasi lunari",
                "nl": "Toon maanfasen",
                "pt": "Mostrar fases da lua",
                "ru": "Показать фазы луны",
                "ja": "月相を表示",
                "zh": "显示月相",
                "ko": "달의 위상 표시"
            },
            "description": {
                "en": "Show phases of Azeroth's moons",
                "de": "Zeige Phasen der Monde von Azeroth"
            }
        },
        "show_dragon_aspect": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show Dragon Aspect",
                "de": "Drachenaspekt anzeigen",
                "es": "Mostrar aspecto dragón",
                "fr": "Afficher l'aspect dragon",
                "it": "Mostra aspetto drago",
                "nl": "Toon drakenaspect",
                "pt": "Mostrar aspecto dragão",
                "ru": "Показать аспект дракона",
                "ja": "ドラゴンアスペクトを表示",
                "zh": "显示龙族守护者",
                "ko": "용의 위상 표시"
            },
            "description": {
                "en": "Display the current Dragon Aspect blessing",
                "de": "Zeige den aktuellen Drachenaspekt-Segen"
            }
        }
    }
}


class WarcraftCalendarSensor(AlternativeTimeSensorBase):
    """Sensor for displaying World of Warcraft Calendar."""
    
    # Class-level update interval
    UPDATE_INTERVAL = UPDATE_INTERVAL
    
    def __init__(self, base_name: str, hass: HomeAssistant) -> None:
        """Initialize the Warcraft calendar sensor."""
        super().__init__(base_name, hass)
        
        # Store CALENDAR_INFO as instance variable for _translate method
        self._calendar_info = CALENDAR_INFO
        
        # Get translated name from metadata
        calendar_name = self._translate('name', 'World of Warcraft Calendar')
        
        # Set sensor attributes
        self._attr_name = f"{base_name} {calendar_name}"
        self._attr_unique_id = f"{base_name}_warcraft"
        self._attr_icon = CALENDAR_INFO.get("icon", "mdi:sword")
        
        # Configuration options with defaults from CALENDAR_INFO
        config_defaults = CALENDAR_INFO.get("config_options", {})
        self._faction = config_defaults.get("faction", {}).get("default", "Neutral")
        self._region = config_defaults.get("region", {}).get("default", "Eastern Kingdoms")
        self._show_events = config_defaults.get("show_events", {}).get("default", True)
        self._show_moons = config_defaults.get("show_moons", {}).get("default", True)
        self._show_dragon_aspect = config_defaults.get("show_dragon_aspect", {}).get("default", True)
        
        # Warcraft data
        self._warcraft_data = CALENDAR_INFO["warcraft_data"]
        
        # Flag to track if options have been loaded
        self._options_loaded = False
        
        # Initialize state
        self._state = None
        self._warcraft_date = {}
        
        _LOGGER.debug(f"Initialized Warcraft Calendar sensor: {self._attr_name}")
    
    def _load_options(self) -> None:
        """Load plugin options after IDs are set."""
        if self._options_loaded:
            return
            
        try:
            options = self.get_plugin_options()
            if options:
                # Update configuration from plugin options
                self._faction = options.get("faction", self._faction)
                self._region = options.get("region", self._region)
                self._show_events = options.get("show_events", self._show_events)
                self._show_moons = options.get("show_moons", self._show_moons)
                self._show_dragon_aspect = options.get("show_dragon_aspect", self._show_dragon_aspect)
                
                _LOGGER.debug(f"Warcraft sensor loaded options: faction={self._faction}, "
                            f"region={self._region}, show_events={self._show_events}")
            else:
                _LOGGER.debug("Warcraft sensor using default options - no custom options found")
                
            self._options_loaded = True
        except Exception as e:
            _LOGGER.debug(f"Warcraft sensor could not load options yet: {e}")
    
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
        
        # Add Warcraft-specific attributes
        if self._warcraft_date:
            attrs.update(self._warcraft_date)
            
            # Add description in user's language
            attrs["description"] = self._translate('description')
            
            # Add reference
            attrs["reference"] = CALENDAR_INFO.get('reference_url', '')
            
            # Add faction and region info
            attrs["faction"] = self._faction
            attrs["region"] = self._region
        
        return attrs
    
    def _calculate_moon_phase(self, days_since_epoch: int, moon_data: dict) -> str:
        """Calculate moon phase based on cycle."""
        cycle_position = days_since_epoch % moon_data["cycle_days"]
        
        if "phases" in moon_data and len(moon_data["phases"]) > 2:
            # For moons with multiple phases (White Lady)
            phase_length = moon_data["cycle_days"] / len(moon_data["phases"])
            phase_index = int(cycle_position / phase_length)
            return moon_data["phases"][min(phase_index, len(moon_data["phases"]) - 1)]
        else:
            # For binary visibility (Blue Child)
            if cycle_position < moon_data["cycle_days"] / 2:
                return "Visible"
            else:
                return "Hidden"
    
    def _get_current_event(self, month: int, day: int) -> str:
        """Get current event if any."""
        date_key = f"{month}-{day}"
        events = self._warcraft_data["events"]
        
        # Check for exact date match
        if date_key in events:
            return events[date_key]
        
        # Check for ongoing events (simplified - in reality would need date ranges)
        ongoing_events = {
            (1, 23, 2, 10): "Lunar Festival",
            (6, 21, 7, 5): "Midsummer Fire Festival",
            (9, 20, 10, 6): "Brewfest",
            (10, 18, 11, 1): "Hallow's End",
            (11, 7, 11, 30): "Pilgrim's Bounty",
            (12, 15, 1, 2): "Winter Veil"
        }
        
        for (start_m, start_d, end_m, end_d), event in ongoing_events.items():
            if start_m <= month <= end_m:
                if (month == start_m and day >= start_d) or (month == end_m and day <= end_d) or (start_m < month < end_m):
                    return event
        
        return None
    
    def _get_dragon_aspect_blessing(self, day_of_year: int) -> tuple:
        """Get current Dragon Aspect blessing (rotates every 73 days)."""
        aspects = list(self._warcraft_data["dragon_aspects"].items())
        aspect_index = (day_of_year // 73) % len(aspects)
        return aspects[aspect_index]
    
    def _calculate_warcraft_date(self, earth_date: datetime) -> Dict[str, Any]:
        """Calculate Warcraft calendar date from Earth date."""
        
        # Calculate day of year
        day_of_year = earth_date.timetuple().tm_yday
        
        # Map to Warcraft calendar (using Earth calendar as base for simplicity)
        month = earth_date.month
        day = earth_date.day
        year = self._warcraft_data["current_year"]
        
        # Get month data
        month_data = self._warcraft_data["months"][month - 1]
        month_name = month_data["name"]
        season = month_data["season"]
        
        # Get weekday
        weekday = self._warcraft_data["weekdays"][earth_date.weekday()]
        
        # Calculate days since epoch for moon phases
        epoch_date = datetime(2004, 11, 23)  # WoW release date
        days_since_epoch = (earth_date - epoch_date).days
        
        # Calculate moon phases
        white_lady_phase = self._calculate_moon_phase(
            days_since_epoch, 
            self._warcraft_data["moons"]["white_lady"]
        )
        blue_child_phase = self._calculate_moon_phase(
            days_since_epoch,
            self._warcraft_data["moons"]["blue_child"]
        )
        
        # Format the date
        formatted = f"Year {year}, {weekday}, {day} {month_name}"
        
        result = {
            "year": year,
            "month": month,
            "month_name": month_name,
            "day": day,
            "weekday": weekday,
            "season": season,
            "formatted": formatted,
            "full_date": f"{formatted} ({season})"
        }
        
        # Add event if configured
        if self._show_events:
            event = self._get_current_event(month, day)
            if event:
                result["current_event"] = event
                result["full_date"] += f" - {event}"
        
        # Add moon phases if configured
        if self._show_moons:
            result["white_lady_phase"] = white_lady_phase
            result["blue_child_phase"] = blue_child_phase
            result["moons"] = f"White Lady: {white_lady_phase}, Blue Child: {blue_child_phase}"
        
        # Add Dragon Aspect if configured
        if self._show_dragon_aspect:
            aspect_name, aspect_domain = self._get_dragon_aspect_blessing(day_of_year)
            result["dragon_aspect"] = aspect_name
            result["aspect_domain"] = aspect_domain
            result["blessing"] = f"Blessed by {aspect_name}, Aspect of {aspect_domain}"
        
        # Add faction-specific greeting
        faction_greetings = {
            "Alliance": "For the Alliance!",
            "Horde": "For the Horde!",
            "Neutral": "Safe travels, adventurer"
        }
        result["greeting"] = faction_greetings.get(self._faction, "Safe travels")
        
        return result
    
    def update(self) -> None:
        """Update the sensor."""
        # Ensure options are loaded (in case async_added_to_hass hasn't run yet)
        if not self._options_loaded:
            self._load_options()
        
        now = datetime.now()
        self._warcraft_date = self._calculate_warcraft_date(now)
        
        # Set state to formatted Warcraft date
        self._state = self._warcraft_date["formatted"]
        
        _LOGGER.debug(f"Updated Warcraft Calendar to {self._state}")