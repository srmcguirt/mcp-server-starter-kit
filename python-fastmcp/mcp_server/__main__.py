"""Entry point for stdio transport.

Run with:
    python -m mcp_server

This is the mode used by Claude Desktop, Cursor, Cline, Windsurf.
The server communicates via stdin/stdout (JSON-RPC over stdio).

CRITICAL: Do not print anything to stdout here.
stdout is the JSON-RPC transport. Any print() corrupts it.
Use the logger (which writes to stderr) for all output.
"""

import sys

from .logger import get_logger
from .server import mcp

logger = get_logger(__name__)


def main() -> None:
    """Start the MCP server in stdio mode."""
    logger.info("Starting MCP server (stdio transport)")

    try:
        mcp.run()  # Blocks, reads from stdin, writes to stdout (JSON-RPC only)
    except KeyboardInterrupt:
        logger.info("MCP server stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error("MCP server crashed", error=str(e), exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
