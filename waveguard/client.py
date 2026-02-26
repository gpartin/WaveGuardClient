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

import logging
import os
import time
import random
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

__version__ = "3.2.0"

logger = logging.getLogger("waveguard")


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
    p_value: float
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


@dataclass
class FingerprintResult:
    """Result of a ``/v1/fingerprint`` call.

    Attributes
    ----------
    fingerprint : list[float]
        Physics embedding vector (52-dim at L0, 62-dim at L1).
    dimensions : int
        Number of dimensions (52 at Level 0, 62 at Level 1).
    labels : list[str]
        Human-readable label for each dimension.
    encoder_type : str
        Encoder used to map input data onto the lattice.
    latency_ms : float
        Server-side processing time.
    field_level : int
        Field level used (0=real scalar, 1=complex).
    raw : dict
        Full JSON response.
    """

    fingerprint: List[float]
    dimensions: int
    labels: List[str]
    encoder_type: str
    latency_ms: float
    field_level: int = 0
    raw: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CompareResult:
    """Result of a ``/v1/compare`` call.

    Attributes
    ----------
    similarity : float
        Cosine similarity (0–1).  >0.95 = very similar.
    distance : float
        Euclidean distance between fingerprints.
    fingerprint_a : list[float]
        Physics embedding of data_a.
    fingerprint_b: List[float]
        Physics embedding of data_b.
    dimensions : int
        Number of dimensions.
    encoder_type : str
        Encoder used.
    latency_ms : float
        Server-side processing time.
    raw : dict
        Full JSON response.
    """

    similarity: float
    distance: float
    fingerprint_a: List[float]
    fingerprint_b: List[float]
    dimensions: int
    encoder_type: str
    latency_ms: float
    raw: Dict[str, Any] = field(default_factory=dict)


# ─────────────────────────────── Client ───────────────────────────────────


