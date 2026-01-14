"use client";

/**
 * MergeFieldCard - Individual merge field card with copy functionality
 */

import { useState } from "react";
import { Copy, Check, Repeat } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import type { MergeField } from "@/types/v2";

interface MergeFieldCardProps {
  field: MergeField;
  onClick?: () => void;
  onCopy?: (syntax: string) => void;
  showUsageCount?: boolean;
}

export function MergeFieldCard({
  field,
  onClick,
  onCopy,
  showUsageCount = true,
}: MergeFieldCardProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async (e: React.MouseEvent) => {
    e.stopPropagation();
    const mergeFieldSyntax = `[[${field.path}]]`;
    
    try {
      await navigator.clipboard.writeText(mergeFieldSyntax);
      setCopied(true);
      onCopy?.(mergeFieldSyntax);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("Failed to copy:", err);
    }
  };

  return (
    <div
      className={cn(
        "flex flex-col rounded-lg border bg-white p-3 transition-all duration-200",
        "hover:shadow-md hover:border-primary/50",
        onClick && "cursor-pointer"
      )}
      onClick={onClick}
    >
      {/* Header */}
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center gap-2">
          <h4 className="font-medium text-gray-900">{field.label}</h4>
          {field.is_iterable && (
            <Badge variant="outline" className="gap-1 text-xs">
              <Repeat className="h-3 w-3" />
              Loop
            </Badge>
          )}
        </div>
        <Button
          variant="ghost"
          size="icon"
          className={cn(
            "h-8 w-8 shrink-0",
            copied ? "text-green-500" : "text-gray-400 hover:text-gray-900"
          )}
          onClick={handleCopy}
          title="Kopier til utklippstavle"
        >
          {copied ? (
            <Check className="h-4 w-4" />
          ) : (
            <Copy className="h-4 w-4" />
          )}
        </Button>
      </div>

      {/* Path/Code - clickable for quick copy */}
      <button
        className="mt-2 block w-full text-left rounded bg-gray-100 hover:bg-gray-200 px-2 py-1.5 text-xs font-mono text-gray-800 transition-colors"
        onClick={handleCopy}
        title="Klikk for å kopiere"
      >
        [[{field.path}]]
      </button>

      {/* Description and example */}
      {(field.description || field.example_value) && (
        <div className="mt-2 text-xs text-gray-500 space-y-1">
          {field.description && <p>{field.description}</p>}
          {field.example_value && (
            <p className="italic">
              <span className="text-gray-400">Eksempel:</span> {field.example_value}
            </p>
          )}
        </div>
      )}

      {/* Footer with usage count and data type */}
      <div className="mt-2 pt-2 border-t flex items-center justify-between">
        <Badge variant="secondary" className="text-xs">
          {field.data_type}
        </Badge>
        {showUsageCount && field.usage_count > 0 && (
          <span className="text-xs text-gray-400">
            Brukt {field.usage_count} ganger
          </span>
        )}
      </div>
    </div>
  );
}
