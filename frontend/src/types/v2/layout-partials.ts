/**
 * Layout Partial Types for Headers/Footers/Signatures
 */

/**
 * Partial types
 */
export type LayoutPartialType = 'header' | 'footer' | 'signature';

/**
 * Context where partial can be used
 */
export type LayoutPartialContext = 'pdf' | 'email' | 'sms' | 'all';

/**
 * Header, footer, or signature partial template
 */
export interface LayoutPartial {
  id: string;
  name: string;
  type: LayoutPartialType;
  context: LayoutPartialContext;
  document_type?: string | null;
  html_content: string;
  is_default: boolean;
  created_by: string;
  updated_by: string;
  created_at: string;
  updated_at: string;
}

/**
 * Create layout partial payload
 */
export interface LayoutPartialCreate {
  name: string;
  type: LayoutPartialType;
  html_content: string;
  context?: LayoutPartialContext;
  document_type?: string;
  is_default?: boolean;
}

/**
 * Update layout partial payload (all optional)
 */
export interface LayoutPartialUpdate {
  name?: string;
  type?: LayoutPartialType;
  context?: LayoutPartialContext;
  document_type?: string;
  html_content?: string;
  is_default?: boolean;
}

/**
 * Layout partial list response
 */
export interface LayoutPartialListResponse {
  partials: LayoutPartial[];
  total: number;
}

/**
 * Result of set-default operation
 */
export interface LayoutPartialSetDefaultResponse {
  id: string;
  is_default: boolean;
  previous_default_id: string | null;
}
