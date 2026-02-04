/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    unoptimized: true,
  },
  env: {
    NEXT_PUBLIC_API_URL: 'http://localhost:8000/api/v1',
  },
}

module.exports = nextConfig
