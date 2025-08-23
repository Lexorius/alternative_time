"""
Battlestar Galactica Calendar System for Home Assistant
Includes Colonial Calendar and other BSG time systems
"""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional
import logging
from ..sensor import AlternativeTimeSensorBase

_LOGGER = logging.getLogger(__name__)

CALENDAR_INFO = {
    'id': 'battlestar_galactica',
    'name': {
        'en': 'Battlestar Galactica Calendar',
        'de': 'Battlestar Galactica Kalender',
        'es': 'Calendario de Battlestar Galactica',
        'fr': 'Calendrier Battlestar Galactica',
        'it': 'Calendario di Battlestar Galactica',
        'nl': 'Battlestar Galactica Kalender',
        'pl': 'Kalendarz Battlestar Galactica',
        'pt': 'Calendário Battlestar Galactica',
        'ru': 'Календарь Звездный крейсер Галактика',
        'ja': 'バトルスター・ギャラクティカ暦',
        'zh': '太空堡垒卡拉狄加日历',
        'ko': '배틀스타 갈락티카 달력'
    },
    'description': {
        'en': 'Time systems from the Battlestar Galactica universe, including the Colonial Calendar used by the Twelve Colonies of Kobol',
        'de': 'Zeitsysteme aus dem Battlestar Galactica Universum, einschließlich des Kolonialkalenders der Zwölf Kolonien von Kobol',
        'es': 'Sistemas de tiempo del universo Battlestar Galactica, incluyendo el Calendario Colonial usado por las Doce Colonias de Kobol',
        'fr': "Systèmes temporels de l'univers Battlestar Galactica, y compris le calendrier colonial utilisé par les Douze Colonies de Kobol",
        'it': "Sistemi temporali dell'universo Battlestar Galactica, incluso il Calendario Coloniale usato dalle Dodici Colonie di Kobol",
        'nl': 'Tijdsystemen uit het Battlestar Galactica universum, inclusief de Koloniale Kalender gebruikt door de Twaalf Koloniën van Kobol',
        'pl': 'Systemy czasu z uniwersum Battlestar Galactica, w tym Kalendarz Kolonialny używany przez Dwanaście Kolonii Kobol',
        'pt': 'Sistemas de tempo do universo Battlestar Galactica, incluindo o Calendário Colonial usado pelas Doze Colônias de Kobol',
        'ru': 'Системы времени из вселенной Звездный крейсер Галактика, включая Колониальный календарь Двенадцати Колоний Кобола',
        'ja': 'バトルスター・ギャラクティカの宇宙の時間システム、コボルの12コロニーが使用する植民地暦を含む',
        'zh': '太空堡垒卡拉狄加宇宙的时间系统，包括科博尔十二殖民地使用的殖民地日历',
        'ko': '배틀스타 갈락티카 우주의 시간 시스템, 코볼의 12개 식민지가 사용하는 식민지 달력 포함'
    },
    'icon': 'mdi:rocket-launch',
    'category': 'scifi',
    'accuracy': 'fictional',
    'version': '1.0.0',
    'author': 'Alternative Time Systems',
    'update_interval': 3600,  # Update every hour
    
    # Colonial Calendar Months (21 days each for standard months)
    'months': {
        'colonial': [
            {
                'name': {
                    'en': 'Caprica',
                    'de': 'Caprica',
                    'es': 'Caprica',
                    'fr': 'Caprica',
                    'it': 'Caprica',
                    'nl': 'Caprica',
                    'pl': 'Caprica',
                    'pt': 'Caprica',
                    'ru': 'Каприка',
                    'ja': 'カプリカ',
                    'zh': '卡布里卡',
                    'ko': '카프리카'
                },
                'days': 28
            },
            {
                'name': {
                    'en': 'Aquaria',
                    'de': 'Aquaria',
                    'es': 'Aquaria',
                    'fr': 'Aquaria',
                    'it': 'Aquaria',
                    'nl': 'Aquaria',
                    'pl': 'Aquaria',
                    'pt': 'Aquaria',
                    'ru': 'Акуария',
                    'ja': 'アクアリア',
                    'zh': '水瓶座',
                    'ko': '아쿠아리아'
                },
                'days': 28
            },
            {
                'name': {
                    'en': 'Picon',
                    'de': 'Picon',
                    'es': 'Picon',
                    'fr': 'Picon',
                    'it': 'Picon',
                    'nl': 'Picon',
                    'pl': 'Picon',
                    'pt': 'Picon',
                    'ru': 'Пикон',
                    'ja': 'パイコン',
                    'zh': '派康',
                    'ko': '파이콘'
                },
                'days': 28
            },
            {
                'name': {
                    'en': 'Aerilon',
                    'de': 'Aerilon',
                    'es': 'Aerilon',
                    'fr': 'Aerilon',
                    'it': 'Aerilon',
                    'nl': 'Aerilon',
                    'pl': 'Aerilon',
                    'pt': 'Aerilon',
                    'ru': 'Аэрилон',
                    'ja': 'エアリロン',
                    'zh': '艾瑞隆',
                    'ko': '에어릴론'
                },
                'days': 28
            },
            {
                'name': {
                    'en': 'Tauron',
                    'de': 'Tauron',
                    'es': 'Tauron',
                    'fr': 'Tauron',
                    'it': 'Tauron',
                    'nl': 'Tauron',
                    'pl': 'Tauron',
                    'pt': 'Tauron',
                    'ru': 'Таурон',
                    'ja': 'タウロン',
                    'zh': '金牛座',
                    'ko': '타우론'
                },
                'days': 28
            },
            {
                'name': {
                    'en': 'Gemenon',
                    'de': 'Gemenon',
                    'es': 'Gemenon',
                    'fr': 'Gemenon',
                    'it': 'Gemenon',
                    'nl': 'Gemenon',
                    'pl': 'Gemenon',
                    'pt': 'Gemenon',
                    'ru': 'Геменон',
                    'ja': 'ジェメノン',
                    'zh': '双子座',
                    'ko': '제메논'
                },
                'days': 28
            },
            {
                'name': {
                    'en': 'Canceron',
                    'de': 'Canceron',
                    'es': 'Canceron',
                    'fr': 'Canceron',
                    'it': 'Canceron',
                    'nl': 'Canceron',
                    'pl': 'Canceron',
                    'pt': 'Canceron',
                    'ru': 'Кансерон',
                    'ja': 'キャンセロン',
                    'zh': '巨蟹座',
                    'ko': '캔서론'
                },
                'days': 28
            },
            {
                'name': {
                    'en': 'Leonis',
                    'de': 'Leonis',
                    'es': 'Leonis',
                    'fr': 'Leonis',
                    'it': 'Leonis',
                    'nl': 'Leonis',
                    'pl': 'Leonis',
                    'pt': 'Leonis',
                    'ru': 'Леонис',
                    'ja': 'レオニス',
                    'zh': '狮子座',
                    'ko': '레오니스'
                },
                'days': 28
            },
            {
                'name': {
                    'en': 'Virgon',
                    'de': 'Virgon',
                    'es': 'Virgon',
                    'fr': 'Virgon',
                    'it': 'Virgon',
                    'nl': 'Virgon',
                    'pl': 'Virgon',
                    'pt': 'Virgon',
                    'ru': 'Виргон',
                    'ja': 'ヴァーゴン',
                    'zh': '处女座',
                    'ko': '버곤'
                },
                'days': 28
            },
            {
                'name': {
                    'en': 'Libran',
                    'de': 'Libran',
                    'es': 'Libran',
                    'fr': 'Libran',
                    'it': 'Libran',
                    'nl': 'Libran',
                    'pl': 'Libran',
                    'pt': 'Libran',
                    'ru': 'Либран',
                    'ja': 'リブラン',
                    'zh': '天秤座',
                    'ko': '리브란'
                },
                'days': 28
            },
            {
                'name': {
                    'en': 'Scorpia',
                    'de': 'Scorpia',
                    'es': 'Scorpia',
                    'fr': 'Scorpia',
                    'it': 'Scorpia',
                    'nl': 'Scorpia',
                    'pl': 'Scorpia',
                    'pt': 'Scorpia',
                    'ru': 'Скорпия',
                    'ja': 'スコーピア',
                    'zh': '天蝎座',
                    'ko': '스코피아'
                },
                'days': 28
            },
            {
                'name': {
                    'en': 'Sagittaron',
                    'de': 'Sagittaron',
                    'es': 'Sagittaron',
                    'fr': 'Sagittaron',
                    'it': 'Sagittaron',
                    'nl': 'Sagittaron',
                    'pl': 'Sagittaron',
                    'pt': 'Sagittaron',
                    'ru': 'Сагиттарон',
                    'ja': 'サジタロン',
                    'zh': '射手座',
                    'ko': '사지타론'
                },
                'days': 28
            },
            {
                'name': {
                    'en': 'Colonial Unity',
                    'de': 'Koloniale Einheit',
                    'es': 'Unidad Colonial',
                    'fr': 'Unité Coloniale',
                    'it': 'Unità Coloniale',
                    'nl': 'Koloniale Eenheid',
                    'pl': 'Jedność Kolonialna',
                    'pt': 'Unidade Colonial',
                    'ru': 'Колониальное Единство',
                    'ja': '植民地統一',
                    'zh': '殖民地团结',
                    'ko': '식민지 통합'
                },
                'days': 29  # Extra day for leap years
            }
        ]
    },
    
    'weekdays': {
        'colonial': [
            {
                'en': 'Kronos',
                'de': 'Kronos',
                'es': 'Kronos',
                'fr': 'Kronos',
                'it': 'Kronos',
                'nl': 'Kronos',
                'pl': 'Kronos',
                'pt': 'Kronos',
                'ru': 'Кронос',
                'ja': 'クロノス',
                'zh': '克洛诺斯',
                'ko': '크로노스'
            },
            {
                'en': 'Zeus',
                'de': 'Zeus',
                'es': 'Zeus',
                'fr': 'Zeus',
                'it': 'Zeus',
                'nl': 'Zeus',
                'pl': 'Zeus',
                'pt': 'Zeus',
                'ru': 'Зевс',
                'ja': 'ゼウス',
                'zh': '宙斯',
                'ko': '제우스'
            },
            {
                'en': 'Ares',
                'de': 'Ares',
                'es': 'Ares',
                'fr': 'Arès',
                'it': 'Ares',
                'nl': 'Ares',
                'pl': 'Ares',
                'pt': 'Ares',
                'ru': 'Арес',
                'ja': 'アレス',
                'zh': '阿瑞斯',
                'ko': '아레스'
            },
            {
                'en': 'Hermes',
                'de': 'Hermes',
                'es': 'Hermes',
                'fr': 'Hermès',
                'it': 'Hermes',
                'nl': 'Hermes',
                'pl': 'Hermes',
                'pt': 'Hermes',
                'ru': 'Гермес',
                'ja': 'ヘルメス',
                'zh': '赫尔墨斯',
                'ko': '헤르메스'
            },
            {
                'en': 'Apollo',
                'de': 'Apollo',
                'es': 'Apolo',
                'fr': 'Apollon',
                'it': 'Apollo',
                'nl': 'Apollo',
                'pl': 'Apollo',
                'pt': 'Apolo',
                'ru': 'Аполлон',
                'ja': 'アポロ',
                'zh': '阿波罗',
                'ko': '아폴로'
            },
            {
                'en': 'Aphrodite',
                'de': 'Aphrodite',
                'es': 'Afrodita',
                'fr': 'Aphrodite',
                'it': 'Afrodite',
                'nl': 'Aphrodite',
                'pl': 'Afrodyta',
                'pt': 'Afrodite',
                'ru': 'Афродита',
                'ja': 'アフロディーテ',
                'zh': '阿芙罗狄蒂',
                'ko': '아프로디테'
            },
            {
                'en': 'Hestia',
                'de': 'Hestia',
                'es': 'Hestia',
                'fr': 'Hestia',
                'it': 'Estia',
                'nl': 'Hestia',
                'pl': 'Hestia',
                'pt': 'Héstia',
                'ru': 'Гестия',
                'ja': 'ヘスティア',
                'zh': '赫斯提亚',
                'ko': '헤스티아'
            }
        ]
    },
    
    'special_dates': [
        {
            'name': {
                'en': 'Colonial Day',
                'de': 'Kolonialtag',
                'es': 'Día Colonial',
                'fr': 'Jour Colonial',
                'it': 'Giorno Coloniale',
                'nl': 'Koloniale Dag',
                'pl': 'Dzień Kolonialny',
                'pt': 'Dia Colonial',
                'ru': 'День Колоний',
                'ja': '植民地記念日',
                'zh': '殖民地日',
                'ko': '식민지의 날'
            },
            'description': {
                'en': 'Anniversary of the signing of the Articles of Colonization',
                'de': 'Jahrestag der Unterzeichnung der Kolonisationsartikel',
                'es': 'Aniversario de la firma de los Artículos de Colonización',
                'fr': 'Anniversaire de la signature des Articles de Colonisation',
                'it': 'Anniversario della firma degli Articoli di Colonizzazione',
                'nl': 'Verjaardag van de ondertekening van de Kolonisatie Artikelen',
                'pl': 'Rocznica podpisania Artykułów Kolonizacji',
                'pt': 'Aniversário da assinatura dos Artigos de Colonização',
                'ru': 'Годовщина подписания Статей колонизации',
                'ja': '植民地化条項署名記念日',
                'zh': '殖民条款签署纪念日',
                'ko': '식민지 조항 서명 기념일'
            },
            'month': 3,  # Month of Picon
            'day': 15
        },
        {
            'name': {
                'en': 'Armistice Day',
                'de': 'Waffenstillstandstag',
                'es': 'Día del Armisticio',
                'fr': "Jour de l'Armistice",
                'it': "Giorno dell'Armistizio",
                'nl': 'Wapenstilstandsdag',
                'pl': 'Dzień Rozejmu',
                'pt': 'Dia do Armistício',
                'ru': 'День Перемирия',
                'ja': '休戦記念日',
                'zh': '停战日',
                'ko': '휴전 기념일'
            },
            'description': {
                'en': 'End of the First Cylon War',
                'de': 'Ende des Ersten Zylonenkrieges',
                'es': 'Fin de la Primera Guerra Cylon',
                'fr': 'Fin de la Première Guerre Cylon',
                'it': 'Fine della Prima Guerra Cylon',
                'nl': 'Einde van de Eerste Cylon Oorlog',
                'pl': 'Koniec Pierwszej Wojny Cylońskiej',
                'pt': 'Fim da Primeira Guerra Cylon',
                'ru': 'Конец Первой войны с Сайлонами',
                'ja': '第一次サイロン戦争終結',
                'zh': '第一次赛昂战争结束',
                'ko': '제1차 사일론 전쟁 종료'
            },
            'month': 9,  # Month of Virgon
            'day': 1
        }
    ],
    
    'plugin_options': {
        'calendar_type': {
            'type': 'select',
            'default': 'colonial',
            'options': {
                'colonial': {
                    'en': 'Colonial Calendar',
                    'de': 'Kolonialkalender',
                    'es': 'Calendario Colonial',
                    'fr': 'Calendrier Colonial',
                    'it': 'Calendario Coloniale',
                    'nl': 'Koloniale Kalender',
                    'pl': 'Kalendarz Kolonialny',
                    'pt': 'Calendário Colonial',
                    'ru': 'Колониальный календарь',
                    'ja': '植民地暦',
                    'zh': '殖民地日历',
                    'ko': '식민지 달력'
                },
                'cylon': {
                    'en': 'Cylon Time',
                    'de': 'Zylonen-Zeit',
                    'es': 'Tiempo Cylon',
                    'fr': 'Temps Cylon',
                    'it': 'Tempo Cylon',
                    'nl': 'Cylon Tijd',
                    'pl': 'Czas Cylonów',
                    'pt': 'Tempo Cylon',
                    'ru': 'Время Сайлонов',
                    'ja': 'サイロン時間',
                    'zh': '赛昂时间',
                    'ko': '사일론 시간'
                },
                'military': {
                    'en': 'Colonial Military Time',
                    'de': 'Koloniale Militärzeit',
                    'es': 'Hora Militar Colonial',
                    'fr': 'Heure Militaire Coloniale',
                    'it': 'Ora Militare Coloniale',
                    'nl': 'Koloniale Militaire Tijd',
                    'pl': 'Kolonialny Czas Wojskowy',
                    'pt': 'Hora Militar Colonial',
                    'ru': 'Колониальное военное время',
                    'ja': '植民地軍事時間',
                    'zh': '殖民地军事时间',
                    'ko': '식민지 군사 시간'
                }
            },
            'label': {
                'en': 'Calendar Type',
                'de': 'Kalendertyp',
                'es': 'Tipo de Calendario',
                'fr': 'Type de Calendrier',
                'it': 'Tipo di Calendario',
                'nl': 'Kalendertype',
                'pl': 'Typ Kalendarza',
                'pt': 'Tipo de Calendário',
                'ru': 'Тип календаря',
                'ja': 'カレンダータイプ',
                'zh': '日历类型',
                'ko': '달력 유형'
            }
        },
        'show_yahren': {
            'type': 'boolean',
            'default': True,
            'label': {
                'en': 'Show Yahren (Year)',
                'de': 'Zeige Yahren (Jahr)',
                'es': 'Mostrar Yahren (Año)',
                'fr': 'Afficher Yahren (Année)',
                'it': 'Mostra Yahren (Anno)',
                'nl': 'Toon Yahren (Jaar)',
                'pl': 'Pokaż Yahren (Rok)',
                'pt': 'Mostrar Yahren (Ano)',
                'ru': 'Показать Яхрен (Год)',
                'ja': 'ヤーレン（年）を表示',
                'zh': '显示亚伦（年）',
                'ko': '야렌(년) 표시'
            }
        },
        'show_sectare': {
            'type': 'boolean',
            'default': False,
            'label': {
                'en': 'Show Sectare (Month)',
                'de': 'Zeige Sectare (Monat)',
                'es': 'Mostrar Sectare (Mes)',
                'fr': 'Afficher Sectare (Mois)',
                'it': 'Mostra Sectare (Mese)',
                'nl': 'Toon Sectare (Maand)',
                'pl': 'Pokaż Sectare (Miesiąc)',
                'pt': 'Mostrar Sectare (Mês)',
                'ru': 'Показать Сектаре (Месяц)',
                'ja': 'セクターレ（月）を表示',
                'zh': '显示塞克塔雷（月）',
                'ko': '섹타레(월) 표시'
            }
        },
        'epoch_year': {
            'type': 'number',
            'default': 2003,
            'min': 1900,
            'max': 3000,
            'label': {
                'en': 'Epoch Year (Earth Calendar)',
                'de': 'Epochenjahr (Erdkalender)',
                'es': 'Año de Época (Calendario Terrestre)',
                'fr': 'Année Époque (Calendrier Terrestre)',
                'it': "Anno dell'Epoca (Calendario Terrestre)",
                'nl': 'Epoche Jaar (Aarde Kalender)',
                'pl': 'Rok Epoki (Kalendarz Ziemski)',
                'pt': 'Ano da Época (Calendário Terrestre)',
                'ru': 'Год эпохи (Земной календарь)',
                'ja': 'エポック年（地球暦）',
                'zh': '纪元年（地球日历）',
                'ko': '에포크 연도 (지구 달력)'
            }
        }
    }
}


