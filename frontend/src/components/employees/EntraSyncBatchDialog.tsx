"use client";

import { useState } from "react";
import {
  Loader2,
  User,
  ImageIcon,
  Mail,
  Cloud,
  Users,
  ChevronDown,
  ChevronUp,
} from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Progress } from "@/components/ui/progress";
import { entraSyncApi } from "@/lib/api";
import { resolveAvatarUrl } from "@/lib/api/config";
import type { EntraSyncBatchResult, SyncScope } from "@/types/entra-sync";
import type { EmployeeWithOffice } from "@/types/v3";

interface EntraSyncBatchDialogProps {
  employees: EmployeeWithOffice[];
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSyncComplete?: (result: EntraSyncBatchResult) => void;
}

/**
 * EntraSyncBatchDialog - Batch sync multiple employees dialog
 */
export function EntraSyncBatchDialog({
  employees,
  open,
  onOpenChange,
  onSyncComplete,
}: EntraSyncBatchDialogProps) {
  const [syncing, setSyncing] = useState(false);
  const [result, setResult] = useState<EntraSyncBatchResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showErrors, setShowErrors] = useState(false);

  // Sync scope toggles
  const [syncProfile, setSyncProfile] = useState(true);
  const [syncPhoto, setSyncPhoto] = useState(true);
  const [syncSignature, setSyncSignature] = useState(true);

  const handleSync = async () => {
    const scope: SyncScope[] = [];
    if (syncProfile) scope.push("profile");
    if (syncPhoto) scope.push("photo");
    if (syncSignature) scope.push("signature");

    if (scope.length === 0) {
      setError("Velg minst én ting å synkronisere");
      return;
    }

    setSyncing(true);
    setError(null);

    try {
      const syncResult = await entraSyncApi.pushBatch({
        employee_ids: employees.map((e) => e.id),
        scope,
      });
      setResult(syncResult);
      onSyncComplete?.(syncResult);
    } catch (err) {
      console.error("[EntraSyncBatchDialog] Sync error:", err);
      setError(err instanceof Error ? err.message : "Synkronisering feilet");
    } finally {
      setSyncing(false);
    }
  };

  const handleClose = () => {
    setResult(null);
    setError(null);
    setShowErrors(false);
    onOpenChange(false);
  };

  const failedResults = result?.results.filter((r) => !r.success && r.error) || [];

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Cloud className="h-5 w-5" />
            Synkroniser {employees.length} ansatte til Entra ID
          </DialogTitle>
          <DialogDescription>
            Batch-oppdatering av profiler, bilder og e-postsignaturer.
          </DialogDescription>
        </DialogHeader>

        <div className="py-4 space-y-4">
          {syncing ? (
            // Progress view
            <div className="space-y-4">
              <div className="flex items-center justify-center py-6">
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
              </div>
              <p className="text-center text-muted-foreground">
                Synkroniserer {employees.length} ansatte...
              </p>
              <Progress value={50} className="w-full" />
            </div>
          ) : result ? (
            // Result view
            <div className="space-y-4">
              {/* Summary */}
              <div className="grid grid-cols-3 gap-4 text-center">
                <div className="p-3 bg-green-50 rounded-lg">
                  <div className="text-2xl font-bold text-green-600">{result.successful}</div>
                  <div className="text-sm text-green-700">Vellykket</div>
                </div>
                <div className="p-3 bg-yellow-50 rounded-lg">
                  <div className="text-2xl font-bold text-yellow-600">{result.skipped}</div>
                  <div className="text-sm text-yellow-700">Hoppet over</div>
                </div>
                <div className="p-3 bg-red-50 rounded-lg">
                  <div className="text-2xl font-bold text-red-600">{result.failed}</div>
                  <div className="text-sm text-red-700">Feilet</div>
                </div>
              </div>

              {/* Details */}
              <div className="space-y-2 text-sm border-t pt-4">
                <div className="flex items-center justify-between">
                  <span className="flex items-center gap-2">
                    <User className="h-4 w-4" />
                    Profiler oppdatert
                  </span>
                  <span className="font-medium">{result.profiles_updated}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="flex items-center gap-2">
                    <ImageIcon className="h-4 w-4" />
                    Bilder lastet opp
                  </span>
                  <span className="font-medium">{result.photos_uploaded}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="flex items-center gap-2">
                    <Mail className="h-4 w-4" />
                    Signaturer satt
                  </span>
                  <span className="font-medium">{result.signatures_pushed}</span>
                </div>
              </div>

              {/* Errors expandable */}
              {failedResults.length > 0 && (
                <div className="border-t pt-4">
                  <button
                    onClick={() => setShowErrors(!showErrors)}
                    className="flex items-center gap-2 text-sm text-destructive hover:underline w-full justify-between"
                  >
                    <span>Vis {failedResults.length} feil</span>
                    {showErrors ? (
                      <ChevronUp className="h-4 w-4" />
                    ) : (
                      <ChevronDown className="h-4 w-4" />
                    )}
                  </button>
                  {showErrors && (
                    <ScrollArea className="h-[120px] mt-2">
                      <div className="space-y-2">
                        {failedResults.map((r) => (
                          <div
                            key={r.employee_id}
                            className="text-sm p-2 bg-destructive/5 rounded-md"
                          >
                            <p className="font-medium">{r.employee_name}</p>
                            <p className="text-destructive text-xs">{r.error}</p>
                          </div>
                        ))}
                      </div>
                    </ScrollArea>
                  )}
                </div>
              )}
            </div>
          ) : (
            // Config view
            <div className="space-y-4">
              {/* Selected employees */}
              <div>
                <h4 className="text-sm font-medium mb-2 flex items-center gap-2">
                  <Users className="h-4 w-4" />
                  Valgte ansatte ({employees.length})
                </h4>
                <ScrollArea className="h-[150px] rounded-md border p-2">
                  <div className="space-y-2">
                    {employees.map((emp) => (
                      <div key={emp.id} className="flex items-center gap-2">
                        <Avatar className="h-6 w-6">
                          <AvatarImage src={resolveAvatarUrl(emp.profile_image_url, 48)} alt={emp.full_name} />
                          <AvatarFallback
                            className="text-[10px]"
                            style={{ backgroundColor: emp.office.color }}
                          >
                            {emp.initials}
                          </AvatarFallback>
                        </Avatar>
                        <span className="text-sm truncate">{emp.full_name}</span>
                      </div>
                    ))}
                  </div>
                </ScrollArea>
              </div>

              {/* Sync options */}
              <div className="space-y-3">
                <h4 className="text-sm font-medium">Hva skal synkroniseres?</h4>
                <div className="space-y-2">
                  <div className="flex items-center space-x-2">
                    <Checkbox
                      id="batch-sync-profile"
                      checked={syncProfile}
                      onCheckedChange={(checked) => setSyncProfile(checked === true)}
                    />
                    <Label htmlFor="batch-sync-profile" className="flex items-center gap-2">
                      <User className="h-4 w-4" />
                      Profiler (navn, tittel, telefon, etc.)
                    </Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Checkbox
                      id="batch-sync-photo"
                      checked={syncPhoto}
                      onCheckedChange={(checked) => setSyncPhoto(checked === true)}
                    />
                    <Label htmlFor="batch-sync-photo" className="flex items-center gap-2">
                      <ImageIcon className="h-4 w-4" />
                      Profilbilder
                    </Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Checkbox
                      id="batch-sync-signature"
                      checked={syncSignature}
                      onCheckedChange={(checked) => setSyncSignature(checked === true)}
                    />
                    <Label htmlFor="batch-sync-signature" className="flex items-center gap-2">
                      <Mail className="h-4 w-4" />
                      E-postsignaturer
                    </Label>
                  </div>
                </div>
              </div>

              {error && (
                <div className="p-3 bg-destructive/10 rounded-lg text-sm text-destructive">
                  {error}
                </div>
              )}
            </div>
          )}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={handleClose} disabled={syncing}>
            {result ? "Lukk" : "Avbryt"}
          </Button>
          {!result && (
            <Button onClick={handleSync} disabled={syncing || employees.length === 0}>
              {syncing ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Synkroniserer...
                </>
              ) : (
                <>Start synkronisering</>
              )}
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
