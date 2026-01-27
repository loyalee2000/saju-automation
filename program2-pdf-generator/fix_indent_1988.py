import os

target_file = "../program1-calculator/saju_app.py"

with open(target_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []

for i, line in enumerate(lines):
    # Check for the corrupted def _calculate_pillar_sinsal line
    # Seen in output: "        def _calculate_pillar_sinsal(self, gan, ji, pillar_type):"
    # Wait, the error was IndentationError on line 249, which is the """" docstring.
    # Because the line before it `def ...` was indented by 8 spaces? 
    # Or maybe because it was inside `_calculate_sinsal` or something?
    # In the `sed` output:
    # Line 248: `        def _calculate_pillar_sinsal(self, gan, ji, pillar_type):`
    # This is 8 spaces. This implies it's inside `_calculate_sinsal`? 
    # Or just incorrectly indented. Class methods should be 4 spaces.
    
    # Also I see `_calculate_sinsal` above seemingly cut off?
    # `        samhap = {`
    # `            '인(寅)': '인오술', ...`
    # `            }`
    # Then `        def _calculate_pillar_sinsal...`
    
    # We want `def _calculate_pillar_sinsal` to be at 4 spaces.
    
    if "def _calculate_pillar_sinsal(self, gan, ji, pillar_type):" in line:
        new_lines.append("    def _calculate_pillar_sinsal(self, gan, ji, pillar_type):\n")
        continue

    new_lines.append(line)

with open(target_file, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("Fixed indentation for _calculate_pillar_sinsal.")
