"use client";

import { useState, useEffect, useCallback } from 'react';
import { checklistsApi, type ChecklistTemplateListParams, type ChecklistInstanceListParams } from '@/lib/api/checklists';
import type { ChecklistTemplate, ChecklistInstanceWithDetails, ChecklistStatus } from '@/types/v3';

export function useChecklistTemplates(params?: ChecklistTemplateListParams) {
  const [templates, setTemplates] = useState<ChecklistTemplate[]>([]);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await checklistsApi.listTemplates(params);
      setTemplates(data.items);
      setTotal(data.total);
    } catch (err) {
      console.error('[useChecklistTemplates] Error:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch checklist templates');
    } finally {
      setIsLoading(false);
    }
  }, [params?.type, params?.is_active]);

  useEffect(() => {
    fetch();
  }, [fetch]);

  // Separate by type
  const onboardingTemplates = templates.filter(t => t.type === 'onboarding');
  const offboardingTemplates = templates.filter(t => t.type === 'offboarding');

  return { 
    templates, 
    total,
    onboardingTemplates,
    offboardingTemplates,
    isLoading, 
    error, 
    refetch: fetch 
  };
}

export function useChecklistInstances(params?: ChecklistInstanceListParams) {
  const [instances, setInstances] = useState<ChecklistInstanceWithDetails[]>([]);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await checklistsApi.listInstances(params);
      setInstances(data.items);
      setTotal(data.total);
    } catch (err) {
      console.error('[useChecklistInstances] Error:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch checklist instances');
    } finally {
      setIsLoading(false);
    }
  }, [params?.employee_id, params?.status, params?.skip, params?.limit]);

  useEffect(() => {
    fetch();
  }, [fetch]);

  // Group by status
  const byStatus = instances.reduce((acc, instance) => {
    const status = instance.status;
    if (!acc[status]) acc[status] = [];
    acc[status].push(instance);
    return acc;
  }, {} as Record<ChecklistStatus, ChecklistInstanceWithDetails[]>);

  // Overdue count
  const overdueCount = instances.filter(i => i.is_overdue).length;

  return { 
    instances, 
    total,
    byStatus,
    overdueCount,
    isLoading, 
    error, 
    refetch: fetch 
  };
}

export function useChecklistInstance(id: string | null) {
  const [instance, setInstance] = useState<ChecklistInstanceWithDetails | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    if (!id) {
      setInstance(null);
      return;
    }

    setIsLoading(true);
    setError(null);
    try {
      const data = await checklistsApi.getInstance(id);
      setInstance(data);
    } catch (err) {
      console.error('[useChecklistInstance] Error:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch checklist instance');
    } finally {
      setIsLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetch();
  }, [fetch]);

  const toggleItem = useCallback(async (itemName: string, completed: boolean) => {
    if (!id) return;
    try {
      const updated = await checklistsApi.toggleItem(id, itemName, completed);
      setInstance(updated);
      return updated;
    } catch (err) {
      console.error('[useChecklistInstance] Toggle error:', err);
      throw err;
    }
  }, [id]);

  return { instance, isLoading, error, refetch: fetch, toggleItem };
}
