/**
 * Hook for grouping templates by various criteria
 */

import { useMemo } from 'react';
import type { TemplateWithMetadata, ShelfGroupBy, GroupedTemplates } from '@/types/v2';
import { FileText, Mail, MessageSquare, FolderOpen, CheckCircle, Clock } from 'lucide-react';

export function useGroupedTemplates(
  templates: TemplateWithMetadata[],
  groupBy: ShelfGroupBy
): GroupedTemplates {
  return useMemo(() => {
    const groups = new Map<string, TemplateWithMetadata[]>();

    // Group templates
    templates.forEach((template) => {
      let key: string;
      let label: string;

      switch (groupBy) {
        case 'channel':
          key = template.channel;
          label = getChannelLabel(template.channel);
          break;
        case 'category':
          key = template.categories[0]?.id || 'uncategorized';
          label = template.categories[0]?.name || 'Ukategorisert';
          break;
        case 'status':
          key = template.status;
          label = getStatusLabel(template.status);
          break;
        case 'phase':
          key = template.phases[0] || 'no-phase';
          label = template.phases[0] || 'Ingen fase';
          break;
        default:
          key = 'all';
          label = 'Alle maler';
      }

      if (!groups.has(key)) {
        groups.set(key, []);
      }
      groups.get(key)!.push(template);
    });

    // Convert to ShelfGroup array
    const shelfGroups = Array.from(groups.entries()).map(([id, templates]) => ({
      id,
      label: getLabelForGroup(id, groupBy),
      icon: getIconForGroup(id, groupBy),
      templates,
      isCollapsed: false,
    }));

    return {
      groups: shelfGroups,
      totalCount: templates.length,
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

function getIconForGroup(id: string, groupBy: ShelfGroupBy): React.ReactNode {
  if (groupBy === 'channel') {
    const icons: Record<string, React.ReactNode> = {
      pdf: <FileText className="h-4 w-4" />,
      email: <Mail className="h-4 w-4" />,
      sms: <MessageSquare className="h-4 w-4" />,
      pdf_email: <FileText className="h-4 w-4" />,
    };
    return icons[id];
  }

  if (groupBy === 'status') {
    const icons: Record<string, React.ReactNode> = {
      published: <CheckCircle className="h-4 w-4" />,
      draft: <Clock className="h-4 w-4" />,
    };
    return icons[id];
  }

  return <FolderOpen className="h-4 w-4" />;
}
