"""
WaveGuard MCP Server — Model Context Protocol for Claude Desktop & AI Agents.

Stateless anomaly detection via wave physics simulation.
One tool: ``waveguard_scan``.  Send training + test data, get anomaly scores.

Transports
----------
- **stdio** (default) — add to Claude Desktop config
- **HTTP** — ``python -m mcp_server --http --port 3001``

Claude Desktop config
~~~~~~~~~~~~~~~~~~~~~
Add to ``~/.config/claude/claude_desktop_config.json``
(macOS/Linux) or ``%APPDATA%\\Claude\\claude_desktop_config.json`` (Windows)::

    {
      "mcpServers": {
        "waveguard": {
          "command": "python",
          "args": ["/path/to/WaveGuardClient/mcp_server/server.py"],
          "env": {
            "WAVEGUARD_API_KEY": "your-key-here"
          }
        }
      }
    }

Smithery / Glama config
~~~~~~~~~~~~~~~~~~~~~~~
::

    {
      "mcpServers": {
        "waveguard": {
          "url": "https://gpartin--waveguard-api-fastapi-app.modal.run/mcp",
          "transport": "http"
        }
      }
    }
"""

from __future__ import annotations

import os
import sys
import json
import argparse
from typing import Any, Dict, List, Optional

# ── Configuration ──────────────────────────────────────────────────────────

API_URL = os.environ.get(
    "WAVEGUARD_API_URL",
    "https://gpartin--waveguard-api-fastapi-app.modal.run",
)
API_KEY = os.environ.get("WAVEGUARD_API_KEY", "")

# ── HTTP client ───────────────────────────────────────────────────────────

try:
    import requests

    _session = requests.Session()
    if API_KEY:
        _session.headers["X-API-Key"] = API_KEY
except ImportError:
    _session = None  # type: ignore[assignment]


def _api_post(path: str, body: dict) -> dict:
    if _session is None:
        raise RuntimeError("requests library required: pip install requests")
    resp = _session.post(f"{API_URL}{path}", json=body, timeout=90)
    resp.raise_for_status()
    return resp.json()


def _api_get(path: str) -> Any:
    if _session is None:
        raise RuntimeError("requests library required: pip install requests")
    resp = _session.get(f"{API_URL}{path}", timeout=30)
    resp.raise_for_status()
    return resp.json()


# ═══════════════════════════════════════════════════════════════════════════
# MCP Tool Definitions
# ═══════════════════════════════════════════════════════════════════════════

