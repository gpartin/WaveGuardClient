"""
Example 3: Log Analysis — detect unusual log messages.

WaveGuard handles text natively. Send normal log lines as training,
and it detects unusual patterns in new log lines.

Usage:
    export WAVEGUARD_API_KEY="your-key"
    python 03_log_analysis.py
"""

import os
from waveguard import WaveGuard

api_key = os.environ.get("WAVEGUARD_API_KEY", "demo")
wg = WaveGuard(api_key=api_key)

# ── Normal log lines (what healthy operations look like) ──────────────────
normal_logs = [
    "2026-02-24 10:15:03 INFO  Request processed in 45ms [200 OK]",
    "2026-02-24 10:15:04 INFO  Request processed in 52ms [200 OK]",
    "2026-02-24 10:15:05 INFO  Cache hit ratio=0.94 ttl=300s",
    "2026-02-24 10:15:06 INFO  Request processed in 38ms [200 OK]",
    "2026-02-24 10:15:07 DEBUG Healthcheck passed cpu=35% mem=55%",
    "2026-02-24 10:15:08 INFO  Request processed in 41ms [200 OK]",
]

# ── New log lines to check ────────────────────────────────────────────────
suspect_logs = [
    # Normal
    "2026-02-24 10:20:03 INFO  Request processed in 48ms [200 OK]",
    # Suspicious — stack trace in a log line
    "2026-02-24 10:20:04 ERROR Unhandled NullPointerException at com.app.service.UserService.getUser(UserService.java:142)",
    # Normal
    "2026-02-24 10:20:05 INFO  Cache hit ratio=0.93 ttl=300s",
    # Suspicious — SQL injection attempt in access log
    "2026-02-24 10:20:06 WARN  GET /api/users?id=1;DROP TABLE users-- 404 from 185.220.101.42",
    # Suspicious — Bitcoin miner detected
    "2026-02-24 10:20:07 CRIT  Process xmrig consuming 98% CPU, listening on port 45678",
]

# ── Scan with text encoder ────────────────────────────────────────────────
result = wg.scan(
    training=normal_logs,
    test=suspect_logs,
    encoder_type="text",
)

# ── Report ────────────────────────────────────────────────────────────────
print("=== Log Anomaly Scan ===\n")

for i, r in enumerate(result.results):
    log_line = suspect_logs[i]
    status = "🚨 ANOMALY" if r.is_anomaly else "✅ Normal"
    # Truncate long log lines for display
    display = log_line[:80] + "..." if len(log_line) > 80 else log_line
    print(f"  {status}  (score={r.score:.1f}, conf={r.confidence:.0%})")
    print(f"           {display}")
    print()

print(f"Summary: {result.summary.anomalies_found}/{result.summary.total_test_samples} anomalous lines")
