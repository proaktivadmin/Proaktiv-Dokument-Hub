"use client";

import { useCallback, useEffect, useState } from 'react';
import { notificationsApi } from '@/lib/api/notifications';
import type { Notification } from '@/types/notification';

interface UseNotificationsOptions {
  limit?: number;
  pollInterval?: number; // in milliseconds, 0 to disable
}

interface UseNotificationsReturn {
  notifications: Notification[];
  unreadCount: number;
  total: number;
  isLoading: boolean;
  error: Error | null;
  refresh: () => Promise<void>;
  markAsRead: (id: string) => Promise<void>;
  markAllAsRead: () => Promise<void>;
  deleteNotification: (id: string) => Promise<void>;
  clearAll: () => Promise<void>;
}

export function useNotifications(
  options: UseNotificationsOptions = {}
): UseNotificationsReturn {
  const { limit = 20, pollInterval = 30000 } = options;

  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchNotifications = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await notificationsApi.list({ limit });
      setNotifications(data.items);
      setUnreadCount(data.unread_count);
      setTotal(data.total);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to fetch notifications'));
    } finally {
      setIsLoading(false);
    }
  }, [limit]);

  useEffect(() => {
    fetchNotifications();
  }, [fetchNotifications]);

  useEffect(() => {
    if (pollInterval <= 0) return;

    const interval = setInterval(fetchNotifications, pollInterval);
    return () => clearInterval(interval);
  }, [pollInterval, fetchNotifications]);

  const markAsRead = useCallback(async (id: string) => {
    await notificationsApi.markAsRead(id);
    const existing = notifications.find((item) => item.id === id);
    setNotifications((prev) =>
      prev.map((item) => (item.id === id ? { ...item, is_read: true } : item))
    );
    if (existing && !existing.is_read) {
      setUnreadCount((prev) => Math.max(0, prev - 1));
    }
  }, [notifications]);

  const markAllAsRead = useCallback(async () => {
    await notificationsApi.markAllAsRead();
    setNotifications((prev) => prev.map((item) => ({ ...item, is_read: true })));
    setUnreadCount(0);
  }, []);

  const deleteNotification = useCallback(async (id: string) => {
    const existing = notifications.find((item) => item.id === id);
    await notificationsApi.delete(id);
    setNotifications((prev) => prev.filter((item) => item.id !== id));
    setTotal((prev) => Math.max(0, prev - 1));
    if (existing && !existing.is_read) {
      setUnreadCount((prev) => Math.max(0, prev - 1));
    }
  }, [notifications]);

  const clearAll = useCallback(async () => {
    await notificationsApi.clearAll();
    setNotifications([]);
    setUnreadCount(0);
    setTotal(0);
  }, []);

  return {
    notifications,
    unreadCount,
    total,
    isLoading,
    error,
    refresh: fetchNotifications,
    markAsRead,
    markAllAsRead,
    deleteNotification,
    clearAll,
  };
}
