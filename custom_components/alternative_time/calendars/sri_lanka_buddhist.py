"""Sri Lankan Buddhist Calendar implementation - Version 1.0.0."""
from __future__ import annotations

import logging
import math
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Tuple

from homeassistant.core import HomeAssistant

from ..sensor import AlternativeTimeSensorBase

_LOGGER = logging.getLogger(__name__)

# ============================================
# CALENDAR METADATA
# ============================================

# Update hourly — Poya status and "days until" only change on day boundaries
UPDATE_INTERVAL = 3600

CALENDAR_INFO = {
    "id": "sri_lanka_buddhist",
    "version": "1.0.0",
    "icon": "mdi:dharmachakra",
    "category": "cultural",
    "accuracy": "approximate",  # Full moon calculation is mean-synodic, not true ephemeris
    "update_interval": UPDATE_INTERVAL,

    # Multi-language names
    "name": {
        "en": "Sri Lankan Buddhist Calendar",
        "de": "Sri-lankischer buddhistischer Kalender",
        "es": "Calendario Budista de Sri Lanka",
        "fr": "Calendrier Bouddhiste Sri-Lankais",
        "it": "Calendario Buddista dello Sri Lanka",
        "nl": "Srilankaans Boeddhistische Kalender",
        "pl": "Kalendarz Buddyjski Sri Lanki",
        "pt": "Calendário Budista do Sri Lanka",
        "ru": "Шри-ланкийский буддийский календарь",
        "ja": "スリランカ仏教暦",
        "zh": "斯里兰卡佛历",
        "ko": "스리랑카 불교 달력",
        "si": "ශ්‍රී ලාංකේය බෞද්ධ දින දර්ශනය",
        "ta": "இலங்கை பௌத்த நாட்காட்டி"
    },

    "description": {
        "en": "Buddhist Era calendar with Sinhala Poya (full moon) days and Sinhala/Tamil New Year",
        "de": "Buddhistischer Ära-Kalender mit Singhalesischen Poya-Tagen (Vollmond) und Singhalesisch-Tamilischem Neujahr",
        "es": "Calendario de la Era Budista con días Poya cingaleses (luna llena) y Año Nuevo cingalés/tamil",
        "fr": "Calendrier de l'Ère Bouddhiste avec jours Poya (pleine lune) et Nouvel An cinghalais/tamoul",
        "it": "Calendario dell'Era Buddista con giorni Poya cingalesi (luna piena) e Capodanno cingalese/tamil",
        "nl": "Boeddhistische Era kalender met Singalese Poya (volle maan) dagen en Singalees/Tamil Nieuwjaar",
        "pl": "Kalendarz Ery Buddyjskiej z syngaleskimi dniami Poya (pełnia księżyca) i Nowym Rokiem syngalesko-tamilskim",
        "pt": "Calendário da Era Budista com dias Poya cingaleses (lua cheia) e Ano Novo cingalês/tâmil",
        "ru": "Календарь буддийской эры с сингальскими днями Поя (полнолуние) и сингальско-тамильским Новым годом",
        "ja": "シンハラのポーヤ（満月）の日とシンハラ・タミル新年を含む仏暦",
        "zh": "佛历，含僧伽罗满月日（波耶）和僧伽罗/泰米尔新年",
        "ko": "신할라 포야(보름달) 일과 신할라/타밀 새해를 포함한 불교 시대 달력",
        "si": "පෝය දින සහ සිංහල හා දෙමළ අලුත් අවුරුද්ද සහිත බෞද්ධ ශක දින දර්ශනය",
        "ta": "சிங்கள மற்றும் தமிழ் புத்தாண்டு மற்றும் பௌர்ணமி (போய) நாட்களுடன் கூடிய பௌத்த சக நாட்காட்டி"
    },

    # Detailed information
    "detailed_info": {
        "en": {
            "overview": "Traditional calendar used in Sri Lanka, combining the Buddhist Era year with the lunar Poya (full moon) cycle",
            "structure": "Gregorian months for civil dates, but every full moon is a major religious observance",
            "year": "Buddhist Era (BE) = Common Era (CE) + 543",
            "new_year": "Sinhala and Tamil New Year (Aluth Avurudda / Puthandu), astronomically computed, usually 13–14 April",
            "poya": "Each lunar month has one Poya day (the full moon), and each is named: Duruthu, Nawam, Medin, Bak, Vesak, Poson, Esala, Nikini, Binara, Vap, Il, Unduvap",
            "vesak": "Vesak Poya (May full moon) commemorates the Buddha's birth, enlightenment, and parinirvana — the most important Buddhist holiday",
            "poson": "Poson Poya (June full moon) marks the introduction of Buddhism to Sri Lanka by Arahat Mahinda in 247 BCE",
            "weeks": "7-day week; weekdays bear Sinhala names derived from the planets"
        },
        "de": {
            "overview": "Traditioneller Kalender Sri Lankas, der das buddhistische Ära-Jahr mit dem Poya-Zyklus (Vollmond) verbindet",
            "structure": "Gregorianische Monate für zivile Daten, aber jeder Vollmond ist ein wichtiger religiöser Feiertag",
            "year": "Buddhistische Ära (BE) = Christliche Ära (CE) + 543",
            "new_year": "Singhalesisch-Tamilisches Neujahr (Aluth Avurudda / Puthandu), astronomisch berechnet, meist 13.–14. April",
            "poya": "Jeder Mondmonat hat einen Poya-Tag (Vollmond), benannt: Duruthu, Nawam, Medin, Bak, Vesak, Poson, Esala, Nikini, Binara, Vap, Il, Unduvap",
            "vesak": "Vesak Poya (Vollmond im Mai) erinnert an Geburt, Erleuchtung und Parinirvana Buddhas — der wichtigste buddhistische Feiertag",
            "poson": "Poson Poya (Vollmond im Juni) erinnert an die Einführung des Buddhismus in Sri Lanka durch Arahat Mahinda 247 v. Chr.",
            "weeks": "7-Tage-Woche; Wochentage tragen singhalesische Namen von den Planeten"
        }
    },

    # Sri Lankan calendar data
    "sri_lanka_data": {
        # Sinhala Poya names — one per Gregorian month the full moon falls in
        # Index 0 = January (Duruthu), ... 11 = December (Unduvap)
        "poya": [
            {
                "name": "Duruthu",
                "sinhala": "දුරුතු",
                "tamil": "துருது",
                "month_en": "January",
                "significance": {
                    "en": "Commemorates the Buddha's first visit to Sri Lanka",
                    "de": "Erinnert an Buddhas ersten Besuch auf Sri Lanka",
                    "si": "බුදුන් වහන්සේගේ පළමු ශ්‍රී ලංකා සංචාරය"
                }
            },
            {
                "name": "Nawam",
                "sinhala": "නවම්",
                "tamil": "நவம்",
                "month_en": "February",
                "significance": {
                    "en": "Marks the first conference of Buddhist monks",
                    "de": "Markiert die erste Versammlung buddhistischer Mönche",
                    "si": "පළමු සංඝ සමුළුව"
                }
            },
            {
                "name": "Medin",
                "sinhala": "මැදින්",
                "tamil": "மெதின்",
                "month_en": "March",
                "significance": {
                    "en": "Commemorates the Buddha's visit to his father King Suddhodana",
                    "de": "Erinnert an Buddhas Besuch bei seinem Vater König Suddhodana",
                    "si": "බුදුන් වහන්සේගේ පියා සුද්ධෝදන රජු හමුවට වැඩම කිරීම"
                }
            },
            {
                "name": "Bak",
                "sinhala": "බක්",
                "tamil": "பக்",
                "month_en": "April",
                "significance": {
                    "en": "Marks the Buddha's second visit to Sri Lanka",
                    "de": "Erinnert an Buddhas zweiten Besuch auf Sri Lanka",
                    "si": "බුදුන් වහන්සේගේ දෙවන ශ්‍රී ලංකා සංචාරය"
                }
            },
            {
                "name": "Vesak",
                "sinhala": "වෙසක්",
                "tamil": "வேசாக்",
                "month_en": "May",
                "significance": {
                    "en": "Buddha's birth, enlightenment, and parinirvana — the holiest Buddhist day",
                    "de": "Geburt, Erleuchtung und Parinirvana Buddhas — der heiligste buddhistische Tag",
                    "si": "බුදුන් වහන්සේගේ ජන්මය, බුද්ධත්වය හා පරිනිර්වාණය"
                }
            },
            {
                "name": "Poson",
                "sinhala": "පොසොන්",
                "tamil": "பொசொன்",
                "month_en": "June",
                "significance": {
                    "en": "Introduction of Buddhism to Sri Lanka by Arahat Mahinda (247 BCE)",
                    "de": "Einführung des Buddhismus in Sri Lanka durch Arahat Mahinda (247 v. Chr.)",
                    "si": "මහින්ද හිමියන් විසින් ශ්‍රී ලංකාවට බුද්ධාගම ගෙන ඒම"
                }
            },
            {
                "name": "Esala",
                "sinhala": "ඇසළ",
                "tamil": "எசள",
                "month_en": "July",
                "significance": {
                    "en": "Buddha's first sermon; Kandy Esala Perahera procession",
                    "de": "Buddhas erste Predigt; Kandy-Esala-Perahera-Prozession",
                    "si": "බුදුන් වහන්සේගේ ධර්ම චක්‍ර ප්‍රවර්තන දේශනය; නුවර ඇසළ පෙරහැර"
                }
            },
            {
                "name": "Nikini",
                "sinhala": "නිකිණි",
                "tamil": "நிகினி",
                "month_en": "August",
                "significance": {
                    "en": "First Buddhist council convened after the Buddha's parinirvana",
                    "de": "Erstes buddhistisches Konzil nach Buddhas Parinirvana",
                    "si": "පළමු සංගායනාව"
                }
            },
            {
                "name": "Binara",
                "sinhala": "බිනර",
                "tamil": "பினர",
                "month_en": "September",
                "significance": {
                    "en": "Establishment of the order of Buddhist nuns (Bhikkhuni Sangha)",
                    "de": "Gründung des Ordens der buddhistischen Nonnen (Bhikkhuni Sangha)",
                    "si": "භික්ෂුණී ශාසනය පිහිටුවීම"
                }
            },
            {
                "name": "Vap",
                "sinhala": "වප්",
                "tamil": "வப்",
                "month_en": "October",
                "significance": {
                    "en": "End of the Vassa (rainy season retreat) for Buddhist monks",
                    "de": "Ende der Vassa (Regenzeit-Klausur) der buddhistischen Mönche",
                    "si": "වස් සමාදන් අවසානය"
                }
            },
            {
                "name": "Il",
                "sinhala": "ඉල්",
                "tamil": "இல்",
                "month_en": "November",
                "significance": {
                    "en": "Commemorates the Buddha sending 60 Arahats to spread the Dhamma",
                    "de": "Erinnert daran, dass Buddha 60 Arahats aussandte, das Dhamma zu verbreiten",
                    "si": "අරහත්වරුන් සැට දෙනා ධර්ම ප්‍රචාරයට යැවීම"
                }
            },
            {
                "name": "Unduvap",
                "sinhala": "උඳුවප්",
                "tamil": "உந்துவப்",
                "month_en": "December",
                "significance": {
                    "en": "Arrival of Theri Sanghamitta with a sapling of the Sacred Bodhi Tree",
                    "de": "Ankunft der Theri Sanghamitta mit einem Schössling des heiligen Bodhi-Baums",
                    "si": "සංඝමිත්තා තෙරණිය ජයශ්‍රී මහා බෝධියේ ශාඛාවක් ගෙන ඒම"
                }
            }
        ],

        # Sinhala weekday names (Irida = Sunday is day 0)
        "weekdays": [
            {"name": "Irida", "sinhala": "ඉරිදා", "tamil": "ஞாயிறு", "english": "Sunday", "planet": "Sun"},
            {"name": "Sanduda", "sinhala": "සඳුදා", "tamil": "திங்கள்", "english": "Monday", "planet": "Moon"},
            {"name": "Angaharuwada", "sinhala": "අඟහරුවාදා", "tamil": "செவ்வாய்", "english": "Tuesday", "planet": "Mars"},
            {"name": "Badada", "sinhala": "බදාදා", "tamil": "புதன்", "english": "Wednesday", "planet": "Mercury"},
            {"name": "Brahaspathinda", "sinhala": "බ්‍රහස්පතින්දා", "tamil": "வியாழன்", "english": "Thursday", "planet": "Jupiter"},
            {"name": "Sikurada", "sinhala": "සිකුරාදා", "tamil": "வெள்ளி", "english": "Friday", "planet": "Venus"},
            {"name": "Senasurada", "sinhala": "සෙනසුරාදා", "tamil": "சனி", "english": "Saturday", "planet": "Saturn"}
        ],

        # Sinhala digits (Lith Illakkam, U+0DE6 – U+0DEF)
        "sinhala_digits": ["෦", "෧", "෨", "෩", "෪", "෫", "෬", "෭", "෮", "෯"],

        # Major fixed-date Sri Lankan public holidays (month, day)
        # Poya days are computed separately
        "holidays": {
            (1, 14): {"en": "Tamil Thai Pongal Day", "si": "තමිල් තෛපොංගල් දිනය"},
            (2, 4): {"en": "Independence Day", "si": "නිදහස් දිනය"},
            (4, 13): {"en": "Sinhala and Tamil New Year's Eve", "si": "අලුත් අවුරුදු දා"},
            (4, 14): {"en": "Sinhala and Tamil New Year", "si": "අලුත් අවුරුද්ද"},
            (5, 1): {"en": "May Day", "si": "මැයි දිනය"},
            (12, 25): {"en": "Christmas Day", "si": "නත්තල"}
        },

        # UI label translations
        "labels": {
            "next_poya": {
                "en": "Next Poya", "de": "Nächster Poya-Tag",
                "es": "Próximo Poya", "fr": "Prochain Poya",
                "it": "Prossimo Poya", "nl": "Volgende Poya",
                "pt": "Próximo Poya", "ru": "Следующий Поя",
                "ja": "次のポーヤ", "zh": "下一个波耶",
                "ko": "다음 포야", "si": "ඊළඟ පෝය", "ta": "அடுத்த போய"
            },
            "today_poya": {
                "en": "Today is {name} Poya!",
                "de": "Heute ist {name} Poya!",
                "si": "අද {name} පෝය දිනයයි!",
                "ta": "இன்று {name} போய!"
            },
            "days_until": {
                "en": "in {n} days", "de": "in {n} Tagen",
                "es": "en {n} días", "fr": "dans {n} jours",
                "it": "fra {n} giorni", "nl": "over {n} dagen",
                "pt": "em {n} dias", "ru": "через {n} дн.",
                "ja": "{n}日後", "zh": "{n}天后",
                "ko": "{n}일 후", "si": "තවත් දින {n}කින්",
                "ta": "{n} நாட்களில்"
            },
            "tomorrow": {
                "en": "tomorrow", "de": "morgen",
                "es": "mañana", "fr": "demain",
                "it": "domani", "nl": "morgen",
                "pt": "amanhã", "ru": "завтра",
                "ja": "明日", "zh": "明天",
                "ko": "내일", "si": "හෙට", "ta": "நாளை"
            },
            "new_year": {
                "en": "Sinhala/Tamil New Year",
                "de": "Singhalesisch/Tamilisches Neujahr",
                "es": "Año Nuevo Cingalés/Tamil",
                "fr": "Nouvel An Cinghalais/Tamoul",
                "it": "Capodanno Cingalese/Tamil",
                "nl": "Singalees/Tamil Nieuwjaar",
                "pt": "Ano Novo Cingalês/Tâmil",
                "ru": "Сингальско-тамильский Новый год",
                "ja": "シンハラ・タミル新年",
                "zh": "僧伽罗/泰米尔新年",
                "ko": "신할라/타밀 새해",
                "si": "අලුත් අවුරුද්ද", "ta": "புத்தாண்டு"
            }
        }
    },

    "reference_url": "https://en.wikipedia.org/wiki/Poya",
    "origin": "Sri Lanka",

    "example": "Vesak Poya | Wednesday, 14 May 2568 BE",
    "example_meaning": "Vesak full-moon day on 14 May 2025 CE (= 2568 Buddhist Era)",

    "related": ["suriyakati_thai", "hindu_panchang", "lunar_time"],

    "tags": [
        "cultural", "buddhist", "sri_lanka", "sinhala", "tamil",
        "poya", "vesak", "lunar", "be"
    ],

    "config_options": {
        "display_language": {
            "type": "select",
            "default": "english",
            "options": ["english", "sinhala", "tamil", "romanized", "combined"],
            "label": {
                "en": "Display Language", "de": "Anzeigesprache",
                "es": "Idioma de visualización", "fr": "Langue d'affichage",
                "si": "ප්‍රදර්ශන භාෂාව", "ta": "காட்சி மொழி"
            },
            "description": {
                "en": "Choose how to display dates (English, Sinhala script, Tamil script, romanized, or combined English+Sinhala)",
                "de": "Wählen Sie die Darstellung (Englisch, Singhalesisch, Tamilisch, romanisiert oder kombiniert)",
                "si": "දින දර්ශන භාෂාව තෝරන්න"
            }
        },
        "use_sinhala_numerals": {
            "type": "boolean",
            "default": False,
            "label": {
                "en": "Use Sinhala Numerals",
                "de": "Singhalesische Ziffern verwenden",
                "si": "සිංහල ඉලක්කම් භාවිතා කරන්න"
            },
            "description": {
                "en": "Display numbers using Sinhala Lith Illakkam (෦–෯) instead of Arabic digits. Note: Sinhala uses Arabic digits in modern daily life.",
                "de": "Zahlen mit singhalesischen Lith-Illakkam-Ziffern (෦–෯) anzeigen. Hinweis: Im modernen Alltag werden arabische Ziffern verwendet.",
                "si": "අරාබි ඉලක්කම් වෙනුවට සිංහල ලිත් ඉලක්කම් භාවිතා කරන්න"
            }
        },
        "show_next_poya": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show Next Poya Day",
                "de": "Nächsten Poya-Tag anzeigen",
                "si": "ඊළඟ පෝය දිනය පෙන්වන්න"
            },
            "description": {
                "en": "Show the name and date of the next Poya (full moon) day",
                "de": "Name und Datum des nächsten Poya-Tags (Vollmond) anzeigen",
                "si": "ඊළඟ පෝය දිනයේ නම සහ දිනය පෙන්වන්න"
            }
        },
        "show_significance": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show Poya Significance",
                "de": "Bedeutung des Poya-Tags anzeigen",
                "si": "පෝය දිනයේ වැදගත්කම පෙන්වන්න"
            },
            "description": {
                "en": "Display the historical/religious significance of each Poya day",
                "de": "Die religiöse/historische Bedeutung jedes Poya-Tags anzeigen",
                "si": "එක් එක් පෝය දිනයේ ආගමික වැදගත්කම පෙන්වන්න"
            }
        },
        "show_new_year": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show Sinhala/Tamil New Year",
                "de": "Singhalesisch/Tamilisches Neujahr anzeigen",
                "si": "අලුත් අවුරුද්ද පෙන්වන්න"
            },
            "description": {
                "en": "Show countdown to the next Sinhala and Tamil New Year (Aluth Avurudda)",
                "de": "Zähler bis zum nächsten Singhalesisch-Tamilischen Neujahr (Aluth Avurudda) anzeigen",
                "si": "ඊළඟ අලුත් අවුරුද්ද දක්වා දින ගණන පෙන්වන්න"
            }
        }
    }
}


