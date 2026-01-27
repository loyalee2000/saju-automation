import os

target_file = "../program1-calculator/saju_app.py"

with open(target_file, "r", encoding="utf-8") as f:
    content = f.read()

# Replacement again.

new_method = """    def get_result_json(self):
        # 1) Calculate basic pillars
        pillars_data = self.get_gan_ji()
        
        # Ohaeng
        ohaeng_cnt = self.analyze_ohaeng(pillars_data)
        
        # Extract Chars
        def extract_char(text, idx):
            if not text or len(text) <= idx: return ""
            return text[idx]
            
        self.year_gan_char = extract_char(pillars_data['year'], 0)
        self.year_ji_char = extract_char(pillars_data['year'], 4)
        self.month_gan_char = extract_char(pillars_data['month'], 0)
        self.month_ji_char = extract_char(pillars_data['month'], 4)
        self.day_gan_char = extract_char(pillars_data['day'], 0)
        self.day_ji_char = extract_char(pillars_data['day'], 4)
        
        if "모름" in pillars_data['hour'] or "Unknown" in pillars_data['hour']:
             self.hour_gan_char = ""
             self.hour_ji_char = ""
        else:
             self.hour_gan_char = extract_char(pillars_data['hour'], 0)
             self.hour_ji_char = extract_char(pillars_data['hour'], 4)
        
        saja_gan = [self.year_gan_char, self.month_gan_char, self.day_gan_char, self.hour_gan_char]
        saja_ji = [self.year_ji_char, self.month_ji_char, self.day_ji_char, self.hour_ji_char]
        
        # Pillars List for Strength/Yongsin
        pillars_list = [
            {'gan': self.year_gan_char, 'ji': self.year_ji_char},
            {'gan': self.month_gan_char, 'ji': self.month_ji_char},
            {'gan': self.day_gan_char, 'ji': self.day_ji_char},
            {'gan': self.hour_gan_char, 'ji': self.hour_ji_char}
        ]

        # Daewoon
        daewoon_result = self.get_daewoon(pillars_data['year_gan_idx'], pillars_data['month_gan_idx'], pillars_data['month_ji_idx'])
        
        # Gyeokguk
        gyeokguk = self._calculate_gyeokguk(self.day_gan_char, self.month_ji_char, saja_gan)
        
        # Gongmang
        gongmang_list = self._calculate_gongmang(self.day_gan_char, self.day_ji_char) 
        # _calculate_gongmang returns a list or string? 
        # Original: return [ji1, ji2] or similar.
        # User output expected: String or List. Let's assume list and join.
        if isinstance(gongmang_list, list):
             gongmang = ", ".join(gongmang_list)
        else:
             gongmang = gongmang_list
        
        # Strength (Requires list of pillars)
        strength_res = self._calculate_saju_strength(self.day_gan_char, pillars_list, ohaeng_cnt)
        
        # Yongsin (Requires strength score)
        score = strength_res.get('score', 0)
        yongsin = self._calculate_yongsin(self.day_gan_char, pillars_list, ohaeng_cnt, score)
        
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
            if p_name == "hour" and not self.hour_gan_char:
                continue
            s_gan = self._calculate_pillar_sinsal(saja_gan[idx], saja_ji[idx], "gan")
            s_ji = self._calculate_pillar_sinsal(saja_gan[idx], saja_ji[idx], "ji")
            sinsal_data[p_name]["gan"] = s_gan
            sinsal_data[p_name]["ji"] = s_ji

        # Health
        health_res = self._analyze_health_risks(ohaeng_cnt)
        
        # Sibseong (Check args)
        # _calculate_sibseong usually takes day_gan and loops internally or returns dict
        # Line 207: def _calculate_sibseong(self, day_stem, target, is_stem=True):
        # But previously we called self._calculate_sibseong(). 
        # If there is a wrapper method with 0 args, great. If not, I need to implement the loop.
        # saju_app definition of `_calculate_sibseong` seems to take args.
        # I probably need to loop here or find the wrapper.
        # Looking at previous version, there WAS a `_calculate_sibseong` wrapper?
        # Or I must implement it:
        
        sibseong_data = {}
        # Keys: year_gan, year_ji, month_gan...
        for p_name, idx in pillars_map:
            g = saja_gan[idx]
            j = saja_ji[idx]
            if g:
                if idx == 2: # Day Gan
                   sibseong_data[f"{p_name}_gan"] = "비견" # Self
                else:
                   sibseong_data[f"{p_name}_gan"] = self._calculate_sibseong(self.day_gan_char, g, True)
            
            if j:
                sibseong_data[f"{p_name}_ji"] = self._calculate_sibseong(self.day_gan_char, j, False)

        # Interactions
        # _analyze_interactions() also might not exist if I removed it?
        # I need to check if there is a method `_analyze_interactions`.
        # If not, I must implement interaction detection logic here or call helpers.
        # Original code had `_analyze_interactions`?
        # List printed: 1109:    def _analyze_interactions(self):
        # So it exists.
        interactions_list = self._analyze_interactions()
        
        # --- RICH DATA ---
        
        # 1. Four Pillars Rich
        four_pillars_rich = {}
        for p_name, idx in pillars_map:
            g_char = saja_gan[idx] 
            j_char = saja_ji[idx]
            
            if not g_char: 
                four_pillars_rich[p_name] = {
                    "gan": "", "ji": "", "text": "시간 모름", 
                    "gan_desc": {}, "ji_desc": {}, "pillar_desc": {}
                }
                continue
            
            g_desc = CHEONGAN_DESC.get(g_char, {})
            j_desc = JIJI_DESC.get(j_char, {})
            summary = f"{g_desc.get('nature', '')} 위의 {j_desc.get('animal', '')}"
            detail = f"{g_char}({g_desc.get('nature', '')})의 기운과 {j_char}({j_desc.get('animal', '')})의 기운이 결합된 형태입니다."
            
            full_text = pillars_data[p_name]
            gan_full = full_text[:4] if len(full_text) >= 4 else g_char
            ji_full = full_text[4:] if len(full_text) >= 8 else j_char
            
            four_pillars_rich[p_name] = {
                "gan": gan_full,
                "ji": ji_full,
                "text": full_text,
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
        for p_name, idx in pillars_map:
            j_char = saja_ji[idx]
            if not j_char: continue
            stage = self._calculate_12unseong(self.day_gan_char, j_char)
            # Lookup desc in TWELVE_UNSEONG_DESC_MAP
            desc = TWELVE_UNSEONG_DESC_MAP.get(stage, {})
            twelve_unseong_res[p_name] = {
                "stage": stage,
                "desc": desc
            }
        
        # 4. Sinsal Details
        sinsal_det = {}
        all_sinsals = set()
        for p in sinsal_data.values():
            all_sinsals.update(p['gan'])
            all_sinsals.update(p['ji'])
        
        for s in all_sinsals:
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
            
        # 6. Reference Data
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
            "birth_minute": self.adjusted_dt.minute,
             "summer_time_applied": getattr(self, 'summer_time_applied', False), # Safe access
             "longitude_correction": getattr(self, 'longitude_correction_minute', "N/A")
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
start_idx = content.find(start_marker)

if start_idx != -1:
    next_func_idx = content.find("\n    def ", start_idx + 100)
    
    if next_func_idx != -1:
        new_content = content[:start_idx] + new_method + content[next_func_idx:]
    else:
        new_content = content[:start_idx] + new_method
        
    with open(target_file, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("Fixed get_result_json logic V3.")
else:
    print("Could not find get_result_json.")
