import sys
sys.path.append("../program1-calculator")
from saju_app import SajuAnalyzer
import datetime
import json

# Test Case: 2000-01-01 12:00 (Random date)
# Expected: Daewoon should be calculated by formula, Sinsal by formula.
target_date = "2000-01-01"
target_time = "12:00"
gender = "male"

analyzer = SajuAnalyzer(target_date, target_time, gender)
result = analyzer.get_result_json()

print(f"=== TEST DATE: {target_date} ===")
print(f"Four Pillars: {result['four_pillars']['year']['text']} / {result['four_pillars']['month']['text']} / {result['four_pillars']['day']['text']} / {result['four_pillars']['hour']['text']}")

print("\n=== DAEWOON ===")
print(f"Direction: {result['daewoon']['direction']}")
print(f"First Age: {result['daewoon']['pillars'][0]['age']}")

print("\n=== SINSAL SAMPLE ===")
print("Year Gan:", result['sinsal']['year']['gan'])
print("Day Ji:", result['sinsal']['day']['ji'])
print(json.dumps(result['sinsal'], indent=2, ensure_ascii=False))
