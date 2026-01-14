"use client";

/**
 * CategorySidebar - Category filter sidebar for merge fields
 */

import { cn } from "@/lib/utils";
import { Skeleton } from "@/components/ui/skeleton";
import type { MergeFieldCategoryCount } from "@/types/v2";

interface CategorySidebarProps {
  categories: MergeFieldCategoryCount[];
  selectedCategory: string | null;
  onSelect: (category: string | null) => void;
  isLoading?: boolean;
}

export function CategorySidebar({
  categories,
  selectedCategory,
  onSelect,
  isLoading = false,
}: CategorySidebarProps) {
  if (isLoading) {
    return (
      <div className="w-48 space-y-2">
        {Array.from({ length: 7 }).map((_, i) => (
          <Skeleton key={i} className="h-10 w-full" />
        ))}
      </div>
    );
  }

  return (
    <nav className="w-48 space-y-1">
      {/* All categories option */}
      <button
        className={cn(
          "w-full flex items-center justify-between px-3 py-2 rounded-lg text-sm transition-colors",
          selectedCategory === null
            ? "bg-[#BCAB8A]/20 text-[#272630] font-medium"
            : "text-gray-600 hover:bg-gray-100"
        )}
        onClick={() => onSelect(null)}
      >
        <span>Alle</span>
      </button>

      {/* Category list */}
      {categories.map((category) => (
        <button
          key={category.name}
          className={cn(
            "w-full flex items-center justify-between px-3 py-2 rounded-lg text-sm transition-colors",
            selectedCategory === category.name
              ? "bg-[#BCAB8A]/20 text-[#272630] font-medium"
              : "text-gray-600 hover:bg-gray-100"
          )}
          onClick={() => onSelect(category.name)}
        >
          <span>{category.name}</span>
          {category.count > 0 && (
            <span className="text-xs text-gray-400">{category.count}</span>
          )}
        </button>
      ))}
    </nav>
  );
}
