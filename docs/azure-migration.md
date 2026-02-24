# Azure Anomaly Detector Migration Guide

**Azure Anomaly Detector retires October 1, 2026.** WaveGuard is a drop-in replacement.

## Key Differences

| Feature | Azure Anomaly Detector | WaveGuard |
|---------|----------------------|-----------|
| **API calls** | 3+ (create model, train, detect, delete) | **1** |
| **State** | Stateful (model persists) | **Stateless** (nothing stored) |
| **Training time** | Minutes to hours | **Seconds** (included in scan call) |
| **Data types** | Time series only | **Any** (JSON, text, numbers, time series) |
| **Model management** | Required | **None** |
| **GPU** | Azure-managed | NVIDIA T4 (Modal serverless) |
| **Pricing** | Per-transaction + storage | Per-scan (no storage costs) |

## Migration Steps

### 1. Install the SDK

```bash
pip install waveguard
```

### 2. Replace the client

**Before (Azure):**

```python
from azure.ai.anomalydetector import AnomalyDetectorClient
from azure.core.credentials import AzureKeyCredential

client = AnomalyDetectorClient(endpoint, AzureKeyCredential(key))

# Create and train model (separate step, takes minutes)
model = client.train_multivariate_model(training_request)
# ... wait for training ...

# Detect (separate step)
result = client.detect_multivariate_batch_anomaly(model_id, detect_request)

# Clean up (separate step)
client.delete_multivariate_model(model_id)
```

**After (WaveGuard):**

```python
from waveguard import WaveGuard

wg = WaveGuard(api_key="YOUR_KEY")

# Everything in one call
result = wg.scan(training=normal_data, test=new_data)
```

### 3. Map your data format

Azure requires time-series CSV with timestamps. WaveGuard accepts anything:

```python
# Azure format (time series only):
# timestamp,cpu,memory,errors
# 2025-01-01T00:00:00Z,45,62,0
# 2025-01-01T01:00:00Z,48,63,0

# WaveGuard format (any of these work):
training = [
    {"cpu": 45, "memory": 62, "errors": 0},  # JSON objects
    {"cpu": 48, "memory": 63, "errors": 0},
]

# Or time series arrays:
training = [
    [45, 48, 42, 50, 47],  # window 1
    [46, 49, 43, 48, 45],  # window 2
]

# Or even text:
training = [
    "INFO Request processed in 45ms [200 OK]",
    "INFO Request processed in 52ms [200 OK]",
]
```

### 4. Map response fields

| Azure Field | WaveGuard Field |
|-------------|-----------------|
| `is_anomaly` | `result.is_anomaly` |
| `severity` | `result.score` |
| `score` | `result.confidence` |
| `interpretation` | `result.top_features` |

### 5. Remove Azure cleanup code

Azure requires explicit model deletion. WaveGuard is stateless — there's nothing to clean up.

```python
# DELETE THIS:
# client.delete_multivariate_model(model_id)

# WaveGuard tears down automatically after each scan() call
```

## FAQ

**Q: Do I need to retrain periodically?**
A: No. WaveGuard is stateless — you send training data with every call. Update your normal baseline whenever your definition of "normal" changes.

**Q: What about my existing Azure training data?**
A: Convert your CSV rows to JSON objects or arrays, and pass them as the `training` parameter. No model files to migrate.

**Q: Is the detection quality comparable?**
A: WaveGuard uses a fundamentally different approach (wave physics vs. ML). Results may differ. Test with your data before fully migrating.

**Q: What about latency?**
A: First call may take 5-10s (GPU cold start). Subsequent calls: ~1-3s depending on sample count. Azure typically takes longer due to separate train/detect steps.

## Example

See [examples/05_azure_migration.py](../examples/05_azure_migration.py) for a complete working example.
