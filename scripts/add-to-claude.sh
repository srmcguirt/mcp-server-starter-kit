#!/bin/bash
# Add this MCP server to Claude Desktop's config
# Run: chmod +x scripts/add-to-claude.sh && ./scripts/add-to-claude.sh

set -e

SERVER_NAME="${1:-my-mcp-server}"
SERVER_DIR="$(cd "$(dirname "$0")/.." && pwd)"
CONFIG_PATH="$HOME/Library/Application Support/Claude/claude_desktop_config.json"

echo "📦 Adding MCP server to Claude Desktop..."
echo "   Server name: $SERVER_NAME"
echo "   Server dir:  $SERVER_DIR"
echo "   Config path: $CONFIG_PATH"

# Build first
echo ""
echo "🔨 Building server..."
cd "$SERVER_DIR" && npm run build

# Create config dir if needed
mkdir -p "$(dirname "$CONFIG_PATH")"

# Check if config exists
if [ ! -f "$CONFIG_PATH" ]; then
  echo '{"mcpServers":{}}' > "$CONFIG_PATH"
fi

# Add server using node (handles JSON safely)
node - "$SERVER_NAME" "$SERVER_DIR" "$CONFIG_PATH" << 'EOF'
const fs = require('fs');
const [,, name, dir, configPath] = process.argv;

const config = JSON.parse(fs.readFileSync(configPath, 'utf-8'));
config.mcpServers = config.mcpServers || {};
config.mcpServers[name] = {
  command: 'node',
  args: [`${dir}/dist/index.js`],
  env: {}
};

fs.writeFileSync(configPath, JSON.stringify(config, null, 2));
console.log(`✅ Added "${name}" to Claude Desktop config`);
console.log('');
console.log('🔄 Restart Claude Desktop to pick up the change.');
EOF
