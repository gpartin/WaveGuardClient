"""
Example 2: Server Monitoring — detect infrastructure anomalies.

Real-world pattern: you have a stream of server metrics and want to
catch when something goes wrong. WaveGuard learns what normal servers
look like, then flags any readings that deviate.

Usage:
    export WAVEGUARD_API_KEY="your-key"
    python 02_server_monitoring.py
"""

import os
from waveguard import WaveGuard

api_key = os.environ.get("WAVEGUARD_API_KEY", "demo")
wg = WaveGuard(api_key=api_key)

# ── Baseline: 6 normal readings from a healthy server ────────────────────
normal_readings = [
    {"cpu_pct": 35, "mem_pct": 55, "disk_iops": 200, "net_mbps": 12, "error_rate": 0.01, "latency_p99_ms": 45},
    {"cpu_pct": 40, "mem_pct": 58, "disk_iops": 220, "net_mbps": 15, "error_rate": 0.02, "latency_p99_ms": 50},
    {"cpu_pct": 38, "mem_pct": 56, "disk_iops": 190, "net_mbps": 11, "error_rate": 0.01, "latency_p99_ms": 42},
    {"cpu_pct": 42, "mem_pct": 60, "disk_iops": 230, "net_mbps": 14, "error_rate": 0.03, "latency_p99_ms": 55},
    {"cpu_pct": 37, "mem_pct": 57, "disk_iops": 210, "net_mbps": 13, "error_rate": 0.01, "latency_p99_ms": 48},
    {"cpu_pct": 41, "mem_pct": 59, "disk_iops": 215, "net_mbps": 14, "error_rate": 0.02, "latency_p99_ms": 52},
]

# ── New readings to check ────────────────────────────────────────────────
# Mix of normal operations, a memory leak, and a DDoS attack
new_readings = [
    # Normal operation
    {"cpu_pct": 39, "mem_pct": 57, "disk_iops": 205, "net_mbps": 13, "error_rate": 0.02, "latency_p99_ms": 47},
    # Memory leak — memory climbing, latency spiking
    {"cpu_pct": 65, "mem_pct": 92, "disk_iops": 180, "net_mbps": 10, "error_rate": 0.15, "latency_p99_ms": 450},
    # Normal operation
    {"cpu_pct": 36, "mem_pct": 54, "disk_iops": 195, "net_mbps": 12, "error_rate": 0.01, "latency_p99_ms": 44},
    # DDoS attack — network saturated, high errors
    {"cpu_pct": 98, "mem_pct": 85, "disk_iops": 50, "net_mbps": 980, "error_rate": 0.85, "latency_p99_ms": 5000},
]

# ── Scan ──────────────────────────────────────────────────────────────────
result = wg.scan(training=normal_readings, test=new_readings)

# ── Report ────────────────────────────────────────────────────────────────
labels = ["Normal ops", "Memory leak", "Normal ops", "DDoS attack"]

print("=== Server Health Report ===\n")
print(f"Baseline: {result.summary.total_training_samples} normal readings")
print(f"Checked:  {result.summary.total_test_samples} new readings")
print(f"Latency:  {result.summary.total_latency_ms:.0f}ms\n")

for i, (r, label) in enumerate(zip(result.results, labels)):
    status = "🚨 ALERT" if r.is_anomaly else "✅ OK"
    print(f"  [{status}] Reading {i + 1} ({label})")
    print(f"         Score: {r.score:.1f}  |  Confidence: {r.confidence:.0%}")

    if r.is_anomaly and r.top_features:
        features = ", ".join(f.label for f in r.top_features[:3])
        print(f"         Anomalous dimensions: {features}")
    print()
