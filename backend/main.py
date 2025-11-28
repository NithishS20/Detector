from fastapi import FastAPI, WebSocket, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
import uuid
import datetime

app = FastAPI()

# --- Models ---
class LoginEvent(BaseModel):
    event_id: str
    timestamp: str
    username: str
    device_fingerprint: str
    location: str
    typing_speed: float
    access_time: str

class AnomalyAlert(BaseModel):
    alert_id: str
    created_at: str
    severity: str
    score: float
    username: str
    reasons: List[str]
    risk_factors: List[str]
    status: str
    action: Optional[str] = None

class UserSession(BaseModel):
    username: str
    locked: bool = False
    last_location: Optional[str] = None
    last_device_fingerprint: Optional[str] = None
    last_access_time: Optional[str] = None

# --- In-memory store for demo ---
alerts: List[AnomalyAlert] = []
user_sessions: Dict[str, UserSession] = {}

# --- Enhanced anomaly detection logic ---
def detect_anomaly(event: LoginEvent, session: UserSession) -> Optional[AnomalyAlert]:
    reasons = []
    risk_factors = []
    score = 0.0

    # Typing speed anomaly
    if event.typing_speed > 200:
        reasons.append("Unusually high typing speed")
        risk_factors.append("typing_speed")
        score += 0.3

    # Location anomaly
    if event.location not in ["IN", "US", "UK"]:
        reasons.append(f"Unusual login location: {event.location}")
        risk_factors.append("location")
        score += 0.4

    # Device fingerprint change
    if session.last_device_fingerprint and session.last_device_fingerprint != event.device_fingerprint:
        reasons.append("Device fingerprint changed")
        risk_factors.append("device_fingerprint")
        score += 0.3

    # Location shift (sudden change)
    if session.last_location and session.last_location != event.location:
        reasons.append(f"Sudden location shift from {session.last_location} to {event.location}")
        risk_factors.append("location_shift")
        score += 0.4

    # Unusual access time (e.g., late night)
    hour = int(event.access_time.split(":")[0])
    if hour < 6 or hour > 22:
        reasons.append(f"Unusual access time: {event.access_time}")
        risk_factors.append("access_time")
        score += 0.2

    if score >= 0.5:
        severity = "high" if score > 0.8 else "medium"
        action = "lock_account" if severity == "high" else "re_authenticate"
        alert = AnomalyAlert(
            alert_id=f"A-{datetime.datetime.utcnow().strftime('%Y%m%d')}-{str(uuid.uuid4())[:6]}",
            created_at=datetime.datetime.utcnow().isoformat() + "Z",
            severity=severity,
            score=score,
            username=event.username,
            reasons=reasons,
            risk_factors=risk_factors,
            status="new",
            action=action
        )
        return alert
    return None

@app.post("/api/login_event")
async def login_event(event: LoginEvent):
    session = user_sessions.get(event.username, UserSession(username=event.username))
    if session.locked:
        raise HTTPException(status_code=403, detail="Account is locked due to suspicious activity")
    alert = detect_anomaly(event, session)
    if alert:
        alerts.append(alert)
        if alert.action == "lock_account":
            session.locked = True
        # Update session with last values
        session.last_location = event.location
        session.last_device_fingerprint = event.device_fingerprint
        session.last_access_time = event.access_time
        user_sessions[event.username] = session
        return JSONResponse(alert.dict())
    # Update session even if no alert
    session.last_location = event.location
    session.last_device_fingerprint = event.device_fingerprint
    session.last_access_time = event.access_time
    user_sessions[event.username] = session
    return {"result": "ok"}

@app.post("/api/unlock_account")
async def unlock_account(username: str):
    if username in user_sessions:
        user_sessions[username].locked = False
        return {"result": "Account unlocked"}
    raise HTTPException(status_code=404, detail="User not found")

@app.post("/api/re_authenticate")
async def re_authenticate(username: str):
    # Simulate re-authentication (in real app, send OTP or redirect)
    return {"result": "Re-authentication required", "username": username}

@app.get("/api/sessions")
async def get_sessions():
    return {k: v.dict() for k, v in user_sessions.items()}

@app.get("/api/alerts")
async def get_alerts():
    return [a.dict() for a in alerts]

@app.websocket("/ws/alerts")
async def ws_alerts(websocket: WebSocket):
    await websocket.accept()
    while True:
        # Send new alerts in real-time (for demo, just existing ones)
        for alert in alerts:
            await websocket.send_json(alert.dict())
        await websocket.receive_text()  # Keep connection open
