# AI-Based Intrusion & Behavior Anomaly Detector

## Features
- Real-time login anomaly detection (typing speed, device fingerprint, location, access time)
- AI/ML-based anomaly scoring
- Real-time alerts and risk-score dashboard
- Automatic account lock or re-authentication on high risk
- REST API and WebSocket for alerts
- Modern React frontend dashboard
- Docker Compose for local deployment

## Quickstart
1. Install Docker and Docker Compose
2. Run: `docker-compose up --build`
3. Access backend at http://localhost:8000, frontend at http://localhost:3000

## API
- POST `/api/login_event` — submit login event
- GET `/api/alerts` — list alerts
- WS `/ws/alerts` — stream alerts

## Example login event JSON
```
{
  "event_id": "evt-001",
  "timestamp": "2025-11-28T10:00:00Z",
  "username": "alice",
  "device_fingerprint": "dev-abc",
  "location": "IN",
  "typing_speed": 180.0,
  "access_time": "10:00"
}
```
