"use client";

/**
 * NewTemplateDialog - Create a new template by pasting HTML code
 * Allows users to paste HTML source code from Vitec Next and save to library
 */

import { useState, useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { FileCode, Loader2 } from "lucide-react";

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
import { CodeEditor } from "@/components/editor/CodeEditor";
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

const formSchema = z.object({
  title: z
    .string()
    .min(1, "Tittel er påkrevd")
    .max(255, "Tittel kan ikke være lenger enn 255 tegn"),
  description: z.string().max(1000, "Beskrivelse kan ikke være lenger enn 1000 tegn").optional(),
  status: z.enum(["draft", "published"]).default("draft"),
  category_id: z.string().optional(),
});

type FormData = z.input<typeof formSchema>;

interface NewTemplateDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess?: () => void;
}

export function NewTemplateDialog({
  open,
  onOpenChange,
  onSuccess,
}: NewTemplateDialogProps) {
  const [htmlContent, setHtmlContent] = useState("");
  const [isCreating, setIsCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [categories, setCategories] = useState<Category[]>([]);
  const [categoriesLoading, setCategoriesLoading] = useState(false);
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
  } = useForm<FormData>({
    resolver: zodResolver(formSchema),
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
        .catch((err) => {
          console.error("Failed to fetch categories:", err);
        })
        .finally(() => {
          setCategoriesLoading(false);
        });
    }
  }, [open, categories.length]);

  // Reset form when dialog closes
  useEffect(() => {
    if (!open) {
      reset();
      setHtmlContent("");
      setError(null);
      setSettingsDraft({ ...DEFAULT_TEMPLATE_SETTINGS });
      setSettingsKey((prev) => prev + 1);
    }
  }, [open, reset]);

  const handleSettingsChange = (nextSettings: TemplateSettings) => {
    setSettingsDraft(nextSettings);
  };

  const onSubmit = async (data: FormData) => {
    if (!htmlContent.trim()) {
      setError("HTML-innhold er påkrevd");
      return;
    }

    setIsCreating(true);
    setError(null);

    try {
      // Create a File object from the HTML content
      const blob = new Blob([htmlContent], { type: "text/html" });
      const fileName = `${data.title.replace(/[^a-zA-Z0-9æøåÆØÅ\s-]/g, "").replace(/\s+/g, "-")}.html`;
      const file = new File([blob], fileName, { type: "text/html" });

      // Use the existing upload API
      const created = await templateApi.upload({
        file,
        title: data.title,
        description: data.description || "",
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
        console.error("Failed to save template settings:", settingsError);
        toast({
          title: "Innstillinger ikke lagret",
          description: "Malen ble opprettet, men innstillingene kunne ikke lagres.",
          variant: "destructive",
        });
      }

      onSuccess?.();
      onOpenChange(false);
    } catch (err) {
      console.error("Failed to create template:", err);
      setError(err instanceof Error ? err.message : "Kunne ikke opprette mal");
    } finally {
      setIsCreating(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl h-[85vh] flex flex-col p-0 gap-0">
        <DialogHeader className="px-6 py-4 border-b shrink-0">
          <DialogTitle className="flex items-center gap-2">
            <FileCode className="h-5 w-5 text-primary" />
            Ny mal fra HTML
          </DialogTitle>
          <DialogDescription>
            Lim inn HTML-kildekode fra Vitec Next for å opprette en ny mal i biblioteket.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col flex-1 overflow-hidden">
          {/* Form fields */}
          <div className="px-6 py-4 border-b space-y-4 shrink-0">
            <div className="grid grid-cols-2 gap-4">
              {/* Title */}
              <div className="space-y-2">
                <Label htmlFor="title">Tittel *</Label>
                <Input
                  id="title"
                  placeholder="Navn på malen..."
                  {...register("title")}
                />
                {errors.title && (
                  <p className="text-sm text-red-500">{errors.title.message}</p>
                )}
              </div>

              {/* Category */}
              <div className="space-y-2">
                <Label htmlFor="category">Kategori</Label>
                <Select
                  value={selectedCategoryId || "none"}
                  onValueChange={(value) =>
                    setValue("category_id", value === "none" ? undefined : value)
                  }
                  disabled={categoriesLoading}
                >
                  <SelectTrigger id="category">
                    <SelectValue placeholder="Velg kategori..." />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="none">Ingen kategori</SelectItem>
                    {categories.map((category) => (
                      <SelectItem key={category.id} value={category.id}>
                        {(() => {
                          const IconComponent = getCategoryIcon(category.icon);
                          return <IconComponent className="mr-2 h-4 w-4 text-muted-foreground" />;
                        })()}
                        {category.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="grid grid-cols-1 gap-4">
              {/* Status */}
              <div className="space-y-2">
                <Label htmlFor="status">Status</Label>
                <Select
                  value={watch("status")}
                  onValueChange={(value) => setValue("status", value as "draft" | "published")}
                >
                  <SelectTrigger id="status">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="draft">Utkast</SelectItem>
                    <SelectItem value="published">Publisert</SelectItem>
                  </SelectContent>
                </Select>
              </div>

            </div>

            {/* Description */}
            <div className="space-y-2">
              <Label htmlFor="description">Beskrivelse (valgfritt)</Label>
              <Textarea
                id="description"
                placeholder="Kort beskrivelse av malen..."
                rows={2}
                {...register("description")}
              />
              {errors.description && (
                <p className="text-sm text-red-500">{errors.description.message}</p>
              )}
            </div>

            <details className="rounded-lg border border-[#E5E5E5] p-4">
              <summary className="cursor-pointer text-sm font-medium">
                Avanserte innstillinger
              </summary>
              <div className="mt-4 max-h-[40vh] overflow-y-auto pr-2">
                <TemplateSettingsPanel
                  key={`new-settings-${settingsKey}`}
                  templateId="new"
                  initialSettings={DEFAULT_TEMPLATE_SETTINGS}
                  onSettingsChange={handleSettingsChange}
                  showActions={false}
                  disabled={isCreating}
                />
              </div>
            </details>
          </div>

          {/* Code editor */}
          <div className="flex-1 overflow-hidden flex flex-col">
            <div className="px-6 py-2 border-b bg-muted/30 flex items-center justify-between shrink-0">
              <Label className="text-sm font-medium">HTML-kildekode *</Label>
              <span className="text-xs text-muted-foreground">
                {htmlContent.length.toLocaleString()} tegn
              </span>
            </div>
            <div className="flex-1 overflow-hidden">
              <CodeEditor
                value={htmlContent}
                onChange={setHtmlContent}
                language="html"
                theme="vs-dark"
              />
            </div>
          </div>

          {/* Error message */}
          {error && (
            <div className="px-6 py-2 bg-red-50 border-t border-red-200 text-red-700 text-sm shrink-0">
              {error}
            </div>
          )}

          {/* Footer */}
          <DialogFooter className="px-6 py-4 border-t shrink-0">
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={isCreating}
            >
              Avbryt
            </Button>
            <Button type="submit" disabled={isCreating || !htmlContent.trim()}>
              {isCreating ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Oppretter...
                </>
              ) : (
                <>
                  <FileCode className="h-4 w-4 mr-2" />
                  Opprett mal
                </>
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
