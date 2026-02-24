"""
WaveGuard — Physics-based anomaly detection SDK.

Quick start::

    from waveguard import WaveGuard

    wg = WaveGuard(api_key="YOUR_KEY")
    result = wg.scan(training=normal_data, test=new_data)

    for r in result.results:
        print(r.is_anomaly, r.score, r.confidence)
"""

from .client import (  # noqa: F401
    WaveGuard,
    ScanResult,
    SampleResult,
    ScanSummary,
    FeatureInfo,
    EngineInfo,
    HealthStatus,
    TierInfo,
    __version__,
)
from .exceptions import (  # noqa: F401
    WaveGuardError,
    AuthenticationError,
    ValidationError,
    RateLimitError,
    ServerError,
)

__all__ = [
    # Client
    "WaveGuard",
    # Results
    "ScanResult",
    "SampleResult",
    "ScanSummary",
    "FeatureInfo",
    "EngineInfo",
    "HealthStatus",
    "TierInfo",
    # Exceptions
    "WaveGuardError",
    "AuthenticationError",
    "ValidationError",
    "RateLimitError",
    "ServerError",
    # Meta
    "__version__",
]
