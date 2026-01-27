import os

target_file = "../program1-calculator/saju_app.py"

with open(target_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
inserted = False

for i, line in enumerate(lines):
    new_lines.append(line)
    if not inserted and "# 12신살 계산" in line:
        new_lines.append("            sipsinsal = {\n")
        new_lines.append("                'year': self._calculate_12sinsal(y_ji, y_ji),\n")
        new_lines.append("                'month': self._calculate_12sinsal(y_ji, m_ji),\n")
        new_lines.append("                'day': self._calculate_12sinsal(y_ji, d_ji),\n")
        new_lines.append("                'hour': self._calculate_12sinsal(y_ji, h_ji)\n")
        new_lines.append("            }\n")
        inserted = True

with open(target_file, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("Restored sipsinsal.")
