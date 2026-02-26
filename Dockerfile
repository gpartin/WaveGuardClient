FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml README.md LICENSE ./
COPY waveguard/ waveguard/
COPY mcp_server/ mcp_server/

RUN pip install --no-cache-dir .

EXPOSE 3001

# Default: stdio transport (Claude Desktop / MCP clients)
# Override with --http for HTTP transport
ENTRYPOINT ["python", "-m", "mcp_server.server"]
