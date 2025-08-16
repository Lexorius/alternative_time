"""Minguo Calendar (Republic of China/Taiwan) implementation - Version 2.5."""
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
    "id": "minguo",
    "version": "2.5.0",
    "icon": "mdi:calendar-text",
    "category": "cultural",
    "accuracy": "official",
    "update_interval": UPDATE_INTERVAL,
    
    # Multi-language names
    "name": {
        "en": "Minguo Calendar (Taiwan)",
        "de": "Minguo-Kalender (Taiwan)",
        "es": "Calendario Minguo (Taiwán)",
        "fr": "Calendrier Minguo (Taïwan)",
        "it": "Calendario Minguo (Taiwan)",
        "nl": "Minguo Kalender (Taiwan)",
        "pt": "Calendário Minguo (Taiwan)",
        "ru": "Календарь Миньго (Тайвань)",
        "ja": "民国紀元（台湾）",
        "zh": "民國紀年",
        "zh-tw": "中華民國曆",
        "ko": "민국 달력 (대만)"
    }


class MinguoCalendarSensor(AlternativeTimeSensorBase):
    """Sensor for displaying Minguo Calendar (Taiwan/ROC)."""
    
    # Class-level update interval
    UPDATE_INTERVAL = 3600  # Update every hour
    
    def __init__(self, base_name: str, hass: HomeAssistant) -> None:
        """Initialize the Minguo calendar sensor."""
        super().__init__(base_name, hass)
        
        # Get translated name from metadata
        calendar_name = self._translate('name', 'Minguo Calendar')
        
        # Set sensor attributes
        self._attr_name = f"{base_name} {calendar_name}"
        self._attr_unique_id = f"{base_name}_minguo_calendar"
        self._attr_icon = CALENDAR_INFO.get("icon", "mdi:calendar-text")
        
        # Configuration options
        self._show_chinese = True
        self._show_holidays = True
        self._date_format = "traditional"
        
        # Minguo data
        self._minguo_data = CALENDAR_INFO["minguo_data"]
        
        _LOGGER.debug(f"Initialized Minguo Calendar sensor: {self._attr_name}")
    
    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes."""
        attrs = super().extra_state_attributes
        
        # Add Minguo-specific attributes
        if hasattr(self, '_minguo_date'):
            attrs.update(self._minguo_date)
            
            # Add description in user's language
            attrs["description"] = self._translate('description')
            
            # Add reference
            attrs["reference"] = CALENDAR_INFO.get('reference_url', '')
            
            # Add epoch information
            attrs["epoch_year"] = self._minguo_data["epoch_year"]
        
        return attrs
    
    def _number_to_chinese(self, num: int) -> str:
        """Convert number to Chinese characters."""
        if num == 0:
            return self._minguo_data["chinese_numbers"][0]
        
        result = ""
        if num >= 100:
            hundreds = num // 100
            result += self._minguo_data["chinese_numbers"][hundreds] + "百"
            num %= 100
        
        if num >= 10:
            tens = num // 10
            if tens > 1:
                result += self._minguo_data["chinese_numbers"][tens]
            result += "十"
            num %= 10
        
        if num > 0:
            result += self._minguo_data["chinese_numbers"][num]
        
        return result
    
    def _calculate_minguo_date(self, earth_date: datetime) -> Dict[str, Any]:
        """Calculate Minguo Calendar date from standard date."""
        
        # Calculate Minguo year
        minguo_year = earth_date.year - 1911
        
        # Get Chinese month and weekday names
        month_chinese = self._minguo_data["chinese_months"][earth_date.month - 1]
        weekday_chinese = self._minguo_data["chinese_weekdays"][earth_date.weekday()]
        
        # Determine era
        if minguo_year > 0:
            era = self._minguo_data["eras"]["republic"]["chinese"]
            era_english = self._minguo_data["eras"]["republic"]["english"]
            display_year = minguo_year
        else:
            era = self._minguo_data["eras"]["before"]["chinese"]
            era_english = self._minguo_data["eras"]["before"]["english"]
            display_year = abs(minguo_year - 1)
        
        # Check for holidays
        holiday_info = self._minguo_data["holidays"].get((earth_date.month, earth_date.day), {})
        holiday = ""
        holiday_english = ""
        if holiday_info:
            holiday = f"{holiday_info['emoji']} {holiday_info['name']}"
            holiday_english = holiday_info['en']
        
        # Convert year to Chinese if needed
        year_chinese = self._number_to_chinese(display_year) if self._show_chinese else str(display_year)
        day_chinese = self._number_to_chinese(earth_date.day) if self._show_chinese else str(earth_date.day)
        
        # Format dates based on style
        if self._date_format == "traditional":
            # Traditional Chinese format
            full_date_chinese = f"{era}{year_chinese}年{month_chinese}{day_chinese}日"
            full_date_numeric = f"{era} {display_year}年{earth_date.month}月{earth_date.day}日"
        elif self._date_format == "numeric":
            # Numeric format
            full_date_chinese = f"{era} {display_year}/{earth_date.month:02d}/{earth_date.day:02d}"
            full_date_numeric = f"{era} {display_year}/{earth_date.month:02d}/{earth_date.day:02d}"
        else:  # mixed
            # Mixed format
            full_date_chinese = f"{era}{display_year}年{month_chinese}{earth_date.day}日"
            full_date_numeric = f"{era} {display_year}年{earth_date.month}月{earth_date.day}日"
        
        # Determine season
        if earth_date.month in [3, 4, 5]:
            season = "春季"  # Spring
            season_emoji = "🌸"
        elif earth_date.month in [6, 7, 8]:
            season = "夏季"  # Summer
            season_emoji = "☀️"
        elif earth_date.month in [9, 10, 11]:
            season = "秋季"  # Autumn
            season_emoji = "🍂"
        else:
            season = "冬季"  # Winter
            season_emoji = "❄️"
        
        result = {
            "year": display_year,
            "year_chinese": year_chinese,
            "era": era,
            "era_english": era_english,
            "month": earth_date.month,
            "month_chinese": month_chinese,
            "day": earth_date.day,
            "day_chinese": day_chinese,
            "weekday": weekday_chinese,
            "season": f"{season_emoji} {season}",
            "gregorian_year": earth_date.year,
            "gregorian_date": earth_date.strftime("%Y-%m-%d"),
            "time": earth_date.strftime("%H:%M:%S"),
            "full_date_chinese": full_date_chinese,
            "full_date_numeric": full_date_numeric,
            "full_display": full_date_chinese if self._show_chinese else full_date_numeric
        }
        
        # Add holiday if present and enabled
        if self._show_holidays and holiday:
            result["holiday"] = holiday
            result["holiday_english"] = holiday_english
            result["full_display"] += f" {holiday}"
        
        return result
    
    def update(self) -> None:
        """Update the sensor."""
        now = datetime.now()
        self._minguo_date = self._calculate_minguo_date(now)
        
        # Set state based on format preference
        if self._show_chinese:
            self._state = self._minguo_date["full_date_chinese"]
        else:
            self._state = self._minguo_date["full_date_numeric"]
        
        _LOGGER.debug(f"Updated Minguo Calendar to {self._state}"),
    
    # Short descriptions for UI
    "description": {
        "en": "Taiwan/ROC calendar, Year 1 = 1912 CE (e.g. 民國114年)",
        "de": "Taiwan/ROC Kalender, Jahr 1 = 1912 CE (z.B. 民國114年)",
        "es": "Calendario de Taiwán/ROC, Año 1 = 1912 CE (ej. 民國114年)",
        "fr": "Calendrier de Taïwan/ROC, Année 1 = 1912 CE (ex. 民國114年)",
        "it": "Calendario Taiwan/ROC, Anno 1 = 1912 CE (es. 民國114年)",
        "nl": "Taiwan/ROC kalender, Jaar 1 = 1912 CE (bijv. 民國114年)",
        "pt": "Calendário de Taiwan/ROC, Ano 1 = 1912 CE (ex. 民國114年)",
        "ru": "Календарь Тайваня/КР, Год 1 = 1912 н.э. (напр. 民國114年)",
        "ja": "台湾/中華民国暦、元年 = 西暦1912年（例：民國114年）",
        "zh": "台湾/中华民国历法，元年 = 公元1912年（例：民國114年）",
        "zh-tw": "中華民國曆法，民國元年 = 西元1912年（例：民國114年）",
        "ko": "대만/중화민국 달력, 1년 = 서기 1912년 (예: 民國114年)"
    },
    
    # Detailed information for documentation
    "detailed_info": {
        "en": {
            "overview": "The Minguo calendar is the official calendar used in Taiwan (Republic of China)",
            "epoch": "Year 1 corresponds to 1912 CE, the founding year of the Republic of China",
            "structure": "Uses the same months and days as the Gregorian calendar, only the year numbering differs",
            "usage": "Official documents, government records, and daily life in Taiwan",
            "conversion": "Minguo year = Gregorian year - 1911",
            "before_epoch": "Years before 1912 are denoted as 民前 (before the Republic)",
            "holidays": "Includes traditional Chinese festivals and ROC national holidays"
        },
        "zh-tw": {
            "overview": "民國紀年是中華民國（台灣）的官方曆法",
            "epoch": "民國元年對應西元1912年，即中華民國成立之年",
            "structure": "使用與公曆相同的月份和日期，僅年份編號不同",
            "usage": "用於官方文件、政府記錄和台灣日常生活",
            "conversion": "民國年 = 西元年 - 1911",
            "before_epoch": "1912年之前的年份標記為民前",
            "holidays": "包含傳統中國節日和中華民國國定假日"
        },
        "de": {
            "overview": "Der Minguo-Kalender ist der offizielle Kalender in Taiwan (Republik China)",
            "epoch": "Jahr 1 entspricht 1912 n.Chr., dem Gründungsjahr der Republik China",
            "structure": "Verwendet dieselben Monate und Tage wie der gregorianische Kalender, nur die Jahreszählung unterscheidet sich",
            "usage": "Offizielle Dokumente, Regierungsunterlagen und tägliches Leben in Taiwan",
            "conversion": "Minguo-Jahr = Gregorianisches Jahr - 1911",
            "before_epoch": "Jahre vor 1912 werden als 民前 (vor der Republik) bezeichnet",
            "holidays": "Umfasst traditionelle chinesische Feste und ROC-Nationalfeiertage"
        }
    },
    
    # Minguo-specific data
    "minguo_data": {
        "epoch_year": 1912,
        "founding_date": "1912-01-01",
        
        # Month names in Traditional Chinese
        "chinese_months": [
            "一月", "二月", "三月", "四月", "五月", "六月",
            "七月", "八月", "九月", "十月", "十一月", "十二月"
        ],
        
        # Weekday names in Traditional Chinese
        "chinese_weekdays": [
            "星期一", "星期二", "星期三", "星期四",
            "星期五", "星期六", "星期日"
        ],
        
        # Important dates in ROC calendar
        "holidays": {
            (1, 1): {"name": "中華民國開國紀念日", "emoji": "🎊", "en": "Founding Day of ROC"},
            (2, 28): {"name": "和平紀念日", "emoji": "🕊️", "en": "Peace Memorial Day"},
            (3, 29): {"name": "革命先烈紀念日", "emoji": "🌹", "en": "Youth Day"},
            (4, 4): {"name": "兒童節", "emoji": "👶", "en": "Children's Day"},
            (4, 5): {"name": "清明節", "emoji": "🏔️", "en": "Tomb Sweeping Day"},
            (5, 1): {"name": "勞動節", "emoji": "👷", "en": "Labor Day"},
            (9, 28): {"name": "孔子誕辰紀念日", "emoji": "📚", "en": "Confucius' Birthday"},
            (10, 10): {"name": "國慶日", "emoji": "🇹🇼", "en": "National Day"},
            (10, 25): {"name": "臺灣光復節", "emoji": "🎌", "en": "Retrocession Day"},
            (10, 31): {"name": "蔣公誕辰紀念日", "emoji": "🎖️", "en": "Chiang Kai-shek's Birthday"},
            (11, 12): {"name": "國父誕辰紀念日", "emoji": "🏛️", "en": "Sun Yat-sen's Birthday"},
            (12, 25): {"name": "行憲紀念日", "emoji": "📜", "en": "Constitution Day"}
        },
        
        # Era names
        "eras": {
            "republic": {"chinese": "民國", "english": "Republic Era"},
            "before": {"chinese": "民前", "english": "Before Republic"}
        },
        
        # Number characters
        "chinese_numbers": ["〇", "一", "二", "三", "四", "五", "六", "七", "八", "九", "十"]
    },
    
    # Additional metadata
    "reference_url": "https://en.wikipedia.org/wiki/Republic_of_China_calendar",
    "documentation_url": "https://www.taiwan.gov.tw",
    "origin": "Republic of China (Taiwan)",
    "created_by": "Government of Republic of China",
    "introduced": "January 1, 1912",
    
    # Example format
    "example": "民國 114年3月15日",
    "example_meaning": "Republic Year 114, March 15 (= 2025-03-15 CE)",
    
    # Related calendars
    "related": ["gregorian", "chinese", "japanese"],
    
    # Tags for searching and filtering
    "tags": [
        "cultural", "taiwan", "roc", "republic_of_china", "official",
        "minguo", "chinese", "taiwanese", "asian", "modern"
    ],
    
    # Special features
    "features": {
        "official_calendar": True,
        "gregorian_based": True,
        "traditional_holidays": True,
        "chinese_characters": True,
        "precision": "day"
    },
    
    # Configuration options for this calendar
    "config_options": {
        "show_chinese": {
            "type": "boolean",
            "default": True,
            "description": {
                "en": "Show date in Chinese characters",
                "de": "Datum in chinesischen Zeichen anzeigen",
                "zh-tw": "顯示中文日期"
            }
        },
        "show_holidays": {
            "type": "boolean",
            "default": True,
            "description": {
                "en": "Show ROC national holidays",
                "de": "ROC-Nationalfeiertage anzeigen",
                "zh-tw": "顯示國定假日"
            }
        },
        "date_format": {
            "type": "select",
            "default": "traditional",
            "options": ["traditional", "numeric", "mixed"],
            "description": {
                "en": "Date format style",
                "de": "Datumsformat-Stil",
                "zh-tw": "日期格式樣式"
            }
        }
    }