/**
 * API Configuration
 * 
 * Handles dynamic API URL detection for both development and production.
 */

/**
 * Get the API base URL based on the environment.
 * - In development (localhost): use relative URLs (Next.js rewrites)
 * - In production (Azure): call the backend API directly
 */
export function getApiBaseUrl(): string {
  // If explicitly set, use it
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL;
  }
  
  // Client-side detection for Azure Container Apps
  if (typeof window !== 'undefined') {
    const hostname = window.location.hostname;
    
    // Azure Container Apps pattern: dokumenthub-web.*.azurecontainerapps.io
    if (hostname.includes('azurecontainerapps.io')) {
      // Replace 'web' with 'api' in the hostname
      const apiHostname = hostname.replace('dokumenthub-web', 'dokumenthub-api');
      return `https://${apiHostname}`;
    }
  }
  
  // Default: use relative URLs (for localhost with Next.js rewrites)
  return "";
}

// Cached value for the API base URL
let cachedApiBaseUrl: string | null = null;

/**
 * Get the API base URL with caching
 */
export function getCachedApiBaseUrl(): string {
  if (cachedApiBaseUrl === null) {
    cachedApiBaseUrl = getApiBaseUrl();
  }
  return cachedApiBaseUrl;
}
