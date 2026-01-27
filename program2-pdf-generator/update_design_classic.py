import os

target_file = "../program1-calculator/saju_app.py"

with open(target_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Locate 'class SajuApp:'
start_idx = -1
for i, line in enumerate(lines):
    if "class SajuApp:" in line:
        start_idx = i
        break

if start_idx == -1:
    print("Could not find class SajuApp")
    exit(1)

# Keep content BEFORE SajuApp
content_before = "".join(lines[:start_idx])

# CLASSIC COMPACT GUI CODE
# Preserving all functionality: Solar/Lunar, Leap, Unknown Time, Dynamic Save
new_gui_code = """import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

class SajuApp:
    def __init__(self, root):
        self.root = root
        self.root.title("사주 분석 v2.7 (Classic)")
        self.root.geometry("550x700")  # Compact size
        
        # Use default theme for native look
        # self.style = ttk.Style()
        # self.style.theme_use('default') 
        
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 1. Input Section (Compact Grid)
        input_frame = ttk.LabelFrame(main_frame, text="사주 정보 입력", padding="10")
        input_frame.pack(fill="x", pady=5)
        
        # Row 0: Name & Gender
        ttk.Label(input_frame, text="이름:").grid(row=0, column=0, sticky="e", padx=5, pady=2)
        self.name_entry = ttk.Entry(input_frame, width=15)
        self.name_entry.grid(row=0, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(input_frame, text="성별:").grid(row=0, column=2, sticky="e", padx=5, pady=2)
        self.gender_var = tk.StringVar(value="male")
        frame_g = ttk.Frame(input_frame)
        frame_g.grid(row=0, column=3, sticky="w")
        ttk.Radiobutton(frame_g, text="남", variable=self.gender_var, value="male").pack(side="left")
        ttk.Radiobutton(frame_g, text="여", variable=self.gender_var, value="female").pack(side="left")
        
        # Row 1: Calendar Type
        ttk.Label(input_frame, text="양음력:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
        frame_c = ttk.Frame(input_frame)
        frame_c.grid(row=1, column=1, columnspan=3, sticky="w", padx=5, pady=2)
        
        self.calendar_var = tk.StringVar(value="solar")
        ttk.Radiobutton(frame_c, text="양력", variable=self.calendar_var, value="solar").pack(side="left", padx=2)
        ttk.Radiobutton(frame_c, text="음력", variable=self.calendar_var, value="lunar").pack(side="left", padx=2)
        self.leap_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(frame_c, text="윤달", variable=self.leap_var).pack(side="left", padx=10)

        # Row 2: Date
        ttk.Label(input_frame, text="생년월일:").grid(row=2, column=0, sticky="e", padx=5, pady=2)
        self.date_entry = ttk.Entry(input_frame, width=20)
        self.date_entry.grid(row=2, column=1, columnspan=2, sticky="w", padx=5, pady=2)
        self.date_entry.insert(0, "1974-12-17")
        ttk.Label(input_frame, text="(YYYY-MM-DD)").grid(row=2, column=3, sticky="w")

        # Row 3: Time
        ttk.Label(input_frame, text="시간:").grid(row=3, column=0, sticky="e", padx=5, pady=2)
        self.time_entry = ttk.Entry(input_frame, width=10)
        self.time_entry.grid(row=3, column=1, sticky="w", padx=5, pady=2)
        self.time_entry.insert(0, "12:30")
        
        self.unknown_time_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(input_frame, text="시간 모름", variable=self.unknown_time_var, command=self.toggle_time).grid(row=3, column=2, sticky="w")
        
        # Analyze Button
        self.analyze_btn = ttk.Button(input_frame, text="분석하기", command=self.run_analysis)
        self.analyze_btn.grid(row=4, column=0, columnspan=4, pady=10)
        
        # 2. Result Section (Simple Text)
        result_frame = ttk.LabelFrame(main_frame, text="분석 결과", padding="5")
        result_frame.pack(fill="both", expand=True, pady=5)
        
        self.result_text = tk.Text(result_frame, font=("Menlo", 12), height=20, width=60)
        self.result_text.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=self.result_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.result_text.configure(yscrollcommand=scrollbar.set)

    def toggle_time(self):
        if self.unknown_time_var.get():
            self.time_entry.configure(state='disabled')
        else:
            self.time_entry.configure(state='normal')

    def run_analysis(self):
        name = self.name_entry.get()
        date_str = self.date_entry.get()
        time_str = self.time_entry.get() if not self.unknown_time_var.get() else None
        gender = self.gender_var.get()
        cal_type = self.calendar_var.get()
        is_leap = self.leap_var.get()
        
        try:
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "분석 중...\\n")
            
            # Run Analysis
            analyzer = SajuAnalyzer(date_str, time_str, gender, name, cal_type, is_leap)
            result = analyzer.get_result_json()
            
            # Display Simple Result
            self._display_simple(result)
            
            # Save File Logic (Dynamic Name)
            save_dir = "/Users/loyalee/Desktop/명리심리연구소"
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            
            safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '_', '-')).strip()
            if not safe_name: safe_name = "Unknown"
            filename = f"saju_result_{safe_name}.json"
            save_path = os.path.join(save_dir, filename)
            
            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=4)
                
            self.result_text.insert(tk.END, f"\\n✅ 저장 완료: {filename}")
                
        except Exception as e:
            messagebox.showerror("오류", f"분석 중 오류 발생:\\n{e}")
            import traceback
            traceback.print_exc()

    def _display_simple(self, res):
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

def main():
    root = tk.Tk()
    app = SajuApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
"""

final_content = content_before + new_gui_code

with open(target_file, "w", encoding="utf-8") as f:
    f.write(final_content)

print("Restored Classic Compact GUI.")
