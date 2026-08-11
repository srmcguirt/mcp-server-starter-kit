/**
 * Echo tool — returns whatever you send it.
 * Use this to verify your MCP server is wired up correctly.
 * Delete this once you have your real tools.
 */

import { z } from 'zod';
import { toolResult } from '../lib/error-handler.js';
import type { MCPTool } from '../types.js';

const EchoSchema = z.object({
  message: z.string().min(1).max(10_000),
});

export const echoTool: MCPTool = {
  name: 'echo',
  description: 'Echo back a message. Use to verify the MCP server is working.',
  inputSchema: {
    type: 'object',
    properties: {
      message: {
        type: 'string',
        description: 'The message to echo back',
        maxLength: 10000,
      },
    },
    required: ['message'],
  },
  async execute(args) {
    const { message } = EchoSchema.parse(args);
    return toolResult(`Echo: ${message}`);
  },
};
