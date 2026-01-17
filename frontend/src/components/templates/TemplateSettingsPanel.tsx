"use client";

/**
 * TemplateSettingsPanel - Settings panel for template configuration
 * Handles margins, header/footer/signature, theme, receiver, output type, etc.
 */

import { useState, useEffect, useMemo } from "react";
import { Save, RotateCcw, Loader2, Eye } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { useLayoutPartialsForChannel } from "@/hooks/useLayoutPartials";

export interface TemplateSettings {
  // Margins (in cm)
  marginTop: number;
  marginRight: number;
  marginBottom: number;
  marginLeft: number;
  
  // Header/Footer/Signature template IDs
  headerTemplateId: string | null;
  footerTemplateId: string | null;
  signatureTemplateId: string | null;
  
  // Output settings
  channel: "pdf" | "email" | "sms" | "pdf_email";
  receiverType: string | null;
  receiver: string | null;
  emailSubject: string | null;
  
  // Styling
  themeStylesheet: string | null;
}

const DEFAULT_SETTINGS: TemplateSettings = {
  marginTop: 1.5,
  marginRight: 1.2,
  marginBottom: 1.0,
  marginLeft: 1.0,
  headerTemplateId: null,
  footerTemplateId: null,
  signatureTemplateId: null,
  channel: "pdf_email",
  receiverType: null,
  receiver: null,
  emailSubject: null,
  themeStylesheet: null,
};

// Receiver options from Vitec reference
const RECEIVER_OPTIONS = [
  'Selger', 'Kjøper', 'Visningsdeltager', 'Budgiver', 'Interessent',
  'Utleier', 'Leietaker', 'Megler', 'Bank', 'Forretningsfører',
  'Advokat', 'Takstmann', 'Fotograf', 'Stylist', 'Annet'
] as const;

interface TemplateSettingsPanelProps {
  templateId: string;
  initialSettings?: Partial<TemplateSettings>;
  onSave?: (settings: TemplateSettings) => Promise<void>;
  isSaving?: boolean;
  themeOptions?: Array<{ id: string; name: string }>;
}

