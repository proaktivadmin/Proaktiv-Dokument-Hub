/**
 * Template Settings API Client
 * Handles content editing and settings persistence
 */

import axios from 'axios';
import type {
  SaveTemplateContentRequest,
  SaveTemplateContentResponse,
  UpdateTemplateSettingsRequest,
  UpdateTemplateSettingsResponse,
  GenerateThumbnailResponse,
} from '@/types/v2';
import { getApiBaseUrl } from './config';

const api = axios.create({
  baseURL: `${getApiBaseUrl()}/api`,
});

export const templateSettingsApi = {
  /**
   * Save template HTML content
   * Creates a version snapshot before saving
   */
  async saveContent(
    templateId: string,
    payload: SaveTemplateContentRequest
  ): Promise<SaveTemplateContentResponse> {
    const { data } = await api.put<SaveTemplateContentResponse>(
      `/templates/${templateId}/content`,
      payload
    );
    return data;
  },

  /**
   * Update template settings (Vitec metadata)
   */
  async updateSettings(
    templateId: string,
    payload: UpdateTemplateSettingsRequest
  ): Promise<UpdateTemplateSettingsResponse> {
    const { data } = await api.put<UpdateTemplateSettingsResponse>(
      `/templates/${templateId}/settings`,
      payload
    );
    return data;
  },

  /**
   * Get template settings
   */
  async getSettings(templateId: string): Promise<UpdateTemplateSettingsResponse> {
    const { data } = await api.get<UpdateTemplateSettingsResponse>(
      `/templates/${templateId}/settings`
    );
    return data;
  },

  /**
   * Generate static thumbnail for template
   * Returns 501 if Playwright not installed
   */
  async generateThumbnail(templateId: string): Promise<GenerateThumbnailResponse> {
    const { data } = await api.post<GenerateThumbnailResponse>(
      `/templates/${templateId}/thumbnail`
    );
    return data;
  },
};
