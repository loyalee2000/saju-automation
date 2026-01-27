import os

target_file = "../program1-calculator/saju_app.py"

with open(target_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
start_fix = False
end_fix = False

# We need to target the block starting with self.day_gan_char = ... and ending with }
# and indent it by 4 spaces.

for i, line in enumerate(lines):
    # Detect start of our block
    if "self.day_gan_char = d_gan.split('(')[0]" in line and line.startswith("        self.day_gan_char"):
        start_fix = True
        
    if start_fix and not end_fix:
        # Check if we reached the end (the line with just })
        # But wait, there might be other } lines.
        # The block ends with the closing brace of sinsal dict
        
        # Add 4 spaces
        new_lines.append("    " + line)
        
        if line.strip() == "}":
            end_fix = True
            start_fix = False # Use flag to stop
    else:
        new_lines.append(line)

with open(target_file, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("Fixed indentation.")
