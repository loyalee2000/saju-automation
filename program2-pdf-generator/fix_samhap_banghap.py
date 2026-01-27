import os

target_file = "../program1-calculator/saju_app.py"

with open(target_file, "r", encoding="utf-8") as f:
    content = f.read()

# We need to add Samhap, Banghap detection to _analyze_interactions
# And mark Gongmang pillars in get_result_json

# Find _analyze_interactions and replace it
start_marker = "    def _analyze_interactions(self):"
end_marker = "\n    def get_result_json(self):"

start_idx = content.find(start_marker)
end_idx = content.find(end_marker, start_idx)

if start_idx == -1:
    print("ERROR: Could not find _analyze_interactions")
    exit(1)

new_interactions_method = """    def _analyze_interactions(self):
        interactions = []
        gan_list = [self.year_gan_char, self.month_gan_char, self.day_gan_char, self.hour_gan_char]
        ji_list = [self.year_ji_char, self.month_ji_char, self.day_ji_char, self.hour_ji_char]
        labels = ["년", "월", "일", "시"]
        
        pairs = [(0,1), (0,2), (0,3), (1,2), (1,3), (2,3)]
        
        for i, j in pairs:
            if not gan_list[i] or not gan_list[j]: continue
            l1, l2 = labels[i], labels[j]
            pair_lbl = f"{l1}-{l2}"
            
            # Cheongan Chung
            c_chung = self._calculate_cheongan_chung(gan_list[i], gan_list[j])
            if c_chung: interactions.append(f"천간충({pair_lbl}): {gan_list[i]}{gan_list[j]}충 ({c_chung})")
            
            # Cheongan Hap
            c_hap = self._calculate_cheongan_hap(gan_list[i], gan_list[j])
            if c_hap: interactions.append(f"천간합({pair_lbl}): {gan_list[i]}{gan_list[j]}합 ({c_hap})")
            
            j1, j2 = ji_list[i], ji_list[j]
            if not j1 or not j2: continue
            
            # Jiji Chung
            j_chung = self._calculate_jiji_chung(j1, j2)
            if j_chung: interactions.append(f"지지충({pair_lbl}): {j1}{j2}충 ({j_chung})")
            
            # Jiji Yukhap
            j_yukhap = self._calculate_jiji_yukhap(j1, j2)
            if j_yukhap: interactions.append(f"지지육합({pair_lbl}): {j1}{j2}합 ({j_yukhap})")
            
            # Wonjin
            wonjin = self._calculate_wonjin(j1, j2)
            if wonjin: interactions.append(f"원진({pair_lbl}): {j1}{j2}원진 (애증)")
            
            # Hyeong
            hyeong = self._calculate_hyeong(j1, j2)
            if hyeong: interactions.append(f"형({pair_lbl}): {j1}{j2}형 ({hyeong})")
            
            # Pa
            pa = self._calculate_pa(j1, j2)
            if pa: interactions.append(f"파({pair_lbl}): {j1}{j2}파 (파괴)")
            
            # Hae
            hae = self._calculate_hae(j1, j2)
            if hae: interactions.append(f"해({pair_lbl}): {j1}{j2}해 (해로움)")

        # === SAMHAP (삼합) Check ===
        # 삼합 groups: 인오술(火), 사유축(金), 신자진(水), 해묘미(木)
        samhap_groups = {
            '인오술': ['인', '오', '술'],
            '사유축': ['사', '유', '축'],
            '신자진': ['신', '자', '진'],
            '해묘미': ['해', '묘', '미']
        }
        
        valid_ji = [j for j in ji_list if j]
        
        for name, members in samhap_groups.items():
            matched = [j for j in valid_ji if j in members]
            matched_positions = []
            for idx, j in enumerate(ji_list):
                if j in members:
                    matched_positions.append(labels[idx])
            
            if len(matched) >= 3:
                interactions.append(f"지지삼합({'-'.join(matched_positions)}): {name} (완전삼합)")
            elif len(matched) == 2:
                interactions.append(f"지지삼합(반합)({'-'.join(matched_positions)}): {''.join(matched)}반합 ({name} 중 2자)")

        # === BANGHAP (방합/계절합) Check ===
        # 방합 groups: 인묘진(春木), 사오미(夏火), 신유술(秋金), 해자축(冬水)
        banghap_groups = {
            '인묘진': ['인', '묘', '진'],
            '사오미': ['사', '오', '미'],
            '신유술': ['신', '유', '술'],
            '해자축': ['해', '자', '축']
        }
        
        for name, members in banghap_groups.items():
            matched = [j for j in valid_ji if j in members]
            matched_positions = []
            for idx, j in enumerate(ji_list):
                if j in members:
                    matched_positions.append(labels[idx])
            
            if len(matched) >= 3:
                interactions.append(f"지지방합({'-'.join(matched_positions)}): {name} (완전방합)")
            elif len(matched) == 2:
                interactions.append(f"지지방합(반합)({'-'.join(matched_positions)}): {''.join(matched)}반합 ({name} 중 2자)")
        
        return interactions

    def _check_gongmang_pillars(self, gongmang_list, ji_list, labels):
        \"\"\"Check which pillars have Ji in Gongmang\"\"\"
        result = {}
        for idx, j in enumerate(ji_list):
            if not j: continue
            # Extract char from "오(午)" format
            j_char = j.split('(')[0] if '(' in j else j
            
            is_gongmang = False
            for gm in gongmang_list:
                gm_char = gm.split('(')[0] if '(' in gm else gm
                if j_char == gm_char:
                    is_gongmang = True
                    break
            
            result[labels[idx]] = is_gongmang
        return result

"""

content = content[:start_idx] + new_interactions_method + content[end_idx:]
print("Added Samhap, Banghap detection to _analyze_interactions")


# Now we need to update get_result_json to include gongmang_pillars
# Find where gongmang is assigned and add gongmang_pillars after it

gongmang_marker = '"gongmang": gongmang,'
gongmang_idx = content.find(gongmang_marker)

if gongmang_idx != -1:
    # Insert gongmang_pillars calculation before this line
    # First, find where we can add the calculation
    
    # Replace the gongmang line to include gongmang_pillars
    old_gongmang_section = '"gongmang": gongmang,'
    new_gongmang_section = '''"gongmang": gongmang,
            "gongmang_pillars": self._check_gongmang_pillars(
                gongmang.split(", ") if isinstance(gongmang, str) else gongmang,
                [pillars_data['year'], pillars_data['month'], pillars_data['day'], pillars_data['hour']],
                ["year", "month", "day", "hour"]
            ),'''
    
    content = content.replace(old_gongmang_section, new_gongmang_section, 1)
    print("Added gongmang_pillars to JSON output")
else:
    print("WARNING: Could not find gongmang in JSON output")


with open(target_file, "w", encoding="utf-8") as f:
    f.write(content)

print("\nFixes applied. Restart the app to test.")
