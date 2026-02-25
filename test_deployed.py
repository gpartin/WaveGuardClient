"""Quick smoke test against deployed Modal API + SDK client."""
import json
import urllib.request

API = "https://gpartin--waveguard-api-fastapi-app.modal.run"

training = [
    {"cpu": 45, "mem": 62, "err": 0},
    {"cpu": 48, "mem": 63, "err": 0},
    {"cpu": 42, "mem": 61, "err": 1},
    {"cpu": 50, "mem": 64, "err": 0},
]
test_samples = [
    {"cpu": 46, "mem": 62, "err": 0},     # normal
    {"cpu": 99, "mem": 95, "err": 150},    # anomaly
]

# ── Test 1: Direct API call ──
print("=" * 60)
print("TEST 1: Direct API /v1/scan")
print("=" * 60)
payload = json.dumps({"training": training, "test": test_samples}).encode()
req = urllib.request.Request(
    f"{API}/v1/scan",
    data=payload,
    headers={"Content-Type": "application/json"},
)
resp = json.loads(urllib.request.urlopen(req, timeout=60).read())
print(f"Version: {resp.get('version', '?')}")
for i, r in enumerate(resp["results"]):
    ga = r.get("global_anomaly", "N/A")
    fa = r.get("feature_anomaly", "N/A")
    af = r.get("anomalous_features", "N/A")
    print(f"  Sample {i}: anomaly={r['is_anomaly']}  score={r['score']:.3f}  "
          f"global={ga}  feat={fa}  anomalous_features={af}")

assert not resp["results"][0]["is_anomaly"], "Normal sample flagged!"
assert resp["results"][1]["is_anomaly"], "Anomaly not detected!"
assert "global_anomaly" in resp["results"][0], "Missing global_anomaly field!"
assert "feature_anomaly" in resp["results"][0], "Missing feature_anomaly field!"
assert "anomalous_features" in resp["results"][0], "Missing anomalous_features field!"
print("PASS\n")

# ── Test 2: SDK client ──
print("=" * 60)
print("TEST 2: WaveGuardClient SDK")
print("=" * 60)
from waveguard import WaveGuard

wg = WaveGuard()
result = wg.scan(training=training, test=test_samples)
print(f"  SDK returned {len(result.results)} results")
for i, r in enumerate(result.results):
    print(f"  Sample {i}: anomaly={r.is_anomaly}  score={r.score:.3f}  confidence={r.confidence:.3f}")

assert not result.results[0].is_anomaly, "SDK: Normal flagged!"
assert result.results[1].is_anomaly, "SDK: Anomaly missed!"
print("PASS\n")

# ── Test 3: Health endpoint ──
print("=" * 60)
print("TEST 3: Health check")
print("=" * 60)
health = wg.health()
print(f"  Status: {health.status}  Version: {health.version}")
assert health.version == "2.2.0", f"Wrong version: {health.version}"
print("PASS\n")

print("=" * 60)
print("ALL TESTS PASSED - v2.2.0 deployed and working")
print("=" * 60)
