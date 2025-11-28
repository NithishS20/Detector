import json
import httpx


import json
import httpx
import os

# Always resolve path relative to project root
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
events_path = os.path.join(root, 'synthetic_events.json')
if not os.path.exists(events_path):
    # fallback: try current working directory
    events_path = os.path.abspath('synthetic_events.json')
with open(events_path) as f:
    events = json.load(f)

for event in events:
    r = httpx.post('http://localhost:8000/api/login_event', json=event)
    print(f"Sent event {event['event_id']}: status {r.status_code}")
    if r.status_code == 200 and 'alert_id' in r.text:
        print('  Alert:', r.text)
