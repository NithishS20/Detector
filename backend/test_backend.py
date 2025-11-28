import requests

def test_login_event():
    url = "http://localhost:8000/api/login_event"
    event = {
        "event_id": "evt-test",
        "timestamp": "2025-11-28T10:00:00Z",
        "username": "alice",
        "device_fingerprint": "dev-abc",
        "location": "RU",
        "typing_speed": 250.0,
        "access_time": "10:00"
    }
    r = requests.post(url, json=event)
    assert r.status_code == 200
    data = r.json()
    assert data["severity"] == "high"
    assert data["action"] == "lock_account"

def test_alerts():
    url = "http://localhost:8000/api/alerts"
    r = requests.get(url)
    assert r.status_code == 200
    assert isinstance(r.json(), list)
