import os

target_file = "../program1-calculator/saju_app.py"

with open(target_file, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update _calculate_daewoon_num to use ceil
# Search for: score = abs(term_diff) / 3
# Replace with: import math; return math.ceil(abs(term_diff) / 3)

# We need to find the specific line.
#     def _calculate_daewoon_num(self, is_forward):
#         ...
#         score = abs(term_diff) / 3
#         return round(score) 

# I'll replace the whole method _calculate_daewoon_num
new_daewoon_method = """    def _calculate_daewoon_num(self, is_forward):
        # Find prev/next jeolgi
        year = self.adjusted_dt.year
        month = self.adjusted_dt.month
        day = self.adjusted_dt.day
        
        # We need exact Jeolgi times
        # Reuse internal helper logic if possible, or use standard approximation
        # But wait, self.get_daewoon calls this? No, self.get_daewoon takes indices.
        # This method is likely unused? 
        # Let's check where it's called.
        # It's called inside get_daewoon? No.
        # Ah, I need to check `get_daewoon`.
        pass
"""

# Wait, `get_daewoon` in `saju_app.py` usually calls logic?
# Let's look at `get_daewoon` implementation in the file.
# grep showed `def get_daewoon`.
# I'll just rewrite `_calculate_pillar_sinsal` first as it's the big chunk.

new_sinsal_method = """    def _calculate_pillar_sinsal(self, gan, ji, pillar_type):
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
            
            # Ji-sal / Yeok-ma
            if group == '인오술':
                if target_ji == '인': found.append("지살")
                elif target_ji == '신': found.append("역마")
                elif target_ji == '묘': found.append("년살") # Dohwa
                elif target_ji == '자': found.append("재살")
                elif target_ji == '오': found.append("장성살")
                elif target_ji == '유': found.append("육해살")
                elif target_ji == '술': found.append("화개")
                elif target_ji == '진': found.append("월살")
                elif target_ji == '사': found.append("망신살")
                elif target_ji == '해': found.append("겁살")
                elif target_ji == '축': found.append("천살")
                elif target_ji == '미': found.append("반안살")
            elif group == '사유축':
                if target_ji == '사': found.append("지살")
                elif target_ji == '해': found.append("역마")
                elif target_ji == '오': found.append("년살")
                elif target_ji == '묘': found.append("재살")
                elif target_ji == '유': found.append("장성살")
                elif target_ji == '자': found.append("육해살")
                elif target_ji == '축': found.append("화개")
                elif target_ji == '미': found.append("월살")
                elif target_ji == '신': found.append("망신살")
                elif target_ji == '인': found.append("겁살")
                elif target_ji == '진': found.append("천살")
                elif target_ji == '술': found.append("반안살")
            elif group == '신자진':
                if target_ji == '신': found.append("지살")
                elif target_ji == '인': found.append("역마")
                elif target_ji == '유': found.append("년살")
                elif target_ji == '오': found.append("재살")
                elif target_ji == '자': found.append("장성살")
                elif target_ji == '묘': found.append("육해살")
                elif target_ji == '진': found.append("화개")
                elif target_ji == '술': found.append("월살")
                elif target_ji == '해': found.append("망신살")
                elif target_ji == '사': found.append("겁살")
                elif target_ji == '미': found.append("천살")
                elif target_ji == '축': found.append("반안살")
            elif group == '해묘미':
                if target_ji == '해': found.append("지살")
                elif target_ji == '사': found.append("역마")
                elif target_ji == '자': found.append("년살")
                elif target_ji == '유': found.append("재살")
                elif target_ji == '묘': found.append("장성살")
                elif target_ji == '오': found.append("육해살")
                elif target_ji == '미': found.append("화개")
                elif target_ji == '축': found.append("월살")
                elif target_ji == '인': found.append("망신살")
                elif target_ji == '신': found.append("겁살")
                elif target_ji == '술': found.append("천살")
                elif target_ji == '진': found.append("반안살")
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
        
        amrok_map = {'갑': '해', '을': '술', '병': '신', '정': '미', '무': '신', '기': '미', '경': '사', '신': '진', '임': '인', '계': '축'}
        if amrok_map.get(d_gan) == j_char: res['ji'].append("암록")

        # Yangin (Expanded for Yin stems to match Posteller)
        yangin_map = {
            '갑': '묘', '병': '오', '무': '오', '경': '유', '임': '자', # Yang
            '을': '진', '정': '미', '기': '미', '신': '술', '계': '축'  # Yin (Gwan-dae)
        }
        if yangin_map.get(d_gan) == j_char: res['ji'].append("양인살")

        # Woldeok
        if hasattr(self, 'month_ji_char'):
            m_ji_ref = self.month_ji_char
            wd_stem = None
            if m_ji_ref in ['인', '오', '술']: wd_stem = '병'
            elif m_ji_ref in ['신', '자', '진']: wd_stem = '임'
            elif m_ji_ref in ['해', '묘', '미']: wd_stem = '갑'
            elif m_ji_ref in ['사', '유', '축']: wd_stem = '경'
            
            if wd_stem and g_char == wd_stem:
                res['gan'].append("월덕귀인")

        # Baekho
        baekho_pairs = ["갑진", "을미", "병술", "정축", "무진", "임술", "계축"]
        if (g_char + j_char) in baekho_pairs:
            res['gan'].append("백호대살"); res['ji'].append("백호대살")

        # Goegang
        goegang_pairs = ["무진", "무술", "경진", "경술", "임진", "임술"]
        if (g_char + j_char) in goegang_pairs:
            res['gan'].append("괴강살"); res['ji'].append("괴강살")
            
        # Hyeonchim (Added '미')
        if g_char in ['갑', '신']: res['gan'].append("현침살")
        if j_char in ['묘', '오', '신', '미']: res['ji'].append("현침살")
        
        # Gwimun
        gwimun_map = {'자': '유', '축': '오', '인': '미', '묘': '신', '진': '해', '사': '술',
                      '유': '자', '오': '축', '미': '인', '신': '묘', '해': '진', '술': '사'}
        if gwimun_map.get(d_ji) == j_char: res['ji'].append("귀문관살")

        # Cheoneul
        cheoneul_map = {'갑': ['축','미'], '무': ['축','미'], '경': ['축','미'], '을': ['자','신'], '기': ['자','신'], '병': ['해','유'], '정': ['해','유'], '신': ['인','오'], '임': ['사','묘'], '계': ['사','묘']}
        if j_char in cheoneul_map.get(d_gan, []): res['ji'].append("천을귀인")
            
        # Geumyeo
        geumyeo_map = {'갑': '진', '을': '사', '병': '미', '정': '신', '무': '미', '기': '신', '경': '술', '신': '해', '임': '축', '계': '인'}
        if geumyeo_map.get(d_gan) == j_char: res['ji'].append("금여성")

        # Hakdang
        hakdang_map = {'갑': '해', '을': '오', '병': '인', '정': '유', '무': '인', '기': '유', '경': '사', '신': '자', '임': '신', '계': '묘'}
        if hakdang_map.get(d_gan) == j_char: res['ji'].append("학당귀인")
        for stem in [y_gan, m_gan, h_gan]:
            if stem and hakdang_map.get(stem) == j_char:
                if("학당귀인" not in res['ji']): res['ji'].append("학당귀인")

        # Cheonju (Fixed 'Gi' -> 'Yu')
        cheonju_map = {'갑': '사', '을': '오', '병': '사', '정': '오', '무': '사', '기': '유', '경': '해', '신': '자', '임': '인', '계': '묘'}
        if cheonju_map.get(d_gan) == j_char: res['ji'].append("천주귀인")
            
        # Gwangwi
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

        # Cheonmun
        if j_char in ['술', '해']: res['ji'].append("천문성")
        
        # Cheoneui (Added)
        # Calculates if j_char is Cheoneui wrt Month Ji
        # Need Month Ji.
        if m_ji:
             # Logic matching _calculate_cheoneui: Month Prev is Cheoneui
             order = ['자','축','인','묘','진','사','오','미','신','유','술','해']
             if m_ji in order:
                 idx = order.index(m_ji)
                 prev_idx = (idx - 1) % 12
                 cheoneui_ji = order[prev_idx]
                 if j_char == cheoneui_ji:
                     res['ji'].append("천의성")

        # Gwasuk
        season_map = {'해':'수','자':'수','축':'수', '인':'목','묘':'목','진':'목', '사':'화','오':'화','미':'화', '신':'금','유':'금','술':'금'}
        yg = leason_map = season_map.get(y_ji, '')
        if yg == '목' and j_char == '축': res['ji'].append("과숙살")
        elif yg == '화' and j_char == '진': res['ji'].append("과숙살")
        elif yg == '금' and j_char == '미': res['ji'].append("과숙살")
        elif yg == '수' and j_char == '술': res['ji'].append("과숙살")
            
        return res
"""

# 2. Fix Daewoon rounding
# Locate get_daewoon_start ? 
# Or just search for the rounding logic.
# I will use a search-and-replace for the specific rounding line.
# "score = abs(term_diff) / 3"
# "return round(score)"

method_to_search = """        score = abs(term_diff) / 3
        return round(score)"""

method_replacement = """        score = abs(term_diff) / 3
        import math
        return math.ceil(score)"""

# Read and Apply
import re

start_marker = "    def _calculate_pillar_sinsal(self, gan, ji, pillar_type):"
start_idx = content.find(start_marker)
if start_idx == -1:
    print("Could not find _calculate_pillar_sinsal.")
    exit(1)
    
next_method_idx = content.find("\n    def ", start_idx + 100)
if next_method_idx == -1:
    print("Could not find next method after sinsal.")
else:
    content = content[:start_idx] + new_sinsal_method + content[next_method_idx:]

# Apply Daewoon fix
if method_to_search in content:
    content = content.replace(method_to_search, method_replacement)
    print("Applied Daewoon rounding fix (ceil).")
else:
    # Try simpler match
    print("Could not find exact Daewoon rounding lines. Trying manual regex.")
    content = re.sub(r'return round\(score\)', 'import math; return math.ceil(score)', content)
    print("Applied Daewoon rounding fix (regex).")

with open(target_file, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated Saju Logic.")
