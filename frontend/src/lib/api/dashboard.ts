/**
 * Dashboard API Client
 * Fetches real-time statistics from backend
 */

import axios from 'axios';
import type { DashboardStatsV2 } from '@/types/v2';
import { getApiBaseUrl } from './config';

const api = axios.create({
  baseURL: `${getApiBaseUrl()}/api`,
});

export const dashboardApi = {
  /**
   * Get dashboard statistics
   */
  async getStats(): Promise<DashboardStatsV2> {
    const { data } = await api.get<DashboardStatsV2>('/dashboard/stats');
    return data;
  },
};
