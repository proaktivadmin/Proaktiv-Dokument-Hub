"use client";

import { useState, useEffect } from "react";
import { HardDrive, WifiOff, Wifi, AlertTriangle } from "lucide-react";
import { StorageBrowser } from "@/components/storage";
import { storageApi } from "@/lib/api";
import { cn } from "@/lib/utils";

export default function StoragePage() {
  const [status, setStatus] = useState<{
    configured: boolean;
    connected: boolean;
    message: string;
  } | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    storageApi
      .getStatus()
      .then((data) => {
        setStatus(data);
      })
      .catch((err) => {
        setStatus({
          configured: false,
          connected: false,
          message: err instanceof Error ? err.message : "Kunne ikke sjekke status",
        });
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  const handleStatusChange = (connected: boolean) => {
    setStatus((prev) =>
      prev
        ? {
            ...prev,
            connected,
            message: connected
              ? "Tilkoblet nettverkslagring"
              : "Mistet tilkobling",
          }
        : null
    );
  };

  if (loading) {
    return (
      <div className="container mx-auto px-6 py-8">
        <div className="animate-pulse">
          <div className="h-8 bg-muted rounded w-48 mb-4"></div>
          <div className="h-4 bg-muted rounded w-96 mb-8"></div>
          <div className="h-96 bg-muted rounded"></div>
        </div>
      </div>
    );
  }

  if (!status?.configured) {
    return (
      <div className="container mx-auto px-6 py-8">
        <div className="max-w-md mx-auto text-center py-16">
          <div className="mx-auto w-16 h-16 rounded-full bg-amber-100 flex items-center justify-center mb-6">
            <AlertTriangle className="h-8 w-8 text-amber-600" />
          </div>
          <h1 className="text-2xl font-semibold mb-2">
            Lagring ikke konfigurert
          </h1>
          <p className="text-muted-foreground mb-6">
            WebDAV-tilkobling er ikke satt opp. Kontakt administrator for å
            konfigurere nettverkslagring.
          </p>
          <p className="text-sm text-muted-foreground bg-muted p-4 rounded-lg font-mono">
            Sett WEBDAV_URL, WEBDAV_USERNAME og WEBDAV_PASSWORD i miljøvariabler.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-6 py-8 h-[calc(100vh-80px)] flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-semibold flex items-center gap-3">
            <HardDrive className="h-6 w-6" />
            Nettverkslagring
          </h1>
          <p className="text-muted-foreground mt-1">
            Bla gjennom og administrer filer på proaktiv.no
          </p>
        </div>

        {/* Connection status */}
        <div
          className={cn(
            "flex items-center gap-2 px-3 py-1.5 rounded-full text-sm",
            status.connected
              ? "bg-green-100 text-green-700"
              : "bg-red-100 text-red-700"
          )}
        >
          {status.connected ? (
            <>
              <Wifi className="h-4 w-4" />
              Tilkoblet
            </>
          ) : (
            <>
              <WifiOff className="h-4 w-4" />
              Ikke tilkoblet
            </>
          )}
        </div>
      </div>

      {/* Browser */}
      <div className="flex-1 min-h-0">
        <StorageBrowser onStatusChange={handleStatusChange} />
      </div>
    </div>
  );
}
