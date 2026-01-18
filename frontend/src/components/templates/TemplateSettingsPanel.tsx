"use client";

/**
 * TemplateSettingsPanel - Settings panel for template configuration
 * Handles margins, header/footer/signature, theme, receiver, output type, etc.
 */

import { useState, useEffect } from "react";
import { Save, RotateCcw, Loader2, Eye } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { useLayoutPartialsForChannel } from "@/hooks/useLayoutPartials";
import { RECEIVER_TYPES } from "@/lib/vitec/receiver-types";

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
  templateType: "Objekt/Kontakt" | "System" | null;
  receiverType: string | null;
  receiver: string | null;
  extraReceivers: string[];
  phases: string[];
  assignmentTypes: string[];
  ownershipTypes: string[];
  departments: string[];
  emailSubject: string | null;
  
  // Styling
  themeStylesheet: string | null;
}

export const DEFAULT_TEMPLATE_SETTINGS: TemplateSettings = {
  marginTop: 1.5,
  marginRight: 1.2,
  marginBottom: 1.0,
  marginLeft: 1.0,
  headerTemplateId: null,
  footerTemplateId: null,
  signatureTemplateId: null,
  channel: "pdf_email",
  templateType: null,
  receiverType: null,
  receiver: null,
  extraReceivers: [],
  phases: [],
  assignmentTypes: [],
  ownershipTypes: [],
  departments: [],
  emailSubject: null,
  themeStylesheet: null,
};

const RECEIVER_OPTIONS = Array.from(
  new Set(RECEIVER_TYPES.map((receiver) => receiver.name))
);

const TEMPLATE_TYPE_OPTIONS = [
  { value: "Objekt/Kontakt", label: "Objekt/Kontakt" },
  { value: "System", label: "System" },
];

const RECEIVER_TYPE_OPTIONS = [
  { value: "Egne/kundetilpasset", label: "Egne/kundetilpasset" },
  { value: "Systemstandard", label: "Systemstandard" },
];

const PHASE_OPTIONS = [
  { value: "Innsalg", label: "Innsalg" },
  { value: "Til salgs", label: "Til salgs" },
  { value: "Klargjoring", label: "Klargjøring" },
  { value: "Kontrakt", label: "Kontrakt" },
  { value: "Oppgjor", label: "Oppgjør" },
  { value: "2 faser", label: "2 faser" },
  { value: "3 faser", label: "3 faser" },
  { value: "4 faser", label: "4 faser" },
];

const OWNERSHIP_OPTIONS = [
  { value: "Selveier", label: "Selveier" },
  { value: "Andel", label: "Andel" },
  { value: "Aksje", label: "Aksje" },
  { value: "Obligasjon", label: "Obligasjon" },
  { value: "Tomt", label: "Tomt" },
  { value: "Naering", label: "Næring" },
  { value: "Hytte", label: "Hytte" },
  { value: "Borettslag", label: "Borettslag" },
  { value: "Sameie", label: "Sameie" },
];

interface TemplateSettingsPanelProps {
  templateId: string;
  initialSettings?: Partial<TemplateSettings>;
  onSave?: (settings: TemplateSettings) => Promise<void>;
  isSaving?: boolean;
  themeOptions?: Array<{ id: string; name: string }>;
  showActions?: boolean;
  onSettingsChange?: (settings: TemplateSettings) => void;
  disabled?: boolean;
}

