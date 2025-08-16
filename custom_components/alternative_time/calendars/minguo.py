"""Minguo Calendar (Republic of China/Taiwan) implementation."""
from __future__ import annotations

from datetime import datetime
import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)


class MinguoCalendarSensor(SensorEntity):
    """Sensor for displaying Minguo Calendar (Taiwan/ROC)."""

    def __init__(self, base_name: str) -> None:
        """Initialize the Minguo calendar sensor."""
        self._attr_name = f"{base_name} Minguo Calendar"
        self._attr_unique_id = f"{base_name}_minguo_calendar"
        self._attr_icon = "mdi:calendar-text"
        self._state = None

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        now = datetime.now()
        minguo_year = now.year - 1911
        
        # Month names in Traditional Chinese
        chinese_months = [
            "一月", "二月", "三月", "四月", "五月", "六月",
            "七月", "八月", "九月", "十月", "十一月", "十二月"
        ]
        
        # Weekday names in Traditional Chinese
        chinese_weekdays = [
            "星期一", "星期二", "星期三", "星期四", 
            "星期五", "星期六", "星期日"
        ]
        
        month_chinese = chinese_months[now.month - 1]
        weekday_chinese = chinese_weekdays[now.weekday()]
        
        # Determine era name
        if minguo_year > 0:
            era = "民國"  # Republic Era
            display_year = minguo_year
        else:
            era = "民前"  # Before Republic
            display_year = abs(minguo_year - 1)
        
        # Check for important dates in ROC calendar
        special_day = ""
        if now.month == 1 and now.day == 1:
            special_day = " 🎊 中華民國開國紀念日"  # Founding Day
        elif now.month == 2 and now.day == 28:
            special_day = " 🕊️ 和平紀念日"  # Peace Memorial Day
        elif now.month == 10 and now.day == 10:
            special_day = " 🇹🇼 國慶日"  # National Day
        elif now.month == 10 and now.day == 25:
            special_day = " 🎌 臺灣光復節"  # Retrocession Day
        
        return {
            "year": display_year,
            "era": era,
            "month": now.month,
            "month_chinese": month_chinese,
            "day": now.day,
            "weekday": weekday_chinese,
            "gregorian_year": now.year,
            "full_date_chinese": f"{era}{display_year}年{month_chinese}{now.day}日",
            "full_date_numeric": f"{era} {display_year}/{now.month:02d}/{now.day:02d}",
            "special_day": special_day.strip(),
            "time": now.strftime("%H:%M:%S"),
        }

    def update(self) -> None:
        """Update the sensor."""
        now = datetime.now()
        minguo_year = now.year - 1911
        
        if minguo_year > 0:
            era = "民國"
            display_year = minguo_year
        else:
            era = "民前"
            display_year = abs(minguo_year - 1)
        
        # Format: Era Year/Month/Day
        self._state = f"{era} {display_year}年{now.month}月{now.day}日"