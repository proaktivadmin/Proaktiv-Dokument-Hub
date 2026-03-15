"use client";

import { useState, useCallback, useEffect, useRef } from "react";
import { Header } from "@/components/layout/Header";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Download,
  BarChart3,
  Loader2,
  AlertCircle,
  Mail,
  Trophy,
  Target,
  ChevronRight,
  ChevronDown,
  RefreshCw,
  ArrowUpDown,
  ArrowUp,
  ArrowDown,
} from "lucide-react";
import { Input } from "@/components/ui/input";
import {
  getISOWeek,
  getISOWeekYear,
  startOfISOWeek,
  endOfISOWeek,
  subWeeks,
  format,
} from "date-fns";
import { nb } from "date-fns/locale";
import {
  downloadSalesReport,
  downloadBestPerformers,
  fetchBestPerformers,
  fetchFranchiseReportData,
  getBudgetComparison,
  listReportSubscriptions,
  createReportSubscription,
  deleteReportSubscription,
  testReportSubscription,
  upsertReportBudget,
  fetchSalesReportData,
  type BestPerformersData,
  type BudgetComparisonData,
  type FranchiseDepartment,
  type FranchiseReportData,
  type ReportSubscription,
  type PerformerRow,
  type PerformerProperty,
  type ReportSalesSyncEvent,
  type ReportScopeMetadata,
  type SalesReportData,
  type SalesReportBroker,
  type SalesReportProperty,
} from "@/lib/api/reports";
import { useReportCacheEvents } from "@/hooks/use-report-cache-events";
import { officesApi } from "@/lib/api/offices";
import type { OfficeWithStats } from "@/types/v3";

const MONTHS_NB = [
  "Januar",
  "Februar",
  "Mars",
  "April",
  "Mai",
  "Juni",
  "Juli",
  "August",
  "September",
  "Oktober",
  "November",
  "Desember",
] as const;

function getWeekRange(weeksAgo: number): { from: string; to: string } {
  const now = new Date();
  const weekStart = startOfISOWeek(subWeeks(now, weeksAgo));
  const weekEnd = endOfISOWeek(subWeeks(now, weeksAgo));
  return {
    from: format(weekStart, "yyyy-MM-dd"),
    to: format(weekEnd, "yyyy-MM-dd"),
  };
}

function getMonthRange(year: number, monthIndex: number): { from: string; to: string } {
  const start = new Date(year, monthIndex, 1);
  const end = new Date(year, monthIndex + 1, 0);
  return {
    from: format(start, "yyyy-MM-dd"),
    to: format(end, "yyyy-MM-dd"),
  };
}

/** Format revenue as whole number (no decimals) for sales dashboard. */
function formatRevenue(n: number): string {
  return Math.round(n).toLocaleString("nb-NO", { maximumFractionDigits: 0 });
}

