"use client";

import { Users, Plus, Search, Mail, RefreshCcw, Cloud, CheckSquare, X } from "lucide-react";
import { useState, useMemo } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Checkbox } from "@/components/ui/checkbox";
import { EmployeeCard } from "./EmployeeCard";
import { EntraConnectionStatus } from "./EntraConnectionStatus";
import { VitecConnectionStatus } from "@/components/vitec";
import type { EmployeeWithOffice } from "@/types/v3";

interface EmployeeGridProps {
  employees: EmployeeWithOffice[];
  isLoading: boolean;
  showOffice?: boolean;
  showInactive?: boolean;
  onToggleShowInactive?: () => void;
  onEmployeeClick: (employee: EmployeeWithOffice) => void;
  onCreateNew?: () => void;
  onEdit?: (employee: EmployeeWithOffice) => void;
  onStartOffboarding?: (employee: EmployeeWithOffice) => void;
  onDeactivate?: (employee: EmployeeWithOffice) => void;
  onSync?: () => void;
  isSyncing?: boolean;
  onEntraImport?: () => void;
  isEntraImporting?: boolean;
  currentFilters?: {
    office_id?: string;
    role?: string;
  };
  // Entra sync props
  onEntraSync?: (employee: EmployeeWithOffice) => void;
  onSignaturePreview?: (employee: EmployeeWithOffice) => void;
  onBatchEntraSync?: (employees: EmployeeWithOffice[]) => void;
}


