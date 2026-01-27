import sys
import os
import math
from datetime import datetime

sys.path.append(os.path.abspath("../program1-calculator"))
from saju_app import SajuAnalyzer, SolarTermCalculator

# Test case: 홍지수 1987-02-18 00:30 Female
print("=== 대운수 계산 디버그 (홍지수) ===")
print("생년월일시: 1987-02-18 00:30")
print("성별: 여성")
print()

a = SajuAnalyzer("1987-02-18", "00:30", "solar", "홍지수", "female")

pillars = a.get_gan_ji()
year_gan = pillars['year'][0]
print(f"년간: {year_gan} (정 = 음간)")
print(f"대운 방향: 순행 (음간 + 여성)")
print()

st = SolarTermCalculator()

# February Jeolgi
current_jeolgi = st.find_jeolgi_time(1987, 2)  # 입춘 around Feb 4
next_month_jeolgi = st.find_jeolgi_time(1987, 3)  # 경칩 around Mar 6

print(f"2월 절기 (입춘): {current_jeolgi}")
print(f"3월 절기 (경칩): {next_month_jeolgi}")

birth_dt = datetime(1987, 2, 18, 0, 30)
print(f"생일: {birth_dt}")
print()

# Is birth after current Jeolgi (입춘)?
is_after_current = birth_dt >= current_jeolgi
print(f"2월 절기(입춘) 이후 출생?: {is_after_current}")

# For forward (순행): calculate to NEXT Jeolgi
if is_after_current:
    # Next Jeolgi is 경칩 (March)
    diff_seconds = (next_month_jeolgi - birth_dt).total_seconds()
    print(f"계산: next_jeolgi - birth = {diff_seconds}초")
else:
    # Next Jeolgi is 입춘 itself
    diff_seconds = (current_jeolgi - birth_dt).total_seconds()
    print(f"계산: current_jeolgi - birth = {diff_seconds}초")

diff_days = diff_seconds / (24 * 3600)
print(f"일수 차이: {diff_days:.2f}일")
print()

daewoon_floor = int(diff_days / 3)
daewoon_round = int(round(diff_days / 3))
daewoon_ceil = int(math.ceil(diff_days / 3))

print(f"일수 / 3 = {diff_days / 3:.2f}")
print(f"floor() 결과: {daewoon_floor}")
print(f"round() 결과: {daewoon_round}")
print(f"ceil() 결과: {daewoon_ceil}")
print()

actual_result = a._calculate_daewoon_num(True)  # True = forward
print(f"실제 _calculate_daewoon_num(순행) 결과: {actual_result}")
print()
print(">>> 포스텔러 결과: 5")
