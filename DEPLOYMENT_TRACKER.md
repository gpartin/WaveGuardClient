# Deployment & Submission Tracker

**Last Updated**: 2026-03-16 (Session 128)  
**Maintainer**: Greg Partin (@gpartin)

---

## Product Overview

| Product | Version | Type | Repo (Public) | Repo (Private) | API Endpoint |
|---------|---------|------|---------------|----------------|-------------|
| **WaveGuard** | v3.3.0 | Core Engine | — | gpartin/WaveGuard | `gpartin--waveguard-api-fastapi-app.modal.run` |

**Live Endpoints (23 total, as of 2026-03-16):**

| # | Endpoint | Method | Category | GPU | Added |
|---|----------|--------|----------|-----|-------|
| 1 | `/v1/scan` | POST | Anomaly Detection | Yes | v1.0.0 |
| 2 | `/v1/fingerprint` | POST | Anomaly Detection | Yes | v2.5.0 |
| 3 | `/v1/compare` | POST | Anomaly Detection | Yes | v2.5.0 |
| 4 | `/v1/trajectory_scan` | POST | Intelligence | Yes | v3.3.0 |
| 5 | `/v1/phase_coherence` | POST | Intelligence | Yes | v3.3.0 |
| 6 | `/v1/instability` | POST | Intelligence | Yes | v3.3.0 |
| 7 | `/v1/interaction_matrix` | POST | Intelligence | Yes | v3.3.0 |
| 8 | `/v1/cascade_risk` | POST | Intelligence | Yes | v3.3.0 |
| 9 | `/v1/counterfactual` | POST | Intelligence | Yes | v3.3.0 |
| 10 | `/v1/mechanism_probe` | POST | Intelligence | Yes | v3.3.0 |
| 11 | `/v1/action_surface` | POST | Intelligence | Yes | v3.3.0 |
| 12 | `/v1/multi_horizon_outlook` | POST | Intelligence | Yes | v3.3.0 |
| 13 | `/v1/spectral_analyze` | POST | Intelligence (Lightweight) | No | v3.3.0+ |
| 14 | `/v1/wave_solve` | POST | Intelligence (Lightweight) | No | v3.3.0+ |
| 15 | `/v1/biorhythm` | POST | Intelligence (Lightweight) | No | v3.3.0+ |
| 16 | `/v1/market/{action}` | GET | Market Data | No | v3.0.0 |
| 17 | `/v1/health` | GET | System | No | v1.0.0 |
| 18 | `/v1/tier` | GET | System | No | v2.0.0 |
| 19 | `/v1/pricing` | GET | System | No | v3.0.0 |
| 20 | `/v1/agent/tools` | GET | Discovery | No | v3.3.0 |
| 21 | `/v1/agent/mcp` | GET | Discovery | No | v3.3.0 |
| 22 | `/v1/agent/langchain` | GET | Discovery | No | v3.3.0 |
| 23 | `/v1/analytics/mcp` | POST | Analytics | No | v3.3.0 |
| **WaveGuardClient** | v3.3.0 | Python SDK + MCP | gpartin/WaveGuardClient | — | (uses WaveGuard API) |
| **CryptoGuard** | v0.5.0 | Crypto Validator | — | gpartin/CryptoGuard | `gpartin--cryptoguard-api-fastapi-app.modal.run` |
| **CryptoGuardClient** | v0.3.0 | Python SDK + MCP | gpartin/CryptoGuardClient | — | (uses CryptoGuard API) |

---

## Deployment Matrix

### WaveGuard (Core Engine — Private)

| Channel | Status | Version | Date | Notes |
|---------|--------|---------|------|-------|
| Modal (API) | ✅ LIVE | v3.3.0 | 2026-03-16 | 23 endpoints live (3 new: biorhythm, spectral_analyze, wave_solve) |
| GitHub (Private) | ✅ CURRENT | v3.3.0 | 2026-03-01 | `gpartin/WaveGuard` |

### WaveGuardClient (Public SDK + MCP)

