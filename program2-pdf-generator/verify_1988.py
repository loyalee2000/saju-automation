import sys
sys.path.append("../program1-calculator")
from saju_app import SajuAnalyzer
import json

# User Data: 1988-02-18 17:00 Female
# Note: Input is Solar.
analyzer = SajuAnalyzer("1988-02-18", "17:00", "female")
result = analyzer.get_result_json()

print("=== DEWOON VERIFICATION ===")
daewoon = result['daewoon']
print(f"Direction: {daewoon['direction']}")
print(f"First Daewoon Age: {daewoon['pillars'][0]['age']}") # Expected 4, Current likely 5
print(f"First Daewoon Ganji: {daewoon['pillars'][0]['ganji']}")

print("\n=== SINSAL VERIFICATION ===")
print("Month Gan Sinsal:", result['sinsal']['month']['gan']) # Expected contains '현침살'
print("Day Ji Sinsal:", result['sinsal']['day']['ji'])   # Expected contains '천을귀인', '문창귀인', '학당귀인', '천주귀인', '도화살', '현침살', '귀문관살'
print("Hour Ji Sinsal:", result['sinsal']['hour']['ji']) # Expected contains '관귀학관', ...

print("\n=== FULL SINSAL JSON ===")
print(json.dumps(result['sinsal'], indent=2, ensure_ascii=False))
