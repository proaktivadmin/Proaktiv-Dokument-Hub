import { AxiosError } from "axios";
import type {
  Template,
  TemplateListResponse,
  UploadTemplatePayload,
  UploadTemplateResponse,
  UpdateTemplatePayload,
  UpdateTemplateResponse,
  Category,
  DashboardStats,
  WorkflowTransition,
  WorkflowStatusResponse,
  WorkflowEvent,
} from "@/types";
import { apiClient } from "./api/config";

// Use the shared API client with dynamic URL support
const api = apiClient;

/**
 * Handle API errors with detailed logging
 */
function handleError(error: unknown, context: string): never {
  console.error(`[API Error] ${context}:`, error);

  if (error instanceof AxiosError) {
    // Log detailed error information
    console.error("[API Error] Status:", error.response?.status);
    console.error("[API Error] Data:", error.response?.data);
    console.error("[API Error] Headers:", error.response?.headers);
    console.error("[API Error] Request URL:", error.config?.url);
    console.error("[API Error] Request Method:", error.config?.method);

    if (error.code === "ERR_NETWORK") {
      throw new Error(
        "Nettverksfeil: Kan ikke koble til serveren. Sjekk at backend kjører på port 8000."
      );
    }

    if (error.response?.data?.detail) {
      throw new Error(error.response.data.detail);
    }

    if (error.response?.status === 422) {
      throw new Error("Valideringsfeil: Sjekk at alle felt er korrekt utfylt.");
    }
  }

  if (error instanceof Error) {
    throw error;
  }

  throw new Error("En uventet feil oppstod");
}

/**
 * Analytics API
 */
export const analyticsApi = {
  /**
   * Get dashboard statistics
   */
  async getDashboardStats(): Promise<DashboardStats> {
    try {
      const { data } = await api.get<DashboardStats>("/analytics/dashboard");
      return data;
    } catch (error) {
      handleError(error, "analyticsApi.getDashboardStats");
    }
  },
};

/**
 * Category API
 */
export interface CategoryListResponse {
  categories: Category[];
}

export const categoryApi = {
  /**
   * List all categories
   */
  async list(): Promise<Category[]> {
    try {
      const { data } = await api.get<CategoryListResponse>("/categories");
      return data.categories;
    } catch (error) {
      handleError(error, "categoryApi.list");
    }
  },
};

/**
 * Template API
 */
