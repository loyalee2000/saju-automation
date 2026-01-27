import sys
sys.path.append("../program1-calculator")
from saju_app import SajuAnalyzer
import datetime
import json

# Test Case: 1984-01-29 18:30 Female
# Expected: Daewoon 2. Sinsals detailed. Yongsin present.
target_date = "1984-01-29"
target_time = "18:30"
gender = "female"

analyzer = SajuAnalyzer(target_date, target_time, gender)
result = analyzer.get_result_json()

print(f"=== TEST DATE: {target_date} {target_time} ===")
# Pillars
print(f"Year: {result['four_pillars']['year']['text']} ({result['four_pillars']['year']['ji']})")
print(f"Day: {result['four_pillars']['day']['text']} ({result['four_pillars']['day']['ji']})")

print("\n=== DAEWOON ===")
print(f"Direction: {result['daewoon']['direction']}")
print(f"First Age: {result['daewoon']['pillars'][0]['age']}")

print("\n=== SINSAL ===")
print("Year Ji:", result['sinsal']['year']['ji'])
print("Month Ji:", result['sinsal']['month']['ji'])
print("Day Ji:", result['sinsal']['day']['ji'])
print("Hour Ji:", result['sinsal']['hour']['ji'])

print("\n=== YONGSIN ===")
print("Verdict:", result['strength']['verdict'])
print("Yongsin:", result['yongsin_structure']['primary']['element'])
