import os

target_file = "../program1-calculator/saju_app.py"

with open(target_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []

for i, line in enumerate(lines):
    new_lines.append(line)
    if "self.minute = self.adjusted_dt.minute" in line:
        new_lines.append("        self.email = 'unknown@example.com'\n") # Placeholder

with open(target_file, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("Added email attribute.")
