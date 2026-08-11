/**
 * MCP Server Starter Kit — Production-Ready Boilerplate
 * @version 1.0.0
 *
 * Replace "starter" with your server name and implement your tools below.
 * See README.md for full documentation.
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ErrorCode,
  ListToolsRequestSchema,
  McpError,
} from '@modelcontextprotocol/sdk/types.js';
import { z } from 'zod';
import { logger } from './lib/logger.js';
import { RateLimiter } from './lib/rate-limiter.js';
import { validateEnv } from './lib/env.js';
import { withErrorHandling } from './lib/error-handler.js';
import { tools } from './tools/index.js';

// ─── Startup ────────────────────────────────────────────────────────────────

const env = validateEnv();
const rateLimiter = new RateLimiter({
  maxRequests: env.RATE_LIMIT_MAX_REQUESTS,
  windowMs: env.RATE_LIMIT_WINDOW_MS,
});

const server = new Server(
  {
    name: 'mcp-server-starter',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
      // Uncomment to enable resources and prompts:
      // resources: {},
      // prompts: {},
    },
  }
);

// ─── Tool listing ────────────────────────────────────────────────────────────

server.setRequestHandler(ListToolsRequestSchema, async () => {
  logger.debug('Listing tools');
  return {
    tools: tools.map((tool) => ({
      name: tool.name,
      description: tool.description,
      inputSchema: tool.inputSchema,
    })),
  };
});

// ─── Tool execution ──────────────────────────────────────────────────────────

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  logger.info(`Tool called: ${name}`, { args });

  // Rate limiting
  const clientId = 'default'; // Replace with actual client identification if needed
  if (!rateLimiter.isAllowed(clientId)) {
    throw new McpError(
      ErrorCode.InvalidRequest,
      `Rate limit exceeded. Max ${env.RATE_LIMIT_MAX_REQUESTS} requests per ${env.RATE_LIMIT_WINDOW_MS / 1000}s.`
    );
  }

  // Find and execute tool
  const tool = tools.find((t) => t.name === name);
  if (!tool) {
    throw new McpError(ErrorCode.MethodNotFound, `Unknown tool: ${name}`);
  }

  return withErrorHandling(name, () => tool.execute(args ?? {}));
});

// ─── Start server ─────────────────────────────────────────────────────────────

async function main() {
  logger.info('Starting MCP Server Starter Kit', {
    node: process.version,
    env: env.NODE_ENV,
  });

  const transport = new StdioServerTransport();
  await server.connect(transport);

  logger.info('MCP server running on stdio');
}

main().catch((err) => {
  logger.error('Fatal error starting server', { error: err });
  process.exit(1);
});
