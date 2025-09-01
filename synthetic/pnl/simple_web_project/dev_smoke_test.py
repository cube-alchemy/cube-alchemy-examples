import requests
import time

BASE = "http://localhost:8000"

print("Creating cube...")
r = requests.post(f"{BASE}/cube/new")
r.raise_for_status()
cube_id = r.json()["cube_id"]
print("cube_id:", cube_id)

print("Calling cube.plot() (may return empty plot or image placeholder)...")
r = requests.post(f"{BASE}/cube/call", json={
    "cube_id": cube_id,
    "method": "plot",
    "args": ["PNL"],
})
print(r.status_code, r.text)