"use client";

/**
 * ShelfRow - A single shelf (swimlane) containing grouped templates
 * Uses wrapped grid layout for better space utilization
 */

import { ShelfHeader } from "./ShelfHeader";
import { TemplateCard } from "./TemplateCard";
import { cn } from "@/lib/utils";
import type { ShelfGroup, TemplateWithMetadata } from "@/types/v2";

interface ShelfRowProps {
  shelf: ShelfGroup;
  dimNonMatching?: boolean;
  matchingIds?: Set<string>;
  onTemplateClick: (template: TemplateWithMetadata) => void;
  onToggleCollapse: (shelfId: string) => void;
  onTemplateSettings?: (template: TemplateWithMetadata) => void;
  onTemplateCodeView?: (template: TemplateWithMetadata) => void;
  onTemplatePreview?: (template: TemplateWithMetadata) => void;
  onTemplateEdit?: (template: TemplateWithMetadata) => void;
  onTemplateDownload?: (template: TemplateWithMetadata) => void;
  onTemplateDelete?: (template: TemplateWithMetadata) => void;
}

export function ShelfRow({
  shelf,
  dimNonMatching = false,
  matchingIds,
  onTemplateClick,
  onToggleCollapse,
  onTemplateSettings,
  onTemplateCodeView,
  onTemplatePreview,
  onTemplateEdit,
  onTemplateDownload,
  onTemplateDelete,
}: ShelfRowProps) {
  return (
    <div className={cn("mb-6", shelf.isCollapsed && "mb-2")}>
      <ShelfHeader
        title={shelf.label}
        count={shelf.count}
        isCollapsed={shelf.isCollapsed}
        onToggle={() => onToggleCollapse(shelf.id)}
      />

      {!shelf.isCollapsed && (
        <div className="flex flex-wrap gap-4 py-2">
          {shelf.templates.map((template) => {
            const isDimmed =
              dimNonMatching && matchingIds && !matchingIds.has(template.id);

            return (
              <TemplateCard
                key={template.id}
                template={template}
                isDimmed={isDimmed}
                onClick={() => onTemplateClick(template)}
                onSettingsClick={
                  onTemplateSettings
                    ? () => onTemplateSettings(template)
                    : undefined
                }
                onCodeViewClick={
                  onTemplateCodeView
                    ? () => onTemplateCodeView(template)
                    : undefined
                }
                onPreview={
                  onTemplatePreview
                    ? () => onTemplatePreview(template)
                    : undefined
                }
                onEdit={
                  onTemplateEdit
                    ? () => onTemplateEdit(template)
                    : undefined
                }
                onDownload={
                  onTemplateDownload
                    ? () => onTemplateDownload(template)
                    : undefined
                }
                onDelete={
                  onTemplateDelete
                    ? () => onTemplateDelete(template)
                    : undefined
                }
              />
            );
          })}
        </div>
      )}
    </div>
  );
}
