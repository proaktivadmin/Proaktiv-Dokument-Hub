/**
 * Company Assets API Client
 */

import { apiClient } from './config';
import type { 
  CompanyAsset, 
  CompanyAssetListResponse,
  AssetUploadPayload,
  AssetCategory,
  AssetMetadata 
} from '@/types/v3';

export interface AssetListParams {
  category?: AssetCategory;
  office_id?: string;
  employee_id?: string;
  is_global?: boolean;
  skip?: number;
  limit?: number;
}

export const assetsApi = {
  async list(params?: AssetListParams): Promise<CompanyAssetListResponse> {
    const searchParams = new URLSearchParams();
    if (params?.category) searchParams.set('category', params.category);
    if (params?.office_id) searchParams.set('office_id', params.office_id);
    if (params?.employee_id) searchParams.set('employee_id', params.employee_id);
    if (params?.is_global !== undefined) {
      searchParams.set('is_global', String(params.is_global));
    }
    if (params?.skip) searchParams.set('skip', String(params.skip));
    if (params?.limit) searchParams.set('limit', String(params.limit));
    
    const query = searchParams.toString();
    const response = await apiClient.get(`/assets${query ? `?${query}` : ''}`);
    return response.data;
  },

  async get(id: string): Promise<CompanyAsset> {
    const response = await apiClient.get(`/assets/${id}`);
    return response.data;
  },

  async upload(payload: AssetUploadPayload): Promise<CompanyAsset> {
    const formData = new FormData();
    formData.append('file', payload.file);
    formData.append('name', payload.name);
    formData.append('category', payload.category);
    if (payload.office_id) formData.append('office_id', payload.office_id);
    if (payload.employee_id) formData.append('employee_id', payload.employee_id);
    if (payload.is_global !== undefined) {
      formData.append('is_global', String(payload.is_global));
    }
    if (payload.alt_text) formData.append('alt_text', payload.alt_text);
    if (payload.usage_notes) formData.append('usage_notes', payload.usage_notes);

    const response = await apiClient.post('/assets/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  async download(id: string): Promise<Blob> {
    const response = await apiClient.get(`/assets/${id}/download`, {
      responseType: 'blob',
    });
    return response.data;
  },

  async updateMetadata(id: string, metadata: AssetMetadata): Promise<CompanyAsset> {
    const response = await apiClient.put(`/assets/${id}`, { metadata });
    return response.data;
  },

  async delete(id: string): Promise<void> {
    await apiClient.delete(`/assets/${id}`);
  },

  getDownloadUrl(id: string): string {
    return `/api/assets/${id}/download`;
  },

  getThumbnailUrl(id: string): string {
    return `/api/assets/${id}/thumbnail`;
  },
};
