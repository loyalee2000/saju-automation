import sys
sys.path.append("../program1-calculator")
from saju_app import SajuAnalyzer
import json

target_date = "1974-12-17"
target_time = "12:30"
gender = "male"

analyzer = SajuAnalyzer(target_date, target_time, gender)
result = analyzer.get_result_json()

print("=== DAEWOON YEARS CHECK ===")
pillars = result['daewoon']['pillars']
for p in pillars[:3]:
    print(f"Age: {p['age']} | Year: {p.get('year')} ~ {p.get('end_year')}")

if 'year' in pillars[0]:
    print("SUCCESS: Year field exists.")
else:
    print("FAILURE: Year field missing.")
