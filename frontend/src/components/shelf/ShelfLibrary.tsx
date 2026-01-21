"use client";

/**
 * ShelfLibrary - Main container for shelf-based template library
 */

import { useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { Search, ChevronDown, ChevronUp } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { ShelfRow } from "./ShelfRow";
import { GroupBySelector } from "./GroupBySelector";
import { useGroupedTemplates } from "@/hooks/v2";
import { templateApi } from "@/lib/api";
import type { ShelfGroupBy, TemplateFilterState, TemplateWithMetadata } from "@/types/v2";

interface ShelfLibraryProps {
  defaultGroupBy?: ShelfGroupBy;
  initialFilters?: Partial<TemplateFilterState>;
  onTemplateSelect?: (template: TemplateWithMetadata) => void;
  onTemplateSettings?: (template: TemplateWithMetadata) => void;
  onTemplatePreview?: (template: TemplateWithMetadata) => void;
  onTemplateEdit?: (template: TemplateWithMetadata) => void;
  onTemplateDelete?: (template: TemplateWithMetadata) => void;
}

export function ShelfLibrary({
  defaultGroupBy = "channel",
  initialFilters,
  onTemplateSelect,
  onTemplateSettings,
  onTemplatePreview,
  onTemplateEdit,
  onTemplateDelete,
}: ShelfLibraryProps) {
  const router = useRouter();
  const [groupBy, setGroupBy] = useState<ShelfGroupBy>(defaultGroupBy);
  const [searchQuery, setSearchQuery] = useState(initialFilters?.search || "");
  const [filters] = useState<Partial<TemplateFilterState>>(initialFilters || {});

  const {
    shelves,
    totalTemplates,
    isLoading,
    error,
    toggleCollapse,
    collapseAll,
    expandAll,
    matchingIds,
  } = useGroupedTemplates(groupBy, {
    ...filters,
    search: searchQuery || undefined,
  });

  const handleTemplateClick = useCallback(
    (template: TemplateWithMetadata) => {
      if (onTemplateSelect) {
        onTemplateSelect(template);
      } else {
        // Default: navigate to template detail page
        router.push(`/templates/${template.id}`);
      }
    },
    [onTemplateSelect, router]
  );

  const handleCodeView = useCallback((template: TemplateWithMetadata) => {
    // Navigate to template with code view
    router.push(`/templates/${template.id}?view=code`);
  }, [router]);

  const handleDownload = useCallback(async (template: TemplateWithMetadata) => {
    try {
      const { download_url, file_name } = await templateApi.getDownloadUrl(template.id);
      if (download_url.startsWith("mock://")) {
        alert(`Nedlasting er ikke tilgjengelig ennå. Fil: ${file_name}`);
      } else {
        window.open(download_url, "_blank");
      }
    } catch (error) {
      console.error("Failed to get download URL:", error);
      alert("Kunne ikke laste ned filen. Prøv igjen.");
    }
  }, []);

  return (
    <div className="flex flex-col h-full">
      {/* Header bar */}
      <div className="flex items-center justify-between gap-4 mb-6">
        {/* Search */}
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <Input
            type="search"
            placeholder="Søk maler..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>

        {/* Group by selector */}
        <GroupBySelector value={groupBy} onChange={setGroupBy} />

        {/* Collapse/Expand all */}
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={collapseAll}>
            <ChevronUp className="h-4 w-4 mr-1" />
            Skjul alle
          </Button>
          <Button variant="outline" size="sm" onClick={expandAll}>
            <ChevronDown className="h-4 w-4 mr-1" />
            Vis alle
          </Button>
        </div>
      </div>

      {/* Loading state */}
      {isLoading && (
        <div className="flex items-center justify-center py-12">
          <div className="text-gray-500">Laster maler...</div>
        </div>
      )}

      {/* Error state */}
      {error && (
        <div className="flex items-center justify-center py-12">
          <div className="text-red-500">{error}</div>
        </div>
      )}

      {/* Shelf rows */}
      {!isLoading && !error && (
        <div className="flex-1 overflow-y-auto">
          {shelves.length === 0 ? (
            <div className="flex items-center justify-center py-12 text-gray-500">
              Ingen maler funnet
            </div>
          ) : (
            shelves.map((shelf) => (
              <ShelfRow
                key={shelf.id}
                shelf={shelf}
                dimNonMatching={!!searchQuery}
                matchingIds={matchingIds}
                onTemplateClick={handleTemplateClick}
                onToggleCollapse={toggleCollapse}
                onTemplateSettings={onTemplateSettings}
                onTemplateCodeView={handleCodeView}
                onTemplatePreview={onTemplatePreview}
                onTemplateEdit={onTemplateEdit}
                onTemplateDownload={handleDownload}
                onTemplateDelete={onTemplateDelete}
              />
            ))
          )}
        </div>
      )}

      {/* Footer stats */}
      {!isLoading && (
        <div className="mt-4 text-sm text-gray-500">
          {totalTemplates} maler totalt • {shelves.length} grupper
        </div>
      )}
    </div>
  );
}
