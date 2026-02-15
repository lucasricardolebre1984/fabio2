/** @type {import('next').NextConfig} */
const isVercel = Boolean(process.env.VERCEL)

const nextConfig = {
  // Vercel já controla o empacotamento; manter standalone lá pode quebrar trace files no App Router.
  output: isVercel ? undefined : 'standalone',
  images: {
    unoptimized: true,
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
  },
}

module.exports = nextConfig
