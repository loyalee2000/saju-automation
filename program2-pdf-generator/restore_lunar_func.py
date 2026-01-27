import os

target_file = "../program1-calculator/saju_app.py"

with open(target_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []

# We need to insert def _convert_lunar_to_solar(self, date_str, is_leap):
# before the "try:" block that uses date_str, IF that try block is not inside the def.
# In the current state, it IS inside __init__ effectively.

for i, line in enumerate(lines):
    # Check if this line is "        try:" (8 spaces) and next line uses date_str
    # or just checks for the specific block we saw
    
    if line.strip() == "try:" and i+1 < len(lines) and "year, month, day = map(int, date_str.split('-'))" in lines[i+1]:
        # found the orphan block
        # Insert the function def before it
        # The function def should be at class level indentation (4 spaces)
        new_lines.append("\n    def _convert_lunar_to_solar(self, date_str, is_leap):\n")
        
        # We also need to fix indentation of the try block.
        # Currently it seems indented by 8 spaces (inside __init__).
        # But if we wrap it in a function, it should be 8 spaces too?
        # Yes, if we put def at 4 spaces, the body (try) should be at 8 spaces.
        # But wait, looking at the previous output "        try:", it IS at 8 spaces.
        # So we just need to insert the def line at 4 spaces.
        
        # However, checking the output from 'sed', "        try:" is aligned with "        self.year = ..." (8 spaces).
        # So if I insert "    def ...", then "        try:" is correct indentation for the new function.
        # BUT, was "        try:" previously intended to be inside __init__? No.
        # So the indentation seems consistent for being inside a new method.
        
        new_lines.append(line)
    else:
        new_lines.append(line)

with open(target_file, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("Restored function header.")
