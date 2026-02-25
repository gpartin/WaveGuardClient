"""
WaveGuard Python SDK — stateless anomaly detection via wave physics.

Usage::

    from waveguard import WaveGuard

    wg = WaveGuard(api_key="YOUR_KEY")

    result = wg.scan(
        training=[
            {"cpu": 45, "memory": 62, "errors": 0},
            {"cpu": 48, "memory": 63, "errors": 0},
            {"cpu": 42, "memory": 61, "errors": 1},
            {"cpu": 50, "memory": 64, "errors": 0},
        ],
        test=[
            {"cpu": 46, "memory": 62, "errors": 0},    # normal
            {"cpu": 99, "memory": 95, "errors": 150},   # anomaly
        ],
    )

    for r in result.results:
        print(r.is_anomaly, r.score, r.confidence)
"""

from __future__ import annotations

import requests
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .exceptions import (
    WaveGuardError,
    AuthenticationError,
    ValidationError,
    RateLimitError,
    ServerError,
)

__version__ = "2.0.0"


# ─────────────────────────────── Data Classes ─────────────────────────────


@dataclass
class FeatureInfo:
    """A single top-contributing feature in anomaly scoring."""

    dimension: int
    label: str
    z_score: float


@dataclass
class EngineInfo:
    """Physics engine configuration for this scan."""

    grid_size: int
    evolution_steps: int
    fingerprint_dims: int


@dataclass
class SampleResult:
    """Result of anomaly detection on a single test sample."""

    score: float
    is_anomaly: bool
    threshold: float
    mahalanobis_distance: float
    confidence: float
    top_features: List[FeatureInfo]
    latency_ms: float
    engine: EngineInfo
    raw: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ScanSummary:
    """Aggregate statistics from a scan."""

    total_test_samples: int
    total_training_samples: int
    anomalies_found: int
    anomaly_rate: float
    mean_score: float
    max_score: float
    total_latency_ms: float
    encoder_type: str


@dataclass
class ScanResult:
    """Complete result of a ``/v1/scan`` call.

    Attributes
    ----------
    results : list[SampleResult]
        One entry per test sample, in order.
    summary : ScanSummary
        Aggregate statistics across all test samples.
    raw : dict
        The full JSON response from the API.
    """

    results: List[SampleResult]
    summary: ScanSummary
    raw: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HealthStatus:
    """API health information."""

    status: str
    version: str
    gpu: str
    mode: str
    uptime_seconds: float
    raw: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TierInfo:
    """Current subscription tier and rate limits."""

    tier: str
    limits: Dict[str, int]
    raw: Dict[str, Any] = field(default_factory=dict)


# ─────────────────────────────── Client ───────────────────────────────────


