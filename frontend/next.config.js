/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  
  // API proxy rewrites - allows runtime BACKEND_URL configuration
  // Works with both Railway (production) and localhost (development)
  async rewrites() {
    const backendUrl =
      process.env.BACKEND_URL ||
      process.env.NEXT_PUBLIC_API_URL ||
      (process.env.NODE_ENV === "production"
        ? "https://proaktiv-dokument-hub-production.up.railway.app"
        : "http://localhost:8000");

    const normalizedBackendUrl = backendUrl.replace(/\/+$/, "");
    return [
      {
        source: '/api/:path*',
        destination: `${normalizedBackendUrl}/api/:path*`,
      },
    ];
  },
  
  // Note: Azure Blob Storage patterns removed.
  // Template content is now stored in the database and served via API.
};

module.exports = nextConfig;
