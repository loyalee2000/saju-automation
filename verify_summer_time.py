import urllib.request
import json
import time

def test_summer_time():
    url = "http://localhost:8000/api/analyze"
    
    # known Summer Time Period: 1988-05-08 ~ 1988-10-09
    # Test Date: 1988-05-15 (Sunday)
    # Test Time: 13:30 (1:30 PM)
    # If Summer Time applies, adjusted time should be 12:30.
    # Hour Pillar Change?
    # 13:30 (Sheep/Mi time usually starts 13:30 in Korea standard longitude, or 13:00? 
    # Sa/O/Mi time boundaries:
    # O (Horse): 11:30 ~ 13:30
    # Mi (Sheep): 13:30 ~ 15:30
    #
    # If Input=13:30, and No Adjustment -> 13:30 is exact boundary or start of Mi time.
    # If Input=13:30, Adjusted(-1hr)=12:30 -> 12:30 is middle of O (Horse) time.
    #
    # So if implemented: Pillar should be O (Horse).
    # If NOT implemented: Pillar likely Mi (Sheep).
    
    payload = {
        "name": "SummerTimeTest",
        "gender": "male",
        "year": 1988,
        "month": 5,
        "day": 15,
        "hour": 13,
        "minute": 40, # 13:40 -> Adjusted 12:40 (O/Horse). Unadjusted 13:40 (Mi/Sheep).
        "calendarType": "solar",
        "isLeapMonth": False,
        "location": "서울"
    }

    print(f"Sending request for Summer Time Case: {payload['year']}-{payload['month']}-{payload['day']} {payload['hour']}:{payload['minute']}")
    
    try:
        data_json = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data_json, headers={'Content-Type': 'application/json'})
        
        with urllib.request.urlopen(req) as response:
            res_body = response.read().decode('utf-8')
            data = json.loads(res_body)
            
            pillars = data.get('four_pillars', {})
            hour_pillar = pillars.get('hour', {}).get('text', '')
            
            print(f"\nResult Hour Pillar: {hour_pillar}")
            
            # Expected: Horse (오)
            # Unadjusted: Sheep (미)
            
            if "오(午)" in hour_pillar:
                print("✅ Summer Time Applied Correctly (adjusted to Horse time).")
                print("info.summer_time:", data.get('info', {}).get('summer_time_applied'))
            elif "미(未)" in hour_pillar:
                print("❌ Summer Time NOT Applied (remained Sheep time).")
            else:
                print(f"❓ Unexpected Hour Pillar: {hour_pillar}. Please check manually.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_summer_time()
