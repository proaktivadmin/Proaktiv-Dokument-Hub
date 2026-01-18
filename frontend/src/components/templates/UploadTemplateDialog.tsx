"use client";

import { useState, useCallback, useEffect, useRef } from "react";
import { useDropzone } from "react-dropzone";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Upload, FileText, X, Loader2 } from "lucide-react";

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
import { templateApi, categoryApi } from "@/lib/api";
import { templateSettingsApi } from "@/lib/api/template-settings";
import { useToast } from "@/hooks/use-toast";
import {
  TemplateSettingsPanel,
  type TemplateSettings,
  DEFAULT_TEMPLATE_SETTINGS,
} from "@/components/templates/TemplateSettingsPanel";
import { getCategoryIcon } from "@/lib/category-icons";
import type { TemplateStatus, Category } from "@/types";

const ALLOWED_FILE_TYPES = {
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
  "application/msword": [".doc"],
  "application/pdf": [".pdf"],
  "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [".xlsx"],
  "application/vnd.ms-excel": [".xls"],
  "text/html": [".html", ".htm"],
};

const ALLOWED_EXTENSIONS = ["docx", "doc", "pdf", "xlsx", "xls", "html", "htm"];

const uploadFormSchema = z.object({
  title: z
    .string()
    .min(1, "Tittel er påkrevd")
    .max(255, "Tittel kan ikke være lenger enn 255 tegn"),
  description: z.string().max(1000, "Beskrivelse kan ikke være lenger enn 1000 tegn").optional(),
  status: z.enum(["draft", "published"]).default("draft"),
  category_id: z.string().optional(),
});

type UploadFormData = z.infer<typeof uploadFormSchema>;

interface UploadTemplateDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess?: () => void;
}

