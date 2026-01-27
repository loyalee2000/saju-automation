import os

target_file = "../program1-calculator/saju_app.py"

with open(target_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
skip = False

# We need to fix the specific block around line 1250 (in current file)
# The block should be inside the try block of get_result_json, assuming it starts there.
# Checking context:
# dw['score'] = dw_score; dw['vibe'] = dw_vibe   (16 spaces)
# So the next lines should be 12 spaces (if outside the for loop) or 12 spaces.

# The corrupted lines:
#             # [포스텔러 방식] 신살 계산 - 전면 재작성 (12 spaces)
#             # Store for Sinsal calc (12 spaces)
#             self.day_gan_char = d_gan.split('(')[0] (12 spaces)
#             self.day_ji_char = d_ji.split('(')[0] (12 spaces)
#             
#             # Store for Sinsal calc (12 spaces? No, 8 spaces in sed output)
#         self.day_gan_char = d_gan.split('(')[0] (8 spaces, causing syntax error)

for i, line in enumerate(lines):
    stripped = line.lstrip()
    indent = len(line) - len(stripped)
    
    # Remove the duplicate inserted block header if it exists
    if "# Store for Sinsal calc" in line and i+1 < len(lines) and "self.day_gan_char" in lines[i+1]:
        # This is the start of the block.
        # Check if it was the *bad* one (indent 8).
        if indent == 8:
            # We need to indent this whole block to 12.
            new_lines.append("    " + line)
            continue
            
    # Fix indent for lines starting with self.day_gan_char etc
    if "self.day_gan_char =" in line and indent == 8:
        new_lines.append("    " + line)
        continue
    if "self.day_ji_char =" in line and indent == 8:
        new_lines.append("    " + line)
        continue
    if "self.year_ji_char =" in line and indent == 8:
        new_lines.append("    " + line)
        continue
        
    if "y_sinsal =" in line and indent == 8:
        new_lines.append("    " + line)
        continue
    if "m_sinsal =" in line and indent == 8:
        new_lines.append("    " + line)
        continue
    if "d_sinsal =" in line and indent == 8:
        new_lines.append("    " + line)
        continue
    if "h_sinsal =" in line and indent == 8:
        new_lines.append("    " + line)
        continue
        
    if "sinsal = {" in line and indent == 8:
        new_lines.append("    " + line)
        continue
        
    # Indent dictionary contents
    if "'year': y_sinsal," in line and indent == 12:
        new_lines.append("    " + line)
        continue
    if "'month': m_sinsal," in line and indent == 12:
        new_lines.append("    " + line)
        continue
    if "'day': d_sinsal," in line and indent == 12:
        new_lines.append("    " + line)
        continue
    if "'hour': h_sinsal" in line and indent == 12:
        new_lines.append("    " + line)
        continue

    # Closing brace
    if line.strip() == "}" and indent == 8:
        # We need to be careful not to catch other braces.
        # The sinsal block closing brace.
        # It's usually followed by existing code.
        new_lines.append("    " + line)
        continue
        
    new_lines.append(line)

with open(target_file, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("Cleaned up 1988 patch indentation.")
