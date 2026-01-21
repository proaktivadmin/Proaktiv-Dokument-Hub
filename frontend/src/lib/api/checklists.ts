/**
 * Checklists API Client
 */

import { apiClient } from './config';
import type { 
  ChecklistTemplate,
  ChecklistInstanceWithDetails,
  ChecklistInstanceListResponse,
  ChecklistItem,
  ChecklistType,
  ChecklistStatus 
} from '@/types/v3';

export interface ChecklistTemplateListParams {
  type?: ChecklistType;
  is_active?: boolean;
}

export interface ChecklistInstanceListParams {
  employee_id?: string;
  status?: ChecklistStatus;
  skip?: number;
  limit?: number;
}

export const checklistsApi = {
  // Templates
  async listTemplates(params?: ChecklistTemplateListParams): Promise<{ items: ChecklistTemplate[]; total: number }> {
    const searchParams = new URLSearchParams();
    if (params?.type) searchParams.set('type', params.type);
    if (params?.is_active !== undefined) {
      searchParams.set('is_active', String(params.is_active));
    }
    
    const query = searchParams.toString();
    const response = await apiClient.get(`/checklists/templates${query ? `?${query}` : ''}`);
    return response.data;
  },

  async getTemplate(id: string): Promise<ChecklistTemplate> {
    const response = await apiClient.get(`/checklists/templates/${id}`);
    return response.data;
  },

  async createTemplate(data: {
    name: string;
    description?: string;
    type: ChecklistType;
    items: ChecklistItem[];
  }): Promise<ChecklistTemplate> {
    const response = await apiClient.post('/checklists/templates', data);
    return response.data;
  },

  async updateTemplate(id: string, data: {
    name?: string;
    description?: string;
    items?: ChecklistItem[];
    is_active?: boolean;
  }): Promise<ChecklistTemplate> {
    const response = await apiClient.put(`/checklists/templates/${id}`, data);
    return response.data;
  },

  async deleteTemplate(id: string): Promise<void> {
    await apiClient.delete(`/checklists/templates/${id}`);
  },

  // Instances
  async listInstances(params?: ChecklistInstanceListParams): Promise<ChecklistInstanceListResponse> {
    const searchParams = new URLSearchParams();
    if (params?.employee_id) searchParams.set('employee_id', params.employee_id);
    if (params?.status) searchParams.set('status', params.status);
    if (params?.skip) searchParams.set('skip', String(params.skip));
    if (params?.limit) searchParams.set('limit', String(params.limit));
    
    const query = searchParams.toString();
    const response = await apiClient.get(`/checklists/instances${query ? `?${query}` : ''}`);
    return response.data;
  },

  async getInstance(id: string): Promise<ChecklistInstanceWithDetails> {
    const response = await apiClient.get(`/checklists/instances/${id}`);
    return response.data;
  },

  async assignToEmployee(data: {
    template_id: string;
    employee_id: string;
    due_date?: string;
  }): Promise<ChecklistInstanceWithDetails> {
    const response = await apiClient.post('/checklists/instances', data);
    return response.data;
  },

  async updateProgress(
    instanceId: string, 
    itemsCompleted: string[]
  ): Promise<ChecklistInstanceWithDetails> {
    const response = await apiClient.put(`/checklists/instances/${instanceId}`, { 
      items_completed: itemsCompleted 
    });
    return response.data;
  },

  async toggleItem(
    instanceId: string,
    itemName: string,
    completed: boolean
  ): Promise<ChecklistInstanceWithDetails> {
    const response = await apiClient.post(`/checklists/instances/${instanceId}/toggle`, {
      item_name: itemName,
      completed,
    });
    return response.data;
  },

  async completeChecklist(instanceId: string): Promise<ChecklistInstanceWithDetails> {
    const response = await apiClient.post(`/checklists/instances/${instanceId}/complete`);
    return response.data;
  },

  async cancelChecklist(instanceId: string): Promise<ChecklistInstanceWithDetails> {
    const response = await apiClient.post(`/checklists/instances/${instanceId}/cancel`);
    return response.data;
  },

  // Stats
  async getOverdueInstances(): Promise<{
    count: number;
    instances: ChecklistInstanceWithDetails[];
  }> {
    const response = await apiClient.get('/checklists/instances/overdue');
    return response.data;
  },
};
