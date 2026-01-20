"use client";

import { useEffect, useState } from "react";
import { CheckCircle, XCircle, AlertTriangle, Loader2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { vitecApi, VitecStatus } from "@/lib/api";

interface VitecConnectionStatusProps {
  /** Callback when connection status changes */
  onStatusChange?: (connected: boolean) => void;
  /** Show additional details like installation ID */
  showDetails?: boolean;
  /** Compact mode for inline display */
  compact?: boolean;
}

/**
 * VitecConnectionStatus - Displays Vitec Hub API connection status
 * 
 * Shows one of three states:
 * - Not configured (yellow): Credentials missing in backend
 * - Connected (green): API test succeeded
 * - Error (red): API test failed
 */
export function VitecConnectionStatus({
  onStatusChange,
  showDetails = false,
  compact = false,
}: VitecConnectionStatusProps) {
  const [status, setStatus] = useState<VitecStatus | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    vitecApi
      .getStatus()
      .then((s) => {
        setStatus(s);
        onStatusChange?.(s.connected);
      })
      .catch(() => {
        const errorStatus: VitecStatus = {
          configured: false,
          connected: false,
          error: "Kunne ikke sjekke tilkoblingsstatus",
          installation_id: null,
          available_methods: null,
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
        {!compact && <span>Sjekker Vitec...</span>}
      </Badge>
    );
  }

  if (!status) {
    return null;
  }

  // Not configured
  if (!status.configured) {
    return (
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger asChild>
            <Badge variant="outline" className="gap-1 border-yellow-500 text-yellow-600">
              <AlertTriangle className="h-3 w-3" />
              {!compact && <span>Vitec ikke konfigurert</span>}
            </Badge>
          </TooltipTrigger>
          <TooltipContent side="bottom" className="max-w-xs">
            <p className="text-sm">
              {status.error || "Vitec Hub-legitimasjon er ikke konfigurert i backend."}
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
            <Badge variant="outline" className="gap-1 border-green-500 text-green-600">
              <CheckCircle className="h-3 w-3" />
              {!compact && <span>Vitec tilkoblet</span>}
            </Badge>
          </TooltipTrigger>
          <TooltipContent side="bottom" className="max-w-xs">
            <div className="text-sm space-y-1">
              <p>Vitec Hub API er tilgjengelig.</p>
              {showDetails && status.installation_id && (
                <p className="text-muted-foreground">
                  Installasjon: {status.installation_id}
                </p>
              )}
              {showDetails && status.available_methods && status.available_methods.length > 0 && (
                <p className="text-muted-foreground">
                  Tilgjengelige metoder: {status.available_methods.length}
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
            {!compact && <span>Vitec feil</span>}
          </Badge>
        </TooltipTrigger>
        <TooltipContent side="bottom" className="max-w-xs">
          <p className="text-sm text-red-600">
            {status.error || "Kunne ikke koble til Vitec Hub API."}
          </p>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}
