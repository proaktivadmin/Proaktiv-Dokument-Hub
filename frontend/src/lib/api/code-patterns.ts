/**
 * Code Patterns API Client
 */

import axios from "axios";
import type {
  CodePattern,
  CodePatternCreate,
  CodePatternUpdate,
  CodePatternListResponse,
} from "@/types/v2";
import { getApiBaseUrl } from "./config";

const api = axios.create({
  baseURL: `${getApiBaseUrl()}/api`,
});

export interface CodePatternListParams {
  category?: string;
  search?: string;
  page?: number;
  per_page?: number;
}

export const codePatternsApi = {
  /**
   * List code patterns with optional filters
   */
  async list(params?: CodePatternListParams): Promise<CodePatternListResponse> {
    const { data } = await api.get<CodePatternListResponse>("/code-patterns", {
      params,
    });
    return data;
  },

  /**
   * Get a single code pattern by ID
   */
  async get(patternId: string): Promise<CodePattern> {
    const { data } = await api.get<CodePattern>(`/code-patterns/${patternId}`);
    return data;
  },

  /**
   * Create a new code pattern
   */
  async create(payload: CodePatternCreate): Promise<CodePattern> {
    const { data } = await api.post<CodePattern>("/code-patterns", payload);
    return data;
  },

  /**
   * Update a code pattern
   */
  async update(patternId: string, payload: CodePatternUpdate): Promise<CodePattern> {
    const { data } = await api.put<CodePattern>(`/code-patterns/${patternId}`, payload);
    return data;
  },

  /**
   * Delete a code pattern
   */
  async delete(patternId: string): Promise<void> {
    await api.delete(`/code-patterns/${patternId}`);
  },

  /**
   * Get list of categories
   */
  async getCategories(): Promise<string[]> {
    const { data } = await api.get<{ categories: string[] }>("/code-patterns/categories");
    return data.categories;
  },

  /**
   * Increment usage count
   */
  async incrementUsage(patternId: string): Promise<void> {
    await api.post(`/code-patterns/${patternId}/increment-usage`);
  },
};
