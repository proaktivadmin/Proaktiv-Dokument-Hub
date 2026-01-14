"use client";

import { useEffect, useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { TemplatePreview } from "./TemplatePreview";
import { TemplateSettingsPanel, type TemplateSettings } from "./TemplateSettingsPanel";
import { SimulatorPanel } from "./SimulatorPanel";
import { CodeEditor } from "@/components/editor/CodeEditor";
import { templateApi } from "@/lib/api";
import {
  Download,
  Pencil,
  FileText,
  Calendar,
  HardDrive,
  Tag,
  FolderOpen,
  Eye,
  Settings,
  Play,
  Code,
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
  const [originalContent, setOriginalContent] = useState<string>("");
  const [processedContent, setProcessedContent] = useState<string | null>(null);
  const [testDataEnabled, setTestDataEnabled] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState("preview");
  
  // Derived content: show processed if test data enabled, otherwise original
  const content = testDataEnabled && processedContent ? processedContent : originalContent;

  // Load content when dialog opens with an HTML template
  useEffect(() => {
    if (open && template && canPreview(template.file_type)) {
      loadContent(template.id);
    } else {
      setOriginalContent("");
      setProcessedContent(null);
      setTestDataEnabled(false);
      setError(null);
    }
  }, [open, template]);

  const loadContent = async (templateId: string) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await templateApi.getContent(templateId);
      setOriginalContent(response.content);
      setProcessedContent(null);
      setTestDataEnabled(false);
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
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-5xl h-[85vh] flex flex-col p-0 gap-0">
        {/* Header */}
        <DialogHeader className="px-6 py-4 border-b shrink-0">
          <div className="flex items-center justify-between">
            <div>
              <DialogTitle className="flex items-center gap-2 text-lg">
                <FileText className="h-5 w-5 text-primary" />
                {template.title}
              </DialogTitle>
              <DialogDescription className="flex items-center gap-2 mt-1">
                {template.file_name}
                {getStatusBadge(template.status)}
              </DialogDescription>
            </div>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => onDownload?.(template)}
              >
                <Download className="h-4 w-4 mr-2" />
                Last ned
              </Button>
              <Button
                size="sm"
                onClick={() => onEdit?.(template)}
              >
                <Pencil className="h-4 w-4 mr-2" />
                Rediger
              </Button>
            </div>
          </div>
        </DialogHeader>

        {/* Tabs for different views */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col overflow-hidden">
          <div className="border-b px-6">
            <TabsList className="h-10">
              <TabsTrigger value="preview" className="gap-2">
                <Eye className="h-4 w-4" />
                Forhåndsvisning
              </TabsTrigger>
              <TabsTrigger value="code" className="gap-2">
                <Code className="h-4 w-4" />
                Kode
              </TabsTrigger>
              <TabsTrigger value="settings" className="gap-2">
                <Settings className="h-4 w-4" />
                Innstillinger
              </TabsTrigger>
              <TabsTrigger value="simulator" className="gap-2">
                <Play className="h-4 w-4" />
                Simulator
              </TabsTrigger>
            </TabsList>
          </div>

          {/* Preview Tab */}
          <TabsContent value="preview" className="flex-1 m-0 overflow-hidden">
            {canPreview(template.file_type) ? (
              <TemplatePreview
                content={content}
                title={template.title}
                isLoading={isLoading}
                error={error || undefined}
                testDataEnabled={testDataEnabled}
                hasProcessedData={!!processedContent}
                onToggleTestData={() => setTestDataEnabled(!testDataEnabled)}
              />
            ) : (
              <div className="flex items-center justify-center h-full bg-gray-50">
                <div className="text-center p-8">
                  <FileText className="h-16 w-16 mx-auto mb-4 text-gray-300" />
                  <p className="text-gray-600 font-medium mb-2">
                    Forhåndsvisning ikke tilgjengelig
                  </p>
                  <p className="text-sm text-gray-500">
                    Kun HTML-maler kan forhåndsvises.
                  </p>
                </div>
              </div>
            )}
          </TabsContent>

          {/* Code Tab - Monaco Editor */}
          <TabsContent value="code" className="flex-1 m-0 overflow-hidden">
            {isLoading ? (
              <div className="h-full flex items-center justify-center bg-gray-900 text-gray-400">
                Laster kode...
              </div>
            ) : error ? (
              <div className="h-full flex items-center justify-center bg-gray-900 text-red-400">
                {error}
              </div>
            ) : originalContent ? (
              <CodeEditor
                value={originalContent}
                onChange={(newContent) => {
                  setOriginalContent(newContent);
                  // Clear processed content since original changed
                  setProcessedContent(null);
                  setTestDataEnabled(false);
                }}
                language="html"
                theme="vs-dark"
                onSave={async (value) => {
                  // TODO: Implement save to backend
                  console.log("Save triggered:", value.length, "chars");
                }}
              />
            ) : (
              <div className="h-full flex items-center justify-center bg-gray-900 text-gray-400">
                Ingen kode tilgjengelig
              </div>
            )}
          </TabsContent>

          {/* Settings Tab */}
          <TabsContent value="settings" className="flex-1 m-0 overflow-auto p-6">
            <div className="max-w-xl mx-auto">
              <TemplateSettingsPanel
                templateId={template.id}
                onSave={async (settings: TemplateSettings) => {
                  // TODO: Implement settings save via API
                  console.log("Saving settings:", settings);
                }}
              />
            </div>
          </TabsContent>

          {/* Simulator Tab */}
          <TabsContent value="simulator" className="flex-1 m-0 overflow-hidden">
            <SimulatorPanel
              content={originalContent}
              onApplyTestData={(processed) => {
                // Store the processed content
                setProcessedContent(processed);
                // Enable test data mode
                setTestDataEnabled(true);
                // Switch to preview tab to show result
                setActiveTab("preview");
              }}
            />
          </TabsContent>
        </Tabs>

        {/* Metadata Footer */}
        <div className="border-t px-6 py-3 bg-gray-50 shrink-0">
          <div className="flex flex-wrap items-center gap-4 text-sm text-gray-600">
            <div className="flex items-center gap-1">
              <HardDrive className="h-4 w-4 text-gray-400" />
              {formatFileSize(template.file_size_bytes)}
            </div>
            <div className="flex items-center gap-1">
              <Calendar className="h-4 w-4 text-gray-400" />
              {formatDate(template.updated_at)}
            </div>
            {template.categories.length > 0 && (
              <div className="flex items-center gap-1">
                <FolderOpen className="h-4 w-4 text-gray-400" />
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
            )}
            {template.tags.length > 0 && (
              <div className="flex items-center gap-1">
                <Tag className="h-4 w-4 text-gray-400" />
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
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