TOOLS = [
    {
        "name": "waveguard_scan",
        "description": (
            "Detect anomalies in data using GPU-accelerated wave physics simulation. "
            "Fully stateless — send training data (normal examples) and test data "
            "(samples to check) in ONE call. Returns per-sample anomaly scores, "
            "confidence levels, and the top features explaining WHY each anomaly "
            "was flagged. Works on any data type: JSON objects, numbers, text, "
            "time series, arrays. No separate training step required.\n\n"
            "Example: to check if server metrics are anomalous, send 3-5 normal "
            "readings as training, and the suspect readings as test."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "training": {
                    "type": "array",
                    "description": (
                        "2+ examples of NORMAL/expected data. These define what "
                        "'normal' looks like. All samples should be the same type "
                        "and shape. More samples = better baseline (4-10 is ideal)."
                    ),
                    "minItems": 2,
                },
                "test": {
                    "type": "array",
                    "description": (
                        "1+ data points to check for anomalies. Same type/shape "
                        "as training data. Each sample is scored independently."
                    ),
                    "minItems": 1,
                },
                "sensitivity": {
                    "type": "number",
                    "description": (
                        "Anomaly threshold multiplier (default: 2.0). Lower = more "
                        "sensitive (flags more anomalies). Higher = less sensitive. "
                        "Range: 0.5 to 5.0."
                    ),
                },
                "encoder_type": {
                    "type": "string",
                    "enum": [
                        "json",
                        "numeric",
                        "text",
                        "timeseries",
                        "tabular",
                        "image",
                        "correlation",
                    ],
                    "description": (
                        "Data encoder type. Omit to auto-detect from data shape. "
                        "Auto-detection works well for most data."
                    ),
                },
            },
            "required": ["training", "test"],
        },
    },
    {
        "name": "waveguard_scan_timeseries",
        "description": (
            "Detect anomalies in time-series data using GPU-accelerated wave "
            "physics simulation. Send a flat array of numeric values and a "
            "window size. The tool automatically creates overlapping windows, "
            "uses the first N as training (normal baseline), and scores the "
            "remaining windows as test samples. Returns per-window anomaly "
            "scores, confidence, and p-values.\n\n"
            "Example: send 100 CPU-usage readings with window_size=10. "
            "The first 5 windows become training, the rest are tested."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "data": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": (
                        "Flat array of numeric time-series values in "
                        "chronological order."
                    ),
                    "minItems": 4,
                },
                "window_size": {
                    "type": "integer",
                    "description": (
                        "Number of data points per window (default: 10). "
                        "Smaller windows = finer resolution."
                    ),
                },
                "test_windows": {
                    "type": "integer",
                    "description": (
                        "Number of trailing windows to test (default: auto, "
                        "uses last ~40%% of windows)."
                    ),
                },
                "sensitivity": {
                    "type": "number",
                    "description": (
                        "Anomaly threshold multiplier (default: 2.0). Lower = "
                        "more sensitive. Range: 0.5 to 5.0."
                    ),
                },
            },
            "required": ["data"],
        },
    },
    {
        "name": "waveguard_health",
        "description": (
            "Check WaveGuard API health, GPU availability, version, and engine "
            "status. No authentication required. Use this to verify the service "
            "is running before scanning."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
]


# ═══════════════════════════════════════════════════════════════════════════
# Tool Execution
# ═══════════════════════════════════════════════════════════════════════════


def _execute_timeseries(arguments: dict) -> dict:
    """Sliding-window timeseries scan via the /v1/scan endpoint."""
    data = arguments["data"]
    window = int(arguments.get("window_size", 10))
    sensitivity = arguments.get("sensitivity", 2.0)

    # Build windows
    windows = [data[i : i + window] for i in range(0, len(data) - window + 1)]
    if len(windows) < 3:
        return {
            "content": [
                {
                    "type": "text",
                    "text": (
                        f"Not enough data: {len(data)} points with "
                        f"window_size={window} gives {len(windows)} windows "
                        f"(need at least 3)."
                    ),
                }
            ],
            "isError": True,
        }

    # Split into training / test
    test_count = arguments.get("test_windows")
    if test_count is None:
        test_count = max(1, len(windows) * 2 // 5)
    test_count = min(test_count, len(windows) - 2)

    training = windows[: len(windows) - test_count]
    test = windows[len(windows) - test_count :]

    body: dict = {
        "training": training,
        "test": test,
        "encoder_type": "timeseries",
        "sensitivity": sensitivity,
    }
    result = _api_post("/v1/scan", body)

    # Summarise
    lines = [
        f"Time-series scan: {len(windows)} windows "
        f"(window_size={window}, {len(training)} train, {len(test)} test)",
        "",
    ]
    for i, r in enumerate(result.get("results", [])):
        idx = len(training) + i
        is_anom = r.get("is_anomaly", False)
        conf = r.get("confidence", 0)
        pval = r.get("p_value", 1.0)
        marker = "ANOMALY" if is_anom else "Normal"
        lines.append(
            f"  Window {idx}: {marker} (confidence: {conf:.0%}, "
            f"p-value: {pval:.4f})"
        )
    summary = "\n".join(lines)
    return {
        "content": [
            {"type": "text", "text": summary},
            {"type": "text", "text": json.dumps(result, indent=2)},
        ]
    }


def execute_tool(name: str, arguments: dict) -> dict:
    """Execute an MCP tool and return the result."""
    try:
        if name == "waveguard_scan":
            body: dict = {
                "training": arguments["training"],
                "test": arguments["test"],
            }
            if "sensitivity" in arguments:
                body["sensitivity"] = arguments["sensitivity"]
            if "encoder_type" in arguments:
                body["encoder_type"] = arguments["encoder_type"]

            result = _api_post("/v1/scan", body)

            # Build human-readable summary for the agent
            summary_data = result.get("summary", {})
            total = summary_data.get("total_samples", len(arguments["test"]))
            anomalies = summary_data.get("anomalies_found", 0)
            rate = summary_data.get("anomaly_rate", 0)

            lines = [
                f"Scanned {total} samples: {anomalies} anomalies ({rate:.0%} anomaly rate)",
                "",
            ]

            for i, r in enumerate(result.get("results", [])):
                is_anom = r.get("is_anomaly", False)
                conf = r.get("confidence", 0)
                score = r.get("score", 0)
                marker = "ANOMALY" if is_anom else "Normal"
                line = f"  Sample {i + 1}: {marker} (confidence: {conf:.0%}, score: {score:.1f})"

                if is_anom and r.get("top_features"):
                    feats = r["top_features"][:3]
                    feat_str = ", ".join(
                        f"{f.get('label', '?')} (z={f.get('z_score', 0):.1f})"
                        for f in feats
                    )
                    line += f"\n           Top features: {feat_str}"

                lines.append(line)

            summary = "\n".join(lines)

            return {
                "content": [
                    {"type": "text", "text": summary},
                    {"type": "text", "text": json.dumps(result, indent=2)},
                ]
            }

        elif name == "waveguard_scan_timeseries":
            return _execute_timeseries(arguments)

        elif name == "waveguard_health":
            result = _api_get("/v1/health")
            status = (
                f"Status: {result.get('status', '?')} | "
                f"Version: {result.get('version', '?')} | "
                f"GPU: {result.get('gpu', 'N/A')}"
            )
            return {"content": [{"type": "text", "text": status}]}

        else:
            return {
                "content": [{"type": "text", "text": f"Unknown tool: {name}"}],
                "isError": True,
            }

    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error: {e}"}],
            "isError": True,
        }


# ═══════════════════════════════════════════════════════════════════════════
# MCP Protocol Handler (stdio JSON-RPC transport)
# ═══════════════════════════════════════════════════════════════════════════


class MCPStdioServer:
    """Minimal MCP server implementing JSON-RPC 2.0 over stdio."""

    def __init__(self) -> None:
        self.server_info = {
            "name": "waveguard",
            "version": "2.3.0",
        }

    def handle_message(self, msg: dict) -> Optional[dict]:
        """Process a JSON-RPC 2.0 message and return the response."""
        method = msg.get("method", "")
        msg_id = msg.get("id")
        params = msg.get("params", {})

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {"listChanged": False},
                    },
                    "serverInfo": self.server_info,
                },
            }

        elif method == "notifications/initialized":
            return None

        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {"tools": TOOLS},
            }

        elif method == "tools/call":
            tool_name = params.get("name", "")
            arguments = params.get("arguments", {})
            result = execute_tool(tool_name, arguments)
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": result,
            }

        elif method == "ping":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {},
            }

        else:
            if msg_id is not None:
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}",
                    },
                }
            return None

    def run_stdio(self) -> None:
        """Run the MCP server on stdin/stdout."""
        sys.stderr.write(
            f"WaveGuard MCP server v2.3.0 started (API: {API_URL})\n"
        )
        sys.stderr.flush()

        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                msg = json.loads(line)
            except json.JSONDecodeError as e:
                sys.stderr.write(f"Invalid JSON: {e}\n")
                sys.stderr.flush()
                continue

            response = self.handle_message(msg)
            if response is not None:
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()