export default function ReportsPage() {
  const [loading, setLoading] = useState(false);
  const [downloadLoading, setDownloadLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [mode, setMode] = useState<"department" | "franchise">("department");
  const [includeVat, setIncludeVat] = useState(false);
  const [year, setYear] = useState<number>(new Date().getFullYear());
  const [departmentId, setDepartmentId] = useState<number>(1120);
  const [fromDate, setFromDate] = useState<string | null>(null);
  const [toDate, setToDate] = useState<string | null>(null);
  const [data, setData] = useState<SalesReportData | null>(null);
  const [franchiseData, setFranchiseData] = useState<FranchiseReportData | null>(null);
  const [offices, setOffices] = useState<OfficeWithStats[]>([]);
  const [expandedBrokers, setExpandedBrokers] = useState<Set<string>>(new Set());
  const [expandedProperties, setExpandedProperties] = useState<Set<string>>(new Set());
  const [expandedDepartments, setExpandedDepartments] = useState<Set<number>>(new Set());
  const [reportSort, setReportSort] = useState<{
    column: "name" | "sale_count" | "total";
    direction: "asc" | "desc";
  } | null>(null);

  const [bestPerformers, setBestPerformers] = useState<BestPerformersData | null>(null);
  const [bestLoading, setBestLoading] = useState(false);
  const [bestDownloadLoading, setBestDownloadLoading] = useState(false);
  const [bestFromDate, setBestFromDate] = useState<string | null>(null);
  const [bestToDate, setBestToDate] = useState<string | null>(null);
  const [bestScope, setBestScope] = useState<"week" | "month">("week");

  const [budgetComparison, setBudgetComparison] = useState<BudgetComparisonData | null>(null);
  const [budgetDraft, setBudgetDraft] = useState<Record<number, string>>({});
  const [budgetSavingMonth, setBudgetSavingMonth] = useState<number | null>(null);
  const [budgetLoading, setBudgetLoading] = useState(false);

  const [subscriptions, setSubscriptions] = useState<ReportSubscription[]>([]);
  const [subLoading, setSubLoading] = useState(false);
  const [subSaving, setSubSaving] = useState(false);
  const [subTestId, setSubTestId] = useState<string | null>(null);
  const [subscriptionName, setSubscriptionName] = useState("Ukentlig best performers");
  const [subscriptionRecipients, setSubscriptionRecipients] = useState("");
  const [subscriptionCadence, setSubscriptionCadence] = useState<"weekly" | "monthly">("weekly");
  const [subscriptionReportType, setSubscriptionReportType] = useState<"best_performers" | "franchise_summary">(
    "best_performers"
  );
  const [liveUpdatesEnabled, setLiveUpdatesEnabled] = useState(true);
  const [pendingSyncEvents, setPendingSyncEvents] = useState(0);
  const [lastSyncEventAt, setLastSyncEventAt] = useState<Date | null>(null);
  const suppressLiveEventsUntilRef = useRef<number>(0);

  const loadOffices = useCallback(async () => {
    try {
      const res = await officesApi.list({ is_active: true });
      setOffices(
        res.items.filter(
          (o) =>
            o.vitec_department_id != null &&
            !/oppgjør|aktiv oppgjør|pacta eiendom as\s*-\s*oppgjør/i.test(o.name)
        )
      );
    } catch {
      setOffices([]);
    }
  }, []);

  const loadReport = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      if (mode === "department") {
        const reportData = await fetchSalesReportData({
          year,
          department_id: departmentId,
          from_date: fromDate ?? undefined,
          to_date: toDate ?? undefined,
          include_vat: includeVat,
        });
        setData(reportData);
        setFranchiseData(null);
        setExpandedBrokers(new Set());
        setExpandedProperties(new Set());
      } else {
        const reportData = await fetchFranchiseReportData({
          year,
          from_date: fromDate ?? undefined,
          to_date: toDate ?? undefined,
          include_vat: includeVat,
        });
        setFranchiseData(reportData);
        setData(null);
        setExpandedDepartments(new Set());
      }
      setPendingSyncEvents(0);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Kunne ikke laste rapporten.");
      setData(null);
      setFranchiseData(null);
    } finally {
      setLoading(false);
    }
  }, [mode, year, departmentId, fromDate, toDate, includeVat]);

  const onCacheEvent = useCallback((event: ReportSalesSyncEvent) => {
    const now = Date.now();
    if (now < suppressLiveEventsUntilRef.current) return;
    const changedRows = Number(event.estates_upserted || 0) + Number(event.transactions_upserted || 0);
    if (changedRows <= 0) return;
    setPendingSyncEvents((prev) => Math.min(prev + 1, 99));
    setLastSyncEventAt(new Date());
  }, []);

  const { isConnected: liveUpdatesConnected } = useReportCacheEvents({
    enabled: liveUpdatesEnabled,
    departmentId: mode === "department" ? departmentId : undefined,
    onEvent: onCacheEvent,
  });

  const handleDownload = async () => {
    setDownloadLoading(true);
    setError(null);
    try {
      if (mode !== "department") return;
      const blob = await downloadSalesReport({
        year,
        department_id: departmentId,
        from_date: fromDate ?? undefined,
        to_date: toDate ?? undefined,
        include_vat: includeVat,
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `formidlingsrapport_${departmentId}_${year}.xlsx`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      // Delay revoke so browser can start the download before blob is released
      setTimeout(() => URL.revokeObjectURL(url), 500);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Kunne ikke laste ned rapporten.");
    } finally {
      setDownloadLoading(false);
    }
  };

  const toggleBroker = (brokerId: string) => {
    setExpandedBrokers((prev) => {
      const next = new Set(prev);
      if (next.has(brokerId)) next.delete(brokerId);
      else next.add(brokerId);
      return next;
    });
  };

  const toggleProperty = (key: string) => {
    setExpandedProperties((prev) => {
      const next = new Set(prev);
      if (next.has(key)) next.delete(key);
      else next.add(key);
      return next;
    });
  };

  const toggleDepartment = (departmentIdToToggle: number) => {
    setExpandedDepartments((prev) => {
      const next = new Set(prev);
      if (next.has(departmentIdToToggle)) next.delete(departmentIdToToggle);
      else next.add(departmentIdToToggle);
      return next;
    });
  };

  const loadBestPerformers = useCallback(async () => {
    setBestLoading(true);
    setError(null);
    const from = bestFromDate ?? fromDate;
    const to = bestToDate ?? toDate;
    try {
      const result = await fetchBestPerformers({
        year,
        from_date: from ?? undefined,
        to_date: to ?? undefined,
        include_vat: includeVat,
        top_n: 5,
      });
      setBestPerformers(result);
      if (from) setBestFromDate(from);
      if (to) setBestToDate(to);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Kunne ikke laste best performers.");
    } finally {
      setBestLoading(false);
    }
  }, [year, bestFromDate, bestToDate, fromDate, toDate, includeVat]);

  const handleBestPerformersDownload = async () => {
    setBestDownloadLoading(true);
    setError(null);
    const from = bestFromDate ?? fromDate;
    const to = bestToDate ?? toDate;
    try {
      const blob = await downloadBestPerformers({
        year,
        from_date: from ?? undefined,
        to_date: to ?? undefined,
        include_vat: includeVat,
        top_n: 5,
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "best_performers.xlsx";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      setTimeout(() => URL.revokeObjectURL(url), 500);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Kunne ikke laste ned best performers.");
    } finally {
      setBestDownloadLoading(false);
    }
  };

  const loadBudget = useCallback(async () => {
    setBudgetLoading(true);
    setError(null);
    try {
      const comparison = await getBudgetComparison({
        department_id: departmentId,
        year,
        include_vat: includeVat,
      });
      setBudgetComparison(comparison);
      const nextDraft: Record<number, string> = {};
      comparison.months.forEach((m) => {
        nextDraft[m.month] = String(m.budget || 0);
      });
      setBudgetDraft(nextDraft);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Kunne ikke laste budsjett.");
      setBudgetComparison(null);
    } finally {
      setBudgetLoading(false);
    }
  }, [departmentId, year, includeVat]);

  const saveBudgetMonth = async (month: number) => {
    const raw = budgetDraft[month] ?? "0";
    const value = Number(raw.replace(",", "."));
    if (Number.isNaN(value) || value < 0) return;
    setBudgetSavingMonth(month);
    try {
      await upsertReportBudget({
        department_id: departmentId,
        year,
        month,
        budget_amount: value,
      });
      await loadBudget();
    } finally {
      setBudgetSavingMonth(null);
    }
  };

  const loadSubscriptions = useCallback(async () => {
    setSubLoading(true);
    try {
      const rows = await listReportSubscriptions();
      setSubscriptions(rows);
    } finally {
      setSubLoading(false);
    }
  }, []);

  const createSubscription = async () => {
    const recipients = subscriptionRecipients
      .split(/[;,]/)
      .map((r) => r.trim())
      .filter(Boolean);
    if (recipients.length === 0) return;
    setSubSaving(true);
    try {
      await createReportSubscription({
        name: subscriptionName,
        cadence: subscriptionCadence,
        report_type: subscriptionReportType,
        recipients,
        department_ids: [departmentId],
        include_vat: includeVat,
        day_of_week: 5,
        day_of_month: 1,
        send_hour: 8,
        timezone: "Europe/Oslo",
        is_active: true,
      });
      setSubscriptionRecipients("");
      await loadSubscriptions();
    } finally {
      setSubSaving(false);
    }
  };

  const runTestSend = async (id: string) => {
    setSubTestId(id);
    try {
      await testReportSubscription(id);
    } finally {
      setSubTestId(null);
    }
  };

  const removeSubscription = async (id: string) => {
    await deleteReportSubscription(id);
    await loadSubscriptions();
  };

  const refreshAllFromLive = useCallback(async () => {
    suppressLiveEventsUntilRef.current = Date.now() + 8000;
    await Promise.all([
      loadReport(),
      loadBestPerformers(),
      loadSubscriptions(),
      mode === "department" ? loadBudget() : Promise.resolve(),
    ]);
    setPendingSyncEvents(0);
  }, [loadBestPerformers, loadBudget, loadReport, loadSubscriptions, mode]);

  useEffect(() => {
    loadOffices();
  }, [loadOffices]);
  useEffect(() => {
    loadSubscriptions();
  }, [loadSubscriptions]);

  const sumLabel = includeVat ? "Sum (inkl. mva.)" : "Sum (eksl. mva.)";

  return (
    <div className="min-h-screen bg-background">
      <Header />

      <main className="container mx-auto px-6 py-8">
        <h1 className="text-2xl font-serif font-bold text-foreground mb-2">Rapporter</h1>
        <p className="text-muted-foreground mb-8">
          Inspiser og last ned Formidlingsrapport. Velg omfang og klikk Last inn for å vise data.
        </p>

        {/* Scope filters */}
        <Card className="mb-8 border-border shadow-card">
          <CardHeader>
            <div className="flex items-center gap-3">
              <div className="p-3 rounded-lg bg-secondary">
                <BarChart3 className="h-6 w-6 text-foreground" />
              </div>
              <div>
                <CardTitle className="font-serif">Formidlingsrapport</CardTitle>
                <CardDescription>
                  Vederlag og andre inntekter for meglere som har solgt eiendom
                </CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="space-y-2">
                <Label>År</Label>
                <Select
                  value={String(year)}
                  onValueChange={(v) => setYear(parseInt(v, 10))}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {[2026, 2025, 2024, 2023, 2022].map((y) => (
                      <SelectItem key={y} value={String(y)}>
                        {y}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>Visning</Label>
                <Select
                  value={mode}
                  onValueChange={(v) => setMode(v as "department" | "franchise")}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="department">Enkelt avdeling</SelectItem>
                    <SelectItem value="franchise">Hele franchisen</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>Fra dato</Label>
                <Input
                  type="date"
                  value={fromDate ?? ""}
                  onChange={(e) => setFromDate(e.target.value || null)}
                  placeholder="Hele året"
                />
              </div>
              <div className="space-y-2">
                <Label>Til dato</Label>
                <Input
                  type="date"
                  value={toDate ?? ""}
                  onChange={(e) => setToDate(e.target.value || null)}
                  placeholder="I dag"
                />
              </div>
              <div className="space-y-2">
                <Label>Avdeling</Label>
                <Select
                  value={String(departmentId)}
                  onValueChange={(v) => setDepartmentId(parseInt(v, 10))}
                  disabled={mode === "franchise"}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Velg avdeling" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="1120">Proaktiv Eiendomsmegling AS (1120)</SelectItem>
                    {offices
                      .filter((o) => o.vitec_department_id && o.vitec_department_id !== 1120)
                      .map((o) => (
                        <SelectItem
                          key={o.id}
                          value={String(o.vitec_department_id!)}
                        >
                          {o.name} ({o.vitec_department_id})
                        </SelectItem>
                      ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="flex flex-wrap items-center gap-4">
              <div className="flex items-center gap-2">
                <span className="text-sm text-muted-foreground">Måned:</span>
                <Select
                  value={(() => {
                    if (!fromDate || !toDate) return "all";
                    const from = new Date(fromDate + "T12:00:00");
                    const monthStart = new Date(year, from.getMonth(), 1);
                    const monthEnd = new Date(year, from.getMonth() + 1, 0);
                    if (
                      format(monthStart, "yyyy-MM-dd") === fromDate &&
                      format(monthEnd, "yyyy-MM-dd") === toDate
                    ) {
                      return `${year}-${String(from.getMonth() + 1).padStart(2, "0")}`;
                    }
                    return "all";
                  })()}
                  onValueChange={(v) => {
                    if (v === "all") {
                      setFromDate(null);
                      setToDate(null);
                    } else {
                      const monthIndex = parseInt(v.split("-")[1], 10) - 1;
                      const { from, to } = getMonthRange(year, monthIndex);
                      setFromDate(from);
                      setToDate(to);
                    }
                  }}
                >
                  <SelectTrigger className="w-[140px]">
                    <SelectValue placeholder="Velg måned" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Hele året</SelectItem>
                    {MONTHS_NB.map((name, i) => (
                      <SelectItem
                        key={name}
                        value={`${year}-${String(i + 1).padStart(2, "0")}`}
                      >
                        {name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-sm text-muted-foreground">Uke:</span>
                <Select
                  value={(() => {
                    if (!fromDate || !toDate) return "none";
                    for (let n = 1; n <= 7; n++) {
                      const { from, to } = getWeekRange(n - 1);
                      if (from === fromDate && to === toDate) return String(n);
                    }
                    return "none";
                  })()}
                  onValueChange={(v) => {
                    if (v === "none") return;
                    const weeksAgo = parseInt(v, 10) - 1;
                    const { from, to } = getWeekRange(weeksAgo);
                    setFromDate(from);
                    setToDate(to);
                  }}
                >
                  <SelectTrigger className="w-[180px]">
                    <SelectValue placeholder="Velg uke" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="none">—</SelectItem>
                    {[1, 2, 3, 4, 5, 6, 7].map((n) => {
                      const { from, to } = getWeekRange(n - 1);
                      const weekNum =
                        n === 1
                          ? getISOWeek(new Date())
                          : getISOWeek(subWeeks(new Date(), n - 1));
                      return (
                        <SelectItem key={n} value={String(n)}>
                          Uke {weekNum} ({format(new Date(from), "d. MMM", { locale: nb })} –{" "}
                          {format(new Date(to), "d. MMM", { locale: nb })})
                        </SelectItem>
                      );
                    })}
                  </SelectContent>
                </Select>
              </div>
              <div className="text-sm text-muted-foreground border-l border-border pl-4">
                Nåværende uke: <strong>Uke {getISOWeek(new Date())}</strong> (
                {getISOWeekYear(new Date())})
              </div>
              <div className="flex items-center space-x-2 ml-auto">
                <Checkbox
                  id="include-vat"
                  checked={includeVat}
                  onCheckedChange={(checked) => setIncludeVat(checked === true)}
                />
                <Label htmlFor="include-vat" className="cursor-pointer">
                  Inkluder mva i beløp
                </Label>
              </div>
            </div>
            <div className="flex gap-2">
              <Button
                onClick={loadReport}
                disabled={loading}
                className="bg-primary text-primary-foreground hover:bg-primary/90"
              >
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Laster inn...
                  </>
                ) : (
                  <>
                    <RefreshCw className="mr-2 h-4 w-4" />
                    Last inn rapport
                  </>
                )}
              </Button>
              <Button
                variant="outline"
                onClick={handleDownload}
                disabled={downloadLoading || !data || mode !== "department"}
              >
                {downloadLoading ? (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                  <Download className="mr-2 h-4 w-4" />
                )}
                Last ned Excel
              </Button>
            </div>
            <div className="rounded-md border border-border bg-muted/50 p-3 flex flex-wrap items-center gap-3">
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="live-updates"
                  checked={liveUpdatesEnabled}
                  onCheckedChange={(checked) => setLiveUpdatesEnabled(checked === true)}
                />
                <Label htmlFor="live-updates" className="cursor-pointer">
                  Live dataoppdateringer
                </Label>
              </div>
              <span className="text-xs text-muted-foreground">
                Status: {liveUpdatesEnabled ? (liveUpdatesConnected ? "Tilkoblet" : "Kobler til...") : "Av"}
              </span>
              <span className="text-xs text-muted-foreground">
                Nye data i Vitec: <strong>{pendingSyncEvents}</strong>
                {lastSyncEventAt ? ` · Sist oppdatert: ${lastSyncEventAt.toLocaleTimeString("nb-NO")}` : ""}
              </span>
              <Button
                variant="outline"
                size="sm"
                onClick={refreshAllFromLive}
                disabled={loading || bestLoading || budgetLoading || subLoading}
                className="ml-auto"
              >
                Oppdater fra live data
              </Button>
            </div>
            {error && (
              <div className="p-3 bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-800 rounded-lg flex items-center gap-2 text-red-700 dark:text-red-300">
                <AlertCircle className="h-4 w-4 shrink-0" />
                <span className="text-sm">{error}</span>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Visual dashboard */}
        {data && mode === "department" && (() => {
          const sortedBrokers = [...data.brokers];
          if (reportSort) {
            sortedBrokers.sort((a, b) => {
              let cmp = 0;
              if (reportSort.column === "name") {
                cmp = (a.name ?? "").localeCompare(b.name ?? "", "nb");
              } else if (reportSort.column === "sale_count") {
                cmp = a.sale_count - b.sale_count;
              } else {
                cmp = a.total - b.total;
              }
              return reportSort.direction === "asc" ? cmp : -cmp;
            });
          }
          return (
          <Card className="border border-border shadow-card">
            <CardHeader>
              <div className="flex items-center gap-3">
                <CardTitle className="font-serif">
                  Periode: {data.from_date_display} – {data.to_date_display}
                </CardTitle>
                <DataConfidenceBadge scope={data.scope} />
              </div>
              <CardDescription>
                {data.total_sales} salg totalt · {sumLabel}: {formatRevenue(data.total_revenue)} kr
              </CardDescription>
              <ScopePanel scope={data.scope} />
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-border">
                      <th className="text-left py-3 font-semibold text-foreground w-8" />
                      <th className="text-left py-3 font-semibold text-foreground pl-2 min-w-[10rem]">
                        <SortableHeader
                          label="Megler"
                          column="name"
                          currentSort={reportSort}
                          onSort={(col, dir) => setReportSort({ column: col, direction: dir })}
                        />
                      </th>
                      <th className="text-right py-3 font-semibold text-foreground pr-4 min-w-[5.5rem]">
                        <SortableHeader
                          label="Antall salg"
                          column="sale_count"
                          currentSort={reportSort}
                          onSort={(col, dir) => setReportSort({ column: col, direction: dir })}
                          align="right"
                        />
                      </th>
                      <th className="text-left py-3 font-semibold text-foreground pl-4 min-w-[6rem]">Eiendomstype</th>
                      <th className="text-left py-3 font-semibold text-foreground pl-4 min-w-[6rem]">Oppdragstype</th>
                      <th className="text-right py-3 font-semibold text-foreground pl-4 min-w-[6rem]">
                        <SortableHeader
                          label={`${sumLabel} (kr)`}
                          column="total"
                          currentSort={reportSort}
                          onSort={(col, dir) => setReportSort({ column: col, direction: dir })}
                          align="right"
                        />
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {sortedBrokers.map((broker) => (
                      <BrokerRow
                        key={broker.broker_id}
                        broker={broker}
                        expanded={expandedBrokers.has(broker.broker_id)}
                        expandedProperties={expandedProperties}
                        onToggleBroker={() => toggleBroker(broker.broker_id)}
                        onToggleProperty={toggleProperty}
                      />
                    ))}
                    <tr className="border-t-2 border-primary font-bold bg-secondary/30">
                      <td className="py-3" />
                      <td className="py-3 pl-2">Sum</td>
                      <td className="py-3 text-right pr-4">{data.total_sales}</td>
                      <td className="py-3 pl-4" />
                      <td className="py-3 pl-4" />
                      <td className="py-3 text-right pl-4">
                        {formatRevenue(data.total_revenue)}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
          );
        })()}

        {franchiseData && mode === "franchise" && (
          <Card className="border border-border shadow-card mb-8">
            <CardHeader>
              <CardTitle className="font-serif">Franchise sammendrag</CardTitle>
              <CardDescription>
                {franchiseData.summary.department_count} avdelinger · {franchiseData.summary.total_sales} salg ·{" "}
                {formatRevenue(franchiseData.summary.total_revenue)} kr
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-2">
              {franchiseData.departments.map((dep) => (
                <DepartmentRow
                  key={dep.department_id}
                  department={dep}
                  expanded={expandedDepartments.has(dep.department_id)}
                  onToggle={() => toggleDepartment(dep.department_id)}
                />
              ))}
            </CardContent>
          </Card>
        )}

        <Card className="border border-border shadow-card mb-8">
          <CardHeader>
            <div className="flex items-center gap-2">
              <Trophy className="h-5 w-5 text-accent" />
              <CardTitle className="font-serif">Best performers</CardTitle>
            </div>
            <CardDescription>Ukentlig/månedlig toppliste for meglere og avdelinger.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex flex-wrap items-center gap-4">
              <div className="flex items-center gap-2">
                <span className="text-sm text-muted-foreground">Periode:</span>
                <Select
                  value={bestScope}
                  onValueChange={(v: "week" | "month") => {
                    setBestScope(v);
                    if (v === "week") {
                      const { from, to } = getWeekRange(0);
                      setBestFromDate(from);
                      setBestToDate(to);
                    } else {
                      const now = new Date();
                      setBestFromDate(format(new Date(now.getFullYear(), now.getMonth(), 1), "yyyy-MM-dd"));
                      setBestToDate(format(new Date(now.getFullYear(), now.getMonth() + 1, 0), "yyyy-MM-dd"));
                    }
                  }}
                >
                  <SelectTrigger className="w-[120px]">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="week">Uke</SelectItem>
                    <SelectItem value="month">Måned</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              {bestScope === "week" && (
                <Select
                  value={
                    bestFromDate && bestToDate
                      ? (() => {
                          for (let n = 0; n < 8; n++) {
                            const { from, to } = getWeekRange(n);
                            if (from === bestFromDate && to === bestToDate) return String(n);
                          }
                          return "custom";
                        })()
                      : "0"
                  }
                  onValueChange={(v) => {
                    const n = parseInt(v, 10);
                    if (n >= 0 && n < 8) {
                      const { from, to } = getWeekRange(n);
                      setBestFromDate(from);
                      setBestToDate(to);
                    }
                  }}
                >
                  <SelectTrigger className="w-[200px]">
                    <SelectValue placeholder="Velg uke" />
                  </SelectTrigger>
                  <SelectContent>
                    {[0, 1, 2, 3, 4, 5, 6, 7].map((n) => {
                      const { from, to } = getWeekRange(n);
                      const weekNum = n === 0 ? getISOWeek(new Date()) : getISOWeek(subWeeks(new Date(), n));
                      return (
                        <SelectItem key={n} value={String(n)}>
                          {n === 0 ? "Denne uken" : `Uke ${weekNum}`} ({format(new Date(from), "d. MMM", { locale: nb })} – {format(new Date(to), "d. MMM", { locale: nb })})
                        </SelectItem>
                      );
                    })}
                  </SelectContent>
                </Select>
              )}
              {bestScope === "month" && (
                <Select
                  value={
                    bestFromDate
                      ? `${new Date(bestFromDate).getFullYear()}-${String(new Date(bestFromDate).getMonth() + 1).padStart(2, "0")}`
                      : ""
                  }
                  onValueChange={(v) => {
                    const [y, m] = v.split("-").map(Number);
                    const start = new Date(y, m - 1, 1);
                    const end = new Date(y, m, 0);
                    setBestFromDate(format(start, "yyyy-MM-dd"));
                    setBestToDate(format(end, "yyyy-MM-dd"));
                  }}
                >
                  <SelectTrigger className="w-[140px]">
                    <SelectValue placeholder="Velg måned" />
                  </SelectTrigger>
                  <SelectContent>
                    {MONTHS_NB.map((name, i) => (
                      <SelectItem
                        key={name}
                        value={`${year}-${String(i + 1).padStart(2, "0")}`}
                      >
                        {name} {year}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              )}
              <span className="text-sm text-muted-foreground">
                Omfang: {mode === "department" ? offices.find((o) => o.vitec_department_id === departmentId)?.name ?? `Avd. ${departmentId}` : "Hele franchisen"}
              </span>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" onClick={loadBestPerformers} disabled={bestLoading}>
                {bestLoading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <RefreshCw className="h-4 w-4 mr-2" />}
                Last inn best performers
              </Button>
              <Button variant="outline" onClick={handleBestPerformersDownload} disabled={bestDownloadLoading}>
                {bestDownloadLoading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Download className="h-4 w-4 mr-2" />}
                Last ned ukesrapport
              </Button>
            </div>
            {bestPerformers && (
              <>
                <div className="text-sm text-muted-foreground rounded-md bg-muted/50 px-3 py-2">
                  Viser: <strong>{bestPerformers.from_date_display} – {bestPerformers.to_date_display}</strong>
                  {includeVat ? " (inkl. mva.)" : " (eksl. mva.)"}
                </div>
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <LeaderboardCard
                  title="Eiendomsmegler"
                  rows={bestPerformers.eiendomsmegler}
                  nameKey="name"
                />
                <LeaderboardCard
                  title="Eiendomsmeglerfullmektig"
                  rows={bestPerformers.eiendomsmeglerfullmektig}
                  nameKey="name"
                />
                <LeaderboardCard
                  title="Avdeling"
                  rows={bestPerformers.departments}
                  nameKey="department_name"
                  isDepartmentMode
                />
                </div>
              </>
            )}
          </CardContent>
        </Card>

        <Card className="border border-border shadow-card mb-8">
          <CardHeader>
            <div className="flex items-center gap-2">
              <Target className="h-5 w-5 text-accent" />
              <CardTitle className="font-serif">Budsjett vs faktisk</CardTitle>
            </div>
            <CardDescription>Månedlige budsjetter med YTD-status og prognose.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Button variant="outline" onClick={loadBudget} disabled={budgetLoading}>
              {budgetLoading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <RefreshCw className="h-4 w-4 mr-2" />}
              Last inn budsjett
            </Button>
            {budgetComparison && (
              <>
                <div className="text-sm text-muted-foreground">
                  Status: <strong>{budgetComparison.status}</strong> · YTD:{" "}
                  {formatRevenue(budgetComparison.ytd_actual)} /{" "}
                  {formatRevenue(budgetComparison.ytd_budget)} kr
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-border">
                        <th className="text-left py-2">Måned</th>
                        <th className="text-right py-2">Faktisk</th>
                        <th className="text-right py-2">Budsjett</th>
                        <th className="text-right py-2">Avvik</th>
                        <th className="text-right py-2">% oppnådd</th>
                        <th className="text-right py-2">Lagre</th>
                      </tr>
                    </thead>
                    <tbody>
                      {budgetComparison.months.map((row) => (
                        <tr key={row.month} className="border-b border-border/50">
                          <td className="py-2">{MONTHS_NB[row.month - 1]}</td>
                          <td className="py-2 text-right">{formatRevenue(row.actual)}</td>
                          <td className="py-2 text-right">
                            <Input
                              value={budgetDraft[row.month] ?? ""}
                              onChange={(e) =>
                                setBudgetDraft((prev) => ({ ...prev, [row.month]: e.target.value }))
                              }
                              className="w-28 ml-auto"
                            />
                          </td>
                          <td className="py-2 text-right">{formatRevenue(row.variance)}</td>
                          <td className="py-2 text-right">{row.achieved_percent.toFixed(1)}%</td>
                          <td className="py-2 text-right">
                            <Button
                              variant="outline"
                              size="sm"
                              disabled={budgetSavingMonth === row.month}
                              onClick={() => saveBudgetMonth(row.month)}
                            >
                              {budgetSavingMonth === row.month ? (
                                <Loader2 className="h-4 w-4 animate-spin" />
                              ) : (
                                "Lagre"
                              )}
                            </Button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </>
            )}
          </CardContent>
        </Card>

        <Card className="border border-border shadow-card">
          <CardHeader>
            <div className="flex items-center gap-2">
              <Mail className="h-5 w-5 text-accent" />
              <CardTitle className="font-serif">Abonnementer</CardTitle>
            </div>
            <CardDescription>Planlagt e-postlevering av rapporter.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
              <Input value={subscriptionName} onChange={(e) => setSubscriptionName(e.target.value)} placeholder="Navn" />
              <Input
                value={subscriptionRecipients}
                onChange={(e) => setSubscriptionRecipients(e.target.value)}
                placeholder="mottaker@proaktiv.no; ... "
              />
              <Select value={subscriptionCadence} onValueChange={(v) => setSubscriptionCadence(v as "weekly" | "monthly")}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="weekly">Ukentlig</SelectItem>
                  <SelectItem value="monthly">Månedlig</SelectItem>
                </SelectContent>
              </Select>
              <Select
                value={subscriptionReportType}
                onValueChange={(v) => setSubscriptionReportType(v as "best_performers" | "franchise_summary")}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="best_performers">Best performers</SelectItem>
                  <SelectItem value="franchise_summary">Franchise sammendrag</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="flex gap-2">
              <Button onClick={createSubscription} disabled={subSaving}>
                {subSaving ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
                Opprett abonnement
              </Button>
              <Button variant="outline" onClick={loadSubscriptions} disabled={subLoading}>
                Oppdater liste
              </Button>
            </div>
            <div className="space-y-2">
              {subscriptions.map((sub) => (
                <div
                  key={sub.id}
                  className="flex items-center justify-between rounded-md border border-border p-3"
                >
                  <div className="text-sm">
                    <div className="font-medium">{sub.name}</div>
                    <div className="text-muted-foreground">
                      {sub.report_type} · {sub.cadence} · Neste: {sub.next_run_at ?? "ikke satt"}
                    </div>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => runTestSend(sub.id)}
                    disabled={subTestId === sub.id}
                  >
                    {subTestId === sub.id ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
                    Test send
                  </Button>
                  <Button variant="outline" size="sm" onClick={() => removeSubscription(sub.id)}>
                    Fjern
                  </Button>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {!data && !franchiseData && !loading && !error && (
          <p className="text-muted-foreground text-center py-12">
            Velg omfang og klikk &quot;Last inn rapport&quot; for å vise data.
          </p>
        )}
      </main>
    </div>
  );
}

function SortableHeader({
  label,
  column,
  currentSort,
  onSort,
  align = "left",
}: {
  label: string;
  column: "name" | "sale_count" | "total";
  currentSort: { column: string; direction: "asc" | "desc" } | null;
  onSort: (column: "name" | "sale_count" | "total", direction: "asc" | "desc") => void;
  align?: "left" | "right";
}) {
  const isActive = currentSort?.column === column;
  const handleClick = () => {
    if (isActive && currentSort?.direction === "asc") {
      onSort(column, "desc");
    } else {
      onSort(column, "asc");
    }
  };
  return (
    <button
      type="button"
      onClick={handleClick}
      className={`inline-flex items-center gap-1 hover:text-foreground transition-colors w-full ${align === "right" ? "justify-end" : "justify-start"}`}
    >
      <span>{label}</span>
      {isActive ? (
        currentSort?.direction === "asc" ? (
          <ArrowUp className="h-3.5 w-3.5 text-accent" />
        ) : (
          <ArrowDown className="h-3.5 w-3.5 text-accent" />
        )
      ) : (
        <ArrowUpDown className="h-3.5 w-3.5 text-muted-foreground opacity-60" />
      )}
    </button>
  );
}

function DepartmentRow({
  department,
  expanded,
  onToggle,
}: {
  department: FranchiseDepartment;
  expanded: boolean;
  onToggle: () => void;
}) {
  return (
    <div className="border border-border rounded-md">
      <button
        className="w-full flex items-center justify-between px-3 py-2 hover:bg-muted"
        onClick={onToggle}
      >
        <span className="font-medium">
          {department.department_name} · {department.total_sales} salg
        </span>
        <span className="text-sm text-muted-foreground">
          {formatRevenue(department.total_revenue)} kr ({department.revenue_share_percent}%)
        </span>
      </button>
      {expanded && (
        <div className="px-3 pb-3">
          {department.brokers.map((b) => (
            <div key={b.broker_id} className="flex justify-between text-sm py-1 border-b last:border-b-0">
              <span>{b.name}</span>
              <span>
                {b.sale_count} salg · {formatRevenue(b.total)} kr
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function LeaderboardCard({
  title,
  rows,
  nameKey,
  isDepartmentMode = false,
}: {
  title: string;
  rows: PerformerRow[];
  nameKey: "name" | "department_name";
  includeVat?: boolean;
  isDepartmentMode?: boolean;
}) {
  const [expandedRows, setExpandedRows] = useState<Set<string>>(new Set());
  const [expandedBrokers, setExpandedBrokers] = useState<Set<string>>(new Set());
  const [expandedProperties, setExpandedProperties] = useState<Set<string>>(new Set());

  const toggleRow = (key: string) => {
    setExpandedRows((prev) => {
      const next = new Set(prev);
      if (next.has(key)) next.delete(key);
      else next.add(key);
      return next;
    });
  };
  const toggleBroker = (key: string) => {
    setExpandedBrokers((prev) => {
      const next = new Set(prev);
      if (next.has(key)) next.delete(key);
      else next.add(key);
      return next;
    });
  };
  const toggleProperty = (key: string) => {
    setExpandedProperties((prev) => {
      const next = new Set(prev);
      if (next.has(key)) next.delete(key);
      else next.add(key);
      return next;
    });
  };

  const getRowKey = (row: PerformerRow, i: number) =>
    isDepartmentMode ? `dept-${row.department_id ?? i}` : `broker-${row.broker_id ?? row.name ?? i}`;
  const hasExpandableContent = (row: PerformerRow) =>
    isDepartmentMode ? (row.brokers?.length ?? 0) > 0 : (row.properties?.length ?? 0) > 0;

  return (
    <Card className="border border-border min-w-0 min-h-[18rem]">
      <CardHeader className="pb-2">
        <CardTitle className="text-base">{title}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-0">
        {rows.length === 0 ? (
          <p className="text-sm text-muted-foreground py-2">Ingen data</p>
        ) : (
          <div className="space-y-0.5">
            {rows.map((row, i) => {
              const rowKey = getRowKey(row, i);
              const expanded = expandedRows.has(rowKey);
              const hasContent = hasExpandableContent(row);

              return (
                <div key={rowKey} className="rounded-md border border-border/50 overflow-hidden">
                  <button
                    type="button"
                    className="w-full flex items-center justify-between gap-2 px-3 py-2.5 text-left hover:bg-muted/50 transition-colors"
                    onClick={() => hasContent && toggleRow(rowKey)}
                  >
                    <span className="flex items-center gap-2 min-w-0">
                      {hasContent && (
                        <span className="shrink-0 text-muted-foreground">
                          {expanded ? (
                            <ChevronDown className="h-4 w-4" />
                          ) : (
                            <ChevronRight className="h-4 w-4" />
                          )}
                        </span>
                      )}
                      <span className="font-medium truncate">
                        {i + 1}. {String(row[nameKey] ?? "—")}
                      </span>
                    </span>
                    <span className="shrink-0 text-sm text-muted-foreground">
                      {formatRevenue(Number(row.total_revenue ?? row.total ?? 0))} kr
                    </span>
                  </button>

                  {expanded && hasContent && (
                    <div className="border-t border-border/50 bg-muted/30 px-3 py-2 space-y-2">
                      {isDepartmentMode && row.brokers ? (
                        row.brokers.map((broker) => {
                          const brokerKey = `${rowKey}-${broker.broker_id ?? broker.name}`;
                          const brokerExpanded = expandedBrokers.has(brokerKey);
                          const brokerHasProps = (broker.properties?.length ?? 0) > 0;

                          return (
                            <div key={brokerKey} className="rounded border border-border/40 bg-card">
                              <button
                                type="button"
                                className="w-full flex items-center justify-between px-3 py-2 text-sm hover:bg-muted/30"
                                onClick={() => brokerHasProps && toggleBroker(brokerKey)}
                              >
                                <span className="flex items-center gap-2">
                                  {brokerHasProps && (
                                    <span className="text-muted-foreground">
                                      {brokerExpanded ? (
                                        <ChevronDown className="h-3.5 w-3.5" />
                                      ) : (
                                        <ChevronRight className="h-3.5 w-3.5" />
                                      )}
                                    </span>
                                  )}
                                  <span>{broker.name}</span>
                                </span>
                                <span className="text-muted-foreground">
                                  {formatRevenue(Number(broker.total ?? broker.total_revenue ?? 0))} kr
                                </span>
                              </button>
                              {brokerExpanded && broker.properties && (
                                <PerformerPropertiesList
                                  properties={broker.properties}
                                  expandedProperties={expandedProperties}
                                  onToggleProperty={toggleProperty}
                                  parentKey={brokerKey}
                                />
                              )}
                            </div>
                          );
                        })
                      ) : (
                        row.properties && (
                          <PerformerPropertiesList
                            properties={row.properties}
                            expandedProperties={expandedProperties}
                            onToggleProperty={toggleProperty}
                            parentKey={rowKey}
                          />
                        )
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function PerformerPropertiesList({
  properties,
  expandedProperties,
  onToggleProperty,
  parentKey,
}: {
  properties: PerformerProperty[];
  expandedProperties: Set<string>;
  onToggleProperty: (key: string) => void;
  parentKey: string;
}) {
  return (
    <div className="space-y-1 pl-2 border-l-2 border-border/40">
      {properties.map((prop) => {
        const propKey = `${parentKey}-${prop.estate_id}`;
        const expanded = expandedProperties.has(propKey);
        const hasTxns = (prop.transactions?.length ?? 0) > 0;

        return (
          <div key={propKey} className="text-sm">
            <button
              type="button"
              className="w-full flex items-center justify-between px-2 py-1.5 hover:bg-muted/30 rounded text-left"
              onClick={() => hasTxns && onToggleProperty(propKey)}
            >
              <span className="flex items-center gap-2 min-w-0">
                {hasTxns && (
                  <span className="shrink-0 text-muted-foreground">
                    {expanded ? (
                      <ChevronDown className="h-3 w-3" />
                    ) : (
                      <ChevronRight className="h-3 w-3" />
                    )}
                  </span>
                )}
                <span className="truncate italic text-foreground/90">
                  {prop.address || (prop.assignment_number
                    ? `Adresse ukjent (${prop.assignment_number})`
                    : "Adresse ukjent")}
                </span>
              </span>
              <span className="shrink-0 text-muted-foreground ml-2">
                {formatRevenue(prop.total)} kr
              </span>
            </button>
            {expanded && hasTxns && prop.transactions && (
              <div className="pl-4 py-1 space-y-0.5 text-xs text-muted-foreground border-l border-border/30 ml-2">
                {prop.transactions.map((txn, ti) => (
                  <div key={ti} className="flex justify-between gap-2">
                    <span>
                      {txn.posting_date} · Konto {txn.account}
                      {txn.description ? ` · ${txn.description}` : ""}
                    </span>
                    <span>{formatRevenue(txn.amount)} kr</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

function BrokerRow({
  broker,
  expanded,
  expandedProperties,
  onToggleBroker,
  onToggleProperty,
}: {
  broker: SalesReportBroker;
  expanded: boolean;
  expandedProperties: Set<string>;
  onToggleBroker: () => void;
  onToggleProperty: (key: string) => void;
}) {
  const hasProperties = broker.properties.length > 0;

  return (
    <>
      <tr
        className="border-b border-border hover:bg-muted cursor-pointer"
        onClick={hasProperties ? onToggleBroker : undefined}
      >
        <td className="py-2">
          {hasProperties && (
            <span className="inline-block transition-transform duration-fast">
              {expanded ? (
                <ChevronDown className="h-4 w-4 text-muted-foreground" />
              ) : (
                <ChevronRight className="h-4 w-4 text-muted-foreground" />
              )}
            </span>
          )}
        </td>
        <td className="py-2 font-medium pl-2">{broker.name}</td>
        <td className="py-2 text-right pr-4">{broker.sale_count}</td>
        <td className="py-2 pl-4" />
        <td className="py-2 pl-4" />
        <td className="py-2 text-right pl-4">{formatRevenue(broker.total)}</td>
      </tr>
      {expanded &&
        broker.properties.map((prop) => (
          <PropertyRow
            key={`${broker.broker_id}-${prop.estate_id}`}
            brokerId={broker.broker_id}
            property={prop}
            expanded={expandedProperties.has(`${broker.broker_id}-${prop.estate_id}`)}
            onToggle={() => onToggleProperty(`${broker.broker_id}-${prop.estate_id}`)}
          />
        ))}
    </>
  );
}

function useCurrentTime(intervalMs = 60_000) {
  const [now, setNow] = useState(() => Date.now());
  useEffect(() => {
    const id = setInterval(() => setNow(Date.now()), intervalMs);
    return () => clearInterval(id);
  }, [intervalMs]);
  return now;
}

function DataConfidenceBadge({ scope }: { scope: ReportScopeMetadata | undefined }) {
  const now = useCurrentTime();
  if (!scope?.last_synced_at) return null;

  const syncAge = now - new Date(scope.last_synced_at).getTime();
  const minutes = syncAge / 60_000;
  const hasWarnings = (scope.validation_warnings_count ?? 0) > 0;

  let label: string;
  let color: string;
  if (minutes < 15 && !hasWarnings) {
    label = "Fersk";
    color = "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300";
  } else if (minutes < 120) {
    label = hasWarnings ? "Delvis" : "Fersk";
    color = hasWarnings
      ? "bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300"
      : "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300";
  } else {
    label = "Foreldet";
    color = "bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-300";
  }

  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${color}`}>
      {label}
    </span>
  );
}

function ScopePanel({ scope }: { scope: ReportScopeMetadata | undefined }) {
  const [open, setOpen] = useState(false);
  if (!scope) return null;

  return (
    <div className="rounded-md border border-border bg-muted/50 mt-4">
      <button
        className="w-full flex items-center justify-between px-4 py-2.5 text-sm text-left hover:bg-secondary/30"
        onClick={() => setOpen(!open)}
      >
        <span className="font-medium text-foreground">Datagrunnlag</span>
        <span className="flex items-center gap-2">
          <DataConfidenceBadge scope={scope} />
          {open ? (
            <ChevronDown className="h-4 w-4 text-foreground/50" />
          ) : (
            <ChevronRight className="h-4 w-4 text-foreground/50" />
          )}
        </span>
      </button>
      {open && (
        <div className="px-4 pb-3 space-y-3 border-t border-border text-sm text-foreground/80">
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3 pt-3">
            <div>
              <div className="text-xs uppercase tracking-wide text-foreground/50 mb-1">MVA-håndtering</div>
              <div>{scope.vat_handling === "included" ? "Inkludert" : "Eksl."}</div>
            </div>
            <div>
              <div className="text-xs uppercase tracking-wide text-foreground/50 mb-1">Eiendomsstatus</div>
              <div>{scope.estate_statuses}</div>
            </div>
            <div>
              <div className="text-xs uppercase tracking-wide text-foreground/50 mb-1">Meglere</div>
              <div>Kun meglere med salg i perioden</div>
            </div>
          </div>

          <div>
            <div className="text-xs uppercase tracking-wide text-foreground/50 mb-1">Datakilder</div>
            <div className="space-y-1">
              {scope.data_sources.map((ds) => (
                <div key={ds.name} className="flex items-center justify-between text-sm">
                  <span>{ds.label} ({ds.coverage})</span>
                  <span className="text-foreground/50">{ds.row_count} transaksjoner</span>
                </div>
              ))}
            </div>
          </div>

          <div>
            <div className="text-xs uppercase tracking-wide text-foreground/50 mb-1">Konti inkludert</div>
            <div className="flex flex-wrap gap-1">
              {Object.entries(scope.account_categories).map(([category, accounts]) => (
                <span key={category} className="text-xs">
                  <strong className="capitalize">{category === "vederlag" ? "Vederlag" : "Andre inntekter"}:</strong>{" "}
                  {accounts.join(", ")}
                </span>
              ))}
            </div>
          </div>

          {scope.last_synced_at && (
            <div className="text-xs text-foreground/50">
              Sist synkronisert: {new Date(scope.last_synced_at).toLocaleString("nb-NO")}
              {scope.validation_warnings_count > 0 && (
                <span className="text-amber-600 ml-2">
                  {scope.validation_warnings_count} valideringsadvarsel(er)
                </span>
              )}
            </div>
          )}

          <div className="text-xs text-foreground/50 italic">{scope.data_freshness_note}</div>
        </div>
      )}
    </div>
  );
}

function PropertyRow({
  brokerId,
  property,
  expanded,
  onToggle,
}: {
  brokerId: string;
  property: SalesReportProperty;
  expanded: boolean;
  onToggle: () => void;
}) {
  const hasTransactions = property.transactions.length > 0;

  return (
    <>
      <tr
        className="border-b border-border/50 bg-muted/50 hover:bg-secondary/30 cursor-pointer"
        onClick={hasTransactions ? onToggle : undefined}
      >
        <td className="py-1.5 pl-8">
          {hasTransactions && (
            <span className="inline-block transition-transform duration-fast">
              {expanded ? (
                <ChevronDown className="h-3.5 w-3.5 text-foreground/50" />
              ) : (
                <ChevronRight className="h-3.5 w-3.5 text-foreground/50" />
              )}
            </span>
          )}
        </td>
        <td className="py-1.5 italic text-foreground/80 pl-2">
          {property.address || (property.assignment_number
            ? `Adresse ukjent (${property.assignment_number})`
            : "Adresse ukjent")}
        </td>
        <td className="py-1.5 text-right pr-4">—</td>
        <td className="py-1.5 text-muted-foreground pl-4">{property.property_type}</td>
        <td className="py-1.5 text-muted-foreground pl-4">{property.assignment_type}</td>
        <td className="py-1.5 text-right pl-4">{formatRevenue(property.total)}</td>
      </tr>
          {expanded &&
        property.transactions.map((txn, i) => (
          <tr
            key={`${brokerId}-${property.estate_id}-${i}`}
            className="border-b border-border/30 bg-card"
          >
            <td className="py-1 pl-14" />
            <td className="py-1 text-xs text-muted-foreground pl-2">
              {txn.posting_date} · Konto {txn.account}
              {txn.description ? ` · ${txn.description}` : ""}
            </td>
            <td className="py-1 pr-4" />
            <td className="py-1 pl-4" />
            <td className="py-1 pl-4" />
            <td className="py-1 text-right text-xs pl-4">{formatRevenue(txn.amount)}</td>
          </tr>
        ))}
    </>
  );
}
