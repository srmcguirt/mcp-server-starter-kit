/**
 * Fetch URL tool — fetches content from a URL and returns it as text.
 * Demonstrates: async operations, input validation, error handling,
 * timeout handling, and size limits.
 *
 * Extend this pattern to call your own APIs.
 */

import { z } from 'zod';
import { ErrorCode, McpError } from '@modelcontextprotocol/sdk/types.js';
import { toolResult } from '../lib/error-handler.js';
import { logger } from '../lib/logger.js';
import type { MCPTool } from '../types.js';

const FetchUrlSchema = z.object({
  url: z.string().url(),
  timeout_ms: z.number().int().positive().max(30_000).default(10_000),
  max_bytes: z.number().int().positive().max(1_000_000).default(100_000),
});

export const fetchUrlTool: MCPTool = {
  name: 'fetch_url',
  description:
    'Fetch the text content of a URL. Returns up to 100KB of content. ' +
    'Useful for reading web pages, APIs, or any HTTP endpoint.',
  inputSchema: {
    type: 'object',
    properties: {
      url: {
        type: 'string',
        format: 'uri',
        description: 'The URL to fetch',
      },
      timeout_ms: {
        type: 'number',
        description: 'Request timeout in milliseconds (default: 10000, max: 30000)',
        default: 10000,
      },
      max_bytes: {
        type: 'number',
        description: 'Maximum response size in bytes (default: 100000, max: 1000000)',
        default: 100000,
      },
    },
    required: ['url'],
  },
  async execute(args) {
    const { url, timeout_ms, max_bytes } = FetchUrlSchema.parse(args);

    logger.debug('Fetching URL', { url, timeout_ms, max_bytes });

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout_ms);

    try {
      const response = await fetch(url, {
        signal: controller.signal,
        headers: {
          'User-Agent': 'MCP-Server-Starter/1.0',
          Accept: 'text/plain, text/html, application/json, */*',
        },
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new McpError(
          ErrorCode.InvalidRequest,
          `HTTP ${response.status} ${response.statusText} from ${url}`
        );
      }

      // Read with size limit
      const reader = response.body?.getReader();
      if (!reader) throw new Error('No response body');

      let bytesRead = 0;
      const chunks: Uint8Array[] = [];

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        bytesRead += value.length;
        chunks.push(value);

        if (bytesRead >= max_bytes) {
          reader.cancel();
          break;
        }
      }

      const text = new TextDecoder().decode(
        chunks.reduce((acc, chunk) => {
          const merged = new Uint8Array(acc.length + chunk.length);
          merged.set(acc);
          merged.set(chunk, acc.length);
          return merged;
        }, new Uint8Array(0))
      );

      const truncated = bytesRead >= max_bytes;
      const result = truncated
        ? `${text}\n\n[Response truncated at ${max_bytes} bytes. Use max_bytes to increase limit.]`
        : text;

      logger.debug('URL fetched', { url, bytes: bytesRead, truncated });
      return toolResult(result);
    } catch (err) {
      clearTimeout(timeoutId);

      if (err instanceof McpError) throw err;

      if ((err as Error).name === 'AbortError') {
        throw new McpError(
          ErrorCode.InvalidRequest,
          `Request to ${url} timed out after ${timeout_ms}ms`
        );
      }

      throw err;
    }
  },
};
