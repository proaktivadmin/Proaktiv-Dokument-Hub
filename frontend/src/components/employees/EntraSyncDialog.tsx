"use client";

import { useState, useEffect, useCallback } from "react";
import {
  Loader2,
  User,
  Image,
  Mail,
  CheckCircle,
  XCircle,
  AlertTriangle,
  ArrowRight,
  Cloud,
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
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { entraSyncApi } from "@/lib/api";
import { resolveApiUrl } from "@/lib/api/config";
import type { EntraSyncPreview, EntraSyncResult, SyncScope } from "@/types/entra-sync";
import type { EmployeeWithOffice } from "@/types/v3";

interface EntraSyncDialogProps {
  employee: EmployeeWithOffice | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSyncComplete?: (result: EntraSyncResult) => void;
  onOpenSignaturePreview?: () => void;
}

/**
 * EntraSyncDialog - Single employee sync dialog
 */
export function EntraSyncDialog({
  employee,
  open,
  onOpenChange,
  onSyncComplete,
  onOpenSignaturePreview,
}: EntraSyncDialogProps) {
  const [preview, setPreview] = useState<EntraSyncPreview | null>(null);
  const [loading, setLoading] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<EntraSyncResult | null>(null);

  // Sync scope toggles
  const [syncProfile, setSyncProfile] = useState(true);
  const [syncPhoto, setSyncPhoto] = useState(true);
  const [syncSignature, setSyncSignature] = useState(true);

  const fetchPreview = useCallback(async (employeeId: string) => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await entraSyncApi.getPreview(employeeId);
      setPreview(data);
    } catch (err) {
      console.error("[EntraSyncDialog] Preview error:", err);
      setError(err instanceof Error ? err.message : "Kunne ikke laste forhåndsvisning");
    } finally {
      setLoading(false);
    }
  }, []);

  // Load preview when dialog opens
  useEffect(() => {
    if (open && employee) {
      fetchPreview(employee.id);
    } else {
      setPreview(null);
      setError(null);
      setResult(null);
    }
  }, [open, employee, fetchPreview]);

  const handleSync = async () => {
    if (!employee) return;

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
      const syncResult = await entraSyncApi.pushEmployee(employee.id, { scope });
      setResult(syncResult);
      onSyncComplete?.(syncResult);
    } catch (err) {
      console.error("[EntraSyncDialog] Sync error:", err);
      setError(err instanceof Error ? err.message : "Synkronisering feilet");
    } finally {
      setSyncing(false);
    }
  };

  const hasChanges = preview?.profile_changes.some((c) => c.will_update);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Cloud className="h-5 w-5" />
            Synkroniser til Entra ID
          </DialogTitle>
          <DialogDescription>
            Oppdater profil, bilde og e-postsignatur i Microsoft 365.
          </DialogDescription>
        </DialogHeader>

        {/* Employee header */}
        {employee && (
          <div className="flex items-center gap-3 p-3 bg-muted/30 rounded-lg">
            <Avatar className="h-12 w-12">
              <AvatarImage src={resolveApiUrl(employee.profile_image_url)} />
              <AvatarFallback style={{ backgroundColor: employee.office.color }}>
                {employee.initials}
              </AvatarFallback>
            </Avatar>
            <div>
              <p className="font-medium">{employee.full_name}</p>
              <p className="text-sm text-muted-foreground">{employee.email}</p>
            </div>
          </div>
        )}

        <div className="py-4 space-y-4">
          {loading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
            </div>
          ) : error && !result ? (
            <div className="text-center py-4">
              <XCircle className="h-8 w-8 mx-auto text-destructive mb-2" />
              <p className="text-destructive">{error}</p>
            </div>
          ) : result ? (
            // Show result
            <div className="space-y-4">
              <div className="flex items-center gap-2 justify-center py-4">
                {result.success ? (
                  <>
                    <CheckCircle className="h-8 w-8 text-green-500" />
                    <span className="text-lg font-medium text-green-600">Synkronisering fullført</span>
                  </>
                ) : (
                  <>
                    <XCircle className="h-8 w-8 text-destructive" />
                    <span className="text-lg font-medium text-destructive">Synkronisering feilet</span>
                  </>
                )}
              </div>

              <div className="space-y-2 text-sm">
                <div className="flex items-center gap-2">
                  {result.profile_updated ? (
                    <CheckCircle className="h-4 w-4 text-green-500" />
                  ) : (
                    <XCircle className="h-4 w-4 text-muted-foreground" />
                  )}
                  <span>Profil {result.profile_updated ? "oppdatert" : "ikke oppdatert"}</span>
                </div>
                <div className="flex items-center gap-2">
                  {result.photo_updated ? (
                    <CheckCircle className="h-4 w-4 text-green-500" />
                  ) : (
                    <XCircle className="h-4 w-4 text-muted-foreground" />
                  )}
                  <span>Bilde {result.photo_updated ? "lastet opp" : "ikke lastet opp"}</span>
                </div>
                <div className="flex items-center gap-2">
                  {result.signature_pushed ? (
                    <CheckCircle className="h-4 w-4 text-green-500" />
                  ) : (
                    <XCircle className="h-4 w-4 text-muted-foreground" />
                  )}
                  <span>Signatur {result.signature_pushed ? "satt" : "ikke satt"}</span>
                </div>
              </div>

              {result.error && (
                <div className="p-3 bg-destructive/10 rounded-lg text-sm text-destructive">
                  {result.error}
                </div>
              )}
            </div>
          ) : preview ? (
            // Show preview
            <div className="space-y-4">
              {/* Entra user status */}
              <div className="flex items-center gap-2">
                {preview.entra_user_found ? (
                  <Badge variant="outline" className="gap-1 border-green-500 text-green-600">
                    <CheckCircle className="h-3 w-3" />
                    Bruker funnet i Entra ID
                  </Badge>
                ) : (
                  <Badge variant="outline" className="gap-1 border-yellow-500 text-yellow-600">
                    <AlertTriangle className="h-3 w-3" />
                    Bruker ikke funnet i Entra ID
                  </Badge>
                )}
              </div>

              {/* Profile changes */}
              {hasChanges && (
                <div className="space-y-2">
                  <h4 className="text-sm font-medium flex items-center gap-2">
                    <User className="h-4 w-4" />
                    Profilendringer
                  </h4>
                  <ScrollArea className="h-[150px] rounded-md border p-2">
                    <div className="space-y-1">
                      {preview.profile_changes
                        .filter((c) => c.will_update)
                        .map((change) => (
                          <div key={change.property} className="flex items-center gap-2 text-sm">
                            <code className="bg-muted px-1 rounded text-xs">
                              {change.property}
                            </code>
                            <ArrowRight className="h-3 w-3 text-muted-foreground" />
                            <span className="text-emerald-600 truncate">
                              {change.new_value || "(tom)"}
                            </span>
                          </div>
                        ))}
                    </div>
                  </ScrollArea>
                </div>
              )}

              {/* Sync options */}
              <div className="space-y-3">
                <h4 className="text-sm font-medium">Hva skal synkroniseres?</h4>
                <div className="space-y-2">
                  <div className="flex items-center space-x-2">
                    <Checkbox
                      id="sync-profile"
                      checked={syncProfile}
                      onCheckedChange={(checked) => setSyncProfile(checked === true)}
                    />
                    <Label htmlFor="sync-profile" className="flex items-center gap-2">
                      <User className="h-4 w-4" />
                      Profil (navn, tittel, telefon, etc.)
                    </Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Checkbox
                      id="sync-photo"
                      checked={syncPhoto}
                      onCheckedChange={(checked) => setSyncPhoto(checked === true)}
                      disabled={!preview.photo_url}
                    />
                    <Label
                      htmlFor="sync-photo"
                      className={`flex items-center gap-2 ${!preview.photo_url ? "text-muted-foreground" : ""}`}
                    >
                      <Image className="h-4 w-4" />
                      Profilbilde {!preview.photo_url && "(ingen URL)"}
                    </Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Checkbox
                      id="sync-signature"
                      checked={syncSignature}
                      onCheckedChange={(checked) => setSyncSignature(checked === true)}
                    />
                    <Label htmlFor="sync-signature" className="flex items-center gap-2">
                      <Mail className="h-4 w-4" />
                      E-postsignatur
                    </Label>
                  </div>
                </div>
              </div>
            </div>
          ) : null}
        </div>

        <DialogFooter className="gap-2">
          {onOpenSignaturePreview && !result && (
            <Button
              variant="outline"
              onClick={onOpenSignaturePreview}
              disabled={loading || syncing}
            >
              Forhåndsvis signatur
            </Button>
          )}
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            {result ? "Lukk" : "Avbryt"}
          </Button>
          {!result && (
            <Button onClick={handleSync} disabled={loading || syncing || !!error}>
              {syncing ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Synkroniserer...
                </>
              ) : (
                "Synkroniser"
              )}
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
