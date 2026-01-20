"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

interface BulkActionsProps {
  onAcceptAllNew: () => void;
  onAcceptHighConfidence: () => void;
  onRejectAll: () => void;
  isBusy?: boolean;
}

export function BulkActions({
  onAcceptAllNew,
  onAcceptHighConfidence,
  onRejectAll,
  isBusy = false,
}: BulkActionsProps) {
  return (
    <Card>
      <CardContent className="flex flex-col gap-3 p-4 md:flex-row md:items-center md:justify-between">
        <div className="text-sm text-muted-foreground">
          Hurtigvalg for å behandle mange felt samtidig.
        </div>
        <div className="flex flex-wrap gap-2">
          <Button variant="outline" onClick={onAcceptAllNew} disabled={isBusy}>
            Godkjenn nye
          </Button>
          <Button variant="outline" onClick={onAcceptHighConfidence} disabled={isBusy}>
            Godkjenn høy treff
          </Button>
          <Button variant="destructive" onClick={onRejectAll} disabled={isBusy}>
            Avvis alle
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
