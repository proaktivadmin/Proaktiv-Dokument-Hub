"use client";

import { useState } from "react";
import type { Dispatch, SetStateAction } from "react";
import { AxiosError } from "axios";
import { Header } from "@/components/layout/Header";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { SyncPreview as SyncPreviewComponent } from "@/components/sync";
import { syncApi } from "@/lib/api/sync";
import { useToast } from "@/hooks/use-toast";
import type { SyncCommitResult, SyncDecision, SyncPreview } from "@/types/v3";

export default function SyncPage() {
  const { toast } = useToast();
  const [preview, setPreview] = useState<SyncPreview | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isCommitting, setIsCommitting] = useState(false);
  const [isBulkUpdating, setIsBulkUpdating] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleStartPreview = async () => {
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const data = await syncApi.createPreview();
      setPreview(data);
    } catch (error) {
      const message = extractErrorMessage(error, "Kunne ikke starte forhåndsvisning.");
      setErrorMessage(message);
      toast({
        title: "Forhåndsvisning feilet",
        description: message,
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleDecision = async (
    recordType: "office" | "employee",
    recordId: string,
    fieldName: string,
    decision: SyncDecision
  ) => {
    if (!preview) return;

    try {
      await syncApi.updateDecision(preview.session_id, {
        record_type: recordType,
        record_id: recordId,
        field_name: fieldName,
        decision,
      });
      setPreview((current) =>
        current ? applyDecision(current, recordType, recordId, fieldName, decision) : current
      );
    } catch (error) {
      if (handleSessionExpired(error, toast, setPreview)) return;
      const message = extractErrorMessage(error, "Kunne ikke oppdatere valg.");
      toast({
        title: "Oppdatering feilet",
        description: message,
        variant: "destructive",
      });
    }
  };

  const handleCommit = async () => {
    if (!preview) return;
    setIsCommitting(true);
    try {
      const result = await syncApi.commitSession(preview.session_id);
      toast({
        title: "Synkronisering fullført",
        description: formatCommitResult(result),
      });
    } catch (error) {
      if (handleSessionExpired(error, toast, setPreview)) return;
      const message = extractErrorMessage(error, "Kunne ikke fullføre synkronisering.");
      toast({
        title: "Synkronisering feilet",
        description: message,
        variant: "destructive",
      });
    } finally {
      setIsCommitting(false);
    }
  };

  const handleCancel = async () => {
    if (!preview) return;
    try {
      await syncApi.cancelSession(preview.session_id);
      setPreview(null);
      toast({
        title: "Økten ble avbrutt",
        description: "Forhåndsvisningen er avsluttet.",
      });
    } catch (error) {
      if (handleSessionExpired(error, toast, setPreview)) return;
      const message = extractErrorMessage(error, "Kunne ikke avbryte økten.");
      toast({
        title: "Avbryt feilet",
        description: message,
        variant: "destructive",
      });
    }
  };

  const handleBulkUpdate = async (operations: DecisionOperation[]) => {
    if (!preview) return;
    if (operations.length === 0) {
      toast({
        title: "Ingen felter valgt",
        description: "Ingen felt var tilgjengelig for denne handlingen.",
      });
      return;
    }

    setIsBulkUpdating(true);
    try {
      await Promise.all(
        operations.map((operation) =>
          syncApi.updateDecision(preview.session_id, operation)
        )
      );
      setPreview((current) =>
        current ? applyBulkDecisions(current, operations) : current
      );
      toast({
        title: "Hurtigvalg fullført",
        description: `Oppdaterte ${operations.length} felt.`,
      });
    } catch (error) {
      if (handleSessionExpired(error, toast, setPreview)) return;
      const message = extractErrorMessage(error, "Kunne ikke oppdatere felter.");
      toast({
        title: "Hurtigvalg feilet",
        description: message,
        variant: "destructive",
      });
    } finally {
      setIsBulkUpdating(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main className="container mx-auto px-6 py-8">
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-foreground">Vitec synkronisering</h2>
          <p className="text-muted-foreground">
            Forhåndsvis endringer og godkjenn oppdateringer før de lagres.
          </p>
        </div>

        {!preview && (
          <Card>
            <CardContent className="flex flex-col gap-4 p-6">
              <p className="text-sm text-muted-foreground">
                Start en forhåndsvisning for å se foreslåtte oppdateringer fra Vitec.
              </p>
              {errorMessage && (
                <p className="text-sm text-destructive">{errorMessage}</p>
              )}
              <div>
                <Button onClick={handleStartPreview} disabled={isLoading}>
                  {isLoading ? "Starter..." : "Start forhåndsvisning"}
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {preview && (
          <SyncPreviewComponent
            preview={preview}
            isCommitting={isCommitting}
            isBulkUpdating={isBulkUpdating}
            onDecision={handleDecision}
            onCommit={handleCommit}
            onCancel={handleCancel}
            onAcceptAllNew={() => handleBulkUpdate(buildBulkOperations(preview, "new", "accept"))}
            onAcceptHighConfidence={() =>
              handleBulkUpdate(buildBulkOperations(preview, "high_confidence", "accept"))
            }
            onRejectAll={() => handleBulkUpdate(buildBulkOperations(preview, "all", "reject"))}
          />
        )}
      </main>
    </div>
  );
}

const extractErrorMessage = (error: unknown, fallback: string): string => {
  if (error instanceof AxiosError && error.response?.data?.detail) {
    return error.response.data.detail;
  }
  if (error instanceof Error) {
    return error.message;
  }
  return fallback;
};

const handleSessionExpired = (
  error: unknown,
  toast: ReturnType<typeof useToast>["toast"],
  setPreview: Dispatch<SetStateAction<SyncPreview | null>>
): boolean => {
  if (error instanceof AxiosError && error.response?.status === 410) {
    setPreview(null);
    toast({
      title: "Økten er utløpt",
      description: "Start en ny forhåndsvisning for å fortsette.",
      variant: "destructive",
    });
    return true;
  }
  return false;
};

type BulkMode = "new" | "high_confidence" | "all";

type DecisionOperation = {
  record_type: "office" | "employee";
  record_id: string;
  field_name: string;
  decision: SyncDecision;
};

const buildBulkOperations = (
  preview: SyncPreview,
  mode: BulkMode,
  decision: SyncDecision
): DecisionOperation[] => {
  const operations: DecisionOperation[] = [];

  const shouldIncludeRecord = (record: SyncPreview["offices"][number]): boolean => {
    if (mode === "new") return record.match_type === "new";
    if (mode === "high_confidence") {
      return record.match_type === "matched" && record.match_confidence >= 0.9;
    }
    return record.match_type !== "not_in_vitec";
  };

  const pushRecord = (
    recordType: "office" | "employee",
    record: SyncPreview["offices"][number]
  ) => {
    const recordId = record.local_id ?? record.vitec_id ?? "";
    if (!recordId) return;
    record.fields.forEach((field) => {
      operations.push({
        record_type: recordType,
        record_id: recordId,
        field_name: field.field_name,
        decision,
      });
    });
  };

  preview.offices.filter(shouldIncludeRecord).forEach((record) => {
    pushRecord("office", record);
  });
  preview.employees.filter(shouldIncludeRecord).forEach((record) => {
    pushRecord("employee", record);
  });

  return operations;
};

const applyBulkDecisions = (
  preview: SyncPreview,
  operations: DecisionOperation[]
): SyncPreview => {
  if (operations.length === 0) return preview;
  const operationMap = new Map<string, Map<string, SyncDecision>>();
  operations.forEach((operation) => {
    const key = `${operation.record_type}:${operation.record_id}`;
    if (!operationMap.has(key)) {
      operationMap.set(key, new Map());
    }
    operationMap.get(key)?.set(operation.field_name, operation.decision);
  });

  const updateRecords = (
    records: SyncPreview["offices"],
    recordType: "office" | "employee"
  ) => {
    return records.map((record) => {
      const recordId = record.local_id ?? record.vitec_id ?? "";
      const decisions = operationMap.get(`${recordType}:${recordId}`);
      if (!decisions) return record;
      return {
        ...record,
        fields: record.fields.map((field) => {
          const decision = decisions.get(field.field_name);
          return decision ? { ...field, decision } : field;
        }),
      };
    });
  };

  return {
    ...preview,
    offices: updateRecords(preview.offices, "office"),
    employees: updateRecords(preview.employees, "employee"),
  };
};

const applyDecision = (
  preview: SyncPreview,
  recordType: "office" | "employee",
  recordId: string,
  fieldName: string,
  decision: SyncDecision
): SyncPreview => {
  const key = recordType === "office" ? "offices" : "employees";
  const updatedRecords = preview[key].map((record) => {
    const id = record.local_id ?? record.vitec_id ?? "";
    if (id !== recordId) {
      return record;
    }
    return {
      ...record,
      fields: record.fields.map((field) =>
        field.field_name === fieldName ? { ...field, decision } : field
      ),
    };
  });
  return { ...preview, [key]: updatedRecords };
};

const formatCommitResult = (result: SyncCommitResult): string => {
  return (
    `Kontorer: +${result.offices_created}, oppdatert ${result.offices_updated}, ` +
    `hoppet over ${result.offices_skipped}. ` +
    `Ansatte: +${result.employees_created}, oppdatert ${result.employees_updated}, ` +
    `hoppet over ${result.employees_skipped}.`
  );
};
