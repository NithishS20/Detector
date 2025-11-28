import random, uuid, datetime, json

locations = ["IN", "US", "UK", "RU", "CN", "BR"]
users = ["alice", "bob", "carol", "eve"]

def generate_event():
    return {
        "event_id": str(uuid.uuid4()),
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "username": random.choice(users),
        "device_fingerprint": f"dev-{random.randint(100,999)}",
        "location": random.choice(locations),
        "typing_speed": random.gauss(160, 40),
        "access_time": f"{random.randint(0,23):02d}:{random.randint(0,59):02d}"
    }

def generate_attack():
    # Simulate stolen credential attack: fast typing, odd location
    return {
        "event_id": str(uuid.uuid4()),
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "username": random.choice(users),
        "device_fingerprint": f"dev-{random.randint(100,999)}",
        "location": random.choice(["RU", "CN"]),
        "typing_speed": random.uniform(220, 300),
        "access_time": f"{random.randint(0,23):02d}:{random.randint(0,59):02d}"
    }

if __name__ == "__main__":
    normal = [generate_event() for _ in range(10)]
    attacks = [generate_attack() for _ in range(3)]
    with open("synthetic_events.json", "w") as f:
        json.dump(normal + attacks, f, indent=2)
