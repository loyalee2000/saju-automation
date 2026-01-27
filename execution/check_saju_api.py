import urllib.request
import json
import sys

def check_saju_api():
    """
    Checks if the Saju API is running and returning valid data.
    """
    url = "http://localhost:8000/api/analyze"
    payload = {
        "name": "Health Check",
        "gender": "male",
        "year": 1990,
        "month": 1,
        "day": 1,
        "hour": 12,
        "minute": 0,
        "calendarType": "solar",
        "isLeapMonth": False,
        "location": "서울"
    }

    print(f"Checking API Status: {url}")
    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                res_body = response.read().decode('utf-8')
                result = json.loads(res_body)
                print("✅ API is responding correctly.")
                print(f"   Name in response: {result.get('info', {}).get('name')}")
                return True
            else:
                print(f"❌ API returned status code: {response.status}")
                return False

    except urllib.error.URLError as e:
        print(f"❌ API Connection Error: {e.reason}")
        print("   Is the backend server running? (try: uvicorn saju_app:app --reload)")
        return False
    except json.JSONDecodeError:
        print("❌ API returned invalid JSON.")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False

if __name__ == "__main__":
    success = check_saju_api()
    sys.exit(0 if success else 1)
