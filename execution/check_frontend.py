import urllib.request
import sys

def check_frontend():
    """
    Checks if the Next.js frontend at localhost:3000 is accessible.
    """
    url = "http://localhost:3000"
    print(f"Checking Frontend Status: {url}")
    
    try:
        with urllib.request.urlopen(url, timeout=3) as response:
            if response.status == 200:
                print("✅ Frontend is Running (200 OK)")
                # Read a bit of content to ensure it's not an empty page
                content = response.read(1000).decode('utf-8')
                if "<html" in content or "<!DOCTYPE" in content:
                    print("   Content looks like valid HTML.")
                    return True
                else:
                    print("⚠️  Status is 200, but content looks suspicious.")
                    return False
            else:
                print(f"❌ Frontend returned status code: {response.status}")
                return False

    except urllib.error.URLError as e:
        print(f"❌ Connection Error: {e.reason}")
        print("   Is the Next.js server running? (try: npm run dev)")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False

if __name__ == "__main__":
    success = check_frontend()
    sys.exit(0 if success else 1)
