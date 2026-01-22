/**
 * Entra ID Sync API Client
 */

import { apiClient } from './config';
import type {
  EntraConnectionStatus,
  EntraSyncBatchRequest,
  EntraSyncBatchResult,
  EntraSyncPreview,
  EntraSyncRequest,
  EntraSyncResult,
  RoamingSignaturesStatus,
  SignaturePreview,
} from '@/types/entra-sync';

export const entraSyncApi = {
  /**
   * Get Entra ID connection status
   */
  async getStatus(): Promise<EntraConnectionStatus> {
    const response = await apiClient.get('/entra-sync/status');
    return response.data;
  },

  /**
   * Get roaming signatures status
   */
  async getRoamingSignaturesStatus(): Promise<RoamingSignaturesStatus> {
    const response = await apiClient.get('/entra-sync/roaming-signatures');
    return response.data;
  },

  /**
   * Get sync preview for an employee
   */
  async getPreview(employeeId: string): Promise<EntraSyncPreview> {
    const response = await apiClient.get(`/entra-sync/preview/${employeeId}`);
    return response.data;
  },

  /**
   * Get signature preview for an employee
   */
  async getSignaturePreview(employeeId: string): Promise<SignaturePreview> {
    const response = await apiClient.get(`/entra-sync/signature-preview/${employeeId}`);
    return response.data;
  },

  /**
   * Sync a single employee to Entra ID
   */
  async pushEmployee(employeeId: string, request: EntraSyncRequest): Promise<EntraSyncResult> {
    const response = await apiClient.post(`/entra-sync/push/${employeeId}`, request);
    return response.data;
  },

  /**
   * Sync multiple employees to Entra ID
   */
  async pushBatch(request: EntraSyncBatchRequest): Promise<EntraSyncBatchResult> {
    const response = await apiClient.post('/entra-sync/push-batch', request);
    return response.data;
  },
};
