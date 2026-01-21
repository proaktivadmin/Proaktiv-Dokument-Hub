/**
 * API Configuration
 * 
 * Handles dynamic API URL detection for both development and production.
 * 
 * Supports:
 * - Local development (localhost:3000 → localhost:8000 via Next.js rewrites)
 * - Railway (relative URLs, Next.js rewrites to BACKEND_URL)
 */

import axios, { AxiosInstance } from 'axios';

function normalizeBaseUrl(url: string): string {
  return url.replace(/\/+$/, "");
}

/**
 * Get the API base URL based on the environment.
 * 
 * Priority:
 * 1. NEXT_PUBLIC_API_URL environment variable (if set)
 * 2. Check if we're on the client side and use window.location
 * 3. Empty string (use relative URLs with Next.js rewrites)
 */
export function getApiBaseUrl(): string {
  // If explicitly set, use it
  if (process.env.NEXT_PUBLIC_API_URL) {
    return normalizeBaseUrl(process.env.NEXT_PUBLIC_API_URL);
  }
  
  // On client side, check if we're on Railway production
  if (typeof window !== 'undefined') {
    const hostname = window.location.hostname;
    
    // If on Railway frontend domain, use direct backend URL
    if (hostname.includes('blissful-quietude') || hostname.includes('railway.app')) {
      return 'https://proaktiv-dokument-hub-production.up.railway.app';
    }
  }
  
  // Default: use relative URLs (works with Next.js rewrites for localhost)
  return "";
}

/**
 * Resolve stored DB URLs like `/api/...` to the real backend base URL when needed.
 *
 * This avoids Next.js proxying to `http://localhost:8000` in production when BACKEND_URL
 * isn't set, and makes avatars/banner images work reliably on Railway.
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
