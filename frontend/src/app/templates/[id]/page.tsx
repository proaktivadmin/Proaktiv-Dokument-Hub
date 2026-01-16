"use client";

/**
 * Template Detail Page - Document Viewer
 */

import { useState } from "react";
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

export default function TemplateDetailPage() {
  const params = useParams();
  const router = useRouter();
  const templateId = params.id as string;
  const [settingsOpen, setSettingsOpen] = useState(false);

  const handleSaveSettings = async (settings: TemplateSettings) => {
    console.log("Saving settings for template", templateId, settings);
    // TODO: Call API to save settings
    // await templateApi.updateSettings(templateId, settings);
    setSettingsOpen(false);
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
              onSave={handleSaveSettings}
            />
          </div>
        </SheetContent>
      </Sheet>
    </div>
  );
}
