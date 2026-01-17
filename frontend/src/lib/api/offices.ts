/**
 * Offices API Client
 */

import { apiClient } from './config';
import type { 
  OfficeWithStats, 
  OfficeCreatePayload, 
  OfficeUpdatePayload,
  OfficeListResponse 
} from '@/types/v3';

export interface OfficeListParams {
  city?: string;
  is_active?: boolean;
  skip?: number;
  limit?: number;
}

export const officesApi = {
  async list(params?: OfficeListParams): Promise<OfficeListResponse> {
    const searchParams = new URLSearchParams();
    if (params?.city) searchParams.set('city', params.city);
    if (params?.is_active !== undefined) {
      searchParams.set('is_active', String(params.is_active));
    }
    if (params?.skip) searchParams.set('skip', String(params.skip));
    if (params?.limit) searchParams.set('limit', String(params.limit));
    
    const query = searchParams.toString();
    const response = await apiClient.get(`/offices${query ? `?${query}` : ''}`);
    return response.data;
  },

  async get(id: string): Promise<OfficeWithStats> {
    const response = await apiClient.get(`/offices/${id}`);
    return response.data;
  },

  async create(data: OfficeCreatePayload): Promise<OfficeWithStats> {
    const response = await apiClient.post('/offices', data);
    return response.data;
  },

  async update(id: string, data: OfficeUpdatePayload): Promise<OfficeWithStats> {
    const response = await apiClient.put(`/offices/${id}`, data);
    return response.data;
  },

  async deactivate(id: string): Promise<OfficeWithStats> {
    const response = await apiClient.delete(`/offices/${id}`);
    return response.data;
  },

  async getStats(id: string): Promise<{
    office_id: string;
    employee_count: number;
    active_employee_count: number;
    territory_count: number;
  }> {
    const response = await apiClient.get(`/offices/${id}/stats`);
    return response.data;
  },
};
