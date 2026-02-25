#!/usr/bin/env python3
"""
IoT Predictive Maintenance with WaveGuard
==========================================

Real-world example: Monitor industrial equipment sensors and detect
failures before they happen — with zero ML knowledge required.

This example simulates a factory floor with pump stations.
Each station reports 10 sensor readings every minute.
WaveGuard detects equipment anomalies using physics-based
wave simulation — no model training, no hyperparameters, no drift.

Run:
    pip install WaveGuardClient
    python iot_predictive_maintenance.py
"""

from waveguard import WaveGuard
import random
import time

# ── Simulated sensor readings ─────────────────────────────────────────

def read_healthy_pump():
    """Simulate a healthy industrial pump station."""
    return {
        "temperature_c":   round(random.gauss(72, 3), 1),
        "pressure_psi":    round(random.gauss(14.7, 0.3), 2),
        "vibration_g":     round(abs(random.gauss(0.5, 0.15)), 3),
        "humidity_pct":    round(random.gauss(45, 5), 1),
        "flow_rate_lpm":   round(random.gauss(100, 8), 1),
        "voltage_v":       round(random.gauss(220, 5), 1),
        "current_a":       round(random.gauss(15, 2), 1),
        "rpm":             round(random.gauss(1750, 25)),
        "bearing_temp_c":  round(random.gauss(55, 3), 1),
        "oil_viscosity":   round(random.gauss(32, 2), 1),
    }


def read_failing_pump(failure_type="bearing"):
    """Simulate pump with a developing fault."""
    if failure_type == "bearing":
        return {
            "temperature_c":   round(random.gauss(95, 5), 1),   # HOT
            "pressure_psi":    round(random.gauss(14.7, 0.3), 2),
            "vibration_g":     round(random.gauss(3.5, 0.5), 3),  # HIGH VIBRATION
            "humidity_pct":    round(random.gauss(45, 5), 1),
            "flow_rate_lpm":   round(random.gauss(95, 8), 1),
            "voltage_v":       round(random.gauss(220, 5), 1),
            "current_a":       round(random.gauss(20, 3), 1),   # DRAWING MORE
            "rpm":             round(random.gauss(1700, 50)),     # SLOWING
            "bearing_temp_c":  round(random.gauss(120, 10), 1),  # VERY HOT
            "oil_viscosity":   round(random.gauss(18, 3), 1),   # DEGRADED
        }
    elif failure_type == "leak":
        return {
            "temperature_c":   round(random.gauss(72, 3), 1),
            "pressure_psi":    round(random.gauss(8, 1), 2),     # PRESSURE DROP
            "vibration_g":     round(abs(random.gauss(0.5, 0.15)), 3),
            "humidity_pct":    round(random.gauss(80, 5), 1),    # MOISTURE
            "flow_rate_lpm":   round(random.gauss(30, 5), 1),   # LOW FLOW
            "voltage_v":       round(random.gauss(220, 5), 1),
            "current_a":       round(random.gauss(15, 2), 1),
            "rpm":             round(random.gauss(1750, 25)),
            "bearing_temp_c":  round(random.gauss(55, 3), 1),
            "oil_viscosity":   round(random.gauss(32, 2), 1),
        }
    else:  # overload
        return {
            "temperature_c":   round(random.gauss(88, 3), 1),
            "pressure_psi":    round(random.gauss(18, 1), 2),    # OVER PRESSURE
            "vibration_g":     round(random.gauss(2.0, 0.3), 3),
            "humidity_pct":    round(random.gauss(45, 5), 1),
            "flow_rate_lpm":   round(random.gauss(160, 10), 1),  # HIGH FLOW
            "voltage_v":       round(random.gauss(210, 8), 1),   # SAG
            "current_a":       round(random.gauss(35, 5), 1),    # OVERLOAD
            "rpm":             round(random.gauss(1850, 30)),
            "bearing_temp_c":  round(random.gauss(80, 5), 1),
            "oil_viscosity":   round(random.gauss(25, 2), 1),
        }


def main():
    print("=" * 65)
    print("  IoT Predictive Maintenance with WaveGuard")
    print("  No ML. No models. No tuning. Just physics.")
    print("=" * 65)

    # Connect — no API key needed for free tier
    wg = WaveGuard()
    print(f"\n  Connected to WaveGuard API")

    # ── Step 1: Collect baseline readings from healthy pumps ──────────
    print("\n  📊 Collecting baseline from 20 healthy pump readings...")
    baseline = [read_healthy_pump() for _ in range(20)]

    # ── Step 2: New readings come in — some from failing pumps ────────
    print("  🔍 Scanning 8 new readings for anomalies...\n")

    test_readings = [
        read_healthy_pump(),                       # Normal
        read_healthy_pump(),                       # Normal
        read_failing_pump("bearing"),              # ⚠️ Bearing failure
        read_healthy_pump(),                       # Normal
        read_failing_pump("leak"),                 # ⚠️ Seal leak
        read_healthy_pump(),                       # Normal
        read_failing_pump("overload"),             # ⚠️ Motor overload
        read_healthy_pump(),                       # Normal
    ]

    expected = ["Normal", "Normal", "BEARING FAIL", "Normal",
                "SEAL LEAK", "Normal", "OVERLOAD", "Normal"]

    # ── Step 3: One API call does everything ──────────────────────────
    result = wg.scan(
        training=baseline,
        test=test_readings,
        sensitivity=1.5,
    )

    # ── Step 4: Alert on anomalies ────────────────────────────────────
    alerts = 0
    for i, r in enumerate(result.results):
        status = "🚨 ANOMALY" if r.is_anomaly else "✅ Normal "
        if r.is_anomaly:
            alerts += 1
            features = ", ".join(f"{f.label} (z={f.z_score:.1f})"
                                 for f in r.top_features[:3])
            print(f"  Pump #{i+1}: {status}  confidence={r.confidence:.0%}  "
                  f"p={r.p_value:.4f}")
            print(f"           Expected: {expected[i]}")
            print(f"           Top signals: {features}")
        else:
            print(f"  Pump #{i+1}: {status}  score={r.score:.1f}  "
                  f"Expected: {expected[i]}")

    print(f"\n  ─────────────────────────────────────────────────")
    print(f"  Summary: {alerts} alerts from {len(test_readings)} readings")
    print(f"  Latency: {result.results[0].latency_ms:.0f}ms per sample (GPU)")
    print(f"  Grid: {result.results[0].engine.grid_size}³ lattice")
    print()

    # ── Step 5: Show how easy integration is ──────────────────────────
    print("  💡 To add this to your SCADA/PLC pipeline:")
    print()
    print("     from waveguard import WaveGuard")
    print("     wg = WaveGuard(api_key='YOUR_KEY')")
    print("     result = wg.scan(training=last_hour, test=new_reading)")
    print("     if any(r.is_anomaly for r in result.results):")
    print("         send_maintenance_alert(result)")
    print()


if __name__ == "__main__":
    main()
