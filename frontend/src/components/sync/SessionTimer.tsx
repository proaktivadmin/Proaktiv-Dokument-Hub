"use client";

import { useEffect, useState } from "react";
import { Clock } from "lucide-react";
import { Badge } from "@/components/ui/badge";

interface SessionTimerProps {
  expiresAt: string;
}

const ONE_HOUR_MS = 60 * 60 * 1000;

export function SessionTimer({ expiresAt }: SessionTimerProps) {
  const [remainingMs, setRemainingMs] = useState(() => {
    return new Date(expiresAt).getTime() - Date.now();
  });

  useEffect(() => {
    const interval = setInterval(() => {
      setRemainingMs(new Date(expiresAt).getTime() - Date.now());
    }, 60000);
    return () => clearInterval(interval);
  }, [expiresAt]);

  if (Number.isNaN(remainingMs)) {
    return null;
  }

  if (remainingMs <= 0) {
    return (
      <Badge variant="destructive" className="flex items-center gap-1">
        <Clock className="h-3 w-3" />
        Utløpt
      </Badge>
    );
  }

  const hours = Math.floor(remainingMs / ONE_HOUR_MS);
  const minutes = Math.floor((remainingMs % ONE_HOUR_MS) / 60000);
  const isWarning = remainingMs <= ONE_HOUR_MS;

  return (
    <Badge
      variant="secondary"
      className={isWarning ? "bg-amber-500/10 text-amber-600" : undefined}
    >
      <Clock className="mr-1 h-3 w-3" />
      Utløper om {hours}t {minutes}m
    </Badge>
  );
}
