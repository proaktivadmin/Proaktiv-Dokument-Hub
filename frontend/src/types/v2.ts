/**
 * V2.7 Type Definitions
 * Extends existing types with new backend API support
 */

// Re-export all V2 types from subfolder
export * from './v2/merge-fields';
export * from './v2/code-patterns';
export * from './v2/layout-partials';
export * from './v2/template-metadata';
export * from './v2/shelf-library';

// ============================================================================
// TEMPLATE CONTENT API (V2.7 specific)
// ============================================================================

/**
 * Request payload for saving template content
 */
export interface SaveTemplateContentRequest {
  content: string;
  change_notes?: string;
  auto_sanitize?: boolean;
}

/**
 * Response from saving template content
 */
export interface SaveTemplateContentResponse {
  id: string;
  version: number;
  content_hash: string;
  merge_fields_detected: number;
  previous_version_id?: string;
}

/**
 * Request payload for updating template settings
 */
export interface UpdateTemplateSettingsRequest {
  channel?: string;
  template_type?: string;
  receiver_type?: string;
  receiver?: string;
  extra_receivers?: string[];
  phases?: string[];
  assignment_types?: string[];
  ownership_types?: string[];
  departments?: string[];
  email_subject?: string;
  header_template_id?: string;
  footer_template_id?: string;
  margin_top?: number;
  margin_bottom?: number;
  margin_left?: number;
  margin_right?: number;
}

/**
 * Response from updating template settings
 */
export interface UpdateTemplateSettingsResponse {
  id: string;
  channel?: string;
  template_type?: string;
  receiver_type?: string;
  receiver?: string;
  extra_receivers?: string[];
  phases?: string[];
  assignment_types?: string[];
  ownership_types?: string[];
  departments?: string[];
  email_subject?: string;
  header_template_id?: string;
  footer_template_id?: string;
  margin_top?: number;
  margin_bottom?: number;
  margin_left?: number;
  margin_right?: number;
  updated_at: string;
}

/**
 * Response from generating thumbnail
 */
export interface GenerateThumbnailResponse {
  thumbnail_url: string;
  width: number;
  height: number;
}

// ============================================================================
// DASHBOARD STATS
// ============================================================================

/**
 * Dashboard statistics from backend
 */
export interface DashboardStatsV2 {
  total: number;
  published: number;
  draft: number;
  archived: number;
  downloads: number;
  recent_uploads: RecentUploadV2[];
}

export interface RecentUploadV2 {
  id: string;
  title: string;
  created_at: string;
}
