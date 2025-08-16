"""Tamriel Calendar (Elder Scrolls) implementation - Version 2.5."""
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

# Update interval in seconds (1 hour - dates change slowly in Tamriel)
UPDATE_INTERVAL = 3600

# Complete calendar information for auto-discovery
CALENDAR_INFO = {
    "id": "tamriel",
    "version": "2.5.0",
    "icon": "mdi:sword-cross",
    "category": "fantasy",
    "accuracy": "fictional",
    "update_interval": UPDATE_INTERVAL,
    
    # Multi-language names
    "name": {
        "en": "Tamriel Calendar",
        "de": "Tamriel-Kalender",
        "es": "Calendario de Tamriel",
        "fr": "Calendrier de Tamriel",
        "it": "Calendario di Tamriel",
        "nl": "Tamriel Kalender",
        "pt": "Calendário de Tamriel",
        "ru": "Календарь Тамриэля",
        "ja": "タムリエル暦",
        "zh": "泰姆瑞尔历",
        "ko": "탐리엘 달력"
    },
    
    # Short descriptions for UI
    "description": {
        "en": "Elder Scrolls calendar with two moons, birthsigns, and Daedric summoning days (e.g. 4E 225, Morning Star 16)",
        "de": "Elder Scrolls Kalender mit zwei Monden, Geburtszeichen und Daedrischen Beschwörungstagen (z.B. 4E 225, Morning Star 16)",
        "es": "Calendario de Elder Scrolls con dos lunas, signos de nacimiento y días de invocación daédrica",
        "fr": "Calendrier Elder Scrolls avec deux lunes, signes de naissance et jours d'invocation daedrique",
        "it": "Calendario di Elder Scrolls con due lune, segni zodiacali e giorni di evocazione daedrica",
        "nl": "Elder Scrolls kalender met twee manen, geboortetekens en Daedrische oproepingsdagen",
        "pt": "Calendário Elder Scrolls com duas luas, signos de nascimento e dias de invocação daédrica",
        "ru": "Календарь Elder Scrolls с двумя лунами, знаками рождения и днями призыва даэдра",
        "ja": "2つの月、誕生の星座、デイドラ召喚日を持つエルダースクロールズの暦",
        "zh": "上古卷轴日历，包含双月、诞生星座和魔神召唤日",
        "ko": "두 개의 달, 탄생 별자리, 데이드라 소환일이 있는 엘더스크롤 달력"
    },
    
    # Detailed information for documentation
    "detailed_info": {
        "en": {
            "overview": "The Tamrielic calendar is used throughout the continent of Tamriel in The Elder Scrolls universe",
            "structure": "12 months with varying days (28-31), 7-day weeks from Morndas to Sundas",
            "eras": "Currently in the Fourth Era (4E) following the Oblivion Crisis",
            "moons": "Two moons: Masser (24-day cycle) and Secunda (32-day cycle), important for Khajiit births",
            "birthsigns": "13 constellations determine character traits: The Warrior, The Mage, The Thief, and their charges",
            "daedric": "Specific days are sacred to the 16 Daedric Princes for summoning rituals",
            "holidays": "Numerous festivals throughout the year, from New Life Festival to Saturalia",
            "note": "Based on Skyrim's timeline where 4E 201 = Earth year 2011"
        },
        "de": {
            "overview": "Der tamrielische Kalender wird auf dem gesamten Kontinent Tamriel im Elder Scrolls Universum verwendet",
            "structure": "12 Monate mit unterschiedlichen Tagen (28-31), 7-Tage-Wochen von Morndas bis Sundas",
            "eras": "Aktuell in der Vierten Ära (4Ä) nach der Oblivion-Krise",
            "moons": "Zwei Monde: Masser (24-Tage-Zyklus) und Secunda (32-Tage-Zyklus), wichtig für Khajiit-Geburten",
            "birthsigns": "13 Sternbilder bestimmen Charaktereigenschaften: Der Krieger, Der Magier, Der Dieb und ihre Schützlinge",
            "daedric": "Bestimmte Tage sind den 16 Daedrischen Prinzen für Beschwörungsrituale heilig",
            "holidays": "Zahlreiche Feste im Jahr, vom Neujahrsfest bis Saturalia",
            "note": "Basierend auf Skyrims Zeitlinie, wo 4Ä 201 = Erdjahr 2011"
        }
    },
    
    # Tamriel-specific information
    "tamriel_data": {
        "months": [
            {"name": "Morning Star", "days": 31, "earth": "January"},
            {"name": "Sun's Dawn", "days": 28, "earth": "February"},
            {"name": "First Seed", "days": 31, "earth": "March"},
            {"name": "Rain's Hand", "days": 30, "earth": "April"},
            {"name": "Second Seed", "days": 31, "earth": "May"},
            {"name": "Mid Year", "days": 30, "earth": "June"},
            {"name": "Sun's Height", "days": 31, "earth": "July"},
            {"name": "Last Seed", "days": 31, "earth": "August"},
            {"name": "Hearthfire", "days": 30, "earth": "September"},
            {"name": "Frostfall", "days": 31, "earth": "October"},
            {"name": "Sun's Dusk", "days": 30, "earth": "November"},
            {"name": "Evening Star", "days": 31, "earth": "December"}
        ],
        "weekdays": [
            "Morndas", "Tirdas", "Middas", "Turdas", 
            "Fredas", "Loredas", "Sundas"
        ],
        "birthsigns": [
            "The Ritual", "The Lover", "The Lord", "The Mage",
            "The Shadow", "The Steed", "The Apprentice", "The Warrior",
            "The Lady", "The Tower", "The Atronach", "The Thief"
        ],
        "divines": [
            "Akatosh", "Arkay", "Dibella", "Julianos",
            "Kynareth", "Mara", "Stendarr", "Talos", "Zenithar"
        ]
    },
    
    # Additional metadata
    "reference_url": "https://en.uesp.net/wiki/Lore:Calendar",
    "documentation_url": "https://github.com/yourusername/alternative_time/wiki/Tamriel-Calendar",
    "origin": "The Elder Scrolls series by Bethesda Game Studios",
    "created_by": "Bethesda Game Studios",
    
    # Example format
    "example": "4E 201, Last Seed 17 (Tirdas)",
    "example_meaning": "Fourth Era year 201, 17th day of Last Seed, Tirdas (Tuesday)",
    
    # Related calendars
    "related": ["shire", "rivendell", "discworld"],
    
    # Tags for searching and filtering
    "tags": [
        "fantasy", "elder_scrolls", "skyrim", "tamriel", "gaming",
        "rpg", "bethesda", "tes", "oblivion", "morrowind", "eso",
        "fourth_era", "daedric", "aedric", "khajiit", "argonian"
    ],
    
    # Special features
    "features": {
        "supports_eras": True,
        "supports_moons": True,
        "supports_birthsigns": True,
        "supports_holidays": True,
        "supports_divine_blessings": True,
        "supports_daedric_days": True,
        "precision": "day"
    },
    
    # Configuration options for this calendar
    "config_options": {
        "show_moons": {
            "type": "boolean",
            "default": True,
            "description": {
                "en": "Show Masser and Secunda moon phases",
                "de": "Zeige Masser und Secunda Mondphasen"
            }
        },
        "show_holidays": {
            "type": "boolean",
            "default": True,
            "description": {
                "en": "Show Tamrielic holidays and festivals",
                "de": "Zeige tamrielische Feiertage und Feste"
            }
        },
        "era_start": {
            "type": "select",
            "default": "4E",
            "options": ["1E", "2E", "3E", "4E", "5E"],
            "description": {
                "en": "Select the era to display",
                "de": "Wähle die anzuzeigende Ära"
            }
        }
    }
}


