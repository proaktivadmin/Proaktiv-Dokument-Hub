"use client";

import { useState } from "react";
import { Copy, Check, ExternalLink, Download } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

interface LogoAsset {
  name: string;
  filename: string;
  url: string;
  format: "svg" | "png" | "jpg";
  variant?: string;
  background?: "light" | "dark" | "transparent";
}

// Proaktiv logo assets hosted on proaktiv.no/assets/logos/
const LOGO_ASSETS: LogoAsset[] = [
  // Main logos
  {
    name: "Logo (SVG)",
    filename: "logo.svg",
    url: "https://proaktiv.no/assets/logos/logo.svg",
    format: "svg",
    variant: "full",
    background: "light",
  },
  {
    name: "Logo (PNG)",
    filename: "logo.png",
    url: "https://proaktiv.no/assets/logos/logo.png",
    format: "png",
    variant: "full",
    background: "light",
  },
  {
    name: "Logo Hvit",
    filename: "logo_white.png",
    url: "https://proaktiv.no/assets/logos/logo_white.png",
    format: "png",
    variant: "full",
    background: "dark",
  },
  {
    name: "Logo Enkel Svart",
    filename: "logo_simple_black.png",
    url: "https://proaktiv.no/assets/logos/logo_simple_black.png",
    format: "png",
    variant: "full",
    background: "light",
  },
  {
    name: "Proaktiv Sort",
    filename: "proaktiv_sort.png",
    url: "https://proaktiv.no/assets/logos/proaktiv_sort.png",
    format: "png",
    variant: "full",
    background: "light",
  },
  {
    name: "Proaktiv Eiendomsmegling Sort",
    filename: "proaktiv_eiendomsmegling_sort.png",
    url: "https://proaktiv.no/assets/logos/proaktiv_eiendomsmegling_sort.png",
    format: "png",
    variant: "full",
    background: "light",
  },
  // Lilje icons
  {
    name: "Lilje Clean 52",
    filename: "lilje_clean_52.png",
    url: "https://proaktiv.no/assets/logos/lilje_clean_52.png",
    format: "png",
    variant: "icon",
    background: "transparent",
  },
  {
    name: "Lilje Hel Svart",
    filename: "lilje_hel_black.png",
    url: "https://proaktiv.no/assets/logos/lilje_hel_black.png",
    format: "png",
    variant: "icon",
    background: "light",
  },
  {
    name: "Lilje Hel Warmgrey",
    filename: "lilje_hel_warmgrey.png",
    url: "https://proaktiv.no/assets/logos/lilje_hel_warmgrey.png",
    format: "png",
    variant: "icon",
    background: "light",
  },
  {
    name: "PE Lilje Svart 1920x2080",
    filename: "pe_lilje_svart_1920x2080.png",
    url: "https://proaktiv.no/assets/logos/pe_lilje_svart_1920x2080.png",
    format: "png",
    variant: "icon",
    background: "light",
  },
  {
    name: "PE Logo Svart 1920x2080",
    filename: "pe_logo_svart_1920x2080.1.png",
    url: "https://proaktiv.no/assets/logos/pe_logo_svart_1920x2080.1.png",
    format: "png",
    variant: "full",
    background: "light",
  },
  // Social icons
  {
    name: "Email Ikon",
    filename: "email.png",
    url: "https://proaktiv.no/assets/logos/email.png",
    format: "png",
    variant: "icon",
    background: "transparent",
  },
  {
    name: "Facebook Ikon",
    filename: "facebook.png",
    url: "https://proaktiv.no/assets/logos/facebook.png",
    format: "png",
    variant: "icon",
    background: "transparent",
  },
  {
    name: "Instagram Ikon",
    filename: "instagram.png",
    url: "https://proaktiv.no/assets/logos/instagram.png",
    format: "png",
    variant: "icon",
    background: "transparent",
  },
  {
    name: "LinkedIn Ikon",
    filename: "linkedin.png",
    url: "https://proaktiv.no/assets/logos/linkedin.png",
    format: "png",
    variant: "icon",
    background: "transparent",
  },
  {
    name: "Telefon Ikon",
    filename: "phone.png",
    url: "https://proaktiv.no/assets/logos/phone.png",
    format: "png",
    variant: "icon",
    background: "transparent",
  },
  // Signature
  {
    name: "Proaktiv Signatur",
    filename: "proaktiv-signatur.png",
    url: "https://proaktiv.no/assets/logos/proaktiv-signatur.png",
    format: "png",
    variant: "full",
    background: "transparent",
  },
];

