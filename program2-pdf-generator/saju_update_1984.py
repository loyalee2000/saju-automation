import os

target_file = "../program1-calculator/saju_app.py"

with open(target_file, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update Precise Data for 1984 Lichun
# Find: if year == 1984 and month == 5:
# Note: In Step 281, I appended 1988 line.
# "if year == 1984 and month == 5: return datetime(1984, 5, 5, 10, 23)"
# "        if year == 1988 and month == 2: return datetime(1988, 2, 4, 17, 43)"

new_solar_data = """        if year == 1984 and month == 5: return datetime(1984, 5, 5, 10, 23)
        if year == 1984 and month == 2: return datetime(1984, 2, 4, 23, 18)
        if year == 1988 and month == 2: return datetime(1988, 2, 4, 17, 43)"""

if "if year == 1988 and month == 2:" in content:
    content = content.replace(
        "if year == 1984 and month == 5: return datetime(1984, 5, 5, 10, 23)\n        if year == 1988 and month == 2: return datetime(1988, 2, 4, 17, 43)",
        new_solar_data
    )
    
# 2. Update _calculate_pillar_sinsal to include new Sinsals
# We need to find the method and inject logic.
# Method signature: def _calculate_pillar_sinsal(self, gan, ji, pillar_type):
# We can just replace the whole method again with the expanded version.

new_sinsal_method = """    def _calculate_pillar_sinsal(self, gan, ji, pillar_type):
        res = {'gan': [], 'ji': []}
        
        g_char = gan.split('(')[0] if gan else ""
        j_char = ji.split('(')[0] if ji else ""
        
        if not hasattr(self, 'day_ji_char') or not hasattr(self, 'day_gan_char'):
            return res
            
        d_gan = self.day_gan_char
        d_ji = self.day_ji_char
        y_ji = getattr(self, 'year_ji_char', '')
        
        # === 1. 12 Sinsal (Dual Base) ===
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
            for s in check_12sinsal(y_ji, j_char):
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
        goegang_pairs = ["무진", "무술", "경진", "경술", "임진", "임술"]
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
            
        # Gwangwi (Day Gan base) - Using standard
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

        # === NEW SINSALS ===
        
        # Jeong-rok (정록/건록) - Day Gan vs Ji
        rok_map = {'갑': '인', '을': '묘', '병': '사', '정': '오', '무': '사', '기': '오', '경': '신', '신': '유', '임': '해', '계': '자'}
        if rok_map.get(d_gan) == j_char: res['ji'].append("정록")

        # Cheonmun (천문성) - 'Sul' or 'Hae' in Ji
        if j_char in ['술', '해']: res['ji'].append("천문성")

        # Gwasuk (과숙살) / Goshin (고신살) - Based on Year Ji (Season)
        # Year Ji Season: 
        # In-O-Sul(Fire) -> Gwasuk: Mi, Goshin: Hae? No.
        # Strict Rule:
        # In-Myo-Jin -> Gwa: Chuk, Go: Sa
        # Sa-O-Mi -> Gwa: Jin, Go: Shin
        # Shin-Yu-Sul -> Gwa: Mi, Go: Hae
        # Hae-Ja-Chuk -> Gwa: Sul, Go: In
        
        y_group = None
        if y_ji in ['인','오','술']: y_group = '화' # In-O-Sul -> Sa-O-Mi equivalent season? No used Banghap usually.
        # Actually Gwasuk is based on Banghap (Directional)
        # In-Myo-Jin (East) -> Gwa: Chuk
        # Sa-O-Mi (South) -> Gwa: Jin
        # Shin-Yu-Sul (West) -> Gwa: Mi
        # Hae-Ja-Chuk (North) -> Gwa: Sul
        
        # Map Year Ji to Season Group
        season_map = {
            '인':'목','묘':'목','진':'목',
            '사':'화','오':'화','미':'화',
            '신':'금','유':'금','술':'금',
            '해':'수','자':'수','축':'수'
        }
        
        yg = season_map.get(y_ji)
        
        if yg == '목': # In-Myo-Jin
            if j_char == '축': res['ji'].append("과숙살")
            if j_char == '사': res['ji'].append("고신살")
        elif yg == '화': # Sa-O-Mi
            if j_char == '진': res['ji'].append("과숙살")
            if j_char == '신': res['ji'].append("고신살")
        elif yg == '금': # Shin-Yu-Sul
            if j_char == '미': res['ji'].append("과숙살")
            if j_char == '해': res['ji'].append("고신살")
        elif yg == '수': # Hae-Ja-Chuk
            if j_char == '술': res['ji'].append("과숙살")
            if j_char == '인': res['ji'].append("고신살")

        return res
"""

# Replace the method using markers
start_marker = "    def _calculate_pillar_sinsal(self, gan, ji, pillar_type):"
end_marker = "    def _calculate_sinsal(self, day_branch, target_branch):"
# Look for regex or just basic replacement.

# We will read file, find index of start_marker
start_idx = content.find(start_marker)
# Find end of method. The method is long, ends before `def get_result_json` or similar `_calculate...`.
# Actually, in Step 348 restoration, it was before `get_result_json`? No, it was added earlier.
# The method order in Python doesn't strictly matter if we replace the whole block.
# Let's find the `_calculate_pillar_sinsal` block and replace it.

# Logic to find block end: look for next `    def `
next_def = content.find("    def ", start_idx + 20)
if start_idx != -1 and next_def != -1:
    content = content[:start_idx] + new_sinsal_method + "\n" + content[next_def:]
elif start_idx != -1:
    # Maybe it's the last method (unlikely)
    pass
    
# 3. Restore Yongsin and Strength Logic
# We need to replace the dummy methods added in Step 360.
# Dummy: `def _calculate_saju_strength(self, day_gan, pillars, ohaeng):`

yongsin_code = """    def _calculate_saju_strength(self, day_gan, pillars, ohaeng):
        # Weighting
        # Month Branch: 2.0
        # Day Branch: 1.5
        # Other Branches: 1.0
        # Stems: 1.0 (Day Stem excluded)
        
        # Determine Day Element
        me = self.day_gan_char
        my_elem = CHEONGAN_INFO[me]['element']
        
        # Calculate my side (Ex: Wood -> Wood, Water)
        my_side_score = 0
        total_score = 0
        
        # Elements mapping
        # Saeng (Resource) -> My Elem
        resource_elem = None
        for k, v in OHAENG_SANGSAENG.items():
            if v == my_elem: resource_elem = k; break
            
        def get_elem(char, is_gan):
            if is_gan: return CHEONGAN_INFO.get(char, {}).get('element')
            else: return JIJI_YONG.get(char, {}).get('element')
            
        # Iterate pillars to score
        # Year
        y_g_e = get_elem(pillars['year']['gan'].split('(')[0], True)
        y_j_e = get_elem(pillars['year']['ji'].split('(')[0], False)
        # Month
        m_g_e = get_elem(pillars['month']['gan'].split('(')[0], True)
        m_j_e = get_elem(pillars['month']['ji'].split('(')[0], False)
        # Day
        d_j_e = get_elem(pillars['day']['ji'].split('(')[0], False)
        # Hour
        if not self.time_unknown:
            h_g_e = get_elem(pillars['hour']['gan'].split('(')[0], True)
            h_j_e = get_elem(pillars['hour']['ji'].split('(')[0], False)
            
        # Scoring
        weights = {
            'y_g': 1.0, 'y_j': 1.0,
            'm_g': 1.0, 'm_j': 2.5, # Month Branch heavy weight
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
            total_score += w
            if elem == my_elem or elem == resource_elem:
                my_side_score += w
                
        # Calculate Strength
        # Threshold typically ~40-50%
        # If total ~ 8.0. My side > 4.0 -> Strong.
        # Adjust verdict
        
        ratio = my_side_score / total_score if total_score > 0 else 0.5
        score_val = int(ratio * 100)
        
        verdict = "중화 (Balanced)"
        if score_val >= 55: verdict = "신강 (Strong)"
        elif score_val <= 45: verdict = "신약 (Weak)"
        
        return {'score': score_val, 'verdict': verdict, 'calc_log': []}

    def _calculate_yongsin(self, day_gan, pillars, ohaeng, score):
        # Simple Yongsin logic
        # Weak -> Indong (Resource) or Bibyeok (Companion)
        # Strong -> Sik-sang, Jae-seong, Gwan-seong
        
        me = day_gan.split('(')[0]
        my_elem = CHEONGAN_INFO[me]['element']
        
        primary = "Unknown"
        secondary = "Unknown"
        
        # Elements ring
        # Wood -> Fire -> Earth -> Metal -> Water -> Wood
        ring = ['목', '화', '토', '금', '수']
        idx = ring.index(my_elem)
        
        resource = ring[idx-1]
        companion = my_elem
        output = ring[(idx+1)%5]
        wealth = ring[(idx+2)%5]
        official = ring[(idx+3)%5]
        
        if score <= 45: # Weak
            # Yongsin = Resource (usually)
            primary = resource
            secondary = companion
            reason = "신약하여 인성(Resource)을 용신으로 씀"
        elif score >= 55: # Strong
            # Yongsin = Output or Official or Wealth
            # Simple heuristic: heavily suppressed
            primary = output
            secondary = wealth
            reason = "신강하여 식상(Output)을 용신으로 씀"
        else:
            # Balanced -> Check climate?
            primary = output # Default flow
            secondary = wealth
            reason = "중화 사주, 흐름을 따름"
            
        return {
            'yongsin': primary,
            'yongsin_structure': {
                'primary': {'element': primary, 'type': 'Yongsin'},
                'secondary': {'element': secondary, 'type': 'Heesin'},
                'gisin': {'element': official if score <=45 else resource},
                'lucky_color': 'Red' if primary=='화' else ('Blue' if primary=='목' else ('Black' if primary=='수' else ('White' if primary=='금' else 'Yellow'))),
                'lucky_number': [2,7] if primary=='화' else ([3,8] if primary=='목' else ([1,6] if primary=='수' else ([4,9] if primary=='금' else [0,5]))),
                'unlucky_items': {}
            }
        }
        
    def _analyze_health_risks(self, ohaeng):
        # Check weak/missing elements
        risks = []
        for e, count in ohaeng.items():
            if count == 0:
                risks.append({'type': f"{e} 부족", 'desc': f"{e} 기운이 약해 관련 장기 주의"})
            if count >= 3:
                risks.append({'type': f"{e} 과다", 'desc': f"{e} 기운이 강해 균형 주의"})
        return {'risks': risks, 'summary': "오행 균형 분석"}
"""

dummy_start = "    def _calculate_saju_strength(self, day_gan, pillars, ohaeng):"
dummy_end = '    def _analyze_health_risks(self, ohaeng):\n        return {\'risks\': [], \'summary\': \'건강 분석 결과\'}\n'
# Finding the dummy block
d_start_idx = content.find(dummy_start)
# It ends after health risks return
health_sig = "return {'risks': [], 'summary': '건강 분석 결과'}"
h_idx = content.find(health_sig, d_start_idx)
next_def_after = content.find("    def ", h_idx + 10)

if d_start_idx != -1 and h_idx != -1:
    # Replace up to next_def (or end of dummy block)
    # If next_def exists, replace until there.
    if next_def_after != -1:
        content = content[:d_start_idx] + yongsin_code + "\n" + content[next_def_after:]
    else:
        # Maybe End of block
        content = content[:d_start_idx] + yongsin_code

with open(target_file, "w", encoding="utf-8") as f:
    f.write(content)

print("Applied 1984 fixes: Precise Data, Sinsals (Jeong-rok/Cheonmun/Gwasuk), Yongsin Restore.")
