"use client";

import { useState, useCallback, useEffect } from "react";
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
  type SalesReportData,
  type SalesReportBroker,
  type SalesReportProperty,
} from "@/lib/api/reports";
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

  const [bestPerformers, setBestPerformers] = useState<BestPerformersData | null>(null);
  const [bestLoading, setBestLoading] = useState(false);
  const [bestDownloadLoading, setBestDownloadLoading] = useState(false);

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
    } catch (err) {
      setError(err instanceof Error ? err.message : "Kunne ikke laste rapporten.");
      setData(null);
      setFranchiseData(null);
    } finally {
      setLoading(false);
    }
  }, [mode, year, departmentId, fromDate, toDate, includeVat]);

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
      URL.revokeObjectURL(url);
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
    try {
      const result = await fetchBestPerformers({
        year,
        from_date: fromDate ?? undefined,
        to_date: toDate ?? undefined,
        include_vat: includeVat,
        top_n: 5,
      });
      setBestPerformers(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Kunne ikke laste best performers.");
    } finally {
      setBestLoading(false);
    }
  }, [year, fromDate, toDate, includeVat]);

  const handleBestPerformersDownload = async () => {
    setBestDownloadLoading(true);
    setError(null);
    try {
      const blob = await downloadBestPerformers({
        year,
        from_date: fromDate ?? undefined,
        to_date: toDate ?? undefined,
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
      URL.revokeObjectURL(url);
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

  useEffect(() => {
    loadOffices();
  }, [loadOffices]);
  useEffect(() => {
    loadSubscriptions();
  }, [loadSubscriptions]);

  const sumLabel = includeVat ? "Sum (inkl. mva)" : "Sum (exkl. mva)";

  return (
    <div className="min-h-screen bg-background">
      <Header />

      <main className="container mx-auto px-6 py-8">
        <h1 className="text-2xl font-serif font-bold text-[#272630] mb-2">Rapporter</h1>
        <p className="text-[#272630]/60 mb-8">
          Inspiser og last ned Formidlingsrapport. Velg omfang og klikk Last inn for å vise data.
        </p>

        {/* Scope filters */}
        <Card className="mb-8 border border-[#E5E5E5] shadow-card">
          <CardHeader>
            <div className="flex items-center gap-3">
              <div className="p-3 rounded-lg bg-[#E9E7DC]">
                <BarChart3 className="h-6 w-6 text-[#272630]" />
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
                <span className="text-sm text-[#272630]/60">Måned:</span>
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
                <span className="text-sm text-[#272630]/60">Uke:</span>
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
              <div className="text-sm text-[#272630]/70 border-l border-[#E5E5E5] pl-4">
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
                className="bg-[#272630] hover:bg-[#272630]/90 text-white"
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
            {error && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2 text-red-700">
                <AlertCircle className="h-4 w-4 shrink-0" />
                <span className="text-sm">{error}</span>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Visual dashboard */}
        {data && mode === "department" && (
          <Card className="border border-[#E5E5E5] shadow-card">
            <CardHeader>
              <CardTitle className="font-serif">
                Periode: {data.from_date_display} – {data.to_date_display}
              </CardTitle>
              <CardDescription>
                {data.total_sales} salg totalt · {sumLabel}: {data.total_revenue.toLocaleString("nb-NO")} kr
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-[#E5E5E5]">
                      <th className="text-left py-3 font-semibold text-[#272630] w-8" />
                      <th className="text-left py-3 font-semibold text-[#272630]">Megler</th>
                      <th className="text-right py-3 font-semibold text-[#272630]">Antall salg</th>
                      <th className="text-left py-3 font-semibold text-[#272630]">Eiendomstype</th>
                      <th className="text-left py-3 font-semibold text-[#272630]">Oppdragstype</th>
                      <th className="text-right py-3 font-semibold text-[#272630]">{sumLabel} (kr)</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.brokers.map((broker) => (
                      <BrokerRow
                        key={broker.broker_id}
                        broker={broker}
                        expanded={expandedBrokers.has(broker.broker_id)}
                        expandedProperties={expandedProperties}
                        onToggleBroker={() => toggleBroker(broker.broker_id)}
                        onToggleProperty={toggleProperty}
                      />
                    ))}
                    <tr className="border-t-2 border-[#272630] font-bold bg-[#E9E7DC]/30">
                      <td className="py-3" />
                      <td className="py-3">Sum</td>
                      <td className="py-3 text-right">{data.total_sales}</td>
                      <td className="py-3" />
                      <td className="py-3" />
                      <td className="py-3 text-right">
                        {data.total_revenue.toLocaleString("nb-NO")}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        )}

        {franchiseData && mode === "franchise" && (
          <Card className="border border-[#E5E5E5] shadow-card mb-8">
            <CardHeader>
              <CardTitle className="font-serif">Franchise sammendrag</CardTitle>
              <CardDescription>
                {franchiseData.summary.department_count} avdelinger · {franchiseData.summary.total_sales} salg ·{" "}
                {franchiseData.summary.total_revenue.toLocaleString("nb-NO")} kr
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

        <Card className="border border-[#E5E5E5] shadow-card mb-8">
          <CardHeader>
            <div className="flex items-center gap-2">
              <Trophy className="h-5 w-5 text-[#BCAB8A]" />
              <CardTitle className="font-serif">Best performers</CardTitle>
            </div>
            <CardDescription>Ukentlig/månedlig toppliste for meglere og avdelinger.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
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
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <LeaderboardCard title="Eiendomsmegler" rows={bestPerformers.eiendomsmegler} nameKey="name" />
                <LeaderboardCard
                  title="Eiendomsmeglerfullmektig"
                  rows={bestPerformers.eiendomsmeglerfullmektig}
                  nameKey="name"
                />
                <LeaderboardCard title="Avdeling" rows={bestPerformers.departments} nameKey="department_name" />
              </div>
            )}
          </CardContent>
        </Card>

        <Card className="border border-[#E5E5E5] shadow-card mb-8">
          <CardHeader>
            <div className="flex items-center gap-2">
              <Target className="h-5 w-5 text-[#BCAB8A]" />
              <CardTitle className="font-serif">Budsjett vs faktisk</CardTitle>
            </div>
            <CardDescription>Månedlige budsjetter med YTD-status og prognose.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Button variant="outline" onClick={loadBudget} disabled={budgetLoading}>
              {budgetLoading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <RefreshCw className="h-4 w-4 mr-2" />}
              Last budsjett
            </Button>
            {budgetComparison && (
              <>
                <div className="text-sm text-[#272630]/70">
                  Status: <strong>{budgetComparison.status}</strong> · YTD:{" "}
                  {budgetComparison.ytd_actual.toLocaleString("nb-NO")} /{" "}
                  {budgetComparison.ytd_budget.toLocaleString("nb-NO")} kr
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-[#E5E5E5]">
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
                        <tr key={row.month} className="border-b border-[#E5E5E5]/50">
                          <td className="py-2">{MONTHS_NB[row.month - 1]}</td>
                          <td className="py-2 text-right">{row.actual.toLocaleString("nb-NO")}</td>
                          <td className="py-2 text-right">
                            <Input
                              value={budgetDraft[row.month] ?? ""}
                              onChange={(e) =>
                                setBudgetDraft((prev) => ({ ...prev, [row.month]: e.target.value }))
                              }
                              className="w-28 ml-auto"
                            />
                          </td>
                          <td className="py-2 text-right">{row.variance.toLocaleString("nb-NO")}</td>
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

        <Card className="border border-[#E5E5E5] shadow-card">
          <CardHeader>
            <div className="flex items-center gap-2">
              <Mail className="h-5 w-5 text-[#BCAB8A]" />
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
                  className="flex items-center justify-between rounded-md border border-[#E5E5E5] p-3"
                >
                  <div className="text-sm">
                    <div className="font-medium">{sub.name}</div>
                    <div className="text-[#272630]/60">
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
          <p className="text-[#272630]/60 text-center py-12">
            Velg omfang og klikk &quot;Last inn rapport&quot; for å vise data.
          </p>
        )}
      </main>
    </div>
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
    <div className="border border-[#E5E5E5] rounded-md">
      <button
        className="w-full flex items-center justify-between px-3 py-2 hover:bg-[#F5F5F0]"
        onClick={onToggle}
      >
        <span className="font-medium">
          {department.department_name} · {department.total_sales} salg
        </span>
        <span className="text-sm text-[#272630]/70">
          {department.total_revenue.toLocaleString("nb-NO")} kr ({department.revenue_share_percent}%)
        </span>
      </button>
      {expanded && (
        <div className="px-3 pb-3">
          {department.brokers.map((b) => (
            <div key={b.broker_id} className="flex justify-between text-sm py-1 border-b last:border-b-0">
              <span>{b.name}</span>
              <span>
                {b.sale_count} salg · {b.total.toLocaleString("nb-NO")} kr
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
}: {
  title: string;
  rows: PerformerRow[];
  nameKey: "name" | "department_name";
}) {
  return (
    <Card className="border border-[#E5E5E5]">
      <CardHeader className="pb-2">
        <CardTitle className="text-base">{title}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-1">
        {rows.length === 0 ? (
          <p className="text-sm text-[#272630]/60">Ingen data</p>
        ) : (
          rows.map((row, i) => (
            <div key={`${row[nameKey] ?? i}`} className="flex justify-between text-sm">
              <span>
                {i + 1}. {String(row[nameKey] ?? "—")}
              </span>
              <span>{Number(row.total_revenue ?? 0).toLocaleString("nb-NO")} kr</span>
            </div>
          ))
        )}
      </CardContent>
    </Card>
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
        className="border-b border-[#E5E5E5] hover:bg-[#F5F5F0] cursor-pointer"
        onClick={hasProperties ? onToggleBroker : undefined}
      >
        <td className="py-2">
          {hasProperties && (
            <span className="inline-block transition-transform duration-fast">
              {expanded ? (
                <ChevronDown className="h-4 w-4 text-[#272630]/60" />
              ) : (
                <ChevronRight className="h-4 w-4 text-[#272630]/60" />
              )}
            </span>
          )}
        </td>
        <td className="py-2 font-medium">{broker.name}</td>
        <td className="py-2 text-right">{broker.sale_count}</td>
        <td className="py-2" />
        <td className="py-2" />
        <td className="py-2 text-right">{broker.total.toLocaleString("nb-NO")}</td>
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
        className="border-b border-[#E5E5E5]/50 bg-[#F5F5F0]/50 hover:bg-[#E9E7DC]/30 cursor-pointer"
        onClick={hasTransactions ? onToggle : undefined}
      >
        <td className="py-1.5 pl-8">
          {hasTransactions && (
            <span className="inline-block transition-transform duration-fast">
              {expanded ? (
                <ChevronDown className="h-3.5 w-3.5 text-[#272630]/50" />
              ) : (
                <ChevronRight className="h-3.5 w-3.5 text-[#272630]/50" />
              )}
            </span>
          )}
        </td>
        <td className="py-1.5 italic text-[#272630]/80">{property.address}</td>
        <td className="py-1.5 text-right">—</td>
        <td className="py-1.5 text-[#272630]/70">{property.property_type}</td>
        <td className="py-1.5 text-[#272630]/70">{property.assignment_type}</td>
        <td className="py-1.5 text-right">{property.total.toLocaleString("nb-NO")}</td>
      </tr>
          {expanded &&
        property.transactions.map((txn, i) => (
          <tr
            key={`${brokerId}-${property.estate_id}-${i}`}
            className="border-b border-[#E5E5E5]/30 bg-white"
          >
            <td className="py-1 pl-14" />
            <td className="py-1 text-xs text-[#272630]/70">
              {txn.posting_date} · Konto {txn.account}
              {txn.description ? ` · ${txn.description}` : ""}
            </td>
            <td className="py-1" />
            <td className="py-1" />
            <td className="py-1" />
            <td className="py-1" />
            <td className="py-1 text-right text-xs">{txn.amount.toLocaleString("nb-NO")}</td>
          </tr>
        ))}
    </>
  );
}
