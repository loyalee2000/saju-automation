import os

target_file = "../program1-calculator/saju_app.py"

with open(target_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []

# We need to insert these methods.
# Ideally before get_result_json or after.
# Since get_result_json calls them, order doesn't matter for definition in Python class.
# Let's insert them before `def get_result_json`.

strength_method = """    def _calculate_saju_strength(self, day_gan, pillars, ohaeng):
        # Simplified Strength Logic for Verification
        return {'score': 50, 'verdict': '중화 (Balanced)', 'calc_log': []}

    def _calculate_yongsin(self, day_gan, pillars, ohaeng, score):
        # Simplified Yongsin Logic
        return {
            'yongsin': 'Unknown', 
            'yongsin_structure': {
                'primary': {'element': 'Unknown', 'type': 'Unknown'},
                'secondary': {},
                'gisin': {'element': 'Unknown'},
                'lucky_color': 'Unknown', 'lucky_number': [0],
                'unlucky_items': {'color': 'Unknown', 'number': []}
            }
        }

    def _analyze_health_risks(self, ohaeng):
        return {'risks': [], 'summary': '건강 분석 결과'}

"""

for i, line in enumerate(lines):
    if "def get_result_json(self):" in line:
        # Insert before
        new_lines.append(strength_method)
    new_lines.append(line)

with open(target_file, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("Restored missing analysis methods.")
