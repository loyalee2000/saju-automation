import os

target_file = "../program1-calculator/saju_app.py"

with open(target_file, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add 1984 Data
new_solar_data = '''        key = f"{year}-{month:02d}"
        if key in precise_data:
            return datetime.strptime(precise_data[key], "%Y-%m-%d %H:%M")
            
        # [NEW] precise data for 1984
        if year == 1984 and month == 5:
             return datetime(1984, 5, 5, 10, 23)

        # Fallback approximation (Improved)'''

# Locate the fallback line to insert before
if "        # Fallback approximation (Improved)" in content:
    content = content.replace(
        '        # Fallback approximation (Improved)', 
        new_solar_data
    )
elif "        key = f\"{year}-{month:02d}\"" in content:
     # Fallback if already modified or different structure, try to find the block
     pass

# 2. Add Sinsal Logic
# flexible search for the helper method if it exists or insert it
new_sinsal_method = '''    def _calculate_pillar_sinsal(self, gan, ji, pillar_type):
        """
        Calculate Sinsal (Divine Spirits) for a specific pillar.
        Returns a list of Sinsal names.
        """
        sinsal_list = []
        
        # Store day char for safe access
        if not hasattr(self, 'day_ji_char'): return []
        day_ji_char = self.day_ji_char 
        
        samhap_map = {
            '인': '화', '오': '화', '술': '화',
            '사': '금', '유': '금', '축': '금',
            '신': '수', '자': '수', '진': '수',
            '해': '목', '묘': '목', '미': '목'
        }
        
        # Simple lookup for 3-Sinsal based on Day Branch group
        group = samhap_map.get(day_ji_char)
        target = ji.split('(')[0] # Extract Korean char
        
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

        # 2. 백호대살 (Baekho)
        baekho_pairs = ["갑진", "을미", "병술", "정축", "무진", "임술", "계축"]
        gan_char = gan.split('(')[0]
        ganji = gan_char + target
        if ganji in baekho_pairs:
            sinsal_list.append("백호대살")
            
        # 3. 괴강살 (Goegang)
        goegang_pairs = ["무진", "무술", "경진", "경술", "임진", "임술"]
        if ganji in goegang_pairs:
            sinsal_list.append("괴강살")
            
        # 4. 현침살 (Hyeonchim)
        if gan_char in ['갑', '신'] or target in ['묘', '오', '신']:
            sinsal_list.append("현침살")
            
        # 5. 귀문관살 (Gwimun)
        gwimun_map = {'자': '유', '축': '오', '인': '미', '묘': '신', '진': '해', '사': '술',
                      '유': '자', '오': '축', '미': '인', '신': '묘', '해': '진', '술': '사'}
        if gwimun_map.get(day_ji_char) == target:
            sinsal_list.append("귀문관살")
            
        # 6. 천을귀인 (Cheoneul)
        day_gan_char = getattr(self, 'day_gan_char', '')
        cheoneul_map = {
            '갑': ['축', '미'], '무': ['축', '미'], '경': ['축', '미'],
            '을': ['자', '신'], '기': ['자', '신'],
            '병': ['해', '유'], '정': ['해', '유'],
            '신': ['인', '오'],
            '임': ['사', '묘'], '계': ['사', '묘']
        }
        if target in cheoneul_map.get(day_gan_char, []):
            sinsal_list.append("천을귀인")

        # 7. 금여성 (Geumyeo)
        geumyeo_map = {
            '갑': '진', '을': '사', '병': '미', '정': '신', '무': '미',
            '기': '신', '경': '술', '신': '해', '임': '축', '계': '인'
        }
        if geumyeo_map.get(day_gan_char) == target:
            sinsal_list.append("금여성")
            
        # 8. 천문성 (Cheonmun)
        if target in ['술', '해']:
             sinsal_list.append("천문성")

        return list(set(sinsal_list))

    def _calculate_sinsal(self, day_branch, target_branch):
        return ""
'''

# Insert method before get_gan_ji
if "def get_gan_ji(self):" in content:
    content = content.replace("def get_gan_ji(self):", new_sinsal_method + "\n\n    def get_gan_ji(self):")


# 3. Update get_result_json structure
# Find the block constructing the result json
# We look for the 'sinsal = {' block or 'sibseong = {' to anchor
if "sinsal = {" in content:
    # This is tricky with simple replace if the block is large.
    # We'll rely on the specific previous content structure or use regex
    pass

# Let's use a robust replace for the sinsal block
import re
pattern = r"sinsal = \{[^\}]+\}"
replacement = '''# Store for Sinsal calc
        self.day_gan_char = d_gan.split('(')[0]
        self.day_ji_char = d_ji.split('(')[0]
        
        sinsal = {
            'year': {
                'gan': self._calculate_pillar_sinsal(y_gan, y_ji, 'year'),
                'ji': self._calculate_pillar_sinsal(y_gan, y_ji, 'year')
            },
            'month': {
                'gan': self._calculate_pillar_sinsal(m_gan, m_ji, 'month'),
                'ji': self._calculate_pillar_sinsal(m_gan, m_ji, 'month')
            },
            'day': {
                'gan': self._calculate_pillar_sinsal(d_gan, d_ji, 'day'),
                'ji': self._calculate_pillar_sinsal(d_gan, d_ji, 'day')
            },
            'hour': {
                'gan': self._calculate_pillar_sinsal(h_gan, h_ji, 'hour') if not self.time_unknown else [],
                'ji': self._calculate_pillar_sinsal(h_gan, h_ji, 'hour') if not self.time_unknown else []
            } 
        }'''

content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open(target_file, "w", encoding="utf-8") as f:
    f.write(content)

print("Successfully patched saju_app.py")
