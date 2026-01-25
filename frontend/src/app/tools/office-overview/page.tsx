"use client";

import { useState, useMemo } from "react";
import { Header } from "@/components/layout/Header";
import { useOffices } from "@/hooks/v3/useOffices";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import {
  Search,
  Building2,
  Check,
  X,
  Download,
  AlertTriangle,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface OfficeInfo {
  id: string;
  name: string;
  legal_name: string | null;
  organization_number: string | null;
  email: string | null;
  phone: string | null;
  street_address: string | null;
  postal_code: string | null;
  city: string | null;
  homepage_url: string | null;
  employee_count: number;
}

function StatusIcon({ value }: { value: string | null | undefined }) {
  if (value && value.trim()) {
    return <Check className="h-4 w-4 text-emerald-600" />;
  }
  return <X className="h-4 w-4 text-red-500" />;
}

function MissingBadge({ fields }: { fields: string[] }) {
  if (fields.length === 0) return null;
  return (
    <Badge variant="destructive" className="text-xs">
      <AlertTriangle className="h-3 w-3 mr-1" />
      {fields.length} mangler
    </Badge>
  );
}

export default function OfficeOverviewPage() {
  const { offices, isLoading } = useOffices({ include_sub: true });
  const [search, setSearch] = useState("");

  const officeData: OfficeInfo[] = useMemo(() => {
    if (!offices) return [];
    return offices.map((o) => ({
      id: o.id,
      name: o.name,
      legal_name: o.legal_name,
      organization_number: o.organization_number,
      email: o.email,
      phone: o.phone,
      street_address: o.street_address,
      postal_code: o.postal_code,
      city: o.city,
      homepage_url: o.homepage_url,
      employee_count: o.employee_count ?? 0,
    }));
  }, [offices]);

  const filteredOffices = useMemo(() => {
    if (!search.trim()) return officeData;
    const q = search.toLowerCase();
    return officeData.filter(
      (o) =>
        o.name.toLowerCase().includes(q) ||
        o.legal_name?.toLowerCase().includes(q) ||
        o.city?.toLowerCase().includes(q) ||
        o.email?.toLowerCase().includes(q)
    );
  }, [officeData, search]);

  const officesWithMissingInfo = useMemo(() => {
    return filteredOffices.filter((o) => {
      if (o.employee_count === 0) return false;
      return !o.phone || !o.street_address || !o.city || !o.postal_code;
    });
  }, [filteredOffices]);

  const getMissingFields = (o: OfficeInfo): string[] => {
    const missing: string[] = [];
    if (!o.phone) missing.push("telefon");
    if (!o.street_address) missing.push("adresse");
    if (!o.city) missing.push("by");
    if (!o.postal_code) missing.push("postnr");
    if (!o.email) missing.push("e-post");
    return missing;
  };

  const handleExportCSV = () => {
    const headers = [
      "Kontor",
      "Juridisk navn",
      "Org.nr",
      "E-post",
      "Telefon",
      "Adresse",
      "Postnr",
      "By",
      "Nettside",
      "Ansatte",
    ];
    const rows = filteredOffices.map((o) => [
      o.name,
      o.legal_name ?? "",
      o.organization_number ?? "",
      o.email ?? "",
      o.phone ?? "",
      o.street_address ?? "",
      o.postal_code ?? "",
      o.city ?? "",
      o.homepage_url ?? "",
      o.employee_count.toString(),
    ]);

    const csv = [headers, ...rows]
      .map((row) => row.map((cell) => `"${cell.replace(/"/g, '""')}"`).join(","))
      .join("\n");

    const blob = new Blob(["\uFEFF" + csv], { type: "text/csv;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `kontorer-oversikt-${new Date().toISOString().slice(0, 10)}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main className="container mx-auto px-6 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <Building2 className="h-6 w-6 text-muted-foreground" />
            <h2 className="text-2xl font-bold text-foreground">Kontor-oversikt</h2>
          </div>
          <p className="text-muted-foreground">
            Komplett oversikt over alle kontorer med signatur-informasjon
          </p>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-white rounded-lg border p-4 shadow-card">
            <div className="text-sm text-muted-foreground">Totalt kontorer</div>
            <div className="text-2xl font-bold">{officeData.length}</div>
          </div>
          <div className="bg-white rounded-lg border p-4 shadow-card">
            <div className="text-sm text-muted-foreground">Med ansatte</div>
            <div className="text-2xl font-bold">
              {officeData.filter((o) => o.employee_count > 0).length}
            </div>
          </div>
          <div
            className={cn(
              "rounded-lg border p-4 shadow-card",
              officesWithMissingInfo.length > 0
                ? "bg-red-50 border-red-200"
                : "bg-emerald-50 border-emerald-200"
            )}
          >
            <div className="text-sm text-muted-foreground">Mangler informasjon</div>
            <div
              className={cn(
                "text-2xl font-bold",
                officesWithMissingInfo.length > 0 ? "text-red-600" : "text-emerald-600"
              )}
            >
              {officesWithMissingInfo.length}
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="flex items-center gap-4 mb-6">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Søk på kontor, juridisk navn, by..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-10"
            />
          </div>
          <Button variant="outline" onClick={handleExportCSV}>
            <Download className="h-4 w-4 mr-2" />
            Eksporter CSV
          </Button>
        </div>

        {/* Warning banner if missing info */}
        {officesWithMissingInfo.length > 0 && (
          <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-6 flex items-start gap-3">
            <AlertTriangle className="h-5 w-5 text-amber-600 mt-0.5" />
            <div>
              <div className="font-medium text-amber-800">
                {officesWithMissingInfo.length} kontor(er) med ansatte mangler signatur-informasjon
              </div>
              <div className="text-sm text-amber-700 mt-1">
                {officesWithMissingInfo.map((o) => o.name).join(", ")}
              </div>
            </div>
          </div>
        )}

        {/* Table */}
        <div className="bg-white rounded-lg border shadow-card overflow-hidden">
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow className="bg-muted/50">
                  <TableHead className="font-semibold">Kontor</TableHead>
                  <TableHead className="font-semibold">Juridisk navn</TableHead>
                  <TableHead className="font-semibold">Org.nr</TableHead>
                  <TableHead className="font-semibold text-center">E-post</TableHead>
                  <TableHead className="font-semibold text-center">Telefon</TableHead>
                  <TableHead className="font-semibold text-center">Adresse</TableHead>
                  <TableHead className="font-semibold text-right">Ansatte</TableHead>
                  <TableHead className="font-semibold">Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {isLoading ? (
                  <TableRow>
                    <TableCell colSpan={8} className="text-center py-8 text-muted-foreground">
                      Laster kontorer...
                    </TableCell>
                  </TableRow>
                ) : filteredOffices.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={8} className="text-center py-8 text-muted-foreground">
                      Ingen kontorer funnet
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredOffices.map((office) => {
                    const missing = getMissingFields(office);
                    const hasEmployees = office.employee_count > 0;
                    const hasIssues = hasEmployees && missing.length > 0;

                    return (
                      <TableRow
                        key={office.id}
                        className={cn(
                          hasIssues && "bg-red-50/50",
                          !hasEmployees && "opacity-60"
                        )}
                      >
                        <TableCell className="font-medium">{office.name}</TableCell>
                        <TableCell className="text-muted-foreground">
                          {office.legal_name ?? "-"}
                        </TableCell>
                        <TableCell className="font-mono text-sm">
                          {office.organization_number ?? "-"}
                        </TableCell>
                        <TableCell className="text-center">
                          <StatusIcon value={office.email} />
                        </TableCell>
                        <TableCell className="text-center">
                          <StatusIcon value={office.phone} />
                        </TableCell>
                        <TableCell className="text-center">
                          <StatusIcon
                            value={
                              office.street_address && office.city && office.postal_code
                                ? "ok"
                                : null
                            }
                          />
                        </TableCell>
                        <TableCell className="text-right">{office.employee_count}</TableCell>
                        <TableCell>
                          {hasEmployees ? (
                            missing.length > 0 ? (
                              <MissingBadge fields={missing} />
                            ) : (
                              <Badge
                                variant="outline"
                                className="text-emerald-600 border-emerald-200 bg-emerald-50"
                              >
                                <Check className="h-3 w-3 mr-1" />
                                Komplett
                              </Badge>
                            )
                          ) : (
                            <span className="text-xs text-muted-foreground">Ingen ansatte</span>
                          )}
                        </TableCell>
                      </TableRow>
                    );
                  })
                )}
              </TableBody>
            </Table>
          </div>
        </div>

        {/* Details section */}
        <div className="mt-8">
          <h3 className="text-lg font-semibold mb-4">Detaljert informasjon</h3>
          <div className="grid gap-4">
            {filteredOffices
              .filter((o) => o.employee_count > 0)
              .map((office) => (
                <div
                  key={office.id}
                  className="bg-white rounded-lg border shadow-card p-4"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <h4 className="font-semibold text-lg">{office.name}</h4>
                      <p className="text-sm text-muted-foreground">
                        {office.legal_name}
                        {office.organization_number && ` • Org.nr: ${office.organization_number}`}
                      </p>
                    </div>
                    <Badge variant="secondary">{office.employee_count} ansatte</Badge>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 text-sm">
                    <div>
                      <div className="text-muted-foreground mb-1">E-post</div>
                      <div className={cn(!office.email && "text-red-500 font-medium")}>
                        {office.email || "Ikke registrert"}
                      </div>
                    </div>
                    <div>
                      <div className="text-muted-foreground mb-1">Telefon</div>
                      <div className={cn(!office.phone && "text-red-500 font-medium")}>
                        {office.phone || "Ikke registrert"}
                      </div>
                    </div>
                    <div>
                      <div className="text-muted-foreground mb-1">Adresse</div>
                      <div
                        className={cn(
                          (!office.street_address || !office.city) && "text-red-500 font-medium"
                        )}
                      >
                        {office.street_address && office.postal_code && office.city
                          ? `${office.street_address}, ${office.postal_code} ${office.city}`
                          : "Ikke registrert"}
                      </div>
                    </div>
                    <div>
                      <div className="text-muted-foreground mb-1">Nettside</div>
                      <div className="truncate">
                        {office.homepage_url ? (
                          <a
                            href={office.homepage_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-blue-600 hover:underline"
                          >
                            {office.homepage_url.replace(/^https?:\/\//, "")}
                          </a>
                        ) : (
                          <span className="text-muted-foreground">Ikke registrert</span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
          </div>
        </div>
      </main>
    </div>
  );
}
