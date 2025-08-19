
"""Trackmania Events (COTD, Weekly Shorts, Bonk Cup) - Version 1.1 with extended translations."""
from __future__ import annotations

from datetime import datetime, timedelta
import logging
from typing import Dict, Any, List
try:
    from zoneinfo import ZoneInfo  # Python 3.9+
except Exception:  # pragma: no cover
    ZoneInfo = None  # type: ignore

from homeassistant.core import HomeAssistant
from ..sensor import AlternativeTimeSensorBase

_LOGGER = logging.getLogger(__name__)

# ============================================
# CALENDAR METADATA
# ============================================

UPDATE_INTERVAL = 60  # seconds

CALENDAR_INFO = {
    "id": "trackmania",
    "version": "1.1.0",
    "icon": "mdi:flag-checkered",
    "category": "gaming",
    "accuracy": "official/community",
    "update_interval": UPDATE_INTERVAL,

    # Multi-language names (aligned with other calendars in this repo)
    "name": {
        "en": "Trackmania Events",
        "de": "Trackmania Events",
        "es": "Eventos de Trackmania",
        "fr": "Événements Trackmania",
        "it": "Eventi di Trackmania",
        "nl": "Trackmania-evenementen",
        "pt": "Eventos de Trackmania",
        "ru": "События Trackmania",
        "ja": "トラックマニアのイベント",
        "zh": "Trackmania 活动",
        "ko": "트랙매니아 이벤트"
    },

    # Short descriptions for UI
    "description": {
        "en": "Shows next start times for Cup of the Day (03:00 / 11:00 / 19:00 CE(S)T), Weekly Shorts (Sun 18:00), and Bonk Cup (Thu 20:00).",
        "de": "Zeigt die nächsten Startzeiten für Cup of the Day (03:00 / 11:00 / 19:00 ME(S)Z), Weekly Shorts (So 18:00) und Bonk Cup (Do 20:00).",
        "es": "Muestra los próximos inicios de Cup of the Day (03:00 / 11:00 / 19:00 CE(S)T), Weekly Shorts (dom 18:00) y Bonk Cup (jue 20:00).",
        "fr": "Affiche les prochains horaires de Cup of the Day (03:00 / 11:00 / 19:00 CE(S)T), Weekly Shorts (dim 18:00) et Bonk Cup (jeu 20:00).",
        "it": "Mostra i prossimi orari per Cup of the Day (03:00 / 11:00 / 19:00 CE(S)T), Weekly Shorts (dom 18:00) e Bonk Cup (gio 20:00).",
        "nl": "Toont de volgende tijden voor Cup of the Day (03:00 / 11:00 / 19:00 CE(S)T), Weekly Shorts (zo 18:00) en Bonk Cup (do 20:00).",
        "pt": "Mostra os próximos horários de Cup of the Day (03:00 / 11:00 / 19:00 CE(S)T), Weekly Shorts (dom 18:00) e Bonk Cup (qui 20:00).",
        "ru": "Показывает ближайшие старты Cup of the Day (03:00 / 11:00 / 19:00 CE(S)T), Weekly Shorts (вс 18:00) и Bonk Cup (чт 20:00).",
        "ja": "Cup of the Day（03:00 / 11:00 / 19:00 CE(S)T）、Weekly Shorts（日曜18:00）、Bonk Cup（木曜20:00）の次回開始時刻を表示します。",
        "zh": "显示 Cup of the Day（每天 03:00 / 11:00 / 19:00 CE(S)T）、Weekly Shorts（周日 18:00）和 Bonk Cup（周四 20:00）下一次开始时间。",
        "ko": "Cup of the Day(매일 03:00 / 11:00 / 19:00 CE(S)T), Weekly Shorts(일 18:00), Bonk Cup(목 20:00)의 다음 시작 시간을 표시합니다."
    },

    # Sources (for reference only in attributes)
    "sources": {
        "cotd_doc": "https://doc.trackmania.com/play/how-to-play-cotd/",
        "weekly_shorts_guidelines": "https://doc.trackmania.com/create/map-review/weekly-shorts-guidelines/"
    },

    # Configuration options with multi-language descriptions
    "config_options": {
        "timezone": {
            "type": "text",
            "default": "Europe/Berlin",
            "description": {
                "en": "IANA timezone to compute local event times",
                "de": "IANA-Zeitzone zur Berechnung lokaler Zeiten",
                "es": "Zona horaria IANA para calcular los horarios locales",
                "fr": "Fuseau horaire IANA pour calculer les heures locales",
                "it": "Fuso orario IANA per calcolare gli orari locali",
                "nl": "IANA-tijdzone voor lokale tijden",
                "pt": "Fuso horário IANA para horários locais",
                "ru": "Часовой пояс IANA для расчёта местного времени",
                "ja": "ローカル時間計算に使用する IANA タイムゾーン",
                "zh": "用于计算本地时间的 IANA 时区",
                "ko": "로컬 시간 계산에 사용할 IANA 표준 시간대"
            }
        },
        "enable_cotd": {
            "type": "boolean",
            "default": True,
            "description": {
                "en": "Enable Cup of the Day",
                "de": "Cup of the Day aktivieren",
                "es": "Activar Cup of the Day",
                "fr": "Activer Cup of the Day",
                "it": "Abilita Cup of the Day",
                "nl": "Cup of the Day inschakelen",
                "pt": "Ativar Cup of the Day",
                "ru": "Включить Cup of the Day",
                "ja": "Cup of the Day を有効化",
                "zh": "启用 Cup of the Day",
                "ko": "Cup of the Day 활성화"
            }
        },
        "enable_weekly_shorts": {
            "type": "boolean",
            "default": True,
            "description": {
                "en": "Enable Weekly Shorts (release)",
                "de": "Weekly Shorts (Release) aktivieren",
                "es": "Activar Weekly Shorts (lanzamiento)",
                "fr": "Activer Weekly Shorts (publication)",
                "it": "Abilita Weekly Shorts (rilascio)",
                "nl": "Weekly Shorts (release) inschakelen",
                "pt": "Ativar Weekly Shorts (lançamento)",
                "ru": "Включить Weekly Shorts (релиз)",
                "ja": "Weekly Shorts（リリース）を有効化",
                "zh": "启用 Weekly Shorts（发布）",
                "ko": "Weekly Shorts(릴리스) 활성화"
            }
        },
        "enable_bonk_cup": {
            "type": "boolean",
            "default": True,
            "description": {
                "en": "Enable Bonk Cup",
                "de": "Bonk Cup aktivieren",
                "es": "Activar Bonk Cup",
                "fr": "Activer Bonk Cup",
                "it": "Abilita Bonk Cup",
                "nl": "Bonk Cup inschakelen",
                "pt": "Ativar Bonk Cup",
                "ru": "Включить Bonk Cup",
                "ja": "Bonk Cup を有効化",
                "zh": "启用 Bonk Cup",
                "ko": "Bonk Cup 활성화"
            }
        },
        "horizon_days": {
            "type": "number",
            "default": 14,
            "description": {
                "en": "How many days ahead to list events",
                "de": "Wie viele Tage im Voraus Events auflisten",
                "es": "Cuántos días listar por adelantado",
                "fr": "Nombre de jours à l’avance à lister",
                "it": "Quanti giorni in anticipo elencare",
                "nl": "Aantal dagen vooruit om te tonen",
                "pt": "Quantos dias à frente listar",
                "ru": "На сколько дней вперёд показывать события",
                "ja": "何日先までイベントを表示するか",
                "zh": "列出未来多少天的赛事",
                "ko": "며칠 앞까지 이벤트를 표시할지"
            }
        }
    }
}


