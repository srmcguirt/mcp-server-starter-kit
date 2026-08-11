/**
 * Structured logger — uses Winston for JSON output in production,
 * human-readable format in development.
 *
 * MCP servers communicate via stdio, so we log to stderr to avoid
 * contaminating the MCP protocol stream.
 */

import { createLogger, format, transports } from 'winston';

const isDev = process.env.NODE_ENV !== 'production';

export const logger = createLogger({
  level: process.env.LOG_LEVEL ?? (isDev ? 'debug' : 'info'),
  format: isDev
    ? format.combine(
        format.colorize(),
        format.timestamp({ format: 'HH:mm:ss' }),
        format.printf(({ timestamp, level, message, ...meta }) => {
          const metaStr = Object.keys(meta).length ? ` ${JSON.stringify(meta)}` : '';
          return `${timestamp} ${level}: ${message}${metaStr}`;
        })
      )
    : format.combine(format.timestamp(), format.json()),
  // CRITICAL: Log to stderr, not stdout — stdout is reserved for MCP protocol
  transports: [new transports.Stream({ stream: process.stderr })],
});
