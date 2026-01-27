import urllib.request
import json
import sys

def test_saju_analysis():
    url = "http://localhost:8000/api/analyze"
    payload = {
        "name": "Test User",
        "gender": "male",
        "year": 1974,
        "month": 12,
        "day": 17,
        "hour": 12,
        "minute": 30,
        "calendarType": "solar",
        "isLeapMonth": False,
        "location": "서울"
    }

    print(f"Sending request to {url} with payload: {payload}")
    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req) as response:
            res_body = response.read().decode('utf-8')
            data = json.loads(res_body)
            
            print("\n=== Analysis Result ===")
            info = data.get('info', {})
            print(f"Name: {info.get('name')}")
            print(f"Date: {info.get('solar_date')}")
            
            pillars = data.get('four_pillars', {})
            print(f"Year: {pillars.get('year', {}).get('text')}")
            print(f"Month: {pillars.get('month', {}).get('text')}")
            print(f"Day: {pillars.get('day', {}).get('text')}")
            print(f"Hour: {pillars.get('hour', {}).get('text')}")
            
            # Check Top-Level Sinsal
            sinsal = data.get('sinsal')
            if sinsal:
                print("\n✅ 'sinsal' found at top level.")
                for p in ['year', 'month', 'day', 'hour']:
                    stars = sinsal.get(p, {})
                    print(f"  - {p.title()} Sinsal: Gan={stars.get('gan')}, Ji={stars.get('ji')}")
            else:
                 print("\n❌ 'sinsal' MISSING at top level.")

            # Check Derived just in case
            derived = data.get('derived', {})
            if derived:
                print("\nDerived found (unexpectedly?):", list(derived.keys()))

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_saju_analysis()