class BattlestarGalacticaSensor(AlternativeTimeSensorBase):
    """Sensor for Battlestar Galactica time systems."""
    
    def __init__(self, name: str, hass):
        """Initialize the sensor."""
        super().__init__(name, hass, CALENDAR_INFO)
        self._colonial_epoch = datetime(2003, 1, 1)  # BSG Series start
        
    def calculate_time(self) -> Dict[str, Any]:
        """Calculate current Battlestar Galactica time."""
        try:
            options = self.get_plugin_options()
            calendar_type = options.get('calendar_type', 'colonial')
            show_yahren = options.get('show_yahren', True)
            show_sectare = options.get('show_sectare', False)
            epoch_year = options.get('epoch_year', 2003)
            
            # Update epoch if changed
            self._colonial_epoch = datetime(epoch_year, 1, 1)
            
            now = datetime.now()
            lang = self.get_current_language()
            
            if calendar_type == 'colonial':
                return self._calculate_colonial_calendar(now, lang, show_yahren, show_sectare)
            elif calendar_type == 'cylon':
                return self._calculate_cylon_time(now, lang)
            elif calendar_type == 'military':
                return self._calculate_military_time(now, lang)
            else:
                return self._calculate_colonial_calendar(now, lang, show_yahren, show_sectare)
                
        except Exception as e:
            _LOGGER.error(f"Error calculating BSG time: {e}")
            return {
                'date': 'Error',
                'full': 'Calculation Error',
                'details': {}
            }
    
    def _calculate_colonial_calendar(self, dt: datetime, lang: str, show_yahren: bool, show_sectare: bool) -> Dict[str, Any]:
        """Calculate Colonial Calendar date."""
        # Days since epoch
        delta = dt - self._colonial_epoch
        total_days = delta.days
        
        # Colonial year has 365 days (13 months * 28 days + 1 day)
        yahren = total_days // 365 + 1  # Year 1 starts at epoch
        day_of_yahren = total_days % 365
        
        # Find current month and day
        months = CALENDAR_INFO['months']['colonial']
        current_day = day_of_yahren
        month_idx = 0
        
        for idx, month in enumerate(months):
            if current_day < month['days']:
                month_idx = idx
                break
            current_day -= month['days']
        
        month_name = months[month_idx]['name'][lang]
        day = current_day + 1  # Days start at 1
        
        # Get weekday (7-day week)
        weekday_idx = total_days % 7
        weekday = CALENDAR_INFO['weekdays']['colonial'][weekday_idx][lang]
        
        # Build display strings
        date_parts = []
        if show_yahren:
            yahren_label = {
                'en': f'Yahren {yahren}',
                'de': f'Yahren {yahren}',
                'es': f'Yahren {yahren}',
                'fr': f'Yahren {yahren}',
                'it': f'Yahren {yahren}',
                'nl': f'Yahren {yahren}',
                'pl': f'Yahren {yahren}',
                'pt': f'Yahren {yahren}',
                'ru': f'Яхрен {yahren}',
                'ja': f'ヤーレン {yahren}',
                'zh': f'亚伦 {yahren}',
                'ko': f'야렌 {yahren}'
            }
            date_parts.append(yahren_label.get(lang, f'Yahren {yahren}'))
        
        if show_sectare:
            sectare_label = {
                'en': f'Sectare {month_idx + 1}',
                'de': f'Sectare {month_idx + 1}',
                'es': f'Sectare {month_idx + 1}',
                'fr': f'Sectare {month_idx + 1}',
                'it': f'Sectare {month_idx + 1}',
                'nl': f'Sectare {month_idx + 1}',
                'pl': f'Sectare {month_idx + 1}',
                'pt': f'Sectare {month_idx + 1}',
                'ru': f'Сектаре {month_idx + 1}',
                'ja': f'セクターレ {month_idx + 1}',
                'zh': f'塞克塔雷 {month_idx + 1}',
                'ko': f'섹타레 {month_idx + 1}'
            }
            date_parts.append(sectare_label.get(lang, f'Sectare {month_idx + 1}'))
        
        date_parts.append(f'{weekday}, {day} {month_name}')
        
        # Check for special dates
        special_date = None
        for special in CALENDAR_INFO['special_dates']:
            if special['month'] - 1 == month_idx and special['day'] == day:
                special_date = special['name'][lang]
                break
        
        # Time calculation (using Earth hours/minutes for simplicity)
        time_str = dt.strftime('%H:%M:%S')
        
        result = {
            'date': ', '.join(date_parts),
            'full': f"{', '.join(date_parts)} {time_str}",
            'details': {
                'yahren': yahren,
                'month': month_name,
                'month_number': month_idx + 1,
                'day': day,
                'weekday': weekday,
                'time': time_str,
                'day_of_yahren': day_of_yahren + 1,
                'special_date': special_date
            }
        }
        
        if special_date:
            result['special'] = special_date
            
        return result
    
    def _calculate_cylon_time(self, dt: datetime, lang: str) -> Dict[str, Any]:
        """Calculate Cylon time (base-12 system)."""
        # Cylons use a base-12 timing system
        total_seconds = (dt.hour * 3600 + dt.minute * 60 + dt.second)
        
        # Convert to base-12 cycles (1 cycle = 7200 seconds = 2 hours)
        cycles = total_seconds / 7200
        cycle_num = int(cycles)
        cycle_fraction = cycles - cycle_num
        
        # Centon = 1/100 of a cycle
        centons = int(cycle_fraction * 100)
        
        # Micron = 1/100 of a centon
        microns = int((cycle_fraction * 100 - centons) * 100)
        
        cylon_time = f"Cycle {cycle_num:02d}:{centons:02d}:{microns:02d}"
        
        time_labels = {
            'en': cylon_time,
            'de': f"Zyklus {cycle_num:02d}:{centons:02d}:{microns:02d}",
            'es': f"Ciclo {cycle_num:02d}:{centons:02d}:{microns:02d}",
            'fr': f"Cycle {cycle_num:02d}:{centons:02d}:{microns:02d}",
            'it': f"Ciclo {cycle_num:02d}:{centons:02d}:{microns:02d}",
            'nl': f"Cyclus {cycle_num:02d}:{centons:02d}:{microns:02d}",
            'pl': f"Cykl {cycle_num:02d}:{centons:02d}:{microns:02d}",
            'pt': f"Ciclo {cycle_num:02d}:{centons:02d}:{microns:02d}",
            'ru': f"Цикл {cycle_num:02d}:{centons:02d}:{microns:02d}",
            'ja': f"サイクル {cycle_num:02d}:{centons:02d}:{microns:02d}",
            'zh': f"周期 {cycle_num:02d}:{centons:02d}:{microns:02d}",
            'ko': f"사이클 {cycle_num:02d}:{centons:02d}:{microns:02d}"
        }
        
        return {
            'date': time_labels.get(lang, cylon_time),
            'full': time_labels.get(lang, cylon_time),
            'details': {
                'cycles': cycle_num,
                'centons': centons,
                'microns': microns,
                'total_centons': cycle_num * 100 + centons
            }
        }
    
    def _calculate_military_time(self, dt: datetime, lang: str) -> Dict[str, Any]:
        """Calculate Colonial Military time format."""
        # Colonial military uses a modified 24-hour format with centons
        hours = dt.hour
        minutes = dt.minute
        seconds = dt.second
        
        # Convert minutes to centons (100 centons = 1 hour)
        centons = int((minutes * 60 + seconds) / 36)  # 3600 seconds / 100 = 36 seconds per centon
        
        military_time = f"{hours:02d}{centons:02d}"
        
        # Add callsign based on hour
        callsigns = [
            'Alpha', 'Bravo', 'Charlie', 'Delta', 'Echo', 'Foxtrot',
            'Golf', 'Hotel', 'India', 'Juliet', 'Kilo', 'Lima',
            'Mike', 'November', 'Oscar', 'Papa', 'Quebec', 'Romeo',
            'Sierra', 'Tango', 'Uniform', 'Victor', 'Whiskey', 'X-ray'
        ]
        callsign = callsigns[hours % 24]
        
        time_str = f"{military_time} {callsign}"
        
        return {
            'date': time_str,
            'full': f"Colonial Military Time: {time_str}",
            'details': {
                'hours': hours,
                'centons': centons,
                'callsign': callsign,
                'numeric': military_time
            }
        }
    
    def get_extra_state_attributes(self) -> Dict[str, Any]:
        """Return additional state attributes."""
        attrs = super().get_extra_state_attributes()
        
        # Add BSG-specific attributes
        current_time = self.calculate_time()
        details = current_time.get('details', {})
        
        if 'yahren' in details:
            attrs['yahren'] = details['yahren']
        if 'cycles' in details:
            attrs['cylon_cycles'] = details['cycles']
        if 'callsign' in details:
            attrs['military_callsign'] = details['callsign']
        if 'special_date' in details and details['special_date']:
            attrs['special_event'] = details['special_date']
            
        # Add famous BSG quotes
        quotes = [
            "So say we all!",
            "All of this has happened before, and all of it will happen again.",
            "There must be some kind of way out of here.",
            "Nothing but the rain.",
            "Grab your gun and bring the cat in.",
            "Sometimes you gotta roll the hard six.",
            "The last frakkin' airlock.",
            "By your command."
        ]
        import random
        attrs['bsg_quote'] = random.choice(quotes)
        
        return attrs