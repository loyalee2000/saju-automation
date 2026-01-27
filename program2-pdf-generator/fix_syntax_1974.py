import os

target_file = "../program1-calculator/saju_app.py"

with open(target_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if "self.hour_gan_char =" in line and "else" in line:
        # Force correct line
        # Assuming h_gan is available in context (it is, from split_pillar)
        new_lines.append('        self.hour_gan_char = h_gan.split("(")[0] if h_gan != "모름" else ""\n')
    else:
        new_lines.append(line)

with open(target_file, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("Fixed syntax error for hour_gan_char.")
