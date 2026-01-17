/**
 * Employees API Client
 */

import { apiClient } from './config';
import type { 
  EmployeeWithOffice, 
  EmployeeCreatePayload, 
  EmployeeUpdatePayload,
  EmployeeListResponse,
  StartOffboardingPayload,
  EmployeeStatus 
} from '@/types/v3';

export interface EmployeeListParams {
  office_id?: string;
  status?: EmployeeStatus | EmployeeStatus[];
  skip?: number;
  limit?: number;
}

export const employeesApi = {
  async list(params?: EmployeeListParams): Promise<EmployeeListResponse> {
    const searchParams = new URLSearchParams();
    if (params?.office_id) searchParams.set('office_id', params.office_id);
    if (params?.status) {
      const statuses = Array.isArray(params.status) ? params.status : [params.status];
      statuses.forEach(s => searchParams.append('status', s));
    }
    if (params?.skip) searchParams.set('skip', String(params.skip));
    if (params?.limit) searchParams.set('limit', String(params.limit));
    
    const query = searchParams.toString();
    const response = await apiClient.get(`/employees${query ? `?${query}` : ''}`);
    return response.data;
  },

  async get(id: string): Promise<EmployeeWithOffice> {
    const response = await apiClient.get(`/employees/${id}`);
    return response.data;
  },

  async create(data: EmployeeCreatePayload): Promise<EmployeeWithOffice> {
    const response = await apiClient.post('/employees', data);
    return response.data;
  },

  async update(id: string, data: EmployeeUpdatePayload): Promise<EmployeeWithOffice> {
    const response = await apiClient.put(`/employees/${id}`, data);
    return response.data;
  },

  async startOffboarding(id: string, data: StartOffboardingPayload): Promise<EmployeeWithOffice> {
    const response = await apiClient.post(`/employees/${id}/offboarding`, data);
    return response.data;
  },

  async deactivate(id: string): Promise<EmployeeWithOffice> {
    const response = await apiClient.delete(`/employees/${id}`);
    return response.data;
  },

  async getOffboardingDue(): Promise<{
    count: number;
    employees: EmployeeWithOffice[];
  }> {
    const response = await apiClient.get('/employees/offboarding/due');
    return response.data;
  },
};
