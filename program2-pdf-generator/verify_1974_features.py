import sys
sys.path.append("../program1-calculator")
from saju_app import SajuAnalyzer
import json

target_date = "1974-12-17"
target_time = "12:30"
gender = "male"

analyzer = SajuAnalyzer(target_date, target_time, gender)
result = analyzer.get_result_json()

print("=== NEW FEATURES CHECK ===")
print("Luck Cycle Present:", "luck_cycle" in result)
if "luck_cycle" in result:
    print("Yearly Count:", len(result['luck_cycle']['yearly']))
    print("Monthly Count:", len(result['luck_cycle']['monthly']))

print("Multi Yongsin Present:", "multi_yongsin" in result)

print("Yongsin Structure Keys:", result['yongsin_structure']['primary'].keys())
print("Health Analysis Keys:", result['health_analysis'].keys())
print("Detailed Risks Example:", result['health_analysis']['risks'][0] if result['health_analysis']['risks'] else "None")
