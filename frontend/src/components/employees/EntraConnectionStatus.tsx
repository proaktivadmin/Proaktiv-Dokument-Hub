"use client";

import { useEffect, useState } from "react";
import { XCircle, AlertTriangle, Loader2, Cloud } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { entraSyncApi } from "@/lib/api";
import type { EntraConnectionStatus as EntraStatus } from "@/types/entra-sync";

interface EntraConnectionStatusProps {
  /** Callback when connection status changes */
  onStatusChange?: (connected: boolean) => void;
  /** Show additional details */
  showDetails?: boolean;
  /** Compact mode for inline display */
  compact?: boolean;
}

/**
 * EntraConnectionStatus - Displays Microsoft Entra ID connection status
 * 
 * Shows one of three states:
 * - Not configured (yellow): Credentials missing in backend
 * - Connected (green): Entra ID is configured
 * - Error (red): Configuration error
 */
export function EntraConnectionStatus({
  onStatusChange,
  showDetails = false,
  compact = false,
}: EntraConnectionStatusProps) {
  const [status, setStatus] = useState<EntraStatus | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    entraSyncApi
      .getStatus()
      .then((s) => {
        setStatus(s);
        onStatusChange?.(s.connected);
      })
      .catch(() => {
        const errorStatus: EntraStatus = {
          enabled: false,
          connected: false,
          error: "Kunne ikke sjekke Entra ID-status",
          tenant_id: null,
          client_id: null,
        };
        setStatus(errorStatus);
        onStatusChange?.(false);
      })
      .finally(() => setLoading(false));
  }, [onStatusChange]);

  if (loading) {
    return (
      <Badge variant="outline" className="gap-1">
        <Loader2 className="h-3 w-3 animate-spin" />
        {!compact && <span>Sjekker Entra ID...</span>}
      </Badge>
    );
  }

  if (!status) {
    return null;
  }

  // Not configured
  if (!status.enabled) {
    return (
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger asChild>
            <Badge variant="outline" className="gap-1 border-yellow-500 text-yellow-600">
              <AlertTriangle className="h-3 w-3" />
              {!compact && <span>Entra ID ikke konfigurert</span>}
            </Badge>
          </TooltipTrigger>
          <TooltipContent side="bottom" className="max-w-xs">
            <p className="text-sm">
              {status.error || "Entra ID-legitimasjon er ikke konfigurert. Sett ENTRA_TENANT_ID og ENTRA_CLIENT_ID."}
            </p>
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>
    );
  }

  // Connected
  if (status.connected) {
    return (
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger asChild>
            <Badge variant="outline" className="gap-1 border-sky-500 text-sky-600">
              <Cloud className="h-3 w-3" />
              {!compact && <span>Entra ID</span>}
            </Badge>
          </TooltipTrigger>
          <TooltipContent side="bottom" className="max-w-xs">
            <div className="text-sm space-y-1">
              <p>Microsoft Entra ID er konfigurert.</p>
              {showDetails && status.tenant_id && (
                <p className="text-muted-foreground">
                  Tenant: {status.tenant_id}
                </p>
              )}
            </div>
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>
    );
  }

  // Error (configured but not connected)
  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <Badge variant="outline" className="gap-1 border-red-500 text-red-600">
            <XCircle className="h-3 w-3" />
            {!compact && <span>Entra ID feil</span>}
          </Badge>
        </TooltipTrigger>
        <TooltipContent side="bottom" className="max-w-xs">
          <p className="text-sm text-red-600">
            {status.error || "Kunne ikke koble til Microsoft Entra ID."}
          </p>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}
