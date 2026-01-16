/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  
  // API proxy rewrites - allows runtime BACKEND_URL configuration
  // Works with both Railway (production) and localhost (development)
  async rewrites() {
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';
    return [
      {
        source: '/api/:path*',
        destination: `${backendUrl}/api/:path*`,
      },
    ];
  },
  
  // Note: Azure Blob Storage patterns removed.
  // Template content is now stored in the database and served via API.
};

module.exports = nextConfig;
