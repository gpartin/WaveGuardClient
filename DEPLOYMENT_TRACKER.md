# Deployment & Submission Tracker

**Last Updated**: 2026-02-26
**Maintainer**: Greg Partin (@gpartin)

---

## Product Overview

| Product | Version | Type | Repo (Public) | Repo (Private) | API Endpoint |
|---------|---------|------|---------------|----------------|-------------|
| **WaveGuard** | v3.2.0 | Core Engine | — | gpartin/WaveGuard | `gpartin--waveguard-api-fastapi-app.modal.run` |
| **WaveGuardClient** | v3.2.0 | Python SDK + MCP | gpartin/WaveGuardClient | — | (uses WaveGuard API) |
| **CryptoGuard** | v0.3.0 | Crypto Validator | — | gpartin/CryptoGuard | `gpartin--cryptoguard-api-fastapi-app.modal.run` |
| **CryptoGuardClient** | v0.3.0 | Python SDK + MCP | gpartin/CryptoGuardClient | — | (uses CryptoGuard API) |

---

## Deployment Matrix

### WaveGuard (Core Engine — Private)

| Channel | Status | Version | Date | Notes |
|---------|--------|---------|------|-------|
| Modal (API) | ✅ LIVE | v3.2.0 | 2026-02-25 | `gpartin--waveguard-api-fastapi-app.modal.run` |
| GitHub (Private) | ✅ CURRENT | v3.2.0 | 2026-02-25 | `gpartin/WaveGuard` |

### WaveGuardClient (Public SDK + MCP)

| Channel | Status | Version | Date | URL / ID | Notes |
|---------|--------|---------|------|----------|-------|
| GitHub | ✅ LIVE | v3.2.0 | 2026-02-25 | [gpartin/WaveGuardClient](https://github.com/gpartin/WaveGuardClient) | Public repo |
| PyPI | ✅ LIVE | v3.2.0 | 2026-02-25 | [WaveGuardClient](https://pypi.org/project/WaveGuardClient/) | `pip install WaveGuardClient` |
| awesome-mcp-servers | ✅ MERGED | — | 2026-02-26 | [PR #2378](https://github.com/punkpeye/awesome-mcp-servers/pull/2378) | Analytics category |
| x402 Ecosystem | ✅ SUBMITTED | — | 2026-02-26 | [PR #1341](https://github.com/anthropics/x402/pull/1341) | Signed commit `6a39fa9` |
| Smithery | ✅ LIVE | v3.2.0 | 2026-02-26 | [emergentphysicslab/waveguard](https://smithery.ai/server/emergentphysicslab/waveguard) | 100/100 quality score |
| Glama | ✅ SUBMITTED | — | 2026-02-26 | — | Pending review |

### CryptoGuard (Crypto Validator — Private)

| Channel | Status | Version | Date | Notes |
|---------|--------|---------|------|-------|
| Modal (API) | ✅ LIVE | v0.3.0 | 2026-02-25 | `gpartin--cryptoguard-api-fastapi-app.modal.run` |
| RapidAPI | ✅ LIVE | v0.3.0 | 2026-02-26 | `cryptoguard.p.rapidapi.com` — Free/Pro/Ultra tiers |
| GitHub (Private) | ✅ CURRENT | v0.3.0 | 2026-02-25 | `gpartin/CryptoGuard` |

### CryptoGuardClient (Public SDK + MCP)

| Channel | Status | Version | Date | URL / ID | Notes |
|---------|--------|---------|------|----------|-------|
| GitHub | ✅ LIVE | v0.3.0 | 2026-02-26 | [gpartin/CryptoGuardClient](https://github.com/gpartin/CryptoGuardClient) | Public, 22 files, commit `f03248f` |
| GitHub Release | ✅ CREATED | v0.3.0 | 2026-02-26 | [v0.3.0](https://github.com/gpartin/CryptoGuardClient/releases/tag/v0.3.0) | Triggers PyPI workflow |
| PyPI | ✅ LIVE | v0.3.0 | 2026-02-26 | [CryptoGuardClient](https://pypi.org/project/CryptoGuardClient/) | `pip install CryptoGuardClient` |
| awesome-mcp-servers | ✅ SUBMITTED | — | 2026-02-26 | [PR #2440](https://github.com/punkpeye/awesome-mcp-servers/pull/2440) | Finance & Fintech category |
| x402 Ecosystem | ✅ SUBMITTED | — | 2026-02-26 | [PR #1358](https://github.com/anthropics/x402/pull/1358) | Signed commit `b58bd0b`, replied to @Must-be-Ash |
| Smithery | ✅ LIVE | v0.3.0 | 2026-02-26 | [emergentphysicslab/cryptoguard](https://smithery.ai/server/emergentphysicslab/cryptoguard) | 100/100 quality score |
| Glama | ✅ SUBMITTED | — | 2026-02-26 | — | Pending review |

---

## Pending Actions

### ✅ COMPLETED: PyPI (Both Products)

- **WaveGuardClient** v3.2.0 — LIVE on PyPI (2026-02-25)
- **CryptoGuardClient** v0.3.0 — LIVE on PyPI (2026-02-26)

### ✅ COMPLETED: Smithery (Both Products)

- **WaveGuard** — 100/100 quality score (emergentphysicslab/waveguard)
- **CryptoGuard** — 100/100 quality score (emergentphysicslab/cryptoguard)

### ✅ COMPLETED: Glama (Both Products)

- **WaveGuard** — Submitted 2026-02-26, pending review
- **CryptoGuard** — Submitted 2026-02-26, pending review

### 🟡 Pending: PR Merges (Waiting on Maintainers)

- awesome-mcp-servers: PRs #2378 (WaveGuard) and #2440 (CryptoGuard) awaiting merge
- x402 ecosystem: PRs #1341 (WaveGuard) and #1358 (CryptoGuard) awaiting merge

### 🟢 Optional: Community Posts (When Ready)

See individual `LAUNCH_SUBMISSIONS.md` in each repo for pre-written posts:
- `C:\Papers\WaveGuardClient\LAUNCH_SUBMISSIONS.md` — Show HN, r/MachineLearning, r/IoT, r/MCP
- `C:\Papers\CryptoGuardClient\LAUNCH_SUBMISSIONS.md` — Show HN, r/CryptoCurrency, r/MCP, r/algotrading

---

## PR Status Dashboard

| PR | Repo | Title | Status | Date | Notes |
|----|------|-------|--------|------|-------|
| [#1341](https://github.com/anthropics/x402/pull/1341) | anthropics/x402 | Add WaveGuard to ecosystem | ✅ OPEN | 2026-02-26 | Signed commit `6a39fa9` |
| [#1358](https://github.com/anthropics/x402/pull/1358) | anthropics/x402 | Add CryptoGuard to ecosystem | ✅ OPEN | 2026-02-26 | Signed commit `b58bd0b`, replied to reviewer |
| [#2378](https://github.com/punkpeye/awesome-mcp-servers/pull/2378) | punkpeye/awesome-mcp-servers | Add WaveGuard | ✅ OPEN | 2026-02-26 | Analytics category |
| [#2440](https://github.com/punkpeye/awesome-mcp-servers/pull/2440) | punkpeye/awesome-mcp-servers | Add CryptoGuard | ✅ OPEN | 2026-02-26 | Finance & Fintech category |

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
│  - v3.2.0            │     │  - v0.3.0            │
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
