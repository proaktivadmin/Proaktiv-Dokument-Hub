"use client";

import { Building2, Filter } from "lucide-react";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { cn } from "@/lib/utils";
import type { OfficeWithStats, EmployeeStatus } from "@/types/v3";

interface EmployeeSidebarProps {
  offices: OfficeWithStats[];
  selectedOfficeId: string | null;
  statusFilters: EmployeeStatus[];
  statusCounts: Record<EmployeeStatus, number>;
  onOfficeSelect: (officeId: string | null) => void;
  onStatusToggle: (status: EmployeeStatus) => void;
}

const statusLabels: Record<EmployeeStatus, string> = {
  active: "Aktiv",
  onboarding: "Onboarding",
  offboarding: "Offboarding",
  inactive: "Inaktiv",
};

// Helper function to shorten office names
const shortenOfficeName = (name: string): string => {
  // Remove "Proaktiv Eiendomsmegling" and clean up
  return name
    .replace(/Proaktiv Eiendomsmegling\s*/gi, '')
    .replace(/^-\s*/, '') // Remove leading dash
    .trim() || name; // Fallback to original if empty
};

export function EmployeeSidebar({
  offices,
  selectedOfficeId,
  statusFilters,
  statusCounts,
  onOfficeSelect,
  onStatusToggle,
}: EmployeeSidebarProps) {
  return (
    <aside className="w-64 shrink-0 space-y-6">
      {/* Office filter */}
      <div>
        <div className="flex items-center gap-2 mb-3">
          <Building2 className="h-4 w-4 text-muted-foreground" />
          <h3 className="font-medium text-sm">Kontorer</h3>
        </div>
        
        <div className="space-y-1">
          <button
            onClick={() => onOfficeSelect(null)}
            className={cn(
              "w-full text-left px-3 py-2 rounded-md text-sm transition-colors",
              selectedOfficeId === null
                ? "bg-primary text-primary-foreground"
                : "hover:bg-muted"
            )}
          >
            Alle kontorer
          </button>
          
          {offices.map((office) => (
            <button
              key={office.id}
              onClick={() => onOfficeSelect(office.id)}
              className={cn(
                "w-full text-left px-3 py-2 rounded-md text-sm transition-colors flex items-center justify-between gap-2",
                selectedOfficeId === office.id
                  ? "bg-primary text-primary-foreground"
                  : "hover:bg-muted"
              )}
            >
              <div className="flex items-center gap-2 min-w-0">
                <div 
                  className="w-2 h-2 rounded-full shrink-0"
                  style={{ backgroundColor: office.color }}
                />
                <span className="truncate">{shortenOfficeName(office.name)}</span>
              </div>
              <span className={cn(
                "text-xs shrink-0",
                selectedOfficeId === office.id 
                  ? "text-primary-foreground/70" 
                  : "text-muted-foreground"
              )}>
                ({office.employee_count})
              </span>
            </button>
          ))}
        </div>
      </div>

      <Separator />

      {/* Status filter */}
      <div>
        <div className="flex items-center gap-2 mb-3">
          <Filter className="h-4 w-4 text-muted-foreground" />
          <h3 className="font-medium text-sm">Status</h3>
        </div>

        <div className="space-y-3">
          {(Object.keys(statusLabels) as EmployeeStatus[]).map((status) => (
            <div key={status} className="flex items-center space-x-2">
              <Checkbox
                id={`status-${status}`}
                checked={statusFilters.includes(status)}
                onCheckedChange={() => onStatusToggle(status)}
              />
              <Label 
                htmlFor={`status-${status}`} 
                className="cursor-pointer text-sm flex items-center justify-between flex-1"
              >
                <span>{statusLabels[status]}</span>
                <span className="text-muted-foreground text-xs">
                  ({statusCounts[status] || 0})
                </span>
              </Label>
            </div>
          ))}
        </div>
      </div>
    </aside>
  );
}
