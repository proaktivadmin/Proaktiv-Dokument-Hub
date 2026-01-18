/**
 * Extended Template Metadata Types (Vitec Parity)
 */

/**
 * Template channel types
 */
export type TemplateChannel = 'pdf' | 'email' | 'sms' | 'pdf_email';

/**
 * Template type (Vitec classification)
 */
export type TemplateType = 'Objekt/Kontakt' | 'System';

/**
 * Receiver type
 */
export type ReceiverType = 'Egne/kundetilpasset' | 'Systemstandard';

/**
 * Receiver roles (dynamic list from Vitec/Proaktiv)
 */
export type Receiver = string;

export interface TemplateTag {
  id: string;
  name: string;
  color: string;
}

/**
 * Transaction phases
 */
export type TransactionPhase = 
  | 'Oppdrag' 
  | 'Markedsføring' 
  | 'Visning' 
  | 'Budrunde' 
  | 'Kontrakt' 
  | 'Oppgjør';

/**
 * Ownership types
 */
export type OwnershipType = 'Bolig' | 'Aksje' | 'Tomt' | 'Næring' | 'Hytte';

/**
 * Extended template with Vitec metadata fields
 */
export interface TemplateWithMetadata {
  id: string;
  title: string;
  description: string | null;
  file_name: string;
  file_type: string;
  file_size_bytes: number;
  status: 'draft' | 'published' | 'archived';
  version: number;
  preview_url: string | null;
  created_at: string | null;
  updated_at: string | null;
  attachments?: string[];
  tags?: TemplateTag[];
  
  // V2 Vitec Metadata Fields
  preview_thumbnail_url: string | null;
  channel: TemplateChannel;
  template_type: TemplateType | null;
  receiver_type: ReceiverType | null;
  receiver: Receiver | null;
  extra_receivers: string[];
  phases: TransactionPhase[];
  assignment_types: string[];
  ownership_types: OwnershipType[];
  departments: string[];
  email_subject: string | null;
  header_template_id: string | null;
  footer_template_id: string | null;
  margin_top: number;
  margin_bottom: number;
  margin_left: number;
  margin_right: number;
}

/**
 * Template metadata update payload
 */
export interface TemplateMetadataUpdate {
  channel?: TemplateChannel;
  template_type?: TemplateType;
  receiver_type?: ReceiverType;
  receiver?: Receiver;
  extra_receivers?: string[];
  phases?: TransactionPhase[];
  assignment_types?: string[];
  ownership_types?: OwnershipType[];
  departments?: string[];
  email_subject?: string;
  header_template_id?: string | null;
  footer_template_id?: string | null;
  margin_top?: number;
  margin_bottom?: number;
  margin_left?: number;
  margin_right?: number;
  preview_thumbnail_url?: string;
}

/**
 * Template analysis result
 */
export interface TemplateAnalysisResult {
  template_id: string;
  merge_fields_found: string[];
  conditions_found: string[];
  loops_found: string[];
  unknown_fields: string[];
  analysis_timestamp: string;
}
