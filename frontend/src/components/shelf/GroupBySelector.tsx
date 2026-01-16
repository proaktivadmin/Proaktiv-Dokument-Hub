"use client";

/**
 * GroupBySelector - Dropdown for selecting grouping mode
 */

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import type { ShelfGroupBy } from "@/types/v2";

interface GroupBySelectorProps {
  value: ShelfGroupBy;
  onChange: (groupBy: ShelfGroupBy) => void;
}

const GROUP_OPTIONS: { value: ShelfGroupBy; label: string }[] = [
  { value: "channel", label: "Kanal" },
  { value: "phase", label: "Fase" },
  { value: "receiver", label: "Mottaker" },
  { value: "ownership_type", label: "Eierform" },
  { value: "category", label: "Kategori" },
];

export function GroupBySelector({ value, onChange }: GroupBySelectorProps) {
  return (
    <div className="flex items-center gap-2">
      <span className="text-sm text-gray-500">Grupper etter:</span>
      <Select value={value} onValueChange={(v) => onChange(v as ShelfGroupBy)}>
        <SelectTrigger className="w-[140px] bg-white/80 backdrop-blur-sm">
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          {GROUP_OPTIONS.map((option) => (
            <SelectItem key={option.value} value={option.value}>
              {option.label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}
