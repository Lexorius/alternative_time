"""Solar System Planetary Positions implementation - Version 1.0.0
Displays current positions of planets in our solar system.

Shows heliocentric longitude, distance from Sun, and constellation location.
Example: Mars: 45.2° | 1.52 AU | Taurus
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import math
import logging
from typing import Dict, Any, Optional

from homeassistant.core import HomeAssistant
from ..sensor import AlternativeTimeSensorBase

_LOGGER = logging.getLogger(__name__)

# ============================================
# CALENDAR METADATA
# ============================================

# Update interval in seconds (300 seconds = 5 minutes, planets move slowly)
UPDATE_INTERVAL = 300

# Complete calendar information for auto-discovery
CALENDAR_INFO = {
    "id": "solar_system",
    "version": "1.0.0",
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
        "en": "Current positions of planets in the solar system",
        "de": "Aktuelle Positionen der Planeten im Sonnensystem",
        "es": "Posiciones actuales de los planetas en el sistema solar",
        "fr": "Positions actuelles des planètes dans le système solaire",
        "it": "Posizioni attuali dei pianeti nel sistema solare",
        "nl": "Huidige posities van planeten in het zonnestelsel",
        "pl": "Aktualne pozycje planet w Układzie Słonecznym",
        "pt": "Posições atuais dos planetas no sistema solar",
        "ru": "Текущие позиции планет в Солнечной системе",
        "ja": "太陽系の惑星の現在位置",
        "zh": "太阳系行星的当前位置",
        "ko": "태양계 행성의 현재 위치"
    },
    
    # Solar system specific data
    "solar_data": {
        # Planets with their orbital elements (simplified Keplerian elements)
        # Values are approximate for epoch J2000.0
        "planets": {
            "mercury": {
                "name": {
                    "en": "Mercury", "de": "Merkur", "es": "Mercurio", "fr": "Mercure",
                    "it": "Mercurio", "nl": "Mercurius", "pl": "Merkury", "pt": "Mercúrio",
                    "ru": "Меркурий", "ja": "水星", "zh": "水星", "ko": "수성"
                },
                "symbol": "☿",
                "semi_major_axis": 0.387098,  # AU
                "eccentricity": 0.205635,
                "inclination": 7.005,  # degrees
                "mean_longitude": 252.250,  # degrees at J2000
                "perihelion_longitude": 77.456,
                "orbital_period": 87.969  # days
            },
            "venus": {
                "name": {
                    "en": "Venus", "de": "Venus", "es": "Venus", "fr": "Vénus",
                    "it": "Venere", "nl": "Venus", "pl": "Wenus", "pt": "Vênus",
                    "ru": "Венера", "ja": "金星", "zh": "金星", "ko": "금성"
                },
                "symbol": "♀",
                "semi_major_axis": 0.723332,
                "eccentricity": 0.006772,
                "inclination": 3.395,
                "mean_longitude": 181.979,
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
                "semi_major_axis": 1.000000,
                "eccentricity": 0.016709,
                "inclination": 0.000,
                "mean_longitude": 100.464,
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
                "semi_major_axis": 1.523679,
                "eccentricity": 0.093400,
                "inclination": 1.850,
                "mean_longitude": 355.433,
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
                "semi_major_axis": 5.202887,
                "eccentricity": 0.048498,
                "inclination": 1.303,
                "mean_longitude": 34.351,
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
                "semi_major_axis": 9.536676,
                "eccentricity": 0.053862,
                "inclination": 2.485,
                "mean_longitude": 50.077,
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
                "semi_major_axis": 19.189165,
                "eccentricity": 0.047257,
                "inclination": 0.772,
                "mean_longitude": 314.055,
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
                "semi_major_axis": 30.069923,
                "eccentricity": 0.008859,
                "inclination": 1.769,
                "mean_longitude": 304.880,
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
                "semi_major_axis": 39.482117,
                "eccentricity": 0.2488,
                "inclination": 17.16,
                "mean_longitude": 238.929,
                "perihelion_longitude": 224.067,
                "orbital_period": 90560.0
            },
            "jwst": {
                "name": {
                    "en": "James Webb Space Telescope", "de": "James-Webb-Weltraumteleskop", 
                    "es": "Telescopio Espacial James Webb", "fr": "Télescope Spatial James Webb",
                    "it": "Telescopio Spaziale James Webb", "nl": "James Webb Ruimtetelescoop",
                    "pl": "Kosmiczny Teleskop Jamesa Webba", "pt": "Telescópio Espacial James Webb",
                    "ru": "Космический телескоп Джеймса Уэбба", "ja": "ジェイムズ・ウェッブ宇宙望遠鏡",
                    "zh": "詹姆斯·韦伯太空望远镜", "ko": "제임스 웹 우주 망원경"
                },
                "symbol": "🔭",
                "semi_major_axis": 1.01,  # ~1.01 AU (L2 point is about 1.5 million km from Earth)
                "eccentricity": 0.0,  # Halo orbit around L2
                "inclination": 0.0,
                "mean_longitude": 0.0,  # Stays aligned with Earth-Sun line
                "perihelion_longitude": 0.0,
                "orbital_period": 365.256,  # Orbits with Earth around the Sun
                "special_type": "space_telescope",
                "location": "L2",
                "distance_from_earth_km": 1500000  # 1.5 million km
            }
        },
        
        # Zodiac constellations for position reference
        "constellations": [
            {"name": {
                "en": "Aries", "de": "Widder", "es": "Aries", "fr": "Bélier",
                "it": "Ariete", "nl": "Ram", "pl": "Baran", "pt": "Áries",
                "ru": "Овен", "ja": "牡羊座", "zh": "白羊座", "ko": "양자리"
            }, "start": 0, "symbol": "♈"},
            {"name": {
                "en": "Taurus", "de": "Stier", "es": "Tauro", "fr": "Taureau",
                "it": "Toro", "nl": "Stier", "pl": "Byk", "pt": "Touro",
                "ru": "Телец", "ja": "牡牛座", "zh": "金牛座", "ko": "황소자리"
            }, "start": 30, "symbol": "♉"},
            {"name": {
                "en": "Gemini", "de": "Zwillinge", "es": "Géminis", "fr": "Gémeaux",
                "it": "Gemelli", "nl": "Tweelingen", "pl": "Bliźnięta", "pt": "Gêmeos",
                "ru": "Близнецы", "ja": "双子座", "zh": "双子座", "ko": "쌍둥이자리"
            }, "start": 60, "symbol": "♊"},
            {"name": {
                "en": "Cancer", "de": "Krebs", "es": "Cáncer", "fr": "Cancer",
                "it": "Cancro", "nl": "Kreeft", "pl": "Rak", "pt": "Câncer",
                "ru": "Рак", "ja": "蟹座", "zh": "巨蟹座", "ko": "게자리"
            }, "start": 90, "symbol": "♋"},
            {"name": {
                "en": "Leo", "de": "Löwe", "es": "Leo", "fr": "Lion",
                "it": "Leone", "nl": "Leeuw", "pl": "Lew", "pt": "Leão",
                "ru": "Лев", "ja": "獅子座", "zh": "狮子座", "ko": "사자자리"
            }, "start": 120, "symbol": "♌"},
            {"name": {
                "en": "Virgo", "de": "Jungfrau", "es": "Virgo", "fr": "Vierge",
                "it": "Vergine", "nl": "Maagd", "pl": "Panna", "pt": "Virgem",
                "ru": "Дева", "ja": "乙女座", "zh": "处女座", "ko": "처녀자리"
            }, "start": 150, "symbol": "♍"},
            {"name": {
                "en": "Libra", "de": "Waage", "es": "Libra", "fr": "Balance",
                "it": "Bilancia", "nl": "Weegschaal", "pl": "Waga", "pt": "Libra",
                "ru": "Весы", "ja": "天秤座", "zh": "天秤座", "ko": "천칭자리"
            }, "start": 180, "symbol": "♎"},
            {"name": {
                "en": "Scorpio", "de": "Skorpion", "es": "Escorpio", "fr": "Scorpion",
                "it": "Scorpione", "nl": "Schorpioen", "pl": "Skorpion", "pt": "Escorpião",
                "ru": "Скорпион", "ja": "蠍座", "zh": "天蝎座", "ko": "전갈자리"
            }, "start": 210, "symbol": "♏"},
            {"name": {
                "en": "Sagittarius", "de": "Schütze", "es": "Sagitario", "fr": "Sagittaire",
                "it": "Sagittario", "nl": "Boogschutter", "pl": "Strzelec", "pt": "Sagitário",
                "ru": "Стрелец", "ja": "射手座", "zh": "射手座", "ko": "궁수자리"
            }, "start": 240, "symbol": "♐"},
            {"name": {
                "en": "Capricorn", "de": "Steinbock", "es": "Capricornio", "fr": "Capricorne",
                "it": "Capricorno", "nl": "Steenbok", "pl": "Koziorożec", "pt": "Capricórnio",
                "ru": "Козерог", "ja": "山羊座", "zh": "摩羯座", "ko": "염소자리"
            }, "start": 270, "symbol": "♑"},
            {"name": {
                "en": "Aquarius", "de": "Wassermann", "es": "Acuario", "fr": "Verseau",
                "it": "Acquario", "nl": "Waterman", "pl": "Wodnik", "pt": "Aquário",
                "ru": "Водолей", "ja": "水瓶座", "zh": "水瓶座", "ko": "물병자리"
            }, "start": 300, "symbol": "♒"},
            {"name": {
                "en": "Pisces", "de": "Fische", "es": "Piscis", "fr": "Poissons",
                "it": "Pesci", "nl": "Vissen", "pl": "Ryby", "pt": "Peixes",
                "ru": "Рыбы", "ja": "魚座", "zh": "双鱼座", "ko": "물고기자리"
            }, "start": 330, "symbol": "♓"}
        ]
    },
    
    # Reference URL
    "reference_url": "https://en.wikipedia.org/wiki/Planetary_positions",
    
    # Plugin configuration options
    "plugin_options": {
        "display_planet": {
            "type": "select",
            "default": "all",
            "label": {
                "en": "Display Planet",
                "de": "Planet anzeigen",
                "es": "Mostrar Planeta",
                "fr": "Afficher Planète",
                "it": "Mostra Pianeta",
                "nl": "Planeet Weergeven",
                "pl": "Wyświetl Planetę",
                "pt": "Exibir Planeta",
                "ru": "Показать планету",
                "ja": "惑星を表示",
                "zh": "显示行星",
                "ko": "행성 표시"
            },
            "description": {
                "en": "Select which planet to display or all planets",
                "de": "Wählen Sie welchen Planeten oder alle Planeten anzeigen",
                "es": "Seleccione qué planeta mostrar o todos los planetas",
                "fr": "Sélectionnez quelle planète afficher ou toutes les planètes",
                "it": "Seleziona quale pianeta visualizzare o tutti i pianeti",
                "nl": "Selecteer welke planeet weer te geven of alle planeten",
                "pl": "Wybierz planetę do wyświetlenia lub wszystkie planety",
                "pt": "Selecione qual planeta exibir ou todos os planetas",
                "ru": "Выберите планету для отображения или все планеты",
                "ja": "表示する惑星または全惑星を選択",
                "zh": "选择要显示的行星或所有行星",
                "ko": "표시할 행성 또는 모든 행성 선택"
            },
            "options": [
                {"value": "all", "label": {
                    "en": "All Planets", 
                    "de": "Alle Planeten",
                    "es": "Todos los Planetas",
                    "fr": "Toutes les Planètes",
                    "it": "Tutti i Pianeti",
                    "nl": "Alle Planeten",
                    "pl": "Wszystkie Planety",
                    "pt": "Todos os Planetas",
                    "ru": "Все планеты",
                    "ja": "すべての惑星",
                    "zh": "所有行星",
                    "ko": "모든 행성"
                }},
                {"value": "mercury", "label": {
                    "en": "Mercury",
                    "de": "Merkur",
                    "es": "Mercurio",
                    "fr": "Mercure",
                    "it": "Mercurio",
                    "nl": "Mercurius",
                    "pl": "Merkury",
                    "pt": "Mercúrio",
                    "ru": "Меркурий",
                    "ja": "水星",
                    "zh": "水星",
                    "ko": "수성"
                }},
                {"value": "venus", "label": {
                    "en": "Venus",
                    "de": "Venus",
                    "es": "Venus",
                    "fr": "Vénus",
                    "it": "Venere",
                    "nl": "Venus",
                    "pl": "Wenus",
                    "pt": "Vênus",
                    "ru": "Венера",
                    "ja": "金星",
                    "zh": "金星",
                    "ko": "금성"
                }},
                {"value": "earth", "label": {
                    "en": "Earth",
                    "de": "Erde",
                    "es": "Tierra",
                    "fr": "Terre",
                    "it": "Terra",
                    "nl": "Aarde",
                    "pl": "Ziemia",
                    "pt": "Terra",
                    "ru": "Земля",
                    "ja": "地球",
                    "zh": "地球",
                    "ko": "지구"
                }},
                {"value": "mars", "label": {
                    "en": "Mars",
                    "de": "Mars",
                    "es": "Marte",
                    "fr": "Mars",
                    "it": "Marte",
                    "nl": "Mars",
                    "pl": "Mars",
                    "pt": "Marte",
                    "ru": "Марс",
                    "ja": "火星",
                    "zh": "火星",
                    "ko": "화성"
                }},
                {"value": "jupiter", "label": {
                    "en": "Jupiter",
                    "de": "Jupiter",
                    "es": "Júpiter",
                    "fr": "Jupiter",
                    "it": "Giove",
                    "nl": "Jupiter",
                    "pl": "Jowisz",
                    "pt": "Júpiter",
                    "ru": "Юпитер",
                    "ja": "木星",
                    "zh": "木星",
                    "ko": "목성"
                }},
                {"value": "saturn", "label": {
                    "en": "Saturn",
                    "de": "Saturn",
                    "es": "Saturno",
                    "fr": "Saturne",
                    "it": "Saturno",
                    "nl": "Saturnus",
                    "pl": "Saturn",
                    "pt": "Saturno",
                    "ru": "Сатурн",
                    "ja": "土星",
                    "zh": "土星",
                    "ko": "토성"
                }},
                {"value": "uranus", "label": {
                    "en": "Uranus",
                    "de": "Uranus",
                    "es": "Urano",
                    "fr": "Uranus",
                    "it": "Urano",
                    "nl": "Uranus",
                    "pl": "Uran",
                    "pt": "Urano",
                    "ru": "Уран",
                    "ja": "天王星",
                    "zh": "天王星",
                    "ko": "천왕성"
                }},
                {"value": "neptune", "label": {
                    "en": "Neptune",
                    "de": "Neptun",
                    "es": "Neptuno",
                    "fr": "Neptune",
                    "it": "Nettuno",
                    "nl": "Neptunus",
                    "pl": "Neptun",
                    "pt": "Netuno",
                    "ru": "Нептун",
                    "ja": "海王星",
                    "zh": "海王星",
                    "ko": "해왕성"
                }},
                {"value": "pluto", "label": {
                    "en": "Pluto (Dwarf)",
                    "de": "Pluto (Zwergplanet)",
                    "es": "Plutón (Enano)",
                    "fr": "Pluton (Naine)",
                    "it": "Plutone (Nano)",
                    "nl": "Pluto (Dwerg)",
                    "pl": "Pluton (Karłowata)",
                    "pt": "Plutão (Anão)",
                    "ru": "Плутон (Карлик)",
                    "ja": "冥王星（準惑星）",
                    "zh": "冥王星（矮行星）",
                    "ko": "명왕성 (왜행성)"
                }},
                {"value": "jwst", "label": {
                    "en": "JWST (L2 Point)",
                    "de": "JWST (L2-Punkt)",
                    "es": "JWST (Punto L2)",
                    "fr": "JWST (Point L2)",
                    "it": "JWST (Punto L2)",
                    "nl": "JWST (L2-punt)",
                    "pl": "JWST (Punkt L2)",
                    "pt": "JWST (Ponto L2)",
                    "ru": "JWST (Точка L2)",
                    "ja": "JWST（L2点）",
                    "zh": "JWST（L2点）",
                    "ko": "JWST (L2 지점)"
                }}
            ]
        },
        "coordinate_system": {
            "type": "select",
            "default": "heliocentric",
            "label": {
                "en": "Coordinate System",
                "de": "Koordinatensystem",
                "es": "Sistema de Coordenadas",
                "fr": "Système de Coordonnées",
                "it": "Sistema di Coordinate",
                "nl": "Coördinatensysteem",
                "pl": "Układ Współrzędnych",
                "pt": "Sistema de Coordenadas",
                "ru": "Система координат",
                "ja": "座標系",
                "zh": "坐标系",
                "ko": "좌표계"
            },
            "description": {
                "en": "Choose heliocentric (Sun-centered) or geocentric (Earth-centered) view",
                "de": "Wählen Sie heliozentrisch (sonnenzentriert) oder geozentrisch (erdzentriert)",
                "es": "Elija vista heliocéntrica (centrada en el Sol) o geocéntrica (centrada en la Tierra)",
                "fr": "Choisissez vue héliocentrique (centrée sur le Soleil) ou géocentrique (centrée sur la Terre)",
                "it": "Scegli vista eliocentrica (centrata sul Sole) o geocentrica (centrata sulla Terra)",
                "nl": "Kies heliocentrisch (zon-gecentreerd) of geocentrisch (aarde-gecentreerd)",
                "pl": "Wybierz widok heliocentryczny (słoneczny) lub geocentryczny (ziemski)",
                "pt": "Escolha visão heliocêntrica (centrada no Sol) ou geocêntrica (centrada na Terra)",
                "ru": "Выберите гелиоцентрический (Солнце в центре) или геоцентрический (Земля в центре) вид",
                "ja": "太陽中心（太陽系）または地球中心（地心）ビューを選択",
                "zh": "选择日心（以太阳为中心）或地心（以地球为中心）视图",
                "ko": "태양 중심(태양계) 또는 지구 중심(지구계) 보기 선택"
            },
            "options": [
                {"value": "heliocentric", "label": {
                    "en": "Heliocentric (Sun-centered)",
                    "de": "Heliozentrisch (Sonnenzentriert)",
                    "es": "Heliocéntrico (Centrado en el Sol)",
                    "fr": "Héliocentrique (Centré sur le Soleil)",
                    "it": "Eliocentrico (Centrato sul Sole)",
                    "nl": "Heliocentrisch (Zon-gecentreerd)",
                    "pl": "Heliocentryczny (Słoneczny)",
                    "pt": "Heliocêntrico (Centrado no Sol)",
                    "ru": "Гелиоцентрический (Солнце в центре)",
                    "ja": "太陽中心",
                    "zh": "日心（以太阳为中心）",
                    "ko": "태양 중심"
                }},
                {"value": "geocentric", "label": {
                    "en": "Geocentric (Earth-centered)",
                    "de": "Geozentrisch (Erdzentriert)",
                    "es": "Geocéntrico (Centrado en la Tierra)",
                    "fr": "Géocentrique (Centré sur la Terre)",
                    "it": "Geocentrico (Centrato sulla Terra)",
                    "nl": "Geocentrisch (Aarde-gecentreerd)",
                    "pl": "Geocentryczny (Ziemski)",
                    "pt": "Geocêntrico (Centrado na Terra)",
                    "ru": "Геоцентрический (Земля в центре)",
                    "ja": "地球中心",
                    "zh": "地心（以地球为中心）",
                    "ko": "지구 중심"
                }}
            ]
        },
        "observer_latitude": {
            "type": "float",
            "default": 49.14,  # Default: Heilbronn, Germany
            "min": -90.0,
            "max": 90.0,
            "label": {
                "en": "Observer Latitude",
                "de": "Beobachter Breitengrad",
                "es": "Latitud del Observador",
                "fr": "Latitude de l'Observateur",
                "it": "Latitudine dell'Osservatore",
                "nl": "Waarnemersbreedte",
                "pl": "Szerokość Geograficzna Obserwatora",
                "pt": "Latitude do Observador",
                "ru": "Широта наблюдателя",
                "ja": "観測者の緯度",
                "zh": "观察者纬度",
                "ko": "관찰자 위도"
            },
            "description": {
                "en": "Your latitude for visibility calculations (-90 to 90)",
                "de": "Ihr Breitengrad für Sichtbarkeitsberechnungen (-90 bis 90)",
                "es": "Su latitud para cálculos de visibilidad (-90 a 90)",
                "fr": "Votre latitude pour les calculs de visibilité (-90 à 90)",
                "it": "La tua latitudine per i calcoli di visibilità (-90 a 90)",
                "nl": "Uw breedtegraad voor zichtbaarheidsberekeningen (-90 tot 90)",
                "pl": "Twoja szerokość geograficzna do obliczeń widoczności (-90 do 90)",
                "pt": "Sua latitude para cálculos de visibilidade (-90 a 90)",
                "ru": "Ваша широта для расчета видимости (-90 до 90)",
                "ja": "可視性計算のための緯度（-90から90）",
                "zh": "用于可见性计算的纬度（-90至90）",
                "ko": "가시성 계산을 위한 위도 (-90에서 90)"
            }
        },
        "observer_longitude": {
            "type": "float",
            "default": 9.22,  # Default: Heilbronn, Germany
            "min": -180.0,
            "max": 180.0,
            "label": {
                "en": "Observer Longitude",
                "de": "Beobachter Längengrad",
                "es": "Longitud del Observador",
                "fr": "Longitude de l'Observateur",
                "it": "Longitudine dell'Osservatore",
                "nl": "Waarnemerslengte",
                "pl": "Długość Geograficzna Obserwatora",
                "pt": "Longitude do Observador",
                "ru": "Долгота наблюдателя",
                "ja": "観測者の経度",
                "zh": "观察者经度",
                "ko": "관찰자 경도"
            },
            "description": {
                "en": "Your longitude for visibility calculations (-180 to 180)",
                "de": "Ihr Längengrad für Sichtbarkeitsberechnungen (-180 bis 180)",
                "es": "Su longitud para cálculos de visibilidad (-180 a 180)",
                "fr": "Votre longitude pour les calculs de visibilité (-180 à 180)",
                "it": "La tua longitudine per i calcoli di visibilità (-180 a 180)",
                "nl": "Uw lengtegraad voor zichtbaarheidsberekeningen (-180 tot 180)",
                "pl": "Twoja długość geograficzna do obliczeń widoczności (-180 do 180)",
                "pt": "Sua longitude para cálculos de visibilidade (-180 a 180)",
                "ru": "Ваша долгота для расчета видимости (-180 до 180)",
                "ja": "可視性計算のための経度（-180から180）",
                "zh": "用于可见性计算的经度（-180至180）",
                "ko": "가시성 계산을 위한 경도 (-180에서 180)"
            }
        },
        "show_visibility": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show Visibility Times",
                "de": "Sichtbarkeitszeiten anzeigen",
                "es": "Mostrar Tiempos de Visibilidad",
                "fr": "Afficher les Heures de Visibilité",
                "it": "Mostra Tempi di Visibilità",
                "nl": "Zichtbaarheidstijden Tonen",
                "pl": "Pokaż Czasy Widoczności",
                "pt": "Mostrar Tempos de Visibilidade",
                "ru": "Показать время видимости",
                "ja": "可視時間を表示",
                "zh": "显示可见时间",
                "ko": "가시 시간 표시"
            },
            "description": {
                "en": "Display when planets are visible from your location",
                "de": "Anzeigen wann Planeten von Ihrem Standort sichtbar sind",
                "es": "Mostrar cuándo los planetas son visibles desde su ubicación",
                "fr": "Afficher quand les planètes sont visibles depuis votre position",
                "it": "Visualizza quando i pianeti sono visibili dalla tua posizione",
                "nl": "Weergeven wanneer planeten zichtbaar zijn vanaf uw locatie",
                "pl": "Wyświetl, kiedy planety są widoczne z Twojej lokalizacji",
                "pt": "Exibir quando os planetas são visíveis da sua localização",
                "ru": "Отображать, когда планеты видны из вашего местоположения",
                "ja": "あなたの場所から惑星が見える時間を表示",
                "zh": "显示从您的位置可以看到行星的时间",
                "ko": "당신의 위치에서 행성이 보이는 시간 표시"
            }
        },
            "type": "select",
            "default": "all",
            "label": {
                "en": "Display Planet",
                "de": "Planet anzeigen",
                "es": "Mostrar Planeta",
                "fr": "Afficher Planète",
                "it": "Mostra Pianeta",
                "nl": "Planeet Weergeven",
                "pl": "Wyświetl Planetę",
                "pt": "Exibir Planeta",
                "ru": "Показать планету",
                "ja": "惑星を表示",
                "zh": "显示行星",
                "ko": "행성 표시"
            },
            "description": {
                "en": "Select which planet to display or all planets",
                "de": "Wählen Sie welchen Planeten oder alle Planeten anzeigen",
                "es": "Seleccione qué planeta mostrar o todos los planetas",
                "fr": "Sélectionnez quelle planète afficher ou toutes les planètes",
                "it": "Seleziona quale pianeta visualizzare o tutti i pianeti",
                "nl": "Selecteer welke planeet weer te geven of alle planeten",
                "pl": "Wybierz planetę do wyświetlenia lub wszystkie planety",
                "pt": "Selecione qual planeta exibir ou todos os planetas",
                "ru": "Выберите планету для отображения или все планеты",
                "ja": "表示する惑星または全惑星を選択",
                "zh": "选择要显示的行星或所有行星",
                "ko": "표시할 행성 또는 모든 행성 선택"
            },
            "options": [
                {"value": "all", "label": {
                    "en": "All Planets", 
                    "de": "Alle Planeten",
                    "es": "Todos los Planetas",
                    "fr": "Toutes les Planètes",
                    "it": "Tutti i Pianeti",
                    "nl": "Alle Planeten",
                    "pl": "Wszystkie Planety",
                    "pt": "Todos os Planetas",
                    "ru": "Все планеты",
                    "ja": "すべての惑星",
                    "zh": "所有行星",
                    "ko": "모든 행성"
                }},
                {"value": "mercury", "label": {
                    "en": "Mercury",
                    "de": "Merkur",
                    "es": "Mercurio",
                    "fr": "Mercure",
                    "it": "Mercurio",
                    "nl": "Mercurius",
                    "pl": "Merkury",
                    "pt": "Mercúrio",
                    "ru": "Меркурий",
                    "ja": "水星",
                    "zh": "水星",
                    "ko": "수성"
                }},
                {"value": "venus", "label": {
                    "en": "Venus",
                    "de": "Venus",
                    "es": "Venus",
                    "fr": "Vénus",
                    "it": "Venere",
                    "nl": "Venus",
                    "pl": "Wenus",
                    "pt": "Vênus",
                    "ru": "Венера",
                    "ja": "金星",
                    "zh": "金星",
                    "ko": "금성"
                }},
                {"value": "earth", "label": {
                    "en": "Earth",
                    "de": "Erde",
                    "es": "Tierra",
                    "fr": "Terre",
                    "it": "Terra",
                    "nl": "Aarde",
                    "pl": "Ziemia",
                    "pt": "Terra",
                    "ru": "Земля",
                    "ja": "地球",
                    "zh": "地球",
                    "ko": "지구"
                }},
                {"value": "mars", "label": {
                    "en": "Mars",
                    "de": "Mars",
                    "es": "Marte",
                    "fr": "Mars",
                    "it": "Marte",
                    "nl": "Mars",
                    "pl": "Mars",
                    "pt": "Marte",
                    "ru": "Марс",
                    "ja": "火星",
                    "zh": "火星",
                    "ko": "화성"
                }},
                {"value": "jupiter", "label": {
                    "en": "Jupiter",
                    "de": "Jupiter",
                    "es": "Júpiter",
                    "fr": "Jupiter",
                    "it": "Giove",
                    "nl": "Jupiter",
                    "pl": "Jowisz",
                    "pt": "Júpiter",
                    "ru": "Юпитер",
                    "ja": "木星",
                    "zh": "木星",
                    "ko": "목성"
                }},
                {"value": "saturn", "label": {
                    "en": "Saturn",
                    "de": "Saturn",
                    "es": "Saturno",
                    "fr": "Saturne",
                    "it": "Saturno",
                    "nl": "Saturnus",
                    "pl": "Saturn",
                    "pt": "Saturno",
                    "ru": "Сатурн",
                    "ja": "土星",
                    "zh": "土星",
                    "ko": "토성"
                }},
                {"value": "uranus", "label": {
                    "en": "Uranus",
                    "de": "Uranus",
                    "es": "Urano",
                    "fr": "Uranus",
                    "it": "Urano",
                    "nl": "Uranus",
                    "pl": "Uran",
                    "pt": "Urano",
                    "ru": "Уран",
                    "ja": "天王星",
                    "zh": "天王星",
                    "ko": "천왕성"
                }},
                {"value": "neptune", "label": {
                    "en": "Neptune",
                    "de": "Neptun",
                    "es": "Neptuno",
                    "fr": "Neptune",
                    "it": "Nettuno",
                    "nl": "Neptunus",
                    "pl": "Neptun",
                    "pt": "Netuno",
                    "ru": "Нептун",
                    "ja": "海王星",
                    "zh": "海王星",
                    "ko": "해왕성"
                }}
            ]
        },
        "coordinate_system": {
            "type": "select",
            "default": "heliocentric",
            "label": {
                "en": "Coordinate System",
                "de": "Koordinatensystem",
                "es": "Sistema de Coordenadas",
                "fr": "Système de Coordonnées",
                "it": "Sistema di Coordinate",
                "nl": "Coördinatensysteem",
                "pl": "Układ Współrzędnych",
                "pt": "Sistema de Coordenadas",
                "ru": "Система координат",
                "ja": "座標系",
                "zh": "坐标系",
                "ko": "좌표계"
            },
            "description": {
                "en": "Choose heliocentric (Sun-centered) or geocentric (Earth-centered) view",
                "de": "Wählen Sie heliozentrisch (sonnenzentriert) oder geozentrisch (erdzentriert)",
                "es": "Elija vista heliocéntrica (centrada en el Sol) o geocéntrica (centrada en la Tierra)",
                "fr": "Choisissez vue héliocentrique (centrée sur le Soleil) ou géocentrique (centrée sur la Terre)",
                "it": "Scegli vista eliocentrica (centrata sul Sole) o geocentrica (centrata sulla Terra)",
                "nl": "Kies heliocentrisch (zon-gecentreerd) of geocentrisch (aarde-gecentreerd)",
                "pl": "Wybierz widok heliocentryczny (słoneczny) lub geocentryczny (ziemski)",
                "pt": "Escolha visão heliocêntrica (centrada no Sol) ou geocêntrica (centrada na Terra)",
                "ru": "Выберите гелиоцентрический (Солнце в центре) или геоцентрический (Земля в центре) вид",
                "ja": "太陽中心（太陽系）または地球中心（地心）ビューを選択",
                "zh": "选择日心（以太阳为中心）或地心（以地球为中心）视图",
                "ko": "태양 중심(태양계) 또는 지구 중심(지구계) 보기 선택"
            },
            "options": [
                {"value": "heliocentric", "label": {
                    "en": "Heliocentric (Sun-centered)",
                    "de": "Heliozentrisch (Sonnenzentriert)",
                    "es": "Heliocéntrico (Centrado en el Sol)",
                    "fr": "Héliocentrique (Centré sur le Soleil)",
                    "it": "Eliocentrico (Centrato sul Sole)",
                    "nl": "Heliocentrisch (Zon-gecentreerd)",
                    "pl": "Heliocentryczny (Słoneczny)",
                    "pt": "Heliocêntrico (Centrado no Sol)",
                    "ru": "Гелиоцентрический (Солнце в центре)",
                    "ja": "太陽中心",
                    "zh": "日心（以太阳为中心）",
                    "ko": "태양 중심"
                }},
                {"value": "geocentric", "label": {
                    "en": "Geocentric (Earth-centered)",
                    "de": "Geozentrisch (Erdzentriert)",
                    "es": "Geocéntrico (Centrado en la Tierra)",
                    "fr": "Géocentrique (Centré sur la Terre)",
                    "it": "Geocentrico (Centrato sulla Terra)",
                    "nl": "Geocentrisch (Aarde-gecentreerd)",
                    "pl": "Geocentryczny (Ziemski)",
                    "pt": "Geocêntrico (Centrado na Terra)",
                    "ru": "Геоцентрический (Земля в центре)",
                    "ja": "地球中心",
                    "zh": "地心（以地球为中心）",
                    "ko": "지구 중심"
                }}
            ]
        },
        "show_distance": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show Distance",
                "de": "Entfernung anzeigen",
                "es": "Mostrar Distancia",
                "fr": "Afficher Distance",
                "it": "Mostra Distanza",
                "nl": "Afstand Tonen",
                "pl": "Pokaż Odległość",
                "pt": "Mostrar Distância",
                "ru": "Показать расстояние",
                "ja": "距離を表示",
                "zh": "显示距离",
                "ko": "거리 표시"
            },
            "description": {
                "en": "Display distance from Sun (or Earth in geocentric mode) in AU and km",
                "de": "Entfernung von der Sonne anzeigen (oder Erde im geozentrischen Modus) in AE und km",
                "es": "Mostrar distancia desde el Sol (o Tierra en modo geocéntrico) en UA y km",
                "fr": "Afficher la distance du Soleil (ou de la Terre en mode géocentrique) en UA et km",
                "it": "Visualizza distanza dal Sole (o Terra in modalità geocentrica) in UA e km",
                "nl": "Afstand van de zon weergeven (of aarde in geocentrische modus) in AE en km",
                "pl": "Wyświetl odległość od Słońca (lub Ziemi w trybie geocentrycznym) w j.a. i km",
                "pt": "Exibir distância do Sol (ou Terra no modo geocêntrico) em UA e km",
                "ru": "Отображать расстояние от Солнца (или Земли в геоцентрическом режиме) в а.е. и км",
                "ja": "太陽からの距離を表示（地心モードでは地球から）AUとkm",
                "zh": "显示与太阳的距离（地心模式下为地球）以AU和km为单位",
                "ko": "태양으로부터의 거리 표시 (지구 중심 모드에서는 지구) AU와 km 단위"
            }
        },
        "show_constellation": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show Constellation",
                "de": "Sternbild anzeigen",
                "es": "Mostrar Constelación",
                "fr": "Afficher Constellation",
                "it": "Mostra Costellazione",
                "nl": "Sterrenbeeld Tonen",
                "pl": "Pokaż Konstelację",
                "pt": "Mostrar Constelação",
                "ru": "Показать созвездие",
                "ja": "星座を表示",
                "zh": "显示星座",
                "ko": "별자리 표시"
            },
            "description": {
                "en": "Display zodiac constellation where planet is located",
                "de": "Tierkreissternbild anzeigen, in dem sich der Planet befindet",
                "es": "Mostrar constelación del zodíaco donde se encuentra el planeta",
                "fr": "Afficher la constellation du zodiaque où se trouve la planète",
                "it": "Visualizza costellazione zodiacale dove si trova il pianeta",
                "nl": "Dierenriem sterrenbeeld weergeven waar planeet zich bevindt",
                "pl": "Wyświetl konstelację zodiaku, w której znajduje się planeta",
                "pt": "Exibir constelação do zodíaco onde o planeta está localizado",
                "ru": "Отображать зодиакальное созвездие, где находится планета",
                "ja": "惑星が位置する黄道星座を表示",
                "zh": "显示行星所在的黄道星座",
                "ko": "행성이 위치한 황도 별자리 표시"
            }
        },
        "show_retrograde": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show Retrograde Motion",
                "de": "Rückläufige Bewegung anzeigen",
                "es": "Mostrar Movimiento Retrógrado",
                "fr": "Afficher Mouvement Rétrograde",
                "it": "Mostra Moto Retrogrado",
                "nl": "Retrograde Beweging Tonen",
                "pl": "Pokaż Ruch Wsteczny",
                "pt": "Mostrar Movimento Retrógrado",
                "ru": "Показать ретроградное движение",
                "ja": "逆行を表示",
                "zh": "显示逆行",
                "ko": "역행 표시"
            },
            "description": {
                "en": "Indicate when planets appear to move backward",
                "de": "Anzeigen wenn Planeten rückläufig erscheinen",
                "es": "Indicar cuando los planetas parecen moverse hacia atrás",
                "fr": "Indiquer quand les planètes semblent reculer",
                "it": "Indica quando i pianeti sembrano muoversi all'indietro",
                "nl": "Aangeven wanneer planeten achteruit lijken te bewegen",
                "pl": "Wskaż, gdy planety wydają się poruszać wstecz",
                "pt": "Indicar quando os planetas parecem se mover para trás",
                "ru": "Указывать, когда планеты движутся в обратном направлении",
                "ja": "惑星が逆行しているように見える時を示す",
                "zh": "指示行星看起来向后移动的时候",
                "ko": "행성이 뒤로 움직이는 것처럼 보일 때 표시"
            }
        }
    }
}


class SolarSystemSensor(AlternativeTimeSensorBase):
    """Sensor for displaying solar system planetary positions."""
    
    # Class-level update interval
    UPDATE_INTERVAL = 300  # Update every 5 minutes
    
    def __init__(self, base_name: str, hass: HomeAssistant) -> None:
        """Initialize the Solar System sensor with standard 2-parameter signature."""
        super().__init__(base_name, hass)
        
        # Get calendar info
        calendar_name = self._translate('name', 'Solar System Positions')
        self._attr_name = f"{base_name} {calendar_name}"
        self._attr_unique_id = f"solar_system_{base_name.lower().replace(' ', '_')}"
        
        # Set update interval
        self._update_interval = timedelta(seconds=UPDATE_INTERVAL)
        
        # Solar system specific data
        self._solar_data = CALENDAR_INFO.get("solar_data", {})
        self._planets = self._solar_data.get("planets", {})
        self._constellations = self._solar_data.get("constellations", [])
        
        # Initialize with defaults
        self._display_planet = "all"
        self._coordinate_system = "heliocentric"
        self._show_distance = True
        self._show_constellation = True
        self._show_retrograde = True
        self._show_visibility = True
        self._observer_latitude = 49.14  # Default: Heilbronn
        self._observer_longitude = 9.22
        
        # Planet positions data storage
        self._positions_info = {}
        self._state = "Initializing..."
        
        # Debug flag
        self._first_update = True
        
        # User language
        self._user_language = 'en'
    
    @property
    def state(self) -> str:
        """Return the state of the sensor."""
        return self._state
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes."""
        attrs = super().extra_state_attributes
        
        # Add solar system specific attributes
        if self._positions_info:
            attrs.update(self._positions_info)
            
            # Add description
            attrs["description"] = self._translate('description')
            
            # Add reference
            attrs["reference"] = CALENDAR_INFO.get('reference_url', '')
            
            # Add config info
            attrs["config"] = {
                "display_planet": self._display_planet,
                "coordinate_system": self._coordinate_system,
                "show_distance": self._show_distance,
                "show_constellation": self._show_constellation,
                "show_retrograde": self._show_retrograde
            }
        
        return attrs
    
    def _get_planet_name(self, planet_id: str) -> str:
        """Get localized planet name."""
        planet_data = self._planets.get(planet_id, {})
        names = planet_data.get("name", {})
        return names.get(self._user_language, names.get("en", planet_id.title()))
    
    def _get_constellation(self, longitude: float) -> tuple:
        """Get constellation for given ecliptic longitude."""
        # Normalize longitude to 0-360
        longitude = longitude % 360
        
        for constellation in self._constellations:
            start = constellation["start"]
            end = (start + 30) % 360
            
            if start <= longitude < end or (start > end and (longitude >= start or longitude < end)):
                names = constellation.get("name", {})
                name = names.get(self._user_language, names.get("en", "Unknown"))
                symbol = constellation.get("symbol", "")
                return (name, symbol)
        
        return ("Unknown", "")
    
    def _calculate_planet_position(self, planet_id: str, jd: float) -> Dict[str, Any]:
        """Calculate simplified planet position using Keplerian elements."""
        planet = self._planets[planet_id]
        
        # Days since J2000.0
        d = jd - 2451545.0
        
        # Mean anomaly
        n = 360.0 / planet["orbital_period"]  # Mean motion (degrees/day)
        M = (planet["mean_longitude"] + n * d) % 360
        
        # Simplified equation of center (first order approximation)
        e = planet["eccentricity"]
        C = (2 * e - e**3 / 4) * math.sin(math.radians(M)) * 180 / math.pi
        
        # True anomaly (simplified)
        v = M + C
        
        # Heliocentric longitude
        longitude = (v + planet["perihelion_longitude"]) % 360
        
        # Distance from Sun (simplified)
        a = planet["semi_major_axis"]
        r = a * (1 - e**2) / (1 + e * math.cos(math.radians(v)))
        
        return {
            "longitude": longitude,
            "distance": r,
            "mean_anomaly": M,
            "true_anomaly": v
        }
    
    def _calculate_geocentric_position(self, planet_pos: Dict, earth_pos: Dict) -> Dict[str, Any]:
        """Convert heliocentric to geocentric coordinates (simplified)."""
        # This is a simplified calculation for demonstration
        # Real calculation would need proper coordinate transformation
        
        # Relative longitude
        geo_longitude = (planet_pos["longitude"] - earth_pos["longitude"]) % 360
        
        # Approximate distance using law of cosines
        angle_diff = math.radians(planet_pos["longitude"] - earth_pos["longitude"])
        r_p = planet_pos["distance"]
        r_e = earth_pos["distance"]
        
        distance = math.sqrt(r_p**2 + r_e**2 - 2 * r_p * r_e * math.cos(angle_diff))
        
        return {
            "longitude": geo_longitude,
            "distance": distance
        }
    
    def _calculate_visibility(self, planet_id: str, dt: datetime) -> Dict[str, Any]:
        """Calculate simplified visibility times for a planet."""
        # This is a simplified calculation
        # Real calculation would need proper ephemeris data
        
        # Get planet's geocentric position
        planet_pos = self._calculate_planet_position(planet_id, self._datetime_to_jd(dt))
        earth_pos = self._calculate_planet_position("earth", self._datetime_to_jd(dt))
        geo_pos = self._calculate_geocentric_position(planet_pos, earth_pos)
        
        # Calculate elongation from Sun (angle between planet and Sun as seen from Earth)
        elongation = abs(geo_pos["longitude"] - earth_pos["longitude"])
        if elongation > 180:
            elongation = 360 - elongation
        
        # Determine visibility based on elongation
        # Inner planets (Mercury, Venus) best visible near greatest elongation
        # Outer planets best visible at opposition (elongation ~180°)
        
        visibility = {
            "elongation": elongation,
            "visible": False,
            "rise_time": None,
            "set_time": None,
            "best_time": None,
            "visibility_period": None
        }
        
        # Simple visibility rules based on elongation
        if planet_id in ["mercury", "venus"]:
            # Inner planets - morning or evening star
            if 15 < elongation < 47:  # Near maximum elongation
                visibility["visible"] = True
                if geo_pos["longitude"] < earth_pos["longitude"]:
                    # Morning star (visible before sunrise)
                    visibility["visibility_period"] = "Morning star"
                    visibility["best_time"] = "Before sunrise"
                    # Approximate times (simplified)
                    sunrise = 6.0  # 6:00 AM
                    visibility["rise_time"] = f"{int(sunrise-3):02d}:00"
                    visibility["set_time"] = f"{int(sunrise):02d}:00"
                else:
                    # Evening star (visible after sunset)
                    visibility["visibility_period"] = "Evening star"
                    visibility["best_time"] = "After sunset"
                    # Approximate times (simplified)
                    sunset = 18.0  # 6:00 PM
                    visibility["rise_time"] = f"{int(sunset):02d}:00"
                    visibility["set_time"] = f"{int(sunset+3):02d}:00"
        else:
            # Outer planets
            if elongation > 60:  # Reasonably separated from Sun
                visibility["visible"] = True
                
                # Calculate approximate rise/set times based on elongation
                # This is very simplified - real calculation needs proper algorithms
                hour_angle = elongation / 15  # Convert to hours
                
                if elongation > 150:  # Near opposition
                    visibility["visibility_period"] = "All night"
                    visibility["best_time"] = "Midnight"
                    visibility["rise_time"] = "18:00"  # Sunset
                    visibility["set_time"] = "06:00"   # Sunrise
                elif elongation > 90:
                    visibility["visibility_period"] = "Most of night"
                    visibility["best_time"] = "Late evening"
                    rise_hour = 18 + (180 - elongation) / 15
                    set_hour = 6 - (180 - elongation) / 15
                    visibility["rise_time"] = f"{int(rise_hour % 24):02d}:00"
                    visibility["set_time"] = f"{int(set_hour % 24):02d}:00"
                else:
                    visibility["visibility_period"] = "Part of night"
                    visibility["best_time"] = "Evening"
                    visibility["rise_time"] = "20:00"
                    visibility["set_time"] = "23:00"
        
        return visibility
        """Check if planet appears to be in retrograde motion."""
        # Simplified check - in reality this would need more sophisticated calculation
        if planet_id in ["mercury", "venus"]:
            # Inner planets
            diff = (current_pos - previous_pos) % 360
            return diff > 180  # Moving "backward" relative to normal motion
        elif planet_id != "earth":
            # Outer planets
            diff = (current_pos - previous_pos) % 360
            return diff > 180
        return False
    
    def _format_position(self, planet_id: str, position: Dict) -> str:
        """Format planet position for display."""
        planet_name = self._get_planet_name(planet_id)
        symbol = self._planets[planet_id].get("symbol", "")
        
        parts = [f"{symbol} {planet_name}:"]
        
        # Add longitude
        parts.append(f"{position['longitude']:.1f}°")
        
        # Add distance if configured
        if self._show_distance:
            au = position['distance']
            km = au * 149597870.7  # 1 AU = 149,597,870.7 km
            parts.append(f"{au:.3f} AU ({km/1e6:.1f} Mio km)")
        
        # Add constellation if configured
        if self._show_constellation:
            const_name, const_symbol = self._get_constellation(position['longitude'])
            parts.append(f"{const_symbol} {const_name}")
        
        # Add visibility if configured
        if self._show_visibility and "visibility" in position:
            vis = position["visibility"]
            if vis.get("visible"):
                parts.append(f"👁 {vis.get('rise_time', 'N/A')}-{vis.get('set_time', 'N/A')}")
            else:
                parts.append("🚫 Not visible")
        
        # Add retrograde indicator if applicable
        if self._show_retrograde and position.get("retrograde", False):
            parts.append("℞")
        
        return " | ".join(parts)
    
    def _calculate_positions(self, dt: datetime) -> Dict[str, Any]:
        """Calculate all planetary positions."""
        # Calculate Julian Date
        jd = self._datetime_to_jd(dt)
        
        # Astronomical Unit in kilometers
        AU_TO_KM = 149597870.7
        
        result = {
            "julian_date": jd,
            "timestamp": dt.isoformat(),
            "observer_location": {
                "latitude": self._observer_latitude,
                "longitude": self._observer_longitude
            },
            "positions": {}
        }
        
        # Calculate Earth position first (needed for geocentric)
        earth_pos = None
        if "earth" in self._planets:
            earth_pos = self._calculate_planet_position("earth", jd)
        
        # Calculate positions for selected planets
        planets_to_calc = [self._display_planet] if self._display_planet != "all" else self._planets.keys()
        
        for planet_id in planets_to_calc:
            if planet_id not in self._planets:
                continue
            
            # Skip Earth in planet list (it's the observer)
            if planet_id == "earth":
                continue
            
            # Calculate heliocentric position
            helio_pos = self._calculate_planet_position(planet_id, jd)
            
            # Convert to geocentric if needed
            if self._coordinate_system == "geocentric" and earth_pos:
                position = self._calculate_geocentric_position(helio_pos, earth_pos)
            else:
                position = helio_pos
            
            # Add constellation
            const_name, const_symbol = self._get_constellation(position['longitude'])
            position['constellation'] = const_name
            position['constellation_symbol'] = const_symbol
            
            # Add distance in both AU and km
            position['distance_au'] = position['distance']
            position['distance_km'] = position['distance'] * AU_TO_KM
            position['distance_million_km'] = position['distance_km'] / 1e6
            
            # Calculate visibility if configured
            if self._show_visibility:
                visibility = self._calculate_visibility(planet_id, dt)
                position['visibility'] = visibility
            
            # Store position
            planet_name = self._get_planet_name(planet_id)
            result["positions"][planet_name] = position
        
        return result
    
    def _datetime_to_jd(self, dt: datetime) -> float:
        """Convert datetime to Julian Date."""
        # Ensure UTC
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            dt = dt.astimezone(timezone.utc)
        
        # Algorithm from Meeus
        year = dt.year
        month = dt.month
        day = dt.day + (dt.hour + dt.minute/60 + dt.second/3600) / 24
        
        if month <= 2:
            year -= 1
            month += 12
        
        a = int(year / 100)
        b = 2 - a + int(a / 4)
        
        jd = int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + b - 1524.5
        
        return jd
    
    def update(self) -> None:
        """Update the sensor."""
        # Update user language
        if self.hass and hasattr(self.hass, 'config'):
            self._user_language = self.hass.config.language if hasattr(self.hass.config, 'language') else 'en'
        
        # Load options on every update
        options = self.get_plugin_options()
        
        # Debug on first update
        if self._first_update:
            if options:
                _LOGGER.info(f"Solar System sensor options in first update: {options}")
            else:
                _LOGGER.debug("Solar System sensor using defaults (no options configured)")
            self._first_update = False
        
        # Update configuration
        if options:
            self._display_planet = options.get("display_planet", "all")
            self._coordinate_system = options.get("coordinate_system", "heliocentric")
            self._show_distance = bool(options.get("show_distance", True))
            self._show_constellation = bool(options.get("show_constellation", True))
            self._show_retrograde = bool(options.get("show_retrograde", True))
            self._show_visibility = bool(options.get("show_visibility", True))
            
            # Update observer location
            try:
                lat = float(options.get("observer_latitude", 49.14))
                if -90 <= lat <= 90:
                    self._observer_latitude = lat
            except (ValueError, TypeError):
                pass
            
            try:
                lon = float(options.get("observer_longitude", 9.22))
                if -180 <= lon <= 180:
                    self._observer_longitude = lon
            except (ValueError, TypeError):
                pass
        
        # Calculate positions
        try:
            now = datetime.now(timezone.utc)
            self._positions_info = self._calculate_positions(now)
            
            # Format state based on selected display
            if self._display_planet == "all":
                # Show summary
                num_planets = len(self._positions_info.get("positions", {}))
                self._state = f"{num_planets} planets tracked"
            else:
                # Show specific planet
                planet_name = self._get_planet_name(self._display_planet)
                pos = self._positions_info.get("positions", {}).get(planet_name, {})
                if pos:
                    self._state = self._format_position(self._display_planet, pos)
                else:
                    self._state = f"{planet_name}: No data"
            
        except Exception as e:
            _LOGGER.error(f"Error calculating solar system positions: {e}")
            self._state = "Error"
            self._positions_info = {"error": str(e)}
        
        _LOGGER.debug(f"Updated Solar System to {self._state}")


# Required for Home Assistant to discover this calendar
__all__ = ['SolarSystemSensor', 'CALENDAR_INFO']