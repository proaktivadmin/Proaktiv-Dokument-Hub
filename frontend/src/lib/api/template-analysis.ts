/**
 * Template Analysis API Client
 */

import type { TemplateAnalysisResult } from "@/types/v2";
import { apiClient } from "./config";

const api = apiClient;

export const templateAnalysisApi = {
  /**
   * Analyze a template for merge fields, conditions, and loops
   */
  async analyze(templateId: string): Promise<TemplateAnalysisResult> {
    const { data } = await api.get<TemplateAnalysisResult>(
      `/templates/${templateId}/analyze`
    );
    return data;
  },
};
