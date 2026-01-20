"use client";

import { useState, useEffect, useCallback } from 'react';
import { employeesApi, type EmployeeListParams } from '@/lib/api/employees';
import type { EmployeeWithOffice, EmployeeStatus } from '@/types/v3';

export function useEmployees(params?: EmployeeListParams) {
  const [employees, setEmployees] = useState<EmployeeWithOffice[]>([]);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await employeesApi.list(params);
      setEmployees(data.items);
      setTotal(data.total);
    } catch (err) {
      console.error('[useEmployees] Error:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch employees');
    } finally {
      setIsLoading(false);
    }
  }, [
    params?.office_id,
    JSON.stringify(params?.status),
    params?.role,
    params?.is_featured,
    params?.search,
    params?.skip,
    params?.limit,
  ]);


  useEffect(() => {
    fetch();
  }, [fetch]);

  // Group by status
  const byStatus = employees.reduce((acc, emp) => {
    const status = emp.status;
    if (!acc[status]) acc[status] = [];
    acc[status].push(emp);
    return acc;
  }, {} as Record<EmployeeStatus, EmployeeWithOffice[]>);

  // Count by status
  const statusCounts: Record<EmployeeStatus, number> = {
    active: byStatus.active?.length || 0,
    onboarding: byStatus.onboarding?.length || 0,
    offboarding: byStatus.offboarding?.length || 0,
    inactive: byStatus.inactive?.length || 0,
  };

  return {
    employees,
    total,
    byStatus,
    statusCounts,
    isLoading,
    error,
    refetch: fetch
  };
}

export function useEmployee(id: string | null) {
  const [employee, setEmployee] = useState<EmployeeWithOffice | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    if (!id) {
      setEmployee(null);
      return;
    }

    setIsLoading(true);
    setError(null);
    try {
      const data = await employeesApi.get(id);
      setEmployee(data);
    } catch (err) {
      console.error('[useEmployee] Error:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch employee');
    } finally {
      setIsLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetch();
  }, [fetch]);

  return { employee, isLoading, error, refetch: fetch };
}
