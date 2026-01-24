"use client";

import { MapPin, Users, Phone, Mail, MoreVertical, Building } from "lucide-react";
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
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import type { OfficeWithStats, EmployeeWithOffice } from "@/types/v3";
import { resolveApiUrl, resolveAvatarUrl } from "@/lib/api/config";

interface OfficeCardProps {
  office: OfficeWithStats;
  employees?: EmployeeWithOffice[];
  onClick: () => void;
  onEdit?: () => void;
  onDeactivate?: () => void;
  onEmployeeClick?: (employee: EmployeeWithOffice) => void;
}

export function OfficeCard({ office, employees = [], onClick, onEdit, onDeactivate, onEmployeeClick }: OfficeCardProps) {
  const activeEmployees = employees.filter(e => e.status === 'active').slice(0, 6);
  // Prefer banner_image_url, fall back to profile_image_url
  const bannerImage = office.banner_image_url || office.profile_image_url;
  const statusIndicatorClass = office.is_active ? "bg-emerald-500" : "bg-red-500";
  
  return (
    <Card 
      className="group cursor-pointer hover:shadow-card-hover hover:-translate-y-0.5 transition-all duration-slow overflow-hidden"
      onClick={onClick}
    >
      {/* Banner Image */}
      {bannerImage ? (
        <div className="relative h-40 w-full overflow-hidden">
          <img 
            src={resolveApiUrl(bannerImage) ?? bannerImage} 
            alt={office.name}
            className="w-full h-full object-cover object-top group-hover:scale-105 transition-transform duration-300"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/20 to-transparent" />

          <div
            className={`absolute top-2 right-2 h-3 w-3 rounded-full ring-2 ring-white/80 ${statusIndicatorClass}`}
            title={office.is_active ? "Aktiv" : "Inaktiv"}
          />
          
          {/* City badge on banner */}
          {office.city && (
            <div className="absolute bottom-2 left-2">
              <Badge variant="secondary" className="bg-white/90 text-slate-900 backdrop-blur-sm">
                <MapPin className="h-3 w-3 mr-1" />
                {office.city}
              </Badge>
            </div>
          )}
        </div>
      ) : (
        <div 
          className="relative h-40 w-full"
          style={{ backgroundColor: office.color }}
        >
          <div className="absolute inset-0 bg-linear-to-br from-white/10 to-transparent" />

          <div
            className={`absolute top-2 right-2 h-3 w-3 rounded-full ring-2 ring-white/80 ${statusIndicatorClass}`}
            title={office.is_active ? "Aktiv" : "Inaktiv"}
          />
          
          {/* City badge */}
          {office.city && (
            <div className="absolute bottom-2 left-2">
              <Badge variant="secondary" className="bg-white/90 text-slate-900 backdrop-blur-sm">
                <MapPin className="h-3 w-3 mr-1" />
                {office.city}
              </Badge>
            </div>
          )}
        </div>
      )}

      <CardContent className="p-4">
        <div className="flex items-start justify-between mb-3">
          <div className="flex-1 min-w-0">
            {office.legal_name && office.legal_name !== office.name ? (
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <h3 className="font-semibold text-lg mb-1 group-hover:text-primary transition-colors truncate cursor-help">
                      {office.name}
                    </h3>
                  </TooltipTrigger>
                  <TooltipContent side="top" className="max-w-xs">
                    <div className="flex items-center gap-1.5 text-xs">
                      <Building className="h-3 w-3" />
                      <span>Juridisk navn: {office.legal_name}</span>
                    </div>
                    {office.organization_number && (
                      <div className="text-xs text-muted-foreground mt-1">
                        Org.nr: {office.organization_number}
                      </div>
                    )}
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>
            ) : (
              <h3 className="font-semibold text-lg mb-1 group-hover:text-primary transition-colors truncate">
                {office.name}
              </h3>
            )}
          </div>
          
          <DropdownMenu>
            <DropdownMenuTrigger asChild onClick={(e) => e.stopPropagation()}>
              <Button variant="ghost" size="icon" className="h-8 w-8 opacity-0 group-hover:opacity-100 shrink-0">
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

        {/* Employee count with avatars */}
        <div className="flex items-center gap-3 mb-3">
          <div className="flex items-center gap-1.5 text-sm text-muted-foreground">
            <Users className="h-4 w-4" />
            <span>{office.employee_count} ansatte</span>
            {office.active_employee_count < office.employee_count && (
              <span className="text-xs text-amber-600">
                ({office.active_employee_count} aktive)
              </span>
            )}
          </div>
        </div>

        {/* Employee avatars */}
        {activeEmployees.length > 0 && (
          <div className="flex items-center gap-2 mb-3 pb-3 border-b">
            <div className="flex -space-x-2">
              {activeEmployees.map((emp) => (
                <Avatar 
                  key={emp.id}
                  className="h-8 w-8 border-2 border-background cursor-pointer hover:scale-110 transition-transform duration-fast ease-standard"
                  onClick={(e) => {
                    e.stopPropagation();
                    onEmployeeClick?.(emp);
                  }}
                >
                  <AvatarImage src={resolveAvatarUrl(emp.profile_image_url, 64)} alt={emp.full_name} />
                  <AvatarFallback 
                    className="text-xs font-medium text-white"
                    style={{ backgroundColor: office.color }}
                  >
                    {emp.initials}
                  </AvatarFallback>
                </Avatar>
              ))}
            </div>
            {office.employee_count > 6 && (
              <span className="text-xs text-muted-foreground">
                +{office.employee_count - 6} flere
              </span>
            )}
          </div>
        )}

        {/* Sub-offices (Næring, Næringsoppgjør) */}
        {office.sub_offices && office.sub_offices.length > 0 && (
          <div className="mb-3 pb-3 border-b">
            <p className="text-xs text-muted-foreground mb-2">Avdelinger</p>
            <div className="flex flex-wrap gap-1">
              {office.sub_offices.map((sub) => (
                <span
                  key={sub.id}
                  className="px-2 py-0.5 text-xs rounded bg-muted text-muted-foreground"
                >
                  {sub.name.replace(office.name + ' - ', '').replace(office.name + ' ', '')}
                  {sub.employee_count > 0 && ` (${sub.employee_count})`}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Contact info */}
        {(office.phone || office.email) && (
          <div className="flex items-center gap-4 text-xs text-muted-foreground">
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
