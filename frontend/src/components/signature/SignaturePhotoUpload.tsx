"use client";

import { useCallback, useRef, useState } from "react";
import { Camera, X, Check } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useSignaturePhotoUpload } from "@/hooks/v3/useSignaturePhotoUpload";

const MAX_SIZE = 5 * 1024 * 1024; // 5 MB
const ACCEPTED = ".jpg,.jpeg,.png";

interface SignaturePhotoUploadProps {
  employeeId: string;
  onUploaded: () => void;
}

export function SignaturePhotoUpload({ employeeId, onUploaded }: SignaturePhotoUploadProps) {
  const { upload, isUploading, error } = useSignaturePhotoUpload(employeeId);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (file.size > MAX_SIZE) {
      alert("Bildet må være mindre enn 5 MB.");
      return;
    }

    if (!file.type.startsWith("image/")) {
      alert("Kun JPEG og PNG er støttet.");
      return;
    }

    setSelectedFile(file);
    const url = URL.createObjectURL(file);
    setPreview(url);
  }, []);

  const handleCancel = useCallback(() => {
    setSelectedFile(null);
    if (preview) URL.revokeObjectURL(preview);
    setPreview(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  }, [preview]);

  const handleConfirm = useCallback(async () => {
    if (!selectedFile) return;

    try {
      await upload(selectedFile);
      handleCancel();
      onUploaded();
    } catch {
      // Error state handled by hook
    }
  }, [selectedFile, upload, handleCancel, onUploaded]);

  return (
    <div className="space-y-2">
      <input
        ref={fileInputRef}
        type="file"
        accept={ACCEPTED}
        onChange={handleFileSelect}
        className="hidden"
      />

      {preview ? (
        <div className="flex items-center gap-3">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={preview}
            alt="Forhåndsvisning"
            className="h-16 w-16 rounded-lg object-cover border"
          />
          <div className="flex gap-2">
            <Button
              size="sm"
              onClick={handleConfirm}
              disabled={isUploading}
            >
              <Check className="mr-1 h-3 w-3" />
              {isUploading ? "Laster opp..." : "Bekreft"}
            </Button>
            <Button
              size="sm"
              variant="outline"
              onClick={handleCancel}
              disabled={isUploading}
            >
              <X className="mr-1 h-3 w-3" />
              Avbryt
            </Button>
          </div>
        </div>
      ) : (
        <Button
          size="sm"
          variant="outline"
          onClick={() => fileInputRef.current?.click()}
        >
          <Camera className="mr-2 h-4 w-4" />
          Last opp nytt bilde
        </Button>
      )}

      {error && (
        <p className="text-xs text-destructive">{error}</p>
      )}
    </div>
  );
}
