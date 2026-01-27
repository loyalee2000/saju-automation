import os
import re

target_file = "../program1-calculator/saju_app.py"

with open(target_file, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update Solar Term Data (1988)
# Find existing precise_data map and inject 1988-02
new_solar_data = '''        if key in precise_data:
            return datetime.strptime(precise_data[key], "%Y-%m-%d %H:%M")
            
        if year == 1984 and month == 5: return datetime(1984, 5, 5, 10, 23)
        if year == 1988 and month == 2: return datetime(1988, 2, 4, 17, 43)

        # Fallback approximation (Improved)'''

if "if year == 1984 and month == 5:" in content:
    content = content.replace("if year == 1984 and month == 5: return datetime(1984, 5, 5, 10, 23)", 
                              "if year == 1984 and month == 5: return datetime(1984, 5, 5, 10, 23)\n        if year == 1988 and month == 2: return datetime(1988, 2, 4, 17, 43)")

# 2. Update Daewoon Rounding (Round to Floor/Int)
# Find: daewoon_num = int(round(diff_days / 3))
# Replace with: daewoon_num = int(diff_days / 3)
if "daewoon_num = int(round(diff_days / 3))" in content:
    content = content.replace("daewoon_num = int(round(diff_days / 3))", 
                              "daewoon_num = int(diff_days / 3)")

# 3. Comprehensive Sinsal Logic (Separated Gan/Ji)
# We will rewrite the _calculate_pillar_sinsal method to return {'gan': [], 'ji': []}
# And update the get_result_json to use it data structure.

new_sinsal_method = '''    def _calculate_pillar_sinsal(self, gan, ji, pillar_type):
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
'''

# Use regex to find the old method and replace
# The old method signature: def _calculate_pillar_sinsal(self, gan, ji, pillar_type):
pattern = r"def _calculate_pillar_sinsal\(self, gan, ji, pillar_type\):.+?return list\(set\(sinsal_list\)\)"
# Note: regex replace on multi-line is tricky. Better to find the start and just replace the block if structure is known.
# Or just append the new one and remove the old one. Python allows redefinition.
# But cleaner to replace.

# Actually, I'll use the unique signature `samhap_map = {` inside the method to identify it
if "samhap_map = {" in content:
    # Find start index
    start_idx = content.find("def _calculate_pillar_sinsal(self, gan, ji, pillar_type):")
    # Find end index (heuristic: next def or end of file)
    next_def = content.find("def ", start_idx + 10)
    
    if start_idx != -1 and next_def != -1:
        # replace the range
        content = content[:start_idx] + new_sinsal_method + "\n\n    " + content[next_def:]
    elif start_idx != -1:
        # Last method
        content = content[:start_idx] + new_sinsal_method

# 4. Update get_result_json to use new Sinsal structure
# Current structure calls it like: 'gan': self._calculate_pillar_sinsal(...), 'ji': self._calculate_pillar_sinsal(...)
# New structure needs: 
# res = self._calculate_pillar_sinsal(...)
# 'gan': res['gan'], 'ji': res['ji']

# Find the Sinsal construction block
sinsal_block_pattern = r"sinsal = \{[^\}]+\}"
replacement_sinsal = '''# Store for Sinsal calc
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
        }'''

# Replace the block
content = re.sub(sinsal_block_pattern, replacement_sinsal, content, flags=re.DOTALL)

with open(target_file, "w", encoding="utf-8") as f:
    f.write(content)

print("Applied 1988 specific updates.")
