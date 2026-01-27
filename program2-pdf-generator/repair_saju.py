import os

target_file = "../program1-calculator/saju_app.py"

with open(target_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
skip = False
repaired = False

# We need to insert the missing method and close the previous one properly
# expected break point:
# '            \'신(申)\': \'신자진\', \'자(子)\': \'신자진\', \'진(辰)\': \'신자진\',\n'
# followed by
# '        year_gan_idx = (saju_year - 4) % 10\n'

for i, line in enumerate(lines):
    new_lines.append(line)
    
    # Detect the specific corruption point
    if "'진(辰)': '신자진'," in line and i+1 < len(lines) and "year_gan_idx =" in lines[i+1]:
        # Close the broken _calculate_sinsal (which we want to replace anyway)
        # Actually, let's just insert the new method and get_gan_ji here
        
        # Remove the last appended line since it's part of the broken dict
        new_lines.pop()
        
        # Insert new _calculate_pillar_sinsal
        new_lines.append("""        }
        
    def _calculate_pillar_sinsal(self, gan, ji, pillar_type):
        sinsal_list = []
        if not hasattr(self, 'day_ji_char'): return []
        day_ji_char = self.day_ji_char 
        
        samhap_map = {
            '인': '화', '오': '화', '술': '화',
            '사': '금', '유': '금', '축': '금',
            '신': '수', '자': '수', '진': '수',
            '해': '목', '묘': '목', '미': '목'
        }
        
        # 1. 3 Sinsal
        group = samhap_map.get(day_ji_char)
        target = ji.split('(')[0]
        
        if group == '화':
            if target == '신': sinsal_list.append("역마살")
            elif target == '묘': sinsal_list.append("도화살")
            elif target == '술': sinsal_list.append("화개살")
        elif group == '금':
            if target == '해': sinsal_list.append("역마살")
            elif target == '오': sinsal_list.append("도화살")
            elif target == '축': sinsal_list.append("화개살")
        elif group == '수':
            if target == '인': sinsal_list.append("역마살")
            elif target == '유': sinsal_list.append("도화살")
            elif target == '진': sinsal_list.append("화개살")
        elif group == '목':
            if target == '사': sinsal_list.append("역마살")
            elif target == '자': sinsal_list.append("도화살")
            elif target == '미': sinsal_list.append("화개살")

        # 2. Baekho (Expanded)
        baekho_pairs = ["갑진", "을미", "병술", "정축", "무진", "임술", "계축"]
        gan_char = gan.split('(')[0]
        ganji = gan_char + target
        if ganji in baekho_pairs: sinsal_list.append("백호대살")
            
        # 3. Goegang
        goegang_pairs = ["무진", "무술", "경진", "경술", "임진", "임술"]
        if ganji in goegang_pairs: sinsal_list.append("괴강살")
            
        # 4. Hyeonchim
        if gan_char in ['갑', '신'] or target in ['묘', '오', '신']: sinsal_list.append("현침살")
            
        # 5. Gwimun
        gwimun_map = {'자': '유', '축': '오', '인': '미', '묘': '신', '진': '해', '사': '술',
                      '유': '자', '오': '축', '미': '인', '신': '묘', '해': '진', '술': '사'}
        if gwimun_map.get(day_ji_char) == target: sinsal_list.append("귀문관살")
            
        # 6. Cheoneul
        day_gan_char = getattr(self, 'day_gan_char', '')
        cheoneul_map = {
            '갑': ['축', '미'], '무': ['축', '미'], '경': ['축', '미'],
            '을': ['자', '신'], '기': ['자', '신'],
            '병': ['해', '유'], '정': ['해', '유'],
            '신': ['인', '오'],
            '임': ['사', '묘'], '계': ['사', '묘']
        }
        if target in cheoneul_map.get(day_gan_char, []): sinsal_list.append("천을귀인")

        # 7. Geumyeo
        geumyeo_map = {
            '갑': '진', '을': '사', '병': '미', '정': '신', '무': '미',
            '기': '신', '경': '술', '신': '해', '임': '축', '계': '인'
        }
        if geumyeo_map.get(day_gan_char) == target: sinsal_list.append("금여성")

        return list(set(sinsal_list))

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
\n""")

with open(target_file, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("Repaired saju_app.py")
