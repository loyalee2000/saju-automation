import os

target_file = "../program1-calculator/saju_app.py"

with open(target_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
skip = False

# We want to remove the old Sinsal methods if they are causing syntax errors or are unused
# Specifically the empty one: def _calculate_cheonmun(self, gan, branch):

for i, line in enumerate(lines):
    if "def _calculate_cheonmun(self, gan, branch):" in line:
        # Skip this line and potentially following lines if they were part of it? 
        # But here it's empty, so just skipping the def line fixes the indentation error 
        # for the next def.
        continue
        
    new_lines.append(line)

with open(target_file, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("Removed dead code.")
