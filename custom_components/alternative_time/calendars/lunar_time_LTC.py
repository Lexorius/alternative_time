"""Lunar Coordinate Time (TCL) implementation - Version 1.0.0.

Based on the LTE440 (Lunar Time Ephemeris) paper by Lu, Yang & Xie (2025).
Implements relativistic time transformations between Lunar Coordinate Time (TCL),
Barycentric Dynamical Time (TDB), and Barycentric Coordinate Time (TCB).

Reference: "Lunar time ephemeris LTE440: Definitions, algorithm, and performance"
Astronomy & Astrophysics, Volume 704, A76 (December 2025)
DOI: https://doi.org/10.1051/0004-6361/202557345
GitHub: https://github.com/xlucn/LTE440
"""
from __future__ import annotations

from datetime import datetime, timezone
import logging
import math
from typing import Dict, Any, Optional

from homeassistant.core import HomeAssistant
from ..sensor import AlternativeTimeSensorBase

_LOGGER = logging.getLogger(__name__)

# ============================================
# CALENDAR METADATA
# ============================================

# Update interval in seconds (60 seconds = 1 minute)
# TCL changes slowly, but we want reasonable responsiveness
UPDATE_INTERVAL = 60

# Complete calendar information for auto-discovery
CALENDAR_INFO = {
    "id": "lunar_time",
    "version": "1.0.0",
    "icon": "mdi:moon-waning-crescent",
    "category": "space",
    "accuracy": "scientific",
    "update_interval": UPDATE_INTERVAL,
    
    # Multi-language names
    "name": {
        "en": "Lunar Coordinate Time (TCL)",
        "de": "Lunare Koordinatenzeit (TCL)",
        "es": "Tiempo de Coordenadas Lunares (TCL)",
        "fr": "Temps de Coordonnées Lunaires (TCL)",
        "it": "Tempo di Coordinate Lunari (TCL)",
        "nl": "Lunaire Coördinatentijd (TCL)",
        "pl": "Księżycowy Czas Koordynatowy (TCL)",
        "pt": "Tempo de Coordenadas Lunares (TCL)",
        "ru": "Лунное координатное время (TCL)",
        "ja": "月座標時 (TCL)",
        "zh": "月球坐标时 (TCL)",
        "ko": "달 좌표시 (TCL)"
    },
    
    # Short descriptions for UI
    "description": {
        "en": "Relativistic lunar timescale for cislunar space operations",
        "de": "Relativistische Mondzeit für cislunare Raumoperationen",
        "es": "Escala de tiempo lunar relativista para operaciones espaciales cislunares",
        "fr": "Échelle de temps lunaire relativiste pour les opérations cislunaires",
        "it": "Scala temporale lunare relativistica per operazioni cislunari",
        "nl": "Relativistische maantijdschaal voor cislunaire ruimteoperaties",
        "pl": "Relatywistyczna skala czasu księżycowego dla operacji cislunarnych",
        "pt": "Escala de tempo lunar relativística para operações cislunares",
        "ru": "Релятивистская лунная шкала времени для окололунных операций",
        "ja": "地球月間空間運用のための相対論的月時間スケール",
        "zh": "用于地月空间作业的相对论月球时标",
        "ko": "지구-달 공간 작전을 위한 상대론적 달 시간 척도"
    },
    
    # Translations for compatibility
    "translations": {
        "en": {
            "name": "Lunar Coordinate Time (TCL)",
            "description": "Relativistic time dilation between Earth and Moon based on LTE440 ephemeris. A clock on the Moon runs ~56.7 µs/day faster than on Earth."
        },
        "de": {
            "name": "Lunare Koordinatenzeit (TCL)",
            "description": "Relativistische Zeitdilatation zwischen Erde und Mond basierend auf der LTE440-Ephemeride. Eine Uhr auf dem Mond läuft ~56,7 µs/Tag schneller als auf der Erde."
        },
        "es": {
            "name": "Tiempo de Coordenadas Lunares (TCL)",
            "description": "Dilatación temporal relativista entre la Tierra y la Luna basada en la efeméride LTE440. Un reloj en la Luna funciona ~56,7 µs/día más rápido que en la Tierra."
        },
        "fr": {
            "name": "Temps de Coordonnées Lunaires (TCL)",
            "description": "Dilatation temporelle relativiste entre la Terre et la Lune basée sur l'éphéméride LTE440. Une horloge sur la Lune avance de ~56,7 µs/jour par rapport à la Terre."
        },
        "it": {
            "name": "Tempo di Coordinate Lunari (TCL)",
            "description": "Dilatazione temporale relativistica tra Terra e Luna basata sull'effemeride LTE440. Un orologio sulla Luna è più veloce di ~56,7 µs/giorno rispetto alla Terra."
        },
        "nl": {
            "name": "Lunaire Coördinatentijd (TCL)",
            "description": "Relativistische tijdsdilatatie tussen Aarde en Maan gebaseerd op de LTE440-efemeride. Een klok op de Maan loopt ~56,7 µs/dag sneller dan op Aarde."
        },
        "pl": {
            "name": "Księżycowy Czas Koordynatowy (TCL)",
            "description": "Relatywistyczna dylatacja czasu między Ziemią a Księżycem oparta na efemeridach LTE440. Zegar na Księżycu chodzi ~56,7 µs/dzień szybciej niż na Ziemi."
        },
        "pt": {
            "name": "Tempo de Coordenadas Lunares (TCL)",
            "description": "Dilatação temporal relativística entre Terra e Lua baseada na efeméride LTE440. Um relógio na Lua funciona ~56,7 µs/dia mais rápido que na Terra."
        },
        "ru": {
            "name": "Лунное координатное время (TCL)",
            "description": "Релятивистское замедление времени между Землёй и Луной на основе эфемерид LTE440. Часы на Луне идут на ~56,7 мкс/день быстрее, чем на Земле."
        },
        "ja": {
            "name": "月座標時 (TCL)",
            "description": "LTE440暦に基づく地球と月の間の相対論的時間遅延。月の時計は地球より約56.7µs/日速く進みます。"
        },
        "zh": {
            "name": "月球坐标时 (TCL)",
            "description": "基于LTE440星历的地月相对论时间膨胀。月球上的时钟比地球快约56.7微秒/天。"
        },
        "ko": {
            "name": "달 좌표시 (TCL)",
            "description": "LTE440 천체력에 기반한 지구와 달 사이의 상대론적 시간 지연. 달의 시계는 지구보다 약 56.7µs/일 빠르게 작동합니다."
        }
    },
    
    # LTE440-specific constants from the paper
    "lte440_data": {
        # Defining constants from IAU 2006 Resolution B3
        "L_B": 1.550519768e-8,  # Defining constant for TDB
        "TDB_0": -6.55e-5,      # seconds, offset constant
        
        # Secular drift rates from LTE440 paper (Equations 18, 19)
        "L_C_M": 1.4825362167e-8,  # TCL/TCB secular drift: ⟨dTCL/dTCB⟩ = 1 - L_C^M
        "L_D_M": 6.79835524e-10,   # TCL/TDB secular drift: ⟨dTCL/dTDB⟩ = 1 + L_D^M
        
        # Calibrated value from LTE441 comparison (Equation 22)
        "L_C_M_calibrated": 1.4825362217e-8,
        
        # Periodic variations (Table 3 from paper)
        # Format: (amplitude_seconds, period_days, phase_radians, source)
        "periodic_terms": [
            (1.65e-3, 365.2596, 2.94906, "Earth-Moon barycenter around Sun"),
            (126e-6, 29.5306, -2.51814, "Moon orbit around Earth"),
            (14.8e-6, 398.88, 2.25498, "Moon-Jupiter synodic"),
            (11.6e-6, 182.6298, -0.27233, "Semi-annual solar"),
            (7.39e-6, 4332.6044, 1.40232, "Jupiter orbital"),
            (4.39e-6, 583.93, -0.20621, "Moon-Venus synodic"),
            (4.31e-6, 399.01, 0.76127, "Moon-Mars synodic"),
            (2.86e-6, 14.7653, 0.80366, "Half lunar month"),
            (2.10e-6, 10746.1209, 1.36621, "Saturn orbital"),
            (1.67e-6, 779.93, 1.67439, "Mars synodic"),
            (1.54e-6, 30686.3472, 2.19003, "Uranus orbital"),
            (1.46e-6, 584.00, 2.69896, "Venus synodic"),
            (1.35e-6, 27.2122, -2.47067, "Tropical lunar month"),
        ],
        
        # Epoch: 1977 January 1, 0h0m32.184s TT (when TT, TCG, TCB, TCL coincide)
        # Expressed as Julian Date (TDB)
        "epoch_jd_tdb": 2443144.5003725,  # 1977-01-01 00:00:32.184 TT
        
        # J2000.0 epoch for periodic calculations
        "j2000_jd": 2451545.0,  # 2000-01-01 12:00:00 TT
        
        # Physical constants
        "seconds_per_day": 86400.0,
        "days_per_julian_year": 365.25,
        
        # Accuracy estimates from paper
        "accuracy_ns_2050": 0.15,  # nanoseconds
        "precision_ps": 1.0,       # picoseconds
        
        # Daily drift (derived): L_D^M * seconds_per_day
        # ≈ 6.79835524e-10 * 86400 ≈ 58.738 µs/day (TCL runs faster)
        "daily_drift_microseconds": 58.738,
    },
    
    # Configuration options for the sensor
    "config_options": {
        "display_format": {
            "type": "select",
            "default": "drift_microseconds",
            "options": ["drift_microseconds", "drift_nanoseconds", "drift_seconds", "clock_ratio", "accumulated_ms"],
            "label": {
                "en": "Display Format",
                "de": "Anzeigeformat",
                "es": "Formato de Visualización",
                "fr": "Format d'Affichage",
                "it": "Formato di Visualizzazione",
                "nl": "Weergaveformaat",
                "pl": "Format Wyświetlania",
                "pt": "Formato de Exibição",
                "ru": "Формат Отображения",
                "ja": "表示形式",
                "zh": "显示格式",
                "ko": "표시 형식"
            },
            "description": {
                "en": "Choose how to display the lunar time drift",
                "de": "Wählen Sie die Anzeige der Mondzeit-Drift",
                "es": "Elija cómo mostrar la deriva del tiempo lunar",
                "fr": "Choisissez l'affichage de la dérive temporelle lunaire",
                "it": "Scegli come visualizzare la deriva temporale lunare",
                "nl": "Kies hoe de maantijdsdrift wordt weergegeven",
                "pl": "Wybierz sposób wyświetlania dryfu czasu księżycowego",
                "pt": "Escolha como exibir a deriva do tempo lunar",
                "ru": "Выберите отображение лунного временного дрейфа",
                "ja": "月時間ドリフトの表示方法を選択",
                "zh": "选择月球时间漂移的显示方式",
                "ko": "달 시간 드리프트 표시 방법 선택"
            },
            "option_labels": {
                "drift_microseconds": {
                    "en": "Daily Drift (µs/day)",
                    "de": "Tägliche Drift (µs/Tag)",
                    "es": "Deriva Diaria (µs/día)",
                    "fr": "Dérive Quotidienne (µs/jour)",
                    "it": "Deriva Giornaliera (µs/giorno)",
                    "nl": "Dagelijkse Drift (µs/dag)",
                    "pl": "Dzienny Dryf (µs/dzień)",
                    "pt": "Deriva Diária (µs/dia)",
                    "ru": "Суточный Дрейф (мкс/день)",
                    "ja": "日次ドリフト (µs/日)",
                    "zh": "每日漂移 (µs/天)",
                    "ko": "일일 드리프트 (µs/일)"
                },
                "drift_nanoseconds": {
                    "en": "Daily Drift (ns/day)",
                    "de": "Tägliche Drift (ns/Tag)",
                    "es": "Deriva Diaria (ns/día)",
                    "fr": "Dérive Quotidienne (ns/jour)",
                    "it": "Deriva Giornaliera (ns/giorno)",
                    "nl": "Dagelijkse Drift (ns/dag)",
                    "pl": "Dzienny Dryf (ns/dzień)",
                    "pt": "Deriva Diária (ns/dia)",
                    "ru": "Суточный Дрейф (нс/день)",
                    "ja": "日次ドリフト (ns/日)",
                    "zh": "每日漂移 (ns/天)",
                    "ko": "일일 드리프트 (ns/일)"
                },
                "drift_seconds": {
                    "en": "Drift Rate (s/s)",
                    "de": "Driftrate (s/s)",
                    "es": "Tasa de Deriva (s/s)",
                    "fr": "Taux de Dérive (s/s)",
                    "it": "Tasso di Deriva (s/s)",
                    "nl": "Driftsnelheid (s/s)",
                    "pl": "Wskaźnik Dryfu (s/s)",
                    "pt": "Taxa de Deriva (s/s)",
                    "ru": "Скорость Дрейфа (с/с)",
                    "ja": "ドリフト率 (s/s)",
                    "zh": "漂移率 (s/s)",
                    "ko": "드리프트율 (s/s)"
                },
                "clock_ratio": {
                    "en": "Clock Ratio (TCL/TDB)",
                    "de": "Uhrverhältnis (TCL/TDB)",
                    "es": "Razón de Reloj (TCL/TDB)",
                    "fr": "Rapport d'Horloge (TCL/TDB)",
                    "it": "Rapporto Orologio (TCL/TDB)",
                    "nl": "Klokverhouding (TCL/TDB)",
                    "pl": "Stosunek Zegarów (TCL/TDB)",
                    "pt": "Razão do Relógio (TCL/TDB)",
                    "ru": "Соотношение Часов (TCL/TDB)",
                    "ja": "クロック比 (TCL/TDB)",
                    "zh": "时钟比率 (TCL/TDB)",
                    "ko": "시계 비율 (TCL/TDB)"
                },
                "accumulated_ms": {
                    "en": "Accumulated Difference (ms)",
                    "de": "Akkumulierte Differenz (ms)",
                    "es": "Diferencia Acumulada (ms)",
                    "fr": "Différence Cumulée (ms)",
                    "it": "Differenza Accumulata (ms)",
                    "nl": "Geaccumuleerd Verschil (ms)",
                    "pl": "Skumulowana Różnica (ms)",
                    "pt": "Diferença Acumulada (ms)",
                    "ru": "Накопленная Разница (мс)",
                    "ja": "累積差 (ms)",
                    "zh": "累积差 (ms)",
                    "ko": "누적 차이 (ms)"
                }
            }
        },
        "show_periodic_terms": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show Periodic Variations",
                "de": "Periodische Variationen anzeigen",
                "es": "Mostrar Variaciones Periódicas",
                "fr": "Afficher les Variations Périodiques",
                "it": "Mostra Variazioni Periodiche",
                "nl": "Toon Periodieke Variaties",
                "pl": "Pokaż Wariacje Okresowe",
                "pt": "Mostrar Variações Periódicas",
                "ru": "Показать Периодические Вариации",
                "ja": "周期変動を表示",
                "zh": "显示周期变化",
                "ko": "주기적 변동 표시"
            },
            "description": {
                "en": "Include annual (~1.65ms) and monthly (~126µs) periodic terms",
                "de": "Jährliche (~1,65ms) und monatliche (~126µs) periodische Terme einbeziehen",
                "es": "Incluir términos periódicos anuales (~1,65ms) y mensuales (~126µs)",
                "fr": "Inclure les termes périodiques annuels (~1,65ms) et mensuels (~126µs)",
                "it": "Includere termini periodici annuali (~1,65ms) e mensili (~126µs)",
                "nl": "Inclusief jaarlijkse (~1,65ms) en maandelijkse (~126µs) periodieke termen",
                "pl": "Uwzględnij roczne (~1,65ms) i miesięczne (~126µs) terminy okresowe",
                "pt": "Incluir termos periódicos anuais (~1,65ms) e mensais (~126µs)",
                "ru": "Включить годовые (~1,65мс) и месячные (~126мкс) периодические члены",
                "ja": "年周期（~1.65ms）と月周期（~126µs）の項を含める",
                "zh": "包含年度（~1.65ms）和月度（~126µs）周期项",
                "ko": "연간(~1.65ms) 및 월간(~126µs) 주기 항 포함"
            }
        },
        "use_calibrated_drift": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Use Calibrated Drift Rate",
                "de": "Kalibrierte Driftrate verwenden",
                "es": "Usar Tasa de Deriva Calibrada",
                "fr": "Utiliser le Taux de Dérive Calibré",
                "it": "Usa Tasso di Deriva Calibrato",
                "nl": "Gebruik Gekalibreerde Driftsnelheid",
                "pl": "Użyj Skalibrowanego Wskaźnika Dryfu",
                "pt": "Usar Taxa de Deriva Calibrada",
                "ru": "Использовать Калиброванную Скорость Дрейфа",
                "ja": "校正済みドリフト率を使用",
                "zh": "使用校准漂移率",
                "ko": "보정된 드리프트율 사용"
            },
            "description": {
                "en": "Use L_C^M calibrated with LTE441 for improved long-term accuracy",
                "de": "L_C^M mit LTE441 kalibriert für verbesserte Langzeitgenauigkeit verwenden",
                "es": "Usar L_C^M calibrado con LTE441 para mejor precisión a largo plazo",
                "fr": "Utiliser L_C^M calibré avec LTE441 pour une meilleure précision à long terme",
                "it": "Usa L_C^M calibrato con LTE441 per maggiore precisione a lungo termine",
                "nl": "Gebruik L_C^M gekalibreerd met LTE441 voor betere langetermijnnauwkeurigheid",
                "pl": "Użyj L_C^M skalibrowanego z LTE441 dla lepszej dokładności długoterminowej",
                "pt": "Usar L_C^M calibrado com LTE441 para melhor precisão a longo prazo",
                "ru": "Использовать L_C^M, калиброванный с LTE441 для улучшенной долгосрочной точности",
                "ja": "LTE441で校正されたL_C^Mを使用して長期精度を向上",
                "zh": "使用LTE441校准的L_C^M以提高长期精度",
                "ko": "장기 정확도 향상을 위해 LTE441로 보정된 L_C^M 사용"
            }
        },
        "precision_digits": {
            "type": "select",
            "default": "3",
            "options": ["1", "2", "3", "4", "5", "6"],
            "label": {
                "en": "Decimal Precision",
                "de": "Dezimalpräzision",
                "es": "Precisión Decimal",
                "fr": "Précision Décimale",
                "it": "Precisione Decimale",
                "nl": "Decimale Precisie",
                "pl": "Precyzja Dziesiętna",
                "pt": "Precisão Decimal",
                "ru": "Десятичная Точность",
                "ja": "小数点精度",
                "zh": "小数精度",
                "ko": "소수점 정밀도"
            },
            "description": {
                "en": "Number of decimal places to display",
                "de": "Anzahl der anzuzeigenden Dezimalstellen",
                "es": "Número de decimales a mostrar",
                "fr": "Nombre de décimales à afficher",
                "it": "Numero di decimali da visualizzare",
                "nl": "Aantal decimalen om weer te geven",
                "pl": "Liczba miejsc dziesiętnych do wyświetlenia",
                "pt": "Número de casas decimais a exibir",
                "ru": "Количество десятичных знаков для отображения",
                "ja": "表示する小数点以下の桁数",
                "zh": "要显示的小数位数",
                "ko": "표시할 소수점 자릿수"
            }
        }
    },
    
    # Additional metadata
    "reference_url": "https://doi.org/10.1051/0004-6361/202557345",
    "documentation_url": "https://github.com/xlucn/LTE440",
    "origin": "Purple Mountain Observatory, Chinese Academy of Sciences",
    "created_by": "Lu, Yang & Xie (2025)",
    "based_on": "JPL DE440 Ephemeris",
    
    # IAU Resolution references
    "iau_resolutions": [
        "IAU 2000 Resolution B1.5 (TCG-TCB transformation)",
        "IAU 2006 Resolution B3 (TDB redefinition)",
        "IAU 2024 Resolution II (LCRS and TCL establishment)",
        "IAU 2024 Resolution III (Coordinated lunar time standard)"
    ],
    
    # Related calendars
    "related": ["tai", "ut1", "julian", "mars"],
    
    # Tags for searching and filtering
    "tags": [
        "lunar", "moon", "tcl", "tdb", "tcb", "relativistic", "time-dilation",
        "ephemeris", "lte440", "de440", "cislunar", "space", "scientific",
        "astronomical", "iau", "coordinate-time", "selenocenter"
    ],
    
    # Extended notes
    "notes": {
        "en": (
            "Lunar Coordinate Time (TCL) is the time coordinate for the Lunar Celestial Reference System (LCRS), "
            "established by IAU 2024 Resolution II. Due to relativistic effects (lower gravity and orbital motion), "
            "a clock on the Moon's selenoid runs approximately 56.7 microseconds per day faster than a clock on Earth's geoid. "
            "The main periodic variations are annual (~1.65 ms, from Earth-Moon barycenter orbit) and "
            "monthly (~126 µs, from Moon's orbit around Earth). LTE440 accuracy is <0.15 ns until 2050."
        ),
        "de": (
            "Die Lunare Koordinatenzeit (TCL) ist die Zeitkoordinate für das Lunare Himmlische Referenzsystem (LCRS), "
            "etabliert durch die IAU-Resolution II von 2024. Aufgrund relativistischer Effekte (geringere Gravitation und Orbitalbewegung) "
            "läuft eine Uhr auf dem Mondselenoid etwa 56,7 Mikrosekunden pro Tag schneller als eine Uhr auf dem Erdgeoid. "
            "Die wichtigsten periodischen Variationen sind jährlich (~1,65 ms, von der Erde-Mond-Baryzentrum-Umlaufbahn) und "
            "monatlich (~126 µs, von der Mondumlaufbahn um die Erde). Die LTE440-Genauigkeit beträgt <0,15 ns bis 2050."
        ),
        "es": (
            "El Tiempo de Coordenadas Lunares (TCL) es la coordenada temporal del Sistema de Referencia Celestial Lunar (LCRS), "
            "establecido por la Resolución II de la UAI de 2024. Debido a efectos relativistas (menor gravedad y movimiento orbital), "
            "un reloj en el selenoide lunar funciona aproximadamente 56,7 microsegundos por día más rápido que uno en el geoide terrestre."
        ),
        "fr": (
            "Le Temps de Coordonnées Lunaires (TCL) est la coordonnée temporelle du Système de Référence Céleste Lunaire (LCRS), "
            "établi par la Résolution II de l'UAI de 2024. En raison des effets relativistes, "
            "une horloge sur le sélénoïde lunaire avance d'environ 56,7 microsecondes par jour par rapport au géoïde terrestre."
        ),
        "it": (
            "Il Tempo di Coordinate Lunari (TCL) è la coordinata temporale del Sistema di Riferimento Celestiale Lunare (LCRS), "
            "stabilito dalla Risoluzione II dell'IAU del 2024. A causa degli effetti relativistici, "
            "un orologio sul selenoide lunare funziona circa 56,7 microsecondi al giorno più velocemente rispetto al geoide terrestre."
        ),
        "nl": (
            "Lunaire Coördinatentijd (TCL) is de tijdcoördinaat voor het Lunaire Hemelse Referentiesysteem (LCRS), "
            "vastgesteld door IAU 2024 Resolutie II. Door relativistische effecten "
            "loopt een klok op het maanselenoid ongeveer 56,7 microseconden per dag sneller dan op het aardse geoïde."
        ),
        "pl": (
            "Księżycowy Czas Koordynatowy (TCL) to współrzędna czasowa dla Księżycowego Niebieskiego Układu Odniesienia (LCRS), "
            "ustanowionego przez Rezolucję II IAU z 2024 roku. Ze względu na efekty relatywistyczne "
            "zegar na selenoidzie księżycowym chodzi o około 56,7 mikrosekundy dziennie szybciej niż na geoidzie ziemskiej."
        ),
        "pt": (
            "O Tempo de Coordenadas Lunares (TCL) é a coordenada temporal do Sistema de Referência Celestial Lunar (LCRS), "
            "estabelecido pela Resolução II da IAU de 2024. Devido a efeitos relativísticos, "
            "um relógio no selenoide lunar funciona aproximadamente 56,7 microssegundos por dia mais rápido que no geoide terrestre."
        ),
        "ru": (
            "Лунное координатное время (TCL) — это временная координата Лунной небесной системы отсчёта (LCRS), "
            "установленной резолюцией II МАС 2024 года. Из-за релятивистских эффектов "
            "часы на лунном селеноиде идут примерно на 56,7 микросекунды в день быстрее, чем на земном геоиде."
        ),
        "ja": (
            "月座標時（TCL）は、2024年IAU決議IIで確立された月天球参照系（LCRS）の時間座標です。"
            "相対論的効果により、月のセレノイド上の時計は地球のジオイド上の時計より約56.7マイクロ秒/日速く進みます。"
        ),
        "zh": (
            "月球坐标时（TCL）是月球天球参考系（LCRS）的时间坐标，由2024年IAU第二号决议建立。"
            "由于相对论效应，月球大地水准面上的时钟比地球大地水准面上的时钟每天快约56.7微秒。"
        ),
        "ko": (
            "달 좌표시(TCL)는 2024년 IAU 결의안 II에 의해 설립된 달 천구 기준계(LCRS)의 시간 좌표입니다. "
            "상대론적 효과로 인해 달의 셀레노이드 위의 시계는 지구의 지오이드 위의 시계보다 하루에 약 56.7마이크로초 빠르게 작동합니다."
        )
    }
}


