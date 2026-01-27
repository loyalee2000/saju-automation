import os

target_file = "../program1-calculator/saju_app.py"

with open(target_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    # Check for the double indented methods I inserted
    # "        def _calculate_luck_cycle" -> "    def _calculate_luck_cycle"
    if line.startswith("        def _calculate_luck_cycle"):
        new_lines.append(line.replace("        def", "    def", 1))
    elif line.startswith("        def _calculate_multi_yongsin"):
        new_lines.append(line.replace("        def", "    def", 1))
    elif line.startswith("        def _calculate_yongsin"):
        new_lines.append(line.replace("        def", "    def", 1))
    elif line.startswith("        def _analyze_health_risks"):
        new_lines.append(line.replace("        def", "    def", 1))
    # get_result_json might also be affected
    elif line.startswith("        def get_result_json"):
        new_lines.append(line.replace("        def", "    def", 1))
    else:
        new_lines.append(line)

with open(target_file, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("Fixed indentation for restored methods.")
