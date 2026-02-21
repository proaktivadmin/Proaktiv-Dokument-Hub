"use client";

import { useState, useEffect, useCallback } from "react";
import {
  ArrowLeft,
  CheckCircle2,
  AlertTriangle,
  Layers,
  Merge,
  Loader2,
  Eye,
  ChevronDown,
  ChevronUp,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  dedupApi,
  type DedupMergeCandidateGroup,
  type DedupMergeAnalysis,
  type DedupMergePreview,
} from "@/lib/api";

type DashboardView = "candidates" | "analysis" | "preview";

const complexityLabels: Record<string, string> = {
  simple: "Enkel",
  moderate: "Moderat",
  complex: "Kompleks",
};

const complexityColors: Record<string, string> = {
  simple: "bg-green-50 text-green-700 border-green-200",
  moderate: "bg-amber-50 text-amber-700 border-amber-200",
  complex: "bg-red-50 text-red-700 border-red-200",
};

export function DeduplicationDashboard() {
  const [view, setView] = useState<DashboardView>("candidates");
  const [groups, setGroups] = useState<DedupMergeCandidateGroup[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Analysis state
  const [selectedGroup, setSelectedGroup] = useState<DedupMergeCandidateGroup | null>(null);
  const [analysis, setAnalysis] = useState<DedupMergeAnalysis | null>(null);
  const [analyzingLoading, setAnalyzingLoading] = useState(false);

  // Preview state
  const [primaryId, setPrimaryId] = useState<string>("");
  const [preview, setPreview] = useState<DedupMergePreview | null>(null);
  const [previewLoading, setPreviewLoading] = useState(false);

  // Merge state
  const [merging, setMerging] = useState(false);
  const [mergeComplete, setMergeComplete] = useState(false);

  const loadCandidates = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await dedupApi.candidates();
      setGroups(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Kunne ikke laste kandidater");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadCandidates();
  }, [loadCandidates]);

  const handleAnalyze = async (group: DedupMergeCandidateGroup) => {
    setSelectedGroup(group);
    setAnalyzingLoading(true);
    setView("analysis");
    setAnalysis(null);
    setPreview(null);
    setMergeComplete(false);

    const ids = group.candidates.map((c) => c.template_id);
    setPrimaryId(ids[0]);

    try {
      const result = await dedupApi.analyze(ids);
      setAnalysis(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Analyse feilet");
      setView("candidates");
    } finally {
      setAnalyzingLoading(false);
    }
  };

  const handlePreview = async () => {
    if (!selectedGroup || !primaryId) return;
    setPreviewLoading(true);
    setView("preview");

    const ids = selectedGroup.candidates.map((c) => c.template_id);
    try {
      const result = await dedupApi.preview(ids, primaryId);
      setPreview(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Forhåndsvisning feilet");
      setView("analysis");
    } finally {
      setPreviewLoading(false);
    }
  };

  const handleExecute = async () => {
    if (!selectedGroup || !primaryId || !preview) return;
    setMerging(true);

    const ids = selectedGroup.candidates.map((c) => c.template_id);
    try {
      await dedupApi.execute(ids, primaryId, preview.merged_html);
      setMergeComplete(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Sammenslåing feilet");
    } finally {
      setMerging(false);
    }
  };

  const handleBack = () => {
    if (view === "preview") {
      setView("analysis");
      setPreview(null);
    } else if (view === "analysis") {
      setView("candidates");
      setSelectedGroup(null);
      setAnalysis(null);
    }
  };

  const totalTemplates = groups.reduce((sum, g) => sum + g.candidates.length, 0);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="h-6 w-6 animate-spin text-[#BCAB8A]" />
        <span className="ml-3 text-[#272630]/60 font-sans">Leter etter duplikater...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <AlertTriangle className="h-8 w-8 text-red-500 mx-auto mb-3" />
        <p className="text-red-600 mb-4">{error}</p>
        <Button
          variant="outline"
          onClick={() => {
            setError(null);
            loadCandidates();
          }}
        >
          Prøv igjen
        </Button>
      </div>
    );
  }

  // ── Merge complete ──
  if (mergeComplete) {
    return (
      <div className="text-center py-16">
        <CheckCircle2 className="h-12 w-12 text-green-500 mx-auto mb-4" />
        <h3 className="text-xl font-serif font-semibold text-[#272630] mb-2">
          Sammenslåing fullført
        </h3>
        <p className="text-[#272630]/60 font-sans mb-6">
          Primærmalen er oppdatert og {preview?.templates_to_archive.length ?? 0} mal(er)
          er arkivert.
        </p>
        <Button
          onClick={() => {
            setMergeComplete(false);
            setView("candidates");
            setSelectedGroup(null);
            setAnalysis(null);
            setPreview(null);
            loadCandidates();
          }}
        >
          Tilbake til oversikt
        </Button>
      </div>
    );
  }

  // ── Candidate list view ──
  if (view === "candidates") {
    return (
      <div>
        <div className="mb-6">
          <p className="text-[#272630]/60 font-sans">
            Funnet {groups.length} grupper med mulige duplikater ({totalTemplates} maler
            totalt)
          </p>
        </div>

        {groups.length === 0 ? (
          <div className="text-center py-16">
            <CheckCircle2 className="h-10 w-10 text-green-500 mx-auto mb-4" />
            <h3 className="text-lg font-serif font-semibold text-[#272630]">
              Ingen duplikater funnet
            </h3>
            <p className="text-[#272630]/60 font-sans mt-2">
              Alle maler er unike — ingen sammenslåing nødvendig.
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {groups.map((group) => (
              <CandidateGroupCard
                key={group.base_title}
                group={group}
                onAnalyze={() => handleAnalyze(group)}
              />
            ))}
          </div>
        )}
      </div>
    );
  }

  // ── Analysis view ──
  if (view === "analysis" && selectedGroup) {
    return (
      <div>
        <div className="flex items-center gap-3 mb-6">
          <Button variant="ghost" size="sm" onClick={handleBack}>
            <ArrowLeft className="h-4 w-4 mr-1" />
            Tilbake
          </Button>
          <h3 className="text-xl font-serif font-semibold text-[#272630]">
            {selectedGroup.base_title} — Sammenslåingsanalyse
          </h3>
        </div>

        {analyzingLoading ? (
          <div className="flex items-center justify-center py-16">
            <Loader2 className="h-6 w-6 animate-spin text-[#BCAB8A]" />
            <span className="ml-3 text-[#272630]/60 font-sans">Analyserer maler...</span>
          </div>
        ) : analysis ? (
          <div className="space-y-6">
            {/* Templates in group */}
            <Card>
              <CardHeader>
                <CardTitle className="text-base font-sans">
                  Maler i gruppen ({analysis.templates.length})
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {analysis.templates.map((t) => (
                  <div
                    key={t.template_id}
                    className="flex items-center justify-between py-2 px-3 rounded-md bg-[#F5F5F0]"
                  >
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium text-[#272630]">{t.title}</span>
                      {t.property_type && (
                        <Badge variant="outline" className="text-xs">
                          {t.property_type}
                        </Badge>
                      )}
                    </div>
                    <span className="text-xs text-[#272630]/50 font-sans tabular-nums">
                      {(t.similarity_score * 100).toFixed(0)}% likhet
                    </span>
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* Shared vs Divergent sections */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <SectionList
                title="Delte seksjoner"
                icon={<CheckCircle2 className="h-4 w-4 text-green-600" />}
                sections={analysis.shared_sections}
                emptyLabel="Ingen delte seksjoner"
              />
              <SectionList
                title="Avvikende seksjoner"
                icon={<AlertTriangle className="h-4 w-4 text-amber-500" />}
                sections={analysis.divergent_sections}
                emptyLabel="Ingen avvik"
              />
            </div>

            {analysis.unique_sections.length > 0 && (
              <SectionList
                title="Unike seksjoner"
                icon={<Layers className="h-4 w-4 text-sky-500" />}
                sections={analysis.unique_sections}
                emptyLabel=""
              />
            )}

            {/* Complexity + Warnings */}
            <div className="flex items-center gap-4">
              <span className="text-sm text-[#272630]/60 font-sans">Kompleksitet:</span>
              <Badge
                className={`border ${complexityColors[analysis.merge_complexity]}`}
                variant="outline"
              >
                {complexityLabels[analysis.merge_complexity]}
              </Badge>
              {analysis.auto_mergeable && (
                <Badge className="bg-green-50 text-green-700 border-green-200" variant="outline">
                  Automatisk sammenslåbar
                </Badge>
              )}
            </div>

            {analysis.warnings.length > 0 && (
              <div className="bg-amber-50 border border-amber-200 rounded-md p-4">
                <div className="flex items-center gap-2 mb-2">
                  <AlertTriangle className="h-4 w-4 text-amber-600" />
                  <span className="text-sm font-medium text-amber-800">Advarsler</span>
                </div>
                <ul className="list-disc pl-5 space-y-1">
                  {analysis.warnings.map((w, i) => (
                    <li key={i} className="text-sm text-amber-700">
                      {w}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Primary selection + Preview button */}
            <div className="flex items-center gap-4 pt-4 border-t border-[#E5E5E5]">
              <label className="text-sm font-medium text-[#272630]">Velg primærmal:</label>
              <Select value={primaryId} onValueChange={setPrimaryId}>
                <SelectTrigger className="w-[320px]">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {analysis.templates.map((t) => (
                    <SelectItem key={t.template_id} value={t.template_id}>
                      {t.title}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Button onClick={handlePreview} disabled={!primaryId}>
                <Eye className="h-4 w-4 mr-2" />
                Forhåndsvis sammenslåing
              </Button>
            </div>
          </div>
        ) : null}
      </div>
    );
  }

  // ── Preview view ──
  if (view === "preview" && selectedGroup) {
    return (
      <div>
        <div className="flex items-center gap-3 mb-6">
          <Button variant="ghost" size="sm" onClick={handleBack}>
            <ArrowLeft className="h-4 w-4 mr-1" />
            Tilbake
          </Button>
          <h3 className="text-xl font-serif font-semibold text-[#272630]">
            Forhåndsvisning — {selectedGroup.base_title}
          </h3>
        </div>

        {previewLoading ? (
          <div className="flex items-center justify-center py-16">
            <Loader2 className="h-6 w-6 animate-spin text-[#BCAB8A]" />
            <span className="ml-3 text-[#272630]/60 font-sans">
              Genererer sammenslått mal...
            </span>
          </div>
        ) : preview ? (
          <div className="space-y-6">
            {/* Stats */}
            <div className="flex items-center gap-6">
              <div className="flex items-center gap-2">
                <Merge className="h-4 w-4 text-[#BCAB8A]" />
                <span className="text-sm text-[#272630]/70 font-sans">
                  vitec-if betingelser lagt til:{" "}
                  <strong>{preview.vitec_if_conditions_added}</strong>
                </span>
              </div>
              <div className="flex items-center gap-2">
                {preview.validation_passed ? (
                  <CheckCircle2 className="h-4 w-4 text-green-600" />
                ) : (
                  <AlertTriangle className="h-4 w-4 text-amber-500" />
                )}
                <span className="text-sm text-[#272630]/70 font-sans">
                  Validering:{" "}
                  <strong>{preview.validation_passed ? "Bestått" : "Advarsler"}</strong>
                </span>
              </div>
              <div className="text-sm text-[#272630]/70 font-sans">
                Maler som arkiveres:{" "}
                <strong>{preview.templates_to_archive.length}</strong>
              </div>
            </div>

            {preview.warnings.length > 0 && (
              <div className="bg-amber-50 border border-amber-200 rounded-md p-4">
                <div className="flex items-center gap-2 mb-2">
                  <AlertTriangle className="h-4 w-4 text-amber-600" />
                  <span className="text-sm font-medium text-amber-800">Advarsler</span>
                </div>
                <ul className="list-disc pl-5 space-y-1">
                  {preview.warnings.map((w, i) => (
                    <li key={i} className="text-sm text-amber-700">
                      {w}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* HTML Preview */}
            <Card>
              <CardHeader>
                <CardTitle className="text-base font-sans">Sammenslått HTML</CardTitle>
              </CardHeader>
              <CardContent>
                <pre className="bg-[#F5F5F0] rounded-md p-4 text-xs font-mono overflow-x-auto max-h-[500px] overflow-y-auto whitespace-pre-wrap">
                  {preview.merged_html}
                </pre>
              </CardContent>
            </Card>

            {/* Action buttons */}
            <div className="flex items-center justify-between pt-4 border-t border-[#E5E5E5]">
              <Button variant="outline" onClick={handleBack}>
                Avbryt
              </Button>
              <Button onClick={handleExecute} disabled={merging}>
                {merging ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Slår sammen...
                  </>
                ) : (
                  <>
                    <Merge className="h-4 w-4 mr-2" />
                    Utfør sammenslåing
                  </>
                )}
              </Button>
            </div>
          </div>
        ) : null}
      </div>
    );
  }

  return null;
}

// ── Sub-components ──

function CandidateGroupCard({
  group,
  onAnalyze,
}: {
  group: DedupMergeCandidateGroup;
  onAnalyze: () => void;
}) {
  const [expanded, setExpanded] = useState(false);

  return (
    <Card className="group hover:shadow-card-hover hover:-translate-y-0.5 transition-all duration-slow">
      <CardContent className="p-5">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <h4 className="text-lg font-serif font-semibold text-[#272630]">
                {group.base_title}
              </h4>
              <Badge variant="secondary" className="text-xs">
                {group.candidates.length} varianter
              </Badge>
              {group.category && (
                <Badge variant="outline" className="text-xs">
                  {group.category}
                </Badge>
              )}
            </div>

            <button
              onClick={() => setExpanded(!expanded)}
              className="flex items-center gap-1 text-sm text-[#BCAB8A] hover:text-[#272630] transition-colors duration-fast"
            >
              {expanded ? (
                <ChevronUp className="h-3.5 w-3.5" />
              ) : (
                <ChevronDown className="h-3.5 w-3.5" />
              )}
              {expanded ? "Skjul varianter" : "Vis varianter"}
            </button>

            {expanded && (
              <div className="mt-3 space-y-1.5">
                {group.candidates.map((c) => (
                  <div
                    key={c.template_id}
                    className="flex items-center justify-between text-sm py-1.5 px-3 rounded bg-[#F5F5F0]"
                  >
                    <span className="text-[#272630]">{c.title}</span>
                    <span className="text-[#272630]/50 font-sans tabular-nums">
                      {(c.similarity_score * 100).toFixed(0)}% likhet
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="flex flex-col items-end gap-2 ml-4">
            <span className="text-xs text-[#272630]/50 font-sans">
              Estimert reduksjon: {group.estimated_reduction} mal(er)
            </span>
            <Button size="sm" onClick={onAnalyze}>
              <Layers className="h-4 w-4 mr-1.5" />
              Analyser
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function SectionList({
  title,
  icon,
  sections,
  emptyLabel,
}: {
  title: string;
  icon: React.ReactNode;
  sections: { path: string; preview: string }[];
  emptyLabel: string;
}) {
  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-sm font-sans flex items-center gap-2">
          {icon}
          {title} ({sections.length})
        </CardTitle>
      </CardHeader>
      <CardContent>
        {sections.length === 0 ? (
          <p className="text-sm text-[#272630]/50 font-sans">{emptyLabel}</p>
        ) : (
          <ul className="space-y-1.5">
            {sections.map((s, i) => (
              <li
                key={i}
                className="text-xs font-mono text-[#272630]/70 bg-[#F5F5F0] rounded px-2 py-1.5 truncate"
                title={s.preview}
              >
                <span className="text-[#BCAB8A] mr-1.5">{s.path}</span>
                {s.preview.slice(0, 80)}
                {s.preview.length > 80 ? "…" : ""}
              </li>
            ))}
          </ul>
        )}
      </CardContent>
    </Card>
  );
}
