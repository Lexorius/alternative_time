"""Solar System Planetary Positions - Version 1.0.6

Home Assistant "Alternative Time Systems" calendar plugin.

- Kompatibel mit vorhandener config_flow.py und sensor.py (keine Änderungen dort nötig)
- Bietet CALENDAR_INFO für Auto-Discovery & Options-UI (mit vollständigen Übersetzungen)
- Sensor-Klasse: SolarSystemSensor(base_name, hass) (AlternativeTimeSensorBase-konform)
- Visualisierung:
    - solar_system_map_html  (Canvas + JS, jetzt CCW)
    - solar_system_map_svg   (reines SVG, jetzt CCW)
    - solar_system_map_svg_data_uri (Base64) + entity_picture für Lovelace
- Neu:
    - Darstellung dreht sich LINKS herum (gegen den Uhrzeigersinn, Nordblick)
    - Radial-Markierungen für den 1. jedes Monats (berechnet aus Erdbahn)
"""
from __future__ import annotations

from datetime import datetime, timezone
import math
import json
import logging
import base64
from typing import Dict, Any, Tuple, List

from homeassistant.core import HomeAssistant
from ..sensor import AlternativeTimeSensorBase

# Optional: Falls euer sensor.py eine interne Registry bereitstellt
try:
    from ..sensor import _CONFIG_ENTRIES  # type: ignore
except Exception:  # pragma: no cover
    _CONFIG_ENTRIES = {}

_LOGGER = logging.getLogger(__name__)

# ============================================
# KONSTANTEN / METADATEN
# ============================================

UPDATE_INTERVAL = 300  # Sekunden

