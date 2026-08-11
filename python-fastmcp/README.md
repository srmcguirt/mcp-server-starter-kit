# MCP Server Starter Kit — Python/FastMCP Edition

Production-ready MCP server boilerplate in Python using [FastMCP](https://github.com/jlowin/fastmcp).

> Part of the **WireForge MCP Server Starter Kit** premium tier.

---

## Why Python + FastMCP?

FastMCP is the cleanest way to build MCP servers in Python. It handles the protocol boilerplate so you focus on your tools.

```python
# TypeScript MCP server:
server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [{ name: 'echo', ... }]
}))
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  if (request.params.name === 'echo') { ... }
})

# Python FastMCP:
@mcp.tool()
async def echo(text: str) -> str:
    """Echo a message back."""
    return text
```

Same protocol. Half the code.

---

## Quickstart

```bash
# Clone or copy this folder
cd python-fastmcp

# Install
pip install -r requirements.txt
# or with uv (recommended)
uv pip install -r requirements.txt

# Configure
cp .env.example .env

# Run
python -m mcp_server

# Or with uvicorn for SSE transport
uvicorn mcp_server.server:app --port 8000
```

---

## Project Structure

```
python-fastmcp/
├── mcp_server/
│   ├── __init__.py
│   ├── __main__.py          # Entry point (python -m mcp_server)
│   ├── server.py            # FastMCP app, ASGI app for SSE
│   ├── config.py            # Pydantic Settings, env validation
│   ├── logger.py            # Structlog — stderr only (never stdout!)
│   ├── rate_limiter.py      # Token-bucket rate limiter
│   └── tools/
│       ├── __init__.py      # Tool registry
│       ├── echo.py          # Example: echo tool
│       └── fetch_url.py     # Example: HTTP fetch tool
├── tests/
│   ├── test_echo.py
│   ├── test_fetch_url.py
│   └── test_rate_limiter.py
├── .env.example
├── requirements.txt
├── pyproject.toml
└── Dockerfile               # Production-ready
```

---

## Adding Your Own Tool

```python
# mcp_server/tools/my_tool.py
from fastmcp import FastMCP
from pydantic import BaseModel, Field
from ..logger import get_logger
from ..rate_limiter import RateLimiter

logger = get_logger(__name__)


class SearchInput(BaseModel):
    query: str = Field(..., description="Search query", min_length=1, max_length=500)
    limit: int = Field(10, description="Max results", ge=1, le=100)


def register_my_tool(mcp: FastMCP, rate_limiter: RateLimiter) -> None:
    @mcp.tool()
    async def search_database(query: str, limit: int = 10) -> dict:
        """Search the database and return matching records."""
        # Validate with Pydantic
        args = SearchInput(query=query, limit=limit)
        
        # Rate limiting
        if not rate_limiter.is_allowed("search_database"):
            raise ValueError(f"Rate limit exceeded. Resets at {rate_limiter.reset_at()}")
        
        logger.info("search_database called", query=args.query, limit=args.limit)
        
        # Your logic here
        results = await db.search(args.query, args.limit)
        
        return {"results": results, "count": len(results)}
```

Then register it in `mcp_server/tools/__init__.py`:

```python
from .my_tool import register_my_tool

def register_all_tools(mcp: FastMCP, rate_limiter: RateLimiter) -> None:
    register_echo(mcp, rate_limiter)
    register_fetch_url(mcp, rate_limiter)
    register_my_tool(mcp, rate_limiter)  # ← add this
```

---

## Claude Desktop Configuration

```json
{
  "mcpServers": {
    "my-python-server": {
      "command": "python",
      "args": ["-m", "mcp_server"],
      "cwd": "/path/to/python-fastmcp",
      "env": {
        "RATE_LIMIT_MAX_REQUESTS": "60",
        "RATE_LIMIT_WINDOW_MS": "60000"
      }
    }
  }
}
```

Or use the auto-config script:

```bash
python scripts/add_to_claude.py
```

---

## Transport Modes

**stdio (default)** — For Claude Desktop, Cursor, Cline:

```bash
python -m mcp_server
```

**SSE (HTTP)** — For remote deployment or multi-client:

```bash
uvicorn mcp_server.server:app --host 0.0.0.0 --port 8000
```

Then configure with the SSE URL:

```json
{
  "mcpServers": {
    "my-server": {
      "url": "http://localhost:8000/sse"
    }
  }
}
```

---

## Key Design Decisions

### Stderr-only logging
```python
# logger.py — structlog configured to write to sys.stderr
# NEVER use print() or log to sys.stdout in an MCP server
# stdout is reserved for JSON-RPC protocol messages
```

### Pydantic Settings for env validation
```python
# config.py
class Settings(BaseSettings):
    rate_limit_max_requests: int = Field(60, ge=1, le=10000)
    rate_limit_window_ms: int = Field(60000, ge=1000)
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

# Fails fast on startup if validation fails — no silent misconfigs
settings = Settings()
```

### Token-bucket rate limiting
```python
# rate_limiter.py — same algorithm as TypeScript edition
class RateLimiter:
    def is_allowed(self, client_id: str) -> bool: ...
    def remaining(self, client_id: str) -> int: ...
    def reset_at(self, client_id: str) -> str: ...  # ISO 8601 timestamp
```