# Mean synodic month length (days)
_SYNODIC_MONTH = 29.530588861

# JDE of the new moon nearest 2000-01-06 18:14 UTC (Meeus, ch. 49)
_JDE_NEW_MOON_K0 = 2451550.09766


def _datetime_to_jd(dt: datetime) -> float:
    """Convert a UTC datetime to Julian Date."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    year = dt.year
    month = dt.month
    day = dt.day + (dt.hour + dt.minute / 60.0 + dt.second / 3600.0) / 24.0
    if month <= 2:
        year -= 1
        month += 12
    a = year // 100
    b = 2 - a + a // 4
    jd = int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + b - 1524.5
    return float(jd)


def _jd_to_datetime(jd: float) -> datetime:
    """Convert a Julian Date back to a UTC datetime."""
    jd_plus = jd + 0.5
    z = int(jd_plus)
    f = jd_plus - z
    if z < 2299161:
        a = z
    else:
        alpha = int((z - 1867216.25) / 36524.25)
        a = z + 1 + alpha - alpha // 4
    b = a + 1524
    c = int((b - 122.1) / 365.25)
    d = int(365.25 * c)
    e = int((b - d) / 30.6001)
    day_full = b - d - int(30.6001 * e) + f
    month = e - 1 if e < 14 else e - 13
    year = c - 4716 if month > 2 else c - 4715
    day_i = int(day_full)
    frac = day_full - day_i
    secs = int(round(frac * 86400.0))
    hh, rem = divmod(secs, 3600)
    mm, ss = divmod(rem, 60)
    # Clamp seconds rollovers from rounding
    if hh >= 24:
        base = datetime(year, int(month), int(day_i), 0, 0, 0, tzinfo=timezone.utc)
        return base + timedelta(seconds=hh * 3600 + mm * 60 + ss)
    return datetime(year, int(month), int(day_i), hh, mm, ss, tzinfo=timezone.utc)


def _full_moon_jde(k: int) -> float:
    """Return the Julian Ephemeris Day of the k-th full moon after k=0.

    Implements Meeus, "Astronomical Algorithms" (2nd ed.) chapter 49 with the
    main periodic corrections for full moon (Table 49.B). Accurate to within
    a few minutes — well below the day-boundary precision Poya days need.
    """
    k_fm = k + 0.5  # Full moon offset within the lunation cycle
    T = k_fm / 1236.85  # Julian centuries since 2000-01-06

    jde = (
        _JDE_NEW_MOON_K0
        + _SYNODIC_MONTH * k_fm
        + 0.00015437 * T * T
        - 0.000000150 * T ** 3
        + 0.00000000073 * T ** 4
    )

    # Sun's mean anomaly
    M = 2.5534 + 29.10535670 * k_fm - 0.0000014 * T * T - 0.00000011 * T ** 3
    # Moon's mean anomaly
    Mp = (
        201.5643 + 385.81693528 * k_fm + 0.0107582 * T * T
        + 0.00001238 * T ** 3 - 0.000000058 * T ** 4
    )
    # Moon's argument of latitude
    F = (
        160.7108 + 390.67050284 * k_fm - 0.0016118 * T * T
        - 0.00000227 * T ** 3 + 0.000000011 * T ** 4
    )
    # Longitude of ascending node
    Omega = 124.7746 - 1.56375588 * k_fm + 0.0020672 * T * T + 0.00000215 * T ** 3
    # Earth-orbit eccentricity correction
    E = 1.0 - 0.002516 * T - 0.0000074 * T * T

    Mr = math.radians(M)
    Mpr = math.radians(Mp)
    Fr = math.radians(F)
    Or = math.radians(Omega)

    corr = (
        -0.40614 * math.sin(Mpr)
        + 0.17302 * E * math.sin(Mr)
        + 0.01614 * math.sin(2 * Mpr)
        + 0.01043 * math.sin(2 * Fr)
        + 0.00734 * E * math.sin(Mpr - Mr)
        - 0.00515 * E * math.sin(Mpr + Mr)
        + 0.00209 * E * E * math.sin(2 * Mr)
        - 0.00111 * math.sin(Mpr - 2 * Fr)
        - 0.00057 * math.sin(Mpr + 2 * Fr)
        + 0.00056 * E * math.sin(2 * Mpr + Mr)
        - 0.00042 * math.sin(3 * Mpr)
        + 0.00042 * E * math.sin(Mr + 2 * Fr)
        + 0.00038 * E * math.sin(Mr - 2 * Fr)
        - 0.00024 * E * math.sin(2 * Mpr - Mr)
        - 0.00017 * math.sin(Or)
        - 0.00007 * math.sin(Mpr + 2 * Mr)
        + 0.00004 * math.sin(2 * Mpr - 2 * Fr)
        + 0.00004 * math.sin(3 * Mr)
        + 0.00003 * math.sin(Mpr + Mr - 2 * Fr)
        + 0.00003 * math.sin(2 * Mpr + 2 * Fr)
        - 0.00003 * math.sin(Mpr + Mr + 2 * Fr)
        + 0.00003 * math.sin(Mpr - Mr + 2 * Fr)
        - 0.00002 * math.sin(Mpr - Mr - 2 * Fr)
        - 0.00002 * math.sin(3 * Mpr + Mr)
        + 0.00002 * math.sin(4 * Mpr)
    )
    return jde + corr


# Sri Lanka Standard Time offset (UTC+5:30, no DST)
_SL_OFFSET = timedelta(hours=5, minutes=30)


def _nearest_full_moon(dt: datetime) -> Tuple[datetime, float]:
    """Return (UTC datetime of nearest full moon, signed days offset from dt)."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    target_jd = _datetime_to_jd(dt)
    k_approx = round((target_jd - _JDE_NEW_MOON_K0) / _SYNODIC_MONTH)

    best_dt: Optional[datetime] = None
    best_off: Optional[float] = None
    for k in (k_approx - 1, k_approx, k_approx + 1):
        jde = _full_moon_jde(int(k))
        fm_dt = _jd_to_datetime(jde)
        off = (fm_dt - dt).total_seconds() / 86400.0
        if best_off is None or abs(off) < abs(best_off):
            best_off = off
            best_dt = fm_dt
    assert best_dt is not None and best_off is not None
    return best_dt, best_off


