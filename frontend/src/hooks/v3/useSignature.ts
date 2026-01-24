"use client";

import { useCallback, useEffect, useState } from "react";
import { apiClient } from "@/lib/api/config";

export type SignatureVersion = "with-photo" | "no-photo";

export interface SignatureResponse {
  html: string;
  text: string;
  employee_name: string;
  employee_email: string;
}

export interface SignatureSendResponse {
  success: boolean;
  sent_to: string;
  message: string;
}

export function useSignature(
  employeeId: string | null,
  version: SignatureVersion = "with-photo"
) {
  const [signature, setSignature] = useState<SignatureResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    if (!employeeId) {
      setSignature(null);
      setError(null);
      return;
    }

    setIsLoading(true);
    setError(null);
    try {
      const response = await apiClient.get<SignatureResponse>(
        `/signatures/${employeeId}`,
        {
          params: { version },
        }
      );
      setSignature(response.data);
    } catch (err) {
      console.error("[useSignature] Error:", err);
      setError(
        err instanceof Error ? err.message : "Kunne ikke laste signaturen"
      );
      setSignature(null);
    } finally {
      setIsLoading(false);
    }
  }, [employeeId, version]);

  useEffect(() => {
    fetch();
  }, [fetch]);

  return { signature, isLoading, error, refetch: fetch };
}

export function useSendSignature(employeeId: string | null) {
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const send = useCallback(async (): Promise<SignatureSendResponse> => {
    if (!employeeId) {
      const message = "Mangler ansatt-ID";
      setError(message);
      throw new Error(message);
    }

    setIsSending(true);
    setError(null);
    try {
      const response = await apiClient.post<SignatureSendResponse>(
        `/signatures/${employeeId}/send`
      );
      return response.data;
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Kunne ikke sende signatur";
      console.error("[useSendSignature] Error:", err);
      setError(message);
      throw new Error(message);
    } finally {
      setIsSending(false);
    }
  }, [employeeId]);

  return { send, isSending, error };
}
