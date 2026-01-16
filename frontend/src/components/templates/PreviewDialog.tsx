"use client";

import { useEffect, useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { TemplatePreview } from "./TemplatePreview";
import { templateApi } from "@/lib/api";
import type { Template } from "@/types";

interface PreviewDialogProps {
  template: Template | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function PreviewDialog({
  template,
  open,
  onOpenChange,
}: PreviewDialogProps) {
  const [content, setContent] = useState<string>("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (open && template) {
      loadContent(template.id);
    } else {
      // Reset state when dialog closes
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
      const errorMessage = err instanceof Error ? err.message : "Kunne ikke laste innhold";
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  // Check if template supports preview
  const isHtmlTemplate = template?.file_type === "html" || template?.file_type === "htm";

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-6xl h-[90vh] flex flex-col p-0 gap-0">
        <DialogHeader className="px-6 py-4 border-b shrink-0">
          <DialogTitle className="flex items-center gap-2">
            <span>Forhåndsvisning</span>
            {template && (
              <span className="text-sm font-normal text-slate-500">
                — {template.title}
              </span>
            )}
          </DialogTitle>
        </DialogHeader>
        
        <div className="flex-1 overflow-hidden">
          {!isHtmlTemplate ? (
            <div className="flex items-center justify-center h-full bg-amber-50">
              <div className="text-center p-8">
                <p className="text-amber-700 font-medium mb-2">
                  Forhåndsvisning ikke tilgjengelig
                </p>
                <p className="text-amber-600 text-sm">
                  Kun HTML-maler kan forhåndsvises. Denne malen er av typen{" "}
                  <span className="font-mono bg-amber-100 px-1 rounded">
                    {template?.file_type}
                  </span>
                </p>
              </div>
            </div>
          ) : (
            <TemplatePreview
              content={content}
              title={template?.title}
              isLoading={isLoading}
              error={error || undefined}
            />
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}



