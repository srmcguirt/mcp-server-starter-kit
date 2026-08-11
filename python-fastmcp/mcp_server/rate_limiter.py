"""Token-bucket rate limiter.

Prevents runaway AI agent tool calls from hammering downstream APIs.
Claude can loop tool calls — without rate limiting, you may see 5+ calls/second
until an error occurs or a user interrupts.

Usage:
    limiter = RateLimiter(max_requests=60, window_ms=60000)

    if not limiter.is_allowed("my_tool"):
        raise ValueError(f"Rate limit exceeded. Resets at {limiter.reset_at('my_tool')}")

    # proceed with tool logic
"""

import threading
import time
from dataclasses import dataclass, field


@dataclass
class _Bucket:
    """Per-client rate limit state."""
    tokens: float
    last_refill: float = field(default_factory=time.monotonic)


class RateLimiter:
    """Token-bucket rate limiter with per-client tracking.

    Each client_id (typically a tool name) gets its own bucket.
    Tokens refill at a constant rate up to max_requests per window.
    """

    def __init__(self, max_requests: int = 60, window_ms: int = 60000) -> None:
        self._max = max_requests
        self._window_s = window_ms / 1000.0
        self._refill_rate = max_requests / self._window_s  # tokens per second
        self._buckets: dict[str, _Bucket] = {}
        self._lock = threading.Lock()

    def _refill(self, bucket: _Bucket) -> None:
        """Add tokens based on elapsed time since last refill."""
        now = time.monotonic()
        elapsed = now - bucket.last_refill
        bucket.tokens = min(self._max, bucket.tokens + elapsed * self._refill_rate)
        bucket.last_refill = now

    def is_allowed(self, client_id: str) -> bool:
        """Check if a request is allowed. Consumes one token if so."""
        with self._lock:
            if client_id not in self._buckets:
                self._buckets[client_id] = _Bucket(tokens=float(self._max))
            bucket = self._buckets[client_id]
            self._refill(bucket)
            if bucket.tokens >= 1.0:
                bucket.tokens -= 1.0
                return True
            return False

    def remaining(self, client_id: str) -> int:
        """Return the number of tokens remaining for a client."""
        with self._lock:
            if client_id not in self._buckets:
                return self._max
            bucket = self._buckets[client_id]
            self._refill(bucket)
            return int(bucket.tokens)

    def reset_at(self, client_id: str) -> str:
        """Return ISO 8601 timestamp when the bucket will have 1 token again."""
        with self._lock:
            if client_id not in self._buckets:
                return _iso_now()
            bucket = self._buckets[client_id]
            self._refill(bucket)
            tokens_needed = max(0.0, 1.0 - bucket.tokens)
            seconds_until_reset = tokens_needed / self._refill_rate
            reset_epoch = time.time() + seconds_until_reset
            return _iso_from_epoch(reset_epoch)


def _iso_now() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()


def _iso_from_epoch(epoch: float) -> str:
    from datetime import datetime, timezone
    return datetime.fromtimestamp(epoch, tz=timezone.utc).isoformat()
