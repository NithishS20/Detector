from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, Optional
import httpx
import asyncio
import math

from .models import LoginEvent, ProfileCreate, CheckResult
from . import storage

app = FastAPI(title="Automated Reporting Server")

# allow cors from local frontend/backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

AI_BACKEND_URL = "http://localhost:8000/api/login_event"

# Adjustable sensitivity threshold: lower => fewer forwards, higher => more sensitive
SENSITIVITY_THRESHOLD = 0.65

# Enable geo-IP lookups (best-effort; disabled by default to avoid external dependency)
GEOIP_ENABLED = False

profiles = storage.load_profiles()

@app.on_event('shutdown')
def _on_shutdown():
    storage.save_profiles(profiles)

@app.get('/')
def root():
    return {"status": "automated_reporter running"}

@app.post('/profiles')
async def create_profile(payload: ProfileCreate):
    site = payload.site
    username = payload.username
    events = [e.dict() for e in payload.events]
    profiles.setdefault(site, {})
    profile = storage.make_profile_from_events(events)
    profiles[site][username] = profile
    storage.save_profiles(profiles)
    return {"created": True, "site": site, "username": username, "profile": profile}

@app.post('/profiles/{site}/{username}/add_event')
async def add_profile_event(site: str, username: str, event: LoginEvent):
    profiles.setdefault(site, {})
    if username not in profiles[site]:
        profiles[site][username] = storage.make_profile_from_events([event.dict()])
    else:
        storage.update_profile_incremental(profiles[site][username], event.dict())
    storage.save_profiles(profiles)
    return {"updated": True, "site": site, "username": username, "profile": profiles[site][username]}

@app.get('/profiles')
def list_profiles():
    return profiles

@app.get('/profiles/{site}/{username}')
def get_profile(site: str, username: str):
    site_map = profiles.get(site)
    if not site_map or username not in site_map:
        raise HTTPException(status_code=404, detail='profile not found')
    return site_map[username]

async def forward_to_ai_backend(event: Dict[str, Any]):
    # Build payload expected by the AI backend's LoginEvent model
    from uuid import uuid4
    import datetime as _dt
    payload = {
        'event_id': f'evt-{uuid4().hex[:8]}',
        'timestamp': _dt.datetime.utcnow().isoformat() + 'Z',
        'username': event.get('username'),
        'device_fingerprint': event.get('device_fingerprint') or '',
        'location': event.get('location') or '',
        'typing_speed': event.get('typing_speed') or 0.0,
        'access_time': event.get('access_time') or _dt.datetime.utcnow().isoformat() + 'Z'
    }
    # include any extra fields under 'additional' key (exclude keys we've already set)
    known = set(payload.keys())
    payload['additional'] = {k: v for k, v in event.items() if k not in known}
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.post(AI_BACKEND_URL, json=payload)
            return resp.status_code, resp.text
        except Exception as e:
            return None, str(e)

