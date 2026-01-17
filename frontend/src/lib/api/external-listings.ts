/**
 * External Listings API Client
 */

import { apiClient } from './config';
import type { 
  ExternalListing,
  ExternalListingCreatePayload,
  ExternalListingListResponse,
  ListingSource,
  ListingStatus
} from '@/types/v3';

export interface ExternalListingListParams {
  office_id?: string;
  employee_id?: string;
  source?: ListingSource;
  status?: ListingStatus;
  skip?: number;
  limit?: number;
}

export const externalListingsApi = {
  async list(params?: ExternalListingListParams): Promise<ExternalListingListResponse> {
    const searchParams = new URLSearchParams();
    if (params?.office_id) searchParams.set('office_id', params.office_id);
    if (params?.employee_id) searchParams.set('employee_id', params.employee_id);
    if (params?.source) searchParams.set('source', params.source);
    if (params?.status) searchParams.set('status', params.status);
    if (params?.skip) searchParams.set('skip', String(params.skip));
    if (params?.limit) searchParams.set('limit', String(params.limit));
    
    const query = searchParams.toString();
    const response = await apiClient.get(`/external-listings${query ? `?${query}` : ''}`);
    return response.data;
  },

  async get(id: string): Promise<ExternalListing> {
    const response = await apiClient.get(`/external-listings/${id}`);
    return response.data;
  },

  async create(data: ExternalListingCreatePayload): Promise<ExternalListing> {
    const response = await apiClient.post('/external-listings', data);
    return response.data;
  },

  async update(id: string, data: Partial<ExternalListingCreatePayload>): Promise<ExternalListing> {
    const response = await apiClient.put(`/external-listings/${id}`, data);
    return response.data;
  },

  async delete(id: string): Promise<void> {
    await apiClient.delete(`/external-listings/${id}`);
  },

  async verify(id: string, notes?: string): Promise<ExternalListing> {
    const response = await apiClient.post(`/external-listings/${id}/verify`, { notes });
    return response.data;
  },

  async markNeedsUpdate(id: string, notes?: string): Promise<ExternalListing> {
    const response = await apiClient.post(`/external-listings/${id}/needs-update`, { notes });
    return response.data;
  },

  // Stats
  async getStats(): Promise<{
    total: number;
    by_source: Record<ListingSource, number>;
    by_status: Record<ListingStatus, number>;
    needs_attention: number;
  }> {
    const response = await apiClient.get('/external-listings/stats');
    return response.data;
  },

  async getNeedingAttention(): Promise<{
    count: number;
    listings: ExternalListing[];
  }> {
    const response = await apiClient.get('/external-listings/needs-attention');
    return response.data;
  },
};
