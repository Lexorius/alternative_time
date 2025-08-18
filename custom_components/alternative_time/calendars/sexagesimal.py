"""Sexagesimal Cycle Calendar (干支 Gānzhī) implementation - Version 2.5."""
from __future__ import annotations

from datetime import datetime
import logging
from typing import Dict, Any, Tuple

from homeassistant.core import HomeAssistant
from ..sensor import AlternativeTimeSensorBase

_LOGGER = logging.getLogger(__name__)

# ============================================
# CALENDAR METADATA
# ============================================

# Update interval in seconds (3600 = 1 hour for daily cycle)
UPDATE_INTERVAL = 3600

# Complete calendar information for auto-discovery
CALENDAR_INFO = {
    "id": "sexagesimal",
    "version": "2.5.0",
    "icon": "mdi:numeric-6-box-multiple",
    "category": "cultural",
    "accuracy": "traditional",
    "update_interval": UPDATE_INTERVAL,
    
    # Multi-language names
    "name": {
        "en": "Sexagesimal Cycle Calendar",
        "de": "Sexagesimalzyklus-Kalender",
        "es": "Calendario del Ciclo Sexagesimal",
        "fr": "Calendrier du Cycle Sexagésimal",
        "it": "Calendario del Ciclo Sessagesimale",
        "nl": "Sexagesimale Cyclus Kalender",
        "pt": "Calendário do Ciclo Sexagesimal",
        "ru": "Шестидесятеричный циклический календарь",
        "ja": "六十干支暦",
        "zh": "干支纪年历",
        "ko": "육십간지력"
    },
    
    # Short descriptions for UI
    "description": {
        "en": "Traditional 60-year cycle with Heavenly Stems and Earthly Branches",
        "de": "Traditioneller 60-Jahres-Zyklus mit Himmelsstämmen und Erdzweigen",
        "es": "Ciclo tradicional de 60 años con Tallos Celestiales y Ramas Terrestres",
        "fr": "Cycle traditionnel de 60 ans avec Tiges Célestes et Branches Terrestres",
        "it": "Ciclo tradizionale di 60 anni con Steli Celesti e Rami Terrestri",
        "nl": "Traditionele 60-jarige cyclus met Hemelse Stammen en Aardse Takken",
        "pt": "Ciclo tradicional de 60 anos com Troncos Celestiais e Ramos Terrestres",
        "ru": "Традиционный 60-летний цикл с Небесными Стволами и Земными Ветвями",
        "ja": "天干と地支による伝統的な60年周期",
        "zh": "天干地支六十甲子循环系统",
        "ko": "천간과 지지에 의한 전통적인 60년 주기"
    },
    
    # Detailed information for documentation
    "detailed_info": {
        "en": {
            "overview": "The Sexagesimal cycle is a traditional East Asian calendar system",
            "structure": "Combines 10 Heavenly Stems with 12 Earthly Branches for a 60-year cycle",
            "usage": "Used in Chinese, Japanese, Korean, and Vietnamese calendars",
            "elements": "Each stem and branch is associated with elements and yin-yang",
            "zodiac": "The 12 branches correspond to the zodiac animals",
            "applications": "Used for years, months, days, and hours"
        },
        "de": {
            "overview": "Der Sexagesimalzyklus ist ein traditionelles ostasiatisches Kalendersystem",
            "structure": "Kombiniert 10 Himmelsstämme mit 12 Erdzweigen für einen 60-Jahres-Zyklus",
            "usage": "Verwendet in chinesischen, japanischen, koreanischen und vietnamesischen Kalendern",
            "elements": "Jeder Stamm und Zweig ist mit Elementen und Yin-Yang verbunden",
            "zodiac": "Die 12 Zweige entsprechen den Tierkreiszeichen",
            "applications": "Verwendet für Jahre, Monate, Tage und Stunden"
        }
    },
    
    # Sexagesimal system data
    "sexagesimal_data": {
        # Ten Heavenly Stems (十天干)
        "heavenly_stems": [
            {
                "cn": "甲", "traditional": "甲", "pinyin": "jiǎ", 
                "element": "Wood", "element_cn": "木", "yin_yang": "Yang",
                "number": 1, "color": "青", "color_en": "Green",
                "direction": "East", "season": "Spring"
            },
            {
                "cn": "乙", "traditional": "乙", "pinyin": "yǐ",
                "element": "Wood", "element_cn": "木", "yin_yang": "Yin",
                "number": 2, "color": "青", "color_en": "Green",
                "direction": "East", "season": "Spring"
            },
            {
                "cn": "丙", "traditional": "丙", "pinyin": "bǐng",
                "element": "Fire", "element_cn": "火", "yin_yang": "Yang",
                "number": 3, "color": "赤", "color_en": "Red",
                "direction": "South", "season": "Summer"
            },
            {
                "cn": "丁", "traditional": "丁", "pinyin": "dīng",
                "element": "Fire", "element_cn": "火", "yin_yang": "Yin",
                "number": 4, "color": "赤", "color_en": "Red",
                "direction": "South", "season": "Summer"
            },
            {
                "cn": "戊", "traditional": "戊", "pinyin": "wù",
                "element": "Earth", "element_cn": "土", "yin_yang": "Yang",
                "number": 5, "color": "黄", "color_en": "Yellow",
                "direction": "Center", "season": "Late Summer"
            },
            {
                "cn": "己", "traditional": "己", "pinyin": "jǐ",
                "element": "Earth", "element_cn": "土", "yin_yang": "Yin",
                "number": 6, "color": "黄", "color_en": "Yellow",
                "direction": "Center", "season": "Late Summer"
            },
            {
                "cn": "庚", "traditional": "庚", "pinyin": "gēng",
                "element": "Metal", "element_cn": "金", "yin_yang": "Yang",
                "number": 7, "color": "白", "color_en": "White",
                "direction": "West", "season": "Autumn"
            },
            {
                "cn": "辛", "traditional": "辛", "pinyin": "xīn",
                "element": "Metal", "element_cn": "金", "yin_yang": "Yin",
                "number": 8, "color": "白", "color_en": "White",
                "direction": "West", "season": "Autumn"
            },
            {
                "cn": "壬", "traditional": "壬", "pinyin": "rén",
                "element": "Water", "element_cn": "水", "yin_yang": "Yang",
                "number": 9, "color": "黑", "color_en": "Black",
                "direction": "North", "season": "Winter"
            },
            {
                "cn": "癸", "traditional": "癸", "pinyin": "guǐ",
                "element": "Water", "element_cn": "水", "yin_yang": "Yin",
                "number": 10, "color": "黑", "color_en": "Black",
                "direction": "North", "season": "Winter"
            }
        ],
        
        # Twelve Earthly Branches (十二地支)
        "earthly_branches": [
            {
                "cn": "子", "traditional": "子", "pinyin": "zǐ",
                "animal": "Rat", "animal_cn": "鼠", "emoji": "🐀",
                "hour": "23:00-01:00", "month": 11, "yin_yang": "Yang",
                "element": "Water", "direction": "North"
            },
            {
                "cn": "丑", "traditional": "丑", "pinyin": "chǒu",
                "animal": "Ox", "animal_cn": "牛", "emoji": "🐂",
                "hour": "01:00-03:00", "month": 12, "yin_yang": "Yin",
                "element": "Earth", "direction": "NNE"
            },
            {
                "cn": "寅", "traditional": "寅", "pinyin": "yín",
                "animal": "Tiger", "animal_cn": "虎", "emoji": "🐅",
                "hour": "03:00-05:00", "month": 1, "yin_yang": "Yang",
                "element": "Wood", "direction": "ENE"
            },
            {
                "cn": "卯", "traditional": "卯", "pinyin": "mǎo",
                "animal": "Rabbit", "animal_cn": "兔", "emoji": "🐇",
                "hour": "05:00-07:00", "month": 2, "yin_yang": "Yin",
                "element": "Wood", "direction": "East"
            },
            {
                "cn": "辰", "traditional": "辰", "pinyin": "chén",
                "animal": "Dragon", "animal_cn": "龙", "emoji": "🐉",
                "hour": "07:00-09:00", "month": 3, "yin_yang": "Yang",
                "element": "Earth", "direction": "ESE"
            },
            {
                "cn": "巳", "traditional": "巳", "pinyin": "sì",
                "animal": "Snake", "animal_cn": "蛇", "emoji": "🐍",
                "hour": "09:00-11:00", "month": 4, "yin_yang": "Yin",
                "element": "Fire", "direction": "SSE"
            },
            {
                "cn": "午", "traditional": "午", "pinyin": "wǔ",
                "animal": "Horse", "animal_cn": "马", "emoji": "🐴",
                "hour": "11:00-13:00", "month": 5, "yin_yang": "Yang",
                "element": "Fire", "direction": "South"
            },
            {
                "cn": "未", "traditional": "未", "pinyin": "wèi",
                "animal": "Goat", "animal_cn": "羊", "emoji": "🐑",
                "hour": "13:00-15:00", "month": 6, "yin_yang": "Yin",
                "element": "Earth", "direction": "SSW"
            },
            {
                "cn": "申", "traditional": "申", "pinyin": "shēn",
                "animal": "Monkey", "animal_cn": "猴", "emoji": "🐵",
                "hour": "15:00-17:00", "month": 7, "yin_yang": "Yang",
                "element": "Metal", "direction": "WSW"
            },
            {
                "cn": "酉", "traditional": "酉", "pinyin": "yǒu",
                "animal": "Rooster", "animal_cn": "鸡", "emoji": "🐔",
                "hour": "17:00-19:00", "month": 8, "yin_yang": "Yin",
                "element": "Metal", "direction": "West"
            },
            {
                "cn": "戌", "traditional": "戌", "pinyin": "xū",
                "animal": "Dog", "animal_cn": "狗", "emoji": "🐕",
                "hour": "19:00-21:00", "month": 9, "yin_yang": "Yang",
                "element": "Earth", "direction": "WNW"
            },
            {
                "cn": "亥", "traditional": "亥", "pinyin": "hài",
                "animal": "Pig", "animal_cn": "猪", "emoji": "🐖",
                "hour": "21:00-23:00", "month": 10, "yin_yang": "Yin",
                "element": "Water", "direction": "NNW"
            }
        ],
        
        # 60 Cycle combinations
        "cycle_names": [
            "甲子", "乙丑", "丙寅", "丁卯", "戊辰", "己巳", "庚午", "辛未", "壬申", "癸酉",
            "甲戌", "乙亥", "丙子", "丁丑", "戊寅", "己卯", "庚辰", "辛巳", "壬午", "癸未",
            "甲申", "乙酉", "丙戌", "丁亥", "戊子", "己丑", "庚寅", "辛卯", "壬辰", "癸巳",
            "甲午", "乙未", "丙申", "丁酉", "戊戌", "己亥", "庚子", "辛丑", "壬寅", "癸卯",
            "甲辰", "乙巳", "丙午", "丁未", "戊申", "己酉", "庚戌", "辛亥", "壬子", "癸丑",
            "甲寅", "乙卯", "丙辰", "丁巳", "戊午", "己未", "庚申", "辛酉", "壬戌", "癸亥"
        ],
        
        # Five Elements relationships
        "wu_xing": {
            "generating": {
                "Wood": "Fire", "Fire": "Earth", "Earth": "Metal",
                "Metal": "Water", "Water": "Wood"
            },
            "overcoming": {
                "Wood": "Earth", "Earth": "Water", "Water": "Fire",
                "Fire": "Metal", "Metal": "Wood"
            }
        },
        
        # Reference epochs for calculations
        "epochs": {
            "year": {"date": "1984-02-02", "stem": 0, "branch": 0},  # 甲子年
            "month": {"date": "1984-01-01", "stem": 5, "branch": 10},  # 己亥月
            "day": {"date": "1984-01-01", "stem": 0, "branch": 10},  # 甲戌日
            "hour": {"base": "1984-01-01 00:00", "stem": 0, "branch": 0}  # 甲子时
        }
    },
    
    # Additional metadata
    "reference_url": "https://en.wikipedia.org/wiki/Sexagenary_cycle",
    "documentation_url": "https://www.chinesefortunecalendar.com/",
    "origin": "Ancient China",
    "created_by": "Ancient Chinese astronomers",
    "period": "Shang Dynasty (1600-1046 BCE)",
    
    # Example format
    "example": "甲子年 乙丑月 丙寅日 丁卯时",
    "example_meaning": "Wood-Rat Year, Wood-Ox Month, Fire-Tiger Day, Fire-Rabbit Hour",
    
    # Related calendars
    "related": ["chinese", "japanese", "korean", "vietnamese"],
    
    # Tags for searching and filtering
    "tags": [
        "cultural", "asian", "chinese", "traditional", "sexagesimal",
        "ganzhi", "stems", "branches", "zodiac", "elements"
    ],
    
    # Special features
    "features": {
        "cyclical": True,
        "elements": True,
        "zodiac": True,
        "yin_yang": True,
        "precision": "hour"
    },
    
    # Configuration options
    "config_options": {
        "cycle_type": {
            "type": "select",
            "default": "all",
            "options": ["all", "year", "month", "day", "hour"],
            "description": {
                "en": "Which cycles to display",
                "de": "Welche Zyklen anzeigen",
                "zh": "显示哪些周期"
            }
        },
        "display_format": {
            "type": "select",
            "default": "chinese",
            "options": ["chinese", "pinyin", "english", "detailed"],
            "description": {
                "en": "Display format",
                "de": "Anzeigeformat",
                "zh": "显示格式"
            }
        },
        "show_elements": {
            "type": "boolean",
            "default": True,
            "description": {
                "en": "Show Five Elements (Wu Xing)",
                "de": "Fünf Elemente anzeigen (Wu Xing)",
                "zh": "显示五行"
            }
        },
        "show_zodiac": {
            "type": "boolean",
            "default": True,
            "description": {
                "en": "Show zodiac animals",
                "de": "Tierkreiszeichen anzeigen",
                "zh": "显示生肖"
            }
        },
        "show_cycle_number": {
            "type": "boolean",
            "default": False,
            "description": {
                "en": "Show position in 60-year cycle",
                "de": "Position im 60-Jahre-Zyklus anzeigen",
                "zh": "显示六十甲子序号"
            }
        }
    }
}


