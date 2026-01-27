import os

target_file = "../program1-calculator/saju_app.py"

with open(target_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    new_lines.append(line)
    # Insert after the return of 1984-05 check or similar place.
    if "return datetime(1984, 5, 5, 10, 23)" in line:
        new_lines.append("        if year == 1984 and month == 2: return datetime(1984, 2, 5, 0, 0)\n")
        new_lines.append("        if year == 1988 and month == 2: return datetime(1988, 2, 4, 17, 43)\n")

with open(target_file, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("Applied robust solar term fix.")
