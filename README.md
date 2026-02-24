<p align="center">
  <img src="https://img.shields.io/pypi/v/WaveGuardClient?style=for-the-badge&color=blueviolet" alt="PyPI">
  <img src="https://img.shields.io/badge/API-v2.0.0_stateless-brightgreen?style=for-the-badge" alt="v2.0.0">
  <img src="https://img.shields.io/badge/GPU-CUDA_accelerated-76B900?style=for-the-badge&logo=nvidia" alt="CUDA">
  <img src="https://img.shields.io/badge/MCP-Claude_Desktop-orange?style=for-the-badge" alt="MCP">
  <a href="https://smithery.ai/server/gpartin/WaveGuardClient"><img src="https://smithery.ai/badge/gpartin/WaveGuardClient" alt="Smithery"></a>
</p>

<h1 align="center">WaveGuard Python SDK</h1>

<p align="center">
  <strong>Anomaly detection powered by wave physics. Not machine learning.</strong><br>
  One API call. Fully stateless. Works on any data type.
</p>

<p align="center">
  <a href="#quickstart">Quickstart</a> •
  <a href="#use-cases">Use Cases</a> •
  <a href="#examples">Examples</a> •
  <a href="docs/api-reference.md">API Reference</a> •
  <a href="docs/mcp-integration.md">MCP / Claude</a> •
  <a href="docs/azure-migration.md">Azure Migration</a>
</p>

---

## What is WaveGuard?

WaveGuard is a **general-purpose anomaly detection API**. Send it any data — server metrics, financial transactions, log files, sensor readings, time series — and get back anomaly scores, confidence levels, and explanations of *which features* triggered the alert.

**No training pipelines. No model management. No state. One API call.**

```
Your data  →  WaveGuard API (GPU)  →  Anomaly scores + explanations
```

Under the hood, it uses GPU-accelerated wave physics instead of machine learning. You don't need to know or care about the physics — it's all server-side.

<details>
<summary><strong>How does it actually work?</strong></summary>

Your data is encoded onto a 32³ lattice and run through coupled wave equation simulations on GPU. Normal data produces stable wave patterns; anomalies produce divergent ones. A 52-dimensional statistical fingerprint is compared between training and test data. Everything is torn down after each call — nothing is stored.

The key advantage over ML: no training data requirements (2+ samples is enough), no model drift, no retraining, no hyperparameter tuning. Same API call works on structured data, text, numbers, and time series.

</details>

## Install

```bash
pip install WaveGuardClient
```

That's it. The only dependency is `requests`. All physics runs server-side on GPU.

## Quickstart

The same `scan()` call works on any data type. Here are three different industries — same API:

### Detect a compromised server

```python
from waveguard import WaveGuard

wg = WaveGuard(api_key="YOUR_KEY")

result = wg.scan(
    training=[
        {"cpu": 45, "memory": 62, "disk_io": 120, "errors": 0},
        {"cpu": 48, "memory": 63, "disk_io": 115, "errors": 0},
        {"cpu": 42, "memory": 61, "disk_io": 125, "errors": 1},
    ],
    test=[
        {"cpu": 46, "memory": 62, "disk_io": 119, "errors": 0},    # ✅ normal
        {"cpu": 99, "memory": 95, "disk_io": 800, "errors": 150},   # 🚨 anomaly
    ],
)

for r in result.results:
    print(f"{'🚨' if r.is_anomaly else '✅'}  score={r.score:.1f}  confidence={r.confidence:.0%}")
```

### Flag a fraudulent transaction

```python
result = wg.scan(
    training=[
        {"amount": 74.50, "items": 3, "session_sec": 340, "returning": 1},
        {"amount": 52.00, "items": 2, "session_sec": 280, "returning": 1},
        {"amount": 89.99, "items": 4, "session_sec": 410, "returning": 0},
    ],
    test=[
        {"amount": 68.00, "items": 2, "session_sec": 300, "returning": 1},     # ✅ normal
        {"amount": 4200.00, "items": 25, "session_sec": 8, "returning": 0},     # 🚨 fraud
    ],
)
```

