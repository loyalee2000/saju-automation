import sys
sys.path.append("../program1-calculator")
from saju_app import SajuAnalyzer
import json

# User Data: 1984-04-22 09:00 Male
analyzer = SajuAnalyzer("1984-04-22", "09:00", "male")
result = analyzer.get_result_json()

print("=== DEWOON VERIFICATION ===")
daewoon = result['daewoon']
print(f"Direction: {daewoon['direction']}")
print(f"First Daewoon Age: {daewoon['pillars'][0]['age']}") # Should be 4
print(f"First Daewoon Ganji: {daewoon['pillars'][0]['ganji']}")

print("\n=== SINSAL VERIFICATION ===")
print(json.dumps(result['sinsal'], indent=2, ensure_ascii=False))
