FROM node:20-alpine AS builder

WORKDIR /app

# Copy config and source files required for Next build.
COPY package*.json tsconfig.json next.config.js tailwind.config.ts postcss.config.js ./
COPY src ./src
COPY public ./public

# Install dependencies and force standalone output for container runtime.
RUN npm ci
ARG NEXT_PUBLIC_API_URL=http://127.0.0.1:8000/api/v1
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
ENV NEXT_OUTPUT_STANDALONE=1
RUN npm run build

FROM node:20-alpine AS runner

WORKDIR /app
ENV NODE_ENV=production
ENV PORT=3000
ENV HOSTNAME=0.0.0.0

COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

EXPOSE 3000
CMD ["node", "server.js"]
