import os

target_file = "../program1-calculator/saju_app.py"

with open(target_file, "r", encoding="utf-8") as f:
    content = f.read()

# V6 Replacement

new_method = """    def get_result_json(self):
        # 1) Calculate basic pillars
        pillars_data = self.get_gan_ji()
        
        # Ohaeng (Expects dict of Full Strings)
        ohaeng_cnt = self.analyze_ohaeng(pillars_data)
        
        def split_pillar(p_text):
            if not p_text or "Unknown" in p_text or "모름" in p_text: 
                return "", "", "", ""
            idx1 = p_text.find(')')
            if idx1 == -1: return "", "", "", ""
            
            g_full = p_text[:idx1+1]
            j_full = p_text[idx1+1:]
            
            g_char = g_full.split('(')[0]
            j_char = j_full.split('(')[0]
            
            return g_full, j_full, g_char, j_char

        # Parse all pillars
        y_gf, y_jf, y_gc, y_jc = split_pillar(pillars_data['year'])
        m_gf, m_jf, m_gc, m_jc = split_pillar(pillars_data['month'])
        d_gf, d_jf, d_gc, d_jc = split_pillar(pillars_data['day'])
        h_gf, h_jf, h_gc, h_jc = split_pillar(pillars_data['hour'])
        
        self.year_gan_char = y_gc
        self.year_ji_char = y_jc
        self.month_gan_char = m_gc
        self.month_ji_char = m_jc
        self.day_gan_char = d_gc
        self.day_ji_char = d_jc
        self.hour_gan_char = h_gc
        self.hour_ji_char = h_jc
        
        saja_gan_char = [y_gc, m_gc, d_gc, h_gc]
        saja_ji_char = [y_jc, m_jc, d_jc, h_jc]
        
        saja_gan_full = [y_gf, m_gf, d_gf, h_gf]
        saja_ji_full = [y_jf, m_jf, d_jf, h_jf]
        
        daewoon_result = self.get_daewoon(pillars_data['year_gan_idx'], pillars_data['month_gan_idx'], pillars_data['month_ji_idx'])
        
        gyeokguk = self._calculate_gyeokguk(d_gc, m_jc, saja_gan_char)
        
        if d_gf and d_jf:
             gongmang_list = self._calculate_gongmang(d_gf, d_jf)
             if isinstance(gongmang_list, list):
                 gongmang = ", ".join(gongmang_list)
             else:
                 gongmang = gongmang_list
        else:
             gongmang = "해당 없음"
        
        strength_res = self._calculate_saju_strength(d_gc, pillars_data, ohaeng_cnt)
        
        score = strength_res.get('score', 0)
        yongsin = self._calculate_yongsin(d_gc, pillars_data, ohaeng_cnt, score)
        
        luck_cycle = self._calculate_luck_cycle()
        
        # Sinsal (Fixing dict assignment)
        sinsal_data = {
            "year": {"gan": [], "ji": []},
            "month": {"gan": [], "ji": []},
            "day": {"gan": [], "ji": []},
            "hour": {"gan": [], "ji": []}
        }
        pillars_map = [("year", 0), ("month", 1), ("day", 2), ("hour", 3)]
        for p_name, idx in pillars_map:
            if p_name == "hour" and not h_gc: continue
            
            # _calculate_pillar_sinsal returns {'gan': [], 'ji': []}
            s_res = self._calculate_pillar_sinsal(saja_gan_char[idx], saja_ji_char[idx], "both")
            
            sinsal_data[p_name]["gan"] = s_res.get('gan', [])
            sinsal_data[p_name]["ji"] = s_res.get('ji', [])

        health_res = self._analyze_health_risks(ohaeng_cnt)
        
        sibseong_data = {}
        for p_name, idx in pillars_map:
            if idx == 2: 
                sibseong_data[f"{p_name}_gan"] = "비견"
            else:
                 if saja_gan_char[idx]:
                    sibseong_data[f"{p_name}_gan"] = self._calculate_sibseong(d_gc, saja_gan_char[idx], True)
            
            if saja_ji_char[idx]:
                 sibseong_data[f"{p_name}_ji"] = self._calculate_sibseong(d_gc, saja_ji_char[idx], False)

        interactions_list = self._analyze_interactions()

        four_pillars_rich = {}
        for p_name, idx in pillars_map:
            g_full = saja_gan_full[idx] or ""
            j_full = saja_ji_full[idx] or ""
            g_char = saja_gan_char[idx] or ""
            j_char = saja_ji_char[idx] or ""
            
            if not g_char: 
                four_pillars_rich[p_name] = {
                    "gan": "", "ji": "", "text": "시간 모름", 
                    "gan_desc": {}, "ji_desc": {}, "pillar_desc": {}
                }
                continue
            
            g_desc = CHEONGAN_DESC.get(g_full, {})
            j_desc = JIJI_DESC.get(j_full, {})
            
            if not g_desc and g_char:
                 for k in CHEONGAN_DESC:
                     if k.startswith(g_char): g_desc = CHEONGAN_DESC[k]; break
            if not j_desc and j_char:
                 for k in JIJI_DESC:
                     if k.startswith(j_char): j_desc = JIJI_DESC[k]; break
            
            g_nature = g_desc.get('nature', '')
            j_animal = j_desc.get('animal', '')
            summary = f"{g_nature} 위의 {j_animal}"
            detail = f"{g_char}({g_nature})의 기운과 {j_char}({j_animal})의 기운이 결합된 형태입니다."
            
            four_pillars_rich[p_name] = {
                "gan": g_full,
                "ji": j_full,
                "text": pillars_data[p_name],
                "gan_desc": g_desc,
                "ji_desc": j_desc,
                "pillar_desc": {"summary": summary, "detail": detail}
            }

        sib_details = {}
        for k, v in sibseong_data.items():
            if v in SIBSEONG_DETAILS:
                sib_details[k] = SIBSEONG_DETAILS[v]
            else:
                sib_details[k] = {"name": v, "desc": {}}

        twelve_unseong_res = {}
        for p_name, idx in pillars_map:
            j_c = saja_ji_char[idx]
            if not j_c: continue
            stage = self._calculate_12unseong(d_gc, j_c)
            desc = TWELVE_UNSEONG_DESC_MAP.get(stage, {})
            twelve_unseong_res[p_name] = {
                "stage": stage,
                "desc": desc
            }
        
        sinsal_det = {}
        all_sinsals = set()
        for p in sinsal_data.values():
            all_sinsals.update(p['gan'])
            all_sinsals.update(p['ji'])
        
        for s in all_sinsals:
            key = s
            if s not in SINSAL_DETAILS:
                if s.endswith("살"): key = s[:-1]
                elif s + "살" in SINSAL_DETAILS: key = s + "살"
            
            if key in SINSAL_DETAILS:
                sinsal_det[s] = SINSAL_DETAILS[key]

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
             "summer_time_applied": getattr(self, 'summer_time_applied', False), 
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
    print("Fixed get_result_json logic V6.")
else:
    print("Could not find get_result_json.")
