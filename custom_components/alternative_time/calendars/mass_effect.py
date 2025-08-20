"""Mass Effect - Galactic Standard Time & Year
Version 2.5.1 - Mit verbessertem Logging und Fehlerbehandlung
"""
from __future__ import annotations

from datetime import datetime, timezone, timedelta
import logging
from typing import Dict, Any

from homeassistant.core import HomeAssistant
from ..sensor import AlternativeTimeSensorBase

_LOGGER = logging.getLogger(__name__)

UPDATE_INTERVAL = 1  # smooth clock

CALENDAR_INFO = {
    "id": "mass_effect",
    "version": "2.5.1",
    "icon": "mdi:rocket",
    "category": "scifi",
    "accuracy": "fictional",
    "update_interval": UPDATE_INTERVAL,

    "name": {
        "en": "Mass Effect – Galactic Standard",
        "de": "Mass Effect – Galaktischer Standard",
        "es": "Mass Effect – Estándar Galáctico",
        "fr": "Mass Effect – Standard Galactique",
        "it": "Mass Effect – Standard Galattico",
        "nl": "Mass Effect – Galactische Standaard",
        "pt": "Mass Effect – Padrão Galáctico",
        "ru": "Mass Effect – Галактический стандарт",
        "ja": "マスエフェクト – 銀河標準",
        "zh": "质量效应 – 银河标准",
        "ko": "매스 이펙트 – 은하 표준"
    },

    "description": {
        "en": "Shows Galactic Standard Time (GST 20:100:100; 1 GST s = 0.5 s) and optional Galactic Standard Year (GSY) counter.",
        "de": "Zeigt die Galactic Standard Time (GST 20:100:100; 1 GST s = 0,5 s) sowie optional einen Galactic Standard Year (GSY) Zähler.",
        "es": "Muestra el Tiempo Estándar Galáctico (GST 20:100:100; 1 GST s = 0,5 s) y, opcionalmente, el contador del Año Estándar Galáctico (GSY).",
        "fr": "Affiche l'heure standard galactique (GST 20:100:100 ; 1 s GST = 0,5 s) et, en option, le compteur d'année standard galactique (GSY).",
        "it": "Mostra il Tempo Standard Galattico (GST 20:100:100; 1 s GST = 0,5 s) e opzionalmente il contatore dell'Anno Standard Galattico (GSY).",
        "nl": "Toont de Galactic Standard Time (GST 20:100:100; 1 GST s = 0,5 s) en optioneel de Galactic Standard Year (GSY).",
        "pt": "Mostra o Tempo Padrão Galáctico (GST 20:100:100; 1 s GST = 0,5 s) e, opcionalmente, o contador do Ano Padrão Galáctico (GSY).",
        "ru": "Показывает Галактическое стандартное время (GST 20:100:100; 1 с GST = 0,5 с) и опциональный счётчик Галактического стандартного года (GSY).",
        "ja": "銀河標準時 (GST 20:100:100、1 GST 秒 = 0.5 秒) と、オプションの銀河標準年 (GSY) カウンターを表示します。",
        "zh": "显示银河标准时间（GST 20:100:100；1 GST 秒 = 0.5 秒）以及可选的银河标准年（GSY）计数器。",
        "ko": "은하 표준 시간(GST 20:100:100; 1 GST초 = 0.5초)과 선택적인 은하 표준 연도(GSY) 카운터를 표시합니다."
    },

    "sources": {
        "wiki_lore": "https://masseffect.fandom.com/wiki/Galactic_Standard",
    },

    "config_options": {
        "enable_gst": {
            "type": "boolean",
            "default": True,
            "description": { 
                "en": "Show GST clock", 
                "de": "GST-Uhr anzeigen" 
            }
        },
        "precision": {
            "type": "select",
            "default": "second",
            "options": ["second", "centisecond"],
            "description": { 
                "en": "Clock precision", 
                "de": "Uhr-Präzision" 
            }
        },
        "show_period": {
            "type": "boolean",
            "default": True,
            "description": { 
                "en": "Show time period (Night/Morning/etc.)", 
                "de": "Tagesabschnitt anzeigen (Nacht/Morgen/usw.)" 
            }
        },
        "enable_gsy": {
            "type": "boolean",
            "default": False,
            "description": { 
                "en": "Enable GSY counter (approximate)", 
                "de": "GSY-Zähler aktivieren (annähernd)" 
            }
        },
        "epoch_gs0_utc": {
            "type": "text",
            "default": "2183-01-01T00:00:00Z",
            "description": { 
                "en": "Epoch for 0 GSY (UTC ISO-8601)", 
                "de": "Epoche für 0 GSY (UTC ISO-8601)" 
            }
        },
        "gsy_length_days": {
            "type": "number",
            "default": 398.1,
            "description": { 
                "en": "Length of 1 GSY in Earth days (approx.)", 
                "de": "Länge von 1 GSY in Erdtagen (ca.)" 
            }
        }
    }
}


