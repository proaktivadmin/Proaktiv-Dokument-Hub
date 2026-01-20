"use client";

import { AlertTriangle, CheckCircle2, XCircle } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { FieldDiff, SyncDecision } from "@/types/v3";

const FIELD_LABELS: Record<string, string> = {
  name: "Markedsnavn",
  legal_name: "Juridisk navn",
  organization_number: "Org.nr",
  email: "Epost",
  phone: "Telefon",
  street_address: "Adresse",
  postal_code: "Postnr",
  city: "Sted",
  first_name: "Fornavn",
  last_name: "Etternavn",
  title: "Tittel",
  system_roles: "Roller",
};

const formatValue = (value: unknown): string => {
  if (value === null || value === undefined) return "—";
  if (typeof value === "boolean") return value ? "Ja" : "Nei";
  if (typeof value === "number") return String(value);
  if (typeof value === "string") return value.trim() ? value : "—";
  if (Array.isArray(value)) {
    return value.length ? value.map((item) => String(item)).join(", ") : "—";
  }
  return JSON.stringify(value);
};

interface FieldDiffRowProps {
  field: FieldDiff;
  onDecision: (decision: SyncDecision) => void;
}

export function FieldDiffRow({ field, onDecision }: FieldDiffRowProps) {
  const label = FIELD_LABELS[field.field_name] ?? field.field_name;
  const isAccepted = field.decision === "accept";
  const isRejected = field.decision === "reject";

  return (
    <div className="rounded-lg border bg-background p-3">
      <div className="flex flex-col gap-2">
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-sm font-medium">{label}</span>
          {field.has_conflict && (
            <Badge variant="secondary" className="bg-amber-500/10 text-amber-600">
              <AlertTriangle className="mr-1 h-3 w-3" />
              Konflikt
            </Badge>
          )}
        </div>

        <div className="grid gap-3 md:grid-cols-[1fr_1fr_auto] md:items-center">
          <div>
            <p className="text-xs text-muted-foreground">Lokalt</p>
            <p className="text-sm">{formatValue(field.local_value)}</p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground">Vitec</p>
            <p className="text-sm">{formatValue(field.vitec_value)}</p>
          </div>
          <div className="flex gap-2">
            <Button
              size="sm"
              variant={isAccepted ? "default" : "outline"}
              className={isAccepted ? "bg-emerald-600 hover:bg-emerald-700" : undefined}
              onClick={() => onDecision("accept")}
            >
              <CheckCircle2 className="mr-2 h-4 w-4" />
              Godkjenn
            </Button>
            <Button
              size="sm"
              variant={isRejected ? "destructive" : "outline"}
              onClick={() => onDecision("reject")}
            >
              <XCircle className="mr-2 h-4 w-4" />
              Avvis
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
