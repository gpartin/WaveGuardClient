"""
WaveGuard exception hierarchy.

All exceptions inherit from WaveGuardError so you can catch them with a
single ``except WaveGuardError`` block, or handle specific cases granularly.
"""

__all__ = [
    "WaveGuardError",
    "AuthenticationError",
    "ValidationError",
    "RateLimitError",
    "ServerError",
]


class WaveGuardError(Exception):
    """Base exception for all WaveGuard SDK errors.

    Attributes
    ----------
    message : str
        Human-readable error description.
    status_code : int
        HTTP status code (0 if not from an HTTP response).
    detail : str
        Raw error body from the API, if available.
    """

    def __init__(self, message: str, status_code: int = 0, detail: str = ""):
        self.message = message
        self.status_code = status_code
        self.detail = detail
        super().__init__(message)


class AuthenticationError(WaveGuardError):
    """API key is invalid, expired, or missing (HTTP 401)."""
    pass


class ValidationError(WaveGuardError):
    """Request data failed server-side validation (HTTP 422).

    Check ``detail`` for specifics (e.g. empty training array, type mismatch).
    """
    pass


class RateLimitError(WaveGuardError):
    """Rate limit or subscription tier limit exceeded (HTTP 429).

    Back off and retry, or upgrade your tier at
    https://rapidapi.com/gpartin/api/waveguard
    """

    UPGRADE_URL = "https://rapidapi.com/gpartin/api/waveguard"


class ServerError(WaveGuardError):
    """Internal server error (HTTP 5xx).

    Usually transient — retry after a short delay.
    """
    pass