CALENDAR_INFO: Dict[str, Any] = {
    "id": "solar_system",
    "version": "1.0.6",
    "icon": "mdi:orbit",
    "category": "space",
    "accuracy": "approximate",
    "update_interval": UPDATE_INTERVAL,

    # Vollständige mehrsprachige Namen
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
        "ko": "태양계 위치",
    },

    # Vollständige mehrsprachige Beschreibungen
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
        "ko": "태양계 행성의 현재 위치",
    },

    # Referenz
    "reference_url": "https://en.wikipedia.org/wiki/Planetary_positions",

    # Vollständige Konfig-Optionen (wie config_flow sie ausliest)
    "config_options": {
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
                "ko": "행성 표시",
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
                "ko": "표시할 행성 또는 모든 행성 선택",
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
                    "ko": "모든 행성",
                }},
                {"value": "mercury", "label": {
                    "en": "Mercury", "de": "Merkur", "es": "Mercurio", "fr": "Mercure",
                    "it": "Mercurio", "nl": "Mercurius", "pl": "Merkury", "pt": "Mercúrio",
                    "ru": "Меркурий", "ja": "水星", "zh": "水星", "ko": "수성",
                }},
                {"value": "venus", "label": {
                    "en": "Venus", "de": "Venus", "es": "Venus", "fr": "Vénus",
                    "it": "Venere", "nl": "Venus", "pl": "Wenus", "pt": "Vênus",
                    "ru": "Венера", "ja": "金星", "zh": "金星", "ko": "금성",
                }},
                {"value": "earth", "label": {
                    "en": "Earth", "de": "Erde", "es": "Tierra", "fr": "Terre",
                    "it": "Terra", "nl": "Aarde", "pl": "Ziemia", "pt": "Terra",
                    "ru": "Земля", "ja": "地球", "zh": "地球", "ko": "지구",
                }},
                {"value": "mars", "label": {
                    "en": "Mars", "de": "Mars", "es": "Marte", "fr": "Mars",
                    "it": "Marte", "nl": "Mars", "pl": "Mars", "pt": "Marte",
                    "ru": "Марс", "ja": "火星", "zh": "火星", "ko": "화성",
                }},
                {"value": "jupiter", "label": {
                    "en": "Jupiter", "de": "Jupiter", "es": "Júpiter", "fr": "Jupiter",
                    "it": "Giove", "nl": "Jupiter", "pl": "Jowisz", "pt": "Júpiter",
                    "ru": "Юпитер", "ja": "木星", "zh": "木星", "ko": "목성",
                }},
                {"value": "saturn", "label": {
                    "en": "Saturn", "de": "Saturn", "es": "Saturno", "fr": "Saturne",
                    "it": "Saturno", "nl": "Saturnus", "pl": "Saturn", "pt": "Saturno",
                    "ru": "Сатурн", "ja": "土星", "zh": "土星", "ko": "토성",
                }},
                {"value": "uranus", "label": {
                    "en": "Uranus", "de": "Uranus", "es": "Urano", "fr": "Uranus",
                    "it": "Urano", "nl": "Uranus", "pl": "Uran", "pt": "Urano",
                    "ru": "Уран", "ja": "天王星", "zh": "天王星", "ko": "천왕성",
                }},
                {"value": "neptune", "label": {
                    "en": "Neptune", "de": "Neptun", "es": "Neptuno", "fr": "Neptune",
                    "it": "Nettuno", "nl": "Neptunus", "pl": "Neptun", "pt": "Netuno",
                    "ru": "Нептун", "ja": "海王星", "zh": "海王星", "ko": "해왕성",
                }},
                {"value": "pluto", "label": {
                    "en": "Pluto (Dwarf)", "de": "Pluto (Zwergplanet)", "es": "Plutón (Enano)",
                    "fr": "Pluton (Naine)", "it": "Plutone (Nano)", "nl": "Pluto (Dwerg)",
                    "pl": "Pluton (Karłowata)", "pt": "Plutão (Anão)", "ru": "Плутон (Карлик)",
                    "ja": "冥王星（準惑星）", "zh": "冥王星（矮行星）", "ko": "명왕성 (왜행성)",
                }},
                {"value": "jwst", "label": {
                    "en": "JWST (L2 Point)", "de": "JWST (L2-Punkt)", "es": "JWST (Punto L2)",
                    "fr": "JWST (Point L2)", "it": "JWST (Punto L2)", "nl": "JWST (L2-punt)",
                    "pl": "JWST (Punkt L2)", "pt": "JWST (Ponto L2)", "ru": "JWST (Точка L2)",
                    "ja": "JWST（L2点）", "zh": "JWST（L2点）", "ko": "JWST (L2 지점)",
                }},
            ],
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
                "ko": "좌표계",
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
                "ko": "태양 중심(태양계) 또는 지구 중심(지구계) 보기 선택",
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
                    "ko": "태양 중심",
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
                    "ko": "지구 중심",
                }},
            ],
        },

        "observer_latitude": {
            "type": "number",
            "default": 0.0,
            "min": -90.0,
            "max": 90.0,
            "step": 0.01,
            "label": {
                "en": "Observer Latitude (uses HA location if empty)",
                "de": "Beobachter Breitengrad (nutzt HA-Position wenn leer)",
                "es": "Latitud del Observador (usa ubicación HA si está vacío)",
                "fr": "Latitude de l'Observateur (utilise position HA si vide)",
                "it": "Latitudine dell'Osservatore (usa posizione HA se vuoto)",
                "nl": "Waarnemersbreedte (gebruikt HA-locatie indien leeg)",
                "pl": "Szerokość Geograficzna (używa lokalizacji HA jeśli puste)",
                "pt": "Latitude do Observador (usa localização HA se vazio)",
                "ru": "Широта наблюдателя (использует местоположение HA если пусто)",
                "ja": "観測者の緯度（空の場合はHA位置を使用）",
                "zh": "观察者纬度（如果为空则使用HA位置）",
                "ko": "관찰자 위도 (비어있으면 HA 위치 사용)",
            },
            "description": {
                "en": "Your latitude (-90 to 90). Leave at 0 to use Home Assistant location",
                "de": "Ihr Breitengrad (-90 bis 90). Bei 0 wird die Home Assistant Position verwendet",
                "es": "Su latitud (-90 a 90). Deje en 0 para usar la ubicación de Home Assistant",
                "fr": "Votre latitude (-90 à 90). Laissez à 0 pour utiliser la position Home Assistant",
                "it": "La tua latitudine (-90 a 90). Lascia a 0 per usare la posizione di Home Assistant",
                "nl": "Uw breedtegraad (-90 tot 90). Laat op 0 om Home Assistant locatie te gebruiken",
                "pl": "Twoja szerokość (-90 do 90). Zostaw 0 aby użyć lokalizacji Home Assistant",
                "pt": "Sua latitude (-90 a 90). Deixe em 0 para usar a localização do Home Assistant",
                "ru": "Ваша широта (-90 до 90). Оставьте 0 для использования местоположения Home Assistant",
                "ja": "緯度（-90から90）。0のままにするとHome Assistantの位置を使用",
                "zh": "纬度（-90至90）。保留0以使用Home Assistant位置",
                "ko": "위도 (-90에서 90). 0으로 두면 Home Assistant 위치 사용",
            },
        },

        "observer_longitude": {
            "type": "number",
            "default": 0.0,
            "min": -180.0,
            "max": 180.0,
            "step": 0.01,
            "label": {
                "en": "Observer Longitude (uses HA location if empty)",
                "de": "Beobachter Längengrad (nutzt HA-Position wenn leer)",
                "es": "Longitud del Observador (usa ubicación HA si está vacío)",
                "fr": "Longitude de l'Observateur (utilise position HA si vide)",
                "it": "Longitudine dell'Osservatore (usa posizione HA se vuoto)",
                "nl": "Waarnemerslengte (gebruikt HA-locatie indien leeg)",
                "pl": "Długość Geograficzna (używa lokalizacji HA jeśli puste)",
                "pt": "Longitude do Observador (usa localização HA se vazio)",
                "ru": "Долгота наблюдателя (использует местоположение HA если пусто)",
                "ja": "観測者の経度（空の場合はHA位置を使用）",
                "zh": "观察者经度（如果为空则使用HA位置）",
                "ko": "관찰자 경도 (비어있으면 HA 위치 사용)",
            },
            "description": {
                "en": "Your longitude (-180 to 180). Leave at 0 to use Home Assistant location",
                "de": "Ihr Längengrad (-180 bis 180). Bei 0 wird die Home Assistant Position verwendet",
                "es": "Su longitud (-180 a 180). Deje en 0 para usar la ubicación de Home Assistant",
                "fr": "Votre longitude (-180 à 180). Laissez à 0 pour utiliser la position Home Assistant",
                "it": "La tua longitudine (-180 a 180). Lascia a 0 per usare la posizione di Home Assistant",
                "nl": "Uw lengtegraad (-180 tot 180). Laat op 0 om Home Assistant locatie te gebruiken",
                "pl": "Twoja długość (-180 do 180). Zostaw 0 aby użyć lokalizacji Home Assistant",
                "pt": "Sua longitude (-180 a 180). Deixe em 0 para usar a localização do Home Assistant",
                "ru": "Ваша долгота (-180 до 180). Оставьте 0 для использования местоположения Home Assistant",
                "ja": "経度（-180から180）。0のままにするとHome Assistantの位置を使用",
                "zh": "经度（-180至180）。保留0以使用Home Assistant位置",
                "ko": "경도 (-180에서 180). 0으로 두면 Home Assistant 위치 사용",
            },
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
                "ko": "가시 시간 표시",
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
                "ko": "당신의 위치에서 행성이 보이는 시간 표시",
            },
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
                "ko": "거리 표시",
            },
            "description": {
                "en": "Display distance from Sun (or Earth in geocentric mode) in AU and km",
                "de": "Entfernung von der Sonne anzeigen (oder Erde im geozentrischen Modus) in AE und km",
                "es": "Mostrar distancia desde el Sol (o Tierra en modo geocéntrico) en UA y km",
                "fr": "Afficher la distance du Soleil (ou de la Terre en mode géocentrique) en UA et km",
                "it": "Visualizza distanza dal Sole (o Terra in modalità geocentrica) in UA e km",
                "nl": "Afstand van de zon wiedergeven (of aarde in geocentrische modus) in AE en km",
                "pl": "Wyświetl odległość od Słońca (lub Ziemi w trybie geocentrycznym) w j.a. i km",
                "pt": "Exibir distância do Sol (ou Terra no modo geocêntrico) em UA e km",
                "ru": "Отображать расстояние от Солнца (или Земли в геоцентрическом режиме) в а.е. и км",
                "ja": "太陽からの距離を表示（地心モードでは地球から）AUとkm",
                "zh": "显示与太阳的距离（地心模式下为地球）以AU和km为单位",
                "ko": "태양으로부터의 거리 표시 (지구 중심 모드에서는 지구) AU와 km 단위",
            },
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
                "ko": "별자리 표시",
            },
            "description": {
                "en": "Display zodiac constellation where planet is located",
                "de": "Tierkreissternbild anzeigen, in dem sich der Planet befindet",
                "es": "Mostrar constelación del zodíaco donde se encuentra el planeta",
                "fr": "Afficher la constellation du zodiaque où se trouve la planète",
                "it": "Visualizza costellazione zodiacale dove si trova il pianeta",
                "nl": "Dierenriem sterrenbeeld wiedergeven waar planeet zich bevindt",
                "pl": "Wyświetl konstelację zodiaku, w której znajduje się planeta",
                "pt": "Exibir constelação do zodíaco onde o planeta está localizado",
                "ru": "Отображать зодиакальное созвездие, где находится планета",
                "ja": "惑星が位置する黄道星座を表示",
                "zh": "显示行星所在的黄道星座",
                "ko": "행성이 위치한 황도 별자리 표시",
            },
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
                "ko": "역행 표시",
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
                "ko": "행성이 뒤로 움직이는 것처럼 보일 때 표시",
            },
        },

        "enable_visualization": {
            "type": "boolean",
            "default": False,
            "label": {
                "en": "Enable Solar System Map",
                "de": "Sonnensystem-Karte aktivieren",
                "es": "Activar Mapa del Sistema Solar",
                "fr": "Activer la Carte du Système Solaire",
                "it": "Attiva Mappa del Sistema Solare",
                "nl": "Zonnestelselkaart Activeren",
                "pl": "Włącz Mapę Układu Słonecznego",
                "pt": "Ativar Mapa do Sistema Solar",
                "ru": "Включить карту Солнечной системы",
                "ja": "太陽系マップを有効化",
                "zh": "启用太阳系地图",
                "ko": "태양계 지도 활성화",
            },
            "description": {
                "en": "Generate interactive visualization of planet positions",
                "de": "Interaktive Visualisierung der Planetenpositionen generieren",
                "es": "Generar visualización interactiva de posiciones planetarias",
                "fr": "Générer une visualisation interactive des positions planétaires",
                "it": "Genera visualizzazione interattiva delle posizioni planetarie",
                "nl": "Genereer interactieve visualisatie van planeetposities",
                "pl": "Generuj interaktywną wizualizację pozycji planet",
                "pt": "Gerar visualização interativa das posições planetárias",
                "ru": "Создать интерактивную визуализацию положений планет",
                "ja": "惑星位置のインタラクティブな視覚化を生成",
                "zh": "生成行星位置的交互式可视化",
                "ko": "행성 위치의 대화형 시각화 생성",
            },
        },

        "visualization_scale": {
            "type": "select",
            "default": "logarithmic",
            "label": {
                "en": "Map Scale",
                "de": "Kartenskalierung",
                "es": "Escala del Mapa",
                "fr": "Échelle de la Carte",
                "it": "Scala della Mappa",
                "nl": "Kaartschaal",
                "pl": "Skala Mapy",
                "pt": "Escala do Mapa",
                "ru": "Масштаб карты",
                "ja": "地図の縮尺",
                "zh": "地图比例",
                "ko": "지도 축척",
            },
            "description": {
                "en": "Choose scale for orbit visualization",
                "de": "Skalierung für Umlaufbahn-Visualisierung wählen",
                "es": "Elegir escala para visualización de órbitas",
                "fr": "Choisir l'échelle pour la visualisation des orbites",
                "it": "Scegli scala per visualizzazione orbite",
                "nl": "Kies schaal voor baanvisualisatie",
                "pl": "Wybierz skalę dla wizualizacji orbit",
                "pt": "Escolher escala para visualização de órbitas",
                "ru": "Выберите масштаб для визуализации орбит",
                "ja": "軌道視覚化のスケールを選択",
                "zh": "选择轨道可视化的比例",
                "ko": "궤도 시각화를 위한 축척 선택",
            },
            "options": [
                {"value": "logarithmic", "label": {
                    "en": "Logarithmic (All planets visible)",
                    "de": "Logarithmisch (Alle Planeten sichtbar)",
                    "es": "Logarítmica (Todos los planetas visibles)",
                    "fr": "Logarithmique (Toutes les planètes visibles)",
                    "it": "Logaritmica (Tutti i pianeti visibili)",
                    "nl": "Logaritmisch (Alle planeten zichtbaar)",
                    "pl": "Logarytmiczna (Wszystkie planety widoczne)",
                    "pt": "Logarítmica (Todos os planetas visíveis)",
                    "ru": "Логарифмическая (Все планеты видны)",
                    "ja": "対数（すべての惑星が見える）",
                    "zh": "对数（所有行星可见）",
                    "ko": "로그 (모든 행성 표시)",
                }},
                {"value": "linear", "label": {
                    "en": "Linear (True scale)",
                    "de": "Linear (Wahrer Maßstab)",
                    "es": "Lineal (Escala real)",
                    "fr": "Linéaire (Échelle réelle)",
                    "it": "Lineare (Scala reale)",
                    "nl": "Lineair (Ware schaal)",
                    "pl": "Liniowa (Prawdziwa skala)",
                    "pt": "Linear (Escala real)",
                    "ru": "Линейная (Истинный масштаб)",
                    "ja": "線形（実際のスケール）",
                    "zh": "线性（真实比例）",
                    "ko": "선형 (실제 축척)",
                }},
                {"value": "compressed", "label": {
                    "en": "Compressed (Inner system focus)",
                    "de": "Komprimiert (Fokus inneres System)",
                    "es": "Comprimida (Enfoque sistema interior)",
                    "fr": "Compressée (Focus système intérieur)",
                    "it": "Compressa (Focus sistema interno)",
                    "nl": "Gecomprimeerd (Focus binnenste systeem)",
                    "pl": "Skompresowana (Fokus na układ wewnętrzny)",
                    "pt": "Comprimida (Foco sistema interior)",
                    "ru": "Сжатая (Фокус на внутренней системе)",
                    "ja": "圧縮（内側システムフォーカス）",
                    "zh": "压缩（内部系统焦点）",
                    "ko": "압축 (내부 시스템 중심)",
                }},
            ],
        },
    },

    # Sonnen-/Planeten-/Sternbilddaten (mit Übersetzungen)
    "solar_data": {
        # 12 Tierkreissternbilder à 30°
        "constellations": [
            {"name": {"en": "Aries", "de": "Widder", "es": "Aries", "fr": "Bélier",
                      "it": "Ariete", "nl": "Ram", "pl": "Baran", "pt": "Áries",
                      "ru": "Овен", "ja": "牡羊座", "zh": "白羊座", "ko": "양자리"}, "start": 0, "symbol": "♈"},
            {"name": {"en": "Taurus", "de": "Stier", "es": "Tauro", "fr": "Taureau",
                      "it": "Toro", "nl": "Stier", "pl": "Byk", "pt": "Touro",
                      "ru": "Телец", "ja": "牡牛座", "zh": "金牛座", "ko": "황소자리"}, "start": 30, "symbol": "♉"},
            {"name": {"en": "Gemini", "de": "Zwillinge", "es": "Géminis", "fr": "Gémeaux",
                      "it": "Gemelli", "nl": "Tweelingen", "pl": "Bliźnięta", "pt": "Gêmeos",
                      "ru": "Близнецы", "ja": "双子座", "zh": "双子座", "ko": "쌍둥이자리"}, "start": 60, "symbol": "♊"},
            {"name": {"en": "Cancer", "de": "Krebs", "es": "Cáncer", "fr": "Cancer",
                      "it": "Cancro", "nl": "Kreeft", "pl": "Rak", "pt": "Câncer",
                      "ru": "Рак", "ja": "蟹座", "zh": "巨蟹座", "ko": "게자리"}, "start": 90, "symbol": "♋"},
            {"name": {"en": "Leo", "de": "Löwe", "es": "Leo", "fr": "Lion",
                      "it": "Leone", "nl": "Leeuw", "pl": "Lew", "pt": "Leão",
                      "ru": "Лев", "ja": "獅子座", "zh": "狮子座", "ko": "사자자리"}, "start": 120, "symbol": "♌"},
            {"name": {"en": "Virgo", "de": "Jungfrau", "es": "Virgo", "fr": "Vierge",
                      "it": "Vergine", "nl": "Maagd", "pl": "Panna", "pt": "Virgem",
                      "ru": "Дева", "ja": "乙女座", "zh": "处女座", "ko": "처녀자리"}, "start": 150, "symbol": "♍"},
            {"name": {"en": "Libra", "de": "Waage", "es": "Libra", "fr": "Balance",
                      "it": "Bilancia", "nl": "Weegschaal", "pl": "Waga", "pt": "Libra",
                      "ru": "Весы", "ja": "天秤座", "zh": "天秤座", "ko": "천칭자리"}, "start": 180, "symbol": "♎"},
            {"name": {"en": "Scorpio", "de": "Skorpion", "es": "Escorpio", "fr": "Scorpion",
                      "it": "Scorpione", "nl": "Schorpioen", "pl": "Skorpion", "pt": "Escorpião",
                      "ru": "Скорпион", "ja": "蠍座", "zh": "天蝎座", "ko": "전갈자리"}, "start": 210, "symbol": "♏"},
            {"name": {"en": "Sagittarius", "de": "Schütze", "es": "Sagitario", "fr": "Sagittaire",
                      "it": "Sagittario", "nl": "Boogschutter", "pl": "Strzelec", "pt": "Sagitário",
                      "ru": "Стрелец", "ja": "射手座", "zh": "射手座", "ko": "궁수자리"}, "start": 240, "symbol": "♐"},
            {"name": {"en": "Capricorn", "de": "Steinbock", "es": "Capricornio", "fr": "Capricorne",
                      "it": "Capricorno", "nl": "Steenbok", "pl": "Koziorożec", "pt": "Capricórnio",
                      "ru": "Козерог", "ja": "山羊座", "zh": "摩羯座", "ko": "염소자리"}, "start": 270, "symbol": "♑"},
            {"name": {"en": "Aquarius", "de": "Wassermann", "es": "Acuario", "fr": "Verseau",
                      "it": "Acquario", "nl": "Waterman", "pl": "Wodnik", "pt": "Aquário",
                      "ru": "Водолей", "ja": "水瓶座", "zh": "水瓶座", "ko": "물병자리"}, "start": 300, "symbol": "♒"},
            {"name": {"en": "Pisces", "de": "Fische", "es": "Piscis", "fr": "Poissons",
                      "it": "Pesci", "nl": "Vissen", "pl": "Ryby", "pt": "Peixes",
                      "ru": "Рыбы", "ja": "魚座", "zh": "双鱼座", "ko": "물고기자리"}, "start": 330, "symbol": "♓"},
        ],

        # Planeten (J2000; vereinfachte Elemente) + vollsprachige Namen
        "planets": {
            "mercury": {
                "name": {"en": "Mercury", "de": "Merkur", "es": "Mercurio", "fr": "Mercure",
                         "it": "Mercurio", "nl": "Mercurius", "pl": "Merkury", "pt": "Mercúrio",
                         "ru": "Меркурий", "ja": "水星", "zh": "水星", "ko": "수성"},
                "symbol": "☿",
                "semi_major_axis": 0.387098,
                "eccentricity": 0.205635,
                "inclination": 7.005,
                "mean_longitude": 252.250,
                "perihelion_longitude": 77.456,
                "orbital_period": 87.969,
            },
            "venus": {
                "name": {"en": "Venus", "de": "Venus", "es": "Venus", "fr": "Vénus",
                         "it": "Venere", "nl": "Venus", "pl": "Wenus", "pt": "Vênus",
                         "ru": "Венера", "ja": "金星", "zh": "金星", "ko": "금성"},
                "symbol": "♀",
                "semi_major_axis": 0.723332,
                "eccentricity": 0.006772,
                "inclination": 3.395,
                "mean_longitude": 181.979,
                "perihelion_longitude": 131.564,
                "orbital_period": 224.701,
            },
            "earth": {
                "name": {"en": "Earth", "de": "Erde", "es": "Tierra", "fr": "Terre",
                         "it": "Terra", "nl": "Aarde", "pl": "Ziemia", "pt": "Terra",
                         "ru": "Земля", "ja": "地球", "zh": "地球", "ko": "지구"},
                "symbol": "⊕",
                "semi_major_axis": 1.0,
                "eccentricity": 0.016709,
                "inclination": 0.0,
                "mean_longitude": 100.464,
                "perihelion_longitude": 102.937,
                "orbital_period": 365.256,
            },
            "mars": {
                "name": {"en": "Mars", "de": "Mars", "es": "Marte", "fr": "Mars",
                         "it": "Marte", "nl": "Mars", "pl": "Mars", "pt": "Marte",
                         "ru": "Марс", "ja": "火星", "zh": "火星", "ko": "화성"},
                "symbol": "♂",
                "semi_major_axis": 1.523679,
                "eccentricity": 0.0934,
                "inclination": 1.85,
                "mean_longitude": 355.433,
                "perihelion_longitude": 336.060,
                "orbital_period": 686.980,
            },
            "jupiter": {
                "name": {"en": "Jupiter", "de": "Jupiter", "es": "Júpiter", "fr": "Jupiter",
                         "it": "Giove", "nl": "Jupiter", "pl": "Jowisz", "pt": "Júpiter",
                         "ru": "Юпитер", "ja": "木星", "zh": "木星", "ko": "목성"},
                "symbol": "♃",
                "semi_major_axis": 5.202887,
                "eccentricity": 0.048498,
                "inclination": 1.303,
                "mean_longitude": 34.351,
                "perihelion_longitude": 14.331,
                "orbital_period": 4332.589,
            },
            "saturn": {
                "name": {"en": "Saturn", "de": "Saturn", "es": "Saturno", "fr": "Saturne",
                         "it": "Saturno", "nl": "Saturnus", "pl": "Saturn", "pt": "Saturno",
                         "ru": "Сатурн", "ja": "土星", "zh": "土星", "ko": "토성"},
                "symbol": "♄",
                "semi_major_axis": 9.536676,
                "eccentricity": 0.053862,
                "inclination": 2.485,
                "mean_longitude": 50.077,
                "perihelion_longitude": 93.057,
                "orbital_period": 10759.22,
            },
            "uranus": {
                "name": {"en": "Uranus", "de": "Uranus", "es": "Urano", "fr": "Uranus",
                         "it": "Urano", "nl": "Uranus", "pl": "Uran", "pt": "Urano",
                         "ru": "Уран", "ja": "天王星", "zh": "天王星", "ko": "천왕성"},
                "symbol": "♅",
                "semi_major_axis": 19.189165,
                "eccentricity": 0.047257,
                "inclination": 0.772,
                "mean_longitude": 314.055,
                "perihelion_longitude": 173.005,
                "orbital_period": 30688.5,
            },
            "neptune": {
                "name": {"en": "Neptune", "de": "Neptun", "es": "Neptuno", "fr": "Neptune",
                         "it": "Nettuno", "nl": "Neptunus", "pl": "Neptun", "pt": "Netuno",
                         "ru": "Нептун", "ja": "海王星", "zh": "海王星", "ko": "해왕성"},
                "symbol": "♆",
                "semi_major_axis": 30.069923,
                "eccentricity": 0.008859,
                "inclination": 1.769,
                "mean_longitude": 304.880,
                "perihelion_longitude": 48.123,
                "orbital_period": 60182.0,
            },
            "pluto": {
                "name": {"en": "Pluto (Dwarf Planet)", "de": "Pluto (Zwergplanet)", "es": "Plutón (Planeta Enano)",
                         "fr": "Pluton (Planète Naine)", "it": "Plutone (Pianeta Nano)", "nl": "Pluto (Dwergplaneet)",
                         "pl": "Pluton (Planeta Karłowata)", "pt": "Plutão (Planeta Anão)", "ru": "Плутон (Карликовая планета)",
                         "ja": "冥王星（準惑星）", "zh": "冥王星（矮行星）", "ko": "명왕성 (왜행성)"},
                "symbol": "♇",
                "semi_major_axis": 39.482117,
                "eccentricity": 0.2488,
                "inclination": 17.16,
                "mean_longitude": 238.929,
                "perihelion_longitude": 224.067,
                "orbital_period": 90560.0,
            },
            "jwst": {
                "name": {"en": "James Webb Space Telescope", "de": "James-Webb-Weltraumteleskop",
                         "es": "Telescopio Espacial James Webb", "fr": "Télescope Spatial James Webb",
                         "it": "Telescopio Spaziale James Webb", "nl": "James Webb Ruimtetelescoop",
                         "pl": "Kosmiczny Teleskop Jamesa Webba", "pt": "Telescópio Espacial James Webb",
                         "ru": "Космический телескоп Джеймса Уэбба", "ja": "ジェイムズ・ウェッブ宇宙望遠鏡",
                         "zh": "詹姆斯·韦伯太空望远镜", "ko": "제임스 웹 우주 망원경"},
                "symbol": "🔭",
                "semi_major_axis": 1.01,
                "eccentricity": 0.0,
                "inclination": 0.0,
                "mean_longitude": 0.0,
                "perihelion_longitude": 0.0,
                "orbital_period": 365.256,
                "special_type": "space_telescope",
                "location": "L2",
                "distance_from_earth_km": 1_500_000,
            },
        },
    },
}

