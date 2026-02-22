const { withSentryConfig } = require("@sentry/nextjs");

const isDev = process.env.NODE_ENV === 'development';

// Backend URL for CSP connect-src directive
// In production, this is the Railway backend; in dev, localhost
// Normalize to remove trailing slashes for consistent CSP formatting
// Note: Frontend is on Vercel, backend remains on Railway
const backendUrl = (process.env.BACKEND_URL 
  || process.env.NEXT_PUBLIC_API_URL 
  || (isDev ? 'http://localhost:8000' : 'https://proaktiv-admin.up.railway.app')
).replace(/\/+$/, '');

/**
 * Content Security Policy
 * Protects against XSS, clickjacking, and other code injection attacks.
 * 
 * IMPORTANT: For Vercel deployments, vercel.json defines its own CSP headers.
 * Keep both CSPs synchronized! The vercel.json CSP is static and must match
 * the production version of this CSP (isDev=false).
 * 
 * @see https://nextjs.org/docs/app/guides/content-security-policy
 * @see frontend/vercel.json - headers section for Vercel-specific CSP
 */
const cspHeader = `
  default-src 'self';
  script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://cdn.ckeditor.com;
  style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net;
  img-src 'self' blob: data: https://proaktiv.no https://*.proaktiv.no https://*.sentry.io https://*.openstreetmap.org;
  font-src 'self' data: https://cdn.jsdelivr.net;
  worker-src 'self' blob:;
  connect-src 'self' ${backendUrl} https://*.sentry.io https://*.ingest.sentry.io wss://*.sentry.io https://cdn.jsdelivr.net ${isDev ? 'ws://localhost:* http://localhost:*' : ''};
  frame-ancestors 'none';
  base-uri 'self';
  form-action 'self';
  object-src 'none';
  ${isDev ? '' : 'upgrade-insecure-requests;'}
`.replace(/\s{2,}/g, ' ').trim();

/** @type {import('next').NextConfig} */
const nextConfig = {
  // Vercel automatically handles output mode; standalone only needed for local Docker
  // Disabled on Windows due to EINVAL error with colons in chunk filenames (node:inspector)
  ...(process.env.VERCEL || process.platform === 'win32' ? {} : { output: 'standalone' }),
  
  // API proxy rewrites - only used for local development
  // Vercel uses vercel.json rewrites for production
  ...(process.env.VERCEL
    ? {}
    : {
        async rewrites() {
          const backendUrl =
            process.env.BACKEND_URL ||
            process.env.NEXT_PUBLIC_API_URL ||
            (process.env.NODE_ENV === "production"
              ? "https://proaktiv-admin.up.railway.app"
              : "http://localhost:8000");

          const normalizedBackendUrl = backendUrl.replace(/\/+$/, "");
          return [
            {
              source: '/api/:path*',
              destination: `${normalizedBackendUrl}/api/:path*`,
            },
          ];
        },
      }),

  /**
   * Security headers
   * @see https://nextjs.org/docs/app/guides/content-security-policy
   */
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'Content-Security-Policy',
            value: cspHeader,
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block',
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin',
          },
          {
            key: 'Permissions-Policy',
            value: 'camera=(), microphone=(), geolocation=()',
          },
        ],
      },
    ];
  },
  
  // Transpile Leaflet which has issues with standard Next.js bundling
  transpilePackages: ['leaflet', 'react-leaflet'],
  
  // Turbopack specific configuration for Leaflet
  turbo: {
    resolveAlias: {
      leaflet: 'leaflet/dist/leaflet-src.js',
    },
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
