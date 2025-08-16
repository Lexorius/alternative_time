"""Roman Calendar implementation."""
from __future__ import annotations

from datetime import datetime
import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)


class RomanCalendarSensor(SensorEntity):
    """Sensor for displaying Roman Calendar."""

    def __init__(self, base_name: str) -> None:
        """Initialize the Roman calendar sensor."""
        self._attr_name = f"{base_name} Roman Calendar"
        self._attr_unique_id = f"{base_name}_roman_calendar"
        self._attr_icon = "mdi:pillar"
        self._state = None

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        roman_date = self._calculate_roman_date(datetime.now())
        
        return {
            "year_auc": roman_date["year_auc"],
            "year_ad": roman_date["year_ad"],
            "consul_year": roman_date["consul_year"],
            "month": roman_date["month"],
            "month_latin": roman_date["month_latin"],
            "day": roman_date["day"],
            "day_latin": roman_date["day_latin"],
            "day_type": roman_date["day_type"],
            "market_day": roman_date["market_day"],
            "hora": roman_date["hora"],
            "hora_type": roman_date["hora_type"],
            "festival": roman_date["festival"],
            "lucky_unlucky": roman_date["lucky_unlucky"],
            "phase_of_month": roman_date["phase_of_month"],
            "week_letter": roman_date["week_letter"],
            "gregorian_date": datetime.now().strftime("%Y-%m-%d"),
        }

    def _calculate_roman_date(self, earth_date: datetime) -> dict:
        """Calculate Roman date from modern date."""
        
        # Roman months with Latin names and days
        roman_months = [
            ("Ianuarius", "January", 31),
            ("Februarius", "February", 28),
            ("Martius", "March", 31),
            ("Aprilis", "April", 30),
            ("Maius", "May", 31),
            ("Iunius", "June", 30),
            ("Iulius/Quinctilis", "July", 31),  # Quinctilis before Julius Caesar
            ("Augustus/Sextilis", "August", 31),  # Sextilis before Augustus
            ("September", "September", 30),
            ("October", "October", 31),
            ("November", "November", 30),
            ("December", "December", 31)
        ]
        
        # Calculate Ab Urbe Condita (from founding of Rome, 753 BC)
        year_auc = earth_date.year + 753
        
        # Also show in regnal years (example: during Augustus)
        # Augustus ruled 27 BC - 14 AD
        if -27 <= (earth_date.year - 2000) <= 14:
            consul_year = f"Imp. Caesar Augustus, Year {earth_date.year + 27}"
        else:
            # Generic consul format
            consul_year = f"Anno Domini {earth_date.year}"
        
        # Get month info
        month_index = earth_date.month - 1
        month_latin, month_english, days_in_month = roman_months[month_index]
        
        # Calculate Roman day notation (counting backwards from Kalends, Nones, Ides)
        day = earth_date.day
        
        # Determine Nones and Ides for this month
        if earth_date.month in [3, 5, 7, 10]:  # March, May, July, October
            nones_day = 7
            ides_day = 15
        else:
            nones_day = 5
            ides_day = 13
        
        # Calculate the Roman day notation
        if day == 1:
            day_latin = f"Kalendis {self._get_month_ablative(month_latin)}"
            day_type = "Kalends"
            phase_of_month = "Beginning"
        elif day < nones_day:
            days_before = nones_day - day + 1  # Romans counted inclusively
            day_latin = f"ante diem {self._to_roman_numeral(days_before)} Nonas {self._get_month_accusative(month_latin)}"
            day_type = "Before Nones"
            phase_of_month = "Waxing"
        elif day == nones_day:
            day_latin = f"Nonis {self._get_month_ablative(month_latin)}"
            day_type = "Nones"
            phase_of_month = "First Quarter"
        elif day < ides_day:
            days_before = ides_day - day + 1
            day_latin = f"ante diem {self._to_roman_numeral(days_before)} Idus {self._get_month_accusative(month_latin)}"
            day_type = "Before Ides"
            phase_of_month = "Waxing"
        elif day == ides_day:
            day_latin = f"Idibus {self._get_month_ablative(month_latin)}"
            day_type = "Ides"
            phase_of_month = "Full"
        else:
            # Days after Ides count toward next month's Kalends
            if month_index < 11:
                next_month = roman_months[month_index + 1][0]
            else:
                next_month = roman_months[0][0]
            
            # Calculate days until next Kalends
            days_before = days_in_month - day + 2  # +2 because of inclusive counting
            day_latin = f"ante diem {self._to_roman_numeral(days_before)} Kalendas {self._get_month_accusative(next_month)}"
            day_type = "Before Kalends"
            phase_of_month = "Waning"
        
        # Nundinal cycle (8-day market week, labeled A-H)
        # Calculate continuous day count from a reference point
        reference_date = datetime(2000, 1, 1)
        days_since_reference = (earth_date - reference_date).days
        nundinal_letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        week_letter = nundinal_letters[days_since_reference % 8]
        market_day = "🛒 Market Day" if week_letter == 'A' else ""
        
        # Roman hours (12 day hours, 12 night hours, varying length)
        # Simplified: using equal hours
        hour = earth_date.hour
        if 6 <= hour < 18:
            # Day hours (Prima to Duodecima)
            hora_number = hour - 5
            hora_names = ["Prima", "Secunda", "Tertia", "Quarta", "Quinta", "Sexta",
                         "Septima", "Octava", "Nona", "Decima", "Undecima", "Duodecima"]
            if hora_number <= 12:
                hora = f"Hora {hora_names[hora_number - 1]}"
                hora_type = "Dies (Day)"
            else:
                hora = "Vespera"
                hora_type = "Evening"
        else:
            # Night hours
            if hour >= 18:
                hora_number = hour - 17
            else:
                hora_number = hour + 7
            
            night_watches = ["Prima Vigilia", "Secunda Vigilia", "Tertia Vigilia", "Quarta Vigilia"]
            watch = night_watches[min((hora_number - 1) // 3, 3)]
            hora = watch
            hora_type = "Nox (Night)"
        
        # Check for Roman festivals and special days
        festival = self._get_roman_festival(earth_date.month, earth_date.day)
        
        # Lucky/Unlucky days (Dies Fasti/Nefasti)
        # Simplified version
        if day_type in ["Kalends", "Nones", "Ides"]:
            lucky_unlucky = "Dies Nefastus (Unlucky)"
        elif festival:
            lucky_unlucky = "Dies Festus (Festival)"
        elif week_letter == 'A':
            lucky_unlucky = "Dies Nundinae (Market)"
        elif day % 2 == 0:
            lucky_unlucky = "Dies Fastus (Lucky)"
        else:
            lucky_unlucky = "Dies Comitialis (Assembly)"
        
        return {
            "year_auc": year_auc,
            "year_ad": earth_date.year,
            "consul_year": consul_year,
            "month": month_english,
            "month_latin": month_latin,
            "day": day,
            "day_latin": day_latin,
            "day_type": day_type,
            "market_day": market_day,
            "hora": hora,
            "hora_type": hora_type,
            "festival": festival,
            "lucky_unlucky": lucky_unlucky,
            "phase_of_month": phase_of_month,
            "week_letter": week_letter,
        }
    
    def _get_month_ablative(self, month: str) -> str:
        """Get ablative case of month name."""
        ablatives = {
            "Ianuarius": "Ianuariis",
            "Februarius": "Februariis",
            "Martius": "Martiis",
            "Aprilis": "Aprilibus",
            "Maius": "Maiis",
            "Iunius": "Iuniis",
            "Iulius/Quinctilis": "Iuliis",
            "Augustus/Sextilis": "Augustis",
            "September": "Septembribus",
            "October": "Octobribus",
            "November": "Novembribus",
            "December": "Decembribus"
        }
        return ablatives.get(month, month)
    
    def _get_month_accusative(self, month: str) -> str:
        """Get accusative case of month name."""
        accusatives = {
            "Ianuarius": "Ianuarias",
            "Februarius": "Februarias",
            "Martius": "Martias",
            "Aprilis": "Apriles",
            "Maius": "Maias",
            "Iunius": "Iunias",
            "Iulius/Quinctilis": "Iulias",
            "Augustus/Sextilis": "Augustas",
            "September": "Septembres",
            "October": "Octobres",
            "November": "Novembres",
            "December": "Decembres"
        }
        return accusatives.get(month, month)
    
    def _to_roman_numeral(self, num: int) -> str:
        """Convert number to Roman numeral."""
        val = [
            1000, 900, 500, 400,
            100, 90, 50, 40,
            10, 9, 5, 4,
            1
        ]
        syms = [
            'M', 'CM', 'D', 'CD',
            'C', 'XC', 'L', 'XL',
            'X', 'IX', 'V', 'IV',
            'I'
        ]
        roman_num = ''
        i = 0
        while num > 0:
            for _ in range(num // val[i]):
                roman_num += syms[i]
                num -= val[i]
            i += 1
        return roman_num
    
    def _get_roman_festival(self, month: int, day: int) -> str:
        """Get Roman festival for given date."""
        festivals = {
            (1, 1): "🎊 Kalendae Ianuariae - New Year",
            (1, 9): "⚖️ Agonalia",
            (1, 11): "🌾 Carmentalia",
            (2, 13): "🐺 Lupercalia - Wolf Festival",
            (2, 15): "🐺 Lupercalia",
            (2, 21): "👻 Feralia - Festival of the Dead",
            (2, 22): "🏠 Caristia - Family Day",
            (3, 1): "🔥 Matronalia - Women's Day",
            (3, 14): "🐴 Equirria - Horse Races",
            (3, 15): "🗡️ Anna Perenna",
            (3, 17): "🍷 Liberalia - Coming of Age",
            (3, 19): "⚔️ Quinquatria - Mars Festival",
            (4, 1): "🌸 Veneralia - Venus Festival",
            (4, 4): "🌍 Megalesia - Cybele Festival",
            (4, 12): "🌾 Cerealia - Ceres Festival",
            (4, 21): "🏛️ Parilia - Founding of Rome",
            (4, 25): "🦮 Robigalia",
            (5, 1): "🌺 Floralia - Flower Festival",
            (5, 9): "👻 Lemuria - Ghost Festival",
            (5, 11): "👻 Lemuria",
            (5, 13): "👻 Lemuria",
            (6, 9): "🍞 Vestalia - Vesta Festival",
            (6, 11): "⚔️ Matralia",
            (7, 5): "🌿 Poplifugia",
            (7, 7): "🎭 Ludi Apollinares",
            (7, 23): "🌊 Neptunalia - Neptune Festival",
            (8, 13): "🌙 Diana Festival",
            (8, 19): "🍇 Vinalia Rustica - Wine Festival",
            (8, 23): "🔥 Vulcanalia - Vulcan Festival",
            (9, 13): "⚡ Ides of September - Jupiter",
            (10, 11): "🍷 Meditrinalia - Wine Tasting",
            (10, 15): "🐴 October Horse",
            (11, 13): "⚡ Ides - Jupiter Festival",
            (12, 17): "🎉 Saturnalia Begins",
            (12, 19): "🎊 Saturnalia - Role Reversal Day",
            (12, 21): "☀️ Divalia",
            (12, 23): "🌾 Larentalia",
            (12, 25): "☀️ Dies Natalis Solis Invicti"
        }
        return festivals.get((month, day), "")

    def update(self) -> None:
        """Update the sensor."""
        roman_date = self._calculate_roman_date(datetime.now())
        
        # Format: AUC Year, Day Type
        # Example: "AUC 2777, ante diem III Kalendas Ianuarias"
        self._state = f"AUC {roman_date['year_auc']}, {roman_date['day_latin']}"