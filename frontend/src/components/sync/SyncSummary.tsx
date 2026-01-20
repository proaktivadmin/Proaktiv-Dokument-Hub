"use client";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import type { SyncSummary as SyncSummaryType } from "@/types/v3";

interface SyncSummaryProps {
  summary: SyncSummaryType;
}

export function SyncSummary({ summary }: SyncSummaryProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Oppsummering</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <h4 className="text-sm font-semibold text-muted-foreground">Kontorer</h4>
          <div className="flex flex-wrap gap-2">
            <Badge variant="secondary">Nye: {summary.offices_new}</Badge>
            <Badge variant="secondary">Matchet: {summary.offices_matched}</Badge>
            <Badge variant="secondary">Ikke i Vitec: {summary.offices_not_in_vitec}</Badge>
          </div>
        </div>
        <Separator />
        <div className="space-y-2">
          <h4 className="text-sm font-semibold text-muted-foreground">Ansatte</h4>
          <div className="flex flex-wrap gap-2">
            <Badge variant="secondary">Nye: {summary.employees_new}</Badge>
            <Badge variant="secondary">Matchet: {summary.employees_matched}</Badge>
            <Badge variant="secondary">Ikke i Vitec: {summary.employees_not_in_vitec}</Badge>
            <Badge variant="secondary">Mangler kontor: {summary.employees_missing_office}</Badge>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
