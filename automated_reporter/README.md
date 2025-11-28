Automated Reporting Server

This small FastAPI server maintains baseline behavior profiles for site users and checks incoming login attempts against these profiles. If an attempt looks suspicious, the server forwards a report to the AI Intrusion & Anomaly Detector backend (`http://localhost:8000/api/login_event`).

Files:
- `main.py` - FastAPI application
- `models.py` - Pydantic models
- `storage.py` - Simple JSON-backed profile storage (`profiles.json` created in same folder)

How it works:
1. Create a baseline profile for a site and username by POSTing to `/profiles` with several `LoginEvent` objects.
2. For each login attempt, POST a `LoginEvent` to `/check`.
3. If the attempt is suspicious (heuristic similarity < 0.6), a report is forwarded to the AI backend.

Example cURL to create profile (send JSON with an `events` array using the schema in models.py):

```powershell
curl -X POST "http://localhost:8100/profiles" -H "Content-Type: application/json" -d @profile.json
```

Example login check:

```powershell
curl -X POST "http://localhost:8100/check" -H "Content-Type: application/json" -d @attempt.json
```

Run locally:

```powershell
cd automated_reporter
# make sure your python venv is activated with FastAPI and httpx installed
python -m uvicorn main:app --reload --port 8100
```

Notes:
- This server uses a simple JSON file `profiles.json` to persist profiles. For production, replace with a real DB.
- The forwarding endpoint assumes the AI backend is available at `http://localhost:8000/api/login_event`.
- The comparison heuristics are intentionally simple; adjust weights and thresholds as needed.
