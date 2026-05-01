# Cosmic Speedometer - Version 1.3.0
# A fun "tachometer" showing how fast Earth and the Solar System are moving
# through space at different scales.
# Now with scientific uncertainty percentages and galactic calendar!

from __future__ import annotations

import logging
import math
from typing import Any, Dict, Optional, Tuple

from homeassistant.core import HomeAssistant

from ..sensor import AlternativeTimeSensorBase

_LOGGER = logging.getLogger(__name__)

# ============================================
# CALENDAR METADATA
# ============================================

UPDATE_INTERVAL = 60  # Update every minute

# Physical constants
SPEED_OF_LIGHT_KMH = 1079252848.8  # km/h (c)
SPEED_OF_LIGHT_KMS = 299792.458  # km/s
SPEED_OF_SOUND_KMH = 1234.8  # km/h (Mach 1 at sea level, 20°C)
AU_IN_KM = 149597870.7  # 1 AU in km
LIGHTYEAR_IN_KM = 9460730472580.8  # 1 light-year in km
PARSEC_IN_KM = 30856775814913.673  # 1 parsec in km
EARTH_CIRCUMFERENCE_KM = 40075.017  # Earth's equatorial circumference in km
MOON_DISTANCE_KM = 384400.0  # Average Earth-Moon distance in km
LIGHTSECOND_IN_KM = 299792.458  # 1 light-second in km

# Galactic year constants
GALACTIC_YEAR_EARTH_YEARS = 225000000  # 225 million Earth years per galactic year
GALACTIC_YEAR_UNCERTAINTY = 11.0  # ±11% (range 200-250 million years)
SUN_AGE_EARTH_YEARS = 4600000000  # 4.6 billion Earth years
SUN_AGE_UNCERTAINTY = 1.0  # ±1% (very well determined from meteorites)
# Reference point: We estimate the Sun is currently ~4.2% into its current galactic orbit
# Based on position relative to last perihelion passage

