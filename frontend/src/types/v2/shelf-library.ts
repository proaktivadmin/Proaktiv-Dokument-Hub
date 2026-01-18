/**
 * Shelf Library Types for Template Grouping
 */

import type { TemplateWithMetadata, TemplateChannel, TransactionPhase, Receiver, OwnershipType } from './template-metadata';

/**
 * Grouping options for shelf layout
 */
export type ShelfGroupBy = 'channel' | 'phase' | 'receiver' | 'category' | 'ownership_type' | 'status';

/**
 * A single shelf (swimlane) containing grouped templates
 */
export interface ShelfGroup {
  id: string;                           // Unique identifier for the shelf
  label: string;                        // Display label (e.g., "PDF", "E-post")
  groupValue: string;                   // The actual value being grouped
  templates: TemplateWithMetadata[];
  count: number;                        // Total templates in this group
  isCollapsed: boolean;                 // UI state
}

/**
 * Grouped templates organized by shelf
 */
export interface GroupedTemplates {
  groupBy: ShelfGroupBy;
  shelves: ShelfGroup[];
  totalTemplates: number;
}

/**
 * Filter state for template library
 */
export interface TemplateFilterState {
  search: string;
  channel: TemplateChannel | null;
  phases: TransactionPhase[];
  receiver: Receiver | null;
  ownership_types: OwnershipType[];
  status: 'draft' | 'published' | 'archived' | null;
  category_id?: string | null;
}

/**
 * Shelf row display configuration
 */
export interface ShelfDisplayConfig {
  cardWidth: number;                    // Card width in px (default: 160)
  cardHeight: number;                   // Card height in px (default: 200)
  gap: number;                          // Gap between cards
  showScrollArrows: boolean;
  dimNonMatching: boolean;              // Dim non-matching cards on filter
  hideEmptyShelves: boolean;
}
