import { AxiosError } from "axios";
import type {
  TemplateListResponse,
  UploadTemplatePayload,
  UploadTemplateResponse,
  UpdateTemplatePayload,
  UpdateTemplateResponse,
  Category,
  DashboardStats,
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

      // auto_sanitize defaults to true, so only append if explicitly set
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