import os

target_file = "../program1-calculator/saju_app.py"

with open(target_file, "r", encoding="utf-8") as f:
    content = f.read()

# Logic to parse pillars inside _calculate_saju_strength correctly
old_parsing = """        def get_elem(char, is_gan):
            if is_gan: return CHEONGAN_INFO.get(char, {}).get('element')
            else: return JIJI_YONG.get(char, {}).get('element')
            
        # Iterate pillars to score
        # Year
        y_g_e = get_elem(pillars['year']['gan'].split('(')[0], True)
        y_j_e = get_elem(pillars['year']['ji'].split('(')[0], False)"""

new_parsing = """        import re
        def get_elem(char, is_gan):
            if is_gan: return CHEONGAN_INFO.get(char, {}).get('element')
            else: return JIJI_YONG.get(char, {}).get('element')
            
        def extract(p):
            # p ex: 갑(甲)자(子)
            parts = re.findall(r'.\(.\)', p)
            if len(parts) == 2: return parts[0].split('(')[0], parts[1].split('(')[0]
            # fallback
            if len(p) >= 2: return p[0], p[1]
            return "", ""
            
        y_g, y_j = extract(pillars['year'])
        m_g, m_j = extract(pillars['month'])
        d_g, d_j = extract(pillars['day'])
        h_g, h_j = extract(pillars['hour'])
        
        # Iterate pillars to score
        # Year
        y_g_e = get_elem(y_g, True)
        y_j_e = get_elem(y_j, False)"""

# Also update the rest of variable usage
# m_g_e = get_elem(pillars['month']['gan']...) -> get_elem(m_g, True)

full_new_method_start = """    def _calculate_saju_strength(self, day_gan, pillars, ohaeng):
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
            else: return JIJI_YONG.get(char, {}).get('element')

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
"""

# Replace the method again
start_m = "    def _calculate_saju_strength(self, day_gan, pillars, ohaeng):"
end_m = "    def _calculate_yongsin(self, day_gan, pillars, ohaeng, score):"

# Find start
s_idx = content.find(start_m)
e_idx = content.find(end_m)

if s_idx != -1 and e_idx != -1:
    content = content[:s_idx] + full_new_method_start + "\n" + content[e_idx:]

with open(target_file, "w", encoding="utf-8") as f:
    f.write(content)

print("Fixed Strength logic parsing.")
