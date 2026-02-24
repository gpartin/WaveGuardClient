"""
Example 1: Quickstart — detect anomalies in 30 seconds.

WaveGuard finds anomalies with ONE API call:
  1. Send normal data (training) + suspect data (test)
  2. Get back per-sample anomaly scores
  3. Done — nothing stored, fully stateless

Usage:
    export WAVEGUARD_API_KEY="your-key"
    python 01_quickstart.py
"""

import os
from waveguard import WaveGuard

# ── Initialize client ─────────────────────────────────────────────────────
api_key = os.environ.get("WAVEGUARD_API_KEY", "demo")
wg = WaveGuard(api_key=api_key)

# ── Check API health first ────────────────────────────────────────────────
health = wg.health()
print(f"API Status: {health.status} | Version: {health.version} | GPU: {health.gpu}")
print()

# ── Define training data (what "normal" looks like) ───────────────────────
training = [
    {"cpu": 45, "memory": 62, "disk_io": 120, "errors": 0},
    {"cpu": 48, "memory": 63, "disk_io": 115, "errors": 0},
    {"cpu": 42, "memory": 61, "disk_io": 125, "errors": 1},
    {"cpu": 50, "memory": 64, "disk_io": 118, "errors": 0},
    {"cpu": 47, "memory": 63, "disk_io": 122, "errors": 0},
]

# ── Define test data (what you want to check) ────────────────────────────
test = [
    {"cpu": 46, "memory": 62, "disk_io": 119, "errors": 0},    # looks normal
    {"cpu": 99, "memory": 95, "disk_io": 800, "errors": 150},   # looks anomalous
    {"cpu": 44, "memory": 60, "disk_io": 121, "errors": 0},    # looks normal
]

# ── Scan! ─────────────────────────────────────────────────────────────────
result = wg.scan(training=training, test=test)

# ── Print results ─────────────────────────────────────────────────────────
print(f"Scanned {result.summary.total_test_samples} samples")
print(f"Anomalies found: {result.summary.anomalies_found}")
print(f"Total latency: {result.summary.total_latency_ms:.0f}ms")
print(f"Encoder used: {result.summary.encoder_type}")
print()

for i, r in enumerate(result.results):
    status = "🚨 ANOMALY" if r.is_anomaly else "✅ Normal"
    print(f"  Sample {i}: {status}")
    print(f"    Score: {r.score:.2f} (threshold: {r.threshold:.2f})")
    print(f"    Confidence: {r.confidence:.0%}")
    print(f"    Mahalanobis distance: {r.mahalanobis_distance:.2f}")

    if r.is_anomaly and r.top_features:
        print(f"    Top features driving anomaly:")
        for feat in r.top_features[:3]:
            print(f"      - {feat.label}: z-score = {feat.z_score:.1f}")
    print()
