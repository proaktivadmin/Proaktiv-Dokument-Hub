"use client";

import { useState, useCallback } from "react";
import { Image as ImageIcon, Plus, Upload } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Skeleton } from "@/components/ui/skeleton";
import { AssetCard } from "./AssetCard";
import { AssetUploadDialog } from "./AssetUploadDialog";
import { AssetPreviewDialog } from "./AssetPreviewDialog";
import { assetsApi } from "@/lib/api/assets";
import type { CompanyAsset, AssetCategory } from "@/types/v3";

interface AssetGalleryProps {
  assets: CompanyAsset[];
  categoryCounts: Record<AssetCategory, number>;
  isLoading: boolean;
  scope: "global" | "office" | "employee";
  scopeId?: string;
  onRefresh: () => void;
}

const categories: { value: AssetCategory | "all"; label: string }[] = [
  { value: "all", label: "Alle" },
  { value: "logo", label: "Logoer" },
  { value: "photo", label: "Foto" },
  { value: "marketing", label: "Markedsføring" },
  { value: "document", label: "Dokumenter" },
  { value: "other", label: "Annet" },
];

export function AssetGallery({
  assets,
  categoryCounts,
  isLoading,
  scope,
  scopeId,
  onRefresh,
}: AssetGalleryProps) {
  const [selectedCategory, setSelectedCategory] = useState<AssetCategory | "all">("all");
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [previewAsset, setPreviewAsset] = useState<CompanyAsset | null>(null);

  const filteredAssets = selectedCategory === "all"
    ? assets
    : assets.filter((a) => a.category === selectedCategory);

  const handleDelete = useCallback(async (asset: CompanyAsset) => {
    if (!confirm(`Er du sikker på at du vil slette "${asset.name}"?`)) return;
    
    try {
      await assetsApi.delete(asset.id);
      onRefresh();
    } catch (err) {
      console.error("Failed to delete asset:", err);
    }
  }, [onRefresh]);

  if (isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-10 w-full max-w-lg" />
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
          {Array.from({ length: 10 }).map((_, i) => (
            <Skeleton key={i} className="aspect-square" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Category tabs */}
      <div className="flex items-center justify-between gap-4 flex-wrap">
        <Tabs value={selectedCategory} onValueChange={(v) => setSelectedCategory(v as AssetCategory | "all")}>
          <TabsList>
            {categories.map((cat) => (
              <TabsTrigger key={cat.value} value={cat.value} className="gap-1.5">
                {cat.label}
                {cat.value !== "all" && (
                  <span className="text-xs text-muted-foreground">
                    ({categoryCounts[cat.value as AssetCategory] || 0})
                  </span>
                )}
              </TabsTrigger>
            ))}
          </TabsList>
        </Tabs>

        <Button onClick={() => setUploadDialogOpen(true)}>
          <Upload className="h-4 w-4 mr-2" />
          Last opp fil
        </Button>
      </div>

      {/* Gallery grid */}
      {filteredAssets.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-16 text-center">
          <ImageIcon className="h-16 w-16 text-muted-foreground/50 mb-4" />
          <h3 className="text-lg font-medium mb-1">Ingen filer</h3>
          <p className="text-sm text-muted-foreground mb-4">
            {selectedCategory !== "all"
              ? "Ingen filer i denne kategorien"
              : "Last opp din første fil for å komme i gang"}
          </p>
          <Button onClick={() => setUploadDialogOpen(true)}>
            <Plus className="h-4 w-4 mr-2" />
            Last opp fil
          </Button>
        </div>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
          {filteredAssets.map((asset) => (
            <AssetCard
              key={asset.id}
              asset={asset}
              onClick={() => setPreviewAsset(asset)}
              onDelete={() => handleDelete(asset)}
            />
          ))}
        </div>
      )}

      {/* Upload dialog */}
      <AssetUploadDialog
        open={uploadDialogOpen}
        onOpenChange={setUploadDialogOpen}
        scope={scope}
        scopeId={scopeId}
        onSuccess={onRefresh}
      />

      {/* Preview dialog */}
      <AssetPreviewDialog
        asset={previewAsset}
        open={!!previewAsset}
        onOpenChange={(open) => !open && setPreviewAsset(null)}
      />
    </div>
  );
}
