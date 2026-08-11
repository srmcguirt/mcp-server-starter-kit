/**
 * Tool registry — add your custom tools here.
 *
 * Each tool must implement the MCPTool interface:
 * - name: unique identifier (snake_case recommended)
 * - description: what the tool does (AI uses this to decide when to call it)
 * - inputSchema: JSON Schema for input validation
 * - execute: the actual implementation
 *
 * Example tools included:
 * - echo: simple hello-world tool to verify the server works
 * - fetch_url: fetch content from a URL (demonstrates async + external calls)
 *
 * Delete example tools and add your own!
 */

import type { MCPTool } from '../types.js';
import { echoTool } from './echo.js';
import { fetchUrlTool } from './fetch-url.js';

export const tools: MCPTool[] = [
  echoTool,
  fetchUrlTool,
  // Add your tools here:
  // myCustomTool,
];
