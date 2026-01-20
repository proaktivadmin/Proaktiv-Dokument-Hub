"use client";

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { BulkActions } from "./BulkActions";
import { SessionTimer } from "./SessionTimer";
import { SyncSummary } from "./SyncSummary";
import { RecordDiffCard } from "./RecordDiffCard";
import type { SyncDecision, SyncPreview as SyncPreviewType } from "@/types/v3";

interface SyncPreviewProps {
  preview: SyncPreviewType;
  isCommitting: boolean;
  isBulkUpdating: boolean;
  onDecision: (
    recordType: "office" | "employee",
    recordId: string,
    fieldName: string,
    decision: SyncDecision
  ) => void;
  onCommit: () => void;
  onCancel: () => void;
  onAcceptAllNew: () => void;
  onAcceptHighConfidence: () => void;
  onRejectAll: () => void;
}

export function SyncPreview({
  preview,
  isCommitting,
  isBulkUpdating,
  onDecision,
  onCommit,
  onCancel,
  onAcceptAllNew,
  onAcceptHighConfidence,
  onRejectAll,
}: SyncPreviewProps) {
  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <SessionTimer expiresAt={preview.expires_at} />
        <div className="flex flex-wrap items-center gap-2">
          <Button onClick={onCommit} disabled={isCommitting}>
            {isCommitting ? "Lagrer..." : "Fullfør synkronisering"}
          </Button>
          <Button variant="outline" onClick={onCancel}>
            Avbryt økt
          </Button>
        </div>
      </div>

      <BulkActions
        onAcceptAllNew={onAcceptAllNew}
        onAcceptHighConfidence={onAcceptHighConfidence}
        onRejectAll={onRejectAll}
        isBusy={isBulkUpdating}
      />

      <SyncSummary summary={preview.summary} />

      <Tabs defaultValue="offices" className="space-y-4">
        <TabsList>
          <TabsTrigger value="offices">
            Kontorer ({preview.offices.length})
          </TabsTrigger>
          <TabsTrigger value="employees">
            Ansatte ({preview.employees.length})
          </TabsTrigger>
        </TabsList>

        <TabsContent value="offices" className="space-y-4">
          {preview.offices.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              Ingen kontorendringer funnet.
            </p>
          ) : (
            preview.offices.map((record) => (
              <RecordDiffCard
                key={record.local_id ?? record.vitec_id ?? record.display_name}
                record={record}
                recordType="office"
                onDecision={onDecision}
              />
            ))
          )}
        </TabsContent>

        <TabsContent value="employees" className="space-y-4">
          {preview.employees.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              Ingen ansattendringer funnet.
            </p>
          ) : (
            preview.employees.map((record) => (
              <RecordDiffCard
                key={record.local_id ?? record.vitec_id ?? record.display_name}
                record={record}
                recordType="employee"
                onDecision={onDecision}
              />
            ))
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
