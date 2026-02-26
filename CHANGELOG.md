# Changelog

All notable changes to this project will be documented in this file.

## [3.1.0] — 2026-02-26

### Added
- **Live crypto market data**: New server endpoint `/v1/market/{action}` with
  7 actions (token_data, price_history, ohlc, top_coins, search, dex_token,
  dex_search) powered by CoinGecko and DexScreener
- **10th MCP tool**: `waveguard_market_data` for AI agents to fetch live crypto prices
- **Solana multi-chain support**: x402 payments now support 7 networks including
  Solana mainnet (Base, Ethereum, Polygon, Arbitrum, Optimism, Solana)
- **A2A protocol**: Google Agent-to-Agent discovery at `/.well-known/agent.json`
  (protocol v0.3.0, 4 skills)
- **Bazaar discovery**: x402 extensions now include JSON Schema `inputSchema`/`outputSchema`
  for decentralized API marketplace discovery

### Changed
- Version bumped to 3.1.0 across all files and registries

## [3.0.0] — 2026-02-25

### Added
- **Fingerprint endpoint** (`POST /v1/fingerprint`): Raw 52-dim physics embeddings
- **Compare endpoint** (`POST /v1/compare`): Structural similarity between datasets
- **5 crypto risk tools**: `token_risk`, `wallet_profile`, `volume_check`,
  `price_manipulation`, `market_data` — all available via MCP
- **x402 crypto payments**: Pay-per-call with USDC ($0.01/call) on Base mainnet
- **6 MCP prompts**: Guided workflows for anomaly analysis, monitoring, crypto due diligence

### Changed
- MCP tools expanded from 3 to 9 (now 10 in 3.1.0)
- Server architecture split: CPU web function + GPU compute function on Modal

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
