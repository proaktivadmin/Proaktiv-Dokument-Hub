/**
 * Auth API Client
 *
 * Handles authentication with the backend.
 * Uses relative URLs (/api/*) so Vercel rewrites them to Railway,
 * making session cookies first-party (same origin).
 */

import axios from "axios";

const authClient = axios.create({
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
  },
});

export interface AuthStatus {
  authenticated: boolean;
  email?: string;
  expires_at?: string;
}

export interface AuthCheckResponse {
  authenticated: boolean;
  auth_required: boolean;
  email?: string;
}

export interface LoginResponse {
  success: boolean;
  message: string;
  expires_at: string;
}

export const authApi = {
  /**
   * Log in with email + password
   */
  async login(email: string, password: string): Promise<LoginResponse> {
    const { data } = await authClient.post<LoginResponse>("/api/auth/login", {
      email,
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
   * Get authentication status (includes email of the logged-in user)
   */
  async getStatus(): Promise<AuthStatus> {
    const { data } = await authClient.get<AuthStatus>("/api/auth/status");
    return data;
  },

  /**
   * Quick auth check — returns true if authenticated (doesn't throw)
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
