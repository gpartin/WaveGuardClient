# Changelog

All notable changes to this project will be documented in this file.

## [2.3.0] — 2026-02-24

### Added
- **Automatic retry with exponential backoff**: `max_retries=2` by default.
  Retries on 429, 500, 502, 503, 504, connection errors, and timeouts.
  Respects server `Retry-After` header.
- **Environment variable auto-read**: SDK reads `WAVEGUARD_API_KEY` from env
  if no `api_key` is passed. Matches stripe/openai SDK pattern.
- **Debug logging**: `logging.getLogger("waveguard")` for request-level
  diagnostics. Enable with `logging.basicConfig(level=logging.DEBUG)`.
- **MCP console script**: `pip install WaveGuardClient[mcp]` now installs
  `waveguard-mcp` command. Works with `uvx --from WaveGuardClient waveguard-mcp`.

### Fixed
- MCP server was excluded from PyPI package — `mcp_server/` now included
- Non-JSON 200 responses now raise `WaveGuardError` instead of silently
  returning zeroed results

### Improved
- Error messages now suggest `WAVEGUARD_API_KEY` env var on auth failures
- Clearer timeout error messages include retry count

## [2.2.0] — 2026-02-24

### Added
- Multi-resolution scoring: per-feature local energy measurement alongside global fingerprint
- PCA dimensionality reduction when n_samples < n_dims
- Adaptive per-feature z-score thresholds (Bonferroni-style correction)
- New response fields: `global_anomaly`, `feature_anomaly`, `anomalous_features`

### Improved
- IoT F1: 0.30 → 0.87 (+190%) — subtle per-feature anomalies now detected
- Average F1: 0.65 → 0.76 (+17%) across 6 benchmark scenarios
- WaveGuard now wins 4/6 scenarios vs sklearn (was 1/6)

## [2.0.0] — 2026-02-24

### Added
- Initial public release of the WaveGuard Python SDK
- `WaveGuard` client class with `scan()`, `health()`, and `tier()` methods
- Full exception hierarchy: `AuthenticationError`, `ValidationError`, `RateLimitError`, `ServerError`
- MCP server for Claude Desktop & AI agent integration (stdio + HTTP transports)
- 7 runnable examples covering all major use cases
- Documentation: getting started, API reference, MCP integration, Azure migration guide
- Test suite with mocked HTTP responses (runs offline)
- `pip install WaveGuardClient` with minimal dependencies (just `requests`)

### Key Features
- **One-call API**: Send training + test data → get anomaly scores back
- **Fully stateless**: Nothing persists between calls
- **Any data type**: JSON, numbers, text, time series — auto-detected
- **MCP support**: Built-in server for Claude Desktop and AI agents
- **Azure migration**: Drop-in replacement for Azure Anomaly Detector (retiring Oct 2026)
