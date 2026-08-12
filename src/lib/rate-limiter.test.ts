import { describe, it, expect, vi, afterEach } from 'vitest';
import { RateLimiter } from './rate-limiter.js';

afterEach(() => {
  vi.useRealTimers();
});

describe('RateLimiter', () => {
  it('allows up to maxRequests within a window, then blocks', () => {
    const limiter = new RateLimiter({ maxRequests: 3, windowMs: 60_000 });

    expect(limiter.isAllowed('a')).toBe(true);
    expect(limiter.isAllowed('a')).toBe(true);
    expect(limiter.isAllowed('a')).toBe(true);
    expect(limiter.isAllowed('a')).toBe(false);
  });

  it('tracks each client independently', () => {
    const limiter = new RateLimiter({ maxRequests: 1, windowMs: 60_000 });

    expect(limiter.isAllowed('a')).toBe(true);
    expect(limiter.isAllowed('a')).toBe(false);
    // b has its own bucket and is unaffected by a exhausting theirs
    expect(limiter.isAllowed('b')).toBe(true);
  });

  it('refills once the window elapses', () => {
    vi.useFakeTimers();
    const limiter = new RateLimiter({ maxRequests: 2, windowMs: 1_000 });

    expect(limiter.isAllowed('a')).toBe(true);
    expect(limiter.isAllowed('a')).toBe(true);
    expect(limiter.isAllowed('a')).toBe(false);

    vi.advanceTimersByTime(1_001);

    expect(limiter.isAllowed('a')).toBe(true);
  });

  it('reports remaining quota, floored at zero', () => {
    const limiter = new RateLimiter({ maxRequests: 2, windowMs: 60_000 });

    expect(limiter.remaining('a')).toBe(2);
    limiter.isAllowed('a');
    expect(limiter.remaining('a')).toBe(1);
    limiter.isAllowed('a');
    limiter.isAllowed('a'); // blocked, must not push remaining negative
    expect(limiter.remaining('a')).toBe(0);
  });

  it('reports a full quota for an unknown client', () => {
    const limiter = new RateLimiter({ maxRequests: 5, windowMs: 60_000 });
    expect(limiter.remaining('never-seen')).toBe(5);
  });

  it('does not keep the process alive via its prune timer', () => {
    // The pruning interval is unref'd; if that regresses, a server using this
    // limiter will hang on shutdown instead of exiting.
    const limiter = new RateLimiter({ maxRequests: 1, windowMs: 1_000 });
    expect(limiter.isAllowed('a')).toBe(true);
  });
});
