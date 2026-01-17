/**
 * Storage API Client
 * 
 * Client for WebDAV network storage operations.
 */

import { AxiosError } from "axios";
import { apiClient } from "./config";

// Types

export interface StorageItem {
  name: string;
  path: string;
  is_directory: boolean;
  size: number;
  modified: string | null;
  content_type: string | null;
}

export interface BrowseResponse {
  path: string;
  items: StorageItem[];
  parent_path: string | null;
}

export interface StorageStatus {
  configured: boolean;
  connected: boolean;
  message: string;
}

export interface ImportToLibraryPayload {
  path: string;
  title: string;
  description?: string;
  status?: "draft" | "published";
  category_id?: string;
  auto_sanitize?: boolean;
}

export interface ImportResult {
  success: boolean;
  template: {
    id: string;
    title: string;
    file_name: string;
    file_type: string;
    status: string;
  };
}

export interface MovePayload {
  source: string;
  destination: string;
}

// Error handler

function handleError(error: unknown, context: string): never {
  console.error(`[Storage API Error] ${context}:`, error);

  if (error instanceof AxiosError) {
    if (error.code === "ERR_NETWORK") {
      throw new Error("Nettverksfeil: Kan ikke koble til serveren.");
    }

    if (error.response?.data?.detail) {
      throw new Error(error.response.data.detail);
    }

    if (error.response?.status === 503) {
      throw new Error("Lagring er ikke konfigurert. Kontakt administrator.");
    }
  }

  if (error instanceof Error) {
    throw error;
  }

  throw new Error("En uventet feil oppstod");
}

// API Client

export const storageApi = {
  /**
   * Get storage connection status
   */
  async getStatus(): Promise<StorageStatus> {
    try {
      const { data } = await apiClient.get<StorageStatus>("/storage/status");
      return data;
    } catch (error) {
      handleError(error, "storageApi.getStatus");
    }
  },

  /**
   * Browse a directory
   */
  async browse(path: string = "/"): Promise<BrowseResponse> {
    try {
      const { data } = await apiClient.get<BrowseResponse>("/storage/browse", {
        params: { path },
      });
      return data;
    } catch (error) {
      handleError(error, "storageApi.browse");
    }
  },

  /**
   * Download a file
   */
  async download(path: string): Promise<Blob> {
    try {
      const response = await apiClient.get("/storage/download", {
        params: { path },
        responseType: "blob",
      });
      return response.data;
    } catch (error) {
      handleError(error, "storageApi.download");
    }
  },

  /**
   * Get download URL for direct linking
   */
  getDownloadUrl(path: string): string {
    const encodedPath = encodeURIComponent(path);
    return `/api/storage/download?path=${encodedPath}`;
  },

  /**
   * Upload a file
   */
  async upload(
    destinationPath: string,
    file: File
  ): Promise<{ success: boolean; path: string; filename: string; size: number }> {
    try {
      const formData = new FormData();
      formData.append("path", destinationPath);
      formData.append("file", file);

      const { data } = await apiClient.post("/storage/upload", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      return data;
    } catch (error) {
      handleError(error, "storageApi.upload");
    }
  },

  /**
   * Create a directory
   */
  async createDirectory(path: string): Promise<{ success: boolean; path: string }> {
    try {
      const formData = new FormData();
      formData.append("path", path);

      const { data } = await apiClient.post("/storage/mkdir", formData);
      return data;
    } catch (error) {
      handleError(error, "storageApi.createDirectory");
    }
  },

  /**
   * Move or rename a file/directory
   */
  async move(
    source: string,
    destination: string
  ): Promise<{ success: boolean; source: string; destination: string }> {
    try {
      const { data } = await apiClient.post<{
        success: boolean;
        source: string;
        destination: string;
      }>("/storage/move", { source, destination });
      return data;
    } catch (error) {
      handleError(error, "storageApi.move");
    }
  },

  /**
   * Delete a file or directory
   */
  async delete(path: string): Promise<{ success: boolean; path: string }> {
    try {
      const { data } = await apiClient.delete("/storage/delete", {
        params: { path },
      });
      return data;
    } catch (error) {
      handleError(error, "storageApi.delete");
    }
  },

  /**
   * Import a file to the template library
   */
  async importToLibrary(payload: ImportToLibraryPayload): Promise<ImportResult> {
    try {
      const { data } = await apiClient.post<ImportResult>(
        "/storage/import-to-library",
        payload
      );
      return data;
    } catch (error) {
      handleError(error, "storageApi.importToLibrary");
    }
  },
};
