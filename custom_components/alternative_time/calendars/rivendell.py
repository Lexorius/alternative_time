"""Rivendell Calendar (Elven/Imladris) implementation - Version 2.5."""
from __future__ import annotations

from datetime import datetime
import logging
import math
from typing import Dict, Any

from homeassistant.core import HomeAssistant
from ..sensor import AlternativeTimeSensorBase

_LOGGER = logging.getLogger(__name__)

# ============================================
# CALENDAR METADATA
# ============================================

# Update interval in seconds (1 hour - elven time flows differently)
UPDATE_INTERVAL = 3600

# Complete calendar information for auto-discovery
CALENDAR_INFO = {
    "id": "rivendell",
    "version": "2.5.0",
    "icon": "mdi:forest",
    "category": "fantasy",
    "accuracy": "fictional",
    "update_interval": UPDATE_INTERVAL,
    
    # Multi-language names
    "name": {
        "en": "Rivendell Calendar",
        "de": "Bruchtal-Kalender",
        "es": "Calendario de Rivendel",
        "fr": "Calendrier de Fondcombe",
        "it": "Calendario di Gran Burrone",
        "nl": "Rivendel Kalender",
        "pt": "Calendário de Valfenda",
        "ru": "Календарь Ривенделла",
        "ja": "裂け谷の暦",
        "zh": "瑞文戴尔历",
        "ko": "리븐델 달력",
        "sindarin": "Aes Imladris",
        "quenya": "Aras Arcimbele"
    },
    
    # Short descriptions for UI
    "description": {
        "en": "Elven calendar with Quenya names, 6 seasons, and yén cycles (e.g. F.A. 24, Tuilë 35)",
        "de": "Elbischer Kalender mit Quenya-Namen, 6 Jahreszeiten und Yén-Zyklen (z.B. F.A. 24, Tuilë 35)",
        "es": "Calendario élfico con nombres Quenya, 6 estaciones y ciclos yén (ej. C.E. 24, Tuilë 35)",
        "fr": "Calendrier elfique avec noms Quenya, 6 saisons et cycles yén (ex. Q.Â. 24, Tuilë 35)",
        "it": "Calendario elfico con nomi Quenya, 6 stagioni e cicli yén (es. Q.E. 24, Tuilë 35)",
        "nl": "Elfenkalender met Quenya namen, 6 seizoenen en yén cycli (bijv. V.E. 24, Tuilë 35)",
        "pt": "Calendário élfico com nomes Quenya, 6 estações e ciclos yén (ex. Q.E. 24, Tuilë 35)",
        "ru": "Эльфийский календарь с именами на Квенья, 6 сезонов и циклы йен (напр. Ч.Э. 24, Туйлэ 35)",
        "ja": "クウェンヤ語の名前、6つの季節、イェーンサイクルを持つエルフの暦（例：第四紀24年、トゥイレ35日）",
        "zh": "精灵历法，使用昆雅语名称，6个季节和长年周期（例：第四纪元24年，春季35日）",
        "ko": "퀘냐 이름, 6계절, 옌 주기가 있는 엘프 달력 (예: 제4시대 24년, 투일레 35일)"
    },
    
    # Detailed information for documentation
    "detailed_info": {
        "en": {
            "overview": "The Calendar of Imladris (Rivendell) follows the Elven reckoning of time, as kept by Elrond Half-elven",
            "structure": "The Elven year (loa) has 6 seasons of varying length, totaling 365 days (366 in leap years)",
            "seasons": "Tuilë (Spring-54d), Lairë (Summer-72d), Yávië (Autumn-54d), Quellë (Fading-72d), Hrívë (Winter-72d), Coirë (Stirring-41d)",
            "yen": "A yén (long-year) equals 144 solar years, the preferred unit for Elven lifespan measurement",
            "days": "6-day week: Elenya (Stars), Anarya (Sun), Isilya (Moon), Aldúya (Two Trees), Menelya (Heavens), Valanya (Valar)",
            "special": "Special days include Yestarë (first day), Loëndë (mid-year), and Mettarë (last day)",
            "ages": "Currently in the Fourth Age, following the departure of the Ring-bearers",
            "note": "Time in Rivendell seems to flow differently, preserved by Vilya, Elrond's Ring of Power"
        },
        "de": {
            "overview": "Der Kalender von Imladris (Bruchtal) folgt der elbischen Zeitrechnung, wie sie von Elrond Halbelb geführt wird",
            "structure": "Das Elbenjahr (loa) hat 6 Jahreszeiten unterschiedlicher Länge, insgesamt 365 Tage (366 in Schaltjahren)",
            "seasons": "Tuilë (Frühling-54T), Lairë (Sommer-72T), Yávië (Herbst-54T), Quellë (Schwinden-72T), Hrívë (Winter-72T), Coirë (Erwachen-41T)",
            "yen": "Ein Yén (Langjahr) entspricht 144 Sonnenjahren, die bevorzugte Einheit zur Messung der Elbenlebensspanne",
            "days": "6-Tage-Woche: Elenya (Sterne), Anarya (Sonne), Isilya (Mond), Aldúya (Zwei Bäume), Menelya (Himmel), Valanya (Valar)",
            "special": "Besondere Tage sind Yestarë (erster Tag), Loëndë (Mittsommer) und Mettarë (letzter Tag)",
            "ages": "Derzeit im Vierten Zeitalter, nach der Abreise der Ringträger",
            "note": "Die Zeit in Bruchtal scheint anders zu fließen, bewahrt durch Vilya, Elronds Ring der Macht"
        }
    },
    
    # Elven calendar data
    "elven_data": {
        "seasons": [
            {"quenya": "Tuilë", "sindarin": "Ethuil", "english": "Spring", "days": 54, "emoji": "🌸"},
            {"quenya": "Lairë", "sindarin": "Laer", "english": "Summer", "days": 72, "emoji": "☀️"},
            {"quenya": "Yávië", "sindarin": "Iavas", "english": "Autumn", "days": 54, "emoji": "🍂"},
            {"quenya": "Quellë", "sindarin": "Firith", "english": "Fading", "days": 72, "emoji": "🍃"},
            {"quenya": "Hrívë", "sindarin": "Rhîw", "english": "Winter", "days": 72, "emoji": "❄️"},
            {"quenya": "Coirë", "sindarin": "Echuir", "english": "Stirring", "days": 41, "emoji": "🌱"}
        ],
        "weekdays": [
            {"quenya": "Elenya", "sindarin": "Orgilion", "english": "Stars-day"},
            {"quenya": "Anarya", "sindarin": "Oranor", "english": "Sun-day"},
            {"quenya": "Isilya", "sindarin": "Orithil", "english": "Moon-day"},
            {"quenya": "Aldúya", "sindarin": "Orgaladhad", "english": "Two Trees-day"},
            {"quenya": "Menelya", "sindarin": "Ormenel", "english": "Heavens-day"},
            {"quenya": "Valanya", "sindarin": "Orbelain", "english": "Valar-day"}
        ],
        "special_days": [
            {"name": "Yestarë", "meaning": "First Day", "date": "before Spring"},
            {"name": "Loëndë", "meaning": "Mid-year's Day", "date": "between Spring and Summer"},
            {"name": "Yáviérë", "meaning": "Harvest Festival", "date": "after Autumn"},
            {"name": "Mettarë", "meaning": "Last Day", "date": "after Winter"}
        ],
        "star_signs": [
            "Menelmacar (Orion)", "Valacirca (Great Bear)", "Wilwarin (Butterfly)",
            "Telumendil (Lover of Heavens)", "Soronúmë (Eagle)", "Anarríma (Sun-border)",
            "Gil-galad (Star of Radiance)", "Elemmírë (Star-jewel)", "Helluin (Sirius)",
            "Carnil (Red Star)", "Luinil (Blue Star)", "Nénar (Water Star)"
        ],
        "time_periods": {
            "dawn": {"quenya": "Tindómë", "sindarin": "Minuial", "english": "Dawn twilight"},
            "morning": {"quenya": "Ára", "sindarin": "Aur", "english": "Morning"},
            "midday": {"quenya": "Endë", "sindarin": "Enedh", "english": "Midday"},
            "afternoon": {"quenya": "Undómë", "sindarin": "Uial", "english": "Afternoon"},
            "evening": {"quenya": "Andúnë", "sindarin": "Aduial", "english": "Evening twilight"},
            "night": {"quenya": "Lómë", "sindarin": "Fuin", "english": "Night"}
        }
    },
    
    # Additional metadata
    "reference_url": "http://tolkiengateway.net/wiki/Calendar_of_Imladris",
    "documentation_url": "https://github.com/yourusername/alternative_time/wiki/Rivendell-Calendar",
    "origin": "J.R.R. Tolkien's Middle-earth legendarium",
    "created_by": "J.R.R. Tolkien",
    
    # Example format
    "example": "F.A. 24, Tuilë 35 (Elenya)",
    "example_meaning": "Fourth Age year 24, 35th day of Spring, Stars-day",
    
    # Related calendars
    "related": ["shire", "tamriel"],
    
    # Tags for searching and filtering
    "tags": [
        "fantasy", "tolkien", "lotr", "middle_earth", "elven", "elvish",
        "rivendell", "imladris", "elrond", "quenya", "sindarin",
        "first_age", "second_age", "third_age", "fourth_age"
    ],
    
    # Special features
    "features": {
        "supports_ages": True,
        "supports_yen": True,
        "supports_seasons": True,
        "supports_special_days": True,
        "supports_star_signs": True,
        "precision": "day",
        "languages": ["quenya", "sindarin", "westron"]
    },
    
    # Configuration options
    "config_options": {
        "language_mode": {
            "type": "select",
            "default": "quenya",
            "options": ["quenya", "sindarin", "english", "mixed"],
            "description": {
                "en": "Choose the language for calendar terms",
                "de": "Wähle die Sprache für Kalenderbegriffe"
            }
        },
        "show_yen": {
            "type": "boolean",
            "default": True,
            "description": {
                "en": "Show yén (144-year cycle) count",
                "de": "Zeige Yén (144-Jahre-Zyklus) Zählung"
            }
        },
        "show_star_signs": {
            "type": "boolean",
            "default": True,
            "description": {
                "en": "Show Elven star signs and constellations",
                "de": "Zeige elbische Sternzeichen und Konstellationen"
            }
        },
        "age_reckoning": {
            "type": "select",
            "default": "fourth",
            "options": ["first", "second", "third", "fourth"],
            "description": {
                "en": "Which Age to use for reckoning",
                "de": "Welches Zeitalter zur Berechnung verwenden"
            }
        }
    }
}


