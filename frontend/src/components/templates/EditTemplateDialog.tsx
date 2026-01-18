"use client";

import { useState, useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Loader2, Save, Settings } from "lucide-react";

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
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
import { useTemplateSettings } from "@/hooks/useTemplateSettings";
import {
  TemplateSettingsPanel,
  type TemplateSettings,
  DEFAULT_TEMPLATE_SETTINGS,
} from "@/components/templates/TemplateSettingsPanel";
import { getCategoryIcon } from "@/lib/category-icons";
import type { Template, TemplateStatus, Category } from "@/types";
import type { UpdateTemplateSettingsRequest } from "@/types/v2";

const editFormSchema = z.object({
  title: z
    .string()
    .min(1, "Tittel er påkrevd")
    .max(255, "Tittel kan ikke være lenger enn 255 tegn"),
  description: z.string().max(2000, "Beskrivelse kan ikke være lenger enn 2000 tegn").optional(),
  status: z.enum(["draft", "published", "archived"]),
  category_id: z.string().optional(),
});

type EditFormData = z.infer<typeof editFormSchema>;

interface EditTemplateDialogProps {
  template: Template | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess?: () => void;
}

export function EditTemplateDialog({
  template,
  open,
  onOpenChange,
  onSuccess,
}: EditTemplateDialogProps) {
  const [isSaving, setIsSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [categories, setCategories] = useState<Category[]>([]);
  const [categoriesLoading, setCategoriesLoading] = useState(false);
  const [settingsDraft, setSettingsDraft] = useState<TemplateSettings>(DEFAULT_TEMPLATE_SETTINGS);
  const [settingsDirty, setSettingsDirty] = useState(false);
  const [activeTab, setActiveTab] = useState("metadata");

  const {
    register,
    handleSubmit,
    reset,
    setValue,
    watch,
    formState: { errors, isDirty },
  } = useForm<EditFormData>({
    resolver: zodResolver(editFormSchema),
    defaultValues: {
      title: "",
      description: "",
      status: "draft",
      category_id: undefined,
    },
  });

  const selectedStatus = watch("status");
  const selectedCategoryId = watch("category_id");

  const { settings: backendSettings, isLoading: settingsLoading } = useTemplateSettings(
    template?.id ?? null
  );

  const initialSettings = backendSettings
    ? {
        marginTop: backendSettings.margin_top ?? DEFAULT_TEMPLATE_SETTINGS.marginTop,
        marginRight: backendSettings.margin_right ?? DEFAULT_TEMPLATE_SETTINGS.marginRight,
        marginBottom: backendSettings.margin_bottom ?? DEFAULT_TEMPLATE_SETTINGS.marginBottom,
        marginLeft: backendSettings.margin_left ?? DEFAULT_TEMPLATE_SETTINGS.marginLeft,
        headerTemplateId: backendSettings.header_template_id ?? null,
        footerTemplateId: backendSettings.footer_template_id ?? null,
        signatureTemplateId: null,
        channel:
          (backendSettings.channel as TemplateSettings["channel"]) ??
          DEFAULT_TEMPLATE_SETTINGS.channel,
      templateType: (backendSettings.template_type as TemplateSettings["templateType"]) ?? null,
        receiverType: backendSettings.receiver_type ?? null,
        receiver: backendSettings.receiver ?? null,
      extraReceivers: backendSettings.extra_receivers ?? [],
      phases: backendSettings.phases ?? [],
      assignmentTypes: backendSettings.assignment_types ?? [],
      ownershipTypes: backendSettings.ownership_types ?? [],
      departments: backendSettings.departments ?? [],
        emailSubject: backendSettings.email_subject ?? null,
        themeStylesheet: null,
      }
    : DEFAULT_TEMPLATE_SETTINGS;

  // Reset form when template changes
  useEffect(() => {
    if (template && open) {
      reset({
        title: template.title,
        description: template.description || "",
        status: template.status,
        category_id: template.categories?.[0]?.id || undefined,
      });
      setSaveError(null);
      setActiveTab("metadata");
      setSettingsDirty(false);
      setSettingsDraft({ ...DEFAULT_TEMPLATE_SETTINGS, ...initialSettings });
    }
  }, [template, open, reset]);

  useEffect(() => {
    if (open) {
      setSettingsDraft({ ...DEFAULT_TEMPLATE_SETTINGS, ...initialSettings });
      setSettingsDirty(false);
    }
  }, [open, initialSettings]);

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

  const handleClose = () => {
    if (!isSaving) {
      reset();
      setSaveError(null);
      setSettingsDirty(false);
      onOpenChange(false);
    }
  };

  const handleSettingsChange = (nextSettings: TemplateSettings) => {
    setSettingsDraft(nextSettings);
    const baseline = { ...DEFAULT_TEMPLATE_SETTINGS, ...initialSettings };
    setSettingsDirty(JSON.stringify(nextSettings) !== JSON.stringify(baseline));
  };

  const onSubmit = async (data: EditFormData) => {
    if (!template) return;

    setIsSaving(true);
    setSaveError(null);

    try {
      await templateApi.update(template.id, {
        title: data.title,
        description: data.description || undefined,
        status: data.status as TemplateStatus,
        category_ids: data.category_id ? [data.category_id] : [],
      });

      if (settingsDirty) {
        const payload: UpdateTemplateSettingsRequest = {
          channel: settingsDraft.channel,
          template_type: settingsDraft.templateType ?? undefined,
          receiver: settingsDraft.receiver ?? undefined,
          receiver_type: settingsDraft.receiverType ?? undefined,
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
        };

        await templateSettingsApi.updateSettings(template.id, payload);
      }

      // Close dialog and trigger refresh
      onOpenChange(false);
      onSuccess?.();
    } catch (error) {
      console.error("[Edit] Error:", error);
      setSaveError(
        error instanceof Error ? error.message : "Kunne ikke lagre endringer. Prøv igjen."
      );
    } finally {
      setIsSaving(false);
    }
  };

  if (!template) return null;

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-[880px] max-h-[85vh] overflow-hidden flex flex-col">
        <DialogHeader>
          <DialogTitle>Rediger mal</DialogTitle>
          <DialogDescription>
            Rediger metadata for malen. Filen kan ikke endres.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6 overflow-hidden flex flex-col">
          {/* File Info (Read-only) */}
          <div className="p-3 border rounded-lg bg-muted/50">
            <p className="text-sm font-medium">{template.file_name}</p>
            <p className="text-xs text-muted-foreground mt-1">
              Filtype: {template.file_type.toUpperCase()} • Versjon: {template.version}
            </p>
          </div>

          <Tabs
            value={activeTab}
            onValueChange={setActiveTab}
            className="flex-1 overflow-hidden flex flex-col"
          >
            <TabsList>
              <TabsTrigger value="metadata">Detaljer</TabsTrigger>
              <TabsTrigger value="settings" className="flex items-center gap-2">
                <Settings className="h-4 w-4" />
                Innstillinger
              </TabsTrigger>
            </TabsList>

            <TabsContent value="metadata" className="space-y-6 overflow-auto pr-2">
              {/* Title Field */}
              <div className="space-y-2">
                <Label htmlFor="edit-title">Tittel</Label>
                <Input
                  id="edit-title"
                  placeholder="F.eks. Kjøpekontrakt bolig v2.0"
                  {...register("title")}
                  disabled={isSaving}
                />
                {errors.title && (
                  <p className="text-sm text-destructive">{errors.title.message}</p>
                )}
              </div>

              {/* Description Field */}
              <div className="space-y-2">
                <Label htmlFor="edit-description">
                  Beskrivelse{" "}
                  <span className="text-muted-foreground font-normal">(valgfritt)</span>
                </Label>
                <Textarea
                  id="edit-description"
                  placeholder="En kort beskrivelse av malen..."
                  rows={3}
                  {...register("description")}
                  disabled={isSaving}
                />
                {errors.description && (
                  <p className="text-sm text-destructive">{errors.description.message}</p>
                )}
              </div>

              {/* Category Select */}
              <div className="space-y-2">
                <Label htmlFor="edit-category">
                  Kategori{" "}
                  <span className="text-muted-foreground font-normal">(valgfritt)</span>
                </Label>
                <Select
                  value={selectedCategoryId || "none"}
                  onValueChange={(value) =>
                    setValue("category_id", value === "none" ? undefined : value, {
                      shouldDirty: true,
                    })
                  }
                  disabled={isSaving || categoriesLoading}
                >
                  <SelectTrigger id="edit-category">
                    <SelectValue placeholder={categoriesLoading ? "Laster..." : "Velg kategori"} />
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
                    {categories.length === 0 && !categoriesLoading && (
                      <SelectItem value="" disabled>
                        Ingen kategorier funnet
                      </SelectItem>
                    )}
                  </SelectContent>
                </Select>
              </div>

              {/* Status Select */}
              <div className="space-y-2">
                <Label>Status</Label>
                <Select
                  value={selectedStatus}
                  onValueChange={(value) =>
                    setValue("status", value as TemplateStatus, { shouldDirty: true })
                  }
                  disabled={isSaving}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="draft">
                      <span className="flex items-center gap-2">
                        <span className="h-2 w-2 rounded-full bg-amber-500" />
                        Utkast
                      </span>
                    </SelectItem>
                    <SelectItem value="published">
                      <span className="flex items-center gap-2">
                        <span className="h-2 w-2 rounded-full bg-green-500" />
                        Publisert
                      </span>
                    </SelectItem>
                    <SelectItem value="archived">
                      <span className="flex items-center gap-2">
                        <span className="h-2 w-2 rounded-full bg-slate-400" />
                        Arkivert
                      </span>
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </TabsContent>

            <TabsContent value="settings" className="overflow-auto pr-2">
              {settingsLoading ? (
                <div className="text-sm text-muted-foreground py-4">
                  Laster innstillinger...
                </div>
              ) : (
                <TemplateSettingsPanel
                  key={template.id}
                  templateId={template.id}
                  initialSettings={initialSettings}
                  onSettingsChange={handleSettingsChange}
                  showActions={false}
                  disabled={isSaving}
                />
              )}
            </TabsContent>
          </Tabs>

          {/* Save Error */}
          {saveError && (
            <div className="p-3 text-sm text-destructive bg-destructive/10 rounded-lg">
              {saveError}
            </div>
          )}

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={handleClose}
              disabled={isSaving}
            >
              Avbryt
            </Button>
            <Button type="submit" disabled={isSaving || (!isDirty && !settingsDirty)}>
              {isSaving ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Lagrer...
                </>
              ) : (
                <>
                  <Save className="mr-2 h-4 w-4" />
                  Lagre endringer
                </>
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
