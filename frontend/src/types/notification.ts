/**
 * Notification Types
 */
export type NotificationType =
  | 'employee_added'
  | 'employee_removed'
  | 'employee_updated'
  | 'office_added'
  | 'office_removed'
  | 'office_updated'
  | 'upn_mismatch'
  | 'sync_error';

export type NotificationSeverity = 'info' | 'warning' | 'error';

export type NotificationEntityType = 'employee' | 'office' | 'sync';

export interface Notification {
  id: string;
  type: NotificationType;
  entity_type: NotificationEntityType;
  entity_id: string | null;
  title: string;
  message: string;
  severity: NotificationSeverity;
  is_read: boolean;
  metadata: Record<string, unknown> | null;
  created_at: string;
}

export interface NotificationListResponse {
  items: Notification[];
  total: number;
  unread_count: number;
}

export interface UnreadCountResponse {
  count: number;
}
