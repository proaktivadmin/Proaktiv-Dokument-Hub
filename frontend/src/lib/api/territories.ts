/**
 * Territories API Client
 */

import { apiClient } from './config';
import type { 
  PostalCode,
  OfficeTerritory,
  OfficeTerritoryWithDetails,
  OfficeTerritoryListResponse,
  TerritoryMapData,
  TerritorySource,
  TerritoryImportResult
} from '@/types/v3';

export interface TerritoryListParams {
  office_id?: string;
  source?: TerritorySource;
  is_blacklisted?: boolean;
  skip?: number;
  limit?: number;
}

export const territoriesApi = {
  // Postal Codes
  async listPostalCodes(params?: { skip?: number; limit?: number }): Promise<{ items: PostalCode[]; total: number }> {
    const searchParams = new URLSearchParams();
    if (params?.skip) searchParams.set('skip', String(params.skip));
    if (params?.limit) searchParams.set('limit', String(params.limit));
    
    const query = searchParams.toString();
    const response = await apiClient.get(`/postal-codes${query ? `?${query}` : ''}`);
    return response.data;
  },

  async syncPostalCodes(): Promise<{ synced: number; message: string }> {
    const response = await apiClient.post('/postal-codes/sync');
    return response.data;
  },

  async searchPostalCodes(query: string): Promise<PostalCode[]> {
    const response = await apiClient.get(`/postal-codes/search?q=${encodeURIComponent(query)}`);
    return response.data;
  },

  // Territories
  async list(params?: TerritoryListParams): Promise<OfficeTerritoryListResponse> {
    const searchParams = new URLSearchParams();
    if (params?.office_id) searchParams.set('office_id', params.office_id);
    if (params?.source) searchParams.set('source', params.source);
    if (params?.is_blacklisted !== undefined) {
      searchParams.set('is_blacklisted', String(params.is_blacklisted));
    }
    if (params?.skip) searchParams.set('skip', String(params.skip));
    if (params?.limit) searchParams.set('limit', String(params.limit));
    
    const query = searchParams.toString();
    const response = await apiClient.get(`/territories${query ? `?${query}` : ''}`);
    return response.data;
  },

  async create(data: {
    office_id: string;
    postal_code: string;
    source: TerritorySource;
    priority?: number;
    is_blacklisted?: boolean;
    valid_from?: string;
    valid_to?: string;
  }): Promise<OfficeTerritoryWithDetails> {
    const response = await apiClient.post('/territories', data);
    return response.data;
  },

  async update(id: string, data: Partial<OfficeTerritory>): Promise<OfficeTerritoryWithDetails> {
    const response = await apiClient.put(`/territories/${id}`, data);
    return response.data;
  },

  async delete(id: string): Promise<void> {
    await apiClient.delete(`/territories/${id}`);
  },

  async getMapData(layers?: TerritorySource[]): Promise<TerritoryMapData> {
    const searchParams = new URLSearchParams();
    if (layers?.length) {
      layers.forEach(l => searchParams.append('layer', l));
    }
    
    const query = searchParams.toString();
    const response = await apiClient.get(`/territories/map${query ? `?${query}` : ''}`);
    return response.data;
  },

  async getLayers(): Promise<TerritorySource[]> {
    const response = await apiClient.get('/territories/layers');
    return response.data;
  },

  async importFromCsv(file: File, source: TerritorySource): Promise<TerritoryImportResult> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('source', source);
    
    const response = await apiClient.post('/territories/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  // Blacklist
  async getBlacklist(): Promise<string[]> {
    const response = await apiClient.get('/territories/blacklist');
    return response.data;
  },

  async addToBlacklist(postalCode: string, reason?: string): Promise<void> {
    await apiClient.post('/territories/blacklist', { postal_code: postalCode, reason });
  },

  async removeFromBlacklist(postalCode: string): Promise<void> {
    await apiClient.delete(`/territories/blacklist/${postalCode}`);
  },

  // Stats
  async getStats(): Promise<{
    total_territories: number;
    by_source: Record<TerritorySource, number>;
    offices_with_territories: number;
    blacklisted_count: number;
  }> {
    const response = await apiClient.get('/territories/stats');
    return response.data;
  },
};
