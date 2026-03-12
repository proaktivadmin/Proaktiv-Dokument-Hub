"use client";

import { useEffect, useRef, useState } from "react";

import {
  buildReportCacheEventsStreamUrl,
  listReportCacheEvents,
  type ReportSalesSyncEvent,
} from "@/lib/api/reports";

interface UseReportCacheEventsOptions {
  enabled?: boolean;
  departmentId?: number;
  onEvent?: (event: ReportSalesSyncEvent) => void;
}

interface UseReportCacheEventsReturn {
  isConnected: boolean;
  latestEvent: ReportSalesSyncEvent | null;
  latestEventAt: Date | null;
  reconnectAttempt: number;
}

export function useReportCacheEvents(
  options: UseReportCacheEventsOptions = {}
): UseReportCacheEventsReturn {
  const { enabled = true, departmentId, onEvent } = options;
  const [isConnected, setIsConnected] = useState(false);
  const [latestEvent, setLatestEvent] = useState<ReportSalesSyncEvent | null>(null);
  const [latestEventAt, setLatestEventAt] = useState<Date | null>(null);
  const [reconnectAttempt, setReconnectAttempt] = useState(0);
  const lastSeenIdRef = useRef<number | null>(null);

  useEffect(() => {
    if (!enabled) {
      return;
    }

    let source: EventSource | null = null;
    let closed = false;
    let reconnectTimer: ReturnType<typeof setTimeout> | null = null;

    const connect = () => {
      const url = buildReportCacheEventsStreamUrl({
        department_id: departmentId,
        since_id: lastSeenIdRef.current ?? undefined,
        poll_interval_seconds: 2,
        max_seconds: 55,
      });
      source = new EventSource(url, { withCredentials: true });

      source.onopen = () => {
        setIsConnected(true);
        setReconnectAttempt(0);
      };

      const handleEvent = (raw: MessageEvent<string>) => {
        try {
          const parsed = JSON.parse(raw.data) as ReportSalesSyncEvent;
          if (typeof parsed.id === "number") {
            lastSeenIdRef.current = parsed.id;
          }
          setLatestEvent(parsed);
          setLatestEventAt(new Date());
          onEvent?.(parsed);
        } catch {
          // Ignore malformed event payloads.
        }
      };

      source.onmessage = handleEvent;
      source.addEventListener("cache_sync", (event) => handleEvent(event as MessageEvent<string>));

      source.onerror = () => {
        setIsConnected(false);
        source?.close();
        if (closed) return;
        setReconnectAttempt((prev) => {
          const next = Math.min(prev + 1, 8);
          const delayMs = Math.min(1000 * 2 ** next, 30000);
          reconnectTimer = setTimeout(connect, delayMs);
          return next;
        });
      };
    };

    const start = async () => {
      // Prime cursor from the latest known event to avoid replaying old history on connect.
      if (lastSeenIdRef.current == null) {
        try {
          const latest = await listReportCacheEvents({ department_id: departmentId, limit: 1 });
          const latestId = latest.at(0)?.id;
          if (typeof latestId === "number") {
            lastSeenIdRef.current = latestId;
          }
        } catch {
          // Non-fatal: stream connection will still work.
        }
      }
      connect();
    };

    void start();

    return () => {
      closed = true;
      if (reconnectTimer) clearTimeout(reconnectTimer);
      source?.close();
    };
  }, [enabled, departmentId, onEvent]);

  return {
    isConnected: enabled ? isConnected : false,
    latestEvent,
    latestEventAt,
    reconnectAttempt,
  };
}
