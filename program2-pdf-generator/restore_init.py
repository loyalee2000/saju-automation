import os

target_file = "../program1-calculator/saju_app.py"

with open(target_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []

for i, line in enumerate(lines):
    new_lines.append(line)
    if "self.month = self.adjusted_dt.month" in line:
        # Check if next line is already self.day (to avoid dupes if I run twice)
        if i+1 < len(lines) and "self.day =" in lines[i+1]:
            continue
            
        new_lines.append("        self.day = self.adjusted_dt.day\n")
        new_lines.append("        self.hour = self.adjusted_dt.hour\n")
        new_lines.append("        self.minute = self.adjusted_dt.minute\n")

with open(target_file, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("Restored init attributes.")
