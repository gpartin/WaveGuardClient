"""
Example 5: Azure Migration — drop-in replacement for Azure Anomaly Detector.

Azure Anomaly Detector retires October 2026. WaveGuard is a stateless,
single-call alternative that works on ANY data type (not just time series).

This example shows the migration path side-by-side.

Usage:
    export WAVEGUARD_API_KEY="your-key"
    python 05_azure_migration.py
"""

import os
from waveguard import WaveGuard

api_key = os.environ.get("WAVEGUARD_API_KEY", "demo")

# ═══════════════════════════════════════════════════════════════════════════
# BEFORE: Azure Anomaly Detector (retiring October 2026)
# ═══════════════════════════════════════════════════════════════════════════

# from azure.ai.anomalydetector import AnomalyDetectorClient
# from azure.core.credentials import AzureKeyCredential
#
# client = AnomalyDetectorClient(
#     endpoint="https://YOUR-RESOURCE.cognitiveservices.azure.com",
#     credential=AzureKeyCredential("YOUR-AZURE-KEY"),
# )
#
# # Step 1: Create and train a model (async, takes minutes)
# model = client.train_multivariate_model(
#     ModelInfo(
#         data_source="https://storage.blob.core.windows.net/data/training.csv",
#         start_time="2025-01-01T00:00:00Z",
#         end_time="2025-01-31T00:00:00Z",
#     )
# )
#
# # Step 2: Wait for training to complete
# model_id = model.model_id
# # ... poll until status == "READY" ...
#
# # Step 3: Run detection (separate call)
# result = client.detect_multivariate_batch_anomaly(
#     model_id,
#     DetectionRequest(
#         source="https://storage.blob.core.windows.net/data/test.csv",
#         start_time="2025-02-01T00:00:00Z",
#         end_time="2025-02-07T00:00:00Z",
#     ),
# )
#
# # Step 4: Clean up
# client.delete_multivariate_model(model_id)

# ═══════════════════════════════════════════════════════════════════════════
# AFTER: WaveGuard — ONE call, stateless, any data type
# ═══════════════════════════════════════════════════════════════════════════

wg = WaveGuard(api_key=api_key)

# Your training data — just normal examples, in-memory, any format
training_data = [
    {"temperature": 22.1, "humidity": 45, "pressure": 1013, "vibration": 0.02},
    {"temperature": 22.5, "humidity": 46, "pressure": 1012, "vibration": 0.03},
    {"temperature": 21.8, "humidity": 44, "pressure": 1014, "vibration": 0.02},
    {"temperature": 22.3, "humidity": 45, "pressure": 1013, "vibration": 0.02},
    {"temperature": 22.0, "humidity": 47, "pressure": 1011, "vibration": 0.03},
]

# Your test data — samples to check
test_data = [
    {"temperature": 22.2, "humidity": 45, "pressure": 1013, "vibration": 0.02},  # normal
    {"temperature": 85.0, "humidity": 12, "pressure": 980, "vibration": 2.50},   # anomaly
]

# One call — learn, detect, tear down
result = wg.scan(training=training_data, test=test_data)

# ── Results ───────────────────────────────────────────────────────────────
print("=== Azure → WaveGuard Migration Example ===\n")
print("Key differences:")
print("  Azure:     2+ API calls, stateful model, time-series only, minutes to train")
print("  WaveGuard: 1  API call, stateless, any data type, seconds\n")

for i, r in enumerate(result.results):
    status = "ANOMALY" if r.is_anomaly else "Normal"
    print(f"  Sample {i + 1}: {status} (score={r.score:.1f}, confidence={r.confidence:.0%})")

print(f"\nTotal latency: {result.summary.total_latency_ms:.0f}ms")
print(f"Encoder: {result.summary.encoder_type}")
