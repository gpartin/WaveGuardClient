<p align="center">
  <img src="https://img.shields.io/pypi/v/WaveGuardClient?style=for-the-badge&color=blueviolet" alt="PyPI">
    <img src="https://img.shields.io/badge/API-v3.3.0_stateless-brightgreen?style=for-the-badge" alt="v3.3.0">
  <img src="https://img.shields.io/badge/GPU--powered_API-server--side_CUDA-76B900?style=for-the-badge&logo=nvidia" alt="GPU-powered API">
  <img src="https://img.shields.io/badge/MCP-Claude_Desktop-orange?style=for-the-badge" alt="MCP">
  <a href="https://smithery.ai/servers/emergentphysicslab/waveguard"><img src="https://smithery.ai/badge/emergentphysicslab/waveguard" alt="Smithery"></a>
</p>

<h1 align="center">WaveGuard Python SDK</h1>

<p align="center">
  <strong>Anomaly detection powered by wave physics. Not machine learning.</strong><br>
  One API call. Fully stateless. Works on any data type.
</p>

<p align="center">
  <a href="#benchmarks">Benchmarks</a> •
  <a href="#quickstart">Quickstart</a> •
  <a href="#use-cases">Use Cases</a> •
  <a href="#examples">Examples</a> •
  <a href="#mcp-server-claude-desktop">MCP / Claude</a> •
  <a href="docs/api-reference.md">API Reference</a>
</p>

---

## What is WaveGuard?

WaveGuard is a **general-purpose anomaly detection API**. Send it any data — server metrics, financial transactions, log files, sensor readings, time series — and get back anomaly scores, confidence levels, and explanations of *which features* triggered the alert.

**No training pipelines. No model management. No state. One API call.**

```
Your data  →  WaveGuard API (GPU)  →  Anomaly scores + explanations
```

Under the hood, it uses GPU-accelerated wave physics instead of machine learning. You don't need to know or care about the physics — it's all server-side.

### Modal dashboard vs API endpoints

If you look at Modal, you will see deployed **functions** (for example `fastapi_app`, `gpu_scan`, `gpu_fingerprint`).
Those are compute/runtime units, not the HTTP route list.

To see all live API endpoints, use:
- OpenAPI docs: `https://gpartin--waveguard-api-fastapi-app.modal.run/docs`
- OpenAPI JSON: `https://gpartin--waveguard-api-fastapi-app.modal.run/openapi.json`

<details>
<summary><strong>How does it actually work?</strong></summary>

Your data is encoded onto a 64³ lattice and run through coupled wave equation simulations on GPU. Normal data produces stable wave patterns; anomalies produce divergent ones. A 52-dimensional statistical fingerprint is compared between training and test data. Everything is torn down after each call — nothing is stored.

The key advantage over ML: no training data requirements (2+ samples is enough), no model drift, no retraining, no hyperparameter tuning. Same API call works on structured data, text, numbers, and time series.

</details>

## Benchmarks (v2.2)

**WaveGuard v2.2 vs scikit-learn** across 6 real-world scenarios (10 training + 10 test samples each).

> **TL;DR**: WaveGuard v2.2 **wins 4 of 6 scenarios** and averages 0.76 F1 — competitive with sklearn methods while requiring zero ML expertise.

### F1 Score (balanced precision-recall)

| Scenario | WaveGuard | IsolationForest | LOF | OneClassSVM |
|----------|:---------:|:---------------:|:---:|:-----------:|
| Server Metrics (IT Ops) | **0.87** | 0.71 | 0.87 | 0.62 |
| Financial Fraud | **0.83** | 0.74 | 0.77 | 0.77 |
| IoT Sensors (Industrial) | **0.87** | 0.69 | 0.69 | 0.65 |
| Network Traffic (Security) | **0.82** | 0.61 | 0.77 | 0.61 |
| Time-Series (Monitoring) | 0.46 | 0.77 | **0.80** | 0.67 |
| Sparse Features (Logs) | 0.72 | **0.90** | 0.82 | 0.78 |
| **Average** | **0.76** | 0.74 | **0.79** | 0.68 |

### What's new in v2.2

Multi-resolution scoring tracks each feature's **local lattice energy** in addition to global fingerprint distance. This catches subtle per-feature anomalies (like 3 of 10 IoT sensors drifting) that v2.1's global averaging missed. IoT F1 improved from 0.30 → 0.87.

### When to choose WaveGuard over sklearn

| Choose WaveGuard when... | Choose sklearn when... |
|--------------------------|------------------------|
| False alarms are expensive (alert fatigue, SRE pages) | You need to catch every possible anomaly |
| You have no ML expertise on the team | You have data scientists who can tune models |
| You need a zero-config API call | You can manage model lifecycle (train/save/load) |
| Data schema changes frequently | Feature engineering is stable |
| Your AI agent needs anomaly detection (MCP) | Everything runs locally, no API calls |

<details>
<summary><strong>Reproduce these benchmarks</strong></summary>

```bash
pip install WaveGuardClient scikit-learn
python benchmarks/benchmark_vs_sklearn.py
```

Results saved to `benchmarks/benchmark_results.json`. Benchmarks use deterministic random seeds for reproducibility.

</details>

