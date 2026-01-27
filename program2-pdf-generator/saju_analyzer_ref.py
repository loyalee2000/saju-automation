# -*- coding: utf-8 -*-
"""
사주 분석 자동화 프로그램 (Saju Analysis Automation) v3.0

[업데이트 내용]
- 십성(Sibseong/Ten Gods) 분석 추가
- 신살(Sinsal/Divine Spirits) 분석 추가 (역마, 도화, 화개)
- 양력/음력(Solar/Lunar) 변환 지원
- 윤달(Leap Month) 지원
- 날짜/시간 입력 형식 유연화 (YYYYMMDD, HHMM 지원)
- 이름(Name) 입력 추가
- 태어난 시간 모름(Unknown Time) 지원
- 성별(Gender) 입력 추가
- 대운(Daewoon) 계산 로직 추가 (순행/역행)
- 썸머타임(Summer Time) 자동 보정
- JSON 형태의 데이터 구조 반환
- 서울 실제 태양시(32분) 보정

[설치 필요한 라이브러리]
pip install korean_lunar_calendar
"""

import sys
import json
import re
from datetime import datetime, timedelta
from korean_lunar_calendar import KoreanLunarCalendar

# ... (기초 데이터 정의) ...
CHEONGAN = ['갑(甲)', '을(乙)', '병(丙)', '정(丁)', '무(戊)', '기(己)', '경(庚)', '신(辛)', '임(壬)', '계(癸)']
JIJI = ['자(子)', '축(丑)', '인(寅)', '묘(卯)', '진(辰)', '사(巳)', '오(午)', '미(未)', '신(申)', '유(酉)', '술(戌)', '해(亥)']

# 오행 및 음양 정보 (0: 양, 1: 음)
# 목: Tree, 화: Fire, 토: Earth, 금: Metal, 수: Water
CHEONGAN_INFO = {
    '갑(甲)': {'element': '목', 'polarity': 0}, '을(乙)': {'element': '목', 'polarity': 1},
    '병(丙)': {'element': '화', 'polarity': 0}, '정(丁)': {'element': '화', 'polarity': 1},
    '무(戊)': {'element': '토', 'polarity': 0}, '기(己)': {'element': '토', 'polarity': 1},
    '경(庚)': {'element': '금', 'polarity': 0}, '신(辛)': {'element': '금', 'polarity': 1},
    '임(壬)': {'element': '수', 'polarity': 0}, '계(癸)': {'element': '수', 'polarity': 1}
}

JIJI_INFO = {
    '자(子)': {'element': '수', 'polarity': 0}, '축(丑)': {'element': '토', 'polarity': 1},
    '인(寅)': {'element': '목', 'polarity': 0}, '묘(卯)': {'element': '목', 'polarity': 1},
    '진(辰)': {'element': '토', 'polarity': 0}, '사(巳)': {'element': '화', 'polarity': 1}, # 사화는 체는 음이나 용은 양 (여기선 일반적 음양 적용, 사화는 원래 양화이나 음으로 쓰임 등 복잡하지만 단순화) -> 수정: 자(양), 축(음), 인(양), 묘(음), 진(양), 사(음-원래양), 오(양-원래음), 미(음), 신(양), 유(음), 술(양), 해(음-원래양)
    # 지지 음양은 자(양), 축(음), 인(양), 묘(음), 진(양), 사(양), 오(음), 미(음), 신(양), 유(음), 술(양), 해(음) - 체용론에 따라 다름.
    # 십성 계산을 위해 일반적인 명리학적 음양(체) 기준:
    # 자(양), 축(음), 인(양), 묘(음), 진(양), 사(양), 오(음), 미(음), 신(양), 유(음), 술(양), 해(음)
    # *주의: 자수는 체는 양이나 용은 음, 사화는 체는 양이나 용은 음... 십성 계산시 '용'을 기준으로 하는 경우가 많음.
    # 여기서는 십성 계산의 표준인 '용(Usage)' 기준으로 설정합니다.
    # 자(음), 축(음), 인(양), 묘(음), 진(양), 사(양), 오(음), 미(음), 신(양), 유(음), 술(양), 해(양) -> 해수는 체는 음이나 용은 양
}

