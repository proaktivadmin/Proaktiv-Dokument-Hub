/**
 * V3 Types - Office & Employee Hub, Assets, Territory, Checklists
 */

// =============================================================================
// Office Types
// =============================================================================

export type OfficeType = 'main' | 'sub' | 'regional';

export interface Office {
  id: string;
  name: string; // Marketing/display name
  legal_name: string | null; // Legal company name (e.g., 'Proaktiv Gruppen AS')
  short_code: string;
  organization_number: string | null; // Norwegian org number for matching/merging
  vitec_department_id: number | null;
  office_type: OfficeType; // main, sub, or regional
  parent_office_id: string | null; // For sub-departments
  email: string | null;
  phone: string | null;
  street_address: string | null;
  postal_code: string | null;
  city: string | null;
  homepage_url: string | null;
  google_my_business_url: string | null;
  facebook_url: string | null;
  instagram_url: string | null;
  linkedin_url: string | null;
  profile_image_url: string | null;
  banner_image_url: string | null; // Office banner image for cards
  description: string | null;
  color: string; // Hex color for territory map
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface SubOfficeSummary {
  id: string;
  name: string;
  short_code: string;
  employee_count: number;
  is_active: boolean;
}

export interface OfficeWithStats extends Office {
  employee_count: number;
  active_employee_count: number;
  territory_count: number;
  sub_offices: SubOfficeSummary[];
}

export type OfficeCreatePayload = Omit<Office, 'id' | 'created_at' | 'updated_at'>;
export type OfficeUpdatePayload = Partial<OfficeCreatePayload>;

export interface OfficeListResponse {
  items: OfficeWithStats[];
  total: number;
}

export interface OfficeSyncResult {
  total: number;
  synced: number;
  created: number;
  updated: number;
  skipped: number;
}

// =============================================================================
// Employee Types
// =============================================================================

export type EmployeeStatus = 'active' | 'onboarding' | 'offboarding' | 'inactive';
export type EmployeeType = 'internal' | 'external' | 'system';

export interface Employee {
  id: string;
  office_id: string;
  vitec_employee_id: string | null;
  first_name: string;
  last_name: string;
  title: string | null;
  email: string | null;
  phone: string | null;
  homepage_profile_url: string | null;
  linkedin_url: string | null;
  facebook_url: string | null;
  instagram_url: string | null;
  twitter_url: string | null;
  sharepoint_folder_url: string | null;
  profile_image_url: string | null;
  description: string | null;
  system_roles: string[];
  status: EmployeeStatus;
  employee_type: EmployeeType; // internal, external, or system
  external_company: string | null; // Company name for external developers/consultants
  entra_upn: string | null; // User Principal Name in Entra ID
  entra_upn_mismatch: boolean; // True if Entra UPN differs from email (SSO will fail)
  entra_user_id: string | null;
  entra_mail: string | null;
  entra_display_name: string | null;
  entra_given_name: string | null;
  entra_surname: string | null;
  entra_job_title: string | null;
  entra_mobile_phone: string | null;
  entra_department: string | null;
  entra_office_location: string | null;
  entra_street_address: string | null;
  entra_postal_code: string | null;
  entra_country: string | null;
  entra_account_enabled: boolean | null;
  entra_mismatch_fields: string[];
  entra_last_synced_at: string | null;
  is_featured_broker: boolean;
  start_date: string | null; // ISO date

