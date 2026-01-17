/**
 * useInventoryStats Hook
 * 
 * Fetches Vitec template inventory sync statistics from the backend.
 */

import { useState, useEffect, useCallback } from 'react';
import { dashboardApi } from '@/lib/api/dashboard';
import type { InventoryStatsResponse } from '@/types/v2';

interface UseInventoryStatsReturn {
  data: InventoryStatsResponse | null;
  isLoading: boolean;
  error: string | null;
  refetch: () => void;
}

export function useInventoryStats(missingLimit: number = 5): UseInventoryStatsReturn {
  const [data, setData] = useState<InventoryStatsResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchInventory = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await dashboardApi.getInventoryStats(missingLimit);
      setData(response);
    } catch (err) {
      console.error('Error fetching inventory stats:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch inventory stats');
    } finally {
      setIsLoading(false);
    }
  }, [missingLimit]);

  useEffect(() => {
    fetchInventory();
  }, [fetchInventory]);

  return {
    data,
    isLoading,
    error,
    refetch: fetchInventory
  };
}
