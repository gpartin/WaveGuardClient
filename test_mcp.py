"""Test MCP endpoint: tools/list (verify 3 tools) + waveguard_scan_timeseries."""
import requests
import json

URL = "https://gpartin--waveguard-api-fastapi-app.modal.run/mcp"
HDR = {"Content-Type": "application/json"}


def mcp(method, params=None, msg_id=1):
    body = {"jsonrpc": "2.0", "method": method, "id": msg_id}
    if params:
        body["params"] = params
    r = requests.post(URL, json=body, headers=HDR, timeout=90)
    r.raise_for_status()
    return r.json()


# 1) Initialize
init = mcp("initialize", {"protocolVersion": "2024-11-05",
                           "capabilities": {},
                           "clientInfo": {"name": "test", "version": "1.0"}})
print("=== MCP INITIALIZE ===")
print(f"Server: {init['result']['serverInfo']}")

# 2) tools/list
tools = mcp("tools/list", msg_id=2)
names = [t["name"] for t in tools["result"]["tools"]]
print(f"\n=== MCP TOOLS/LIST ({len(names)} tools) ===")
for n in names:
    print(f"  - {n}")

assert "waveguard_scan_timeseries" in names, "timeseries tool missing!"
print("\nPASS: waveguard_scan_timeseries present")

# 3) Call waveguard_scan_timeseries
import math
# Generate sine wave with a spike anomaly
data = [math.sin(i * 0.3) * 10 + 50 for i in range(40)]
data[35] = 200  # anomaly spike

ts_result = mcp("tools/call", {
    "name": "waveguard_scan_timeseries",
    "arguments": {
        "data": data,
        "window_size": 5,
        "sensitivity": 2.0,
    }
}, msg_id=3)

print("\n=== MCP TIMESERIES SCAN ===")
content = ts_result["result"]["content"]
print(content[0]["text"])

# Parse JSON results
full = json.loads(content[1]["text"])
results = full.get("results", [])
print(f"\nReturned {len(results)} test windows")
any_anomaly = any(r.get("is_anomaly") for r in results)
any_pvalue = any("p_value" in r for r in results)
print(f"Any anomaly detected: {any_anomaly}")
print(f"p_value in results: {any_pvalue}")

# 4) Summary
print("\n=== ALL MCP CHECKS ===")
checks = [
    ("3 tools listed", len(names) == 3),
    ("timeseries tool present", "waveguard_scan_timeseries" in names),
    ("timeseries returns results", len(results) > 0),
    ("p_value in results", any_pvalue),
]
for name, ok in checks:
    print(f"  {'PASS' if ok else 'FAIL'}: {name}")
print(f"\nAll MCP checks passed: {all(ok for _, ok in checks)}")
