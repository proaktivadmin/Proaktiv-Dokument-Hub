"use client";

import { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { 
  FileText, 
  Users, 
  Download, 
  CheckCircle2,
  XCircle,
  Building2,
  Monitor,
  Maximize2,
  X,
  Palette,
  Eye
} from "lucide-react";
import { BudPortalMockup } from "./BudPortalMockup";
import { VisningPortalMockup } from "./VisningPortalMockup";
import { SalgsoppgavePortalMockup } from "./SalgsoppgavePortalMockup";

/**
 * PortalPreview Component
 * 
 * Main container for previewing Vitec portal skins.
 * Allows switching between Bud and Visning portals with configuration info.
 */

export function PortalPreview() {
  const [activeTab, setActiveTab] = useState("bud");
  const [showVossMode, setShowVossMode] = useState(false);
  const [fullscreenPortal, setFullscreenPortal] = useState<"bud" | "visning" | "salgsoppgave" | null>(null);
  const [useVanillaSkin, setUseVanillaSkin] = useState(false);

  // Fullscreen overlay
  if (fullscreenPortal) {
    return (
      <div className="fixed inset-0 z-50 bg-gray-100">
        {/* Fullscreen Header */}
        <div className="absolute top-0 left-0 right-0 bg-white border-b shadow-sm z-10">
          <div className="flex items-center justify-between px-4 py-3">
            <div className="flex items-center gap-3">
              <Badge variant="outline" className={useVanillaSkin ? "bg-gray-500 text-white border-0" : "bg-[#272630] text-white border-0"}>
                {useVanillaSkin ? "VANILLA" : "PROAKTIV"}
              </Badge>
              <span className="font-medium">
                {fullscreenPortal === "bud" ? "Budportal" : fullscreenPortal === "visning" ? "Visningsportal" : "Bestill salgsoppgave"} — Fullskjerm forhåndsvisning
              </span>
              {showVossMode && (
                <Badge variant="outline" className="bg-amber-100 text-amber-800 border-amber-300">
                  <Building2 className="h-3 w-3 mr-1" />
                  Voss-modus
                </Badge>
              )}
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant={useVanillaSkin ? "default" : "outline"}
                size="sm"
                onClick={() => setUseVanillaSkin(!useVanillaSkin)}
                className={useVanillaSkin ? "bg-gray-600 hover:bg-gray-700" : ""}
              >
                <Palette className="h-4 w-4 mr-2" />
                {useVanillaSkin ? "Vis Proaktiv" : "Vis Vanilla"}
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowVossMode(!showVossMode)}
              >
                <Building2 className="h-4 w-4 mr-2" />
                {showVossMode ? "Deaktiver" : "Aktiver"} Voss-modus
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setFullscreenPortal(null)}
              >
                <X className="h-4 w-4 mr-2" />
                Lukk fullskjerm
              </Button>
            </div>
          </div>
        </div>

        {/* Fullscreen Content */}
        <div className="pt-14 h-full overflow-auto">
          {fullscreenPortal === "bud" ? (
            <BudPortalMockup showFinancing={showVossMode} fullscreen useVanillaSkin={useVanillaSkin} />
          ) : fullscreenPortal === "visning" ? (
            <VisningPortalMockup showFinancing={showVossMode} fullscreen useVanillaSkin={useVanillaSkin} />
          ) : (
            <SalgsoppgavePortalMockup showFinancing={showVossMode} fullscreen useVanillaSkin={useVanillaSkin} />
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-foreground">Portal Skins</h1>
          <p className="text-muted-foreground mt-1">
            Forhåndsvisning av Proaktiv-merkede Vitec-portaler
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Badge variant="outline" className="bg-emerald-50 text-emerald-700 border-emerald-200">
            <CheckCircle2 className="h-3 w-3 mr-1" />
            Klar for godkjenning
          </Badge>
          <Button variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Last ned ZIP
          </Button>
        </div>
      </div>

      {/* Configuration Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-[#272630]" />
              Primærfarge
            </CardTitle>
          </CardHeader>
          <CardContent>
            <code className="text-xs bg-muted px-2 py-1 rounded">#272630</code>
            <p className="text-xs text-muted-foreground mt-1">Proaktiv Charcoal</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-[#bcab8a]" />
              Aksentfarge
            </CardTitle>
          </CardHeader>
          <CardContent>
            <code className="text-xs bg-muted px-2 py-1 rounded">#bcab8a</code>
            <p className="text-xs text-muted-foreground mt-1">Proaktiv Bronse</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Samtykke-opsjoner</CardTitle>
          </CardHeader>
          <CardContent className="space-y-1">
            <div className="flex items-center gap-2 text-xs">
              <CheckCircle2 className="h-3 w-3 text-emerald-600" />
              <span>Verdivurdering</span>
            </div>
            <div className="flex items-center gap-2 text-xs">
              <CheckCircle2 className="h-3 w-3 text-emerald-600" />
              <span>Budvarsel (visning)</span>
            </div>
            <div className="flex items-center gap-2 text-xs">
              <XCircle className="h-3 w-3 text-red-400" />
              <span className="text-muted-foreground">Nyhetsbrev (skjult)</span>
            </div>
            <div className="flex items-center gap-2 text-xs">
              <XCircle className="h-3 w-3 text-red-400" />
              <span className="text-muted-foreground">Finansiering (skjult)*</span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Skin Toggle */}
      <Card className={useVanillaSkin ? "bg-gray-100 border-gray-300" : "bg-[#272630]/5 border-[#272630]/20"}>
        <CardContent className="py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Palette className={useVanillaSkin ? "h-5 w-5 text-gray-600" : "h-5 w-5 text-[#272630]"} />
              <div>
                <p className={useVanillaSkin ? "text-sm font-medium text-gray-900" : "text-sm font-medium text-[#272630]"}>
                  {useVanillaSkin ? "Vanilla Skin (Bootstrap standard)" : "Proaktiv Skin (Tilpasset)"}
                </p>
                <p className={useVanillaSkin ? "text-xs text-gray-600" : "text-xs text-[#272630]/70"}>
                  {useVanillaSkin 
                    ? "Viser standard Bootstrap-farger for sammenligning med live portaler" 
                    : "Viser Proaktiv-merkede farger, knapper og elementer"}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant={useVanillaSkin ? "default" : "outline"}
                size="sm"
                onClick={() => setUseVanillaSkin(!useVanillaSkin)}
                className={useVanillaSkin ? "bg-gray-600 hover:bg-gray-700" : "border-[#272630] text-[#272630] hover:bg-[#272630]/10"}
              >
                <Eye className="h-4 w-4 mr-2" />
                {useVanillaSkin ? "Bytt til Proaktiv" : "Bytt til Vanilla"}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Voss Office Toggle */}
      <Card className="bg-amber-50 border-amber-200">
        <CardContent className="py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Building2 className="h-5 w-5 text-amber-600" />
              <div>
                <p className="text-sm font-medium text-amber-900">Proaktiv Voss - Spesialkonfigurasjon</p>
                <p className="text-xs text-amber-700">Voss-kontoret har finansiering aktivert (backend-overstyring)</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs text-amber-700">Simuler Voss</span>
              <input
                type="checkbox"
                checked={showVossMode}
                onChange={(e) => setShowVossMode(e.target.checked)}
                className="h-4 w-4 rounded border-amber-300 text-amber-600 focus:ring-amber-500"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Portal Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <div className="flex items-center justify-between mb-4">
          <TabsList>
            <TabsTrigger value="bud" className="gap-2">
              <FileText className="h-4 w-4" />
              Budportal
            </TabsTrigger>
            <TabsTrigger value="visning" className="gap-2">
              <Users className="h-4 w-4" />
              Visningsportal
            </TabsTrigger>
            <TabsTrigger value="salgsoppgave" className="gap-2">
              <Download className="h-4 w-4" />
              Salgsoppgave
            </TabsTrigger>
          </TabsList>

          <div className="flex items-center gap-3">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setFullscreenPortal(activeTab as "bud" | "visning" | "salgsoppgave")}
            >
              <Maximize2 className="h-4 w-4 mr-2" />
              Fullskjerm
            </Button>
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <Monitor className="h-4 w-4" />
              <span>Desktop</span>
            </div>
          </div>
        </div>

        <TabsContent value="bud" className="mt-0">
          <Card>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-lg">Budportal</CardTitle>
                  <CardDescription>
                    Portal for innsending av bud på eiendommer
                  </CardDescription>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant={useVanillaSkin ? "outline" : "secondary"}>
                    {useVanillaSkin ? "VANILLA" : "PROAKTIV-bud.zip"}
                  </Badge>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setFullscreenPortal("bud")}
                  >
                    <Maximize2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent className="p-0 border-t">
              <div className="bg-gray-100 rounded-b-lg overflow-hidden">
                <BudPortalMockup showFinancing={showVossMode} useVanillaSkin={useVanillaSkin} />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="visning" className="mt-0">
          <Card>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-lg">Visningsportal</CardTitle>
                  <CardDescription>
                    Portal for påmelding til visninger
                  </CardDescription>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant={useVanillaSkin ? "outline" : "secondary"}>
                    {useVanillaSkin ? "VANILLA" : "PROAKTIV-visning.zip"}
                  </Badge>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setFullscreenPortal("visning")}
                  >
                    <Maximize2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent className="p-0 border-t">
              <div className="bg-gray-100 rounded-b-lg overflow-hidden">
                <VisningPortalMockup showFinancing={showVossMode} useVanillaSkin={useVanillaSkin} />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="salgsoppgave" className="mt-0">
          <Card>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-lg">Bestill salgsoppgave</CardTitle>
                  <CardDescription>
                    Portal for å bestille salgsoppgave på e-post
                  </CardDescription>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant={useVanillaSkin ? "outline" : "secondary"}>
                    {useVanillaSkin ? "VANILLA" : "PROAKTIV-visning.zip"}
                  </Badge>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setFullscreenPortal("salgsoppgave")}
                  >
                    <Maximize2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent className="p-0 border-t">
              <div className="bg-gray-100 rounded-b-lg overflow-hidden">
                <SalgsoppgavePortalMockup showFinancing={showVossMode} useVanillaSkin={useVanillaSkin} />
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* File Summary */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Filer i leveransen</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium text-sm mb-2 flex items-center gap-2">
                <FileText className="h-4 w-4 text-blue-600" />
                Budportal (4 filer)
              </h4>
              <ul className="text-xs space-y-1 text-muted-foreground">
                <li>• PROAKTIV.scss</li>
                <li>• PROAKTIV.css</li>
                <li>• PROAKTIV.min.css</li>
                <li>• PROAKTIV.json</li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium text-sm mb-2 flex items-center gap-2">
                <Users className="h-4 w-4 text-emerald-600" />
                Visningsportal (13 filer)
              </h4>
              <ul className="text-xs space-y-1 text-muted-foreground">
                <li>• PROAKTIV.scss / .css / .min.css / .json</li>
                <li>• 4 e-postmaler (oppdatert signatur)</li>
                <li>• 2 notatmaler</li>
                <li>• 2 SMS-maler</li>
                <li>• blacklist.json</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Accuracy Note */}
      <Card className="bg-emerald-50 border-emerald-200">
        <CardContent className="py-3">
          <div className="flex items-start gap-3">
            <CheckCircle2 className="h-5 w-5 text-emerald-600 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-emerald-900">Autentisk forhåndsvisning</p>
              <p className="text-xs text-emerald-700 mt-1">
                Denne forhåndsvisningen bruker den <strong>eksakte HTML-strukturen</strong> fra Vitecs live portaler,
                kombinert med Proaktiv-skinnet. Farger, knapper, skjemaelementer og samtykke-opsjoner vil
                se identiske ut i produksjon. Bruk fullskjerm-modus for beste opplevelse.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
