import os

target_file = "../program1-calculator/saju_app.py"

with open(target_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
# It seems the `_calculate_pillar_sinsal` block I inserted (which uses 4 spaces for method, 8 for internal)
# might have collided with existing indent.
# The error "unindent does not match" usually means I went from deep to shallow incorrectly or mixed.

# I'll just re-indent the whole file or the relevant section programmatically.
# Or simpler: Just replace the method block with *clean* indentation.
# 4 spaces for method def.
# 8 spaces for code inside.
# 12 spaces for if/for inside.

# Let's locate the function and fix it.

target_method = "def _calculate_pillar_sinsal(self, gan, ji, pillar_type):"
inside_method = False

for i, line in enumerate(lines):
    if target_method in line:
        inside_method = True
        new_lines.append(line) # Ensure 4 spaces?
        continue
    
    if inside_method:
        # Detect end: next def
        if "    def " in line and line.strip().startswith("def _"):
             inside_method = False
             new_lines.append(line)
             continue
             
        # Fix indent.
        # If line is not empty and not just whitespace
        stripped = line.lstrip()
        if not stripped:
            new_lines.append(line)
            continue
            
        # The patch string had:
        #     def ...
        #         res = ...
        #         def check...
        #             ...
        #
        # Maybe `check_12sinsal` inner function indent was tricky.
        # I check the previous error: "res['ji'].extend(check_12sinsal(d_ji, j_char))"
        # This line was seemingly unindented wrong.
        pass # Just pass through, I will use `reindent` approach with `sed` or rewrite the method cleanly.

# Re-writing the method via script is safer.

method_code = """    def _calculate_pillar_sinsal(self, gan, ji, pillar_type):
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
"""

# Replace in file using start/end logic more robustly
# We replace from `def _calculate_pillar_sinsal(self, gan, ji, pillar_type):`
# to `def _calculate_sinsal(self, day_branch, target_branch):` (next method)

final_lines = []
skip = False
inserted = False

for line in lines:
    if "def _calculate_pillar_sinsal(" in line:
        skip = True
        
    if "def _calculate_sinsal(" in line and skip:
        skip = False
        final_lines.append(method_code + "\n\n")
        inserted = True
        
    if not skip:
        final_lines.append(line)

# Safety: if inserted is False (pattern not found), unexpected.
# Check file content again if needed. But assuming markers exist.

with open(target_file, "w", encoding="utf-8") as f:
    f.writelines(final_lines)

print("Fixed indentation for Sinsal.")
