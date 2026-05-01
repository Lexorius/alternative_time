"""Old English Calendar (Lady Day) implementation - Version 1.0.

Historical English calendar where the year began on March 25 (Lady Day).
Used in England from 1155 to 1752 before the Gregorian calendar reform.
"""
from __future__ import annotations

import logging
from datetime import date, datetime
from typing import Any, Dict, Optional

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
    "id": "old_english",
    "version": "1.0.0",
    "icon": "mdi:crown",
    "category": "historical",
    "accuracy": "historical",
    "update_interval": UPDATE_INTERVAL,

    # Multi-language names
    "name": {
        "en": "Old English Calendar",
        "de": "Altenglischer Kalender",
        "es": "Calendario Inglés Antiguo",
        "fr": "Calendrier Anglais Ancien",
        "it": "Calendario Inglese Antico",
        "nl": "Oud-Engelse Kalender",
        "pl": "Stary Kalendarz Angielski",
        "pt": "Calendário Inglês Antigo",
        "ru": "Староанглийский календарь",
        "ja": "古英語暦",
        "zh": "古英语历法",
        "ko": "고대 영어 달력"
    },

    # Short descriptions for UI
    "description": {
        "en": "Historical English calendar with year starting on Lady Day (March 25), used 1155-1752",
        "de": "Historischer englischer Kalender mit Jahresbeginn am Lady Day (25. März), verwendet 1155-1752",
        "es": "Calendario histórico inglés con año comenzando en Lady Day (25 de marzo), usado 1155-1752",
        "fr": "Calendrier historique anglais avec année commençant à Lady Day (25 mars), utilisé 1155-1752",
        "it": "Calendario storico inglese con anno che inizia il Lady Day (25 marzo), usato 1155-1752",
        "nl": "Historische Engelse kalender met jaar beginnend op Lady Day (25 maart), gebruikt 1155-1752",
        "pl": "Historyczny kalendarz angielski z rokiem zaczynającym się w Lady Day (25 marca), używany 1155-1752",
        "pt": "Calendário histórico inglês com ano começando no Lady Day (25 de março), usado 1155-1752",
        "ru": "Исторический английский календарь с началом года в День Леди (25 марта), использовался 1155-1752",
        "ja": "レディ・デイ（3月25日）に年が始まる歴史的な英語暦、1155-1752年使用",
        "zh": "历史英语日历，年从圣母领报节（3月25日）开始，使用于1155-1752年",
        "ko": "레이디 데이(3월 25일)에 연도가 시작되는 역사적 영어 달력, 1155-1752년 사용"
    },

    # Detailed information for documentation
    "detailed_info": {
        "en": {
            "overview": "The Old English Calendar used Lady Day (March 25) as New Year's Day from 1155 until 1752",
            "lady_day": "Lady Day commemorates the Annunciation - when the angel Gabriel told Mary she would bear Jesus",
            "quarter_days": "Quarter Days were key dates for rent, contracts, and employment: Lady Day, Midsummer, Michaelmas, Christmas",
            "dual_dating": "Between January 1 and March 24, dates were often written with both years (e.g., 1660/61)",
            "reform": "The Calendar (New Style) Act 1750 moved New Year to January 1 and adopted the Gregorian calendar in 1752",
            "tax_year": "The UK tax year still ends on April 5 (Old Lady Day), a vestige of this calendar"
        },
        "de": {
            "overview": "Der altenglische Kalender verwendete Lady Day (25. März) als Neujahrstag von 1155 bis 1752",
            "lady_day": "Lady Day erinnert an die Verkündigung - als der Engel Gabriel Maria verkündete, dass sie Jesus gebären würde",
            "quarter_days": "Quartalstage waren wichtige Termine für Miete, Verträge und Beschäftigung: Lady Day, Midsummer, Michaelmas, Christmas",
            "dual_dating": "Zwischen dem 1. Januar und dem 24. März wurden Daten oft mit beiden Jahren geschrieben (z.B. 1660/61)",
            "reform": "Der Calendar (New Style) Act 1750 verlegte Neujahr auf den 1. Januar und übernahm 1752 den Gregorianischen Kalender",
            "tax_year": "Das britische Steuerjahr endet immer noch am 5. April (Old Lady Day), ein Überbleibsel dieses Kalenders"
        }
    },

    # Old English Calendar specific data
    "old_english_data": {
        # Quarter Days (key dates in the English calendar year)
        "quarter_days": {
            "lady_day": {
                "date": (3, 25),
                "name": {
                    "en": "Lady Day",
                    "de": "Mariä Verkündigung",
                    "es": "Día de la Anunciación",
                    "fr": "Jour de l'Annonciation",
                    "it": "Giorno dell'Annunciazione",
                    "nl": "Maria-Boodschap",
                    "pl": "Dzień Zwiastowania",
                    "pt": "Dia da Anunciação",
                    "ru": "День Благовещения",
                    "ja": "聖母マリアの日",
                    "zh": "圣母领报节",
                    "ko": "성모 영보 대축일"
                },
                "meaning": "New Year's Day / Feast of the Annunciation",
                "emoji": "👑"
            },
            "midsummer": {
                "date": (6, 24),
                "name": {
                    "en": "Midsummer Day",
                    "de": "Johannistag",
                    "es": "Día de San Juan",
                    "fr": "Fête de la Saint-Jean",
                    "it": "Festa di San Giovanni",
                    "nl": "Midzomerdag",
                    "pl": "Dzień Świętego Jana",
                    "pt": "Dia de São João",
                    "ru": "Иванов день",
                    "ja": "真夏の日",
                    "zh": "仲夏节",
                    "ko": "한여름날"
                },
                "meaning": "Feast of St John the Baptist",
                "emoji": "☀️"
            },
            "michaelmas": {
                "date": (9, 29),
                "name": {
                    "en": "Michaelmas",
                    "de": "Michaelistag",
                    "es": "San Miguel",
                    "fr": "Saint-Michel",
                    "it": "San Michele",
                    "nl": "Sint-Michielsdag",
                    "pl": "Święto Świętego Michała",
                    "pt": "São Miguel",
                    "ru": "Михайлов день",
                    "ja": "ミカエル祭",
                    "zh": "米迦勒节",
                    "ko": "미카엘 축일"
                },
                "meaning": "Feast of St Michael and All Angels",
                "emoji": "⚔️"
            },
            "christmas": {
                "date": (12, 25),
                "name": {
                    "en": "Christmas Day",
                    "de": "Weihnachten",
                    "es": "Navidad",
                    "fr": "Noël",
                    "it": "Natale",
                    "nl": "Kerstmis",
                    "pl": "Boże Narodzenie",
                    "pt": "Natal",
                    "ru": "Рождество",
                    "ja": "クリスマス",
                    "zh": "圣诞节",
                    "ko": "크리스마스"
                },
                "meaning": "Feast of the Nativity",
                "emoji": "🎄"
            }
        },

        # Old Lady Day (after 1752 calendar reform)
        "old_lady_day": {
            "date": (4, 5),
            "name": "Old Lady Day",
            "meaning": "Lady Day adjusted for the 11 lost days of 1752 calendar reform"
        },

        # English months
        "months": [
            {"english": "January", "latin": "Januarius"},
            {"english": "February", "latin": "Februarius"},
            {"english": "March", "latin": "Martius"},
            {"english": "April", "latin": "Aprilis"},
            {"english": "May", "latin": "Maius"},
            {"english": "June", "latin": "Junius"},
            {"english": "July", "latin": "Julius"},
            {"english": "August", "latin": "Augustus"},
            {"english": "September", "latin": "September"},
            {"english": "October", "latin": "October"},
            {"english": "November", "latin": "November"},
            {"english": "December", "latin": "December"}
        ],

        # Historical events by date (month, day)
        "historical_events": {
            (1, 30): "👑 Execution of King Charles I (1649)",
            (2, 6): "👑 Accession of Queen Elizabeth II (1952)",
            (3, 25): "🎊 Lady Day - New Year's Day (Old Style)",
            (4, 5): "📋 Old Lady Day - UK Tax Year ends",
            (4, 6): "📋 UK Tax Year begins",
            (4, 21): "👑 Birthday of Queen Elizabeth II (1926)",
            (4, 23): "🏴󠁧󠁢󠁥󠁮󠁧󠁿 St George's Day",
            (5, 29): "👑 Restoration of King Charles II (1660)",
            (6, 15): "📜 Magna Carta sealed (1215)",
            (6, 24): "☀️ Midsummer Day",
            (7, 4): "🔔 American Independence (1776)",
            (9, 2): "🔥 Great Fire of London began (1666)",
            (9, 14): "📅 Gregorian Calendar adopted in Britain (1752)",
            (9, 29): "⚔️ Michaelmas",
            (10, 31): "🎃 All Hallows' Eve",
            (11, 5): "🎆 Guy Fawkes Night (Gunpowder Plot 1605)",
            (12, 25): "🎄 Christmas Day"
        },

        # English monarchs for regnal years (simplified list)
        "monarchs": [
            {"name": "William I", "start": 1066, "end": 1087, "house": "Norman"},
            {"name": "Henry II", "start": 1154, "end": 1189, "house": "Plantagenet"},
            {"name": "Richard I", "start": 1189, "end": 1199, "house": "Plantagenet"},
            {"name": "John", "start": 1199, "end": 1216, "house": "Plantagenet"},
            {"name": "Henry III", "start": 1216, "end": 1272, "house": "Plantagenet"},
            {"name": "Edward I", "start": 1272, "end": 1307, "house": "Plantagenet"},
            {"name": "Edward II", "start": 1307, "end": 1327, "house": "Plantagenet"},
            {"name": "Edward III", "start": 1327, "end": 1377, "house": "Plantagenet"},
            {"name": "Richard II", "start": 1377, "end": 1399, "house": "Plantagenet"},
            {"name": "Henry IV", "start": 1399, "end": 1413, "house": "Lancaster"},
            {"name": "Henry V", "start": 1413, "end": 1422, "house": "Lancaster"},
            {"name": "Henry VI", "start": 1422, "end": 1461, "house": "Lancaster"},
            {"name": "Edward IV", "start": 1461, "end": 1483, "house": "York"},
            {"name": "Richard III", "start": 1483, "end": 1485, "house": "York"},
            {"name": "Henry VII", "start": 1485, "end": 1509, "house": "Tudor"},
            {"name": "Henry VIII", "start": 1509, "end": 1547, "house": "Tudor"},
            {"name": "Edward VI", "start": 1547, "end": 1553, "house": "Tudor"},
            {"name": "Mary I", "start": 1553, "end": 1558, "house": "Tudor"},
            {"name": "Elizabeth I", "start": 1558, "end": 1603, "house": "Tudor"},
            {"name": "James I", "start": 1603, "end": 1625, "house": "Stuart"},
            {"name": "Charles I", "start": 1625, "end": 1649, "house": "Stuart"},
            {"name": "Interregnum", "start": 1649, "end": 1660, "house": "Commonwealth"},
            {"name": "Charles II", "start": 1660, "end": 1685, "house": "Stuart"},
            {"name": "James II", "start": 1685, "end": 1688, "house": "Stuart"},
            {"name": "William III & Mary II", "start": 1689, "end": 1702, "house": "Stuart/Orange"},
            {"name": "Anne", "start": 1702, "end": 1714, "house": "Stuart"},
            {"name": "George I", "start": 1714, "end": 1727, "house": "Hanover"},
            {"name": "George II", "start": 1727, "end": 1760, "house": "Hanover"},
            {"name": "George III", "start": 1760, "end": 1820, "house": "Hanover"},
            {"name": "George IV", "start": 1820, "end": 1830, "house": "Hanover"},
            {"name": "William IV", "start": 1830, "end": 1837, "house": "Hanover"},
            {"name": "Victoria", "start": 1837, "end": 1901, "house": "Hanover"},
            {"name": "Edward VII", "start": 1901, "end": 1910, "house": "Saxe-Coburg-Gotha"},
            {"name": "George V", "start": 1910, "end": 1936, "house": "Windsor"},
            {"name": "Edward VIII", "start": 1936, "end": 1936, "house": "Windsor"},
            {"name": "George VI", "start": 1936, "end": 1952, "house": "Windsor"},
            {"name": "Elizabeth II", "start": 1952, "end": 2022, "house": "Windsor"},
            {"name": "Charles III", "start": 2022, "end": None, "house": "Windsor"}
        ],

        # Days until next quarter day labels
        "countdown_labels": {
            "en": "days until",
            "de": "Tage bis",
            "es": "días hasta",
            "fr": "jours jusqu'à",
            "it": "giorni fino a",
            "nl": "dagen tot",
            "pl": "dni do",
            "pt": "dias até",
            "ru": "дней до",
            "ja": "日まで",
            "zh": "天到",
            "ko": "일까지"
        }
    },

    # Additional metadata
    "reference_url": "https://en.wikipedia.org/wiki/Lady_Day",
    "documentation_url": "https://en.wikipedia.org/wiki/Old_Style_and_New_Style_dates",
    "origin": "Kingdom of England",
    "created_by": "English legal tradition",
    "period": "1155-1752 CE",

    # Example format
    "example": "15 January 1660/61 (Old Style)",
    "example_meaning": "15th of January, year 1660 (Old Style) or 1661 (New Style)",

    # Related calendars
    "related": ["julian", "roman", "gregorian"],

    # Tags for searching and filtering
    "tags": [
        "historical", "english", "british", "lady_day", "quarter_day",
        "tudor", "stuart", "medieval", "julian", "old_style", "tax_year"
    ],

    # Special features
    "features": {
        "dual_dating": True,
        "quarter_days": True,
        "regnal_years": True,
        "historical_events": True,
        "tax_year_calculation": True,
        "precision": "day"
    },

    # Configuration options
    "config_options": {
        "show_dual_date": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show Dual Dating",
                "de": "Doppeldatierung anzeigen",
                "es": "Mostrar fecha doble",
                "fr": "Afficher double datation",
                "it": "Mostra doppia datazione",
                "nl": "Dubbele datering tonen",
                "pl": "Pokaż podwójną datę",
                "pt": "Mostrar datação dupla",
                "ru": "Показать двойную датировку",
                "ja": "二重日付を表示",
                "zh": "显示双重日期",
                "ko": "이중 날짜 표시"
            },
            "description": {
                "en": "Show both Old Style and New Style years between Jan 1 and Mar 24",
                "de": "Zeige beide Jahre (Alt- und Neustil) zwischen 1. Jan und 24. März"
            }
        },
        "show_regnal_year": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show Regnal Year",
                "de": "Regierungsjahr anzeigen",
                "es": "Mostrar año de reinado",
                "fr": "Afficher année de règne",
                "it": "Mostra anno di regno",
                "nl": "Regeringsjaar tonen",
                "pl": "Pokaż rok panowania",
                "pt": "Mostrar ano de reinado",
                "ru": "Показать год правления",
                "ja": "治世年を表示",
                "zh": "显示统治年",
                "ko": "재위 연도 표시"
            },
            "description": {
                "en": "Display the regnal year of the current monarch",
                "de": "Zeige das Regierungsjahr des aktuellen Monarchen"
            }
        },
        "show_quarter_days": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show Quarter Days",
                "de": "Quartalstage anzeigen",
                "es": "Mostrar días cuartos",
                "fr": "Afficher jours de quartier",
                "it": "Mostra giorni di trimestre",
                "nl": "Kwartaaldagen tonen",
                "pl": "Pokaż dni kwartalne",
                "pt": "Mostrar dias de trimestre",
                "ru": "Показать квартальные дни",
                "ja": "四半期の日を表示",
                "zh": "显示季度日",
                "ko": "분기일 표시"
            },
            "description": {
                "en": "Show countdown to next quarter day",
                "de": "Zeige Countdown zum nächsten Quartalstag"
            }
        },
        "show_events": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show Historical Events",
                "de": "Historische Ereignisse anzeigen",
                "es": "Mostrar eventos históricos",
                "fr": "Afficher événements historiques",
                "it": "Mostra eventi storici",
                "nl": "Historische gebeurtenissen tonen",
                "pl": "Pokaż wydarzenia historyczne",
                "pt": "Mostrar eventos históricos",
                "ru": "Показать исторические события",
                "ja": "歴史的イベントを表示",
                "zh": "显示历史事件",
                "ko": "역사적 사건 표시"
            },
            "description": {
                "en": "Display notable historical events for the current date",
                "de": "Zeige bedeutende historische Ereignisse für das aktuelle Datum"
            }
        },
        "year_style": {
            "type": "select",
            "default": "old_style",
            "options": ["old_style", "new_style", "both"],
            "label": {
                "en": "Year Style",
                "de": "Jahresstil",
                "es": "Estilo de año",
                "fr": "Style d'année",
                "it": "Stile anno",
                "nl": "Jaarstijl",
                "pl": "Styl roku",
                "pt": "Estilo de ano",
                "ru": "Стиль года",
                "ja": "年スタイル",
                "zh": "年份风格",
                "ko": "연도 스타일"
            },
            "description": {
                "en": "Choose Old Style (year starts March 25), New Style (year starts January 1), or both",
                "de": "Wähle Altstil (Jahr beginnt 25. März), Neustil (Jahr beginnt 1. Januar) oder beide"
            }
        }
    }
}