# ═══════════════════════════════════════════════════════════════════════════
# HTTP transport (for remote MCP clients / Smithery / Glama)
# ═══════════════════════════════════════════════════════════════════════════


def run_http_server(port: int = 3001) -> None:
    """Run MCP over HTTP for remote agent access."""
    try:
        from fastapi import FastAPI as FA
        import uvicorn
    except ImportError:
        print("HTTP transport requires: pip install fastapi uvicorn")
        sys.exit(1)

    mcp_app = FA(title="WaveGuard MCP Server", version="2.3.0")
    server = MCPStdioServer()

    @mcp_app.post("/mcp")
    async def mcp_endpoint(request: dict) -> dict:  # type: ignore[type-arg]
        return server.handle_message(request)  # type: ignore[return-value]

    @mcp_app.get("/mcp/tools")
    async def mcp_tools() -> dict:  # type: ignore[type-arg]
        return {"tools": TOOLS}

    print(f"WaveGuard MCP HTTP server v2.3.0 on port {port}")
    uvicorn.run(mcp_app, host="0.0.0.0", port=port)


# ═══════════════════════════════════════════════════════════════════════════
# Entry point
# ═══════════════════════════════════════════════════════════════════════════

def main():
    """Entry point for `waveguard-mcp` console script."""
    parser = argparse.ArgumentParser(
        description="WaveGuard MCP Server v2.3.0"
    )
    parser.add_argument(
        "--http",
        action="store_true",
        help="Use HTTP transport instead of stdio",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=3001,
        help="HTTP port (default: 3001)",
    )
    parser.add_argument(
        "--api-url",
        type=str,
        default=None,
        help="WaveGuard API URL (overrides $WAVEGUARD_API_URL)",
    )
    args = parser.parse_args()

    global API_URL
    if args.api_url:
        API_URL = args.api_url

    if args.http:
        run_http_server(args.port)
    else:
        server = MCPStdioServer()
        server.run_stdio()


if __name__ == "__main__":
    main()
