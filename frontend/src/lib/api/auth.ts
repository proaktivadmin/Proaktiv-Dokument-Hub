/**
 * Auth API Client
 * 
 * Handles authentication with the backend.
 * Always uses the full backend URL for cross-origin cookie handling.
 */

import axios from "axios";
import { getApiBaseUrl } from "./config";

// Railway backend URL - must use full URL for cross-origin cookies
const BACKEND_URL = "https://proaktiv-dokument-hub-production.up.railway.app";

// Create axios instance with credentials enabled
const authClient = axios.create({
  withCredentials: true, // Required for cookies
  headers: {
    "Content-Type": "application/json",
  },
});

// Add request interceptor to set base URL dynamically
// For auth, we ALWAYS use the full backend URL to ensure cookies work cross-origin
authClient.interceptors.request.use((config) => {
  if (config.url && !config.url.startsWith('http')) {
    // Use getApiBaseUrl for local dev, hardcoded for production reliability
    const baseUrl = typeof window !== 'undefined' && window.location.hostname === 'localhost'
      ? getApiBaseUrl()
      : BACKEND_URL;
    config.url = `${baseUrl}${config.url}`;
  }
  return config;
});

export interface AuthStatus {
  authenticated: boolean;
  expires_at?: string;
}

export interface AuthCheckResponse {
  authenticated: boolean;
  auth_required: boolean;
}

export interface LoginResponse {
  success: boolean;
  message: string;
  expires_at: string;
}

export const authApi = {
  /**
   * Log in with password
   */
  async login(password: string): Promise<LoginResponse> {
    const { data } = await authClient.post<LoginResponse>("/api/auth/login", {
      password,
    });
    return data;
  },

  /**
   * Log out
   */
  async logout(): Promise<void> {
    await authClient.post("/api/auth/logout");
  },

  /**
   * Get authentication status
   */
  async getStatus(): Promise<AuthStatus> {
    const { data } = await authClient.get<AuthStatus>("/api/auth/status");
    return data;
  },

  /**
   * Quick auth check - returns true if authenticated
   * Returns false if not authenticated (doesn't throw)
   */
  async check(): Promise<AuthCheckResponse> {
    try {
      const { data } = await authClient.get<AuthCheckResponse>("/api/auth/check");
      return data;
    } catch {
      return { authenticated: false, auth_required: true };
    }
  },
};
