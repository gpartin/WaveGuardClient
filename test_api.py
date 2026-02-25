"""Quick test: SDK direct API + p_value + grid 64."""
from waveguard import WaveGuard

wg = WaveGuard()

sr = wg.scan(
    training=[
        {"cpu": 45, "mem": 60, "disk": 30, "net": 100, "io": 20},
        {"cpu": 50, "mem": 65, "disk": 32, "net": 110, "io": 22},
        {"cpu": 48, "mem": 62, "disk": 31, "net": 105, "io": 21},
        {"cpu": 47, "mem": 63, "disk": 29, "net": 102, "io": 19},
        {"cpu": 46, "mem": 61, "disk": 30, "net": 108, "io": 23},
    ],
    test=[
        {"cpu": 46, "mem": 61, "disk": 30, "net": 103, "io": 20},
        {"cpu": 99, "mem": 95, "disk": 90, "net": 900, "io": 85},
    ],
)

print("=== SDK DIRECT API TEST ===")
print(f"Results: {len(sr.results)} samples")
for i, r in enumerate(sr.results):
    print(
        f"  Sample {i+1}: anomaly={r.is_anomaly}, score={r.score:.2f}, "
        f"confidence={r.confidence:.2%}, p_value={r.p_value:.6f}, "
        f"grid={r.engine.grid_size}"
    )
    feats = [(f.label, round(f.z_score, 2)) for f in r.top_features[:3]]
    print(f"           top features: {feats}")

print()
print(f"p_value field present: {hasattr(sr.results[0], 'p_value')}")
print(f"Grid size (should be 64): {sr.results[0].engine.grid_size}")
print()
print("=== ALL CHECKS ===")
checks = [
    ("p_value field exists", hasattr(sr.results[0], 'p_value')),
    ("Grid = 64", sr.results[0].engine.grid_size == 64),
    ("p_value is float", isinstance(sr.results[0].p_value, float)),
    ("2 results returned", len(sr.results) == 2),
]
for name, ok in checks:
    print(f"  {'PASS' if ok else 'FAIL'}: {name}")
print(f"\nAll checks passed: {all(ok for _, ok in checks)}")
