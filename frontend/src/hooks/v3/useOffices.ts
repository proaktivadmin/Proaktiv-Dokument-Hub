"use client";

import { useState, useEffect, useCallback } from 'react';
import { officesApi, type OfficeListParams } from '@/lib/api/offices';
import type { OfficeWithStats } from '@/types/v3';

export function useOffices(params?: OfficeListParams) {
  const [offices, setOffices] = useState<OfficeWithStats[]>([]);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await officesApi.list(params);
      setOffices(data.items);
      setTotal(data.total);
    } catch (err) {
      console.error('[useOffices] Error:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch offices');
    } finally {
      setIsLoading(false);
    }
  }, [params?.city, params?.is_active, params?.office_type, params?.include_sub, params?.skip, params?.limit]);

  useEffect(() => {
    fetch();
  }, [fetch]);

  // Group by city for filtering
  const cities = Array.from(new Set(offices.map(o => o.city).filter(Boolean))) as string[];

  return { 
    offices, 
    total,
    cities,
    isLoading, 
    error, 
    refetch: fetch 
  };
}

export function useOffice(id: string | null) {
  const [office, setOffice] = useState<OfficeWithStats | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    if (!id) {
      setOffice(null);
      return;
    }

    setIsLoading(true);
    setError(null);
    try {
      const data = await officesApi.get(id);
      setOffice(data);
    } catch (err) {
      console.error('[useOffice] Error:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch office');
    } finally {
      setIsLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetch();
  }, [fetch]);

  return { office, isLoading, error, refetch: fetch };
}
