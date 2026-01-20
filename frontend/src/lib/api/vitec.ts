/**
 * Vitec API Client
 * 
 * Handles Vitec Hub connection status and sync triggers.
 */

import { apiClient } from './config';

/**
 * Vitec API connection status response
 */
export interface VitecStatus {
  configured: boolean;
  connected: boolean;
  installation_id: string | null;
  error: string | null;
  available_methods: string[] | null;
}

/**
 * Vitec API client for connection status and management
 */
export const vitecApi = {
  /**
   * Get Vitec Hub API connection status
   * 
   * Checks if credentials are configured and if the API is reachable.
   * Does not require installation ID - just tests authentication.
   */
  async getStatus(): Promise<VitecStatus> {
    const response = await apiClient.get<VitecStatus>('/vitec/status');
    return response.data;
  },
};
