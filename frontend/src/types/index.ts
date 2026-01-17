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
}

export type TemplateStatus = "draft" | "published" | "archived";

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
 * Re-export V2 and V3 types
 */
export * from './v2';
export * from './v3';
