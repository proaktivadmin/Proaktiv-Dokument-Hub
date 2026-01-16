/**
 * Hook for template settings management
 */

import { useState, useEffect } from 'react';
import { templateSettingsApi } from '@/lib/api';
import type { UpdateTemplateSettingsResponse } from '@/types/v2';

interface UseTemplateSettingsReturn {
  settings: UpdateTemplateSettingsResponse | null;
  isLoading: boolean;
  error: string | null;
  refetch: () => void;
}

export function useTemplateSettings(templateId: string | null): UseTemplateSettingsReturn {
  const [settings, setSettings] = useState<UpdateTemplateSettingsResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchSettings = async () => {
    if (!templateId) return;

    setIsLoading(true);
    setError(null);

    try {
      const data = await templateSettingsApi.getSettings(templateId);
      setSettings(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load settings');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchSettings();
  }, [templateId]);

  return { settings, isLoading, error, refetch: fetchSettings };
}