### Catch a security event in logs

```python
result = wg.scan(
    training=[
        "2026-02-24 10:15:03 INFO  Request processed in 45ms [200 OK]",
        "2026-02-24 10:15:04 INFO  Request processed in 52ms [200 OK]",
        "2026-02-24 10:15:05 INFO  Cache hit ratio=0.94 ttl=300s",
    ],
    test=[
        "2026-02-24 10:20:03 INFO  Request processed in 48ms [200 OK]",                  # ✅ normal
        "2026-02-24 10:20:04 CRIT  xmrig consuming 98% CPU, port 45678 open",             # 🚨 crypto miner
        "2026-02-24 10:20:05 WARN  GET /api/users?id=1;DROP TABLE users-- from 185.x.x",  # 🚨 SQL injection
    ],
    encoder_type="text",
)
```

**Same client. Same `scan()` call. Any data.**

## Use Cases

WaveGuard works on **any structured, numeric, or text data**. If you can describe "normal," it can detect deviations.

| Industry | What You Scan | What It Catches |
|----------|---------------|------------------|
| **DevOps** | Server metrics (CPU, memory, latency) | Memory leaks, DDoS attacks, runaway processes |
| **Fintech** | Transactions (amount, velocity, location) | Fraud, money laundering, account takeover |
| **Security** | Log files, access events | SQL injection, crypto miners, privilege escalation |
| **IoT / Manufacturing** | Sensor readings (temp, pressure, vibration) | Equipment failure, calibration drift |
| **E-commerce** | User behavior (session time, cart, clicks) | Bot traffic, bulk purchase fraud, scraping |
| **Healthcare** | Lab results, vitals, biomarkers | Abnormal readings, data entry errors |
| **Time Series** | Metric windows (latency, throughput) | Spikes, flatlines, seasonal breaks |

**The API doesn't know your domain.** It just knows what "normal" looks like (your training data) and flags anything that deviates. This makes it general — you bring the context, it brings the detection.

### Supported Data Types

All auto-detected from data shape. No configuration needed:

| Type | Example | Use When |
|------|---------|----------|
| JSON objects | `{"cpu": 45, "memory": 62}` | Structured records with named fields |
| Numeric arrays | `[1.0, 1.2, 5.8, 1.1]` | Feature vectors, embeddings |
| Text strings | `"ERROR segfault at 0x0"` | Logs, messages, free text |
| Time series | `[100, 102, 98, 105, 99]` | Metric windows, sequential readings |

## Examples

Every example is a runnable Python script. They span **6 industries and 4 data types** to show WaveGuard isn't tied to one domain:

| # | Example | Industry | Data Type | What It Shows |
|---|---------|----------|-----------|---------------|
| 01 | [Quickstart](examples/01_quickstart.py) | General | JSON | Minimal scan in 10 lines |
| 02 | [Server Monitoring](examples/02_server_monitoring.py) | DevOps | JSON | Memory leak + DDoS detection |
| 03 | [Log Analysis](examples/03_log_analysis.py) | Security | Text | SQL injection, crypto miner, stack traces |
| 04 | [Time Series](examples/04_time_series.py) | Monitoring | Numeric | Latency spikes, flatline detection |
| 05 | [Azure Migration](examples/05_azure_migration.py) | Enterprise | JSON | Side-by-side Azure replacement |
| 06 | [Batch Scanning](examples/06_batch_scanning.py) | E-commerce | JSON | 20 transactions, fraud flagging |
| 07 | [Error Handling](examples/07_error_handling.py) | Production | — | Retry logic, exponential backoff |

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
- **PyPI**: https://pypi.org/project/WaveGuardClient/
- **Smithery**: https://smithery.ai/server/gpartin/WaveGuardClient
- **Glama MCP**: https://glama.ai/mcp/servers/@gpartin/WaveGuardClient
- **mcp.so**: https://mcp.so/server/WaveGuardClient/gpartin

## License

MIT — see [LICENSE](LICENSE).
