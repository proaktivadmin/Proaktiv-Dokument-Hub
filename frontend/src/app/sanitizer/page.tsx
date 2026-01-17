"use client";

/**
 * Sanitizer Page - Tool for stripping inline CSS from templates
 * Provides before/after preview and permanent save functionality
 */

import { useState, useEffect } from "react";
import { Wand2, Check, AlertTriangle } from "lucide-react";
import { Header } from "@/components/layout/Header";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { TemplatePreview } from "@/components/templates/TemplatePreview";
import { useTemplates } from "@/hooks/useTemplates";
import { templateApi } from "@/lib/api";
import { apiClient } from "@/lib/api/config";

interface ValidationResult {
  has_vitec_wrapper: boolean;
  has_resource_reference: boolean;
  has_legacy_font_tags: boolean;
  legacy_style_count: number;
  is_valid: boolean;
}

interface SanitizeResult {
  html: string;
  original_length: number;
  sanitized_length: number;
}

export default function SanitizerPage() {
  const { templates, isLoading: templatesLoading } = useTemplates({ per_page: 100 });
  const [selectedTemplateId, setSelectedTemplateId] = useState<string>("");
  const [originalContent, setOriginalContent] = useState<string>("");
  const [sanitizedContent, setSanitizedContent] = useState<string>("");
  const [validation, setValidation] = useState<ValidationResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saveSuccess, setSaveSuccess] = useState(false);

  // Filter to only HTML templates
  const htmlTemplates = templates.filter(
    (t) => t.file_type === "html" || t.file_type === "htm"
  );

  // Load template content when selected
  useEffect(() => {
    if (!selectedTemplateId) {
      setOriginalContent("");
      setSanitizedContent("");
      setValidation(null);
      return;
    }

    async function loadTemplate() {
      setIsLoading(true);
      setError(null);
      setSaveSuccess(false);

      try {
        const response = await templateApi.getContent(selectedTemplateId);
        setOriginalContent(response.content);
        setSanitizedContent("");
        setValidation(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Kunne ikke laste mal");
      } finally {
        setIsLoading(false);
      }
    }

    loadTemplate();
  }, [selectedTemplateId]);

  // Validate original content
  useEffect(() => {
    if (!originalContent) return;

    async function validateContent() {
      try {
        const response = await apiClient.post("/sanitize/validate", {
          html: originalContent,
        });
        setValidation(response.data);
      } catch (err) {
        console.error("Validation failed:", err);
      }
    }

    validateContent();
  }, [originalContent]);

  const handleSanitize = async () => {
    if (!originalContent || !selectedTemplateId) return;

    setIsLoading(true);
    setIsSaving(true);
    setError(null);
    setSaveSuccess(false);

    try {
      const response = await apiClient.post<SanitizeResult>("/sanitize/preview", {
        html: originalContent,
        update_resource: true,
        theme_class: "proaktiv-theme",
      });

      const sanitizedHtml = response.data.html;

      // Persist sanitized content immediately
      await apiClient.put(`/templates/${selectedTemplateId}/content`, {
        content: sanitizedHtml,
        auto_sanitize: false,
      });

      setSanitizedContent(sanitizedHtml);
      setOriginalContent(sanitizedHtml);
      setSaveSuccess(true);

      // Re-validate
      try {
        const valResponse = await apiClient.post("/sanitize/validate", {
          html: sanitizedHtml,
        });
        setValidation(valResponse.data);
      } catch {
        // Validation failure is not critical
      }
    } catch (err: unknown) {
      const errorMessage = err instanceof Error
        ? err.message
        : (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || "Sanitering feilet";
      setError(errorMessage);
    } finally {
      setIsLoading(false);
      setIsSaving(false);
    }
  };

  const selectedTemplate = templates.find((t) => t.id === selectedTemplateId);

  return (
    <div className="flex flex-col h-screen bg-background">
      <Header />

      {/* Page header */}
      <div className="border-b bg-white">
        <div className="container mx-auto px-6 py-6">
          <h2 className="text-2xl font-bold text-foreground">Sanitizer</h2>
          <p className="text-muted-foreground">Rens inline CSS fra maler og standardiser stilen</p>
        </div>
      </div>

      {/* Controls */}
      <div className="border-b bg-muted/30">
        <div className="container mx-auto px-6 py-4">
        <div className="flex items-end gap-4">
          <div className="flex-1 max-w-md space-y-2">
            <Label htmlFor="template-select">Velg mal</Label>
            <Select
              value={selectedTemplateId}
              onValueChange={setSelectedTemplateId}
              disabled={templatesLoading}
            >
              <SelectTrigger id="template-select">
                <SelectValue placeholder="Velg en HTML-mal..." />
              </SelectTrigger>
              <SelectContent>
                {htmlTemplates.map((template) => (
                  <SelectItem key={template.id} value={template.id}>
                    {template.title}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Validation status */}
          {validation && (
            <div className="flex items-center gap-2">
              {validation.is_valid ? (
                <Badge className="bg-green-100 text-green-700 gap-1">
                  <Check className="h-3 w-3" />
                  Gyldig
                </Badge>
              ) : (
                <Badge className="bg-amber-100 text-amber-700 gap-1">
                  <AlertTriangle className="h-3 w-3" />
                  Trenger sanitering
                </Badge>
              )}
              {validation.legacy_style_count > 0 && (
                <Badge variant="outline">
                  {validation.legacy_style_count} inline stiler
                </Badge>
              )}
              {validation.has_legacy_font_tags && (
                <Badge variant="outline">Har &lt;font&gt; tags</Badge>
              )}
            </div>
          )}

          <div className="flex items-center gap-3">
            <Button
              onClick={handleSanitize}
              disabled={!originalContent || isLoading || isSaving}
            >
              <Wand2 className="h-4 w-4 mr-2" />
              {isSaving ? "Saniterer og lagrer..." : "Sanitér og lagre"}
            </Button>
            <span className="text-sm text-muted-foreground">
              Endringen lagres permanent i malen.
            </span>
          </div>
        </div>

        {error && (
          <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-md text-red-700 text-sm">
            {error}
          </div>
        )}

        {saveSuccess && (
          <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-md text-green-700 text-sm flex items-center gap-2">
            <Check className="h-4 w-4" />
            Endringene ble lagret permanent!
          </div>
        )}
        </div>
      </div>

      {/* Preview area */}
      <div className="flex-1 flex overflow-hidden">
        {!selectedTemplateId ? (
          <div className="flex-1 flex items-center justify-center text-gray-500">
            <div className="text-center">
              <Wand2 className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p className="font-medium">Velg en mal for å starte</p>
              <p className="text-sm">Kun HTML-maler kan saniteres</p>
            </div>
          </div>
        ) : (
          <>
            {/* Original */}
            <div className="flex-1 flex flex-col border-r">
              <div className="px-4 py-2 border-b bg-gray-100 text-sm font-medium">
                Original
                {originalContent && (
                  <span className="text-gray-500 font-normal ml-2">
                    ({originalContent.length.toLocaleString()} tegn)
                  </span>
                )}
              </div>
              <div className="flex-1 overflow-hidden">
                <TemplatePreview
                  content={originalContent}
                  title={selectedTemplate?.title || "Original"}
                  isLoading={isLoading && !sanitizedContent}
                />
              </div>
            </div>

            {/* Sanitized */}
            <div className="flex-1 flex flex-col">
              <div className="px-4 py-2 border-b bg-gray-100 text-sm font-medium">
                Sanitert (lagret)
                {sanitizedContent && (
                  <span className="text-gray-500 font-normal ml-2">
                    ({sanitizedContent.length.toLocaleString()} tegn)
                    <span className="text-green-600 ml-1">
                      -{((1 - sanitizedContent.length / originalContent.length) * 100).toFixed(0)}%
                    </span>
                  </span>
                )}
              </div>
              <div className="flex-1 overflow-hidden">
                {sanitizedContent ? (
                  <TemplatePreview
                    content={sanitizedContent}
                    title={`${selectedTemplate?.title || "Sanitert"} (sanitert)`}
                  />
                ) : (
                  <div className="flex items-center justify-center h-full text-gray-400">
                    <div className="text-center">
                      <Wand2 className="h-8 w-8 mx-auto mb-2 opacity-50" />
                      <p>Klikk "Sanitér" for å se resultatet</p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
