<p align="center">
  <img src="https://img.shields.io/pypi/v/waveguard?style=for-the-badge&color=blueviolet" alt="PyPI">
  <img src="https://img.shields.io/badge/API-v2.0.0_stateless-brightgreen?style=for-the-badge" alt="v2.0.0">
  <img src="https://img.shields.io/badge/GPU-CUDA_accelerated-76B900?style=for-the-badge&logo=nvidia" alt="CUDA">
  <img src="https://img.shields.io/badge/MCP-Claude_Desktop-orange?style=for-the-badge" alt="MCP">
</p>

<h1 align="center">WaveGuard Python SDK</h1>

<p align="center">
  <strong>Anomaly detection powered by wave physics. Not machine learning.</strong><br>
  One API call. Fully stateless. Works on any data type.
</p>

<p align="center">
  <a href="#quickstart">Quickstart</a> •
  <a href="#examples">Examples</a> •
  <a href="docs/api-reference.md">API Reference</a> •
  <a href="docs/mcp-integration.md">MCP / Claude</a> •
  <a href="docs/azure-migration.md">Azure Migration</a>
</p>

---

## What is WaveGuard?

WaveGuard detects anomalies by encoding your data onto a 3D lattice and running GPU-accelerated **wave physics simulations**. Normal data produces stable wave patterns; anomalies produce divergent ones.

**No training pipelines. No model management. No state.**

```
Your data → 3D wave simulation on GPU → Anomaly scores back
```

## Install

```bash
pip install waveguard
```

That's it. The only dependency is `requests`. All physics runs server-side on GPU.

## Quickstart

```python
from waveguard import WaveGuard

wg = WaveGuard(api_key="YOUR_KEY")

result = wg.scan(
    training=[
        {"cpu": 45, "memory": 62, "disk_io": 120, "errors": 0},
        {"cpu": 48, "memory": 63, "disk_io": 115, "errors": 0},
        {"cpu": 42, "memory": 61, "disk_io": 125, "errors": 1},
        {"cpu": 50, "memory": 64, "disk_io": 118, "errors": 0},
    ],
    test=[
        {"cpu": 46, "memory": 62, "disk_io": 119, "errors": 0},    # normal
        {"cpu": 99, "memory": 95, "disk_io": 800, "errors": 150},   # anomaly
    ],
)

print(f"Anomalies: {result.summary.anomalies_found}/{result.summary.total_test_samples}")

for r in result.results:
    status = "🚨 ANOMALY" if r.is_anomaly else "✅ Normal"
    print(f"  {status}  score={r.score:.1f}  confidence={r.confidence:.0%}")
```

**Output:**
```
Anomalies: 1/2
  ✅ Normal   score=0.5  confidence=10%
  🚨 ANOMALY  score=8.3  confidence=95%
```

## How It Works

1. Send **training** data (examples of normal) + **test** data (what to check)
2. The API encodes both onto a 32³ lattice and runs coupled wave equations
3. Statistical fingerprints are compared — anomalies produce divergent wave patterns
4. You get back per-sample scores, confidence, and the **top features explaining why**
5. Everything tears down — **nothing is stored between calls**

<details>
<summary><strong>What data types are supported?</strong></summary>

All of them. Auto-detected from data shape:

| Type | Example |
|------|---------|
| JSON objects | `{"cpu": 45, "memory": 62}` |
| Numeric arrays | `[1.0, 1.2, 5.8, 1.1]` |
| Text strings | `"ERROR segfault at 0x0"` |
| Time series | `[100, 102, 98, 105, 99]` |

</details>

## Examples

