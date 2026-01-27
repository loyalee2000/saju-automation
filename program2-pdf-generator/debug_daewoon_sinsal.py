import sys
import os
import datetime

sys.path.append(os.path.abspath("../program1-calculator"))
from saju_app import SajuAnalyzer

# Provide dummy date
a = SajuAnalyzer("1980-10-03")

try:
    # 1980-10-03
    prev_j = a._find_previous_jeolgi_date_pycal(1980, 10, 3)
    next_j = a._find_next_jeolgi_date_pycal(1980, 10, 3)
    print(f"Prev Jeolgi: {prev_j}")
    print(f"Next Jeolgi: {next_j}")
    
    birth = datetime.datetime(1980, 10, 3, 14, 30)
    
    diff_days = (birth - prev_j).total_seconds() / 86400
    print(f"Diff Days (Reverse): {diff_days}")
    print(f"Divided by 3: {diff_days/3}")
    print(f"Round: {round(diff_days/3)}")
    
except Exception as e:
    print(f"Error in Jeolgi: {e}")

print("\n--- Sinsal Logic ---")
print("Cheoneui Logic Check ('유', '신'):")
if hasattr(a, '_calculate_cheoneui'):
    print(f"Result: {a._calculate_cheoneui('유', '신')}")
else:
    print("Method _calculate_cheoneui missing.")
    
print(f"Hyunchim '미': {a._calculate_hyunchim('미')}")
