/**
 * Dashboard API Client
 * Fetches real-time statistics from backend
 */

import type { DashboardStatsV2, InventoryStatsResponse } from '@/types/v2';
import { apiClient } from './config';

const api = apiClient;

export const dashboardApi = {
  /**
   * Get dashboard statistics
   */
  async getStats(): Promise<DashboardStatsV2> {
    const { data } = await api.get<DashboardStatsV2>('/dashboard/stats');
    return data;
  },

  /**
   * Get inventory sync statistics
   */
  async getInventoryStats(missingLimit: number = 5): Promise<InventoryStatsResponse> {
    const { data } = await api.get<InventoryStatsResponse>('/dashboard/inventory', {
      params: { missing_limit: missingLimit }
    });
    return data;
  },
};