export function TemplateSettingsPanel({
  templateId,
  initialSettings,
  onSave,
  isSaving: isSavingProp = false,
  themeOptions = [],
  showActions = true,
  onSettingsChange,
  disabled = false,
}: TemplateSettingsPanelProps) {
  const [settings, setSettings] = useState<TemplateSettings>({
    ...DEFAULT_TEMPLATE_SETTINGS,
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
  const isInteractionDisabled = disabled || isSaving;

  // Sync local state when initialSettings prop changes (e.g., after save/refetch)
  useEffect(() => {
    setSettings({
      ...DEFAULT_TEMPLATE_SETTINGS,
      ...initialSettings,
    });
  }, [initialSettings]);

  // Track changes
  useEffect(() => {
    const initial = { ...DEFAULT_TEMPLATE_SETTINGS, ...initialSettings };
    const changed = JSON.stringify(settings) !== JSON.stringify(initial);
    setHasChanges(changed);
  }, [settings, initialSettings]);

  useEffect(() => {
    onSettingsChange?.(settings);
  }, [onSettingsChange, settings]);

  const handleMarginChange = (
    side: "marginTop" | "marginRight" | "marginBottom" | "marginLeft",
    value: string
  ) => {
    const numValue = parseFloat(value) || 0;
    setSettings((prev) => ({ ...prev, [side]: numValue }));
  };

  const toggleMultiValue = (
    key: "phases" | "ownershipTypes",
    value: string
  ) => {
    setSettings((prev) => {
      const current = prev[key] ?? [];
      const next = current.includes(value)
        ? current.filter((item) => item !== value)
        : [...current, value];
      return { ...prev, [key]: next };
    });
  };

  const handleCommaListChange = (
    key: "extraReceivers" | "assignmentTypes" | "departments",
    value: string
  ) => {
    const next = value
      .split(",")
      .map((item) => item.trim())
      .filter(Boolean);
    setSettings((prev) => ({ ...prev, [key]: next }));
  };

  const formatCommaList = (values: string[]) => values.join(", ");

  const handleSave = async () => {
    if (!onSave) return;
    await onSave(settings);
  };

  const handleReset = () => {
    setSettings({ ...DEFAULT_TEMPLATE_SETTINGS, ...initialSettings });
  };

  return (
    <div className="space-y-4">
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
              disabled={isInteractionDisabled}
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
              disabled={isInteractionDisabled}
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
              disabled={isInteractionDisabled}
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
              disabled={isInteractionDisabled}
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
                  disabled={isInteractionDisabled || partialsLoading}
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
                    type="button"
                    onClick={() => {
                      const header = headers.find(h => h.id === settings.headerTemplateId);
                      if (header) setPreviewPartial({ name: header.name, content: header.html_content });
                    }}
                    disabled={isInteractionDisabled}
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
                  disabled={isInteractionDisabled || partialsLoading}
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
                    type="button"
                    onClick={() => {
                      const footer = footers.find(f => f.id === settings.footerTemplateId);
                      if (footer) setPreviewPartial({ name: footer.name, content: footer.html_content });
                    }}
                    disabled={isInteractionDisabled}
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
                  disabled={isInteractionDisabled || partialsLoading}
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
                    type="button"
                    onClick={() => {
                      const sig = signatures.find(s => s.id === settings.signatureTemplateId);
                      if (sig) setPreviewPartial({ name: sig.name, content: sig.html_content });
                    }}
                    disabled={isInteractionDisabled}
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
              disabled={isInteractionDisabled}
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
                disabled={isInteractionDisabled}
              />
            </div>
          )}
        </div>
      </div>

      <Separator />

      {/* Categorization */}
      <div>
        <h3 className="text-sm font-medium mb-3">Kategorisering</h3>
        <div className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="template-type">Maltype</Label>
              <Select
                value={settings.templateType ?? "none"}
                onValueChange={(value) =>
                  setSettings((prev) => ({
                    ...prev,
                    templateType: value === "none" ? null : (value as TemplateSettings["templateType"]),
                  }))
                }
                disabled={isInteractionDisabled}
              >
                <SelectTrigger id="template-type">
                  <SelectValue placeholder="Velg maltype..." />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">Ikke spesifisert</SelectItem>
                  {TEMPLATE_TYPE_OPTIONS.map((option) => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="receiver-type">Mottakertype</Label>
              <Select
                value={settings.receiverType ?? "none"}
                onValueChange={(value) =>
                  setSettings((prev) => ({
                    ...prev,
                    receiverType: value === "none" ? null : value,
                  }))
                }
                disabled={isInteractionDisabled}
              >
                <SelectTrigger id="receiver-type">
                  <SelectValue placeholder="Velg mottakertype..." />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">Ikke spesifisert</SelectItem>
                  {RECEIVER_TYPE_OPTIONS.map((option) => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

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
              disabled={isInteractionDisabled}
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

          <div className="space-y-2">
            <Label htmlFor="extra-receivers">Ekstra mottakere (kommaseparert)</Label>
            <Textarea
              id="extra-receivers"
              value={formatCommaList(settings.extraReceivers)}
              onChange={(e) => handleCommaListChange("extraReceivers", e.target.value)}
              placeholder="F.eks. Megler, Bank, Interessent"
              disabled={isInteractionDisabled}
            />
          </div>

          <div className="space-y-2">
            <Label>Faser</Label>
            <div className="grid gap-2 sm:grid-cols-2">
              {PHASE_OPTIONS.map((option) => (
                <label key={option.value} className="flex items-center gap-2 text-sm">
                  <Checkbox
                    checked={settings.phases.includes(option.value)}
                    onCheckedChange={() => toggleMultiValue("phases", option.value)}
                    disabled={isInteractionDisabled}
                  />
                  <span>{option.label}</span>
                </label>
              ))}
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="assignment-types">Oppdragstype (kommaseparert)</Label>
            <Textarea
              id="assignment-types"
              value={formatCommaList(settings.assignmentTypes)}
              onChange={(e) => handleCommaListChange("assignmentTypes", e.target.value)}
              placeholder="F.eks. Oppdrag, Markedsføring"
              disabled={isInteractionDisabled}
            />
          </div>

          <div className="space-y-2">
            <Label>Eieform</Label>
            <div className="grid gap-2 sm:grid-cols-2">
              {OWNERSHIP_OPTIONS.map((option) => (
                <label key={option.value} className="flex items-center gap-2 text-sm">
                  <Checkbox
                    checked={settings.ownershipTypes.includes(option.value)}
                    onCheckedChange={() => toggleMultiValue("ownershipTypes", option.value)}
                    disabled={isInteractionDisabled}
                  />
                  <span>{option.label}</span>
                </label>
              ))}
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="departments">Avdelinger (kommaseparert)</Label>
            <Textarea
              id="departments"
              value={formatCommaList(settings.departments)}
              onChange={(e) => handleCommaListChange("departments", e.target.value)}
              placeholder="F.eks. Salg, Utleie"
              disabled={isInteractionDisabled}
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
              disabled={isInteractionDisabled}
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
      {showActions && (
        <div className="flex gap-2 pt-4">
          <Button
            variant="outline"
            type="button"
            onClick={handleReset}
            disabled={!hasChanges || isInteractionDisabled}
          >
            <RotateCcw className="h-4 w-4 mr-2" />
            Tilbakestill
          </Button>
          <Button
            type="button"
            onClick={handleSave}
            disabled={!hasChanges || isInteractionDisabled}
            className="flex-1"
          >
            <Save className="h-4 w-4 mr-2" />
            {isSaving ? "Lagrer..." : "Lagre endringer"}
          </Button>
        </div>
      )}

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
