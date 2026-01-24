/**
 * Notifications API Client
 */

import { apiClient } from './config';
import type {
  Notification,
  NotificationListResponse,
  UnreadCountResponse,
} from '@/types/notification';

export interface NotificationListParams {
  skip?: number;
  limit?: number;
  unread_only?: boolean;
}

export const notificationsApi = {
  async list(params?: NotificationListParams): Promise<NotificationListResponse> {
    const searchParams = new URLSearchParams();
    if (params?.skip !== undefined) searchParams.set('skip', String(params.skip));
    if (params?.limit !== undefined) searchParams.set('limit', String(params.limit));
    if (params?.unread_only !== undefined) {
      searchParams.set('unread_only', String(params.unread_only));
    }

    const query = searchParams.toString();
    const response = await apiClient.get(`/notifications${query ? `?${query}` : ''}`);
    return response.data;
  },

  async getUnreadCount(): Promise<UnreadCountResponse> {
    const response = await apiClient.get('/notifications/unread-count');
    return response.data;
  },

  async markAsRead(id: string): Promise<Notification> {
    const response = await apiClient.patch(`/notifications/${id}/read`);
    return response.data;
  },

  async markAllAsRead(): Promise<{ count: number }> {
    const response = await apiClient.post('/notifications/read-all');
    return response.data;
  },

  async delete(id: string): Promise<void> {
    await apiClient.delete(`/notifications/${id}`);
  },

  async clearAll(): Promise<{ count: number }> {
    const response = await apiClient.post('/notifications/clear');
    return response.data;
  },
};
