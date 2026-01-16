/**
 * V2.7 Type Definitions
 * Extends existing types with new backend API support
 */

import type { Template } from './index';

// ============================================================================
// TEMPLATE CONTENT & SETTINGS
// ============================================================================

/**
 * Extended template type with V2.7 Vitec metadata fields
 */
export interface TemplateWithMetadata extends Template {
  // Channel and Type
  channel: TemplateChannel;
  template_type: TemplateType;
  
  // Receiver
  receiver_type?: ReceiverType;
  receiver?: Receiver;
  extra_receivers: string[];
  
  // Filtering/Categorization
  phases: Phase[];
  assignment_types: string[];
  ownership_types: OwnershipType[];
  departments: string[];
  
  // Email
  email_subject?: string;
  
  // Layout References
  header_template_id?: string;
  footer_template_id?: string;
  
  // Margins (in cm)
  margin_top?: number;
  margin_bottom?: number;
  margin_left?: number;
  margin_right?: number;
  
  // Thumbnail
  preview_thumbnail_url?: string;
}

export type TemplateChannel = 'pdf' | 'email' | 'sms' | 'pdf_email';
export type TemplateType = 'Objekt/Kontakt' | 'System';
export type ReceiverType = 'Egne/kundetilpasset' | 'Systemstandard';
export type Receiver = 'Selger' | 'Kjøper' | 'Megler' | 'Bank' | 'Forretningsfører';
export type Phase = 'Oppdrag' | 'Markedsføring' | 'Visning' | 'Budrunde' | 'Kontrakt' | 'Oppgjør';
export type OwnershipType = 'Bolig' | 'Aksje' | 'Tomt' | 'Næring' | 'Hytte';

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
  channel?: TemplateChannel;
  template_type?: TemplateType;
  receiver_type?: ReceiverType;
  receiver?: Receiver;
  extra_receivers?: string[];
  phases?: Phase[];
  assignment_types?: string[];
  ownership_types?: OwnershipType[];
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
export interface UpdateTemplateSettingsResponse extends TemplateWithMetadata {
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

// ============================================================================
// SHELF GROUPING
// ============================================================================

/**
 * Shelf grouping configuration
 */
export type ShelfGroupBy = 'channel' | 'category' | 'status' | 'phase';

/**
 * Grouped templates for shelf display
 */
export interface ShelfGroup {
  id: string;
  label: string;
  icon?: React.ReactNode;
  templates: TemplateWithMetadata[];
  isCollapsed: boolean;
}

/**
 * Result of grouping templates
 */
export interface GroupedTemplates {
  groups: ShelfGroup[];
  totalCount: number;
}