class TamrielCalendarSensor(AlternativeTimeSensorBase):
    """Sensor for displaying Tamrielic Calendar from Elder Scrolls."""
    
    # Class-level update interval
    UPDATE_INTERVAL = 3600  # Update every hour
    
    def __init__(self, base_name: str, hass: HomeAssistant) -> None:
        """Initialize the Tamriel calendar sensor."""
        super().__init__(base_name, hass)
        
        # Get translated name from metadata
        calendar_name = self._translate('name', 'Tamriel Calendar')
        
        # Set sensor attributes
        self._attr_name = f"{base_name} {calendar_name}"
        self._attr_unique_id = f"{base_name}_tamriel_calendar"
        self._attr_icon = CALENDAR_INFO.get("icon", "mdi:sword-cross")
        
        # Get configuration options
        self._show_moons = True  # Could be from config
        self._show_holidays = True  # Could be from config
        self._era = "4E"  # Fourth Era
        
        # Tamriel data
        self._tamriel_data = CALENDAR_INFO["tamriel_data"]
        
        _LOGGER.debug(f"Initialized Tamriel Calendar sensor: {self._attr_name}")
    
    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes."""
        attrs = super().extra_state_attributes
        
        # Add Tamriel-specific attributes
        if hasattr(self, '_tamriel_date'):
            attrs.update(self._tamriel_date)
            
            # Add description in user's language
            attrs["description"] = self._translate('description')
            
            # Add calendar reference
            attrs["reference"] = CALENDAR_INFO.get('reference_url', '')
        
        return attrs
    
    def _calculate_tamriel_date(self, earth_date: datetime) -> Dict[str, Any]:
        """Calculate Tamrielic date from Earth date."""
        
        # Tamriel months data
        tamriel_months = self._tamriel_data["months"]
        tamriel_weekdays = self._tamriel_data["weekdays"]
        birthsigns = self._tamriel_data["birthsigns"]
        divines = self._tamriel_data["divines"]
        
        # Calculate Tamrielic Era and Year
        # 4E 201 is when Skyrim takes place (2011 Earth year)
        years_since_2011 = earth_date.year - 2011
        tamriel_year = 201 + years_since_2011
        
        # Determine Era
        if self._era == "4E" and tamriel_year > 433:
            # After 4E 433, could transition to 5E
            era = "5E"
            era_name = "Fifth Era"
            display_year = tamriel_year - 433
        else:
            era = self._era
            era_name = f"{self._era[0]}{'st' if self._era[0] == '1' else 'nd' if self._era[0] == '2' else 'rd' if self._era[0] == '3' else 'th'} Era"
            display_year = tamriel_year
        
        # Get month and day
        month_index = earth_date.month - 1
        tamriel_month = tamriel_months[month_index]["name"]
        tamriel_day = earth_date.day
        
        # Get weekday (Monday = 0 in Python, Morndas = 0 in Tamriel)
        weekday_index = earth_date.weekday()
        tamriel_weekday = tamriel_weekdays[weekday_index]
        
        # Get birthsign
        birthsign = birthsigns[month_index]
        
        # Determine season
        if earth_date.month in [12, 1, 2]:
            season = "Winter"
            season_emoji = "❄️"
        elif earth_date.month in [3, 4, 5]:
            season = "Spring"
            season_emoji = "🌸"
        elif earth_date.month in [6, 7, 8]:
            season = "Summer"
            season_emoji = "☀️"
        else:
            season = "Autumn"
            season_emoji = "🍂"
        
        # Check for Tamrielic holidays
        holiday = self._get_tamriel_holiday(earth_date.month, earth_date.day)
        
        # Divine blessing (cycles through the Nine Divines)
        divine_index = (earth_date.day - 1) % 9
        divine_blessing = divines[divine_index]
        
        # Daedric Prince summon days
        daedric_prince = self._get_daedric_summoning_day(earth_date.month, earth_date.day)
        
        # Calculate moon phases if enabled
        moon_data = {}
        if self._show_moons:
            # Masser (larger moon) - 24 day cycle
            masser_phase = self._get_moon_phase(earth_date.day % 24, 24, "Masser")
            
            # Secunda (smaller moon) - 32 day cycle
            secunda_phase = self._get_moon_phase(earth_date.day % 32, 32, "Secunda")
            
            moon_data = {
                "moon_phase_masser": masser_phase,
                "moon_phase_secunda": secunda_phase,
                "khajiit_form": self._get_khajiit_form(masser_phase, secunda_phase)
            }
        
        # Time period descriptions
        hour = earth_date.hour
        if 5 <= hour < 8:
            time_period = "Dawn"
            time_emoji = "🌅"
        elif 8 <= hour < 12:
            time_period = "Morning"
            time_emoji = "🌤️"
        elif 12 <= hour < 17:
            time_period = "Afternoon"
            time_emoji = "☀️"
        elif 17 <= hour < 20:
            time_period = "Dusk"
            time_emoji = "🌆"
        elif 20 <= hour < 24:
            time_period = "Night"
            time_emoji = "🌙"
        else:
            time_period = "Witching Hour"
            time_emoji = "⭐"
        
        # Guild activities by day
        guild_days = {
            "Morndas": "Mages Guild studies",
            "Tirdas": "Fighters Guild training",
            "Middas": "Merchants' market day",
            "Turdas": "Thieves Guild planning",
            "Fredas": "Temple prayers",
            "Loredas": "Dark Brotherhood contracts",
            "Sundas": "Day of rest and worship"
        }
        guild_day = guild_days.get(tamriel_weekday, "")
        
        result = {
            "era": era,
            "era_name": era_name,
            "year": display_year,
            "month": tamriel_month,
            "day": tamriel_day,
            "weekday": tamriel_weekday,
            "birthsign": birthsign,
            "season": f"{season_emoji} {season}",
            "divine_blessing": f"⚜️ {divine_blessing}",
            "guild_activity": guild_day,
            "time_period": f"{time_emoji} {time_period}",
            "full_date": f"{era} {display_year}, {tamriel_month} {tamriel_day} ({tamriel_weekday})",
        }
        
        # Add optional data
        if holiday and self._show_holidays:
            result["holiday"] = holiday
        
        if daedric_prince:
            result["daedric_prince"] = daedric_prince
        
        if moon_data:
            result.update(moon_data)
        
        return result
    
    def _get_tamriel_holiday(self, month: int, day: int) -> str:
        """Get Tamrielic holiday for given date."""
        holidays = {
            (1, 1): "🎊 New Life Festival",
            (1, 15): "🏔️ South Wind's Prayer",
            (1, 16): "📚 Day of Lights",
            (2, 5): "⚔️ Othroktide",
            (2, 16): "💕 Heart's Day",
            (3, 7): "🌱 First Planting",
            (3, 21): "🏛️ Hogithum",
            (4, 1): "🤡 Jester's Day",
            (4, 28): "🌸 Day of Shame",
            (5, 7): "🌾 Second Planting",
            (5, 30): "🔥 Fire Festival",
            (6, 16): "🏪 Mid Year Celebration",
            (6, 24): "⚡ Tibedetha",
            (7, 10): "🛍️ Merchants' Festival",
            (7, 12): "🗡️ Divad Etep't",
            (8, 21): "🍃 Harvest's End",
            (9, 8): "⚒️ Tales and Tallows",
            (10, 13): "👻 Witches' Festival",
            (10, 30): "🦴 Old Life Festival",
            (11, 18): "🛡️ Warriors' Festival",
            (11, 20): "🐺 Moon Festival",
            (12, 15): "🌟 North Wind's Prayer",
            (12, 31): "🎭 Saturalia"
        }
        return holidays.get((month, day), "")
    
    def _get_daedric_summoning_day(self, month: int, day: int) -> str:
        """Get Daedric Prince summoning day."""
        daedric_days = {
            (1, 1): "🌙 Sheogorath",
            (1, 13): "⚔️ Mehrunes Dagon",
            (2, 13): "🍷 Sanguine",
            (3, 5): "📖 Hermaeus Mora",
            (3, 21): "🌑 Namira",
            (4, 9): "🦌 Hircine",
            (5, 9): "💎 Clavicus Vile",
            (6, 5): "🕸️ Peryite",
            (7, 10): "☠️ Vaermina",
            (8, 8): "🔮 Azura",
            (9, 19): "⚖️ Meridia",
            (10, 13): "🔥 Boethiah",
            (11, 8): "🗿 Malacath",
            (11, 20): "🕷️ Mephala",
            (12, 20): "🌑 Nocturnal",
            (12, 31): "⚔️ Molag Bal"
        }
        return daedric_days.get((month, day), "")
    
    def _get_moon_phase(self, day_in_cycle: int, cycle_length: int, moon_name: str) -> str:
        """Calculate moon phase with emoji."""
        phase_portion = day_in_cycle / cycle_length
        
        if phase_portion < 0.125:
            return f"🌑 {moon_name}: New"
        elif phase_portion < 0.25:
            return f"🌒 {moon_name}: Waxing Crescent"
        elif phase_portion < 0.375:
            return f"🌓 {moon_name}: First Quarter"
        elif phase_portion < 0.5:
            return f"🌔 {moon_name}: Waxing Gibbous"
        elif phase_portion < 0.625:
            return f"🌕 {moon_name}: Full"
        elif phase_portion < 0.75:
            return f"🌖 {moon_name}: Waning Gibbous"
        elif phase_portion < 0.875:
            return f"🌗 {moon_name}: Last Quarter"
        else:
            return f"🌘 {moon_name}: Waning Crescent"
    
    def _get_khajiit_form(self, masser: str, secunda: str) -> str:
        """Determine Khajiit form based on moon phases (simplified)."""
        if "Full" in masser and "Full" in secunda:
            return "🐯 Senche (Large quadruped)"
        elif "Full" in masser and "New" in secunda:
            return "🐆 Pahmar (Large quadruped)"
        elif "New" in masser and "Full" in secunda:
            return "🐈 Alfiq (Housecat)"
        elif "New" in masser and "New" in secunda:
            return "🧝 Ohmes (Elven appearance)"
        else:
            return "🐱 Cathay (Humanoid)"

    def update(self) -> None:
        """Update the sensor."""
        now = datetime.now()
        self._tamriel_date = self._calculate_tamriel_date(now)
        
        # Format: Era Year, Month Day (Weekday)
        # Example: "4E 225, Morning Star 16 (Tirdas)"
        self._state = self._tamriel_date["full_date"]
        
        _LOGGER.debug(f"Updated Tamriel calendar to {self._state}")