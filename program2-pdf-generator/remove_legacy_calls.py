import os

target_file = "../program1-calculator/saju_app.py"

with open(target_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
skip = False

# Remove the legacy Sinsal block inside get_result_json
# Starts with "# === 일간 기준 신살 ==="
# Ends with the last check (Gwaegang)

for i, line in enumerate(lines):
    if "# === 일간 기준 신살 ===" in line:
        skip = True
        
    if skip:
        # Heuristic to stop skipping: when indentation drops back or we see something else
        # The block is inside a loop (16 spaces indent).
        # We stop skipping if we see something that is NOT part of this block.
        # But looking at Step 240 output, this block goes until the end of the loop body for Sinsal.
        # The next thing after this loop?
        # Step 156 tail output showed:
        # output += ...
        # which is 8 spaces indent.
        
        # So if we see a line with < 16 spaces indent that is not empty/comment, we stop skipping.
        # But wait, there might be other things in the loop?
        # The loop iterates `for p_name...`.
        # Step 149 showed `sinsal[p_name]['ji'].append("괴강살")` as the last thing.
        # Then `formatted_pillars = ...` is likely after the loop (12 spaces).
        
        if len(line.strip()) > 0 and not line.strip().startswith("#") and (len(line) - len(line.lstrip())) < 16:
            skip = False
            
    if not skip:
        new_lines.append(line)

with open(target_file, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("Removed legacy legacy calls.")
