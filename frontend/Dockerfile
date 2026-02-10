# 1. Start with a base image containing Node.js installed
# Using alpine version for smaller image size
FROM node:20-alpine AS builder

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy package.json and package-lock.json first to leverage Docker cache
# This ensures that we don't re-install dependencies if only source code changes
COPY package.json package-lock.json ./

# 4. Install dependencies defined in package-lock.json
RUN npm ci

# 5. Copy the rest of the application source code
COPY . .

# 6. Build the Next.js application for production
RUN npm run build

# 7. Start a new stage for the production image to keep it small
FROM node:20-alpine AS runner

# 8. Set working directory for the runner stage
WORKDIR /app

# 9. Set NODE_ENV to production for optimization
ENV NODE_ENV=production

# 10. Create a non-root user for security
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# 11. Copy public assets from the builder stage
COPY --from=builder /app/public ./public

# 12. Copy the built application (standalone output) from the builder stage
# Automatically leverage output traces to reduce image size
# https://nextjs.org/docs/advanced-features/output-file-tracing
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

# 13. Switch to the non-root user
USER nextjs

# 14. Expose the port the app runs on
EXPOSE 3000

# 15. Set environment variables for the server
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# 16. Command to start the application
CMD ["node", "server.js"]
