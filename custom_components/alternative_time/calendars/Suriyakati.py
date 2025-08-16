"""Suriyakati Calendar (Thai Buddhist Calendar) implementation."""
from __future__ import annotations

from datetime import datetime, timedelta

from .base import AlternativeTimeSensorBase


class SuriyakatiCalendarSensor(AlternativeTimeSensorBase):
    """Sensor for displaying Suriyakati Calendar (Thai)."""

    def __init__(self, base_name: str) -> None:
        """Initialize the Suriyakati calendar sensor."""
        super().__init__(base_name, "suriyakati_calendar", "Suriyakati Calendar")
        self._attr_icon = "mdi:buddhism"
        self._update_interval = timedelta(hours=1)
        
        # Thai month names
        self.thai_months = {
            1: "มกราคม",      # Makarakhom (January)
            2: "กุมภาพันธ์",   # Kumphaphan (February)
            3: "มีนาคม",      # Minakhom (March)
            4: "เมษายน",     # Mesayon (April)
            5: "พฤษภาคม",    # Phruetsaphakhom (May)
            6: "มิถุนายน",    # Mithunayon (June)
            7: "กรกฎาคม",    # Karakadakhom (July)
            8: "สิงหาคม",     # Singhakhom (August)
            9: "กันยายน",     # Kanyayon (September)
            10: "ตุลาคม",     # Tulakhom (October)
            11: "พฤศจิกายน",  # Phruetsachikayon (November)
            12: "ธันวาคม"     # Thanwakhom (December)
        }
        
        # Romanized month names
        self.roman_months = {
            1: "Makarakhom", 2: "Kumphaphan", 3: "Minakhom", 
            4: "Mesayon", 5: "Phruetsaphakhom", 6: "Mithunayon",
            7: "Karakadakhom", 8: "Singhakhom", 9: "Kanyayon",
            10: "Tulakhom", 11: "Phruetsachikayon", 12: "Thanwakhom"
        }
        
        # Thai numerals 0-9
        self.thai_digits = "๐๑๒๓๔๕๖๗๘๙"
        
        # Thai weekdays
        self.thai_weekdays = [
            "วันอาทิตย์",   # Sunday (Sun day)
            "วันจันทร์",    # Monday (Moon day)
            "วันอังคาร",    # Tuesday (Mars day)
            "วันพุธ",       # Wednesday (Mercury day)
            "วันพฤหัสบดี",  # Thursday (Jupiter day)
            "วันศุกร์",      # Friday (Venus day)
            "วันเสาร์"      # Saturday (Saturn day)
        ]
        
        # Thai zodiac animals (12-year cycle)
        self.thai_zodiac = [
            "ชวด",   # Rat
            "ฉลู",    # Ox
            "ขาล",   # Tiger
            "เถาะ",   # Rabbit
            "มะโรง",  # Dragon
            "มะเส็ง",  # Snake
            "มะเมีย",  # Horse
            "มะแม",   # Goat
            "วอก",   # Monkey
            "ระกา",   # Rooster
            "จอ",    # Dog
            "กุน"     # Pig
        ]
        
        # Important Thai Buddhist holidays
        self.thai_holidays = {
            (1, 1): "วันขึ้นปีใหม่ (New Year)",
            (2, 14): "วันวาเลนไทน์ (Valentine's Day)",
            (4, 6): "วันจักรี (Chakri Day)",
            (4, 13): "วันสงกรานต์ (Songkran)",
            (5, 1): "วันแรงงาน (Labour Day)",
            (7, 28): "วันเฉลิมพระชนมพรรษา (King's Birthday)",
            (8, 12): "วันแม่แห่งชาติ (Mother's Day)",
            (10, 13): "วันคล้ายวันสวรรคต (Memorial Day)",
            (12, 5): "วันพ่อแห่งชาติ (Father's Day)",
            (12, 10): "วันรัฐธรรมนูญ (Constitution Day)"
        }

    def to_thai_number(self, n):
        """Convert number to Thai numerals."""
        return ''.join(self.thai_digits[int(d)] for d in str(n))
    
    def calculate_time(self) -> str:
        """Calculate current Suriyakati Calendar date.
        
        The Thai calendar (Suriyakati) is the official calendar of Thailand:
        
        Key features:
        - Buddhist Era (BE) = Common Era (CE) + 543
        - Solar calendar (same as Gregorian)
        - Year starts on January 1 (since 1941)
        - Traditional New Year (Songkran) still celebrated April 13-15
        
        Cultural aspects:
        - Days are associated with colors
        - Each day has a planetary deity
        - 12-year animal cycle (similar to Chinese zodiac)
        - Important Buddhist holy days follow lunar calendar
        
        Numerals:
        - Thai numerals: ๐๑๒๓๔๕๖๗๘๙
        - Often mixed with Arabic numerals in modern usage
        
        Format: Thai date | Romanized | BE year | Zodiac
        Example: ๒๕ ธันวาคม ๒๕๖๘ | 25 Thanwakhom 2568 BE | Year of the Dragon
        """
        now = datetime.now()
        
        # Calculate Buddhist Era year
        buddhist_year = now.year + 543
        
        # Get Thai month name
        thai_month = self.thai_months[now.month]
        roman_month = self.roman_months[now.month]
        
        # Convert day and year to Thai numerals
        thai_day = self.to_thai_number(now.day)
        thai_year = self.to_thai_number(buddhist_year)
        
        # Get weekday
        weekday_index = (now.weekday() + 1) % 7  # Thai week starts on Sunday
        thai_weekday = self.thai_weekdays[weekday_index]
        
        # Calculate zodiac animal (12-year cycle)
        # Thai zodiac starts from year 0 = Rat
        # Aligned so that 2024 CE (2567 BE) = Year of the Dragon (index 4)
        zodiac_index = (buddhist_year - 3) % 12
        zodiac_animal = self.thai_zodiac[zodiac_index]
        
        # Check for holidays
        holiday = self.thai_holidays.get((now.month, now.day), "")
        holiday_str = f" | {holiday}" if holiday else ""
        
        # Buddhist holy day calculation (simplified)
        # Full moon days (15th of lunar month) are important
        # This is simplified - actual calculation follows lunar calendar
        lunar_approximation = (now.day + now.month * 2) % 30
        if lunar_approximation in [8, 15, 23, 30]:  # Quarter moon days
            if lunar_approximation == 15:
                holy_day = " | 🌕 วันพระ (Buddhist Holy Day)"
            else:
                holy_day = " | 🌓 วันพระ (Buddhist Holy Day)"
        else:
            holy_day = ""
        
        # Time period in Thai tradition
        hour = now.hour
        if 6 <= hour < 12:
            time_period = "เช้า (Morning)"
        elif 12 <= hour < 13:
            time_period = "เที่ยง (Noon)"
        elif 13 <= hour < 16:
            time_period = "บ่าย (Afternoon)"
        elif 16 <= hour < 18:
            time_period = "เย็น (Evening)"
        elif 18 <= hour < 20:
            time_period = "ค่ำ (Early Night)"
        else:
            time_period = "ดึก (Late Night)"
        
        # Format: Thai | Romanized | Additional info
        thai_date = f"{thai_day} {thai_month} {thai_year}"
        roman_date = f"{now.day} {roman_month} {buddhist_year} BE"
        
        return f"{thai_date} | {roman_date} | {zodiac_animal} | {time_period}{holy_day}{holiday_str}"