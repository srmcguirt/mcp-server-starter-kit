"""FastMCP server — main application factory.

Creates the FastMCP instance, registers all tools, and
exposes both stdio (for Claude Desktop) and ASGI (for SSE/HTTP).

CRITICAL: All logging goes to stderr. stdout is reserved for JSON-RPC.
"""

from fastmcp import FastMCP

from .config import settings
from .logger import get_logger
from .rate_limiter import RateLimiter
from .tools import register_all_tools

logger = get_logger(__name__)

# Build the FastMCP application
mcp = FastMCP(name=settings.mcp_server_name)

# Build shared rate limiter
rate_limiter = RateLimiter(
    max_requests=settings.rate_limit_max_requests,
    window_ms=settings.rate_limit_window_ms,
)

# Register all tools
register_all_tools(mcp, rate_limiter)

logger.info(
    "MCP server initialized",
    name=settings.mcp_server_name,
    rate_limit_max=settings.rate_limit_max_requests,
    rate_limit_window_ms=settings.rate_limit_window_ms,
)

# ASGI app — for SSE transport (uvicorn mcp_server.server:app)
app = mcp.http_app()