> **Expanded benchmarks**: WaveGuard ranks #1 in F1 score on all 12 public benchmark datasets. See the full comparison on [HuggingFace](https://huggingface.co/datasets/emergentphysicslab/waveguard-benchmarks).

## Real-World Validation: Crypto Crash Detection

WaveGuard powers [CryptoGuard](https://github.com/gpartin/CryptoGuard), a crypto risk scanner. Backtested against 7 historical crashes (LUNA, FTX, Celsius, 3AC, UST, SOL/FTX, TITAN):

| Method | Recall | Avg Lead Time | False Positive Rate |
|--------|--------|---------------|---------------------|
| **WaveGuard** | **100% (7/7)** | **27.4 days** | **6.1%** |
| Z-score baseline | 100% (7/7) | 28.4 days | 29.9% |
| Rolling volatility | 86% (6/7) | 15.5 days | 4.0% |

WaveGuard flagged FTT (FTX token) at CAUTION on October 16, 2022 — **23 days before the 94% crash** — while z-score analysis showed nothing unusual.

5× fewer false alarms than statistical baselines with the same recall. Full results: [CryptoGuard backtest](https://github.com/gpartin/CryptoGuard/tree/main/backtest).

## Install

```bash
pip install WaveGuardClient
```

That's it. The only dependency is `requests`. All physics runs server-side on GPU.

**[Get your free API key on RapidAPI →](https://rapidapi.com/gpartin/api/waveguard)**

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

Every example is a runnable Python script that hits the live API:

| # | Example | Industry | What It Shows |
|---|---------|----------|---------------|
| 🏭 | [IoT Predictive Maintenance](examples/iot_predictive_maintenance.py) | Manufacturing | Detect bearing failure, leaks, overloads from sensor data |
| 🔒 | [Network Intrusion Detection](examples/network_intrusion_detection.py) | Cybersecurity | Catch port scans, C2 beacons, DDoS, data exfiltration |
| 🤖 | [MCP Agent Demo](examples/mcp_agent_demo.py) | AI/Agents | Claude calls WaveGuard via MCP — zero ML knowledge |
| 01 | [Quickstart](examples/01_quickstart.py) | General | Minimal scan in 10 lines |
| 02 | [Server Monitoring](examples/02_server_monitoring.py) | DevOps | Memory leak + DDoS detection |
| 03 | [Log Analysis](examples/03_log_analysis.py) | Security | SQL injection, crypto miner detection |
| 04 | [Time Series](examples/04_time_series.py) | Monitoring | Latency spikes, flatline detection |
| 06 | [Batch Scanning](examples/06_batch_scanning.py) | E-commerce | 20 transactions, fraud flagging |
| 07 | [Error Handling](examples/07_error_handling.py) | Production | Retry logic, exponential backoff |

```bash
pip install WaveGuardClient
python examples/iot_predictive_maintenance.py
```

## MCP Server (Claude Desktop)

**The first physics-based anomaly detector available as an MCP tool.** Give any AI agent the ability to detect anomalies — zero ML knowledge required.

### Quick setup

```json
{
  "mcpServers": {
    "waveguard": {
      "command": "uvx",
      "args": ["--from", "WaveGuardClient", "waveguard-mcp"]
    }
  }
}
```

Then ask Claude: *"Are any of these sensor readings anomalous?"* — it calls `waveguard_scan` automatically.

### Available MCP tools

| Tool | Description |
|------|-------------|
| `waveguard_scan` | Detect anomalies in any structured data |
| `waveguard_scan_timeseries` | Auto-window time-series and detect anomalous segments |
| `waveguard_health` | Check API status and GPU availability |

See the [MCP Agent Demo](examples/mcp_agent_demo.py) for a working example, or the [MCP Integration Guide](docs/mcp-integration.md) for full setup.

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

### Advanced intelligence methods (v3.3.0)

- `wg.counterfactual(...)`
- `wg.trajectory_scan(...)`
- `wg.instability(...)`
- `wg.phase_coherence(...)`
- `wg.interaction_matrix(...)`
- `wg.cascade_risk(...)`
- `wg.mechanism_probe(...)`
- `wg.action_surface(...)`
- `wg.multi_horizon_outlook(...)`

These map directly to `/v1/*` intelligence endpoints and return the raw JSON payload
for maximal compatibility with rapidly evolving server-side response schemas.

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
│   └── server.py           # stdio + HTTP transport
├── benchmarks/             # Reproducible benchmarks vs sklearn
│   ├── benchmark_vs_sklearn.py
│   └── benchmark_results.json
├── examples/               # 9 runnable examples
├── docs/                   # Documentation
│   ├── getting-started.md
│   ├── api-reference.md
│   ├── mcp-integration.md
│   └── azure-migration.md
├── tests/                  # Test suite
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

- **RapidAPI** (get your API key): https://rapidapi.com/gpartin/api/waveguard
- **Live API**: https://gpartin--waveguard-api-fastapi-app.modal.run
- **Interactive Docs (Swagger)**: https://gpartin--waveguard-api-fastapi-app.modal.run/docs
- **PyPI**: https://pypi.org/project/WaveGuardClient/
- **Smithery**: https://smithery.ai/servers/emergentphysicslab/waveguard
- **Glama**: https://glama.ai/mcp/connectors/com.emergentphysicslab/waveguard

## License

MIT — see [LICENSE](LICENSE).
