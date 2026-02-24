"""
Example 4: Time Series — detect anomalies in metric streams.

Feed WaveGuard normal time windows and check new windows for anomalies.
Each sample is an array of numbers representing a time window.

Usage:
    export WAVEGUARD_API_KEY="your-key"
    python 04_time_series.py
"""

import os
from waveguard import WaveGuard

api_key = os.environ.get("WAVEGUARD_API_KEY", "demo")
wg = WaveGuard(api_key=api_key)

# ── Normal time windows (stable oscillating metric) ──────────────────────
# Each sample is a 10-point window of a response-time metric (ms)
normal_windows = [
    [45, 48, 42, 50, 47, 44, 49, 46, 43, 51],
    [46, 49, 43, 48, 45, 47, 50, 44, 42, 48],
    [44, 47, 41, 49, 46, 45, 48, 43, 44, 50],
    [47, 50, 44, 51, 48, 46, 49, 45, 43, 49],
    [43, 46, 40, 48, 45, 44, 47, 42, 41, 47],
]

# ── Test windows ──────────────────────────────────────────────────────────
test_windows = [
    # Normal — same statistical shape
    [45, 47, 43, 49, 46, 44, 48, 45, 42, 50],
    # Anomaly — latency spike (sudden sustained increase)
    [45, 48, 120, 350, 500, 480, 510, 490, 520, 500],
    # Anomaly — flatline (metric stopped updating)
    [45, 45, 45, 45, 45, 45, 45, 45, 45, 45],
    # Normal — slightly different but same distribution
    [48, 51, 45, 52, 49, 47, 50, 46, 44, 51],
]

# ── Scan ──────────────────────────────────────────────────────────────────
result = wg.scan(
    training=normal_windows,
    test=test_windows,
    encoder_type="timeseries",
)

# ── Report ────────────────────────────────────────────────────────────────
labels = ["Normal window", "Latency spike", "Flatline", "Normal window"]

print("=== Time Series Anomaly Detection ===\n")

for i, (r, label) in enumerate(zip(result.results, labels)):
    status = "🚨" if r.is_anomaly else "✅"
    preview = str(test_windows[i][:5])[:-1] + ", ...]"
    print(f"  {status} Window {i + 1}: {label}")
    print(f"     Data: {preview}")
    print(f"     Score: {r.score:.2f}  |  Confidence: {r.confidence:.0%}")
    print()

print(f"Detected: {result.summary.anomalies_found} anomalies out of {result.summary.total_test_samples} windows")
