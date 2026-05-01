# Solar System Planetary Positions implementation - Version 1.4.0
# Displays current positions of planets in our solar system as SVG (and optional PNG).
# Fixed: January at top, Earth with "You are here" marker, JWST removed
# Fixed v1.4.0: Corrected planetary position calculation (mean longitude vs mean anomaly)

from __future__ import annotations

import base64
import io
import logging
import math
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

try:
    from PIL import Image, ImageDraw, ImageFont  # optional
except Exception:
    Image = None
    ImageDraw = None
    ImageFont = None

from homeassistant.core import HomeAssistant

from ..sensor import AlternativeTimeSensorBase

_LOGGER = logging.getLogger(__name__)

# ============================================
# CALENDAR METADATA
# ============================================

UPDATE_INTERVAL = 300  # seconds

CALENDAR_INFO = {
    "id": "solar_system",
    "version": "1.4.0",
    "icon": "mdi:orbit",
    "category": "space",
    "accuracy": "approximate",
    "update_interval": UPDATE_INTERVAL,

    # Multi-language names
    "name": {
        "en": "Solar System Positions",
        "de": "Sonnensystem Positionen",
        "es": "Posiciones del Sistema Solar",
        "fr": "Positions du Système Solaire",
        "it": "Posizioni del Sistema Solare",
        "nl": "Zonnestelsel Posities",
        "pl": "Pozycje Układu Słonecznego",
        "pt": "Posições do Sistema Solar",
        "ru": "Позиции Солнечной системы",
        "ja": "太陽系の位置",
        "zh": "太阳系位置",
        "ko": "태양계 위치"
    },

    # Short descriptions for UI
    "description": {
        "en": "Current positions of planets in the solar system.",
        "de": "Aktuelle Positionen der Planeten im Sonnensystem.",
        "es": "Posiciones actuales de los planetas en el sistema solar.",
        "fr": "Positions actuelles des planètes dans le système solaire.",
        "it": "Posizioni attuali dei pianeti nel sistema solare.",
        "nl": "Huidige posities van planeten in het zonnestelsel.",
        "pl": "Aktualne pozycje planet w Układzie Słonecznym.",
        "pt": "Posições atuais dos planetas no sistema solar.",
        "ru": "Текущие позиции планет в Солнечной системе.",
        "ja": "太陽系の惑星の現在位置。",
        "zh": "太阳系行星的当前位置。",
        "ko": "태양계 행성의 현재 위치."
    },

    # Solar system specific data
    "solar_data": {
        # Planets (simplified Keplerian elements, J2000.0)
        "planets": {
            "mercury": {
                "name": {
                    "en": "Mercury", "de": "Merkur", "es": "Mercurio", "fr": "Mercure",
                    "it": "Mercurio", "nl": "Mercurius", "pl": "Merkury", "pt": "Mercúrio",
                    "ru": "Меркурий", "ja": "水星", "zh": "水星", "ko": "수성"
                },
                "symbol": "☿",
                "color": "#8C7853",
                "semi_major_axis": 0.387098,
                "eccentricity": 0.205635,
                "inclination": 7.005,
                "mean_longitude_j2000": 252.250,
                "perihelion_longitude": 77.456,
                "orbital_period": 87.969
            },
            "venus": {
                "name": {
                    "en": "Venus", "de": "Venus", "es": "Venus", "fr": "Vénus",
                    "it": "Venere", "nl": "Venus", "pl": "Wenus", "pt": "Vênus",
                    "ru": "Венера", "ja": "金星", "zh": "金星", "ko": "금성"
                },
                "symbol": "♀",
                "color": "#FFC649",
                "semi_major_axis": 0.723332,
                "eccentricity": 0.006772,
                "inclination": 3.395,
                "mean_longitude_j2000": 181.979,
                "perihelion_longitude": 131.564,
                "orbital_period": 224.701
            },
            "earth": {
                "name": {
                    "en": "Earth", "de": "Erde", "es": "Tierra", "fr": "Terre",
                    "it": "Terra", "nl": "Aarde", "pl": "Ziemia", "pt": "Terra",
                    "ru": "Земля", "ja": "地球", "zh": "地球", "ko": "지구"
                },
                "symbol": "⊕",
                "color": "#4A90E2",
                "semi_major_axis": 1.0,
                "eccentricity": 0.016709,
                "inclination": 0.0,
                "mean_longitude_j2000": 100.464,
                "perihelion_longitude": 102.937,
                "orbital_period": 365.256
            },
            "mars": {
                "name": {
                    "en": "Mars", "de": "Mars", "es": "Marte", "fr": "Mars",
                    "it": "Marte", "nl": "Mars", "pl": "Mars", "pt": "Marte",
                    "ru": "Марс", "ja": "火星", "zh": "火星", "ko": "화성"
                },
                "symbol": "♂",
                "color": "#CD5C5C",
                "semi_major_axis": 1.523679,
                "eccentricity": 0.0934,
                "inclination": 1.85,
                "mean_longitude_j2000": 355.433,
                "perihelion_longitude": 336.060,
                "orbital_period": 686.980
            },
            "jupiter": {
                "name": {
                    "en": "Jupiter", "de": "Jupiter", "es": "Júpiter", "fr": "Jupiter",
                    "it": "Giove", "nl": "Jupiter", "pl": "Jowisz", "pt": "Júpiter",
                    "ru": "Юпитер", "ja": "木星", "zh": "木星", "ko": "목성"
                },
                "symbol": "♃",
                "color": "#DAA520",
                "semi_major_axis": 5.202887,
                "eccentricity": 0.048498,
                "inclination": 1.303,
                "mean_longitude_j2000": 34.351,
                "perihelion_longitude": 14.331,
                "orbital_period": 4332.589
            },
            "saturn": {
                "name": {
                    "en": "Saturn", "de": "Saturn", "es": "Saturno", "fr": "Saturne",
                    "it": "Saturno", "nl": "Saturnus", "pl": "Saturn", "pt": "Saturno",
                    "ru": "Сатурн", "ja": "土星", "zh": "土星", "ko": "토성"
                },
                "symbol": "♄",
                "color": "#F4A460",
                "semi_major_axis": 9.536676,
                "eccentricity": 0.053862,
                "inclination": 2.485,
                "mean_longitude_j2000": 50.077,
                "perihelion_longitude": 93.057,
                "orbital_period": 10759.22
            },
            "uranus": {
                "name": {
                    "en": "Uranus", "de": "Uranus", "es": "Urano", "fr": "Uranus",
                    "it": "Urano", "nl": "Uranus", "pl": "Uran", "pt": "Urano",
                    "ru": "Уран", "ja": "天王星", "zh": "天王星", "ko": "천왕성"
                },
                "symbol": "♅",
                "color": "#4FD0E2",
                "semi_major_axis": 19.189165,
                "eccentricity": 0.047257,
                "inclination": 0.772,
                "mean_longitude_j2000": 314.055,
                "perihelion_longitude": 173.005,
                "orbital_period": 30688.5
            },
            "neptune": {
                "name": {
                    "en": "Neptune", "de": "Neptun", "es": "Neptuno", "fr": "Neptune",
                    "it": "Nettuno", "nl": "Neptunus", "pl": "Neptun", "pt": "Netuno",
                    "ru": "Нептун", "ja": "海王星", "zh": "海王星", "ko": "해왕성"
                },
                "symbol": "♆",
                "color": "#4169E1",
                "semi_major_axis": 30.069923,
                "eccentricity": 0.008859,
                "inclination": 1.769,
                "mean_longitude_j2000": 304.880,
                "perihelion_longitude": 48.123,
                "orbital_period": 60182.0
            },
            "pluto": {
                "name": {
                    "en": "Pluto (Dwarf Planet)", "de": "Pluto (Zwergplanet)", "es": "Plutón (Planeta Enano)",
                    "fr": "Pluton (Planète Naine)", "it": "Plutone (Pianeta Nano)", "nl": "Pluto (Dwergplaneet)",
                    "pl": "Pluton (Planeta Karłowata)", "pt": "Plutão (Planeta Anão)",
                    "ru": "Плутон (Карликовая планета)", "ja": "冥王星（準惑星）",
                    "zh": "冥王星（矮行星）", "ko": "명왕성 (왜행성)"
                },
                "symbol": "♇",
                "color": "#9B870C",
                "semi_major_axis": 39.482117,
                "eccentricity": 0.2488,
                "inclination": 17.16,
                "mean_longitude_j2000": 238.929,
                "perihelion_longitude": 224.067,
                "orbital_period": 90560.0,
                "is_dwarf_planet": True
            },
            # Deep-space probes (visualization only; crude kinematics)
            "voyager1": {
                "name": {
                    "en": "Voyager 1", "de": "Voyager 1", "es": "Voyager 1", "fr": "Voyager 1",
                    "it": "Voyager 1", "nl": "Voyager 1", "pl": "Voyager 1", "pt": "Voyager 1",
                    "ru": "Вояджер-1", "ja": "ボイジャー1号", "zh": "旅行者1号", "ko": "보이저 1호"
                },
                "symbol": "🛰",
                "color": "#00D1B2",
                "special_type": "probe",
                # approx heliolongitude anchor (deg, J2000) and AU at epoch and outward speed in AU/yr
                "anchor_longitude": 255.0,
                "anchor_au": 163.0,  # Updated for 2025
                "speed_au_per_year": 3.6
            },
            "voyager2": {
                "name": {
                    "en": "Voyager 2", "de": "Voyager 2", "es": "Voyager 2", "fr": "Voyager 2",
                    "it": "Voyager 2", "nl": "Voyager 2", "pl": "Voyager 2", "pt": "Voyager 2",
                    "ru": "Вояджер-2", "ja": "ボイジャー2号", "zh": "旅行者2号", "ko": "보이저 2호"
                },
                "symbol": "🛰",
                "color": "#00A3A3",
                "special_type": "probe",
                "anchor_longitude": 300.0,
                "anchor_au": 137.0,  # Updated for 2025
                "speed_au_per_year": 3.3
            }
        },

        # Zodiac constellations (for positioning)
        "constellations": [
            {"name": {"en": "Aries", "de": "Widder", "es": "Aries", "fr": "Bélier", "it": "Ariete", "nl": "Ram", "pl": "Baran", "pt": "Áries", "ru": "Овен", "ja": "牡羊座", "zh": "白羊座", "ko": "양자리"}, "symbol": "♈", "start": 0},
            {"name": {"en": "Taurus", "de": "Stier", "es": "Tauro", "fr": "Taureau", "it": "Toro", "nl": "Stier", "pl": "Byk", "pt": "Touro", "ru": "Телец", "ja": "牡牛座", "zh": "金牛座", "ko": "황소자리"}, "symbol": "♉", "start": 30},
            {"name": {"en": "Gemini", "de": "Zwillinge", "es": "Géminis", "fr": "Gémeaux", "it": "Gemelli", "nl": "Tweelingen", "pl": "Bliźnięta", "pt": "Gêmeos", "ru": "Близнецы", "ja": "双子座", "zh": "双子座", "ko": "쌍둥이자리"}, "symbol": "♊", "start": 60},
            {"name": {"en": "Cancer", "de": "Krebs", "es": "Cáncer", "fr": "Cancer", "it": "Cancro", "nl": "Kreeft", "pl": "Rak", "pt": "Câncer", "ru": "Рак", "ja": "蟹座", "zh": "巨蟹座", "ko": "게자리"}, "symbol": "♋", "start": 90},
            {"name": {"en": "Leo", "de": "Löwe", "es": "Leo", "fr": "Lion", "it": "Leone", "nl": "Leeuw", "pl": "Lew", "pt": "Leão", "ru": "Лев", "ja": "獅子座", "zh": "狮子座", "ko": "사자자리"}, "symbol": "♌", "start": 120},
            {"name": {"en": "Virgo", "de": "Jungfrau", "es": "Virgo", "fr": "Vierge", "it": "Vergine", "nl": "Maagd", "pl": "Panna", "pt": "Virgem", "ru": "Дева", "ja": "乙女座", "zh": "处女座", "ko": "처녀자리"}, "symbol": "♍", "start": 150},
            {"name": {"en": "Libra", "de": "Waage", "es": "Libra", "fr": "Balance", "it": "Bilancia", "nl": "Weegschaal", "pl": "Waga", "pt": "Libra", "ru": "Весы", "ja": "天秤座", "zh": "天秤座", "ko": "천칭자리"}, "symbol": "♎", "start": 180},
            {"name": {"en": "Scorpio", "de": "Skorpion", "es": "Escorpio", "fr": "Scorpion", "it": "Scorpione", "nl": "Schorpioen", "pl": "Skorpion", "pt": "Escorpião", "ru": "Скорпион", "ja": "蠍座", "zh": "天蝎座", "ko": "전갈자리"}, "symbol": "♏", "start": 210},
            {"name": {"en": "Sagittarius", "de": "Schütze", "es": "Sagitario", "fr": "Sagittaire", "it": "Sagittario", "nl": "Boogschutter", "pl": "Strzelec", "pt": "Sagitário", "ru": "Стрелец", "ja": "射手座", "zh": "射手座", "ko": "궁수자리"}, "symbol": "♐", "start": 240},
            {"name": {"en": "Capricorn", "de": "Steinbock", "es": "Capricornio", "fr": "Capricorne", "it": "Capricorno", "nl": "Steenbok", "pl": "Koziorożec", "pt": "Capricórnio", "ru": "Козерог", "ja": "山羊座", "zh": "摩羯座", "ko": "염소자리"}, "symbol": "♑", "start": 270},
            {"name": {"en": "Aquarius", "de": "Wassermann", "es": "Acuario", "fr": "Verseau", "it": "Acquario", "nl": "Waterman", "pl": "Wodnik", "pt": "Aquário", "ru": "Водолей", "ja": "水瓶座", "zh": "水瓶座", "ko": "물병자리"}, "symbol": "♒", "start": 300},
            {"name": {"en": "Pisces", "de": "Fische", "es": "Piscis", "fr": "Poissons", "it": "Pesci", "nl": "Vissen", "pl": "Ryby", "pt": "Peixes", "ru": "Рыбы", "ja": "魚座", "zh": "双鱼座", "ko": "물고기자리"}, "symbol": "♓", "start": 330}
        ],

        # Month names for visualization
        "months": {
            "en": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
            "de": ["Jan", "Feb", "Mär", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"],
            "es": ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"],
            "fr": ["Jan", "Fév", "Mar", "Avr", "Mai", "Jui", "Jul", "Aoû", "Sep", "Oct", "Nov", "Déc"],
            "it": ["Gen", "Feb", "Mar", "Apr", "Mag", "Giu", "Lug", "Ago", "Set", "Ott", "Nov", "Dic"],
            "nl": ["Jan", "Feb", "Mrt", "Apr", "Mei", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dec"],
            "pl": ["Sty", "Lut", "Mar", "Kwi", "Maj", "Cze", "Lip", "Sie", "Wrz", "Paź", "Lis", "Gru"],
            "pt": ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"],
            "ru": ["Янв", "Фев", "Мар", "Апр", "Май", "Июн", "Июл", "Авг", "Сен", "Окт", "Ноя", "Дек"],
            "ja": ["1月", "2月", "3月", "4月", "5月", "6月", "7月", "8月", "9月", "10月", "11月", "12月"],
            "zh": ["一月", "二月", "三月", "四月", "五月", "六月", "七月", "八月", "九月", "十月", "十一月", "十二月"],
            "ko": ["1월", "2월", "3월", "4월", "5월", "6월", "7월", "8월", "9월", "10월", "11월", "12월"]
        },

        # Visualization labels
        "you_are_here": {
            "en": "You are here", "de": "Sie sind hier", "es": "Usted está aquí", "fr": "Vous êtes ici",
            "it": "Voi siete qui", "nl": "U bent hier", "pl": "Jesteś tutaj", "pt": "Você está aqui",
            "ru": "Вы здесь", "ja": "あなたはここにいます", "zh": "你在这里", "ko": "당신은 여기 있습니다"
        },

        # Footer text
        "footer": {
            "en": "Heliocentric · Sun at center · Jan at top",
            "de": "Heliozentrisch · Sonne im Zentrum · Jan oben",
            "es": "Heliocéntrico · Sol en el centro · Ene arriba",
            "fr": "Héliocentrique · Soleil au centre · Jan en haut",
            "it": "Eliocentrico · Sole al centro · Gen in alto",
            "nl": "Heliocentrisch · Zon in het midden · Jan boven",
            "pl": "Heliocentryczny · Słońce w centrum · Sty na górze",
            "pt": "Heliocêntrico · Sol no centro · Jan no topo",
            "ru": "Гелиоцентрический · Солнце в центре · Янв вверху",
            "ja": "太陽中心 · 太陽が中心 · 1月が上",
            "zh": "日心 · 太阳在中心 · 一月在上",
            "ko": "태양 중심 · 태양이 중심 · 1월이 위"
        },

        # Kuiper belt labels
        "kuiper_belt": {
            "en": "Kuiper Belt", "de": "Kuipergürtel", "es": "Cinturón de Kuiper", "fr": "Ceinture de Kuiper",
            "it": "Fascia di Kuiper", "nl": "Kuipergordel", "pl": "Pas Kuipera", "pt": "Cinturão de Kuiper",
            "ru": "Пояс Койпера", "ja": "カイパーベルト", "zh": "柯伊伯带", "ko": "카이퍼 벨트"
        }
    },

    # Configuration options for config_flow
    "config_options": {
        "display_planet": {
            "type": "select",
            "default": "all",
            "label": {"en": "Display Planet", "de": "Planet anzeigen", "es": "Mostrar Planeta", "fr": "Afficher Planète", "it": "Mostra Pianeta", "nl": "Toon Planeet", "pl": "Wyświetl Planetę", "pt": "Mostrar Planeta", "ru": "Показать Планету", "ja": "惑星を表示", "zh": "显示行星", "ko": "행성 표시"},
            "description": {"en": "Select a specific planet or show all", "de": "Wählen Sie einen bestimmten Planeten oder alle anzeigen", "es": "Seleccione un planeta específico o mostrar todos", "fr": "Sélectionnez une planète spécifique ou afficher tout", "it": "Seleziona un pianeta specifico o mostra tutti", "nl": "Selecteer een specifieke planeet of toon alles", "pl": "Wybierz konkretną planetę lub pokaż wszystkie", "pt": "Selecione um planeta específico ou mostrar todos", "ru": "Выберите конкретную планету или показать все", "ja": "特定の惑星を選択するか、すべてを表示", "zh": "选择特定行星或显示全部", "ko": "특정 행성을 선택하거나 모두 표시"},
            "options": [
                {"value": "all", "label": {"en": "All Planets", "de": "Alle Planeten", "es": "Todos los Planetas", "fr": "Toutes les Planètes", "it": "Tutti i Pianeti", "nl": "Alle Planeten", "pl": "Wszystkie Planety", "pt": "Todos os Planetas", "ru": "Все Планеты", "ja": "すべての惑星", "zh": "所有行星", "ko": "모든 행성"}},
                {"value": "mercury", "label": {"en": "Mercury", "de": "Merkur", "es": "Mercurio", "fr": "Mercure", "it": "Mercurio", "nl": "Mercurius", "pl": "Merkury", "pt": "Mercúrio", "ru": "Меркурий", "ja": "水星", "zh": "水星", "ko": "수성"}},
                {"value": "venus", "label": {"en": "Venus", "de": "Venus", "es": "Venus", "fr": "Vénus", "it": "Venere", "nl": "Venus", "pl": "Wenus", "pt": "Vênus", "ru": "Венера", "ja": "金星", "zh": "金星", "ko": "금성"}},
                {"value": "earth", "label": {"en": "Earth", "de": "Erde", "es": "Tierra", "fr": "Terre", "it": "Terra", "nl": "Aarde", "pl": "Ziemia", "pt": "Terra", "ru": "Земля", "ja": "地球", "zh": "地球", "ko": "지구"}},
                {"value": "mars", "label": {"en": "Mars", "de": "Mars", "es": "Marte", "fr": "Mars", "it": "Marte", "nl": "Mars", "pl": "Mars", "pt": "Marte", "ru": "Марс", "ja": "火星", "zh": "火星", "ko": "화성"}},
                {"value": "jupiter", "label": {"en": "Jupiter", "de": "Jupiter", "es": "Júpiter", "fr": "Jupiter", "it": "Giove", "nl": "Jupiter", "pl": "Jowisz", "pt": "Júpiter", "ru": "Юпитер", "ja": "木星", "zh": "木星", "ko": "목성"}},
                {"value": "saturn", "label": {"en": "Saturn", "de": "Saturn", "es": "Saturno", "fr": "Saturne", "it": "Saturno", "nl": "Saturnus", "pl": "Saturn", "pt": "Saturno", "ru": "Сатурн", "ja": "土星", "zh": "土星", "ko": "토성"}},
                {"value": "uranus", "label": {"en": "Uranus", "de": "Uranus", "es": "Urano", "fr": "Uranus", "it": "Urano", "nl": "Uranus", "pl": "Uran", "pt": "Urano", "ru": "Уран", "ja": "天王星", "zh": "天王星", "ko": "천왕성"}},
                {"value": "neptune", "label": {"en": "Neptune", "de": "Neptun", "es": "Neptuno", "fr": "Neptune", "it": "Nettuno", "nl": "Neptunus", "pl": "Neptun", "pt": "Netuno", "ru": "Нептун", "ja": "海王星", "zh": "海王星", "ko": "해왕성"}},
                {"value": "pluto", "label": {"en": "Pluto", "de": "Pluto", "es": "Plutón", "fr": "Pluton", "it": "Plutone", "nl": "Pluto", "pl": "Pluton", "pt": "Plutão", "ru": "Плутон", "ja": "冥王星", "zh": "冥王星", "ko": "명왕성"}}
            ]
        },
        "coordinate_system": {
            "type": "select",
            "default": "heliocentric",
            "label": {"en": "Coordinate System", "de": "Koordinatensystem", "es": "Sistema de Coordenadas", "fr": "Système de Coordonnées", "it": "Sistema di Coordinate", "nl": "Coördinatensysteem", "pl": "Układ Współrzędnych", "pt": "Sistema de Coordenadas", "ru": "Система Координат", "ja": "座標系", "zh": "坐标系", "ko": "좌표계"},
            "description": {"en": "Choose coordinate reference", "de": "Koordinatenreferenz wählen", "es": "Elegir referencia de coordenadas", "fr": "Choisir référence de coordonnées", "it": "Scegli riferimento coordinate", "nl": "Kies coördinaatreferentie", "pl": "Wybierz odniesienie współrzędnych", "pt": "Escolher referência de coordenadas", "ru": "Выберите систему отсчёта", "ja": "座標基準を選択", "zh": "选择坐标参考", "ko": "좌표 기준 선택"},
            "options": [
                {"value": "heliocentric", "label": {"en": "Heliocentric (Sun-centered)", "de": "Heliozentrisch (Sonnenzentriert)", "es": "Heliocéntrico (Centrado en el Sol)", "fr": "Héliocentrique (Centré sur le Soleil)", "it": "Eliocentrico (Centrato sul Sole)", "nl": "Heliocentrisch (Zon-gecentreerd)", "pl": "Heliocentryczny (Słońce w centrum)", "pt": "Heliocêntrico (Centrado no Sol)", "ru": "Гелиоцентрическая (Солнце в центре)", "ja": "太陽中心（太陽中心）", "zh": "日心（以太阳为中心）", "ko": "태양 중심(태양 중심)"}},
                {"value": "geocentric", "label": {"en": "Geocentric (Earth-centered)", "de": "Geozentrisch (Erdzentriert)", "es": "Geocéntrico (Centrado en la Tierra)", "fr": "Géocentrique (Centré sur la Terre)", "it": "Geocentrico (Centrato sulla Terra)", "nl": "Geocentrisch (Aarde-gecentreerd)", "pl": "Geocentryczny (Ziemia w centrum)", "pt": "Geocêntrico (Centrado na Terra)", "ru": "Геоцентрическая (Земля в центре)", "ja": "地球中心（地球中心）", "zh": "地心（以地球为中心）", "ko": "지구 중심(지구 중심)"}}
            ]
        },
        "show_distance": {
            "type": "boolean",
            "default": True,
            "label": {"en": "Show Distance", "de": "Entfernung anzeigen", "es": "Mostrar Distancia", "fr": "Afficher Distance", "it": "Mostra Distanza", "nl": "Toon Afstand", "pl": "Pokaż Odległość", "pt": "Mostrar Distância", "ru": "Показать Расстояние", "ja": "距離を表示", "zh": "显示距离", "ko": "거리 표시"},
            "description": {"en": "Display distance in AU and km", "de": "Entfernung in AE und km anzeigen", "es": "Mostrar distancia en UA y km", "fr": "Afficher distance en UA et km", "it": "Mostra distanza in UA e km", "nl": "Toon afstand in AE en km", "pl": "Pokaż odległość w AU i km", "pt": "Mostrar distância em UA e km", "ru": "Показать расстояние в а.е. и км", "ja": "AUとkmで距離を表示", "zh": "以AU和公里显示距离", "ko": "AU와 km로 거리 표시"}
        },
        "show_constellation": {
            "type": "boolean",
            "default": True,
            "label": {"en": "Show Constellation", "de": "Sternbild anzeigen", "es": "Mostrar Constelación", "fr": "Afficher Constellation", "it": "Mostra Costellazione", "nl": "Toon Sterrenbeeld", "pl": "Pokaż Konstelację", "pt": "Mostrar Constelação", "ru": "Показать Созвездие", "ja": "星座を表示", "zh": "显示星座", "ko": "별자리 표시"},
            "description": {"en": "Display zodiac constellation", "de": "Tierkreiszeichen anzeigen", "es": "Mostrar constelación zodiacal", "fr": "Afficher constellation du zodiaque", "it": "Mostra costellazione zodiacale", "nl": "Toon sterrenbeeld", "pl": "Pokaż konstelację zodiaku", "pt": "Mostrar constelação zodiacal", "ru": "Показать созвездие зодиака", "ja": "黄道星座を表示", "zh": "显示黄道星座", "ko": "황도 별자리 표시"}
        },
        "show_retrograde": {
            "type": "boolean",
            "default": True,
            "label": {"en": "Show Retrograde Status", "de": "Retrograd-Status anzeigen", "es": "Mostrar Estado Retrógrado", "fr": "Afficher État Rétrograde", "it": "Mostra Stato Retrogrado", "nl": "Toon Retrograde Status", "pl": "Pokaż Status Retrograde", "pt": "Mostrar Estado Retrógrado", "ru": "Показать Ретроградный Статус", "ja": "逆行状態を表示", "zh": "显示逆行状态", "ko": "역행 상태 표시"},
            "description": {"en": "Indicate when planets appear to move backwards", "de": "Anzeigen, wenn Planeten rückwärts zu laufen scheinen", "es": "Indicar cuando los planetas parecen moverse hacia atrás", "fr": "Indiquer quand les planètes semblent reculer", "it": "Indicare quando i pianeti sembrano muoversi all'indietro", "nl": "Aangeven wanneer planeten achteruit lijken te bewegen", "pl": "Wskazać, gdy planety wydają się cofać", "pt": "Indicar quando os planetas parecem mover-se para trás", "ru": "Показывать, когда планеты движутся назад", "ja": "惑星が後退しているように見えるときを示す", "zh": "指示行星逆行", "ko": "행성이 뒤로 움직이는 것처럼 보일 때 표시"}
        },
        "show_visibility": {
            "type": "boolean",
            "default": True,
            "label": {"en": "Show Visibility Info", "de": "Sichtbarkeitsinfo anzeigen", "es": "Mostrar Info de Visibilidad", "fr": "Afficher Info de Visibilité", "it": "Mostra Info Visibilità", "nl": "Toon Zichtbaarheidsinfo", "pl": "Pokaż Info o Widoczności", "pt": "Mostrar Info de Visibilidade", "ru": "Показать Инфо о Видимости", "ja": "可視性情報を表示", "zh": "显示可见性信息", "ko": "가시성 정보 표시"},
            "description": {"en": "Show best viewing times for planets", "de": "Beste Beobachtungszeiten anzeigen", "es": "Mostrar mejores horarios de observación", "fr": "Afficher meilleurs moments d'observation", "it": "Mostra migliori orari di osservazione", "nl": "Toon beste waarnemingstijden", "pl": "Pokaż najlepsze czasy obserwacji", "pt": "Mostrar melhores horários de observação", "ru": "Показать лучшее время наблюдения", "ja": "最適な観測時間を表示", "zh": "显示最佳观测时间", "ko": "최적 관측 시간 표시"}
        },
        "enable_visualization": {
            "type": "boolean",
            "default": True,
            "label": {"en": "Enable Visualization", "de": "Visualisierung aktivieren", "es": "Habilitar Visualización", "fr": "Activer Visualisation", "it": "Abilita Visualizzazione", "nl": "Visualisatie Inschakelen", "pl": "Włącz Wizualizację", "pt": "Habilitar Visualização", "ru": "Включить Визуализацию", "ja": "視覚化を有効にする", "zh": "启用可视化", "ko": "시각화 활성화"},
            "description": {"en": "Generate SVG/PNG solar system map", "de": "SVG/PNG-Sonnensystemkarte generieren", "es": "Generar mapa del sistema solar SVG/PNG", "fr": "Générer carte système solaire SVG/PNG", "it": "Genera mappa sistema solare SVG/PNG", "nl": "Genereer SVG/PNG zonnestelselkaart", "pl": "Generuj mapę Układu Słonecznego SVG/PNG", "pt": "Gerar mapa do sistema solar SVG/PNG", "ru": "Создать карту солнечной системы SVG/PNG", "ja": "太陽系マップSVG/PNGを生成", "zh": "生成SVG/PNG太阳系地图", "ko": "SVG/PNG 태양계 지도 생성"}
        },
        "visualization_scale": {
            "type": "select",
            "default": "logarithmic",
            "label": {"en": "Visualization Scale", "de": "Visualisierungsskala", "es": "Escala de Visualización", "fr": "Échelle de Visualisation", "it": "Scala di Visualizzazione", "nl": "Visualisatieschaal", "pl": "Skala Wizualizacji", "pt": "Escala de Visualização", "ru": "Масштаб Визуализации", "ja": "視覚化スケール", "zh": "可视化比例", "ko": "시각화 축척"},
            "description": {"en": "Choose scale for orbit visualization", "de": "Skalierung für Umlaufbahn-Visualisierung wählen", "es": "Elegir escala para visualización de órbitas", "fr": "Choisir l'échelle pour la visualisation des orbites", "it": "Scegli scala per visualizzazione orbite", "nl": "Kies schaal voor baanvisualisatie", "pl": "Wybierz skalę dla wizualizacji orbit", "pt": "Escolher escala para visualização de órbitas", "ru": "Выберите масштаб для визуализации орбит", "ja": "軌道視覚化のスケールを選択", "zh": "选择轨道可视化的比例", "ko": "궤도 시각화를 위한 축척 선택"},
            "options": [
                {"value": "logarithmic", "label": {"en": "Logarithmic (All visible)", "de": "Logarithmisch (Alles sichtbar)", "es": "Logarítmica (Todo visible)", "fr": "Logarithmique (Tout visible)", "it": "Logaritmica (Tutto visibile)", "nl": "Logaritmisch (Alles zichtbaar)", "pl": "Logarytmiczna (Wszystko widoczne)", "pt": "Logarítmica (Tudo visível)", "ru": "Логарифмическая (Всё видно)", "ja": "対数（すべて見える）", "zh": "对数（全部可见）", "ko": "로그(모두 표시)"}},
                {"value": "linear", "label": {"en": "Linear (True scale)", "de": "Linear (Wahrer Maßstab)", "es": "Lineal (Escala real)", "fr": "Linéaire (Échelle réelle)", "it": "Lineare (Scala reale)", "nl": "Lineair (Ware schaal)", "pl": "Liniowa (Prawdziwa skala)", "pt": "Linear (Escala real)", "ru": "Линейная (Истинный масштаб)", "ja": "線形（実際のスケール）", "zh": "线性（真实比例）", "ko": "선형(실제 축척)"}},
                {"value": "compressed", "label": {"en": "Compressed (Inner focus)", "de": "Komprimiert (Inneres System)", "es": "Comprimida (Interior)", "fr": "Compressée (Intérieur)", "it": "Compressa (Interno)", "nl": "Gecomprimeerd (Binnenste)", "pl": "Skompresowana (Wewnętrzny)", "pt": "Comprimida (Interior)", "ru": "Сжатая (Внутренняя)", "ja": "圧縮（内側）", "zh": "压缩（内部）", "ko": "압축(내부)"}}
            ]
        }
    }
}


class SolarSystemSensor(AlternativeTimeSensorBase):
    """Sensor for displaying solar system planetary positions."""

    UPDATE_INTERVAL = UPDATE_INTERVAL
    AU_TO_KM = 149_597_870.7

    # -------------- ctor --------------
    def __init__(self, base_name: str, hass: HomeAssistant) -> None:
        # language must exist before anything else
        self._user_language = 'en'
        super().__init__(base_name, hass)

        try:
            if hass and hasattr(hass, "config"):
                lang = getattr(hass.config, "language", None)
                if lang:
                    self._user_language = lang
        except Exception:
            pass

        calendar_name = self._translate('name', 'Solar System Positions')
        self._attr_name = f"{base_name} {calendar_name}"
        self._attr_unique_id = f"solar_system_{base_name.lower().replace(' ', '_')}"

        self._update_interval = timedelta(seconds=UPDATE_INTERVAL)
        self._solar_data = CALENDAR_INFO.get("solar_data", {})
        self._planets = self._solar_data.get("planets", {})
        self._constellations = self._solar_data.get("constellations", [])

        default_latitude = 49.14
        default_longitude = 9.22
        if hass and hasattr(hass, 'config'):
            default_latitude = hass.config.latitude
            default_longitude = hass.config.longitude

        # defaults
        self._display_planet = "all"
        self._coordinate_system = "heliocentric"
        self._show_distance = True
        self._show_constellation = True
        self._show_retrograde = True
        self._show_visibility = True
        self._enable_visualization = True
        self._visualization_scale = "logarithmic"
        self._show_kuiper_belt = True

        self._observer_latitude = default_latitude
        self._observer_longitude = default_longitude

        self._positions_info: Dict[str, Any] = {}
        self._state = "Initializing..."
        self._first_update = True

        # Pre-generated visualization data (generated in update(), used in extra_state_attributes)
        self._cached_svg: Optional[str] = None
        self._cached_png_data_uri: Optional[str] = None
        self._cached_local_paths: Dict[str, str] = {}

    # -------------- helpers --------------
    def _lang(self) -> str:
        try:
            lang = (self._user_language or 'en').lower()
            # Handle language variants like "de-DE" -> "de"
            if '-' in lang:
                lang = lang.split('-')[0]
            return lang
        except Exception:
            return 'en'

    def _translate(self, key: str, default: Optional[str] = None) -> str:
        # fallback if base doesn't supply translate
        try:
            section = CALENDAR_INFO.get(key)
            if isinstance(section, dict):
                return section.get(self._lang(), section.get("en", default or key))
        except Exception:
            pass
        return default or key

    def _get_solar_data_text(self, key: str, default: str = "") -> str:
        """Get localized text from solar_data section."""
        try:
            section = self._solar_data.get(key, {})
            if isinstance(section, dict):
                return section.get(self._lang(), section.get("en", default))
        except Exception:
            pass
        return default

    def _get_month_names(self) -> List[str]:
        """Get localized month names."""
        months = self._solar_data.get("months", {})
        return months.get(self._lang(), months.get("en", ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]))

    def _get_planet_name(self, planet_id: str) -> str:
        pdata = self._planets.get(planet_id, {})
        names = pdata.get("name", {})
        return names.get(self._lang(), names.get("en", planet_id.title()))

    def _get_planet_color(self, planet_id: str) -> str:
        pdata = self._planets.get(planet_id, {})
        return pdata.get("color", "#FFFFFF")

    def _get_constellation(self, longitude: float) -> tuple[str, str]:
        lon = longitude % 360.0
        for c in self._constellations:
            start = float(c["start"])
            end = (start + 30.0) % 360.0
            if start <= lon < end or (start > end and (lon >= start or lon < end)):
                names = c.get("name", {})
                return names.get(self._lang(), names.get("en", "Unknown")), c.get("symbol", "")
        return "Unknown", ""

    # -------------- positions --------------
    def _calculate_planet_position(self, planet_id: str, jd: float) -> Dict[str, Any]:
        """
        Calculate heliocentric position of a planet using Keplerian orbital elements.

        FIXED in v1.4.0: Corrected the calculation of heliocentric longitude.
        The previous version incorrectly calculated the mean anomaly and added
        perihelion_longitude twice, resulting in incorrect positions.

        The correct formulas (per JPL's "Approximate Positions of the Planets"):
        1. L = L0 + n*d  (Mean Longitude)
        2. M = L - ω     (Mean Anomaly, where ω = perihelion_longitude)
        3. C = equation_of_center(M, e)
        4. true_longitude = L + C  (NOT v + ω!)
        """
        p = self._planets[planet_id]

        # Deep-space probes: radial outward (very rough), fixed longitude anchor
        if p.get("special_type") == "probe":
            # elapsed years since J2000 (JD 2451545.0 ~ 2000-01-01 12:00 TT)
            years = (jd - 2451545.0) / 365.25
            r = max(1.0, float(p.get("anchor_au", 100.0)) + years * float(p.get("speed_au_per_year", 3.5)))
            longi = float(p.get("anchor_longitude", 300.0)) % 360.0
            return {
                "longitude": longi,
                "distance": r,
                "mean_anomaly": 0.0,
                "true_anomaly": 0.0
            }

        # Planets - Standard Keplerian calculation (CORRECTED)
        d = jd - 2451545.0  # Days since J2000.0
        n = 360.0 / float(p["orbital_period"])  # Mean daily motion (degrees/day)

        # Step 1: Calculate Mean Longitude (L)
        # L = L0 + n*d, where L0 is mean_longitude_j2000
        L = (float(p["mean_longitude_j2000"]) + n * d) % 360.0

        # Step 2: Calculate Mean Anomaly (M)
        # M = L - ω, where ω is the longitude of perihelion
        omega = float(p["perihelion_longitude"])
        M = (L - omega + 360.0) % 360.0

        e = float(p["eccentricity"])

        # Step 3: Equation of center (simplified series expansion)
        # C ≈ (2e - e³/4)sin(M) + (5/4)e²sin(2M) + (13/12)e³sin(3M)
        M_rad = math.radians(M)
        C = (2.0 * e - (e**3) / 4.0) * math.sin(M_rad) * (180.0 / math.pi)
        C += (5.0 / 4.0) * (e**2) * math.sin(2.0 * M_rad) * (180.0 / math.pi)
        C += (13.0 / 12.0) * (e**3) * math.sin(3.0 * M_rad) * (180.0 / math.pi)

        # True anomaly
        v = M + C

        # Step 4: Heliocentric ecliptic longitude = L + C (true longitude)
        # This is the CORRECTED formula - we add C to L, not to v+ω
        longitude = (L + C) % 360.0

        # Distance from Sun (using the orbital equation)
        a = float(p["semi_major_axis"])
        v_rad = math.radians(v)
        r = a * (1 - e**2) / (1 + e * math.cos(v_rad))

        return {
            "longitude": longitude,
            "distance": r,
            "mean_anomaly": M,
            "true_anomaly": v,
            "mean_longitude": L,
            "equation_of_center": C
        }

    def _calculate_geocentric_position(self, planet_pos: Dict, earth_pos: Dict) -> Dict[str, Any]:
        geo_longitude = (planet_pos["longitude"] - earth_pos["longitude"]) % 360.0
        angle_diff = math.radians(planet_pos["longitude"] - earth_pos["longitude"])
        r_p = float(planet_pos["distance"])
        r_e = float(earth_pos["distance"])
        distance = math.sqrt(r_p**2 + r_e**2 - 2.0 * r_p * r_e * math.cos(angle_diff))
        return {"longitude": geo_longitude, "distance": distance}

    def _calculate_visibility(self, planet_id: str, dt: datetime) -> Dict[str, Any]:
        planet_pos = self._calculate_planet_position(planet_id, self._datetime_to_jd(dt))
        earth_pos = self._calculate_planet_position("earth", self._datetime_to_jd(dt))
        geo_pos = self._calculate_geocentric_position(planet_pos, earth_pos)
        elong = abs(geo_pos["longitude"] - earth_pos["longitude"])
        if elong > 180.0:
            elong = 360.0 - elong

        vis = {"elongation": elong, "visible": False, "rise_time": None, "set_time": None, "best_time": None, "visibility_period": None}
        if planet_id in ["mercury", "venus"]:
            if 15.0 < elong < 47.0:
                vis["visible"] = True
                if geo_pos["longitude"] < earth_pos["longitude"]:
                    vis.update({"visibility_period": "Morning star", "best_time": "Before sunrise", "rise_time": "03:00", "set_time": "06:00"})
                else:
                    vis.update({"visibility_period": "Evening star", "best_time": "After sunset", "rise_time": "18:00", "set_time": "21:00"})
        else:
            if elong > 60.0:
                vis["visible"] = True
                if elong > 150.0:
                    vis.update({"visibility_period": "All night", "best_time": "Midnight", "rise_time": "18:00", "set_time": "06:00"})
                elif elong > 90.0:
                    vis.update({"visibility_period": "Most of night", "best_time": "Late evening", "rise_time": "20:00", "set_time": "04:00"})
                else:
                    vis.update({"visibility_period": "Part of night", "best_time": "Evening", "rise_time": "20:00", "set_time": "23:00"})
        return vis

    # -------------- SVG --------------
    def _get_earth_reference_angle(self, now: datetime) -> float:
        """
        Calculate the reference angle to rotate the visualization so that
        January is at the top (12 o'clock position).

        We calculate the Earth's heliocentric longitude on January 1st of the
        current year and use that as the reference. All positions are then
        adjusted relative to this, so Earth appears at the top in January.
        """
        # Calculate Earth's position on January 1st of the current year
        jan1 = datetime(now.year, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        jd_jan1 = self._datetime_to_jd(jan1)
        earth_jan1_pos = self._calculate_planet_position("earth", jd_jan1)

        # This is the heliocentric longitude of Earth on Jan 1
        return earth_jan1_pos["longitude"]

    def _generate_visualization_svg(self) -> str:
        width, height = 600, 600
        cx, cy = width / 2, height / 2
        margin = 40
        maxR = min(cx, cy) - margin
        scale = self._visualization_scale

        now = datetime.now(timezone.utc)
        jd = self._datetime_to_jd(now)

        # Get the reference angle for January at top
        ref_angle = self._get_earth_reference_angle(now)

        def scale_r(d: float) -> float:
            d = max(0.0, float(d))
            if scale == "logarithmic":
                return math.log(d + 1.0) / math.log(50.0) * maxR
            elif scale == "compressed":
                return (d ** 0.5) / (50.0 ** 0.5) * maxR
            else:
                return (d / 50.0) * maxR

        def angle_to_xy(angle_deg: float, radius: float) -> Tuple[float, float]:
            """
            Convert angle in degrees to x, y coordinates.
            0° = top (12 o'clock), angles increase clockwise.
            """
            # In our coordinate system:
            # - 0° is at the top (negative y direction)
            # - Angles increase clockwise
            # Standard math: angle from positive x-axis, CCW
            # We want: angle from negative y-axis (top), CW
            # So: math_angle = 90° - our_angle (but we use radians)
            rad = math.radians(90.0 - angle_deg)
            x = cx + math.cos(rad) * radius
            y = cy - math.sin(rad) * radius
            return x, y

        # Prepare planet items for visualization
        items = []
        for pid, pdata in self._planets.items():
            if pdata.get("special_type") == "space_telescope":
                continue  # Skip JWST (removed)

            pname = self._get_planet_name(pid)
            pos_data = self._calculate_planet_position(pid, jd)

            # Adjust longitude relative to reference angle
            # This makes Earth at Jan 1 position appear at 0° (top)
            adjusted_lon = (pos_data["longitude"] - ref_angle + 360.0) % 360.0

            items.append({
                "id": pid,
                "name": pname,
                "lon": adjusted_lon,
                "dist": float(pos_data.get("distance", 1.0)),
                "color": self._get_planet_color(pid),
                "symbol": pdata.get("symbol", ""),
                "is_earth": pid == "earth",
                "is_dwarf_planet": pdata.get("is_dwarf_planet", False),
                "is_probe": pdata.get("special_type") == "probe"
            })

        # Get month names
        month_names = self._get_month_names()

        # SVG header
        out = []
        out.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{int(width)}" height="{int(height)}" viewBox="0 0 {int(width)} {int(height)}" role="img" aria-label="Solar System Map">')
        out.append('<defs>')
        out.append('<style><![CDATA[')
        out.append('text{font-family:Arial,system-ui,Segoe UI,Roboto,sans-serif}')
        out.append('.month-label{font-size:11px;fill:#AAAAAA}')
        out.append('.planet-label{font-size:10px;fill:#FFFFFF}')
        out.append('.earth-label{font-size:11px;fill:#4AE24A;font-weight:bold}')
        out.append('.footer{font-size:10px;fill:#888888}')
        out.append(']]></style>')
        out.append('</defs>')

        # Background
        out.append(f'<rect x="0" y="0" width="{int(width)}" height="{int(height)}" fill="#000022"/>')

        # Sun
        out.append(f'<circle cx="{cx}" cy="{cy}" r="18" fill="#FFD700" stroke="#FFA500" stroke-width="2"/>')
        out.append(f'<text x="{cx}" y="{cy + 5}" fill="#000000" font-size="16" text-anchor="middle">☉</text>')

        # Kuiper Belt (if enabled)
        if self._show_kuiper_belt:
            kb_inner = scale_r(30.0)  # ~30 AU
            kb_outer = scale_r(50.0)  # ~50 AU
            kb_mid = (kb_inner + kb_outer) / 2
            out.append(f'<circle cx="{cx}" cy="{cy}" r="{kb_inner:.2f}" fill="none" stroke="rgba(102,204,255,0.25)" stroke-width="1"/>')
            out.append(f'<circle cx="{cx}" cy="{cy}" r="{kb_outer:.2f}" fill="none" stroke="rgba(102,204,255,0.25)" stroke-width="1"/>')
            out.append(f'<circle cx="{cx}" cy="{cy}" r="{kb_mid:.2f}" fill="none" stroke="rgba(102,204,255,0.15)" stroke-width="{kb_outer - kb_inner:.0f}"/>')

        # Month markers
        for i in range(12):
            angle = i * 30.0
            x1, y1 = angle_to_xy(angle, 25)
            x2, y2 = angle_to_xy(angle, maxR + 20)
            out.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="#333333" stroke-width="1" stroke-dasharray="4,4"/>')
            lx, ly = angle_to_xy(angle, maxR + 35)
            out.append(f'<text x="{lx:.2f}" y="{ly:.2f}" class="month-label" text-anchor="middle" dominant-baseline="middle">{month_names[i]}</text>')

        # Orbits and planets
        for it in items:
            r = scale_r(it["dist"])

            # Draw orbit
            stroke_dash = "4,2" if it["is_dwarf_planet"] else "none"
            stroke_color = "#555555" if it["is_probe"] else "#444444"
            out.append(f'<circle cx="{cx}" cy="{cy}" r="{r:.2f}" fill="none" stroke="{stroke_color}" stroke-width="0.8" stroke-dasharray="{stroke_dash}"/>')

            # Draw planet
            x, y = angle_to_xy(it["lon"], r)

            if it["is_earth"]:
                # Earth with special "You are here" marker
                out.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="8" fill="{it["color"]}" stroke="#00FF00" stroke-width="2"/>')
                you_are_here = self._get_solar_data_text("you_are_here", "You are here")
                # Position label based on where Earth is
                label_offset_y = -18 if it["lon"] < 180 else 25
                out.append(f'<text x="{x:.2f}" y="{y + label_offset_y:.2f}" class="earth-label" text-anchor="middle">{it["symbol"]} {you_are_here}</text>')
            elif it["is_probe"]:
                # Probes: smaller marker
                out.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="3" fill="{it["color"]}" stroke="#FFFFFF" stroke-width="0.5"/>')
                out.append(f'<text x="{x:.2f}" y="{y - 8:.2f}" class="planet-label" text-anchor="middle" font-size="8">{it["name"]}</text>')
            else:
                # Regular planets
                planet_radius = 6 if it["id"] in ["jupiter", "saturn"] else 5
                out.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{planet_radius}" fill="{it["color"]}" stroke="#FFFFFF" stroke-width="1"/>')
                label = f'{it["symbol"]} {it["name"]}'
                out.append(f'<text x="{x:.2f}" y="{y - 10:.2f}" class="planet-label" text-anchor="middle">{label}</text>')

        # Footer
        footer_text = self._get_solar_data_text("footer", "Heliocentric · Sun at center · Jan at top")
        footer_text += f" · {scale.title()}"
        out.append(f'<text x="10" y="{height - 10}" class="footer">{footer_text}</text>')

        out.append("</svg>")
        return "\n".join(out)

    # -------------- PNG (optional) --------------
    def _text_size(self, draw, text: str, font) -> Tuple[int, int]:
        t = str(text)
        try:
            L, T, R, B = draw.textbbox((0, 0), t, font=font)
            return (R - L, B - T)
        except Exception:
            try:
                return font.getsize(t)
            except Exception:
                return (max(1, len(t) * 7), 12)

    def _generate_visualization_png_data_uri(self) -> str:
        if Image is None or ImageDraw is None:
            return ""

        width, height = 600, 600
        cx, cy = width // 2, height // 2
        margin = 40
        maxR = min(cx, cy) - margin
        scale = self._visualization_scale

        now = datetime.now(timezone.utc)
        jd = self._datetime_to_jd(now)
        ref_angle = self._get_earth_reference_angle(now)

        def scale_r(d: float) -> float:
            d = max(0.0, float(d))
            if scale == "logarithmic":
                return math.log(d + 1.0) / math.log(50.0) * maxR
            elif scale == "compressed":
                return (d ** 0.5) / (50.0 ** 0.5) * maxR
            else:
                return (d / 50.0) * maxR

        def angle_to_xy(angle_deg: float, radius: float) -> Tuple[int, int]:
            rad = math.radians(90.0 - angle_deg)
            x = cx + math.cos(rad) * radius
            y = cy - math.sin(rad) * radius
            return int(x), int(y)

        def hex_to_rgb(h: str, a: int = 255) -> tuple[int, int, int, int]:
            h = h.lstrip("#")
            return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)

        # Prepare planet items
        items = []
        for pid, pdata in self._planets.items():
            if pdata.get("special_type") == "space_telescope":
                continue
            pos_data = self._calculate_planet_position(pid, jd)
            adjusted_lon = (pos_data["longitude"] - ref_angle + 360.0) % 360.0
            items.append({
                "id": pid,
                "name": self._get_planet_name(pid),
                "lon": adjusted_lon,
                "dist": float(pos_data.get("distance", 1.0)),
                "color": self._get_planet_color(pid),
                "symbol": pdata.get("symbol", ""),
                "is_earth": pid == "earth",
                "is_dwarf_planet": pdata.get("is_dwarf_planet", False),
                "is_probe": pdata.get("special_type") == "probe"
            })

        # Create image
        img = Image.new("RGBA", (width, height), (0, 0, 34, 255))
        draw = ImageDraw.Draw(img)

        # Load fonts
        try:
            font_label = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 9)
        except Exception:
            font_label = ImageFont.load_default()
            font_small = font_label

        # Sun
        draw.ellipse((cx - 18, cy - 18, cx + 18, cy + 18), fill=(255, 215, 0, 255), outline=(255, 165, 0, 255), width=2)

        # Kuiper Belt
        if self._show_kuiper_belt:
            kb_inner = int(scale_r(30.0))
            kb_outer = int(scale_r(50.0))
            draw.ellipse((cx - kb_inner, cy - kb_inner, cx + kb_inner, cy + kb_inner),
                         outline=(102, 204, 255, 64), width=1)
            draw.ellipse((cx - kb_outer, cy - kb_outer, cx + kb_outer, cy + kb_outer),
                         outline=(102, 204, 255, 64), width=1)

        # Month markers
        month_names = self._get_month_names()
        for i in range(12):
            angle = i * 30.0
            x1, y1 = angle_to_xy(angle, 25)
            x2, y2 = angle_to_xy(angle, maxR + 20)
            draw.line([(x1, y1), (x2, y2)], fill=(51, 51, 51, 255), width=1)
            lx, ly = angle_to_xy(angle, maxR + 35)
            tw, th = self._text_size(draw, month_names[i], font_small)
            draw.text((lx - tw // 2, ly - th // 2), month_names[i], fill=(170, 170, 170, 255), font=font_small)

        # Orbits and planets
        for it in items:
            r = int(scale_r(it["dist"]))
            # Orbit
            draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(68, 68, 68, 255), width=1)
            # Planet
            x, y = angle_to_xy(it["lon"], r)
            planet_r = 8 if it["is_earth"] else (3 if it["is_probe"] else (6 if it["id"] in ["jupiter", "saturn"] else 5))
            if it["is_earth"]:
                draw.ellipse((x - planet_r, y - planet_r, x + planet_r, y + planet_r),
                             fill=hex_to_rgb(it["color"]),
                             outline=(0, 255, 0, 255),
                             width=2)
                label = f'{it["symbol"]} {self._get_solar_data_text("you_are_here", "You are here")}'
                tw, th = self._text_size(draw, label, font_label)
                draw.text((x - tw // 2, y - 18 - th), label, fill=(74, 226, 74, 255), font=font_label)
            else:
                draw.ellipse((x - planet_r, y - planet_r, x + planet_r, y + planet_r),
                             fill=hex_to_rgb(it["color"]),
                             outline=(255, 255, 255, 255),
                             width=1)
                label = f'{it["symbol"]} {it["name"]}'
                tw, th = self._text_size(draw, label, font_label)
                draw.text((x - tw // 2, y - 12 - th), label, fill=(255, 255, 255, 255), font=font_label)

        # Footer
        footer_text = self._get_solar_data_text("footer", "Heliocentric · Sun at center · Jan at top")
        footer_text += f" · {scale.title()}"
        tw, th = self._text_size(draw, footer_text, font_small)
        draw.text((10, height - 10 - th), footer_text, fill=(136, 136, 136, 255), font=font_small)

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        data = base64.b64encode(buf.getvalue()).decode("ascii")
        return "data:image/png;base64," + data

    # -------------- positions collector --------------
    def _calculate_positions(self, dt: datetime) -> Dict[str, Any]:
        jd = self._datetime_to_jd(dt)
        result: Dict[str, Any] = {
            "julian_date": jd,
            "timestamp": dt.isoformat(),
            "observer_location": {"latitude": self._observer_latitude, "longitude": self._observer_longitude},
            "positions": {}
        }
        earth_pos = None
        if "earth" in self._planets:
            earth_pos = self._calculate_planet_position("earth", jd)

        planets_to_calc = list(self._planets.keys()) if self._display_planet == "all" else [self._display_planet]
        for planet_id in planets_to_calc:
            if planet_id not in self._planets:
                continue
            if self._planets.get(planet_id, {}).get("special_type") == "space_telescope":
                continue  # Skip JWST

            helio_pos = self._calculate_planet_position(planet_id, jd)
            position = self._calculate_geocentric_position(helio_pos, earth_pos) if (self._coordinate_system == "geocentric" and earth_pos and planet_id != "earth") else helio_pos

            cname, csym = self._get_constellation(position['longitude'])
            position['constellation'] = cname
            position['constellation_symbol'] = csym

            position['distance_au'] = float(position['distance'])
            position['distance_km'] = position['distance_au'] * self.AU_TO_KM
            position['distance_million_km'] = position['distance_km'] / 1e6

            if self._show_visibility and self._planets.get(planet_id, {}).get("special_type") not in ("probe",):
                if planet_id != "earth":
                    position['visibility'] = self._calculate_visibility(planet_id, dt)

            position['retrograde'] = False  # simplified placeholder

            pname = self._get_planet_name(planet_id)
            result["positions"][pname] = position

        return result

    # -------------- time conversions --------------
    def _datetime_to_jd(self, dt: datetime) -> float:
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
        a = int(year / 100)
        b = 2 - a + int(a / 4)
        jd = int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + b - 1524.5
        return float(jd)

    def _jd_to_datetime(self, jd: float) -> datetime:
        jd = float(jd) + 0.5
        z = int(jd)
        f = jd - z
        if z < 2299161:
            a = z
        else:
            alpha = int((z - 1867216.25) / 36524.25)
            a = z + 1 + alpha - int(alpha / 4)
        b = a + 1524
        c = int((b - 122.1) / 365.25)
        d = int(365.25 * c)
        e = int((b - d) / 30.6001)
        day = b - d - int(30.6001 * e) + f
        month = e - 1 if e < 14 else e - 13
        year = c - 4716 if month > 2 else c - 4715
        day_i = int(day)
        frac = day - day_i
        seconds = int(round(frac * 86400.0))
        hh = seconds // 3600
        mm = (seconds % 3600) // 60
        ss = seconds % 60
        return datetime(year, int(month), int(day_i), hh, mm, ss, tzinfo=timezone.utc)

    # -------------- asset writing (/local) --------------
    def _write_local_assets(self, svg: str, png_data_uri: Optional[str]) -> Dict[str, str]:
        """Write SVG/PNG under /config/www/alternative_time and return /local paths."""
        out: Dict[str, str] = {}
        try:
            base = self.hass.config.path("www/alternative_time")
            os.makedirs(base, exist_ok=True)
            svg_path = os.path.join(base, "solar_system_map.svg")
            with open(svg_path, "w", encoding="utf-8") as f:
                f.write(svg)
            out["local_svg_path"] = "/local/alternative_time/solar_system_map.svg"

            if png_data_uri and png_data_uri.startswith("data:image/png;base64,"):
                png_path = os.path.join(base, "solar_system_map.png")
                with open(png_path, "wb") as f:
                    f.write(base64.b64decode(png_data_uri.split(",", 1)[1]))
                out["local_png_path"] = "/local/alternative_time/solar_system_map.png"
        except Exception as e:
            _LOGGER.warning("Writing local assets failed: %s", e)
        return out

    # -------------- HA attributes/state --------------
    @property
    def state(self) -> str:
        return self._state

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        attrs = super().extra_state_attributes

        if self._positions_info:
            attrs.update(self._positions_info)
            attrs["description"] = self._translate("description")
            attrs["reference"] = CALENDAR_INFO.get("reference_url", "")
            attrs["config"] = {
                "display_planet": self._display_planet,
                "coordinate_system": self._coordinate_system,
                "show_distance": self._show_distance,
                "show_constellation": self._show_constellation,
                "show_retrograde": self._show_retrograde,
                "show_visibility": self._show_visibility,
                "enable_visualization": self._enable_visualization,
                "visualization_scale": self._visualization_scale
            }

            # Use cached visualization data (generated in update() to avoid blocking)
            if self._enable_visualization and self._cached_svg:
                attrs["solar_system_map_svg"] = self._cached_svg

                if self._cached_png_data_uri:
                    attrs["solar_system_map_png"] = self._cached_png_data_uri

                # entity_picture: prefer PNG, fallback to SVG data URI
                if self._cached_png_data_uri:
                    attrs["entity_picture"] = self._cached_png_data_uri
                else:
                    # SVG as data-uri
                    svg_b64 = base64.b64encode(self._cached_svg.encode("utf-8")).decode("ascii")
                    attrs["entity_picture"] = "data:image/svg+xml;base64," + svg_b64

                # Add local paths if available
                attrs.update(self._cached_local_paths)

        return attrs

    # -------------- formatting --------------
    def _format_position(self, planet_id: str, position: Dict[str, Any]) -> str:
        planet_name = self._get_planet_name(planet_id)
        symbol = self._planets[planet_id].get("symbol", "")
        parts = [f"{symbol} {planet_name}:"]
        parts.append(f"{position['longitude']:.1f}°")
        if self._show_distance:
            au = position['distance']
            km = au * self.AU_TO_KM
            parts.append(f"{au:.3f} AU ({km/1e6:.1f} Mio km)")
        if self._show_constellation:
            const_name, const_symbol = self._get_constellation(position['longitude'])
            parts.append(f"{const_symbol} {const_name}")
        if self._show_visibility and "visibility" in position:
            vis = position["visibility"]
            if vis.get("visible"):
                parts.append(f"👁 {vis.get('rise_time','N/A')}-{vis.get('set_time','N/A')}")
            else:
                parts.append("🚫 Not visible")
        if self._show_retrograde and position.get("retrograde", False):
            parts.append("℞")
        return " | ".join(parts)

    # -------------- HA update --------------
    def update(self) -> None:
        if self.hass and hasattr(self.hass, 'config'):
            self._user_language = getattr(self.hass.config, 'language', 'en') or 'en'

        options = self.get_plugin_options()
        if options:
            self._display_planet = options.get("display_planet", self._display_planet)
            self._coordinate_system = options.get("coordinate_system", self._coordinate_system)
            self._show_distance = options.get("show_distance", self._show_distance)
            self._show_constellation = options.get("show_constellation", self._show_constellation)
            self._show_retrograde = options.get("show_retrograde", self._show_retrograde)
            self._show_visibility = options.get("show_visibility", self._show_visibility)
            self._enable_visualization = options.get("enable_visualization", self._enable_visualization)
            self._visualization_scale = options.get("visualization_scale", self._visualization_scale)

        try:
            now = datetime.now(timezone.utc)
            self._positions_info = self._calculate_positions(now)

            # Generate visualizations here where blocking I/O is allowed
            if self._enable_visualization:
                try:
                    self._cached_svg = self._generate_visualization_svg()
                except Exception as e:
                    _LOGGER.warning("SVG generation failed: %s", e)
                    self._cached_svg = None

                try:
                    self._cached_png_data_uri = self._generate_visualization_png_data_uri()
                except Exception as e:
                    _LOGGER.debug("PNG generation failed: %s", e)
                    self._cached_png_data_uri = None

                # Write files to /local (blocking I/O is OK here in update())
                if self._cached_svg:
                    try:
                        self._cached_local_paths = self._write_local_assets(
                            self._cached_svg,
                            self._cached_png_data_uri if self._cached_png_data_uri else None
                        )
                    except Exception as e:
                        _LOGGER.warning("Writing local assets failed: %s", e)
                        self._cached_local_paths = {}
            else:
                self._cached_svg = None
                self._cached_png_data_uri = None
                self._cached_local_paths = {}

            if self._display_planet == "all":
                num_objects = len(self._positions_info.get("positions", {}))
                self._state = f"{num_objects} objects tracked"
            else:
                planet_name = self._get_planet_name(self._display_planet)
                pos = self._positions_info.get("positions", {}).get(planet_name, {})
                self._state = self._format_position(self._display_planet, pos) if pos else f"{planet_name}: No data"
        except Exception as e:
            _LOGGER.exception("Error calculating solar system positions")
            self._state = "Error"
            self._positions_info = {"error": str(e)}

        _LOGGER.debug("Updated Solar System to %s", self._state)


__all__ = ["SolarSystemSensor", "CALENDAR_INFO"]
