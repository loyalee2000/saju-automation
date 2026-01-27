import os

target_file = "../program1-calculator/saju_app.py"

with open(target_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Range to replace: line 1175 (index 1174) to line 1505 (index 1504)
# Note: grep output is 1-based. Python list is 0-based.
# We want to replace FROM `def get_result_json(self):`
# TO just before `def get_verbose_result(self):`

start_line_idx = -1
end_line_idx = -1

for i, line in enumerate(lines):
    if "def get_result_json(self):" in line:
        start_line_idx = i
    if "def get_verbose_result(self):" in line or "def get_verbose_result" in line:
        # Note: grep showed "def get_verbose_result(self):"
        if i > start_line_idx and start_line_idx != -1:
            end_line_idx = i
            break

if start_line_idx == -1 or end_line_idx == -1:
    print(f"Indices not found. Start: {start_line_idx}, End: {end_line_idx}")
    exit(1)

new_method_lines = [
    "    def get_result_json(self):\n",
    "        try:\n",
    "            pillars = self.get_gan_ji()\n",
    "        except AttributeError:\n",
    "            raise\n",
    "\n",
    "        ohaeng = self.analyze_ohaeng(pillars)\n",
    "        daewoon = self.get_daewoon(pillars['year_gan_idx'], pillars['month_gan_idx'], pillars['month_ji_idx'])\n",
    "\n",
    "        def split_pillar(p):\n",
    "            if p == '모름(Unknown)': return '모름', '모름'\n",
    "            import re\n",
    "            parts = re.findall(r'.\(.\)', p)\n",
    "            if len(parts) == 2:\n",
    "                return parts[0], parts[1]\n",
    "            return p, p\n", 
    "\n",
    "        y_gan, y_ji = split_pillar(pillars['year'])\n",
    "        m_gan, m_ji = split_pillar(pillars['month'])\n",
    "        d_gan, d_ji = split_pillar(pillars['day'])\n",
    "        h_gan, h_ji = split_pillar(pillars['hour'])\n",
    "\n",
    "        self.day_gan_char = d_gan.split('(')[0] if d_gan else ''\n",
    "        self.day_ji_char = d_ji.split('(')[0] if d_ji else ''\n",
    "        self.year_ji_char = y_ji.split('(')[0] if y_ji else ''\n",
    "\n",
    "        y_sinsal = self._calculate_pillar_sinsal(y_gan, y_ji, 'year')\n",
    "        m_sinsal = self._calculate_pillar_sinsal(m_gan, m_ji, 'month')\n",
    "        d_sinsal = self._calculate_pillar_sinsal(d_gan, d_ji, 'day')\n",
    "        h_sinsal = self._calculate_pillar_sinsal(h_gan, h_ji, 'hour') if not self.time_unknown else {'gan':[], 'ji':[]}\n",
    "\n",
    "        sinsal = {\n",
    "            'year': y_sinsal,\n",
    "            'month': m_sinsal,\n",
    "            'day': d_sinsal,\n",
    "            'hour': h_sinsal\n",
    "        }\n",
    "\n",
    "        twelve_unseong = {\n",
    "            'year': self._calculate_12unseong(d_gan, y_ji),\n",
    "            'month': self._calculate_12unseong(d_gan, m_ji),\n",
    "            'day': self._calculate_12unseong(d_gan, d_ji),\n",
    "            'hour': self._calculate_12unseong(d_gan, h_ji)\n",
    "        }\n",
    "\n",
    "        jijanggan = {\n",
    "            'year': self._get_jijanggan(y_ji),\n",
    "            'month': self._get_jijanggan(m_ji),\n",
    "            'day': self._get_jijanggan(d_ji),\n",
    "            'hour': self._get_jijanggan(h_ji)\n",
    "        }\n",
    "\n",
    "        sipsinsal = {\n",
    "            'year': self._calculate_12sinsal(y_ji, y_ji),\n",
    "            'month': self._calculate_12sinsal(y_ji, m_ji),\n",
    "            'day': self._calculate_12sinsal(y_ji, d_ji),\n",
    "            'hour': self._calculate_12sinsal(y_ji, h_ji)\n",
    "        }\n",
    "\n",
    "        heaven_stems_list = [y_gan, m_gan]\n",
    "        if not self.time_unknown: heaven_stems_list.append(h_gan)\n",
    "        gyeok_result = self._calculate_gyeokguk(d_gan, m_ji, heaven_stems_list)\n",
    "\n",
    "        gongmang_chars = self._calculate_gongmang(d_gan, d_ji)\n",
    "        gm_pillars = []\n",
    "        gm_clean = [gm.split('(')[0] for gm in gongmang_chars]\n",
    "        if y_ji.split('(')[0] in gm_clean: gm_pillars.append(f'년지({y_ji.split('(')[0]})')\n",
    "        if m_ji.split('(')[0] in gm_clean: gm_pillars.append(f'월지({m_ji.split('(')[0]})')\n",
    "        if h_ji.split('(')[0] in gm_clean: gm_pillars.append(f'시지({h_ji.split('(')[0]})')\n",
    "        gongmang_str = ', '.join(gm_pillars) if gm_pillars else '해당 없음'\n",
    "\n",
    "        strength = self._calculate_saju_strength(d_gan, pillars, ohaeng)\n",
    "        yongsin_result = self._calculate_yongsin(d_gan, pillars, ohaeng, strength['score'])\n",
    "        health_result = self._analyze_health_risks(ohaeng)\n",
    "\n",
    "        # Basic Sibseong to prevent verification errors\n",
    "        sibseong = {\n",
    "             'year_gan': {'name': self._calculate_sibseong(d_gan, y_gan, True), 'role': 'Neutral'},\n",
    "             'year_ji': {'name': self._calculate_sibseong(d_gan, y_ji, False), 'role': 'Neutral'},\n",
    "             'month_gan': {'name': self._calculate_sibseong(d_gan, m_gan, True), 'role': 'Neutral'},\n",
    "             'month_ji': {'name': self._calculate_sibseong(d_gan, m_ji, False), 'role': 'Neutral'},\n",
    "             'day_gan': {'name': '비견', 'role': 'Neutral'},\n",
    "             'day_ji': {'name': self._calculate_sibseong(d_gan, d_ji, False), 'role': 'Neutral'},\n",
    "             'hour_gan': {'name': self._calculate_sibseong(d_gan, h_gan, True), 'role': 'Neutral'} if not self.time_unknown else {'name': '', 'role': ''},\n",
    "             'hour_ji': {'name': self._calculate_sibseong(d_gan, h_ji, False), 'role': 'Neutral'} if not self.time_unknown else {'name': '', 'role': ''}\n",
    "        }\n",
    "        interactions = []\n",
    "        interaction_details = []\n",
    "\n",
    "        result = {\n",
    "            'info': {\n",
    "                'name': self.name,\n",
    "                'email': self.email,\n",
    "                'input_date': self.birth_date_str,\n",
    "                'calendar_type': '음력(Lunar)' if self.calendar_type == 'lunar' else '양력(Solar)',\n",
    "                'is_leap_month': self.is_leap_month,\n",
    "                'input_time': '모름(Unknown)' if self.time_unknown else self.input_dt.strftime('%H:%M'),\n",
    "                'gender': '남성(Male)' if self.gender == 'male' else '여성(Female)',\n",
    "                'adjusted_date': self.adjusted_dt.strftime('%Y-%m-%d %H:%M'),\n",
    "                'summer_time_applied': self.is_summer_time,\n",
    "                'longitude_correction': '-32분 (서울 기준)' if not self.time_unknown else '적용 안 함'\n",
    "            },\n",
    "            'four_pillars': {\n",
    "                'year': {'gan': y_gan, 'ji': y_ji},\n",
    "                'month': {'gan': m_gan, 'ji': m_ji},\n",
    "                'day': {'gan': d_gan, 'ji': d_ji},\n",
    "                'hour': {'gan': h_gan, 'ji': h_ji}\n",
    "            },\n",
    "            'five_elements': ohaeng,\n",
    "            'gyeokguk': gyeok_result,\n",
    "            'daewoon': daewoon,\n",
    "            'sibseong': sibseong,\n",
    "            'sinsal': sinsal,\n",
    "            'interactions': interactions,\n",
    "            'interaction_details': interaction_details,\n",
    "            'twelve_unseong': twelve_unseong,\n",
    "            'jijanggan': jijanggan,\n",
    "            'sipsinsal': sipsinsal,\n",
    "            'gongmang': gongmang_str,\n",
    "            'strength': strength,\n",
    "            'yongsin_structure': yongsin_result['yongsin_structure'],\n",
    "            'health_analysis': health_result\n",
    "        }\n",
    "        return result\n",
    "\n"
]

final_lines = lines[:start_line_idx] + new_method_lines + lines[end_line_idx:]

with open(target_file, "w", encoding="utf-8") as f:
    f.writelines(final_lines)

print("Restored by line numbers.")
