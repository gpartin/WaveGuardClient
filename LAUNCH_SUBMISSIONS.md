# WaveGuard Launch Submissions

## 1. awesome-mcp-servers PR

**File to edit in their repo**: `README.md` under the relevant category (Analytics / Data / Science)

**Entry to add:**

```markdown
- [WaveGuard](https://github.com/gpartin/WaveGuardClient) - Physics-based anomaly detection via GPU-accelerated wave simulation. Zero-config, stateless, works on any data type. 90% precision (3x fewer false alarms than Isolation Forest). `pip install WaveGuardClient`
```

**PR Title:** `Add WaveGuard - physics-based anomaly detection MCP server`

**PR Body:**

WaveGuard is an anomaly detection MCP server powered by GPU-accelerated wave physics instead of machine learning.

**Why it's useful for MCP users:**
- AI agents can detect anomalies with zero ML knowledge
- Works on any data: JSON, numbers, text, time-series
- Fully stateless — one API call, no model management
- 90% average precision (lowest false alarm rate vs sklearn methods)
- GPU-accelerated on NVIDIA T4

**MCP Tools:**
- `waveguard_scan` — Detect anomalies in structured data
- `waveguard_scan_timeseries` — Auto-window time-series anomaly detection
- `waveguard_health` — API health check

**Setup:**
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

**Links:**
- PyPI: https://pypi.org/project/WaveGuardClient/
- GitHub: https://github.com/gpartin/WaveGuardClient
- Benchmarks: https://github.com/gpartin/WaveGuardClient/tree/main/benchmarks

---

## 2. Show HN Post

**Title:** `Show HN: WaveGuard – Anomaly detection with wave physics, not ML (MCP + API)`

**Body:**

Hi HN,

I built an anomaly detection API that uses GPU-accelerated wave physics simulation instead of machine learning. You send it data (any type), it runs a coupled-wave simulation on NVIDIA T4 GPUs, and tells you what's anomalous.

**Key difference from sklearn/PyOD/ML approaches:**
- 90% average precision vs 60% for Isolation Forest (3× fewer false alarms)
- Zero configuration — no hyperparameters, no contamination fraction, no n_neighbors
- Fully stateless — no model training, no state management, no drift
- Works as an MCP tool — Claude can do anomaly detection with zero ML knowledge

**How it works:**
Your data is encoded onto a 64³ lattice. Normal data is fed through with wave equation dynamics active (chi adapts). Then test data is propagated through the frozen landscape — normal data resonates smoothly, anomalies scatter. A 52-dimensional fingerprint is compared via Mahalanobis distance.

**Benchmarks against sklearn (6 scenarios):**
- WaveGuard: 90% precision, 58% recall
- Isolation Forest: 60% precision, 95% recall
- LOF: 66% precision, 98% recall

WaveGuard trades recall for precision. For production alerting where false alarms cause SRE pages at 3am, that's the right tradeoff.

**Try it:**
```
pip install WaveGuardClient
```

```python
from waveguard import WaveGuard
wg = WaveGuard()  # free tier, no key needed
result = wg.scan(
    training=[{"cpu": 45}, {"cpu": 48}, {"cpu": 42}],
    test=[{"cpu": 46}, {"cpu": 99}]
)
```

Free tier: 100 scans/month, GPU-accelerated, no API key required.

GitHub: https://github.com/gpartin/WaveGuardClient
Benchmarks: https://github.com/gpartin/WaveGuardClient/tree/main/benchmarks

---

## 3. Reddit r/MachineLearning Post

**Title:** `[P] Physics-based anomaly detection that beats Isolation Forest on precision (90% vs 60%)`

**Body:**

Built an anomaly detection API that uses wave physics simulation instead of ML. Benchmarked against sklearn across 6 scenarios:

| Method | Avg Precision | Avg F1 |
|--------|:---:|:---:|
| **WaveGuard** | **0.90** | 0.65 |
| LOF | 0.66 | 0.79 |
| IsolationForest | 0.60 | 0.72 |
| OneClassSVM | 0.53 | 0.68 |

**The tradeoff:** WaveGuard flags fewer anomalies, but when it flags one, it's almost always right. For production alerting (SRE pages, SCADA alarms), minimizing false positives matters more than catching every edge case.

**How it works:**
- Each data sample is encoded onto a 64³ lattice
- Training data sculpts a "chi landscape" via coupled wave equations (Klein-Gordon + gravitational coupling)
- Test data propagates through the frozen landscape
- Normal data resonates; anomalies scatter off the learned structure
- Fully stateless — one API call, nothing persisted

**Key features:**
- GPU-accelerated (NVIDIA T4)
- Works on any data type (JSON, text, numbers, time-series)
- Available as an MCP tool for AI agents
- Free tier: 100 scans/month, no API key needed

`pip install WaveGuardClient`

Code + benchmarks: https://github.com/gpartin/WaveGuardClient

---

## 4. Reddit r/IoT / r/SCADA Post

**Title:** `Physics-based anomaly detection for industrial IoT sensors — no ML expertise needed`

**Body:**

If you're running sensor monitoring on pumps, compressors, or any rotating equipment, here's an anomaly detection API that works with zero ML knowledge:

```python
from waveguard import WaveGuard

wg = WaveGuard()
result = wg.scan(
    training=last_hour_of_readings,  # list of dicts
    test=[current_reading],
)
if result.results[0].is_anomaly:
    send_maintenance_alert()
```

**What makes it different from ML-based solutions:**
- No model training, no hyperparameters, no drift
- 100% precision on IoT sensor data in benchmarks (zero false alarms)
- Works with any sensor schema — just pass dicts with your field names
- One API call: send baseline readings + new reading → get anomaly flag
- Also available as MCP tool for AI-assisted monitoring

We tested it against bearing failures, seal leaks, motor overloads, and voltage sags. It catches catastrophic failures reliably with zero false alarms. Subtle faults (like slow pressure leaks) sometimes slip through — that's the tradeoff for no false pages at 3am.

Free tier: 100 scans/month, GPU-accelerated.
`pip install WaveGuardClient`

Full example: https://github.com/gpartin/WaveGuardClient/blob/main/examples/iot_predictive_maintenance.py

---

## 5. Reddit r/MCP Post

**Title:** `WaveGuard MCP Server — Give Claude anomaly detection with zero ML knowledge`

**Body:**

Published an MCP server that adds anomaly detection to Claude Desktop. Uses wave physics simulation on GPU instead of ML.

**Setup (30 seconds):**

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

**Then ask Claude:**
> "Check if any of these server metrics look anomalous: cpu=45 mem=62 errors=0, cpu=99 mem=95 errors=150"

Claude calls `waveguard_scan`, gets back anomaly flags, confidence scores, and which features triggered the alert.

**Three tools:**
- `waveguard_scan` — any structured data
- `waveguard_scan_timeseries` — auto-windows time-series data
- `waveguard_health` — API status

**Why physics instead of ML?** Zero config. No contamination fraction, no n_neighbors, no nu parameter. The agent just sends data and gets results. 90% precision means very few false alarms.

Free tier: 100 scans/month, GPU-accelerated, no API key.

PyPI: `pip install WaveGuardClient`
GitHub: https://github.com/gpartin/WaveGuardClient
