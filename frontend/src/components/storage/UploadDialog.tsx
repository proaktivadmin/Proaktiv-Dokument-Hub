"use client";

import { useState, useCallback, useRef } from "react";
import { useDropzone } from "react-dropzone";
import { Upload, FileText, X, Loader2, CheckCircle } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { storageApi } from "@/lib/api";
import { cn } from "@/lib/utils";

interface UploadDialogProps {
  open: boolean;
  currentPath: string;
  onOpenChange: (open: boolean) => void;
  onComplete: () => void;
}

interface UploadFile {
  file: File;
  status: "pending" | "uploading" | "success" | "error";
  error?: string;
}

export function UploadDialog({
  open,
  currentPath,
  onOpenChange,
  onComplete,
}: UploadDialogProps) {
  const [files, setFiles] = useState<UploadFile[]>([]);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const newFiles = acceptedFiles.map((file) => ({
      file,
      status: "pending" as const,
    }));
    setFiles((prev) => [...prev, ...newFiles]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    noClick: true,
  });

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = e.target.files;
    if (selectedFiles && selectedFiles.length > 0) {
      onDrop(Array.from(selectedFiles));
    }
    e.target.value = "";
  };

  const handleOpenFilePicker = () => {
    fileInputRef.current?.click();
  };

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const handleUpload = async () => {
    if (files.length === 0) return;

    setUploading(true);

    for (let i = 0; i < files.length; i++) {
      if (files[i].status !== "pending") continue;

      setFiles((prev) =>
        prev.map((f, idx) =>
          idx === i ? { ...f, status: "uploading" as const } : f
        )
      );

      try {
        await storageApi.upload(currentPath, files[i].file);
        setFiles((prev) =>
          prev.map((f, idx) =>
            idx === i ? { ...f, status: "success" as const } : f
          )
        );
      } catch (err) {
        setFiles((prev) =>
          prev.map((f, idx) =>
            idx === i
              ? {
                  ...f,
                  status: "error" as const,
                  error: err instanceof Error ? err.message : "Opplasting feilet",
                }
              : f
          )
        );
      }
    }

    setUploading(false);
  };

  const handleClose = () => {
    if (uploading) return;

    const hasUploaded = files.some((f) => f.status === "success");
    setFiles([]);
    onOpenChange(false);

    if (hasUploaded) {
      onComplete();
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const pendingFiles = files.filter((f) => f.status === "pending");
  const allDone = files.length > 0 && pendingFiles.length === 0 && !uploading;

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Last opp filer</DialogTitle>
          <DialogDescription>
            Last opp filer til: {currentPath}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {/* Drop zone */}
          <div
            {...getRootProps()}
            onClick={handleOpenFilePicker}
            className={cn(
              "border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors",
              isDragActive
                ? "border-primary bg-primary/5"
                : "border-muted-foreground/25 hover:border-primary/50"
            )}
          >
            <input
              ref={fileInputRef}
              type="file"
              multiple
              onChange={handleFileInputChange}
              style={{ display: "none" }}
            />
            <input {...getInputProps()} />
            <Upload className="mx-auto h-10 w-10 text-muted-foreground mb-3" />
            <p className="text-sm text-muted-foreground">
              {isDragActive
                ? "Slipp filene her..."
                : "Dra og slipp filer her, eller klikk for å velge"}
            </p>
          </div>

          {/* File list */}
          {files.length > 0 && (
            <div className="max-h-48 overflow-auto space-y-2">
              {files.map((item, index) => (
                <div
                  key={`${item.file.name}-${index}`}
                  className={cn(
                    "flex items-center gap-3 p-3 border rounded-lg",
                    item.status === "success" && "bg-green-50 border-green-200",
                    item.status === "error" && "bg-red-50 border-red-200"
                  )}
                >
                  {item.status === "uploading" ? (
                    <Loader2 className="h-5 w-5 animate-spin text-primary" />
                  ) : item.status === "success" ? (
                    <CheckCircle className="h-5 w-5 text-green-500" />
                  ) : (
                    <FileText className="h-5 w-5 text-muted-foreground" />
                  )}

                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">
                      {item.file.name}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {item.error || formatFileSize(item.file.size)}
                    </p>
                  </div>

                  {item.status === "pending" && (
                    <Button
                      type="button"
                      variant="ghost"
                      size="icon"
                      onClick={() => removeFile(index)}
                      disabled={uploading}
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={handleClose} disabled={uploading}>
            {allDone ? "Lukk" : "Avbryt"}
          </Button>
          {!allDone && (
            <Button
              onClick={handleUpload}
              disabled={uploading || pendingFiles.length === 0}
            >
              {uploading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Laster opp...
                </>
              ) : (
                <>
                  <Upload className="mr-2 h-4 w-4" />
                  Last opp ({pendingFiles.length})
                </>
              )}
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
