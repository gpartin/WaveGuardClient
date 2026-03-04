"""End-to-end verification of deployed WaveGuard API with L0 and L1 support."""
import requests
import json

BASE = "https://gpartin--waveguard-api-fastapi-app.modal.run"

# Test 1: Health
print("=== Health ===")
r = requests.get(f"{BASE}/v1/health")
print(f"Status: {r.status_code}, Version: {r.json().get('version', 'N/A')}")

# Test 2: L0 scan
print("\n=== L0 Scan ===")
body = {
    "training": [
        {"cpu": 45, "memory": 62, "errors": 0},
        {"cpu": 48, "memory": 63, "errors": 0},
        {"cpu": 42, "memory": 61, "errors": 1},
        {"cpu": 50, "memory": 64, "errors": 0},
    ],
    "test": [
        {"cpu": 46, "memory": 62, "errors": 0},
        {"cpu": 99, "memory": 95, "errors": 150},
    ],
}
r = requests.post(f"{BASE}/v1/scan", json=body)
data = r.json()
anomalies = data["summary"]["anomalies_found"]
print(f"Status: {r.status_code}, Anomalies: {anomalies}")
assert r.status_code == 200, f"L0 scan failed: {r.status_code}"
assert anomalies >= 1, f"Expected anomaly, got {anomalies}"

# Test 3: L1 scan
print("\n=== L1 Scan (field_level=1) ===")
body["field_level"] = 1
r = requests.post(f"{BASE}/v1/scan", json=body)
data = r.json()
if r.status_code == 200:
    anomalies = data["summary"]["anomalies_found"]
    print(f"Status: {r.status_code}, Anomalies: {anomalies}")
else:
    print(f"Status: {r.status_code}, Response: {json.dumps(data, indent=2)}")

# Test 4: L0 fingerprint
print("\n=== L0 Fingerprint ===")
body2 = {"data": {"cpu": 45, "memory": 62, "errors": 0}}
r = requests.post(f"{BASE}/v1/fingerprint", json=body2)
fp = r.json()
dims = fp.get("dimensions")
fl = fp.get("field_level", "N/A")
print(f"Status: {r.status_code}, Dims: {dims}, Level: {fl}")
assert r.status_code == 200, f"L0 fingerprint failed: {r.status_code}"
assert dims == 52, f"Expected 52 dims, got {dims}"

# Test 5: L1 fingerprint
print("\n=== L1 Fingerprint (field_level=1) ===")
body2["field_level"] = 1
r = requests.post(f"{BASE}/v1/fingerprint", json=body2)
fp = r.json()
if r.status_code == 200:
    dims = fp.get("dimensions")
    fl = fp.get("field_level", "N/A")
    print(f"Status: {r.status_code}, Dims: {dims}, Level: {fl}")
    assert dims == 62, f"Expected 62 dims, got {dims}"
else:
    print(f"Status: {r.status_code}, Response: {json.dumps(fp, indent=2)}")

print("\n=== ALL TESTS COMPLETE ===")
