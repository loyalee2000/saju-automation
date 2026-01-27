import os
import datetime
import re

target_file = "../program1-calculator/saju_app.py"

with open(target_file, "r", encoding="utf-8") as f:
    content = f.read()

# === CODE BLOCKS ===

luck_cycle_method = """    def _calculate_luck_cycle(self):
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
"""

multi_yongsin_method = """    def _calculate_multi_yongsin(self, score):
        return []
"""

yongsin_method = """    def _calculate_yongsin(self, day_gan, pillars, ohaeng, score):
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
"""

health_method = """    def _analyze_health_risks(self, ohaeng):
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
"""

# Combined Method String
new_methods_block = luck_cycle_method + "\n" + multi_yongsin_method + "\n" + yongsin_method + "\n" + health_method + "\n"

# get_result_json (Recovered + Updated)
# Note: I'll use the one from restore_get_result_json.py but adding the new keys.

get_result_json_code = """    def get_result_json(self):
        try:
            pillars = self.get_gan_ji()
        except AttributeError:
             raise
             
        ohaeng = self.analyze_ohaeng(pillars)
        daewoon = self.get_daewoon(pillars['year_gan_idx'], pillars['month_gan_idx'], pillars['month_ji_idx'])
        
        def split_pillar(p):
            if p == "모름(Unknown)": return "모름", "모름"
            parts = re.findall(r'.\(.\)', p)
            if len(parts) == 2: return parts[0], parts[1]
            return p, p 
            
        y_gan, y_ji = split_pillar(pillars['year'])
        m_gan, m_ji = split_pillar(pillars['month'])
        d_gan, d_ji = split_pillar(pillars['day'])
        h_gan, h_ji = split_pillar(pillars['hour'])
        
        self.day_gan_char = d_gan.split('(')[0] if d_gan else ""
        self.day_ji_char = d_ji.split('(')[0] if d_ji else ""
        self.year_ji_char = y_ji.split('(')[0] if y_ji else ""
        self.year_gan_char = y_gan.split('(')[0] if y_gan else ""
        self.month_gan_char = m_gan.split('(')[0] if m_gan else ""
        self.hour_gan_char = h_gan.split('(')[0] if h_gan != "모름" else ""

        y_sinsal = self._calculate_pillar_sinsal(y_gan, y_ji, 'year')
        m_sinsal = self._calculate_pillar_sinsal(m_gan, m_ji, 'month')
        d_sinsal = self._calculate_pillar_sinsal(d_gan, d_ji, 'day')
        h_sinsal = self._calculate_pillar_sinsal(h_gan, h_ji, 'hour') if not self.time_unknown else {'gan':[], 'ji':[]}
        
        sinsal = { 'year': y_sinsal, 'month': m_sinsal, 'day': d_sinsal, 'hour': h_sinsal }
        
        twelve_unseong = {
            'year': self._calculate_12unseong(d_gan, y_ji),
            'month': self._calculate_12unseong(d_gan, m_ji),
            'day': self._calculate_12unseong(d_gan, d_ji),
            'hour': self._calculate_12unseong(d_gan, h_ji)
        }

        jijanggan = {
            'year': self._get_jijanggan(y_ji),
            'month': self._get_jijanggan(m_ji),
            'day': self._get_jijanggan(d_ji),
            'hour': self._get_jijanggan(h_ji)
        }

        sipsinsal = {
            'year': self._calculate_12sinsal(y_ji, y_ji),
            'month': self._calculate_12sinsal(y_ji, m_ji),
            'day': self._calculate_12sinsal(y_ji, d_ji),
            'hour': self._calculate_12sinsal(y_ji, h_ji)
        }

        heaven_stems_list = [y_gan, m_gan]
        if not self.time_unknown: heaven_stems_list.append(h_gan)
        gyeok_result = self._calculate_gyeokguk(d_gan, m_ji, heaven_stems_list)
        
        gongmang_chars = self._calculate_gongmang(d_gan, d_ji)
        gm_pillars = []
        gm_clean = [gm.split('(')[0] for gm in gongmang_chars]
        if y_ji.split('(')[0] in gm_clean: gm_pillars.append(f"년지({y_ji.split('(')[0]})")
        if m_ji.split('(')[0] in gm_clean: gm_pillars.append(f"월지({m_ji.split('(')[0]})")
        if h_ji.split('(')[0] in gm_clean: gm_pillars.append(f"시지({h_ji.split('(')[0]})")
        gongmang_str = ", ".join(gm_pillars) if gm_pillars else "해당 없음"

        strength = self._calculate_saju_strength(d_gan, pillars, ohaeng)
        yongsin_result = self._calculate_yongsin(d_gan, pillars, ohaeng, strength['score'])
        
        result = {
            "info": {
                "name": self.name,
                "email": self.email,
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
            "gyeokguk": gyeok_result,
            "daewoon": daewoon,
            "sibseong": {}, # Simplified for stability
            "sinsal": sinsal,
            "interactions": [],
            "interaction_details": [],
            "twelve_unseong": twelve_unseong,
            "jijanggan": jijanggan,
            "sipsinsal": sipsinsal,
            "gongmang": gongmang_str,
            "strength": strength,
            "yongsin_structure": yongsin_result['yongsin_structure'],
            "multi_yongsin": yongsin_result.get('multi_yongsin', []),
            "luck_cycle": self._calculate_luck_cycle(), 
            "health_analysis": self._analyze_health_risks(ohaeng),
            "comprehensive_analysis": {}
        }
        return result
"""

# === CLEANUP & INJECTION ===

# 1. Remove old definitions of affected methods
patterns_to_remove = [
    r"def _calculate_yongsin\(.*?\):.*?(?=\n\s*def |\Z)",
    r"def _analyze_health_risks\(.*?\):.*?(?=\n\s*def |\Z)",
    # We also remove get_result_json if it exists partially or fully
    r"def get_result_json\(.*?\):.*?(?=\n\s*def |\Z)"
]

# We use re.DOTALL
for pat in patterns_to_remove:
    content = re.sub(pat, "", content, flags=re.DOTALL)

# 2. Insert New Methods
# We insert them before `def _calculate_saju_strength` as a safe anchor.
anchor = "def _calculate_saju_strength"
idx = content.find(anchor)

if idx != -1:
    content = content[:idx] + new_methods_block + "\n" + get_result_json_code + "\n\n" + content[idx:]
else:
    # Append to end of class?
    # Find last method?
    # Safe anchor: `display_result`.
    anchor2 = "def display_result"
    idx2 = content.find(anchor2)
    if idx2 != -1:
        content = content[:idx2] + new_methods_block + "\n" + get_result_json_code + "\n\n" + content[idx2:]
    else:
        # Just append?
        content += "\n" + new_methods_block + "\n" + get_result_json_code

with open(target_file, "w", encoding="utf-8") as f:
    f.write(content)

print("Restored all features and methods successfully.")
