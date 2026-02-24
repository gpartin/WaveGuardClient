"""
Example 6: Batch Scanning — process many samples efficiently.

When you have many items to check, send them all in one scan() call.
The API parallelizes test-sample evaluation on the GPU.

Usage:
    export WAVEGUARD_API_KEY="your-key"
    python 06_batch_scanning.py
"""

import os
import random
from waveguard import WaveGuard

api_key = os.environ.get("WAVEGUARD_API_KEY", "demo")
wg = WaveGuard(api_key=api_key)


def generate_normal_transaction():
    """Generate a normal e-commerce transaction."""
    return {
        "amount_usd": round(random.gauss(75, 20), 2),
        "items": random.randint(1, 5),
        "session_duration_sec": random.randint(120, 600),
        "pages_viewed": random.randint(3, 15),
        "returning_customer": random.choice([0, 1]),
    }


def generate_fraud_transaction():
    """Generate a suspicious transaction."""
    return {
        "amount_usd": round(random.gauss(2500, 500), 2),  # much higher
        "items": random.randint(10, 30),                    # bulk purchase
        "session_duration_sec": random.randint(5, 20),      # very fast
        "pages_viewed": 1,                                  # direct checkout
        "returning_customer": 0,                            # new account
    }


# ── Generate data ─────────────────────────────────────────────────────────
random.seed(42)

# 8 normal transactions as training baseline
training = [generate_normal_transaction() for _ in range(8)]

# 20 test transactions: mostly normal, a few fraudulent
test = []
labels = []
for i in range(20):
    if i in [3, 7, 12, 18]:  # inject fraud at these positions
        test.append(generate_fraud_transaction())
        labels.append("FRAUD")
    else:
        test.append(generate_normal_transaction())
        labels.append("legit")

# ── Single scan call for all 20 test samples ──────────────────────────────
result = wg.scan(training=training, test=test)

# ── Report ────────────────────────────────────────────────────────────────
print("=== Batch Transaction Scan ===\n")
print(f"Training baseline: {result.summary.total_training_samples} transactions")
print(f"Batch size: {result.summary.total_test_samples} transactions")
print(f"Total time: {result.summary.total_latency_ms:.0f}ms")
per_sample = result.summary.total_latency_ms / max(result.summary.total_test_samples, 1)
print(f"Per-sample: {per_sample:.1f}ms")
print()

# Count hits
true_pos = sum(1 for r, l in zip(result.results, labels) if r.is_anomaly and l == "FRAUD")
false_pos = sum(1 for r, l in zip(result.results, labels) if r.is_anomaly and l == "legit")
total_fraud = labels.count("FRAUD")

print(f"Fraud injected: {total_fraud}")
print(f"Fraud detected: {true_pos}")
print(f"False alarms:   {false_pos}")
print()

# Show all flagged transactions
for i, (r, label) in enumerate(zip(result.results, labels)):
    if r.is_anomaly:
        actual = "FRAUD" if label == "FRAUD" else "false alarm"
        print(f"  🚨 Transaction {i + 1}: ${test[i]['amount_usd']:.2f}, "
              f"{test[i]['items']} items, {test[i]['session_duration_sec']}s "
              f"— score={r.score:.1f} ({actual})")
