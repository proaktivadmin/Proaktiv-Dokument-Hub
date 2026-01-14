"use client";

/**
 * TemplateSettingsPanel - Settings panel for template configuration
 * Handles margins, header/footer, theme, receiver, output type, etc.
 */

import { useState, useEffect } from "react";
import { Save, RotateCcw } from "lucide-react";
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

export interface TemplateSettings {
  // Margins (in cm)
  marginTop: number;
  marginRight: number;
  marginBottom: number;
  marginLeft: number;
  
  // Header/Footer template IDs
  headerTemplateId: string | null;
  footerTemplateId: string | null;
  
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
  channel: "pdf_email",
  receiverType: null,
  receiver: null,
  emailSubject: null,
  themeStylesheet: null,
};

interface TemplateSettingsPanelProps {
  templateId: string;
  initialSettings?: Partial<TemplateSettings>;
  onSave?: (settings: TemplateSettings) => Promise<void>;
  headerOptions?: Array<{ id: string; title: string }>;
  footerOptions?: Array<{ id: string; title: string }>;
  themeOptions?: Array<{ id: string; name: string }>;
}

export function TemplateSettingsPanel({
  templateId,
  initialSettings,
  onSave,
  headerOptions = [],
  footerOptions = [],
  themeOptions = [],
}: TemplateSettingsPanelProps) {
  const [settings, setSettings] = useState<TemplateSettings>({
    ...DEFAULT_SETTINGS,
    ...initialSettings,
  });
  const [isSaving, setIsSaving] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);

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
    setIsSaving(true);
    try {
      await onSave(settings);
    } finally {
      setIsSaving(false);
    }
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

      {/* Header/Footer Section */}
      <div>
        <h3 className="text-sm font-medium mb-3">Topptekst og Bunntekst</h3>
        <div className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="header-template">Topptekst</Label>
            <Select
              value={settings.headerTemplateId || "none"}
              onValueChange={(value) =>
                setSettings((prev) => ({
                  ...prev,
                  headerTemplateId: value === "none" ? null : value,
                }))
              }
            >
              <SelectTrigger id="header-template">
                <SelectValue placeholder="Velg topptekst..." />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="none">Ingen topptekst</SelectItem>
                {headerOptions.map((option) => (
                  <SelectItem key={option.id} value={option.id}>
                    {option.title}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label htmlFor="footer-template">Bunntekst</Label>
            <Select
              value={settings.footerTemplateId || "none"}
              onValueChange={(value) =>
                setSettings((prev) => ({
                  ...prev,
                  footerTemplateId: value === "none" ? null : value,
                }))
              }
            >
              <SelectTrigger id="footer-template">
                <SelectValue placeholder="Velg bunntekst..." />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="none">Ingen bunntekst</SelectItem>
                {footerOptions.map((option) => (
                  <SelectItem key={option.id} value={option.id}>
                    {option.title}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
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
            <Input
              id="receiver"
              value={settings.receiver || ""}
              onChange={(e) =>
                setSettings((prev) => ({
                  ...prev,
                  receiver: e.target.value || null,
                }))
              }
              placeholder="Standard mottaker..."
            />
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
    </div>
  );
}
