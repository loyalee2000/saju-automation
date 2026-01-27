import os

target_file = "../program1-calculator/saju_app.py"

with open(target_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
skip = False

# We look for the "sip# Store for Sinsal calc" corruption
# and the accidentally inserted Sinsal block there.

for i, line in enumerate(lines):
    if "sip#" in line:
        # This line is likely "sipsinsal = {..." that got mangled.
        # We should probably restore sipsinsal calculation if possible, or just remove the garbage.
        # The line seen was: "            sip# Store for Sinsal calc"
        # We will assume we can just remove this garbage line.
        continue
        
    count_spaces = len(line) - len(line.lstrip())
    
    # Fix indentation for the Sinsal block which I inserted with 8 spaces but should be 12
    # The block starts with "        self.day_gan_char = ...", which is 8 spaces.
    # It should be 12 spaces if it is inside key blocks.
    if "self.day_gan_char = d_gan.split('(')[0]" in line and count_spaces == 8:
        # Check if this is the block we want to indent
        new_lines.append("    " + line)
        continue
    
    if "self.day_ji_char = d_ji.split('(')[0]" in line and count_spaces == 8:
        new_lines.append("    " + line)
        continue
        
    if "sinsal = {" in line and count_spaces == 8:
        new_lines.append("    " + line)
        continue
        
    # Indent the content of sinsal dict (lines starting with 'year', 'month' etc indented by 12)
    # The previous insert had them at 12 spaces, so they need 16 spaces?
    # Original insert:
    #             'year': {
    #                 'gan': ...
    # This is 12 spaces. Expected 16.
    if "    'year': {" in line and count_spaces == 12:
         new_lines.append("    " + line)
         continue
         
    if "    'month': {" in line and count_spaces == 12:
         new_lines.append("    " + line)
         continue

    if "    'day': {" in line and count_spaces == 12:
         new_lines.append("    " + line)
         continue

    if "    'hour': {" in line and count_spaces == 12:
         new_lines.append("    " + line)
         continue
         
    if "    'gan': self._calculate_pillar" in line and count_spaces == 16:
         new_lines.append("    " + line)
         continue
    if "    'ji': self._calculate_pillar" in line and count_spaces == 16:
         new_lines.append("    " + line)
         continue

    # Closing brace indentation
    if line.strip() == "}" and count_spaces == 8:
        new_lines.append("    " + line)
        continue

    new_lines.append(line)

with open(target_file, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("Cleaned up saju_app.py")
