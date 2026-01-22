const { withSentryConfig } = require("@sentry/nextjs");

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

// Wrap with Sentry only if DSN is configured
const sentryConfig = {
  // For all available options, see:
  // https://github.com/getsentry/sentry-webpack-plugin#options

  // Suppress source map uploading logs during build
  silent: !process.env.CI,

  // Upload source maps to Sentry for better stack traces
  // Requires SENTRY_AUTH_TOKEN environment variable
  org: process.env.SENTRY_ORG,
  project: process.env.SENTRY_PROJECT,

  // Automatically tree-shake Sentry logger statements to reduce bundle size
  disableLogger: true,

  // Hides source maps from generated client bundles
  hideSourceMaps: true,

  // Automatically instrument React components (recommended)
  reactComponentAnnotation: {
    enabled: true,
  },

  // Route browser requests to Sentry through a Next.js rewrite to circumvent ad-blockers
  // This can increase your server load as well as your hosting bill
  // Note: Check that the configured route will not match with your Next.js middleware
  tunnelRoute: "/monitoring",

  // Disable Sentry webpack plugin if no auth token (for local dev without Sentry)
  automaticVercelMonitors: false,
};

module.exports = process.env.NEXT_PUBLIC_SENTRY_DSN
  ? withSentryConfig(nextConfig, sentryConfig)
  : nextConfig;
