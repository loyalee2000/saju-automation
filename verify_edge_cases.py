import urllib.request
import json

def run_test(name, payload, expected_desc):
    url = "http://localhost:8000/api/analyze"
    print(f"\n[{name}] Input: {payload['year']}-{payload['month']}-{payload['day']} {payload['hour']}:{payload['minute']}")
    
    try:
        data_json = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data_json, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            pillars = data.get('four_pillars', {})
            
            y = pillars.get('year', {}).get('text', '')
            m = pillars.get('month', {}).get('text', '')
            d = pillars.get('day', {}).get('text', '')
            h = pillars.get('hour', {}).get('text', '')
            
            print(f"Result: {y}년 {m}월 {d}일 {h}시")
            print(f"Expect: {expected_desc}")
            return data
    except Exception as e:
        print(f"Error: {e}")
        return None

def verify_edge_cases():
    print("=== Commercial Accuracy Audit: Edge Cases ===")

    # 1. Ipchun (Year/Month Transition)
    # 1986 Ipchun is Feb 4, 16:08.
    # Before 16:08 -> Year: Eul-Chuk (1985), Month: Gi-Chuk (Jan)
    # After  16:08 -> Year: Byeong-In (1986), Month: Gyeong-In (Feb)
    
    # Case A: 1986-02-04 16:00 (Before)
    run_test("Ipchun PRE", {
        "year": 1986, "month": 2, "day": 4, "hour": 16, "minute": 00,
        "calendarType": "solar", "gender": "male", "name": "IpchunPre"
    }, "Year=을축(1985), Month=기축(Previous)")

    # Case B: 1986-02-04 16:15 (After)
    run_test("Ipchun POST", {
        "year": 1986, "month": 2, "day": 4, "hour": 16, "minute": 15,
        "calendarType": "solar", "gender": "male", "name": "IpchunPost"
    }, "Year=병인(1986), Month=경인(New)")

    # 2. Midnight (Day/Time Transition) & Longitude Correction (-30m)
    # Korea Standard Time (135E) vs Real Time (127.5E) approx -30min.
    # Day switch usually happens at 23:30 (Midnight starts).
    # Date: 2024-01-01 (Gap-Ja Day)
    
    # Case C: 2024-01-01 23:20 -> Adjusted 22:50 (Pig Time, Same Day)
    # Case D: 2024-01-01 23:40 -> Adjusted 23:10 (Rat Time, Start of Next Day? Or Late Rat of Same Day?)
    # Traditional Saju usually treats 23:30 ~ 00:00 as 'Late Rat' (Ya-Ja-Si) belonging to TODAY,
    # or 'Early Rat' (Jo-Ja-Si) belonging to TOMORROW. 
    # Let's see how our engine behaves. *Common commercial standard varies*, but usually 23:30 starts proper Rat time.
    # If using 'Yaja-si': Day Pillar remains, Hour Pillar is Rat.
    # If using 'Joja-si' (Standard): Day Pillar changes to Next Day.
    
    run_test("Midnight A (23:20)", {
        "year": 2024, "month": 1, "day": 1, "hour": 23, "minute": 20,
        "calendarType": "solar", "gender": "male", "name": "MidA"
    }, "Day=Gap-Ja, Hour=Pig(Hae)")

    run_test("Midnight B (23:40)", {
        "year": 2024, "month": 1, "day": 1, "hour": 23, "minute": 40,
        "calendarType": "solar", "gender": "male", "name": "MidB"
    }, "Day=Gap-Ja (if Yaja) or Eul-Chuk (if Joja), Hour=Rat(Ja)")
    
    # 3. Lunar Leap Month
    # 2023 had a Leap Month 2. (Feb 20 ~ Mar 21 is normal Feb, Mar 22 ~ Apr 19 is Leap Feb)
    # Let's verify conversion doesn't crash.
    # Lunar 2023-02-15 (Leap) -> Solar approx 2023-04-05
    run_test("Lunar Leap", {
        "year": 2023, "month": 2, "day": 15, "hour": 12, "minute": 0,
        "calendarType": "lunar", "isLeapMonth": True, "gender": "male", "name": "LeapTest"
    }, "Solar ~2023-04-05, Month=Gap-Jin (Apr) or Gye-Myo (Mar)?")

if __name__ == "__main__":
    verify_edge_cases()
