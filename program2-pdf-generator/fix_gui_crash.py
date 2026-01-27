import os

target_file = "../program1-calculator/saju_app.py"

with open(target_file, "r", encoding="utf-8") as f:
    content = f.read()

# Locate _display_simple
# We will replace the whole method to be safe.

old_part = """    def _display_simple(self, res):
        t = self.result_text
        t.delete(1.0, tk.END)
        
        t.insert(tk.END, f"=== {res['info']['name']}님의 사주 ===\\n\\n")
        
        fp = res['four_pillars']
        t.insert(tk.END, "시주  일주  월주  년주\\n")
        t.insert(tk.END, f"{fp['hour']['text']}  {fp['day']['text']}  {fp['month']['text']}  {fp['year']['text']}\\n\\n")
        
        t.insert(tk.END, f"대운수: {res['daewoon']['pillars'][0]['age']} ({res['daewoon']['direction']})\\n")
        t.insert(tk.END, f"강약: {res['strength']['verdict']} ({res['strength']['score']}점)\\n\\n")
        
        y = res['yongsin_structure']
        t.insert(tk.END, f"용신: {y['primary']['element']} ({y['primary']['type']})\\n")
        t.insert(tk.END, f"희신: {y['secondary']['element']} | 기신: {y['gisin']['element']}\\n\\n")
        
        s = res['sinsal']
        t.insert(tk.END, "[신살]\\n")
        t.insert(tk.END, f"년: {', '.join(s['year']['ji'])}\\n")
        t.insert(tk.END, f"월: {', '.join(s['month']['ji'])}\\n")
        t.insert(tk.END, f"일: {', '.join(s['day']['ji'])}\\n")
        t.insert(tk.END, f"시: {', '.join(s['hour']['ji'])}\\n")
        
        if 'luck_cycle' in res:
            t.insert(tk.END, "\\n[세운 (최근 10년)]\\n")
            lc = res['luck_cycle']['yearly']
            for item in lc:
                t.insert(tk.END, f"{item['year']}: {item['ganji']}  ")
            t.insert(tk.END, "\\n")
"""

new_part = """    def _display_simple(self, res):
        t = self.result_text
        t.delete(1.0, tk.END)
        
        # Info
        name = res.get('info', {}).get('name', 'Unknown')
        t.insert(tk.END, f"=== {name}님의 사주 ===\\n\\n")
        
        # Pillars
        fp = res.get('four_pillars', {})
        t.insert(tk.END, "시주  일주  월주  년주\\n")
        
        def get_p_text(p_key):
            return fp.get(p_key, {}).get('text', '')
            
        t.insert(tk.END, f"{get_p_text('hour')}  {get_p_text('day')}  {get_p_text('month')}  {get_p_text('year')}\\n\\n")
        
        # Daewoon
        dw = res.get('daewoon', {})
        dw_cols = dw.get('pillars', [])
        dw_age = dw_cols[0].get('age', '-') if dw_cols else '-'
        dw_dir = dw.get('direction', '-')
        t.insert(tk.END, f"대운수: {dw_age} ({dw_dir})\\n")
        
        # Strength
        st = res.get('strength', {})
        st_verdict = st.get('verdict', '-')
        st_score = st.get('score', 0)
        t.insert(tk.END, f"강약: {st_verdict} ({st_score}점)\\n\\n")
        
        # Yongsin (Safe Access)
        y = res.get('yongsin_structure', {})
        prim = y.get('primary') or {} # Handle None
        sec = y.get('secondary') or {}
        gisin = y.get('gisin') or {}
        
        p_el = prim.get('element', '-')
        p_type = prim.get('type', '-')
        s_el = sec.get('element', '-')
        g_el = gisin.get('element', '-')
        
        t.insert(tk.END, f"용신: {p_el} ({p_type})\\n")
        t.insert(tk.END, f"희신: {s_el} | 기신: {g_el}\\n\\n")
        
        # Sinsal
        s = res.get('sinsal', {})
        t.insert(tk.END, "[신살]\\n")
        
        def join_sinsal(p_key):
            # p_key -> {'gan': [], 'ji': []}
            p_data = s.get(p_key, {})
            items = p_data.get('ji', []) + p_data.get('gan', [])
            # Filter duplicates if any
            items = list(dict.fromkeys(items)) 
            return ', '.join(items) if items else '-'

        t.insert(tk.END, f"년: {join_sinsal('year')}\\n")
        t.insert(tk.END, f"월: {join_sinsal('month')}\\n")
        t.insert(tk.END, f"일: {join_sinsal('day')}\\n")
        t.insert(tk.END, f"시: {join_sinsal('hour')}\\n")
        
        if 'luck_cycle' in res:
            t.insert(tk.END, "\\n[세운 (최근 10년)]\\n")
            lc = res['luck_cycle'].get('yearly', [])
            for item in lc:
                t.insert(tk.END, f"{item['year']}: {item['ganji']}  ")
            t.insert(tk.END, "\\n")
"""

# Determine start/end of _display_simple
start_marker = "    def _display_simple(self, res):"
start_idx = content.find(start_marker)

if start_idx != -1:
    # Find next method or class end
    # SajuApp usually ends with this method or main.
    # Look for "def main():" or "if __name__" or next "def "
    next_def = content.find("\ndef main():", start_idx)
    next_method = content.find("\n    def ", start_idx + 50)
    
    end_idx = -1
    if next_method != -1:
        end_idx = next_method
    elif next_def != -1:
        end_idx = next_def
    else:
        # Just replace until end? 
        # Risky if other stuff exists
        # Let's assume it ends before `def main():`
        pass

    if end_idx != -1:
         new_content = content[:start_idx] + new_part + content[end_idx:]
    else:
         # Assume it was the last method in class
         # Find where class ends?
         # It's indented.
         # Let's search for "def main():" specifically
         main_idx = content.find("def main():")
         if main_idx != -1:
             new_content = content[:start_idx] + new_part + content[main_idx:]
         else:
             print("Could not find end of _display_simple.")
             exit(1)

    with open(target_file, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("Fixed _display_simple crash.")

else:
    print("_display_simple not found.")
