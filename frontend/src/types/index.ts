/**
 * Template Types
 */
export interface Tag {
  id: string;
  name: string;
  color: string;
}

export interface Category {
  id: string;
  name: string;
  icon: string | null;
  description?: string | null;
  sort_order?: number | null;
  created_at?: string | null;
}

export interface Template {
  id: string;
  title: string;
  description: string | null;
  file_name: string;
  file_type: string;
  file_size_bytes: number;
  status: TemplateStatus;
  version: number;
  preview_url: string | null;
  created_at: string | null;
  updated_at: string | null;
  tags: Tag[];
  categories: Category[];
  attachments?: string[];
  workflow_status?: WorkflowStatus;
  is_archived_legacy?: boolean;
  origin?: string | null;
  published_version?: number | null;
  reviewed_at?: string | null;
  reviewed_by?: string | null;
  ckeditor_validated?: boolean;
}

export type TemplateStatus = "draft" | "published" | "archived";
export type WorkflowStatus = "draft" | "in_review" | "published" | "archived";

export interface WorkflowTransition {
  action: "submit" | "approve" | "reject" | "unpublish" | "archive" | "restore";
  reviewer?: string;
  reason?: string;
}

export interface WorkflowStatusResponse {
  template_id: string;
  workflow_status: WorkflowStatus;
  published_version: number | null;
  reviewed_at: string | null;
  reviewed_by: string | null;
  ckeditor_validated: boolean;
  ckeditor_validated_at: string | null;
}

export interface WorkflowEvent {
  timestamp: string;
  from_status: string;
  to_status: string;
  actor: string | null;
  notes: string | null;
}

export interface TemplateListResponse {
  templates: Template[];
  pagination: {
    total: number;
    page: number;
    per_page: number;
    total_pages: number;
  };
}

export interface UploadTemplatePayload {
  file: File;
  title: string;
  description?: string;
  status?: TemplateStatus;
  category_id?: string;
  auto_sanitize?: boolean;
}

export interface UploadTemplateResponse {
  id: string;
  title: string;
  file_name: string;
  status: TemplateStatus;
  created_at: string | null;
}

export interface UpdateTemplatePayload {
  title?: string;
  description?: string;
  status?: TemplateStatus;
  category_ids?: string[];
}

export interface UpdateTemplateResponse {
  id: string;
  title: string;
  status: TemplateStatus;
  updated_at: string | null;
}

/**
 * Dashboard Stats
 */
export interface RecentUpload {
  template_id: string;
  title: string;
  created_at: string | null;
}

export interface DashboardStats {
  total_templates: number;
  published_templates: number;
  draft_templates: number;
  archived_templates: number;
  total_downloads_30d: number;
  most_downloaded: unknown[];
  recent_uploads: RecentUpload[];
  categories_breakdown: Record<string, number>;
}

/**
 * API Error
 */
export interface ApiError {
  detail: string;
}

/**
 * Template Comparison Types
 */
export interface StructuralChange {
  category: "cosmetic" | "structural" | "content" | "merge_fields" | "logic" | "breaking";
  element_path: string;
  description: string;
  before: string | null;
  after: string | null;
}

export interface ComparisonConflict {
  section: string;
  our_change: string;
  vitec_change: string;
  severity: "low" | "medium" | "high";
}

export interface ChangeClassification {
  cosmetic: number;
  structural: number;
  content: number;
  merge_fields: number;
  logic: number;
  breaking: number;
  total: number;
}

export interface ComparisonResult {
  changes: StructuralChange[];
  classification: ChangeClassification;
  conflicts: ComparisonConflict[];
  stored_hash: string;
  updated_hash: string;
  hashes_match: boolean;
}

export interface AnalysisReport {
  summary: string;
  changes_by_category: Record<string, string[]>;
  impact: string;
  conflicts: ComparisonConflict[];
  recommendation: "ADOPT" | "IGNORE" | "PARTIAL_MERGE" | "REVIEW_REQUIRED";
  suggested_actions: string[];
  ai_powered: boolean;
  raw_comparison: ComparisonResult;
}

/**
 * Re-export V2 and V3 types
 */
export * from './v2';
export * from './v3';
export * from './entra-sync';