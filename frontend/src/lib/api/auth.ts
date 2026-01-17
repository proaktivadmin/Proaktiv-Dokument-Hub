/**
 * Auth API Client
 * 
 * Handles authentication with the backend.
 */

import axios from "axios";
import { getApiBaseUrl } from "./config";

// Create axios instance with credentials enabled
const authClient = axios.create({
  withCredentials: true, // Required for cookies
  headers: {
    "Content-Type": "application/json",
  },
});

// Add request interceptor to set base URL dynamically (same pattern as main API)
authClient.interceptors.request.use((config) => {
  const baseUrl = getApiBaseUrl();
  if (config.url && !config.url.startsWith('http')) {
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
