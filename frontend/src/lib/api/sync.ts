/**
 * Sync Review API Client
 */

import { apiClient } from "./config";
import type {
  SyncPreview,
  SyncDecisionUpdatePayload,
  SyncCommitResult,
} from "@/types/v3";

export const syncApi = {
  async createPreview(): Promise<SyncPreview> {
    const response = await apiClient.post("/sync/preview");
    return response.data;
  },

  async getSession(sessionId: string): Promise<SyncPreview> {
    const response = await apiClient.get(`/sync/sessions/${sessionId}`);
    return response.data;
  },

  async updateDecision(
    sessionId: string,
    payload: SyncDecisionUpdatePayload
  ): Promise<{ success: boolean }> {
    const response = await apiClient.patch(
      `/sync/sessions/${sessionId}/decisions`,
      payload
    );
    return response.data;
  },

  async commitSession(sessionId: string): Promise<SyncCommitResult> {
    const response = await apiClient.post(`/sync/sessions/${sessionId}/commit`);
    return response.data;
  },

  async cancelSession(sessionId: string): Promise<{ success: boolean }> {
    const response = await apiClient.delete(`/sync/sessions/${sessionId}`);
    return response.data;
  },
};
