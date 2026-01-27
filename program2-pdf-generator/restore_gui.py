import os

target_file = "../program1-calculator/saju_app.py"

# Standard SajuApp GUI Code (Simplified for recovery, should catch most needs)
# Imports might be missing? No, imports are at top.
# We append this to the end.

gui_code = """
import tkinter as tk
from tkinter import ttk, messagebox
import threading

class SajuApp:
    def __init__(self, root):
        self.root = root
        self.root.title("사주 분석 프로그램 v2.0 (포스텔러 맞춤형)")
        self.root.geometry("600x750")
        
        # Styles
        style = ttk.Style()
        style.configure("TLabel", font=("Apple SD Gothic Neo", 12))
        style.configure("TButton", font=("Apple SD Gothic Neo", 12))
        
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Input Fields
        ttk.Label(main_frame, text="이름:").grid(row=0, column=0, sticky="w", pady=5)
        self.name_entry = ttk.Entry(main_frame)
        self.name_entry.grid(row=0, column=1, sticky="ew", pady=5)
        
        ttk.Label(main_frame, text="생년월일 (YYYY-MM-DD):").grid(row=1, column=0, sticky="w", pady=5)
        self.date_entry = ttk.Entry(main_frame)
        self.date_entry.grid(row=1, column=1, sticky="ew", pady=5)
        self.date_entry.insert(0, "1984-01-29")
        
        ttk.Label(main_frame, text="시간 (HH:MM):").grid(row=2, column=0, sticky="w", pady=5)
        self.time_entry = ttk.Entry(main_frame)
        self.time_entry.grid(row=2, column=1, sticky="ew", pady=5)
        self.time_entry.insert(0, "18:30")
        
        ttk.Label(main_frame, text="성별:").grid(row=3, column=0, sticky="w", pady=5)
        self.gender_var = tk.StringVar(value="male")
        ttk.Radiobutton(main_frame, text="남성", variable=self.gender_var, value="male").grid(row=3, column=1, sticky="w")
        ttk.Radiobutton(main_frame, text="여성", variable=self.gender_var, value="female").grid(row=3, column=1, sticky="e")
        
        # Actions
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        self.analyze_btn = ttk.Button(btn_frame, text="사주 분석 실행", command=self.run_analysis)
        self.analyze_btn.pack(side=tk.LEFT, padx=5)
        
        # Result Area
        self.result_text = tk.Text(main_frame, height=20, font=("Menlo", 12))
        self.result_text.grid(row=6, column=0, columnspan=2, sticky="nsew", pady=5)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.result_text.yview)
        scrollbar.grid(row=6, column=2, sticky="ns")
        self.result_text.configure(yscrollcommand=scrollbar.set)
        
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(6, weight=1)

    def run_analysis(self):
        name = self.name_entry.get()
        date_str = self.date_entry.get()
        time_str = self.time_entry.get()
        gender = self.gender_var.get()
        
        try:
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "분석 중입니다...\\n")
            
            analyzer = SajuAnalyzer(date_str, time_str, gender, name=name)
            result = analyzer.get_result_json()
            
            # Simple Display
            output = f"=== {name}님의 사주 분석 결과 ===\\n"
            output += f"일주: {result['four_pillars']['day']['text']}\\n"
            output += f"월주: {result['four_pillars']['month']['text']}\\n"
            output += f"년주: {result['four_pillars']['year']['text']}\\n"
            output += f"시주: {result['four_pillars']['hour']['text']}\\n\\n"
            
            output += f"대운수: {result['daewoon']['pillars'][0]['age']}\\n"
            output += f"대운흐름: {result['daewoon']['direction']}\\n\\n"
            
            output += "=== 신살 ===\\n"
            s = result['sinsal']
            output += f"일반: {s['day']['gan'] + s['day']['ji']}\\n\\n"
            
            output += "=== 용신 ===\\n"
            y = result['yongsin_structure']
            output += f"용신: {y['primary']['element']} ({y['primary']['type']})\\n"
            
            self.result_text.insert(tk.END, output)
            
            # Save JSON
            with open("saju_analysis_result.json", "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("완료", "분석이 완료되었습니다. 결과가 저장되었습니다.")
            
        except Exception as e:
            messagebox.showerror("오류", f"분석 중 오류가 발생했습니다:\\n{str(e)}")
            import traceback
            traceback.print_exc()

def main():
    root = tk.Tk()
    app = SajuApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
"""

with open(target_file, "a", encoding="utf-8") as f:
    f.write(gui_code)

print("Restored SajuApp GUI class.")