class RivendellCalendarSensor(AlternativeTimeSensorBase):
    """Sensor for displaying Rivendell/Elven Calendar from Middle-earth."""
    
    # Class-level update interval
    UPDATE_INTERVAL = 3600  # Update every hour
    
    def __init__(self, base_name: str, hass: HomeAssistant) -> None:
        """Initialize the Rivendell calendar sensor."""
        super().__init__(base_name, hass)
        
        # Get translated name from metadata
        calendar_name = self._translate('name', 'Rivendell Calendar')
        
        # Set sensor attributes
        self._attr_name = f"{base_name} {calendar_name}"
        self._attr_unique_id = f"{base_name}_rivendell_calendar"
        self._attr_icon = CALENDAR_INFO.get("icon", "mdi:forest")
        
        # Configuration options (could come from config)
        self._language_mode = "quenya"  # quenya, sindarin, english, mixed
        self._show_yen = True
        self._show_star_signs = True
        self._age_reckoning = "fourth"
        
        # Elven data
        self._elven_data = CALENDAR_INFO["elven_data"]
        
        _LOGGER.debug(f"Initialized Rivendell Calendar sensor: {self._attr_name}")
    
    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes."""
        attrs = super().extra_state_attributes
        
        # Add Rivendell-specific attributes
        if hasattr(self, '_elven_date'):
            attrs.update(self._elven_date)
            
            # Add description in user's language
            attrs["description"] = self._translate('description')
            
            # Add reference
            attrs["reference"] = CALENDAR_INFO.get('reference_url', '')
            
            # Add special lore
            attrs["lore"] = self._get_daily_lore()
        
        return attrs
    
    def _calculate_elven_date(self, earth_date: datetime) -> Dict[str, Any]:
        """Calculate Elven Calendar date from Earth date."""
        
        # Calculate years from reference point (year 2000 = start of Fourth Age)
        years_since_2000 = earth_date.year - 2000
        fourth_age_year = 1 + years_since_2000
        
        # Calculate yén (144-year cycle)
        yen = (fourth_age_year - 1) // 144 + 1
        loa = (fourth_age_year - 1) % 144 + 1
        
        # Calculate day of year
        day_of_year = earth_date.timetuple().tm_yday
        
        # Adjust for calendar starting on March 20 (Spring Equinox)
        if earth_date.month < 3 or (earth_date.month == 3 and earth_date.day < 20):
            # Still in previous Elven year
            day_of_year = day_of_year + 365 - 79
            fourth_age_year -= 1
            loa = (fourth_age_year - 1) % 144 + 1
        else:
            day_of_year = day_of_year - 79
        
        if day_of_year <= 0:
            day_of_year += 365
        
        # Determine season and day within season
        season_data = self._get_season(day_of_year)
        
        # Get weekday (6-day Elven week)
        day_index = earth_date.toordinal() % 6
        weekday_data = self._elven_data["weekdays"][day_index]
        
        # Get time of day
        time_period = self._get_time_period(earth_date.hour)
        
        # Check for special days
        special_day = self._get_special_day(earth_date)
        
        # Get star sign (monthly)
        star_sign = self._elven_data["star_signs"][earth_date.month - 1]
        
        # Moon phases in Sindarin
        moon_phase = self._get_sindarin_moon_phase(earth_date)
        
        # Determine Age
        age_names = {
            "first": ("First Age", "F.A.", "Elain Einior"),
            "second": ("Second Age", "S.A.", "Elain Edin"),
            "third": ("Third Age", "T.A.", "Elain Nedein"),
            "fourth": ("Fourth Age", "F.A.", "Elain Canthui")
        }
        age_name, age_abbr, age_sindarin = age_names[self._age_reckoning]
        
        # Build display strings based on language mode
        if self._language_mode == "quenya":
            season_name = season_data["quenya"]
            weekday_name = weekday_data["quenya"]
            time_name = time_period["quenya"]
        elif self._language_mode == "sindarin":
            season_name = season_data["sindarin"]
            weekday_name = weekday_data["sindarin"]
            time_name = time_period["sindarin"]
        elif self._language_mode == "english":
            season_name = season_data["english"]
            weekday_name = weekday_data["english"]
            time_name = time_period["english"]
        else:  # mixed
            season_name = f"{season_data['quenya']} ({season_data['english']})"
            weekday_name = f"{weekday_data['quenya']} ({weekday_data['english']})"
            time_name = f"{time_period['quenya']} ({time_period['english']})"
        
        # Create result
        result = {
            "age": age_abbr,
            "age_name": age_name,
            "age_sindarin": age_sindarin,
            "year": fourth_age_year,
            "season": f"{season_data['emoji']} {season_name}",
            "season_quenya": season_data["quenya"],
            "season_sindarin": season_data["sindarin"],
            "day_in_season": season_data["day_in_season"],
            "weekday": weekday_name,
            "weekday_quenya": weekday_data["quenya"],
            "weekday_sindarin": weekday_data["sindarin"],
            "time_period": f"{time_period['emoji']} {time_name}",
            "moon_phase": moon_phase,
            "full_date": f"{age_abbr} {fourth_age_year}, {season_name} {season_data['day_in_season']} ({weekday_name})"
        }
        
        # Add optional data
        if self._show_yen:
            result["yen"] = yen
            result["loa"] = loa
            result["yen_display"] = f"Yén {yen}, Loa {loa}"
        
        if self._show_star_signs:
            result["star_sign"] = f"✨ {star_sign}"
        
        if special_day:
            result["special_day"] = special_day
        
        # Add poetic time description
        result["elven_greeting"] = self._get_elven_greeting(earth_date.hour)
        
        return result
    
    def _get_season(self, day_of_year: int) -> Dict[str, Any]:
        """Determine Elven season from day of year."""
        seasons = self._elven_data["seasons"]
        days_counted = 0
        
        for season in seasons:
            days_counted += season["days"]
            if day_of_year <= days_counted:
                day_in_season = day_of_year - (days_counted - season["days"])
                return {
                    **season,
                    "day_in_season": day_in_season
                }
        
        # Default to last season
        return {
            **seasons[-1],
            "day_in_season": day_of_year - (365 - seasons[-1]["days"])
        }
    
    def _get_time_period(self, hour: int) -> Dict[str, Any]:
        """Get Elven time period for hour."""
        periods = self._elven_data["time_periods"]
        
        if 5 <= hour < 7:
            period = periods["dawn"]
            emoji = "🌅"
        elif 7 <= hour < 12:
            period = periods["morning"]
            emoji = "🌤️"
        elif 12 <= hour < 15:
            period = periods["midday"]
            emoji = "☀️"
        elif 15 <= hour < 18:
            period = periods["afternoon"]
            emoji = "🌇"
        elif 18 <= hour < 21:
            period = periods["evening"]
            emoji = "🌆"
        else:
            period = periods["night"]
            emoji = "🌙"
        
        return {**period, "emoji": emoji}
    
    def _get_special_day(self, date: datetime) -> str:
        """Check for special Elven days."""
        special_days = {
            (3, 20): "🌅 Yestarë - First Day of the Year",
            (3, 25): "🌟 Elven New Year (Lady Day)",
            (6, 21): "☀️ Loëndë - Mid-year's Day",
            (9, 22): "🍂 Yáviérë - Harvest Festival (Bilbo & Frodo's Birthday)",
            (9, 29): "🌙 Durin's Day" if self._is_durins_day(date) else "",
            (12, 21): "⭐ Mettarë - Last Day of the Year"
        }
        return special_days.get((date.month, date.day), "")
    
    def _is_durins_day(self, date: datetime) -> bool:
        """Check if it's Durin's Day (first day of last moon of autumn)."""
        if date.month == 10 and 20 <= date.day <= 31:
            day_in_lunar = date.day % 29.5
            return day_in_lunar < 2
        return False
    
    def _get_sindarin_moon_phase(self, date: datetime) -> str:
        """Get moon phase in Sindarin."""
        day_in_lunar = date.day % 29.5
        
        if day_in_lunar < 2:
            return "🌑 Ithil Dú (Dark Moon)"
        elif day_in_lunar < 7:
            return "🌒 Ithil Orthad (Rising Moon)"
        elif day_in_lunar < 9:
            return "🌓 Ithil Perian (Half Moon)"
        elif day_in_lunar < 14:
            return "🌔 Ithil Síla (Bright Moon)"
        elif day_in_lunar < 16:
            return "🌕 Ithil Pennas (Full Moon)"
        elif day_in_lunar < 21:
            return "🌖 Ithil Dant (Falling Moon)"
        elif day_in_lunar < 23:
            return "🌗 Ithil Harn (Wounded Moon)"
        else:
            return "🌘 Ithil Fuin (Shadow Moon)"
    
    def _get_elven_greeting(self, hour: int) -> str:
        """Get appropriate Elven greeting for time of day."""
        greetings = {
            (5, 9): "Mae govannen (Well met)",
            (9, 12): "Alae (Good day)",
            (12, 17): "Mae aur (Good day)",
            (17, 21): "Mae dû (Good evening)",
            (21, 5): "Mae fuin (Good night)"
        }
        
        for (start, end), greeting in greetings.items():
            if start <= hour < end or (start > end and (hour >= start or hour < end)):
                return greeting
        return "Mae govannen"
    
    def _get_daily_lore(self) -> str:
        """Get a piece of Elven lore for the day."""
        day = datetime.now().day
        lore_pieces = [
            "The light of Eärendil shines brightest tonight",
            "Vilya, mightiest of the Three, preserves this realm",
            "The Last Homely House welcomes all weary travelers",
            "In Imladris, time flows like the Bruinen - sometimes swift, sometimes still",
            "The Council of Elrond convened on October 25th, T.A. 3018",
            "Elrond Half-elven has dwelt here since S.A. 1697",
            "The shards of Narsil were kept here for 3000 years",
            "Songs of the Elder Days echo in these halls",
            "The memory of Elendil is preserved in these archives",
            "Gil-galad's star once shone above these valleys"
        ]
        
        # Use day as index (cycling through lore)
        return lore_pieces[day % len(lore_pieces)]

    def update(self) -> None:
        """Update the sensor."""
        now = datetime.now()
        self._elven_date = self._calculate_elven_date(now)
        
        # Set state to full date
        self._state = self._elven_date["full_date"]
        
        _LOGGER.debug(f"Updated Rivendell calendar to {self._state}")