class SexagesimalCalendarSensor(AlternativeTimeSensorBase):
    """Sensor for displaying Sexagesimal Cycle Calendar (干支)."""
    
    # Class-level update interval
    UPDATE_INTERVAL = 3600  # Update every hour
    
    def __init__(self, base_name: str, hass: HomeAssistant) -> None:
        """Initialize the Sexagesimal calendar sensor."""
        super().__init__(base_name, hass)
        
        # Get translated name from metadata
        calendar_name = self._translate('name', 'Sexagesimal Cycle Calendar')
        
        # Set sensor attributes
        self._attr_name = f"{base_name} {calendar_name}"
        self._attr_unique_id = f"{base_name}_sexagesimal"
        self._attr_icon = CALENDAR_INFO.get("icon", "mdi:numeric-6-box-multiple")
        
        # Get plugin options
        options = self.get_plugin_options()
        
        # Configuration options with defaults
        self._cycle_type = options.get("cycle_type", "all")
        self._display_format = options.get("display_format", "chinese")
        self._show_elements = options.get("show_elements", True)
        self._show_zodiac = options.get("show_zodiac", True)
        self._show_cycle_number = options.get("show_cycle_number", False)
        
        # Sexagesimal data
        self._sexagesimal_data = CALENDAR_INFO["sexagesimal_data"]
        
        _LOGGER.debug(f"Initialized Sexagesimal Calendar sensor: {self._attr_name}")
    
    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes."""
        attrs = super().extra_state_attributes
        
        # Add Sexagesimal-specific attributes
        if hasattr(self, '_sexagesimal_date'):
            attrs.update(self._sexagesimal_date)
            
            # Add description in user's language
            attrs["description"] = self._translate('description')
            
            # Add reference
            attrs["reference"] = CALENDAR_INFO.get('reference_url', '')
        
        return attrs
    
    def _calculate_stem_branch(self, reference_date: str, reference_stem: int, 
                              reference_branch: int, target_date: datetime,
                              cycle_days: int) -> Tuple[int, int, int]:
        """Calculate stem and branch indices for a given date."""
        ref = datetime.strptime(reference_date, "%Y-%m-%d" if ":" not in reference_date else "%Y-%m-%d %H:%M")
        
        if cycle_days == 365:  # Year calculation
            # Use years difference
            diff = target_date.year - ref.year
        elif cycle_days == 30:  # Month calculation
            # Use months difference
            diff = (target_date.year - ref.year) * 12 + (target_date.month - ref.month)
        elif cycle_days == 1:  # Day calculation
            diff = (target_date.date() - ref.date()).days
        else:  # Hour calculation (cycle_days == 0.0833)
            diff = int((target_date - ref).total_seconds() / 7200)  # 2-hour periods
        
        stem_index = (reference_stem + diff) % 10
        branch_index = (reference_branch + diff) % 12
        cycle_position = (stem_index * 6 + branch_index) % 60
        
        return stem_index, branch_index, cycle_position
    
    def _get_hour_branch(self, hour: int) -> int:
        """Get the earthly branch for a given hour."""
        # Each branch covers 2 hours, starting from 23:00 (子时)
        if hour >= 23 or hour < 1:
            return 0  # 子
        elif hour < 3:
            return 1  # 丑
        elif hour < 5:
            return 2  # 寅
        elif hour < 7:
            return 3  # 卯
        elif hour < 9:
            return 4  # 辰
        elif hour < 11:
            return 5  # 巳
        elif hour < 13:
            return 6  # 午
        elif hour < 15:
            return 7  # 未
        elif hour < 17:
            return 8  # 申
        elif hour < 19:
            return 9  # 酉
        elif hour < 21:
            return 10  # 戌
        else:
            return 11  # 亥
    
    def _format_stem_branch(self, stem: Dict, branch: Dict, cycle_pos: int) -> str:
        """Format stem-branch combination based on display format."""
        if self._display_format == "chinese":
            result = f"{stem['cn']}{branch['cn']}"
        elif self._display_format == "pinyin":
            result = f"{stem['pinyin']}{branch['pinyin']}"
        elif self._display_format == "english":
            result = f"{stem['element']}-{branch['animal']}"
        else:  # detailed
            result = f"{stem['cn']}{branch['cn']}({stem['pinyin']}{branch['pinyin']})"
        
        if self._show_cycle_number:
            result = f"{result}[{cycle_pos + 1}/60]"
        
        return result
    
    def _calculate_sexagesimal_date(self, earth_date: datetime) -> Dict[str, Any]:
        """Calculate Sexagesimal cycle for given date."""
        
        result = {}
        display_parts = []
        
        # Calculate Year Cycle (年柱)
        if self._cycle_type in ["all", "year"]:
            year_stem, year_branch, year_cycle = self._calculate_stem_branch(
                self._sexagesimal_data["epochs"]["year"]["date"],
                self._sexagesimal_data["epochs"]["year"]["stem"],
                self._sexagesimal_data["epochs"]["year"]["branch"],
                earth_date, 365
            )
            
            year_stem_data = self._sexagesimal_data["heavenly_stems"][year_stem]
            year_branch_data = self._sexagesimal_data["earthly_branches"][year_branch]
            
            result["year_stem_cn"] = year_stem_data["cn"]
            result["year_branch_cn"] = year_branch_data["cn"]
            result["year_ganzhi"] = f"{year_stem_data['cn']}{year_branch_data['cn']}"
            result["year_animal"] = year_branch_data["animal"]
            result["year_emoji"] = year_branch_data["emoji"]
            result["year_element"] = year_stem_data["element"]
            result["year_cycle_position"] = year_cycle + 1
            
            year_display = self._format_stem_branch(year_stem_data, year_branch_data, year_cycle)
            if self._show_zodiac:
                year_display = f"{year_branch_data['emoji']} {year_display}年"
            else:
                year_display = f"{year_display}年"
            
            display_parts.append(year_display)
        
        # Calculate Month Cycle (月柱)
        if self._cycle_type in ["all", "month"]:
            month_stem, month_branch, month_cycle = self._calculate_stem_branch(
                self._sexagesimal_data["epochs"]["month"]["date"],
                self._sexagesimal_data["epochs"]["month"]["stem"],
                self._sexagesimal_data["epochs"]["month"]["branch"],
                earth_date, 30
            )
            
            month_stem_data = self._sexagesimal_data["heavenly_stems"][month_stem]
            month_branch_data = self._sexagesimal_data["earthly_branches"][month_branch]
            
            result["month_stem_cn"] = month_stem_data["cn"]
            result["month_branch_cn"] = month_branch_data["cn"]
            result["month_ganzhi"] = f"{month_stem_data['cn']}{month_branch_data['cn']}"
            result["month_element"] = month_stem_data["element"]
            
            month_display = self._format_stem_branch(month_stem_data, month_branch_data, month_cycle)
            display_parts.append(f"{month_display}月")
        
        # Calculate Day Cycle (日柱)
        if self._cycle_type in ["all", "day"]:
            day_stem, day_branch, day_cycle = self._calculate_stem_branch(
                self._sexagesimal_data["epochs"]["day"]["date"],
                self._sexagesimal_data["epochs"]["day"]["stem"],
                self._sexagesimal_data["epochs"]["day"]["branch"],
                earth_date, 1
            )
            
            day_stem_data = self._sexagesimal_data["heavenly_stems"][day_stem]
            day_branch_data = self._sexagesimal_data["earthly_branches"][day_branch]
            
            result["day_stem_cn"] = day_stem_data["cn"]
            result["day_branch_cn"] = day_branch_data["cn"]
            result["day_ganzhi"] = f"{day_stem_data['cn']}{day_branch_data['cn']}"
            result["day_element"] = day_stem_data["element"]
            
            day_display = self._format_stem_branch(day_stem_data, day_branch_data, day_cycle)
            display_parts.append(f"{day_display}日")
        
        # Calculate Hour Cycle (时柱)
        if self._cycle_type in ["all", "hour"]:
            hour_branch_index = self._get_hour_branch(earth_date.hour)
            # Hour stem is calculated based on day stem and hour branch
            # Formula: (day_stem * 2 + hour_branch) % 10
            if self._cycle_type in ["all", "day"]:
                hour_stem_index = (day_stem * 2 + hour_branch_index) % 10
            else:
                # If we don't have day stem, calculate it
                day_stem, _, _ = self._calculate_stem_branch(
                    self._sexagesimal_data["epochs"]["day"]["date"],
                    self._sexagesimal_data["epochs"]["day"]["stem"],
                    self._sexagesimal_data["epochs"]["day"]["branch"],
                    earth_date, 1
                )
                hour_stem_index = (day_stem * 2 + hour_branch_index) % 10
            
            hour_stem_data = self._sexagesimal_data["heavenly_stems"][hour_stem_index]
            hour_branch_data = self._sexagesimal_data["earthly_branches"][hour_branch_index]
            
            result["hour_stem_cn"] = hour_stem_data["cn"]
            result["hour_branch_cn"] = hour_branch_data["cn"]
            result["hour_ganzhi"] = f"{hour_stem_data['cn']}{hour_branch_data['cn']}"
            result["hour_element"] = hour_stem_data["element"]
            result["hour_period"] = hour_branch_data["hour"]
            
            hour_cycle = (hour_stem_index * 6 + hour_branch_index) % 60
            hour_display = self._format_stem_branch(hour_stem_data, hour_branch_data, hour_cycle)
            display_parts.append(f"{hour_display}时")
        
        # Add Five Elements relationships if enabled
        if self._show_elements and self._cycle_type == "all":
            elements = []
            if "year_element" in result:
                elements.append(result["year_element"])
            if "month_element" in result:
                elements.append(result["month_element"])
            if "day_element" in result:
                elements.append(result["day_element"])
            if "hour_element" in result:
                elements.append(result["hour_element"])
            
            if len(elements) >= 2:
                # Check generating relationship
                generating = []
                overcoming = []
                wu_xing = self._sexagesimal_data["wu_xing"]
                
                for i in range(len(elements) - 1):
                    if wu_xing["generating"].get(elements[i]) == elements[i + 1]:
                        generating.append(f"{elements[i]}→{elements[i + 1]}")
                    elif wu_xing["overcoming"].get(elements[i]) == elements[i + 1]:
                        overcoming.append(f"{elements[i]}⊗{elements[i + 1]}")
                
                if generating:
                    result["generating_cycle"] = ", ".join(generating)
                if overcoming:
                    result["overcoming_cycle"] = ", ".join(overcoming)
                
                # Add element balance
                element_count = {}
                for elem in elements:
                    element_count[elem] = element_count.get(elem, 0) + 1
                result["element_balance"] = element_count
        
        # Build full display string
        full_display = " ".join(display_parts)
        
        result["gregorian_date"] = earth_date.strftime("%Y-%m-%d")
        result["gregorian_time"] = earth_date.strftime("%H:%M:%S")
        result["full_display"] = full_display
        
        return result
    
    def update(self) -> None:
        """Update the sensor."""
        now = datetime.now()
        self._sexagesimal_date = self._calculate_sexagesimal_date(now)
        
        # Set state to formatted date
        self._state = self._sexagesimal_date.get("full_display", "Unknown")
        
        _LOGGER.debug(f"Updated Sexagesimal Calendar to {self._state}")