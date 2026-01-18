"use client";

import { useState, useEffect, useCallback } from "react";
import { templateApi } from "@/lib/api";
import type { Template, TemplateListResponse } from "@/types";

interface UseTemplatesParams {
  status?: string;
  search?: string;
  category_id?: string;
  receiver?: string;
  page?: number;
  per_page?: number;
  sort_by?: string;
  sort_order?: string;
}

interface UseTemplatesReturn {
  templates: Template[];
  pagination: TemplateListResponse["pagination"] | null;
  isLoading: boolean;
  error: string | null;
  refetch: () => void;
}

export function useTemplates(params: UseTemplatesParams = {}): UseTemplatesReturn {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [pagination, setPagination] = useState<TemplateListResponse["pagination"] | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTemplates = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const data = await templateApi.list(params);
      setTemplates(data.templates);
      setPagination(data.pagination);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load templates");
      console.error("[useTemplates] Error:", err);
    } finally {
      setIsLoading(false);
    }
  }, [
    params.status,
    params.search,
    params.category_id,
    params.receiver,
    params.page,
    params.per_page,
    params.sort_by,
    params.sort_order,
  ]);

  useEffect(() => {
    fetchTemplates();
  }, [fetchTemplates]);

  return { templates, pagination, isLoading, error, refetch: fetchTemplates };
}

/**
 * Hook to fetch recent templates (limit 5)
 */
export function useRecentTemplates(): UseTemplatesReturn {
  return useTemplates({ per_page: 5, sort_by: "created_at", sort_order: "desc" });
}
