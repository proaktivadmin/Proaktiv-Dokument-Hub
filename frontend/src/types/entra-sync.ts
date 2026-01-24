/**
 * Entra ID Sync Types
 */

// =============================================================================
// Sync Scope
// =============================================================================

export type SyncScope = 'profile' | 'photo' | 'signature';

// =============================================================================
// Property Change
// =============================================================================

export interface PropertyChange {
  property: string;
  current_value: string | null;
  new_value: string | null;
  will_update: boolean;
}

// =============================================================================
// Preview Types
// =============================================================================

export interface EntraSyncPreview {
  employee_id: string;
  employee_name: string;
  employee_email: string | null;
  entra_user_found: boolean;
  entra_user_id: string | null;
  entra_upn: string | null;
  profile_changes: PropertyChange[];
  photo_needs_update: boolean;
  photo_url: string | null;
  signature_preview_available: boolean;
}

export interface SignaturePreview {
  employee_id: string;
  employee_name: string;
  html: string;
  text: string;
}

// =============================================================================
// Request Types
// =============================================================================

export interface EntraSyncRequest {
  scope: SyncScope[];
  dry_run?: boolean;
}

export interface EntraSyncBatchRequest {
  employee_ids: string[];
  scope: SyncScope[];
  dry_run?: boolean;
}

export interface EntraImportRequest {
  dry_run?: boolean;
  filter_email?: string;
}

// =============================================================================
// Result Types
// =============================================================================

export interface EntraSyncResult {
  success: boolean;
  employee_id: string;
  employee_name: string;
  entra_user_id: string | null;
  profile_updated: boolean;
  profile_changes: string[];
  profile_error: string | null;
  photo_updated: boolean;
  photo_error: string | null;
  signature_pushed: boolean;
  signature_error: string | null;
  error: string | null;
}

export interface EntraSyncBatchResult {
  total: number;
  successful: number;
  failed: number;
  skipped: number;
  results: EntraSyncResult[];
  profiles_updated: number;
  photos_uploaded: number;
  signatures_pushed: number;
}

export interface EntraImportResult {
  success: boolean;
  dry_run: boolean;
  employees_loaded: number | null;
  matched_updated: number | null;
  employees_not_matched: number | null;
  entra_users_not_matched: number | null;
  error: string | null;
}

// =============================================================================
// Status Types
// =============================================================================

export interface EntraConnectionStatus {
  connected: boolean;
  enabled: boolean;
  tenant_id: string | null;
  client_id: string | null;
  error: string | null;
}

export interface RoamingSignaturesStatus {
  enabled: boolean;
  warning: string | null;
}
