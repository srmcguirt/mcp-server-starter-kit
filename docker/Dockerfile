# MCP Server Starter Kit — Production Dockerfile
# Multi-stage build: build → production (minimal image)

# ─── Stage 1: Build ──────────────────────────────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app

# Install dependencies first (cache layer)
COPY package*.json ./
RUN npm ci

# Copy source and build
COPY tsconfig.json ./
COPY src/ ./src/
RUN npm run build

# Prune dev dependencies
RUN npm ci --omit=dev

# ─── Stage 2: Production ─────────────────────────────────────────────────────
FROM node:20-alpine AS production

# Security: run as non-root
RUN addgroup -g 1001 -S mcp && adduser -u 1001 -S mcp -G mcp
USER mcp

WORKDIR /app

# Copy only what's needed
COPY --from=builder --chown=mcp:mcp /app/dist ./dist
COPY --from=builder --chown=mcp:mcp /app/node_modules ./node_modules
COPY --from=builder --chown=mcp:mcp /app/package.json ./

ENV NODE_ENV=production

# MCP servers communicate via stdio — no port needed for local use
# Expose a healthcheck port if you add an HTTP health endpoint
# EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD node -e "require('./dist/index.js')" || exit 1

CMD ["node", "dist/index.js"]
