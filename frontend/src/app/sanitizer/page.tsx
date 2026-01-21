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
import { TemplatePreview } from "@/components/templates/TemplatePreview";
import { useTemplates } from "@/hooks/useTemplates";
import { templateApi } from "@/lib/api";
import { templateSettingsApi } from "@/lib/api/template-settings";
import { apiClient } from "@/lib/api/config";
import type { UpdateTemplateSettingsResponse } from "@/types/v2";

interface ValidationResult {
  has_vitec_wrapper: boolean;
  has_resource_reference: boolean;
  has_legacy_font_tags: boolean;
  legacy_style_count: number;
  is_valid: boolean;
}

interface NormalizeResult {
  html: string;
  report: Record<string, number | boolean>;
}

export default function SanitizerPage() {
  const { templates, isLoading: templatesLoading } = useTemplates({ per_page: 100 });
  const [selectedTemplateId, setSelectedTemplateId] = useState<string>("");
  const [originalContent, setOriginalContent] = useState<string>("");
  const [validation, setValidation] = useState<ValidationResult | null>(null);
  const [normalizeReport, setNormalizeReport] = useState<Record<string, number | boolean> | null>(null);
  const [templateSettings, setTemplateSettings] = useState<UpdateTemplateSettingsResponse | null>(null);
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
      setValidation(null);
      setNormalizeReport(null);
      setTemplateSettings(null);
      return;
    }

    async function loadTemplate() {
      setIsLoading(true);
      setError(null);
      setSaveSuccess(false);

      try {
        const response = await templateApi.getContent(selectedTemplateId);
        setOriginalContent(response.content);
        setValidation(null);
        setNormalizeReport(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Kunne ikke laste mal");
      } finally {
        setIsLoading(false);
      }
    }

    loadTemplate();
  }, [selectedTemplateId]);

  // Load template settings (for channel warnings)
  useEffect(() => {
    if (!selectedTemplateId) return;

    async function loadSettings() {
      try {
        const settings = await templateSettingsApi.getSettings(selectedTemplateId);
        setTemplateSettings(settings);
      } catch {
        setTemplateSettings(null);
      }
    }

    loadSettings();
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

  const handleNormalize = async () => {
    if (!originalContent || !selectedTemplateId) return;

    setIsLoading(true);
    setIsSaving(true);
    setError(null);
    setSaveSuccess(false);

    try {
      const response = await apiClient.post<NormalizeResult>("/sanitize/normalize", {
        html: originalContent,
      });

      const normalizedHtml = response.data.html;

      // Persist normalized content immediately
      await apiClient.put(`/templates/${selectedTemplateId}/content`, {
        content: normalizedHtml,
        auto_sanitize: false,
      });

      setOriginalContent(normalizedHtml);
      setNormalizeReport(response.data.report || null);
      setSaveSuccess(true);

      // Re-validate
      try {
        const valResponse = await apiClient.post("/sanitize/validate", {
          html: normalizedHtml,
        });
        setValidation(valResponse.data);
      } catch {
        // Validation failure is not critical
      }
    } catch (err: unknown) {
      const errorMessage = err instanceof Error
        ? err.message
        : (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || "Normalisering feilet";
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
          <h2 className="text-2xl font-bold text-foreground">Normalisering til Vitec</h2>
          <p className="text-muted-foreground">
            Fjern Proaktiv-design og lagre malen i Vitec-standard (permanent)
          </p>
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
              onClick={handleNormalize}
              disabled={!originalContent || isLoading || isSaving}
            >
              <Wand2 className="h-4 w-4 mr-2" />
              {isSaving ? "Normaliserer og lagrer..." : "Normaliser til Vitec (lagre)"}
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

        {templateSettings?.channel && (templateSettings.channel === "email" || templateSettings.channel === "sms") && (
          <div className="mt-4 p-3 bg-amber-50 border border-amber-200 rounded-md text-amber-700 text-sm">
            <strong>Advarsel:</strong> Denne malen er for {templateSettings.channel.toUpperCase()}.
            Normalisering kan påvirke e-post/SMS layout.
          </div>
        )}

        {normalizeReport && (
          <div className="mt-4 p-3 bg-muted/50 border rounded-md text-sm">
            <p className="font-medium mb-2">Normaliseringsrapport</p>
            <div className="grid grid-cols-2 gap-2 text-muted-foreground">
              {Object.entries(normalizeReport).map(([key, value]) => (
                <div key={key} className="flex items-center justify-between gap-2">
                  <span>{key.replace(/_/g, " ")}</span>
                  <span className="font-medium text-foreground">{String(value)}</span>
                </div>
              ))}
            </div>
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
              <p className="text-sm">Kun HTML-maler kan normaliseres</p>
            </div>
          </div>
        ) : (
          <div className="flex-1 flex flex-col">
            <div className="px-4 py-2 border-b bg-gray-100 text-sm font-medium">
              Forhåndsvisning
              {originalContent && (
                <span className="text-gray-500 font-normal ml-2">
                  ({originalContent.length.toLocaleString()} tegn)
                </span>
              )}
            </div>
            <div className="flex-1 overflow-hidden">
              <TemplatePreview
                content={originalContent}
                title={selectedTemplate?.title || "Forhåndsvisning"}
                isLoading={isLoading}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
