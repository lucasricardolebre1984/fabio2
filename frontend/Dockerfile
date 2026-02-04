FROM node:20-alpine AS builder

WORKDIR /app

# Copy config files
COPY package*.json tsconfig.json next.config.js tailwind.config.ts components.json postcss.config.js ./
COPY src ./src

# Create public folder if it doesn't exist (Next.js requires it)
RUN mkdir -p ./public

# Install ALL dependencies (including devDependencies for build)
RUN npm ci

# Build the application
RUN npm run build

# Production stage
FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install only production dependencies
RUN npm ci --only=production

# Copy built application from builder stage
COPY --from=builder /app/.next ./.next

# Create public folder in production
RUN mkdir -p ./public

# Expose port
EXPOSE 3000

# Start the application
CMD ["node", ".next/standalone/server.js"]
