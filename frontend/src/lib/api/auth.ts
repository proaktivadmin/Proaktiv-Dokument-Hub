/**
 * Auth API Client
 * 
 * Handles authentication with the backend.
 */

import axios from "axios";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Create axios instance with credentials enabled
const authClient = axios.create({
  baseURL: API_BASE_URL,
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
