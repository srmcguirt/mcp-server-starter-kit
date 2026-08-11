"""Structured logging to stderr only.

CRITICAL: Never log to stdout in an MCP server.
stdout is reserved for JSON-RPC protocol messages.
Any non-JSON-RPC output on stdout corrupts the MCP session.

This module configures structlog to write to sys.stderr exclusively.
"""

import logging
import sys

import structlog

from .config import settings

# Map string log level to logging constant
_LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}

_level = _LOG_LEVELS.get(settings.log_level.upper(), logging.INFO)

# Configure stdlib logging — stderr only, never stdout
logging.basicConfig(
    level=_level,
    stream=sys.stderr,  # ← CRITICAL: stderr, not stdout
    format="%(message)s",
)

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer(
            colors=False  # No ANSI codes — keeps stderr clean in non-TTY envs
        ),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(_level),
    logger_factory=structlog.PrintLoggerFactory(file=sys.stderr),  # ← stderr
    cache_logger_on_first_use=True,
)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a named structured logger writing to stderr."""
    return structlog.get_logger(name)