export const templateApi = {
  /**
   * List templates with optional filtering
   */
  async list(params?: {
    status?: string;
    search?: string;
    category_id?: string;
    receiver?: string;
    page?: number;
    per_page?: number;
    sort_by?: string;
    sort_order?: string;
  }): Promise<TemplateListResponse> {
    try {
      const { data } = await api.get<TemplateListResponse>("/templates", {
        params,
      });
      return data;
    } catch (error) {
      handleError(error, "templateApi.list");
    }
  },

  /**
   * Get a single template by ID
   */
  async getById(templateId: string): Promise<Template> {
    try {
      const { data } = await api.get<Template>(`/templates/${templateId}`);
      return data;
    } catch (error) {
      handleError(error, "templateApi.getById");
    }
  },

  /**
   * Upload a new template
   */
  async upload(payload: UploadTemplatePayload): Promise<UploadTemplateResponse> {
    try {
      const formData = new FormData();
      formData.append("file", payload.file);
      formData.append("title", payload.title);

      if (payload.description) {
        formData.append("description", payload.description);
      }

      if (payload.status) {
        formData.append("status", payload.status);
      }

      if (payload.category_id) {
        formData.append("category_id", payload.category_id);
      }

      // auto_sanitize defaults to false, so only append if explicitly set
      if (payload.auto_sanitize !== undefined) {
        formData.append("auto_sanitize", String(payload.auto_sanitize));
      }

      // Debug logging
      console.log("[API] Uploading template:", {
        fileName: payload.file.name,
        fileSize: payload.file.size,
        fileType: payload.file.type,
        title: payload.title,
        description: payload.description,
        status: payload.status,
        category_id: payload.category_id,
        auto_sanitize: payload.auto_sanitize,
      });

      const { data } = await api.post<UploadTemplateResponse>(
        "/templates",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      console.log("[API] Upload successful:", data);
      return data;
    } catch (error) {
      handleError(error, "templateApi.upload");
    }
  },

  /**
   * Update template metadata
   */
  async update(
    templateId: string,
    payload: UpdateTemplatePayload
  ): Promise<UpdateTemplateResponse> {
    try {
      console.log("[API] Updating template:", { templateId, payload });

      const { data } = await api.put<UpdateTemplateResponse>(
        `/templates/${templateId}`,
        payload
      );

      console.log("[API] Update successful:", data);
      return data;
    } catch (error) {
      handleError(error, "templateApi.update");
    }
  },

  /**
   * Delete a template by ID
   */
  async delete(templateId: string): Promise<void> {
    try {
      await api.delete(`/templates/${templateId}`);
    } catch (error) {
      handleError(error, "templateApi.delete");
    }
  },

  /**
   * Get download URL for a template
   */
  async getDownloadUrl(
    templateId: string
  ): Promise<{ download_url: string; file_name: string }> {
    try {
      const { data } = await api.get<{ download_url: string; file_name: string }>(
        `/templates/${templateId}/download`
      );
      return data;
    } catch (error) {
      handleError(error, "templateApi.getDownloadUrl");
    }
  },

  /**
   * Get template content for preview (HTML templates only)
   */
  async getContent(
    templateId: string
  ): Promise<{ id: string; title: string; file_type: string; content: string }> {
    try {
      const { data } = await api.get<{
        id: string;
        title: string;
        file_type: string;
        content: string;
      }>(`/templates/${templateId}/content`);
      return data;
    } catch (error) {
      handleError(error, "templateApi.getContent");
    }
  },

  /**
   * Save template HTML content
   */
  async saveContent(
    templateId: string,
    content: string,
    changeNotes?: string,
    autoSanitize?: boolean
  ): Promise<{ id: string; version: number; content_hash: string; merge_fields_detected: number }> {
    try {
      const { data } = await api.put(`/templates/${templateId}/content`, {
        content,
        change_notes: changeNotes,
        auto_sanitize: autoSanitize ?? false,
      });
      return data;
    } catch (error) {
      handleError(error, "templateApi.saveContent");
    }
  },

  /**
   * Transition workflow state
   */
  async transitionWorkflow(
    templateId: string,
    body: WorkflowTransition
  ): Promise<WorkflowStatusResponse> {
    try {
      const { data } = await api.post<WorkflowStatusResponse>(
        `/templates/${templateId}/workflow`,
        body
      );
      return data;
    } catch (error) {
      handleError(error, "templateApi.transitionWorkflow");
    }
  },

  /**
   * Get current workflow status
   */
  async getWorkflowStatus(
    templateId: string
  ): Promise<WorkflowStatusResponse> {
    try {
      const { data } = await api.get<WorkflowStatusResponse>(
        `/templates/${templateId}/workflow`
      );
      return data;
    } catch (error) {
      handleError(error, "templateApi.getWorkflowStatus");
    }
  },

  /**
   * Get workflow transition history
   */
  async getWorkflowHistory(
    templateId: string
  ): Promise<WorkflowEvent[]> {
    try {
      const { data } = await api.get<WorkflowEvent[]>(
        `/templates/${templateId}/workflow/history`
      );
      return data;
    } catch (error) {
      handleError(error, "templateApi.getWorkflowHistory");
    }
  },
};

/**
 * Deduplication types
 */
export interface DedupMergeCandidate {
  template_id: string;
  title: string;
  property_type: string | null;
  content_length: number;
  similarity_score: number;
}

export interface DedupMergeCandidateGroup {
  base_title: string;
  candidates: DedupMergeCandidate[];
  category: string | null;
  estimated_reduction: number;
}

export interface DedupContentSection {
  path: string;
  content_hash: string;
  is_shared: boolean;
  differs_in: string[];
  preview: string;
}

export interface DedupMergeAnalysis {
  group_title: string;
  templates: DedupMergeCandidate[];
  shared_sections: DedupContentSection[];
  divergent_sections: DedupContentSection[];
  unique_sections: DedupContentSection[];
  merge_complexity: "simple" | "moderate" | "complex";
  auto_mergeable: boolean;
  warnings: string[];
}

export interface DedupMergePreview {
  merged_html: string;
  primary_template_id: string;
  templates_to_archive: string[];
  vitec_if_conditions_added: number;
  warnings: string[];
  validation_passed: boolean;
}

export interface DedupMergeResult {
  primary_template_id: string;
  archived_template_ids: string[];
  new_version: number;
  property_types_covered: string[];
}

/**
 * Deduplication API
 */
export const dedupApi = {
  async candidates(): Promise<DedupMergeCandidateGroup[]> {
    try {
      const { data } = await api.get<DedupMergeCandidateGroup[]>("/templates/dedup/candidates");
      return data;
    } catch (error) {
      handleError(error, "dedupApi.candidates");
    }
  },

  async analyze(templateIds: string[]): Promise<DedupMergeAnalysis> {
    try {
      const { data } = await api.post<DedupMergeAnalysis>("/templates/dedup/analyze", {
        template_ids: templateIds,
      });
      return data;
    } catch (error) {
      handleError(error, "dedupApi.analyze");
    }
  },

  async preview(templateIds: string[], primaryId: string): Promise<DedupMergePreview> {
    try {
      const { data } = await api.post<DedupMergePreview>("/templates/dedup/preview", {
        template_ids: templateIds,
        primary_id: primaryId,
      });
      return data;
    } catch (error) {
      handleError(error, "dedupApi.preview");
    }
  },

  async execute(templateIds: string[], primaryId: string, mergedHtml: string): Promise<DedupMergeResult> {
    try {
      const { data } = await api.post<DedupMergeResult>("/templates/dedup/execute", {
        template_ids: templateIds,
        primary_id: primaryId,
        merged_html: mergedHtml,
      });
      return data;
    } catch (error) {
      handleError(error, "dedupApi.execute");
    }
  },
};

/**
 * Word Conversion types
 */
export interface ValidationItem {
  rule: string;
  passed: boolean;
  detail: string | null;
}

export interface ConversionResult {
  html: string;
  warnings: string[];
  validation: ValidationItem[];
  merge_fields_detected: string[];
  is_valid: boolean;
}

/**
 * Word Conversion API
 */
export const wordConversionApi = {
  async convertDocx(file: File): Promise<ConversionResult> {
    try {
      const formData = new FormData();
      formData.append("file", file);
      const { data } = await api.post<ConversionResult>(
        "/templates/convert-docx",
        formData,
        { headers: { "Content-Type": "multipart/form-data" } }
      );
      return data;
    } catch (error) {
      handleError(error, "wordConversionApi.convertDocx");
    }
  },
};

/**
 * V2 API Clients - Re-export from dedicated files
 */
export { mergeFieldsApi } from "./api/merge-fields";
export { codePatternsApi } from "./api/code-patterns";
export { layoutPartialsApi } from "./api/layout-partials";
export { templateAnalysisApi } from "./api/template-analysis";
export { templateSettingsApi } from "./api/template-settings";
export { dashboardApi } from "./api/dashboard";
export { storageApi } from "./api/storage";
export type { StorageItem, BrowseResponse, StorageStatus, ImportToLibraryPayload, ImportResult } from "./api/storage";
export { vitecApi } from "./api/vitec";
export type { VitecStatus } from "./api/vitec";
export { entraSyncApi } from "./api/entra-sync";

/**
 * Template Comparison API
 */
export const templateComparisonApi = {
  async compareWithVitec(
    templateId: string,
    updatedHtml: string
  ): Promise<import("@/types").AnalysisReport> {
    try {
      const { data } = await api.post<import("@/types").AnalysisReport>(
        `/templates/${templateId}/compare`,
        { updated_html: updatedHtml }
      );
      return data;
    } catch (error) {
      handleError(error, "templateComparisonApi.compareWithVitec");
    }
  },

  async applyComparison(
    templateId: string,
    action: "adopt" | "ignore",
    updatedHtml?: string
  ): Promise<{ status: string; version?: number; new_hash?: string }> {
    try {
      const { data } = await api.post<{
        status: string;
        version?: number;
        new_hash?: string;
      }>(`/templates/${templateId}/compare/apply`, {
        action,
        updated_html: updatedHtml,
      });
      return data;
    } catch (error) {
      handleError(error, "templateComparisonApi.applyComparison");
    }
  },

  async compareStandalone(
    storedHtml: string,
    updatedHtml: string,
    title: string
  ): Promise<import("@/types").AnalysisReport> {
    try {
      const { data } = await api.post<import("@/types").AnalysisReport>(
        "/templates/compare-standalone",
        { stored_html: storedHtml, updated_html: updatedHtml, template_title: title }
      );
      return data;
    } catch (error) {
      handleError(error, "templateComparisonApi.compareStandalone");
    }
  },
};