class MassEffectGalacticStandardSensor(AlternativeTimeSensorBase):
    """Sensor for Mass Effect Galactic Standard Time/Year."""

    UPDATE_INTERVAL = UPDATE_INTERVAL

    # Konstanten für GST-Berechnung
    GST_SECONDS_PER_SEC = 2.0  # 1 GST sec = 0.5 Earth sec (=> 2 GST s per Earth s)
    GST_SECONDS_PER_MIN = 100
    GST_MINUTES_PER_HOUR = 100
    GST_HOURS_PER_DAY = 20
    GST_SECONDS_PER_HOUR = GST_SECONDS_PER_MIN * GST_MINUTES_PER_HOUR  # 10,000
    GST_SECONDS_PER_DAY = GST_SECONDS_PER_HOUR * GST_HOURS_PER_DAY     # 200,000

    EARTH_SECONDS_PER_GST_SECOND = 0.5
    EARTH_SECONDS_PER_GST_DAY = GST_SECONDS_PER_DAY * EARTH_SECONDS_PER_GST_SECOND  # 100,000s

    def __init__(self, base_name: str, hass: HomeAssistant) -> None:
        super().__init__(base_name, hass)

        calendar_name = self._translate('name', 'Mass Effect – Galactic Standard')
        self._attr_name = f"{base_name} {calendar_name}"
        self._attr_unique_id = f"{base_name}_mass_effect_gs"
        self._attr_icon = CALENDAR_INFO.get("icon", "mdi:rocket")

        # Defaults (werden in update() überschrieben)
        self._enable_gst = True
        self._precision = "second"
        self._show_period = True
        self._enable_gsy = False
        self._epoch_gs0_utc = "2183-01-01T00:00:00Z"
        self._gsy_length_days = 398.1

        # Daten-Cache
        self._data: Dict[str, Any] = {}
        self._state = "Initializing..."
        
        # Flag für einmaliges Logging
        self._first_update = True

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        attrs = super().extra_state_attributes
        if self._data:
            attrs.update(self._data)
            attrs["description"] = self._translate('description')
            attrs["reference"] = CALENDAR_INFO.get("sources", {})
        return attrs

    # ---------- helpers ----------
    def _parse_epoch(self, txt: str) -> datetime:
        """Parse ISO8601 epoch string to datetime."""
        try:
            if txt.endswith('Z'):
                # strip Z and set tz
                base = txt[:-1]
                dt = datetime.fromisoformat(base)
                return dt.replace(tzinfo=timezone.utc)
            dt = datetime.fromisoformat(txt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except Exception as e:
            _LOGGER.warning("Invalid epoch_gs0_utc '%s': %s, using default 2183-01-01T00:00:00Z", txt, e)
            return datetime(2183, 1, 1, 0, 0, 0, tzinfo=timezone.utc)

    def _format_gst(self, gst_total_seconds: float) -> Dict[str, Any]:
        """Format GST seconds into readable time."""
        # Normalize to [0, day)
        gst_in_day = gst_total_seconds % self.GST_SECONDS_PER_DAY

        h = int(gst_in_day // self.GST_SECONDS_PER_HOUR)
        rem = gst_in_day - h * self.GST_SECONDS_PER_HOUR
        m = int(rem // self.GST_SECONDS_PER_MIN)
        s_float = rem - m * self.GST_SECONDS_PER_MIN
        s = int(s_float)

        # centiseconds (0..99) from fractional GST second
        centi = int((s_float - s) * 100)

        if self._precision == "centisecond":
            formatted = f"{h:02d}:{m:03d}:{s:03d}.{centi:02d} GST"
        else:
            formatted = f"{h:02d}:{m:03d}:{s:03d} GST"

        # period of GS day (rough, 5 equal segments)
        period = ""
        if self._show_period:
            if h < 4:
                period = "Night"
            elif h < 8:
                period = "Dawn"
            elif h < 12:
                period = "Morning"
            elif h < 16:
                period = "Afternoon"
            else:
                period = "Evening"

        progress = (gst_in_day / self.GST_SECONDS_PER_DAY) * 100.0

        return {
            "gst_formatted": formatted,
            "gst_hours": h,
            "gst_minutes": m,
            "gst_seconds": s,
            "gst_centiseconds": centi,
            "gst_day_progress": f"{progress:.1f}%",
            "gst_period": period
        }

    # ---------- update ----------
    def update(self) -> None:
        """Update the sensor state."""
        try:
            # Lade Plugin-Optionen
            opts = self.get_plugin_options()
            
            # Debug-Logging beim ersten Update
            if self._first_update:
                if opts:
                    _LOGGER.info(f"Mass Effect sensor loaded options: {opts}")
                else:
                    _LOGGER.debug("Mass Effect sensor using default options")
                self._first_update = False
            
            # Wende Optionen an
            self._enable_gst = bool(opts.get("enable_gst", True))
            self._precision = str(opts.get("precision", "second"))
            self._show_period = bool(opts.get("show_period", True))
            self._enable_gsy = bool(opts.get("enable_gsy", False))
            self._epoch_gs0_utc = str(opts.get("epoch_gs0_utc", "2183-01-01T00:00:00Z"))
            
            try:
                self._gsy_length_days = float(opts.get("gsy_length_days", 398.1))
                # Validierung
                if self._gsy_length_days <= 0:
                    _LOGGER.warning("Invalid gsy_length_days %f, using default 398.1", self._gsy_length_days)
                    self._gsy_length_days = 398.1
            except (ValueError, TypeError):
                self._gsy_length_days = 398.1

            now_utc = datetime.now(timezone.utc)

            # GST clock
            display_parts = []
            data: Dict[str, Any] = {
                "now_utc": now_utc.strftime("%Y-%m-%d %H:%M:%S UTC"),
                "config": {
                    "gst_enabled": self._enable_gst,
                    "gsy_enabled": self._enable_gsy,
                    "precision": self._precision,
                    "show_period": self._show_period
                }
            }

            if self._enable_gst:
                # total GST seconds since Unix epoch
                unix_seconds = now_utc.timestamp()
                gst_total_seconds = unix_seconds * self.GST_SECONDS_PER_SEC
                gst_block = self._format_gst(gst_total_seconds)
                data.update(gst_block)
                display_parts.append(gst_block["gst_formatted"])

            # GSY (optional approximate counter)
            if self._enable_gsy:
                epoch_dt = self._parse_epoch(self._epoch_gs0_utc)
                delta = now_utc - epoch_dt
                earth_days = delta.total_seconds() / 86400.0
                gsy_float = earth_days / self._gsy_length_days
                gsy_year = int(gsy_float)
                gsy_frac = gsy_float - gsy_year

                # also show approximate day-of-year in GST days
                gst_days_total = delta.total_seconds() / self.EARTH_SECONDS_PER_GST_DAY
                gst_days_in_year = self._gsy_length_days / (self.EARTH_SECONDS_PER_GST_DAY / 86400.0)  # ≈ 343.9
                doy_gst = gst_days_total - (int(gst_days_total / gst_days_in_year) * gst_days_in_year)

                data.update({
                    "gsy_epoch_utc": epoch_dt.isoformat(),
                    "gsy_year": gsy_year,
                    "gsy_progress": f"{gsy_frac*100:.2f}%",
                    "gsy_length_days_earth": self._gsy_length_days,
                    "gsy_day_of_year_gst": round(doy_gst, 2)
                })
                display_parts.append(f"GSY {gsy_year} (+{gsy_frac*100:.1f}%)")

            # State string
            if display_parts:
                self._state = " | ".join(display_parts)
            elif not self._enable_gst and not self._enable_gsy:
                self._state = "Disabled (enable GST or GSY)"
            else:
                self._state = "No data"
                
            self._data = data

        except Exception as exc:
            _LOGGER.exception("Failed to update Mass Effect Galactic Standard: %s", exc)
            self._state = "Error"
            self._data = {"error": str(exc)}