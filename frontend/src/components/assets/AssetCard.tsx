"use client";

import { File, Image as ImageIcon, Download, Trash2, MoreVertical } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { assetsApi } from "@/lib/api/assets";
import type { CompanyAsset, AssetCategory } from "@/types/v3";

interface AssetCardProps {
  asset: CompanyAsset;
  onClick?: () => void;
  onDelete?: () => void;
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

export function AssetCard({ asset, onClick, onDelete }: AssetCardProps) {
  const handleDownload = async (e: React.MouseEvent) => {
    e.stopPropagation();
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

  return (
    <Card 
      className="group cursor-pointer hover:shadow-md transition-all duration-200 overflow-hidden"
      onClick={onClick}
    >
      {/* Preview area */}
      <div className="aspect-square bg-muted flex items-center justify-center relative overflow-hidden">
        {asset.is_image ? (
          <img
            src={assetsApi.getDownloadUrl(asset.id)}
            alt={asset.name}
            className="w-full h-full object-cover"
          />
        ) : (
          <File className="h-16 w-16 text-muted-foreground/50" />
        )}
        
        {/* Overlay actions */}
        <div className="absolute inset-0 bg-black/0 group-hover:bg-black/40 transition-colors flex items-center justify-center opacity-0 group-hover:opacity-100">
          <div className="flex gap-2">
            <Button size="icon" variant="secondary" onClick={handleDownload}>
              <Download className="h-4 w-4" />
            </Button>
            {onDelete && (
              <Button 
                size="icon" 
                variant="secondary" 
                className="text-destructive hover:text-destructive"
                onClick={(e) => { e.stopPropagation(); onDelete(); }}
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            )}
          </div>
        </div>
      </div>

      <CardContent className="p-3">
        <div className="flex items-start justify-between gap-2">
          <div className="min-w-0 flex-1">
            <h3 className="font-medium text-sm truncate" title={asset.name}>
              {asset.name}
            </h3>
            <p className="text-xs text-muted-foreground truncate">
              {asset.file_size_formatted}
            </p>
          </div>
          
          <Badge variant="secondary" className={`text-xs shrink-0 ${categoryColors[asset.category]}`}>
            {categoryLabels[asset.category]}
          </Badge>
        </div>
      </CardContent>
    </Card>
  );
}
