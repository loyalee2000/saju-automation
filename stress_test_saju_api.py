import urllib.request
import json
import random
import time
import sys
from datetime import datetime

def generate_random_case(idx):
    year = random.randint(1950, 2024)
    month = random.randint(1, 12)
    # Simple day generation to avoid invalid dates
    day = random.randint(1, 28) 
    hour = random.randint(0, 23)
    minute = random.randint(0, 59)
    gender = random.choice(["male", "female"])
    
    return {
        "name": f"TestUser_{idx}",
        "gender": gender,
        "year": year,
        "month": month,
        "day": day,
        "hour": hour,
        "minute": minute,
        "calendarType": "solar",
        "isLeapMonth": False,
        "location": "서울"
    }

def validate_response(data):
    # Check for essential keys matching our new type definition
    required_keys = ['info', 'four_pillars', 'five_elements', 'daewoon', 'sinsal']
    missing = [k for k in required_keys if k not in data]
    
    if missing:
        return False, f"Missing top-level keys: {missing}"
    
    # Check Sinsal structure (essential for recent fixes)
    sinsal = data.get('sinsal')
    if not isinstance(sinsal, dict):
        return False, "Sinsal is not a dict"
        
    for p in ['year', 'month', 'day', 'hour']:
        if p not in sinsal:
            return False, f"Sinsal missing pillar '{p}'"
            
    return True, "OK"

def run_stress_test(count=100):
    url = "http://localhost:8000/api/analyze"
    print(f"🚀 Starting Stress Test: {count} cases...")
    
    success_count = 0
    fail_count = 0
    errors = []
    
    start_time = time.time()
    
    for i in range(count):
        payload = generate_random_case(i + 1)
        try:
            data_json = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(url, data=data_json, headers={'Content-Type': 'application/json'})
            
            with urllib.request.urlopen(req) as response:
                if response.status != 200:
                    fail_count += 1
                    errors.append(f"Case {i+1}: HTTP {response.status}")
                    continue
                    
                res_body = response.read().decode('utf-8')
                data = json.loads(res_body)
                
                is_valid, msg = validate_response(data)
                if is_valid:
                    success_count += 1
                    # print(f"✅ Case {i+1} ({payload['year']}-{payload['month']}-{payload['day']}): OK")
                else:
                    fail_count += 1
                    errors.append(f"Case {i+1} Validation Error: {msg}")
                    print(f"❌ Case {i+1} Failed: {msg}")

        except Exception as e:
            fail_count += 1
            errors.append(f"Case {i+1} Exception: {str(e)}")
            print(f"❌ Case {i+1} Exception: {e}")
            
        if (i + 1) % 10 == 0:
            print(f"Progress: {i + 1}/{count}...")

    duration = time.time() - start_time
    
    print("\n" + "="*30)
    print(f"📊 Test Summary ({count} cases)")
    print(f"Total Time: {duration:.2f}s")
    print(f"✅ Success: {success_count}")
    print(f"❌ Failed: {fail_count}")
    
    if errors:
        print("\nErrors:")
        for e in errors[:10]: # Validating first 10 errors
            print(f" - {e}")
        if len(errors) > 10:
            print(f" ... and {len(errors) - 10} more.")
            
    if fail_count == 0:
        print("\n✨ ALL TESTS PASSED! System is robust.")
    else:
        print("\n⚠️ SYSTEM HAS ISSUES. Inspect errors.")

if __name__ == "__main__":
    run_stress_test(100)
