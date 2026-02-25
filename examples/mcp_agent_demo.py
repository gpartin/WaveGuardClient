#!/usr/bin/env python3
"""
AI Agent Anomaly Detection via MCP
===================================

Show how an AI agent (Claude, GPT, etc.) can use WaveGuard as an MCP tool
to detect anomalies in data — no ML knowledge needed by the agent or user.

This example demonstrates the MCP protocol flow that happens when a user
asks Claude: "Check if any of these sensor readings look weird."

For actual MCP integration with Claude Desktop, see:
  https://github.com/gpartin/WaveGuardClient/blob/main/docs/mcp-integration.md

Run:
    pip install WaveGuardClient
    python mcp_agent_demo.py
"""

import json
import requests


def main():
    print("=" * 65)
    print("  WaveGuard MCP Tool Demo — AI Agent Anomaly Detection")
    print("  First physics-based anomaly detector available as MCP tool")
    print("=" * 65)

    API_URL = "https://gpartin--waveguard-api-fastapi-app.modal.run"

    # ── Step 1: Show available MCP tools ──────────────────────────────
    print("\n  Step 1: Agent discovers available tools via MCP\n")

    list_msg = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list",
        "params": {},
    }

    resp = requests.post(f"{API_URL}/mcp", json=list_msg)
    tools = resp.json()["result"]["tools"]
    for tool in tools:
        print(f"    🔧 {tool['name']}: {tool['description'][:60]}...")

    # ── Step 2: Agent scans structured data ───────────────────────────
    print("\n  Step 2: Agent calls waveguard_scan with user's data\n")

    scan_msg = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "waveguard_scan",
            "arguments": {
                "training": [
                    {"cpu": 45, "memory": 62, "errors": 0},
                    {"cpu": 48, "memory": 63, "errors": 0},
                    {"cpu": 42, "memory": 61, "errors": 1},
                    {"cpu": 50, "memory": 64, "errors": 0},
                    {"cpu": 47, "memory": 62, "errors": 0},
                ],
                "test": [
                    {"cpu": 46, "memory": 62, "errors": 0},
                    {"cpu": 99, "memory": 95, "errors": 150},
                    {"cpu": 44, "memory": 63, "errors": 0},
                ],
            },
        },
    }

    resp = requests.post(f"{API_URL}/mcp", json=scan_msg)
    result = resp.json()["result"]
    # First content block is human-readable summary
    print(f"    Agent receives:\n")
    for line in result["content"][0]["text"].split("\n")[:8]:
        print(f"    {line}")

    # ── Step 3: Agent scans time-series ───────────────────────────────
    print("\n\n  Step 3: Agent calls waveguard_scan_timeseries\n")

    # Simulate temperature sensor with an anomalous spike
    import random
    random.seed(42)
    normal_data = [round(72 + random.gauss(0, 2), 1) for _ in range(50)]
    # Inject anomaly at positions 35-39
    anomalous_data = normal_data.copy()
    anomalous_data[35:40] = [95.2, 97.1, 110.3, 98.7, 92.4]

    ts_msg = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "waveguard_scan_timeseries",
            "arguments": {
                "data": anomalous_data,
                "window_size": 5,
            },
        },
    }

    resp = requests.post(f"{API_URL}/mcp", json=ts_msg)
    result = resp.json()["result"]
    print(f"    Agent receives:\n")
    for line in result["content"][0]["text"].split("\n")[:10]:
        print(f"    {line}")

    # ── Step 4: Show Claude Desktop config ────────────────────────────
    print("\n\n  Step 4: Add WaveGuard to Claude Desktop\n")
    print("    Add this to your claude_desktop_config.json:\n")

    config = {
        "mcpServers": {
            "waveguard": {
                "command": "uvx",
                "args": ["--from", "WaveGuardClient", "waveguard-mcp"],
            }
        }
    }
    print(f"    {json.dumps(config, indent=4).replace(chr(10), chr(10) + '    ')}")

    print("\n    Then ask Claude: 'Check these readings for anomalies'")
    print("    Claude will call waveguard_scan automatically.\n")

    # ── Summary ───────────────────────────────────────────────────────
    print("  " + "─" * 60)
    print("  Why MCP + WaveGuard?")
    print("    • AI agent does anomaly detection with ZERO ML knowledge")
    print("    • Works on any data type (JSON, numbers, time-series)")
    print("    • No model management — fully stateless")
    print("    • Physics-based: zero-config, no hyperparameters")
    print("    • GPU-accelerated: 100ms per sample on NVIDIA T4")
    print()


if __name__ == "__main__":
    main()
