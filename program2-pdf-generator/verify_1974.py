import sys
sys.path.append("../program1-calculator")
from saju_app import SajuAnalyzer
import datetime
import json

# Test Case: 1974-12-17 12:30 Male
target_date = "1974-12-17"
target_time = "12:30"
gender = "male"

analyzer = SajuAnalyzer(target_date, target_time, gender)
result = analyzer.get_result_json()

print(f"=== TEST DATE: {target_date} {target_time} ===")
print(f"Year: {result['four_pillars']['year']['text']} ({result['four_pillars']['year']['ji']})")
print(f"Month: {result['four_pillars']['month']['text']} ({result['four_pillars']['month']['ji']})")
print(f"Day: {result['four_pillars']['day']['text']} ({result['four_pillars']['day']['ji']})")

print("\n=== DAEWOON ===")
print(f"Direction: {result['daewoon']['direction']}")
print(f"First Age: {result['daewoon']['pillars'][0]['age']}")

print("\n=== SINSAL ===")
print("Year Ji:", result['sinsal']['year']['ji'])
print("Month Ji:", result['sinsal']['month']['ji'])
print("Day Ji:", result['sinsal']['day']['ji'])
print("Hour Ji:", result['sinsal']['hour']['ji'])
print("Day Gan:", result['sinsal']['day']['gan'])
