/**
 * Code Pattern Types for Pattern Library
 */

/**
 * Reusable code pattern (HTML/Vitec snippets)
 */
export interface CodePattern {
  id: string;
  name: string;
  category: string;                     // e.g., "Tabeller", "Betingelser", "Lister"
  description: string | null;
  html_code: string;                    // The actual HTML/Vitec code
  variables_used: string[];             // Array of merge field paths used
  preview_thumbnail_url: string | null;
  usage_count: number;
  created_by: string;
  updated_by: string;
  created_at: string;
  updated_at: string;
}

/**
 * Create code pattern payload
 */
export interface CodePatternCreate {
  name: string;
  category: string;
  html_code: string;
  description?: string;
  variables_used?: string[];
}

/**
 * Update code pattern payload (all optional)
 */
export interface CodePatternUpdate {
  name?: string;
  category?: string;
  html_code?: string;
  description?: string;
  variables_used?: string[];
}

/**
 * Paginated code pattern list response
 */
export interface CodePatternListResponse {
  patterns: CodePattern[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}
