import sys
import os
import json
import re
import math
from datetime import datetime, time, timedelta
import tkinter as tk
from tkinter import messagebox, scrolledtext
from korean_lunar_calendar import KoreanLunarCalendar
import saju_data
from saju_desc_data import *
from saju_data import CHEONGAN, JIJI, OHAENG, YUKCHIN, SIBSEONG_DESC, SINSAL_DESC, CHEONGAN_DESC, JIJI_DESC, ILJU_DESC_SUMMARY, ILJU_DESC_DETAIL, DAEWOON_DESC, YEARLY_LUCK_DESC, SUMMER_TIME_PERIODS, CHEONGAN_INFO, JIJI_INFO, OHAENG_SANGSAENG, OHAENG_SANGGEUK, JIJANGGAN_WEIGHT, WOLRYEONG_STRENGTH




class SolarTermCalculator:
    _jeolgi_data = None
    
    @classmethod
    def _load_jeolgi_data(cls):
        if cls._jeolgi_data is None:
            import json
            import os
            # Look for jeolgi_data.json in same directory as this script
            script_dir = os.path.dirname(os.path.abspath(__file__))
            data_path = os.path.join(script_dir, 'jeolgi_data.json')
            if os.path.exists(data_path):
                with open(data_path, 'r', encoding='utf-8') as f:
                    cls._jeolgi_data = json.load(f)
            else:
                cls._jeolgi_data = {}
        return cls._jeolgi_data
    
    def find_jeolgi_time(self, year, month):
        # Load precise data from JSON
        data = self._load_jeolgi_data()
        key = f"{year}-{month:02d}"
        
        if key in data:
            return datetime.strptime(data[key], "%Y-%m-%d %H:%M")
        
        # Fallback approximation for dates not in database
        term_map = {
            1: 6, 2: 4, 3: 6, 4: 5, 5: 6, 6: 6,
            7: 7, 8: 8, 9: 8, 10: 9, 11: 8, 12: 7
        }
        day = term_map.get(month, 5)
        return datetime(year, month, day, 12, 0)




