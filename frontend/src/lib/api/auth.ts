/**
 * Auth API Client
 * 
 * Handles authentication with the backend.
 * Uses relative URLs (/api/*) so Vercel rewrites them to Railway,
 * making session cookies first-party (same origin).
 */

import axios from "axios";

// Create axios instance with credentials enabled
// Using relative URLs so Vercel's rewrite handles routing to Railway
// This makes cookies first-party, avoiding third-party cookie blocking
const authClient = axios.create({
  withCredentials: true, // Required for cookies
  headers: {
    "Content-Type": "application/json",
  },
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
