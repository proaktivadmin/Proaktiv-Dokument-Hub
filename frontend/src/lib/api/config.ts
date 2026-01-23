/**
 * API Configuration
 * 
 * Handles dynamic API URL detection for both development and production.
 * 
 * Supports:
 * - Local development (localhost:3000 → localhost:8000 via Next.js rewrites)
 * - Vercel production (vercel.json rewrites to Railway backend)
 */

import axios, { AxiosInstance } from 'axios';

function normalizeBaseUrl(url: string): string {
  return url.replace(/\/+$/, "");
}

/**
 * Get the API base URL based on the environment.
 * 
 * IMPORTANT: We use relative URLs (empty base) so that:
 * - All API requests go through Vercel's rewrite proxy (/api/* → Railway)
 * - Session cookies remain first-party (same origin as frontend)
 * - Third-party cookie blocking doesn't break authentication
 * 
 * Priority:
 * 1. NEXT_PUBLIC_API_URL environment variable (if set for special cases)
 * 2. Empty string (use relative URLs with Next.js/Vercel rewrites)
 */
export function getApiBaseUrl(): string {
  // If explicitly set, use it (for special debugging/testing scenarios)
  if (process.env.NEXT_PUBLIC_API_URL) {
    return normalizeBaseUrl(process.env.NEXT_PUBLIC_API_URL);
  }
  
  // Always use relative URLs - Vercel/Next.js rewrites handle routing to Railway
  // This keeps cookies first-party and avoids third-party cookie blocking
  return "";
}

/**
 * Resolve stored DB URLs like `/api/...` to the real backend base URL when needed.
 *
 * This avoids Next.js proxying to `http://localhost:8000` in production when BACKEND_URL
 * isn't set, and makes avatars/banner images work reliably.
 */
export function resolveApiUrl(url: string | null | undefined): string | undefined {
  if (!url) return undefined;
  if (/^https?:\/\//i.test(url) || url.startsWith("data:") || url.startsWith("blob:")) {
    return url;
  }

  // Only rewrite our API proxy paths; leave other relative URLs untouched
  if (url.startsWith("/api/") || url === "/api") {
    const baseUrl = getApiBaseUrl();
    if (baseUrl) return `${baseUrl}${url}`;
  }

  return url;
}

/**
 * Resolve an image URL with optional resizing for avatars.
 * 
 * When the URL is a Vitec picture endpoint, appends size and crop parameters
 * to get a properly cropped square image.
 * 
 * @param url - The image URL (e.g., /api/vitec/employees/ABCD/picture)
 * @param size - Desired square size in pixels (e.g., 64, 128, 256)
 * @param crop - Crop mode: "top" for portraits, "center" for general
 */
export function resolveAvatarUrl(
  url: string | null | undefined,
  size: number = 128,
  crop: "top" | "center" = "top"
): string | undefined {
  const resolved = resolveApiUrl(url);
  if (!resolved) return undefined;

  // Only add params to Vitec picture endpoints
  if (resolved.includes("/vitec/employees/") && resolved.includes("/picture")) {
    const separator = resolved.includes("?") ? "&" : "?";
    return `${resolved}${separator}size=${size}&crop=${crop}`;
  }

  return resolved;
}

/**
 * Create an axios instance with dynamic base URL support.
 * Uses a request interceptor to set the correct base URL on each request,
 * which is necessary because the module loads during SSR when window is undefined.
 */
export function createApiClient(): AxiosInstance {
  const api = axios.create({
    withCredentials: true, // Required for auth cookies
  });
  
  // Add request interceptor to set base URL dynamically
  api.interceptors.request.use((config) => {
    // Get the current base URL (will be correct on client-side)
    const baseUrl = getApiBaseUrl();
    
    // Only modify if URL doesn't already have a host
    if (config.url && !config.url.startsWith('http')) {
      // Ensure URL starts with /api
      const apiPath = config.url.startsWith('/api') ? config.url : `/api${config.url.startsWith('/') ? '' : '/'}${config.url}`;
      config.url = `${baseUrl}${apiPath}`;
    }
    
    return config;
  });
  
  return api;
}

// Shared API client instance with dynamic URL support
export const apiClient = createApiClient();
