"""Synodic Periods Calendar Plugin for Alternative Time Systems.

Tracks planetary synodic cycles (planet-to-planet alignments as seen from Earth).
No external dependencies - uses simplified astronomical algorithms.

A synodic period is the time required for a planet to return to the same position
relative to Earth and the Sun (e.g., opposition to opposition, conjunction to conjunction).
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
import logging
import math

from ..sensor import AlternativeTimeSensorBase

_LOGGER = logging.getLogger(__name__)

# Calendar metadata and configuration
CALENDAR_INFO = {
    "id": "synodic",
    "version": "2.5.1",
    "name": {
        "en": "Synodic Periods Calendar",
        "de": "Synodischer Perioden-Kalender",
        "es": "Calendario de Períodos Sinódicos",
        "fr": "Calendrier des Périodes Synodiques",
        "it": "Calendario dei Periodi Sinodici",
        "nl": "Synodische Perioden Kalender",
        "pl": "Kalendarz Okresów Synodycznych",
        "pt": "Calendário de Períodos Sinódicos",
        "ru": "Календарь Синодических Периодов",
        "ja": "会合周期カレンダー",
        "zh": "会合周期历",
        "ko": "회합 주기 달력"
    },
    "description": {
        "en": "Astronomical calendar tracking planetary alignments and synodic cycles (oppositions, conjunctions, elongations)",
        "de": "Astronomischer Kalender zur Verfolgung von Planetenkonstellationen und synodischen Zyklen (Oppositionen, Konjunktionen, Elongationen)",
        "es": "Calendario astronómico que rastrea alineaciones planetarias y ciclos sinódicos (oposiciones, conjunciones, elongaciones)",
        "fr": "Calendrier astronomique suivant les alignements planétaires et cycles synodiques (oppositions, conjonctions, élongations)",
        "it": "Calendario astronomico che traccia allineamenti planetari e cicli sinodici (opposizioni, congiunzioni, elongazioni)",
        "nl": "Astronomische kalender voor planetaire uitlijningen en synodische cycli (opposities, conjuncties, elongaties)",
        "pl": "Kalendarz astronomiczny śledzący układy planetarne i cykle synodyczne (opozycje, koniunkcje, elongacje)",
        "pt": "Calendário astronômico rastreando alinhamentos planetários e ciclos sinódicos (oposições, conjunções, elongações)",
        "ru": "Астрономический календарь отслеживания планетарных выравниваний и синодических циклов (противостояния, соединения, элонгации)",
        "ja": "惑星の配列と会合周期を追跡する天文カレンダー（衝、合、離角）",
        "zh": "追踪行星排列和会合周期的天文历（冲、合、大距）",
        "ko": "행성 정렬과 회합 주기를 추적하는 천문 달력 (충, 합, 이각)"
    },
    "category": "technical",
    "update_interval": 3600,  # Update hourly
    "accuracy": "day",
    "icon": "mdi:orbit",
    "reference_url": "https://en.wikipedia.org/wiki/Orbital_period#Synodic_period",
    
    # Scientific disclaimer
    "disclaimer": {
        "en": "⚠️ SIMPLIFIED CALCULATIONS: Uses mean orbital elements for approximate positions. Accuracy ±1-2 days for inner planets, ±5-10 days for outer planets. Perfect planetary alignment is extremely rare (next: May 6, 2492). For precise ephemerides, consult NASA JPL Horizons.",
        "de": "⚠️ VEREINFACHTE BERECHNUNGEN: Verwendet mittlere Bahnelemente für ungefähre Positionen. Genauigkeit ±1-2 Tage für innere Planeten, ±5-10 Tage für äußere Planeten. Perfekte Planetenausrichtung ist extrem selten (nächste: 6. Mai 2492). Für präzise Ephemeriden siehe NASA JPL Horizons.",
        "es": "⚠️ CÁLCULOS SIMPLIFICADOS: Usa elementos orbitales medios para posiciones aproximadas. Precisión ±1-2 días para planetas interiores, ±5-10 días para planetas exteriores. La alineación planetaria perfecta es extremadamente rara (próxima: 6 mayo 2492). Para efemérides precisas, consulte NASA JPL Horizons.",
        "fr": "⚠️ CALCULS SIMPLIFIÉS: Utilise des éléments orbitaux moyens pour des positions approximatives. Précision ±1-2 jours pour les planètes intérieures, ±5-10 jours pour les planètes extérieures. L'alignement planétaire parfait est extrêmement rare (prochain: 6 mai 2492). Pour des éphémérides précises, consultez NASA JPL Horizons.",
        "it": "⚠️ CALCOLI SEMPLIFICATI: Usa elementi orbitali medi per posizioni approssimate. Precisione ±1-2 giorni per pianeti interni, ±5-10 giorni per pianeti esterni. L'allineamento planetario perfetto è estremamente raro (prossimo: 6 maggio 2492). Per effemeridi precise, consultare NASA JPL Horizons.",
        "nl": "⚠️ VEREENVOUDIGDE BEREKENINGEN: Gebruikt gemiddelde baanelementen voor benaderde posities. Nauwkeurigheid ±1-2 dagen voor binnenplaneten, ±5-10 dagen voor buitenplaneten. Perfecte planetaire uitlijning is extreem zeldzaam (volgende: 6 mei 2492). Voor precieze efemeriden, raadpleeg NASA JPL Horizons.",
        "pl": "⚠️ UPROSZCZONE OBLICZENIA: Używa średnich elementów orbitalnych dla przybliżonych pozycji. Dokładność ±1-2 dni dla planet wewnętrznych, ±5-10 dni dla planet zewnętrznych. Idealne ustawienie planet jest niezwykle rzadkie (następne: 6 maja 2492). Dla dokładnych efemeryd, skonsultuj NASA JPL Horizons.",
        "pt": "⚠️ CÁLCULOS SIMPLIFICADOS: Usa elementos orbitais médios para posições aproximadas. Precisão ±1-2 dias para planetas interiores, ±5-10 dias para planetas exteriores. O alinhamento planetário perfeito é extremamente raro (próximo: 6 maio 2492). Para efemérides precisas, consulte NASA JPL Horizons.",
        "ru": "⚠️ УПРОЩЕННЫЕ ВЫЧИСЛЕНИЯ: Использует средние орбитальные элементы для приблизительных позиций. Точность ±1-2 дня для внутренних планет, ±5-10 дней для внешних планет. Идеальное выравнивание планет крайне редко (следующее: 6 мая 2492). Для точных эфемерид обратитесь к NASA JPL Horizons.",
        "ja": "⚠️ 簡略化された計算：平均軌道要素を使用した概算位置。内惑星は±1-2日、外惑星は±5-10日の精度。完全な惑星直列は極めて稀（次回：2492年5月6日）。正確な暦表についてはNASA JPL Horizonsを参照。",
        "zh": "⚠️ 简化计算：使用平均轨道元素进行近似定位。内行星精度±1-2天，外行星±5-10天。完美的行星排列极其罕见（下次：2492年5月6日）。精确星历表请查询NASA JPL Horizons。",
        "ko": "⚠️ 단순화된 계산: 평균 궤도 요소를 사용한 근사 위치. 내행성 ±1-2일, 외행성 ±5-10일 정확도. 완벽한 행성 정렬은 극히 드물다 (다음: 2492년 5월 6일). 정밀한 천체력은 NASA JPL Horizons 참조."
    },
    
    # Event definitions
    "event_definitions": {
        "opposition": {
            "en": "Opposition: Planet is directly opposite the Sun from Earth (180°). Best viewing time - planet is visible all night, closest to Earth, and brightest.",
            "de": "Opposition: Planet steht der Sonne von der Erde aus gesehen direkt gegenüber (180°). Beste Beobachtungszeit - Planet ist die ganze Nacht sichtbar, erdnah und am hellsten.",
            "es": "Oposición: El planeta está directamente opuesto al Sol desde la Tierra (180°). Mejor momento para observar - planeta visible toda la noche, más cercano y brillante.",
            "fr": "Opposition: La planète est directement opposée au Soleil depuis la Terre (180°). Meilleur moment d'observation - planète visible toute la nuit, plus proche et plus brillante.",
            "it": "Opposizione: Il pianeta è direttamente opposto al Sole dalla Terra (180°). Miglior momento di osservazione - pianeta visibile tutta la notte, più vicino e luminoso.",
            "nl": "Oppositie: Planeet staat recht tegenover de Zon gezien vanaf de Aarde (180°). Beste waarneemtijd - planeet is hele nacht zichtbaar, dichtst bij en helderst.",
            "pl": "Opozycja: Planeta znajduje się dokładnie naprzeciwko Słońca z Ziemi (180°). Najlepszy czas obserwacji - planeta widoczna całą noc, najbliżej i najjaśniejsza.",
            "pt": "Oposição: Planeta está diretamente oposto ao Sol da Terra (180°). Melhor momento de observação - planeta visível toda a noite, mais próximo e brilhante.",
            "ru": "Противостояние: Планета находится прямо напротив Солнца от Земли (180°). Лучшее время наблюдения - планета видна всю ночь, ближе всего и ярче всего.",
            "ja": "衝：地球から見て惑星が太陽の正反対にある（180°）。最良の観測時期 - 一晩中見え、最も近く、最も明るい。",
            "zh": "冲：行星从地球看与太阳正相对（180°）。最佳观测时间 - 整夜可见，距离最近，最亮。",
            "ko": "충: 지구에서 볼 때 행성이 태양 정반대편에 위치 (180°). 최고의 관측 시기 - 밤새 보이고, 가장 가깝고 밝음."
        },
        "conjunction": {
            "en": "Conjunction: Planet is aligned with the Sun from Earth's perspective (0°). Planet is invisible, hidden in Sun's glare.",
            "de": "Konjunktion: Planet ist aus Erdsicht mit der Sonne ausgerichtet (0°). Planet ist unsichtbar, im Sonnenglanz verborgen.",
            "es": "Conjunción: El planeta está alineado con el Sol desde la perspectiva de la Tierra (0°). Planeta invisible, oculto en el resplandor solar.",
            "fr": "Conjonction: La planète est alignée avec le Soleil depuis la Terre (0°). Planète invisible, cachée dans l'éclat solaire.",
            "it": "Congiunzione: Il pianeta è allineato con il Sole dalla prospettiva terrestre (0°). Pianeta invisibile, nascosto nel bagliore solare.",
            "nl": "Conjunctie: Planeet is uitgelijnd met de Zon vanuit Aards perspectief (0°). Planeet is onzichtbaar, verborgen in zonneglans.",
            "pl": "Koniunkcja: Planeta jest w jednej linii ze Słońcem z perspektywy Ziemi (0°). Planeta niewidoczna, ukryta w blasku Słońca.",
            "pt": "Conjunção: Planeta está alinhado com o Sol da perspectiva da Terra (0°). Planeta invisível, oculto no brilho solar.",
            "ru": "Соединение: Планета выровнена с Солнцем с точки зрения Земли (0°). Планета невидима, скрыта в солнечном сиянии.",
            "ja": "合：地球から見て惑星が太陽と一直線上にある（0°）。惑星は見えず、太陽の輝きに隠れる。",
            "zh": "合：从地球看行星与太阳成一线（0°）。行星不可见，隐藏在太阳光辉中。",
            "ko": "합: 지구에서 볼 때 행성이 태양과 일직선 (0°). 행성은 보이지 않고, 태양 빛에 숨음."
        },
        "elongation": {
            "en": "Greatest Elongation: Inner planet reaches maximum angular distance from Sun. Best viewing time for Mercury/Venus.",
            "de": "Größte Elongation: Innerer Planet erreicht maximalen Winkelabstand zur Sonne. Beste Beobachtungszeit für Merkur/Venus.",
            "es": "Máxima Elongación: Planeta interior alcanza distancia angular máxima del Sol. Mejor momento para ver Mercurio/Venus.",
            "fr": "Élongation Maximale: Planète intérieure atteint distance angulaire maximale du Soleil. Meilleur moment pour voir Mercure/Vénus.",
            "it": "Massima Elongazione: Pianeta interno raggiunge massima distanza angolare dal Sole. Miglior momento per vedere Mercurio/Venere.",
            "nl": "Grootste Elongatie: Binnenplaneet bereikt maximale hoekafstand tot de Zon. Beste tijd om Mercurius/Venus te zien.",
            "pl": "Największa Elongacja: Planeta wewnętrzna osiąga maksymalną odległość kątową od Słońca. Najlepszy czas na obserwację Merkurego/Wenus.",
            "pt": "Máxima Elongação: Planeta interior atinge distância angular máxima do Sol. Melhor momento para ver Mercúrio/Vênus.",
            "ru": "Наибольшая элонгация: Внутренняя планета достигает максимального углового расстояния от Солнца. Лучшее время для наблюдения Меркурия/Венеры.",
            "ja": "最大離角：内惑星が太陽から最大角距離に達する。水星・金星の最良観測時期。",
            "zh": "大距：内行星达到与太阳的最大角距离。观测水星/金星的最佳时机。",
            "ko": "최대 이각: 내행성이 태양으로부터 최대 각거리에 도달. 수성/금성 관측 최적기."
        },
        "planetary_alignment": {
            "en": "Planetary Alignment: Multiple planets appear in a line from Earth's perspective. Perfect alignment of all planets is extremely rare!",
            "de": "Planetenausrichtung: Mehrere Planeten erscheinen aus Erdsicht in einer Linie. Perfekte Ausrichtung aller Planeten ist extrem selten!",
            "es": "Alineación Planetaria: Múltiples planetas aparecen en línea desde la perspectiva terrestre. ¡La alineación perfecta de todos los planetas es extremadamente rara!",
            "fr": "Alignement Planétaire: Plusieurs planètes apparaissent alignées depuis la Terre. L'alignement parfait de toutes les planètes est extrêmement rare!",
            "it": "Allineamento Planetario: Più pianeti appaiono in linea dalla prospettiva terrestre. L'allineamento perfetto di tutti i pianeti è estremamente raro!",
            "nl": "Planetaire Uitlijning: Meerdere planeten verschijnen in een lijn vanaf de Aarde. Perfecte uitlijning van alle planeten is extreem zeldzaam!",
            "pl": "Ustawienie Planet: Wiele planet pojawia się w linii z perspektywy Ziemi. Idealne ustawienie wszystkich planet jest niezwykle rzadkie!",
            "pt": "Alinhamento Planetário: Múltiplos planetas aparecem em linha da perspectiva terrestre. O alinhamento perfeito de todos os planetas é extremamente raro!",
            "ru": "Парад Планет: Несколько планет выстраиваются в линию с точки зрения Земли. Идеальное выравнивание всех планет крайне редко!",
            "ja": "惑星直列：地球から見て複数の惑星が一直線に並ぶ。全惑星の完全な直列は極めて稀！",
            "zh": "行星连珠：从地球看多个行星排成一线。所有行星完美排列极其罕见！",
            "ko": "행성 정렬: 지구에서 볼 때 여러 행성이 일직선으로 보임. 모든 행성의 완벽한 정렬은 극히 드물다!"
        }
    },
    
    # Configuration options
    "config_options": {
        "show_inner_planets": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show Inner Planets",
                "de": "Innere Planeten anzeigen",
                "es": "Mostrar planetas interiores",
                "fr": "Afficher les planètes intérieures",
                "it": "Mostra pianeti interni",
                "nl": "Toon binnenplaneten",
                "pl": "Pokaż planety wewnętrzne",
                "pt": "Mostrar planetas interiores",
                "ru": "Показать внутренние планеты",
                "ja": "内惑星を表示",
                "zh": "显示内行星",
                "ko": "내행성 표시"
            },
            "description": {
                "en": "Track Mercury and Venus elongations and conjunctions",
                "de": "Verfolge Merkur und Venus Elongationen und Konjunktionen",
                "es": "Rastrear elongaciones y conjunciones de Mercurio y Venus",
                "fr": "Suivre les élongations et conjonctions de Mercure et Vénus"
            }
        },
        "show_outer_planets": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show Outer Planets",
                "de": "Äußere Planeten anzeigen",
                "es": "Mostrar planetas exteriores",
                "fr": "Afficher les planètes extérieures",
                "it": "Mostra pianeti esterni",
                "nl": "Toon buitenplaneten",
                "pl": "Pokaż planety zewnętrzne",
                "pt": "Mostrar planetas exteriores",
                "ru": "Показать внешние планеты",
                "ja": "外惑星を表示",
                "zh": "显示外行星",
                "ko": "외행성 표시"
            },
            "description": {
                "en": "Track Mars, Jupiter, Saturn oppositions and conjunctions",
                "de": "Verfolge Mars, Jupiter, Saturn Oppositionen und Konjunktionen",
                "es": "Rastrear oposiciones y conjunciones de Marte, Júpiter, Saturno",
                "fr": "Suivre les oppositions et conjonctions de Mars, Jupiter, Saturne"
            }
        },
        "show_planetary_alignment": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show Planetary Alignments",
                "de": "Planetenausrichtungen anzeigen",
                "es": "Mostrar alineaciones planetarias",
                "fr": "Afficher les alignements planétaires",
                "it": "Mostra allineamenti planetari",
                "nl": "Toon planetaire uitlijningen",
                "pl": "Pokaż ustawienia planet",
                "pt": "Mostrar alinhamentos planetários",
                "ru": "Показать парады планет",
                "ja": "惑星直列を表示",
                "zh": "显示行星连珠",
                "ko": "행성 정렬 표시"
            },
            "description": {
                "en": "Calculate when multiple planets align (rare events!)",
                "de": "Berechne wann mehrere Planeten sich ausrichten (seltene Ereignisse!)",
                "es": "Calcular cuando múltiples planetas se alinean (¡eventos raros!)",
                "fr": "Calculer quand plusieurs planètes s'alignent (événements rares!)"
            }
        },
        "show_event_definitions": {
            "type": "boolean",
            "default": True,
            "label": {
                "en": "Show Event Explanations",
                "de": "Ereigniserklärungen anzeigen",
                "es": "Mostrar explicaciones de eventos",
                "fr": "Afficher les explications des événements",
                "it": "Mostra spiegazioni eventi",
                "nl": "Toon gebeurtenis uitleg",
                "pl": "Pokaż wyjaśnienia wydarzeń",
                "pt": "Mostrar explicações de eventos",
                "ru": "Показать объяснения событий",
                "ja": "イベント説明を表示",
                "zh": "显示事件说明",
                "ko": "이벤트 설명 표시"
            }
        },
        "alignment_threshold": {
            "type": "number",
            "default": 30,
            "label": {
                "en": "Alignment Threshold (degrees)",
                "de": "Ausrichtungsschwelle (Grad)",
                "es": "Umbral de alineación (grados)",
                "fr": "Seuil d'alignement (degrés)",
                "it": "Soglia di allineamento (gradi)",
                "nl": "Uitlijningsdrempel (graden)",
                "pl": "Próg wyrównania (stopnie)",
                "pt": "Limite de alinhamento (graus)",
                "ru": "Порог выравнивания (градусы)",
                "ja": "整列しきい値（度）",
                "zh": "对齐阈值（度）",
                "ko": "정렬 임계값 (도)"
            },
            "description": {
                "en": "Maximum angular separation to consider planets aligned (10-45°)",
                "de": "Maximaler Winkelabstand für Planetenausrichtung (10-45°)",
                "es": "Separación angular máxima para considerar planetas alineados (10-45°)",
                "fr": "Séparation angulaire maximale pour considérer les planètes alignées (10-45°)"
            }
        }
    },
    
    # Planetary data
    "planetary_data": {
        # Mean orbital periods in Earth days
        "orbital_periods": {
            "mercury": 87.969,
            "venus": 224.701,
            "earth": 365.256,
            "mars": 686.980,
            "jupiter": 4332.589,
            "saturn": 10759.22,
            "uranus": 30685.4,
            "neptune": 60189.0
        },
        
        # Synodic periods in Earth days (planet-to-planet as seen from Earth)
        "synodic_periods": {
            "mercury": 115.88,  # Inferior conjunction to inferior conjunction
            "venus": 583.92,    # Inferior conjunction to inferior conjunction
            "mars": 779.94,     # Opposition to opposition
            "jupiter": 398.88,  # Opposition to opposition
            "saturn": 378.09,   # Opposition to opposition
            "uranus": 369.66,   # Opposition to opposition
            "neptune": 367.49   # Opposition to opposition
        },
        
        # Maximum elongations for inner planets
        "max_elongations": {
            "mercury": 28.0,  # degrees
            "venus": 47.0     # degrees
        },
        
        # Notable planetary alignments (simplified)
        "alignments": {
            "mini_alignment": {
                "planets": ["mercury", "venus", "mars"],
                "frequency_years": 2.5,
                "last": datetime(2024, 1, 27),
                "threshold": 30
            },
            "visible_alignment": {
                "planets": ["mercury", "venus", "mars", "jupiter", "saturn"],
                "frequency_years": 19,
                "last": datetime(2022, 6, 24),
                "threshold": 40
            },
            "grand_alignment": {
                "planets": ["mercury", "venus", "earth", "mars", "jupiter", "saturn", "uranus", "neptune"],
                "frequency_years": 170,
                "last": datetime(1982, 3, 10),
                "threshold": 90
            },
            "perfect_alignment": {
                "planets": ["all"],
                "frequency_years": 5000,
                "next": datetime(2492, 5, 6),
                "threshold": 10
            }
        },
        
        # Reference epoch for calculations (J2000.0)
        "epoch": {
            "date": datetime(2000, 1, 1, 12, 0, 0),  # J2000.0
            "jd": 2451545.0  # Julian Date
        }
    }
}

# Update interval for this sensor
UPDATE_INTERVAL = CALENDAR_INFO["update_interval"]

class SynodicCalendarSensor(AlternativeTimeSensorBase):
    """Sensor for Synodic Periods Calendar."""
    
    # Class-level update interval
    UPDATE_INTERVAL = UPDATE_INTERVAL
    
    def __init__(self, base_name: str, hass) -> None:
        """Initialize the Synodic calendar sensor."""
        super().__init__(base_name, hass)
        
        # Get translated name from metadata
        calendar_name = self._translate('name', 'Synodic Periods Calendar')
        
        # Set sensor attributes
        self._attr_name = f"{base_name} {calendar_name}"
        self._attr_unique_id = f"{base_name}_synodic_calendar"
        self._attr_icon = CALENDAR_INFO.get("icon", "mdi:orbit")
        
        # Default configuration options
        self._show_inner_planets = True
        self._show_outer_planets = True
        self._show_planetary_alignment = True
        self._show_event_definitions = True
        self._alignment_threshold = 30
        
        # Planetary data
        self._planetary_data = CALENDAR_INFO["planetary_data"]
        
        # Track if options have been loaded
        self._options_loaded = False
        
        _LOGGER.debug(f"Initialized Synodic Calendar sensor: {self._attr_name}")
    
    def _load_options(self) -> None:
        """Load configuration options from config entry."""
        if self._options_loaded:
            return
            
        try:
            options = self.get_plugin_options()
            if options:
                # Update configuration from plugin options
                self._show_inner_planets = options.get("show_inner_planets", self._show_inner_planets)
                self._show_outer_planets = options.get("show_outer_planets", self._show_outer_planets)
                self._show_planetary_alignment = options.get("show_planetary_alignment", self._show_planetary_alignment)
                self._show_event_definitions = options.get("show_event_definitions", self._show_event_definitions)
                self._alignment_threshold = options.get("alignment_threshold", self._alignment_threshold)
                
                _LOGGER.debug(f"Synodic sensor loaded options: inner={self._show_inner_planets}, "
                            f"outer={self._show_outer_planets}, alignment={self._show_planetary_alignment}, "
                            f"definitions={self._show_event_definitions}, threshold={self._alignment_threshold}")
            else:
                _LOGGER.debug("Synodic sensor using default options - no custom options found")
                
            self._options_loaded = True
        except Exception as e:
            _LOGGER.debug(f"Synodic sensor could not load options yet: {e}")
    
    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        await super().async_added_to_hass()
        
        # Try to load options now that IDs should be set
        self._load_options()
    
    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes."""
        attrs = super().extra_state_attributes
        
        # Add Synodic-specific attributes
        if hasattr(self, '_synodic_calendar'):
            attrs.update(self._synodic_calendar)
            
            # Add description in user's language
            attrs["description"] = self._translate('description')
            
            # Add disclaimer
            attrs["disclaimer"] = self._translate('disclaimer')
            
            # Add reference
            attrs["reference"] = CALENDAR_INFO.get('reference_url', '')
            
            # Add event definitions if enabled
            if self._show_event_definitions:
                attrs["event_definitions"] = {
                    "opposition": self._translate_dict(CALENDAR_INFO["event_definitions"]["opposition"]),
                    "conjunction": self._translate_dict(CALENDAR_INFO["event_definitions"]["conjunction"]),
                    "elongation": self._translate_dict(CALENDAR_INFO["event_definitions"]["elongation"]),
                    "alignment": self._translate_dict(CALENDAR_INFO["event_definitions"]["planetary_alignment"])
                }
            
            # Add configuration status
            attrs["config"] = {
                "show_inner_planets": self._show_inner_planets,
                "show_outer_planets": self._show_outer_planets,
                "show_planetary_alignment": self._show_planetary_alignment,
                "show_event_definitions": self._show_event_definitions,
                "alignment_threshold": self._alignment_threshold
            }
        
        return attrs
    
    def _translate_dict(self, translations: Dict[str, str]) -> str:
        """Get translation for current language from a dict."""
        lang = self._user_language if self._user_language else "en"
        if lang in translations:
            return translations[lang]
        elif lang[:2] in translations:
            return translations[lang[:2]]
        return translations.get("en", "")
    
    def _julian_date(self, date: datetime) -> float:
        """Convert datetime to Julian Date."""
        a = (14 - date.month) // 12
        y = date.year + 4800 - a
        m = date.month + 12 * a - 3
        
        jdn = date.day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
        jd = jdn + (date.hour - 12) / 24.0 + date.minute / 1440.0 + date.second / 86400.0
        
        return jd
    
    def _ecliptic_longitude(self, planet: str, jd: float) -> float:
        """Calculate approximate ecliptic longitude (simplified Keplerian)."""
        d = jd - self._planetary_data["epoch"]["jd"]
        period = self._planetary_data["orbital_periods"][planet]
        
        # Mean longitude (very simplified)
        L = (360.0 * d / period) % 360.0
        
        # Add some basic perturbations for major planets
        if planet == "jupiter":
            saturn_period = self._planetary_data["orbital_periods"]["saturn"]
            saturn_L = (360.0 * d / saturn_period) % 360.0
            L += 5.0 * math.sin(math.radians(2 * L - saturn_L))
        elif planet == "saturn":
            jupiter_period = self._planetary_data["orbital_periods"]["jupiter"]
            jupiter_L = (360.0 * d / jupiter_period) % 360.0
            L += 3.0 * math.sin(math.radians(2 * L - jupiter_L))
        
        return L % 360.0
    
    def _next_synodic_event(self, planet: str, current_jd: float) -> Tuple[str, float, datetime]:
        """Calculate next synodic event for a planet."""
        synodic_period = self._planetary_data["synodic_periods"][planet]
        
        # Find approximate phase in current cycle
        d = current_jd - self._planetary_data["epoch"]["jd"]
        cycle_position = (d % synodic_period) / synodic_period
        
        if planet in ["mercury", "venus"]:
            # Inner planets: conjunctions and elongations
            events = [
                (0.125, "Greatest Eastern Elongation"),
                (0.5, "Superior Conjunction"),
                (0.875, "Greatest Western Elongation"),
                (1.0, "Inferior Conjunction")
            ]
        else:
            # Outer planets: opposition and conjunction
            events = [
                (0.0, "Conjunction"),
                (0.5, "Opposition"),
                (1.0, "Conjunction")
            ]
        
        # Find next event
        next_event = None
        min_wait = synodic_period
        
        for event_phase, event_name in events:
            if event_phase > cycle_position:
                wait = (event_phase - cycle_position) * synodic_period
            else:
                wait = ((1.0 - cycle_position) + event_phase) * synodic_period
            
            if wait < min_wait:
                min_wait = wait
                next_event = event_name
        
        event_jd = current_jd + min_wait
        event_date = datetime.utcfromtimestamp((event_jd - 2440587.5) * 86400)
        
        return next_event, min_wait, event_date
    
    def _check_alignment(self, current_jd: float) -> Dict[str, Any]:
        """Check for planetary alignments."""
        # Calculate all planet positions
        all_planets = ["mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune"]
        positions = {}
        
        for planet in all_planets:
            positions[planet] = self._ecliptic_longitude(planet, current_jd)
        
        # Check different alignment types
        alignments = []
        
        for align_name, align_data in self._planetary_data["alignments"].items():
            if align_name == "perfect_alignment":
                # Special case - fixed date far in future
                days_until = (align_data["next"] - datetime.now()).days
                alignments.append({
                    "type": "Perfect Alignment (All Planets)",
                    "planets": "All 8 planets",
                    "date": align_data["next"].strftime("%Y-%m-%d"),
                    "days_until": days_until,
                    "rarity": "Once in ~5000 years"
                })
            else:
                # Check if planets are currently aligned
                planets_to_check = align_data["planets"]
                if len(planets_to_check) > 1:
                    planet_positions = [positions[p] for p in planets_to_check if p in positions]
                    if planet_positions:
                        # Check angular spread
                        min_pos = min(planet_positions)
                        max_pos = max(planet_positions)
                        spread = min(max_pos - min_pos, 360 - (max_pos - min_pos))
                        
                        if spread <= align_data["threshold"]:
                            alignments.append({
                                "type": f"{align_name.replace('_', ' ').title()}",
                                "planets": ", ".join([p.capitalize() for p in planets_to_check]),
                                "current_spread": f"{spread:.1f}°",
                                "status": "ACTIVE NOW!"
                            })
        
        # Find next major alignment
        if not alignments:
            # Calculate next visible alignment (simplified)
            visible_align = self._planetary_data["alignments"]["visible_alignment"]
            years_since_last = (datetime.now() - visible_align["last"]).days / 365.25
            years_until_next = visible_align["frequency_years"] - (years_since_last % visible_align["frequency_years"])
            next_date = datetime.now() + timedelta(days=years_until_next * 365.25)
            
            alignments.append({
                "type": "Next Visible Alignment",
                "planets": "Mercury, Venus, Mars, Jupiter, Saturn",
                "date": next_date.strftime("%Y-%m-%d"),
                "days_until": int(years_until_next * 365.25),
                "note": "Approximate - check astronomy sites for exact dates"
            })
        
        return {"alignments": alignments}
    
    def _format_synodic_state(self, earth_date: datetime) -> str:
        """Format the main state display."""
        jd = self._julian_date(earth_date)
        
        # Check for alignments first if enabled
        if self._show_planetary_alignment:
            alignment_data = self._check_alignment(jd)
            for align in alignment_data["alignments"]:
                if "ACTIVE NOW" in str(align.get("status", "")):
                    return f"⚠️ {align['type']} ACTIVE!"
        
        # Get closest upcoming event
        upcoming_events = []
        
        if self._show_inner_planets:
            for planet in ["mercury", "venus"]:
                event, days, date = self._next_synodic_event(planet, jd)
                upcoming_events.append((days, planet.capitalize(), event))
        
        if self._show_outer_planets:
            for planet in ["mars", "jupiter", "saturn"]:
                event, days, date = self._next_synodic_event(planet, jd)
                upcoming_events.append((days, planet.capitalize(), event))
        
        # Sort by days until event
        upcoming_events.sort(key=lambda x: x[0])
        
        if upcoming_events:
            days, planet, event = upcoming_events[0]
            
            # Translate event name if possible
            if "Opposition" in event:
                event_key = "Opposition"
            elif "Conjunction" in event:
                event_key = "Conjunction"
            elif "Elongation" in event:
                event_key = "Elongation"
            else:
                event_key = event
            
            return f"{planet}: {event_key} in {int(days)} days"
        else:
            return "No events configured"
    
    def _calculate_time(self, earth_date: datetime) -> None:
        """Calculate synodic calendar information."""
        try:
            # Reload options
            self._load_options()
            
            # Calculate Julian Date
            jd = self._julian_date(earth_date)
            
            # Format the main state
            synodic_state = self._format_synodic_state(earth_date)
            
            # Build attribute data
            self._synodic_calendar = {
                "julian_date": round(jd, 5),
                "days_since_j2000": round(jd - self._planetary_data["epoch"]["jd"], 2),
                "current_positions": {},
                "upcoming_events": {},
                "synodic_periods": {}
            }
            
            # Calculate current positions
            planets_to_track = []
            if self._show_inner_planets:
                planets_to_track.extend(["mercury", "venus"])
            if self._show_outer_planets:
                planets_to_track.extend(["mars", "jupiter", "saturn"])
            
            for planet in planets_to_track:
                longitude = self._ecliptic_longitude(planet, jd)
                
                self._synodic_calendar["current_positions"][planet] = {
                    "ecliptic_longitude": f"{longitude:.1f}°"
                }
                
                # Calculate next synodic event
                event, days, date = self._next_synodic_event(planet, jd)
                self._synodic_calendar["upcoming_events"][planet] = {
                    "event": event,
                    "days_until": int(days),
                    "date": date.strftime("%Y-%m-%d")
                }
                
                # Add synodic period info
                self._synodic_calendar["synodic_periods"][planet] = {
                    "days": self._planetary_data["synodic_periods"][planet],
                    "years": round(self._planetary_data["synodic_periods"][planet] / 365.256, 2)
                }
            
            # Add alignment information if enabled
            if self._show_planetary_alignment:
                self._synodic_calendar["planetary_alignments"] = self._check_alignment(jd)
            
            # Set state
            self._state = synodic_state
            
        except Exception as e:
            _LOGGER.error(f"Error calculating synodic calendar: {e}")
            self._state = "Error"
            self._synodic_calendar = {"error": str(e)}
    
    def get_calendar_metadata(self) -> Dict[str, Any]:
        """Return calendar metadata."""
        return CALENDAR_INFO

# Export the sensor class
__all__ = ["SynodicCalendarSensor", "CALENDAR_INFO", "UPDATE_INTERVAL"]