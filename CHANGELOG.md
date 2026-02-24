# Changelog

All notable changes to this project will be documented in this file.

## [2.0.0] — 2026-02-24

### Added
- Initial public release of the WaveGuard Python SDK
- `WaveGuard` client class with `scan()`, `health()`, and `tier()` methods
- Full exception hierarchy: `AuthenticationError`, `ValidationError`, `RateLimitError`, `ServerError`
- MCP server for Claude Desktop & AI agent integration (stdio + HTTP transports)
- 7 runnable examples covering all major use cases
- Documentation: getting started, API reference, MCP integration, Azure migration guide
- Test suite with mocked HTTP responses (runs offline)
- `pip install waveguard` with minimal dependencies (just `requests`)

### Key Features
- **One-call API**: Send training + test data → get anomaly scores back
- **Fully stateless**: Nothing persists between calls
- **Any data type**: JSON, numbers, text, time series — auto-detected
- **MCP support**: Built-in server for Claude Desktop and AI agents
- **Azure migration**: Drop-in replacement for Azure Anomaly Detector (retiring Oct 2026)