export function TemplateSettingsPanel({
  templateId,
  initialSettings,
  onSave,
  isSaving: isSavingProp = false,
  themeOptions = [],
}: TemplateSettingsPanelProps) {
  const [settings, setSettings] = useState<TemplateSettings>({
    ...DEFAULT_SETTINGS,
    ...initialSettings,
  });
  const [hasChanges, setHasChanges] = useState(false);
  const [previewPartial, setPreviewPartial] = useState<{ name: string; content: string } | null>(null);
  
  // Fetch layout partials based on selected channel
  const { 
    headers, 
    footers, 
    signatures, 
    isLoading: partialsLoading 
  } = useLayoutPartialsForChannel(settings.channel);
  
  // Use prop if provided, otherwise use internal state
  const isSaving = isSavingProp;

  // Sync local state when initialSettings prop changes (e.g., after save/refetch)
  useEffect(() => {
    setSettings({
      ...DEFAULT_SETTINGS,
      ...initialSettings,
    });
  }, [initialSettings]);

  // Track changes
  useEffect(() => {
    const initial = { ...DEFAULT_SETTINGS, ...initialSettings };
    const changed = JSON.stringify(settings) !== JSON.stringify(initial);
    setHasChanges(changed);
  }, [settings, initialSettings]);

  const handleMarginChange = (
    side: "marginTop" | "marginRight" | "marginBottom" | "marginLeft",
    value: string
  ) => {
    const numValue = parseFloat(value) || 0;
    setSettings((prev) => ({ ...prev, [side]: numValue }));
  };

  const handleSave = async () => {
    if (!onSave) return;
    await onSave(settings);
  };

  const handleReset = () => {
    setSettings({ ...DEFAULT_SETTINGS, ...initialSettings });
  };

  return (
    <div className="space-y-6">
      {/* Margins Section */}
      <div>
        <h3 className="text-sm font-medium mb-3">Sidemarger (cm)</h3>
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="margin-top">Topp</Label>
            <Input
              id="margin-top"
              type="number"
              step="0.1"
              min="0"
              max="5"
              value={settings.marginTop}
              onChange={(e) => handleMarginChange("marginTop", e.target.value)}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="margin-right">Høyre</Label>
            <Input
              id="margin-right"
              type="number"
              step="0.1"
              min="0"
              max="5"
              value={settings.marginRight}
              onChange={(e) => handleMarginChange("marginRight", e.target.value)}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="margin-bottom">Bunn</Label>
            <Input
              id="margin-bottom"
              type="number"
              step="0.1"
              min="0"
              max="5"
              value={settings.marginBottom}
              onChange={(e) => handleMarginChange("marginBottom", e.target.value)}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="margin-left">Venstre</Label>
            <Input
              id="margin-left"
              type="number"
              step="0.1"
              min="0"
              max="5"
              value={settings.marginLeft}
              onChange={(e) => handleMarginChange("marginLeft", e.target.value)}
            />
          </div>
        </div>
      </div>

      <Separator />

      {/* Header/Footer/Signature Section */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-medium">Layout</h3>
          {partialsLoading && (
            <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
          )}
        </div>
        <div className="space-y-4">
          {/* Header (PDF only) */}
          {(settings.channel === "pdf" || settings.channel === "pdf_email") && (
            <div className="space-y-2">
              <Label htmlFor="header-template">Topptekst (PDF)</Label>
              <div className="flex gap-2">
                <Select
                  value={settings.headerTemplateId || "none"}
                  onValueChange={(value) =>
                    setSettings((prev) => ({
                      ...prev,
                      headerTemplateId: value === "none" ? null : value,
                    }))
                  }
                >
                  <SelectTrigger id="header-template" className="flex-1">
                    <SelectValue placeholder="Velg topptekst..." />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="none">Ingen topptekst</SelectItem>
                    {headers.map((header) => (
                      <SelectItem key={header.id} value={header.id}>
                        {header.name}
                        {header.is_default && " ⭐"}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {settings.headerTemplateId && (
                  <Button
                    variant="outline"
                    size="icon"
                    onClick={() => {
                      const header = headers.find(h => h.id === settings.headerTemplateId);
                      if (header) setPreviewPartial({ name: header.name, content: header.html_content });
                    }}
                  >
                    <Eye className="h-4 w-4" />
                  </Button>
                )}
              </div>
            </div>
          )}

          {/* Footer (PDF only) */}
          {(settings.channel === "pdf" || settings.channel === "pdf_email") && (
            <div className="space-y-2">
              <Label htmlFor="footer-template">Bunntekst (PDF)</Label>
              <div className="flex gap-2">
                <Select
                  value={settings.footerTemplateId || "none"}
                  onValueChange={(value) =>
                    setSettings((prev) => ({
                      ...prev,
                      footerTemplateId: value === "none" ? null : value,
                    }))
                  }
                >
                  <SelectTrigger id="footer-template" className="flex-1">
                    <SelectValue placeholder="Velg bunntekst..." />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="none">Ingen bunntekst</SelectItem>
                    {footers.map((footer) => (
                      <SelectItem key={footer.id} value={footer.id}>
                        {footer.name}
                        {footer.document_type && ` (${footer.document_type})`}
                        {footer.is_default && " ⭐"}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {settings.footerTemplateId && (
                  <Button
                    variant="outline"
                    size="icon"
                    onClick={() => {
                      const footer = footers.find(f => f.id === settings.footerTemplateId);
                      if (footer) setPreviewPartial({ name: footer.name, content: footer.html_content });
                    }}
                  >
                    <Eye className="h-4 w-4" />
                  </Button>
                )}
              </div>
            </div>
          )}

          {/* Signature (Email/SMS) */}
          {(settings.channel === "email" || settings.channel === "sms" || settings.channel === "pdf_email") && (
            <div className="space-y-2">
              <Label htmlFor="signature-template">
                Signatur ({settings.channel === "sms" ? "SMS" : "E-post"})
              </Label>
              <div className="flex gap-2">
                <Select
                  value={settings.signatureTemplateId || "none"}
                  onValueChange={(value) =>
                    setSettings((prev) => ({
                      ...prev,
                      signatureTemplateId: value === "none" ? null : value,
                    }))
                  }
                >
                  <SelectTrigger id="signature-template" className="flex-1">
                    <SelectValue placeholder="Velg signatur..." />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="none">Ingen signatur</SelectItem>
                    {signatures.map((sig) => (
                      <SelectItem key={sig.id} value={sig.id}>
                        {sig.name}
                        {sig.context !== "all" && ` (${sig.context.toUpperCase()})`}
                        {sig.is_default && " ⭐"}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {settings.signatureTemplateId && (
                  <Button
                    variant="outline"
                    size="icon"
                    onClick={() => {
                      const sig = signatures.find(s => s.id === settings.signatureTemplateId);
                      if (sig) setPreviewPartial({ name: sig.name, content: sig.html_content });
                    }}
                  >
                    <Eye className="h-4 w-4" />
                  </Button>
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      <Separator />

      {/* Output Settings */}
      <div>
        <h3 className="text-sm font-medium mb-3">Utdata</h3>
        <div className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="channel">Kanal</Label>
            <Select
              value={settings.channel}
              onValueChange={(value) =>
                setSettings((prev) => ({
                  ...prev,
                  channel: value as TemplateSettings["channel"],
                }))
              }
            >
              <SelectTrigger id="channel">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="pdf_email">PDF + E-post</SelectItem>
                <SelectItem value="pdf">Kun PDF</SelectItem>
                <SelectItem value="email">Kun E-post</SelectItem>
                <SelectItem value="sms">SMS</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {(settings.channel === "email" || settings.channel === "pdf_email") && (
            <div className="space-y-2">
              <Label htmlFor="email-subject">Emnelinje</Label>
              <Input
                id="email-subject"
                value={settings.emailSubject || ""}
                onChange={(e) =>
                  setSettings((prev) => ({
                    ...prev,
                    emailSubject: e.target.value || null,
                  }))
                }
                placeholder="Emne for e-post..."
              />
            </div>
          )}

          <div className="space-y-2">
            <Label htmlFor="receiver">Mottaker</Label>
            <Select
              value={settings.receiver || "none"}
              onValueChange={(value) =>
                setSettings((prev) => ({
                  ...prev,
                  receiver: value === "none" ? null : value,
                }))
              }
            >
              <SelectTrigger id="receiver">
                <SelectValue placeholder="Velg mottaker..." />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="none">Ikke spesifisert</SelectItem>
                {RECEIVER_OPTIONS.map((option) => (
                  <SelectItem key={option} value={option}>
                    {option}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>
      </div>

      <Separator />

      {/* Theme Section */}
      <div>
        <h3 className="text-sm font-medium mb-3">Design</h3>
        <div className="space-y-2">
          <Label htmlFor="theme">Stilark</Label>
          <Select
            value={settings.themeStylesheet || "none"}
            onValueChange={(value) =>
              setSettings((prev) => ({
                ...prev,
                themeStylesheet: value === "none" ? null : value,
              }))
            }
          >
            <SelectTrigger id="theme">
              <SelectValue placeholder="Velg stilark..." />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="none">Standard</SelectItem>
              <SelectItem value="vitec-premium">Vitec Premium</SelectItem>
              <SelectItem value="proaktiv-classic">Proaktiv Classic</SelectItem>
              {themeOptions.map((option) => (
                <SelectItem key={option.id} value={option.id}>
                  {option.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Actions */}
      <div className="flex gap-2 pt-4">
        <Button
          variant="outline"
          onClick={handleReset}
          disabled={!hasChanges || isSaving}
        >
          <RotateCcw className="h-4 w-4 mr-2" />
          Tilbakestill
        </Button>
        <Button
          onClick={handleSave}
          disabled={!hasChanges || isSaving}
          className="flex-1"
        >
          <Save className="h-4 w-4 mr-2" />
          {isSaving ? "Lagrer..." : "Lagre endringer"}
        </Button>
      </div>

      {/* Partial Preview Dialog */}
      <Dialog open={!!previewPartial} onOpenChange={() => setPreviewPartial(null)}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>{previewPartial?.name || "Forhåndsvisning"}</DialogTitle>
          </DialogHeader>
          <div className="border rounded-md p-4 bg-white min-h-[200px]">
            {previewPartial?.content && (
              <div 
                dangerouslySetInnerHTML={{ __html: previewPartial.content }} 
                className="vitec-preview"
              />
            )}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
