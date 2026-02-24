# API Reference

## `WaveGuard` Client

### Constructor

```python
from waveguard import WaveGuard

wg = WaveGuard(
    api_key="YOUR_KEY",
    base_url="https://gpartin--waveguard-api-fastapi-app.modal.run",  # default
    timeout=120.0,  # seconds
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `api_key` | `str` | *(required)* | Your WaveGuard API key |
| `base_url` | `str` | Production URL | API endpoint |
| `timeout` | `float` | `120.0` | Request timeout in seconds |

---

### `wg.scan(training, test, encoder_type=None, sensitivity=None)`

**The only method you need.** Sends training + test data in one call, returns anomaly scores.

```python
result = wg.scan(
    training=[{"cpu": 45}, {"cpu": 48}, {"cpu": 42}],
    test=[{"cpu": 46}, {"cpu": 99}],
    sensitivity=1.0,
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `training` | `list` | *(required)* | 2+ examples of normal data |
| `test` | `list` | *(required)* | 1+ samples to check |
| `encoder_type` | `str` | `None` (auto) | Force: `"json"`, `"numeric"`, `"text"`, `"timeseries"`, `"tabular"` |
| `sensitivity` | `float` | `None` (1.0) | 0.5–3.0. Lower = more sensitive |

**Returns:** `ScanResult`

---

### `wg.health()`

Check API status and GPU availability. No authentication required.

```python
health = wg.health()
print(health.status, health.gpu)
```

**Returns:** `HealthStatus`

---

### `wg.tier()`

Get current subscription tier and rate limits.

```python
tier = wg.tier()
print(tier.tier, tier.limits)
```

**Returns:** `TierInfo`

---

## Response Types

### `ScanResult`

| Attribute | Type | Description |
|-----------|------|-------------|
| `results` | `list[SampleResult]` | One entry per test sample, in order |
| `summary` | `ScanSummary` | Aggregate statistics |
| `raw` | `dict` | Full JSON response |

### `SampleResult`

| Attribute | Type | Description |
|-----------|------|-------------|
| `score` | `float` | Anomaly score (0 = normal, higher = more anomalous) |
| `is_anomaly` | `bool` | Whether this sample is flagged |
| `threshold` | `float` | Score threshold for flagging |
| `mahalanobis_distance` | `float` | Statistical distance from training distribution |
| `confidence` | `float` | 0.0–1.0 confidence in the anomaly call |
| `top_features` | `list[FeatureInfo]` | Top dimensions driving the score |
| `latency_ms` | `float` | Per-sample processing time |
| `engine` | `EngineInfo` | Physics engine config used |
| `raw` | `dict` | Raw JSON for this sample |

### `ScanSummary`

| Attribute | Type | Description |
|-----------|------|-------------|
| `total_test_samples` | `int` | Number of test samples |
| `total_training_samples` | `int` | Number of training samples |
| `anomalies_found` | `int` | Count of flagged anomalies |
| `anomaly_rate` | `float` | Fraction flagged |
| `mean_score` | `float` | Average anomaly score |
| `max_score` | `float` | Highest anomaly score |
| `total_latency_ms` | `float` | Total scan wall-clock time |
| `encoder_type` | `str` | Encoder used (auto-detected or specified) |

### `FeatureInfo`

| Attribute | Type | Description |
|-----------|------|-------------|
| `dimension` | `int` | Index into the fingerprint vector |
| `label` | `str` | Human-readable label (e.g. `"kurt_E"`, `"skew_chi"`) |
| `z_score` | `float` | Standard deviations from training mean |

### `EngineInfo`

| Attribute | Type | Description |
|-----------|------|-------------|
| `grid_size` | `int` | Lattice size (N in N×N×N) |
| `evolution_steps` | `int` | Wave evolution steps per sample |
| `fingerprint_dims` | `int` | Fingerprint vector dimensionality |

### `HealthStatus`

| Attribute | Type | Description |
|-----------|------|-------------|
| `status` | `str` | `"healthy"` or error state |
| `version` | `str` | API version |
| `gpu` | `str` | GPU info (e.g. `"T4"`) |
| `mode` | `str` | Running mode |
| `uptime_seconds` | `float` | Server uptime |

### `TierInfo`

| Attribute | Type | Description |
|-----------|------|-------------|
| `tier` | `str` | `"BASIC"`, `"PRO"`, `"ULTRA"`, or `"MEGA"` |
| `limits` | `dict` | `max_training_samples`, `max_test_samples`, `rate_limit_per_min` |

---

## Exceptions

All exceptions inherit from `WaveGuardError`:

```python
from waveguard import WaveGuardError, AuthenticationError, ValidationError, RateLimitError, ServerError
```

| Exception | HTTP Code | When |
|-----------|-----------|------|
| `AuthenticationError` | 401 | Invalid or missing API key |
| `ValidationError` | 422 | Bad request data |
| `RateLimitError` | 429 | Rate or tier limit exceeded |
| `ServerError` | 5xx | Transient server errors |
| `WaveGuardError` | any | Catch-all base class |

Each exception has `.message`, `.status_code`, and `.detail` attributes.

---

## REST API (Direct HTTP)

If you prefer raw HTTP calls:

### `POST /v1/scan`

```bash
curl -X POST https://gpartin--waveguard-api-fastapi-app.modal.run/v1/scan \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-key" \
  -d '{
    "training": [{"cpu": 45}, {"cpu": 48}, {"cpu": 42}],
    "test": [{"cpu": 46}, {"cpu": 99}]
  }'
```

### `GET /v1/health`

```bash
curl https://gpartin--waveguard-api-fastapi-app.modal.run/v1/health
```

### `GET /v1/tier`

```bash
curl -H "X-API-Key: your-key" \
  https://gpartin--waveguard-api-fastapi-app.modal.run/v1/tier
```

### Interactive Docs

Full Swagger UI: https://gpartin--waveguard-api-fastapi-app.modal.run/docs
