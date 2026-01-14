"use client";

/**
 * MergeFieldSearch - Search input with autocomplete suggestions
 */

import { useState, useRef, useEffect } from "react";
import { Search } from "lucide-react";
import { Input } from "@/components/ui/input";
import { useMergeFieldAutocomplete } from "@/hooks/v2";
import { cn } from "@/lib/utils";
import type { MergeField } from "@/types/v2";

interface MergeFieldSearchProps {
  value: string;
  onChange: (value: string) => void;
  onSuggestionSelect?: (field: MergeField) => void;
  placeholder?: string;
}

export function MergeFieldSearch({
  value,
  onChange,
  onSuggestionSelect,
  placeholder = "Søk flettekoder...",
}: MergeFieldSearchProps) {
  const [isFocused, setIsFocused] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const { suggestions, isLoading } = useMergeFieldAutocomplete(value);

  const showDropdown = isFocused && suggestions.length > 0;

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(e.target as Node) &&
        inputRef.current &&
        !inputRef.current.contains(e.target as Node)
      ) {
        setIsFocused(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleSuggestionClick = (field: MergeField) => {
    onChange(field.path);
    setIsFocused(false);
    onSuggestionSelect?.(field);
  };

  return (
    <div className="relative">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
        <Input
          ref={inputRef}
          type="search"
          placeholder={placeholder}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onFocus={() => setIsFocused(true)}
          className="pl-10 bg-white/80 backdrop-blur-sm"
        />
        {isLoading && (
          <div className="absolute right-3 top-1/2 -translate-y-1/2">
            <div className="h-4 w-4 animate-spin rounded-full border-2 border-gray-300 border-t-[#BCAB8A]" />
          </div>
        )}
      </div>

      {/* Suggestions dropdown */}
      {showDropdown && (
        <div
          ref={dropdownRef}
          className="absolute z-50 mt-1 w-full rounded-lg border bg-white shadow-lg max-h-64 overflow-y-auto"
        >
          {suggestions.map((field) => (
            <button
              key={field.id}
              className={cn(
                "w-full flex flex-col items-start px-4 py-2 text-left hover:bg-gray-50",
                "border-b last:border-b-0"
              )}
              onClick={() => handleSuggestionClick(field)}
            >
              <div className="flex items-center gap-2">
                <span className="font-medium text-[#272630]">{field.label}</span>
                <code className="text-xs text-gray-500 bg-gray-100 px-1 rounded">
                  {field.path}
                </code>
              </div>
              {field.description && (
                <span className="text-xs text-gray-500 mt-0.5">
                  {field.description}
                </span>
              )}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
