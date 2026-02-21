"use client";

import { useState, useCallback } from "react";
import {
  AlertTriangle,
  CheckCircle,
  ArrowRightLeft,
  Loader2,
  Sparkles,
  X,
  ChevronDown,
  ChevronUp,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import { useToast } from "@/hooks/use-toast";
import { templateComparisonApi } from "@/lib/api";
import type { AnalysisReport, ChangeClassification } from "@/types";

interface TemplateComparisonProps {
  templateId: string;
  currentContent: string;
  templateTitle: string;
  onAdopt: (newContent: string) => void;
  onDismiss: () => void;
}

const RECOMMENDATION_CONFIG: Record<
  string,
  { label: string; color: string; description: string }
> = {
  ADOPT: {
    label: "Overta",
    color: "bg-emerald-50 text-emerald-700 border-emerald-200",
    description: "Anbefaler å overta Vitecs versjon",
  },
  IGNORE: {
    label: "Behold",
    color: "bg-slate-100 text-slate-700 border-slate-200",
    description: "Anbefaler å beholde vår versjon",
  },
  PARTIAL_MERGE: {
    label: "Delvis overtagelse",
    color: "bg-amber-50 text-amber-700 border-amber-200",
    description: "Anbefaler å ta noen endringer",
  },
  REVIEW_REQUIRED: {
    label: "Gjennomgang nødvendig",
    color: "bg-red-50 text-red-700 border-red-200",
    description: "Krever manuell vurdering",
  },
};

const CATEGORY_LABELS: Record<string, string> = {
  cosmetic: "Kosmetisk",
  structural: "Strukturell",
  content: "Innhold",
  merge_fields: "Flettekoder",
  logic: "Logikk",
  breaking: "Kritisk",
  kosmetisk: "Kosmetisk",
  strukturell: "Strukturell",
  innhold: "Innhold",
  flettekoder: "Flettekoder",
  logikk: "Logikk",
  kritisk: "Kritisk",
};

function ClassificationBadges({
  classification,
}: {
  classification: ChangeClassification;
}) {
  const items = [
    { key: "cosmetic", label: "Kosmetisk", count: classification.cosmetic },
    {
      key: "structural",
      label: "Strukturell",
      count: classification.structural,
    },
    { key: "content", label: "Innhold", count: classification.content },
    {
      key: "merge_fields",
      label: "Flettekoder",
      count: classification.merge_fields,
    },
    { key: "logic", label: "Logikk", count: classification.logic },
    { key: "breaking", label: "Kritisk", count: classification.breaking },
  ];

  return (
    <div className="flex flex-wrap gap-2">
      {items
        .filter((item) => item.count > 0)
        .map((item) => (
          <Badge
            key={item.key}
            variant="outline"
            className={
              item.key === "breaking"
                ? "text-red-600 border-red-200 bg-red-50"
                : item.key === "logic" || item.key === "merge_fields"
                  ? "text-amber-600 border-amber-200 bg-amber-50"
                  : "text-slate-600 border-slate-200"
            }
          >
            {item.label}: {item.count}
          </Badge>
        ))}
    </div>
  );
}

export function TemplateComparison({
  templateId,
  currentContent: _currentContent,
  templateTitle: _templateTitle,
  onAdopt,
  onDismiss,
}: TemplateComparisonProps) {
  void _currentContent;
  void _templateTitle;
  const { toast } = useToast();
  const [pastedHtml, setPastedHtml] = useState("");
  const [report, setReport] = useState<AnalysisReport | null>(null);
  const [isComparing, setIsComparing] = useState(false);
  const [isApplying, setIsApplying] = useState(false);
  const [showDetails, setShowDetails] = useState(false);

  const handleCompare = useCallback(async () => {
    if (!pastedHtml.trim()) {
      toast({
        title: "Mangler innhold",
        description: "Lim inn oppdatert Vitec-kode først.",
        variant: "destructive",
      });
      return;
    }

    setIsComparing(true);
    setReport(null);

    try {
      const result = await templateComparisonApi.compareWithVitec(
        templateId,
        pastedHtml
      );
      setReport(result);

      if (result.raw_comparison.hashes_match) {
        toast({
          title: "Identisk",
          description: "Innholdet er identisk med lagret versjon.",
        });
      }
    } catch {
      toast({
        title: "Feil",
        description: "Kunne ikke sammenligne malene.",
        variant: "destructive",
      });
    } finally {
      setIsComparing(false);
    }
  }, [pastedHtml, templateId, toast]);

  const handleAdopt = useCallback(async () => {
    setIsApplying(true);
    try {
      await templateComparisonApi.applyComparison(
        templateId,
        "adopt",
        pastedHtml
      );
      onAdopt(pastedHtml);
      toast({
        title: "Overtatt",
        description: "Vitec-versjonen er nå lagret.",
      });
    } catch {
      toast({
        title: "Feil",
        description: "Kunne ikke overta versjonen.",
        variant: "destructive",
      });
    } finally {
      setIsApplying(false);
    }
  }, [templateId, pastedHtml, onAdopt, toast]);

  const handleIgnore = useCallback(async () => {
    setIsApplying(true);
    try {
      await templateComparisonApi.applyComparison(
        templateId,
        "ignore",
        pastedHtml
      );
      toast({
        title: "Beholdt",
        description: "Vår versjon beholdes. Vitec-oppdateringen er markert som gjennomgått.",
      });
      onDismiss();
    } catch {
      toast({
        title: "Feil",
        description: "Kunne ikke lagre valget.",
        variant: "destructive",
      });
    } finally {
      setIsApplying(false);
    }
  }, [templateId, pastedHtml, onDismiss, toast]);

  const recConfig = report
    ? RECOMMENDATION_CONFIG[report.recommendation] ||
      RECOMMENDATION_CONFIG.REVIEW_REQUIRED
    : null;

  return (
    <div className="flex flex-col gap-4 h-full overflow-auto p-3">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="font-serif text-lg font-semibold text-[#272630]">
          Sammenlign med Vitec-oppdatering
        </h3>
        <Button variant="ghost" size="icon" onClick={onDismiss}>
          <X className="h-4 w-4" />
        </Button>
      </div>

      {/* Paste area */}
      <div className="space-y-2">
        <label className="text-sm font-medium text-[#272630]">
          Lim inn oppdatert Vitec-kode
        </label>
        <Textarea
          value={pastedHtml}
          onChange={(e) => setPastedHtml(e.target.value)}
          placeholder="Lim inn HTML-koden fra Vitec her..."
          className="min-h-[120px] font-mono text-xs transition-colors duration-normal focus:ring-2 focus:ring-[#BCAB8A]"
        />
        <Button
          onClick={handleCompare}
          disabled={isComparing || !pastedHtml.trim()}
          className="w-full"
        >
          {isComparing ? (
            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
          ) : (
            <ArrowRightLeft className="h-4 w-4 mr-2" />
          )}
          Sammenlign
        </Button>
      </div>

      {/* Analysis results */}
      {report && (
        <div className="space-y-4">
          {/* Identical check */}
          {report.raw_comparison.hashes_match ? (
            <div className="rounded-lg border border-emerald-200 bg-emerald-50 p-4">
              <div className="flex items-center gap-2">
                <CheckCircle className="h-5 w-5 text-emerald-600" />
                <p className="font-medium text-emerald-700">
                  Identisk — ingen endringer oppdaget
                </p>
              </div>
            </div>
          ) : (
            <>
              {/* AI badge */}
              {report.ai_powered && (
                <div className="flex items-center gap-1.5 text-xs text-[#BCAB8A]">
                  <Sparkles className="h-3.5 w-3.5" />
                  AI-analyse
                </div>
              )}

              {/* Summary */}
              <div className="rounded-lg border bg-white p-4 shadow-card space-y-3">
                <p className="text-sm leading-relaxed">{report.summary}</p>

                {/* Classification badges */}
                <ClassificationBadges
                  classification={report.raw_comparison.classification}
                />
              </div>

              {/* Changes by category */}
              {Object.keys(report.changes_by_category).length > 0 && (
                <div className="rounded-lg border bg-white p-4 shadow-card space-y-3">
                  <button
                    onClick={() => setShowDetails(!showDetails)}
                    className="flex items-center gap-2 text-sm font-medium text-[#272630] hover:text-[#BCAB8A] transition-colors duration-normal w-full"
                  >
                    {showDetails ? (
                      <ChevronUp className="h-4 w-4" />
                    ) : (
                      <ChevronDown className="h-4 w-4" />
                    )}
                    Detaljerte endringer
                  </button>

                  {showDetails && (
                    <div className="space-y-3 pt-2">
                      {Object.entries(report.changes_by_category).map(
                        ([category, items]) => (
                          <div key={category}>
                            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-1">
                              {CATEGORY_LABELS[category] || category}
                            </p>
                            <ul className="space-y-1">
                              {items.map((item, i) => (
                                <li
                                  key={i}
                                  className="text-sm text-[#272630] pl-3 border-l-2 border-[#E9E7DC]"
                                >
                                  {item}
                                </li>
                              ))}
                            </ul>
                          </div>
                        )
                      )}
                    </div>
                  )}
                </div>
              )}

              {/* Impact */}
              <div className="rounded-lg border bg-white p-4 shadow-card">
                <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-1">
                  Påvirkning på vår versjon
                </p>
                <p className="text-sm leading-relaxed">{report.impact}</p>
              </div>

              {/* Conflicts */}
              {report.conflicts.length > 0 && (
                <div className="rounded-lg border border-amber-200 bg-amber-50 p-4 space-y-2">
                  <div className="flex items-center gap-2">
                    <AlertTriangle className="h-4 w-4 text-amber-600" />
                    <p className="text-sm font-medium text-amber-700">
                      {report.conflicts.length} konflikt(er)
                    </p>
                  </div>
                  {report.conflicts.map((conflict, i) => (
                    <div
                      key={i}
                      className="text-sm text-amber-800 pl-6 space-y-0.5"
                    >
                      <p className="font-medium">{conflict.section}</p>
                      <p className="text-xs">
                        Vår endring: {conflict.our_change}
                      </p>
                      <p className="text-xs">
                        Vitec endring: {conflict.vitec_change}
                      </p>
                    </div>
                  ))}
                </div>
              )}

              {/* Recommendation */}
              {recConfig && (
                <div
                  className={`rounded-lg border p-4 ${recConfig.color}`}
                >
                  <p className="text-sm font-medium">
                    Anbefaling: {recConfig.label}
                  </p>
                  <p className="text-xs mt-1">{recConfig.description}</p>
                  {report.suggested_actions.length > 0 && (
                    <ul className="mt-2 space-y-1">
                      {report.suggested_actions.map((action, i) => (
                        <li key={i} className="text-xs pl-3 border-l-2">
                          {action}
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              )}

              {/* Action buttons */}
              <div className="flex gap-2 pt-2">
                <Button
                  variant="outline"
                  onClick={handleIgnore}
                  disabled={isApplying}
                  className="flex-1"
                >
                  Behold vår versjon
                </Button>
                <Button
                  onClick={handleAdopt}
                  disabled={isApplying}
                  className="flex-1 bg-[#272630] hover:bg-[#272630]/90"
                >
                  {isApplying ? (
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  ) : null}
                  Overta Vitec-versjon
                </Button>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}
