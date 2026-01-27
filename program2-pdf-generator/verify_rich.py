import sys
sys.path.append("../program1-calculator")
from saju_app import SajuAnalyzer
import json

# Test Case: 1994-04-20 08:30 Female (User's example)
target_date = "1994-04-20"
target_time = "08:30"
gender = "female"
name = "이정민"

analyzer = SajuAnalyzer(target_date, target_time, gender, name, calendar_type='solar')
result = analyzer.get_result_json()

print("=== RICH DATA CHECK ===")
fp_year = result['four_pillars']['year']
print(f"Year Gan Desc: {fp_year.get('gan_desc', 'MISSING')}")
print(f"Year Ji Desc: {fp_year.get('ji_desc', 'MISSING')}")
print(f"Pillar Desc: {fp_year.get('pillar_desc', 'MISSING')}")

print("\n=== SIBSEONG DETAILS CHECK ===")
print(json.dumps(result.get('sibseong_details', {}), indent=2, ensure_ascii=False))

print("\n=== SINSAL DETAILS CHECK ===")
print(json.dumps(result.get('sinsal_details', {}), indent=2, ensure_ascii=False))

print("\n=== INTERACTION DETAILS CHECK ===")
print(json.dumps(result.get('interaction_details', []), indent=2, ensure_ascii=False))
