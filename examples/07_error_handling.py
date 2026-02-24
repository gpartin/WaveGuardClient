"""
Example 7: Error Handling — gracefully handle API errors.

Shows how to catch and handle each error type:
  - AuthenticationError (bad key)
  - ValidationError (bad data)
  - RateLimitError (too many requests)
  - ServerError (transient failures)
  - WaveGuardError (catch-all)

Usage:
    export WAVEGUARD_API_KEY="your-key"
    python 07_error_handling.py
"""

import os
import time
from waveguard import (
    WaveGuard,
    WaveGuardError,
    AuthenticationError,
    ValidationError,
    RateLimitError,
    ServerError,
)

api_key = os.environ.get("WAVEGUARD_API_KEY", "demo")


def scan_with_retry(wg, training, test, max_retries=3):
    """Scan with automatic retry on transient errors."""
    for attempt in range(max_retries):
        try:
            return wg.scan(training=training, test=test)

        except AuthenticationError:
            print("❌ Bad API key — check your WAVEGUARD_API_KEY")
            raise  # Don't retry auth errors

        except ValidationError as e:
            print(f"❌ Data validation failed: {e.detail}")
            raise  # Don't retry bad data

        except RateLimitError:
            wait = 2 ** attempt  # exponential backoff
            print(f"⏳ Rate limited — retrying in {wait}s (attempt {attempt + 1}/{max_retries})")
            time.sleep(wait)

        except ServerError:
            wait = 2 ** attempt
            print(f"⚠️  Server error — retrying in {wait}s (attempt {attempt + 1}/{max_retries})")
            time.sleep(wait)

        except WaveGuardError as e:
            print(f"❌ Unexpected error ({e.status_code}): {e.message}")
            raise

    raise WaveGuardError(f"Failed after {max_retries} retries")


# ── Demo 1: Successful scan ──────────────────────────────────────────────
print("=== Error Handling Examples ===\n")
print("--- Demo 1: Normal scan with retry wrapper ---")

wg = WaveGuard(api_key=api_key)

training = [{"x": 1}, {"x": 2}, {"x": 3}]
test = [{"x": 2}, {"x": 100}]

try:
    result = scan_with_retry(wg, training, test)
    print(f"✅ Scan complete: {result.summary.anomalies_found} anomalies\n")
except WaveGuardError as e:
    print(f"Scan failed: {e.message}\n")


# ── Demo 2: Bad API key ──────────────────────────────────────────────────
print("--- Demo 2: Bad API key ---")

bad_wg = WaveGuard(api_key="definitely-not-a-real-key")

try:
    bad_wg.scan(training=training, test=test)
except AuthenticationError as e:
    print(f"Caught AuthenticationError: {e.message}")
    print(f"  HTTP status: {e.status_code}\n")
except WaveGuardError:
    print("Caught some other error (API might accept any key in demo mode)\n")


# ── Demo 3: Validation error ────────────────────────────────────────────
print("--- Demo 3: Invalid data ---")

try:
    # Empty training array should fail validation
    wg.scan(training=[], test=[{"x": 1}])
except ValidationError as e:
    print(f"Caught ValidationError: {e.message}\n")
except WaveGuardError as e:
    print(f"Caught error: {e.message}\n")

print("Done!")
