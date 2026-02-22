"use client";

import { useState, useCallback, useRef } from "react";
import { useDropzone } from "react-dropzone";
import {
  Upload,
  FileText,
  X,
  Loader2,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Download,
  Save,
  Code2,
} from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  wordConversionApi,
  templateApi,
  type ConversionResult,
} from "@/lib/api";
import { useToast } from "@/hooks/use-toast";
import { cn } from "@/lib/utils";

interface WordConversionDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess?: () => void;
}

type ConversionState = "idle" | "converting" | "done" | "error";

export function WordConversionDialog({
  open,
  onOpenChange,
  onSuccess,
}: WordConversionDialogProps) {
  const [file, setFile] = useState<File | null>(null);
  const [state, setState] = useState<ConversionState>("idle");
  const [result, setResult] = useState<ConversionResult | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { toast } = useToast();

  const handleReset = useCallback(() => {
    setFile(null);
    setState("idle");
    setResult(null);
    setErrorMessage(null);
    setIsSaving(false);
  }, []);

  const handleClose = useCallback(() => {
    if (state !== "converting" && !isSaving) {
      handleReset();
      onOpenChange(false);
    }
  }, [state, isSaving, handleReset, onOpenChange]);

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      if (acceptedFiles.length === 0) return;

      const selected = acceptedFiles[0];
      const ext = selected.name.split(".").pop()?.toLowerCase();

      if (ext !== "docx" && ext !== "rtf") {
        setErrorMessage(
          "Kun .docx- og .rtf-filer er støttet."
        );
        return;
      }

      setFile(selected);
      setErrorMessage(null);
      setState("converting");
      setResult(null);

      try {
        const conversionResult = await wordConversionApi.convertDocx(selected);
        setResult(conversionResult);
        setState("done");
      } catch (err) {
        setState("error");
        setErrorMessage(
          err instanceof Error
            ? err.message
            : "Konvertering feilet. Prøv igjen."
        );
      }
    },
    []
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        [".docx"],
      "application/rtf": [".rtf"],
      "text/rtf": [".rtf"],
    },
    maxFiles: 1,
    multiple: false,
    noClick: true,
    disabled: state === "converting",
  });

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      onDrop(Array.from(files));
    }
    e.target.value = "";
  };

  const handleDownloadHtml = useCallback(() => {
    if (!result) return;
    const blob = new Blob([result.html], { type: "text/html;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = file
      ? file.name.replace(/\.(docx|rtf)$/i, ".html")
      : "converted.html";
    a.click();
    URL.revokeObjectURL(url);
  }, [result, file]);

  const handleSaveAsDraft = useCallback(async () => {
    if (!result || !file) return;
    setIsSaving(true);

    try {
      const htmlBlob = new Blob([result.html], { type: "text/html" });
      const htmlFile = new File(
        [htmlBlob],
        file.name.replace(/\.(docx|rtf)$/i, ".html"),
        { type: "text/html" }
      );

      await templateApi.upload({
        file: htmlFile,
        title: file.name.replace(/\.(docx|rtf)$/i, ""),
        description: `Konvertert fra dokument: ${file.name}`,
        status: "draft",
      });

      toast({
        title: "Mal opprettet",
        description: `"${file.name.replace(/\.(docx|rtf)$/i, "")}" er lagret som utkast.`,
      });

      onSuccess?.();
      handleClose();
    } catch (err) {
      toast({
        title: "Lagring feilet",
        description:
          err instanceof Error ? err.message : "Kunne ikke lagre malen.",
        variant: "destructive",
      });
    } finally {
      setIsSaving(false);
    }
  }, [result, file, toast, onSuccess, handleClose]);

  const warningCount = result?.warnings.length ?? 0;
  const validationPassed =
    result?.validation.filter((v) => v.passed).length ?? 0;
  const validationFailed =
    result?.validation.filter((v) => !v.passed).length ?? 0;

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-[720px] max-h-[90vh] flex flex-col">
        <DialogHeader>
          <DialogTitle className="font-serif text-xl">
            Konverter dokument
          </DialogTitle>
        </DialogHeader>

        <ScrollArea className="flex-1 pr-4 -mr-4">
          <div className="space-y-5 pb-4">
            {/* File upload / status area */}
            {state === "idle" && !file && (
              <div
                {...getRootProps()}
                onClick={() => fileInputRef.current?.click()}
                className={cn(
                  "border-2 border-dashed rounded-lg p-10 text-center cursor-pointer transition-colors duration-normal",
                  isDragActive
                    ? "border-[#BCAB8A] bg-[#BCAB8A]/5"
                    : "border-muted-foreground/25 hover:border-[#BCAB8A]/50"
                )}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".docx,.rtf"
                  onChange={handleFileInputChange}
                  style={{ display: "none" }}
                />
                <input {...getInputProps()} />
                <Upload className="mx-auto h-10 w-10 text-muted-foreground/60 mb-3" />
                <p className="text-sm text-muted-foreground mb-1">
                  {isDragActive
                    ? "Slipp filen her..."
                    : "Dra og slipp fil her, eller klikk for å velge"}
                </p>
                <p className="text-xs text-muted-foreground/60">
                  Word (.docx) og RTF (.rtf) er støttet
                </p>
              </div>
            )}

            {/* Error for wrong file type */}
            {errorMessage && state === "idle" && (
              <div className="p-3 text-sm text-destructive bg-destructive/10 rounded-lg">
                {errorMessage}
              </div>
            )}

            {/* Converting state */}
            {state === "converting" && file && (
              <div className="flex flex-col items-center gap-3 py-8">
                <Loader2 className="h-8 w-8 animate-spin text-[#BCAB8A]" />
                <p className="text-sm text-muted-foreground">
                  Konverterer{" "}
                  <span className="font-medium text-foreground">
                    {file.name}
                  </span>
                  ...
                </p>
              </div>
            )}

            {/* Error state */}
            {state === "error" && (
              <div className="space-y-4">
                <div className="p-4 text-sm text-destructive bg-destructive/10 rounded-lg flex items-start gap-3">
                  <XCircle className="h-5 w-5 shrink-0 mt-0.5" />
                  <div>
                    <p className="font-medium">Konvertering feilet</p>
                    <p className="mt-1">{errorMessage}</p>
                  </div>
                </div>
                <Button
                  variant="outline"
                  onClick={handleReset}
                  className="w-full"
                >
                  Prøv igjen
                </Button>
              </div>
            )}

            {/* Results */}
            {state === "done" && result && (
              <>
                {/* File info bar */}
                <div className="flex items-center gap-3 p-3 border rounded-lg bg-muted/30">
                  <FileText className="h-5 w-5 text-[#BCAB8A] shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{file?.name}</p>
                    <p className="text-xs text-muted-foreground">
                      {file
                        ? `${(file.size / 1024).toFixed(1)} KB`
                        : ""}
                      {" → "}
                      {(new Blob([result.html]).size / 1024).toFixed(1)} KB HTML
                    </p>
                  </div>
                  <Button variant="ghost" size="icon" onClick={handleReset}>
                    <X className="h-4 w-4" />
                    <span className="sr-only">Fjern</span>
                  </Button>
                </div>

                {/* Preview */}
                <section>
                  <h3 className="text-sm font-medium mb-2 flex items-center gap-2">
                    <Code2 className="h-4 w-4 text-[#BCAB8A]" />
                    Forhåndsvisning
                  </h3>
                  <div className="border rounded-lg overflow-hidden bg-white">
                    <iframe
                      srcDoc={result.html}
                      title="Konvertert forhåndsvisning"
                      className="w-full border-0"
                      style={{ height: 400 }}
                      sandbox="allow-same-origin"
                    />
                  </div>
                </section>

                {/* Warnings */}
                {warningCount > 0 && (
                  <section>
                    <h3 className="text-sm font-medium mb-2 flex items-center gap-2">
                      <AlertTriangle className="h-4 w-4 text-amber-500" />
                      Advarsler ({warningCount})
                    </h3>
                    <div className="border border-amber-200 bg-amber-50 rounded-lg p-3 space-y-1.5">
                      {result.warnings.map((w, i) => (
                        <p
                          key={i}
                          className="text-xs text-amber-800 flex items-start gap-2"
                        >
                          <span className="shrink-0 mt-0.5">⚠</span>
                          {w}
                        </p>
                      ))}
                    </div>
                  </section>
                )}

                {/* Validation */}
                <section>
                  <h3 className="text-sm font-medium mb-2 flex items-center gap-2">
                    {result.is_valid ? (
                      <CheckCircle2 className="h-4 w-4 text-emerald-500" />
                    ) : (
                      <XCircle className="h-4 w-4 text-destructive" />
                    )}
                    Validering ({validationPassed}/{result.validation.length}{" "}
                    bestått)
                  </h3>
                  <div className="border rounded-lg divide-y">
                    {result.validation.map((item, i) => (
                      <div
                        key={i}
                        className="flex items-start gap-2.5 px-3 py-2"
                      >
                        {item.passed ? (
                          <CheckCircle2 className="h-4 w-4 text-emerald-500 shrink-0 mt-0.5" />
                        ) : (
                          <XCircle className="h-4 w-4 text-destructive shrink-0 mt-0.5" />
                        )}
                        <div className="min-w-0">
                          <p className="text-xs font-medium">{item.rule}</p>
                          {item.detail && (
                            <p className="text-xs text-muted-foreground">
                              {item.detail}
                            </p>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                  {validationFailed > 0 && (
                    <p className="text-xs text-destructive mt-2">
                      {validationFailed} valideringsregel(er) feilet. Sjekk
                      resultatet før lagring.
                    </p>
                  )}
                </section>

                {/* Merge fields */}
                {result.merge_fields_detected.length > 0 && (
                  <section>
                    <h3 className="text-sm font-medium mb-2 flex items-center gap-2">
                      <Code2 className="h-4 w-4 text-[#BCAB8A]" />
                      Flettekoder funnet (
                      {result.merge_fields_detected.length})
                    </h3>
                    <div className="border rounded-lg p-3 flex flex-wrap gap-1.5">
                      {result.merge_fields_detected.map((field) => (
                        <span
                          key={field}
                          className="text-xs font-mono px-2 py-1 rounded bg-[#F3E8FF] text-[#6D28D9]"
                        >
                          [[{field}]]
                        </span>
                      ))}
                    </div>
                  </section>
                )}

                {/* Actions */}
                <div className="flex items-center justify-end gap-3 pt-2 border-t">
                  <Button
                    variant="outline"
                    onClick={handleDownloadHtml}
                  >
                    <Download className="h-4 w-4 mr-2" />
                    Last ned HTML
                  </Button>
                  <Button
                    onClick={handleSaveAsDraft}
                    disabled={isSaving}
                  >
                    {isSaving ? (
                      <>
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        Lagrer...
                      </>
                    ) : (
                      <>
                        <Save className="h-4 w-4 mr-2" />
                        Lagre som utkast
                      </>
                    )}
                  </Button>
                </div>
              </>
            )}
          </div>
        </ScrollArea>
      </DialogContent>
    </Dialog>
  );
}
