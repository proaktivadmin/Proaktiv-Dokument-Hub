/**
 * Dashboard API Client
 * Fetches real-time statistics from backend
 */

import type { DashboardStatsV2 } from '@/types/v2';
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
};
