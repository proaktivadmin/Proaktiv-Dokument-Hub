"use client";

/**
 * Hooks for fetching layout partials (headers/footers).
 */

import { useState, useEffect, useCallback } from "react";
import { layoutPartialsApi } from "@/lib/api";
import type {
  LayoutPartial,
  LayoutPartialType,
  LayoutPartialContext,
} from "@/types/v2";

export interface UseLayoutPartialsResult {
  partials: LayoutPartial[];
  total: number;
  isLoading: boolean;
  error: string | null;
  refetch: () => void;
  setDefault: (partialId: string) => Promise<void>;
}

/**
 * Hook for fetching layout partials (headers/footers).
 */
export function useLayoutPartials(
  type?: LayoutPartialType,
  context?: LayoutPartialContext
): UseLayoutPartialsResult {
  const [partials, setPartials] = useState<LayoutPartial[]>([]);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchPartials = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await layoutPartialsApi.list(type, context);
      
      setPartials(response.partials);
      setTotal(response.total);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch layout partials");
    } finally {
      setIsLoading(false);
    }
  }, [type, context]);

  useEffect(() => {
    fetchPartials();
  }, [fetchPartials]);

  const setDefault = useCallback(async (partialId: string) => {
    await layoutPartialsApi.setDefault(partialId);
    // Refetch to update the list
    await fetchPartials();
  }, [fetchPartials]);

  return {
    partials,
    total,
    isLoading,
    error,
    refetch: fetchPartials,
    setDefault,
  };
}

export interface UseDefaultPartialResult {
  partial: LayoutPartial | null;
  isLoading: boolean;
}

/**
 * Hook for fetching the default partial for a type/context.
 */
export function useDefaultPartial(
  type: LayoutPartialType,
  context: LayoutPartialContext = "all"
): UseDefaultPartialResult {
  const [partial, setPartial] = useState<LayoutPartial | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchDefault = async () => {
      setIsLoading(true);
      
      try {
        const result = await layoutPartialsApi.getDefault(type, context);
        setPartial(result);
      } catch (err) {
        setPartial(null);
      } finally {
        setIsLoading(false);
      }
    };

    fetchDefault();
  }, [type, context]);

  return {
    partial,
    isLoading,
  };
}
