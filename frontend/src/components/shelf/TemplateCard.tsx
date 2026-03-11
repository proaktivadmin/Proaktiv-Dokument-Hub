"use client";

/**
 * TemplateCard - Individual template card for shelf display
 * Now includes live document preview for HTML templates
 */

import { useState, useEffect, useRef, useCallback } from "react";
import {
  Settings,
  Code,
  FileText,
  FileSpreadsheet,
  FileType,
  Mail,
  MessageSquare,
  MoreHorizontal,
  Eye,
  Download,
  Pencil,
  Trash2,
  Loader2,
  Paperclip,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { cn } from "@/lib/utils";
import { templateApi } from "@/lib/api";
import type { TemplateWithMetadata, TemplateChannel } from "@/types/v2";

interface TemplateCardProps {
  template: TemplateWithMetadata;
  width?: number;
  height?: number;
  isDimmed?: boolean;
  isSelected?: boolean;
  onClick?: () => void;
  onSettingsClick?: () => void;
  onCodeViewClick?: () => void;
  onPreview?: () => void;
  onEdit?: () => void;
  onDownload?: () => void;
  onDelete?: () => void;
}

const CHANNEL_ICONS: Record<TemplateChannel, React.ReactNode> = {
  pdf: <FileText className="h-3 w-3" />,
  email: <Mail className="h-3 w-3" />,
  sms: <MessageSquare className="h-3 w-3" />,
  pdf_email: <FileText className="h-3 w-3" />,
};

const CHANNEL_COLORS: Record<TemplateChannel, string> = {
  pdf: "bg-[#F5EDE1] text-[#8A5A2B]",
  email: "bg-[#E6EEF9] text-[#1E40AF]",
  sms: "bg-[#EFE8F8] text-[#6D28D9]",
  pdf_email: "bg-[#EEEAF7] text-[#4338CA]",
};

// File type icons for non-HTML templates
const FILE_TYPE_ICONS: Record<string, React.ReactNode> = {
  pdf: <FileText className="h-12 w-12 text-red-400" />,
  docx: <FileType className="h-12 w-12 text-blue-400" />,
  doc: <FileType className="h-12 w-12 text-blue-400" />,
  xlsx: <FileSpreadsheet className="h-12 w-12 text-green-400" />,
  xls: <FileSpreadsheet className="h-12 w-12 text-green-400" />,
};

const WORKFLOW_BADGE_STYLES: Record<string, string> = {
  draft: "bg-gray-100 text-gray-600",
  in_review: "bg-amber-50 text-amber-700",
  published: "bg-emerald-50 text-emerald-700",
  archived: "bg-slate-100 text-slate-600",
};

const WORKFLOW_LABELS: Record<string, string> = {
  draft: "Utkast",
  in_review: "Til godkj.",
  published: "Publisert",
  archived: "Arkivert",
};

function WorkflowBadge({ template }: { template: TemplateWithMetadata }) {
  const ws = (template as unknown as Record<string, unknown>).workflow_status as string | undefined;
  const isLegacy = (template as unknown as Record<string, unknown>).is_archived_legacy as boolean | undefined;
  const status = ws || template.status;
  const style = WORKFLOW_BADGE_STYLES[status] || WORKFLOW_BADGE_STYLES.draft;
  const label = WORKFLOW_LABELS[status] || status;

  return (
    <span className="flex items-center gap-1">
      <Badge className={cn("text-[10px]", style)}>{label}</Badge>
      {isLegacy && <Badge className="text-[10px] bg-slate-200 text-slate-500">Arv</Badge>}
    </span>
  );
}

export function TemplateCard({
  template,
  width = 200,
  height = 250,
  isDimmed = false,
  isSelected = false,
  onClick,
  onSettingsClick,
  onCodeViewClick,
  onPreview,
  onEdit,
  onDownload,
  onDelete,
}: TemplateCardProps) {
  const [isHovered, setIsHovered] = useState(false);
  const [previewContent, setPreviewContent] = useState<string | null>(null);
  const [isLoadingPreview, setIsLoadingPreview] = useState(false);
  const [previewError, setPreviewError] = useState(false);
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const cardRef = useRef<HTMLDivElement>(null);
  const hasAttemptedLoad = useRef(false);
  const attachmentNames = (template.attachments ?? []).filter(Boolean);
  const hasAttachments = attachmentNames.length > 0;
  const originTags = (template.tags ?? [])
    .map((tag) => tag.name.trim().toLowerCase())
    .filter(Boolean);
  const isKundemal = originTags.some((tag) => tag.includes("kundemal"));
  const isVitec = originTags.some((tag) => tag.includes("vitec"));
  const originLabel = isKundemal ? "Kundemal" : isVitec ? "Vitec Next" : null;
  const originBadgeClass = isKundemal
    ? "bg-[#E7F5EC] text-[#166534]"
    : "bg-[#E6EEF9] text-[#1E40AF]";
  const channelLabel = template.channel === "pdf_email" ? "PDF" : template.channel.toUpperCase();

  const canPreview = template.file_type === "html" || template.file_type === "htm";

  // Build the preview document for the iframe
  const buildPreviewDocument = useCallback((content: string): string => {
    return `<!DOCTYPE html>
<html lang="no">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link rel="stylesheet" href="/vitec-stilark.css" />
  <style>
    body {
      transform-origin: top left;
      transform: scale(0.2);
      width: 500%;
      pointer-events: none;
      overflow: hidden;
    }
  </style>
</head>
<body class="vitec-preview-mode">
  ${content}
</body>
</html>`;
  }, []);

  const loadPreviewContent = useCallback(async () => {
    setIsLoadingPreview(true);
    setPreviewError(false);
    try {
      const response = await templateApi.getContent(template.id);
      setPreviewContent(response.content);
    } catch (error) {
      console.error("Failed to load preview:", error);
      setPreviewError(true);
    } finally {
      setIsLoadingPreview(false);
    }
  }, [template.id]);

  // Load preview content when card becomes visible
  useEffect(() => {
    if (!canPreview || hasAttemptedLoad.current) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting && !hasAttemptedLoad.current) {
            hasAttemptedLoad.current = true;
            loadPreviewContent();
          }
        });
      },
      { threshold: 0.1 }
    );

    if (cardRef.current) {
      observer.observe(cardRef.current);
    }

    return () => observer.disconnect();
  }, [canPreview, loadPreviewContent]);

  // Write content to iframe when loaded
  useEffect(() => {
    if (iframeRef.current && previewContent) {
      const doc = iframeRef.current.contentDocument;
      if (doc) {
        doc.open();
        doc.write(buildPreviewDocument(previewContent));
        doc.close();
      }
    }
  }, [previewContent, buildPreviewDocument]);



  // Render the thumbnail content based on state
  const renderThumbnail = () => {
    // Show static image thumbnail if available
    if (template.preview_thumbnail_url) {
      return (
        <img
          src={template.preview_thumbnail_url}
          alt={template.title}
          className="h-full w-full object-cover"
        />
      );
    }

    // For HTML templates, show live preview
    if (canPreview) {
      if (isLoadingPreview) {
        return (
          <div className="flex h-full items-center justify-center text-gray-400">
            <Loader2 className="h-8 w-8 animate-spin" />
          </div>
        );
      }

      if (previewError) {
        return (
          <div className="flex h-full items-center justify-center text-gray-300">
            <FileText className="h-12 w-12" />
          </div>
        );
      }

      if (previewContent) {
        return (
          <iframe
            ref={iframeRef}
            title={`Preview of ${template.title}`}
            className="w-full h-full border-0 pointer-events-none"
            sandbox="allow-same-origin"
            style={{ 
              minHeight: "100%",
              background: "white"
            }}
          />
        );
      }

      // Waiting to load (placeholder)
      return (
        <div className="flex h-full items-center justify-center text-gray-300 bg-gradient-to-b from-gray-50 to-gray-100">
          <FileText className="h-12 w-12 opacity-50" />
        </div>
      );
    }

    // For non-HTML files, show file type icon
    const icon = FILE_TYPE_ICONS[template.file_type] || (
      <FileText className="h-12 w-12 text-gray-300" />
    );

    return (
      <div className="flex h-full items-center justify-center bg-gradient-to-b from-gray-50 to-gray-100">
        {icon}
      </div>
    );
  };

  return (
    <div
      ref={cardRef}
      className={cn(
        "flex flex-col rounded-lg border bg-white shadow-card ring-1 ring-black/[0.03] transition-all duration-slow cursor-pointer",
        "hover:shadow-card-hover hover:-translate-y-0.5 hover:border-[#BCAB8A]",
        isDimmed && "opacity-30",
        isSelected && "ring-2 ring-strong border-[#BCAB8A] shadow-glow"
      )}
      style={{ width, height }}
      onClick={onClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Thumbnail area */}
      <div className="relative flex-1 overflow-hidden rounded-t-lg bg-gray-50">
        {renderThumbnail()}

        {/* Hover actions */}
        {isHovered && (
          <div className="absolute inset-0 flex items-center justify-center gap-2 bg-black/40">
            {onSettingsClick && (
              <Button
                size="icon"
                variant="secondary"
                className="h-8 w-8"
                onClick={(e) => {
                  e.stopPropagation();
                  onSettingsClick();
                }}
              >
                <Settings className="h-4 w-4" />
              </Button>
            )}
          </div>
        )}

        {/* Origin badge */}
        {originLabel && (
          <Badge className={cn("absolute right-2 top-2 text-xs", originBadgeClass)}>
            {originLabel}
          </Badge>
        )}

        {/* Dropdown menu (top-left) */}
        <div className="absolute left-2 top-2" onClick={(e) => e.stopPropagation()}>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="secondary"
                size="icon"
                className={cn(
                  "h-7 w-7 opacity-0 transition-opacity",
                  isHovered && "opacity-100"
                )}
              >
                <MoreHorizontal className="h-4 w-4" />
                <span className="sr-only">Åpne meny</span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="start">
              {canPreview && onPreview && (
                <DropdownMenuItem onClick={onPreview}>
                  <Eye className="mr-2 h-4 w-4" />
                  Forhåndsvis
                </DropdownMenuItem>
              )}
              {onCodeViewClick && (
                <DropdownMenuItem onClick={onCodeViewClick}>
                  <Code className="mr-2 h-4 w-4" />
                  Kode
                </DropdownMenuItem>
              )}
              {onDownload && (
                <DropdownMenuItem onClick={onDownload}>
                  <Download className="mr-2 h-4 w-4" />
                  Last ned
                </DropdownMenuItem>
              )}
              {onEdit && (
                <DropdownMenuItem onClick={onEdit}>
                  <Pencil className="mr-2 h-4 w-4" />
                  Rediger
                </DropdownMenuItem>
              )}
              {onDelete && (
                <>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem
                    onClick={onDelete}
                    className="text-red-600 focus:text-red-600 focus:bg-red-50"
                  >
                    <Trash2 className="mr-2 h-4 w-4" />
                    Slett
                  </DropdownMenuItem>
                </>
              )}
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>

      {/* Title area */}
      <div className="flex flex-col gap-1 px-2 pb-2 pt-1">
        <h4 className="truncate text-sm font-medium text-gray-900" title={template.title}>
          {template.title}
        </h4>
        <div className="text-xs text-gray-500 flex items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <Badge className={cn("gap-1 text-[10px]", CHANNEL_COLORS[template.channel])}>
              {CHANNEL_ICONS[template.channel]}
              {channelLabel}
            </Badge>
            <WorkflowBadge template={template} />
          </div>
          {hasAttachments && (
            <span
              className="inline-flex items-center gap-1"
              title={attachmentNames.join(", ")}
            >
              <Paperclip className="h-3 w-3" />
              {attachmentNames.length}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
