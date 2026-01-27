import os

target_file = "../program1-calculator/saju_app.py"

with open(target_file, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update _calculate_daewoon_num
# diff_days = diff_seconds / (24 * 3600)
# daewoon_num = int(diff_days / 3) -> round(diff_days / 3)

if "daewoon_num = int(diff_days / 3)" in content:
    content = content.replace("daewoon_num = int(diff_days / 3)", "daewoon_num = int(round(diff_days / 3))")

# 2. Update get_result_json to save all gan chars
# Find where self.day_gan_char is set.
# "self.day_gan_char = d_gan.split('(')[0]"
# We want to add:
# self.year_gan_char = y_gan.split('(')[0]
# self.month_gan_char = m_gan.split('(')[0]
# self.hour_gan_char = h_gan.split('(')[0] if h_gan else ""

marker = "self.day_gan_char = d_gan.split('(')[0]"
injection = """        self.day_gan_char = d_gan.split('(')[0]
        self.year_gan_char = y_gan.split('(')[0]
        self.month_gan_char = m_gan.split('(')[0]
        self.hour_gan_char = h_gan.split('(')[0] if h_gan != "모름" else """""
# Note: h_gan might be "모름".

if marker in content and "self.year_gan_char" not in content:
    content = content.replace(marker, injection)
    
# 3. Update _calculate_pillar_sinsal
# We replace the whole method again to be clean and include new logic.

new_sinsal_method = """    def _calculate_pillar_sinsal(self, gan, ji, pillar_type):
        res = {'gan': [], 'ji': []}
        
        g_char = gan.split('(')[0] if gan else ""
        j_char = ji.split('(')[0] if ji else ""
        
        # Ensure we have context
        if not hasattr(self, 'day_gan_char'): return res
        
        d_gan = self.day_gan_char
        d_ji = self.day_ji_char
        y_ji = getattr(self, 'year_ji_char', '')
        y_gan = getattr(self, 'year_gan_char', '')
        m_gan = getattr(self, 'month_gan_char', '')
        h_gan = getattr(self, 'hour_gan_char', '')
        
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
            y_res = check_12sinsal(y_ji, j_char)
            for s in y_res:
                if s not in res['ji']: res['ji'].append(s)

        # Broad Check
        if j_char in ['자', '오', '묘', '유'] and "도화" not in res['ji']: res['ji'].append("도화")
        if j_char in ['인', '신', '사', '해'] and "역마" not in res['ji']: res['ji'].append("역마")
        if j_char in ['진', '술', '축', '미'] and "화개" not in res['ji']: res['ji'].append("화개")

        # === 2. Gilseong / Sal ===
        
        # Amrok (Updated: Hex-Combine with Geonrok)
        # Gap-Hae, Eul-Sul, Byung-Shin, Jung-Mi, Mu-Shin, Gi-Mi, Gyeong-Sa, Shin-Jin, Im-In, Gye-Chuk
        amrok_map = {'갑': '해', '을': '술', '병': '신', '정': '미', '무': '신', '기': '미', '경': '사', '신': '진', '임': '인', '계': '축'}
        if amrok_map.get(d_gan) == j_char: res['ji'].append("암록")

        # Yangin (Day Gan Base)
        # Gap-Myo, Byung-Wu, Mu-Wu, Gyeong-Yu, Im-Ja
        yangin_map = {'갑': '묘', '병': '오', '무': '오', '경': '유', '임': '자'}
        if yangin_map.get(d_gan) == j_char: res['ji'].append("양인살")

        # Woldeok (Month Ji Base -> Check Heavenly Stem)
        # In-O-Sul -> Byung
        # Shin-Ja-Jin -> Im
        # Hae-Myo-Mi -> Gap
        # Sa-Yu-Chuk -> Gyeong
        
        # Verify Month Ji
        m_ji_char = getattr(self, 'month_ji_char', '')
        if not m_ji_char and hasattr(self, 'month'):
             # Try to get from Month Pillar if not saved? 
             # Wait, get_result_json saves month_ji_char? No, not yet.
             # I need to access Month Ji.
             pass
        # I actually should add `self.month_ji_char` to `get_result_json` injection too.
        # Assuming I do that, or parse `self.month` here? 
        # `self.month` is integer (1~12). Not GanJi.
        # The pillar is computed in `get_result_json`.
        # I MUST inject `self.month_ji_char` in `get_result_json`.
        
        # Woldeok Logic placeholder (relies on m_ji_char)
        if hasattr(self, 'month_ji_char'):
            m_ji = self.month_ji_char
            wd_stem = None
            if m_ji in ['인', '오', '술']: wd_stem = '병'
            elif m_ji in ['신', '자', '진']: wd_stem = '임'
            elif m_ji in ['해', '묘', '미']: wd_stem = '갑'
            elif m_ji in ['사', '유', '축']: wd_stem = '경'
            
            if wd_stem and g_char == wd_stem:
                res['gan'].append("월덕귀인")
                # Some display logic puts it in Ji as well for visualization, but standard is Gan.
                # If User's JSON showed it on Day row (Gan/Ji column), maybe add to Ji too?
                # Let's add to both for visibility if needed? No, standard is Gan.

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
        
        # Gwimun
        gwimun_map = {'자': '유', '축': '오', '인': '미', '묘': '신', '진': '해', '사': '술',
                      '유': '자', '오': '축', '미': '인', '신': '묘', '해': '진', '술': '사'}
        if gwimun_map.get(d_ji) == j_char: res['ji'].append("귀문관살")

        # Cheoneul (Day Gan base)
        cheoneul_map = {'갑': ['축','미'], '무': ['축','미'], '경': ['축','미'], '을': ['자','신'], '기': ['자','신'], '병': ['해','유'], '정': ['해','유'], '신': ['인','오'], '임': ['사','묘'], '계': ['사','묘']}
        if j_char in cheoneul_map.get(d_gan, []): res['ji'].append("천을귀인")
            
        # Geumyeo (Day Gan base)
        geumyeo_map = {'갑': '진', '을': '사', '병': '미', '정': '신', '무': '미', '기': '신', '경': '술', '신': '해', '임': '축', '계': '인'}
        if geumyeo_map.get(d_gan) == j_char: res['ji'].append("금여성")

        # Hakdang (Expanded: Check all Stems)
        # Specifically Day Gan is primary. But maybe Month Gan/Year Gan too.
        # Map: Yang->Jangsaeng, Yin->Jangsaeng(Legacy)? or Yin->Saji?
        # Posteller seems to follow: Yang->Jangsaeng, Yin->Jangsaeng.
        # Gap-Hae, Eul-Wu, Byung-In, Jung-Yu, Mu-In, Gi-Yu, Gyeong-Sa, Shin-Ja, Im-Shin, Gye-Myo.
        hakdang_map = {'갑': '해', '을': '오', '병': '인', '정': '유', '무': '인', '기': '유', '경': '사', '신': '자', '임': '신', '계': '묘'}
        
        # Check Day Gan
        if hakdang_map.get(d_gan) == j_char: res['ji'].append("학당귀인")
        # Check Year/Month/Hour Gans
        for stem in [y_gan, m_gan, h_gan]:
            if stem and hakdang_map.get(stem) == j_char:
                if("학당귀인" not in res['ji']): res['ji'].append("학당귀인")

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

        # Jeong-rok
        rok_map = {'갑': '인', '을': '묘', '병': '사', '정': '오', '무': '사', '기': '오', '경': '신', '신': '유', '임': '해', '계': '자'}
        if rok_map.get(d_gan) == j_char: res['ji'].append("정록")

        # Cheonmun ('Sul' or 'Hae')
        if j_char in ['술', '해']: res['ji'].append("천문성")

        # Gwasuk (Year Ji Base)
        season_map = {'해':'수','자':'수','축':'수', '인':'목','묘':'목','진':'목', '사':'화','오':'화','미':'화', '신':'금','유':'금','술':'금'}
        yg = season_map.get(y_ji, '')
        if yg == '목' and j_char == '축': res['ji'].append("과숙살")
        elif yg == '화' and j_char == '진': res['ji'].append("과숙살")
        elif yg == '금' and j_char == '미': res['ji'].append("과숙살")
        elif yg == '수' and j_char == '술': res['ji'].append("과숙살")
            
        return res
"""

# Injection for self.month_ji_char in get_result_json
# Find: self.day_ji_char = d_ji.split('(')[0]
# Add: self.month_ji_char = m_ji.split('(')[0]
# Also need self.year_ji_char (already there in prev logic?)
# In Step 424 Ref: line 526: y_gan, y_ji = ...
# My Step 360 Patch added `self.year_ji_char`, `self.day_ji_char`.
# I should ensure all are present.

injection_ji = """        self.day_ji_char = d_ji.split('(')[0]
        self.year_ji_char = y_ji.split('(')[0]
        self.month_ji_char = m_ji.split('(')[0]"""

if "self.day_ji_char =" in content and "self.month_ji_char" not in content:
    content = content.replace("self.day_ji_char = d_ji.split('(')[0]", injection_ji)

# Replace the method
start_m = "    def _calculate_pillar_sinsal(self, gan, ji, pillar_type):"
end_m = "    def _calculate_sinsal(self, day_branch, target_branch):"
s_idx = content.find(start_m)
e_idx = content.find(end_m)

if s_idx != -1 and e_idx != -1:
    content = content[:s_idx] + new_sinsal_method + "\n" + content[e_idx:]

with open(target_file, "w", encoding="utf-8") as f:
    f.write(content)

print("Applied 1974 fixes: Daewoon Rounding, Sinsal (Amrok, Yangin, Woldeok(Month), Hakdang(Broad)).")
