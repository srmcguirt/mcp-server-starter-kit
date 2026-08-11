/**
 * Environment variable validation.
 * Fails fast on startup if required env vars are missing.
 * Add your own required variables here.
 */

import { z } from 'zod';
import dotenv from 'dotenv';

dotenv.config();

const EnvSchema = z.object({
  NODE_ENV: z.enum(['development', 'production', 'test']).default('development'),
  LOG_LEVEL: z.enum(['error', 'warn', 'info', 'debug']).default('info'),

  // Rate limiting
  RATE_LIMIT_MAX_REQUESTS: z.coerce.number().positive().default(60),
  RATE_LIMIT_WINDOW_MS: z.coerce.number().positive().default(60_000),

  // Add your own API keys and config here:
  // MY_API_KEY: z.string().min(1, 'MY_API_KEY is required'),
  // MY_API_BASE_URL: z.string().url().default('https://api.example.com'),
});

export type Env = z.infer<typeof EnvSchema>;

export function validateEnv(): Env {
  const result = EnvSchema.safeParse(process.env);

  if (!result.success) {
    const errors = result.error.errors
      .map((e) => `  ${e.path.join('.')}: ${e.message}`)
      .join('\n');
    throw new Error(`Environment validation failed:\n${errors}\n\nSee .env.example for required variables.`);
  }

  return result.data;
}
