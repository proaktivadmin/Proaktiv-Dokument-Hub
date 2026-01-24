"use client";

import { Phone, Mail, AlertTriangle, MoreVertical, Cloud, FileSignature } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Checkbox } from "@/components/ui/checkbox";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import type { EmployeeWithOffice, EmployeeStatus } from "@/types/v3";
import { resolveAvatarUrl } from "@/lib/api/config";
import { cn } from "@/lib/utils";

interface EmployeeCardProps {
  employee: EmployeeWithOffice;
  showOffice?: boolean;
  onClick: () => void;
  onEdit?: () => void;
  onStartOffboarding?: () => void;
  onDeactivate?: () => void;
  // Selection props
  selectable?: boolean;
  selected?: boolean;
  onSelectChange?: (selected: boolean) => void;
  // Entra sync props
  entraConnected?: boolean;
  onEntraSync?: () => void;
  onSignaturePreview?: () => void;
}

const statusConfig: Record<EmployeeStatus, { label: string; variant: "default" | "secondary" | "destructive" | "outline"; className: string }> = {
  active: { label: "Aktiv", variant: "default", className: "bg-emerald-500/10 text-emerald-600 hover:bg-emerald-500/20" },
  onboarding: { label: "Onboarding", variant: "default", className: "bg-sky-500/10 text-sky-600 hover:bg-sky-500/20" },
  offboarding: { label: "Offboarding", variant: "default", className: "bg-amber-500/10 text-amber-600 hover:bg-amber-500/20" },
  inactive: { label: "Inaktiv", variant: "secondary", className: "" },
};

export function EmployeeCard({
  employee,
  showOffice = false,
  onClick,
  onEdit,
  onStartOffboarding,
  onDeactivate,
  selectable = false,
  selected = false,
  onSelectChange,
  entraConnected = false,
  onEntraSync,
  onSignaturePreview,
}: EmployeeCardProps) {
  const status = statusConfig[employee.status];

  return (
    <Card
      className={cn(
        "group cursor-pointer hover:shadow-card-hover hover:-translate-y-0.5 transition-all duration-slow",
        selected && "ring-2 ring-primary shadow-glow"
      )}
      onClick={onClick}
    >
      <CardContent className="p-4">
        <div className="flex items-start gap-3">
          {/* Selection checkbox */}
          {selectable && (
            <div
              className="shrink-0 pt-1"
              onClick={(e) => e.stopPropagation()}
            >
              <Checkbox
                checked={selected}
                onCheckedChange={(checked) => onSelectChange?.(checked === true)}
              />
            </div>
          )}

          {/* Avatar with profile image */}
          <Avatar className="w-12 h-12 shrink-0 transition-transform duration-fast ease-standard hover:scale-105">
            <AvatarImage src={resolveAvatarUrl(employee.profile_image_url, 128)} alt={employee.full_name} />
            <AvatarFallback 
              className="text-white font-semibold"
              style={{ backgroundColor: employee.office.color }}
            >
              {employee.initials}
            </AvatarFallback>
          </Avatar>

          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between gap-2">
              <div>
                <h3 className="font-semibold group-hover:text-primary transition-colors truncate">
                  {employee.full_name}
                </h3>
                {employee.title && (
                  <p className="text-sm text-muted-foreground truncate">{employee.title}</p>
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
                    Se profil
                  </DropdownMenuItem>
                  {onEdit && (
                    <DropdownMenuItem onClick={(e) => { e.stopPropagation(); onEdit(); }}>
                      Rediger
                    </DropdownMenuItem>
                  )}
                  {/* Entra ID sync options */}
                  {entraConnected && (
                    <>
                      <DropdownMenuSeparator />
                      {onEntraSync && (
                        <DropdownMenuItem onClick={(e) => { e.stopPropagation(); onEntraSync(); }}>
                          <Cloud className="h-4 w-4 mr-2" />
                          Synkroniser til Entra ID
                        </DropdownMenuItem>
                      )}
                      {onSignaturePreview && (
                        <DropdownMenuItem onClick={(e) => { e.stopPropagation(); onSignaturePreview(); }}>
                          <FileSignature className="h-4 w-4 mr-2" />
                          Forhåndsvis signatur
                        </DropdownMenuItem>
                      )}
                    </>
                  )}
                  <DropdownMenuSeparator />
                  {onStartOffboarding && employee.status === "active" && (
                    <DropdownMenuItem
                      className="text-amber-600"
                      onClick={(e) => { e.stopPropagation(); onStartOffboarding(); }}
                    >
                      Start offboarding
                    </DropdownMenuItem>
                  )}
                  {onDeactivate && (
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

            <div className="flex items-center gap-2 mt-2 flex-wrap">
              <Badge variant={status.variant} className={status.className}>
                {status.label}
              </Badge>
              {showOffice && (
                <Badge variant="outline" style={{ borderColor: employee.office.color, color: employee.office.color }}>
                  {employee.office.short_code}
                </Badge>
              )}
              {employee.system_roles && employee.system_roles.map((role, idx) => (
                <Badge key={idx} variant="secondary" className="bg-slate-100 text-slate-600">
                  {role}
                </Badge>
              ))}
            </div>

            {/* Offboarding warning */}
            {employee.status === "offboarding" && employee.days_until_end !== null && (
              <div className="flex items-center gap-1.5 mt-2 text-xs text-amber-600">
                <AlertTriangle className="h-3 w-3" />
                <span>
                  {employee.days_until_end <= 0
                    ? "Sluttdato passert"
                    : `${employee.days_until_end} dager igjen`}
                </span>
              </div>
            )}

            {/* Contact info */}
            {(employee.email || employee.phone) && (
              <div className="flex items-center gap-3 mt-2 text-xs text-muted-foreground">
                {employee.phone && (
                  <div className="flex items-center gap-1">
                    <Phone className="h-3 w-3" />
                    <span>{employee.phone}</span>
                  </div>
                )}
                {employee.email && (
                  <div className="flex items-center gap-1 truncate">
                    <Mail className="h-3 w-3" />
                    <span className="truncate">{employee.email}</span>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