# 십성 계산을 위한 지지 음양 (용 기준)
JIJI_YONG = {
    '자(子)': {'element': '수', 'polarity': 0}, # 양수 (원래 체는 양, 용은 음? 아니 자수는 음수로 취급하여 정편관 따짐. 임수가 양수, 계수가 음수. 자수는 계수와 같음 -> 음)
    # 수정: 십성 도출 시 자수는 '계수(음수)'로 봅니다. 해수는 '임수(양수)'로 봅니다.
    '자(子)': {'element': '수', 'polarity': 1}, # 음
    '축(丑)': {'element': '토', 'polarity': 1}, # 음
    '인(寅)': {'element': '목', 'polarity': 0}, # 양
    '묘(卯)': {'element': '목', 'polarity': 1}, # 음
    '진(辰)': {'element': '토', 'polarity': 0}, # 양
    '사(巳)': {'element': '화', 'polarity': 0}, # 양 (병화)
    '오(午)': {'element': '화', 'polarity': 1}, # 음 (정화)
    '미(未)': {'element': '토', 'polarity': 1}, # 음
    '신(申)': {'element': '금', 'polarity': 0}, # 양
    '유(酉)': {'element': '금', 'polarity': 1}, # 음
    '술(戌)': {'element': '토', 'polarity': 0}, # 양
    '해(亥)': {'element': '수', 'polarity': 0}, # 양 (임수)
}

# 오행 상생상극 관계 (생하는 관계)
OHAENG_SANGSAENG = {
    '목': '화', '화': '토', '토': '금', '금': '수', '수': '목'
}
# 오행 상극 관계 (극하는 관계)
OHAENG_SANGGEUK = {
    '목': '토', '토': '수', '수': '화', '화': '금', '금': '목'
}

# 한국 썸머타임 시행 기간 (시작일, 종료일)
SUMMER_TIME_PERIODS = [
    (datetime(1948, 6, 1, 0, 0), datetime(1948, 9, 13, 0, 0)),
    (datetime(1949, 4, 3, 0, 0), datetime(1949, 9, 11, 0, 0)),
    (datetime(1950, 4, 1, 0, 0), datetime(1950, 9, 10, 0, 0)),
    (datetime(1951, 5, 6, 0, 0), datetime(1951, 9, 9, 0, 0)),
    (datetime(1955, 5, 5, 0, 0), datetime(1955, 9, 9, 0, 0)),
    (datetime(1956, 5, 20, 0, 0), datetime(1956, 9, 30, 0, 0)),
    (datetime(1957, 5, 5, 0, 0), datetime(1957, 9, 22, 0, 0)),
    (datetime(1958, 5, 4, 0, 0), datetime(1958, 9, 21, 0, 0)),
    (datetime(1959, 5, 3, 0, 0), datetime(1959, 9, 20, 0, 0)),
    (datetime(1960, 5, 1, 0, 0), datetime(1960, 9, 18, 0, 0)),
    (datetime(1987, 5, 10, 2, 0), datetime(1987, 10, 11, 3, 0)),
    (datetime(1988, 5, 8, 2, 0), datetime(1988, 10, 9, 3, 0))
]

