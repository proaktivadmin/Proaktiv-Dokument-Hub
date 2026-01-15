/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  
  // API proxy rewrites - allows runtime BACKEND_URL configuration
  // This eliminates the need for NEXT_PUBLIC_API_URL at build time
  async rewrites() {
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';
    return [
      {
        source: '/api/:path*',
        destination: `${backendUrl}/api/:path*`,
      },
    ];
  },
  
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '*.blob.core.windows.net',
      },
    ],
  },
};

module.exports = nextConfig;
