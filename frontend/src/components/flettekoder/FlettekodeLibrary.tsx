"use client";

/**
 * FlettekodeLibrary - Main container for merge field library
 */

import { useState } from "react";
import { CategorySidebar } from "./CategorySidebar";
import { MergeFieldSearch } from "./MergeFieldSearch";
import { MergeFieldGrid } from "./MergeFieldGrid";
import { useMergeFields, useMergeFieldCategories } from "@/hooks/v2";
import type { MergeField } from "@/types/v2";

interface FlettekodeLibraryProps {
  initialCategory?: string;
  onCopy?: (field: MergeField) => void;
}

export function FlettekodeLibrary({ initialCategory, onCopy }: FlettekodeLibraryProps) {
  const [selectedCategory, setSelectedCategory] = useState<string | null>(
    initialCategory || null
  );
  const [searchQuery, setSearchQuery] = useState("");

  const { categories, isLoading: categoriesLoading } = useMergeFieldCategories();
  const { fields, total, isLoading: fieldsLoading, page, totalPages } = useMergeFields({
    category: selectedCategory || undefined,
    search: searchQuery || undefined,
    perPage: 50,
  });

  const handleFieldClick = (field: MergeField) => {
    // Copy to clipboard
    navigator.clipboard.writeText(`[[${field.path}]]`);
    onCopy?.(field);
  };

  return (
    <div className="flex gap-6 h-full">
      {/* Sidebar */}
      <aside className="shrink-0">
        <CategorySidebar
          categories={categories}
          selectedCategory={selectedCategory}
          onSelect={setSelectedCategory}
          isLoading={categoriesLoading}
        />
      </aside>

      {/* Main content */}
      <main className="flex-1 flex flex-col min-w-0">
        {/* Search */}
        <div className="mb-4">
          <MergeFieldSearch
            value={searchQuery}
            onChange={setSearchQuery}
            onSuggestionSelect={(field) => {
              handleFieldClick(field);
            }}
          />
        </div>

        {/* Grid */}
        <div className="flex-1 overflow-y-auto">
          <MergeFieldGrid
            fields={fields}
            isLoading={fieldsLoading}
            onFieldClick={handleFieldClick}
          />
        </div>

        {/* Footer */}
        <div className="mt-4 text-sm text-gray-500">
          {total} flettekoder funnet
          {totalPages > 1 && ` • Side ${page} av ${totalPages}`}
        </div>
      </main>
    </div>
  );
}