interface LogoCardProps {
  logo: LogoAsset;
}

function LogoCard({ logo }: LogoCardProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(logo.url);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const link = document.createElement("a");
    link.href = logo.url;
    link.download = logo.filename;
    link.target = "_blank";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const bgClass = logo.background === "dark" 
    ? "bg-slate-800" 
    : logo.background === "light" 
      ? "bg-white border" 
      : "bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAiIGhlaWdodD0iMjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGRlZnM+PHBhdHRlcm4gaWQ9ImdyaWQiIHdpZHRoPSIyMCIgaGVpZ2h0PSIyMCIgcGF0dGVyblVuaXRzPSJ1c2VyU3BhY2VPblVzZSI+PHJlY3Qgd2lkdGg9IjEwIiBoZWlnaHQ9IjEwIiBmaWxsPSIjZjBmMGYwIi8+PHJlY3QgeD0iMTAiIHk9IjEwIiB3aWR0aD0iMTAiIGhlaWdodD0iMTAiIGZpbGw9IiNmMGYwZjAiLz48L3BhdHRlcm4+PC9kZWZzPjxyZWN0IHdpZHRoPSIxMDAlIiBoZWlnaHQ9IjEwMCUiIGZpbGw9InVybCgjZ3JpZCkiLz48L3N2Zz4=')]";

  return (
    <Card className="group overflow-hidden">
      {/* Preview area */}
      <div className={`relative h-32 flex items-center justify-center p-4 ${bgClass}`}>
        <img 
          src={logo.url} 
          alt={logo.name}
          className="max-h-full max-w-full object-contain"
          onError={(e) => {
            (e.target as HTMLImageElement).style.display = "none";
          }}
        />
      </div>

      <CardContent className="p-4">
        <div className="flex items-start justify-between gap-2 mb-3">
          <div className="min-w-0">
            <h3 className="font-medium text-sm truncate">{logo.name}</h3>
            <p className="text-xs text-muted-foreground truncate">{logo.filename}</p>
          </div>
          <Badge variant="outline" className="shrink-0 text-xs">
            {logo.format.toUpperCase()}
          </Badge>
        </div>

        {/* Actions */}
        <div className="flex gap-2">
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="flex-1"
                  onClick={handleCopy}
                >
                  {copied ? (
                    <>
                      <Check className="h-3.5 w-3.5 mr-1.5 text-green-600" />
                      Kopiert!
                    </>
                  ) : (
                    <>
                      <Copy className="h-3.5 w-3.5 mr-1.5" />
                      Kopier URL
                    </>
                  )}
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                <p className="text-xs font-mono max-w-xs truncate">{logo.url}</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>

          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button 
                  variant="ghost" 
                  size="icon"
                  className="shrink-0"
                  onClick={handleDownload}
                >
                  <Download className="h-4 w-4" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>Last ned</TooltipContent>
            </Tooltip>
          </TooltipProvider>

          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button 
                  variant="ghost" 
                  size="icon"
                  className="shrink-0"
                  asChild
                >
                  <a href={logo.url} target="_blank" rel="noopener noreferrer">
                    <ExternalLink className="h-4 w-4" />
                  </a>
                </Button>
              </TooltipTrigger>
              <TooltipContent>Åpne i ny fane</TooltipContent>
            </Tooltip>
          </TooltipProvider>
        </div>
      </CardContent>
    </Card>
  );
}

export function LogoLibrary() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold">Proaktiv Logoer</h3>
          <p className="text-sm text-muted-foreground">
            Offisielle logoer og ikoner fra proaktiv.no for bruk i dokumenter og presentasjoner
          </p>
        </div>
        <Badge variant="secondary">{LOGO_ASSETS.length} filer</Badge>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {LOGO_ASSETS.map((logo) => (
          <LogoCard key={logo.filename} logo={logo} />
        ))}
      </div>

      <div className="text-xs text-muted-foreground border-t pt-4">
        <p>
          <strong>Tips:</strong> Bruk SVG-formatet når mulig for best kvalitet i alle størrelser. 
          Hvite varianter er ment for mørk bakgrunn.
        </p>
      </div>
    </div>
  );
}
