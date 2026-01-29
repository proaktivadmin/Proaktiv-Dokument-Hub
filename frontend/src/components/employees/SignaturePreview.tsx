"use client";

import { useMemo, useState } from "react";
import toast, { Toaster } from "react-hot-toast";
import { Loader2, Mail, ExternalLink } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  useSendSignature,
  useSignature,
  type SignatureVersion,
} from "@/hooks/v3/useSignature";
import { buildSignatureDoc, VERSION_LABELS } from "@/lib/signature";

interface SignaturePreviewProps {
  employeeId: string;
  employeeEmail: string;
  employeeName: string;
}

export function SignaturePreview({
  employeeId,
  employeeEmail,
  employeeName,
}: SignaturePreviewProps) {
  const [version, setVersion] = useState<SignatureVersion>("with-photo");
  const { signature, isLoading, error } = useSignature(employeeId, version);
  const { send, isSending } = useSendSignature(employeeId);

  const signatureHtml = signature?.html;
  const signatureDoc = useMemo(() => {
    if (!signatureHtml) return "";
    return buildSignatureDoc(signatureHtml);
  }, [signatureHtml]);

  const canSend = Boolean(employeeEmail?.trim());
  const publicSignatureUrl = `/signature/${employeeId}`;

  const handleSend = async () => {
    if (!canSend) {
      toast.error("Ingen mottakeradresse registrert");
      return;
    }

    try {
      const result = await send();
      if (result.success) {
        toast.success(`Signatur sendt til ${result.sent_to}`);
      } else {
        toast.error(result.message || "Kunne ikke sende signatur");
      }
    } catch (err) {
      toast.error(
        err instanceof Error ? err.message : "Kunne ikke sende signatur"
      );
    }
  };

  const handleOpenPublicPage = () => {
    window.open(publicSignatureUrl, "_blank", "noopener,noreferrer");
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Signatur</CardTitle>
        <CardDescription>
          Forhåndsvisning for {employeeName}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex flex-col gap-3">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Mail className="h-4 w-4" />
              <span>
                Sendes til{" "}
                <span className="font-medium text-foreground">
                  {employeeEmail || "Ikke registrert"}
                </span>
              </span>
            </div>
            <div className="flex gap-2">
              <Button
                variant="outline"
                onClick={handleOpenPublicPage}
                className="gap-2"
              >
                <ExternalLink className="h-4 w-4" />
                Åpne ansattvisning
              </Button>
              <Button onClick={handleSend} disabled={!canSend || isSending}>
                {isSending ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Sender...
                  </>
                ) : (
                  "Send signatur til ansatt"
                )}
              </Button>
            </div>
          </div>
        </div>

        <Tabs
          value={version}
          onValueChange={(value) => setVersion(value as SignatureVersion)}
        >
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="with-photo">{VERSION_LABELS["with-photo"]}</TabsTrigger>
            <TabsTrigger value="no-photo">{VERSION_LABELS["no-photo"]}</TabsTrigger>
          </TabsList>

          {(["with-photo", "no-photo"] as SignatureVersion[]).map(
            (tabVersion) => (
              <TabsContent key={tabVersion} value={tabVersion} className="mt-4">
                {isLoading ? (
                  <Skeleton className="h-[240px] w-full" />
                ) : error ? (
                  <div className="rounded-md border border-destructive/30 bg-destructive/5 p-4 text-sm text-destructive">
                    {error}
                  </div>
                ) : signature ? (
                  <iframe
                    title={`Signatur ${VERSION_LABELS[version]}`}
                    sandbox=""
                    srcDoc={signatureDoc}
                    className="h-[240px] w-full rounded-md border bg-white"
                  />
                ) : (
                  <div className="rounded-md border border-dashed p-4 text-sm text-muted-foreground">
                    Ingen signatur tilgjengelig.
                  </div>
                )}
              </TabsContent>
            )
          )}
        </Tabs>
      </CardContent>
      <Toaster position="top-right" />
    </Card>
  );
}
