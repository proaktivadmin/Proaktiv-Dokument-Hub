/**
 * Merge Fields API Client
 */

import axios from "axios";
import type {
  MergeField,
  MergeFieldCreate,
  MergeFieldUpdate,
  MergeFieldListResponse,
  MergeFieldDiscoveryResult,
  MergeFieldDataType,
} from "@/types/v2";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: `${API_BASE_URL}/api`,
});

export interface MergeFieldListParams {
  category?: string;
  search?: string;
  data_type?: MergeFieldDataType;
  is_iterable?: boolean;
  page?: number;
  per_page?: number;
}

export const mergeFieldsApi = {
  /**
   * List merge fields with optional filters
   */
  async list(params?: MergeFieldListParams): Promise<MergeFieldListResponse> {
    const { data } = await api.get<MergeFieldListResponse>("/merge-fields", {
      params,
    });
    return data;
  },

  /**
   * Get a single merge field by ID
   */
  async get(fieldId: string): Promise<MergeField> {
    const { data } = await api.get<MergeField>(`/merge-fields/${fieldId}`);
    return data;
  },

  /**
   * Create a new merge field
   */
  async create(payload: MergeFieldCreate): Promise<MergeField> {
    const { data } = await api.post<MergeField>("/merge-fields", payload);
    return data;
  },

  /**
   * Update a merge field
   */
  async update(fieldId: string, payload: MergeFieldUpdate): Promise<MergeField> {
    const { data } = await api.put<MergeField>(`/merge-fields/${fieldId}`, payload);
    return data;
  },

  /**
   * Delete a merge field
   */
  async delete(fieldId: string): Promise<void> {
    await api.delete(`/merge-fields/${fieldId}`);
  },

  /**
   * Get list of categories
   */
  async getCategories(): Promise<string[]> {
    const { data } = await api.get<{ categories: string[] }>("/merge-fields/categories");
    return data.categories;
  },

  /**
   * Search for autocomplete suggestions
   */
  async autocomplete(query: string, limit: number = 10): Promise<MergeField[]> {
    const { data } = await api.get<MergeField[]>("/merge-fields/autocomplete", {
      params: { q: query, limit },
    });
    return data;
  },

  /**
   * Trigger merge field discovery scan
   */
  async scan(createMissing: boolean = true): Promise<MergeFieldDiscoveryResult> {
    const { data } = await api.post<MergeFieldDiscoveryResult>("/merge-fields/scan", null, {
      params: { create_missing: createMissing },
    });
    return data;
  },
};
