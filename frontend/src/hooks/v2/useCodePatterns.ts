"use client";

/**
 * Hooks for fetching code patterns from the pattern library.
 */

import { useState, useEffect, useCallback } from "react";
import { codePatternsApi } from "@/lib/api";
import type { CodePattern } from "@/types/v2";

export interface UseCodePatternsOptions {
  category?: string;
  search?: string;
  page?: number;
  perPage?: number;
}

export interface UseCodePatternsResult {
  patterns: CodePattern[];
  total: number;
  page: number;
  totalPages: number;
  isLoading: boolean;
  error: string | null;
  refetch: () => void;
}

/**
 * Hook for fetching code patterns from the pattern library.
 */
export function useCodePatterns(options: UseCodePatternsOptions = {}): UseCodePatternsResult {
  const [patterns, setPatterns] = useState<CodePattern[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(options.page || 1);
  const [totalPages, setTotalPages] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchPatterns = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await codePatternsApi.list({
        category: options.category,
        search: options.search,
        page,
        per_page: options.perPage || 20,
      });
      
      setPatterns(response.patterns);
      setTotal(response.total);
      setTotalPages(response.total_pages);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch code patterns");
    } finally {
      setIsLoading(false);
    }
  }, [options.category, options.search, options.perPage, page]);

  useEffect(() => {
    fetchPatterns();
  }, [fetchPatterns]);

  return {
    patterns,
    total,
    page,
    totalPages,
    isLoading,
    error,
    refetch: fetchPatterns,
  };
}

export interface UseCodePatternCategoriesResult {
  categories: string[];
  isLoading: boolean;
  error: string | null;
}

/**
 * Hook for fetching code pattern categories.
 */
export function useCodePatternCategories(): UseCodePatternCategoriesResult {
  const [categories, setCategories] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchCategories = async () => {
      setIsLoading(true);
      setError(null);
      
      try {
        const categoryNames = await codePatternsApi.getCategories();
        setCategories(categoryNames);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to fetch categories");
      } finally {
        setIsLoading(false);
      }
    };

    fetchCategories();
  }, []);

  return {
    categories,
    isLoading,
    error,
  };
}
