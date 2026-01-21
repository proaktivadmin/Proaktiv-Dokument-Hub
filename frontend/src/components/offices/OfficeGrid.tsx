"use client";

import { Building2, Plus, Search, RefreshCcw } from "lucide-react";
import { useState, useEffect } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { OfficeCard } from "./OfficeCard";
import { VitecConnectionStatus } from "@/components/vitec";
import { employeesApi } from "@/lib/api/employees";
import type { OfficeWithStats, EmployeeWithOffice } from "@/types/v3";

interface OfficeGridProps {
  offices: OfficeWithStats[];
  cities: string[];
  isLoading: boolean;
  onOfficeClick: (office: OfficeWithStats) => void;
  onCreateNew?: () => void;
  onEdit?: (office: OfficeWithStats) => void;
  onDeactivate?: (office: OfficeWithStats) => void;
  onSync?: () => void;
  isSyncing?: boolean;
  onEmployeeClick?: (employee: EmployeeWithOffice) => void;
}

export function OfficeGrid({
  offices,
  cities,
  isLoading,
  onOfficeClick,
  onCreateNew,
  onEdit,
  onDeactivate,
  onSync,
  isSyncing = false,
  onEmployeeClick,
}: OfficeGridProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [cityFilter, setCityFilter] = useState<string>("all");
  const [showInactive, setShowInactive] = useState(false);
  const [employeesByOffice, setEmployeesByOffice] = useState<Record<string, EmployeeWithOffice[]>>({});
  const [vitecConnected, setVitecConnected] = useState<boolean | null>(null);
  const showActions = Boolean(onCreateNew || onSync);

  // Fetch employees for all offices
  useEffect(() => {
    const fetchEmployees = async () => {
      try {
        const response = await employeesApi.list({ status: ['active', 'onboarding'] });
        const grouped: Record<string, EmployeeWithOffice[]> = {};
        response.items.forEach(emp => {
          if (!grouped[emp.office_id]) {
            grouped[emp.office_id] = [];
          }
          grouped[emp.office_id].push(emp);
        });
        setEmployeesByOffice(grouped);
      } catch (error) {
        console.error("Failed to fetch employees:", error);
      }
    };

    if (offices.length > 0) {
      fetchEmployees();
    }
  }, [offices]);

  // Filter offices
  const filteredOffices = offices.filter((office) => {
    // Search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      const matchesSearch =
        office.name.toLowerCase().includes(query) ||
        office.short_code.toLowerCase().includes(query) ||
        (office.city?.toLowerCase().includes(query) ?? false);
      if (!matchesSearch) return false;
    }

    // City filter
    if (cityFilter !== "all" && office.city !== cityFilter) {
      return false;
    }

    // Status filter (active by default)
    if (!showInactive && !office.is_active) return false;

    return true;
  });

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="flex items-center gap-4">
          <Skeleton className="h-10 flex-1 max-w-sm" />
          <Skeleton className="h-10 w-32" />
          <Skeleton className="h-10 w-32" />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-40" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Filters */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Søk kontorer..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9"
          />
        </div>

        <Select value={cityFilter} onValueChange={setCityFilter}>
          <SelectTrigger className="w-[150px]">
            <SelectValue placeholder="Alle byer" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Alle byer</SelectItem>
            {cities.map((city) => (
              <SelectItem key={city} value={city}>
                {city}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Button
          variant="outline"
          onClick={() => setShowInactive((prev) => !prev)}
        >
          {showInactive ? "Skjul inaktive" : "Vis inaktive"}
        </Button>

        {showActions && (
          <div className="flex gap-2 ml-auto items-center">
            <VitecConnectionStatus onStatusChange={setVitecConnected} />
            {onSync && (
              <Button
                variant="outline"
                onClick={onSync}
                disabled={isSyncing || vitecConnected === false}
                title={vitecConnected === false ? "Vitec API ikke tilkoblet" : undefined}
              >
                <RefreshCcw className="h-4 w-4 mr-2" />
                {isSyncing ? "Synkroniserer..." : "Synkroniser Vitec"}
              </Button>
            )}
            {onCreateNew && (
              <Button onClick={onCreateNew}>
                <Plus className="h-4 w-4 mr-2" />
                Nytt kontor
              </Button>
            )}
          </div>
        )}
      </div>

      {/* Grid */}
      {filteredOffices.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <Building2 className="h-12 w-12 text-muted-foreground/50 mb-4" />
          <h3 className="text-lg font-medium mb-1">Ingen kontorer funnet</h3>
          <p className="text-sm text-muted-foreground mb-4">
            {searchQuery || cityFilter !== "all"
              ? "Prøv å endre søket eller filtrene"
              : "Kom i gang ved å opprette ditt første kontor"}
          </p>
          {onCreateNew && !searchQuery && cityFilter === "all" && (
            <Button onClick={onCreateNew}>
              <Plus className="h-4 w-4 mr-2" />
              Opprett kontor
            </Button>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredOffices.map((office) => (
            <OfficeCard
              key={office.id}
              office={office}
              employees={employeesByOffice[office.id] || []}
              onClick={() => onOfficeClick(office)}
              onEdit={onEdit ? () => onEdit(office) : undefined}
              onDeactivate={onDeactivate ? () => onDeactivate(office) : undefined}
              onEmployeeClick={onEmployeeClick}
            />
          ))}
        </div>
      )}
    </div>
  );
}
