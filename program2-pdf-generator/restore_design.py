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

# NEW IMPROVED GUI CODE
new_gui_code = """import tkinter as tk
from tkinter import ttk, messagebox, font
import json
import threading

class SajuApp:
    def __init__(self, root):
        self.root = root
        self.root.title("사주 분석 프로그램 v2.5 (Professional)")
        self.root.geometry("1000x800")
        self.root.configure(bg="#2E2E2E")
        
        # Configure Styles
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Dark Theme Configuration
        self.style.configure(".", background="#2E2E2E", foreground="white", fieldbackground="#404040")
        self.style.configure("TLabel", background="#2E2E2E", foreground="#E0E0E0", font=("Apple SD Gothic Neo", 12))
        self.style.configure("Header.TLabel", font=("Apple SD Gothic Neo", 18, "bold"), foreground="#FFFFFF")
        self.style.configure("TButton", font=("Apple SD Gothic Neo", 12, "bold"), background="#4A4A4A", foreground="white", borderwidth=0)
        self.style.map("TButton", background=[("active", "#5A5A5A")])
        self.style.configure("TEntry", fieldbackground="#404040", foreground="white", insertcolor="white")
        self.style.configure("TRadiobutton", background="#2E2E2E", foreground="#E0E0E0", font=("Apple SD Gothic Neo", 11))
        
        # Main Container
        main_frame = ttk.Frame(root, padding="30")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Header
        header = ttk.Label(main_frame, text="사주 명리학 정밀 분석기", style="Header.TLabel")
        header.pack(anchor="center", pady=(0, 20))
        
        # Input Section (Frame)
        input_frame = ttk.LabelFrame(main_frame, text="기본 정보", padding="20")
        input_frame.pack(fill="x", pady=10)
        # Apply dark style to LabelFrame label? Hard in Tkinter. 
        # Just use Frame with Label header if needed. But LabelFrame is okay.
        
        # Grid Layout
        input_frame.columnconfigure(1, weight=1)
        input_frame.columnconfigure(3, weight=1)
        
        # Row 0: Name & Gender
        ttk.Label(input_frame, text="이름").grid(row=0, column=0, sticky="w", padx=10, pady=10)
        self.name_entry = ttk.Entry(input_frame)
        self.name_entry.grid(row=0, column=1, sticky="ew", padx=10, pady=10)
        
        ttk.Label(input_frame, text="성별").grid(row=0, column=2, sticky="w", padx=10, pady=10)
        gender_frame = ttk.Frame(input_frame)
        gender_frame.grid(row=0, column=3, sticky="w", padx=10, pady=10)
        self.gender_var = tk.StringVar(value="male")
        ttk.Radiobutton(gender_frame, text="남성", variable=self.gender_var, value="male").pack(side="left", padx=10)
        ttk.Radiobutton(gender_frame, text="여성", variable=self.gender_var, value="female").pack(side="left", padx=10)
        
        # Row 1: Date & Time
        ttk.Label(input_frame, text="생년월일 (YYYY-MM-DD)").grid(row=1, column=0, sticky="w", padx=10, pady=10)
        self.date_entry = ttk.Entry(input_frame)
        self.date_entry.grid(row=1, column=1, sticky="ew", padx=10, pady=10)
        self.date_entry.insert(0, "1974-12-17")
        
        ttk.Label(input_frame, text="시간 (HH:MM)").grid(row=1, column=2, sticky="w", padx=10, pady=10)
        self.time_entry = ttk.Entry(input_frame)
        self.time_entry.grid(row=1, column=3, sticky="ew", padx=10, pady=10)
        self.time_entry.insert(0, "12:30")

        # Action Button
        self.btn_frame = ttk.Frame(main_frame)
        self.btn_frame.pack(fill="x", pady=20)
        
        analyze_btn = ttk.Button(self.btn_frame, text="분석 시작 (Analyze)", command=self.run_analysis)
        analyze_btn.pack(side="right", padx=10)
        
        # Result Section
        self.result_frame = ttk.LabelFrame(main_frame, text="분석 결과", padding="10")
        self.result_frame.pack(fill="both", expand=True)
        
        # Text Widget with Dark Theme
        self.result_text = tk.Text(self.result_frame, font=("Menlo", 13), bg="#1E1E1E", fg="#D0D0D0", 
                                   insertbackground="white", padx=10, pady=10, borderwidth=0, relief="flat")
        self.result_text.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(self.result_frame, orient="vertical", command=self.result_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.result_text.configure(yscrollcommand=scrollbar.set)
        
        # Tags for formatting
        self.result_text.tag_configure("header", font=("Apple SD Gothic Neo", 15, "bold"), foreground="#4EC9B0")
        self.result_text.tag_configure("info", foreground="#569CD6")
        self.result_text.tag_configure("highlight", foreground="#CE9178")
        self.result_text.tag_configure("normal", foreground="#D0D0D0")

    def run_analysis(self):
        name = self.name_entry.get()
        date_str = self.date_entry.get()
        time_str = self.time_entry.get()
        gender = self.gender_var.get()
        
        try:
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "데이터 분석 중...\\n", "info")
            
            analyzer = SajuAnalyzer(date_str, time_str, gender, name=name)
            result = analyzer.get_result_json()
            
            self._display_result(result)
            
            # Save JSON
            with open("saju_analysis_result.json", "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=4)
                
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred:\\n{e}")
            self.result_text.insert(tk.END, f"Error: {e}\\n", "highlight")

    def _display_result(self, res):
        t = self.result_text
        t.delete(1.0, tk.END)
        
        # Header
        t.insert(tk.END, f"=== {res['info']['name']}님의 사주 분석 결과 ===\\n\\n", "header")
        
        # Four Pillars Table-like
        t.insert(tk.END, "[사주 팔자 (Four Pillars)]\\n", "info")
        fp = res['four_pillars']
        row_format = "{:<10} {:<10} {:<10} {:<10}\\n"
        t.insert(tk.END, row_format.format("시주", "일주", "월주", "년주"), "highlight")
        t.insert(tk.END, row_format.format("-" * 8, "-" * 8, "-" * 8, "-" * 8), "normal")
        t.insert(tk.END, row_format.format(fp['hour']['text'], fp['day']['text'], fp['month']['text'], fp['year']['text']), "normal")
        t.insert(tk.END, "\\n")
        
        # Basic Info
        t.insert(tk.END, f"대운수: {res['daewoon']['pillars'][0]['age']} | 대운방향: {res['daewoon']['direction']}\\n", "normal")
        t.insert(tk.END, f"사주강약: {res['strength']['verdict']} (점수: {res['strength']['score']})\\n\\n", "normal")
        
        # Yongsin
        y = res['yongsin_structure']
        t.insert(tk.END, "[용신 (Yongsin)]\\n", "info")
        t.insert(tk.END, f"주용신: {y['primary']['element']} ({y['primary']['type']})\\n", "highlight")
        t.insert(tk.END, f"설명: {y['primary']['reason']}\\n", "normal")
        t.insert(tk.END, f"희신: {y['secondary']['element']} | 기신: {y['gisin']['element']}\\n", "normal")
        t.insert(tk.END, f"행운색: {y['lucky_color']} | 행운숫자: {y['lucky_number']}\\n\\n", "normal")
        
        # Sinsal
        t.insert(tk.END, "[신살 및 귀인 (Sinsal)]\\n", "info")
        s = res['sinsal']
        t.insert(tk.END, f"년지: {', '.join(s['year']['ji']) if s['year']['ji'] else '-'}\\n", "normal")
        t.insert(tk.END, f"월지: {', '.join(s['month']['ji']) if s['month']['ji'] else '-'}\\n", "normal")
        t.insert(tk.END, f"일지: {', '.join(s['day']['ji']) if s['day']['ji'] else '-'}\\n", "normal")
        t.insert(tk.END, f"시지: {', '.join(s['hour']['ji']) if s['hour']['ji'] else '-'}\\n", "normal")
        if s['year']['gan'] or s['month']['gan'] or s['day']['gan'] or s['hour']['gan']:
             t.insert(tk.END, "천간 신살: ", "normal")
             all_gan = s['year']['gan'] + s['month']['gan'] + s['day']['gan'] + s['hour']['gan']
             t.insert(tk.END, f"{', '.join(all_gan)}\\n", "highlight")
        t.insert(tk.END, "\\n")
        
        # Luck Cycle Partial
        if 'luck_cycle' in res:
            t.insert(tk.END, "[세운 (Yearly Luck) - 향후 10년]\\n", "info")
            lc = res['luck_cycle']['yearly']
            line = ""
            for item in lc:
                line += f"{item['year']}({item['ganji']})  "
            t.insert(tk.END, line + "\\n\\n", "normal")

        # Health
        if 'health_analysis' in res:
             t.insert(tk.END, "[건강 분석]\\n", "info")
             h = res['health_analysis']
             t.insert(tk.END, f"요약: {h['summary']}\\n", "normal")
             for r in h['risks']:
                 t.insert(tk.END, f"- {r['type']}: {r['advice']}\\n", "normal")

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

print("Restored Professional Dark GUI.")
