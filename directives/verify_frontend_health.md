# Directive: Verify Frontend Health

## Goal
Confirm that the Next.js frontend application is up and accessible.

## Inputs
None. Checks local default port 3000.

## Execution Steps
1. Run `execution/check_frontend.py`.

## Expected Output
- **Success**: "✅ Frontend is Running (200 OK)"
- **Failure**: "❌ Connection Error" (Usually means `npm run dev` isn't running).

## When to use
- Before starting development to ensure environment is ready.
- After making significant config changes (e.g. `next.config.js`) to ensure server restarted correctly.
