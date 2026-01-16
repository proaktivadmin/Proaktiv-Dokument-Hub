"use client";

/**
 * Hook for fetching and grouping templates into shelves.
 */

import { useState, useEffect, useCallback, useMemo } from "react";
import { templateApi } from "@/lib/api";
import type {
  ShelfGroupBy,
  ShelfGroup,
  TemplateFilterState,
  TemplateWithMetadata,
} from "@/types/v2";

// Labels for different group values
const CHANNEL_LABELS: Record<string, string> = {
  pdf: "PDF",
  email: "E-post",
  sms: "SMS",
  pdf_email: "PDF & E-post",
};

const PHASE_LABELS: Record<string, string> = {
  Oppdrag: "Oppdrag",
  Markedsføring: "Markedsføring",
  Visning: "Visning",
  Budrunde: "Budrunde",
  Kontrakt: "Kontrakt",
  Oppgjør: "Oppgjør",
};

export interface UseGroupedTemplatesResult {
  shelves: ShelfGroup[];
  totalTemplates: number;
  isLoading: boolean;
  error: string | null;
  toggleCollapse: (shelfId: string) => void;
  collapseAll: () => void;
  expandAll: () => void;
  refetch: () => void;
  matchingIds: Set<string>;
}

/**
 * Group templates by the specified field
 */
function groupTemplates(
  templates: TemplateWithMetadata[],
  groupBy: ShelfGroupBy
): Map<string, TemplateWithMetadata[]> {
  const groups = new Map<string, TemplateWithMetadata[]>();

  for (const template of templates) {
    let groupValues: string[] = [];

    switch (groupBy) {
      case "channel":
        groupValues = [template.channel || "pdf_email"];
        break;
      case "phase":
        groupValues = template.phases.length > 0 ? template.phases : ["Ukjent"];
        break;
      case "receiver":
        groupValues = template.receiver ? [template.receiver] : ["Ukjent"];
        break;
      case "ownership_type":
        groupValues = template.ownership_types.length > 0 ? template.ownership_types : ["Ukjent"];
        break;
      case "category":
        groupValues = ["Alle"]; // TODO: Add category support
        break;
    }

    for (const value of groupValues) {
      if (!groups.has(value)) {
        groups.set(value, []);
      }
      groups.get(value)!.push(template);
    }
  }

  return groups;
}

/**
 * Get label for a group value
 */
function getGroupLabel(groupBy: ShelfGroupBy, value: string): string {
  switch (groupBy) {
    case "channel":
      return CHANNEL_LABELS[value] || value;
    case "phase":
      return PHASE_LABELS[value] || value;
    default:
      return value;
  }
}

/**
 * Hook for fetching and grouping templates into shelves.
 */
export function useGroupedTemplates(
  groupBy: ShelfGroupBy,
  filters?: Partial<TemplateFilterState>
): UseGroupedTemplatesResult {
  const [templates, setTemplates] = useState<TemplateWithMetadata[]>([]);
  const [collapsedShelves, setCollapsedShelves] = useState<Set<string>>(new Set());
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTemplates = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      // Fetch all templates (we'll group client-side)
      const response = await templateApi.list({
        status: filters?.status || undefined,
        search: filters?.search || undefined,
        per_page: 100, // Get all for grouping
      });

      // Transform to TemplateWithMetadata (add default V2 fields)
      const templatesWithMetadata: TemplateWithMetadata[] = response.templates.map((t) => ({
        ...t,
        preview_thumbnail_url: null,
        channel: "pdf_email" as const, // Default for existing templates
        template_type: null,
        receiver_type: null,
        receiver: null,
        extra_receivers: [],
        phases: [],
        assignment_types: [],
        ownership_types: [],
        departments: [],
        email_subject: null,
        header_template_id: null,
        footer_template_id: null,
        margin_top: 1.5,
        margin_bottom: 1.0,
        margin_left: 1.0,
        margin_right: 1.2,
      }));

      setTemplates(templatesWithMetadata);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch templates");
    } finally {
      setIsLoading(false);
    }
  }, [filters?.status, filters?.search]);

  useEffect(() => {
    fetchTemplates();
  }, [fetchTemplates]);

  // Group templates into shelves
  const shelves = useMemo((): ShelfGroup[] => {
    const grouped = groupTemplates(templates, groupBy);
    
    return Array.from(grouped.entries())
      .map(([value, items]) => ({
        id: `shelf-${groupBy}-${value}`,
        label: getGroupLabel(groupBy, value),
        groupValue: value,
        templates: items,
        count: items.length,
        isCollapsed: collapsedShelves.has(`shelf-${groupBy}-${value}`),
      }))
      .sort((a, b) => a.label.localeCompare(b.label, "nb"));
  }, [templates, groupBy, collapsedShelves]);

  // Calculate matching IDs based on filters
  const matchingIds = useMemo((): Set<string> => {
    if (!filters?.search && !filters?.channel && !filters?.receiver && 
        (!filters?.phases || filters.phases.length === 0) &&
        (!filters?.ownership_types || filters.ownership_types.length === 0)) {
      return new Set(templates.map((t) => t.id));
    }

    return new Set(
      templates
        .filter((t) => {
          if (filters?.channel && t.channel !== filters.channel) return false;
          if (filters?.receiver && t.receiver !== filters.receiver) return false;
          if (filters?.phases && filters.phases.length > 0) {
            if (!filters.phases.some((p) => t.phases.includes(p))) return false;
          }
          if (filters?.ownership_types && filters.ownership_types.length > 0) {
            if (!filters.ownership_types.some((o) => t.ownership_types.includes(o))) return false;
          }
          return true;
        })
        .map((t) => t.id)
    );
  }, [templates, filters]);

  const toggleCollapse = useCallback((shelfId: string) => {
    setCollapsedShelves((prev) => {
      const next = new Set(prev);
      if (next.has(shelfId)) {
        next.delete(shelfId);
      } else {
        next.add(shelfId);
      }
      return next;
    });
  }, []);

  const collapseAll = useCallback(() => {
    setCollapsedShelves(new Set(shelves.map((s) => s.id)));
  }, [shelves]);

  const expandAll = useCallback(() => {
    setCollapsedShelves(new Set());
  }, []);

  return {
    shelves,
    totalTemplates: templates.length,
    isLoading,
    error,
    toggleCollapse,
    collapseAll,
    expandAll,
    refetch: fetchTemplates,
    matchingIds,
  };
}
