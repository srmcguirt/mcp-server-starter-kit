"""Environment configuration with Pydantic Settings validation.

Fails fast on startup if required variables are missing or invalid.
No silent misconfigurations.
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Server configuration from environment variables."""

    # Rate limiting
    rate_limit_max_requests: int = Field(
        default=60,
        ge=1,
        le=10000,
        description="Maximum requests per rate-limit window",
    )
    rate_limit_window_ms: int = Field(
        default=60000,
        ge=1000,
        description="Rate limit window duration in milliseconds",
    )

    # Server identity
    mcp_server_name: str = Field(
        default="mcp-server-starter",
        description="Server name shown in Claude Desktop",
    )

    # Logging
    log_level: str = Field(
        default="INFO",
        pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$",
        description="Log level",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        # Raises ValidationError on startup if any required field is invalid
        extra="ignore",
    )


# Singleton — import this everywhere
# Raises pydantic.ValidationError if env is misconfigured — fails fast, not silently
settings = Settings()
