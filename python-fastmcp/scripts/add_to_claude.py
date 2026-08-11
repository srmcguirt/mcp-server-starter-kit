#!/usr/bin/env python3
"""Auto-add this MCP server to Claude Desktop configuration.

Usage:
    python scripts/add_to_claude.py

Reads: ~/Library/Application Support/Claude/claude_desktop_config.json
Writes: same file, with this server added under mcpServers
"""

import json
import os
import sys
from pathlib import Path


def find_config() -> Path:
    """Find claude_desktop_config.json on this platform."""
    if sys.platform == "darwin":
        return (
            Path.home()
            / "Library"
            / "Application Support"
            / "Claude"
            / "claude_desktop_config.json"
        )
    elif sys.platform == "win32":
        appdata = os.environ.get("APPDATA", "")
        return Path(appdata) / "Claude" / "claude_desktop_config.json"
    else:
        # Linux
        return Path.home() / ".config" / "Claude" / "claude_desktop_config.json"


def main() -> None:
    config_path = find_config()
    server_dir = Path(__file__).parent.parent.resolve()

    print(f"Claude config: {config_path}")
    print(f"Server directory: {server_dir}")

    # Read existing config (or create empty)
    if config_path.exists():
        with open(config_path) as f:
            config = json.load(f)
    else:
        config = {}
        config_path.parent.mkdir(parents=True, exist_ok=True)

    # Add our server
    config.setdefault("mcpServers", {})
    server_name = "mcp-server-starter-python"

    config["mcpServers"][server_name] = {
        "command": "python",
        "args": ["-m", "mcp_server"],
        "cwd": str(server_dir),
        "env": {
            "RATE_LIMIT_MAX_REQUESTS": "60",
            "RATE_LIMIT_WINDOW_MS": "60000",
            "LOG_LEVEL": "INFO",
        },
    }

    # Write back
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)

    print(f"\n✅ Added '{server_name}' to Claude Desktop config.")
    print("   Restart Claude Desktop to connect.")
    print(f"\n   Config: {config_path}")


if __name__ == "__main__":
    main()
