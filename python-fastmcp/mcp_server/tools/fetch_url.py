"""Fetch URL tool — HTTP GET with timeout and size limit.

Demonstrates async HTTP calls in an MCP tool with:
- Timeout control (prevents hanging tool calls)
- Response size limit (prevents memory exhaustion)
- Pydantic input validation
- Rate limiting
- Structured error responses
"""

from typing import Any

import httpx
from pydantic import BaseModel, Field, HttpUrl

from fastmcp import FastMCP

from ..logger import get_logger
from ..rate_limiter import RateLimiter

logger = get_logger(__name__)

# Safety limits
DEFAULT_TIMEOUT_SECONDS = 10
DEFAULT_MAX_BYTES = 1024 * 1024  # 1MB
MAX_ALLOWED_BYTES = 10 * 1024 * 1024  # 10MB hard cap


class FetchUrlInput(BaseModel):
    """Validated input for the fetch_url tool."""

    url: HttpUrl = Field(..., description="URL to fetch (must be http or https)")
    timeout_seconds: int = Field(
        default=DEFAULT_TIMEOUT_SECONDS,
        ge=1,
        le=30,
        description="Request timeout in seconds",
    )
    max_bytes: int = Field(
        default=DEFAULT_MAX_BYTES,
        ge=1,
        le=MAX_ALLOWED_BYTES,
        description="Maximum response size in bytes",
    )


def register_fetch_url(mcp: FastMCP, rate_limiter: RateLimiter) -> None:
    """Register the fetch_url tool with the MCP server."""

    @mcp.tool()
    async def fetch_url(
        url: str,
        timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
        max_bytes: int = DEFAULT_MAX_BYTES,
    ) -> dict[str, Any]:
        """Fetch the content of a URL via HTTP GET.

        Returns the response status, headers, and body (truncated if too large).

        Args:
            url: The URL to fetch. Must be http or https.
            timeout_seconds: How long to wait before giving up (1-30s).
            max_bytes: Maximum response body size to return (default 1MB, max 10MB).

        Returns:
            Dict with status_code, content_type, body, and truncated flag.
        """
        # Validate inputs
        args = FetchUrlInput(url=url, timeout_seconds=timeout_seconds, max_bytes=max_bytes)
        url_str = str(args.url)

        # Rate limit
        if not rate_limiter.is_allowed("fetch_url"):
            reset = rate_limiter.reset_at("fetch_url")
            logger.warning("fetch_url rate limit exceeded", url=url_str, reset_at=reset)
            raise ValueError(f"Rate limit exceeded for fetch_url. Resets at {reset}")

        logger.info("fetch_url called", url=url_str, timeout=args.timeout_seconds)

        async with httpx.AsyncClient(
            timeout=httpx.Timeout(args.timeout_seconds),
            follow_redirects=True,
            limits=httpx.Limits(max_connections=10),
        ) as client:
            response = await client.get(url_str)

        # Read body up to max_bytes
        body = response.text
        truncated = False
        if len(response.content) > args.max_bytes:
            # Decode only what we need
            body = response.content[: args.max_bytes].decode("utf-8", errors="replace")
            truncated = True

        logger.info(
            "fetch_url complete",
            url=url_str,
            status_code=response.status_code,
            content_length=len(response.content),
            truncated=truncated,
        )

        return {
            "status_code": response.status_code,
            "content_type": response.headers.get("content-type", "unknown"),
            "body": body,
            "truncated": truncated,
            "bytes_returned": len(body.encode("utf-8")),
        }