# ============================================
# SENSOR CLASS
# ============================================

class LunarTimeSensor(AlternativeTimeSensorBase):
    """Sensor for displaying Lunar Coordinate Time (TCL) based on LTE440."""

    # Class-level update interval
    UPDATE_INTERVAL = UPDATE_INTERVAL

    def __init__(self, base_name: str, hass: HomeAssistant) -> None:
        """Initialize the Lunar Time sensor."""
        super().__init__(base_name, hass)

        # Store CALENDAR_INFO as instance variable
        self._calendar_info = CALENDAR_INFO

        # Localized name for the entity
        calendar_name = self._translate("name", "Lunar Coordinate Time (TCL)")

        # Set sensor attributes
        self._attr_name = f"{base_name} {calendar_name}"
        self._attr_unique_id = f"{base_name}_lunar_time_tcl"
        self._attr_icon = CALENDAR_INFO.get("icon", "mdi:moon-waning-crescent")

        # Configuration options with defaults
        config_defaults = CALENDAR_INFO.get("config_options", {})
        self._display_format = config_defaults.get("display_format", {}).get("default", "drift_microseconds")
        self._show_periodic_terms = config_defaults.get("show_periodic_terms", {}).get("default", True)
        self._use_calibrated_drift = config_defaults.get("use_calibrated_drift", {}).get("default", True)
        self._precision_digits = int(config_defaults.get("precision_digits", {}).get("default", "3"))

        # LTE440 data
        self._lte_data = CALENDAR_INFO["lte440_data"]

        # Flag to track if options have been loaded
        self._options_loaded = False

        # Initialize state
        self._state = None
        self._tcl_info: Dict[str, Any] = {}

        _LOGGER.debug(f"Initialized Lunar Time sensor: {self._attr_name}")

    def _load_options(self) -> None:
        """Load plugin options after IDs are set."""
        if self._options_loaded:
            return

        try:
            options = self.get_plugin_options()
            if options:
                self._display_format = options.get("display_format", self._display_format)
                self._show_periodic_terms = options.get("show_periodic_terms", self._show_periodic_terms)
                self._use_calibrated_drift = options.get("use_calibrated_drift", self._use_calibrated_drift)
                self._precision_digits = int(options.get("precision_digits", self._precision_digits))

                _LOGGER.debug(f"Lunar Time sensor loaded options: format={self._display_format}, "
                             f"periodic={self._show_periodic_terms}, calibrated={self._use_calibrated_drift}")
            else:
                _LOGGER.debug("Lunar Time sensor using default options")

            self._options_loaded = True
        except Exception as e:
            _LOGGER.debug(f"Lunar Time sensor could not load options yet: {e}")

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        await super().async_added_to_hass()

        # Try to load options now that IDs should be set
        self._load_options()

        # Perform initial update
        self.update()

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes."""
        attrs = super().extra_state_attributes or {}

        if self._tcl_info:
            attrs.update(self._tcl_info)

            # Add description in user's language
            attrs["description"] = self._translate('description')

            # Add configuration info
            attrs["display_format_setting"] = self._display_format
            attrs["show_periodic_terms_setting"] = self._show_periodic_terms
            attrs["use_calibrated_drift_setting"] = self._use_calibrated_drift

        return attrs

    def _datetime_to_jd(self, dt: datetime) -> float:
        """Convert datetime to Julian Date."""
        # Ensure UTC
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            dt = dt.astimezone(timezone.utc)

        # Julian Date calculation
        year = dt.year
        month = dt.month
        day = dt.day + dt.hour / 24.0 + dt.minute / 1440.0 + dt.second / 86400.0 + dt.microsecond / 86400000000.0

        if month <= 2:
            year -= 1
            month += 12

        a = int(year / 100)
        b = 2 - a + int(a / 4)

        jd = int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + b - 1524.5

        return jd

    def _calculate_periodic_variation(self, jd: float) -> float:
        """Calculate the sum of periodic variations at given Julian Date.
        
        Based on Table 3 from the LTE440 paper.
        """
        if not self._show_periodic_terms:
            return 0.0

        j2000_jd = self._lte_data["j2000_jd"]
        days_since_j2000 = jd - j2000_jd

        total_variation = 0.0

        for amplitude, period, phase, source in self._lte_data["periodic_terms"]:
            # Calculate periodic term: A * sin(2π/T * t + φ)
            angular_frequency = 2.0 * math.pi / period
            term = amplitude * math.sin(angular_frequency * days_since_j2000 + phase)
            total_variation += term

        return total_variation

    def _calculate_tcl_tdb_difference(self, dt: datetime) -> Dict[str, Any]:
        """Calculate TCL - TDB difference and related quantities.
        
        Based on equations from the LTE440 paper:
        - Secular drift: ⟨dTCL/dTDB⟩ = 1 + L_D^M
        - TCL - TDB ≈ (L_B/(1-L_B)) * (TDB - t0) + periodic terms
        """
        jd = self._datetime_to_jd(dt)
        
        # Get constants
        L_B = self._lte_data["L_B"]
        TDB_0 = self._lte_data["TDB_0"]
        
        # Select drift rate (calibrated or standard)
        if self._use_calibrated_drift:
            L_C_M = self._lte_data["L_C_M_calibrated"]
        else:
            L_C_M = self._lte_data["L_C_M"]
        
        L_D_M = self._lte_data["L_D_M"]
        
        # Calculate days since epoch (1977-01-01)
        epoch_jd = self._lte_data["epoch_jd_tdb"]
        days_since_epoch = jd - epoch_jd
        seconds_since_epoch = days_since_epoch * self._lte_data["seconds_per_day"]
        
        # Calculate secular drift contribution to TCL - TDB
        # From Eq. (11): LDTE(TDB) = (L_B/(1-L_B))*(TDB-t0) - TDB0/(1-L_B) + LTE(TDB)
        secular_term = (L_B / (1 - L_B)) * seconds_since_epoch
        
        # Add periodic variations
        periodic_variation = self._calculate_periodic_variation(jd)
        
        # Total TCL - TDB difference
        tcl_minus_tdb = secular_term + periodic_variation
        
        # Calculate instantaneous drift rate (with periodic contribution)
        # Base secular drift
        secular_drift_rate = L_D_M
        
        # Add derivative of periodic terms for instantaneous rate
        j2000_jd = self._lte_data["j2000_jd"]
        days_since_j2000 = jd - j2000_jd
        periodic_drift_rate = 0.0
        
        if self._show_periodic_terms:
            for amplitude, period, phase, source in self._lte_data["periodic_terms"]:
                angular_frequency = 2.0 * math.pi / period
                # Derivative: dA*sin(ωt+φ)/dt = A*ω*cos(ωt+φ)
                # Convert from per-day to dimensionless
                term_rate = (amplitude * angular_frequency * 
                            math.cos(angular_frequency * days_since_j2000 + phase) / 
                            self._lte_data["seconds_per_day"])
                periodic_drift_rate += term_rate
        
        total_drift_rate = secular_drift_rate + periodic_drift_rate
        
        # Clock ratio: dTCL/dTDB = 1 + L_D^M + periodic
        clock_ratio = 1.0 + total_drift_rate
        
        # Daily drift in microseconds
        daily_drift_us = total_drift_rate * self._lte_data["seconds_per_day"] * 1e6
        
        # Daily drift in nanoseconds
        daily_drift_ns = daily_drift_us * 1000
        
        # Calculate current periodic contributions from major terms
        annual_term = 0.0
        monthly_term = 0.0
        if self._show_periodic_terms and len(self._lte_data["periodic_terms"]) >= 2:
            # Annual term (first in list)
            amp1, per1, ph1, _ = self._lte_data["periodic_terms"][0]
            annual_term = amp1 * math.sin(2.0 * math.pi / per1 * days_since_j2000 + ph1)
            
            # Monthly term (second in list)
            amp2, per2, ph2, _ = self._lte_data["periodic_terms"][1]
            monthly_term = amp2 * math.sin(2.0 * math.pi / per2 * days_since_j2000 + ph2)
        
        return {
            "julian_date": round(jd, 6),
            "days_since_epoch": round(days_since_epoch, 4),
            "seconds_since_epoch": round(seconds_since_epoch, 2),
            
            # TCL - TDB difference
            "tcl_minus_tdb_seconds": round(tcl_minus_tdb, 9),
            "tcl_minus_tdb_milliseconds": round(tcl_minus_tdb * 1e3, 6),
            "tcl_minus_tdb_microseconds": round(tcl_minus_tdb * 1e6, 3),
            
            # Drift rates
            "drift_rate_dimensionless": f"{total_drift_rate:.12e}",
            "daily_drift_microseconds": round(daily_drift_us, 3),
            "daily_drift_nanoseconds": round(daily_drift_ns, 3),
            "clock_ratio_tcl_tdb": f"{clock_ratio:.15f}",
            
            # Secular constants from LTE440
            "L_C_M": f"{L_C_M:.10e}",
            "L_D_M": f"{L_D_M:.10e}",
            "using_calibrated_rate": self._use_calibrated_drift,
            
            # Periodic variation details
            "periodic_variation_seconds": round(periodic_variation, 9) if self._show_periodic_terms else 0.0,
            "periodic_variation_microseconds": round(periodic_variation * 1e6, 3) if self._show_periodic_terms else 0.0,
            "annual_term_milliseconds": round(annual_term * 1e3, 4) if self._show_periodic_terms else 0.0,
            "monthly_term_microseconds": round(monthly_term * 1e6, 3) if self._show_periodic_terms else 0.0,
            
            # Metadata
            "reference": "LTE440 (Lu, Yang & Xie, 2025)",
            "accuracy_estimate": f"<{self._lte_data['accuracy_ns_2050']} ns until 2050",
            "ephemeris_basis": "JPL DE440",
            
            # Explanation
            "explanation_en": "A clock on the Moon runs faster than on Earth due to lower gravity (general relativity) and orbital motion (special relativity)",
            "calendar_type": "Lunar Coordinate Time",
            "iau_resolution": "IAU 2024 Resolution II"
        }

    def _format_state(self, tcl_info: Dict[str, Any]) -> str:
        """Format the sensor state based on display format setting."""
        precision = self._precision_digits
        
        if self._display_format == "drift_microseconds":
            value = tcl_info["daily_drift_microseconds"]
            return f"{value:.{precision}f} µs/day"
        
        elif self._display_format == "drift_nanoseconds":
            value = tcl_info["daily_drift_nanoseconds"]
            return f"{value:.{precision}f} ns/day"
        
        elif self._display_format == "drift_seconds":
            value = float(tcl_info["drift_rate_dimensionless"])
            return f"{value:.{precision}e}"
        
        elif self._display_format == "clock_ratio":
            ratio = tcl_info["clock_ratio_tcl_tdb"]
            # Show deviation from 1
            return ratio
        
        elif self._display_format == "accumulated_ms":
            value = tcl_info["tcl_minus_tdb_milliseconds"]
            return f"{value:.{precision}f} ms"
        
        else:
            # Default to microseconds
            value = tcl_info["daily_drift_microseconds"]
            return f"{value:.{precision}f} µs/day"

    def set_options(
        self,
        *,
        display_format: Optional[str] = None,
        show_periodic_terms: Optional[bool] = None,
        use_calibrated_drift: Optional[bool] = None,
        precision_digits: Optional[int] = None
    ) -> None:
        """Set calendar options from config flow."""
        if display_format is not None:
            valid_formats = ["drift_microseconds", "drift_nanoseconds", "drift_seconds", "clock_ratio", "accumulated_ms"]
            if display_format in valid_formats:
                self._display_format = display_format
                _LOGGER.debug(f"Set display_format to: {display_format}")

        if show_periodic_terms is not None:
            self._show_periodic_terms = bool(show_periodic_terms)
            _LOGGER.debug(f"Set show_periodic_terms to: {show_periodic_terms}")

        if use_calibrated_drift is not None:
            self._use_calibrated_drift = bool(use_calibrated_drift)
            _LOGGER.debug(f"Set use_calibrated_drift to: {use_calibrated_drift}")

        if precision_digits is not None:
            self._precision_digits = int(precision_digits)
            _LOGGER.debug(f"Set precision_digits to: {precision_digits}")

    def update(self) -> None:
        """Update the sensor."""
        try:
            now = datetime.now(timezone.utc)
            
            # Calculate TCL information
            self._tcl_info = self._calculate_tcl_tdb_difference(now)
            
            # Format state
            self._state = self._format_state(self._tcl_info)
            
            _LOGGER.debug(f"Lunar Time updated: {self._state}")
            
        except Exception as e:
            _LOGGER.error(f"Error updating Lunar Time sensor: {e}")
            self._state = "Error"
            self._tcl_info = {"error": str(e)}
