/** @type {import('next').NextConfig} */
const useStandalone = process.env.NEXT_OUTPUT_STANDALONE === '1'

const nextConfig = {
  // Usa standalone somente quando explicitamente solicitado (ex.: build de container).
  output: useStandalone ? 'standalone' : undefined,
  images: {
    unoptimized: true,
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
  },
}

module.exports = nextConfig
