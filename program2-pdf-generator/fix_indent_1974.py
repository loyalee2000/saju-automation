import os

target_file = "../program1-calculator/saju_app.py"

with open(target_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

# The error is at "self.day_gan_char = d_gan.split('(')[0]"
# It says "unexpected indent". Probably I added extra spaces or similar.
# The context is inside `get_result_json`.
# Standard indent is 8 spaces (method inside class).
# Let's inspect around line 1511.

new_lines = []
for i, line in enumerate(lines):
    # Locate the block I injected.
    if "self.day_gan_char =" in line and "d_gan.split" in line:
        # Re-indent to 8 spaces (assuming it's inside get_result_json)
        # But wait, helper function split_pillar was defined inside get_result_json at 12 spaces?
        # No, `get_result_json` logic is at 8 spaces level?
        # Let's check `get_result_json` def. It is at 4 spaces.
        # So code inside is 8 spaces.
        stripped = line.strip()
        new_lines.append("        " + stripped + "\n")
        continue

    if "self.year_gan_char =" in line:
        stripped = line.strip()
        new_lines.append("        " + stripped + "\n")
        continue

    if "self.month_gan_char =" in line:
        stripped = line.strip()
        new_lines.append("        " + stripped + "\n")
        continue

    if "self.hour_gan_char =" in line:
        stripped = line.strip()
        new_lines.append("        " + stripped + "\n")
        continue
        
    if "self.day_ji_char =" in line and "d_ji.split" in line:
         stripped = line.strip()
         new_lines.append("        " + stripped + "\n")
         continue
         
    if "self.year_ji_char =" in line:
         stripped = line.strip()
         new_lines.append("        " + stripped + "\n")
         continue
         
    if "self.month_ji_char =" in line:
         stripped = line.strip()
         new_lines.append("        " + stripped + "\n")
         continue
         
    new_lines.append(line)

with open(target_file, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("Fixed indentation for variable injections.")
