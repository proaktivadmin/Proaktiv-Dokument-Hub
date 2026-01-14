"use client";

/**
 * Hooks for fetching merge fields from the Flettekode registry.
 */

import { useState, useEffect, useCallback } from "react";
import { mergeFieldsApi } from "@/lib/api";
import type {
  MergeField,
  MergeFieldDataType,
  MergeFieldCategoryCount,
} from "@/types/v2";

export interface UseMergeFieldsOptions {
  category?: string;
  search?: string;
  dataType?: MergeFieldDataType;
  isIterable?: boolean;
  page?: number;
  perPage?: number;
}

export interface UseMergeFieldsResult {
  fields: MergeField[];
  total: number;
  page: number;
  totalPages: number;
  isLoading: boolean;
  error: string | null;
  refetch: () => void;
  goToPage: (page: number) => void;
}

/**
 * Hook for fetching merge fields from the Flettekode registry.
 */
export function useMergeFields(options: UseMergeFieldsOptions = {}): UseMergeFieldsResult {
  const [fields, setFields] = useState<MergeField[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(options.page || 1);
  const [totalPages, setTotalPages] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchFields = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await mergeFieldsApi.list({
        category: options.category,
        search: options.search,
        data_type: options.dataType,
        is_iterable: options.isIterable,
        page,
        per_page: options.perPage || 50,
      });
      
      setFields(response.merge_fields);
      setTotal(response.total);
      setTotalPages(response.total_pages);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch merge fields");
    } finally {
      setIsLoading(false);
    }
  }, [options.category, options.search, options.dataType, options.isIterable, options.perPage, page]);

  useEffect(() => {
    fetchFields();
  }, [fetchFields]);

  const goToPage = useCallback((newPage: number) => {
    setPage(newPage);
  }, []);

  return {
    fields,
    total,
    page,
    totalPages,
    isLoading,
    error,
    refetch: fetchFields,
    goToPage,
  };
}

export interface UseMergeFieldCategoriesResult {
  categories: MergeFieldCategoryCount[];
  isLoading: boolean;
  error: string | null;
  refetch: () => void;
}

/**
 * Hook for fetching merge field categories with counts.
 */
export function useMergeFieldCategories(): UseMergeFieldCategoriesResult {
  const [categories, setCategories] = useState<MergeFieldCategoryCount[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchCategories = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const categoryNames = await mergeFieldsApi.getCategories();
      
      // For now, we don't have counts from the API, so set count to 0
      // This could be enhanced later with a dedicated endpoint
      const categoriesWithCounts: MergeFieldCategoryCount[] = categoryNames.map(name => ({
        name,
        count: 0,
      }));
      
      setCategories(categoriesWithCounts);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch categories");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchCategories();
  }, [fetchCategories]);

  return {
    categories,
    isLoading,
    error,
    refetch: fetchCategories,
  };
}

export interface UseMergeFieldAutocompleteResult {
  suggestions: MergeField[];
  isLoading: boolean;
}

/**
 * Hook for merge field autocomplete suggestions.
 */
export function useMergeFieldAutocomplete(
  query: string,
  limit: number = 10
): UseMergeFieldAutocompleteResult {
  const [suggestions, setSuggestions] = useState<MergeField[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    // Only search if query is at least 2 characters
    if (query.length < 2) {
      setSuggestions([]);
      return;
    }

    let cancelled = false;
    
    const fetchSuggestions = async () => {
      setIsLoading(true);
      
      try {
        const results = await mergeFieldsApi.autocomplete(query, limit);
        if (!cancelled) {
          setSuggestions(results);
        }
      } catch (err) {
        if (!cancelled) {
          setSuggestions([]);
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    };

    // Debounce the search
    const timeoutId = setTimeout(fetchSuggestions, 200);

    return () => {
      cancelled = true;
      clearTimeout(timeoutId);
    };
  }, [query, limit]);

  return {
    suggestions,
    isLoading,
  };
}
