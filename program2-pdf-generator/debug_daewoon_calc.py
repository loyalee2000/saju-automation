import sys
import os
import math
from datetime import datetime

sys.path.append(os.path.abspath("../program1-calculator"))
from saju_app import SajuAnalyzer, SolarTermCalculator

# Test case: 정혜진 1980-10-03 14:30 Female
print("=== 대운수 계산 디버그 ===")
print("생년월일시: 1980-10-03 14:30")
print("성별: 여성")
print()

# Create analyzer
a = SajuAnalyzer("1980-10-03", "14:30", "solar", "정혜진", "female")

# Get year stem to determine direction
pillars = a.get_gan_ji()
print(f"사주 원국: {pillars}")
year_pillar = pillars['year']
year_gan = year_pillar[0]  # 경(庚)
print(f"년간: {year_gan}")

# 경(庚) is Yang (index 6 in Cheongan is even -> Yang)
# Female + Yang Year = Reverse (역행)
print(f"대운 방향: 역행 (경금 양간 + 여성)")
print()

# Now trace the Jeolgi calculation
st = SolarTermCalculator()

# Current Jeolgi for October
current_jeolgi = st.find_jeolgi_time(1980, 10)
print(f"10월 절기 (한로): {current_jeolgi}")

# Previous Jeolgi (September = Baeklu)
prev_jeolgi = st.find_jeolgi_time(1980, 9)
print(f"9월 절기 (백로): {prev_jeolgi}")

# Birth datetime
birth_dt = datetime(1980, 10, 3, 14, 30)
print(f"생일: {birth_dt}")
print()

# Is birth after current Jeolgi?
is_after_current = birth_dt >= current_jeolgi
print(f"10월 절기 이후 출생?: {is_after_current}")

# For reverse (역행):
# If after current Jeolgi: diff = birth - current_jeolgi
# If before current Jeolgi: diff = birth - prev_jeolgi

if is_after_current:
    diff_seconds = (birth_dt - current_jeolgi).total_seconds()
    print(f"계산: birth - current_jeolgi = {diff_seconds}초")
else:
    diff_seconds = (birth_dt - prev_jeolgi).total_seconds()
    print(f"계산: birth - prev_jeolgi = {diff_seconds}초")

diff_days = diff_seconds / (24 * 3600)
print(f"일수 차이: {diff_days:.2f}일")
print()

daewoon_round = int(round(diff_days / 3))
daewoon_ceil = int(math.ceil(diff_days / 3))

print(f"일수 / 3 = {diff_days / 3:.2f}")
print(f"round() 결과: {daewoon_round}")
print(f"ceil() 결과: {daewoon_ceil}")
print()

# Call actual method
actual_result = a._calculate_daewoon_num(False)  # False = reverse
print(f"실제 _calculate_daewoon_num(역행) 결과: {actual_result}")
