# Production Dockerfile — Python/FastMCP MCP Server
# Multi-stage build: slim runtime image
# Security: non-root user, read-only filesystem where possible

# ---------- Build stage ----------
FROM python:3.12-slim AS builder

WORKDIR /build

# Install build dependencies
RUN pip install --no-cache-dir uv

# Copy dependency files first (layer cache)
COPY requirements.txt pyproject.toml ./

# Install into /build/venv
RUN uv venv /build/venv && \
    . /build/venv/bin/activate && \
    uv pip install --no-cache-dir -r requirements.txt

# ---------- Production stage ----------
FROM python:3.12-slim AS production

# Security: create non-root user
RUN groupadd --system mcp && \
    useradd --system --gid mcp --shell /bin/false mcp

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /build/venv /app/venv

# Copy application code
COPY mcp_server/ ./mcp_server/

# Set ownership
RUN chown -R mcp:mcp /app

# Switch to non-root user
USER mcp

# Activate venv
ENV PATH="/app/venv/bin:$PATH"
ENV PYTHONPATH="/app"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Healthcheck — verify the module imports cleanly
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD python -c "import mcp_server; print('ok')" || exit 1

# Default: stdio transport (for Claude Desktop via docker run)
# Override CMD for SSE: ["uvicorn", "mcp_server.server:app", "--host", "0.0.0.0", "--port", "8000"]
CMD ["python", "-m", "mcp_server"]