export function EmployeeGrid({
  employees,
  isLoading,
  showOffice = true,
  showInactive = false,
  onToggleShowInactive,
  onEmployeeClick,
  onCreateNew,
  onEdit,
  onStartOffboarding,
  onDeactivate,
  onSync,
  isSyncing = false,
  onEntraImport,
  isEntraImporting = false,
  currentFilters,
  onEntraSync,
  onSignaturePreview,
  onBatchEntraSync,
}: EmployeeGridProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [vitecConnected, setVitecConnected] = useState<boolean | null>(null);
  const [entraConnected, setEntraConnected] = useState<boolean | null>(null);
  const [selectionMode, setSelectionMode] = useState(false);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const showActions = Boolean(onCreateNew || onSync || onEntraImport || onBatchEntraSync);

  // Filter employees by search
  const filteredEmployees = employees.filter((employee) => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    return (
      employee.full_name.toLowerCase().includes(query) ||
      (employee.title?.toLowerCase().includes(query) ?? false) ||
      (employee.email?.toLowerCase().includes(query) ?? false) ||
      employee.office.name.toLowerCase().includes(query)
    );
  });

  // Get selected employees
  const selectedEmployees = useMemo(() => {
    return filteredEmployees.filter((e) => selectedIds.has(e.id));
  }, [filteredEmployees, selectedIds]);

  // Selection handlers
  const toggleSelect = (employeeId: string) => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(employeeId)) {
        next.delete(employeeId);
      } else {
        next.add(employeeId);
      }
      return next;
    });
  };

  const selectAll = () => {
    setSelectedIds(new Set(filteredEmployees.map((e) => e.id)));
  };

  const clearSelection = () => {
    setSelectedIds(new Set());
    setSelectionMode(false);
  };

  const allSelected = filteredEmployees.length > 0 && filteredEmployees.every((e) => selectedIds.has(e.id));

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="flex items-center gap-4">
          <Skeleton className="h-10 flex-1 max-w-sm" />
          <Skeleton className="h-10 w-32" />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-32" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4 flex-1">
      {/* Header with search */}
      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Søk ansatte..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9"
          />
        </div>

        {onToggleShowInactive && (
          <Button variant="outline" onClick={onToggleShowInactive}>
            {showInactive ? "Skjul inaktive" : "Vis inaktive"}
          </Button>
        )}

        {showActions && (
          <div className="flex gap-2 ml-auto items-center">
            <VitecConnectionStatus onStatusChange={setVitecConnected} />
            <EntraConnectionStatus onStatusChange={setEntraConnected} />
            
            {/* Selection mode toggle */}
            {entraConnected && onBatchEntraSync && (
              <Button
                variant={selectionMode ? "secondary" : "outline"}
                onClick={() => {
                  if (selectionMode) {
                    clearSelection();
                  } else {
                    setSelectionMode(true);
                  }
                }}
              >
                <CheckSquare className="h-4 w-4 mr-2" />
                {selectionMode ? "Avbryt valg" : "Velg flere"}
              </Button>
            )}

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

            {onEntraImport && (
              <Button
                variant="outline"
                onClick={onEntraImport}
                disabled={isEntraImporting || entraConnected === false}
                title={entraConnected === false ? "Entra ID ikke konfigurert" : undefined}
              >
                <Cloud className="h-4 w-4 mr-2" />
                {isEntraImporting ? "Henter Entra..." : "Hent Entra"}
              </Button>
            )}
            {/* Email Group Button */}
            <Button
              variant="outline"
              onClick={() => {
                if (currentFilters) {
                  const params = new URLSearchParams();
                  if (currentFilters.office_id) params.append('office_id', currentFilters.office_id);
                  if (currentFilters.role) params.append('role', currentFilters.role);

                  // Direct fetch to trigger download/mailto
                  fetch(`/api/employees/email-group?${params.toString()}`)
                    .then(res => res.json())
                    .then(data => {
                      if (data.mailto_link) window.location.href = data.mailto_link;
                    })
                    .catch(err => console.error("Failed to get email group", err));
                }
              }}
            >
              <Mail className="h-4 w-4 mr-2" />
              E-postliste
            </Button>

            {onCreateNew && (
              <Button onClick={onCreateNew}>
                <Plus className="h-4 w-4 mr-2" />
                Ny ansatt
              </Button>
            )}
          </div>
        )}

      </div>

      {/* Selection action bar */}
      {selectionMode && selectedIds.size > 0 && (
        <div className="flex items-center gap-4 p-3 bg-primary/5 rounded-lg border border-primary/20">
          <div className="flex items-center gap-2">
            <Checkbox
              checked={allSelected}
              onCheckedChange={(checked) => {
                if (checked) {
                  selectAll();
                } else {
                  setSelectedIds(new Set());
                }
              }}
            />
            <span className="text-sm font-medium">
              {selectedIds.size} valgt
            </span>
          </div>
          
          <div className="flex gap-2 ml-auto">
            {onBatchEntraSync && (
              <Button
                size="sm"
                onClick={() => onBatchEntraSync(selectedEmployees)}
              >
                <Cloud className="h-4 w-4 mr-2" />
                Synkroniser {selectedIds.size} til Entra ID
              </Button>
            )}
            <Button size="sm" variant="ghost" onClick={clearSelection}>
              <X className="h-4 w-4" />
            </Button>
          </div>
        </div>
      )}

      {/* Grid */}
      {filteredEmployees.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <Users className="h-12 w-12 text-muted-foreground/50 mb-4" />
          <h3 className="text-lg font-medium mb-1">Ingen ansatte funnet</h3>
          <p className="text-sm text-muted-foreground mb-4">
            {searchQuery
              ? "Prøv å endre søket"
              : "Kom i gang ved å legge til din første ansatt"}
          </p>
          {onCreateNew && !searchQuery && (
            <Button onClick={onCreateNew}>
              <Plus className="h-4 w-4 mr-2" />
              Legg til ansatt
            </Button>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filteredEmployees.map((employee) => (
            <EmployeeCard
              key={employee.id}
              employee={employee}
              showOffice={showOffice}
              onClick={() => onEmployeeClick(employee)}
              onEdit={onEdit ? () => onEdit(employee) : undefined}
              onStartOffboarding={onStartOffboarding ? () => onStartOffboarding(employee) : undefined}
              onDeactivate={onDeactivate ? () => onDeactivate(employee) : undefined}
              // Selection props
              selectable={selectionMode}
              selected={selectedIds.has(employee.id)}
              onSelectChange={() => toggleSelect(employee.id)}
              // Entra props
              entraConnected={entraConnected === true}
              onEntraSync={onEntraSync ? () => onEntraSync(employee) : undefined}
              onSignaturePreview={onSignaturePreview ? () => onSignaturePreview(employee) : undefined}
            />
          ))}
        </div>
      )}
    </div>
  );
}