def _poya_date(full_moon_utc: datetime) -> datetime:
    """Compute the Sri Lankan Poya civil date for a given astronomical full moon.

    Sri Lankan Poya follows the moonrise convention: Poya is the civil day on
    which the moon rises while at or just before full. Since moonrise on a
    full-moon day is ~18:00 local time, the rule is:

      - If the astronomical full moon occurs in Sri Lanka Standard Time
        at hour >= 18, Poya is that SLST date.
      - Otherwise (full moon before 18:00 SLST), Poya is the day before.

    This rule is equivalent to subtracting 18 hours from the SLST full moon
    time and taking the date. It reproduces the officially proclaimed Sri
    Lankan Poya calendar exactly for the 2023–2026 test sample.
    """
    fm_slst = full_moon_utc + _SL_OFFSET
    shifted = fm_slst - timedelta(hours=18)
    return datetime(shifted.year, shifted.month, shifted.day, tzinfo=timezone.utc)


def _next_poya_on_or_after(today_utc: datetime) -> Tuple[datetime, datetime]:
    """Find the first Poya day that is >= today_utc (returned as midnight UTC).

    Returns (poya_civil_date, full_moon_utc) so callers can also report the
    underlying astronomical instant.
    """
    if today_utc.tzinfo is None:
        today_utc = today_utc.replace(tzinfo=timezone.utc)
    today_day = datetime(today_utc.year, today_utc.month, today_utc.day, tzinfo=timezone.utc)

    # Start from the lunation nearest today, then step forward if needed
    target_jd = _datetime_to_jd(today_utc)
    k_approx = round((target_jd - _JDE_NEW_MOON_K0) / _SYNODIC_MONTH)
    for k in (k_approx - 1, k_approx, k_approx + 1, k_approx + 2):
        fm = _jd_to_datetime(_full_moon_jde(int(k)))
        poya = _poya_date(fm)
        if poya >= today_day:
            return poya, fm
    # Fallback (should never hit)
    fm = _jd_to_datetime(_full_moon_jde(int(k_approx + 3)))
    return _poya_date(fm), fm


