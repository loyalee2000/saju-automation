import sys
sys.path.append("../program1-calculator")
from saju_app import SajuAnalyzer
import json

target_date = "1974-12-17"
target_time = "12:30"
gender = "male"

analyzer = SajuAnalyzer(target_date, target_time, gender)
result = analyzer.get_result_json()

print("=== SIPSINSAL OUTPUT ===")
print(json.dumps(result.get('sipsinsal', {}), indent=4, ensure_ascii=False))