class WaveGuard:
    """WaveGuard Anomaly Detection client.

    Parameters
    ----------
    api_key : str
        Your WaveGuard API key.
    base_url : str, optional
        API base URL.  Defaults to the production Modal endpoint.
    timeout : float, optional
        Request timeout in seconds.  Default ``120`` (generous for GPU
        cold starts).

    Examples
    --------
    >>> wg = WaveGuard(api_key="wg_test_key")
    >>> result = wg.scan(
    ...     training=[{"a": 1}, {"a": 2}, {"a": 3}],
    ...     test=[{"a": 100}],
    ... )
    >>> result.results[0].is_anomaly
    True
    """

    DEFAULT_URL = "https://gpartin--waveguard-api-fastapi-app.modal.run"

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = DEFAULT_URL,
        timeout: float = 120.0,
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._session = requests.Session()
        headers = {
            "Content-Type": "application/json",
            "User-Agent": f"waveguard-python/{__version__}",
        }
        if api_key:
            headers["X-API-Key"] = api_key
        self._session.headers.update(headers)

    # ── Core API ──────────────────────────────────────────────────────

    def scan(
        self,
        training: List[Any],
        test: List[Any],
        encoder_type: Optional[str] = None,
        sensitivity: Optional[float] = None,
    ) -> ScanResult:
        """Scan test data for anomalies against a training baseline.

        This is the only method you need.  Send training + test data in a
        single call, get anomaly scores back, and everything is torn down.
        Fully stateless — nothing persists between calls.

        Parameters
        ----------
        training : list
            2+ examples of **normal** data.  All entries must be the same
            type and shape.
        test : list
            1+ samples to check for anomalies.
        encoder_type : str, optional
            Force a specific encoder: ``"json"``, ``"numeric"``,
            ``"text"``, ``"timeseries"``, ``"tabular"``.
            Leave *None* for auto-detection (recommended).
        sensitivity : float, optional
            Detection sensitivity in the range 0.5–3.0.
            Lower values are more sensitive (flag more anomalies).

        Returns
        -------
        ScanResult
            ``.results`` has one :class:`SampleResult` per test sample.
            ``.summary`` has aggregate stats.
        """
        body: Dict[str, Any] = {
            "training": training,
            "test": test,
        }
        if encoder_type is not None:
            body["encoder_type"] = encoder_type
        if sensitivity is not None:
            body["sensitivity"] = sensitivity

        resp = self._post("/v1/scan", body)
        return self._parse_scan(resp, len(training), len(test))

    # ── Utility ───────────────────────────────────────────────────────

    def health(self) -> HealthStatus:
        """Check API health and GPU status.  No auth required."""
        resp = self._get("/v1/health")
        return HealthStatus(
            status=resp.get("status", "unknown"),
            version=resp.get("version", ""),
            gpu=resp.get("gpu", ""),
            mode=resp.get("mode", ""),
            uptime_seconds=resp.get("uptime_seconds", 0.0),
            raw=resp,
        )

    def tier(self) -> TierInfo:
        """Get current subscription tier and rate limits."""
        resp = self._get("/v1/tier")
        return TierInfo(
            tier=resp.get("tier", ""),
            limits=resp.get("limits", {}),
            raw=resp,
        )

    # ── Response parsing ──────────────────────────────────────────────

    def _parse_scan(
        self, resp: dict, n_train: int, n_test: int
    ) -> ScanResult:
        results = []
        for r in resp.get("results", []):
            features = [
                FeatureInfo(
                    dimension=f.get("dimension", 0),
                    label=f.get("label", ""),
                    z_score=f.get("z_score", 0.0),
                )
                for f in r.get("top_features", [])
            ]
            eng = r.get("engine", {})
            results.append(
                SampleResult(
                    score=r.get("score", 0.0),
                    is_anomaly=r.get("is_anomaly", False),
                    threshold=r.get("threshold", 0.0),
                    mahalanobis_distance=r.get("mahalanobis_distance", 0.0),
                    confidence=r.get("confidence", 0.0),
                    top_features=features,
                    latency_ms=r.get("latency_ms", 0.0),
                    engine=EngineInfo(
                        grid_size=eng.get("grid_size", 32),
                        evolution_steps=eng.get("evolution_steps", 150),
                        fingerprint_dims=eng.get("fingerprint_dims", 52),
                    ),
                    raw=r,
                )
            )

        s = resp.get("summary", {})
        summary = ScanSummary(
            total_test_samples=s.get("total_test_samples", n_test),
            total_training_samples=s.get("total_training_samples", n_train),
            anomalies_found=s.get("anomalies_found", 0),
            anomaly_rate=s.get("anomaly_rate", 0.0),
            mean_score=s.get("mean_score", 0.0),
            max_score=s.get("max_score", 0.0),
            total_latency_ms=s.get("total_latency_ms", 0.0),
            encoder_type=s.get("encoder_type", "auto"),
        )

        return ScanResult(results=results, summary=summary, raw=resp)

    # ── Internal HTTP ─────────────────────────────────────────────────

    def _post(self, path: str, body: dict) -> dict:
        url = f"{self.base_url}{path}"
        try:
            r = self._session.post(url, json=body, timeout=self.timeout)
        except requests.ConnectionError:
            raise WaveGuardError(f"Cannot connect to {self.base_url}")
        except requests.Timeout:
            raise WaveGuardError(
                f"Request timed out after {self.timeout}s"
            )
        return self._handle(r)

    def _get(self, path: str) -> dict:
        url = f"{self.base_url}{path}"
        try:
            r = self._session.get(url, timeout=self.timeout)
        except requests.ConnectionError:
            raise WaveGuardError(f"Cannot connect to {self.base_url}")
        except requests.Timeout:
            raise WaveGuardError(
                f"Request timed out after {self.timeout}s"
            )
        return self._handle(r)

    def _handle(self, r: requests.Response) -> dict:
        if r.status_code == 401:
            raise AuthenticationError(
                "Invalid or missing API key",
                status_code=401,
                detail=r.text,
            )
        if r.status_code == 422:
            raise ValidationError(
                f"Validation failed: {r.text}",
                status_code=422,
                detail=r.text,
            )
        if r.status_code == 429:
            raise RateLimitError(
                f"Rate or tier limit exceeded. "
                f"Upgrade at {RateLimitError.UPGRADE_URL}\n"
                f"Detail: {r.text}",
                status_code=429,
                detail=r.text,
            )
        if r.status_code >= 500:
            raise ServerError(
                f"Server error {r.status_code}: {r.text}",
                status_code=r.status_code,
                detail=r.text,
            )
        if r.status_code >= 400:
            raise WaveGuardError(
                f"API error {r.status_code}: {r.text}",
                status_code=r.status_code,
                detail=r.text,
            )
        try:
            return r.json()
        except ValueError:
            return {"raw": r.text}

    def __repr__(self) -> str:
        return f"WaveGuard(base_url='{self.base_url}')"
