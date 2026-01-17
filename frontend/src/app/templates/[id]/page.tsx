"use client";

/**
 * Template Detail Page - Document Viewer
 */

import { useState, useMemo } from "react";
import { useParams, useRouter } from "next/navigation";
import { DocumentViewer } from "@/components/viewer";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
} from "@/components/ui/sheet";
import { TemplateSettingsPanel, type TemplateSettings } from "@/components/templates/TemplateSettingsPanel";
import { useTemplateSettings } from "@/hooks/useTemplateSettings";
import { templateSettingsApi } from "@/lib/api/template-settings";
import { useToast } from "@/hooks/use-toast";
import type { UpdateTemplateSettingsRequest } from "@/types/v2";

export default function TemplateDetailPage() {
  const params = useParams();
  const router = useRouter();
  const templateId = params.id as string;
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const { toast } = useToast();

  // Fetch current settings from backend
  const { settings: backendSettings, refetch: refetchSettings } = useTemplateSettings(templateId);

  // Map backend snake_case to frontend camelCase
  const initialSettings = useMemo((): Partial<TemplateSettings> | undefined => {
    if (!backendSettings) return undefined;
    return {
      marginTop: backendSettings.margin_top ?? 1.5,
      marginRight: backendSettings.margin_right ?? 1.2,
      marginBottom: backendSettings.margin_bottom ?? 1.0,
      marginLeft: backendSettings.margin_left ?? 1.0,
      headerTemplateId: backendSettings.header_template_id ?? null,
      footerTemplateId: backendSettings.footer_template_id ?? null,
      signatureTemplateId: null, // Not in backend yet
      channel: (backendSettings.channel as TemplateSettings["channel"]) ?? "pdf_email",
      receiverType: backendSettings.receiver_type ?? null,
      receiver: backendSettings.receiver ?? null,
      emailSubject: backendSettings.email_subject ?? null,
      themeStylesheet: null, // Not in backend yet
    };
  }, [backendSettings]);

  const handleSaveSettings = async (settings: TemplateSettings) => {
    setIsSaving(true);
    try {
      // Map frontend camelCase to backend snake_case
      const payload: UpdateTemplateSettingsRequest = {
        channel: settings.channel,
        receiver: settings.receiver ?? undefined,
        receiver_type: settings.receiverType ?? undefined,
        email_subject: settings.emailSubject ?? undefined,
        header_template_id: settings.headerTemplateId ?? undefined,
        footer_template_id: settings.footerTemplateId ?? undefined,
        margin_top: settings.marginTop,
        margin_bottom: settings.marginBottom,
        margin_left: settings.marginLeft,
        margin_right: settings.marginRight,
      };

      await templateSettingsApi.updateSettings(templateId, payload);

      toast({
        title: "Innstillinger lagret",
        description: "Malens innstillinger ble oppdatert.",
      });

      refetchSettings();
      setSettingsOpen(false);
    } catch (error) {
      console.error("Failed to save settings:", error);
      toast({
        title: "Kunne ikke lagre",
        description: "Det oppsto en feil ved lagring av innstillinger.",
        variant: "destructive",
      });
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="h-screen bg-[#FAFAF8]">
      <DocumentViewer
        templateId={templateId}
        enableInspector
        onBack={() => router.push("/templates")}
        onSettings={() => setSettingsOpen(true)}
      />

      {/* Settings Sheet */}
      <Sheet open={settingsOpen} onOpenChange={setSettingsOpen}>
        <SheetContent className="w-[400px] sm:w-[540px] overflow-y-auto">
          <SheetHeader>
            <SheetTitle>Innstillinger</SheetTitle>
            <SheetDescription>
              Konfigurer marginer, topptekst, bunntekst og andre innstillinger for denne malen.
            </SheetDescription>
          </SheetHeader>
          <div className="mt-6">
            <TemplateSettingsPanel
              templateId={templateId}
              initialSettings={initialSettings}
              onSave={handleSaveSettings}
              isSaving={isSaving}
            />
          </div>
        </SheetContent>
      </Sheet>
    </div>
  );
}