CALENDAR_INFO = {
    "id": "cosmic_speedometer",
    "version": "1.3.0",
    "icon": "mdi:speedometer",
    "category": "space",
    "accuracy": "calculated",
    "update_interval": UPDATE_INTERVAL,

    # Multi-language names
    "name": {
        "en": "Cosmic Speedometer",
        "de": "Kosmisches Tachometer",
        "es": "Velocímetro Cósmico",
        "fr": "Tachymètre Cosmique",
        "it": "Tachimetro Cosmico",
        "nl": "Kosmische Snelheidsmeter",
        "pl": "Kosmiczny Prędkościomierz",
        "pt": "Velocímetro Cósmico",
        "ru": "Космический Спидометр",
        "ja": "宇宙速度計",
        "zh": "宇宙速度计",
        "ko": "우주 속도계"
    },

    # Short descriptions for UI
    "description": {
        "en": "How fast are you really moving? Earth rotation, orbit, solar system, and galaxy speeds!",
        "de": "Wie schnell bewegst du dich wirklich? Erdrotation, Umlaufbahn, Sonnensystem und Galaxiegeschwindigkeiten!",
        "es": "¿Qué tan rápido te mueves realmente? ¡Rotación terrestre, órbita, sistema solar y velocidades galácticas!",
        "fr": "À quelle vitesse vous déplacez-vous vraiment ? Rotation terrestre, orbite, système solaire et vitesses galactiques !",
        "it": "Quanto velocemente ti stai muovendo davvero? Rotazione terrestre, orbita, sistema solare e velocità galattiche!",
        "nl": "Hoe snel beweeg je echt? Aardrotatie, baan, zonnestelsel en melkwegsnelheden!",
        "pl": "Jak szybko naprawdę się poruszasz? Rotacja Ziemi, orbita, Układ Słoneczny i prędkości galaktyczne!",
        "pt": "Quão rápido você está realmente se movendo? Rotação da Terra, órbita, sistema solar e velocidades galácticas!",
        "ru": "Как быстро вы на самом деле движетесь? Вращение Земли, орбита, Солнечная система и скорости галактики!",
        "ja": "あなたは実際どれくらい速く動いていますか？地球の自転、公転、太陽系、銀河の速度！",
        "zh": "你实际移动有多快？地球自转、公转、太阳系和银河系速度！",
        "ko": "당신은 실제로 얼마나 빨리 움직이고 있나요? 지구 자전, 공전, 태양계 및 은하 속도!"
    },

    # Invalid unit message (multi-language)
    "invalid_unit_message": {
        "en": "Not a valid unit of measurement",
        "de": "Keine valide Maßeinheit",
        "es": "No es una unidad de medida válida",
        "fr": "Pas une unité de mesure valide",
        "it": "Non è un'unità di misura valida",
        "nl": "Geen geldige maateenheid",
        "pl": "Nieprawidłowa jednostka miary",
        "pt": "Não é uma unidade de medida válida",
        "ru": "Недопустимая единица измерения",
        "ja": "有効な測定単位ではありません",
        "zh": "无效的测量单位",
        "ko": "유효한 측정 단위가 아닙니다"
    },

    # Configuration options
    "config_options": {
        "speed_unit": {
            "type": "select",
            "default": "km/h",
            "options": [
                "km/h", "km/s", "m/s",           # Metrisch
                "c", "Mach",                      # Relativ
                "AU/h", "AU/s",                   # Astronomische Einheiten
                "ly/h", "ly/s",                   # Lichtjahre
                "pc/h", "pc/s",                   # Parsec
                "ls/s",                           # Lichtsekunden pro Sekunde
                "🌍/h", "🌙/h",                   # Anschaulich
                "mph"                             # Ungültig (Easter Egg)
            ],
            "label": {
                "en": "Speed Unit",
                "de": "Geschwindigkeitseinheit",
                "es": "Unidad de Velocidad",
                "fr": "Unité de Vitesse",
                "it": "Unità di Velocità",
                "nl": "Snelheidseenheid",
                "pl": "Jednostka Prędkości",
                "pt": "Unidade de Velocidade",
                "ru": "Единица Скорости",
                "ja": "速度単位",
                "zh": "速度单位",
                "ko": "속도 단위"
            },
            "description": {
                "en": "Unit for displaying speeds: metric (km/h, m/s), astronomical (AU, ly, pc), relative (c, Mach), or fun (🌍/h, 🌙/h)",
                "de": "Einheit für Geschwindigkeiten: metrisch (km/h, m/s), astronomisch (AU, ly, pc), relativ (c, Mach) oder lustig (🌍/h, 🌙/h)",
                "es": "Unidad para velocidades: métrica (km/h, m/s), astronómica (AU, ly, pc), relativa (c, Mach) o divertida (🌍/h, 🌙/h)",
                "fr": "Unité pour les vitesses: métrique (km/h, m/s), astronomique (AU, ly, pc), relative (c, Mach) ou amusante (🌍/h, 🌙/h)",
                "it": "Unità per le velocità: metrica (km/h, m/s), astronomica (AU, ly, pc), relativa (c, Mach) o divertente (🌍/h, 🌙/h)",
                "nl": "Eenheid voor snelheden: metrisch (km/h, m/s), astronomisch (AU, ly, pc), relatief (c, Mach) of leuk (🌍/h, 🌙/h)",
                "pl": "Jednostka prędkości: metryczna (km/h, m/s), astronomiczna (AU, ly, pc), względna (c, Mach) lub zabawna (🌍/h, 🌙/h)",
                "pt": "Unidade para velocidades: métrica (km/h, m/s), astronômica (AU, ly, pc), relativa (c, Mach) ou divertida (🌍/h, 🌙/h)",
                "ru": "Единица скорости: метрическая (км/ч, м/с), астрономическая (AU, ly, pc), относительная (c, Mach) или забавная (🌍/h, 🌙/h)",
                "ja": "速度単位: メートル法 (km/h, m/s)、天文学的 (AU, ly, pc)、相対的 (c, Mach)、または面白い (🌍/h, 🌙/h)",
                "zh": "速度单位: 公制 (km/h, m/s)、天文 (AU, ly, pc)、相对 (c, Mach) 或有趣的 (🌍/h, 🌙/h)",
                "ko": "속도 단위: 미터법 (km/h, m/s), 천문학적 (AU, ly, pc), 상대적 (c, Mach) 또는 재미있는 (🌍/h, 🌙/h)"
            }
        },
        "use_observer_location": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Use Home Location",
                "de": "Heimatstandort verwenden",
                "es": "Usar Ubicación de Casa",
                "fr": "Utiliser l'Emplacement Domicile",
                "it": "Usa Posizione Casa",
                "nl": "Gebruik Thuislocatie",
                "pl": "Użyj Lokalizacji Domowej",
                "pt": "Usar Localização de Casa",
                "ru": "Использовать Домашнее Местоположение",
                "ja": "ホームの場所を使用",
                "zh": "使用家庭位置",
                "ko": "홈 위치 사용"
            },
            "description": {
                "en": "Calculate rotation speed based on your Home Assistant location (latitude affects rotation speed)",
                "de": "Rotationsgeschwindigkeit basierend auf Ihrem Home Assistant Standort berechnen (Breitengrad beeinflusst Rotationsgeschwindigkeit)",
                "es": "Calcular velocidad de rotación según su ubicación de Home Assistant (la latitud afecta la velocidad de rotación)",
                "fr": "Calculer la vitesse de rotation en fonction de votre emplacement Home Assistant (la latitude affecte la vitesse de rotation)",
                "it": "Calcola la velocità di rotazione in base alla posizione di Home Assistant (la latitudine influisce sulla velocità di rotazione)",
                "nl": "Bereken rotatiesnelheid op basis van uw Home Assistant-locatie (breedtegraad beïnvloedt rotatiesnelheid)",
                "pl": "Oblicz prędkość rotacji na podstawie lokalizacji Home Assistant (szerokość geograficzna wpływa na prędkość rotacji)",
                "pt": "Calcular velocidade de rotação com base na localização do Home Assistant (latitude afeta velocidade de rotação)",
                "ru": "Рассчитать скорость вращения на основе местоположения Home Assistant (широта влияет на скорость вращения)",
                "ja": "Home Assistantの場所に基づいて回転速度を計算（緯度が回転速度に影響）",
                "zh": "根据您的Home Assistant位置计算自转速度（纬度影响自转速度）",
                "ko": "Home Assistant 위치를 기반으로 회전 속도 계산 (위도가 회전 속도에 영향)"
            }
        },
        "show_earth_rotation": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show Earth Rotation Speed",
                "de": "Erdrotationsgeschwindigkeit anzeigen",
                "es": "Mostrar Velocidad de Rotación Terrestre",
                "fr": "Afficher Vitesse de Rotation Terrestre",
                "it": "Mostra Velocità di Rotazione Terrestre",
                "nl": "Toon Aardrotatie Snelheid",
                "pl": "Pokaż Prędkość Rotacji Ziemi",
                "pt": "Mostrar Velocidade de Rotação da Terra",
                "ru": "Показать Скорость Вращения Земли",
                "ja": "地球の自転速度を表示",
                "zh": "显示地球自转速度",
                "ko": "지구 자전 속도 표시"
            },
            "description": {
                "en": "Your speed due to Earth's daily rotation (varies by latitude: ~1,670 km/h at equator, 0 at poles)",
                "de": "Ihre Geschwindigkeit durch die tägliche Erdrotation (variiert nach Breitengrad: ~1.670 km/h am Äquator, 0 an den Polen)",
                "es": "Su velocidad debido a la rotación diaria de la Tierra (varía según latitud: ~1.670 km/h en el ecuador, 0 en los polos)",
                "fr": "Votre vitesse due à la rotation quotidienne de la Terre (varie selon la latitude: ~1 670 km/h à l'équateur, 0 aux pôles)",
                "it": "La tua velocità dovuta alla rotazione giornaliera della Terra (varia in base alla latitudine: ~1.670 km/h all'equatore, 0 ai poli)",
                "nl": "Uw snelheid door de dagelijkse aardrotatie (varieert per breedtegraad: ~1.670 km/u op de evenaar, 0 op de polen)",
                "pl": "Twoja prędkość z powodu dziennej rotacji Ziemi (zależy od szerokości: ~1670 km/h na równiku, 0 na biegunach)",
                "pt": "Sua velocidade devido à rotação diária da Terra (varia por latitude: ~1.670 km/h no equador, 0 nos polos)",
                "ru": "Ваша скорость из-за суточного вращения Земли (зависит от широты: ~1670 км/ч на экваторе, 0 на полюсах)",
                "ja": "地球の日周自転による速度（緯度により変化：赤道で約1,670 km/h、極では0）",
                "zh": "由于地球每日自转产生的速度（因纬度而异：赤道约1,670 km/h，两极为0）",
                "ko": "지구의 일일 자전으로 인한 속도 (위도에 따라 다름: 적도에서 ~1,670 km/h, 극지방에서 0)"
            }
        },
        "show_earth_orbit": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show Earth Orbital Speed",
                "de": "Erdumlaufgeschwindigkeit anzeigen",
                "es": "Mostrar Velocidad Orbital Terrestre",
                "fr": "Afficher Vitesse Orbitale Terrestre",
                "it": "Mostra Velocità Orbitale Terrestre",
                "nl": "Toon Aardbaansnelheid",
                "pl": "Pokaż Prędkość Orbitalną Ziemi",
                "pt": "Mostrar Velocidade Orbital da Terra",
                "ru": "Показать Орбитальную Скорость Земли",
                "ja": "地球の公転速度を表示",
                "zh": "显示地球公转速度",
                "ko": "지구 공전 속도 표시"
            },
            "description": {
                "en": "Earth's speed around the Sun (~107,000 km/h or ~30 km/s)",
                "de": "Erdgeschwindigkeit um die Sonne (~107.000 km/h oder ~30 km/s)",
                "es": "Velocidad de la Tierra alrededor del Sol (~107.000 km/h o ~30 km/s)",
                "fr": "Vitesse de la Terre autour du Soleil (~107 000 km/h ou ~30 km/s)",
                "it": "Velocità della Terra intorno al Sole (~107.000 km/h o ~30 km/s)",
                "nl": "Snelheid van de Aarde rond de Zon (~107.000 km/u of ~30 km/s)",
                "pl": "Prędkość Ziemi wokół Słońca (~107 000 km/h lub ~30 km/s)",
                "pt": "Velocidade da Terra ao redor do Sol (~107.000 km/h ou ~30 km/s)",
                "ru": "Скорость Земли вокруг Солнца (~107 000 км/ч или ~30 км/с)",
                "ja": "太陽の周りの地球の速度（約107,000 km/h または約30 km/s）",
                "zh": "地球绕太阳运行速度（约107,000 km/h 或约30 km/s）",
                "ko": "태양 주위를 도는 지구의 속도 (~107,000 km/h 또는 ~30 km/s)"
            }
        },
        "show_solar_system_speed": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show Solar System Speed in Galaxy",
                "de": "Sonnensystemgeschwindigkeit in Galaxie anzeigen",
                "es": "Mostrar Velocidad del Sistema Solar en Galaxia",
                "fr": "Afficher Vitesse du Système Solaire dans la Galaxie",
                "it": "Mostra Velocità del Sistema Solare nella Galassia",
                "nl": "Toon Zonnestelselsnelheid in Melkweg",
                "pl": "Pokaż Prędkość Układu Słonecznego w Galaktyce",
                "pt": "Mostrar Velocidade do Sistema Solar na Galáxia",
                "ru": "Показать Скорость Солнечной Системы в Галактике",
                "ja": "銀河系内の太陽系速度を表示",
                "zh": "显示太阳系在银河系中的速度",
                "ko": "은하계 내 태양계 속도 표시"
            },
            "description": {
                "en": "Solar System's speed around the Milky Way center (~828,000 km/h or ~230 km/s)",
                "de": "Geschwindigkeit des Sonnensystems um das Milchstraßenzentrum (~828.000 km/h oder ~230 km/s)",
                "es": "Velocidad del Sistema Solar alrededor del centro de la Vía Láctea (~828.000 km/h o ~230 km/s)",
                "fr": "Vitesse du Système Solaire autour du centre de la Voie Lactée (~828 000 km/h ou ~230 km/s)",
                "it": "Velocità del Sistema Solare intorno al centro della Via Lattea (~828.000 km/h o ~230 km/s)",
                "nl": "Snelheid van het Zonnestelsel rond het centrum van de Melkweg (~828.000 km/u of ~230 km/s)",
                "pl": "Prędkość Układu Słonecznego wokół centrum Drogi Mlecznej (~828 000 km/h lub ~230 km/s)",
                "pt": "Velocidade do Sistema Solar ao redor do centro da Via Láctea (~828.000 km/h ou ~230 km/s)",
                "ru": "Скорость Солнечной системы вокруг центра Млечного Пути (~828 000 км/ч или ~230 км/с)",
                "ja": "天の川銀河の中心周りの太陽系の速度（約828,000 km/h または約230 km/s）",
                "zh": "太阳系绕银河系中心运行速度（约828,000 km/h 或约230 km/s）",
                "ko": "은하수 중심 주위를 도는 태양계의 속도 (~828,000 km/h 또는 ~230 km/s)"
            }
        },
        "show_galaxy_speed": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show Milky Way Speed Through Universe",
                "de": "Milchstraßengeschwindigkeit durchs Universum anzeigen",
                "es": "Mostrar Velocidad de Vía Láctea en Universo",
                "fr": "Afficher Vitesse de la Voie Lactée dans l'Univers",
                "it": "Mostra Velocità della Via Lattea nell'Universo",
                "nl": "Toon Melkwegsnelheid door Universum",
                "pl": "Pokaż Prędkość Drogi Mlecznej przez Wszechświat",
                "pt": "Mostrar Velocidade da Via Láctea no Universo",
                "ru": "Показать Скорость Млечного Пути во Вселенной",
                "ja": "宇宙を通る天の川銀河の速度を表示",
                "zh": "显示银河系在宇宙中的速度",
                "ko": "우주를 통과하는 은하수 속도 표시"
            },
            "description": {
                "en": "Milky Way's speed towards the Great Attractor (~2,100,000 km/h or ~600 km/s)",
                "de": "Geschwindigkeit der Milchstraße zum Großen Attraktor (~2.100.000 km/h oder ~600 km/s)",
                "es": "Velocidad de la Vía Láctea hacia el Gran Atractor (~2.100.000 km/h o ~600 km/s)",
                "fr": "Vitesse de la Voie Lactée vers le Grand Attracteur (~2 100 000 km/h ou ~600 km/s)",
                "it": "Velocità della Via Lattea verso il Grande Attrattore (~2.100.000 km/h o ~600 km/s)",
                "nl": "Snelheid van de Melkweg naar de Grote Attractor (~2.100.000 km/u of ~600 km/s)",
                "pl": "Prędkość Drogi Mlecznej w kierunku Wielkiego Atraktora (~2 100 000 km/h lub ~600 km/s)",
                "pt": "Velocidade da Via Láctea em direção ao Grande Atrator (~2.100.000 km/h ou ~600 km/s)",
                "ru": "Скорость Млечного Пути к Великому Аттрактору (~2 100 000 км/ч или ~600 км/с)",
                "ja": "グレートアトラクターに向かう天の川銀河の速度（約2,100,000 km/h または約600 km/s）",
                "zh": "银河系朝向巨引源的速度（约2,100,000 km/h 或约600 km/s）",
                "ko": "거대 끌개를 향한 은하수의 속도 (~2,100,000 km/h 또는 ~600 km/s)"
            }
        },
        "show_sun_rotation": {
            "type": "boolean",
            "default": False,
            "label": {
                "en": "Show Sun Equatorial Rotation Speed",
                "de": "Sonnenäquatorrotationsgeschwindigkeit anzeigen",
                "es": "Mostrar Velocidad de Rotación Ecuatorial del Sol",
                "fr": "Afficher Vitesse de Rotation Équatoriale du Soleil",
                "it": "Mostra Velocità di Rotazione Equatoriale del Sole",
                "nl": "Toon Zon Equatoriale Rotatiesnelheid",
                "pl": "Pokaż Prędkość Rotacji Równikowej Słońca",
                "pt": "Mostrar Velocidade de Rotação Equatorial do Sol",
                "ru": "Показать Экваториальную Скорость Вращения Солнца",
                "ja": "太陽の赤道回転速度を表示",
                "zh": "显示太阳赤道自转速度",
                "ko": "태양 적도 회전 속도 표시"
            },
            "description": {
                "en": "The Sun's surface rotation speed at its equator (~7,189 km/h)",
                "de": "Die Oberflächenrotationsgeschwindigkeit der Sonne am Äquator (~7.189 km/h)",
                "es": "La velocidad de rotación de la superficie del Sol en su ecuador (~7.189 km/h)",
                "fr": "La vitesse de rotation de la surface du Soleil à son équateur (~7 189 km/h)",
                "it": "La velocità di rotazione superficiale del Sole al suo equatore (~7.189 km/h)",
                "nl": "De oppervlakte-rotatiesnelheid van de Zon aan de evenaar (~7.189 km/u)",
                "pl": "Prędkość rotacji powierzchni Słońca na równiku (~7189 km/h)",
                "pt": "A velocidade de rotação da superfície do Sol em seu equador (~7.189 km/h)",
                "ru": "Скорость вращения поверхности Солнца на экваторе (~7189 км/ч)",
                "ja": "赤道での太陽の表面回転速度（約7,189 km/h）",
                "zh": "太阳赤道表面自转速度（约7,189 km/h）",
                "ko": "적도에서의 태양 표면 회전 속도 (~7,189 km/h)"
            }
        },
        "show_total_speed": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show Total Combined Speed",
                "de": "Gesamte kombinierte Geschwindigkeit anzeigen",
                "es": "Mostrar Velocidad Total Combinada",
                "fr": "Afficher Vitesse Totale Combinée",
                "it": "Mostra Velocità Totale Combinata",
                "nl": "Toon Totale Gecombineerde Snelheid",
                "pl": "Pokaż Całkowitą Łączną Prędkość",
                "pt": "Mostrar Velocidade Total Combinada",
                "ru": "Показать Общую Комбинированную Скорость",
                "ja": "合計速度を表示",
                "zh": "显示总合速度",
                "ko": "총 합산 속도 표시"
            },
            "description": {
                "en": "Your approximate total speed through space (all motions combined)",
                "de": "Ihre ungefähre Gesamtgeschwindigkeit durch den Weltraum (alle Bewegungen kombiniert)",
                "es": "Su velocidad total aproximada a través del espacio (todos los movimientos combinados)",
                "fr": "Votre vitesse totale approximative à travers l'espace (tous les mouvements combinés)",
                "it": "La tua velocità totale approssimativa attraverso lo spazio (tutti i movimenti combinati)",
                "nl": "Uw geschatte totale snelheid door de ruimte (alle bewegingen gecombineerd)",
                "pl": "Twoja przybliżona całkowita prędkość przez kosmos (wszystkie ruchy połączone)",
                "pt": "Sua velocidade total aproximada através do espaço (todos os movimentos combinados)",
                "ru": "Ваша приблизительная общая скорость в космосе (все движения вместе)",
                "ja": "宇宙を通る概算総速度（すべての運動を合計）",
                "zh": "您在太空中的大致总速度（所有运动的总和）",
                "ko": "우주를 통과하는 대략적인 총 속도 (모든 운동의 합)"
            }
        },
        "show_fun_comparisons": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show Fun Speed Comparisons",
                "de": "Lustige Geschwindigkeitsvergleiche anzeigen",
                "es": "Mostrar Comparaciones de Velocidad Divertidas",
                "fr": "Afficher Comparaisons de Vitesse Amusantes",
                "it": "Mostra Confronti di Velocità Divertenti",
                "nl": "Toon Leuke Snelheidsvergelijkingen",
                "pl": "Pokaż Zabawne Porównania Prędkości",
                "pt": "Mostrar Comparações de Velocidade Divertidas",
                "ru": "Показать Забавные Сравнения Скоростей",
                "ja": "楽しい速度比較を表示",
                "zh": "显示有趣的速度比较",
                "ko": "재미있는 속도 비교 표시"
            },
            "description": {
                "en": "Compare speeds to everyday objects (bullets, jets, cheetahs, etc.)",
                "de": "Geschwindigkeiten mit Alltagsobjekten vergleichen (Kugeln, Jets, Geparden usw.)",
                "es": "Comparar velocidades con objetos cotidianos (balas, aviones, guepardos, etc.)",
                "fr": "Comparer les vitesses aux objets du quotidien (balles, jets, guépards, etc.)",
                "it": "Confronta le velocità con oggetti quotidiani (proiettili, jet, ghepardi, ecc.)",
                "nl": "Vergelijk snelheden met alledaagse objecten (kogels, jets, cheeta's, enz.)",
                "pl": "Porównaj prędkości z codziennymi obiektami (kule, odrzutowce, gepardy itp.)",
                "pt": "Compare velocidades com objetos cotidianos (balas, jatos, guepardos, etc.)",
                "ru": "Сравните скорости с повседневными объектами (пули, самолеты, гепарды и т.д.)",
                "ja": "日常のものと速度を比較（弾丸、ジェット機、チーターなど）",
                "zh": "将速度与日常物体进行比较（子弹、喷气式飞机、猎豹等）",
                "ko": "일상적인 물체와 속도 비교 (총알, 제트기, 치타 등)"
            }
        },
        "display_mode": {
            "type": "select",
            "default": "total",
            "options": ["total", "earth_rotation", "earth_orbit", "solar_system", "galaxy", "all"],
            "label": {
                "en": "Primary Display",
                "de": "Primäre Anzeige",
                "es": "Visualización Principal",
                "fr": "Affichage Principal",
                "it": "Visualizzazione Principale",
                "nl": "Primaire Weergave",
                "pl": "Główny Wyświetlacz",
                "pt": "Exibição Principal",
                "ru": "Основной Дисплей",
                "ja": "メイン表示",
                "zh": "主显示",
                "ko": "기본 디스플레이"
            },
            "description": {
                "en": "Which speed to show as the main sensor state",
                "de": "Welche Geschwindigkeit als Hauptsensorstatus angezeigt werden soll",
                "es": "Qué velocidad mostrar como estado principal del sensor",
                "fr": "Quelle vitesse afficher comme état principal du capteur",
                "it": "Quale velocità mostrare come stato principale del sensore",
                "nl": "Welke snelheid als hoofdsensorstatus weergeven",
                "pl": "Którą prędkość pokazać jako główny stan czujnika",
                "pt": "Qual velocidade mostrar como estado principal do sensor",
                "ru": "Какую скорость показывать как основное состояние датчика",
                "ja": "メインセンサー状態として表示する速度",
                "zh": "作为主传感器状态显示哪个速度",
                "ko": "주 센서 상태로 표시할 속도"
            }
        },
        "show_galactic_calendar": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show Galactic Calendar",
                "de": "Galaktischen Kalender anzeigen",
                "es": "Mostrar Calendario Galáctico",
                "fr": "Afficher le Calendrier Galactique",
                "it": "Mostra Calendario Galattico",
                "nl": "Toon Galactische Kalender",
                "pl": "Pokaż Kalendarz Galaktyczny",
                "pt": "Mostrar Calendário Galáctico",
                "ru": "Показать Галактический Календарь",
                "ja": "銀河カレンダーを表示",
                "zh": "显示银河日历",
                "ko": "은하 달력 표시"
            },
            "description": {
                "en": "Show Sun's galactic age, current galactic year progress, and time until next galactic new year",
                "de": "Zeigt das galaktische Alter der Sonne, den Fortschritt im aktuellen galaktischen Jahr und die Zeit bis zum nächsten galaktischen Neujahr",
                "es": "Muestra la edad galáctica del Sol, el progreso del año galáctico actual y el tiempo hasta el próximo año nuevo galáctico",
                "fr": "Affiche l'âge galactique du Soleil, la progression de l'année galactique actuelle et le temps jusqu'au prochain nouvel an galactique",
                "it": "Mostra l'età galattica del Sole, il progresso dell'anno galattico attuale e il tempo fino al prossimo capodanno galattico",
                "nl": "Toont de galactische leeftijd van de Zon, de voortgang van het huidige galactische jaar en de tijd tot het volgende galactische nieuwjaar",
                "pl": "Pokazuje wiek galaktyczny Słońca, postęp bieżącego roku galaktycznego i czas do następnego galaktycznego Nowego Roku",
                "pt": "Mostra a idade galáctica do Sol, o progresso do ano galáctico atual e o tempo até o próximo ano novo galáctico",
                "ru": "Показывает галактический возраст Солнца, прогресс текущего галактического года и время до следующего галактического Нового года",
                "ja": "太陽の銀河年齢、現在の銀河年の進捗、次の銀河新年までの時間を表示",
                "zh": "显示太阳的银河年龄、当前银河年进度以及距离下一个银河新年的时间",
                "ko": "태양의 은하 나이, 현재 은하년 진행률, 다음 은하 새해까지의 시간 표시"
            }
        }
    },

    # Speed data and constants
    "speed_data": {
        # All base speeds in km/h for consistency
        # Uncertainty values based on current scientific measurements
        "earth_equator_rotation_kmh": 1674.4,  # km/h at equator
        "earth_equator_rotation_uncertainty": 0.1,  # ±0.1% - very well known
        "earth_radius_km": 6371.0,  # km
        "earth_orbital_speed_kmh": 107208.0,  # ~29.78 km/s
        "earth_orbital_uncertainty": 0.1,  # ±0.1% - very well known from Kepler's laws
        "solar_system_galactic_speed_kmh": 828000.0,  # ~230 km/s (NASA/Wikipedia current value)
        "solar_system_galactic_uncertainty": 10.0,  # ±10% - range 200-250 km/s in literature
        "galaxy_speed_kmh": 2160000.0,  # ~600 km/s towards Great Attractor
        "galaxy_speed_uncertainty": 15.0,  # ±15% - difficult to measure precisely
        "sun_equator_rotation_kmh": 7189.0,  # ~1.997 km/s at Sun's equator
        "sun_equator_rotation_uncertainty": 1.0,  # ±1% - measured via sunspot tracking

        # Galactic calendar data
        "galactic_year_earth_years": 225000000,  # 225 million Earth years
        "galactic_year_uncertainty": 11.0,  # ±11% (range 200-250 million years)
        "sun_age_earth_years": 4600000000,  # 4.6 billion Earth years
        "sun_age_uncertainty": 1.0,  # ±1% - determined from meteorites
        "sun_galactic_orbits_completed": 20.4,  # ~20 complete orbits
        "current_orbit_progress_percent": 44.0,  # Estimated ~44% into current orbit

        # Fun comparison objects (in km/h)
        "comparisons": {
            "walking": {"speed_kmh": 5, "emoji": "🚶"},
            "bicycle": {"speed_kmh": 20, "emoji": "🚴"},
            "car_highway": {"speed_kmh": 120, "emoji": "🚗"},
            "cheetah": {"speed_kmh": 120, "emoji": "🐆"},
            "bullet_train": {"speed_kmh": 320, "emoji": "🚄"},
            "commercial_jet": {"speed_kmh": 900, "emoji": "✈️"},
            "bullet": {"speed_kmh": 2736, "emoji": "🔫"},
            "sr71_blackbird": {"speed_kmh": 3540, "emoji": "🛩️"},
            "space_shuttle": {"speed_kmh": 28000, "emoji": "🚀"},
            "apollo_reentry": {"speed_kmh": 40000, "emoji": "🌙"},
            "voyager_1": {"speed_kmh": 61200, "emoji": "🛸"},
            "parker_solar_probe": {"speed_kmh": 692000, "emoji": "☀️"}
        }
    },

    # Unit display names (multi-language)
    "unit_names": {
        "km/h": {
            "en": "km/h",
            "de": "km/h",
            "es": "km/h",
            "fr": "km/h",
            "it": "km/h",
            "nl": "km/u",
            "pl": "km/h",
            "pt": "km/h",
            "ru": "км/ч",
            "ja": "km/h",
            "zh": "公里/小时",
            "ko": "km/h"
        },
        "km/s": {
            "en": "km/s",
            "de": "km/s",
            "es": "km/s",
            "fr": "km/s",
            "it": "km/s",
            "nl": "km/s",
            "pl": "km/s",
            "pt": "km/s",
            "ru": "км/с",
            "ja": "km/s",
            "zh": "公里/秒",
            "ko": "km/s"
        },
        "m/s": {
            "en": "m/s",
            "de": "m/s",
            "es": "m/s",
            "fr": "m/s",
            "it": "m/s",
            "nl": "m/s",
            "pl": "m/s",
            "pt": "m/s",
            "ru": "м/с",
            "ja": "m/s",
            "zh": "米/秒",
            "ko": "m/s"
        },
        "AU/h": {
            "en": "AU/h",
            "de": "AE/h",
            "es": "UA/h",
            "fr": "UA/h",
            "it": "UA/h",
            "nl": "AE/u",
            "pl": "AU/h",
            "pt": "UA/h",
            "ru": "а.е./ч",
            "ja": "AU/h",
            "zh": "天文单位/小时",
            "ko": "AU/h"
        },
        "AU/s": {
            "en": "AU/s",
            "de": "AE/s",
            "es": "UA/s",
            "fr": "UA/s",
            "it": "UA/s",
            "nl": "AE/s",
            "pl": "AU/s",
            "pt": "UA/s",
            "ru": "а.е./с",
            "ja": "AU/s",
            "zh": "天文单位/秒",
            "ko": "AU/s"
        },
        "ly/h": {
            "en": "ly/h",
            "de": "Lj/h",
            "es": "al/h",
            "fr": "al/h",
            "it": "al/h",
            "nl": "lj/u",
            "pl": "ly/h",
            "pt": "al/h",
            "ru": "св.г./ч",
            "ja": "光年/h",
            "zh": "光年/小时",
            "ko": "광년/h"
        },
        "ly/s": {
            "en": "ly/s",
            "de": "Lj/s",
            "es": "al/s",
            "fr": "al/s",
            "it": "al/s",
            "nl": "lj/s",
            "pl": "ly/s",
            "pt": "al/s",
            "ru": "св.г./с",
            "ja": "光年/s",
            "zh": "光年/秒",
            "ko": "광년/s"
        },
        "pc/h": {
            "en": "pc/h",
            "de": "pc/h",
            "es": "pc/h",
            "fr": "pc/h",
            "it": "pc/h",
            "nl": "pc/u",
            "pl": "pc/h",
            "pt": "pc/h",
            "ru": "пк/ч",
            "ja": "pc/h",
            "zh": "秒差距/小时",
            "ko": "pc/h"
        },
        "pc/s": {
            "en": "pc/s",
            "de": "pc/s",
            "es": "pc/s",
            "fr": "pc/s",
            "it": "pc/s",
            "nl": "pc/s",
            "pl": "pc/s",
            "pt": "pc/s",
            "ru": "пк/с",
            "ja": "pc/s",
            "zh": "秒差距/秒",
            "ko": "pc/s"
        },
        "c": {
            "en": "c",
            "de": "c",
            "es": "c",
            "fr": "c",
            "it": "c",
            "nl": "c",
            "pl": "c",
            "pt": "c",
            "ru": "c",
            "ja": "c",
            "zh": "c",
            "ko": "c"
        },
        "Mach": {
            "en": "Mach",
            "de": "Mach",
            "es": "Mach",
            "fr": "Mach",
            "it": "Mach",
            "nl": "Mach",
            "pl": "Mach",
            "pt": "Mach",
            "ru": "Мах",
            "ja": "マッハ",
            "zh": "马赫",
            "ko": "마하"
        },
        "ls/s": {
            "en": "ls/s",
            "de": "Ls/s",
            "es": "sl/s",
            "fr": "sl/s",
            "it": "sl/s",
            "nl": "ls/s",
            "pl": "ls/s",
            "pt": "sl/s",
            "ru": "св.с/с",
            "ja": "光秒/s",
            "zh": "光秒/秒",
            "ko": "광초/s"
        },
        "🌍/h": {
            "en": "Earth circumferences/h",
            "de": "Erdumfänge/h",
            "es": "Circunferencias terrestres/h",
            "fr": "Circonférences terrestres/h",
            "it": "Circonferenze terrestri/h",
            "nl": "Aardomtrekken/u",
            "pl": "Obwodów Ziemi/h",
            "pt": "Circunferências terrestres/h",
            "ru": "Окружностей Земли/ч",
            "ja": "地球周/h",
            "zh": "地球周长/小时",
            "ko": "지구둘레/h"
        },
        "🌙/h": {
            "en": "Moon distances/h",
            "de": "Mondentfernungen/h",
            "es": "Distancias lunares/h",
            "fr": "Distances lunaires/h",
            "it": "Distanze lunari/h",
            "nl": "Maanafstanden/u",
            "pl": "Odległości do Księżyca/h",
            "pt": "Distâncias lunares/h",
            "ru": "Лунных расстояний/ч",
            "ja": "月距離/h",
            "zh": "月球距离/小时",
            "ko": "달거리/h"
        }
    },

    # Labels for different speeds (multi-language)
    "speed_labels": {
        "earth_rotation": {
            "en": "Earth Rotation",
            "de": "Erdrotation",
            "es": "Rotación Terrestre",
            "fr": "Rotation Terrestre",
            "it": "Rotazione Terrestre",
            "nl": "Aardrotatie",
            "pl": "Rotacja Ziemi",
            "pt": "Rotação da Terra",
            "ru": "Вращение Земли",
            "ja": "地球の自転",
            "zh": "地球自转",
            "ko": "지구 자전"
        },
        "earth_orbit": {
            "en": "Earth Orbit",
            "de": "Erdumlaufbahn",
            "es": "Órbita Terrestre",
            "fr": "Orbite Terrestre",
            "it": "Orbita Terrestre",
            "nl": "Aardbaan",
            "pl": "Orbita Ziemi",
            "pt": "Órbita da Terra",
            "ru": "Орбита Земли",
            "ja": "地球の公転",
            "zh": "地球公转",
            "ko": "지구 공전"
        },
        "solar_system": {
            "en": "Solar System in Galaxy",
            "de": "Sonnensystem in Galaxie",
            "es": "Sistema Solar en Galaxia",
            "fr": "Système Solaire dans Galaxie",
            "it": "Sistema Solare nella Galassia",
            "nl": "Zonnestelsel in Melkweg",
            "pl": "Układ Słoneczny w Galaktyce",
            "pt": "Sistema Solar na Galáxia",
            "ru": "Солнечная Система в Галактике",
            "ja": "銀河系内の太陽系",
            "zh": "银河系中的太阳系",
            "ko": "은하 내 태양계"
        },
        "galaxy": {
            "en": "Milky Way in Universe",
            "de": "Milchstraße im Universum",
            "es": "Vía Láctea en Universo",
            "fr": "Voie Lactée dans l'Univers",
            "it": "Via Lattea nell'Universo",
            "nl": "Melkweg in Universum",
            "pl": "Droga Mleczna we Wszechświecie",
            "pt": "Via Láctea no Universo",
            "ru": "Млечный Путь во Вселенной",
            "ja": "宇宙内の天の川銀河",
            "zh": "宇宙中的银河系",
            "ko": "우주 내 은하수"
        },
        "sun_rotation": {
            "en": "Sun Rotation",
            "de": "Sonnenrotation",
            "es": "Rotación del Sol",
            "fr": "Rotation du Soleil",
            "it": "Rotazione del Sole",
            "nl": "Zonrotatie",
            "pl": "Rotacja Słońca",
            "pt": "Rotação do Sol",
            "ru": "Вращение Солнца",
            "ja": "太陽の自転",
            "zh": "太阳自转",
            "ko": "태양 자전"
        },
        "total": {
            "en": "Total Speed Through Space",
            "de": "Gesamtgeschwindigkeit durch den Weltraum",
            "es": "Velocidad Total a Través del Espacio",
            "fr": "Vitesse Totale à Travers l'Espace",
            "it": "Velocità Totale Attraverso lo Spazio",
            "nl": "Totale Snelheid Door de Ruimte",
            "pl": "Całkowita Prędkość Przez Kosmos",
            "pt": "Velocidade Total Através do Espaço",
            "ru": "Общая Скорость Через Космос",
            "ja": "宇宙を通る総速度",
            "zh": "穿越太空的总速度",
            "ko": "우주를 통과하는 총 속도"
        },
        "galactic_age": {
            "en": "Sun's Galactic Age",
            "de": "Galaktisches Alter der Sonne",
            "es": "Edad Galáctica del Sol",
            "fr": "Âge Galactique du Soleil",
            "it": "Età Galattica del Sole",
            "nl": "Galactische Leeftijd van de Zon",
            "pl": "Wiek Galaktyczny Słońca",
            "pt": "Idade Galáctica do Sol",
            "ru": "Галактический Возраст Солнца",
            "ja": "太陽の銀河年齢",
            "zh": "太阳的银河年龄",
            "ko": "태양의 은하 나이"
        },
        "galactic_year_progress": {
            "en": "Current Galactic Year Progress",
            "de": "Fortschritt im aktuellen galaktischen Jahr",
            "es": "Progreso del Año Galáctico Actual",
            "fr": "Progression de l'Année Galactique Actuelle",
            "it": "Progresso dell'Anno Galattico Attuale",
            "nl": "Voortgang Huidig Galactisch Jaar",
            "pl": "Postęp Bieżącego Roku Galaktycznego",
            "pt": "Progresso do Ano Galáctico Atual",
            "ru": "Прогресс Текущего Галактического Года",
            "ja": "現在の銀河年の進捗",
            "zh": "当前银河年进度",
            "ko": "현재 은하년 진행률"
        },
        "next_galactic_new_year": {
            "en": "Time Until Next Galactic New Year",
            "de": "Zeit bis zum nächsten galaktischen Neujahr",
            "es": "Tiempo Hasta el Próximo Año Nuevo Galáctico",
            "fr": "Temps Jusqu'au Prochain Nouvel An Galactique",
            "it": "Tempo Fino al Prossimo Capodanno Galattico",
            "nl": "Tijd Tot Volgend Galactisch Nieuwjaar",
            "pl": "Czas do Następnego Galaktycznego Nowego Roku",
            "pt": "Tempo Até o Próximo Ano Novo Galáctico",
            "ru": "Время до Следующего Галактического Нового Года",
            "ja": "次の銀河新年までの時間",
            "zh": "距离下一个银河新年的时间",
            "ko": "다음 은하 새해까지의 시간"
        },
        "galactic_years_unit": {
            "en": "galactic years",
            "de": "galaktische Jahre",
            "es": "años galácticos",
            "fr": "années galactiques",
            "it": "anni galattici",
            "nl": "galactische jaren",
            "pl": "lat galaktycznych",
            "pt": "anos galácticos",
            "ru": "галактических лет",
            "ja": "銀河年",
            "zh": "银河年",
            "ko": "은하년"
        },
        "million_years": {
            "en": "million years",
            "de": "Millionen Jahre",
            "es": "millones de años",
            "fr": "millions d'années",
            "it": "milioni di anni",
            "nl": "miljoen jaar",
            "pl": "milionów lat",
            "pt": "milhões de anos",
            "ru": "миллионов лет",
            "ja": "百万年",
            "zh": "百万年",
            "ko": "백만년"
        }
    },

    # Fun facts (multi-language)
    "fun_facts": {
        "en": [
            "Even sitting still, you're hurtling through space faster than any spacecraft!",
            "You travel about 2.6 million km every day just from Earth's orbit!",
            "In the time it takes to read this, you've moved about 500 km through the galaxy!",
            "One galactic year (orbit around Milky Way) takes about 225 million Earth years!",
            "The fastest human-made object (Parker Solar Probe) is still slower than our galaxy moves!",
            "At galaxy speed, you could travel from Earth to the Moon in about 10 minutes!",
            "You're moving at about 0.2% the speed of light right now!",
            "The Sun is about 20 galactic years old - it has orbited the Milky Way ~20 times!",
            "When the Sun was born, dinosaurs wouldn't exist for another 16 galactic years!",
            "Humans have existed for only 0.001 galactic years - a cosmic eyeblink!"
        ],
        "de": [
            "Selbst im Stillstand rasen Sie schneller durch den Weltraum als jedes Raumschiff!",
            "Sie legen jeden Tag etwa 2,6 Millionen km allein durch die Erdumlaufbahn zurück!",
            "Während Sie dies lesen, haben Sie sich etwa 500 km durch die Galaxie bewegt!",
            "Ein galaktisches Jahr (Umlauf um die Milchstraße) dauert etwa 225 Millionen Erdenjahre!",
            "Das schnellste von Menschen geschaffene Objekt (Parker Solar Probe) ist immer noch langsamer als unsere Galaxie!",
            "Mit Galaxiegeschwindigkeit könnten Sie in etwa 10 Minuten von der Erde zum Mond reisen!",
            "Sie bewegen sich gerade mit etwa 0,2% der Lichtgeschwindigkeit!",
            "Die Sonne ist etwa 20 galaktische Jahre alt - sie hat die Milchstraße ~20 Mal umkreist!",
            "Als die Sonne geboren wurde, würden Dinosaurier erst in 16 galaktischen Jahren existieren!",
            "Menschen existieren erst seit 0,001 galaktischen Jahren - ein kosmischer Wimpernschlag!"
        ],
        "es": [
            "¡Incluso sentado quieto, estás atravesando el espacio más rápido que cualquier nave espacial!",
            "¡Viajas unos 2,6 millones de km cada día solo por la órbita terrestre!",
            "¡En el tiempo que tardas en leer esto, te has movido unos 500 km a través de la galaxia!",
            "¡Un año galáctico (órbita alrededor de la Vía Láctea) toma unos 225 millones de años terrestres!",
            "¡El objeto más rápido hecho por humanos (Parker Solar Probe) sigue siendo más lento que nuestra galaxia!",
            "¡A velocidad galáctica, podrías viajar de la Tierra a la Luna en unos 10 minutos!",
            "¡Te estás moviendo a aproximadamente 0,2% de la velocidad de la luz ahora mismo!",
            "¡El Sol tiene unos 20 años galácticos - ha orbitado la Vía Láctea ~20 veces!",
            "¡Cuando nació el Sol, los dinosaurios no existirían por otros 16 años galácticos!",
            "¡Los humanos han existido solo 0,001 años galácticos - un parpadeo cósmico!"
        ],
        "fr": [
            "Même assis immobile, vous traversez l'espace plus vite que n'importe quel vaisseau spatial !",
            "Vous parcourez environ 2,6 millions de km chaque jour rien que par l'orbite terrestre !",
            "Le temps de lire ceci, vous avez parcouru environ 500 km à travers la galaxie !",
            "Une année galactique (orbite autour de la Voie Lactée) prend environ 225 millions d'années terrestres !",
            "L'objet le plus rapide fait par l'homme (Parker Solar Probe) est encore plus lent que notre galaxie !",
            "À la vitesse galactique, vous pourriez voyager de la Terre à la Lune en environ 10 minutes !",
            "Vous vous déplacez à environ 0,2% de la vitesse de la lumière en ce moment !",
            "Le Soleil a environ 20 années galactiques - il a orbité la Voie Lactée ~20 fois !",
            "Quand le Soleil est né, les dinosaures n'existeraient pas avant 16 années galactiques !",
            "Les humains n'existent que depuis 0,001 années galactiques - un clin d'œil cosmique !"
        ],
        "it": [
            "Anche stando fermo, stai attraversando lo spazio più velocemente di qualsiasi astronave!",
            "Percorri circa 2,6 milioni di km ogni giorno solo dall'orbita terrestre!",
            "Nel tempo di leggere questo, ti sei mosso di circa 500 km attraverso la galassia!",
            "Un anno galattico (orbita intorno alla Via Lattea) dura circa 225 milioni di anni terrestri!",
            "L'oggetto più veloce fatto dall'uomo (Parker Solar Probe) è ancora più lento della nostra galassia!",
            "Alla velocità galattica, potresti viaggiare dalla Terra alla Luna in circa 10 minuti!",
            "Ti stai muovendo a circa lo 0,2% della velocità della luce in questo momento!",
            "Il Sole ha circa 20 anni galattici - ha orbitato la Via Lattea ~20 volte!",
            "Quando il Sole è nato, i dinosauri non sarebbero esistiti per altri 16 anni galattici!",
            "Gli umani esistono da solo 0,001 anni galattici - un battito di ciglia cosmico!"
        ],
        "nl": [
            "Zelfs stilzittend raas je sneller door de ruimte dan welk ruimteschip ook!",
            "Je reist elke dag ongeveer 2,6 miljoen km alleen door de baan van de Aarde!",
            "In de tijd die je nodig hebt om dit te lezen, heb je ongeveer 500 km door de melkweg afgelegd!",
            "Een galactisch jaar (baan rond de Melkweg) duurt ongeveer 225 miljoen Aardse jaren!",
            "Het snelste door mensen gemaakte object (Parker Solar Probe) is nog steeds langzamer dan onze melkweg!",
            "Met melkwegsnelheid zou je in ongeveer 10 minuten van de Aarde naar de Maan kunnen reizen!",
            "Je beweegt nu met ongeveer 0,2% van de lichtsnelheid!",
            "De Zon is ongeveer 20 galactische jaren oud - ze heeft de Melkweg ~20 keer omcirkeld!",
            "Toen de Zon werd geboren, zouden dinosaurussen pas over 16 galactische jaren bestaan!",
            "Mensen bestaan pas 0,001 galactische jaren - een kosmische oogwenk!"
        ],
        "pl": [
            "Nawet siedząc nieruchomo, pędzisz przez kosmos szybciej niż jakikolwiek statek kosmiczny!",
            "Podróżujesz około 2,6 miliona km dziennie tylko z orbity Ziemi!",
            "W czasie potrzebnym na przeczytanie tego, przesunąłeś się o około 500 km przez galaktykę!",
            "Jeden rok galaktyczny (orbita wokół Drogi Mlecznej) trwa około 225 milionów lat ziemskich!",
            "Najszybszy obiekt stworzony przez człowieka (Parker Solar Probe) jest wciąż wolniejszy niż nasza galaktyka!",
            "Z prędkością galaktyczną mógłbyś podróżować z Ziemi na Księżyc w około 10 minut!",
            "Poruszasz się teraz z prędkością około 0,2% prędkości światła!",
            "Słońce ma około 20 lat galaktycznych - okrążyło Drogę Mleczną ~20 razy!",
            "Kiedy Słońce się narodziło, dinozaury nie istniałyby jeszcze przez 16 lat galaktycznych!",
            "Ludzie istnieją tylko od 0,001 lat galaktycznych - kosmiczne mrugnięcie okiem!"
        ],
        "pt": [
            "Mesmo parado, você está atravessando o espaço mais rápido que qualquer nave espacial!",
            "Você viaja cerca de 2,6 milhões de km todos os dias apenas pela órbita da Terra!",
            "No tempo que leva para ler isso, você se moveu cerca de 500 km pela galáxia!",
            "Um ano galáctico (órbita ao redor da Via Láctea) leva cerca de 225 milhões de anos terrestres!",
            "O objeto mais rápido feito pelo homem (Parker Solar Probe) ainda é mais lento que nossa galáxia!",
            "Na velocidade galáctica, você poderia viajar da Terra à Lua em cerca de 10 minutos!",
            "Você está se movendo a cerca de 0,2% da velocidade da luz agora mesmo!",
            "O Sol tem cerca de 20 anos galácticos - orbitou a Via Láctea ~20 vezes!",
            "Quando o Sol nasceu, os dinossauros não existiriam por mais 16 anos galácticos!",
            "Os humanos existem há apenas 0,001 anos galácticos - uma piscada cósmica!"
        ],
        "ru": [
            "Даже сидя на месте, вы мчитесь через космос быстрее любого космического корабля!",
            "Вы проходите около 2,6 миллиона км каждый день только от орбиты Земли!",
            "За время чтения этого вы переместились примерно на 500 км через галактику!",
            "Один галактический год (орбита вокруг Млечного Пути) занимает около 225 миллионов земных лет!",
            "Самый быстрый объект, созданный человеком (Parker Solar Probe), все еще медленнее нашей галактики!",
            "На галактической скорости вы могли бы добраться от Земли до Луны примерно за 10 минут!",
            "Сейчас вы движетесь со скоростью около 0,2% скорости света!",
            "Солнцу около 20 галактических лет - оно обошло Млечный Путь ~20 раз!",
            "Когда Солнце родилось, динозавры не существовали бы еще 16 галактических лет!",
            "Люди существуют всего 0,001 галактических лет - космическое мгновение!"
        ],
        "ja": [
            "じっと座っていても、どの宇宙船よりも速く宇宙を駆け抜けています！",
            "地球の公転だけで毎日約260万kmを移動しています！",
            "これを読む間に、銀河を約500km移動しました！",
            "銀河年（天の川周回）は約2億2500万年かかります！",
            "人類最速の物体（パーカーソーラープローブ）でも、銀河の動きより遅い！",
            "銀河の速度なら、地球から月まで約10分で行けます！",
            "今、あなたは光速の約0.2%で移動しています！",
            "太陽は約20銀河年齢 - 天の川を約20回周回しました！",
            "太陽が生まれた時、恐竜はまだ16銀河年後まで存在しませんでした！",
            "人類は0.001銀河年しか存在していません - 宇宙のまばたき！"
        ],
        "zh": [
            "即使坐着不动，你穿越太空的速度也比任何宇宙飞船都快！",
            "仅地球公转，你每天就移动约260万公里！",
            "阅读这段话的时间里，你已经在银河系中移动了约500公里！",
            "一个银河年（绕银河系一圈）大约需要2.25亿地球年！",
            "人类制造的最快物体（帕克太阳探测器）仍比我们银河系的移动速度慢！",
            "以银河速度，你可以在大约10分钟内从地球到达月球！",
            "你现在正以光速的约0.2%移动！",
            "太阳大约有20个银河年 - 它已经绕银河系运行了约20次！",
            "太阳诞生时，恐龙还要再过16个银河年才会存在！",
            "人类只存在了0.001个银河年 - 宇宙的一瞬间！"
        ],
        "ko": [
            "가만히 앉아 있어도 어떤 우주선보다 빠르게 우주를 질주하고 있습니다!",
            "지구 공전만으로 매일 약 260만 km를 이동합니다!",
            "이 글을 읽는 동안 은하계를 약 500km 이동했습니다!",
            "은하년(은하수 공전)은 약 2억 2,500만 지구년이 걸립니다!",
            "인류가 만든 가장 빠른 물체(파커 태양 탐사선)도 우리 은하의 속도보다 느립니다!",
            "은하 속도로 지구에서 달까지 약 10분 만에 갈 수 있습니다!",
            "지금 당신은 빛의 속도의 약 0.2%로 움직이고 있습니다!",
            "태양은 약 20 은하년입니다 - 은하수를 약 20번 공전했습니다!",
            "태양이 태어났을 때, 공룡은 16 은하년 후에야 존재했습니다!",
            "인류는 0.001 은하년밖에 존재하지 않았습니다 - 우주적 눈 깜짝할 사이!"
        ]
    },

    # Reference
    "reference_url": "https://en.wikipedia.org/wiki/Earth%27s_rotation"
}

