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
  pdf: "bg-blue-100 text-blue-700",
  email: "bg-green-100 text-green-700",
  sms: "bg-purple-100 text-purple-700",
  pdf_email: "bg-amber-100 text-amber-700",
};

// File type icons for non-HTML templates
const FILE_TYPE_ICONS: Record<string, React.ReactNode> = {
  pdf: <FileText className="h-12 w-12 text-red-400" />,
  docx: <FileType className="h-12 w-12 text-blue-400" />,
  doc: <FileType className="h-12 w-12 text-blue-400" />,
  xlsx: <FileSpreadsheet className="h-12 w-12 text-green-400" />,
  xls: <FileSpreadsheet className="h-12 w-12 text-green-400" />,
};

export function TemplateCard({
  template,
  width = 160,
  height = 200,
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
      transform: scale(0.15);
      width: 666.67%;
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
  }, [canPreview]);

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

  const loadPreviewContent = async () => {
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
  };

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
        "flex flex-col rounded-lg border bg-white transition-all duration-200 cursor-pointer",
        "hover:shadow-lg hover:border-primary/50",
        isDimmed && "opacity-30",
        isSelected && "ring-2 ring-primary border-primary"
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
            {onCodeViewClick && (
              <Button
                size="icon"
                variant="secondary"
                className="h-8 w-8"
                onClick={(e) => {
                  e.stopPropagation();
                  onCodeViewClick();
                }}
              >
                <Code className="h-4 w-4" />
              </Button>
            )}
          </div>
        )}

        {/* Channel badge */}
        <Badge
          className={cn(
            "absolute right-2 top-2 gap-1 text-xs",
            CHANNEL_COLORS[template.channel]
          )}
        >
          {CHANNEL_ICONS[template.channel]}
          {template.channel === "pdf_email" ? "PDF" : template.channel.toUpperCase()}
        </Badge>

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
      <div className="flex flex-col gap-1 p-2">
        <h4 className="truncate text-sm font-medium text-gray-900" title={template.title}>
          {template.title}
        </h4>
        <span className="text-xs text-gray-500">
          v{template.version} • {template.status}
        </span>
      </div>
    </div>
  );
}
