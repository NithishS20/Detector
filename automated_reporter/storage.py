import json
import os
from typing import Dict, Any, List

PROFILES_PATH = os.path.join(os.path.dirname(__file__), 'profiles.json')

DEFAULT_PROFILES = {}

def load_profiles() -> Dict[str, Any]:
    if not os.path.exists(PROFILES_PATH):
        return DEFAULT_PROFILES.copy()
    try:
        with open(PROFILES_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return DEFAULT_PROFILES.copy()

def save_profiles(profiles: Dict[str, Any]):
    with open(PROFILES_PATH, 'w', encoding='utf-8') as f:
        json.dump(profiles, f, indent=2)

def make_profile_from_events(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    # Compute simple aggregates: avg typing_speed, unique device fingerprints, locations, typical hours
    typing_values = [e.get('typing_speed') for e in events if e.get('typing_speed') is not None]
    device_set = list({e.get('device_fingerprint') for e in events if e.get('device_fingerprint')})
    loc_set = list({e.get('location') for e in events if e.get('location')})
    ua_set = list({e.get('user_agent') for e in events if e.get('user_agent')})
    ip_set = list({e.get('ip_address') for e in events if e.get('ip_address')})
    hours = [
        int(e.get('access_time')[11:13])
        for e in events
        if e.get('access_time') and len(e.get('access_time')) >= 13
    ]
    avg_typing = sum(typing_values) / len(typing_values) if typing_values else None
    std_typing = (sum((x - avg_typing) ** 2 for x in typing_values) / len(typing_values)) ** 0.5 if typing_values and len(typing_values) > 1 else None
    hour_counts = {}
    for h in hours:
        hour_counts[h] = hour_counts.get(h, 0) + 1
    # identify typical hour range as hours with occurrences
    typical_hours = sorted(hour_counts.keys())

    profile = {
        'avg_typing_speed': avg_typing,
        'std_typing_speed': std_typing,
        'device_fingerprints': device_set,
        'locations': loc_set,
        'user_agents': ua_set,
        'ip_addresses': ip_set,
        'typical_hours': typical_hours,
        'samples': len(events)
    }
    return profile

def update_profile_incremental(profile: Dict[str, Any], event: Dict[str, Any]) -> Dict[str, Any]:
    # Update averages conservatively
    samples = profile.get('samples', 0)
    if event.get('typing_speed') is not None:
        if profile.get('avg_typing_speed') is None:
            profile['avg_typing_speed'] = event['typing_speed']
            profile['std_typing_speed'] = None
        else:
            # incremental average
            new_avg = (profile['avg_typing_speed'] * samples + event['typing_speed']) / (samples + 1)
            # naive std update omitted for simplicity
            profile['avg_typing_speed'] = new_avg
    if event.get('device_fingerprint'):
        if event['device_fingerprint'] not in profile.get('device_fingerprints', []):
            profile.setdefault('device_fingerprints', []).append(event['device_fingerprint'])
    if event.get('user_agent'):
        if event['user_agent'] not in profile.get('user_agents', []):
            profile.setdefault('user_agents', []).append(event['user_agent'])
    if event.get('ip_address'):
        if event['ip_address'] not in profile.get('ip_addresses', []):
            profile.setdefault('ip_addresses', []).append(event['ip_address'])
    if event.get('location'):
        if event['location'] not in profile.get('locations', []):
            profile.setdefault('locations', []).append(event['location'])
    if event.get('access_time') and len(event['access_time']) >= 13:
        try:
            h = int(event['access_time'][11:13])
            if 'typical_hours' not in profile:
                profile['typical_hours'] = [h]
            elif h not in profile['typical_hours']:
                profile['typical_hours'].append(h)
                profile['typical_hours'].sort()
        except Exception:
            pass
    profile['samples'] = samples + 1
    return profile

