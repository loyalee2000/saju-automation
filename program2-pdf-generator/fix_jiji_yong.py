import os

target_file = "../program1-calculator/saju_app.py"

with open(target_file, "r", encoding="utf-8") as f:
    content = f.read()

# Replace JIJI_YONG with JIJI_INFO in _calculate_saju_strength
# Context: "else: return JIJI_YONG.get(char, {}).get('element')"
# We will match widely just in case.

if "JIJI_YONG.get" in content:
    content = content.replace("JIJI_YONG.get", "JIJI_INFO.get")
    
if "JIJI_YONG[" in content:
    content = content.replace("JIJI_YONG[", "JIJI_INFO[")

with open(target_file, "w", encoding="utf-8") as f:
    f.write(content)

print("Replaced JIJI_YONG with JIJI_INFO.")