# ============================================
# SENSOR
# ============================================

class SolarSystemSensor(AlternativeTimeSensorBase):
    """Sensor for displaying solar system planetary positions (CCW + monthly markers)."""

    UPDATE_INTERVAL = UPDATE_INTERVAL  # class-level

    def __init__(self, base_name: str, hass: HomeAssistant) -> None:
        super().__init__(base_name, hass)
        self._hass = hass

        try:
            calendar_name = self._translate("name", "Solar System Positions")
        except Exception:
            calendar_name = "Solar System Positions"

        self._attr_name = f"{base_name} {calendar_name}"
        self._attr_unique_id = f"solar_system_{base_name.lower().replace(' ', '_')}"

        self._solar_data = CALENDAR_INFO.get("solar_data", {})
        self._planets = self._solar_data.get("planets", {})
        self._constellations = self._solar_data.get("constellations", [])

        self._display_planet = "all"
        self._coordinate_system = "heliocentric"
        self._observer_latitude = float(getattr(getattr(hass, "config", None), "latitude", 0.0) or 0.0)
        self._observer_longitude = float(getattr(getattr(hass, "config", None), "longitude", 0.0) or 0.0)
        self._show_visibility = True
        self._show_distance = True
        self._show_constellation = True
        self._show_retrograde = True
        self._enable_visualization = False
        self._visualization_scale = "logarithmic"

        self._positions_info: Dict[str, Any] = {}
        self._state = "Initializing..."

    # ----- HA properties -----
    @property
    def state(self) -> str:
        return self._state

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        attrs = super().extra_state_attributes
        if self._positions_info:
            attrs.update(self._positions_info)
            try:
                attrs["description"] = self._translate("description", "")
            except Exception:
                attrs["description"] = CALENDAR_INFO["description"].get("en", "")
            attrs["reference"] = CALENDAR_INFO.get("reference_url", "")
            attrs["config"] = {
                "display_planet": self._display_planet,
                "coordinate_system": self._coordinate_system,
                "show_distance": self._show_distance,
                "show_constellation": self._show_constellation,
                "show_retrograde": self._show_retrograde,
                "show_visibility": self._show_visibility,
                "enable_visualization": self._enable_visualization,
                "visualization_scale": self._visualization_scale,
            }
            if self._enable_visualization:
                # SVG
                svg = self._generate_visualization_svg()
                attrs["solar_system_map_svg"] = svg
                data_uri = "data:image/svg+xml;base64," + base64.b64encode(svg.encode("utf-8")).decode("ascii")
                attrs["solar_system_map_svg_data_uri"] = data_uri
                attrs["entity_picture"] = data_uri  # für picture-entity

                # HTML (Canvas)
                attrs["solar_system_map_html"] = self._generate_visualization_html()
        return attrs

    # ----- Core calculations -----
    def _datetime_to_jd(self, dt: datetime) -> float:
        """Convert datetime to Julian Date (Meeus)."""
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            dt = dt.astimezone(timezone.utc)
        year = dt.year
        month = dt.month
        day = dt.day + (dt.hour + dt.minute/60 + dt.second/3600)/24
        if month <= 2:
            year -= 1
            month += 12
        a = int(year / 100)
        b = 2 - a + int(a / 4)
        jd = int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + b - 1524.5
        return float(jd)

    def _get_constellation(self, longitude: float) -> Tuple[str, str]:
        """Map ecliptic longitude to a 30° zodiac segment."""
        lon = longitude % 360.0
        lang = getattr(getattr(self._hass, "config", None), "language", "en") or "en"
        for c in self._constellations:
            start = float(c.get("start", 0))
            end = (start + 30.0) % 360.0
            if start <= lon < end or (start > end and (lon >= start or lon < end)):
                names = c.get("name", {})
                name = names.get(lang) or names.get("en", "Unknown")
                return name, str(c.get("symbol", ""))
        return "Unknown", ""

    def _calc_planet(self, pid: str, jd: float) -> Dict[str, Any]:
        """Very simplified heliocentric position from mean longitude & eccentricity."""
        p = self._planets[pid]

        # JWST (L2)
        if p.get("special_type") == "space_telescope":
            earth = self._calc_planet("earth", jd) if "earth" in self._planets else {"longitude": 0.0, "distance": 1.0}
            return {
                "longitude": (earth["longitude"] + 180.0) % 360.0,
                "distance": 1.01,
                "mean_anomaly": 0.0,
                "true_anomaly": 0.0,
                "location": "L2 Lagrange Point",
                "distance_from_earth_km": p.get("distance_from_earth_km", 1_500_000),
            }

        d = jd - 2451545.0
        n = 360.0 / float(p["orbital_period"])  # deg/day
        M = (p["mean_longitude"] + n * d) % 360.0
        e = float(p["eccentricity"])

        # 1. Ordnung der Gleichung des Zentrums (grobe Näherung)
        C = (2 * e - e**3 / 4.0) * math.sin(math.radians(M)) * (180.0 / math.pi)
        v = (M + C) % 360.0
        L = (v + p["perihelion_longitude"]) % 360.0

        a = float(p["semi_major_axis"])
        r = a * (1 - e**2) / (1 + e * math.cos(math.radians(v)))

        return {"longitude": L, "distance": r, "mean_anomaly": M, "true_anomaly": v}

    def _to_geocentric(self, planet_pos: Dict[str, float], earth_pos: Dict[str, float]) -> Dict[str, float]:
        """Simplified geocentric conversion in the ecliptic plane (vector difference)."""
        lam_p = math.radians(planet_pos["longitude"])
        lam_e = math.radians(earth_pos["longitude"])
        r_p = planet_pos["distance"]
        r_e = earth_pos["distance"]
        x = r_p * math.cos(lam_p) - r_e * math.cos(lam_e)
        y = r_p * math.sin(lam_p) - r_e * math.sin(lam_e)
        lam_geo = (math.degrees(math.atan2(y, x)) + 360.0) % 360.0
        dist = math.hypot(x, y)
        return {"longitude": lam_geo, "distance": dist}

    def _approx_visibility(self, pid: str, geo_long: float, earth_long: float) -> Dict[str, Any]:
        """Very coarse visibility window based on elongation only."""
        elong = abs((geo_long - earth_long + 540.0) % 360.0 - 180.0)  # 0..180
        vis = {"elongation": elong, "visible": False, "rise_time": None, "set_time": None, "best_time": None, "visibility_period": None}

        if pid in ("mercury", "venus"):
            if 15.0 < elong < 47.0:
                vis["visible"] = True
                evening = ((geo_long - earth_long) % 360.0) > 180.0
                if evening:
                    vis.update({"visibility_period": "Evening", "best_time": "After sunset", "rise_time": "18:00", "set_time": "21:00"})
                else:
                    vis.update({"visibility_period": "Morning", "best_time": "Before sunrise", "rise_time": "03:00", "set_time": "06:00"})
        else:
            if elong > 60.0:
                vis["visible"] = True
                if elong > 150.0:
                    vis.update({"visibility_period": "All night", "best_time": "Midnight", "rise_time": "18:00", "set_time": "06:00"})
                elif elong > 90.0:
                    vis.update({"visibility_period": "Most of night", "best_time": "Late evening", "rise_time": "20:00", "set_time": "04:00"})
                else:
                    vis.update({"visibility_period": "Evening", "best_time": "Evening", "rise_time": "20:00", "set_time": "23:00"})
        return vis

    # ----- Monats-Markierungen -----
    def _month_names(self, lang: str) -> List[str]:
        names = {
            "de": ["1. Jan", "1. Feb", "1. Mär", "1. Apr", "1. Mai", "1. Jun",
                   "1. Jul", "1. Aug", "1. Sep", "1. Okt", "1. Nov", "1. Dez"],
            "en": ["1 Jan", "1 Feb", "1 Mar", "1 Apr", "1 May", "1 Jun",
                   "1 Jul", "1 Aug", "1 Sep", "1 Oct", "1 Nov", "1 Dec"],
            "fr": ["1 janv.", "1 févr.", "1 mars", "1 avr.", "1 mai", "1 juin",
                   "1 juil.", "1 août", "1 sept.", "1 oct.", "1 nov.", "1 déc."],
            "es": ["1 ene", "1 feb", "1 mar", "1 abr", "1 may", "1 jun",
                   "1 jul", "1 ago", "1 sep", "1 oct", "1 nov", "1 dic"],
            "it": ["1 gen", "1 feb", "1 mar", "1 apr", "1 mag", "1 giu",
                   "1 lug", "1 ago", "1 set", "1 ott", "1 nov", "1 dic"],
            "nl": ["1 jan", "1 feb", "1 mrt", "1 apr", "1 mei", "1 jun",
                   "1 jul", "1 aug", "1 sep", "1 okt", "1 nov", "1 dec"],
            "pl": ["1 sty", "1 lut", "1 mar", "1 kwi", "1 maj", "1 cze",
                   "1 lip", "1 sie", "1 wrz", "1 paź", "1 lis", "1 gru"],
            "pt": ["1 jan", "1 fev", "1 mar", "1 abr", "1 mai", "1 jun",
                   "1 jul", "1 ago", "1 set", "1 out", "1 nov", "1 dez"],
            "ru": ["1 янв", "1 фев", "1 мар", "1 апр", "1 май", "1 июн",
                   "1 июл", "1 авг", "1 сен", "1 окт", "1 ноя", "1 дек"],
            "ja": ["1月1日", "2月1日", "3月1日", "4月1日", "5月1日", "6月1日",
                   "7月1日", "8月1日", "9月1日", "10月1日", "11月1日", "12月1日"],
            "zh": ["1月1日", "2月1日", "3月1日", "4月1日", "5月1日", "6月1日",
                   "7月1日", "8月1日", "9月1日", "10月1日", "11月1日", "12月1日"],
            "ko": ["1월1일", "2월1일", "3월1일", "4월1일", "5월1일", "6월1일",
                   "7월1일", "8월1일", "9월1일", "10월1일", "11월1일", "12월1일"],
        }
        return names.get(lang) or names["en"]

    def _monthly_markers(self, year: int) -> List[Dict[str, Any]]:
        """Berechne Erd-Helio-Längengrade am 1. jedes Monats (Helio-Referenzen)."""
        lang = getattr(getattr(self._hass, "config", None), "language", "en") or "en"
        labels = self._month_names(lang)
        marks: List[Dict[str, Any]] = []
        for m in range(1, 13):
            dt = datetime(year, m, 1, 0, 0, tzinfo=timezone.utc)
            jd = self._datetime_to_jd(dt)
            earth = self._calc_planet("earth", jd)
            marks.append({"lon": float(earth["longitude"] % 360.0), "label": labels[m - 1]})
        return marks

    # ----- Visualisierung (HTML/Canvas) -----
    def _generate_visualization_html(self) -> str:
        colors = {
            "mercury": "#8C7853", "venus": "#FFC649", "earth": "#4A90E2",
            "mars": "#CD5C5C", "jupiter": "#DAA520", "saturn": "#F4A460",
            "uranus": "#4FD0E2", "neptune": "#4169E1", "pluto": "#9B870C",
            "jwst": "#FF1493",
        }
        positions = self._positions_info.get("positions", {})
        lang = getattr(getattr(self._hass, "config", None), "language", "en") or "en"

        data = []
        for pid, pdata in self._planets.items():
            pname = pdata.get("name", {}).get(lang) or pdata.get("name", {}).get("en") or pid.title()
            pos = positions.get(pname)
            if not pos:
                continue
            data.append({
                "id": pid,
                "name": pname,
                "longitude": float(pos.get("longitude", 0.0)),
                "distance": float(pos.get("distance", 1.0)),
                "color": colors.get(pid, "#FFFFFF"),
                "symbol": pdata.get("symbol", ""),
            })

        # Monats-Markierungen
        year = datetime.now(timezone.utc).year
        month_marks = self._monthly_markers(year)

        return f"""
        <div style="width:100%;max-width:600px;margin:auto">
          <canvas id="solar-map" width="600" height="600" style="width:100%;border:1px solid #333;background:#000033"></canvas>
          <script>
          (function(){{
            const canvas = document.getElementById('solar-map');
            const ctx = canvas.getContext('2d');
            const cx = canvas.width/2, cy = canvas.height/2;
            const maxR = Math.min(cx, cy) - 30;
            const scale = "{self._visualization_scale}";
            const planets = {json.dumps(data)};
            const marks = {json.dumps(month_marks)};

            function scaleR(d) {{
              if (scale === 'logarithmic') return Math.log(d + 1)/Math.log(40)*maxR;
              if (scale === 'compressed') return Math.pow(d, 0.5)/Math.pow(40, 0.5)*maxR;
              return (d/40)*maxR;
            }}

            // Hintergrund
            ctx.fillStyle = '#000033'; ctx.fillRect(0,0,canvas.width,canvas.height);

            // Sonne
            ctx.beginPath(); ctx.arc(cx,cy,15,0,2*Math.PI);
            ctx.fillStyle='#FFD700'; ctx.fill(); ctx.strokeStyle='#FFA500'; ctx.lineWidth=2; ctx.stroke();

            // 0°/1.1. Referenz nach oben (CCW)
            ctx.strokeStyle = '#666'; ctx.lineWidth = 1; ctx.setLineDash([6,4]);
            ctx.beginPath(); ctx.moveTo(cx, cy); ctx.lineTo(cx, 20); ctx.stroke(); ctx.setLineDash([]);
            ctx.fillStyle = '#FFFFFF'; ctx.font = '11px Arial'; ctx.textAlign = 'center';
            ctx.fillText('0° / 1.1.', cx, 16);

            // Monats-Linien (1. jedes Monats) – CCW: Winkel = (90 - lon)
            ctx.strokeStyle = '#555'; ctx.lineWidth = 1; ctx.setLineDash([4,4]);
            marks.forEach(m => {{
              const ang = (90 - m.lon) * Math.PI/180;
              const x = cx + Math.cos(ang) * (maxR);
              const y = cy + Math.sin(ang) * (maxR);
              ctx.beginPath(); ctx.moveTo(cx, cy); ctx.lineTo(x, y); ctx.stroke();
              // Label außen leicht versetzt
              const lx = cx + Math.cos(ang) * (maxR + 12);
              const ly = cy + Math.sin(ang) * (maxR + 12);
              ctx.fillStyle='#fff'; ctx.font='10px Arial'; ctx.textAlign='center';
              ctx.fillText(m.label, lx, ly);
            }});
            ctx.setLineDash([]);

            // Orbits & Planeten (CCW)
            planets.forEach(p => {{
              const r = scaleR(p.distance);
              ctx.beginPath(); ctx.arc(cx,cy,r,0,2*Math.PI);
              ctx.strokeStyle='#444'; ctx.lineWidth=0.5; ctx.stroke();

              const ang = (90 - p.longitude) * Math.PI/180;  // CCW
              const x = cx + Math.cos(ang)*r;
              const y = cy + Math.sin(ang)*r;

              ctx.beginPath(); ctx.arc(x,y,5,0,2*Math.PI);
              ctx.fillStyle=p.color; ctx.fill();
              ctx.strokeStyle='#fff'; ctx.lineWidth=1; ctx.stroke();

              ctx.fillStyle='#fff'; ctx.font='10px Arial'; ctx.textAlign='center';
              ctx.fillText((p.symbol? p.symbol+' ' : '') + p.name, x, y-10);
            }});

            ctx.fillStyle = '#FFFFFF';
            ctx.font = '11px Arial';
            ctx.textAlign = 'left';
            ctx.fillText('CCW · Sonne im Zentrum · 0°/1.1. oben · Maßstab: ' + scale, 10, canvas.height - 10);
          }})();
          </script>
        </div>
        """

    # ----- Visualisierung (SVG, kein JS) -----
    def _generate_visualization_svg(self) -> str:
        """Inline-SVG: Draufsicht, CCW, Sonne in Mitte, 0°/1.1. oben, Monatslinien."""
        width, height = 600, 600
        cx, cy = width // 2, height // 2
        margin = 30
        maxR = min(cx, cy) - margin
        scale = self._visualization_scale

        colors = {
            "mercury": "#8C7853", "venus": "#FFC649", "earth": "#4A90E2",
            "mars": "#CD5C5C", "jupiter": "#DAA520", "saturn": "#F4A460",
            "uranus": "#4FD0E2", "neptune": "#4169E1", "pluto": "#9B870C",
            "jwst": "#FF1493",
        }
        positions = self._positions_info.get("positions", {})
        lang = getattr(getattr(self._hass, "config", None), "language", "en") or "en"

        def scale_r(d: float) -> float:
            d = float(d)
            if scale == "logarithmic":
                return math.log(d + 1.0) / math.log(40.0) * maxR
            elif scale == "compressed":
                return (d ** 0.5) / (40.0 ** 0.5) * maxR
            else:
                return (d / 40.0) * maxR

        # Monats-Markierungen (Helio-Lon der Erde am 1. jedes Monats)
        year = datetime.now(timezone.utc).year
        marks = self._monthly_markers(year)

        items = []
        for pid, pdata in self._planets.items():
            if pid == "earth":
                continue
            pname = pdata.get("name", {}).get(lang) or pdata.get("name", {}).get("en") or pid.title()
            pos = positions.get(pname)
            if not pos:
                continue
            items.append({
                "id": pid,
                "name": pname,
                "lon": float(pos.get("longitude", 0.0)),
                "dist": float(pos.get("distance", 1.0)),
                "color": colors.get(pid, "#FFFFFF"),
                "symbol": pdata.get("symbol", ""),
            })

        parts = []
        parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="Solar System Map (CCW)">')
        parts.append('<defs><style><![CDATA[text{font-family:Arial,system-ui,Segoe UI,Roboto,sans-serif}]]></style></defs>')
        parts.append(f'<rect x="0" y="0" width="{width}" height="{height}" fill="#000033"/>')
        parts.append(f'<circle cx="{cx}" cy="{cy}" r="15" fill="#FFD700" stroke="#FFA500" stroke-width="2"/>')
        # 0°/1.1. oben
        parts.append(f'<line x1="{cx}" y1="{cy}" x2="{cx}" y2="{margin}" stroke="#666" stroke-dasharray="6,4" stroke-width="1"/>')
        parts.append(f'<text x="{cx}" y="{margin-6}" fill="#FFFFFF" font-size="11" text-anchor="middle">0° / 1.1.</text>')

        # Monatslinien (CCW: ang = 90 - lon)
        for m in marks:
            ang = math.radians(90.0 - float(m["lon"]))
            x = cx + math.cos(ang) * maxR
            y = cy + math.sin(ang) * maxR
            parts.append(f'<line x1="{cx}" y1="{cy}" x2="{x:.2f}" y2="{y:.2f}" stroke="#555" stroke-dasharray="4,4" stroke-width="1"/>')
            lx = cx + math.cos(ang) * (maxR + 12)
            ly = cy + math.sin(ang) * (maxR + 12)
            label = str(m["label"]).replace("&", "&amp;")
            parts.append(f'<text x="{lx:.2f}" y="{ly:.2f}" fill="#FFFFFF" font-size="10" text-anchor="middle">{label}</text>')

        # Orbits & Planeten (CCW)
        for it in items:
            r = scale_r(it["dist"])
            parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r:.2f}" fill="none" stroke="#444" stroke-width="0.6"/>')
            ang = math.radians(90.0 - it["lon"])  # CCW
            x = cx + math.cos(ang) * r
            y = cy + math.sin(ang) * r
            parts.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="5" fill="{it["color"]}" stroke="#FFFFFF" stroke-width="1"/>')
            label = (it["symbol"] + " " if it["symbol"] else "") + it["name"]
            label = label.replace("&", "&amp;")
            parts.append(f'<text x="{x:.2f}" y="{(y-10):.2f}" fill="#FFFFFF" font-size="10" text-anchor="middle">{label}</text>')

        parts.append(f'<text x="10" y="{height-10}" fill="#FFFFFF" font-size="11">CCW · Sonne im Zentrum · 0°/1.1. oben · Maßstab: {scale}</text>')
        parts.append('</svg>')
        return "".join(parts)

    # ----- Hilfen -----
    def _planet_local_name(self, pid: str) -> str:
        lang = getattr(getattr(self._hass, "config", None), "language", "en") or "en"
        names = self._planets.get(pid, {}).get("name", {})
        return names.get(lang) or names.get("en", pid.title())

    def _format_position_line(self, pid: str, position: Dict[str, Any]) -> str:
        symbol = self._planets[pid].get("symbol", "")
        name = self._planet_local_name(pid)
        parts = [f"{symbol} {name}:"]

        if position.get("location") == "L2 Lagrange Point":
            parts.append("L2")
            km = position.get("distance_from_earth_km")
            if self._show_distance and isinstance(km, (int, float)):
                parts.append(f"{km/1e6:.1f} Mio km (from Earth)")
        else:
            parts.append(f"{position['longitude']:.1f}°")
            if self._show_distance:
                au = position["distance"]
                km = au * 149_597_870.7
                parts.append(f"{au:.3f} AU ({km/1e6:.1f} Mio km)")
            if self._show_constellation:
                cname, csym = self._get_constellation(position["longitude"])
                parts.append(f"{csym} {cname}")

        if self._show_visibility and "visibility" in position:
            vis = position["visibility"]
            parts.append("👁 " + (f"{vis.get('rise_time','?')}-{vis.get('set_time','?')}" if vis.get("visible") else "nicht sichtbar"))

        if self._show_retrograde and position.get("retrograde"):
            parts.append("℞")

        return " | ".join(parts)

    # ----- Update -----
    def update(self) -> None:
        """Berechnet/aktualisiert die Zustands- und Attributdaten."""
        opts = super().get_plugin_options()

        # Fallback: einige Implementationen legen Optionen unter calendar_options ab
        try:
            entry_id = getattr(self, "_config_entry_id", None)
            cal_id = getattr(self, "_calendar_id", None)
            if (not opts or not isinstance(opts, dict)) and entry_id and cal_id and _CONFIG_ENTRIES:
                ce = _CONFIG_ENTRIES.get(entry_id)
                data = getattr(ce, "data", {}) or {}
                calopts = (data.get("calendar_options") or {}).get(cal_id, {})
                if calopts:
                    opts = dict(calopts)
        except Exception as _e:
            _LOGGER.debug(f"Options fallback failed: {_e}")

        try:
            self._display_planet = str(opts.get("display_planet", self._display_planet))
            self._coordinate_system = str(opts.get("coordinate_system", self._coordinate_system))
            self._show_visibility = bool(opts.get("show_visibility", self._show_visibility))
            self._show_distance = bool(opts.get("show_distance", self._show_distance))
            self._show_constellation = bool(opts.get("show_constellation", self._show_constellation))
            self._show_retrograde = bool(opts.get("show_retrograde", self._show_retrograde))
            self._enable_visualization = bool(opts.get("enable_visualization", self._enable_visualization))
            self._visualization_scale = str(opts.get("visualization_scale", self._visualization_scale))

            lat = float(opts.get("observer_latitude", 0.0) or 0.0)
            lon = float(opts.get("observer_longitude", 0.0) or 0.0)
            if abs(lat) > 1e-9:
                self._observer_latitude = lat
            if abs(lon) > 1e-9:
                self._observer_longitude = lon
        except Exception as exc:
            _LOGGER.debug(f"Option parsing issue: {exc}")

        now = datetime.now(timezone.utc)
        jd = self._datetime_to_jd(now)
        AU_KM = 149_597_870.7

        # Erde zuerst für geozentrische Umrechnung
        earth = self._calc_planet("earth", jd) if "earth" in self._planets else {"longitude": 0.0, "distance": 1.0}

        result: Dict[str, Any] = {
            "julian_date": jd,
            "timestamp": now.isoformat(),
            "observer_location": {"latitude": self._observer_latitude, "longitude": self._observer_longitude},
            "positions": {},
        }

        # Welche Planeten?
        planet_ids = list(self._planets.keys()) if self._display_planet == "all" else [self._display_planet]
        for pid in planet_ids:
            if pid not in self._planets or pid == "earth":
                continue

            helio = self._calc_planet(pid, jd)
            pos = helio
            if self._coordinate_system == "geocentric":
                pos = self._to_geocentric(helio, earth)

            cname, csym = self._get_constellation(pos["longitude"])
            pos["constellation"] = cname
            pos["constellation_symbol"] = csym

            pos["distance_au"] = pos["distance"]
            pos["distance_km"] = pos["distance"] * AU_KM
            pos["distance_million_km"] = pos["distance_km"] / 1e6

            if self._show_visibility:
                geo_now = pos if self._coordinate_system == "geocentric" else self._to_geocentric(helio, earth)
                pos["visibility"] = self._approx_visibility(pid, geo_now["longitude"], earth["longitude"])

            if self._show_retrograde:
                jd_prev = jd - 1.0
                earth_prev = self._calc_planet("earth", jd_prev)
                helio_prev = self._calc_planet(pid, jd_prev)
                geo_now = pos if self._coordinate_system == "geocentric" else self._to_geocentric(helio, earth)
                geo_prev = self._to_geocentric(helio_prev, earth_prev)
                dlon = ((geo_now["longitude"] - geo_prev["longitude"] + 540.0) % 360.0) - 180.0
                pos["retrograde"] = dlon < 0

            result["positions"][self._planet_local_name(pid)] = pos

        self._positions_info = result

        # Zustandsstring
        if self._display_planet == "all":
            self._state = f"{len(result['positions'])} planets tracked"
        else:
            pid = self._display_planet
            name = self._planet_local_name(pid)
            pos = result["positions"].get(name, {})
            self._state = self._format_position_line(pid, pos) if pos else f"{name}: No data"


__all__ = ["SolarSystemSensor", "CALENDAR_INFO"]
