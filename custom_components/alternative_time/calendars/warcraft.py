"""World of Warcraft Azeroth Calendar implementation - Version 2.5."""
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

# Update interval in seconds (3600 seconds = 1 hour)
UPDATE_INTERVAL = 3600

# Complete calendar information for auto-discovery
CALENDAR_INFO = {
    "id": "warcraft",
    "version": "2.5.0",
    "icon": "mdi:sword",
    "category": "fantasy",
    "accuracy": "fictional",
    "update_interval": UPDATE_INTERVAL,
    
    # Multi-language names
    "name": {
        "en": "World of Warcraft Calendar",
        "de": "World of Warcraft Kalender",
        "es": "Calendario de World of Warcraft",
        "fr": "Calendrier de World of Warcraft",
        "it": "Calendario di World of Warcraft",
        "nl": "World of Warcraft Kalender",
        "pt": "Calendário de World of Warcraft",
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
        "ja": "季節イベントと月相を含むアゼロスの暦",
        "zh": "艾泽拉斯日历，包含季节活动和月相",
        "ko": "계절 이벤트와 달의 위상이 있는 아제로스 달력"
    },
    
    # Detailed information for documentation
    "detailed_info": {
        "en": {
            "overview": "The calendar of Azeroth from World of Warcraft, tracking time across the world",
            "structure": "12 months following real-world calendar with in-game seasonal events",
            "timeline": "Currently Year 35 after the Dark Portal opened (canon timeline)",
            "events": "Major seasonal events like Brewfest, Winter Veil, Hallow's End",
            "moons": "Two moons - White Lady and Blue Child with different phases",
            "regions": "Time varies between Eastern Kingdoms, Kalimdor, Northrend, and Pandaria",
            "factions": "Alliance and Horde observe different holidays",
            "magic": "Temporal anomalies due to Bronze Dragonflight activities"
        },
        "de": {
            "overview": "Der Kalender von Azeroth aus World of Warcraft, verfolgt die Zeit in der Welt",
            "structure": "12 Monate nach realem Kalender mit Ingame-Events",
            "timeline": "Aktuell Jahr 35 nach Öffnung des Dunklen Portals (Kanon-Zeitlinie)",
            "events": "Große saisonale Events wie Braufest, Winterhauch, Schlotternächte",
            "moons": "Zwei Monde - Weiße Lady und Blaues Kind mit verschiedenen Phasen",
            "regions": "Zeit variiert zwischen Östlichen Königreichen, Kalimdor, Nordend und Pandaria",
            "factions": "Allianz und Horde feiern verschiedene Feiertage",
            "magic": "Zeitanomalien durch Aktivitäten des Bronzenen Drachenschwarms"
        }
    },
    
    # Warcraft-specific data
    "warcraft_data": {
        # Azeroth months (similar to Earth but with fantasy names)
        "months": [
            {"num": 1, "name": "Deepwood", "season": "Winter", "emoji": "❄️"},
            {"num": 2, "name": "Snowdown", "season": "Winter", "emoji": "⛄"},
            {"num": 3, "name": "Thawing", "season": "Spring", "emoji": "🌱"},
            {"num": 4, "name": "Blooming", "season": "Spring", "emoji": "🌸"},
            {"num": 5, "name": "Growing", "season": "Spring", "emoji": "🌿"},
            {"num": 6, "name": "Brightleaf", "season": "Summer", "emoji": "☀️"},
            {"num": 7, "name": "Highsun", "season": "Summer", "emoji": "🌞"},
            {"num": 8, "name": "Harvest", "season": "Summer", "emoji": "🌾"},
            {"num": 9, "name": "Brewtime", "season": "Autumn", "emoji": "🍺"},
            {"num": 10, "name": "Harvestfall", "season": "Autumn", "emoji": "🍂"},
            {"num": 11, "name": "Twilight", "season": "Autumn", "emoji": "🌆"},
            {"num": 12, "name": "Starfall", "season": "Winter", "emoji": "⭐"}
        ],
        
        # Days of the week in Azeroth
        "weekdays": [
            {"name": "Day of the Sun", "abbr": "Sun", "element": "Light"},
            {"name": "Day of the Moon", "abbr": "Moon", "element": "Shadow"},
            {"name": "Day of the Earth", "abbr": "Earth", "element": "Earth"},
            {"name": "Day of the Wind", "abbr": "Wind", "element": "Air"},
            {"name": "Day of the Tides", "abbr": "Tide", "element": "Water"},
            {"name": "Day of the Flame", "abbr": "Flame", "element": "Fire"},
            {"name": "Day of the Wisp", "abbr": "Wisp", "element": "Spirit"}
        ],
        
        # Major seasonal events (mapped to real dates)
        "events": {
            (1, 1): {"name": "New Year", "faction": "Both", "emoji": "🎊"},
            (1, 25): {"name": "Lunar Festival", "faction": "Both", "emoji": "🏮"},
            (2, 14): {"name": "Love is in the Air", "faction": "Both", "emoji": "💕"},
            (3, 17): {"name": "Noblegarden", "faction": "Both", "emoji": "🥚"},
            (5, 1): {"name": "Children's Week", "faction": "Both", "emoji": "👶"},
            (6, 21): {"name": "Midsummer Fire Festival", "faction": "Both", "emoji": "🔥"},
            (7, 4): {"name": "Fireworks Spectacular", "faction": "Both", "emoji": "🎆"},
            (8, 15): {"name": "Call of the Scarab", "faction": "Both", "emoji": "🪲"},
            (9, 20): {"name": "Brewfest", "faction": "Both", "emoji": "🍺"},
            (9, 19): {"name": "Harvest Festival", "faction": "Both", "emoji": "🌾"},
            (10, 18): {"name": "Hallow's End", "faction": "Both", "emoji": "🎃"},
            (11, 1): {"name": "Day of the Dead", "faction": "Both", "emoji": "💀"},
            (11, 21): {"name": "Pilgrim's Bounty", "faction": "Both", "emoji": "🦃"},
            (12, 15): {"name": "Feast of Winter Veil", "faction": "Both", "emoji": "🎄"}
        },
        
        # Moon phases (two moons)
        "moons": {
            "white_lady": {
                "name": "White Lady",
                "cycle_days": 28,
                "phases": ["🌑 New", "🌒 Waxing Crescent", "🌓 First Quarter", "🌔 Waxing Gibbous",
                          "🌕 Full", "🌖 Waning Gibbous", "🌗 Last Quarter", "🌘 Waning Crescent"]
            },
            "blue_child": {
                "name": "Blue Child",
                "cycle_days": 35,
                "phases": ["🔵 Hidden", "🔵 Rising", "🔵 Peak", "🔵 Setting"]
            }
        },
        
        # Regions and their time differences
        "regions": {
            "Eastern Kingdoms": {"offset": 0, "capital": "Stormwind", "faction": "Alliance"},
            "Kalimdor": {"offset": -3, "capital": "Orgrimmar", "faction": "Horde"},
            "Northrend": {"offset": 2, "capital": "Dalaran", "faction": "Neutral"},
            "Pandaria": {"offset": -5, "capital": "Shrine", "faction": "Neutral"},
            "Broken Isles": {"offset": 1, "capital": "Dalaran", "faction": "Neutral"},
            "Shadowlands": {"offset": 0, "capital": "Oribos", "faction": "Neutral"}
        },
        
        # Time periods
        "time_periods": [
            {"name": "Dawn", "hours": (5, 8), "emoji": "🌅", "activity": "Daily quests reset"},
            {"name": "Morning", "hours": (8, 12), "emoji": "☀️", "activity": "Peak trading"},
            {"name": "Noon", "hours": (12, 14), "emoji": "🌞", "activity": "PvP battles"},
            {"name": "Afternoon", "hours": (14, 17), "emoji": "🌤️", "activity": "Dungeon runs"},
            {"name": "Dusk", "hours": (17, 20), "emoji": "🌇", "activity": "Guild events"},
            {"name": "Evening", "hours": (20, 23), "emoji": "🌃", "activity": "Raid time"},
            {"name": "Night", "hours": (23, 5), "emoji": "🌙", "activity": "Rare spawns"}
        ],
        
        # Faction-specific details
        "factions": {
            "Alliance": {"greeting": "For the Alliance!", "color": "Blue", "emoji": "🦁"},
            "Horde": {"greeting": "For the Horde!", "color": "Red", "emoji": "⚔️"},
            "Neutral": {"greeting": "Balance in all things", "color": "Green", "emoji": "☯️"}
        },
        
        # Dragon Aspects (for flavor)
        "dragon_aspects": [
            {"name": "Alexstrasza", "domain": "Life", "day": 1},
            {"name": "Ysera", "domain": "Dreams", "day": 2},
            {"name": "Nozdormu", "domain": "Time", "day": 3},
            {"name": "Malygos", "domain": "Magic", "day": 4},
            {"name": "Neltharion", "domain": "Earth", "day": 5}
        ],
        
        # Current year in Azeroth timeline
        "current_year": 35,  # Year 35 after the Dark Portal
        "year_name": "Year of the Phoenix"
    },
    
    # Additional metadata
    "reference_url": "https://wowpedia.fandom.com/wiki/Calendar",
    "documentation_url": "https://worldofwarcraft.com/en-us/story/timeline",
    "origin": "World of Warcraft",
    "created_by": "Blizzard Entertainment",
    "introduced": "World of Warcraft (2004)",
    
    # Example format
    "example": "Year 35, Day of the Wisp, 15th of Brewtime | 🍺 Brewfest | White Lady: 🌕 Full",
    "example_meaning": "Year 35 after Dark Portal, Day of the Wisp, 15th of Brewtime month, during Brewfest, White Lady moon is full",
    
    # Related calendars
    "related": ["tamriel", "shire", "discworld"],
    
    # Tags for searching and filtering
    "tags": [
        "fantasy", "warcraft", "wow", "azeroth", "blizzard",
        "mmorpg", "alliance", "horde", "gaming"
    ],
    
    # Special features
    "features": {
        "dual_moons": True,
        "seasonal_events": True,
        "faction_specific": True,
        "regional_time": True,
        "dragon_aspects": True,
        "precision": "day"
    },
    
    # Configuration options for this calendar
    "config_options": {
        "faction": {
            "type": "select",
            "default": "Neutral",
            "options": ["Alliance", "Horde", "Neutral"],
            "description": {
                "en": "Your faction allegiance",
                "de": "Deine Fraktionszugehörigkeit"
            }
        },
        "region": {
            "type": "select",
            "default": "Eastern Kingdoms",
            "options": ["Eastern Kingdoms", "Kalimdor", "Northrend", "Pandaria", "Broken Isles", "Shadowlands"],
            "description": {
                "en": "Current region for time reference",
                "de": "Aktuelle Region für Zeitreferenz"
            }
        },
        "show_events": {
            "type": "boolean",
            "default": True,
            "description": {
                "en": "Show seasonal events",
                "de": "Saisonale Events anzeigen"
            }
        },
        "show_moons": {
            "type": "boolean",
            "default": True,
            "description": {
                "en": "Show moon phases",
                "de": "Mondphasen anzeigen"
            }
        },
        "show_dragon_aspect": {
            "type": "boolean",
            "default": True,
            "description": {
                "en": "Show dragon aspect of the day",
                "de": "Drachenaspekt des Tages anzeigen"
            }
        }
    }
}


