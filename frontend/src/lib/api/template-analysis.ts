/**
 * Template Analysis API Client
 */

import axios from "axios";
import type { TemplateAnalysisResult } from "@/types/v2";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: `${API_BASE_URL}/api`,
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
