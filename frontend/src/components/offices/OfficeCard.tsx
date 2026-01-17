"use client";

import { Building2, MapPin, Users, Phone, Mail, MoreVertical } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import type { OfficeWithStats } from "@/types/v3";

interface OfficeCardProps {
  office: OfficeWithStats;
  onClick: () => void;
  onEdit?: () => void;
  onDeactivate?: () => void;
}

export function OfficeCard({ office, onClick, onEdit, onDeactivate }: OfficeCardProps) {
  return (
    <Card 
      className="group cursor-pointer hover:shadow-md transition-all duration-200 border-l-4"
      style={{ borderLeftColor: office.color }}
      onClick={onClick}
    >
      <CardContent className="p-4">
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-2">
            <Badge 
              variant="outline" 
              className="font-mono text-xs"
              style={{ borderColor: office.color, color: office.color }}
            >
              {office.short_code}
            </Badge>
            <Badge 
              variant={office.is_active ? "default" : "secondary"}
              className={office.is_active ? "bg-green-500/10 text-green-600 hover:bg-green-500/20" : ""}
            >
              {office.is_active ? "Aktiv" : "Inaktiv"}
            </Badge>
          </div>
          
          <DropdownMenu>
            <DropdownMenuTrigger asChild onClick={(e) => e.stopPropagation()}>
              <Button variant="ghost" size="icon" className="h-8 w-8 opacity-0 group-hover:opacity-100">
                <MoreVertical className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={(e) => { e.stopPropagation(); onClick(); }}>
                Se detaljer
              </DropdownMenuItem>
              {onEdit && (
                <DropdownMenuItem onClick={(e) => { e.stopPropagation(); onEdit(); }}>
                  Rediger
                </DropdownMenuItem>
              )}
              <DropdownMenuSeparator />
              {onDeactivate && office.is_active && (
                <DropdownMenuItem 
                  className="text-destructive"
                  onClick={(e) => { e.stopPropagation(); onDeactivate(); }}
                >
                  Deaktiver
                </DropdownMenuItem>
              )}
            </DropdownMenuContent>
          </DropdownMenu>
        </div>

        <h3 className="font-semibold text-lg mb-1 group-hover:text-primary transition-colors">
          {office.name}
        </h3>

        {office.city && (
          <div className="flex items-center gap-1.5 text-sm text-muted-foreground mb-3">
            <MapPin className="h-3.5 w-3.5" />
            <span>{office.city}</span>
          </div>
        )}

        <div className="flex items-center gap-4 text-sm text-muted-foreground">
          <div className="flex items-center gap-1.5">
            <Users className="h-3.5 w-3.5" />
            <span>{office.employee_count} ansatte</span>
          </div>
          {office.active_employee_count < office.employee_count && (
            <span className="text-xs text-amber-600">
              ({office.active_employee_count} aktive)
            </span>
          )}
        </div>

        {(office.phone || office.email) && (
          <div className="mt-3 pt-3 border-t flex items-center gap-4 text-xs text-muted-foreground">
            {office.phone && (
              <div className="flex items-center gap-1">
                <Phone className="h-3 w-3" />
                <span>{office.phone}</span>
              </div>
            )}
            {office.email && (
              <div className="flex items-center gap-1 truncate">
                <Mail className="h-3 w-3" />
                <span className="truncate">{office.email}</span>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
