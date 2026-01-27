# Directive: Verify Saju API Status

## Goal
Check if the Saju backend API is running and functioning correctly.

## Inputs
None required. The script uses default test data.

## Execution Steps
1. Run the `execution/check_saju_api.py` script.
2. Observe the output.

## Expected Output
- **Success**: "✅ API is responding correctly." message.
- **Failure**: Error message indicating connection refusal or invalid response.

## Troubleshooting
- If connection fails, ensure the backend server is started (`uvicorn saju_app:app --reload` in `saju-web-backend`).
- If port differs, update the script url.
