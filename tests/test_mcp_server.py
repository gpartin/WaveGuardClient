"""
Tests for the WaveGuard MCP server tool execution.
"""

import json
import pytest
from unittest.mock import patch, MagicMock


# We need to mock requests before importing the server
@pytest.fixture(autouse=True)
def mock_requests():
    with patch.dict("os.environ", {"WAVEGUARD_API_KEY": "test-key"}):
        yield


class TestToolExecution:
    def test_health_tool(self):
        with patch("mcp_server.server._api_get") as mock_get:
            mock_get.return_value = {
                "status": "healthy",
                "version": "2.0.0",
                "gpu": "T4",
            }

            from mcp_server.server import execute_tool

            result = execute_tool("waveguard_health", {})

            assert not result.get("isError")
            text = result["content"][0]["text"]
            assert "healthy" in text
            assert "T4" in text

    def test_scan_tool(self):
        with patch("mcp_server.server._api_post") as mock_post:
            mock_post.return_value = {
                "results": [
                    {
                        "is_anomaly": True,
                        "confidence": 0.95,
                        "score": 8.0,
                        "top_features": [
                            {"label": "cpu", "z_score": 4.2}
                        ],
                    }
                ],
                "summary": {
                    "total_samples": 1,
                    "anomalies_found": 1,
                    "anomaly_rate": 1.0,
                },
            }

            from mcp_server.server import execute_tool

            result = execute_tool(
                "waveguard_scan",
                {
                    "training": [{"cpu": 45}, {"cpu": 48}],
                    "test": [{"cpu": 99}],
                },
            )

            assert not result.get("isError")
            assert len(result["content"]) == 2
            assert "ANOMALY" in result["content"][0]["text"]

    def test_unknown_tool(self):
        from mcp_server.server import execute_tool

        result = execute_tool("nonexistent_tool", {})
        assert result.get("isError") is True
        assert "Unknown tool" in result["content"][0]["text"]

    def test_scan_error_handling(self):
        with patch("mcp_server.server._api_post") as mock_post:
            mock_post.side_effect = Exception("Connection failed")

            from mcp_server.server import execute_tool

            result = execute_tool(
                "waveguard_scan",
                {
                    "training": [{"a": 1}, {"a": 2}],
                    "test": [{"a": 3}],
                },
            )

            assert result.get("isError") is True
            assert "Connection failed" in result["content"][0]["text"]


class TestMCPProtocol:
    def test_initialize(self):
        from mcp_server.server import MCPStdioServer

        server = MCPStdioServer()
        response = server.handle_message(
            {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
        )

        assert response["id"] == 1
        assert response["result"]["protocolVersion"] == "2024-11-05"
        assert response["result"]["serverInfo"]["name"] == "waveguard"

    def test_tools_list(self):
        from mcp_server.server import MCPStdioServer

        server = MCPStdioServer()
        response = server.handle_message(
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
        )

        tools = response["result"]["tools"]
        names = [t["name"] for t in tools]
        assert "waveguard_scan" in names
        assert "waveguard_health" in names

    def test_ping(self):
        from mcp_server.server import MCPStdioServer

        server = MCPStdioServer()
        response = server.handle_message(
            {"jsonrpc": "2.0", "id": 3, "method": "ping"}
        )

        assert response["id"] == 3
        assert response["result"] == {}

    def test_unknown_method(self):
        from mcp_server.server import MCPStdioServer

        server = MCPStdioServer()
        response = server.handle_message(
            {"jsonrpc": "2.0", "id": 4, "method": "unknown/method", "params": {}}
        )

        assert "error" in response
        assert response["error"]["code"] == -32601

    def test_notification_returns_none(self):
        from mcp_server.server import MCPStdioServer

        server = MCPStdioServer()
        response = server.handle_message(
            {"jsonrpc": "2.0", "method": "notifications/initialized"}
        )

        assert response is None
