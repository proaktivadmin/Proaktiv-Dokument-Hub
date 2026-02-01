"use client";

import { useCallback, useEffect, useState } from "react";
import { apiClient } from "@/lib/api/config";

export interface SignatureOverrides {
  employee_id: string;
  display_name: string | null;
  job_title: string | null;
  mobile_phone: string | null;
  email: string | null;
  office_name: string | null;
  facebook_url: string | null;
  instagram_url: string | null;
  linkedin_url: string | null;
  employee_url: string | null;
  updated_at: string;
}

export interface SignatureOverrideInput {
  display_name?: string | null;
  job_title?: string | null;
  mobile_phone?: string | null;
  email?: string | null;
  office_name?: string | null;
  facebook_url?: string | null;
  instagram_url?: string | null;
  linkedin_url?: string | null;
  employee_url?: string | null;
}

export function useSignatureOverrides(employeeId: string | null) {
  const [overrides, setOverrides] = useState<SignatureOverrides | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchOverrides = useCallback(async () => {
    if (!employeeId) return;

    setIsLoading(true);
    setError(null);
    try {
      const response = await apiClient.get<SignatureOverrides | null>(
        `/signatures/${employeeId}/overrides`
      );
      setOverrides(response.data);
    } catch {
      // 404 is expected when no overrides exist
      setOverrides(null);
    } finally {
      setIsLoading(false);
    }
  }, [employeeId]);

  useEffect(() => {
    fetchOverrides();
  }, [fetchOverrides]);

  const save = useCallback(
    async (data: SignatureOverrideInput): Promise<SignatureOverrides> => {
      if (!employeeId) throw new Error("Missing employee ID");

      setIsSaving(true);
      setError(null);
      try {
        const response = await apiClient.put<SignatureOverrides>(
          `/signatures/${employeeId}/overrides`,
          data
        );
        setOverrides(response.data);
        return response.data;
      } catch (err) {
        const message =
          err instanceof Error ? err.message : "Kunne ikke lagre endringer";
        setError(message);
        throw new Error(message);
      } finally {
        setIsSaving(false);
      }
    },
    [employeeId]
  );

  const reset = useCallback(async (): Promise<void> => {
    if (!employeeId) return;

    setIsSaving(true);
    setError(null);
    try {
      await apiClient.delete(`/signatures/${employeeId}/overrides`);
      setOverrides(null);
    } catch {
      // Ignore 404 — already no overrides
    } finally {
      setIsSaving(false);
    }
  }, [employeeId]);

  return {
    overrides,
    isLoading,
    isSaving,
    error,
    save,
    reset,
    refetch: fetchOverrides,
  };
}