  end_date: string | null;
  hide_from_homepage_date: string | null;
  delete_data_date: string | null;
  created_at: string;
  updated_at: string;
}

export interface OfficeMinimal {
  id: string;
  name: string;
  short_code: string;
  color: string;
}

export interface EmployeeWithOffice extends Employee {
  office: OfficeMinimal;
  full_name: string;
  initials: string;
  days_until_end: number | null;
}

export type EmployeeCreatePayload = Omit<Employee, 'id' | 'created_at' | 'updated_at'>;
export type EmployeeUpdatePayload = Partial<EmployeeCreatePayload>;

export interface StartOffboardingPayload {
  end_date: string;
  hide_from_homepage_date?: string;
  delete_data_date?: string;
}

export interface EmployeeListResponse {
  items: EmployeeWithOffice[];
  total: number;
}

export interface EmployeeSyncResult {
  total: number;
  synced: number;
  created: number;
  updated: number;
  skipped: number;
  missing_office: number;
}

// =============================================================================
// Sync Review Types
// =============================================================================

export type SyncDecision = 'accept' | 'reject';

export interface FieldDiff {
  field_name: string;
  local_value: unknown | null;
  vitec_value: unknown | null;
  has_conflict: boolean;
  decision: SyncDecision | null;
}

export type RecordMatchType = 'new' | 'matched' | 'not_in_vitec';

export interface RecordDiff {
  match_type: RecordMatchType;
  local_id: string | null;
  vitec_id: string | null;
  display_name: string;
  fields: FieldDiff[];
  match_confidence: number;
  match_method: string | null;
}

export interface SyncSummary {
  offices_new: number;
  offices_matched: number;
  offices_not_in_vitec: number;
  employees_new: number;
  employees_matched: number;
  employees_not_in_vitec: number;
  employees_missing_office: number;
}

export interface SyncPreview {
  session_id: string;
  created_at: string;
  expires_at: string;
  offices: RecordDiff[];
  employees: RecordDiff[];
  summary: SyncSummary;
}

export interface SyncDecisionUpdatePayload {
  record_type: 'office' | 'employee';
  record_id: string;
  field_name: string;
  decision: SyncDecision;
}

export interface SyncCommitResult {
  offices_created: number;
  offices_updated: number;
  offices_skipped: number;
  employees_created: number;
  employees_updated: number;
  employees_skipped: number;
}

// =============================================================================
// External Listings Types
// =============================================================================

export type ListingSource =
  | 'anbudstjenester'
  | 'finn'
  | 'nummeropplysning'
  | '1881'
  | 'gulesider'
  | 'google'
  | 'other';

export type ListingStatus = 'verified' | 'needs_update' | 'pending_check' | 'removed';
export type ListingType = 'office' | 'broker' | 'company';

export interface ExternalListing {
  id: string;
  office_id: string | null;
  employee_id: string | null;
  source: ListingSource;
  listing_url: string;
  listing_type: ListingType;
  status: ListingStatus;
  last_verified_at: string | null;
  last_verified_by: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
  source_display_name: string;
  owner_type: 'office' | 'employee';
  is_verified: boolean;
  needs_attention: boolean;
}

export type ExternalListingCreatePayload = Omit<
  ExternalListing,
  'id' | 'created_at' | 'updated_at' | 'last_verified_at' | 'last_verified_by' | 'source_display_name' | 'owner_type' | 'is_verified' | 'needs_attention'
>;

export interface ExternalListingListResponse {
  items: ExternalListing[];
  total: number;
}

// =============================================================================
// Checklist Types
// =============================================================================

export type ChecklistType = 'onboarding' | 'offboarding';
export type ChecklistStatus = 'in_progress' | 'completed' | 'cancelled';

export interface ChecklistItem {
  name: string;
  description: string | null;
  required: boolean;
  order: number;
}

export interface ChecklistTemplate {
  id: string;
  name: string;
  description: string | null;
  type: ChecklistType;
  items: ChecklistItem[];
  is_active: boolean;
  item_count: number;
  required_item_count: number;
  created_at: string;
  updated_at: string;
}

export interface EmployeeMinimal {
  id: string;
  first_name: string;
  last_name: string;
}

export interface ProgressInfo {
  completed: number;
  total: number;
  percentage: number;
}

export interface ChecklistInstance {
  id: string;
  template_id: string;
  employee_id: string;
  status: ChecklistStatus;
  items_completed: string[]; // Item names that are completed
  due_date: string | null;
  completed_at: string | null;
  created_at: string;
  updated_at: string;
  completed_count: number;
  total_count: number;
  progress_percentage: number;
  is_completed: boolean;
  is_overdue: boolean;
}

export interface ChecklistInstanceWithDetails extends ChecklistInstance {
  template: ChecklistTemplate;
  employee: EmployeeMinimal;
  progress: ProgressInfo;
}

export interface ChecklistInstanceListResponse {
  items: ChecklistInstanceWithDetails[];
  total: number;
}

// =============================================================================
// Company Assets Types
// =============================================================================

export type AssetCategory = 'logo' | 'photo' | 'marketing' | 'document' | 'other';

export interface AssetMetadata {
  dimensions?: { width: number; height: number };
  alt_text?: string;
  usage_notes?: string;
}

export interface CompanyAsset {
  id: string;
  office_id: string | null;
  employee_id: string | null;
  is_global: boolean;
  name: string;
  filename: string;
  category: AssetCategory;
  content_type: string;
  file_size: number;
  storage_path: string;
  metadata: AssetMetadata | null;
  created_at: string;
  updated_at: string;
  scope: 'global' | 'office' | 'employee';
  is_image: boolean;
  file_size_formatted: string;
}

export interface AssetUploadPayload {
  file: File;
  name: string;
  category: AssetCategory;
  office_id?: string;
  employee_id?: string;
  is_global?: boolean;
  alt_text?: string;
  usage_notes?: string;
}

export interface CompanyAssetListResponse {
  items: CompanyAsset[];
  total: number;
}

// =============================================================================
// Territory Types
// =============================================================================

export type TerritorySource = 'vitec_next' | 'finn' | 'anbudstjenester' | 'homepage' | 'other';

export interface PostalCode {
  postal_code: string;
  postal_name: string;
  municipality_code: string | null;
  municipality_name: string | null;
  category: string | null;
  full_location: string;
  category_name: string;
  is_street_address: boolean;
  created_at: string;
  updated_at: string;
}

export interface OfficeTerritory {
  id: string;
  office_id: string;
  postal_code: string;
  source: TerritorySource;
  priority: number;
  is_blacklisted: boolean;
  valid_from: string | null;
  valid_to: string | null;
  is_active: boolean;
  source_display_name: string;
  created_at: string;
  updated_at: string;
}

export interface OfficeTerritoryWithDetails extends OfficeTerritory {
  office: OfficeMinimal;
  postal_info: PostalCode;
}

export interface OfficeTerritoryListResponse {
  items: OfficeTerritoryWithDetails[];
  total: number;
}

export interface TerritoryFeatureProperties {
  postal_code: string;
  postal_name: string;
  office_id: string | null;
  office_name: string | null;
  office_color: string | null;
  source: TerritorySource | null;
  is_blacklisted: boolean;
}

export interface TerritoryFeature {
  type: 'Feature';
  properties: TerritoryFeatureProperties;
  geometry: {
    type: 'Polygon';
    coordinates: number[][][];
  };
}

export interface TerritoryMapData {
  type: 'FeatureCollection';
  features: TerritoryFeature[];
}

export interface TerritoryImportResult {
  imported: number;
  errors: string[];
}

// =============================================================================
// Layout Partial Versioning Types
// =============================================================================

export interface LayoutPartialVersion {
  id: string;
  partial_id: string;
  version_number: number;
  html_content: string;
  change_notes: string | null;
  created_by: string;
  created_at: string;
}

export interface LayoutPartialVersionListResponse {
  partial_id: string;
  current_version: number;
  versions: LayoutPartialVersion[];
}

export interface LayoutPartialRevertResponse {
  partial_id: string;
  reverted_from: number;
  new_version: number;
  message: string;
}

export type DefaultScope = 'all' | 'category' | 'medium';
export type Medium = 'pdf' | 'email' | 'sms';

export interface LayoutPartialDefault {
  id: string;
  partial_id: string;
  scope: DefaultScope;
  category_id: string | null;
  medium: Medium | null;
  priority: number;
  scope_description: string;
  created_at: string;
  updated_at: string;
}

export interface LayoutPartialDefaultListResponse {
  items: LayoutPartialDefault[];
  total: number;
}

// =============================================================================
// Bulk Operations Types
// =============================================================================

export type TemplateStatus = 'draft' | 'published' | 'archived';

export interface BulkStatusUpdate {
  template_ids: string[];
  status: TemplateStatus;
}

export interface BulkCategoryUpdate {
  template_ids: string[];
  category_ids: string[];
  mode: 'add' | 'replace' | 'remove';
}

export interface BulkOperationResult {
  updated: number;
  failed: number;
  updated_ids: string[];
  failed_details: Array<{ id: string; error: string }>;
}

// =============================================================================
// Template Version Types
// =============================================================================

export interface TemplateVersion {
  id: string;
  template_id: string;
  version_number: number;
  file_name: string;
  file_size_bytes: number;
  created_by: string;
  change_notes: string | null;
  created_at: string;
}

export interface TemplateVersionListResponse {
  template_id: string;
  current_version: number;
  versions: TemplateVersion[];
}

export interface TemplateRestoreResponse {
  template_id: string;
  restored_from: number;
  new_version: number;
  message: string;
}
