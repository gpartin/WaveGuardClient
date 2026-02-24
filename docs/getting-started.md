# Getting Started

Get anomaly detection running in under a minute.

## Install

```bash
pip install WaveGuardClient
```

Or install from source:

```bash
git clone https://github.com/gpartin/WaveGuardClient.git
cd WaveGuardClient
pip install -e .
```

## Get an API Key

1. Visit the [WaveGuard API](https://gpartin--waveguard-api-fastapi-app.modal.run/docs)
2. The demo key `demo` works for testing (rate-limited)
3. For production use, contact us for a key

## Your First Scan

```python
from waveguard import WaveGuard

wg = WaveGuard(api_key="demo")

# One call: learn normal → detect anomalies → tear down
result = wg.scan(
    training=[
        {"cpu": 45, "memory": 62, "errors": 0},
        {"cpu": 48, "memory": 63, "errors": 0},
        {"cpu": 42, "memory": 61, "errors": 1},
    ],
    test=[
        {"cpu": 46, "memory": 62, "errors": 0},    # normal
        {"cpu": 99, "memory": 95, "errors": 150},   # anomaly
    ],
)

for r in result.results:
    print(f"anomaly={r.is_anomaly}  score={r.score:.1f}  confidence={r.confidence:.0%}")
```

## How It Works

WaveGuard doesn't use machine learning. It encodes your data onto a 3D lattice
and runs GPU-accelerated wave physics simulations:

1. **Training data** teaches the lattice what "normal" looks like
2. **Test data** is run through the learned lattice
3. Normal data produces stable wave patterns; anomalies produce divergent ones
4. Statistical comparison flags anomalies with confidence scores
5. Everything is torn down — nothing is stored between calls

## Supported Data Types

All types are auto-detected. You don't need to change anything:

| Type | Example |
|------|---------|
| JSON objects | `{"cpu": 45, "memory": 62}` |
| Numeric arrays | `[1.0, 1.2, 5.8, 1.1]` |
| Text strings | `"ERROR segfault at 0x0"` |
| Time series | `[100, 102, 98, 105, 99]` |

## What's Next

- [API Reference](api-reference.md) — all methods, parameters, and response types
- [MCP Integration](mcp-integration.md) — use WaveGuard from Claude Desktop
- [Azure Migration](azure-migration.md) — replacing Azure Anomaly Detector
- [Examples](../examples/) — 7 runnable examples
