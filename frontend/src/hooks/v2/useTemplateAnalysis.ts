"use client";

/**
 * Hook for analyzing a template's merge fields and patterns.
 */

import { useState, useEffect, useCallback } from "react";
import { templateAnalysisApi } from "@/lib/api";
import type { TemplateAnalysisResult } from "@/types/v2";

export interface UseTemplateAnalysisResult {
  analysis: TemplateAnalysisResult | null;
  isLoading: boolean;
  error: string | null;
  reanalyze: () => void;
}

/**
 * Hook for analyzing a template's merge fields and patterns.
 */
export function useTemplateAnalysis(
  templateId: string | null
): UseTemplateAnalysisResult {
  const [analysis, setAnalysis] = useState<TemplateAnalysisResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchAnalysis = useCallback(async () => {
    if (!templateId) {
      setAnalysis(null);
      return;
    }

    setIsLoading(true);
    setError(null);
    
    try {
      const result = await templateAnalysisApi.analyze(templateId);
      setAnalysis(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to analyze template");
      setAnalysis(null);
    } finally {
      setIsLoading(false);
    }
  }, [templateId]);

  useEffect(() => {
    fetchAnalysis();
  }, [fetchAnalysis]);

  return {
    analysis,
    isLoading,
    error,
    reanalyze: fetchAnalysis,
  };
}
