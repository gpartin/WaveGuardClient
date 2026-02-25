"""
Tests for the WaveGuard Python SDK client.

These tests use mocked HTTP responses so they run offline and fast.
"""

import json
import pytest
from unittest.mock import patch, MagicMock

from waveguard import (
    WaveGuard,
    ScanResult,
    SampleResult,
    HealthStatus,
    TierInfo,
    WaveGuardError,
    AuthenticationError,
    ValidationError,
    RateLimitError,
    ServerError,
)


# ── Fixtures ──────────────────────────────────────────────────────────────


@pytest.fixture
def wg():
    return WaveGuard(api_key="test-key-123")


def _mock_response(status_code=200, json_data=None, text=""):
    resp = MagicMock()
    resp.status_code = status_code
    resp.text = text or json.dumps(json_data or {})
    resp.json.return_value = json_data or {}
    resp.headers = {}
    return resp


SCAN_RESPONSE = {
    "results": [
        {
            "score": 0.5,
            "is_anomaly": False,
            "threshold": 2.0,
            "mahalanobis_distance": 0.5,
            "confidence": 0.1,
            "top_features": [],
            "latency_ms": 5.0,
            "engine": {
                "grid_size": 32,
                "evolution_steps": 150,
                "fingerprint_dims": 52,
            },
        },
        {
            "score": 8.3,
            "is_anomaly": True,
            "threshold": 2.0,
            "mahalanobis_distance": 8.3,
            "confidence": 0.95,
            "top_features": [
                {"dimension": 5, "label": "kurt_E", "z_score": 4.2},
                {"dimension": 12, "label": "skew_chi", "z_score": 3.1},
            ],
            "latency_ms": 5.2,
            "engine": {
                "grid_size": 32,
                "evolution_steps": 150,
                "fingerprint_dims": 52,
            },
        },
    ],
    "summary": {
        "total_test_samples": 2,
        "total_training_samples": 3,
        "anomalies_found": 1,
        "anomaly_rate": 0.5,
        "mean_score": 4.4,
        "max_score": 8.3,
        "total_latency_ms": 120.0,
        "encoder_type": "json",
    },
}


# ── Scan tests ────────────────────────────────────────────────────────────


class TestScan:
    @patch("waveguard.client.requests.Session")
    def test_scan_parses_results(self, mock_session_cls):
        session = MagicMock()
        session.request.return_value = _mock_response(200, SCAN_RESPONSE)
        mock_session_cls.return_value = session

        wg = WaveGuard(api_key="test", max_retries=0)
        result = wg.scan(
            training=[{"a": 1}, {"a": 2}, {"a": 3}],
            test=[{"a": 2}, {"a": 100}],
        )

        assert isinstance(result, ScanResult)
        assert len(result.results) == 2
        assert result.results[0].is_anomaly is False
        assert result.results[1].is_anomaly is True
        assert result.results[1].score == 8.3
        assert result.results[1].confidence == 0.95
        assert result.summary.anomalies_found == 1
        assert result.summary.encoder_type == "json"

    @patch("waveguard.client.requests.Session")
    def test_scan_top_features(self, mock_session_cls):
        session = MagicMock()
        session.request.return_value = _mock_response(200, SCAN_RESPONSE)
        mock_session_cls.return_value = session

        wg = WaveGuard(api_key="test", max_retries=0)
        result = wg.scan(training=[{"a": 1}, {"a": 2}], test=[{"a": 100}])

        anomaly = result.results[1]
        assert len(anomaly.top_features) == 2
        assert anomaly.top_features[0].label == "kurt_E"
        assert anomaly.top_features[0].z_score == 4.2

    @patch("waveguard.client.requests.Session")
    def test_scan_sends_optional_params(self, mock_session_cls):
        session = MagicMock()
        session.request.return_value = _mock_response(200, SCAN_RESPONSE)
        mock_session_cls.return_value = session

        wg = WaveGuard(api_key="test", max_retries=0)
        wg.scan(
            training=[{"a": 1}, {"a": 2}],
            test=[{"a": 3}],
            encoder_type="text",
            sensitivity=0.5,
        )

        call_args = session.request.call_args
        body = call_args.kwargs.get("json") or call_args[1].get("json")
        assert body["encoder_type"] == "text"
        assert body["sensitivity"] == 0.5


# ── Error handling tests ──────────────────────────────────────────────────