class WarcraftCalendarSensor(AlternativeTimeSensorBase):
    """Sensor for displaying World of Warcraft Azeroth Calendar."""
    
    # Class-level update interval
    UPDATE_INTERVAL = 3600  # Update every hour
    
    def __init__(self, base_name: str, hass: HomeAssistant) -> None:
        """Initialize the Warcraft calendar sensor."""
        super().__init__(base_name, hass)
        
        # Get translated name from metadata
        calendar_name = self._translate('name', 'World of Warcraft Calendar')
        
        # Set sensor attributes
        self._attr_name = f"{base_name} {calendar_name}"
        self._attr_unique_id = f"{base_name}_warcraft"
        self._attr_icon = CALENDAR_INFO.get("icon", "mdi:sword")
        
        # Configuration options
        self._faction = "Neutral"
        self._region = "Eastern Kingdoms"
        self._show_events = True
        self._show_moons = True
        self._show_dragon_aspect = True
        
        # Warcraft data
        self._warcraft_data = CALENDAR_INFO["warcraft_data"]
        
        _LOGGER.debug(f"Initialized Warcraft Calendar sensor: {self._attr_name}")
    
    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes."""
        attrs = super().extra_state_attributes
        
        # Ensure attrs is a dictionary
        if attrs is None:
            attrs = {}
        
        # Add Warcraft-specific attributes
        if hasattr(self, '_warcraft_date'):
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
        phase_index = int((cycle_position / moon_data["cycle_days"]) * len(moon_data["phases"]))
        if phase_index >= len(moon_data["phases"]):
            phase_index = len(moon_data["phases"]) - 1
        return moon_data["phases"][phase_index]
    
    def _get_dragon_aspect(self, day: int) -> Dict[str, str]:
        """Get dragon aspect for the day."""
        aspects = self._warcraft_data["dragon_aspects"]
        aspect_index = (day - 1) % len(aspects)
        return aspects[aspect_index]
    
    def _calculate_warcraft_date(self, earth_date: datetime) -> Dict[str, Any]:
        """Calculate Warcraft calendar date from Earth date."""
        
        # Current year in Azeroth (Year 35 after Dark Portal)
        azeroth_year = self._warcraft_data["current_year"]
        year_name = self._warcraft_data["year_name"]
        
        # Get month and day (following Earth calendar)
        month_data = self._warcraft_data["months"][earth_date.month - 1]
        day = earth_date.day
        
        # Get weekday
        weekday_index = earth_date.weekday()
        if weekday_index == 6:  # Sunday
            weekday_index = 0
        else:
            weekday_index += 1
        weekday_data = self._warcraft_data["weekdays"][weekday_index]
        
        # Check for events
        event_data = self._warcraft_data["events"].get((earth_date.month, earth_date.day))
        event = ""
        if event_data and self._show_events:
            # Check if event is faction-specific
            if event_data["faction"] in ["Both", self._faction]:
                event = f"{event_data['emoji']} {event_data['name']}"
        
        # Calculate moon phases
        days_since_epoch = (earth_date - datetime(2000, 1, 1)).days
        white_lady_phase = ""
        blue_child_phase = ""
        
        if self._show_moons:
            white_lady_phase = self._calculate_moon_phase(
                days_since_epoch, 
                self._warcraft_data["moons"]["white_lady"]
            )
            blue_child_phase = self._calculate_moon_phase(
                days_since_epoch,
                self._warcraft_data["moons"]["blue_child"]
            )
        
        # Get time period
        hour = earth_date.hour
        time_period = None
        for period in self._warcraft_data["time_periods"]:
            start, end = period["hours"]
            if start <= hour < end or (start > end and (hour >= start or hour < end)):
                time_period = period
                break
        
        # Get region info
        region_data = self._warcraft_data["regions"].get(self._region, {})
        region_capital = region_data.get("capital", "Unknown")
        region_faction = region_data.get("faction", "Neutral")
        
        # Get faction info
        faction_data = self._warcraft_data["factions"].get(self._faction, {})
        faction_greeting = faction_data.get("greeting", "")
        faction_emoji = faction_data.get("emoji", "")
        
        # Get dragon aspect
        dragon_aspect = None
        if self._show_dragon_aspect:
            dragon_aspect = self._get_dragon_aspect(day)
        
        # Build date string
        date_parts = [
            f"Year {azeroth_year}",
            weekday_data["name"],
            f"{day}{'st' if day == 1 else 'nd' if day == 2 else 'rd' if day == 3 else 'th'} of {month_data['name']}"
        ]
        
        # Add event if present
        if event:
            date_parts.append(event)
        
        # Add moon phases
        if self._show_moons:
            date_parts.append(f"White Lady: {white_lady_phase}")
            if earth_date.day % 7 == 0:  # Blue Child visible every 7 days
                date_parts.append(f"Blue Child: {blue_child_phase}")
        
        # Add time period
        if time_period:
            date_parts.append(f"{time_period['emoji']} {time_period['name']}")
        
        full_display = " | ".join(date_parts)
        
        result = {
            "year": azeroth_year,
            "year_name": year_name,
            "month": earth_date.month,
            "month_name": month_data["name"],
            "season": month_data["season"],
            "season_emoji": month_data["emoji"],
            "day": day,
            "weekday": weekday_data["name"],
            "weekday_abbr": weekday_data["abbr"],
            "element": weekday_data["element"],
            "event": event,
            "white_lady_phase": white_lady_phase,
            "blue_child_phase": blue_child_phase,
            "time_period": time_period["name"] if time_period else "",
            "time_activity": time_period["activity"] if time_period else "",
            "region": self._region,
            "region_capital": region_capital,
            "region_faction": region_faction,
            "faction_greeting": faction_greeting,
            "faction_emoji": faction_emoji,
            "gregorian_date": earth_date.strftime("%Y-%m-%d"),
            "time": earth_date.strftime("%H:%M:%S"),
            "full_display": full_display
        }
        
        # Add dragon aspect if enabled
        if dragon_aspect:
            result["dragon_aspect"] = dragon_aspect["name"]
            result["dragon_domain"] = dragon_aspect["domain"]
            result["dragon_message"] = f"Under the protection of {dragon_aspect['name']}, Aspect of {dragon_aspect['domain']}"
        
        # Add special messages based on time
        if time_period:
            if time_period["name"] == "Dawn":
                result["special_message"] = "Daily quests have reset!"
            elif time_period["name"] == "Evening":
                result["special_message"] = "Raid time! Gather your guild!"
            elif time_period["name"] == "Night":
                result["special_message"] = "Rare spawns may appear..."
        
        # Add faction war cry
        if self._faction != "Neutral":
            result["war_cry"] = faction_greeting
        
        return result
    
    def update(self) -> None:
        """Update the sensor."""
        now = datetime.now()
        self._warcraft_date = self._calculate_warcraft_date(now)
        
        # Set state to formatted date
        self._state = self._warcraft_date["full_display"]
        
        _LOGGER.debug(f"Updated Warcraft Calendar to {self._state}")