| Channel | Status | Version | Date | URL / ID | Notes |
|---------|--------|---------|------|----------|-------|
| GitHub | ✅ LIVE | v3.3.0 | 2026-03-01 | [gpartin/WaveGuardClient](https://github.com/gpartin/WaveGuardClient) | Public repo |
| PyPI | ✅ LIVE | v3.3.0 | 2026-03-01 | [WaveGuardClient](https://pypi.org/project/WaveGuardClient/) | `pip install WaveGuardClient` |
| awesome-mcp-servers | 🟡 OPEN | — | 2026-03-01 | [PR #2378](https://github.com/punkpeye/awesome-mcp-servers/pull/2378) | Glama-link requirement addressed; awaiting maintainer merge |
| x402 Ecosystem | 🟡 OPEN | — | 2026-03-01 | [PR #1341](https://github.com/coinbase/x402/pull/1341) | Maintainer review gate: 0/1 approval currently shown |
| Smithery | ✅ LIVE | v3.3.0 | 2026-03-01 | [emergentphysicslab/waveguard](https://smithery.ai/server/emergentphysicslab/waveguard) | 100/100 quality score |
| Glama | 🟡 SUBMITTED | — | 2026-02-26 | — | Pending review |

### CryptoGuard (Crypto Validator — Private)

| Channel | Status | Version | Date | Notes |
|---------|--------|---------|------|-------|
| Modal (API) | ✅ LIVE | v0.5.0 | 2026-03-01 | `gpartin--cryptoguard-api-fastapi-app.modal.run` (agent route normalization deployed) |
| RapidAPI | 🟡 BEHIND | ~v2.0.0 | 2026-03-01 | [waveguard](https://rapidapi.com/gpartin/api/waveguard) | OpenAPI spec ready (`openapi_rapidapi.json`), needs manual dashboard import. See `docs/RAPIDAPI_PUBLISH_CHECKLIST_v3.3.0.md` |
| GitHub (Private) | ✅ CURRENT | v0.5.0 | 2026-03-01 | `gpartin/CryptoGuard` |

### CryptoGuardClient (Public SDK + MCP)

| Channel | Status | Version | Date | URL / ID | Notes |
|---------|--------|---------|------|----------|-------|
| GitHub | ✅ LIVE | v0.3.0 | 2026-02-26 | [gpartin/CryptoGuardClient](https://github.com/gpartin/CryptoGuardClient) | Public, 22 files, commit `f03248f` |
| GitHub Release | ✅ CREATED | v0.3.0 | 2026-02-26 | [v0.3.0](https://github.com/gpartin/CryptoGuardClient/releases/tag/v0.3.0) | Triggers PyPI workflow |
| PyPI | ✅ LIVE | v0.3.0 | 2026-02-26 | [CryptoGuardClient](https://pypi.org/project/CryptoGuardClient/) | `pip install CryptoGuardClient` |
| awesome-mcp-servers | 🟡 OPEN | — | 2026-03-01 | [PR #2440](https://github.com/punkpeye/awesome-mcp-servers/pull/2440) | Awaiting maintainer merge (no explicit requested changes visible) |
| x402 Ecosystem | 🟡 OPEN | — | 2026-03-01 | [PR #1358](https://github.com/coinbase/x402/pull/1358) | Maintainer review gate: 0/1 approval currently shown |
| Smithery | ✅ LIVE | v0.3.0 | 2026-02-26 | [emergentphysicslab/cryptoguard](https://smithery.ai/server/emergentphysicslab/cryptoguard) | 100/100 quality score |
| Glama | 🟡 SUBMITTED | — | 2026-02-26 | — | Pending review |

---

## Pending Actions

### ✅ COMPLETED: PyPI (Both Products)

- **WaveGuardClient** v3.3.0 — LIVE on PyPI (2026-03-01)
- **CryptoGuardClient** v0.3.0 — LIVE on PyPI (2026-02-26)

### 🟢 Next PyPI bump playbook (when needed)

- Prepare release with: `./scripts/prepare_pypi_release.ps1 -Version <next_version>`
- Checklist: `docs/PYPI_RELEASE_CHECKLIST_v3.3.0.md`
- Current package version in `pyproject.toml`: `3.3.0`

### ✅ COMPLETED: Smithery (Both Products)

- **WaveGuard** — 100/100 quality score (emergentphysicslab/waveguard)
- **CryptoGuard** — 100/100 quality score (emergentphysicslab/cryptoguard)

### ✅ COMPLETED: Glama (Both Products)

- **WaveGuard** — Submitted 2026-02-26, pending review
- **CryptoGuard** — Submitted 2026-02-26, pending review

### 🟡 Pending: PR Merges (Distribution Parity Critical Path)

- awesome-mcp-servers:
    - [#2378](https://github.com/punkpeye/awesome-mcp-servers/pull/2378): requirement updates addressed (Glama link + wording), waiting maintainer merge.
    - [#2440](https://github.com/punkpeye/awesome-mcp-servers/pull/2440): open and waiting maintainer merge.
- x402 ecosystem:
    - [#1341](https://github.com/coinbase/x402/pull/1341): commit signing and metadata refinements done; currently blocked on maintainer approval gate (0/1).
    - [#1358](https://github.com/coinbase/x402/pull/1358): commit signing and metadata ordering updates done; currently blocked on maintainer approval gate (0/1).

### 🔵 Distribution Parity Next Actions (48h Cadence)

1. Post concise follow-up comments on all 4 open PRs with current live links + request for final maintainer merge/review.
2. For x402 PRs, explicitly re-request review from current assignee/maintainer after signed-commit updates.
3. Verify Glama listing status for both products and add direct listing URLs to trackers once approved.
4. Re-audit PR states daily until both awesome and x402 entries are merged for WaveGuard and CryptoGuard.

### 🟢 Optional: Community Posts (When Ready)

See individual `LAUNCH_SUBMISSIONS.md` in each repo for pre-written posts:
- `C:\Papers\WaveGuardClient\LAUNCH_SUBMISSIONS.md` — Show HN, r/MachineLearning, r/IoT, r/MCP
- `C:\Papers\CryptoGuardClient\LAUNCH_SUBMISSIONS.md` — Show HN, r/CryptoCurrency, r/MCP, r/algotrading

---

## PR Status Dashboard

| PR | Repo | Title | Status | Date | Notes |
|----|------|-------|--------|------|-------|
| [#1341](https://github.com/coinbase/x402/pull/1341) | coinbase/x402 | Add WaveGuard to ecosystem | ✅ OPEN | 2026-03-01 | Blocker: required maintainer approval (0/1 shown) |
| [#1358](https://github.com/coinbase/x402/pull/1358) | coinbase/x402 | Add CryptoGuard to ecosystem | ✅ OPEN | 2026-03-01 | Blocker: required maintainer approval (0/1 shown) |
| [#2378](https://github.com/punkpeye/awesome-mcp-servers/pull/2378) | punkpeye/awesome-mcp-servers | Add WaveGuard | ✅ OPEN | 2026-03-01 | Glama requirement satisfied; waiting maintainer merge |
| [#2440](https://github.com/punkpeye/awesome-mcp-servers/pull/2440) | punkpeye/awesome-mcp-servers | Add CryptoGuard | ✅ OPEN | 2026-03-01 | Waiting maintainer merge |

---

## GPG Signing

All commits in public repos are GPG-signed.

- **Key**: RSA4096 `E8875D4CF99C572F`
- **Identity**: Greg Partin <gpartin@gmail.com>
- **Config**: `git config --global commit.gpgsign true`
- **GitHub**: Key uploaded and verified

---

## Version History

### CryptoGuardClient

| Version | Date | Changes |
|---------|------|---------|
| v0.3.0 | 2026-02-26 | Initial release. Python SDK + MCP server, 5 tools, typed exceptions, x402 payments, free tier. |

### WaveGuardClient

| Version | Date | Changes |
|---------|------|---------|
| v3.3.0+ | 2026-03-16 | 3 new lightweight endpoints: biorhythm, spectral_analyze, wave_solve (server-side, no SDK update needed) |
| v3.2.0 | 2026-02-25 | Level 1 (Complex Ψ) support. 62-dim fingerprint, complex field encoding, phase-based charge. |
| v3.1.0 | 2026-02-24 | Multi-resolution scoring, time-series auto-windowing. |
| v3.0.0 | 2026-02-23 | MCP server integration, stdio + HTTP transports. |

---

## Architecture

```
┌──────────────────────┐     ┌──────────────────────┐
│  WaveGuardClient     │     │  CryptoGuardClient   │
│  (Public, PyPI)      │     │  (Public, PyPI)       │
│  - Python SDK        │     │  - Python SDK        │
│  - MCP Server        │     │  - MCP Server        │
│  - 3 tools           │     │  - 5 tools           │
└──────────┬───────────┘     └──────────┬───────────┘
           │ HTTPS                      │ HTTPS
           ▼                            ▼
┌──────────────────────┐     ┌──────────────────────┐
│  WaveGuard           │     │  CryptoGuard         │
│  (Private, Modal)    │◄────│  (Private, Modal)    │
│  - GPU engine        │     │  - Validator engine   │
│  - RTX 4060 / T4     │     │  - Uses WaveGuard    │
│  - v3.3.0            │     │  - v0.5.0            │
└──────────────────────┘     └──────────────────────┘
```

---

## Submission Process (Template for Future Products)

### Automated (Agent can do)
1. **GitHub repo**: Create public repo with SDK + MCP server
2. **GitHub release**: Create tagged release (triggers PyPI workflow)
3. **awesome-mcp-servers PR**: Fork, add entry, create PR
4. **x402 ecosystem PR**: Fork, add entry, create PR

### Manual (Human required)
1. **PyPI trusted publisher**: Configure at pypi.org (one-time per project)
2. **Smithery**: Submit at smithery.ai (web form)
3. **Glama**: Submit at glama.ai/mcp/servers (web form)
4. **Show HN**: Post at news.ycombinator.com
5. **Reddit**: Post in relevant subreddits

### Required Files for Submission
- `README.md` — comprehensive docs
- `smithery.yaml` — Smithery stdio config
- `server.json` — MCP Schema / Glama config
- `mcp.json` — MCP registry format
- `.github/workflows/publish.yml` — PyPI trusted publisher workflow
- `LAUNCH_SUBMISSIONS.md` — pre-written posts for all channels
- `CHANGELOG.md` — version history