class TestErrors:
    @patch("waveguard.client.requests.Session")
    def test_401_raises_auth_error(self, mock_session_cls):
        session = MagicMock()
        session.request.return_value = _mock_response(401, text="Unauthorized")
        mock_session_cls.return_value = session

        wg = WaveGuard(api_key="bad-key", max_retries=0)
        with pytest.raises(AuthenticationError):
            wg.scan(training=[{"a": 1}, {"a": 2}], test=[{"a": 3}])

    @patch("waveguard.client.requests.Session")
    def test_422_raises_validation_error(self, mock_session_cls):
        session = MagicMock()
        session.request.return_value = _mock_response(422, text="Empty training")
        mock_session_cls.return_value = session

        wg = WaveGuard(api_key="test", max_retries=0)
        with pytest.raises(ValidationError):
            wg.scan(training=[], test=[{"a": 1}])

    @patch("waveguard.client.requests.Session")
    def test_429_raises_rate_limit_error(self, mock_session_cls):
        session = MagicMock()
        session.request.return_value = _mock_response(429, text="Rate limited")
        mock_session_cls.return_value = session

        wg = WaveGuard(api_key="test", max_retries=0)
        with pytest.raises(RateLimitError):
            wg.scan(training=[{"a": 1}, {"a": 2}], test=[{"a": 3}])

    @patch("waveguard.client.requests.Session")
    def test_500_raises_server_error(self, mock_session_cls):
        session = MagicMock()
        session.request.return_value = _mock_response(500, text="Internal error")
        mock_session_cls.return_value = session

        wg = WaveGuard(api_key="test", max_retries=0)
        with pytest.raises(ServerError):
            wg.scan(training=[{"a": 1}, {"a": 2}], test=[{"a": 3}])

    @patch("waveguard.client.requests.Session")
    def test_connection_error(self, mock_session_cls):
        import requests as req

        session = MagicMock()
        session.request.side_effect = req.ConnectionError("Cannot connect")
        mock_session_cls.return_value = session

        wg = WaveGuard(api_key="test", max_retries=0)
        with pytest.raises(WaveGuardError, match="Cannot connect"):
            wg.scan(training=[{"a": 1}, {"a": 2}], test=[{"a": 3}])

    def test_exception_hierarchy(self):
        assert issubclass(AuthenticationError, WaveGuardError)
        assert issubclass(ValidationError, WaveGuardError)
        assert issubclass(RateLimitError, WaveGuardError)
        assert issubclass(ServerError, WaveGuardError)


# ── Health & Tier tests ───────────────────────────────────────────────────


class TestHealth:
    @patch("waveguard.client.requests.Session")
    def test_health_parses(self, mock_session_cls):
        session = MagicMock()
        session.request.return_value = _mock_response(
            200,
            {
                "status": "healthy",
                "version": "2.0.0",
                "gpu": "T4",
                "mode": "production",
                "uptime_seconds": 3600,
            },
        )
        mock_session_cls.return_value = session

        wg = WaveGuard(api_key="test", max_retries=0)
        h = wg.health()
        assert isinstance(h, HealthStatus)
        assert h.status == "healthy"
        assert h.gpu == "T4"

    @patch("waveguard.client.requests.Session")
    def test_tier_parses(self, mock_session_cls):
        session = MagicMock()
        session.request.return_value = _mock_response(
            200,
            {
                "tier": "PRO",
                "limits": {
                    "max_training_samples": 100,
                    "max_test_samples": 50,
                    "rate_limit_per_min": 60,
                },
            },
        )
        mock_session_cls.return_value = session

        wg = WaveGuard(api_key="test", max_retries=0)
        t = wg.tier()
        assert isinstance(t, TierInfo)
        assert t.tier == "PRO"
        assert t.limits["max_training_samples"] == 100


# ── Client configuration tests ────────────────────────────────────────────


class TestConfig:
    def test_default_url(self):
        wg = WaveGuard(api_key="test")
        assert "modal.run" in wg.base_url

    def test_custom_url(self):
        wg = WaveGuard(api_key="test", base_url="http://localhost:8000")
        assert wg.base_url == "http://localhost:8000"

    def test_trailing_slash_stripped(self):
        wg = WaveGuard(api_key="test", base_url="http://localhost:8000/")
        assert not wg.base_url.endswith("/")

    def test_repr(self):
        wg = WaveGuard(api_key="secret", base_url="http://localhost:8000")
        assert "secret" not in repr(wg)
        assert "localhost:8000" in repr(wg)