# ============================================
# SENSOR CLASS
# ============================================

class OldEnglishCalendarSensor(AlternativeTimeSensorBase):
    """Sensor for displaying Old English Calendar (Lady Day) dates."""

    # Class-level update interval
    UPDATE_INTERVAL = UPDATE_INTERVAL

    def __init__(self, base_name: str, hass: HomeAssistant) -> None:
        """Initialize the Old English calendar sensor."""
        super().__init__(base_name, hass)

        # Set sensor-specific attributes
        calendar_name = self._translate('name') or "Old English Calendar"
        self._attr_name = f"{base_name} {calendar_name}"
        self._attr_unique_id = f"{base_name}_old_english_calendar"
        self._attr_icon = CALENDAR_INFO["icon"]

        # State data
        self._old_english_date = {}

        # Configuration options (defaults)
        self._show_dual_date = True
        self._show_regnal_year = True
        self._show_quarter_days = True
        self._show_events = True
        self._year_style = "old_style"

        # Calendar data reference
        self._old_english_data = CALENDAR_INFO.get("old_english_data", {})

        # Options loaded flag
        self._options_loaded = False

    def _load_options(self) -> None:
        """Load configuration options from config entry."""
        if self._options_loaded:
            return

        try:
            options = self.get_plugin_options()

            if options:
                self._show_dual_date = options.get("show_dual_date", self._show_dual_date)
                self._show_regnal_year = options.get("show_regnal_year", self._show_regnal_year)
                self._show_quarter_days = options.get("show_quarter_days", self._show_quarter_days)
                self._show_events = options.get("show_events", self._show_events)
                self._year_style = options.get("year_style", self._year_style)

                _LOGGER.debug(f"Old English sensor loaded options: dual={self._show_dual_date}, "
                            f"regnal={self._show_regnal_year}, quarter={self._show_quarter_days}, "
                            f"events={self._show_events}, style={self._year_style}")
            else:
                _LOGGER.debug("Old English sensor using default options")

            self._options_loaded = True
        except Exception as e:
            _LOGGER.debug(f"Old English sensor could not load options: {e}")

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        await super().async_added_to_hass()
        self._load_options()

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes."""
        attrs = super().extra_state_attributes

        if self._old_english_date:
            attrs.update(self._old_english_date)

            # Add description in user's language
            attrs["description"] = self._translate('description')

            # Add reference
            attrs["reference"] = CALENDAR_INFO.get('reference_url', '')

            # Add configuration status
            attrs["config"] = {
                "show_dual_date": self._show_dual_date,
                "show_regnal_year": self._show_regnal_year,
                "show_quarter_days": self._show_quarter_days,
                "show_events": self._show_events,
                "year_style": self._year_style
            }

        return attrs

    def _get_old_style_year(self, dt: datetime) -> int:
        """Calculate the Old Style year (year starts March 25).

        In Old Style:
        - March 25 to December 31 = same as modern year
        - January 1 to March 24 = modern year - 1
        """
        if dt.month < 3 or (dt.month == 3 and dt.day < 25):
            return dt.year - 1
        return dt.year

    def _is_dual_date_period(self, dt: datetime) -> bool:
        """Check if the date falls in the dual dating period (Jan 1 - Mar 24)."""
        return dt.month < 3 or (dt.month == 3 and dt.day < 25)

    def _format_dual_date(self, dt: datetime) -> str:
        """Format the year with dual dating (e.g., 1660/61)."""
        if self._is_dual_date_period(dt):
            old_year = dt.year - 1
            new_year = dt.year
            # Format: 1660/61
            return f"{old_year}/{str(new_year)[-2:]}"
        return str(dt.year)

    def _get_current_monarch(self, year: int) -> Optional[Dict[str, Any]]:
        """Get the monarch for the given year."""
        monarchs = self._old_english_data.get("monarchs", [])

        for monarch in monarchs:
            start = monarch["start"]
            end = monarch["end"]

            if end is None:  # Current monarch
                if year >= start:
                    return monarch
            elif start <= year <= end:
                return monarch

        return None

    def _calculate_regnal_year(self, dt: datetime) -> Optional[Dict[str, Any]]:
        """Calculate the regnal year for the current date."""
        monarch = self._get_current_monarch(dt.year)

        if not monarch:
            return None

        regnal_year = dt.year - monarch["start"] + 1

        return {
            "monarch": monarch["name"],
            "house": monarch["house"],
            "regnal_year": regnal_year,
            "formatted": f"{regnal_year} {monarch['name']}"
        }

    def _get_quarter_day_info(self, dt: datetime, lang: str = "en") -> Dict[str, Any]:
        """Get information about quarter days."""
        quarter_days = self._old_english_data.get("quarter_days", {})
        current_date = (dt.month, dt.day)

        # Check if today is a quarter day
        current_quarter = None
        for key, qd in quarter_days.items():
            if qd["date"] == current_date:
                name = qd["name"].get(lang, qd["name"].get("en", key))
                current_quarter = {
                    "name": name,
                    "meaning": qd["meaning"],
                    "emoji": qd["emoji"]
                }
                break

        # Calculate days until next quarter day
        quarter_dates = [
            ((3, 25), "lady_day"),
            ((6, 24), "midsummer"),
            ((9, 29), "michaelmas"),
            ((12, 25), "christmas")
        ]

        today = date(dt.year, dt.month, dt.day)
        next_quarter = None
        days_until = None

        for qd_date, qd_key in quarter_dates:
            qd_this_year = date(dt.year, qd_date[0], qd_date[1])
            if qd_this_year > today:
                delta = (qd_this_year - today).days
                next_quarter = quarter_days[qd_key]
                days_until = delta
                break

        # If no quarter day found this year, get first one next year
        if next_quarter is None:
            qd_next_year = date(dt.year + 1, 3, 25)  # Lady Day next year
            delta = (qd_next_year - today).days
            next_quarter = quarter_days["lady_day"]
            days_until = delta

        next_name = next_quarter["name"].get(lang, next_quarter["name"].get("en", ""))
        countdown_label = self._old_english_data.get("countdown_labels", {}).get(lang, "days until")

        return {
            "current_quarter_day": current_quarter,
            "next_quarter_day": next_name,
            "days_until_next": days_until,
            "countdown": f"{days_until} {countdown_label} {next_name}"
        }

    def _get_historical_event(self, dt: datetime) -> Optional[str]:
        """Get historical event for the current date."""
        events = self._old_english_data.get("historical_events", {})
        return events.get((dt.month, dt.day))

    def _get_season_info(self, dt: datetime) -> Dict[str, Any]:
        """Get season information based on quarter days."""
        month = dt.month
        day = dt.day

        # Seasons based on quarter days
        if (month == 3 and day >= 25) or month in [4, 5] or (month == 6 and day < 24):
            season = "Spring"
            emoji = "🌸"
        elif (month == 6 and day >= 24) or month in [7, 8] or (month == 9 and day < 29):
            season = "Summer"
            emoji = "☀️"
        elif (month == 9 and day >= 29) or month in [10, 11] or (month == 12 and day < 25):
            season = "Autumn"
            emoji = "🍂"
        else:
            season = "Winter"
            emoji = "❄️"

        return {"season": season, "emoji": emoji}

    def _is_tax_year_relevant(self, dt: datetime) -> Optional[Dict[str, Any]]:
        """Check if the date is relevant to the UK tax year."""
        if dt.month == 4 and dt.day == 5:
            return {
                "event": "Old Lady Day",
                "meaning": "UK Tax Year ends",
                "emoji": "📋"
            }
        elif dt.month == 4 and dt.day == 6:
            return {
                "event": "UK Tax Year begins",
                "meaning": "First day of new UK tax year",
                "emoji": "📋"
            }
        return None

    def _ordinal(self, n: int) -> str:
        """Convert number to ordinal (1st, 2nd, 3rd, etc.)."""
        if 11 <= (n % 100) <= 13:
            suffix = 'th'
        else:
            suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
        return f"{n}{suffix}"

    def _calculate_old_english_date(self, earth_date: datetime) -> Dict[str, Any]:
        """Calculate Old English calendar date."""

        # Load options if not already loaded
        self._load_options()

        # Get language
        lang = getattr(self._hass.config, "language", "en")
        if "-" in lang:
            lang = lang.split("-")[0]
        elif "_" in lang:
            lang = lang.split("_")[0]

        # Calculate years
        new_style_year = earth_date.year
        old_style_year = self._get_old_style_year(earth_date)

        # Determine which year to display
        is_dual_period = self._is_dual_date_period(earth_date)

        if self._year_style == "old_style":
            display_year = str(old_style_year)
        elif self._year_style == "new_style":
            display_year = str(new_style_year)
        else:  # both
            if is_dual_period:
                display_year = self._format_dual_date(earth_date)
            else:
                display_year = str(new_style_year)

        # Get month name
        month_data = self._old_english_data["months"][earth_date.month - 1]
        month_name = month_data["english"]

        # Get day ordinal
        day_ordinal = self._ordinal(earth_date.day)

        # Format the date
        if is_dual_period and self._show_dual_date:
            formatted_date = f"{day_ordinal} {month_name} {display_year} (Old Style)"
        else:
            formatted_date = f"{day_ordinal} {month_name} {display_year}"

        result = {
            "formatted": formatted_date,
            "day": earth_date.day,
            "day_ordinal": day_ordinal,
            "month": month_name,
            "month_number": earth_date.month,
            "old_style_year": old_style_year,
            "new_style_year": new_style_year,
            "display_year": display_year,
            "is_dual_date_period": is_dual_period,
            "gregorian_date": earth_date.strftime("%Y-%m-%d")
        }

        # Add season info
        season_info = self._get_season_info(earth_date)
        result["season"] = season_info["season"]
        result["season_emoji"] = season_info["emoji"]

        # Add regnal year if configured
        if self._show_regnal_year:
            regnal = self._calculate_regnal_year(earth_date)
            if regnal:
                result["regnal_year"] = regnal["regnal_year"]
                result["monarch"] = regnal["monarch"]
                result["royal_house"] = regnal["house"]
                result["regnal_formatted"] = regnal["formatted"]

        # Add quarter day info if configured
        if self._show_quarter_days:
            quarter_info = self._get_quarter_day_info(earth_date, lang)
            if quarter_info["current_quarter_day"]:
                result["is_quarter_day"] = True
                result["quarter_day_name"] = quarter_info["current_quarter_day"]["name"]
                result["quarter_day_meaning"] = quarter_info["current_quarter_day"]["meaning"]
                result["quarter_day_emoji"] = quarter_info["current_quarter_day"]["emoji"]
            else:
                result["is_quarter_day"] = False

            result["next_quarter_day"] = quarter_info["next_quarter_day"]
            result["days_until_quarter_day"] = quarter_info["days_until_next"]
            result["quarter_day_countdown"] = quarter_info["countdown"]

        # Add historical event if configured
        if self._show_events:
            event = self._get_historical_event(earth_date)
            if event:
                result["historical_event"] = event

            # Check for tax year relevance
            tax_info = self._is_tax_year_relevant(earth_date)
            if tax_info:
                result["tax_year_event"] = tax_info["event"]
                result["tax_year_meaning"] = tax_info["meaning"]

        # Add information about Lady Day
        if earth_date.month == 3 and earth_date.day == 25:
            result["special_day"] = "Lady Day"
            result["special_meaning"] = "New Year's Day (Old Style)"
            result["lady_day_info"] = "The Feast of the Annunciation - New Year began on this day from 1155 to 1752"

        # Calculate days until/since Lady Day (New Year)
        this_year_lady_day = date(earth_date.year, 3, 25)
        today = date(earth_date.year, earth_date.month, earth_date.day)

        if today < this_year_lady_day:
            days_to_new_year = (this_year_lady_day - today).days
            result["days_until_old_new_year"] = days_to_new_year
        else:
            days_since_new_year = (today - this_year_lady_day).days
            result["days_since_old_new_year"] = days_since_new_year
            result["old_style_day_of_year"] = days_since_new_year + 1

        return result

    def update(self) -> None:
        """Update the sensor."""
        now = datetime.now()
        self._old_english_date = self._calculate_old_english_date(now)

        # Set state to formatted date
        self._state = self._old_english_date["formatted"]

        _LOGGER.debug(f"Updated Old English Calendar to {self._state}")
