# 🚀 MCP Server Starter Kit

**Production-ready Model Context Protocol (MCP) server boilerplate.** 
Ship your first MCP server in minutes, not days.

[![CI](https://github.com/srmcguirt/mcp-server-starter-kit/actions/workflows/ci.yml/badge.svg)](https://github.com/srmcguirt/mcp-server-starter-kit/actions/workflows/ci.yml) ![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg) ![TypeScript](https://img.shields.io/badge/TypeScript-5.x-3178C6?logo=typescript&logoColor=white) ![Node](https://img.shields.io/badge/Node-%3E%3D18-339933?logo=node.js&logoColor=white) ![MCP](https://img.shields.io/badge/MCP-Compatible-8A2BE2)

> 💎 **Premium edition** with Python (FastMCP) version, Railway/Render deploy configs, auth patterns, and 1-on-1 setup support → [Get it on Gumroad →](https://srmcguirt.gumroad.com/l/mcp-starter)

---

## What's included

| Feature | Status |
|---------|--------|
| TypeScript with strict mode | ✅ |
| Proper stderr logging (won't break MCP stdio) | ✅ |
| Token-bucket rate limiter | ✅ |
| Environment variable validation (Zod) | ✅ |
| Centralized error handling | ✅ |
| 2 example tools (echo + fetch_url) | ✅ |
| Docker + docker-compose | ✅ |
| Claude Desktop auto-config script | ✅ |
| Unit test setup (Vitest) | ✅ |
| Python/FastMCP version | 💎 Premium |
| Railway one-click deploy | 💎 Premium |
| API key auth middleware | 💎 Premium |
| OAuth 2.0 integration pattern | 💎 Premium |
| Webhook receiver tool | 💎 Premium |
| Database connection pattern | 💎 Premium |

---

## Why this starter kit?

Every MCP server tutorial shows you a 30-line "hello world." Then you try to build something real and discover:

- **Logging to stdout breaks MCP** — the protocol uses stdout for communication; your `console.log` corrupts it
- **No rate limiting** — a runaway AI agent can hammer your APIs
- **No input validation** — AI can send malformed arguments and crash your server
- **No error handling** — unhandled exceptions crash the whole server
- **No deploy story** — how do you actually run this in production?

This starter kit solves all of that from day one.

---

## Quick start

### Option 1: Use as a template

```bash
# Clone and rename
git clone https://github.com/srmcguirt/mcp-server-starter-kit my-mcp-server
cd my-mcp-server

# Install dependencies
npm install

# Copy env file and fill in your values
cp .env.example .env

# Start in dev mode (hot reload)
npm run dev
```

### Option 2: Scaffold with npx

```bash
npx @srmcguirt/mcp-server-starter init my-server-name
cd my-server-name
npm install && npm run dev
```

### Option 3: Install as a library

```bash
npm install @srmcguirt/mcp-server-starter
```

---

## Add your first tool

Open `src/tools/` and create a new file:

```typescript
// src/tools/my-tool.ts
import { z } from 'zod';
import { toolResult } from '../lib/error-handler.js';
import type { MCPTool } from '../types.js';

const MyInputSchema = z.object({
 query: z.string().min(1).max(500),
 limit: z.number().int().positive().max(100).default(10),
});

export const myTool: MCPTool = {
 name: 'my_tool',
 description: 'Search for something and return results. Be specific about what this does — the AI reads this description.',
 inputSchema: {
 type: 'object',
 properties: {
 query: { type: 'string', description: 'The search query' },
 limit: { type: 'number', description: 'Max results to return', default: 10 },
 },
 required: ['query'],
 },
 async execute(args) {
 const { query, limit } = MyInputSchema.parse(args);

 // Your implementation here
 const results = await myApi.search(query, { limit });

 return toolResult(JSON.stringify(results, null, 2));
 },
};
```

Then register it in `src/tools/index.ts`:

```typescript
import { myTool } from './my-tool.js';

export const tools: MCPTool[] = [
 echoTool,
 fetchUrlTool,
 myTool, // 👈 Add here
];
```

---

## Connect to Claude Desktop

```bash
# Build and add to Claude Desktop config automatically
chmod +x scripts/add-to-claude.sh
./scripts/add-to-claude.sh my-server-name

# Then restart Claude Desktop
```

Or manually add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
 "mcpServers": {
 "my-server-name": {
 "command": "node",
 "args": ["/absolute/path/to/my-mcp-server/dist/index.js"],
 "env": {
 "MY_API_KEY": "your-key-here"
 }
 }
 }
}
```

---

## Connect to Cursor / Cline / Windsurf

Add to your editor's MCP settings:

```json
{
 "mcp": {
 "servers": {
 "my-server-name": {
 "command": "node",
 "args": ["/absolute/path/to/my-mcp-server/dist/index.js"]
 }
 }
 }
}
```

---

## Deploy with Docker

```bash
# Build and run with docker-compose
cd docker && docker-compose up --build

# Or build manually
docker build -f docker/Dockerfile -t my-mcp-server .
docker run -it --env-file .env my-mcp-server
```

---

## Project structure

```
mcp-server-starter/
├── src/
│ ├── index.ts # Server entry point — wire everything together here
│ ├── types.ts # MCPTool interface and shared types
│ ├── lib/
│ │ ├── logger.ts # Winston logger — always logs to stderr
│ │ ├── rate-limiter.ts # Token-bucket rate limiter
│ │ ├── env.ts # Environment variable validation (Zod)
│ │ └── error-handler.ts # Centralized error handling + toolResult helpers
│ └── tools/
│ ├── index.ts # Tool registry — add your tools here
│ ├── echo.ts # Example: simple string echo
│ └── fetch-url.ts # Example: HTTP fetch with timeout + size limit
├── docker/
│ ├── Dockerfile # Multi-stage production build
│ └── docker-compose.yml # Local development + production compose
├── scripts/
│ └── add-to-claude.sh # Auto-add to Claude Desktop config
├── .env.example # Required environment variables
├── tsconfig.json # Strict TypeScript config
└── package.json
```

---

## Key patterns

### ✅ Always log to stderr

```typescript
// ❌ WRONG — corrupts MCP protocol
console.log('something happened');

// ✅ CORRECT — logs to stderr, leaves stdout clean
logger.info('something happened');
```

### ✅ Validate all input with Zod

```typescript
// ❌ WRONG — trusting AI-provided args
const { query } = args as { query: string };

// ✅ CORRECT — parse and validate
const { query } = MySchema.parse(args); // throws McpError on invalid input
```

### ✅ Use withErrorHandling for every tool

```typescript
// ❌ WRONG — unhandled exceptions crash the server
async execute(args) {
 return await riskyOperation(args);
}

// ✅ CORRECT — errors logged + safe message returned to AI
return withErrorHandling('my_tool', () => riskyOperation(args));
```

---

## 💎 Premium Edition — $49

The open source version is a solid foundation. The **Gumroad premium download** adds:

- ✅ Python/FastMCP version (same patterns, same quality)
- ✅ API key authentication middleware
- ✅ OAuth 2.0 integration pattern (GitHub, Google, etc.)
- ✅ Railway + Render one-click deploy configs
- ✅ Database connection patterns (Postgres, SQLite, Redis)
- ✅ Webhook receiver tool template
- ✅ Streaming responses pattern
- ✅ MCP resources and prompts examples
- ✅ 30-min video walkthrough: building a real production MCP server
- ✅ 6 real-world example servers (GitHub, Notion, Slack, Postgres, filesystem, web search)
- ✅ Commercial license (use in client work and products)

**[Get the premium edition →](https://srmcguirt.gumroad.com/l/mcp-starter)**

---

## FAQ

**Q: Why TypeScript and not JavaScript?** 
A: MCP tool schemas need to match your implementation exactly. TypeScript catches mismatches at build time, not at 2am when an AI passes unexpected input.

**Q: Why log to stderr?** 
A: MCP uses stdio transport — stdout carries the JSON-RPC protocol. Anything you write to stdout that isn't valid MCP JSON will corrupt the connection. The logger in this kit always writes to stderr.

**Q: Can I use this with Python?** 
A: The Python/FastMCP version is in the premium edition. The patterns are identical — just in Python.

**Q: Is this compatible with all MCP clients?** 
A: Yes. Uses the official `@modelcontextprotocol/sdk`. Tested with Claude Desktop, Cursor, Cline, and Windsurf.

---

## Contributing

PRs welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## License

MIT — free for personal and open source use. 
Commercial license (client work, products, resale) included in the [Premium Edition on Gumroad](https://srmcguirt.gumroad.com/l/mcp-starter).

---

## 📬 Stay Updated

Get a free sample prompt + updates when new tools ship:

**→ [srmcguirt.dev](https://srmcguirt.dev)**
