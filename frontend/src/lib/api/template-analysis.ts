/**
 * Template Analysis API Client
 */

import axios from "axios";
import type { TemplateAnalysisResult } from "@/types/v2";
import { getApiBaseUrl } from "./config";

const api = axios.create({
  baseURL: `${getApiBaseUrl()}/api`,
});

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
