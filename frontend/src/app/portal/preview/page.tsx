"use client";

import { useRouter } from "next/navigation";
import { ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { PortalPreview } from "@/components/portal";

/**
 * Portal Preview Page
 * 
 * Displays interactive mockups of Proaktiv-branded Vitec portals
 * for design review and approval before deployment.
 */
export default function PortalPreviewPage() {
  const router = useRouter();

  return (
    <div className="min-h-screen bg-[#FAFAF8]">
      {/* Header */}
      <header className="bg-white border-b sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => router.push("/")}
              className="gap-2"
            >
              <ArrowLeft className="h-4 w-4" />
              Tilbake
            </Button>
            <div className="h-6 w-px bg-border" />
            <h1 className="font-medium">Portal Skin Preview</h1>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs text-muted-foreground">Proaktiv Dokument Hub</span>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        <PortalPreview />
      </main>
    </div>
  );
}
