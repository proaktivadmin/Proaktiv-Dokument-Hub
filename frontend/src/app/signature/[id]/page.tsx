"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { useParams } from "next/navigation";
import { ChevronDown, Copy, Mail, Keyboard } from "lucide-react";

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

  const signatureHtml = signature?.html;
  const signatureDoc = useMemo(() => {
    if (!signatureHtml) return "";
    return buildSignatureDoc(signatureHtml);
  }, [signatureHtml]);

  const showError = !isLoading && (!signature || error || !employeeId);

  // Detect mobile device
  const isMobile = useMemo(() => {
    if (typeof window === "undefined") return false;
    return /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
  }, []);

  const handleCopy = useCallback(async () => {
    if (!signature?.html) return;

    try {
      // Try modern ClipboardItem API first (works on desktop browsers)
      if (navigator.clipboard?.write && typeof ClipboardItem !== "undefined") {
        const blob = new Blob([signature.html], { type: "text/html" });
        const clipboardItem = new ClipboardItem({ "text/html": blob });
        await navigator.clipboard.write([clipboardItem]);

        toast({
          title: "Signatur kopiert som HTML!",
          description: "Lim inn i e-postprogrammet ditt for full formatering.",
        });
        return;
      }

      // Fallback: Try copying plain text (works on mobile)
      if (signature.text && navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(signature.text);
        toast({
          title: "Signatur kopiert som tekst",
          description: "HTML-formatering er ikke støttet på denne enheten. Lim inn i e-postprogrammet.",
        });
        return;
      }

      // Final fallback: Use execCommand (legacy but wider support)
      const textArea = document.createElement("textarea");
      textArea.value = signature.text || signature.html;
      textArea.style.position = "fixed";
      textArea.style.left = "-9999px";
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand("copy");
      document.body.removeChild(textArea);

      toast({
        title: "Signatur kopiert som tekst",
        description: "Lim inn i e-postprogrammet ditt.",
      });
    } catch {
      toast({
        title: "Kunne ikke kopiere signaturen",
        description: "Prøv å markere og kopiere teksten manuelt.",
        variant: "destructive",
      });
    }
  }, [signature, toast]);

  // Open default email client
  const handleOpenEmailApp = useCallback(() => {
    window.location.href = `mailto:`;
  }, []);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ctrl/Cmd + C when not in an input field - copy signature
      if ((e.ctrlKey || e.metaKey) && e.key === "c") {
        const activeElement = document.activeElement;
        const isInInput =
          activeElement instanceof HTMLInputElement ||
          activeElement instanceof HTMLTextAreaElement ||
          activeElement?.getAttribute("contenteditable") === "true";

        // Only intercept if no text is selected
        const selection = window.getSelection();
        if (!isInInput && (!selection || selection.toString().length === 0)) {
          e.preventDefault();
          handleCopy();
        }
      }

      // Ctrl/Cmd + M - open email app
      if ((e.ctrlKey || e.metaKey) && e.key === "m") {
        e.preventDefault();
        handleOpenEmailApp();
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [handleCopy, handleOpenEmailApp]);

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
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src="https://proaktiv.no/assets/logos/proaktiv_sort.png"
              alt="Proaktiv"
              className="h-14 w-auto"
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
                  Lenken kan være utløpt eller feil. Ta kontakt med Proaktiv
                  Administrasjonen hvis du trenger ny signatur.
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
                            <Skeleton className="h-[320px] w-full sm:h-[240px]" />
                          ) : signature ? (
                            <iframe
                              title={`Signatur ${versionLabels[version]}`}
                              sandbox=""
                              srcDoc={signatureDoc}
                              className="h-[320px] w-full rounded-md border bg-white sm:h-[240px]"
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

              <div className="flex flex-col gap-3">
                <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
                  <Button onClick={handleCopy} disabled={!signature?.html} className="w-full sm:w-auto">
                    <Copy className="mr-2 h-4 w-4" />
                    Kopier signatur
                    {!isMobile && (
                      <kbd className="ml-2 hidden rounded bg-muted px-1.5 py-0.5 text-[10px] font-medium text-muted-foreground sm:inline-block">
                        ⌘C
                      </kbd>
                    )}
                  </Button>
                  {isMobile && (
                    <Button
                      variant="outline"
                      onClick={handleOpenEmailApp}
                      className="w-full sm:w-auto"
                    >
                      <Mail className="mr-2 h-4 w-4" />
                      Åpne e-post
                    </Button>
                  )}
                </div>
                <p className="text-sm text-muted-foreground">
                  {isMobile
                    ? "Om du er på telefon kan du benytte knappen over for å åpne e-posten din etter at signaturen er kopiert."
                    : "For å sikre at signaturen fremkommer riktig er det viktig at du benytter «Kopier signatur»-knappen og limer inn som ny signatur. Ikke kopier signaturen manuelt."}
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
                  <div className="space-y-2">
                    <p className="font-medium text-foreground">
                      📱 iPhone / Android
                    </p>
                    <ol className="list-decimal space-y-1 pl-4">
                      <li>Åpne denne siden på PC for best resultat.</li>
                      <li>Mobilapper støtter ofte kun tekstsignaturer.</li>
                      <li>For Outlook-appen: Innstillinger → Signatur.</li>
                      <li>For Gmail-appen: Innstillinger → konto → Mobilsignatur.</li>
                    </ol>
                  </div>
                </div>
              </details>

              {/* Keyboard shortcuts info (desktop only) */}
              {!isMobile && (
                <div className="hidden items-center gap-2 text-xs text-muted-foreground sm:flex">
                  <Keyboard className="h-3.5 w-3.5" />
                  <span>Hurtigtaster:</span>
                  <kbd className="rounded bg-muted px-1.5 py-0.5 font-mono text-[10px]">⌘C</kbd>
                  <span>kopier</span>
                  <span className="text-muted-foreground/50">•</span>
                  <kbd className="rounded bg-muted px-1.5 py-0.5 font-mono text-[10px]">⌘M</kbd>
                  <span>åpne e-post</span>
                </div>
              )}

              {/* Support contact section */}
              <div className="mt-4 rounded-lg border bg-muted/30 p-4 text-sm">
                <p className="font-medium text-foreground mb-2">Trenger du hjelp?</p>
                <p className="text-muted-foreground mb-3">
                  Opplever du problemer med signaturen din eller har behov for tilpasninger,
                  ta kontakt med Proaktiv Administrasjonen per e-post.
                </p>
                <Button variant="outline" size="sm" asChild>
                  <a
                    href={`mailto:adrian@proaktiv.no?subject=${encodeURIComponent(
                      `Signatur - ${signature?.employee_name || "Ansatt"}`
                    )}&body=${encodeURIComponent(
                      `Med vennlig hilsen\nProaktiv Administrasjonen\n\n---\n\nØnsker du tilpasninger av din signatur?\nBeskriv:\n\n\nOpplever du tekniske problemer med din signatur?\nBeskriv:\n\n\nSkjermbilde (Win+Shift+S):\n`
                    )}`}
                  >
                    <Mail className="mr-2 h-4 w-4" />
                    Kontakt oss
                  </a>
                </Button>
              </div>
            </div>
          )}
        </div>
        <Toaster />
      </main>
    </div>
  );
}
