"use client";

import { useEffect, useState } from "react";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
  SheetFooter,
} from "@/components/ui/sheet";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { TemplatePreview } from "./TemplatePreview";
import { templateApi } from "@/lib/api";
import {
  Download,
  Pencil,
  FileText,
  Calendar,
  HardDrive,
  Tag,
  FolderOpen,
} from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import { nb } from "date-fns/locale";
import type { Template } from "@/types";

interface TemplateDetailSheetProps {
  template: Template | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onEdit?: (template: Template) => void;
  onDownload?: (template: Template) => void;
}

export function TemplateDetailSheet({
  template,
  open,
  onOpenChange,
  onEdit,
  onDownload,
}: TemplateDetailSheetProps) {
  const [content, setContent] = useState<string>("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load content when sheet opens with an HTML template
  useEffect(() => {
    if (open && template && canPreview(template.file_type)) {
      loadContent(template.id);
    } else {
      setContent("");
      setError(null);
    }
  }, [open, template]);

  const loadContent = async (templateId: string) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await templateApi.getContent(templateId);
      setContent(response.content);
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Kunne ikke laste innhold";
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const canPreview = (fileType: string) => {
    return fileType === "html" || fileType === "htm";
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return "Ukjent";
    try {
      return formatDistanceToNow(new Date(dateString), {
        addSuffix: true,
        locale: nb,
      });
    } catch {
      return "Ukjent";
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "published":
        return (
          <Badge className="bg-green-100 text-green-700 hover:bg-green-100">
            Publisert
          </Badge>
        );
      case "draft":
        return (
          <Badge className="bg-amber-100 text-amber-700 hover:bg-amber-100">
            Utkast
          </Badge>
        );
      default:
        return (
          <Badge className="bg-muted text-muted-foreground hover:bg-muted">
            {status}
          </Badge>
        );
    }
  };

  if (!template) return null;

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent className="w-full sm:max-w-2xl flex flex-col p-0 gap-0">
        <SheetHeader className="px-6 py-4 border-b shrink-0">
          <SheetTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5 text-muted-foreground" />
            {template.title}
          </SheetTitle>
          <SheetDescription className="flex items-center gap-2">
            {template.file_name}
            {getStatusBadge(template.status)}
          </SheetDescription>
        </SheetHeader>

        {/* Preview Area */}
        <div className="flex-1 overflow-hidden">
          {canPreview(template.file_type) ? (
            <TemplatePreview
              content={content}
              title={template.title}
              isLoading={isLoading}
              error={error || undefined}
            />
          ) : (
            <div className="flex items-center justify-center h-full bg-muted">
              <div className="text-center p-8">
                <FileText className="h-16 w-16 mx-auto mb-4 text-muted-foreground opacity-50" />
                <p className="text-muted-foreground font-medium mb-2">
                  Forhåndsvisning ikke tilgjengelig
                </p>
                <p className="text-sm text-muted-foreground">
                  Kun HTML-maler kan forhåndsvises.
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Metadata Section */}
        <div className="border-t px-6 py-4 bg-muted/30 shrink-0">
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div className="flex items-center gap-2">
              <HardDrive className="h-4 w-4 text-muted-foreground" />
              <span className="text-muted-foreground">Størrelse:</span>
              <span className="font-medium">
                {formatFileSize(template.file_size_bytes)}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <Calendar className="h-4 w-4 text-muted-foreground" />
              <span className="text-muted-foreground">Oppdatert:</span>
              <span className="font-medium">
                {formatDate(template.updated_at)}
              </span>
            </div>
            {template.categories.length > 0 && (
              <div className="flex items-center gap-2 col-span-2">
                <FolderOpen className="h-4 w-4 text-muted-foreground" />
                <span className="text-muted-foreground">Kategorier:</span>
                <div className="flex gap-1 flex-wrap">
                  {template.categories.map((cat) => (
                    <Badge
                      key={cat.id}
                      variant="secondary"
                      className="text-xs"
                    >
                      {cat.icon && <span className="mr-1">{cat.icon}</span>}
                      {cat.name}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
            {template.tags.length > 0 && (
              <div className="flex items-center gap-2 col-span-2">
                <Tag className="h-4 w-4 text-muted-foreground" />
                <span className="text-muted-foreground">Tags:</span>
                <div className="flex gap-1 flex-wrap">
                  {template.tags.map((tag) => (
                    <Badge
                      key={tag.id}
                      style={{ backgroundColor: tag.color }}
                      className="text-xs text-white"
                    >
                      {tag.name}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
          </div>
          {template.description && (
            <p className="mt-3 text-sm text-muted-foreground">
              {template.description}
            </p>
          )}
        </div>

        {/* Footer Actions */}
        <SheetFooter className="border-t px-6 py-4 shrink-0">
          <div className="flex gap-2 w-full">
            <Button
              variant="outline"
              className="flex-1"
              onClick={() => onDownload?.(template)}
            >
              <Download className="h-4 w-4 mr-2" />
              Last ned
            </Button>
            <Button
              className="flex-1 bg-secondary text-secondary-foreground hover:bg-secondary/90"
              onClick={() => onEdit?.(template)}
            >
              <Pencil className="h-4 w-4 mr-2" />
              Rediger
            </Button>
          </div>
        </SheetFooter>
      </SheetContent>
    </Sheet>
  );
}
