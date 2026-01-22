"use client";

import { useState, useEffect, useCallback } from 'react';
import { entraSyncApi } from '@/lib/api/entra-sync';
import type {
  EntraConnectionStatus,
  EntraSyncPreview,
  EntraSyncResult,
  EntraSyncBatchResult,
  SignaturePreview,
  SyncScope,
} from '@/types/entra-sync';

/**
 * Hook for Entra ID connection status
 */
export function useEntraStatus() {
  const [status, setStatus] = useState<EntraConnectionStatus | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await entraSyncApi.getStatus();
      setStatus(data);
    } catch (err) {
      console.error('[useEntraStatus] Error:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch status');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetch();
  }, [fetch]);

  return {
    status,
    isConnected: status?.connected ?? false,
    isEnabled: status?.enabled ?? false,
    isLoading,
    error,
    refetch: fetch,
  };
}

/**
 * Hook for syncing employees to Entra ID
 */
export function useEntraSync() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { isConnected, isEnabled, status } = useEntraStatus();

  /**
   * Get preview of what would change for an employee
   */
  const getPreview = useCallback(async (employeeId: string): Promise<EntraSyncPreview | null> => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await entraSyncApi.getPreview(employeeId);
      return data;
    } catch (err) {
      console.error('[useEntraSync] Preview error:', err);
      setError(err instanceof Error ? err.message : 'Failed to get preview');
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Get signature preview for an employee
   */
  const getSignaturePreview = useCallback(async (employeeId: string): Promise<SignaturePreview | null> => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await entraSyncApi.getSignaturePreview(employeeId);
      return data;
    } catch (err) {
      console.error('[useEntraSync] Signature preview error:', err);
      setError(err instanceof Error ? err.message : 'Failed to get signature preview');
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Sync a single employee to Entra ID
   */
  const pushEmployee = useCallback(async (
    employeeId: string,
    scope: SyncScope[] = ['profile', 'photo', 'signature'],
    dryRun: boolean = false
  ): Promise<EntraSyncResult | null> => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await entraSyncApi.pushEmployee(employeeId, { scope, dry_run: dryRun });
      return data;
    } catch (err) {
      console.error('[useEntraSync] Push error:', err);
      setError(err instanceof Error ? err.message : 'Failed to sync employee');
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Sync multiple employees to Entra ID
   */
  const pushBatch = useCallback(async (
    employeeIds: string[],
    scope: SyncScope[] = ['profile', 'photo', 'signature'],
    dryRun: boolean = false
  ): Promise<EntraSyncBatchResult | null> => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await entraSyncApi.pushBatch({ employee_ids: employeeIds, scope, dry_run: dryRun });
      return data;
    } catch (err) {
      console.error('[useEntraSync] Batch push error:', err);
      setError(err instanceof Error ? err.message : 'Failed to sync employees');
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);

  return {
    // Status
    isConnected,
    isEnabled,
    status,
    
    // Loading state
    isLoading,
    error,
    
    // Actions
    getPreview,
    getSignaturePreview,
    pushEmployee,
    pushBatch,
  };
}
