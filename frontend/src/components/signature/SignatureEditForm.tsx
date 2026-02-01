"use client";

import { useCallback, useState } from "react";
import { Pencil, RotateCcw, Save, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useToast } from "@/hooks/use-toast";
import {
  useSignatureOverrides,
  type SignatureOverrideInput,
} from "@/hooks/v3/useSignatureOverrides";
// Photo upload hidden for now — pending WebDAV configuration
// import { SignaturePhotoUpload } from "./SignaturePhotoUpload";

interface SignatureEditFormProps {
  employeeId: string;
  /** Current values from signature response (used as defaults when no overrides) */
  currentName: string;
  currentEmail: string;
  onSaved: () => void;
}

interface FormFields {
  display_name: string;
  job_title: string;
  mobile_phone: string;
  email: string;
  office_name: string;
  facebook_url: string;
  instagram_url: string;
  linkedin_url: string;
  employee_url: string;
}

const EMPTY_FIELDS: FormFields = {
  display_name: "",
  job_title: "",
  mobile_phone: "",
  email: "",
  office_name: "",
  facebook_url: "",
  instagram_url: "",
  linkedin_url: "",
  employee_url: "",
};

export function SignatureEditForm({
  employeeId,
  currentName,
  currentEmail,
  onSaved,
}: SignatureEditFormProps) {
  const { overrides, isSaving, save, reset } = useSignatureOverrides(employeeId);
  const { toast } = useToast();
  const [isEditing, setIsEditing] = useState(false);
  const [fields, setFields] = useState<FormFields>(EMPTY_FIELDS);

  const hasOverrides = overrides !== null;

  /** Build FormFields from current overrides (or empty) */
  const fieldsFromOverrides = useCallback((): FormFields => {
    if (!overrides) return EMPTY_FIELDS;
    return {
      display_name: overrides.display_name ?? "",
      job_title: overrides.job_title ?? "",
      mobile_phone: overrides.mobile_phone ?? "",
      email: overrides.email ?? "",
      office_name: overrides.office_name ?? "",
      facebook_url: overrides.facebook_url ?? "",
      instagram_url: overrides.instagram_url ?? "",
      linkedin_url: overrides.linkedin_url ?? "",
      employee_url: overrides.employee_url ?? "",
    };
  }, [overrides]);

  const handleChange = useCallback(
    (field: keyof FormFields) => (e: React.ChangeEvent<HTMLInputElement>) => {
      setFields((prev) => ({ ...prev, [field]: e.target.value }));
    },
    []
  );

  const handleSave = useCallback(async () => {
    // Only send non-empty fields as overrides (empty = use original)
    const data: SignatureOverrideInput = {};
    for (const [key, value] of Object.entries(fields)) {
      const trimmed = value.trim();
      if (trimmed) {
        (data as Record<string, string>)[key] = trimmed;
      } else {
        (data as Record<string, null>)[key] = null;
      }
    }

    try {
      await save(data);
      setIsEditing(false);
      onSaved();
      toast({
        title: "Endringer lagret",
        description: "Signaturen er oppdatert med dine tilpasninger.",
      });
    } catch {
      toast({
        title: "Kunne ikke lagre",
        description: "Prøv igjen eller kontakt IT-avdelingen.",
        variant: "destructive",
      });
    }
  }, [fields, save, onSaved, toast]);

  const handleReset = useCallback(async () => {
    await reset();
    setFields(EMPTY_FIELDS);
    setIsEditing(false);
    onSaved();
    toast({
      title: "Tilbakestilt",
      description: "Signaturen bruker nå de opprinnelige verdiene.",
    });
  }, [reset, onSaved, toast]);

  const handleCancel = useCallback(() => {
    setFields(fieldsFromOverrides());
    setIsEditing(false);
  }, [fieldsFromOverrides]);

  return (
    <div className="rounded-lg border bg-white shadow-card ring-1 ring-black/3">
      <div className="flex items-center justify-between px-6 py-4">
        <div>
          <p className="text-sm font-medium text-foreground">
            {currentName || "Ansatt"}
          </p>
          <p className="text-xs text-muted-foreground">{currentEmail}</p>
        </div>
        {!isEditing ? (
          <Button
            size="sm"
            variant="outline"
            onClick={() => { setFields(fieldsFromOverrides()); setIsEditing(true); }}
          >
            <Pencil className="mr-2 h-3 w-3" />
            Rediger
          </Button>
        ) : (
          <div className="flex gap-2">
            <Button size="sm" onClick={handleSave} disabled={isSaving}>
              <Save className="mr-1 h-3 w-3" />
              {isSaving ? "Lagrer..." : "Lagre"}
            </Button>
            <Button
              size="sm"
              variant="outline"
              onClick={handleCancel}
              disabled={isSaving}
            >
              <X className="mr-1 h-3 w-3" />
              Avbryt
            </Button>
          </div>
        )}
      </div>

      {isEditing && (
        <div className="space-y-6 border-t px-6 py-4">
          {/* Photo upload */}
          {/* Contact info */}
          <div className="space-y-3">
            <p className="text-xs font-semibold uppercase tracking-wider text-foreground/60">
              Kontaktinfo
            </p>
            <p className="text-xs text-muted-foreground">
              La felt stå tomme for å bruke de opprinnelige verdiene fra systemet.
            </p>
            <div className="grid gap-3 sm:grid-cols-2">
              <FieldInput label="Navn" value={fields.display_name} onChange={handleChange("display_name")} placeholder="F.eks. Ola Nordmann" />
              <FieldInput label="Tittel" value={fields.job_title} onChange={handleChange("job_title")} placeholder="F.eks. Eiendomsmegler" />
              <FieldInput label="Telefon" value={fields.mobile_phone} onChange={handleChange("mobile_phone")} placeholder="F.eks. 98 76 54 32" />
              <FieldInput label="E-post" value={fields.email} onChange={handleChange("email")} placeholder="F.eks. ola@proaktiv.no" type="email" />
              <FieldInput label="Kontor/avdeling" value={fields.office_name} onChange={handleChange("office_name")} placeholder="F.eks. Proaktiv Oslo" />
            </div>
          </div>

          {/* Social links */}
          <div className="space-y-3">
            <p className="text-xs font-semibold uppercase tracking-wider text-foreground/60">
              Lenker
            </p>
            <div className="grid gap-3 sm:grid-cols-2">
              <FieldInput label="Hjemmeside" value={fields.employee_url} onChange={handleChange("employee_url")} placeholder="https://proaktiv.no/ansatt/..." />
              <FieldInput label="Facebook" value={fields.facebook_url} onChange={handleChange("facebook_url")} placeholder="https://facebook.com/..." />
              <FieldInput label="Instagram" value={fields.instagram_url} onChange={handleChange("instagram_url")} placeholder="https://instagram.com/..." />
              <FieldInput label="LinkedIn" value={fields.linkedin_url} onChange={handleChange("linkedin_url")} placeholder="https://linkedin.com/..." />
            </div>
          </div>

          {/* Reset button */}
          {hasOverrides && (
            <div className="border-t pt-3">
              <Button
                size="sm"
                variant="ghost"
                onClick={handleReset}
                disabled={isSaving}
                className="text-muted-foreground hover:text-destructive"
              >
                <RotateCcw className="mr-2 h-3 w-3" />
                Tilbakestill til opprinnelige verdier
              </Button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

interface FieldInputProps {
  label: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  placeholder?: string;
  type?: string;
}

function FieldInput({ label, value, onChange, placeholder, type = "text" }: FieldInputProps) {
  return (
    <div className="space-y-1">
      <Label className="text-xs text-muted-foreground">{label}</Label>
      <Input
        type={type}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        className="h-8 text-sm"
      />
    </div>
  );
}
