"use client";

import { useMemo, useState } from "react";
import Image from "next/image";
import { useParams } from "next/navigation";
import { ChevronDown, Copy } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Toaster } from "@/components/ui/toaster";
import { useToast } from "@/hooks/use-toast";
import {
  useSignature,
  type SignatureVersion,
} from "@/hooks/v3/useSignature";

const versionLabels: Record<SignatureVersion, string> = {
  "with-photo": "Med bilde",
  "no-photo": "Uten bilde",
};

const buildSignatureDoc = (html: string) => `<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <style>
      body {
        margin: 0;
        padding: 12px;
        background: white;
        font-family: Arial, sans-serif;
      }
    </style>
  </head>
  <body>${html}</body>
</html>`;

export default function SignaturePage() {
  const params = useParams();
  const employeeId =
    typeof params.id === "string"
      ? params.id
      : Array.isArray(params.id)
        ? params.id[0]
        : null;

  const [version, setVersion] = useState<SignatureVersion>("with-photo");
  const { signature, isLoading, error } = useSignature(employeeId, version);
  const { toast } = useToast();

  const signatureDoc = useMemo(() => {
    if (!signature?.html) return "";
    return buildSignatureDoc(signature.html);
  }, [signature?.html]);

  const showError = !isLoading && (!signature || error || !employeeId);

  const handleCopy = async () => {
    if (!signature?.html) return;

    try {
      if (!navigator.clipboard?.write || typeof ClipboardItem === "undefined") {
        throw new Error("ClipboardItem not supported");
      }

      const blob = new Blob([signature.html], { type: "text/html" });
      const clipboardItem = new ClipboardItem({ "text/html": blob });
      await navigator.clipboard.write([clipboardItem]);

      toast({
        title: "Signatur kopiert!",
        description: "Lim inn i e-postprogrammet ditt.",
      });
    } catch {
      toast({
        title: "Kunne ikke kopiere signaturen",
        description: "Prøv igjen eller kopier fra forhåndsvisningen.",
        variant: "destructive",
      });
    }
  };

  const handleTabChange = (value: string) => {
    if (value === "with-photo" || value === "no-photo") {
      setVersion(value);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto px-6 py-10">
        <div className="mx-auto flex max-w-3xl flex-col gap-6">
          <div className="flex justify-center sm:justify-start">
            <Image
              src="/assets/proaktiv-logo-black.png"
              alt="Proaktiv"
              width={200}
              height={56}
              className="h-10 w-auto"
              priority
            />
          </div>

          {isLoading ? (
            <div className="space-y-6">
              <Skeleton className="h-9 w-64" />
              <Skeleton className="h-10 w-full" />
              <Card>
                <CardContent className="p-4">
                  <Skeleton className="h-[240px] w-full" />
                </CardContent>
              </Card>
              <Skeleton className="h-10 w-48" />
              <Skeleton className="h-20 w-full" />
            </div>
          ) : showError ? (
            <Card>
              <CardContent className="p-8 text-center space-y-3">
                <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">
                  Proaktiv Dokument Hub
                </p>
                <h1 className="text-2xl font-semibold font-serif">
                  Signatur ikke funnet
                </h1>
                <p className="text-sm text-muted-foreground">
                  Lenken kan være utløpt eller feil. Ta kontakt med IT hvis du
                  trenger ny signatur.
                </p>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-6">
              <div className="space-y-2">
                <h1 className="text-3xl font-bold font-serif text-foreground">
                  Din e-postsignatur, {signature?.employee_name ?? "deg"}
                </h1>
                <p className="text-sm text-muted-foreground">
                  Velg versjon og kopier signaturen inn i e-postprogrammet ditt.
                </p>
              </div>

              <Tabs
                value={version}
                onValueChange={handleTabChange}
                className="space-y-4"
              >
                <TabsList className="grid w-full grid-cols-2">
                  <TabsTrigger value="with-photo">
                    {versionLabels["with-photo"]}
                  </TabsTrigger>
                  <TabsTrigger value="no-photo">
                    {versionLabels["no-photo"]}
                  </TabsTrigger>
                </TabsList>

                {(["with-photo", "no-photo"] as SignatureVersion[]).map(
                  (tabVersion) => (
                    <TabsContent key={tabVersion} value={tabVersion} className="mt-0">
                      <Card>
                        <CardContent className="p-4">
                          {isLoading ? (
                            <Skeleton className="h-[240px] w-full" />
                          ) : signature ? (
                            <iframe
                              title={`Signatur ${versionLabels[version]}`}
                              sandbox=""
                              srcDoc={signatureDoc}
                              className="h-[240px] w-full rounded-md border bg-white"
                            />
                          ) : (
                            <div className="rounded-md border border-dashed p-4 text-sm text-muted-foreground">
                              Ingen signatur tilgjengelig.
                            </div>
                          )}
                        </CardContent>
                      </Card>
                    </TabsContent>
                  )
                )}
              </Tabs>

              <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
                <Button onClick={handleCopy} disabled={!signature?.html}>
                  <Copy className="mr-2 h-4 w-4" />
                  Kopier signatur
                </Button>
                <p className="text-sm text-muted-foreground">
                  Signaturen kopieres som HTML for best mulig utseende.
                </p>
              </div>

              <details className="group rounded-lg border bg-white shadow-card ring-1 ring-black/3">
                <summary className="flex cursor-pointer items-center justify-between gap-3 px-6 py-4 text-sm font-medium text-foreground transition-colors duration-fast ease-standard hover:text-foreground">
                  <span>Slik legger du inn signaturen</span>
                  <ChevronDown className="h-4 w-4 text-muted-foreground transition-transform duration-fast ease-standard group-open:rotate-180" />
                </summary>
                <div className="space-y-4 border-t px-6 py-4 text-sm text-muted-foreground">
                  <div className="space-y-2">
                    <p className="font-medium text-foreground">
                      Outlook (Windows/Mac)
                    </p>
                    <ol className="list-decimal space-y-1 pl-4">
                      <li>Gå til Signaturer i Outlook-innstillingene.</li>
                      <li>Opprett en ny signatur for riktig konto.</li>
                      <li>Lim inn signaturen og lagre endringene.</li>
                    </ol>
                  </div>
                  <div className="space-y-2">
                    <p className="font-medium text-foreground">Gmail</p>
                    <ol className="list-decimal space-y-1 pl-4">
                      <li>Klikk tannhjulet og velg &quot;Se alle innstillinger&quot;.</li>
                      <li>Finn &quot;Signatur&quot; under &quot;Generelt&quot;.</li>
                      <li>Lim inn signaturen og lagre nederst.</li>
                    </ol>
                  </div>
                  <div className="space-y-2">
                    <p className="font-medium text-foreground">Apple Mail</p>
                    <ol className="list-decimal space-y-1 pl-4">
                      <li>Åpne Mail → Innstillinger → Signaturer.</li>
                      <li>Velg konto og trykk + for ny signatur.</li>
                      <li>Lim inn signaturen og fjern standardtekst.</li>
                    </ol>
                  </div>
                </div>
              </details>
            </div>
          )}
        </div>
        <Toaster />
      </main>
    </div>
  );
}