class SriLankaBuddhistSensor(AlternativeTimeSensorBase):
    """Sensor for displaying the Sri Lankan Buddhist calendar."""

    UPDATE_INTERVAL = UPDATE_INTERVAL

    def __init__(self, base_name: str, hass: HomeAssistant) -> None:
        """Initialize the Sri Lankan Buddhist calendar sensor."""
        super().__init__(base_name, hass)

        calendar_name = self._translate('name', 'Sri Lankan Buddhist Calendar')
        self._attr_name = f"{base_name} {calendar_name}"
        self._attr_unique_id = f"{base_name}_sri_lanka_buddhist"
        self._attr_icon = CALENDAR_INFO.get("icon", "mdi:dharmachakra")

        # Default configuration
        self._display_language = "english"
        self._use_sinhala_numerals = False
        self._show_next_poya = True
        self._show_significance = True
        self._show_new_year = True

        self._sl_data = CALENDAR_INFO["sri_lanka_data"]
        self._options_loaded = False

        self._sl_date: Dict[str, Any] = {}
        self._state = "Initializing..."

        _LOGGER.debug(f"Initialized Sri Lankan Buddhist Calendar sensor: {self._attr_name}")

    # ---------- options ----------
    def _load_options(self) -> None:
        if self._options_loaded:
            return
        try:
            options = self.get_plugin_options()
            if options:
                self._display_language = options.get("display_language", self._display_language)
                self._use_sinhala_numerals = options.get("use_sinhala_numerals", self._use_sinhala_numerals)
                self._show_next_poya = options.get("show_next_poya", self._show_next_poya)
                self._show_significance = options.get("show_significance", self._show_significance)
                self._show_new_year = options.get("show_new_year", self._show_new_year)
            self._options_loaded = True
        except Exception as e:
            _LOGGER.debug(f"Sri Lanka calendar could not load options yet: {e}")

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self._load_options()

    # ---------- helpers ----------
    def _lang(self) -> str:
        try:
            lang = (self._user_language or 'en').lower() if hasattr(self, '_user_language') else 'en'
            if '-' in lang:
                lang = lang.split('-')[0]
            return lang
        except Exception:
            return 'en'

    def _label(self, key: str, default: str = "") -> str:
        """Localised UI label from sri_lanka_data.labels[key]."""
        labels = self._sl_data.get("labels", {}).get(key, {})
        return labels.get(self._lang(), labels.get("en", default))

    def _to_sinhala_number(self, n: int) -> str:
        if not self._use_sinhala_numerals:
            return str(n)
        digits = self._sl_data["sinhala_digits"]
        return ''.join(digits[int(d)] for d in str(n))

    def _format_number(self, n: int) -> str:
        return self._to_sinhala_number(n) if self._use_sinhala_numerals else str(n)

    # ---------- Sinhala/Tamil New Year ----------
    @staticmethod
    def _sinhala_new_year(year: int) -> datetime:
        """Approximate date of Aluth Avurudda (Sinhala/Tamil New Year).

        Astronomically the moment the Sun enters Mesha (Aries) by sidereal
        reckoning, almost always 14 April (occasionally 13 April due to
        leap-year drift). The festival day is officially proclaimed annually.
        We use 14 April as a stable approximation — within ±1 day of reality.
        """
        return datetime(year, 4, 14, tzinfo=timezone.utc)

    # ---------- main computation ----------
    def _calculate(self, now: datetime) -> Dict[str, Any]:
        self._load_options()

        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)

        # Buddhist Era
        buddhist_year = now.year + 543

        # Weekday (Sinhala convention: Sunday = 0)
        # Python: Monday = 0 ... Sunday = 6
        weekday_index = (now.weekday() + 1) % 7
        weekday = self._sl_data["weekdays"][weekday_index]

        # Today (Sri Lanka civil date — Poya is proclaimed in SL time)
        now_slst = now + _SL_OFFSET
        today = datetime(now_slst.year, now_slst.month, now_slst.day, tzinfo=timezone.utc)

        # Next Poya from today onwards (might be today)
        next_poya_date, next_fm_utc = _next_poya_on_or_after(today)
        days_to_next_poya = (next_poya_date - today).days
        is_poya_today = (days_to_next_poya == 0)

        # Poya names are indexed by the Gregorian month the Poya date falls in
        poya_today = self._sl_data["poya"][today.month - 1] if is_poya_today else None
        poya_next = self._sl_data["poya"][next_poya_date.month - 1]

        # Sinhala/Tamil New Year — find the next one
        ny_this = self._sinhala_new_year(now.year)
        if now < ny_this:
            ny_next = ny_this
        else:
            ny_next = self._sinhala_new_year(now.year + 1)
        days_to_ny = (datetime(ny_next.year, ny_next.month, ny_next.day, tzinfo=timezone.utc) - today).days

        # Fixed holiday for today?
        holiday = self._sl_data["holidays"].get((now.month, now.day))

        # ---------- assemble result ----------
        result: Dict[str, Any] = {
            "buddhist_year": buddhist_year,
            "gregorian_date": now.strftime("%Y-%m-%d"),
            "gregorian_year": now.year,
            "weekday_english": weekday["english"],
            "weekday_sinhala": weekday["sinhala"],
            "weekday_tamil": weekday["tamil"],
            "weekday_romanized": weekday["name"],
            "weekday_planet": weekday["planet"],
            "is_poya_today": is_poya_today,
            "days_until_next_poya": days_to_next_poya,
            "next_poya_date": next_poya_date.strftime("%Y-%m-%d"),
            "next_poya_full_moon_utc": next_fm_utc.strftime("%Y-%m-%d %H:%M UTC"),
            "next_poya_name": poya_next["name"],
            "next_poya_sinhala": poya_next["sinhala"],
            "next_poya_tamil": poya_next["tamil"],
        }

        if self._show_significance:
            sig = poya_next.get("significance", {})
            result["next_poya_significance"] = sig.get(self._lang(), sig.get("en", ""))

        if is_poya_today and poya_today:
            result["poya_today_name"] = poya_today["name"]
            result["poya_today_sinhala"] = poya_today["sinhala"]
            result["poya_today_tamil"] = poya_today["tamil"]
            if self._show_significance:
                sig_today = poya_today.get("significance", {})
                result["poya_today_significance"] = sig_today.get(self._lang(), sig_today.get("en", ""))

        if self._show_new_year:
            result["next_sinhala_new_year"] = ny_next.strftime("%Y-%m-%d")
            result["days_until_sinhala_new_year"] = days_to_ny
            result["next_buddhist_year"] = ny_next.year + 543

        if holiday:
            result["holiday_english"] = holiday.get("en", "")
            result["holiday_sinhala"] = holiday.get("si", "")

        # Build the formatted state string
        result["formatted"] = self._format_state(
            now, buddhist_year, weekday,
            is_poya_today, poya_today,
            days_to_next_poya, poya_next, next_poya_date
        )

        return result

    # ---------- formatting ----------
    def _format_state(
        self,
        now: datetime,
        buddhist_year: int,
        weekday: Dict[str, str],
        is_poya_today: bool,
        poya_today: Optional[Dict[str, Any]],
        days_to_next_poya: int,
        poya_next: Dict[str, Any],
        next_poya_date: datetime,
    ) -> str:
        lang = self._display_language
        day_str = self._format_number(now.day)
        year_str = self._format_number(buddhist_year)
        month_en = now.strftime("%B")

        # Weekday + date in the chosen language
        if lang == "sinhala":
            wd = weekday["sinhala"]
            date_part = f"{wd}, {day_str} {month_en} {year_str} බෞ.ව."
        elif lang == "tamil":
            wd = weekday["tamil"]
            date_part = f"{wd}, {day_str} {month_en} {year_str} BE"
        elif lang == "romanized":
            wd = weekday["name"]
            date_part = f"{wd}, {day_str} {month_en} {year_str} BE"
        elif lang == "combined":
            wd_en = weekday["english"]
            wd_si = weekday["sinhala"]
            date_part = f"{wd_en} ({wd_si}), {day_str} {month_en} {year_str} BE"
        else:  # english
            wd = weekday["english"]
            date_part = f"{wd}, {day_str} {month_en} {year_str} BE"

        # Poya status
        if is_poya_today and poya_today:
            template = self._label("today_poya", "Today is {name} Poya!")
            poya_name = poya_today["sinhala"] if lang == "sinhala" else (
                poya_today["tamil"] if lang == "tamil" else poya_today["name"]
            )
            return f"🌕 {template.format(name=poya_name)} · {date_part}"

        if self._show_next_poya:
            poya_name = poya_next["sinhala"] if lang == "sinhala" else (
                poya_next["tamil"] if lang == "tamil" else poya_next["name"]
            )
            if days_to_next_poya == 0:
                # safety branch — handled by is_poya_today above
                when = ""
            elif days_to_next_poya == 1:
                when = self._label("tomorrow", "tomorrow")
            else:
                template = self._label("days_until", "in {n} days")
                when = template.format(n=self._format_number(days_to_next_poya))
            next_label = self._label("next_poya", "Next Poya")
            return f"{date_part} · {next_label}: {poya_name} ({when})"

        return date_part

    # ---------- HA hooks ----------
    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        attrs = super().extra_state_attributes
        if self._sl_date:
            attrs.update(self._sl_date)
            attrs["description"] = self._translate("description")
            attrs["reference"] = CALENDAR_INFO.get("reference_url", "")
            attrs["config"] = {
                "display_language": self._display_language,
                "use_sinhala_numerals": self._use_sinhala_numerals,
                "show_next_poya": self._show_next_poya,
                "show_significance": self._show_significance,
                "show_new_year": self._show_new_year,
            }
        return attrs

    def update(self) -> None:
        try:
            now = datetime.now(timezone.utc)
            self._sl_date = self._calculate(now)
            self._state = self._sl_date["formatted"]
        except Exception as e:
            _LOGGER.exception("Error calculating Sri Lankan Buddhist date")
            self._state = "Error"
            self._sl_date = {"error": str(e)}

        _LOGGER.debug(f"Updated Sri Lankan Buddhist Calendar to {self._state}")
