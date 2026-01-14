/**
 * Merge Field Types for Flettekode System
 */

/**
 * Data types supported by merge fields
 */
export type MergeFieldDataType = 'string' | 'number' | 'date' | 'boolean' | 'array';

/**
 * Merge field category names
 */
export type MergeFieldCategory = 
  | 'Selger' 
  | 'Kjøper' 
  | 'Eiendom' 
  | 'Megler' 
  | 'Økonomi' 
  | 'Oppdrag'
  | 'Kontor';

/**
 * Individual merge field from the Flettekode registry
 */
export interface MergeField {
  id: string;
  path: string;                          // e.g., "selger.navn", "eiendom.adresse"
  category: MergeFieldCategory | string;
  label: string;                         // Display name, e.g., "Selger Navn"
  description: string | null;
  example_value: string | null;          // e.g., "Ola Nordmann"
  data_type: MergeFieldDataType;
  is_iterable: boolean;                  // Can be used with vitec-foreach
  parent_model: string | null;           // e.g., "Model.selgere"
  usage_count: number;
  created_at: string;
  updated_at: string;
}

/**
 * Create merge field payload
 */
export interface MergeFieldCreate {
  path: string;
  category: string;
  label: string;
  description?: string;
  example_value?: string;
  data_type?: MergeFieldDataType;
  is_iterable?: boolean;
  parent_model?: string;
}

/**
 * Update merge field payload (all optional)
 */
export interface MergeFieldUpdate {
  path?: string;
  category?: string;
  label?: string;
  description?: string;
  example_value?: string;
  data_type?: MergeFieldDataType;
  is_iterable?: boolean;
  parent_model?: string;
}

/**
 * Paginated merge field list response
 */
export interface MergeFieldListResponse {
  merge_fields: MergeField[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

/**
 * Result of merge field auto-discovery scan
 */
export interface MergeFieldDiscoveryResult {
  discovered_count: number;
  new_fields: string[];
  existing_fields: string[];
  templates_scanned: number;
}

/**
 * Category with count for sidebar
 */
export interface MergeFieldCategoryCount {
  name: string;
  count: number;
}
