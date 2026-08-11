/**
 * Centralized error handling for MCP tool execution.
 *
 * Converts unknown errors to proper MCP error responses.
 * Logs full error details server-side; returns safe messages to the client.
 */

import { ErrorCode, McpError } from '@modelcontextprotocol/sdk/types.js';
import { logger } from './logger.js';

/**
 * Wraps a tool execution function with:
 * - Automatic error logging
 * - Safe error messages (no internal details exposed to AI client)
 * - McpError passthrough (already properly formatted)
 */
export async function withErrorHandling<T>(
  toolName: string,
  fn: () => Promise<T>
): Promise<T> {
  try {
    return await fn();
  } catch (err) {
    // Already an MCP error — re-throw as-is
    if (err instanceof McpError) {
      logger.warn(`MCP error in tool ${toolName}`, {
        code: err.code,
        message: err.message,
      });
      throw err;
    }

    // Unknown error — log details, return generic message
    const message = err instanceof Error ? err.message : String(err);
    logger.error(`Unexpected error in tool ${toolName}`, {
      error: message,
      stack: err instanceof Error ? err.stack : undefined,
    });

    throw new McpError(
      ErrorCode.InternalError,
      `Tool "${toolName}" encountered an internal error. Check server logs for details.`
    );
  }
}

/**
 * Create a standardized tool result
 */
export function toolResult(text: string) {
  return {
    content: [{ type: 'text' as const, text }],
  };
}

/**
 * Create a JSON tool result
 */
export function jsonResult(data: unknown) {
  return toolResult(JSON.stringify(data, null, 2));
}