| # | Example | Use Case |
|---|---------|----------|
| 01 | [Quickstart](examples/01_quickstart.py) | Minimal working example |
| 02 | [Server Monitoring](examples/02_server_monitoring.py) | Detect infra anomalies (memory leak, DDoS) |
| 03 | [Log Analysis](examples/03_log_analysis.py) | Flag unusual log lines (errors, attacks) |
| 04 | [Time Series](examples/04_time_series.py) | Detect spikes/flatlines in metric windows |
| 05 | [Azure Migration](examples/05_azure_migration.py) | Drop-in Azure Anomaly Detector replacement |
| 06 | [Batch Scanning](examples/06_batch_scanning.py) | Scan 20+ samples efficiently in one call |
| 07 | [Error Handling](examples/07_error_handling.py) | Retry logic, exception handling patterns |

## MCP Server (Claude Desktop)

Give Claude the ability to detect anomalies. Add to your Claude Desktop config:

```json
{
  "mcpServers": {
    "waveguard": {
      "command": "python",
      "args": ["/path/to/WaveGuardClient/mcp_server/server.py"],
      "env": {
        "WAVEGUARD_API_KEY": "your-key"
      }
    }
  }
}
```

Then ask Claude: *"Check if these server metrics are anomalous..."*

See [MCP Integration Guide](docs/mcp-integration.md) for full setup.

## Azure Migration

**Azure Anomaly Detector retires October 2026.** WaveGuard is a drop-in replacement:

```python
# Before (Azure) — 3+ API calls, stateful, time-series only
client = AnomalyDetectorClient(endpoint, credential)
model = client.train_multivariate_model(request)   # minutes
result = client.detect_multivariate_batch_anomaly(model_id, data)
client.delete_multivariate_model(model_id)

# After (WaveGuard) — 1 API call, stateless, any data type
wg = WaveGuard(api_key="YOUR_KEY")
result = wg.scan(training=normal_data, test=new_data)  # seconds
```

See [Azure Migration Guide](docs/azure-migration.md) for details.

## API Reference

### `wg.scan(training, test, encoder_type=None, sensitivity=None)`

| Parameter | Type | Description |
|-----------|------|-------------|
| `training` | `list` | 2+ examples of normal data |
| `test` | `list` | 1+ samples to check |
| `encoder_type` | `str` | Force: `"json"`, `"numeric"`, `"text"`, `"timeseries"` (default: auto) |
| `sensitivity` | `float` | 0.5–3.0, lower = more sensitive (default: 1.0) |

Returns `ScanResult` with `.results` (per-sample) and `.summary` (aggregate).

### `wg.health()` / `wg.tier()`

Health check (no auth) and subscription tier info.

### Error Handling

```python
from waveguard import WaveGuard, AuthenticationError, RateLimitError

try:
    result = wg.scan(training=data, test=new_data)
except AuthenticationError:
    print("Bad API key")
except RateLimitError:
    print("Too many requests — back off and retry")
```

Full API reference: [docs/api-reference.md](docs/api-reference.md)

## Project Structure

```
WaveGuardClient/
├── waveguard/              # Python SDK package
│   ├── __init__.py         # Public API exports
│   ├── client.py           # WaveGuard client class
│   └── exceptions.py       # Exception hierarchy
├── mcp_server/             # MCP server for Claude Desktop
│   ├── server.py           # stdio + HTTP transport
│   └── README.md           # MCP setup guide
├── examples/               # 7 runnable examples
├── docs/                   # Documentation
│   ├── getting-started.md
│   ├── api-reference.md
│   ├── mcp-integration.md
│   └── azure-migration.md
├── tests/                  # Test suite (runs offline)
├── pyproject.toml          # Package config (pip install -e .)
└── CHANGELOG.md
```

## Development

```bash
git clone https://github.com/gpartin/WaveGuardClient.git
cd WaveGuardClient
pip install -e ".[dev]"
pytest
```

## Links

- **Live API**: https://gpartin--waveguard-api-fastapi-app.modal.run
- **Interactive Docs (Swagger)**: https://gpartin--waveguard-api-fastapi-app.modal.run/docs
- **Engine + Research**: https://github.com/gpartin/LFMAnomalyDetection

## License

MIT — see [LICENSE](LICENSE).
