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
  ChevronRight,
  ChevronDown,
  RefreshCw,
} from "lucide-react";
import {
  downloadSalesReport,
  fetchSalesReportData,
  type SalesReportData,
  type SalesReportBroker,
  type SalesReportProperty,
} from "@/lib/api/reports";
import { officesApi } from "@/lib/api/offices";
import type { OfficeWithStats } from "@/types/v3";

export default function ReportsPage() {
  const [loading, setLoading] = useState(false);
  const [downloadLoading, setDownloadLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [includeVat, setIncludeVat] = useState(false);
  const [year, setYear] = useState<number>(new Date().getFullYear());
  const [departmentId, setDepartmentId] = useState<number>(1120);
  const [data, setData] = useState<SalesReportData | null>(null);
  const [offices, setOffices] = useState<OfficeWithStats[]>([]);
  const [expandedBrokers, setExpandedBrokers] = useState<Set<string>>(new Set());
  const [expandedProperties, setExpandedProperties] = useState<Set<string>>(new Set());

  const loadOffices = useCallback(async () => {
    try {
      const res = await officesApi.list({ is_active: true });
      setOffices(res.items.filter((o) => o.vitec_department_id != null));
    } catch {
      setOffices([]);
    }
  }, []);

  const loadReport = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const reportData = await fetchSalesReportData({
        year,
        department_id: departmentId,
        include_vat: includeVat,
      });
      setData(reportData);
      setExpandedBrokers(new Set());
      setExpandedProperties(new Set());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Kunne ikke laste rapporten.");
      setData(null);
    } finally {
      setLoading(false);
    }
  }, [year, departmentId, includeVat]);

  const handleDownload = async () => {
    setDownloadLoading(true);
    setError(null);
    try {
      const blob = await downloadSalesReport({
        year,
        department_id: departmentId,
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

  useEffect(() => {
    loadOffices();
  }, [loadOffices]);

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
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
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
                <Label>Avdeling</Label>
                <Select
                  value={String(departmentId)}
                  onValueChange={(v) => setDepartmentId(parseInt(v, 10))}
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
              <div className="flex items-center space-x-2 pt-8">
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
                disabled={downloadLoading || !data}
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
        {data && (
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
                      <th className="text-right py-3 font-semibold text-[#272630]">{sumLabel} (kr)</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.brokers.map((broker) => (
                      <BrokerRow
                        key={broker.broker_id}
                        broker={broker}
                        sumLabel={sumLabel}
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

        {!data && !loading && !error && (
          <p className="text-[#272630]/60 text-center py-12">
            Velg omfang og klikk &quot;Last inn rapport&quot; for å vise data.
          </p>
        )}
      </main>
    </div>
  );
}

function BrokerRow({
  broker,
  sumLabel,
  expanded,
  expandedProperties,
  onToggleBroker,
  onToggleProperty,
}: {
  broker: SalesReportBroker;
  sumLabel: string;
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
        <td className="py-2 text-right">{broker.total.toLocaleString("nb-NO")}</td>
      </tr>
      {expanded &&
        broker.properties.map((prop) => (
          <PropertyRow
            key={`${broker.broker_id}-${prop.estate_id}`}
            brokerId={broker.broker_id}
            property={prop}
            sumLabel={sumLabel}
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
  sumLabel,
  expanded,
  onToggle,
}: {
  brokerId: string;
  property: SalesReportProperty;
  sumLabel: string;
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
            <td className="py-1 text-right">—</td>
            <td className="py-1 text-right text-xs">{txn.amount.toLocaleString("nb-NO")}</td>
          </tr>
        ))}
    </>
  );
}
