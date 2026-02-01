"use client";

import { useCallback, useState } from "react";
import { apiClient } from "@/lib/api/config";

interface UploadResult {
  success: boolean;
  asset_id: string;
  message: string;
}

export function useSignaturePhotoUpload(employeeId: string | null) {
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const upload = useCallback(
    async (file: File): Promise<UploadResult> => {
      if (!employeeId) throw new Error("Missing employee ID");

      setIsUploading(true);
      setError(null);
      try {
        const formData = new FormData();
        formData.append("file", file);

        const response = await apiClient.post<UploadResult>(
          `/signatures/${employeeId}/photo/upload`,
          formData,
          {
            headers: { "Content-Type": "multipart/form-data" },
          }
        );
        return response.data;
      } catch (err) {
        const message =
          err instanceof Error ? err.message : "Kunne ikke laste opp bilde";
        setError(message);
        throw new Error(message);
      } finally {
        setIsUploading(false);
      }
    },
    [employeeId]
  );

  return { upload, isUploading, error };
}
