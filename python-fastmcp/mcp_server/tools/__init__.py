"""Tool registry — register all tools with the FastMCP instance."""

from fastmcp import FastMCP

from ..rate_limiter import RateLimiter
from .echo import register_echo
from .fetch_url import register_fetch_url


def register_all_tools(mcp: FastMCP, rate_limiter: RateLimiter) -> None:
    """Register all MCP tools.

    To add a new tool:
    1. Create mcp_server/tools/my_tool.py
    2. Define register_my_tool(mcp, rate_limiter) in it
    3. Import and call it here
    """
    register_echo(mcp, rate_limiter)
    register_fetch_url(mcp, rate_limiter)
