"use client";

/**
 * MergeFieldGrid - Grid of merge field cards
 */

import { MergeFieldCard } from "./MergeFieldCard";
import { Skeleton } from "@/components/ui/skeleton";
import type { MergeField } from "@/types/v2";

interface MergeFieldGridProps {
  fields: MergeField[];
  isLoading?: boolean;
  onFieldClick?: (field: MergeField) => void;
}

export function MergeFieldGrid({
  fields,
  isLoading = false,
  onFieldClick,
}: MergeFieldGridProps) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {Array.from({ length: 9 }).map((_, i) => (
          <Skeleton key={i} className="h-32 rounded-lg" />
        ))}
      </div>
    );
  }

  if (fields.length === 0) {
    return (
      <div className="flex items-center justify-center py-12 text-gray-500">
        Ingen flettekoder funnet
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      {fields.map((field) => (
        <MergeFieldCard
          key={field.id}
          field={field}
          onClick={onFieldClick ? () => onFieldClick(field) : undefined}
        />
      ))}
    </div>
  );
}
