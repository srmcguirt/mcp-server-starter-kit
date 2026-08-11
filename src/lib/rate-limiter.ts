/**
 * Token-bucket rate limiter.
 * Prevents a runaway AI agent from hammering your downstream APIs.
 *
 * Usage:
 *   const limiter = new RateLimiter({ maxRequests: 60, windowMs: 60_000 })
 *   if (!limiter.isAllowed('client-id')) throw new McpError(...)
 */

interface RateLimiterOptions {
  maxRequests: number;
  windowMs: number;
}

interface WindowEntry {
  count: number;
  resetAt: number;
}

export class RateLimiter {
  private readonly maxRequests: number;
  private readonly windowMs: number;
  private readonly windows: Map<string, WindowEntry> = new Map();

  constructor({ maxRequests, windowMs }: RateLimiterOptions) {
    this.maxRequests = maxRequests;
    this.windowMs = windowMs;

    // Prune stale windows every minute to prevent memory growth
    setInterval(() => this.prune(), 60_000).unref();
  }

  isAllowed(clientId: string): boolean {
    const now = Date.now();
    const entry = this.windows.get(clientId);

    if (!entry || now >= entry.resetAt) {
      this.windows.set(clientId, { count: 1, resetAt: now + this.windowMs });
      return true;
    }

    if (entry.count >= this.maxRequests) {
      return false;
    }

    entry.count++;
    return true;
  }

  remaining(clientId: string): number {
    const now = Date.now();
    const entry = this.windows.get(clientId);
    if (!entry || now >= entry.resetAt) return this.maxRequests;
    return Math.max(0, this.maxRequests - entry.count);
  }

  resetAt(clientId: string): number {
    const entry = this.windows.get(clientId);
    return entry?.resetAt ?? Date.now();
  }

  private prune() {
    const now = Date.now();
    for (const [id, entry] of this.windows.entries()) {
      if (now >= entry.resetAt) {
        this.windows.delete(id);
      }
    }
  }
}
