# MCP Integration

Use WaveGuard from **Claude Desktop**, **Cursor**, or any MCP-compatible AI agent through the included Model Context Protocol server.

## What is MCP?

[Model Context Protocol](https://modelcontextprotocol.io/) (MCP) lets AI assistants call external tools. The WaveGuard MCP server gives Claude (and other agents) the ability to detect anomalies in any data you discuss.

## Setup — Claude Desktop

### 1. Clone this repo

```bash
git clone https://github.com/gpartin/WaveGuardClient.git
```

### 2. Install dependencies

```bash
pip install requests
```

### 3. Add to Claude Desktop config

**macOS / Linux:** `~/.config/claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

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

### 4. Restart Claude Desktop

The WaveGuard tool icon should appear in Claude's tool list.

## Usage Examples

Once configured, ask Claude naturally:

> "I have these server metrics from the last hour: cpu=45, mem=62, errors=0 (repeated 4 times with slight variations). Now I'm seeing cpu=99, mem=95, errors=150. Is this anomalous?"

> "Check if this log line is unusual compared to normal access logs: 'GET /api/users?id=1;DROP TABLE users-- 404'"

> "Here's a week of daily sales: [1200, 1150, 1300, 1180, 1250, 1220, 1190]. Today's number is 45. Is that an anomaly?"

Claude will automatically call `waveguard_scan` and explain the results.

## Available Tools

### `waveguard_scan`

Detect anomalies. Send normal examples (training) and suspect data (test).

**Parameters:**
- `training` (required): 2+ normal data examples
- `test` (required): 1+ samples to check
- `sensitivity`: 0.5–5.0 (lower = more sensitive)
- `encoder_type`: json, numeric, text, timeseries (auto-detected by default)

### `waveguard_health`

Check if the API is running. No parameters.

## Remote / HTTP Mode

For Smithery, Glama, or remote agents:

```bash
python mcp_server/server.py --http --port 3001
```

Agent config:

```json
{
  "mcpServers": {
    "waveguard": {
      "url": "http://localhost:3001/mcp",
      "transport": "http"
    }
  }
}
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `WAVEGUARD_API_KEY` | *(empty)* | Your API key |
| `WAVEGUARD_API_URL` | Production endpoint | Override API URL |
