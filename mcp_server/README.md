# WaveGuard MCP Server

An [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) server that gives AI agents — including **Claude Desktop**, **Cursor**, and any MCP-compatible client — access to WaveGuard anomaly detection.

## Quick Setup (Claude Desktop)

### 1. Install dependencies

```bash
pip install requests
```

### 2. Add to Claude Desktop config

**macOS / Linux**: `~/.config/claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "waveguard": {
      "command": "python",
      "args": ["/absolute/path/to/WaveGuardClient/mcp_server/server.py"],
      "env": {
        "WAVEGUARD_API_KEY": "your-key-here"
      }
    }
  }
}
```

### 3. Restart Claude Desktop

Claude can now use WaveGuard! Try asking:

> "Check if these server metrics have any anomalies. Normal readings: cpu=45, memory=62, errors=0; cpu=48, memory=63, errors=0; cpu=42, memory=61, errors=1; cpu=50, memory=64, errors=0. Check this reading: cpu=99, memory=95, errors=150."

## Available Tools

### `waveguard_scan`

Detect anomalies in any data type. Send training (normal) + test (suspect) data in one call.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `training` | array | Yes | 2+ examples of normal data |
| `test` | array | Yes | 1+ samples to check |
| `sensitivity` | number | No | 0.5–5.0, lower = more sensitive |
| `encoder_type` | string | No | Force: json, numeric, text, timeseries |

### `waveguard_health`

Check API status, GPU availability, and version. No auth required.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `WAVEGUARD_API_KEY` | *(empty)* | Your API key |
| `WAVEGUARD_API_URL` | `https://gpartin--waveguard-api-fastapi-app.modal.run` | API endpoint |

## HTTP Transport

For remote agents (Smithery, Glama, etc.), run in HTTP mode:

```bash
python server.py --http --port 3001
```

Then configure your agent to connect to `http://localhost:3001/mcp`.