class WaveGuard:
    """WaveGuard Anomaly Detection client.

    Parameters
    ----------
    api_key : str, optional
        Your WaveGuard API key.  If not provided, reads from the
        ``WAVEGUARD_API_KEY`` environment variable.  Free-tier scans
        work without a key (rate-limited).
    base_url : str, optional
        API base URL.  Defaults to the production Modal endpoint.
    timeout : float, optional
        Request timeout in seconds.  Default ``120`` (generous for GPU
        cold starts).
    max_retries : int, optional
        Number of automatic retries on transient errors (429, 500, 502,
        503, 504, connection errors, timeouts).  Default ``2``.
        Set to ``0`` to disable retries.

    Examples
    --------
    >>> wg = WaveGuard()  # reads WAVEGUARD_API_KEY from env
    >>> result = wg.scan(
    ...     training=[{"a": 1}, {"a": 2}, {"a": 3}],
    ...     test=[{"a": 100}],
    ... )
    >>> result.results[0].is_anomaly
    True
    """

    DEFAULT_URL = "https://gpartin--waveguard-api-fastapi-app.modal.run"

    # Status codes that trigger automatic retry
    _RETRYABLE_STATUS = {429, 500, 502, 503, 504}

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = DEFAULT_URL,
        timeout: float = 120.0,
        max_retries: int = 2,
    ):
        self.api_key = api_key or os.environ.get("WAVEGUARD_API_KEY")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self._session = requests.Session()
        headers = {
            "Content-Type": "application/json",
            "User-Agent": f"waveguard-python/{__version__}",
        }
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        self._session.headers.update(headers)

    # ── Core API ──────────────────────────────────────────────────────

    def scan(
        self,
        training: List[Any],
        test: List[Any],
        encoder_type: Optional[str] = None,
        sensitivity: Optional[float] = None,
        field_level: int = 0,
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
            ``"text"``, ``"timeseries"``, ``"tabular"``,
            ``"complex_numeric"``.
            Leave *None* for auto-detection (recommended).
        sensitivity : float, optional
            Detection sensitivity in the range 0.5–3.0.
            Lower values are more sensitive (flag more anomalies).
        field_level : int
            Physics field complexity. 0 = real scalar (default).
            1 = complex field (phase-aware, 62-dim fingerprints).

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
        if field_level:
            body["field_level"] = field_level

        resp = self._post("/v1/scan", body)
        return self._parse_scan(resp, len(training), len(test))

    def fingerprint(
        self,
        data: Any,
        encoder_type: Optional[str] = None,
        field_level: int = 0,
    ) -> FingerprintResult:
        """Get a physics embedding of any data item.

        Parameters
        ----------
        data : any
            A single data item to fingerprint (JSON object, list, string, etc.).
        encoder_type : str, optional
            Force a specific encoder.  Leave *None* for auto-detection.
        field_level : int
            0 = real scalar (52-dim, default).
            1 = complex field (62-dim, includes phase statistics).

        Returns
        -------
        FingerprintResult
            ``.fingerprint`` is the embedding vector (52 or 62 dims).
            ``.labels`` names each dimension.
        """
        body: Dict[str, Any] = {"data": data}
        if encoder_type is not None:
            body["encoder_type"] = encoder_type
        if field_level:
            body["field_level"] = field_level

        resp = self._post("/v1/fingerprint", body)
        return FingerprintResult(
            fingerprint=resp.get("fingerprint", []),
            dimensions=resp.get("dimensions", 0),
            labels=resp.get("labels", []),
            encoder_type=resp.get("encoder_type", "auto"),
            latency_ms=resp.get("latency_ms", 0.0),
            field_level=resp.get("field_level", 0),
            raw=resp,
        )

    def compare(
        self,
        data_a: Any,
        data_b: Any,
        encoder_type: Optional[str] = None,
    ) -> CompareResult:
        """Compare two data items for structural similarity.

        Parameters
        ----------
        data_a : any
            First data item.
        data_b : any
            Second data item (same type as data_a).
        encoder_type : str, optional
            Force a specific encoder.  Leave *None* for auto-detection.

        Returns
        -------
        CompareResult
            ``.similarity`` is cosine similarity (0–1).
            ``.distance`` is Euclidean distance.
        """
        body: Dict[str, Any] = {"data_a": data_a, "data_b": data_b}
        if encoder_type is not None:
            body["encoder_type"] = encoder_type

        resp = self._post("/v1/compare", body)
        return CompareResult(
            similarity=resp.get("similarity", 0.0),
            distance=resp.get("distance", 0.0),
            fingerprint_a=resp.get("fingerprint_a", []),
            fingerprint_b=resp.get("fingerprint_b", []),
            dimensions=resp.get("dimensions", 0),
            encoder_type=resp.get("encoder_type", "auto"),
            latency_ms=resp.get("latency_ms", 0.0),
            raw=resp,
        )

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
                    p_value=r.get("p_value", 1.0),
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
        return self._request("POST", path, json=body)

    def _get(self, path: str) -> dict:
        return self._request("GET", path)

    def _request(
        self,
        method: str,
        path: str,
        json: Optional[dict] = None,
    ) -> dict:
        """Execute an HTTP request with automatic retry and backoff."""
        url = f"{self.base_url}{path}"
        last_exc: Optional[Exception] = None

        for attempt in range(1 + self.max_retries):
            try:
                logger.debug(
                    "%s %s (attempt %d/%d)",
                    method, path, attempt + 1, 1 + self.max_retries,
                )
                r = self._session.request(
                    method, url, json=json, timeout=self.timeout
                )

                # Non-retryable errors — raise immediately
                if r.status_code in (401, 403):
                    raise AuthenticationError(
                        "Invalid or missing API key. "
                        "Set WAVEGUARD_API_KEY or pass api_key= to WaveGuard().",
                        status_code=r.status_code,
                        detail=r.text,
                    )
                if r.status_code == 422:
                    raise ValidationError(
                        f"Validation failed: {r.text}",
                        status_code=422,
                        detail=r.text,
                    )

                # Retryable errors
                if r.status_code in self._RETRYABLE_STATUS:
                    retry_after = r.headers.get("Retry-After")
                    if r.status_code == 429 and attempt == self.max_retries:
                        raise RateLimitError(
                            f"Rate or tier limit exceeded. "
                            f"Upgrade at {RateLimitError.UPGRADE_URL}\n"
                            f"Detail: {r.text}",
                            status_code=429,
                            detail=r.text,
                        )
                    if attempt < self.max_retries:
                        delay = self._backoff_delay(attempt, retry_after)
                        logger.info(
                            "Retryable %d from %s — retrying in %.1fs",
                            r.status_code, path, delay,
                        )
                        time.sleep(delay)
                        continue
                    # Final attempt — raise appropriate error
                    if r.status_code >= 500:
                        raise ServerError(
                            f"Server error {r.status_code} after "
                            f"{self.max_retries} retries",
                            status_code=r.status_code,
                            detail=r.text,
                        )

                # Other 4xx errors
                if r.status_code >= 400:
                    raise WaveGuardError(
                        f"API error {r.status_code}: {r.text}",
                        status_code=r.status_code,
                        detail=r.text,
                    )

                # Success
                try:
                    return r.json()
                except ValueError:
                    raise WaveGuardError(
                        f"Unexpected non-JSON response from {path}",
                        status_code=r.status_code,
                        detail=r.text,
                    )

            except (requests.ConnectionError, requests.Timeout) as e:
                last_exc = e
                if attempt < self.max_retries:
                    delay = self._backoff_delay(attempt)
                    logger.info(
                        "%s on %s — retrying in %.1fs",
                        type(e).__name__, path, delay,
                    )
                    time.sleep(delay)
                    continue
                if isinstance(e, requests.Timeout):
                    raise WaveGuardError(
                        f"Request timed out after {self.timeout}s "
                        f"({self.max_retries} retries exhausted)"
                    ) from e
                raise WaveGuardError(
                    f"Cannot connect to {self.base_url} "
                    f"({self.max_retries} retries exhausted)"
                ) from e

        # Should not reach here, but just in case
        raise WaveGuardError("Request failed") from last_exc

    @staticmethod
    def _backoff_delay(
        attempt: int, retry_after: Optional[str] = None
    ) -> float:
        """Exponential backoff with jitter, respecting Retry-After."""
        if retry_after:
            try:
                return min(float(retry_after), 60.0)
            except ValueError:
                pass
        base = min(2 ** attempt, 30)  # 1, 2, 4, 8, ... capped at 30s
        return base + random.uniform(0, base * 0.5)

    def __repr__(self) -> str:
        return f"WaveGuard(base_url='{self.base_url}')"