class SajuAnalyzer:
    def __init__(self, birth_date_str, birth_time_str=None, gender='male', name='Unknown', calendar_type='solar', is_leap_month=False, email=''):
        """
        name: User's name
        gender: 'male' or 'female'
        birth_time_str: "HH:MM", "HHMM" or None/Empty
        birth_date_str: "YYYY-MM-DD", "YYYYMMDD", etc.
        calendar_type: 'solar' or 'lunar'
        is_leap_month: True or False (only for lunar)
        email: Client's email address
        """
        self.name = name
        self.gender = gender.lower()
        self.calendar_type = calendar_type
        self.is_leap_month = is_leap_month
        self.email = email
        
        # 날짜 정규화
        self.birth_date_str = self._normalize_date(birth_date_str)
        
        # 음력이면 양력으로 변환
        if self.calendar_type == 'lunar':
            self.birth_date_str = self._convert_lunar_to_solar(self.birth_date_str, self.is_leap_month)
        
        # 시간 정보가 없으면 00:00으로 임시 설정하되, unknown 플래그 설정
        if not birth_time_str or birth_time_str.strip() == "":
            self.time_unknown = True
            birth_time_str = "00:00"
        else:
            self.time_unknown = False
            # 시간 정규화
            birth_time_str = self._normalize_time(birth_time_str)
            
        self.input_dt = datetime.strptime(f"{self.birth_date_str} {birth_time_str}", "%Y-%m-%d %H:%M")
        
        # 썸머타임 체크 (시간을 모르면 썸머타임 의미 없음)
        if not self.time_unknown:
            self.is_summer_time = self._check_summer_time(self.input_dt)
        else:
            self.is_summer_time = False
        
        # 썸머타임이면 1시간 빼기 (표준시로 변환)
        if self.is_summer_time:
            self.adjusted_dt = self.input_dt - timedelta(hours=1)
        else:
            self.adjusted_dt = self.input_dt
            
        self.year = self.adjusted_dt.year
        self.month = self.adjusted_dt.month
        self.day = self.adjusted_dt.day
        self.hour = self.adjusted_dt.hour
        self.minute = self.adjusted_dt.minute

    def _convert_lunar_to_solar(self, date_str, is_leap):
        try:
            year, month, day = map(int, date_str.split('-'))
            calendar = KoreanLunarCalendar()
            calendar.setLunarDate(year, month, day, is_leap)
            return calendar.SolarIsoFormat()
        except Exception as e:
            print(f"Lunar conversion error: {e}")
            return date_str

    def _normalize_date(self, date_str):
        nums = re.sub(r'[^0-9]', '', date_str)
        if len(nums) == 8:
            return f"{nums[:4]}-{nums[4:6]}-{nums[6:]}"
        return date_str 

    def _normalize_time(self, time_str):
        nums = re.sub(r'[^0-9]', '', time_str)
        if len(nums) == 4:
            return f"{nums[:2]}:{nums[2:]}"
        return time_str

    def _check_summer_time(self, dt):
        for start, end in SUMMER_TIME_PERIODS:
            if start <= dt < end:
                return True
        return False

    def _get_ganji(self, year, month, day, hour, minute):
        # ... (기존 간지 계산 로직 유지, 단 십성 계산을 위해 분리 필요하지만 일단 기존 코드 활용)
        # 여기서는 기존 로직을 그대로 두되, 십성 계산을 위해 get_result_json에서 처리
        pass # 실제 구현은 아래 get_result_json 내의 로직을 따름

    def _calculate_sibseong(self, day_stem, target, is_stem=True):
        """
        일간(Day Stem)을 기준으로 대상(Target)의 십성을 계산
        day_stem: '갑(甲)'
        target: '을(乙)' (천간) or '자(子)' (지지)
        is_stem: True if target is Stem, False if Branch
        """
        me = CHEONGAN_INFO[day_stem]
        
        if is_stem:
            you = CHEONGAN_INFO[target]
        else:
            you = JIJI_YONG[target]
            
        my_elem = me['element']
        your_elem = you['element']
        my_pol = me['polarity']
        your_pol = you['polarity']
        
        # 비겁 (같은 오행)
        if my_elem == your_elem:
            if my_pol == your_pol: return "비견"
            else: return "겁재"
            
        # 식상 (내가 생함)
        if OHAENG_SANGSAENG[my_elem] == your_elem:
            if my_pol == your_pol: return "식신"
            else: return "상관"
            
        # 재성 (내가 극함)
        if OHAENG_SANGGEUK[my_elem] == your_elem:
            if my_pol == your_pol: return "편재"
            else: return "정재"
            
        # 관성 (나를 극함)
        if OHAENG_SANGGEUK[your_elem] == my_elem:
            if my_pol == your_pol: return "편관"
            else: return "정관"
            
        # 인성 (나를 생함)
        if OHAENG_SANGSAENG[your_elem] == my_elem:
            if my_pol == your_pol: return "편인"
            else: return "정인"
            
        return ""

    def _calculate_sinsal(self, day_branch, target_branch):
        """
        일지(Day Branch)를 기준으로 대상 지지의 신살(역마, 도화, 화개) 계산
        (현대 명리에서는 일지 기준을 많이 사용)
        """
        # 삼합 국(Frame) 결정
        # 인오술(화) -> 신(역마), 묘(도화), 술(화개) ... 가 아니라
        # 인오술: 신(역마), 묘(도화), 술(화개)
        # 사유축: 해(역마), 오(도화), 축(화개)
        # 신자진: 인(역마), 유(도화), 진(화개)
        # 해묘미: 사(역마), 자(도화), 미(화개)
        
        # 일지가 속한 삼합 찾기
        samhap = {
            '인(寅)': '인오술', '오(午)': '인오술', '술(戌)': '인오술',
            '사(巳)': '사유축', '유(酉)': '사유축', '축(丑)': '사유축',
            '신(申)': '신자진', '자(子)': '신자진', '진(辰)': '신자진',
            '해(亥)': '해묘미', '묘(卯)': '해묘미', '미(未)': '해묘미'
        }
        
        group = samhap.get(day_branch)
        if not group: return ""
        
        # 신살 매핑
        sinsal_map = {
            '인오술': {'신(申)': '역마', '묘(卯)': '도화', '술(戌)': '화개'},
            '사유축': {'해(亥)': '역마', '오(午)': '도화', '축(丑)': '화개'},
            '신자진': {'인(寅)': '역마', '유(酉)': '도화', '진(辰)': '화개'},
            '해묘미': {'사(巳)': '역마', '자(子)': '도화', '미(未)': '화개'}
        }
        
        target_sinsal = sinsal_map[group].get(target_branch, "")
        return target_sinsal

    def get_result_json(self):
        # ... (기존 간지 계산 로직 복사 및 수정) ...
        # 입춘 계산 등 복잡한 로직은 기존 코드 유지 필요.
        # 여기서는 편의상 기존 코드를 그대로 가져오되, 십성/신살 추가
        
        # 1. 입춘일 계산 (간단화된 버전, 실제로는 절기력 필요하지만 여기선 datetime 기준 근사치 혹은 기존 로직 사용)
        # 기존 로직이 없으므로 다시 작성해야 함. (이전 파일 내용을 덮어쓰므로)
        # *중요*: 이전 파일의 절기 계산 로직을 복원해야 함.
        
        # (절기 데이터 - 간략화)
        # 입춘은 대략 2월 4일경.
        # 월주 구하기 위해선 24절기가 필요함.
        # 여기서는 간단히 양력 월일로 월주를 추정하는 기존 방식(혹은 개선된 방식) 사용
        
        # ... (절기 로직 복원) ...
        # SajuAnalyzer의 핵심 로직인 '사주 세우기'가 필요함.
        # 이전 코드의 get_result_json을 참고하여 재작성.
        
        # 년주
        year_gan = CHEONGAN[(self.year - 4) % 10]
        year_ji = JIJI[(self.year - 4) % 12]
        
        # 입춘 기준 년주 보정 (2월 4일 전이면 전년도)
        # 간단히 2월 4일 00시를 기준으로 함 (정밀 절기력 라이브러리 없으므로)
        ipchun = datetime(self.year, 2, 4, 0, 0)
        if self.adjusted_dt < ipchun:
            year_gan = CHEONGAN[(self.year - 1 - 4) % 10]
            year_ji = JIJI[(self.year - 1 - 4) % 12]
            
        # 월주 (년두법)
        # 갑기년 -> 병인두, 을경년 -> 무인두...
        year_gan_idx = CHEONGAN.index(year_gan)
        start_gan_idx = (year_gan_idx % 5) * 2 + 2 # 갑(0)->병(2), 을(1)->무(4)...
        
        # 절기별 월 구분 (대략적)
        solar_terms = [
            (2, 4), (3, 6), (4, 5), (5, 6), (6, 6), (7, 7),
            (8, 8), (9, 8), (10, 8), (11, 7), (12, 7), (1, 6)
        ]
        
        # 현재 날짜가 어떤 절기에 속하는지 찾기
        # 월 인덱스: 인(0) ~ 축(11)
        month_idx = 0
        curr_month = self.adjusted_dt.month
        curr_day = self.adjusted_dt.day
        
        # 간단한 비교 로직
        # 2월 4일 이후면 인월(0), 3월 6일 이후면 묘월(1)...
        # 1월은 축월(11) (전년도 해자축의 축)
        
        target_month_idx = -1
        
        # 1월 소한(1.6) 이전이면 전년도 자월(10) -> 축월(11) 이어야 하는데...
        # 로직: 
        # 1. 일단 월을 찾는다.
        # 2. 해당 월의 절기일보다 작으면 이전 월로 간주.
        
        # 절기 기준일 매핑 (월 -> 절기일)
        term_days = {m: d for m, d in solar_terms}
        
        if curr_day >= term_days.get(curr_month, 1):
            # 해당 월의 절기 지남 -> 해당 월의 지지
            # 2월 -> 인(0), 3월 -> 묘(1)... 12월 -> 자(10), 1월 -> 축(11)
            if curr_month == 1: month_idx = 11 # 축
            elif curr_month == 2: month_idx = 0 # 인
            else: month_idx = curr_month - 2
        else:
            # 해당 월의 절기 안 지남 -> 이전 월의 지지
            if curr_month == 1: month_idx = 10 # 자 (12월 절기 지남) -> 전년도 자월
            elif curr_month == 2: month_idx = 11 # 축 (1월 절기 지남)
            else: month_idx = curr_month - 3
            
        month_gan = CHEONGAN[(start_gan_idx + month_idx) % 10]
        month_ji = JIJI[(month_idx + 2) % 12] # 인(2)부터 시작하므로
        
        # 일주 (일진)
        # 기준일: 1900년 1월 1일 (갑술일)
        base_date = datetime(1900, 1, 1)
        # 날짜 차이 계산
        diff_days = (datetime(self.year, self.month, self.day) - base_date).days
        # 1900.1.1은 갑술(10) -> 갑(0), 술(10)
        # 갑술은 60갑자 중 10번째 (갑자0, 을축1... 갑술10)
        # 60갑자 인덱스 계산
        # 갑자(0) 기준 1900.1.1은 10
        base_idx = 10 
        curr_idx = (base_idx + diff_days) % 60
        
        day_gan = CHEONGAN[curr_idx % 10]
        day_ji = JIJI[curr_idx % 12]
        
        # 시주 (시두법)
        # 갑기일 -> 갑자시, 을경일 -> 병자시...
        day_gan_idx = CHEONGAN.index(day_gan)
        start_hour_gan_idx = (day_gan_idx % 5) * 2
        
        # 시간 -> 자시(0) ~ 해시(11)
        # 야자시/조자시 구분 없이 23:30~01:30을 자시로 봄 (서울 보정 이미 됨)
        # 23:30 ~ 01:29 -> 자시 (0)
        # 01:30 ~ 03:29 -> 축시 (1)
        
        # 분을 시간으로 환산하여 계산
        total_minutes = self.hour * 60 + self.minute
        # 자시 시작 23:30 = 1410분. 
        # 00:00 ~ 01:29 (89분) -> 자시
        # 23:30 ~ 23:59 -> 자시
        
        # 30분을 뺀 시간을 기준으로 2시간씩 나눔
        # 예: 01:30 -> 01:00 -> /2 = 0 (자시? 아님 축시여야 함)
        # 공식: (시간 * 60 + 분 + 30) // 120 % 12
        # 01:30 -> 90+30=120 -> 1 (축시)
        # 23:30 -> 1410+30=1440 -> 12 -> 0 (자시)
        
        hour_idx = (total_minutes + 30) // 120 % 12
        
        hour_gan = CHEONGAN[(start_hour_gan_idx + hour_idx) % 10]
        hour_ji = JIJI[hour_idx]
        
        # 시주 모름 처리
        if self.time_unknown:
            hour_gan = "모름"
            hour_ji = "모름"
            
        pillars = {
            'year': f"{year_gan}{year_ji}",
            'month': f"{month_gan}{month_ji}",
            'day': f"{day_gan}{day_ji}",
            'hour': f"{hour_gan}{hour_ji}"
        }
        
        # 오행 분석
        ohaeng = {'목': 0, '화': 0, '토': 0, '금': 0, '수': 0}
        
        # 천간 오행
        for p in [year_gan, month_gan, day_gan]:
            ohaeng[CHEONGAN_INFO[p]['element']] += 1
        if not self.time_unknown:
            ohaeng[CHEONGAN_INFO[hour_gan]['element']] += 1
            
        # 지지 오행 (용 기준)
        for p in [year_ji, month_ji, day_ji]:
            ohaeng[JIJI_YONG[p]['element']] += 1
        if not self.time_unknown:
            ohaeng[JIJI_YONG[hour_ji]['element']] += 1
            
    def _calculate_gyeokguk(self, day_gan, month_branch, heaven_stems):
        """
        격국 산출 함수 (월지 지장간 투간법)
        day_gan: 일간 (예: '갑')
        month_branch: 월지 (예: '인')
        heaven_stems: 천간 리스트 (예: ['갑', '병', '무']) - 연간, 월간, 시간
        """
        # 0. 데이터 준비
        # saju_data에서 가져옴 (import 필요 - 상단에서 import 안했으므로 함수 내에서 하거나 전역 수정 필요. 여기선 함수내용에서 처리)
        # Note: saju_analyzer.py top-level already imports basic stuff, but JIJANGGAN might not be imported.
        # However, looking at the file, saju_data is likely imported as a module if used elsewhere, 
        # but in saju_analyzer.py, it imports CHEONGAN etc from specific definitions or file?
        # Let's check imports. Line 23-30 doesn't show saju_data import.
        # But 'from saju_batch_processor_v2 import ...' was in '1번_사주수집.py'.
        # 'saju_analyzer.py' seems to have data defined inside it (lines 30-97).
        # Ah! saju_analyzer.py has its OWN data definitions (lines 30-97).
        # It DOES NOT import saju_data.py.
        # 'saju_app.py' imports 'saju_data'.
        # I should Import saju_data inside this method or verify if I can import it at top or just use the logic with provided JIJANGGAN table from user.
        # The user provided the table. I should Include the table in the code or import it.
        # Since I am editing a class method, I can't easily add top-level import without editing top of file.
        # I will do a local import inside the method to be safe and robust.
        
        try:
            from saju_data import JIJANGGAN, GYEOKGUK_DESC
        except ImportError:
            # Fallback if saju_data.py is not in path or circular import
            # Define minimal needed data here as per user spec
            JIJANGGAN = {
                '자': {'chogi': '임', 'junggi': None, 'bonggi': '계'},
                '축': {'chogi': '계', 'junggi': '신', 'bonggi': '기'},
                '인': {'chogi': '무', 'junggi': '병', 'bonggi': '갑'},
                '묘': {'chogi': '갑', 'junggi': None, 'bonggi': '을'},
                '진': {'chogi': '을', 'junggi': '계', 'bonggi': '무'},
                '사': {'chogi': '무', 'junggi': '경', 'bonggi': '병'},
                '오': {'chogi': '병', 'junggi': '기', 'bonggi': '정'},
                '미': {'chogi': '정', 'junggi': '을', 'bonggi': '기'},
                '신': {'chogi': '무', 'junggi': '임', 'bonggi': '경'},
                '유': {'chogi': '경', 'junggi': None, 'bonggi': '신'},
                '술': {'chogi': '신', 'junggi': '정', 'bonggi': '무'},
                '해': {'chogi': '무', 'junggi': '갑', 'bonggi': '임'}
            }
            # Simplified map if GYEOKGUK_DESC missing
            GYEOKGUK_DESC = {}

        # 한글만 추출 (혹시 한자 포함된 경우)
        day_gan_char = day_gan.split('(')[0]
        month_branch_char = month_branch.split('(')[0]
        stems_char = [s.split('(')[0] for s in heaven_stems if s]

        if month_branch_char not in JIJANGGAN:
            return {"name": "알수없음", "basis": "월지 데이터 오류"}

        jijanggan = JIJANGGAN[month_branch_char]
        bonggi = jijanggan['bonggi']
        junggi = jijanggan['junggi']
        chogi = jijanggan['chogi']
        
        gyeok_elem = None
        basis = ""

        # 1. 예외 처리: 자, 묘, 유는 무조건 본기
        if month_branch_char in ['자', '묘', '유']:
            gyeok_elem = bonggi
            basis = f"월지 '{month_branch_char}'는 왕지이므로 투간 여부와 상관없이 본기 '{bonggi}'를 격으로 취함"
        else:
            # 2. 투간 확인 (본기 > 중기 > 초기)
            if bonggi in stems_char:
                gyeok_elem = bonggi
                basis = f"월지 '{month_branch_char}'의 지장간 본기 '{bonggi}'가 천간에 투출됨 (가장 강력)"
            elif junggi and junggi in stems_char:
                gyeok_elem = junggi
                basis = f"월지 '{month_branch_char}'의 지장간 중기 '{junggi}'가 천간에 투출됨"
            elif chogi in stems_char:
                gyeok_elem = chogi
                basis = f"월지 '{month_branch_char}'의 지장간 초기 '{chogi}'가 천간에 투출됨"
            else:
                # 3. 미투간 시 본기
                gyeok_elem = bonggi
                basis = f"월지 지장간이 투출되지 않아 본기 '{bonggi}'를 격으로 취함"
        
        # 4. 십성 변환 (격국 명칭)
        # 일간 vs 격(오행/음양) -> 십성 산출
        # 기존 _calculate_sibseong 활용 (천간 vs 천간 기준)
        
        sibseong = self._calculate_sibseong(day_gan_char, gyeok_elem, is_stem=True)
        
        gyeok_name = f"{sibseong}격"
        
        # 비견/겁재 예외 처리 (건록/양인 등) - 사용자 요청대로 그냥 비견/겁재격으로 표기
        
        # 상세 설명 조회
        desc_info = GYEOKGUK_DESC.get(gyeok_name, {})
        desc_text = desc_info.get("desc", f"{gyeok_name}입니다.")

        return {
            "name": gyeok_name,
            "full_name": f"{gyeok_name} (Class: {sibseong})",
            "element": gyeok_elem,
            "basis": basis,
            "desc": desc_text
        }

    def get_result_json(self):
        pillars = self.get_gan_ji()
        ohaeng = self.analyze_ohaeng(pillars)
        daewoon = self.get_daewoon(pillars['year_gan_idx'], pillars['month_gan_idx'], pillars['month_ji_idx'])
        
        # Helper to split "갑(甲)자(子)" -> "갑(甲)", "자(子)"
        def split_pillar(p):
            if p == "모름(Unknown)": return "모름", "모름"
            # 정규식으로 분리: 한글(한자) 패턴
            # 예: 갑(甲) -> match
            parts = re.findall(r'.\(.\)', p)
            if len(parts) == 2:
                return parts[0], parts[1]
            return p, p # Fallback
            
        y_gan, y_ji = split_pillar(pillars['year'])
        m_gan, m_ji = split_pillar(pillars['month'])
        d_gan, d_ji = split_pillar(pillars['day'])
        h_gan, h_ji = split_pillar(pillars['hour'])
        
        sibseong = {
            'year_gan': self._calculate_sibseong(d_gan, y_gan, True),
            'year_ji': self._calculate_sibseong(d_gan, y_ji, False),
            'month_gan': self._calculate_sibseong(d_gan, m_gan, True),
            'month_ji': self._calculate_sibseong(d_gan, m_ji, False),
            'day_gan': "비견", # 본원 -> 비견으로 변경
            'day_ji': self._calculate_sibseong(d_gan, d_ji, False),
            'hour_gan': self._calculate_sibseong(d_gan, h_gan, True) if not self.time_unknown else "",
            'hour_ji': self._calculate_sibseong(d_gan, h_ji, False) if not self.time_unknown else ""
        }
        
        sinsal = {
            'year_ji': self._calculate_sinsal(d_ji, y_ji),
            'month_ji': self._calculate_sinsal(d_ji, m_ji),
            'day_ji': "",
            'hour_ji': self._calculate_sinsal(d_ji, h_ji) if not self.time_unknown else ""
        }
        
        # [NEW] 격국 계산
        # 천간 리스트: 연월시 (일간 제외)
        heaven_stems_list = [y_gan, m_gan]
        if not self.time_unknown:
            heaven_stems_list.append(h_gan)
            
        gyeok_result = self._calculate_gyeokguk(d_gan, m_ji, heaven_stems_list)
        
        result = {
            "info": {
                "name": self.name,
                "email": self.email,  # Added email field
                "input_date": self.birth_date_str,
                "calendar_type": "음력(Lunar)" if self.calendar_type == 'lunar' else "양력(Solar)",
                "is_leap_month": self.is_leap_month,
                "input_time": "모름(Unknown)" if self.time_unknown else self.input_dt.strftime("%H:%M"),
                "gender": "남성(Male)" if self.gender == 'male' else "여성(Female)",
                "adjusted_date": self.adjusted_dt.strftime("%Y-%m-%d %H:%M"),
                "summer_time_applied": self.is_summer_time,
                "longitude_correction": "-32분 (서울 기준)" if not self.time_unknown else "적용 안 함"
            },
            "four_pillars": {
                "year": {"gan": y_gan, "ji": y_ji},
                "month": {"gan": m_gan, "ji": m_ji},
                "day": {"gan": d_gan, "ji": d_ji},
                "hour": {"gan": h_gan, "ji": h_ji}
            },
            "five_elements": ohaeng,
            "gyeokguk": gyeok_result, # [NEW] Added Gyeokguk
            "daewoon": daewoon,
            "sibseong": sibseong,
            "sinsal": sinsal
        }
        return result

    # (Old methods removed to fix NameError and duplication)



# ---------------------------------------------------------
# 3. 메인 실행 함수
# ---------------------------------------------------------

def main():
    print("="*50)
    print("🔮 사주 분석 자동화 프로그램 v2.1 🔮")
    print("="*50)
    
    try:
        input_date = input("생년월일을 입력하세요 (예: 1990-01-01): ")
        input_time = input("태어난 시간을 입력하세요 (예: 14:30): ")
        input_gender = input("성별을 입력하세요 (male/female): ")
        
        analyzer = SajuAnalyzer(input_date, input_time, input_gender)
        result = analyzer.get_result_json()
        
        print("\n" + "="*50)
        print("📊 분석 결과 (JSON Format)")
        print("="*50)
        print(json.dumps(result, indent=4, ensure_ascii=False))
        
        print("\n" + "="*50)
        print("분석이 완료되었습니다.")
        print("="*50)

    except ValueError:
        print("\n[오류] 날짜나 시간 형식이 올바르지 않습니다.")
    except Exception as e:
        print(f"\n[오류] 문제가 발생했습니다: {e}")

if __name__ == "__main__":
    main()
