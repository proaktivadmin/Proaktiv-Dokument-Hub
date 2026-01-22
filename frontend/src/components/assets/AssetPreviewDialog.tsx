"use client";

import { Download, File, FileText, FileSpreadsheet, Maximize2, type LucideIcon } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { assetsApi } from "@/lib/api/assets";
import type { CompanyAsset, AssetCategory } from "@/types/v3";

interface AssetPreviewDialogProps {
  asset: CompanyAsset | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const categoryLabels: Record<AssetCategory, string> = {
  logo: "Logo",
  photo: "Foto",
  marketing: "Markedsføring",
  document: "Dokument",
  other: "Annet",
};

const categoryColors: Record<AssetCategory, string> = {
  logo: "bg-purple-500/10 text-purple-600",
  photo: "bg-blue-500/10 text-blue-600",
  marketing: "bg-green-500/10 text-green-600",
  document: "bg-amber-500/10 text-amber-600",
  other: "bg-gray-500/10 text-gray-600",
};

// Render the appropriate file icon based on mime type
function FileIconDisplay({ mimeType, className }: { mimeType: string; className?: string }) {
  let IconComponent: LucideIcon = File;
  
  if (mimeType.includes("spreadsheet") || mimeType.includes("excel")) {
    IconComponent = FileSpreadsheet;
  } else if (mimeType.includes("pdf") || mimeType.includes("document") || mimeType.includes("text")) {
    IconComponent = FileText;
  }
  
  return <IconComponent className={className} />;
}

export function AssetPreviewDialog({ asset, open, onOpenChange }: AssetPreviewDialogProps) {
  if (!asset) return null;

  const handleDownload = async () => {
    try {
      const blob = await assetsApi.download(asset.id);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = asset.filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error("Failed to download:", err);
    }
  };

  const handleOpenInNewTab = () => {
    window.open(assetsApi.getDownloadUrl(asset.id), "_blank");
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[90vh] flex flex-col p-0 gap-0 overflow-hidden">
        <DialogHeader className="px-6 py-4 border-b shrink-0">
          <div className="flex items-center justify-between gap-4">
            <div className="min-w-0">
              <DialogTitle className="text-lg truncate">{asset.name}</DialogTitle>
              <div className="flex items-center gap-2 mt-1 text-sm text-muted-foreground">
                <Badge variant="secondary" className={`text-xs ${categoryColors[asset.category]}`}>
                  {categoryLabels[asset.category]}
                </Badge>
                <span>{asset.file_size_formatted}</span>
                <span>•</span>
                <span>{asset.content_type}</span>
              </div>
            </div>
            <div className="flex items-center gap-2 shrink-0">
              <Button variant="outline" size="sm" onClick={handleOpenInNewTab}>
                <Maximize2 className="h-4 w-4 mr-2" />
                Åpne i ny fane
              </Button>
              <Button size="sm" onClick={handleDownload}>
                <Download className="h-4 w-4 mr-2" />
                Last ned
              </Button>
            </div>
          </div>
        </DialogHeader>

        {/* Preview area */}
        <div className="flex-1 overflow-auto bg-muted/30 flex items-center justify-center p-4 min-h-[400px]">
          {asset.is_image ? (
            <img
              src={assetsApi.getDownloadUrl(asset.id)}
              alt={asset.name}
              className="max-w-full max-h-[70vh] object-contain rounded-lg shadow-lg"
            />
          ) : asset.content_type === "application/pdf" ? (
            <iframe
              src={assetsApi.getDownloadUrl(asset.id)}
              className="w-full h-[70vh] rounded-lg border bg-white"
              title={asset.name}
            />
          ) : (
            <div className="text-center py-16">
              <FileIconDisplay mimeType={asset.content_type} className="h-24 w-24 mx-auto text-muted-foreground/50 mb-4" />
              <h3 className="text-lg font-medium mb-1">{asset.filename}</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Forhåndsvisning ikke tilgjengelig for denne filtypen
              </p>
              <Button onClick={handleDownload}>
                <Download className="h-4 w-4 mr-2" />
                Last ned for å åpne
              </Button>
            </div>
          )}
        </div>

        {/* Footer with metadata */}
        <div className="px-6 py-3 border-t bg-muted/20 text-sm text-muted-foreground shrink-0">
          <div className="flex items-center justify-between">
            <span>
              Lastet opp: {new Date(asset.created_at).toLocaleDateString("nb-NO", {
                year: "numeric",
                month: "long",
                day: "numeric",
                hour: "2-digit",
                minute: "2-digit",
              })}
            </span>
            <span className="font-mono text-xs">{asset.filename}</span>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
