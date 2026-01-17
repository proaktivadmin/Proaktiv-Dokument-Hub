"use client";

import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { Upload, X, File as FileIcon } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
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
import { assetsApi } from "@/lib/api/assets";
import type { AssetCategory } from "@/types/v3";

interface AssetUploadDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  scope: "global" | "office" | "employee";
  scopeId?: string;
  onSuccess: () => void;
}

const categories: { value: AssetCategory; label: string }[] = [
  { value: "logo", label: "Logo" },
  { value: "photo", label: "Foto" },
  { value: "marketing", label: "Markedsføring" },
  { value: "document", label: "Dokument" },
  { value: "other", label: "Annet" },
];

export function AssetUploadDialog({
  open,
  onOpenChange,
  scope,
  scopeId,
  onSuccess,
}: AssetUploadDialogProps) {
  const [file, setFile] = useState<File | null>(null);
  const [name, setName] = useState("");
  const [category, setCategory] = useState<AssetCategory>("other");
  const [altText, setAltText] = useState("");
  const [usageNotes, setUsageNotes] = useState("");
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      const newFile = acceptedFiles[0];
      setFile(newFile);
      if (!name) {
        // Use filename without extension as default name
        setName(newFile.name.replace(/\.[^/.]+$/, ""));
      }
      // Auto-detect category
      if (newFile.type.startsWith("image/")) {
        if (newFile.name.toLowerCase().includes("logo")) {
          setCategory("logo");
        } else {
          setCategory("photo");
        }
      } else if (newFile.type === "application/pdf") {
        setCategory("document");
      }
    }
  }, [name]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    multiple: false,
    accept: {
      "image/*": [".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"],
      "application/pdf": [".pdf"],
      "application/msword": [".doc"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
    },
  });

  const handleSubmit = async () => {
    if (!file || !name) return;

    setIsUploading(true);
    setError(null);

    try {
      await assetsApi.upload({
        file,
        name,
        category,
        is_global: scope === "global",
        office_id: scope === "office" ? scopeId : undefined,
        employee_id: scope === "employee" ? scopeId : undefined,
        alt_text: altText || undefined,
        usage_notes: usageNotes || undefined,
      });

      onSuccess();
      onOpenChange(false);
      resetForm();
    } catch (err) {
      console.error("Upload failed:", err);
      setError(err instanceof Error ? err.message : "Opplasting feilet");
    } finally {
      setIsUploading(false);
    }
  };

  const resetForm = () => {
    setFile(null);
    setName("");
    setCategory("other");
    setAltText("");
    setUsageNotes("");
    setError(null);
  };

  const handleClose = () => {
    onOpenChange(false);
    resetForm();
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle>Last opp fil</DialogTitle>
          <DialogDescription>
            Last opp en fil til{" "}
            {scope === "global" ? "den globale filsamlingen" : "dette området"}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {/* Dropzone */}
          {!file ? (
            <div
              {...getRootProps()}
              className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
                isDragActive
                  ? "border-primary bg-primary/5"
                  : "border-muted-foreground/25 hover:border-primary/50"
              }`}
            >
              <input {...getInputProps()} />
              <Upload className="h-10 w-10 mx-auto text-muted-foreground mb-3" />
              <p className="text-sm text-muted-foreground">
                {isDragActive
                  ? "Slipp filen her..."
                  : "Dra og slipp en fil her, eller klikk for å velge"}
              </p>
              <p className="text-xs text-muted-foreground mt-1">
                Bilder, PDF og dokumenter støttes
              </p>
            </div>
          ) : (
            <div className="flex items-center gap-3 p-3 bg-muted rounded-lg">
              <FileIcon className="h-8 w-8 text-muted-foreground" />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">{file.name}</p>
                <p className="text-xs text-muted-foreground">
                  {(file.size / 1024).toFixed(1)} KB
                </p>
              </div>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setFile(null)}
                className="shrink-0"
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          )}

          {/* Name */}
          <div className="space-y-2">
            <Label htmlFor="name">Navn *</Label>
            <Input
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Proaktiv logo primær"
            />
          </div>

          {/* Category */}
          <div className="space-y-2">
            <Label htmlFor="category">Kategori</Label>
            <Select value={category} onValueChange={(v) => setCategory(v as AssetCategory)}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {categories.map((cat) => (
                  <SelectItem key={cat.value} value={cat.value}>
                    {cat.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Alt text */}
          <div className="space-y-2">
            <Label htmlFor="altText">Alt-tekst (for bilder)</Label>
            <Input
              id="altText"
              value={altText}
              onChange={(e) => setAltText(e.target.value)}
              placeholder="Beskrivelse av bildet"
            />
          </div>

          {/* Usage notes */}
          <div className="space-y-2">
            <Label htmlFor="usageNotes">Bruksnotater</Label>
            <Textarea
              id="usageNotes"
              value={usageNotes}
              onChange={(e) => setUsageNotes(e.target.value)}
              placeholder="Notater om bruk av denne filen..."
              rows={2}
            />
          </div>

          {error && (
            <div className="p-3 bg-destructive/10 text-destructive text-sm rounded-md">
              {error}
            </div>
          )}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={handleClose}>
            Avbryt
          </Button>
          <Button
            onClick={handleSubmit}
            disabled={!file || !name || isUploading}
          >
            {isUploading ? "Laster opp..." : "Last opp"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