export function UploadTemplateDialog({
  open,
  onOpenChange,
  onSuccess,
}: UploadTemplateDialogProps) {
  const [file, setFile] = useState<File | null>(null);
  const [fileError, setFileError] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [categories, setCategories] = useState<Category[]>([]);
  const [categoriesLoading, setCategoriesLoading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [settingsDraft, setSettingsDraft] = useState<TemplateSettings>(DEFAULT_TEMPLATE_SETTINGS);
  const [settingsKey, setSettingsKey] = useState(0);
  const { toast } = useToast();

  const {
    register,
    handleSubmit,
    reset,
    setValue,
    watch,
    formState: { errors },
  } = useForm<UploadFormData>({
    resolver: zodResolver(uploadFormSchema),
    defaultValues: {
      title: "",
      description: "",
      status: "draft",
      category_id: undefined,
    },
  });

  const selectedCategoryId = watch("category_id");

  // Fetch categories when dialog opens
  useEffect(() => {
    if (open && categories.length === 0) {
      setCategoriesLoading(true);
      categoryApi
        .list()
        .then((data) => {
          setCategories(data);
        })
        .catch((error) => {
          console.error("Failed to load categories:", error);
        })
        .finally(() => {
          setCategoriesLoading(false);
        });
    }
  }, [open, categories.length]);

  const onDrop = useCallback((acceptedFiles: File[], rejectedFiles: unknown[]) => {
    console.log("[Dropzone] onDrop called:", { acceptedFiles, rejectedFiles });
    setFileError(null);

    if (rejectedFiles.length > 0) {
      setFileError("Ugyldig filtype. Tillatte formater: html, docx, doc, pdf, xlsx, xls");
      return;
    }

    if (acceptedFiles.length > 0) {
      const selectedFile = acceptedFiles[0];
      const extension = selectedFile.name.split(".").pop()?.toLowerCase();

      console.log("[Dropzone] File selected:", {
        name: selectedFile.name,
        size: selectedFile.size,
        type: selectedFile.type,
        extension,
      });

      if (!extension || !ALLOWED_EXTENSIONS.includes(extension)) {
        setFileError("Ugyldig filtype. Tillatte formater: html, docx, doc, pdf, xlsx, xls");
        return;
      }

      setFile(selectedFile);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: ALLOWED_FILE_TYPES,
    maxFiles: 1,
    multiple: false,
    useFsAccessApi: false,
    noClick: true, // We handle click manually for better compatibility
    noKeyboard: false,
  });

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      onDrop(Array.from(files), []);
    }
    // Reset input so same file can be selected again
    e.target.value = "";
  };

  const handleOpenFilePicker = () => {
    fileInputRef.current?.click();
  };

  const removeFile = () => {
    setFile(null);
    setFileError(null);
  };

  const handleClose = () => {
    if (!isUploading) {
      setFile(null);
      setFileError(null);
      setUploadError(null);
      reset();
      setSettingsDraft({ ...DEFAULT_TEMPLATE_SETTINGS });
      setSettingsKey((prev) => prev + 1);
      onOpenChange(false);
    }
  };

  const handleSettingsChange = (nextSettings: TemplateSettings) => {
    setSettingsDraft(nextSettings);
  };

  const onSubmit = async (data: UploadFormData) => {
    if (!file) {
      setFileError("Vennligst velg en fil å laste opp");
      return;
    }

    setIsUploading(true);
    setUploadError(null);

    try {
      const created = await templateApi.upload({
        file,
        title: data.title,
        description: data.description || undefined,
        status: data.status as TemplateStatus,
        category_id: data.category_id || undefined,
      });

      try {
        await templateSettingsApi.updateSettings(created.id, {
          channel: settingsDraft.channel,
          template_type: settingsDraft.templateType ?? undefined,
          receiver_type: settingsDraft.receiverType ?? undefined,
          receiver: settingsDraft.receiver ?? undefined,
          extra_receivers: settingsDraft.extraReceivers,
          phases: settingsDraft.phases,
          assignment_types: settingsDraft.assignmentTypes,
          ownership_types: settingsDraft.ownershipTypes,
          departments: settingsDraft.departments,
          email_subject: settingsDraft.emailSubject ?? undefined,
          header_template_id: settingsDraft.headerTemplateId ?? undefined,
          footer_template_id: settingsDraft.footerTemplateId ?? undefined,
          margin_top: settingsDraft.marginTop,
          margin_bottom: settingsDraft.marginBottom,
          margin_left: settingsDraft.marginLeft,
          margin_right: settingsDraft.marginRight,
        });
      } catch (settingsError) {
        console.error("[Upload] Settings Error:", settingsError);
        toast({
          title: "Innstillinger ikke lagret",
          description: "Malen ble opprettet, men innstillingene kunne ikke lagres.",
          variant: "destructive",
        });
      }

      // Reset form and close dialog on success
      setFile(null);
      reset();
      setSettingsDraft({ ...DEFAULT_TEMPLATE_SETTINGS });
      setSettingsKey((prev) => prev + 1);
      onOpenChange(false);
      onSuccess?.();
    } catch (error) {
      console.error("[Upload] Error:", error);
      setUploadError(
        error instanceof Error ? error.message : "Opplasting feilet. Prøv igjen."
      );
    } finally {
      setIsUploading(false);
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Last opp mal</DialogTitle>
          <DialogDescription>
            Last opp en ny dokumentmal til biblioteket. Støttede formater: HTML,
            Word, PDF og Excel.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          {/* File Upload Area */}
          <div className="space-y-2">
            <Label>Fil</Label>
            {!file ? (
              <div
                {...getRootProps()}
                onClick={handleOpenFilePicker}
                className={`
                  border-2 border-dashed rounded-lg p-8 text-center cursor-pointer
                  transition-colors
                  ${
                    isDragActive
                      ? "border-primary bg-primary/5"
                      : "border-muted-foreground/25 hover:border-primary/50"
                  }
                  ${fileError ? "border-destructive" : ""}
                `}
              >
                {/* Hidden file input for manual click handling */}
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".html,.htm,.docx,.doc,.pdf,.xlsx,.xls"
                  onChange={handleFileInputChange}
                  style={{ display: "none" }}
                />
                {/* Keep dropzone input for drag-and-drop */}
                <input {...getInputProps()} />
                <Upload className="mx-auto h-10 w-10 text-muted-foreground mb-3" />
                <p className="text-sm text-muted-foreground mb-1">
                  {isDragActive
                    ? "Slipp filen her..."
                    : "Dra og slipp en fil her, eller klikk for å velge"}
                </p>
                <p className="text-xs text-muted-foreground mt-2">
                  Støttede formater: .html, .docx, .doc, .pdf, .xlsx, .xls
                </p>
              </div>
            ) : (
              <div className="flex items-center gap-3 p-3 border rounded-lg bg-muted/50">
                <FileText className="h-8 w-8 text-primary flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">{file.name}</p>
                  <p className="text-xs text-muted-foreground">
                    {formatFileSize(file.size)}
                  </p>
                </div>
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  onClick={removeFile}
                  disabled={isUploading}
                >
                  <X className="h-4 w-4" />
                  <span className="sr-only">Fjern fil</span>
                </Button>
              </div>
            )}
            {fileError && (
              <p className="text-sm text-destructive">{fileError}</p>
            )}
          </div>

          {/* Title Field */}
          <div className="space-y-2">
            <Label htmlFor="title">Tittel</Label>
            <Input
              id="title"
              placeholder="F.eks. Kjøpekontrakt bolig v2.0"
              {...register("title")}
              disabled={isUploading}
            />
            {errors.title && (
              <p className="text-sm text-destructive">{errors.title.message}</p>
            )}
          </div>

          {/* Description Field */}
          <div className="space-y-2">
            <Label htmlFor="description">
              Beskrivelse{" "}
              <span className="text-muted-foreground font-normal">
                (valgfritt)
              </span>
            </Label>
            <Textarea
              id="description"
              placeholder="En kort beskrivelse av malen..."
              rows={3}
              {...register("description")}
              disabled={isUploading}
            />
            {errors.description && (
              <p className="text-sm text-destructive">
                {errors.description.message}
              </p>
            )}
          </div>

          {/* Category Select */}
          <div className="space-y-2">
            <Label htmlFor="category">
              Kategori{" "}
              <span className="text-muted-foreground font-normal">
                (valgfritt)
              </span>
            </Label>
            <Select
              value={selectedCategoryId || "none"}
              onValueChange={(value) =>
                setValue("category_id", value === "none" ? undefined : value)
              }
              disabled={isUploading || categoriesLoading}
            >
              <SelectTrigger id="category">
                <SelectValue placeholder={categoriesLoading ? "Laster..." : "Velg kategori"} />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="none">Ingen kategori</SelectItem>
                {categories.length === 0 && !categoriesLoading ? (
                  <div className="px-2 py-4 text-sm text-muted-foreground text-center">
                    Ingen kategorier funnet
                  </div>
                ) : (
                  categories.map((category) => (
                    <SelectItem key={category.id} value={category.id}>
                      {(() => {
                        const IconComponent = getCategoryIcon(category.icon);
                        return <IconComponent className="mr-2 h-4 w-4 text-muted-foreground" />;
                      })()}
                      {category.name}
                    </SelectItem>
                  ))
                )}
              </SelectContent>
            </Select>
          </div>

          {/* Status Toggle */}
          <div className="space-y-2">
            <Label>Status</Label>
            <div className="flex gap-4">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  value="draft"
                  {...register("status")}
                  disabled={isUploading}
                  className="h-4 w-4 text-primary"
                />
                <span className="text-sm">Utkast</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  value="published"
                  {...register("status")}
                  disabled={isUploading}
                  className="h-4 w-4 text-primary"
                />
                <span className="text-sm">Publisert</span>
              </label>
            </div>
          </div>

          <details className="rounded-lg border border-[#E5E5E5] p-4">
            <summary className="cursor-pointer text-sm font-medium">
              Avanserte innstillinger
            </summary>
            <div className="mt-4 max-h-[40vh] overflow-y-auto pr-2">
              <TemplateSettingsPanel
                key={`upload-settings-${settingsKey}`}
                templateId="upload"
                initialSettings={DEFAULT_TEMPLATE_SETTINGS}
                onSettingsChange={handleSettingsChange}
                showActions={false}
                disabled={isUploading}
              />
            </div>
          </details>

          {/* Upload Error */}
          {uploadError && (
            <div className="p-3 text-sm text-destructive bg-destructive/10 rounded-lg">
              {uploadError}
            </div>
          )}

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={handleClose}
              disabled={isUploading}
            >
              Avbryt
            </Button>
            <Button type="submit" disabled={isUploading || !file}>
              {isUploading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Laster opp...
                </>
              ) : (
                <>
                  <Upload className="mr-2 h-4 w-4" />
                  Last opp
                </>
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
