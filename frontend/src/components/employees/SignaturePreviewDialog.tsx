"use client";

import { useState, useEffect, useCallback } from "react";
import { Loader2, Mail, FileText } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { entraSyncApi } from "@/lib/api";
import type { SignaturePreview } from "@/types/entra-sync";

interface SignaturePreviewDialogProps {
  employeeId: string | null;
  employeeName?: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onPushSignature?: () => void;
  showPushButton?: boolean;
}

/**
 * SignaturePreviewDialog - Shows email signature preview for an employee
 */
export function SignaturePreviewDialog({
  employeeId,
  employeeName,
  open,
  onOpenChange,
  onPushSignature,
  showPushButton = false,
}: SignaturePreviewDialogProps) {
  const [preview, setPreview] = useState<SignaturePreview | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"html" | "text">("html");

  const fetchPreview = useCallback(async (id: string) => {
    setLoading(true);
    setError(null);
    try {
      const data = await entraSyncApi.getSignaturePreview(id);
      setPreview(data);
    } catch (err) {
      console.error("[SignaturePreviewDialog] Error:", err);
      setError(err instanceof Error ? err.message : "Kunne ikke laste signatur");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (open && employeeId) {
      fetchPreview(employeeId);
    } else {
      setPreview(null);
      setError(null);
    }
  }, [open, employeeId, fetchPreview]);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[80vh]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Mail className="h-5 w-5" />
            E-postsignatur
          </DialogTitle>
          <DialogDescription>
            {employeeName || preview?.employee_name || "Forhåndsvisning av e-postsignatur"}
          </DialogDescription>
        </DialogHeader>

        <div className="py-4">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
            </div>
          ) : error ? (
            <div className="text-center py-8">
              <p className="text-destructive">{error}</p>
            </div>
          ) : preview ? (
            <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as "html" | "text")}>
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="html" className="gap-2">
                  <Mail className="h-4 w-4" />
                  HTML
                </TabsTrigger>
                <TabsTrigger value="text" className="gap-2">
                  <FileText className="h-4 w-4" />
                  Ren tekst
                </TabsTrigger>
              </TabsList>

              <TabsContent value="html" className="mt-4">
                <ScrollArea className="h-[350px] rounded-md border p-4 bg-white">
                  <div
                    dangerouslySetInnerHTML={{ __html: preview.html }}
                    className="signature-preview"
                  />
                </ScrollArea>
              </TabsContent>

              <TabsContent value="text" className="mt-4">
                <ScrollArea className="h-[350px] rounded-md border p-4 bg-muted/30">
                  <pre className="text-sm whitespace-pre-wrap font-mono">
                    {preview.text}
                  </pre>
                </ScrollArea>
              </TabsContent>
            </Tabs>
          ) : null}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Lukk
          </Button>
          {showPushButton && onPushSignature && (
            <Button onClick={onPushSignature} disabled={loading || !!error}>
              Push signatur til Exchange
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
