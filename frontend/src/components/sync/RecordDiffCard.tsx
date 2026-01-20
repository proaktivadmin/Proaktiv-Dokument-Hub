"use client";

import { useState } from "react";
import { ChevronDown, ChevronUp } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import type { RecordDiff, SyncDecision } from "@/types/v3";
import { FieldDiffRow } from "./FieldDiffRow";

const matchTypeLabels: Record<RecordDiff["match_type"], string> = {
  new: "Ny",
  matched: "Match",
  not_in_vitec: "Ikke i Vitec",
};

const matchTypeStyles: Record<RecordDiff["match_type"], string> = {
  new: "bg-sky-500/10 text-sky-600",
  matched: "bg-emerald-500/10 text-emerald-600",
  not_in_vitec: "bg-slate-100 text-slate-600",
};

const matchMethodLabels: Record<string, string> = {
  organization_number: "Org.nr",
  vitec_department_id: "Vitec avdeling",
  name_exact: "Navn (eksakt)",
  name_fuzzy: "Navn (likhet)",
  vitec_employee_id: "Vitec ansatt",
  email: "E-post",
  name_office: "Navn + kontor",
};

interface RecordDiffCardProps {
  record: RecordDiff;
  recordType: "office" | "employee";
  onDecision: (
    recordType: "office" | "employee",
    recordId: string,
    fieldName: string,
    decision: SyncDecision
  ) => void;
}

export function RecordDiffCard({ record, recordType, onDecision }: RecordDiffCardProps) {
  const [isOpen, setIsOpen] = useState(record.match_type !== "not_in_vitec");
  const recordId = record.local_id ?? record.vitec_id ?? "";
  const confidence = Math.round(record.match_confidence * 100);

  const handleDecision = (fieldName: string, decision: SyncDecision) => {
    if (!recordId) return;
    onDecision(recordType, recordId, fieldName, decision);
  };

  return (
    <Card>
      <CardContent className="p-4">
        <div className="flex items-start justify-between gap-3">
          <div className="space-y-1">
            <div className="flex flex-wrap items-center gap-2">
              <h3 className="text-base font-semibold">{record.display_name}</h3>
              <Badge variant="secondary" className={matchTypeStyles[record.match_type]}>
                {matchTypeLabels[record.match_type]}
              </Badge>
              {record.match_type === "matched" && (
                <Badge variant="outline">{confidence}%</Badge>
              )}
            </div>
            {record.match_method && (
              <p className="text-xs text-muted-foreground">
                Match: {matchMethodLabels[record.match_method] ?? record.match_method}
              </p>
            )}
          </div>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setIsOpen((prev) => !prev)}
            aria-label="Vis detaljer"
          >
            {isOpen ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
          </Button>
        </div>

        {isOpen && (
          <div className="mt-4 space-y-3">
            {record.fields.length === 0 ? (
              <p className="text-sm text-muted-foreground">
                {record.match_type === "not_in_vitec"
                  ? "Finnes lokalt, ikke i Vitec."
                  : "Ingen feltendringer funnet."}
              </p>
            ) : (
              record.fields.map((field) => (
                <FieldDiffRow
                  key={field.field_name}
                  field={field}
                  onDecision={(decision) => handleDecision(field.field_name, decision)}
                />
              ))
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