class TrackmaniaEventsSensor(AlternativeTimeSensorBase):
    """Sensor that lists upcoming Trackmania event times."""

    UPDATE_INTERVAL = UPDATE_INTERVAL  # class-level for HA throttling

    def __init__(self, base_name: str, hass: HomeAssistant) -> None:
        super().__init__(base_name, hass)

        calendar_name = self._translate('name', 'Trackmania Events')

        self._attr_name = f"{base_name} {calendar_name}"
        self._attr_unique_id = f"{base_name}_trackmania_events"
        self._attr_icon = CALENDAR_INFO.get("icon", "mdi:flag-checkered")

        # Options (could later be loaded from config flow)
        self._tz_name = "Europe/Berlin"
        self._enable_cotd = True
        self._enable_weekly_shorts = True
        self._enable_bonk = True
        self._horizon_days = 14

        # Cached attributes
        self._tm_events: Dict[str, Any] = {}

    # -------------------- HA properties --------------------
    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        attrs = super().extra_state_attributes
        if self._tm_events:
            attrs.update(self._tm_events)
            attrs["description"] = self._translate('description')
            attrs["reference"] = CALENDAR_INFO.get("sources", {})
        return attrs

    # -------------------- Helpers --------------------
    def _tz(self):
        if ZoneInfo is not None:
            try:
                return ZoneInfo(self._tz_name)
            except Exception:  # pragma: no cover
                _LOGGER.warning("Invalid tz %s, falling back to Europe/Berlin", self._tz_name)
                return ZoneInfo("Europe/Berlin")
        return None

    def _make_event(self, when: datetime, title: str, tag: str) -> Dict[str, Any]:
        now = datetime.now(when.tzinfo)
        delta = when - now
        seconds = int(delta.total_seconds())
        sign = "" if seconds >= 0 else "-"
        seconds = abs(seconds)
        dh, rem = divmod(seconds, 3600)
        dm, ds = divmod(rem, 60)
        in_h = f"{sign}{dh:02d}:{dm:02d}:{ds:02d}"
        return {
            "title": title,
            "tag": tag,
            "when_local": when.strftime("%Y-%m-%d %H:%M:%S %Z"),
            "when_iso": when.isoformat(),
            "in": in_h
        }

    def _iter_days(self, start: datetime, days: int):
        for i in range(days+1):
            yield (start + timedelta(days=i)).date()

    def _generate_upcoming(self, now: datetime) -> List[Dict[str, Any]]:
        tz = now.tzinfo
        events: List[Dict[str, Any]] = []

        for d in self._iter_days(now, self._horizon_days):
            # Daily COTD times (03:00, 11:00, 19:00 local)
            if self._enable_cotd:
                for hh in (3, 11, 19):
                    when = datetime(d.year, d.month, d.day, hh, 0, 0, tzinfo=tz)
                    if when >= now - timedelta(hours=1):  # include last hour for context
                        events.append(self._make_event(when, "Cup of the Day", "cotd"))

            # Weekly Shorts: Sundays 18:00 local
            if self._enable_weekly_shorts:
                if d.weekday() == 6:  # Sunday
                    when = datetime(d.year, d.month, d.day, 18, 0, 0, tzinfo=tz)
                    if when >= now - timedelta(hours=1):
                        events.append(self._make_event(when, "Weekly Shorts (release)", "weekly_shorts"))

            # Bonk Cup: Thursdays 20:00 local
            if self._enable_bonk:
                if d.weekday() == 3:  # Thursday
                    when = datetime(d.year, d.month, d.day, 20, 0, 0, tzinfo=tz)
                    if when >= now - timedelta(hours=1):
                        events.append(self._make_event(when, "Bonk Cup", "bonk_cup"))

        events.sort(key=lambda e: e["when_iso"])
        return events

    # -------------------- Calculation & update --------------------
    def update(self) -> None:
        try:
            tz = self._tz()
            now = datetime.now(tz)
            upcoming = self._generate_upcoming(now)

            if upcoming:
                next_ev = next((e for e in upcoming if e["when_iso"] >= now.isoformat()), upcoming[0])
                self._tm_events = {
                    "timezone": self._tz_name,
                    "now_local": now.strftime("%Y-%m-%d %H:%M:%S %Z"),
                    "next_event": next_ev,
                    "upcoming_events": upcoming[:20]
                }
                self._state = f"Next: {next_ev['title']} @ {next_ev['when_local']} (in {next_ev['in']})"
            else:
                self._tm_events = {"timezone": self._tz_name, "now_local": now.strftime("%Y-%m-%d %H:%M:%S %Z")}
                self._state = "No events found"
        except Exception as exc:  # pragma: no cover
            _LOGGER.exception("Failed to update Trackmania events: %s", exc)
            self._state = "Error"
