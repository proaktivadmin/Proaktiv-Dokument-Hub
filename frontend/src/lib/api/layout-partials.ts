/**
 * Layout Partials API Client
 */

import axios from "axios";
import type {
  LayoutPartial,
  LayoutPartialCreate,
  LayoutPartialUpdate,
  LayoutPartialListResponse,
  LayoutPartialSetDefaultResponse,
  LayoutPartialType,
  LayoutPartialContext,
} from "@/types/v2";
import { getApiBaseUrl } from "./config";

const api = axios.create({
  baseURL: `${getApiBaseUrl()}/api`,
});

export interface LayoutPartialListParams {
  type?: LayoutPartialType;
  context?: LayoutPartialContext;
}

export const layoutPartialsApi = {
  /**
   * List layout partials with optional filters
   */
  async list(params?: LayoutPartialListParams): Promise<LayoutPartialListResponse> {
    const { data } = await api.get<LayoutPartialListResponse>("/layout-partials", {
      params,
    });
    return data;
  },

  /**
   * Get a single layout partial by ID
   */
  async get(partialId: string): Promise<LayoutPartial> {
    const { data } = await api.get<LayoutPartial>(`/layout-partials/${partialId}`);
    return data;
  },

  /**
   * Get the default partial for a type/context
   */
  async getDefault(
    type: LayoutPartialType,
    context: LayoutPartialContext = "all"
  ): Promise<LayoutPartial | null> {
    try {
      const { data } = await api.get<LayoutPartial>("/layout-partials/default", {
        params: { type, context },
      });
      return data;
    } catch (error) {
      // 404 means no default is set
      if (axios.isAxiosError(error) && error.response?.status === 404) {
        return null;
      }
      throw error;
    }
  },

  /**
   * Create a new layout partial
   */
  async create(payload: LayoutPartialCreate): Promise<LayoutPartial> {
    const { data } = await api.post<LayoutPartial>("/layout-partials", payload);
    return data;
  },

  /**
   * Update a layout partial
   */
  async update(partialId: string, payload: LayoutPartialUpdate): Promise<LayoutPartial> {
    const { data } = await api.put<LayoutPartial>(`/layout-partials/${partialId}`, payload);
    return data;
  },

  /**
   * Delete a layout partial
   */
  async delete(partialId: string): Promise<void> {
    await api.delete(`/layout-partials/${partialId}`);
  },

  /**
   * Set a partial as the default for its type/context
   */
  async setDefault(partialId: string): Promise<LayoutPartialSetDefaultResponse> {
    const { data } = await api.post<LayoutPartialSetDefaultResponse>(
      `/layout-partials/${partialId}/set-default`
    );
    return data;
  },
};