# ============================================
# SENSOR CLASS
# ============================================

class CosmicSpeedometerSensor(AlternativeTimeSensorBase):
    """Sensor showing cosmic speeds - Earth rotation, orbit, solar system, and galaxy speeds."""

    UPDATE_INTERVAL = UPDATE_INTERVAL

    def __init__(self, base_name: str, hass: HomeAssistant) -> None:
        """Initialize the Cosmic Speedometer sensor."""
        super().__init__(base_name, hass)

        # Store CALENDAR_INFO as instance variable for _translate method
        self._calendar_info = CALENDAR_INFO

        # Get user's language
        self._user_language = "en"
        if hass and hasattr(hass, "config"):
            self._user_language = getattr(hass.config, "language", "en") or "en"

        # Get translated name
        calendar_name = self._translate("name", "Cosmic Speedometer")

        # Set sensor attributes
        self._attr_name = f"{base_name} {calendar_name}"
        self._attr_unique_id = f"{base_name}_cosmic_speedometer"
        self._attr_icon = CALENDAR_INFO.get("icon", "mdi:speedometer")

        # Configuration options with defaults
        config_defaults = CALENDAR_INFO.get("config_options", {})
        self._speed_unit = config_defaults.get("speed_unit", {}).get("default", "km/h")
        self._use_observer_location = config_defaults.get("use_observer_location", {}).get("default", True)
        self._show_earth_rotation = config_defaults.get("show_earth_rotation", {}).get("default", True)
        self._show_earth_orbit = config_defaults.get("show_earth_orbit", {}).get("default", True)
        self._show_solar_system_speed = config_defaults.get("show_solar_system_speed", {}).get("default", True)
        self._show_galaxy_speed = config_defaults.get("show_galaxy_speed", {}).get("default", True)
        self._show_sun_rotation = config_defaults.get("show_sun_rotation", {}).get("default", False)
        self._show_total_speed = config_defaults.get("show_total_speed", {}).get("default", True)
        self._show_fun_comparisons = config_defaults.get("show_fun_comparisons", {}).get("default", True)
        self._display_mode = config_defaults.get("display_mode", {}).get("default", "total")
        self._show_galactic_calendar = config_defaults.get("show_galactic_calendar", {}).get("default", True)

        # Observer location (default to equator if not set)
        self._observer_latitude = 0.0
        self._observer_longitude = 0.0
        if hass and hasattr(hass, "config"):
            self._observer_latitude = getattr(hass.config, "latitude", 0.0)
            self._observer_longitude = getattr(hass.config, "longitude", 0.0)

        # Speed data
        self._speed_data = CALENDAR_INFO.get("speed_data", {})

        # State
        self._state = "Initializing..."
        self._speeds = {}

        # Flag to track if options have been loaded
        self._options_loaded = False
        self._first_update = True

        _LOGGER.debug(f"Initialized Cosmic Speedometer sensor: {self._attr_name}")

    def _lang(self) -> str:
        """Get user's language code."""
        try:
            lang = (self._user_language or "en").lower()
            if "-" in lang:
                lang = lang.split("-")[0]
            elif "_" in lang:
                lang = lang.split("_")[0]
            return lang
        except Exception:
            return "en"

    def _translate(self, key: str, default: Optional[str] = None) -> str:
        """Translate a key from CALENDAR_INFO."""
        try:
            section = CALENDAR_INFO.get(key)
            if isinstance(section, dict):
                return section.get(self._lang(), section.get("en", default or key))
        except Exception:
            pass
        return default or key

    def _get_label(self, key: str) -> str:
        """Get a localized label."""
        labels = CALENDAR_INFO.get("speed_labels", {}).get(key, {})
        if isinstance(labels, dict):
            return labels.get(self._lang(), labels.get("en", key))
        return key

    def _get_unit_name(self, unit: str) -> str:
        """Get the localized unit name."""
        unit_names = CALENDAR_INFO.get("unit_names", {}).get(unit, {})
        if isinstance(unit_names, dict):
            return unit_names.get(self._lang(), unit_names.get("en", unit))
        return unit

    def _get_invalid_unit_message(self) -> str:
        """Get the localized 'invalid unit' message."""
        messages = CALENDAR_INFO.get("invalid_unit_message", {})
        if isinstance(messages, dict):
            return messages.get(self._lang(), messages.get("en", "Not a valid unit of measurement"))
        return "Not a valid unit of measurement"

    def _load_options(self) -> None:
        """Load plugin options after IDs are set."""
        if self._options_loaded:
            return

        # Get plugin options from config entry
        plugin_options = self.get_plugin_options()

        if plugin_options:
            _LOGGER.debug(f"Loading Cosmic Speedometer options: {plugin_options}")

            self._speed_unit = plugin_options.get("speed_unit", self._speed_unit)
            self._use_observer_location = plugin_options.get("use_observer_location", self._use_observer_location)
            self._show_earth_rotation = plugin_options.get("show_earth_rotation", self._show_earth_rotation)
            self._show_earth_orbit = plugin_options.get("show_earth_orbit", self._show_earth_orbit)
            self._show_solar_system_speed = plugin_options.get("show_solar_system_speed", self._show_solar_system_speed)
            self._show_galaxy_speed = plugin_options.get("show_galaxy_speed", self._show_galaxy_speed)
            self._show_sun_rotation = plugin_options.get("show_sun_rotation", self._show_sun_rotation)
            self._show_total_speed = plugin_options.get("show_total_speed", self._show_total_speed)
            self._show_fun_comparisons = plugin_options.get("show_fun_comparisons", self._show_fun_comparisons)
            self._display_mode = plugin_options.get("display_mode", self._display_mode)
            self._show_galactic_calendar = plugin_options.get("show_galactic_calendar", self._show_galactic_calendar)

        self._options_loaded = True

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added to hass."""
        await super().async_added_to_hass()
        self._load_options()
        self.update()

    def set_options(
        self,
        speed_unit: Optional[str] = None,
        use_observer_location: Optional[bool] = None,
        show_earth_rotation: Optional[bool] = None,
        show_earth_orbit: Optional[bool] = None,
        show_solar_system_speed: Optional[bool] = None,
        show_galaxy_speed: Optional[bool] = None,
        show_sun_rotation: Optional[bool] = None,
        show_total_speed: Optional[bool] = None,
        show_fun_comparisons: Optional[bool] = None,
        display_mode: Optional[str] = None,
        show_galactic_calendar: Optional[bool] = None
    ) -> None:
        """Set sensor options programmatically."""
        if speed_unit is not None:
            self._speed_unit = speed_unit
        if use_observer_location is not None:
            self._use_observer_location = use_observer_location
        if show_earth_rotation is not None:
            self._show_earth_rotation = show_earth_rotation
        if show_earth_orbit is not None:
            self._show_earth_orbit = show_earth_orbit
        if show_solar_system_speed is not None:
            self._show_solar_system_speed = show_solar_system_speed
        if show_galaxy_speed is not None:
            self._show_galaxy_speed = show_galaxy_speed
        if show_sun_rotation is not None:
            self._show_sun_rotation = show_sun_rotation
        if show_total_speed is not None:
            self._show_total_speed = show_total_speed
        if show_fun_comparisons is not None:
            self._show_fun_comparisons = show_fun_comparisons
        if display_mode is not None:
            self._display_mode = display_mode
        if show_galactic_calendar is not None:
            self._show_galactic_calendar = show_galactic_calendar

    def _is_valid_unit(self, unit: str) -> bool:
        """Check if a unit is valid."""
        valid_units = [
            "km/h", "km/s", "m/s",           # Metrisch
            "c", "Mach",                      # Relativ
            "AU/h", "AU/s",                   # Astronomische Einheiten
            "ly/h", "ly/s",                   # Lichtjahre
            "pc/h", "pc/s",                   # Parsec
            "ls/s",                           # Lichtsekunden pro Sekunde
            "🌍/h", "🌙/h"                    # Anschaulich
        ]
        return unit in valid_units

    def _convert_speed(self, speed_kmh: float) -> Tuple[float, str, bool]:
        """Convert speed from km/h to the configured unit.

        Returns:
            tuple: (converted_value, unit_string, is_valid)
        """
        unit = self._speed_unit

        # Check for invalid units (like mph)
        if not self._is_valid_unit(unit):
            return 0.0, self._get_invalid_unit_message(), False

        # Get localized unit name
        unit_display = self._get_unit_name(unit)

        # Metrisch
        if unit == "km/h":
            return speed_kmh, unit_display, True
        elif unit == "km/s":
            return speed_kmh / 3600, unit_display, True
        elif unit == "m/s":
            return speed_kmh * 1000 / 3600, unit_display, True

        # Relativ
        elif unit == "c":
            return speed_kmh / SPEED_OF_LIGHT_KMH, unit_display, True
        elif unit == "Mach":
            return speed_kmh / SPEED_OF_SOUND_KMH, unit_display, True

        # Astronomische Einheiten
        elif unit == "AU/h":
            return speed_kmh / AU_IN_KM, unit_display, True
        elif unit == "AU/s":
            return speed_kmh / 3600 / AU_IN_KM, unit_display, True

        # Lichtjahre
        elif unit == "ly/h":
            return speed_kmh / LIGHTYEAR_IN_KM, unit_display, True
        elif unit == "ly/s":
            return speed_kmh / 3600 / LIGHTYEAR_IN_KM, unit_display, True

        # Parsec
        elif unit == "pc/h":
            return speed_kmh / PARSEC_IN_KM, unit_display, True
        elif unit == "pc/s":
            return speed_kmh / 3600 / PARSEC_IN_KM, unit_display, True

        # Lichtsekunden pro Sekunde (= Bruchteil von c)
        elif unit == "ls/s":
            return speed_kmh / 3600 / LIGHTSECOND_IN_KM, unit_display, True

        # Anschaulich
        elif unit == "🌍/h":
            return speed_kmh / EARTH_CIRCUMFERENCE_KM, unit_display, True
        elif unit == "🌙/h":
            return speed_kmh / MOON_DISTANCE_KM, unit_display, True

        else:
            # Fallback to km/h for any unexpected unit
            return speed_kmh, "km/h", True

    def _format_speed(self, speed_kmh: float, include_unit: bool = True) -> str:
        """Format a speed value with appropriate precision."""
        value, unit, is_valid = self._convert_speed(speed_kmh)

        # If unit is invalid, return the error message
        if not is_valid:
            return f"⚠️ {unit}"

        # Determine precision based on magnitude - always use readable numbers, fully written out
        # Use dots as thousand separators (European format, not imperial commas!)
        if abs(value) >= 1000:
            # Large values: full number with thousand separators (dots), no decimals
            formatted = f"{value:,.0f}".replace(",", ".")
        elif abs(value) >= 100:
            formatted = f"{value:.1f}".replace(".", ",")  # Decimal comma
        elif abs(value) >= 1:
            formatted = f"{value:.2f}".replace(".", ",")  # Decimal comma
        elif abs(value) >= 0.01:
            formatted = f"{value:.4f}".replace(".", ",")
        elif abs(value) >= 0.001:
            formatted = f"{value:.5f}".replace(".", ",")
        elif abs(value) >= 0.0001:
            formatted = f"{value:.6f}".replace(".", ",")
        elif abs(value) >= 0.00001:
            formatted = f"{value:.7f}".replace(".", ",")
        elif abs(value) >= 0.000001:
            formatted = f"{value:.8f}".replace(".", ",")
        elif abs(value) >= 0.0000001:
            formatted = f"{value:.9f}".replace(".", ",")
        elif abs(value) >= 0.00000001:
            formatted = f"{value:.10f}".replace(".", ",")
        elif abs(value) >= 0.000000001:
            formatted = f"{value:.11f}".replace(".", ",")
        elif abs(value) >= 0.0000000001:
            formatted = f"{value:.12f}".replace(".", ",")
        elif abs(value) >= 0.00000000001:
            formatted = f"{value:.13f}".replace(".", ",")
        elif abs(value) >= 0.000000000001:
            formatted = f"{value:.14f}".replace(".", ",")
        elif abs(value) >= 0.0000000000001:
            formatted = f"{value:.15f}".replace(".", ",")
        elif abs(value) == 0:
            formatted = "0"
        else:
            # For extremely small values, show with maximum precision
            formatted = f"{value:.18f}".rstrip('0').rstrip('.').replace(".", ",")

        if include_unit:
            return f"{formatted} {unit}"
        return formatted

    def _calculate_earth_rotation_speed(self) -> float:
        """Calculate Earth rotation speed at the observer's latitude."""
        if self._use_observer_location:
            latitude = self._observer_latitude
        else:
            latitude = 0.0  # Equator

        # Earth rotation speed varies with latitude: v = v_equator * cos(latitude)
        equator_speed = self._speed_data.get("earth_equator_rotation_kmh", 1674.4)
        latitude_rad = math.radians(abs(latitude))
        return equator_speed * math.cos(latitude_rad)

    def _get_fun_comparison(self, speed_kmh: float) -> Dict[str, Any]:
        """Get a fun comparison for a given speed."""
        comparisons = self._speed_data.get("comparisons", {})

        best_match = None
        best_ratio = float("inf")

        for name, data in comparisons.items():
            comp_speed = data.get("speed_kmh", 1)
            ratio = speed_kmh / comp_speed

            # Find the closest match that's not too far off
            if ratio >= 0.5:  # Speed is at least half of comparison
                if best_match is None or ratio < best_ratio:
                    best_match = name
                    best_ratio = ratio

        if best_match:
            data = comparisons[best_match]
            return {
                "name": best_match.replace("_", " ").title(),
                "emoji": data.get("emoji", "🚀"),
                "times_faster": round(speed_kmh / data.get("speed_kmh", 1), 1)
            }

        return {"name": "walking", "emoji": "🚶", "times_faster": round(speed_kmh / 5, 1)}

    def _calculate_speeds(self) -> Dict[str, Any]:
        """Calculate all cosmic speeds."""
        speeds = {}

        # Check if we have a valid unit
        is_valid_unit = self._is_valid_unit(self._speed_unit)

        # Earth rotation speed (varies by latitude)
        earth_rotation = self._calculate_earth_rotation_speed()
        earth_rotation_uncertainty = self._speed_data.get("earth_equator_rotation_uncertainty", 0.1)
        speeds["earth_rotation"] = {
            "speed_kmh": earth_rotation,
            "formatted": self._format_speed(earth_rotation),
            "label": self._get_label("earth_rotation"),
            "latitude_factor": f"at {abs(self._observer_latitude):.1f}°{'N' if self._observer_latitude >= 0 else 'S'}" if self._use_observer_location else "at equator",
            "emoji": "🌍",
            "uncertainty_percent": earth_rotation_uncertainty,
            "valid": is_valid_unit
        }

        # Earth orbital speed (relatively constant)
        earth_orbit = self._speed_data.get("earth_orbital_speed_kmh", 107208.0)
        earth_orbit_uncertainty = self._speed_data.get("earth_orbital_uncertainty", 0.1)
        speeds["earth_orbit"] = {
            "speed_kmh": earth_orbit,
            "formatted": self._format_speed(earth_orbit),
            "label": self._get_label("earth_orbit"),
            "emoji": "☀️",
            "uncertainty_percent": earth_orbit_uncertainty,
            "valid": is_valid_unit
        }

        # Solar system speed in galaxy
        solar_system = self._speed_data.get("solar_system_galactic_speed_kmh", 828000.0)
        solar_system_uncertainty = self._speed_data.get("solar_system_galactic_uncertainty", 10.0)
        speeds["solar_system"] = {
            "speed_kmh": solar_system,
            "formatted": self._format_speed(solar_system),
            "label": self._get_label("solar_system"),
            "emoji": "🌌",
            "uncertainty_percent": solar_system_uncertainty,
            "valid": is_valid_unit
        }

        # Galaxy speed in universe
        galaxy = self._speed_data.get("galaxy_speed_kmh", 2160000.0)
        galaxy_uncertainty = self._speed_data.get("galaxy_speed_uncertainty", 15.0)
        speeds["galaxy"] = {
            "speed_kmh": galaxy,
            "formatted": self._format_speed(galaxy),
            "label": self._get_label("galaxy"),
            "destination": "Great Attractor",
            "emoji": "🌀",
            "uncertainty_percent": galaxy_uncertainty,
            "valid": is_valid_unit
        }

        # Sun rotation (bonus)
        sun_rotation = self._speed_data.get("sun_equator_rotation_kmh", 7189.0)
        sun_rotation_uncertainty = self._speed_data.get("sun_equator_rotation_uncertainty", 1.0)
        speeds["sun_rotation"] = {
            "speed_kmh": sun_rotation,
            "formatted": self._format_speed(sun_rotation),
            "label": self._get_label("sun_rotation"),
            "emoji": "☀️",
            "uncertainty_percent": sun_rotation_uncertainty,
            "valid": is_valid_unit
        }

        # Calculate approximate total speed through space
        # Uncertainty for total is dominated by the largest uncertainties (galaxy speed)
        total_approximate = galaxy  # The largest component dominates
        total_uncertainty = galaxy_uncertainty  # Dominated by galaxy measurement uncertainty
        speeds["total"] = {
            "speed_kmh": total_approximate,
            "formatted": self._format_speed(total_approximate),
            "label": self._get_label("total"),
            "note": "Approximate (velocities are in different directions)",
            "emoji": "🚀",
            "uncertainty_percent": total_uncertainty,
            "valid": is_valid_unit
        }

        # Add fun comparisons (only if valid unit)
        if self._show_fun_comparisons and is_valid_unit:
            for key, speed_info in speeds.items():
                speed_info["comparison"] = self._get_fun_comparison(speed_info["speed_kmh"])

        return speeds

    def _get_random_fun_fact(self) -> str:
        """Get a random fun fact in the user's language."""
        import random
        facts = CALENDAR_INFO.get("fun_facts", {}).get(self._lang(),
                CALENDAR_INFO.get("fun_facts", {}).get("en", []))
        if facts:
            return random.choice(facts)
        return ""

    def _calculate_galactic_calendar(self) -> Dict[str, Any]:
        """Calculate galactic calendar data - Sun's galactic age and current orbit progress."""
        galactic_year = self._speed_data.get("galactic_year_earth_years", GALACTIC_YEAR_EARTH_YEARS)
        galactic_year_uncertainty = self._speed_data.get("galactic_year_uncertainty", GALACTIC_YEAR_UNCERTAINTY)
        sun_age = self._speed_data.get("sun_age_earth_years", SUN_AGE_EARTH_YEARS)
        sun_age_uncertainty = self._speed_data.get("sun_age_uncertainty", SUN_AGE_UNCERTAINTY)

        # Calculate Sun's galactic age (how many complete orbits)
        sun_galactic_age = sun_age / galactic_year

        # Calculate progress in current orbit
        current_orbit_progress = (sun_galactic_age % 1) * 100  # Percentage

        # Calculate time remaining until next galactic new year
        remaining_progress = 100 - current_orbit_progress
        remaining_earth_years = (remaining_progress / 100) * galactic_year
        remaining_million_years = remaining_earth_years / 1000000

        # Get localized labels
        galactic_years_unit = self._get_label("galactic_years_unit")
        million_years_unit = self._get_label("million_years")

        return {
            "sun_galactic_age": sun_galactic_age,
            "sun_galactic_age_formatted": f"{sun_galactic_age:.1f} {galactic_years_unit} (±{galactic_year_uncertainty}%)",
            "sun_galactic_orbits_complete": int(sun_galactic_age),
            "current_orbit_progress_percent": current_orbit_progress,
            "current_orbit_progress_formatted": f"{current_orbit_progress:.1f}%",
            "remaining_earth_years": remaining_earth_years,
            "remaining_million_years": remaining_million_years,
            "next_galactic_new_year_formatted": f"~{remaining_million_years:.0f} {million_years_unit}",
            "galactic_year_length_formatted": f"{galactic_year / 1000000:.0f} {million_years_unit}",
            "uncertainties": {
                "galactic_year": galactic_year_uncertainty,
                "sun_age": sun_age_uncertainty
            }
        }

    @property
    def state(self) -> str:
        """Return the state of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes."""
        attrs = super().extra_state_attributes

        # Check if unit is valid
        is_valid_unit = self._is_valid_unit(self._speed_unit)

        # Add description
        attrs["description"] = self._translate("description")

        # Add unit validity status
        if not is_valid_unit:
            attrs["unit_error"] = self._get_invalid_unit_message()
            attrs["selected_unit"] = self._speed_unit
            attrs["valid_units"] = [
                "km/h", "km/s", "m/s", "c", "Mach",
                "AU/h", "AU/s", "ly/h", "ly/s", "pc/h", "pc/s",
                "ls/s", "🌍/h", "🌙/h"
            ]

        # Add calculated speeds with uncertainty
        if self._show_earth_rotation:
            earth_rot = self._speeds.get("earth_rotation", {})
            uncertainty = earth_rot.get("uncertainty_percent", 0)
            attrs["earth_rotation_speed"] = f"{earth_rot.get('formatted', 'N/A')} (±{uncertainty}%)"
            if self._use_observer_location:
                attrs["earth_rotation_latitude"] = earth_rot.get("latitude_factor", "")

        if self._show_earth_orbit:
            earth_orb = self._speeds.get("earth_orbit", {})
            uncertainty = earth_orb.get("uncertainty_percent", 0)
            attrs["earth_orbital_speed"] = f"{earth_orb.get('formatted', 'N/A')} (±{uncertainty}%)"

        if self._show_solar_system_speed:
            solar_sys = self._speeds.get("solar_system", {})
            uncertainty = solar_sys.get("uncertainty_percent", 0)
            attrs["solar_system_galactic_speed"] = f"{solar_sys.get('formatted', 'N/A')} (±{uncertainty}%)"

        if self._show_galaxy_speed:
            galaxy = self._speeds.get("galaxy", {})
            uncertainty = galaxy.get("uncertainty_percent", 0)
            attrs["milky_way_cosmic_speed"] = f"{galaxy.get('formatted', 'N/A')} (±{uncertainty}%)"
            attrs["destination"] = "Great Attractor"

        if self._show_sun_rotation:
            sun_rot = self._speeds.get("sun_rotation", {})
            uncertainty = sun_rot.get("uncertainty_percent", 0)
            attrs["sun_rotation_speed"] = f"{sun_rot.get('formatted', 'N/A')} (±{uncertainty}%)"

        if self._show_total_speed:
            total = self._speeds.get("total", {})
            uncertainty = total.get("uncertainty_percent", 0)
            attrs["total_cosmic_speed"] = f"{total.get('formatted', 'N/A')} (±{uncertainty}%)"

        # Add fun comparisons (only if valid unit)
        if self._show_fun_comparisons and is_valid_unit:
            comparisons = {}
            for key, speed_info in self._speeds.items():
                if "comparison" in speed_info:
                    comp = speed_info["comparison"]
                    comparisons[key] = f"{comp['emoji']} {comp['times_faster']}x faster than a {comp['name']}"
            if comparisons:
                attrs["speed_comparisons"] = comparisons

        # Add a fun fact
        attrs["fun_fact"] = self._get_random_fun_fact()

        # Add galactic calendar data
        if self._show_galactic_calendar:
            galactic_calendar = self._calculate_galactic_calendar()
            attrs["galactic_calendar"] = {
                "sun_galactic_age": galactic_calendar["sun_galactic_age_formatted"],
                "orbits_completed": galactic_calendar["sun_galactic_orbits_complete"],
                "current_orbit_progress": galactic_calendar["current_orbit_progress_formatted"],
                "next_galactic_new_year": galactic_calendar["next_galactic_new_year_formatted"],
                "galactic_year_length": galactic_calendar["galactic_year_length_formatted"]
            }
            # Also add as individual attributes for easier access
            attrs["sun_galactic_age"] = galactic_calendar["sun_galactic_age_formatted"]
            attrs["galactic_orbits_completed"] = galactic_calendar["sun_galactic_orbits_complete"]
            attrs["current_galactic_year_progress"] = galactic_calendar["current_orbit_progress_formatted"]
            attrs["next_galactic_new_year_in"] = galactic_calendar["next_galactic_new_year_formatted"]

        # Add speed breakdown with emojis and uncertainty
        speed_breakdown = []
        if self._show_earth_rotation and "earth_rotation" in self._speeds:
            s = self._speeds["earth_rotation"]
            speed_breakdown.append(f"🌍 {s['label']}: {s['formatted']} (±{s.get('uncertainty_percent', 0)}%)")
        if self._show_earth_orbit and "earth_orbit" in self._speeds:
            s = self._speeds["earth_orbit"]
            speed_breakdown.append(f"☀️ {s['label']}: {s['formatted']} (±{s.get('uncertainty_percent', 0)}%)")
        if self._show_solar_system_speed and "solar_system" in self._speeds:
            s = self._speeds["solar_system"]
            speed_breakdown.append(f"🌌 {s['label']}: {s['formatted']} (±{s.get('uncertainty_percent', 0)}%)")
        if self._show_galaxy_speed and "galaxy" in self._speeds:
            s = self._speeds["galaxy"]
            speed_breakdown.append(f"🌀 {s['label']}: {s['formatted']} (±{s.get('uncertainty_percent', 0)}%)")
        if speed_breakdown:
            attrs["speed_breakdown"] = speed_breakdown

        # Add configuration info
        attrs["config"] = {
            "speed_unit": self._speed_unit,
            "unit_valid": is_valid_unit,
            "use_observer_location": self._use_observer_location,
            "observer_latitude": self._observer_latitude if self._use_observer_location else None,
            "display_mode": self._display_mode
        }

        # Add all raw speeds in km/h for automations (always in km/h regardless of display unit)
        attrs["raw_speeds_kmh"] = {
            key: info.get("speed_kmh", 0)
            for key, info in self._speeds.items()
        }

        # Add uncertainty percentages for all speeds
        attrs["uncertainties_percent"] = {
            key: info.get("uncertainty_percent", 0)
            for key, info in self._speeds.items()
        }

        return attrs

    def update(self) -> None:
        """Update the sensor."""
        # Update user language
        if self.hass and hasattr(self.hass, "config"):
            self._user_language = getattr(self.hass.config, "language", "en") or "en"

        # Load options if not yet loaded
        if not self._options_loaded:
            self._load_options()

        # Log on first update
        if self._first_update:
            options = self.get_plugin_options()
            if options:
                _LOGGER.info(f"Cosmic Speedometer options on first update: {options}")
            else:
                _LOGGER.debug("Cosmic Speedometer using defaults")
            self._first_update = False

        # Update observer location from Home Assistant config
        if self._use_observer_location and self.hass and hasattr(self.hass, "config"):
            self._observer_latitude = getattr(self.hass.config, "latitude", self._observer_latitude)
            self._observer_longitude = getattr(self.hass.config, "longitude", self._observer_longitude)

        # Calculate all speeds
        self._speeds = self._calculate_speeds()

        # Check if unit is valid
        is_valid_unit = self._is_valid_unit(self._speed_unit)

        # If unit is invalid, show error message as state
        if not is_valid_unit:
            self._state = f"⚠️ {self._get_invalid_unit_message()}"
            _LOGGER.debug(f"Updated Cosmic Speedometer with invalid unit: {self._speed_unit}")
            return

        # Set state based on display mode
        if self._display_mode == "all":
            # Show a summary
            parts = []
            if "earth_rotation" in self._speeds:
                parts.append(f"🌍{self._speeds['earth_rotation']['formatted']}")
            if "earth_orbit" in self._speeds:
                parts.append(f"☀️{self._speeds['earth_orbit']['formatted']}")
            if "solar_system" in self._speeds:
                parts.append(f"🌌{self._speeds['solar_system']['formatted']}")
            self._state = " | ".join(parts[:3]) if parts else "Active"
        elif self._display_mode in self._speeds:
            speed_info = self._speeds[self._display_mode]
            self._state = f"{speed_info.get('emoji', '🚀')} {speed_info['formatted']}"
        else:
            # Default to total
            if "total" in self._speeds:
                self._state = f"🚀 {self._speeds['total']['formatted']}"
            else:
                self._state = "Active"

        _LOGGER.debug(f"Updated Cosmic Speedometer to {self._state}")


__all__ = ["CosmicSpeedometerSensor", "CALENDAR_INFO"]
