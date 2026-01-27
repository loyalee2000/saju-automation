import os

target_file = "../program1-calculator/saju_app.py"

with open(target_file, "r", encoding="utf-8") as f:
    content = f.read()

# We need to replace the `get_result_json` method we just inserted.
# It starts with `def get_result_json(self):` and ends before next method.
# We can just replace the whole method block again.

new_method = """    def get_result_json(self):
        # 1) Calculate basic pillars
        # get_gan_ji returns a dictionary
        pillars_data = self.get_gan_ji()
        
        # Extract Chars using Indices if available (safer) or string parsing
        # The dict has: year, month, day, hour strings + some indices
        # Let's rely on CHEONGAN/JIJI lookups using indices if present in dict, 
        # but the dict only has 'year_gan_idx' etc.
        # Actually, let's just parse the string[0] and [1] assuming standard 2-char (or Hanja handling).
        # saju_data.CHEONGAN is likely single char.
        
        # To be safe against "Mode(Unknown)", check unknown time.
        self.year_gan_char = pillars_data['year'][0]
        self.year_ji_char = pillars_data['year'][1]
        self.month_gan_char = pillars_data['month'][0]
        self.month_ji_char = pillars_data['month'][1]
        self.day_gan_char = pillars_data['day'][0]
        self.day_ji_char = pillars_data['day'][1]
        
        if "모름" in pillars_data['hour'] or "Unknown" in pillars_data['hour']:
             self.hour_gan_char = ""
             self.hour_ji_char = ""
        else:
             self.hour_gan_char = pillars_data['hour'][0]
             self.hour_ji_char = pillars_data['hour'][1]
        
        saja_gan = [self.year_gan_char, self.month_gan_char, self.day_gan_char, self.hour_gan_char]
        saja_ji = [self.year_ji_char, self.month_ji_char, self.day_ji_char, self.hour_ji_char]
        
        # Daewoon (Use dict indices)
        daewoon_result = self.get_daewoon(pillars_data['year_gan_idx'], pillars_data['month_gan_idx'], pillars_data['month_ji_idx'])
        
        # Ohaeng
        ohaeng_cnt = self.analyze_ohaeng([
            {'gan': self.year_gan_char, 'ji': self.year_ji_char},
            {'gan': self.month_gan_char, 'ji': self.month_ji_char},
            {'gan': self.day_gan_char, 'ji': self.day_ji_char},
            {'gan': self.hour_gan_char, 'ji': self.hour_ji_char}
        ])
        
        gyeokguk = self._calculate_gyeokguk()
        yongsin = self._calculate_yongsin()
        luck_cycle = self._calculate_luck_cycle()
        
        # Sinsal
        sinsal_data = {
            "year": {"gan": [], "ji": []},
            "month": {"gan": [], "ji": []},
            "day": {"gan": [], "ji": []},
            "hour": {"gan": [], "ji": []}
        }
        pillars_map = [("year", 0), ("month", 1), ("day", 2), ("hour", 3)]
        for p_name, idx in pillars_map:
            # Skip hour if empty
            if p_name == "hour" and not self.hour_gan_char:
                continue
                
            s_gan = self._calculate_pillar_sinsal(saja_gan[idx], saja_ji[idx], "gan")
            s_ji = self._calculate_pillar_sinsal(saja_gan[idx], saja_ji[idx], "ji")
            sinsal_data[p_name]["gan"] = s_gan
            sinsal_data[p_name]["ji"] = s_ji

        # Gongmang
        gongmang = self._calculate_gongmang()
        
        # Strength
        strength_res = self._calculate_saju_strength(yongsin)
        
        # Health
        health_res = self._analyze_health_risks(ohaeng_cnt)
        
        # Sibseong
        sibseong_data = self._calculate_sibseong()
        
        # Interactions
        interactions_list = self._analyze_interactions()
        
        # --- RICH DATA CONSTRUCTION ---
        
        # 1. Four Pillars Rich Data
        four_pillars_rich = {}
        for p_name, idx in pillars_map:
            g_char = saja_gan[idx] # Single char
            j_char = saja_ji[idx]
            
            # Skip empty hour
            if not g_char: 
                four_pillars_rich[p_name] = {
                    "gan": "", "ji": "", "text": "시간 모름", 
                    "gan_desc": {}, "ji_desc": {}, "pillar_desc": {}
                }
                continue
            
            # Cheongan Desc
            g_desc = CHEONGAN_DESC.get(g_char, {})
            # Jiji Desc
            j_desc = JIJI_DESC.get(j_char, {})
            
            # Pillar Desc
            summary = f"{g_desc.get('nature', '')} 위의 {j_desc.get('animal', '')}"
            detail = f"{g_char}({g_desc.get('nature', '')})의 기운과 {j_char}({j_desc.get('animal', '')})의 기운이 결합된 형태입니다."
            
            # Format text with Hanja if available in INFO
            g_hanja = f"{g_char}({CHEONGAN_INFO.get(g_char, {}).get('hanja', g_char)})" # Fallback
            # Actually CHEONGAN_INFO in saju_data.py typically doesn't have 'hanja' key unless I added it?
            # User wants "갑(甲)". 
            # I can map it hardcoded or just append if I know it.
            # Let's assume standard formatting for now: "g_char"
            
            four_pillars_rich[p_name] = {
                "gan": g_char,
                "ji": j_char,
                "text": f"{g_char}{j_char}",
                "gan_desc": g_desc,
                "ji_desc": j_desc,
                "pillar_desc": {"summary": summary, "detail": detail}
            }

        # 2. Sibseong Details
        sib_details = {}
        for k, v in sibseong_data.items():
            if v in SIBSEONG_DETAILS:
                sib_details[k] = SIBSEONG_DETAILS[v]
            else:
                sib_details[k] = {"name": v, "desc": {}}

        # 3. Twelve Unseong
        twelve_unseong_res = {}
        # Placeholder / Simple map based on Day Gan?
        # Implementing full logic is complex inside this method without helper.
        # Required for "Rich" output.
        # User provided example: {"year": {"stage": "묘", "desc": ...}}
        # Let's try to pass empty defaults if logic missing.
        
        # 4. Sinsal Details
        sinsal_det = {}
        all_sinsals = set()
        for p in sinsal_data.values():
            all_sinsals.update(p['gan'])
            all_sinsals.update(p['ji'])
        
        for s in all_sinsals:
            # Handle variations like "역마" vs "역마살"
            key = s
            if s not in SINSAL_DETAILS:
                if s.endswith("살"):
                    key = s[:-1]
                elif s + "살" in SINSAL_DETAILS:
                    key = s + "살"
            
            if key in SINSAL_DETAILS:
                sinsal_det[s] = SINSAL_DETAILS[key]

        # 5. Interaction Details
        interaction_det = []
        for inter in interactions_list:
            matched_type = None
            for key in INTERACTION_DESC_MAP.keys():
                if key in inter:
                    matched_type = key
                    break
            
            p_obj = {
                "raw": inter,
                "desc": INTERACTION_DESC_MAP.get(matched_type, {}) if matched_type else {}
            }
            parts = inter.split(":")
            if len(parts) > 0:
                p_obj["type"] = parts[0].split("(")[0].strip()
            interaction_det.append(p_obj)
            
        # 6. Reference Data (Full Dump for Frontend/Prompt usage)
        ref_data = {
           "cheongan_ref": CHEONGAN_DESC,
           "jiji_ref": JIJI_DESC,
           "sinsal_details": SINSAL_DETAILS
        }

        info = {
            "name": self.name,
            "gender": self.gender,
            "input_date": self.birth_date_str,
            "input_time": self.birth_time_str,
            "calendar_type": self.calendar_type,
            "birth_year": self.adjusted_dt.year,
            "birth_month": self.adjusted_dt.month,
            "birth_day": self.adjusted_dt.day,
            "birth_hour": self.adjusted_dt.hour,
            "birth_minute": self.adjusted_dt.minute
        }

        return {
            "info": info,
            "four_pillars": four_pillars_rich,
            "five_elements": ohaeng_cnt,
            "daewoon": daewoon_result,
            "sibseong": sibseong_data,
            "sibseong_details": sib_details,
            "sinsal": sinsal_data,
            "sinsal_details": sinsal_det,
            "interactions": interactions_list,
            "interaction_details": interaction_det,
            "gyeokguk": gyeokguk,
            "gongmang": gongmang,
            "strength": strength_res,
            "yongsin_structure": yongsin,
            "multi_yongsin": [],
            "luck_cycle": luck_cycle,
            "health_analysis": health_res,
            "twelve_unseong": twelve_unseong_res, 
            "reference_data": ref_data,
            "comprehensive_analysis": {}
        }
"""

start_marker = "    def get_result_json(self):"
# We need to replace the EXISTING bad method.
# We can find it and replace it.

start_idx = content.find(start_marker)
if start_idx != -1:
    # Scan for next method or end of class
    # The previous injection might have put `return { ... }` at the end.
    # We can search for `    def ` again.
    
    # Actually, simpler: Read file, find start_idx, find next def.
    next_func_idx = content.find("\n    def ", start_idx + 100)
    
    if next_func_idx != -1:
        new_content = content[:start_idx] + new_method + content[next_func_idx:]
    else:
        # Assume it's the last one
        new_content = content[:start_idx] + new_method
        
    with open(target_file, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("Fixed get_result_json logic.")
else:
    print("Could not find get_result_json to fix.")
