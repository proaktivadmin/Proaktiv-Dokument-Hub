/**
 * useLayoutPartials Hook
 * 
 * Fetches layout partials (headers, footers, signatures) from the backend.
 */

import { useState, useEffect, useCallback, useMemo } from 'react';
import { layoutPartialsApi } from '@/lib/api/layout-partials';
import type { LayoutPartial } from '@/types/v2';

interface UseLayoutPartialsReturn {
  partials: LayoutPartial[];
  headers: LayoutPartial[];
  footers: LayoutPartial[];
  signatures: LayoutPartial[];
  isLoading: boolean;
  error: string | null;
  refetch: () => void;
}

interface UseLayoutPartialsOptions {
  type?: 'header' | 'footer' | 'signature';
  context?: 'pdf' | 'email' | 'sms' | 'all';
}

export function useLayoutPartials(options: UseLayoutPartialsOptions = {}): UseLayoutPartialsReturn {
  const [partials, setPartials] = useState<LayoutPartial[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchPartials = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await layoutPartialsApi.list(options.type, options.context);
      setPartials(response.partials);
    } catch (err) {
      console.error('Error fetching layout partials:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch layout partials');
    } finally {
      setIsLoading(false);
    }
  }, [options.type, options.context]);

  useEffect(() => {
    fetchPartials();
  }, [fetchPartials]);

  // Derived lists
  const headers = useMemo(() => 
    partials.filter(p => p.type === 'header'),
    [partials]
  );

  const footers = useMemo(() => 
    partials.filter(p => p.type === 'footer'),
    [partials]
  );

  const signatures = useMemo(() => 
    partials.filter(p => p.type === 'signature'),
    [partials]
  );

  return {
    partials,
    headers,
    footers,
    signatures,
    isLoading,
    error,
    refetch: fetchPartials
  };
}

/**
 * Get partials filtered by context (pdf, email, sms)
 */
export function useLayoutPartialsForChannel(channel: 'pdf' | 'email' | 'sms' | 'pdf_email') {
  const { partials, isLoading, error, refetch } = useLayoutPartials();

  const filterByChannel = useCallback((items: LayoutPartial[]) => {
    // For pdf_email, show all pdf-compatible and email-compatible partials
    if (channel === 'pdf_email') {
      return items.filter(p => 
        p.context === 'all' || 
        p.context === 'pdf' || 
        p.context === 'email'
      );
    }
    // Otherwise filter by specific channel
    return items.filter(p => 
      p.context === 'all' || 
      p.context === channel
    );
  }, [channel]);

  const headers = useMemo(() => 
    filterByChannel(partials.filter(p => p.type === 'header')),
    [partials, filterByChannel]
  );

  const footers = useMemo(() => 
    filterByChannel(partials.filter(p => p.type === 'footer')),
    [partials, filterByChannel]
  );

  const signatures = useMemo(() => 
    filterByChannel(partials.filter(p => p.type === 'signature')),
    [partials, filterByChannel]
  );

  return {
    headers,
    footers,
    signatures,
    isLoading,
    error,
    refetch
  };
}
