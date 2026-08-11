"""Tests for the token-bucket rate limiter."""

import time

import pytest

from mcp_server.rate_limiter import RateLimiter


def test_allows_initial_requests():
    limiter = RateLimiter(max_requests=5, window_ms=60000)
    for _ in range(5):
        assert limiter.is_allowed("test") is True


def test_blocks_after_limit_exceeded():
    limiter = RateLimiter(max_requests=3, window_ms=60000)
    for _ in range(3):
        limiter.is_allowed("test")
    # 4th request should be denied
    assert limiter.is_allowed("test") is False


def test_remaining_decrements():
    limiter = RateLimiter(max_requests=10, window_ms=60000)
    assert limiter.remaining("test") == 10
    limiter.is_allowed("test")
    assert limiter.remaining("test") == 9


def test_separate_clients_independent():
    limiter = RateLimiter(max_requests=2, window_ms=60000)
    limiter.is_allowed("client_a")
    limiter.is_allowed("client_a")
    # client_a is exhausted
    assert limiter.is_allowed("client_a") is False
    # client_b is unaffected
    assert limiter.is_allowed("client_b") is True


def test_reset_at_returns_iso_string():
    limiter = RateLimiter(max_requests=1, window_ms=60000)
    limiter.is_allowed("test")  # exhaust
    reset_at = limiter.reset_at("test")
    # Should be a valid ISO 8601 string
    assert "T" in reset_at
    assert reset_at.endswith("+00:00") or reset_at.endswith("Z") or "+" in reset_at


def test_tokens_refill_over_time():
    """Tokens should refill as time passes (fast window for testing)."""
    limiter = RateLimiter(max_requests=2, window_ms=200)  # 200ms window
    limiter.is_allowed("test")
    limiter.is_allowed("test")
    assert limiter.is_allowed("test") is False  # exhausted

    time.sleep(0.15)  # wait for some refill
    assert limiter.remaining("test") >= 1
