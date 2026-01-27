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
from saju_data import CHEONGAN, JIJI, OHAENG, YUKCHIN, SIBSEONG_DESC, SINSAL_DESC, CHEONGAN_DESC, JIJI_DESC, ILJU_DESC_SUMMARY, ILJU_DESC_DETAIL, DAEWOON_DESC, YEARLY_LUCK_DESC, SUMMER_TIME_PERIODS, CHEONGAN_INFO, JIJI_INFO, OHAENG_SANGSAENG, OHAENG_SANGGEUK, JIJANGGAN_WEIGHT, WOLRYEONG_STRENGTH




class SolarTermCalculator:
    def find_jeolgi_time(self, year, month):
        # [Precise Solar Term Data]
        # Source: KASI (Korea Astronomy and Space Science Institute)
        # Entry times in KST (Timezone correction handled by pillar logic)
        precise_data = {
            "1958-02": "1958-02-04 16:20",
            "1958-01": "1958-01-06 04:36",
            "1957-02": "1957-02-04 10:48",
            "1998-08": "1998-08-08 00:25",
            "1955-02": "1955-02-04 23:18",
            "1956-02": "1956-02-05 05:12",
            }
        
        key = f"{year}-{month:02d}"
        if key in precise_data:
            return datetime.strptime(precise_data[key], "%Y-%m-%d %H:%M")
        
        key = f"{year}-{month:02d}"
        if key in precise_data:
            return datetime.strptime(precise_data[key], "%Y-%m-%d %H:%M")
            
        # [NEW] precise data for 1984
        if year == 1984 and month == 5:
             return datetime(1984, 5, 5, 10, 23)

        # Fallback approximation (Improved)
        term_map = {
            1: 6, 2: 4, 3: 6, 4: 5, 5: 6, 6: 6,
            7: 7, 8: 8, 9: 8, 10: 9, 11: 8, 12: 7
            }
        day = term_map.get(month, 5)
        # For years not in precise_data, we default to 12:00 for better split
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
        """
        Calculate Sinsal returning separated lists for Gan and Ji.
        """
        res = {'gan': [], 'ji': []}
        
        # Safe char extraction
        g_char = gan.split('(')[0] if gan else ""
        j_char = ji.split('(')[0] if ji else ""
        
        if not hasattr(self, 'day_ji_char') or not hasattr(self, 'day_gan_char'):
            return res
            
        d_gan = self.day_gan_char
        d_ji = self.day_ji_char
        y_ji = getattr(self, 'year_ji_char', '') # We need to ensure we store this
        
        # === 12 Sinsal (Yeokma, Dohwa, Hwagae, etc) ===
        # Dual Base: Day Ji AND Year Ji
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
                elif target_ji == '자': found.append("재살") # Optional expansion
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

        # Apply 12 Sinsal to JI only
        # 1. Day Base
        res['ji'].extend(check_12sinsal(d_ji, j_char))
        # 2. Year Base (if available) - Avoid dupes
        if y_ji:
            for s in check_12sinsal(y_ji, j_char):
                if s not in res['ji']: res['ji'].append(s)

        # Broad Check (Posteller Style fallback)
        if j_char in ['자', '오', '묘', '유'] and "도화" not in res['ji']: res['ji'].append("도화")
        if j_char in ['인', '신', '사', '해'] and "역마" not in res['ji']: res['ji'].append("역마")
        if j_char in ['진', '술', '축', '미'] and "화개" not in res['ji']: res['ji'].append("화개")

        # === Gilseong / Hyung / Sal ===
        
        # 1. Baekho (백호대살) - Gan+Ji Pair
        baekho_pairs = ["갑진", "을미", "병술", "정축", "무진", "임술", "계축"]
        if (g_char + j_char) in baekho_pairs:
            res['gan'].append("백호대살") # Display on both or one? Usually visually on both
            res['ji'].append("백호대살")

        # 2. Goegang (괴강살) - Gan+Ji Pair
        goegang_pairs = ["무진", "무술", "경진", "경술", "임진", "임술"]
        if (g_char + j_char) in goegang_pairs:
            res['gan'].append("괴강살")
            res['ji'].append("괴강살")
            
        # 3. Hyeonchim (현침살) - Character based
        if g_char in ['갑', '신']: res['gan'].append("현침살")
        if j_char in ['묘', '오', '신']: res['ji'].append("현침살") # Shin (Monkey) is also Hyeonchim
        # Note: '신' logic. In Hangul 辛(Gan) and 申(Ji) are both 신.
        # My check `g_char in ['갑', '신']` works for 辛. `'신'` string matches.
        
        # 4. Gwimun (귀문관살) - Day Ji vs Target Ji
        gwimun_map = {'자': '유', '축': '오', '인': '미', '묘': '신', '진': '해', '사': '술',
                      '유': '자', '오': '축', '미': '인', '신': '묘', '해': '진', '술': '사'}
        if gwimun_map.get(d_ji) == j_char:
             res['ji'].append("귀문관살")
             
        # 5. Cheoneul (천을귀인) - Day Gan vs Target Ji
        cheoneul_map = {
            '갑': ['축', '미'], '무': ['축', '미'], '경': ['축', '미'],
            '을': ['자', '신'], '기': ['자', '신'],
            '병': ['해', '유'], '정': ['해', '유'],
            '신': ['인', '오'],
            '임': ['사', '묘'], '계': ['사', '묘']
            }
        if j_char in cheoneul_map.get(d_gan, []):
            res['ji'].append("천을귀인")
            
        # 6. Geumyeo (금여성) - Day Gan vs Target Ji
        geumyeo_map = {
            '갑': '진', '을': '사', '병': '미', '정': '신', '무': '미',
            '기': '신', '경': '술', '신': '해', '임': '축', '계': '인'
            }
        if geumyeo_map.get(d_gan) == j_char:
            res['ji'].append("금여성")

        # 7. Hakdang (학당귀인) - Day Gan vs Target Ji (Jangsaeng)
        hakdang_map = {
            '갑': '해', '을': '오', '병': '인', '정': '유', '무': '인',
            '기': '유', '경': '사', '신': '자', '임': '신', '계': '묘'
            }
        if hakdang_map.get(d_gan) == j_char:
            res['ji'].append("학당귀인")

        # 8. Cheonju (천주귀인) - Day Gan vs Target Ji
        # Common map: Gap-Sa, Eul-O, Byeong-Sa... Gye-Myo
        cheonju_map = {
            '갑': '사', '을': '오', '병': '사', '정': '오', '무': '사',
            '기': '오', '경': '해', '신': '자', '임': '인', '계': '묘'
            }
        if cheonju_map.get(d_gan) == j_char:
            res['ji'].append("천주귀인")
            
        # 9. Gwangwi (관귀학관) - Day Gan vs Target Ji
        gwangwi_map = {
            '갑': '사', '을': '사', '병': '신', '정': '신', '무': '해',
            '기': '해', '경': '인', '신': '인', '임': '신', '계': '신'
            }
        if gwangwi_map.get(d_gan) == j_char:
            res['ji'].append("관귀학관")

        # 10. Munchang (문창귀인) - Day Gan vs Target Ji
        munchang_map = {
             '갑': '사', '을': '오', '병': '신', '정': '유', '무': '신',
             '기': '유', '경': '해', '신': '자', '임': '인', '계': '묘'
            }
        if munchang_map.get(d_gan) == j_char:
            res['ji'].append("문창귀인")

        # 11. Hongyeom (홍염살) - Day Gan vs Target Ji
        hongyeom_map = {
            '갑': '오', '을': '오', '병': '인', '정': '미', '무': '진',
            '기': '진', '경': '술', '신': '유', '임': '자', '계': '신'
            }
        if hongyeom_map.get(d_gan) == j_char:
            res['ji'].append("홍염살")
            
        # 12. Taegeuk (태극귀인) - Day Gan vs Target Ji
        taegeuk_map = {
             '갑': ['자','오'], '을': ['자','오'], 
             '병': ['묘','유'], '정': ['묘','유'],
             '무': ['진','술','축','미'], '기': ['진','술','축','미'],
             '경': ['인','해'], '신': ['인','해'],
             '임': ['사','신'], '계': ['사','신']
            }
        if j_char in taegeuk_map.get(d_gan, []):
            res['ji'].append("태극귀인")

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
        if birth_dt.date() == current_jeolgi_dt.date():
             is_after_current_jeolgi = False

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
        daewoon_num = int(diff_days / 3)
        
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
        
        for i in range(10): 
            if is_forward:
                curr_gan = (curr_gan + 1) % 10
                curr_ji = (curr_ji + 1) % 12
            else:
                curr_gan = (curr_gan - 1 + 10) % 10
                curr_ji = (curr_ji - 1 + 12) % 12
            pillar = CHEONGAN[curr_gan] + JIJI[curr_ji]
            
            age = start_age + (i * 10)
            if i == 0 and start_age == 0: age = 1 # 0세 대운은 1세로 표기하는 경우
            
            daewoon_list.append({'age': age, 'ganji': pillar})
            
        return {'direction': '순행' if is_forward else '역행', 'pillars': daewoon_list}

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

    def _calculate_gongmang(self, day_gan, day_ji):
        gan_idx = CHEONGAN.index(day_gan)
        ji_idx = JIJI.index(day_ji)
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

        # 귀문관살 (Standard Logic + Variants)
        gwimun_map = {
            '자': ['미'], '미': ['자', '인'], 
            '축': ['오'], '오': ['축', '신'], 
            '인': ['유', '미'], '유': ['인'], 
            '묘': ['신'], '신': ['묘'],
            '진': ['해'], '해': ['진'],
            '사': ['술'], '술': ['사']
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

    def _analyze_health_risks(self, ohaeng_counts):
        risks = []
        health_data = saju_data.HEALTH_DESC
        for elem_key, count in ohaeng_counts.items():
            elem_simple = elem_key.split('(')[0]
            info = health_data.get(elem_simple, {})
            if not info: continue
            if count >= 3:
                risks.append({"type": "태과 (Excess)", "element": elem_key, "organs": info['organs'], "symptoms": info['symptoms'], "advice": f"[{elem_simple} 과다] {info['advice']} 해당 장기의 과부하를 주의하세요."})
            elif count == 0:
                risks.append({"type": "불급 (Deficiency)", "element": elem_key, "organs": info['organs'], "symptoms": info['symptoms'], "advice": f"[{elem_simple} 부족] {info['advice']} 해당 장기의 기능 저하를 주의하세요."})
        if not risks:
            risks.append({"type": "균형 (Balanced)", "element": "전체", "organs": "전신", "symptoms": "없음", "advice": "오행이 고루 분포되어 건강한 편입니다."})
        return {"risks": risks, "summary": f"총 {len(risks)}개의 건강 주의 항목이 발견되었습니다." if risks[0]['type'] != "균형 (Balanced)" else "오행 균형이 양호합니다."}

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

    def get_result_json(self):
        try:
            pillars = self.get_gan_ji()
            ohaeng = self.analyze_ohaeng(pillars)
            daewoon = self.get_daewoon(pillars['year_gan_idx'], pillars['month_gan_idx'], pillars['month_ji_idx'])
            
            calendar = KoreanLunarCalendar()
            calendar.setSolarDate(self.year, self.month, self.day)
            lunar_date_str = f"{calendar.lunarYear}-{calendar.lunarMonth:02d}-{calendar.lunarDay:02d} {'윤달' if calendar.isIntercalation else ''}"
            
            y_gan, y_ji = self._split_pillar(pillars['year'])
            m_gan, m_ji = self._split_pillar(pillars['month'])
            d_gan, d_ji = self._split_pillar(pillars['day'])
            h_gan, h_ji = self._split_pillar(pillars['hour'])
            d_gan_part = d_gan.split('(')[0]

            heavenly_stems = [y_gan.split('(')[0], m_gan.split('(')[0], h_gan.split('(')[0]]
            gyeokguk_info = self._calculate_gyeokguk(d_gan, m_ji, heavenly_stems)
            strength_info = self._analyze_strength(pillars, ohaeng)
            yongsin_result = self._determine_yongsin(strength_info, ohaeng, d_gan, pillars)
            multi_yongsin = self._determine_multi_yongsin(strength_info, ohaeng, d_gan, pillars)
            health_result = self._analyze_health_risks(ohaeng)

            ys_struct = yongsin_result['yongsin_structure']
            yongsin_elem = ys_struct['primary']['element'].split('(')[0] if ys_struct['primary'] else ""
            heeshin_elem = ys_struct['secondary']['element'].split('(')[0] if ys_struct['secondary'] else ""
            
            def get_role(gan_ji_char):
                if not gan_ji_char: return "Neutral"
                elem = self._get_ohaeng(gan_ji_char.split('(')[0])
                if elem == yongsin_elem or elem == heeshin_elem: return "Good"
                gisin_elem_val = ys_struct['gisin']['element'].split('(')[0] if ys_struct['gisin'] else ""
                if elem == gisin_elem_val: return "Bad"
                return "Neutral"

            sibseong = {
                'year_gan': {'name': self._calculate_sibseong(d_gan, y_gan, True), 'role': get_role(y_gan)},
                'year_ji': {'name': self._calculate_sibseong(d_gan, y_ji, False), 'role': get_role(y_ji)},
                'month_gan': {'name': self._calculate_sibseong(d_gan, m_gan, True), 'role': get_role(m_gan)},
                'month_ji': {'name': self._calculate_sibseong(d_gan, m_ji, False), 'role': get_role(m_ji)},
                'day_gan': {'name': "비견", 'role': "Neutral"}, 
                'day_ji': {'name': self._calculate_sibseong(d_gan, d_ji, False), 'role': get_role(d_ji)},
                'hour_gan': {'name': self._calculate_sibseong(d_gan, h_gan, True), 'role': get_role(h_gan)} if not self.time_unknown else {'name': "", 'role': ""},
                'hour_ji': {'name': self._calculate_sibseong(d_gan, h_ji, False), 'role': get_role(h_ji)} if not self.time_unknown else {'name': "", 'role': ""}
            }
            
            for dw in daewoon['pillars']:
                dw_gan, dw_ji = self._split_pillar(dw['ganji'])
                dw['gan'] = dw_gan; dw['ji'] = dw_ji
                dw_stem_elem = self._get_ohaeng(dw_gan); dw_branch_elem = self._get_ohaeng(dw_ji)
                dw_score = 50; dw_vibe = "Normal"
                match_count = 0
                if dw_stem_elem in [yongsin_elem, heeshin_elem]: match_count += 1
                if dw_branch_elem in [yongsin_elem, heeshin_elem]: match_count += 1
                if match_count == 2: dw_score = 90; dw_vibe = "Very Good"
                elif match_count == 1: dw_score = 70; dw_vibe = "Good"
                
                # 기신운 체크
                gisin_val = ys_struct['gisin']['element'].split('(')[0] if ys_struct['gisin'] else ""
                if gisin_val and (dw_stem_elem == gisin_val or dw_branch_elem == gisin_val):
                    dw_score = 30; dw_vibe = "Bad"
                
                # 소토 특수 룰
                if ys_struct['primary'] and "소토" in ys_struct['primary']['type']:
                     if dw_stem_elem == '금' or dw_branch_elem == '금':
                         dw_score = 30; dw_vibe = "Bad (소토 방해)"
                         
                dw['score'] = dw_score; dw['vibe'] = dw_vibe

            # [포스텔러 방식] 신살 계산 - 전면 재작성
            # Store for Sinsal calc
            self.day_gan_char = d_gan.split('(')[0]
            self.day_ji_char = d_ji.split('(')[0]
            
            # Store for Sinsal calc
            self.day_gan_char = d_gan.split('(')[0]
            self.day_ji_char = d_ji.split('(')[0]
            self.year_ji_char = y_ji.split('(')[0]
        
            y_sinsal = self._calculate_pillar_sinsal(y_gan, y_ji, 'year')
            m_sinsal = self._calculate_pillar_sinsal(m_gan, m_ji, 'month')
            d_sinsal = self._calculate_pillar_sinsal(d_gan, d_ji, 'day')
            h_sinsal = self._calculate_pillar_sinsal(h_gan, h_ji, 'hour') if not self.time_unknown else {'gan':[], 'ji':[]}
        
            sinsal = {
                'year': y_sinsal,
                'month': m_sinsal,
                'day': d_sinsal,
                'hour': h_sinsal
        }

            # 각 주(柱)별 천간/지지 추출
            pillars_list = [
                ('year', y_gan, y_ji),
                ('month', m_gan, m_ji),
                ('day', d_gan, d_ji),
                ('hour', h_gan, h_ji)
            ]

            for p_name, gan_full, ji_full in pillars_list:
                if gan_full == "모름" or ji_full == "모름":
                    continue

                gan_char = gan_full.split('(')[0]
                ji_char = ji_full.split('(')[0]

                # === 지지 신살 (년지/일지 기준 관계) ===
                # 포스텔러 등 정밀 만세력은 년지 기준과 일지 기준을 모두 적용함 (Dual Base)
                
                # 1. 일지 기준
                rel_sinsal_day = self._calculate_sinsal(d_ji, ji_full)
                if rel_sinsal_day:
                    sinsal[p_name]['ji'].append(rel_sinsal_day)
                    
                # 2. 년지 기준
                rel_sinsal_year = self._calculate_sinsal(y_ji, ji_full)
                if rel_sinsal_year:
                     # 중복 방지 (이미 일지 기준에서 들어갔을 수도 있음)
                     if rel_sinsal_year not in sinsal[p_name]['ji']:
                         sinsal[p_name]['ji'].append(rel_sinsal_year)

                # 3. 글자 자체 기본 신살 (포스텔러 스타일 - Broad Check)
                # 역마: 인/신/사/해, 도화: 자/오/묘/유, 화개: 진/술/축/미
                if ji_char in ['인', '신', '사', '해']:
                    if "역마" not in sinsal[p_name]['ji']: sinsal[p_name]['ji'].append("역마")
                
                if ji_char in ['자', '오', '묘', '유']:
                    if "도화" not in sinsal[p_name]['ji']: sinsal[p_name]['ji'].append("도화")
                    
                if ji_char in ['진', '술', '축', '미']:
                    if "화개" not in sinsal[p_name]['ji']: sinsal[p_name]['ji'].append("화개")

            for p in sinsal:
                sinsal[p]['gan'] = list(dict.fromkeys([x for x in sinsal[p]['gan'] if x]))
                sinsal[p]['ji'] = list(dict.fromkeys([x for x in sinsal[p]['ji'] if x]))

            interactions = []
            interaction_details = []
            def add_detail(cat, lbl, pair, val):
                outcome = "무승부"
                if len(pair) >= 2:
                    c1 = pair[0]; c2 = pair[1]
                    e1 = self._get_ohaeng(c1); e2 = self._get_ohaeng(c2)
                    p1 = ohaeng.get(f"{e1}({self._get_eng(e1)})", 0)
                    p2 = ohaeng.get(f"{e2}({self._get_eng(e2)})", 0)
                    if p1 > p2: outcome = f"{e1} 승리"
                    elif p2 > p1: outcome = f"{e2} 승리"
                interaction_details.append({"type": cat, "label": lbl, "pair": pair, "value": val, "outcome": outcome})

            # Interaction Loops (Gan/Ji) - All Pairs Restored
            pairs_gan = [('년-월', y_gan, m_gan), ('년-일', y_gan, d_gan), ('년-시', y_gan, h_gan), ('월-일', m_gan, d_gan), ('월-시', m_gan, h_gan), ('일-시', d_gan, h_gan)]
            for label, g1, g2 in pairs_gan:
                if g1 == "모름" or g2 == "모름": continue
                g1_char = g1.split('(')[0]; g2_char = g2.split('(')[0]
                hap = self._calculate_cheongan_hap(g1, g2)
                if hap: interactions.append(f"천간합({label}): {g1_char}{g2_char}합 ({hap})"); add_detail("천간합", label, f"{g1_char}{g2_char}", hap)
                chung = self._calculate_cheongan_chung(g1, g2)
                if chung: interactions.append(f"천간충({label}): {g1_char}{g2_char}충 ({chung})"); add_detail("천간충", label, f"{g1_char}{g2_char}", chung)

            pairs_ji = [('년-월', y_ji, m_ji), ('년-일', y_ji, d_ji), ('년-시', y_ji, h_ji), ('월-일', m_ji, d_ji), ('월-시', m_ji, h_ji), ('일-시', d_ji, h_ji)]
            for label, j1, j2 in pairs_ji:
                if j1 == "모름" or j2 == "모름": continue
                j1_char = j1.split('(')[0]; j2_char = j2.split('(')[0]
                yukhap = self._calculate_jiji_yukhap(j1, j2)
                if yukhap: interactions.append(f"지지육합({label}): {j1_char}{j2_char}합 ({yukhap}국)"); add_detail("지지육합", label, f"{j1_char}{j2_char}", yukhap)
                chung = self._calculate_jiji_chung(j1, j2)
                if chung: interactions.append(f"지지충({label}): {j1_char}{j2_char}충 ({chung})"); add_detail("지지충", label, f"{j1_char}{j2_char}", chung)
                wonjin = self._calculate_wonjin(j1, j2)
                if wonjin: interactions.append(f"원진({label}): {j1_char}{j2_char}원진"); add_detail("원진", label, f"{j1_char}{j2_char}", "성립")
                hyeong = self._calculate_hyeong(j1, j2)
                if hyeong: interactions.append(f"형({label}): {j1_char}{j2_char}형 ({hyeong})"); add_detail("형", label, f"{j1_char}{j2_char}", hyeong)
                pa = self._calculate_pa(j1, j2)
                if pa: interactions.append(f"파({label}): {j1_char}{j2_char}파"); add_detail("파", label, f"{j1_char}{j2_char}", "성립")
                hae = self._calculate_hae(j1, j2)
                if hae: interactions.append(f"해({label}): {j1_char}{j2_char}해"); add_detail("해", label, f"{j1_char}{j2_char}", "성립")

            jis = [y_ji, m_ji, d_ji, h_ji]
            jis_chars = [j.split('(')[0] for j in jis if j != "모름"]
            samhap_groups = {'신자진': '수국', '인오술': '화국', '사유축': '금국', '해묘미': '목국'}
            for chars, guk in samhap_groups.items():
                count = 0
                for c in chars: 
                    if c in jis_chars: count += 1
                if count == 3: interactions.append(f"지지삼합: {chars} {guk} (성립)"); add_detail("삼합", "전체", chars, guk)
                elif count == 2: interactions.append(f"지지삼합(반합): {chars} 중 2자 ({guk} 기운)"); add_detail("삼합", "반합", chars, guk)

            # 지지방합 (Banghap) - Seasonal Alliance
            banghap_groups = {'인묘진': '목국(동방)', '사오미': '화국(남방)', '신유술': '금국(서방)', '해자축': '수국(북방)'}
            for chars, guk in banghap_groups.items():
                count = 0
                for c in chars:
                    if c in jis_chars: count += 1
                if count == 3: interactions.append(f"지지방합: {chars} {guk} (성립)"); add_detail("방합", "전체", chars, guk)
                # 방합은 보통 반합을 잘 안 쳐주기도 하지만, 포스텔러가 디테일하다면 2자도 볼 수 있음. 일단 포함.
                elif count == 2: interactions.append(f"지지방합(반합): {chars} 중 2자 ({guk} 기운)"); add_detail("방합", "반합", chars, guk)

            gongmang_chars = self._calculate_gongmang(d_gan, d_ji)
            active_gongmang = []
            target_branches = [y_ji.split('(')[0], m_ji.split('(')[0], h_ji.split('(')[0]]
            
            # Which pillars are Gongmang?
            gm_pillars = []
            gm_clean = [gm.split('(')[0] for gm in gongmang_chars]
            
            if y_ji.split('(')[0] in gm_clean: gm_pillars.append(f"년지({y_ji.split('(')[0]})")
            if m_ji.split('(')[0] in gm_clean: gm_pillars.append(f"월지({m_ji.split('(')[0]})")
            if h_ji.split('(')[0] in gm_clean: gm_pillars.append(f"시지({h_ji.split('(')[0]})")
            
            if gm_pillars:
                interactions.append(f"공망: {', '.join(gm_pillars)}")
                for pill in gm_pillars:
                     add_detail("공망", "지지", pill, "성립")
            
            gongmang_str = ", ".join(gm_pillars) if gm_pillars else "해당 없음"

            comprehensive_analysis = {
                "personality": f"일간 {d_gan_part}의 성향과 {gyeokguk_info['name']}의 특성을 겸비했습니다.",
                "wealth_luck": "재성 분석 및 용신 활용 조언 필요", 
                "health_guide": "건강 분석 참조",
                "lucky_items": {
                    "color": yongsin_result['yongsin_structure']['lucky_color'],
                    "number": yongsin_result['yongsin_structure']['lucky_number']
                }
            if health_result['risks'] and health_result['risks'][0]['type'] != "균형 (Balanced)":
                 risk_elems = [r['element'].split('(')[0] for r in health_result['risks']]
                 comprehensive_analysis['health_guide'] = f"{', '.join(risk_elems)} 오행 건강 주의 필요"

            current_year = datetime.now().year
            yearly_luck = self._calculate_yearly_luck(current_year)
            monthly_luck = self._calculate_monthly_luck(current_year)
            
            twelve_unseong = {
                'year': self._calculate_12unseong(d_gan, y_ji),
                'month': self._calculate_12unseong(d_gan, m_ji),
                'day': self._calculate_12unseong(d_gan, d_ji),
                'hour': self._calculate_12unseong(d_gan, h_ji)
            }

            # 지장간 계산
            jijanggan = {
                'year': self._get_jijanggan(y_ji),
                'month': self._get_jijanggan(m_ji),
                'day': self._get_jijanggan(d_ji),
                'hour': self._get_jijanggan(h_ji)
            }

            # 12신살 계산 (년지 기준)
            sip# Store for Sinsal calc
            self.day_gan_char = d_gan.split('(')[0]
            self.day_ji_char = d_ji.split('(')[0]
            self.year_ji_char = y_ji.split('(')[0]
        
            y_sinsal = self._calculate_pillar_sinsal(y_gan, y_ji, 'year')
            m_sinsal = self._calculate_pillar_sinsal(m_gan, m_ji, 'month')
            d_sinsal = self._calculate_pillar_sinsal(d_gan, d_ji, 'day')
            h_sinsal = self._calculate_pillar_sinsal(h_gan, h_ji, 'hour') if not self.time_unknown else {'gan':[], 'ji':[]}
        
            sinsal = {
                'year': y_sinsal,
                'month': m_sinsal,
                'day': d_sinsal,
                'hour': h_sinsal
            }
            self.day_gan_char = d_gan.split('(')[0]
            self.day_ji_char = d_ji.split('(')[0]
        
            # Store for Sinsal calc
            self.day_gan_char = d_gan.split('(')[0]
            self.day_ji_char = d_ji.split('(')[0]
            self.year_ji_char = y_ji.split('(')[0]
        
            y_sinsal = self._calculate_pillar_sinsal(y_gan, y_ji, 'year')
            m_sinsal = self._calculate_pillar_sinsal(m_gan, m_ji, 'month')
            d_sinsal = self._calculate_pillar_sinsal(d_gan, d_ji, 'day')
            h_sinsal = self._calculate_pillar_sinsal(h_gan, h_ji, 'hour') if not self.time_unknown else {'gan':[], 'ji':[]}
        
            sinsal = {
                'year': y_sinsal,
                'month': m_sinsal,
                'day': d_sinsal,
                'hour': h_sinsal
        }

            formatted_pillars = {
                'year': {'gan': y_gan, 'ji': y_ji, 'text': pillars['year']},
            
            result = {
                "info": {
                    "name": self.name,
                    "input_date": self.birth_date_str,
                    "calendar_type": "양력(Solar)" if self.calendar_type == 'solar' else "음력(Lunar)",
                    "is_leap_month": self.is_leap_month,
                    "input_time": self.birth_time_str if not self.time_unknown else "모름(Unknown)",
                    "gender": "남성(Male)" if self.gender == 'male' else "여성(Female)",
                    "summer_time_applied": False,
                    "longitude_correction": "N/A",
                    "birth_year": self.year,
                    "birth_month": self.month,
                    "birth_day": self.day,
                    "birth_hour": self.hour,
                    "birth_minute": self.minute,
                    "solar_date": f"{self.year}-{self.month:02d}-{self.day:02d}",
                    "lunar_date": lunar_date_str
                },
                "four_pillars": formatted_pillars,
                "five_elements": ohaeng,
                "daewoon": daewoon,
                "sibseong": sibseong,
                "sinsal": sinsal,
                "interactions": interactions,
                "interaction_details": interaction_details,
                "twelve_unseong": twelve_unseong,
                "jijanggan": jijanggan,
                "sipsinsal": sipsinsal,
                "gyeokguk": gyeokguk_info,
                "gongmang": gongmang_str,
                "strength": strength_info,
                "yongsin_structure": yongsin_result['yongsin_structure'],
                "multi_yongsin": multi_yongsin,
                "health_analysis": health_result,
                "comprehensive_analysis": comprehensive_analysis,
                "luck_cycle": {"yearly": yearly_luck, "monthly": monthly_luck}
            }
            return result
        except Exception as e:
            print(f"Error in get_result_json: {e}")
            import traceback
            traceback.print_exc()
            raise e

    def get_verbose_result(self):
        basic_result = self.get_result_json()
        def get_desc(dict_obj, key, field="nature"):
            if not key: return ""
            if key in dict_obj:
                val = dict_obj[key]
                if isinstance(val, dict): return val.get(field, "")
                return val
            key_hangul = key.split('(')[0]
            for k, v in dict_obj.items():
                if k.startswith(key_hangul):
                    if isinstance(v, dict): return v.get(field, "")
                    return v
            return ""

        def get_full_desc(dict_obj, key):
            if not key: return {}
            if key in dict_obj: return dict_obj[key]
            key_hangul = key.split('(')[0]
            for k, v in dict_obj.items():
                if k.startswith(key_hangul): return v
            return {}

        pillars = basic_result['four_pillars']
        for p_name in ['year', 'month', 'day', 'hour']:
            p = pillars[p_name]
            gan = p['gan']; ji = p['ji']
            p['gan_desc'] = get_full_desc(saju_data.CHEONGAN_DESC, gan)
            p['ji_desc'] = get_full_desc(saju_data.JIJI_DESC, ji)
            if gan == "모름" or ji == "모름":
                p['gan_desc'] = {}; p['ji_desc'] = {}
                p['pillar_desc'] = {"summary": "시간 모름", "detail": "분석 불가"}
            else:
                gan_nature = get_desc(saju_data.CHEONGAN_DESC, gan, "nature")
                ji_animal = get_desc(saju_data.JIJI_DESC, ji, "animal")
                p['pillar_desc'] = {
                    "summary": f"{gan_nature} 위의 {ji_animal}",
                    "detail": f"{gan}({gan_nature})의 기운과 {ji}({ji_animal})의 기운이 결합된 형태입니다. 천간의 {get_desc(saju_data.CHEONGAN_DESC, gan, 'keywords')} 성향과 지지의 {get_desc(saju_data.JIJI_DESC, ji, 'meaning')} 특성이 조화를 이룹니다."
                }

        sibseong = basic_result['sibseong']
        basic_result['sibseong_details'] = {}
        for key, val in sibseong.items():
            if not val: continue
            search_key = val if not isinstance(val, dict) else val.get('name', '')
            basic_result['sibseong_details'][key] = {"name": val, "desc": get_full_desc(saju_data.SIBSEONG_DESC, search_key)}

        sinsal = basic_result['sinsal']
        user_cheongan = set(); user_jiji = set()
        for p_val in basic_result['four_pillars'].values():
             if isinstance(p_val, dict): user_cheongan.add(p_val.get('gan')); user_jiji.add(p_val.get('ji'))
        filtered_cheongan_ref = {k: v for k, v in saju_data.CHEONGAN_DESC.items() if any(uc in k for uc in user_cheongan)}
        filtered_jiji_ref = {k: v for k, v in saju_data.JIJI_DESC.items() if any(uj in k for uj in user_jiji)}
        basic_result['reference_data'] = {"cheongan_ref": filtered_cheongan_ref, "jiji_ref": filtered_jiji_ref}
        
        basic_result['sinsal_details'] = {}
        all_sinsals = set()
        for p in sinsal.values(): all_sinsals.update(p['gan']); all_sinsals.update(p['ji'])
        for s in all_sinsals: basic_result['sinsal_details'][s] = get_desc(saju_data.SINSAL_DESC, s, "")
        
        basic_result['comprehensive_analysis'] = {}
        return basic_result
# ---------------------------------------------------------
# 2. GUI Logic
# ---------------------------------------------------------

class SajuGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("사주 분석 프로그램 v3.0")
        self.root.geometry("550x900")

        self.font_title = ("AppleGothic", 20, "bold")
        self.font_content = ("AppleGothic", 12)

        title_label = tk.Label(root, text="🔮 사주 분석기 🔮", font=self.font_title)
        title_label.pack(pady=20)

        input_frame = tk.Frame(root)
        input_frame.pack(pady=10)

        tk.Label(input_frame, text="이름:", font=self.font_content).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.name_entry = tk.Entry(input_frame, font=self.font_content)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)
        self.name_entry.insert(0, "홍길동")

        tk.Label(input_frame, text="생년월일:", font=self.font_content).grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.date_entry = tk.Entry(input_frame, font=self.font_content)
        self.date_entry.grid(row=1, column=1, padx=5, pady=5)
        self.date_entry.insert(0, "1990-01-01")
        
        self.calendar_var = tk.StringVar(value="solar")
        cal_frame = tk.Frame(input_frame)
        cal_frame.grid(row=1, column=2, padx=5, pady=5, sticky="w")
        tk.Radiobutton(cal_frame, text="양력", variable=self.calendar_var, value="solar", font=self.font_content).pack(side="left")
        tk.Radiobutton(cal_frame, text="음력", variable=self.calendar_var, value="lunar", font=self.font_content).pack(side="left")
        
        self.leap_month_var = tk.BooleanVar()
        self.leap_month_chk = tk.Checkbutton(input_frame, text="윤달", variable=self.leap_month_var, font=self.font_content)
        self.leap_month_chk.grid(row=1, column=3, padx=5, pady=5)

        tk.Label(input_frame, text="태어난 시간:", font=self.font_content).grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.time_entry = tk.Entry(input_frame, font=self.font_content)
        self.time_entry.grid(row=2, column=1, padx=5, pady=5)
        self.time_entry.insert(0, "14:30")
        
        self.unknown_time_var = tk.BooleanVar()
        self.unknown_time_chk = tk.Checkbutton(input_frame, text="시간 모름", variable=self.unknown_time_var, command=self.toggle_time_entry, font=self.font_content)
        self.unknown_time_chk.grid(row=2, column=2, padx=5, pady=5)

        tk.Label(input_frame, text="성별:", font=self.font_content).grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.gender_var = tk.StringVar(value="male")
        gender_frame = tk.Frame(input_frame)
        gender_frame.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        tk.Radiobutton(gender_frame, text="남성", variable=self.gender_var, value="male", font=self.font_content).pack(side="left", padx=5)
        tk.Radiobutton(gender_frame, text="여성", variable=self.gender_var, value="female", font=self.font_content).pack(side="left", padx=5)

        analyze_btn = tk.Button(root, text="분석하기", command=self.analyze, bg="#4a7abc", fg="black", font=("AppleGothic", 14, "bold"), height=2)
        analyze_btn.pack(pady=15, fill='x', padx=50)

        self.result_area = scrolledtext.ScrolledText(root, width=60, height=30, font=self.font_content)
        self.result_area.pack(pady=10, padx=20, fill='both', expand=True)

    def toggle_time_entry(self):
        if self.unknown_time_var.get():
            self.time_entry.config(state='disabled')
        else:
            self.time_entry.config(state='normal')

    def analyze(self):
        name = self.name_entry.get()
        date_str = self.date_entry.get()
        gender = self.gender_var.get()
        calendar_type = self.calendar_var.get()
        is_leap_month = self.leap_month_var.get()
        
        if self.unknown_time_var.get():
            time_str = None
        else:
            time_str = self.time_entry.get()

        try:
            analyzer = SajuAnalyzer(date_str, time_str, gender, name, calendar_type, is_leap_month)
            result = analyzer.get_verbose_result()
            
            # Convert to JSON string (for saving)
            json_str = json.dumps(result, ensure_ascii=False, indent=4)
            
            # Display using GUI method (Fix: call self.display_result)
            self.display_result(result)
            
            # Save to file
            import os
            output_dir = "/Users/loyalee/Desktop/명리심리연구소"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            safe_name = name.strip() if name else "Unknown"
            safe_name = safe_name.replace("/", "_").replace("\\", "_")
            filename = f"saju_result_{safe_name}.json"
            
            output_path = os.path.join(output_dir, filename)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(json_str)
            messagebox.showinfo("완료", f"분석이 완료되었습니다.\n'{filename}' 파일로 저장되었습니다.")
            
        except ValueError:
            messagebox.showerror("오류", "날짜나 시간 형식이 올바르지 않습니다.\n예: 1990-01-01, 14:30")
        except Exception as e:
            messagebox.showerror("오류", f"분석 중 문제가 발생했습니다:\n{e}")
            import traceback
            traceback.print_exc()

    def display_result(self, result):
        self.result_area.delete(1.0, tk.END)
        
        info = result['info']
        pillars = result['four_pillars']
        ohaeng = result['five_elements']
        daewoon = result['daewoon']
        sibseong = result.get('sibseong', {})
        sinsal = result.get('sinsal', {})
        interactions = result.get('interactions', [])
        gongmang = result.get('gongmang', '')
        strength = result.get('strength', {})
        yongsin = result.get('yongsin', '')
        luck_cycle = result.get('luck_cycle', {})
        
        output = f"✨ [{info['name']}] 님의 사주 분석 결과 ✨\n\n"
        output += f"📅 입력 날짜: {info['input_date']} ({info['calendar_type']})\n"
        if info['calendar_type'] == "음력(Lunar)" and info['is_leap_month']:
            output += f"   (윤달 적용됨)\n"
        output += f"⏰ 시간: {info['input_time']}\n"
        output += f"👤 성별: {info['gender']}\n"
        output += "-" * 50 + "\n\n"
        
        output += "[🏮 사주팔자 상세 분석]\n\n"
        output += f"{'':<6} {'시주':<8} {'일주':<8} {'월주':<8} {'년주':<8}\n"
        output += "-" * 45 + "\n"
        
        h_gan = pillars['hour']['gan']
        d_gan = pillars['day']['gan']
        m_gan = pillars['month']['gan']
        y_gan = pillars['year']['gan']
        
        output += f"{'천간':<6} {h_gan:<8} {d_gan:<8} {m_gan:<8} {y_gan:<8}\n"
        output += "-" * 45 + "\n"
        
        h_ji = pillars['hour']['ji']
        d_ji = pillars['day']['ji']
        m_ji = pillars['month']['ji']
        y_ji = pillars['year']['ji']
        
        output += f"{'지지':<6} {h_ji:<8} {d_ji:<8} {m_ji:<8} {y_ji:<8}\n"
        output += "\n" + "-" * 50 + "\n\n"
        
        output += "[🌲 오행 분석]\n"
        for element, count in ohaeng.items():
            bar = "■" * count + "□" * (4 - count)
            output += f"{element}: {count}개 {bar}\n"
        output += "\n" + "-" * 50 + "\n"
        
        if strength:
            output += f"[💪 신강/신약 & 용신]\n"
            output += f"- 구분: {strength['verdict']} (점수: {strength['score']})\n"
            if isinstance(yongsin, dict):
                p = yongsin.get('primary', {})
                s = yongsin.get('secondary', {})
                output += f"- 주용신: {p.get('element', '') if p else '없음'} ({p.get('type', '') if p else ''})\n"
                output += f"- 희신: {s.get('element', '') if s else '없음'}\n"
            else:
                output += f"- 용신: {yongsin}\n"
            output += "\n" + "-" * 50 + "\n"

        output += f"[🌊 대운 (Luck Cycles)]\n"
        if daewoon:
             pillars_list = daewoon.get('pillars', [])
             daewoon_strs = [f"{d['age']}세 {d['ganji']}" for d in pillars_list]
             for i in range(0, len(daewoon_strs), 5):
                 output += " -> ".join(daewoon_strs[i:i+5]) + "\n"
        
        self.result_area.insert(tk.END, output)

if __name__ == "__main__":
    root = tk.Tk()
    app = SajuGUI(root)
    print("✨ 프로그램이 실행되었습니다! 새로 뜬 창을 확인해주세요. (Dock에 파이썬 아이콘이 뜰 수 있습니다) ✨")
    root.mainloop()
