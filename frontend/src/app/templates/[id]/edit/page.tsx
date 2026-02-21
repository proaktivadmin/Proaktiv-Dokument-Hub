"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { useParams, useRouter } from "next/navigation";
import {
  ArrowLeft,
  ArrowRightLeft,
  Save,
  SendHorizonal,
  CheckCircle,
  XCircle,
  Archive,
  Code,
  Eye,
  ShieldCheck,
  Loader2,
  History,
  Settings,
  Variable,
  Highlighter,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/hooks/use-toast";
import { templateApi } from "@/lib/api";
import { TemplatePreview } from "@/components/templates/TemplatePreview";
import {
  CKEditorSandbox,
  type CKEditorSandboxRef,
  type CKEditorValidationResult,
} from "@/components/editor/CKEditorSandbox";
import { MergeFieldPanel } from "@/components/editor/MergeFieldPanel";
import { MergeFieldAutocomplete } from "@/components/editor/MergeFieldAutocomplete";
import { useMergeFieldHighlighter } from "@/components/editor/MergeFieldHighlighter";
import { TemplateComparison } from "@/components/editor/TemplateComparison";
import type {
  WorkflowTransition,
  WorkflowStatusResponse,
  WorkflowEvent,
} from "@/types";

const STATUS_CONFIG: Record<
  string,
  { label: string; color: string; icon: React.ReactNode }
> = {
  draft: {
    label: "Utkast",
    color: "bg-gray-100 text-gray-700 border-gray-200",
    icon: <Code className="h-3.5 w-3.5" />,
  },
  in_review: {
    label: "Til godkjenning",
    color: "bg-amber-50 text-amber-700 border-amber-200",
    icon: <Eye className="h-3.5 w-3.5" />,
  },
  published: {
    label: "Publisert",
    color: "bg-emerald-50 text-emerald-700 border-emerald-200",
    icon: <CheckCircle className="h-3.5 w-3.5" />,
  },
  archived: {
    label: "Arkivert",
    color: "bg-slate-100 text-slate-600 border-slate-200",
    icon: <Archive className="h-3.5 w-3.5" />,
  },
};

export default function TemplateEditPage() {
  const params = useParams();
  const router = useRouter();
  const { toast } = useToast();
  const templateId = params.id as string;

  const editorRef = useRef<CKEditorSandboxRef>(null);
  const editorIframeRef = useRef<HTMLIFrameElement>(null);

  const [content, setContent] = useState("");
  const [originalContent, setOriginalContent] = useState("");
  const [title, setTitle] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [isTransitioning, setIsTransitioning] = useState(false);
  const [editorReady, setEditorReady] = useState(false);
  const [isSourceMode, setIsSourceMode] = useState(false);
  const [origin, setOrigin] = useState<string | null>(null);

  const [workflowStatus, setWorkflowStatus] =
    useState<WorkflowStatusResponse | null>(null);
  const [workflowHistory, setWorkflowHistory] = useState<WorkflowEvent[]>([]);
  const [validationResult, setValidationResult] =
    useState<CKEditorValidationResult | null>(null);

  const hasChanges = content !== originalContent;

  const { isActive: isHighlightActive, toggle: toggleHighlight, removeHighlights } =
    useMergeFieldHighlighter({ editorIframeRef, isSourceMode });

  const handleInsertAtCursor = useCallback(
    (html: string) => {
      editorRef.current?.insertAtCursor(html);
    },
    []
  );

  // Load template content and workflow status
  useEffect(() => {
    async function load() {
      setIsLoading(true);
      try {
        const [contentRes, statusRes, historyRes, templateRes] = await Promise.all([
          templateApi.getContent(templateId),
          templateApi.getWorkflowStatus(templateId),
          templateApi.getWorkflowHistory(templateId),
          templateApi.getById(templateId),
        ]);
        setContent(contentRes.content);
        setOriginalContent(contentRes.content);
        setTitle(contentRes.title);
        setWorkflowStatus(statusRes);
        setWorkflowHistory(historyRes);
        setOrigin(templateRes.origin ?? null);
      } catch {
        toast({
          title: "Feil",
          description: "Kunne ikke laste malinnhold.",
          variant: "destructive",
        });
      } finally {
        setIsLoading(false);
      }
    }
    load();
  }, [templateId, toast]);

  const handleSave = useCallback(async () => {
    setIsSaving(true);
    removeHighlights();
    try {
      const currentContent =
        (await editorRef.current?.getContent()) || content;
      await templateApi.saveContent(templateId, currentContent);
      setOriginalContent(currentContent);
      setContent(currentContent);
      toast({ title: "Lagret", description: "Malinnholdet ble lagret." });
    } catch {
      toast({
        title: "Feil",
        description: "Kunne ikke lagre innholdet.",
        variant: "destructive",
      });
    } finally {
      setIsSaving(false);
    }
  }, [content, templateId, toast, removeHighlights]);

  const handleWorkflowAction = useCallback(
    async (action: WorkflowTransition["action"]) => {
      setIsTransitioning(true);
      try {
        const result = await templateApi.transitionWorkflow(templateId, {
          action,
        });
        setWorkflowStatus(result);
        const updatedHistory =
          await templateApi.getWorkflowHistory(templateId);
        setWorkflowHistory(updatedHistory);

        const labels: Record<string, string> = {
          submit: "Sendt til gjennomgang",
          approve: "Godkjent og publisert",
          reject: "Avvist",
          unpublish: "Avpublisert",
          archive: "Arkivert",
          restore: "Gjenopprettet",
        };
        toast({
          title: labels[action] || action,
          description: `Malen ble ${(labels[action] || action).toLowerCase()}.`,
        });
      } catch (err) {
        toast({
          title: "Feil",
          description:
            err instanceof Error
              ? err.message
              : "Kunne ikke utføre handling.",
          variant: "destructive",
        });
      } finally {
        setIsTransitioning(false);
      }
    },
    [templateId, toast]
  );

  const handleValidate = useCallback(async () => {
    const result = await editorRef.current?.validate();
    if (result) {
      setValidationResult(result);
      toast({
        title: result.isClean
          ? "Validering bestått"
          : "CKEditor endret innholdet",
        description: result.isClean
          ? "CKEditor gjorde ingen endringer."
          : `${result.changes.length} endring(er) oppdaget.`,
        variant: result.isClean ? "default" : "destructive",
      });
    }
  }, [toast]);

  const toggleSourceMode = useCallback(() => {
    if (isSourceMode) {
      editorRef.current?.switchToWysiwyg();
    } else {
      editorRef.current?.switchToSource();
    }
    setIsSourceMode((prev) => !prev);
  }, [isSourceMode]);

  const currentStatus = workflowStatus?.workflow_status || "draft";
  const statusConfig = STATUS_CONFIG[currentStatus] || STATUS_CONFIG.draft;

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center bg-background">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className="flex h-screen flex-col bg-background">
      {/* Header toolbar */}
      <header className="flex items-center justify-between border-b bg-white px-4 py-2 shadow-soft">
        <div className="flex items-center gap-3">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => router.push(`/templates/${templateId}`)}
          >
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="font-serif text-lg font-semibold text-[#272630] truncate max-w-[300px]">
              {title}
            </h1>
            <div className="flex items-center gap-2">
              <Badge
                variant="outline"
                className={`gap-1 text-xs ${statusConfig.color}`}
              >
                {statusConfig.icon}
                {statusConfig.label}
              </Badge>
              {hasChanges && (
                <span className="text-xs text-amber-600">Ulagrede endringer</span>
              )}
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* Source/WYSIWYG toggle */}
          <Button variant="outline" size="sm" onClick={toggleSourceMode}>
            <Code className="h-4 w-4 mr-1" />
            {isSourceMode ? "WYSIWYG" : "Kilde"}
          </Button>

          {/* Merge field highlight toggle */}
          <Button
            variant={isHighlightActive ? "secondary" : "outline"}
            size="sm"
            onClick={toggleHighlight}
            disabled={isSourceMode}
            title="Uthev flettekoder"
          >
            <Highlighter className="h-4 w-4 mr-1" />
            Flettekoder
          </Button>

          {/* Validate */}
          <Button variant="outline" size="sm" onClick={handleValidate}>
            <ShieldCheck className="h-4 w-4 mr-1" />
            Valider i CKEditor
          </Button>

          {/* Save */}
          <Button
            size="sm"
            onClick={handleSave}
            disabled={isSaving || !hasChanges}
          >
            {isSaving ? (
              <Loader2 className="h-4 w-4 mr-1 animate-spin" />
            ) : (
              <Save className="h-4 w-4 mr-1" />
            )}
            Lagre
          </Button>

          {/* Workflow actions */}
          {currentStatus === "draft" && (
            <Button
              size="sm"
              variant="outline"
              onClick={() => handleWorkflowAction("submit")}
              disabled={isTransitioning}
            >
              <SendHorizonal className="h-4 w-4 mr-1" />
              Send til gjennomgang
            </Button>
          )}
          {currentStatus === "in_review" && (
            <>
              <Button
                size="sm"
                className="bg-emerald-600 hover:bg-emerald-700"
                onClick={() => handleWorkflowAction("approve")}
                disabled={isTransitioning}
              >
                <CheckCircle className="h-4 w-4 mr-1" />
                Godkjenn
              </Button>
              <Button
                size="sm"
                variant="destructive"
                onClick={() => handleWorkflowAction("reject")}
                disabled={isTransitioning}
              >
                <XCircle className="h-4 w-4 mr-1" />
                Avvis
              </Button>
            </>
          )}
          {currentStatus === "published" && (
            <Button
              size="sm"
              variant="outline"
              onClick={() => handleWorkflowAction("unpublish")}
              disabled={isTransitioning}
            >
              Avpubliser
            </Button>
          )}
        </div>
      </header>

      {/* Main content area */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left panel — CKEditor */}
        <div className="w-[60%] border-r relative">
          <CKEditorSandbox
            ref={(node) => {
              // Forward the CKEditorSandboxRef to editorRef
              (editorRef as React.MutableRefObject<CKEditorSandboxRef | null>).current = node;
              // Capture the underlying iframe element for autocomplete/highlighter
              const wrapper = (node as unknown as { _iframeEl?: HTMLIFrameElement })?._iframeEl;
              if (!wrapper) {
                // Fallback: find the iframe in the DOM
                const container = document.querySelector('[title="CKEditor 4 Sandbox"]');
                if (container instanceof HTMLIFrameElement) {
                  (editorIframeRef as React.MutableRefObject<HTMLIFrameElement | null>).current = container;
                }
              }
            }}
            content={content}
            onChange={setContent}
            onValidation={setValidationResult}
            onReady={() => {
              setEditorReady(true);
              const iframe = document.querySelector('[title="CKEditor 4 Sandbox"]');
              if (iframe instanceof HTMLIFrameElement) {
                (editorIframeRef as React.MutableRefObject<HTMLIFrameElement | null>).current = iframe;
              }
            }}
            onModeChange={(mode) => setIsSourceMode(mode === "source")}
            className="h-full"
          />
          {!editorReady && (
            <div className="absolute inset-0 flex items-center justify-center bg-white/80">
              <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
            </div>
          )}
          <MergeFieldAutocomplete
            editorIframeRef={editorIframeRef}
            onInsert={handleInsertAtCursor}
            isSourceMode={isSourceMode}
          />
        </div>

        {/* Right panel — Tabs */}
        <div className="w-[40%] flex flex-col overflow-hidden">
          <Tabs defaultValue="preview" className="flex flex-1 flex-col">
            <TabsList className="mx-3 mt-3 shrink-0">
              <TabsTrigger value="preview" className="gap-1">
                <Eye className="h-3.5 w-3.5" />
                Forhåndsvisning
              </TabsTrigger>
              <TabsTrigger value="validation" className="gap-1">
                <ShieldCheck className="h-3.5 w-3.5" />
                Validering
              </TabsTrigger>
              <TabsTrigger value="settings" className="gap-1">
                <Settings className="h-3.5 w-3.5" />
                Innstillinger
              </TabsTrigger>
              <TabsTrigger value="history" className="gap-1">
                <History className="h-3.5 w-3.5" />
                Historikk
              </TabsTrigger>
              <TabsTrigger value="flettekoder" className="gap-1">
                <Variable className="h-3.5 w-3.5" />
                Flettekoder
              </TabsTrigger>
              {origin === "vitec_system" && (
                <TabsTrigger value="compare" className="gap-1">
                  <ArrowRightLeft className="h-3.5 w-3.5" />
                  Sammenlign
                </TabsTrigger>
              )}
            </TabsList>

            <TabsContent value="preview" className="flex-1 overflow-auto p-3">
              <div className="rounded-lg border bg-white shadow-card">
                <TemplatePreview content={content} title={title} />
              </div>
            </TabsContent>

            <TabsContent value="validation" className="flex-1 overflow-auto p-3">
              <div className="space-y-4">
                <h3 className="font-serif text-lg font-semibold">
                  CKEditor-validering
                </h3>
                {validationResult ? (
                  <div className="space-y-3">
                    <div
                      className={`rounded-lg border p-4 ${
                        validationResult.isClean
                          ? "bg-emerald-50 border-emerald-200"
                          : "bg-amber-50 border-amber-200"
                      }`}
                    >
                      <p className="font-medium">
                        {validationResult.isClean
                          ? "Ingen endringer — CKEditor aksepterer innholdet"
                          : `${validationResult.changes.length} endring(er) oppdaget`}
                      </p>
                      <p className="text-sm text-muted-foreground mt-1">
                        Input: {validationResult.inputLength} tegn → Output:{" "}
                        {validationResult.outputLength} tegn
                      </p>
                    </div>
                    {validationResult.changes.map((change, i) => (
                      <div
                        key={i}
                        className="rounded-lg border p-3 space-y-2"
                      >
                        <div className="flex items-center gap-2">
                          <Badge
                            variant="outline"
                            className={
                              change.type === "stripped"
                                ? "text-red-600 border-red-200"
                                : change.type === "added"
                                ? "text-blue-600 border-blue-200"
                                : "text-amber-600 border-amber-200"
                            }
                          >
                            {change.type === "stripped"
                              ? "Fjernet"
                              : change.type === "added"
                              ? "Lagt til"
                              : "Omskrevet"}
                          </Badge>
                          <span className="text-sm">{change.description}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-muted-foreground text-sm">
                    Klikk &quot;Valider i CKEditor&quot; for å sjekke om CKEditor
                    endrer innholdet.
                  </p>
                )}
              </div>
            </TabsContent>

            <TabsContent value="settings" className="flex-1 overflow-auto p-3">
              <div className="space-y-4">
                <h3 className="font-serif text-lg font-semibold">
                  Innstillinger
                </h3>
                <p className="text-sm text-muted-foreground">
                  For å endre malinnstillinger, bruk{" "}
                  <button
                    onClick={() =>
                      router.push(`/templates/${templateId}`)
                    }
                    className="text-[#BCAB8A] underline hover:text-[#272630] transition-colors"
                  >
                    visningssiden
                  </button>
                  .
                </p>
              </div>
            </TabsContent>

            <TabsContent value="history" className="flex-1 overflow-auto p-3">
              <div className="space-y-4">
                <h3 className="font-serif text-lg font-semibold">
                  Arbeidsflythistorikk
                </h3>
                {workflowHistory.length > 0 ? (
                  <div className="space-y-2">
                    {workflowHistory.map((event, i) => {
                      const fromLabel =
                        STATUS_CONFIG[event.from_status]?.label ||
                        event.from_status;
                      const toLabel =
                        STATUS_CONFIG[event.to_status]?.label ||
                        event.to_status;
                      return (
                        <div
                          key={i}
                          className="flex items-start gap-3 rounded-lg border p-3"
                        >
                          <div className="flex-1">
                            <p className="text-sm font-medium">
                              {fromLabel} → {toLabel}
                            </p>
                            {event.notes && (
                              <p className="text-xs text-muted-foreground mt-1">
                                {event.notes}
                              </p>
                            )}
                            <p className="text-xs text-muted-foreground mt-1">
                              {event.actor && `Av ${event.actor} · `}
                              {event.timestamp
                                ? new Date(event.timestamp).toLocaleString(
                                    "nb-NO"
                                  )
                                : ""}
                            </p>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                ) : (
                  <p className="text-sm text-muted-foreground">
                    Ingen historikk ennå.
                  </p>
                )}
              </div>
            </TabsContent>

            <TabsContent
              value="flettekoder"
              className="flex-1 overflow-auto p-3"
            >
              <MergeFieldPanel
                onInsert={handleInsertAtCursor}
                currentContent={content}
                templateId={templateId}
              />
            </TabsContent>

            {origin === "vitec_system" && (
              <TabsContent value="compare" className="flex-1 overflow-auto">
                <TemplateComparison
                  templateId={templateId}
                  currentContent={content}
                  templateTitle={title}
                  onAdopt={(newContent) => {
                    setContent(newContent);
                    setOriginalContent(newContent);
                  }}
                  onDismiss={() => {
                    const tabsList = document.querySelector('[role="tablist"]');
                    const previewTab = tabsList?.querySelector('[value="preview"]') as HTMLButtonElement | null;
                    previewTab?.click();
                  }}
                />
              </TabsContent>
            )}
          </Tabs>
        </div>
      </div>
    </div>
  );
}
