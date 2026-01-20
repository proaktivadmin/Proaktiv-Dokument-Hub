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
 * Picture sync response
 */
export interface SyncPicturesResponse {
  total: number;
  synced: number;
  failed: number;
  skipped: number;
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

  /**
   * Sync office banner pictures from Vitec Hub
   * 
   * Fetches and stores banner images for all offices with vitec_department_id.
   */
  async syncOfficePictures(): Promise<SyncPicturesResponse> {
    const response = await apiClient.post<SyncPicturesResponse>('/vitec/sync-office-pictures');
    return response.data;
  },

  /**
   * Sync employee profile pictures from Vitec Hub
   * 
   * Fetches and stores profile images for all employees with vitec_employee_id.
   */
  async syncEmployeePictures(): Promise<SyncPicturesResponse> {
    const response = await apiClient.post<SyncPicturesResponse>('/vitec/sync-employee-pictures');
    return response.data;
  },
};
