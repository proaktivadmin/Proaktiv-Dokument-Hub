"use client";

import { Building2, Plus, Search } from "lucide-react";
import { useState } from "react";
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
import type { OfficeWithStats } from "@/types/v3";

interface OfficeGridProps {
  offices: OfficeWithStats[];
  cities: string[];
  isLoading: boolean;
  onOfficeClick: (office: OfficeWithStats) => void;
  onCreateNew?: () => void;
  onEdit?: (office: OfficeWithStats) => void;
  onDeactivate?: (office: OfficeWithStats) => void;
}

export function OfficeGrid({
  offices,
  cities,
  isLoading,
  onOfficeClick,
  onCreateNew,
  onEdit,
  onDeactivate,
}: OfficeGridProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [cityFilter, setCityFilter] = useState<string>("all");
  const [statusFilter, setStatusFilter] = useState<string>("all");

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

    // Status filter
    if (statusFilter === "active" && !office.is_active) return false;
    if (statusFilter === "inactive" && office.is_active) return false;

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

        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-[140px]">
            <SelectValue placeholder="Alle statuser" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Alle statuser</SelectItem>
            <SelectItem value="active">Aktive</SelectItem>
            <SelectItem value="inactive">Inaktive</SelectItem>
          </SelectContent>
        </Select>

        {onCreateNew && (
          <Button onClick={onCreateNew} className="ml-auto">
            <Plus className="h-4 w-4 mr-2" />
            Nytt kontor
          </Button>
        )}
      </div>

      {/* Grid */}
      {filteredOffices.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <Building2 className="h-12 w-12 text-muted-foreground/50 mb-4" />
          <h3 className="text-lg font-medium mb-1">Ingen kontorer funnet</h3>
          <p className="text-sm text-muted-foreground mb-4">
            {searchQuery || cityFilter !== "all" || statusFilter !== "all"
              ? "Prøv å endre søket eller filtrene"
              : "Kom i gang ved å opprette ditt første kontor"}
          </p>
          {onCreateNew && !searchQuery && cityFilter === "all" && statusFilter === "all" && (
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
              onClick={() => onOfficeClick(office)}
              onEdit={onEdit ? () => onEdit(office) : undefined}
              onDeactivate={onDeactivate ? () => onDeactivate(office) : undefined}
            />
          ))}
        </div>
      )}
    </div>
  );
}
