/**
 * Hook for grouping templates by various criteria
 */

import { useMemo } from 'react';
import type { TemplateWithMetadata, ShelfGroupBy, GroupedTemplates } from '@/types/v2';

export function useGroupedTemplates(
  templates: TemplateWithMetadata[],
  groupBy: ShelfGroupBy
): GroupedTemplates {
  return useMemo(() => {
    const groups = new Map<string, TemplateWithMetadata[]>();

    // Group templates
    templates.forEach((template) => {
      let key: string;

      switch (groupBy) {
        case 'channel':
          key = template.channel;
          break;
        case 'category':
          // Use template_type as category fallback
          key = template.template_type || 'uncategorized';
          break;
        case 'status':
          key = template.status;
          break;
        case 'phase':
          key = template.phases[0] || 'no-phase';
          break;
        default:
          key = 'all';
      }

      if (!groups.has(key)) {
        groups.set(key, []);
      }
      groups.get(key)!.push(template);
    });

    // Convert to ShelfGroup array
    const shelves = Array.from(groups.entries()).map(([id, groupTemplates]) => ({
      id,
      label: getLabelForGroup(id, groupBy),
      groupValue: id,
      templates: groupTemplates,
      count: groupTemplates.length,
      isCollapsed: false,
    }));

    return {
      groupBy,
      shelves,
      totalTemplates: templates.length,
    };
  }, [templates, groupBy]);
}

function getChannelLabel(channel: string): string {
  const labels: Record<string, string> = {
    pdf: 'PDF',
    email: 'E-post',
    sms: 'SMS',
    pdf_email: 'PDF & E-post',
  };
  return labels[channel] || channel;
}

function getStatusLabel(status: string): string {
  const labels: Record<string, string> = {
    published: 'Publisert',
    draft: 'Utkast',
    archived: 'Arkivert',
  };
  return labels[status] || status;
}

function getLabelForGroup(id: string, groupBy: ShelfGroupBy): string {
  switch (groupBy) {
    case 'channel':
      return getChannelLabel(id);
    case 'status':
      return getStatusLabel(id);
    default:
      return id;
  }
}

