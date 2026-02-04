/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  images: {
    unoptimized: true,
  },
  env: {
    NEXT_PUBLIC_API_URL: 'http://56.124.101.16:8000/api/v1',
  },
}

module.exports = nextConfig