@app.post('/check')
async def check_event(event: LoginEvent, background_tasks: BackgroundTasks):
    site = event.site
    username = event.username
    site_map = profiles.get(site, {})
    profile = site_map.get(username)
    if not profile:
        # No baseline; respond that profile missing
        raise HTTPException(status_code=404, detail='no baseline profile for this site/username')

    # Compute similarity heuristics
    reasons = []
    score_components = []

    # Typing similarity
    avg_t = profile.get('avg_typing_speed')
    std_t = profile.get('std_typing_speed')
    typing_similarity = 1.0
    if avg_t is not None and event.typing_speed is not None:
        diff = abs(event.typing_speed - avg_t)
        # if std available use it, else normalize by avg
        denom = std_t if std_t and std_t > 0 else max(1.0, avg_t)
        typing_similarity = max(0.0, 1.0 - (diff / denom))
        if typing_similarity < 0.6:
            reasons.append(f"Typing speed deviates (got {event.typing_speed}, avg {avg_t})")
    score_components.append(('typing', typing_similarity))

    # Device fingerprint
    device_list = profile.get('device_fingerprints', [])
    device_match = 1.0 if (event.device_fingerprint and event.device_fingerprint in device_list) else 0.0
    if device_match == 0.0:
        reasons.append('Device fingerprint mismatch')
    score_components.append(('device', device_match))

    # User-Agent similarity (simple token/jaccard-based fuzzy match)
    ua_list = profile.get('user_agents', [])
    ua_match = 1.0
    if ua_list and event.user_agent:
        def jaccard(a: str, b: str) -> float:
            sa = set([t for t in a.lower().split() if len(t) > 2])
            sb = set([t for t in b.lower().split() if len(t) > 2])
            if not sa or not sb:
                return 0.0
            inter = sa.intersection(sb)
            union = sa.union(sb)
            return len(inter) / len(union)

        best = 0.0
        for ua in ua_list:
            if not ua:
                continue
            best = max(best, jaccard(ua, event.user_agent))
        # choose threshold for UA similarity
        ua_match = 1.0 if best >= 0.45 else 0.0
        if ua_match == 0.0:
            reasons.append('User-Agent mismatch')
    score_components.append(('ua', ua_match))

    # Location
    locs = profile.get('locations', [])
    loc_match = 1.0 if (event.location and event.location in locs) else 0.0
    if loc_match == 0.0:
        reasons.append(f'Unusual login location: {event.location}')
    score_components.append(('location', loc_match))

    # Time of day
    typical_hours = profile.get('typical_hours', [])
    time_match = 1.0
    if event.access_time and len(event.access_time) >= 13 and typical_hours:
        try:
            hour = int(event.access_time[11:13])
            time_match = 1.0 if hour in typical_hours else 0.0
            if time_match == 0.0:
                reasons.append(f'Unusual login hour: {hour}')
        except Exception:
            time_match = 0.5
    score_components.append(('time', time_match))

    # IP address match (exact or prefix)
    ip_list = profile.get('ip_addresses', [])
    ip_match = 1.0
    if ip_list and event.ip_address:
        ip_match = 0.0
        for ip in ip_list:
            if ip and event.ip_address.startswith(ip):
                ip_match = 1.0
                break
        if ip_match == 0.0:
            reasons.append('IP address mismatch')
    score_components.append(('ip', ip_match))

    # Optional geo-IP check: attempt to resolve country/region and compare against profile locations
    if GEOIP_ENABLED and event.ip_address:
        geo_ok = False
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                r = await client.get(f'http://ip-api.com/json/{event.ip_address}?fields=status,country,regionName')
                if r.status_code == 200:
                    data = r.json()
                    if data.get('status') == 'success':
                        country = data.get('country')
                        region = data.get('regionName')
                        # compare country/region to any known locations in profile (simple substring match)
                        locs = profile.get('locations', [])
                        for loc in locs:
                            if loc and ((country and country in loc) or (region and region in loc) or (loc in country or loc in region)):
                                geo_ok = True
                                break
                        if not geo_ok:
                            reasons.append(f'Geo-IP location {country}/{region} unusual')
        except Exception:
            # best-effort only
            pass

    # Weighted similarity
    # Updated weights include user-agent and ip checks
    weights = {'typing': 0.35, 'device': 0.25, 'location': 0.15, 'time': 0.1, 'ua': 0.1, 'ip': 0.05}
    similarity = 0.0
    for k, val in score_components:
        similarity += weights.get(k, 0) * val

    suspicious = similarity < 0.6

    forwarded = False
    forwarded_status = None
    if suspicious:
        # Build report and forward to AI backend
        report = {
            'username': event.username,
            'site': event.site,
            'device_fingerprint': event.device_fingerprint,
            'typing_speed': event.typing_speed,
            'location': event.location,
            'access_time': event.access_time,
            'user_agent': event.user_agent,
            'ip_address': event.ip_address,
            'source': 'automated_reporter',
            'score': round(1.0 - similarity, 2),
            'reasons': reasons,
            'risk_factors': [r.split()[0].lower() for r in reasons]
        }
        # forward in background
        background_tasks.add_task(forward_to_ai_backend, report)
        forwarded = True

    # Optionally update profile with this event (if desired)
    storage.update_profile_incremental(profile, event.dict())
    storage.save_profiles(profiles)

    return {"suspicious": suspicious, "similarity": round(similarity, 3), "reasons": reasons, "forwarded": forwarded}

# Health endpoint to verify backend connectivity
@app.get('/health')
async def health_check():
    # Try simple connection to AI backend
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            r = await client.get('http://localhost:8000/api/alerts')
            return {"status": "ok", "ai_backend": r.status_code}
        except Exception as e:
            return {"status": "ok", "ai_backend": str(e)}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8100)
