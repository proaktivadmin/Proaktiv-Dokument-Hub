"use client";

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { SyncSummary } from "./SyncSummary";
import { RecordDiffCard } from "./RecordDiffCard";
import type { SyncDecision, SyncPreview as SyncPreviewType } from "@/types/v3";

interface SyncPreviewProps {
  preview: SyncPreviewType;
  isCommitting: boolean;
  onDecision: (
    recordType: "office" | "employee",
    recordId: string,
    fieldName: string,
    decision: SyncDecision
  ) => void;
  onCommit: () => void;
  onCancel: () => void;
}

export function SyncPreview({
  preview,
  isCommitting,
  onDecision,
  onCommit,
  onCancel,
}: SyncPreviewProps) {
  return (
    <div className="space-y-6">
      <SyncSummary summary={preview.summary} />

      <div className="flex flex-wrap items-center gap-2">
        <Button onClick={onCommit} disabled={isCommitting}>
          {isCommitting ? "Lagrer..." : "Fullfør synkronisering"}
        </Button>
        <Button variant="outline" onClick={onCancel}>
          Avbryt økt
        </Button>
      </div>

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
