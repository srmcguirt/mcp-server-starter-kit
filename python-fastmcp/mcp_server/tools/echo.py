"""Echo tool — returns input text unchanged.

Demonstrates the minimal tool pattern:
- Pydantic input validation
- Rate limiting
- Structured logging (stderr only)
- Error handling
"""

from pydantic import BaseModel, Field

from fastmcp import FastMCP

from ..logger import get_logger
from ..rate_limiter import RateLimiter

logger = get_logger(__name__)


class EchoInput(BaseModel):
    """Validated input for the echo tool."""

    text: str = Field(
        ...,
        description="Text to echo back",
        min_length=1,
        max_length=10000,
    )


def register_echo(mcp: FastMCP, rate_limiter: RateLimiter) -> None:
    """Register the echo tool with the MCP server."""

    @mcp.tool()
    async def echo(text: str) -> str:
        """Echo text back unchanged.

        Useful for testing that the MCP server is connected
        and Claude can call tools.

        Args:
            text: The text to echo. Must be 1-10000 characters.

        Returns:
            The same text, unchanged.
        """
        # Validate input with Pydantic
        args = EchoInput(text=text)

        # Rate limit by tool name
        if not rate_limiter.is_allowed("echo"):
            reset = rate_limiter.reset_at("echo")
            logger.warning("echo rate limit exceeded", reset_at=reset)
            raise ValueError(f"Rate limit exceeded for echo tool. Resets at {reset}")

        logger.info("echo called", text_length=len(args.text))
        return args.text