class SajuAnalyzer:
    def __init__(self, birth_date_str, birth_time_str=None, gender='male', name='Unknown', calendar_type='solar', is_leap_month=False):
        self.name = name
        self.gender = gender.lower()
        self.calendar_type = calendar_type
        self.is_leap_month = is_leap_month
        
        self.birth_date_str = self._normalize_date(birth_date_str)
        
        if self.calendar_type == 'lunar':
            self.birth_date_str = self._convert_lunar_to_solar(self.birth_date_str, self.is_leap_month)
        
        if not birth_time_str or birth_time_str.strip() == "":
            self.time_unknown = True
            birth_time_str = "00:00"
        else:
            self.time_unknown = False
            birth_time_str = self._normalize_time(birth_time_str)
        
        self.birth_time_str = birth_time_str
            
        self.input_dt = datetime.strptime(f"{self.birth_date_str} {birth_time_str}", "%Y-%m-%d %H:%M")
        
        if not self.time_unknown:
            self.is_summer_time = self._check_summer_time(self.input_dt)
        else:
            self.is_summer_time = False
        
        if self.is_summer_time:
            self.adjusted_dt = self.input_dt - timedelta(hours=1)
        else:
            self.adjusted_dt = self.input_dt
            
        self.year = self.adjusted_dt.year
        self.month = self.adjusted_dt.month
        self.day = self.adjusted_dt.day
        self.hour = self.adjusted_dt.hour
        self.minute = self.adjusted_dt.minute
        self.email = 'unknown@example.com'

    def _convert_lunar_to_solar(self, date_str, is_leap):
        try:
            year, month, day = map(int, date_str.split('-'))
            calendar = KoreanLunarCalendar()
            if not calendar.setLunarDate(year, month, day, is_leap):
                raise ValueError(f"Invalid Lunar Date: {date_str} (Leap: {is_leap})")
                
            solar_date = calendar.SolarIsoFormat()
            if solar_date == "0000-00-00":
                raise ValueError(f"Failed to convert Lunar Date: {date_str}")
                
            return solar_date
        except Exception as e:
            print(f"Lunar conversion error: {e}")
            raise ValueError(f"음력 변환 오류: {e}")

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
        check_date = dt.strftime("%Y-%m-%d")
        for period in SUMMER_TIME_PERIODS:
            if period['start'] <= check_date <= period['end']:
                return True
        return False

    def _calculate_hyunchim(self, char):
        c = char.split('(')[0]
        # 현침살: 갑, 신, 묘, 오, 미, 신(申)
        if c in ['갑', '신', '묘', '오', '미']: 
            return "현침살"
        return ""

    def _calculate_yangin(self, stem, branch):
        # 양인살: 양간이 제왕지를 만났을 때
        # 갑-묘, 병-오, 무-오, 경-유, 임-자
        s_char = stem.split('(')[0]
        b_char = branch.split('(')[0]
        
        yangin_map = {
            '갑': '묘', '병': '오', '무': '오', '경': '유', '임': '자'
            }
        
        if s_char in yangin_map and yangin_map[s_char] == b_char:
            return True
        return False

    def _calculate_cheondeok(self, month_branch, target_char):
        """천덕귀인 계산: 월지 기준, 천간 또는 지지"""
        m_ji = month_branch.split('(')[0]
        t_char = target_char.split('(')[0]

        # 천덕귀인 매핑 (월지 기준 -> 천간/지지)
        cd_map = {
            '자': ['경', '사'],  # 자월: 경천간 또는 사지지
            '축': ['병', '묘'],  # 축월: 병천간 또는 묘지지
            '인': ['정'],
            '묘': ['신'],       # 묘월: 신지지
            '진': ['임'],
            '사': ['신'],       # 사월: 신지지
            '오': ['갑', '해'], # 오월: 갑천간 또는 해지지
            '미': ['을'],
            '신': ['무', '계'],
            '유': ['임', '인'], # 유월: 임천간 또는 인지지
            '술': ['병'],
            '해': ['을']
            }

        if m_ji in cd_map and t_char in cd_map[m_ji]:
            return True
        return False

    def _calculate_woldeok(self, month_branch, target_stem):
        m_ji = month_branch.split('(')[0]
        t_gan = target_stem.split('(')[0]
        
        # 월덕귀인 (삼합의 왕지 천간)
        # 인오술(화) -> 병, 신자진(수) -> 임, 해묘미(목) -> 갑, 사유축(금) -> 경
        wd_map = {
            '인': '병', '오': '병', '술': '병',
            '신': '임', '자': '임', '진': '임',
            '해': '갑', '묘': '갑', '미': '갑',
            '사': '경', '유': '경', '축': '경'
            }
        
        if m_ji in wd_map and wd_map[m_ji] == t_gan:
            return True
        return False

    def _calculate_cheoneui(self, month_branch, target_branch):
        m_ji = month_branch.split('(')[0]
        t_ji = target_branch.split('(')[0]
        
        cheoneui_map = {
            '인': '축', '묘': '인', '진': '묘', '사': '진', '오': '사', '미': '오',
            '신': '미', '유': '신', '술': '유', '해': '술', '자': '해', '축': '자'
            }
        
        target_cheoneui = cheoneui_map.get(m_ji, "")
        if target_cheoneui == t_ji:
            return "천의성"
        return ""

    def _calculate_sibseong(self, day_stem, target, is_stem=True):
        def get_info(key, info_dict):
            if key in info_dict: return info_dict[key]
            k_char = key.split('(')[0]
            for k, v in info_dict.items():
                if k.startswith(k_char): return v
            raise KeyError(f"Key not found: {key}")

        try:
            me = get_info(day_stem, CHEONGAN_INFO)
            if is_stem:
                you = get_info(target, CHEONGAN_INFO)
            else:
                you = get_info(target, JIJI_INFO)
        except KeyError:
            return ""
            
        my_elem = me['element']
        your_elem = you['element']
        my_pol = me['polarity']
        your_pol = you['polarity']
        
        if my_elem == your_elem:
            if my_pol == your_pol: return "비견"
            else: return "겁재"
        if OHAENG_SANGSAENG[my_elem] == your_elem:
            if my_pol == your_pol: return "식신"
            else: return "상관"
        if OHAENG_SANGGEUK[my_elem] == your_elem:
            if my_pol == your_pol: return "편재"
            else: return "정재"
        if OHAENG_SANGGEUK[your_elem] == my_elem:
            if my_pol == your_pol: return "편관"
            else: return "정관"
        if OHAENG_SANGSAENG[your_elem] == my_elem:
            if my_pol == your_pol: return "편인"
            else: return "정인"
        return ""

    def _calculate_sinsal(self, day_branch, target_branch):
        samhap = {
            '인(寅)': '인오술', '오(午)': '인오술', '술(戌)': '인오술',
            '사(巳)': '사유축', '유(酉)': '사유축', '축(丑)': '사유축',
            }
        
    def _calculate_pillar_sinsal(self, gan, ji, pillar_type):
        res = {'gan': [], 'ji': []}
        
        g_char = gan.split('(')[0] if gan else ""
        j_char = ji.split('(')[0] if ji else ""
        
        if not hasattr(self, 'day_gan_char'): return res
        
        d_gan = self.day_gan_char
        d_ji = self.day_ji_char
        y_ji = getattr(self, 'year_ji_char', '')
        y_gan = getattr(self, 'year_gan_char', '')
        m_gan = getattr(self, 'month_gan_char', '')
        h_gan = getattr(self, 'hour_gan_char', '')
        m_ji = getattr(self, 'month_ji_char', '')

        # === 1. 12 Sinsal (Dual Base) ===
        def check_12sinsal(base_ji, target_ji):
            samhap = {
                '인': '인오술', '오': '인오술', '술': '인오술',
                '사': '사유축', '유': '사유축', '축': '사유축',
                '신': '신자진', '자': '신자진', '진': '신자진',
                '해': '해묘미', '묘': '해묘미', '미': '해묘미'
            }
            group = samhap.get(base_ji, '')
            found = []
            
            if group == '인오술':
                if target_ji == '인': found.append("지살")
                elif target_ji == '신': found.append("역마")
                elif target_ji == '오': found.append("장성살")
                elif target_ji == '술': found.append("화개")
            elif group == '사유축':
                if target_ji == '사': found.append("지살")
                elif target_ji == '해': found.append("역마")
                elif target_ji == '유': found.append("장성살")
                elif target_ji == '축': found.append("화개")
            elif group == '신자진':
                if target_ji == '신': found.append("지살")
                elif target_ji == '인': found.append("역마")
                elif target_ji == '자': found.append("장성살")
                elif target_ji == '진': found.append("화개")
            elif group == '해묘미':
                if target_ji == '해': found.append("지살")
                elif target_ji == '사': found.append("역마")
                elif target_ji == '묘': found.append("장성살")
                elif target_ji == '미': found.append("화개")
            return found

        res['ji'].extend(check_12sinsal(d_ji, j_char))
        
        if y_ji:
            y_res = check_12sinsal(y_ji, j_char)
            for s in y_res:
                if s not in res['ji']: res['ji'].append(s)

        # Broad Check for common sinsals
        if j_char in ['자', '오', '묘', '유'] and "도화" not in res['ji']: res['ji'].append("도화")
        if j_char in ['인', '신', '사', '해'] and "역마" not in res['ji']: res['ji'].append("역마")
        if j_char in ['진', '술', '축', '미'] and "화개" not in res['ji']: res['ji'].append("화개")

        # === 2. Gilseong / Sal ===
        
        # 암록 (Day Gan -> Ji)
        amrok_map = {'갑': '해', '을': '술', '병': '신', '정': '미', '무': '신', '기': '미', '경': '사', '신': '진', '임': '인', '계': '축'}
        if amrok_map.get(d_gan) == j_char: res['ji'].append("암록")

        # 양인살 (Day Gan -> Ji) - EXPANDED for Yin stems
        yangin_map = {
            '갑': '묘', '병': '오', '무': '오', '경': '유', '임': '자', # Yang (건록+1)
            '을': '진', '정': '미', '기': '미', '신': '술', '계': '축'  # Yin (관대)
        }
        if yangin_map.get(d_gan) == j_char: res['ji'].append("양인살")

        # 월덕귀인 (Month Ji -> Stem check)
        if m_ji:
            wd_stem = None
            if m_ji in ['인', '오', '술']: wd_stem = '병'
            elif m_ji in ['신', '자', '진']: wd_stem = '임'
            elif m_ji in ['해', '묘', '미']: wd_stem = '갑'
            elif m_ji in ['사', '유', '축']: wd_stem = '경'
            
            if wd_stem and g_char == wd_stem:
                res['gan'].append("월덕귀인")

        # 백호대살
        baekho_pairs = ["갑진", "을미", "병술", "정축", "무진", "임술", "계축"]
        if (g_char + j_char) in baekho_pairs:
            res['gan'].append("백호대살"); res['ji'].append("백호대살")

        # 괴강살
        goegang_pairs = ["경진", "경술", "임진", "임술"]  # 표준 4괴강
        if (g_char + j_char) in goegang_pairs:
            res['gan'].append("괴강살"); res['ji'].append("괴강살")
            
        # 현침살 (FIXED: 미 added)
        if g_char in ['갑', '신']: res['gan'].append("현침살")
        if j_char in ['묘', '오', '신', '미']: res['ji'].append("현침살")
        
        # 천사성 (天赦星): 무술, 무신 등 특정 조합
        # 일간이 무(戊) 또는 기(己)이고, 지지가 신(申), 인(寅) 등
        cheonsa_map = {'무': ['신', '인'], '기': ['사', '해'], '병': ['자', '오']}
        if d_gan in cheonsa_map and j_char in cheonsa_map.get(d_gan, []):
            res['ji'].append("천사성")
        
        # 귀문관살 (Posteller Style - Simplified)
        # 진-해 조합이 사주에 있으면 양쪽 다 표시
        gwimun_pairs = {'자': '미', '미': '자', '축': '오', '오': '축', 
                        '인': '유', '유': '인', '묘': '신', '신': '묘', 
                        '진': '해', '해': '진', '사': '술', '술': '사'}
        partner = gwimun_pairs.get(j_char)
        if partner:
            # d_ji가 partner와 일치하거나, 현재 지지가 d_ji와 귀문관살 관계
            if d_ji == partner or j_char == gwimun_pairs.get(d_ji):
                res['ji'].append("귀문관살")

        # 천을귀인
        cheoneul_map = {'갑': ['축','미'], '무': ['축','미'], '경': ['축','미'], '을': ['자','신'], '기': ['자','신'], '병': ['해','유'], '정': ['해','유'], '신': ['인','오'], '임': ['사','묘'], '계': ['사','묘']}
        if j_char in cheoneul_map.get(d_gan, []): res['ji'].append("천을귀인")
            
        # 금여성
        geumyeo_map = {'갑': '진', '을': '사', '병': '미', '정': '신', '무': '미', '기': '신', '경': '술', '신': '해', '임': '축', '계': '인'}
        if geumyeo_map.get(d_gan) == j_char: res['ji'].append("금여성")

        # 학당귀인
        hakdang_map = {'갑': '해', '을': '오', '병': '인', '정': '유', '무': '인', '기': '유', '경': '사', '신': '자', '임': '신', '계': '묘'}
        if hakdang_map.get(d_gan) == j_char: res['ji'].append("학당귀인")
        for stem in [y_gan, m_gan, h_gan]:
            if stem and hakdang_map.get(stem) == j_char:
                if("학당귀인" not in res['ji']): res['ji'].append("학당귀인")

        # 천주귀인 (FIXED: 기 -> 유)
        cheonju_map = {'갑': '축', '을': '자', '병': '해', '정': '술', '무': '신', '기': '유', '경': '오', '신': '사', '임': '묘', '계': '인'}
        if cheonju_map.get(d_gan) == j_char: res['ji'].append("천주귀인")
            
        # 관귀학관
        gwangwi_map = {'갑': '사', '을': '사', '병': '신', '정': '신', '무': '해', '기': '해', '경': '인', '신': '인', '임': '신', '계': '신'}
        if gwangwi_map.get(d_gan) == j_char: res['ji'].append("관귀학관")

        # 문창귀인
        munchang_map = {'갑': '사', '을': '오', '병': '신', '정': '유', '무': '신', '기': '유', '경': '해', '신': '자', '임': '인', '계': '묘'}
        if munchang_map.get(d_gan) == j_char: res['ji'].append("문창귀인")

        # 홍염살
        hongyeom_map = {'갑': '오', '을': '오', '병': '인', '정': '미', '무': '진', '기': '진', '경': '술', '신': '유', '임': '자', '계': '신'}
        if hongyeom_map.get(d_gan) == j_char: res['ji'].append("홍염살")

        # 태극귀인
        taegeuk_map = {'갑': ['자','오'], '을': ['자','오'], '병': ['묘','유'], '정': ['묘','유'], '무': ['진','술','축','미'], '기': ['진','술','축','미'], '경': ['인','해'], '신': ['인','해'], '임': ['사','신'], '계': ['사','신']}
        if j_char in taegeuk_map.get(d_gan, []): res['ji'].append("태극귀인")

        # 정록
        rok_map = {'갑': '인', '을': '묘', '병': '사', '정': '오', '무': '사', '기': '오', '경': '신', '신': '유', '임': '해', '계': '자'}
        if rok_map.get(d_gan) == j_char: res['ji'].append("정록")

        # 천문성
        if j_char in ['술', '해']: res['ji'].append("천문성")
        
        # 천의성 (FIXED: Check Month Ji -> Prev Ji == Target Ji (Year Ji))
        # Example: Month Yu (酉), Prev is Shin (申). If Year Ji = 신, then 천의성.
        order = ['자','축','인','묘','진','사','오','미','신','유','술','해']
        if m_ji and m_ji in order:
            idx = order.index(m_ji)
            prev_idx = (idx - 1) % 12
            cheoneui_ji = order[prev_idx]
            if j_char == cheoneui_ji:
                res['ji'].append("천의성")

        # 과숙살 (Year Ji Season)
        season_map = {'해':'수','자':'수','축':'수', '인':'목','묘':'목','진':'목', '사':'화','오':'화','미':'화', '신':'금','유':'금','술':'금'}
        yg = season_map.get(y_ji, '')
        if yg == '목' and j_char == '축': res['ji'].append("과숙살")
        elif yg == '화' and j_char == '진': res['ji'].append("과숙살")
        elif yg == '금' and j_char == '미': res['ji'].append("과숙살")
        elif yg == '수' and j_char == '술': res['ji'].append("과숙살")
            
        return res


    def _calculate_sinsal(self, day_branch, target_branch):
        samhap = {
            '인(寅)': '인오술', '오(午)': '인오술', '술(戌)': '인오술',
            '사(巳)': '사유축', '유(酉)': '사유축', '축(丑)': '사유축',
            }
        
        def check_12sinsal(base_ji, target_ji):
            samhap = {
                '인': '화', '오': '화', '술': '화',
                '사': '금', '유': '금', '축': '금',
                '신': '수', '자': '수', '진': '수',
                '해': '목', '묘': '목', '미': '목'
            }
            group = samhap.get(base_ji)
            if not group: return []
            
            found = []
            if group == '화': # In-O-Sul
                if target_ji == '신': found.append("역마")
                elif target_ji == '묘': found.append("도화")
                elif target_ji == '술': found.append("화개")
                elif target_ji == '자': found.append("재살")
            elif group == '금': # Sa-Yu-Chuk
                if target_ji == '해': found.append("역마")
                elif target_ji == '오': found.append("도화")
                elif target_ji == '축': found.append("화개")
            elif group == '수': # Shin-Ja-Jin
                if target_ji == '인': found.append("역마")
                elif target_ji == '유': found.append("도화")
                elif target_ji == '진': found.append("화개")
            elif group == '목': # Hae-Myo-Mi
                if target_ji == '사': found.append("역마")
                elif target_ji == '자': found.append("도화")
                elif target_ji == '미': found.append("화개")
            return found

        res['ji'].extend(check_12sinsal(d_ji, j_char))
        
        if y_ji:
            y_res = check_12sinsal(y_ji, j_char)
            for s in y_res:
                if s not in res['ji']: res['ji'].append(s)

        # Broad Check
        if j_char in ['자', '오', '묘', '유'] and "도화" not in res['ji']: res['ji'].append("도화")
        if j_char in ['인', '신', '사', '해'] and "역마" not in res['ji']: res['ji'].append("역마")
        if j_char in ['진', '술', '축', '미'] and "화개" not in res['ji']: res['ji'].append("화개")

        # === 2. Gilseong / Sal ===
        
        # Baekho
        baekho_pairs = ["갑진", "을미", "병술", "정축", "무진", "임술", "계축"]
        if (g_char + j_char) in baekho_pairs:
            res['gan'].append("백호대살"); res['ji'].append("백호대살")

        # Goegang
        goegang_pairs = ["경진", "경술", "임진", "임술"]  # 표준 4괴강
        if (g_char + j_char) in goegang_pairs:
            res['gan'].append("괴강살"); res['ji'].append("괴강살")
            
        # Hyeonchim
        if g_char in ['갑', '신']: res['gan'].append("현침살")
        if j_char in ['묘', '오', '신']: res['ji'].append("현침살")
        
        # Gwimun (Day Ji base)
        gwimun_map = {'자': '유', '축': '오', '인': '미', '묘': '신', '진': '해', '사': '술',
                      '유': '자', '오': '축', '미': '인', '신': '묘', '해': '진', '술': '사'}
        if gwimun_map.get(d_ji) == j_char: res['ji'].append("귀문관살")

        # Cheoneul (Day Gan base)
        cheoneul_map = {'갑': ['축','미'], '무': ['축','미'], '경': ['축','미'], '을': ['자','신'], '기': ['자','신'], '병': ['해','유'], '정': ['해','유'], '신': ['인','오'], '임': ['사','묘'], '계': ['사','묘']}
        if j_char in cheoneul_map.get(d_gan, []): res['ji'].append("천을귀인")
            
        # Geumyeo (Day Gan base)
        geumyeo_map = {'갑': '진', '을': '사', '병': '미', '정': '신', '무': '미', '기': '신', '경': '술', '신': '해', '임': '축', '계': '인'}
        if geumyeo_map.get(d_gan) == j_char: res['ji'].append("금여성")

        # Hakdang (Day Gan base)
        hakdang_map = {'갑': '해', '을': '오', '병': '인', '정': '유', '무': '인', '기': '유', '경': '사', '신': '자', '임': '신', '계': '묘'}
        if hakdang_map.get(d_gan) == j_char: res['ji'].append("학당귀인")

        # Cheonju (Day Gan base)
        cheonju_map = {'갑': '사', '을': '오', '병': '사', '정': '오', '무': '사', '기': '오', '경': '해', '신': '자', '임': '인', '계': '묘'}
        if cheonju_map.get(d_gan) == j_char: res['ji'].append("천주귀인")
            
        # Gwangwi (Day Gan base)
        gwangwi_map = {'갑': '사', '을': '사', '병': '신', '정': '신', '무': '해', '기': '해', '경': '인', '신': '인', '임': '신', '계': '신'}
        if gwangwi_map.get(d_gan) == j_char: res['ji'].append("관귀학관")

        # Munchang
        munchang_map = {'갑': '사', '을': '오', '병': '신', '정': '유', '무': '신', '기': '유', '경': '해', '신': '자', '임': '인', '계': '묘'}
        if munchang_map.get(d_gan) == j_char: res['ji'].append("문창귀인")

        # Hongyeom
        hongyeom_map = {'갑': '오', '을': '오', '병': '인', '정': '미', '무': '진', '기': '진', '경': '술', '신': '유', '임': '자', '계': '신'}
        if hongyeom_map.get(d_gan) == j_char: res['ji'].append("홍염살")

        # Taegeuk
        taegeuk_map = {'갑': ['자','오'], '을': ['자','오'], '병': ['묘','유'], '정': ['묘','유'], '무': ['진','술','축','미'], '기': ['진','술','축','미'], '경': ['인','해'], '신': ['인','해'], '임': ['사','신'], '계': ['사','신']}
        if j_char in taegeuk_map.get(d_gan, []): res['ji'].append("태극귀인")

        # Jeong-rok / Geon-rok
        # Map for Geon-rok (Day Gan -> Month Ji usually, but technically any column)
        # Gap-In, Eul-Myo, Byeong-Sa...
        rok_map = {'갑': '인', '을': '묘', '병': '사', '정': '오', '무': '사', '기': '오', '경': '신', '신': '유', '임': '해', '계': '자'}
        if rok_map.get(d_gan) == j_char: res['ji'].append("정록")

        # Cheonmun
        if j_char in ['술', '해']: res['ji'].append("천문성")

        # Gwasuk / Goshin (Year Ji base)
        # Hae-Ja-Chuk (Water) -> Gwasuk: Sul
        season_map = {'해':'수','자':'수','축':'수', '인':'목','묘':'목','진':'목', '사':'화','오':'화','미':'화', '신':'금','유':'금','술':'금'}
        yg = season_map.get(y_ji, '')
        
        if yg == '목': # In-Myo-Jin -> Gwa: Chuk
            if j_char == '축': res['ji'].append("과숙살")
        elif yg == '화': # Sa-O-Mi -> Gwa: Jin
            if j_char == '진': res['ji'].append("과숙살")
        elif yg == '금': # Shin-Yu-Sul -> Gwa: Mi
            if j_char == '미': res['ji'].append("과숙살")
        elif yg == '수': # Hae-Ja-Chuk -> Gwa: Sul
            if j_char == '술': res['ji'].append("과숙살")
            
        return res


    def _calculate_sinsal(self, day_branch, target_branch):
        return ""

    def get_gan_ji(self):
        # Restore missing logic start
        st_calc = SolarTermCalculator()
        cutoff_dt = st_calc.find_jeolgi_time(self.year, self.month)
        birth_dt = datetime(self.year, self.month, self.day, self.hour, self.minute)
        
        saju_year = self.year
        if self.month == 1:
            saju_year -= 1
        elif self.month == 2:
            if birth_dt < cutoff_dt:
                saju_year -= 1

        year_gan_idx = (saju_year - 4) % 10
        year_ji_idx = (saju_year - 4) % 12
        year_pillar = CHEONGAN[year_gan_idx] + JIJI[year_ji_idx]
        
        # 3. Determine Month Pillar (based on current month's Jeolgi)
        if birth_dt >= cutoff_dt:
            current_saju_month = self.month
        else:
            current_saju_month = self.month - 1
            if current_saju_month == 0:
                current_saju_month = 12
        
        month_ji_idx = (current_saju_month - 2) % 12
        # Start Gan logic based on Year Gan
        start_gan_idx = (year_gan_idx % 5) * 2 + 2
        month_gan_idx = (start_gan_idx + month_ji_idx) % 10
        real_month_ji_idx = (month_ji_idx + 2) % 12
        month_pillar = CHEONGAN[month_gan_idx] + JIJI[real_month_ji_idx]
        
        # 4. Day Pillar (remains based on calendar days)
        base_date = datetime(1900, 1, 1)
        base_gan_idx = 0 
        base_ji_idx = 10 
        diff_days = (datetime(self.year, self.month, self.day) - base_date).days
        
        day_gan_idx = (base_gan_idx + diff_days) % 10
        day_ji_idx = (base_ji_idx + diff_days) % 12
        day_pillar = CHEONGAN[day_gan_idx] + JIJI[day_ji_idx]
        
        # 5. Hour Pillar
        if self.time_unknown:
            time_pillar = "모름(Unknown)"
        else:
            total_mins = self.hour * 60 + self.minute
            total_mins -= 32 # Standard longitude correction
            if total_mins < 0:
                total_mins += 24 * 60
                diff_days -= 1
            adj_hour = total_mins // 60
            if adj_hour >= 23:
                diff_days += 1
            
            # Recalculate day pillar if time pushes it over
            day_gan_idx = (base_gan_idx + diff_days) % 10
            day_ji_idx = (base_ji_idx + diff_days) % 12
            day_pillar = CHEONGAN[day_gan_idx] + JIJI[day_ji_idx]
            
            time_branch_idx = ((adj_hour + 1) // 2) % 12
            start_time_gan_idx = (day_gan_idx % 5) * 2
            time_gan_idx = (start_time_gan_idx + time_branch_idx) % 10
            time_pillar = CHEONGAN[time_gan_idx] + JIJI[time_branch_idx]
        
        return {
            'year': year_pillar, 'month': month_pillar, 'day': day_pillar, 'hour': time_pillar,
            'year_gan_idx': year_gan_idx, 'month_gan_idx': month_gan_idx, 'month_ji_idx': real_month_ji_idx 
            }


    def _calculate_daewoon_num(self, is_forward):
        st_calc = SolarTermCalculator()
        current_jeolgi_dt = st_calc.find_jeolgi_time(self.year, self.month)
        birth_dt = datetime(self.year, self.month, self.day, self.hour, self.minute)
        
        is_after_current_jeolgi = birth_dt >= current_jeolgi_dt
        # [Fixed] 날짜가 같아도 시간 비교 결과를 신뢰함 (정밀 데이터 사용)
        # if birth_dt.date() == current_jeolgi_dt.date(): is_after... line removed

        if is_forward:
            if is_after_current_jeolgi:
                if self.month == 12:
                    next_year = self.year + 1
                    next_month = 1
                else:
                    next_year = self.year
                    next_month = self.month + 1
                next_jeolgi_dt = st_calc.find_jeolgi_time(next_year, next_month)
                diff_seconds = (next_jeolgi_dt - birth_dt).total_seconds()
            else:
                diff_seconds = (current_jeolgi_dt - birth_dt).total_seconds()
        else:
            if is_after_current_jeolgi:
                diff_seconds = (birth_dt - current_jeolgi_dt).total_seconds()
            else:
                if self.month == 1:
                    prev_year = self.year - 1
                    prev_month = 12
                else:
                    prev_year = self.year
                    prev_month = self.month - 1
                prev_jeolgi_dt = st_calc.find_jeolgi_time(prev_year, prev_month)
                diff_seconds = (birth_dt - prev_jeolgi_dt).total_seconds()
                
        diff_days = diff_seconds / (24 * 3600)
        import math
        daewoon_num = int(round(diff_days / 3))
        
        if daewoon_num <= 0: daewoon_num = 0 # 일부 만세력 0 시작 허용
        if daewoon_num > 10: daewoon_num = 10
        
        return daewoon_num

    def get_daewoon(self, year_gan_idx, month_gan_idx, month_ji_idx):
        is_year_yang = (year_gan_idx % 2 == 0)
        is_male = (self.gender == 'male')
        is_forward = (is_year_yang == is_male)
        
        start_age = self._calculate_daewoon_num(is_forward)
        
        daewoon_list = []
        curr_gan = month_gan_idx
        curr_ji = month_ji_idx
        
        # Base Year for calculation
        # Assuming daewoon_num is Korean Age (Standard Saju).
        # Korean Age 1 = Birth Year.
        # Start Year = Birth Year + (Start Age - 1)
        base_year = self.adjusted_dt.year
        
        # [Posteller Style] 대운수는 만나이/한국나이 혼용되나, 보통 '대운수'부터 10년 단위.
        # 예: 대운수 3 -> 3~12세, 13~22세...
        for i in range(10): 
            if is_forward:
                curr_gan = (curr_gan + 1) % 10
                curr_ji = (curr_ji + 1) % 12
            else:
                curr_gan = (curr_gan - 1 + 10) % 10
                curr_ji = (curr_ji - 1 + 12) % 12
            pillar = CHEONGAN[curr_gan] + JIJI[curr_ji]
            
            # Start age for this block
            block_start_age = start_age + (i * 10)
            block_end_age = block_start_age + 9
            
            # Calculate Gregorian Year
            # age세 = 출생년도 + (age - 1)  (if Korean age 1 at birth)
            # ex: born 1966. age 3 = 1968. (1966 + 3 - 1)
            current_start_year = base_year + block_start_age - 1
            
            # Calculate Seun (Yearly Luck) for this Daewoon block (10 years)
            seun_list = []
            for y_idx in range(10):
                seun_year = current_start_year + y_idx
                seun_age = block_start_age + y_idx
                # Calculate Seun Ganji
                # Base year 1984 is Gap-Ja (Index 0, 0)
                # 1924 is also Gap-Ja
                diff = seun_year - 1924
                g_i = diff % 10
                j_i = diff % 12
                seun_ganji = f"{CHEONGAN[g_i]}{JIJI[j_i]}"
                # Calculate Monthly Luck (Wolun) for this Seun Year
                monthly_luck = self._calculate_monthly_plans(seun_year)
                seun_list.append({"year": seun_year, "age": seun_age, "ganji": seun_ganji, "monthly_luck": monthly_luck})

            # Check Interaction (Daewoon Ji vs Ilji/Wolji)
            dw_ji = JIJI[curr_ji].split('(')[0]
            interaction_note = self._check_daewoon_interaction(dw_ji)

            daewoon_list.append({
                "age": block_start_age,
                "end_age": block_end_age, 
                "ganji": pillar,
                "year": current_start_year,
                "end_year": current_start_year + 9, 
                "seun": seun_list,
                "highlight": interaction_note
            })
            
        return {"direction": "순행" if is_forward else "역행", "pillars": daewoon_list}

    def _check_daewoon_interaction(self, dw_ji):
        """대운 지지와 일지/월지의 합충형 관계 분석"""
        notes = []
        
        # 1. 일지 (Day Branch) Check - Most Important (Personal)
        if self.day_ji_char:
            d_ji = self.day_ji_char.split('(')[0]
            # Chung
            if self._calculate_jiji_chung(dw_ji, d_ji):
                notes.append(f"일지충({d_ji}{dw_ji}충: 신변변동)")
            # Hap (Yukhap)
            elif self._calculate_jiji_yukhap(dw_ji, d_ji):
                notes.append(f"일지합({d_ji}{dw_ji}합: 안정/결혼)")
            # Hyeong
            elif self._calculate_hyeong(dw_ji, d_ji):
                notes.append(f"일지형({d_ji}{dw_ji}형: 조정/수술)")
            # Wonjin
            elif self._calculate_wonjin(dw_ji, d_ji):
                notes.append(f"일지원진({d_ji}{dw_ji}: 민감/갈등)")

        # 2. 월지 (Month Branch) Check - Social/Career
        if self.month_ji_char:
            m_ji = self.month_ji_char.split('(')[0]
            if self._calculate_jiji_chung(dw_ji, m_ji):
                notes.append(f"월지충({m_ji}{dw_ji}충: 사회적변동)")
            elif self._calculate_hyeong(dw_ji, m_ji):
                notes.append(f"월지형({m_ji}{dw_ji}형: 직업조정)")
                
        return " / ".join(notes) if notes else ""
            
        return {"direction": "순행" if is_forward else "역행", "pillars": daewoon_list}

    def _calculate_monthly_plans(self, year):
        """
        Calculate Monthly Ganji (Wolun) for a specific Gregorian Year.
        Logic:
        - Jan: 12th month (Chuk) of previous Saju Year.
        - Feb-Dec: 1st-11th months (In, Myo...) of current Saju Year.
        Duhuibeop (Head-Matching Rule) for Month Gan:
        - Year Gan gap/gi -> Tiger is Byung-In ...
        """
        from saju_data import CHEONGAN, JIJI
        
        # 1. Determine Year Gan Index for CURRENT year and PREVIOUS year
        # 1984 = Gap-Ja (Gap=0). (year - 4) % 10 is standard formula for Gan index
        curr_year_gan_idx = (year - 4) % 10
        prev_year_gan_idx = (year - 1 - 4) % 10
        
        months = []
        
        for m in range(1, 13):
            # Target Gan and Ji indices
            t_gan_idx = 0
            t_ji_idx = 0
            
            if m == 1:
                # January: Belongs to previous year's 12th month (Chuk)
                # Tiger(In) of prev year starts at:
                start_gan = (prev_year_gan_idx % 5) * 2 + 2 # 0(Gap)->2(Byung), etc.
                # Chuk is Tiger + 11
                t_gan_idx = (start_gan + 11) % 10
                t_ji_idx = 1 # Chuk is index 1 in standard JIJI list ['Ja', 'Chuk', 'In'...] ?? 
                # Wait, JIJI = ['자', '축', '인', '묘'...] -> Ja=0, Chuk=1. Correct.
            else:
                # Feb (2) ~ Dec (12)
                # Maps to In (Tiger) ~ Ja (Rat) of CURRENT year
                # m=2 (Feb) -> In (Tiger). JIJI index 2.
                # m=12 (Dec) -> Ja (Rat). JIJI index 0.
                
                # Logic:
                # m=2 (Feb) -> In (Tiger, idx 2)
                # m=3 (Mar) -> Myo (Rabbit, idx 3)
                # ...
                # m=11 (Nov) -> Hae (Pig, idx 11)
                # m=12 (Dec) -> Ja (Rat, idx 0)
                
                # Formula for Ji index:
                # If m==12: 0 (Ja)
                # Else: m 
                # Let's check: m=2 -> 2(In). Correct. m=11 -> 11(Hae). Correct.
                t_ji_idx = 0 if m == 12 else m
                
                # Calculate Gan
                # Start Gan for Tiger (Feb/m=2) of CURRENT year
                start_gan = (curr_year_gan_idx % 5) * 2 + 2
                
                # Offset from Tiger (m=2)
                # m=2 -> offset 0
                # m=3 -> offset 1
                # ...
                # m=12 -> offset 10
                offset = m - 2
                t_gan_idx = (start_gan + offset) % 10
            
            gan_char = CHEONGAN[t_gan_idx]
            ji_char = JIJI[t_ji_idx]
            months.append(f"{m}월({gan_char}{ji_char})")
            
        return " ".join(months)

    def _calculate_korean_age(self, birth_year):
        """만 나이 기반이 아닌 한국 나이 (태어난 해 = 1세) 계산"""
        # Simply current_year - birth_year + 1
        current_year = datetime.now().year
        return current_year - birth_year + 1

    def analyze_ohaeng(self, pillars):
        counts = {'목(Tree)': 0, '화(Fire)': 0, '토(Earth)': 0, '금(Metal)': 0, '수(Water)': 0}
        c_map = {'갑(甲)': '목(Tree)', '을(乙)': '목(Tree)', '병(丙)': '화(Fire)', '정(丁)': '화(Fire)', '무(戊)': '토(Earth)', '기(己)': '토(Earth)', '경(庚)': '금(Metal)', '신(辛)': '금(Metal)', '임(壬)': '수(Water)', '계(癸)': '수(Water)'}
        j_map = {'인(寅)': '목(Tree)', '묘(卯)': '목(Tree)', '사(巳)': '화(Fire)', '오(午)': '화(Fire)', '진(辰)': '토(Earth)', '술(戌)': '토(Earth)', '축(丑)': '토(Earth)', '미(未)': '토(Earth)', '신(申)': '금(Metal)', '유(酉)': '금(Metal)', '해(亥)': '수(Water)', '자(子)': '수(Water)'}
        
        for key in ['year', 'month', 'day', 'hour']: 
            pillar = pillars[key]
            if pillar == "모름(Unknown)": continue
            parts = re.findall(r'.\(.\)', pillar)
            if len(parts) == 2:
                gan, ji = parts[0], parts[1]
                if gan in c_map: counts[c_map[gan]] += 1
                if ji in j_map: counts[j_map[ji]] += 1
        return counts

    def _calculate_cheongan_hap(self, gan1, gan2):
        hap_map = {'갑': '기', '을': '경', '병': '신', '정': '임', '무': '계', '기': '갑', '경': '을', '신': '병', '임': '정', '계': '무'}
        g1 = gan1.split('(')[0]
        g2 = gan2.split('(')[0]
        if hap_map.get(g1) == g2: return f"{g1}{g2}합"
        return ""

    def _calculate_cheongan_chung(self, gan1, gan2):
        g1 = gan1.split('(')[0]; g2 = gan2.split('(')[0]
        pairs = [{'갑', '경'}, {'을', '신'}, {'병', '임'}, {'정', '계'}]
        if {g1, g2} in pairs: return "충"
        # 추가 천간충 (무갑, 기을 등)
        extra_pairs = [{'무', '갑'}, {'기', '을'}, {'경', '병'}, {'신', '정'}, {'임', '무'}, {'계', '기'}]
        if {g1, g2} in extra_pairs: return "충"
        return ""

    def _calculate_jiji_hap(self, ji1, ji2):
        hap_map = {'자': '축', '축': '자', '인': '해', '해': '인', '묘': '술', '술': '묘', '진': '유', '유': '진', '사': '신', '신': '사', '오': '미', '미': '오'}
        j1 = ji1.split('(')[0]; j2 = ji2.split('(')[0]
        if hap_map.get(j1) == j2: return f"{j1}{j2}육합"
        return ""

    def _calculate_jiji_chung(self, ji1, ji2):
        chung_map = {'자': '오', '오': '자', '축': '미', '미': '축', '인': '신', '신': '인', '묘': '유', '유': '묘', '진': '술', '술': '진', '사': '해', '해': '사'}
        j1 = ji1.split('(')[0]; j2 = ji2.split('(')[0]
        if chung_map.get(j1) == j2: return f"{j1}{j2}충"
        return ""
        
    def _calculate_wonjin(self, ji1, ji2):
        wonjin_map = {'자': '미', '미': '자', '축': '오', '오': '축', '인': '유', '유': '인', '묘': '신', '신': '묘', '진': '해', '해': '진', '사': '술', '술': '사'}
        j1 = ji1.split('(')[0]; j2 = ji2.split('(')[0]
        if wonjin_map.get(j1) == j2: return f"{j1}{j2}원진"
        return ""

    def _calculate_jiji_yukhap(self, j1, j2):
        pairs = [({'자', '축'}, '토'), ({'인', '해'}, '목'), ({'묘', '술'}, '화'), ({'진', '유'}, '금'), ({'사', '신'}, '수'), ({'오', '미'}, '화')]
        s1 = j1.split('(')[0]; s2 = j2.split('(')[0]
        for p_set, element in pairs:
            if {s1, s2} == p_set: return element
        return ""

    def _calculate_hyeong(self, ji1, ji2):
        s1 = ji1.split('(')[0]; s2 = ji2.split('(')[0]
        # 인사신 삼형: 인-사-신 (Three Penalty) often required fully. 
        # But commonly Sa-Shin is Hyeong+Hap. In-Shin is Chung+Hyeong. 
        # In-Sa is just Hae+Hyeong. Posteller seems to exclude In-Sa as Hyeong.
        if {s1, s2} == {'사', '신'}: return "무은지형" # Removed In-Sa
        if {s1, s2} == {'축', '술'} or {s1, s2} == {'술', '미'}: return "지세지형"
        if {s1, s2} == {'자', '묘'}: return "무례지형"
        if s1 == s2 and s1 in ['진', '오', '유', '해']: return "자형"
        return ""

    def _calculate_pa(self, ji1, ji2):
        pa_map = {'자': '유', '유': '자', '축': '진', '진': '축', '인': '해', '해': '인', '묘': '오', '오': '묘', '사': '신', '신': '사', '술': '미', '미': '술'}
        j1 = ji1.split('(')[0]; j2 = ji2.split('(')[0]
        if pa_map.get(j1) == j2: return f"{j1}{j2}파"
        return ""

    def _calculate_hae(self, ji1, ji2):
        hae_map = {'자': '미', '미': '자', '축': '오', '오': '축', '인': '사', '사': '인', '묘': '진', '진': '묘', '신': '해', '해': '신', '유': '술', '술': '유'}
        j1 = ji1.split('(')[0]; j2 = ji2.split('(')[0]
        if hae_map.get(j1) == j2: return f"{j1}{j2}해"
        return ""

    def _calculate_gongmang(self, gan, ji): # Renamed args for clarity: expecting Gan/Ji of a pilar to find ITS group gongmang, OR usually finding Day Pillar's gongmang
        # Method: Find position of Gan in 0-9. Find position of Ji in 0-11.
        # Diff = (Ji_idx - Gan_idx) % 12.
        # Gongmang are the two branches at Diff-1 and Diff (in modulo 12).
        # Actually simpler: Gongmang is defined by the Xun (group of 10).
        g_idx = CHEONGAN.index(gan)
        j_idx = JIJI.index(ji)
        
        # Calculate the start of the Xun (Gap-??)
        # Shift Ji back by Gan's index
        start_ji_idx = (j_idx - g_idx) % 12
        
        # Gongmang are the two branches following the 10th stem (Gui)
        # The 10th stem is at index 9.
        # So (start_ji_idx + 10) % 12 and (start_ji_idx + 11) % 12
        gm1_idx = (start_ji_idx + 10) % 12
        gm2_idx = (start_ji_idx + 11) % 12
        
        return [JIJI[gm1_idx].split('(')[0], JIJI[gm2_idx].split('(')[0]]

    def _calculate_12unseong(self, day_gan, target_ji):
        # Ship-i-unseong (12 Stages of Life) based on Day Gan vs Target Branch
        # Use simple map logic or index math
        # Day Gan Polarities:
        # Yang: Gap(In), Byeong/Mu(In), Gyeong(Sa), Im(Shin) -> Start 'Jangsaeng'
        # Yin:  Eul(O), Jeong/Gi(Yu), Shin(Ja), Gye(Myo)   -> Start 'Jangsaeng' IS DIFFERENT (Reverse)
        d_gan = day_gan.split('(')[0]
        t_ji = target_ji.split('(')[0]
        
        # Ordering: Jangsaeng, Mokyok, Gwandae, Geonrok, Jewang, Soe, Byeong, Sa, Myo, Jeol, Tae, Yang
        stages = ["장생", "목욕", "관대", "건록", "제왕", "쇠", "병", "사", "묘", "절", "태", "양"]
        ji_order = ['자','축','인','묘','진','사','오','미','신','유','술','해']
        
        # Starting Branch for Jangsaeng (Growth) for each Stem
        yang_starts = {'갑': '해', '병': '인', '무': '인', '경': '사', '임': '신'}
        yin_starts = {'을': '오', '정': '유', '기': '유', '신': '자', '계': '묘'}
        
        t_idx = ji_order.index(t_ji)

        if d_gan in yang_starts:
            start_ji = yang_starts[d_gan]
            s_idx = ji_order.index(start_ji)
            # Yang stems count forward
            # Distance from start
            diff = (t_idx - s_idx) % 12
            return stages[diff]
        elif d_gan in yin_starts:
            start_ji = yin_starts[d_gan]
            s_idx = ji_order.index(start_ji)
            # Yin stems count backward
            # Jangsaeng is at start_ji. 
            # If t_ji is start_ji, diff 0. 
            # Count BACKWARDS: s_idx - t_idx
            diff = (s_idx - t_idx) % 12
            return stages[diff]
        return ""

    def _calculate_jijanggan(self, ji):
        # Hidden Stems
        j = ji.split('(')[0]
        map_data = {
            '자': ['임', '계'], '축': ['계', '신기', '기'], '인': ['무', '병', '갑'], 
            '묘': ['갑', '을'], '진': ['을', '계', '무'], '사': ['무', '경', '병'], 
            '오': ['병', '기', '정'], '미': ['정', '을', '기'], '신': ['무', '임', '경'], 
            '유': ['경', '신'], '술': ['신', '정', '무'], '해': ['무', '갑', '임']
        }
        # 축, 진, 술 -> middle is special compound? Standard is usually 3. 
        # Chuk: Gye (9), Shin (3), Gi (18) -> Adjusted: Gye, Shin, Gi
        # Creating standard list strings
        if j in map_data:
            return map_data[j]
        return []

    def _calculate_nabeum(self, gan, ji):
        # Nabeum (Sound) - Simplified mapping
        # 60 Ganji mapping to Nabeum Name
        key = gan.split('(')[0] + ji.split('(')[0]
        nabeum_map = {
            '갑자': '해중금', '을축': '해중금', '병인': '노중화', '정묘': '노중화', '무진': '대림목', '기사': '대림목',
            '경오': '로방토', '신미': '로방토', '임신': '검봉금', '계유': '검봉금', '갑술': '산두화', '을해': '산두화',
            '병자': '간하수', '정축': '간하수', '무인': '성두토', '기묘': '성두토', '경진': '백랍금', '신사': '백랍금',
            '임오': '양류목', '계미': '양류목', '갑신': '천중수', '을유': '천중수', '병술': '옥상토', '정해': '옥상토',
            '무자': '벽력화', '기축': '벽력화', '경인': '송백목', '신묘': '송백목', '임진': '장류수', '계사': '장류수',
            '갑오': '사중금', '을미': '사중금', '병신': '산하화', '정유': '산하화', '무술': '평지목', '기해': '평지목',
            '경자': '벽상토', '신축': '벽상토', '임인': '금박금', '계묘': '금박금', '갑진': '복등화', '을사': '복등화',
            '병오': '천하수', '정미': '천하수', '무신': '대역토', '기유': '대역토', '경술': '차천금', '신해': '차천금',
            '임자': '상자목', '계축': '상자목', '갑인': '대계수', '을묘': '대계수', '병진': '사중토', '정사': '사중토',
            '무오': '천상화', '기미': '천상화', '경신': '석류목', '신유': '석류목', '임술': '大海수', '계해': '大海수'
        }
        return nabeum_map.get(key, "")

    def get_result_json(self):
        pillars = self.get_gan_ji()
        
        # Extract Chars
        y_gan, y_ji = pillars['year'][0:2], pillars['year'][2:4]
        m_gan, m_ji = pillars['month'][0:2], pillars['month'][2:4]
        d_gan, d_ji = pillars['day'][0:2], pillars['day'][2:4]
        h_gan, h_ji = pillars['hour'][0:2], pillars['hour'][2:4] if pillars['hour'] != "모름(Unknown)" else ("", "")

        # Store for internal use in sinsal calc
        self.day_gan_char = d_gan.split('(')[0]
        self.day_ji_char = d_ji.split('(')[0]
        self.year_gan_char = y_gan.split('(')[0]; self.year_ji_char = y_ji.split('(')[0]
        self.month_gan_char = m_gan.split('(')[0]; self.month_ji_char = m_ji.split('(')[0]
        self.hour_gan_char = h_gan.split('(')[0] if h_gan else ""; self.hour_ji_char = h_ji.split('(')[0] if h_ji else ""

        # Basic Info
        info = {
            "name": self.name,
            "gender": self.gender,
            "solar_date": {"year": self.year, "month": self.month, "day": self.day, "hour": self.hour, "minute": self.minute},
            # Dummy Lunar (should implement real conversion if needed for display)
            "lunar_date": {"year": self.year, "month": self.month, "day": self.day}, 
            "ddi": YUKCHIN[JIJI.index(pillars['year'][2:])]['animal'], # Simple Zodiac from Year Branch
            "age": datetime.now().year - self.year + 1 # Korean Age
        }

        # Calculate Derived Data
        # Gongmang (Void) - Calculated based on Day Pillar
        gongmang_list = self._calculate_gongmang(pillars['day'][0:2], pillars['day'][2:])
        
        # 12 Unseong (Day Gan vs Each Ji)
        unseong = {
            'year': self._calculate_12unseong(pillars['day'][0:2], pillars['year'][2:]),
            'month': self._calculate_12unseong(pillars['day'][0:2], pillars['month'][2:]),
            'day': self._calculate_12unseong(pillars['day'][0:2], pillars['day'][2:]),
            'hour': self._calculate_12unseong(pillars['day'][0:2], pillars['hour'][2:]) if h_ji else ""
        }
        
        # Jijanggan
        jijanggan = {
            'year': self._calculate_jijanggan(pillars['year'][2:]),
            'month': self._calculate_jijanggan(pillars['month'][2:]),
            'day': self._calculate_jijanggan(pillars['day'][2:]),
            'hour': self._calculate_jijanggan(pillars['hour'][2:]) if h_ji else []
        }
        
        # Nabeum
        nabeum = {
            'year': self._calculate_nabeum(pillars['year'][0:2], pillars['year'][2:]),
            'month': self._calculate_nabeum(pillars['month'][0:2], pillars['month'][2:]),
            'day': self._calculate_nabeum(pillars['day'][0:2], pillars['day'][2:]),
            'hour': self._calculate_nabeum(pillars['hour'][0:2], pillars['hour'][2:]) if h_ji else ""
        }
        
        # Sinsal (Divine Spirits)
        sinsal_raw = {
            'year': self._calculate_pillar_sinsal(y_gan, y_ji, 'year'),
            'month': self._calculate_pillar_sinsal(m_gan, m_ji, 'month'),
            'day': self._calculate_pillar_sinsal(d_gan, d_ji, 'day'),
            'hour': self._calculate_pillar_sinsal(h_gan, h_ji, 'hour') if h_ji else {'gan':[], 'ji':[]}
        }
        
        # Flatten sinsal for simpler display if needed, or keep structured
        
        # Daewoon
        daewoon_data = self.get_daewoon(pillars['year_gan_idx'], pillars['month_gan_idx'], pillars['month_ji_idx'])
        
        # Five Elements
        five_elements = self.analyze_ohaeng(pillars)

        return {
            "info": info,
            "four_pillars": {
                "year": {"gan": y_gan, "ji": y_ji},
                "month": {"gan": m_gan, "ji": m_ji},
                "day": {"gan": d_gan, "ji": d_ji},
                "hour": {"gan": h_gan, "ji": h_ji}
            },
            "five_elements": five_elements,
            "daewoon": daewoon_data,
            "derived": {
                "gongmang": gongmang_list,
                "unseong": unseong,
                "jijanggan": jijanggan,
                "nabeum": nabeum,
                "sinsal": sinsal_raw
            }
        }
        diff = (ji_idx - gan_idx) % 12
        gongmang_map = {0: ['술(戌)', '해(亥)'], 10: ['신(申)', '유(酉)'], 8: ['오(午)', '미(未)'], 6: ['진(辰)', '사(巳)'], 4: ['인(寅)', '묘(卯)'], 2: ['자(子)', '축(丑)']}
        return gongmang_map.get(diff, [])

    def _calculate_cheoneuigwin(self, day_gan, branch):
        gan = day_gan.split('(')[0]; ji = branch.split('(')[0]
        # Cheoneul Guiin Map (Standard)
        # Gab/Mu/Gyeong -> Chuk/Mi
        # Eul/Gi -> Ja/Shin
        # Byeong/Jeong -> Hae/Yu
        # Im/Gye -> Sa/Myo
        # Shin -> O/In
        map_data = {
            '갑': ['축', '미'], '무': ['축', '미'], '경': ['축', '미'], 
            '을': ['자', '신'], '기': ['자', '신'], 
            '병': ['해', '유'], '정': ['해', '유'], 
            '임': ['사', '묘'], '계': ['사', '묘'], 
            '신': ['오', '인']
            }
        if ji in map_data.get(gan, []): return "천을귀인"
        return ""

    def _calculate_hongyeom(self, day_gan, branch):
        gan = day_gan.split('(')[0]; ji = branch.split('(')[0]
        pairs = [('갑', '오'), ('병', '인'), ('정', '미'), ('무', '진'), ('경', '술'), ('신', '유'), ('임', '자'), ('계', '신'), ('경', '신'), ('을', '오'), ('기', '진')]
        if (gan, ji) in pairs: return "홍염살"
        return ""

    def _calculate_gosin(self, year_branch, branch):
        y_ji = year_branch.split('(')[0]; ji = branch.split('(')[0]
        groups = {'인': '사', '묘': '사', '진': '사', '사': '신', '오': '신', '미': '신', '신': '해', '유': '해', '술': '해', '해': '인', '자': '인', '축': '인'}
        if groups.get(y_ji) == ji: return "고신살"
        return ""

    def _calculate_taegeuk(self, day_gan, branch):
        gan = day_gan.split('(')[0]; ji = branch.split('(')[0]
        map_data = {'갑': ['자', '오'], '을': ['자', '오'], '병': ['유', '묘'], '정': ['유', '묘'], '무': ['진', '술', '축', '미'], '기': ['진', '술', '축', '미'], '경': ['인', '해'], '신': ['인', '해'], '임': ['사', '신'], '계': ['사', '신']}
        if ji in map_data.get(gan, []): return "태극귀인"
        return ""

    def _calculate_mungok(self, day_gan, branch):
        gan = day_gan.split('(')[0]; ji = branch.split('(')[0]
        pairs = [('갑', '해'), ('을', '자'), ('병', '인'), ('정', '묘'), ('무', '인'), ('기', '묘'), ('경', '사'), ('신', '오'), ('임', '신'), ('계', '유')]
        if (gan, ji) in pairs: return "문곡귀인"
        return ""

    def _calculate_gwangwi(self, day_gan, branch):
        """관귀학관: 관성이 장생하는 지지"""
        gan = day_gan.split('(')[0]; ji = branch.split('(')[0]
        # Logic: Gwan's Jangsaeng.
        # Tree(Gab/Eul) -> Gwan=Metal -> Jangsaeng=Sa
        # Fire(Byeong/Jeong) -> Gwan=Water -> Jangsaeng=Shin
        # Earth(Mu/Gi) -> Gwan=Wood -> Jangsaeng=Hae
        # Metal(Gyeong/Shin) -> Gwan=Fire -> Jangsaeng=In
        # Water(Im/Gye) -> Gwan=Earth -> Jangsaeng=In (Fire/Earth same cycle) or Sa (if Earth=Water variant)
        # Posteller uses standard Fire/Earth same cycle for Jangsaeng. Im/Gye -> In.
        
        map_data = {
            '갑': ['사'], '을': ['사'],
            '병': ['신'], '정': ['신'],
            '무': ['해'], '기': ['해'],
            '경': ['인'], '신': ['인'],
            '임': ['인'], '계': ['인']
            }
        return "관귀학관" if ji in map_data.get(gan, []) else ""

    def _calculate_hwangeundaesa(self, gan, ji):
        """황은대사: 임금의 은혜를 입는 길신"""
        if gan == "모름" or ji == "모름": return False
        g = gan.split('(')[0]; j = ji.split('(')[0]
        # Known Hwangeun pairs: Gyeong-Jin is typical.
        # Adding Gyeong-Jin as confirmed by user.
        pairs = [('경', '진')]
        return (g, j) in pairs

    def _calculate_jeongrok(self, day_gan, branch):
        gan = day_gan.split('(')[0]; ji = branch.split('(')[0]
        pairs = [('갑', '인'), ('을', '묘'), ('병', '사'), ('정', '오'), ('무', '사'), ('기', '오'), ('경', '신'), ('신', '유'), ('임', '해'), ('계', '자')]
        if (gan, ji) in pairs: return "정록"
        return ""
        
    def _calculate_geumyeo(self, day_gan, branch):
        gan = day_gan.split('(')[0]; ji = branch.split('(')[0]
        pairs = [('갑', '진'), ('을', '사'), ('병', '미'), ('정', '신'), ('무', '미'), ('기', '신'), ('경', '술'), ('신', '해'), ('임', '축'), ('계', '인')]
        if (gan, ji) in pairs: return "금여성"
        return ""
        
    def _calculate_gwasuk(self, year_branch, branch):
        y_ji = year_branch.split('(')[0]; ji = branch.split('(')[0]
        groups = {'인': '축', '묘': '축', '진': '축', '사': '진', '오': '진', '미': '진', '신': '미', '유': '미', '술': '미', '해': '술', '자': '술', '축': '술'}
        if groups.get(y_ji) == ji: return "과숙살"
        return ""

    def _calculate_baekho(self, gan, ji):
        """백호대살 계산: 천간과 지지의 조합"""
        if gan == "모름" or ji == "모름": return False
        g = gan.split('(')[0]; j = ji.split('(')[0]
        baekho_pairs = {
            '갑': '술', '을': '미', '병': '술', '정': '축',
            '무': '진', '기': '축', '경': '진', '신': '축', # 신금 백호는 신축? 아니 보통 신금백호는 없음. 수정 필요
            '임': '술', '계': '축' 
            }
        # Standard Baekho: Gab-Jin, Eul-Mi, Byeong-Sul, Jeong-Chuk, Mu-Jin, Gi-Chuk, Gyeong-Jin, Im-Sul, Gye-Chuk?
        # Let's use the commonly accepted list:
        # Gab-Jin, Eul-Mi, Byeong-Sul, Jeong-Chuk, Mu-Jin, Im-Sul, Gye-Chuk.
        # My previous list was: '갑': '술', '을': '해' (Wrong).
        # Correct List:
        baekho_pairs = {
            '갑': '진', '을': '미', '병': '술', '정': '축',
            '무': '진', '임': '술', '계': '축'
            }
        # Ki-Chuk, Gyeong-Jin? Some references say 7 Baekho.
        # Standard 7: 甲辰, 乙未, 丙戌, 丁丑, 戊辰, 壬戌, 癸丑.
        return baekho_pairs.get(g) == j
        return baekho_pairs.get(g) == j


    def _calculate_gwaegang(self, gan, ji):
        """괴강살 계산: 경진, 경술, 임신, 무술 일주/시주"""
        if gan == "모름" or ji == "모름": return False
        g = gan.split('(')[0]; j = ji.split('(')[0]
        gwaegang_pairs = [
            ('경', '진'),  # 경진
            ('경', '술'),  # 경술
            ('임', '신'),  # 임신
            ('무', '술')   # 무술
        ]
        return (g, j) in gwaegang_pairs

    def _calculate_gwimun(self, day_ji, target_ji):
        """귀문관살 계산: 일지 기준으로 특정 지지에 나타남 (자미, 축오, 인유, 묘신, 진해, 사술 + 변형)"""
        if day_ji == "모름" or target_ji == "모름": return False
        d_ji = day_ji.split('(')[0]; t_ji = target_ji.split('(')[0]

        # 귀문관살 (Posteller Style - 양방향)
        # 진-해, 해-진 양쪽 다 귀문관살 적용
        gwimun_map = {
            '자': ['미'], '미': ['자', '인'], 
            '축': ['오'], '오': ['축', '신'], 
            '인': ['유', '미'], '유': ['인'], 
            '묘': ['신'], '신': ['묘'],
            '진': ['해'], '해': ['진', '술'],  # 해-진에도 귀문관
            '사': ['술'], '술': ['사', '해']
            }

        return t_ji in gwimun_map.get(d_ji, [])

    def _calculate_amlok(self, day_gan, branch):
        """암록: 재물을 돕는 숨겨진 길신"""
        g = day_gan.split('(')[0]; j = branch.split('(')[0]
        # 甲-亥, 乙-戌, 丙-申, 丁-未, 戊-申, 己-未, 庚-巳, 辛-辰, 壬-寅, 癸-丑
        map_data = {'갑':'해', '을':'술', '병':'신', '정':'미', '무':'신', '기':'미', '경':'사', '신':'진', '임':'인', '계':'축'}
        return map_data.get(g) == j

    def _calculate_yangin(self, day_gan, branch):
        """양인살: 양간의 제왕지 + 음간의 관대지(포스텔러 확장)"""
        g = day_gan.split('(')[0]; j = branch.split('(')[0]
        # Yangin Pairs (Yang Stems - Standard)
        # 甲-卯, 丙-午, 戊-午, 庚-酉, 壬-子
        # Yin Stems (Extended - Posteller style)
        # 乙-辰, 丁-未, 己-未, 辛-戌, 癸-丑
        yangin_pairs = [
            ('갑','묘'), ('병','오'), ('무','오'), ('경','유'), ('임','자'),
            ('을','진'), ('정','미'), ('기','미'), ('신','술'), ('계','축')
        ]
        return (g, j) in yangin_pairs

    def _calculate_geumyeo(self, day_gan, branch):
        """금여성 계산: 일간+지지 조합"""
        if day_gan == "모름" or branch == "모름": return False
        d_gan = day_gan.split('(')[0]; ji = branch.split('(')[0]
        geumyeo_pairs = [
            ('갑', '진'), ('을', '사'), ('병', '미'), ('정', '신'),
            ('무', '미'), ('기', '신'), ('경', '술'), ('신', '해'),
            ('임', '축'), ('계', '인')
        ]
        return (d_gan, ji) in geumyeo_pairs

    def _calculate_munchang(self, day_gan, branch):
        """문창귀인 계산: 일간별 특정 지지"""
        if day_gan == "모름" or branch == "모름": return False
        d_gan = day_gan.split('(')[0]; ji = branch.split('(')[0]
        munchang_map = {
            '갑': '사', '을': '오', '병': '신', '정': '유',
            '무': '신', '기': '유', '경': '해', '신': '자',
            '임': '인', '계': '묘'
            }
        return munchang_map.get(d_gan) == ji

    def _calculate_mungok(self, day_gan, branch):
        """문곡귀인 계산: 일간별 특정 지지"""
        if day_gan == "모름" or branch == "모름": return False
        d_gan = day_gan.split('(')[0]; ji = branch.split('(')[0]
        mungok_map = {
            '갑': '해', '을': '자', '병': '인', '정': '묘',
            '무': '인', '기': '묘', '경': '사', '신': '오',
            '임': '신', '계': '유'
            }
        return mungok_map.get(d_gan) == ji

    def _calculate_nabeum(self, ganji):
        """납음오행 계산"""
        if not ganji or ganji == "모름(Unknown)" or ganji == "모름": return ""

        # Use _split_pillar logic to separate Gan and Ji parts from "Gan(H)Ji(H)"
        import re
        parts = re.findall(r'[가-힣]', ganji)
        # Typically "갑(甲)자(子)" -> ['갑', '甲', '자', '子']
        # We want the first Hangul of Gan and first Hangul of Ji.
        # But clearer is to split by pattern.
        
        # Simplified robust parsing
        # Remove all parentheses and contents
        clean = re.sub(r'\([^)]*\)', '', ganji) # "갑자"
        clean = re.sub(r'\s+', '', clean) # Remove spaces
        
        if len(clean) < 2: return ""
        
        gan_char = clean[0]
        ji_char = clean[1]
            
        # 60 Ganji Nabeum Table
        nabeum_map = {
            '갑자': '해중금', '을축': '해중금', '병인': '노중화', '정묘': '노중화', '무진': '대림목', '기사': '대림목',
            '경오': '로방토', '신미': '로방토', '임신': '검봉금', '계유': '검봉금', '갑술': '산두화', '을해': '산두화',
            '병자': '간하수', '정축': '간하수', '무인': '성두토', '기묘': '성두토', '경진': '백랍금', '신사': '백랍금',
            '임오': '양류목', '계미': '양류목', '갑신': '천중수', '을유': '천중수', '병술': '옥상토', '정해': '옥상토',
            '무자': '벽력화', '기축': '벽력화', '경인': '송백목', '신묘': '송백목', '임진': '장류수', '계사': '장류수',
            '갑오': '사중금', '을미': '사중금', '병신': '산하화', '정유': '산하화', '무술': '평지목', '기해': '평지목',
            '경자': '벽상토', '신축': '벽상토', '임인': '금박금', '계묘': '금박금', '갑진': '복등화', '을사': '복등화',
            '병오': '천하수', '정미': '천하수', '무신': '대역토', '기유': '대역토', '경술': '차천금', '신해': '차천금',
            '임자': '상자목', '계축': '상자목', '갑인': '대계수', '을묘': '대계수', '병진': '사중토', '정사': '사중토',
            '무오': '천상화', '기미': '천상화', '경신': '석류목', '신유': '석류목', '임술': '대海水', '계해': '대海水'
        }
        key = gan_char + ji_char
        return nabeum_map.get(key, "")

    def _calculate_12unseong(self, gan, ji):
        if gan == "모름" or ji == "모름": return None
        gan_char = gan.split('(')[0]; ji_char = ji.split('(')[0]
        table = saju_data.UNSEONG_TABLE.get(gan_char)
        if not table: return None
        try:
            idx = table.index(ji_char)
            stages = ["장생", "목욕", "관대", "건록", "제왕", "쇠", "병", "사", "묘", "절", "태", "양"]
            return stages[idx]
        except ValueError: return None

    def _get_jijanggan(self, ji):
        """지장간 추출: 지지의 초기, 중기, 본기 천간"""
        if ji == "모름":
            return {"chogi": None, "junggi": None, "bonggi": None}
        ji_char = ji.split('(')[0]
        if ji_char not in saju_data.JIJANGGAN:
            return {"chogi": None, "junggi": None, "bonggi": None}
        return saju_data.JIJANGGAN[ji_char]

    def _calculate_12sinsal(self, year_ji, target_ji):
        """12신살 (Standard Myeongli): 년지 삼합 기준"""
        if year_ji == "모름" or target_ji == "모름": return ""

        y_char = year_ji.split('(')[0]
        t_char = target_ji.split('(')[0]

        # 1. 삼합 국에 따른 겁살(Geopsal) 시작점 확인
        # 인오술(화국) -> 해(亥)가 겁살
        # 사유축(금국) -> 인(寅)이 겁살
        # 신자진(수국) -> 사(巳)가 겁살
        # 해묘미(목국) -> 신(申)이 겁살
        
        start_char = ""
        if y_char in ['인', '오', '술']: start_char = '해'
        elif y_char in ['사', '유', '축']: start_char = '인'
        elif y_char in ['신', '자', '진']: start_char = '사'
        elif y_char in ['해', '묘', '미']: start_char = '신'
        
        if not start_char: return ""

        # 2. 12신살 순서 (겁살부터 시작)
        sinsal_order = ['겁살', '재살', '천살', '지살', '년살', '월살', '망신', '장성', '반안', '역마', '육해', '화개']
        ji_order = ['자', '축', '인', '묘', '진', '사', '오', '미', '신', '유', '술', '해']

        # 3. 인덱스 차이 계산
        s_idx = ji_order.index(start_char)
        t_idx = ji_order.index(t_char)
        
        diff = (t_idx - s_idx) % 12
        return sinsal_order[diff]

    def _calculate_gyeokguk(self, day_gan, month_ji, heaven_stems):
        m_ji_char = month_ji.split('(')[0]
        if m_ji_char not in saju_data.JIJANGGAN: return {"name": "잡기재관격", "basis": "지장간 정보 없음"}
        jijanggan = saju_data.JIJANGGAN[m_ji_char]
        bonggi = jijanggan['bonggi']; junggi = jijanggan['junggi']; chogi = jijanggan['chogi']
        
        gyeok_gan = None; basis = ""
        if m_ji_char in ['자', '묘', '유']:
            gyeok_gan = bonggi
            basis = f"월지 '{m_ji_char}'는 왕지이므로 투간과 무관하게 본기 '{bonggi}'를 격으로 취용"
        else:
            if bonggi in heaven_stems:
                gyeok_gan = bonggi
                basis = f"월지 '{m_ji_char}'의 본기 '{bonggi}'가 천간에 투출됨"
            elif junggi and junggi in heaven_stems:
                gyeok_gan = junggi
                basis = f"월지 '{m_ji_char}'의 중기 '{junggi}'가 천간에 투출됨"
            elif chogi in heaven_stems:
                gyeok_gan = chogi
                basis = f"월지 '{m_ji_char}'의 초기 '{chogi}'가 천간에 투출됨"
            else:
                gyeok_gan = bonggi
                basis = f"월지 지장간이 투출되지 않아 본기 '{bonggi}'를 격으로 취용"
                
        sibseong = self._calculate_sibseong(day_gan.split('(')[0], gyeok_gan, is_stem=True)
        gyeok_name = f"{sibseong}격"
        
        if sibseong == "비견":
            gyeok_name = "건록격"
            basis += " (비견 -> 건록격 변환)"
        elif sibseong == "겁재":
            d_gan_char = day_gan.split('(')[0]
            if d_gan_char in ['갑', '병', '무', '경', '임']:
                gyeok_name = "양인격"
                basis += " (양일간 겁재 -> 양인격 변환)"
            else:
                gyeok_name = "월겁격"
                basis += " (음일간 겁재 -> 월겁격 변환)"
                
        return {"name": gyeok_name, "basis": basis, "desc": saju_data.GYEOKGUK_DESC.get(gyeok_name, {"name": gyeok_name, "desc": "설명 없음"})}

    def _split_pillar(self, p):
        if p == "모름(Unknown)": return "모름", "모름"
        parts = re.findall(r'[가-힣]\([^\)]+\)', p)
        if len(parts) == 2: return parts[0], parts[1]
        return p, p

    def _analyze_strength(self, pillars, ohaeng):
        """
        [V2] 득령/득지/득세 기반 신강/신약 판별
        - 지장간 뿌리 분석
        """
        import saju_data
        
        d_gan_part, d_ji_part = self._split_pillar(pillars['day'])
        m_gan_part, m_ji_part = self._split_pillar(pillars['month'])
        y_gan_part, y_ji_part = self._split_pillar(pillars['year'])
        h_gan_part, h_ji_part = self._split_pillar(pillars['hour'])
        
        d_gan = d_gan_part.split('(')[0]
        my_element = OHAENG.get(d_gan, '목')
        inseong_element = {'목': '수', '화': '목', '토': '화', '금': '토', '수': '금'}[my_element]
        
        score = 0.0
        calc_log = []
        
        # === 1. 득령(得令) ===
        m_ji = m_ji_part.split('(')[0] if m_ji_part != "모름" else None
        if m_ji and m_ji in saju_data.JIJANGGAN:
            jijanggan = saju_data.JIJANGGAN[m_ji]
            bonggi = jijanggan.get('bonggi')
            if bonggi:
                bonggi_elem = OHAENG.get(bonggi, '')
                if bonggi_elem == my_element or bonggi_elem == inseong_element:
                    score += 40
                    calc_log.append(f"득령+40(월지본기{bonggi}={bonggi_elem})")
        
        # === 2. 득지(得地) ===
        d_ji = d_ji_part.split('(')[0] if d_ji_part != "모름" else None
        if d_ji and d_ji in saju_data.JIJANGGAN:
            jijanggan = saju_data.JIJANGGAN[d_ji]
            has_root = False
            for key in ['bonggi', 'junggi', 'chogi']:
                hidden = jijanggan.get(key)
                if hidden:
                    hidden_elem = OHAENG.get(hidden, '')
                    if hidden_elem == my_element or hidden_elem == inseong_element:
                        has_root = True
                        break
            if has_root:
                score += 15
                calc_log.append(f"득지+15(일지뿌리)")
        
        # === 3. 득세(得勢) ===
        check_positions = [
            ('year_gan', y_gan_part), ('year_ji', y_ji_part),
            ('month_gan', m_gan_part), ('hour_gan', h_gan_part), ('hour_ji', h_ji_part)
        ]
        
        for name, char_part in check_positions:
            if char_part == "모름": continue
            char = char_part.split('(')[0]
            if 'gan' in name:
                elem = OHAENG.get(char, '')
                if elem == my_element or elem == inseong_element:
                    score += 10
                    calc_log.append(f"득세+10({name})")
            else:
                if char in saju_data.JIJANGGAN:
                    bonggi = saju_data.JIJANGGAN[char].get('bonggi')
                    if bonggi:
                        bonggi_elem = OHAENG.get(bonggi, '')
                        if bonggi_elem == my_element or bonggi_elem == inseong_element:
                            score += 10
                            calc_log.append(f"득세+10({name})")
        
        verdict = ""
        verdict_code = ""
        if score >= 70: verdict = "극신강/종왕격 (Extreme Strong)"; verdict_code = "JongWang"
        elif score >= 55: verdict = "신강 (Strong)"; verdict_code = "Strong"
        elif score >= 45: verdict = "중화 (Balanced)"; verdict_code = "Balanced"
        elif score >= 30: verdict = "신약 (Weak)"; verdict_code = "Weak"
        else: verdict = "극신약/종격 (Extreme Weak)"; verdict_code = "JongGyeok"
            
        return {"score": int(score), "verdict": verdict, "verdict_code": verdict_code, "calc_log": calc_log}

    def _determine_yongsin(self, strength_info, ohaeng_counts, day_gan, pillars):
        import saju_data
        d_gan = day_gan.split('(')[0]
        my_element = OHAENG.get(d_gan, '목')
        _, m_ji_part = self._split_pillar(pillars['month'])
        m_ji = m_ji_part.split('(')[0]
        
        # 1. 조후 (Seasonal)
        jobu_yongsin = None
        season_map = {'해':'수','자':'수','축':'수','인':'목','묘':'목','진':'목','사':'화','오':'화','미':'화','신':'금','유':'금','술':'금'}
        season = season_map.get(m_ji, '')
        jobu_candidates = []
        jobu_reason = ""
        if season == '수':
            jobu_candidates, jobu_reason = ['화', '토'], "겨울철에 태어나 한기를 녹이는 화(Fire)가 시급합니다 (조후)."
        elif season == '화':
            jobu_candidates, jobu_reason = ['수', '금'], "여름철에 태어나 열기를 식히는 수(Water)가 시급합니다 (조후)."
        
        if jobu_candidates:
            for cand in jobu_candidates:
                if ohaeng_counts.get(cand, 0) > 0:
                     jobu_yongsin = {'element': cand, 'type': '조후용신', 'reason': jobu_reason}
                     break

        # 2. 억부 (Eokbu)
        score = strength_info['score']
        is_strong = (score >= 55)
        eokbu_yongsin = None
        inseong_map = {'목': '수', '화': '목', '토': '화', '금': '토', '수': '금'}
        siksang_map = {'목': '화', '화': '토', '토': '금', '금': '수', '수': '목'}
        gwan_map = {'목': '금', '화': '수', '토': '목', '금': '화', '수': '토'}
        jaeseong_map = {'목': '토', '화': '금', '토': '수', '금': '목', '수': '화'}
        
        if is_strong:
            candidates = [(gwan_map[my_element], '관성', '억부용신(Suppress)'), (siksang_map[my_element], '식상', '억부용신(Drain)'), (jaeseong_map[my_element], '재성', '억부용신(Control)')]
            base_reason = "일간이 신강하여 힘을 조절하는 오행이 필요합니다."
        else:
            candidates = [(inseong_map[my_element], '인성', '억부용신(Support)'), (my_element, '비겁', '억부용신(Strengthen)')]
            base_reason = "일간이 신약하여 힘을 보태는 오행이 필요합니다."
            
        for elem, ten_god, y_type in candidates:
            if ohaeng_counts.get(elem, 0) > 0:
                eokbu_yongsin = {'element': elem, 'type': y_type, 'reason': f"{base_reason} ({ten_god})"}
                break
        
        if not eokbu_yongsin:
             eokbu_yongsin = {'element': candidates[0][0], 'type': candidates[0][2], 'reason': f"{base_reason} ({candidates[0][1]}, 원국 미약)"}

        # Final
        primary, secondary = None, None
        if jobu_yongsin:
            primary = jobu_yongsin
            if eokbu_yongsin and eokbu_yongsin['element'] != primary['element']:
                 secondary = {'element': eokbu_yongsin['element'], 'type': '희신', 'reason': eokbu_yongsin['reason']}
        else:
            primary = eokbu_yongsin
            yongsin_elem = primary['element']
            heeshin_elem = inseong_map.get(yongsin_elem, '')
            if heeshin_elem and ohaeng_counts.get(heeshin_elem, 0) > 0:
                secondary = {'element': heeshin_elem, 'type': '희신', 'reason': f"용신({yongsin_elem})을 생조하는 희신입니다."}

        eng_map = {'목': 'Tree', '화': 'Fire', '토': 'Earth', '금': 'Metal', '수': 'Water'}
        color_map = {'목': '청색/초록(Green)', '화': '적색/빨강(Red)', '토': '황색/노랑(Yellow)', '금': '백색/흰색(White)', '수': '흑색/검정(Black)'}
        num_map = {'목': [3, 8], '화': [2, 7], '토': [5, 10], '금': [4, 9], '수': [1, 6]}
        
        gisin_elem = inseong_map[my_element] if is_strong else gwan_map[my_element]
        gisin_reason = "신강한 일간을 더욱 강하게 하여 균형을 깹니다 (인성)." if is_strong else "신약한 일간을 억제하여 더욱 약하게 만듭니다 (관성)."
        
        return {"yongsin_structure": {
            "primary": {"element": f"{primary['element']}({eng_map.get(primary['element'], '')})", "type": primary['type'], "reason": primary['reason'], "eng": eng_map.get(primary['element'], '')},
            "secondary": {"element": f"{secondary['element']}({eng_map.get(secondary['element'], '')})", "type": secondary['type'], "reason": secondary['reason']} if secondary else {},
            "gisin": {"element": f"{gisin_elem}({eng_map.get(gisin_elem, '')})", "type": "기신", "reason": gisin_reason},
            "unlucky_items": {"color": color_map.get(gisin_elem, ""), "number": num_map.get(gisin_elem, []), "desc": f"{gisin_elem} 기운이 강한 색상이나 의류는 피하세요."},
            "lucky_color": color_map.get(primary['element'], ""),
            "lucky_number": num_map.get(primary['element'], [])
        }}

    def _determine_multi_yongsin(self, strength_info, ohaeng_counts, day_gan, pillars):
        import saju_data
        yongsin_list = []
        inseong_map = {'목': '수', '화': '목', '토': '화', '금': '토', '수': '금'}
        siksang_map = {'목': '화', '화': '토', '토': '금', '금': '수', '수': '목'}
        gwan_map = {'목': '금', '화': '수', '토': '목', '금': '화', '수': '토'}
        jaeseong_map = {'목': '토', '화': '금', '토': '수', '금': '목', '수': '화'}
        eng_map = {'목': 'Tree', '화': 'Fire', '토': 'Earth', '금': 'Metal', '수': 'Water'}
        d_gan = day_gan.split('(')[0]
        my_element = saju_data.OHAENG.get(d_gan, '목')
        is_strong = (strength_info['score'] >= 55)

        if is_strong:
            for m in [gwan_map, siksang_map, jaeseong_map]:
                e = m[my_element]
                if ohaeng_counts.get(e, 0) > 0:
                    yongsin_list.append({"element": f"{e}({eng_map[e]})", "type": "억부용신", "priority": 1, "reason": "신강 조절"})
        else:
            for m in [inseong_map]:
                e = m[my_element]
                if ohaeng_counts.get(e, 0) > 0:
                    yongsin_list.append({"element": f"{e}({eng_map[e]})", "type": "억부용신", "priority": 1, "reason": "신약 보강"})
            if ohaeng_counts.get(my_element, 0) > 0:
                yongsin_list.append({"element": f"{my_element}({eng_map[my_element]})", "type": "억부용신", "priority": 1, "reason": "비겁 지원"})

        elem_exists = {e: (cnt > 0) for e, cnt in ohaeng_counts.items()}
        pairs = [('금', '목', '수', '금생수생목'), ('수', '화', '목', '수생목생화'), ('화', '금', '토', '화생토생금'), ('토', '수', '금', '토생금생수'), ('목', '토', '화', '목생화생토')]
        for e1, e2, med, res in pairs:
            if elem_exists.get(e1) and elem_exists.get(e2):
                yongsin_list.append({"element": f"{med}({eng_map[med]})", "type": "통관용신", "priority": 2, "reason": res})
        return yongsin_list

    def _get_eng(self, elem):
        eng_map = {'목': 'Tree', '화': 'Fire', '토': 'Earth', '금': 'Metal', '수': 'Water'}
        return eng_map.get(elem, elem)

    def _get_ohaeng(self, char):
        return OHAENG.get(char.split('(')[0], '')

    

    def _calculate_yearly_luck(self, current_year):
        luck = []
        base_year = 1984
        for i in range(10):
            target_year = current_year + i
            diff = target_year - base_year
            gan_idx = diff % 10
            ji_idx = diff % 12
            ganji = CHEONGAN[gan_idx] + JIJI[ji_idx]
            luck.append({'year': target_year, 'ganji': ganji})
        return luck

    def _calculate_monthly_luck(self, current_year):
        diff = current_year - 1984
        year_gan_idx = diff % 10
        y_gan_char = CHEONGAN[year_gan_idx].split('(')[0]
        start_gan_map = {'갑': 2, '기': 2, '을': 4, '경': 4, '병': 6, '신': 6, '정': 8, '임': 8, '무': 0, '계': 0}
        start_gan_idx = start_gan_map.get(y_gan_char, 0)
        luck = []
        for i in range(12):
            m_gan_idx = (start_gan_idx + i) % 10
            m_ji_idx = (2 + i) % 12 
            ganji = CHEONGAN[m_gan_idx] + JIJI[m_ji_idx]
            display_month = i + 2
            if display_month > 12: display_month -= 12
            luck.append({'month': display_month, 'ganji': ganji})
        return luck

    def display_result(self, result):
        # GUI Display function (Truncated for brevity in class logic, usually handled by GUI class)
        return "분석 완료" 

    def _calculate_luck_cycle(self):
        # Current Year (System Time)
        now = datetime.now()
        cur_year = now.year
        
        yearly = []
        def get_ganji(y):
            gi = (y - 4) % 10
            ji = (y - 4) % 12
            return f"{CHEONGAN[gi]}{JIJI[ji]}"
            
        for i in range(10):
            y = cur_year + i
            yearly.append({"year": y, "ganji": get_ganji(y)})
            
        monthly = []
        # Generate 12 months for current year
        cur_m = now.month
        y_gan_idx = (cur_year - 4) % 10
        start_m_gan_idx = (y_gan_idx % 5) * 2 + 2
        
        for i in range(12):
            # Month 1 is Tiger (Feb) roughly for GanJi purpose in simplified view
            # Typically 2월=寅.
            m_num = (i + 2)
            if m_num > 12: m_num -= 12
            
            m_gan_idx = (start_m_gan_idx + i) % 10
            m_ji_idx = (2 + i) % 12
            
            monthly.append({
                "month": m_num,
                "ganji": f"{CHEONGAN[m_gan_idx]}{JIJI[m_ji_idx]}"
            })
            
        return {"yearly": yearly, "monthly": monthly}

    def _calculate_multi_yongsin(self, score):
        return []

    def _calculate_yongsin(self, day_gan, pillars, ohaeng, score):
        me = day_gan.split('(')[0]
        # Safety check if me is empty
        if not me: return {'yongsin': '', 'yongsin_structure': {}, 'multi_yongsin': []}

        my_elem = CHEONGAN_INFO.get(me, {'element': '목'})['element']
        
        ring = ['목', '화', '토', '금', '수']
        eng_map = {'목':'Tree', '화':'Fire', '토':'Earth', '금':'Metal', '수':'Water'}
        try:
            idx = ring.index(my_elem)
        except ValueError:
            idx = 0
        
        resource = ring[idx-1]
        companion = my_elem
        output = ring[(idx+1)%5]
        wealth = ring[(idx+2)%5]
        official = ring[(idx+3)%5]
        
        primary = None
        type_str = ""
        reason = ""
        
        if score <= 45: # Weak
            primary = resource
            secondary = companion
            gisin = official
            type_str = "억부용신(Support)"
            reason = f"일간이 신약하여 힘을 보태는 {primary} 오행이 필요합니다. (인성)"
        elif score >= 55: # Strong
            primary = output
            secondary = wealth
            gisin = resource
            type_str = "억부용신(Suppress)"
            reason = f"일간이 신강하여 기운을 설기하는 {primary} 오행이 필요합니다. (식상)"
        else:
            primary = output
            secondary = wealth
            gisin = resource
            type_str = "조후용신(Balance)"
            reason = "중화 사주로 흐름을 원활하게 하는 오행이 좋습니다."
            
        p_eng = eng_map.get(primary, 'Unknown')
        
        return {
            'yongsin': primary,
            'yongsin_structure': {
                'primary': {
                    'element': f"{primary}({p_eng})",
                    'type': type_str,
                    'reason': reason,
                    'eng': p_eng
                },
                'secondary': {'element': secondary, 'type': 'Heesin'},
                'gisin': {
                    'element': f"{gisin}({eng_map.get(gisin, '')})",
                    'type': '기신',
                    'reason': f"{gisin} 오행은 균형을 깨뜨릴 수 있습니다."
                },
                'lucky_color': 'Red' if primary=='화' else ('Blue' if primary=='목' else ('Black' if primary=='수' else ('White' if primary=='금' else 'Yellow'))),
                'lucky_number': [2,7] if primary=='화' else ([3,8] if primary=='목' else ([1,6] if primary=='수' else ([4,9] if primary=='금' else [0,5]))),
                'unlucky_items': {}
            },
            'multi_yongsin': self._calculate_multi_yongsin(score)
        }

    def _analyze_health_risks(self, ohaeng):
        risks = []
        organs = {'목': '간/담', '화': '심장/소장', '토': '비/위', '금': '폐/대장', '수': '신장/방광'}
        
        for e, count in ohaeng.items():
            if count == 0:
                risks.append({
                    'type': f"{e} 부족", 
                    'element': e,
                    'organs': organs.get(e, '전신'),
                    'symptoms': "피로, 면역력 저하",
                    'advice': f"{e} 기운을 보충하는 식습관이 필요합니다."
                })
            elif count >= 3:
                risks.append({
                    'type': f"{e} 과다",
                    'element': e,
                    'organs': organs.get(e, '전신'),
                    'symptoms': "해당 장기의 과부하",
                    'advice': f"{e} 기운을 조절하는 습관이 필요합니다."
                })
                
        if not risks:
            risks.append({
                'type': "균형 (Balanced)",
                'element': "전체",
                'organs': "전신",
                'symptoms': "없음",
                'advice': "오행이 고루 분포되어 건강한 편입니다."
            })
            
        return {'risks': risks, 'summary': "오행 건강 분석 결과입니다."}


    def _analyze_interactions(self):
        interactions = []
        gan_list = [self.year_gan_char, self.month_gan_char, self.day_gan_char, self.hour_gan_char]
        ji_list = [self.year_ji_char, self.month_ji_char, self.day_ji_char, self.hour_ji_char]
        labels = ["년", "월", "일", "시"]
        
        pairs = [(0,1), (0,2), (0,3), (1,2), (1,3), (2,3)]
        
        for i, j in pairs:
            if not gan_list[i] or not gan_list[j]: continue
            l1, l2 = labels[i], labels[j]
            pair_lbl = f"{l1}-{l2}"
            
            # Cheongan Chung
            c_chung = self._calculate_cheongan_chung(gan_list[i], gan_list[j])
            if c_chung: interactions.append(f"천간충({pair_lbl}): {gan_list[i]}{gan_list[j]}충 ({c_chung})")
            
            # Cheongan Hap
            c_hap = self._calculate_cheongan_hap(gan_list[i], gan_list[j])
            if c_hap: interactions.append(f"천간합({pair_lbl}): {gan_list[i]}{gan_list[j]}합 ({c_hap})")
            
            j1, j2 = ji_list[i], ji_list[j]
            if not j1 or not j2: continue
            
            # Jiji Chung
            j_chung = self._calculate_jiji_chung(j1, j2)
            if j_chung: interactions.append(f"지지충({pair_lbl}): {j1}{j2}충 ({j_chung})")
            
            # Jiji Yukhap
            j_yukhap = self._calculate_jiji_yukhap(j1, j2)
            if j_yukhap: interactions.append(f"지지육합({pair_lbl}): {j1}{j2}합 ({j_yukhap})")
            
            # Wonjin
            wonjin = self._calculate_wonjin(j1, j2)
            if wonjin: interactions.append(f"원진({pair_lbl}): {j1}{j2}원진 (애증)")
            
            # Hyeong
            hyeong = self._calculate_hyeong(j1, j2)
            if hyeong: interactions.append(f"형({pair_lbl}): {j1}{j2}형 ({hyeong})")
            
            # Pa
            pa = self._calculate_pa(j1, j2)
            if pa: interactions.append(f"파({pair_lbl}): {j1}{j2}파 (파괴)")
            
            # Hae
            hae = self._calculate_hae(j1, j2)
            if hae: interactions.append(f"해({pair_lbl}): {j1}{j2}해 (해로움)")

        # === SAMHAP (삼합) Check ===
        # 삼합 groups: 인오술(火), 사유축(金), 신자진(水), 해묘미(木)
        samhap_groups = {
            '인오술': ['인', '오', '술'],
            '사유축': ['사', '유', '축'],
            '신자진': ['신', '자', '진'],
            '해묘미': ['해', '묘', '미']
        }
        
        valid_ji = [j for j in ji_list if j]
        
        for name, members in samhap_groups.items():
            matched = [j for j in valid_ji if j in members]
            matched_positions = []
            for idx, j in enumerate(ji_list):
                if j in members:
                    matched_positions.append(labels[idx])
            
            if len(matched) >= 3:
                # 삼합은 3글자가 모두 달라야 완전삼합 (중복 허용하더라도 3종류면 OK)
                unique_matched = set(matched)
                if len(unique_matched) == 3:
                    interactions.append(f"지지삼합({'-'.join(matched_positions)}): {name} (완전삼합)")
            elif len(matched) == 2:
                # 반합: 두 글자가 서로 달라야 함 (예: 신-자 OK, 진-진 NO)
                if matched[0] != matched[1]:
                    interactions.append(f"지지삼합(반합)({'-'.join(matched_positions)}): {''.join(matched)}반합 ({name} 중 2자)")

        # === BANGHAP (방합/계절합) Check ===
        # 방합 groups: 인묘진(春木), 사오미(夏火), 신유술(秋金), 해자축(冬水)
        banghap_groups = {
            '인묘진': ['인', '묘', '진'],
            '사오미': ['사', '오', '미'],
            '신유술': ['신', '유', '술'],
            '해자축': ['해', '자', '축']
        }
        
        for name, members in banghap_groups.items():
            matched = [j for j in valid_ji if j in members]
            matched_positions = []
            for idx, j in enumerate(ji_list):
                if j in members:
                    matched_positions.append(labels[idx])
            
            if len(matched) >= 3:
                unique_matched = set(matched)
                if len(unique_matched) == 3:
                    interactions.append(f"지지방합({'-'.join(matched_positions)}): {name} (완전방합)")
            elif len(matched) == 2:
                # 방합 반합: 두 글자가 서로 달라야 함
                if matched[0] != matched[1]:
                    interactions.append(f"지지방합(반합)({'-'.join(matched_positions)}): {''.join(matched)}반합 ({name} 중 2자)")
        
        return interactions

    def _check_gongmang_pillars(self, gongmang_list, ji_list, labels):
        """Check which pillars have Ji in Gongmang"""
        result = {}
        for idx, j in enumerate(ji_list):
            if not j: continue
            # Extract char from "오(午)" format
            j_char = j.split('(')[0] if '(' in j else j
            
            is_gongmang = False
            for gm in gongmang_list:
                gm_char = gm.split('(')[0] if '(' in gm else gm
                if j_char == gm_char:
                    is_gongmang = True
                    break
            
            result[labels[idx]] = is_gongmang
        return result


    def get_result_json(self):
        # 1) Calculate basic pillars
        pillars_data = self.get_gan_ji()
        
        # Ohaeng (Expects dict of Full Strings)
        ohaeng_cnt = self.analyze_ohaeng(pillars_data)
        
        def split_pillar(p_text):
            if not p_text or "Unknown" in p_text or "모름" in p_text: 
                return "", "", "", ""
            idx1 = p_text.find(')')
            if idx1 == -1: return "", "", "", ""
            
            g_full = p_text[:idx1+1]
            j_full = p_text[idx1+1:]
            
            g_char = g_full.split('(')[0]
            j_char = j_full.split('(')[0]
            
            return g_full, j_full, g_char, j_char

        # Parse all pillars
        y_gf, y_jf, y_gc, y_jc = split_pillar(pillars_data['year'])
        m_gf, m_jf, m_gc, m_jc = split_pillar(pillars_data['month'])
        d_gf, d_jf, d_gc, d_jc = split_pillar(pillars_data['day'])
        h_gf, h_jf, h_gc, h_jc = split_pillar(pillars_data['hour'])
        
        self.year_gan_char = y_gc
        self.year_ji_char = y_jc
        self.month_gan_char = m_gc
        self.month_ji_char = m_jc
        self.day_gan_char = d_gc
        self.day_ji_char = d_jc
        self.hour_gan_char = h_gc
        self.hour_ji_char = h_jc
        
        saja_gan_char = [y_gc, m_gc, d_gc, h_gc]
        saja_ji_char = [y_jc, m_jc, d_jc, h_jc]
        
        saja_gan_full = [y_gf, m_gf, d_gf, h_gf]
        saja_ji_full = [y_jf, m_jf, d_jf, h_jf]
        
        daewoon_result = self.get_daewoon(pillars_data['year_gan_idx'], pillars_data['month_gan_idx'], pillars_data['month_ji_idx'])
        
        gyeokguk = self._calculate_gyeokguk(d_gc, m_jc, saja_gan_char)
        
        if d_gf and d_jf:
             gongmang_list = self._calculate_gongmang(d_gf, d_jf)
             if isinstance(gongmang_list, list):
                 gongmang = ", ".join(gongmang_list)
             else:
                 gongmang = gongmang_list
        else:
             gongmang = "해당 없음"
        
        strength_res = self._calculate_saju_strength(d_gc, pillars_data, ohaeng_cnt)
        
        score = strength_res.get('score', 0)
        yongsin = self._calculate_yongsin(d_gc, pillars_data, ohaeng_cnt, score)
        
        luck_cycle = self._calculate_luck_cycle()
        
        # Sinsal (Fixing dict assignment)
        sinsal_data = {
            "year": {"gan": [], "ji": []},
            "month": {"gan": [], "ji": []},
            "day": {"gan": [], "ji": []},
            "hour": {"gan": [], "ji": []}
        }
        pillars_map = [("year", 0), ("month", 1), ("day", 2), ("hour", 3)]
        for p_name, idx in pillars_map:
            if p_name == "hour" and not h_gc: continue
            
            # _calculate_pillar_sinsal returns {'gan': [], 'ji': []}
            s_res = self._calculate_pillar_sinsal(saja_gan_char[idx], saja_ji_char[idx], "both")
            
            sinsal_data[p_name]["gan"] = s_res.get('gan', [])
            sinsal_data[p_name]["ji"] = s_res.get('ji', [])

        # [Posteller] 귀문관살 후처리: 진-해 조합이 있으면 양쪽 다 표시
        gwimun_pairs = [('자', '미'), ('축', '오'), ('인', '유'), ('묘', '신'), ('진', '해'), ('사', '술')]
        all_jiji = [saja_ji_char[i].split('(')[0] if saja_ji_char[i] else '' for i in range(4)]
        for pair in gwimun_pairs:
            if pair[0] in all_jiji and pair[1] in all_jiji:
                # 양쪽 모두 귀문관살 추가
                for p_name, idx in pillars_map:
                    j_char = saja_ji_char[idx].split('(')[0] if saja_ji_char[idx] else ''
                    if j_char in pair:
                        if "귀문관살" not in sinsal_data[p_name]["ji"]:
                            sinsal_data[p_name]["ji"].append("귀문관살")

        health_res = self._analyze_health_risks(ohaeng_cnt)
        
        sibseong_data = {}
        for p_name, idx in pillars_map:
            if idx == 2: 
                sibseong_data[f"{p_name}_gan"] = "비견"
            else:
                 if saja_gan_char[idx]:
                    sibseong_data[f"{p_name}_gan"] = self._calculate_sibseong(d_gc, saja_gan_char[idx], True)
            
            if saja_ji_char[idx]:
                 sibseong_data[f"{p_name}_ji"] = self._calculate_sibseong(d_gc, saja_ji_char[idx], False)

        interactions_list = self._analyze_interactions()

        four_pillars_rich = {}
        for p_name, idx in pillars_map:
            g_full = saja_gan_full[idx] or ""
            j_full = saja_ji_full[idx] or ""
            g_char = saja_gan_char[idx] or ""
            j_char = saja_ji_char[idx] or ""
            
            if not g_char: 
                four_pillars_rich[p_name] = {
                    "gan": "", "ji": "", "text": "시간 모름", 
                    "gan_desc": {}, "ji_desc": {}, "pillar_desc": {}
                }
                continue
            
            g_desc = CHEONGAN_DESC.get(g_full, {})
            j_desc = JIJI_DESC.get(j_full, {})
            
            if not g_desc and g_char:
                 for k in CHEONGAN_DESC:
                     if k.startswith(g_char): g_desc = CHEONGAN_DESC[k]; break
            if not j_desc and j_char:
                 for k in JIJI_DESC:
                     if k.startswith(j_char): j_desc = JIJI_DESC[k]; break
            
            g_nature = g_desc.get('nature', '')
            j_animal = j_desc.get('animal', '')
            summary = f"{g_nature} 위의 {j_animal}"
            detail = f"{g_char}({g_nature})의 기운과 {j_char}({j_animal})의 기운이 결합된 형태입니다."
            
            four_pillars_rich[p_name] = {
                "gan": g_full,
                "ji": j_full,
                "text": pillars_data[p_name],
                "gan_desc": g_desc,
                "ji_desc": j_desc,
                "pillar_desc": {"summary": summary, "detail": detail}
            }

        sib_details = {}
        for k, v in sibseong_data.items():
            if v in SIBSEONG_DETAILS:
                sib_details[k] = SIBSEONG_DETAILS[v]
            else:
                sib_details[k] = {"name": v, "desc": {}}

        twelve_unseong_res = {}
        for p_name, idx in pillars_map:
            j_c = saja_ji_char[idx]
            if not j_c: continue
            stage = self._calculate_12unseong(d_gc, j_c)
            desc = TWELVE_UNSEONG_DESC_MAP.get(stage, {})
            twelve_unseong_res[p_name] = {
                "stage": stage,
                "desc": desc
            }
        
        sinsal_det = {}
        all_sinsals = set()
        for p in sinsal_data.values():
            all_sinsals.update(p['gan'])
            all_sinsals.update(p['ji'])
        
        for s in all_sinsals:
            key = s
            if s not in SINSAL_DETAILS:
                if s.endswith("살"): key = s[:-1]
                elif s + "살" in SINSAL_DETAILS: key = s + "살"
            
            if key in SINSAL_DETAILS:
                sinsal_det[s] = SINSAL_DETAILS[key]

        interaction_det = []
        for inter in interactions_list:
            matched_type = None
            for key in INTERACTION_DESC_MAP.keys():
                if key in inter:
                    matched_type = key
                    break
            p_obj = {
                "raw": inter,
                "desc": INTERACTION_DESC_MAP.get(matched_type, {}) if matched_type else {}
            }
            parts = inter.split(":")
            if len(parts) > 0:
                p_obj["type"] = parts[0].split("(")[0].strip()
            interaction_det.append(p_obj)
            
        ref_data = {
           "cheongan_ref": CHEONGAN_DESC,
           "jiji_ref": JIJI_DESC,
           "sinsal_details": SINSAL_DETAILS
        }

        info = {
            "name": self.name,
            "gender": self.gender,
            "solar_date": {"year": self.adjusted_dt.year, "month": self.adjusted_dt.month, "day": self.adjusted_dt.day, "hour": self.adjusted_dt.hour, "minute": self.adjusted_dt.minute},
            # Note: Lunar date conversion needed if we want to show it. For now, mimicking structure or using passed value
            # Assuming self.lunar_date was set during init if available, or we compute it. 
            # Ideally we use the property from the calculator. 
            "lunar_date": {"year": 0, "month": 0, "day": 0}, # Placeholder or need actual calculation
            "ddi": JIJI_DESC.get(self.year_ji_char + "(%s)" % (JIJI[JIJI.index(self.year_ji_char) if self.year_ji_char in JIJI else 0].split('(')[1]), {}).get('animal', '') if self.year_ji_char else '',
            "age": self._calculate_korean_age(self.adjusted_dt.year),
            "input_date": self.birth_date_str,
            "input_time": self.birth_time_str,
            "calendar_type": self.calendar_type,
            "birth_year": self.adjusted_dt.year,
            "birth_month": self.adjusted_dt.month,
            "birth_day": self.adjusted_dt.day,
            "birth_hour": self.adjusted_dt.hour,
            "birth_minute": self.adjusted_dt.minute,
             "summer_time_applied": getattr(self, 'summer_time_applied', False), 
             "longitude_correction": getattr(self, 'longitude_correction_minute', "N/A")
        }

        return {
            "info": info,
            "four_pillars": four_pillars_rich,
            "five_elements": ohaeng_cnt,
            "daewoon": daewoon_result,
            "sibseong": sibseong_data,
            "sibseong_details": sib_details,
            "sinsal": sinsal_data,
            "sinsal_details": sinsal_det,
            "interactions": interactions_list,
            "interaction_details": interaction_det,
            "gyeokguk": gyeokguk,
            "gongmang": gongmang,
            "gongmang_pillars": self._check_gongmang_pillars(
                gongmang.split(", ") if isinstance(gongmang, str) else gongmang,
                [pillars_data['year'], pillars_data['month'], pillars_data['day'], pillars_data['hour']],
                ["year", "month", "day", "hour"]
            ),
            "strength": strength_res,
            "yongsin_structure": yongsin,
            "multi_yongsin": [],
            "luck_cycle": luck_cycle,
            "health_analysis": health_res,
            "twelve_unseong": twelve_unseong_res, 
            "reference_data": ref_data,
            "comprehensive_analysis": {},
            # Additional keys to support frontend if needed (keeping 'derived' data but flattening)
            "jijanggan": {
                "year": self._get_jijanggan(saja_ji_char[0]) if saja_ji_char[0] else {},
                "month": self._get_jijanggan(saja_ji_char[1]) if saja_ji_char[1] else {},
                "day": self._get_jijanggan(saja_ji_char[2]) if saja_ji_char[2] else {},
                "hour": self._get_jijanggan(saja_ji_char[3]) if saja_ji_char[3] else {}
            },
            "nabeum": {
                "year": self._calculate_nabeum(pillars_data['year']),
                "month": self._calculate_nabeum(pillars_data['month']),
                "day": self._calculate_nabeum(pillars_data['day']),
                "hour": self._calculate_nabeum(pillars_data['hour'])
            }
        }

    def _calculate_saju_strength(self, day_gan, pillars, ohaeng):
        # Weighting
        # Month Branch: 2.0
        # Day Branch: 1.5
        # Other Branches: 1.0
        # Stems: 1.0 (Day Stem excluded)
        
        # Determine Day Element
        me = self.day_gan_char
        my_elem = CHEONGAN_INFO.get(me, {}).get('element', '') 
        
        # Calculate my side (Ex: Wood -> Wood, Water)
        my_side_score = 0
        total_score = 0
        
        # Elements mapping
        # Saeng (Resource) -> My Elem
        resource_elem = None
        for k, v in OHAENG_SANGSAENG.items():
            if v == my_elem: resource_elem = k; break
            
        import re
        def get_elem(char, is_gan):
            if is_gan: return CHEONGAN_INFO.get(char, {}).get('element')
            else: return JIJI_INFO.get(char, {}).get('element')

        def extract(p):
            # p ex: 갑(甲)자(子)
            parts = re.findall(r'.\(.\)', p)
            if len(parts) == 2: return parts[0].split('(')[0], parts[1].split('(')[0]
            # fallback for simple string
            # Removing parens
            clean = re.sub(r'\(.\)', '', p)
            if len(clean) >= 2: return clean[0], clean[1]
            return "", ""

        y_g, y_j = extract(pillars['year'])
        m_g, m_j = extract(pillars['month'])
        d_g, d_j = extract(pillars['day'])
        h_g, h_j = extract(pillars['hour'])

        # Year
        y_g_e = get_elem(y_g, True)
        y_j_e = get_elem(y_j, False)
        # Month
        m_g_e = get_elem(m_g, True)
        m_j_e = get_elem(m_j, False)
        # Day (Ji only)
        # d_j_e = get_elem(d_j, False) # logic below
        d_j_e = get_elem(d_j, False)
        
        # Hour
        if not self.time_unknown:
            h_g_e = get_elem(h_g, True)
            h_j_e = get_elem(h_j, False)
            
        # Scoring
        weights = {
            'y_g': 1.0, 'y_j': 1.0,
            'm_g': 1.0, 'm_j': 2.5,
            'd_j': 1.5,
            'h_g': 1.0, 'h_j': 1.0
        }
        
        items = [
            (y_g_e, 1.0), (y_j_e, 1.0),
            (m_g_e, 1.0), (m_j_e, 2.5),
            (d_j_e, 1.5)
        ]
        if not self.time_unknown:
           items.extend([(h_g_e, 1.0), (h_j_e, 1.0)])
           
        for elem, w in items:
            if not elem: continue
            total_score += w
            if elem == my_elem or elem == resource_elem:
                my_side_score += w
                
        # Calculate Strength
        ratio = my_side_score / total_score if total_score > 0 else 0.5
        score_val = int(ratio * 100)
        
        verdict = "중화 (Balanced)"
        if score_val >= 55: verdict = "신강 (Strong)"
        elif score_val <= 45: verdict = "신약 (Weak)"
        
        return {'score': score_val, 'verdict': verdict, 'calc_log': []}

    

    
import tkinter as tk
from tkinter import ttk, messagebox
import threading

import tkinter as tk
from tkinter import ttk, messagebox, font
import json
import threading

import tkinter as tk
from tkinter import ttk, messagebox, font
import json
import threading

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

class SajuApp:
    def __init__(self, root):
        self.root = root
        self.root.title("사주 분석 v2.7 (Classic)")
        self.root.geometry("550x700")  # Compact size
        
        # Use default theme for native look
        # self.style = ttk.Style()
        # self.style.theme_use('default') 
        
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 1. Input Section (Compact Grid)
        input_frame = ttk.LabelFrame(main_frame, text="사주 정보 입력", padding="10")
        input_frame.pack(fill="x", pady=5)
        
        # Row 0: Name & Gender
        ttk.Label(input_frame, text="이름:").grid(row=0, column=0, sticky="e", padx=5, pady=2)
        self.name_entry = ttk.Entry(input_frame, width=15)
        self.name_entry.grid(row=0, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(input_frame, text="성별:").grid(row=0, column=2, sticky="e", padx=5, pady=2)
        self.gender_var = tk.StringVar(value="male")
        frame_g = ttk.Frame(input_frame)
        frame_g.grid(row=0, column=3, sticky="w")
        ttk.Radiobutton(frame_g, text="남", variable=self.gender_var, value="male").pack(side="left")
        ttk.Radiobutton(frame_g, text="여", variable=self.gender_var, value="female").pack(side="left")
        
        # Row 1: Calendar Type
        ttk.Label(input_frame, text="양음력:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
        frame_c = ttk.Frame(input_frame)
        frame_c.grid(row=1, column=1, columnspan=3, sticky="w", padx=5, pady=2)
        
        self.calendar_var = tk.StringVar(value="solar")
        ttk.Radiobutton(frame_c, text="양력", variable=self.calendar_var, value="solar").pack(side="left", padx=2)
        ttk.Radiobutton(frame_c, text="음력", variable=self.calendar_var, value="lunar").pack(side="left", padx=2)
        self.leap_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(frame_c, text="윤달", variable=self.leap_var).pack(side="left", padx=10)

        # Row 2: Date
        ttk.Label(input_frame, text="생년월일:").grid(row=2, column=0, sticky="e", padx=5, pady=2)
        self.date_entry = ttk.Entry(input_frame, width=20)
        self.date_entry.grid(row=2, column=1, columnspan=2, sticky="w", padx=5, pady=2)
        self.date_entry.insert(0, "1974-12-17")
        ttk.Label(input_frame, text="(YYYY-MM-DD)").grid(row=2, column=3, sticky="w")

        # Row 3: Time
        ttk.Label(input_frame, text="시간:").grid(row=3, column=0, sticky="e", padx=5, pady=2)
        self.time_entry = ttk.Entry(input_frame, width=10)
        self.time_entry.grid(row=3, column=1, sticky="w", padx=5, pady=2)
        self.time_entry.insert(0, "12:30")
        
        self.unknown_time_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(input_frame, text="시간 모름", variable=self.unknown_time_var, command=self.toggle_time).grid(row=3, column=2, sticky="w")
        
        # Analyze Button
        self.analyze_btn = ttk.Button(input_frame, text="분석하기", command=self.run_analysis)
        self.analyze_btn.grid(row=4, column=0, columnspan=4, pady=10)
        
        # 2. Result Section (Simple Text)
        result_frame = ttk.LabelFrame(main_frame, text="분석 결과", padding="5")
        result_frame.pack(fill="both", expand=True, pady=5)
        
        self.result_text = tk.Text(result_frame, font=("Menlo", 12), height=20, width=60)
        self.result_text.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=self.result_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.result_text.configure(yscrollcommand=scrollbar.set)

    def toggle_time(self):
        if self.unknown_time_var.get():
            self.time_entry.configure(state='disabled')
        else:
            self.time_entry.configure(state='normal')

    def run_analysis(self):
        name = self.name_entry.get()
        date_str = self.date_entry.get()
        time_str = self.time_entry.get() if not self.unknown_time_var.get() else None
        gender = self.gender_var.get()
        cal_type = self.calendar_var.get()
        is_leap = self.leap_var.get()
        
        try:
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "분석 중...\n")
            
            # Run Analysis
            analyzer = SajuAnalyzer(date_str, time_str, gender, name, cal_type, is_leap)
            result = analyzer.get_result_json()
            
            # Display Simple Result
            self._display_simple(result)
            
            # Save File Logic (Dynamic Name)
            save_dir = "/Users/loyalee/Desktop/명리심리연구소"
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            
            safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '_', '-')).strip()
            if not safe_name: safe_name = "Unknown"
            filename = f"saju_result_{safe_name}.json"
            save_path = os.path.join(save_dir, filename)
            
            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=4)
                
            self.result_text.insert(tk.END, f"\n✅ 저장 완료: {filename}")
                
        except Exception as e:
            messagebox.showerror("오류", f"분석 중 오류 발생:\n{e}")
            import traceback
            traceback.print_exc()

    def _display_simple(self, res):
        t = self.result_text
        t.delete(1.0, tk.END)
        
        # Info
        name = res.get('info', {}).get('name', 'Unknown')
        t.insert(tk.END, f"=== {name}님의 사주 ===\n\n")
        
        # Pillars
        fp = res.get('four_pillars', {})
        t.insert(tk.END, "시주  일주  월주  년주\n")
        
        def get_p_text(p_key):
            return fp.get(p_key, {}).get('text', '')
            
        t.insert(tk.END, f"{get_p_text('hour')}  {get_p_text('day')}  {get_p_text('month')}  {get_p_text('year')}\n\n")
        
        # Daewoon
        dw = res.get('daewoon', {})
        dw_cols = dw.get('pillars', [])
        dw_age = dw_cols[0].get('age', '-') if dw_cols else '-'
        dw_dir = dw.get('direction', '-')
        t.insert(tk.END, f"대운수: {dw_age} ({dw_dir})\n")
        
        # Strength
        st = res.get('strength', {})
        st_verdict = st.get('verdict', '-')
        st_score = st.get('score', 0)
        t.insert(tk.END, f"강약: {st_verdict} ({st_score}점)\n\n")
        
        # Yongsin (Safe Access)
        y = res.get('yongsin_structure', {})
        prim = y.get('primary') or {} # Handle None
        sec = y.get('secondary') or {}
        gisin = y.get('gisin') or {}
        
        p_el = prim.get('element', '-')
        p_type = prim.get('type', '-')
        s_el = sec.get('element', '-')
        g_el = gisin.get('element', '-')
        
        t.insert(tk.END, f"용신: {p_el} ({p_type})\n")
        t.insert(tk.END, f"희신: {s_el} | 기신: {g_el}\n\n")
        
        # Sinsal
        s = res.get('sinsal', {})
        t.insert(tk.END, "[신살]\n")
        
        def join_sinsal(p_key):
            # p_key -> {'gan': [], 'ji': []}
            p_data = s.get(p_key, {})
            items = p_data.get('ji', []) + p_data.get('gan', [])
            # Filter duplicates if any
            items = list(dict.fromkeys(items)) 
            return ', '.join(items) if items else '-'

        t.insert(tk.END, f"년: {join_sinsal('year')}\n")
        t.insert(tk.END, f"월: {join_sinsal('month')}\n")
        t.insert(tk.END, f"일: {join_sinsal('day')}\n")
        t.insert(tk.END, f"시: {join_sinsal('hour')}\n")
        
        if 'luck_cycle' in res:
            t.insert(tk.END, "\n[세운 (최근 10년)]\n")
            lc = res['luck_cycle'].get('yearly', [])
            for item in lc:
                t.insert(tk.END, f"{item['year']}: {item['ganji']}  ")
            t.insert(tk.END, "\n")

def main():
    root = tk.Tk()
    app = SajuApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
