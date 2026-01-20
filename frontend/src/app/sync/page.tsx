"use client";

import { useState } from "react";
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
      const message = extractErrorMessage(error, "Kunne ikke avbryte økten.");
      toast({
        title: "Avbryt feilet",
        description: message,
        variant: "destructive",
      });
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
            onDecision={handleDecision}
            onCommit={handleCommit}
            onCancel={handleCancel}
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
  return `Kontorer: +${result.offices_created}, oppdatert ${result.offices_updated}. ` +
    `Ansatte: +${result.employees_created}, oppdatert ${result.employees_updated}.`;
};
